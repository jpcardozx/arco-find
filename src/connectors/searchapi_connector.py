#!/usr/bin/env python3
"""
🔌 SearchAPI Connector - Meta Ads Library Integration
Connector real para SearchAPI Meta Ads Library sem simulações
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class MetaAdData:
    """Dados reais de anúncios Meta extraídos via SearchAPI"""
    ad_id: str
    advertiser_name: str
    ad_text: str
    call_to_action: str
    targeting_countries: List[str]
    page_name: str
    spend_estimate: Optional[str] = None
    impressions_estimate: Optional[str] = None
    active_status: str = "ACTIVE"
    ad_delivery_start_time: Optional[str] = None

class SearchAPIConnector:
    """
    Connector real para SearchAPI Meta Ads Library
    Coleta dados reais de anúncios Meta sem simulações
    """
    
    def __init__(self, api_key: str = None):
        # Default API key if not provided
        if api_key is None:
            try:
                from config.api_keys import APIConfig
                api_config = APIConfig()
                api_key = api_config.SEARCH_API_KEY
            except:
                api_key = "3sgTQQBwGfmtBR1WBW61MgnU"  # Default fallback
        
        self.api_key = api_key
        self.base_url = "https://www.searchapi.io/api/v1/search"
        self.session = None
        
    async def _get_session(self):
        """Get or create aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
        
    async def search_meta_ads(self, 
                             query: str,
                             countries: List[str] = ["US"],
                             limit: int = 20,
                             active_status: str = "ACTIVE") -> List[MetaAdData]:
        """
        🔍 Busca anúncios reais no Meta Ads Library via SearchAPI
        
        Args:
            query: Termo de busca (ex: "dental clinic")
            countries: Lista de países (ex: ["US", "CA"])
            limit: Número máximo de anúncios
            active_status: Status dos anúncios (ACTIVE, INACTIVE, ALL)
            
        Returns:
            Lista de dados reais de anúncios Meta
        """
        try:
            session = await self._get_session()
            
            params = {
                'api_key': self.api_key,
                'engine': 'facebook_ads_library',
                'q': query,
                'ad_reached_countries': ','.join(countries),
                'ad_active_status': active_status,
                'limit': limit
            }
            
            logger.info(f"🔍 Searching Meta Ads: '{query}' in {countries}")
            
            async with session.get(self.base_url, params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    ads_raw = data.get('ads', [])
                    
                    # Parse real Meta ads data
                    parsed_ads = []
                    for ad in ads_raw:
                        try:
                            meta_ad = MetaAdData(
                                ad_id=ad.get('ad_snapshot_url', '').split('id=')[-1][:15],
                                advertiser_name=ad.get('page_name', 'Unknown'),
                                ad_text=ad.get('ad_creative_bodies', [''])[0][:200],
                                call_to_action=ad.get('ad_creative_link_captions', [''])[0],
                                targeting_countries=ad.get('ad_delivery_start_time', '').split(',') if ad.get('ad_delivery_start_time') else countries,
                                page_name=ad.get('page_name', 'Unknown'),
                                spend_estimate=ad.get('spend', {}).get('lower_bound'),
                                active_status=ad.get('ad_delivery_stop_time', 'ACTIVE'),
                                ad_delivery_start_time=ad.get('ad_delivery_start_time')
                            )
                            parsed_ads.append(meta_ad)
                        except Exception as e:
                            logger.warning(f"⚠️ Error parsing ad: {e}")
                            continue
                    
                    logger.info(f"✅ Found {len(parsed_ads)} real Meta ads")
                    return parsed_ads
                    
                elif response.status == 400:
                    logger.warning(f"⚠️ SearchAPI 400: Check query parameters")
                    return []
                elif response.status == 401:
                    logger.error(f"❌ SearchAPI 401: Invalid API key")
                    return []
                else:
                    logger.error(f"❌ SearchAPI error {response.status}")
                    return []
                    
        except asyncio.TimeoutError:
            logger.error("❌ SearchAPI timeout")
            return []
        except Exception as e:
            logger.error(f"❌ SearchAPI error: {e}")
            return []
    
    async def discover_competitors(self, 
                                 industry_keywords: List[str],
                                 countries: List[str] = ["US"]) -> Dict[str, List[MetaAdData]]:
        """
        🎯 Descobre competidores reais por indústria via Meta Ads
        
        Args:
            industry_keywords: Keywords da indústria (ex: ["dental", "dentist"])
            countries: Países alvo
            
        Returns:
            Dict com keyword -> lista de anúncios reais
        """
        competitors = {}
        
        for keyword in industry_keywords:
            ads = await self.search_meta_ads(
                query=keyword,
                countries=countries,
                limit=50
            )
            competitors[keyword] = ads
            
        return competitors
    
    async def analyze_ad_spend_patterns(self, ads: List[MetaAdData]) -> Dict[str, any]:
        """
        📊 Analisa padrões reais de investimento em anúncios
        
        Args:
            ads: Lista de anúncios reais
            
        Returns:
            Análise de padrões de spend
        """
        total_ads = len(ads)
        advertisers = set(ad.advertiser_name for ad in ads)
        
        # Analyze spend estimates where available
        spend_data = []
        for ad in ads:
            if ad.spend_estimate:
                try:
                    spend_data.append(float(ad.spend_estimate))
                except:
                    continue
        
        analysis = {
            'total_ads_analyzed': total_ads,
            'unique_advertisers': len(advertisers),
            'avg_spend_estimate': sum(spend_data) / len(spend_data) if spend_data else 0,
            'spend_estimates_available': len(spend_data),
            'top_advertisers': list(advertisers)[:10],
            'analysis_timestamp': datetime.now().isoformat(),
            'data_source': 'SearchAPI Meta Ads Library (Real Data)'
        }
        
        return analysis
    
    async def search_companies(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for companies using SearchAPI - generic company search
        """
        try:
            session = await self._get_session()
            
            params = {
                'engine': 'google',
                'q': query,
                'api_key': self.api_key,
                'num': max_results,
                'gl': 'us',
                'hl': 'en'
            }
            
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract company information from search results
                    companies = []
                    for result in data.get('organic_results', [])[:max_results]:
                        company_info = {
                            'name': result.get('title', ''),
                            'website': result.get('displayed_link', ''),
                            'description': result.get('snippet', ''),
                            'source': 'google_search'
                        }
                        
                        # Basic validation
                        if company_info['name'] and company_info['website']:
                            companies.append(company_info)
                    
                    logger.info(f"✅ Found {len(companies)} companies for query: {query}")
                    return companies
                else:
                    logger.warning(f"⚠️ SearchAPI error {response.status} for query: {query}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Company search error: {e}")
            return []
    
    async def discover_strategic_prospects(self, target, max_results: int = 10) -> List[Dict]:
        """
        Discover strategic prospects based on search target criteria
        """
        try:
            # Build strategic search query
            query_parts = []
            
            # Add industry keywords
            if hasattr(target, 'industry') and target.industry:
                query_parts.append(target.industry)
            
            # Add pain point keywords
            if hasattr(target, 'pain_point_keywords') and target.pain_point_keywords:
                pain_keywords = " OR ".join(target.pain_point_keywords[:2])  # Limit for API efficiency
                query_parts.append(f"({pain_keywords})")
            
            # Add location targeting
            if hasattr(target, 'location_focus') and target.location_focus:
                query_parts.append(f"site:linkedin.com/company {target.location_focus}")
            
            # Combine query
            strategic_query = " ".join(query_parts) if query_parts else "business marketing"
            
            logger.info(f"🎯 Strategic prospect search: {strategic_query}")
            
            # Use existing search_companies method
            prospects = await self.search_companies(strategic_query, max_results)
            
            # Enhance results with strategic scoring
            enhanced_prospects = []
            for prospect in prospects:
                enhanced_prospect = {
                    **prospect,
                    'strategic_score': self._calculate_strategic_score(prospect, target),
                    'discovery_method': 'strategic_search',
                    'target_match': True
                }
                enhanced_prospects.append(enhanced_prospect)
            
            # Sort by strategic score
            enhanced_prospects.sort(key=lambda x: x.get('strategic_score', 0), reverse=True)
            
            logger.info(f"✅ Discovered {len(enhanced_prospects)} strategic prospects")
            return enhanced_prospects
            
        except Exception as e:
            logger.error(f"❌ Strategic prospect discovery error: {e}")
            return []
    
    def _calculate_strategic_score(self, prospect: Dict, target) -> int:
        """Calculate strategic score based on target criteria"""
        score = 50  # Base score
        
        # Industry match
        if hasattr(target, 'industry') and target.industry:
            if target.industry.lower() in prospect.get('description', '').lower():
                score += 20
        
        # Pain point keywords match
        if hasattr(target, 'pain_point_keywords') and target.pain_point_keywords:
            description = prospect.get('description', '').lower()
            for keyword in target.pain_point_keywords:
                if keyword.lower() in description:
                    score += 10
        
        # Website quality (basic check)
        website = prospect.get('website', '')
        if website and len(website) > 10:
            score += 10
        
        # Priority score from target
        if hasattr(target, 'priority_score'):
            score += min(target.priority_score, 20)
        
        return min(score, 100)  # Cap at 100
    
    def search_ads_by_page(self, page_name: str) -> Dict:
        """
        Busca anúncios por nome da página (método sincrono para compatibilidade)
        """
        try:
            import requests
            
            params = {
                'engine': 'facebook_ads_library',
                'q': page_name,
                'api_key': self.api_key,
                'ad_reached_countries': 'US',
                'limit': 10
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ SearchAPI: Encontrados anúncios para {page_name}")
                return data
            else:
                logger.warning(f"⚠️ SearchAPI erro {response.status_code} para {page_name}")
                return {"data": []}
                
        except Exception as e:
            logger.error(f"❌ Erro na busca SearchAPI: {e}")
            return {"data": []}
    
    async def close(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
    
    def __del__(self):
        """Cleanup on deletion"""
        if self.session and not self.session.closed:
            try:
                asyncio.get_event_loop().run_until_complete(self.close())
            except:
                pass
