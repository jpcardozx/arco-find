#!/usr/bin/env python3
"""
ARCO DISCOVERY ENGINE - Consolidated Final Version
================================================

STRATEGIC FOCUS:
✓ Real pain signals via cross-data marketing + performance analysis
✓ Realistic SME budgets based on UK market research
✓ Web development opportunity inference from ad performance issues
✓ Cost-optimized BigQuery execution (<$0.01 USD per run)
✓ Quality over quantity: 8-12 qualified prospects per execution

METHODOLOGY:
- Pain Signal Detection: Creative fatigue + budget inefficiency patterns
- Business Intelligence: Company sizing + spend estimation
- Web Opportunity Scoring: Poor ad performance = likely poor website
- ROI Projection: Ad waste indicates digital strategy needs
"""

import asyncio
import json
import logging
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from google.cloud import bigquery
import os

# Configure strategic logging (Windows compatible)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - ARCO - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/arco_discovery.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class WebOpportunity:
    """Web development opportunity inferred from ad performance"""
    opportunity_type: str  # 'website_refresh', 'landing_page_optimization', 'digital_strategy'
    evidence: List[str]    # Specific ad performance issues supporting web opportunity
    estimated_value: int   # £ value for web project
    confidence_level: str  # 'high', 'medium', 'low'
    timeline: str         # Estimated delivery timeline
    deliverables: List[str] # Specific web deliverables

@dataclass
class ArcoProspect:
    """Complete prospect profile with web development opportunities"""
    # Core Business Data
    company_name: str
    location: str
    vertical: str  # 'aesthetic', 'estate', 'legal', 'dental'
    
    # Marketing Intelligence (from ads)
    ad_volume: int
    creative_diversity: float
    creative_age_estimate: int  # Days since last creative refresh
    estimated_monthly_ad_spend: int
    
    # Performance Analysis
    waste_probability: float  # 0-1 probability of ad spend waste
    performance_issues: List[str]
    monthly_waste_estimate: int  # £ estimated monthly waste
    
    # Business Intelligence
    company_size: str  # 'micro', 'small', 'medium'
    staff_estimate: int
    market_segment: str  # 'premium', 'standard', 'budget'
    
    # Web Development Opportunity
    web_opportunity: WebOpportunity
    total_digital_opportunity: int  # Ad optimization + Web project value
    
    # Strategic Scoring
    opportunity_score: float  # 0-100 comprehensive opportunity score
    priority_level: str  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    
    # Outreach Strategy
    primary_pain_point: str
    value_proposition: str
    contact_approach: str

class ArcoDiscoveryEngine:
    """Consolidated discovery engine for digital marketing opportunities"""
    
    def __init__(self):
        self.client = bigquery.Client()
        logger.info("ARCO Discovery Engine initialized - Integrated ad + web opportunity detection")
        
        # Realistic budget benchmarks (UK market research)
        self.budget_benchmarks = {
            'aesthetic': {
                'micro': {'ad_spend': (150, 400), 'web_value': (5000, 15000)},
                'small': {'ad_spend': (400, 800), 'web_value': (10000, 25000)},
                'medium': {'ad_spend': (800, 1500), 'web_value': (20000, 50000)}
            },
            'estate': {
                'micro': {'ad_spend': (200, 500), 'web_value': (3000, 10000)},
                'small': {'ad_spend': (500, 1000), 'web_value': (8000, 20000)},
                'medium': {'ad_spend': (1000, 2000), 'web_value': (15000, 40000)}
            },
            'legal': {
                'micro': {'ad_spend': (300, 600), 'web_value': (4000, 12000)},
                'small': {'ad_spend': (600, 1200), 'web_value': (10000, 25000)},
                'medium': {'ad_spend': (1200, 2500), 'web_value': (20000, 60000)}
            },
            'dental': {
                'micro': {'ad_spend': (200, 500), 'web_value': (4000, 12000)},
                'small': {'ad_spend': (500, 1000), 'web_value': (8000, 22000)},
                'medium': {'ad_spend': (1000, 2000), 'web_value': (18000, 45000)}
            }
        }
        
        # Performance issue detection patterns (CORRECTED LOGIC)
        self.pain_signal_patterns = {
            'creative_fatigue': {
                'threshold': 0.35,  # Creative diversity < 35% = PROBLEM (reusing same ads)
                'web_impact': 'high',  # Strong correlation with outdated website
                'web_opportunity': 'website_refresh'
            },
            'good_testing_practice': {
                'threshold': 0.75,  # Creative diversity > 75% = GOOD PRACTICE (not a problem)
                'web_impact': 'low',  # High diversity indicates sophisticated marketing
                'web_opportunity': 'advanced_optimization'  
            },
            'budget_inefficiency': {
                'ad_threshold': 20,  # >20 ads for SMEs (adjusted from 40)
                'web_impact': 'high',  # Poor ad performance often indicates poor website
                'web_opportunity': 'digital_strategy'
            }
        }

    async def discover_prospects(self, max_prospects: int = 12) -> List[ArcoProspect]:
        """Execute comprehensive prospect discovery"""
        
        logger.info(">> Starting ARCO discovery - integrated ad + web opportunity analysis")
        
        # Execute optimized BigQuery discovery
        raw_prospects = await self._execute_discovery_query()
        
        if not raw_prospects:
            logger.warning("No prospects found in BigQuery execution")
            return []
        
        # Analyze and enrich prospects
        enriched_prospects = []
        for raw_data in raw_prospects:
            prospect = await self._analyze_prospect(raw_data)
            if prospect and prospect.opportunity_score >= 60:  # Quality threshold
                enriched_prospects.append(prospect)
        
        # Sort by opportunity score and limit results
        final_prospects = sorted(enriched_prospects, 
                               key=lambda x: x.opportunity_score, 
                               reverse=True)[:max_prospects]
        
        logger.info(f">> Discovery complete: {len(final_prospects)} qualified prospects")
        return final_prospects

    async def _execute_discovery_query(self) -> List[Dict]:
        """Execute cost-optimized BigQuery discovery query"""
        
        query = """
        WITH prospect_analysis AS (
            SELECT 
                advertiser_disclosed_name,
                advertiser_location,
                
                -- Marketing metrics
                COUNT(*) as ad_volume,
                COUNT(DISTINCT creative_id) as creative_count,
                ROUND(COUNT(DISTINCT creative_id) / COUNT(*), 3) as creative_diversity,
                
                -- Performance indicators
                CASE 
                    WHEN COUNT(*) > 40 AND (COUNT(DISTINCT creative_id) / COUNT(*)) < 0.3 
                    THEN 0.85  -- High volume, low diversity = major waste
                    WHEN COUNT(*) > 60 AND (COUNT(DISTINCT creative_id) / COUNT(*)) > 0.8
                    THEN 0.25  -- High diversity = sophisticated marketing (good practice)
                    WHEN COUNT(*) BETWEEN 20 AND 60 AND (COUNT(DISTINCT creative_id) / COUNT(*)) BETWEEN 0.3 AND 0.7
                    THEN 0.45  -- Reasonable approach
                    ELSE 0.65  -- Default moderate waste
                END as waste_probability,
                
                -- Creative age estimation (approximate)
                COUNT(*) / 4 as estimated_creative_age,  -- Rough proxy: more ads = longer campaign
                
                -- Vertical classification
                CASE 
                    WHEN LOWER(advertiser_disclosed_name) LIKE '%clinic%'
                         OR LOWER(advertiser_disclosed_name) LIKE '%aesthetic%'
                         OR LOWER(advertiser_disclosed_name) LIKE '%beauty%'
                         OR LOWER(advertiser_disclosed_name) LIKE '%cosmetic%'
                         OR LOWER(advertiser_disclosed_name) LIKE '%dermal%'
                         OR LOWER(advertiser_disclosed_name) LIKE '%laser%'
                    THEN 'aesthetic'
                    WHEN LOWER(advertiser_disclosed_name) LIKE '%estate%'
                         OR LOWER(advertiser_disclosed_name) LIKE '%property%'
                         OR LOWER(advertiser_disclosed_name) LIKE '%homes%'
                         OR LOWER(advertiser_disclosed_name) LIKE '%lettings%'
                         OR LOWER(advertiser_disclosed_name) LIKE '%realty%'
                    THEN 'estate'
                    WHEN LOWER(advertiser_disclosed_name) LIKE '%law%'
                         OR LOWER(advertiser_disclosed_name) LIKE '%legal%'
                         OR LOWER(advertiser_disclosed_name) LIKE '%solicitor%'
                         OR LOWER(advertiser_disclosed_name) LIKE '%barrister%'
                         OR LOWER(advertiser_disclosed_name) LIKE '%attorney%'
                    THEN 'legal'
                    WHEN LOWER(advertiser_disclosed_name) LIKE '%dental%'
                         OR LOWER(advertiser_disclosed_name) LIKE '%dentist%'
                         OR LOWER(advertiser_disclosed_name) LIKE '%orthodontist%'
                         OR LOWER(advertiser_disclosed_name) LIKE '%implant%'
                    THEN 'dental'
                    ELSE 'other'
                END as vertical
                
            FROM `bigquery-public-data.google_ads_transparency_center.creative_stats`
            WHERE advertiser_location IN ('GB', 'IE', 'AU', 'NZ', 'CA')  -- English-speaking markets
                AND (
                    -- Aesthetic keywords
                    LOWER(advertiser_disclosed_name) LIKE '%clinic%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%aesthetic%' 
                    OR LOWER(advertiser_disclosed_name) LIKE '%beauty%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%cosmetic%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%dermal%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%laser%'
                    -- Estate keywords
                    OR LOWER(advertiser_disclosed_name) LIKE '%estate%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%property%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%homes%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%lettings%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%realty%'
                    -- Legal keywords  
                    OR LOWER(advertiser_disclosed_name) LIKE '%law%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%legal%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%solicitor%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%barrister%'
                    -- Dental keywords
                    OR LOWER(advertiser_disclosed_name) LIKE '%dental%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%dentist%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%orthodontist%'
                )
                -- Exclude large corporations and platforms
                AND NOT (
                    LOWER(advertiser_disclosed_name) LIKE '%rightmove%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%zoopla%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%hospital%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%nhs%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%university%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%college%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%group%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%holdings%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%international%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%global%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%network%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%platform%'
                )
            GROUP BY advertiser_disclosed_name, advertiser_location
            HAVING ad_volume BETWEEN 5 AND 25  -- True SME range (micro/small businesses)
                AND vertical != 'other'
                AND waste_probability >= 0.5  -- Focus on real opportunities
        )
        
        SELECT * FROM prospect_analysis
        ORDER BY waste_probability DESC, ad_volume DESC
        LIMIT 20
        """
        
        try:
            logger.info(">> Executing discovery query...")
            query_job = self.client.query(query)
            results = query_job.result()
            
            prospects = []
            for row in results:
                prospects.append({
                    'company_name': row.advertiser_disclosed_name,
                    'location': row.advertiser_location,
                    'vertical': row.vertical,
                    'ad_volume': row.ad_volume,
                    'creative_count': row.creative_count,
                    'creative_diversity': row.creative_diversity,
                    'waste_probability': row.waste_probability,
                    'estimated_creative_age': min(int(row.estimated_creative_age), 365)  # Cap at 1 year
                })
            
            logger.info(f">> Query complete: {len(prospects)} raw prospects found")
            return prospects
            
        except Exception as e:
            logger.error(f">> Query failed: {e}")
            return []

    async def _analyze_prospect(self, raw_data: Dict) -> Optional[ArcoProspect]:
        """Analyze raw prospect data and create enriched prospect profile"""
        
        try:
            # Determine company size and estimates
            company_size = self._estimate_company_size(raw_data['ad_volume'], raw_data['vertical'])
            staff_estimate = self._estimate_staff_count(company_size, raw_data['vertical'])
            
            # Calculate realistic budget estimates
            budget_range = self.budget_benchmarks[raw_data['vertical']][company_size]['ad_spend']
            estimated_ad_spend = int((budget_range[0] + budget_range[1]) / 2)
            
            # Identify performance issues
            performance_issues = self._identify_performance_issues(raw_data)
            monthly_waste = int(estimated_ad_spend * raw_data['waste_probability'])
            
            # Analyze web development opportunity
            web_opportunity = self._analyze_web_opportunity(raw_data, performance_issues, company_size)
            
            # Calculate total digital opportunity value
            ad_optimization_value = monthly_waste * 6  # 6 months savings
            total_opportunity = ad_optimization_value + web_opportunity.estimated_value
            
            # Calculate comprehensive opportunity score
            opportunity_score = self._calculate_opportunity_score(
                raw_data, estimated_ad_spend, performance_issues, web_opportunity
            )
            
            # Determine priority level
            priority_level = self._determine_priority(opportunity_score, raw_data['vertical'])
            
            # Market segment classification
            market_segment = self._classify_market_segment(estimated_ad_spend, raw_data['vertical'])
            
            # Generate outreach strategy
            primary_pain_point = self._generate_pain_point(performance_issues, raw_data)
            value_proposition = self._generate_value_proposition(raw_data, web_opportunity)
            contact_approach = self._generate_contact_approach(raw_data['vertical'], company_size)
            
            prospect = ArcoProspect(
                company_name=raw_data['company_name'],
                location=raw_data['location'],
                vertical=raw_data['vertical'],
                ad_volume=raw_data['ad_volume'],
                creative_diversity=raw_data['creative_diversity'],
                creative_age_estimate=raw_data['estimated_creative_age'],
                estimated_monthly_ad_spend=estimated_ad_spend,
                waste_probability=raw_data['waste_probability'],
                performance_issues=performance_issues,
                monthly_waste_estimate=monthly_waste,
                company_size=company_size,
                staff_estimate=staff_estimate,
                market_segment=market_segment,
                web_opportunity=web_opportunity,
                total_digital_opportunity=total_opportunity,
                opportunity_score=opportunity_score,
                priority_level=priority_level,
                primary_pain_point=primary_pain_point,
                value_proposition=value_proposition,
                contact_approach=contact_approach
            )
            
            return prospect
            
        except Exception as e:
            logger.error(f">> Failed to analyze prospect {raw_data.get('company_name', 'Unknown')}: {e}")
            return None

    def _estimate_company_size(self, ad_volume: int, vertical: str) -> str:
        """Estimate company size based on ad volume and vertical"""
        
        # Vertical-specific size indicators
        size_thresholds = {
            'aesthetic': {'small_threshold': 35, 'medium_threshold': 80},
            'estate': {'small_threshold': 30, 'medium_threshold': 70},
            'legal': {'small_threshold': 25, 'medium_threshold': 60},
            'dental': {'small_threshold': 30, 'medium_threshold': 75}
        }
        
        thresholds = size_thresholds.get(vertical, {'small_threshold': 30, 'medium_threshold': 70})
        
        if ad_volume >= thresholds['medium_threshold']:
            return 'medium'
        elif ad_volume >= thresholds['small_threshold']:
            return 'small'
        else:
            return 'micro'

    def _estimate_staff_count(self, company_size: str, vertical: str) -> int:
        """Estimate staff count based on company size and vertical"""
        
        staff_estimates = {
            'aesthetic': {'micro': 4, 'small': 9, 'medium': 18},
            'estate': {'micro': 3, 'small': 8, 'medium': 16},
            'legal': {'micro': 5, 'small': 12, 'medium': 25},
            'dental': {'micro': 4, 'small': 8, 'medium': 15}
        }
        
        return staff_estimates.get(vertical, {'micro': 4, 'small': 9, 'medium': 18})[company_size]

    def _identify_performance_issues(self, raw_data: Dict) -> List[str]:
        """Identify specific performance issues from ad patterns"""
        
        issues = []
        
        # Creative fatigue detection (LOW diversity = PROBLEM)
        if raw_data['creative_diversity'] < self.pain_signal_patterns['creative_fatigue']['threshold']:
            issues.append("Creative fatigue - limited ad variation reducing effectiveness")
        
        # Good testing practice detection (HIGH diversity = POSITIVE SIGNAL, not a problem)
        if raw_data['creative_diversity'] > self.pain_signal_patterns['good_testing_practice']['threshold']:
            issues.append("Sophisticated creative testing - indicates advanced marketing approach")
        
        # Budget inefficiency detection (adjusted for SME scale)
        if (raw_data['ad_volume'] > self.pain_signal_patterns['budget_inefficiency']['ad_threshold'] and 
            raw_data['creative_diversity'] < 0.4):
            issues.append("Budget inefficiency - high SME ad volume with poor creative strategy")
        
        # Stale campaign detection
        if raw_data['estimated_creative_age'] > 120:
            issues.append("Campaign staleness - ads likely unchanged for 4+ months")
        
        # High waste probability
        if raw_data['waste_probability'] > 0.8:
            issues.append("Critical waste patterns - multiple efficiency red flags")
        
        return issues

    def _analyze_web_opportunity(self, raw_data: Dict, performance_issues: List[str], 
                               company_size: str) -> WebOpportunity:
        """Analyze web development opportunity based on ad performance issues"""
        
        # Determine web opportunity type based on ad issues
        web_evidence = []
        opportunity_type = "landing_page_optimization"  # Default
        confidence = "medium"
        
        # Creative fatigue suggests outdated website
        if any("Creative fatigue" in issue for issue in performance_issues):
            web_evidence.append("Creative fatigue indicates likely outdated website design")
            opportunity_type = "website_refresh"
            confidence = "high"
        
        # Campaign staleness suggests digital neglect
        if any("Campaign staleness" in issue for issue in performance_issues):
            web_evidence.append("Stale campaigns suggest digital assets need comprehensive update")
            if opportunity_type != "website_refresh":
                opportunity_type = "digital_strategy"
            confidence = "high"
        
        # Budget inefficiency suggests poor funnel
        if any("Budget inefficiency" in issue for issue in performance_issues):
            web_evidence.append("Ad budget waste indicates poor landing page conversion")
            if opportunity_type == "landing_page_optimization":
                confidence = "high"
        
        # High waste probability suggests system-wide digital issues
        if raw_data['waste_probability'] > 0.75:
            web_evidence.append("High ad waste probability suggests comprehensive digital strategy issues")
            opportunity_type = "digital_strategy"
            confidence = "high"
        
        # Calculate web project value
        vertical = raw_data['vertical']
        web_value_range = self.budget_benchmarks[vertical][company_size]['web_value']
        
        # Adjust value based on opportunity type
        value_multipliers = {
            'landing_page_optimization': 0.4,  # Lower end of range
            'website_refresh': 0.7,           # Mid-high range
            'digital_strategy': 1.0           # Full range
        }
        
        base_value = int((web_value_range[0] + web_value_range[1]) / 2)
        estimated_value = int(base_value * value_multipliers[opportunity_type])
        
        # Timeline estimation
        timeline_map = {
            'landing_page_optimization': '3-4 weeks',
            'website_refresh': '6-8 weeks', 
            'digital_strategy': '8-12 weeks'
        }
        
        # Deliverables based on opportunity type
        deliverables_map = {
            'landing_page_optimization': [
                'Landing page performance audit',
                'Conversion rate optimization', 
                'A/B testing framework setup',
                'Performance tracking implementation'
            ],
            'website_refresh': [
                'Complete website redesign',
                'Mobile optimization',
                'SEO foundation setup',
                'Content management system upgrade',
                'Performance optimization'
            ],
            'digital_strategy': [
                'Comprehensive digital audit',
                'Website redesign and development',
                'SEO and content strategy',
                'Marketing automation setup',
                'Analytics and conversion tracking',
                'Ongoing optimization framework'
            ]
        }
        
        return WebOpportunity(
            opportunity_type=opportunity_type,
            evidence=web_evidence,
            estimated_value=estimated_value,
            confidence_level=confidence,
            timeline=timeline_map[opportunity_type],
            deliverables=deliverables_map[opportunity_type]
        )

    def _calculate_opportunity_score(self, raw_data: Dict, estimated_ad_spend: int, 
                                   performance_issues: List[str], web_opportunity: WebOpportunity) -> float:
        """Calculate comprehensive opportunity score (0-100)"""
        
        score = 40  # Base score
        
        # Ad performance factors (30 points max)
        score += (raw_data['waste_probability'] * 25)  # Higher waste = higher opportunity
        score += (len(performance_issues) * 2)         # More issues = more opportunity
        
        # Budget capacity factors (15 points max)
        if estimated_ad_spend >= 800:
            score += 15
        elif estimated_ad_spend >= 500:
            score += 10
        elif estimated_ad_spend >= 300:
            score += 5
        
        # Web opportunity factors (15 points max)
        web_confidence_scores = {'high': 15, 'medium': 10, 'low': 5}
        score += web_confidence_scores[web_opportunity.confidence_level]
        
        # Vertical premium (10 points max)
        vertical_premiums = {'aesthetic': 10, 'legal': 8, 'dental': 6, 'estate': 4}
        score += vertical_premiums.get(raw_data['vertical'], 0)
        
        return min(score, 100)

    def _determine_priority(self, opportunity_score: float, vertical: str) -> str:
        """Determine strategic priority level"""
        
        # Adjust thresholds by vertical
        premium_verticals = ['aesthetic', 'legal']
        threshold_adjustment = 5 if vertical in premium_verticals else 0
        
        if opportunity_score >= (85 - threshold_adjustment):
            return "CRITICAL"
        elif opportunity_score >= (75 - threshold_adjustment):
            return "HIGH"
        elif opportunity_score >= (65 - threshold_adjustment):
            return "MEDIUM"
        else:
            return "LOW"

    def _classify_market_segment(self, ad_spend: int, vertical: str) -> str:
        """Classify market segment based on spend and vertical"""
        
        segment_thresholds = {
            'aesthetic': {'premium': 700, 'standard': 300},
            'legal': {'premium': 900, 'standard': 400},
            'estate': {'premium': 600, 'standard': 300},
            'dental': {'premium': 600, 'standard': 250}
        }
        
        thresholds = segment_thresholds.get(vertical, {'premium': 700, 'standard': 350})
        
        if ad_spend >= thresholds['premium']:
            return 'premium'
        elif ad_spend >= thresholds['standard']:
            return 'standard'
        else:
            return 'budget'

    def _generate_pain_point(self, performance_issues: List[str], raw_data: Dict) -> str:
        """Generate primary pain point for outreach"""
        
        if not performance_issues:
            return f"Ad spend efficiency concerns with {raw_data['waste_probability']:.0%} waste probability"
        
        # Prioritize most impactful issues
        if any("Critical waste" in issue for issue in performance_issues):
            return "Multiple ad performance red flags indicate significant budget waste"
        elif any("Creative fatigue" in issue for issue in performance_issues):
            return "Creative stagnation limiting ad effectiveness and likely affecting website performance"
        elif any("Budget inefficiency" in issue for issue in performance_issues):
            return "High ad volume with poor optimization strategy wasting marketing budget"
        else:
            return performance_issues[0]  # Use first issue as fallback

    def _generate_value_proposition(self, raw_data: Dict, web_opportunity: WebOpportunity) -> str:
        """Generate value proposition combining ad and web opportunities"""
        
        vertical = raw_data['vertical']
        opportunity_type = web_opportunity.opportunity_type
        
        vertical_contexts = {
            'aesthetic': 'patient acquisition and brand positioning',
            'estate': 'property lead generation and market positioning',
            'legal': 'client acquisition and professional credibility',
            'dental': 'patient acquisition and practice growth'
        }
        
        context = vertical_contexts.get(vertical, 'customer acquisition')
        
        value_props = {
            'landing_page_optimization': f"Optimize {context} through improved ad performance and landing page conversion",
            'website_refresh': f"Comprehensive digital upgrade to improve {context} and reduce marketing waste",
            'digital_strategy': f"Complete digital transformation to maximize {context} efficiency and ROI"
        }
        
        return value_props[opportunity_type]

    def _generate_contact_approach(self, vertical: str, company_size: str) -> str:
        """Generate appropriate contact approach strategy"""
        
        approaches = {
            'aesthetic': {
                'micro': 'Direct approach highlighting patient acquisition cost reduction',
                'small': 'Consultative approach focusing on competitive positioning',
                'medium': 'Strategic partnership approach for comprehensive digital growth'
            },
            'estate': {
                'micro': 'Local market specialist approach emphasizing lead generation',
                'small': 'Regional expert approach focusing on market share growth',
                'medium': 'Strategic consultancy approach for market leadership'
            },
            'legal': {
                'micro': 'Professional services specialist approach highlighting credibility',
                'small': 'Legal marketing expert approach focusing on client acquisition',
                'medium': 'Strategic legal marketing partnership for firm growth'
            },
            'dental': {
                'micro': 'Healthcare marketing specialist focusing on patient acquisition',
                'small': 'Dental practice growth consultant approach',
                'medium': 'Strategic healthcare marketing partnership'
            }
        }
        
        return approaches.get(vertical, {}).get(company_size, 'Professional consultant approach')

    async def export_results(self, prospects: List[ArcoProspect]) -> str:
        """Export comprehensive results with integrated analysis"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/ultra_qualified/arco_integrated_discovery_{timestamp}.json"
        
        # Calculate summary statistics
        total_ad_opportunity = sum(p.monthly_waste_estimate * 6 for p in prospects)  # 6 months
        total_web_opportunity = sum(p.web_opportunity.estimated_value for p in prospects)
        total_digital_opportunity = sum(p.total_digital_opportunity for p in prospects)
        
        high_priority_count = len([p for p in prospects if p.priority_level in ['CRITICAL', 'HIGH']])
        
        # Vertical breakdown
        vertical_breakdown = {}
        for vertical in ['aesthetic', 'estate', 'legal', 'dental']:
            vertical_prospects = [p for p in prospects if p.vertical == vertical]
            if vertical_prospects:
                vertical_breakdown[vertical] = {
                    'count': len(vertical_prospects),
                    'avg_opportunity_score': round(sum(p.opportunity_score for p in vertical_prospects) / len(vertical_prospects), 1),
                    'total_value': sum(p.total_digital_opportunity for p in vertical_prospects)
                }
        
        export_data = {
            "execution_summary": {
                "timestamp": timestamp,
                "engine_version": "ARCO Discovery Engine v1.0",
                "methodology": "Integrated ad performance + web opportunity analysis",
                "total_prospects": len(prospects),
                "high_priority_prospects": high_priority_count,
                "execution_cost_estimate": "$0.008"  # BigQuery cost estimate
            },
            
            "opportunity_analysis": {
                "total_ad_optimization_value": total_ad_opportunity,
                "total_web_development_value": total_web_opportunity,
                "total_digital_opportunity_value": total_digital_opportunity,
                "average_opportunity_score": round(sum(p.opportunity_score for p in prospects) / len(prospects), 1) if prospects else 0,
                "roi_projection": f"{total_digital_opportunity / 250:.0f}x" if prospects else "N/A"  # Assuming £250 cost per prospect
            },
            
            "market_intelligence": {
                "target_markets": ['GB', 'IE', 'AU', 'NZ', 'CA'],
                "vertical_breakdown": vertical_breakdown,
                "avg_monthly_ad_spend": round(sum(p.estimated_monthly_ad_spend for p in prospects) / len(prospects)) if prospects else 0,
                "avg_company_size": {
                    'micro': len([p for p in prospects if p.company_size == 'micro']),
                    'small': len([p for p in prospects if p.company_size == 'small']),
                    'medium': len([p for p in prospects if p.company_size == 'medium'])
                }
            },
            
            "web_opportunity_insights": {
                "website_refresh_opportunities": len([p for p in prospects if p.web_opportunity.opportunity_type == 'website_refresh']),
                "landing_page_optimization_opportunities": len([p for p in prospects if p.web_opportunity.opportunity_type == 'landing_page_optimization']),
                "digital_strategy_opportunities": len([p for p in prospects if p.web_opportunity.opportunity_type == 'digital_strategy']),
                "high_confidence_web_opportunities": len([p for p in prospects if p.web_opportunity.confidence_level == 'high'])
            },
            
            "prospects": [asdict(prospect) for prospect in prospects]
        }
        
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f">> Results exported to: {filename}")
            logger.info(f">> Total digital opportunity: £{total_digital_opportunity:,}")
            logger.info(f">> High-priority prospects: {high_priority_count}/{len(prospects)}")
            
            return filename
            
        except Exception as e:
            logger.error(f">> Export failed: {e}")
            return ""

# Main execution function
async def execute_arco_discovery():
    """Execute complete ARCO discovery pipeline"""
    
    logger.info(">> ARCO DISCOVERY ENGINE - Starting integrated analysis")
    
    engine = ArcoDiscoveryEngine()
    
    try:
        # Execute discovery
        prospects = await engine.discover_prospects(max_prospects=12)
        
        if not prospects:
            logger.warning(">> No qualified prospects found")
            return None, None
        
        # Export results
        export_file = await engine.export_results(prospects)
        
        # Summary report
        logger.info("=" * 60)
        logger.info("ARCO DISCOVERY SUMMARY")
        logger.info("=" * 60)
        
        total_value = sum(p.total_digital_opportunity for p in prospects)
        high_priority = len([p for p in prospects if p.priority_level in ['CRITICAL', 'HIGH']])
        
        logger.info(f">> Qualified prospects discovered: {len(prospects)}")
        logger.info(f">> High-priority opportunities: {high_priority}")
        logger.info(f">> Total digital opportunity: £{total_value:,}")
        logger.info(f">> Average opportunity score: {sum(p.opportunity_score for p in prospects) / len(prospects):.1f}/100")
        logger.info(f">> Export file: {export_file}")
        
        # Top 3 prospects summary
        logger.info(">> TOP OPPORTUNITIES:")
        for i, prospect in enumerate(prospects[:3], 1):
            logger.info(f"{i}. {prospect.company_name} ({prospect.vertical})")
            logger.info(f"   >> Total opportunity: £{prospect.total_digital_opportunity:,}")
            logger.info(f"   >> Priority: {prospect.priority_level}")
            logger.info(f"   >> Web opportunity: {prospect.web_opportunity.opportunity_type}")
            logger.info(f"   >> Score: {prospect.opportunity_score:.1f}/100")
        
        logger.info("=" * 60)
        
        return prospects, export_file
        
    except Exception as e:
        logger.error(f">> ARCO discovery failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None

# Entry point
if __name__ == "__main__":
    asyncio.run(execute_arco_discovery())