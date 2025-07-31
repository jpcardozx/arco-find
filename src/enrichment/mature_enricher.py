#!/usr/bin/env python3
"""
🎯 MATURE PROSPECT ENRICHMENT SYSTEM
Sistema sóbrio e controlado para enriquecimento de prospects
Foco em APIs estáveis, custos controlados e insights acionáveis
"""

import requests
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EnrichmentCosts:
    """Track enrichment costs per prospect"""
    pagespeed_calls: int = 0
    searchapi_calls: int = 0
    total_estimated_cost: float = 0.0
    
    def add_pagespeed_call(self):
        self.pagespeed_calls += 1
        self.total_estimated_cost += 0.005  # $0.005 per call
    
    def add_searchapi_call(self):
        self.searchapi_calls += 1
        self.total_estimated_cost += 0.02   # $0.02 per call
    
    def get_summary(self) -> Dict:
        return {
            'pagespeed_calls': self.pagespeed_calls,
            'searchapi_calls': self.searchapi_calls,
            'total_cost': round(self.total_estimated_cost, 3),
            'cost_per_prospect': round(self.total_estimated_cost, 3)
        }

class MatureProspectEnricher:
    """
    Sistema maduro de enriquecimento com controle de custos e rate limiting
    """
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.costs = EnrichmentCosts()
        self.rate_limit_delay = 1.0  # 1 second between calls
        self.last_api_call = 0
        
        # Load API config
        try:
            from config.api_keys import APIConfig
            self.config = APIConfig()
            logger.info("✅ API configuration loaded")
        except ImportError:
            logger.error("❌ Failed to load API configuration")
            self.config = None
    
    def _respect_rate_limit(self):
        """Ensure we respect API rate limits"""
        now = time.time()
        if now - self.last_api_call < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - (now - self.last_api_call)
            time.sleep(sleep_time)
        self.last_api_call = time.time()
    
    def clean_domain(self, domain: str) -> str:
        """Clean and validate domain"""
        if not domain:
            return ""
        
        # Remove protocol and path
        import re
        domain = re.sub(r'^https?://', '', domain)
        domain = re.sub(r'/.*$', '', domain)
        domain = re.sub(r' › .*$', '', domain)  # Remove breadcrumb paths
        domain = re.sub(r' \|.*$', '', domain)  # Remove pipe separators
        domain = re.sub(r' -.*$', '', domain)   # Remove dash separators
        domain = re.sub(r'\s+', '', domain)     # Remove all whitespace
        domain = domain.split('›')[0].strip()   # Take only first part before ›
        domain = domain.split('|')[0].strip()   # Take only first part before |
        domain = domain.lower().strip()
        
        # Basic domain validation
        if '.' not in domain or len(domain) < 4 or ' ' in domain:
            return ""
            
        # Ensure it's a valid domain format
        if not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', domain):
            return ""
            
        return domain
    
    def get_website_performance(self, domain: str) -> Dict:
        """
        Get website performance with controlled API usage
        Returns structured performance data
        """
        clean_domain = self.clean_domain(domain)
        if not clean_domain:
            return self._empty_performance_data()
        
        if self.dry_run:
            self.costs.add_pagespeed_call()
            return self._mock_performance_data(clean_domain)
        
        if not self.config or not self.config.GOOGLE_PAGESPEED_API_KEY:
            logger.warning("⚠️ PageSpeed API not configured")
            return self._empty_performance_data()
        
        try:
            self._respect_rate_limit()
            
            url = f"https://{clean_domain}"
            api_url = "https://www.googleapis.com/pagespeed/insights/v5/runPagespeed"
            
            params = {
                'url': url,
                'key': self.config.GOOGLE_PAGESPEED_API_KEY,
                'category': ['performance', 'accessibility', 'best-practices', 'seo'],
                'strategy': 'desktop'
            }
            
            response = requests.get(api_url, params=params, timeout=15)
            self.costs.add_pagespeed_call()
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_pagespeed_data(data)
            else:
                logger.warning(f"⚠️ PageSpeed API error {response.status_code} for {domain}")
                return self._empty_performance_data()
                
        except Exception as e:
            logger.error(f"❌ PageSpeed check failed for {domain}: {e}")
            return self._empty_performance_data()
    
    def _parse_pagespeed_data(self, data: Dict) -> Dict:
        """Parse PageSpeed Insights response"""
        lighthouse = data.get('lighthouseResult', {})
        categories = lighthouse.get('categories', {})
        
        # Extract scores
        performance = categories.get('performance', {}).get('score', 0) * 100
        accessibility = categories.get('accessibility', {}).get('score', 0) * 100
        best_practices = categories.get('best-practices', {}).get('score', 0) * 100
        seo = categories.get('seo', {}).get('score', 0) * 100
        
        # Calculate overall score
        overall_score = (performance + accessibility + best_practices + seo) / 4
        
        return {
            'performance_score': round(performance, 1),
            'accessibility_score': round(accessibility, 1),
            'best_practices_score': round(best_practices, 1),
            'seo_score': round(seo, 1),
            'overall_score': round(overall_score, 1),
            'website_status': 'active',
            'last_checked': datetime.now().isoformat(),
            'needs_improvement': overall_score < 70
        }
    
    def _mock_performance_data(self, domain: str) -> Dict:
        """Generate realistic mock data for dry run"""
        # Generate realistic scores based on domain patterns
        base_score = 65
        if any(pattern in domain for pattern in ['.ca', 'dental', 'medical']):
            base_score = 72  # Professional sites tend to be better
        elif any(pattern in domain for pattern in ['beauty', 'spa']):
            base_score = 58  # Often image-heavy, slower
        
        performance = max(30, min(95, base_score + hash(domain) % 20 - 10))
        
        return {
            'performance_score': performance,
            'accessibility_score': performance + 5,
            'best_practices_score': performance - 3,
            'seo_score': performance + 2,
            'overall_score': performance,
            'website_status': 'active',
            'last_checked': datetime.now().isoformat(),
            'needs_improvement': performance < 70,
            'dry_run': True
        }
    
    def _empty_performance_data(self) -> Dict:
        """Return empty performance data structure"""
        return {
            'performance_score': 0,
            'accessibility_score': 0,
            'best_practices_score': 0,
            'seo_score': 0,
            'overall_score': 0,
            'website_status': 'unknown',
            'last_checked': datetime.now().isoformat(),
            'needs_improvement': True
        }
    
    def calculate_digital_maturity(self, prospect: Dict, performance_data: Dict) -> Dict:
        """
        Calculate digital maturity score based on multiple factors
        Returns actionable insights for outreach
        """
        business_type = prospect.get('business_type', '').lower()
        market_region = prospect.get('market_region', '')
        overall_score = performance_data.get('overall_score', 0)
        
        # Base maturity calculation
        maturity_factors = []
        
        # 1. Website performance (40% weight)
        if overall_score >= 80:
            maturity_factors.append(85)  # Excellent
        elif overall_score >= 70:
            maturity_factors.append(70)  # Good
        elif overall_score >= 50:
            maturity_factors.append(55)  # Average
        else:
            maturity_factors.append(30)  # Poor
        
        # 2. Industry digital adoption patterns (30% weight)
        industry_adoption = {
            'dental': 65, 'medical': 60, 'legal': 55, 'accounting': 75,
            'beauty': 70, 'real_estate': 80, 'physiotherapy': 60
        }
        maturity_factors.append(industry_adoption.get(business_type, 60))
        
        # 3. Geographic tech adoption (20% weight)
        geo_factor = 60  # Default
        if any(city in market_region for city in ['Vancouver', 'Toronto', 'Seattle']):
            geo_factor = 80
        elif any(city in market_region for city in ['Calgary', 'Montreal']):
            geo_factor = 70
        maturity_factors.append(geo_factor)
        
        # 4. Revenue size indicator (10% weight)
        revenue = prospect.get('estimated_monthly_revenue', 0)
        if revenue >= 150000:
            maturity_factors.append(80)  # Larger businesses = more tech
        elif revenue >= 100000:
            maturity_factors.append(70)
        else:
            maturity_factors.append(60)
        
        # Calculate weighted average
        weights = [0.4, 0.3, 0.2, 0.1]
        maturity_score = sum(factor * weight for factor, weight in zip(maturity_factors, weights))
        
        return {
            'digital_maturity_score': round(maturity_score, 1),
            'technology_readiness': self._get_readiness_level(maturity_score),
            'primary_opportunity': self._identify_opportunity(performance_data),
            'improvement_priority': self._get_improvement_priority(performance_data),
            'estimated_impact_months': self._estimate_impact_timeline(maturity_score)
        }
    
    def _get_readiness_level(self, score: float) -> str:
        """Determine technology readiness level"""
        if score >= 75:
            return 'High'
        elif score >= 60:
            return 'Medium'
        elif score >= 45:
            return 'Low'
        else:
            return 'Critical'
    
    def _identify_opportunity(self, performance_data: Dict) -> str:
        """Identify primary improvement opportunity"""
        scores = {
            'performance': performance_data.get('performance_score', 0),
            'accessibility': performance_data.get('accessibility_score', 0),
            'seo': performance_data.get('seo_score', 0),
            'best_practices': performance_data.get('best_practices_score', 0)
        }
        
        # Find lowest scoring area
        lowest_area = min(scores.items(), key=lambda x: x[1])
        
        opportunities = {
            'performance': 'Website Speed Optimization',
            'accessibility': 'Accessibility & UX Improvements',
            'seo': 'SEO & Content Strategy',
            'best_practices': 'Technical Standards & Security'
        }
        
        return opportunities.get(lowest_area[0], 'Digital Modernization')
    
    def _get_improvement_priority(self, performance_data: Dict) -> str:
        """Get improvement priority level"""
        overall = performance_data.get('overall_score', 0)
        
        if overall < 50:
            return 'Urgent'
        elif overall < 70:
            return 'High'
        elif overall < 85:
            return 'Medium'
        else:
            return 'Low'
    
    def _estimate_impact_timeline(self, maturity_score: float) -> int:
        """Estimate months to see impact"""
        if maturity_score >= 70:
            return 2  # Quick wins
        elif maturity_score >= 50:
            return 4  # Medium effort
        else:
            return 6  # Significant work needed
    
    def generate_outreach_insights(self, prospect: Dict, enrichment_data: Dict) -> Dict:
        """
        Generate actionable insights for outreach
        Focus on specific, measurable opportunities
        """
        business_type = prospect.get('business_type', '').title()
        fit_score = prospect.get('overall_fit_score', 0)
        monthly_revenue = prospect.get('estimated_monthly_revenue', 0)
        
        performance = enrichment_data.get('performance_score', 0)
        maturity = enrichment_data.get('digital_maturity_score', 0)
        opportunity = enrichment_data.get('primary_opportunity', '')
        priority = enrichment_data.get('improvement_priority', '')
        
        # Generate specific talking points
        talking_points = []
        
        # Performance-based insights
        if performance < 50:
            talking_points.append(f"Website loading {50-performance:.0f}% slower than industry standard")
        elif performance < 70:
            talking_points.append("Page speed optimizations could improve user experience")
        
        # Revenue-based insights
        monthly_k = monthly_revenue / 1000
        if monthly_revenue >= 100000:
            talking_points.append(f"${monthly_k:.0f}k/month business - significant ROI potential")
        
        # Industry-specific insights
        industry_insights = {
            'Dental': "Patient booking optimization typically increases appointments 15-25%",
            'Legal': "Professional website credibility directly impacts client acquisition",
            'Medical': "Accessibility compliance critical for healthcare websites",
            'Accounting': "Trust signals essential for financial services online presence"
        }
        
        if business_type in industry_insights:
            talking_points.append(industry_insights[business_type])
        
        return {
            'outreach_priority': self._calculate_outreach_priority(fit_score, maturity, monthly_revenue),
            'primary_pain_point': opportunity,
            'urgency_level': priority,
            'talking_points': talking_points[:3],  # Top 3 points
            'estimated_monthly_impact': self._estimate_monthly_impact(monthly_revenue, performance),
            'follow_up_timeline': self._get_follow_up_timeline(priority),
            'success_probability': self._calculate_success_probability(fit_score, maturity)
        }
    
    def _calculate_outreach_priority(self, fit_score: float, maturity: float, revenue: float) -> str:
        """Calculate overall outreach priority"""
        priority_score = (fit_score * 0.4) + ((100 - maturity) * 0.3) + (min(revenue/200000, 1) * 0.3)
        
        if priority_score >= 0.8:
            return 'Platinum'
        elif priority_score >= 0.7:
            return 'Gold'
        elif priority_score >= 0.6:
            return 'Silver'
        else:
            return 'Bronze'
    
    def _estimate_monthly_impact(self, revenue: float, performance: float) -> float:
        """Estimate potential monthly impact"""
        # Conservative impact estimation
        base_impact = revenue * 0.05  # 5% base improvement
        
        # Performance penalty factor
        if performance < 50:
            base_impact *= 1.5  # 50% more impact for poor sites
        elif performance < 70:
            base_impact *= 1.2  # 20% more impact
        
        return round(base_impact, 0)
    
    def _get_follow_up_timeline(self, priority: str) -> str:
        """Get follow-up timeline based on priority"""
        timelines = {
            'Urgent': '24 hours',
            'High': '3 days',
            'Medium': '1 week',
            'Low': '2 weeks'
        }
        return timelines.get(priority, '1 week')
    
    def _calculate_success_probability(self, fit_score: float, maturity: float) -> float:
        """Calculate probability of successful conversion"""
        # Lower maturity = higher need = higher conversion probability
        need_factor = max(0.3, (100 - maturity) / 100)
        fit_factor = fit_score
        
        probability = (need_factor * 0.6) + (fit_factor * 0.4)
        return round(min(probability, 0.95), 2)  # Cap at 95%
    
    def enrich_prospect(self, prospect: Dict) -> Tuple[Dict, Dict]:
        """
        Main enrichment method - returns (enriched_prospect, costs)
        """
        domain = prospect.get('domain', '')
        
        logger.info(f"🔍 Enriching prospect: {prospect.get('company_name', 'Unknown')} ({domain})")
        
        # Get website performance
        performance_data = self.get_website_performance(domain)
        
        # Calculate digital maturity
        maturity_data = self.calculate_digital_maturity(prospect, performance_data)
        
        # Generate outreach insights
        insights_data = self.generate_outreach_insights(prospect, {**performance_data, **maturity_data})
        
        # Combine all enrichment data
        enriched_prospect = {
            **prospect,
            'enrichment': {
                'performance': performance_data,
                'digital_maturity': maturity_data,
                'outreach_insights': insights_data,
                'enriched_at': datetime.now().isoformat(),
                'dry_run': self.dry_run
            }
        }
        
        return enriched_prospect, self.costs.get_summary()
    
    def enrich_prospect_list(self, prospects: List[Dict], max_prospects: int = None) -> Tuple[List[Dict], Dict]:
        """
        Enrich multiple prospects with cost tracking
        """
        if max_prospects:
            prospects = prospects[:max_prospects]
        
        logger.info(f"🚀 Starting enrichment for {len(prospects)} prospects")
        
        enriched_prospects = []
        start_time = time.time()
        
        for i, prospect in enumerate(prospects, 1):
            logger.info(f"Processing {i}/{len(prospects)}: {prospect.get('company_name', 'Unknown')}")
            
            enriched_prospect, _ = self.enrich_prospect(prospect)
            enriched_prospects.append(enriched_prospect)
            
            # Progress update every 10 prospects
            if i % 10 == 0:
                logger.info(f"✅ Processed {i}/{len(prospects)} prospects")
        
        total_time = time.time() - start_time
        final_costs = self.costs.get_summary()
        final_costs['total_time_seconds'] = round(total_time, 1)
        final_costs['prospects_processed'] = len(enriched_prospects)
        
        logger.info(f"🎯 Enrichment complete: {len(enriched_prospects)} prospects in {total_time:.1f}s")
        logger.info(f"💰 Total estimated cost: ${final_costs['total_cost']:.3f}")
        
        return enriched_prospects, final_costs

# Example usage
if __name__ == "__main__":
    # Example prospect
    sample_prospect = {
        'company_name': 'Sample Dental Clinic',
        'domain': 'sampleclinic.ca',
        'business_type': 'dental',
        'market_region': 'Vancouver, BC',
        'estimated_monthly_revenue': 120000,
        'overall_fit_score': 0.85
    }
    
    # Test with dry run
    enricher = MatureProspectEnricher(dry_run=True)
    enriched, costs = enricher.enrich_prospect(sample_prospect)
    
    print("🎯 Sample Enrichment Result:")
    print(json.dumps(enriched['enrichment'], indent=2))
    print(f"\n💰 Costs: {costs}")
