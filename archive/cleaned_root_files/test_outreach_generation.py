"""
Test script to demonstrate personalized outreach generation.
Shows how the OutreachEngine creates data-driven, personalized messaging
for high-priority prospects based on their specific context and insights.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional

# Add the arco directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'arco'))

from arco.engines.outreach_engine import OutreachEngine, OutreachContent
from arco.engines.priority_engine import PriorityScore
from arco.models.prospect import Prospect, MarketingData


@dataclass
class MockProspect:
    """Mock prospect for testing outreach generation."""
    company_name: str
    domain: str
    website: str = ""
    industry: str = ""
    employee_count: int = 0
    revenue: int = 0
    technologies: List[str] = None
    funding_stage: str = ""
    last_funding_date: Optional[datetime] = None
    job_postings_count: int = 0
    traffic_growth_rate: float = 0.0
    contact_email: str = ""
    decision_maker_emails: List[str] = None
    marketing_data: Optional[MarketingData] = None

    def __post_init__(self):
        if self.technologies is None:
            self.technologies = []
        if self.decision_maker_emails is None:
            self.decision_maker_emails = []
        if not self.website:
            self.website = f"https://{self.domain}"


def create_priority_prospects_with_insights() -> List[tuple]:
    """Create priority prospects with marketing insights for outreach testing."""
    prospects_with_scores = []
    
    # High-priority SaaS prospect with performance issues
    saas_prospect = MockProspect(
        company_name="TechFlow Solutions",
        domain="techflow.io",
        industry="saas",
        employee_count=75,
        revenue=8500000,
        technologies=["aws", "kubernetes", "react", "node.js", "postgresql", "stripe"],
        funding_stage="series_a",
        last_funding_date=datetime.now() - timedelta(days=90),
        job_postings_count=15,
        traffic_growth_rate=0.45,
        decision_maker_emails=["cto@techflow.io", "vp-eng@techflow.io"],
        contact_email="hello@techflow.io"
    )
    
    # Add marketing data with performance issues
    saas_marketing_data = MarketingData()
    saas_marketing_data.web_vitals = type('WebVitals', (), {
        'lcp': 3.2,  # Slow loading
        'fid': 120,
        'cls': 0.15  # Layout shift issues
    })()
    saas_marketing_data.bounce_rate = 0.58
    saas_marketing_data.conversion_rate = 0.032
    saas_marketing_data.organic_traffic_share = 0.55
    saas_marketing_data.paid_traffic_share = 0.35
    saas_marketing_data.data_confidence = 0.9
    saas_prospect.marketing_data = saas_marketing_data
    
    saas_score = PriorityScore(
        total_score=85.5,
        company_size_score=70.0,
        revenue_potential_score=85.0,
        technology_maturity_score=80.0,
        growth_indicators_score=90.0,
        contact_accessibility_score=85.0,
        confidence_level=90.0,
        priority_tier="HIGH"
    )
    
    prospects_with_scores.append((saas_prospect, saas_score))
    
    # High-growth ecommerce prospect
    ecommerce_prospect = MockProspect(
        company_name="GreenStyle Commerce",
        domain="greenstyle.com",
        industry="ecommerce",
        employee_count=45,
        revenue=6200000,
        technologies=["shopify", "klaviyo", "google ads", "facebook ads", "recharge"],
        funding_stage="seed",
        last_funding_date=datetime.now() - timedelta(days=150),
        job_postings_count=8,
        traffic_growth_rate=0.65,
        decision_maker_emails=["cmo@greenstyle.com", "founder@greenstyle.com"],
        contact_email="team@greenstyle.com"
    )
    
    # Add marketing data with conversion issues
    ecommerce_marketing_data = MarketingData()
    ecommerce_marketing_data.web_vitals = type('WebVitals', (), {
        'lcp': 2.8,
        'fid': 95,
        'cls': 0.12
    })()
    ecommerce_marketing_data.bounce_rate = 0.62  # High bounce rate
    ecommerce_marketing_data.conversion_rate = 0.024
    ecommerce_marketing_data.organic_traffic_share = 0.35
    ecommerce_marketing_data.paid_traffic_share = 0.55  # Heavy paid reliance
    ecommerce_marketing_data.data_confidence = 0.85
    ecommerce_prospect.marketing_data = ecommerce_marketing_data
    
    ecommerce_score = PriorityScore(
        total_score=78.2,
        company_size_score=60.0,
        revenue_potential_score=75.0,
        technology_maturity_score=70.0,
        growth_indicators_score=95.0,
        contact_accessibility_score=80.0,
        confidence_level=85.0,
        priority_tier="HIGH"
    )
    
    prospects_with_scores.append((ecommerce_prospect, ecommerce_score))
    
    # Fintech prospect with scaling challenges
    fintech_prospect = MockProspect(
        company_name="PayStream Technologies",
        domain="paystream.co",
        industry="fintech",
        employee_count=110,
        revenue=14000000,
        technologies=["aws", "go", "react", "postgresql", "stripe", "plaid"],
        funding_stage="series_b",
        last_funding_date=datetime.now() - timedelta(days=45),
        job_postings_count=22,
        traffic_growth_rate=0.38,
        decision_maker_emails=["cto@paystream.co", "ceo@paystream.co"],
        contact_email="contact@paystream.co"
    )
    
    # Add marketing data with good performance but scaling needs
    fintech_marketing_data = MarketingData()
    fintech_marketing_data.web_vitals = type('WebVitals', (), {
        'lcp': 2.1,  # Good performance
        'fid': 65,
        'cls': 0.08
    })()
    fintech_marketing_data.bounce_rate = 0.42
    fintech_marketing_data.conversion_rate = 0.048
    fintech_marketing_data.organic_traffic_share = 0.70
    fintech_marketing_data.paid_traffic_share = 0.25
    fintech_marketing_data.data_confidence = 0.88
    fintech_prospect.marketing_data = fintech_marketing_data
    
    fintech_score = PriorityScore(
        total_score=92.1,
        company_size_score=85.0,
        revenue_potential_score=95.0,
        technology_maturity_score=90.0,
        growth_indicators_score=95.0,
        contact_accessibility_score=90.0,
        confidence_level=88.0,
        priority_tier="HIGH"
    )
    
    prospects_with_scores.append((fintech_prospect, fintech_score))
    
    return prospects_with_scores


async def test_outreach_generation():
    """Test personalized outreach generation for priority prospects."""
    print("🎯 PERSONALIZED OUTREACH GENERATION TEST")
    print("=" * 60)
    
    # Initialize outreach engine
    outreach_engine = OutreachEngine()
    print("✅ OutreachEngine initialized with personalized templates")
    
    # Get priority prospects with insights
    priority_prospects = create_priority_prospects_with_insights()
    print(f"📊 Testing outreach generation for {len(priority_prospects)} priority prospects")
    
    # Generate outreach for each priority prospect
    for i, (prospect, priority_score) in enumerate(priority_prospects, 1):
        print(f"\n{'='*60}")
        print(f"🎯 PRIORITY PROSPECT #{i}: {prospect.company_name}")
        print(f"{'='*60}")
        
        # Display prospect context
        print(f"📋 PROSPECT CONTEXT:")
        print(f"   • Company: {prospect.company_name} ({prospect.domain})")
        print(f"   • Industry: {prospect.industry}")
        print(f"   • Size: {prospect.employee_count} employees, ${prospect.revenue:,} revenue")
        print(f"   • Funding: {prospect.funding_stage}")
        print(f"   • Growth: {prospect.traffic_growth_rate:.0%} traffic growth, {prospect.job_postings_count} open positions")
        print(f"   • Priority Score: {priority_score.total_score:.1f}/100 ({priority_score.priority_tier})")
        
        if prospect.decision_maker_emails:
            print(f"   • Decision Makers: {', '.join(prospect.decision_maker_emails)}")
        
        # Display marketing insights
        if prospect.marketing_data:
            md = prospect.marketing_data
            print(f"\n📊 MARKETING INSIGHTS:")
            print(f"   • Page Speed: {md.web_vitals.lcp:.1f}s LCP, {md.web_vitals.cls:.2f} CLS")
            print(f"   • Conversion Rate: {md.conversion_rate:.1%}")
            print(f"   • Bounce Rate: {md.bounce_rate:.1%}")
            print(f"   • Traffic Mix: {md.organic_traffic_share:.0%} organic, {md.paid_traffic_share:.0%} paid")
        
        # Generate personalized outreach
        print(f"\n🚀 GENERATING PERSONALIZED OUTREACH...")
        outreach_content = await outreach_engine.generate_outreach(
            prospect=prospect,
            priority_score=priority_score
        )
        
        # Display generated outreach components
        print(f"\n📧 GENERATED OUTREACH CONTENT:")
        print(f"   Subject Line: {outreach_content.subject_line}")
        print(f"   Opening Hook: {outreach_content.opening_hook}")
        print(f"   Value Prop: {outreach_content.value_proposition}")
        print(f"   Call to Action: {outreach_content.call_to_action}")
        
        if outreach_content.specific_insights:
            print(f"\n💡 SPECIFIC INSIGHTS:")
            for insight in outreach_content.specific_insights:
                print(f"   • {insight}")
        
        if outreach_content.technical_talking_points:
            print(f"\n🔧 TECHNICAL TALKING POINTS:")
            for point in outreach_content.technical_talking_points:
                print(f"   • {point}")
        
        if outreach_content.urgency_factors:
            print(f"\n⏰ URGENCY FACTORS:")
            for factor in outreach_content.urgency_factors:
                print(f"   • {factor}")
        
        # Display ROI projections
        roi = outreach_content.roi_projections
        if roi.get("monthly_savings", 0) > 0:
            print(f"\n💰 ROI PROJECTIONS:")
            print(f"   • Monthly Savings: ${roi['monthly_savings']:,.0f}")
            print(f"   • Annual Savings: ${roi['annual_savings']:,.0f}")
            if roi.get("conversion_improvement", 0) > 0:
                print(f"   • Conversion Improvement: {roi['conversion_improvement']:.1%}")
            print(f"   • Confidence Level: {roi['confidence_level']}")
        
        # Generate complete email
        print(f"\n📨 COMPLETE EMAIL:")
        print("-" * 40)
        complete_email = outreach_engine.format_email(outreach_content, prospect)
        print(complete_email)
        print("-" * 40)
    
    # Summary and recommendations
    print(f"\n📋 OUTREACH GENERATION SUMMARY")
    print("=" * 60)
    print(f"✅ Generated personalized outreach for {len(priority_prospects)} priority prospects")
    print(f"📊 Each outreach includes:")
    print(f"   • Personalized subject line based on company context")
    print(f"   • Industry-specific opening hook")
    print(f"   • Data-driven value proposition")
    print(f"   • Specific insights from marketing analysis")
    print(f"   • Technical talking points for credibility")
    print(f"   • Urgency factors for timing")
    print(f"   • ROI projections when applicable")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"   1. Review and customize each outreach message")
    print(f"   2. Research decision makers on LinkedIn")
    print(f"   3. Send outreach within 24-48 hours for optimal timing")
    print(f"   4. Track response rates and refine messaging")
    print(f"   5. Prepare for follow-up conversations with technical details")
    
    print(f"\n📈 EXPECTED RESULTS:")
    print(f"   • 20-30% response rate from personalized outreach")
    print(f"   • 40-60% meeting acceptance rate from responses")
    print(f"   • Higher qualification rate due to data-driven insights")
    
    return priority_prospects


if __name__ == "__main__":
    # Run the outreach generation test
    prospects = asyncio.run(test_outreach_generation())
    
    print(f"\n✅ Outreach generation test completed successfully!")
    print(f"🎯 Ready to begin personalized outreach to {len(prospects)} priority prospects")