"""
Pydantic models for CheckMate Virtue invoicing system.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator

# Enums
class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class PaymentMethod(str, Enum):
    CASH = "cash"
    CHECK = "check"
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    OTHER = "other"

class TaxType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"

class ItemType(str, Enum):
    LABOR = "labor"
    PARTS = "parts"
    MATERIALS = "materials"
    SERVICE = "service"
    OTHER = "other"

# Base Models
class Address(BaseModel):
    """Address model for clients and company."""
    street: str = Field(..., description="Street address")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State/Province")
    zip_code: str = Field(..., description="ZIP/Postal code")
    country: str = Field(default="USA", description="Country")

class ContactInfo(BaseModel):
    """Contact information model."""
    phone: Optional[str] = Field(None, description="Phone number")
    email: Optional[str] = Field(None, description="Email address")
    website: Optional[str] = Field(None, description="Website URL")

class Client(BaseModel):
    """Client model for invoicing."""
    id: str = Field(..., description="Unique client ID")
    name: str = Field(..., description="Client name")
    company: Optional[str] = Field(None, description="Company name")
    address: Address = Field(..., description="Client address")
    contact: ContactInfo = Field(..., description="Contact information")
    tax_id: Optional[str] = Field(None, description="Tax ID number")
    notes: Optional[str] = Field(None, description="Additional notes")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Job(BaseModel):
    """Job/work order model."""
    id: str = Field(..., description="Unique job ID")
    name: str = Field(..., description="Job name/description")
    description: Optional[str] = Field(None, description="Job description")
    job_number: Optional[str] = Field(None, description="Job number/reference")
    start_date: Optional[date] = Field(None, description="Job start date")
    completion_date: Optional[date] = Field(None, description="Job completion date")
    status: str = Field(default="in_progress", description="Job status")
    notes: Optional[str] = Field(None, description="Job notes")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class InvoiceItem(BaseModel):
    """Individual invoice item model with job association."""
    id: str = Field(..., description="Unique item ID")
    job_id: Optional[str] = Field(None, description="Associated job ID")
    item_type: ItemType = Field(..., description="Type of item (labor, parts, etc.)")
    description: str = Field(..., description="Item description")
    quantity: Decimal = Field(..., ge=0, description="Quantity")
    unit_price: Decimal = Field(..., ge=0, description="Unit price")
    unit: str = Field(default="item", description="Unit of measurement")
    tax_rate: Decimal = Field(default=0, ge=0, le=100, description="Tax rate percentage")
    discount_percent: Decimal = Field(default=0, ge=0, le=100, description="Discount percentage")
    notes: Optional[str] = Field(None, description="Item notes")
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate item subtotal before tax and discount."""
        return self.quantity * self.unit_price
    
    @property
    def discount_amount(self) -> Decimal:
        """Calculate discount amount."""
        return self.subtotal * (self.discount_percent / Decimal('100'))
    
    @property
    def taxable_amount(self) -> Decimal:
        """Calculate taxable amount after discount."""
        return self.subtotal - self.discount_amount
    
    @property
    def tax_amount(self) -> Decimal:
        """Calculate tax amount."""
        return self.taxable_amount * (self.tax_rate / Decimal('100'))
    
    @property
    def total(self) -> Decimal:
        """Calculate item total including tax and discount."""
        return self.subtotal - self.discount_amount + self.tax_amount

class Payment(BaseModel):
    """Payment model for invoice payments."""
    id: str = Field(..., description="Unique payment ID")
    invoice_id: str = Field(..., description="Associated invoice ID")
    amount: Decimal = Field(..., ge=0, description="Payment amount")
    payment_date: date = Field(..., description="Payment date")
    payment_method: PaymentMethod = Field(..., description="Payment method")
    reference: Optional[str] = Field(None, description="Payment reference number")
    notes: Optional[str] = Field(None, description="Payment notes")
    created_at: datetime = Field(default_factory=datetime.now)

class Invoice(BaseModel):
    """Complete invoice model with job-based organization."""
    id: str = Field(..., description="Unique invoice ID")
    invoice_number: str = Field(..., description="Human-readable invoice number")
    client_id: str = Field(..., description="Client ID")
    inspection_id: Optional[str] = Field(None, description="Associated inspection ID")
    industry_type: str = Field(..., description="Industry type")
    
    # Invoice details
    issue_date: date = Field(..., description="Invoice issue date")
    due_date: date = Field(..., description="Invoice due date")
    status: InvoiceStatus = Field(default=InvoiceStatus.DRAFT, description="Invoice status")
    
    # Items and amounts - organized by job
    jobs: List[Job] = Field(default=[], description="Jobs/work orders")
    items: List[InvoiceItem] = Field(default=[], description="Invoice items")
    subtotal: Decimal = Field(default=0, ge=0, description="Subtotal before tax")
    tax_amount: Decimal = Field(default=0, ge=0, description="Total tax amount")
    discount_amount: Decimal = Field(default=0, ge=0, description="Total discount amount")
    total: Decimal = Field(default=0, ge=0, description="Total invoice amount")
    
    # Job-based totals
    labor_total: Decimal = Field(default=0, ge=0, description="Total labor charges")
    parts_total: Decimal = Field(default=0, ge=0, description="Total parts charges")
    materials_total: Decimal = Field(default=0, ge=0, description="Total materials charges")
    service_total: Decimal = Field(default=0, ge=0, description="Total service charges")
    
    # Additional charges
    shipping: Decimal = Field(default=0, ge=0, description="Shipping charges")
    handling: Decimal = Field(default=0, ge=0, description="Handling charges")
    other_charges: Decimal = Field(default=0, ge=0, description="Other charges")
    
    # Terms and notes
    terms: Optional[str] = Field(None, description="Payment terms")
    notes: Optional[str] = Field(None, description="Invoice notes")
    footer: Optional[str] = Field(None, description="Invoice footer text")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    sent_at: Optional[datetime] = Field(None, description="Date invoice was sent")
    paid_at: Optional[datetime] = Field(None, description="Date invoice was paid")
    
    # Payments
    payments: List[Payment] = Field(default=[], description="Invoice payments")
    
    @property
    def amount_paid(self) -> Decimal:
        """Calculate total amount paid."""
        return sum(payment.amount for payment in self.payments)
    
    @property
    def balance_due(self) -> Decimal:
        """Calculate remaining balance."""
        return self.total - self.amount_paid
    
    @property
    def is_paid(self) -> bool:
        """Check if invoice is fully paid."""
        return self.balance_due <= 0
    
    @property
    def is_overdue(self) -> bool:
        """Check if invoice is overdue."""
        return (self.status == InvoiceStatus.SENT and 
                self.due_date < date.today() and 
                not self.is_paid)
    
    def calculate_totals(self):
        """Calculate all invoice totals including job-based breakdowns."""
        self.subtotal = sum(item.subtotal for item in self.items)
        self.tax_amount = sum(item.tax_amount for item in self.items)
        self.discount_amount = sum(item.discount_amount for item in self.items)
        
        # Calculate job-based totals
        self.labor_total = sum(item.subtotal for item in self.items if item.item_type == ItemType.LABOR)
        self.parts_total = sum(item.subtotal for item in self.items if item.item_type == ItemType.PARTS)
        self.materials_total = sum(item.subtotal for item in self.items if item.item_type == ItemType.MATERIALS)
        self.service_total = sum(item.subtotal for item in self.items if item.item_type == ItemType.SERVICE)
        
        self.total = (self.subtotal - self.discount_amount + 
                     self.tax_amount + self.shipping + 
                     self.handling + self.other_charges)

class CompanyInfo(BaseModel):
    """Company information for invoice templates."""
    name: str = Field(..., description="Company name")
    address: Address = Field(..., description="Company address")
    contact: ContactInfo = Field(..., description="Company contact info")
    logo_url: Optional[str] = Field(None, description="Company logo URL")
    tax_id: Optional[str] = Field(None, description="Company tax ID")
    website: Optional[str] = Field(None, description="Company website")
    bank_info: Optional[str] = Field(None, description="Bank account information")

class InvoiceTemplate(BaseModel):
    """Invoice template model with job-based structure."""
    id: str = Field(..., description="Template ID")
    name: str = Field(..., description="Template name")
    industry_type: str = Field(..., description="Associated industry")
    description: Optional[str] = Field(None, description="Template description")
    
    # Default values
    default_terms: Optional[str] = Field(None, description="Default payment terms")
    default_notes: Optional[str] = Field(None, description="Default invoice notes")
    default_footer: Optional[str] = Field(None, description="Default footer text")
    
    # Template jobs and items
    default_jobs: List[Dict[str, Any]] = Field(default=[], description="Default jobs/work orders")
    default_items: List[Dict[str, Any]] = Field(default=[], description="Default invoice items")
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# Request/Response Models
class CreateInvoiceRequest(BaseModel):
    """Request model for creating a new invoice."""
    client_id: str = Field(..., description="Client ID")
    inspection_id: Optional[str] = Field(None, description="Associated inspection ID")
    industry_type: str = Field(..., description="Industry type")
    issue_date: date = Field(default_factory=date.today, description="Invoice issue date")
    due_date: Optional[date] = Field(None, description="Invoice due date")
    template_id: Optional[str] = Field(None, description="Invoice template ID")
    jobs: List[Dict[str, Any]] = Field(default=[], description="Jobs/work orders")
    items: List[Dict[str, Any]] = Field(default=[], description="Invoice items")
    terms: Optional[str] = Field(None, description="Payment terms")
    notes: Optional[str] = Field(None, description="Invoice notes")

class UpdateInvoiceRequest(BaseModel):
    """Request model for updating an invoice."""
    client_id: Optional[str] = Field(None, description="Client ID")
    issue_date: Optional[date] = Field(None, description="Invoice issue date")
    due_date: Optional[date] = Field(None, description="Invoice due date")
    status: Optional[InvoiceStatus] = Field(None, description="Invoice status")
    jobs: Optional[List[Dict[str, Any]]] = Field(None, description="Jobs/work orders")
    items: Optional[List[Dict[str, Any]]] = Field(None, description="Invoice items")
    terms: Optional[str] = Field(None, description="Payment terms")
    notes: Optional[str] = Field(None, description="Invoice notes")
    shipping: Optional[Decimal] = Field(None, description="Shipping charges")
    handling: Optional[Decimal] = Field(None, description="Handling charges")
    other_charges: Optional[Decimal] = Field(None, description="Other charges")

class CreateClientRequest(BaseModel):
    """Request model for creating a new client."""
    name: str = Field(..., description="Client name")
    company: Optional[str] = Field(None, description="Company name")
    address: Address = Field(..., description="Client address")
    contact: ContactInfo = Field(..., description="Contact information")
    tax_id: Optional[str] = Field(None, description="Tax ID number")
    notes: Optional[str] = Field(None, description="Additional notes")

class CreateJobRequest(BaseModel):
    """Request model for creating a new job."""
    name: str = Field(..., description="Job name")
    description: Optional[str] = Field(None, description="Job description")
    job_number: Optional[str] = Field(None, description="Job number")
    start_date: Optional[date] = Field(None, description="Job start date")
    status: str = Field(default="in_progress", description="Job status")
    notes: Optional[str] = Field(None, description="Job notes")

class CreatePaymentRequest(BaseModel):
    """Request model for creating a payment."""
    invoice_id: str = Field(..., description="Invoice ID")
    amount: Decimal = Field(..., ge=0, description="Payment amount")
    payment_date: date = Field(default_factory=date.today, description="Payment date")
    payment_method: PaymentMethod = Field(..., description="Payment method")
    reference: Optional[str] = Field(None, description="Payment reference")
    notes: Optional[str] = Field(None, description="Payment notes")

# Utility functions
def generate_invoice_id() -> str:
    """Generate unique invoice ID."""
    return f"INV_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def generate_invoice_number(prefix: str = "INV") -> str:
    """Generate human-readable invoice number."""
    return f"{prefix}-{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"

def generate_client_id() -> str:
    """Generate unique client ID."""
    return f"CLIENT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def generate_job_id() -> str:
    """Generate unique job ID."""
    return f"JOB_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def generate_payment_id() -> str:
    """Generate unique payment ID."""
    return f"PAY_{datetime.now().strftime('%Y%m%d_%H%M%S')}" 