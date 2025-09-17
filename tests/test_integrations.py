"""
Tests for ARCO integrations.

This module contains tests for the ARCO integrations with external services.
"""

import os
import asyncio
import unittest
from unittest.mock import patch

from arco.integrations import WappalyzerIntegration, GoogleSearchAPI, GooglePageSpeedAPI


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


class TestGoogleSearchAPI(unittest.TestCase):
    """Tests for the Google Search API integration."""
    
    def setUp(self):
        """Set up the test environment."""
        self.search_api = GoogleSearchAPI()
    
    def test_initialization_without_search_engine_id(self):
        """Test initialization without search engine ID."""
        result = self.search_api.initialize("dummy_key")
        self.assertFalse(result)
    
    def test_initialization_with_search_engine_id(self):
        """Test initialization with search engine ID."""
        result = self.search_api.initialize("dummy_key", search_engine_id="dummy_cx")
        self.assertTrue(result)
    
    def test_rate_limit_status(self):
        """Test getting rate limit status."""
        status = self.search_api.get_rate_limit_status()
        self.assertEqual(status["limit"], 100)
        self.assertEqual(status["remaining"], 100)
    
    @patch('httpx.Client.get')
    def test_search(self, mock_get):
        """Test searching with the Google Search API."""
        # Mock httpx.Client.get to return a successful response
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "title": "Test Result",
                    "link": "https://example.com",
                    "snippet": "This is a test result.",
                    "displayLink": "example.com",
                    "formattedUrl": "https://example.com"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        self.search_api.initialize("dummy_key", search_engine_id="dummy_cx")
        results = self.search_api.search("test query")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Test Result")
        self.assertEqual(results[0]["url"], "https://example.com")
    
    @unittest.skipIf(not os.environ.get('RUN_LIVE_TESTS'), "Skipping live test")
    def test_search_saas_footprint(self):
        """Test searching for SaaS footprints."""
        api_key = os.environ.get('GOOGLE_SEARCH_API_KEY')
        search_engine_id = os.environ.get('GOOGLE_SEARCH_CX')
        
        if not api_key or not search_engine_id:
            self.skipTest("Google Search API credentials not available")
        
        self.search_api.initialize(api_key, search_engine_id=search_engine_id)
        result = asyncio.run(self.search_api.search_saas_footprint("shopify.com", "shopify_plus"))
        
        self.assertIn("found", result)
        self.assertIn("confidence", result)


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