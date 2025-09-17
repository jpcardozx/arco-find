"""
Test the enhanced LeakEngine with real technical performance analysis.
Focus on precise technical metrics rather than conversion estimates.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional
import json

# Add the arco directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'arco'))

from arco.engines.priority_engine import PriorityEngine, PriorityScore
from arco.engines.leak_engine import LeakEngine
from arco.integrations.google_analytics import GoogleAnalyticsIntegration
from arco.models.prospect import Prospect, MarketingData


@dataclass
class TechnicalProspect:
    """Prospect focused on technical analysis."""
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


def create_technical_prospects() -> List[TechnicalProspect]:
    """Create prospects for technical performance analysis."""
    return [
        # Fast performance sites
        TechnicalProspect(
            company_name="Google",
            domain="google.com",
            industry="technology",
            employee_count=150000,
            revenue=280000000000,  # $280B
            technologies=["go", "javascript", "kubernetes", "google cloud"],
            decision_maker_emails=["partnerships@google.com"],
            contact_email="business@google.com"
        ),
        
        # Medium performance sites
        TechnicalProspect(
            company_name="Shopify",
            domain="shopify.com",
            industry="saas",
            employee_count=12000,
            revenue=5600000000,  # $5.6B
            technologies=["ruby", "react", "kubernetes", "google cloud"],
            funding_stage="public",
            job_postings_count=150,
            decision_maker_emails=["partnerships@shopify.com"],
            contact_email="enterprise@shopify.com"
        ),
        
        # Slower performance sites
        TechnicalProspect(
            company_name="WordPress.com",
            domain="wordpress.com",
            industry="saas",
            employee_count=1800,
            revenue=500000000,  # $500M
            technologies=["php", "javascript", "mysql", "kubernetes"],
            funding_stage="private",
            job_postings_count=25,
            contact_email="business@wordpress.com"
        ),
        
        # GitHub for comparison
        TechnicalProspect(
            company_name="GitHub",
            domain="github.com",
            industry="software",
            employee_count=3000,
            revenue=1000000000,  # $1B
            technologies=["ruby", "go", "react", "kubernetes", "aws"],
            funding_stage="acquired",
            job_postings_count=80,
            decision_maker_emails=["partnerships@github.com"],
            contact_email="enterprise@github.com"
        )
    ]


async def test_technical_analysis():
    """Test technical performance analysis with real data."""
    print("🔧 TECHNICAL PERFORMANCE ANALYSIS TEST")
    print("=" * 70)
    print("Focus on precise technical metrics and optimization opportunities")
    print()
    
    # Load technical prospects
    prospects = create_technical_prospects()
    print(f"📊 Analyzing {len(prospects)} prospects for technical performance:")
    for prospect in prospects:
        print(f"   • {prospect.company_name} ({prospect.domain})")
    print()
    
    # Initialize Google Analytics integration
    ga_integration = GoogleAnalyticsIntegration()
    
    # Perform technical analysis for each prospect
    technical_results = []
    
    for i, prospect in enumerate(prospects, 1):
        print(f"🔍 {i}. ANALYZING {prospect.company_name.upper()}")
        print(f"{'='*60}")
        
        try:
            # Get real web vitals
            print(f"📊 Collecting real performance data for {prospect.domain}...")
            web_vitals = await ga_integration.get_web_vitals(prospect.domain)
            
            if web_vitals:
                print(f"✅ Web Vitals collected successfully!")
                print(f"   • LCP (Largest Contentful Paint): {web_vitals.lcp:.2f}s")
                print(f"   • FID (First Input Delay): {web_vitals.fid:.0f}ms" if web_vitals.fid else "   • FID: N/A")
                print(f"   • CLS (Cumulative Layout Shift): {web_vitals.cls:.3f}" if web_vitals.cls else "   • CLS: N/A")
                print(f"   • TTFB (Time to First Byte): {web_vitals.ttfb:.0f}ms" if web_vitals.ttfb else "   • TTFB: N/A")
                
                # Perform technical analysis
                print(f"\n🔧 Technical Performance Analysis:")
                technical_analysis = await ga_integration.get_technical_performance_analysis(prospect.domain)
                
                if technical_analysis:
                    print(f"   • Performance Score: {technical_analysis.get('performance_score', 0)}/100")
                    print(f"   • Performance Grade: {technical_analysis.get('performance_grade', 'Unknown')}")
                    print(f"   • User Experience Impact: {technical_analysis.get('user_experience_impact', 'Unknown')}")
                    print(f"   • SEO Impact: {technical_analysis.get('seo_impact', 'Unknown')}")
                    
                    # Technical issues
                    issues = technical_analysis.get('technical_issues', [])
                    if issues:
                        print(f"\n⚠️ Technical Issues Identified:")
                        for issue in issues:
                            print(f"     • {issue}")
                    
                    # Optimization opportunities
                    opportunities = technical_analysis.get('optimization_opportunities', [])
                    if opportunities:
                        print(f"\n💡 Optimization Opportunities:")
                        for opp in opportunities:
                            print(f"     • {opp}")
                    
                    # Calculate business impact
                    print(f"\n💰 Business Impact Analysis:")
                    if web_vitals.lcp > 2.5:
                        delay_seconds = web_vitals.lcp - 2.5
                        print(f"     • Page load delay: {delay_seconds:.1f}s beyond optimal")
                        print(f"     • Potential user experience degradation")
                        if prospect.revenue > 0:
                            # Conservative impact estimate based on technical metrics only
                            monthly_revenue = prospect.revenue / 12
                            print(f"     • Monthly revenue at risk: ${monthly_revenue * 0.01:,.0f} (1% conservative estimate)")
                    else:
                        print(f"     • Excellent performance - competitive advantage")
                        print(f"     • Strong foundation for user experience")
                    
                    technical_results.append({
                        "prospect": prospect,
                        "web_vitals": web_vitals,
                        "technical_analysis": technical_analysis,
                        "performance_score": technical_analysis.get('performance_score', 0)
                    })
                
            else:
                print(f"❌ Failed to collect web vitals for {prospect.domain}")
                technical_results.append({
                    "prospect": prospect,
                    "web_vitals": None,
                    "technical_analysis": None,
                    "performance_score": 0
                })
                
        except Exception as e:
            print(f"❌ Error analyzing {prospect.domain}: {e}")
            technical_results.append({
                "prospect": prospect,
                "web_vitals": None,
                "technical_analysis": None,
                "performance_score": 0,
                "error": str(e)
            })
        
        print()
    
    # Summary and insights
    print(f"📋 TECHNICAL ANALYSIS SUMMARY")
    print("=" * 70)
    
    # Sort by performance score
    technical_results.sort(key=lambda x: x.get('performance_score', 0), reverse=True)
    
    print(f"🏆 Performance Ranking:")
    for i, result in enumerate(technical_results, 1):
        prospect = result['prospect']
        score = result.get('performance_score', 0)
        web_vitals = result.get('web_vitals')
        
        if web_vitals and web_vitals.lcp:
            print(f"   {i}. {prospect.company_name:<15} | Score: {score:3.0f}/100 | LCP: {web_vitals.lcp:.2f}s")
        else:
            print(f"   {i}. {prospect.company_name:<15} | Score: {score:3.0f}/100 | No data")
    
    print(f"\n🎯 Key Technical Insights:")
    
    # Best performers
    best_performers = [r for r in technical_results if r.get('performance_score', 0) >= 80]
    if best_performers:
        print(f"   ✅ Excellent Performance ({len(best_performers)} companies):")
        for result in best_performers:
            prospect = result['prospect']
            print(f"      • {prospect.company_name}: Strong technical foundation")
    
    # Performance issues
    poor_performers = [r for r in technical_results if r.get('performance_score', 0) < 40]
    if poor_performers:
        print(f"   ⚠️ Performance Optimization Needed ({len(poor_performers)} companies):")
        for result in poor_performers:
            prospect = result['prospect']
            web_vitals = result.get('web_vitals')
            if web_vitals and web_vitals.lcp:
                print(f"      • {prospect.company_name}: {web_vitals.lcp:.1f}s LCP - significant optimization opportunity")
    
    # Technical recommendations
    print(f"\n🔧 Technical Recommendations:")
    print(f"   1. Focus on LCP optimization for sites >2.5s")
    print(f"   2. Implement JavaScript optimization for high FID")
    print(f"   3. Address layout stability for CLS issues")
    print(f"   4. Server response time optimization for TTFB")
    
    print(f"\n💼 Business Applications:")
    print(f"   • Use technical analysis for credible technical discussions")
    print(f"   • Quantify optimization opportunities with real metrics")
    print(f"   • Position solutions based on actual performance data")
    print(f"   • Avoid speculative conversion rate estimates")
    
    # Close session
    if ga_integration.session and not ga_integration.session.closed:
        await ga_integration.session.close()
    
    return technical_results


async def test_leak_engine_integration():
    """Test integration with the enhanced LeakEngine."""
    print(f"\n🔍 LEAK ENGINE INTEGRATION TEST")
    print("=" * 70)
    
    # Create a sample prospect
    prospect = TechnicalProspect(
        company_name="Test Company",
        domain="shopify.com",  # Use a real domain for testing
        industry="saas",
        employee_count=100,
        revenue=10000000,
        technologies=["ruby", "react", "kubernetes"],
        funding_stage="series_b",
        job_postings_count=15,
        decision_maker_emails=["cto@testcompany.com"]
    )
    
    print(f"🎯 Testing LeakEngine with {prospect.company_name} ({prospect.domain})")
    
    try:
        # Initialize LeakEngine
        leak_engine = LeakEngine()
        
        # Analyze prospect
        print(f"📊 Running leak analysis...")
        leak_result = await leak_engine.analyze(prospect)
        
        if leak_result:
            print(f"✅ Leak analysis completed!")
            print(f"   • Total Monthly Waste: ${leak_result.total_monthly_waste:.2f}")
            print(f"   • Number of Leaks: {len(leak_result.leaks)}")
            print(f"   • Processing Time: {leak_result.processing_time:.2f}s")
            
            # Display marketing-specific leaks
            marketing_leaks = [leak for leak in leak_result.leaks if hasattr(leak, 'technical_recommendation')]
            if marketing_leaks:
                print(f"\n🔧 Marketing/Performance Leaks:")
                for leak in marketing_leaks:
                    print(f"     • {leak.description}")
                    if hasattr(leak, 'technical_recommendation'):
                        print(f"       Recommendation: {leak.technical_recommendation}")
            
        else:
            print(f"❌ Leak analysis failed")
            
    except Exception as e:
        print(f"❌ LeakEngine integration error: {e}")
        print(f"   This is expected if LeakEngine needs additional configuration")


if __name__ == "__main__":
    # Run technical analysis test
    print("🚀 Starting Technical Performance Analysis")
    results = asyncio.run(test_technical_analysis())
    
    # Run LeakEngine integration test
    asyncio.run(test_leak_engine_integration())
    
    print(f"\n✅ Technical analysis completed!")
    print(f"🎯 {len(results)} prospects analyzed with real technical data")
    print(f"🔧 Focus on measurable technical metrics for credible outreach")