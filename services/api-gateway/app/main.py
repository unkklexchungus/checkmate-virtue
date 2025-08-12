"""
Workshop service main application.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from _shared.config.settings import settings
from _shared.utils.database import api_gateway_db

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.service.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting workshop service...")
    
    # Create database schema
    try:
        await api_gateway_db.create_schema()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down workshop service...")
    await api_gateway_db.close()


# Create FastAPI app
app = FastAPI(
    title="api-gateway",
    description="Workshop management service",
    version=settings.service.service_version,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.security.cors_origins,
    allow_credentials=settings.security.cors_credentials,
    allow_methods=settings.security.cors_methods,
    allow_headers=settings.security.cors_headers,
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": settings.service.service_version
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    try:
        # Test database connection
        async with api_gateway_db.async_session_maker() as session:
            await session.exec("SELECT 1")
        
        return {
            "status": "ready",
            "service": "api-gateway",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "not ready",
                "service": "api-gateway",
                "error": str(e)
            }
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.service.debug else "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.service.debug,
        log_level=settings.service.log_level.lower()
    )
