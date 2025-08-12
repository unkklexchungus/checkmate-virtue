from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from typing import Dict, Any, Optional
import os
from pathlib import Path
from datetime import datetime

from .models import InspectionCreate
from .service import (
    load_inspection_template, 
    save_inspection, 
    find_inspection, 
    update_inspection,
    generate_inspection_id
)

router = APIRouter(prefix="/inspection", tags=["Inspection"])

# Templates setup
templates = Jinja2Templates(directory="templates")

@router.get("/template")
async def get_inspection_template():
    """Get the inspection template."""
    return load_inspection_template()

@router.get("/form", response_class=HTMLResponse)
async def inspection_form(request: Request):
    """Render the inspection form page."""
    template = load_inspection_template()
    return templates.TemplateResponse("inspection_form.html", {
        "request": request,
        "template": template
    })

@router.get("/list", response_class=HTMLResponse)
async def inspection_list(request: Request):
    """Render the inspection list page."""
    from .service import load_inspections
    inspections = load_inspections()
    return templates.TemplateResponse("inspection_list.html", {
        "request": request,
        "inspections": inspections
    })

@router.post("/")
async def create_inspection(data: InspectionCreate):
    """Create a new inspection."""
    # Auto-fill vehicle data if VIN is included
    vehicle_info = None
    if data.vin:
        try:
            from modules.vehicle_data.service import decode_vin
            decoded_vehicle = await decode_vin(data.vin)
            vehicle_info = {
                "vin": data.vin,
                "year": decoded_vehicle.year,
                "make": decoded_vehicle.make,
                "model": decoded_vehicle.model,
                "trim": decoded_vehicle.trim,
                "engine": decoded_vehicle.engine_displacement,
                "transmission": decoded_vehicle.transmission_type,
                "body_style": decoded_vehicle.body_style,
                "fuel_type": decoded_vehicle.fuel_type,
                "drivetrain": decoded_vehicle.drivetrain,
                "country_of_origin": decoded_vehicle.country_of_origin,
                "plant_code": decoded_vehicle.plant_code,
                "serial_number": decoded_vehicle.serial_number
            }
        except Exception as e:
            print(f"VIN decoding failed: {e}")
            vehicle_info = {"vin": data.vin}
    
    # Create inspection data
    inspection_data = {
        "id": generate_inspection_id(),
        "vin": data.vin,
        "vehicle_id": data.vehicle_id,
        "vehicle_info": vehicle_info,
        "items": [item.model_dump() for item in data.items],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    # Save to database
    if save_inspection(inspection_data):
        return {
            "message": "Inspection saved successfully", 
            "inspection_id": inspection_data["id"],
            "data": inspection_data
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to save inspection")

@router.get("/{inspection_id}")
async def get_inspection(inspection_id: str):
    """Get a specific inspection by ID."""
    inspection = find_inspection(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return inspection

@router.put("/{inspection_id}")
async def update_inspection_data(inspection_id: str, data: InspectionCreate):
    """Update an existing inspection."""
    inspection = find_inspection(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    # Update inspection data
    inspection["items"] = [item.model_dump() for item in data.items]
    inspection["updated_at"] = datetime.now().isoformat()
    
    if update_inspection(inspection_id, inspection):
        return {"message": "Inspection updated successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update inspection")

@router.post("/photos")
async def upload_photo_no_id():
    """Handle photo upload requests without inspection ID."""
    raise HTTPException(
        status_code=400, 
        detail="Inspection ID is required. Use /inspection/{inspection_id}/photos"
    )

@router.post("/{inspection_id}/photos")
async def upload_photo(
    inspection_id: str,
    file: UploadFile = File(...),
    step: str = Form(...),
    subcategory: str = Form(...),
    item: str = Form(...)
):
    """Upload photo for inspection item."""
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file extension
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Check file size (5MB limit)
    if file.size and file.size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")
    
    # Find inspection
    inspection = find_inspection(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    # Create upload directory
    upload_dir = Path("static/uploads/inspections")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{inspection_id}_{step}_{subcategory}_{item}_{timestamp}{file_ext}"
    file_path = upload_dir / filename
    
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Update inspection data
    photo_url = f"/static/uploads/inspections/{filename}"
    for item_data in inspection["items"]:
        if (item_data["step"] == step and 
            item_data["subcategory"] == subcategory and 
            item_data["item"] == item):
            item_data["photo_url"] = photo_url
            update_inspection(inspection_id, inspection)
            return {"message": "Photo uploaded successfully", "photo_url": photo_url}
    
    raise HTTPException(status_code=404, detail="Inspection item not found")

@router.post("/{inspection_id}/finalize")
async def finalize_inspection(inspection_id: str):
    """Finalize an inspection, making it read-only."""
    inspection = find_inspection(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    # Update inspection status to finalized
    inspection["status"] = "finalized"
    inspection["finalized_at"] = datetime.now().isoformat()
    
    if update_inspection(inspection_id, inspection):
        return {"message": "Inspection finalized successfully", "status": "finalized"}
    else:
        raise HTTPException(status_code=500, detail="Failed to finalize inspection")

@router.get("/{inspection_id}/report")
async def generate_inspection_report(
    inspection_id: str, 
    format: str = "html"
):
    """Generate an inspection report in HTML or PDF format."""
    inspection = find_inspection(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    if format.lower() == "pdf":
        return await generate_pdf_report(inspection)
    else:
        return await generate_html_report(inspection)

async def generate_html_report(inspection: Dict[str, Any]) -> HTMLResponse:
    """Generate HTML report for inspection."""
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")
    
    # Calculate summary statistics
    items = inspection.get("items", [])
    total_items = len(items)
    pass_count = sum(1 for item in items if item.get("status") == "pass")
    recommended_count = sum(1 for item in items if item.get("status") == "recommended")
    required_count = sum(1 for item in items if item.get("status") == "required")
    photo_count = sum(1 for item in items if item.get("photo_url"))
    
    report_data = {
        "inspection": inspection,
        "summary": {
            "total_items": total_items,
            "pass_count": pass_count,
            "recommended_count": recommended_count,
            "required_count": required_count,
            "photo_count": photo_count
        },
        "generated_at": datetime.now().isoformat()
    }
    
    return templates.TemplateResponse("inspection_report.html", {
        "request": None,  # We'll need to handle this properly
        "report": report_data
    })

async def generate_pdf_report(inspection: Dict[str, Any]):
    """Generate PDF report for inspection."""
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    import tempfile
    import os
    
    # Create temporary file for PDF
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_file.close()
    
    doc = SimpleDocTemplate(temp_file.name, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title = Paragraph(f"Inspection Report - {inspection.get('id', 'Unknown')}", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Basic information
    story.append(Paragraph(f"<b>Inspection ID:</b> {inspection.get('id', 'Unknown')}", styles['Normal']))
    story.append(Paragraph(f"<b>Date:</b> {inspection.get('created_at', 'Unknown')}", styles['Normal']))
    story.append(Paragraph(f"<b>VIN:</b> {inspection.get('vin', 'Not provided')}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Items table
    items = inspection.get("items", [])
    if items:
        table_data = [['Item', 'Status', 'Notes']]
        for item in items:
            table_data.append([
                item.get('item', 'Unknown'),
                item.get('status', 'Not set'),
                item.get('notes', '')[:50] + '...' if len(item.get('notes', '')) > 50 else item.get('notes', '')
            ])
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
    
    doc.build(story)
    
    # Read the generated PDF
    with open(temp_file.name, 'rb') as f:
        pdf_content = f.read()
    
    # Clean up temporary file
    os.unlink(temp_file.name)
    
    from fastapi.responses import Response
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=inspection_{inspection_id}.pdf"}
    )