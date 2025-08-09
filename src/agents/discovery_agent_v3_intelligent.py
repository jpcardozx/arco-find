"""
Discovery Agent V3 - INTELLIGENT MULTI-ENGINE APPROACH
STRATEGIC VULNERABILITY-FOCUSED DISCOVERY ENGINE

Based on real SearchAPI documentation analysis:
- LinkedIn Ad Library (Primary) - Real B2B intelligence  
- Google Ads Transparency Center (Secondary) - Consumer validation
- Ad Details API (Deep analysis) - Vulnerability detection
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


class IntelligentDiscoveryAgent:
    """
    INTELLIGENT DISCOVERY ENGINE - ESCALONATED MULTI-SOURCE STRATEGY
    
    STRATEGY HIERARCHY:
    1. LinkedIn Ad Library (Primary) - Real B2B data, professional targeting
    2. Google Ads Transparency Center (Secondary) - Consumer/enterprise mix
    3. Cross-validation with Ad Details API for vulnerability detection
    
    VULNERABILITY INDICATORS (Auto-detect poor ad execution):
    - Short campaign durations (<7 days) = Poor planning
    - Generic CTAs without value prop = Weak creative strategy  
    - Broad demographic targeting = Unfocused approach
    - High impression ranges with low duration = Budget waste
    - Missing platform optimization = Poor media strategy
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or APIConfig.SEARCHAPI_KEY
        self.base_url = "https://www.searchapi.io/api/v1"
        self.session = None
        self.logger = logger
        
        # INTELLIGENT VERTICAL CONFIGURATIONS - VULNERABILITY-FOCUSED QUERIES
        self.vertical_configs = {
            Vertical.HVAC_MULTI: {
                "linkedin_queries": [
                    "hvac emergency service",
                    "air conditioning installation", 
                    "heating repair contractors",
                    "hvac maintenance plans"
                ],
                "google_queries": [
                    "24/7 hvac emergency",
                    "same day air conditioning repair",
                    "licensed hvac contractors near me",
                    "hvac financing options"
                ],
                "vulnerability_indicators": [
                    "emergency_positioning_without_24_7_proof",
                    "generic_hvac_service_messaging", 
                    "seasonal_campaigns_running_off_season",
                    "high_cpc_broad_match_keywords"
                ]
            },
            Vertical.DENTAL_CLINICS: {
                "linkedin_queries": [
                    "dental implant marketing",
                    "cosmetic dentistry advertising", 
                    "dental practice growth",
                    "patient acquisition dentistry"
                ],
                "google_queries": [
                    "dental implants cost",
                    "cosmetic dentist near me",
                    "emergency dental care",
                    "teeth whitening special offers"
                ],
                "vulnerability_indicators": [
                    "price_focused_messaging_without_value",
                    "generic_dental_service_ads",
                    "emergency_claims_without_availability_proof",
                    "before_after_images_without_disclaimers"
                ]
            },
            Vertical.URGENT_CARE: {
                "linkedin_queries": [
                    "urgent care marketing",
                    "walk-in clinic advertising",
                    "immediate care patient acquisition",
                    "express clinic lead generation"
                ],
                "google_queries": [
                    "urgent care",
                    "walk in clinic",
                    "immediate care",
                    "express clinic"
                ],
                "vulnerability_indicators": [
                    "wait_time_claims_without_verification",
                    "generic_urgent_care_messaging",
                    "insurance_acceptance_without_details",
                    "broad_geographic_targeting_without_local_presence"
                ]
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
    
    async def run_intelligent_discovery(self, 
                                      vertical: Vertical = None,
                                      max_credits: int = 50,
                                      target_discoveries: int = 15) -> List[DiscoveryOutput]:
        """
        INTELLIGENT ESCALONATED DISCOVERY ENGINE
        
        STRATEGY:
        1. LinkedIn Ad Library (Primary) - Real B2B intelligence
        2. Google Transparency Center (Secondary) - Consumer validation  
        3. Ad Details API (Deep analysis) - Vulnerability detection
        """
        logger.info(f"🧠 INTELLIGENT DISCOVERY ENGINE - Max credits: {max_credits}")
        logger.info(f"🎯 Target: {target_discoveries} qualified prospects with ad vulnerabilities")
        
        discovered_advertisers = []
        credits_used = 0
        
        # Select verticals to process
        target_verticals = [vertical] if vertical else list(self.vertical_configs.keys())
        
        for target_vertical in target_verticals:
            if credits_used >= max_credits:
                break
                
            logger.info(f"🔍 Processing vertical: {target_vertical.value}")
            config = self.vertical_configs[target_vertical]
            
            # PHASE 1: LinkedIn Ad Library (Primary Intelligence Source)
            linkedin_results = await self._search_linkedin_ads(
                config["linkedin_queries"], 
                target_vertical,
                max_credits - credits_used
            )
            
            for result in linkedin_results:
                if credits_used >= max_credits or len(discovered_advertisers) >= target_discoveries:
                    break
                    
                # Deep vulnerability analysis
                vulnerability_analysis = await self._analyze_linkedin_ad_vulnerabilities(result)
                
                if vulnerability_analysis["vulnerability_score"] >= 6:  # High vulnerability threshold
                    discovery = await self._create_discovery_output(result, vulnerability_analysis, target_vertical)
                    discovered_advertisers.append(discovery)
                    credits_used += 1
                    
            # PHASE 2: Google Transparency Center (Validation & Additional Discovery)
            if len(discovered_advertisers) < target_discoveries and credits_used < max_credits:
                google_results = await self._search_google_transparency(
                    config["google_queries"],
                    target_vertical, 
                    max_credits - credits_used
                )
                
                for result in google_results:
                    if credits_used >= max_credits or len(discovered_advertisers) >= target_discoveries:
                        break
                        
                    # Cross-validate with Ad Details API
                    ad_details = await self._get_ad_details_vulnerability_analysis(result)
                    
                    if ad_details["vulnerability_score"] >= 7:  # Higher threshold for Google
                        discovery = await self._create_discovery_output(result, ad_details, target_vertical)
                        discovered_advertisers.append(discovery)
                        credits_used += 1
        
        logger.info(f"✅ DISCOVERY COMPLETE: {len(discovered_advertisers)} qualified prospects")
        logger.info(f"💰 Credits used: {credits_used}/{max_credits}")
        
        return discovered_advertisers
    
    async def _search_linkedin_ads(self, queries: List[str], vertical: Vertical, max_credits: int) -> List[Dict]:
        """
        PRIMARY ENGINE: LinkedIn Ad Library - Real B2B Intelligence
        
        LinkedIn provides superior B2B data quality with:
        - Professional targeting details
        - Company-specific campaigns  
        - Ad format sophistication analysis
        - Time period targeting strategies
        """
        results = []
        credits_used = 0
        
        logger.info(f"🔵 LinkedIn Ad Library Search - {vertical.value}")
        
        for query in queries:
            if credits_used >= max_credits:
                break
                
            params = {
                "engine": "linkedin_ad_library",
                "q": query,
                "time_period": "last_30_days",  # Recent campaigns only
                "api_key": self.api_key
            }
            
            try:
                async with self.session.get(f"{self.base_url}/search", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        ads = data.get("ads", [])
                        
                        for ad in ads[:5]:  # Top 5 results per query
                            # Extract advertiser intelligence
                            advertiser_info = {
                                "source": "linkedin",
                                "query": query,
                                "advertiser_name": ad.get("advertiser", {}).get("name"),
                                "ad_type": ad.get("ad_type"),
                                "content": ad.get("content", {}),
                                "ad_id": ad.get("id"),
                                "raw_data": ad
                            }
                            results.append(advertiser_info)
                            
                        credits_used += 1
                        logger.info(f"  📊 Query: {query} - Found {len(ads)} ads")
                        
                    else:
                        logger.error(f"LinkedIn API error: {response.status}")
                        
            except Exception as e:
                logger.error(f"LinkedIn search error: {e}")
                
        return results
        
    async def _search_google_transparency(self, queries: List[str], vertical: Vertical, max_credits: int) -> List[Dict]:
        """
        SECONDARY ENGINE: Google Ads Transparency Center - Consumer Validation
        
        Google provides broader market intelligence with:
        - Geographic targeting analysis
        - Platform distribution insights  
        - Creative format optimization
        - Impression volume indicators
        """
        results = []
        credits_used = 0
        
        logger.info(f"🔴 Google Transparency Center Search - {vertical.value}")
        
        # Use advertiser search first to find relevant advertisers
        for query in queries:
            if credits_used >= max_credits:
                break
                
            # Step 1: Advertiser Search
            params = {
                "engine": "google_ads_transparency_center_advertiser_search",
                "q": query,
                "num_advertisers": 10,
                "api_key": self.api_key
            }
            
            try:
                async with self.session.get(f"{self.base_url}/search", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        advertisers = data.get("advertisers", [])
                        
                        for advertiser in advertisers[:3]:  # Top 3 per query
                            # Extract advertiser intelligence
                            advertiser_info = {
                                "source": "google_transparency",
                                "query": query,
                                "advertiser_id": advertiser.get("id"),
                                "advertiser_name": advertiser.get("name"),
                                "region": advertiser.get("region"),
                                "ads_count": advertiser.get("ads_count", {}),
                                "is_verified": advertiser.get("is_verified", False),
                                "raw_data": advertiser
                            }
                            results.append(advertiser_info)
                            
                        credits_used += 1
                        logger.info(f"  📊 Query: {query} - Found {len(advertisers)} advertisers")
                        
                    else:
                        logger.error(f"Google Transparency API error: {response.status}")
                        
            except Exception as e:
                logger.error(f"Google Transparency search error: {e}")
                
        return results
        
    async def _analyze_linkedin_ad_vulnerabilities(self, ad_data: Dict) -> Dict:
        """
        LINKEDIN VULNERABILITY ANALYSIS ENGINE
        
        Analyzes LinkedIn ads for execution weaknesses that indicate ARCO opportunity:
        - Generic messaging without value proposition
        - Poor CTA optimization  
        - Weak targeting sophistication
        - Creative format misalignment
        """
        content = ad_data.get("content", {})
        ad_type = ad_data.get("ad_type", "")
        
        vulnerability_score = 0
        vulnerabilities = []
        
        # VULNERABILITY 1: Generic Headlines (Score: 0-3)
        headline = content.get("headline", "").lower()
        if any(generic in headline for generic in ["services", "solutions", "best", "quality"]):
            vulnerability_score += 2
            vulnerabilities.append("generic_value_proposition")
        
        # VULNERABILITY 2: Weak CTA (Score: 0-2)
        cta = content.get("cta", "").lower()
        if cta in ["learn more", "click here", "visit website"]:
            vulnerability_score += 2
            vulnerabilities.append("weak_call_to_action")
            
        # VULNERABILITY 3: Ad Format Misalignment (Score: 0-3)
        if ad_type == "image" and not content.get("image"):
            vulnerability_score += 3
            vulnerabilities.append("missing_visual_content")
        elif ad_type == "carousel" and len(content.get("items", [])) < 3:
            vulnerability_score += 2
            vulnerabilities.append("underutilized_carousel_format")
            
        # VULNERABILITY 4: Professional Messaging Issues (Score: 0-2)
        if any(word in headline for word in ["cheap", "discount", "sale"]):
            vulnerability_score += 2
            vulnerabilities.append("price_focused_b2b_messaging")
            
        return {
            "vulnerability_score": min(vulnerability_score, 10),
            "vulnerabilities": vulnerabilities,
            "analysis_engine": "linkedin_professional_targeting",
            "recommended_arco_approach": "consultative_b2b_optimization"
        }
    
    async def _get_ad_details_vulnerability_analysis(self, result: Dict) -> Dict:
        """
        GOOGLE AD DETAILS VULNERABILITY ANALYSIS
        
        Uses Ad Details API to analyze campaign execution quality:
        - Campaign duration analysis (short = poor planning)
        - Geographic targeting efficiency
        - Platform distribution optimization
        - Creative format effectiveness
        """
        advertiser_id = result.get("advertiser_id")
        if not advertiser_id:
            return {"vulnerability_score": 0, "vulnerabilities": [], "analysis_engine": "google_ad_details", "error": "missing_advertiser_id"}
        
        # Get ad creatives for this advertiser
        params = {
            "engine": "google_ads_transparency_center",
            "advertiser_id": advertiser_id,
            "time_period": "last_30_days",
            "num": 20,
            "api_key": self.api_key
        }
        
        vulnerability_score = 0
        vulnerabilities = []
        
        try:
            async with self.session.get(f"{self.base_url}/search", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    ad_creatives = data.get("ad_creatives", [])
                    
                    if not ad_creatives:
                        vulnerability_score += 3
                        vulnerabilities.append("no_recent_ad_activity")
                        return {
                            "vulnerability_score": vulnerability_score,
                            "vulnerabilities": vulnerabilities,
                            "analysis_engine": "google_ad_details"
                        }
                    
                    # Analyze campaign patterns
                    total_campaigns = len(ad_creatives)
                    short_campaigns = 0
                    formats = {}
                    
                    for creative in ad_creatives:
                        # VULNERABILITY 1: Short campaign durations
                        days_shown = creative.get("total_days_shown", 0)
                        if days_shown < 7:
                            short_campaigns += 1
                            
                        # VULNERABILITY 2: Format distribution
                        format_type = creative.get("format", "unknown")
                        formats[format_type] = formats.get(format_type, 0) + 1
                    
                    # Calculate vulnerability scores
                    if short_campaigns / total_campaigns > 0.6:  # >60% short campaigns
                        vulnerability_score += 3
                        vulnerabilities.append("poor_campaign_planning_short_durations")
                    
                    if len(formats) == 1:  # Only one format used
                        vulnerability_score += 2
                        vulnerabilities.append("limited_creative_format_testing")
                    
                    # VULNERABILITY 3: Get detailed analysis for top creative
                    if ad_creatives:
                        top_creative = ad_creatives[0]
                        creative_id = top_creative.get("id")
                        
                        if creative_id:
                            detail_analysis = await self._analyze_creative_details(advertiser_id, creative_id)
                            vulnerability_score += detail_analysis.get("vulnerability_score", 0)
                            vulnerabilities.extend(detail_analysis.get("vulnerabilities", []))
                    
                else:
                    logger.error(f"Google Ad Details API error: {response.status}")
                    vulnerability_score += 1
                    vulnerabilities.append("transparency_api_access_issues")
                    
        except Exception as e:
            logger.error(f"Google Ad Details analysis error: {e}")
            vulnerability_score += 1
            vulnerabilities.append("technical_analysis_error")
            
        return {
            "vulnerability_score": min(vulnerability_score, 10),
            "vulnerabilities": vulnerabilities,
            "analysis_engine": "google_ad_details",
            "total_campaigns_analyzed": len(ad_creatives) if 'ad_creatives' in locals() else 0
        }
    
    async def _analyze_creative_details(self, advertiser_id: str, creative_id: str) -> Dict:
        """
        DEEP CREATIVE ANALYSIS using Ad Details API
        
        Analyzes specific creative execution for sophisticated vulnerabilities:
        - Audience targeting sophistication
        - Geographic precision
        - Platform optimization
        - Creative variations quality
        """
        params = {
            "engine": "google_ads_transparency_center_ad_details",
            "advertiser_id": advertiser_id,
            "creative_id": creative_id,
            "api_key": self.api_key
        }
        
        vulnerability_score = 0
        vulnerabilities = []
        
        try:
            async with self.session.get(f"{self.base_url}/search", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Analyze ad information
                    ad_info = data.get("ad_information", {})
                    audience_selection = ad_info.get("audience_selection", {})
                    
                    # VULNERABILITY 1: Poor audience targeting
                    if audience_selection.get("demographic_info") == "Some included, some excluded":
                        vulnerability_score += 1
                        vulnerabilities.append("unfocused_demographic_targeting")
                    
                    if audience_selection.get("geographic_locations") == "Some included, some excluded":
                        vulnerability_score += 1
                        vulnerabilities.append("broad_geographic_targeting")
                    
                    # VULNERABILITY 2: Creative variations analysis
                    variations = data.get("variations", [])
                    if len(variations) < 2:
                        vulnerability_score += 2
                        vulnerabilities.append("insufficient_creative_testing")
                    
                    # VULNERABILITY 3: Video duration analysis (if video)
                    if ad_info.get("format") == "video":
                        for variation in variations:
                            duration = variation.get("duration", "")
                            if duration and ":" in duration:
                                minutes, seconds = duration.split(":")
                                total_seconds = int(minutes) * 60 + int(seconds)
                                if total_seconds > 120:  # >2 minutes
                                    vulnerability_score += 1
                                    vulnerabilities.append("excessive_video_length_poor_engagement")
                    
                else:
                    logger.error(f"Creative Details API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Creative details analysis error: {e}")
            
        return {
            "vulnerability_score": vulnerability_score,
            "vulnerabilities": vulnerabilities
        }
    
    async def _create_discovery_output(self, result: Dict, vulnerability_analysis: Dict, vertical: Vertical) -> DiscoveryOutput:
        """
        Create comprehensive discovery output with vulnerability intelligence
        """
        advertiser_name = result.get("advertiser_name", "Unknown")
        source = result.get("source", "unknown")
        
        # Extract domain if available
        domain = None
        if source == "linkedin":
            # Try to extract domain from LinkedIn content
            content = result.get("content", {})
            if "link" in content:
                domain = urlparse(content["link"]).netloc
        elif source == "google_transparency":
            # For Google, domain might be in raw_data or we need to fetch it
            domain = f"{advertiser_name.lower().replace(' ', '')}.com"  # Estimation
        
        return DiscoveryOutput(
            company_name=advertiser_name,
            domain=domain,
            vertical=vertical,
            demand_score=8.5,  # High score due to vulnerability detection
            fit_score=vulnerability_analysis["vulnerability_score"],
            contact_info={
                "source": source,
                "discovery_query": result.get("query", ""),
                "ad_vulnerabilities": vulnerability_analysis["vulnerabilities"],
                "arco_opportunity": vulnerability_analysis.get("recommended_arco_approach", "optimization_required")
            },
            ad_details={
                "vulnerability_analysis": vulnerability_analysis,
                "source_data": result.get("raw_data", {}),
                "discovery_engine": f"{source}_vulnerability_focused"
            }
        )
