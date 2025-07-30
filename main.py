from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import json
import os
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

app = FastAPI(
    title="CheckMate Virtue",
    description="Professional Vehicle Inspection System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories
os.makedirs("static/uploads", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("data", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Pydantic models
class VehicleInfo(BaseModel):
    year: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    vin: Optional[str] = None
    license_plate: Optional[str] = None
    mileage: Optional[str] = None

class InspectionRequest(BaseModel):
    title: str
    vehicle_info: VehicleInfo
    inspector_name: str
    inspector_id: str

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/inspection-template")
async def get_inspection_template():
    """Get the basic inspection template from the original APK"""
    try:
        with open("CheckMateVirtue/assets/basic_inspection.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error": "Inspection template not found"}

@app.get("/inspections", response_class=HTMLResponse)
async def list_inspections(request: Request):
    """List all inspections"""
    try:
        with open("data/inspections.json", "r") as f:
            inspections = json.load(f)
    except FileNotFoundError:
        inspections = []
    
    return templates.TemplateResponse("inspections.html", {
        "request": request,
        "inspections": inspections
    })

@app.get("/inspections/new", response_class=HTMLResponse)
async def new_inspection(request: Request):
    """New inspection form"""
    return templates.TemplateResponse("new_inspection.html", {"request": request})

@app.post("/api/inspections")
async def create_inspection(inspection: InspectionRequest):
    """Create a new inspection"""
    # Load template
    try:
        with open("CheckMateVirtue/assets/basic_inspection.json", "r") as f:
            template = json.load(f)
    except FileNotFoundError:
        template = {"inspection_points": {}}
    
    # Create inspection data
    inspection_data = {
        "id": f"insp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "title": inspection.title,
        "vehicle_info": inspection.vehicle_info.dict(),
        "inspector_name": inspection.inspector_name,
        "inspector_id": inspection.inspector_id,
        "date": datetime.now().isoformat(),
        "categories": [],
        "status": "draft"
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
    try:
        with open("data/inspections.json", "r") as f:
            inspections = json.load(f)
    except FileNotFoundError:
        inspections = []
    
    inspections.append(inspection_data)
    
    with open("data/inspections.json", "w") as f:
        json.dump(inspections, f, indent=2)
    
    return {"message": "Inspection created successfully", "inspection_id": inspection_data["id"]}

@app.get("/inspections/{inspection_id}", response_class=HTMLResponse)
async def view_inspection(request: Request, inspection_id: str):
    """View a specific inspection"""
    try:
        with open("data/inspections.json", "r") as f:
            inspections = json.load(f)
    except FileNotFoundError:
        return {"error": "No inspections found"}
    
    inspection = next((i for i in inspections if i["id"] == inspection_id), None)
    if not inspection:
        return {"error": "Inspection not found"}
    
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
):
    """Upload photo for inspection item"""
    # Save file
    filename = f"{inspection_id}_{category}_{item}_{file.filename}"
    filepath = os.path.join("static/uploads", filename)
    
    with open(filepath, "wb") as f:
        content = file.file.read()
        f.write(content)
    
    # Update inspection with photo
    try:
        with open("data/inspections.json", "r") as f:
            inspections = json.load(f)
    except FileNotFoundError:
        return {"error": "No inspections found"}
    
    for inspection in inspections:
        if inspection["id"] == inspection_id:
            for category_obj in inspection["categories"]:
                if category_obj["name"].lower().replace(" ", "_") == category:
                    for item_obj in category_obj["items"]:
                        if item_obj["name"].lower().replace(" ", "_") == item:
                            item_obj["photos"].append(f"/static/uploads/{filename}")
                            break
    
    with open("data/inspections.json", "w") as f:
        json.dump(inspections, f, indent=2)
    
    return {"message": "Photo uploaded successfully"}

@app.put("/api/inspections/{inspection_id}")
async def update_inspection(inspection_id: str, inspection: dict):
    """Update an existing inspection"""
    try:
        with open("data/inspections.json", "r") as f:
            inspections = json.load(f)
    except FileNotFoundError:
        return {"error": "No inspections found"}
    
    # Update existing inspection
    for i, existing in enumerate(inspections):
        if existing["id"] == inspection_id:
            inspections[i] = inspection
            break
    else:
        return {"error": "Inspection not found"}
    
    with open("data/inspections.json", "w") as f:
        json.dump(inspections, f, indent=2)
    
    return {"message": "Inspection updated successfully"}

@app.get("/api/inspections/{inspection_id}/report")
async def generate_report(inspection_id: str):
    """Generate inspection report"""
    try:
        with open("data/inspections.json", "r") as f:
            inspections = json.load(f)
    except FileNotFoundError:
        return {"error": "No inspections found"}
    
    inspection = next((i for i in inspections if i["id"] == inspection_id), None)
    if not inspection:
        return {"error": "Inspection not found"}
    
    # Generate summary
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
            "completion_rate": (passed_items + failed_items) / total_items * 100 if total_items > 0 else 0
        }
    }
    
    return report

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 