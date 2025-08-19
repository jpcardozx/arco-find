"""
ARCO SearchAPI - Layer 2: Advertiser Consolidation Engine (S-tier Async)
========================================================

Engine 2: google_ads_transparency_center
- Consolida dados de anunciantes específicos por advertiser_id 
- Usa async aiohttp para performance otimizada
- Filtra por atividade recente e volume útil
- Qualifica prospects para Layer 3

Input: advertiser_ids do Layer 1
Output: anunciantes qualificados com métricas de atividade
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Set
import logging
from pathlib import Path

from ..config.arco_config_simple import get_config, get_api_key


class SearchAPILayer2AdvertiserConsolidation:
    """
    S-tier async Layer 2 engine for advertiser consolidation using SearchAPI
    Google Ads Transparency Center API for detailed advertiser information
    """
    
    def __init__(self):
        self.config = get_config()
        self.api_key = get_api_key()
        self.base_url = self.config.searchapi.base_url
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Rate limiting
        self.semaphore = asyncio.Semaphore(3)  # Max 3 concurrent requests
        
        # Qualification thresholds
        self.min_ads_count = 5
        self.max_ads_count = 100
        self.min_quality_score = 0.6
        self.target_regions = ["IE", "GB", "MT", "CY", "US", "CA", "AU"]  # Anglophone focus
        
        # Excluded domains (big franchises, marketplaces)
        self.excluded_domains = {
            "google.com", "facebook.com", "instagram.com", "youtube.com",
            "rightmove.co.uk", "zoopla.co.uk", "daft.ie", "myhome.ie"
        }
    
    async def _make_search_request(self, params: Dict[str, any]) -> Optional[Dict[str, any]]:
        """Make async request to SearchAPI Google Ads Transparency Center"""
        
        search_params = {
            "engine": "google_ads_transparency_center",
            "api_key": self.api_key,
            **params
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.base_url, params=search_params, timeout=30) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"API Error {response.status}: {await response.text()}")
                        return None
                        
            except Exception as e:
                self.logger.error(f"Request failed: {str(e)}")
                return None
    
    async def consolidate_advertiser_info(self, advertiser_id: str, advertiser_name: str, region: str, domain: str = None) -> Optional[Dict[str, any]]:
        """
        Consolidate detailed information for a specific advertiser using SearchAPI
        """
        async with self.semaphore:
            self.logger.info(f"[CONSOLIDATE] {advertiser_name} ({advertiser_id}) in {region}")
            
            # First try with domain if available (and short enough)
            if domain and len(domain) <= 30:
                params = {
                    "domain": domain,
                    "gl": region.lower()
                }
                
                result = await self._make_search_request(params)
                
                if result and result.get("ad_creatives"):
                    processed_data = self._process_advertiser_data(result, advertiser_id, advertiser_name, region, domain)
                    if processed_data:
                        self.logger.info(f"[SUCCESS] {advertiser_name}: {processed_data.get('total_campaigns', 0)} campaigns, score {processed_data.get('quality_score', 0):.2f}")
                    return processed_data
            
            # If domain search failed or no domain, this API doesn't support advertiser_id directly
            # So we return None for now (could implement fallback to advertiser search engine)
            self.logger.warning(f"[SKIP] No valid domain or ads found for {advertiser_name}")
            return None
    
    def _process_advertiser_data(self, api_result: Dict[str, any], advertiser_id: str, advertiser_name: str, region: str, domain: str = None) -> Optional[Dict[str, any]]:
        """Process API result into structured advertiser data"""
        
        try:
            # Extract key information from API response
            search_info = api_result.get("search_information", {})
            ad_creatives = api_result.get("ad_creatives", [])
            
            if not ad_creatives:
                return None
            
            # Calculate metrics
            total_campaigns = len(ad_creatives)
            
            # Extract domains and websites
            websites = set()
            formats = set()
            advertisers_found = set()
            creative_ids = []
            
            for creative in ad_creatives:
                # Extract target domain
                if creative.get("target_domain"):
                    websites.add(creative["target_domain"])
                
                # Format type
                if creative.get("format"):
                    formats.add(creative["format"])
                
                # Advertiser info
                if creative.get("advertiser"):
                    advertisers_found.add(creative["advertiser"].get("name", ""))
                
                # Creative IDs for Layer 3
                if creative.get("id"):
                    creative_ids.append(creative["id"])
            
            # Calculate active campaigns (ads shown recently)
            from datetime import datetime, timedelta
            recent_cutoff = datetime.now() - timedelta(days=90)  # 90 days ago
            
            active_campaigns = 0
            for creative in ad_creatives:
                if creative.get("last_shown_datetime"):
                    try:
                        last_shown = datetime.fromisoformat(creative["last_shown_datetime"].replace('Z', '+00:00'))
                        if last_shown > recent_cutoff:
                            active_campaigns += 1
                    except:
                        pass  # Skip if date parsing fails
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(
                total_campaigns, active_campaigns, len(websites), region, advertiser_name
            )
            
            # Determine if qualified for Layer 3
            is_qualified = (
                total_campaigns >= self.min_ads_count and
                total_campaigns <= self.max_ads_count and
                quality_score >= self.min_quality_score and
                region in self.target_regions
            )
            
            return {
                "advertiser_id": advertiser_id,
                "advertiser_name": advertiser_name,
                "region": region,
                "domain_searched": domain,
                "total_campaigns": total_campaigns,
                "active_campaigns": active_campaigns,
                "websites": list(websites)[:5],  # Limit to top 5
                "ad_formats": list(formats),
                "advertisers_found": list(advertisers_found),
                "creative_ids": creative_ids[:10],  # For Layer 3
                "quality_score": quality_score,
                "is_qualified": is_qualified,
                "recommended_for_layer3": is_qualified and quality_score > 0.8,
                "consolidation_timestamp": datetime.now().isoformat(),
                "api_response_sample": {
                    "search_info": search_info,
                    "total_creatives_found": len(ad_creatives),
                    "sample_creatives": ad_creatives[:2]  # Keep 2 samples for reference
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error processing advertiser {advertiser_name}: {str(e)}")
            return None
    
    def _calculate_quality_score(self, total_campaigns: int, active_campaigns: int, 
                               unique_websites: int, region: str, advertiser_name: str) -> float:
        """Calculate quality score for advertiser"""
        
        score = 0.0
        
        # Campaign volume score (0-0.4) - sweet spot 10-50 campaigns
        if 10 <= total_campaigns <= 50:
            score += 0.4
        elif 5 <= total_campaigns <= 100:
            score += 0.3
        elif total_campaigns > 0:
            score += 0.2
        
        # Activity score (0-0.3)
        if total_campaigns > 0:
            activity_ratio = active_campaigns / total_campaigns
            score += activity_ratio * 0.3
        
        # Website diversity score (0-0.2) - indicates real business vs spam
        if unique_websites >= 2:
            score += 0.2
        elif unique_websites >= 1:
            score += 0.1
        
        # Region priority score (0-0.1)
        if region in ["GB", "IE"]:
            score += 0.1  # Primary Europa targets
        elif region in ["MT", "CY"]:
            score += 0.08  # Secondary Europa targets
        elif region in ["US", "CA", "AU"]:
            score += 0.05  # Anglophone alternatives
        
        return min(score, 1.0)
    
    async def process_layer1_seeds(self, layer1_data: Dict[str, any]) -> Dict[str, any]:
        """
        Process Layer 1 seeds and consolidate advertiser information using domains
        """
        self.logger.info("[START] Layer 2 Advertiser Consolidation - Real SearchAPI calls using domains")
        
        # Extract domains from Layer 1 - these are what we'll search for
        domains_to_search = []
        
        # Get aggregated domains from Layer 1
        aggregated_domains = layer1_data.get("aggregated_domains", [])
        
        for domain_entry in aggregated_domains:
            if isinstance(domain_entry, str):
                # Handle different formats
                if domain_entry.startswith("{'name': '") and domain_entry.endswith("'}"):
                    # Extract domain from string format "{'name': 'domain.com'}"
                    domain = domain_entry.split("'")[3]
                else:
                    domain = domain_entry
                
                # Filter domains by length (API limit) and relevance
                if len(domain) <= 30 and any(keyword in domain.lower() for keyword in 
                    ['property', 'estate', 'agent', 'real', 'home', 'house', 'rent', 'manage']):
                    domains_to_search.append(domain)
        
        # Limit to top 15 domains for cost control
        domains_to_search = domains_to_search[:15]
        
        self.logger.info(f"[PROCESSING] {len(domains_to_search)} relevant domains from Layer 1")
        
        # Create async tasks for domain-based consolidation
        tasks = []
        
        for domain in domains_to_search:
            # Create a synthetic advertiser entry for domain-based search
            task = self.consolidate_advertiser_info(
                advertiser_id=f"DOMAIN_{domain}",
                advertiser_name=f"Advertiser for {domain}",
                region="GB",  # Default to GB for Europa strategy
                domain=domain
            )
            tasks.append((domain, task))
        
        # Execute consolidation with rate limiting
        self.logger.info(f"[EXECUTING] {len(tasks)} async domain consolidation requests")
        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        # Process results
        qualified_advertisers = []
        failed_consolidations = []
        
        for i, result in enumerate(results):
            domain = tasks[i][0]
            if isinstance(result, Exception):
                failed_consolidations.append({
                    "domain": domain,
                    "error": str(result)
                })
            elif result:
                qualified_advertisers.append(result)
        
        # Filter and sort qualified advertisers
        high_quality = [adv for adv in qualified_advertisers if adv["recommended_for_layer3"]]
        medium_quality = [adv for adv in qualified_advertisers if adv["is_qualified"] and not adv["recommended_for_layer3"]]
        
        # Sort by quality score
        high_quality.sort(key=lambda x: x["quality_score"], reverse=True)
        medium_quality.sort(key=lambda x: x["quality_score"], reverse=True)
        
        layer2_results = {
            "timestamp": datetime.now().isoformat(),
            "input_domains": len(domains_to_search),
            "processed_domains": len(domains_to_search),
            "successful_consolidations": len(qualified_advertisers),
            "failed_consolidations": len(failed_consolidations),
            "qualified_advertisers": qualified_advertisers,
            "high_priority": high_quality,
            "medium_priority": medium_quality,
            "failed_requests": failed_consolidations,
            "api_calls_used": len(tasks),
            "domains_processed": domains_to_search,
            "summary": {
                "total_domains_from_layer1": len(aggregated_domains),
                "filtered_domains": len(domains_to_search),
                "processed_count": len(domains_to_search),
                "high_quality_leads": len(high_quality),
                "medium_quality_leads": len(medium_quality),
                "qualification_rate": len(qualified_advertisers) / len(domains_to_search) if domains_to_search else 0,
                "success_rate": len(qualified_advertisers) / len(tasks) if tasks else 0
            }
        }
        
        self.logger.info(f"[COMPLETE] Layer 2: {len(high_quality)} high-priority, {len(medium_quality)} medium-priority leads from domains")
        
        return layer2_results
    
    async def save_results(self, results: Dict[str, any], output_dir: Path) -> str:
        """Save Layer 2 results to JSON file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"layer2_consolidation_{timestamp}.json"
        filepath = output_dir / filename
        
        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"[SAVED] Layer 2 results: {filepath}")
        return str(filepath)


# Test async functionality
async def test_layer2():
    """Test function for Layer 2"""
    logging.basicConfig(level=logging.INFO)
    
    layer2 = SearchAPILayer2AdvertiserConsolidation()
    
    # Test single advertiser consolidation
    test_result = await layer2.consolidate_advertiser_info(
        "AR06972987913109766145", 
        "Kyle Property Management", 
        "IE"
    )
    
    if test_result:
        print(f"✅ Test successful: {test_result['advertiser_name']} - Score: {test_result['quality_score']:.2f}")
    else:
        print("❌ Test failed")


if __name__ == "__main__":
    asyncio.run(test_layer2())