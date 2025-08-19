#!/usr/bin/env python3
"""
Test for the new unified ARCO system
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_unified_crm_system():
    """Test the unified CRM system"""
    print("Testing Unified CRM System...")
    
    from src.core.unified_crm_system import UnifiedCRMEnrichmentEngine
    
    # Sample lead data
    sample_leads = [
        {
            "company_name": "TechCorp Solutions",
            "domain": "techcorp.com",
            "industry": "Software",
            "country": "US",
            "search_keywords": ["crm software"],
            "ad_volume_score": 85,
            "estimated_monthly_spend": 15000,
            "confirmed_advertiser": True,
            "advertising_platforms": ["google"],
            "creative_diversity_score": 0.3,
            "performance_score": 45,
            "estimated_cpa": 180,
        }
    ]
    
    crm_engine = UnifiedCRMEnrichmentEngine()
    enriched_leads = crm_engine.enrich_lead_batch(sample_leads)
    
    assert len(enriched_leads) == 1
    lead = enriched_leads[0]
    assert lead.company_name == "TechCorp Solutions"
    assert len(lead.pain_signals) > 0
    assert len(lead.growth_opportunities) > 0
    assert lead.lead_quality_score > 0
    
    print("✅ Unified CRM System test passed")

def test_strategic_scorer():
    """Test the strategic scoring system"""
    print("Testing Strategic Scorer...")
    
    from src.scoring.strategic_lead_scorer import StrategicLeadScorer
    
    sample_lead = {
        "company_name": "TestCorp",
        "industry": "ecommerce",
        "country": "US",
        "estimated_monthly_spend": 12000,
        "estimated_cpa": 180,
        "conversion_rate": 1.8,
        "bounce_rate": 65,
        "creative_diversity_score": 0.25,
        "mobile_performance_score": 45,
        "competitor_density": 9,
    }
    
    scorer = StrategicLeadScorer()
    final_score, analysis = scorer.calculate_strategic_score(sample_lead)
    
    assert 0 <= final_score <= 100
    assert "pain_signals" in analysis
    assert "growth_opportunities" in analysis
    assert "recommended_priority" in analysis
    
    print("✅ Strategic Scorer test passed")

async def test_consolidated_pipeline():
    """Test the consolidated pipeline"""
    print("Testing Consolidated Pipeline...")
    
    from src.pipelines.consolidated_searchapi_pipeline import ConsolidatedSearchAPIPipeline, SearchAPIConfig
    
    config = SearchAPIConfig(
        api_key="test_key",
        target_regions=["US"],
        target_verticals=["marketing_agencies"],
        budget_per_execution=0.10,
        max_leads_per_batch=5
    )
    
    # Test pipeline initialization
    async with ConsolidatedSearchAPIPipeline(config) as pipeline:
        assert pipeline.config.api_key == "test_key"
        assert len(pipeline.config.target_regions) == 1
        
    print("✅ Consolidated Pipeline test passed")

def run_all_tests():
    """Run all tests"""
    print("\n🧪 RUNNING ARCO UNIFIED SYSTEM TESTS")
    print("="*50)
    
    try:
        test_unified_crm_system()
        test_strategic_scorer()
        asyncio.run(test_consolidated_pipeline())
        
        print("\n✅ ALL TESTS PASSED")
        print("The new unified ARCO system is working correctly!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()