"""
CheckMate Virtue - Multi-Industry Professional Inspection System
A FastAPI-based web application for professional inspections across multiple industries.
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
from auth import setup_auth_middleware, get_user_from_session
from invoice_routes import router as invoice_router

# Create necessary directories
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Available Industries
AVAILABLE_INDUSTRIES = {
    "automotive": {
        "name": "Automotive",
        "icon": "fas fa-car",
        "description": "Vehicle inspections and maintenance",
        "template_file": "templates/industries/automotive.json"
    },
    "construction": {
        "name": "Construction",
        "icon": "fas fa-hard-hat",
        "description": "Site safety and structural integrity",
        "template_file": "templates/industries/construction.json"
    },
    "food_safety": {
        "name": "Food Safety",
        "icon": "fas fa-utensils",
        "description": "Restaurant and kitchen hygiene",
        "template_file": "templates/industries/food_safety.json"
    },
    "healthcare": {
        "name": "Healthcare",
        "icon": "fas fa-hospital",
        "description": "Medical equipment and facility safety",
        "template_file": "templates/industries/healthcare.json"
    },
    "manufacturing": {
        "name": "Manufacturing",
        "icon": "fas fa-industry",
        "description": "Equipment and quality control",
        "template_file": "templates/industries/manufacturing.json"
    },
    "real_estate": {
        "name": "Real Estate",
        "icon": "fas fa-building",
        "description": "Property condition and maintenance",
        "template_file": "templates/industries/real_estate.json"
    },
    "it_datacenter": {
        "name": "IT & Data Centers",
        "icon": "fas fa-server",
        "description": "Infrastructure and security",
        "template_file": "templates/industries/it_datacenter.json"
    },
    "environmental": {
        "name": "Environmental",
        "icon": "fas fa-leaf",
        "description": "Compliance and waste management",
        "template_file": "templates/industries/environmental.json"
    }
}

# Pydantic Models
class IndustryInfo(BaseModel):
    """Industry-specific information model."""
    industry_type: str = Field(..., description="Type of industry")
    facility_name: Optional[str] = Field(None, description="Facility name")
    location: Optional[str] = Field(None, description="Location/address")
    contact_person: Optional[str] = Field(None, description="Contact person")
    phone: Optional[str] = Field(None, description="Contact phone")
    email: Optional[str] = Field(None, description="Contact email")

class VehicleInfo(BaseModel):
    """Vehicle information model (for automotive industry)."""
    year: Optional[str] = Field(None, description="Vehicle year")
    make: Optional[str] = Field(None, description="Vehicle make")
    model: Optional[str] = Field(None, description="Vehicle model")
    vin: Optional[str] = Field(None, description="Vehicle identification number")
    license_plate: Optional[str] = Field(None, description="License plate number")
    mileage: Optional[str] = Field(None, description="Vehicle mileage")

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
    industry_type: str = Field(..., description="Industry type for template selection")

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
    """Get inspection template for specific industry."""
    if industry_type not in AVAILABLE_INDUSTRIES:
        return None
    
    template_file = Path(AVAILABLE_INDUSTRIES[industry_type]["template_file"])
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
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    story.append(Paragraph(f"Inspection Report: {inspection['title']}", title_style))
    story.append(Spacer(1, 12))
    
    # Inspection Details
    details_data = [
        ['Inspection ID:', inspection['id']],
        ['Date:', inspection['date']],
        ['Inspector:', inspection['inspector_name']],
        ['Industry:', inspection['industry_type'].replace('_', ' ').title()],
        ['Status:', inspection['status']]
    ]
    
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
    
    # Categories and Items
    for category in inspection['categories']:
        # Category header
        category_style = ParagraphStyle(
            'CategoryHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20
        )
        story.append(Paragraph(f"Category: {category['name']}", category_style))
        
        if category.get('description'):
            story.append(Paragraph(f"Description: {category['description']}", styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Items table
        if category['items']:
            items_data = [['Item', 'Grade', 'Notes']]
            for item in category['items']:
                items_data.append([
                    item['name'],
                    item['grade'],
                    item['notes'][:50] + '...' if len(item['notes']) > 50 else item['notes']
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
    
    # Build PDF
    doc.build(story)
    return temp_path

# FastAPI App Setup
app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_CREDENTIALS,
    allow_methods=CORS_METHODS,
    allow_headers=CORS_HEADERS,
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Setup auth middleware
setup_auth_middleware(app)

# Include invoice routes
app.include_router(invoice_router)

# Routes
@app.get("/")
async def root(request: Request) -> HTMLResponse:
    """Home page."""
    user = get_user_from_session(request)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@app.get("/industries")
async def list_industries(request: Request) -> HTMLResponse:
    """List available industries."""
    user = get_user_from_session(request)
    return templates.TemplateResponse("industries.html", {
        "request": request, 
        "user": user,
        "industries": AVAILABLE_INDUSTRIES
    })

@app.get("/industries/{industry_id}/new")
async def new_industry_inspection(request: Request, industry_id: str) -> HTMLResponse:
    """New inspection form for specific industry."""
    if industry_id not in AVAILABLE_INDUSTRIES:
        raise HTTPException(status_code=404, detail="Industry not found")
    
    user = get_user_from_session(request)
    return templates.TemplateResponse("new_industry_inspection.html", {
        "request": request, 
        "user": user,
        "industry_id": industry_id,
        "industry": AVAILABLE_INDUSTRIES[industry_id]
    })

@app.get("/api/industries/{industry_id}/template")
async def get_industry_template_api(industry_id: str) -> Dict[str, Any]:
    """Get inspection template for specific industry."""
    template = get_industry_template(industry_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Industry template not found")
    return template

@app.get("/api/inspection-template")
async def get_inspection_template() -> Dict[str, Any]:
    """Get the basic inspection template (for backward compatibility)."""
    template = load_json_file(TEMPLATE_FILE)
    if template is None:
        raise HTTPException(status_code=404, detail="Inspection template not found")
    return template

@app.get("/inspections", response_class=HTMLResponse)
async def list_inspections(request: Request) -> HTMLResponse:
    """List all inspections."""
    inspections = load_json_file(INSPECTIONS_FILE, [])
    user = get_user_from_session(request)
    return templates.TemplateResponse("inspections.html", {
        "request": request,
        "user": user,
        "inspections": inspections
    })

@app.get("/inspections/new", response_class=HTMLResponse)
async def new_inspection(request: Request) -> HTMLResponse:
    """New inspection form (redirect to industries)."""
    return templates.TemplateResponse("redirect_to_industries.html", {"request": request})

@app.post("/api/inspections")
async def create_inspection(inspection: InspectionRequest) -> Dict[str, str]:
    """Create a new inspection."""
    # Load template for the specified industry
    template = get_industry_template(inspection.industry_type)
    if template is None:
        raise HTTPException(status_code=404, detail="Industry template not found")
    
    # Create inspection data
    inspection_data = {
        "id": generate_inspection_id(),
        "title": inspection.title,
        "industry_info": inspection.industry_info.model_dump(),
        "vehicle_info": inspection.vehicle_info.model_dump() if inspection.vehicle_info else None,
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
    
    # Update inspection data
    for category_data in inspection["categories"]:
        if category_data["name"].lower().replace(" ", "_") == category.lower():
            for item_data in category_data["items"]:
                if item_data["name"] == item:
                    item_data["photos"].append(filename)
                    update_inspection_data(inspection_id, inspection)
                    return {"message": "Photo uploaded successfully", "filename": filename}
    
    raise HTTPException(status_code=404, detail="Category or item not found")

@app.put("/api/inspections/{inspection_id}")
async def update_inspection(inspection_id: str, inspection: Dict[str, Any]) -> Dict[str, str]:
    """Update inspection data."""
    if not validate_inspection_data(inspection):
        raise HTTPException(status_code=400, detail="Invalid inspection data")
    
    if update_inspection_data(inspection_id, inspection):
        return {"message": "Inspection updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Inspection not found")

@app.get("/api/inspections/{inspection_id}/report")
async def generate_report(inspection_id: str) -> Dict[str, Any]:
    """Generate inspection report."""
    inspection = find_inspection(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    # Calculate statistics
    total_items = 0
    graded_items = 0
    passed_items = 0
    failed_items = 0
    
    for category in inspection["categories"]:
        for item in category["items"]:
            total_items += 1
            if item["grade"] != "N/A":
                graded_items += 1
                if item["grade"] in ["Pass", "Good", "Excellent"]:
                    passed_items += 1
                elif item["grade"] in ["Fail", "Poor", "Critical"]:
                    failed_items += 1
    
    # Generate report
    report = {
        "inspection_id": inspection["id"],
        "title": inspection["title"],
        "date": inspection["date"],
        "inspector": inspection["inspector_name"],
        "industry_type": inspection["industry_type"],
        "status": inspection["status"],
        "statistics": {
            "total_items": total_items,
            "graded_items": graded_items,
            "passed_items": passed_items,
            "failed_items": failed_items,
            "completion_percentage": (graded_items / total_items * 100) if total_items > 0 else 0,
            "pass_rate": (passed_items / graded_items * 100) if graded_items > 0 else 0
        },
        "categories": inspection["categories"]
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
            media_type="application/pdf",
            filename=f"inspection_report_{inspection_id}.pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", PORT))
    uvicorn.run(app, host=HOST, port=port)
