"""
Simple session management for CheckMate Virtue.
"""

from fastapi import Request, HTTPException
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
import os
from dotenv import load_dotenv
from jose import JWTError, jwt

# Load environment variables from .env file
load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")

# User model
class User:
    def __init__(self, id: str, email: str, name: str, provider: str):
        self.id = id
        self.email = email
        self.name = name
        self.provider = provider

# Session management
def get_user_from_session(request: Request) -> User:
    """Get user from session or return a default user."""
    user_data = request.session.get("user")
    if user_data:
        return User(
            id=user_data.get("id"),
            email=user_data.get("email"),
            name=user_data.get("name"),
            provider=user_data.get("provider")
        )
    # Return a default user for demo purposes
    return User(
        id="demo-user",
        email="demo@checkmate.com",
        name="Demo User",
        provider="demo"
    )

def set_user_session(request: Request, user: User):
    request.session["user"] = {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "provider": user.provider
    }

def clear_user_session(request: Request):
    request.session.clear()

# Middleware setup
def setup_auth_middleware(app):
    app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
