#!/usr/bin/env python3
"""
🎯 ARCO ADS INTELLIGENCE ENGINE
Detecção de vazamentos em campanhas de ads para ROI imediato

FILOSOFIA: Ads operam em ciclos de 7-30 dias, não 6-12 meses como websites.
Por isso, detectamos vazamentos que geram economia IMEDIATA, não melhorias futuras.

Core Value Proposition:
- Economia ≥ R$ 6k/mês em ≤ 30 dias
- ROI mensurável desde o primeiro dia
- Vazamentos detectáveis via APIs públicas
"""

import requests
import json
import time
import re
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class AdLeak:
    """Representa um vazamento detectado em campanhas de ads"""
    leak_type: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    estimated_monthly_loss: float  # em USD
    detection_source: str
    evidence: Dict
    fix_timeline: str  # '24h', '7d', '30d'
    fix_complexity: str  # 'simple', 'medium', 'complex'

@dataclass
class AdsProfile:
    """Perfil completo de inteligência de ads de uma empresa"""
    company_name: str
    domain: str
    detected_ad_platforms: List[str]
    estimated_monthly_spend: float
    primary_ad_channel: str
    detected_leaks: List[AdLeak]
    tech_tax_score: float  # 0-10, onde 10 = máximo vazamento
    immediate_savings_potential: float
    decision_maker_profile: Dict
    contact_info: Dict

class MetaAdsIntelligence:
    """Sistema de inteligência para Meta Ads (Facebook/Instagram)"""
    
    def __init__(self):
        self.base_url = "https://www.facebook.com/ads/library/api"
        self.transparency_url = "https://www.facebook.com/ads/library"
        
    def detect_ad_spend_patterns(self, business_name: str, page_id: str = None) -> Dict:
        """
        Detecta padrões de gastos em Meta Ads via FB Ads Library
        
        VAZAMENTOS DETECTADOS:
        1. Creative fatigue (mesmo criativo > 45 dias)
        2. Targeting overlap (CTR < 1.2%)
        3. Budget mal distribuído (CPC > benchmark + 40%)
        4. Retargeting leak (frequency > 4.5x)
        """
        
        logger.info(f"🔍 Analisando Meta Ads para: {business_name}")
        
        try:
            # Simular busca na Meta Ads Library (API pública)
            search_params = {
                'search_terms': business_name,
                'ad_type': 'ALL',
                'ad_active_status': 'ALL',
                'ad_reached_countries': ['BR', 'US', 'CA'],
                'search_page_ids': page_id if page_id else None
            }
            
            # Em produção, usar FB Ads Library API real
            detected_ads = self._simulate_meta_ads_data(business_name)
            
            leaks = []
            total_estimated_spend = 0
            
            # LEAK 1: Creative Fatigue Detection
            for ad in detected_ads.get('ads', []):
                days_running = (datetime.now() - datetime.fromisoformat(ad['start_date'])).days
                
                if days_running > 45 and ad['delivery_info']['spend'] > 500:
                    leak = AdLeak(
                        leak_type="creative_fatigue",
                        severity="high",
                        estimated_monthly_loss=ad['delivery_info']['spend'] * 0.35,  # 35% waste
                        detection_source="Meta Ads Library",
                        evidence={
                            "ad_id": ad['id'],
                            "days_running": days_running,
                            "creative_title": ad['creative']['title'],
                            "current_ctr": ad['delivery_info']['ctr'],
                            "benchmark_ctr": 2.1  # Benchmark odontologia
                        },
                        fix_timeline="7d",
                        fix_complexity="simple"
                    )
                    leaks.append(leak)
                    total_estimated_spend += ad['delivery_info']['spend']
            
            # LEAK 2: Low CTR Detection
            for ad in detected_ads.get('ads', []):
                ctr = ad['delivery_info']['ctr']
                if ctr < 1.2:  # Abaixo do benchmark
                    leak = AdLeak(
                        leak_type="low_ctr_targeting",
                        severity="critical",
                        estimated_monthly_loss=ad['delivery_info']['spend'] * 0.45,
                        detection_source="Meta Performance Analysis",
                        evidence={
                            "ad_id": ad['id'],
                            "current_ctr": ctr,
                            "benchmark_ctr": 2.1,
                            "ctr_gap": round(((2.1 - ctr) / 2.1) * 100, 1)
                        },
                        fix_timeline="24h",
                        fix_complexity="medium"
                    )
                    leaks.append(leak)
            
            return {
                'platform': 'Meta Ads',
                'detected_leaks': leaks,
                'estimated_monthly_spend': total_estimated_spend,
                'intelligence_confidence': 0.85,
                'data_freshness': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro na análise Meta Ads: {e}")
            return {'error': str(e)}
    
    def _simulate_meta_ads_data(self, business_name: str) -> Dict:
        """Simula dados da Meta Ads Library para desenvolvimento"""
        return {
            'ads': [
                {
                    'id': 'meta_ad_001',
                    'start_date': '2025-04-15T00:00:00',
                    'creative': {
                        'title': 'Implante Dentário Premium',
                        'image_url': 'https://example.com/ad1.jpg'
                    },
                    'delivery_info': {
                        'spend': 2800,  # USD/mês
                        'ctr': 0.8,  # Baixo CTR
                        'frequency': 5.2  # Alta frequência
                    }
                },
                {
                    'id': 'meta_ad_002', 
                    'start_date': '2025-01-10T00:00:00',  # > 45 dias
                    'creative': {
                        'title': 'Clareamento Dental',
                        'image_url': 'https://example.com/ad2.jpg'
                    },
                    'delivery_info': {
                        'spend': 1900,
                        'ctr': 1.1,
                        'frequency': 3.8
                    }
                }
            ]
        }

class GoogleAdsIntelligence:
    """Sistema de inteligência para Google Ads"""
    
    def __init__(self):
        self.base_url = "https://transparencyreport.google.com/political-ads"
        
    def detect_search_ads_leaks(self, domain: str, business_name: str) -> Dict:
        """
        Detecta vazamentos em Google Search Ads
        
        VAZAMENTOS DETECTADOS:
        1. Quality Score baixo (< 6/10)
        2. CPC acima do benchmark (+40%)
        3. Search lost IS > 30%
        4. Keywords canibalizando
        """
        
        logger.info(f"🔍 Analisando Google Ads para: {domain}")
        
        try:
            # Simular análise de Google Ads (em produção usar Google Ads API)
            search_data = self._simulate_google_ads_data(business_name)
            
            leaks = []
            
            # LEAK 1: Quality Score Issues
            for keyword in search_data.get('keywords', []):
                if keyword['quality_score'] < 6:
                    leak = AdLeak(
                        leak_type="low_quality_score",
                        severity="high",
                        estimated_monthly_loss=keyword['monthly_spend'] * 0.3,
                        detection_source="Google Ads Quality Score",
                        evidence={
                            "keyword": keyword['term'],
                            "quality_score": keyword['quality_score'],
                            "current_cpc": keyword['avg_cpc'],
                            "benchmark_cpc": keyword['benchmark_cpc']
                        },
                        fix_timeline="7d",
                        fix_complexity="medium"
                    )
                    leaks.append(leak)
            
            # LEAK 2: High CPC vs Benchmark
            for keyword in search_data.get('keywords', []):
                cpc_premium = (keyword['avg_cpc'] - keyword['benchmark_cpc']) / keyword['benchmark_cpc']
                if cpc_premium > 0.4:  # 40% acima do benchmark
                    leak = AdLeak(
                        leak_type="high_cpc_premium",
                        severity="critical",
                        estimated_monthly_loss=keyword['monthly_spend'] * cpc_premium * 0.6,
                        detection_source="CPC Benchmark Analysis",
                        evidence={
                            "keyword": keyword['term'],
                            "current_cpc": keyword['avg_cpc'],
                            "benchmark_cpc": keyword['benchmark_cpc'],
                            "premium_percentage": round(cpc_premium * 100, 1)
                        },
                        fix_timeline="24h",
                        fix_complexity="simple"
                    )
                    leaks.append(leak)
            
            return {
                'platform': 'Google Ads',
                'detected_leaks': leaks,
                'estimated_monthly_spend': sum(k['monthly_spend'] for k in search_data.get('keywords', [])),
                'intelligence_confidence': 0.78,
                'data_freshness': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro na análise Google Ads: {e}")
            return {'error': str(e)}
    
    def _simulate_google_ads_data(self, business_name: str) -> Dict:
        """Simula dados de Google Ads para desenvolvimento"""
        return {
            'keywords': [
                {
                    'term': 'implante dentário',
                    'quality_score': 4,  # Baixo
                    'avg_cpc': 12.50,
                    'benchmark_cpc': 8.20,
                    'monthly_spend': 3200
                },
                {
                    'term': 'dentista rio de janeiro',
                    'quality_score': 7,
                    'avg_cpc': 6.80,
                    'benchmark_cpc': 5.90,
                    'monthly_spend': 1800
                }
            ]
        }

class TikTokAdsIntelligence:
    """Sistema de inteligência para TikTok Ads"""
    
    def detect_tiktok_creative_fatigue(self, business_name: str) -> Dict:
        """
        Detecta fadiga de criativos no TikTok
        
        VAZAMENTOS ESPECÍFICOS TIKTOK:
        1. Creative > 21 dias (ciclo mais rápido)
        2. CTR < 2.5% (benchmark TikTok mais alto)
        3. Creative não otimizado para mobile
        """
        
        logger.info(f"🔍 Analisando TikTok Ads para: {business_name}")
        
        # Simular dados TikTok
        creative_data = {
            'creatives': [
                {
                    'id': 'tiktok_001',
                    'start_date': '2025-05-01T00:00:00',
                    'ctr': 1.8,  # Baixo para TikTok
                    'spend': 1500
                }
            ]
        }
        
        leaks = []
        for creative in creative_data['creatives']:
            days_running = (datetime.now() - datetime.fromisoformat(creative['start_date'])).days
            
            if creative['ctr'] < 2.5:
                leak = AdLeak(
                    leak_type="tiktok_low_engagement",
                    severity="high",
                    estimated_monthly_loss=creative['spend'] * 0.4,
                    detection_source="TikTok Creative Center",
                    evidence={
                        "creative_id": creative['id'],
                        "current_ctr": creative['ctr'],
                        "benchmark_ctr": 2.5,
                        "days_running": days_running
                    },
                    fix_timeline="48h",
                    fix_complexity="medium"
                )
                leaks.append(leak)
        
        return {
            'platform': 'TikTok Ads',
            'detected_leaks': leaks,
            'estimated_monthly_spend': sum(c['spend'] for c in creative_data['creatives']),
            'intelligence_confidence': 0.72
        }

class AdsIntelligenceEngine:
    """Engine principal de inteligência de ads - integra todos os canais"""
    
    def __init__(self):
        self.meta_intel = MetaAdsIntelligence()
        self.google_intel = GoogleAdsIntelligence()
        self.tiktok_intel = TikTokAdsIntelligence()
        
    def comprehensive_ads_audit(self, company_name: str, domain: str, 
                               contact_info: Dict = None) -> AdsProfile:
        """
        Auditoria completa de ads intelligence
        
        PROCESSO:
        1. Detectar presença em cada plataforma
        2. Analisar vazamentos por canal
        3. Calcular TechTax Score
        4. Priorizar quick wins por ROI
        """
        
        logger.info(f"🚀 Iniciando auditoria completa para: {company_name}")
        
        # Analisar cada plataforma
        meta_results = self.meta_intel.detect_ad_spend_patterns(company_name)
        google_results = self.google_intel.detect_search_ads_leaks(domain, company_name)
        tiktok_results = self.tiktok_intel.detect_tiktok_creative_fatigue(company_name)
        
        # Consolidar vazamentos
        all_leaks = []
        total_spend = 0
        platforms = []
        
        for results in [meta_results, google_results, tiktok_results]:
            if 'detected_leaks' in results:
                all_leaks.extend(results['detected_leaks'])
                total_spend += results.get('estimated_monthly_spend', 0)
                platforms.append(results['platform'])
        
        # Calcular TechTax Score (0-10)
        tech_tax_score = self._calculate_tech_tax_score(all_leaks, total_spend)
        
        # Calcular economia imediata potencial
        immediate_savings = sum(leak.estimated_monthly_loss for leak in all_leaks)
        
        # Identificar canal principal
        primary_channel = self._identify_primary_channel(meta_results, google_results, tiktok_results)
        
        # Gerar perfil de decisor
        decision_maker = self._generate_decision_maker_profile(company_name, total_spend)
        
        return AdsProfile(
            company_name=company_name,
            domain=domain,
            detected_ad_platforms=platforms,
            estimated_monthly_spend=total_spend,
            primary_ad_channel=primary_channel,
            detected_leaks=all_leaks,
            tech_tax_score=tech_tax_score,
            immediate_savings_potential=immediate_savings,
            decision_maker_profile=decision_maker,
            contact_info=contact_info or {}
        )
    
    def _calculate_tech_tax_score(self, leaks: List[AdLeak], total_spend: float) -> float:
        """
        Calcula TechTax Score baseado em:
        - Número de vazamentos críticos
        - % do budget sendo desperdiçado
        - Facilidade de correção
        """
        
        if not leaks or total_spend == 0:
            return 0.0
        
        critical_leaks = len([l for l in leaks if l.severity == 'critical'])
        total_waste = sum(leak.estimated_monthly_loss for leak in leaks)
        waste_percentage = min(total_waste / total_spend, 1.0)
        
        # Score base na porcentagem de desperdício
        base_score = waste_percentage * 7  # Max 7 pontos
        
        # Bonus por vazamentos críticos
        critical_bonus = min(critical_leaks * 0.5, 2.0)  # Max 2 pontos
        
        # Bonus por facilidade de correção (quick wins)
        quick_wins = len([l for l in leaks if l.fix_timeline in ['24h', '48h']])
        quick_win_bonus = min(quick_wins * 0.2, 1.0)  # Max 1 ponto
        
        final_score = min(base_score + critical_bonus + quick_win_bonus, 10.0)
        
        return round(final_score, 1)
    
    def _identify_primary_channel(self, meta_results: Dict, 
                                google_results: Dict, tiktok_results: Dict) -> str:
        """Identifica o canal com maior gasto"""
        
        spends = {
            'Meta Ads': meta_results.get('estimated_monthly_spend', 0),
            'Google Ads': google_results.get('estimated_monthly_spend', 0),
            'TikTok Ads': tiktok_results.get('estimated_monthly_spend', 0)
        }
        
        return max(spends.items(), key=lambda x: x[1])[0]
    
    def _generate_decision_maker_profile(self, company_name: str, monthly_spend: float) -> Dict:
        """Gera perfil do tomador de decisão baseado no gasto"""
        
        if monthly_spend > 10000:
            return {
                'likely_title': 'Marketing Director',
                'decision_authority': 'high',
                'budget_approval': 'autonomous',
                'pain_point': 'ROI accountability',
                'urgency_level': 'high'
            }
        elif monthly_spend > 3000:
            return {
                'likely_title': 'Marketing Manager',
                'decision_authority': 'medium',
                'budget_approval': 'needs_approval',
                'pain_point': 'performance optimization',
                'urgency_level': 'medium'
            }
        else:
            return {
                'likely_title': 'Owner/Founder',
                'decision_authority': 'high',
                'budget_approval': 'autonomous',
                'pain_point': 'cost efficiency',
                'urgency_level': 'high'
            }
    
    def generate_quick_win_report(self, profile: AdsProfile) -> Dict:
        """
        Gera relatório focado em quick wins para conversão imediata
        
        ESTRUTURA:
        1. Headline de impacto (economia mensal)
        2. Top 3 vazamentos mais críticos
        3. Evidências visuais (screenshots simulados)
        4. Timeline de correção
        5. ROI projetado
        """
        
        # Ordenar vazamentos por impacto (economia * facilidade)
        prioritized_leaks = sorted(
            profile.detected_leaks,
            key=lambda l: l.estimated_monthly_loss * (2 if l.fix_timeline in ['24h', '48h'] else 1),
            reverse=True
        )
        
        top_3_leaks = prioritized_leaks[:3]
        
        # Calcular ROI do audit ARCO
        audit_investment = 147  # USD
        monthly_savings = sum(leak.estimated_monthly_loss for leak in top_3_leaks)
        roi_percentage = ((monthly_savings - audit_investment) / audit_investment) * 100
        
        report = {
            'headline': {
                'monthly_savings': f"${monthly_savings:,.0f}",
                'roi_percentage': f"{roi_percentage:.0f}%",
                'payback_days': max(1, int(audit_investment / (monthly_savings / 30)))
            },
            'critical_leaks': [
                {
                    'title': self._leak_to_title(leak),
                    'monthly_loss': f"${leak.estimated_monthly_loss:,.0f}",
                    'fix_timeline': leak.fix_timeline,
                    'evidence': leak.evidence,
                    'urgency_reason': self._generate_urgency_reason(leak)
                }
                for leak in top_3_leaks
            ],
            'next_steps': {
                'immediate_action': 'Schedule 12-min diagnostic call',
                'timeline': 'Fixes implemented within 7 days',
                'guarantee': 'Savings < $6k/year = 100% refund + $50 credit'
            },
            'tech_tax_assessment': {
                'score': f"{profile.tech_tax_score}/10",
                'category': self._score_to_category(profile.tech_tax_score),
                'benchmark': 'Industry average: 3.2/10'
            }
        }
        
        return report
    
    def _leak_to_title(self, leak: AdLeak) -> str:
        """Converte vazamento técnico em headline de negócio"""
        titles = {
            'creative_fatigue': 'Creative rodando há {days} dias - fadiga comprovada',
            'low_ctr_targeting': 'CTR {ctr}% vs benchmark {benchmark}% - targeting ineficiente',
            'high_cpc_premium': 'CPC {premium}% acima do mercado - dinheiro queimado',
            'low_quality_score': 'Quality Score {score}/10 - penalização severa',
            'tiktok_low_engagement': 'Engajamento TikTok {ctr}% - criativo não converte'
        }
        
        template = titles.get(leak.leak_type, 'Vazamento detectado - otimização necessária')
        
        # Substituir variáveis da evidência
        for key, value in leak.evidence.items():
            template = template.replace(f'{{{key}}}', str(value))
        
        return template
    
    def _generate_urgency_reason(self, leak: AdLeak) -> str:
        """Gera razão de urgência específica para cada tipo de vazamento"""
        urgency_map = {
            'creative_fatigue': 'Cada dia adicional reduz CTR em 0.1%',
            'low_ctr_targeting': 'Competidores capturando seu tráfego qualificado',
            'high_cpc_premium': 'Orçamento esgotando 40% mais rápido que necessário',
            'low_quality_score': 'Google penalizando posicionamento dos anúncios',
            'tiktok_low_engagement': 'Algoritmo TikTok reduzindo reach organicamente'
        }
        
        return urgency_map.get(leak.leak_type, 'Impacto composto aumenta diariamente')
    
    def _score_to_category(self, score: float) -> str:
        """Converte score numérico em categoria de risco"""
        if score >= 8.0:
            return 'EMERGENCY - Bleeding money daily'
        elif score >= 6.0:
            return 'HIGH RISK - Significant waste detected'
        elif score >= 4.0:
            return 'MODERATE - Optimization opportunities'
        elif score >= 2.0:
            return 'LOW RISK - Minor inefficiencies'
        else:
            return 'OPTIMIZED - Rare in SME market'

# Função de demonstração
def main():
    """Demo do Ads Intelligence Engine"""
    
    print("🚀 ARCO ADS INTELLIGENCE ENGINE - DEMO")
    print("=" * 50)
    
    # Simular empresa real
    test_company = {
        'name': 'Clínica Odontológica Premium',
        'domain': 'dentistapremium.com.br',
        'contact': {
            'email': 'marketing@dentistapremium.com.br',
            'phone': '+55 21 99999-9999'
        }
    }
    
    # Inicializar engine
    engine = AdsIntelligenceEngine()
    
    # Executar auditoria completa
    print(f"🔍 Analisando: {test_company['name']}")
    print("⏳ Coletando dados de Meta, Google e TikTok...")
    
    profile = engine.comprehensive_ads_audit(
        test_company['name'],
        test_company['domain'],
        test_company['contact']
    )
    
    # Gerar relatório de quick wins
    report = engine.generate_quick_win_report(profile)
    
    # Exibir resultados
    print("\n📊 RESULTADOS DA AUDITORIA")
    print("=" * 30)
    print(f"Empresa: {profile.company_name}")
    print(f"Canais detectados: {', '.join(profile.detected_ad_platforms)}")
    print(f"Gasto mensal estimado: ${profile.estimated_monthly_spend:,.0f}")
    print(f"TechTax Score: {profile.tech_tax_score}/10 ({engine._score_to_category(profile.tech_tax_score)})")
    
    print(f"\n💰 OPORTUNIDADE IMEDIATA")
    print("=" * 25)
    print(f"Economia mensal potencial: {report['headline']['monthly_savings']}")
    print(f"ROI do audit: {report['headline']['roi_percentage']}")
    print(f"Payback: {report['headline']['payback_days']} dias")
    
    print(f"\n🔥 TOP 3 VAZAMENTOS CRÍTICOS")
    print("=" * 30)
    for i, leak in enumerate(report['critical_leaks'], 1):
        print(f"{i}. {leak['title']}")
        print(f"   💸 Perda mensal: {leak['monthly_loss']}")
        print(f"   ⏰ Correção: {leak['fix_timeline']}")
        print(f"   🚨 Urgência: {leak['urgency_reason']}")
        print()
    
    # Salvar resultado
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results/ads_intelligence_audit_{timestamp}.json"
    
    output_data = {
        'profile': asdict(profile),
        'quick_win_report': report,
        'audit_timestamp': datetime.now().isoformat(),
        'engine_version': '1.0.0'
    }
    
    try:
        import os
        os.makedirs('results', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"📁 Relatório salvo: {filename}")
        
    except Exception as e:
        print(f"⚠️ Erro ao salvar: {e}")
    
    print("\n✅ AUDITORIA COMPLETA!")
    print("🎯 Próximo passo: Agendar call de 12 min para demonstração ao vivo")

if __name__ == "__main__":
    main()
