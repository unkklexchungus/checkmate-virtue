"""
Runtime configuration for robust base-URL handling across environments.
"""

import os
import socket
import logging
from urllib.parse import urljoin, urlparse
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)

# Base URL Configuration - Single source of truth for all environments
BASE_URL = os.getenv("APP_BASE_URL", "http://127.0.0.1:8000")

def build_url(path: str) -> str:
    """
    Safely join BASE_URL and path, handling edge cases.
    
    Args:
        path: The path to append to the base URL
        
    Returns:
        The complete URL
        
    Examples:
        >>> build_url("/api/health")
        'http://127.0.0.1:8000/api/health'
        >>> build_url("api/health")  # No leading slash
        'http://127.0.0.1:8000/api/health'
        >>> build_url("")  # Empty path
        'http://127.0.0.1:8000'
    """
    if not path:
        return BASE_URL.rstrip('/')
    
    # Ensure path starts with / for proper URL joining
    if not path.startswith('/'):
        path = '/' + path
    
    return urljoin(BASE_URL, path)

def is_ipv6_url(url: str) -> bool:
    """
    Check if a URL uses IPv6 addressing.
    
    Args:
        url: The URL to check
        
    Returns:
        True if the URL contains IPv6 addressing
    """
    try:
        parsed = urlparse(url)
        # For IPv6 addresses, urlparse may not extract hostname correctly
        # Check the netloc directly for IPv6 patterns
        netloc = parsed.netloc
        
        # Check for IPv6 patterns in netloc
        if '::' in netloc:
            return True
        
        # Check for bracketed IPv6 addresses
        if netloc.startswith('[') and ']' in netloc:
            return True
        
        # Check for specific IPv6 localhost
        if netloc.startswith('::1:'):
            return True
            
        return False
    except Exception:
        return False

def log_startup_info():
    """
    Log startup information about BASE_URL and IPv6 detection.
    """
    logger.info(f"🚀 Application starting with BASE_URL: {BASE_URL}")
    
    # Check for IPv6 usage
    if is_ipv6_url(BASE_URL):
        logger.warning(
            "⚠️  IPv6 detected in BASE_URL. This may cause connection issues in some environments. "
            "Consider using IPv4 (127.0.0.1) or container service names for Docker environments."
        )
    
    # Log network information
    try:
        # Get local IP addresses
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        logger.info(f"🌐 Hostname: {hostname}, Local IP: {local_ip}")
    except Exception as e:
        logger.warning(f"⚠️  Could not determine local network info: {e}")
    
    # Log environment context
    env_context = []
    if os.getenv("DOCKER_ENV"):
        env_context.append("Docker")
    if os.getenv("CI"):
        env_context.append("CI")
    if os.getenv("RAILWAY_ENVIRONMENT"):
        env_context.append("Railway")
    
    if env_context:
        logger.info(f"🏗️  Environment context: {' + '.join(env_context)}")
    else:
        logger.info("🏗️  Environment context: Local development")

def validate_base_url() -> bool:
    """
    Validate that BASE_URL is properly formatted.
    
    Returns:
        True if BASE_URL is valid, False otherwise
    """
    try:
        parsed = urlparse(BASE_URL)
        if not parsed.scheme or not parsed.netloc:
            logger.error(f"❌ Invalid BASE_URL format: {BASE_URL}")
            return False
        
        # Check for common issues
        if parsed.scheme not in ['http', 'https']:
            logger.error(f"❌ Unsupported scheme in BASE_URL: {parsed.scheme}")
            return False
        
        logger.info(f"✅ BASE_URL validation passed: {BASE_URL}")
        return True
        
    except Exception as e:
        logger.error(f"❌ BASE_URL validation failed: {e}")
        return False

# Initialize logging and validation on module import
if __name__ != "__main__":
    log_startup_info()
    validate_base_url()
