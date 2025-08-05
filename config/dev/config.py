"""
Development configuration settings.
"""

from app.config import Settings


class DevSettings(Settings):
    """Development-specific settings."""
    
    # Override settings for development
    LOG_LEVEL: str = "DEBUG"
    ENABLE_API_DOCS: bool = True
    ENABLE_CACHING: bool = False
    ENABLE_HTTPS_REDIRECT: bool = False
    SECURE_HEADERS: bool = False
    RATE_LIMIT_ENABLED: bool = False
    ENABLE_REQUEST_LOGGING: bool = True
    
    # Development-specific paths
    UPLOAD_DIR: str = "app/static/uploads"
    TEMPLATES_DIR: str = "app/templates"
    DATA_DIR: str = "data"
    PDF_TEMP_DIR: str = "temp"
    
    class Config:
        env_file = ".env.dev" 