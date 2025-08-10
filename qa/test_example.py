#!/usr/bin/env python3
"""
Example test script demonstrating the browser testing system.
This shows how to create custom test scenarios.
"""

import os
import sys
from pathlib import Path

# Add the qa directory to the path
qa_dir = Path(__file__).parent
sys.path.insert(0, str(qa_dir))

from run_browser_tests import BrowserTestRunner
from playwright.sync_api import Page

class CustomTestRunner(BrowserTestRunner):
    """Custom test runner with additional test scenarios."""
    
    def test_custom_scenarios(self, page: Page):
        """Test custom scenarios specific to your application."""
        print("\n=== Testing Custom Scenarios ===")
        
        # Test a specific form submission
        self.navigate_to_page(page, f"{self.BASE_URL}/inspections/new", "Custom inspection form test")
        
        # Test form interaction
        try:
            # Look for form fields and fill them
            title_field = page.locator('input[name="title"], input[placeholder*="title"], input[placeholder*="Title"]')
            if title_field.count() > 0:
                title_field.first.fill("Custom Test Inspection")
                print("✅ Filled title field")
            
            # Test form submission
            submit_button = page.locator('button[type="submit"], input[type="submit"], button:has-text("Submit"), button:has-text("Create")')
            if submit_button.count() > 0:
                submit_button.first.click()
                self.wait_for_network_idle(page)
                print("✅ Submitted form")
                
        except Exception as e:
            self.log_error("custom-test", "FORM_ERROR", f"Form interaction failed: {str(e)}", page.url)
    
    def test_api_endpoints(self, page: Page):
        """Test specific API endpoints."""
        print("\n=== Testing API Endpoints ===")
        
        # Test VIN decoder with a real VIN
        test_vins = [
            "1HGBH41JXMN109186",  # Honda Civic
            "5NPE34AF4FH012345",  # Hyundai Sonata
            "WBA3B5C50FD123456"   # BMW 3 Series
        ]
        
        for vin in test_vins:
            try:
                response = page.request.get(f"{self.BASE_URL}/vehicle/decode/{vin}")
                if response.status == 200:
                    data = response.json()
                    print(f"✅ VIN {vin} decoded successfully: {data.get('make', 'Unknown')} {data.get('model', 'Unknown')}")
                else:
                    self.log_error("vehicle-service", "API_ERROR", 
                                  f"VIN decoder failed for {vin}: {response.status}", 
                                  f"{self.BASE_URL}/vehicle/decode/{vin}")
            except Exception as e:
                self.log_error("vehicle-service", "API_ERROR", 
                              f"VIN decoder exception for {vin}: {str(e)}", 
                              f"{self.BASE_URL}/vehicle/decode/{vin}")
    
    def run_tests(self):
        """Override the main test runner to include custom tests."""
        print("Starting Custom CheckMate Virtue Browser Tests")
        print(f"Base URL: {self.BASE_URL}")
        print(f"Headless: {self.HEADLESS}")
        print(f"Timeout: {self.TIMEOUT}ms")
        
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.HEADLESS)
            context = browser.new_context()
            page = context.new_page()
            
            # Setup error handlers
            self.setup_error_handlers(page)
            
            try:
                # Run standard tests
                self.test_public_routes(page)
                self.test_authenticated_routes(page)
                self.test_form_submissions(page)
                
                # Run custom tests
                self.test_custom_scenarios(page)
                self.test_api_endpoints(page)
                
            except Exception as e:
                self.log_error("test-runner", "TEST_ERROR", 
                              f"Test execution failed: {str(e)}", page.url)
            
            finally:
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
    """Main entry point for custom tests."""
    # Set default configuration
    os.environ.setdefault("BASE_URL", "http://localhost:8000")
    os.environ.setdefault("HEADLESS", "true")
    
    try:
        runner = CustomTestRunner()
        success = runner.run_tests()
        
        if success:
            print("\n✅ All custom tests completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Custom tests completed with errors. Check logs for details.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
