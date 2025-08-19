"""
ARCO Web Vitals & Pain Signals Engine
Analisa performance técnica e mapeia para sprints específicos
Pipeline: Confirmed Advertisers -> CrUX/PSI Analysis -> Sprint Recommendations
"""

import requests
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import time
import os

logger = logging.getLogger(__name__)

class WebVitalsEngine:
    """
    Engine para análise de Web Vitals e mapeamento de pain signals
    Usa CrUX/PSI APIs para prova de dor mensurável
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.psi_base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        
        # Sprint mapping baseado em pain signals
        self.sprint_mapping = {
            'web_vitals_patch': {
                'triggers': ['poor_lcp', 'poor_inp', 'poor_cls'],
                'price_usd': 497,
                'description': 'LCP/INP/CLS optimization + image optimization + caching'
            },
            'cro_express': {
                'triggers': ['poor_mobile_ux', 'no_ssl', 'generic_landing'],
                'price_usd': 497,
                'description': 'Landing page optimization + forms + CTA alignment'
            },
            'tracking_sane': {
                'triggers': ['no_ga4', 'broken_pixel', 'missing_events'],
                'price_usd': 497,
                'description': 'GA4/GTM setup + Meta/Google pixels + conversion events'
            },
            'leadflow_rescue': {
                'triggers': ['form_errors', 'no_whatsapp_tracking', 'missing_thankyou'],
                'price_usd': 497,
                'description': 'Form optimization + WhatsApp tracking + lead nurture'
            }
        }
        
        # Thresholds baseados em Core Web Vitals
        self.vitals_thresholds = {
            'lcp': {'good': 2500, 'poor': 4000},  # ms
            'fid': {'good': 100, 'poor': 300},    # ms
            'inp': {'good': 200, 'poor': 500},    # ms (novo CWV desde 2024)
            'cls': {'good': 0.1, 'poor': 0.25},   # score
            'ttfb': {'good': 800, 'poor': 1800},  # ms
            'fcp': {'good': 1800, 'poor': 3000}   # ms
        }
    
    def analyze_web_vitals_batch(self, confirmed_prospects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analisa Web Vitals para lista de prospects confirmados
        """
        
        logger.info("Iniciando análise Web Vitals para %d prospects", len(confirmed_prospects))
        
        analyzed_prospects = []
        
        for i, prospect in enumerate(confirmed_prospects, 1):
            logger.info("Analisando %d/%d: %s", i, len(confirmed_prospects), 
                       prospect.get('company_name', 'Unknown'))
            
            # Rate limiting para PSI API
            if i > 1:
                time.sleep(1)
            
            try:
                # Análise completa de Web Vitals + pain signals
                web_analysis = self._analyze_prospect_website(prospect)
                
                # Mapear pain signals para sprints
                sprint_recommendations = self._map_pain_to_sprints(web_analysis['pain_signals'])
                
                # Adicionar dados de análise
                prospect['web_analysis'] = web_analysis
                prospect['sprint_recommendations'] = sprint_recommendations
                prospect['total_opportunity_value_usd'] = sum(s['price_usd'] for s in sprint_recommendations)
                prospect['analyzed_at'] = datetime.now().isoformat()
                
                analyzed_prospects.append(prospect)
                
                logger.info("✅ Analisado: %s (Opportunity: $%d)", 
                           prospect['company_name'], prospect['total_opportunity_value_usd'])
                
            except Exception as e:
                logger.error("Erro analisando %s: %s", prospect.get('company_name'), e)
                # Adicionar prospect mesmo com erro, mas marcado
                prospect['web_analysis'] = {'error': str(e), 'analyzed': False}
                prospect['sprint_recommendations'] = []
                prospect['total_opportunity_value_usd'] = 0
                analyzed_prospects.append(prospect)
        
        logger.info("Análise Web Vitals concluída: %d prospects processados", len(analyzed_prospects))
        return analyzed_prospects
    
    def _analyze_prospect_website(self, prospect: Dict[str, Any]) -> Dict[str, Any]:
        """
        Análise completa de website: Web Vitals + pain signals técnicos
        """
        
        website = prospect.get('website') or prospect.get('inferred_website')
        if not website:
            return {
                'error': 'No website found',
                'analyzed': False,
                'pain_signals': []
            }
        
        # Normalizar URL
        if not website.startswith('http'):
            website = f"https://{website}"
        
        analysis = {
            'website_url': website,
            'analyzed': True,
            'timestamp': datetime.now().isoformat()
        }
        
        # 1. PageSpeed Insights (Mobile + Desktop)
        psi_mobile = self._get_pagespeed_insights(website, strategy='mobile')
        psi_desktop = self._get_pagespeed_insights(website, strategy='desktop')
        
        analysis['psi_mobile'] = psi_mobile
        analysis['psi_desktop'] = psi_desktop
        
        # 2. Análise de Web Vitals
        vitals_analysis = self._analyze_core_web_vitals(psi_mobile, psi_desktop)
        analysis['web_vitals'] = vitals_analysis
        
        # 3. Análise técnica adicional
        tech_analysis = self._analyze_technical_stack(website)
        analysis['technical_stack'] = tech_analysis
        
        # 4. Identificar pain signals
        pain_signals = self._identify_pain_signals(vitals_analysis, tech_analysis, website)
        analysis['pain_signals'] = pain_signals
        
        # 5. Score de oportunidade
        analysis['opportunity_score'] = self._calculate_opportunity_score(pain_signals, vitals_analysis)
        
        return analysis
    
    def _get_pagespeed_insights(self, url: str, strategy: str = 'mobile') -> Dict[str, Any]:
        """
        Busca dados PageSpeed Insights
        """
        
        try:
            params = {
                'url': url,
                'key': self.api_key,
                'strategy': strategy,
                'category': 'performance',
                'fields': 'lighthouseResult,loadingExperience,id'
            }
            
            response = requests.get(self.psi_base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'data': data,
                    'strategy': strategy
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}",
                    'strategy': strategy
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'strategy': strategy
            }
    
    def _analyze_core_web_vitals(self, psi_mobile: Dict, psi_desktop: Dict) -> Dict[str, Any]:
        """
        Extrai e analisa Core Web Vitals de PSI data
        """
        
        vitals = {}
        
        for device, psi_data in [('mobile', psi_mobile), ('desktop', psi_desktop)]:
            vitals[device] = {}
            
            if not psi_data.get('success'):
                vitals[device]['error'] = psi_data.get('error', 'Unknown error')
                continue
            
            # CrUX (Real User Metrics) - preferido
            loading_exp = psi_data.get('data', {}).get('loadingExperience', {})
            if loading_exp.get('metrics'):
                crux_metrics = loading_exp['metrics']
                vitals[device]['crux'] = self._extract_crux_metrics(crux_metrics)
            
            # Lab Data (Lighthouse) - fallback
            lighthouse = psi_data.get('data', {}).get('lighthouseResult', {})
            if lighthouse.get('audits'):
                lab_metrics = lighthouse['audits']
                vitals[device]['lab'] = self._extract_lab_metrics(lab_metrics)
            
            # Performance Score
            if lighthouse.get('categories', {}).get('performance'):
                vitals[device]['performance_score'] = lighthouse['categories']['performance']['score'] * 100
        
        return vitals
    
    def _extract_crux_metrics(self, crux_metrics: Dict) -> Dict[str, Any]:
        """
        Extrai métricas CrUX (dados reais de usuários)
        """
        
        metrics = {}
        
        # Mapear métricas CrUX
        crux_mapping = {
            'LARGEST_CONTENTFUL_PAINT_MS': 'lcp',
            'FIRST_INPUT_DELAY_MS': 'fid',
            'INTERACTION_TO_NEXT_PAINT': 'inp',  # Novo CWV 2024
            'CUMULATIVE_LAYOUT_SHIFT_SCORE': 'cls',
            'FIRST_CONTENTFUL_PAINT_MS': 'fcp'
        }
        
        for crux_key, metric_key in crux_mapping.items():
            if crux_key in crux_metrics:
                metric_data = crux_metrics[crux_key]
                p75_value = metric_data.get('percentile', 0)
                
                metrics[metric_key] = {
                    'p75_value': p75_value,
                    'category': self._categorize_metric(metric_key, p75_value),
                    'percentiles': metric_data.get('distributions', [])
                }
        
        return metrics
    
    def _extract_lab_metrics(self, lab_audits: Dict) -> Dict[str, Any]:
        """
        Extrai métricas Lab (Lighthouse) como fallback
        """
        
        metrics = {}
        
        # Mapear audits Lighthouse
        lab_mapping = {
            'largest-contentful-paint': 'lcp',
            'max-potential-fid': 'fid',
            'cumulative-layout-shift': 'cls',
            'first-contentful-paint': 'fcp',
            'total-blocking-time': 'tbt'
        }
        
        for audit_key, metric_key in lab_mapping.items():
            if audit_key in lab_audits:
                audit_data = lab_audits[audit_key]
                value = audit_data.get('numericValue', 0)
                
                metrics[metric_key] = {
                    'value': value,
                    'category': self._categorize_metric(metric_key, value),
                    'score': audit_data.get('score', 0),
                    'display_value': audit_data.get('displayValue', '')
                }
        
        return metrics
    
    def _categorize_metric(self, metric_key: str, value: float) -> str:
        """
        Categoriza métrica como good/needs-improvement/poor
        """
        
        if metric_key not in self.vitals_thresholds:
            return 'unknown'
        
        thresholds = self.vitals_thresholds[metric_key]
        
        if value <= thresholds['good']:
            return 'good'
        elif value <= thresholds['poor']:
            return 'needs-improvement'
        else:
            return 'poor'
    
    def _analyze_technical_stack(self, website: str) -> Dict[str, Any]:
        """
        Análise básica de stack técnico
        """
        
        tech_analysis = {
            'analyzed': True,
            'issues': []
        }
        
        try:
            # HEAD request para headers
            response = requests.head(website, timeout=10, allow_redirects=True)
            
            # Verificar HTTPS
            if not response.url.startswith('https://'):
                tech_analysis['issues'].append('no_ssl')
            
            # Verificar headers de performance
            headers = response.headers
            
            if 'cache-control' not in headers:
                tech_analysis['issues'].append('no_cache_headers')
            
            if 'content-encoding' not in headers:
                tech_analysis['issues'].append('no_compression')
            
            # Server info
            tech_analysis['server'] = headers.get('server', 'unknown')
            tech_analysis['final_url'] = response.url
            
        except Exception as e:
            tech_analysis['error'] = str(e)
            tech_analysis['analyzed'] = False
        
        return tech_analysis
    
    def _identify_pain_signals(self, vitals_analysis: Dict, tech_analysis: Dict, website: str) -> List[Dict[str, Any]]:
        """
        Identifica pain signals específicos baseados na análise
        """
        
        pain_signals = []
        
        # Verificar Web Vitals mobile (prioridade)
        mobile_vitals = vitals_analysis.get('mobile', {})
        
        # CrUX metrics (dados reais) têm prioridade
        crux_data = mobile_vitals.get('crux', {})
        lab_data = mobile_vitals.get('lab', {})
        
        # LCP Poor
        lcp_data = crux_data.get('lcp') or lab_data.get('lcp')
        if lcp_data and lcp_data.get('category') == 'poor':
            pain_signals.append({
                'type': 'poor_lcp',
                'description': f"LCP {lcp_data.get('p75_value', lcp_data.get('value', 0))/1000:.1f}s > 4.0s threshold",
                'severity': 'high',
                'sprint_trigger': 'web_vitals_patch',
                'evidence': f"Core Web Vital failure - mobile LCP",
                'potential_impact': 'High bounce rate, poor SEO ranking'
            })
        
        # INP Poor (novo CWV 2024)
        inp_data = crux_data.get('inp')
        if inp_data and inp_data.get('category') == 'poor':
            pain_signals.append({
                'type': 'poor_inp',
                'description': f"INP {inp_data.get('p75_value', 0)}ms > 500ms threshold",
                'severity': 'high',
                'sprint_trigger': 'web_vitals_patch',
                'evidence': f"New Core Web Vital (2024) failure - mobile INP",
                'potential_impact': 'Poor user interaction experience'
            })
        
        # CLS Poor
        cls_data = crux_data.get('cls') or lab_data.get('cls')
        if cls_data and cls_data.get('category') == 'poor':
            pain_signals.append({
                'type': 'poor_cls',
                'description': f"CLS {cls_data.get('p75_value', cls_data.get('value', 0)):.3f} > 0.25 threshold",
                'severity': 'medium',
                'sprint_trigger': 'web_vitals_patch',
                'evidence': f"Layout shift issues affecting UX",
                'potential_impact': 'Accidental clicks, poor UX'
            })
        
        # Performance Score baixo
        perf_score = mobile_vitals.get('performance_score', 100)
        if perf_score < 50:
            pain_signals.append({
                'type': 'poor_mobile_ux',
                'description': f"Mobile performance score {perf_score}/100",
                'severity': 'high',
                'sprint_trigger': 'cro_express',
                'evidence': f"Lighthouse mobile performance score",
                'potential_impact': 'Poor mobile conversion rates'
            })
        
        # Issues técnicos
        tech_issues = tech_analysis.get('issues', [])
        if 'no_ssl' in tech_issues:
            pain_signals.append({
                'type': 'no_ssl',
                'description': "Website not using HTTPS",
                'severity': 'critical',
                'sprint_trigger': 'cro_express',
                'evidence': f"HTTP instead of HTTPS: {website}",
                'potential_impact': 'Security warnings, SEO penalty'
            })
        
        return pain_signals
    
    def _calculate_opportunity_score(self, pain_signals: List[Dict], vitals_analysis: Dict) -> float:
        """
        Calcula score de oportunidade baseado em pain signals
        """
        
        score = 0.0
        
        # Score baseado em severity
        for signal in pain_signals:
            severity = signal.get('severity', 'low')
            if severity == 'critical':
                score += 30
            elif severity == 'high':
                score += 20
            elif severity == 'medium':
                score += 10
            else:
                score += 5
        
        # Boost se múltiplos Core Web Vitals ruins
        cwv_issues = len([s for s in pain_signals if s.get('type', '').startswith('poor_')])
        if cwv_issues >= 2:
            score += 20
        
        # Boost se performance score muito baixo
        mobile_score = vitals_analysis.get('mobile', {}).get('performance_score', 100)
        if mobile_score < 30:
            score += 25
        
        return min(100.0, score)
    
    def _map_pain_to_sprints(self, pain_signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Mapeia pain signals para sprints específicos
        """
        
        recommended_sprints = set()
        
        # Mapear cada pain signal para sprint
        for signal in pain_signals:
            sprint_trigger = signal.get('sprint_trigger')
            if sprint_trigger and sprint_trigger in self.sprint_mapping:
                recommended_sprints.add(sprint_trigger)
        
        # Converter para lista com detalhes
        sprint_recommendations = []
        for sprint_key in recommended_sprints:
            sprint_info = self.sprint_mapping[sprint_key].copy()
            sprint_info['sprint_key'] = sprint_key
            
            # Adicionar pain signals relacionados
            related_signals = [s for s in pain_signals 
                             if s.get('sprint_trigger') == sprint_key]
            sprint_info['related_pain_signals'] = related_signals
            sprint_info['pain_count'] = len(related_signals)
            
            sprint_recommendations.append(sprint_info)
        
        # Ordenar por prioridade (mais pain signals primeiro)
        sprint_recommendations.sort(key=lambda x: x['pain_count'], reverse=True)
        
        return sprint_recommendations
    
    def save_vitals_analysis(self, analyzed_prospects: List[Dict[str, Any]], 
                           source_info: Dict[str, Any] = None) -> str:
        """
        Salva resultados da análise de Web Vitals
        """
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"data/analyzed/web_vitals_analysis_{timestamp}.json"
        
        os.makedirs('data/analyzed', exist_ok=True)
        
        # Estatísticas
        stats = self._generate_vitals_statistics(analyzed_prospects)
        
        save_data = {
            'analysis_metadata': {
                'timestamp': datetime.now().isoformat(),
                'engine': 'web_vitals_v1.0',
                'total_analyzed': len(analyzed_prospects),
                'source_info': source_info
            },
            'statistics': stats,
            'analyzed_prospects': analyzed_prospects
        }
        
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2, default=str)
        
        logger.info("Web Vitals analysis salvos: %s", filename)
        return filename
    
    def _generate_vitals_statistics(self, prospects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Gera estatísticas da análise de Web Vitals
        """
        
        if not prospects:
            return {}
        
        total_prospects = len(prospects)
        successful_analyses = len([p for p in prospects if p.get('web_analysis', {}).get('analyzed')])
        
        # Distribuição de pain signals
        pain_distribution = {}
        sprint_distribution = {}
        opportunity_values = []
        
        for prospect in prospects:
            pain_signals = prospect.get('web_analysis', {}).get('pain_signals', [])
            sprints = prospect.get('sprint_recommendations', [])
            opportunity = prospect.get('total_opportunity_value_usd', 0)
            
            for signal in pain_signals:
                signal_type = signal.get('type', 'unknown')
                pain_distribution[signal_type] = pain_distribution.get(signal_type, 0) + 1
            
            for sprint in sprints:
                sprint_key = sprint.get('sprint_key', 'unknown')
                sprint_distribution[sprint_key] = sprint_distribution.get(sprint_key, 0) + 1
            
            if opportunity > 0:
                opportunity_values.append(opportunity)
        
        return {
            'analysis_success_rate': successful_analyses / total_prospects if total_prospects > 0 else 0,
            'pain_signal_distribution': pain_distribution,
            'sprint_distribution': sprint_distribution,
            'opportunity_analysis': {
                'total_prospects_with_opportunity': len(opportunity_values),
                'total_opportunity_value_usd': sum(opportunity_values),
                'avg_opportunity_per_prospect': sum(opportunity_values) / len(opportunity_values) if opportunity_values else 0,
                'max_opportunity': max(opportunity_values) if opportunity_values else 0
            }
        }

def main():
    """Teste do Web Vitals Engine"""
    
    print("ARCO Web Vitals Engine")
    print("=" * 40)
    
    # Configuração
    api_key = os.getenv('GOOGLE_PSI_API_KEY')
    if not api_key:
        print("ERRO: GOOGLE_PSI_API_KEY não configurada")
        return
    
    engine = WebVitalsEngine(api_key)
    
    # Prospects de teste (simulando confirmados)
    test_prospects = [
        {
            'company_name': 'Sydney Dental Clinic',
            'website': 'https://example.com',  # Site teste
            'ad_confirmation': {'is_active': True, 'confidence_score': 0.8}
        }
    ]
    
    # Analisar Web Vitals
    try:
        analyzed = engine.analyze_web_vitals_batch(test_prospects)
        
        print(f"Análise concluída: {len(analyzed)} prospects")
        
        for prospect in analyzed:
            print(f"\n{prospect['company_name']}:")
            
            web_analysis = prospect.get('web_analysis', {})
            if web_analysis.get('analyzed'):
                pain_signals = web_analysis.get('pain_signals', [])
                sprints = prospect.get('sprint_recommendations', [])
                
                print(f"  Pain signals: {len(pain_signals)}")
                print(f"  Sprints recomendados: {len(sprints)}")
                print(f"  Opportunity value: ${prospect.get('total_opportunity_value_usd', 0)}")
                
                if pain_signals:
                    print("  Top pain signal:", pain_signals[0].get('description', 'N/A'))
                
                if sprints:
                    print("  Top sprint:", sprints[0].get('description', 'N/A'))
            else:
                print(f"  Erro: {web_analysis.get('error', 'Unknown')}")
        
        # Salvar resultados
        if analyzed:
            output_file = engine.save_vitals_analysis(analyzed, {
                'source': 'test_run',
                'prospects_tested': len(test_prospects)
            })
            print(f"\nResultados salvos: {output_file}")
            
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()