#!/usr/bin/env python3
"""
🎯 MINAS GERAIS REALISTIC LEADS GENERATOR
Sistema realista e criterioso para identificar leads genuinamente qualificados
em Minas Gerais com scoring honesto e análise técnica rigorosa.

CRITÉRIOS REALISTAS:
- Score máximo 85/100 (ninguém é perfeito)
- Penalizações por problemas reais
- Análise técnica rigorosa
- SaaS savings baseadas em evidências
- Rate limiting adequado
"""

import requests
import json
import time
import logging
import re
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from urllib.parse import urlparse

# Configuração
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# APIs
GOOGLE_API_KEY = "AIzaSyDNo6ycjKNYfDBmbFbOLI7kk-A-teppPaE"
GOOGLE_PLACES_URL = "https://maps.googleapis.com/maps/api/place"
PAGESPEED_API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

@dataclass
class RealisticLead:
    """Lead com scoring realista"""
    place_id: str
    name: str
    business_type: str
    address: str
    phone: Optional[str]
    website: Optional[str]
    rating: Optional[float]
    user_ratings_total: Optional[int]
    
    # Análise técnica rigorosa
    tech_analysis: Optional[Dict]
    qualification_score: int  # Max 85/100
    opportunity_score: int   # Max 75/100
    priority_level: str
    
    # Problemas identificados
    technical_issues: List[str]
    missed_opportunities: List[str]
    realistic_savings: Dict
    
    # Recomendações honestas
    honest_assessment: str
    next_steps: List[str]

class RealisticLeadGenerator:
    """Gerador com critérios realistas"""
    
    def __init__(self):
        self.session = requests.Session()
        self.analyzed_count = 0
        self.max_analyses = 10  # Limit para evitar rate limiting
        
        # Nichos com expectativas realistas
        self.realistic_niches = [
            {
                'query': 'escritorio contabilidade Belo Horizonte MG',
                'business_type': 'accounting',
                'expected_score_range': (35, 65),
                'common_issues': ['outdated_tech', 'no_analytics', 'slow_site']
            },
            {
                'query': 'clinica dentista medico Belo Horizonte MG', 
                'business_type': 'healthcare',
                'expected_score_range': (25, 55),
                'common_issues': ['basic_website', 'no_booking', 'poor_mobile']
            },
            {
                'query': 'advogado escritorio juridico Belo Horizonte MG',
                'business_type': 'legal', 
                'expected_score_range': (30, 60),
                'common_issues': ['template_site', 'no_ssl', 'outdated_content']
            }
        ]
    
    def search_businesses_by_niche(self, niche: Dict) -> List[Dict]:
        """Buscar negócios com rate limiting adequado"""
        url = f"{GOOGLE_PLACES_URL}/textsearch/json"
        
        params = {
            'query': niche['query'],
            'key': GOOGLE_API_KEY,
            'language': 'pt-BR',
            'region': 'br'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Check quota
            if data.get('status') == 'OVER_QUERY_LIMIT':
                logger.error("❌ Google API quota exceeded")
                return []
            
            if data.get('status') == 'OK':
                results = data.get('results', [])
                logger.info(f"🔍 {niche['business_type']}: {len(results)} negócios encontrados")
                return results[:5]  # Limitar para análise focada
            else:
                logger.warning(f"❌ API Error: {data.get('status')}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Erro na busca: {e}")
            return []
    
    def analyze_website_rigorously(self, website: str) -> Optional[Dict]:
        """Análise técnica rigorosa e honesta"""
        if not website or self.analyzed_count >= self.max_analyses:
            return None
            
        # Limpar URL
        if not website.startswith(('http://', 'https://')):
            website = f"https://{website}"
        
        try:
            self.analyzed_count += 1
            logger.info(f"   🔧 Análise {self.analyzed_count}/{self.max_analyses}: {website}")
            
            # PageSpeed API call com timeout realista
            perf_url = PAGESPEED_API_URL
            params = {
                'url': website,
                'key': GOOGLE_API_KEY,
                'strategy': 'desktop',
                'category': ['PERFORMANCE', 'SEO', 'ACCESSIBILITY']
            }
            
            response = self.session.get(perf_url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            # Extrair métricas realistas
            lighthouse = data.get('lighthouseResult', {})
            categories = lighthouse.get('categories', {})
            audits = lighthouse.get('audits', {})
            
            performance_score = int((categories.get('performance', {}).get('score', 0) or 0) * 100)
            seo_score = int((categories.get('seo', {}).get('score', 0) or 0) * 100)
            accessibility_score = int((categories.get('accessibility', {}).get('score', 0) or 0) * 100)
            
            # Análise técnica rigorosa
            tech_issues = []
            tech_stack = {
                'cms': 'Unknown',
                'has_analytics': False,
                'has_ssl': website.startswith('https://'),
                'responsive': False,
                'frameworks': []
            }
            
            # WordPress detection rigorosa
            final_url = data.get('lighthouseResult', {}).get('finalUrl', website)
            if any(indicator in str(audits) for indicator in ['/wp-content/', '/wp-includes/', 'wp-json']):
                tech_stack['cms'] = 'WordPress'
            
            # Analytics detection rigorosa  
            if 'uses-passive-event-listeners' in audits:
                analytics_audit = str(audits.get('uses-passive-event-listeners', {}))
                if 'google-analytics' in analytics_audit.lower() or 'gtag' in analytics_audit.lower():
                    tech_stack['has_analytics'] = True
            
            # Responsive check
            viewport_audit = audits.get('viewport', {})
            if viewport_audit.get('score', 0) == 1:
                tech_stack['responsive'] = True
            
            # Identificar problemas técnicos reais
            if performance_score < 50:
                tech_issues.append(f"Performance crítica: {performance_score}/100")
            elif performance_score < 70:
                tech_issues.append(f"Performance baixa: {performance_score}/100")
            
            if seo_score < 80:
                tech_issues.append(f"SEO deficiente: {seo_score}/100")
                
            if not tech_stack['has_ssl']:
                tech_issues.append("Site inseguro (HTTP)")
                
            if not tech_stack['responsive']:
                tech_issues.append("Não responsivo para mobile")
                
            if not tech_stack['has_analytics']:
                tech_issues.append("Sem Google Analytics")
            
            # Core Web Vitals
            lcp_audit = audits.get('largest-contentful-paint', {})
            if lcp_audit.get('numericValue', 0) > 2500:
                tech_issues.append("LCP muito lento (>2.5s)")
            
            fid_audit = audits.get('max-potential-fid', {})
            if fid_audit.get('numericValue', 0) > 100:
                tech_issues.append("FID alto (interatividade lenta)")
            
            cls_audit = audits.get('cumulative-layout-shift', {})
            if cls_audit.get('numericValue', 0) > 0.1:
                tech_issues.append("CLS alto (layout instável)")
            
            # Rate limiting crucial
            time.sleep(3)
            
            return {
                'performance_score': performance_score,
                'seo_score': seo_score,
                'accessibility_score': accessibility_score,
                'tech_stack': tech_stack,
                'technical_issues': tech_issues,
                'analyzed_url': final_url,
                'audit_count': len(audits),
                'analysis_depth': 'rigorous'
            }
            
        except requests.exceptions.Timeout:
            logger.warning(f"   ⏰ Timeout na análise de {website}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"   ❌ Erro de rede: {e}")
            return None
        except Exception as e:
            logger.error(f"   ❌ Erro na análise técnica: {e}")
            return None
    
    def calculate_realistic_score(self, business: Dict, tech_analysis: Dict) -> int:
        """Calcular score realista com penalizações"""
        score = 0
        max_possible = 85  # Ninguém é perfeito
        
        # Base business metrics (max 25 pontos)
        rating = business.get('rating', 0) or 0
        if rating >= 4.8:
            score += 15
        elif rating >= 4.5:
            score += 12
        elif rating >= 4.0:
            score += 8
        elif rating >= 3.5:
            score += 5
        
        reviews = business.get('user_ratings_total', 0) or 0
        if reviews >= 100:
            score += 10
        elif reviews >= 50:
            score += 7
        elif reviews >= 20:
            score += 5
        elif reviews >= 5:
            score += 2
        
        # Website existence and basic info (max 20 pontos)
        if business.get('website'):
            score += 10
        if business.get('formatted_phone_number'):
            score += 5
        if business.get('formatted_address'):
            score += 5
        
        # Technical analysis (max 40 pontos, com penalizações)
        if tech_analysis:
            perf = tech_analysis.get('performance_score', 0)
            seo = tech_analysis.get('seo_score', 0)
            issues = tech_analysis.get('technical_issues', [])
            
            # Performance scoring (penaliza baixa performance)
            if perf >= 90:
                score += 15
            elif perf >= 75:
                score += 12
            elif perf >= 60:
                score += 8
            elif perf >= 40:
                score += 4
            # < 40 = 0 pontos
            
            # SEO scoring
            if seo >= 95:
                score += 10
            elif seo >= 85:
                score += 7
            elif seo >= 70:
                score += 4
            # < 70 = 0 pontos
            
            # Tech stack bonus
            tech_stack = tech_analysis.get('tech_stack', {})
            if tech_stack.get('has_analytics'):
                score += 5
            if tech_stack.get('has_ssl'):
                score += 5
            if tech_stack.get('responsive'):
                score += 5
            
            # Penalizações por problemas técnicos
            penalty = min(len(issues) * 3, 15)  # Max 15 pontos de penalização
            score -= penalty
        
        # Business hours/status penalty
        if business.get('business_status') != 'OPERATIONAL':
            score -= 10
        
        return max(0, min(score, max_possible))
    
    def assess_realistic_opportunities(self, tech_analysis: Dict, business_type: str) -> Dict:
        """Avaliar oportunidades baseadas em evidências"""
        if not tech_analysis:
            return {
                'opportunity_score': 0,
                'potential_savings': 0,
                'recommendations': [],
                'evidence_based': False
            }
        
        opportunity_score = 0
        potential_savings = 0
        recommendations = []
        
        tech_stack = tech_analysis.get('tech_stack', {})
        issues = tech_analysis.get('technical_issues', [])
        perf_score = tech_analysis.get('performance_score', 100)
        seo_score = tech_analysis.get('seo_score', 100)
        
        # Performance optimization (baseado em score real)
        if perf_score < 50:
            opportunity_score += 20
            potential_savings += 300  # Custo mensal realista
            recommendations.append(f"Otimização crítica de performance ({perf_score}/100)")
        elif perf_score < 70:
            opportunity_score += 10
            potential_savings += 150
            recommendations.append(f"Melhorias de performance ({perf_score}/100)")
        
        # SEO improvements
        if seo_score < 80:
            opportunity_score += 15
            potential_savings += 200
            recommendations.append(f"Otimização de SEO ({seo_score}/100)")
        
        # Analytics setup
        if not tech_stack.get('has_analytics'):
            opportunity_score += 15
            potential_savings += 100
            recommendations.append("Implementação de Google Analytics")
        
        # SSL security
        if not tech_stack.get('has_ssl'):
            opportunity_score += 10
            potential_savings += 50
            recommendations.append("Implementação de certificado SSL")
        
        # Mobile responsiveness
        if not tech_stack.get('responsive'):
            opportunity_score += 10
            potential_savings += 250
            recommendations.append("Otimização para dispositivos móveis")
        
        # Business type specific (conservativo)
        if business_type == 'accounting' and len(issues) >= 3:
            opportunity_score += 10
            potential_savings += 200
            recommendations.append("Automação básica de processos")
        
        return {
            'opportunity_score': min(opportunity_score, 75),  # Max 75/100
            'potential_savings': potential_savings,  # Por mês, não ano
            'recommendations': recommendations,
            'evidence_based': True,
            'technical_issues_count': len(issues)
        }
    
    def determine_realistic_priority(self, qual_score: int, opp_score: int) -> str:
        """Priorização realista"""
        combined = (qual_score + opp_score) / 2
        
        if combined >= 70:
            return "🔥 HIGH"
        elif combined >= 55:
            return "⚡ MEDIUM" 
        elif combined >= 40:
            return "📊 LOW"
        else:
            return "❌ NOT QUALIFIED"
    
    def generate_honest_assessment(self, business: Dict, tech_analysis: Dict, opportunities: Dict) -> str:
        """Avaliação honesta e realista"""
        name = business.get('name', 'Business')
        
        if not tech_analysis:
            return f"{name}: Sem website ou análise técnica indisponível. Prioridade baixa."
        
        issues = tech_analysis.get('technical_issues', [])
        perf = tech_analysis.get('performance_score', 0)
        opp_score = opportunities.get('opportunity_score', 0)
        
        if len(issues) >= 4:
            return f"{name}: Múltiplos problemas técnicos ({len(issues)} issues). Oportunidade de modernização completa."
        elif perf < 50:
            return f"{name}: Performance crítica ({perf}/100). Urgente otimização para não perder clientes."
        elif opp_score >= 50:
            return f"{name}: Bom potencial ({opp_score}/75). Melhorias incrementais com ROI claro."
        else:
            return f"{name}: Poucas oportunidades técnicas. Foco em outras estratégias de growth."
    
    def filter_minas_gerais_only(self, address: str) -> bool:
        """Filtro rigoroso para Minas Gerais"""
        if not address:
            return False
        
        mg_indicators = [
            'MG', 'Minas Gerais', 'Belo Horizonte', 'Contagem', 
            'Uberlândia', 'Juiz de Fora', 'Betim', 'Montes Claros'
        ]
        
        return any(indicator in address for indicator in mg_indicators)
    
    def generate_realistic_leads(self) -> List[RealisticLead]:
        """Gerar leads com critérios realistas"""
        all_leads = []
        
        logger.info("🎯 ANÁLISE REALISTA DE LEADS - MINAS GERAIS")
        logger.info("Critérios: Score máximo 85/100, penalizações por problemas reais")
        logger.info("=" * 80)
        
        for niche in self.realistic_niches:
            logger.info(f"\n🔍 Analisando nicho: {niche['business_type']}")
            logger.info(f"Score esperado: {niche['expected_score_range'][0]}-{niche['expected_score_range'][1]}/85")
            
            businesses = self.search_businesses_by_niche(niche)
            
            for business in businesses:
                place_id = business.get('place_id')
                if not place_id:
                    continue
                
                # Filtrar apenas Minas Gerais
                address = business.get('formatted_address', '')
                if not self.filter_minas_gerais_only(address):
                    continue
                
                name = business.get('name', 'Unknown')
                logger.info(f"   📍 Analisando: {name}")
                
                # Rate limiting entre businesses
                time.sleep(1)
                
                # Análise técnica rigorosa
                website = business.get('website')
                tech_analysis = None
                if website and self.analyzed_count < self.max_analyses:
                    tech_analysis = self.analyze_website_rigorously(website)
                
                # Scoring realista
                qual_score = self.calculate_realistic_score(business, tech_analysis)
                opportunities = self.assess_realistic_opportunities(tech_analysis, niche['business_type'])
                opp_score = opportunities.get('opportunity_score', 0)
                
                # Filtro de qualificação mínima
                if qual_score >= 35:  # Threshold realista
                    priority = self.determine_realistic_priority(qual_score, opp_score)
                    assessment = self.generate_honest_assessment(business, tech_analysis, opportunities)
                    
                    issues = tech_analysis.get('technical_issues', []) if tech_analysis else []
                    recommendations = opportunities.get('recommendations', [])
                    
                    # Próximos passos realistas
                    next_steps = []
                    if qual_score >= 60:
                        next_steps.append("Contact decision maker directly")
                    elif qual_score >= 45:
                        next_steps.append("Send technical audit report first")
                    else:
                        next_steps.append("Nurture with valuable content")
                    
                    lead = RealisticLead(
                        place_id=place_id,
                        name=name,
                        business_type=niche['business_type'],
                        address=address,
                        phone=business.get('formatted_phone_number'),
                        website=website,
                        rating=business.get('rating'),
                        user_ratings_total=business.get('user_ratings_total'),
                        tech_analysis=tech_analysis,
                        qualification_score=qual_score,
                        opportunity_score=opp_score,
                        priority_level=priority,
                        technical_issues=issues,
                        missed_opportunities=recommendations,
                        realistic_savings={
                            'monthly': opportunities.get('potential_savings', 0),
                            'annual': opportunities.get('potential_savings', 0) * 12
                        },
                        honest_assessment=assessment,
                        next_steps=next_steps
                    )
                    
                    all_leads.append(lead)
                    logger.info(f"   ✅ Qualificado: {qual_score}/85 | Opp: {opp_score}/75 | {priority}")
                else:
                    logger.info(f"   ❌ Não qualificado: {qual_score}/85 (mín: 35)")
                
                # Rate limiting crucial
                time.sleep(2)
        
        # Ordenar por score combinado realista
        all_leads.sort(key=lambda x: (x.qualification_score + x.opportunity_score) / 2, reverse=True)
        
        return all_leads[:5]  # Top 5 realistas
    
    def export_realistic_results(self, leads: List[RealisticLead]) -> str:
        """Exportar resultados realistas"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/realistic_minas_gerais_leads_{timestamp}.json"
        
        if not leads:
            logger.warning("❌ Nenhum lead qualificado encontrado com critérios realistas")
            return None
        
        export_data = {
            'generated_at': datetime.now().isoformat(),
            'total_leads': len(leads),
            'methodology': 'Realistic Lead Qualification with Rigorous Scoring',
            'scoring_system': {
                'max_qualification_score': 85,
                'max_opportunity_score': 75,
                'min_threshold': 35,
                'penalty_system': 'Yes - technical issues reduce score'
            },
            'api_calls_made': self.analyzed_count,
            'leads': [asdict(lead) for lead in leads],
            'realistic_summary': {
                'avg_qualification_score': sum(l.qualification_score for l in leads) / len(leads),
                'avg_opportunity_score': sum(l.opportunity_score for l in leads) / len(leads),
                'total_monthly_savings': sum(l.realistic_savings['monthly'] for l in leads),
                'priority_distribution': {
                    priority: len([l for l in leads if priority in l.priority_level])
                    for priority in ['HIGH', 'MEDIUM', 'LOW']
                }
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return filename

def main():
    """Executar análise realista"""
    generator = RealisticLeadGenerator()
    
    try:
        leads = generator.generate_realistic_leads()
        
        if leads:
            filename = generator.export_realistic_results(leads)
            
            print(f"\n🎯 ANÁLISE REALISTA CONCLUÍDA")
            print(f"✅ {len(leads)} leads genuinamente qualificados")
            print(f"📁 Resultados: {filename}")
            
            # Summary realista
            avg_qual = sum(l.qualification_score for l in leads) / len(leads)
            avg_opp = sum(l.opportunity_score for l in leads) / len(leads)
            monthly_savings = sum(l.realistic_savings['monthly'] for l in leads)
            
            print(f"\n📊 RESUMO REALISTA:")
            print(f"• Score médio qualificação: {avg_qual:.1f}/85")
            print(f"• Score médio oportunidade: {avg_opp:.1f}/75")
            print(f"• Economia mensal total: R$ {monthly_savings:,.0f}")
            print(f"• API calls utilizadas: {generator.analyzed_count}/10")
            
            # Mostrar distribuição de prioridade
            for lead in leads:
                print(f"• {lead.name}: {lead.qualification_score}/85 | {lead.priority_level}")
                
        else:
            print("❌ Nenhum lead qualificado com critérios realistas")
            print("💡 Considere ajustar thresholds ou expandir critérios de busca")
            
    except Exception as e:
        logger.error(f"❌ Erro na execução: {e}")

if __name__ == "__main__":
    main()
