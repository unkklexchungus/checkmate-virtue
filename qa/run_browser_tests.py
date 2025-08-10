#!/usr/bin/env python3
"""
Browser Testing Orchestrator for CheckMate Virtue
Runs end-to-end browser tests and captures runtime errors by service/type.
"""

import json
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from urllib.parse import urlparse

try:
    from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
except ImportError:
    print("Playwright not installed. Installing...")
    os.system("pip install playwright")
    os.system("playwright install")
    from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext

# Configuration
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
TIMEOUT = int(os.getenv("TIMEOUT", "30000"))
RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", "2"))
WAIT_FOR_IDLE = int(os.getenv("WAIT_FOR_IDLE", "2000"))

# Test credentials (from env or defaults)
TEST_USERNAME = os.getenv("TEST_USERNAME", "test@example.com")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "testpass123")

# Paths
QA_DIR = Path(__file__).parent
LOGS_DIR = QA_DIR / "logs"
SCREENSHOTS_DIR = LOGS_DIR / "screenshots"
SERVICE_MAP_FILE = QA_DIR / "service_map.json"

# Ensure directories exist
LOGS_DIR.mkdir(exist_ok=True)
SCREENSHOTS_DIR.mkdir(exist_ok=True)

@dataclass
class ErrorLog:
    """Error log entry."""
    service: str
    error_type: str
    message: str
    url: str
    timestamp: str
    screenshot_path: Optional[str] = None
    html_snapshot: Optional[str] = None
    stack_trace: Optional[str] = None

class BrowserTestRunner:
    """Main browser test runner class."""
    
    def __init__(self):
        self.errors: List[ErrorLog] = []
        self.service_map: Dict[str, str] = {}
        self.current_page: Optional[str] = None
        self.first_error_per_page: Dict[str, bool] = {}
        
        # Load service mapping
        self._load_service_map()
        
    def _load_service_map(self):
        """Load service mapping from JSON file."""
        try:
            with open(SERVICE_MAP_FILE, 'r') as f:
                self.service_map = json.load(f)
        except FileNotFoundError:
            print(f"Warning: Service map file not found at {SERVICE_MAP_FILE}")
            self.service_map = {}
    
    def detect_service_from_url(self, url: str) -> str:
        """Detect service name from URL."""
        parsed = urlparse(url)
        path = parsed.path.lstrip('/')
        
        for pattern, service in self.service_map.items():
            if pattern in path:
                return service
        
        # Fallback detection based on path segments
        if path.startswith('api/'):
            segments = path.split('/')
            if len(segments) > 1:
                return f"{segments[1]}-service"
        
        return "unknown-service"
    
    def log_error(self, service: str, error_type: str, message: str, url: str = "", 
                  screenshot_path: Optional[str] = None, html_snapshot: Optional[str] = None,
                  stack_trace: Optional[str] = None):
        """Log an error with metadata."""
        # Only take screenshot for first error per page
        if self.current_page and self.current_page not in self.first_error_per_page:
            self.first_error_per_page[self.current_page] = True
            if not screenshot_path:
                screenshot_path = f"screenshots/error_{service}_{error_type}_{int(time.time())}.png"
        
        error = ErrorLog(
            service=service,
            error_type=error_type,
            message=message,
            url=url,
            timestamp=datetime.now().isoformat(),
            screenshot_path=screenshot_path,
            html_snapshot=html_snapshot,
            stack_trace=stack_trace
        )
        
        self.errors.append(error)
        print(f"ERROR [{service}] {error_type}: {message}")
    
    def setup_error_handlers(self, page: Page):
        """Setup error handlers for the page."""
        
        # Console errors
        page.on("console", lambda msg: (
            self.log_error("frontend", "JS_ERROR", msg.text, page.url) 
            if msg.type == "error" else None
        ))
        
        # Page errors (unhandled exceptions)
        page.on("pageerror", lambda exc: 
            self.log_error("frontend", "UNHANDLED_EXCEPTION", str(exc), page.url, 
                          stack_trace=traceback.format_exc())
        )
        
        # Failed network requests
        page.on("requestfailed", lambda req: 
            self.log_error(
                self.detect_service_from_url(req.url), 
                "NETWORK_ERROR", 
                f"{req.method} {req.url} → {req.failure().error_text if req.failure() else 'Unknown error'}", 
                page.url
            )
        )
        
        # Response errors (4xx, 5xx)
        page.on("response", lambda resp: (
            self.log_error(
                self.detect_service_from_url(resp.url),
                "HTTP_ERROR",
                f"{resp.status} {resp.status_text} for {resp.url}",
                page.url
            ) if resp.status >= 400 else None
        ))
    
    def wait_for_network_idle(self, page: Page, timeout: int = WAIT_FOR_IDLE):
        """Wait for network to be idle."""
        try:
            page.wait_for_load_state("networkidle", timeout=timeout)
        except:
            # If network idle doesn't happen, just wait a bit
            page.wait_for_timeout(1000)
    
    def retry_action(self, action, max_attempts: int = RETRY_ATTEMPTS):
        """Retry an action with exponential backoff."""
        for attempt in range(max_attempts):
            try:
                return action()
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise e
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def navigate_to_page(self, page: Page, url: str, description: str = ""):
        """Navigate to a page with error handling."""
        self.current_page = url
        print(f"Navigating to: {url} {description}")
        
        try:
            self.retry_action(lambda: page.goto(url, timeout=TIMEOUT))
            self.wait_for_network_idle(page)
            return True
        except Exception as e:
            self.log_error("navigation", "NAVIGATION_ERROR", 
                          f"Failed to navigate to {url}: {str(e)}", url)
            return False
    
    def test_public_routes(self, page: Page):
        """Test all public routes."""
        print("\n=== Testing Public Routes ===")
        
        # Home page
        self.navigate_to_page(page, f"{BASE_URL}/", "Home page")
        
        # Test automotive inspection form
        self.navigate_to_page(page, f"{BASE_URL}/inspection/form", "Automotive inspection form")
        
        # Test automotive template API
        try:
            response = page.request.get(f"{BASE_URL}/api/inspection-template")
            if response.status >= 400:
                self.log_error("inspection-service", "API_ERROR", 
                              f"Automotive template API failed: {response.status}", 
                              f"{BASE_URL}/api/inspection-template")
        except Exception as e:
            self.log_error("inspection-service", "API_ERROR", 
                          f"Automotive template API exception: {str(e)}", 
                          f"{BASE_URL}/api/inspection-template")
        
        # Inspections list
        self.navigate_to_page(page, f"{BASE_URL}/inspections", "Inspections list")
        
        # New inspection form
        self.navigate_to_page(page, f"{BASE_URL}/inspections/new", "New inspection form")
        
        # Invoice routes
        self.navigate_to_page(page, f"{BASE_URL}/invoices", "Invoices list")
        self.navigate_to_page(page, f"{BASE_URL}/invoices/new", "New invoice form")
        self.navigate_to_page(page, f"{BASE_URL}/invoices/clients", "Clients list")
        self.navigate_to_page(page, f"{BASE_URL}/invoices/clients/new", "New client form")
        
        # VIN decoder test pages
        self.navigate_to_page(page, f"{BASE_URL}/test-vin", "VIN decoder test")
        self.navigate_to_page(page, f"{BASE_URL}/test-vin-simple", "Simple VIN decoder test")
        
        # Test VIN decoder API
        test_vin = "1HGBH41JXMN109186"  # Sample VIN
        try:
            response = page.request.get(f"{BASE_URL}/vehicle/decode/{test_vin}")
            if response.status >= 400:
                self.log_error("vehicle-service", "API_ERROR", 
                              f"VIN decoder API failed: {response.status}", 
                              f"{BASE_URL}/vehicle/decode/{test_vin}")
        except Exception as e:
            self.log_error("vehicle-service", "API_ERROR", 
                          f"VIN decoder API exception: {str(e)}", 
                          f"{BASE_URL}/vehicle/decode/{test_vin}")
    
    def test_authenticated_routes(self, page: Page):
        """Test authenticated routes (if login is available)."""
        print("\n=== Testing Authenticated Routes ===")
        
        # Try to login if login page exists
        login_url = f"{BASE_URL}/login"
        try:
            response = page.request.get(login_url)
            if response.status == 200:
                self.navigate_to_page(page, login_url, "Login page")
                
                # Try to fill login form
                try:
                    username_field = page.locator('input[name="username"], input[name="email"], input[type="email"]')
                    password_field = page.locator('input[name="password"], input[type="password"]')
                    
                    if username_field.count() > 0 and password_field.count() > 0:
                        username_field.first.fill(TEST_USERNAME)
                        password_field.first.fill(TEST_PASSWORD)
                        
                        # Try to submit
                        submit_button = page.locator('button[type="submit"], input[type="submit"]')
                        if submit_button.count() > 0:
                            submit_button.first.click()
                            self.wait_for_network_idle(page)
                            
                            # Test authenticated routes after login
                            self.test_authenticated_flows(page)
                except Exception as e:
                    self.log_error("auth-service", "LOGIN_ERROR", 
                                  f"Login form interaction failed: {str(e)}", login_url)
        except Exception as e:
            print(f"Login page not available or error: {str(e)}")
    
    def test_authenticated_flows(self, page: Page):
        """Test flows that require authentication."""
        # Test creating a new inspection
        self.navigate_to_page(page, f"{BASE_URL}/inspections/new", "Authenticated new inspection")
        
        # Test creating a new invoice
        self.navigate_to_page(page, f"{BASE_URL}/invoices/new", "Authenticated new invoice")
        
        # Test viewing existing inspections (if any exist)
        self.navigate_to_page(page, f"{BASE_URL}/inspections", "Authenticated inspections list")
    
    def test_form_submissions(self, page: Page):
        """Test form submissions and API calls."""
        print("\n=== Testing Form Submissions ===")
        
        # Test inspection creation API
        test_inspection_data = {
            "title": "Test Inspection",
            "industry_info": {
                "industry_type": "automotive",
                "facility_name": "Test Facility",
                "location": "Test Location"
            },
            "inspector_name": "Test Inspector",
            "inspector_id": "TEST001",
            "industry_type": "automotive"
        }
        
        try:
            response = page.request.post(
                f"{BASE_URL}/api/inspections",
                data=json.dumps(test_inspection_data),
                headers={"Content-Type": "application/json"}
            )
            if response.status >= 400:
                self.log_error("inspection-service", "API_ERROR", 
                              f"Inspection creation API failed: {response.status}", 
                              f"{BASE_URL}/api/inspections")
        except Exception as e:
            self.log_error("inspection-service", "API_ERROR", 
                          f"Inspection creation API exception: {str(e)}", 
                          f"{BASE_URL}/api/inspections")
        
        # Test invoice creation API
        test_invoice_data = {
            "client_id": "test_client_001",
            "industry_type": "automotive",
            "issue_date": "2024-12-01",
            "due_date": "2024-12-31",
            "items": [
                {
                    "description": "Test Item",
                    "quantity": 1,
                    "unit_price": 100,
                    "item_type": "service"
                }
            ]
        }
        
        try:
            response = page.request.post(
                f"{BASE_URL}/invoices/api/invoices",
                data=json.dumps(test_invoice_data),
                headers={"Content-Type": "application/json"}
            )
            if response.status >= 400:
                self.log_error("invoice-service", "API_ERROR", 
                              f"Invoice creation API failed: {response.status}", 
                              f"{BASE_URL}/invoices/api/invoices")
        except Exception as e:
            self.log_error("invoice-service", "API_ERROR", 
                          f"Invoice creation API exception: {str(e)}", 
                          f"{BASE_URL}/invoices/api/invoices")
    
    def save_error_logs(self):
        """Save error logs to files."""
        # Group errors by service and type
        grouped_errors = {}
        for error in self.errors:
            if error.service not in grouped_errors:
                grouped_errors[error.service] = {}
            if error.error_type not in grouped_errors[error.service]:
                grouped_errors[error.service][error.error_type] = []
            grouped_errors[error.service][error.error_type].append({
                "message": error.message,
                "url": error.url,
                "timestamp": error.timestamp,
                "screenshot_path": error.screenshot_path,
                "html_snapshot": error.html_snapshot,
                "stack_trace": error.stack_trace
            })
        
        # Save JSON format
        json_file = LOGS_DIR / "error-log.json"
        with open(json_file, 'w') as f:
            json.dump(grouped_errors, f, indent=2, default=str)
        
        # Save human-readable format
        txt_file = LOGS_DIR / "error-log.txt"
        with open(txt_file, 'w') as f:
            f.write(f"CheckMate Virtue Browser Test Error Log\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Total Errors: {len(self.errors)}\n")
            f.write("=" * 80 + "\n\n")
            
            for service, types in grouped_errors.items():
                f.write(f"SERVICE: {service}\n")
                for error_type, errors in types.items():
                    f.write(f"    TYPE: {error_type}\n")
                    for error in errors:
                        f.write(f"        - {error['message']}\n")
                        f.write(f"          URL: {error['url']}\n")
                        f.write(f"          Time: {error['timestamp']}\n")
                        if error.get('screenshot_path'):
                            f.write(f"          Screenshot: {error['screenshot_path']}\n")
                        f.write("\n")
                f.write("\n")
        
        print(f"\nError logs saved to:")
        print(f"  JSON: {json_file}")
        print(f"  Text: {txt_file}")
    
    def run_tests(self):
        """Run all browser tests."""
        print("Starting CheckMate Virtue Browser Tests")
        print(f"Base URL: {BASE_URL}")
        print(f"Headless: {HEADLESS}")
        print(f"Timeout: {TIMEOUT}ms")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=HEADLESS)
            context = browser.new_context()
            page = context.new_page()
            
            # Setup error handlers
            self.setup_error_handlers(page)
            
            try:
                # Test public routes
                self.test_public_routes(page)
                
                # Test authenticated routes
                self.test_authenticated_routes(page)
                
                # Test form submissions
                self.test_form_submissions(page)
                
            except Exception as e:
                self.log_error("test-runner", "TEST_ERROR", 
                              f"Test execution failed: {str(e)}", page.url,
                              stack_trace=traceback.format_exc())
            
            finally:
                # Take final screenshot
                try:
                    screenshot_path = SCREENSHOTS_DIR / f"final_state_{int(time.time())}.png"
                    page.screenshot(path=str(screenshot_path))
                    print(f"Final screenshot saved: {screenshot_path}")
                except Exception as e:
                    print(f"Failed to take final screenshot: {e}")
                
                browser.close()
        
        # Save error logs
        self.save_error_logs()
        
        # Print summary
        print(f"\n=== Test Summary ===")
        print(f"Total errors captured: {len(self.errors)}")
        
        if self.errors:
            print("\nErrors by service:")
            service_counts = {}
            for error in self.errors:
                service_counts[error.service] = service_counts.get(error.service, 0) + 1
            
            for service, count in sorted(service_counts.items()):
                print(f"  {service}: {count} errors")
        
        return len(self.errors) == 0

def main():
    """Main entry point."""
    try:
        runner = BrowserTestRunner()
        success = runner.run_tests()
        
        if success:
            print("\n✅ All tests completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Tests completed with errors. Check logs for details.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
