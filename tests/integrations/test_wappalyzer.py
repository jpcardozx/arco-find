"""
Tests for Wappalyzer integration.

This module contains tests for the Wappalyzer integration.
"""

import os
import asyncio
import unittest
from unittest.mock import patch

from arco.integrations import WappalyzerIntegration


class TestWappalyzerIntegration(unittest.TestCase):
    """Tests for the Wappalyzer integration."""
    
    def setUp(self):
        """Set up the test environment."""
        self.wappalyzer = WappalyzerIntegration()
    
    def test_initialization(self):
        """Test initialization of the Wappalyzer integration."""
        result = self.wappalyzer.initialize("dummy_key")
        # Should return True even with a dummy key since Wappalyzer doesn't need an API key
        self.assertTrue(result)
    
    def test_rate_limit_status(self):
        """Test getting rate limit status."""
        status = self.wappalyzer.get_rate_limit_status()
        self.assertEqual(status["limit"], "unlimited")
        self.assertEqual(status["remaining"], "unlimited")
    
    @patch('subprocess.run')
    def test_cli_availability_check(self, mock_run):
        """Test checking Wappalyzer CLI availability."""
        # Mock subprocess.run to simulate CLI availability
        mock_run.return_value.returncode = 0
        
        wappalyzer = WappalyzerIntegration()
        self.assertTrue(wappalyzer.wappalyzer_cli_available)
    
    @unittest.skipIf(not os.environ.get('RUN_LIVE_TESTS'), "Skipping live test")
    def test_analyze_url(self):
        """Test analyzing a URL with Wappalyzer."""
        result = asyncio.run(self.wappalyzer.analyze_url("example.com"))
        self.assertIn("technologies", result)


if __name__ == '__main__':
    unittest.main()