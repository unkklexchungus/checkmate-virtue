"""
CheckMate Virtue - Automotive Professional Inspection System
A FastAPI-based web application for professional automotive inspections.
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
from app.config.runtime import log_startup_info, validate_base_url
from auth import setup_auth_middleware, get_user_from_session
from invoice_routes import router as invoice_router
from models import CreateInvoiceRequest
from modules.vehicle_data.routes import router as vehicle_router
from modules.inspection.routes import router as inspection_router, legacy_router as inspection_legacy_router
from modules.inspection.api_v1 import router as inspection_api_v1_router



# Create necessary directories
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Automotive Industry Configuration
AUTOMOTIVE_INDUSTRY = {
    "name": "Automotive",
    "icon": "fas fa-car",
    "description": "Vehicle inspections and maintenance",
    "template_file": "templates/industries/automotive.json"
}

# Pydantic Models
class IndustryInfo(BaseModel):
    """Automotive industry information model."""
    industry_type: str = Field(default="automotive", description="Type of industry")
    facility_name: Optional[str] = Field(None, description="Dealership/Shop name")
    location: Optional[str] = Field(None, description="Location/address")
    contact_person: Optional[str] = Field(None, description="Contact person")
    phone: Optional[str] = Field(None, description="Contact phone")
    email: Optional[str] = Field(None, description="Contact email")

class VehicleInfo(BaseModel):
    """Vehicle information model (for automotive industry) - compatible with comprehensive vehicle data."""
    year: Optional[str] = Field(None, description="Vehicle year")
    make: Optional[str] = Field(None, description="Vehicle make")
    model: Optional[str] = Field(None, description="Vehicle model")
    vin: Optional[str] = Field(None, description="Vehicle identification number")
    license_plate: Optional[str] = Field(None, description="License plate number")
    mileage: Optional[str] = Field(None, description="Vehicle mileage")
    
    # Additional fields for comprehensive vehicle data
    trim: Optional[str] = Field(None, description="Vehicle trim level")
    body_style: Optional[str] = Field(None, description="Vehicle body style")
    engine: Optional[str] = Field(None, description="Engine information")
    transmission: Optional[str] = Field(None, description="Transmission type")
    drivetrain: Optional[str] = Field(None, description="Drivetrain type")
    fuel_type: Optional[str] = Field(None, description="Fuel type")
    country_of_origin: Optional[str] = Field(None, description="Country of origin")
    plant_code: Optional[str] = Field(None, description="Manufacturing plant code")
    serial_number: Optional[str] = Field(None, description="Serial number")
    


class InspectionRequest(BaseModel):
    """Inspection request model with industry support."""
    title: str = Field(
        ..., 
        min_length=MIN_TITLE_LENGTH,
        max_length=MAX_TITLE_LENGTH,
        description="Inspection title"
    )
    industry_info: IndustryInfo = Field(..., description="Industry information")
    vehicle_info: Optional[VehicleInfo] = Field(None, description="Vehicle information (for automotive)")
    inspector_name: str = Field(
        ..., 
        min_length=MIN_INSPECTOR_NAME_LENGTH,
        max_length=MAX_INSPECTOR_NAME_LENGTH,
        description="Inspector name"
    )
    inspector_id: str = Field(..., description="Inspector ID")
    industry_type: str = Field(default="automotive", description="Industry type for template selection")

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
    industry_info: IndustryInfo
    vehicle_info: Optional[VehicleInfo]
    inspector_name: str
    inspector_id: str
    date: str
    categories: List[InspectionCategory]
    status: str = "draft"
    industry_type: str

class InspectionUpdate(BaseModel):
    """Inspection update model with validation."""
    title: str = Field(
        ..., 
        min_length=MIN_TITLE_LENGTH,
        max_length=MAX_TITLE_LENGTH,
        description="Inspection title"
    )
    inspector_name: str = Field(
        ..., 
        min_length=MIN_INSPECTOR_NAME_LENGTH,
        max_length=MAX_INSPECTOR_NAME_LENGTH,
        description="Inspector name"
    )
    inspector_id: str = Field(..., description="Inspector ID")
    vehicle_info: Optional[VehicleInfo] = Field(None, description="Vehicle information")
    categories: List[InspectionCategory] = Field(default_factory=list, description="Inspection categories")
    status: str = Field(default="draft", description="Inspection status")

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
    required_fields = ["id", "title", "industry_info", "inspector_name", "inspector_id", "date", "categories", "industry_type"]
    return all(field in data for field in required_fields)

def get_industry_template(industry_type: str) -> Optional[Dict[str, Any]]:
    """Get inspection template for automotive industry."""
    if industry_type != "automotive":
        return None
    
    template_file = Path(AUTOMOTIVE_INDUSTRY["template_file"])
    return load_json_file(template_file)

def generate_pdf_report(inspection: Dict[str, Any]) -> str:
    """Generate PDF report for inspection."""
    # Create temporary file for PDF
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_path = temp_file.name
    temp_file.close()
    
    # Create PDF document
    doc = SimpleDocTemplate(temp_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Header: Business name, Inspector, VIN/vehicle info, date
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20,
        alignment=TA_CENTER
    )
    story.append(Paragraph("CheckMate Virtue", header_style))
    story.append(Paragraph("Automotive Professional Inspection System", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    story.append(Paragraph(f"Inspection Report: {inspection.get('title', 'Vehicle Inspection')}", title_style))
    story.append(Spacer(1, 12))
    
    # Inspection Details
    details_data = [
        ['Inspection ID:', inspection.get('id', 'N/A')],
        ['Date:', inspection.get('date', inspection.get('created_at', 'N/A'))],
        ['Inspector:', inspection.get('inspector_name', 'N/A')],
        ['Inspector ID:', inspection.get('inspector_id', 'N/A')],
        ['Status:', inspection.get('status', 'N/A')]
    ]
    
    # Add VIN and vehicle information
    if inspection.get('vin'):
        details_data.append(['VIN:', inspection['vin']])
    
    if inspection.get('vehicle_info'):
        vehicle = inspection['vehicle_info']
        if vehicle.get('year') and vehicle.get('make') and vehicle.get('model'):
            details_data.append(['Vehicle:', f"{vehicle['year']} {vehicle['make']} {vehicle['model']}"])
        if vehicle.get('license_plate'):
            details_data.append(['License Plate:', vehicle['license_plate']])
    
    details_table = Table(details_data, colWidths=[2*inch, 4*inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(details_table)
    story.append(Spacer(1, 20))
    
    # Calculate summary totals
    total_items = 0
    pass_items = 0
    recommended_items = 0
    required_items = 0
    na_items = 0
    
    # Categories and Items
    for category in inspection.get('categories', []):
        # Category header
        category_style = ParagraphStyle(
            'CategoryHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20
        )
        story.append(Paragraph(f"Category: {category.get('name', 'Unknown')}", category_style))
        
        if category.get('description'):
            story.append(Paragraph(f"Description: {category['description']}", styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Items table
        if category.get('items'):
            items_data = [['Item', 'Status', 'Notes']]
            for item in category['items']:
                total_items += 1
                grade = item.get('grade', 'N/A').lower()
                
                if grade == 'pass':
                    pass_items += 1
                elif grade == 'recommended':
                    recommended_items += 1
                elif grade == 'required':
                    required_items += 1
                else:
                    na_items += 1
                
                items_data.append([
                    item.get('name', 'Unknown'),
                    item.get('grade', 'N/A'),
                    item.get('notes', '')[:50] + '...' if len(item.get('notes', '')) > 50 else item.get('notes', '')
                ])
            
            items_table = Table(items_data, colWidths=[3*inch, 1*inch, 2*inch])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(items_table)
            story.append(Spacer(1, 12))
    
    # Summary totals
    story.append(Spacer(1, 20))
    summary_style = ParagraphStyle(
        'Summary',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20
    )
    story.append(Paragraph("Summary Totals", summary_style))
    
    summary_data = [
        ['Total Items', 'Pass', 'Recommended', 'Required', 'N/A'],
        [str(total_items), str(pass_items), str(recommended_items), str(required_items), str(na_items)]
    ]
    
    summary_table = Table(summary_data, colWidths=[1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    
    # Build PDF
    doc.build(story)
    return temp_path

# FastAPI App Setup
app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION
)

# CORS middleware - Environment-driven configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Setup auth middleware
setup_auth_middleware(app)

# Global exception handler for 405 Method Not Allowed
@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc: HTTPException):
    """Handle 405 Method Not Allowed errors gracefully."""
    if request.method == "OPTIONS":
        # Handle CORS preflight requests
        return JSONResponse(
            status_code=200,
            content={"message": "OK"},
            headers={
                "Access-Control-Allow-Origin": CORS_ORIGINS[0] if CORS_ORIGINS else "http://localhost:8000",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Credentials": "true",
            }
        )
    
    return JSONResponse(
        status_code=405,
        content={
            "error": "Method Not Allowed",
            "message": f"The {request.method} method is not allowed for this endpoint",
            "allowed_methods": ["GET"] if request.url.path == "/" else []
        }
    )

# Include invoice routes
app.include_router(invoice_router)

# Include vehicle data routes
app.include_router(vehicle_router)

# Include inspection routes (legacy and API v1)
app.include_router(inspection_legacy_router)
app.include_router(inspection_api_v1_router)





# Routes
@app.get("/healthz")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for service monitoring and test setup."""
    return {"status": "ok"}

@app.get("/")
async def root(request: Request) -> HTMLResponse:
    """Home page."""
    user = get_user_from_session(request)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@app.options("/")
async def root_options():
    """Handle OPTIONS requests for root route."""
    return {"message": "OK"}



@app.get("/api/inspection-template")
async def get_inspection_template() -> Dict[str, Any]:
    """Get the basic inspection template (for backward compatibility)."""
    template = load_json_file(TEMPLATE_FILE)
    if template is None:
        raise HTTPException(status_code=404, detail="Inspection template not found")
    return template

# Legacy API endpoints for backward compatibility
@app.get("/api/inspections/{inspection_id}")
async def get_inspection_legacy(inspection_id: str) -> Dict[str, Any]:
    """Get a specific inspection by ID (legacy endpoint)."""
    inspection = find_inspection(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return inspection

@app.patch("/api/inspections/{inspection_id}")
async def save_draft_inspection_legacy(inspection_id: str, draft_data: Dict[str, Any]) -> Dict[str, str]:
    """Save draft inspection data (legacy endpoint)."""
    inspection = find_inspection(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    # Update inspection with draft data
    inspection.update(draft_data)
    inspection["updated_at"] = datetime.now().isoformat()
    
    if update_inspection_data(inspection_id, inspection):
        return {"message": "Draft saved successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save draft")

@app.put("/api/inspections/{inspection_id}")
async def update_inspection_legacy(inspection_id: str, inspection: InspectionUpdate) -> Dict[str, str]:
    """Update inspection data with validation (legacy endpoint)."""
    # Find existing inspection
    existing_inspection = find_inspection(inspection_id)
    if not existing_inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    # Update inspection data with validated fields
    updated_inspection = {
        **existing_inspection,
        "title": inspection.title,
        "inspector_name": inspection.inspector_name,
        "inspector_id": inspection.inspector_id,
        "vehicle_info": inspection.vehicle_info.model_dump() if inspection.vehicle_info else existing_inspection.get("vehicle_info"),
        "categories": [category.model_dump() for category in inspection.categories],
        "status": inspection.status,
        "updated_at": datetime.now().isoformat()
    }
    
    if update_inspection_data(inspection_id, updated_inspection):
        return {"message": "Inspection updated successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update inspection")

@app.post("/api/inspections/{inspection_id}/photos")
async def upload_photo_legacy(
    inspection_id: str,
    file: UploadFile = File(...),
    category: str = Form(...),
    item: str = Form(...)
) -> Dict[str, str]:
    """Upload photo for inspection item (legacy endpoint)."""
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
    upload_dir = Path("static/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{inspection_id}_{category}_{item}_{timestamp}{file_ext}"
    file_path = upload_dir / filename
    
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Update inspection data (simplified for legacy compatibility)
    photo_url = f"/static/uploads/{filename}"
    
    # For legacy compatibility, we'll just return success
    # The actual inspection update would need to be handled differently
    return {"message": "Photo uploaded successfully", "photo_url": photo_url}

@app.get("/api/inspections/{inspection_id}/report/pdf")
async def generate_pdf_report_endpoint_legacy(inspection_id: str) -> FileResponse:
    """Generate PDF report for inspection (legacy endpoint)."""
    inspection = find_inspection(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    # Create a simple text report for now
    temp_file = Path("temp") / f"inspection_report_{inspection_id}.txt"
    temp_file.parent.mkdir(exist_ok=True)
    
    with open(temp_file, "w") as f:
        f.write(f"Inspection Report for {inspection.get('title', 'Untitled')}\n")
        f.write(f"Inspection ID: {inspection_id}\n")
        f.write(f"Status: {inspection.get('status', 'Unknown')}\n")
        f.write(f"Created: {inspection.get('created_at', 'Unknown')}\n")
    
    return FileResponse(
        temp_file,
        media_type="text/plain",
        filename=f"inspection_report_{inspection_id}.txt"
    )

@app.get("/api/inspections/{inspection_id}/report")
async def generate_inspection_report_legacy(
    inspection_id: str, 
    format: str = "html"
) -> HTMLResponse:
    """Generate an inspection report in HTML format (legacy endpoint)."""
    inspection = find_inspection(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    return templates.TemplateResponse("view_inspection.html", {
        "request": Request,
        "inspection": inspection
    })

@app.get("/inspections", response_class=HTMLResponse)
async def list_inspections(request: Request) -> HTMLResponse:
    """List all inspections - redirect to new guided inspection list."""
    return templates.TemplateResponse("redirect_to_guided_inspections.html", {"request": request})

@app.get("/inspections/new", response_class=HTMLResponse)
async def new_inspection(request: Request) -> HTMLResponse:
    """New inspection page."""
    return templates.TemplateResponse("redirect_to_guided_inspection.html", {"request": request})

@app.get("/inspections/edit/{inspection_id}", response_class=HTMLResponse)
async def edit_inspection(request: Request, inspection_id: str) -> HTMLResponse:
    """Edit existing inspection page."""
    return templates.TemplateResponse("redirect_to_guided_inspection.html", {
        "request": request,
        "inspection_id": inspection_id
    })

@app.post("/api/inspections")
async def create_inspection(inspection: InspectionRequest) -> Dict[str, str]:
    """Create a new inspection with enhanced vehicle data integration."""
    # Load template for the specified industry
    template = get_industry_template(inspection.industry_type)
    if template is None:
        raise HTTPException(status_code=404, detail="Industry template not found")
    
    # Enhanced vehicle info processing with VIN decoding
    vehicle_info = None
    if inspection.vehicle_info:
        vehicle_data = inspection.vehicle_info.model_dump()
        
        # If VIN is provided, try to decode it
        if vehicle_data.get("vin"):
            try:
                from modules.vehicle_data.service import decode_vin
                decoded_vehicle = await decode_vin(vehicle_data["vin"])
                
                # Update vehicle info with decoded data, keeping existing values if not found
                if decoded_vehicle.year and not vehicle_data.get("year"):
                    vehicle_data["year"] = decoded_vehicle.year
                if decoded_vehicle.make and not vehicle_data.get("make"):
                    vehicle_data["make"] = decoded_vehicle.make
                if decoded_vehicle.model and not vehicle_data.get("model"):
                    vehicle_data["model"] = decoded_vehicle.model
                if decoded_vehicle.trim and not vehicle_data.get("trim"):
                    vehicle_data["trim"] = decoded_vehicle.trim
                if decoded_vehicle.engine_displacement and not vehicle_data.get("engine"):
                    vehicle_data["engine"] = decoded_vehicle.engine_displacement
                if decoded_vehicle.transmission_type and not vehicle_data.get("transmission"):
                    vehicle_data["transmission"] = decoded_vehicle.transmission_type
                if decoded_vehicle.body_style and not vehicle_data.get("body_style"):
                    vehicle_data["body_style"] = decoded_vehicle.body_style
                if decoded_vehicle.fuel_type and not vehicle_data.get("fuel_type"):
                    vehicle_data["fuel_type"] = decoded_vehicle.fuel_type
                if decoded_vehicle.drivetrain and not vehicle_data.get("drivetrain"):
                    vehicle_data["drivetrain"] = decoded_vehicle.drivetrain
                if decoded_vehicle.country_of_origin and not vehicle_data.get("country_of_origin"):
                    vehicle_data["country_of_origin"] = decoded_vehicle.country_of_origin
                if decoded_vehicle.plant_code and not vehicle_data.get("plant_code"):
                    vehicle_data["plant_code"] = decoded_vehicle.plant_code
                if decoded_vehicle.serial_number and not vehicle_data.get("serial_number"):
                    vehicle_data["serial_number"] = decoded_vehicle.serial_number
                    
            except Exception as e:
                print(f"VIN decoding failed: {e}")
                # Continue with original vehicle data if decoding fails
        
        vehicle_info = vehicle_data
    
    # Create inspection data
    inspection_data = {
        "id": generate_inspection_id(),
        "title": inspection.title,
        "industry_info": inspection.industry_info.model_dump(),
        "vehicle_info": vehicle_info,
        "inspector_name": inspection.inspector_name,
        "inspector_id": inspection.inspector_id,
        "date": datetime.now().isoformat(),
        "categories": [],
        "status": DEFAULT_INSPECTION_STATUS,
        "industry_type": inspection.industry_type
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

@app.post("/api/invoices")
async def create_invoice_canonical(request: CreateInvoiceRequest) -> Dict[str, Any]:
    """Create a new invoice - canonical API endpoint."""
    # Import the invoice creation logic from invoice_routes
    from invoice_routes import create_invoice
    
    # Call the existing invoice creation function
    return await create_invoice(request)

@app.get("/inspections/{inspection_id}", response_class=HTMLResponse)
async def view_inspection(request: Request, inspection_id: str) -> HTMLResponse:
    """View a specific inspection."""
    inspection = find_inspection(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    user = get_user_from_session(request)
    return templates.TemplateResponse("view_inspection.html", {
        "request": request,
        "user": user,
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
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Check file size
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    # Find inspection
    inspection = find_inspection(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    # Save file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{inspection_id}_{category}_{item}_{timestamp}{file_ext}"
    file_path = UPLOAD_DIR / filename
    
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Update inspection data - handle both old and new data structures
    if "categories" in inspection:
        # Old structure with categories
        for category_data in inspection["categories"]:
            if category_data["name"].lower().replace(" ", "_") == category.lower():
                for item_data in category_data["items"]:
                    if item_data["name"] == item:
                        if "photos" not in item_data:
                            item_data["photos"] = []
                        item_data["photos"].append(filename)
                        update_inspection_data(inspection_id, inspection)
                        return {"message": "Photo uploaded successfully", "photo_url": f"/static/uploads/{filename}"}
    elif "items" in inspection:
        # New structure with items array
        if not inspection["items"]:
            # If items array is empty, create a new item for this photo
            new_item = {
                "step": category.split(" - ")[0] if " - " in category else category,
                "subcategory": category.split(" - ")[1] if " - " in category else "",
                "item": item,
                "status": "",
                "notes": "",
                "photo_url": f"/static/uploads/{filename}"
            }
            inspection["items"].append(new_item)
            update_inspection_data(inspection_id, inspection)
            return {"message": "Photo uploaded successfully", "photo_url": f"/static/uploads/{filename}"}
        
        # Check existing items
        for item_data in inspection["items"]:
            # Check if this item matches the category and item name
            # The category parameter contains "step - subcategory" format
            expected_category = f"{item_data.get('step', '')} - {item_data.get('subcategory', '')}"
            if (expected_category.lower() == category.lower() and
                item_data.get("item", "").lower() == item.lower()):
                
                if "photo_url" not in item_data:
                    item_data["photo_url"] = ""
                item_data["photo_url"] = f"/static/uploads/{filename}"
                update_inspection_data(inspection_id, inspection)
                return {"message": "Photo uploaded successfully", "photo_url": f"/static/uploads/{filename}"}
        
        # If we get here, the item doesn't exist, so create it
        new_item = {
            "step": category.split(" - ")[0] if " - " in category else category,
            "subcategory": category.split(" - ")[1] if " - " in category else "",
            "item": item,
            "status": "",
            "notes": "",
            "photo_url": f"/static/uploads/{filename}"
        }
        inspection["items"].append(new_item)
        update_inspection_data(inspection_id, inspection)
        return {"message": "Photo uploaded successfully", "photo_url": f"/static/uploads/{filename}"}


    """Update inspection data with validation."""
    # Find existing inspection
    existing_inspection = find_inspection(inspection_id)
    if not existing_inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    # Update inspection data with validated fields
    updated_inspection = {
        **existing_inspection,
        "title": inspection.title,
        "inspector_name": inspection.inspector_name,
        "inspector_id": inspection.inspector_id,
        "vehicle_info": inspection.vehicle_info.model_dump() if inspection.vehicle_info else existing_inspection.get("vehicle_info"),
        "categories": [category.model_dump() for category in inspection.categories],
        "status": inspection.status,
        "updated_at": datetime.now().isoformat()
    }
    
    if update_inspection_data(inspection_id, updated_inspection):
        return {"message": "Inspection updated successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update inspection")


    
    return report

@app.get("/test-vin")
async def test_vin_page(request: Request) -> HTMLResponse:
    """Test page for VIN decoder functionality."""
    return FileResponse("test_vin_frontend.html")

@app.get("/test-vin-simple")
async def test_vin_simple_page(request: Request) -> HTMLResponse:
    """Simple test page for VIN decoder functionality."""
    return FileResponse("test_vin_simple.html")



if __name__ == "__main__":
    # Log startup information and validate configuration
    log_startup_info()
    validate_base_url()
    
    port = int(os.getenv("PORT", PORT))
    uvicorn.run(app, host=HOST, port=port)
