"""
Invoice business logic service.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config import settings
from app.models.invoice import Invoice, Client
from app.utils.file_utils import load_json_file, save_json_file


class InvoiceService:
    """Service for handling invoice business logic."""
    
    def __init__(self):
        self.invoices_file = settings.DATA_DIR / "invoices.json"
        self.clients_file = settings.DATA_DIR / "clients.json"
        
        # Ensure data directory exists
        settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Initialize files if they don't exist
        if not self.invoices_file.exists():
            save_json_file(self.invoices_file, [])
        if not self.clients_file.exists():
            save_json_file(self.clients_file, [])
    
    def get_all_invoices(self) -> List[Dict[str, Any]]:
        """Get all invoices."""
        return load_json_file(self.invoices_file, [])
    
    def get_invoice(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """Get invoice by ID."""
        invoices = self.get_all_invoices()
        for invoice in invoices:
            if invoice.get("id") == invoice_id:
                return invoice
        return None
    
    def create_invoice(self, invoice: Invoice) -> str:
        """Create a new invoice."""
        invoice_id = f"inv_{uuid.uuid4().hex[:8]}"
        
        # Create invoice data
        invoice_data = {
            "id": invoice_id,
            "client_id": invoice.client_id,
            "invoice_number": invoice.invoice_number,
            "date": invoice.date.isoformat() if invoice.date else datetime.now().isoformat(),
            "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
            "items": [item.dict() for item in invoice.items],
            "subtotal": invoice.subtotal,
            "tax_rate": invoice.tax_rate,
            "tax_amount": invoice.tax_amount,
            "total": invoice.total,
            "status": invoice.status,
            "notes": invoice.notes,
        }
        
        # Load existing invoices
        invoices = self.get_all_invoices()
        invoices.append(invoice_data)
        
        # Save updated invoices
        save_json_file(self.invoices_file, invoices)
        
        return invoice_id
    
    def update_invoice(self, invoice_id: str, invoice_data: Dict[str, Any]) -> bool:
        """Update invoice data."""
        invoices = self.get_all_invoices()
        
        for i, invoice in enumerate(invoices):
            if invoice.get("id") == invoice_id:
                # Update invoice data
                invoice.update(invoice_data)
                invoice["last_updated"] = datetime.now().isoformat()
                
                # Save updated invoices
                save_json_file(self.invoices_file, invoices)
                return True
        
        return False
    
    def get_all_clients(self) -> List[Dict[str, Any]]:
        """Get all clients."""
        return load_json_file(self.clients_file, [])
    
    def get_client(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get client by ID."""
        clients = self.get_all_clients()
        for client in clients:
            if client.get("id") == client_id:
                return client
        return None
    
    def create_client(self, client: Client) -> str:
        """Create a new client."""
        client_id = f"client_{uuid.uuid4().hex[:8]}"
        
        # Create client data
        client_data = {
            "id": client_id,
            "name": client.name,
            "email": client.email,
            "phone": client.phone,
            "address": client.address,
            "company": client.company,
        }
        
        # Load existing clients
        clients = self.get_all_clients()
        clients.append(client_data)
        
        # Save updated clients
        save_json_file(self.clients_file, clients)
        
        return client_id 