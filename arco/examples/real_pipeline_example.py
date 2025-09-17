"""
Real pipeline example demonstrating the refactored ARCO system.

This example shows how to use the new service layer architecture
with dependency injection to analyze prospects.
"""

import asyncio
import logging
from datetime import datetime

from arco.core.container import get_container
from arco.services import register_services, get_prospect_orchestrator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Demonstrate the refactored pipeline with real data collection."""
    
    logger.info("🚀 Starting Real Pipeline Example with Professional Architecture")
    
    # Setup dependency injection
    container = get_container()
    register_services(container)
    
    # Validate all services are properly registered
    container.validate_registrations()
    
    # Get orchestrator with all dependencies injected
    orchestrator = get_prospect_orchestrator(container)
    
    # Sample prospects for testing (using new dict format)
    sample_prospects = [
        {
            'id': '1',
            'company_name': 'TechCorp Solutions',
            'domain': 'techcorp.com',
            'industry': 'Technology',
            'employee_count': 150,
            'country': 'United States'
        },
        {
            'id': '2',
            'company_name': 'E-commerce Plus',
            'domain': 'ecommerceplus.com',
            'industry': 'E-commerce',
            'employee_count': 75,
            'country': 'Canada'
        },
        {
            'id': '3',
            'company_name': 'SaaS Innovations',
            'domain': 'saasinnovations.com',
            'industry': 'Software',
            'employee_count': 200,
            'country': 'United Kingdom'
        }
    ]
    
    logger.info(f"📊 Processing {len(sample_prospects)} sample prospects with comprehensive analysis")
    
    # Process with comprehensive analysis
    comprehensive_prospects = await orchestrator.process_prospects_batch(sample_prospects)
    
    # Generate executive report
    executive_report = await orchestrator.generate_executive_report(comprehensive_prospects)
    
    # Display results
    print("\n" + "="*70)
    print("🎯 PROFESSIONAL PIPELINE EXAMPLE RESULTS")
    print("="*70)
    print(f"Prospects Analyzed: {len(comprehensive_prospects)}")
    print(f"Hot Leads: {executive_report['executive_summary']['hot_leads_identified']}")
    print(f"Average Lead Score: {executive_report['executive_summary']['average_lead_score']}/100")
    print(f"Total Budget Signals: {executive_report['executive_summary']['total_budget_signals']}")
    
    print("\n📋 COMPREHENSIVE PROSPECT ANALYSIS:")
    for prospect in comprehensive_prospects:
        print(f"\n🏢 {prospect.company_name}")
        print(f"   Domain: {prospect.domain}")
        print(f"   Business Model: {prospect.business_model.value}")
        print(f"   Company Scale: {prospect.company_scale.value}")
        print(f"   Lead Score: {prospect.lead_score.total_score}/100 ({prospect.lead_score.temperature.value})")
        print(f"   Budget Verification: {prospect.lead_score.budget_verification_score}/40")
        print(f"   Urgency Assessment: {prospect.lead_score.urgency_assessment_score}/30")
        print(f"   Project Timing: {prospect.lead_score.project_timing_score}/20")
        print(f"   Decision Access: {prospect.lead_score.decision_access_score}/10")
        print(f"   Partnership Potential: {prospect.calculate_partnership_potential():.2f}")
        print(f"   Data Quality: {prospect.business_intelligence.data_quality_score:.2f}")
        print(f"   Hot Lead: {'🔥 YES' if prospect.is_hot_lead() else '❄️ No'}")
        
        # Business Intelligence Summary
        bi = prospect.business_intelligence
        print(f"   📊 Business Intelligence:")
        print(f"      Ad Investment: {'✅' if bi.ad_investment.facebook_active or bi.ad_investment.google_active else '❌'}")
        print(f"      Monthly Ad Spend: ${bi.ad_investment.estimated_monthly_spend:,}")
        print(f"      Recent Funding: {bi.funding_profile.recent_funding_months or 'None'} months ago")
        print(f"      Tech Hiring: {bi.hiring_activity.tech_job_postings} positions")
        print(f"      Leadership Hiring: {bi.hiring_activity.tech_leadership_hiring} positions")
        
        # Scoring Rationale
        if prospect.lead_score.scoring_rationale:
            print(f"   🎯 Scoring Rationale:")
            for rationale in prospect.lead_score.scoring_rationale[:3]:
                print(f"      • {rationale}")
        
        # Approach Strategy
        print(f"   📋 Recommended Approach: {prospect.lead_score.recommended_approach}")
    
    print("\n📊 EXECUTIVE INSIGHTS:")
    print(f"Business Model Distribution:")
    for model, count in executive_report['market_analysis']['business_models'].items():
        print(f"  • {model}: {count}")
    
    print(f"\nStrategic Recommendations:")
    for recommendation in executive_report['recommendations']:
        print(f"  • {recommendation}")
    
    print("\n" + "="*70)
    logger.info("✅ Professional pipeline example completed successfully")


if __name__ == "__main__":
    asyncio.run(main())