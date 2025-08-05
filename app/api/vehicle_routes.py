"""
Vehicle API routes.
"""

from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.services.vehicle_service import VehicleService

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

# Initialize services
vehicle_service = VehicleService()


@router.get("/decode/{vin}", response_model=Dict[str, Any])
async def decode_vin(vin: str) -> Dict[str, Any]:
    """Decode VIN and return vehicle information."""
    try:
        vehicle_data = vehicle_service.decode_vin(vin)
        if vehicle_data:
            return vehicle_data
        else:
            raise HTTPException(status_code=404, detail="VIN not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/test-vin", response_class=HTMLResponse)
async def test_vin_page(request: Request) -> HTMLResponse:
    """Render VIN test page."""
    from app.main import templates
    
    return templates.TemplateResponse(
        "test_vin_frontend.html",
        {"request": request},
    )


@router.get("/test-vin-simple", response_class=HTMLResponse)
async def test_vin_simple_page(request: Request) -> HTMLResponse:
    """Render simple VIN test page."""
    from app.main import templates
    
    return templates.TemplateResponse(
        "test_vin_simple.html",
        {"request": request},
    ) 