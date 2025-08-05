"""
Inspection-related Pydantic models.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.config import settings


class IndustryInfo(BaseModel):
    """Industry-specific information model."""

    industry_type: str = Field(..., description="Type of industry")
    facility_name: Optional[str] = Field(None, description="Facility name")
    location: Optional[str] = Field(None, description="Location/address")
    contact_person: Optional[str] = Field(None, description="Contact person")
    phone: Optional[str] = Field(None, description="Contact phone")


class VehicleInfo(BaseModel):
    """Vehicle information model (for automotive industry)."""

    year: Optional[str] = Field(None, description="Vehicle year")
    make: Optional[str] = Field(None, description="Vehicle make")
    model: Optional[str] = Field(None, description="Vehicle model")
    vin: Optional[str] = Field(None, description="Vehicle identification number")
    license_plate: Optional[str] = Field(None, description="License plate number")
    mileage: Optional[str] = Field(None, description="Vehicle mileage")
    trim: Optional[str] = Field(None, description="Vehicle trim level")
    body_style: Optional[str] = Field(None, description="Vehicle body style")
    engine: Optional[str] = Field(None, description="Engine information")
    transmission: Optional[str] = Field(None, description="Transmission type")
    drivetrain: Optional[str] = Field(None, description="Drivetrain type")
    fuel_type: Optional[str] = Field(None, description="Fuel type")
    country_of_origin: Optional[str] = Field(None, description="Country of origin")
    plant_code: Optional[str] = Field(None, description="Manufacturing plant code")
    serial_number: Optional[str] = Field(None, description="Serial number")


class InspectionRequest(BaseModel):
    """Inspection request model with industry support."""

    title: str = Field(
        ...,
        min_length=settings.MIN_TITLE_LENGTH,
        max_length=settings.MAX_TITLE_LENGTH,
        description="Inspection title",
    )
    industry_info: IndustryInfo = Field(..., description="Industry information")
    vehicle_info: Optional[VehicleInfo] = Field(
        None, description="Vehicle information (for automotive)"
    )
    inspector_name: str = Field(
        ...,
        min_length=settings.MIN_INSPECTOR_NAME_LENGTH,
        max_length=settings.MAX_INSPECTOR_NAME_LENGTH,
        description="Inspector name",
    )
    inspector_id: str = Field(..., description="Inspector ID")
    industry_type: str = Field(..., description="Industry type for template selection")


class InspectionItem(BaseModel):
    """Individual inspection item model."""

    name: str
    grade: str = "N/A"
    notes: str = ""
    photos: List[str] = []


class InspectionCategory(BaseModel):
    """Inspection category model."""

    name: str
    description: str = ""
    items: List[InspectionItem] = []


class InspectionData(BaseModel):
    """Complete inspection data model."""

    id: str
    title: str
    industry_info: IndustryInfo
    vehicle_info: Optional[VehicleInfo]
    inspector_name: str
    inspector_id: str
    date: str
    categories: List[InspectionCategory]
    status: str = settings.DEFAULT_INSPECTION_STATUS
    industry_type: str 