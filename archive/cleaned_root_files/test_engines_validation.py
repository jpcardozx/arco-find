#!/usr/bin/env python3
"""
Test script to validate existing engines functionality.
Task 1.1: Test existing engines functionality
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any

# Add arco to path
sys.path.insert(0, str(Path(__file__).parent / "arco"))

from arco.models.prospect import Prospect, Contact, Technology
from arco.pipelines.marketing_pipeline import MarketingPipeline
from arco.engines.lead_enrichment_engine import LeadEnrichmentEngine
from arco.engines.leak_engine import LeakEngine
from arco.engines.lead_qualification_engine import LeadQualificationEngine
from arco.engines.priority_engine import PriorityEngine

async def test_marketing_pipeline():
    """Test MarketingPipeline with sample domain."""
    print("🧪 Testing MarketingPipeline...")
    
    try:
        # Create sample prospect
        prospect = Prospect(
            domain="shopify.com",
            company_name="Shopify",
            website="https://shopify.com"
        )
        
        # Initialize pipeline
        pipeline = MarketingPipeline()
        
        # Process prospect
        result = await pipeline.process_prospect_async(prospect)
        
        if result:
            print(f"✅ MarketingPipeline: Successfully processed {prospect.domain}")
            print(f"   - Marketing data collected: {bool(prospect.marketing_data)}")
            if prospect.marketing_data and prospect.marketing_data.web_vitals:
                print(f"   - Web Vitals LCP: {prospect.marketing_data.web_vitals.lcp}s")
            return True
        else:
            print(f"❌ MarketingPipeline: Failed to process {prospect.domain}")
            return False
            
    except Exception as e:
        print(f"❌ MarketingPipeline: Error - {e}")
        return False

async def test_lead_enrichment_engine():
    """Test LeadEnrichmentEngine with sample prospect."""
    print("\n🧪 Testing LeadEnrichmentEngine...")
    
    try:
        # Create sample prospect
        prospect = Prospect(
            domain="shopify.com",
            company_name="Shopify",
            website="https://shopify.com"
        )
        
        # Initialize engine
        engine = LeadEnrichmentEngine()
        
        # Enrich prospect
        result = await engine.enrich_prospect(prospect)
        
        if result.success:
            print(f"✅ LeadEnrichmentEngine: Successfully enriched {prospect.domain}")
            print(f"   - Enriched fields: {result.enriched_fields}")
            print(f"   - New technologies: {len(result.new_technologies)}")
            print(f"   - Confidence scores: {result.confidence_scores}")
            return True
        else:
            print(f"❌ LeadEnrichmentEngine: Failed to enrich {prospect.domain}")
            print(f"   - Errors: {result.errors}")
            return False
            
    except Exception as e:
        print(f"❌ LeadEnrichmentEngine: Error - {e}")
        return False

async def test_leak_engine():
    """Test LeakEngine for financial waste calculation."""
    print("\n🧪 Testing LeakEngine...")
    
    try:
        # Create sample prospect
        prospect = Prospect(
            domain="shopify.com",
            company_name="Shopify",
            website="https://shopify.com",
            employee_count=100,
            revenue=10000000
        )
        
        # Initialize engine
        engine = LeakEngine()
        
        # Analyze prospect
        leak_result = await engine.analyze(prospect)
        
        if leak_result.total_monthly_waste > 0:
            print(f"✅ LeakEngine: Successfully analyzed {prospect.domain}")
            print(f"   - Monthly waste: ${leak_result.total_monthly_waste:.2f}")
            print(f"   - Annual savings: ${leak_result.annual_savings:.2f}")
            print(f"   - Leaks found: {len(leak_result.leaks)}")
            return True
        else:
            print(f"⚠️ LeakEngine: No significant waste found for {prospect.domain}")
            print(f"   - Processing time: {leak_result.processing_time:.2f}s")
            return True  # This is still a successful test
            
    except Exception as e:
        print(f"❌ LeakEngine: Error - {e}")
        return False

def test_lead_qualification_engine():
    """Test LeadQualificationEngine scoring."""
    print("\n🧪 Testing LeadQualificationEngine...")
    
    try:
        # Create sample prospect with good data
        prospect = Prospect(
            domain="shopify.com",
            company_name="Shopify",
            website="https://shopify.com",
            employee_count=100,
            revenue=10000000,
            industry="Technology",
            country="Canada"
        )
        
        # Add some contacts
        prospect.contacts = [
            Contact(name="John Doe", email="john@shopify.com", position="CEO"),
            Contact(name="Jane Smith", email="jane@shopify.com", position="CTO")
        ]
        
        # Add some technologies
        prospect.technologies = [
            Technology(name="Ruby on Rails", category="web_frameworks"),
            Technology(name="PostgreSQL", category="databases"),
            Technology(name="Redis", category="caching")
        ]
        
        # Initialize engine
        engine = LeadQualificationEngine()
        
        # Qualify lead
        is_qualified, lead_score = engine.qualify_lead(prospect)
        
        print(f"✅ LeadQualificationEngine: Successfully scored {prospect.domain}")
        print(f"   - Qualified: {is_qualified}")
        print(f"   - Total score: {lead_score.total_score:.1f}/100")
        print(f"   - Qualification level: {lead_score.qualification_level}")
        print(f"   - Priority level: {lead_score.priority_level}")
        
        return True
        
    except Exception as e:
        print(f"❌ LeadQualificationEngine: Error - {e}")
        return False

async def test_priority_engine():
    """Test PriorityEngine for lead prioritization."""
    print("\n🧪 Testing PriorityEngine...")
    
    try:
        # Create sample prospects
        prospects = [
            Prospect(
                domain="shopify.com",
                company_name="Shopify",
                website="https://shopify.com",
                employee_count=100,
                revenue=10000000,
                industry="Technology"
            ),
            Prospect(
                domain="example.com",
                company_name="Example Corp",
                website="https://example.com",
                employee_count=50,
                revenue=5000000,
                industry="E-commerce"
            )
        ]
        
        # Initialize engine
        engine = PriorityEngine()
        
        # Score batch
        scored_prospects = await engine.score_batch(prospects)
        
        if scored_prospects:
            print(f"✅ PriorityEngine: Successfully scored {len(scored_prospects)} prospects")
            for prospect, score in scored_prospects:
                print(f"   - {prospect.domain}: {score.total_score:.1f} ({score.priority_tier})")
            return True
        else:
            print(f"❌ PriorityEngine: No prospects scored")
            return False
            
    except Exception as e:
        print(f"❌ PriorityEngine: Error - {e}")
        return False

async def main():
    """Run all engine tests."""
    print("🚀 Starting Engine Validation Tests")
    print("=" * 50)
    
    results = {}
    
    # Test each engine
    results['marketing_pipeline'] = await test_marketing_pipeline()
    results['lead_enrichment'] = await test_lead_enrichment_engine()
    results['leak_engine'] = await test_leak_engine()
    results['lead_qualification'] = test_lead_qualification_engine()
    results['priority_engine'] = await test_priority_engine()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(results.values())
    total = len(results)
    
    for engine, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {engine}: {status}")
    
    print(f"\nOverall: {passed}/{total} engines working correctly")
    
    if passed == total:
        print("🎉 All engines are functional!")
        return True
    else:
        print("⚠️ Some engines need attention")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)