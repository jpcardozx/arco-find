"""
🔍 REAL SCRAPING DISCOVERY ENGINE
=================================
Implementação madura e estratégica com scraping real
Sem mocks, sem dados fabricados
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from typing import List, Dict
import re
from urllib.parse import urlparse, urljoin
import csv
from io import StringIO

class RealScrapingEngine:
    """Engine de scraping real - abordagem madura"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        
        self.prospects = []
        
    def scrape_shopify_stores(self) -> List[Dict]:
        """Scraping real de Shopify stores via múltiplas fontes"""
        print("🛍️ Scraping real Shopify stores...")
        
        shopify_prospects = []
        
        # Fonte 1: BuiltWith Shopify report
        try:
            builtwith_stores = self._scrape_builtwith_shopify()
            shopify_prospects.extend(builtwith_stores)
            print(f"  ✅ BuiltWith: {len(builtwith_stores)} stores")
        except Exception as e:
            print(f"  ❌ BuiltWith error: {e}")
        
        # Fonte 2: Shopify App Store (stores que usam apps específicos)
        try:
            app_store_stores = self._scrape_shopify_app_stores()
            shopify_prospects.extend(app_store_stores)
            print(f"  ✅ App Store: {len(app_store_stores)} stores")
        except Exception as e:
            print(f"  ❌ App Store error: {e}")
            
        # Fonte 3: E-commerce directories brasileiros
        try:
            directory_stores = self._scrape_ecommerce_directories()
            shopify_prospects.extend(directory_stores)
            print(f"  ✅ Directories: {len(directory_stores)} stores")
        except Exception as e:
            print(f"  ❌ Directories error: {e}")
        
        return shopify_prospects
    
    def _scrape_builtwith_shopify(self) -> List[Dict]:
        """Scrape BuiltWith para encontrar sites Shopify"""
        prospects = []
        
        # BuiltWith tem dados públicos limitados, mas podemos tentar
        url = "https://trends.builtwith.com/shop/Shopify"
        
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Procurar por links de domínios
            domain_links = soup.find_all('a', href=True)
            
            for link in domain_links:
                href = link.get('href', '')
                # Filtrar domínios que parecem ser lojas
                if self._is_valid_store_domain(href):
                    domain = self._extract_domain(href)
                    if domain and domain not in [p['domain'] for p in prospects]:
                        prospects.append({
                            'name': self._extract_store_name(link.text or domain),
                            'domain': domain,
                            'source': 'builtwith',
                            'category': 'shopify_small'
                        })
                        
                if len(prospects) >= 15:  # Limite para evitar spam
                    break
                    
        except Exception as e:
            print(f"BuiltWith scraping error: {e}")
        
        return prospects
    
    def _scrape_shopify_app_stores(self) -> List[Dict]:
        """Scrape Shopify App Store para encontrar stores que usam apps específicos"""
        prospects = []
        
        # Apps populares que small businesses usam
        target_apps = [
            "klaviyo-email-marketing",
            "product-reviews", 
            "privy-convert-more-visitors",
            "judge-me-product-reviews",
            "smile-loyalty-rewards"
        ]
        
        for app in target_apps:
            try:
                url = f"https://apps.shopify.com/{app}"
                response = self.session.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Procurar por reviews ou menções de stores
                review_sections = soup.find_all(['div', 'section'], class_=re.compile(r'review|testimonial|customer'))
                
                for section in review_sections:
                    # Extrair menções de domínios
                    text = section.get_text()
                    domains = re.findall(r'[a-zA-Z0-9-]+\.[a-zA-Z]{2,}', text)
                    
                    for domain in domains:
                        if self._is_valid_store_domain(domain) and len(prospects) < 10:
                            prospects.append({
                                'name': self._extract_store_name(domain),
                                'domain': domain,
                                'source': f'shopify_app_{app}',
                                'category': 'shopify_small'
                            })
                            
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"App store scraping error for {app}: {e}")
                continue
        
        return prospects
    
    def _scrape_ecommerce_directories(self) -> List[Dict]:
        """Scrape diretórios de e-commerce brasileiros"""
        prospects = []
        
        # Diretórios conhecidos
        directories = [
            "https://ecommercebrasil.com.br/directory",
            "https://www.e-commerce.org.br/empresas",
        ]
        
        for directory_url in directories:
            try:
                response = self.session.get(directory_url)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Procurar por links de empresas
                company_links = soup.find_all('a', href=True)
                
                for link in company_links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    if self._is_valid_store_domain(href):
                        domain = self._extract_domain(href)
                        if domain and len(prospects) < 15:
                            prospects.append({
                                'name': self._extract_store_name(text or domain),
                                'domain': domain,
                                'source': 'ecommerce_directory',
                                'category': 'shopify_small'
                            })
                
                time.sleep(2)  # Rate limiting mais conservador
                
            except Exception as e:
                print(f"Directory scraping error: {e}")
                continue
        
        return prospects
    
    def scrape_saas_companies(self) -> List[Dict]:
        """Scrape SaaS companies brasileiras"""
        print("💻 Scraping real SaaS companies...")
        
        saas_prospects = []
        
        # Fonte 1: Product Hunt Brasil
        try:
            ph_companies = self._scrape_product_hunt_brazil()
            saas_prospects.extend(ph_companies)
            print(f"  ✅ Product Hunt: {len(ph_companies)} companies")
        except Exception as e:
            print(f"  ❌ Product Hunt error: {e}")
        
        # Fonte 2: AngelList Brasil
        try:
            angel_companies = self._scrape_angel_list_brazil()
            saas_prospects.extend(angel_companies)
            print(f"  ✅ AngelList: {len(angel_companies)} companies")
        except Exception as e:
            print(f"  ❌ AngelList error: {e}")
            
        # Fonte 3: GitHub brasileiro com web apps
        try:
            github_companies = self._scrape_github_brazilian_saas()
            saas_prospects.extend(github_companies)
            print(f"  ✅ GitHub: {len(github_companies)} companies")
        except Exception as e:
            print(f"  ❌ GitHub error: {e}")
        
        return saas_prospects
    
    def _scrape_product_hunt_brazil(self) -> List[Dict]:
        """Scrape Product Hunt para SaaS brasileiros"""
        prospects = []
        
        try:
            # Product Hunt tem proteção, mas podemos tentar
            url = "https://www.producthunt.com/topics/brazil"
            response = self.session.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Procurar por produtos
                product_links = soup.find_all('a', href=re.compile(r'/posts/'))
                
                for link in product_links[:20]:  # Limite
                    try:
                        product_url = urljoin("https://www.producthunt.com", link['href'])
                        product_response = self.session.get(product_url)
                        product_soup = BeautifulSoup(product_response.text, 'html.parser')
                        
                        # Extrair nome e website
                        title_element = product_soup.find('h1')
                        website_link = product_soup.find('a', href=re.compile(r'https?://(?!.*producthunt)'))
                        
                        if title_element and website_link:
                            name = title_element.get_text(strip=True)
                            domain = self._extract_domain(website_link['href'])
                            
                            if domain and self._is_valid_saas_domain(domain):
                                prospects.append({
                                    'name': name,
                                    'domain': domain,
                                    'source': 'product_hunt',
                                    'category': 'saas_bootstrap'
                                })
                        
                        time.sleep(1)  # Rate limiting
                        
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"Product Hunt scraping error: {e}")
        
        return prospects
    
    def _scrape_angel_list_brazil(self) -> List[Dict]:
        """Scrape AngelList para startups brasileiras"""
        prospects = []
        
        try:
            # AngelList/Wellfound busca
            url = "https://angel.co/brazil/startups"
            response = self.session.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Procurar por startups
                startup_elements = soup.find_all(['div', 'a'], class_=re.compile(r'startup|company'))
                
                for element in startup_elements[:15]:
                    try:
                        name_element = element.find(['h3', 'h4', 'strong'])
                        link_element = element.find('a', href=True)
                        
                        if name_element and link_element:
                            name = name_element.get_text(strip=True)
                            href = link_element.get('href', '')
                            
                            # Se é link externo, extrair domain
                            if href.startswith('http') and 'angel.co' not in href:
                                domain = self._extract_domain(href)
                                if domain and self._is_valid_saas_domain(domain):
                                    prospects.append({
                                        'name': name,
                                        'domain': domain,
                                        'source': 'angel_list',
                                        'category': 'saas_bootstrap'
                                    })
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"AngelList scraping error: {e}")
        
        return prospects
    
    def _scrape_github_brazilian_saas(self) -> List[Dict]:
        """Scrape GitHub para encontrar SaaS brasileiros com websites"""
        prospects = []
        
        try:
            # GitHub search para repositórios brasileiros com websites
            search_terms = ["saas+language:JavaScript+brazil", "webapp+language:Python+brazil"]
            
            for term in search_terms:
                url = f"https://github.com/search?q={term}&type=repositories"
                response = self.session.get(url)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Procurar repositórios
                    repo_links = soup.find_all('a', href=re.compile(r'/[^/]+/[^/]+$'))
                    
                    for repo_link in repo_links[:10]:
                        try:
                            repo_url = urljoin("https://github.com", repo_link['href'])
                            repo_response = self.session.get(repo_url)
                            repo_soup = BeautifulSoup(repo_response.text, 'html.parser')
                            
                            # Procurar link do website
                            website_link = repo_soup.find('a', {'rel': 'nofollow', 'href': re.compile(r'https?://')})
                            
                            if website_link:
                                domain = self._extract_domain(website_link['href'])
                                name = repo_link.get_text(strip=True).split('/')[-1]
                                
                                if domain and self._is_valid_saas_domain(domain):
                                    prospects.append({
                                        'name': name.replace('-', ' ').title(),
                                        'domain': domain,
                                        'source': 'github',
                                        'category': 'saas_bootstrap'
                                    })
                            
                            time.sleep(1)
                        except Exception as e:
                            continue
                            
                time.sleep(2)  # Rate limiting entre searches
                
        except Exception as e:
            print(f"GitHub scraping error: {e}")
        
        return prospects
    
    def _is_valid_store_domain(self, url_or_domain: str) -> bool:
        """Valida se é um domínio de loja válido"""
        if not url_or_domain:
            return False
        
        domain = self._extract_domain(url_or_domain)
        if not domain:
            return False
        
        # Filtros
        invalid_patterns = [
            'shopify.com', 'facebook.com', 'instagram.com', 'twitter.com',
            'linkedin.com', 'youtube.com', 'google.com', 'builtwith.com',
            'github.com', 'wordpress.com', 'wix.com'
        ]
        
        return not any(pattern in domain.lower() for pattern in invalid_patterns)
    
    def _is_valid_saas_domain(self, domain: str) -> bool:
        """Valida se é um domínio SaaS válido"""
        if not domain:
            return False
        
        # Similar ao store, mas com critérios específicos para SaaS
        invalid_patterns = [
            'github.com', 'gitlab.com', 'bitbucket.com', 'facebook.com',
            'linkedin.com', 'twitter.com', 'instagram.com', 'youtube.com',
            'google.com', 'microsoft.com', 'apple.com'
        ]
        
        return not any(pattern in domain.lower() for pattern in invalid_patterns)
    
    def _extract_domain(self, url: str) -> str:
        """Extrai domínio limpo de uma URL"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www.
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain
        except:
            return ""
    
    def _extract_store_name(self, text: str) -> str:
        """Extrai nome da loja do texto"""
        if not text:
            return "Unknown Store"
        
        # Limpa o texto
        name = re.sub(r'[^\w\s]', '', text).strip()
        name = ' '.join(name.split())  # Remove espaços extras
        
        return name.title() if name else "Unknown Store"
    
    def save_results(self, prospects: List[Dict], filename: str = None) -> str:
        """Salva resultados do scraping"""
        if not filename:
            filename = f"data/scraped_prospects_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            'scraping_metadata': {
                'scraped_at': datetime.now().isoformat(),
                'total_prospects': len(prospects),
                'sources': list(set(p.get('source', 'unknown') for p in prospects))
            },
            'prospects': prospects
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Results saved: {filename}")
        return filename
    
    def run_full_discovery(self) -> List[Dict]:
        """Executa descoberta completa com scraping real"""
        print("🎯 STARTING REAL SCRAPING DISCOVERY")
        print("=" * 50)
        
        all_prospects = []
        
        # Scrape Shopify stores
        shopify_prospects = self.scrape_shopify_stores()
        all_prospects.extend(shopify_prospects)
        
        # Scrape SaaS companies
        saas_prospects = self.scrape_saas_companies()
        all_prospects.extend(saas_prospects)
        
        # Remove duplicatas
        unique_prospects = []
        seen_domains = set()
        
        for prospect in all_prospects:
            domain = prospect.get('domain', '')
            if domain and domain not in seen_domains:
                seen_domains.add(domain)
                unique_prospects.append(prospect)
        
        print(f"\n✅ SCRAPING COMPLETE")
        print(f"  • Total prospects: {len(unique_prospects)}")
        print(f"  • Shopify stores: {len([p for p in unique_prospects if p.get('category') == 'shopify_small'])}")
        print(f"  • SaaS companies: {len([p for p in unique_prospects if p.get('category') == 'saas_bootstrap'])}")
        
        # Salvar resultados
        filename = self.save_results(unique_prospects)
        
        return unique_prospects

def main():
    """Executa o scraping real"""
    engine = RealScrapingEngine()
    prospects = engine.run_full_discovery()
    
    # Mostrar sample
    print(f"\n📋 SAMPLE PROSPECTS (first 10):")
    for i, prospect in enumerate(prospects[:10], 1):
        print(f"  {i}. {prospect['name']} ({prospect['domain']})")
        print(f"     • Category: {prospect['category']}")
        print(f"     • Source: {prospect['source']}")
        print()
    
    return prospects

if __name__ == "__main__":
    main()
