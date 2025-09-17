"""
Test script to validate real Google API integration.
Tests actual PageSpeed Insights API calls with real domains.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the arco directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'arco'))

from arco.integrations.google_analytics import GoogleAnalyticsIntegration
from arco.integrations.google_ads import GoogleAdsIntegration


async def test_real_google_apis():
    """Test real Google API integration with actual domains."""
    print("🔍 TESTING REAL GOOGLE API INTEGRATION")
    print("=" * 60)
    
    # Test domains - mix of fast and slow sites
    test_domains = [
        "google.com",      # Should be very fast
        "github.com",      # Should be fast
        "shopify.com",     # Should be decent
        "wordpress.com",   # Might be slower
        "example.com"      # Simple test site
    ]
    
    # Initialize Google Analytics integration
    print("🚀 Initializing Google Analytics integration...")
    ga_integration = GoogleAnalyticsIntegration()
    
    print(f"✅ API Key configured: {bool(ga_integration.api_key)}")
    print(f"📡 API Key preview: {ga_integration.api_key[:20]}..." if ga_integration.api_key else "❌ No API key")
    print()
    
    # Test web vitals collection for each domain
    print("📊 TESTING WEB VITALS COLLECTION")
    print("-" * 40)
    
    results = []
    
    for i, domain in enumerate(test_domains, 1):
        print(f"\n{i}. Testing {domain}...")
        
        try:
            # Test web vitals
            web_vitals = await ga_integration.get_web_vitals(domain)
            
            if web_vitals:
                print(f"   ✅ Web Vitals collected successfully!")
                print(f"      • LCP: {web_vitals.lcp:.2f}s" if web_vitals.lcp else "      • LCP: N/A")
                print(f"      • FID: {web_vitals.fid:.0f}ms" if web_vitals.fid else "      • FID: N/A")
                print(f"      • CLS: {web_vitals.cls:.3f}" if web_vitals.cls else "      • CLS: N/A")
                print(f"      • TTFB: {web_vitals.ttfb:.0f}ms" if web_vitals.ttfb else "      • TTFB: N/A")
                print(f"      • Source: {web_vitals.data_source}")
                
                results.append({
                    "domain": domain,
                    "success": True,
                    "lcp": web_vitals.lcp,
                    "cls": web_vitals.cls,
                    "data_source": web_vitals.data_source
                })
            else:
                print(f"   ❌ Failed to collect web vitals")
                results.append({
                    "domain": domain,
                    "success": False,
                    "error": "No data returned"
                })
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                "domain": domain,
                "success": False,
                "error": str(e)
            })
    
    # Test conversion metrics
    print(f"\n📈 TESTING CONVERSION METRICS ESTIMATION")
    print("-" * 40)
    
    for i, domain in enumerate(test_domains[:3], 1):  # Test first 3 domains
        print(f"\n{i}. Testing conversion metrics for {domain}...")
        
        try:
            conversion_metrics = await ga_integration.get_conversion_metrics(domain)
            
            if conversion_metrics:
                print(f"   ✅ Conversion metrics estimated!")
                print(f"      • Bounce Rate: {conversion_metrics.get('bounce_rate', 0):.1%}")
                print(f"      • Conversion Rate: {conversion_metrics.get('conversion_rate', 0):.2%}")
                print(f"      • Avg Session Duration: {conversion_metrics.get('avg_session_duration', 0):.0f}s")
                print(f"      • Performance Penalty: {conversion_metrics.get('performance_penalty', 0):.1%}")
            else:
                print(f"   ❌ Failed to get conversion metrics")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test traffic source analysis
    print(f"\n🚦 TESTING TRAFFIC SOURCE ANALYSIS")
    print("-" * 40)
    
    for i, domain in enumerate(test_domains[:2], 1):  # Test first 2 domains
        print(f"\n{i}. Testing traffic sources for {domain}...")
        
        try:
            traffic_sources = await ga_integration.get_traffic_sources(domain)
            
            if traffic_sources:
                print(f"   ✅ Traffic sources analyzed!")
                print(f"      • Organic Search: {traffic_sources.get('organic_search', 0):.1%}")
                print(f"      • Paid Search: {traffic_sources.get('paid_search', 0):.1%}")
                print(f"      • Direct: {traffic_sources.get('direct', 0):.1%}")
                print(f"      • Social: {traffic_sources.get('social', 0):.1%}")
                print(f"      • Confidence: {traffic_sources.get('confidence_score', 0):.2f}")
            else:
                print(f"   ❌ Failed to analyze traffic sources")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Summary
    print(f"\n📋 TEST SUMMARY")
    print("=" * 60)
    
    successful_tests = len([r for r in results if r.get("success")])
    total_tests = len(results)
    
    print(f"✅ Successful API calls: {successful_tests}/{total_tests}")
    print(f"📊 Success rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests > 0:
        print(f"\n🎯 REAL DATA COLLECTED:")
        for result in results:
            if result.get("success"):
                domain = result["domain"]
                lcp = result.get("lcp")
                print(f"   • {domain}: LCP={lcp:.2f}s" if lcp else f"   • {domain}: Data collected")
    
    if successful_tests >= total_tests * 0.6:  # 60% success rate
        print(f"\n✅ GOOGLE API INTEGRATION IS WORKING!")
        print(f"🚀 Ready to use real marketing data in workflow")
    else:
        print(f"\n⚠️ API integration needs attention")
        print(f"🔧 Check API key and rate limits")
    
    # Close session
    if ga_integration.session and not ga_integration.session.closed:
        await ga_integration.session.close()
    
    return results


if __name__ == "__main__":
    # Run the real API test
    results = asyncio.run(test_real_google_apis())
    
    print(f"\n✅ Real API integration test completed!")
    print(f"📊 Results: {len([r for r in results if r.get('success')])} successful API calls")