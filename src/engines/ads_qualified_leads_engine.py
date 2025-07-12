#!/usr/bin/env python3
"""
🎯 ADS QUALIFIED LEADS ENGINE - Otimizado ARCO Methodology
Evolução inteligente baseada na estrutura ARCO existente:
- Parte da análise de ads dentro do ICP
- Usa RealAdsIntelligenceEngine como base
- Qualifica por sinais específicos (não busca genérica)
- Metodologia superior focada em ADS LEAKS
"""

import os
import sys
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

# Add ARCO engine paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from engines.real_ads_intelligence_engine import RealAdsIntelligenceEngine
from specialist.ultra_qualified_leads_detector import UltraQualifiedLeadsDetector, AdLeak
from config.arco_config_manager import get_config

logger = logging.getLogger(__name__)

class AdsQualifiedLeadsEngine:
    """
    Engine otimizado que PARTE dos ads disponíveis dentro do ICP,
    em vez de busca genérica. Baseado na metodologia ARCO superior.
    """
    
    def __init__(self):
        self.config = get_config()
        self.real_ads_engine = RealAdsIntelligenceEngine()
        self.ultra_detector = UltraQualifiedLeadsDetector()
        
        # ICP Definitions baseado na metodologia ARCO
        self.icp_definitions = {
            'dental_premium_toronto': {
                'industry': 'dental',
                'location_radius': 'Toronto GTA',
                'spend_threshold': 15000,  # USD/month minimum
                'target_signals': [
                    'lighthouse_mobile_score < 45',
                    'saas_renewal_window <= 60_days',
                    'ads_ctr_below_benchmark',
                    'performance_leak_critical'
                ],
                'qualification_minimum': 2  # Need 2+ signals
            },
            
            'dermatology_miami_tampa': {
                'industry': 'dermatology',
                'location_radius': 'Miami-Tampa Corridor',
                'spend_threshold': 20000,
                'target_signals': [
                    'meta_ads_active',
                    'tiktok_opportunity_gap',
                    'lighthouse_mobile_score < 40',
                    'new_leadership_90_days'
                ],
                'qualification_minimum': 2
            },
            
            'dtc_petfood_premium': {
                'industry': 'pet_food',
                'location_radius': 'US Northeast/Midwest',
                'spend_threshold': 25000,
                'target_signals': [
                    'multi_platform_ads_active',
                    'attribution_leak_detected',
                    'conversion_rate_below_benchmark',
                    'tech_stack_bloat'
                ],
                'qualification_minimum': 3  # Higher threshold for DTC
            }
        }
        
        # ADS PLATFORMS INTELLIGENCE (ARCO's focus)
        self.ads_platforms_analysis = {
            'meta': {
                'api_available': True,
                'intelligence_depth': 'deep',
                'leak_detection': ['audience_overlap', 'budget_waste', 'creative_fatigue']
            },
            'google': {
                'api_available': True,
                'intelligence_depth': 'deep', 
                'leak_detection': ['keyword_cannibalization', 'quality_score_drops', 'bid_inefficiency']
            },
            'tiktok': {
                'api_available': False,
                'intelligence_depth': 'surface',
                'leak_detection': ['creative_mismatch', 'audience_targeting_waste']
            }
        }

    def discover_ads_qualified_prospects(self, icp_segment: str, target_count: int = 20) -> List[Dict]:
        """
        METODOLOGIA OTIMIZADA: Parte dos ads ativos dentro do ICP,
        não de busca genérica. Muito mais inteligente.
        """
        logger.info(f"🎯 Descobrindo prospects qualificados por ADS no ICP: {icp_segment}")
        
        if icp_segment not in self.icp_definitions:
            raise ValueError(f"ICP segment {icp_segment} não definido")
            
        icp_config = self.icp_definitions[icp_segment]
        qualified_prospects = []
        
        # FASE 1: ADS INTELLIGENCE DISCOVERY
        # Em vez de Google Places, usar Meta/Google APIs para encontrar
        # empresas que JÁ fazem ads no nosso ICP
        ads_active_companies = self._discover_companies_via_ads_apis(icp_config)
        
        # FASE 2: SIGNAL-BASED QUALIFICATION
        # Qualificar por sinais específicos, não por dados genéricos        for company in ads_active_companies[:target_count]:
            qualification_result = self._analyze_ads_qualification_signals(company, icp_config)
            
            if qualification_result['qualified']:
                qualified_prospects.append(qualification_result)
                
        logger.info(f"✅ {len(qualified_prospects)} prospects qualificados descobertos")
        return qualified_prospects

    def _discover_companies_via_ads_apis(self, icp_config: Dict) -> List[Dict]:
        """
        MÉTODO SUPERIOR: Descobrir empresas através de ads ativos,
        não através de busca genérica.
        """
        companies = []
        
        try:
            # Meta Business API: Buscar anunciantes ativos no setor
            if self.real_ads_engine.meta_api:
                meta_advertisers = self._find_meta_advertisers_in_industry(
                    icp_config['industry'], 
                    icp_config['location_radius']
                )
                companies.extend(meta_advertisers)
                
            # Google Ads API: Buscar anunciantes ativos
            if self.real_ads_engine.google_api:
                google_advertisers = self._find_google_advertisers_in_industry(
                    icp_config['industry'],
                    icp_config['location_radius']  
                )
                companies.extend(google_advertisers)
                
            # Remove duplicatas por domínio
            unique_companies = self._deduplicate_by_domain(companies)
            
            logger.info(f"📊 {len(unique_companies)} empresas ativas em ads descobertas")
            return unique_companies
            
        except Exception as e:
            logger.error(f"❌ Erro na descoberta via APIs de ads: {e}")
            # Fallback para método ARCO existente se APIs falharem
            return self._fallback_to_arco_discovery(icp_config)

    def _find_meta_advertisers_in_industry(self, industry: str, location: str) -> List[Dict]:
        """
        Usar Meta Business API para encontrar anunciantes ativos
        (muito superior a busca genérica)
        """
        advertisers = []
        
        try:
            # Usar Meta Ad Library API para encontrar anunciantes ativos
            industry_keywords = self._get_industry_keywords(industry)
            
            for keyword in industry_keywords:
                search_results = self.real_ads_engine.meta_engine.search_ad_library(
                    keyword=keyword,
                    location=location,
                    active_only=True
                )
                
                for ad_data in search_results:
                    company_info = {
                        'company_name': ad_data['page_name'],
                        'website_url': ad_data.get('website_url'),
                        'meta_page_id': ad_data['page_id'],
                        'ads_detected': True,
                        'platform': 'meta',
                        'discovery_source': 'meta_ad_library'
                    }
                    advertisers.append(company_info)
                    
            return advertisers
            
        except Exception as e:
            logger.error(f"❌ Meta advertisers discovery failed: {e}")
            return []

    def _find_google_advertisers_in_industry(self, industry: str, location: str) -> List[Dict]:
        """
        Usar Google Ads API para encontrar anunciantes ativos
        """
        advertisers = []
        
        try:
            # Usar Google Ads Transparency Report ou Keyword Intelligence
            industry_keywords = self._get_industry_keywords(industry)
            
            for keyword in industry_keywords:
                # Buscar quem está fazendo ads para essas keywords
                competitors_data = self.real_ads_engine.google_engine.get_keyword_competitors(
                    keyword=keyword,
                    location=location
                )
                
                for competitor in competitors_data:
                    company_info = {
                        'company_name': competitor['advertiser_name'],
                        'website_url': competitor['display_url'],
                        'google_ads_active': True,
                        'platform': 'google',
                        'discovery_source': 'google_ads_intelligence'
                    }
                    advertisers.append(company_info)
                    
            return advertisers
            
        except Exception as e:
            logger.error(f"❌ Google advertisers discovery failed: {e}")
            return []

    def _analyze_ads_qualification_signals(self, company: Dict, icp_config: Dict) -> Dict:
        """
        CORE DA METODOLOGIA ARCO: Qualificação por sinais específicos,
        não por dados genéricos.
        """
        signals_detected = []
        qualification_score = 0
        
        try:
            website_url = company.get('website_url')
            if not website_url:
                return {'qualified': False, 'reason': 'no_website'}
                
            # SIGNAL 1: Mobile Performance Leak
            mobile_signal = self._check_mobile_performance_signal(website_url)
            if mobile_signal['detected']:
                signals_detected.append(mobile_signal)
                qualification_score += mobile_signal['score']
                
            # SIGNAL 2: SaaS Renewal Window  
            saas_signal = self._check_saas_renewal_signal(company)
            if saas_signal['detected']:
                signals_detected.append(saas_signal)
                qualification_score += saas_signal['score']
                
            # SIGNAL 3: ADS Performance Below Benchmark
            ads_signal = self._check_ads_performance_signal(company, icp_config)
            if ads_signal['detected']:
                signals_detected.append(ads_signal)
                qualification_score += ads_signal['score']
                
            # SIGNAL 4: Tech Stack Bloat
            tech_signal = self._check_tech_bloat_signal(website_url)
            if tech_signal['detected']:
                signals_detected.append(tech_signal)
                qualification_score += tech_signal['score']
                
            # QUALIFICAÇÃO FINAL
            qualified = len(signals_detected) >= icp_config['qualification_minimum']
            
            return {
                'qualified': qualified,
                'company': company,
                'signals_detected': signals_detected,
                'qualification_score': qualification_score,
                'signal_count': len(signals_detected),
                'minimum_required': icp_config['qualification_minimum']
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de sinais para {company.get('company_name')}: {e}")
            return {'qualified': False, 'reason': 'analysis_error'}

    def _check_mobile_performance_signal(self, website_url: str) -> Dict:
        """
        SIGNAL: Lighthouse mobile score < threshold = leak detectado
        """
        try:
            # Usar RealAdsIntelligenceEngine para análise real
            analysis = self.real_ads_engine.analyze_website_performance(website_url)
            mobile_score = analysis.get('mobile_score', 100)
            
            if mobile_score < 45:
                return {
                    'detected': True,
                    'signal_type': 'mobile_performance_leak',
                    'score': 25,  # High priority signal
                    'evidence': f"Mobile score: {mobile_score}/100 (critical)",
                    'estimated_monthly_loss': self._calculate_performance_loss(mobile_score),
                    'urgency': 'critical'
                }
                
            return {'detected': False}
            
        except Exception as e:
            logger.error(f"Mobile performance check failed: {e}")
            return {'detected': False}

    def _check_saas_renewal_signal(self, company: Dict) -> Dict:
        """
        SIGNAL: SaaS renewal window <= 60 days = urgency detectada
        """
        try:
            # Usar tech stack analysis do ARCO
            tech_leaks = self.ultra_detector.tech_detector.detect_tech_leaks(
                company.get('website_url'), 
                company.get('industry', 'general')
            )
            
            # Procurar por renewals próximos
            for leak in tech_leaks:
                if 'renewal' in leak.leak_type.lower() or leak.urgency == 'critical':
                    return {
                        'detected': True,
                        'signal_type': 'saas_renewal_urgency',
                        'score': 30,  # Highest priority
                        'evidence': f"Tech Tax leak: {leak.leak_type}",
                        'estimated_monthly_savings': leak.monthly_savings,
                        'urgency': 'immediate'
                    }
                    
            return {'detected': False}
            
        except Exception as e:
            logger.error(f"SaaS renewal check failed: {e}")
            return {'detected': False}

    def _check_ads_performance_signal(self, company: Dict, icp_config: Dict) -> Dict:
        """
        SIGNAL: ADS performance abaixo do benchmark = leak detectado
        """
        try:
            website_url = company.get('website_url')
            industry = icp_config['industry']
            
            # Usar RealAdsIntelligenceEngine para análise real de ads
            ads_analysis = self.real_ads_engine.get_real_ads_intelligence(
                website_url, 
                company.get('company_name')
            )
            
            # Check for performance leaks
            estimated_spend = ads_analysis.get('estimated_monthly_spend', 0)
            detected_leaks = ads_analysis.get('detected_leaks', [])
            
            if estimated_spend >= icp_config['spend_threshold'] and len(detected_leaks) >= 2:
                return {
                    'detected': True,
                    'signal_type': 'ads_performance_leak',
                    'score': 20,
                    'evidence': f"${estimated_spend:,}/month spend with {len(detected_leaks)} leaks detected",
                    'estimated_monthly_loss': sum(leak['monthly_loss'] for leak in detected_leaks),
                    'urgency': 'high'
                }
                
            return {'detected': False}
            
        except Exception as e:
            logger.error(f"Ads performance check failed: {e}")
            return {'detected': False}

    def _check_tech_bloat_signal(self, website_url: str) -> Dict:
        """
        SIGNAL: Tech stack bloat = overspending detectado
        """
        try:
            # Usar TechTaxDetector do ARCO (muito superior)
            tech_leaks = self.ultra_detector.tech_detector.detect_tech_leaks(
                website_url, 
                'general'
            )
            
            total_savings = sum(leak.monthly_savings for leak in tech_leaks)
            
            if total_savings >= 200:  # $200+ monthly savings available
                return {
                    'detected': True,
                    'signal_type': 'tech_stack_bloat',
                    'score': 15,
                    'evidence': f"{len(tech_leaks)} tech inefficiencies detected",
                    'estimated_monthly_savings': total_savings,
                    'urgency': 'medium'
                }
                
            return {'detected': False}
            
        except Exception as e:
            logger.error(f"Tech bloat check failed: {e}")
            return {'detected': False}

    def _calculate_performance_loss(self, mobile_score: float) -> float:
        """
        Calcular perda financeira baseada em mobile score ruim
        """
        # For every 10 points below 85, lose 5% conversions
        score_gap = (85 - mobile_score) / 10
        loss_rate = min(score_gap * 0.05, 0.30)  # Cap at 30% loss
        
        # Estimate base monthly ad spend (conservative)
        base_monthly_spend = 10000
        
        # Calculate monthly revenue loss
        # Assuming 3% conversion rate and $400 average value
        monthly_revenue_loss = base_monthly_spend * 0.03 * 400 * loss_rate
        
        return min(monthly_revenue_loss, base_monthly_spend * 0.4)

    def _get_industry_keywords(self, industry: str) -> List[str]:
        """
        Keywords específicos por indústria para descoberta inteligente
        """
        keywords_map = {
            'dental': [
                'dental clinic', 'dentist near me', 'cosmetic dentistry',
                'dental implants', 'teeth whitening', 'orthodontist'
            ],
            'dermatology': [
                'dermatologist', 'botox clinic', 'skin treatment',
                'cosmetic dermatology', 'anti aging', 'laser treatment'
            ],
            'pet_food': [
                'premium dog food', 'organic pet food', 'pet nutrition',
                'natural dog treats', 'grain free dog food'
            ]
        }
        
        return keywords_map.get(industry, ['business', 'company', 'service'])

    def _deduplicate_by_domain(self, companies: List[Dict]) -> List[Dict]:
        """
        Remove duplicatas por domínio
        """
        seen_domains = set()
        unique_companies = []
        
        for company in companies:
            website = company.get('website_url', '').lower()
            domain = website.replace('www.', '').replace('https://', '').replace('http://', '').split('/')[0]
            
            if domain and domain not in seen_domains:
                seen_domains.add(domain)
                unique_companies.append(company)
                
        return unique_companies

    def _fallback_to_arco_discovery(self, icp_config: Dict) -> List[Dict]:
        """
        Fallback para metodologia ARCO existente se APIs falharem
        """
        logger.warning("⚠️ Usando fallback para descoberta ARCO")
        
        # Usar UltraQualifiedLeadsDetector existente
        niche_key = list(self.ultra_detector.priority_niches.keys())[0]  # First niche as fallback
        
        leads = self.ultra_detector.discover_ultra_qualified_leads(
            niche_key, 
            limit=20
        )
        
        # Convert to expected format
        companies = []
        for lead in leads:
            companies.append({
                'company_name': lead.get('company_name'),
                'website_url': lead.get('website_url'),
                'discovery_source': 'arco_fallback'
            })
            
        return companies

    def generate_qualified_prospects_report(self, prospects: List[Dict], icp_segment: str) -> str:
        """
        Gerar relatório executivo dos prospects qualificados
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ads_qualified_prospects_{icp_segment}_{timestamp}.json"
        filepath = os.path.join('results', filename)
        
        os.makedirs('results', exist_ok=True)
        
        report_data = {
            'meta': {
                'icp_segment': icp_segment,
                'discovery_method': 'ads_intelligence_apis',
                'methodology': 'arco_optimized',
                'total_prospects': len(prospects),
                'qualified_prospects': len([p for p in prospects if p.get('qualified')]),
                'timestamp': datetime.now().isoformat()
            },
            'prospects': prospects,
            'summary': {
                'total_estimated_monthly_savings': sum(
                    sum(signal.get('estimated_monthly_savings', 0) for signal in p.get('signals_detected', []))
                    for p in prospects if p.get('qualified')
                ),
                'avg_qualification_score': sum(p.get('qualification_score', 0) for p in prospects) / max(len(prospects), 1),
                'top_signals': self._analyze_top_signals(prospects)
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"✅ Relatório salvo: {filepath}")
        return filepath

    def _analyze_top_signals(self, prospects: List[Dict]) -> Dict:
        """
        Analisar quais sinais são mais frequentes
        """
        signal_counts = {}
        
        for prospect in prospects:
            if prospect.get('qualified'):
                for signal in prospect.get('signals_detected', []):
                    signal_type = signal.get('signal_type')
                    if signal_type:
                        signal_counts[signal_type] = signal_counts.get(signal_type, 0) + 1
                        
        return dict(sorted(signal_counts.items(), key=lambda x: x[1], reverse=True))


def demo_ads_qualified_engine():
    """
    Demo da metodologia otimizada baseada no ARCO
    """
    print("🚀 ADS QUALIFIED LEADS ENGINE - Metodologia ARCO Otimizada")
    print("=" * 80)
    
    try:
        engine = AdsQualifiedLeadsEngine()
        
        # Test ICP segment
        icp_segment = 'dental_premium_toronto'
        
        print(f"🎯 Analisando ICP: {icp_segment}")
        print(f"📊 Metodologia: Descoberta via ADS APIs + Qualificação por Sinais")
        
        # Discover qualified prospects
        prospects = engine.discover_ads_qualified_prospects(icp_segment, 10)
        
        print(f"\n✅ RESULTADOS:")
        print(f"   • Total prospects analisados: {len(prospects)}")
        
        qualified = [p for p in prospects if p.get('qualified')]
        print(f"   • Prospects qualificados: {len(qualified)}")
        
        if qualified:
            print(f"\n🎯 TOP QUALIFIED PROSPECTS:")
            for i, prospect in enumerate(qualified[:3], 1):
                company = prospect['company']
                signals = prospect['signals_detected']
                print(f"\n   {i}. {company.get('company_name', 'Unknown')}")
                print(f"      • Website: {company.get('website_url')}")
                print(f"      • Qualification Score: {prospect['qualification_score']}")
                print(f"      • Signals: {len(signals)} detected")
                
                for signal in signals:
                    print(f"        - {signal['signal_type']}: {signal.get('evidence')}")
                    
        # Generate report
        report_path = engine.generate_qualified_prospects_report(prospects, icp_segment)
        print(f"\n📄 Relatório gerado: {report_path}")
        
        print(f"\n🎉 METODOLOGIA ARCO: Superior à busca genérica!")
        print(f"   • Foco em ADS ativos dentro do ICP")
        print(f"   • Qualificação por sinais específicos")
        print(f"   • Aproveitamento da estrutura ARCO existente")
        
    except Exception as e:
        print(f"❌ Erro na demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    demo_ads_qualified_engine()
