"""
Vehicle-related Pydantic models.
"""

from typing import Optional

from pydantic import BaseModel, Field


class VehicleData(BaseModel):
    """Vehicle data model for VIN decoding."""

    vin: str = Field(..., description="Vehicle Identification Number")
    year: Optional[str] = Field(None, description="Vehicle year")
    make: Optional[str] = Field(None, description="Vehicle make")
    model: Optional[str] = Field(None, description="Vehicle model")
    trim: Optional[str] = Field(None, description="Vehicle trim level")
    body_style: Optional[str] = Field(None, description="Vehicle body style")
    engine: Optional[str] = Field(None, description="Engine information")
    transmission: Optional[str] = Field(None, description="Transmission type")
    drivetrain: Optional[str] = Field(None, description="Drivetrain type")
    fuel_type: Optional[str] = Field(None, description="Fuel type")
    country_of_origin: Optional[str] = Field(None, description="Country of origin")
    plant_code: Optional[str] = Field(None, description="Manufacturing plant code")
    serial_number: Optional[str] = Field(None, description="Serial number")
    license_plate: Optional[str] = Field(None, description="License plate number")
    mileage: Optional[str] = Field(None, description="Vehicle mileage") 