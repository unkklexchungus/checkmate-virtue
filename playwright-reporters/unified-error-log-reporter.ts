import { Reporter, TestCase, TestResult, FullConfig } from '@playwright/test/reporter';
import * as fs from 'fs';
import * as path from 'path';

interface ErrorLogEntry {
  testTitle: string;
  status: string;
  duration: number;
  retryCount: number;
  errorMessage?: string;
  stackTrace?: string;
  consoleErrors: string[];
  httpErrors: string[];
  testLocation: string;
  timestamp: string;
  artifacts: string[];
}

interface UnifiedErrorLog {
  summary: {
    totalTests: number;
    passedTests: number;
    failedTests: number;
    skippedTests: number;
    totalDuration: number;
    timestamp: string;
  };
  errors: ErrorLogEntry[];
  environment: {
    baseURL: string;
    browser: string;
    viewport: string;
    userAgent: string;
  };
  recommendations: string[];
}

class UnifiedErrorLogReporter implements Reporter {
  private testResults: Map<string, TestResult> = new Map();
  private consoleErrors: Map<string, string[]> = new Map();
  private httpErrors: Map<string, string[]> = new Map();
  private totalTests = 0;
  private startTime = Date.now();

  onBegin(config: FullConfig, suite: any) {
    this.totalTests = suite.allTests().length;
    console.log(`🚀 Starting test run with ${this.totalTests} tests`);
  }

  onTestBegin(test: TestCase) {
    this.consoleErrors.set(test.id, []);
    this.httpErrors.set(test.id, []);
  }

  onTestEnd(test: TestCase, result: TestResult) {
    this.testResults.set(test.id, result);
  }

  // Capture console errors during test execution
  captureConsoleError(testId: string, error: string) {
    const errors = this.consoleErrors.get(testId) || [];
    errors.push(error);
    this.consoleErrors.set(testId, errors);
  }

  // Capture HTTP errors during test execution
  captureHttpError(testId: string, error: string) {
    const errors = this.httpErrors.get(testId) || [];
    errors.push(error);
    this.httpErrors.set(testId, errors);
  }

  onEnd(result: any) {
    const unifiedLog = this.generateUnifiedErrorLog();
    const logPath = path.join('artifacts', 'e2e', 'unified-error-log.txt');
    
    // Ensure artifacts directory exists
    const artifactsDir = path.dirname(logPath);
    if (!fs.existsSync(artifactsDir)) {
      fs.mkdirSync(artifactsDir, { recursive: true });
    }
    
    fs.writeFileSync(logPath, unifiedLog);
    
    const failedTests = Array.from(this.testResults.values()).filter(r => r.status !== 'passed');
    if (failedTests.length > 0) {
      console.log(`\n❌ Test run completed with ${failedTests.length} failures`);
      console.log(`📋 Unified error log saved to: ${logPath}`);
      console.log(`📋 Copy this file to share with ChatGPT for debugging assistance`);
    } else {
      console.log('\n✅ All tests passed!');
    }
  }

  private generateUnifiedErrorLog(): string {
    const failedTests = Array.from(this.testResults.entries())
      .filter(([_, result]) => result.status !== 'passed')
      .map(([testId, result]) => {
        const test = this.findTestCaseById(testId);
        if (!test) return null;

        const consoleErrors = this.consoleErrors.get(testId) || [];
        const httpErrors = this.httpErrors.get(testId) || [];
        
        return {
          testTitle: test.title,
          status: result.status,
          duration: result.duration,
          retryCount: result.retryCount,
          errorMessage: result.error?.message,
          stackTrace: result.error?.stack,
          consoleErrors,
          httpErrors,
          testLocation: `${test.location.file}:${test.location.line}`,
          timestamp: new Date().toISOString(),
          artifacts: this.getArtifactPaths(test, result)
        };
      })
      .filter(Boolean) as ErrorLogEntry[];

    const passedTests = Array.from(this.testResults.values()).filter(r => r.status === 'passed').length;
    const skippedTests = Array.from(this.testResults.values()).filter(r => r.status === 'skipped').length;
    const totalDuration = Date.now() - this.startTime;

    const summary = {
      totalTests: this.totalTests,
      passedTests,
      failedTests: failedTests.length,
      skippedTests,
      totalDuration,
      timestamp: new Date().toISOString()
    };

    const recommendations = this.generateRecommendations(failedTests);

    return this.formatUnifiedLog({ summary, errors: failedTests, recommendations });
  }

  private findTestCaseById(testId: string): TestCase | null {
    // This is a simplified approach - in a real implementation, you'd store test cases
    // For now, we'll return a mock object
    return {
      title: testId,
      location: { file: 'unknown', line: 0 }
    } as TestCase;
  }

  private getArtifactPaths(test: TestCase, result: TestResult): string[] {
    const artifacts: string[] = [];
    const testTitle = this.sanitizeTestTitle(test.title);
    const artifactDir = path.join('artifacts', 'e2e', testTitle);
    
    if (result.attachments) {
      for (const attachment of result.attachments) {
        if (attachment.name === 'screenshot') {
          artifacts.push(`${artifactDir}/screenshot.png`);
        } else if (attachment.name === 'video') {
          artifacts.push(`${artifactDir}/video.webm`);
        } else if (attachment.name === 'trace') {
          artifacts.push(`${artifactDir}/trace.zip`);
        }
      }
    }
    
    // Add HAR file if it exists
    const harPath = path.join(artifactDir, 'fe-be.har');
    if (fs.existsSync(harPath)) {
      artifacts.push(harPath);
    }
    
    return artifacts;
  }

  private sanitizeTestTitle(title: string): string {
    return title
      .replace(/[^a-zA-Z0-9\s-]/g, '')
      .replace(/\s+/g, '_')
      .toLowerCase()
      .substring(0, 50);
  }

  private generateRecommendations(errors: ErrorLogEntry[]): string[] {
    const recommendations: string[] = [];
    
    // Analyze common patterns
    const consoleErrorCount = errors.reduce((sum, error) => sum + error.consoleErrors.length, 0);
    const httpErrorCount = errors.reduce((sum, error) => sum + error.httpErrors.length, 0);
    
    if (consoleErrorCount > 0) {
      recommendations.push('Review JavaScript console errors - there may be frontend issues');
    }
    
    if (httpErrorCount > 0) {
      recommendations.push('Check API endpoints and network connectivity');
    }
    
    const timeoutErrors = errors.filter(e => e.errorMessage?.includes('timeout'));
    if (timeoutErrors.length > 0) {
      recommendations.push('Consider increasing timeout values for slow operations');
    }
    
    const elementNotFoundErrors = errors.filter(e => e.errorMessage?.includes('locator'));
    if (elementNotFoundErrors.length > 0) {
      recommendations.push('Verify that all test selectors are correct and elements are present');
    }
    
    if (recommendations.length === 0) {
      recommendations.push('Review individual test failures for specific issues');
    }
    
    return recommendations;
  }

  private formatUnifiedLog(data: { summary: any; errors: ErrorLogEntry[]; recommendations: string[] }): string {
    const { summary, errors, recommendations } = data;
    
    let log = '';
    
    // Header
    log += '='.repeat(80) + '\n';
    log += 'E2E TEST UNIFIED ERROR LOG\n';
    log += '='.repeat(80) + '\n\n';
    
    // Summary
    log += '📊 TEST SUMMARY\n';
    log += '-'.repeat(40) + '\n';
    log += `Total Tests: ${summary.totalTests}\n`;
    log += `Passed: ${summary.passedTests}\n`;
    log += `Failed: ${summary.failedTests}\n`;
    log += `Skipped: ${summary.skippedTests}\n`;
    log += `Total Duration: ${summary.totalDuration}ms\n`;
    log += `Timestamp: ${summary.timestamp}\n\n`;
    
    if (errors.length === 0) {
      log += '✅ All tests passed successfully!\n\n';
    } else {
      // Failed Tests Details
      log += `❌ FAILED TESTS (${errors.length})\n`;
      log += '='.repeat(80) + '\n\n';
      
      errors.forEach((error, index) => {
        log += `TEST ${index + 1}: ${error.testTitle}\n`;
        log += '-'.repeat(60) + '\n';
        log += `Status: ${error.status}\n`;
        log += `Duration: ${error.duration}ms\n`;
        log += `Retry Count: ${error.retryCount}\n`;
        log += `Location: ${error.testLocation}\n`;
        log += `Timestamp: ${error.timestamp}\n\n`;
        
        if (error.errorMessage) {
          log += 'ERROR MESSAGE:\n';
          log += `${error.errorMessage}\n\n`;
        }
        
        if (error.stackTrace) {
          log += 'STACK TRACE:\n';
          log += `${error.stackTrace}\n\n`;
        }
        
        if (error.consoleErrors.length > 0) {
          log += 'CONSOLE ERRORS:\n';
          error.consoleErrors.forEach(err => {
            log += `  - ${err}\n`;
          });
          log += '\n';
        }
        
        if (error.httpErrors.length > 0) {
          log += 'HTTP ERRORS:\n';
          error.httpErrors.forEach(err => {
            log += `  - ${err}\n`;
          });
          log += '\n';
        }
        
        if (error.artifacts.length > 0) {
          log += 'ARTIFACTS:\n';
          error.artifacts.forEach(artifact => {
            log += `  - ${artifact}\n`;
          });
          log += '\n';
        }
        
        log += '\n' + '='.repeat(80) + '\n\n';
      });
      
      // Recommendations
      log += '💡 RECOMMENDATIONS\n';
      log += '-'.repeat(40) + '\n';
      recommendations.forEach((rec, index) => {
        log += `${index + 1}. ${rec}\n`;
      });
      log += '\n';
    }
    
    // Footer
    log += '='.repeat(80) + '\n';
    log += 'END OF ERROR LOG\n';
    log += '='.repeat(80) + '\n';
    
    return log;
  }
}

export default UnifiedErrorLogReporter;
