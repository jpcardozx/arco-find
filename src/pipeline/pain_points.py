"""Engine de Análise de Pain Points

Módulo responsável por identificar problemas e oportunidades
em websites, com quantificação de impacto financeiro.
"""

import logging
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from src.models.lead import RealLead

# Configuração de logging
logger = logging.getLogger("arco.pain_points_engine")


class PainSeverity(Enum):
    """Níveis de severidade para pain points"""
    CRITICAL = auto()
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()


class OpportunityType(Enum):
    """Tipos de oportunidades de melhoria"""
    CONVERSION_RATE = auto()
    PERFORMANCE = auto()
    SEO_RANKING = auto()
    USER_EXPERIENCE = auto()
    TECHNICAL_DEBT = auto()
    MOBILE_OPTIMIZATION = auto()


@dataclass
class PainPoint:
    """Modelo para um pain point identificado

    Representa um problema ou oportunidade de melhoria identificado
    no website de um lead, com quantificação de impacto.
    """
    description: str
    severity: PainSeverity
    opportunity_type: OpportunityType
    estimated_monthly_loss: float
    estimated_annual_opportunity: float
    implementation_effort: str
    roi_potential: str
    confidence_level: str
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    actionable_next_steps: List[str] = field(default_factory=list)


@dataclass
class OpportunityCalculation:
    """Resultado completo do cálculo de oportunidades

    Representa o conjunto completo de oportunidades identificadas
    para um lead, com agregações e metodologia.
    """
    total_annual_opportunity: float
    confidence_score: int
    pain_points: List[PainPoint] = field(default_factory=list)
    quick_wins: List[PainPoint] = field(default_factory=list)
    major_improvements: List[PainPoint] = field(default_factory=list)
    methodology: str = ""
    assumptions: List[str] = field(default_factory=list)


class PainPointsAnalyzer:
    """Engine para análise de pain points e oportunidades

    Identifica problemas e oportunidades de melhoria em websites,
    quantificando o impacto financeiro e priorizando ações.
    """

    def __init__(self):
        """Inicializa o engine com benchmarks e configurações"""
        # Impacto da performance em taxas de conversão
        self.performance_impact = {
            "lcp": {
                # Segundos : % perda
                2.5: 0,      # Bom (referência)
                3.0: 7,      # Precisa melhorar
                3.5: 10,     # Precisa melhorar
                4.0: 17,     # Ruim
                4.5: 24,     # Ruim
                5.0: 32,     # Ruim
                5.5: 38,     # Crítico
                6.0: 45,     # Crítico
                6.5: 52,     # Crítico
                7.0: 58,     # Crítico
                7.5: 65,     # Crítico
                8.0: 70,     # Crítico
                10.0: 85,    # Crítico
            },
            "cls": {
                # CLS : % perda
                0.1: 0,      # Bom (referência)
                0.15: 5,     # Precisa melhorar
                0.2: 8,      # Precisa melhorar
                0.25: 12,    # Ruim
                0.3: 15,     # Ruim
                0.4: 20,     # Crítico
                0.5: 25,     # Crítico
            },
            "fcp": {
                # Segundos : % perda
                1.8: 0,      # Bom (referência)
                2.0: 3,      # Precisa melhorar
                2.5: 5,      # Precisa melhorar
                3.0: 8,      # Ruim
                3.5: 10,     # Ruim
                4.0: 12,     # Crítico
                5.0: 15,     # Crítico
            }
        }

        # Benchmarks de taxas de conversão por indústria
        self.conversion_benchmarks = {
            "E-commerce": {
                "average": 2.5,            # %
                "good": 3.6,               # %
                "mobile_discount": 0.7,    # Fator multiplicador para mobile
                "revenue_per_conversion": 180,  # Valor médio de pedido
            },
            "Retail": {
                "average": 2.2,
                "good": 3.3,
                "mobile_discount": 0.6,
                "revenue_per_conversion": 150,
            },
            "Professional Services": {
                "average": 3.0,
                "good": 5.0,
                "mobile_discount": 0.5,
                "revenue_per_conversion": 500,  # Valor médio de lead
            },
            "Healthcare": {
                "average": 3.2,
                "good": 5.5,
                "mobile_discount": 0.6,
                "revenue_per_conversion": 300,
            },
            "Real Estate": {
                "average": 2.0,
                "good": 4.0,
                "mobile_discount": 0.5,
                "revenue_per_conversion": 800,
            },
            "Food & Beverage": {
                "average": 1.5,
                "good": 3.0,
                "mobile_discount": 0.8,
                "revenue_per_conversion": 50,
            },
            "Beauty & Wellness": {
                "average": 2.8,
                "good": 4.5,
                "mobile_discount": 0.7,
                "revenue_per_conversion": 120,
            },
            "Fitness": {
                "average": 2.5,
                "good": 4.0,
                "mobile_discount": 0.6,
                "revenue_per_conversion": 200,
            },
            "Education": {
                "average": 2.8,
                "good": 4.8,
                "mobile_discount": 0.5,
                "revenue_per_conversion": 1000,
            },
            "General Business": {
                "average": 2.0,
                "good": 3.5,
                "mobile_discount": 0.6,
                "revenue_per_conversion": 200,
            }
        }

    def analyze(self, lead: RealLead) -> Dict[str, Any]:
        """Analisa pain points e oportunidades para um lead

        Args:
            lead: Objeto RealLead com dados do lead

        Returns:
            Dicionário com pain points e oportunidades identificadas
        """
        # Identifica indústria
        industry = self._identify_industry(lead)

        # Estima tráfego mensal
        traffic_data = self._estimate_monthly_traffic(lead, industry)
        monthly_traffic = traffic_data.get("monthly_traffic", 0)

        # Análise de performance
        performance_pain_points = self._analyze_performance_pain_points(lead, monthly_traffic, industry)

        # Análise mobile
        mobile_pain_points = self._analyze_mobile_pain_points(lead, monthly_traffic, industry)

        # Análise de tech debt
        tech_debt_pain_points = self._analyze_technical_debt(lead)

        # Análise de oportunidades de conversão
        conversion_pain_points = self._analyze_conversion_opportunities(lead, monthly_traffic, industry)

        # Análise de SEO
        seo_pain_points = self._analyze_seo_opportunities(lead)

        # Combina todos os pain points
        all_pain_points = [
            *performance_pain_points,
            *mobile_pain_points,
            *tech_debt_pain_points,
            *conversion_pain_points,
            *seo_pain_points
        ]

        # Formata para o formato esperado da API
        formatted_pain_points = []
        total_opportunity = 0

        for pp in all_pain_points:
            # Calcula oportunidade anual
            annual_opportunity = pp.estimated_monthly_loss * 12
            total_opportunity += annual_opportunity

            # Formata para API
            formatted_pp = {
                "description": pp.description,
                "severity": pp.severity.name,
                "type": pp.opportunity_type.name,
                "monthly_loss": int(pp.estimated_monthly_loss),
                "annual_opportunity": int(annual_opportunity),
                "effort": pp.implementation_effort,
                "roi": pp.roi_potential,
                "next_steps": pp.actionable_next_steps
            }

            formatted_pain_points.append(formatted_pp)

        # Ordena por oportunidade
        formatted_pain_points.sort(key=lambda x: x["annual_opportunity"], reverse=True)

        # Calcula oportunidade total anual
        formatted_total = f"R$ {total_opportunity/1000:.0f}k/ano"

        return {
            "pain_points": formatted_pain_points,
            "revenue_opportunity": formatted_total,
            "monthly_traffic_estimate": monthly_traffic
        }

    def _identify_industry(self, lead: RealLead) -> str:
        """Identifica a indústria do lead para benchmarking

        Args:
            lead: Objeto RealLead

        Returns:
            Nome da indústria normalizado para benchmarking
        """
        # Usa a indústria já identificada se disponível e válida
        if lead.industry in self.conversion_benchmarks:
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

    def _estimate_monthly_traffic(self, lead: RealLead, industry: str) -> Dict[str, Any]:
        """Estima o tráfego mensal do website

        Esta é uma estimativa simplificada baseada em heurísticas.
        Uma implementação completa usaria dados de SEO ou integrações.

        Args:
            lead: Objeto RealLead
            industry: Indústria identificada

        Returns:
            Dicionário com estimativas de tráfego
        """
        # Heurística baseada em reviews e indústria
        review_count = lead.review_count

        # Fatores de multiplicação por indústria
        traffic_multipliers = {
            "E-commerce": 15,
            "Retail": 12,
            "Food & Beverage": 8,
            "Healthcare": 10,
            "Professional Services": 12,
            "Real Estate": 15,
            "Beauty & Wellness": 10,
            "Fitness": 12,
            "Education": 15,
            "General Business": 10
        }

        multiplier = traffic_multipliers.get(industry, 10)

        # Base de tráfego estimada por reviews
        base_traffic = 0
        if review_count > 0:
            base_traffic = review_count * multiplier

        # Ajusta por tech stack
        tech_factor = 1.0
        if len(lead.tech_stack) > 5:
            tech_factor = 1.5
        elif len(lead.tech_stack) > 2:
            tech_factor = 1.2

        # Ajusta por performance
        perf_factor = 1.0
        if lead.performance_score > 80:
            perf_factor = 1.3
        elif lead.performance_score > 60:
            perf_factor = 1.1
        elif lead.performance_score > 0 and lead.performance_score < 40:
            perf_factor = 0.8

        # Tráfego estimado
        estimated_traffic = max(500, base_traffic * tech_factor * perf_factor)

        # Adiciona variação baseada no e-commerce
        if lead.ecommerce_platform:
            if industry == "E-commerce":
                estimated_traffic *= 1.5
            else:
                estimated_traffic *= 1.2

        # Distribuição de dispositivos
        mobile_pct = 65  # Padrão: 65% mobile
        desktop_pct = 35

        # Ajusta por indústria
        if industry == "E-commerce":
            mobile_pct = 70
        elif industry == "Professional Services":
            mobile_pct = 55
        elif industry == "Food & Beverage":
            mobile_pct = 75

        return {
            "monthly_traffic": int(estimated_traffic),
            "mobile_pct": mobile_pct,
            "desktop_pct": desktop_pct,
            "mobile_traffic": int(estimated_traffic * mobile_pct / 100),
            "desktop_traffic": int(estimated_traffic * desktop_pct / 100)
        }

    def _analyze_performance_pain_points(self, lead: RealLead, monthly_traffic: int, industry: str) -> List[PainPoint]:
        """Analisa pain points relacionados à performance

        Args:
            lead: Objeto RealLead
            monthly_traffic: Tráfego mensal estimado
            industry: Indústria identificada

        Returns:
            Lista de pain points de performance
        """
        pain_points = []

        # Obtém benchmarks de conversão
        benchmarks = self.conversion_benchmarks.get(industry, self.conversion_benchmarks["General Business"])
        baseline_conversion = benchmarks["average"]
        revenue_per_conversion = benchmarks["revenue_per_conversion"]
        mobile_factor = benchmarks["mobile_discount"]

        # Estima conversões baseline
        monthly_conversions = (monthly_traffic * baseline_conversion / 100)
        monthly_revenue = monthly_conversions * revenue_per_conversion

        # Analisa LCP (Largest Contentful Paint)
        lcp = lead.lcp_mobile
        if lcp > 2.5:
            # Determina a perda com base nos benchmarks
            loss_pct = 0
            for threshold, impact in sorted(self.performance_impact["lcp"].items()):
                if lcp >= threshold:
                    loss_pct = impact
                else:
                    break

            if loss_pct > 0:
                # Estima perda financeira
                affected_traffic = monthly_traffic * 0.65  # Mobile traffic
                affected_conversions = (affected_traffic * baseline_conversion / 100) * (loss_pct / 100)
                monthly_loss = affected_conversions * revenue_per_conversion

                # Determina severidade
                severity = PainSeverity.MEDIUM
                if lcp >= 5.0:
                    severity = PainSeverity.CRITICAL
                elif lcp >= 4.0:
                    severity = PainSeverity.HIGH

                # Cria pain point
                pp = PainPoint(
                    description=f"LCP lento de {lcp:.1f}s afeta conversões em dispositivos móveis",
                    severity=severity,
                    opportunity_type=OpportunityType.PERFORMANCE,
                    estimated_monthly_loss=monthly_loss,
                    estimated_annual_opportunity=monthly_loss * 12,
                    implementation_effort="Médio",
                    roi_potential="Alto",
                    confidence_level="Alto",
                    supporting_data={
                        "lcp": lcp,
                        "loss_pct": loss_pct,
                        "affected_traffic": affected_traffic
                    },
                    actionable_next_steps=[
                        "Otimizar imagens e carregamento de recursos",
                        "Implementar técnicas de lazy loading",
                        "Revisar hosting e CDN"
                    ]
                )

                pain_points.append(pp)

        # Analisa CLS (Cumulative Layout Shift)
        cls = lead.cls_mobile
        if cls > 0.1:
            # Determina a perda com base nos benchmarks
            loss_pct = 0
            for threshold, impact in sorted(self.performance_impact["cls"].items()):
                if cls >= threshold:
                    loss_pct = impact
                else:
                    break

            if loss_pct > 0:
                # Estima perda financeira
                affected_traffic = monthly_traffic * 0.65  # Mobile traffic
                affected_conversions = (affected_traffic * baseline_conversion / 100) * (loss_pct / 100)
                monthly_loss = affected_conversions * revenue_per_conversion

                # Determina severidade
                severity = PainSeverity.MEDIUM
                if cls >= 0.4:
                    severity = PainSeverity.CRITICAL
                elif cls >= 0.25:
                    severity = PainSeverity.HIGH

                # Cria pain point
                pp = PainPoint(
                    description=f"Instabilidade visual (CLS: {cls:.2f}) prejudica experiência móvel",
                    severity=severity,
                    opportunity_type=OpportunityType.USER_EXPERIENCE,
                    estimated_monthly_loss=monthly_loss,
                    estimated_annual_opportunity=monthly_loss * 12,
                    implementation_effort="Médio",
                    roi_potential="Médio-Alto",
                    confidence_level="Médio-Alto",
                    supporting_data={
                        "cls": cls,
                        "loss_pct": loss_pct,
                        "affected_traffic": affected_traffic
                    },
                    actionable_next_steps=[
                        "Definir dimensões para elementos carregados dinamicamente",
                        "Estabilizar carregamento de fontes",
                        "Reservar espaço para anúncios e recursos externos"
                    ]
                )

                pain_points.append(pp)

        # Analisa FCP (First Contentful Paint)
        fcp = lead.fcp_mobile
        if fcp > 1.8:
            # Determina a perda com base nos benchmarks
            loss_pct = 0
            for threshold, impact in sorted(self.performance_impact["fcp"].items()):
                if fcp >= threshold:
                    loss_pct = impact
                else:
                    break

            if loss_pct > 0:
                # Estima perda financeira
                affected_traffic = monthly_traffic * 0.65  # Mobile traffic
                affected_conversions = (affected_traffic * baseline_conversion / 100) * (loss_pct / 100)
                monthly_loss = affected_conversions * revenue_per_conversion

                # Determina severidade
                severity = PainSeverity.MEDIUM
                if fcp >= 4.0:
                    severity = PainSeverity.HIGH
                elif fcp >= 3.0:
                    severity = PainSeverity.MEDIUM

                # Cria pain point
                pp = PainPoint(
                    description=f"Carregamento inicial lento (FCP: {fcp:.1f}s) aumenta taxa de abandono",
                    severity=severity,
                    opportunity_type=OpportunityType.PERFORMANCE,
                    estimated_monthly_loss=monthly_loss,
                    estimated_annual_opportunity=monthly_loss * 12,
                    implementation_effort="Médio",
                    roi_potential="Médio",
                    confidence_level="Médio",
                    supporting_data={
                        "fcp": fcp,
                        "loss_pct": loss_pct,
                        "affected_traffic": affected_traffic
                    },
                    actionable_next_steps=[
                        "Otimizar carregamento de CSS crítico",
                        "Reduzir bloqueio de renderização por JavaScript",
                        "Implementar resource hints (preconnect, preload)"
                    ]
                )

                pain_points.append(pp)

        # Performance score geral
        if lead.performance_score < 50:
            # Perda de visibilidade em SEO e experiência geral
            estimated_loss = monthly_revenue * 0.1  # Estimativa conservadora

            pp = PainPoint(
                description=f"Performance geral baixa (score: {lead.performance_score}) afeta SEO e conversões",
                severity=PainSeverity.HIGH,
                opportunity_type=OpportunityType.SEO_RANKING,
                estimated_monthly_loss=estimated_loss,
                estimated_annual_opportunity=estimated_loss * 12,
                implementation_effort="Alto",
                roi_potential="Alto",
                confidence_level="Médio",
                actionable_next_steps=[
                    "Auditoria completa de performance",
                    "Otimização de assets (imagens, scripts, CSS)",
                    "Implementação de estratégia de caching"
                ]
            )

            pain_points.append(pp)

        return pain_points

    def _analyze_mobile_pain_points(self, lead: RealLead, monthly_traffic: int, industry: str) -> List[PainPoint]:
        """Analisa pain points específicos para mobile

        Args:
            lead: Objeto RealLead
            monthly_traffic: Tráfego mensal estimado
            industry: Indústria identificada

        Returns:
            Lista de pain points mobile
        """
        pain_points = []

        # Obtém benchmarks de conversão
        benchmarks = self.conversion_benchmarks.get(industry, self.conversion_benchmarks["General Business"])
        baseline_conversion = benchmarks["average"]
        revenue_per_conversion = benchmarks["revenue_per_conversion"]
        mobile_factor = benchmarks["mobile_discount"]

        # Estima tráfego mobile
        mobile_traffic = monthly_traffic * 0.65  # 65% mobile em média

        # Gap de conversão mobile vs desktop (baseado no benchmark da indústria)
        # O gap representa a diferença entre a taxa de conversão mobile vs desktop
        mobile_conversion = baseline_conversion * mobile_factor
        desktop_conversion = baseline_conversion / (1 - (1 - mobile_factor) * 0.65)  # Ajuste para manter a média

        conversion_gap = desktop_conversion - mobile_conversion

        # Se a performance mobile for particularmente ruim
        if lead.lcp_mobile > 4.0 and lead.performance_score < 60:
            # Potencial de melhoria: reduzir o gap em 30-50%
            improvement_potential = conversion_gap * 0.4  # 40% de redução do gap

            # Conversões adicionais
            additional_conversions = mobile_traffic * improvement_potential / 100
            monthly_opportunity = additional_conversions * revenue_per_conversion

            pp = PainPoint(
                description="Experiência mobile significativamente inferior prejudica conversões",
                severity=PainSeverity.HIGH,
                opportunity_type=OpportunityType.MOBILE_OPTIMIZATION,
                estimated_monthly_loss=monthly_opportunity,
                estimated_annual_opportunity=monthly_opportunity * 12,
                implementation_effort="Alto",
                roi_potential="Alto",
                confidence_level="Médio-Alto",
                supporting_data={
                    "mobile_traffic": mobile_traffic,
                    "conversion_gap": conversion_gap,
                    "improvement_potential": improvement_potential
                },
                actionable_next_steps=[
                    "Auditoria de UX mobile",
                    "Otimização de formulários para mobile",
                    "Implementação de design responsivo avançado"
                ]
            )

            pain_points.append(pp)

        # Se o lead for e-commerce e tiver problemas de performance
        if lead.ecommerce_platform and lead.lcp_mobile > 3.5:
            # Problema específico de checkout mobile
            checkout_abandonment_increase = min(lead.lcp_mobile - 2.5, 5) * 3  # 3% para cada segundo acima de 2.5s, max 15%

            # Estima perda no checkout
            cart_sessions = mobile_traffic * 0.15  # ~15% das sessões chegam ao carrinho
            lost_checkouts = cart_sessions * (checkout_abandonment_increase / 100)
            monthly_opportunity = lost_checkouts * revenue_per_conversion

            pp = PainPoint(
                description="Abandono de checkout mobile elevado devido à performance",
                severity=PainSeverity.CRITICAL,
                opportunity_type=OpportunityType.CONVERSION_RATE,
                estimated_monthly_loss=monthly_opportunity,
                estimated_annual_opportunity=monthly_opportunity * 12,
                implementation_effort="Médio",
                roi_potential="Muito Alto",
                confidence_level="Alto",
                supporting_data={
                    "mobile_traffic": mobile_traffic,
                    "cart_sessions": cart_sessions,
                    "abandonment_increase": checkout_abandonment_increase
                },
                actionable_next_steps=[
                    "Otimização do fluxo de checkout",
                    "Redução de steps no processo de compra",
                    "Implementação de checkout progressivo"
                ]
            )

            pain_points.append(pp)

        return pain_points

    def _analyze_technical_debt(self, lead: RealLead) -> List[PainPoint]:
        """Analisa pain points relacionados à dívida técnica

        Args:
            lead: Objeto RealLead

        Returns:
            Lista de pain points de dívida técnica
        """
        pain_points = []

        # Detecção simplificada de dívida técnica
        tech_issues = []

        # Tecnologias desatualizadas ou problemáticas
        outdated_tech = {
            "jQuery": "Pode causar problemas de performance e segurança",
            "Flash": "Tecnologia obsoleta não suportada por navegadores modernos",
            "AngularJS": "Framework descontinuado com problemas de segurança"
        }

        for tech in lead.tech_stack:
            if tech in outdated_tech:
                tech_issues.append({
                    "tech": tech,
                    "issue": outdated_tech[tech]
                })

        # WordPress com muitos plugins = técnica dívida potencial
        if "WordPress" in lead.tech_stack and len(lead.tech_stack) > 8:
            tech_issues.append({
                "tech": "WordPress + plugins excessivos",
                "issue": "Excesso de plugins causa conflitos e problemas de performance"
            })

        # Combinações problemáticas
        if "WordPress" in lead.tech_stack and "Elementor" in lead.tech_stack:
            # Verifica outras combinações problemáticas
            if any(t in ["WPBakery", "Divi", "Visual Composer"] for t in lead.tech_stack):
                tech_issues.append({
                    "tech": "Múltiplos page builders",
                    "issue": "Conflito entre page builders causa problemas de performance"
                })

        # Cria pain points para cada issue técnico significativo
        for issue in tech_issues:
            # Estima impacto financeiro (simplificado)
            monthly_loss = 2000  # Valor conservador

            pp = PainPoint(
                description=f"Dívida técnica: {issue['tech']} - {issue['issue']}",
                severity=PainSeverity.MEDIUM,
                opportunity_type=OpportunityType.TECHNICAL_DEBT,
                estimated_monthly_loss=monthly_loss,
                estimated_annual_opportunity=monthly_loss * 12,
                implementation_effort="Médio-Alto",
                roi_potential="Médio",
                confidence_level="Médio",
                actionable_next_steps=[
                    "Auditoria técnica completa",
                    "Plano de migração para tecnologias modernas",
                    "Consolidação e simplificação da stack"
                ]
            )

            pain_points.append(pp)

        # Problemas específicos de e-commerce
        if lead.ecommerce_platform == "WooCommerce" and len(lead.tech_stack) > 10:
            pp = PainPoint(
                description="WooCommerce com excesso de plugins afeta estabilidade e conversão",
                severity=PainSeverity.HIGH,
                opportunity_type=OpportunityType.TECHNICAL_DEBT,
                estimated_monthly_loss=3000,  # Estimativa conservadora
                estimated_annual_opportunity=36000,
                implementation_effort="Alto",
                roi_potential="Alto",
                confidence_level="Médio-Alto",
                actionable_next_steps=[
                    "Auditoria de plugins WooCommerce",
                    "Remoção de plugins redundantes ou problemáticos",
                    "Implementação de soluções nativas para substituir plugins"
                ]
            )

            pain_points.append(pp)

        # Problemas de Shopify com muitos apps
        if lead.ecommerce_platform == "Shopify" and len(lead.tech_stack) > 12:
            pp = PainPoint(
                description="Shopify com excesso de apps prejudica performance e ROI",
                severity=PainSeverity.MEDIUM,
                opportunity_type=OpportunityType.TECHNICAL_DEBT,
                estimated_monthly_loss=2500,  # Estimativa conservadora
                estimated_annual_opportunity=30000,
                implementation_effort="Médio",
                roi_potential="Médio-Alto",
                confidence_level="Médio",
                actionable_next_steps=[
                    "Auditoria de apps Shopify",
                    "Consolidação de funcionalidades em apps principais",
                    "Implementação de soluções personalizadas para substituir apps redundantes"
                ]
            )

            pain_points.append(pp)

        return pain_points

    def _analyze_conversion_opportunities(self, lead: RealLead, monthly_traffic: int, industry: str) -> List[PainPoint]:
        """Analisa oportunidades de melhoria de conversão

        Args:
            lead: Objeto RealLead
            monthly_traffic: Tráfego mensal estimado
            industry: Indústria identificada

        Returns:
            Lista de pain points de conversão
        """
        pain_points = []

        # Obtém benchmarks de conversão
        benchmarks = self.conversion_benchmarks.get(industry, self.conversion_benchmarks["General Business"])
        baseline_conversion = benchmarks["average"]
        good_conversion = benchmarks["good"]
        revenue_per_conversion = benchmarks["revenue_per_conversion"]

        # Potencial de melhoria: diferença entre médio e bom
        conversion_improvement = good_conversion - baseline_conversion

        # Conversões adicionais potenciais
        additional_conversions = monthly_traffic * conversion_improvement / 100
        monthly_opportunity = additional_conversions * revenue_per_conversion

        # Diferentes tipos de oportunidades de conversão

        # 1. E-commerce: otimização de página de produto
        if lead.ecommerce_platform:
            # Estima sessões em páginas de produto
            product_page_sessions = monthly_traffic * 0.4  # ~40% das sessões chegam a páginas de produto

            # Conversão atual e potencial
            current_conversion = baseline_conversion * 0.8  # Geralmente abaixo da média do site
            potential_conversion = current_conversion * 1.3  # +30% com otimizações

            # Vendas adicionais
            additional_sales = product_page_sessions * (potential_conversion - current_conversion) / 100
            pdp_opportunity = additional_sales * revenue_per_conversion

            pp = PainPoint(
                description="Páginas de produto sub-otimizadas reduzem taxa de conversão",
                severity=PainSeverity.HIGH,
                opportunity_type=OpportunityType.CONVERSION_RATE,
                estimated_monthly_loss=pdp_opportunity,
                estimated_annual_opportunity=pdp_opportunity * 12,
                implementation_effort="Médio",
                roi_potential="Alto",
                confidence_level="Alto",
                supporting_data={
                    "product_page_sessions": product_page_sessions,
                    "current_conversion": current_conversion,
                    "potential_conversion": potential_conversion
                },
                actionable_next_steps=[
                    "Otimização de imagens e galerias de produto",
                    "Melhoria da apresentação de informações críticas",
                    "Implementação de social proof e reviews"
                ]
            )

            pain_points.append(pp)

            # 2. E-commerce: carrinho abandonado
            cart_abandonment_rate = 75  # Taxa média de abandono
            cart_sessions = monthly_traffic * 0.15  # ~15% das sessões chegam ao carrinho
            abandonment_reduction = 15  # Potencial de redução em pontos percentuais

            recovered_carts = cart_sessions * (abandonment_reduction / 100)
            cart_opportunity = recovered_carts * revenue_per_conversion

            pp = PainPoint(
                description="Alta taxa de abandono de carrinho representa vendas perdidas",
                severity=PainSeverity.CRITICAL,
                opportunity_type=OpportunityType.CONVERSION_RATE,
                estimated_monthly_loss=cart_opportunity,
                estimated_annual_opportunity=cart_opportunity * 12,
                implementation_effort="Médio",
                roi_potential="Muito Alto",
                confidence_level="Muito Alto",
                supporting_data={
                    "cart_sessions": cart_sessions,
                    "abandonment_rate": cart_abandonment_rate,
                    "abandonment_reduction": abandonment_reduction
                },
                actionable_next_steps=[
                    "Implementação de fluxo de checkout otimizado",
                    "Estratégia de recuperação de carrinho abandonado",
                    "Remoção de barreiras de conversão no checkout"
                ]
            )

            pain_points.append(pp)

        # 3. Lead generation: formulários ineficientes
        if industry in ["Professional Services", "Healthcare", "Real Estate", "Education"]:
            # Estima sessões em páginas de contato/formulário
            form_page_sessions = monthly_traffic * 0.1  # ~10% das sessões chegam a formulários

            # Conversão atual e potencial
            current_conversion = baseline_conversion * 0.7  # Geralmente abaixo da média do site
            potential_conversion = current_conversion * 1.5  # +50% com otimizações

            # Leads adicionais
            additional_leads = form_page_sessions * (potential_conversion - current_conversion) / 100
            form_opportunity = additional_leads * revenue_per_conversion

            pp = PainPoint(
                description="Formulários de contato com baixa taxa de conversão",
                severity=PainSeverity.HIGH,
                opportunity_type=OpportunityType.CONVERSION_RATE,
                estimated_monthly_loss=form_opportunity,
                estimated_annual_opportunity=form_opportunity * 12,
                implementation_effort="Baixo-Médio",
                roi_potential="Muito Alto",
                confidence_level="Alto",
                supporting_data={
                    "form_page_sessions": form_page_sessions,
                    "current_conversion": current_conversion,
                    "potential_conversion": potential_conversion
                },
                actionable_next_steps=[
                    "Simplificação e otimização de formulários",
                    "Implementação de multi-step forms",
                    "Adição de elementos de confiança e social proof"
                ]
            )

            pain_points.append(pp)

        return pain_points

    def _analyze_seo_opportunities(self, lead: RealLead) -> List[PainPoint]:
        """Analisa oportunidades de SEO

        Args:
            lead: Objeto RealLead

        Returns:
            Lista de pain points de SEO
        """
        pain_points = []

        # Oportunidade de SEO baseada na performance
        if lead.performance_score < 60:
            # Core Web Vitals é um fator de ranking
            # Estima perda de tráfego orgânico
            seo_impact = 2500  # Valor base conservador

            # Ajusta com base na severidade dos problemas
            if lead.lcp_mobile > 4.0 or lead.cls_mobile > 0.25:
                seo_impact *= 1.5

            pp = PainPoint(
                description="Performance ruim prejudica posicionamento orgânico (Core Web Vitals)",
                severity=PainSeverity.HIGH,
                opportunity_type=OpportunityType.SEO_RANKING,
                estimated_monthly_loss=seo_impact,
                estimated_annual_opportunity=seo_impact * 12,
                implementation_effort="Médio-Alto",
                roi_potential="Alto",
                confidence_level="Médio-Alto",
                actionable_next_steps=[
                    "Otimização de Core Web Vitals",
                    "Implementação de estratégia de caching",
                    "Otimização de assets críticos"
                ]
            )

            pain_points.append(pp)

        return pain_points
