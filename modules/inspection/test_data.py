"""
Test data for inspection module.
Provides deterministic seed data for testing and development.
"""

import os
from typing import Dict, Any, List
from datetime import datetime
from .service import generate_inspection_id


# Deterministic test data
TEST_INSPECTOR = {
    "id": "INS001",
    "name": "John Doe",
    "email": "john.doe@checkmate-virtue.com",
    "phone": "+1-555-0123",
    "certification": "ASE Certified Master Technician",
    "experience_years": 15,
    "specializations": ["Engine Diagnostics", "Electrical Systems", "Brake Systems"]
}

TEST_VEHICLE = {
    "vin": "1HGBH41JXMN109186",
    "year": "2020",
    "make": "Honda",
    "model": "Civic",
    "trim": "EX",
    "engine": "1.5L Turbo",
    "transmission": "CVT",
    "body_style": "Sedan",
    "fuel_type": "Gasoline",
    "drivetrain": "FWD",
    "country_of_origin": "USA",
    "plant_code": "H",
    "serial_number": "109186"
}

TEST_INSPECTION_TEMPLATE = {
    "title": "Comprehensive Vehicle Inspection",
    "description": "Complete automotive inspection covering all major systems",
    "industry_type": "automotive",
    "version": "1.0",
    "inspection_points": {
        "Exterior": {
            "description": "External vehicle condition assessment",
            "items": [
                {"name": "Body Panels", "type": "visual", "required": True},
                {"name": "Windows & Glass", "type": "visual", "required": True},
                {"name": "Lights & Signals", "type": "functional", "required": True},
                {"name": "Tires & Wheels", "type": "measurement", "required": True}
            ]
        },
        "Interior": {
            "description": "Internal vehicle condition assessment",
            "items": [
                {"name": "Seats & Upholstery", "type": "visual", "required": True},
                {"name": "Dashboard & Controls", "type": "functional", "required": True},
                {"name": "Climate Control", "type": "functional", "required": False},
                {"name": "Audio System", "type": "functional", "required": False}
            ]
        },
        "Engine": {
            "description": "Engine performance and condition assessment",
            "items": [
                {"name": "Engine Start", "type": "functional", "required": True},
                {"name": "Engine Noise", "type": "auditory", "required": True},
                {"name": "Oil Level", "type": "measurement", "required": True},
                {"name": "Coolant Level", "type": "measurement", "required": True}
            ]
        },
        "Brakes": {
            "description": "Brake system assessment",
            "items": [
                {"name": "Brake Pedal Feel", "type": "functional", "required": True},
                {"name": "Brake Fluid Level", "type": "measurement", "required": True},
                {"name": "Brake Pads", "type": "visual", "required": True},
                {"name": "Parking Brake", "type": "functional", "required": True}
            ]
        }
    }
}

TEST_INSPECTION_ITEMS = [
    {
        "step": "Exterior",
        "subcategory": "Body",
        "item": "Body Panels",
        "status": "pass",
        "notes": "All panels in good condition, no major dents or damage",
        "photo_url": None
    },
    {
        "step": "Exterior",
        "subcategory": "Glass",
        "item": "Windows & Glass",
        "status": "pass",
        "notes": "All windows intact, no cracks or chips",
        "photo_url": None
    },
    {
        "step": "Exterior",
        "subcategory": "Lighting",
        "item": "Lights & Signals",
        "status": "pass",
        "notes": "All lights and signals functioning properly",
        "photo_url": None
    },
    {
        "step": "Exterior",
        "subcategory": "Wheels",
        "item": "Tires & Wheels",
        "status": "recommended",
        "notes": "Tires show moderate wear, recommend replacement within 6 months",
        "photo_url": None
    },
    {
        "step": "Interior",
        "subcategory": "Comfort",
        "item": "Seats & Upholstery",
        "status": "pass",
        "notes": "Seats in good condition, minor wear on driver seat",
        "photo_url": None
    },
    {
        "step": "Interior",
        "subcategory": "Controls",
        "item": "Dashboard & Controls",
        "status": "pass",
        "notes": "All dashboard controls functioning properly",
        "photo_url": None
    },
    {
        "step": "Engine",
        "subcategory": "Performance",
        "item": "Engine Start",
        "status": "pass",
        "notes": "Engine starts immediately, no hesitation",
        "photo_url": None
    },
    {
        "step": "Engine",
        "subcategory": "Condition",
        "item": "Engine Noise",
        "status": "pass",
        "notes": "Engine runs smoothly, no unusual noises",
        "photo_url": None
    },
    {
        "step": "Engine",
        "subcategory": "Fluids",
        "item": "Oil Level",
        "status": "pass",
        "notes": "Oil level at proper mark, oil appears clean",
        "photo_url": None
    },
    {
        "step": "Engine",
        "subcategory": "Cooling",
        "item": "Coolant Level",
        "status": "pass",
        "notes": "Coolant level adequate, no visible leaks",
        "photo_url": None
    },
    {
        "step": "Brakes",
        "subcategory": "Operation",
        "item": "Brake Pedal Feel",
        "status": "pass",
        "notes": "Brake pedal has good feel and response",
        "photo_url": None
    },
    {
        "step": "Brakes",
        "subcategory": "Fluids",
        "item": "Brake Fluid Level",
        "status": "pass",
        "notes": "Brake fluid at proper level",
        "photo_url": None
    }
]


def create_test_inspection(
    inspection_id: str = None,
    inspector: Dict[str, Any] = None,
    vehicle: Dict[str, Any] = None,
    items: List[Dict[str, Any]] = None,
    status: str = "draft"
) -> Dict[str, Any]:
    """
    Create a test inspection with deterministic data.
    
    Args:
        inspection_id: Optional custom inspection ID
        inspector: Optional custom inspector data
        vehicle: Optional custom vehicle data
        items: Optional custom inspection items
        status: Inspection status (draft, in_progress, completed, finalized)
    
    Returns:
        Complete inspection data dictionary
    """
    if inspection_id is None:
        inspection_id = generate_inspection_id()
    
    if inspector is None:
        inspector = TEST_INSPECTOR.copy()
    
    if vehicle is None:
        vehicle = TEST_VEHICLE.copy()
    
    if items is None:
        items = TEST_INSPECTION_ITEMS.copy()
    
    return {
        "id": inspection_id,
        "title": "Comprehensive Vehicle Inspection",
        "inspector_name": inspector["name"],
        "inspector_id": inspector["id"],
        "inspector_email": inspector["email"],
        "inspector_phone": inspector["phone"],
        "vin": vehicle["vin"],
        "vehicle_info": vehicle,
        "items": items,
        "status": status,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "notes": "Test inspection created for development and testing purposes",
        "total_items": len(items),
        "completed_items": len([item for item in items if item["status"] in ["pass", "fail"]]),
        "pass_count": len([item for item in items if item["status"] == "pass"]),
        "fail_count": len([item for item in items if item["status"] == "fail"]),
        "recommended_count": len([item for item in items if item["status"] == "recommended"])
    }


def get_test_inspector() -> Dict[str, Any]:
    """Get the test inspector data."""
    return TEST_INSPECTOR.copy()


def get_test_vehicle() -> Dict[str, Any]:
    """Get the test vehicle data."""
    return TEST_VEHICLE.copy()


def get_test_inspection_template() -> Dict[str, Any]:
    """Get the test inspection template."""
    return TEST_INSPECTION_TEMPLATE.copy()


def get_test_inspection_items() -> List[Dict[str, Any]]:
    """Get the test inspection items."""
    return TEST_INSPECTION_ITEMS.copy()


def is_test_environment() -> bool:
    """Check if we're in a test environment."""
    return (
        os.getenv("ENVIRONMENT") == "test" or
        os.getenv("TESTING") == "true" or
        os.getenv("DEBUG") == "true" or
        "pytest" in os.getenv("PYTHONPATH", "")
    )


def should_use_test_data() -> bool:
    """Determine if test data should be used."""
    return is_test_environment() or os.getenv("USE_TEST_DATA") == "true"
