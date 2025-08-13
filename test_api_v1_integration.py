#!/usr/bin/env python3
"""
Integration test for API v1 endpoints.
Verifies that all key endpoints exist and return expected responses.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from main import app

class APIV1IntegrationTest:
    """Integration test for API v1 endpoints."""
    
    def __init__(self):
        self.client = TestClient(app)
        self.test_results = []
    
    def test_health_endpoint(self) -> bool:
        """Test the health check endpoint."""
        try:
            response = self.client.get("/healthz")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            self.test_results.append(("Health Check", "PASS", "Health endpoint working"))
            return True
        except Exception as e:
            self.test_results.append(("Health Check", "FAIL", str(e)))
            return False
    
    def test_inspection_template_v1(self) -> bool:
        """Test the inspection template endpoint."""
        try:
            response = self.client.get("/api/v1/inspection/template")
            assert response.status_code == 200
            data = response.json()
            assert "inspection_points" in data
            self.test_results.append(("Inspection Template v1", "PASS", "Template endpoint working"))
            return True
        except Exception as e:
            self.test_results.append(("Inspection Template v1", "FAIL", str(e)))
            return False
    
    def test_create_inspection_v1(self) -> bool:
        """Test the create inspection endpoint."""
        try:
            inspection_data = {
                "vin": "1HGBH41JXMN109186",
                "vehicle_id": 1,
                "items": [
                    {
                        "step": "Exterior",
                        "subcategory": "Body",
                        "item": "Paint Condition",
                        "status": "Pass",
                        "notes": "Good condition"
                    }
                ]
            }
            
            response = self.client.post("/api/v1/inspection", json=inspection_data)
            print(f"Create inspection response status: {response.status_code}")
            print(f"Create inspection response body: {response.text}")
            
            if response.status_code != 200:
                self.test_results.append(("Create Inspection v1", "FAIL", f"Status {response.status_code}: {response.text}"))
                return False
                
            data = response.json()
            assert "inspection_id" in data
            assert "message" in data
            
            # Store the inspection ID for later tests
            self.test_inspection_id = data["inspection_id"]
            self.test_results.append(("Create Inspection v1", "PASS", f"Inspection created: {self.test_inspection_id}"))
            return True
        except Exception as e:
            self.test_results.append(("Create Inspection v1", "FAIL", f"Exception: {str(e)}"))
            return False
    
    def test_get_inspection_v1(self) -> bool:
        """Test the get inspection endpoint."""
        try:
            if not hasattr(self, 'test_inspection_id'):
                self.test_results.append(("Get Inspection v1", "SKIP", "No inspection ID available"))
                return False
            
            response = self.client.get(f"/api/v1/inspection/{self.test_inspection_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == self.test_inspection_id
            self.test_results.append(("Get Inspection v1", "PASS", "Inspection retrieved successfully"))
            return True
        except Exception as e:
            self.test_results.append(("Get Inspection v1", "FAIL", str(e)))
            return False
    
    def test_patch_inspection_v1(self) -> bool:
        """Test the patch inspection endpoint."""
        try:
            if not hasattr(self, 'test_inspection_id'):
                self.test_results.append(("Patch Inspection v1", "SKIP", "No inspection ID available"))
                return False
            
            patch_data = {
                "title": "Updated Test Inspection",
                "inspector_name": "Test Inspector"
            }
            
            response = self.client.patch(f"/api/v1/inspection/{self.test_inspection_id}", json=patch_data)
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            self.test_results.append(("Patch Inspection v1", "PASS", "Inspection patched successfully"))
            return True
        except Exception as e:
            self.test_results.append(("Patch Inspection v1", "FAIL", str(e)))
            return False
    
    def test_finalize_inspection_v1(self) -> bool:
        """Test the finalize inspection endpoint."""
        try:
            if not hasattr(self, 'test_inspection_id'):
                self.test_results.append(("Finalize Inspection v1", "SKIP", "No inspection ID available"))
                return False
            
            response = self.client.post(f"/api/v1/inspection/{self.test_inspection_id}/finalize")
            # This might fail if required fields are missing, which is expected
            if response.status_code == 200:
                data = response.json()
                assert "message" in data
                self.test_results.append(("Finalize Inspection v1", "PASS", "Inspection finalized successfully"))
                return True
            elif response.status_code == 400:
                self.test_results.append(("Finalize Inspection v1", "PASS", "Properly rejected incomplete inspection"))
                return True
            else:
                raise Exception(f"Unexpected status code: {response.status_code}")
        except Exception as e:
            self.test_results.append(("Finalize Inspection v1", "FAIL", str(e)))
            return False
    
    def test_report_inspection_v1(self) -> bool:
        """Test the report generation endpoint."""
        try:
            if not hasattr(self, 'test_inspection_id'):
                self.test_results.append(("Report Inspection v1", "SKIP", "No inspection ID available"))
                return False
            
            response = self.client.get(f"/api/v1/inspection/{self.test_inspection_id}/report")
            assert response.status_code == 200
            self.test_results.append(("Report Inspection v1", "PASS", "Report generated successfully"))
            return True
        except Exception as e:
            self.test_results.append(("Report Inspection v1", "FAIL", str(e)))
            return False
    
    def test_legacy_compatibility(self) -> bool:
        """Test legacy endpoint compatibility."""
        try:
            # Test legacy template endpoint
            response = self.client.get("/api/inspection-template")
            assert response.status_code == 200
            data = response.json()
            assert "inspection_points" in data
            
            # Test legacy inspection endpoint
            if hasattr(self, 'test_inspection_id'):
                response = self.client.get(f"/api/inspections/{self.test_inspection_id}")
                assert response.status_code == 200
                data = response.json()
                assert data["id"] == self.test_inspection_id
            
            self.test_results.append(("Legacy Compatibility", "PASS", "Legacy endpoints working"))
            return True
        except Exception as e:
            self.test_results.append(("Legacy Compatibility", "FAIL", str(e)))
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests."""
        print("🧪 Running API v1 Integration Tests...")
        print("=" * 50)
        
        tests = [
            self.test_health_endpoint,
            self.test_inspection_template_v1,
            self.test_create_inspection_v1,
            self.test_get_inspection_v1,
            self.test_patch_inspection_v1,
            self.test_finalize_inspection_v1,
            self.test_report_inspection_v1,
            self.test_legacy_compatibility,
        ]
        
        passed = 0
        failed = 0
        skipped = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                failed += 1
                print(f"❌ Test {test.__name__} failed with exception: {e}")
        
        # Count results
        for test_name, status, message in self.test_results:
            if status == "PASS":
                passed += 1
            elif status == "FAIL":
                failed += 1
            elif status == "SKIP":
                skipped += 1
        
        # Print results
        print("\n📊 Test Results:")
        print("-" * 50)
        for test_name, status, message in self.test_results:
            status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⏭️"
            print(f"{status_icon} {test_name}: {status} - {message}")
        
        print("\n" + "=" * 50)
        print(f"📈 Summary: {passed} passed, {failed} failed, {skipped} skipped")
        
        return {
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "total": passed + failed + skipped,
            "results": self.test_results
        }

def main():
    """Main function to run the integration tests."""
    test_runner = APIV1IntegrationTest()
    results = test_runner.run_all_tests()
    
    # Exit with appropriate code
    if results["failed"] > 0:
        print("❌ Some tests failed!")
        sys.exit(1)
    else:
        print("✅ All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()
