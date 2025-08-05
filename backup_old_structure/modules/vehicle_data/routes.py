"""
Vehicle data API routes for CheckMate Virtue.
"""

from fastapi import APIRouter, HTTPException

from app.models import VehicleInfo
from .service import decode_vin

router = APIRouter(prefix="/vehicle", tags=["Vehicle"])


@router.get("/decode/{vin}", response_model=VehicleInfo)
async def get_vehicle_data(vin: str):
    """
    Decode a VIN and return vehicle information.

    Args:
        vin: Vehicle Identification Number to decode

    Returns:
        VehicleInfo object with decoded vehicle data
    """
    try:
        # Validate VIN format (basic check)
        if not vin or len(vin) < 10:
            raise HTTPException(status_code=400, detail="Invalid VIN format")

        vehicle = await decode_vin(vin)
        return vehicle

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to decode VIN: {str(e)}")


@router.get("/health")
async def vehicle_service_health():
    """
    Health check endpoint for vehicle data service.
    """
    return {"status": "healthy", "service": "vehicle_data"}
