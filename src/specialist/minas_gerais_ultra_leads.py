#!/usr/bin/env python3
"""
🏆 MINAS GERAIS ULTRA-QUALIFIED LEADS GENERATOR
Sistema especializado para identificar 5 leads ultra-qualificados 
em nichos receptivos no estado de Minas Gerais.

Focos principais:
- Empresas de tecnologia em BH
- Contabilidade e consultoria 
- Clínicas e saúde
- Agências de marketing
- E-commerce e varejo
"""

import requests
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

# Configuração
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# APIs
GOOGLE_API_KEY = "AIzaSyDNo6ycjKNYfDBmbFbOLI7kk-A-teppPaE"
GOOGLE_PLACES_URL = "https://maps.googleapis.com/maps/api/place"
PAGESPEED_API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

@dataclass
class MinasGeraisLead:
    """Lead ultra-qualificado de Minas Gerais"""
    place_id: str
    name: str
    business_type: str
    address: str
    phone: Optional[str]
    website: Optional[str]
    rating: Optional[float]
    user_ratings_total: Optional[int]
    
    # Análise técnica
    tech_analysis: Optional[Dict]
    performance_analysis: Optional[Dict]
    saas_opportunities: Optional[Dict]
    
    # Scoring
    qualification_score: int
    opportunity_value_range: str
    priority_level: str
    approach_strategy: str

class MinasGeraisLeadGenerator:
    """Gerador especializado de leads para Minas Gerais"""
    
    def __init__(self):
        self.session = requests.Session()
        
        # Nichos receptivos em MG
        self.target_niches = [
            {
                'query': 'contabilidade escritorio Belo Horizonte MG',
                'business_type': 'accounting',
                'receptivity': 'ALTA',
                'avg_budget': '$3000-8000'
            },
            {
                'query': 'clinica medica dentista Belo Horizonte MG',
                'business_type': 'healthcare', 
                'receptivity': 'ALTA',
                'avg_budget': '$2000-6000'
            },
            {
                'query': 'agencia marketing digital Belo Horizonte MG',
                'business_type': 'marketing',
                'receptivity': 'MÉDIA',
                'avg_budget': '$4000-12000'
            },
            {
                'query': 'empresa tecnologia software Belo Horizonte MG',
                'business_type': 'technology',
                'receptivity': 'ALTA',
                'avg_budget': '$5000-15000'
            },
            {
                'query': 'loja ecommerce varejo Belo Horizonte MG',
                'business_type': 'retail',
                'receptivity': 'MÉDIA',
                'avg_budget': '$3000-10000'
            },
            {
                'query': 'advocacia escritorio juridico Belo Horizonte MG',
                'business_type': 'legal',
                'receptivity': 'ALTA',
                'avg_budget': '$2500-7000'
            },
            {
                'query': 'restaurante cafe padaria Belo Horizonte MG',
                'business_type': 'food',
                'receptivity': 'BAIXA',
                'avg_budget': '$1500-4000'
            }
        ]
    
    def search_businesses_by_niche(self, niche: Dict) -> List[Dict]:
        """Buscar negócios por nicho específico"""
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
            
            if data.get('status') == 'OK':
                results = data.get('results', [])
                logger.info(f"🔍 {niche['business_type']}: {len(results)} negócios encontrados")
                return results
            else:
                logger.warning(f"❌ API Error: {data.get('status')}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Erro na busca: {e}")
            return []
    
    def get_business_details(self, place_id: str) -> Optional[Dict]:
        """Obter detalhes completos do negócio"""
        url = f"{GOOGLE_PLACES_URL}/details/json"
        
        params = {
            'place_id': place_id,
            'key': GOOGLE_API_KEY,
            'fields': 'name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,business_status,types,opening_hours',
            'language': 'pt-BR'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'OK':
                return data.get('result', {})
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro nos detalhes: {e}")
            return None
    
    def analyze_website_tech(self, website: str) -> Optional[Dict]:
        """Analisar tecnologia do site"""
        if not website:
            return None
            
        # Limpar URL
        if not website.startswith(('http://', 'https://')):
            website = f"https://{website}"
        
        try:
            # Análise básica de performance
            perf_url = PAGESPEED_API_URL
            params = {
                'url': website,
                'key': GOOGLE_API_KEY,
                'strategy': 'desktop',
                'category': ['PERFORMANCE', 'SEO']
            }
            
            response = self.session.get(perf_url, params=params, timeout=45)
            response.raise_for_status()
            data = response.json()
            
            # Extrair métricas
            lighthouse = data.get('lighthouseResult', {})
            categories = lighthouse.get('categories', {})
            
            performance_score = categories.get('performance', {}).get('score', 0) * 100
            seo_score = categories.get('seo', {}).get('score', 0) * 100
            
            # Tecnologias detectadas (simplificado)
            tech_stack = {
                'cms': [],
                'analytics': [],
                'ecommerce': [],
                'frameworks': []
            }
            
            # Detectar tecnologias básicas via user agent e scripts
            audits = lighthouse.get('audits', {})
            
            # WordPress detection
            if any('wp-' in str(audit) for audit in audits.values()):
                tech_stack['cms'].append('WordPress')
            
            # Analytics detection
            if any('analytics' in str(audit).lower() for audit in audits.values()):
                tech_stack['analytics'].append('Google Analytics')
                
            return {
                'performance_score': int(performance_score),
                'seo_score': int(seo_score),
                'tech_stack': tech_stack,
                'has_ssl': website.startswith('https://'),
                'analyzed_url': website
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na análise técnica: {e}")
            return None
    
    def detect_saas_opportunities(self, tech_analysis: Dict, business_type: str) -> Dict:
        """Detectar oportunidades de economia em SaaS"""
        opportunities = {
            'potential_savings': 0,
            'recommendations': [],
            'tools_to_replace': []
        }
        
        if not tech_analysis:
            return opportunities
        
        tech_stack = tech_analysis.get('tech_stack', {})
        performance = tech_analysis.get('performance_score', 100)
        
        # WordPress premium plugins detectados (estimativa)
        if 'WordPress' in tech_stack.get('cms', []):
            opportunities['potential_savings'] += 1200  # $100/mês
            opportunities['recommendations'].append('Substituir plugins premium por alternativas gratuitas')
            opportunities['tools_to_replace'].append('WordPress Premium Plugins')
        
        # Analytics ausente = oportunidade
        if not tech_stack.get('analytics'):
            opportunities['potential_savings'] += 600  # Google Analytics setup
            opportunities['recommendations'].append('Implementar Google Analytics para business intelligence')
        
        # Performance baixa = otimização necessária  
        if performance < 70:
            opportunities['potential_savings'] += 800  # Otimização performance
            opportunities['recommendations'].append('Otimização de performance para melhor conversão')
        
        # Tipo de negócio específico
        if business_type in ['accounting', 'legal']:
            opportunities['potential_savings'] += 1500  # Automação específica
            opportunities['recommendations'].append('Automação de processos específicos do setor')
        
        return opportunities
    
    def calculate_qualification_score(self, business: Dict, tech_analysis: Dict, saas_ops: Dict) -> int:
        """Calcular score de qualificação (0-100)"""
        score = 0
        
        # Rating alto = +20 pontos
        rating = business.get('rating', 0) or 0
        if rating >= 4.5:
            score += 20
        elif rating >= 4.0:
            score += 15
        elif rating >= 3.5:
            score += 10
        
        # Reviews = indicador de atividade (+15 pontos)
        reviews = business.get('user_ratings_total', 0) or 0
        if reviews >= 50:
            score += 15
        elif reviews >= 20:
            score += 10
        elif reviews >= 5:
            score += 5
        
        # Website = +15 pontos
        if business.get('website'):
            score += 15
        
        # Telefone = +10 pontos  
        if business.get('formatted_phone_number'):
            score += 10
        
        # Análise técnica bem-sucedida = +20 pontos
        if tech_analysis:
            score += 20
            
            # Performance baixa = mais oportunidade
            perf = tech_analysis.get('performance_score', 100)
            if perf < 60:
                score += 15  # Mais oportunidade
            elif perf < 80:
                score += 10
        
        # SaaS savings = +20 pontos
        if saas_ops and saas_ops.get('potential_savings', 0) > 1000:
            score += 20
        elif saas_ops and saas_ops.get('potential_savings', 0) > 500:
            score += 15
        
        return min(score, 100)
    
    def determine_priority_level(self, score: int, saas_savings: int) -> str:
        """Determinar nível de prioridade"""
        if score >= 70 and saas_savings >= 1500:
            return "🔥 ULTRA HIGH"
        elif score >= 60 and saas_savings >= 1000:
            return "⚡ HIGH"
        elif score >= 45:
            return "📊 MEDIUM"
        else:
            return "📋 LOW"
    
    def generate_approach_strategy(self, business_type: str, saas_ops: Dict, tech_analysis: Dict) -> str:
        """Gerar estratégia de abordagem personalizada"""
        savings = saas_ops.get('potential_savings', 0) if saas_ops else 0
        performance = tech_analysis.get('performance_score', 100) if tech_analysis else 100
        
        if business_type == 'accounting':
            if savings > 1000:
                return f"Economia de R$ {savings*6:,.0f}/ano em ferramentas + automação de processos contábeis"
            else:
                return "Digitalização e automação de processos contábeis para maior eficiência"
        
        elif business_type == 'healthcare':
            if performance < 70:
                return f"Site com performance {performance}/100 está perdendo pacientes + economia de R$ {savings*6:,.0f}/ano"
            else:
                return "Otimização digital para atrair mais pacientes online"
        
        elif business_type == 'marketing':
            return f"Suas próprias ferramentas têm gaps técnicos - economia de R$ {savings*6:,.0f}/ano + performance"
        
        elif business_type == 'technology':
            return f"Análise técnica detectou R$ {savings*6:,.0f}/ano em economia + otimizações críticas"
        
        elif business_type == 'legal':
            return f"Automatização jurídica + economia de R$ {savings*6:,.0f}/ano em ferramentas"
        
        else:
            if savings > 1000:
                return f"Economia imediata de R$ {savings*6:,.0f}/ano + melhorias de performance"
            else:
                return "Otimização digital para aumentar conversões e vendas"
    
    def generate_ultra_qualified_leads(self) -> List[MinasGeraisLead]:
        """Gerar 5 leads ultra-qualificados de Minas Gerais"""
        all_leads = []
        
        logger.info("🎯 INICIANDO BUSCA DE LEADS ULTRA-QUALIFICADOS EM MINAS GERAIS")
        logger.info("=" * 80)
        
        # Buscar em todos os nichos
        for niche in self.target_niches:
            if niche['receptivity'] in ['ALTA', 'MÉDIA']:  # Focar nos mais receptivos
                logger.info(f"\n🔍 Analisando nicho: {niche['business_type']}")
                
                businesses = self.search_businesses_by_niche(niche)
                
                for business in businesses[:3]:  # Top 3 por nicho
                    place_id = business.get('place_id')
                    if not place_id:
                        continue
                    
                    # Detalhes completos
                    details = self.get_business_details(place_id)
                    if not details:
                        continue
                    
                    # Filtrar apenas Minas Gerais
                    address = details.get('formatted_address', '')
                    if not any(city in address for city in ['MG', 'Minas Gerais', 'Belo Horizonte', 'Contagem', 'Uberlândia', 'Juiz de Fora']):
                        continue
                    
                    logger.info(f"   📍 Analisando: {details.get('name', 'Unknown')}")
                    
                    # Análise técnica
                    website = details.get('website')
                    tech_analysis = None
                    if website:
                        logger.info(f"   🔧 Analisando site: {website}")
                        tech_analysis = self.analyze_website_tech(website)
                        time.sleep(2)  # Rate limiting
                    
                    # SaaS opportunities
                    saas_ops = self.detect_saas_opportunities(tech_analysis, niche['business_type'])
                    
                    # Qualification score
                    qual_score = self.calculate_qualification_score(details, tech_analysis, saas_ops)
                    
                    # Apenas leads com score >= 45
                    if qual_score >= 45:
                        priority = self.determine_priority_level(qual_score, saas_ops.get('potential_savings', 0))
                        approach = self.generate_approach_strategy(niche['business_type'], saas_ops, tech_analysis)
                        
                        lead = MinasGeraisLead(
                            place_id=place_id,
                            name=details.get('name', ''),
                            business_type=niche['business_type'],
                            address=address,
                            phone=details.get('formatted_phone_number'),
                            website=website,
                            rating=details.get('rating'),
                            user_ratings_total=details.get('user_ratings_total'),
                            tech_analysis=tech_analysis,
                            performance_analysis=tech_analysis,
                            saas_opportunities=saas_ops,
                            qualification_score=qual_score,
                            opportunity_value_range=niche['avg_budget'],
                            priority_level=priority,
                            approach_strategy=approach
                        )
                        
                        all_leads.append(lead)
                        logger.info(f"   ✅ Lead qualificado! Score: {qual_score}/100 | {priority}")
                    
                    # Rate limiting
                    time.sleep(1)
        
        # Ordenar por score e pegar top 5
        all_leads.sort(key=lambda x: x.qualification_score, reverse=True)
        top_5_leads = all_leads[:5]
        
        logger.info(f"\n🏆 TOP 5 LEADS ULTRA-QUALIFICADOS SELECIONADOS")
        logger.info("=" * 80)
        
        for i, lead in enumerate(top_5_leads, 1):
            logger.info(f"\n{i}. {lead.name}")
            logger.info(f"   Score: {lead.qualification_score}/100 | {lead.priority_level}")
            logger.info(f"   Tipo: {lead.business_type} | Valor: {lead.opportunity_value_range}")
            logger.info(f"   Estratégia: {lead.approach_strategy}")
        
        return top_5_leads
    
    def export_results(self, leads: List[MinasGeraisLead]) -> str:
        """Exportar resultados para arquivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/minas_gerais_ultra_leads_{timestamp}.json"
        
        export_data = {
            'generated_at': datetime.now().isoformat(),
            'total_leads': len(leads),
            'target_state': 'Minas Gerais',
            'methodology': 'ARCO Ultra-Qualified Lead Generation',
            'focus_niches': [niche['business_type'] for niche in self.target_niches if niche['receptivity'] in ['ALTA', 'MÉDIA']],
            'leads': [asdict(lead) for lead in leads],
            'summary': {
                'avg_qualification_score': sum(lead.qualification_score for lead in leads) / len(leads) if leads else 0,
                'total_potential_savings': sum(lead.saas_opportunities.get('potential_savings', 0) for lead in leads if lead.saas_opportunities),
                'priority_distribution': {
                    'ultra_high': len([l for l in leads if 'ULTRA HIGH' in l.priority_level]),
                    'high': len([l for l in leads if 'HIGH' in l.priority_level and 'ULTRA' not in l.priority_level]),
                    'medium': len([l for l in leads if 'MEDIUM' in l.priority_level]),
                    'low': len([l for l in leads if 'LOW' in l.priority_level])
                }
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return filename

def main():
    """Executar geração de leads de Minas Gerais"""
    generator = MinasGeraisLeadGenerator()
    
    try:
        # Gerar leads
        leads = generator.generate_ultra_qualified_leads()
        
        if leads:
            # Exportar resultados
            filename = generator.export_results(leads)
            
            print(f"\n🎉 MISSÃO CUMPRIDA!")
            print(f"✅ {len(leads)} leads ultra-qualificados identificados em Minas Gerais")
            print(f"📁 Resultados salvos em: {filename}")
            
            # Summary executivo
            total_savings = sum(lead.saas_opportunities.get('potential_savings', 0) for lead in leads if lead.saas_opportunities)
            avg_score = sum(lead.qualification_score for lead in leads) / len(leads)
            
            print(f"\n📊 RESUMO EXECUTIVO:")
            print(f"• Score médio de qualificação: {avg_score:.1f}/100")
            print(f"• Economia total potencial: R$ {total_savings*6:,.0f}/ano")
            print(f"• Leads ULTRA HIGH: {len([l for l in leads if 'ULTRA HIGH' in l.priority_level])}")
            print(f"• Leads HIGH: {len([l for l in leads if 'HIGH' in l.priority_level and 'ULTRA' not in l.priority_level])}")
            
        else:
            print("❌ Nenhum lead ultra-qualificado encontrado. Ajustar critérios de busca.")
            
    except Exception as e:
        logger.error(f"❌ Erro na execução: {e}")
        print(f"❌ Erro na execução: {e}")

if __name__ == "__main__":
    main()
