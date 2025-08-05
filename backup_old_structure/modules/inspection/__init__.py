"""
Inspection Module for CheckMate Virtue
Guided inspection flow with subcategories, checkboxes, and 3-color status states.
"""

from app.models import InspectionCreate, InspectionItem
from .routes import router
from .service import load_inspection_template

__all__ = ["InspectionItem", "InspectionCreate", "load_inspection_template", "router"]
