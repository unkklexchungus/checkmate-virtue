"""
Pytest configuration and fixtures.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_inspection_data():
    """Sample inspection data for testing."""
    return {
        "title": "Test Inspection",
        "industry_info": {
            "industry_type": "automotive",
            "facility_name": "Test Facility",
            "location": "Test Location",
            "contact_person": "Test Contact",
            "phone": "123-456-7890"
        },
        "vehicle_info": {
            "year": "2020",
            "make": "Toyota",
            "model": "Camry",
            "vin": "1HGBH41JXMN109186",
            "license_plate": "TEST123",
            "mileage": "50000"
        },
        "inspector_name": "Test Inspector",
        "inspector_id": "insp_001",
        "industry_type": "automotive"
    }


@pytest.fixture
def sample_vehicle_data():
    """Sample vehicle data for testing."""
    return {
        "vin": "1HGBH41JXMN109186",
        "year": "2020",
        "make": "Toyota",
        "model": "Camry",
        "trim": "SE",
        "body_style": "Sedan",
        "engine": "2.5L I4",
        "transmission": "Automatic",
        "drivetrain": "FWD",
        "fuel_type": "Gasoline",
        "country_of_origin": "Japan",
        "plant_code": "M",
        "serial_number": "109186"
    } 