#!/usr/bin/env python3
"""
Standalone regression test for Playwright goto method.
This test verifies that page.goto is callable and navigation works correctly.
"""

import os
import sys
from pathlib import Path

# Add the qa directory to the path
qa_dir = Path(__file__).parent
sys.path.insert(0, str(qa_dir))

from test_helpers import verify_page_goto_callable, safe_navigate, create_regression_test
from playwright.sync_api import sync_playwright, Page

def test_goto_callable():
    """Test that page.goto is callable."""
    print("Testing page.goto callability...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # Verify goto is callable
            verify_page_goto_callable(page)
            print("✅ page.goto is callable")
            
            # Test basic navigation
            base_url = os.getenv("APP_BASE_URL", "http://127.0.0.1:8000")
            if safe_navigate(page, base_url, timeout=10000):
                print(f"✅ Successfully navigated to {base_url}")
                print(f"   Page title: {page.title()}")
                print(f"   Current URL: {page.url}")
            else:
                print(f"❌ Failed to navigate to {base_url}")
                return False
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
        finally:
            browser.close()
    
    return True

def test_regression():
    """Run the full regression test."""
    print("Running full regression test...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            success = create_regression_test(page)
            return success
        finally:
            browser.close()

def main():
    """Main entry point."""
    print("=== Playwright Goto Regression Test ===")
    
    # Test 1: Verify goto is callable
    if not test_goto_callable():
        print("❌ Goto callability test failed")
        sys.exit(1)
    
    # Test 2: Full regression test
    if not test_regression():
        print("❌ Full regression test failed")
        sys.exit(1)
    
    print("✅ All regression tests passed!")
    sys.exit(0)

if __name__ == "__main__":
    main()
