"""
Configuration settings for CheckMate Virtue application.
"""

from pathlib import Path

# Application Settings
APP_NAME = "CheckMate Virtue"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Professional Vehicle Inspection System"

# Server Settings
HOST = "0.0.0.0"
PORT = 8000

# File Paths
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
TEMPLATES_DIR = BASE_DIR / "templates"
DATA_DIR = BASE_DIR / "data"
INSPECTIONS_FILE = DATA_DIR / "inspections.json"
TEMPLATE_FILE = BASE_DIR / "CheckMateVirtue" / "assets" / "basic_inspection.json"

# CORS Settings
CORS_ORIGINS = ["*"]
CORS_CREDENTIALS = True
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]

# File Upload Settings
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}

# Inspection Settings
DEFAULT_INSPECTION_STATUS = "draft"
INSPECTION_ID_PREFIX = "insp"

# Validation Settings
MIN_TITLE_LENGTH = 1
MAX_TITLE_LENGTH = 200
MIN_INSPECTOR_NAME_LENGTH = 1
MAX_INSPECTOR_NAME_LENGTH = 100 