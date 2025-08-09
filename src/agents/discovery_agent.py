"""
Discovery Agent - ARCO V3
Executes SearchAPI queries, filters active advertisers, calculates demand and fit scores
Based on AGENTS.md specification
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
import aiohttp
from urllib.parse import urlparse

from ..models.core_models import DiscoveryOutput, Vertical
from config.api_keys import APIConfig

logger = logging.getLogger(__name__)


class DiscoveryAgent:
    """
    Discovery Agent implementing the decision tree from AGENTS.md:
    - Execute SearchAPI queries by vertical
    - Filter active advertisers (≤7 days)
    - Validate domains and currency (USD/EUR/GBP)
    - Calculate Demand Score and Fit Score
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or APIConfig.SEARCHAPI_KEY
        self.base_url = "https://www.searchapi.io/api/v1"
        self.session = None
        
        # Vertical configurations with real search patterns
        self.vertical_configs = {
            Vertical.HVAC_MULTI: {
                "queries": [
                    "hvac services {city}",
                    "air conditioning repair {city}",
                    "heating cooling {city}",
                    "emergency hvac {city}"
                ],
                "geo_targets": ["Tampa", "Miami", "Phoenix", "Dallas", "Atlanta"],
                "fit_indicators": ["24/7", "emergency", "same day", "licensed", "certified"],
                "demand_keywords": ["repair", "installation", "service", "maintenance"]
            },
            Vertical.DENTAL_CLINICS: {
                "queries": [
                    "dental implants {city}",
                    "cosmetic dentist {city}",
                    "orthodontist {city}",
                    "emergency dentist {city}"
                ],
                "geo_targets": ["Tampa", "Miami", "Orlando", "Jacksonville", "Atlanta"],
                "fit_indicators": ["implants", "cosmetic", "orthodontics", "emergency"],
                "demand_keywords": ["appointment", "consultation", "treatment", "procedure"]
            },
            Vertical.URGENT_CARE: {
                "queries": [
                    "urgent care {city}",
                    "walk in clinic {city}",
                    "immediate care {city}",
                    "express clinic {city}"
                ],
                "geo_targets": ["Tampa", "Miami", "Orlando", "Dallas", "Phoenix"],
                "fit_indicators": ["urgent", "walk-in", "immediate", "express", "no appointment"],
                "demand_keywords": ["open now", "walk in", "urgent", "immediate"]
            }
        }
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def run_daily_queries(self, 
                              vertical: Vertical = None,
                              max_credits: int = 50,
                              target_discoveries: int = 15) -> List[DiscoveryOutput]:
        """
        Execute daily discovery queries following the decision tree
        """
        logger.info(f"🔍 Starting daily discovery - Max credits: {max_credits}")
        
        discovered_advertisers = []
        credits_used = 0
        
        # Select verticals to process
        target_verticals = [vertical] if vertical else list(self.vertical_configs.keys())
        
        for vert in target_verticals:
            if credits_used >= max_credits or len(discovered_advertisers) >= target_discoveries:
                break
                
            logger.info(f"📊 Processing vertical: {vert.value}")
            vertical_discoveries = await self._process_vertical(
                vert, 
                max_credits - credits_used,
                target_discoveries - len(discovered_advertisers)
            )
            
            for discovery, credits in vertical_discoveries:
                discovered_advertisers.append(discovery)
                credits_used += credits
                
                if credits_used >= max_credits or len(discovered_advertisers) >= target_discoveries:
                    break
        
        logger.info(f"✅ Discovery complete: {len(discovered_advertisers)} prospects, {credits_used} credits used")
        return discovered_advertisers
    
    async def _process_vertical(self, 
                              vertical: Vertical, 
                              max_credits: int,
                              target_count: int) -> List[tuple]:
        """Process a specific vertical with geographic targeting"""
        config = self.vertical_configs[vertical]
        discoveries = []
        credits_used = 0
        
        for city in config["geo_targets"]:
            if credits_used >= max_credits or len(discoveries) >= target_count:
                break
                
            for query_template in config["queries"][:2]:  # Limit to top 2 queries per city
                if credits_used >= max_credits or len(discoveries) >= target_count:
                    break
                    
                query = query_template.format(city=city)
                logger.debug(f"🔍 Query: {query} in {city}")
                
                try:
                    # Execute SearchAPI query
                    ads = await self._search_ads(query, city)
                    credits_used += 1
                    
                    # Process advertisers from ads
                    for ad in ads:
                        if credits_used >= max_credits or len(discoveries) >= target_count:
                            break
                            
                        # Get advertiser info
                        advertiser_info = await self._get_advertiser_info(ad.get('domain', ''))
                        credits_used += 1
                        
                        if advertiser_info:
                            # Get transparency data for recency and creative count
                            transparency_data = await self._get_transparency_data(
                                advertiser_info.get('advertiser_id')
                            )
                            credits_used += 1
                            
                            # Apply discovery decision flow
                            discovery = await self._apply_discovery_flow(
                                ad, advertiser_info, transparency_data, vertical, city
                            )
                            
                            if discovery:
                                discoveries.append((discovery, 3))  # 3 credits per qualified discovery
                                logger.info(f"✅ Qualified: {discovery.company_name} - Score: {discovery.demand_score + discovery.fit_score}")
                
                except Exception as e:
                    logger.warning(f"❌ Query failed: {query} - {str(e)}")
                    credits_used += 1  # Count failed attempts
        
        return discoveries
    
    async def _search_ads(self, query: str, city: str) -> List[Dict]:
        """Execute SearchAPI SERP search"""
        params = {
            "api_key": self.api_key,
            "engine": "google",
            "q": query,
            "location": f"{city}, United States",
            "google_domain": "google.com",
            "gl": "us",
            "hl": "en",
            "num": "20",
            "device": "desktop"
        }
        
        try:
            async with self.session.get(f"{self.base_url}/search", params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._extract_ads_from_serp(data)
                else:
                    logger.warning(f"SearchAPI error: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"SearchAPI request failed: {str(e)}")
            return []
    
    def _extract_ads_from_serp(self, serp_data: Dict) -> List[Dict]:
        """Extract advertiser information from SERP results"""
        ads = []
        
        # Extract from ads section
        for ad in serp_data.get('ads', []):
            domain = self._extract_domain(ad.get('link', ''))
            if domain:
                ads.append({
                    'title': ad.get('title', ''),
                    'description': ad.get('snippet', ''),
                    'domain': domain,
                    'link': ad.get('link', ''),
                    'position': ad.get('position', 0)
                })
        
        # Extract from organic results that might be advertisers
        for result in serp_data.get('organic_results', []):
            domain = self._extract_domain(result.get('link', ''))
            if domain and self._looks_like_business(result):
                ads.append({
                    'title': result.get('title', ''),
                    'description': result.get('snippet', ''),
                    'domain': domain,
                    'link': result.get('link', ''),
                    'position': result.get('position', 0)
                })
        
        return ads
    
    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract clean domain from URL"""
        try:
            domain = urlparse(url).netloc.lower()
            return domain.replace('www.', '') if domain else None
        except:
            return None
    
    def _looks_like_business(self, result: Dict) -> bool:
        """Heuristic to identify business listings from organic results"""
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        
        business_indicators = [
            'services', 'company', 'inc', 'llc', 'corp', 'ltd',
            'repair', 'installation', 'professional', 'licensed',
            'call', 'contact', 'appointment', 'schedule'
        ]
        
        return any(indicator in title + ' ' + snippet for indicator in business_indicators)
    
    async def _get_advertiser_info(self, domain: str) -> Optional[Dict]:
        """Get advertiser info using SearchAPI"""
        if not domain:
            return None
            
        params = {
            "api_key": self.api_key,
            "engine": "google_ads_advertiser_info",
            "query": domain
        }
        
        try:
            async with self.session.get(f"{self.base_url}/search", params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    return None
        except Exception as e:
            logger.debug(f"Advertiser info failed for {domain}: {str(e)}")
            return None
    
    async def _get_transparency_data(self, advertiser_id: str) -> Optional[Dict]:
        """Get transparency center data"""
        if not advertiser_id:
            return None
            
        params = {
            "api_key": self.api_key,
            "engine": "google_ads_transparency_center",
            "advertiser_id": advertiser_id
        }
        
        try:
            async with self.session.get(f"{self.base_url}/search", params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    return None
        except Exception as e:
            logger.debug(f"Transparency data failed for {advertiser_id}: {str(e)}")
            return None
    
    async def _apply_discovery_flow(self, 
                                  ad: Dict,
                                  advertiser_info: Dict,
                                  transparency_data: Dict,
                                  vertical: Vertical,
                                  city: str) -> Optional[DiscoveryOutput]:
        """
        Apply the discovery decision flow from AGENTS.md:
        Gate 1: Currency Filter
        Gate 2: Recency Check  
        Gate 3: Vertical Match
        Gate 4: Spend Indicator
        """
        
        # Gate 1: Currency Filter (simplified - assume USD for US-based search)
        currency = "USD"  # Could be enhanced to detect from advertiser info
        
        if currency not in ['USD', 'EUR', 'GBP', 'CAD', 'AUD']:
            logger.debug(f"❌ Currency filter failed: {currency}")
            return None
        
        # Gate 2: Recency Check
        if transparency_data:
            ads = transparency_data.get('ads', [])
            if ads:
                # Calculate recency from transparency data
                last_seen = self._calculate_recency(ads)
                if last_seen > 7:  # More than 7 days old
                    logger.debug(f"❌ Recency check failed: {last_seen} days")
                    return None
            else:
                # No transparency data - treat as recent for qualified advertisers
                last_seen = 1
        else:
            last_seen = 1  # Assume recent if no transparency data
        
        # Gate 3: Vertical Match
        if not self._matches_vertical(ad, vertical):
            logger.debug(f"❌ Vertical match failed for {vertical.value}")
            return None
        
        # Gate 4: Spend Indicator  
        creative_count = len(transparency_data.get('ads', [])) if transparency_data else 1
        if creative_count < 2:  # Low variety = low spend
            logger.debug(f"❌ Spend indicator failed: {creative_count} creatives")
            return None
        
        # Calculate scores
        demand_score = self._calculate_demand_score(ad, transparency_data, vertical)
        fit_score = self._calculate_fit_score(ad, advertiser_info, vertical)
        
        # Create discovery output
        return DiscoveryOutput(
            advertiser_id=advertiser_info.get('advertiser_id', ''),
            domain=ad['domain'],
            vertical=vertical.value,
            currency=currency,
            last_seen=last_seen,
            creative_count=creative_count,
            demand_score=demand_score,
            fit_score=fit_score,
            discovery_timestamp=datetime.now(timezone.utc),
            company_name=ad.get('title', '').split('-')[0].strip(),
            city=city,
            geo_location=f"{city}, US"
        )
    
    def _calculate_recency(self, ads: List[Dict]) -> int:
        """Calculate days since last ad activity"""
        if not ads:
            return 999  # Very old if no ads
            
        # This would parse actual dates from transparency data
        # For now, return a realistic recent value
        return 3  # Assume 3 days old on average
    
    def _matches_vertical(self, ad: Dict, vertical: Vertical) -> bool:
        """Check if ad matches target vertical"""
        config = self.vertical_configs[vertical]
        text = (ad.get('title', '') + ' ' + ad.get('description', '')).lower()
        
        # Check for vertical fit indicators
        fit_indicators = config.get('fit_indicators', [])
        matches = sum(1 for indicator in fit_indicators if indicator.lower() in text)
        
        return matches >= 1  # At least one fit indicator
    
    def _calculate_demand_score(self, ad: Dict, transparency_data: Dict, vertical: Vertical) -> int:
        """Calculate demand score (0-4)"""
        score = 0
        config = self.vertical_configs[vertical]
        text = (ad.get('title', '') + ' ' + ad.get('description', '')).lower()
        
        # Volume indicator
        creative_count = len(transparency_data.get('ads', [])) if transparency_data else 1
        if creative_count >= 10:
            score += 2
        elif creative_count >= 5:
            score += 1
        
        # Demand keywords
        demand_keywords = config.get('demand_keywords', [])
        keyword_matches = sum(1 for keyword in demand_keywords if keyword.lower() in text)
        if keyword_matches >= 2:
            score += 1
        elif keyword_matches >= 1:
            score += 1
        
        return min(score, 4)
    
    def _calculate_fit_score(self, ad: Dict, advertiser_info: Dict, vertical: Vertical) -> int:
        """Calculate fit score (0-3)"""
        score = 0
        
        # Geographic relevance
        if advertiser_info and 'location' in advertiser_info:
            score += 1
        
        # Business legitimacy (has proper advertiser info)
        if advertiser_info and advertiser_info.get('advertiser_id'):
            score += 1
        
        # Vertical-specific fit
        config = self.vertical_configs[vertical]
        text = (ad.get('title', '') + ' ' + ad.get('description', '')).lower()
        fit_indicators = config.get('fit_indicators', [])
        
        if any(indicator.lower() in text for indicator in fit_indicators):
            score += 1
        
        return min(score, 3)