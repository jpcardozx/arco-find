"""Pipeline principal do ARCO Real Lead System - Versão refatorada

Este módulo contém a implementação do pipeline de descoberta e qualificação
de leads reais, integrando com o APIService para melhor gestão de requisições.
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from src.api_service import APIService
from src.models.lead import Lead
from src.pipeline.pain_points import PainPointsAnalyzer
from src.pipeline.revenue import RevenueEstimator

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='real_pipeline.log'
)
logger = logging.getLogger("arco.lead_pipeline")


class LeadPipeline:
    """Pipeline principal do ARCO Real Lead System

    Gerencia o fluxo completo de descoberta, análise e qualificação de leads:
    1. Descoberta via Google Places API
    2. Análise de performance via PageSpeed API
    3. Detecção de stack tecnológico
    4. Análise de oportunidades e pain points
    5. Estimativa de receita
    6. Qualificação e scoring
    """

    def __init__(self, 
                 google_api_key: str,
                 target_locations: List[str] = None,
                 batch_size: int = 10,
                 request_delay: float = 1.0,
                 min_score: int = 70,
                 target_count: int = 20):
        """Inicializa o pipeline com configurações

        Args:
            google_api_key: API key do Google para PageSpeed e Places
            target_locations: Lista de localizações para busca
            batch_size: Tamanho dos lotes para processamento
            request_delay: Delay entre requisições (segundos)
            min_score: Score mínimo para qualificação (0-100)
            target_count: Quantidade alvo de leads qualificados
        """
        self.google_api_key = google_api_key
        self.target_locations = target_locations or [
            "São Paulo, Brasil",
            "Rio de Janeiro, Brasil",
            "Belo Horizonte, Brasil",
            "Brasília, Brasil",
            "Curitiba, Brasil"
        ]
        self.batch_size = batch_size
        self.request_delay = request_delay
        self.min_score = min_score
        self.target_count = target_count

        # ICPs (Ideal Customer Profiles)
        self.icps = {
            "P1": {
                "name": "Growth E-commerce",
                "revenue": "US$ 500k-3M/ano",
                "stack": ["Shopify", "WooCommerce"],
                "pain": "60%+ mobile, perdas checkout"
            },
            "P2": {
                "name": "Nicho DTC",
                "revenue": "US$ 1M-5M/ano",
                "stack": ["Shopify"],
                "pain": "Margem apertada, CAC subindo"
            },
            "P3": {
                "name": "Serviços Profissionais",
                "revenue": "US$ 300k-1M/ano",
                "stack": ["WordPress", "Elementor"],
                "pain": "Formulário quebrado = agenda vazia"
            },
            "P4": {
                "name": "Early SaaS",
                "revenue": "MRR US$ 5-50k",
                "stack": ["React", "WordPress"],
                "pain": "Trial→Paid drop >30%"
            }
        }

        # Componentes especializados
        self.revenue_estimator = None
        self.pain_points_analyzer = None
        self.api_service = None

    async def __aenter__(self):
        """Context manager para inicializar serviços"""
        # Inicializa APIService
        self.api_service = APIService(cache_enabled=True, cache_ttl=86400)
        await self.api_service.__aenter__()

        # Registra APIs com configurações específicas
        self.api_service.register_api(
            "google_places", 
            calls_per_second=0.5, 
            max_concurrent=3
        )
        self.api_service.register_api(
            "pagespeed", 
            calls_per_second=0.2, 
            max_concurrent=2
        )

        # Inicializa engines especializados
        self.revenue_estimator = RevenueEstimator()
        self.pain_points_analyzer = PainPointsAnalyzer()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager para liberar recursos"""
        if self.api_service:
            await self.api_service.__aexit__(exc_type, exc_val, exc_tb)

    async def discover_businesses(self, location: str, business_type: str = None) -> List[Dict]:
        """Descobre empresas em uma localização usando Google Places API

        Args:
            location: Localização para busca (ex: "São Paulo, Brasil")
            business_type: Tipo de negócio (opcional)

        Returns:
            Lista de empresas descobertas
        """
        logger.info(f"Descobrindo empresas em {location}")

        query = business_type + " " + location if business_type else location

        result = await self.api_service.query(
            api_name="google_places",
            url="https://maps.googleapis.com/maps/api/place/textsearch/json",
            params={
                'query': query,
                'key': self.google_api_key
            }
        )

        if not result['success']:
            logger.error(f"Erro ao descobrir empresas em {location}: {result['error']}")
            return []

        businesses = result['data'].get('results', [])
        logger.info(f"Descobertas {len(businesses)} empresas em {location}")

        # Extrai dados relevantes
        processed_businesses = []
        for business in businesses:
            try:
                # Extrai apenas os dados necessários nesta fase
                business_data = {
                    "business_name": business.get("name", ""),
                    "location": business.get("formatted_address", ""),
                    "place_id": business.get("place_id", ""),
                    "rating": business.get("rating", 0),
                    "user_ratings_total": business.get("user_ratings_total", 0)
                }

                # Adiciona se tiver dados mínimos
                if business_data["business_name"] and business_data["place_id"]:
                    processed_businesses.append(business_data)
            except Exception as e:
                logger.warning(f"Erro ao processar empresa {business.get('name', 'desconhecida')}: {str(e)}")

        return processed_businesses

    async def get_place_details(self, place_id: str) -> Dict:
        """Obtém detalhes de um local pelo place_id

        Args:
            place_id: ID do local no Google Places API

        Returns:
            Detalhes do local
        """
        logger.debug(f"Obtendo detalhes para place_id: {place_id}")

        result = await self.api_service.query(
            api_name="google_places",
            url="https://maps.googleapis.com/maps/api/place/details/json",
            params={
                'place_id': place_id,
                'fields': 'name,formatted_address,website,formatted_phone_number,international_phone_number,opening_hours,rating,user_ratings_total,types',
                'key': self.google_api_key
            }
        )

        if not result['success'] or 'result' not in result['data']:
            logger.warning(f"Erro ao obter detalhes para place_id {place_id}: {result.get('error', 'Erro desconhecido')}")
            return {}

        return result['data']['result']

    async def analyze_website_performance(self, domain: str) -> Dict:
        """Analisa a performance de um website usando Google PageSpeed API

        Args:
            domain: Domínio do website

        Returns:
            Dados de performance
        """
        if not domain.startswith(('http://', 'https://')):
            url = f"https://{domain}"
        else:
            url = domain

        logger.debug(f"Analisando performance para: {url}")

        result = await self.api_service.query(
            api_name="pagespeed",
            url="https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
            params={
                'url': url,
                'key': self.google_api_key,
                'strategy': 'mobile'
            }
        )

        if not result['success']:
            logger.warning(f"Erro ao analisar performance para {url}: {result.get('error', 'Erro desconhecido')}")
            return self._get_default_performance_data()

        try:
            # Extrai métricas principais
            lighthouse_result = result['data'].get('lighthouseResult', {})
            audits = lighthouse_result.get('audits', {})

            # Performance score
            categories = lighthouse_result.get('categories', {})
            performance = categories.get('performance', {})
            performance_score = int(performance.get('score', 0) * 100) if performance else 0

            # Extrai métricas Core Web Vitals
            lcp = audits.get('largest-contentful-paint', {}).get('numericValue', 0) / 1000  # ms -> s
            cls = audits.get('cumulative-layout-shift', {}).get('numericValue', 0)
            fcp = audits.get('first-contentful-paint', {}).get('numericValue', 0) / 1000  # ms -> s

            # Identifica issues críticos
            performance_issues = []

            if lcp > 4.0:
                performance_issues.append(f"LCP crítico: {lcp:.1f}s (meta: <2.5s)")
            elif lcp > 2.5:
                performance_issues.append(f"LCP precisa melhorar: {lcp:.1f}s (meta: <2.5s)")

            if cls > 0.25:
                performance_issues.append(f"CLS crítico: {cls:.2f} (meta: <0.1)")
            elif cls > 0.1:
                performance_issues.append(f"CLS precisa melhorar: {cls:.2f} (meta: <0.1)")

            if fcp > 3.0:
                performance_issues.append(f"FCP crítico: {fcp:.1f}s (meta: <1.8s)")
            elif fcp > 1.8:
                performance_issues.append(f"FCP precisa melhorar: {fcp:.1f}s (meta: <1.8s)")

            return {
                "performance_score": performance_score,
                "lcp_mobile": round(lcp, 1),
                "cls_mobile": round(cls, 2),
                "fcp_mobile": round(fcp, 1),
                "performance_issues": performance_issues
            }

        except Exception as e:
            logger.error(f"Erro ao processar dados de performance para {url}: {str(e)}")
            return self._get_default_performance_data()

    def _get_default_performance_data(self) -> Dict:
        """Retorna dados de performance default para casos de erro"""
        return {
            "performance_score": 0,
            "lcp_mobile": 0.0,
            "cls_mobile": 0.0,
            "fcp_mobile": 0.0,
            "performance_issues": ["Não foi possível analisar a performance"]
        }

    async def detect_tech_stack(self, domain: str) -> Dict:
        """Detecta o stack tecnológico de um website

        Args:
            domain: Domínio do website

        Returns:
            Dados do stack tecnológico
        """
        if not domain.startswith(('http://', 'https://')):
            url = f"https://{domain}"
        else:
            url = domain

        # Implementação simplificada - na versão real usaríamos
        # técnicas mais avançadas de detecção (Wappalyzer API, etc)
        tech_indicators = await self._analyze_tech_indicators(url)

        tech_stack = tech_indicators.get("tech_stack", [])
        cms_platform = ""
        ecommerce_platform = ""
        marketing_tools = []

        # Identifica plataformas principais
        for tech in tech_stack:
            tech_lower = tech.lower()

            # CMS platforms
            if tech_lower in ["wordpress", "wp"]:
                cms_platform = "WordPress"
            elif tech_lower == "drupal":
                cms_platform = "Drupal"
            elif tech_lower == "joomla":
                cms_platform = "Joomla"

            # E-commerce platforms
            if tech_lower == "woocommerce":
                ecommerce_platform = "WooCommerce"
            elif tech_lower == "shopify":
                ecommerce_platform = "Shopify"
            elif tech_lower == "magento":
                ecommerce_platform = "Magento"

            # Marketing tools
            if tech_lower in ["google analytics", "ga", "gtm"]:
                marketing_tools.append("Google Analytics")
            elif tech_lower in ["facebook pixel", "meta pixel"]:
                marketing_tools.append("Meta Pixel")
            elif tech_lower == "klaviyo":
                marketing_tools.append("Klaviyo")
            elif tech_lower == "mailchimp":
                marketing_tools.append("Mailchimp")

        return {
            "tech_stack": tech_stack,
            "cms_platform": cms_platform,
            "ecommerce_platform": ecommerce_platform,
            "marketing_tools": marketing_tools
        }

    async def _analyze_tech_indicators(self, url: str) -> Dict:
        """Analisa indicadores tecnológicos de um website

        Esta é uma versão simplificada. Uma implementação completa usaria
        técnicas mais avançadas, como:
        1. Headers HTTP (X-Powered-By, etc)
        2. Análise de HTML (meta tags, scripts, etc)
        3. Análise de cookies
        4. APIs específicas (BuiltWith, Wappalyzer)

        Args:
            url: URL do website

        Returns:
            Indicadores tecnológicos detectados
        """
        try:
            # Simula detecção com base em patterns comuns
            # Na implementação real, faríamos scraping ou usaríamos APIs
            techs = []

            # Simula descoberta para o domínio específico (para demonstração)
            domain = url.replace("https://", "").replace("http://", "").split("/")[0]

            # Detecta com base no domínio
            if "shopify" in domain:
                techs.append("Shopify")

            # Aqui usaríamos requisições HTTP reais e análise de HTML
            # Simulando resultados baseados no domínio para exemplo
            if domain.endswith(".com.br") or domain.endswith(".br"):
                if "loja" in domain or "shop" in domain:
                    techs.append("WooCommerce")
                    techs.append("WordPress")
                elif "blog" in domain:
                    techs.append("WordPress")

            # Adiciona tech stacks específicos para domínios de exemplo
            # Este é apenas um mock para demonstração
            if domain == "insightjunior.com.br":
                techs = ["WordPress", "WooCommerce"]
            elif domain == "fashionnova.com":
                techs = ["Shopify", "Klaviyo", "Yotpo", "Judge.me"]
            elif "vtex" in domain:
                techs = ["VTEX", "Google Tag Manager", "jQuery"]

            return {
                "tech_stack": techs
            }

        except Exception as e:
            logger.error(f"Erro ao analisar tech stack para {url}: {str(e)}")
            return {"tech_stack": []}

    async def analyze_lead(self, business_data: Dict) -> Lead:
        """Analisa um lead potencial

        Args:
            business_data: Dados iniciais do negócio

        Returns:
            Objeto Lead completo com análise
        """
        # Extrai website do negócio
        place_details = await self.get_place_details(business_data.get("place_id", ""))
        website = place_details.get("website", "")

        # Extrai domínio
        domain = ""
        if website:
            domain = website.replace("https://", "").replace("http://", "").split("/")[0]

        # Se não tem domínio, não podemos analisar
        if not domain:
            logger.warning(f"Negócio {business_data.get('business_name')} não possui website")
            return None

        # Criação do lead básico
        lead = Lead(
            business_name=business_data.get("business_name", ""),
            domain=domain,
            location=business_data.get("location", ""),
            discovery_source="Google Places",
            review_score=float(business_data.get("rating", 0)),
            review_count=int(business_data.get("user_ratings_total", 0))
        )

        # Análise de performance
        perf_data = await self.analyze_website_performance(domain)
        lead.performance_score = perf_data.get("performance_score", 0)
        lead.lcp_mobile = perf_data.get("lcp_mobile", 0.0)
        lead.cls_mobile = perf_data.get("cls_mobile", 0.0)
        lead.fcp_mobile = perf_data.get("fcp_mobile", 0.0)
        lead.performance_issues = perf_data.get("performance_issues", [])

        # Detecção de stack tecnológico
        tech_data = await self.detect_tech_stack(domain)
        lead.tech_stack = tech_data.get("tech_stack", [])
        lead.cms_platform = tech_data.get("cms_platform", "")
        lead.ecommerce_platform = tech_data.get("ecommerce_platform", "")
        lead.marketing_tools = tech_data.get("marketing_tools", [])

        # Extrai indústria
        lead.industry = self._extract_industry(place_details, lead.tech_stack)

        # Análise adicional usando engines especializados
        # Estimativa de receita
        revenue_data = self.revenue_estimator.estimate_revenue(lead)
        lead.revenue_estimate = revenue_data.get("revenue_estimate", "")
        lead.employee_count = revenue_data.get("employee_count", "")

        # Análise de pain points
        pain_points_data = self.pain_points_analyzer.analyze(lead)
        lead.pain_points = pain_points_data.get("pain_points", [])
        lead.revenue_opportunity = pain_points_data.get("revenue_opportunity", "")

        # Determina ICP match
        lead.icp_match = self._determine_icp_match(lead)

        # Calcula score de qualificação
        lead.qualification_score = self._calculate_qualification_score(lead)

        # Determina estratégia de abordagem
        lead.approach_strategy = self._determine_approach_strategy(lead)

        # Determina nível de urgência
        lead.urgency_level = self._determine_urgency_level(lead)

        # Atualiza timestamp
        lead.last_updated = datetime.now()

        return lead

    def _extract_industry(self, place_details: Dict, tech_stack: List[str]) -> str:
        """Extrai a indústria com base nos detalhes do local e tech stack

        Args:
            place_details: Detalhes do Google Places
            tech_stack: Stack tecnológico detectado

        Returns:
            Indústria identificada
        """
        # Extrai dos tipos do Google Places
        types = place_details.get("types", [])

        # Mapeamento de tipos para indústrias
        industry_mapping = {
            "restaurant": "Food & Beverage",
            "food": "Food & Beverage",
            "cafe": "Food & Beverage",
            "bar": "Food & Beverage",
            "store": "Retail",
            "shop": "Retail",
            "clothing_store": "Fashion Retail",
            "shoe_store": "Fashion Retail",
            "health": "Healthcare",
            "doctor": "Healthcare",
            "hospital": "Healthcare",
            "school": "Education",
            "university": "Education",
            "lodging": "Hospitality",
            "hotel": "Hospitality",
            "real_estate": "Real Estate",
            "finance": "Financial Services",
            "bank": "Financial Services",
            "lawyer": "Professional Services",
            "accounting": "Professional Services",
            "beauty_salon": "Beauty & Wellness",
            "spa": "Beauty & Wellness",
            "gym": "Fitness",
        }

        # Tenta identificar a indústria pelos tipos
        for type_name in types:
            if type_name in industry_mapping:
                return industry_mapping[type_name]

        # Se não encontrou pelos tipos, tenta pelo tech stack
        if "WooCommerce" in tech_stack or "Shopify" in tech_stack:
            return "E-commerce"
        elif "WordPress" in tech_stack:
            return "General Business"

        # Default
        return "General Business"

    def _determine_icp_match(self, lead: Lead) -> str:
        """Determina qual ICP (Ideal Customer Profile) melhor corresponde ao lead

        Args:
            lead: Objeto Lead com dados do lead

        Returns:
            Código do ICP (P1, P2, P3, P4) ou vazio se não houver match
        """
        # P1: Growth E-commerce
        if (lead.ecommerce_platform in ["Shopify", "WooCommerce"] and
                lead.lcp_mobile > 3.0 and
                "checkout" in [issue.lower() for issue in lead.performance_issues]):
            return "P1"

        # P2: Nicho DTC
        if (lead.ecommerce_platform == "Shopify" and
                len(lead.marketing_tools) >= 2):
            return "P2"

        # P3: Serviços Profissionais
        if (lead.cms_platform == "WordPress" and
                "form" in [issue.lower() for issue in lead.performance_issues] and
                lead.industry in ["Professional Services", "Healthcare", "Real Estate"]):
            return "P3"

        # P4: Early SaaS
        if ("React" in lead.tech_stack or lead.cms_platform == "WordPress"):
            return "P4"

        # Sem match claro
        return ""

    def _calculate_qualification_score(self, lead: Lead) -> int:
        """Calcula o score de qualificação do lead

        Args:
            lead: Objeto Lead com dados do lead

        Returns:
            Score de qualificação (0-100)
        """
        score = 0

        # LCP Severity (20 pontos)
        if lead.lcp_mobile > 4.0:
            score += 20  # Crítico
        elif lead.lcp_mobile > 3.0:
            score += 10  # Precisa melhorar

        # Tech Stack (25 pontos)
        if lead.ecommerce_platform == "Shopify":
            score += 15
        elif lead.ecommerce_platform == "WooCommerce":
            score += 12

        # Complexidade de apps
        app_complexity = min(len(lead.tech_stack), 10)
        score += app_complexity

        # E-commerce (10 pontos)
        if lead.ecommerce_platform:
            score += 10

        # Industry Match (15 pontos)
        if lead.industry == "E-commerce":
            score += 15
        elif lead.industry in ["Retail", "Fashion Retail"]:
            score += 12
        elif lead.industry in ["Professional Services", "Healthcare", "Real Estate"]:
            score += 10
        elif lead.industry != "General Business":
            score += 8

        # Domain Authority (10 pontos)
        # Simplificado - na implementação real usaríamos dados de SEO
        if lead.review_count > 100:
            score += 10
        elif lead.review_count > 50:
            score += 7
        elif lead.review_count > 10:
            score += 5

        # Bônus por ICP match (20 pontos)
        if lead.icp_match in ["P1", "P2"]:
            score += 20
        elif lead.icp_match in ["P3", "P4"]:
            score += 15

        return min(score, 100)  # Máximo 100 pontos

    def _determine_approach_strategy(self, lead: Lead) -> str:
        """Determina a estratégia de abordagem para o lead

        Args:
            lead: Objeto Lead com dados do lead

        Returns:
            Estratégia de abordagem recomendada
        """
        if lead.qualification_score >= 85:
            return "Contato direto: Audit + Proposta Sprint"
        elif lead.qualification_score >= 70:
            return "Snapshot gratuito + Email com insights"
        elif lead.qualification_score >= 60:
            return "Lead nurturing: Conteúdo educativo"
        else:
            return "Sem abordagem - qualificação insuficiente"

    def _determine_urgency_level(self, lead: Lead) -> str:
        """Determina o nível de urgência para abordar o lead

        Args:
            lead: Objeto Lead com dados do lead

        Returns:
            Nível de urgência (Alto, Médio, Baixo)
        """
        # Critérios de urgência alta
        if lead.lcp_mobile > 5.0 or lead.qualification_score >= 85:
            return "Alto"

        # Critérios de urgência média
        if lead.lcp_mobile > 3.0 or lead.qualification_score >= 70:
            return "Médio"

        # Default
        return "Baixo"

    async def run_pipeline(self, business_type: str = None) -> List[Lead]:
        """Executa o pipeline completo de descoberta e qualificação

        Args:
            business_type: Tipo de negócio para filtrar (opcional)

        Returns:
            Lista de leads qualificados
        """
        logger.info(f"Iniciando pipeline de descoberta e qualificação")

        all_leads = []
        qualified_leads = []

        # 1. Fase de descoberta
        raw_businesses = []
        for location in self.target_locations:
            businesses = await self.discover_businesses(location, business_type)
            raw_businesses.extend(businesses)

            # Aguarda entre localizações para evitar rate limiting
            await asyncio.sleep(self.request_delay * 2)

        logger.info(f"Descobertas {len(raw_businesses)} empresas no total")

        # 2. Fase de análise e qualificação
        total = len(raw_businesses)
        count = 0
        batch_num = 1
        current_batch = []

        # Processa em batches
        for business in raw_businesses:
            current_batch.append(business)
            count += 1

            # Processa o batch quando atingir o tamanho ou no final
            if len(current_batch) >= self.batch_size or count == total:
                logger.info(f"Processando batch {batch_num}/{(total + self.batch_size - 1) // self.batch_size}")

                # Processa cada negócio no batch em paralelo
                tasks = [self.analyze_lead(business) for business in current_batch]
                leads = await asyncio.gather(*tasks)

                # Filtra leads válidos
                valid_leads = [lead for lead in leads if lead is not None]
                all_leads.extend(valid_leads)

                # Filtra leads qualificados
                batch_qualified = [lead for lead in valid_leads if lead.qualification_score >= self.min_score]
                qualified_leads.extend(batch_qualified)

                logger.info(f"Batch {batch_num}: {len(valid_leads)} leads válidos, {len(batch_qualified)} qualificados")

                # Limpa batch e incrementa contador
                current_batch = []
                batch_num += 1

                # Verifica se já atingimos o número alvo de leads qualificados
                if len(qualified_leads) >= self.target_count:
                    logger.info(f"Atingido número alvo de {self.target_count} leads qualificados")
                    break

                # Aguarda entre batches para evitar rate limiting
                await asyncio.sleep(self.request_delay * 2)

        # Ordena por score de qualificação
        qualified_leads.sort(key=lambda x: x.qualification_score, reverse=True)

        logger.info(f"Pipeline concluído: {len(all_leads)} leads válidos, {len(qualified_leads)} qualificados")
        return qualified_leads

    def save_results(self, leads: List[Lead], output_prefix: str = None) -> Dict[str, str]:
        """Salva os resultados em diferentes formatos

        Args:
            leads: Lista de leads qualificados
            output_prefix: Prefixo para os arquivos de saída

        Returns:
            Dicionário com os caminhos dos arquivos gerados
        """
        if not leads:
            logger.warning("Nenhum lead para salvar")
            return {}

        # Cria diretório de resultados se não existir
        os.makedirs("results", exist_ok=True)

        # Gera timestamp para os arquivos
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = output_prefix or f"real_leads_{timestamp}"

        # Converte leads para dicionários
        leads_dict = []
        for lead in leads:
            lead_dict = {
                "business_name": lead.business_name,
                "domain": lead.domain,
                "industry": lead.industry,
                "location": lead.location,
                "revenue_estimate": lead.revenue_estimate,
                "employee_count": lead.employee_count,
                "performance_score": lead.performance_score,
                "lcp_mobile": lead.lcp_mobile,
                "cls_mobile": lead.cls_mobile,
                "fcp_mobile": lead.fcp_mobile,
                "performance_issues": lead.performance_issues,
                "tech_stack": lead.tech_stack,
                "cms_platform": lead.cms_platform,
                "ecommerce_platform": lead.ecommerce_platform,
                "marketing_tools": lead.marketing_tools,
                "qualification_score": lead.qualification_score,
                "icp_match": lead.icp_match,
                "pain_points": lead.pain_points,
                "revenue_opportunity": lead.revenue_opportunity,
                "approach_strategy": lead.approach_strategy,
                "urgency_level": lead.urgency_level,
                "last_updated": lead.last_updated.isoformat()
            }
            leads_dict.append(lead_dict)

        output_files = {}

        # Salva JSON
        json_path = f"results/{prefix}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(leads_dict, f, ensure_ascii=False, indent=2)
        output_files["json"] = json_path
        logger.info(f"Resultados salvos em JSON: {json_path}")

        # Salva CSV
        try:
            import pandas as pd

            # Simplifica dados para CSV
            csv_data = []
            for lead in leads:
                csv_lead = {
                    "business_name": lead.business_name,
                    "domain": lead.domain,
                    "industry": lead.industry,
                    "qualification_score": lead.qualification_score,
                    "icp_match": lead.icp_match,
                    "lcp_mobile": lead.lcp_mobile,
                    "performance_score": lead.performance_score,
                    "tech_stack": ", ".join(lead.tech_stack),
                    "revenue_estimate": lead.revenue_estimate,
                    "approach_strategy": lead.approach_strategy,
                    "urgency_level": lead.urgency_level
                }
                csv_data.append(csv_lead)

            # Cria DataFrame e salva
            df = pd.DataFrame(csv_data)
            csv_path = f"results/{prefix}.csv"
            df.to_csv(csv_path, index=False, encoding="utf-8")
            output_files["csv"] = csv_path
            logger.info(f"Resultados salvos em CSV: {csv_path}")

        except ImportError:
            logger.warning("Pandas não encontrado. Não foi possível salvar CSV.")

        # Gera relatório markdown
        report_path = f"results/{prefix}_report.md"
        report_content = self._generate_report(leads)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        output_files["report"] = report_path
        logger.info(f"Relatório gerado: {report_path}")

        return output_files

    def _generate_report(self, leads: List[Lead]) -> str:
        """Gera um relatório em markdown com insights sobre os leads

        Args:
            leads: Lista de leads qualificados

        Returns:
            Conteúdo do relatório em markdown
        """
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")

        # Cabeçalho do relatório
        report = f"# Relatório de Leads Qualificados ARCO\n\n"
        report += f"**Data da análise:** {timestamp}\n\n"
        report += f"**Total de leads qualificados:** {len(leads)}\n\n"

        # Distribuição de scores
        score_ranges = {
            "90-100": 0,
            "80-89": 0,
            "70-79": 0,
            "60-69": 0,
            "0-59": 0
        }

        for lead in leads:
            score = lead.qualification_score
            if score >= 90:
                score_ranges["90-100"] += 1
            elif score >= 80:
                score_ranges["80-89"] += 1
            elif score >= 70:
                score_ranges["70-79"] += 1
            elif score >= 60:
                score_ranges["60-69"] += 1
            else:
                score_ranges["0-59"] += 1

        report += "## Distribuição de Scores\n\n"
        report += "| Range | Quantidade | Percentual |\n"
        report += "|-------|------------|------------|\n"

        for range_name, count in score_ranges.items():
            percent = (count / len(leads)) * 100 if leads else 0
            report += f"| {range_name} | {count} | {percent:.1f}% |\n"

        report += "\n"

        # Distribuição de ICPs
        icp_counts = {"P1": 0, "P2": 0, "P3": 0, "P4": 0, "Outros": 0}

        for lead in leads:
            if lead.icp_match in icp_counts:
                icp_counts[lead.icp_match] += 1
            else:
                icp_counts["Outros"] += 1

        report += "## Distribuição de ICPs\n\n"
        report += "| ICP | Descrição | Quantidade | Percentual |\n"
        report += "|-----|-----------|------------|------------|\n"

        for icp, count in icp_counts.items():
            if icp != "Outros":
                percent = (count / len(leads)) * 100 if leads else 0
                desc = self.icps.get(icp, {}).get("name", "")
                report += f"| {icp} | {desc} | {count} | {percent:.1f}% |\n"
            elif count > 0:
                percent = (count / len(leads)) * 100
                report += f"| Outros | Sem match claro | {count} | {percent:.1f}% |\n"

        report += "\n"

        # Top 10 leads
        report += "## Top 10 Leads\n\n"

        for i, lead in enumerate(leads[:10], 1):
            report += f"### {i}. {lead.business_name} ({lead.domain})\n\n"
            report += f"**Score:** {lead.qualification_score} | **ICP:** {lead.icp_match} | **Urgência:** {lead.urgency_level}\n\n"
            report += f"**Industry:** {lead.industry}\n\n"
            report += f"**Tech Stack:** {', '.join(lead.tech_stack)}\n\n"

            report += "**Performance Issues:**\n\n"
            for issue in lead.performance_issues:
                report += f"- {issue}\n"

            report += "\n**Estratégia:** {lead.approach_strategy}\n\n"
            report += "---\n\n"

        # Insights e recomendações
        report += "## Insights e Recomendações\n\n"

        # Tech stack insights
        tech_counts = {}
        for lead in leads:
            for tech in lead.tech_stack:
                tech_counts[tech] = tech_counts.get(tech, 0) + 1

        top_techs = sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        report += "### Tech Stack Predominante\n\n"
        for tech, count in top_techs:
            percent = (count / len(leads)) * 100
            report += f"- **{tech}**: {count} leads ({percent:.1f}%)\n"

        report += "\n"

        # Performance insights
        avg_lcp = sum(lead.lcp_mobile for lead in leads) / len(leads) if leads else 0
        avg_perf_score = sum(lead.performance_score for lead in leads) / len(leads) if leads else 0

        report += "### Métricas de Performance\n\n"
        report += f"- **LCP Médio:** {avg_lcp:.1f}s\n"
        report += f"- **Performance Score Médio:** {avg_perf_score:.0f}/100\n\n"

        return report
