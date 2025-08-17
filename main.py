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

import os

from config import *
from app.config.runtime import log_startup_info, validate_base_url
from auth import setup_auth_middleware, get_user_from_session
from invoice_routes import router as invoice_router
from models import CreateInvoiceRequest
from modules.vehicle_data.routes import router as vehicle_router
from modules.inspection.routes import router as inspection_router, legacy_router as inspection_legacy_router
from modules.inspection.api_v1 import router as inspection_api_v1_router
from modules.inspection.test_routes import test_router as inspection_test_router
from modules.inspection.tire_routes import tire_router



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
    print(f"Loading JSON file: {file_path}")
    print(f"File exists: {file_path.exists()}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"Successfully loaded {len(data) if isinstance(data, list) else 'data'} from {file_path}")
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading JSON file {file_path}: {e}")
        return default

def save_json_file(file_path: Path, data: Any) -> None:
    """Save data to JSON file with error handling."""
    print(f"Saving JSON file: {file_path}")
    print(f"Data to save: {len(data) if isinstance(data, list) else 'data'}")
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved data to {file_path}")
    except Exception as e:
        print(f"Error saving JSON file {file_path}: {e}")
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
    print(f"Getting industry template for: {industry_type}")
    
    if industry_type != "automotive":
        print(f"Industry type '{industry_type}' not supported")
        return None
    
    template_file = Path(AUTOMOTIVE_INDUSTRY["template_file"])
    print(f"Loading template from: {template_file}")
    print(f"Template file exists: {template_file.exists()}")
    
    template = load_json_file(template_file)
    print(f"Template loaded: {template is not None}")
    
    return template



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

# Breadcrumb helper function
def get_breadcrumbs(path: str, title: str = None) -> List[Dict[str, str]]:
    """Generate breadcrumb navigation based on the current path."""
    breadcrumbs = []
    
    # Define breadcrumb mappings for different paths
    path_mappings = {
        "/inspection/form": [
            {"text": "Inspections", "url": "/inspection/list", "icon": "fas fa-clipboard-list"},
            {"text": "New Inspection", "url": "/inspection/form", "icon": "fas fa-plus"}
        ],
        "/inspection/list": [
            {"text": "Inspections", "url": "/inspection/list", "icon": "fas fa-clipboard-list"}
        ],
        "/inspections": [
            {"text": "Legacy Inspections", "url": "/inspections", "icon": "fas fa-clipboard-check"}
        ],
        "/invoices": [
            {"text": "Invoices", "url": "/invoices", "icon": "fas fa-file-invoice"}
        ],
        "/invoices/new": [
            {"text": "Invoices", "url": "/invoices", "icon": "fas fa-file-invoice"},
            {"text": "New Invoice", "url": "/invoices/new", "icon": "fas fa-plus"}
        ],
        "/invoices/clients": [
            {"text": "Invoices", "url": "/invoices", "icon": "fas fa-file-invoice"},
            {"text": "Clients", "url": "/invoices/clients", "icon": "fas fa-users"}
        ],
        "/login": [
            {"text": "Login", "url": "/login", "icon": "fas fa-sign-in-alt"}
        ],
        "/test-vin-decoder": [
            {"text": "VIN Decoder Test", "url": "/test-vin-decoder", "icon": "fas fa-barcode"}
        ]
    }
    
    # Get breadcrumbs for the current path
    if path in path_mappings:
        breadcrumbs = path_mappings[path]
    elif path.startswith("/inspection/view/"):
        inspection_id = path.split("/")[-1]
        breadcrumbs = [
            {"text": "Inspections", "url": "/inspection/list", "icon": "fas fa-clipboard-list"},
            {"text": f"Inspection {inspection_id}", "url": path, "icon": "fas fa-eye"}
        ]
    elif path.startswith("/invoices/view/"):
        invoice_id = path.split("/")[-1]
        breadcrumbs = [
            {"text": "Invoices", "url": "/invoices", "icon": "fas fa-file-invoice"},
            {"text": f"Invoice {invoice_id}", "url": path, "icon": "fas fa-eye"}
        ]
    elif path.startswith("/invoices/edit/"):
        invoice_id = path.split("/")[-1]
        breadcrumbs = [
            {"text": "Invoices", "url": "/invoices", "icon": "fas fa-file-invoice"},
            {"text": f"Edit Invoice {invoice_id}", "url": path, "icon": "fas fa-edit"}
        ]
    
    # Add custom title if provided
    if title and breadcrumbs:
        breadcrumbs[-1]["text"] = title
    
    return breadcrumbs

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

# Include tire inspection router
app.include_router(tire_router)

# Include test routes (only in development/test mode)
if os.getenv("DEBUG") == "true" or os.getenv("ENABLE_TEST_ROUTES") == "true":
    app.include_router(inspection_test_router)





# Routes
@app.get("/healthz")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for service monitoring and test setup."""
    return {"status": "ok"}

@app.get("/")
async def root(request: Request) -> HTMLResponse:
    """Home page."""
    user = get_user_from_session(request)
    breadcrumbs = get_breadcrumbs("/")
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "user": user, 
        "breadcrumbs": breadcrumbs
    })

@app.get("/test-vin-decoder")
async def test_vin_decoder(request: Request) -> HTMLResponse:
    """Test page for VIN decoder functionality."""
    breadcrumbs = get_breadcrumbs("/test-vin-decoder")
    return templates.TemplateResponse("test_vin_decoder_fix.html", {
        "request": request,
        "breadcrumbs": breadcrumbs
    })

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request) -> HTMLResponse:
    """Login page."""
    breadcrumbs = get_breadcrumbs("/login")
    return templates.TemplateResponse("login.html", {
        "request": request,
        "breadcrumbs": breadcrumbs
    })

@app.options("/")
async def root_options():
    """Handle OPTIONS requests for root route."""
    return {"message": "OK"}



@app.get("/api/inspection-template")
async def get_inspection_template() -> Dict[str, Any]:
    """Get the automotive inspection template."""
    template = get_industry_template("automotive")
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

# Legacy photo upload endpoint removed - using unified endpoint below





@app.get("/inspections", response_class=HTMLResponse)
async def list_inspections(request: Request) -> HTMLResponse:
    """List all inspections - redirect to new guided inspection list."""
    breadcrumbs = [
        {"text": "Legacy Inspections", "url": "/inspections", "icon": "fas fa-clipboard-check"}
    ]
    return templates.TemplateResponse("redirect_to_guided_inspections.html", {
        "request": request,
        "breadcrumbs": breadcrumbs
    })

@app.get("/inspections/new", response_class=HTMLResponse)
async def new_inspection(request: Request) -> HTMLResponse:
    """New inspection page."""
    breadcrumbs = [
        {"text": "Legacy Inspections", "url": "/inspections", "icon": "fas fa-clipboard-check"},
        {"text": "New Inspection", "url": "/inspections/new", "icon": "fas fa-plus"}
    ]
    return templates.TemplateResponse("redirect_to_guided_inspection.html", {
        "request": request,
        "breadcrumbs": breadcrumbs
    })

@app.get("/inspections/edit/{inspection_id}", response_class=HTMLResponse)
async def edit_inspection(request: Request, inspection_id: str) -> HTMLResponse:
    """Edit existing inspection page."""
    breadcrumbs = [
        {"text": "Legacy Inspections", "url": "/inspections", "icon": "fas fa-clipboard-check"},
        {"text": f"Edit Inspection {inspection_id}", "url": f"/inspections/edit/{inspection_id}", "icon": "fas fa-edit"}
    ]
    return templates.TemplateResponse("redirect_to_guided_inspection.html", {
        "request": request,
        "inspection_id": inspection_id,
        "breadcrumbs": breadcrumbs
    })

@app.post("/api/inspections")
async def create_inspection(inspection: InspectionRequest) -> Dict[str, str]:
    """Create a new inspection with enhanced vehicle data integration."""
    print(f"=== CREATE INSPECTION REQUEST ===")
    print(f"Received inspection request: {inspection}")
    print(f"Inspection industry_type: {inspection.industry_type}")
    
    # Load template for the specified industry
    template = get_industry_template(inspection.industry_type)
    if template is None:
        print(f"ERROR: Template not found for industry_type: {inspection.industry_type}")
        raise HTTPException(status_code=404, detail="Industry template not found")
    
    print(f"Template loaded successfully")
    
    # Enhanced vehicle info processing with VIN decoding
    vehicle_info = None
    if inspection.vehicle_info:
        vehicle_data = inspection.vehicle_info.model_dump()
        print(f"Vehicle data: {vehicle_data}")
        
        # If VIN is provided, try to decode it
        if vehicle_data.get("vin"):
            try:
                from modules.vehicle_data.service import decode_vin
                decoded_vehicle = await decode_vin(vehicle_data["vin"])
                print(f"VIN decoded successfully: {decoded_vehicle}")
                
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
    
    print(f"Generated inspection ID: {inspection_data['id']}")
    
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
    
    print(f"Added {len(inspection_data['categories'])} categories")
    
    # Save inspection
    try:
        inspections = load_json_file(INSPECTIONS_FILE, [])
        print(f"Loaded {len(inspections)} existing inspections")
        inspections.append(inspection_data)
        save_json_file(INSPECTIONS_FILE, inspections)
        print(f"Saved inspection to file: {INSPECTIONS_FILE}")
    except Exception as e:
        print(f"ERROR saving inspection: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save inspection: {str(e)}")
    
    print(f"=== INSPECTION CREATED SUCCESSFULLY ===")
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
    breadcrumbs = [
        {"text": "Inspections", "url": "/inspection/list", "icon": "fas fa-clipboard-list"},
        {"text": f"Inspection {inspection_id}", "url": f"/inspections/{inspection_id}", "icon": "fas fa-eye"}
    ]
    return templates.TemplateResponse("view_inspection.html", {
        "request": request,
        "user": user,
        "inspection": inspection,
        "breadcrumbs": breadcrumbs
    })

@app.post("/api/inspections/{inspection_id}/photos")
async def upload_photo(
    inspection_id: str,
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    item: Optional[str] = Form(None),
    step: Optional[str] = Form(None),
    subcategory: Optional[str] = Form(None)
):
    """Upload photo for inspection item."""
    print(f"=== UPLOAD PHOTO ===")
    print(f"Inspection ID: {inspection_id}")
    print(f"Category: {category}")
    print(f"Item: {item}")
    print(f"Step: {step}")
    print(f"Subcategory: {subcategory}")
    
    # Validate file type
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
    
    print(f"Inspection found: {inspection.get('id')}")
    print(f"Inspection structure: categories={bool(inspection.get('categories'))}, items={bool(inspection.get('items'))}")
    if inspection.get('categories'):
        print(f"Categories: {[cat.get('name') for cat in inspection['categories']]}")
    
    # Handle parameter compatibility - support both legacy and new formats
    if step and subcategory and item:
        # New format: step, subcategory, item
        category_param = f"{step} - {subcategory}"
        item_param = item
    elif category and item:
        # Legacy format: category, item
        category_param = category
        item_param = item
    else:
        raise HTTPException(status_code=400, detail="Missing required parameters. Use either (category, item) or (step, subcategory, item)")
    
    print(f"Category param: {category_param}")
    print(f"Item param: {item_param}")
    
    # Create upload directory with consistent path
    upload_dir = Path("static/uploads/inspections")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file with consistent naming
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_category = category_param.replace(" ", "_").replace("/", "_")
    safe_item = item_param.replace(" ", "_").replace("/", "_")
    filename = f"{inspection_id}_{safe_category}_{safe_item}_{timestamp}{file_ext}"
    file_path = upload_dir / filename
    
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Update inspection data - handle both old and new data structures
    photo_url = f"/static/uploads/inspections/{filename}"
    
    if "categories" in inspection:
        print("Processing categories structure...")
        # Check if categories array is empty
        if not inspection["categories"]:
            print("Categories array is empty, creating new category...")
            # Create the category and item
            new_category = {
                "name": category_param,
                "description": category_param,
                "items": [
                    {
                        "name": item_param,
                        "grade": "N/A",
                        "notes": "",
                        "photos": [filename]
                    }
                ]
            }
            inspection["categories"].append(new_category)
            update_inspection_data(inspection_id, inspection)
            return {"message": "Photo uploaded successfully", "photo_url": photo_url}
        
        # Old structure with categories
        for category_data in inspection["categories"]:
            print(f"Checking category: '{category_data['name']}' vs '{category_param}'")
            # More flexible category matching
            category_match = False
            if category_data["name"].lower().replace(" ", "_") == category_param.lower().replace(" ", "_"):
                category_match = True
            elif category_data["name"].lower() == category_param.lower():
                category_match = True
            elif category_data["name"].lower().replace("_", " ") == category_param.lower().replace("_", " "):
                category_match = True
            
            if category_match:
                print(f"Category match found: {category_data['name']}")
                for item_data in category_data["items"]:
                    print(f"Checking item: '{item_data['name']}' vs '{item_param}'")
                    # More flexible item matching
                    item_match = False
                    if item_data["name"] == item_param:
                        item_match = True
                    elif item_data["name"].lower() == item_param.lower():
                        item_match = True
                    elif item_data["name"].lower().replace(" ", "_") == item_param.lower().replace(" ", "_"):
                        item_match = True
                    
                    if item_match:
                        print(f"Item match found: {item_data['name']}")
                        if "photos" not in item_data:
                            item_data["photos"] = []
                        item_data["photos"].append(filename)
                        update_inspection_data(inspection_id, inspection)
                        return {"message": "Photo uploaded successfully", "photo_url": photo_url}
                print(f"No item match found in category {category_data['name']}")
                
                # If no item match found, create the item
                print(f"Creating new item '{item_param}' in category '{category_data['name']}'")
                new_item = {
                    "name": item_param,
                    "grade": "N/A",
                    "notes": "",
                    "photos": [filename]
                }
                category_data["items"].append(new_item)
                update_inspection_data(inspection_id, inspection)
                return {"message": "Photo uploaded successfully", "photo_url": photo_url}
        
        print("No category match found, creating new category...")
        # If no category match found, create the category and item
        new_category = {
            "name": category_param,
            "description": category_param,
            "items": [
                {
                    "name": item_param,
                    "grade": "N/A",
                    "notes": "",
                    "photos": [filename]
                }
            ]
        }
        inspection["categories"].append(new_category)
        update_inspection_data(inspection_id, inspection)
        return {"message": "Photo uploaded successfully", "photo_url": photo_url}
    elif "items" in inspection:
        print("Processing items structure...")
        # New structure with items array
        if not inspection["items"]:
            # If items array is empty, create a new item for this photo
            new_item = {
                "step": step or category_param.split(" - ")[0] if " - " in category_param else category_param,
                "subcategory": subcategory or category_param.split(" - ")[1] if " - " in category_param else "",
                "item": item_param,
                "status": "",
                "notes": "",
                "photo_url": photo_url
            }
            inspection["items"].append(new_item)
            update_inspection_data(inspection_id, inspection)
            return {"message": "Photo uploaded successfully", "photo_url": photo_url}
        
        # Check existing items
        for item_data in inspection["items"]:
            # Check if this item matches the category and item name
            expected_category = f"{item_data.get('step', '')} - {item_data.get('subcategory', '')}"
            if (expected_category.lower() == category_param.lower() and
                item_data.get("item", "").lower() == item_param.lower()):
                
                item_data["photo_url"] = photo_url
                update_inspection_data(inspection_id, inspection)
                return {"message": "Photo uploaded successfully", "photo_url": photo_url}
        
        # If we get here, the item doesn't exist, so create it
        new_item = {
            "step": step or category_param.split(" - ")[0] if " - " in category_param else category_param,
            "subcategory": subcategory or category_param.split(" - ")[1] if " - " in category_param else "",
            "item": item_param,
            "status": "",
            "notes": "",
            "photo_url": photo_url
        }
        inspection["items"].append(new_item)
        update_inspection_data(inspection_id, inspection)
        return {"message": "Photo uploaded successfully", "photo_url": photo_url}
    
    # If we get here, the structure is unknown
    print("ERROR: Unknown inspection data structure")
    print(f"Inspection keys: {list(inspection.keys())}")
    raise HTTPException(status_code=500, detail="Unknown inspection data structure")


    
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

    log_startup_info()
    validate_base_url()
    
    port = int(os.getenv("PORT", PORT))
    uvicorn.run(app, host=HOST, port=port)
