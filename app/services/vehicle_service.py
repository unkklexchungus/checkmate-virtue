"""
Vehicle business logic service.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

from app.config import settings
from app.models.vehicle import VehicleData
from app.utils.file_utils import load_json_file


class VehicleService:
    """Service for handling vehicle business logic."""
    
    def __init__(self):
        self.static_data_file = Path("modules/vehicle_data/static_vin_data.json")
        self.vin_decoder = None  # Will be initialized when needed
    
    def decode_vin(self, vin: str) -> Optional[Dict[str, Any]]:
        """Decode VIN and return vehicle information."""
        if not vin or len(vin) != 17:
            return None
        
        # Load static VIN data
        static_data = load_json_file(self.static_data_file, {})
        
        # Create vehicle data object
        vehicle_data = VehicleData(
            vin=vin,
            year=self._extract_year(vin),
            make=self._extract_make(vin, static_data),
            model=self._extract_model(vin, static_data),
            trim=self._extract_trim(vin, static_data),
            body_style=self._extract_body_style(vin, static_data),
            engine=self._extract_engine(vin, static_data),
            transmission=self._extract_transmission(vin, static_data),
            drivetrain=self._extract_drivetrain(vin, static_data),
            fuel_type=self._extract_fuel_type(vin, static_data),
            country_of_origin=self._extract_country(vin, static_data),
            plant_code=self._extract_plant_code(vin),
            serial_number=self._extract_serial_number(vin),
        )
        
        return vehicle_data.dict()
    
    def _extract_year(self, vin: str) -> Optional[str]:
        """Extract year from VIN."""
        try:
            year_code = vin[9]
            year_map = {
                'A': '2010', 'B': '2011', 'C': '2012', 'D': '2013', 'E': '2014',
                'F': '2015', 'G': '2016', 'H': '2017', 'J': '2018', 'K': '2019',
                'L': '2020', 'M': '2021', 'N': '2022', 'P': '2023', 'R': '2024',
                '1': '2001', '2': '2002', '3': '2003', '4': '2004', '5': '2005',
                '6': '2006', '7': '2007', '8': '2008', '9': '2009'
            }
            return year_map.get(year_code)
        except (IndexError, KeyError):
            return None
    
    def _extract_make(self, vin: str, static_data: Dict[str, Any]) -> Optional[str]:
        """Extract make from VIN."""
        try:
            wmi = vin[:3]
            return static_data.get("makes", {}).get(wmi)
        except (IndexError, KeyError):
            return None
    
    def _extract_model(self, vin: str, static_data: Dict[str, Any]) -> Optional[str]:
        """Extract model from VIN."""
        try:
            # This is a simplified extraction - real implementation would be more complex
            return static_data.get("models", {}).get(vin[:6])
        except (IndexError, KeyError):
            return None
    
    def _extract_trim(self, vin: str, static_data: Dict[str, Any]) -> Optional[str]:
        """Extract trim from VIN."""
        try:
            return static_data.get("trims", {}).get(vin[8])
        except (IndexError, KeyError):
            return None
    
    def _extract_body_style(self, vin: str, static_data: Dict[str, Any]) -> Optional[str]:
        """Extract body style from VIN."""
        try:
            return static_data.get("body_styles", {}).get(vin[2])
        except (IndexError, KeyError):
            return None
    
    def _extract_engine(self, vin: str, static_data: Dict[str, Any]) -> Optional[str]:
        """Extract engine information from VIN."""
        try:
            return static_data.get("engines", {}).get(vin[7])
        except (IndexError, KeyError):
            return None
    
    def _extract_transmission(self, vin: str, static_data: Dict[str, Any]) -> Optional[str]:
        """Extract transmission from VIN."""
        try:
            return static_data.get("transmissions", {}).get(vin[7])
        except (IndexError, KeyError):
            return None
    
    def _extract_drivetrain(self, vin: str, static_data: Dict[str, Any]) -> Optional[str]:
        """Extract drivetrain from VIN."""
        try:
            return static_data.get("drivetrains", {}).get(vin[6])
        except (IndexError, KeyError):
            return None
    
    def _extract_fuel_type(self, vin: str, static_data: Dict[str, Any]) -> Optional[str]:
        """Extract fuel type from VIN."""
        try:
            return static_data.get("fuel_types", {}).get(vin[7])
        except (IndexError, KeyError):
            return None
    
    def _extract_country(self, vin: str, static_data: Dict[str, Any]) -> Optional[str]:
        """Extract country of origin from VIN."""
        try:
            country_code = vin[0]
            return static_data.get("countries", {}).get(country_code)
        except (IndexError, KeyError):
            return None
    
    def _extract_plant_code(self, vin: str) -> Optional[str]:
        """Extract plant code from VIN."""
        try:
            return vin[10]
        except IndexError:
            return None
    
    def _extract_serial_number(self, vin: str) -> Optional[str]:
        """Extract serial number from VIN."""
        try:
            return vin[12:]
        except IndexError:
            return None 