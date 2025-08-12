#!/usr/bin/env python3
"""
Unit tests for runtime configuration module.
"""

import os
import unittest
from unittest.mock import patch, MagicMock
import sys
import tempfile

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from config.runtime import build_url, is_ipv6_url, validate_base_url, BASE_URL


class TestRuntimeConfig(unittest.TestCase):
    """Test cases for runtime configuration."""

    def setUp(self):
        """Set up test environment."""
        # Store original environment
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Clean up test environment."""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_build_url_with_leading_slash(self):
        """Test build_url with path that has leading slash."""
        with patch.dict(os.environ, {'APP_BASE_URL': 'http://127.0.0.1:8000'}):
            # Re-import to get fresh BASE_URL
            import importlib
            import config.runtime
            importlib.reload(config.runtime)
            
            result = config.runtime.build_url('/api/health')
            self.assertEqual(result, 'http://127.0.0.1:8000/api/health')

    def test_build_url_without_leading_slash(self):
        """Test build_url with path that doesn't have leading slash."""
        with patch.dict(os.environ, {'APP_BASE_URL': 'http://127.0.0.1:8000'}):
            # Re-import to get fresh BASE_URL
            import importlib
            import config.runtime
            importlib.reload(config.runtime)
            
            result = config.runtime.build_url('api/health')
            self.assertEqual(result, 'http://127.0.0.1:8000/api/health')

    def test_build_url_empty_path(self):
        """Test build_url with empty path."""
        with patch.dict(os.environ, {'APP_BASE_URL': 'http://127.0.0.1:8000'}):
            # Re-import to get fresh BASE_URL
            import importlib
            import config.runtime
            importlib.reload(config.runtime)
            
            result = config.runtime.build_url('')
            self.assertEqual(result, 'http://127.0.0.1:8000')

    def test_build_url_none_path(self):
        """Test build_url with None path."""
        with patch.dict(os.environ, {'APP_BASE_URL': 'http://127.0.0.1:8000'}):
            # Re-import to get fresh BASE_URL
            import importlib
            import config.runtime
            importlib.reload(config.runtime)
            
            result = config.runtime.build_url(None)
            self.assertEqual(result, 'http://127.0.0.1:8000')

    def test_build_url_with_base_url_trailing_slash(self):
        """Test build_url with base URL that has trailing slash."""
        with patch.dict(os.environ, {'APP_BASE_URL': 'http://127.0.0.1:8000/'}):
            # Re-import to get fresh BASE_URL
            import importlib
            import config.runtime
            importlib.reload(config.runtime)
            
            result = config.runtime.build_url('/api/health')
            self.assertEqual(result, 'http://127.0.0.1:8000/api/health')

    def test_build_url_with_complex_path(self):
        """Test build_url with complex path."""
        with patch.dict(os.environ, {'APP_BASE_URL': 'http://127.0.0.1:8000'}):
            # Re-import to get fresh BASE_URL
            import importlib
            import config.runtime
            importlib.reload(config.runtime)
            
            result = config.runtime.build_url('/api/v1/users/123/profile')
            self.assertEqual(result, 'http://127.0.0.1:8000/api/v1/users/123/profile')

    def test_build_url_with_query_params(self):
        """Test build_url with path containing query parameters."""
        with patch.dict(os.environ, {'APP_BASE_URL': 'http://127.0.0.1:8000'}):
            # Re-import to get fresh BASE_URL
            import importlib
            import config.runtime
            importlib.reload(config.runtime)
            
            result = config.runtime.build_url('/api/search?q=test&page=1')
            self.assertEqual(result, 'http://127.0.0.1:8000/api/search?q=test&page=1')

    def test_build_url_with_fragment(self):
        """Test build_url with path containing fragment."""
        with patch.dict(os.environ, {'APP_BASE_URL': 'http://127.0.0.1:8000'}):
            # Re-import to get fresh BASE_URL
            import importlib
            import config.runtime
            importlib.reload(config.runtime)
            
            result = config.runtime.build_url('/api/docs#section1')
            self.assertEqual(result, 'http://127.0.0.1:8000/api/docs#section1')

    def test_build_url_with_docker_service_name(self):
        """Test build_url with Docker service name as base URL."""
        with patch.dict(os.environ, {'APP_BASE_URL': 'http://api-gateway:8000'}):
            # Re-import to get fresh BASE_URL
            import importlib
            import config.runtime
            importlib.reload(config.runtime)
            
            result = config.runtime.build_url('/health')
            self.assertEqual(result, 'http://api-gateway:8000/health')

    def test_build_url_with_https(self):
        """Test build_url with HTTPS base URL."""
        with patch.dict(os.environ, {'APP_BASE_URL': 'https://api.example.com'}):
            # Re-import to get fresh BASE_URL
            import importlib
            import config.runtime
            importlib.reload(config.runtime)
            
            result = config.runtime.build_url('/api/secure')
            self.assertEqual(result, 'https://api.example.com/api/secure')

    def test_is_ipv6_url_with_ipv4(self):
        """Test is_ipv6_url with IPv4 address."""
        self.assertFalse(is_ipv6_url('http://127.0.0.1:8000'))
        self.assertFalse(is_ipv6_url('http://192.168.1.1:8000'))

    def test_is_ipv6_url_with_ipv6(self):
        """Test is_ipv6_url with IPv6 address."""
        self.assertTrue(is_ipv6_url('http://[::1]:8000'))
        self.assertTrue(is_ipv6_url('http://[2001:db8::1]:8000'))
        self.assertTrue(is_ipv6_url('http://::1:8000'))

    def test_is_ipv6_url_with_hostname(self):
        """Test is_ipv6_url with hostname."""
        self.assertFalse(is_ipv6_url('http://localhost:8000'))
        self.assertFalse(is_ipv6_url('http://api.example.com'))

    def test_is_ipv6_url_with_invalid_url(self):
        """Test is_ipv6_url with invalid URL."""
        self.assertFalse(is_ipv6_url('not-a-url'))
        self.assertFalse(is_ipv6_url(''))

    def test_validate_base_url_with_valid_url(self):
        """Test validate_base_url with valid URL."""
        with patch.dict(os.environ, {'APP_BASE_URL': 'http://127.0.0.1:8000'}):
            # Re-import to get fresh BASE_URL
            import importlib
            import config.runtime
            importlib.reload(config.runtime)
            
            self.assertTrue(config.runtime.validate_base_url())

    def test_validate_base_url_with_https(self):
        """Test validate_base_url with HTTPS URL."""
        with patch.dict(os.environ, {'APP_BASE_URL': 'https://api.example.com'}):
            # Re-import to get fresh BASE_URL
            import importlib
            import config.runtime
            importlib.reload(config.runtime)
            
            self.assertTrue(config.runtime.validate_base_url())

    def test_validate_base_url_with_invalid_scheme(self):
        """Test validate_base_url with invalid scheme."""
        with patch.dict(os.environ, {'APP_BASE_URL': 'ftp://127.0.0.1:8000'}):
            # Re-import to get fresh BASE_URL
            import importlib
            import config.runtime
            importlib.reload(config.runtime)
            
            self.assertFalse(config.runtime.validate_base_url())

    def test_validate_base_url_with_missing_scheme(self):
        """Test validate_base_url with missing scheme."""
        with patch.dict(os.environ, {'APP_BASE_URL': '127.0.0.1:8000'}):
            # Re-import to get fresh BASE_URL
            import importlib
            import config.runtime
            importlib.reload(config.runtime)
            
            self.assertFalse(config.runtime.validate_base_url())

    def test_validate_base_url_with_missing_host(self):
        """Test validate_base_url with missing host."""
        with patch.dict(os.environ, {'APP_BASE_URL': 'http://'}):
            # Re-import to get fresh BASE_URL
            import importlib
            import config.runtime
            importlib.reload(config.runtime)
            
            self.assertFalse(config.runtime.validate_base_url())

    def test_base_url_default_value(self):
        """Test that BASE_URL has correct default value."""
        # Clear APP_BASE_URL to test default
        if 'APP_BASE_URL' in os.environ:
            del os.environ['APP_BASE_URL']
        
        # Re-import to get fresh default
        import importlib
        import config.runtime
        importlib.reload(config.runtime)
        
        self.assertEqual(config.runtime.BASE_URL, 'http://127.0.0.1:8000')

    def test_base_url_from_environment(self):
        """Test that BASE_URL is read from environment."""
        with patch.dict(os.environ, {'APP_BASE_URL': 'http://custom.example.com:9000'}):
            # Re-import to get fresh value
            import importlib
            import config.runtime
            importlib.reload(config.runtime)
            
            self.assertEqual(config.runtime.BASE_URL, 'http://custom.example.com:9000')


if __name__ == '__main__':
    unittest.main()
