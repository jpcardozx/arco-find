#!/usr/bin/env python3
"""
Test real prospect analysis with hot lead identification.
Demonstrate how to identify hot leads using business context, not just technical metrics.
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

# Add arco to path
sys.path.insert(0, str(Path(__file__).parent / "arco"))

from arco.models.prospect import Prospect

@dataclass
class BusinessContext:
    """Business context data for lead scoring."""
    job_postings: int = 0
    recent_website_changes: bool = False
    recent_tech_changes: bool = False
    tech_modernity_score: int = 50
    performance_score: int = 50
    security_issues: bool = False
    industry_growth_rate: float = 0.0
    competitive_pressure: str = "low"  # low, medium, high
    company_news_mentions: int = 0

@dataclass
class LeadScore:
    """Lead scoring result."""
    total_score: int
    temperature: str  # HOT, WARM, LUKEWARM, COLD
    reasons: List[str]
    recommended_approach: str
    business_insights: List[str]

class HotLeadIdentifier:
    """Identify hot leads using business context and real data."""
    
    def __init__(self):
        self.industry_growth_rates = {
            "technology": 0.15,
            "ecommerce": 0.12,
            "healthcare": 0.08,
            "retail": 0.05,
            "consumer services": 0.03
        }
    
    def analyze_prospect_temperature(self, prospect: Prospect, context: BusinessContext) -> LeadScore:
        """Analyze how hot a prospect is based on business indicators."""
        
        score = 0
        reasons = []
        business_insights = []
        
        # 1. Growth Indicators (0-30 points)
        growth_score = self._score_growth_indicators(prospect, context)
        score += growth_score
        if growth_score > 15:
            reasons.append(f"Strong growth signals ({growth_score}/30)")
            if context.job_postings >= 5:
                business_insights.append(f"Hiring {context.job_postings} people - expansion phase")
        
        # 2. Technology Investment (0-25 points)
        tech_score = self._score_tech_investment(prospect, context)
        score += tech_score
        if tech_score > 10:
            reasons.append(f"Technology investment indicators ({tech_score}/25)")
            if context.recent_tech_changes:
                business_insights.append("Recent technology changes - active IT projects")
        
        # 3. Urgency Factors (0-35 points)
        urgency_score = self._score_urgency_factors(prospect, context)
        score += urgency_score
        if urgency_score > 15:
            reasons.append(f"High urgency factors ({urgency_score}/35)")
            if context.performance_score < 30:
                business_insights.append("Severe performance issues affecting business")
        
        # 4. Market Context (0-10 points)
        market_score = self._score_market_context(prospect, context)
        score += market_score
        
        # Determine temperature
        temperature = self._calculate_temperature(score)
        approach = self._get_approach_strategy(temperature, prospect, context)
        
        return LeadScore(
            total_score=score,
            temperature=temperature,
            reasons=reasons,
            recommended_approach=approach,
            business_insights=business_insights
        )
    
    def _score_growth_indicators(self, prospect: Prospect, context: BusinessContext) -> int:
        """Score based on growth signals."""
        score = 0
        
        # Job postings indicate budget and growth
        if context.job_postings >= 10:
            score += 20
        elif context.job_postings >= 5:
            score += 15
        elif context.job_postings >= 2:
            score += 10
        
        # Website changes indicate active development
        if context.recent_website_changes:
            score += 10
        
        # Company news mentions indicate activity
        if context.company_news_mentions >= 3:
            score += 5
        
        return min(score, 30)
    
    def _score_tech_investment(self, prospect: Prospect, context: BusinessContext) -> int:
        """Score based on technology investment indicators."""
        score = 0
        
        # Recent tech changes indicate active IT investment
        if context.recent_tech_changes:
            score += 15
        
        # Outdated technology creates modernization opportunity
        if context.tech_modernity_score < 40:
            score += 10
        elif context.tech_modernity_score < 60:
            score += 5
        
        return min(score, 25)
    
    def _score_urgency_factors(self, prospect: Prospect, context: BusinessContext) -> int:
        """Score based on urgency indicators."""
        score = 0
        
        # Performance issues create urgency
        if context.performance_score < 30:
            score += 20
        elif context.performance_score < 50:
            score += 15
        elif context.performance_score < 70:
            score += 10
        
        # Security issues create immediate urgency
        if context.security_issues:
            score += 15
        
        return min(score, 35)
    
    def _score_market_context(self, prospect: Prospect, context: BusinessContext) -> int:
        """Score based on market timing and context."""
        score = 0
        
        # Industry growth rate
        industry_growth = self.industry_growth_rates.get(prospect.industry.lower(), 0.05)
        if industry_growth > 0.10:
            score += 5
        elif industry_growth > 0.07:
            score += 3
        
        # Competitive pressure
        if context.competitive_pressure == "high":
            score += 5
        elif context.competitive_pressure == "medium":
            score += 3
        
        return min(score, 10)
    
    def _calculate_temperature(self, score: int) -> str:
        """Calculate lead temperature based on total score."""
        if score >= 70:
            return "HOT"
        elif score >= 50:
            return "WARM"
        elif score >= 30:
            return "LUKEWARM"
        else:
            return "COLD"
    
    def _get_approach_strategy(self, temperature: str, prospect: Prospect, context: BusinessContext) -> str:
        """Get recommended approach strategy."""
        
        if temperature == "HOT":
            return "Immediate outreach with specific business impact focus and urgency"
        elif temperature == "WARM":
            return "Targeted outreach with competitive analysis and growth support"
        elif temperature == "LUKEWARM":
            return "Educational content and nurturing with periodic check-ins"
        else:
            return "Low priority - add to nurture sequence"

def create_test_prospects_with_context():
    """Create test prospects with realistic business context."""
    
    prospects_with_context = [
        {
            "prospect": Prospect(
                domain="toh.com.br",
                company_name="Toh Acessórios Pet",
                industry="consumer services",
                employee_count=13,
                country="Brazil"
            ),
            "context": BusinessContext(
                job_postings=3,  # Small growth
                recent_website_changes=True,
                tech_modernity_score=60,  # Decent tech
                performance_score=45,  # Poor performance
                security_issues=False,
                competitive_pressure="medium"
            )
        },
        
        {
            "prospect": Prospect(
                domain="bikinilasirene.com.br",
                company_name="La Sirène",
                industry="retail",
                employee_count=10,
                country="Brazil"
            ),
            "context": BusinessContext(
                job_postings=0,  # No hiring
                recent_website_changes=False,
                tech_modernity_score=40,  # Outdated
                performance_score=25,  # Very poor performance
                security_issues=True,  # Security issues
                competitive_pressure="high"  # High competition in fashion
            )
        },
        
        {
            "prospect": Prospect(
                domain="joolabrasil.com",
                company_name="JOOLA Brasil",
                industry="retail",
                employee_count=7,
                country="Brazil"
            ),
            "context": BusinessContext(
                job_postings=2,  # Some growth
                recent_website_changes=True,
                recent_tech_changes=True,  # Active tech investment
                tech_modernity_score=70,  # Modern tech
                performance_score=60,  # Decent performance
                security_issues=False,
                company_news_mentions=5,  # Active in market
                competitive_pressure="medium"
            )
        },
        
        {
            "prospect": Prospect(
                domain="magnavita.com.br",
                company_name="Empório Magna Vita",
                industry="retail",
                employee_count=10,
                country="Brazil"
            ),
            "context": BusinessContext(
                job_postings=0,  # No growth signals
                recent_website_changes=False,
                tech_modernity_score=50,  # Average tech
                performance_score=80,  # Good performance
                security_issues=False,
                competitive_pressure="low"
            )
        }
    ]
    
    return prospects_with_context

def analyze_prospects_for_hot_leads():
    """Analyze prospects to identify hot leads."""
    
    print("🔥 HOT LEAD IDENTIFICATION - REAL PROSPECT ANALYSIS")
    print("=" * 60)
    
    identifier = HotLeadIdentifier()
    prospects_data = create_test_prospects_with_context()
    
    results = []
    
    for data in prospects_data:
        prospect = data["prospect"]
        context = data["context"]
        
        # Analyze lead temperature
        lead_score = identifier.analyze_prospect_temperature(prospect, context)
        results.append((prospect, context, lead_score))
        
        # Display results
        print(f"\n🏢 {prospect.company_name} ({prospect.domain})")
        print(f"   Industry: {prospect.industry} | Employees: {prospect.employee_count}")
        print(f"   🌡️ Temperature: {lead_score.temperature} (Score: {lead_score.total_score}/100)")
        
        if lead_score.reasons:
            print(f"   📊 Scoring Reasons:")
            for reason in lead_score.reasons:
                print(f"      • {reason}")
        
        if lead_score.business_insights:
            print(f"   💡 Business Insights:")
            for insight in lead_score.business_insights:
                print(f"      • {insight}")
        
        print(f"   🎯 Recommended Approach: {lead_score.recommended_approach}")
    
    # Sort by temperature and score
    hot_leads = [r for r in results if r[2].temperature in ["HOT", "WARM"]]
    lukewarm_leads = [r for r in results if r[2].temperature == "LUKEWARM"]
    cold_leads = [r for r in results if r[2].temperature == "COLD"]
    
    print(f"\n📊 LEAD TEMPERATURE SUMMARY:")
    print(f"   🔥 HOT/WARM Leads: {len(hot_leads)}")
    print(f"   🌡️ LUKEWARM Leads: {len(lukewarm_leads)}")
    print(f"   ❄️ COLD Leads: {len(cold_leads)}")
    
    # Show prioritized outreach list
    if hot_leads:
        print(f"\n🎯 PRIORITY OUTREACH LIST:")
        for i, (prospect, context, score) in enumerate(hot_leads, 1):
            print(f"   {i}. {prospect.company_name} - {score.temperature} ({score.total_score}/100)")
            
            # Create specific outreach message
            message = create_outreach_message(prospect, context, score)
            print(f"      📧 Suggested Message: {message}")
    
    return results

def create_outreach_message(prospect: Prospect, context: BusinessContext, score: LeadScore) -> str:
    """Create personalized outreach message based on business context."""
    
    if score.temperature == "HOT" or score.temperature == "WARM":
        if context.job_postings >= 5:
            return f"I see {prospect.company_name} is expanding (hiring {context.job_postings} people). Your website performance might become a bottleneck as you grow."
        elif context.security_issues:
            return f"I noticed some security concerns with {prospect.domain} that could expose {prospect.company_name} to risks."
        elif context.performance_score < 30:
            return f"{prospect.company_name}'s website loads very slowly, which could be costing you customers in the competitive {prospect.industry} market."
        else:
            return f"I analyzed {prospect.domain} and found some optimization opportunities that could help {prospect.company_name} stay competitive."
    else:
        return f"Quick technical analysis available for {prospect.company_name} when you're ready to optimize your website."

def main():
    """Main analysis function."""
    
    results = analyze_prospects_for_hot_leads()
    
    print(f"\n✅ KEY LEARNINGS:")
    print(f"   1. Business context dramatically changes lead prioritization")
    print(f"   2. Job postings and growth signals are strong hot lead indicators")
    print(f"   3. Security issues create immediate urgency")
    print(f"   4. Performance problems + competitive pressure = warm leads")
    print(f"   5. Technical analysis alone misses the business story")
    
    print(f"\n🚀 NEXT STEPS:")
    print(f"   1. Implement job posting scraping for growth signals")
    print(f"   2. Monitor website changes to detect active projects")
    print(f"   3. Add security vulnerability scanning")
    print(f"   4. Create industry-specific competitive pressure indicators")
    print(f"   5. Build automated business context collection")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)