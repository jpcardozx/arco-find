"""
Tests for Google Search API integration.

This module contains tests for the Google Search API integration.
"""

import os
import asyncio
import unittest
from unittest.mock import patch

from arco.integrations import GoogleSearchAPI


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


if __name__ == '__main__':
    unittest.main()