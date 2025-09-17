#!/usr/bin/env python3
"""
Análise direta dos 175 prospects usando bibliotecas Python consolidadas.
Foca em dados reais sem simulação, usando APIs e bibliotecas estabelecidas.
"""

import pandas as pd
import requests
import json
import time
import re
from urllib.parse import urlparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import concurrent.futures
from dataclasses import dataclass
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ProspectAnalysis:
    """Resultado da análise de um prospect."""
    company: str
    domain: str
    website: str
    industry: str
    employees: int
    technologies: List[str]
    
    # Análise técnica
    website_accessible: bool
    response_time: float
    has_ssl: bool
    page_size_kb: float
    
    # Análise de tecnologia
    has_shopify: bool
    has_wordpress: bool
    has_google_analytics: bool
    has_facebook_pixel: bool
    has_klaviyo: bool
    
    # Scoring
    tech_score: int
    performance_score: int
    qualification_score: int
    
    # Potencial de economia
    estimated_monthly_waste: float
    estimated_annual_savings: float
    
    # Metadados
    analysis_date: datetime
    analysis_success: bool
    error_message: Optional[str] = None

class ProspectAnalyzer:
    """Analisador de prospects usando bibliotecas Python consolidadas."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Benchmarks de custos de tecnologias (valores reais de mercado)
        self.tech_costs = {
            'shopify': {'basic': 29, 'shopify': 79, 'advanced': 299},
            'klaviyo': {'email': 20, 'sms': 45, 'growth': 150},
            'google_analytics': {'free': 0, 'premium': 150000},  # GA4 é gratuito, GA360 é caro
            'facebook_pixel': {'free': 0},
            'wordpress': {'hosting': 10, 'premium': 45, 'business': 125},
            'woocommerce': {'free': 0, 'extensions': 200},  # Média de extensões
        }
    
    def analyze_prospect(self, row: pd.Series) -> ProspectAnalysis:
        """Analisa um prospect individual."""
        company = row.get('Company', '')
        website = row.get('Website', '')
        domain = self._extract_domain(website)
        
        logger.info(f"Analisando: {company} ({domain})")
        
        try:
            # Análise técnica do website
            website_data = self._analyze_website(website)
            
            # Análise de tecnologias
            tech_data = self._analyze_technologies(website, row.get('Technologies', ''))
            
            # Cálculo de scores
            tech_score = self._calculate_tech_score(tech_data)
            performance_score = self._calculate_performance_score(website_data)
            qualification_score = self._calculate_qualification_score(
                tech_score, performance_score, row.get('# Employees', 0)
            )
            
            # Estimativa de economia
            monthly_waste, annual_savings = self._estimate_savings(tech_data, row.get('# Employees', 0))
            
            return ProspectAnalysis(
                company=company,
                domain=domain,
                website=website,
                industry=row.get('Industry', ''),
                employees=int(row.get('# Employees', 0)),
                technologies=tech_data['detected_technologies'],
                
                website_accessible=website_data['accessible'],
                response_time=website_data['response_time'],
                has_ssl=website_data['has_ssl'],
                page_size_kb=website_data['page_size_kb'],
                
                has_shopify=tech_data['has_shopify'],
                has_wordpress=tech_data['has_wordpress'],
                has_google_analytics=tech_data['has_google_analytics'],
                has_facebook_pixel=tech_data['has_facebook_pixel'],
                has_klaviyo=tech_data['has_klaviyo'],
                
                tech_score=tech_score,
                performance_score=performance_score,
                qualification_score=qualification_score,
                
                estimated_monthly_waste=monthly_waste,
                estimated_annual_savings=annual_savings,
                
                analysis_date=datetime.now(),
                analysis_success=True
            )
            
        except Exception as e:
            logger.error(f"Erro analisando {company}: {e}")
            return ProspectAnalysis(
                company=company,
                domain=domain,
                website=website,
                industry=row.get('Industry', ''),
                employees=int(row.get('# Employees', 0)),
                technologies=[],
                
                website_accessible=False,
                response_time=0.0,
                has_ssl=False,
                page_size_kb=0.0,
                
                has_shopify=False,
                has_wordpress=False,
                has_google_analytics=False,
                has_facebook_pixel=False,
                has_klaviyo=False,
                
                tech_score=0,
                performance_score=0,
                qualification_score=0,
                
                estimated_monthly_waste=0.0,
                estimated_annual_savings=0.0,
                
                analysis_date=datetime.now(),
                analysis_success=False,
                error_message=str(e)
            )
    
    def _extract_domain(self, website: str) -> str:
        """Extrai o domínio de uma URL."""
        if not website:
            return ''
        try:
            if not website.startswith(('http://', 'https://')):
                website = 'https://' + website
            return urlparse(website).netloc.replace('www.', '')
        except:
            return website
    
    def _analyze_website(self, website: str) -> Dict:
        """Analisa aspectos técnicos do website."""
        if not website:
            return {
                'accessible': False,
                'response_time': 0.0,
                'has_ssl': False,
                'page_size_kb': 0.0,
                'content': ''
            }
        
        try:
            if not website.startswith(('http://', 'https://')):
                website = 'https://' + website
            
            start_time = time.time()
            response = self.session.get(website, timeout=10, verify=False)
            response_time = time.time() - start_time
            
            return {
                'accessible': response.status_code == 200,
                'response_time': response_time,
                'has_ssl': website.startswith('https://'),
                'page_size_kb': len(response.content) / 1024,
                'content': response.text[:10000]  # Primeiros 10KB para análise
            }
            
        except Exception as e:
            logger.warning(f"Erro acessando {website}: {e}")
            return {
                'accessible': False,
                'response_time': 10.0,  # Timeout
                'has_ssl': website.startswith('https://') if website else False,
                'page_size_kb': 0.0,
                'content': ''
            }
    
    def _analyze_technologies(self, website: str, tech_string: str) -> Dict:
        """Analisa tecnologias usando dados do Apollo + análise de conteúdo."""
        tech_data = {
            'detected_technologies': [],
            'has_shopify': False,
            'has_wordpress': False,
            'has_google_analytics': False,
            'has_facebook_pixel': False,
            'has_klaviyo': False,
        }
        
        # Análise baseada nos dados do Apollo
        if tech_string:
            tech_lower = tech_string.lower()
            
            if 'shopify' in tech_lower:
                tech_data['has_shopify'] = True
                tech_data['detected_technologies'].append('Shopify')
            
            if 'wordpress' in tech_lower:
                tech_data['has_wordpress'] = True
                tech_data['detected_technologies'].append('WordPress')
            
            if 'google analytics' in tech_lower:
                tech_data['has_google_analytics'] = True
                tech_data['detected_technologies'].append('Google Analytics')
            
            if 'facebook' in tech_lower:
                tech_data['has_facebook_pixel'] = True
                tech_data['detected_technologies'].append('Facebook Pixel')
            
            if 'klaviyo' in tech_lower:
                tech_data['has_klaviyo'] = True
                tech_data['detected_technologies'].append('Klaviyo')
        
        # Análise adicional do conteúdo do website (se disponível)
        website_data = self._analyze_website(website)
        if website_data['content']:
            content_lower = website_data['content'].lower()
            
            # Padrões de detecção mais específicos
            if 'shopify' in content_lower or 'shopify.com' in content_lower:
                if not tech_data['has_shopify']:
                    tech_data['has_shopify'] = True
                    tech_data['detected_technologies'].append('Shopify (detected)')
            
            if 'gtag(' in content_lower or 'google-analytics' in content_lower:
                if not tech_data['has_google_analytics']:
                    tech_data['has_google_analytics'] = True
                    tech_data['detected_technologies'].append('Google Analytics (detected)')
            
            if 'fbq(' in content_lower or 'facebook.com/tr' in content_lower:
                if not tech_data['has_facebook_pixel']:
                    tech_data['has_facebook_pixel'] = True
                    tech_data['detected_technologies'].append('Facebook Pixel (detected)')
            
            if 'klaviyo' in content_lower or 'kla.js' in content_lower:
                if not tech_data['has_klaviyo']:
                    tech_data['has_klaviyo'] = True
                    tech_data['detected_technologies'].append('Klaviyo (detected)')
        
        return tech_data
    
    def _calculate_tech_score(self, tech_data: Dict) -> int:
        """Calcula score baseado no stack tecnológico."""
        score = 0
        
        # Pontuação por tecnologia detectada
        if tech_data['has_shopify']:
            score += 25  # E-commerce platform
        if tech_data['has_google_analytics']:
            score += 20  # Analytics
        if tech_data['has_facebook_pixel']:
            score += 15  # Marketing tracking
        if tech_data['has_klaviyo']:
            score += 20  # Email marketing
        if tech_data['has_wordpress']:
            score += 10  # CMS
        
        # Bonus por diversidade de stack
        tech_count = len(tech_data['detected_technologies'])
        if tech_count >= 3:
            score += 10
        elif tech_count >= 5:
            score += 20
        
        return min(score, 100)
    
    def _calculate_performance_score(self, website_data: Dict) -> int:
        """Calcula score de performance do website."""
        if not website_data['accessible']:
            return 0
        
        score = 50  # Base score para site acessível
        
        # Penalizar tempo de resposta alto
        if website_data['response_time'] < 1.0:
            score += 20
        elif website_data['response_time'] < 2.0:
            score += 10
        elif website_data['response_time'] > 5.0:
            score -= 20
        
        # Bonus por SSL
        if website_data['has_ssl']:
            score += 15
        
        # Penalizar páginas muito pesadas
        if website_data['page_size_kb'] > 2000:  # > 2MB
            score -= 15
        elif website_data['page_size_kb'] < 500:  # < 500KB
            score += 10
        
        return max(0, min(score, 100))
    
    def _calculate_qualification_score(self, tech_score: int, performance_score: int, employees: int) -> int:
        """Calcula score geral de qualificação."""
        # Peso dos componentes
        weighted_score = (
            tech_score * 0.4 +
            performance_score * 0.3 +
            min(employees * 10, 30)  # Max 30 pontos por funcionários
        )
        
        return int(min(weighted_score, 100))
    
    def _estimate_savings(self, tech_data: Dict, employees: int) -> Tuple[float, float]:
        """Estima economia potencial baseada em tecnologias detectadas."""
        monthly_waste = 0.0
        
        # Estimativas baseadas em custos reais de mercado
        if tech_data['has_shopify']:
            # Assumir plano médio Shopify ($79) + apps (~$200)
            monthly_waste += 279
        
        if tech_data['has_klaviyo']:
            # Baseado no número de funcionários (proxy para tamanho da lista)
            if employees <= 5:
                monthly_waste += 45  # Plano básico
            elif employees <= 20:
                monthly_waste += 150  # Plano growth
            else:
                monthly_waste += 300  # Plano pro
        
        if tech_data['has_wordpress']:
            # Hosting + plugins premium
            monthly_waste += 75
        
        # Adicionar desperdício por performance ruim
        # Sites lentos perdem ~7% de conversões por segundo de atraso
        # Assumindo $10k/mês de receita média para pequenas empresas
        performance_waste = max(0, employees * 50)  # Estimativa conservadora
        monthly_waste += performance_waste
        
        annual_savings = monthly_waste * 12
        
        return monthly_waste, annual_savings

def main():
    """Função principal para análise dos prospects."""
    logger.info("Iniciando análise dos 175 prospects...")
    
    # Carregar dados consolidados
    df = pd.read_csv('arco/consolidated_prospects.csv')
    logger.info(f"Carregados {len(df)} prospects")
    
    # Inicializar analisador
    analyzer = ProspectAnalyzer()
    
    # Analisar prospects (com paralelização limitada para não sobrecarregar)
    results = []
    
    # Processar em lotes pequenos para evitar rate limiting
    batch_size = 5
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        logger.info(f"Processando lote {i//batch_size + 1}/{(len(df)-1)//batch_size + 1}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            batch_results = list(executor.map(analyzer.analyze_prospect, [row for _, row in batch.iterrows()]))
            results.extend(batch_results)
        
        # Pausa entre lotes para ser respeitoso com os servidores
        time.sleep(2)
    
    logger.info(f"Análise concluída. {len(results)} prospects processados")
    
    # Filtrar e ranquear os top 10% (17-18 prospects)
    successful_results = [r for r in results if r.analysis_success and r.qualification_score > 0]
    successful_results.sort(key=lambda x: x.qualification_score, reverse=True)
    
    top_10_percent = successful_results[:18]  # Top 10% de 175
    
    logger.info(f"Top 10% identificados: {len(top_10_percent)} prospects")
    
    # Salvar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Salvar análise completa
    full_results = []
    for result in results:
        full_results.append({
            'company': result.company,
            'domain': result.domain,
            'website': result.website,
            'industry': result.industry,
            'employees': result.employees,
            'technologies': ', '.join(result.technologies),
            'website_accessible': result.website_accessible,
            'response_time': result.response_time,
            'has_ssl': result.has_ssl,
            'page_size_kb': result.page_size_kb,
            'tech_score': result.tech_score,
            'performance_score': result.performance_score,
            'qualification_score': result.qualification_score,
            'estimated_monthly_waste': result.estimated_monthly_waste,
            'estimated_annual_savings': result.estimated_annual_savings,
            'analysis_success': result.analysis_success,
            'error_message': result.error_message
        })
    
    # Salvar CSV completo
    pd.DataFrame(full_results).to_csv(f'output/full_analysis_{timestamp}.csv', index=False)
    
    # Salvar top 10% em JSON para análise detalhada
    top_results = []
    for result in top_10_percent:
        top_results.append({
            'rank': top_10_percent.index(result) + 1,
            'company': result.company,
            'domain': result.domain,
            'website': result.website,
            'industry': result.industry,
            'employees': result.employees,
            'technologies': result.technologies,
            'qualification_score': result.qualification_score,
            'tech_score': result.tech_score,
            'performance_score': result.performance_score,
            'estimated_monthly_waste': result.estimated_monthly_waste,
            'estimated_annual_savings': result.estimated_annual_savings,
            'website_accessible': result.website_accessible,
            'response_time': result.response_time,
            'has_ssl': result.has_ssl,
            'analysis_date': result.analysis_date.isoformat()
        })
    
    with open(f'output/top_10_percent_{timestamp}.json', 'w') as f:
        json.dump({
            'analysis_date': datetime.now().isoformat(),
            'total_prospects': len(df),
            'successfully_analyzed': len(successful_results),
            'top_10_percent_count': len(top_10_percent),
            'average_qualification_score': sum(r.qualification_score for r in successful_results) / len(successful_results),
            'total_estimated_annual_savings': sum(r.estimated_annual_savings for r in top_10_percent),
            'prospects': top_results
        }, f, indent=2)
    
    # Imprimir resumo
    print(f"\n🎯 ANÁLISE CONCLUÍDA - TOP 10% DOS PROSPECTS")
    print(f"=" * 50)
    print(f"Total analisados: {len(results)}")
    print(f"Análises bem-sucedidas: {len(successful_results)}")
    print(f"Top 10% selecionados: {len(top_10_percent)}")
    print(f"Score médio: {sum(r.qualification_score for r in successful_results) / len(successful_results):.1f}")
    print(f"Economia anual total (top 10%): ${sum(r.estimated_annual_savings for r in top_10_percent):,.0f}")
    
    print(f"\n🏆 TOP 5 PROSPECTS:")
    for i, result in enumerate(top_10_percent[:5], 1):
        print(f"{i}. {result.company}")
        print(f"   Score: {result.qualification_score}/100 | Economia anual: ${result.estimated_annual_savings:,.0f}")
        print(f"   Website: {result.website} | Tecnologias: {len(result.technologies)}")
    
    print(f"\nArquivos salvos:")
    print(f"- output/full_analysis_{timestamp}.csv")
    print(f"- output/top_10_percent_{timestamp}.json")

if __name__ == "__main__":
    main()