import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import os

TEMPLATE_PATH = Path(__file__).parent / "templates.json"

def load_inspection_template() -> Dict[str, Any]:
    """Load the inspection template from JSON file."""
    try:
        with open(TEMPLATE_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"steps": []}
    except json.JSONDecodeError:
        return {"steps": []}

def save_inspection_template(template: Dict[str, Any]) -> bool:
    """Save the inspection template to JSON file."""
    try:
        with open(TEMPLATE_PATH, "w") as f:
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
    """Load all inspections from the data file."""
    data_file = get_inspection_data_file()
    try:
        with open(data_file, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

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