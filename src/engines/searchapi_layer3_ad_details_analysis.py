"""
ARCO SearchAPI - Layer 3: Ad Details & Landing Analysis Engine (S-tier Async)
=============================================================

Engine 3: google_ads_transparency_center_ad_details
- Extrai payload completo dos criativos específicos usando async aiohttp
- Captura final_url para análise técnica da landing page
- Calcula score ARCO final com base em CRO signals

Input: creative_ids do Layer 2
Output: anúncios detalhados + landing pages + scores técnicos
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import logging
from urllib.parse import urlparse, parse_qs
import re
from pathlib import Path

from ..config.arco_config_simple import get_config, get_api_key


class SearchAPILayer3AdDetailsAnalysis:
    """
    S-tier async Layer 3 engine for ad details analysis using SearchAPI
    Google Ads Transparency Center Ad Details API
    """
    
    def __init__(self):
        self.config = get_config()
        self.api_key = get_api_key()
        self.base_url = self.config.searchapi.base_url
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Rate limiting
        self.semaphore = asyncio.Semaphore(2)  # Max 2 concurrent requests for detailed analysis
        
        # Componentes do Score ARCO (totalizando 100 pontos)
        self.score_weights = {
            "ad_activity": 30,      # Atividade publicitária (já do Layer 2)
            "technical": 40,        # Core Web Vitals + stack
            "cro_signals": 30       # CRO + coerência anúncio→LP
        }
        
        # Padrões de CTA para detectar
        self.cta_patterns = [
            r"book now", r"call now", r"get quote", r"free consultation",
            r"schedule", r"contact us", r"learn more", r"get started",
            r"sign up", r"register", r"download", r"claim"
        ]
        
        # Sinais de urgência/prova social
        self.urgency_patterns = [
            r"limited time", r"today only", r"act fast", r"while stocks last",
            r"\d+% off", r"free", r"guarantee", r"certified", r"award"
        ]
    
    async def analyze_ad_details(self, layer2_results: List[Dict]) -> Dict:
        """
        S-tier async análise completa de detalhes dos anúncios
        
        Args:
            layer2_results: Lista de leads qualificados do Layer 2 com creative_ids
            
        Returns:
            Dict com análise detalhada de cada creative_id e scores ARCO finais
        """
        start_time = time.time()
        
        self.logger.info(f"Starting Layer 3 ad details analysis for {len(layer2_results)} qualified leads")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "layer3_analysis": [],
            "summary": {
                "total_leads_analyzed": 0,
                "successful_analyses": 0,
                "failed_analyses": 0,
                "top_performers": [],
                "execution_time": 0
            }
        }
        
        # Processar cada lead (domain) para obter todos os criativos
        domain_analysis_tasks = []
        
        for lead in layer2_results:
            domain = lead.get("domain", "").replace("DOMAIN_", "")  # Remove prefix se existir
            if domain:
                domain_analysis_tasks.append(
                    self._analyze_domain_creatives(domain, lead)
                )
        
        # Execute análises em paralelo com controle de rate limiting
        if domain_analysis_tasks:
            self.logger.info(f"Analyzing {len(domain_analysis_tasks)} domains in parallel")
            domain_results = await asyncio.gather(*domain_analysis_tasks, return_exceptions=True)
            
            # Processar resultados de cada domínio
            for result in domain_results:
                if isinstance(result, Exception):
                    self.logger.error(f"Domain analysis failed: {result}")
                    results["summary"]["failed_analyses"] += 1
                else:
                    if result and isinstance(result, list):
                        results["layer3_analysis"].extend(result)
                        results["summary"]["successful_analyses"] += len(result)
                    elif result:
                        results["summary"]["failed_analyses"] += 1
        
        # Atualizar summary
        results["summary"]["total_leads_analyzed"] = len(layer2_results)
        results["summary"]["execution_time"] = round(time.time() - start_time, 2)
        
        # Identificar top performers
        results["summary"]["top_performers"] = self._identify_top_performers(
            results["layer3_analysis"]
        )
        
        success_rate = (len(results["layer3_analysis"]) / 
                       sum(len(lead.get("creative_ids", [])) for lead in layer2_results) * 100) if layer2_results else 0
        
        self.logger.info(f"Layer 3 completed: {len(results['layer3_analysis'])} creatives analyzed ({success_rate:.1f}% success) in {results['summary']['execution_time']}s")
        
        return results
    
    async def _analyze_domain_creatives(self, domain: str, lead_data: Dict) -> List[Dict]:
        """
        Analisa todos os criativos de um domínio específico
        """
        async with self.semaphore:
            try:
                # Obter todos os criativos do domínio
                domain_creatives = await self._get_domain_creatives(domain)
                
                if not domain_creatives:
                    return []
                
                # Filtrar apenas os creative_ids que estão no Layer 2
                target_creative_ids = set(lead_data.get("creative_ids", []))
                
                results = []
                for creative in domain_creatives:
                    creative_id = creative.get("id")
                    if creative_id in target_creative_ids:
                        # Análise da landing page (se disponível)
                        landing_analysis = await self._analyze_landing_page(creative)
                        
                        # Calcular score ARCO final
                        arco_score = self._calculate_arco_score(
                            creative, 
                            landing_analysis, 
                            lead_data
                        )
                        
                        results.append({
                            "creative_id": creative_id,
                            "lead_domain": domain,
                            "lead_score": lead_data.get("score", 0),
                            "creative_details": creative,
                            "landing_analysis": landing_analysis,
                            "arco_score": arco_score,
                            "timestamp": datetime.now().isoformat()
                        })
                
                return results
                
            except Exception as e:
                self.logger.error(f"Error analyzing domain {domain}: {e}")
                return []
    
    async def _get_domain_creatives(self, domain: str) -> Optional[List[Dict]]:
        """
        S-tier async call para obter todos os criativos de um domínio
        """
        params = {
            "engine": "google_ads_transparency_center",
            "api_key": self.api_key,
            "domain": domain
        }
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extrair criativos da resposta
                        if "ad_creatives" in data:
                            return data["ad_creatives"]
                        
                        self.logger.warning(f"No ad_creatives found for domain {domain}")
                        return None
                    else:
                        self.logger.error(f"API error for domain {domain}: {response.status}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"Request failed for domain {domain}: {e}")
            return None
    
    async def _analyze_single_creative(self, creative_id: str, lead_data: Dict) -> Optional[Dict]:
        """
        Análise S-tier async de um creative específico
        """
        async with self.semaphore:
            try:
                # API call para detalhes do creative
                creative_details = await self._get_creative_details(creative_id)
                
                if not creative_details:
                    return None
                
                # Análise da landing page (se disponível)
                landing_analysis = await self._analyze_landing_page(creative_details)
                
                # Calcular score ARCO final
                arco_score = self._calculate_arco_score(
                    creative_details, 
                    landing_analysis, 
                    lead_data
                )
                
                return {
                    "creative_id": creative_id,
                    "lead_domain": lead_data.get("domain", "unknown"),
                    "lead_score": lead_data.get("score", 0),
                    "creative_details": creative_details,
                    "landing_analysis": landing_analysis,
                    "arco_score": arco_score,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                self.logger.error(f"Error analyzing creative {creative_id}: {e}")
                return None
    
    async def _get_creative_details(self, creative_id: str) -> Optional[Dict]:
        """
        S-tier async call para detalhes de um creative específico
        """
        params = {
            "engine": "google_ads_transparency_center",
            "api_key": self.api_key,
            "creative_id": creative_id
        }
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extrair informações relevantes do creative
                        if "ad_details" in data:
                            return self._extract_creative_data(data["ad_details"])
                        elif "results" in data and data["results"]:
                            return self._extract_creative_data(data["results"][0])
                        elif "ad_variations" in data:
                            return self._extract_creative_data(data)
                        
                        self.logger.warning(f"No ad details found for creative {creative_id}")
                        return None
                    else:
                        self.logger.error(f"API error for creative {creative_id}: {response.status}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"Request failed for creative {creative_id}: {e}")
            return None
    
    def _extract_creative_data(self, creative_data: Dict) -> Dict:
        """
        Extrai dados estruturados do creative (formato API real)
        """
        extracted = {
            "creative_id": creative_data.get("id"),
            "advertiser_name": creative_data.get("advertiser", {}).get("name"),
            "advertiser_id": creative_data.get("advertiser", {}).get("id"),
            "target_domain": creative_data.get("target_domain"),
            "format": creative_data.get("format"),
            "first_shown": creative_data.get("first_shown_datetime"),
            "last_shown": creative_data.get("last_shown_datetime"),
            "total_days_shown": creative_data.get("total_days_shown", 0),
            "headlines": [],
            "descriptions": [],
            "final_urls": [],
            "image_url": None,
            "primary_landing_page": None,
            "cro_signals": {}
        }
        
        # Extrair URLs de imagem se disponível
        if "image" in creative_data:
            extracted["image_url"] = creative_data["image"].get("link")
        
        # Extrair texto se disponível (alguns criativos têm texto)
        if "text" in creative_data:
            text_data = creative_data["text"]
            if "headlines" in text_data:
                extracted["headlines"] = text_data["headlines"]
            if "descriptions" in text_data:
                extracted["descriptions"] = text_data["descriptions"]
            if "display_url" in text_data:
                extracted["final_urls"].append(text_data["display_url"])
        
        # Usar target_domain como landing page principal se não houver URL específica
        if extracted["final_urls"]:
            extracted["primary_landing_page"] = extracted["final_urls"][0]
        else:
            extracted["primary_landing_page"] = f"https://{extracted['target_domain']}"
        
        # Análise de CRO baseada nos dados disponíveis
        extracted["cro_signals"] = self._analyze_cro_signals(extracted)
        
        return extracted
    
    def _analyze_cro_signals(self, extracted_data: Dict) -> Dict:
        """
        Análise de sinais de CRO nos criativos (adaptada para dados reais)
        """
        cro_analysis = {
            "cta_strength": 0,          # 0-10 pontos
            "urgency_signals": 0,       # 0-5 pontos  
            "benefit_clarity": 0,       # 0-10 pontos
            "trust_signals": 0,         # 0-5 pontos
            "total_cro_score": 0,       # 0-30 pontos
            "detected_ctas": [],
            "detected_urgency": [],
            "improvement_suggestions": [],
            "activity_score": 0         # Baseado em days_shown
        }
        
        # Concatenar todos os textos do anúncio
        all_text = []
        all_text.extend(extracted_data.get("headlines", []))
        all_text.extend(extracted_data.get("descriptions", []))
        
        combined_text = " ".join(all_text).lower()
        
        # Se não há texto, usar apenas métricas de atividade
        if not combined_text.strip():
            # Score baseado em atividade (total_days_shown)
            days_shown = extracted_data.get("total_days_shown", 0)
            if days_shown >= 30:
                cro_analysis["activity_score"] = 15  # Alto
            elif days_shown >= 14:
                cro_analysis["activity_score"] = 10  # Médio
            elif days_shown >= 7:
                cro_analysis["activity_score"] = 5   # Baixo
            
            cro_analysis["total_cro_score"] = cro_analysis["activity_score"]
            return cro_analysis
        
        # Análise de texto se disponível
        # 1. Análise de CTAs
        found_ctas = []
        for pattern in self.cta_patterns:
            if re.search(pattern, combined_text, re.IGNORECASE):
                found_ctas.append(pattern)
        
        cro_analysis["detected_ctas"] = found_ctas
        cro_analysis["cta_strength"] = min(10, len(found_ctas) * 3)
        
        # 2. Sinais de urgência
        found_urgency = []
        for pattern in self.urgency_patterns:
            if re.search(pattern, combined_text, re.IGNORECASE):
                found_urgency.append(pattern)
        
        cro_analysis["detected_urgency"] = found_urgency
        cro_analysis["urgency_signals"] = min(5, len(found_urgency) * 2)
        
        # 3. Clareza de benefício
        benefit_keywords = ["free", "guarantee", "certified", "expert", "professional", "quality"]
        benefit_count = sum(1 for keyword in benefit_keywords if keyword in combined_text)
        cro_analysis["benefit_clarity"] = min(10, benefit_count * 2)
        
        # 4. Sinais de confiança
        trust_keywords = ["certified", "licensed", "insured", "guarantee", "warranty", "award"]
        trust_count = sum(1 for keyword in trust_keywords if keyword in combined_text)
        cro_analysis["trust_signals"] = min(5, trust_count * 2)
        
        # 5. Score de atividade
        days_shown = extracted_data.get("total_days_shown", 0)
        if days_shown >= 30:
            cro_analysis["activity_score"] = 5
        elif days_shown >= 14:
            cro_analysis["activity_score"] = 3
        elif days_shown >= 7:
            cro_analysis["activity_score"] = 1
        
        # Score total de CRO
        cro_analysis["total_cro_score"] = (
            cro_analysis["cta_strength"] +
            cro_analysis["urgency_signals"] +
            cro_analysis["benefit_clarity"] +
            cro_analysis["trust_signals"] +
            cro_analysis["activity_score"]
        )
        
        # Sugestões de melhoria
        if cro_analysis["cta_strength"] < 5:
            cro_analysis["improvement_suggestions"].append("Add stronger call-to-action")
        
        if cro_analysis["urgency_signals"] == 0:
            cro_analysis["improvement_suggestions"].append("Include urgency or scarcity elements")
        
        if cro_analysis["trust_signals"] < 3:
            cro_analysis["improvement_suggestions"].append("Add trust signals (certifications, guarantees)")
        
        if days_shown < 7:
            cro_analysis["improvement_suggestions"].append("Increase ad duration for better testing")
        
        return cro_analysis
    
    async def _analyze_landing_page(self, creative_data: Dict) -> Dict:
        """
        Análise básica da landing page baseada nos dados do creative
        """
        landing_analysis = {
            "primary_url": creative_data.get("target_domain"),
            "advertiser_name": creative_data.get("advertiser", {}).get("name"),
            "format": creative_data.get("format"),
            "days_active": creative_data.get("total_days_shown", 0),
            "technical_score": 0,
            "content_match": 0,
            "total_landing_score": 0
        }
        
        # Score técnico baseado em heurísticas
        domain = landing_analysis["primary_url"]
        if domain:
            # Bonificar domínios que parecem profissionais
            if any(term in domain.lower() for term in ['estate', 'property', 'real', 'homes']):
                landing_analysis["technical_score"] += 3
            
            # Bonificar atividade sustentada
            if landing_analysis["days_active"] >= 30:
                landing_analysis["technical_score"] += 5
            elif landing_analysis["days_active"] >= 14:
                landing_analysis["technical_score"] += 3
            elif landing_analysis["days_active"] >= 7:
                landing_analysis["technical_score"] += 1
            
            # Bonificar formatos visuais (mais engajamento)
            if landing_analysis["format"] in ["image", "video"]:
                landing_analysis["technical_score"] += 2
            
            landing_analysis["technical_score"] = max(0, min(10, landing_analysis["technical_score"]))
        
        # Score de coerência baseado no advertiser_name
        if landing_analysis["advertiser_name"]:
            advertiser = landing_analysis["advertiser_name"].lower()
            if any(term in advertiser for term in ['estate', 'property', 'real', 'homes', 'agents']):
                landing_analysis["content_match"] = 8
            elif any(term in advertiser for term in ['data', 'pty', 'ltd', 'corp']):
                landing_analysis["content_match"] = 5  # Empresas de dados/corporativas
            else:
                landing_analysis["content_match"] = 3
        
        landing_analysis["total_landing_score"] = (
            landing_analysis["technical_score"] + 
            landing_analysis["content_match"]
        )
        
        return landing_analysis
    
    def _calculate_arco_score(self, creative_data: Dict, landing_analysis: Dict, lead_data: Dict) -> Dict:
        """
        Calcula score ARCO final usando dados reais da API
        """
        # Extrair dados do creative
        creative_details = self._extract_creative_data(creative_data)
        
        # Componentes do score
        ad_activity_score = lead_data.get("score", 0) * 100  # Score do Layer 2 (0-1) → 0-100
        cro_score = creative_details.get("cro_signals", {}).get("total_cro_score", 0)
        technical_score = landing_analysis.get("total_landing_score", 0) * 2  # 0-20 → 0-40
        
        # Peso por componente
        weighted_ad_activity = (ad_activity_score * self.score_weights["ad_activity"]) / 100
        weighted_cro = (cro_score * self.score_weights["cro_signals"]) / 35  # Ajustado para novo máximo
        weighted_technical = (technical_score * self.score_weights["technical"]) / 40
        
        total_score = weighted_ad_activity + weighted_cro + weighted_technical
        
        return {
            "total_score": round(total_score, 2),
            "components": {
                "ad_activity": round(weighted_ad_activity, 2),
                "cro_signals": round(weighted_cro, 2), 
                "technical": round(weighted_technical, 2)
            },
            "raw_scores": {
                "ad_activity": round(ad_activity_score, 2),
                "cro_signals": cro_score,
                "technical": round(technical_score, 2)
            },
            "creative_details": {
                "days_shown": creative_details.get("total_days_shown", 0),
                "format": creative_details.get("format"),
                "advertiser": creative_details.get("advertiser_name")
            },
            "grade": self._get_score_grade(total_score)
        }
    
    def _clean_final_url(self, url: str) -> Optional[str]:
        """
        Limpa URL final removendo parâmetros de tracking
        """
        
        if not url:
            return None
        
        try:
            # Remove parâmetros de tracking comuns
            tracking_params = [
                'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term',
                'gclid', 'fbclid', 'msclkid', '_ga', 'mc_eid'
            ]
            
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            # Remove tracking params
            clean_params = {k: v for k, v in query_params.items() 
                          if k not in tracking_params}
            
            # Reconstroi URL
            if clean_params:
                clean_query = '&'.join([f"{k}={v[0]}" for k, v in clean_params.items()])
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{clean_query}"
            else:
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            
            return clean_url
            
        except Exception:
            return url
    
    def _identify_top_performers(self, analyses: List[Dict]) -> List[Dict]:
        """
        Identifica os top performers por score ARCO
        """
        if not analyses:
            return []
        
        # Ordenar por score total
        sorted_analyses = sorted(
            analyses, 
            key=lambda x: x.get("arco_score", {}).get("total_score", 0), 
            reverse=True
        )
        
        # Retornar top 5
        top_performers = []
        for analysis in sorted_analyses[:5]:
            creative_details = analysis.get("arco_score", {}).get("creative_details", {})
            top_performers.append({
                "creative_id": analysis.get("creative_id"),
                "domain": analysis.get("lead_domain"),
                "total_score": analysis.get("arco_score", {}).get("total_score", 0),
                "grade": analysis.get("arco_score", {}).get("grade", "D"),
                "advertiser": creative_details.get("advertiser"),
                "format": creative_details.get("format"),
                "days_shown": creative_details.get("days_shown", 0),
                "primary_landing_page": analysis.get("creative_details", {}).get("primary_landing_page")
            })
        
        return top_performers
    
    def _get_score_grade(self, score: float) -> str:
        """
        Converte score numérico em grade
        """
        if score >= 80:
            return "A+"
        elif score >= 70:
            return "A"
        elif score >= 60:
            return "B+"
        elif score >= 50:
            return "B"
        elif score >= 40:
            return "C+"
        elif score >= 30:
            return "C"
        else:
            return "D"
        
        for advertiser in qualified_list:
            try:
                advertiser_id = advertiser["advertiser_id"]
                creative_ids = advertiser["creative_ids"][:max_creatives_per_advertiser]
                
                advertiser_results = {
                    "advertiser_info": advertiser,
                    "creative_analyses": {},
                    "best_creative": None,
                    "final_score": None
                }
                
                best_score = 0
                best_creative_data = None
                
                # Analisar cada criativo
                for creative_id in creative_ids:
                    try:
                        # Rate limiting
                        time.sleep(1.0)
                        
                        # Buscar detalhes do anúncio
                        ad_details = self.get_ad_details(advertiser_id, creative_id)
                        processing_results["summary"]["api_calls_used"] += 1
                        
                        # Análise técnica da landing page principal
                        primary_lp = ad_details["extracted_data"].get("primary_landing_page")
                        technical_analysis = self.analyze_landing_page_technical(primary_lp)
                        
                        # Score ARCO final
                        final_score = self.calculate_final_arco_score(
                            ad_details=ad_details,
                            technical_analysis=technical_analysis,
                            layer2_scores=advertiser  # scores do Layer 2
                        )
                        
                        creative_analysis = {
                            "ad_details": ad_details,
                            "technical_analysis": technical_analysis,
                            "final_score": final_score
                        }
                        
                        advertiser_results["creative_analyses"][creative_id] = creative_analysis
                        
                        # Acompanhar melhor criativo
                        if final_score["total_arco_score"] > best_score:
                            best_score = final_score["total_arco_score"]
                            best_creative_data = creative_analysis
                        
                    except Exception as e:
                        self.logger.error(f"Error processing creative {creative_id}: {str(e)}")
                        continue
                
                # Definir melhor criativo e score final do anunciante
                advertiser_results["best_creative"] = best_creative_data
                advertiser_results["final_score"] = best_creative_data["final_score"] if best_creative_data else {"total_arco_score": 0, "qualification_tier": "rejected"}
                
                processing_results["processed_results"][advertiser_id] = advertiser_results
                
                # Classificar por tier
                tier = advertiser_results["final_score"]["qualification_tier"]
                
                if tier == "premium":
                    processing_results["final_qualified"][advertiser_id] = advertiser_results
                    processing_results["summary"]["premium_tier"] += 1
                    
                    if advertiser_results["final_score"]["outreach_readiness"]:
                        processing_results["outreach_ready"][advertiser_id] = advertiser_results
                
                elif tier == "qualified":
                    processing_results["final_qualified"][advertiser_id] = advertiser_results
                    processing_results["summary"]["qualified_tier"] += 1
                    
                    if advertiser_results["final_score"]["outreach_readiness"]:
                        processing_results["outreach_ready"][advertiser_id] = advertiser_results
                
                elif tier == "potential":
                    processing_results["summary"]["potential_tier"] += 1
                else:
                    processing_results["summary"]["rejected_tier"] += 1
                
                self.logger.info(f"Advertiser {advertiser_id}: {tier} (score: {best_score})")
                
            except Exception as e:
                self.logger.error(f"Error processing advertiser {advertiser}: {str(e)}")
                continue
        
        return processing_results
    
    def generate_outreach_data(self, outreach_ready: Dict) -> List[Dict]:
        """
        Gera dados estruturados para outreach
        """
        
        outreach_list = []
        
        for advertiser_id, data in outreach_ready.items():
            best_creative = data["best_creative"]
            ad_details = best_creative["ad_details"]
            
            outreach_data = {
                "advertiser_id": advertiser_id,
                "domain": ad_details["extracted_data"].get("primary_landing_page"),
                "arco_score": best_creative["final_score"]["total_arco_score"],
                "priority_level": best_creative["final_score"]["priority_level"],
                "pain_points": best_creative["ad_details"]["cro_analysis"]["improvement_suggestions"],
                "headlines_used": ad_details["extracted_data"]["headlines"][:3],
                "landing_page": ad_details["extracted_data"]["primary_landing_page"],
                "suggested_improvements": self._generate_improvement_suggestions(best_creative),
                "outreach_angle": self._determine_outreach_angle(best_creative),
                "estimated_opportunity": self._estimate_opportunity_size(data)
            }
            
            outreach_list.append(outreach_data)
        
        # Ordenar por score descendente
        outreach_list.sort(key=lambda x: x["arco_score"], reverse=True)
        
        return outreach_list
    
    def _generate_improvement_suggestions(self, creative_data: Dict) -> List[str]:
        """
        Gera sugestões específicas de melhoria
        """
        
        suggestions = []
        cro_analysis = creative_data["ad_details"]["cro_analysis"]
        technical = creative_data["technical_analysis"]
        
        # Sugestões de CRO
        suggestions.extend(cro_analysis.get("improvement_suggestions", []))
        
        # Sugestões técnicas
        if technical.get("technical_score", 0) < 30:
            suggestions.append("Optimize Core Web Vitals for mobile")
            suggestions.append("Improve page loading speed")
        
        return suggestions[:5]  # Máximo 5 sugestões
    
    def _determine_outreach_angle(self, creative_data: Dict) -> str:
        """
        Determina o ângulo de abordagem para outreach
        """
        
        score = creative_data["final_score"]["total_arco_score"]
        cro_score = creative_data["ad_details"]["cro_analysis"]["total_cro_score"]
        
        if score >= 70:
            return "Performance optimization for high-performing ads"
        elif cro_score < 15:
            return "Landing page conversion optimization"
        else:
            return "Technical performance improvements"
    
    def _estimate_opportunity_size(self, advertiser_data: Dict) -> str:
        """
        Estima tamanho da oportunidade
        """
        
        ad_activity = advertiser_data["advertiser_info"].get("total_ads", 0)
        
        if ad_activity >= 30:
            return "High - Active advertiser with significant spend"
        elif ad_activity >= 10:
            return "Medium - Moderate advertising activity"
        else:
            return "Low - Limited advertising activity"

# Exemplo de uso
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Configuração
    API_KEY = "your_searchapi_key_here"
    
    # Inicializar engine
    details_engine = SearchAPILayer3AdDetailsAnalysis(api_key=API_KEY)
    
    # Exemplo: processar anunciantes qualificados do Layer 2
    qualified_from_layer2 = [
        {
            "advertiser_id": "AR123456789",
            "domain": "example-dental.com.au",
            "qualification_score": 75,
            "creative_ids": ["CR111", "CR222", "CR333"],
            "total_ads": 25
        }
    ]
    
    results = details_engine.process_qualified_advertisers(qualified_from_layer2)
    outreach_data = details_engine.generate_outreach_data(results["outreach_ready"])
    
    print(f"Outreach ready: {len(outreach_data)} advertisers")
