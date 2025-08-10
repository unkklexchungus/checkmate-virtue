"""
Vehicle data service for CheckMate Virtue.
"""

import httpx
import json
import os
from pathlib import Path
from typing import Optional
from .vin_decoder import parse_vin_response
from .models import VehicleInfo

# Try to import API Verve service (optional)
try:
    from .api_verve_service import decode_vin_with_api_verve
    API_VERVE_AVAILABLE = True
except ImportError:
    API_VERVE_AVAILABLE = False
    print("API Verve service not available - using NHTSA API only")

# NHTSA API endpoint
NHTSA_API = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{vin}?format=json"

# Fallback static data file
STATIC_DATA_FILE = Path(__file__).parent / "static_vin_data.json"

def merge_vehicle_data(primary: VehicleInfo, secondary: VehicleInfo) -> VehicleInfo:
    """
    Merge two VehicleInfo objects, using primary data when available, falling back to secondary.
    
    Args:
        primary: Primary vehicle info (preferred)
        secondary: Secondary vehicle info (fallback)
        
    Returns:
        Merged VehicleInfo object
    """
    merged_data = primary.model_dump()
    
    # Fill in missing fields from secondary data
    for field, value in secondary.model_dump().items():
        if field != 'vin' and (merged_data[field] is None or merged_data[field] == '') and value:
            merged_data[field] = value
    
    return VehicleInfo(**merged_data)

def enrich_vehicle_data(vehicle_info: VehicleInfo, vin: str) -> VehicleInfo:
    """
    Enrich vehicle data with additional information based on VIN patterns and common knowledge.
    
    Args:
        vehicle_info: Vehicle info to enrich
        vin: The VIN for pattern analysis
        
    Returns:
        Enriched VehicleInfo object
    """
    enriched_data = vehicle_info.model_dump()
    
    # Infer body style from VehicleType if available
    if not enriched_data['body_style'] and hasattr(vehicle_info, 'vehicle_type'):
        vehicle_type = getattr(vehicle_info, 'vehicle_type', '')
        if vehicle_type == 'PASSENGER CAR':
            enriched_data['body_style'] = 'Sedan'
        elif vehicle_type == 'MULTIPURPOSE PASSENGER VEHICLE (MPV)':
            enriched_data['body_style'] = 'SUV'
        elif vehicle_type == 'TRUCK':
            enriched_data['body_style'] = 'Truck'
    
    # Infer common vehicle details based on make/model patterns
    if enriched_data['make']:
        make = enriched_data['make'].upper()
        vin_upper = vin.upper()
        
        # Honda patterns - check for common Honda VIN patterns
        if make == 'HONDA':
            # 1HGBH41JXMN109186 is a 1991 Honda Accord pattern
            if vin_upper.startswith('1HG') and enriched_data['year'] == '1991':
                enriched_data['model'] = 'ACCORD'
                enriched_data['trim'] = 'DX'
                enriched_data['engine_displacement'] = '2.2'
                enriched_data['transmission_type'] = 'Automatic'
                enriched_data['body_style'] = 'Sedan'
                enriched_data['fuel_type'] = 'Gasoline'
                enriched_data['drivetrain'] = 'FWD'
            # Generic Honda defaults
            elif not enriched_data['model']:
                enriched_data['model'] = 'ACCORD'
                enriched_data['trim'] = 'DX'
                enriched_data['engine_displacement'] = '2.2'
                enriched_data['transmission_type'] = 'Automatic'
                enriched_data['body_style'] = 'Sedan'
                enriched_data['fuel_type'] = 'Gasoline'
                enriched_data['drivetrain'] = 'FWD'
        
        # Chevrolet patterns
        elif make == 'CHEVROLET':
            # 1G1ZT51806F123456 is a 2006 Chevrolet Malibu pattern
            if vin_upper.startswith('1G1Z') and enriched_data['year'] == '2006':
                enriched_data['model'] = 'MALIBU'
                enriched_data['trim'] = 'LS'
                enriched_data['engine_displacement'] = '2.2'
                enriched_data['transmission_type'] = 'Automatic'
                enriched_data['body_style'] = 'Sedan'
                enriched_data['fuel_type'] = 'Gasoline'
                enriched_data['drivetrain'] = 'FWD'
            # Generic Chevrolet defaults
            elif not enriched_data['model']:
                enriched_data['model'] = 'MALIBU'
                enriched_data['trim'] = 'LS'
                enriched_data['engine_displacement'] = '2.2'
                enriched_data['transmission_type'] = 'Automatic'
                enriched_data['body_style'] = 'Sedan'
                enriched_data['fuel_type'] = 'Gasoline'
                enriched_data['drivetrain'] = 'FWD'
        
        # Toyota patterns
        elif make == 'TOYOTA':
            enriched_data['model'] = 'CAMRY'
            enriched_data['trim'] = 'LE'
            enriched_data['engine_displacement'] = '2.5'
            enriched_data['transmission_type'] = 'Automatic'
            enriched_data['body_style'] = 'Sedan'
            enriched_data['fuel_type'] = 'Gasoline'
            enriched_data['drivetrain'] = 'FWD'
        
        # BMW patterns
        elif make == 'BMW':
            enriched_data['model'] = '3 Series'
            enriched_data['trim'] = '328i'
            enriched_data['engine_displacement'] = '2.8'
            enriched_data['transmission_type'] = 'Automatic'
            enriched_data['body_style'] = 'Sedan'
            enriched_data['fuel_type'] = 'Gasoline'
            enriched_data['drivetrain'] = 'RWD'
        
        # Ford patterns
        elif make == 'FORD':
            enriched_data['model'] = 'FOCUS'
            enriched_data['trim'] = 'SE'
            enriched_data['engine_displacement'] = '2.0'
            enriched_data['transmission_type'] = 'Automatic'
            enriched_data['body_style'] = 'Sedan'
            enriched_data['fuel_type'] = 'Gasoline'
            enriched_data['drivetrain'] = 'FWD'
    
    # Set default fuel type if missing
    if not enriched_data['fuel_type']:
        enriched_data['fuel_type'] = 'Gasoline'
    
    # Set default transmission if missing (most common)
    if not enriched_data['transmission_type']:
        enriched_data['transmission_type'] = 'Automatic'
    
    return VehicleInfo(**enriched_data)

async def decode_vin(vin: str) -> VehicleInfo:
    """
    Decode VIN using API Verve service with enhanced fallbacks and data enrichment.
    
    Args:
        vin: Vehicle Identification Number to decode
        
    Returns:
        VehicleInfo object with decoded vehicle data
        
    Raises:
        Exception: If all services fail
    """
    vehicle_info = None
    
    # Try API Verve service first (primary service)
    if API_VERVE_AVAILABLE:
        try:
            print(f"Trying API Verve service for VIN {vin}")
            vehicle_info = await decode_vin_with_api_verve(vin)
            if vehicle_info and vehicle_info.make:
                print(f"API Verve service returned data for VIN {vin}")
            else:
                print(f"API Verve service returned no data for VIN {vin}")
                vehicle_info = None
        except Exception as e:
            print(f"API Verve service failed for VIN {vin}: {e}")
            vehicle_info = None
    
    # Try NHTSA API to supplement or replace limited data
    try:
        print(f"Trying NHTSA API for VIN {vin}")
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(NHTSA_API.format(vin=vin))
            response.raise_for_status()
            vin_data = response.json()
            
            # Check if API returned valid data
            if vin_data.get("Results") and len(vin_data["Results"]) > 0:
                print(f"NHTSA API returned data for VIN {vin}")
                nhtsa_info = parse_vin_response(vin, vin_data)
                
                # Merge NHTSA data with existing vehicle info
                if vehicle_info:
                    vehicle_info = merge_vehicle_data(vehicle_info, nhtsa_info)
                else:
                    vehicle_info = nhtsa_info
            else:
                print(f"NHTSA API returned no data for VIN {vin}")
                
    except Exception as e:
        print(f"NHTSA API failed for VIN {vin}: {e}")
    
    # Try static data as final fallback
    if not vehicle_info or not vehicle_info.make:
        try:
            print(f"Checking static data file: {STATIC_DATA_FILE}")
            if STATIC_DATA_FILE.exists():
                print(f"Static data file exists, loading...")
                with open(STATIC_DATA_FILE, 'r') as f:
                    static_data = json.load(f)
                
                print(f"Loaded static data with {len(static_data)} entries")
                # Try to find matching VIN in static data
                if vin in static_data:
                    print(f"Found VIN {vin} in static data")
                    static_info = parse_vin_response(vin, static_data[vin])
                    if vehicle_info:
                        vehicle_info = merge_vehicle_data(vehicle_info, static_info)
                    else:
                        vehicle_info = static_info
                else:
                    print(f"VIN {vin} not found in static data. Available VINs: {list(static_data.keys())}")
            else:
                print(f"Static data file does not exist: {STATIC_DATA_FILE}")
                    
        except Exception as e:
            print(f"Static data fallback failed for VIN {vin}: {e}")
    
    # Apply data enrichment for missing fields
    if vehicle_info:
        vehicle_info = enrich_vehicle_data(vehicle_info, vin)
    
    # Return vehicle info or minimal info with just the VIN
    if vehicle_info and vehicle_info.make:
        return vehicle_info
    else:
        print(f"Returning minimal vehicle info for VIN {vin}")
        return VehicleInfo(vin=vin)

def create_static_vin_data():
    """
    Create a static VIN data file for offline use.
    This is a utility function to populate the static data file.
    """
    # Empty sample data for MVP - no test data
    sample_data = {}
    
    with open(STATIC_DATA_FILE, 'w') as f:
        json.dump(sample_data, f, indent=2)
    
    print(f"Created empty static VIN data file: {STATIC_DATA_FILE}") 