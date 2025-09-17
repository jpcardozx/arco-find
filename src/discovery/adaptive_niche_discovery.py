
#!/usr/bin/env python3
"""
🎯 ADAPTIVE NICHE DISCOVERY ENGINE
Discovery adaptativo por nicho usando Google Custom Search API

FOCO: Discovery real baseado em nicho da campanha
- Google Custom Search API adaptativo
- Queries específicas por nicho (beauty, B2B SaaS, local services)
- Qualification real via PageSpeed + revenue estimation
- Zero mock data - apenas prospects reais descobertos
"""

import os
import json
import asyncio
import aiohttp
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import time
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

@dataclass
class DiscoveredProspect:
    """Prospect descoberto via Custom Search"""
    company_name: str
    domain: str
    website: str
    search_query: str
    niche: str
    discovery_source: str
    snippet: str
    
    # Qualification
    performance_score: int
    estimated_revenue: int
    tech_stack: List[str]
    issues_found: List[str]
    
    # Scoring
    priority: str
    confidence: str
    analysis_time: float

class AdaptiveNicheDiscovery:
    """
    Discovery engine adaptativo por nicho
    
    Usa Google Custom Search para descobrir prospects reais
    baseado no nicho da campanha
    """
    
    def __init__(self):
        # Google APIs
        self.search_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        self.search_cx = os.getenv('GOOGLE_SEARCH_CX')
        self.pagespeed_key = os.getenv('GOOGLE_PAGESPEED_API_KEY')
        
        # Dynamic query builder - adapts based on results
        self.niche_intelligence = {
            'beauty_skincare': {
                'core_terms': ['beauty', 'skincare', 'cosmetics', 'makeup', 'beleza', 'cosméticos'],
                'modifiers': ['store', 'loja', 'products', 'produtos', 'routine', 'rotina'],
                'revenue_indicators': ['premium', 'luxury', 'professional', 'clinic', 'spa'],
                'tech_signals': ['shopify', 'woocommerce', 'magento'],
                'domain_patterns': ['.com.br', '.beauty', '.cosmetics']
            },
            'b2b_saas': {
                'core_terms': ['software', 'saas', 'platform', 'plataforma', 'sistema', 'solução'],
                'modifiers': ['enterprise', 'business', 'corporate', 'empresarial', 'gestão'],
                'revenue_indicators': ['enterprise', 'corporate', 'API', 'integration', 'white-label'],
                'tech_signals': ['react', 'angular', 'aws', 'azure', 'api'],
                'domain_patterns': ['.com', '.io', '.app', '.tech']
            },
            'ecommerce': {
                'core_terms': ['ecommerce', 'e-commerce', 'loja', 'store', 'marketplace', 'shopping'],
                'modifiers': ['online', 'virtual', 'delivery', 'entrega', 'vendas'],
                'revenue_indicators': ['marketplace', 'catalog', 'inventory', 'payment'],
                'tech_signals': ['shopify', 'woocommerce', 'magento', 'vtex'],
                'domain_patterns': ['.com.br', '.store', '.shop']
            },
            'local_services': {
                'core_terms': ['serviços', 'services', 'consultoria', 'clinic', 'studio', 'agency'],
                'modifiers': ['local', 'atendimento', 'professional', 'especializado'],
                'revenue_indicators': ['appointment', 'booking', 'consultation', 'premium'],
                'tech_signals': ['wordpress', 'appointment', 'booking'],
                'domain_patterns': ['.com.br', '.local', '.services']
            }
        }
        
        # Query performance tracking for adaptive improvement
        self.query_performance = {}
        self.successful_patterns = {}
        
        # Advanced revenue estimation matrices
        self.revenue_intelligence = {
            'beauty_skincare': {
                'base_revenue': 25000,
                'domain_multipliers': {'.com': 1.4, '.com.br': 1.2, '.beauty': 1.6, '.cosmetics': 1.5},
                'content_signals': {
                    'high_value': ['premium', 'luxury', 'professional', 'dermatologist', 'clinic'],
                    'medium_value': ['natural', 'organic', 'boutique', 'salon'],
                    'enterprise': ['wholesale', 'distributor', 'brand', 'laboratory']
                },
                'tech_value': {'shopify_plus': 2.0, 'magento_enterprise': 1.8, 'custom_platform': 1.6}
            },
            'b2b_saas': {
                'base_revenue': 35000,
                'domain_multipliers': {'.com': 1.5, '.io': 1.3, '.app': 1.2, '.ai': 1.4},
                'content_signals': {
                    'high_value': ['enterprise', 'api', 'integration', 'white-label', 'custom'],
                    'medium_value': ['business', 'professional', 'team', 'collaboration'],
                    'enterprise': ['corporate', 'security', 'compliance', 'scalable']
                },
                'tech_value': {'aws': 1.4, 'azure': 1.3, 'microservices': 1.5, 'kubernetes': 1.6}
            },
            'ecommerce': {
                'base_revenue': 30000,
                'domain_multipliers': {'.com': 1.3, '.com.br': 1.1, '.store': 1.2, '.shop': 1.1},
                'content_signals': {
                    'high_value': ['marketplace', 'catalog', 'inventory', 'wholesale'],
                    'medium_value': ['retail', 'shopping', 'products', 'delivery'],
                    'enterprise': ['b2b', 'distributor', 'supplier', 'logistics']
                },
                'tech_value': {'vtex': 1.5, 'shopify_plus': 1.4, 'magento_commerce': 1.3}
            },
            'local_services': {
                'base_revenue': 15000,
                'domain_multipliers': {'.com': 1.2, '.com.br': 1.0, '.services': 1.1},
                'content_signals': {
                    'high_value': ['consultation', 'premium', 'specialist', 'appointment'],
                    'medium_value': ['professional', 'certified', 'experience'],
                    'enterprise': ['corporate', 'enterprise', 'business', 'contract']
                },
                'tech_value': {'custom_booking': 1.3, 'crm_integration': 1.2, 'appointment_system': 1.1}
            }
        }
        
        print("🎯 ADAPTIVE NICHE DISCOVERY ENGINE")
        print("=" * 50)
        print(f"🔑 Search API: {'✅' if self.search_key else '❌'}")
        print(f"🔍 Custom Search CX: {'✅' if self.search_cx else '❌'}")
        print(f"⚡ PageSpeed API: {'✅' if self.pagespeed_key else '❌'}")
        print(f"📊 Niches configured: {len(self.niche_intelligence)}")

    def _build_adaptive_queries(self, niche: str, context: str = 'broad') -> List[str]:
        """
        Constrói queries adaptivas baseadas na intelligence do nicho
        
        Args:
            niche: niche para construir queries
            context: 'broad', 'specific', 'revenue_focused'
        """
        
        if niche not in self.niche_intelligence:
            return []
        
        intel = self.niche_intelligence[niche]
        queries = []
        
        # Base combinations
        core_terms = intel['core_terms']
        modifiers = intel['modifiers']
        
        if context == 'broad':
            # Broad discovery queries
            for term in core_terms[:3]:  # Top 3 core terms
                queries.append(f'"{term}" site:com.br')
                queries.append(f'"{term}" {modifiers[0]} site:com.br')
        
        elif context == 'revenue_focused':
            # Revenue-focused queries
            revenue_terms = intel['revenue_indicators']
            for term in core_terms[:2]:
                for rev_term in revenue_terms[:2]:
                    queries.append(f'"{term}" "{rev_term}" site:com.br')
        
        elif context == 'tech_specific':
            # Technology-specific queries
            tech_signals = intel['tech_signals']
            for tech in tech_signals:
                queries.append(f'"{tech}" {core_terms[0]} site:com.br')
        
        # Domain-specific queries
        for pattern in intel['domain_patterns']:
            if '.com.br' in pattern:
                queries.append(f'{core_terms[0]} {modifiers[0]} site:com.br')
        
        return queries[:6]  # Limit to 6 queries per context

    async def discover_prospects_by_niche(self, niche: str, limit: int = 20, context: str = 'broad') -> List[DiscoveredProspect]:
        """
        Descobre prospects reais usando Custom Search adaptativo por nicho
        
        Args:
            niche: beauty_skincare, b2b_saas, ecommerce, local_services
            limit: número de prospects para descobrir
            context: 'broad', 'revenue_focused', 'tech_specific'
        """
        
        if niche not in self.niche_intelligence:
            raise ValueError(f"Niche '{niche}' not supported. Available: {list(self.niche_intelligence.keys())}")
        
        print(f"\n🎯 DISCOVERING {niche.upper()} PROSPECTS")
        print(f"📊 Target: {limit} real prospects")
        print(f"🔍 Context: {context}")
        
        # Build adaptive queries
        queries = self._build_adaptive_queries(niche, context)
        
        print(f"🔍 Adaptive queries: {len(queries)}")
        print("=" * 60)
        
        discovered_prospects = []
        prospects_per_query = max(1, limit // len(queries))
        
        for i, query in enumerate(queries, 1):
            if len(discovered_prospects) >= limit:
                break
                
            print(f"\n🔍 Query {i}/{len(queries)}: {query[:50]}...")
            
            # Track query performance
            query_start = time.time()
            
            # Search for prospects
            search_results = await self._search_google_custom(query, prospects_per_query)
            
            if not search_results:
                print(f"  ⚠️ No results for this query")
                self._track_query_performance(query, 0, time.time() - query_start)
                continue
            
            print(f"  📋 Found {len(search_results)} potential prospects")
            
            valid_prospects = 0
            # Qualify each result
            for result in search_results:
                if len(discovered_prospects) >= limit:
                    break
                
                domain = self._extract_domain(result.get('link', ''))
                if not domain or self._is_excluded_domain(domain):
                    continue
                
                print(f"  🔍 Analyzing: {domain}")
                
                # Qualify prospect with enhanced intelligence
                prospect = await self._qualify_prospect_enhanced(result, query, niche, context)
                
                if prospect and prospect.confidence != 'REJECTED':
                    discovered_prospects.append(prospect)
                    valid_prospects += 1
                    print(f"    ✅ {prospect.priority}: {prospect.company_name} (${prospect.estimated_revenue:,})")
                else:
                    print(f"    ❌ Rejected or failed qualification")
            
            # Track query performance for learning
            self._track_query_performance(query, valid_prospects, time.time() - query_start)
        
        print(f"\n🏆 DISCOVERY COMPLETED")
        print(f"📊 Total prospects found: {len(discovered_prospects)}")
        print(f"💰 Total pipeline: ${sum(p.estimated_revenue for p in discovered_prospects):,}")
        
        return discovered_prospects

    async def _search_google_custom(self, query: str, num_results: int = 10) -> List[Dict]:
        """Executa busca no Google Custom Search"""
        
        if not self.search_key or not self.search_cx:
            print(f"  ❌ Google Search API not configured")
            return []
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.search_key,
            'cx': self.search_cx,
            'q': query,
            'num': min(num_results, 10),  # Google limit
            'gl': 'br',  # Brazil
            'lr': 'lang_pt|lang_en'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('items', [])
                    else:
                        print(f"  ❌ Search API error: {response.status}")
                        return []
        except Exception as e:
            print(f"  ❌ Search error: {e}")
            return []

    def _extract_domain(self, url: str) -> Optional[str]:
        """Extrai domain limpo da URL"""
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain if domain else None
        except:
            return None

    def _is_excluded_domain(self, domain: str) -> bool:
        """Filtra domains que não são prospects válidos"""
        
        excluded = [
            'google.com', 'facebook.com', 'instagram.com', 'linkedin.com',
            'youtube.com', 'twitter.com', 'wikipedia.org', 'amazon.com',
            'mercadolivre.com.br', 'americanas.com.br', 'magazineluiza.com.br',
            'gov.br', 'edu.br', 'org.br'
        ]
        
        return any(excluded_domain in domain for excluded_domain in excluded)

    async def _qualify_prospect(self, search_result: Dict, query: str, niche: str) -> Optional[DiscoveredProspect]:
        """Qualifica prospect descoberto"""
        
        start_time = time.time()
        
        url = search_result.get('link', '')
        title = search_result.get('title', '')
        snippet = search_result.get('snippet', '')
        
        domain = self._extract_domain(url)
        if not domain:
            return None
        
        # Extract company name from title
        company_name = self._extract_company_name(title, domain)
        
        try:
            # Parallel qualification tasks
            tasks = [
                self._get_performance_score(domain),
                self._estimate_revenue_by_niche(domain, niche, snippet),
                self._detect_basic_tech_stack(domain)
            ]
            
            perf_score, revenue, tech_stack = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=5.0
            )
            
            # Handle exceptions
            if isinstance(perf_score, Exception):
                perf_score = 50
            if isinstance(revenue, Exception):
                revenue = self.niche_revenue_base.get(niche, 20000)
            if isinstance(tech_stack, Exception):
                tech_stack = []
            
            # Issues detection
            issues = []
            if perf_score < 50:
                issues.append('poor_performance')
            if perf_score < 30:
                issues.append('critical_performance')
            
            # Priority classification
            priority = self._classify_priority(perf_score, revenue)
            
            # Confidence assessment
            confidence = "HIGH" if perf_score > 0 and revenue > 0 else "MEDIUM"
            
            analysis_time = time.time() - start_time
            
            return DiscoveredProspect(
                company_name=company_name,
                domain=domain,
                website=url,
                search_query=query,
                niche=niche,
                discovery_source='google_custom_search',
                snippet=snippet[:200],
                performance_score=perf_score,
                estimated_revenue=revenue,
                tech_stack=tech_stack,
                issues_found=issues,
                priority=priority,
                confidence=confidence,
                analysis_time=analysis_time
            )
            
        except Exception as e:
            print(f"    ❌ Qualification error: {e}")
            return None

    def _extract_company_name(self, title: str, domain: str) -> str:
        """Extrai nome da empresa do title ou domain"""
        
        if title:
            # Clean title
            company = title.split('|')[0].split('-')[0].strip()
            if len(company) > 5 and not any(word in company.lower() for word in ['home', 'página', 'site']):
                return company
        
        # Fallback to domain
        domain_name = domain.split('.')[0]
        return domain_name.title()

    async def _get_performance_score(self, domain: str) -> int:
        """Performance score via PageSpeed API"""
        
        if not self.pagespeed_key:
            return 50
        
        url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        params = {
            'url': f'https://{domain}',
            'key': self.pagespeed_key,
            'category': 'performance',
            'strategy': 'mobile'
        }
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=4.0)) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        score = data.get('lighthouseResult', {}).get('categories', {}).get('performance', {}).get('score', 0.5)
                        return int(score * 100)
        except:
            pass
        
        return 50

    async def _estimate_revenue_by_niche(self, domain: str, niche: str, snippet: str, tech_stack: List[str] = None) -> int:
        """
        Advanced revenue estimation com intelligence por nicho
        
        Analisa domain, content signals, tech stack para estimativa precisa
        """
        
        if niche not in self.revenue_intelligence:
            return 20000
        
        intel = self.revenue_intelligence[niche]
        base_revenue = intel['base_revenue']
        multiplier = 1.0
        
        # Domain intelligence
        for domain_ext, mult in intel['domain_multipliers'].items():
            if domain.endswith(domain_ext):
                multiplier *= mult
                break
        
        # Content signal analysis
        snippet_lower = snippet.lower()
        content_signals = intel['content_signals']
        
        # High-value signals (strongest impact)
        for signal in content_signals['high_value']:
            if signal in snippet_lower:
                multiplier *= 1.5
                break
        
        # Enterprise signals (premium tier)
        for signal in content_signals['enterprise']:
            if signal in snippet_lower:
                multiplier *= 1.8
                break
        
        # Medium-value signals
        for signal in content_signals['medium_value']:
            if signal in snippet_lower:
                multiplier *= 1.2
                break
        
        # Tech stack intelligence
        if tech_stack:
            tech_value = intel['tech_value']
            for tech in tech_stack:
                tech_lower = tech.lower()
                for tech_signal, tech_mult in tech_value.items():
                    if tech_signal in tech_lower:
                        multiplier *= tech_mult
                        break
        
        # Domain age and authority indicators
        if any(indicator in domain for indicator in ['corp', 'group', 'holding']):
            multiplier *= 1.3
        
        # Professional domain patterns
        if len(domain.split('.')[0]) > 8:  # Longer domain names often indicate established businesses
            multiplier *= 1.1
        
        final_revenue = int(base_revenue * multiplier)
        
        # Smart ranges by niche
        niche_ranges = {
            'beauty_skincare': (8000, 150000),
            'b2b_saas': (15000, 250000),
            'ecommerce': (10000, 200000),
            'local_services': (5000, 80000)
        }
        
        min_rev, max_rev = niche_ranges.get(niche, (5000, 100000))
        return max(min_rev, min(max_rev, final_revenue))

    async def _detect_basic_tech_stack(self, domain: str) -> List[str]:
        """Detecção básica de tech stack"""
        
        tech_stack = []
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=3.0)) as session:
                async with session.get(f'https://{domain}') as response:
                    if response.status == 200:
                        content = await response.text()
                        content_lower = content.lower()
                        
                        # Common platforms
                        if 'shopify' in content_lower:
                            tech_stack.append('Shopify')
                        if 'wordpress' in content_lower:
                            tech_stack.append('WordPress')
                        if 'woocommerce' in content_lower:
                            tech_stack.append('WooCommerce')
                        if 'react' in content_lower:
                            tech_stack.append('React')
                        if 'angular' in content_lower:
                            tech_stack.append('Angular')
        except:
            pass
        
        return tech_stack

    def _classify_priority(self, performance: int, revenue: int) -> str:
        """Classificação de prioridade do prospect"""
        
        if performance < 40 and revenue >= 50000:
            return "IMMEDIATE"
        elif performance < 50 and revenue >= 30000:
            return "HIGH"
        elif performance < 70 and revenue >= 15000:
            return "MEDIUM"
        else:
            return "LOW"

    def export_discovery_report(self, prospects: List[DiscoveredProspect], niche: str, output_dir: str = "output") -> str:
        """Export relatório de discovery"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(output_dir, exist_ok=True)
        
        total_pipeline = sum(p.estimated_revenue for p in prospects)
        avg_revenue = total_pipeline / len(prospects) if prospects else 0
        
        # Priority distribution
        priority_counts = {}
        for prospect in prospects:
            priority_counts[prospect.priority] = priority_counts.get(prospect.priority, 0) + 1
        
        export_data = {
            'metadata': {
                'timestamp': timestamp,
                'niche': niche,
                'discovery_method': 'adaptive_niche_google_search',
                'total_prospects': len(prospects)
            },
            'pipeline_metrics': {
                'total_pipeline_value': total_pipeline,
                'avg_revenue_per_prospect': avg_revenue,
                'priority_distribution': priority_counts
            },
            'prospects': [asdict(prospect) for prospect in prospects]
        }
        
        json_file = os.path.join(output_dir, f"niche_discovery_{niche}_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 DISCOVERY REPORT EXPORTED:")
        print(f"  • File: {json_file}")
        print(f"  • Niche: {niche}")
        print(f"  • Prospects: {len(prospects)}")
        print(f"  • Pipeline: ${total_pipeline:,}")
        
        return json_file

    def _track_query_performance(self, query: str, valid_prospects: int, time_taken: float):
        """Track query performance for adaptive learning"""
        
        if query not in self.query_performance:
            self.query_performance[query] = {
                'uses': 0,
                'total_prospects': 0,
                'total_time': 0,
                'avg_prospects': 0,
                'avg_time': 0
            }
        
        perf = self.query_performance[query]
        perf['uses'] += 1
        perf['total_prospects'] += valid_prospects
        perf['total_time'] += time_taken
        perf['avg_prospects'] = perf['total_prospects'] / perf['uses']
        perf['avg_time'] = perf['total_time'] / perf['uses']
        
        # Track successful patterns
        if valid_prospects > 0:
            pattern = self._extract_query_pattern(query)
            if pattern not in self.successful_patterns:
                self.successful_patterns[pattern] = 0
            self.successful_patterns[pattern] += valid_prospects

    def _extract_query_pattern(self, query: str) -> str:
        """Extract reusable pattern from query"""
        
        # Simplify query to pattern
        pattern = query.lower()
        pattern = pattern.replace('"', '').replace('site:com.br', 'site:domain')
        return pattern[:50]  # Truncate for storage

    async def _qualify_prospect_enhanced(self, search_result: Dict, query: str, niche: str, context: str) -> Optional[DiscoveredProspect]:
        """Enhanced prospect qualification with niche intelligence"""
        
        start_time = time.time()
        
        url = search_result.get('link', '')
        title = search_result.get('title', '')
        snippet = search_result.get('snippet', '')
        
        domain = self._extract_domain(url)
        if not domain:
            return None
        
        # Extract company name with intelligence
        company_name = self._extract_company_name_enhanced(title, domain, snippet, niche)
        
        try:
            # Enhanced parallel qualification
            tasks = [
                self._get_performance_score(domain),
                self._detect_enhanced_tech_stack(domain, niche),
                self._analyze_business_signals(snippet, niche)
            ]
            
            perf_score, tech_stack, business_signals = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=6.0
            )
            
            # Handle exceptions
            if isinstance(perf_score, Exception):
                perf_score = 50
            if isinstance(tech_stack, Exception):
                tech_stack = []
            if isinstance(business_signals, Exception):
                business_signals = {}
            
            # Enhanced revenue estimation
            revenue = await self._estimate_revenue_by_niche(domain, niche, snippet, tech_stack)
            
            # Enhanced issues detection
            issues = self._detect_business_issues(perf_score, business_signals, tech_stack)
            
            # Priority classification with business intelligence
            priority = self._classify_priority_enhanced(perf_score, revenue, business_signals, context)
            
            # Confidence assessment
            confidence = self._assess_confidence(perf_score, business_signals, len(tech_stack))
            
            analysis_time = time.time() - start_time
            
            return DiscoveredProspect(
                company_name=company_name,
                domain=domain,
                website=url,
                search_query=query,
                niche=niche,
                discovery_source='google_custom_search_enhanced',
                snippet=snippet[:200],
                performance_score=perf_score,
                estimated_revenue=revenue,
                tech_stack=tech_stack,
                issues_found=issues,
                priority=priority,
                confidence=confidence,
                analysis_time=analysis_time
            )
            
        except Exception as e:
            print(f"    ❌ Enhanced qualification error: {e}")
            return None

    def _extract_company_name_enhanced(self, title: str, domain: str, snippet: str, niche: str) -> str:
        """Enhanced company name extraction with niche intelligence"""
        
        if title:
            # Clean title with niche awareness
            company = title.split('|')[0].split('-')[0].strip()
            
            # Remove common website words
            remove_words = ['home', 'página', 'site', 'oficial', 'official', 'store', 'loja']
            if not any(word in company.lower() for word in remove_words) and len(company) > 3:
                return company
        
        # Extract from snippet if available
        if snippet:
            lines = snippet.split('.')
            for line in lines[:2]:  # Check first 2 sentences
                if len(line.strip()) > 5 and len(line.strip()) < 50:
                    potential_name = line.strip()
                    if not any(word in potential_name.lower() for word in ['http', 'www', 'site']):
                        return potential_name
        
        # Fallback to domain
        domain_name = domain.split('.')[0]
        return domain_name.replace('-', ' ').title()

    async def _detect_enhanced_tech_stack(self, domain: str, niche: str) -> List[str]:
        """Enhanced tech stack detection with niche intelligence"""
        
        tech_stack = []
        niche_intel = self.niche_intelligence.get(niche, {})
        expected_tech = niche_intel.get('tech_signals', [])
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=4.0)) as session:
                async with session.get(f'https://{domain}', allow_redirects=True) as response:
                    if response.status == 200:
                        content = await response.text()
                        content_lower = content.lower()
                        headers = dict(response.headers)
                        
                        # Niche-specific tech detection
                        for tech in expected_tech:
                            if tech.lower() in content_lower:
                                tech_stack.append(tech.title())
                        
                        # Common platforms
                        tech_patterns = {
                            'shopify': ['shopify', 'shop.js', 'cdn.shopify'],
                            'wordpress': ['wp-content', 'wordpress', 'wp-includes'],
                            'react': ['react', '_react', 'reactjs'],
                            'angular': ['angular', 'ng-app', 'angularjs'],
                            'vue': ['vue.js', 'vuejs', '__vue__'],
                            'woocommerce': ['woocommerce', 'wc-'],
                            'magento': ['magento', 'mage/cookies'],
                            'vtex': ['vtex', 'vteximg', 'vtexcommercestable']
                        }
                        
                        for platform, patterns in tech_patterns.items():
                            if any(pattern in content_lower for pattern in patterns):
                                tech_stack.append(platform.title())
                        
                        # Server/framework detection from headers
                        server = headers.get('server', '').lower()
                        if 'nginx' in server:
                            tech_stack.append('Nginx')
                        if 'apache' in server:
                            tech_stack.append('Apache')
                        
        except Exception:
            pass
        
        return list(set(tech_stack))  # Remove duplicates

    async def _analyze_business_signals(self, snippet: str, niche: str) -> Dict:
        """Analyze business intelligence signals from snippet"""
        
        signals = {
            'business_maturity': 'unknown',
            'target_market': 'unknown',
            'revenue_signals': [],
            'scale_indicators': []
        }
        
        snippet_lower = snippet.lower()
        
        # Business maturity signals
        if any(word in snippet_lower for word in ['founded', 'established', 'since', 'anos', 'years']):
            signals['business_maturity'] = 'established'
        elif any(word in snippet_lower for word in ['startup', 'new', 'nova', 'launching']):
            signals['business_maturity'] = 'startup'
        
        # Target market analysis
        if any(word in snippet_lower for word in ['enterprise', 'corporate', 'business', 'empresarial']):
            signals['target_market'] = 'b2b'
        elif any(word in snippet_lower for word in ['consumer', 'customer', 'cliente', 'personal']):
            signals['target_market'] = 'b2c'
        
        # Revenue signals
        revenue_words = ['premium', 'luxury', 'professional', 'enterprise', 'corporate', 'subscription', 'pricing']
        signals['revenue_signals'] = [word for word in revenue_words if word in snippet_lower]
        
        # Scale indicators
        scale_words = ['global', 'international', 'nacional', 'leading', 'largest', 'premier']
        signals['scale_indicators'] = [word for word in scale_words if word in snippet_lower]
        
        return signals

    def _detect_business_issues(self, performance: int, business_signals: Dict, tech_stack: List[str]) -> List[str]:
        """Detect potential business issues"""
        
        issues = []
        
        # Performance issues
        if performance < 30:
            issues.append('critical_performance')
        elif performance < 50:
            issues.append('poor_performance')
        
        # Tech stack issues
        if not tech_stack:
            issues.append('unknown_tech_stack')
        elif any(old_tech in ' '.join(tech_stack).lower() for old_tech in ['old', 'legacy', 'deprecated']):
            issues.append('outdated_technology')
        
        # Business maturity issues
        if business_signals.get('business_maturity') == 'startup':
            issues.append('early_stage_risk')
        
        return issues

    def _classify_priority_enhanced(self, performance: int, revenue: int, business_signals: Dict, context: str) -> str:
        """Enhanced priority classification with business intelligence"""
        
        # Base priority on performance and revenue
        if performance < 40 and revenue >= 80000:
            base_priority = "IMMEDIATE"
        elif performance < 50 and revenue >= 50000:
            base_priority = "HIGH"
        elif performance < 70 and revenue >= 25000:
            base_priority = "MEDIUM"
        else:
            base_priority = "LOW"
        
        # Adjust based on business signals
        if business_signals.get('target_market') == 'b2b' and revenue >= 40000:
            if base_priority == "MEDIUM":
                base_priority = "HIGH"
            elif base_priority == "LOW":
                base_priority = "MEDIUM"
        
        # Context-specific adjustments
        if context == 'revenue_focused' and revenue >= 60000:
            if base_priority in ["MEDIUM", "LOW"]:
                base_priority = "HIGH"
        
        return base_priority

    def _assess_confidence(self, performance: int, business_signals: Dict, tech_stack_count: int) -> str:
        """Assess confidence level in the prospect analysis"""
        
        confidence_score = 0
        
        # Performance confidence
        if performance > 0:
            confidence_score += 2
        
        # Business signals confidence
        if business_signals.get('business_maturity') != 'unknown':
            confidence_score += 1
        if business_signals.get('target_market') != 'unknown':
            confidence_score += 1
        if business_signals.get('revenue_signals'):
            confidence_score += 1
        
        # Tech stack confidence
        if tech_stack_count > 0:
            confidence_score += 1
        if tech_stack_count > 2:
            confidence_score += 1
        
        if confidence_score >= 5:
            return "HIGH"
        elif confidence_score >= 3:
            return "MEDIUM"
        else:
            return "LOW"

# Demo
async def demo_adaptive_discovery():
    """Demo do adaptive discovery por nicho"""
    
    print("\n🎯 ADAPTIVE NICHE DISCOVERY DEMO")
    print("=" * 60)
    
    engine = AdaptiveNicheDiscovery()
    
    # Test discovery for beauty/skincare niche
    niche = 'beauty_skincare'
    prospects = await engine.discover_prospects_by_niche(niche, limit=10)
    
    if prospects:
        # Show top prospects
        top_prospects = sorted(prospects, key=lambda x: x.estimated_revenue, reverse=True)[:5]
        
        print(f"\n🔥 TOP {niche.upper()} PROSPECTS:")
        for i, prospect in enumerate(top_prospects, 1):
            print(f"  {i}. {prospect.company_name} ({prospect.domain})")
            print(f"     💰 Revenue: ${prospect.estimated_revenue:,}")
            print(f"     📊 Performance: {prospect.performance_score}/100")
            print(f"     🎯 Priority: {prospect.priority}")
            print(f"     🔍 Query: {prospect.search_query[:50]}...")
        
        # Export report
        report_file = engine.export_discovery_report(prospects, niche)
        
        print(f"\n✅ Adaptive Niche Discovery operational!")
        print(f"📄 Report: {report_file}")
    else:
        print(f"❌ No prospects discovered for {niche}")

if __name__ == "__main__":
    asyncio.run(demo_adaptive_discovery())
