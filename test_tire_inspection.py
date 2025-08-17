#!/usr/bin/env python3
"""
Test suite for tire inspection functionality.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime

from modules.inspection.tire_models import (
    TireInspection, TireInspectionCreate, TireReading, 
    TirePos, Light
)
from modules.inspection.tire_service import (
    get_tire_inspection, create_or_update_tire_inspection,
    delete_tire_inspection, get_tire_inspection_status,
    validate_tire_reading
)
from main import app

# Test client
client = TestClient(app)

class TestTireModels:
    """Test tire inspection models."""
    
    def test_tire_reading_validation(self):
        """Test tire reading validation."""
        # Valid reading
        reading = TireReading(
            psi_in=32.0,
            psi_out=35.0,
            tread_32nds=7.0,
            status=Light.GREEN
        )
        assert reading.psi_in == 32.0
        assert reading.psi_out == 35.0
        assert reading.tread_32nds == 7.0
        assert reading.status == Light.GREEN
        
        # Test PSI validation
        with pytest.raises(ValueError, match="PSI must be between 0 and 80"):
            TireReading(psi_in=85.0)
            
        with pytest.raises(ValueError, match="PSI must be between 0 and 80"):
            TireReading(psi_out=-5.0)
            
        # Test tread validation
        with pytest.raises(ValueError, match="Tread must be between 0 and 20"):
            TireReading(tread_32nds=25.0)
            
        with pytest.raises(ValueError, match="Tread must be between 0 and 20"):
            TireReading(tread_32nds=-1.0)
    
    def test_tire_inspection_creation(self):
        """Test tire inspection creation."""
        readings = {
            TirePos.LF: TireReading(psi_in=32, psi_out=35, tread_32nds=7, status=Light.GREEN),
            TirePos.RF: TireReading(psi_in=30, psi_out=35, tread_32nds=6, status=Light.YELLOW),
            TirePos.LR: TireReading(psi_in=28, psi_out=35, tread_32nds=5, status=Light.YELLOW),
            TirePos.RR: TireReading(psi_in=34, psi_out=35, tread_32nds=7, status=Light.GREEN),
            TirePos.SPARE: TireReading(psi_in=45, psi_out=45, tread_32nds=None, status=Light.NA)
        }
        
        inspection = TireInspection(
            inspection_id="test_inspection_123",
            tire_front="Michelin Primacy",
            tire_rear="Michelin Primacy",
            size_front="225/45R17",
            size_rear="225/45R17",
            speed_load_front="94V",
            speed_load_rear="94V",
            readings=readings,
            rotation=True,
            balance=False,
            maintenance=False,
            tire_wear_concern=True,
            alignment_check=Light.YELLOW,
            cond_inner_wear=True,
            cond_cupping_feather=True
        )
        
        assert inspection.inspection_id == "test_inspection_123"
        assert inspection.tire_front == "Michelin Primacy"
        assert len(inspection.readings) == 5
        assert inspection.readings[TirePos.LF].status == Light.GREEN
        assert inspection.readings[TirePos.RF].status == Light.YELLOW
        assert inspection.alignment_check == Light.YELLOW
        assert inspection.rotation is True
        assert inspection.cond_inner_wear is True
    
    def test_section_status_calculation(self):
        """Test section status calculation logic."""
        # Test GREEN status
        readings = {
            TirePos.LF: TireReading(status=Light.GREEN),
            TirePos.RF: TireReading(status=Light.GREEN),
            TirePos.LR: TireReading(status=Light.GREEN),
            TirePos.RR: TireReading(status=Light.GREEN)
        }
        inspection = TireInspection(
            inspection_id="test_123",
            readings=readings,
            alignment_check=Light.GREEN
        )
        assert inspection.get_section_status() == Light.GREEN
        
        # Test YELLOW status
        readings[TirePos.RF].status = Light.YELLOW
        inspection = TireInspection(
            inspection_id="test_123",
            readings=readings,
            alignment_check=Light.GREEN
        )
        assert inspection.get_section_status() == Light.YELLOW
        
        # Test RED status
        readings[TirePos.LF].status = Light.RED
        inspection = TireInspection(
            inspection_id="test_123",
            readings=readings,
            alignment_check=Light.GREEN
        )
        assert inspection.get_section_status() == Light.RED
        
        # Test alignment RED overrides YELLOW
        readings[TirePos.LF].status = Light.GREEN
        readings[TirePos.RF].status = Light.YELLOW
        inspection = TireInspection(
            inspection_id="test_123",
            readings=readings,
            alignment_check=Light.RED
        )
        assert inspection.get_section_status() == Light.RED
    
    def test_auto_suggestions(self):
        """Test auto-suggestion logic."""
        readings = {
            TirePos.LF: TireReading(tread_32nds=2.0),  # Low tread
            TirePos.RF: TireReading(tread_32nds=7.0),
            TirePos.LR: TireReading(tread_32nds=7.0),
            TirePos.RR: TireReading(tread_32nds=7.0)
        }
        
        inspection = TireInspection(
            inspection_id="test_123",
            readings=readings,
            alignment_check=Light.RED,
            cond_inner_wear=True,
            cond_cupping_feather=True
        )
        
        suggestions = inspection.auto_suggest_work_items()
        assert "rotation" in suggestions
        assert "tire_wear_concern" in suggestions
        assert "balance" in suggestions
        assert "maintenance" in suggestions

class TestTireService:
    """Test tire service functions."""
    
    @patch('modules.inspection.tire_service._load_tire_data')
    @patch('modules.inspection.tire_service._save_tire_data')
    def test_create_tire_inspection(self, mock_save, mock_load):
        """Test creating a new tire inspection."""
        mock_load.return_value = {}
        mock_save.return_value = True
        
        tire_data = TireInspectionCreate(
            tire_front="Michelin Primacy",
            readings={
                TirePos.LF: TireReading(psi_in=32, psi_out=35, status=Light.GREEN)
            }
        )
        
        result = create_or_update_tire_inspection("test_123", tire_data)
        
        assert result is not None
        assert result.inspection_id == "test_123"
        assert result.tire_front == "Michelin Primacy"
        assert result.readings[TirePos.LF].psi_in == 32
        
        mock_save.assert_called_once()
    
    @patch('modules.inspection.tire_service._load_tire_data')
    def test_get_tire_inspection(self, mock_load):
        """Test getting an existing tire inspection."""
        mock_data = {
            "test_123": {
                "id": "tire_456",
                "inspection_id": "test_123",
                "tire_front": "Michelin Primacy",
                "readings": {
                    "LF": {
                        "psi_in": 32.0,
                        "psi_out": 35.0,
                        "tread_32nds": 7.0,
                        "status": "GREEN"
                    }
                },
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
        mock_load.return_value = mock_data
        
        result = get_tire_inspection("test_123")
        
        assert result is not None
        assert result.inspection_id == "test_123"
        assert result.tire_front == "Michelin Primacy"
        assert result.readings[TirePos.LF].psi_in == 32.0
        assert result.readings[TirePos.LF].status == Light.GREEN
    
    def test_validate_tire_reading(self):
        """Test tire reading validation."""
        # Valid reading
        valid_data = {
            "psi_in": 32.0,
            "psi_out": 35.0,
            "tread_32nds": 7.0,
            "status": "GREEN"
        }
        errors = validate_tire_reading(valid_data)
        assert len(errors) == 0
        
        # Invalid PSI
        invalid_psi = {"psi_in": 85.0}
        errors = validate_tire_reading(invalid_psi)
        assert "psi_in" in errors
        
        # Invalid tread
        invalid_tread = {"tread_32nds": 25.0}
        errors = validate_tire_reading(invalid_tread)
        assert "tread_32nds" in errors
        
        # PSI logic error
        psi_logic_error = {"psi_in": 35.0, "psi_out": 30.0}
        errors = validate_tire_reading(psi_logic_error)
        assert "psi_logic" in errors

class TestTireAPI:
    """Test tire inspection API endpoints."""
    
    def test_create_tire_inspection_api(self):
        """Test creating tire inspection via API."""
        tire_data = {
            "tire_front": "Michelin Primacy",
            "tire_rear": "Michelin Primacy",
            "size_front": "225/45R17",
            "size_rear": "225/45R17",
            "speed_load_front": "94V",
            "speed_load_rear": "94V",
            "readings": {
                "LF": {
                    "psi_in": 32.0,
                    "psi_out": 35.0,
                    "tread_32nds": 7.0,
                    "status": "GREEN"
                },
                "RF": {
                    "psi_in": 30.0,
                    "psi_out": 35.0,
                    "tread_32nds": 6.0,
                    "status": "YELLOW"
                }
            },
            "rotation": True,
            "balance": False,
            "maintenance": False,
            "tire_wear_concern": True,
            "alignment_check": "YELLOW",
            "cond_inner_wear": True,
            "cond_cupping_feather": True
        }
        
        with patch('modules.inspection.tire_service.create_or_update_tire_inspection') as mock_create:
            mock_inspection = TireInspection(
                inspection_id="test_123",
                **tire_data
            )
            mock_create.return_value = mock_inspection
            
            response = client.post("/api/v1/inspections/test_123/tires", json=tire_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["section_status"] == "YELLOW"
            assert "suggestions" in data
    
    def test_get_tire_inspection_api(self):
        """Test getting tire inspection via API."""
        with patch('modules.inspection.tire_service.get_tire_inspection') as mock_get:
            # Create a complete mock inspection with all required fields
            readings = {
                TirePos.LF: TireReading(psi_in=32, psi_out=35, status=Light.GREEN),
                TirePos.RF: TireReading(psi_in=32, psi_out=35, status=Light.GREEN),
                TirePos.LR: TireReading(psi_in=32, psi_out=35, status=Light.GREEN),
                TirePos.RR: TireReading(psi_in=32, psi_out=35, status=Light.GREEN),
                TirePos.SPARE: TireReading(psi_in=45, psi_out=45, status=Light.NA)
            }
            mock_inspection = TireInspection(
                inspection_id="test_123",
                tire_front="Michelin Primacy",
                tire_rear="Michelin Primacy",
                size_front="225/45R17",
                size_rear="225/45R17",
                speed_load_front="94V",
                speed_load_rear="94V",
                readings=readings,
                rotation=False,
                balance=False,
                maintenance=False,
                tire_wear_concern=False,
                alignment_check=Light.GREEN,
                cond_even_wear=False,
                cond_inner_wear=False,
                cond_outer_wear=False,
                cond_center_wear=False,
                cond_cupping_feather=False,
                cond_sidewall_damage=False,
                cond_cracking_dryrot=False,
                cond_puncture_object=False,
                cond_bead_damage=False,
                cond_cords_visible=False,
                cond_noise_vibration=False,
                cond_age_over_6y=False
            )
            mock_get.return_value = mock_inspection
            
            response = client.get("/api/v1/inspections/test_123/tires")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["tire_front"] == "Michelin Primacy"
            assert data["section_status"] == "GREEN"
    
    def test_get_tire_inspection_empty(self):
        """Test getting tire inspection when none exists."""
        with patch('modules.inspection.tire_service.get_tire_inspection') as mock_get:
            mock_get.return_value = None
            
            response = client.get("/api/v1/inspections/test_123/tires")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["section_status"] == "GREEN"
    
    def test_validate_tire_data_api(self):
        """Test tire data validation via API."""
        tire_data = {
            "tire_front": "Test Tire",
            "readings": {
                "LF": {
                    "psi_in": 85.0,  # Invalid PSI
                    "psi_out": 35.0,
                    "tread_32nds": 25.0,  # Invalid tread
                    "status": "GREEN"
                },
                "RF": {
                    "psi_in": 32.0,
                    "psi_out": 35.0,
                    "tread_32nds": 7.0,
                    "status": "GREEN"
                },
                "LR": {
                    "psi_in": 32.0,
                    "psi_out": 35.0,
                    "tread_32nds": 7.0,
                    "status": "GREEN"
                },
                "RR": {
                    "psi_in": 32.0,
                    "psi_out": 35.0,
                    "tread_32nds": 7.0,
                    "status": "GREEN"
                },
                "SPARE": {
                    "psi_in": 45.0,
                    "psi_out": 45.0,
                    "tread_32nds": None,
                    "status": "NA"
                }
            },
            "alignment_check": "GREEN"
        }
        
        response = client.post("/api/v1/inspections/test_123/tires/validate", json=tire_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["is_valid"] is False
        assert "LF" in data["validation_errors"]
        assert len(data["business_warnings"]) > 0

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
