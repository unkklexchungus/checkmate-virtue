#!/usr/bin/env python3
"""
Test script for VIN decoder functionality.
Demonstrates all the different ways to use the VIN decoder.
"""

import sys
import os
import subprocess
import asyncio
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_node_cli():
    """Test the Node.js CLI directly - REMOVED (API Verve service removed)."""
    print("🔧 Testing Node.js CLI...")
    print("⏭️  Node.js CLI removed - API Verve service no longer available")
    return True

def test_python_api_verve():
    """Test the Python API Verve integration - REMOVED (API Verve service removed)."""
    print("\n🐍 Testing Python API Verve integration...")
    print("⏭️  API Verve integration removed - using NHTSA API only")
    return True

async def test_python_service():
    """Test the main Python VIN decoder service."""
    print("\n🚗 Testing Python VIN decoder service...")
    try:
        from modules.vehicle_data.service import decode_vin
        
        result = await decode_vin('1HGBH41JXMN109186')
        
        if result:
            print("✅ Python VIN decoder service test passed")
            print(f"  VIN: {result.vin}")
            print(f"  Year: {result.year}")
            print(f"  Make: {result.make}")
            print(f"  Model: {result.model}")
        else:
            print("❌ Python VIN decoder service returned no result")
            
    except Exception as e:
        print(f"❌ Python VIN decoder service test error: {e}")

def test_npm_scripts():
    """Test the npm scripts - REMOVED (No npm allowed in this project)."""
    print("\n📦 Testing npm scripts...")
    print("⏭️  npm scripts removed - No npm allowed in this project")
    return True

def main():
    """Run all tests."""
    print("🚗 VIN Decoder Test Suite")
    print("=" * 50)
    
    # Test Node.js CLI
    test_node_cli()
    
    # Test Python API Verve integration
    test_python_api_verve()
    
    # Test npm scripts
    test_npm_scripts()
    
    # Test Python service (async)
    print("\n🔄 Testing async Python service...")
    asyncio.run(test_python_service())
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("\n📋 Usage Summary:")
    print("  • Node.js CLI: node vin_decoder_cli.js [VIN]")
    print("  • npm script: REMOVED (No npm allowed)")
    print("  • Python service: await decode_vin(VIN)")
    print("  • Python API Verve: decode_vin_with_api_verve_sync(VIN)")

if __name__ == "__main__":
    main()
