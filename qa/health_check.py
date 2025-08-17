#!/usr/bin/env python3
"""
Health Check Utility for CheckMate Virtue
Polls the /healthz endpoint with exponential backoff to ensure the service is ready.
"""

import os
import time
import httpx
from typing import Optional
from urllib.parse import urljoin

def get_base_url() -> str:
    """Get the base URL from environment or use default."""
    # Try to import from app.config.runtime first, fallback to environment variable
    try:
        from app.config.runtime import BASE_URL
        return BASE_URL
    except ImportError:
        # Fallback to environment variable
        return os.getenv('APP_BASE_URL', 'http://localhost:8000')

def wait_for_health(
    base_url: Optional[str] = None,
    timeout: int = 60,
    initial_delay: float = 1.0,
    max_delay: float = 10.0,
    backoff_factor: float = 2.0
) -> bool:
    """
    Wait for the service to become healthy by polling the /healthz endpoint.
    
    Args:
        base_url: Base URL of the service (defaults to APP_BASE_URL env var)
        timeout: Maximum time to wait in seconds
        initial_delay: Initial delay between attempts in seconds
        max_delay: Maximum delay between attempts in seconds
        backoff_factor: Factor to multiply delay by on each failure
        
    Returns:
        True if service becomes healthy within timeout, False otherwise
        
    Raises:
        httpx.RequestError: If there are network issues
    """
    if base_url is None:
        base_url = get_base_url()
    
    health_url = urljoin(base_url, "/healthz")
    start_time = time.time()
    delay = initial_delay
    
    print(f"Waiting for service to become healthy at {health_url}")
    
    while time.time() - start_time < timeout:
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(health_url)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "ok":
                        print(f"Service is healthy! Response: {data}")
                        return True
                    else:
                        print(f"Service responded but status is not 'ok': {data}")
                else:
                    print(f"Service responded with status code: {response.status_code}")
                    
        except httpx.RequestError as e:
            print(f"Connection failed: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        
        # Wait before next attempt
        time.sleep(delay)
        
        # Exponential backoff
        delay = min(delay * backoff_factor, max_delay)
    
    print(f"Service did not become healthy within {timeout} seconds")
    return False

def check_health(base_url: Optional[str] = None) -> bool:
    """
    Simple health check without waiting.
    
    Args:
        base_url: Base URL of the service (defaults to APP_BASE_URL env var)
        
    Returns:
        True if service is healthy, False otherwise
    """
    if base_url is None:
        base_url = get_base_url()
    
    health_url = urljoin(base_url, "/healthz")
    
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(health_url)
            if response.status_code == 200:
                data = response.json()
                return data.get("status") == "ok"
    except Exception:
        pass
    
    return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = None
    
    success = wait_for_health(base_url)
    sys.exit(0 if success else 1)
