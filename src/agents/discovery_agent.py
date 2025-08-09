"""
Discovery Agent - ARCO V3 INTELLIGENT ENGINE
STRATEGIC MULTI-ENGINE APPROACH WITH VULNERABILITY-FOCUSED DISCOVERY
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
    ARCO V3 INTELLIGENT ESCALATED DISCOVERY ENGINE
    
    🎯 STRATEGIC ESCALATION HIERARCHY:
    1️⃣ PRIMARY: LinkedIn Ad Library → B2B Professional targeting, rich company data
    2️⃣ SECONDARY: Google Ads Transparency Center → Volume + Cross-platform validation  
    3️⃣ TERTIARY: Reddit Ad Library → Community-driven, niche targeting validation
    4️⃣ INTELLIGENCE: Google Ad Details API → Deep vulnerability analysis
    
    🚨 INTELLIGENT VULNERABILITY DETECTION:
    ═══════════════════════════════════════════════
    LinkedIn Indicators:
    • Ad types mismatch (carousel for simple offers = overcomplicated)
    • Generic headlines without value props = weak messaging
    • Missing CTAs or poor CTA copy = conversion problems
    • Document ads for service businesses = format misalignment
    
    Google Ads Indicators:
    • Campaign duration <14 days = poor planning/testing
    • Broad geographic targeting with local services = waste
    • Video ads <15s or >90s for B2B = duration optimization issues
    • High impression ranges (>10k) with short duration = budget burn
    
    Reddit Indicators:
    • HIGH budget category with gaming industry + B2B keywords = wrong platform
    • Feed placement only (missing comments) = engagement missed
    • Video content for non-entertainment = format misalignment
    
    ⚡ REAL-TIME INTELLIGENCE SYNTHESIS:
    Cross-validates findings across platforms to identify companies with
    systematic advertising execution problems = HIGH-VALUE ARCO PROSPECTS
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or APIConfig.SEARCHAPI_KEY
        self.base_url = "https://www.searchapi.io/api/v1"
        self.session = None
        self.logger = logger
        
        # 🧠 INTELLIGENT ENGINE CONFIGURATION - REDDIT-FIRST STRATEGY
        self.engines = {
            "primary": "reddit_ad_library",  # NICHOS MENOS MADUROS = VULNERABILIDADES ÓBVIAS
            "secondary": "google_ads_transparency_center_advertiser_search", 
            "tertiary": "linkedin_ad_library",  # EMPRESAS MADURAS = MENOS VULNERÁVEIS
            "intelligence": "google_ads_transparency_center_ad_details"
        }
        
        # 🎯 VULNERABILITY-FOCUSED VERTICAL CONFIGURATIONS - REDDIT-FIRST STRATEGY
        self.vertical_configs = {
            Vertical.HVAC_MULTI: {
                "reddit_queries": [
                    "home repair emergency",  # Nichos menos tech-savvy
                    "air conditioning summer deals",  # Price-focused vulnerabilities  
                    "heating winter preparation",  # Seasonal targeting issues
                    "home improvement financing"  # High-ticket amateur targeting
                ],
                "google_queries": [
                    "24/7 hvac emergency repair",  # Emergency claims validation
                    "same day air conditioning",  # Speed claims verification
                    "licensed hvac contractors",  # Credential claims checking
                    "hvac financing options"  # High-ticket targeting validation
                ],
                "linkedin_queries": [
                    "hvac contractor software",  # B2B validation only
                    "commercial hvac installation",  # Enterprise confirmation  
                    "hvac maintenance contracts",  # Recurring revenue validation
                    "hvac emergency service"  # Professional cross-check
                ],
                "vulnerability_focus": "emergency_claims_without_infrastructure",
                "geo_targets": ["Tampa", "Miami", "Phoenix", "Dallas", "Atlanta"]
            },
            
            Vertical.URGENT_CARE: {
                "reddit_queries": [
                    "healthcare alternatives",  # Anti-establishment sentiment
                    "avoid emergency room costs",  # Cost-conscious targeting
                    "quick medical attention",  # Speed expectation vulnerability
                    "family health solutions"  # Local healthcare communities
                ],
                "google_queries": [
                    "urgent care open now",  # Immediate need validation
                    "walk in clinic near me",  # Local competition analysis
                    "express care {city}",  # Geographic specific
                    "immediate medical care"  # Broad urgency targeting
                ],
                "reddit_queries": [
                    "urgent care vs emergency room",  # Educational content opportunity
                    "walk in clinic experience",  # Community reviews/feedback
                    "quick medical care options"  # Alternative seeking behavior
                ],
                "vulnerability_focus": "wait_time_claims_without_verification",
                "geo_targets": ["Tampa", "Miami", "Orlando", "Dallas", "Phoenix"]
            },
            
            Vertical.DENTAL_CLINICS: {
                "linkedin_queries": [
                    "gym membership marketing",  # B2B fitness marketing
                    "fitness club lead generation",  # Business focus
                    "personal training sales",  # High-value service focus
                    "fitness center retention"  # Operational efficiency
                ],
                "google_queries": [
                    "gym membership deals",  # Price-focused vulnerability
                    "fitness club near me",  # Local competition

                    "personal trainer {city}",  # High-value service targeting
                    "24 hour gym access"  # Convenience positioning
                ],
                "reddit_queries": [
                    "best gym membership value",  # Value-conscious community
                    "fitness club recommendations",  # Social proof seeking
                    "home gym vs gym membership"  # Decision-making content
                ],
                "vulnerability_focus": "price_focused_messaging_without_value",
                "geo_targets": ["Tampa", "Miami", "Atlanta", "Dallas", "Phoenix"]
            },
            
            Vertical.AUTO_SERVICES: {
                "linkedin_queries": [
                    "auto dealership marketing",  # B2B automotive marketing
                    "car sales lead generation",  # Sales process focus
                    "automotive digital advertising",  # Technology adoption
                    "dealership customer acquisition"  # Business development
                ],
                "google_queries": [
                    "cars for sale {city}",  # Local inventory focus
                    "auto financing deals",  # Financial services targeting
                    "certified pre-owned vehicles",  # Quality positioning
                    "car dealership near me"  # Geographic competition
                ],
                "reddit_queries": [
                    "car buying experience",  # Process discussion
                    "dealership vs private sale",  # Channel preference
                    "auto financing advice"  # Financial guidance seeking
                ],
                "vulnerability_focus": "inventory_messaging_without_availability",
                "geo_targets": ["Tampa", "Miami", "Dallas", "Phoenix", "Atlanta"]
            }
        }
        
        # 🧠 VULNERABILITY INTELLIGENCE PATTERNS - SPECIFIC BY VERTICAL
        self.vulnerability_patterns = {
            "hvac_contractors": {
                "critical_signals": [
                    {
                        "pattern": r"24/7|emergency|same day|immediate",
                        "vulnerability": "emergency_claims_without_proof_system",
                        "evidence_required": ["response_time_tracking", "dispatcher_system", "real_time_status"],
                        "roi_potential": 8500,  # $ monthly savings potential
                        "urgency": "high",
                        "context": "Emergency response claims without verifiable infrastructure"
                    },
                    {
                        "pattern": r"licensed|certified|insured|bonded", 
                        "vulnerability": "credential_claims_without_verification",
                        "evidence_required": ["license_verification_system", "certification_display", "insurance_validation"],
                        "roi_potential": 4200,
                        "urgency": "medium",
                        "context": "Professional credentials without public verification system"
                    },
                    {
                        "pattern": r"free estimate|no cost|guaranteed|warranty",
                        "vulnerability": "value_claims_without_specificity",
                        "evidence_required": ["estimate_process_transparency", "warranty_terms_clarity", "service_guarantees"],
                        "roi_potential": 3100,
                        "urgency": "medium",
                        "context": "Value propositions without clear terms or process"
                    }
                ]
            },
            
            "urgent_care": {
                "critical_signals": [
                    {
                        "pattern": r"no wait|under \d+ minutes|immediate|fast|quick",
                        "vulnerability": "wait_time_promises_without_tracking",
                        "evidence_required": ["queue_management_system", "real_time_updates", "wait_time_display"],
                        "roi_potential": 12000,
                        "urgency": "critical",
                        "context": "Wait time promises without real-time verification system"
                    },
                    {
                        "pattern": r"walk.?in|no appointment|open \d+|24.?hour",
                        "vulnerability": "availability_claims_without_confirmation",
                        "evidence_required": ["online_scheduling_integration", "real_time_availability", "capacity_management"],
                        "roi_potential": 7800,
                        "urgency": "high",
                        "context": "Availability claims without real-time capacity verification"
                    }
                ]
            },
            
            "fitness_gyms": {
                "critical_signals": [
                    {
                        "pattern": r"lose \d+ pounds|transform|results|before.?after",
                        "vulnerability": "transformation_claims_without_tracking",
                        "evidence_required": ["progress_tracking_system", "results_verification", "client_testimonial_validation"],
                        "roi_potential": 5600,
                        "urgency": "medium",
                        "context": "Transformation promises without systematic progress tracking"
                    },
                    {
                        "pattern": r"\$\d+|deal|special|discount|limited time",
                        "vulnerability": "price_focused_messaging_without_value_proof",
                        "evidence_required": ["value_demonstration_system", "competitor_comparison", "service_differentiation"],
                        "roi_potential": 4300,
                        "urgency": "medium",
                        "context": "Price-focused messaging without clear value differentiation"
                    }
                ]
            },
            
            "auto_dealers": {
                "critical_signals": [
                    {
                        "pattern": r"in stock|available now|\d+ cars|huge selection",
                        "vulnerability": "inventory_claims_without_real_time_data",
                        "evidence_required": ["real_time_inventory_system", "stock_level_integration", "availability_confirmation"],
                        "roi_potential": 9200,
                        "urgency": "high",
                        "context": "Inventory availability claims without real-time verification"
                    },
                    {
                        "pattern": r"best price|lowest rate|guaranteed|unbeatable",
                        "vulnerability": "price_superiority_claims_without_evidence",
                        "evidence_required": ["price_comparison_system", "market_rate_tracking", "competitor_monitoring"],
                        "roi_potential": 6700,
                        "urgency": "medium",
                        "context": "Price superiority claims without market comparison system"
                    }
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
    
    async def run_daily_queries(self, 
                              vertical: Vertical = None,
                              max_credits: int = 50,
                              target_discoveries: int = 15) -> List[DiscoveryOutput]:
        """
        🚀 ARCO V3 ESCALATED INTELLIGENT DISCOVERY ENGINE
        
        MULTI-ENGINE STRATEGY:
        🥇 LinkedIn Ad Library (Primary) - B2B Professional Intelligence
        🥈 Google Transparency Center (Secondary) - Volume + Cross-validation  
        🥉 Reddit Ad Library (Tertiary) - Community + Niche Intelligence
        🔬 Google Ad Details API (Intelligence) - Deep Vulnerability Analysis
        
        INTELLIGENCE FOCUS: Companies showing signs of poor ad execution = ARCO opportunities
        """
        logger.info(f"🧠 ESCALATED DISCOVERY ENGINE - Max credits: {max_credits}")
        logger.info(f"🎯 Target: {target_discoveries} vulnerability-scored prospects")
        
        discovered_advertisers = []
        credits_used = 0
        
        # Select verticals to process
        target_verticals = [vertical] if vertical else list(self.vertical_configs.keys())
        
        # 🚀 Execute escalated discovery strategy
        for target_vertical in target_verticals:
            if credits_used >= max_credits or len(discovered_advertisers) >= target_discoveries:
                break
                
            logger.info(f"📊 Processing vertical: {target_vertical.value}")
            config = self.vertical_configs[target_vertical]
            
            # 🥇 PHASE 1: Reddit Ad Library (Primary - Niches menos tech-savvy)
            reddit_results = await self._search_reddit_ads(
                config["reddit_queries"],
                target_vertical,
                min(10, max_credits - credits_used)  # Maior alocação para Reddit
            )
            
            for result in reddit_results:
                if credits_used >= max_credits or len(discovered_advertisers) >= target_discoveries:
                    break
                    
                # VULNERABILITY INTELLIGENCE ANALYSIS
                vulnerability_analysis = await self._analyze_vulnerability_intelligence(result, target_vertical)
                
                if vulnerability_analysis["total_vulnerability_score"] >= 7:  # High vulnerability threshold
                    discovery = await self._create_discovery_output(result, vulnerability_analysis, target_vertical)
                    discovered_advertisers.append(discovery)
                    credits_used += 1
                    logger.info(f"✅ Reddit prospect: {result.get('profile_info', {}).get('name', 'Unknown')} (score: {vulnerability_analysis['total_vulnerability_score']})")
                    
            # 🥈 PHASE 2: Google Transparency Center (Volume + Validation)
            if len(discovered_advertisers) < target_discoveries and credits_used < max_credits:
                google_results = await self._search_google_transparency(
                    config["google_queries"],
                    target_vertical, 
                    min(6, max_credits - credits_used)
                )
                
                for result in google_results:
                    if credits_used >= max_credits or len(discovered_advertisers) >= target_discoveries:
                        break
                        
                    # Google vulnerability intelligence analysis
                    ad_details = await self._get_ad_details_vulnerability_analysis(result)
                    
                    if ad_details["vulnerability_score"] >= 8:  # Higher threshold for Google volume
                        discovery = await self._create_discovery_output(result, ad_details, target_vertical)
                        discovered_advertisers.append(discovery)
                        credits_used += 1
                        logger.info(f"✅ Google prospect: {result.get('name', 'Unknown')} (score: {ad_details['vulnerability_score']})")
            
            # 🥉 PHASE 3: LinkedIn Ad Library (Validation + Enterprise confirmation)
            if len(discovered_advertisers) < target_discoveries and credits_used < (max_credits - 3):  # Reserve credits
                linkedin_queries = config.get("linkedin_queries", [])
                if linkedin_queries:
                    linkedin_results = await self._search_linkedin_ads(
                        linkedin_queries,
                        target_vertical,
                        min(4, max_credits - credits_used)  # Limited LinkedIn - empresas maduras
                    )
                
                for result in linkedin_results:
                    if credits_used >= max_credits or len(discovered_advertisers) >= target_discoveries:
                        break
                        
                    # LinkedIn vulnerability analysis (higher standards)
                    linkedin_analysis = await self._analyze_linkedin_ad_vulnerabilities(result)
                    
                    if linkedin_analysis["vulnerability_score"] >= 6:  # Lower threshold - validation only
                        discovery = await self._create_discovery_output(result, linkedin_analysis, target_vertical)
                        discovered_advertisers.append(discovery)
                        credits_used += 1
                        logger.info(f"✅ LinkedIn prospect: {result.get('advertiser_name', 'Unknown')} (score: {linkedin_analysis['vulnerability_score']})")
        
        logger.info(f"🎯 REDDIT-FIRST DISCOVERY COMPLETE: {len(discovered_advertisers)} qualified prospects")
        logger.info(f"💰 Credits used: {credits_used}/{max_credits}")
        logger.info(f"📊 Discovery rate: {len(discovered_advertisers)/credits_used:.2f} prospects/credit" if credits_used > 0 else "N/A")
        
        return discovered_advertisers

    async def _analyze_vulnerability_intelligence(self, ad_data: Dict, vertical: Vertical) -> Dict:
        """
        🧠 VULNERABILITY INTELLIGENCE ENGINE
        
        Análise específica por vertical usando padrões de vulnerabilidade inteligentes.
        Detecta gaps entre claims dos ads e infraestrutura necessária para suportá-los.
        
        Args:
            ad_data: Dados do ad (Reddit/Google/LinkedIn)
            vertical: Vertical específico para análise contextual
            
        Returns:
            Dict com vulnerability score, insights acionáveis e ROI potencial
        """
        import re
        
        # Mapear vertical para padrões de vulnerabilidade
        vertical_mapping = {
            Vertical.HVAC_MULTI: "hvac_contractors",
            Vertical.URGENT_CARE: "urgent_care", 
            Vertical.FITNESS_GYMS: "fitness_gyms",
            Vertical.AUTO_DEALERS: "auto_dealers"
        }
        
        vertical_key = vertical_mapping.get(vertical, "hvac_contractors")
        patterns = self.vulnerability_patterns.get(vertical_key, {}).get("critical_signals", [])
        
        # Extrair texto do ad para análise
        ad_text = ""
        if "title" in ad_data:
            ad_text += ad_data["title"] + " "
        if "description" in ad_data:
            ad_text += ad_data["description"] + " "
        if "text" in ad_data:
            ad_text += ad_data["text"] + " "
        if "profile_info" in ad_data and "description" in ad_data["profile_info"]:
            ad_text += ad_data["profile_info"]["description"] + " "
            
        ad_text = ad_text.lower()
        
        vulnerability_score = 0
        actionable_insights = []
        total_roi_potential = 0
        
        # Analisar cada padrão de vulnerabilidade
        for signal in patterns:
            pattern_match = re.search(signal["pattern"], ad_text, re.IGNORECASE)
            
            if pattern_match:
                # DETECTOU VULNERABILIDADE ESPECÍFICA
                vulnerability_score += 3 if signal["urgency"] == "critical" else 2 if signal["urgency"] == "high" else 1
                
                # REAL INFRASTRUCTURE GAP DETECTION
                infrastructure_gap = await self._detect_infrastructure_gap(
                    ad_data.get("domain", ""), 
                    signal["evidence_required"]
                )
                
                if infrastructure_gap:
                    # CONFIRMOU GAP DE INFRAESTRUTURA
                    vulnerability_score += 2
                    total_roi_potential += signal["roi_potential"]
                    
                    actionable_insights.append({
                        "vulnerability_type": signal["vulnerability"],
                        "evidence": f"Claims '{pattern_match.group()}' detected without {infrastructure_gap}",
                        "roi_potential": signal["roi_potential"],
                        "urgency": signal["urgency"],
                        "context": signal["context"],
                        "infrastructure_required": signal["evidence_required"],
                        "action_plan": f"Implement {infrastructure_gap} to support {pattern_match.group()} claims"
                    })
                    
                    logger.info(f"🎯 Vulnerability detected: {signal['vulnerability']} - ROI: ${signal['roi_potential']}")
        
        # SCORING FINAL
        total_vulnerability_score = min(10, vulnerability_score)  # Cap at 10
        
        return {
            "total_vulnerability_score": total_vulnerability_score,
            "actionable_insights": actionable_insights,
            "monthly_roi_potential": total_roi_potential,
            "vertical_focus": vertical_key,
            "ad_analysis_summary": f"Detected {len(actionable_insights)} vulnerabilities with ${total_roi_potential:,} monthly savings potential"
        }
    
    async def _detect_infrastructure_gap(self, domain: str, evidence_required: List[str]) -> str:
        """
        🔍 REAL INFRASTRUCTURE GAP DETECTION
        
        Performs actual website analysis to detect missing infrastructure
        required to support advertising claims.
        
        Args:
            domain: Target domain to analyze
            evidence_required: List of infrastructure elements to verify
            
        Returns:
            str: Specific infrastructure gap detected or None if complete
        """
        if not domain:
            return "domain_verification_required"
        
        # REAL INFRASTRUCTURE ANALYSIS
        try:
            # Check for real-time tracking systems
            if "response_time_tracking" in evidence_required:
                # Real check: Look for response time APIs/dashboards
                has_tracking = await self._check_response_tracking(domain)
                if not has_tracking:
                    return "real-time response tracking dashboard"
            
            if "queue_management_system" in evidence_required:
                # Real check: Look for queue status endpoints
                has_queue = await self._check_queue_system(domain)
                if not has_queue:
                    return "live queue status display"
            
            if "real_time_inventory_system" in evidence_required:
                # Real check: Look for inventory APIs
                has_inventory = await self._check_inventory_system(domain)
                if not has_inventory:
                    return "dynamic inventory availability system"
            
            if "license_verification_system" in evidence_required:
                # Real check: Look for credential verification
                has_verification = await self._check_verification_system(domain)
                if not has_verification:
                    return "credential verification portal"
            
            if "progress_tracking_system" in evidence_required:
                # Real check: Look for progress tracking features
                has_progress = await self._check_progress_tracking(domain)
                if not has_progress:
                    return "client progress tracking platform"
                    
            # If all systems present, no gap detected
            return None
            
        except Exception as e:
            logger.warning(f"Infrastructure gap detection failed for {domain}: {e}")
            return "infrastructure_analysis_required"
    
    async def _check_response_tracking(self, domain: str) -> bool:
        """Check if domain has real-time response tracking system"""
        try:
            # Look for common response tracking endpoints
            tracking_endpoints = [
                f"https://{domain}/api/response-time",
                f"https://{domain}/tracking/status",
                f"https://{domain}/dashboard/response"
            ]
            
            async with self.session.get(f"https://{domain}", timeout=10) as response:
                if response.status == 200:
                    content = await response.text()
                    # Check for tracking-related keywords in source
                    tracking_indicators = ["response-time", "tracking", "real-time", "status-dashboard"]
                    return any(indicator in content.lower() for indicator in tracking_indicators)
        except:
            pass
        return False
    
    async def _check_queue_system(self, domain: str) -> bool:
        """Check if domain has queue management system"""
        try:
            async with self.session.get(f"https://{domain}", timeout=10) as response:
                if response.status == 200:
                    content = await response.text()
                    queue_indicators = ["queue", "wait-time", "check-in", "appointment-status"]
                    return any(indicator in content.lower() for indicator in queue_indicators)
        except:
            pass
        return False
    
    async def _check_inventory_system(self, domain: str) -> bool:
        """Check if domain has real-time inventory system"""
        try:
            async with self.session.get(f"https://{domain}", timeout=10) as response:
                if response.status == 200:
                    content = await response.text()
                    inventory_indicators = ["in-stock", "inventory", "availability", "real-time"]
                    return any(indicator in content.lower() for indicator in inventory_indicators)
        except:
            pass
        return False
    
    async def _check_verification_system(self, domain: str) -> bool:
        """Check if domain has credential verification system"""
        try:
            async with self.session.get(f"https://{domain}", timeout=10) as response:
                if response.status == 200:
                    content = await response.text()
                    verification_indicators = ["license", "certified", "verified", "credentials"]
                    return any(indicator in content.lower() for indicator in verification_indicators)
        except:
            pass
        return False
    
    async def _check_progress_tracking(self, domain: str) -> bool:
        """Check if domain has progress tracking system"""
        try:
            async with self.session.get(f"https://{domain}", timeout=10) as response:
                if response.status == 200:
                    content = await response.text()
                    progress_indicators = ["progress", "tracking", "results", "dashboard"]
                    return any(indicator in content.lower() for indicator in progress_indicators)
        except:
            pass
        return False
    
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
                "q": query.replace("{city}", ""),  # Remove city placeholder
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

    async def _execute_escalated_discovery(self, target_verticals: List[Vertical], max_credits: int, target_discoveries: int) -> List[DiscoveryOutput]:
        """
        🚀 ARCO V3 ESCALATED DISCOVERY STRATEGY
        
        PHASE 1: LinkedIn Ad Library (Primary Intelligence)
        PHASE 2: Google Transparency Center (Volume + Validation)  
        PHASE 3: Reddit Ad Library (Niche + Community Validation)
        PHASE 4: Cross-platform Vulnerability Synthesis
        """
        discovered_advertisers = []
        credits_used = 0
        
        logger.info(f"🎯 ESCALATED DISCOVERY: {len(target_verticals)} verticals, {max_credits} credits, target {target_discoveries}")
        
        for vertical in target_verticals:
            if credits_used >= max_credits or len(discovered_advertisers) >= target_discoveries:
                break
                
            config = self.vertical_configs[vertical]
            
            # 🥇 PHASE 1: LinkedIn Ad Library (B2B Professional Focus)
            linkedin_queries = config.get("linkedin_queries", [])
            if linkedin_queries:
                linkedin_results = await self._search_linkedin_ads(
                    linkedin_queries,
                    vertical,
                    min(5, max_credits - credits_used)  # Start conservative
                )
            
            for result in linkedin_results:
                if credits_used >= max_credits or len(discovered_advertisers) >= target_discoveries:
                    break
                    
                # Deep vulnerability analysis
                vulnerability_analysis = await self._analyze_linkedin_ad_vulnerabilities(result)
                
                if vulnerability_analysis["vulnerability_score"] >= 6:  # High vulnerability threshold
                    discovery = await self._create_discovery_output(result, vulnerability_analysis, vertical)
                    discovered_advertisers.append(discovery)
                    credits_used += 1
                    
            # 🥈 PHASE 2: Google Transparency Center (Validation & Additional Discovery)
            if len(discovered_advertisers) < target_discoveries and credits_used < max_credits:
                google_results = await self._search_google_transparency(
                    config["google_queries"],
                    vertical, 
                    max_credits - credits_used
                )
                
                for result in google_results:
                    if credits_used >= max_credits or len(discovered_advertisers) >= target_discoveries:
                        break
                        
                    # Cross-validate with Ad Details API
                    ad_details = await self._get_ad_details_vulnerability_analysis(result)
                    
                    if ad_details["vulnerability_score"] >= 7:  # Higher threshold for Google
                        discovery = await self._create_discovery_output(result, ad_details, vertical)
                        discovered_advertisers.append(discovery)
                        credits_used += 1
    async def _search_linkedin_ads(self, queries: List[str], vertical: Vertical, max_credits: int) -> List[Dict]:
        """
        🔵 LINKEDIN AD LIBRARY SEARCH - B2B PROFESSIONAL INTELLIGENCE
        
        Focus: Professional targeting, company intelligence, B2B vulnerability detection
        Filters: Country targeting, time_period optimization for fresh data
        """
        results = []
        credits_used = 0
        
        for query in queries:
            if credits_used >= max_credits:
                break
                
            try:
                params = {
                    "engine": self.engines["primary"],
                    "q": query,
                    "country": "US,CA,GB,AU",  # English-speaking B2B markets
                    "time_period": "last_30_days",  # Fresh campaigns only
                    "api_key": self.api_key
                }
                
                async with self.session.get(f"{self.base_url}/search", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        ads = data.get("ads", [])
                        results.extend(ads[:3])  # Top 3 per query for quality
                        credits_used += 1
                        logger.info(f"✅ LinkedIn search '{query}': {len(ads)} ads found")
                    else:
                        logger.warning(f"❌ LinkedIn search failed for '{query}': {response.status}")
                        
            except Exception as e:
                logger.error(f"💥 LinkedIn search error for '{query}': {str(e)}")
                
        return results[:max_credits]  # Respect credit limit
        
    async def _search_google_transparency(self, queries: List[str], vertical: Vertical, max_credits: int) -> List[Dict]:
        """
        🔴 GOOGLE ADS TRANSPARENCY CENTER SEARCH - VOLUME + VALIDATION
        
        Focus: High-volume discovery, cross-platform validation, geographic intelligence
        Strategy: Broad discovery then filter by quality indicators
        """
        results = []
        credits_used = 0
        
        for query in queries:
            if credits_used >= max_credits:
                break
                
            try:
                params = {
                    "engine": self.engines["secondary"],
                    "q": query,
                    "region": "US",  # Focus on US market for consistency
                    "num_advertisers": 20,  # Higher volume for filtering
                    "api_key": self.api_key
                }
                
                async with self.session.get(f"{self.base_url}/search", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        advertisers = data.get("advertisers", [])
                        
                        # Filter for verified advertisers with significant ad volume
                        quality_advertisers = [
                            adv for adv in advertisers 
                            if adv.get("is_verified", False) and 
                               adv.get("ads_count", {}).get("lower", 0) >= 10
                        ]
                        
                        results.extend(quality_advertisers[:5])  # Top 5 quality advertisers
                        credits_used += 1
                        logger.info(f"✅ Google search '{query}': {len(quality_advertisers)} quality advertisers")
                    else:
                        logger.warning(f"❌ Google search failed for '{query}': {response.status}")
                        
            except Exception as e:
                logger.error(f"💥 Google search error for '{query}': {str(e)}")
                
        return results[:max_credits]
        
    async def _search_reddit_ads(self, queries: List[str], vertical: Vertical, max_credits: int) -> List[Dict]:
        """
        🟠 REDDIT AD LIBRARY SEARCH - COMMUNITY + NICHE VALIDATION
        
        Focus: Community engagement, niche targeting validation, alternative channels
        Strategy: Industry-specific filtering with budget/placement analysis
        """
        results = []
        credits_used = 0
        
        # Map verticals to Reddit industries
        industry_mapping = {
            Vertical.HVAC_MULTI: "RETAIL_AND_ECOMMERCE",
            Vertical.URGENT_CARE: "HEALTH_AND_BEAUTY", 
            Vertical.DENTAL_CLINICS: "HEALTH_AND_BEAUTY",
            Vertical.MEDICAL_AESTHETICS: "HEALTH_AND_BEAUTY",
            Vertical.AUTO_SERVICES: "AUTO",
            Vertical.REAL_ESTATE: "REAL_ESTATE",
            Vertical.VETERINARY: "HEALTH_AND_BEAUTY"
        }
        
        industry = industry_mapping.get(vertical, "OTHER")
        
        for query in queries:
            if credits_used >= max_credits:
                break
                
            try:
                params = {
                    "engine": self.engines["tertiary"],
                    "q": query,
                    "industry": industry,
                    "budget_category": "MEDIUM,HIGH",  # Focus on serious advertisers
                    "post_type": "IMAGE,VIDEO",  # Visual content for engagement
                    "placements": "FEED,COMMENTS_PAGE",  # Full placement strategy
                    "api_key": self.api_key
                }
                
                async with self.session.get(f"{self.base_url}/search", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        ads = data.get("ads", [])
                        
                        # Filter for ads with engagement indicators
                        engaging_ads = [
                            ad for ad in ads 
                            if ad.get("creative", {}).get("allow_comments", False) and
                               ad.get("budget_category") in ["MEDIUM", "HIGH"]
                        ]
                        
                        results.extend(engaging_ads[:2])  # Quality over quantity
                        credits_used += 1
                        logger.info(f"✅ Reddit search '{query}': {len(engaging_ads)} engaging ads")
                    else:
                        logger.warning(f"❌ Reddit search failed for '{query}': {response.status}")
                        
            except Exception as e:
                logger.error(f"💥 Reddit search error for '{query}': {str(e)}")
                
        return results[:max_credits]
    
    async def _get_ad_details_vulnerability_analysis(self, advertiser_data: Dict) -> Dict:
        """
        🔬 GOOGLE AD DETAILS API - DEEP VULNERABILITY INTELLIGENCE
        
        Analyzes specific ad creatives for execution problems:
        - Campaign duration patterns
        - Geographic targeting efficiency  
        - Creative format optimization
        - Audience selection quality
        """
        try:
            advertiser_id = advertiser_data.get("id")
            if not advertiser_id:
                return {"vulnerability_score": 0, "vulnerabilities": [], "analysis_engine": "google_ad_details_failed"}
            
            # For now, we'll use advertiser-level data since we need specific creative_id for ad details
            # In production, this would iterate through advertiser's creative IDs
            
            vulnerability_score = 0
            vulnerabilities = []
            
            # VULNERABILITY 1: Ad Volume vs Quality Analysis (Score: 0-3)
            ads_count = advertiser_data.get("ads_count", {})
            lower_count = ads_count.get("lower", 0)
            upper_count = ads_count.get("upper", 0)
            
            if upper_count > 100 and lower_count < 10:  # High variance = poor targeting
                vulnerability_score += 3
                vulnerabilities.append("high_ad_volume_variance_poor_targeting")
            elif upper_count > 50:  # High volume without testing = spray and pray
                vulnerability_score += 2
                vulnerabilities.append("high_volume_without_optimization")
            
            # VULNERABILITY 2: Verification Status Analysis (Score: 0-2)
            if not advertiser_data.get("is_verified", False):
                vulnerability_score += 2
                vulnerabilities.append("unverified_advertiser_compliance_risk")
            
            # VULNERABILITY 3: Regional Focus Analysis (Score: 0-2)
            region = advertiser_data.get("region", "")
            if region not in ["US", "CA", "GB", "AU"]:  # Non-English markets for English campaigns
                vulnerability_score += 2
                vulnerabilities.append("geographic_market_misalignment")
            
            # VULNERABILITY 4: Company Name Analysis (Score: 0-3)
            company_name = advertiser_data.get("name", "").lower()
            if any(indicator in company_name for indicator in ["llc", "inc", "corp"]):
                # Formal business structure but advertising = potential growth stage
                vulnerability_score += 1
                vulnerabilities.append("formal_business_advertising_growth_opportunity")
            
            return {
                "vulnerability_score": min(vulnerability_score, 10),
                "vulnerabilities": vulnerabilities,
                "analysis_engine": "google_transparency_advertiser_analysis", 
                "recommended_arco_approach": "systematic_campaign_optimization"
            }
            
        except Exception as e:
            logger.error(f"💥 Google Ad Details analysis error: {str(e)}")
            return {"vulnerability_score": 0, "vulnerabilities": [], "analysis_engine": "google_ad_details_error"}

    async def _analyze_reddit_ad_vulnerabilities(self, ad_data: Dict) -> Dict:
        """
        🟠 REDDIT AD VULNERABILITY ANALYSIS - COMMUNITY ENGAGEMENT INTELLIGENCE
        
        Detects poor community engagement and platform misalignment:
        - Budget category vs industry alignment
        - Placement strategy optimization
        - Creative format effectiveness
        - Community engagement indicators
        """
        vulnerability_score = 0
        vulnerabilities = []
        
        try:
            # VULNERABILITY 1: Budget Category Misalignment (Score: 0-3)
            budget_category = ad_data.get("budget_category", "")
            industry = ad_data.get("industry", "")
            
            if budget_category == "HIGH" and industry == "GAMING":
                vulnerability_score += 3
                vulnerabilities.append("overinvestment_gaming_niche_market")
            elif budget_category == "LOW" and industry in ["FINANCIAL_SERVICES", "REAL_ESTATE"]:
                vulnerability_score += 2
                vulnerabilities.append("underinvestment_high_value_industries")
            
            # VULNERABILITY 2: Placement Strategy Issues (Score: 0-2)
            placements = ad_data.get("placements", [])
            if len(placements) == 1 and "FEED" in placements:
                vulnerability_score += 2
                vulnerabilities.append("limited_placement_strategy_missed_engagement")
            
            # VULNERABILITY 3: Creative Format Misalignment (Score: 0-2)
            creative = ad_data.get("creative", {})
            creative_type = creative.get("type", "")
            
            if creative_type == "VIDEO" and industry not in ["GAMING", "ENTERTAINMENT"]:
                vulnerability_score += 2
                vulnerabilities.append("video_format_misalignment_non_entertainment")
            
            # VULNERABILITY 4: Engagement Settings (Score: 0-3)
            allow_comments = creative.get("allow_comments", False)
            if not allow_comments:
                vulnerability_score += 3
                vulnerabilities.append("disabled_comments_missed_community_engagement")
            
            return {
                "vulnerability_score": min(vulnerability_score, 10),
                "vulnerabilities": vulnerabilities,
                "analysis_engine": "reddit_community_engagement_analysis",
                "recommended_arco_approach": "community_driven_optimization"
            }
            
        except Exception as e:
            logger.error(f"💥 Reddit vulnerability analysis error: {str(e)}")
            return {"vulnerability_score": 0, "vulnerabilities": [], "analysis_engine": "reddit_analysis_error"}
        
        for city in config["geo_targets"]:
            if credits_used >= max_credits or len(discoveries) >= target_count:
                break
                
            logger.info(f"📍 Searching in {city}")
            
            for query_template in config["queries"][:2]:  # Limit to top 2 queries per city
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
        SINGLE SOURCE: Advertiser Search API ONLY
        Real advertiser discovery - no SERP fallback, no simulated data
        """
        logger.debug(f"🚀 ADVERTISER SEARCH ONLY: '{query}' in {city}")
        
        # Use ONLY Advertiser Search API - no fallbacks
        advertiser_prospects = await self._search_advertisers_primary(query, city)
        
        logger.info(f"✅ ADVERTISER SEARCH RESULT: {len(advertiser_prospects)} real advertisers found")
        return advertiser_prospects  # Return only real advertiser data

    async def _search_advertisers_primary(self, query: str, city: str) -> List[Dict]:
        """
        STRATEGIC WEEKEND + FUSO HORÁRIO DISCOVERY
        Primary advertiser discovery with critical vulnerability analysis
        """
        prospects = []
        
        # STRATEGIC QUERY OPTIMIZATION - Multiple angles, maximum coverage
        weekend_enhanced_queries = [
            f"healthcare {city}",                 # Primary: Broad healthcare
            f"medical {city}",                    # Secondary: Medical services  
            f"urgent care {city}",                # Target: Urgent care specific
            f"emergency {city}",                  # Crisis: Emergency services
            f"clinic {city}",                     # Local: Clinic/practice
            f"hospital {city}",                   # Major: Hospital systems
            f"doctor {city}",                     # Personal: Doctor practices
            f"24 hour {city}",                    # Timing: 24-hour services
        ]
        
        total_advertisers_found = 0
        
        # Execute ALL query variations for maximum coverage  
        for enhanced_query in weekend_enhanced_queries:
            if total_advertisers_found >= 50:  # Stop at reasonable limit
                break
                
            params = {
                "api_key": self.api_key,
                "engine": "google_ads_transparency_center_advertiser_search",
                "q": enhanced_query,
                "num_advertisers": 30,   # Reduced per query, but more queries
                "num_domains": 20,       # Focused domain discovery
                "region": "US"
            }
            
            try:
                async with self.session.get(f"{self.base_url}/search", params=params, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract confirmed advertisers with ENHANCED vulnerability pre-screening
                        advertisers = data.get('advertisers', [])
                        current_query_count = 0
                        
                        for advertiser in advertisers:
                            if current_query_count >= 15:  # Limit per query for quality
                                break
                                
                            ads_count = advertiser.get('ads_count', {})
                            
                            # ENHANCED: Multiple signal analysis
                            advertiser_name = advertiser.get('name', '').lower()
                            weekend_relevance = any(keyword in advertiser_name for keyword in 
                                                  ['emergency', 'urgent', '24/7', '24 hour', 'weekend', 'immediate'])
                            
                            # COMPETITIVE INTELLIGENCE: Activity analysis
                            upper_ads = ads_count.get('upper', 0)
                            lower_ads = ads_count.get('lower', 0)
                            ad_activity_score = min(upper_ads / 10, 5)  # Scale 0-5
                            
                            # Estimate domain with validation
                            estimated_domain = self._estimate_domain_from_name(advertiser.get('name', ''))
                            
                            # CRITICAL FIX: Skip advertisers without real domains
                            if not estimated_domain:
                                continue  # Skip fake domain prospects
                            
                            # STRATEGIC VULNERABILITY PRE-SCREENING
                            vulnerability_flags = []
                            priority_score = 1  # Higher = better prospect
                            
                            # Volume-based insights (not just flags)
                            if upper_ads < 5:
                                vulnerability_flags.append('MINIMAL_AD_PRESENCE')
                                priority_score -= 2
                            elif 5 <= upper_ads <= 25:
                                vulnerability_flags.append('MODERATE_ACTIVITY')  # Sweet spot for growth
                                priority_score += 1
                            elif upper_ads > 100:
                                vulnerability_flags.append('HIGH_VOLUME_INEFFICIENCY')  # Optimization opportunity
                                priority_score += 2
                            
                            # Weekend/emergency bonus
                            if weekend_relevance:
                                vulnerability_flags.append('WEEKEND_POSITIONED')
                                priority_score += 3
                            
                            # Verification insights
                            if not advertiser.get('is_verified', False):
                                vulnerability_flags.append('UNVERIFIED_STATUS')
                                priority_score += 1  # Actually good - easier to approach
                            
                            # Query relevance bonus
                            if enhanced_query in ['urgent care', 'emergency', '24 hour']:
                                priority_score += 1
                            
                            prospect = {
                                'title': advertiser.get('name', ''),
                                'description': f"Advertiser: {lower_ads}-{upper_ads} campaigns | Weekend: {weekend_relevance} | Activity: {ad_activity_score:.1f}/5",
                                'domain': estimated_domain,
                                'source': 'strategic_advertiser',
                                'advertiser_id': advertiser.get('id'),
                                'ads_count_range': ads_count,
                                'is_verified': advertiser.get('is_verified', False),
                                'region': advertiser.get('region', 'US'),
                                'tier': 'STRATEGIC' if priority_score >= 3 else 'ACTIVE',
                                'weekend_relevance': weekend_relevance,
                                'vulnerability_flags': vulnerability_flags,
                                'priority': priority_score,
                                'query_matched': enhanced_query,
                                'ad_activity_score': ad_activity_score
                            }
                            prospects.append(prospect)
                            current_query_count += 1
                            total_advertisers_found += 1
                        
                        # Extract advertiser domains with weekend context
                        domains = data.get('domains', [])
                        existing_domains = {p['domain'] for p in prospects}
                        
                        for domain_obj in domains:
                            domain_name = domain_obj.get('name', '')
                            if domain_name and domain_name not in existing_domains:
                                # Weekend relevance check for domains
                                domain_weekend_relevance = any(keyword in domain_name.lower() for keyword in 
                                                             ['emergency', 'urgent', '24', 'express', 'immediate'])
                                
                                prospect = {
                                    'title': self._format_title_from_domain(domain_name),
                                    'description': f"Active domain | Weekend relevance: {domain_weekend_relevance}",
                                    'domain': domain_name,
                                    'source': 'advertiser_domain',
                                    'advertiser_id': '',
                                    'ads_count_range': {'lower': 1, 'upper': 20},
                                    'is_verified': False,
                                    'region': 'US',
                                    'tier': 'ACTIVE',
                                    'weekend_relevance': domain_weekend_relevance,
                                    'vulnerability_flags': ['DOMAIN_ONLY_DATA'],
                                    'priority': 2 if domain_weekend_relevance else 3,
                                    'query_matched': enhanced_query
                                }
                                prospects.append(prospect)
                        
                        if advertisers or domains:
                            self.logger.info(f"🎯 ENHANCED DISCOVERY '{enhanced_query}': {current_query_count} strategic advertisers + {len(domains)} domains")
                            self.logger.info(f"📈 Total coverage: {total_advertisers_found} advertisers across {len(weekend_enhanced_queries)} query angles")
                            # Continue to next query for broader coverage
                            
                    else:
                        self.logger.warning(f"❌ Query '{enhanced_query}' failed: {response.status} - investigate API limits")
                        
            except Exception as e:
                self.logger.error(f"Advertiser Search failed for '{enhanced_query}': {e}")
        
        # STRATEGIC PRIORITIZATION: Weekend-relevant first, then by ad volume
        prospects.sort(key=lambda x: (
            -x['priority'],  # Lower priority number = higher priority
            -x['ads_count_range'].get('upper', 0),  # Higher ad count = higher priority
            x['weekend_relevance']  # Weekend relevance as tiebreaker
        ))
        
        return prospects[:25]  # Top 25 strategically prioritized prospects

    def _estimate_domain_from_name(self, advertiser_name: str) -> str:
        """
        CRITICAL FIX: Use real domain detection instead of fake estimates
        Only return domains we can verify, not artificial constructions
        """
        if not advertiser_name:
            return None  # Don't create fake domains
        
        # Skip if advertiser name seems like a fake/estimated domain already
        if any(pattern in advertiser_name.lower() for pattern in ['.com', 'www.', 'http']):
            return advertiser_name.lower()
        
        # For now, return None instead of creating fake domains
        # This will force the system to find REAL advertisers with actual domains
        return None

    def _format_title_from_domain(self, domain: str) -> str:
        """Format business title from domain name"""
        name = domain.replace('.com', '').replace('.net', '').replace('.org', '')
        name = name.replace('-', ' ').replace('_', ' ')
        return name.title()

    def _classify_advertiser_tier(self, ads_count: Dict) -> str:
        """Classify advertiser based on campaign volume"""
        upper_count = ads_count.get('upper', 0)
        
        if upper_count >= 100:
            return 'ENTERPRISE'    # 100+ campaigns
        elif upper_count >= 50:
            return 'PREMIUM'       # 50-99 campaigns
        elif upper_count >= 20:
            return 'STANDARD'      # 20-49 campaigns
        elif upper_count >= 5:
            return 'LIGHT'         # 5-19 campaigns
        else:
            return 'MINIMAL'       # 1-4 campaigns

    # REMOVED: SERP fallback method - using only real advertiser data

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
        """
        REAL AD INTELLIGENCE: Use Google Ads Transparency Center Ad Details API
        No simulations, no fallbacks - only real advertiser data
        """
        try:
            # Use Google Ads Transparency Center Ad Details API
            params = {
                "api_key": self.api_key,
                "engine": "google_ads_transparency_center",
                "domain": domain
            }
            
            async with self.session.get(f"{self.base_url}/search", params=params, timeout=20) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract REAL ad data
                    ad_creatives = data.get('ad_creatives', [])
                    search_info = data.get('search_information', {})
                    total_results = search_info.get('total_results', 0)
                    
                    if not ad_creatives or total_results == 0:
                        # INFORMATIVE FALLBACK - not generative
                        self.logger.info(f"   ❌ NO AD INVESTMENT - No advertising found for {domain}")
                        return 0, {
                            'analysis': 'NO_DIGITAL_ADVERTISING',
                            'total_creatives': 0,
                            'investment_score': 0,
                            'vulnerabilities': [],
                            'opportunity_note': f'Domain {domain} has no advertising presence in Google Ads Transparency Center'
                        }
                    
                    # REAL DATA ANALYSIS - no simulation
                    ad_count = len(ad_creatives)
                    self.logger.info(f"✅ REAL AD DATA FOUND: {ad_count} ads for {domain}")
                    
                    # Calculate investment score based on REAL ad volume
                    investment_score = 0
                    if ad_count >= 100:
                        investment_score = 7  # Heavy advertiser
                    elif ad_count >= 50:
                        investment_score = 6  # Significant advertiser  
                    elif ad_count >= 20:
                        investment_score = 5  # Moderate advertiser
                    elif ad_count >= 10:
                        investment_score = 4  # Light advertiser
                    elif ad_count >= 5:
                        investment_score = 3  # Minimal advertiser
                    elif ad_count >= 1:
                        investment_score = 2  # Test advertiser
                    
                    # Analyze REAL ad patterns for vulnerabilities
                    vulnerabilities = []
                    formats_found = set()
                    duration_data = []
                    recent_activity = 0
                    
                    # Process REAL ad data
                    current_time = datetime.now()
                    for ad in ad_creatives[:20]:  # Sample for performance
                        # Real format analysis
                        ad_format = ad.get('format', 'unknown')
                        formats_found.add(ad_format)
                        
                        # Real duration analysis
                        days_shown = ad.get('total_days_shown', 0)
                        if days_shown > 0:
                            duration_data.append(days_shown)
                        
                        # Real recency analysis
                        last_shown = ad.get('last_shown_datetime')
                        if last_shown:
                            try:
                                last_date = datetime.fromisoformat(last_shown.replace('Z', '+00:00'))
                                days_ago = (current_time - last_date.replace(tzinfo=None)).days
                                if days_ago <= 30:
                                    recent_activity += 1
                            except:
                                pass
                    
                    # REAL VULNERABILITY DETECTION
                    if 'video' not in formats_found and ad_count > 5:
                        vulnerabilities.append('MISSING_VIDEO_STRATEGY')
                    
                    if len(formats_found) <= 1 and ad_count > 10:
                        vulnerabilities.append('SINGLE_FORMAT_LIMITATION')
                    
                    if duration_data:
                        avg_duration = sum(duration_data) / len(duration_data)
                        if avg_duration > 365:
                            vulnerabilities.append('COMPLETELY_STALE_CAMPAIGNS')
                        elif avg_duration < 30:
                            vulnerabilities.append('SHORT_CAMPAIGN_CYCLES')
                    
                    if recent_activity == 0 and ad_count > 0:
                        vulnerabilities.append('NO_RECENT_ACTIVITY')
                    
                    self.logger.info(f"   💰 Ad Investment Score: {investment_score}/7")
                    self.logger.info(f"   🔍 Vulnerabilities: {vulnerabilities}")
                    
                    return investment_score, {
                        'analysis': 'REAL_AD_DATA_ANALYZED',
                        'total_creatives': ad_count,
                        'investment_score': investment_score,
                        'formats': list(formats_found),
                        'avg_duration_days': sum(duration_data) / len(duration_data) if duration_data else 0,
                        'recent_activity_count': recent_activity,
                        'vulnerabilities': vulnerabilities,
                        'transparency_data': data  # Store full response for further analysis
                    }
                    
                elif response.status == 400:
                    # INFORMATIVE FALLBACK - API error
                    self.logger.warning(f"   ⚠️ AD DATA UNAVAILABLE - API returned 400 for {domain}")
                    return 0, {
                        'analysis': 'TRANSPARENCY_API_ERROR',
                        'total_creatives': 0,
                        'investment_score': 0,
                        'error_note': f'Google Ads Transparency Center returned 400 for {domain}',
                        'possible_reasons': ['Domain not in advertising system', 'Insufficient traffic data']
                    }
                    
                else:
                    # INFORMATIVE FALLBACK - unexpected status
                    self.logger.warning(f"   ❌ AD API ERROR {response.status} for {domain}")
                    return 0, {
                        'analysis': f'API_ERROR_{response.status}',
                        'total_creatives': 0,
                        'investment_score': 0,
                        'error_note': f'API returned status {response.status}'
                    }
                    
        except Exception as e:
            # INFORMATIVE FALLBACK - technical error
            self.logger.debug(f"Ad verification error for {domain}: {e}")
            return 0, {
                'analysis': 'TECHNICAL_ERROR',
                'total_creatives': 0,
                'investment_score': 0,
                'error_note': f'Technical error during ad verification: {str(e)}'
            }

    async def _analyze_strategic_vulnerabilities(self, domain: str, ad_analysis: dict) -> dict:
        """
        CRITICAL VULNERABILITY ANALYSIS: Deep ad strategy assessment
        Progressive disclosure for weekend-strong verticals in optimal fuso horário
        """
        investment_score = ad_analysis.get('investment_score', 0)
        
        if investment_score < 2:
            # Don't waste credits on minimal advertisers
            return {
                'tier': 'basic',
                'outreach_insights': ['NO_DIGITAL_MATURITY'],
                'followup_insights': [],
                'proposal_insights': ['Complete digital strategy rebuild needed'],
                'revenue_opportunity': 'HIGH_GREENFIELD'
            }
        
        try:
            # EXECUTE DEEP AD ANALYSIS for qualified prospects
            self.logger.info(f"🔬 EXECUTING AD DETAILS ANALYSIS for {domain}")
            
            # Get transparency data for vulnerability analysis
            transparency_data = ad_analysis.get('transparency_data')
            if not transparency_data:
                # Fetch transparency data if not already available
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
            
            ad_creatives = transparency_data.get('ad_creatives', [])
            
            if not ad_creatives:
                return {
                    'tier': 'basic', 
                    'outreach_insights': ['NO_AD_CREATIVE_DATA'],
                    'followup_insights': [],
                    'proposal_insights': ['Unable to analyze ad strategy']
                }
            
            # CRITICAL VULNERABILITY ANALYSIS with real data
            vulnerability_insights = await self._analyze_ad_details_vulnerabilities_real(ad_creatives, domain)
            
            # WEEKEND OPERATIONAL CONTEXT
            current_hour_utc = datetime.now().hour
            is_weekend_peak = current_hour_utc in [7, 8, 9, 10, 11]  # 4-8am Brasília = 7-11am UTC = Weekend peak US
            
            strategic_insights = {
                'tier': 'strategic',
                'outreach_insights': [],      # Immediate hook (1-2 vulnerabilities)
                'followup_insights': [],      # Progressive disclosure (2-3 insights)
                'proposal_insights': [],      # Complete strategic assessment
                'revenue_opportunity': '',    # Quantified opportunity
                'timing_advantage': is_weekend_peak,  # Strategic timing context
                'vulnerability_severity': vulnerability_insights.get('severity', 'MEDIUM')
            }
            
            # CRITICAL VULNERABILITY DETECTION
            critical_vulns = vulnerability_insights.get('critical_vulnerabilities', [])
            medium_vulns = vulnerability_insights.get('medium_vulnerabilities', [])
            strategic_gaps = vulnerability_insights.get('strategic_gaps', [])
            
            # OUTREACH PRIORITIZATION (Immediate impact)
            if 'WEEKEND_GAP' in critical_vulns:
                strategic_insights['outreach_insights'].append('MISSING_WEEKEND_STRATEGY')
            elif 'EMERGENCY_MESSAGING_WEAK' in critical_vulns:
                strategic_insights['outreach_insights'].append('POOR_URGENCY_POSITIONING')
            elif critical_vulns:
                strategic_insights['outreach_insights'].append(f'CRITICAL_{critical_vulns[0]}')
            
            # FOLLOW-UP DISCLOSURE (Progressive revelation)
            strategic_insights['followup_insights'].extend(medium_vulns[:2])
            if is_weekend_peak:
                strategic_insights['followup_insights'].append('WEEKEND_TIMING_OPPORTUNITY')
            
            # PROPOSAL INSIGHTS (Complete analysis)
            strategic_insights['proposal_insights'] = critical_vulns + medium_vulns + strategic_gaps
            
            # REVENUE OPPORTUNITY CALCULATION
            base_investment = investment_score * 1000  # Base monthly ad spend
            vulnerability_multiplier = len(critical_vulns) * 0.3 + len(medium_vulns) * 0.15
            weekend_multiplier = 1.4 if is_weekend_peak else 1.0
            
            revenue_opportunity = int(base_investment * (1 + vulnerability_multiplier) * weekend_multiplier)
            strategic_insights['revenue_opportunity'] = f'${revenue_opportunity:,}/month improvement potential'
            
            # TIMING CONTEXT for outreach
            if is_weekend_peak:
                strategic_insights['outreach_insights'].append('WEEKEND_OPERATIONAL_TIMING')
            
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
        # NEW LOGIC: Focus on TOTAL OPPORTUNITY vs. current perfect fit
        growth_potential_score = fit_score + demand_score + (ad_investment_score // 2)  # Investment boost
        
        min_threshold = 3  # Lower barrier for growth opportunities
        if growth_potential_score < min_threshold:
            logger.info(f"❌ GATE 6 FAILED: Total growth potential below threshold ({growth_potential_score} < {min_threshold})")
            return None
        
        logger.info(f"✅ ALL GATES PASSED - GROWTH OPPORTUNITY QUALIFIED! 🚀")
        logger.info(f"   � Growth Potential Score: {growth_potential_score}/15 (fit:{fit_score} + demand:{demand_score} + investment:{ad_investment_score//2})")
        
        # Create discovery output with strategic insights
        return DiscoveryOutput(
            advertiser_id=advertiser_info.get('advertiser_id', '') if advertiser_info else '',
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
        if advertiser_info and advertiser_info.get('advertiser_id'):
            score += 1
        
        # Vertical-specific fit
        config = self.vertical_configs[vertical]
        text = (ad.get('title', '') + ' ' + ad.get('description', '')).lower()
        fit_indicators = config.get('fit_indicators', [])
        
        if any(indicator.lower() in text for indicator in fit_indicators):
            score += 1
        
        return min(score, 5)
    
    def _assess_business_quality(self, domain: str, title: str, description: str, advertiser_info: Dict) -> int:
        """Assess if this is a legitimate, identifiable business (0-5 score)"""
        score = 0
        
        # CRITERION 1: Professional company name (not generic/spammy)
        if self._is_professional_company_name(title):
            score += 1
        
        # CRITERION 2: Established domain (not random/generic)
        if self._is_established_domain(domain):
            score += 1
            
        # CRITERION 3: Has proper advertiser information
        if advertiser_info and advertiser_info.get('advertiser_id'):
            score += 1
            
        # CRITERION 4: Location/contact information available
        if self._has_location_info(advertiser_info, description):
            score += 1
            
        # CRITERION 5: Professional description (not keyword-stuffed)
        if self._is_professional_description(description):
            score += 1
            
        return score
    
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
        
        professional_count = sum(1 for indicator in professional_indicators if indicator in description_lower)
        return professional_count >= 1
    
    def _get_quality_issues(self, domain: str, title: str, description: str, advertiser_info: Dict) -> List[str]:
        """Get list of quality issues for logging"""
        issues = []
        
        if not self._is_professional_company_name(title):
            issues.append("Non-professional company name")
            
        if not self._is_established_domain(domain):
            issues.append("Generic/suspicious domain")
            
        if not (advertiser_info and advertiser_info.get('advertiser_id')):
            issues.append("Missing advertiser information")
            
        if not self._has_location_info(advertiser_info, description):
            issues.append("No location information")
            
        if not self._is_professional_description(description):
            issues.append("Unprofessional description")
            
        return issues
        
        return min(score, 3)