"""
Tests for retry and fallback mechanisms in ARCO integrations.
"""

import unittest
import asyncio
from unittest.mock import patch, MagicMock
import httpx
import pytest

from arco.utils.retry import RetryConfig, with_retry, with_retry_async, FallbackChain
from arco.integrations.google_api import GoogleSearchAPI
from arco.integrations.wappalyzer import WappalyzerIntegration


class TestRetryMechanisms(unittest.TestCase):
    """Test cases for retry mechanisms."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.google_api = GoogleSearchAPI()
        self.google_api.initialize("test_api_key", search_engine_id="test_search_engine_id")
    
    @patch('httpx.Client')
    def test_retry_on_connection_error(self, mock_client):
        """Test retry mechanism on connection error."""
        # Configure the mock to raise ConnectionError twice and then succeed
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"title": "Test", "link": "https://test.com", "snippet": "Test snippet"}]}
        
        mock_client_instance = MagicMock()
        mock_client_instance.__enter__.return_value.get.side_effect = [
            ConnectionError("Connection refused"),
            ConnectionError("Connection timed out"),
            mock_response
        ]
        mock_client.return_value = mock_client_instance
        
        # Execute search with retry
        results = self.google_api.search("test query", retry_config=RetryConfig(max_retries=3, retry_delay=0.01))
        
        # Verify results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Test")
        self.assertEqual(mock_client_instance.__enter__.return_value.get.call_count, 3)
    
    @patch('httpx.Client')
    def test_retry_on_status_code(self, mock_client):
        """Test retry mechanism on specific status codes."""
        # Configure the mock to return 429 (Too Many Requests) twice and then 200
        mock_response_429 = MagicMock()
        mock_response_429.status_code = 429
        
        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {"items": [{"title": "Test", "link": "https://test.com", "snippet": "Test snippet"}]}
        
        mock_client_instance = MagicMock()
        mock_client_instance.__enter__.return_value.get.side_effect = [
            mock_response_429,
            mock_response_429,
            mock_response_200
        ]
        mock_client.return_value = mock_client_instance
        
        # Execute search with retry
        results = self.google_api.search("test query", retry_config=RetryConfig(max_retries=3, retry_delay=0.01))
        
        # Verify results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Test")
        self.assertEqual(mock_client_instance.__enter__.return_value.get.call_count, 3)
    
    @patch('httpx.Client')
    def test_max_retries_exceeded(self, mock_client):
        """Test behavior when max retries are exceeded."""
        # Configure the mock to always raise ConnectionError
        mock_client_instance = MagicMock()
        mock_client_instance.__enter__.return_value.get.side_effect = ConnectionError("Connection refused")
        mock_client.return_value = mock_client_instance
        
        # Execute search with retry
        results = self.google_api.search("test query", retry_config=RetryConfig(max_retries=3, retry_delay=0.01))
        
        # Verify results (should be empty after all retries fail)
        self.assertEqual(len(results), 0)
        self.assertEqual(mock_client_instance.__enter__.return_value.get.call_count, 3)


@pytest.mark.asyncio
class TestFallbackMechanisms:
    """Test cases for fallback mechanisms."""
    
    @pytest.fixture
    def wappalyzer(self):
        """Create a WappalyzerIntegration instance for testing."""
        wapp = WappalyzerIntegration()
        wapp.initialize("test_api_key")
        return wapp
    
    @patch('arco.integrations.wappalyzer.WappalyzerIntegration._analyze_with_cli')
    @patch('arco.integrations.wappalyzer.WappalyzerIntegration._analyze_with_py_lib')
    @patch('arco.integrations.wappalyzer.WappalyzerIntegration._analyze_with_http_fallback')
    async def test_fallback_chain(self, mock_http, mock_py, mock_cli, wappalyzer):
        """Test fallback chain when primary methods fail."""
        # Configure mocks
        mock_cli.side_effect = Exception("CLI failed")
        mock_py.side_effect = Exception("Python lib failed")
        mock_http.return_value = {"technologies": [{"name": "Fallback Tech", "categories": ["Test"]}]}
        
        # Force availability flags
        wappalyzer.wappalyzer_cli_available = True
        wappalyzer.wappalyzer_py_available = True
        
        # Execute analyze_url which should try all methods and fall back to HTTP
        result = await wappalyzer.analyze_url("https://example.com")
        
        # Verify results
        assert len(result["technologies"]) == 1
        assert result["technologies"][0]["name"] == "Fallback Tech"
        
        # Verify all methods were called in order
        mock_cli.assert_called_once()
        mock_py.assert_called_once()
        mock_http.assert_called_once()
    
    @patch('arco.integrations.wappalyzer.WappalyzerIntegration._analyze_with_cli')
    @patch('arco.integrations.wappalyzer.WappalyzerIntegration._analyze_with_py_lib')
    @patch('arco.integrations.wappalyzer.WappalyzerIntegration._analyze_with_http_fallback')
    async def test_fallback_chain_first_success(self, mock_http, mock_py, mock_cli, wappalyzer):
        """Test fallback chain when first method succeeds."""
        # Configure mocks
        mock_cli.return_value = {"technologies": [{"name": "CLI Tech", "categories": ["Test"]}]}
        
        # Force availability flags
        wappalyzer.wappalyzer_cli_available = True
        wappalyzer.wappalyzer_py_available = True
        
        # Execute analyze_url which should succeed with first method
        result = await wappalyzer.analyze_url("https://example.com")
        
        # Verify results
        assert len(result["technologies"]) == 1
        assert result["technologies"][0]["name"] == "CLI Tech"
        
        # Verify only first method was called
        mock_cli.assert_called_once()
        mock_py.assert_not_called()
        mock_http.assert_not_called()


@pytest.mark.asyncio
class TestAsyncRetry:
    """Test cases for async retry mechanisms."""
    
    @pytest.fixture
    def google_api(self):
        """Create a GoogleSearchAPI instance for testing."""
        api = GoogleSearchAPI()
        api.initialize("test_api_key", search_engine_id="test_search_engine_id")
        return api
    
    @patch('httpx.AsyncClient')
    async def test_async_retry(self, mock_client, google_api):
        """Test async retry mechanism."""
        # Configure the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"title": "Test", "link": "https://test.com", "snippet": "Test snippet"}]}
        
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__.return_value.get.side_effect = [
            ConnectionError("Connection refused"),
            mock_response
        ]
        mock_client.return_value = mock_client_instance
        
        # Execute search with retry
        result = await google_api.search_saas_footprint("example.com", "typeform", 
                                                       retry_config=RetryConfig(max_retries=2, retry_delay=0.01))
        
        # Verify results
        assert result["found"] == True
        assert mock_client_instance.__aenter__.return_value.get.call_count == 2


if __name__ == '__main__':
    unittest.main()