#!/usr/bin/env python3
"""
ENHANCED DISCOVERY AGENT - ARCO V3
Critical improvements based on SearchAPI documentation analysis
3-Layer Strategy: Advertiser Search → Ad Details Enrichment → Vulnerability Analysis
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any, Tuple
import aiohttp
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class EnhancedDiscoveryAgent:
    """
    ENHANCED Discovery Agent with 3-Layer Strategy:
    Layer 1: MAXIMUM Advertiser Search (100 advertisers + 100 domains)
    Layer 2: Ad Details Enrichment (creative analysis)  
    Layer 3: Strategic Vulnerability Analysis (growth opportunities)
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.searchapi.io/api/v1"
        self.session = None
        self.logger = logger
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def discover_growth_opportunities(self, query: str, region: str = "US") -> List[Dict]:
        """
        CRITICAL: 3-Layer Enhanced Discovery Strategy
        Returns highly qualified prospects with enriched vulnerability data
        """
        self.logger.info(f"🚀 ENHANCED DISCOVERY: {query} in {region}")
        
        # LAYER 1: MAXIMUM Advertiser Search
        advertisers_data = await self._layer1_maximum_advertiser_search(query, region)
        
        # LAYER 2: Ad Details Enrichment
        enriched_prospects = await self._layer2_ad_details_enrichment(advertisers_data)
        
        # LAYER 3: Strategic Vulnerability Analysis
        qualified_prospects = await self._layer3_vulnerability_analysis(enriched_prospects)
        
        return qualified_prospects
    
    async def _layer1_maximum_advertiser_search(self, query: str, region: str) -> Dict:
        """
        LAYER 1: MAXIMUM Advertiser Search
        Uses correct engine with maximum parameters
        """
        params = {
            "api_key": self.api_key,
            "engine": "google_ads_transparency_center_advertiser_search",  # CORRECTED
            "q": query,
            "region": region,
            "num_advertisers": 100,  # MAXIMUM
            "num_domains": 100       # MAXIMUM
        }
        
        self.logger.info(f"📡 LAYER 1: Advertiser Search with MAXIMUM parameters")
        self.logger.info(f"   Query: {query}")
        self.logger.info(f"   Max Advertisers: 100")
        self.logger.info(f"   Max Domains: 100")
        
        try:
            async with self.session.get(f"{self.base_url}/search", params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    advertisers = data.get('advertisers', [])
                    domains = data.get('domains', [])
                    
                    self.logger.info(f"✅ LAYER 1 SUCCESS:")
                    self.logger.info(f"   📊 Advertisers found: {len(advertisers)}")
                    self.logger.info(f"   🌐 Domains found: {len(domains)}")
                    
                    return data
                else:
                    self.logger.error(f"❌ LAYER 1 FAILED: HTTP {response.status}")
                    return {"advertisers": [], "domains": []}
        
        except Exception as e:
            self.logger.error(f"❌ LAYER 1 EXCEPTION: {e}")
            return {"advertisers": [], "domains": []}
    
    async def _layer2_ad_details_enrichment(self, advertisers_data: Dict) -> List[Dict]:
        """
        LAYER 2: Ad Details Enrichment
        Extracts creative_ids and enriches with detailed ad information
        """
        advertisers = advertisers_data.get('advertisers', [])
        domains = advertisers_data.get('domains', [])
        
        self.logger.info(f"🔬 LAYER 2: Ad Details Enrichment")
        self.logger.info(f"   Processing {len(advertisers)} advertisers")
        
        enriched_prospects = []
        
        # Process advertisers with detailed enrichment
        for advertiser in advertisers[:20]:  # Focus on top 20 for quality
            enriched_prospect = await self._enrich_advertiser_details(advertiser)
            if enriched_prospect:
                enriched_prospects.append(enriched_prospect)
        
        # Process domains with basic enrichment
        for domain_obj in domains[:20]:  # Focus on top 20 domains
            domain_prospect = await self._enrich_domain_details(domain_obj)
            if domain_prospect:
                enriched_prospects.append(domain_prospect)
        
        self.logger.info(f"✅ LAYER 2 COMPLETE: {len(enriched_prospects)} enriched prospects")
        return enriched_prospects
    
    async def _enrich_advertiser_details(self, advertiser: Dict) -> Optional[Dict]:
        """
        CRITICAL: Enrich advertiser with Ad Details API
        Extracts creative_ids and analyzes ad variations
        """
        advertiser_id = advertiser.get('id')
        if not advertiser_id:
            return None
        
        self.logger.info(f"🔍 Enriching advertiser: {advertiser.get('name', 'Unknown')}")
        
        # Step 1: Get advertiser's ads via transparency center
        transparency_data = await self._get_advertiser_ads(advertiser_id)
        if not transparency_data:
            return advertiser  # Return basic data if enrichment fails
        
        # Step 2: Extract creative_ids for detailed analysis
        ad_creatives = transparency_data.get('ad_creatives', [])
        creative_ids = [creative.get('creative_id') for creative in ad_creatives[:5]]  # Top 5
        
        # Step 3: Enrich with ad details for each creative
        detailed_creatives = []
        for creative_id in creative_ids:
            if creative_id:
                ad_details = await self._get_ad_details(advertiser_id, creative_id)
                if ad_details:
                    detailed_creatives.append(ad_details)
        
        # Combine enriched data
        enriched_data = {
            **advertiser,
            'transparency_data': transparency_data,
            'detailed_creatives': detailed_creatives,
            'enrichment_level': 'FULL',
            'total_creatives_analyzed': len(detailed_creatives)
        }
        
        self.logger.info(f"✅ Enriched {advertiser.get('name')}: {len(detailed_creatives)} detailed creatives")
        return enriched_data
    
    async def _get_advertiser_ads(self, advertiser_id: str) -> Optional[Dict]:
        """Get advertiser ads via transparency center"""
        params = {
            "api_key": self.api_key,
            "engine": "google_ads_transparency_center",
            "advertiser_id": advertiser_id
        }
        
        try:
            async with self.session.get(f"{self.base_url}/search", params=params, timeout=20) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            self.logger.debug(f"Transparency data failed for {advertiser_id}: {e}")
            return None
    
    async def _get_ad_details(self, advertiser_id: str, creative_id: str) -> Optional[Dict]:
        """
        CRITICAL: Ad Details API for deep creative analysis
        Extracts variations, ad_information, regions data
        """
        params = {
            "api_key": self.api_key,
            "engine": "google_ads_transparency_center_ad_details",  # CORRECT ENGINE
            "advertiser_id": advertiser_id,
            "creative_id": creative_id
        }
        
        try:
            async with self.session.get(f"{self.base_url}/search", params=params, timeout=20) as response:
                if response.status == 200:
                    ad_details = await response.json()
                    
                    # Extract rich data for vulnerability analysis
                    ad_information = ad_details.get('ad_information', {})
                    variations = ad_details.get('variations', [])
                    
                    return {
                        'creative_id': creative_id,
                        'ad_information': ad_information,
                        'variations': variations,
                        'format': ad_information.get('format'),
                        'topic': ad_information.get('topic'),
                        'first_shown_date': ad_information.get('first_shown_date'),
                        'last_shown_date': ad_information.get('last_shown_date'),
                        'regions': ad_information.get('regions', []),
                        'audience_selection': ad_information.get('audience_selection', {}),
                        'enrichment_timestamp': datetime.now().isoformat()
                    }
                return None
        except Exception as e:
            self.logger.debug(f"Ad details failed for {creative_id}: {e}")
            return None
    
    async def _enrich_domain_details(self, domain_obj: Dict) -> Optional[Dict]:
        """Basic domain enrichment"""
        domain_name = domain_obj.get('name')
        if not domain_name:
            return None
        
        return {
            'domain': domain_name,
            'type': 'domain_prospect',
            'enrichment_level': 'BASIC',
            'estimated_business_name': self._format_business_name(domain_name)
        }
    
    def _format_business_name(self, domain: str) -> str:
        """Format business name from domain"""
        name = domain.replace('.com', '').replace('.net', '').replace('.org', '')
        return name.replace('-', ' ').replace('_', ' ').title()
    
    async def _layer3_vulnerability_analysis(self, enriched_prospects: List[Dict]) -> List[Dict]:
        """
        LAYER 3: Strategic Vulnerability Analysis
        Analyzes enriched data for growth opportunities and vulnerabilities
        """
        self.logger.info(f"🎯 LAYER 3: Strategic Vulnerability Analysis")
        
        qualified_prospects = []
        
        for prospect in enriched_prospects:
            vulnerability_analysis = await self._analyze_strategic_vulnerabilities(prospect)
            
            # Qualify based on growth potential
            growth_score = self._calculate_growth_score(vulnerability_analysis)
            
            if growth_score >= 5:  # Minimum threshold
                qualified_prospect = {
                    **prospect,
                    'vulnerability_analysis': vulnerability_analysis,
                    'growth_score': growth_score,
                    'qualification_status': 'QUALIFIED',
                    'analysis_timestamp': datetime.now().isoformat()
                }
                qualified_prospects.append(qualified_prospect)
        
        # Sort by growth score (highest first)
        qualified_prospects.sort(key=lambda x: x['growth_score'], reverse=True)
        
        self.logger.info(f"✅ LAYER 3 COMPLETE: {len(qualified_prospects)} qualified prospects")
        return qualified_prospects
    
    async def _analyze_strategic_vulnerabilities(self, prospect: Dict) -> Dict:
        """
        CRITICAL: Strategic vulnerability analysis using enriched ad details
        """
        vulnerabilities = []
        opportunities = []
        strategic_insights = []
        
        # Analyze based on enrichment level
        if prospect.get('enrichment_level') == 'FULL':
            # Deep analysis with ad details
            detailed_creatives = prospect.get('detailed_creatives', [])
            
            # 1. FORMAT ANALYSIS
            formats = set()
            for creative in detailed_creatives:
                fmt = creative.get('format')
                if fmt:
                    formats.add(fmt)
            
            if 'video' not in formats and len(formats) > 0:
                vulnerabilities.append('MISSING_VIDEO_STRATEGY')
                opportunities.append('Video advertising implementation ($2-5K/month potential)')
            
            if len(formats) == 1:
                vulnerabilities.append('SINGLE_FORMAT_LIMITATION')
                opportunities.append('Multi-format strategy expansion')
            
            # 2. RECENCY ANALYSIS
            recent_ads = 0
            now = datetime.now()
            
            for creative in detailed_creatives:
                last_shown = creative.get('last_shown_date')
                if last_shown:
                    try:
                        last_date = datetime.fromisoformat(last_shown)
                        days_ago = (now - last_date).days
                        if days_ago <= 30:
                            recent_ads += 1
                    except:
                        continue
            
            if recent_ads == 0:
                vulnerabilities.append('STALE_CAMPAIGN_PORTFOLIO')
                opportunities.append('Campaign refresh and optimization ($3-8K/month)')
            
            # 3. AUDIENCE TARGETING ANALYSIS
            for creative in detailed_creatives:
                audience_selection = creative.get('audience_selection', {})
                if audience_selection.get('demographic_info') == 'Some included, some excluded':
                    strategic_insights.append('Advanced demographic targeting available')
                if audience_selection.get('geographic_locations') == 'Some included, some excluded':
                    strategic_insights.append('Geographic optimization opportunity')
            
            # 4. TOPIC ANALYSIS
            topics = set()
            for creative in detailed_creatives:
                topic = creative.get('topic')
                if topic:
                    topics.add(topic)
            
            if len(topics) == 1:
                vulnerabilities.append('LIMITED_TOPIC_DIVERSIFICATION')
                opportunities.append('Cross-topic expansion strategy')
        
        else:
            # Basic analysis for domain-only prospects
            vulnerabilities.append('NO_DIGITAL_ADVERTISING_PRESENCE')
            opportunities.append('Complete digital advertising setup ($5-15K/month potential)')
            strategic_insights.append('Greenfield opportunity for digital transformation')
        
        return {
            'vulnerabilities': vulnerabilities,
            'opportunities': opportunities,
            'strategic_insights': strategic_insights,
            'total_vulnerabilities': len(vulnerabilities),
            'opportunity_value': self._calculate_opportunity_value(vulnerabilities)
        }
    
    def _calculate_growth_score(self, vulnerability_analysis: Dict) -> int:
        """Calculate growth potential score (0-10)"""
        vulnerabilities = vulnerability_analysis.get('vulnerabilities', [])
        opportunities = vulnerability_analysis.get('opportunities', [])
        
        # High-impact vulnerabilities = high growth potential
        high_impact_vulns = [
            'NO_DIGITAL_ADVERTISING_PRESENCE',
            'STALE_CAMPAIGN_PORTFOLIO', 
            'MISSING_VIDEO_STRATEGY',
            'LIMITED_TOPIC_DIVERSIFICATION'
        ]
        
        score = 0
        for vuln in vulnerabilities:
            if any(high in vuln for high in high_impact_vulns):
                score += 2
            else:
                score += 1
        
        # Bonus for multiple opportunities
        score += min(len(opportunities), 3)
        
        return min(score, 10)  # Cap at 10
    
    def _calculate_opportunity_value(self, vulnerabilities: List[str]) -> str:
        """Calculate revenue opportunity based on vulnerabilities"""
        if any('NO_DIGITAL_ADVERTISING_PRESENCE' in v for v in vulnerabilities):
            return 'HIGH ($5-15K/month potential)'
        elif any('STALE_CAMPAIGN_PORTFOLIO' in v for v in vulnerabilities):
            return 'MEDIUM-HIGH ($3-8K/month potential)'
        elif len(vulnerabilities) >= 2:
            return 'MEDIUM ($2-5K/month potential)'
        else:
            return 'LOW-MEDIUM ($1-3K/month potential)'


# INTEGRATION EXAMPLE
async def test_enhanced_discovery():
    """Test the enhanced 3-layer discovery strategy"""
    api_key = "your_api_key_here"
    
    async with EnhancedDiscoveryAgent(api_key) as agent:
        prospects = await agent.discover_growth_opportunities(
            query="dental implants Tampa",
            region="US"
        )
        
        print(f"✅ Enhanced Discovery Results: {len(prospects)} qualified prospects")
        
        for i, prospect in enumerate(prospects[:3], 1):
            print(f"\n🏢 PROSPECT {i}:")
            print(f"   Name: {prospect.get('name', 'Unknown')}")
            print(f"   Growth Score: {prospect.get('growth_score')}/10")
            print(f"   Opportunity Value: {prospect.get('vulnerability_analysis', {}).get('opportunity_value')}")
            print(f"   Key Vulnerabilities: {len(prospect.get('vulnerability_analysis', {}).get('vulnerabilities', []))}")


if __name__ == "__main__":
    asyncio.run(test_enhanced_discovery())
