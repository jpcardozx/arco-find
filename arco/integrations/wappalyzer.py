"""
Wappalyzer Integration for ARCO.

This module provides integration with Wappalyzer for technology stack detection.
It supports both the Python Wappalyzer library and the Wappalyzer CLI.
"""

import json
import logging
import subprocess
import asyncio
from typing import Dict, List, Any, Optional
import httpx

from arco.integrations.base import APIClientInterface
from arco.utils.retry import RetryConfig, with_retry, with_retry_async, FallbackChain

logger = logging.getLogger(__name__)

class WappalyzerIntegration(APIClientInterface):
    """Integration with Wappalyzer for technology stack detection."""
    
    def __init__(self):
        """Initialize the Wappalyzer integration."""
        self.api_key = None
        self.wappalyzer_cli_available = False
        self.wappalyzer_py_available = False
        self._check_wappalyzer_availability()
    
    def _check_wappalyzer_availability(self) -> None:
        """Check if Wappalyzer CLI or Python library is available."""
        # Check CLI availability
        try:
            result = subprocess.run(
                ["wappalyzer", "--version"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                timeout=2
            )
            if result.returncode == 0:
                self.wappalyzer_cli_available = True
                logger.info("Wappalyzer CLI is available")
            else:
                logger.warning("Wappalyzer CLI check failed")
        except (FileNotFoundError, subprocess.SubprocessError):
            logger.warning("Wappalyzer CLI not found")
        
        # Check Python library availability
        try:
            from Wappalyzer import Wappalyzer
            self.wappalyzer_py_available = True
            logger.info("Python Wappalyzer library is available")
        except ImportError:
            logger.warning("Python Wappalyzer library not found")
    
    def initialize(self, api_key: str, **kwargs) -> bool:
        """
        Initialize the Wappalyzer integration with credentials.
        
        Args:
            api_key: API key for authentication (not used for local Wappalyzer)
            **kwargs: Additional configuration parameters
            
        Returns:
            True if initialization was successful, False otherwise
        """
        self.api_key = api_key
        
        if not self.wappalyzer_cli_available and not self.wappalyzer_py_available:
            logger.error("Neither Wappalyzer CLI nor Python library is available")
            return False
        
        return True
    
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Not applicable for Wappalyzer integration.
        
        Args:
            query: Search query
            **kwargs: Additional search parameters
            
        Returns:
            Empty list as this method is not applicable
        """
        logger.warning("Search method is not applicable for Wappalyzer integration")
        return []
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get the current rate limit status.
        
        Returns:
            Dictionary with rate limit information
        """
        # Local Wappalyzer has no rate limits
        return {
            "limit": "unlimited",
            "remaining": "unlimited",
            "reset": None
        }
    
    async def analyze_url(self, url: str, timeout: int = 15, retry_config: Optional[RetryConfig] = None) -> Dict[str, Any]:
        """
        Analyze a URL using Wappalyzer.
        
        Args:
            url: URL to analyze
            timeout: Timeout in seconds
            retry_config: Custom retry configuration
            
        Returns:
            Dictionary with detected technologies
        """
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        # Create a fallback chain with available methods
        fallback_methods = []
        
        # Add CLI method if available
        if self.wappalyzer_cli_available:
            fallback_methods.append(lambda: self._analyze_with_cli(url, timeout))
        
        # Add Python library method if available
        if self.wappalyzer_py_available:
            fallback_methods.append(lambda: self._analyze_with_py_lib(url, timeout))
        
        # Always add HTTP fallback as the last resort
        fallback_methods.append(lambda: self._analyze_with_http_fallback(url, timeout))
        
        # Create and execute the fallback chain
        fallback_chain = FallbackChain(fallback_methods)
        
        try:
            return await fallback_chain.execute_async()
        except Exception as e:
            logger.error(f"All Wappalyzer analysis methods failed: {e}")
            # Return empty result as a last resort
            return {"technologies": []}
    
    async def _analyze_with_cli(self, url: str, timeout: int) -> Optional[Dict[str, Any]]:
        """
        Analyze a URL using Wappalyzer CLI.
        
        Args:
            url: URL to analyze
            timeout: Timeout in seconds
            
        Returns:
            Dictionary with detected technologies or None if failed
        """
        cmd = f"wappalyzer --urls {url} --format json"
        
        try:
            # Use asyncio to run subprocess with timeout
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            
            if process.returncode == 0:
                wapp_data = json.loads(stdout.decode())
                return self._process_cli_output(wapp_data)
            else:
                logger.warning(f"Wappalyzer CLI failed: {stderr.decode()}")
                return None
        except (asyncio.TimeoutError, json.JSONDecodeError) as e:
            logger.warning(f"Wappalyzer CLI analysis error: {e}")
            return None
    
    def _process_cli_output(self, wapp_data: Dict) -> Dict[str, Any]:
        """
        Process Wappalyzer CLI output.
        
        Args:
            wapp_data: Wappalyzer CLI output data
            
        Returns:
            Processed technology data
        """
        result = {"technologies": []}
        
        # CLI output format is different from Python library
        if isinstance(wapp_data, list) and len(wapp_data) > 0:
            site_data = wapp_data[0]
            technologies = site_data.get("technologies", [])
            
            for tech in technologies:
                result["technologies"].append({
                    "name": tech.get("name", ""),
                    "categories": [cat.get("name", "") for cat in tech.get("categories", [])],
                    "confidence": tech.get("confidence", 0),
                    "version": tech.get("version", "")
                })
        
        return result
    
    async def _analyze_with_py_lib(self, url: str, timeout: int) -> Dict[str, Any]:
        """
        Analyze a URL using Python Wappalyzer library.
        
        Args:
            url: URL to analyze
            timeout: Timeout in seconds
            
        Returns:
            Dictionary with detected technologies
        """
        from Wappalyzer import Wappalyzer, WebPage
        
        wappalyzer = Wappalyzer.latest()
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            webpage = WebPage.new_from_response(response)
            technologies = wappalyzer.analyze(webpage)
            
            result = {"technologies": []}
            
            for tech_name in technologies:
                tech_info = technologies[tech_name]
                result["technologies"].append({
                    "name": tech_name,
                    "categories": tech_info.get("categories", []),
                    "confidence": 100,  # Python library doesn't provide confidence
                    "version": tech_info.get("version", "")
                })
            
            return result
    
    async def _analyze_with_http_fallback(self, url: str, timeout: int) -> Dict[str, Any]:
        """
        Analyze a URL using HTTP fallback method.
        
        This is a simple fallback that checks for common technology signatures
        in the HTML and HTTP headers when Wappalyzer is not available.
        
        Args:
            url: URL to analyze
            timeout: Timeout in seconds
            
        Returns:
            Dictionary with detected technologies
        """
        result = {"technologies": []}
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)
                html = response.text
                headers = response.headers
                
                # Check for common technologies in headers
                server = headers.get("Server", "")
                if "nginx" in server.lower():
                    result["technologies"].append({
                        "name": "Nginx",
                        "categories": ["Web servers"],
                        "confidence": 100,
                        "version": ""
                    })
                elif "apache" in server.lower():
                    result["technologies"].append({
                        "name": "Apache",
                        "categories": ["Web servers"],
                        "confidence": 100,
                        "version": ""
                    })
                
                # Check for common technologies in HTML
                if "wp-content" in html:
                    result["technologies"].append({
                        "name": "WordPress",
                        "categories": ["CMS"],
                        "confidence": 80,
                        "version": ""
                    })
                
                if "shopify" in html.lower():
                    result["technologies"].append({
                        "name": "Shopify",
                        "categories": ["E-commerce"],
                        "confidence": 80,
                        "version": ""
                    })
                
                if "gtag" in html or "google-analytics" in html:
                    result["technologies"].append({
                        "name": "Google Analytics",
                        "categories": ["Analytics"],
                        "confidence": 80,
                        "version": ""
                    })
                
                if "klaviyo" in html.lower():
                    result["technologies"].append({
                        "name": "Klaviyo",
                        "categories": ["Email marketing"],
                        "confidence": 80,
                        "version": ""
                    })
                
                if "hubspot" in html.lower():
                    result["technologies"].append({
                        "name": "HubSpot",
                        "categories": ["CRM"],
                        "confidence": 80,
                        "version": ""
                    })
                
                if "typeform" in html.lower():
                    result["technologies"].append({
                        "name": "Typeform",
                        "categories": ["Forms"],
                        "confidence": 80,
                        "version": ""
                    })
        
        except Exception as e:
            logger.warning(f"HTTP fallback analysis failed: {e}")
        
        return result