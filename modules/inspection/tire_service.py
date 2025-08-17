import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import logging

from .tire_models import TireInspection, TireInspectionCreate, TirePos, Light

# Setup logging
logger = logging.getLogger(__name__)

# Data storage path
DATA_DIR = Path("data")
TIRE_DATA_FILE = DATA_DIR / "tire_inspections.json"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

def _load_tire_data() -> Dict[str, Any]:
    """Load tire inspection data from JSON file."""
    try:
        if TIRE_DATA_FILE.exists():
            with open(TIRE_DATA_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading tire data: {e}")
        return {}

def _save_tire_data(data: Dict[str, Any]) -> bool:
    """Save tire inspection data to JSON file."""
    try:
        with open(TIRE_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        logger.error(f"Error saving tire data: {e}")
        return False

def get_tire_inspection(inspection_id: str) -> Optional[TireInspection]:
    """Get tire inspection by inspection ID."""
    try:
        data = _load_tire_data()
        tire_data = data.get(inspection_id)
        
        if tire_data:
            # Convert string keys back to TirePos enum
            readings = {}
            for pos_str, reading_data in tire_data.get('readings', {}).items():
                try:
                    if pos_str in [pos.value for pos in TirePos]:
                        readings[TirePos(pos_str)] = reading_data
                except (ValueError, AttributeError):
                    # Skip invalid tire positions
                    continue
            
            tire_data['readings'] = readings
            return TireInspection(**tire_data)
        
        return None
    except Exception as e:
        logger.error(f"Error getting tire inspection for {inspection_id}: {e}")
        return None

def create_or_update_tire_inspection(inspection_id: str, tire_data: TireInspectionCreate) -> Optional[TireInspection]:
    """Create or update tire inspection."""
    try:
        data = _load_tire_data()
        
        # Check if tire inspection already exists
        existing = data.get(inspection_id)
        
        if existing:
            # Update existing
            existing.update(tire_data.model_dump())
            existing['updated_at'] = datetime.now(timezone.utc).isoformat()
            tire_inspection = TireInspection(**existing)
        else:
            # Create new
            tire_inspection = TireInspection(
                inspection_id=inspection_id,
                **tire_data.model_dump()
            )
        
        # Convert TirePos enum keys to strings for JSON serialization
        readings_dict = {}
        for pos, reading in tire_inspection.readings.items():
            try:
                readings_dict[pos.value] = reading.model_dump()
            except (AttributeError, ValueError):
                # Skip invalid tire positions
                continue
        
        # Prepare data for storage
        storage_data = tire_inspection.model_dump()
        storage_data['readings'] = readings_dict
        
        data[inspection_id] = storage_data
        
        if _save_tire_data(data):
            return tire_inspection
        else:
            logger.error(f"Failed to save tire inspection for {inspection_id}")
            return None
            
    except Exception as e:
        logger.error(f"Error creating/updating tire inspection for {inspection_id}: {e}")
        return None

def delete_tire_inspection(inspection_id: str) -> bool:
    """Delete tire inspection by inspection ID."""
    try:
        data = _load_tire_data()
        
        if inspection_id in data:
            del data[inspection_id]
            return _save_tire_data(data)
        
        return True  # Already doesn't exist
    except Exception as e:
        logger.error(f"Error deleting tire inspection for {inspection_id}: {e}")
        return False

def get_tire_inspection_status(inspection_id: str) -> Optional[Light]:
    """Get the overall status of a tire inspection."""
    try:
        tire_inspection = get_tire_inspection(inspection_id)
        if tire_inspection:
            return tire_inspection.get_section_status()
        return None
    except Exception as e:
        logger.error(f"Error getting tire inspection status for {inspection_id}: {e}")
        return None

def validate_tire_reading(reading_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate tire reading data and return any validation errors."""
    errors = {}
    
    try:
        # Validate PSI values
        psi_in = reading_data.get('psi_in')
        psi_out = reading_data.get('psi_out')
        
        if psi_in is not None and (psi_in < 0 or psi_in > 80):
            errors['psi_in'] = 'PSI must be between 0 and 80'
        
        if psi_out is not None and (psi_out < 0 or psi_out > 80):
            errors['psi_out'] = 'PSI must be between 0 and 80'
        
        # Validate tread
        tread = reading_data.get('tread_32nds')
        if tread is not None and (tread < 0 or tread > 20):
            errors['tread_32nds'] = 'Tread must be between 0 and 20 32nds'
        
        # Validate status
        status = reading_data.get('status')
        if status and status not in [light.value for light in Light]:
            errors['status'] = f'Status must be one of: {", ".join([light.value for light in Light])}'
        
        # Check PSI logic
        if psi_in is not None and psi_out is not None and psi_out < psi_in:
            errors['psi_logic'] = 'PSI Out should not be less than PSI In'
        
    except Exception as e:
        errors['validation'] = f'Validation error: {str(e)}'
    
    return errors
