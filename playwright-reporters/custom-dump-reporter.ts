import { Reporter, TestCase, TestResult, FullConfig } from '@playwright/test/reporter';
import * as fs from 'fs';
import * as path from 'path';

interface ArtifactInfo {
  type: string;
  path: string;
  description: string;
}

interface TestDump {
  title: string;
  status: string;
  duration: number;
  retryCount: number;
  artifacts: ArtifactInfo[];
  errorMessage?: string;
  timestamp: string;
}

class CustomDumpReporter implements Reporter {
  private testResults: Map<string, TestResult> = new Map();

  onBegin(config: FullConfig, suite: any) {
    console.log(`🚀 Starting test run with ${suite.allTests().length} tests`);
  }

  onTestEnd(test: TestCase, result: TestResult) {
    this.testResults.set(test.id, result);
    
    if (result.status !== 'passed') {
      this.captureArtifacts(test, result);
    }
  }

  private async captureArtifacts(test: TestCase, result: TestResult) {
    const testTitle = this.sanitizeTestTitle(test.title);
    const artifactDir = path.join('artifacts', 'e2e', testTitle);
    
    // Create artifact directory
    if (!fs.existsSync(artifactDir)) {
      fs.mkdirSync(artifactDir, { recursive: true });
    }

    const artifacts: ArtifactInfo[] = [];
    const dump: TestDump = {
      title: test.title,
      status: result.status,
      duration: result.duration,
      retryCount: result.retryCount,
      artifacts: artifacts,
      errorMessage: result.error?.message,
      timestamp: new Date().toISOString()
    };

    // Capture screenshots
    if (result.attachments) {
      for (const attachment of result.attachments) {
        if (attachment.name === 'screenshot') {
          const screenshotPath = path.join(artifactDir, 'screenshot.png');
          if (attachment.body) {
            fs.writeFileSync(screenshotPath, attachment.body);
            artifacts.push({
              type: 'screenshot',
              path: screenshotPath,
              description: 'Full page screenshot on failure'
            });
          }
        } else if (attachment.name === 'video') {
          const videoPath = path.join(artifactDir, 'video.webm');
          if (attachment.body) {
            fs.writeFileSync(videoPath, attachment.body);
            artifacts.push({
              type: 'video',
              path: videoPath,
              description: 'Test execution video'
            });
          }
        } else if (attachment.name === 'trace') {
          const tracePath = path.join(artifactDir, 'trace.zip');
          if (attachment.body) {
            fs.writeFileSync(tracePath, attachment.body);
            artifacts.push({
              type: 'trace',
              path: tracePath,
              description: 'Playwright trace file'
            });
          }
        }
      }
    }

    // Copy HAR file if it exists
    const harPath = 'artifacts/e2e/har/fe-be.har';
    if (fs.existsSync(harPath)) {
      const harCopyPath = path.join(artifactDir, 'fe-be.har');
      fs.copyFileSync(harPath, harCopyPath);
      artifacts.push({
        type: 'har',
        path: harCopyPath,
        description: 'HTTP Archive (HAR) file with all requests'
      });
    }

    // Capture DOM content if page is available
    if (result.error && result.error.message.includes('page')) {
      try {
        // This would need to be captured during test execution
        const domPath = path.join(artifactDir, 'dom.html');
        // For now, we'll create a placeholder
        fs.writeFileSync(domPath, `<!-- DOM content would be captured here -->\n<!-- Test: ${test.title} -->\n<!-- Error: ${result.error.message} -->`);
        artifacts.push({
          type: 'dom',
          path: domPath,
          description: 'Page DOM content at time of failure'
        });
      } catch (e) {
        console.warn('Could not capture DOM content:', e);
      }
    }

    // Create console and network log
    const logPath = path.join(artifactDir, 'console-and-network.log');
    const logContent = [
      `Test: ${test.title}`,
      `Status: ${result.status}`,
      `Duration: ${result.duration}ms`,
      `Retry Count: ${result.retryCount}`,
      `Timestamp: ${new Date().toISOString()}`,
      '',
      'Error Details:',
      result.error?.message || 'No error message',
      '',
      'Stack Trace:',
      result.error?.stack || 'No stack trace',
      '',
      'Test Location:',
      `${test.location.file}:${test.location.line}`,
      '',
      'Artifacts Captured:',
      ...artifacts.map(a => `- ${a.type}: ${a.path}`)
    ].join('\n');
    
    fs.writeFileSync(logPath, logContent);
    artifacts.push({
      type: 'log',
      path: logPath,
      description: 'Console and network activity log'
    });

    // Create sample response JSON (placeholder)
    const responsePath = path.join(artifactDir, 'sample-response.json');
    const sampleResponse = {
      test: test.title,
      status: result.status,
      error: result.error?.message,
      timestamp: new Date().toISOString(),
      note: 'This is a placeholder. Actual API responses would be captured during test execution.'
    };
    fs.writeFileSync(responsePath, JSON.stringify(sampleResponse, null, 2));
    artifacts.push({
      type: 'response',
      path: responsePath,
      description: 'Sample API response data'
    });

    // Update dump with artifacts
    dump.artifacts = artifacts;

    // Write dump files
    const dumpJsonPath = path.join(artifactDir, 'dump.json');
    const dumpMdPath = path.join(artifactDir, 'dump.md');
    
    fs.writeFileSync(dumpJsonPath, JSON.stringify(dump, null, 2));
    
    const markdownContent = this.generateMarkdownReport(dump);
    fs.writeFileSync(dumpMdPath, markdownContent);

    console.log(`📸 Artifacts captured for failed test: ${test.title}`);
    console.log(`   📁 Location: ${artifactDir}`);
    console.log(`   📊 Artifacts: ${artifacts.length} files`);
  }

  private sanitizeTestTitle(title: string): string {
    return title
      .replace(/[^a-zA-Z0-9\s-]/g, '')
      .replace(/\s+/g, '_')
      .toLowerCase()
      .substring(0, 50);
  }

  private generateMarkdownReport(dump: TestDump): string {
    return `# Test Failure Report

## Test Information
- **Title**: ${dump.title}
- **Status**: ${dump.status}
- **Duration**: ${dump.duration}ms
- **Retry Count**: ${dump.retryCount}
- **Timestamp**: ${dump.timestamp}

## Error Details
${dump.errorMessage ? `\`\`\`\n${dump.errorMessage}\n\`\`\`` : 'No error message available'}

## Artifacts Captured
${dump.artifacts.map(artifact => `- **${artifact.type}**: \`${artifact.path}\` - ${artifact.description}`).join('\n')}

## How to Use These Artifacts

### Screenshot
View the full page screenshot to see the UI state at the time of failure.

### Video
Play the video to see the test execution and identify where it failed.

### Trace
Use Playwright Trace Viewer to analyze the test step by step:
\`\`\`bash
npx playwright show-trace ${dump.artifacts.find(a => a.type === 'trace')?.path || 'trace.zip'}
\`\`\`

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
`;
  }

  onEnd(result: any) {
    const failedTests = Array.from(this.testResults.values()).filter(r => r.status !== 'passed');
    if (failedTests.length > 0) {
      console.log(`\n❌ Test run completed with ${failedTests.length} failures`);
      console.log('📸 Artifacts have been captured in the artifacts/e2e/ directory');
    } else {
      console.log('\n✅ All tests passed!');
    }
  }
}

export default CustomDumpReporter;
