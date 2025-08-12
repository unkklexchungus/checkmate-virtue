# Test Failure Report

## Test Information
- **Title**: S4: Finalize + Report - generate and validate report
- **Status**: failed
- **Duration**: 9539ms
- **Retry Count**: undefined
- **Timestamp**: 2025-08-12T09:30:35.171Z

## Error Details
```
Error: [31mTimed out 5000ms waiting for [39m[2mexpect([22m[31mlocator[39m[2m).[22mtoContainText[2m([22m[32mexpected[39m[2m)[22m

Locator: locator('[data-testid="inspection-status"]')
[32m- Expected string  - 1[39m
[31m+ Received string  + 3[39m

[32m- finalized[39m
[31m+[39m
[31m+                          Status: Draft[39m
[31m+ [43m                    [49m[39m
Call log:
[2m  - Expect "toContainText" with timeout 5000ms[22m
[2m  - waiting for locator('[data-testid="inspection-status"]')[22m
[2m    9 × locator resolved to <div id="inspection-status" class="alert alert-info" data-testid="inspection-status">…</div>[22m
[2m      - unexpected value "[22m
[2m                         Status: Draft[22m
[2m                    "[22m

```

## Artifacts Captured
- **har**: `artifacts/e2e/s4_finalize_report_-_generate_and_validate_report/fe-be.har` - HTTP Archive (HAR) file with all requests
- **log**: `artifacts/e2e/s4_finalize_report_-_generate_and_validate_report/console-and-network.log` - Console and network activity log
- **response**: `artifacts/e2e/s4_finalize_report_-_generate_and_validate_report/sample-response.json` - Sample API response data

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
