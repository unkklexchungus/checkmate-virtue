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
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
from pydantic import BaseModel, Field

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
            if item["grade"] == "Pass":
                passed_items += 1
            elif item["grade"] == "Fail":
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

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT) 