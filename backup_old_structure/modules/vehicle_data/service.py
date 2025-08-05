"""
Vehicle data service for CheckMate Virtue.
"""

import json
import os
from pathlib import Path
from typing import Optional

import httpx

from app.models import VehicleInfo
from .vin_decoder import parse_vin_response

# NHTSA API endpoint
NHTSA_API = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{vin}?format=json"

# Fallback static data file
STATIC_DATA_FILE = Path(__file__).parent / "static_vin_data.json"


async def decode_vin(vin: str) -> VehicleInfo:
    """
    Decode VIN using NHTSA API with fallback to static data.

    Args:
        vin: Vehicle Identification Number to decode

    Returns:
        VehicleInfo object with decoded vehicle data

    Raises:
        Exception: If both API and static data fail
    """
    # Try NHTSA API first (primary source)
    try:
        print(f"Trying NHTSA API for VIN {vin}")
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(NHTSA_API.format(vin=vin))
            response.raise_for_status()
            vin_data = response.json()

            # Check if API returned valid data
            if vin_data.get("Results") and len(vin_data["Results"]) > 0:
                # Check if we got meaningful data (not just empty/null values)
                result = vin_data["Results"][0]
                has_data = False

                # Check for key fields that indicate we have real data
                key_fields = ["Make", "Model", "ModelYear", "VIN"]
                for field in key_fields:
                    if (
                        result.get(field)
                        and result.get(field) != ""
                        and result.get(field) != "0"
                    ):
                        has_data = True
                        break

                if has_data:
                    print(f"NHTSA API returned valid data for VIN {vin}")
                    return parse_vin_response(vin, vin_data)
                else:
                    print(f"NHTSA API returned empty data for VIN {vin}")
            else:
                print(f"NHTSA API returned no data for VIN {vin}")

    except Exception as e:
        print(f"NHTSA API failed for VIN {vin}: {e}")

    # Try static data as fallback (for testing/offline use)
    try:
        print(f"Checking static data file: {STATIC_DATA_FILE}")
        if STATIC_DATA_FILE.exists():
            print(f"Static data file exists, loading...")
            with open(STATIC_DATA_FILE, "r") as f:
                static_data = json.load(f)

            print(f"Loaded static data with {len(static_data)} entries")
            # Try to find matching VIN in static data
            if vin in static_data:
                print(f"Found VIN {vin} in static data")
                return parse_vin_response(vin, static_data[vin])
            else:
                print(
                    f"VIN {vin} not found in static data. Available VINs: {list(static_data.keys())}"
                )
        else:
            print(f"Static data file does not exist: {STATIC_DATA_FILE}")

    except Exception as e:
        print(f"Static data fallback failed for VIN {vin}: {e}")

    # Return minimal vehicle info with just the VIN if both sources fail
    print(f"Returning minimal vehicle info for VIN {vin}")
    return VehicleInfo(vin=vin)


def create_static_vin_data():
    """
    Create a static VIN data file with sample data for offline use.
    This is a utility function to populate the static data file.
    """
    sample_data = {
        "1HGBH41JXMN109186": {
            "Results": [
                {"Variable": "Model Year", "Value": "1991"},
                {"Variable": "Make", "Value": "HONDA"},
                {"Variable": "Model", "Value": "ACCORD"},
                {"Variable": "Trim", "Value": "DX"},
                {"Variable": "Displacement (L)", "Value": "2.2"},
                {"Variable": "Transmission Style", "Value": "Automatic"},
                {"Variable": "Body Style", "Value": "Sedan"},
                {"Variable": "Fuel Type - Primary", "Value": "Gasoline"},
                {"Variable": "Drive Type", "Value": "FWD"},
                {"Variable": "Plant Country", "Value": "USA"},
                {"Variable": "Plant Code", "Value": "H"},
                {"Variable": "Series", "Value": "ACCORD"},
            ]
        },
        "1G1ZT51806F123456": {
            "Results": [
                {"Variable": "Model Year", "Value": "2006"},
                {"Variable": "Make", "Value": "CHEVROLET"},
                {"Variable": "Model", "Value": "CORVETTE"},
                {"Variable": "Trim", "Value": "Z06"},
                {"Variable": "Displacement (L)", "Value": "7.0"},
                {"Variable": "Transmission Style", "Value": "Manual"},
                {"Variable": "Body Style", "Value": "Coupe"},
                {"Variable": "Fuel Type - Primary", "Value": "Gasoline"},
                {"Variable": "Drive Type", "Value": "RWD"},
                {"Variable": "Plant Country", "Value": "USA"},
                {"Variable": "Plant Code", "Value": "B"},
                {"Variable": "Series", "Value": "CORVETTE"},
            ]
        },
    }

    with open(STATIC_DATA_FILE, "w") as f:
        json.dump(sample_data, f, indent=2)

    print(f"Created static VIN data file: {STATIC_DATA_FILE}")
