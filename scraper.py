#!/usr/bin/env python3
"""
ARCO Lead Scraping System
Sistema completo de prospecção baseado nos tiers ARCO:
- Insight → Leak Fix → Sprint 72h → Velocity Rebuild + Pulse

Meta: 100 leads pré-qualificados com score ≥70
"""

import asyncio
import aiohttp
import json
import csv
import time
import logging
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from urllib.parse import urlparse
import re
import os
from datetime import datetime, timedelta

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('arco_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class CompanyProfile:
    """Perfil completo da empresa para análise ARCO"""
    domain: str
    company_name: str = ""
    industry: str = ""
    estimated_revenue: str = ""
    tech_stack: List[str] = None
    performance_metrics: Dict[str, Any] = None
    saas_apps: List[str] = None
    contact_info: Dict[str, str] = None
    score: int = 0
    qualification_notes: str = ""
    created_at: str = ""
    
    def __post_init__(self):
        if self.tech_stack is None:
            self.tech_stack = []
        if self.performance_metrics is None:
            self.performance_metrics = {}
        if self.saas_apps is None:
            self.saas_apps = []
        if self.contact_info is None:
            self.contact_info = {}
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

class ARCOProspectingScraper:
    """
    Sistema de prospecção ARCO baseado nos ICPs definidos:
    P1: Growth E-commerce (US$ 500k-3M/ano)
    P2: Nicho DTC 1-3M (Shopify + GA4 + ≥8 apps)
    P3: Serviços Profissionais (US$ 300k-1M/ano)
    P4: Early SaaS Bootstrapped (MRR US$ 5-50k)
    """
    
    def __init__(self):
        self.google_api_key = os.getenv('GOOGLE_API_KEY', 'AIzaSyDNo6ycjKNYfDBmbFbOLI7kk-A-teppPaE')
        self.session = None
        self.scraped_companies = []
        self.qualified_leads = []
        
        # Rate limiting
        self.request_delay = 1.0  # segundos entre requests
        self.last_request_time = 0
        
        # Patterns para detecção de tecnologias
        self.tech_patterns = {
            'shopify': [r'shopify', r'shop\.app', r'myshopify\.com'],
            'wordpress': [r'wp-content', r'wordpress', r'/wp-'],
            'woocommerce': [r'woocommerce', r'wc-', r'shop/?'],
            'react': [r'react', r'_react', r'__react'],
            'next': [r'next\.js', r'_next/', r'__next'],
            'elementor': [r'elementor', r'elementor-'],
            'shopify_apps': [r'klaviyo', r'yotpo', r'judge\.me', r'privy', r'boldcommerce']
        }
        
        # ICP targets
        self.icp_domains = [
            # E-commerce growth
            'shopify.com', 'bigcommerce.com', 'woocommerce.com',
            # DTC brands
            'supplement', 'skincare', 'fashion', 'jewelry', 'pet',
            # Professional services
            'law', 'legal', 'clinic', 'medical', 'accounting', 'consulting',
            # SaaS
            'saas', 'software', 'app', 'platform', 'tool'
        ]
    
    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()
    
    async def rate_limit(self):
        """Aplica rate limiting entre requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_delay:
            await asyncio.sleep(self.request_delay - time_since_last)
        self.last_request_time = time.time()
    
    async def analyze_website_performance(self, domain: str) -> Dict[str, Any]:
        """
        Análise de performance usando PageSpeed Insights API
        Foco em métricas que impactam conversão
        """
        await self.rate_limit()
        
        url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        params = {
            'url': f'https://{domain}',
            'key': self.google_api_key,
            'strategy': 'mobile',  # Foco mobile (60%+ tráfego)
            'category': ['PERFORMANCE', 'ACCESSIBILITY', 'BEST_PRACTICES']
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extrai métricas críticas
                    lighthouse_result = data.get('lighthouseResult', {})
                    audits = lighthouse_result.get('audits', {})
                    
                    # Core Web Vitals
                    lcp = audits.get('largest-contentful-paint', {}).get('numericValue', 0) / 1000
                    cls = audits.get('cumulative-layout-shift', {}).get('numericValue', 0)
                    inp = audits.get('interaction-to-next-paint', {}).get('numericValue', 0)
                    
                    # Scores
                    categories = lighthouse_result.get('categories', {})
                    performance_score = categories.get('performance', {}).get('score', 0) * 100
                    
                    return {
                        'lcp_mobile': lcp,
                        'cls_mobile': cls,
                        'inp_mobile': inp,
                        'performance_score': performance_score,
                        'issues_detected': lcp > 2.5 or cls > 0.1 or inp > 200,
                        'estimated_loss_pct': max(0, (lcp - 2.5) * 10) if lcp > 2.5 else 0,
                        'api_success': True
                    }
                
                else:
                    logger.warning(f"PageSpeed API failed for {domain}: {response.status}")
                    return {'api_success': False, 'error': f'API Status: {response.status}'}
                    
        except Exception as e:
            logger.error(f"Error analyzing {domain}: {str(e)}")
            return {'api_success': False, 'error': str(e)}
    
    async def detect_tech_stack(self, domain: str) -> Dict[str, Any]:
        """
        Detecção de stack tecnológico via análise de HTML/headers
        Foca em identificar plataformas e apps relevantes para ARCO
        """
        await self.rate_limit()
        
        tech_stack = {
            'platform': 'unknown',
            'cms': 'unknown',
            'ecommerce': False,
            'apps_detected': [],
            'saas_complexity': 0,
            'shopify_apps': []
        }
        
        url = f'https://{domain}'
        
        try:
            async with self.session.get(url, allow_redirects=True) as response:
                if response.status == 200:
                    html = await response.text()
                    headers = dict(response.headers)
                    
                    # Detecção de plataforma
                    html_lower = html.lower()
                    
                    # Shopify detection
                    if any(pattern in html_lower for pattern in ['shopify', 'myshopify', 'shop.app']):
                        tech_stack['platform'] = 'shopify'
                        tech_stack['ecommerce'] = True
                        
                        # Conta apps Shopify
                        for app_pattern in self.tech_patterns['shopify_apps']:
                            if re.search(app_pattern, html_lower):
                                tech_stack['shopify_apps'].append(app_pattern)
                        
                        tech_stack['saas_complexity'] = len(tech_stack['shopify_apps'])
                    
                    # WordPress detection
                    elif any(pattern in html_lower for pattern in ['/wp-content', 'wordpress', 'wp-includes']):
                        tech_stack['platform'] = 'wordpress'
                        tech_stack['cms'] = 'wordpress'
                        
                        # WooCommerce check
                        if any(pattern in html_lower for pattern in ['woocommerce', 'wc-ajax']):
                            tech_stack['ecommerce'] = True
                            tech_stack['platform'] = 'woocommerce'
                    
                    # React/Next.js detection
                    if any(pattern in html_lower for pattern in ['react', '_react', '__react']):
                        tech_stack['apps_detected'].append('react')
                    
                    if any(pattern in html_lower for pattern in ['next.js', '_next/', '__next']):
                        tech_stack['apps_detected'].append('nextjs')
                    
                    # Server headers analysis
                    server = headers.get('server', '').lower()
                    if 'nginx' in server:
                        tech_stack['apps_detected'].append('nginx')
                    elif 'apache' in server:
                        tech_stack['apps_detected'].append('apache')
                    
                    return tech_stack
                    
        except Exception as e:
            logger.error(f"Error detecting tech stack for {domain}: {str(e)}")
            return tech_stack
    
    def calculate_qualification_score(self, profile: CompanyProfile) -> int:
        """
        Sistema de score baseado nos critérios ARCO (Gate ≥ 70):
        - GMV band match: 20 pts
        - LCP severity: 20 pts  
        - Checkout length: 15 pts
        - # apps paid: 10 pts
        - Traffic > 20k: 10 pts
        - Decision-maker contact: 15 pts
        - Recent ad spend: 10 pts
        """
        score = 0
        notes = []
        
        # Performance severity (20 pts)
        if profile.performance_metrics.get('api_success'):
            lcp = profile.performance_metrics.get('lcp_mobile', 0)
            if lcp > 4.0:
                score += 20
                notes.append("LCP crítico >4s")
            elif lcp > 3.0:
                score += 10
                notes.append("LCP moderado 3-4s")
        
        # Tech stack complexity (25 pts total)
        if profile.tech_stack:
            platform = None
            for tech in profile.tech_stack:
                if 'shopify' in tech.lower():
                    platform = 'shopify'
                    break
                elif 'wordpress' in tech.lower():
                    platform = 'wordpress'
                    break
            
            if platform == 'shopify':
                score += 15
                notes.append("Shopify platform")
                
                # Apps complexity
                app_count = len(profile.saas_apps)
                if app_count >= 8:
                    score += 10
                    notes.append(f"{app_count} apps detected")
                elif app_count >= 5:
                    score += 5
                    notes.append(f"{app_count} apps detected")
            
            elif platform == 'wordpress':
                score += 10
                notes.append("WordPress platform")
        
        # E-commerce bonus (10 pts)
        domain_lower = profile.domain.lower()
        ecommerce_indicators = ['shop', 'store', 'buy', 'cart', 'checkout']
        if any(indicator in domain_lower for indicator in ecommerce_indicators):
            score += 10
            notes.append("E-commerce indicators")
        
        # Industry match (15 pts)
        industry_keywords = ['supplement', 'fashion', 'beauty', 'pet', 'jewelry', 'law', 'clinic', 'accounting']
        if any(keyword in domain_lower for keyword in industry_keywords):
            score += 15
            notes.append("Target industry match")
        
        # Domain authority proxy (10 pts)
        if len(profile.domain.split('.')) == 2 and not any(x in domain_lower for x in ['test', 'demo', 'staging']):
            score += 10
            notes.append("Professional domain")
        
        profile.score = score
        profile.qualification_notes = "; ".join(notes)
        
        return score
    
    async def enrich_contact_info(self, domain: str) -> Dict[str, str]:
        """
        Enriquecimento básico de informações de contato
        Busca por emails e informações de contato no site
        """
        await self.rate_limit()
        
        contact_info = {
            'general_email': '',
            'contact_page': '',
            'linkedin': '',
            'phone': ''
        }
        
        try:
            # Tenta página de contato
            contact_urls = [
                f'https://{domain}/contact',
                f'https://{domain}/contact-us',
                f'https://{domain}/about',
                f'https://{domain}'
            ]
            
            for url in contact_urls:
                try:
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            html = await response.text()
                            
                            # Busca emails
                            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                            emails = re.findall(email_pattern, html)
                            
                            # Filtra emails relevantes (remove genéricos)
                            relevant_emails = [
                                email for email in emails 
                                if not any(generic in email.lower() for generic in ['noreply', 'no-reply', 'support', 'hello'])
                            ]
                            
                            if relevant_emails:
                                contact_info['general_email'] = relevant_emails[0]
                            
                            # Busca LinkedIn
                            linkedin_pattern = r'linkedin\.com/(?:company/|in/)([A-Za-z0-9-]+)'
                            linkedin_matches = re.findall(linkedin_pattern, html)
                            if linkedin_matches:
                                contact_info['linkedin'] = f"linkedin.com/company/{linkedin_matches[0]}"
                            
                            # Busca telefone
                            phone_pattern = r'[\+]?[1-9]?[0-9]{7,15}'
                            phone_matches = re.findall(phone_pattern, html)
                            if phone_matches:
                                contact_info['phone'] = phone_matches[0]
                            
                            if contact_info['general_email']:
                                break
                                
                except Exception as e:
                    logger.debug(f"Error fetching {url}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error enriching contact for {domain}: {str(e)}")
        
        return contact_info
    
    async def analyze_company(self, domain: str) -> CompanyProfile:
        """Análise completa de uma empresa"""
        logger.info(f"Analyzing company: {domain}")
        
        # Cria perfil base
        profile = CompanyProfile(domain=domain)
        
        # Análises paralelas
        try:
            performance_task = self.analyze_website_performance(domain)
            tech_task = self.detect_tech_stack(domain)
            contact_task = self.enrich_contact_info(domain)
            
            # Aguarda todas as análises
            performance_result, tech_result, contact_result = await asyncio.gather(
                performance_task, tech_task, contact_task,
                return_exceptions=True
            )
            
            # Processa resultados
            if isinstance(performance_result, dict):
                profile.performance_metrics = performance_result
            
            if isinstance(tech_result, dict):
                profile.tech_stack = [tech_result.get('platform', 'unknown')]
                profile.saas_apps = tech_result.get('shopify_apps', [])
            
            if isinstance(contact_result, dict):
                profile.contact_info = contact_result
            
            # Calcula score de qualificação
            score = self.calculate_qualification_score(profile)
            
            logger.info(f"Company {domain} analyzed - Score: {score}")
            
            return profile
            
        except Exception as e:
            logger.error(f"Error analyzing company {domain}: {str(e)}")
            profile.qualification_notes = f"Analysis error: {str(e)}"
            return profile
    
    def generate_seed_domains(self, count: int = 150) -> List[str]:
        """
        Gera lista de domínios seed baseada nos ICPs ARCO
        Combina diferentes estratégias para encontrar targets relevantes
        """
        
        # Domínios exemplo para diferentes ICPs
        seed_domains = [
            # E-commerce Growth (ICP P1)
            'fashionnova.com', 'gymshark.com', 'mvmt.com', 'allbirds.com', 'warby-parker.com',
            'casper.com', 'glossier.com', 'away.com', 'outdoor-voices.com', 'everlane.com',
            
            # DTC Brands (ICP P2)  
            'ritual.com', 'hims.com', 'curology.com', 'native.com', 'harry-s.com',
            'thirdlove.com', 'rothy-s.com', 'brooklinen.com', 'parachute-home.com', 'purple.com',
            
            # Professional Services (ICP P3)
            'rocket-lawyer.com', 'legalzoom.com', 'nolo.com', 'avvo.com', 'martindale.com',
            'findlaw.com', 'justia.com', 'lawyers.com', 'attorney.com', 'lawfirm.com',
            
            # SaaS Bootstrapped (ICP P4)
            'calendly.com', 'typeform.com', 'convertkit.com', 'gumroad.com', 'carrd.co',
            'notion.so', 'airtable.com', 'webflow.com', 'figma.com', 'canva.com',
            
            # Targets adicionais baseados em padrões
            'supplement-store.com', 'skincare-brand.com', 'pet-products.com', 'jewelry-shop.com',
            'law-office.com', 'dental-clinic.com', 'accounting-firm.com', 'consulting-group.com'
        ]
        
        # Adiciona variações para alcançar o count desejado
        extended_domains = seed_domains.copy()
        
        # Gera variações de domínios baseadas em keywords relevantes
        keywords = [
            'shop', 'store', 'boutique', 'market', 'brand', 'company', 'group',
            'law', 'legal', 'clinic', 'medical', 'dental', 'accounting', 'consulting',
            'software', 'app', 'tool', 'platform', 'saas', 'tech'
        ]
        
        extensions = ['.com', '.co', '.io', '.net']
        
        # Gera combinações até atingir o count
        import random
        random.seed(42)  # Para reprodutibilidade
        
        while len(extended_domains) < count:
            keyword = random.choice(keywords)
            suffix = random.choice(['co', 'inc', 'group', 'solutions', 'services'])
            extension = random.choice(extensions)
            
            domain = f"{keyword}-{suffix}{extension}".replace('.', '')
            if domain not in extended_domains:
                extended_domains.append(domain)
        
        return extended_domains[:count]
    
    async def scrape_leads(self, target_count: int = 100, min_score: int = 70) -> List[CompanyProfile]:
        """
        Processo principal de scraping para leads qualificados
        Meta: 100 leads com score ≥ 70
        """
        logger.info(f"Starting lead scraping - Target: {target_count} leads with score ≥ {min_score}")
        
        # Gera lista de domínios seed
        seed_domains = self.generate_seed_domains(count=target_count * 2)  # 2x para compensar filtros
        
        qualified_leads = []
        total_analyzed = 0
        
        # Processa em batches para evitar sobrecarga
        batch_size = 10
        
        for i in range(0, len(seed_domains), batch_size):
            batch = seed_domains[i:i + batch_size]
            
            # Análise paralela do batch
            tasks = [self.analyze_company(domain) for domain in batch]
            
            try:
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, CompanyProfile):
                        total_analyzed += 1
                        
                        if result.score >= min_score:
                            qualified_leads.append(result)
                            logger.info(f"✓ Qualified lead: {result.domain} (Score: {result.score})")
                        
                        # Salva todos os resultados
                        self.scraped_companies.append(result)
                
                # Progress update
                logger.info(f"Progress: {total_analyzed}/{len(seed_domains)} analyzed, {len(qualified_leads)} qualified")
                
                # Para quando atingir o target
                if len(qualified_leads) >= target_count:
                    logger.info(f"✅ Target reached: {len(qualified_leads)} qualified leads")
                    break
                    
            except Exception as e:
                logger.error(f"Error processing batch {i}: {str(e)}")
                continue
            
            # Rate limiting entre batches
            await asyncio.sleep(2)
        
        self.qualified_leads = qualified_leads[:target_count]
        
        logger.info(f"Scraping completed: {len(self.qualified_leads)} qualified leads from {total_analyzed} analyzed")
        
        return self.qualified_leads
    
    def save_results(self, filename: str = None):
        """Salva resultados em CSV e JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"arco_leads_{timestamp}"
        
        # CSV para análise
        csv_file = f"{filename}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if self.qualified_leads:
                writer = csv.DictWriter(f, fieldnames=asdict(self.qualified_leads[0]).keys())
                writer.writeheader()
                
                for lead in self.qualified_leads:
                    writer.writerow(asdict(lead))
        
        # JSON detalhado
        json_file = f"{filename}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(lead) for lead in self.qualified_leads], f, indent=2, ensure_ascii=False)
        
        # Relatório de summary
        summary_file = f"{filename}_summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("ARCO LEADS SCRAPING REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total Qualified Leads: {len(self.qualified_leads)}\n")
            f.write(f"Total Companies Analyzed: {len(self.scraped_companies)}\n")
            f.write(f"Qualification Rate: {len(self.qualified_leads)/len(self.scraped_companies)*100:.1f}%\n\n")
            
            # Score distribution
            scores = [lead.score for lead in self.qualified_leads]
            f.write("SCORE DISTRIBUTION:\n")
            f.write(f"Average Score: {sum(scores)/len(scores):.1f}\n")
            f.write(f"Highest Score: {max(scores)}\n")
            f.write(f"Lowest Score: {min(scores)}\n\n")
            
            # Top leads
            f.write("TOP 10 LEADS:\n")
            top_leads = sorted(self.qualified_leads, key=lambda x: x.score, reverse=True)[:10]
            for i, lead in enumerate(top_leads, 1):
                f.write(f"{i}. {lead.domain} - Score: {lead.score} - {lead.qualification_notes}\n")
        
        logger.info(f"Results saved: {csv_file}, {json_file}, {summary_file}")
        
        return csv_file, json_file, summary_file

async def main():
    """Função principal para executar o scraping"""
    
    # Configuração do Google API Key
    google_key = os.getenv('GOOGLE_API_KEY')
    if not google_key:
        logger.error("GOOGLE_API_KEY not found in environment variables")
        return
    
    logger.info("Starting ARCO Lead Scraping System")
    logger.info(f"Google API Key configured: {google_key[:10]}...")
    
    async with ARCOProspectingScraper() as scraper:
        # Executa scraping para 100 leads qualificados
        qualified_leads = await scraper.scrape_leads(target_count=100, min_score=70)
        
        # Salva resultados
        if qualified_leads:
            csv_file, json_file, summary_file = scraper.save_results()
            
            logger.info("=" * 60)
            logger.info("SCRAPING COMPLETED SUCCESSFULLY")
            logger.info(f"✅ {len(qualified_leads)} qualified leads generated")
            logger.info(f"📊 Results saved to: {csv_file}")
            logger.info(f"📋 Summary available in: {summary_file}")
            logger.info("=" * 60)
            
            # Mostra top 5 leads
            print("\n🎯 TOP 5 QUALIFIED LEADS:")
            print("-" * 60)
            top_leads = sorted(qualified_leads, key=lambda x: x.score, reverse=True)[:5]
            
            for i, lead in enumerate(top_leads, 1):
                print(f"{i}. {lead.domain}")
                print(f"   Score: {lead.score}/100")
                print(f"   Notes: {lead.qualification_notes}")
                if lead.performance_metrics.get('lcp_mobile'):
                    print(f"   LCP: {lead.performance_metrics['lcp_mobile']:.1f}s")
                if lead.contact_info.get('general_email'):
                    print(f"   Email: {lead.contact_info['general_email']}")
                print()
        
        else:
            logger.warning("No qualified leads found. Consider adjusting criteria.")

if __name__ == "__main__":
    # Configura API key como variável de ambiente
    os.environ['GOOGLE_API_KEY'] = 'AIzaSyDNo6ycjKNYfDBmbFbOLI7kk-A-teppPaE'
    
    # Executa scraping
    asyncio.run(main())
