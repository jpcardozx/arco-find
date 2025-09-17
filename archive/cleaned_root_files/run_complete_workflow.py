#!/usr/bin/env python3
"""
COMPLETE INTEGRATED WORKFLOW - Part 1
Comprehensive analysis of 175 prospects with real data and actionable insights.
"""

import asyncio
import sys
import os
import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import pandas as pd

# Add arco to path  
sys.path.insert(0, str(Path(__file__).parent / "arco"))

@dataclass
class EnhancedProspectAnalysis:
    """Complete prospect analysis with all data points."""
    company_name: str
    domain: str
    industry: str
    employee_count: int
    country: str
    performance_score: int = 0
    lcp_seconds: float = 0.0
    total_score: int = 0
    temperature: str = "COLD"
    priority_rank: int = 999
    key_insights: List[str] = None
    value_proposition: str = ""
    recommended_approach: str = ""
    
    def __post_init__(self):
        if self.key_insights is None:
            self.key_insights = []

async def main():
    """Main workflow execution."""
    print("🚀 COMPLETE INTEGRATED WORKFLOW")
    print("=" * 50)
    print("Starting comprehensive analysis of 175 prospects...")
    
    # Load CSV data
    df = pd.read_csv("arco/consolidated_prospects.csv")
    print(f"✅ Loaded {len(df)} prospects from CSV")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
class Co
mprehensiveAnalyzer:
    """Complete prospect analysis system."""
    
    def __init__(self):
        from arco.integrations.google_analytics import GoogleAnalyticsIntegration
        self.ga_integration = GoogleAnalyticsIntegration()
        self.results = []
    
    async def analyze_prospect(self, prospect_data: Dict) -> EnhancedProspectAnalysis:
        """Analyze single prospect comprehensively."""
        
        # Extract basic info
        company_name = prospect_data.get('Company', '')
        domain = self._extract_domain(prospect_data.get('Website', ''))
        industry = prospect_data.get('Industry', '')
        employee_count = int(prospect_data.get('# Employees', 0))
        country = prospect_data.get('Company Country', '')
        
        analysis = EnhancedProspectAnalysis(
            company_name=company_name,
            domain=domain,
            industry=industry,
            employee_count=employee_count,
            country=country
        )
        
        if not domain:
            return analysis
        
        try:
            # Get real performance data
            web_vitals = await self.ga_integration.get_web_vitals(domain)
            if web_vitals:
                analysis.performance_score = self._calculate_performance_score(web_vitals)
                analysis.lcp_seconds = web_vitals.lcp
            
            # Calculate business scores
            analysis.total_score = self._calculate_total_score(analysis, prospect_data)
            analysis.temperature = self._calculate_temperature(analysis.total_score)
            
            # Generate insights
            analysis.key_insights = self._generate_insights(analysis, prospect_data)
            analysis.value_proposition = self._create_value_proposition(analysis)
            analysis.recommended_approach = self._get_approach_strategy(analysis)
            
        except Exception as e:
            print(f"⚠️ Error analyzing {domain}: {e}")
        
        return analysis
    
    def _extract_domain(self, website: str) -> str:
        """Extract domain from website URL."""
        if not website or pd.isna(website):
            return ""
        
        website = str(website).strip()
        if website.startswith(('http://', 'https://')):
            website = website.split('://', 1)[1]
        
        if website.startswith('www.'):
            website = website[4:]
        
        return website.split('/')[0].split('?')[0]
    
    def _calculate_performance_score(self, web_vitals) -> int:
        """Calculate performance score from web vitals."""
        score = 100
        
        if web_vitals.lcp:
            if web_vitals.lcp > 4.0:
                score -= 40
            elif web_vitals.lcp > 2.5:
                score -= 20
        
        return max(0, score)
    
    def _calculate_total_score(self, analysis: EnhancedProspectAnalysis, data: Dict) -> int:
        """Calculate comprehensive lead score."""
        score = 0
        
        # Performance issues (urgency)
        if analysis.performance_score < 50:
            score += 25
        elif analysis.performance_score < 70:
            score += 15
        
        # Company size (budget indicator)
        if analysis.employee_count >= 50:
            score += 20
        elif analysis.employee_count >= 20:
            score += 15
        elif analysis.employee_count >= 10:
            score += 10
        
        # Industry scoring
        high_value_industries = ['technology', 'retail', 'ecommerce']
        if any(ind in analysis.industry.lower() for ind in high_value_industries):
            score += 15
        
        # Technology stack (from CSV)
        technologies = data.get('Technologies', '')
        if technologies and len(str(technologies)) > 100:  # Rich tech stack
            score += 10
        
        return min(score, 100)
    
    def _calculate_temperature(self, score: int) -> str:
        """Calculate lead temperature."""
        if score >= 70:
            return "HOT"
        elif score >= 50:
            return "WARM"
        elif score >= 30:
            return "LUKEWARM"
        else:
            return "COLD"    d
ef _generate_insights(self, analysis: EnhancedProspectAnalysis, data: Dict) -> List[str]:
        """Generate actionable business insights."""
        insights = []
        
        # Performance insights
        if analysis.lcp_seconds > 4.0:
            insights.append(f"Critical: Site loads in {analysis.lcp_seconds:.1f}s (Google recommends <2.5s)")
            insights.append("Poor performance directly impacts SEO rankings and user experience")
        elif analysis.lcp_seconds > 2.5:
            insights.append(f"Performance issue: {analysis.lcp_seconds:.1f}s load time needs optimization")
        
        # Business context insights
        if analysis.employee_count >= 20:
            insights.append(f"Growing company ({analysis.employee_count} employees) - likely has budget for optimization")
        
        # Industry-specific insights
        if 'retail' in analysis.industry.lower():
            insights.append("E-commerce business - performance directly affects conversion rates")
        elif 'technology' in analysis.industry.lower():
            insights.append("Tech company - should prioritize modern, fast website as competitive advantage")
        
        # Geographic insights
        if analysis.country == "Brazil":
            insights.append("Brazilian market - mobile performance critical for local users")
        
        return insights
    
    def _create_value_proposition(self, analysis: EnhancedProspectAnalysis) -> str:
        """Create specific value proposition for the prospect."""
        
        if analysis.temperature == "HOT":
            if analysis.lcp_seconds > 4.0:
                return f"Your website's {analysis.lcp_seconds:.1f}s load time is costing you customers. We can optimize it to under 2.5s, improving both user experience and SEO rankings."
            else:
                return f"As a growing {analysis.industry} company, we can help you optimize your digital presence for competitive advantage."
        
        elif analysis.temperature == "WARM":
            return f"We've identified optimization opportunities for {analysis.company_name} that could improve your website performance and business results."
        
        else:
            return f"Technical audit available for {analysis.company_name} when you're ready to optimize your online presence."
    
    def _get_approach_strategy(self, analysis: EnhancedProspectAnalysis) -> str:
        """Get recommended approach strategy."""
        
        if analysis.temperature == "HOT":
            return "PRIORITY: Immediate outreach with specific performance impact and business case"
        elif analysis.temperature == "WARM":
            return "QUALIFIED: Targeted outreach with competitive analysis and optimization opportunities"
        elif analysis.temperature == "LUKEWARM":
            return "NURTURE: Educational content about performance optimization benefits"
        else:
            return "LOW PRIORITY: Add to general nurture sequence"

async def run_comprehensive_analysis():
    """Run the complete analysis workflow."""
    
    print("🚀 STARTING COMPREHENSIVE ANALYSIS")
    print("=" * 50)
    
    analyzer = ComprehensiveAnalyzer()
    
    # Load CSV data
    df = pd.read_csv("arco/consolidated_prospects.csv")
    print(f"✅ Loaded {len(df)} prospects from CSV")
    
    # Process prospects in batches
    batch_size = 5  # Small batches for API rate limiting
    all_analyses = []
    
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        print(f"\n📊 Processing batch {i//batch_size + 1}/{(len(df) + batch_size - 1)//batch_size}")
        
        # Process batch
        batch_tasks = []
        for _, row in batch.iterrows():
            task = analyzer.analyze_prospect(row.to_dict())
            batch_tasks.append(task)
        
        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        
        # Handle results
        for j, result in enumerate(batch_results):
            if isinstance(result, Exception):
                print(f"❌ Error processing prospect {i+j}: {result}")
            else:
                all_analyses.append(result)
                print(f"✅ {result.company_name}: {result.temperature} ({result.total_score}/100)")
        
        # Rate limiting
        if i + batch_size < len(df):
            print("⏳ Rate limiting delay...")
            await asyncio.sleep(3)
    
    # Sort by score
    all_analyses.sort(key=lambda x: x.total_score, reverse=True)
    
    # Assign ranks
    for i, analysis in enumerate(all_analyses):
        analysis.priority_rank = i + 1
    
    return all_analyses

# Update main function
async def main():
    """Main workflow execution."""
    print("🚀 COMPLETE INTEGRATED WORKFLOW")
    print("=" * 50)
    
    # Run comprehensive analysis
    results = await run_comprehensive_analysis()
    
    # Generate reports
    await generate_comprehensive_reports(results)
    
    return True

async def generate_comprehensive_reports(results: List[EnhancedProspectAnalysis]):
    """Generate comprehensive reports and CRM organization."""
    
    print(f"\n📊 GENERATING COMPREHENSIVE REPORTS")
    print("=" * 40)
    
    # Summary statistics
    hot_leads = [r for r in results if r.temperature == "HOT"]
    warm_leads = [r for r in results if r.temperature == "WARM"]
    lukewarm_leads = [r for r in results if r.temperature == "LUKEWARM"]
    cold_leads = [r for r in results if r.temperature == "COLD"]
    
    print(f"🔥 HOT Leads: {len(hot_leads)}")
    print(f"🌡️ WARM Leads: {len(warm_leads)}")
    print(f"🌤️ LUKEWARM Leads: {len(lukewarm_leads)}")
    print(f"❄️ COLD Leads: {len(cold_leads)}")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # JSON export
    results_data = []
    for result in results:
        results_data.append({
            "company_name": result.company_name,
            "domain": result.domain,
            "industry": result.industry,
            "employee_count": result.employee_count,
            "country": result.country,
            "performance_score": result.performance_score,
            "lcp_seconds": result.lcp_seconds,
            "total_score": result.total_score,
            "temperature": result.temperature,
            "priority_rank": result.priority_rank,
            "key_insights": result.key_insights,
            "value_proposition": result.value_proposition,
            "recommended_approach": result.recommended_approach
        })
    
    # Save JSON
    json_file = f"comprehensive_analysis_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Detailed results saved: {json_file}")
    
    # Create priority outreach list
    priority_leads = [r for r in results if r.temperature in ["HOT", "WARM"]][:20]
    
    if priority_leads:
        print(f"\n🎯 TOP 20 PRIORITY LEADS:")
        for i, lead in enumerate(priority_leads, 1):
            print(f"{i:2d}. {lead.company_name:<25} | {lead.temperature:<8} | Score: {lead.total_score:2d}/100")
            if lead.key_insights:
                print(f"    💡 {lead.key_insights[0]}")
    
    return results_data