"""
Invoice routes for CheckMate Virtue invoicing system.
"""

import json
import os
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates

from models import (
    Invoice, InvoiceItem, Payment, Client, CompanyInfo, Job,
    CreateInvoiceRequest, UpdateInvoiceRequest, CreateClientRequest, CreatePaymentRequest, CreateJobRequest,
    InvoiceStatus, PaymentMethod, ItemType, generate_invoice_id, generate_invoice_number,
    generate_client_id, generate_job_id, generate_payment_id
)

# File paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
INVOICES_FILE = DATA_DIR / "invoices.json"
CLIENTS_FILE = DATA_DIR / "clients.json"
COMPANY_FILE = BASE_DIR / "company_info.json"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)

# Templates
templates = Jinja2Templates(directory="templates")

# Router
router = APIRouter(prefix="/invoices", tags=["invoices"])

# Utility functions
def load_json_file(file_path: Path, default: Any = None) -> Any:
    """Load JSON file with error handling."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default

def save_json_file(file_path: Path, data: Any) -> None:
    """Save data to JSON file with error handling."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save data: {str(e)}")

def find_invoice(invoice_id: str) -> Optional[Dict[str, Any]]:
    """Find invoice by ID."""
    invoices = load_json_file(INVOICES_FILE, [])
    return next((i for i in invoices if i["id"] == invoice_id), None)

def find_client(client_id: str) -> Optional[Dict[str, Any]]:
    """Find client by ID."""
    clients = load_json_file(CLIENTS_FILE, [])
    return next((c for c in clients if c["id"] == client_id), None)

def update_invoice_data(invoice_id: str, updated_data: Dict[str, Any]) -> bool:
    """Update invoice data in file."""
    invoices = load_json_file(INVOICES_FILE, [])
    
    for i, invoice in enumerate(invoices):
        if invoice["id"] == invoice_id:
            invoices[i] = updated_data
            save_json_file(INVOICES_FILE, invoices)
            return True
    return False

def load_company_info() -> CompanyInfo:
    """Load company information."""
    company_data = load_json_file(COMPANY_FILE)
    if company_data:
        return CompanyInfo(**company_data)
    
    # Default company info
    return CompanyInfo(
        name="CheckMate Virtue",
        address={
            "street": "123 Professional Drive",
            "city": "Business City",
            "state": "CA",
            "zip_code": "90210",
            "country": "USA"
        },
        contact={
            "phone": "(555) 123-4567",
            "email": "info@checkmatevirtue.com",
            "website": "https://checkmatevirtue.com"
        },
        logo_url="/static/images/logo.png",
        tax_id="12-3456789",
        website="https://checkmatevirtue.com",
        bank_info="Bank: Professional Bank\nAccount: 1234567890\nRouting: 987654321"
    )

# Routes
@router.get("/", response_class=HTMLResponse)
async def list_invoices(request: Request) -> HTMLResponse:
    """List all invoices."""
    invoices = load_json_file(INVOICES_FILE, [])
    clients = load_json_file(CLIENTS_FILE, [])
    
    # Add client info to invoices
    for invoice in invoices:
        client = find_client(invoice.get("client_id", ""))
        invoice["client"] = client
    
    breadcrumbs = [
        {"text": "Invoices", "url": "/invoices", "icon": "fas fa-file-invoice"}
    ]
    return templates.TemplateResponse("invoices/list.html", {
        "request": request,
        "invoices": invoices,
        "clients": clients,
        "breadcrumbs": breadcrumbs
    })

@router.get("/new", response_class=HTMLResponse)
async def new_invoice_form(request: Request) -> HTMLResponse:
    """New invoice form."""
    clients = load_json_file(CLIENTS_FILE, [])
    breadcrumbs = [
        {"text": "Invoices", "url": "/invoices", "icon": "fas fa-file-invoice"},
        {"text": "New Invoice", "url": "/invoices/new", "icon": "fas fa-plus"}
    ]
    return templates.TemplateResponse("invoices/new.html", {
        "request": request,
        "clients": clients,
        "breadcrumbs": breadcrumbs
    })

# Client routes
@router.get("/clients", response_class=HTMLResponse)
async def list_clients(request: Request) -> HTMLResponse:
    """List all clients."""
    clients = load_json_file(CLIENTS_FILE, [])
    breadcrumbs = [
        {"text": "Invoices", "url": "/invoices", "icon": "fas fa-file-invoice"},
        {"text": "Clients", "url": "/invoices/clients", "icon": "fas fa-users"}
    ]
    return templates.TemplateResponse("invoices/clients.html", {
        "request": request,
        "clients": clients,
        "breadcrumbs": breadcrumbs
    })

@router.get("/clients/new", response_class=HTMLResponse)
async def new_client_form(request: Request) -> HTMLResponse:
    """New client form."""
    breadcrumbs = [
        {"text": "Invoices", "url": "/invoices", "icon": "fas fa-file-invoice"},
        {"text": "Clients", "url": "/invoices/clients", "icon": "fas fa-users"},
        {"text": "New Client", "url": "/invoices/clients/new", "icon": "fas fa-plus"}
    ]
    return templates.TemplateResponse("invoices/new_client.html", {
        "request": request,
        "breadcrumbs": breadcrumbs
    })

@router.get("/{invoice_id}", response_class=HTMLResponse)
async def view_invoice(request: Request, invoice_id: str) -> HTMLResponse:
    """View a specific invoice."""
    invoice = find_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Ensure numeric fields are properly formatted
    if invoice.get("total") is not None:
        try:
            invoice["total"] = float(invoice["total"])
        except (ValueError, TypeError):
            invoice["total"] = 0.0
    
    if invoice.get("subtotal") is not None:
        try:
            invoice["subtotal"] = float(invoice["subtotal"])
        except (ValueError, TypeError):
            invoice["subtotal"] = 0.0
    
    if invoice.get("tax_amount") is not None:
        try:
            invoice["tax_amount"] = float(invoice["tax_amount"])
        except (ValueError, TypeError):
            invoice["tax_amount"] = 0.0
    
    if invoice.get("discount_amount") is not None:
        try:
            invoice["discount_amount"] = float(invoice["discount_amount"])
        except (ValueError, TypeError):
            invoice["discount_amount"] = 0.0
    
    # Calculate totals for each item
    if invoice.get("items"):
        for item in invoice["items"]:
            try:
                quantity = float(item.get("quantity", 0))
                unit_price = float(item.get("unit_price", 0))
                tax_rate = float(item.get("tax_rate", 0))
                discount_percent = float(item.get("discount_percent", 0))
                
                subtotal = quantity * unit_price
                discount_amount = subtotal * (discount_percent / 100)
                taxable_amount = subtotal - discount_amount
                tax_amount = taxable_amount * (tax_rate / 100)
                total = subtotal - discount_amount + tax_amount
                
                item["subtotal"] = subtotal
                item["discount_amount"] = discount_amount
                item["tax_amount"] = tax_amount
                item["total"] = total
            except (ValueError, TypeError):
                item["subtotal"] = 0.0
                item["discount_amount"] = 0.0
                item["tax_amount"] = 0.0
                item["total"] = 0.0
    
    client = find_client(invoice.get("client_id", ""))
    company = load_company_info()
    
    breadcrumbs = [
        {"text": "Invoices", "url": "/invoices", "icon": "fas fa-file-invoice"},
        {"text": f"Invoice {invoice_id}", "url": f"/invoices/{invoice_id}", "icon": "fas fa-eye"}
    ]
    return templates.TemplateResponse("invoices/view.html", {
        "request": request,
        "invoice": invoice,
        "client": client,
        "breadcrumbs": breadcrumbs,
        "company": company
    })

@router.get("/{invoice_id}/edit", response_class=HTMLResponse)
async def edit_invoice_form(request: Request, invoice_id: str) -> HTMLResponse:
    """Edit invoice form."""
    invoice = find_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    clients = load_json_file(CLIENTS_FILE, [])
    
    breadcrumbs = [
        {"text": "Invoices", "url": "/invoices", "icon": "fas fa-file-invoice"},
        {"text": f"Edit Invoice {invoice_id}", "url": f"/invoices/{invoice_id}/edit", "icon": "fas fa-edit"}
    ]
    return templates.TemplateResponse("invoices/edit.html", {
        "request": request,
        "invoice": invoice,
        "clients": clients,
        "breadcrumbs": breadcrumbs
    })

@router.post("/api/invoices")
async def create_invoice(request: CreateInvoiceRequest) -> Dict[str, Any]:
    """Create a new invoice."""
    # Validate client exists
    client = find_client(request.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Create invoice
    invoice_data = {
        "id": generate_invoice_id(),
        "invoice_number": generate_invoice_number(),
        "client_id": request.client_id,
        "inspection_id": request.inspection_id,
        "industry_type": request.industry_type,
        "issue_date": request.issue_date.isoformat(),
        "due_date": (request.due_date or (date.today() + datetime.timedelta(days=30))).isoformat(),
        "status": InvoiceStatus.DRAFT.value,
        "jobs": [],
        "items": [],
        "subtotal": 0,
        "tax_amount": 0,
        "discount_amount": 0,
        "total": 0,
        "labor_total": 0,
        "parts_total": 0,
        "materials_total": 0,
        "service_total": 0,
        "shipping": 0,
        "handling": 0,
        "other_charges": 0,
        "terms": request.terms,
        "notes": request.notes,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "payments": []
    }
    
    # Add jobs if provided
    if hasattr(request, 'jobs') and request.jobs:
        for job_data in request.jobs:
            # Handle empty date strings
            start_date = job_data.get("start_date")
            if start_date == "":
                start_date = None
            
            job = Job(
                id=generate_job_id(),
                name=job_data["name"],
                description=job_data.get("description"),
                job_number=job_data.get("job_number"),
                start_date=start_date,
                status=job_data.get("status", "completed")
            )
            invoice_data["jobs"].append(job.model_dump())
    
    # Add items
    for item_data in request.items:
        item = InvoiceItem(
            id=f"item_{len(invoice_data['items']) + 1}",
            job_id=item_data.get("job_id"),
            item_type=item_data.get("item_type", "service"),
            description=item_data["description"],
            quantity=Decimal(str(item_data["quantity"])),
            unit_price=Decimal(str(item_data["unit_price"])),
            unit=item_data.get("unit", "item"),
            tax_rate=Decimal(str(item_data.get("tax_rate", 0))),
            discount_percent=Decimal(str(item_data.get("discount_percent", 0))),
            notes=item_data.get("notes", "")
        )
        invoice_data["items"].append(item.model_dump())
    
    # Calculate totals
    invoice = Invoice(**invoice_data)
    invoice.calculate_totals()
    invoice_data = invoice.model_dump()
    
    # Save invoice
    invoices = load_json_file(INVOICES_FILE, [])
    invoices.append(invoice_data)
    save_json_file(INVOICES_FILE, invoices)
    
    return {
        "message": "Invoice created successfully",
        "invoice_id": invoice_data["id"],
        "invoice_number": invoice_data["invoice_number"]
    }

@router.put("/api/invoices/{invoice_id}")
async def update_invoice(invoice_id: str, request: UpdateInvoiceRequest) -> Dict[str, str]:
    """Update an invoice."""
    invoice = find_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Update fields
    if request.client_id:
        invoice["client_id"] = request.client_id
    if request.issue_date:
        invoice["issue_date"] = request.issue_date.isoformat()
    if request.due_date:
        invoice["due_date"] = request.due_date.isoformat()
    if request.status:
        invoice["status"] = request.status.value
    if request.terms:
        invoice["terms"] = request.terms
    if request.notes:
        invoice["notes"] = request.notes
    if request.shipping is not None:
        invoice["shipping"] = float(request.shipping)
    if request.handling is not None:
        invoice["handling"] = float(request.handling)
    if request.other_charges is not None:
        invoice["other_charges"] = float(request.other_charges)
    
    # Update jobs if provided
    if hasattr(request, 'jobs') and request.jobs:
        invoice["jobs"] = []
        for job_data in request.jobs:
            # Handle empty date strings
            start_date = job_data.get("start_date")
            if start_date == "":
                start_date = None
            
            job = Job(
                id=job_data.get("id", generate_job_id()),
                name=job_data["name"],
                description=job_data.get("description"),
                job_number=job_data.get("job_number"),
                start_date=start_date,
                status=job_data.get("status", "completed")
            )
            invoice["jobs"].append(job.model_dump())
    
    # Update items if provided
    if request.items:
        invoice["items"] = []
        for item_data in request.items:
            item = InvoiceItem(
                id=item_data.get("id", f"item_{len(invoice['items']) + 1}"),
                job_id=item_data.get("job_id"),
                item_type=item_data.get("item_type", "service"),
                description=item_data["description"],
                quantity=Decimal(str(item_data["quantity"])),
                unit_price=Decimal(str(item_data["unit_price"])),
                unit=item_data.get("unit", "item"),
                tax_rate=Decimal(str(item_data.get("tax_rate", 0))),
                discount_percent=Decimal(str(item_data.get("discount_percent", 0))),
                notes=item_data.get("notes", "")
            )
            invoice["items"].append(item.model_dump())
    
    # Recalculate totals
    invoice_obj = Invoice(**invoice)
    invoice_obj.calculate_totals()
    invoice = invoice_obj.model_dump()
    invoice["updated_at"] = datetime.now().isoformat()
    
    # Save updated invoice
    if update_invoice_data(invoice_id, invoice):
        return {"message": "Invoice updated successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update invoice")

@router.delete("/api/invoices/{invoice_id}")
async def delete_invoice(invoice_id: str) -> Dict[str, str]:
    """Delete an invoice."""
    invoices = load_json_file(INVOICES_FILE, [])
    original_count = len(invoices)
    
    invoices = [i for i in invoices if i["id"] != invoice_id]
    
    if len(invoices) == original_count:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    save_json_file(INVOICES_FILE, invoices)
    return {"message": "Invoice deleted successfully"}

@router.post("/api/invoices/{invoice_id}/send")
async def send_invoice(invoice_id: str) -> Dict[str, str]:
    """Mark invoice as sent."""
    invoice = find_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    invoice["status"] = InvoiceStatus.SENT.value
    invoice["sent_at"] = datetime.now().isoformat()
    invoice["updated_at"] = datetime.now().isoformat()
    
    if update_invoice_data(invoice_id, invoice):
        return {"message": "Invoice marked as sent"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update invoice")

@router.post("/api/invoices/{invoice_id}/payments")
async def add_payment(invoice_id: str, request: CreatePaymentRequest) -> Dict[str, str]:
    """Add payment to invoice."""
    invoice = find_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Create payment
    payment = Payment(
        id=generate_payment_id(),
        invoice_id=invoice_id,
        amount=request.amount,
        payment_date=request.payment_date,
        payment_method=request.payment_method,
        reference=request.reference,
        notes=request.notes
    )
    
    # Add payment to invoice
    invoice["payments"].append(payment.model_dump())
    invoice["updated_at"] = datetime.now().isoformat()
    
    # Check if invoice is fully paid
    invoice_obj = Invoice(**invoice)
    if invoice_obj.is_paid:
        invoice["status"] = InvoiceStatus.PAID.value
        invoice["paid_at"] = datetime.now().isoformat()
    
    if update_invoice_data(invoice_id, invoice):
        return {"message": "Payment added successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to add payment")

@router.get("/api/invoices/{invoice_id}/pdf")
async def generate_invoice_pdf(invoice_id: str) -> FileResponse:
    """Generate PDF invoice."""
    invoice = find_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    client = find_client(invoice.get("client_id", ""))
    company = load_company_info()
    
    # Generate PDF (implementation needed)
    # For now, return JSON response
    return JSONResponse({
        "message": "PDF generation not yet implemented",
        "invoice_id": invoice_id
    })

@router.post("/api/clients")
async def create_client(request: CreateClientRequest) -> Dict[str, Any]:
    """Create a new client."""
    client_data = {
        "id": generate_client_id(),
        "name": request.name,
        "company": request.company,
        "address": request.address.model_dump(),
        "contact": request.contact.model_dump(),
        "tax_id": request.tax_id,
        "notes": request.notes,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    # Save client
    clients = load_json_file(CLIENTS_FILE, [])
    clients.append(client_data)
    save_json_file(CLIENTS_FILE, clients)
    
    return {
        "message": "Client created successfully",
        "client_id": client_data["id"]
    }

# Template routes
@router.get("/templates/{industry_type}")
async def get_invoice_template(industry_type: str) -> Dict[str, Any]:
    """Get invoice template for industry."""
    template_file = BASE_DIR / "templates" / "invoices" / f"{industry_type}.json"
    template = load_json_file(template_file)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return template 