import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import os

TEMPLATE_PATH = Path(__file__).parent / "templates.json"
AUTOMOTIVE_TEMPLATE_PATH = Path("templates/industries/automotive.json")

def load_inspection_template() -> Dict[str, Any]:
    """Load the inspection template from JSON file."""
    # Try to load the automotive template first
    try:
        with open(AUTOMOTIVE_TEMPLATE_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback to the default template
        try:
            with open(TEMPLATE_PATH, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"inspection_points": {}}
        except json.JSONDecodeError:
            return {"inspection_points": {}}
    except json.JSONDecodeError:
        # Fallback to the default template
        try:
            with open(TEMPLATE_PATH, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"inspection_points": {}}
        except json.JSONDecodeError:
            return {"inspection_points": {}}

def save_inspection_template(template: Dict[str, Any]) -> bool:
    """Save the inspection template to JSON file."""
    try:
        # Save to automotive template by default
        with open(AUTOMOTIVE_TEMPLATE_PATH, "w") as f:
            json.dump(template, f, indent=2)
        return True
    except Exception:
        return False

def get_inspection_data_file() -> Path:
    """Get the path to the inspection data file."""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    return data_dir / "inspections.json"

def load_inspections() -> list:
    """Load all inspections from the data file and migrate old format to new format."""
    data_file = get_inspection_data_file()
    try:
        with open(data_file, "r") as f:
            inspections = json.load(f)
        
        # Migrate old format inspections to new format
        migrated = False
        for inspection in inspections:
            if needs_migration(inspection):
                migrate_inspection_format(inspection)
                migrated = True
        
        # Save back if migrations were performed
        if migrated:
            with open(data_file, "w") as f:
                json.dump(inspections, f, indent=2)
        
        return inspections
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def needs_migration(inspection: Dict[str, Any]) -> bool:
    """Check if inspection needs migration from old format to new format."""
    # Old format has 'items' array but no 'categories'
    return (
        'items' in inspection and 
        isinstance(inspection['items'], list) and 
        'categories' not in inspection
    )

def migrate_inspection_format(inspection: Dict[str, Any]) -> None:
    """Migrate inspection from old format to new format."""
    if not needs_migration(inspection):
        return
    
    # Group items by step (category)
    categories = {}
    for item in inspection['items']:
        step = item.get('step', 'General')
        if step not in categories:
            categories[step] = {
                'name': step,
                'description': step,
                'items': []
            }
        
        # Convert old item format to new format
        new_item = {
            'name': item.get('item', item.get('name', 'Unknown')),
            'grade': item.get('status', 'N/A'),
            'notes': item.get('notes', ''),
            'photos': [item['photo_url']] if item.get('photo_url') else []
        }
        categories[step]['items'].append(new_item)
    
    # Update inspection with new format
    inspection['categories'] = list(categories.values())
    
    # Remove old format fields
    if 'items' in inspection:
        del inspection['items']
    
    # Ensure required fields exist
    if 'title' not in inspection:
        inspection['title'] = f"Inspection {inspection.get('id', 'Unknown')}"
    
    if 'industry_info' not in inspection:
        inspection['industry_info'] = {
            'industry_type': 'automotive',
            'facility_name': '',
            'location': '',
            'contact_person': '',
            'phone': '',
            'email': ''
        }
    
    if 'status' not in inspection:
        inspection['status'] = 'draft'

def save_inspection(inspection_data: Dict[str, Any]) -> bool:
    """Save a new inspection to the data file."""
    inspections = load_inspections()
    inspections.append(inspection_data)
    
    data_file = get_inspection_data_file()
    try:
        with open(data_file, "w") as f:
            json.dump(inspections, f, indent=2)
        return True
    except Exception:
        return False

def find_inspection(inspection_id: str) -> Optional[Dict[str, Any]]:
    """Find an inspection by ID."""
    inspections = load_inspections()
    return next((i for i in inspections if i.get("id") == inspection_id), None)

def update_inspection(inspection_id: str, updated_data: Dict[str, Any]) -> bool:
    """Update an existing inspection."""
    inspections = load_inspections()
    
    for i, inspection in enumerate(inspections):
        if inspection.get("id") == inspection_id:
            inspections[i] = updated_data
            data_file = get_inspection_data_file()
            try:
                with open(data_file, "w") as f:
                    json.dump(inspections, f, indent=2)
                return True
            except Exception:
                return False
    
    return False

def generate_inspection_id() -> str:
    """Generate a unique inspection ID."""
    return f"INSP_{datetime.now().strftime('%Y%m%d_%H%M%S')}" 