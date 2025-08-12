"""
Configuration settings for CheckMate Virtue application.
"""

import os
from pathlib import Path

# Application Settings
APP_NAME = "CheckMate Virtue"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Professional Automotive Inspection System"

# Import the new runtime configuration
from app.config.runtime import BASE_URL, build_url, log_startup_info, validate_base_url

# Base URL Configuration - Single source of truth for all environments
# Now handled by app.config.runtime
APP_BASE_URL = BASE_URL

# Server Settings - Railway compatible
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", 8000))

# File Paths
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
TEMPLATES_DIR = BASE_DIR / "templates"
DATA_DIR = BASE_DIR / "data"
INSPECTIONS_FILE = DATA_DIR / "inspections.json"
TEMPLATE_FILE = BASE_DIR / "basic_inspection.json"

# Create necessary directories
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# CORS Settings - Environment-driven with proper defaults
CORS_ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",")
CORS_ORIGINS = [origin.strip() for origin in CORS_ALLOW_ORIGINS if origin.strip()]
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

# Railway specific settings
IS_PRODUCTION = os.getenv("RAILWAY_ENVIRONMENT") == "production"
RAILWAY_PROJECT_ID = os.getenv("RAILWAY_PROJECT_ID")
RAILWAY_SERVICE_ID = os.getenv("RAILWAY_SERVICE_ID")

# Performance settings
ENABLE_CACHING = IS_PRODUCTION
CACHE_TTL = 300  # 5 minutes

# Security settings
ENABLE_HTTPS_REDIRECT = IS_PRODUCTION
SECURE_HEADERS = IS_PRODUCTION

# Logging settings
LOG_LEVEL = "INFO" if IS_PRODUCTION else "DEBUG"
ENABLE_REQUEST_LOGGING = IS_PRODUCTION

# Database settings (for future expansion)
DATABASE_URL = os.getenv("DATABASE_URL")
USE_DATABASE = DATABASE_URL is not None

# File storage settings (for future expansion)
STORAGE_TYPE = os.getenv("STORAGE_TYPE", "local")  # local, s3, cloudinary
CLOUD_STORAGE_URL = os.getenv("CLOUD_STORAGE_URL")

# Email settings (for future expansion)
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
ENABLE_EMAIL_NOTIFICATIONS = all([SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD])

# API settings
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"
ENABLE_API_DOCS = not IS_PRODUCTION  # Disable docs in production

# PDF Generation settings
PDF_TEMP_DIR = Path("/tmp") if IS_PRODUCTION else BASE_DIR / "temp"
PDF_TEMP_DIR.mkdir(exist_ok=True)

# Session settings
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "your-secret-key-change-in-production")
SESSION_COOKIE_SECURE = IS_PRODUCTION
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# Rate limiting settings
RATE_LIMIT_ENABLED = IS_PRODUCTION
RATE_LIMIT_REQUESTS = 100  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

# Monitoring settings
ENABLE_HEALTH_CHECK = True
HEALTH_CHECK_ENDPOINT = "/healthz"
ENABLE_METRICS = IS_PRODUCTION
METRICS_ENDPOINT = "/metrics"

# Development settings
DEBUG = not IS_PRODUCTION
RELOAD = not IS_PRODUCTION 