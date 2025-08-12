"""
Enhanced test helpers for artifact capture in browser tests.
Provides utilities for capturing screenshots and HTML snapshots on failures.
"""

import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from playwright.sync_api import Page

# Import artifact capture from conftest
try:
    from conftest import artifact_capture, ARTIFACTS_DIR, HTML_DIR
except ImportError:
    # Fallback if conftest is not available
    ARTIFACTS_DIR = Path(__file__).parent / "artifacts"
    HTML_DIR = ARTIFACTS_DIR / "html"
    artifact_capture = None


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
    
    # Create test-specific directory
    test_dir = ARTIFACTS_DIR / _sanitize_test_name(test_name)
    test_dir.mkdir(exist_ok=True)
    (test_dir / "screenshots").mkdir(exist_ok=True)
    (test_dir / "html").mkdir(exist_ok=True)
    
    # Capture screenshot
    try:
        screenshot_path = test_dir / "screenshots" / f"{error_type}_{timestamp}.png"
        page.screenshot(path=str(screenshot_path))
        artifacts["screenshot"] = str(screenshot_path.relative_to(ARTIFACTS_DIR.parent))
    except Exception as e:
        print(f"Failed to capture screenshot: {e}")
        artifacts["screenshot"] = None
    
    # Capture HTML snapshot
    try:
        html_path = test_dir / "html" / f"{error_type}_{timestamp}.html"
        html_content = page.content()
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        artifacts["html_snapshot"] = str(html_path.relative_to(ARTIFACTS_DIR.parent))
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
    Ensure artifacts are captured, even if previous attempts failed.
    
    Args:
        page: Playwright page object
        test_name: Name of the test
        error_type: Type of error/failure
        
    Returns:
        Dictionary with paths to captured artifacts
    """
    artifacts = capture_failure_artifacts(page, test_name, error_type)
    
    # Ensure we have at least placeholder paths
    if not artifacts.get("screenshot"):
        artifacts["screenshot"] = f"artifacts/{test_name}/screenshots/{error_type}_failed.png"
    
    if not artifacts.get("html_snapshot"):
        artifacts["html_snapshot"] = f"artifacts/{test_name}/html/{error_type}_failed.html"
    
    return artifacts


def log_artifacts_to_console(artifacts: Dict[str, str], prefix: str = ""):
    """
    Log artifact paths to console for easy access.
    
    Args:
        artifacts: Dictionary of artifact paths
        prefix: Optional prefix for log messages
    """
    if artifacts.get("screenshot"):
        print(f"{prefix}Screenshot: {artifacts['screenshot']}")
    if artifacts.get("html_snapshot"):
        print(f"{prefix}HTML Snapshot: {artifacts['html_snapshot']}")


def get_artifact_summary(test_name: str) -> Dict[str, Any]:
    """
    Get a summary of all artifacts for a test.
    
    Args:
        test_name: Name of the test
        
    Returns:
        Dictionary with artifact summary
    """
    test_dir = ARTIFACTS_DIR / _sanitize_test_name(test_name)
    
    if not test_dir.exists():
        return {"test_name": test_name, "artifacts": [], "total_count": 0}
    
    artifacts = []
    total_count = 0
    
    # Scan screenshots
    screenshots_dir = test_dir / "screenshots"
    if screenshots_dir.exists():
        for screenshot in screenshots_dir.glob("*.png"):
            artifacts.append({
                "type": "screenshot",
                "path": str(screenshot.relative_to(ARTIFACTS_DIR.parent)),
                "size": screenshot.stat().st_size if screenshot.exists() else 0,
                "timestamp": screenshot.stat().st_mtime if screenshot.exists() else 0
            })
            total_count += 1
    
    # Scan HTML snapshots
    html_dir = test_dir / "html"
    if html_dir.exists():
        for html_file in html_dir.glob("*.html"):
            artifacts.append({
                "type": "html_snapshot",
                "path": str(html_file.relative_to(ARTIFACTS_DIR.parent)),
                "size": html_file.stat().st_size if html_file.exists() else 0,
                "timestamp": html_file.stat().st_mtime if html_file.exists() else 0
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
    Save artifact report to file.
    
    Args:
        test_names: List of test names to include in report
        output_path: Optional output path, defaults to artifacts directory
        
    Returns:
        Path to saved report file
    """
    if output_path is None:
        output_path = ARTIFACTS_DIR / "artifact_report.txt"
    
    report_content = create_artifact_report(test_names)
    
    with open(output_path, 'w') as f:
        f.write(report_content)
    
    return output_path
