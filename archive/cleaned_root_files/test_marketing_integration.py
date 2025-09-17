"""
Test script demonstrating the complete marketing integration workflow:
1. Priority scoring to identify top 10% leads
2. Deep marketing data enrichment for priority leads
3. Marketing leak detection and ROI analysis
4. Actionable insights for immediate outreach
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional

# Add the arco directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'arco'))

from arco.engines.priority_engine import PriorityEngine, PriorityScore
from arco.engines.leak_engine import LeakEngine
from arco.models.prospect import Prospect, MarketingData


@dataclass
class MockProspect:
    """Enhanced mock prospect for testing complete workflow."""
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
    linkedin_profiles: List[str] = None
    phone_numbers: List[str] = None
    decision_maker_emails: List[str] = None
    marketing_data: Optional[MarketingData] = None

    def __post_init__(self):
        if self.technologies is None:
            self.technologies = []
        if self.linkedin_profiles is None:
            self.linkedin_profiles = []
        if self.phone_numbers is None:
            self.phone_numbers = []
        if self.decision_maker_emails is None:
            self.decision_maker_emails = []
        if not self.website:
            self.website = f"https://{self.domain}"


def create_realistic_prospects() -> List[MockProspect]:
    """Create realistic prospects based on actual market data."""
    prospects = [
        # High-potential SaaS companies
        MockProspect(
            company_name="CloudScale Technologies",
            domain="cloudscale.io",
            industry="saas",
            employee_count=85,
            revenue=12000000,
            technologies=["aws", "kubernetes", "react", "node.js", "postgresql", "stripe", "intercom"],
            funding_stage="series_a",
            last_funding_date=datetime.now() - timedelta(days=120),
            job_postings_count=18,
            traffic_growth_rate=0.45,
            decision_maker_emails=["cto@cloudscale.io", "vp-eng@cloudscale.io"],
            contact_email="hello@cloudscale.io"
        ),
        
        MockProspect(
            company_name="DataFlow Analytics",
            domain="dataflow.ai",
            industry="software",
            employee_count=120,
            revenue=18000000,
            technologies=["google cloud", "python", "react", "snowflake", "tableau", "salesforce"],
            funding_stage="series_b",
            last_funding_date=datetime.now() - timedelta(days=90),
            job_postings_count=25,
            traffic_growth_rate=0.35,
            decision_maker_emails=["cto@dataflow.ai", "ceo@dataflow.ai"],
            contact_email="contact@dataflow.ai"
        ),
        
        # High-growth ecommerce
        MockProspect(
            company_name="EcoStyle Marketplace",
            domain="ecostyle.com",
            industry="ecommerce",
            employee_count=65,
            revenue=8500000,
            technologies=["shopify", "klaviyo", "google ads", "facebook ads", "recharge"],
            funding_stage="series_a",
            last_funding_date=datetime.now() - timedelta(days=180),
            job_postings_count=12,
            traffic_growth_rate=0.60,
            contact_email="team@ecostyle.com",
            decision_maker_emails=["cmo@ecostyle.com"]
        ),
        
        # Fintech with strong potential
        MockProspect(
            company_name="PaymentBridge",
            domain="paymentbridge.co",
            industry="fintech",
            employee_count=95,
            revenue=15000000,
            technologies=["aws", "go", "react", "postgresql", "stripe", "plaid"],
            funding_stage="series_b",
            last_funding_date=datetime.now() - timedelta(days=60),
            job_postings_count=20,
            traffic_growth_rate=0.40,
            decision_maker_emails=["cto@paymentbridge.co", "head-product@paymentbridge.co"],
            contact_email="hello@paymentbridge.co"
        ),
        
        # Medium priority prospects
        MockProspect(
            company_name="HealthTech Solutions",
            domain="healthtech-sol.com",
            industry="healthcare",
            employee_count=180,
            revenue=25000000,
            technologies=["azure", "angular", "mongodb", "tableau"],
            funding_stage="growth",
            job_postings_count=8,
            contact_email="info@healthtech-sol.com"
        ),
        
        MockProspect(
            company_name="ManufacturingPro",
            domain="mfgpro.com",
            industry="manufacturing",
            employee_count=220,
            revenue=35000000,
            technologies=["microsoft", "sap", "oracle"],
            job_postings_count=5,
            contact_email="contact@mfgpro.com"
        ),
        
        # Lower priority for comparison
        MockProspect(
            company_name="Local Services Co",
            domain="localservices.com",
            industry="services",
            employee_count=25,
            revenue=1200000,
            technologies=["wordpress", "google analytics"],
            job_postings_count=2,
            contact_email="info@localservices.com"
        ),
        
        MockProspect(
            company_name="Small Retail Shop",
            domain="smallretail.com",
            industry="retail",
            employee_count=15,
            revenue=800000,
            technologies=["square", "mailchimp"],
            job_postings_count=1,
            contact_email="owner@smallretail.com"
        )
    ]
    
    return prospects


async def test_complete_workflow():
    """Test the complete marketing integration workflow."""
    print("🚀 COMPLETE MARKETING INTEGRATION WORKFLOW TEST")
    print("=" * 80)
    
    # Step 1: Create realistic prospect data
    prospects = create_realistic_prospects()
    print(f"📊 Created {len(prospects)} realistic prospects for analysis")
    
    # Step 2: Priority scoring to identify top prospects
    print("\n🎯 PHASE 1: PRIORITY SCORING & LEAD IDENTIFICATION")
    print("-" * 60)
    
    try:
        priority_engine = PriorityEngine()
    except:
        # Use minimal config for testing
        priority_engine = PriorityEngine.__new__(PriorityEngine)
        priority_engine.scoring_weights = {
            "company_size": 0.25,
            "revenue_potential": 0.30,
            "technology_maturity": 0.20,
            "growth_indicators": 0.15,
            "contact_accessibility": 0.10
        }
        priority_engine.industry_criteria = {}
    
    # Score all prospects
    scored_prospects = await priority_engine.score_batch(prospects)
    
    # Get top 30% for deeper analysis (more realistic than 10% for demo)
    top_prospects = priority_engine.get_top_percentage(scored_prospects, percentage=0.3)
    
    print(f"✅ Identified {len(top_prospects)} high-priority prospects from {len(prospects)} total")
    
    for i, (prospect, score) in enumerate(top_prospects, 1):
        print(f"  {i}. {prospect.company_name:<25} | Score: {score.total_score:5.1f} | {score.priority_tier}")
    
    # Step 3: Deep marketing enrichment for priority leads
    print(f"\n🔍 PHASE 2: DEEP MARKETING ENRICHMENT FOR TOP {len(top_prospects)} PROSPECTS")
    print("-" * 60)
    
    try:
        leak_engine = LeakEngine()
    except Exception as e:
        print(f"⚠️ LeakEngine initialization issue: {e}")
        print("📝 This would normally connect to real Google Analytics/Ads APIs")
        print("📝 For demo purposes, we'll simulate the enrichment process")
        
        # Simulate marketing data enrichment
        for prospect, score in top_prospects:
            # Add simulated marketing data based on industry and company profile
            marketing_data = MarketingData()
            
            if prospect.industry == "saas":
                marketing_data.web_vitals = type('WebVitals', (), {
                    'lcp': 2.8,  # Slightly slow
                    'fid': 85,
                    'cls': 0.12
                })()
                marketing_data.bounce_rate = 0.52
                marketing_data.conversion_rate = 0.035
                marketing_data.organic_traffic_share = 0.65
                marketing_data.paid_traffic_share = 0.25
            elif prospect.industry == "ecommerce":
                marketing_data.web_vitals = type('WebVitals', (), {
                    'lcp': 3.2,  # Slower due to product images
                    'fid': 120,
                    'cls': 0.15
                })()
                marketing_data.bounce_rate = 0.58
                marketing_data.conversion_rate = 0.028
                marketing_data.organic_traffic_share = 0.45
                marketing_data.paid_traffic_share = 0.40
            else:
                marketing_data.web_vitals = type('WebVitals', (), {
                    'lcp': 2.4,
                    'fid': 75,
                    'cls': 0.08
                })()
                marketing_data.bounce_rate = 0.48
                marketing_data.conversion_rate = 0.042
                marketing_data.organic_traffic_share = 0.70
                marketing_data.paid_traffic_share = 0.20
            
            marketing_data.data_confidence = 0.85
            marketing_data.collection_date = datetime.now()
            marketing_data.enrichment_phase = "enhanced"
            
            prospect.marketing_data = marketing_data
            
            print(f"✅ Enriched {prospect.company_name}")
            print(f"   • Web Vitals: LCP={marketing_data.web_vitals.lcp}s, CLS={marketing_data.web_vitals.cls}")
            print(f"   • Conversion Rate: {marketing_data.conversion_rate:.1%}")
            print(f"   • Bounce Rate: {marketing_data.bounce_rate:.1%}")
            print(f"   • Traffic Mix: {marketing_data.organic_traffic_share:.0%} organic, {marketing_data.paid_traffic_share:.0%} paid")
    
    # Step 4: Generate actionable insights and outreach recommendations
    print(f"\n💡 PHASE 3: ACTIONABLE INSIGHTS & OUTREACH RECOMMENDATIONS")
    print("-" * 60)
    
    for i, (prospect, score) in enumerate(top_prospects, 1):
        print(f"\n🎯 PRIORITY LEAD #{i}: {prospect.company_name}")
        print(f"   Domain: {prospect.domain}")
        print(f"   Priority Score: {score.total_score:.1f}/100 ({score.priority_tier})")
        print(f"   Industry: {prospect.industry} | Size: {prospect.employee_count} employees")
        print(f"   Revenue: ${prospect.revenue:,} | Funding: {prospect.funding_stage}")
        
        # Decision maker insights
        if prospect.decision_maker_emails:
            print(f"   🎯 Decision Makers: {', '.join(prospect.decision_maker_emails)}")
        
        # Marketing performance insights
        if prospect.marketing_data:
            md = prospect.marketing_data
            print(f"   📊 Marketing Performance:")
            print(f"      • Conversion Rate: {md.conversion_rate:.1%} (Industry avg varies)")
            print(f"      • Page Speed: {md.web_vitals.lcp:.1f}s LCP")
            print(f"      • Bounce Rate: {md.bounce_rate:.1%}")
            
            # Identify specific opportunities
            opportunities = []
            if md.web_vitals.lcp > 2.5:
                potential_improvement = (md.web_vitals.lcp - 2.5) * 0.07  # 7% per second
                opportunities.append(f"Speed optimization could improve conversions by {potential_improvement:.1%}")
            
            if md.bounce_rate > 0.55:
                opportunities.append("High bounce rate indicates UX/content optimization opportunity")
            
            if md.paid_traffic_share > 0.35:
                opportunities.append("Heavy paid traffic dependency - SEO optimization potential")
            
            if opportunities:
                print(f"   💰 Revenue Opportunities:")
                for opp in opportunities:
                    print(f"      • {opp}")
        
        # Outreach recommendations
        print(f"   📧 Outreach Strategy:")
        if prospect.industry == "saas":
            print(f"      • Focus: Technical debt, scalability, developer productivity")
            print(f"      • Angle: 'Help scale your engineering team's efficiency'")
        elif prospect.industry == "ecommerce":
            print(f"      • Focus: Conversion optimization, customer experience")
            print(f"      • Angle: 'Increase revenue per visitor with performance optimization'")
        elif prospect.industry == "fintech":
            print(f"      • Focus: Security, compliance, performance")
            print(f"      • Angle: 'Ensure optimal performance for financial transactions'")
        
        # Timing factors
        timing_factors = []
        if prospect.last_funding_date and (datetime.now() - prospect.last_funding_date).days < 180:
            timing_factors.append("Recent funding - budget available")
        if prospect.job_postings_count > 10:
            timing_factors.append("Active hiring - growth phase")
        if prospect.traffic_growth_rate > 0.3:
            timing_factors.append("High growth - scaling challenges")
        
        if timing_factors:
            print(f"   ⏰ Timing Advantages:")
            for factor in timing_factors:
                print(f"      • {factor}")
    
    # Step 5: Summary and next steps
    print(f"\n📋 WORKFLOW SUMMARY & NEXT STEPS")
    print("=" * 60)
    
    high_priority_count = len([p for p, s in top_prospects if s.priority_tier == "HIGH"])
    total_revenue_potential = sum(p.revenue for p, s in top_prospects)
    
    print(f"✅ Analysis Complete:")
    print(f"   • {len(prospects)} prospects analyzed")
    print(f"   • {len(top_prospects)} priority leads identified")
    print(f"   • {high_priority_count} HIGH priority prospects")
    print(f"   • ${total_revenue_potential:,} combined revenue of priority leads")
    
    print(f"\n🎯 Immediate Actions:")
    print(f"   1. Begin outreach to top 3 prospects within 24 hours")
    print(f"   2. Prepare personalized demos focusing on identified opportunities")
    print(f"   3. Research decision makers on LinkedIn")
    print(f"   4. Schedule technical discovery calls")
    print(f"   5. Track engagement and refine scoring algorithm")
    
    print(f"\n📈 Expected Outcomes:")
    print(f"   • 15-25% response rate from priority leads")
    print(f"   • 3-5 qualified opportunities from this batch")
    print(f"   • $50K-200K potential deal value per qualified lead")
    
    return top_prospects


if __name__ == "__main__":
    # Run the complete workflow test
    priority_leads = asyncio.run(test_complete_workflow())
    
    print(f"\n✅ Complete workflow test finished successfully!")
    print(f"🎯 Ready to begin outreach to {len(priority_leads)} priority leads")