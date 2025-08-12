"""
Customer schemas for request/response DTOs.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

from _shared.models.base import BaseResponse, PaginationParams, PaginatedResponse


class AddressCreate(BaseModel):
    """Address creation request."""
    street: str = Field(..., description="Street address")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State/Province")
    zip_code: str = Field(..., description="ZIP/Postal code")
    country: str = Field(default="USA", description="Country")


class AddressUpdate(BaseModel):
    """Address update request."""
    street: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State/Province")
    zip_code: Optional[str] = Field(None, description="ZIP/Postal code")
    country: Optional[str] = Field(None, description="Country")


class AddressResponse(BaseModel):
    """Address response."""
    id: int
    street: str
    city: str
    state: str
    zip_code: str
    country: str


class ContactInfoCreate(BaseModel):
    """Contact info creation request."""
    phone: Optional[str] = Field(None, description="Phone number")
    email: Optional[EmailStr] = Field(None, description="Email address")
    website: Optional[str] = Field(None, description="Website URL")


class ContactInfoUpdate(BaseModel):
    """Contact info update request."""
    phone: Optional[str] = Field(None, description="Phone number")
    email: Optional[EmailStr] = Field(None, description="Email address")
    website: Optional[str] = Field(None, description="Website URL")


class ContactInfoResponse(BaseModel):
    """Contact info response."""
    id: int
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]


class CustomerCreate(BaseModel):
    """Customer creation request."""
    name: str = Field(..., description="Customer name")
    company: Optional[str] = Field(None, description="Company name")
    tax_id: Optional[str] = Field(None, description="Tax ID number")
    notes: Optional[str] = Field(None, description="Additional notes")
    address: Optional[AddressCreate] = Field(None, description="Customer address")
    contact: Optional[ContactInfoCreate] = Field(None, description="Contact information")


class CustomerUpdate(BaseModel):
    """Customer update request."""
    name: Optional[str] = Field(None, description="Customer name")
    company: Optional[str] = Field(None, description="Company name")
    tax_id: Optional[str] = Field(None, description="Tax ID number")
    notes: Optional[str] = Field(None, description="Additional notes")
    address: Optional[AddressUpdate] = Field(None, description="Customer address")
    contact: Optional[ContactInfoUpdate] = Field(None, description="Contact information")


class CustomerResponse(BaseModel):
    """Customer response."""
    id: int
    name: str
    company: Optional[str]
    tax_id: Optional[str]
    notes: Optional[str]
    full_name: str
    address: Optional[AddressResponse]
    contact: Optional[ContactInfoResponse]
    created_at: datetime
    updated_at: datetime


class CustomerListResponse(BaseResponse):
    """Customer list response."""
    data: List[CustomerResponse]


class CustomerDetailResponse(BaseResponse):
    """Customer detail response."""
    data: CustomerResponse


class CustomerPaginatedResponse(PaginatedResponse):
    """Paginated customer response."""
    items: List[CustomerResponse]
