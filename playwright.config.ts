import { defineConfig, devices } from '@playwright/test';

/**
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './tests/e2e',
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: [
    ['list'],
    ['html', { open: 'never' }],
    ['junit', { outputFile: 'artifacts/junit.xml' }],
    ['./playwright-reporters/custom-dump-reporter.ts'],
    ['./playwright-reporters/unified-error-log-reporter.ts']
  ],
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: process.env.E2E_BASE_URL || process.env.FRONTEND_URL || 'http://127.0.0.1:8000',

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'retain-on-failure',
    
    /* Record video only when retrying a test for the first time. */
    video: 'retain-on-failure',
    
    /* Take screenshot only when retrying a test for the first time. */
    screenshot: 'only-on-failure',
    
    /* Viewport size */
    viewport: { width: 1440, height: 900 },
    
    /* Context options */
    contextOptions: {
      recordHar: { 
        path: 'artifacts/e2e/har/fe-be.har', 
        content: 'embed' 
      }
    },
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
