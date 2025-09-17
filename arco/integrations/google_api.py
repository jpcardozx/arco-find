"""
Google API Integration for ARCO.

This module provides integration with Google APIs, including:
- Google Custom Search API for SaaS footprint confirmation
- Google PageSpeed Insights API for performance analysis
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional, Callable
import httpx
import asyncio

from arco.integrations.base import APIClientInterface
from arco.utils.retry import RetryConfig, with_retry, with_retry_async, FallbackChain

logger = logging.getLogger(__name__)

class GoogleSearchAPI(APIClientInterface):
    """Google Custom Search API integration for ARCO."""
    
    def __init__(self):
        """Initialize the Google Search API integration."""
        self.api_key = None
        self.search_engine_id = None
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.rate_limit_info = {
            "limit": 100,  # Default daily limit for free tier
            "remaining": 100,
            "reset": None
        }
    
    def initialize(self, api_key: str, **kwargs) -> bool:
        """
        Initialize the Google Search API integration with credentials.
        
        Args:
            api_key: API key for authentication
            **kwargs: Additional configuration parameters including search_engine_id
            
        Returns:
            True if initialization was successful, False otherwise
        """
        self.api_key = api_key
        self.search_engine_id = kwargs.get("search_engine_id")
        
        if not self.search_engine_id:
            logger.error("Search engine ID is required for Google Search API")
            return False
        
        logger.info("Google Search API initialized")
        return True
    
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search for data using the Google Custom Search API.
        
        Args:
            query: Search query
            **kwargs: Additional search parameters
                - num: Number of results (default: 10, max: 10)
                - start: Start index (default: 1)
                - site: Site to search within
                - retry_config: Custom retry configuration
                
        Returns:
            List of search results
        """
        num = min(kwargs.get("num", 10), 10)  # Max 10 results per request
        start = kwargs.get("start", 1)
        site = kwargs.get("site")
        retry_config = kwargs.get("retry_config", RetryConfig())
        
        # If site is provided, restrict search to that site
        if site:
            query = f"site:{site} {query}"
        
        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": query,
            "num": num,
            "start": start
        }
        
        @with_retry(config=retry_config)
        def _execute_search() -> List[Dict[str, Any]]:
            with httpx.Client(timeout=retry_config.retry_delay * 2) as client:
                response = client.get(self.base_url, params=params)
                
                if response.status_code != 200:
                    logger.error(f"Google Search API error: {response.status_code}")
                    # Return a dict with status_code so the retry decorator can check it
                    if response.status_code in retry_config.retry_on_status_codes:
                        raise ConnectionError(f"Retryable status code: {response.status_code}")
                    return []
                
                data = response.json()
                
                # Update rate limit info (Google doesn't provide this in headers,
                # so we're just decrementing our counter)
                self.rate_limit_info["remaining"] -= 1
                
                # Extract and format search results
                items = data.get("items", [])
                results = []
                
                for item in items:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "displayLink": item.get("displayLink", ""),
                        "formattedUrl": item.get("formattedUrl", "")
                    })
                
                return results
        
        try:
            return _execute_search()
        except Exception as e:
            logger.error(f"Google Search API request failed after retries: {e}")
            return []
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get the current rate limit status.
        
        Returns:
            Dictionary with rate limit information
        """
        return self.rate_limit_info
    
    async def search_saas_footprint(self, domain: str, saas_tool: str, retry_config: Optional[RetryConfig] = None) -> Dict[str, Any]:
        """
        Search for specific SaaS tool usage on a domain.
        
        Args:
            domain: Domain to search within
            saas_tool: SaaS tool to search for
            retry_config: Custom retry configuration
            
        Returns:
            Dictionary with search results and confidence score
        """
        # SaaS-specific search queries
        queries = {
            'typeform': f'typeform OR "typeform.com" OR "embed.typeform"',
            'klaviyo': f'klaviyo OR "klaviyo.com" OR "a.klaviyo"',
            'hubspot': f'hubspot OR "hs-scripts" OR "hsforms"',
            'shopify_plus': f'"shopify plus" OR "plus.shopify"',
            'recharge': f'recharge OR "rechargepayments"',
            'gorgias': f'gorgias OR "gorgias.com"'
        }
        
        query = queries.get(saas_tool.lower())
        if not query:
            return {'found': False, 'confidence': 0.0}
        
        # Add site restriction
        query = f"site:{domain} {query}"
        
        params = {
            'key': self.api_key,
            'cx': self.search_engine_id,
            'q': query,
            'num': 3  # Only need few results to confirm
        }
        
        config = retry_config or RetryConfig(
            max_retries=3,
            retry_delay=1.0,
            backoff_factor=2.0
        )
        
        async def _execute_search() -> Dict[str, Any]:
            async with httpx.AsyncClient(timeout=config.retry_delay * 2) as client:
                response = await client.get(self.base_url, params=params)
                
                if response.status_code != 200:
                    if response.status_code in config.retry_on_status_codes:
                        raise ConnectionError(f"Retryable status code: {response.status_code}")
                    return {'found': False, 'confidence': 0.0, 'error': response.status_code}
                
                data = response.json()
                items = data.get('items', [])
                
                # Update rate limit info
                self.rate_limit_info["remaining"] -= 1
                
                # Analyze results
                confidence = min(len(items) * 0.4, 1.0)  # More results = higher confidence
                
                evidence = []
                for item in items:
                    title = item.get('title', '')
                    snippet = item.get('snippet', '')
                    evidence.append({
                        'title': title,
                        'snippet': snippet,
                        'url': item.get('link', '')
                    })
                
                return {
                    'found': len(items) > 0,
                    'confidence': confidence,
                    'evidence_count': len(items),
                    'evidence': evidence
                }
        
        try:
            return await with_retry_async(_execute_search, config=config)
        except Exception as e:
            logger.error(f"SaaS footprint search failed after retries: {e}")
            return {'found': False, 'confidence': 0.0, 'error': str(e)}


class GooglePageSpeedAPI(APIClientInterface):
    """Google PageSpeed Insights API integration for ARCO."""
    
    def __init__(self):
        """Initialize the Google PageSpeed API integration."""
        self.api_key = None
        self.base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        self.rate_limit_info = {
            "limit": 25000,  # Default daily limit for free tier
            "remaining": 25000,
            "reset": None
        }
    
    def initialize(self, api_key: str, **kwargs) -> bool:
        """
        Initialize the Google PageSpeed API integration with credentials.
        
        Args:
            api_key: API key for authentication
            **kwargs: Additional configuration parameters
            
        Returns:
            True if initialization was successful, False otherwise
        """
        self.api_key = api_key
        logger.info("Google PageSpeed API initialized")
        return True
    
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Not applicable for PageSpeed API.
        
        Args:
            query: Search query
            **kwargs: Additional search parameters
            
        Returns:
            Empty list as this method is not applicable
        """
        logger.warning("Search method is not applicable for PageSpeed API")
        return []
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get the current rate limit status.
        
        Returns:
            Dictionary with rate limit information
        """
        return self.rate_limit_info
    
    def analyze_url(self, url: str, strategy: str = "mobile", retry_config: Optional[RetryConfig] = None) -> Dict[str, Any]:
        """
        Analyze a URL using Google PageSpeed Insights API.
        
        Args:
            url: URL to analyze
            strategy: Analysis strategy ("mobile" or "desktop")
            retry_config: Custom retry configuration
            
        Returns:
            Dictionary with PageSpeed analysis results
        """
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        params = {
            "url": url,
            "key": self.api_key,
            "strategy": strategy
        }
        
        config = retry_config or RetryConfig(
            max_retries=3,
            retry_delay=2.0,
            backoff_factor=2.0
        )
        
        @with_retry(config=config)
        def _execute_analysis() -> Dict[str, Any]:
            with httpx.Client(timeout=config.retry_delay * 5) as client:
                response = client.get(self.base_url, params=params)
                
                if response.status_code != 200:
                    logger.error(f"PageSpeed API error: {response.status_code}")
                    if response.status_code in config.retry_on_status_codes:
                        raise ConnectionError(f"Retryable status code: {response.status_code}")
                    return {"error": f"API error: {response.status_code}"}
                
                data = response.json()
                
                # Update rate limit info
                self.rate_limit_info["remaining"] -= 1
                
                # Extract key metrics
                lighthouse_result = data.get("lighthouseResult", {})
                categories = lighthouse_result.get("categories", {})
                performance = categories.get("performance", {})
                
                # Extract audits
                audits = lighthouse_result.get("audits", {})
                
                # Extract key performance metrics
                metrics = {}
                for metric_key in ["first-contentful-paint", "largest-contentful-paint", 
                                  "total-blocking-time", "cumulative-layout-shift",
                                  "speed-index", "interactive"]:
                    if metric_key in audits:
                        metrics[metric_key] = {
                            "score": audits[metric_key].get("score"),
                            "value": audits[metric_key].get("numericValue"),
                            "display_value": audits[metric_key].get("displayValue")
                        }
                
                return {
                    "performance_score": performance.get("score", 0) * 100,
                    "metrics": metrics,
                    "strategy": strategy,
                    "analyzed_url": url
                }
        
        try:
            return _execute_analysis()
        except Exception as e:
            logger.error(f"PageSpeed API request failed after retries: {e}")
            return {"error": str(e)}
    
    async def analyze_url_async(self, url: str, strategy: str = "mobile", retry_config: Optional[RetryConfig] = None) -> Dict[str, Any]:
        """
        Analyze a URL using Google PageSpeed Insights API asynchronously.
        
        Args:
            url: URL to analyze
            strategy: Analysis strategy ("mobile" or "desktop")
            retry_config: Custom retry configuration
            
        Returns:
            Dictionary with PageSpeed analysis results
        """
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        params = {
            "url": url,
            "key": self.api_key,
            "strategy": strategy
        }
        
        config = retry_config or RetryConfig(
            max_retries=3,
            retry_delay=2.0,
            backoff_factor=2.0
        )
        
        async def _execute_analysis() -> Dict[str, Any]:
            async with httpx.AsyncClient(timeout=config.retry_delay * 5) as client:
                response = await client.get(self.base_url, params=params)
                
                if response.status_code != 200:
                    logger.error(f"PageSpeed API error: {response.status_code}")
                    if response.status_code in config.retry_on_status_codes:
                        raise ConnectionError(f"Retryable status code: {response.status_code}")
                    return {"error": f"API error: {response.status_code}"}
                
                data = response.json()
                
                # Update rate limit info
                self.rate_limit_info["remaining"] -= 1
                
                # Extract key metrics
                lighthouse_result = data.get("lighthouseResult", {})
                categories = lighthouse_result.get("categories", {})
                performance = categories.get("performance", {})
                
                # Extract audits
                audits = lighthouse_result.get("audits", {})
                
                # Extract key performance metrics
                metrics = {}
                for metric_key in ["first-contentful-paint", "largest-contentful-paint", 
                                  "total-blocking-time", "cumulative-layout-shift",
                                  "speed-index", "interactive"]:
                    if metric_key in audits:
                        metrics[metric_key] = {
                            "score": audits[metric_key].get("score"),
                            "value": audits[metric_key].get("numericValue"),
                            "display_value": audits[metric_key].get("displayValue")
                        }
                
                return {
                    "performance_score": performance.get("score", 0) * 100,
                    "metrics": metrics,
                    "strategy": strategy,
                    "analyzed_url": url
                }
        
        try:
            return await with_retry_async(_execute_analysis, config=config)
        except Exception as e:
            logger.error(f"PageSpeed API request failed after retries: {e}")
            return {"error": str(e)}
    
    def calculate_performance_loss(self, performance_score: float, estimated_revenue: float) -> Dict[str, Any]:
        """
        Calculate estimated revenue loss due to poor performance.
        
        Args:
            performance_score: PageSpeed performance score (0-100)
            estimated_revenue: Estimated monthly revenue in dollars
            
        Returns:
            Dictionary with performance loss calculations
        """
        # Research shows that a 1-second delay in page load time can result in:
        # - 7% reduction in conversions
        # - 11% fewer page views
        # - 16% decrease in customer satisfaction
        
        # We'll use a simplified model based on these findings
        if performance_score >= 90:
            # Excellent performance, minimal loss
            conversion_impact = 0.01  # 1%
        elif performance_score >= 70:
            # Good performance, small loss
            conversion_impact = 0.03  # 3%
        elif performance_score >= 50:
            # Average performance, moderate loss
            conversion_impact = 0.07  # 7%
        elif performance_score >= 30:
            # Poor performance, significant loss
            conversion_impact = 0.11  # 11%
        else:
            # Very poor performance, severe loss
            conversion_impact = 0.16  # 16%
        
        monthly_loss = estimated_revenue * conversion_impact
        annual_loss = monthly_loss * 12
        
        return {
            "performance_score": performance_score,
            "conversion_impact_percentage": conversion_impact * 100,
            "estimated_monthly_loss": monthly_loss,
            "estimated_annual_loss": annual_loss,
            "estimated_monthly_revenue": estimated_revenue
        }