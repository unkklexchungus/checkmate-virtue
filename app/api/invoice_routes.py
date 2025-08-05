"""
Invoice API routes.
"""

from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.models.invoice import Invoice, Client
from app.services.invoice_service import InvoiceService

router = APIRouter(prefix="/invoices", tags=["invoices"])

# Initialize services
invoice_service = InvoiceService()


@router.get("/", response_class=HTMLResponse)
async def list_invoices_page(request: Request) -> HTMLResponse:
    """Render invoices list page."""
    from app.main import templates
    
    invoices = invoice_service.get_all_invoices()
    return templates.TemplateResponse(
        "invoices/list.html",
        {"request": request, "invoices": invoices},
    )


@router.get("/api", response_model=List[Dict[str, Any]])
async def list_invoices_api() -> List[Dict[str, Any]]:
    """Get all invoices as JSON."""
    return invoice_service.get_all_invoices()


@router.get("/new", response_class=HTMLResponse)
async def new_invoice_page(request: Request) -> HTMLResponse:
    """Render new invoice page."""
    from app.main import templates
    
    clients = invoice_service.get_all_clients()
    return templates.TemplateResponse(
        "invoices/new.html",
        {"request": request, "clients": clients},
    )


@router.post("/api", response_model=Dict[str, str])
async def create_invoice(invoice: Invoice) -> Dict[str, str]:
    """Create a new invoice."""
    try:
        invoice_id = invoice_service.create_invoice(invoice)
        return {"id": invoice_id, "message": "Invoice created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{invoice_id}", response_class=HTMLResponse)
async def view_invoice_page(request: Request, invoice_id: str) -> HTMLResponse:
    """Render invoice view page."""
    from app.main import templates
    
    invoice = invoice_service.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return templates.TemplateResponse(
        "invoices/view.html",
        {"request": request, "invoice": invoice},
    )


@router.get("/api/{invoice_id}", response_model=Dict[str, Any])
async def get_invoice_api(invoice_id: str) -> Dict[str, Any]:
    """Get invoice by ID."""
    invoice = invoice_service.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.put("/api/{invoice_id}", response_model=Dict[str, str])
async def update_invoice(
    invoice_id: str, invoice_data: Dict[str, Any]
) -> Dict[str, str]:
    """Update invoice data."""
    try:
        success = invoice_service.update_invoice(invoice_id, invoice_data)
        if success:
            return {"message": "Invoice updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Invoice not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/clients", response_class=HTMLResponse)
async def list_clients_page(request: Request) -> HTMLResponse:
    """Render clients list page."""
    from app.main import templates
    
    clients = invoice_service.get_all_clients()
    return templates.TemplateResponse(
        "invoices/clients.html",
        {"request": request, "clients": clients},
    )


@router.get("/api/clients", response_model=List[Dict[str, Any]])
async def list_clients_api() -> List[Dict[str, Any]]:
    """Get all clients as JSON."""
    return invoice_service.get_all_clients()


@router.post("/api/clients", response_model=Dict[str, str])
async def create_client(client: Client) -> Dict[str, str]:
    """Create a new client."""
    try:
        client_id = invoice_service.create_client(client)
        return {"id": client_id, "message": "Client created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 