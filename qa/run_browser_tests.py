#!/usr/bin/env python3
"""
Browser Testing Orchestrator for CheckMate Virtue
Runs end-to-end browser tests and captures runtime errors by service/type.
Enhanced to test all buttons and functions on pages.
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

# Import test helpers
try:
    from test_helpers import verify_page_goto_callable, safe_navigate, create_regression_test
except ImportError:
    # Fallback if test_helpers is not available
    def verify_page_goto_callable(page: Page) -> bool:
        if not hasattr(page, 'goto') or not callable(page.goto):
            raise AssertionError(f"Page.goto is not callable. Type: {type(page.goto)}")
        return True
    
    def safe_navigate(page: Page, url: str, timeout=None) -> bool:
        verify_page_goto_callable(page)
        try:
            if timeout:
                page.goto(url, timeout=timeout)
            else:
                page.goto(url)
            return True
        except Exception as e:
            print(f"Navigation failed to {url}: {e}")
            return False
    
    def create_regression_test(page: Page) -> bool:
        from app.config.runtime import BASE_URL
        try:
            verify_page_goto_callable(page)
            if not safe_navigate(page, BASE_URL):
                return False
            page.wait_for_load_state("networkidle", timeout=10000)
            title = page.title()
            if not title:
                print("Warning: Page has no title")
            body = page.locator('body')
            if body.count() == 0:
                print("Error: Body element not found")
                return False
            print(f"✅ Regression test passed: {BASE_URL} loaded successfully")
            return True
        except Exception as e:
            print(f"❌ Regression test failed: {e}")
            return False

# Configuration
from app.config.runtime import BASE_URL
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
TIMEOUT = int(os.getenv("TIMEOUT", "30000"))
RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", "2"))
WAIT_FOR_IDLE = int(os.getenv("WAIT_FOR_IDLE", "2000"))

# Test credentials (from env or defaults)
TEST_USERNAME = os.getenv("TEST_USERNAME", "test@example.com")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "testpass123")

# Test data
TEST_DATA = {
    "vin": "1HGBH41JXMN109186",  # Sample Honda VIN
    "client": {
        "name": "Test Client",
        "company": "Test Company",
        "email": "test@example.com",
        "phone": "555-123-4567",
        "address": "123 Test St, Test City, CA 90210"
    },
    "inspection": {
        "title": "Comprehensive Vehicle Inspection",
        "inspector_name": "John Doe",
        "inspector_id": "INS001",
        "facility_name": "Test Auto Shop",
        "location": "Test Location"
    },
    "invoice": {
        "description": "Vehicle Inspection Service",
        "quantity": 1,
        "unit_price": 150.00,
        "issue_date": "2024-12-01",
        "due_date": "2024-12-31"
    }
}

# Paths
QA_DIR = Path(__file__).parent
LOGS_DIR = QA_DIR / "logs"
SCREENSHOTS_DIR = LOGS_DIR / "screenshots"
ARTIFACTS_DIR = QA_DIR / "artifacts"
HTML_DIR = ARTIFACTS_DIR / "html"
SERVICE_MAP_FILE = QA_DIR / "service_map.json"

# Ensure directories exist
LOGS_DIR.mkdir(exist_ok=True)
SCREENSHOTS_DIR.mkdir(exist_ok=True)
ARTIFACTS_DIR.mkdir(exist_ok=True)
HTML_DIR.mkdir(exist_ok=True)

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
        self.test_inspection_id: Optional[str] = None
        self.test_invoice_id: Optional[str] = None
        
        # Load service mapping
        self._load_service_map()
        
        # Ensure service is healthy before running tests
        self._ensure_service_health()
    
    def _ensure_service_health(self):
        """Ensure the service is healthy before running tests."""
        try:
            from health_check import wait_for_health
            print(f"Checking service health at {BASE_URL}")
            if not wait_for_health(BASE_URL):
                raise RuntimeError(f"Service at {BASE_URL} did not become healthy within timeout")
            print("Service is healthy, proceeding with tests")
        except ImportError:
            print("Warning: health_check module not available, skipping health check")
        except Exception as e:
            print(f"Error during health check: {e}")
            raise
        
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
                  stack_trace: Optional[str] = None, page: Optional[Page] = None):
        """Log an error with metadata and capture artifacts."""
        timestamp = int(time.time())
        
        # Always capture both screenshot and HTML snapshot for every error
        if page:
            try:
                # Capture screenshot
                if not screenshot_path:
                    screenshot_path = f"artifacts/{service}_{error_type}_{timestamp}.png"
                    full_screenshot_path = ARTIFACTS_DIR / f"{service}_{error_type}_{timestamp}.png"
                    page.screenshot(path=str(full_screenshot_path))
                
                # Capture HTML snapshot
                if not html_snapshot:
                    html_snapshot = f"artifacts/html/{service}_{error_type}_{timestamp}.html"
                    full_html_path = HTML_DIR / f"{service}_{error_type}_{timestamp}.html"
                    html_content = page.content()
                    with open(full_html_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                
            except Exception as e:
                print(f"Failed to capture artifacts: {e}")
                # Ensure we have fallback paths even if capture fails
                if not screenshot_path:
                    screenshot_path = f"artifacts/{service}_{error_type}_{timestamp}.png"
                if not html_snapshot:
                    html_snapshot = f"artifacts/html/{service}_{error_type}_{timestamp}.html"
        
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
        if screenshot_path:
            print(f"  Screenshot: {screenshot_path}")
        if html_snapshot:
            print(f"  HTML Snapshot: {html_snapshot}")
    
    def setup_error_handlers(self, page: Page):
        """Setup error handlers for the page."""
        
        # Console errors
        page.on("console", lambda msg: (
            self.log_error("frontend", "JS_ERROR", msg.text, page.url, page=page) 
            if msg.type == "error" else None
        ))
        
        # Page errors (unhandled exceptions)
        page.on("pageerror", lambda exc: 
            self.log_error("frontend", "UNHANDLED_EXCEPTION", str(exc), page.url, 
                          stack_trace=traceback.format_exc(), page=page)
        )
        
        # Failed network requests
        page.on("requestfailed", lambda req: 
            self.log_error(
                self.detect_service_from_url(req.url), 
                "NETWORK_ERROR", 
                f"{req.method} {req.url} → {req.failure().error_text if req.failure() else 'Unknown error'}", 
                page.url, page=page
            )
        )
        
        # Response errors (4xx, 5xx)
        page.on("response", lambda resp: (
            self.log_error(
                self.detect_service_from_url(resp.url),
                "HTTP_ERROR",
                f"{resp.status} {resp.status_text} for {resp.url}",
                page.url, page=page
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
            # Sanity check: verify page.goto is callable
            if not hasattr(page, 'goto') or not callable(page.goto):
                raise AssertionError(f"Page.goto is not callable. Type: {type(page.goto)}")
            
            self.retry_action(lambda: page.goto(url, timeout=TIMEOUT))
            self.wait_for_network_idle(page)
            return True
        except Exception as e:
            self.log_error("navigation", "NAVIGATION_ERROR", 
                          f"Failed to navigate to {url}: {str(e)}", url, page=page)
            return False
    
    def test_all_buttons_and_links(self, page: Page, description: str = ""):
        """Test all clickable elements on the current page."""
        print(f"Testing all buttons and links on {description}")
        
        try:
            # Test all buttons
            buttons = page.locator('button, input[type="button"], input[type="submit"], .btn')
            button_count = buttons.count()
            
            for i in range(button_count):
                try:
                    button = buttons.nth(i)
                    button_text = button.text_content() or button.get_attribute('aria-label') or f"Button {i}"
                    
                    # Skip certain buttons that might cause navigation
                    if any(skip in button_text.lower() for skip in ['logout', 'delete', 'remove']):
                        continue
                    
                    print(f"  Testing button: {button_text}")
                    
                    # Check if button is visible and enabled
                    if button.is_visible() and not button.is_disabled():
                        # Take screenshot before click
                        before_screenshot = SCREENSHOTS_DIR / f"before_click_{i}_{int(time.time())}.png"
                        page.screenshot(path=str(before_screenshot))
                        
                        # Click the button
                        button.click()
                        self.wait_for_network_idle(page)
                        
                        # Take screenshot after click
                        after_screenshot = SCREENSHOTS_DIR / f"after_click_{i}_{int(time.time())}.png"
                        page.screenshot(path=str(after_screenshot))
                        
                        print(f"    ✅ Clicked: {button_text}")
                        
                except Exception as e:
                    print(f"    ❌ Failed to click button {i}: {str(e)}")
                    self.log_error("ui-testing", "BUTTON_CLICK_ERROR", 
                                  f"Failed to click button {i}: {str(e)}", page.url)
            
            # Test all links
            links = page.locator('a[href]')
            link_count = links.count()
            
            for i in range(link_count):
                try:
                    link = links.nth(i)
                    link_text = link.text_content() or link.get_attribute('aria-label') or f"Link {i}"
                    href = link.get_attribute('href')
                    
                    # Skip external links and certain internal links
                    if href and (href.startswith('http') or href.startswith('mailto:') or href.startswith('tel:')):
                        continue
                    
                    print(f"  Testing link: {link_text} -> {href}")
                    
                    if link.is_visible():
                        # Store current URL
                        current_url = page.url
                        
                        # Click the link
                        link.click()
                        self.wait_for_network_idle(page)
                        
                        # Check if navigation occurred
                        if page.url != current_url:
                            print(f"    ✅ Navigated: {link_text}")
                            # Go back to test more links
                            page.go_back()
                            self.wait_for_network_idle(page)
                        else:
                            print(f"    ⚠️ No navigation: {link_text}")
                            
                except Exception as e:
                    print(f"    ❌ Failed to click link {i}: {str(e)}")
                    self.log_error("ui-testing", "LINK_CLICK_ERROR", 
                                  f"Failed to click link {i}: {str(e)}", page.url)
                    
        except Exception as e:
            self.log_error("ui-testing", "UI_TEST_ERROR", 
                          f"Failed to test UI elements: {str(e)}", page.url)
    
    def test_form_interactions(self, page: Page, description: str = ""):
        """Test form interactions on the current page."""
        print(f"Testing form interactions on {description}")
        
        try:
            # Test all input fields
            inputs = page.locator('input, textarea, select')
            input_count = inputs.count()
            
            for i in range(input_count):
                try:
                    input_element = inputs.nth(i)
                    input_type = input_element.get_attribute('type') or 'text'
                    input_name = input_element.get_attribute('name') or input_element.get_attribute('id') or f"input_{i}"
                    
                    print(f"  Testing input: {input_name} ({input_type})")
                    
                    if input_element.is_visible() and not input_element.is_disabled():
                        # Fill with appropriate test data
                        if input_type in ['text', 'email', 'url']:
                            if 'vin' in input_name.lower():
                                input_element.fill(TEST_DATA['vin'])
                            elif 'email' in input_name.lower():
                                input_element.fill(TEST_DATA['client']['email'])
                            elif 'phone' in input_name.lower():
                                input_element.fill(TEST_DATA['client']['phone'])
                            elif 'name' in input_name.lower():
                                input_element.fill(TEST_DATA['client']['name'])
                            else:
                                input_element.fill(f"Test {input_name}")
                        elif input_type == 'number':
                            input_element.fill('100')
                        elif input_type == 'date':
                            input_element.fill('2024-12-01')
                        elif input_type == 'file':
                            # Skip file inputs for now
                            continue
                        
                        print(f"    ✅ Filled: {input_name}")
                        
                except Exception as e:
                    print(f"    ❌ Failed to fill input {i}: {str(e)}")
                    self.log_error("ui-testing", "INPUT_FILL_ERROR", 
                                  f"Failed to fill input {i}: {str(e)}", page.url)
            
            # Test select dropdowns
            selects = page.locator('select')
            select_count = selects.count()
            
            for i in range(select_count):
                try:
                    select_element = selects.nth(i)
                    select_name = select_element.get_attribute('name') or select_element.get_attribute('id') or f"select_{i}"
                    
                    print(f"  Testing select: {select_name}")
                    
                    if select_element.is_visible() and not select_element.is_disabled():
                        # Get all options
                        options = select_element.locator('option')
                        option_count = options.count()
                        
                        if option_count > 1:
                            # Select the second option (skip the first if it's a placeholder)
                            select_element.select_option(index=1)
                            print(f"    ✅ Selected option in: {select_name}")
                        
                except Exception as e:
                    print(f"    ❌ Failed to select option {i}: {str(e)}")
                    self.log_error("ui-testing", "SELECT_ERROR", 
                                  f"Failed to select option {i}: {str(e)}", page.url)
                    
        except Exception as e:
            self.log_error("ui-testing", "FORM_TEST_ERROR", 
                          f"Failed to test form interactions: {str(e)}", page.url)
    
    def test_inspection_form_comprehensive(self, page: Page):
        """Comprehensive test of the inspection form."""
        print("\n=== Testing Inspection Form Comprehensive ===")
        
        if not self.navigate_to_page(page, f"{BASE_URL}/inspection/form", "Inspection form"):
            return
        
        try:
            # Test VIN decoding
            print("Testing VIN decoding...")
            vin_input = page.locator('#vin')
            if vin_input.count() > 0:
                vin_input.first.fill(TEST_DATA['vin'])
                
                decode_button = page.locator('#decode-vin')
                if decode_button.count() > 0:
                    decode_button.first.click()
                    self.wait_for_network_idle(page)
                    print("  ✅ VIN decode button clicked")
            
            # Test form interactions
            self.test_form_interactions(page, "inspection form")
            
            # Test step navigation
            step_buttons = page.locator('#steps-nav button')
            step_count = step_buttons.count()
            
            for i in range(step_count):
                try:
                    step_button = step_buttons.nth(i)
                    step_text = step_button.text_content()
                    print(f"Testing step: {step_text}")
                    
                    step_button.click()
                    self.wait_for_network_idle(page)
                    print(f"  ✅ Navigated to step: {step_text}")
                    
                    # Test form elements in this step
                    self.test_form_interactions(page, f"step {step_text}")
                    
                except Exception as e:
                    print(f"  ❌ Failed to navigate to step {i}: {str(e)}")
            
            # Test save inspection
            save_button = page.locator('#save-inspection')
            if save_button.count() > 0:
                save_button.first.click()
                self.wait_for_network_idle(page)
                print("  ✅ Save inspection button clicked")
                
                # Check if we got an inspection ID
                try:
                    # Look for any response that might contain an inspection ID
                    response = page.wait_for_response(lambda r: '/api/inspections' in r.url, timeout=5000)
                    if response.status == 200:
                        response_data = response.json()
                        if 'inspection_id' in response_data:
                            self.test_inspection_id = response_data['inspection_id']
                            print(f"  ✅ Created inspection: {self.test_inspection_id}")
                except:
                    print("  ⚠️ No inspection creation response detected")
            
        except Exception as e:
            self.log_error("inspection-service", "INSPECTION_FORM_ERROR", 
                          f"Inspection form test failed: {str(e)}", page.url)
    
    def test_invoice_form_comprehensive(self, page: Page):
        """Comprehensive test of the invoice form."""
        print("\n=== Testing Invoice Form Comprehensive ===")
        
        if not self.navigate_to_page(page, f"{BASE_URL}/invoices/new", "New invoice form"):
            return
        
        try:
            # Test form interactions
            self.test_form_interactions(page, "invoice form")
            
            # Test adding invoice items
            add_item_buttons = page.locator('button:has-text("Add Item"), button:has-text("Add Line Item")')
            if add_item_buttons.count() > 0:
                add_item_buttons.first.click()
                self.wait_for_network_idle(page)
                print("  ✅ Add item button clicked")
                
                # Fill in the new item
                self.test_form_interactions(page, "new invoice item")
            
            # Test save invoice
            save_buttons = page.locator('button:has-text("Save"), button:has-text("Create Invoice")')
            if save_buttons.count() > 0:
                save_buttons.first.click()
                self.wait_for_network_idle(page)
                print("  ✅ Save invoice button clicked")
                
                # Check if we got an invoice ID
                try:
                    response = page.wait_for_response(lambda r: '/invoices/api' in r.url, timeout=5000)
                    if response.status == 200:
                        response_data = response.json()
                        if 'invoice_id' in response_data:
                            self.test_invoice_id = response_data['invoice_id']
                            print(f"  ✅ Created invoice: {self.test_invoice_id}")
                except:
                    print("  ⚠️ No invoice creation response detected")
            
        except Exception as e:
            self.log_error("invoice-service", "INVOICE_FORM_ERROR", 
                          f"Invoice form test failed: {str(e)}", page.url)
    
    def test_public_routes(self, page: Page):
        """Test all public routes with comprehensive UI testing."""
        print("\n=== Testing Public Routes ===")
        
        # Home page
        if self.navigate_to_page(page, f"{BASE_URL}/", "Home page"):
            self.test_all_buttons_and_links(page, "home page")
        
        # Test automotive inspection form
        if self.navigate_to_page(page, f"{BASE_URL}/inspection/form", "Automotive inspection form"):
            self.test_inspection_form_comprehensive(page)
        
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
        if self.navigate_to_page(page, f"{BASE_URL}/inspections", "Inspections list"):
            self.test_all_buttons_and_links(page, "inspections list")
        
        # New inspection form
        if self.navigate_to_page(page, f"{BASE_URL}/inspections/new", "New inspection form"):
            self.test_form_interactions(page, "new inspection form")
            self.test_all_buttons_and_links(page, "new inspection form")
        
        # Invoice routes
        if self.navigate_to_page(page, f"{BASE_URL}/invoices", "Invoices list"):
            self.test_all_buttons_and_links(page, "invoices list")
        
        if self.navigate_to_page(page, f"{BASE_URL}/invoices/new", "New invoice form"):
            self.test_invoice_form_comprehensive(page)
        
        if self.navigate_to_page(page, f"{BASE_URL}/invoices/clients", "Clients list"):
            self.test_all_buttons_and_links(page, "clients list")
        
        if self.navigate_to_page(page, f"{BASE_URL}/invoices/clients/new", "New client form"):
            self.test_form_interactions(page, "new client form")
            self.test_all_buttons_and_links(page, "new client form")
        
        # VIN decoder test pages
        if self.navigate_to_page(page, f"{BASE_URL}/test-vin", "VIN decoder test"):
            self.test_form_interactions(page, "VIN decoder test")
            self.test_all_buttons_and_links(page, "VIN decoder test")
        
        if self.navigate_to_page(page, f"{BASE_URL}/test-vin-simple", "Simple VIN decoder test"):
            self.test_form_interactions(page, "simple VIN decoder test")
            self.test_all_buttons_and_links(page, "simple VIN decoder test")
        
        # Test VIN decoder API
        test_vin = TEST_DATA['vin']
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
                
                # Test form interactions on login page
                self.test_form_interactions(page, "login page")
                
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
        if self.navigate_to_page(page, f"{BASE_URL}/inspections/new", "Authenticated new inspection"):
            self.test_form_interactions(page, "authenticated new inspection")
            self.test_all_buttons_and_links(page, "authenticated new inspection")
        
        # Test creating a new invoice
        if self.navigate_to_page(page, f"{BASE_URL}/invoices/new", "Authenticated new invoice"):
            self.test_invoice_form_comprehensive(page)
        
        # Test viewing existing inspections (if any exist)
        if self.navigate_to_page(page, f"{BASE_URL}/inspections", "Authenticated inspections list"):
            self.test_all_buttons_and_links(page, "authenticated inspections list")
    
    def test_form_submissions(self, page: Page):
        """Test form submissions and API calls."""
        print("\n=== Testing Form Submissions ===")
        
        # Test inspection creation API
        test_inspection_data = {
            "title": TEST_DATA['inspection']['title'],
            "industry_info": {
                "industry_type": "automotive",
                "facility_name": TEST_DATA['inspection']['facility_name'],
                "location": TEST_DATA['inspection']['location']
            },
            "inspector_name": TEST_DATA['inspection']['inspector_name'],
            "inspector_id": TEST_DATA['inspection']['inspector_id'],
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
            else:
                print("  ✅ Inspection creation API test passed")
        except Exception as e:
            self.log_error("inspection-service", "API_ERROR", 
                          f"Inspection creation API exception: {str(e)}", 
                          f"{BASE_URL}/api/inspections")
        
        # Test invoice creation API
        test_invoice_data = {
            "client_id": "test_client_001",
            "industry_type": "automotive",
            "issue_date": TEST_DATA['invoice']['issue_date'],
            "due_date": TEST_DATA['invoice']['due_date'],
            "items": [
                {
                    "description": TEST_DATA['invoice']['description'],
                    "quantity": TEST_DATA['invoice']['quantity'],
                    "unit_price": TEST_DATA['invoice']['unit_price'],
                    "item_type": "service"
                }
            ]
        }
        
        try:
            # Test canonical endpoint first
            response = page.request.post(
                f"{BASE_URL}/api/invoices",
                data=json.dumps(test_invoice_data),
                headers={"Content-Type": "application/json"}
            )
            if response.status >= 400:
                self.log_error("invoice-service", "API_ERROR", 
                              f"Canonical invoice creation API failed: {response.status}", 
                              f"{BASE_URL}/api/invoices")
            else:
                print("  ✅ Canonical invoice creation API test passed")
                
            # Test backward compatibility endpoint
            response = page.request.post(
                f"{BASE_URL}/invoices/api/invoices",
                data=json.dumps(test_invoice_data),
                headers={"Content-Type": "application/json"}
            )
            if response.status >= 400:
                self.log_error("invoice-service", "API_ERROR", 
                              f"Backward compatibility invoice creation API failed: {response.status}", 
                              f"{BASE_URL}/invoices/api/invoices")
            else:
                print("  ✅ Backward compatibility invoice creation API test passed")
        except Exception as e:
            self.log_error("invoice-service", "API_ERROR", 
                          f"Invoice creation API exception: {str(e)}", 
                          f"{BASE_URL}/api/invoices")
    
    def test_existing_data_interactions(self, page: Page):
        """Test interactions with existing data."""
        print("\n=== Testing Existing Data Interactions ===")
        
        # Test viewing existing inspections
        if self.navigate_to_page(page, f"{BASE_URL}/inspections", "Inspections list"):
            # Look for inspection links to click
            inspection_links = page.locator('a[href*="/inspections/"]')
            if inspection_links.count() > 0:
                first_inspection = inspection_links.first
                inspection_url = first_inspection.get_attribute('href')
                print(f"Testing existing inspection: {inspection_url}")
                
                first_inspection.click()
                self.wait_for_network_idle(page)
                
                # Test all buttons and links on the inspection view page
                self.test_all_buttons_and_links(page, "inspection view page")
                self.test_form_interactions(page, "inspection view page")
        
        # Test viewing existing invoices
        if self.navigate_to_page(page, f"{BASE_URL}/invoices", "Invoices list"):
            # Look for invoice links to click
            invoice_links = page.locator('a[href*="/invoices/"]')
            if invoice_links.count() > 0:
                first_invoice = invoice_links.first
                invoice_url = first_invoice.get_attribute('href')
                print(f"Testing existing invoice: {invoice_url}")
                
                first_invoice.click()
                self.wait_for_network_idle(page)
                
                # Test all buttons and links on the invoice view page
                self.test_all_buttons_and_links(page, "invoice view page")
                self.test_form_interactions(page, "invoice view page")
    
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
                        if error.get('html_snapshot'):
                            f.write(f"          HTML Snapshot: {error['html_snapshot']}\n")
                        f.write("\n")
                f.write("\n")
        
        print(f"\nError logs saved to:")
        print(f"  JSON: {json_file}")
        print(f"  Text: {txt_file}")
        print(f"  Artifacts directory: {ARTIFACTS_DIR}")
        print(f"  Screenshots: {SCREENSHOTS_DIR}")
        print(f"  HTML snapshots: {HTML_DIR}")
    
    def run_tests(self):
        """Run all browser tests."""
        print("Starting CheckMate Virtue Browser Tests")
        print(f"Base URL: {BASE_URL}")
        print(f"Headless: {HEADLESS}")
        print(f"Timeout: {TIMEOUT}ms")
        print(f"Test Data: {json.dumps(TEST_DATA, indent=2)}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=HEADLESS)
            context = browser.new_context()
            page = context.new_page()
            
            # Setup error handlers
            self.setup_error_handlers(page)
            
            try:
                # Run regression test first to verify basic functionality
                print("\n=== Running Regression Test ===")
                if not create_regression_test(page):
                    self.log_error("regression", "REGRESSION_FAILED", 
                                  "Basic regression test failed", BASE_URL, page=page)
                
                # Test public routes with comprehensive UI testing
                self.test_public_routes(page)
                
                # Test authenticated routes
                self.test_authenticated_routes(page)
                
                # Test form submissions
                self.test_form_submissions(page)
                
                # Test interactions with existing data
                self.test_existing_data_interactions(page)
                
            except Exception as e:
                self.log_error("test-runner", "TEST_ERROR", 
                              f"Test execution failed: {str(e)}", page.url,
                              stack_trace=traceback.format_exc(), page=page)
            
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
        
        # Generate artifact report
        try:
            from test_artifact_helpers import create_artifact_report, save_artifact_report
            test_names = ["browser_test_runner"]  # Main test runner
            report = create_artifact_report(test_names)
            print("\n" + report)
            
            # Save report to file
            report_path = save_artifact_report(test_names)
            print(f"Artifact report saved to: {report_path}")
        except ImportError:
            print("Warning: test_artifact_helpers not available, skipping artifact report")
        
        # Print summary
        print(f"\n=== Test Summary ===")
        print(f"Total errors captured: {len(self.errors)}")
        print(f"Test inspection ID: {self.test_inspection_id}")
        print(f"Test invoice ID: {self.test_invoice_id}")
        
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
