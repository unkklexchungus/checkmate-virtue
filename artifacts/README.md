# Test Artifacts Documentation

This directory contains test artifacts generated during E2E testing and performance monitoring.

## Directory Structure

```
artifacts/
├── README.md                    # This file
├── junit.xml                    # JUnit test results
└── e2e/                         # E2E test artifacts
    ├── har/                     # HTTP Archive (HAR) files
    │   └── fe-be.har           # Frontend-backend communication logs
    ├── screenshots/             # Test failure screenshots
    ├── videos/                  # Test execution videos (on failure)
    ├── traces/                  # Playwright trace files (on failure)
    └── [test-name]/             # Test-specific artifacts (organized by test name)
        ├── dump.json            # Test data dump
        ├── dump.md              # Human-readable test summary
        ├── fe-be.har            # Test-specific HAR file
        └── [other artifacts]    # Additional test-specific files
```

## Artifact Types

### E2E Test Artifacts (`artifacts/e2e/`)

#### HAR Files (`har/`)
- **Purpose**: Capture HTTP requests/responses between frontend and backend
- **Location**: `artifacts/e2e/har/fe-be.har`
- **Use Case**: Debug API communication issues, analyze request patterns
- **Format**: HTTP Archive (HAR) format, viewable in browser dev tools

#### Screenshots (`screenshots/`)
- **Purpose**: Visual snapshots of test failures
- **Location**: `artifacts/e2e/screenshots/`
- **Use Case**: Debug UI issues, verify visual state at failure point
- **Format**: PNG images

#### Videos (`videos/`)
- **Purpose**: Record test execution for failed tests
- **Location**: `artifacts/e2e/videos/`
- **Use Case**: Step-by-step replay of test failures
- **Format**: MP4 video files

#### Traces (`traces/`)
- **Purpose**: Detailed execution traces for failed tests
- **Location**: `artifacts/e2e/traces/`
- **Use Case**: Deep debugging of test execution, timing analysis
- **Format**: Playwright trace files (viewable with `npx playwright show-trace`)

### Test-Specific Artifacts (`artifacts/e2e/[test-name]/`)

Each test creates its own subdirectory with:
- **dump.json**: Raw test data and state
- **dump.md**: Human-readable test summary
- **fe-be.har**: Test-specific HTTP communication logs
- **Additional files**: Test-specific artifacts (images, reports, etc.)

## Performance Monitoring

### Frontend Performance Marks
- **VIN Decode**: `vin-decode-start` → `vin-decode-end`
- **Save Inspection**: `save-inspection-start` → `save-inspection-end`
- **Finalize Inspection**: `finalize-inspection-start` → `finalize-inspection-end`

### Backend Request Timing
- **Log Level**: INFO (development only)
- **Format**: `PERF: {endpoint_name} completed in {duration}ms`
- **Location**: Application logs

## How to Use

### Viewing HAR Files
```bash
# Open in browser dev tools
# Or use HAR viewer tools
```

### Viewing Traces
```bash
npx playwright show-trace artifacts/e2e/traces/[trace-file].zip
```

### Analyzing Performance
```bash
# Check browser console for frontend timing marks
# Check application logs for backend timing
```

### Debugging Test Failures
1. Check `artifacts/e2e/screenshots/` for visual state
2. Review `artifacts/e2e/videos/` for execution replay
3. Analyze `artifacts/e2e/traces/` for detailed execution
4. Examine `artifacts/e2e/har/` for API communication issues

## Cleanup

Artifacts are automatically cleaned up between test runs, but you can manually clean them:

```bash
# Remove all artifacts
rm -rf artifacts/e2e/*

# Remove specific test artifacts
rm -rf artifacts/e2e/[test-name]/
```

## Notes

- Artifacts are only generated on test failures by default (except HAR files)
- Performance timing is lightweight and doesn't impact test execution
- All timing data is logged at INFO level for easy filtering
- Test-specific artifacts are organized by test name for easy identification
