#!/usr/bin/env python3
"""
ARCO Consolidated SearchAPI Pipeline
===================================
Substitui os layers fragmentados por pipeline coerente e estratégico.
Progressão lógica: Seed → Qualification → Analysis → CRM Enrichment
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from ..core.unified_crm_system import UnifiedCRMEnrichmentEngine

logger = logging.getLogger(__name__)

@dataclass 
class SearchAPIConfig:
    """Configuração consolidada do pipeline SearchAPI"""
    api_key: str
    target_regions: List[str] = None
    target_verticals: List[str] = None
    budget_per_execution: float = 0.50  # Controle rigoroso de custos
    max_leads_per_batch: int = 50
    quality_threshold: float = 70.0
    rate_limit_delay: float = 1.0
    
    def __post_init__(self):
        if self.target_regions is None:
            self.target_regions = ["US", "GB", "CA", "AU"]  # Anglophone focus
        if self.target_verticals is None:
            self.target_verticals = ["marketing_agencies", "ecommerce", "saas", "dental"]

class ConsolidatedSearchAPIPipeline:
    """Pipeline SearchAPI consolidado com progressão lógica"""
    
    def __init__(self, config: SearchAPIConfig):
        self.config = config
        self.session = None
        self.crm_engine = UnifiedCRMEnrichmentEngine()
        
        # API endpoints consolidados
        self.endpoints = {
            "search": "https://www.searchapi.io/api/v1/search",
            "ads_transparency": "https://www.searchapi.io/api/v1/ads_transparency",
            "domain_analysis": "https://www.searchapi.io/api/v1/domain"
        }
        
        # Tracking de custos e performance
        self.execution_stats = {
            "total_cost": 0.0,
            "api_calls": 0,
            "leads_generated": 0,
            "quality_leads": 0,
            "start_time": None
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        self.execution_stats["start_time"] = datetime.now()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def execute_strategic_pipeline(self, target_count: int = 50) -> Dict[str, Any]:
        """
        Executa pipeline estratégico completo:
        1. Strategic Seed Generation (smart keyword targeting)
        2. Advertiser Qualification (real advertiser validation) 
        3. Deep Analysis (pain signals & opportunities)
        4. Unified CRM Enrichment (batch output)
        """
        logger.info(f"Starting strategic pipeline for {target_count} qualified leads")
        
        pipeline_results = {
            "pipeline_id": f"strategic_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "execution_timestamp": datetime.now().isoformat(),
            "target_count": target_count,
            "stages": {
                "seed_generation": {},
                "advertiser_qualification": {},
                "deep_analysis": {},
                "crm_enrichment": {}
            },
            "final_leads": [],
            "execution_stats": {}
        }
        
        try:
            # Stage 1: Strategic Seed Generation
            logger.info("Stage 1: Strategic Seed Generation")
            seed_results = await self._strategic_seed_generation()
            pipeline_results["stages"]["seed_generation"] = seed_results
            
            # Stage 2: Advertiser Qualification
            logger.info("Stage 2: Advertiser Qualification") 
            qualified_advertisers = await self._advertiser_qualification(seed_results["potential_advertisers"])
            pipeline_results["stages"]["advertiser_qualification"] = {
                "total_checked": len(seed_results["potential_advertisers"]),
                "qualified_count": len(qualified_advertisers),
                "qualification_rate": len(qualified_advertisers) / len(seed_results["potential_advertisers"]) if seed_results["potential_advertisers"] else 0
            }
            
            # Stage 3: Deep Analysis
            logger.info("Stage 3: Deep Analysis")
            analyzed_leads = await self._deep_analysis(qualified_advertisers[:target_count])
            pipeline_results["stages"]["deep_analysis"] = {
                "analyzed_count": len(analyzed_leads),
                "high_quality_count": len([l for l in analyzed_leads if l.get("quality_score", 0) >= self.config.quality_threshold])
            }
            
            # Stage 4: Unified CRM Enrichment
            logger.info("Stage 4: Unified CRM Enrichment")
            enriched_leads = self.crm_engine.enrich_lead_batch(analyzed_leads)
            pipeline_results["stages"]["crm_enrichment"] = {
                "enriched_count": len(enriched_leads),
                "high_priority_count": len([l for l in enriched_leads if l.outreach_priority == "high"])
            }
            
            pipeline_results["final_leads"] = [asdict(lead) for lead in enriched_leads]
            pipeline_results["execution_stats"] = self.execution_stats
            
            # Save consolidated results
            output_file = await self._save_pipeline_results(pipeline_results)
            pipeline_results["output_file"] = output_file
            
            logger.info(f"Strategic pipeline completed. {len(enriched_leads)} leads enriched.")
            return pipeline_results
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            pipeline_results["error"] = str(e)
            return pipeline_results
    
    async def _strategic_seed_generation(self) -> Dict[str, Any]:
        """Stage 1: Geração estratégica de seeds com foco em pain signals"""
        
        # Keywords estratégicos por vertical com foco em pain points
        strategic_keywords = {
            "marketing_agencies": [
                "marketing agency client retention problems",
                "digital marketing roi tracking issues", 
                "advertising spend optimization tools",
                "marketing agency scaling challenges"
            ],
            "ecommerce": [
                "ecommerce conversion rate optimization",
                "online store performance issues",
                "ecommerce customer acquisition cost",
                "shopify store optimization services"
            ],
            "saas": [
                "saas customer churn reduction",
                "software user onboarding optimization", 
                "saas growth marketing strategies",
                "b2b software lead generation"
            ],
            "dental": [
                "dental practice marketing automation",
                "dentist patient acquisition strategies",
                "dental clinic online booking",
                "orthodontist marketing optimization"
            ]
        }
        
        potential_advertisers = []
        
        for vertical in self.config.target_verticals:
            if vertical not in strategic_keywords:
                continue
                
            keywords = strategic_keywords[vertical]
            
            for keyword in keywords:
                for region in self.config.target_regions:
                    
                    # SearchAPI call para encontrar anunciantes
                    search_data = await self._searchapi_call("search", {
                        "q": keyword,
                        "gl": region,
                        "num": 20,
                        "device": "desktop"
                    })
                    
                    if search_data and "ads" in search_data:
                        for ad in search_data["ads"]:
                            advertiser_data = {
                                "domain": self._extract_domain(ad.get("link", "")),
                                "title": ad.get("title", ""),
                                "description": ad.get("description", ""),
                                "keyword_context": keyword,
                                "region": region,
                                "vertical": vertical,
                                "ad_position": ad.get("position", 0),
                                "found_timestamp": datetime.now().isoformat()
                            }
                            
                            # Filtrar duplicatas
                            if not any(p["domain"] == advertiser_data["domain"] for p in potential_advertisers):
                                potential_advertisers.append(advertiser_data)
                    
                    # Rate limiting
                    await asyncio.sleep(self.config.rate_limit_delay)
        
        return {
            "total_keywords_searched": len(strategic_keywords) * len(self.config.target_regions),
            "potential_advertisers": potential_advertisers,
            "verticals_coverage": list(strategic_keywords.keys()),
            "regions_coverage": self.config.target_regions
        }
    
    async def _advertiser_qualification(self, potential_advertisers: List[Dict]) -> List[Dict]:
        """Stage 2: Qualificação real de anunciantes (elimina false positives)"""
        
        qualified_advertisers = []
        
        for advertiser in potential_advertisers:
            domain = advertiser.get("domain", "")
            if not domain or domain in ["google.com", "facebook.com", "linkedin.com"]:
                continue
            
            # Verificar se é realmente um anunciante ativo
            qualification_score = await self._calculate_advertiser_qualification(advertiser)
            
            if qualification_score >= 60:  # Threshold para qualificação
                advertiser["qualification_score"] = qualification_score
                advertiser["qualified_timestamp"] = datetime.now().isoformat()
                qualified_advertisers.append(advertiser)
            
            # Rate limiting
            await asyncio.sleep(self.config.rate_limit_delay)
            
            # Budget protection
            if self.execution_stats["total_cost"] >= self.config.budget_per_execution:
                logger.warning("Budget limit reached, stopping qualification")
                break
        
        return qualified_advertisers
    
    async def _calculate_advertiser_qualification(self, advertiser: Dict) -> float:
        """Calcula score de qualificação real do anunciante"""
        
        domain = advertiser.get("domain", "")
        qualification_factors = []
        
        # Factor 1: Ad transparency check
        transparency_data = await self._searchapi_call("ads_transparency", {
            "q": domain,
            "type": "advertiser"
        })
        
        if transparency_data and transparency_data.get("ads_count", 0) > 0:
            ads_count = transparency_data.get("ads_count", 0)
            if ads_count >= 10:
                qualification_factors.append(30)  # High ad volume
            elif ads_count >= 5:
                qualification_factors.append(20)  # Medium ad volume  
            else:
                qualification_factors.append(10)  # Low ad volume
        else:
            qualification_factors.append(0)  # No ads found
        
        # Factor 2: Domain analysis
        domain_data = await self._searchapi_call("domain_analysis", {
            "domain": domain
        })
        
        if domain_data:
            # Traffic indicators
            if domain_data.get("traffic_rank", 999999) < 100000:
                qualification_factors.append(25)  # High traffic
            elif domain_data.get("traffic_rank", 999999) < 500000:
                qualification_factors.append(15)  # Medium traffic
            else:
                qualification_factors.append(5)   # Low traffic
            
            # Business indicators
            if domain_data.get("business_category"):
                qualification_factors.append(15)  # Clear business category
            else:
                qualification_factors.append(5)
        
        # Factor 3: Keyword relevance
        keyword_relevance = self._calculate_keyword_relevance(advertiser)
        qualification_factors.append(keyword_relevance)
        
        # Factor 4: Regional targeting appropriateness
        region_score = self._calculate_region_score(advertiser)
        qualification_factors.append(region_score)
        
        return min(sum(qualification_factors), 100)
    
    def _calculate_keyword_relevance(self, advertiser: Dict) -> float:
        """Calcula relevância das keywords para o anunciante"""
        
        keyword = advertiser.get("keyword_context", "").lower()
        title = advertiser.get("title", "").lower()
        description = advertiser.get("description", "").lower()
        
        # Pain signal keywords get higher relevance
        pain_signal_keywords = ["problems", "issues", "optimization", "improve", "increase", "reduce", "solution"]
        
        relevance_score = 0
        
        # Title relevance
        for pain_keyword in pain_signal_keywords:
            if pain_keyword in title:
                relevance_score += 5
        
        # Description relevance
        for pain_keyword in pain_signal_keywords:
            if pain_keyword in description:
                relevance_score += 3
        
        # Direct keyword match
        if any(word in title + " " + description for word in keyword.split()):
            relevance_score += 10
        
        return min(relevance_score, 20)
    
    def _calculate_region_score(self, advertiser: Dict) -> float:
        """Calcula score baseado na região de targeting"""
        
        region = advertiser.get("region", "")
        
        # Prioritize English-speaking regions for easier outreach
        high_priority_regions = ["US", "GB", "CA", "AU"]
        medium_priority_regions = ["IE", "NZ", "ZA"]
        
        if region in high_priority_regions:
            return 10
        elif region in medium_priority_regions:
            return 7
        else:
            return 3
    
    async def _deep_analysis(self, qualified_advertisers: List[Dict]) -> List[Dict]:
        """Stage 3: Análise profunda para identificação de pain signals e opportunities"""
        
        analyzed_leads = []
        
        for advertiser in qualified_advertisers:
            try:
                # Deep domain analysis
                deep_analysis = await self._perform_deep_analysis(advertiser)
                
                # Merge advertiser data with deep analysis
                complete_lead = {**advertiser, **deep_analysis}
                
                # Calculate final quality score
                complete_lead["quality_score"] = self._calculate_final_quality_score(complete_lead)
                
                analyzed_leads.append(complete_lead)
                
            except Exception as e:
                logger.error(f"Deep analysis failed for {advertiser.get('domain', 'unknown')}: {e}")
                continue
            
            # Rate limiting and budget protection
            await asyncio.sleep(self.config.rate_limit_delay)
            
            if self.execution_stats["total_cost"] >= self.config.budget_per_execution:
                logger.warning("Budget limit reached, stopping deep analysis")
                break
        
        return analyzed_leads
    
    async def _perform_deep_analysis(self, advertiser: Dict) -> Dict:
        """Análise profunda de um anunciante para pain signals"""
        
        domain = advertiser.get("domain", "")
        
        # Comprehensive ads analysis
        ads_analysis = await self._analyze_advertising_patterns(domain)
        
        # Technical analysis indicators
        tech_analysis = await self._analyze_technical_indicators(domain)
        
        # Competitive analysis
        competitive_analysis = await self._analyze_competitive_position(advertiser)
        
        return {
            "company_name": self._extract_company_name(advertiser),
            "industry": advertiser.get("vertical", "Unknown"),
            "country": advertiser.get("region", "Unknown"),
            "estimated_monthly_spend": ads_analysis.get("estimated_spend", 0),
            "advertising_platforms": ads_analysis.get("platforms", []),
            "creative_diversity_score": ads_analysis.get("creative_diversity", 0),
            "campaign_strategies": ads_analysis.get("strategies", []),
            "target_audiences": ads_analysis.get("audiences", []),
            "creative_themes": ads_analysis.get("themes", []),
            "performance_score": tech_analysis.get("performance_score", 70),
            "estimated_cpa": ads_analysis.get("estimated_cpa", 100),
            "confirmed_advertiser": True,  # Already qualified
            "data_sources": ["searchapi_consolidated"]
        }
    
    async def _analyze_advertising_patterns(self, domain: str) -> Dict:
        """Analisa padrões de publicidade para identificar pain points"""
        
        # Get advertising data from transparency APIs
        ads_data = await self._searchapi_call("ads_transparency", {
            "q": domain,
            "type": "detailed_analysis"
        })
        
        if not ads_data:
            return {
                "estimated_spend": 2000,  # Conservative estimate
                "platforms": ["google"],
                "creative_diversity": 0.3,
                "strategies": ["search"],
                "audiences": ["general"],
                "themes": ["product"],
                "estimated_cpa": 120
            }
        
        # Analyze advertising patterns for pain signals
        total_ads = ads_data.get("total_ads", 0)
        unique_creatives = ads_data.get("unique_creatives", 0)
        platforms = ads_data.get("platforms", ["google"])
        
        # Calculate spend estimate based on ad volume
        if total_ads > 100:
            estimated_spend = 15000
        elif total_ads > 50:
            estimated_spend = 8000
        elif total_ads > 20:
            estimated_spend = 4000
        else:
            estimated_spend = 2000
        
        # Creative diversity (pain signal if low)
        creative_diversity = min(unique_creatives / max(total_ads, 1), 1.0)
        
        # Estimated CPA (pain signal if high)
        estimated_cpa = max(50, 200 - (creative_diversity * 100))
        
        return {
            "estimated_spend": estimated_spend,
            "platforms": platforms,
            "creative_diversity": creative_diversity,
            "strategies": ["search", "display"] if total_ads > 20 else ["search"],
            "audiences": ["business_owners", "professionals"] if total_ads > 50 else ["general"],
            "themes": ["efficiency", "growth"] if creative_diversity > 0.5 else ["product"],
            "estimated_cpa": estimated_cpa
        }
    
    async def _analyze_technical_indicators(self, domain: str) -> Dict:
        """Analisa indicadores técnicos para pain signals"""
        
        # Performance analysis (can indicate technical pain points)
        performance_score = 70  # Default - would integrate with PageSpeed API
        
        # Estimate performance based on domain characteristics
        if ".shopify" in domain:
            performance_score = 65  # Shopify tends to be slower
        elif ".wordpress" in domain:
            performance_score = 60  # WordPress can have performance issues
        elif domain.endswith((".io", ".ai", ".tech")):
            performance_score = 80  # Tech domains usually better optimized
        
        return {
            "performance_score": performance_score,
            "mobile_optimization": performance_score > 70,
            "page_speed_issues": performance_score < 60
        }
    
    async def _analyze_competitive_position(self, advertiser: Dict) -> Dict:
        """Analisa posição competitiva para identificar pressões"""
        
        keyword = advertiser.get("keyword_context", "")
        region = advertiser.get("region", "")
        
        # Analyze competitive landscape
        competitive_data = await self._searchapi_call("search", {
            "q": keyword,
            "gl": region,
            "num": 10
        })
        
        competitor_count = 0
        if competitive_data and "ads" in competitive_data:
            competitor_count = len(competitive_data["ads"])
        
        return {
            "competitor_density": competitor_count,
            "competitive_pressure": "high" if competitor_count > 8 else "medium" if competitor_count > 4 else "low"
        }
    
    def _calculate_final_quality_score(self, lead_data: Dict) -> float:
        """Calcula score final de qualidade do lead"""
        
        score_components = []
        
        # Advertiser qualification (0-25 points)
        score_components.append(min(lead_data.get("qualification_score", 0) * 0.25, 25))
        
        # Spending volume (0-25 points) 
        spend = lead_data.get("estimated_monthly_spend", 0)
        if spend > 10000:
            score_components.append(25)
        elif spend > 5000:
            score_components.append(20)
        elif spend > 2000:
            score_components.append(15)
        else:
            score_components.append(10)
        
        # Pain signal indicators (0-30 points)
        pain_score = 0
        if lead_data.get("creative_diversity_score", 1) < 0.4:
            pain_score += 10  # Low creative diversity
        if lead_data.get("estimated_cpa", 0) > 150:
            pain_score += 10  # High CPA
        if lead_data.get("performance_score", 100) < 60:
            pain_score += 10  # Poor performance
        
        score_components.append(pain_score)
        
        # Strategic fit (0-20 points)
        region = lead_data.get("country", "")
        if region in ["US", "GB", "CA", "AU"]:
            score_components.append(20)
        else:
            score_components.append(10)
        
        return min(sum(score_components), 100)
    
    async def _searchapi_call(self, endpoint_type: str, params: Dict) -> Optional[Dict]:
        """Faz chamada para SearchAPI com tracking de custos"""
        
        if endpoint_type not in self.endpoints:
            logger.error(f"Unknown endpoint type: {endpoint_type}")
            return None
        
        url = self.endpoints[endpoint_type]
        params["api_key"] = self.config.api_key
        
        try:
            async with self.session.get(url, params=params) as response:
                self.execution_stats["api_calls"] += 1
                self.execution_stats["total_cost"] += 0.01  # Estimated cost per call
                
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"API call failed: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"API call exception: {e}")
            return None
    
    def _extract_domain(self, url: str) -> str:
        """Extrai domínio limpo da URL"""
        if not url:
            return ""
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url if url.startswith(('http://', 'https://')) else f'https://{url}')
            domain = parsed.netloc.lower()
            
            # Remove www prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain
        except:
            return ""
    
    def _extract_company_name(self, advertiser: Dict) -> str:
        """Extrai nome da empresa a partir dos dados do anunciante"""
        
        title = advertiser.get("title", "")
        domain = advertiser.get("domain", "")
        
        # Try to extract from title first
        if title:
            # Remove common ad words
            cleaned_title = title.replace("- Official Site", "").replace("| Official", "").strip()
            if len(cleaned_title) > 3:
                return cleaned_title
        
        # Fallback to domain
        if domain:
            return domain.replace(".com", "").replace(".co", "").replace(".io", "").title()
        
        return "Unknown Company"
    
    async def _save_pipeline_results(self, results: Dict) -> str:
        """Salva resultados consolidados do pipeline"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"strategic_pipeline_results_{timestamp}.json"
        
        output_dir = Path("data/pipeline_results")
        output_dir.mkdir(parents=True, exist_ok=True)
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Pipeline results saved: {filepath}")
        return str(filepath)

# Demo function
async def demo_consolidated_pipeline():
    """Demo do pipeline consolidado"""
    
    config = SearchAPIConfig(
        api_key="demo_key",
        target_regions=["US", "GB"],
        target_verticals=["marketing_agencies"],
        budget_per_execution=0.25,
        max_leads_per_batch=10
    )
    
    async with ConsolidatedSearchAPIPipeline(config) as pipeline:
        results = await pipeline.execute_strategic_pipeline(target_count=5)
        
        print("\n🚀 CONSOLIDATED SEARCHAPI PIPELINE RESULTS")
        print("=" * 55)
        print(f"Pipeline ID: {results['pipeline_id']}")
        print(f"Target Count: {results['target_count']}")
        print(f"Final Leads: {len(results['final_leads'])}")
        print(f"Total Cost: ${results['execution_stats']['total_cost']:.3f}")
        print(f"API Calls: {results['execution_stats']['api_calls']}")

if __name__ == "__main__":
    asyncio.run(demo_consolidated_pipeline())