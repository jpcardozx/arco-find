#!/usr/bin/env python3
"""
Test script for enhanced performance impact leak detection.

This script tests the _analyze_performance_impact method to ensure it properly
detects web vitals issues and calculates conversion losses based on industry benchmarks.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from arco.engines.leak_engine import LeakEngine
from arco.models.prospect import Prospect, MarketingData, WebVitals
from arco.models.qualified_prospect import MarketingLeak

async def test_performance_impact_detection():
    """Test the enhanced performance impact leak detection."""
    
    print("🧪 Testing Enhanced Performance Impact Leak Detection")
    print("=" * 60)
    
    # Initialize the leak engine
    engine = LeakEngine()
    
    # Test Case 1: Poor LCP (Largest Contentful Paint)
    print("\n📊 Test Case 1: Poor LCP Performance")
    prospect1 = Prospect(
        domain="slow-site.com",
        company_name="Slow Loading Co",
        industry="ecommerce",
        employee_count=25,
        revenue=2000000
    )
    
    # Create marketing data with poor LCP
    marketing_data1 = MarketingData(
        web_vitals=WebVitals(
            lcp=4.2,  # Poor LCP (>2.5s)
            fid=80,   # Good FID
            cls=0.05, # Good CLS
            ttfb=400, # Good TTFB
            data_source="pagespeed"
        ),
        conversion_rate=0.025,
        data_confidence=0.8
    )
    prospect1.marketing_data = marketing_data1
    
    # Get industry benchmarks
    benchmarks = engine.marketing_benchmarks.get('industries', {}).get('ecommerce', {})
    
    # Test performance impact analysis
    performance_leaks = engine._analyze_performance_impact(prospect1, marketing_data1, benchmarks)
    
    print(f"   Domain: {prospect1.domain}")
    print(f"   LCP: {marketing_data1.web_vitals.lcp}s (threshold: 2.5s)")
    print(f"   Performance leaks detected: {len(performance_leaks)}")
    
    for leak in performance_leaks:
        print(f"   - Type: {leak.type}")
        print(f"   - Monthly waste: ${leak.monthly_waste:.2f}")
        print(f"   - Description: {leak.description}")
        print(f"   - Recommendation: {leak.technical_recommendation}")
    
    # Test Case 2: Poor FID (First Input Delay)
    print("\n📊 Test Case 2: Poor FID Performance")
    prospect2 = Prospect(
        domain="slow-interaction.com",
        company_name="Slow Interaction Co",
        industry="saas",
        employee_count=50,
        revenue=5000000
    )
    
    marketing_data2 = MarketingData(
        web_vitals=WebVitals(
            lcp=2.0,   # Good LCP
            fid=250,   # Poor FID (>100ms)
            cls=0.08,  # Good CLS
            ttfb=500,  # Good TTFB
            data_source="lighthouse"
        ),
        conversion_rate=0.035,
        data_confidence=0.9
    )
    prospect2.marketing_data = marketing_data2
    
    benchmarks2 = engine.marketing_benchmarks.get('industries', {}).get('saas', {})
    performance_leaks2 = engine._analyze_performance_impact(prospect2, marketing_data2, benchmarks2)
    
    print(f"   Domain: {prospect2.domain}")
    print(f"   FID: {marketing_data2.web_vitals.fid}ms (threshold: 100ms)")
    print(f"   Performance leaks detected: {len(performance_leaks2)}")
    
    for leak in performance_leaks2:
        print(f"   - Type: {leak.type}")
        print(f"   - Monthly waste: ${leak.monthly_waste:.2f}")
        print(f"   - Description: {leak.description}")
        print(f"   - Recommendation: {leak.technical_recommendation}")
    
    # Test Case 3: Poor CLS (Cumulative Layout Shift)
    print("\n📊 Test Case 3: Poor CLS Performance")
    prospect3 = Prospect(
        domain="layout-shifts.com",
        company_name="Layout Shift Co",
        industry="retail",
        employee_count=15,
        revenue=1500000
    )
    
    marketing_data3 = MarketingData(
        web_vitals=WebVitals(
            lcp=2.2,   # Good LCP
            fid=90,    # Good FID
            cls=0.35,  # Poor CLS (>0.1)
            ttfb=450,  # Good TTFB
            data_source="crux"
        ),
        conversion_rate=0.028,
        data_confidence=0.7
    )
    prospect3.marketing_data = marketing_data3
    
    benchmarks3 = engine.marketing_benchmarks.get('industries', {}).get('retail', {})
    performance_leaks3 = engine._analyze_performance_impact(prospect3, marketing_data3, benchmarks3)
    
    print(f"   Domain: {prospect3.domain}")
    print(f"   CLS: {marketing_data3.web_vitals.cls} (threshold: 0.1)")
    print(f"   Performance leaks detected: {len(performance_leaks3)}")
    
    for leak in performance_leaks3:
        print(f"   - Type: {leak.type}")
        print(f"   - Monthly waste: ${leak.monthly_waste:.2f}")
        print(f"   - Description: {leak.description}")
        print(f"   - Recommendation: {leak.technical_recommendation}")
    
    # Test Case 4: Poor TTFB (Time to First Byte)
    print("\n📊 Test Case 4: Poor TTFB Performance")
    prospect4 = Prospect(
        domain="slow-server.com",
        company_name="Slow Server Co",
        industry="ecommerce",
        employee_count=100,
        revenue=10000000
    )
    
    marketing_data4 = MarketingData(
        web_vitals=WebVitals(
            lcp=2.3,    # Good LCP
            fid=85,     # Good FID
            cls=0.08,   # Good CLS
            ttfb=1200,  # Poor TTFB (>600ms)
            data_source="pagespeed"
        ),
        conversion_rate=0.030,
        data_confidence=0.85
    )
    prospect4.marketing_data = marketing_data4
    
    benchmarks4 = engine.marketing_benchmarks.get('industries', {}).get('ecommerce', {})
    performance_leaks4 = engine._analyze_performance_impact(prospect4, marketing_data4, benchmarks4)
    
    print(f"   Domain: {prospect4.domain}")
    print(f"   TTFB: {marketing_data4.web_vitals.ttfb}ms (threshold: 600ms)")
    print(f"   Performance leaks detected: {len(performance_leaks4)}")
    
    for leak in performance_leaks4:
        print(f"   - Type: {leak.type}")
        print(f"   - Monthly waste: ${leak.monthly_waste:.2f}")
        print(f"   - Description: {leak.description}")
        print(f"   - Recommendation: {leak.technical_recommendation}")
    
    # Test Case 5: Multiple Performance Issues
    print("\n📊 Test Case 5: Multiple Performance Issues")
    prospect5 = Prospect(
        domain="multiple-issues.com",
        company_name="Multiple Issues Co",
        industry="saas",
        employee_count=200,
        revenue=25000000
    )
    
    marketing_data5 = MarketingData(
        web_vitals=WebVitals(
            lcp=5.1,    # Very poor LCP
            fid=350,    # Very poor FID
            cls=0.28,   # Poor CLS
            ttfb=1500,  # Very poor TTFB
            data_source="lighthouse"
        ),
        conversion_rate=0.040,
        data_confidence=0.95
    )
    # Add performance score dynamically (as done in the enrichment process)
    marketing_data5.performance_score = 25  # Very poor overall score
    prospect5.marketing_data = marketing_data5
    
    benchmarks5 = engine.marketing_benchmarks.get('industries', {}).get('saas', {})
    performance_leaks5 = engine._analyze_performance_impact(prospect5, marketing_data5, benchmarks5)
    
    print(f"   Domain: {prospect5.domain}")
    print(f"   LCP: {marketing_data5.web_vitals.lcp}s, FID: {marketing_data5.web_vitals.fid}ms")
    print(f"   CLS: {marketing_data5.web_vitals.cls}, TTFB: {marketing_data5.web_vitals.ttfb}ms")
    print(f"   Overall Performance Score: {marketing_data5.performance_score}/100")
    print(f"   Performance leaks detected: {len(performance_leaks5)}")
    
    total_monthly_waste = 0
    for leak in performance_leaks5:
        print(f"   - Type: {leak.type}")
        print(f"   - Monthly waste: ${leak.monthly_waste:.2f}")
        print(f"   - Severity: {leak.severity}")
        print(f"   - Description: {leak.description}")
        total_monthly_waste += leak.monthly_waste
    
    print(f"   📈 Total Monthly Performance Waste: ${total_monthly_waste:.2f}")
    print(f"   📈 Total Annual Performance Waste: ${total_monthly_waste * 12:.2f}")
    
    # Test Case 6: Good Performance (No Leaks)
    print("\n📊 Test Case 6: Good Performance (No Leaks Expected)")
    prospect6 = Prospect(
        domain="fast-site.com",
        company_name="Fast Site Co",
        industry="ecommerce",
        employee_count=30,
        revenue=3000000
    )
    
    marketing_data6 = MarketingData(
        web_vitals=WebVitals(
            lcp=1.8,   # Excellent LCP
            fid=65,    # Excellent FID
            cls=0.05,  # Excellent CLS
            ttfb=350,  # Good TTFB
            data_source="crux"
        ),
        conversion_rate=0.032,
        data_confidence=0.9
    )
    # Add performance score dynamically (as done in the enrichment process)
    marketing_data6.performance_score = 95  # Excellent score
    prospect6.marketing_data = marketing_data6
    
    benchmarks6 = engine.marketing_benchmarks.get('industries', {}).get('ecommerce', {})
    performance_leaks6 = engine._analyze_performance_impact(prospect6, marketing_data6, benchmarks6)
    
    print(f"   Domain: {prospect6.domain}")
    print(f"   LCP: {marketing_data6.web_vitals.lcp}s, FID: {marketing_data6.web_vitals.fid}ms")
    print(f"   CLS: {marketing_data6.web_vitals.cls}, TTFB: {marketing_data6.web_vitals.ttfb}ms")
    print(f"   Overall Performance Score: {marketing_data6.performance_score}/100")
    print(f"   Performance leaks detected: {len(performance_leaks6)} (Expected: 0)")
    
    if performance_leaks6:
        print("   ⚠️  Unexpected leaks detected for good performance site!")
        for leak in performance_leaks6:
            print(f"   - {leak.type}: ${leak.monthly_waste:.2f}")
    else:
        print("   ✅ No performance leaks detected (as expected)")
    
    print("\n" + "=" * 60)
    print("🎯 Performance Impact Leak Detection Test Complete!")
    print(f"✅ All test cases executed successfully")
    
    # Clean up
    await engine.close()

if __name__ == "__main__":
    asyncio.run(test_performance_impact_detection())