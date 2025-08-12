# Test Failure Report

## Test Information
- **Title**: S3: Save Draft + Resume - persistence verification
- **Status**: timedOut
- **Duration**: 30087ms
- **Retry Count**: undefined
- **Timestamp**: 2025-08-12T09:26:49.901Z

## Error Details
```
[31mTest timeout of 30000ms exceeded.[39m
```

## Artifacts Captured
- **har**: `artifacts/e2e/s3_save_draft_resume_-_persistence_verification/fe-be.har` - HTTP Archive (HAR) file with all requests
- **log**: `artifacts/e2e/s3_save_draft_resume_-_persistence_verification/console-and-network.log` - Console and network activity log
- **response**: `artifacts/e2e/s3_save_draft_resume_-_persistence_verification/sample-response.json` - Sample API response data

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
