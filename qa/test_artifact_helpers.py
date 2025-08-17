"""
Enhanced test helpers for artifact capture in browser tests.
Provides utilities for capturing screenshots and HTML snapshots on failures.
"""

import os
import time
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

# Optional Playwright import
try:
    from playwright.sync_api import Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    # Create a dummy Page type for type hints
    Page = Any

# Import artifact capture from conftest
try:
    from conftest import artifact_capture, ARTIFACTS_DIR, HTML_DIR
except ImportError:
    # Fallback if conftest is not available
    ARTIFACTS_DIR = Path(__file__).parent / "artifacts"
    HTML_DIR = ARTIFACTS_DIR / "html"
    artifact_capture = None


def ensure_writable_directory(directory: Path) -> Path:
    """
    Ensure a directory exists and is writable, with fallback to temp directory.
    
    Args:
        directory: Directory path to check/create
        
    Returns:
        Writable directory path (original or fallback)
    """
    try:
        # Try to create the directory if it doesn't exist
        directory.mkdir(parents=True, exist_ok=True)
        
        # Test if directory is writable by creating a test file
        test_file = directory / f".test_write_{int(time.time())}"
        test_file.write_text("test")
        test_file.unlink()  # Clean up test file
        
        return directory
    except (PermissionError, OSError) as e:
        print(f"Warning: Cannot write to {directory}: {e}")
        
        # Fallback to temp directory
        fallback_dir = Path(tempfile.gettempdir()) / "test_artifacts"
        try:
            fallback_dir.mkdir(exist_ok=True)
            print(f"Using fallback directory: {fallback_dir}")
            return fallback_dir
        except Exception as fallback_error:
            print(f"Warning: Cannot create fallback directory: {fallback_error}")
            # Last resort: use current directory
            return Path.cwd() / "test_artifacts"


def capture_failure_artifacts(page: Page, test_name: str, error_type: str = "failure") -> Dict[str, str]:
    """
    Capture both screenshot and HTML snapshot for a test failure.
    
    Args:
        page: Playwright page object
        test_name: Name of the test for artifact organization
        error_type: Type of error/failure for artifact naming
        
    Returns:
        Dictionary with paths to captured artifacts
    """
    timestamp = int(time.time())
    artifacts = {}
    
    # Ensure we have a writable artifacts directory
    base_artifacts_dir = ensure_writable_directory(ARTIFACTS_DIR)
    
    # Create test-specific directory
    test_dir = base_artifacts_dir / _sanitize_test_name(test_name)
    test_dir = ensure_writable_directory(test_dir)
    
    # Create subdirectories
    screenshots_dir = ensure_writable_directory(test_dir / "screenshots")
    html_dir = ensure_writable_directory(test_dir / "html")
    
    # Capture screenshot
    try:
        screenshot_path = screenshots_dir / f"{error_type}_{timestamp}.png"
        page.screenshot(path=str(screenshot_path))
        artifacts["screenshot"] = str(screenshot_path.relative_to(base_artifacts_dir))
        print(f"✓ Screenshot captured: {artifacts['screenshot']}")
    except Exception as e:
        print(f"Failed to capture screenshot: {e}")
        artifacts["screenshot"] = None
    
    # Capture HTML snapshot
    try:
        html_path = html_dir / f"{error_type}_{timestamp}.html"
        html_content = page.content()
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        artifacts["html_snapshot"] = str(html_path.relative_to(base_artifacts_dir))
        print(f"✓ HTML snapshot captured: {artifacts['html_snapshot']}")
    except Exception as e:
        print(f"Failed to capture HTML snapshot: {e}")
        artifacts["html_snapshot"] = None
    
    return artifacts


def capture_step_artifacts(page: Page, test_name: str, step_name: str) -> Dict[str, str]:
    """
    Capture artifacts for a specific test step.
    
    Args:
        page: Playwright page object
        test_name: Name of the test
        step_name: Name of the step being captured
        
    Returns:
        Dictionary with paths to captured artifacts
    """
    return capture_failure_artifacts(page, test_name, f"step_{step_name}")


def ensure_artifacts_captured(page: Page, test_name: str, error_type: str = "failure") -> Dict[str, str]:
    """
    Guaranteed artifact capture with multiple fallback strategies.
    
    Args:
        page: Playwright page object
        test_name: Name of the test
        error_type: Type of error/failure
        
    Returns:
        Dictionary with paths to captured artifacts
    """
    # Try primary capture method
    artifacts = capture_failure_artifacts(page, test_name, error_type)
    
    # If primary method failed, try fallback methods
    if not artifacts.get("screenshot") or not artifacts.get("html_snapshot"):
        print("Primary artifact capture failed, trying fallback methods...")
        
        # Fallback 1: Try with simplified paths
        try:
            fallback_dir = Path(tempfile.gettempdir()) / "test_artifacts_fallback"
            fallback_dir.mkdir(exist_ok=True)
            
            timestamp = int(time.time())
            sanitized_test_name = _sanitize_test_name(test_name)
            
            # Try screenshot capture
            if not artifacts.get("screenshot"):
                try:
                    screenshot_path = fallback_dir / f"{sanitized_test_name}_{error_type}_{timestamp}.png"
                    page.screenshot(path=str(screenshot_path))
                    artifacts["screenshot"] = str(screenshot_path)
                    print(f"✓ Fallback screenshot captured: {artifacts['screenshot']}")
                except Exception as e:
                    print(f"Fallback screenshot capture failed: {e}")
            
            # Try HTML capture
            if not artifacts.get("html_snapshot"):
                try:
                    html_path = fallback_dir / f"{sanitized_test_name}_{error_type}_{timestamp}.html"
                    html_content = page.content()
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    artifacts["html_snapshot"] = str(html_path)
                    print(f"✓ Fallback HTML captured: {artifacts['html_snapshot']}")
                except Exception as e:
                    print(f"Fallback HTML capture failed: {e}")
                    
        except Exception as e:
            print(f"Fallback artifact capture failed: {e}")
    
    return artifacts


def get_artifact_summary(test_name: str) -> Dict[str, Any]:
    """
    Get a summary of artifacts for a specific test.
    
    Args:
        test_name: Name of the test
        
    Returns:
        Dictionary with artifact summary information
    """
    test_dir = ARTIFACTS_DIR / _sanitize_test_name(test_name)
    artifacts = []
    total_count = 0
    
    if test_dir.exists():
        # Check screenshots
        screenshots_dir = test_dir / "screenshots"
        if screenshots_dir.exists():
            for screenshot_file in screenshots_dir.glob("*.png"):
                artifacts.append({
                    "type": "screenshot",
                    "path": str(screenshot_file.relative_to(ARTIFACTS_DIR)),
                    "size": screenshot_file.stat().st_size,
                    "timestamp": screenshot_file.stat().st_mtime
                })
                total_count += 1
        
        # Check HTML snapshots
        html_dir = test_dir / "html"
        if html_dir.exists():
            for html_file in html_dir.glob("*.html"):
                artifacts.append({
                    "type": "html_snapshot",
                    "path": str(html_file.relative_to(ARTIFACTS_DIR)),
                    "size": html_file.stat().st_size,
                    "timestamp": html_file.stat().st_mtime
                })
                total_count += 1
    
    return {
        "test_name": test_name,
        "artifacts": artifacts,
        "total_count": total_count
    }


def _sanitize_test_name(test_name: str) -> str:
    """Sanitize test name for use as directory name."""
    return test_name.replace('/', '_').replace('\\', '_').replace(':', '_')


def create_artifact_report(test_names: list) -> str:
    """
    Create a comprehensive artifact report for multiple tests.
    
    Args:
        test_names: List of test names to include in report
        
    Returns:
        Formatted report string
    """
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("ARTIFACT CAPTURE REPORT")
    report_lines.append("=" * 80)
    report_lines.append(f"Generated: {datetime.now().isoformat()}")
    report_lines.append(f"Artifacts Directory: {ARTIFACTS_DIR}")
    report_lines.append("")
    
    total_artifacts = 0
    
    for test_name in test_names:
        summary = get_artifact_summary(test_name)
        report_lines.append(f"Test: {test_name}")
        report_lines.append(f"  Total Artifacts: {summary['total_count']}")
        
        if summary['artifacts']:
            for artifact in summary['artifacts']:
                report_lines.append(f"    {artifact['type']}: {artifact['path']}")
        else:
            report_lines.append("    No artifacts captured")
        
        report_lines.append("")
        total_artifacts += summary['total_count']
    
    report_lines.append(f"Total Artifacts Across All Tests: {total_artifacts}")
    report_lines.append("")
    report_lines.append("To view artifacts in CI:")
    report_lines.append("1. Download the artifacts directory from CI")
    report_lines.append("2. Open HTML files in a web browser")
    report_lines.append("3. View PNG screenshots with any image viewer")
    report_lines.append("=" * 80)
    
    return "\n".join(report_lines)


def save_artifact_report(test_names: list, output_path: Optional[Path] = None) -> Path:
    """
    Save artifact report to file with enhanced error handling.
    
    Args:
        test_names: List of test names to include in report
        output_path: Optional output path, defaults to artifacts directory
        
    Returns:
        Path to saved report file
    """
    if output_path is None:
        output_path = ARTIFACTS_DIR / "artifact_report.txt"
    
    report_content = create_artifact_report(test_names)
    
    # Try multiple fallback locations if the primary location fails
    fallback_locations = [
        output_path,
        Path.cwd() / "artifact_report.txt",
        Path(tempfile.gettempdir()) / "artifact_report.txt",
        Path("/tmp/artifact_report.txt")
    ]
    
    for location in fallback_locations:
        try:
            # Ensure the directory exists
            location.parent.mkdir(parents=True, exist_ok=True)
            
            with open(location, 'w') as f:
                f.write(report_content)
            
            print(f"✓ Artifact report saved to: {location}")
            return location
        except (PermissionError, OSError) as e:
            print(f"Warning: Could not write to {location}: {e}")
            continue
    
    # If all locations fail, print the report to console
    print("Warning: Could not save artifact report to any location")
    print("Printing report to console:")
    print(report_content)
    
    # Return a dummy path to avoid breaking the test
    return Path("/tmp/artifact_report.txt")


def log_artifacts_to_console(artifacts: Dict[str, str], test_name: str):
    """
    Log artifact paths to console for easy access.
    
    Args:
        artifacts: Dictionary of captured artifacts
        test_name: Name of the test
    """
    print(f"\n📋 Artifacts captured for test: {test_name}")
    print("=" * 50)
    
    if artifacts.get("screenshot"):
        print(f"📸 Screenshot: {artifacts['screenshot']}")
    else:
        print("❌ Screenshot: Failed to capture")
    
    if artifacts.get("html_snapshot"):
        print(f"🌐 HTML Snapshot: {artifacts['html_snapshot']}")
    else:
        print("❌ HTML Snapshot: Failed to capture")
    
    print("=" * 50)


def cleanup_old_artifacts(max_age_hours: int = 24):
    """
    Clean up old artifacts to prevent disk space issues.
    
    Args:
        max_age_hours: Maximum age of artifacts in hours before cleanup
    """
    try:
        cutoff_time = time.time() - (max_age_hours * 3600)
        cleaned_count = 0
        
        for artifact_file in ARTIFACTS_DIR.rglob("*"):
            if artifact_file.is_file() and artifact_file.stat().st_mtime < cutoff_time:
                try:
                    artifact_file.unlink()
                    cleaned_count += 1
                except Exception as e:
                    print(f"Warning: Could not delete old artifact {artifact_file}: {e}")
        
        if cleaned_count > 0:
            print(f"✓ Cleaned up {cleaned_count} old artifacts")
    except Exception as e:
        print(f"Warning: Artifact cleanup failed: {e}")
