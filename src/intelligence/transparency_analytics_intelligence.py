"""
🎯 GOOGLE ADS TRANSPARENCY CENTER + ANALYTICS CROSS-REFERENCE INTELLIGENCE
Strategic lead discovery usando dados públicos de transparência cruzados com analytics
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class AdTransparencyLead:
    """Lead descoberto via Google Ads Transparency Center + Analytics cross-reference"""
    company_name: str
    domain: str
    advertiser_id: str
    current_ad_spend_signals: Dict
    transparency_data: Dict
    analytics_signals: Dict
    qualification_score: float
    urgency_indicators: List[str]

class GoogleAdsTransparencyIntelligence:
    """
    Cruzamento de dados do Google Ads Transparency Center com Analytics
    para identificar leads altamente qualificados
    """
    
    def __init__(self):
        self.transparency_base_url = "https://adstransparency.google.com/advertiser"
        self.analytics_patterns = self._load_analytics_patterns()
        self.high_value_indicators = self._load_high_value_indicators()
    
    def _load_analytics_patterns(self) -> Dict:
        """Padrões de analytics que indicam problemas de conversão"""
        return {
            'bounce_rate_patterns': {
                'critical': '>70%',
                'high': '60-70%',
                'medium': '50-60%'
            },
            'session_duration_patterns': {
                'critical': '<30s',
                'high': '30-60s',
                'medium': '60-120s'
            },
            'conversion_funnel_issues': {
                'cart_abandonment': '>80%',
                'form_abandonment': '>60%',
                'checkout_abandonment': '>70%'
            },
            'traffic_quality_signals': {
                'paid_vs_organic_imbalance': '>80% paid',
                'geographic_mismatch': 'targeting vs conversion geography',
                'device_performance_gap': 'mobile vs desktop conversion delta >50%'
            }
        }
    
    def _load_high_value_indicators(self) -> Dict:
        """Indicadores de alto valor baseados em transparência publicitária"""
        return {
            'spend_volume_signals': {
                'enterprise': '>$50k/month ad spend',
                'smb_high': '$10k-50k/month',
                'smb_medium': '$2k-10k/month'
            },
            'campaign_sophistication': {
                'advanced': 'multiple campaign types, lookalike audiences',
                'intermediate': 'search + display campaigns',
                'basic': 'single campaign type'
            },
            'market_presence_indicators': {
                'competitive_keywords': 'bidding on competitor terms',
                'brand_protection': 'defensive brand campaigns',
                'expansion_signals': 'new market/geo testing'
            }
        }

    async def discover_transparency_leads(self, industry_filters: List[str], 
                                        location_filters: List[str]) -> List[AdTransparencyLead]:
        """
        Descobrir leads usando Google Ads Transparency Center data
        """
        leads = []
        
        for industry in industry_filters:
            for location in location_filters:
                # Query transparency center data
                transparency_companies = await self._query_transparency_center(industry, location)
                
                for company_data in transparency_companies:
                    # Cross-reference with analytics patterns
                    analytics_intelligence = await self._analyze_analytics_patterns(company_data)
                    
                    # Qualify lead based on transparency + analytics signals
                    qualified_lead = await self._qualify_transparency_lead(
                        company_data, analytics_intelligence
                    )
                    
                    if qualified_lead and qualified_lead.qualification_score > 0.7:
                        leads.append(qualified_lead)
        
        return sorted(leads, key=lambda x: x.qualification_score, reverse=True)

    async def _query_transparency_center(self, industry: str, location: str) -> List[Dict]:
        """
        Query Google Ads Transparency Center para encontrar anunciantes ativos
        """
        # Simulated transparency center query (in reality, we'd scrape or use API)
        transparency_queries = [
            f"{industry} services {location}",
            f"{industry} companies {location}",
            f"best {industry} {location}",
            f"{industry} near me {location}"
        ]
        
        discovered_advertisers = []
        
        for query in transparency_queries:
            # This would be actual transparency center scraping
            advertisers = await self._scrape_transparency_center(query)
            discovered_advertisers.extend(advertisers)
        
        return self._deduplicate_advertisers(discovered_advertisers)
    
    async def _scrape_transparency_center(self, query: str) -> List[Dict]:
        """
        Scrape transparency center data for active advertisers
        """
        # Real implementation would scrape:
        # - Advertiser names
        # - Ad spend indicators
        # - Campaign types
        # - Geographic targeting
        # - Audience targeting data
        
        # Simulated high-value data based on real patterns
        return [
            {
                'advertiser_name': 'Elite Legal Services Dallas',
                'domain': 'elitelegalservices.com',
                'advertiser_id': 'AR1234567890',
                'spend_indicators': {
                    'volume_tier': 'high',  # Based on ad frequency/placement
                    'geographic_scope': ['Dallas', 'Fort Worth', 'Arlington'],
                    'campaign_types': ['Search', 'Display', 'Video'],
                    'keyword_categories': ['personal injury lawyer', 'car accident attorney', 'legal services']
                },
                'targeting_intelligence': {
                    'demographics': 'Age 25-65, All genders',
                    'interests': ['Legal services', 'Insurance claims', 'Medical care'],
                    'behaviors': ['Recently searched for lawyers', 'Visited legal websites']
                }
            },
            {
                'advertiser_name': 'Premier Auto Collision Repair',
                'domain': 'premierautocollision.com',
                'advertiser_id': 'AR9876543210',
                'spend_indicators': {
                    'volume_tier': 'medium',
                    'geographic_scope': ['Phoenix', 'Scottsdale', 'Tempe'],
                    'campaign_types': ['Search', 'Local'],
                    'keyword_categories': ['auto repair', 'collision repair', 'car body shop']
                },
                'targeting_intelligence': {
                    'demographics': 'Age 25-55, All genders',
                    'interests': ['Automotive', 'Insurance', 'Vehicle maintenance'],
                    'behaviors': ['Recently searched for auto repair', 'Visited automotive websites']
                }
            }
        ]
    
    async def _analyze_analytics_patterns(self, company_data: Dict) -> Dict:
        """
        Analisar padrões de analytics para identificar problemas de conversão
        """
        domain = company_data.get('domain')
        
        # Esta seria integração real com:
        # - SimilarWeb API
        # - Ahrefs API  
        # - SEMrush API
        # - Google Analytics Intelligence (onde possível)
        
        # Simulação baseada em padrões reais observados
        analytics_intelligence = {
            'traffic_analysis': await self._analyze_traffic_patterns(domain),
            'conversion_signals': await self._detect_conversion_issues(domain),
            'competitive_analysis': await self._analyze_competitive_position(domain),
            'technical_performance': await self._analyze_technical_metrics(domain)
        }
        
        return analytics_intelligence
    
    async def _analyze_traffic_patterns(self, domain: str) -> Dict:
        """Analisar padrões de tráfego que indicam problemas"""
        # Real implementation would use APIs like SimilarWeb
        
        # Simulação baseada em padrões de legal/automotive
        if 'legal' in domain.lower() or 'law' in domain.lower():
            return {
                'monthly_visitors': 15000,
                'traffic_sources': {
                    'paid_search': 0.65,  # 65% paid - RED FLAG para legal
                    'organic_search': 0.20,
                    'direct': 0.10,
                    'referral': 0.05
                },
                'bounce_rate_estimate': 0.72,  # 72% - CRITICAL
                'avg_session_duration': 45,  # 45 seconds - LOW
                'pages_per_session': 1.8,   # LOW engagement
                'conversion_rate_estimate': 0.02,  # 2% - POOR for legal
                'problem_indicators': [
                    'HIGH_PAID_DEPENDENCY',
                    'POOR_ENGAGEMENT_METRICS', 
                    'LOW_CONVERSION_RATE'
                ]
            }
        else:
            return {
                'monthly_visitors': 8500,
                'traffic_sources': {
                    'paid_search': 0.45,
                    'organic_search': 0.35,
                    'direct': 0.15,
                    'referral': 0.05
                },
                'bounce_rate_estimate': 0.68,
                'avg_session_duration': 90,
                'pages_per_session': 2.1,
                'conversion_rate_estimate': 0.035,
                'problem_indicators': [
                    'MODERATE_PAID_DEPENDENCY',
                    'CONVERSION_OPTIMIZATION_NEEDED'
                ]
            }
    
    async def _detect_conversion_issues(self, domain: str) -> Dict:
        """Detectar problemas específicos de conversão"""
        
        return {
            'funnel_analysis': {
                'landing_page_performance': {
                    'bounce_rate': 0.72,
                    'time_to_interact': 4.2,  # seconds
                    'cta_visibility_score': 0.3,  # LOW
                    'form_completion_rate': 0.15  # 15% - POOR
                },
                'conversion_bottlenecks': [
                    {
                        'stage': 'Landing Page',
                        'drop_off_rate': 0.72,
                        'primary_issue': 'Slow load time + unclear value prop'
                    },
                    {
                        'stage': 'Contact Form',
                        'drop_off_rate': 0.85,
                        'primary_issue': 'Too many required fields'
                    },
                    {
                        'stage': 'Thank You Page',
                        'drop_off_rate': 0.20,
                        'primary_issue': 'No next steps provided'
                    }
                ]
            },
            'attribution_problems': {
                'tracking_accuracy': 0.45,  # 45% accuracy - POOR
                'cross_device_tracking': False,
                'offline_conversion_tracking': False,
                'issues_detected': [
                    'GCLID_PARAMETER_LOSS',
                    'CROSS_DOMAIN_TRACKING_MISSING',
                    'PHONE_CALL_ATTRIBUTION_MISSING'
                ]
            }
        }
    
    async def _analyze_competitive_position(self, domain: str) -> Dict:
        """Analisar posição competitiva via dados públicos"""
        
        return {
            'keyword_competition': {
                'branded_keyword_defense': 0.3,  # 30% - WEAK
                'competitor_keyword_overlap': 0.8,  # 80% - HIGH competition
                'market_share_estimate': 0.12,  # 12% local market share
                'cost_efficiency_vs_competitors': 0.6  # 60% - ROOM FOR IMPROVEMENT
            },
            'ad_creative_analysis': {
                'message_uniqueness_score': 0.25,  # 25% - GENERIC messaging
                'cta_effectiveness_estimate': 0.4,  # 40% - WEAK CTAs
                'visual_differentiation': 0.3,  # 30% - GENERIC visuals
                'competitive_advantage_clarity': 0.2  # 20% - UNCLEAR positioning
            },
            'market_opportunity_signals': [
                'WEAK_BRANDED_DEFENSE',
                'GENERIC_MESSAGING',
                'POOR_CONVERSION_TRACKING',
                'HIGH_COST_INEFFICIENCY'
            ]
        }
    
    async def _analyze_technical_metrics(self, domain: str) -> Dict:
        """Analisar métricas técnicas via PageSpeed + outras fontes"""
        
        # Simulação baseada em padrões reais de SMB websites
        return {
            'core_web_vitals': {
                'largest_contentful_paint': 4.8,  # seconds - POOR
                'first_input_delay': 180,  # ms - POOR  
                'cumulative_layout_shift': 0.35,  # score - POOR
                'overall_score': 23  # /100 - CRITICAL
            },
            'mobile_performance': {
                'mobile_speed_score': 18,  # /100 - CRITICAL
                'mobile_usability_score': 45,  # /100 - POOR
                'mobile_conversion_rate': 0.008,  # 0.8% - TERRIBLE
                'mobile_vs_desktop_gap': 0.6  # 60% performance gap
            },
            'seo_technical_health': {
                'crawlability_score': 0.7,  # 70% - GOOD
                'indexability_issues': 12,  # count - MODERATE
                'schema_markup_completeness': 0.2,  # 20% - POOR
                'local_seo_optimization': 0.4  # 40% - POOR
            }
        }
    
    async def _qualify_transparency_lead(self, company_data: Dict, 
                                       analytics_intelligence: Dict) -> Optional[AdTransparencyLead]:
        """
        Qualificar lead baseado em transparency + analytics cross-reference
        """
        
        # Scoring algorithm baseado em fatores reais de conversão
        qualification_factors = {
            'ad_spend_volume': self._score_ad_spend(company_data['spend_indicators']),
            'conversion_problems': self._score_conversion_issues(analytics_intelligence['conversion_signals']),
            'technical_debt': self._score_technical_issues(analytics_intelligence['technical_performance']),
            'competitive_vulnerability': self._score_competitive_weakness(analytics_intelligence['competitive_analysis']),
            'market_opportunity': self._score_market_opportunity(analytics_intelligence)
        }
        
        # Weighted qualification score
        qualification_score = (
            qualification_factors['ad_spend_volume'] * 0.25 +
            qualification_factors['conversion_problems'] * 0.30 +
            qualification_factors['technical_debt'] * 0.25 +
            qualification_factors['competitive_vulnerability'] * 0.15 +
            qualification_factors['market_opportunity'] * 0.05
        )
        
        # Urgency indicators baseados em dados reais
        urgency_indicators = self._calculate_urgency_indicators(
            company_data, analytics_intelligence
        )
        
        return AdTransparencyLead(
            company_name=company_data['advertiser_name'],
            domain=company_data['domain'],
            advertiser_id=company_data['advertiser_id'],
            current_ad_spend_signals=company_data['spend_indicators'],
            transparency_data=company_data,
            analytics_signals=analytics_intelligence,
            qualification_score=qualification_score,
            urgency_indicators=urgency_indicators
        )
    
    def _score_ad_spend(self, spend_indicators: Dict) -> float:
        """Score baseado em volume de ad spend (mais gasto = mais qualificado)"""
        volume_tier = spend_indicators.get('volume_tier', 'low')
        
        scoring = {
            'high': 1.0,    # >$50k/month
            'medium': 0.8,  # $10k-50k/month  
            'low': 0.5      # <$10k/month
        }
        
        return scoring.get(volume_tier, 0.3)
    
    def _score_conversion_issues(self, conversion_signals: Dict) -> float:
        """Score problemas de conversão (mais problemas = mais qualificado)"""
        issues_count = len(conversion_signals.get('attribution_problems', {}).get('issues_detected', []))
        funnel_problems = len(conversion_signals.get('funnel_analysis', {}).get('conversion_bottlenecks', []))
        
        # Mais problemas = mais oportunidade = score mais alto
        total_issues = issues_count + funnel_problems
        
        if total_issues >= 5:
            return 1.0  # Critical issues = highest opportunity
        elif total_issues >= 3:
            return 0.8  # Moderate issues
        elif total_issues >= 1:
            return 0.6  # Some issues
        else:
            return 0.2  # Few issues = less opportunity
    
    def _score_technical_issues(self, technical_performance: Dict) -> float:
        """Score problemas técnicos (Core Web Vitals, mobile, etc.)"""
        cwv = technical_performance.get('core_web_vitals', {})
        mobile = technical_performance.get('mobile_performance', {})
        
        # Poor performance = high opportunity score
        performance_score = cwv.get('overall_score', 50)
        mobile_score = mobile.get('mobile_speed_score', 50)
        
        avg_performance = (performance_score + mobile_score) / 2
        
        if avg_performance < 30:
            return 1.0  # Critical performance issues
        elif avg_performance < 50:
            return 0.8  # Poor performance
        elif avg_performance < 70:
            return 0.6  # Moderate performance
        else:
            return 0.3  # Good performance = less opportunity
    
    def _score_competitive_weakness(self, competitive_analysis: Dict) -> float:
        """Score vulnerabilidades competitivas"""
        keyword_comp = competitive_analysis.get('keyword_competition', {})
        ad_creative = competitive_analysis.get('ad_creative_analysis', {})
        
        # Weak competitive position = high opportunity
        branded_defense = keyword_comp.get('branded_keyword_defense', 0.5)
        message_uniqueness = ad_creative.get('message_uniqueness_score', 0.5)
        
        weakness_score = 1 - ((branded_defense + message_uniqueness) / 2)
        return weakness_score
    
    def _score_market_opportunity(self, analytics_intelligence: Dict) -> float:
        """Score oportunidade de mercado baseada em traffic patterns"""
        traffic = analytics_intelligence.get('traffic_analysis', {})
        
        # High paid dependency + poor conversion = high opportunity
        paid_dependency = traffic.get('traffic_sources', {}).get('paid_search', 0.3)
        conversion_rate = traffic.get('conversion_rate_estimate', 0.03)
        
        if paid_dependency > 0.6 and conversion_rate < 0.03:
            return 1.0  # High opportunity
        elif paid_dependency > 0.4 and conversion_rate < 0.05:
            return 0.7  # Moderate opportunity
        else:
            return 0.4  # Lower opportunity
    
    def _calculate_urgency_indicators(self, company_data: Dict, 
                                    analytics_intelligence: Dict) -> List[str]:
        """Calcular indicadores de urgência baseados em dados reais"""
        
        urgency_indicators = []
        
        # Technical urgency
        technical = analytics_intelligence.get('technical_performance', {})
        cwv_score = technical.get('core_web_vitals', {}).get('overall_score', 50)
        
        if cwv_score < 25:
            urgency_indicators.append('CRITICAL_CORE_WEB_VITALS')
        
        # Conversion urgency  
        conversion = analytics_intelligence.get('conversion_signals', {})
        tracking_accuracy = conversion.get('attribution_problems', {}).get('tracking_accuracy', 0.5)
        
        if tracking_accuracy < 0.5:
            urgency_indicators.append('ATTRIBUTION_CRISIS')
        
        # Competitive urgency
        competitive = analytics_intelligence.get('competitive_analysis', {})
        branded_defense = competitive.get('keyword_competition', {}).get('branded_keyword_defense', 0.5)
        
        if branded_defense < 0.4:
            urgency_indicators.append('BRAND_VULNERABILITY')
        
        # Financial urgency (high spend + poor performance)
        spend_tier = company_data.get('spend_indicators', {}).get('volume_tier', 'low')
        conversion_rate = analytics_intelligence.get('traffic_analysis', {}).get('conversion_rate_estimate', 0.03)
        
        if spend_tier in ['medium', 'high'] and conversion_rate < 0.02:
            urgency_indicators.append('AD_SPEND_WASTE')
        
        return urgency_indicators

    async def generate_transparency_lead_report(self, leads: List[AdTransparencyLead]) -> Dict:
        """
        Gerar relatório de leads descobertos via Transparency Center + Analytics
        """
        
        if not leads:
            return {'error': 'No qualified leads found'}
        
        # Aggregate insights
        total_ad_spend_opportunity = sum(
            self._estimate_monthly_ad_spend(lead.current_ad_spend_signals) 
            for lead in leads
        )
        
        total_waste_opportunity = sum(
            self._calculate_monthly_waste(lead.analytics_signals)
            for lead in leads
        )
        
        return {
            'discovery_summary': {
                'total_qualified_leads': len(leads),
                'avg_qualification_score': sum(l.qualification_score for l in leads) / len(leads),
                'total_monthly_ad_spend_in_scope': total_ad_spend_opportunity,
                'total_monthly_waste_opportunity': total_waste_opportunity,
                'discovery_timestamp': datetime.utcnow().isoformat()
            },
            'urgency_distribution': self._analyze_urgency_distribution(leads),
            'industry_breakdown': self._analyze_industry_breakdown(leads),
            'top_opportunities': [
                {
                    'company_name': lead.company_name,
                    'domain': lead.domain,
                    'qualification_score': lead.qualification_score,
                    'estimated_monthly_waste': self._calculate_monthly_waste(lead.analytics_signals),
                    'urgency_indicators': lead.urgency_indicators,
                    'primary_issues': self._extract_primary_issues(lead.analytics_signals)
                }
                for lead in leads[:10]  # Top 10
            ],
            'actionable_insights': self._generate_actionable_insights(leads)
        }
    
    def _estimate_monthly_ad_spend(self, spend_indicators: Dict) -> float:
        """Estimar gasto mensal baseado em indicators do transparency center"""
        volume_tier = spend_indicators.get('volume_tier', 'low')
        
        estimates = {
            'high': 75000,    # $75k/month average
            'medium': 25000,  # $25k/month average
            'low': 5000       # $5k/month average
        }
        
        return estimates.get(volume_tier, 2500)
    
    def _calculate_monthly_waste(self, analytics_signals: Dict) -> float:
        """Calcular desperdício mensal baseado em analytics"""
        traffic = analytics_signals.get('traffic_analysis', {})
        conversion = analytics_signals.get('conversion_signals', {})
        
        # Estimate based on traffic + conversion issues
        monthly_visitors = traffic.get('monthly_visitors', 5000)
        conversion_rate = traffic.get('conversion_rate_estimate', 0.03)
        paid_percentage = traffic.get('traffic_sources', {}).get('paid_search', 0.4)
        
        # Potential improvement from optimization
        potential_conversion_improvement = 0.5  # 50% improvement possible
        
        monthly_paid_visitors = monthly_visitors * paid_percentage
        current_conversions = monthly_paid_visitors * conversion_rate
        potential_conversions = monthly_paid_visitors * (conversion_rate * (1 + potential_conversion_improvement))
        
        # Estimate waste (assuming $200 average cost per conversion)
        avg_cost_per_conversion = 200
        monthly_waste = (potential_conversions - current_conversions) * avg_cost_per_conversion
        
        return max(monthly_waste, 500)  # Minimum $500 waste estimate
    
    def _analyze_urgency_distribution(self, leads: List[AdTransparencyLead]) -> Dict:
        """Analisar distribuição de urgência"""
        urgency_counts = {}
        
        for lead in leads:
            for indicator in lead.urgency_indicators:
                urgency_counts[indicator] = urgency_counts.get(indicator, 0) + 1
        
        return urgency_counts
    
    def _analyze_industry_breakdown(self, leads: List[AdTransparencyLead]) -> Dict:
        """Analisar breakdown por indústria"""
        industry_data = {}
        
        for lead in leads:
            # Extract industry from domain/company name
            industry = self._extract_industry(lead.company_name, lead.domain)
            
            if industry not in industry_data:
                industry_data[industry] = {
                    'count': 0,
                    'total_qualification_score': 0,
                    'total_waste_opportunity': 0
                }
            
            industry_data[industry]['count'] += 1
            industry_data[industry]['total_qualification_score'] += lead.qualification_score
            industry_data[industry]['total_waste_opportunity'] += self._calculate_monthly_waste(lead.analytics_signals)
        
        # Calculate averages
        for industry in industry_data:
            count = industry_data[industry]['count']
            industry_data[industry]['avg_qualification_score'] = industry_data[industry]['total_qualification_score'] / count
        
        return industry_data
    
    def _extract_industry(self, company_name: str, domain: str) -> str:
        """Extract industry from company name/domain"""
        text = f"{company_name} {domain}".lower()
        
        if any(term in text for term in ['legal', 'law', 'attorney', 'lawyer']):
            return 'legal'
        elif any(term in text for term in ['auto', 'car', 'vehicle', 'repair', 'collision']):
            return 'automotive'
        elif any(term in text for term in ['medical', 'health', 'doctor', 'clinic']):
            return 'healthcare'
        elif any(term in text for term in ['real estate', 'realtor', 'property']):
            return 'real_estate'
        elif any(term in text for term in ['restaurant', 'food', 'dining']):
            return 'restaurant'
        else:
            return 'other'
    
    def _extract_primary_issues(self, analytics_signals: Dict) -> List[str]:
        """Extract primary issues from analytics signals"""
        issues = []
        
        # Technical issues
        technical = analytics_signals.get('technical_performance', {})
        cwv_score = technical.get('core_web_vitals', {}).get('overall_score', 50)
        
        if cwv_score < 30:
            issues.append('Critical Core Web Vitals')
        
        # Conversion issues
        conversion = analytics_signals.get('conversion_signals', {})
        tracking_accuracy = conversion.get('attribution_problems', {}).get('tracking_accuracy', 0.5)
        
        if tracking_accuracy < 0.5:
            issues.append('Poor Conversion Tracking')
        
        # Traffic quality issues
        traffic = analytics_signals.get('traffic_analysis', {})
        bounce_rate = traffic.get('bounce_rate_estimate', 0.5)
        
        if bounce_rate > 0.7:
            issues.append('High Bounce Rate')
        
        return issues
    
    def _generate_actionable_insights(self, leads: List[AdTransparencyLead]) -> List[str]:
        """Generate actionable insights from discovered leads"""
        insights = []
        
        # High-level patterns
        high_score_leads = [l for l in leads if l.qualification_score > 0.8]
        if high_score_leads:
            insights.append(f"{len(high_score_leads)} leads with qualification score >80% - prioritize for immediate outreach")
        
        # Urgency patterns
        critical_leads = [l for l in leads if 'CRITICAL_CORE_WEB_VITALS' in l.urgency_indicators]
        if critical_leads:
            insights.append(f"{len(critical_leads)} leads with critical performance issues - use technical audit approach")
        
        # Industry patterns
        industry_breakdown = self._analyze_industry_breakdown(leads)
        top_industry = max(industry_breakdown.items(), key=lambda x: x[1]['total_waste_opportunity'])
        insights.append(f"Highest opportunity in {top_industry[0]} industry: ${top_industry[1]['total_waste_opportunity']:,.0f} monthly waste")
        
        return insights

# Usage example
async def main():
    transparency_intelligence = GoogleAdsTransparencyIntelligence()
    
    # Target industries and locations based on S-tier analysis
    industry_filters = ['legal services', 'automotive repair', 'healthcare', 'real estate']
    location_filters = ['Dallas', 'Phoenix', 'Austin', 'San Antonio']
    
    # Discover leads using transparency + analytics cross-reference
    qualified_leads = await transparency_intelligence.discover_transparency_leads(
        industry_filters, location_filters
    )
    
    # Generate comprehensive report
    report = await transparency_intelligence.generate_transparency_lead_report(qualified_leads)
    
    print(f"🎯 Discovered {len(qualified_leads)} qualified leads via Transparency Center + Analytics")
    print(f"💰 Total monthly waste opportunity: ${report['discovery_summary']['total_monthly_waste_opportunity']:,.0f}")
    
    return report

if __name__ == "__main__":
    asyncio.run(main())
