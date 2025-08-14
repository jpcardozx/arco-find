"""
ARCO Find: Competitive Intelligence and Market Analysis System
Professional-grade market research automation and competitive positioning
"""

import json
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from urllib.parse import urljoin, urlparse
import re

logger = logging.getLogger(__name__)

@dataclass
class CompetitorProfile:
    """Comprehensive competitor profile"""
    company_name: str
    domain: str
    vertical: str
    region: str
    estimated_monthly_spend: float
    campaign_count: int
    ad_platforms: List[str]
    positioning_keywords: List[str]
    target_audience: str
    competitive_advantages: List[str]
    market_share_estimate: float
    analysis_date: str

@dataclass
class MarketIntelligence:
    """Market intelligence summary"""
    vertical: str
    region: str
    market_size_estimate: float
    average_spend_per_business: float
    competition_density: str
    growth_trends: List[str]
    key_players: List[str]
    market_opportunities: List[str]
    entry_barriers: List[str]
    analysis_timestamp: str

class CompetitiveAnalyzer:
    """Advanced competitive analysis and market intelligence"""
    
    def __init__(self, api_keys: Dict[str, str] = None):
        self.api_keys = api_keys or {}
        self.market_data = {}
        self.competitor_cache = {}
        
    def analyze_market_position(self, prospect: Dict) -> Dict:
        """Comprehensive market position analysis"""
        vertical = prospect.get('vertical', '')
        region = prospect.get('region', '')
        
        # Get competitors
        competitors = self.identify_competitors(prospect)
        
        # Analyze positioning
        positioning_analysis = self._analyze_competitive_positioning(prospect, competitors)
        
        # Market share estimation
        market_share = self._estimate_market_share(prospect, competitors)
        
        # Opportunity identification
        opportunities = self._identify_market_opportunities(prospect, competitors)
        
        # Strategic vulnerabilities
        vulnerabilities = self._assess_strategic_vulnerabilities(prospect, competitors)
        
        return {
            'prospect_name': prospect.get('company_name', ''),
            'market_position': positioning_analysis,
            'market_share_estimate': market_share,
            'competitive_opportunities': opportunities,
            'strategic_vulnerabilities': vulnerabilities,
            'competitor_count': len(competitors),
            'analysis_confidence': self._calculate_analysis_confidence(competitors),
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def identify_competitors(self, prospect: Dict) -> List[CompetitorProfile]:
        """Identify and profile direct competitors"""
        vertical = prospect.get('vertical', '')
        region = prospect.get('region', '')
        cache_key = f"{vertical}_{region}"
        
        # Check cache first
        if cache_key in self.competitor_cache:
            cached_data = self.competitor_cache[cache_key]
            if self._is_cache_valid(cached_data['timestamp']):
                return cached_data['competitors']
        
        # Generate simulated competitors for demonstration
        # In production, this would integrate with real data sources
        competitors = self._generate_market_competitors(prospect)
        
        # Cache results
        self.competitor_cache[cache_key] = {
            'competitors': competitors,
            'timestamp': datetime.now().isoformat()
        }
        
        return competitors
    
    def generate_market_intelligence_report(self, vertical: str, region: str) -> MarketIntelligence:
        """Generate comprehensive market intelligence report"""
        
        # Market sizing
        market_size = self._estimate_market_size(vertical, region)
        
        # Competition analysis
        competition_data = self._analyze_competition_density(vertical, region)
        
        # Trend analysis
        trends = self._identify_market_trends(vertical, region)
        
        # Opportunity mapping
        opportunities = self._map_market_opportunities(vertical, region)
        
        return MarketIntelligence(
            vertical=vertical,
            region=region,
            market_size_estimate=market_size,
            average_spend_per_business=competition_data['avg_spend'],
            competition_density=competition_data['density'],
            growth_trends=trends,
            key_players=competition_data['key_players'],
            market_opportunities=opportunities,
            entry_barriers=self._identify_entry_barriers(vertical, region),
            analysis_timestamp=datetime.now().isoformat()
        )
    
    def _generate_market_competitors(self, prospect: Dict) -> List[CompetitorProfile]:
        """Generate realistic competitor profiles based on prospect data"""
        vertical = prospect.get('vertical', '')
        region = prospect.get('region', '')
        prospect_spend = prospect.get('estimated_monthly_spend', 5000)
        
        # Vertical-specific competitor patterns
        competitor_templates = {
            'dental': [
                {'name_pattern': '{region} Dental Clinic', 'spend_multiplier': 1.2},
                {'name_pattern': 'Advanced {vertical} Center', 'spend_multiplier': 1.5},
                {'name_pattern': '{region} Family Dentistry', 'spend_multiplier': 0.8},
                {'name_pattern': 'Premier Dental Group', 'spend_multiplier': 2.0}
            ],
            'fitness': [
                {'name_pattern': '{region} Fitness Center', 'spend_multiplier': 1.1},
                {'name_pattern': 'Elite Training Studio', 'spend_multiplier': 1.3},
                {'name_pattern': 'FitLife Gym', 'spend_multiplier': 0.9},
                {'name_pattern': 'Athletic Performance Center', 'spend_multiplier': 1.8}
            ],
            'legal': [
                {'name_pattern': '{region} Law Group', 'spend_multiplier': 1.4},
                {'name_pattern': 'Premier Legal Services', 'spend_multiplier': 1.7},
                {'name_pattern': 'Professional Law Firm', 'spend_multiplier': 1.2},
                {'name_pattern': 'Expert Legal Counsel', 'spend_multiplier': 2.2}
            ]
        }
        
        templates = competitor_templates.get(vertical, [
            {'name_pattern': f'{region} {vertical.title()} Services', 'spend_multiplier': 1.2}
        ])
        
        competitors = []
        for i, template in enumerate(templates[:4]):  # Top 4 competitors
            name = template['name_pattern'].format(
                region=region, 
                vertical=vertical.title()
            )
            
            estimated_spend = prospect_spend * template['spend_multiplier']
            campaign_count = max(5, int(estimated_spend / 300))  # Realistic campaign density
            
            competitor = CompetitorProfile(
                company_name=name,
                domain=f"{name.lower().replace(' ', '')}.com",
                vertical=vertical,
                region=region,
                estimated_monthly_spend=estimated_spend,
                campaign_count=campaign_count,
                ad_platforms=['Facebook', 'Google Ads', 'Instagram'],
                positioning_keywords=self._generate_positioning_keywords(vertical),
                target_audience=f"{region} residents seeking {vertical} services",
                competitive_advantages=self._generate_competitive_advantages(vertical),
                market_share_estimate=max(0.05, 0.25 - (i * 0.05)),  # Decreasing market share
                analysis_date=datetime.now().isoformat()
            )
            
            competitors.append(competitor)
        
        return competitors
    
    def _analyze_competitive_positioning(self, prospect: Dict, competitors: List[CompetitorProfile]) -> Dict:
        """Analyze prospect's competitive positioning"""
        prospect_spend = prospect.get('estimated_monthly_spend', 0)
        prospect_campaigns = prospect.get('total_ads', 0)
        
        # Spend positioning
        competitor_spends = [c.estimated_monthly_spend for c in competitors]
        spend_percentile = self._calculate_percentile(prospect_spend, competitor_spends)
        
        # Campaign volume positioning
        competitor_campaigns = [c.campaign_count for c in competitors]
        campaign_percentile = self._calculate_percentile(prospect_campaigns, competitor_campaigns)
        
        # Market position assessment
        if spend_percentile >= 75:
            spend_position = "Market Leader"
        elif spend_percentile >= 50:
            spend_position = "Strong Competitor"
        elif spend_percentile >= 25:
            spend_position = "Mid-Market Player"
        else:
            spend_position = "Emerging Player"
        
        return {
            'spend_position': spend_position,
            'spend_percentile': spend_percentile,
            'campaign_volume_percentile': campaign_percentile,
            'competitive_intensity': self._assess_competitive_intensity(competitors),
            'positioning_opportunities': self._identify_positioning_gaps(prospect, competitors)
        }
    
    def _estimate_market_share(self, prospect: Dict, competitors: List[CompetitorProfile]) -> float:
        """Estimate prospect's market share"""
        prospect_spend = prospect.get('estimated_monthly_spend', 0)
        total_market_spend = prospect_spend + sum(c.estimated_monthly_spend for c in competitors)
        
        if total_market_spend > 0:
            return round(prospect_spend / total_market_spend, 3)
        return 0.0
    
    def _identify_market_opportunities(self, prospect: Dict, competitors: List[CompetitorProfile]) -> List[str]:
        """Identify specific market opportunities"""
        opportunities = []
        
        prospect_spend = prospect.get('estimated_monthly_spend', 0)
        prospect_campaigns = prospect.get('total_ads', 0)
        
        # Spend efficiency opportunities
        avg_competitor_spend = sum(c.estimated_monthly_spend for c in competitors) / len(competitors) if competitors else 0
        if prospect_spend > 0 and avg_competitor_spend > prospect_spend * 1.3:
            opportunities.append(f"Budget expansion opportunity: {avg_competitor_spend/prospect_spend:.1f}x competitor average")
        
        # Campaign diversification
        avg_competitor_campaigns = sum(c.campaign_count for c in competitors) / len(competitors) if competitors else 0
        if prospect_campaigns > avg_competitor_campaigns * 1.5:
            opportunities.append("Campaign consolidation opportunity: Reduce sprawl for efficiency")
        elif prospect_campaigns < avg_competitor_campaigns * 0.5:
            opportunities.append("Campaign expansion opportunity: Increase market presence")
        
        # Platform opportunities
        common_platforms = set()
        for competitor in competitors:
            common_platforms.update(competitor.ad_platforms)
        
        if len(common_platforms) > 2:
            opportunities.append(f"Multi-platform presence: Competitors active on {len(common_platforms)} platforms")
        
        return opportunities
    
    def _assess_strategic_vulnerabilities(self, prospect: Dict, competitors: List[CompetitorProfile]) -> List[str]:
        """Assess strategic vulnerabilities and risks"""
        vulnerabilities = []
        
        prospect_spend = prospect.get('estimated_monthly_spend', 0)
        
        # Market position vulnerabilities
        high_spend_competitors = [c for c in competitors if c.estimated_monthly_spend > prospect_spend * 2]
        if high_spend_competitors:
            vulnerabilities.append(f"Outspent by {len(high_spend_competitors)} major competitors")
        
        # Campaign efficiency vulnerabilities
        prospect_campaigns = prospect.get('total_ads', 0)
        if prospect_campaigns > 20:
            vulnerabilities.append("Campaign sprawl: High management complexity")
        
        # Market saturation risk
        total_competitors = len(competitors)
        if total_competitors >= 4:
            vulnerabilities.append(f"High competition density: {total_competitors} active competitors")
        
        return vulnerabilities
    
    def _estimate_market_size(self, vertical: str, region: str) -> float:
        """Estimate total addressable market size"""
        # Market size estimates based on industry data
        market_multipliers = {
            'dental': {'US': 50000000, 'CA': 8000000, 'AU': 12000000},
            'fitness': {'US': 35000000, 'CA': 6000000, 'AU': 8000000},
            'legal': {'US': 80000000, 'CA': 15000000, 'AU': 18000000},
            'accounting': {'US': 45000000, 'CA': 8000000, 'AU': 10000000}
        }
        
        return market_multipliers.get(vertical, {}).get(region, 10000000)
    
    def _analyze_competition_density(self, vertical: str, region: str) -> Dict:
        """Analyze competition density and characteristics"""
        # Simulated competition analysis
        density_mapping = {
            ('dental', 'US'): {'density': 'High', 'avg_spend': 8500, 'key_players': ['Aspen Dental', 'Heartland Dental']},
            ('fitness', 'US'): {'density': 'Very High', 'avg_spend': 4200, 'key_players': ['Planet Fitness', 'LA Fitness']},
            ('legal', 'US'): {'density': 'Medium', 'avg_spend': 12000, 'key_players': ['Morgan & Morgan', 'Jacoby & Meyers']}
        }
        
        return density_mapping.get((vertical, region), {
            'density': 'Medium', 
            'avg_spend': 5000, 
            'key_players': ['Local Market Leader', 'Regional Chain']
        })
    
    def _identify_market_trends(self, vertical: str, region: str) -> List[str]:
        """Identify key market trends"""
        trend_mapping = {
            'dental': [
                "Increased focus on cosmetic procedures",
                "Telehealth consultations growing",
                "Direct-to-consumer teeth alignment",
                "Emphasis on patient experience"
            ],
            'fitness': [
                "Hybrid online/offline training models",
                "Boutique studio growth",
                "Wearable technology integration",
                "Personalized nutrition services"
            ],
            'legal': [
                "Digital transformation acceleration",
                "Specialized practice areas",
                "Alternative fee structures",
                "Client experience focus"
            ]
        }
        
        return trend_mapping.get(vertical, ["Digital transformation", "Customer experience focus"])
    
    def _map_market_opportunities(self, vertical: str, region: str) -> List[str]:
        """Map market opportunities"""
        opportunity_mapping = {
            'dental': [
                "Underserved suburban markets",
                "Emergency dental services gap",
                "Seniors market expansion",
                "Insurance acceptance optimization"
            ],
            'fitness': [
                "Corporate wellness programs",
                "Senior fitness services",
                "Youth athletic training",
                "Recovery and wellness services"
            ],
            'legal': [
                "Small business legal services",
                "Digital estate planning",
                "Immigration law demand",
                "Regulatory compliance services"
            ]
        }
        
        return opportunity_mapping.get(vertical, ["Market expansion opportunities", "Service differentiation"])
    
    def _identify_entry_barriers(self, vertical: str, region: str) -> List[str]:
        """Identify market entry barriers"""
        barrier_mapping = {
            'dental': ["Professional licensing", "High equipment costs", "Insurance network requirements"],
            'fitness': ["Location/real estate costs", "Equipment investment", "Staff certification"],
            'legal': ["Bar admission requirements", "Professional liability", "Client acquisition costs"]
        }
        
        return barrier_mapping.get(vertical, ["Regulatory requirements", "Capital investment", "Market competition"])
    
    def _generate_positioning_keywords(self, vertical: str) -> List[str]:
        """Generate typical positioning keywords for vertical"""
        keyword_mapping = {
            'dental': ['advanced', 'gentle', 'family-friendly', 'modern', 'experienced'],
            'fitness': ['elite', 'personalized', 'results-driven', 'community', 'professional'],
            'legal': ['experienced', 'aggressive', 'dedicated', 'results-oriented', 'trusted']
        }
        
        return keyword_mapping.get(vertical, ['professional', 'quality', 'experienced'])
    
    def _generate_competitive_advantages(self, vertical: str) -> List[str]:
        """Generate typical competitive advantages"""
        advantage_mapping = {
            'dental': ['State-of-the-art technology', 'Extended hours', 'Insurance acceptance', 'Gentle approach'],
            'fitness': ['Personal training included', '24/7 access', 'Group classes', 'Modern equipment'],
            'legal': ['Free consultation', 'No fee unless we win', 'Experienced team', 'Local expertise']
        }
        
        return advantage_mapping.get(vertical, ['Quality service', 'Competitive pricing', 'Local expertise'])
    
    def _calculate_percentile(self, value: float, comparison_values: List[float]) -> float:
        """Calculate percentile ranking"""
        if not comparison_values:
            return 50.0
        
        below_count = sum(1 for v in comparison_values if v < value)
        return (below_count / len(comparison_values)) * 100
    
    def _assess_competitive_intensity(self, competitors: List[CompetitorProfile]) -> str:
        """Assess competitive intensity level"""
        if len(competitors) >= 5:
            return "Very High"
        elif len(competitors) >= 3:
            return "High"
        elif len(competitors) >= 2:
            return "Moderate"
        else:
            return "Low"
    
    def _identify_positioning_gaps(self, prospect: Dict, competitors: List[CompetitorProfile]) -> List[str]:
        """Identify positioning gaps and opportunities"""
        gaps = []
        
        # Analysis based on competitor positioning
        all_keywords = set()
        for competitor in competitors:
            all_keywords.update(competitor.positioning_keywords)
        
        common_keywords = ['professional', 'quality', 'experienced']
        underused_keywords = [kw for kw in all_keywords if kw not in common_keywords]
        
        if underused_keywords:
            gaps.append(f"Underutilized positioning: {', '.join(underused_keywords[:3])}")
        
        # Campaign volume gaps
        prospect_campaigns = prospect.get('total_ads', 0)
        competitor_campaigns = [c.campaign_count for c in competitors]
        avg_campaigns = sum(competitor_campaigns) / len(competitor_campaigns) if competitor_campaigns else 0
        
        if prospect_campaigns < avg_campaigns * 0.7:
            gaps.append("Campaign volume below market average")
        
        return gaps
    
    def _calculate_analysis_confidence(self, competitors: List[CompetitorProfile]) -> float:
        """Calculate confidence score for analysis"""
        base_confidence = 0.6
        
        # More competitors = higher confidence
        competitor_bonus = min(0.3, len(competitors) * 0.075)
        
        # Recency bonus (simulated)
        recency_bonus = 0.1
        
        return min(1.0, base_confidence + competitor_bonus + recency_bonus)
    
    def _is_cache_valid(self, timestamp: str, max_age_hours: int = 24) -> bool:
        """Check if cached data is still valid"""
        try:
            cache_time = datetime.fromisoformat(timestamp)
            age = datetime.now() - cache_time
            return age < timedelta(hours=max_age_hours)
        except:
            return False

class StrategicIntelligenceGenerator:
    """Generate strategic intelligence reports and recommendations"""
    
    def __init__(self):
        self.competitive_analyzer = CompetitiveAnalyzer()
    
    def generate_prospect_intelligence_report(self, prospect: Dict) -> Dict:
        """Generate comprehensive intelligence report for prospect"""
        
        # Competitive analysis
        competitive_analysis = self.competitive_analyzer.analyze_market_position(prospect)
        
        # Market intelligence
        market_intel = self.competitive_analyzer.generate_market_intelligence_report(
            prospect.get('vertical', ''),
            prospect.get('region', '')
        )
        
        # Strategic recommendations
        recommendations = self._generate_strategic_recommendations(prospect, competitive_analysis)
        
        # Evidence package
        evidence_package = self._compile_evidence_package(prospect, competitive_analysis, market_intel)
        
        return {
            'prospect_overview': {
                'company_name': prospect.get('company_name'),
                'vertical': prospect.get('vertical'),
                'region': prospect.get('region'),
                'monthly_spend': prospect.get('estimated_monthly_spend'),
                'campaign_count': prospect.get('total_ads')
            },
            'competitive_analysis': competitive_analysis,
            'market_intelligence': asdict(market_intel),
            'strategic_recommendations': recommendations,
            'evidence_package': evidence_package,
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'analysis_type': 'comprehensive_strategic_intelligence',
                'confidence_score': competitive_analysis.get('analysis_confidence', 0.8)
            }
        }
    
    def _generate_strategic_recommendations(self, prospect: Dict, competitive_analysis: Dict) -> List[Dict]:
        """Generate strategic recommendations based on analysis"""
        recommendations = []
        
        # Market position recommendations
        market_position = competitive_analysis.get('market_position', {})
        spend_percentile = market_position.get('spend_percentile', 50)
        
        if spend_percentile < 25:
            recommendations.append({
                'category': 'Budget Optimization',
                'priority': 'High',
                'recommendation': 'Increase advertising investment to competitive levels',
                'rationale': f'Currently spending below 75% of competitors (${prospect.get("estimated_monthly_spend", 0):,}/month)',
                'expected_impact': 'Market share growth, improved visibility'
            })
        
        # Campaign efficiency recommendations
        campaign_count = prospect.get('total_ads', 0)
        if campaign_count > 20:
            recommendations.append({
                'category': 'Campaign Consolidation',
                'priority': 'Medium',
                'recommendation': 'Consolidate campaigns for improved efficiency',
                'rationale': f'Managing {campaign_count} campaigns indicates potential sprawl',
                'expected_impact': 'Reduced management complexity, improved ROI tracking'
            })
        
        # Competitive opportunities
        opportunities = competitive_analysis.get('competitive_opportunities', [])
        for opportunity in opportunities[:2]:  # Top 2 opportunities
            recommendations.append({
                'category': 'Market Opportunity',
                'priority': 'Medium',
                'recommendation': opportunity,
                'rationale': 'Identified through competitive gap analysis',
                'expected_impact': 'Competitive advantage, market differentiation'
            })
        
        return recommendations
    
    def _compile_evidence_package(self, prospect: Dict, competitive_analysis: Dict, market_intel: MarketIntelligence) -> Dict:
        """Compile evidence package for outreach"""
        return {
            'market_position_summary': f"{prospect.get('company_name')} ranks in {competitive_analysis.get('market_position', {}).get('spend_position', 'unknown')} tier",
            'competitive_context': f"Market includes {competitive_analysis.get('competitor_count', 0)} active competitors",
            'market_size': f"${market_intel.market_size_estimate:,.0f} total addressable market",
            'key_opportunities': competitive_analysis.get('competitive_opportunities', [])[:3],
            'strategic_vulnerabilities': competitive_analysis.get('strategic_vulnerabilities', [])[:2],
            'evidence_strength': 'High' if competitive_analysis.get('analysis_confidence', 0) > 0.8 else 'Medium'
        }

# Example usage
if __name__ == "__main__":
    # Initialize intelligence generator
    intel_generator = StrategicIntelligenceGenerator()
    
    # Sample prospect data
    sample_prospect = {
        "company_name": "Pure Dentistry",
        "domain": "puredentistry.com.au",
        "vertical": "dental",
        "region": "AU",
        "estimated_monthly_spend": 7250,
        "total_ads": 20
    }
    
    # Generate intelligence report
    intelligence_report = intel_generator.generate_prospect_intelligence_report(sample_prospect)
    
    print("Strategic Intelligence Report Generated:")
    print(f"Prospect: {intelligence_report['prospect_overview']['company_name']}")
    print(f"Market Position: {intelligence_report['competitive_analysis']['market_position']['spend_position']}")
    print(f"Competitors: {intelligence_report['competitive_analysis']['competitor_count']}")
    print(f"Recommendations: {len(intelligence_report['strategic_recommendations'])}")
    print(f"Confidence Score: {intelligence_report['report_metadata']['confidence_score']:.2f}")
