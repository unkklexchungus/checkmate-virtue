#!/usr/bin/env python3
"""
CheckMate Virtue - Application Entry Point
Run this file to start the application.
"""

import uvicorn
from app.main import app
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=not settings.IS_PRODUCTION,
        log_level=settings.LOG_LEVEL.lower(),
    ) 