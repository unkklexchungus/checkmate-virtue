#!/usr/bin/env python3
"""
Simple test to verify that page.goto is callable and not shadowed.
This test doesn't require a server to be running.
"""

import sys
from pathlib import Path

# Add the qa directory to the path
qa_dir = Path(__file__).parent
sys.path.insert(0, str(qa_dir))

from test_helpers import verify_page_goto_callable
from playwright.sync_api import sync_playwright, Page


def test_goto_callable():
    """Test that page.goto is callable without requiring a server."""
    print("Testing page.goto callability...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # Verify goto is callable
            verify_page_goto_callable(page)
            print("✅ page.goto is callable")
            
            # Test that goto is a method, not a string
            if callable(page.goto):
                print("✅ page.goto is callable (verified)")
            else:
                print(f"❌ page.goto is not callable. Type: {type(page.goto)}")
                return False
            
            # Test that goto is not a string
            if isinstance(page.goto, str):
                print(f"❌ page.goto is a string: {page.goto}")
                return False
            else:
                print("✅ page.goto is not a string")
            
            # Test that we can call goto (it will fail with connection refused, but that's expected)
            try:
                page.goto("http://localhost:9999", timeout=1000)
            except Exception as e:
                if "ERR_CONNECTION_REFUSED" in str(e) or "timeout" in str(e).lower():
                    print("✅ page.goto method works (connection refused as expected)")
                else:
                    print(f"❌ Unexpected error calling page.goto: {e}")
                    return False
            
            return True
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
        finally:
            browser.close()


def main():
    """Main entry point."""
    print("=== Testing Goto Method Fix ===")
    
    if test_goto_callable():
        print("✅ All tests passed! Goto method is working correctly.")
        sys.exit(0)
    else:
        print("❌ Tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
