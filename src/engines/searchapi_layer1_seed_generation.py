"""
ARCO SearchAPI - Layer 1: Seed Generation Engine (S-tier)
========================================================

Engine 1: google_ads_transparency_center_advertiser_search
- Busca assíncrona com aiohttp para performance
- Configuração robusta com pydantic
- Keywords otimizadas por vertical/geo
- Rate limiting inteligente

Verticais ARCO:
- Dental/Ortho: invisalign, dental implants, veneers
- Medical Spa: botox, laser hair removal, dermal filler
- Real Estate EU: buyers agent, property investment advice
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, AsyncGenerator
import logging
from pathlib import Path
import sys

# Add config path
sys.path.append(str(Path(__file__).parent.parent))
from config.arco_config_simple import get_config, get_api_key, get_keywords, get_regions

class SearchAPILayer1SeedGeneration:
    """S-tier Layer 1 com aiohttp e configuração robusta"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.config = get_config()
        self.api_key = api_key or get_api_key()
        
        # Auto-detect demo mode (now only for truly invalid keys)
        if not self.api_key or self.api_key in ['demo_mode_get_key_at_serpapi_com', 'your_serpapi_key_here']:
            self.demo_mode = True
        else:
            self.demo_mode = False
            
        self.base_url = self.config.searchapi.base_url
        self.engine = "google_ads_transparency_center_advertiser_search"
        
        # Session para reutilização de conexões
        self.session: Optional[aiohttp.ClientSession] = None
        
        self.logger = logging.getLogger(__name__)
        
        # Rate limiting tracker
        self.last_request_time = 0
        self.request_count = 0
    
    async def __aenter__(self):
        """Context manager entry"""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self._close_session()
    
    async def _ensure_session(self):
        """Garante que a sessão está ativa"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.searchapi.request_timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def _close_session(self):
        """Fecha sessão de forma segura"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _rate_limit(self):
        """Rate limiting inteligente"""
        now = time.time()
        time_since_last = now - self.last_request_time
        
        if time_since_last < self.config.searchapi.rate_limit_delay:
            sleep_time = self.config.searchapi.rate_limit_delay - time_since_last
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    async def _demo_search_advertisers(self, keyword: str, region: str, num_advertisers: int, num_domains: int) -> Dict:
        """Demo implementation with simulated API responses"""
        
        await asyncio.sleep(0.5)  # Simulate API delay
        self.request_count += 1
        
        self.logger.info(f"🎭 DEMO: Searching '{keyword}' in {region} (call #{self.request_count})")
        
        # Create region-specific demo data
        demo_advertisers = [
            {
                "advertiser_id": f"{region.lower()}_advertiser_{keyword.replace(' ', '_')}_{i}",
                "name": f"{region} {keyword.title()} Pro {i}",
                "display_url": f"{keyword.replace(' ', '')}{i}.{region.lower()}",
                "verification_status": "verified",
                "region": region
            }
            for i in range(1, min(num_advertisers, 8) + 1)
        ]
        
        demo_domains = [
            f"{keyword.replace(' ', '')}{i}.{region.lower()}" 
            for i in range(1, min(num_domains, 8) + 1)
        ]
        
        return {
            "advertisers": demo_advertisers,
            "domains": demo_domains,
            "total_advertisers": len(demo_advertisers),
            "total_domains": len(demo_domains),
            "metadata": {
                "status": "Demo Success",
                "keyword": keyword,
                "region": region,
                "processing_time": 0.5
            }
        }
    
    async def search_advertisers_by_keyword(self, 
                                          keyword: str,
                                          region: str = "IE",
                                          num_advertisers: int = 50,
                                          num_domains: int = 50) -> Dict:
        """
        Busca assíncrona de anunciantes por keyword com auto-demo mode
        """
        
        # Check if demo mode
        if self.demo_mode:
            return await self._demo_search_advertisers(keyword, region, num_advertisers, num_domains)
        
        await self._ensure_session()
        await self._rate_limit()
        
        params = {
            "engine": self.engine,
            "q": keyword,
            "region": region,
            "num_advertisers": min(num_advertisers, 100),
            "num_domains": min(num_domains, 100),
            "api_key": self.api_key
        }
        
        for attempt in range(self.config.searchapi.max_retries):
            try:
                self.logger.info(f"[SEARCH] Searching advertisers: '{keyword}' in {region} (attempt {attempt + 1})")
                
                async with self.session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        result = {
                            "keyword": keyword,
                            "region": region,
                            "timestamp": datetime.now().isoformat(),
                            "advertisers": data.get("advertisers", []),
                            "domains": data.get("domains", []),
                            "total_advertisers": len(data.get("advertisers", [])),
                            "total_domains": len(data.get("domains", [])),
                            "search_params": params,
                            "request_count": self.request_count
                        }
                        
                        self.logger.info(f"[FOUND] Found {result['total_advertisers']} advertisers, {result['total_domains']} domains")
                        return result
                    
                    elif response.status == 429:  # Rate limited
                        wait_time = 2 ** attempt
                        self.logger.warning(f"⏳ Rate limited, waiting {wait_time}s")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    else:
                        response.raise_for_status()
                        
            except asyncio.TimeoutError:
                self.logger.warning(f"⏱️ Timeout on attempt {attempt + 1}")
                if attempt < self.config.searchapi.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                    
            except Exception as e:
                self.logger.error(f"❌ Request failed on attempt {attempt + 1}: {str(e)}")
                if attempt < self.config.searchapi.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
        
        # All attempts failed
        self.logger.error(f"❌ All attempts failed for keyword {keyword}")
        return {
            "keyword": keyword,
            "region": region,
            "error": "Max retries exceeded",
            "advertisers": [],
            "domains": [],
            "total_advertisers": 0,
            "total_domains": 0
        }
    
    async def generate_seeds_by_vertical(self, 
                                       vertical: str,
                                       regions: Optional[List[str]] = None,
                                       max_keywords: Optional[int] = None) -> Dict:
        """
        Gera seeds assíncronos para uma vertical específica
        
        Args:
            vertical: Nome da vertical (dental_ortho, medical_spa, real_estate_eu)
            regions: Lista de regiões (default: Europa)
            max_keywords: Máximo de keywords (default: config)
        
        Returns:
            Dict agregado com todos os seeds da vertical
        """
        
        await self._ensure_session()
        
        if regions is None:
            regions = get_regions('europa')  # Default Europa
        
        keywords = get_keywords(vertical)
        if max_keywords:
            keywords = keywords[:max_keywords]
        
        all_seeds = {
            "vertical": vertical,
            "regions": regions,
            "keywords_used": keywords,
            "timestamp": datetime.now().isoformat(),
            "results_by_keyword": {},
            "aggregated_advertisers": {},
            "aggregated_domains": set(),
            "total_unique_advertisers": 0,
            "total_unique_domains": 0,
            "total_api_calls": 0
        }
        
        # Preparar tasks assíncronas para todas as combinações
        tasks = []
        for keyword in keywords:
            for region in regions:
                task = self.search_advertisers_by_keyword(
                    keyword=keyword,
                    region=region,
                    num_advertisers=50,
                    num_domains=50
                )
                tasks.append((f"{keyword}_{region}", task))
        
        # Executar todas as tasks com controle de concorrência
        semaphore = asyncio.Semaphore(3)  # Max 3 concurrent requests
        
        async def bounded_task(key, task):
            async with semaphore:
                return key, await task
        
        self.logger.info(f"[EXECUTING] Executing {len(tasks)} async searches for {vertical}")
        
        # Execute all tasks
        bounded_tasks = [bounded_task(key, task) for key, task in tasks]
        results = await asyncio.gather(*bounded_tasks, return_exceptions=True)
        
        # Process results
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Task failed: {result}")
                continue
                
            key, data = result
            all_seeds["results_by_keyword"][key] = data
            all_seeds["total_api_calls"] += 1
            
            # Agregar advertisers (evitar duplicatas por advertiser_id)
            for advertiser in data.get("advertisers", []):
                advertiser_id = advertiser.get("advertiser_id")
                if advertiser_id and advertiser_id not in all_seeds["aggregated_advertisers"]:
                    all_seeds["aggregated_advertisers"][advertiser_id] = {
                        **advertiser,
                        "first_seen_keyword": data["keyword"],
                        "first_seen_region": data["region"]
                    }
            
            # Agregar domains
            for domain in data.get("domains", []):
                domain_name = domain if isinstance(domain, str) else domain.get("domain", str(domain))
                all_seeds["aggregated_domains"].add(domain_name)
        
        # Finalizar agregação
        all_seeds["aggregated_domains"] = list(all_seeds["aggregated_domains"])
        all_seeds["total_unique_advertisers"] = len(all_seeds["aggregated_advertisers"])
        all_seeds["total_unique_domains"] = len(all_seeds["aggregated_domains"])
        
        self.logger.info(f"[COMPLETE] Vertical {vertical}: {all_seeds['total_unique_advertisers']} unique advertisers, {all_seeds['total_unique_domains']} unique domains")
        
        return all_seeds
    
    async def generate_comprehensive_seeds(self, 
                                         verticals: Optional[List[str]] = None,
                                         regions: Optional[List[str]] = None,
                                         save_to_file: Optional[str] = None) -> Dict:
        """
        Gera seeds completos para múltiplas verticais de forma assíncrona
        
        Args:
            verticals: Lista de verticais (default: config)
            regions: Lista de regiões (default: Europa)
            save_to_file: Caminho para salvar resultados
        
        Returns:
            Dict com seeds de todas as verticais
        """
        
        await self._ensure_session()
        
        if verticals is None:
            verticals = ["dental_ortho", "medical_spa", "real_estate_eu"]
        
        if regions is None:
            regions = get_regions('europa')
        
        comprehensive_seeds = {
            "generation_timestamp": datetime.now().isoformat(),
            "verticals_processed": verticals,
            "regions_processed": regions,
            "results_by_vertical": {},
            "global_aggregation": {
                "all_advertiser_ids": set(),
                "all_domains": set(),
                "total_api_calls": 0
            },
            "performance_metrics": {
                "execution_start": time.time(),
                "total_requests": 0,
                "failed_requests": 0
            }
        }
        
        # Executar verticais em paralelo com limitação
        vertical_tasks = []
        for vertical in verticals:
            task = self.generate_seeds_by_vertical(
                vertical=vertical,
                regions=regions,
                max_keywords=self.config.searchapi.max_keywords_per_vertical
            )
            vertical_tasks.append((vertical, task))
        
        self.logger.info(f"🌍 Processing {len(verticals)} verticals across {len(regions)} regions")
        
        # Execute vertical tasks
        for vertical, task in vertical_tasks:
            try:
                self.logger.info(f"📊 Processing vertical: {vertical}")
                
                vertical_seeds = await task
                comprehensive_seeds["results_by_vertical"][vertical] = vertical_seeds
                
                # Agregação global
                for advertiser_id in vertical_seeds["aggregated_advertisers"].keys():
                    comprehensive_seeds["global_aggregation"]["all_advertiser_ids"].add(advertiser_id)
                
                for domain in vertical_seeds["aggregated_domains"]:
                    comprehensive_seeds["global_aggregation"]["all_domains"].add(domain)
                
                comprehensive_seeds["global_aggregation"]["total_api_calls"] += vertical_seeds["total_api_calls"]
                
            except Exception as e:
                self.logger.error(f"❌ Error processing vertical {vertical}: {str(e)}")
                comprehensive_seeds["performance_metrics"]["failed_requests"] += 1
                continue
        
        # Finalizar métricas
        comprehensive_seeds["performance_metrics"]["execution_time"] = time.time() - comprehensive_seeds["performance_metrics"]["execution_start"]
        comprehensive_seeds["performance_metrics"]["total_requests"] = comprehensive_seeds["global_aggregation"]["total_api_calls"]
        
        # Converter sets para listas
        comprehensive_seeds["global_aggregation"]["all_advertiser_ids"] = list(
            comprehensive_seeds["global_aggregation"]["all_advertiser_ids"]
        )
        comprehensive_seeds["global_aggregation"]["all_domains"] = list(
            comprehensive_seeds["global_aggregation"]["all_domains"]
        )
        
        comprehensive_seeds["global_aggregation"]["total_unique_advertisers"] = len(
            comprehensive_seeds["global_aggregation"]["all_advertiser_ids"]
        )
        comprehensive_seeds["global_aggregation"]["total_unique_domains"] = len(
            comprehensive_seeds["global_aggregation"]["all_domains"]
        )
        
        # Salvar se solicitado
        if save_to_file:
            try:
                with open(save_to_file, 'w', encoding='utf-8') as f:
                    json.dump(comprehensive_seeds, f, indent=2, ensure_ascii=False, default=str)
                self.logger.info(f"💾 Seeds saved to {save_to_file}")
            except Exception as e:
                self.logger.error(f"❌ Failed to save seeds: {str(e)}")
        
        total_time = comprehensive_seeds["performance_metrics"]["execution_time"]
        total_calls = comprehensive_seeds["global_aggregation"]["total_api_calls"]
        self.logger.info(f"🎯 Pipeline complete: {total_calls} calls in {total_time:.2f}s")
        
        return comprehensive_seeds
    
    def get_seed_summary(self, seeds_data: Dict) -> Dict:
        """Gera sumário executivo dos seeds gerados"""
        
        summary = {
            "generation_time": seeds_data.get("generation_timestamp"),
            "verticals_count": len(seeds_data.get("results_by_vertical", {})),
            "total_advertisers": seeds_data.get("global_aggregation", {}).get("total_unique_advertisers", 0),
            "total_domains": seeds_data.get("global_aggregation", {}).get("total_unique_domains", 0),
            "api_calls_used": seeds_data.get("global_aggregation", {}).get("total_api_calls", 0),
            "execution_time": seeds_data.get("performance_metrics", {}).get("execution_time", 0),
            "breakdown_by_vertical": {}
        }
        
        for vertical, data in seeds_data.get("results_by_vertical", {}).items():
            summary["breakdown_by_vertical"][vertical] = {
                "advertisers": data.get("total_unique_advertisers", 0),
                "domains": data.get("total_unique_domains", 0),
                "keywords": len(data.get("keywords_used", [])),
                "regions": len(data.get("regions", []))
            }
        
        return summary

# Async wrapper functions for backward compatibility
async def create_layer1_session(api_key: Optional[str] = None) -> SearchAPILayer1SeedGeneration:
    """Create and initialize Layer 1 session"""
    layer1 = SearchAPILayer1SeedGeneration(api_key)
    await layer1._ensure_session()
    return layer1

# Exemplo de uso
async def main():
    """Exemplo de uso assíncrono"""
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Usar context manager para gestão automática de sessão
        async with SearchAPILayer1SeedGeneration() as layer1:
            
            # Teste single keyword
            result = await layer1.search_advertisers_by_keyword(
                keyword="buyers agent",
                region="IE",
                num_advertisers=10
            )
            
            print(f"🇮🇪 Irlanda: {result['total_advertisers']} advertisers found")
            
            # Teste vertical completo
            vertical_seeds = await layer1.generate_seeds_by_vertical(
                vertical="real_estate_eu",
                regions=["IE", "GB"],
                max_keywords=2
            )
            
            print(f"🏠 Real Estate EU: {vertical_seeds['total_unique_advertisers']} unique advertisers")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
