"""
Configuration settings for CheckMate Virtue application.
"""

import os
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings using Pydantic BaseSettings."""
    
    # Application Settings
    APP_NAME: str = "CheckMate Virtue"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Professional Multi-Industry Inspection System"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = Field(default=8000, env="PORT")
    
    # File Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    UPLOAD_DIR: Path = Field(default_factory=lambda: Path("app/static/uploads"))
    TEMPLATES_DIR: Path = Field(default_factory=lambda: Path("app/templates"))
    DATA_DIR: Path = Field(default_factory=lambda: Path("data"))
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
    
    # Inspection Settings
    DEFAULT_INSPECTION_STATUS: str = "draft"
    INSPECTION_ID_PREFIX: str = "insp"
    
    # Validation Settings
    MIN_TITLE_LENGTH: int = 1
    MAX_TITLE_LENGTH: int = 200
    MIN_INSPECTOR_NAME_LENGTH: int = 1
    MAX_INSPECTOR_NAME_LENGTH: int = 100
    
    # Environment Settings
    IS_PRODUCTION: bool = Field(default=False, env="RAILWAY_ENVIRONMENT")
    RAILWAY_PROJECT_ID: str = Field(default="", env="RAILWAY_PROJECT_ID")
    RAILWAY_SERVICE_ID: str = Field(default="", env="RAILWAY_SERVICE_ID")
    
    # Performance Settings
    ENABLE_CACHING: bool = Field(default=False)
    CACHE_TTL: int = 300  # 5 minutes
    
    # Security Settings
    ENABLE_HTTPS_REDIRECT: bool = Field(default=False)
    SECURE_HEADERS: bool = Field(default=False)
    
    # Logging Settings
    LOG_LEVEL: str = Field(default="INFO" if os.getenv("RAILWAY_ENVIRONMENT") == "production" else "DEBUG")
    ENABLE_REQUEST_LOGGING: bool = Field(default=False)
    
    # Database Settings
    DATABASE_URL: str = Field(default="", env="DATABASE_URL")
    USE_DATABASE: bool = Field(default=False)
    
    # File Storage Settings
    STORAGE_TYPE: str = Field(default="local", env="STORAGE_TYPE")
    CLOUD_STORAGE_URL: str = Field(default="", env="CLOUD_STORAGE_URL")
    
    # Email Settings
    SMTP_HOST: str = Field(default="", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: str = Field(default="", env="SMTP_USERNAME")
    SMTP_PASSWORD: str = Field(default="", env="SMTP_PASSWORD")
    ENABLE_EMAIL_NOTIFICATIONS: bool = Field(default=False)
    
    # API Settings
    API_VERSION: str = "v1"
    API_PREFIX: str = "/api/v1"
    ENABLE_API_DOCS: bool = Field(default=True)
    
    # PDF Generation Settings
    PDF_TEMP_DIR: Path = Field(default_factory=lambda: Path("/tmp") if os.getenv("RAILWAY_ENVIRONMENT") == "production" else Path("temp"))
    
    # Session Settings
    SESSION_SECRET_KEY: str = Field(default="your-secret-key-change-in-production", env="SESSION_SECRET_KEY")
    SESSION_COOKIE_SECURE: bool = Field(default=False)
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
    
    # Rate Limiting Settings
    RATE_LIMIT_ENABLED: bool = Field(default=False)
    
    # Legacy OAuth Settings (for backward compatibility)
    GOOGLE_CLIENT_ID: str = Field(default="", env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = Field(default="", env="GOOGLE_CLIENT_SECRET")
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields from environment
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create necessary directories
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.TEMPLATES_DIR.mkdir(exist_ok=True)
        self.DATA_DIR.mkdir(exist_ok=True)
        self.PDF_TEMP_DIR.mkdir(exist_ok=True)
        
        # Update derived settings
        self.IS_PRODUCTION = os.getenv("RAILWAY_ENVIRONMENT") == "production"
        self.ENABLE_CACHING = self.IS_PRODUCTION
        self.ENABLE_HTTPS_REDIRECT = self.IS_PRODUCTION
        self.SECURE_HEADERS = self.IS_PRODUCTION
        self.ENABLE_API_DOCS = not self.IS_PRODUCTION
        self.SESSION_COOKIE_SECURE = self.IS_PRODUCTION
        self.RATE_LIMIT_ENABLED = self.IS_PRODUCTION
        self.ENABLE_REQUEST_LOGGING = self.IS_PRODUCTION
        self.USE_DATABASE = bool(self.DATABASE_URL)
        self.ENABLE_EMAIL_NOTIFICATIONS = all([self.SMTP_HOST, self.SMTP_USERNAME, self.SMTP_PASSWORD])


# Create settings instance
settings = Settings() 