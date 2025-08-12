#!/usr/bin/env python3
"""
Test script to verify the enhanced artifact capture system.
This script tests the artifact capture functionality without running full browser tests.
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_artifact_directories():
    """Test that artifact directories are created correctly."""
    print("Testing artifact directory creation...")
    
    try:
        from conftest import ARTIFACTS_DIR, HTML_DIR
        from test_artifact_helpers import ARTIFACTS_DIR as helper_artifacts_dir
        
        # Check that directories exist
        assert ARTIFACTS_DIR.exists(), f"ARTIFACTS_DIR does not exist: {ARTIFACTS_DIR}"
        assert HTML_DIR.exists(), f"HTML_DIR does not exist: {HTML_DIR}"
        assert helper_artifacts_dir.exists(), f"Helper ARTIFACTS_DIR does not exist: {helper_artifacts_dir}"
        
        print("✅ Artifact directories created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create artifact directories: {e}")
        return False


def test_helper_functions():
    """Test that helper functions work correctly."""
    print("Testing helper functions...")
    
    try:
        from test_artifact_helpers import (
            _sanitize_test_name,
            create_artifact_report,
            save_artifact_report
        )
        
        # Test sanitize function
        test_name = "test/with:special:chars"
        sanitized = _sanitize_test_name(test_name)
        expected = "test_with_special_chars"
        assert sanitized == expected, f"Expected {expected}, got {sanitized}"
        
        # Test report creation
        test_names = ["test_1", "test_2"]
        report = create_artifact_report(test_names)
        assert "ARTIFACT CAPTURE REPORT" in report
        assert "test_1" in report
        assert "test_2" in report
        
        # Test report saving
        report_path = save_artifact_report(test_names)
        assert report_path.exists()
        
        print("✅ Helper functions work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Helper functions failed: {e}")
        return False


def test_imports():
    """Test that all required modules can be imported."""
    print("Testing module imports...")
    
    try:
        # Test conftest imports
        from conftest import artifact_capture, PlaywrightArtifactCapture
        assert artifact_capture is not None
        assert PlaywrightArtifactCapture is not None
        
        # Test helper imports
        from test_artifact_helpers import capture_failure_artifacts
        assert capture_failure_artifacts is not None
        
        print("✅ All modules imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_directory_structure():
    """Test that the expected directory structure exists."""
    print("Testing directory structure...")
    
    try:
        qa_dir = Path(__file__).parent
        expected_files = [
            "conftest.py",
            "test_artifact_helpers.py",
            "test_artifact_example.py",
            "ARTIFACT_CAPTURE_README.md"
        ]
        
        for file_name in expected_files:
            file_path = qa_dir / file_name
            assert file_path.exists(), f"Expected file not found: {file_path}"
        
        print("✅ Directory structure is correct")
        return True
        
    except Exception as e:
        print(f"❌ Directory structure test failed: {e}")
        return False


def test_enhanced_log_error():
    """Test that the enhanced log_error method signature is correct."""
    print("Testing enhanced log_error method...")
    
    try:
        # Import the enhanced method
        import run_browser_tests
        runner = run_browser_tests.BrowserTestRunner()
        
        # Check that the method accepts the page parameter
        import inspect
        sig = inspect.signature(runner.log_error)
        params = list(sig.parameters.keys())
        
        # Should have page parameter
        assert 'page' in params, f"Expected 'page' parameter, got: {params}"
        
        print("✅ Enhanced log_error method signature is correct")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced log_error test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Enhanced Artifact Capture System Test")
    print("=" * 60)
    print(f"Test run started at: {datetime.now().isoformat()}")
    print()
    
    tests = [
        test_directory_structure,
        test_imports,
        test_artifact_directories,
        test_helper_functions,
        test_enhanced_log_error
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("\n✅ All tests passed! Artifact capture system is ready.")
        print("\nNext steps:")
        print("1. Run: cd qa && python3 run_browser_tests.py")
        print("2. Run: cd qa && python -m pytest test_artifact_example.py -v")
        print("3. Check the artifacts directory for captured files")
    else:
        print(f"\n❌ {failed} test(s) failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
