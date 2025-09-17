"""
Test script to demonstrate the PriorityEngine functionality.
Shows how to identify the top 10% highest-priority leads for immediate outreach.
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


@dataclass
class MockProspect:
    """Mock prospect for testing priority scoring."""
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


def create_sample_prospects() -> List[MockProspect]:
    """Create a diverse set of sample prospects for testing."""
    prospects = [
        # High-priority prospects
        MockProspect(
            company_name="TechCorp Solutions",
            domain="techcorp.com",
            industry="saas",
            employee_count=150,
            revenue=25000000,
            technologies=["aws", "kubernetes", "react", "node.js", "postgresql", "salesforce", "hubspot"],
            funding_stage="series_b",
            last_funding_date=datetime.now() - timedelta(days=180),
            job_postings_count=15,
            traffic_growth_rate=0.35,
            contact_email="contact@techcorp.com",
            decision_maker_emails=["cto@techcorp.com", "ceo@techcorp.com"],
            linkedin_profiles=["linkedin.com/company/techcorp"]
        ),
        
        MockProspect(
            company_name="GrowthStart Inc",
            domain="growthstart.io",
            industry="fintech",
            employee_count=75,
            revenue=8000000,
            technologies=["google cloud", "python", "react", "stripe", "intercom", "google analytics"],
            funding_stage="series_a",
            last_funding_date=datetime.now() - timedelta(days=90),
            job_postings_count=12,
            traffic_growth_rate=0.65,
            contact_email="hello@growthstart.io",
            decision_maker_emails=["founder@growthstart.io"],
            linkedin_profiles=["linkedin.com/company/growthstart"]
        ),
        
        # Medium-priority prospects
        MockProspect(
            company_name="RetailPlus",
            domain="retailplus.com",
            industry="ecommerce",
            employee_count=45,
            revenue=3500000,
            technologies=["shopify", "mailchimp", "google ads", "facebook ads"],
            funding_stage="seed",
            job_postings_count=5,
            traffic_growth_rate=0.15,
            contact_email="info@retailplus.com"
        ),
        
        MockProspect(
            company_name="HealthTech Solutions",
            domain="healthtech.com",
            industry="healthcare",
            employee_count=120,
            revenue=12000000,
            technologies=["azure", "angular", "mongodb", "tableau"],
            funding_stage="growth",
            last_funding_date=datetime.now() - timedelta(days=400),
            job_postings_count=8,
            contact_email="contact@healthtech.com",
            linkedin_profiles=["linkedin.com/company/healthtech"]
        ),
        
        # Lower-priority prospects
        MockProspect(
            company_name="Small Consulting",
            domain="smallconsult.com",
            industry="consulting",
            employee_count=8,
            revenue=500000,
            technologies=["wordpress", "google analytics"],
            job_postings_count=1,
            contact_email="info@smallconsult.com"
        ),
        
        MockProspect(
            company_name="Local Restaurant",
            domain="localrest.com",
            industry="food_service",
            employee_count=25,
            revenue=800000,
            technologies=["square", "facebook"],
            job_postings_count=2,
            contact_email="manager@localrest.com"
        ),
        
        # Additional prospects for better testing
        MockProspect(
            company_name="DataDriven Corp",
            domain="datadriven.ai",
            industry="software",
            employee_count=200,
            revenue=35000000,
            technologies=["aws", "snowflake", "python", "react", "kubernetes", "salesforce"],
            funding_stage="series_c",
            last_funding_date=datetime.now() - timedelta(days=120),
            job_postings_count=25,
            traffic_growth_rate=0.45,
            decision_maker_emails=["cto@datadriven.ai", "vp-eng@datadriven.ai"],
            linkedin_profiles=["linkedin.com/company/datadriven"]
        ),
        
        MockProspect(
            company_name="CloudFirst Startup",
            domain="cloudfirst.dev",
            industry="saas",
            employee_count=35,
            revenue=2000000,
            technologies=["google cloud", "go", "vue", "postgresql", "stripe"],
            funding_stage="seed",
            last_funding_date=datetime.now() - timedelta(days=60),
            job_postings_count=8,
            traffic_growth_rate=0.80,
            contact_email="team@cloudfirst.dev",
            decision_maker_emails=["founder@cloudfirst.dev"]
        ),
        
        MockProspect(
            company_name="Enterprise Solutions Ltd",
            domain="enterprise-sol.com",
            industry="technology",
            employee_count=500,
            revenue=75000000,
            technologies=["azure", "salesforce", "tableau", "marketo", "docker"],
            funding_stage="public",
            job_postings_count=30,
            traffic_growth_rate=0.10,
            contact_email="contact@enterprise-sol.com",
            linkedin_profiles=["linkedin.com/company/enterprise-solutions"]
        ),
        
        MockProspect(
            company_name="MidSize Manufacturing",
            domain="midsize-mfg.com",
            industry="manufacturing",
            employee_count=180,
            revenue=22000000,
            technologies=["microsoft", "oracle", "sap"],
            job_postings_count=6,
            contact_email="info@midsize-mfg.com"
        )
    ]
    
    return prospects


async def test_priority_engine():
    """Test the priority engine with sample prospects."""
    print("🚀 Testing Priority Engine for Lead Scoring and Prioritization")
    print("=" * 70)
    
    # Create sample prospects
    prospects = create_sample_prospects()
    print(f"📊 Created {len(prospects)} sample prospects for testing")
    
    # Initialize priority engine
    try:
        engine = PriorityEngine()
        print("✅ Priority engine initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize priority engine: {e}")
        # Create a minimal config for testing
        engine = PriorityEngine.__new__(PriorityEngine)
        engine.scoring_weights = {
            "company_size": 0.25,
            "revenue_potential": 0.30,
            "technology_maturity": 0.20,
            "growth_indicators": 0.15,
            "contact_accessibility": 0.10
        }
        engine.industry_criteria = {}
        print("✅ Using default configuration for testing")
    
    # Score all prospects
    print("\n🔍 Scoring all prospects...")
    scored_prospects = await engine.score_batch(prospects)
    
    # Display all scored prospects
    print("\n📈 All Prospects Scored (sorted by priority):")
    print("-" * 70)
    for i, (prospect, score) in enumerate(scored_prospects, 1):
        print(f"{i:2d}. {prospect.company_name:<25} | Score: {score.total_score:5.1f} | "
              f"Tier: {score.priority_tier:<6} | Confidence: {score.confidence_level:4.1f}%")
    
    # Get top 10% prospects
    top_prospects = engine.get_top_percentage(scored_prospects, percentage=0.1)
    
    print(f"\n🎯 TOP {len(top_prospects)} PROSPECTS (Top 10%) - PRIORITY FOR IMMEDIATE OUTREACH:")
    print("=" * 70)
    
    for i, (prospect, score) in enumerate(top_prospects, 1):
        print(f"\n{i}. {prospect.company_name} ({prospect.domain})")
        print(f"   Overall Score: {score.total_score:.1f}/100 (Confidence: {score.confidence_level:.1f}%)")
        print(f"   Priority Tier: {score.priority_tier}")
        print(f"   Industry: {prospect.industry}")
        print(f"   Size: {prospect.employee_count} employees, ${prospect.revenue:,} revenue")
        
        # Detailed scoring breakdown
        print(f"   Scoring Breakdown:")
        print(f"     • Company Size: {score.company_size_score:.1f}/100")
        print(f"     • Revenue Potential: {score.revenue_potential_score:.1f}/100")
        print(f"     • Technology Maturity: {score.technology_maturity_score:.1f}/100")
        print(f"     • Growth Indicators: {score.growth_indicators_score:.1f}/100")
        print(f"     • Contact Accessibility: {score.contact_accessibility_score:.1f}/100")
        
        # Contact information
        if prospect.decision_maker_emails:
            print(f"   Decision Maker Contacts: {', '.join(prospect.decision_maker_emails)}")
        elif prospect.contact_email:
            print(f"   Contact Email: {prospect.contact_email}")
        
        # Key technologies
        if prospect.technologies:
            key_tech = prospect.technologies[:5]  # Show first 5 technologies
            print(f"   Key Technologies: {', '.join(key_tech)}")
    
    # Generate insights
    insights = engine.get_priority_insights(scored_prospects)
    
    print(f"\n📊 PRIORITY INSIGHTS:")
    print("-" * 40)
    print(f"Total Prospects Analyzed: {insights.get('total_prospects', 0)}")
    print(f"Average Score: {insights.get('average_score', 0):.1f}/100")
    print(f"Highest Score: {insights.get('highest_score', 0):.1f}/100")
    print(f"High Priority Prospects: {insights.get('high_priority_count', 0)} "
          f"({insights.get('high_priority_percentage', 0):.1f}%)")
    print(f"Top 10% Score Threshold: {insights.get('top_10_percent_threshold', 0):.1f}/100")
    
    print(f"\n🎯 NEXT STEPS:")
    print("-" * 40)
    print("1. Focus immediate outreach efforts on the top prospects listed above")
    print("2. Prepare personalized messaging based on their technology stack and growth indicators")
    print("3. Research decision makers using LinkedIn and company websites")
    print("4. Schedule deep enrichment analysis for these priority leads")
    print("5. Track outreach success rates to refine scoring algorithm")
    
    return top_prospects


if __name__ == "__main__":
    # Run the test
    top_leads = asyncio.run(test_priority_engine())
    
    print(f"\n✅ Priority Engine test completed successfully!")
    print(f"🎯 Identified {len(top_leads)} high-priority leads ready for immediate outreach")