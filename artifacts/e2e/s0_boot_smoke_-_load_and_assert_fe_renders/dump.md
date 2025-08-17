# Test Failure Report

## Test Information
- **Title**: S0: Boot smoke - load "/" and assert FE renders
- **Status**: failed
- **Duration**: 264ms
- **Retry Count**: undefined
- **Timestamp**: 2025-08-14T10:17:57.658Z

## Error Details
```
Error: page.goto: net::ERR_SSL_PROTOCOL_ERROR at http://app:8000/
Call log:
[2m  - navigating to "http://app:8000/", waiting until "load"[22m

```

## Artifacts Captured
- **har**: `artifacts/e2e/s0_boot_smoke_-_load_and_assert_fe_renders/fe-be.har` - HTTP Archive (HAR) file with all requests
- **dom**: `artifacts/e2e/s0_boot_smoke_-_load_and_assert_fe_renders/dom.html` - Page DOM content at time of failure
- **log**: `artifacts/e2e/s0_boot_smoke_-_load_and_assert_fe_renders/console-and-network.log` - Console and network activity log
- **response**: `artifacts/e2e/s0_boot_smoke_-_load_and_assert_fe_renders/sample-response.json` - Sample API response data

## How to Use These Artifacts

### Screenshot
View the full page screenshot to see the UI state at the time of failure.

### Video
Play the video to see the test execution and identify where it failed.

### Trace
Use Playwright Trace Viewer to analyze the test step by step:
```bash
npx playwright show-trace trace.zip
```

### HAR File
Analyze network requests and responses using browser dev tools or HAR viewers.

### Console Log
Check for JavaScript errors and network failures in the console log.

### DOM Content
Examine the page structure at the time of failure.

## Next Steps
1. Review the screenshot and video to understand the failure
2. Check the console log for errors
3. Use the trace file for detailed step-by-step analysis
4. Verify network requests in the HAR file
5. Reproduce the issue locally if possible
