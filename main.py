"""
CheckMate Virtue - Professional Vehicle Inspection System
A FastAPI-based web application for vehicle inspections.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
import uvicorn
from pydantic import BaseModel, Field
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import tempfile
import os

from config import *

# Create necessary directories
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Pydantic Models
class VehicleInfo(BaseModel):
    """Vehicle information model."""
    year: Optional[str] = Field(None, description="Vehicle year")
    make: Optional[str] = Field(None, description="Vehicle make")
    model: Optional[str] = Field(None, description="Vehicle model")
    vin: Optional[str] = Field(None, description="Vehicle identification number")
    license_plate: Optional[str] = Field(None, description="License plate number")
    mileage: Optional[str] = Field(None, description="Vehicle mileage")

class InspectionRequest(BaseModel):
    """Inspection request model."""
    title: str = Field(
        ..., 
        min_length=MIN_TITLE_LENGTH,
        max_length=MAX_TITLE_LENGTH,
        description="Inspection title"
    )
    vehicle_info: VehicleInfo = Field(..., description="Vehicle information")
    inspector_name: str = Field(
        ..., 
        min_length=MIN_INSPECTOR_NAME_LENGTH,
        max_length=MAX_INSPECTOR_NAME_LENGTH,
        description="Inspector name"
    )
    inspector_id: str = Field(..., description="Inspector ID")

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
    vehicle_info: VehicleInfo
    inspector_name: str
    inspector_id: str
    date: str
    categories: List[InspectionCategory]
    status: str = "draft"

# Utility Functions
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
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save data: {str(e)}")

def generate_inspection_id() -> str:
    """Generate unique inspection ID."""
    return f"{INSPECTION_ID_PREFIX}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def find_inspection(inspection_id: str) -> Optional[Dict[str, Any]]:
    """Find inspection by ID."""
    inspections = load_json_file(INSPECTIONS_FILE, [])
    return next((i for i in inspections if i["id"] == inspection_id), None)

def update_inspection_data(inspection_id: str, updated_data: Dict[str, Any]) -> bool:
    """Update inspection data in file."""
    inspections = load_json_file(INSPECTIONS_FILE, [])
    
    for i, inspection in enumerate(inspections):
        if inspection["id"] == inspection_id:
            inspections[i] = updated_data
            save_json_file(INSPECTIONS_FILE, inspections)
            return True
    return False

def validate_inspection_data(data: Dict[str, Any]) -> bool:
    """Validate inspection data structure."""
    required_fields = ["id", "title", "vehicle_info", "inspector_name", "inspector_id", "date", "categories"]
    return all(field in data for field in required_fields)

def generate_pdf_report(inspection: Dict[str, Any]) -> str:
    """Generate PDF report for inspection."""
    # Create temporary file for PDF
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_path = temp_file.name
    temp_file.close()
    
    # Create PDF document
    doc = SimpleDocTemplate(temp_path, pagesize=A4)
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    normal_style = styles['Normal']
    
    # Title
    story.append(Paragraph("CheckMate Virtue - Vehicle Inspection Report", title_style))
    story.append(Spacer(1, 20))
    
    # Inspection Details
    story.append(Paragraph(f"Inspection: {inspection['title']}", heading_style))
    story.append(Paragraph(f"Date: {inspection['date'].split('T')[0] if 'T' in inspection['date'] else inspection['date']}", normal_style))
    story.append(Paragraph(f"Inspector: {inspection['inspector_name']} (ID: {inspection['inspector_id']})", normal_style))
    story.append(Spacer(1, 20))
    
    # Vehicle Information
    if inspection.get('vehicle_info'):
        vehicle = inspection['vehicle_info']
        story.append(Paragraph("Vehicle Information", heading_style))
        vehicle_data = []
        if vehicle.get('year'): vehicle_data.append(['Year', vehicle['year']])
        if vehicle.get('make'): vehicle_data.append(['Make', vehicle['make']])
        if vehicle.get('model'): vehicle_data.append(['Model', vehicle['model']])
        if vehicle.get('vin'): vehicle_data.append(['VIN', vehicle['vin']])
        if vehicle.get('license_plate'): vehicle_data.append(['License Plate', vehicle['license_plate']])
        if vehicle.get('mileage'): vehicle_data.append(['Mileage', vehicle['mileage']])
        
        if vehicle_data:
            vehicle_table = Table(vehicle_data, colWidths=[2*inch, 4*inch])
            vehicle_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(vehicle_table)
            story.append(Spacer(1, 20))
    
    # Inspection Categories
    story.append(Paragraph("Inspection Results", heading_style))
    
    total_items = 0
    passed_items = 0
    failed_items = 0
    
    for category in inspection.get('categories', []):
        story.append(Paragraph(f"Category: {category['name']}", heading_style))
        
        if category.get('items'):
            item_data = [['Item', 'Grade', 'Notes']]
            for item in category['items']:
                item_data.append([
                    item['name'],
                    item.get('grade', 'N/A'),
                    item.get('notes', '')[:50] + '...' if len(item.get('notes', '')) > 50 else item.get('notes', '')
                ])
                total_items += 1
                if item.get('grade') == 'PASS':
                    passed_items += 1
                elif item.get('grade') == 'REC':
                    failed_items += 1
                elif item.get('grade') == 'REQ':
                    failed_items += 1
            
            item_table = Table(item_data, colWidths=[2.5*inch, 1*inch, 2.5*inch])
            item_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.white])
            ]))
            story.append(item_table)
            story.append(Spacer(1, 15))
    
    # Summary
    story.append(Paragraph("Summary", heading_style))
    completion_rate = (passed_items + failed_items) / total_items * 100 if total_items > 0 else 0
    
    summary_data = [
        ['Total Items', str(total_items)],
        ['Passed', str(passed_items)],
        ['Failed', str(failed_items)],
        ['Completion Rate', f"{completion_rate:.1f}%"]
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold')
    ]))
    story.append(summary_table)
    
    # Build PDF
    doc.build(story)
    return temp_path

# FastAPI App
app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_CREDENTIALS,
    allow_methods=CORS_METHODS,
    allow_headers=CORS_HEADERS,
)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Routes
@app.get("/")
async def root(request: Request) -> HTMLResponse:
    """Home page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/inspection-template")
async def get_inspection_template() -> Dict[str, Any]:
    """Get the basic inspection template."""
    template = load_json_file(TEMPLATE_FILE)
    if template is None:
        raise HTTPException(status_code=404, detail="Inspection template not found")
    return template

@app.get("/inspections", response_class=HTMLResponse)
async def list_inspections(request: Request) -> HTMLResponse:
    """List all inspections."""
    inspections = load_json_file(INSPECTIONS_FILE, [])
    return templates.TemplateResponse("inspections.html", {
        "request": request,
        "inspections": inspections
    })

@app.get("/inspections/new", response_class=HTMLResponse)
async def new_inspection(request: Request) -> HTMLResponse:
    """New inspection form."""
    return templates.TemplateResponse("new_inspection.html", {"request": request})

@app.post("/api/inspections")
async def create_inspection(inspection: InspectionRequest) -> Dict[str, str]:
    """Create a new inspection."""
    # Load template
    template = load_json_file(TEMPLATE_FILE, {"inspection_points": {}})
    
    # Create inspection data
    inspection_data = {
        "id": generate_inspection_id(),
        "title": inspection.title,
        "vehicle_info": inspection.vehicle_info.dict(),
        "inspector_name": inspection.inspector_name,
        "inspector_id": inspection.inspector_id,
        "date": datetime.now().isoformat(),
        "categories": [],
        "status": DEFAULT_INSPECTION_STATUS
    }
    
    # Add categories from template
    for category_name, category_data in template["inspection_points"].items():
        category = {
            "name": category_name.replace("_", " ").title(),
            "description": category_data.get("description", ""),
            "items": []
        }
        
        for item_name in category_data.get("items", []):
            category["items"].append({
                "name": item_name,
                "grade": "N/A",
                "notes": "",
                "photos": []
            })
        
        inspection_data["categories"].append(category)
    
    # Save inspection
    inspections = load_json_file(INSPECTIONS_FILE, [])
    inspections.append(inspection_data)
    save_json_file(INSPECTIONS_FILE, inspections)
    
    return {
        "message": "Inspection created successfully", 
        "inspection_id": inspection_data["id"]
    }

@app.get("/inspections/{inspection_id}", response_class=HTMLResponse)
async def view_inspection(request: Request, inspection_id: str) -> HTMLResponse:
    """View a specific inspection."""
    inspection = find_inspection(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    return templates.TemplateResponse("view_inspection.html", {
        "request": request,
        "inspection": inspection
    })

@app.post("/api/inspections/{inspection_id}/photos")
async def upload_photo(
    inspection_id: str,
    file: UploadFile = File(...),
    category: str = Form(...),
    item: str = Form(...)
) -> Dict[str, str]:
    """Upload photo for inspection item."""
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Save file
    filename = f"{inspection_id}_{category}_{item}_{file.filename}"
    filepath = UPLOAD_DIR / filename
    
    try:
        content = await file.read()
        with open(filepath, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Update inspection with photo
    inspection = find_inspection(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    photo_path = f"/static/uploads/{filename}"
    
    for category_obj in inspection["categories"]:
        if category_obj["name"].lower().replace(" ", "_") == category:
            for item_obj in category_obj["items"]:
                if item_obj["name"].lower().replace(" ", "_") == item:
                    item_obj["photos"].append(photo_path)
                    update_inspection_data(inspection_id, inspection)
                    return {"message": "Photo uploaded successfully"}
    
    raise HTTPException(status_code=404, detail="Category or item not found")

@app.put("/api/inspections/{inspection_id}")
async def update_inspection(inspection_id: str, inspection: Dict[str, Any]) -> Dict[str, str]:
    """Update an existing inspection."""
    # Validate inspection data
    if not validate_inspection_data(inspection):
        raise HTTPException(status_code=400, detail="Invalid inspection data structure")
    
    if not update_inspection_data(inspection_id, inspection):
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    return {"message": "Inspection updated successfully"}

@app.get("/api/inspections/{inspection_id}/report")
async def generate_report(inspection_id: str) -> Dict[str, Any]:
    """Generate inspection report."""
    inspection = find_inspection(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    # Calculate summary statistics
    total_items = 0
    passed_items = 0
    failed_items = 0
    
    for category in inspection["categories"]:
        for item in category["items"]:
            total_items += 1
            if item["grade"] == "PASS":
                passed_items += 1
            elif item["grade"] == "REC":
                failed_items += 1
            elif item["grade"] == "REQ":
                failed_items += 1
    
    completion_rate = (
        (passed_items + failed_items) / total_items * 100 
        if total_items > 0 else 0
    )
    
    report = {
        "inspection_id": inspection_id,
        "title": inspection["title"],
        "vehicle_info": inspection["vehicle_info"],
        "inspector": {
            "name": inspection["inspector_name"],
            "id": inspection["inspector_id"]
        },
        "date": inspection["date"],
        "categories": inspection["categories"],
        "summary": {
            "total_items": total_items,
            "passed": passed_items,
            "failed": failed_items,
            "completion_rate": completion_rate
        }
    }
    
    return report

@app.get("/api/inspections/{inspection_id}/report/pdf")
async def generate_pdf_report_endpoint(inspection_id: str) -> FileResponse:
    """Generate PDF report for inspection."""
    inspection = find_inspection(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    try:
        pdf_path = generate_pdf_report(inspection)
        return FileResponse(
            pdf_path,
            media_type='application/pdf',
            filename=f"inspection_{inspection_id}.pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT) 