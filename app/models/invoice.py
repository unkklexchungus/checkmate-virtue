"""
Invoice-related Pydantic models.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Client(BaseModel):
    """Client information model."""

    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    company: Optional[str] = None


class InvoiceItem(BaseModel):
    """Invoice item model."""

    description: str
    quantity: float = 1.0
    unit_price: float
    total: float = 0.0


class Invoice(BaseModel):
    """Invoice model."""

    id: str
    client_id: str
    invoice_number: str
    date: datetime
    due_date: Optional[datetime] = None
    items: List[InvoiceItem] = []
    subtotal: float = 0.0
    tax_rate: float = 0.0
    tax_amount: float = 0.0
    total: float = 0.0
    status: str = "draft"
    notes: Optional[str] = None 