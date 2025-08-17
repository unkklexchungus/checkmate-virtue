"""
Pytest configuration and plugins for Playwright browser tests.
Provides enhanced failure artifact capture for debugging.
"""

import os
import pytest
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from playwright.sync_api import Page, Browser, BrowserContext

# Test artifact directories
QA_DIR = Path(__file__).parent
ARTIFACTS_DIR = QA_DIR / "artifacts"
SCREENSHOTS_DIR = ARTIFACTS_DIR / "screenshots"
HTML_DIR = ARTIFACTS_DIR / "html"

# Import enhanced permission handling
try:
    from test_artifact_helpers import ensure_writable_directory
except ImportError:
    # Fallback function if import fails
    def ensure_writable_directory(directory: Path) -> Path:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            return directory
        except Exception:
            return Path.cwd() / "test_artifacts"

# Ensure artifact directories exist with permission handling
ARTIFACTS_DIR = ensure_writable_directory(ARTIFACTS_DIR)
SCREENSHOTS_DIR = ensure_writable_directory(SCREENSHOTS_DIR)
HTML_DIR = ensure_writable_directory(HTML_DIR)


class PlaywrightArtifactCapture:
    """Captures screenshots and HTML snapshots on test failures."""
    
    def __init__(self):
        self.current_test_name: Optional[str] = None
        self.current_page: Optional[Page] = None
        self.test_artifacts: Dict[str, Dict[str, str]] = {}
    
    def set_test_context(self, test_name: str, page: Page):
        """Set the current test context for artifact capture."""
        self.current_test_name = test_name
        self.current_page = page
        
        # Create test-specific directories with permission handling
        test_dir = ARTIFACTS_DIR / self._sanitize_test_name(test_name)
        test_dir = ensure_writable_directory(test_dir)
        
        # Create subdirectories
        ensure_writable_directory(test_dir / "screenshots")
        ensure_writable_directory(test_dir / "html")
    
    def capture_artifacts(self, error_type: str = "failure") -> Dict[str, str]:
        """Capture both screenshot and HTML snapshot for the current test."""
        if not self.current_test_name or not self.current_page:
            return {}
        
        timestamp = int(time.time())
        test_dir = ARTIFACTS_DIR / self._sanitize_test_name(self.current_test_name)
        
        artifacts = {}
        
        # Capture screenshot with enhanced error handling
        try:
            screenshots_dir = ensure_writable_directory(test_dir / "screenshots")
            screenshot_path = screenshots_dir / f"{error_type}_{timestamp}.png"
            self.current_page.screenshot(path=str(screenshot_path))
            artifacts["screenshot"] = str(screenshot_path.relative_to(QA_DIR))
            print(f"✓ Screenshot captured: {artifacts['screenshot']}")
        except Exception as e:
            print(f"Failed to capture screenshot: {e}")
            artifacts["screenshot"] = None
        
        # Capture HTML snapshot with enhanced error handling
        try:
            html_dir = ensure_writable_directory(test_dir / "html")
            html_path = html_dir / f"{error_type}_{timestamp}.html"
            html_content = self.current_page.content()
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            artifacts["html_snapshot"] = str(html_path.relative_to(QA_DIR))
            print(f"✓ HTML snapshot captured: {artifacts['html_snapshot']}")
        except Exception as e:
            print(f"Failed to capture HTML snapshot: {e}")
            artifacts["html_snapshot"] = None
        
        # Store artifacts for this test
        if self.current_test_name not in self.test_artifacts:
            self.test_artifacts[self.current_test_name] = {}
        self.test_artifacts[self.current_test_name].update(artifacts)
        
        return artifacts
    
    def _sanitize_test_name(self, test_name: str) -> str:
        """Sanitize test name for use as directory name."""
        return test_name.replace('/', '_').replace('\\', '_').replace(':', '_')
    
    def get_test_artifacts(self, test_name: str) -> Dict[str, str]:
        """Get all artifacts for a specific test."""
        return self.test_artifacts.get(test_name, {})


# Global artifact capture instance
artifact_capture = PlaywrightArtifactCapture()


@pytest.fixture(scope="function")
def page_with_artifacts(page: Page, request):
    """Enhanced page fixture that captures artifacts on failures."""
    # Set up test context
    test_name = f"{request.module.__name__}.{request.function.__name__}"
    artifact_capture.set_test_context(test_name, page)
    
    yield page
    
    # Clean up test context
    artifact_capture.current_test_name = None
    artifact_capture.current_page = None


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture artifacts on test failures."""
    outcome = yield
    report = outcome.get_result()
    
    # Only capture artifacts on failures
    if report.when == "call" and report.failed:
        # Get the page object if available
        page = None
        for fixture_name in item.fixturenames:
            if fixture_name == "page_with_artifacts":
                page = item.funcargs.get(fixture_name)
                break
        
        if page:
            # Capture artifacts
            artifacts = artifact_capture.capture_artifacts("failure")
            
            # Add artifact paths to the report
            if artifacts.get("screenshot"):
                report.sections.append(("Screenshot", artifacts["screenshot"]))
            if artifacts.get("html_snapshot"):
                report.sections.append(("HTML Snapshot", artifacts["html_snapshot"]))
            
            # Log artifacts to console
            test_name = f"{item.module.__name__}.{item.function.__name__}"
            print(f"\n📋 Test failed: {test_name}")
            if artifacts.get("screenshot"):
                print(f"📸 Screenshot: {artifacts['screenshot']}")
            if artifacts.get("html_snapshot"):
                print(f"🌐 HTML Snapshot: {artifacts['html_snapshot']}")


@pytest.fixture(scope="session", autouse=True)
def setup_artifacts_environment():
    """Set up the artifacts environment at the start of the test session."""
    print(f"\n🔧 Setting up test artifacts environment...")
    print(f"📁 Artifacts directory: {ARTIFACTS_DIR}")
    print(f"📁 Screenshots directory: {SCREENSHOTS_DIR}")
    print(f"📁 HTML directory: {HTML_DIR}")
    
    # Clean up old artifacts (older than 24 hours)
    try:
        from test_artifact_helpers import cleanup_old_artifacts
        cleanup_old_artifacts(max_age_hours=24)
    except ImportError:
        print("Warning: Could not import cleanup function")
    
    yield
    
    print(f"\n✅ Test session completed. Artifacts available in: {ARTIFACTS_DIR}")


# Additional fixtures for backward compatibility
@pytest.fixture
def artifacts_dir():
    """Provide access to the artifacts directory."""
    return ARTIFACTS_DIR


@pytest.fixture
def screenshots_dir():
    """Provide access to the screenshots directory."""
    return SCREENSHOTS_DIR


@pytest.fixture
def html_dir():
    """Provide access to the HTML directory."""
    return HTML_DIR
