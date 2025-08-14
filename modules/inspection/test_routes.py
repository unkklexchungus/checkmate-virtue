"""
Test routes for inspection module.
Only available in development/test mode.
"""

import os
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any, List
import json
from pathlib import Path

from .test_data import (
    create_test_inspection,
    get_test_inspector,
    get_test_vehicle,
    get_test_inspection_template,
    get_test_inspection_items,
    is_test_environment,
    should_use_test_data
)
from .service import (
    save_inspection,
    load_inspections,
    get_inspection_data_file
)
from .error_responses import handle_inspection_error


# Create test router - only available in dev/test mode
test_router = APIRouter(prefix="/test", tags=["Test Routes"])


def check_test_mode():
    """Check if test routes should be available."""
    if not should_use_test_mode():
        raise HTTPException(
            status_code=403,
            detail="Test routes are only available in development/test mode"
        )


def should_use_test_mode() -> bool:
    """Determine if test mode should be enabled."""
    return (
        is_test_environment() or
        os.getenv("ENABLE_TEST_ROUTES") == "true" or
        os.getenv("DEBUG") == "true"
    )


@test_router.post("/reset")
async def reset_test_data(request: Request):
    """Reset all test data to initial state."""
    try:
        check_test_mode()
        
        # Clear existing inspections
        data_file = get_inspection_data_file()
        if data_file.exists():
            data_file.unlink()
        
        # Create fresh test inspection
        test_inspection = create_test_inspection()
        save_inspection(test_inspection)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Test data reset successfully",
                "inspection_id": test_inspection["id"],
                "inspector": get_test_inspector(),
                "vehicle": get_test_vehicle()
            }
        )
    except Exception as e:
        return handle_inspection_error(e, str(request.url.path))


@test_router.post("/seed")
async def seed_test_data(request: Request):
    """Seed test data with multiple inspections."""
    try:
        check_test_mode()
        
        # Create multiple test inspections with different statuses
        test_inspections = []
        
        # Draft inspection
        draft_inspection = create_test_inspection(
            inspection_id="TEST_DRAFT_001",
            status="draft"
        )
        save_inspection(draft_inspection)
        test_inspections.append(draft_inspection)
        
        # In-progress inspection
        progress_inspection = create_test_inspection(
            inspection_id="TEST_PROGRESS_001",
            status="in_progress"
        )
        # Mark some items as completed
        for item in progress_inspection["items"][:6]:
            item["status"] = "pass"
        save_inspection(progress_inspection)
        test_inspections.append(progress_inspection)
        
        # Completed inspection
        completed_inspection = create_test_inspection(
            inspection_id="TEST_COMPLETED_001",
            status="completed"
        )
        # Mark all items as completed
        for item in completed_inspection["items"]:
            item["status"] = "pass"
        save_inspection(completed_inspection)
        test_inspections.append(completed_inspection)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Test data seeded successfully",
                "inspections_created": len(test_inspections),
                "inspection_ids": [insp["id"] for insp in test_inspections]
            }
        )
    except Exception as e:
        return handle_inspection_error(e, str(request.url.path))


@test_router.get("/inspections")
async def get_test_inspections(request: Request):
    """Get all test inspections."""
    try:
        check_test_mode()
        
        inspections = load_inspections()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Test inspections retrieved successfully",
                "count": len(inspections),
                "inspections": inspections
            }
        )
    except Exception as e:
        return handle_inspection_error(e, str(request.url.path))


@test_router.delete("/inspections/{inspection_id}")
async def delete_test_inspection(inspection_id: str, request: Request):
    """Delete a specific test inspection."""
    try:
        check_test_mode()
        
        inspections = load_inspections()
        original_count = len(inspections)
        
        # Filter out the inspection to delete
        filtered_inspections = [
            insp for insp in inspections 
            if insp.get("id") != inspection_id
        ]
        
        if len(filtered_inspections) == original_count:
            return JSONResponse(
                status_code=404,
                content={
                    "message": f"Inspection {inspection_id} not found",
                    "inspection_id": inspection_id
                }
            )
        
        # Save updated inspections
        data_file = get_inspection_data_file()
        with open(data_file, "w") as f:
            json.dump(filtered_inspections, f, indent=2)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Inspection {inspection_id} deleted successfully",
                "inspection_id": inspection_id,
                "remaining_count": len(filtered_inspections)
            }
        )
    except Exception as e:
        return handle_inspection_error(e, str(request.url.path))


@test_router.delete("/inspections")
async def clear_all_test_inspections(request: Request):
    """Clear all test inspections."""
    try:
        check_test_mode()
        
        data_file = get_inspection_data_file()
        if data_file.exists():
            data_file.unlink()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "All test inspections cleared successfully"
            }
        )
    except Exception as e:
        return handle_inspection_error(e, str(request.url.path))


@test_router.get("/inspector")
async def get_test_inspector_data(request: Request):
    """Get test inspector data."""
    try:
        check_test_mode()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Test inspector data retrieved successfully",
                "inspector": get_test_inspector()
            }
        )
    except Exception as e:
        return handle_inspection_error(e, str(request.url.path))


@test_router.get("/vehicle")
async def get_test_vehicle_data(request: Request):
    """Get test vehicle data."""
    try:
        check_test_mode()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Test vehicle data retrieved successfully",
                "vehicle": get_test_vehicle()
            }
        )
    except Exception as e:
        return handle_inspection_error(e, str(request.url.path))


@test_router.get("/template")
async def get_test_template_data(request: Request):
    """Get test inspection template data."""
    try:
        check_test_mode()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Test template data retrieved successfully",
                "template": get_test_inspection_template()
            }
        )
    except Exception as e:
        return handle_inspection_error(e, str(request.url.path))


@test_router.post("/inspection")
async def create_test_inspection_endpoint(request: Request):
    """Create a new test inspection."""
    try:
        check_test_mode()
        
        test_inspection = create_test_inspection()
        save_inspection(test_inspection)
        
        return JSONResponse(
            status_code=201,
            content={
                "message": "Test inspection created successfully",
                "inspection": test_inspection
            }
        )
    except Exception as e:
        return handle_inspection_error(e, str(request.url.path))


@test_router.get("/status")
async def get_test_mode_status(request: Request):
    """Get test mode status and configuration."""
    try:
        return JSONResponse(
            status_code=200,
            content={
                "test_mode_enabled": should_use_test_mode(),
                "test_environment": is_test_environment(),
                "debug_mode": os.getenv("DEBUG") == "true",
                "enable_test_routes": os.getenv("ENABLE_TEST_ROUTES") == "true",
                "environment": os.getenv("ENVIRONMENT", "unknown")
            }
        )
    except Exception as e:
        return handle_inspection_error(e, str(request.url.path))
