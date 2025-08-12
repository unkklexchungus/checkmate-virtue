#!/usr/bin/env python3
"""
Test helpers for Playwright browser tests.
Provides utilities to prevent and detect goto method shadowing.
"""

import os
from typing import Optional
from playwright.sync_api import Page


def verify_page_goto_callable(page: Page) -> bool:
    """
    Verify that page.goto is callable and not shadowed by a string.
    
    Args:
        page: Playwright Page object
        
    Returns:
        True if page.goto is callable, False otherwise
        
    Raises:
        AssertionError: If page.goto is not callable
    """
    if not hasattr(page, 'goto'):
        raise AssertionError("Page object does not have 'goto' attribute")
    
    if not callable(page.goto):
        raise AssertionError(f"Page.goto is not callable. Type: {type(page.goto)}")
    
    return True


def safe_navigate(page: Page, url: str, timeout: Optional[int] = None) -> bool:
    """
    Safely navigate to a URL with goto shadowing protection.
    
    Args:
        page: Playwright Page object
        url: URL to navigate to
        timeout: Navigation timeout in milliseconds
        
    Returns:
        True if navigation successful, False otherwise
    """
    # Verify goto is callable before attempting navigation
    verify_page_goto_callable(page)
    
    try:
        if timeout:
            page.goto(url, timeout=timeout)
        else:
            page.goto(url)
        return True
    except Exception as e:
        print(f"Navigation failed to {url}: {e}")
        return False


def get_base_url() -> str:
    """Get the base URL from environment variables."""
    from app.config.runtime import BASE_URL
    return BASE_URL


def create_regression_test(page: Page) -> bool:
    """
    Create a simple regression test that verifies basic page functionality.
    
    Args:
        page: Playwright Page object
        
    Returns:
        True if test passes, False otherwise
    """
    base_url = get_base_url()
    
    try:
        # Verify goto is callable
        verify_page_goto_callable(page)
        
        # Navigate to base URL
        if not safe_navigate(page, base_url):
            return False
        
        # Wait for page to load
        page.wait_for_load_state("networkidle", timeout=10000)
        
        # Verify page title exists (basic sanity check)
        title = page.title()
        if not title:
            print("Warning: Page has no title")
        
        # Look for a stable selector (body tag should always exist)
        body = page.locator('body')
        if body.count() == 0:
            print("Error: Body element not found")
            return False
        
        print(f"✅ Regression test passed: {base_url} loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Regression test failed: {e}")
        return False
