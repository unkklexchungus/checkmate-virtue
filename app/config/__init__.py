"""
Configuration package for the application.
"""

from .runtime import BASE_URL, build_url, log_startup_info, validate_base_url

__all__ = ['BASE_URL', 'build_url', 'log_startup_info', 'validate_base_url']
