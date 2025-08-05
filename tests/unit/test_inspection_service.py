"""
Unit tests for inspection service.
"""

import pytest
from unittest.mock import patch, MagicMock

from app.models.inspection import InspectionRequest, IndustryInfo, VehicleInfo
from app.services.inspection_service import InspectionService


class TestInspectionService:
    """Test cases for InspectionService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return InspectionService()
    
    @pytest.fixture
    def sample_request(self):
        """Create sample inspection request."""
        return InspectionRequest(
            title="Test Inspection",
            industry_info=IndustryInfo(
                industry_type="automotive",
                facility_name="Test Facility",
                location="Test Location",
                contact_person="Test Contact",
                phone="123-456-7890"
            ),
            vehicle_info=VehicleInfo(
                year="2020",
                make="Toyota",
                model="Camry",
                vin="1HGBH41JXMN109186"
            ),
            inspector_name="Test Inspector",
            inspector_id="insp_001",
            industry_type="automotive"
        )
    
    def test_create_inspection(self, service, sample_request):
        """Test creating a new inspection."""
        with patch('app.services.inspection_service.save_json_file') as mock_save:
            inspection_id = service.create_inspection(sample_request)
            
            assert inspection_id.startswith("insp_")
            assert len(inspection_id) == 12  # insp_ + 8 hex chars
            mock_save.assert_called_once()
    
    def test_get_inspection(self, service):
        """Test getting inspection by ID."""
        mock_inspections = [
            {"id": "insp_12345678", "title": "Test 1"},
            {"id": "insp_87654321", "title": "Test 2"}
        ]
        
        with patch('app.services.inspection_service.load_json_file', return_value=mock_inspections):
            inspection = service.get_inspection("insp_12345678")
            
            assert inspection is not None
            assert inspection["title"] == "Test 1"
    
    def test_get_inspection_not_found(self, service):
        """Test getting non-existent inspection."""
        mock_inspections = [
            {"id": "insp_12345678", "title": "Test 1"}
        ]
        
        with patch('app.services.inspection_service.load_json_file', return_value=mock_inspections):
            inspection = service.get_inspection("insp_nonexistent")
            
            assert inspection is None
    
    def test_update_inspection(self, service):
        """Test updating inspection."""
        mock_inspections = [
            {"id": "insp_12345678", "title": "Original Title"}
        ]
        
        with patch('app.services.inspection_service.load_json_file', return_value=mock_inspections), \
             patch('app.services.inspection_service.save_json_file') as mock_save:
            
            success = service.update_inspection("insp_12345678", {"title": "Updated Title"})
            
            assert success is True
            mock_save.assert_called_once()
    
    def test_submit_inspection(self, service):
        """Test submitting inspection."""
        mock_inspection = {
            "id": "insp_12345678",
            "title": "Test Inspection",
            "status": "draft"
        }
        
        with patch.object(service, 'get_inspection', return_value=mock_inspection), \
             patch.object(service, 'update_inspection', return_value=True) as mock_update:
            
            success = service.submit_inspection("insp_12345678")
            
            assert success is True
            mock_update.assert_called_once()
    
    def test_get_industry_template(self, service):
        """Test getting industry template."""
        mock_template = {"name": "Automotive Template"}
        
        with patch('app.services.inspection_service.load_json_file', return_value=mock_template):
            template = service.get_industry_template("automotive")
            
            assert template == mock_template 