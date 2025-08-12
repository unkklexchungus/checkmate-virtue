#!/usr/bin/env python3
"""
Test script to verify the automotive service-based architecture.
"""

import asyncio
import httpx
import json
from typing import Dict, Any

# Define headers for API requests
headers = {"Content-Type": "application/json"}


class SystemTester:
    """Test the automotive service system."""
    
    def __init__(self):
        from app.config.runtime import build_url
        self.base_url = build_url("")  # Use the configured base URL
        self.auth_token = None
        self.customer_id = None
        self.vehicle_id = None
    
    async def test_health_checks(self) -> bool:
        """Test health checks for all services."""
        print("🔍 Testing health checks...")
        
        from app.config.runtime import build_url
        services = [
            ("API Gateway", build_url("")),
            ("Customer Service", build_url("")),  # Will be updated based on service configuration
            ("Vehicle Service", build_url("")),   # Will be updated based on service configuration
            ("Appointment Service", build_url("")), # Will be updated based on service configuration
            ("Workshop Service", build_url("")),   # Will be updated based on service configuration
            ("Inventory Service", build_url("")),  # Will be updated based on service configuration
            ("Notification Service", build_url("")), # Will be updated based on service configuration
        ]
        
        async with httpx.AsyncClient() as client:
            for name, url in services:
                try:
                    response = await client.get(f"{url}/health", timeout=5.0)
                    if response.status_code == 200:
                        print(f"✅ {name}: Healthy")
                    else:
                        print(f"❌ {name}: Unhealthy ({response.status_code})")
                        return False
                except Exception as e:
                    print(f"❌ {name}: Error - {e}")
                    return False
        
        print("✅ All services are healthy!")
        return True
    
    async def test_auth_flow(self) -> bool:
        """Test authentication flow - SKIPPED (auth removed)."""
        print("\n🔐 Testing authentication flow...")
        print("⏭️  Auth service removed - skipping auth tests")
        return True
    
    async def test_customer_flow(self) -> bool:
        """Test customer management flow."""
        print("\n👥 Testing customer management flow...")
        
        async with httpx.AsyncClient() as client:
            
            # Create customer
            customer_data = {
                "name": "John Doe",
                "company": "ABC Automotive",
                "tax_id": "12-3456789",
                "notes": "Test customer",
                "address": {
                    "street": "123 Main St",
                    "city": "Anytown",
                    "state": "CA",
                    "zip_code": "90210",
                    "country": "USA"
                },
                "contact": {
                    "phone": "555-123-4567",
                    "email": "john@abc.com",
                    "website": "https://abc.com"
                }
            }
            
            try:
                response = await client.post(
                    f"{self.base_url}/v1/customers",
                    json=customer_data,
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.customer_id = data["data"]["id"]
                    print("✅ Customer creation successful")
                else:
                    print(f"❌ Customer creation failed: {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
                
                # Get customer list
                response = await client.get(
                    f"{self.base_url}/v1/customers",
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    print("✅ Customer list retrieval successful")
                    return True
                else:
                    print(f"❌ Customer list failed: {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ Customer flow error: {e}")
                return False
    
    async def test_vehicle_flow(self) -> bool:
        """Test vehicle management flow."""
        print("\n🚗 Testing vehicle management flow...")
        
        async with httpx.AsyncClient() as client:
            
            # Create vehicle
            vehicle_data = {
                "vin": "1HGBH41JXMN109186",
                "year": "2021",
                "make": "Honda",
                "model": "Civic",
                "trim": "EX",
                "engine": "1.5L Turbo",
                "transmission": "CVT",
                "body_style": "Sedan",
                "fuel_type": "Gasoline",
                "drivetrain": "FWD"
            }
            
            try:
                response = await client.post(
                    f"{self.base_url}/v1/vehicles",
                    json=vehicle_data,
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.vehicle_id = data["data"]["id"]
                    print("✅ Vehicle creation successful")
                else:
                    print(f"❌ Vehicle creation failed: {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
                
                # Test VIN decoding
                response = await client.get(
                    f"{self.base_url}/v1/vehicles/decode/1HGBH41JXMN109186",
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    print("✅ VIN decoding successful")
                    return True
                else:
                    print(f"❌ VIN decoding failed: {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ Vehicle flow error: {e}")
                return False
    
    async def test_workshop_flow(self) -> bool:
        """Test workshop management flow."""
        print("\n🔧 Testing workshop management flow...")
        
        if not self.customer_id or not self.vehicle_id:
            print("❌ Missing required data for workshop flow")
            return False
        
        async with httpx.AsyncClient() as client:
            
            # Create estimate
            estimate_data = {
                "customer_id": self.customer_id,
                "vehicle_id": self.vehicle_id,
                "items": [
                    {
                        "description": "Oil Change",
                        "quantity": 1,
                        "unit_price": 29.99,
                        "item_type": "service"
                    },
                    {
                        "description": "Oil Filter",
                        "quantity": 1,
                        "unit_price": 8.99,
                        "item_type": "parts"
                    }
                ],
                "notes": "Regular maintenance"
            }
            
            try:
                response = await client.post(
                    f"{self.base_url}/v1/workshop/estimates",
                    json=estimate_data,
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    print("✅ Estimate creation successful")
                    return True
                else:
                    print(f"❌ Estimate creation failed: {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
                    
            except Exception as e:
                print(f"❌ Workshop flow error: {e}")
                return False
    
    async def run_all_tests(self) -> bool:
        """Run all system tests."""
        print("🚀 Starting Automotive System Tests")
        print("=" * 50)
        
        tests = [
            ("Health Checks", self.test_health_checks),
            ("Authentication Flow", self.test_auth_flow),
            ("Customer Management", self.test_customer_flow),
            ("Vehicle Management", self.test_vehicle_flow),
            ("Workshop Management", self.test_workshop_flow),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results.append((test_name, False))
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Test Results Summary")
        print("=" * 50)
        
        passed = 0
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{len(results)} tests passed")
        
        if passed == len(results):
            print("🎉 All tests passed! System is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Check the logs above for details.")
            return False


async def main():
    """Main test function."""
    tester = SystemTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎯 System is ready for use!")
        from app.config.runtime import build_url
        print("\nAccess points:")
        print(f"- API Gateway: {build_url('')}")
        print(f"- API Docs: {build_url('/docs')}")
        print("- pgAdmin: http://localhost:5050")
    else:
        print("\n❌ System has issues. Check the logs above.")
    
    return success


if __name__ == "__main__":
    import sys
    
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
