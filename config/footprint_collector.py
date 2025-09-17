#!/usr/bin/env python3
"""
🔍 FOOTPRINT COLLECTOR - Layer 2
High-Performance SaaS & Tech Stack Detection

OBJETIVO: Coleta digital footprint em <0.4s com vendor cost mapping
- Otimizado do leak detector existente
- Integração com ICP Kernel
- Parallel processing para speed
- Cost-aware SaaS detection
"""

import asyncio
import aiohttp
import time
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import json
from urllib.parse import urljoin, urlparse
import socket

# Import ICP Kernel
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))
from icp_kernel import ICPKernel

@dataclass
class FootprintResult:
    """Resultado da coleta de footprint"""
    domain: str
    execution_time: float
    
    # SaaS Detection
    detected_apps: List[str]
    app_costs: Dict[str, int]
    total_waste: int
    
    # Tech Stack
    cms: Optional[str]
    ecommerce_platform: Optional[str]
    analytics: List[str]
    marketing_tools: List[str]
    
    # Basic Performance
    load_time: Optional[float]
    status_code: int
    
    # Metadata
    title: Optional[str]
    meta_description: Optional[str]
    
    success: bool
    error: Optional[str] = None

class FootprintCollector:
    """
    High-performance SaaS footprint collector
    
    Otimizado para speed (<0.4s) e integrado com ICP Kernel
    para cost-aware detection
    """
    
    def __init__(self):
        self.kernel = ICPKernel()
        
        # Performance settings
        self.timeout = 3.0  # 3s timeout
        self.max_concurrent = 10
        
        # Headers para evitar blocking
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # SaaS Detection Patterns (otimizado)
        self.saas_patterns = {
            # Email Marketing
            'klaviyo': [
                r'klaviyo\.com',
                r'klaviyo-media\.com',
                r'klviyo\.com',
                r'static\.klaviyo\.com'
            ],
            'mailchimp': [
                r'mailchimp\.com',
                r'mctk\.com',
                r'chimpstatic\.com',
                r'list-manage\.com'
            ],
            'sendgrid': [
                r'sendgrid\.net',
                r'sendgrid\.com',
                r'sgwidgets\.com'
            ],
            
            # Analytics
            'hotjar': [
                r'hotjar\.com',
                r'hjdebug\.com',
                r'static\.hotjar\.com'
            ],
            'mixpanel': [
                r'mixpanel\.com',
                r'mxpnl\.com',
                r'api\.mixpanel\.com'
            ],
            'fullstory': [
                r'fullstory\.com',
                r'fs\.com'
            ],
            
            # Customer Support
            'zendesk': [
                r'zendesk\.com',
                r'zdassets\.com',
                r'zdchat\.com'
            ],
            'intercom': [
                r'intercom\.io',
                r'intercom\.com',
                r'intercomcdn\.com'
            ],
            'drift': [
                r'drift\.com',
                r'driftt\.com'
            ],
            
            # Forms
            'typeform': [
                r'typeform\.com',
                r'tfstatic\.com'
            ],
            'jotform': [
                r'jotform\.com',
                r'jotfor\.ms'
            ],
            
            # Subscriptions  
            'recharge': [
                r'rechargeapps\.com',
                r'rechargepayments\.com'
            ],
            'loop': [
                r'loop\.com',
                r'getloop\.com'
            ],
            'yotpo': [
                r'yotpo\.com',
                r'yotpoassets\.com'
            ],
            
            # Optimization
            'optimizely': [
                r'optimizely\.com',
                r'optimcdn\.com'
            ],
            'vwo': [
                r'vwo\.com',
                r'visualwebsiteoptimizer\.com'
            ],
            
            # Others
            'shopify': [
                r'shopify\.com',
                r'myshopify\.com',
                r'shopifycdn\.com'
            ],
            'google_analytics': [
                r'google-analytics\.com',
                r'googletagmanager\.com'
            ]
        }
        
        print("🔍 FOOTPRINT COLLECTOR INITIALIZED")
        print("=" * 45)
        print(f"📊 {len(self.saas_patterns)} SaaS patterns loaded")
        print(f"💰 {len(self.kernel.vendor_costs)} vendor costs mapped")
        print(f"⚡ Target: <0.4s per domain")

    async def collect_footprint(self, domain: str) -> FootprintResult:
        """
        Coleta footprint completo de um domain
        
        Performance target: <0.4s
        """
        start_time = time.time()
        
        # Normalize domain
        if not domain.startswith(('http://', 'https://')):
            domain = f'https://{domain}'
        
        parsed_domain = urlparse(domain).netloc
        
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers=self.headers
            ) as session:
                
                # Fetch page content
                content, status_code, load_time = await self._fetch_content(session, domain)
                
                if not content:
                    return FootprintResult(
                        domain=parsed_domain,
                        execution_time=time.time() - start_time,
                        detected_apps=[],
                        app_costs={},
                        total_waste=0,
                        cms=None,
                        ecommerce_platform=None,
                        analytics=[],
                        marketing_tools=[],
                        load_time=load_time,
                        status_code=status_code,
                        title=None,
                        meta_description=None,
                        success=False,
                        error=f"No content retrieved (status: {status_code})"
                    )
                
                # Parallel processing of detection tasks
                tasks = [
                    self._detect_saas_apps(content),
                    self._extract_metadata(content),
                    self._detect_ecommerce_platform(content),
                    self._detect_cms(content)
                ]
                
                results = await asyncio.gather(*tasks)
                detected_apps, metadata, ecommerce_platform, cms = results
                
                # Calculate costs using ICP Kernel
                waste_analysis = self.kernel.estimate_saas_waste(detected_apps)
                
                # Categorize apps
                analytics = [app for app in detected_apps if any(
                    word in app.lower() for word in ['analytics', 'mixpanel', 'hotjar', 'fullstory', 'amplitude']
                )]
                marketing_tools = [app for app in detected_apps if any(
                    word in app.lower() for word in ['klaviyo', 'mailchimp', 'sendgrid', 'typeform', 'campaign']
                )]
                
                execution_time = time.time() - start_time
                
                return FootprintResult(
                    domain=parsed_domain,
                    execution_time=execution_time,
                    detected_apps=detected_apps,
                    app_costs=waste_analysis['app_costs'],
                    total_waste=waste_analysis['total_monthly_waste'],
                    cms=cms,
                    ecommerce_platform=ecommerce_platform,
                    analytics=analytics,
                    marketing_tools=marketing_tools,
                    load_time=load_time,
                    status_code=status_code,
                    title=metadata.get('title'),
                    meta_description=metadata.get('description'),
                    success=True
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            return FootprintResult(
                domain=parsed_domain,
                execution_time=execution_time,
                detected_apps=[],
                app_costs={},
                total_waste=0,
                cms=None,
                ecommerce_platform=None,
                analytics=[],
                marketing_tools=[],
                load_time=None,
                status_code=0,
                title=None,
                meta_description=None,
                success=False,
                error=str(e)
            )

    async def _fetch_content(self, session: aiohttp.ClientSession, url: str) -> Tuple[str, int, float]:
        """Fetch page content with timing"""
        
        start_time = time.time()
        
        try:
            async with session.get(url) as response:
                load_time = time.time() - start_time
                content = await response.text()
                return content, response.status, load_time
                
        except Exception:
            load_time = time.time() - start_time
            return "", 0, load_time

    async def _detect_saas_apps(self, content: str) -> List[str]:
        """Detecta SaaS apps no conteúdo"""
        
        detected = []
        content_lower = content.lower()
        
        for app_name, patterns in self.saas_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    detected.append(app_name)
                    break  # Stop after first match for this app
        
        return list(set(detected))  # Remove duplicates

    async def _extract_metadata(self, content: str) -> Dict[str, str]:
        """Extrai metadados básicos"""
        
        metadata = {}
        
        # Title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
        
        # Meta description
        desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', content, re.IGNORECASE)
        if desc_match:
            metadata['description'] = desc_match.group(1).strip()
        
        return metadata

    async def _detect_ecommerce_platform(self, content: str) -> Optional[str]:
        """Detecta plataforma de ecommerce"""
        
        content_lower = content.lower()
        
        ecommerce_indicators = {
            'shopify': ['shopify', 'myshopify.com', 'shopifycdn'],
            'woocommerce': ['woocommerce', 'wc-ajax'],
            'magento': ['magento', 'mage'],
            'bigcommerce': ['bigcommerce'],
            'squarespace': ['squarespace'],
            'wix': ['wix.com', 'wixstatic']
        }
        
        for platform, indicators in ecommerce_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                return platform
        
        return None

    async def _detect_cms(self, content: str) -> Optional[str]:
        """Detecta CMS"""
        
        content_lower = content.lower()
        
        cms_indicators = {
            'wordpress': ['wp-content', 'wp-includes', 'wordpress'],
            'drupal': ['drupal', 'sites/default'],
            'joomla': ['joomla'],
            'webflow': ['webflow'],
            'ghost': ['ghost'],
            'squarespace': ['squarespace']
        }
        
        for cms, indicators in cms_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                return cms
        
        return None

    async def batch_collect(self, domains: List[str], max_concurrent: int = 10) -> List[FootprintResult]:
        """
        Coleta footprint em batch para múltiplos domains
        
        Otimizado para processar muitos domains rapidamente
        """
        
        print(f"\n🔍 BATCH FOOTPRINT COLLECTION")
        print(f"📊 Domains: {len(domains)}")
        print(f"⚡ Max concurrent: {max_concurrent}")
        
        start_time = time.time()
        
        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def collect_with_limit(domain):
            async with semaphore:
                return await self.collect_footprint(domain)
        
        # Execute all collections
        tasks = [collect_with_limit(domain) for domain in domains]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(FootprintResult(
                    domain=domains[i],
                    execution_time=0,
                    detected_apps=[],
                    app_costs={},
                    total_waste=0,
                    cms=None,
                    ecommerce_platform=None,
                    analytics=[],
                    marketing_tools=[],
                    load_time=None,
                    status_code=0,
                    title=None,
                    meta_description=None,
                    success=False,
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        total_time = time.time() - start_time
        avg_time = total_time / len(domains)
        
        print(f"✅ Batch completed: {total_time:.2f}s total, {avg_time:.3f}s avg")
        
        return processed_results

    def generate_footprint_report(self, results: List[FootprintResult]) -> Dict[str, Any]:
        """Gera relatório de footprint collection"""
        
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        # Performance metrics
        execution_times = [r.execution_time for r in results if r.execution_time > 0]
        avg_execution = sum(execution_times) / len(execution_times) if execution_times else 0
        
        # SaaS apps analysis
        all_apps = []
        total_waste = 0
        for result in successful:
            all_apps.extend(result.detected_apps)
            total_waste += result.total_waste
        
        app_frequency = {}
        for app in all_apps:
            app_frequency[app] = app_frequency.get(app, 0) + 1
        
        # Platform analysis
        platforms = {}
        cms_usage = {}
        
        for result in successful:
            if result.ecommerce_platform:
                platforms[result.ecommerce_platform] = platforms.get(result.ecommerce_platform, 0) + 1
            if result.cms:
                cms_usage[result.cms] = cms_usage.get(result.cms, 0) + 1
        
        return {
            'summary': {
                'total_domains': len(results),
                'successful': len(successful),
                'failed': len(failed),
                'success_rate': len(successful) / len(results) * 100,
                'avg_execution_time': avg_execution,
                'target_met': avg_execution < 0.4  # <0.4s target
            },
            'performance': {
                'fastest': min(execution_times) if execution_times else 0,
                'slowest': max(execution_times) if execution_times else 0,
                'under_target': sum(1 for t in execution_times if t < 0.4),
                'over_target': sum(1 for t in execution_times if t >= 0.4)
            },
            'saas_analysis': {
                'total_apps_detected': len(all_apps),
                'unique_apps': len(set(all_apps)),
                'total_monthly_waste': total_waste,
                'most_common_apps': sorted(app_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
            },
            'tech_stack': {
                'ecommerce_platforms': platforms,
                'cms_systems': cms_usage
            },
            'failed_domains': [{'domain': r.domain, 'error': r.error} for r in failed]
        }

# Demo & Testing
async def demo_footprint_collector():
    """Demo do Footprint Collector"""
    
    print("\n🔍 FOOTPRINT COLLECTOR DEMO")
    print("=" * 50)
    
    collector = FootprintCollector()
    
    # Test domains (beauty/skincare niche)
    test_domains = [
        'glossier.com',
        'sephora.com', 
        'ulta.com',
        'kiehls.com',
        'lush.com'
    ]
    
    print(f"\n🎯 Testing {len(test_domains)} beauty/skincare domains")
    print("Target: <0.4s per domain")
    
    # Single domain test
    print(f"\n🔍 Single domain test: {test_domains[0]}")
    result = await collector.collect_footprint(test_domains[0])
    
    print(f"⚡ Execution time: {result.execution_time:.3f}s")
    print(f"📊 Apps detected: {len(result.detected_apps)}")
    print(f"💰 Monthly waste: ${result.total_waste}")
    print(f"🛍️ Platform: {result.ecommerce_platform}")
    
    if result.detected_apps:
        print(f"📱 Apps: {', '.join(result.detected_apps[:5])}")
    
    # Batch test
    print(f"\n🔥 Batch test: {len(test_domains)} domains")
    batch_results = await collector.batch_collect(test_domains)
    
    # Generate report
    report = collector.generate_footprint_report(batch_results)
    
    print(f"\n📋 BATCH RESULTS:")
    print(f"  • Success rate: {report['summary']['success_rate']:.1f}%")
    print(f"  • Avg time: {report['summary']['avg_execution_time']:.3f}s")
    print(f"  • Target met: {'✅' if report['summary']['target_met'] else '❌'}")
    print(f"  • Total waste: ${report['saas_analysis']['total_monthly_waste']:,}/month")
    print(f"  • Unique apps: {report['saas_analysis']['unique_apps']}")
    
    if report['saas_analysis']['most_common_apps']:
        print(f"  • Top apps: {', '.join([app for app, count in report['saas_analysis']['most_common_apps'][:3]])}")
    
    print(f"\n✅ Footprint Collector ready for production!")

if __name__ == "__main__":
    asyncio.run(demo_footprint_collector())
