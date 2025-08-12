#!/usr/bin/env python3
"""
Smoke test for the canonical invoice API endpoint.
Tests POST /api/invoices with minimal valid payload.
"""

import json
import requests
import sys
from datetime import date, datetime, timedelta
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"
API_ENDPOINT = f"{BASE_URL}/api/invoices"

def create_test_client() -> str:
    """Create a test client and return its ID."""
    client_data = {
        "name": "Test Client",
        "company": "Test Company",
        "address": {
            "street": "123 Test St",
            "city": "Test City",
            "state": "CA",
            "zip_code": "90210",
            "country": "USA"
        },
        "contact": {
            "phone": "(555) 123-4567",
            "email": "test@example.com"
        }
    }
    
    response = requests.post(f"{BASE_URL}/invoices/api/clients", json=client_data)
    if response.status_code == 201 or response.status_code == 200:
        return response.json().get("client_id")
    else:
        # If client creation fails, use a default test client ID
        return "test_client_001"

def test_canonical_invoice_endpoint() -> bool:
    """Test the canonical invoice creation endpoint."""
    print("🧪 Testing canonical invoice API endpoint...")
    
    # Create a test client first
    client_id = create_test_client()
    
    # Minimal valid payload for invoice creation
    test_payload = {
        "client_id": client_id,
        "industry_type": "automotive",
        "issue_date": date.today().isoformat(),
        "due_date": (date.today() + timedelta(days=30)).isoformat(),
        "items": [
            {
                "description": "Test Service",
                "quantity": 1.0,
                "unit_price": 100.00,
                "item_type": "service"
            }
        ]
    }
    
    try:
        print(f"  📤 Sending POST request to {API_ENDPOINT}")
        print(f"  📋 Payload: {json.dumps(test_payload, indent=2)}")
        
        response = requests.post(
            API_ENDPOINT,
            json=test_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"  📥 Response Status: {response.status_code}")
        print(f"  📥 Response Headers: {dict(response.headers)}")
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            print(f"  ✅ Success! Response: {json.dumps(response_data, indent=2)}")
            
            # Verify response structure
            if "invoice_id" in response_data:
                print(f"  ✅ Invoice ID returned: {response_data['invoice_id']}")
                return True
            else:
                print(f"  ❌ Missing invoice_id in response")
                return False
        else:
            print(f"  ❌ Expected 200 OK or 201 Created, got {response.status_code}")
            print(f"  ❌ Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"  ❌ Invalid JSON response: {e}")
        return False

def test_backward_compatibility() -> bool:
    """Test that the old endpoint still works for backward compatibility."""
    print("\n🔄 Testing backward compatibility...")
    
    # Create a test client first
    client_id = create_test_client()
    
    # Minimal valid payload
    test_payload = {
        "client_id": client_id,
        "industry_type": "automotive",
        "issue_date": date.today().isoformat(),
        "due_date": (date.today() + timedelta(days=30)).isoformat(),
        "items": [
            {
                "description": "Backward Compatibility Test",
                "quantity": 1.0,
                "unit_price": 50.00,
                "item_type": "service"
            }
        ]
    }
    
    try:
        old_endpoint = f"{BASE_URL}/invoices/api/invoices"
        print(f"  📤 Sending POST request to {old_endpoint}")
        
        response = requests.post(
            old_endpoint,
            json=test_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"  📥 Response Status: {response.status_code}")
        
        if response.status_code == 201 or response.status_code == 200:
            response_data = response.json()
            print(f"  ✅ Backward compatibility maintained! Response: {json.dumps(response_data, indent=2)}")
            return True
        else:
            print(f"  ❌ Backward compatibility broken! Status: {response.status_code}")
            print(f"  ❌ Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Request failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Invoice API Smoke Tests\n")
    
    # Test canonical endpoint
    canonical_success = test_canonical_invoice_endpoint()
    
    # Test backward compatibility
    backward_success = test_backward_compatibility()
    
    # Summary
    print("\n📊 Test Summary:")
    print(f"  Canonical endpoint (/api/invoices): {'✅ PASS' if canonical_success else '❌ FAIL'}")
    print(f"  Backward compatibility (/invoices/api/invoices): {'✅ PASS' if backward_success else '❌ FAIL'}")
    
    if canonical_success and backward_success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n💥 Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
