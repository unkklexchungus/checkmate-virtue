"""
Inspection API routes.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import ValidationError

from app.config import settings
from app.models.inspection import (
    InspectionCategory,
    InspectionData,
    InspectionItem,
    InspectionRequest,
)
from app.services.inspection_service import InspectionService
from app.utils.file_utils import save_uploaded_file

router = APIRouter(prefix="/inspections", tags=["inspections"])

# Initialize services
inspection_service = InspectionService()


@router.get("/", response_class=HTMLResponse)
async def list_inspections_page(request: Request) -> HTMLResponse:
    """Render inspections list page."""
    from app.main import templates
    
    inspections = inspection_service.get_all_inspections()
    return templates.TemplateResponse(
        "inspections.html",
        {"request": request, "inspections": inspections},
    )


@router.get("/api", response_model=List[Dict[str, Any]])
async def list_inspections_api() -> List[Dict[str, Any]]:
    """Get all inspections as JSON."""
    return inspection_service.get_all_inspections()


@router.post("/api", response_model=Dict[str, str])
async def create_inspection(inspection: InspectionRequest) -> Dict[str, str]:
    """Create a new inspection."""
    try:
        inspection_id = inspection_service.create_inspection(inspection)
        return {"id": inspection_id, "message": "Inspection created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{inspection_id}", response_class=HTMLResponse)
async def view_inspection_page(request: Request, inspection_id: str) -> HTMLResponse:
    """Render inspection view page."""
    from app.main import templates
    
    inspection = inspection_service.get_inspection(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    return templates.TemplateResponse(
        "view_inspection.html",
        {"request": request, "inspection": inspection},
    )


@router.get("/api/{inspection_id}", response_model=Dict[str, Any])
async def get_inspection_api(inspection_id: str) -> Dict[str, Any]:
    """Get inspection by ID."""
    inspection = inspection_service.get_inspection(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return inspection


@router.put("/api/{inspection_id}", response_model=Dict[str, str])
async def update_inspection(
    inspection_id: str, inspection_data: Dict[str, Any]
) -> Dict[str, str]:
    """Update inspection data."""
    try:
        success = inspection_service.update_inspection(inspection_id, inspection_data)
        if success:
            return {"message": "Inspection updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Inspection not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/{inspection_id}/photos")
async def upload_photo(
    inspection_id: str,
    file: UploadFile = File(...),
    category: str = Form(...),
    item: str = Form(...),
) -> Dict[str, str]:
    """Upload photo for inspection item."""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}",
            )
        
        # Save file
        filename = save_uploaded_file(file, inspection_id, category, item)
        
        # Update inspection with photo
        success = inspection_service.add_photo_to_item(
            inspection_id, category, item, filename
        )
        
        if success:
            return {"message": "Photo uploaded successfully", "filename": filename}
        else:
            raise HTTPException(status_code=404, detail="Inspection not found")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/{inspection_id}/submit")
async def submit_inspection(inspection_id: str) -> Dict[str, str]:
    """Submit inspection for finalization."""
    try:
        success = inspection_service.submit_inspection(inspection_id)
        if success:
            return {"message": "Inspection submitted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Inspection not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api/{inspection_id}/report")
async def generate_report(inspection_id: str) -> Dict[str, Any]:
    """Generate inspection report."""
    try:
        report_data = inspection_service.generate_report(inspection_id)
        if report_data:
            return report_data
        else:
            raise HTTPException(status_code=404, detail="Inspection not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api/{inspection_id}/report/pdf")
async def generate_pdf_report(inspection_id: str) -> FileResponse:
    """Generate PDF report."""
    try:
        pdf_path = inspection_service.generate_pdf_report(inspection_id)
        if pdf_path and pdf_path.exists():
            return FileResponse(
                pdf_path,
                media_type="application/pdf",
                filename=f"inspection_{inspection_id}.pdf",
            )
        else:
            raise HTTPException(status_code=404, detail="Report not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 