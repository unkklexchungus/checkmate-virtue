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

# Ensure artifact directories exist
ARTIFACTS_DIR.mkdir(exist_ok=True)
SCREENSHOTS_DIR.mkdir(exist_ok=True)
HTML_DIR.mkdir(exist_ok=True)


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
        
        # Create test-specific directories
        test_dir = ARTIFACTS_DIR / self._sanitize_test_name(test_name)
        test_dir.mkdir(exist_ok=True)
        (test_dir / "screenshots").mkdir(exist_ok=True)
        (test_dir / "html").mkdir(exist_ok=True)
    
    def capture_artifacts(self, error_type: str = "failure") -> Dict[str, str]:
        """Capture both screenshot and HTML snapshot for the current test."""
        if not self.current_test_name or not self.current_page:
            return {}
        
        timestamp = int(time.time())
        test_dir = ARTIFACTS_DIR / self._sanitize_test_name(self.current_test_name)
        
        artifacts = {}
        
        # Capture screenshot
        try:
            screenshot_path = test_dir / "screenshots" / f"{error_type}_{timestamp}.png"
            self.current_page.screenshot(path=str(screenshot_path))
            artifacts["screenshot"] = str(screenshot_path.relative_to(QA_DIR))
        except Exception as e:
            print(f"Failed to capture screenshot: {e}")
            artifacts["screenshot"] = None
        
        # Capture HTML snapshot
        try:
            html_path = test_dir / "html" / f"{error_type}_{timestamp}.html"
            html_content = self.current_page.content()
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            artifacts["html_snapshot"] = str(html_path.relative_to(QA_DIR))
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
    
    # Capture artifacts on test completion (success or failure)
    if request.node.rep_call.failed:
        artifacts = artifact_capture.capture_artifacts("failure")
        print(f"\nTest failed. Artifacts captured:")
        for artifact_type, path in artifacts.items():
            if path:
                print(f"  {artifact_type}: {path}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture artifacts on test failures."""
    outcome = yield
    rep = outcome.get_result()
    
    # Only capture on failures
    if rep.when == "call" and rep.failed:
        test_name = f"{item.module.__name__}.{item.function.__name__}"
        
        # Capture artifacts if we have a page context
        if artifact_capture.current_page and artifact_capture.current_test_name == test_name:
            artifacts = artifact_capture.capture_artifacts("failure")
            
            # Attach artifact paths to the test report
            if artifacts.get("screenshot"):
                rep.sections.append(("Screenshot", artifacts["screenshot"]))
            if artifacts.get("html_snapshot"):
                rep.sections.append(("HTML Snapshot", artifacts["html_snapshot"]))
            
            # Add artifact summary to report
            artifact_summary = []
            for artifact_type, path in artifacts.items():
                if path:
                    artifact_summary.append(f"{artifact_type}: {path}")
            
            if artifact_summary:
                rep.sections.append(("Artifacts", "\n".join(artifact_summary)))


def pytest_configure(config):
    """Configure pytest with custom markers and options."""
    config.addinivalue_line(
        "markers", "playwright: mark test as requiring Playwright browser"
    )
    config.addinivalue_line(
        "markers", "browser: mark test as browser-based test"
    )


def pytest_collection_modifyitems(config, items):
    """Add browser marker to tests that use page_with_artifacts fixture."""
    for item in items:
        if "page_with_artifacts" in item.fixturenames:
            item.add_marker(pytest.mark.browser)
            item.add_marker(pytest.mark.playwright)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Print artifact summary at the end of test run."""
    if artifact_capture.test_artifacts:
        terminalreporter.write_sep("=", "Test Artifacts Summary")
        for test_name, artifacts in artifact_capture.test_artifacts.items():
            terminalreporter.write_line(f"\n{test_name}:")
            for artifact_type, path in artifacts.items():
                if path:
                    terminalreporter.write_line(f"  {artifact_type}: {path}")
        
        terminalreporter.write_line(f"\nArtifacts directory: {ARTIFACTS_DIR}")
        terminalreporter.write_line("View artifacts in CI by downloading the artifacts directory.")
