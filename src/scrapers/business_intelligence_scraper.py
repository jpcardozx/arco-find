#!/usr/bin/env python3
"""
🔍 BUSINESS INTELLIGENCE SCRAPER
Ethical scraping for strategic business intelligence
Focuses on public data sources and respects robots.txt
"""

import requests
import time
import re
import json
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BusinessIntelligence:
    """Structured business intelligence data"""
    company_name: str
    employee_count_estimate: Optional[int]
    revenue_estimate: Optional[str]
    funding_info: Optional[Dict]
    social_media_presence: Dict
    online_reputation: Dict
    competitive_positioning: Dict
    market_signals: List[str]

@dataclass
class CompetitorProfile:
    """Competitor analysis profile"""
    name: str
    website: str
    estimated_size: str
    technology_stack: List[str]
    marketing_positioning: str
    pricing_signals: Optional[str]
    strengths: List[str]
    weaknesses: List[str]

class EthicalWebScraper:
    """Base class for ethical web scraping with respect for robots.txt"""
    
    def __init__(self, delay_range: Tuple[int, int] = (2, 5)):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ARCO Business Intelligence Bot 1.0 (Business Research)'
        })
        self.delay_range = delay_range
        self.robots_cache = {}
    
    def can_fetch(self, url: str) -> bool:
        """Check if we can ethically fetch this URL"""
        try:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            if base_url not in self.robots_cache:
                robots_url = urljoin(base_url, '/robots.txt')
                rp = RobotFileParser()
                rp.set_url(robots_url)
                try:
                    rp.read()
                    self.robots_cache[base_url] = rp
                except:
                    # If robots.txt fails, be conservative
                    self.robots_cache[base_url] = None
                    return True
            
            robots = self.robots_cache[base_url]
            if robots:
                return robots.can_fetch(self.session.headers['User-Agent'], url)
            return True
            
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {url}: {e}")
            return True
    
    def fetch_with_respect(self, url: str) -> Optional[str]:
        """Fetch URL with ethical considerations"""
        if not self.can_fetch(url):
            logger.info(f"Respecting robots.txt: skipping {url}")
            return None
        
        try:
            # Random delay to be respectful
            delay = random.uniform(*self.delay_range)
            time.sleep(delay)
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
            
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

class PublicBusinessDataEnricher(EthicalWebScraper):
    """Enrich business data from public sources"""
    
    def __init__(self):
        super().__init__()
        
        # Public data patterns for employee count estimation
        self.employee_indicators = {
            'micro': [
                r'founded?\s*by\s*[a-z\s]+',
                r'owner[:\s]*[a-z\s]+',
                r'contact\s*me',
                r'my\s*(name|business)'
            ],
            'small': [
                r'our\s*team\s*of\s*\d{1,2}',
                r'team\s*of\s*\d{1,2}\s*professionals',
                r'staff\s*of\s*\d{1,2}',
                r'founded\s*in\s*\d{4}'
            ],
            'medium': [
                r'over\s*\d{2}\s*employees',
                r'team\s*of\s*\d{2,3}\s*professionals',
                r'multiple\s*locations',
                r'departments?'
            ],
            'large': [
                r'over\s*\d{3}\s*employees',
                r'headquarters',
                r'regional\s*offices',
                r'enterprise\s*solutions'
            ]
        }
        
        # Revenue indicators from website content
        self.revenue_indicators = {
            '<$100K': [
                r'home\s*based',
                r'freelance',
                r'startup',
                r'new\s*business'
            ],
            '$100K-$500K': [
                r'small\s*business',
                r'local\s*service',
                r'family\s*owned',
                r'since\s*\d{4}'
            ],
            '$500K-$2M': [
                r'growing\s*company',
                r'established\s*\d{4}',
                r'multiple\s*clients',
                r'professional\s*services'
            ],
            '$2M+': [
                r'industry\s*leader',
                r'enterprise\s*clients',
                r'national\s*presence',
                r'award\s*winning'
            ]
        }
    
    def analyze_website_signals(self, url: str, content: str) -> Dict:
        """Extract business intelligence signals from website"""
        intelligence = {
            'employee_estimate': 'unknown',
            'revenue_estimate': 'unknown',
            'business_maturity': 'unknown',
            'market_position': 'unknown',
            'growth_signals': []
        }
        
        content_lower = content.lower()
        
        # Employee count estimation
        for size, patterns in self.employee_indicators.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    intelligence['employee_estimate'] = size
                    break
            if intelligence['employee_estimate'] != 'unknown':
                break
        
        # Revenue estimation
        for revenue_range, patterns in self.revenue_indicators.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    intelligence['revenue_estimate'] = revenue_range
                    break
            if intelligence['revenue_estimate'] != 'unknown':
                break
        
        # Business maturity signals
        maturity_signals = {
            'startup': [r'startup', r'new\s*company', r'recently\s*founded'],
            'growing': [r'growing', r'expanding', r'scaling'],
            'established': [r'established', r'since\s*\d{4}', r'years?\s*of\s*experience'],
            'mature': [r'industry\s*leader', r'decades\s*of', r'market\s*leader']
        }
        
        for maturity, patterns in maturity_signals.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    intelligence['business_maturity'] = maturity
                    break
            if intelligence['business_maturity'] != 'unknown':
                break
        
        # Growth signals
        growth_patterns = [
            r'hiring', r'jobs?', r'careers?', r'join\s*our\s*team',
            r'expanding', r'new\s*location', r'opening\s*soon',
            r'award', r'recognition', r'featured\s*in'
        ]
        
        for pattern in growth_patterns:
            if re.search(pattern, content_lower):
                intelligence['growth_signals'].append(pattern.replace(r'\s*', ' '))
        
        return intelligence
    
    def analyze_social_media_presence(self, company_name: str, website_content: str) -> Dict:
        """Analyze social media presence from website links"""
        social_presence = {
            'platforms': [],
            'engagement_estimate': 'unknown',
            'content_quality': 'unknown'
        }
        
        # Look for social media links in website content
        social_patterns = {
            'facebook': r'facebook\.com/[a-zA-Z0-9._-]+',
            'instagram': r'instagram\.com/[a-zA-Z0-9._-]+',
            'linkedin': r'linkedin\.com/company/[a-zA-Z0-9._-]+',
            'twitter': r'twitter\.com/[a-zA-Z0-9._-]+'
        }
        
        for platform, pattern in social_patterns.items():
            if re.search(pattern, website_content.lower()):
                social_presence['platforms'].append(platform)
        
        # Estimate engagement based on platform diversity
        platform_count = len(social_presence['platforms'])
        if platform_count >= 3:
            social_presence['engagement_estimate'] = 'high'
        elif platform_count >= 2:
            social_presence['engagement_estimate'] = 'medium'
        elif platform_count >= 1:
            social_presence['engagement_estimate'] = 'low'
        
        return social_presence

class CompetitorAnalyzer(EthicalWebScraper):
    """Analyze competitors from public information"""
    
    def __init__(self):
        super().__init__()
        
        # Competitive positioning indicators
        self.positioning_patterns = {
            'premium': [
                r'premium', r'luxury', r'high[- ]end', r'exclusive',
                r'boutique', r'elite', r'specialist'
            ],
            'value': [
                r'affordable', r'budget', r'value', r'cost[- ]effective',
                r'competitive\s*pricing', r'best\s*price'
            ],
            'service': [
                r'full[- ]service', r'comprehensive', r'one[- ]stop',
                r'complete\s*solution', r'end[- ]to[- ]end'
            ],
            'specialist': [
                r'specialist', r'expert', r'specialized', r'niche',
                r'focused\s*on', r'dedicated\s*to'
            ]
        }
    
    def find_competitors(self, business_type: str, location: str, exclude_domain: str) -> List[str]:
        """Find competitor websites through search simulation"""
        # For production, this would use real search APIs or directories
        # For now, returning empty list to avoid fictitious URL errors
        # TODO: Implement real competitor discovery using Google Search API or similar
        
        logger.info(f"Competitor analysis temporarily disabled - implement real competitor discovery for {business_type} in {location}")
        return []  # Return empty list instead of fictitious URLs
    
    def analyze_competitor(self, competitor_url: str) -> Optional[CompetitorProfile]:
        """Analyze a single competitor"""
        content = self.fetch_with_respect(competitor_url)
        if not content:
            return None
        
        try:
            content_lower = content.lower()
            
            # Extract company name from title or content
            name_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
            name = name_match.group(1).strip() if name_match else urlparse(competitor_url).netloc
            
            # Determine positioning
            positioning = 'unknown'
            for pos_type, patterns in self.positioning_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, content_lower):
                        positioning = pos_type
                        break
                if positioning != 'unknown':
                    break
            
            # Estimate size from content complexity and features
            estimated_size = 'small'  # Default
            if len(content) > 100000:  # Large, complex site
                estimated_size = 'large'
            elif len(content) > 50000:  # Medium complexity
                estimated_size = 'medium'
            
            # Technology detection (basic)
            tech_stack = []
            tech_patterns = {
                'WordPress': [r'wp-content', r'wp-includes'],
                'React': [r'react', r'_next'],
                'Shopify': [r'shopify', r'myshopify'],
                'Squarespace': [r'squarespace']
            }
            
            for tech, patterns in tech_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, content_lower):
                        tech_stack.append(tech)
                        break
            
            # Identify strengths and weaknesses (heuristic analysis)
            strengths = []
            weaknesses = []
            
            # Strength indicators
            if re.search(r'award|recognition|certified|accredited', content_lower):
                strengths.append('Industry recognition')
            if re.search(r'testimonial|review|feedback', content_lower):
                strengths.append('Customer testimonials')
            if re.search(r'blog|news|insights', content_lower):
                strengths.append('Content marketing')
            
            # Weakness indicators
            if not re.search(r'https://', competitor_url):
                weaknesses.append('No SSL certificate')
            if not re.search(r'contact|phone|email', content_lower):
                weaknesses.append('Poor contact information')
            if len(content) < 10000:
                weaknesses.append('Limited website content')
            
            return CompetitorProfile(
                name=name,
                website=competitor_url,
                estimated_size=estimated_size,
                technology_stack=tech_stack,
                marketing_positioning=positioning,
                pricing_signals=None,  # Would require more sophisticated analysis
                strengths=strengths,
                weaknesses=weaknesses
            )
            
        except Exception as e:
            logger.error(f"Error analyzing competitor {competitor_url}: {e}")
            return None

class BusinessIntelligenceEngine:
    """Main engine for business intelligence gathering"""
    
    def __init__(self):
        self.data_enricher = PublicBusinessDataEnricher()
        self.competitor_analyzer = CompetitorAnalyzer()
    
    def gather_intelligence(self, company_name: str, website_url: str, 
                          business_type: str, location: str) -> BusinessIntelligence:
        """Gather comprehensive business intelligence"""
        logger.info(f"🔍 Gathering intelligence for {company_name}")
        
        # Get website content
        website_content = self.data_enricher.fetch_with_respect(website_url)
        
        if not website_content:
            logger.warning(f"Could not fetch website content for {company_name}")
            return self._create_minimal_intelligence(company_name)
        
        # Analyze website signals
        website_signals = self.data_enricher.analyze_website_signals(website_url, website_content)
        
        # Social media presence
        social_presence = self.data_enricher.analyze_social_media_presence(company_name, website_content)
        
        # Find and analyze competitors
        competitors = self.competitor_analyzer.find_competitors(business_type, location, website_url)
        competitor_profiles = []
        
        for competitor_url in competitors[:3]:  # Limit to top 3 for efficiency
            profile = self.competitor_analyzer.analyze_competitor(competitor_url)
            if profile:
                competitor_profiles.append(profile)
        
        # Determine competitive positioning
        competitive_positioning = self._analyze_competitive_position(
            website_signals, competitor_profiles
        )
        
        # Generate market signals
        market_signals = self._generate_market_signals(
            website_signals, social_presence, competitive_positioning
        )
        
        return BusinessIntelligence(
            company_name=company_name,
            employee_count_estimate=self._convert_size_to_count(website_signals['employee_estimate']),
            revenue_estimate=website_signals['revenue_estimate'],
            funding_info=None,  # Would require additional data sources
            social_media_presence=social_presence,
            online_reputation={'source': 'website_analysis', 'signals': website_signals['growth_signals']},
            competitive_positioning=competitive_positioning,
            market_signals=market_signals
        )
    
    def _convert_size_to_count(self, size_estimate: str) -> Optional[int]:
        """Convert size estimate to approximate employee count"""
        size_mapping = {
            'micro': 2,
            'small': 15,
            'medium': 75,
            'large': 250,
            'unknown': None
        }
        return size_mapping.get(size_estimate)
    
    def _analyze_competitive_position(self, website_signals: Dict, 
                                    competitor_profiles: List[CompetitorProfile]) -> Dict:
        """Analyze competitive position relative to competitors"""
        if not competitor_profiles:
            return {'position': 'unknown', 'advantages': [], 'disadvantages': []}
        
        advantages = []
        disadvantages = []
        
        # Compare technology stack
        own_tech_count = len(website_signals.get('tech_stack', []))
        competitor_tech_avg = sum(len(comp.technology_stack) for comp in competitor_profiles) / len(competitor_profiles)
        
        if own_tech_count > competitor_tech_avg:
            advantages.append('More advanced technology stack')
        elif own_tech_count < competitor_tech_avg:
            disadvantages.append('Less sophisticated technology')
        
        # Compare business maturity
        maturity = website_signals.get('business_maturity', 'unknown')
        if maturity in ['established', 'mature']:
            advantages.append('Established market presence')
        elif maturity in ['startup', 'growing']:
            disadvantages.append('Less market maturity than competitors')
        
        return {
            'position': 'competitive' if len(advantages) >= len(disadvantages) else 'challenging',
            'advantages': advantages,
            'disadvantages': disadvantages,
            'competitor_count': len(competitor_profiles)
        }
    
    def _generate_market_signals(self, website_signals: Dict, social_presence: Dict, 
                               competitive_positioning: Dict) -> List[str]:
        """Generate market intelligence signals"""
        signals = []
        
        # Growth signals
        if website_signals.get('growth_signals'):
            signals.append('Company showing growth indicators')
        
        # Digital presence signals
        platform_count = len(social_presence.get('platforms', []))
        if platform_count >= 3:
            signals.append('Strong multi-platform digital presence')
        elif platform_count <= 1:
            signals.append('Limited digital marketing presence')
        
        # Competitive signals
        if competitive_positioning.get('position') == 'challenging':
            signals.append('Facing competitive pressure in market')
        
        # Technology signals
        if website_signals.get('employee_estimate') in ['small', 'medium']:
            signals.append('Likely candidate for digital transformation')
        
        return signals
    
    def _create_minimal_intelligence(self, company_name: str) -> BusinessIntelligence:
        """Create minimal intelligence when data gathering fails"""
        return BusinessIntelligence(
            company_name=company_name,
            employee_count_estimate=None,
            revenue_estimate='unknown',
            funding_info=None,
            social_media_presence={'platforms': [], 'engagement_estimate': 'unknown'},
            online_reputation={'source': 'unavailable'},
            competitive_positioning={'position': 'unknown'},
            market_signals=['Limited public data available']
        )

# Demo function
def demo_business_intelligence():
    """Demo the business intelligence system"""
    print("🔍" + "="*60)
    print("   BUSINESS INTELLIGENCE GATHERING DEMO")
    print("="*63)
    
    engine = BusinessIntelligenceEngine()
    
    # Test cases
    test_companies = [
        {
            'name': 'Test Restaurant',
            'website': 'https://example-restaurant.com',
            'business_type': 'restaurant',
            'location': 'Rio de Janeiro, Brazil'
        },
        {
            'name': 'Test Dental Clinic', 
            'website': 'https://example-dental.com',
            'business_type': 'dental clinic',
            'location': 'Toronto, Canada'
        }
    ]
    
    for company in test_companies:
        print(f"\n🏢 Analyzing: {company['name']}")
        
        intelligence = engine.gather_intelligence(
            company['name'],
            company['website'],
            company['business_type'],
            company['location']
        )
        
        print(f"   • Employee Estimate: {intelligence.employee_count_estimate}")
        print(f"   • Revenue Estimate: {intelligence.revenue_estimate}")
        print(f"   • Social Platforms: {len(intelligence.social_media_presence['platforms'])}")
        print(f"   • Competitive Position: {intelligence.competitive_positioning.get('position')}")
        print(f"   • Market Signals: {len(intelligence.market_signals)}")
    
    print(f"\n🎯 KEY FEATURES:")
    print(f"   • Ethical scraping with robots.txt respect")
    print(f"   • Public data analysis only")
    print(f"   • Competitive intelligence gathering")
    print(f"   • Market signal identification")
    
    print("\n" + "="*63)
    print("   BUSINESS INTELLIGENCE DEMO COMPLETE")
    print("="*63)

if __name__ == "__main__":
    demo_business_intelligence()