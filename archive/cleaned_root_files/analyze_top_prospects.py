#!/usr/bin/env python3
"""
COMPLETE INTEGRATED ANALYSIS OF 175 PROSPECTS
Real data analysis with actionable insights for client partnership.
"""

import asyncio
import sys
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class LeadScore:
    """Score detalhado de um lead."""
    # Scores individuais (0-100)
    segment_score: float = 0.0
    revenue_score: float = 0.0
    technology_score: float = 0.0
    geographic_score: float = 0.0
    competitive_score: float = 0.0
    roi_score: float = 0.0
    
    # Score final ponderado
    final_score: float = 0.0
    confidence_level: float = 0.0
    
    # Justificativas
    strengths: List[str] = None
    opportunities: List[str] = None
    risks: List[str] = None
    
    def __post_init__(self):
        if self.strengths is None:
            self.strengths = []
        if self.opportunities is None:
            self.opportunities = []
        if self.risks is None:
            self.risks = []

@dataclass
class LeadAnalysis:
    """Análise completa de um lead."""
    # Dados básicos
    company: str
    domain: str
    industry: str
    employees: int
    location: str
    
    # Análise detalhada
    segment_analysis: Dict[str, Any]
    revenue_analysis: Dict[str, Any]
    technology_analysis: Dict[str, Any]
    competitive_analysis: Dict[str, Any]
    roi_analysis: Dict[str, Any]
    
    # Score final
    score: LeadScore
    
    # Recomendações estratégicas
    approach_strategy: Dict[str, Any]
    value_proposition: str
    next_steps: List[str]

class AdvancedLeadAnalyzer:
    """Analisador avançado de leads com inteligência de negócio."""
    
    def __init__(self):
        """Inicializa o analisador com configurações otimizadas."""
        self.segment_keywords = self._load_segment_keywords()
        self.technology_categories = self._load_technology_categories()
        self.revenue_multipliers = self._load_revenue_multipliers()
        self.geographic_priorities = self._load_geographic_priorities()
        self.competitive_benchmarks = self._load_competitive_benchmarks()
        
    def _load_segment_keywords(self) -> Dict[str, Dict[str, float]]:
        """Carrega keywords para classificação de segmentos."""
        return {
            'ecommerce': {
                'shopify': 5.0, 'woocommerce': 5.0, 'magento': 4.0, 'vtex': 4.0,
                'loja online': 3.0, 'e-commerce': 3.0, 'vendas online': 2.0,
                'marketplace': 2.0, 'varejo': 2.0
            },
            'fashion': {
                'moda': 5.0, 'roupas': 4.0, 'vestuário': 4.0, 'fashion': 4.0,
                'acessórios': 3.0, 'calçados': 3.0, 'bijuterias': 3.0,
                'beachwear': 3.0, 'bordado': 2.0
            },
            'pet': {
                'pet': 5.0, 'animal': 4.0, 'cachorro': 3.0, 'gato': 3.0,
                'veterinário': 3.0, 'ração': 2.0, 'acessórios pet': 4.0
            },
            'food_health': {
                'natural products': 4.0, 'organic': 4.0, 'suplementos': 4.0,
                'vitaminas': 3.0, 'alimentação': 3.0, 'saúde': 3.0,
                'wellness': 3.0, 'nutrition': 3.0
            },
            'sports': {
                'esporte': 4.0, 'fitness': 4.0, 'tênis': 3.0, 'equipamentos': 3.0,
                'academia': 3.0, 'treinamento': 2.0
            },
            'technology': {
                'software': 5.0, 'tecnologia': 4.0, 'informática': 4.0,
                'computador': 3.0, 'hardware': 3.0, 'eletrônicos': 3.0
            },
            'services': {
                'serviços': 3.0, 'consultoria': 3.0, 'treinamento': 2.0,
                'educação': 2.0, 'desenvolvimento': 3.0
            }
        }
    
    def _load_technology_categories(self) -> Dict[str, List[str]]:
        """Carrega categorias de tecnologias para análise."""
        return {
            'ecommerce_platforms': ['Shopify', 'WooCommerce', 'Magento', 'Vtex', 'PrestaShop'],
            'analytics': ['Google Analytics', 'Hotjar', 'Lucky Orange', 'Mixpanel'],
            'marketing': ['Google AdWords', 'Facebook Custom Audiences', 'DoubleClick', 'Klaviyo'],
            'performance': ['Cloudflare', 'AWS', 'Google Cloud', 'CDN'],
            'email': ['Outlook', 'Gmail', 'SendGrid', 'Mailchimp'],
            'crm': ['HubSpot', 'Salesforce', 'Pipedrive'],
            'payment': ['PayPal', 'Stripe', 'PagSeguro'],
            'infrastructure': ['AWS', 'Google Cloud', 'Azure', 'Digital Ocean']
        }
    
    def _load_revenue_multipliers(self) -> Dict[str, Dict[str, float]]:
        """Carrega multiplicadores de receita por segmento e tamanho."""
        return {
            'ecommerce': {
                '1-10': 400000,    # R$ 400k por funcionário
                '11-50': 250000,   # R$ 250k por funcionário  
                '51-200': 180000   # R$ 180k por funcionário
            },
            'fashion': {
                '1-10': 350000,
                '11-50': 220000,
                '51-200': 160000
            },
            'pet': {
                '1-10': 300000,
                '11-50': 200000,
                '51-200': 140000
            },
            'food_health': {
                '1-10': 320000,
                '11-50': 210000,
                '51-200': 150000
            },
            'technology': {
                '1-10': 500000,
                '11-50': 350000,
                '51-200': 250000
            },
            'default': {
                '1-10': 300000,
                '11-50': 200000,
                '51-200': 150000
            }
        }
    
    def _load_geographic_priorities(self) -> Dict[str, float]:
        """Carrega prioridades geográficas."""
        return {
            'Brazil': {
                'base_multiplier': 2.0,
                'states': {
                    'Sao Paulo': 2.5,
                    'State of Sao Paulo': 2.5,
                    'Rio de Janeiro': 2.2,
                    'State of Rio de Janeiro': 2.2,
                    'Minas Gerais': 2.0,
                    'State of Minas Gerais': 2.0,
                    'Rio Grande do Sul': 1.8,
                    'Santa Catarina': 1.8,
                    'Parana': 1.7
                }
            },
            'international': {
                'United States': 1.2,
                'Canada': 1.1,
                'United Kingdom': 1.0,
                'Germany': 1.0,
                'default': 0.8
            }
        }
    
    def _load_competitive_benchmarks(self) -> Dict[str, Any]:
        """Carrega benchmarks competitivos por segmento."""
        return {
            'ecommerce': {
                'avg_conversion_rate': 0.025,
                'avg_cart_abandonment': 0.70,
                'avg_monthly_ad_spend_per_employee': 500,
                'performance_impact_multiplier': 0.15
            },
            'fashion': {
                'avg_conversion_rate': 0.018,
                'avg_cart_abandonment': 0.75,
                'avg_monthly_ad_spend_per_employee': 400,
                'performance_impact_multiplier': 0.20
            },
            'pet': {
                'avg_conversion_rate': 0.030,
                'avg_cart_abandonment': 0.65,
                'avg_monthly_ad_spend_per_employee': 300,
                'performance_impact_multiplier': 0.12
            },
            'default': {
                'avg_conversion_rate': 0.020,
                'avg_cart_abandonment': 0.70,
                'avg_monthly_ad_spend_per_employee': 400,
                'performance_impact_multiplier': 0.15
            }
        }
    
    def analyze_lead(self, lead_data: Dict[str, Any]) -> LeadAnalysis:
        """Executa análise completa de um lead."""
        logger.info(f"Analisando lead: {lead_data.get('Company', 'Unknown')}")
        
        # Análise de segmento
        segment_analysis = self._analyze_segment(lead_data)
        
        # Análise de receita
        revenue_analysis = self._analyze_revenue_potential(lead_data, segment_analysis)
        
        # Análise tecnológica
        technology_analysis = self._analyze_technology_stack(lead_data, segment_analysis)
        
        # Análise competitiva
        competitive_analysis = self._analyze_competitive_position(lead_data, segment_analysis)
        
        # Análise de ROI
        roi_analysis = self._analyze_roi_potential(lead_data, revenue_analysis, technology_analysis)
        
        # Cálculo do score final
        score = self._calculate_final_score(
            segment_analysis, revenue_analysis, technology_analysis,
            competitive_analysis, roi_analysis, lead_data
        )
        
        # Estratégia de abordagem
        approach_strategy = self._generate_approach_strategy(
            lead_data, segment_analysis, revenue_analysis, roi_analysis
        )
        
        return LeadAnalysis(
            company=lead_data.get('Company', ''),
            domain=self._extract_domain(lead_data.get('Website', '')),
            industry=lead_data.get('Industry', ''),
            employees=self._safe_int(lead_data.get('# Employees', 0)),
            location=f"{lead_data.get('Company City', '')}, {lead_data.get('Company State', '')}, {lead_data.get('Company Country', '')}",
            segment_analysis=segment_analysis,
            revenue_analysis=revenue_analysis,
            technology_analysis=technology_analysis,
            competitive_analysis=competitive_analysis,
            roi_analysis=roi_analysis,
            score=score,
            approach_strategy=approach_strategy,
            value_proposition=self._generate_value_proposition(roi_analysis, segment_analysis),
            next_steps=self._generate_next_steps(score, approach_strategy)
        )    

    def _analyze_segment(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa o segmento específico do lead."""
        description = str(lead_data.get('Short Description', '') + ' ' + 
                         lead_data.get('Keywords', '') + ' ' + 
                         lead_data.get('Industry', '')).lower()
        
        segment_scores = {}
        for segment, keywords in self.segment_keywords.items():
            score = 0.0
            matched_keywords = []
            
            for keyword, weight in keywords.items():
                if keyword in description:
                    score += weight
                    matched_keywords.append(keyword)
            
            if score > 0:
                segment_scores[segment] = {
                    'score': score,
                    'matched_keywords': matched_keywords
                }
        
        # Determina segmento primário
        primary_segment = max(segment_scores.keys(), key=lambda x: segment_scores[x]['score']) if segment_scores else 'general'
        
        return {
            'primary_segment': primary_segment,
            'segment_scores': segment_scores,
            'segment_confidence': min(segment_scores.get(primary_segment, {}).get('score', 0) / 10, 1.0),
            'market_characteristics': self._get_market_characteristics(primary_segment)
        }
    
    def _analyze_revenue_potential(self, lead_data: Dict[str, Any], segment_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa o potencial de receita do lead."""
        employees = self._safe_int(lead_data.get('# Employees', 0))
        declared_revenue = self._safe_float(lead_data.get('Annual Revenue', 0))
        
        # Estimativa por funcionários
        segment = segment_analysis['primary_segment']
        employee_range = self._get_employee_range(employees)
        
        multipliers = self.revenue_multipliers.get(segment, self.revenue_multipliers['default'])
        estimated_revenue = multipliers.get(employee_range, multipliers['1-10']) * employees if employees > 0 else 0
        
        # Usa receita declarada se disponível e confiável
        final_revenue = declared_revenue if declared_revenue > 0 else estimated_revenue
        
        # Ajuste geográfico
        country = lead_data.get('Company Country', '')
        state = lead_data.get('Company State', '')
        geographic_multiplier = self._get_geographic_multiplier(country, state)
        
        adjusted_revenue = final_revenue * geographic_multiplier
        
        # Cálculo do valor do contrato (% da receita anual)
        contract_percentage = self._get_contract_percentage(segment, adjusted_revenue)
        contract_value = adjusted_revenue * contract_percentage
        
        return {
            'estimated_annual_revenue': adjusted_revenue,
            'contract_value_estimate': contract_value,
            'revenue_confidence': 0.9 if declared_revenue > 0 else 0.6,
            'payment_capacity': self._assess_payment_capacity(adjusted_revenue),
            'geographic_multiplier': geographic_multiplier,
            'revenue_source': 'declared' if declared_revenue > 0 else 'estimated'
        }
    
    def _analyze_technology_stack(self, lead_data: Dict[str, Any], segment_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa o stack tecnológico e fit com nossa solução."""
        technologies_str = str(lead_data.get('Technologies', '')).lower()
        
        # Categoriza tecnologias
        categorized_tech = {}
        optimization_opportunities = []
        
        for category, tech_list in self.technology_categories.items():
            found_techs = []
            for tech in tech_list:
                if tech.lower() in technologies_str:
                    found_techs.append(tech)
            
            if found_techs:
                categorized_tech[category] = found_techs
        
        # Identifica oportunidades de otimização
        segment = segment_analysis['primary_segment']
        
        # E-commerce específico
        if segment == 'ecommerce':
            if 'ecommerce_platforms' in categorized_tech:
                optimization_opportunities.append({
                    'type': 'ecommerce_optimization',
                    'description': f"Otimização de conversão para {', '.join(categorized_tech['ecommerce_platforms'])}",
                    'impact': 'high',
                    'monthly_value': 2000
                })
            
            if 'analytics' not in categorized_tech:
                optimization_opportunities.append({
                    'type': 'analytics_gap',
                    'description': 'Falta de ferramentas de analytics avançadas',
                    'impact': 'high',
                    'monthly_value': 1500
                })
        
        # Performance geral
        if 'performance' not in categorized_tech:
            optimization_opportunities.append({
                'type': 'performance_optimization',
                'description': 'Oportunidade de otimização de performance',
                'impact': 'medium',
                'monthly_value': 1000
            })
        
        # Score de maturidade tecnológica
        maturity_score = len(categorized_tech) * 10  # 0-100
        
        return {
            'categorized_technologies': categorized_tech,
            'technology_maturity_score': min(maturity_score, 100),
            'optimization_opportunities': optimization_opportunities,
            'solution_fit_score': self._calculate_solution_fit(categorized_tech, segment),
            'implementation_complexity': self._assess_implementation_complexity(categorized_tech)
        }
    
    def _analyze_competitive_position(self, lead_data: Dict[str, Any], segment_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa posicionamento competitivo."""
        segment = segment_analysis['primary_segment']
        benchmarks = self.competitive_benchmarks.get(segment, self.competitive_benchmarks['default'])
        
        employees = self._safe_int(lead_data.get('# Employees', 0))
        founded_year = self._safe_int(lead_data.get('Founded Year', 0))
        
        # Análise de maturidade da empresa
        current_year = datetime.now().year
        company_age = current_year - founded_year if founded_year > 0 else 0
        
        competitive_advantages = []
        vulnerabilities = []
        
        # Vantagens baseadas em tamanho
        if 5 <= employees <= 50:
            competitive_advantages.append("Tamanho ideal para implementação ágil")
        elif employees > 50:
            competitive_advantages.append("Recursos para investimento em otimização")
        
        # Vulnerabilidades baseadas em idade
        if company_age > 10:
            vulnerabilities.append("Possível resistência a mudanças tecnológicas")
        elif company_age < 2:
            vulnerabilities.append("Foco pode estar em crescimento vs otimização")
        
        # Urgência competitiva
        urgency_score = 50  # Base
        if segment in ['ecommerce', 'fashion']:
            urgency_score += 20  # Mercados mais competitivos
        if employees > 20:
            urgency_score += 15  # Maior pressão por eficiência
        
        return {
            'competitive_advantages': competitive_advantages,
            'vulnerabilities': vulnerabilities,
            'urgency_score': min(urgency_score, 100),
            'market_position': self._assess_market_position(employees, company_age, segment),
            'competitive_pressure': self._assess_competitive_pressure(segment)
        }
    
    def _analyze_roi_potential(self, lead_data: Dict[str, Any], revenue_analysis: Dict[str, Any], 
                              technology_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa potencial de ROI real."""
        annual_revenue = revenue_analysis['estimated_annual_revenue']
        employees = self._safe_int(lead_data.get('# Employees', 0))
        
        # Estimativa de gastos atuais com marketing/tecnologia
        monthly_marketing_spend = employees * 400 if employees > 0 else 2000  # R$ 400 por funcionário
        monthly_tech_waste = 0
        
        # Calcula desperdício baseado em oportunidades
        for opportunity in technology_analysis['optimization_opportunities']:
            monthly_tech_waste += opportunity.get('monthly_value', 0)
        
        # Savings potenciais
        monthly_savings = monthly_tech_waste * 0.7  # 70% do desperdício pode ser recuperado
        annual_savings = monthly_savings * 12
        
        # Custo de implementação (% da receita anual)
        implementation_cost = annual_revenue * 0.02  # 2% da receita anual
        
        # ROI calculation
        if implementation_cost > 0:
            annual_roi = (annual_savings - implementation_cost) / implementation_cost * 100
            payback_months = implementation_cost / monthly_savings if monthly_savings > 0 else 999
        else:
            annual_roi = 0
            payback_months = 999
        
        return {
            'monthly_current_waste': monthly_tech_waste,
            'monthly_savings_potential': monthly_savings,
            'annual_savings_potential': annual_savings,
            'implementation_cost': implementation_cost,
            'annual_roi_percentage': annual_roi,
            'payback_period_months': min(payback_months, 36),
            'three_year_value': annual_savings * 3 - implementation_cost,
            'roi_confidence': 0.7 if monthly_tech_waste > 1000 else 0.4
        }
    
    def _calculate_final_score(self, segment_analysis: Dict[str, Any], revenue_analysis: Dict[str, Any],
                              technology_analysis: Dict[str, Any], competitive_analysis: Dict[str, Any],
                              roi_analysis: Dict[str, Any], lead_data: Dict[str, Any]) -> LeadScore:
        """Calcula score final ponderado."""
        
        # Scores individuais (0-100)
        segment_score = segment_analysis['segment_confidence'] * 100
        
        revenue_score = min((revenue_analysis['estimated_annual_revenue'] / 1000000) * 20, 100)  # Max em R$ 5M
        
        technology_score = technology_analysis['solution_fit_score']
        
        # Score geográfico
        country = lead_data.get('Company Country', '')
        geographic_score = 100 if country == 'Brazil' else 50
        
        competitive_score = competitive_analysis['urgency_score']
        
        roi_score = min(roi_analysis['annual_roi_percentage'] / 2, 100) if roi_analysis['annual_roi_percentage'] > 0 else 0
        
        # Pesos para score final
        weights = {
            'segment': 0.15,
            'revenue': 0.25,
            'technology': 0.20,
            'geographic': 0.15,
            'competitive': 0.10,
            'roi': 0.15
        }
        
        final_score = (
            segment_score * weights['segment'] +
            revenue_score * weights['revenue'] +
            technology_score * weights['technology'] +
            geographic_score * weights['geographic'] +
            competitive_score * weights['competitive'] +
            roi_score * weights['roi']
        )
        
        # Confidence level baseado na qualidade dos dados
        confidence_factors = [
            segment_analysis['segment_confidence'],
            revenue_analysis['revenue_confidence'],
            roi_analysis['roi_confidence'],
            0.8 if lead_data.get('Technologies') else 0.3,
            0.9 if lead_data.get('Company Country') == 'Brazil' else 0.6
        ]
        confidence_level = sum(confidence_factors) / len(confidence_factors)
        
        # Strengths, opportunities, risks
        strengths = []
        opportunities = []
        risks = []
        
        if revenue_score > 70:
            strengths.append(f"Alto potencial de receita (R$ {revenue_analysis['estimated_annual_revenue']:,.0f})")
        
        if geographic_score == 100:
            strengths.append("Localização prioritária (Brasil)")
        
        if roi_analysis['annual_roi_percentage'] > 100:
            opportunities.append(f"ROI excelente ({roi_analysis['annual_roi_percentage']:.0f}%)")
        
        if technology_analysis['solution_fit_score'] < 50:
            risks.append("Baixo fit tecnológico com nossa solução")
        
        if revenue_analysis['payment_capacity'] == 'low':
            risks.append("Capacidade de pagamento limitada")
        
        return LeadScore(
            segment_score=segment_score,
            revenue_score=revenue_score,
            technology_score=technology_score,
            geographic_score=geographic_score,
            competitive_score=competitive_score,
            roi_score=roi_score,
            final_score=final_score,
            confidence_level=confidence_level,
            strengths=strengths,
            opportunities=opportunities,
            risks=risks
        )  
  
    def _generate_approach_strategy(self, lead_data: Dict[str, Any], segment_analysis: Dict[str, Any],
                                  revenue_analysis: Dict[str, Any], roi_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Gera estratégia de abordagem personalizada."""
        segment = segment_analysis['primary_segment']
        
        # Decision maker baseado no tamanho da empresa
        employees = self._safe_int(lead_data.get('# Employees', 0))
        if employees <= 10:
            decision_maker = "CEO/Founder"
            approach_style = "direct_founder"
        elif employees <= 50:
            decision_maker = "CEO/CMO"
            approach_style = "executive_focused"
        else:
            decision_maker = "CMO/CTO"
            approach_style = "technical_business"
        
        # Messaging baseado no segmento
        segment_messaging = {
            'ecommerce': "Otimização de conversão e redução de cart abandonment",
            'fashion': "Melhoria da experiência de compra online",
            'pet': "Aumento da fidelização de clientes pet",
            'food_health': "Otimização para mercado de wellness",
            'technology': "Eficiência operacional e redução de custos",
            'default': "Otimização de performance digital"
        }
        
        primary_message = segment_messaging.get(segment, segment_messaging['default'])
        
        # Timing baseado na urgência
        urgency = roi_analysis.get('payback_period_months', 12)
        if urgency <= 6:
            timing = "immediate"
            urgency_message = "ROI rápido em menos de 6 meses"
        elif urgency <= 12:
            timing = "short_term"
            urgency_message = "Retorno garantido em até 1 ano"
        else:
            timing = "long_term"
            urgency_message = "Investimento estratégico de longo prazo"
        
        return {
            'decision_maker': decision_maker,
            'approach_style': approach_style,
            'primary_message': primary_message,
            'timing': timing,
            'urgency_message': urgency_message,
            'preferred_channel': 'linkedin' if employees > 20 else 'email',
            'meeting_type': 'video_call' if lead_data.get('Company Country') == 'Brazil' else 'phone_call'
        }
    
    def _generate_value_proposition(self, roi_analysis: Dict[str, Any], segment_analysis: Dict[str, Any]) -> str:
        """Gera value proposition específica."""
        monthly_savings = roi_analysis.get('monthly_savings_potential', 0)
        annual_roi = roi_analysis.get('annual_roi_percentage', 0)
        segment = segment_analysis['primary_segment']
        
        if monthly_savings > 5000:
            savings_message = f"economizar R$ {monthly_savings:,.0f} por mês"
        elif monthly_savings > 1000:
            savings_message = f"reduzir custos em R$ {monthly_savings:,.0f} mensais"
        else:
            savings_message = "otimizar seus investimentos digitais"
        
        segment_benefits = {
            'ecommerce': "aumentar conversões e reduzir cart abandonment",
            'fashion': "melhorar a experiência de compra online",
            'pet': "fidelizar clientes e aumentar ticket médio",
            'food_health': "otimizar para o mercado wellness",
            'technology': "aumentar eficiência operacional",
            'default': "otimizar performance digital"
        }
        
        segment_benefit = segment_benefits.get(segment, segment_benefits['default'])
        
        return f"Podemos ajudar sua empresa a {segment_benefit} e {savings_message}, com ROI de {annual_roi:.0f}% ao ano."
    
    def _generate_next_steps(self, score: LeadScore, approach_strategy: Dict[str, Any]) -> List[str]:
        """Gera próximos passos recomendados."""
        steps = []
        
        if score.final_score > 80:
            steps.append("🔥 PRIORIDADE MÁXIMA - Contato imediato")
            steps.append(f"Agendar reunião com {approach_strategy['decision_maker']}")
            steps.append("Preparar proposta personalizada")
        elif score.final_score > 60:
            steps.append("⭐ ALTA PRIORIDADE - Contato em 48h")
            steps.append("Pesquisa adicional sobre necessidades específicas")
            steps.append("Abordagem via LinkedIn + email")
        else:
            steps.append("📋 MÉDIO PRAZO - Nurturing campaign")
            steps.append("Adicionar à sequência de email marketing")
            steps.append("Monitorar crescimento da empresa")
        
        # Steps específicos baseados em riscos
        if "Baixo fit tecnológico" in score.risks:
            steps.append("Investigar stack tecnológico atual")
        
        if "Capacidade de pagamento limitada" in score.risks:
            steps.append("Considerar modelo de pagamento flexível")
        
        return steps
    
    # Métodos auxiliares
    def _extract_domain(self, website: str) -> str:
        """Extrai domínio limpo do website."""
        if not website:
            return ""
        domain = website.replace('http://', '').replace('https://', '').replace('www.', '')
        return domain.split('/')[0]
    
    def _safe_int(self, value: Any) -> int:
        """Conversão segura para int."""
        try:
            return int(float(str(value))) if value and str(value).strip() else 0
        except (ValueError, TypeError):
            return 0
    
    def _safe_float(self, value: Any) -> float:
        """Conversão segura para float."""
        try:
            return float(str(value)) if value and str(value).strip() else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def _get_employee_range(self, employees: int) -> str:
        """Retorna faixa de funcionários."""
        if employees <= 10:
            return '1-10'
        elif employees <= 50:
            return '11-50'
        else:
            return '51-200'
    
    def _get_geographic_multiplier(self, country: str, state: str) -> float:
        """Retorna multiplicador geográfico."""
        if country == 'Brazil':
            base = self.geographic_priorities['Brazil']['base_multiplier']
            state_bonus = self.geographic_priorities['Brazil']['states'].get(state, 1.0)
            return base * state_bonus
        else:
            return self.geographic_priorities['international'].get(country, 
                   self.geographic_priorities['international']['default'])
    
    def _get_contract_percentage(self, segment: str, revenue: float) -> float:
        """Retorna percentual do contrato baseado no segmento e receita."""
        base_percentage = 0.03  # 3% da receita anual
        
        # Ajuste por segmento
        segment_multipliers = {
            'ecommerce': 1.2,
            'technology': 1.5,
            'fashion': 1.0,
            'pet': 0.8,
            'default': 1.0
        }
        
        multiplier = segment_multipliers.get(segment, segment_multipliers['default'])
        
        # Ajuste por receita (empresas maiores pagam percentual menor)
        if revenue > 5000000:  # > R$ 5M
            revenue_adjustment = 0.8
        elif revenue > 1000000:  # > R$ 1M
            revenue_adjustment = 0.9
        else:
            revenue_adjustment = 1.0
        
        return base_percentage * multiplier * revenue_adjustment
    
    def _assess_payment_capacity(self, revenue: float) -> str:
        """Avalia capacidade de pagamento."""
        if revenue > 2000000:
            return 'high'
        elif revenue > 500000:
            return 'medium'
        else:
            return 'low'
    
    def _get_market_characteristics(self, segment: str) -> Dict[str, Any]:
        """Retorna características do mercado por segmento."""
        characteristics = {
            'ecommerce': {
                'market_size_brazil': 161000000000,  # R$ 161 bilhões
                'growth_rate': 0.12,
                'competition_level': 'high',
                'avg_margins': 0.15
            },
            'fashion': {
                'market_size_brazil': 85000000000,
                'growth_rate': 0.08,
                'competition_level': 'very_high',
                'avg_margins': 0.25
            },
            'pet': {
                'market_size_brazil': 54000000000,
                'growth_rate': 0.15,
                'competition_level': 'medium',
                'avg_margins': 0.30
            },
            'default': {
                'market_size_brazil': 50000000000,
                'growth_rate': 0.10,
                'competition_level': 'medium',
                'avg_margins': 0.20
            }
        }
        return characteristics.get(segment, characteristics['default'])
    
    def _calculate_solution_fit(self, categorized_tech: Dict[str, List[str]], segment: str) -> float:
        """Calcula fit da solução (0-100)."""
        base_score = 50
        
        # Bonus por tecnologias relevantes
        if segment == 'ecommerce' and 'ecommerce_platforms' in categorized_tech:
            base_score += 30
        
        if 'analytics' in categorized_tech:
            base_score += 20
        
        if 'marketing' in categorized_tech:
            base_score += 15
        
        # Penalty por falta de tecnologias básicas
        if 'analytics' not in categorized_tech:
            base_score -= 10
        
        return min(base_score, 100)
    
    def _assess_implementation_complexity(self, categorized_tech: Dict[str, List[str]]) -> str:
        """Avalia complexidade de implementação."""
        tech_count = sum(len(techs) for techs in categorized_tech.values())
        
        if tech_count > 15:
            return 'high'
        elif tech_count > 8:
            return 'medium'
        else:
            return 'low'
    
    def _assess_market_position(self, employees: int, company_age: int, segment: str) -> str:
        """Avalia posição no mercado."""
        if employees > 50 and company_age > 5:
            return 'established'
        elif employees > 20 or company_age > 3:
            return 'growing'
        else:
            return 'startup'
    
    def _assess_competitive_pressure(self, segment: str) -> str:
        """Avalia pressão competitiva do segmento."""
        pressure_levels = {
            'ecommerce': 'very_high',
            'fashion': 'very_high',
            'technology': 'high',
            'pet': 'medium',
            'food_health': 'medium',
            'default': 'medium'
        }
        return pressure_levels.get(segment, pressure_levels['default'])

def main():
    """Função principal de execução."""
    logger.info("Iniciando análise profunda dos leads mais promissores...")
    
    # Carrega dados
    prospects_file = "arco/consolidated_prospects.csv"
    if not Path(prospects_file).exists():
        logger.error(f"Arquivo não encontrado: {prospects_file}")
        return
    
    df = pd.read_csv(prospects_file)
    logger.info(f"Carregados {len(df)} leads para análise")
    
    # Inicializa analisador
    analyzer = AdvancedLeadAnalyzer()
    
    # Analisa todos os leads
    analyses = []
    for idx, row in df.iterrows():
        try:
            analysis = analyzer.analyze_lead(row.to_dict())
            analyses.append(analysis)
        except Exception as e:
            logger.error(f"Erro analisando lead {idx}: {e}")
            continue
    
    # Ordena por score final
    analyses.sort(key=lambda x: x.score.final_score, reverse=True)
    
    # Seleciona top 10
    top_10 = analyses[:10]
    
    # Gera relatório
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Salva análise completa
    detailed_results = []
    for analysis in top_10:
        detailed_results.append({
            'company': analysis.company,
            'domain': analysis.domain,
            'industry': analysis.industry,
            'employees': analysis.employees,
            'location': analysis.location,
            'score': asdict(analysis.score),
            'segment_analysis': analysis.segment_analysis,
            'revenue_analysis': analysis.revenue_analysis,
            'technology_analysis': analysis.technology_analysis,
            'competitive_analysis': analysis.competitive_analysis,
            'roi_analysis': analysis.roi_analysis,
            'approach_strategy': analysis.approach_strategy,
            'value_proposition': analysis.value_proposition,
            'next_steps': analysis.next_steps
        })
    
    # Salva JSON detalhado
    json_file = f"top_10_leads_analysis_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(detailed_results, f, indent=2, ensure_ascii=False)
    
    # Gera relatório executivo
    executive_summary = generate_executive_report(top_10)
    
    # Salva relatório executivo
    report_file = f"top_10_leads_executive_report_{timestamp}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(executive_summary)
    
    # Salva CSV resumido
    csv_data = []
    for analysis in top_10:
        csv_data.append({
            'Rank': len(csv_data) + 1,
            'Company': analysis.company,
            'Domain': analysis.domain,
            'Industry': analysis.industry,
            'Employees': analysis.employees,
            'Location': analysis.location,
            'Final_Score': round(analysis.score.final_score, 1),
            'Confidence': round(analysis.score.confidence_level, 2),
            'Estimated_Revenue': analysis.revenue_analysis['estimated_annual_revenue'],
            'Contract_Value': analysis.revenue_analysis['contract_value_estimate'],
            'Monthly_Savings': analysis.roi_analysis['monthly_savings_potential'],
            'Annual_ROI': analysis.roi_analysis['annual_roi_percentage'],
            'Primary_Segment': analysis.segment_analysis['primary_segment'],
            'Decision_Maker': analysis.approach_strategy['decision_maker'],
            'Value_Proposition': analysis.value_proposition
        })
    
    csv_file = f"top_10_leads_summary_{timestamp}.csv"
    pd.DataFrame(csv_data).to_csv(csv_file, index=False)
    
    # Print summary
    print(f"\n{'='*80}")
    print("🎯 TOP 10 LEADS MAIS PROMISSORES - ANÁLISE PROFUNDA")
    print(f"{'='*80}")
    
    for i, analysis in enumerate(top_10, 1):
        print(f"\n{i}. {analysis.company}")
        print(f"   Score: {analysis.score.final_score:.1f}/100 (Confiança: {analysis.score.confidence_level:.0%})")
        print(f"   Segmento: {analysis.segment_analysis['primary_segment'].title()}")
        print(f"   Receita Estimada: R$ {analysis.revenue_analysis['estimated_annual_revenue']:,.0f}")
        print(f"   Valor do Contrato: R$ {analysis.revenue_analysis['contract_value_estimate']:,.0f}")
        print(f"   ROI Anual: {analysis.roi_analysis['annual_roi_percentage']:.0f}%")
        print(f"   Localização: {analysis.location}")
        print(f"   Próximo Passo: {analysis.next_steps[0] if analysis.next_steps else 'N/A'}")
    
    total_contract_value = sum(a.revenue_analysis['contract_value_estimate'] for a in top_10)
    total_monthly_savings = sum(a.roi_analysis['monthly_savings_potential'] for a in top_10)
    
    print(f"\n{'='*80}")
    print("📊 RESUMO EXECUTIVO")
    print(f"{'='*80}")
    print(f"Total de Leads Analisados: {len(analyses)}")
    print(f"Valor Total dos Contratos (Top 10): R$ {total_contract_value:,.0f}")
    print(f"Savings Mensais Potenciais: R$ {total_monthly_savings:,.0f}")
    print(f"Savings Anuais Potenciais: R$ {total_monthly_savings * 12:,.0f}")
    print(f"\nArquivos gerados:")
    print(f"- Análise detalhada: {json_file}")
    print(f"- Relatório executivo: {report_file}")
    print(f"- Resumo CSV: {csv_file}")

def generate_executive_report(top_10: List[LeadAnalysis]) -> str:
    """Gera relatório executivo em markdown."""
    
    report = f"""# 🎯 TOP 10 LEADS MAIS PROMISSORES
## Análise Profunda e Estratégica

**Data da Análise:** {datetime.now().strftime("%d/%m/%Y %H:%M")}

---

## 📋 RESUMO EXECUTIVO

Esta análise identificou os 10 leads mais promissores do pipeline atual, baseada em 6 critérios fundamentais:

1. **Segmentação Específica** - Classificação por nicho de mercado
2. **Potencial de Receita** - Análise financeira detalhada  
3. **Fit Tecnológico** - Compatibilidade com nossa solução
4. **Priorização Geográfica** - Foco no mercado brasileiro
5. **Posicionamento Competitivo** - Análise de urgência e oportunidade
6. **ROI Real** - Cálculos específicos de retorno

### 💰 Números Consolidados

"""
    
    total_contract_value = sum(a.revenue_analysis['contract_value_estimate'] for a in top_10)
    total_monthly_savings = sum(a.roi_analysis['monthly_savings_potential'] for a in top_10)
    avg_roi = sum(a.roi_analysis['annual_roi_percentage'] for a in top_10) / len(top_10)
    
    report += f"""
- **Valor Total dos Contratos:** R$ {total_contract_value:,.0f}
- **Savings Mensais Potenciais:** R$ {total_monthly_savings:,.0f}
- **Savings Anuais Potenciais:** R$ {total_monthly_savings * 12:,.0f}
- **ROI Médio:** {avg_roi:.0f}% ao ano
- **Leads Brasileiros:** {sum(1 for a in top_10 if 'Brazil' in a.location)}/10

---

## 🏆 TOP 10 LEADS DETALHADOS

"""
    
    for i, analysis in enumerate(top_10, 1):
        priority_emoji = "🔥" if analysis.score.final_score > 80 else "⭐" if analysis.score.final_score > 60 else "📋"
        
        report += f"""
### {i}. {priority_emoji} {analysis.company}

**Score Final:** {analysis.score.final_score:.1f}/100 | **Confiança:** {analysis.score.confidence_level:.0%}

#### 📊 Análise Financeira
- **Receita Estimada:** R$ {analysis.revenue_analysis['estimated_annual_revenue']:,.0f}/ano
- **Valor do Contrato:** R$ {analysis.revenue_analysis['contract_value_estimate']:,.0f}
- **Savings Mensais:** R$ {analysis.roi_analysis['monthly_savings_potential']:,.0f}
- **ROI Anual:** {analysis.roi_analysis['annual_roi_percentage']:.0f}%
- **Payback:** {analysis.roi_analysis['payback_period_months']:.0f} meses

#### 🎯 Perfil do Lead
- **Segmento:** {analysis.segment_analysis['primary_segment'].title()}
- **Funcionários:** {analysis.employees}
- **Localização:** {analysis.location}
- **Domínio:** {analysis.domain}

#### 💪 Pontos Fortes
"""
        for strength in analysis.score.strengths:
            report += f"- {strength}\n"
        
        report += f"""
#### 🚀 Oportunidades
"""
        for opportunity in analysis.score.opportunities:
            report += f"- {opportunity}\n"
        
        if analysis.score.risks:
            report += f"""
#### ⚠️ Riscos
"""
            for risk in analysis.score.risks:
                report += f"- {risk}\n"
        
        report += f"""
#### 📞 Estratégia de Abordagem
- **Tomador de Decisão:** {analysis.approach_strategy['decision_maker']}
- **Canal Preferido:** {analysis.approach_strategy['preferred_channel'].title()}
- **Timing:** {analysis.approach_strategy['timing'].replace('_', ' ').title()}
- **Mensagem Principal:** {analysis.approach_strategy['primary_message']}

#### 💬 Value Proposition
> {analysis.value_proposition}

#### ✅ Próximos Passos
"""
        for step in analysis.next_steps:
            report += f"- {step}\n"
        
        report += "\n---\n"
    
    # Análise por segmento
    segments = {}
    for analysis in top_10:
        segment = analysis.segment_analysis['primary_segment']
        if segment not in segments:
            segments[segment] = []
        segments[segment].append(analysis)
    
    report += f"""
## 📈 ANÁLISE POR SEGMENTO

"""
    
    for segment, leads in segments.items():
        count = len(leads)
        avg_score = sum(l.score.final_score for l in leads) / count
        total_value = sum(l.revenue_analysis['contract_value_estimate'] for l in leads)
        
        report += f"""
### {segment.title()} ({count} leads)
- **Score Médio:** {avg_score:.1f}/100
- **Valor Total:** R$ {total_value:,.0f}
- **Leads:** {', '.join(l.company for l in leads)}

"""
    
    report += f"""
---

## 🎯 RECOMENDAÇÕES ESTRATÉGICAS

### Priorização Imediata (Score > 80)
"""
    high_priority = [a for a in top_10 if a.score.final_score > 80]
    if high_priority:
        for analysis in high_priority:
            report += f"- **{analysis.company}** - Contato imediato com {analysis.approach_strategy['decision_maker']}\n"
    else:
        report += "- Nenhum lead com prioridade máxima identificado\n"
    
    report += f"""
### Abordagem em 48h (Score 60-80)
"""
    medium_priority = [a for a in top_10 if 60 <= a.score.final_score <= 80]
    if medium_priority:
        for analysis in medium_priority:
            report += f"- **{analysis.company}** - Pesquisa adicional + abordagem via LinkedIn\n"
    else:
        report += "- Nenhum lead com alta prioridade identificado\n"
    
    report += f"""
### Nurturing de Médio Prazo (Score < 60)
"""
    low_priority = [a for a in top_10 if a.score.final_score < 60]
    if low_priority:
        for analysis in low_priority:
            report += f"- **{analysis.company}** - Campanha de nurturing + monitoramento\n"
    else:
        report += "- Nenhum lead com prioridade baixa identificado\n"
    
    report += f"""
---

## 📊 INSIGHTS ESTRATÉGICOS

### Padrões Identificados
- **Segmento Dominante:** {max(segments.keys(), key=lambda x: len(segments[x]))} ({len(segments[max(segments.keys(), key=lambda x: len(segments[x]))])} leads)
- **Concentração Geográfica:** {sum(1 for a in top_10 if 'Brazil' in a.location)} leads brasileiros
- **Faixa de Funcionários:** {min(a.employees for a in top_10 if a.employees > 0)}-{max(a.employees for a in top_10)} funcionários
- **ROI Médio:** {avg_roi:.0f}% (variação: {min(a.roi_analysis['annual_roi_percentage'] for a in top_10):.0f}%-{max(a.roi_analysis['annual_roi_percentage'] for a in top_10):.0f}%)

### Oportunidades de Mercado
- **E-commerce:** Alta demanda por otimização de conversão
- **Fashion:** Necessidade de melhoria na experiência mobile
- **Pet:** Mercado em crescimento com margens atrativas
- **Food/Health:** Oportunidades em wellness e produtos naturais

### Riscos e Mitigações
- **Capacidade de Pagamento:** {sum(1 for a in top_10 if a.revenue_analysis.get('payment_capacity') == 'low')} leads com capacidade limitada
- **Fit Tecnológico:** {sum(1 for a in top_10 if a.technology_analysis['solution_fit_score'] < 50)} leads com baixo fit
- **Competição:** Segmentos de alta competição requerem abordagem diferenciada

---

*Relatório gerado automaticamente pelo Sistema de Análise Avançada de Leads*
"""
    
    return report

if __name__ == "__main__":
    main()