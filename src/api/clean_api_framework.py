#!/usr/bin/env python3
"""
🔌 CLEAN API CONNECTION FRAMEWORK
Real API connections to Meta Ads and Google Ads Libraries
No mock data - proper error handling and fallbacks
"""

import os
import logging
import requests
import json
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)


@dataclass
class APICredentials:
    """Clean API credentials management"""
    meta_access_token: Optional[str] = None
    google_api_key: Optional[str] = None
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    
    def __post_init__(self):
        # Load from environment variables if not provided
        if not self.meta_access_token:
            self.meta_access_token = os.getenv('META_ACCESS_TOKEN')
        if not self.google_api_key:
            self.google_api_key = os.getenv('GOOGLE_API_KEY')
        if not self.google_client_id:
            self.google_client_id = os.getenv('GOOGLE_CLIENT_ID')
        if not self.google_client_secret:
            self.google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')


@dataclass
class APIResponse:
    """Standard API response format"""
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    rate_limited: bool = False
    from_cache: bool = False


class APIRateLimiter:
    """Simple rate limiting to respect API limits"""
    
    def __init__(self):
        self.last_calls = {}
        self.call_counts = {}
    
    def can_make_call(self, api_name: str, calls_per_minute: int = 60) -> bool:
        """Check if we can make an API call within rate limits"""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old calls
        if api_name in self.last_calls:
            self.last_calls[api_name] = [
                call_time for call_time in self.last_calls[api_name]
                if call_time > minute_ago
            ]
        else:
            self.last_calls[api_name] = []
        
        return len(self.last_calls[api_name]) < calls_per_minute
    
    def record_call(self, api_name: str):
        """Record an API call"""
        if api_name not in self.last_calls:
            self.last_calls[api_name] = []
        self.last_calls[api_name].append(datetime.now())


class MetaAdsAPIClient:
    """Clean Meta Ads API client with proper error handling"""
    
    def __init__(self, credentials: APICredentials):
        self.credentials = credentials
        self.base_url = "https://graph.facebook.com/v18.0"
        self.rate_limiter = APIRateLimiter()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ArcoFind/1.0 Lead Intelligence Platform'
        })
    
    def test_connection(self) -> APIResponse:
        """Test API connection and authentication"""
        if not self.credentials.meta_access_token:
            return APIResponse(
                success=False,
                error="No Meta access token provided"
            )
        
        try:
            if not self.rate_limiter.can_make_call('meta_test'):
                return APIResponse(
                    success=False,
                    error="Rate limit exceeded",
                    rate_limited=True
                )
            
            url = f"{self.base_url}/me"
            params = {
                'access_token': self.credentials.meta_access_token,
                'fields': 'id,name'
            }
            
            response = self.session.get(url, params=params, timeout=15)
            self.rate_limiter.record_call('meta_test')
            
            if response.status_code == 200:
                data = response.json()
                return APIResponse(
                    success=True,
                    data={
                        'user_id': data.get('id'),
                        'user_name': data.get('name'),
                        'api_version': 'v18.0',
                        'connection_status': 'authenticated'
                    },
                    status_code=response.status_code
                )
            else:
                error_data = response.json() if response.content else {}
                return APIResponse(
                    success=False,
                    error=error_data.get('error', {}).get('message', 'Authentication failed'),
                    status_code=response.status_code
                )
                
        except requests.exceptions.Timeout:
            return APIResponse(
                success=False,
                error="API request timeout"
            )
        except requests.exceptions.ConnectionError:
            return APIResponse(
                success=False,
                error="Unable to connect to Meta API - network or DNS issue"
            )
        except Exception as e:
            return APIResponse(
                success=False,
                error=f"Unexpected error: {str(e)}"
            )
    
    def search_ads_library(self, search_terms: str, country_codes: List[str], 
                          limit: int = 25) -> APIResponse:
        """Search Meta Ads Library for active ads"""
        if not self.credentials.meta_access_token:
            return APIResponse(
                success=False,
                error="No Meta access token provided"
            )
        
        try:
            if not self.rate_limiter.can_make_call('meta_ads_library', 200):  # Higher limit for ads library
                return APIResponse(
                    success=False,
                    error="Rate limit exceeded for ads library",
                    rate_limited=True
                )
            
            url = f"{self.base_url}/ads_archive"
            params = {
                'access_token': self.credentials.meta_access_token,
                'search_terms': search_terms,
                'ad_reached_countries': country_codes,
                'ad_active_status': 'ACTIVE',
                'limit': min(limit, 1000),  # Meta's max
                'fields': 'id,page_name,page_id,ad_delivery_start_time,spend,impressions,currency'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            self.rate_limiter.record_call('meta_ads_library')
            
            if response.status_code == 200:
                data = response.json()
                return APIResponse(
                    success=True,
                    data={
                        'ads': data.get('data', []),
                        'total_found': len(data.get('data', [])),
                        'search_terms': search_terms,
                        'countries': country_codes,
                        'timestamp': datetime.now().isoformat()
                    },
                    status_code=response.status_code
                )
            else:
                error_data = response.json() if response.content else {}
                error_info = error_data.get('error', {})
                
                # Handle specific Meta API errors
                if error_info.get('code') == 10 and error_info.get('error_subcode') == 2332002:
                    return APIResponse(
                        success=False,
                        error="Ads Library access requires additional permissions",
                        status_code=response.status_code
                    )
                
                return APIResponse(
                    success=False,
                    error=error_info.get('message', 'Ads Library search failed'),
                    status_code=response.status_code
                )
                
        except requests.exceptions.Timeout:
            return APIResponse(
                success=False,
                error="Ads Library request timeout"
            )
        except Exception as e:
            return APIResponse(
                success=False,
                error=f"Ads Library search error: {str(e)}"
            )
    
    def get_page_info(self, page_id: str) -> APIResponse:
        """Get Meta page information"""
        if not self.credentials.meta_access_token:
            return APIResponse(
                success=False,
                error="No Meta access token provided"
            )
        
        try:
            if not self.rate_limiter.can_make_call('meta_page_info'):
                return APIResponse(
                    success=False,
                    error="Rate limit exceeded",
                    rate_limited=True
                )
            
            url = f"{self.base_url}/{page_id}"
            params = {
                'access_token': self.credentials.meta_access_token,
                'fields': 'id,name,category,website,followers_count,fan_count'
            }
            
            response = self.session.get(url, params=params, timeout=15)
            self.rate_limiter.record_call('meta_page_info')
            
            if response.status_code == 200:
                data = response.json()
                return APIResponse(
                    success=True,
                    data=data,
                    status_code=response.status_code
                )
            else:
                error_data = response.json() if response.content else {}
                return APIResponse(
                    success=False,
                    error=error_data.get('error', {}).get('message', 'Page info failed'),
                    status_code=response.status_code
                )
                
        except Exception as e:
            return APIResponse(
                success=False,
                error=f"Page info error: {str(e)}"
            )


class GoogleAdsAPIClient:
    """Clean Google Ads API client"""
    
    def __init__(self, credentials: APICredentials):
        self.credentials = credentials
        self.rate_limiter = APIRateLimiter()
        self.session = requests.Session()
    
    def test_connection(self) -> APIResponse:
        """Test Google API connection"""
        if not self.credentials.google_api_key:
            return APIResponse(
                success=False,
                error="No Google API key provided"
            )
        
        try:
            # Test with a simple API call (Places API or similar)
            # This is a placeholder - would need specific Google Ads API setup
            return APIResponse(
                success=False,
                error="Google Ads API integration requires OAuth setup - not implemented yet"
            )
            
        except Exception as e:
            return APIResponse(
                success=False,
                error=f"Google API error: {str(e)}"
            )


class UnifiedAPIClient:
    """Unified client for both Meta and Google APIs"""
    
    def __init__(self, credentials: APICredentials = None):
        if credentials is None:
            credentials = APICredentials()
        
        self.credentials = credentials
        self.meta_client = MetaAdsAPIClient(credentials)
        self.google_client = GoogleAdsAPIClient(credentials)
        
        # Simple in-memory cache
        self.cache = {}
        self.cache_ttl = timedelta(minutes=30)
    
    def test_all_connections(self) -> Dict[str, APIResponse]:
        """Test all API connections"""
        logger.info("Testing API connections...")
        
        results = {
            'meta': self.meta_client.test_connection(),
            'google': self.google_client.test_connection()
        }
        
        # Log results
        for api_name, response in results.items():
            if response.success:
                logger.info(f"✅ {api_name.upper()} API: Connected")
                if response.data:
                    logger.info(f"   User: {response.data.get('user_name', 'N/A')}")
            else:
                logger.warning(f"❌ {api_name.upper()} API: {response.error}")
        
        return results
    
    def search_company_ads(self, industry_keywords: List[str], 
                          countries: List[str], limit: int = 50) -> Dict[str, APIResponse]:
        """Search for company ads across both platforms"""
        results = {}
        
        # Try Meta first
        for keyword in industry_keywords:
            cache_key = f"meta_ads_{keyword}_{'_'.join(countries)}"
            
            # Check cache first
            if cache_key in self.cache:
                cached_data, cached_time = self.cache[cache_key]
                if datetime.now() - cached_time < self.cache_ttl:
                    results[f"meta_{keyword}"] = APIResponse(
                        success=True,
                        data=cached_data,
                        from_cache=True
                    )
                    continue
            
            # Make API call
            response = self.meta_client.search_ads_library(keyword, countries, limit)
            results[f"meta_{keyword}"] = response
            
            # Cache successful responses
            if response.success and response.data:
                self.cache[cache_key] = (response.data, datetime.now())
        
        # Google Ads would go here when implemented
        # results['google'] = self.google_client.search_ads(...)
        
        return results
    
    def get_comprehensive_company_data(self, company_identifiers: Dict) -> Dict:
        """Get comprehensive company data from multiple sources"""
        data = {
            'company_name': company_identifiers.get('name', 'Unknown'),
            'sources': [],
            'meta_data': None,
            'google_data': None,
            'last_updated': datetime.now().isoformat()
        }
        
        # Get Meta data if page_id available
        if 'meta_page_id' in company_identifiers:
            meta_response = self.meta_client.get_page_info(company_identifiers['meta_page_id'])
            if meta_response.success:
                data['meta_data'] = meta_response.data
                data['sources'].append('meta')
        
        # Google data would go here when implemented
        
        return data


def demo_clean_api_framework():
    """Demo the clean API framework"""
    print("🔌 CLEAN API CONNECTION FRAMEWORK DEMO")
    print("=" * 45)
    
    # Initialize with environment credentials
    credentials = APICredentials()
    api_client = UnifiedAPIClient(credentials)
    
    print("\n🔍 TESTING API CONNECTIONS...")
    connection_results = api_client.test_all_connections()
    
    for api_name, response in connection_results.items():
        print(f"\n{api_name.upper()} API:")
        print(f"  Status: {'✅ Connected' if response.success else '❌ Failed'}")
        if response.error:
            print(f"  Error: {response.error}")
        if response.data:
            print(f"  User: {response.data.get('user_name', 'N/A')}")
            print(f"  ID: {response.data.get('user_id', 'N/A')}")
    
    print("\n🔍 TESTING ADS SEARCH...")
    search_results = api_client.search_company_ads(
        industry_keywords=['dental', 'dentist'],
        countries=['DE', 'NL'],
        limit=10
    )
    
    for search_key, response in search_results.items():
        print(f"\n{search_key}:")
        print(f"  Success: {'✅' if response.success else '❌'}")
        if response.from_cache:
            print(f"  Source: 📋 Cache")
        if response.success and response.data:
            print(f"  Ads found: {response.data.get('total_found', 0)}")
        elif response.error:
            print(f"  Error: {response.error}")
    
    print("\n✅ CLEAN API FRAMEWORK DEMO COMPLETE")
    print("✅ PROPER ERROR HANDLING")
    print("✅ RATE LIMITING IMPLEMENTED")
    print("✅ CACHING FOR EFFICIENCY")
    print("✅ NO MOCK DATA OR AI DELUSION")


if __name__ == "__main__":
    demo_clean_api_framework()