#!/usr/bin/env python3
"""
🎯 ARCO CLIENT-FOCUSED OPPORTUNITIES DETECTOR
Detectar oportunidades com linguagem focada em RESULTADOS DE NEGÓCIO
Foco: O que o CLIENTE vai sentir/ver, não a tecnologia
"""

import re
import requests
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BusinessOpportunity:
    """Oportunidade focada em resultado de negócio"""
    business_problem: str  # O que o cliente SENTE
    current_impact: str    # Como isso PREJUDICA o negócio
    our_solution: str      # O que fazemos (SEM jargão técnico)
    client_outcome: str    # O que o cliente VAI VER
    estimated_value: float # Valor ajustado por tamanho de negócio
    implementation_effort: str  # Tempo realista
    roi_timeline: str      # Quando vê resultados
    proof_metrics: str     # Como comprovamos sucesso
    urgency_level: str     # Por que fazer agora

@dataclass 
class ClientAnalysis:
    """Análise focada em perspectiva do cliente"""
    domain: str
    business_size: str  # Small, Medium (estimado por tech stack)
    immediate_issues: List[BusinessOpportunity]  # Problemas que cliente JÁ sente
    hidden_opportunities: List[BusinessOpportunity]  # Problemas que cliente NÃO sabe
    competitive_gaps: List[BusinessOpportunity]  # Como concorrentes estão na frente
    total_monthly_loss: float  # $ perdido por mês com problemas atuais
    quick_wins_value: float    # Valor que entregamos em 30 dias
    strategic_value: float     # Valor a longo prazo

class ClientFocusedDetector:
    """Detector focado em problemas de NEGÓCIO, não tecnologia"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Oportunidades em linguagem de NEGÓCIO
        self.business_opportunities = {
            # PROBLEMAS QUE CLIENTE JÁ SENTE
            'slow_website': {
                'business_problem': 'Site demora para carregar',
                'current_impact': 'Visitors saem antes de ver seus serviços',
                'our_solution': 'Otimização de velocidade profissional',
                'client_outcome': 'Site 3x mais rápido, visitors ficam mais tempo',
                'base_value': 2500,  # Valor base para small business
                'effort': '2-3 semanas',
                'roi_timeline': '30 dias',
                'proof_metrics': 'Google PageSpeed score + analytics de bounce rate',
                'urgency': 'Alta - perdendo clientes agora',
                'detection': {
                    'performance_score': 60,  # < 60 = slow
                    'lcp_threshold': 3.0      # > 3s = slow
                }
            },
            
            'not_found_google': {
                'business_problem': 'Difícil de encontrar no Google',
                'current_impact': 'Concorrentes aparecem primeiro nas buscas',
                'our_solution': 'Otimização para motores de busca (SEO)',
                'client_outcome': 'Mais visibilidade no Google, mais clientes encontram vocês',
                'base_value': 1800,
                'effort': '1-2 semanas',
                'roi_timeline': '60-90 dias',
                'proof_metrics': 'Ranking de palavras-chave + tráfego orgânico',
                'urgency': 'Média - mercado está competitivo',
                'detection': {
                    'missing_analytics': True,
                    'poor_seo_score': 80,  # < 80 = poor SEO
                    'missing_meta': True
                }
            },
            
            'looks_outdated': {
                'business_problem': 'Site parece desatualizado',
                'current_impact': 'Clientes questionam se empresa ainda funciona',
                'our_solution': 'Design moderno e responsivo',
                'client_outcome': 'Visual profissional que transmite confiança',
                'base_value': 4000,
                'effort': '3-4 semanas',
                'roi_timeline': '45 dias',
                'proof_metrics': 'Before/after + engagement metrics',
                'urgency': 'Alta - primeira impressão importa',
                'detection': {
                    'old_tech': ['wordpress', 'jquery'],
                    'no_mobile_optimization': True
                }
            },
            
            # PROBLEMAS QUE CLIENTE NÃO SABE
            'invisible_problems': {
                'business_problem': 'Perdendo clientes sem saber por quê',
                'current_impact': 'Sem dados para entender comportamento dos visitors',
                'our_solution': 'Sistema de analytics e tracking profissional',
                'client_outcome': 'Relatórios mensais mostrando de onde vêm os clientes',
                'base_value': 1200,
                'effort': '1 semana',
                'roi_timeline': '30 dias',
                'proof_metrics': 'Dashboard com métricas de conversão',
                'urgency': 'Média - tomada de decisão baseada em dados',
                'detection': {
                    'no_analytics': True,
                    'no_conversion_tracking': True
                }
            },
            
            'security_risk': {
                'business_problem': 'Site vulnerável a ataques',
                'current_impact': 'Risco de dados vazarem ou site sair do ar',
                'our_solution': 'Implementação de segurança SSL e proteção',
                'client_outcome': 'Tranquilidade e proteção total dos dados',
                'base_value': 800,
                'effort': '3-5 dias',
                'roi_timeline': '7 dias',
                'proof_metrics': 'Certificados de segurança + relatório de vulnerabilidades',
                'urgency': 'Crítica - risco de ser hackeado',
                'detection': {
                    'no_ssl': True,
                    'http_only': True
                }
            },
            
            # GAPS COMPETITIVOS
            'competitor_advantage': {
                'business_problem': 'Concorrentes têm sites mais modernos',
                'current_impact': 'Clientes preferem a concorrência',
                'our_solution': 'Modernização completa da presença digital',
                'client_outcome': 'Site que supera a concorrência',
                'base_value': 6000,
                'effort': '4-6 semanas',
                'roi_timeline': '90 dias',
                'proof_metrics': 'Análise competitiva + métricas de performance',
                'urgency': 'Alta - market share em risco',
                'detection': {
                    'outdated_stack': True,
                    'poor_ux': True
                }
            }
        }
        
        # Multiplicadores por tamanho de negócio
        self.business_size_multipliers = {
            'small': 1.0,    # < 10 funcionários
            'medium': 1.8,   # 10-50 funcionários  
            'large': 3.0     # 50+ funcionários
        }
    
    def estimate_business_size(self, tech_stack: Dict, website_complexity: int) -> str:
        """Estimar tamanho do negócio baseado em indicadores"""
        
        # Indicadores de empresa maior
        enterprise_indicators = 0
        
        if 'Salesforce' in str(tech_stack):
            enterprise_indicators += 2
        if 'HubSpot' in str(tech_stack):
            enterprise_indicators += 1
        if website_complexity > 50:  # Muitas páginas/funcionalidades
            enterprise_indicators += 1
        if any(tech in str(tech_stack) for tech in ['React', 'Angular', 'Vue']):
            enterprise_indicators += 1
            
        if enterprise_indicators >= 3:
            return 'large'
        elif enterprise_indicators >= 1:
            return 'medium'
        else:
            return 'small'
    
    def detect_business_problems(self, url: str, tech_stack: Dict, performance_data: Optional[Dict] = None) -> List[BusinessOpportunity]:
        """Detectar problemas do ponto de vista do CLIENTE"""
        
        problems = []
        business_size = self.estimate_business_size(tech_stack, len(str(tech_stack)))
        multiplier = self.business_size_multipliers[business_size]
        
        # Problema: Site lento (cliente SENTE isso)
        if performance_data and performance_data.get('performance_score', 100) < 60:
            opp_data = self.business_opportunities['slow_website']
            problems.append(BusinessOpportunity(
                business_problem=opp_data['business_problem'],
                current_impact=opp_data['current_impact'],
                our_solution=opp_data['our_solution'],
                client_outcome=opp_data['client_outcome'],
                estimated_value=opp_data['base_value'] * multiplier,
                implementation_effort=opp_data['effort'],
                roi_timeline=opp_data['roi_timeline'],
                proof_metrics=opp_data['proof_metrics'],
                urgency_level=opp_data['urgency']
            ))
        
        # Problema: Não tem analytics (cliente NÃO sabe)
        if not tech_stack.get('analytics'):
            opp_data = self.business_opportunities['invisible_problems']
            problems.append(BusinessOpportunity(
                business_problem=opp_data['business_problem'],
                current_impact=opp_data['current_impact'],
                our_solution=opp_data['our_solution'],
                client_outcome=opp_data['client_outcome'],
                estimated_value=opp_data['base_value'] * multiplier,
                implementation_effort=opp_data['effort'],
                roi_timeline=opp_data['roi_timeline'],
                proof_metrics=opp_data['proof_metrics'],
                urgency_level=opp_data['urgency']
            ))
        
        # Problema: Sem SSL (segurança)
        if not url.startswith('https://'):
            opp_data = self.business_opportunities['security_risk']
            problems.append(BusinessOpportunity(
                business_problem=opp_data['business_problem'],
                current_impact=opp_data['current_impact'],
                our_solution=opp_data['our_solution'],
                client_outcome=opp_data['client_outcome'],
                estimated_value=opp_data['base_value'] * multiplier,
                implementation_effort=opp_data['effort'],
                roi_timeline=opp_data['roi_timeline'],
                proof_metrics=opp_data['proof_metrics'],
                urgency_level=opp_data['urgency']
            ))
        
        # Problema: Tech stack outdated (visual)
        if any(tech in str(tech_stack).lower() for tech in ['wordpress', 'jquery']) and business_size != 'large':
            opp_data = self.business_opportunities['looks_outdated']
            problems.append(BusinessOpportunity(
                business_problem=opp_data['business_problem'],
                current_impact=opp_data['current_impact'],
                our_solution=opp_data['our_solution'],
                client_outcome=opp_data['client_outcome'],
                estimated_value=opp_data['base_value'] * multiplier,
                implementation_effort=opp_data['effort'],
                roi_timeline=opp_data['roi_timeline'],
                proof_metrics=opp_data['proof_metrics'],
                urgency_level=opp_data['urgency']
            ))
        
        # Problema: SEO ruim (não aparece no Google)
        if (performance_data and performance_data.get('seo_score', 100) < 80) or not tech_stack.get('analytics'):
            opp_data = self.business_opportunities['not_found_google']
            problems.append(BusinessOpportunity(
                business_problem=opp_data['business_problem'],
                current_impact=opp_data['current_impact'],
                our_solution=opp_data['our_solution'],
                client_outcome=opp_data['client_outcome'],
                estimated_value=opp_data['base_value'] * multiplier,
                implementation_effort=opp_data['effort'],
                roi_timeline=opp_data['roi_timeline'],
                proof_metrics=opp_data['proof_metrics'],
                urgency_level=opp_data['urgency']
            ))
        
        return problems
    
    def calculate_monthly_loss(self, problems: List[BusinessOpportunity]) -> float:
        """Calcular perda mensal estimada com problemas atuais"""
        
        # Estimativas conservadoras de impacto mensal
        loss_estimates = {
            'Site demora para carregar': 500,    # Bounce rate alto
            'Difícil de encontrar no Google': 800,  # Perda de tráfego orgânico
            'Site parece desatualizado': 300,    # Perda de credibilidade
            'Perdendo clientes sem saber por quê': 400,  # Decisões ruins
            'Site vulnerável a ataques': 200     # Risco/downtime
        }
        
        total_monthly_loss = 0
        for problem in problems:
            estimated_loss = loss_estimates.get(problem.business_problem, 100)
            total_monthly_loss += estimated_loss
            
        return total_monthly_loss
    
    def analyze_client_opportunities(self, url: str, tech_stack: Dict, performance_data: Optional[Dict] = None) -> Optional[ClientAnalysis]:
        """Análise completa focada na perspectiva do cliente"""
        try:
            logger.info(f"🎯 Analyzing client-focused opportunities for {url}")
            
            # Filter invalid URLs
            if any(domain in url.lower() for domain in ['instagram.com', 'facebook.com', 'twitter.com']):
                logger.info(f"Skipping social media URL: {url}")
                return None
            
            # Detectar problemas de negócio
            business_problems = self.detect_business_problems(url, tech_stack, performance_data)
            
            if not business_problems:
                logger.info(f"No business problems detected for {url}")
                return None
            
            # Categorizar por urgência
            immediate_issues = [p for p in business_problems if p.urgency_level in ['Crítica', 'Alta']]
            hidden_opportunities = [p for p in business_problems if 'saber' in p.business_problem]
            competitive_gaps = [p for p in business_problems if 'concorr' in p.business_problem.lower()]
            
            # Calcular valores
            total_monthly_loss = self.calculate_monthly_loss(business_problems)
            quick_wins_value = sum(p.estimated_value for p in business_problems if any(timeframe in p.implementation_effort for timeframe in ['1 semana', '3-5 dias', '1-2 semanas']))
            strategic_value = sum(p.estimated_value for p in business_problems)
            
            analysis = ClientAnalysis(
                domain=url,
                business_size=self.estimate_business_size(tech_stack, len(str(tech_stack))),
                immediate_issues=immediate_issues,
                hidden_opportunities=hidden_opportunities,
                competitive_gaps=competitive_gaps,
                total_monthly_loss=total_monthly_loss,
                quick_wins_value=quick_wins_value,
                strategic_value=strategic_value
            )
            
            logger.info(f"✅ Client analysis complete: ${strategic_value:,.0f} total opportunity value")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing client opportunities for {url}: {e}")
            return None

# Demo function
def demo_client_focused_detection():
    """Demo da detecção focada no cliente"""
    print("🎯" + "="*60)
    print("   ARCO CLIENT-FOCUSED OPPORTUNITIES DETECTION")
    print("="*63)
    
    detector = ClientFocusedDetector()
    
    # Test URLs
    test_urls = [
        ("https://parkviewdentaltoronto.com", {'analytics': ['Google Analytics'], 'security': ['SSL']}),
        ("http://argentocpa.ca", {'cms': ['WordPress'], 'javascript': ['jQuery']}),
        ("https://yaletownaccounting.com", {'cms': ['WordPress'], 'ecommerce': ['WooCommerce']})
    ]
    
    for url, mock_tech_stack in test_urls:
        print(f"\n🔍 Analyzing: {url}")
        
        # Mock performance data
        mock_performance = {'performance_score': 45, 'seo_score': 65}
        
        analysis = detector.analyze_client_opportunities(url, mock_tech_stack, mock_performance)
        
        if analysis:
            print(f"💼 BUSINESS PROBLEMS IDENTIFIED:")
            print(f"   • Monthly Loss: ${analysis.total_monthly_loss:,.0f}/month (doing nothing)")
            print(f"   • Quick Wins Value: ${analysis.quick_wins_value:,.0f} (30-day delivery)")
            print(f"   • Total Opportunity: ${analysis.strategic_value:,.0f}")
            print(f"   • Business Size: {analysis.business_size.title()}")
            
            print(f"\n   🔥 IMMEDIATE ISSUES (Client Already Feels):")
            for issue in analysis.immediate_issues[:2]:
                print(f"      • {issue.business_problem}")
                print(f"        Impact: {issue.current_impact}")
                print(f"        Solution: {issue.our_solution}")
                print(f"        Value: ${issue.estimated_value:,.0f}")
                
            print(f"\n   💡 HIDDEN OPPORTUNITIES (Client Doesn't Know):")
            for opp in analysis.hidden_opportunities[:1]:
                print(f"      • {opp.business_problem}")
                print(f"        Impact: {opp.current_impact}")
                print(f"        Value: ${opp.estimated_value:,.0f}")
        else:
            print(f"   • No business problems detected")
    
    print(f"\n🎯 KEY INSIGHTS:")
    print(f"   • Language focused on BUSINESS impact, not tech")
    print(f"   • Values adjusted by business size")
    print(f"   • Urgency levels drive action")
    print(f"   • ROI timelines are realistic")
    
    print("\n" + "="*63)
    print("   CLIENT-FOCUSED ANALYSIS COMPLETE")
    print("="*63)

if __name__ == "__main__":
    demo_client_focused_detection()