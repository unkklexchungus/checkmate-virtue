"""
File utility functions.
"""

import json
import os
import uuid
from pathlib import Path
from typing import Any, Dict

from fastapi import UploadFile

from app.config import settings


def load_json_file(file_path: Path, default: Any = None) -> Any:
    """Load JSON file and return data."""
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading JSON file {file_path}: {e}")
        return default


def save_json_file(file_path: Path, data: Any) -> None:
    """Save data to JSON file."""
    try:
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving JSON file {file_path}: {e}")


def save_uploaded_file(
    file: UploadFile, 
    inspection_id: str, 
    category: str, 
    item: str
) -> str:
    """Save uploaded file and return filename."""
    # Create safe filename
    file_ext = Path(file.filename).suffix.lower()
    safe_filename = f"{inspection_id}_{category}_{item}_{uuid.uuid4().hex[:8]}{file_ext}"
    
    # Create upload directory structure
    upload_dir = settings.UPLOAD_DIR / inspection_id / category
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = upload_dir / safe_filename
    with open(file_path, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)
    
    # Return relative path for storage in database
    return f"{inspection_id}/{category}/{safe_filename}"


def validate_file_extension(filename: str) -> bool:
    """Validate file extension."""
    if not filename:
        return False
    
    file_ext = Path(filename).suffix.lower()
    return file_ext in settings.ALLOWED_EXTENSIONS


def get_file_size(file_path: Path) -> int:
    """Get file size in bytes."""
    try:
        return file_path.stat().st_size
    except OSError:
        return 0


def ensure_directory_exists(directory: Path) -> None:
    """Ensure directory exists, create if it doesn't."""
    directory.mkdir(parents=True, exist_ok=True) 