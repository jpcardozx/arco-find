"""Engine de Estimativa de Receita

Módulo responsável por estimar a receita de empresas com base em
múltiplos indicadores e heurísticas.
"""

import logging
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from src.models.lead import Lead

# Configuração de logging
logger = logging.getLogger("arco.revenue_engine")


class ConfidenceLevel(Enum):
    """Níveis de confiança para estimativas"""
    VERY_LOW = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    VERY_HIGH = auto()


@dataclass
class RevenueEstimate:
    """Modelo para estimativa de receita

    Armazena dados de estimativa de receita com indicadores de confiança
    e metodologia utilizada.
    """
    min_annual: float
    max_annual: float
    confidence_level: ConfidenceLevel
    confidence_score: int
    data_sources: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    range_string: str = ""

    def __post_init__(self):
        """Gera string de range para apresentação"""
        if not self.range_string:
            currency = "R$" if self.min_annual < 1000000 else "US$"

            if self.min_annual >= 1000000:
                min_fmt = f"{self.min_annual/1000000:.1f}M"
                max_fmt = f"{self.max_annual/1000000:.1f}M"
            elif self.min_annual >= 1000:
                min_fmt = f"{self.min_annual/1000:.0f}k"
                max_fmt = f"{self.max_annual/1000:.0f}k"
            else:
                min_fmt = f"{self.min_annual:.0f}"
                max_fmt = f"{self.max_annual:.0f}"

            self.range_string = f"{currency} {min_fmt}-{max_fmt}/ano"


class RevenueEstimator:
    """Engine para estimativa de receita de empresas

    Utiliza múltiplos indicadores para estimar a receita anual de empresas:
    - Indústria e benchmarks
    - Complexidade tecnológica
    - Localização e classificação
    - Maturidade digital
    - Qualidade do website
    """

    def __init__(self):
        """Inicializa o engine com benchmarks e configurações"""
        # Benchmarks de indústria (valores anuais médios em BRL)
        self.industry_benchmarks = {
            "E-commerce": {
                "small": (500000, 3000000),  # 500k - 3M
                "medium": (3000000, 15000000),  # 3M - 15M
                "large": (15000000, 50000000)  # 15M - 50M
            },
            "Retail": {
                "small": (300000, 2000000),  # 300k - 2M
                "medium": (2000000, 10000000),  # 2M - 10M
                "large": (10000000, 40000000)  # 10M - 40M
            },
            "Food & Beverage": {
                "small": (200000, 1500000),  # 200k - 1.5M
                "medium": (1500000, 8000000),  # 1.5M - 8M
                "large": (8000000, 30000000)  # 8M - 30M
            },
            "Healthcare": {
                "small": (400000, 2500000),  # 400k - 2.5M
                "medium": (2500000, 12000000),  # 2.5M - 12M
                "large": (12000000, 50000000)  # 12M - 50M
            },
            "Professional Services": {
                "small": (300000, 2000000),  # 300k - 2M
                "medium": (2000000, 7000000),  # 2M - 7M
                "large": (7000000, 25000000)  # 7M - 25M
            },
            "Real Estate": {
                "small": (500000, 3000000),  # 500k - 3M
                "medium": (3000000, 15000000),  # 3M - 15M
                "large": (15000000, 80000000)  # 15M - 80M
            },
            "Fashion Retail": {
                "small": (400000, 2500000),  # 400k - 2.5M
                "medium": (2500000, 12000000),  # 2.5M - 12M
                "large": (12000000, 50000000)  # 12M - 50M
            },
            "Beauty & Wellness": {
                "small": (200000, 1200000),  # 200k - 1.2M
                "medium": (1200000, 5000000),  # 1.2M - 5M
                "large": (5000000, 20000000)  # 5M - 20M
            },
            "Fitness": {
                "small": (300000, 1500000),  # 300k - 1.5M
                "medium": (1500000, 6000000),  # 1.5M - 6M
                "large": (6000000, 15000000)  # 6M - 15M
            },
            "Education": {
                "small": (500000, 3000000),  # 500k - 3M
                "medium": (3000000, 10000000),  # 3M - 10M
                "large": (10000000, 50000000)  # 10M - 50M
            },
            "General Business": {
                "small": (200000, 1500000),  # 200k - 1.5M
                "medium": (1500000, 7000000),  # 1.5M - 7M
                "large": (7000000, 25000000)  # 7M - 25M
            }
        }

    def estimate_revenue(self, lead: Lead) -> Dict[str, Any]:
        """Estima a receita para um lead

        Args:
            lead: Objeto Lead com dados do lead

        Returns:
            Dicionário com estimativa de receita e dados relacionados
        """
        # Coleta indicadores de receita
        indicators = self._collect_revenue_indicators(lead)

        # Identifica indústria e categoria de tamanho
        industry = self._identify_industry(lead)

        # Calcula complexidade tecnológica
        tech_complexity = self._calculate_tech_complexity(lead)

        # Avalia maturidade digital
        digital_maturity = self._assess_digital_maturity(lead)

        # Classifica localização
        location_tier = self._classify_location_tier(lead)

        # Calcula indicadores de qualidade do website
        website_quality = self._assess_website_quality(lead)

        # Estima com base em diferentes métodos
        estimates = [
            self._estimate_from_reviews(lead),
            self._estimate_from_tech_complexity(lead, tech_complexity),
            self._estimate_from_location_rating(lead, location_tier),
            self._estimate_from_digital_maturity(lead, digital_maturity)
        ]

        # Consolida estimativas
        consolidated = self._consolidate_estimates(estimates, industry)

        # Determina nível de confiança
        confidence = self._calculate_confidence(lead, estimates)
        confidence_level = self._determine_confidence_level(confidence)

        # Cria estimativa final
        revenue_estimate = RevenueEstimate(
            min_annual=consolidated[0],
            max_annual=consolidated[1],
            confidence_level=confidence_level,
            confidence_score=confidence,
            data_sources=indicators.get("data_sources", []),
            assumptions=indicators.get("assumptions", [])
        )

        # Estima número de funcionários
        employee_estimate = self._estimate_employee_count(revenue_estimate)

        return {
            "revenue_estimate": revenue_estimate.range_string,
            "employee_count": employee_estimate,
            "confidence_level": confidence_level.name,
            "confidence_score": confidence
        }

    def _collect_revenue_indicators(self, lead: Lead) -> Dict[str, Any]:
        """Coleta indicadores de receita do lead

        Args:
            lead: Objeto Lead

        Returns:
            Dicionário com indicadores coletados
        """
        indicators = {
            "data_sources": [],
            "assumptions": []
        }

        # Reviews como indicador
        if lead.review_count > 0:
            indicators["data_sources"].append("Google Reviews")

        # Tech stack como indicador
        if lead.tech_stack:
            indicators["data_sources"].append("Tech Stack Analysis")

        # Performance como indicador
        if lead.performance_score > 0:
            indicators["data_sources"].append("Website Performance")

        # Assumptions baseadas na indústria
        if lead.industry:
            indicators["assumptions"].append(f"Industry benchmarks for {lead.industry}")

        return indicators

    def _identify_industry(self, lead: Lead) -> str:
        """Identifica a indústria do lead para benchmarking

        Args:
            lead: Objeto Lead

        Returns:
            Nome da indústria normalizado para benchmarking
        """
        # Usa a indústria já identificada se disponível e válida
        if lead.industry in self.industry_benchmarks:
            return lead.industry

        # Tenta mapear para categorias conhecidas
        industry_mapping = {
            "restaurant": "Food & Beverage",
            "food": "Food & Beverage",
            "cafe": "Food & Beverage",
            "store": "Retail",
            "shop": "Retail",
            "clothing": "Fashion Retail",
            "fashion": "Fashion Retail",
            "health": "Healthcare",
            "clinic": "Healthcare",
            "hospital": "Healthcare",
            "school": "Education",
            "university": "Education",
            "college": "Education",
            "real estate": "Real Estate",
            "property": "Real Estate",
            "consultant": "Professional Services",
            "consulting": "Professional Services",
            "law": "Professional Services",
            "beauty": "Beauty & Wellness",
            "salon": "Beauty & Wellness",
            "spa": "Beauty & Wellness",
            "gym": "Fitness",
            "fitness": "Fitness",
            "e-commerce": "E-commerce",
            "ecommerce": "E-commerce",
            "online store": "E-commerce"
        }

        # Tenta identificar pelo nome do negócio
        name_lower = lead.business_name.lower()
        for keyword, industry in industry_mapping.items():
            if keyword in name_lower:
                return industry

        # Identifica pelo tech stack
        if any(tech in ["Shopify", "WooCommerce", "Magento", "VTEX"] for tech in lead.tech_stack):
            return "E-commerce"

        # Default
        return "General Business"

    def _calculate_tech_complexity(self, lead: Lead) -> int:
        """Calcula a complexidade tecnológica do lead

        Args:
            lead: Objeto Lead

        Returns:
            Score de complexidade tecnológica (0-100)
        """
        score = 0

        # Base pela quantidade de tecnologias
        tech_count = len(lead.tech_stack)
        score += min(tech_count * 5, 30)  # Máx 30 pontos pela quantidade

        # Pontos adicionais para plataformas específicas
        platform_scores = {
            "Shopify": 15,
            "Shopify Plus": 25,
            "Magento": 20,
            "Magento 2": 25,
            "WooCommerce": 10,
            "VTEX": 20,
            "BigCommerce": 15,
            "Salesforce Commerce": 30,
            "WordPress": 5,
            "Drupal": 10,
            "React": 15,
            "Angular": 15,
            "Vue": 12
        }

        for tech in lead.tech_stack:
            if tech in platform_scores:
                score += platform_scores[tech]

        # Pontos para ferramentas de marketing
        marketing_tools = len(lead.marketing_tools)
        score += min(marketing_tools * 5, 15)  # Máx 15 pontos

        # Normaliza para 0-100
        return min(score, 100)

    def _assess_digital_maturity(self, lead: Lead) -> int:
        """Avalia a maturidade digital do lead

        Args:
            lead: Objeto Lead

        Returns:
            Score de maturidade digital (0-100)
        """
        score = 0

        # Base pelo tech stack
        tech_complexity = self._calculate_tech_complexity(lead)
        score += tech_complexity * 0.4  # 40% do peso

        # Performance do site como indicador de investimento
        perf_score = lead.performance_score
        if perf_score > 0:
            score += min(perf_score * 0.3, 30)  # Até 30 pontos

        # Presença em redes sociais
        social_presence = len(lead.social_presence)
        score += min(social_presence * 5, 15)  # Até 15 pontos

        # E-commerce como indicador de maturidade
        if lead.ecommerce_platform:
            score += 15

        # Normaliza para 0-100
        return min(int(score), 100)

    def _classify_location_tier(self, lead: Lead) -> int:
        """Classifica a localização em tiers de valor

        Args:
            lead: Objeto Lead

        Returns:
            Tier da localização (1-5, sendo 5 o mais valioso)
        """
        location = lead.location.lower()

        # Tier 5 - Localizações premium
        tier5_locations = ["jardins", "itaim", "leblon", "ipanema", "barra da tijuca", "são paulo, sp"]
        for loc in tier5_locations:
            if loc in location:
                return 5

        # Tier 4 - Centros urbanos grandes
        tier4_locations = ["são paulo", "rio de janeiro", "belo horizonte", "brasília", "curitiba"]
        for loc in tier4_locations:
            if loc in location:
                return 4

        # Tier 3 - Cidades médias ou áreas comerciais
        tier3_locations = ["campinas", "porto alegre", "recife", "fortaleza", "salvador", "centro"]
        for loc in tier3_locations:
            if loc in location:
                return 3

        # Tier 2 - Cidades menores ou áreas residenciais
        tier2_locations = ["ribeirão preto", "são josé", "joinville", "londrina", "residencial"]
        for loc in tier2_locations:
            if loc in location:
                return 2

        # Tier 1 - Default
        return 1

    def _assess_website_quality(self, lead: Lead) -> int:
        """Avalia a qualidade do website como indicador de investimento

        Args:
            lead: Objeto Lead

        Returns:
            Score de qualidade do website (0-100)
        """
        score = 0

        # Performance como indicador de qualidade
        perf_score = lead.performance_score
        score += min(perf_score, 40)  # Até 40 pontos

        # LCP como indicador (invertido - quanto menor, melhor)
        lcp = lead.lcp_mobile
        if lcp > 0:
            lcp_score = max(0, 30 - (lcp * 5))  # Penaliza LCP alto
            score += lcp_score

        # Tech stack como indicador de investimento
        tech_count = min(len(lead.tech_stack), 6)
        score += tech_count * 5  # Até 30 pontos

        # Normaliza para 0-100
        return min(int(score), 100)

    def _estimate_from_reviews(self, lead: Lead) -> Tuple[float, float]:
        """Estima receita com base em reviews

        Args:
            lead: Objeto Lead

        Returns:
            Tupla (min, max) de estimativa anual
        """
        review_count = lead.review_count

        # Sem reviews, retorna zero
        if review_count <= 0:
            return (0, 0)

        # Diferentes multiplicadores por indústria
        review_multipliers = {
            "E-commerce": (15000, 30000),
            "Retail": (10000, 25000),
            "Food & Beverage": (8000, 20000),
            "Healthcare": (12000, 30000),
            "Professional Services": (15000, 40000),
            "Real Estate": (20000, 50000),
            "General Business": (10000, 25000)
        }

        industry = self._identify_industry(lead)
        multiplier = review_multipliers.get(industry, (10000, 25000))

        min_estimate = review_count * multiplier[0]
        max_estimate = review_count * multiplier[1]

        return (min_estimate, max_estimate)

    def _estimate_from_tech_complexity(self, lead: Lead, tech_complexity: int) -> Tuple[float, float]:
        """Estima receita com base na complexidade tecnológica

        Args:
            lead: Objeto Lead
            tech_complexity: Score de complexidade tecnológica

        Returns:
            Tupla (min, max) de estimativa anual
        """
        if tech_complexity <= 0:
            return (0, 0)

        # Diferentes bases por indústria
        tech_bases = {
            "E-commerce": (500000, 1000000),
            "Retail": (300000, 800000),
            "Food & Beverage": (200000, 500000),
            "Healthcare": (400000, 1000000),
            "Professional Services": (300000, 800000),
            "Real Estate": (400000, 1200000),
            "General Business": (200000, 600000)
        }

        industry = self._identify_industry(lead)
        base = tech_bases.get(industry, (200000, 600000))

        # Multiplicador baseado na complexidade
        multiplier = tech_complexity / 50  # 0-2 range

        min_estimate = base[0] * multiplier
        max_estimate = base[1] * multiplier

        return (min_estimate, max_estimate)

    def _estimate_from_location_rating(self, lead: Lead, location_tier: int) -> Tuple[float, float]:
        """Estima receita com base na classificação da localização

        Args:
            lead: Objeto Lead
            location_tier: Tier da localização (1-5)

        Returns:
            Tupla (min, max) de estimativa anual
        """
        # Diferentes bases por tier
        tier_bases = {
            5: (1000000, 5000000),
            4: (500000, 3000000),
            3: (300000, 1500000),
            2: (200000, 800000),
            1: (100000, 500000)
        }

        base = tier_bases.get(location_tier, (100000, 500000))

        # Ajusta por indústria
        industry = self._identify_industry(lead)
        industry_multipliers = {
            "E-commerce": 1.0,  # Não afetado pela localização física
            "Retail": 1.5,
            "Food & Beverage": 1.2,
            "Healthcare": 1.3,
            "Professional Services": 1.4,
            "Real Estate": 2.0,
            "General Business": 1.0
        }

        multiplier = industry_multipliers.get(industry, 1.0)

        min_estimate = base[0] * multiplier
        max_estimate = base[1] * multiplier

        return (min_estimate, max_estimate)

    def _estimate_from_digital_maturity(self, lead: Lead, digital_maturity: int) -> Tuple[float, float]:
        """Estima receita com base na maturidade digital

        Args:
            lead: Objeto Lead
            digital_maturity: Score de maturidade digital

        Returns:
            Tupla (min, max) de estimativa anual
        """
        if digital_maturity <= 0:
            return (0, 0)

        # Diferentes bases por indústria
        maturity_bases = {
            "E-commerce": (800000, 2000000),
            "Retail": (500000, 1500000),
            "Food & Beverage": (300000, 1000000),
            "Healthcare": (600000, 1800000),
            "Professional Services": (500000, 1500000),
            "Real Estate": (700000, 2000000),
            "General Business": (400000, 1200000)
        }

        industry = self._identify_industry(lead)
        base = maturity_bases.get(industry, (400000, 1200000))

        # Multiplicador baseado na maturidade
        multiplier = digital_maturity / 50  # 0-2 range

        min_estimate = base[0] * multiplier
        max_estimate = base[1] * multiplier

        return (min_estimate, max_estimate)

    def _consolidate_estimates(self, estimates: List[Tuple[float, float]], industry: str) -> Tuple[float, float]:
        """Consolida múltiplas estimativas em uma única

        Args:
            estimates: Lista de estimativas (min, max)
            industry: Indústria identificada

        Returns:
            Tupla (min, max) consolidada
        """
        # Filtra estimativas válidas (não-zero)
        valid_estimates = [est for est in estimates if est[0] > 0 and est[1] > 0]

        if not valid_estimates:
            # Usa benchmark da indústria como fallback
            benchmark = self.industry_benchmarks.get(industry, self.industry_benchmarks["General Business"])
            return benchmark["small"]

        # Calcula médias ponderadas
        total_min = 0
        total_max = 0
        weights = [0.3, 0.3, 0.2, 0.2]  # Pesos para cada método

        for i, estimate in enumerate(valid_estimates):
            weight = weights[i] if i < len(weights) else 0.1
            total_min += estimate[0] * weight
            total_max += estimate[1] * weight

        # Normaliza se não temos todas as estimativas
        weight_sum = sum(weights[:len(valid_estimates)])
        if weight_sum > 0 and weight_sum < 1:
            total_min /= weight_sum
            total_max /= weight_sum

        # Aplica limites de sanidade baseados na indústria
        benchmark = self.industry_benchmarks.get(industry, self.industry_benchmarks["General Business"])

        min_annual = max(total_min, benchmark["small"][0] * 0.5)  # No mínimo 50% do benchmark mínimo
        max_annual = min(total_max, benchmark["large"][1] * 1.5)  # No máximo 150% do benchmark máximo

        return (min_annual, max_annual)

    def _calculate_confidence(self, lead: Lead, estimates: List[Tuple[float, float]]) -> int:
        """Calcula o score de confiança da estimativa

        Args:
            lead: Objeto Lead
            estimates: Lista de estimativas utilizadas

        Returns:
            Score de confiança (0-100)
        """
        confidence = 0

        # Quantidade de estimativas válidas
        valid_estimates = [est for est in estimates if est[0] > 0 and est[1] > 0]
        estimation_count = len(valid_estimates)
        confidence += estimation_count * 15  # Até 60 pontos

        # Consistência entre estimativas
        if estimation_count >= 2:
            min_values = [est[0] for est in valid_estimates]
            max_values = [est[1] for est in valid_estimates]

            min_range = max(min_values) - min(min_values)
            max_range = max(max_values) - min(max_values)

            avg_min = sum(min_values) / len(min_values)
            avg_max = sum(max_values) / len(max_values)

            # Menor variação = maior confiança
            if avg_min > 0 and avg_max > 0:
                min_variation = min_range / avg_min
                max_variation = max_range / avg_max

                avg_variation = (min_variation + max_variation) / 2
                consistency_score = max(0, 20 - (avg_variation * 10))
                confidence += min(consistency_score, 20)  # Até 20 pontos

        # Qualidade dos dados disponíveis
        if lead.review_count > 50:
            confidence += 10
        elif lead.review_count > 10:
            confidence += 5

        if len(lead.tech_stack) > 3:
            confidence += 10
        elif len(lead.tech_stack) > 0:
            confidence += 5

        return min(confidence, 100)

    def _determine_confidence_level(self, confidence_score: int) -> ConfidenceLevel:
        """Determina o nível de confiança baseado no score

        Args:
            confidence_score: Score de confiança (0-100)

        Returns:
            Nível de confiança
        """
        if confidence_score >= 90:
            return ConfidenceLevel.VERY_HIGH
        elif confidence_score >= 70:
            return ConfidenceLevel.HIGH
        elif confidence_score >= 50:
            return ConfidenceLevel.MEDIUM
        elif confidence_score >= 30:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

    def _estimate_employee_count(self, revenue_estimate: RevenueEstimate) -> str:
        """Estima o número de funcionários com base na receita

        Args:
            revenue_estimate: Estimativa de receita

        Returns:
            String com range de funcionários
        """
        # Média das estimativas
        avg_revenue = (revenue_estimate.min_annual + revenue_estimate.max_annual) / 2

        # Diferentes faixas baseadas na receita média
        if avg_revenue < 500000:  # <500k
            return "1-5"
        elif avg_revenue < 2000000:  # 500k-2M
            return "5-15"
        elif avg_revenue < 5000000:  # 2M-5M
            return "15-30"
        elif avg_revenue < 10000000:  # 5M-10M
            return "30-50"
        elif avg_revenue < 20000000:  # 10M-20M
            return "50-100"
        elif avg_revenue < 50000000:  # 20M-50M
            return "100-250"
        else:  # >50M
            return "250+"
