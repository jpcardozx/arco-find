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
    
    def get_advertiser_data(self, 
                          advertiser_id: str = None,
                          domain: str = None,
                          region: str = "AU",
                          platform: str = None,
                          time_period: str = "last_30_days") -> Dict:
        """
        Busca dados detalhados de um anunciante específico
        
        Args:
            advertiser_id: ID do anunciante (ou domain se não tiver ID)
            domain: Domínio do anunciante
            region: Região (AU, NZ, US, CA)
            platform: Plataforma específica (google_search, youtube, etc)
            time_period: Período (last_30_days, last_7_days, today)
        
        Returns:
            Dict com dados consolidados do anunciante
        """
        
        if not advertiser_id and not domain:
            raise ValueError("É necessário fornecer advertiser_id ou domain")
        
        params = {
            "engine": self.engine,
            "region": region,
            "time_period": time_period,
            "api_key": self.api_key
        }
        
        if advertiser_id:
            params["advertiser_id"] = advertiser_id
        else:
            params["domain"] = domain
        
        if platform:
            params["platform"] = platform
        
        try:
            self.logger.info(f"Getting advertiser data for: {advertiser_id or domain}")
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Estrutura padronizada de retorno
            result = {
                "advertiser_id": advertiser_id,
                "domain": domain,
                "region": region,
                "time_period": time_period,
                "timestamp": datetime.now().isoformat(),
                "ads": data.get("ads", []),
                "advertiser_info": data.get("advertiser_info", {}),
                "total_ads": len(data.get("ads", [])),
                "search_params": params,
                "qualification_scores": self._calculate_qualification_scores(data)
            }
            
            return result
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed for {advertiser_id or domain}: {str(e)}")
            return {
                "advertiser_id": advertiser_id,
                "domain": domain,
                "error": str(e),
                "ads": [],
                "total_ads": 0,
                "qualification_scores": {"total_score": 0}
            }
    
    def _calculate_qualification_scores(self, api_data: Dict) -> Dict:
        """
        Calcula scores de qualificação baseados nos critérios ARCO
        """
        
        ads = api_data.get("ads", [])
        advertiser_info = api_data.get("advertiser_info", {})
        
        scores = {
            "activity_score": 0,      # 0-30 pontos
            "volume_score": 0,        # 0-25 pontos  
            "recency_score": 0,       # 0-25 pontos
            "diversity_score": 0,     # 0-20 pontos
            "total_score": 0,         # 0-100 pontos
            "qualification_status": "rejected"
        }
        
        total_ads = len(ads)
        
        # 1. Activity Score (30 pontos max)
        if total_ads >= self.min_ads_threshold:
            if total_ads <= 10:
                scores["activity_score"] = 15
            elif total_ads <= 30:
                scores["activity_score"] = 25
            elif total_ads <= self.max_ads_threshold:
                scores["activity_score"] = 30
            else:
                scores["activity_score"] = 10  # Penalizar volumes muito altos
        
        # 2. Volume Score (25 pontos max)
        if self.min_ads_threshold <= total_ads <= self.max_ads_threshold:
            # Sweet spot: 5-50 ads
            if 5 <= total_ads <= 50:
                scores["volume_score"] = 25
            elif 3 <= total_ads <= 80:
                scores["volume_score"] = 15
        
        # 3. Recency Score (25 pontos max)
        recent_ads = 0
        cutoff_date = datetime.now() - timedelta(days=self.recency_days)
        
        for ad in ads:
            # Tentar extrair data de first_seen ou last_seen
            ad_date = self._extract_ad_date(ad)
            if ad_date and ad_date >= cutoff_date:
                recent_ads += 1
        
        if recent_ads > 0:
            recency_ratio = recent_ads / total_ads if total_ads > 0 else 0
            scores["recency_score"] = min(25, int(recency_ratio * 25))
        
        # 4. Diversity Score (20 pontos max)
        platforms = set()
        formats = set()
        
        for ad in ads:
            if "platform" in ad:
                platforms.add(ad["platform"])
            if "format" in ad:
                formats.add(ad["format"])
        
        diversity_points = len(platforms) * 5 + len(formats) * 3
        scores["diversity_score"] = min(20, diversity_points)
        
        # Score total
        scores["total_score"] = (
            scores["activity_score"] + 
            scores["volume_score"] + 
            scores["recency_score"] + 
            scores["diversity_score"]
        )
        
        # Status de qualificação
        if scores["total_score"] >= 70:
            scores["qualification_status"] = "qualified"
        elif scores["total_score"] >= 50:
            scores["qualification_status"] = "potential"
        else:
            scores["qualification_status"] = "rejected"
        
        return scores
    
    def _extract_ad_date(self, ad: Dict) -> Optional[datetime]:
        """
        Extrai data do anúncio a partir dos campos disponíveis
        """
        
        date_fields = ["last_seen", "first_seen", "date", "timestamp"]
        
        for field in date_fields:
            if field in ad and ad[field]:
                try:
                    # Tentar diferentes formatos de data
                    date_str = ad[field]
                    
                    # ISO format
                    if "T" in date_str:
                        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    
                    # Date only
                    if "-" in date_str and len(date_str) == 10:
                        return datetime.strptime(date_str, "%Y-%m-%d")
                    
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def _is_excluded_domain(self, domain: str) -> bool:
        """
        Verifica se o domínio deve ser excluído
        """
        
        if not domain:
            return True
        
        # Limpar domínio
        clean_domain = domain.lower().strip()
        if clean_domain.startswith("www."):
            clean_domain = clean_domain[4:]
        
        # Check exact matches
        if clean_domain in self.excluded_domains:
            return True
        
        # Check franchise patterns
        for pattern in self.franchise_patterns:
            if re.match(pattern, clean_domain, re.IGNORECASE):
                return True
        
        return False
    
    def consolidate_advertisers_batch(self, 
                                    advertiser_list: List[Dict],
                                    region: str = "AU",
                                    max_batch_size: int = 50) -> Dict:
        """
        Consolida um lote de anunciantes com rate limiting
        
        Args:
            advertiser_list: Lista com advertiser_ids e/ou domains
            region: Região para busca
            max_batch_size: Máximo de anunciantes por lote
        
        Returns:
            Dict com resultados consolidados e qualificados
        """
        
        batch = advertiser_list[:max_batch_size]
        
        consolidation_results = {
            "batch_timestamp": datetime.now().isoformat(),
            "region": region,
            "batch_size": len(batch),
            "processed_advertisers": {},
            "qualified_advertisers": {},
            "potential_advertisers": {},
            "rejected_advertisers": {},
            "summary": {
                "total_processed": 0,
                "qualified_count": 0,
                "potential_count": 0,
                "rejected_count": 0,
                "api_calls_used": 0
            }
        }
        
        for i, advertiser in enumerate(batch):
            try:
                # Rate limiting
                if i > 0:
                    time.sleep(0.8)  # Ser conservador com as calls
                
                advertiser_id = advertiser.get("advertiser_id")
                domain = advertiser.get("domain")
                
                # Skip se domínio excluído
                if domain and self._is_excluded_domain(domain):
                    self.logger.info(f"Skipping excluded domain: {domain}")
                    continue
                
                # Buscar dados do anunciante
                ad_data = self.get_advertiser_data(
                    advertiser_id=advertiser_id,
                    domain=domain,
                    region=region
                )
                
                consolidation_results["api_calls_used"] += 1
                consolidation_results["processed_advertisers"][advertiser_id or domain] = ad_data
                
                # Classificar por qualification status
                status = ad_data["qualification_scores"]["qualification_status"]
                key = advertiser_id or domain
                
                if status == "qualified":
                    consolidation_results["qualified_advertisers"][key] = ad_data
                    consolidation_results["summary"]["qualified_count"] += 1
                elif status == "potential":
                    consolidation_results["potential_advertisers"][key] = ad_data
                    consolidation_results["summary"]["potential_count"] += 1
                else:
                    consolidation_results["rejected_advertisers"][key] = ad_data
                    consolidation_results["summary"]["rejected_count"] += 1
                
                consolidation_results["summary"]["total_processed"] += 1
                
                self.logger.info(f"Processed {key}: {status} (score: {ad_data['qualification_scores']['total_score']})")
                
            except Exception as e:
                self.logger.error(f"Error processing advertiser {advertiser}: {str(e)}")
                continue
        
        return consolidation_results
    
    def get_qualified_advertisers_for_layer3(self, consolidation_data: Dict) -> List[Dict]:
        """
        Extrai anunciantes qualificados para alimentar Layer 3
        
        Returns:
            Lista de anunciantes prontos para análise detalhada
        """
        
        qualified_for_layer3 = []
        
        # Priorizar qualified, depois potential
        for category in ["qualified_advertisers", "potential_advertisers"]:
            for key, advertiser_data in consolidation_data.get(category, {}).items():
                
                # Extrair creative_ids dos anúncios para Layer 3
                creative_ids = []
                for ad in advertiser_data.get("ads", []):
                    if "id" in ad:
                        creative_ids.append(ad["id"])
                
                qualified_advertiser = {
                    "advertiser_id": advertiser_data.get("advertiser_id"),
                    "domain": advertiser_data.get("domain"),
                    "qualification_score": advertiser_data["qualification_scores"]["total_score"],
                    "qualification_status": advertiser_data["qualification_scores"]["qualification_status"],
                    "total_ads": advertiser_data.get("total_ads", 0),
                    "creative_ids": creative_ids[:5],  # Máximo 5 para Layer 3
                    "region": advertiser_data.get("region"),
                    "consolidation_timestamp": advertiser_data.get("timestamp")
                }
                
                qualified_for_layer3.append(qualified_advertiser)
        
        # Ordenar por score descendente
        qualified_for_layer3.sort(key=lambda x: x["qualification_score"], reverse=True)
        
        return qualified_for_layer3

# Exemplo de uso
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Configuração
    API_KEY = "your_searchapi_key_here"
    
    # Inicializar engine
    consolidation_engine = SearchAPILayer2AdvertiserConsolidation(api_key=API_KEY)
    
    # Exemplo: consolidar lista de anunciantes do Layer 1
    advertisers_from_layer1 = [
        {"advertiser_id": "AR123456789", "domain": "example-dental.com.au"},
        {"domain": "medspa-example.com.au"}
    ]
    
    results = consolidation_engine.consolidate_advertisers_batch(
        advertiser_list=advertisers_from_layer1,
        region="AU"
    )
    
    print(f"Qualified: {results['summary']['qualified_count']}")
    print(f"Potential: {results['summary']['potential_count']}")
    print(f"Rejected: {results['summary']['rejected_count']}")
