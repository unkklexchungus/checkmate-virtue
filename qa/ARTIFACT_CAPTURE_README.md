# Enhanced Playwright Test Artifact Capture

This document describes the enhanced Playwright test harness that captures both screenshots and HTML snapshots on every failing step.

## Overview

The enhanced test system provides:

1. **Automatic artifact capture** on every test failure
2. **Both screenshots and HTML snapshots** for comprehensive debugging
3. **Organized artifact storage** by test name and failure type
4. **CI integration** with artifact reporting
5. **Minimal code changes** to existing tests

## Directory Structure

```
qa/
├── artifacts/                    # Main artifacts directory
│   ├── screenshots/             # Global screenshots
│   ├── html/                    # Global HTML snapshots
│   ├── test_name_1/            # Test-specific artifacts
│   │   ├── screenshots/
│   │   └── html/
│   └── test_name_2/
│       ├── screenshots/
│       └── html/
├── conftest.py                  # Pytest configuration with artifact capture
├── test_artifact_helpers.py     # Helper functions for artifact capture
├── run_browser_tests.py         # Enhanced main test runner
└── logs/                        # Legacy logs (still maintained)
    ├── screenshots/
    └── error-log.json
```

## Usage

### For Pytest-based Tests

1. **Use the enhanced page fixture:**

```python
import pytest
from playwright.sync_api import Page

def test_example(page_with_artifacts: Page):
    """Test that automatically captures artifacts on failure."""
    page_with_artifacts.goto("http://example.com")
    # If this fails, both screenshot and HTML will be captured
    assert page_with_artifacts.title() == "Expected Title"
```

2. **Manual artifact capture:**

```python
from test_artifact_helpers import capture_failure_artifacts

def test_with_manual_capture(page: Page):
    try:
        page.goto("http://example.com")
        # Your test logic
    except Exception as e:
        artifacts = capture_failure_artifacts(page, "test_with_manual_capture", "custom_error")
        print(f"Artifacts captured: {artifacts}")
        raise
```

### For Legacy Tests (run_browser_tests.py)

The main test runner has been enhanced to automatically capture artifacts on all failures. No changes needed to existing test logic.

## Artifact Types

### Screenshots
- **Format**: PNG
- **Location**: `artifacts/{test_name}/screenshots/{error_type}_{timestamp}.png`
- **Content**: Full page screenshot at time of failure

### HTML Snapshots
- **Format**: HTML
- **Location**: `artifacts/{test_name}/html/{error_type}_{timestamp}.html`
- **Content**: Complete HTML content of the page at time of failure

## Error Types

The system captures artifacts for these error types:

- `failure` - General test failures
- `JS_ERROR` - JavaScript console errors
- `UNHANDLED_EXCEPTION` - Unhandled page exceptions
- `NETWORK_ERROR` - Failed network requests
- `HTTP_ERROR` - HTTP 4xx/5xx responses
- `NAVIGATION_ERROR` - Page navigation failures
- `REGRESSION_FAILED` - Regression test failures
- `TEST_ERROR` - Test execution errors

## CI Integration

### GitHub Actions Example

```yaml
name: Browser Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install playwright pytest
          playwright install
      
      - name: Run browser tests
        run: |
          cd qa
          python3 run_browser_tests.py
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        if: always()  # Upload even if tests fail
        with:
          name: test-artifacts
          path: qa/artifacts/
          retention-days: 30
```

### Viewing Artifacts in CI

1. **Download artifacts** from CI run
2. **Extract the artifacts directory**
3. **Open HTML files** in a web browser to see page state
4. **View PNG screenshots** with any image viewer

## Helper Functions

### capture_failure_artifacts()

```python
from test_artifact_helpers import capture_failure_artifacts

artifacts = capture_failure_artifacts(page, "my_test", "custom_error")
# Returns: {"screenshot": "path/to/screenshot.png", "html_snapshot": "path/to/html.html"}
```

### capture_step_artifacts()

```python
from test_artifact_helpers import capture_step_artifacts

artifacts = capture_step_artifacts(page, "my_test", "login_step")
# Captures artifacts for a specific test step
```

### ensure_artifacts_captured()

```python
from test_artifact_helpers import ensure_artifacts_captured

artifacts = ensure_artifacts_captured(page, "my_test", "failure")
# Ensures artifacts are captured even if previous attempts failed
```

### create_artifact_report()

```python
from test_artifact_helpers import create_artifact_report, save_artifact_report

# Create report for multiple tests
report = create_artifact_report(["test_1", "test_2", "test_3"])
print(report)

# Save report to file
save_artifact_report(["test_1", "test_2"], "my_report.txt")
```

## Configuration

### Environment Variables

```bash
# Control artifact capture behavior
ARTIFACTS_DIR=./qa/artifacts  # Custom artifacts directory
CAPTURE_HTML=true             # Enable/disable HTML capture (default: true)
CAPTURE_SCREENSHOTS=true      # Enable/disable screenshot capture (default: true)
```

### Pytest Configuration

Add to `pyproject.toml` or `pytest.ini`:

```ini
[tool.pytest.ini_options]
addopts = "--tb=short"
testpaths = ["qa"]
python_files = ["test_*.py", "*_test.py"]
markers = [
    "browser: marks tests as browser-based",
    "playwright: marks tests as requiring Playwright"
]
```

## Troubleshooting

### Artifacts Not Captured

1. **Check directory permissions** - Ensure write access to artifacts directory
2. **Verify page object** - Ensure page is valid and accessible
3. **Check error handling** - Ensure exceptions are properly caught

### Large Artifact Files

1. **HTML files** can be large for complex pages
2. **Screenshots** are typically 100KB-1MB depending on page size
3. **Consider cleanup** for long-running CI pipelines

### Performance Impact

- **Minimal overhead** - Artifacts only captured on failures
- **Async capture** - Non-blocking capture in most cases
- **Configurable** - Can disable specific artifact types if needed

## Migration Guide

### From Legacy System

1. **No code changes required** for existing tests
2. **Enhanced logging** provides more detailed artifact information
3. **Better organization** by test name instead of timestamp only

### To Pytest-based Tests

1. **Replace `page` fixture** with `page_with_artifacts`
2. **Add pytest markers** for better test organization
3. **Use helper functions** for manual artifact capture when needed

## Best Practices

1. **Use descriptive test names** for better artifact organization
2. **Capture artifacts early** in error handling
3. **Review artifacts regularly** to identify patterns
4. **Clean up old artifacts** in long-running CI pipelines
5. **Document custom error types** for team consistency

## Support

For issues with artifact capture:

1. Check the console output for capture errors
2. Verify file system permissions
3. Review the artifact report for missing files
4. Check Playwright version compatibility
