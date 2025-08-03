"""
Vehicle Data Module for CheckMate Virtue
Handles VIN decoding and vehicle information for automotive inspections.
"""

from .models import VehicleInfo
from .service import decode_vin
from .vin_decoder import parse_vin_response

__all__ = ["VehicleInfo", "decode_vin", "parse_vin_response"] 