#!/usr/bin/env python3
"""
🔥 ARCO CUSTOM TECH STACK DETECTOR
Detecção customizada de tecnologias para substituir BuiltWith rate limiting
Baseado em análise de HTML + headers + JavaScript detection
"""

import requests
import re
import json
import time
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomTechDetector:
    """Detector customizado de tech stack para escalar sem rate limiting"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Signatures para detecção de tecnologias
        self.tech_signatures = {
            # CMS Detection
            'cms': {
                'WordPress': [
                    r'wp-content',
                    r'wp-includes',
                    r'wp-admin',
                    r'wordpress',
                    r'themes\/[^\/]+\/',
                    r'plugins\/[^\/]+\/'
                ],
                'Drupal': [
                    r'drupal',
                    r'sites\/default\/files',
                    r'misc\/drupal\.js',
                    r'Drupal\.settings'
                ],
                'Joomla': [
                    r'joomla',
                    r'components\/com_',
                    r'modules\/mod_',
                    r'templates\/[^\/]+\/'
                ],
                'Shopify': [
                    r'shopify',
                    r'cdn\.shopify\.com',
                    r'Shopify\.theme',
                    r'\/assets\/shopify'
                ],
                'Wix': [
                    r'wix\.com',
                    r'static\.wixstatic\.com',
                    r'Wix\.Utils'
                ],
                'Squarespace': [
                    r'squarespace',
                    r'static1\.squarespace\.com',
                    r'Squarespace\.Constants'
                ]
            },
            
            # Analytics Detection
            'analytics': {
                'Google Analytics': [
                    r'google-analytics\.com\/analytics\.js',
                    r'googletagmanager\.com\/gtag',
                    r'gtag\(',
                    r'ga\(',
                    r'UA-\d+-\d+'
                ],
                'Google Analytics 4': [
                    r'gtag\.js',
                    r'G-[A-Z0-9]+',
                    r'config.*G-'
                ],
                'Facebook Pixel': [
                    r'facebook\.net\/tr',
                    r'fbq\(',
                    r'facebook\.com\/tr'
                ],
                'Hotjar': [
                    r'hotjar\.com',
                    r'hjBootstrap',
                    r'hj\.js'
                ],
                'Mixpanel': [
                    r'mixpanel\.com',
                    r'mixpanel\.init',
                    r'mp_'
                ]
            },
            
            # Security Detection
            'security': {
                'SSL Certificate': [
                    r'^https://'  # Check if URL starts with https
                ],
                'Cloudflare': [
                    r'cloudflare',
                    r'cf-ray',
                    r'__cfduid',
                    r'cloudflare\.com'
                ],
                'reCAPTCHA': [
                    r'recaptcha',
                    r'g-recaptcha',
                    r'grecaptcha'
                ],
                'Sucuri': [
                    r'sucuri',
                    r'cloudproxy'
                ]
            },
            
            # JavaScript Frameworks
            'javascript': {
                'React': [
                    r'react',
                    r'ReactDOM',
                    r'__REACT_DEVTOOLS_GLOBAL_HOOK__',
                    r'react\.js',
                    r'react\.production'
                ],
                'Vue.js': [
                    r'vue\.js',
                    r'Vue\.js',
                    r'__VUE__',
                    r'vue\.min\.js'
                ],
                'Angular': [
                    r'angular',
                    r'ng-app',
                    r'angular\.js',
                    r'ng-version'
                ],
                'jQuery': [
                    r'jquery',
                    r'jQuery',
                    r'\$\(',
                    r'jquery\.js'
                ]
            },
            
            # Marketing Tools
            'marketing': {
                'MailChimp': [
                    r'mailchimp',
                    r'mc\.us\d+\.list-manage\.com',
                    r'mailchimp\.js'
                ],
                'Intercom': [
                    r'intercom',
                    r'widget\.intercom\.io',
                    r'Intercom\('
                ],
                'Zendesk': [
                    r'zendesk',
                    r'zopim',
                    r'ze-snippet'
                ],
                'Calendly': [
                    r'calendly',
                    r'calendly\.com\/assets',
                    r'Calendly\.initBadgeWidget'
                ]
            },
            
            # E-commerce
            'ecommerce': {
                'WooCommerce': [
                    r'woocommerce',
                    r'wc-ajax',
                    r'wp-content\/plugins\/woocommerce'
                ],
                'Shopify': [
                    r'shopify',
                    r'cdn\.shopify\.com',
                    r'Shopify\.theme'
                ],
                'BigCommerce': [
                    r'bigcommerce',
                    r'mybigcommerce\.com',
                    r'BigCommerce'
                ]
            }
        }
    
    def detect_tech_stack(self, url: str) -> Dict:
        """Detectar tech stack completo de uma URL"""
        logger.info(f"🔍 Analyzing tech stack for {url}")
        
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Get page content
            response = self.session.get(url, timeout=10, allow_redirects=True)
            
            if response.status_code != 200:
                logger.warning(f"HTTP {response.status_code} for {url}")
                return self._empty_result(url, f"HTTP {response.status_code}")
            
            html_content = response.text.lower()
            headers = {k.lower(): v.lower() for k, v in response.headers.items()}
            
            # Detect technologies
            detected = {}
            tech_counts = {}
            
            for category, technologies in self.tech_signatures.items():
                detected[category] = []
                tech_counts[category] = {'live': 0, 'dead': 0}
                
                for tech_name, patterns in technologies.items():
                    if self._detect_technology(html_content, headers, patterns, url):
                        detected[category].append(tech_name)
                        tech_counts[category]['live'] += 1
            
            # Calculate missing essentials
            missing_essentials = []
            
            if tech_counts['analytics']['live'] == 0:
                missing_essentials.append("No analytics tools detected")
            
            if tech_counts['security']['live'] == 0:
                missing_essentials.append("No security tools detected")
            
            if not url.startswith('https://'):
                missing_essentials.append("No SSL certificate")
            
            if tech_counts['cms']['live'] == 0:
                missing_essentials.append("No CMS detected")
            
            # Calculate tech debt score
            tech_debt_score = self._calculate_tech_debt(tech_counts, missing_essentials)
            
            result = {
                'url': url,
                'status': 'success',
                'detected_technologies': detected,
                'tech_counts': tech_counts,
                'missing_essentials': missing_essentials,
                'tech_debt_score': tech_debt_score,
                'analysis_timestamp': time.time()
            }
            
            logger.info(f"✅ Analysis complete: {sum([counts['live'] for counts in tech_counts.values()])} technologies detected")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {url}: {e}")
            return self._empty_result(url, f"Request error: {str(e)}")
        except Exception as e:
            logger.error(f"Analysis error for {url}: {e}")
            return self._empty_result(url, f"Analysis error: {str(e)}")
    
    def _detect_technology(self, html: str, headers: Dict, patterns: List[str], url: str) -> bool:
        """Detectar se uma tecnologia específica está presente"""
        
        # Check URL protocol for SSL
        if patterns == [r'^https://']:
            return url.startswith('https://')
        
        # Check HTML content
        for pattern in patterns:
            if re.search(pattern, html, re.IGNORECASE):
                return True
        
        # Check headers
        for header_value in headers.values():
            for pattern in patterns:
                if re.search(pattern, header_value, re.IGNORECASE):
                    return True
        
        return False
    
    def _calculate_tech_debt(self, tech_counts: Dict, missing_essentials: List[str]) -> int:
        """Calcular score de tech debt baseado nas ausências"""
        debt_score = 0
        
        # Penalize missing essentials
        debt_score += len(missing_essentials) * 25
        
        # Penalize categories with no technologies
        for category, counts in tech_counts.items():
            if counts['live'] == 0:
                if category == 'security':
                    debt_score += 30  # Security is critical
                elif category == 'analytics':
                    debt_score += 20  # Analytics is important
                else:
                    debt_score += 10  # Other categories
        
        return min(debt_score, 100)
    
    def _empty_result(self, url: str, error: str) -> Dict:
        """Retornar resultado vazio em caso de erro"""
        return {
            'url': url,
            'status': 'error',
            'error': error,
            'detected_technologies': {},
            'tech_counts': {},
            'missing_essentials': [],
            'tech_debt_score': 0,
            'analysis_timestamp': time.time()
        }
    
    def batch_analyze(self, urls: List[str]) -> List[Dict]:
        """Analisar múltiplas URLs em batch"""
        logger.info(f"🚀 Starting batch analysis of {len(urls)} URLs")
        
        results = []
        for i, url in enumerate(urls, 1):
            logger.info(f"Analyzing {i}/{len(urls)}: {url}")
            
            result = self.detect_tech_stack(url)
            results.append(result)
            
            # Small delay to be respectful
            time.sleep(0.5)
        
        logger.info(f"✅ Batch analysis complete: {len(results)} results")
        return results

# Test function
def test_custom_detector():
    """Testar o detector customizado"""
    detector = CustomTechDetector()
    
    test_urls = [
        "https://parkviewdentaltoronto.com",
        "http://argentocpa.ca",
        "https://cityviewdentaltoronto.com",
        "https://yaletownaccounting.com",
        "https://spurrell.ca"
    ]
    
    print("🔥 CUSTOM TECH DETECTOR TEST")
    print("=" * 50)
    
    results = detector.batch_analyze(test_urls)
    
    for result in results:
        print(f"\n📊 Analysis for {result['url']}:")
        print(f"Status: {result['status']}")
        
        if result['status'] == 'success':
            print(f"Tech Debt Score: {result['tech_debt_score']}/100")
            
            for category, technologies in result['detected_technologies'].items():
                if technologies:
                    print(f"{category.title()}: {', '.join(technologies)}")
            
            if result['missing_essentials']:
                print(f"Missing: {', '.join(result['missing_essentials'])}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 50)
    print("🎯 CUSTOM DETECTION COMPLETE")
    
    # Export results
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"custom_tech_analysis_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📄 Results exported to: {filename}")

if __name__ == "__main__":
    test_custom_detector()
