from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict
import httpx
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
import os

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth configuration
config = Config('.env')
oauth = OAuth()

# Google OAuth
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID", "your-google-client-id"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET", "your-google-client-secret"),
    server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# GitHub OAuth
oauth.register(
    name='github',
    client_id=os.getenv("GITHUB_CLIENT_ID", "your-github-client-id"),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET", "your-github-client-secret"),
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

# User model
class User:
    def __init__(self, id: str, email: str, name: str, provider: str):
        self.id = id
        self.email = email
        self.name = name
        self.provider = provider

# Token functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None

# Security
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[User]:
    token = credentials.credentials
    email = verify_token(token)
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return User(id=email, email=email, name=email, provider="jwt")

# Session management
def get_user_from_session(request: Request) -> Optional[User]:
    user_data = request.session.get("user")
    if user_data:
        return User(
            id=user_data.get("id"),
            email=user_data.get("email"),
            name=user_data.get("name"),
            provider=user_data.get("provider")
        )
    return None

def set_user_session(request: Request, user: User):
    request.session["user"] = {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "provider": user.provider
    }

def clear_user_session(request: Request):
    request.session.clear()

# OAuth routes
async def google_login(request: Request):
    redirect_uri = request.url_for('auth_callback', provider='google')
    return await oauth.google.authorize_redirect(request, redirect_uri)

async def github_login(request: Request):
    redirect_uri = request.url_for('auth_callback', provider='github')
    return await oauth.github.authorize_redirect(request, redirect_uri)

async def auth_callback(request: Request, provider: str):
    if provider == 'google':
        token = await oauth.google.authorize_access_token(request)
        user_info = await oauth.google.parse_id_token(request, token)
        user = User(
            id=user_info['sub'],
            email=user_info['email'],
            name=user_info.get('name', user_info['email']),
            provider='google'
        )
    elif provider == 'github':
        token = await oauth.github.authorize_access_token(request)
        async with httpx.AsyncClient() as client:
            resp = await client.get('https://api.github.com/user', headers={'Authorization': f"token {token['access_token']}"})
            user_info = resp.json()
            user = User(
                id=str(user_info['id']),
                email=user_info.get('email', f"{user_info['login']}@github.com"),
                name=user_info.get('name', user_info['login']),
                provider='github'
            )
    else:
        raise HTTPException(status_code=400, detail="Invalid provider")
    
    set_user_session(request, user)
    return {"message": "Login successful", "user": user}

async def logout(request: Request):
    clear_user_session(request)
    return {"message": "Logout successful"}

# Middleware setup
def setup_auth_middleware(app):
    app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
    oauth.init_app(app) 