from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import logging
from functools import wraps
import time
import json
from datetime import datetime

from .tire_models import TireInspectionCreate, TireInspection, TirePos, TireReading, Light
from .tire_service import (
    get_tire_inspection,
    create_or_update_tire_inspection,
    delete_tire_inspection,
    get_tire_inspection_status,
    validate_tire_reading
)

# Setup logging
logger = logging.getLogger(__name__)

# Create the tire API router
tire_router = APIRouter(prefix="/api/v1", tags=["Tire Inspection API"])

# Custom JSON encoder for datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Performance timing decorator
def log_request_timing(func):
    """Decorator to log request timing for tire endpoints."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            end_time = time.time()
            duration = (end_time - start_time) * 1000
            logger.info(f"PERF: {func.__name__} completed in {duration:.2f}ms")
            return result
        except Exception as e:
            end_time = time.time()
            duration = (end_time - start_time) * 1000
            logger.error(f"PERF: {func.__name__} failed after {duration:.2f}ms: {str(e)}")
            raise
    return wrapper

@tire_router.post("/inspections/{inspection_id}/tires")
@log_request_timing
async def create_or_upsert_tire_inspection(
    inspection_id: str,
    tire_data: TireInspectionCreate,
    request: Request
):
    """Create or update tire inspection for an inspection."""
    try:
        # Validate the tire data
        validation_errors = {}
        
                # Validate individual tire readings
        for pos, reading in tire_data.readings.items():
            errors = validate_tire_reading(reading.model_dump())
            if errors:
                validation_errors[str(pos)] = errors

        if validation_errors:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Validation failed",
                    "details": validation_errors,
                    "path": str(request.url.path)
                }
            )
        
        # Create or update the tire inspection
        tire_inspection = create_or_update_tire_inspection(inspection_id, tire_data)
        
        if tire_inspection:
            # Auto-suggest work items
            suggestions = tire_inspection.auto_suggest_work_items()
            
            return JSONResponse(
                content=json.loads(json.dumps({
                    "success": True,
                    "data": tire_inspection.model_dump(),
                    "suggestions": suggestions,
                    "section_status": tire_inspection.get_section_status().value
                }, cls=DateTimeEncoder))
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to create or update tire inspection"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_or_upsert_tire_inspection: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@tire_router.get("/inspections/{inspection_id}/tires")
@log_request_timing
async def get_tire_inspection_data(inspection_id: str, request: Request):
    """Get tire inspection data for an inspection."""
    try:
        tire_inspection = get_tire_inspection(inspection_id)
        
        if tire_inspection:
            return JSONResponse(
                content=json.loads(json.dumps({
                    "success": True,
                    "data": tire_inspection.model_dump(),
                    "section_status": tire_inspection.get_section_status().value
                }, cls=DateTimeEncoder))
            )
        else:
            # Return empty structure for new tire inspection
            empty_tire_data = TireInspectionCreate().model_dump()
            # Create a default inspection to calculate status
            default_inspection = TireInspection(
                inspection_id=inspection_id,
                readings={
                    TirePos.LF: TireReading(status=Light.GREEN),
                    TirePos.RF: TireReading(status=Light.GREEN),
                    TirePos.LR: TireReading(status=Light.GREEN),
                    TirePos.RR: TireReading(status=Light.GREEN),
                    TirePos.SPARE: TireReading(status=Light.NA)
                },
                alignment_check=Light.GREEN
            )
            return JSONResponse(
                content=json.loads(json.dumps({
                    "success": True,
                    "data": empty_tire_data,
                    "section_status": default_inspection.get_section_status().value
                }, cls=DateTimeEncoder))
            )
            
    except Exception as e:
        logger.error(f"Error in get_tire_inspection_data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@tire_router.put("/inspections/{inspection_id}/tires")
@log_request_timing
async def update_tire_inspection(
    inspection_id: str,
    tire_data: TireInspectionCreate,
    request: Request
):
    """Update tire inspection for an inspection."""
    try:
        # Validate the tire data
        validation_errors = {}
        
                # Validate individual tire readings
        for pos, reading in tire_data.readings.items():
            errors = validate_tire_reading(reading.model_dump())
            if errors:
                validation_errors[str(pos)] = errors

        if validation_errors:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Validation failed",
                    "details": validation_errors,
                    "path": str(request.url.path)
                }
            )
        
        # Update the tire inspection
        tire_inspection = create_or_update_tire_inspection(inspection_id, tire_data)
        
        if tire_inspection:
            # Auto-suggest work items
            suggestions = tire_inspection.auto_suggest_work_items()
            
            return JSONResponse(
                content=json.loads(json.dumps({
                    "success": True,
                    "data": tire_inspection.model_dump(),
                    "suggestions": suggestions,
                    "section_status": tire_inspection.get_section_status().value
                }, cls=DateTimeEncoder))
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to update tire inspection"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_tire_inspection: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@tire_router.delete("/inspections/{inspection_id}/tires")
@log_request_timing
async def delete_tire_inspection_data(inspection_id: str, request: Request):
    """Delete tire inspection data for an inspection."""
    try:
        success = delete_tire_inspection(inspection_id)
        
        if success:
            return JSONResponse(
                content={
                    "success": True,
                    "message": "Tire inspection deleted successfully"
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete tire inspection"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_tire_inspection_data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@tire_router.get("/inspections/{inspection_id}/tires/status")
@log_request_timing
async def get_tire_inspection_status_endpoint(inspection_id: str, request: Request):
    """Get the overall status of a tire inspection."""
    try:
        status = get_tire_inspection_status(inspection_id)
        
        return JSONResponse(
            content={
                "success": True,
                "section_status": status.value if status else Light.GREEN.value
            }
        )
        
    except Exception as e:
        logger.error(f"Error in get_tire_inspection_status_endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@tire_router.post("/inspections/{inspection_id}/tires/validate")
@log_request_timing
async def validate_tire_data(
    inspection_id: str,
    tire_data: TireInspectionCreate,
    request: Request
):
    """Validate tire inspection data without saving."""
    try:
        validation_errors = {}
        
        # Validate individual tire readings
        for pos, reading in tire_data.readings.items():
            errors = validate_tire_reading(reading.dict())
            if errors:
                validation_errors[str(pos)] = errors
        
        # Additional business logic validations
        business_errors = []
        
        # Check for low tread warnings
        for pos, reading in tire_data.readings.items():
            if reading.tread_32nds is not None and reading.tread_32nds < 3:
                business_errors.append(f"{pos.value}: Low tread depth ({reading.tread_32nds}/32)")
        
        # Check PSI logic across all tires
        for pos, reading in tire_data.readings.items():
            if (reading.psi_in is not None and reading.psi_out is not None and 
                reading.psi_out < reading.psi_in):
                business_errors.append(f"{pos.value}: PSI Out ({reading.psi_out}) < PSI In ({reading.psi_in})")
        
        return JSONResponse(
            content={
                "success": True,
                "is_valid": len(validation_errors) == 0,
                "validation_errors": validation_errors,
                "business_warnings": business_errors
            }
        )
        
    except Exception as e:
        logger.error(f"Error in validate_tire_data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
