from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, Any, Optional
import os
from pathlib import Path
from datetime import datetime
import time
import logging
from functools import wraps

from .models import InspectionCreate
from .service import (
    load_inspection_template, 
    save_inspection, 
    find_inspection, 
    update_inspection,
    generate_inspection_id
)
from .error_responses import (
    handle_inspection_error,
    inspection_not_found,
    vin_decode_failed,
    file_upload_failed,
    template_not_found
)

# Create the main API router with /api/v1 prefix
router = APIRouter(prefix="/api/v1", tags=["Inspection API v1"])

# Create legacy router for backward compatibility
legacy_router = APIRouter(prefix="/inspection", tags=["Inspection Legacy"])

# Templates setup
templates = Jinja2Templates(directory="templates")

# Performance timing decorator for development
def log_request_timing(func):
    """Decorator to log request timing for inspection endpoints in development."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            end_time = time.time()
            duration = (end_time - start_time) * 1000  # Convert to milliseconds
            
            # Log timing info level in development
            logging.info(f"PERF: {func.__name__} completed in {duration:.2f}ms")
            return result
        except Exception as e:
            end_time = time.time()
            duration = (end_time - start_time) * 1000
            logging.error(f"PERF: {func.__name__} failed after {duration:.2f}ms: {str(e)}")
            raise
    return wrapper

# API v1 endpoints
@router.get("/inspection/template")
@log_request_timing
async def get_inspection_template(request: Request):
    """Get the inspection template."""
    try:
        template = load_inspection_template()
        if not template or not template.get("inspection_points"):
            return template_not_found("automotive", str(request.url.path))
        return template
    except Exception as e:
        return handle_inspection_error(e, str(request.url.path))

@router.post("/inspection")
@log_request_timing
async def create_inspection(data: InspectionCreate, request: Request):
    """Create a new inspection."""
    try:
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
                return vin_decode_failed(data.vin, str(e), str(request.url.path))
        
        # Create inspection data
        inspection_data = {
            "id": generate_inspection_id(),
            "vin": data.vin,
            "vehicle_id": data.vehicle_id,
            "vehicle_info": vehicle_info,
            "items": [item.model_dump() for item in data.items],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "draft"
        }
        
        # Save to database
        if save_inspection(inspection_data):
            return {
                "message": "Inspection saved successfully", 
                "inspection_id": inspection_data["id"],
                "data": inspection_data
            }
        else:
            return handle_inspection_error(
                Exception("Failed to save inspection to database"),
                str(request.url.path)
            )
    except Exception as e:
        return handle_inspection_error(e, str(request.url.path))

@router.get("/inspection/{inspection_id}")
@log_request_timing
async def get_inspection(inspection_id: str, request: Request):
    """Get a specific inspection by ID."""
    try:
        inspection = find_inspection(inspection_id)
        if not inspection:
            return inspection_not_found(inspection_id, str(request.url.path))
        return inspection
    except Exception as e:
        return handle_inspection_error(e, str(request.url.path))

@router.patch("/inspection/{inspection_id}")
@log_request_timing
async def save_draft_inspection(inspection_id: str, draft_data: Dict[str, Any], request: Request):
    """Save draft inspection data."""
    try:
        inspection = find_inspection(inspection_id)
        if not inspection:
            return inspection_not_found(inspection_id, str(request.url.path))
        
        # Update inspection with draft data
        inspection.update(draft_data)
        inspection["updated_at"] = datetime.now().isoformat()
        
        if update_inspection(inspection_id, inspection):
            return {"message": "Draft saved successfully"}
        else:
            return handle_inspection_error(
                Exception("Failed to save draft to database"),
                str(request.url.path)
            )
    except Exception as e:
        return handle_inspection_error(e, str(request.url.path))

@router.put("/inspection/{inspection_id}")
@log_request_timing
async def update_inspection_data(inspection_id: str, data: InspectionCreate, request: Request):
    """Update an existing inspection."""
    try:
        inspection = find_inspection(inspection_id)
        if not inspection:
            return inspection_not_found(inspection_id, str(request.url.path))
        
        # Update inspection data
        inspection["items"] = [item.model_dump() for item in data.items]
        inspection["updated_at"] = datetime.now().isoformat()
        
        if update_inspection(inspection_id, inspection):
            return {"message": "Inspection updated successfully"}
        else:
            return handle_inspection_error(
                Exception("Failed to update inspection in database"),
                str(request.url.path)
            )
    except Exception as e:
        return handle_inspection_error(e, str(request.url.path))

@router.post("/inspection/{inspection_id}/photos")
@log_request_timing
async def upload_photo(
    inspection_id: str,
    file: UploadFile = File(...),
    step: str = Form(...),
    subcategory: str = Form(...),
    item: str = Form(...),
    request: Request = None
):
    """Upload photo for inspection item."""
    try:
        # Validate file
        if not file.filename:
            return file_upload_failed("", "No file provided", str(request.url.path) if request else None)
        
        # Check file extension
        allowed_extensions = {".jpg", ".jpeg", ".png", ".gif"}
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            return file_upload_failed(file.filename, "Invalid file type", str(request.url.path) if request else None)
        
        # Check file size (5MB limit)
        if file.size and file.size > 5 * 1024 * 1024:
            return file_upload_failed(file.filename, "File too large (max 5MB)", str(request.url.path) if request else None)
        
        # Find inspection
        inspection = find_inspection(inspection_id)
        if not inspection:
            return inspection_not_found(inspection_id, str(request.url.path) if request else None)
        
        # Create upload directory with consistent path
        upload_dir = Path("static/uploads/inspections")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file with consistent naming
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_step = step.replace(" ", "_").replace("/", "_")
        safe_subcategory = subcategory.replace(" ", "_").replace("/", "_")
        safe_item = item.replace(" ", "_").replace("/", "_")
        filename = f"{inspection_id}_{safe_step}_{safe_subcategory}_{safe_item}_{timestamp}{file_ext}"
        file_path = upload_dir / filename
        
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
        except Exception as e:
            return file_upload_failed(file.filename, f"Failed to save file: {str(e)}", str(request.url.path) if request else None)
        
        # Update inspection data
        photo_url = f"/static/uploads/inspections/{filename}"
        item_found = False
        
        for item_data in inspection["items"]:
            if (item_data["step"] == step and 
                item_data["subcategory"] == subcategory and 
                item_data["item"] == item):
                item_data["photo_url"] = photo_url
                if update_inspection(inspection_id, inspection):
                    return {"message": "Photo uploaded successfully", "photo_url": photo_url}
                else:
                    return handle_inspection_error(
                        Exception("Failed to update inspection with photo"),
                        str(request.url.path) if request else None
                    )
                item_found = True
                break
        
        if not item_found:
            # Create new item if it doesn't exist
            new_item = {
                "step": step,
                "subcategory": subcategory,
                "item": item,
                "status": "",
                "notes": "",
                "photo_url": photo_url
            }
            inspection["items"].append(new_item)
            if update_inspection(inspection_id, inspection):
                return {"message": "Photo uploaded successfully", "photo_url": photo_url}
            else:
                return handle_inspection_error(
                    Exception("Failed to create new inspection item"),
                    str(request.url.path) if request else None
                )
    except Exception as e:
        return handle_inspection_error(e, str(request.url.path) if request else None)

@router.post("/inspection/{inspection_id}/finalize")
@log_request_timing
async def finalize_inspection(inspection_id: str, request: Request):
    """Finalize an inspection, making it read-only."""
    try:
        inspection = find_inspection(inspection_id)
        if not inspection:
            return inspection_not_found(inspection_id, str(request.url.path))
        
        # Check if all required fields are completed
        required_fields = ["title", "inspector_name", "inspector_id"]
        missing_fields = []
        for field in required_fields:
            if not inspection.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            return handle_inspection_error(
                Exception(f"Missing required fields: {', '.join(missing_fields)}"),
                str(request.url.path)
            )
        
        # Update status to finalized
        inspection["status"] = "finalized"
        inspection["finalized_at"] = datetime.now().isoformat()
        inspection["updated_at"] = datetime.now().isoformat()
        
        if update_inspection(inspection_id, inspection):
            return {
                "message": "Inspection finalized successfully",
                "inspection_id": inspection_id,
                "status": "finalized"
            }
        else:
            return handle_inspection_error(
                Exception("Failed to finalize inspection in database"),
                str(request.url.path)
            )
    except Exception as e:
        return handle_inspection_error(e, str(request.url.path))

@router.get("/inspection/{inspection_id}/report")
@log_request_timing
async def generate_inspection_report(
    inspection_id: str, 
    format: str = "html",
    request: Request = None
):
    """Generate an inspection report in HTML or PDF format."""
    try:
        inspection = find_inspection(inspection_id)
        if not inspection:
            return inspection_not_found(inspection_id, str(request.url.path) if request else None)
        
        if format.lower() == "pdf":
            return await generate_pdf_report(inspection)
        else:
            return await generate_html_report(inspection)
    except Exception as e:
        return handle_inspection_error(e, str(request.url.path) if request else None)

# Legacy endpoints for backward compatibility
@legacy_router.get("/template")
async def get_inspection_template_legacy():
    """Get the inspection template (legacy endpoint)."""
    return load_inspection_template()

@legacy_router.get("/form", response_class=HTMLResponse)
async def inspection_form(request: Request):
    """Render the inspection form page."""
    template = load_inspection_template()
    return templates.TemplateResponse("inspection_form.html", {
        "request": request,
        "template": template
    })

@legacy_router.get("/form/{inspection_id}", response_class=HTMLResponse)
async def edit_inspection_form(request: Request, inspection_id: str):
    """Render the inspection form page for editing an existing inspection."""
    template = load_inspection_template()
    return templates.TemplateResponse("inspection_form.html", {
        "request": request,
        "template": template,
        "inspection_id": inspection_id
    })

@legacy_router.get("/list", response_class=HTMLResponse)
async def inspection_list(request: Request):
    """Render the inspection list page."""
    from .service import load_inspections
    inspections = load_inspections()
    return templates.TemplateResponse("inspection_list.html", {
        "request": request,
        "inspections": inspections
    })

@legacy_router.post("/")
async def create_inspection_legacy(data: InspectionCreate):
    """Create a new inspection (legacy endpoint)."""
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
        "updated_at": datetime.now().isoformat(),
        "status": "draft"
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

@legacy_router.get("/{inspection_id}")
async def get_inspection_legacy(inspection_id: str):
    """Get a specific inspection by ID (legacy endpoint)."""
    inspection = find_inspection(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return inspection

@legacy_router.patch("/{inspection_id}")
async def save_draft_inspection_legacy(inspection_id: str, draft_data: Dict[str, Any]):
    """Save draft inspection data (legacy endpoint)."""
    inspection = find_inspection(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    # Update inspection with draft data
    inspection.update(draft_data)
    inspection["updated_at"] = datetime.now().isoformat()
    
    if update_inspection(inspection_id, inspection):
        return {"message": "Draft saved successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save draft")

@legacy_router.put("/{inspection_id}")
async def update_inspection_data_legacy(inspection_id: str, data: InspectionCreate):
    """Update an existing inspection (legacy endpoint)."""
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

@legacy_router.post("/photos")
async def upload_photo_no_id_legacy():
    """Handle photo upload requests without inspection ID (legacy endpoint)."""
    raise HTTPException(
        status_code=400, 
        detail="Inspection ID is required for photo upload"
    )

@legacy_router.post("/{inspection_id}/photos")
async def upload_photo_legacy(
    inspection_id: str,
    file: UploadFile = File(...),
    step: str = Form(...),
    subcategory: str = Form(...),
    item: str = Form(...)
):
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

@legacy_router.post("/{inspection_id}/finalize")
async def finalize_inspection_legacy(inspection_id: str):
    """Finalize an inspection, making it read-only (legacy endpoint)."""
    inspection = find_inspection(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    # Check if all required fields are completed
    required_fields = ["title", "inspector_name", "inspector_id"]
    for field in required_fields:
        if not inspection.get(field):
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    
    # Update status to finalized
    inspection["status"] = "finalized"
    inspection["finalized_at"] = datetime.now().isoformat()
    inspection["updated_at"] = datetime.now().isoformat()
    
    if update_inspection(inspection_id, inspection):
        return {
            "message": "Inspection finalized successfully",
            "inspection_id": inspection_id,
            "status": "finalized"
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to finalize inspection")

@legacy_router.get("/{inspection_id}/report")
async def generate_inspection_report_legacy(
    inspection_id: str, 
    format: str = "html"
):
    """Generate an inspection report in HTML or PDF format (legacy endpoint)."""
    inspection = find_inspection(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    if format.lower() == "pdf":
        return await generate_pdf_report(inspection)
    else:
        return await generate_html_report(inspection)

# Helper functions for report generation
async def generate_html_report(inspection: Dict[str, Any]) -> HTMLResponse:
    """Generate HTML report for inspection."""
    return templates.TemplateResponse("view_inspection.html", {
        "request": Request,
        "inspection": inspection
    })

async def generate_pdf_report(inspection: Dict[str, Any]) -> FileResponse:
    """Generate PDF report for inspection."""
    # This is a placeholder - implement actual PDF generation
    # For now, return a simple text file
    temp_file = Path("temp") / f"inspection_report_{inspection['id']}.txt"
    temp_file.parent.mkdir(exist_ok=True)
    
    with open(temp_file, "w") as f:
        f.write(f"Inspection Report for {inspection.get('title', 'Untitled')}\n")
        f.write(f"Inspection ID: {inspection['id']}\n")
        f.write(f"Status: {inspection.get('status', 'Unknown')}\n")
        f.write(f"Created: {inspection.get('created_at', 'Unknown')}\n")
    
    return FileResponse(
        temp_file,
        media_type="text/plain",
        filename=f"inspection_report_{inspection['id']}.txt"
    )