#!/usr/bin/env python3
"""
Enhanced Marketing Analysis Pipeline
Runs marketing data collection on prospects using real Google APIs
"""

import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd

from arco.models.prospect import Prospect, MarketingData, WebVitals
from arco.integrations.google_analytics import GoogleAnalyticsIntegration
from arco.integrations.google_ads import GoogleAdsIntegration
from arco.utils.logger import get_logger

logger = get_logger(__name__)

class MarketingAnalysisPipeline:
    """Enhanced pipeline for marketing data analysis with real API integration."""
    
    def __init__(self, google_api_key: str = None):
        """Initialize the pipeline with API credentials."""
        self.google_api_key = google_api_key or os.getenv('GOOGLE_API_KEY')
        self.ga_integration = GoogleAnalyticsIntegration(api_key=self.google_api_key)
        self.ads_integration = GoogleAdsIntegration()  # Will use estimates if no credentials
        self.results = []
        
    async def analyze_prospect(self, prospect: Prospect) -> Dict[str, Any]:
        """
        Analyze a single prospect with comprehensive marketing data collection.
        
        Args:
            prospect: Prospect object to analyze
            
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Analyzing prospect: {prospect.domain}")
        
        analysis_result = {
            'domain': prospect.domain,
            'company_name': prospect.company_name,
            'industry': prospect.industry,
            'employee_count': prospect.employee_count,
            'revenue': prospect.revenue,
            'analysis_date': datetime.now().isoformat(),
            'marketing_data': {},
            'performance_issues': [],
            'opportunities': [],
            'confidence_score': 0.0
        }
        
        try:
            # 1. Collect Web Vitals (real PageSpeed data)
            logger.info(f"Collecting web vitals for {prospect.domain}")
            web_vitals = await self.ga_integration.get_web_vitals(prospect.domain)
            
            if web_vitals:
                analysis_result['marketing_data']['web_vitals'] = web_vitals.to_dict()
                analysis_result['confidence_score'] += 0.3
                
                # Analyze performance issues
                performance_issues = self._analyze_performance_issues(web_vitals)
                analysis_result['performance_issues'].extend(performance_issues)
            
            # 2. Collect Conversion Metrics (estimated from performance)
            logger.info(f"Collecting conversion metrics for {prospect.domain}")
            conversion_metrics = await self.ga_integration.get_conversion_metrics(prospect.domain)
            
            if conversion_metrics:
                analysis_result['marketing_data']['conversion_metrics'] = conversion_metrics
                analysis_result['confidence_score'] += 0.2
                
                # Analyze conversion opportunities
                conversion_opportunities = self._analyze_conversion_opportunities(conversion_metrics)
                analysis_result['opportunities'].extend(conversion_opportunities)
            
            # 3. Collect Traffic Sources (domain-based analysis)
            logger.info(f"Analyzing traffic sources for {prospect.domain}")
            traffic_sources = await self.ga_integration.get_traffic_sources(prospect.domain)
            
            if traffic_sources:
                analysis_result['marketing_data']['traffic_sources'] = traffic_sources
                analysis_result['confidence_score'] += 0.2
                
                # Analyze traffic opportunities
                traffic_opportunities = self._analyze_traffic_opportunities(traffic_sources)
                analysis_result['opportunities'].extend(traffic_opportunities)
            
            # 4. Calculate Marketing Waste Potential
            waste_analysis = self._calculate_marketing_waste(
                web_vitals, conversion_metrics, traffic_sources, prospect
            )
            analysis_result['waste_analysis'] = waste_analysis
            analysis_result['confidence_score'] += 0.3
            
            logger.info(f"Analysis completed for {prospect.domain} (confidence: {analysis_result['confidence_score']:.2f})")
            
        except Exception as e:
            logger.error(f"Error analyzing {prospect.domain}: {e}")
            analysis_result['error'] = str(e)
            analysis_result['confidence_score'] = 0.0
        
        return analysis_result
    
    def _analyze_performance_issues(self, web_vitals: WebVitals) -> List[Dict[str, Any]]:
        """Analyze web performance issues and their business impact."""
        issues = []
        
        if web_vitals.lcp and web_vitals.lcp > 2.5:
            severity = "critical" if web_vitals.lcp > 4.0 else "high"
            conversion_loss = (web_vitals.lcp - 2.5) * 0.07  # 7% per second
            issues.append({
                'type': 'slow_loading',
                'metric': 'LCP',
                'value': web_vitals.lcp,
                'threshold': 2.5,
                'severity': severity,
                'impact': f"~{conversion_loss:.1%} conversion loss",
                'recommendation': 'Optimize images, reduce server response time, eliminate render-blocking resources'
            })
        
        if web_vitals.cls and web_vitals.cls > 0.1:
            severity = "high" if web_vitals.cls > 0.25 else "medium"
            issues.append({
                'type': 'layout_shift',
                'metric': 'CLS',
                'value': web_vitals.cls,
                'threshold': 0.1,
                'severity': severity,
                'impact': 'Poor user experience, increased bounce rate',
                'recommendation': 'Set dimensions for images/videos, avoid inserting content above existing content'
            })
        
        if web_vitals.ttfb and web_vitals.ttfb > 800:
            severity = "high" if web_vitals.ttfb > 1500 else "medium"
            issues.append({
                'type': 'slow_server',
                'metric': 'TTFB',
                'value': web_vitals.ttfb,
                'threshold': 800,
                'severity': severity,
                'impact': 'Delayed page rendering, poor SEO',
                'recommendation': 'Optimize server configuration, use CDN, improve database queries'
            })
        
        return issues
    
    def _analyze_conversion_opportunities(self, conversion_metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """Analyze conversion optimization opportunities."""
        opportunities = []
        
        bounce_rate = conversion_metrics.get('bounce_rate', 0)
        if bounce_rate > 0.6:
            opportunities.append({
                'type': 'high_bounce_rate',
                'current_value': bounce_rate,
                'benchmark': 0.47,
                'potential_improvement': f"{(bounce_rate - 0.47) * 100:.1f}% reduction possible",
                'impact': 'Improve user engagement and conversion rates',
                'tactics': ['Improve page load speed', 'Enhance content relevance', 'Optimize mobile experience']
            })
        
        conversion_rate = conversion_metrics.get('conversion_rate', 0)
        if conversion_rate < 0.02:  # Below 2%
            opportunities.append({
                'type': 'low_conversion_rate',
                'current_value': conversion_rate,
                'benchmark': 0.0268,
                'potential_improvement': f"{((0.0268 - conversion_rate) / conversion_rate * 100):.0f}% increase possible",
                'impact': 'Direct revenue increase',
                'tactics': ['A/B test CTAs', 'Optimize checkout flow', 'Improve value proposition']
            })
        
        return opportunities
    
    def _analyze_traffic_opportunities(self, traffic_sources: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze traffic source optimization opportunities."""
        opportunities = []
        
        organic_search = traffic_sources.get('organic_search', 0)
        paid_search = traffic_sources.get('paid_search', 0)
        
        # Low organic traffic opportunity
        if organic_search < 0.25:
            opportunities.append({
                'type': 'seo_opportunity',
                'current_value': organic_search,
                'benchmark': 0.35,
                'potential_improvement': f"{((0.35 - organic_search) * 100):.0f}% organic traffic increase",
                'impact': 'Reduce paid acquisition costs',
                'tactics': ['Content marketing', 'Technical SEO', 'Link building', 'Local SEO']
            })
        
        # High paid search dependency
        if paid_search > 0.4:
            opportunities.append({
                'type': 'paid_dependency',
                'current_value': paid_search,
                'benchmark': 0.20,
                'risk': 'High dependency on paid channels',
                'impact': 'Diversify traffic sources to reduce acquisition costs',
                'tactics': ['Invest in SEO', 'Content marketing', 'Social media', 'Email marketing']
            })
        
        return opportunities
    
    def _calculate_marketing_waste(self, web_vitals: WebVitals, conversion_metrics: Dict[str, float], 
                                 traffic_sources: Dict[str, Any], prospect: Prospect) -> Dict[str, Any]:
        """Calculate potential marketing waste and savings opportunities."""
        waste_analysis = {
            'total_waste_score': 0.0,
            'monthly_waste_estimate': 0.0,
            'annual_savings_potential': 0.0,
            'waste_categories': []
        }
        
        # Estimate monthly marketing spend based on company size
        estimated_monthly_spend = self._estimate_marketing_spend(prospect)
        
        # Performance-related waste
        if web_vitals and web_vitals.lcp and web_vitals.lcp > 2.5:
            performance_waste = (web_vitals.lcp - 2.5) * 0.07  # 7% conversion loss per second
            performance_waste_amount = estimated_monthly_spend * performance_waste
            
            waste_analysis['waste_categories'].append({
                'category': 'performance_waste',
                'waste_percentage': performance_waste,
                'monthly_waste': performance_waste_amount,
                'annual_waste': performance_waste_amount * 12,
                'description': f'Lost conversions due to {web_vitals.lcp:.1f}s LCP'
            })
            
            waste_analysis['total_waste_score'] += performance_waste
            waste_analysis['monthly_waste_estimate'] += performance_waste_amount
        
        # Traffic source inefficiency
        paid_search = traffic_sources.get('paid_search', 0) if traffic_sources else 0.2
        if paid_search > 0.3:  # High paid dependency
            paid_waste = (paid_search - 0.2) * 0.5  # 50% of excess paid traffic could be organic
            paid_waste_amount = estimated_monthly_spend * paid_waste
            
            waste_analysis['waste_categories'].append({
                'category': 'paid_dependency_waste',
                'waste_percentage': paid_waste,
                'monthly_waste': paid_waste_amount,
                'annual_waste': paid_waste_amount * 12,
                'description': f'Over-reliance on paid search ({paid_search:.1%} vs 20% benchmark)'
            })
            
            waste_analysis['total_waste_score'] += paid_waste
            waste_analysis['monthly_waste_estimate'] += paid_waste_amount
        
        waste_analysis['annual_savings_potential'] = waste_analysis['monthly_waste_estimate'] * 12
        
        return waste_analysis
    
    def _estimate_marketing_spend(self, prospect: Prospect) -> float:
        """Estimate monthly marketing spend based on company characteristics."""
        base_spend = 1000  # Base monthly spend
        
        # Adjust by employee count
        if prospect.employee_count:
            if prospect.employee_count < 10:
                base_spend = 2000
            elif prospect.employee_count < 50:
                base_spend = 5000
            elif prospect.employee_count < 200:
                base_spend = 15000
            else:
                base_spend = 50000
        
        # Adjust by revenue
        if prospect.revenue:
            revenue_factor = min(prospect.revenue / 1000000, 10)  # Cap at 10x
            base_spend *= revenue_factor
        
        # Adjust by industry
        if prospect.industry:
            industry_multipliers = {
                'saas': 1.5,
                'software': 1.5,
                'ecommerce': 1.3,
                'technology': 1.4,
                'finance': 1.2,
                'healthcare': 1.1
            }
            
            for industry, multiplier in industry_multipliers.items():
                if industry.lower() in prospect.industry.lower():
                    base_spend *= multiplier
                    break
        
        return base_spend
    
    async def analyze_prospects_batch(self, prospects: List[Prospect], batch_size: int = 10) -> List[Dict[str, Any]]:
        """Analyze prospects in batches to respect API rate limits."""
        results = []
        
        for i in range(0, len(prospects), batch_size):
            batch = prospects[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(prospects) + batch_size - 1)//batch_size}")
            
            # Process batch concurrently
            batch_tasks = [self.analyze_prospect(prospect) for prospect in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Handle results and exceptions
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch processing error: {result}")
                else:
                    results.append(result)
            
            # Rate limiting - wait between batches
            if i + batch_size < len(prospects):
                logger.info("Waiting 2 seconds between batches for rate limiting...")
                await asyncio.sleep(2)
        
        return results
    
    def save_results(self, results: List[Dict[str, Any]], filename: str = None):
        """Save analysis results to JSON and CSV files."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"marketing_analysis_{timestamp}"
        
        # Save detailed JSON
        json_file = f"{filename}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Save summary CSV
        csv_data = []
        for result in results:
            row = {
                'domain': result['domain'],
                'company_name': result['company_name'],
                'industry': result['industry'],
                'employee_count': result['employee_count'],
                'confidence_score': result['confidence_score'],
                'performance_issues_count': len(result.get('performance_issues', [])),
                'opportunities_count': len(result.get('opportunities', [])),
                'monthly_waste_estimate': result.get('waste_analysis', {}).get('monthly_waste_estimate', 0),
                'annual_savings_potential': result.get('waste_analysis', {}).get('annual_savings_potential', 0),
                'lcp_score': result.get('marketing_data', {}).get('web_vitals', {}).get('lcp'),
                'bounce_rate': result.get('marketing_data', {}).get('conversion_metrics', {}).get('bounce_rate'),
                'organic_traffic': result.get('marketing_data', {}).get('traffic_sources', {}).get('organic_search'),
                'paid_traffic': result.get('marketing_data', {}).get('traffic_sources', {}).get('paid_search')
            }
            csv_data.append(row)
        
        csv_file = f"{filename}_summary.csv"
        df = pd.DataFrame(csv_data)
        df.to_csv(csv_file, index=False)
        
        logger.info(f"Results saved to {json_file} and {csv_file}")
        return json_file, csv_file

async def main():
    """Main execution function."""
    # Load prospects from your existing data
    prospects_file = "arco/consolidated_prospects.csv"  # Adjust path as needed
    
    if not os.path.exists(prospects_file):
        logger.error(f"Prospects file not found: {prospects_file}")
        return
    
    # Load prospects
    df = pd.read_csv(prospects_file)
    prospects = []
    
    for _, row in df.iterrows():
        # Extract domain from website URL
        website = row.get('Website', '')
        domain = website.replace('http://', '').replace('https://', '').replace('www.', '').split('/')[0] if website else ''
        
        # Skip if no valid domain
        if not domain:
            continue
            
        prospect = Prospect(
            domain=domain,
            company_name=row.get('Company Name for Emails', row.get('Company', '')),
            industry=row.get('Industry', ''),
            employee_count=row.get('# Employees'),
            revenue=row.get('Annual Revenue'),
            website=website
        )
        prospects.append(prospect)
    
    logger.info(f"Loaded {len(prospects)} prospects for analysis")
    
    # Initialize pipeline
    pipeline = MarketingAnalysisPipeline()
    
    # Run analysis
    logger.info("Starting marketing analysis pipeline...")
    results = await pipeline.analyze_prospects_batch(prospects, batch_size=5)
    
    # Save results
    json_file, csv_file = pipeline.save_results(results)
    
    # Print summary
    total_prospects = len(results)
    successful_analyses = len([r for r in results if r.get('confidence_score', 0) > 0])
    total_waste = sum(r.get('waste_analysis', {}).get('annual_savings_potential', 0) for r in results)
    
    print(f"\n=== MARKETING ANALYSIS SUMMARY ===")
    print(f"Total prospects analyzed: {total_prospects}")
    print(f"Successful analyses: {successful_analyses}")
    print(f"Success rate: {successful_analyses/total_prospects*100:.1f}%")
    print(f"Total annual savings potential: ${total_waste:,.0f}")
    print(f"Average savings per prospect: ${total_waste/total_prospects:,.0f}")
    print(f"\nResults saved to:")
    print(f"- Detailed: {json_file}")
    print(f"- Summary: {csv_file}")

if __name__ == "__main__":
    asyncio.run(main())