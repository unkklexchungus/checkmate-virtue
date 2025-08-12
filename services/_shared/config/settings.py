"""
Shared configuration settings for all services.
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class DatabaseSettings(BaseSettings):
    """Database configuration."""
    host: str = Field(default="postgres", env="POSTGRES_HOST")
    port: int = Field(default=5432, env="POSTGRES_PORT")
    user: str = Field(default="appuser", env="POSTGRES_USER")
    password: str = Field(default="apppass", env="POSTGRES_PASSWORD")
    database: str = Field(default="appdb", env="POSTGRES_DB")
    schema: str = Field(default="public", env="DB_SCHEMA")
    
    @property
    def url(self) -> str:
        """Get database URL."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    @property
    def sync_url(self) -> str:
        """Get synchronous database URL."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"






class RedisSettings(BaseSettings):
    """Redis configuration."""
    url: str = Field(default="redis://redis:6379/0", env="REDIS_URL")
    host: str = Field(default="redis", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    db: int = Field(default=0, env="REDIS_DB")
    password: Optional[str] = Field(None, env="REDIS_PASSWORD")


class ServiceSettings(BaseSettings):
    """Service-specific configuration."""
    service_name: str = Field(..., env="SERVICE_NAME")
    service_version: str = Field(default="1.0.0", env="SERVICE_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # API Gateway settings
    gateway_url: str = Field(default="http://api-gateway:8000", env="GATEWAY_URL")
    
    # Service URLs (for inter-service communication)
    customer_service_url: str = Field(default="http://customer-service:8000", env="CUSTOMER_SERVICE_URL")
    vehicle_service_url: str = Field(default="http://vehicle-service:8000", env="VEHICLE_SERVICE_URL")
    appointment_service_url: str = Field(default="http://appointment-service:8000", env="APPOINTMENT_SERVICE_URL")
    workshop_service_url: str = Field(default="http://workshop-service:8000", env="WORKSHOP_SERVICE_URL")
    inventory_service_url: str = Field(default="http://inventory-service:8000", env="INVENTORY_SERVICE_URL")
    notification_service_url: str = Field(default="http://notification-service:8000", env="NOTIFICATION_SERVICE_URL")


class SecuritySettings(BaseSettings):
    """Security configuration."""
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    cors_credentials: bool = Field(default=True, env="CORS_CREDENTIALS")
    cors_methods: List[str] = Field(default=["*"], env="CORS_METHODS")
    cors_headers: List[str] = Field(default=["*"], env="CORS_HEADERS")
    
    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")


class Settings(BaseSettings):
    """Main settings class."""
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    service: ServiceSettings = ServiceSettings()
    security: SecuritySettings = SecuritySettings()
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
