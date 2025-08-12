"""
Customer model for customer service.
"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

from _shared.models.base import TimestampMixin


class Address(SQLModel, table=True):
    """Address model."""
    
    __tablename__ = "addresses"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    street: str = Field(..., description="Street address")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State/Province")
    zip_code: str = Field(..., description="ZIP/Postal code")
    country: str = Field(default="USA", description="Country")
    
    # Relationships
    customers: List["Customer"] = Relationship(back_populates="address")


class ContactInfo(SQLModel, table=True):
    """Contact information model."""
    
    __tablename__ = "contact_info"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    phone: Optional[str] = Field(None, description="Phone number")
    email: Optional[str] = Field(None, description="Email address")
    website: Optional[str] = Field(None, description="Website URL")
    
    # Relationships
    customers: List["Customer"] = Relationship(back_populates="contact")


class Customer(SQLModel, TimestampMixin, table=True):
    """Customer model."""
    
    __tablename__ = "customers"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(..., description="Customer name")
    company: Optional[str] = Field(None, description="Company name")
    tax_id: Optional[str] = Field(None, description="Tax ID number")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    # Foreign keys
    address_id: Optional[int] = Field(None, foreign_key="addresses.id")
    contact_id: Optional[int] = Field(None, foreign_key="contact_info.id")
    
    # Relationships
    address: Optional[Address] = Relationship(back_populates="customers")
    contact: Optional[ContactInfo] = Relationship(back_populates="customers")
    
    @property
    def full_name(self) -> str:
        """Get customer's full name."""
        if self.company:
            return f"{self.name} ({self.company})"
        return self.name
