#!/usr/bin/env python3
"""
Test script to validate API configurations and limits.
Task 1.2: Validate API configurations and limits
"""

import asyncio
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add arco to path
sys.path.insert(0, str(Path(__file__).parent / "arco"))

from arco.integrations.google_analytics import GoogleAnalyticsIntegration
from arco.integrations.wappalyzer import WappalyzerIntegration

async def test_google_pagespeed_api():
    """Test Google PageSpeed Insights API configuration and limits."""
    print("🧪 Testing Google PageSpeed Insights API...")
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ Google API Key not found in environment variables")
        return False
    
    print(f"✅ Google API Key found: {api_key[:10]}...")
    
    try:
        # Test API with a simple request
        ga_integration = GoogleAnalyticsIntegration(api_key=api_key)
        
        # Test web vitals collection
        web_vitals = await ga_integration.get_web_vitals("google.com")
        
        if web_vitals and web_vitals.lcp:
            print(f"✅ PageSpeed API working: LCP={web_vitals.lcp}s for google.com")
            return True
        else:
            print("❌ PageSpeed API returned no data")
            return False
            
    except Exception as e:
        print(f"❌ PageSpeed API Error: {e}")
        return False

async def test_rate_limiting_behavior():
    """Test rate limiting behavior and backoff strategies."""
    print("\n🧪 Testing Rate Limiting Behavior...")
    
    api_key = os.getenv('GOOGLE_API_KEY')
    requests_per_minute = int(os.getenv('PAGESPEED_REQUESTS_PER_MINUTE', 60))
    
    print(f"📊 Configured rate limit: {requests_per_minute} requests/minute")
    
    try:
        ga_integration = GoogleAnalyticsIntegration(api_key=api_key)
        
        # Test multiple rapid requests to see rate limiting
        test_domains = ["google.com", "github.com", "stackoverflow.com"]
        start_time = time.time()
        
        results = []
        for domain in test_domains:
            try:
                result = await ga_integration.get_web_vitals(domain)
                results.append(f"✅ {domain}: Success")
            except Exception as e:
                if "quota" in str(e).lower() or "rate" in str(e).lower():
                    results.append(f"⚠️ {domain}: Rate limited - {e}")
                else:
                    results.append(f"❌ {domain}: Error - {e}")
        
        elapsed_time = time.time() - start_time
        
        print(f"📊 Processed {len(test_domains)} requests in {elapsed_time:.2f}s")
        for result in results:
            print(f"   {result}")
        
        # Calculate effective rate
        effective_rate = len(test_domains) / (elapsed_time / 60)  # requests per minute
        print(f"📊 Effective rate: {effective_rate:.1f} requests/minute")
        
        return True
        
    except Exception as e:
        print(f"❌ Rate limiting test failed: {e}")
        return False

def test_wappalyzer_integration():
    """Test Wappalyzer integration configuration."""
    print("\n🧪 Testing Wappalyzer Integration...")
    
    try:
        # Check if we can import and initialize Wappalyzer
        wappalyzer = WappalyzerIntegration()
        print("✅ WappalyzerIntegration initialized successfully")
        
        # Test with a simple domain
        result = asyncio.run(wappalyzer.analyze_url("https://shopify.com"))
        
        if result and "technologies" in result:
            tech_count = len(result["technologies"])
            print(f"✅ Wappalyzer working: Found {tech_count} technologies for shopify.com")
            
            # Show first few technologies
            for tech in result["technologies"][:3]:
                print(f"   - {tech.get('name', 'Unknown')}: {tech.get('categories', [])}")
            
            return True
        else:
            print("❌ Wappalyzer returned no technology data")
            return False
            
    except Exception as e:
        print(f"❌ Wappalyzer integration error: {e}")
        return False

def document_api_quotas():
    """Document API quotas and optimal batch sizes."""
    print("\n📋 API Quotas and Batch Size Documentation:")
    
    # Google PageSpeed Insights quotas
    pagespeed_daily = int(os.getenv('PAGESPEED_REQUESTS_PER_DAY', 25000))
    pagespeed_per_minute = int(os.getenv('PAGESPEED_REQUESTS_PER_MINUTE', 60))
    
    print("🔹 Google PageSpeed Insights API:")
    print(f"   - Daily quota: {pagespeed_daily:,} requests")
    print(f"   - Per minute: {pagespeed_per_minute} requests")
    print(f"   - Recommended batch size: {min(10, pagespeed_per_minute // 6)} requests")
    print(f"   - Delay between batches: {60 / pagespeed_per_minute:.1f}s")
    
    # Wappalyzer (HTTP-based, no official limits but be respectful)
    print("\n🔹 Wappalyzer (HTTP Analysis):")
    print("   - No official API limits (HTTP scraping)")
    print("   - Recommended batch size: 5 requests")
    print("   - Delay between batches: 2.0s (respectful crawling)")
    print("   - Timeout per request: 10s")
    
    # Calculate optimal processing for 175 leads
    total_leads = 175
    
    # PageSpeed calculations
    pagespeed_batch_size = min(10, pagespeed_per_minute // 6)
    pagespeed_batches = (total_leads + pagespeed_batch_size - 1) // pagespeed_batch_size
    pagespeed_time = pagespeed_batches * (60 / pagespeed_per_minute) * pagespeed_batch_size
    
    print(f"\n📊 Processing 175 leads:")
    print(f"   - PageSpeed batches: {pagespeed_batches} x {pagespeed_batch_size} requests")
    print(f"   - Estimated PageSpeed time: {pagespeed_time / 60:.1f} minutes")
    print(f"   - Wappalyzer batches: {(total_leads + 4) // 5} x 5 requests")
    print(f"   - Estimated Wappalyzer time: {((total_leads + 4) // 5) * 2 / 60:.1f} minutes")
    
    return {
        "pagespeed": {
            "daily_quota": pagespeed_daily,
            "per_minute": pagespeed_per_minute,
            "batch_size": pagespeed_batch_size,
            "delay": 60 / pagespeed_per_minute
        },
        "wappalyzer": {
            "batch_size": 5,
            "delay": 2.0,
            "timeout": 10
        },
        "processing_estimates": {
            "total_leads": total_leads,
            "pagespeed_time_minutes": pagespeed_time / 60,
            "wappalyzer_time_minutes": ((total_leads + 4) // 5) * 2 / 60
        }
    }

async def test_backoff_strategies():
    """Test exponential backoff strategies."""
    print("\n🧪 Testing Backoff Strategies...")
    
    def calculate_backoff_delay(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
        """Calculate exponential backoff delay."""
        delay = base_delay * (2 ** attempt)
        return min(delay, max_delay)
    
    print("📊 Exponential Backoff Schedule:")
    for attempt in range(6):
        delay = calculate_backoff_delay(attempt)
        print(f"   Attempt {attempt + 1}: {delay:.1f}s delay")
    
    # Test with a mock failure scenario
    print("\n🔄 Simulating retry with backoff:")
    
    async def mock_api_call_with_retry(max_retries: int = 3):
        """Mock API call with retry logic."""
        for attempt in range(max_retries):
            try:
                # Simulate API call (always fails for demo)
                if attempt < 2:  # Fail first 2 attempts
                    raise Exception("Rate limit exceeded")
                else:
                    return "Success"
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    delay = calculate_backoff_delay(attempt)
                    print(f"   Attempt {attempt + 1} failed: {e}")
                    print(f"   Waiting {delay:.1f}s before retry...")
                    await asyncio.sleep(0.1)  # Short delay for demo
                else:
                    print(f"   Final attempt {attempt + 1} failed: {e}")
                    raise
    
    try:
        result = await mock_api_call_with_retry()
        print(f"✅ Retry strategy successful: {result}")
        return True
    except Exception as e:
        print(f"❌ Retry strategy failed: {e}")
        return False

async def main():
    """Run all API configuration tests."""
    print("🚀 Starting API Configuration Validation")
    print("=" * 50)
    
    results = {}
    
    # Test each API configuration
    results['google_pagespeed'] = await test_google_pagespeed_api()
    results['rate_limiting'] = await test_rate_limiting_behavior()
    results['wappalyzer'] = test_wappalyzer_integration()
    results['backoff_strategies'] = await test_backoff_strategies()
    
    # Document quotas and batch sizes
    quota_info = document_api_quotas()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 API Configuration Test Results:")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} API tests passed")
    
    if passed == total:
        print("🎉 All API configurations are working!")
        return True, quota_info
    else:
        print("⚠️ Some API configurations need attention")
        return False, quota_info

if __name__ == "__main__":
    success, quota_info = asyncio.run(main())
    
    # Save quota information for later use
    import json
    with open("api_quota_info.json", "w") as f:
        json.dump(quota_info, f, indent=2)
    
    print(f"\n💾 API quota information saved to api_quota_info.json")
    
    sys.exit(0 if success else 1)