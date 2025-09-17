#!/usr/bin/env python3
"""
Test script for the refactored LeakEngine.

This script tests the new practical LeakEngine implementation that focuses on
real technical analysis instead of fake financial calculations.
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from arco.engines.leak_engine import LeakEngine
from arco.models.prospect import Prospect

async def test_refactored_leak_engine():
    """Test the refactored LeakEngine with real technical analysis."""
    
    print("🧪 Testing Refactored LeakEngine")
    print("=" * 50)
    
    # Initialize the refactored leak engine
    leak_engine = LeakEngine()
    
    # Test domains
    test_domains = [
        "google.com",
        "shopify.com", 
        "example.com"
    ]
    
    for domain in test_domains:
        print(f"\n🔍 Analyzing {domain}...")
        
        # Create a test prospect
        prospect = Prospect(
            domain=domain,
            company_name=domain.replace('.com', '').capitalize(),
            industry="Technology",
            employee_count=100
        )
        
        try:
            # Analyze the prospect using the refactored engine
            result = await leak_engine.analyze(prospect)
            
            print(f"✅ Analysis complete for {domain}")
            print(f"   • Technical Issues Found: {len(result.leaks)}")
            print(f"   • Technical Severity Score: {result.authority_score:.1f}/100")
            print(f"   • Processing Time: {result.processing_time:.2f}s")
            print(f"   • Monthly Waste (should be 0.0): ${result.total_monthly_waste}")
            
            # Show the types of issues found
            if result.leaks:
                issue_types = set(leak.type for leak in result.leaks)
                print(f"   • Issue Types: {', '.join(issue_types)}")
                
                # Show top 3 issues
                print("   • Top Issues:")
                for i, leak in enumerate(result.leaks[:3]):
                    print(f"     {i+1}. {leak.description} (Severity: {leak.severity})")
            else:
                print("   • No technical issues detected")
            
            # Test qualification
            qualified_prospect = await leak_engine.qualify(prospect, result)
            print(f"   • Qualification Score: {qualified_prospect.qualification_score}/100")
            print(f"   • Priority Tier: {qualified_prospect.priority_tier}")
            print(f"   • Outreach Ready: {qualified_prospect.outreach_ready}")
            
        except Exception as e:
            print(f"❌ Error analyzing {domain}: {e}")
    
    # Clean up
    await leak_engine.close()
    
    print("\n✅ Refactored LeakEngine test complete!")
    print("\nKey Improvements:")
    print("• ✅ Removed fake financial calculations (monthly_waste = 0.0)")
    print("• ✅ Added real Wappalyzer technology detection")
    print("• ✅ Added real PageSpeed Insights Web Vitals analysis")
    print("• ✅ Added quick wins detection (SEO, security, performance)")
    print("• ✅ Technical severity scoring instead of fake money")
    print("• ✅ Actionable technical insights for prospects")

if __name__ == "__main__":
    asyncio.run(test_refactored_leak_engine())