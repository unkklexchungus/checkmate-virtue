"""
Example test demonstrating enhanced artifact capture functionality.
This test shows how to use the new artifact capture system.
"""

import pytest
from playwright.sync_api import Page
from test_artifact_helpers import capture_failure_artifacts, log_artifacts_to_console


@pytest.mark.browser
@pytest.mark.playwright
def test_successful_navigation(page_with_artifacts: Page):
    """Test that succeeds - no artifacts captured."""
    page_with_artifacts.goto("https://example.com")
    assert page_with_artifacts.title() == "Example Domain"


@pytest.mark.browser
@pytest.mark.playwright
def test_failed_navigation(page_with_artifacts: Page):
    """Test that fails - artifacts automatically captured."""
    page_with_artifacts.goto("https://example.com")
    # This will fail and trigger artifact capture
    assert page_with_artifacts.title() == "Wrong Title"


@pytest.mark.browser
@pytest.mark.playwright
def test_manual_artifact_capture(page: Page):
    """Test demonstrating manual artifact capture."""
    try:
        page.goto("https://example.com")
        # Simulate some test logic that might fail
        element = page.locator("h1")
        if not element.is_visible():
            raise Exception("Expected element not visible")
        
        # This assertion will fail
        assert element.text_content() == "Wrong Text"
        
    except Exception as e:
        # Manually capture artifacts
        artifacts = capture_failure_artifacts(page, "test_manual_artifact_capture", "manual_error")
        log_artifacts_to_console(artifacts, "Manual capture: ")
        raise


@pytest.mark.browser
@pytest.mark.playwright
def test_step_by_step_capture(page: Page):
    """Test demonstrating step-by-step artifact capture."""
    # Step 1: Navigate
    page.goto("https://example.com")
    artifacts = capture_failure_artifacts(page, "test_step_by_step_capture", "step_navigation")
    print(f"Navigation step artifacts: {artifacts}")
    
    # Step 2: Check title
    title = page.title()
    if title != "Example Domain":
        artifacts = capture_failure_artifacts(page, "test_step_by_step_capture", "step_title_check")
        print(f"Title check artifacts: {artifacts}")
        raise AssertionError(f"Expected title 'Example Domain', got '{title}'")
    
    # Step 3: Check content
    heading = page.locator("h1")
    if not heading.is_visible():
        artifacts = capture_failure_artifacts(page, "test_step_by_step_capture", "step_content_check")
        print(f"Content check artifacts: {artifacts}")
        raise AssertionError("Expected heading not visible")


@pytest.mark.browser
@pytest.mark.playwright
def test_network_error_handling(page_with_artifacts: Page):
    """Test that triggers network error handling."""
    # This URL will likely fail and trigger network error artifacts
    page_with_artifacts.goto("https://httpstat.us/500")
    # The error handlers in run_browser_tests.py will capture artifacts automatically


@pytest.mark.browser
@pytest.mark.playwright
def test_js_error_handling(page_with_artifacts: Page):
    """Test that triggers JavaScript error handling."""
    # Navigate to a page that might have JS errors
    page_with_artifacts.goto("https://example.com")
    
    # Inject some JavaScript that will cause an error
    page_with_artifacts.evaluate("""
        setTimeout(() => {
            throw new Error('Test JavaScript error');
        }, 100);
    """)
    
    # Wait a bit for the error to be captured
    page_with_artifacts.wait_for_timeout(200)


if __name__ == "__main__":
    # Run this test file directly
    import sys
    import subprocess
    
    print("Running artifact capture example tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        __file__, 
        "-v", 
        "--tb=short"
    ])
    
    print(f"\nTest run completed with exit code: {result.returncode}")
    print("Check the artifacts directory for captured screenshots and HTML snapshots.")
