"""
Production configuration settings.
"""

from app.config import Settings


class ProdSettings(Settings):
    """Production-specific settings."""
    
    # Override settings for production
    LOG_LEVEL: str = "INFO"
    ENABLE_API_DOCS: bool = False
    ENABLE_CACHING: bool = True
    ENABLE_HTTPS_REDIRECT: bool = True
    SECURE_HEADERS: bool = True
    RATE_LIMIT_ENABLED: bool = True
    ENABLE_REQUEST_LOGGING: bool = True
    
    # Production-specific paths
    UPLOAD_DIR: str = "/app/static/uploads"
    TEMPLATES_DIR: str = "/app/templates"
    DATA_DIR: str = "/app/data"
    PDF_TEMP_DIR: str = "/tmp"
    
    class Config:
        env_file = ".env.prod" 