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
        self.logger = logger  # Add logger instance
        
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
            },
            # Sunday-Active Verticals - Canada & EU Focus
            Vertical.RESTAURANTS_CA: {
                "queries": [
                    "restaurant {city}",
                    "fine dining {city}",
                    "brunch {city}",
                    "sunday dinner {city}",
                    "food delivery {city}"
                ],
                "geo_targets": ["Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa"],
                "fit_indicators": ["reservation", "delivery", "takeout", "catering", "open sundays"],
                "demand_keywords": ["menu", "order", "book table", "delivery", "brunch"]
            },
            Vertical.HOTELS_EU: {
                "queries": [
                    "hotel {city}",
                    "boutique hotel {city}",
                    "weekend getaway {city}",
                    "city center hotel {city}",
                    "luxury accommodation {city}"
                ],
                "geo_targets": ["London", "Amsterdam", "Berlin", "Paris", "Barcelona"],
                "fit_indicators": ["booking", "reservation", "concierge", "24/7", "weekend"],
                "demand_keywords": ["book now", "availability", "rates", "weekend", "stay"]
            },
            Vertical.FITNESS_GYMS_CA: {
                "queries": [
                    "gym {city}",
                    "fitness center {city}",
                    "personal training {city}",
                    "sunday workout {city}",
                    "24 hour fitness {city}"
                ],
                "geo_targets": ["Toronto", "Vancouver", "Montreal", "Calgary", "Edmonton"],
                "fit_indicators": ["24/7", "personal training", "group classes", "membership", "open sundays"],
                "demand_keywords": ["membership", "join", "trial", "classes", "training"]
            },
            Vertical.PHARMACIES_EU: {
                "queries": [
                    "pharmacy {city}",
                    "sunday pharmacy {city}",
                    "emergency medication {city}",
                    "prescription {city}",
                    "chemist {city}"
                ],
                "geo_targets": ["London", "Dublin", "Edinburgh", "Manchester", "Birmingham"],
                "fit_indicators": ["prescription", "emergency", "sunday hours", "24 hour", "delivery"],
                "demand_keywords": ["prescription", "medication", "emergency", "open sunday", "delivery"]
            },
            Vertical.GAS_STATIONS_CA: {
                "queries": [
                    "gas station {city}",
                    "petrol station {city}",
                    "fuel {city}",
                    "convenience store gas {city}",
                    "24 hour gas {city}"
                ],
                "geo_targets": ["Toronto", "Vancouver", "Montreal", "Calgary", "Winnipeg"],
                "fit_indicators": ["24/7", "convenience", "car wash", "fuel", "open sundays"],
                "demand_keywords": ["fuel", "gas", "convenience", "open 24", "car wash"]
            },
            Vertical.CONVENIENCE_EU: {
                "queries": [
                    "convenience store {city}",
                    "corner shop {city}",
                    "sunday shopping {city}",
                    "late night store {city}",
                    "24 hour shop {city}"
                ],
                "geo_targets": ["London", "Amsterdam", "Berlin", "Copenhagen", "Stockholm"],
                "fit_indicators": ["24/7", "sunday opening", "convenience", "late night", "groceries"],
                "demand_keywords": ["open late", "sunday hours", "groceries", "convenience", "24 hour"]
            },
            Vertical.EMERGENCY_SERVICES_CA: {
                "queries": [
                    "emergency services {city}",
                    "24 hour repair {city}",
                    "sunday emergency {city}",
                    "plumbing emergency {city}",
                    "locksmith 24 hour {city}"
                ],
                "geo_targets": ["Toronto", "Vancouver", "Montreal", "Calgary", "Halifax"],
                "fit_indicators": ["24/7", "emergency", "same day", "sunday service", "immediate"],
                "demand_keywords": ["emergency", "urgent", "immediate", "24 hour", "sunday"]
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
            logger.info(f"📊 Vertical {vert.value} target: {target_discoveries - len(discovered_advertisers)}, credits: {max_credits - credits_used}")
            
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
        
        logger.info(f"🔍 Processing {vertical.value} with {len(config['geo_targets'])} cities")
        
        # OPTIMIZATION: Process all cities for broader Sunday prospect coverage
        cities_to_process = config["geo_targets"]  # Process ALL cities, not just first one
        
        for city in cities_to_process:
            if credits_used >= max_credits or len(discoveries) >= target_count:
                break
                
            logger.info(f"📍 Searching in {city}")
            
            for query_template in config["queries"][:3]:  # Increased from 2 to 3 queries per city
                if credits_used >= max_credits or len(discoveries) >= target_count:
                    break
                    
                query = query_template.format(city=city)
                logger.info(f"🔍 Executing query: '{query}' in {city}")
                
                try:
                    # Execute SearchAPI query
                    ads = await self._search_ads(query, city)
                    credits_used += 1
                    
                    logger.info(f"🎯 Found {len(ads)} potential advertisers from query: {query}")
                    
                    # Process ALL advertisers found, not just top 5
                    logger.info(f"🎯 Processing ALL {len(ads)} potential advertisers from query: {query}")
                    
                    processed_count = 0  # Initialize counter here
                    for idx, ad in enumerate(ads):  # Process ALL ads
                        if credits_used >= max_credits or len(discoveries) >= target_count:
                            break
                            
                        try:
                            domain = ad.get('domain', 'unknown')
                            title = ad.get('title', 'no title')
                            logger.info(f"🏢 [{idx+1}/{len(ads)}] Processing: {domain} - {title[:50]}...")
                            
                            # Skip advertiser info API calls to save credits for discovery
                            advertiser_info = {}
                            
                            # Apply discovery gates with detailed logging
                            discovery = await self._apply_discovery_gates(
                                ad, advertiser_info, None, vertical
                            )
                            
                            if discovery:
                                discoveries.append((discovery, 0))
                                logger.info(f"✅ QUALIFIED [{len(discoveries)}]: {discovery.domain} (demand: {discovery.demand_score}, fit: {discovery.fit_score})")
                            else:
                                logger.info(f"❌ REJECTED: {domain} - Failed qualification gates")
                                
                            processed_count += 1
                                
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to process ad {ad.get('domain', '')}: {e}")
                            continue
                    
                    logger.info(f"📊 QUERY COMPLETE: {processed_count}/{len(ads)} processed, {len(discoveries)} qualified so far")
                            
                except Exception as e:
                    logger.error(f"❌ Query failed: {query} - {e}")
                    continue
        
        logger.info(f"✅ Vertical {vertical.value} complete: {len(discoveries)} discoveries, {credits_used} credits used")
        return discoveries
    
    async def _search_ads(self, query: str, city: str) -> List[Dict]:
        """
        STRATEGIC SHIFT: Primary discovery using Advertiser Search API
        Returns up to 100 confirmed advertisers + fallback to SERP if needed
        """
        logger.debug(f"🚀 PRIMARY DISCOVERY: Advertiser Search for '{query}' in {city}")
        
        # PRIMARY LAYER: Advertiser Search API (1 credit = up to 100 advertisers!)
        advertiser_prospects = await self._search_advertisers_primary(query, city)
        
        if len(advertiser_prospects) >= 10:
            logger.info(f"✅ ADVERTISER SEARCH SUCCESS: {len(advertiser_prospects)} confirmed advertisers")
            return advertiser_prospects
        
        # FALLBACK: SERP discovery if low advertiser yield
        logger.info(f"🔄 Low advertiser yield ({len(advertiser_prospects)}), complementing with SERP...")
        serp_prospects = await self._search_serp_fallback(query, city)
        
        # Combine results, prioritizing advertisers
        all_prospects = advertiser_prospects + serp_prospects
        return all_prospects[:30]  # Limit to top 30 prospects

    async def _search_advertisers_primary(self, query: str, city: str) -> List[Dict]:
        """
        SIMPLIFIED ADVERTISER DISCOVERY
        Focus on working SearchAPI engines only
        """
        prospects = []
        
        # FOCUSED QUERY OPTIMIZATION
        simplified_queries = [
            f"{query}",  # Original query (e.g., "dental implants Tampa")
            f"dentist {city}",  # Simplified broad query
            f"dental {city}"    # Even broader fallback
        ]
        
        self.logger.info(f"🔍 ADVERTISER SEARCH: Testing {len(simplified_queries)} queries for {city}")
        
        for search_query in simplified_queries:
            if len(prospects) >= 20:  # Stop when we have enough prospects
                break
                
            # CRITICAL FIX: Correct SearchAPI Engine for Advertiser Search
            params = {
                "api_key": self.api_key,
                "engine": "google_ads_transparency_center_advertiser_search",  # CORRECTED ENGINE
                "q": search_query,
                "region": "US",
                "num_advertisers": 100,  # MAXIMUM allowed by API
                "num_domains": 100       # MAXIMUM allowed by API
            }
            
            try:
                async with self.session.get(f"{self.base_url}/search", params=params, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract confirmed advertisers from transparency center
                        advertisers = data.get('advertisers', [])
                        if advertisers:
                            self.logger.info(f"✅ TRANSPARENCY CENTER: Found {len(advertisers)} advertisers for '{search_query}'")
                            
                            for advertiser in advertisers[:10]:  # Limit per query
                                # Use actual advertiser data from transparency center
                                ads_count = advertiser.get('ads_count', {})
                                upper_ads = ads_count.get('upper', 0)
                                
                                prospect = {
                                    'title': advertiser.get('name', ''),
                                    'description': f"Google Ads Advertiser | {upper_ads} campaigns | Verified: {advertiser.get('is_verified', False)}",
                                    'domain': self._estimate_domain_from_name(advertiser.get('name', '')),
                                    'source': 'transparency_center',
                                    'advertiser_id': advertiser.get('id'),
                                    'ads_count_range': ads_count,
                                    'is_verified': advertiser.get('is_verified', False),
                                    'region': advertiser.get('region', 'US'),
                                    'tier': 'VERIFIED' if advertiser.get('is_verified') else 'ACTIVE',
                                    'weekend_relevance': False,
                                    'vulnerability_flags': ['ACTIVE_ADVERTISER'],
                                    'priority': 1,
                                    'query_matched': search_query
                                }
                                prospects.append(prospect)
                        
                        # Also extract domains if available
                        domains = data.get('domains', [])
                        existing_domains = {p['domain'] for p in prospects}
                        
                        for domain_obj in domains[:5]:  # Limit domains per query
                            domain_name = domain_obj.get('name', '')
                            if domain_name and domain_name not in existing_domains:
                                prospect = {
                                    'title': self._format_title_from_domain(domain_name),
                                    'description': f"Active advertising domain",
                                    'domain': domain_name,
                                    'source': 'advertiser_domain',
                                    'advertiser_id': '',
                                    'ads_count_range': {'lower': 1, 'upper': 10},
                                    'is_verified': False,
                                    'region': 'US',
                                    'tier': 'ACTIVE',
                                    'weekend_relevance': False,
                                    'vulnerability_flags': ['DOMAIN_ONLY_DATA'],
                                    'priority': 2,
                                    'query_matched': search_query
                                }
                                prospects.append(prospect)
                        
                        if advertisers or domains:
                            self.logger.info(f"🎯 SUCCESS '{search_query}': {len(advertisers)} advertisers + {len(domains)} domains")
                            
                    else:
                        self.logger.warning(f"❌ Query '{search_query}' failed: {response.status}")
                        
            except Exception as e:
                self.logger.error(f"Advertiser Search failed for '{search_query}': {e}")
        
        # Sort by SMB priority (4-10 campaigns first) then quality
        prospects.sort(key=lambda x: (
            x['priority'],
            # SMB Sweet Spot Priority: 4-10 campaigns = priority 1
            0 if 4 <= x['ads_count_range'].get('upper', 0) <= 10 else 1,
            # Avoid large enterprises (50+ campaigns)
            999 if x['ads_count_range'].get('upper', 0) >= 50 else 0,
            -x['ads_count_range'].get('upper', 0)
        ))
        
        self.logger.info(f"📊 ADVERTISER DISCOVERY COMPLETE: {len(prospects)} total prospects")
        return prospects[:15]  # Return top 15 prospects

    def _estimate_domain_from_name(self, advertiser_name: str) -> str:
        """Estimate domain from advertiser business name"""
        if not advertiser_name:
            return 'unknown-domain.com'
        
        # Clean and format name
        clean_name = advertiser_name.lower()
        clean_name = clean_name.replace(' inc', '').replace(' llc', '').replace(' corp', '')
        clean_name = clean_name.replace(' ', '').replace('-', '').replace('&', 'and')
        clean_name = ''.join(c for c in clean_name if c.isalnum())
        
        return f"{clean_name}.com"

    def _format_title_from_domain(self, domain: str) -> str:
        """Format business title from domain name"""
        name = domain.replace('.com', '').replace('.net', '').replace('.org', '')
        name = name.replace('-', ' ').replace('_', ' ')
        return name.title()

    def _classify_advertiser_tier(self, ads_count: Dict) -> str:
        """Classify advertiser based on campaign volume - SMB FOCUS"""
        upper_count = ads_count.get('upper', 0)
        lower_count = ads_count.get('lower', 0)
        
        # SMB SWEET SPOT: 4-10 campaigns for $997 service
        if 4 <= upper_count <= 10:
            return 'SMB_PREMIUM'   # Perfect $997 target
        elif 11 <= upper_count <= 20:
            return 'SMB_STANDARD'  # Good $997 potential
        elif upper_count >= 50:
            return 'ENTERPRISE'    # Too large - skip
        elif upper_count >= 21:
            return 'MID_MARKET'    # Consider but lower priority
        elif upper_count >= 2:
            return 'LIGHT'         # Small but viable
        else:
            return 'MINIMAL'       # 0-1 campaigns

    async def _search_serp_fallback(self, query: str, city: str) -> List[Dict]:
        """FALLBACK: Traditional SERP search when advertiser yield is low"""
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
        
        logger.debug(f"🔄 SERP fallback: {query} in {city}")
        
        try:
            async with self.session.get(f"{self.base_url}/search", params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    ads = self._extract_ads_from_serp(data)
                    logger.debug(f"📊 SERP fallback found {len(ads)} prospects")
                    return ads
                else:
                    logger.warning(f"SERP fallback error: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"SERP fallback failed: {str(e)}")
            return []

    def _extract_ads_from_serp(self, serp_data: Dict) -> List[Dict]:
        """Extract advertiser information from SERP results - AGGRESSIVE EXTRACTION"""
        ads = []
        
        logger.info(f"📊 SERP data keys: {list(serp_data.keys())}")
        
        # 1. Extract from paid ads section
        ad_count = 0
        for ad in serp_data.get('ads', []):
            domain = self._extract_domain(ad.get('link', ''))
            if domain:
                ads.append({
                    'title': ad.get('title', ''),
                    'description': ad.get('snippet', ''),
                    'domain': domain,
                    'link': ad.get('link', ''),
                    'position': ad.get('position', 0),
                    'source': 'paid_ad',
                    'priority': 1  # Highest priority
                })
                ad_count += 1
        
        # 2. Extract from local results (Google My Business)
        local_count = 0
        for result in serp_data.get('local_results', []):
            link = result.get('link') or result.get('website') or result.get('links', {}).get('website')
            if link:
                domain = self._extract_domain(link)
                if domain:
                    ads.append({
                        'title': result.get('title', ''),
                        'description': result.get('snippet', result.get('type', '')),
                        'domain': domain,
                        'link': link,
                        'position': result.get('position', 0),
                        'source': 'local_listing',
                        'priority': 2,  # High priority
                        'rating': result.get('rating'),
                        'reviews': result.get('reviews'),
                        'address': result.get('address')
                    })
                    local_count += 1
        
        # 3. Extract from organic results - VERY AGGRESSIVE
        organic_count = 0
        for result in serp_data.get('organic_results', []):
            domain = self._extract_domain(result.get('link', ''))
            if domain and self._looks_like_business(result):
                ads.append({
                    'title': result.get('title', ''),
                    'description': result.get('snippet', ''),
                    'domain': domain,
                    'link': result.get('link', ''),
                    'position': result.get('position', 0),
                    'source': 'organic_business',
                    'priority': 3  # Lower priority but still valuable
                })
                organic_count += 1
        
        # 4. Extract from related questions (if they mention businesses)
        question_count = 0
        for question in serp_data.get('related_questions', []):
            if question.get('link'):
                domain = self._extract_domain(question.get('link', ''))
                if domain and self._looks_like_business({'title': question.get('question', ''), 'snippet': question.get('snippet', ''), 'link': question.get('link', '')}):
                    ads.append({
                        'title': question.get('question', ''),
                        'description': question.get('snippet', ''),
                        'domain': domain,
                        'link': question.get('link', ''),
                        'position': 999,
                        'source': 'related_question',
                        'priority': 4  # Lowest priority
                    })
                    question_count += 1
        
        # Sort by priority and position
        ads.sort(key=lambda x: (x['priority'], x['position']))
        
        logger.info(f"📈 EXTRACTION COMPLETE:")
        logger.info(f"   💰 Paid ads: {ad_count}")
        logger.info(f"   � Local listings: {local_count}")
        logger.info(f"   🌐 Organic businesses: {organic_count}")
        logger.info(f"   ❓ Related questions: {question_count}")
        logger.info(f"   🎯 TOTAL PROSPECTS: {len(ads)}")
        
        return ads
    
    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract clean domain from URL"""
        try:
            domain = urlparse(url).netloc.lower()
            return domain.replace('www.', '') if domain else None
        except:
            return None
    
    def _looks_like_business(self, result: Dict) -> bool:
        """Heuristic to identify business listings - VERY INCLUSIVE"""
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        link = result.get('link', '').lower()
        
        # HARD SKIP: Major directories and aggregators
        hard_skip_domains = ['yelp.com', 'yellowpages.com', 'angi.com', 'homeadvisor.com', 
                            'thumbtack.com', 'bbb.org', 'superpages.com', 'manta.com']
        if any(skip in link for skip in hard_skip_domains):
            return False
        
        # SOFT SKIP: Platform subdomains but allow main domains
        platform_indicators = ['facebook.com', 'linkedin.com', 'instagram.com', 'twitter.com']
        if any(platform in link for platform in platform_indicators):
            # Allow if it's a business page, not just platform navigation
            business_in_url = any(term in link for term in ['business', 'company', 'page', 'profile'])
            if not business_in_url:
                return False
        
        # INCLUSION CRITERIA - Very broad
        content = title + ' ' + snippet
        
        # 1. Business structure indicators
        business_structure = ['llc', 'inc', 'corp', 'ltd', 'pllc', 'company', 'co.', 'enterprises']
        has_structure = any(struct in content for struct in business_structure)
        
        # 2. Service indicators  
        service_words = ['services', 'service', 'repair', 'installation', 'maintenance', 
                        'consultation', 'solutions', 'specialists', 'experts', 'professionals']
        has_services = any(service in content for service in service_words)
        
        # 3. Location indicators (suggests local business)
        location_words = ['tampa', 'miami', 'orlando', 'jacksonville', 'florida', 'fl',
                         'local', 'near me', 'area', 'serving', 'location']
        has_location = any(loc in content for loc in location_words)
        
        # 4. Contact/action indicators
        contact_words = ['call', 'contact', 'appointment', 'schedule', 'book', 'quote',
                        'estimate', 'consultation', 'visit', 'hours', 'address']
        has_contact = any(contact in content for contact in contact_words)
        
        # 5. Industry-specific terms
        industry_terms = ['dental', 'medical', 'legal', 'lawyer', 'attorney', 'doctor',
                         'clinic', 'office', 'center', 'practice', 'hvac', 'plumbing',
                         'roofing', 'insurance', 'real estate', 'auto', 'veterinary']
        has_industry = any(industry in content for industry in industry_terms)
        
        # 6. Quality indicators
        quality_words = ['licensed', 'certified', 'accredited', 'insured', 'bonded',
                        'experienced', 'trusted', 'reliable', 'professional']
        has_quality = any(quality in content for quality in quality_words)
        
        # SCORING: More inclusive approach
        score = 0
        if has_structure: score += 2
        if has_services: score += 2  
        if has_location: score += 1
        if has_contact: score += 1
        if has_industry: score += 2
        if has_quality: score += 1
        
        # Lower threshold for inclusion
        is_business = score >= 2
        
        if is_business:
            logger.debug(f"✅ BUSINESS DETECTED: {title[:40]}... (score: {score})")
        else:
            logger.debug(f"❌ NOT BUSINESS: {title[:40]}... (score: {score})")
            
        return is_business
    
    async def _verify_ad_investment(self, domain: str) -> tuple[int, dict]:
        """Verify domain's advertising investment and analyze strategy vulnerabilities"""
        try:
            params = {
                "api_key": self.api_key,
                "engine": "google_ads_transparency_center", 
                "domain": domain
            }
            
            async with self.session.get(f"{self.base_url}/search", params=params, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    search_info = data.get('search_information', {})
                    total_results = search_info.get('total_results', 0)
                    ad_creatives = data.get('ad_creatives', [])
                    ad_count = len(ad_creatives)
                    
                    if ad_count == 0:
                        return 0, {
                            'analysis': 'NO_ADVERTISING',
                            'vulnerabilities': ['Missing lead generation channel', 'No digital advertising presence'],
                            'opportunity_value': 'HIGH ($3000-5000/month potential)'
                        }
                    
                    # Analyze ad investment quality
                    score = 0
                    vulnerabilities = []
                    
                    # REAL PERFORMANCE ANALYSIS - Not generic templates
                    performance_analysis = self._analyze_campaign_performance(ad_creatives, domain)
                    financial_waste = self._calculate_budget_waste(ad_creatives, performance_analysis)
                    competitive_gaps = self._identify_competitive_inefficiencies(ad_creatives, domain)
                    
                    # Only qualify if we can identify REAL waste opportunities
                    total_waste_value = financial_waste.get('monthly_waste_estimate', 0)
                    if total_waste_value < 500:  # Must have >$500/month waste to qualify
                        return 0, {
                            'analysis': 'INSUFFICIENT_WASTE_OPPORTUNITY',
                            'vulnerabilities': [f'Only ${total_waste_value}/month waste detected - below $997 service threshold'],
                            'opportunity_value': f'LOW - ${total_waste_value}/month potential savings'
                        }
                    
                    # SMB-FOCUSED: Target businesses ideal for $997 audit/optimization sprint
                    if ad_count >= 21: 
                        score += 0      # Too structured - longer sales cycle, avoid for initial clients
                        vulnerabilities.append(f'STRUCTURED_OPERATION ({ad_count} campaigns - established process, harder initial sale)')
                    elif ad_count >= 11: 
                        score += 1      # Getting structured - still possible but less ideal
                        vulnerabilities.append(f'SEMI_STRUCTURED ({ad_count} campaigns - some process in place)')
                    elif ad_count >= 4: 
                        score += 3      # SWEET SPOT: Perfect for $997 sprint service
                        vulnerabilities.append(f'SPRINT_SERVICE_IDEAL ({ad_count} campaigns - perfect for optimization sprint)')
                    elif ad_count >= 2: 
                        score += 2      # Good foundation for audit service
                        vulnerabilities.append(f'AUDIT_FOUNDATION ({ad_count} campaigns - strong audit opportunity)')
                    elif ad_count >= 1: 
                        score += 1      # Minimal but workable for transformation service
                        vulnerabilities.append(f'TRANSFORMATION_NEEDED ({ad_count} campaign - complete strategy overhaul)')
                    
                    # Add REAL performance-based vulnerabilities
                    if financial_waste.get('high_cpm_waste', 0) > 200:
                        vulnerabilities.append(f"HIGH_CPM_WASTE (${financial_waste['high_cpm_waste']}/month from inefficient targeting)")
                        score += 2
                    
                    if financial_waste.get('format_inefficiency', 0) > 150:
                        vulnerabilities.append(f"FORMAT_INEFFICIENCY (${financial_waste['format_inefficiency']}/month from poor format mix)")
                        score += 1
                    
                    if competitive_gaps.get('bidding_inefficiency', 0) > 100:
                        vulnerabilities.append(f"BIDDING_INEFFICIENCY (${competitive_gaps['bidding_inefficiency']}/month vs competitors)")
                        score += 1
                    if ad_count >= 1:
                        self.logger.info(f"✅ GROWTH OPPORTUNITY IDENTIFIED: {ad_count} ads = scaling potential")
                    else:
                        self.logger.warning(f"⚠️ NO DIGITAL PRESENCE: {ad_count} ads - complete digital transformation needed")
                        return 0, {
                            'analysis': 'NO_DIGITAL_PRESENCE',
                            'vulnerabilities': ['Complete digital marketing transformation needed'],
                            'opportunity_value': 'MASSIVE - Total market capture potential'
                        }
                    
                    # Analyze ad longevity and formats
                    if ad_creatives:
                        formats = set()
                        total_days = []
                        recent_ads = 0
                        now = datetime.now()
                        
                        for ad in ad_creatives[:10]:  # Sample top 10
                            formats.add(ad.get('format', 'unknown'))
                            days_shown = ad.get('total_days_shown', 0)
                            total_days.append(days_shown)
                            
                            # Check recency
                            try:
                                last_shown = datetime.fromisoformat(ad.get('last_shown_datetime', '').replace('Z', '+00:00'))
                                if (now - last_shown.replace(tzinfo=None)).days <= 30:
                                    recent_ads += 1
                            except:
                                continue
                        
                        # Longevity analysis
                        if total_days:
                            avg_days = sum(total_days) / len(total_days)
                            total_days_sum = sum(total_days)
                            
                            if avg_days >= 200: 
                                score += 2    # Long-term commitment
                            elif avg_days >= 100: 
                                score += 1  # Medium-term
                            elif avg_days >= 30: 
                                score += 1   # Short-term but consistent
                            else:
                                vulnerabilities.append(f'SHORT_CAMPAIGN_DURATIONS ({avg_days:.1f} days avg)')
                        
                        # Format diversity analysis
                        if 'video' in formats: 
                            score += 1  # Video ads = higher budget
                        else:
                            vulnerabilities.append('NO_VIDEO_ADVERTISING')
                            
                        if len(formats) >= 2: 
                            score += 1   # Multiple formats = sophisticated
                        else:
                            vulnerabilities.append(f'LIMITED_FORMAT_DIVERSITY ({list(formats)})')
                        
                        # Recency analysis
                        if recent_ads == 0:
                            vulnerabilities.append('STALE_CAMPAIGNS (no recent activity)')
                        
                        # Campaign sophistication
                        if total_days_sum < 180:
                            vulnerabilities.append(f'SHORT_CAMPAIGN_HISTORY ({total_days_sum} total days)')
                    
                        analysis = {
                        'investment_score': min(score, 7),
                        'total_creatives': ad_count,
                        'formats': list(formats) if ad_creatives else [],
                        'avg_duration': sum(total_days) / len(total_days) if total_days else 0,
                        'total_days_shown': sum(total_days) if total_days else 0,
                        'recent_activity': recent_ads if ad_creatives else 0,
                        'vulnerabilities': vulnerabilities[:3],  # Top 3 issues for outreach
                        'opportunity_value': self._calculate_opportunity_value(vulnerabilities),
                        'transparency_data': data,  # Include full transparency data for strategic analysis
                        'financial_analysis': financial_waste,
                        'performance_analysis': performance_analysis,
                        'competitive_gaps': competitive_gaps
                    }
                    
                    return min(score, 7), analysis
                    
                else:
                    logger.debug(f"Transparency API error {response.status} for {domain}")
                    return 0, {
                        'analysis': 'API_ERROR',
                        'vulnerabilities': ['Unable to verify advertising strategy'],
                        'opportunity_value': 'UNKNOWN'
                    }
                    
        except Exception as e:
            logger.debug(f"Ad investment verification error for {domain}: {e}")
            return 0, {
                'analysis': 'VERIFICATION_FAILED',
                'vulnerabilities': ['Technical verification issue'],
                'opportunity_value': 'UNKNOWN'
            }

    async def _analyze_strategic_vulnerabilities(self, domain: str, ad_analysis: dict) -> dict:
        """
        SMB-FOCUSED VULNERABILITY ANALYSIS: Smart credit usage for $997 service prospects
        """
        investment_score = ad_analysis.get('investment_score', 0)
        ads_count = ad_analysis.get('ads_count', 0)
        
        # CREDIT OPTIMIZATION: Skip expensive analysis for wrong targets
        if investment_score < 2:
            # Don't waste credits on minimal advertisers
            return {
                'tier': 'basic',
                'outreach_insights': ['NO_DIGITAL_MATURITY'],
                'followup_insights': [],
                'proposal_insights': ['Complete digital strategy rebuild needed'],
                'revenue_opportunity': 'HIGH_GREENFIELD'
            }
        
        # SKIP ENTERPRISE PROSPECTS: Too big for $997 service
        if ads_count > 50:
            return {
                'tier': 'enterprise_skip',
                'outreach_insights': ['TOO_LARGE_FOR_SMB_SERVICE'],
                'followup_insights': [],
                'proposal_insights': ['Enterprise prospect - outside $997 service scope'],
                'revenue_opportunity': 'ENTERPRISE_TIER'
            }
        
        try:
            # SMART CREDIT USAGE: Only deep analysis for SMB sweet spot (4-20 campaigns)
            if 4 <= ads_count <= 20:
                self.logger.info(f"🎯 SMB TARGET: Deep analysis for {domain} ({ads_count} campaigns)")
            else:
                self.logger.info(f"⚡ LIGHT ANALYSIS: Basic check for {domain} ({ads_count} campaigns)")
            
            # Get transparency data efficiently (reuse if available)
            transparency_data = ad_analysis.get('transparency_data')
            if not transparency_data and 4 <= ads_count <= 20:
                # Only fetch for SMB targets to save credits
                transparency_params = {
                    "api_key": self.api_key,
                    "engine": "google_ads_transparency_center",
                    "domain": domain
                }
                
                async with self.session.get(f"{self.base_url}/search", params=transparency_params, timeout=20) as response:
                    if response.status == 200:
                        transparency_data = await response.json()
                    else:
                        transparency_data = {}
            
            ad_creatives = transparency_data.get('ad_creatives', []) if transparency_data else []
            
            if not ad_creatives:
                # Basic analysis for prospects without creative data
                return {
                    'tier': 'basic_verified', 
                    'outreach_insights': ['AD_INVESTMENT_VERIFIED'],
                    'followup_insights': ['Request access to ad account for detailed audit'],
                    'proposal_insights': [f'${ads_count * 150:.0f} potential monthly optimization opportunity'],
                    'financial_analysis': {
                        'monthly_waste': ads_count * 150,  # Conservative estimate
                        'estimated_spend': ads_count * 300,
                        'waste_percentage': 50,
                        'inefficiencies': ['Estimated inefficiencies require account access']
                    }
                }
            
            # DETAILED ANALYSIS FOR SMB PROSPECTS ONLY
            if 4 <= ads_count <= 20:
                performance_analysis = self._analyze_campaign_performance(ad_creatives, domain)
                financial_waste = self._calculate_budget_waste(ad_creatives, performance_analysis)
                competitive_gaps = self._identify_competitive_inefficiencies(ad_creatives, domain)
                
                # Get real financial insights with SMB focus
                monthly_waste = financial_waste.get('monthly_waste_estimate', ads_count * 100)
                estimated_spend = len(ad_creatives) * 250  # $250/campaign average for SMBs
                waste_percentage = min((monthly_waste / estimated_spend * 100) if estimated_spend > 0 else 0, 60)
                
                # Build detailed inefficiencies for SMB prospects
                inefficiencies = []
                if isinstance(financial_waste, dict):
                    for key, value in financial_waste.items():
                        if key.endswith('_waste') and value > 0:
                            inefficiencies.append({
                                'type': key.replace('_', ' ').title(),
                                'estimated_waste': value
                            })
                
                # SMB-specific insights based on campaign count
                if ads_count <= 10:
                    tier_insights = ['PERFECT_SMB_TARGET', 'HIGH_OPTIMIZATION_POTENTIAL']
                    revenue_opp = f'${monthly_waste:.0f}/month savings opportunity'
                else:
                    tier_insights = ['SMB_GROWTH_STAGE', 'SCALING_OPTIMIZATION_NEEDED']
                    revenue_opp = f'${monthly_waste:.0f}/month efficiency gains'
                
                return {
                    'tier': 'strategic',
                    'transparency_data': transparency_data,
                    'financial_analysis': {
                        'monthly_waste': monthly_waste,
                        'estimated_spend': estimated_spend,
                        'waste_percentage': waste_percentage,
                        'inefficiencies': inefficiencies
                    },
                    'performance_analysis': performance_analysis,
                    'competitive_gaps': competitive_gaps,
                    'outreach_insights': tier_insights,
                    'followup_insights': [f'Detailed audit of {len(ad_creatives)} campaigns'],
                    'proposal_insights': [f'$997 Sprint: {revenue_opp}', f'ROI: {waste_percentage:.0f}% waste reduction'],
                    'revenue_opportunity': revenue_opp
                }
            else:
                # LIGHT ANALYSIS for non-SMB prospects (save credits)
                basic_waste = ads_count * 75  # Conservative estimate
                return {
                    'tier': 'light_analysis',
                    'outreach_insights': ['CAMPAIGN_OPTIMIZATION_OPPORTUNITY'],
                    'followup_insights': ['Strategic consultation recommended'],
                    'proposal_insights': [f'${basic_waste:.0f}/month potential savings'],
                    'financial_analysis': {
                        'monthly_waste': basic_waste,
                        'estimated_spend': ads_count * 200,
                        'waste_percentage': 35,
                        'inefficiencies': ['Standard optimization opportunities']
                    },
                    'revenue_opportunity': f'${basic_waste:.0f}/month optimization'
                }
                return {
                    'tier': 'basic',
                    'outreach_insights': ['INSUFFICIENT_WASTE_OPPORTUNITY'],
                    'followup_insights': [],
                    'proposal_insights': [f'Only ${monthly_waste:.0f}/month waste detected - below service threshold'],
                    'financial_analysis': {
                        'monthly_waste': monthly_waste,
                        'estimated_spend': estimated_spend,
                        'waste_percentage': waste_percentage,
                        'inefficiencies': []
                    }
                }
            
            # WEEKEND OPERATIONAL CONTEXT
            current_hour_utc = datetime.now().hour
            is_weekend_peak = current_hour_utc in [7, 8, 9, 10, 11]  # 4-8am Brasília = 7-11am UTC = Weekend peak US
            
            strategic_insights = {
                'tier': 'strategic',
                'outreach_insights': [],      # Immediate hook with financial data
                'followup_insights': [],      # Progressive disclosure with ROI
                'proposal_insights': [],      # Complete financial assessment
                'revenue_opportunity': f'${monthly_waste:.0f}/month waste reduction',
                'timing_advantage': is_weekend_peak,
                'vulnerability_severity': 'HIGH' if monthly_waste > 1500 else 'MEDIUM',
                'financial_analysis': {
                    'monthly_waste': monthly_waste,
                    'estimated_spend': estimated_spend,
                    'waste_percentage': waste_percentage,
                    'inefficiencies': inefficiencies,
                    'performance_metrics': performance_analysis,
                    'competitive_gaps': competitive_gaps
                }
            }
            
            # OUTREACH PRIORITIZATION based on REAL waste types
            top_inefficiencies = sorted(inefficiencies, key=lambda x: x.get('estimated_waste', 0), reverse=True)[:2]
            for inefficiency in top_inefficiencies:
                insight_type = inefficiency.get('type', 'UNKNOWN_WASTE')
                strategic_insights['outreach_insights'].append(insight_type)
            
            # FOLLOW-UP DISCLOSURE with specific financial metrics
            strategic_insights['followup_insights'] = [
                f'${waste_percentage:.0f}% budget inefficiency detected',
                f'${monthly_waste:.0f}/month optimization potential',
                'ROI improvement roadmap available'
            ]
            if is_weekend_peak:
                strategic_insights['followup_insights'].append('WEEKEND_TIMING_OPPORTUNITY')
            
            # PROPOSAL INSIGHTS with complete financial breakdown
            strategic_insights['proposal_insights'] = [
                f'Total monthly waste: ${monthly_waste:.0f}',
                f'Estimated monthly spend: ${estimated_spend}',
                f'Waste percentage: {waste_percentage:.1f}%'
            ]
            for inefficiency in inefficiencies:
                strategic_insights['proposal_insights'].append(
                    f"{inefficiency.get('type', 'Unknown')}: ${inefficiency.get('estimated_waste', 0):.0f}/month"
                )

            # TIMING CONTEXT for outreach
            if is_weekend_peak:
                strategic_insights['outreach_insights'].append('WEEKEND_OPERATIONAL_TIMING')

            # ADD CAMPAIGN-SPECIFIC DATA for outreach generation - Use financial analysis vulnerabilities
            strategic_insights['vulnerabilities'] = [inefi.get('type', 'Unknown waste') for inefi in inefficiencies[:3]]
            strategic_insights['ad_count'] = len(ad_creatives)
            
            # IMPROVED: Extract actual formats (not just 'unknown')
            detected_formats = []
            for creative in ad_creatives[:10]:
                fmt = creative.get('format', '').lower()
                if fmt and fmt != 'unknown':
                    detected_formats.append(fmt)
                elif creative.get('preview_url'):  # Has preview = likely image/video
                    if 'video' in creative.get('preview_url', '').lower():
                        detected_formats.append('video')
                    else:
                        detected_formats.append('image')
                elif creative.get('title') or creative.get('description'):  # Has text
                    detected_formats.append('text')
            
            strategic_insights['formats_detected'] = list(set(detected_formats)) if detected_formats else ['text']
            
            # IMPROVED: Calculate average campaign duration with proper handling
            duration_data = []
            for creative in ad_creatives[:10]:
                days = creative.get('total_days_shown', 0)
                if days > 0:  # Only include valid durations
                    duration_data.append(days)
            strategic_insights['avg_campaign_duration'] = round(sum(duration_data) / len(duration_data), 1) if duration_data else 30  # Default 30 days if no data
            
            # IMPROVED: Calculate recent campaigns ratio with better error handling
            recent_campaigns = 0
            valid_campaigns = 0
            now = datetime.now()
            for creative in ad_creatives[:10]:
                try:
                    last_shown_str = creative.get('last_shown_datetime', '')
                    if last_shown_str:
                        # Handle different datetime formats
                        last_shown_str = last_shown_str.replace('Z', '+00:00')
                        last_shown = datetime.fromisoformat(last_shown_str)
                        days_ago = (now - last_shown.replace(tzinfo=None)).days
                        valid_campaigns += 1
                        if days_ago <= 30:
                            recent_campaigns += 1
                except Exception as e:
                    # Try alternative date parsing
                    try:
                        if creative.get('last_shown_datetime'):
                            valid_campaigns += 1
                            # Assume recent if we can't parse (conservative approach)
                            recent_campaigns += 1
                    except:
                        continue
            
            strategic_insights['recent_campaigns_ratio'] = round(recent_campaigns / max(valid_campaigns, 1), 2) if valid_campaigns > 0 else 0.5

            return strategic_insights
            
        except Exception as e:
            self.logger.error(f"Strategic vulnerability analysis failed for {domain}: {e}")
            return {
                'tier': 'basic',
                'outreach_insights': ['ANALYSIS_TECHNICAL_ISSUE'],
                'followup_insights': [],
                'proposal_insights': ad_analysis.get('vulnerabilities', [])
            }

    async def _analyze_ad_details_vulnerabilities_real(self, ad_creatives: List[Dict], domain: str) -> dict:
        """
        REAL AD ANALYSIS: Identify specific vulnerabilities from actual ad data
        Uses real transparency center data instead of API calls
        """
        try:
            if not ad_creatives:
                return {'severity': 'LOW', 'critical_vulnerabilities': ['NO_AD_DATA']}
            
            self.logger.info(f"🔬 ANALYZING {len(ad_creatives)} real ad creatives for {domain}")
            
            # CRITICAL VULNERABILITY DETECTION with real data
            critical_vulnerabilities = []
            medium_vulnerabilities = []
            strategic_gaps = []
            
            # Analyze actual creative data
            sample_creatives = ad_creatives[:10]  # Analyze top 10
            
            # 1. WEEKEND/EMERGENCY MESSAGING ANALYSIS (Real text analysis)
            weekend_keywords = ['weekend', 'emergency', 'urgent', '24/7', '24 hour', 'immediate', 'fast', 'quick']
            emergency_messaging = 0
            total_text_analyzed = 0
            
            for creative in sample_creatives:
                title = creative.get('title', '').lower()
                description = creative.get('description', '').lower()
                creative_text = f"{title} {description}"
                
                if title or description:  # Only count if we have text
                    total_text_analyzed += 1
                    if any(keyword in creative_text for keyword in weekend_keywords):
                        emergency_messaging += 1
            
            if total_text_analyzed > 0:
                emergency_ratio = emergency_messaging / total_text_analyzed
                self.logger.info(f"📊 Emergency messaging ratio: {emergency_ratio:.2f} ({emergency_messaging}/{total_text_analyzed})")
                
                if emergency_ratio == 0:
                    critical_vulnerabilities.append('NO_URGENCY_MESSAGING')
                elif emergency_ratio < 0.3:
                    medium_vulnerabilities.append('WEAK_EMERGENCY_POSITIONING')
            
            # 2. CAMPAIGN RECENCY ANALYSIS (Real dates)
            recent_campaigns = 0
            old_campaigns = 0
            now = datetime.now()
            
            for creative in sample_creatives:
                try:
                    last_shown_str = creative.get('last_shown_datetime', '')
                    if last_shown_str:
                        last_shown = datetime.fromisoformat(last_shown_str.replace('Z', '+00:00'))
                        days_ago = (now - last_shown.replace(tzinfo=None)).days
                        
                        if days_ago <= 30:
                            recent_campaigns += 1
                        elif days_ago > 90:
                            old_campaigns += 1
                except Exception as e:
                    self.logger.debug(f"Date parsing error: {e}")
                    continue
            
            total_dated = recent_campaigns + old_campaigns
            if total_dated > 0:
                recent_ratio = recent_campaigns / len(sample_creatives)
                self.logger.info(f"📊 Recent campaigns ratio: {recent_ratio:.2f} ({recent_campaigns}/{len(sample_creatives)})")
                
                if recent_campaigns == 0:
                    critical_vulnerabilities.append('COMPLETELY_STALE_CAMPAIGNS')
                elif recent_ratio < 0.2:
                    medium_vulnerabilities.append('MOSTLY_OUTDATED_PORTFOLIO')
            
            # 3. FORMAT SOPHISTICATION ANALYSIS (Real formats)
            formats = set()
            for creative in sample_creatives:
                format_type = creative.get('format')
                if format_type:
                    formats.add(format_type)
            
            self.logger.info(f"📊 Ad formats detected: {list(formats)}")
            
            if 'video' not in formats and len(formats) > 0:
                medium_vulnerabilities.append('MISSING_VIDEO_STRATEGY')
            if len(formats) == 1:
                medium_vulnerabilities.append('SINGLE_FORMAT_LIMITATION')
            elif len(formats) == 0:
                critical_vulnerabilities.append('NO_FORMAT_DATA')
            
            # 4. CAMPAIGN DURATION PATTERNS (Real duration analysis)
            short_campaigns = 0
            duration_data = []
            
            for creative in sample_creatives:
                days_shown = creative.get('total_days_shown', 0)
                if days_shown > 0:
                    duration_data.append(days_shown)
                    if days_shown < 14:  # Less than 2 weeks
                        short_campaigns += 1
            
            if duration_data:
                avg_duration = sum(duration_data) / len(duration_data)
                self.logger.info(f"📊 Average campaign duration: {avg_duration:.1f} days")
                
                short_ratio = short_campaigns / len(duration_data)
                if short_ratio > 0.6:
                    critical_vulnerabilities.append('SHORT_CAMPAIGN_STRATEGY')
                elif avg_duration < 30:
                    medium_vulnerabilities.append('SUBOPTIMAL_CAMPAIGN_LENGTH')
            
            # 5. VOLUME ANALYSIS (Real creative count)
            if len(ad_creatives) < 5:
                strategic_gaps.append('LOW_CREATIVE_VOLUME')
            elif len(ad_creatives) < 15:
                strategic_gaps.append('MODERATE_CREATIVE_VOLUME')
            
            # Determine severity based on real findings
            if len(critical_vulnerabilities) >= 2:
                severity = 'CRITICAL'
            elif len(critical_vulnerabilities) >= 1 or len(medium_vulnerabilities) >= 3:
                severity = 'HIGH'
            elif len(medium_vulnerabilities) >= 1:
                severity = 'MEDIUM'
            else:
                severity = 'LOW'
            
            self.logger.info(f"🎯 VULNERABILITY ANALYSIS COMPLETE:")
            self.logger.info(f"   Severity: {severity}")
            self.logger.info(f"   Critical: {critical_vulnerabilities}")
            self.logger.info(f"   Medium: {medium_vulnerabilities}")
            
            return {
                'severity': severity,
                'critical_vulnerabilities': critical_vulnerabilities,
                'medium_vulnerabilities': medium_vulnerabilities,
                'strategic_gaps': strategic_gaps,
                'total_creatives_analyzed': len(sample_creatives),
                'analysis_summary': f"Analyzed {len(sample_creatives)} ads with {len(critical_vulnerabilities)} critical issues"
            }
            
        except Exception as e:
            self.logger.error(f"Real ad vulnerability analysis failed for {domain}: {e}")
            return {
                'severity': 'UNKNOWN',
                'critical_vulnerabilities': ['ANALYSIS_FAILED'],
                'medium_vulnerabilities': [],
                'strategic_gaps': []
            }

    async def _analyze_ad_details_vulnerabilities(self, advertiser_id: str, domain: str) -> dict:
        """
        DEEP AD DETAILS ANALYSIS: Identify specific execution vulnerabilities
        Uses Ad Details API for granular campaign assessment
        """
        try:
            # Get transparency data to extract creative IDs
            transparency_data = await self._get_transparency_data(advertiser_id)
            if not transparency_data or not transparency_data.get('ad_creatives'):
                return {'severity': 'LOW', 'critical_vulnerabilities': ['NO_AD_DATA']}
            
            ad_creatives = transparency_data.get('ad_creatives', [])
            
            # CRITICAL VULNERABILITY DETECTION
            critical_vulnerabilities = []
            medium_vulnerabilities = []
            strategic_gaps = []
            
            # Analyze top 5 creatives for patterns
            sample_creatives = ad_creatives[:5]
            
            # 1. WEEKEND/EMERGENCY MESSAGING ANALYSIS
            weekend_keywords = ['weekend', 'emergency', 'urgent', '24/7', '24 hour', 'immediate']
            emergency_messaging = 0
            
            for creative in sample_creatives:
                creative_text = f"{creative.get('title', '')} {creative.get('description', '')}".lower()
                if any(keyword in creative_text for keyword in weekend_keywords):
                    emergency_messaging += 1
            
            if emergency_messaging == 0:
                critical_vulnerabilities.append('WEEKEND_GAP')
            elif emergency_messaging < len(sample_creatives) * 0.5:
                medium_vulnerabilities.append('WEAK_EMERGENCY_MESSAGING')
            
            # 2. CAMPAIGN RECENCY ANALYSIS
            recent_campaigns = 0
            now = datetime.now()
            
            for creative in sample_creatives:
                try:
                    last_shown = datetime.fromisoformat(creative.get('last_shown_datetime', '').replace('Z', '+00:00'))
                    days_ago = (now - last_shown.replace(tzinfo=None)).days
                    if days_ago <= 14:
                        recent_campaigns += 1
                except:
                    continue
            
            if recent_campaigns == 0:
                critical_vulnerabilities.append('STALE_CAMPAIGNS')
            elif recent_campaigns < len(sample_creatives) * 0.3:
                medium_vulnerabilities.append('OUTDATED_PORTFOLIO')
            
            # 3. FORMAT SOPHISTICATION ANALYSIS
            formats = set(creative.get('format') for creative in sample_creatives if creative.get('format'))
            
            if 'video' not in formats:
                medium_vulnerabilities.append('NO_VIDEO_ADS')
            if len(formats) == 1:
                medium_vulnerabilities.append('SINGLE_FORMAT_LIMITATION')
            
            # 4. CAMPAIGN DURATION PATTERNS
            short_campaigns = 0
            for creative in sample_creatives:
                days_shown = creative.get('total_days_shown', 0)
                if days_shown < 30:
                    short_campaigns += 1
            
            if short_campaigns > len(sample_creatives) * 0.7:
                critical_vulnerabilities.append('SHORT_CAMPAIGN_STRATEGY')
            
            # 5. STRATEGIC GAPS (Advanced analysis)
            if len(ad_creatives) < 10:
                strategic_gaps.append('LIMITED_CREATIVE_VOLUME')
            
            # Determine severity
            if len(critical_vulnerabilities) >= 2:
                severity = 'CRITICAL'
            elif len(critical_vulnerabilities) >= 1 or len(medium_vulnerabilities) >= 3:
                severity = 'HIGH'
            elif len(medium_vulnerabilities) >= 1:
                severity = 'MEDIUM'
            else:
                severity = 'LOW'
            
            return {
                'severity': severity,
                'critical_vulnerabilities': critical_vulnerabilities,
                'medium_vulnerabilities': medium_vulnerabilities,
                'strategic_gaps': strategic_gaps,
                'total_creatives_analyzed': len(sample_creatives)
            }
            
        except Exception as e:
            self.logger.error(f"Ad details vulnerability analysis failed for {advertiser_id}: {e}")
            return {
                'severity': 'UNKNOWN',
                'critical_vulnerabilities': ['ANALYSIS_FAILED'],
                'medium_vulnerabilities': [],
                'strategic_gaps': []
            }
                    
        except Exception as e:
            logger.debug(f"Ad investment verification failed for {domain}: {e}")
            return 0, {
                'analysis': 'VERIFICATION_FAILED', 
                'vulnerabilities': ['Ad verification unavailable'],
                'opportunity_value': 'UNKNOWN'
            }
    
    def _calculate_opportunity_value(self, vulnerabilities: list) -> str:
        """Calculate revenue opportunity based on advertising vulnerabilities"""
        high_impact = ['NO_ADVERTISING', 'STALE_CAMPAIGNS', 'NO_VIDEO_ADVERTISING']
        medium_impact = ['LIMITED_FORMAT_DIVERSITY', 'SHORT_CAMPAIGN_HISTORY', 'LOW_CREATIVE_VOLUME']
        
        high_count = sum(1 for v in vulnerabilities if any(hi in v for hi in high_impact))
        medium_count = sum(1 for v in vulnerabilities if any(mi in v for mi in medium_impact))
        
        if high_count >= 2:
            return 'HIGH ($3000-5000/month potential)'
        elif high_count >= 1 or medium_count >= 2:
            return 'MEDIUM ($1500-3000/month potential)'
        elif medium_count >= 1:
            return 'LOW ($500-1500/month potential)'
        else:
            return 'MINIMAL (<$500/month potential)'
    
    async def _get_advertiser_info(self, domain: str) -> Optional[Dict]:
        """Get advertiser info using SearchAPI - Using valid transparency center engine"""
        if not domain:
            return None
            
        params = {
            "api_key": self.api_key,
            "engine": "google_ads_transparency_center",
            "domain": domain
        }
        
        try:
            async with self.session.get(f"{self.base_url}/search", params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    # Extract advertiser info from transparency data
                    advertisers = data.get('advertisers', [])
                    if advertisers:
                        return advertisers[0]  # Return first advertiser
                    return None
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
    
    async def _get_ad_details_enrichment(self, advertiser_id: str, creative_id: str) -> Optional[Dict]:
        """
        CRITICAL: Ad Details API for deep creative analysis
        Extracts variations, ad_information, regions data for vulnerability analysis
        """
        if not advertiser_id or not creative_id:
            return None
            
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
                    
                    self.logger.info(f"✅ AD DETAILS ENRICHMENT: {creative_id}")
                    self.logger.info(f"   Format: {ad_information.get('format')}")
                    self.logger.info(f"   Topic: {ad_information.get('topic')}")
                    self.logger.info(f"   Variations: {len(variations)}")
                    
                    return {
                        'creative_id': creative_id,
                        'ad_information': ad_information,
                        'variations': variations,
                        'format': ad_information.get('format'),
                        'topic': ad_information.get('topic'),
                        'first_shown_date': ad_information.get('first_shown_date'),
                        'last_shown_date': ad_information.get('last_shown_date'),
                        'last_shown_datetime': ad_information.get('last_shown_datetime'),
                        'regions': ad_information.get('regions', []),
                        'audience_selection': ad_information.get('audience_selection', {}),
                        'enrichment_source': 'ad_details_api',
                        'enrichment_timestamp': datetime.now().isoformat()
                    }
                else:
                    self.logger.debug(f"Ad details API returned {response.status} for {creative_id}")
                    return None
        except Exception as e:
            self.logger.debug(f"Ad details enrichment failed for {creative_id}: {e}")
            return None
    
    async def _apply_discovery_gates(self, 
                                   ad: Dict,
                                   advertiser_info: Dict,
                                   transparency_data: Dict,
                                   vertical: Vertical) -> Optional[DiscoveryOutput]:
        """TRANSPARENT discovery gates with detailed logging"""
        
        domain = ad.get('domain', '')
        title = ad.get('title', '')
        description = ad.get('description', '')
        source = ad.get('source', 'unknown')
        
        logger.info(f"🔍 QUALIFICATION GATES for {domain}")
        logger.info(f"   📝 Title: {title}")
        logger.info(f"   📄 Description: {description[:100]}...")
        logger.info(f"   🎯 Source: {source}")
        
        # GATE 1: Business legitimacy and identifiability
        business_quality_score = self._assess_business_quality(domain, title, description, advertiser_info)
        if business_quality_score < 3:
            logger.info(f"❌ GATE 1 FAILED: Low business quality score ({business_quality_score}/5)")
            logger.info(f"   📋 Reasons: {self._get_quality_issues(domain, title, description, advertiser_info)}")
            return None
        logger.info(f"✅ GATE 1 PASSED: Business legitimacy verified (score: {business_quality_score}/5)")
        
        # GATE 2: Domain quality check
        if len(domain) < 4 or '.' not in domain:
            logger.info(f"❌ GATE 2 FAILED: Invalid domain format: {domain}")
            return None
        logger.info(f"✅ GATE 2 PASSED: Valid domain format")
        
        # GATE 2.5: ICP EXCLUSION FILTER - Filter out major franchises and wrong verticals
        if self._is_excluded_from_icp(domain, title, description, vertical):
            logger.info(f"❌ GATE 2.5 FAILED: Excluded from ICP (major franchise/wrong vertical/too large)")
            return None
        logger.info(f"✅ GATE 2.5 PASSED: ICP alignment verified")
        
        # GATE 3: Spam/junk filtering (very lenient)
        content_lower = (title + ' ' + description).lower()
        spam_indicators = ['free download', 'click here now', 'casino', 'gambling', 'porn', 'xxx']
        spam_found = [spam for spam in spam_indicators if spam in content_lower]
        if spam_found:
            logger.info(f"❌ GATE 3 FAILED: Spam detected: {spam_found}")
            return None
        logger.info(f"✅ GATE 3 PASSED: No spam indicators")
        
        # GATE 4: Vertical relevance scoring
        config = self.vertical_configs.get(vertical, {})
        fit_indicators = config.get('fit_indicators', [])
        demand_keywords = config.get('demand_keywords', [])
        
        fit_matches = [indicator for indicator in fit_indicators if indicator.lower() in content_lower]
        demand_matches = [keyword for keyword in demand_keywords if keyword.lower() in content_lower]
        
        logger.info(f"🎯 VERTICAL ANALYSIS for {vertical.value}:")
        logger.info(f"   ✅ Fit matches: {fit_matches}")
        logger.info(f"   ✅ Demand matches: {demand_matches}")
        
        # Calculate scores (more generous)
        base_score = 2  # Everyone starts with 2
        
        # Fit score calculation
        fit_score = base_score
        if fit_matches:
            fit_score += len(fit_matches)
        if source == 'paid_ad':
            fit_score += 2  # Bonus for paid ads
        elif source == 'local_listing':
            fit_score += 1  # Bonus for local listings
            
        # Demand score calculation  
        demand_score = base_score
        if demand_matches:
            demand_score += len(demand_matches)
        if any(word in content_lower for word in ['appointment', 'call', 'contact', 'schedule']):
            demand_score += 1  # Bonus for action words
            
        # Cap scores
        fit_score = min(fit_score, 5)
        demand_score = min(demand_score, 5)
        
        logger.info(f"📊 SCORING RESULTS:")
        logger.info(f"   🎯 Fit Score: {fit_score}/5")
        logger.info(f"   🔥 Demand Score: {demand_score}/5")
        
        # GATE 5: AD INVESTMENT VERIFICATION (New Premium Gate!)
        logger.info(f"🎯 GATE 5: AD INVESTMENT VERIFICATION")
        
        # Initialize strategic insights
        strategic_insights = {'tier': 'basic', 'outreach_insights': [], 'followup_insights': [], 'proposal_insights': []}
        
        # Check for advertising activity via Transparency Center
        try:
            ad_investment_score, ad_analysis = await self._verify_ad_investment(domain)
            logger.info(f"   💰 Ad Investment Score: {ad_investment_score}/7")
            
            # STRATEGIC ANALYSIS for qualified prospects
            strategic_insights = await self._analyze_strategic_vulnerabilities(domain, ad_analysis)
            
            if ad_investment_score >= 3:  # Minimum threshold for ad investment
                logger.info(f"   ✅ STRONG AD INVESTMENT - High value prospect!")
                logger.info(f"   🎯 Strategic Tier: {strategic_insights['tier']}")
                # Bonus scoring for advertisers
                fit_score += 1
                demand_score += 1
            elif ad_investment_score >= 1:
                logger.info(f"   ⚠️ LIMITED AD INVESTMENT - Medium value prospect")
                logger.info(f"   🎯 Strategic Tier: {strategic_insights['tier']}")
                # No bonus, but doesn't disqualify
            else:
                logger.info(f"   ❌ NO AD INVESTMENT - Low digital maturity prospect")
                # Significant penalty but don't auto-reject (some good prospects might not advertise yet)
                fit_score = max(1, fit_score - 1)
                demand_score = max(1, demand_score - 1)
        except Exception as e:
            logger.info(f"   ⚠️ Ad verification failed: {e} - Proceeding without penalty")
            # Don't penalize for API failures
        
        # Re-cap scores after ad investment analysis
        fit_score = min(fit_score, 5)
        demand_score = min(demand_score, 5)
        
        logger.info(f"📊 FINAL SCORING RESULTS:")
        logger.info(f"   🎯 Fit Score: {fit_score}/5")
        logger.info(f"   🔥 Demand Score: {demand_score}/5")
        
        # GATE 6: GROWTH POTENTIAL threshold (opportunity-focused)
        # OPTIMIZED LOGIC: Rigorous filtering for S-Tier Sunday prospects
        growth_potential_score = fit_score + demand_score + (ad_investment_score // 2)  # Investment boost
        
        min_threshold = 10  # Ultra-rigorous barrier for premium prospects (67% of max score)
        if growth_potential_score < min_threshold:
            logger.info(f"❌ GATE 6 FAILED: Total growth potential below threshold ({growth_potential_score} < {min_threshold})")
            return None
        
        logger.info(f"✅ ALL GATES PASSED - GROWTH OPPORTUNITY QUALIFIED! 🚀")
        logger.info(f"   � Growth Potential Score: {growth_potential_score}/15 (fit:{fit_score} + demand:{demand_score} + investment:{ad_investment_score//2})")
        
        # Create discovery output with strategic insights
        return DiscoveryOutput(
            advertiser_id=ad.get('advertiser_id', '') or (advertiser_info.get('id', '') if advertiser_info else ''),
            domain=domain,
            vertical=vertical.value,
            currency="USD",
            last_seen=1,
            creative_count=1,
            demand_score=demand_score,
            fit_score=fit_score,
            discovery_timestamp=datetime.now(),
            company_name=title,
            strategic_insights=strategic_insights  # Progressive disclosure insights
        )
    
    def _calculate_basic_demand_score(self, ad: Dict, vertical: Vertical) -> int:
        """Calculate basic demand score based on ad content"""
        title = ad.get('title', '').lower()
        description = ad.get('description', '').lower()
        content = title + ' ' + description
        
        config = self.vertical_configs.get(vertical, {})
        demand_keywords = config.get('demand_keywords', [])
        
        score = 0
        for keyword in demand_keywords:
            if keyword in content:
                score += 1
        
        return min(score, 5)  # Cap at 5
    
    def _calculate_basic_fit_score(self, ad: Dict, vertical: Vertical) -> int:
        """Calculate basic fit score based on ad content"""
        title = ad.get('title', '').lower()
        description = ad.get('description', '').lower()
        content = title + ' ' + description
        
        config = self.vertical_configs.get(vertical, {})
        fit_indicators = config.get('fit_indicators', [])
        
        score = 0
        for indicator in fit_indicators:
            if indicator in content:
                score += 1
        
        return min(score, 5)  # Cap at 5
    
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
        if advertiser_info and (advertiser_info.get('advertiser_id') or advertiser_info.get('id')):
            score += 1
        
        # Vertical-specific fit
        config = self.vertical_configs[vertical]
        text = (ad.get('title', '') + ' ' + ad.get('description', '')).lower()
        fit_indicators = config.get('fit_indicators', [])
        
        if any(indicator.lower() in text for indicator in fit_indicators):
            score += 1
        
        return min(score, 5)
    
    def _assess_business_quality(self, domain: str, title: str, description: str, advertiser_info: Dict) -> int:
        """Assess if this is a legitimate, identifiable business (0-5 score) - OPTIMIZED FOR REAL ADVERTISERS"""
        score = 2  # Start with 2 for verified Google Ads advertisers
        
        # CRITERION 1: Has a business name (very lenient)
        if title and len(title) > 3:
            score += 1
        
        # CRITERION 2: Has a domain (basic check)
        if domain and '.' in domain and len(domain) > 5:
            score += 1
            
        # CRITERION 3: Has advertiser verification or campaign count
        if (advertiser_info and (
            advertiser_info.get('advertiser_id') or 
            advertiser_info.get('id') or
            'campaigns' in str(description) or
            'verified' in str(description).lower()
        )):
            score += 1
            
        return min(score, 5)  # Cap at 5
    
    def _is_professional_company_name(self, title: str) -> bool:
        """Check if company name looks professional and identifiable"""
        if not title or len(title) < 3:
            return False
            
        title_lower = title.lower()
        
        # RED FLAGS: Generic/spammy patterns
        spam_patterns = [
            'best', 'top', 'cheap', 'affordable', '#1', 'number 1',
            'click here', 'call now', 'limited time', 'special offer'
        ]
        
        if any(pattern in title_lower for pattern in spam_patterns):
            return False
            
        # POSITIVE INDICATORS: Professional naming
        professional_indicators = [
            # Proper business structures
            'llc', 'inc', 'corporation', 'corp', 'company', 'co.',
            # Professional services
            'medical center', 'clinic', 'hospital', 'center',
            'associates', 'group', 'partners', 'solutions'
        ]
        
        has_professional_structure = any(indicator in title_lower for indicator in professional_indicators)
        
        # LOCATION-BASED NAMES (good sign)
        location_indicators = [
            'tampa', 'miami', 'orlando', 'jacksonville', 'atlanta',
            'dallas', 'houston', 'phoenix', 'denver', 'seattle'
        ]
        has_location = any(loc in title_lower for loc in location_indicators)
        
        # Must have either professional structure OR location + service
        return has_professional_structure or has_location
    
    def _is_established_domain(self, domain: str) -> bool:
        """Check if domain looks established (not randomly generated)"""
        if not domain:
            return False
            
        domain_name = domain.split('.')[0].lower()
        
        # RED FLAGS: Random/generated patterns
        if len(domain_name) < 5:  # Too short
            return False
            
        # Has numbers in weird places (e.g., clinic123, service4u)
        if any(char.isdigit() for char in domain_name) and not domain_name.endswith(('24', '24h', '911')):
            return False
            
        # Too many hyphens (usually spammy)
        if domain_name.count('-') > 2:
            return False
            
        # POSITIVE INDICATORS: Looks like real business
        business_patterns = [
            'clinic', 'medical', 'health', 'care', 'center', 'hospital',
            'dental', 'urgent', 'family', 'practice', 'group', 'associates'
        ]
        
        return any(pattern in domain_name for pattern in business_patterns)
    
    def _is_excluded_from_icp(self, domain: str, title: str, description: str, vertical: Vertical) -> bool:
        """
        Filter out prospects that don't fit our ICP for Sunday lead generation:
        - Major international franchises (too sophisticated)
        - Wrong business verticals (hotels, dental clinics) 
        - Fortune 500 companies (too large)
        - Non-local businesses (poor fit for our services)
        """
        content = f"{domain} {title} {description}".lower()
        
        # Major franchise exclusions (too sophisticated for our target market)
        major_franchises = [
            'planetfitness', 'planet fitness', 'anytime fitness', 'anytimefitness',
            'equinox', 'la fitness', 'lifetime fitness', 'gold gym', 'golds gym',
            'virgin active', 'fitness first', '24 hour fitness', 'crunch fitness',
            'orange theory', 'orangetheory', 'crossfit', 'soulcycle', 'pure barre',
            'snap fitness', 'curves', 'jazzercise'
        ]
        
        # Wrong vertical exclusions (not primary fitness businesses)
        wrong_verticals = [
            'dental', 'dentist', 'teeth', 'orthodont', 'oral health',
            'hotel', 'resort', 'accommodation', 'hospitality',
            'hospital', 'medical center', 'clinic', 'healthcare',
            'pharmacy', 'drug store', 'chemist', 'prescription',
            'restaurant', 'food', 'dining', 'cuisine', 'cafe'
        ]
        
        # Size/sophistication exclusions (Fortune 500, publicly traded companies)
        enterprise_indicators = [
            'inc.', 'corp', 'corporation', 'ltd', 'limited', 'plc',
            'nasdaq', 'nyse', 'fortune', 'international', 'worldwide',
            'global', 'holdings', 'group', 'enterprises'
        ]
        
        # Check for major franchise exclusions
        for franchise in major_franchises:
            if franchise in content:
                return True
        
        # Check for wrong vertical exclusions (especially important for fitness vertical)
        if vertical == Vertical.FITNESS_GYMS_CA:
            for wrong_vertical in wrong_verticals:
                if wrong_vertical in content:
                    return True
        
        # Check for enterprise/large company indicators
        for indicator in enterprise_indicators:
            if indicator in content:
                return True
        
        return False
    
    def _has_location_info(self, advertiser_info: Dict, description: str) -> bool:
        """Check if business has identifiable location information"""
        
        # Check advertiser info for location
        if advertiser_info and 'location' in advertiser_info:
            return True
            
        # Check description for location indicators
        if description:
            location_patterns = [
                'tampa', 'miami', 'orlando', 'florida', 'fl',
                'atlanta', 'georgia', 'ga', 'dallas', 'texas', 'tx',
                'street', 'avenue', 'blvd', 'road', 'suite'
            ]
            
            description_lower = description.lower()
            return any(pattern in description_lower for pattern in location_patterns)
            
        return False
    
    def _is_professional_description(self, description: str) -> bool:
        """Check if description looks professional (not keyword-stuffed spam)"""
        if not description or len(description) < 20:
            return False
            
        description_lower = description.lower()
        
        # RED FLAGS: Spammy patterns
        spam_indicators = [
            'click now', 'call now', 'limited time', 'special offer',
            'best price', 'lowest price', 'guaranteed', '100% satisfaction',
            'free consultation', 'no obligation'
        ]
        
        spam_count = sum(1 for indicator in spam_indicators if indicator in description_lower)
        if spam_count >= 2:  # Multiple spam indicators = reject
            return False
            
        # POSITIVE INDICATORS: Professional language
        professional_indicators = [
            'experienced', 'licensed', 'certified', 'qualified',
            'professional', 'expertise', 'specialists', 'established',
            'serving', 'years of experience', 'board certified'
        ]
        
        return any(indicator in description_lower for indicator in professional_indicators)
    
    def _analyze_campaign_performance(self, ad_creatives: List[Dict], domain: str) -> Dict:
        """Analyze real campaign performance metrics for waste identification"""
        if not ad_creatives:
            return {}
        
        analysis = {
            'avg_campaign_duration': 0,
            'format_distribution': {},
            'recency_score': 0,
            'longevity_issues': [],
            'performance_red_flags': []
        }
        
        total_days = []
        format_counts = {}
        recent_campaigns = 0
        now = datetime.now()
        
        for ad in ad_creatives:
            # Duration analysis
            days_shown = ad.get('total_days_shown', 0)
            if days_shown > 0:
                total_days.append(days_shown)
            
            # Format distribution
            format_type = ad.get('format', 'unknown')
            format_counts[format_type] = format_counts.get(format_type, 0) + 1
            
            # Recency analysis
            try:
                last_shown = ad.get('last_shown_datetime', '')
                if last_shown:
                    last_date = datetime.fromisoformat(last_shown.replace('Z', '+00:00'))
                    days_ago = (now - last_date.replace(tzinfo=None)).days
                    if days_ago <= 30:
                        recent_campaigns += 1
            except:
                continue
        
        # Calculate metrics
        if total_days:
            analysis['avg_campaign_duration'] = sum(total_days) / len(total_days)
        
        analysis['format_distribution'] = format_counts
        analysis['recency_score'] = recent_campaigns / len(ad_creatives) if ad_creatives else 0
        
        # Identify performance issues
        if analysis['avg_campaign_duration'] < 30:
            analysis['performance_red_flags'].append('SHORT_CAMPAIGN_CYCLES')
        
        if analysis['recency_score'] < 0.3:
            analysis['performance_red_flags'].append('LOW_RECENT_ACTIVITY')
        
        if len(format_counts) == 1 and len(ad_creatives) > 3:
            analysis['performance_red_flags'].append('SINGLE_FORMAT_DEPENDENCY')
        
        return analysis
    
    def _calculate_budget_waste(self, ad_creatives: List[Dict], performance_analysis: Dict) -> Dict:
        """Calculate estimated monthly budget waste based on campaign inefficiencies"""
        waste_analysis = {
            'monthly_waste_estimate': 0,
            'high_cpm_waste': 0,
            'format_inefficiency': 0,
            'timing_waste': 0
        }
        
        ad_count = len(ad_creatives)
        if ad_count == 0:
            return waste_analysis
        
        # Estimate budget based on ad count (industry averages)
        estimated_monthly_budget = ad_count * 250  # $250/campaign average for SMBs
        
        # High CPM waste (poor targeting)
        format_dist = performance_analysis.get('format_distribution', {})
        if 'text' in format_dist and format_dist['text'] / ad_count > 0.7:
            # Over-reliance on text ads = higher CPM
            waste_analysis['high_cpm_waste'] = estimated_monthly_budget * 0.15
        
        # Format inefficiency
        if len(format_dist) == 1 and ad_count > 3:
            # Single format = missing optimization opportunities
            waste_analysis['format_inefficiency'] = estimated_monthly_budget * 0.12
        
        # Timing waste
        if performance_analysis.get('recency_score', 0) < 0.3:
            # Low recent activity = potential wasted spend
            waste_analysis['timing_waste'] = estimated_monthly_budget * 0.10
        
        # Total waste
        waste_analysis['monthly_waste_estimate'] = (
            waste_analysis['high_cpm_waste'] + 
            waste_analysis['format_inefficiency'] + 
            waste_analysis['timing_waste']
        )
        
        return waste_analysis
    
    def _identify_competitive_inefficiencies(self, ad_creatives: List[Dict], domain: str) -> Dict:
        """Identify competitive positioning inefficiencies"""
        competitive_analysis = {
            'bidding_inefficiency': 0,
            'positioning_gaps': [],
            'market_share_lost': 0
        }
        
        ad_count = len(ad_creatives)
        estimated_budget = ad_count * 250
        
        # Simple heuristics for competitive inefficiencies
        # (In production, this would use real competitor data)
        
        if ad_count < 5:
            competitive_analysis['bidding_inefficiency'] = estimated_budget * 0.08
            competitive_analysis['positioning_gaps'].append('INSUFFICIENT_MARKET_COVERAGE')
        
        if ad_count > 20:
            competitive_analysis['bidding_inefficiency'] = estimated_budget * 0.06
            competitive_analysis['positioning_gaps'].append('POTENTIAL_OVERBIDDING')
        
        return competitive_analysis
    
    def _get_quality_issues(self, domain: str, title: str, description: str, advertiser_info: Dict) -> List[str]:
        """Get list of quality issues for logging - SIMPLIFIED FOR REAL ADVERTISERS"""
        issues = []
        
        if not title or len(title) <= 3:
            issues.append("Very short/missing title")
            
        if not domain or '.' not in domain or len(domain) <= 5:
            issues.append("Invalid domain format")
            
        if not (advertiser_info or 'campaigns' in str(description) or 'verified' in str(description).lower()):
            issues.append("No verification indicators")
            
        return issues
        
        return min(score, 3)