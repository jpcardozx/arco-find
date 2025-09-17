"""
Tests for Google PageSpeed API integration.

This module contains tests for the Google PageSpeed API integration.
"""

import os
import asyncio
import unittest
from unittest.mock import patch

from arco.integrations import GooglePageSpeedAPI


class TestGooglePageSpeedAPI(unittest.TestCase):
    """Tests for the Google PageSpeed API integration."""
    
    def setUp(self):
        """Set up the test environment."""
        self.pagespeed_api = GooglePageSpeedAPI()
    
    def test_initialization(self):
        """Test initialization of the PageSpeed API."""
        result = self.pagespeed_api.initialize("dummy_key")
        self.assertTrue(result)
    
    def test_rate_limit_status(self):
        """Test getting rate limit status."""
        status = self.pagespeed_api.get_rate_limit_status()
        self.assertEqual(status["limit"], 25000)
        self.assertEqual(status["remaining"], 25000)
    
    @patch('httpx.Client.get')
    def test_analyze_url(self, mock_get):
        """Test analyzing a URL with the PageSpeed API."""
        # Mock httpx.Client.get to return a successful response
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "lighthouseResult": {
                "categories": {
                    "performance": {
                        "score": 0.85
                    }
                },
                "audits": {
                    "first-contentful-paint": {
                        "score": 0.9,
                        "numericValue": 1200,
                        "displayValue": "1.2 s"
                    },
                    "largest-contentful-paint": {
                        "score": 0.8,
                        "numericValue": 2500,
                        "displayValue": "2.5 s"
                    }
                }
            }
        }
        mock_get.return_value = mock_response
        
        self.pagespeed_api.initialize("dummy_key")
        result = self.pagespeed_api.analyze_url("example.com")
        
        self.assertEqual(result["performance_score"], 85)
        self.assertIn("metrics", result)
        self.assertIn("first-contentful-paint", result["metrics"])
        self.assertIn("largest-contentful-paint", result["metrics"])
    
    def test_calculate_performance_loss(self):
        """Test calculating performance loss."""
        self.pagespeed_api.initialize("dummy_key")
        result = self.pagespeed_api.calculate_performance_loss(75, 10000)
        
        self.assertEqual(result["performance_score"], 75)
        self.assertEqual(result["conversion_impact_percentage"], 3.0)
        self.assertEqual(result["estimated_monthly_loss"], 300)
        self.assertEqual(result["estimated_annual_loss"], 3600)
        self.assertEqual(result["estimated_monthly_revenue"], 10000)
    
    @unittest.skipIf(not os.environ.get('RUN_LIVE_TESTS'), "Skipping live test")
    def test_analyze_url_async(self):
        """Test analyzing a URL asynchronously with the PageSpeed API."""
        api_key = os.environ.get('GOOGLE_PAGESPEED_API_KEY')
        
        if not api_key:
            self.skipTest("Google PageSpeed API key not available")
        
        self.pagespeed_api.initialize(api_key)
        result = asyncio.run(self.pagespeed_api.analyze_url_async("example.com"))
        
        self.assertIn("performance_score", result)
        self.assertIn("metrics", result)


if __name__ == '__main__':
    unittest.main()