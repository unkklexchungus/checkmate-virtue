"""
Vehicle data models for CheckMate Virtue.
"""

from pydantic import BaseModel, Field
from typing import Optional

class VehicleInfo(BaseModel):
    """Vehicle information model for VIN decoding."""
    vin: str = Field(..., description="Vehicle Identification Number")
    year: Optional[str] = Field(None, description="Vehicle year")
    make: Optional[str] = Field(None, description="Vehicle make")
    model: Optional[str] = Field(None, description="Vehicle model")
    trim: Optional[str] = Field(None, description="Vehicle trim level")
    engine_displacement: Optional[str] = Field(None, description="Engine displacement in liters")
    transmission_type: Optional[str] = Field(None, description="Transmission type (Automatic/Manual)")
    
    # Additional fields that might be useful
    body_style: Optional[str] = Field(None, description="Vehicle body style")
    fuel_type: Optional[str] = Field(None, description="Fuel type")
    drivetrain: Optional[str] = Field(None, description="Drivetrain type")
    country_of_origin: Optional[str] = Field(None, description="Country of origin")
    plant_code: Optional[str] = Field(None, description="Manufacturing plant code")
    serial_number: Optional[str] = Field(None, description="Serial number") 