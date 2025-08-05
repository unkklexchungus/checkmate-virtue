"""
Inspection business logic service.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config import settings
from app.models.inspection import InspectionRequest, InspectionData
from app.utils.file_utils import load_json_file, save_json_file


class InspectionService:
    """Service for handling inspection business logic."""
    
    def __init__(self):
        self.inspections_file = settings.DATA_DIR / "inspections.json"
        self.templates_dir = settings.TEMPLATES_DIR / "industries"
        
        # Ensure data directory exists
        settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Initialize inspections file if it doesn't exist
        if not self.inspections_file.exists():
            save_json_file(self.inspections_file, [])
    
    def get_all_inspections(self) -> List[Dict[str, Any]]:
        """Get all inspections."""
        return load_json_file(self.inspections_file, [])
    
    def get_inspection(self, inspection_id: str) -> Optional[Dict[str, Any]]:
        """Get inspection by ID."""
        inspections = self.get_all_inspections()
        for inspection in inspections:
            if inspection.get("id") == inspection_id:
                return inspection
        return None
    
    def create_inspection(self, inspection_request: InspectionRequest) -> str:
        """Create a new inspection."""
        inspection_id = f"{settings.INSPECTION_ID_PREFIX}_{uuid.uuid4().hex[:8]}"
        
        # Create inspection data
        inspection_data = {
            "id": inspection_id,
            "title": inspection_request.title,
            "industry_info": inspection_request.industry_info.dict(),
            "vehicle_info": inspection_request.vehicle_info.dict() if inspection_request.vehicle_info else None,
            "inspector_name": inspection_request.inspector_name,
            "inspector_id": inspection_request.inspector_id,
            "date": datetime.now().isoformat(),
            "categories": [],
            "status": settings.DEFAULT_INSPECTION_STATUS,
            "industry_type": inspection_request.industry_type,
        }
        
        # Load existing inspections
        inspections = self.get_all_inspections()
        inspections.append(inspection_data)
        
        # Save updated inspections
        save_json_file(self.inspections_file, inspections)
        
        return inspection_id
    
    def update_inspection(self, inspection_id: str, inspection_data: Dict[str, Any]) -> bool:
        """Update inspection data."""
        inspections = self.get_all_inspections()
        
        for i, inspection in enumerate(inspections):
            if inspection.get("id") == inspection_id:
                # Update inspection data
                inspection.update(inspection_data)
                inspection["last_updated"] = datetime.now().isoformat()
                
                # Save updated inspections
                save_json_file(self.inspections_file, inspections)
                return True
        
        return False
    
    def add_photo_to_item(self, inspection_id: str, category: str, item: str, filename: str) -> bool:
        """Add photo to inspection item."""
        inspection = self.get_inspection(inspection_id)
        if not inspection:
            return False
        
        # Find and update the item
        for cat in inspection.get("categories", []):
            if cat.get("name") == category:
                for item_data in cat.get("items", []):
                    if item_data.get("name") == item:
                        if "photos" not in item_data:
                            item_data["photos"] = []
                        item_data["photos"].append(filename)
                        
                        # Update inspection
                        return self.update_inspection(inspection_id, inspection)
        
        return False
    
    def submit_inspection(self, inspection_id: str) -> bool:
        """Submit inspection for finalization."""
        inspection = self.get_inspection(inspection_id)
        if not inspection:
            return False
        
        # Update status to submitted
        inspection["status"] = "submitted"
        inspection["submitted_date"] = datetime.now().isoformat()
        
        return self.update_inspection(inspection_id, inspection)
    
    def generate_report(self, inspection_id: str) -> Optional[Dict[str, Any]]:
        """Generate inspection report data."""
        inspection = self.get_inspection(inspection_id)
        if not inspection:
            return None
        
        # Add report generation timestamp
        report_data = inspection.copy()
        report_data["report_generated"] = datetime.now().isoformat()
        
        return report_data
    
    def generate_pdf_report(self, inspection_id: str) -> Optional[Path]:
        """Generate PDF report file."""
        from app.utils.pdf_utils import generate_inspection_pdf
        
        inspection = self.get_inspection(inspection_id)
        if not inspection:
            return None
        
        # Generate PDF
        pdf_path = generate_inspection_pdf(inspection)
        return pdf_path
    
    def get_industry_template(self, industry_type: str) -> Optional[Dict[str, Any]]:
        """Get industry template."""
        template_file = self.templates_dir / f"{industry_type}.json"
        if template_file.exists():
            return load_json_file(template_file)
        return None 