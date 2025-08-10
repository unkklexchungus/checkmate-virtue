# CheckMate Virtue Browser Testing Suite

This directory contains a comprehensive browser testing system for the CheckMate Virtue application using Playwright.

## Features

- **End-to-end browser testing** of all public and authenticated routes
- **Error logging by service and type** (JS errors, network errors, HTTP errors, etc.)
- **Automatic screenshot capture** for first error per page
- **Service detection** from API request URLs
- **Retry logic** with exponential backoff
- **Comprehensive reporting** in JSON and human-readable formats

## Quick Start

### 1. Install Dependencies

```bash
# Install Playwright and browsers
pip install playwright
playwright install

# Or use the convenience script
npm run install-deps
```

### 2. Start the Application

```bash
# Start the CheckMate Virtue application
python3 main.py
```

### 3. Run Tests

```bash
# Run tests headless (default)
python qa/run_browser_tests.py

# Run tests with visible browser
HEADLESS=false python qa/run_browser_tests.py

# Run with longer timeout for debugging
HEADLESS=false TIMEOUT=60000 python qa/run_browser_tests.py
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BASE_URL` | `http://localhost:8080` | Base URL of the application |
| `HEADLESS` | `true` | Run browser in headless mode |
| `TIMEOUT` | `30000` | Page navigation timeout (ms) |
| `RETRY_ATTEMPTS` | `2` | Number of retry attempts for failed actions |
| `WAIT_FOR_IDLE` | `2000` | Wait time for network idle (ms) |
| `TEST_USERNAME` | `test@example.com` | Test username for authentication |
| `TEST_PASSWORD` | `testpass123` | Test password for authentication |

### Service Mapping

The `service_map.json` file maps URL patterns to service names for error categorization:

```json
{
  "api/industries": "inspection-service",
  "api/inspections": "inspection-service",
  "api/vehicle": "vehicle-service",
  "api/invoices": "invoice-service"
}
```

## Test Coverage

### Public Routes Tested

- Home page (`/`)
- Industries listing (`/industries`)
- Industry-specific inspection forms (`/industries/{industry}/new`)
- Inspections list (`/inspections`)
- New inspection form (`/inspections/new`)
- Invoice routes (`/invoices/*`)
- VIN decoder test pages (`/test-vin`, `/test-vin-simple`)

### API Endpoints Tested

- Industry templates (`/api/industries/{industry}/template`)
- Inspection creation (`/api/inspections`)
- VIN decoding (`/vehicle/decode/{vin}`)
- Invoice creation (`/api/invoices`)

### Error Types Captured

- **JS_ERROR**: JavaScript console errors
- **UNHANDLED_EXCEPTION**: Unhandled JavaScript exceptions
- **NETWORK_ERROR**: Failed network requests
- **HTTP_ERROR**: HTTP 4xx/5xx responses
- **NAVIGATION_ERROR**: Page navigation failures
- **API_ERROR**: API endpoint failures
- **LOGIN_ERROR**: Authentication failures

## Output Files

### Error Logs

- `qa/logs/error-log.json` - Structured JSON format
- `qa/logs/error-log.txt` - Human-readable format

### Screenshots

- `qa/logs/screenshots/` - Screenshots of first error per page
- `qa/logs/screenshots/final_state_*.png` - Final application state

### Example Output

```
SERVICE: inspection-service
    TYPE: API_ERROR
        - Industry template API failed: 404
          URL: http://localhost:8080/api/industries/automotive/template
          Time: 2024-01-15T10:30:45.123456

SERVICE: vehicle-service
    TYPE: NETWORK_ERROR
        - GET http://localhost:8080/vehicle/decode/1HGBH41JXMN109186 → net::ERR_CONNECTION_REFUSED
          URL: http://localhost:8080/test-vin
          Time: 2024-01-15T10:30:46.789012
```

## Advanced Usage

### Custom Test Scenarios

You can extend the testing by modifying `run_browser_tests.py`:

```python
def test_custom_scenario(self, page: Page):
    """Add your custom test scenario here."""
    self.navigate_to_page(page, f"{BASE_URL}/custom-route")
    # Add your test logic
```

### Adding New Services

1. Update `service_map.json` with new URL patterns
2. Add corresponding test methods in `BrowserTestRunner`
3. Update error handling if needed

### Continuous Integration

```yaml
# Example GitHub Actions workflow
- name: Run Browser Tests
  run: |
    pip install playwright
    playwright install
    python qa/run_browser_tests.py
  env:
    BASE_URL: ${{ secrets.APP_URL }}
    HEADLESS: true
```

## Troubleshooting

### Common Issues

1. **Browser not launching**: Ensure Playwright browsers are installed
2. **Connection refused**: Check if the application is running on the correct port
3. **Timeout errors**: Increase `TIMEOUT` environment variable
4. **Missing screenshots**: Check write permissions for `qa/logs/screenshots/`

### Debug Mode

For debugging, run with visible browser and longer timeouts:

```bash
HEADLESS=false TIMEOUT=60000 python qa/run_browser_tests.py
```

### Manual Browser Testing

You can also use Playwright's built-in tools:

```bash
# Install Playwright browsers
playwright install

# Launch browser manually
playwright open http://localhost:8080
```

## Contributing

When adding new routes or services:

1. Update `service_map.json` with new URL patterns
2. Add corresponding test methods
3. Update this README with new test coverage
4. Ensure error handling covers new scenarios

## License

MIT License - see main project license for details.
