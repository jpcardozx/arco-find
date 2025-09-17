#!/usr/bin/env python3
"""
🎯 ICP-ALIGNED PROSPECT DISCOVERY ENGINE
Foco EXCLUSIVO nos ICPs reais definidos - SEM OVERENGINEERING

ICPs REAIS:
- P1: Growth E-commerce ($500k-3M/ano)  
- P2: Nicho DTC 1-3M (Shopify + GA4 + ≥8 apps)
- P3: Serviços Profissionais ($300k-1M/ano)
- P4: Early SaaS Bootstrapped (MRR $5-50k)

CORRIGE: Total desalinhamento com prospects reais
"""

import os
import json
import asyncio
import aiohttp
import re
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import random

@dataclass 
class ICPProspect:
    """Prospect qualificado dentro do ICP"""
    domain: str
    company_name: str
    icp_type: str
    estimated_revenue: int
    confidence_score: int
    pain_points: List[str]
    discovered_via: str
    contact_info: Dict

class ICPAlignedDiscovery:
    """
    Discovery engine focado EXCLUSIVAMENTE nos ICPs reais
    
    ELIMINA: Overengineering e prospects irrelevantes
    FOCA: Prospects que realmente compram nossos serviços
    """
    
    def __init__(self):
        # ICP Configurations (baseado nos ICPs reais documentados)
        self.icp_configs = {
            'P1_growth_ecommerce': {
                'name': 'Growth E-commerce',
                'revenue_range': (500000, 3000000),
                'platforms': ['shopify', 'woocommerce', 'magento'],
                'employee_range': (5, 50),
                'pain_indicators': [
                    'checkout abandonment', 'mobile performance', 'conversion rate',
                    'cart abandonment', 'page speed', 'user experience'
                ],
                'positive_signals': [
                    'online store', 'ecommerce', 'shop', 'buy now', 'add to cart',
                    'shipping', 'checkout', 'product catalog'
                ],
                'discovery_keywords': [
                    'ecommerce', 'online retail', 'dtc brand', 'shopify store',
                    'online shop', 'e-commerce business'
                ]
            },
            'P2_dtc_niche': {
                'name': 'Nicho DTC',
                'revenue_range': (1000000, 3000000),
                'platforms': ['shopify'],
                'min_apps': 8,
                'employee_range': (10, 75),
                'pain_indicators': [
                    'subscription management', 'customer retention', 'inventory sync',
                    'multi-channel', 'attribution tracking'
                ],
                'positive_signals': [
                    'direct to consumer', 'dtc brand', 'subscription', 'member',
                    'exclusive', 'premium', 'artisan', 'handcrafted'
                ],
                'discovery_keywords': [
                    'dtc', 'direct consumer', 'subscription box', 'premium brand',
                    'artisan', 'handcrafted', 'sustainable'
                ]
            },
            'P3_professional_services': {
                'name': 'Serviços Profissionais',
                'revenue_range': (300000, 1000000),
                'platforms': ['wordpress', 'custom', 'squarespace'],
                'employee_range': (3, 25),
                'pain_indicators': [
                    'lead generation', 'client management', 'appointment booking',
                    'project tracking', 'billing automation'
                ],
                'positive_signals': [
                    'consulting', 'law firm', 'accounting', 'legal services',
                    'professional services', 'expertise', 'consultation'
                ],
                'discovery_keywords': [
                    'law firm', 'legal services', 'consulting', 'accounting',
                    'professional services', 'advisory', 'expertise'
                ]
            },
            'P4_early_saas': {
                'name': 'Early SaaS Bootstrapped',
                'mrr_range': (5000, 50000),
                'employee_range': (2, 15),
                'pain_indicators': [
                    'user onboarding', 'churn reduction', 'manual processes',
                    'scaling', 'automation', 'customer support'
                ],
                'positive_signals': [
                    'saas', 'software', 'platform', 'dashboard', 'api',
                    'subscription', 'free trial', 'demo'
                ],
                'discovery_keywords': [
                    'saas platform', 'software solution', 'b2b software',
                    'business software', 'productivity tool'
                ]
            }
        }
        
        # Sample prospect databases (em produção, usar APIs reais)
        self.sample_prospects = self._load_sample_prospect_database()
        
        print("🎯 ICP-ALIGNED DISCOVERY ENGINE")
        print("=" * 50)
        print(f"📋 ICPs configurados: {len(self.icp_configs)}")
        print(f"🎯 Prospect database: {len(self.sample_prospects)} samples")
        print("✅ Focado EXCLUSIVAMENTE nos ICPs reais")

    def _load_sample_prospect_database(self) -> Dict[str, List[str]]:
        """
        Sample prospect database por ICP
        
        EM PRODUÇÃO: Substituir por discovery APIs reais
        - Shopify App Store scraping para P1/P2
        - Professional directories para P3  
        - Indie Hackers/SaaS directories para P4
        """
        
        return {
            'P1_growth_ecommerce': [
                'beautifulbites.com',
                'premiumskincare.co',
                'activewearplus.com', 
                'organicbaby.store',
                'luxuryhome.shop',
                'fitnessgear.online',
                'sustainablefashion.co',
                'artisancoffee.com',
                'wellness-store.com',
                'outdoorgearshop.com'
            ],
            'P2_dtc_niche': [
                'subscriptionbox.co',
                'premiumskincare.com',
                'artisanfoods.co',
                'curated-lifestyle.com',
                'exclusive-wellness.co',
                'luxury-skincare.store',
                'gourmet-subscription.com',
                'premium-supplements.co',
                'handcrafted-goods.com',
                'sustainable-beauty.co'
            ],
            'P3_professional_services': [
                'smithlegal.com',
                'modernaccounting.co',
                'businessconsulting.pro',
                'familylaw.expert',
                'taxadvisory.com',
                'legalpartners.pro',
                'cpa-services.com',
                'consulting-group.co',
                'advisory-services.pro',
                'professional-law.com'
            ],
            'P4_early_saas': [
                'projectmanager.io',
                'teamcollaboration.app',
                'invoice-automation.co',
                'customer-insights.io',
                'workflow-optimizer.com',
                'data-visualization.app',
                'productivity-suite.io',
                'business-analytics.co',
                'team-dashboard.app',
                'process-automation.io'
            ]
        }

    async def discover_icp_prospects(self, icp_type: str, target_count: int = 50) -> List[ICPProspect]:
        """
        Descobre prospects reais alinhados com o ICP especificado
        
        ELIMINA: Generic discovery que não bate com nossos ICPs
        IMPLEMENTA: Discovery direcionado para clientes reais
        """
        
        if icp_type not in self.icp_configs:
            raise ValueError(f"ICP {icp_type} não definido. Opções: {list(self.icp_configs.keys())}")
        
        print(f"\n🔍 DESCOBRINDO PROSPECTS: {icp_type}")
        print(f"🎯 Target: {target_count} prospects qualificados")
        
        icp_config = self.icp_configs[icp_type]
        discovered_prospects = []
        
        # Get sample domains for this ICP
        sample_domains = self.sample_prospects.get(icp_type, [])
        
        # Em produção: implementar discovery real por fonte
        if icp_type in ['P1_growth_ecommerce', 'P2_dtc_niche']:
            prospects = await self._discover_ecommerce_prospects(icp_config, sample_domains, target_count)
        elif icp_type == 'P3_professional_services':
            prospects = await self._discover_professional_services(icp_config, sample_domains, target_count)
        elif icp_type == 'P4_early_saas':
            prospects = await self._discover_early_saas(icp_config, sample_domains, target_count)
        else:
            prospects = []
        
        # Qualify discovered prospects
        qualified_prospects = []
        for prospect_domain in prospects[:target_count * 2]:  # Discover 2x to filter down
            prospect = await self._qualify_prospect(prospect_domain, icp_type, icp_config)
            if prospect and prospect.confidence_score >= 70:
                qualified_prospects.append(prospect)
                
        print(f"✅ Discovered {len(qualified_prospects)} qualified prospects")
        return qualified_prospects[:target_count]

    async def _discover_ecommerce_prospects(self, icp_config: Dict, sample_domains: List[str], 
                                          target_count: int) -> List[str]:
        """
        Discovery especializado para prospects de e-commerce
        
        EM PRODUÇÃO: 
        - Shopify App Store API
        - BuiltWith e-commerce database
        - SimilarWeb competitive analysis
        """
        
        print("   🛒 E-commerce discovery via multiple sources...")
        
        # Simulate real discovery sources
        discovered_domains = []
        
        # Source 1: Sample database (replace with Shopify App Store API)
        discovered_domains.extend(sample_domains[:target_count // 2])
        
        # Source 2: Competitive analysis (replace with SimilarWeb API)
        competitive_domains = [
            f"competitor-{i}.store" for i in range(1, target_count // 2 + 1)
        ]
        discovered_domains.extend(competitive_domains)
        
        print(f"   ✅ E-commerce sources: {len(discovered_domains)} domains found")
        return discovered_domains

    async def _discover_professional_services(self, icp_config: Dict, sample_domains: List[str],
                                            target_count: int) -> List[str]:
        """
        Discovery especializado para serviços profissionais
        
        EM PRODUÇÃO:
        - Legal directories (Martindale, Avvo)
        - Professional association listings
        - Local business directories
        """
        
        print("   ⚖️ Professional services discovery...")
        
        # Simulate professional services discovery
        discovered_domains = []
        
        # Source 1: Professional directories
        discovered_domains.extend(sample_domains[:target_count // 2])
        
        # Source 2: Association listings
        association_domains = [
            f"legal-firm-{i}.com" for i in range(1, target_count // 2 + 1)
        ]
        discovered_domains.extend(association_domains)
        
        print(f"   ✅ Professional services: {len(discovered_domains)} domains found")
        return discovered_domains

    async def _discover_early_saas(self, icp_config: Dict, sample_domains: List[str],
                                 target_count: int) -> List[str]:
        """
        Discovery especializado para early-stage SaaS
        
        EM PRODUÇÃO:
        - Indie Hackers directory
        - Product Hunt launches
        - AngelList startups
        - MicroConf directory
        """
        
        print("   💻 Early SaaS discovery...")
        
        # Simulate SaaS discovery
        discovered_domains = []
        
        # Source 1: Indie Hackers style discovery
        discovered_domains.extend(sample_domains[:target_count // 2])
        
        # Source 2: Startup directories
        startup_domains = [
            f"saas-startup-{i}.io" for i in range(1, target_count // 2 + 1)
        ]
        discovered_domains.extend(startup_domains)
        
        print(f"   ✅ Early SaaS: {len(discovered_domains)} domains found")
        return discovered_domains

    async def _qualify_prospect(self, domain: str, icp_type: str, icp_config: Dict) -> Optional[ICPProspect]:
        """
        Qualifica prospect simples e direcionado (SEM OVERENGINEERING)
        
        FOCA: Essentials que determinam fit com ICP
        ELIMINA: Analysis desnecessário que não afeta qualification
        """
        
        try:
            # Basic website analysis
            website_data = await self._analyze_website_basic(domain)
            if not website_data:
                return None
            
            # Check ICP fit
            icp_fit = self._check_icp_fit(website_data, icp_config)
            if icp_fit['score'] < 70:
                return None
            
            # Extract company info
            company_name = self._extract_company_name(website_data, domain)
            
            # Estimate revenue (simplified)
            revenue_estimate = self._estimate_revenue_simple(website_data, icp_config)
            
            # Detect pain points (ICP-specific)
            pain_points = self._detect_icp_pain_points(website_data, icp_config)
            
            # Extract basic contact info
            contact_info = self._extract_contact_info(website_data)
            
            return ICPProspect(
                domain=domain,
                company_name=company_name,
                icp_type=icp_type,
                estimated_revenue=revenue_estimate,
                confidence_score=icp_fit['score'],
                pain_points=pain_points,
                discovered_via=icp_fit['signals'],
                contact_info=contact_info
            )
            
        except Exception as e:
            print(f"   ❌ Error qualifying {domain}: {e}")
            return None

    async def _analyze_website_basic(self, domain: str) -> Optional[Dict]:
        """
        Análise básica do website - SIMPLIFICADA
        
        FOCA: Info essencial para ICP qualification
        ELIMINA: Deep analysis desnecessário
        """
        
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f'https://{domain}') as response:
                    if response.status == 200:
                        content = await response.text()
                        return {
                            'url': f'https://{domain}',
                            'title': self._extract_title(content),
                            'content': content[:10000],  # First 10k chars only
                            'meta_description': self._extract_meta_description(content),
                            'status_code': response.status
                        }
        except Exception as e:
            print(f"   ⚠️ Could not analyze {domain}: {e}")
            return None

    def _check_icp_fit(self, website_data: Dict, icp_config: Dict) -> Dict:
        """
        Check fit com ICP específico - DIRETO AO PONTO
        
        ELIMINA: Complex scoring algorithms
        IMPLEMENTA: Simple but effective ICP matching
        """
        
        content = website_data['content'].lower()
        title = website_data.get('title', '').lower()
        meta = website_data.get('meta_description', '').lower()
        
        full_text = f"{title} {meta} {content}"
        
        score = 0
        signals = []
        
        # Check positive signals for this ICP
        positive_signals = icp_config.get('positive_signals', [])
        for signal in positive_signals:
            if signal in full_text:
                score += 15
                signals.append(signal)
        
        # Check platform indicators
        platforms = icp_config.get('platforms', [])
        for platform in platforms:
            if platform in full_text:
                score += 20
                signals.append(f"platform_{platform}")
        
        # Check pain indicators (shows they need our help)
        pain_indicators = icp_config.get('pain_indicators', [])
        for pain in pain_indicators:
            if pain in full_text:
                score += 10
                signals.append(f"pain_{pain}")
        
        # Business model specific checks
        if 'ecommerce' in icp_config['name'].lower():
            ecommerce_indicators = ['shop', 'store', 'buy', 'cart', 'checkout', 'products']
            ecommerce_score = sum(5 for indicator in ecommerce_indicators if indicator in full_text)
            score += ecommerce_score
            
        elif 'saas' in icp_config['name'].lower():
            saas_indicators = ['software', 'platform', 'api', 'dashboard', 'subscription']
            saas_score = sum(8 for indicator in saas_indicators if indicator in full_text)
            score += saas_score
            
        elif 'professional' in icp_config['name'].lower():
            professional_indicators = ['services', 'consulting', 'legal', 'expert', 'professional']
            professional_score = sum(6 for indicator in professional_indicators if indicator in full_text)
            score += professional_score
        
        return {
            'score': min(score, 100),
            'signals': ', '.join(signals[:5])  # Top 5 signals
        }

    def _estimate_revenue_simple(self, website_data: Dict, icp_config: Dict) -> int:
        """
        Revenue estimation SIMPLIFICADA e realista
        
        ELIMINA: Complex algorithms com APIs caras
        IMPLEMENTA: Heuristics baseadas no ICP
        """
        
        content = website_data['content'].lower()
        
        # Base revenue by ICP type
        if 'ecommerce' in icp_config['name'].lower():
            base_revenue = 800000  # Median for growth e-commerce
        elif 'dtc' in icp_config['name'].lower():
            base_revenue = 1500000  # DTC niche typically higher
        elif 'professional' in icp_config['name'].lower():
            base_revenue = 500000  # Professional services median
        elif 'saas' in icp_config['name'].lower():
            base_revenue = 300000  # Early SaaS (MRR * 12)
        else:
            base_revenue = 600000
        
        # Simple revenue indicators
        multiplier = 1.0
        
        # Size indicators
        if any(term in content for term in ['team', 'employees', 'staff']):
            multiplier *= 1.2
        
        # Growth indicators  
        if any(term in content for term in ['growing', 'expanding', 'scaling']):
            multiplier *= 1.3
        
        # Sophistication indicators
        if any(term in content for term in ['enterprise', 'professional', 'premium']):
            multiplier *= 1.4
        
        # Technology indicators
        if any(term in content for term in ['api', 'integration', 'automation']):
            multiplier *= 1.1
        
        estimated_revenue = int(base_revenue * multiplier)
        
        # Clamp to ICP range
        revenue_range = icp_config.get('revenue_range', (0, 10000000))
        return max(revenue_range[0], min(estimated_revenue, revenue_range[1]))

    def _detect_icp_pain_points(self, website_data: Dict, icp_config: Dict) -> List[str]:
        """
        Detecção de pain points específicos do ICP
        
        FOCA: Pain points que nossos serviços resolvem
        ELIMINA: Generic pain points irrelevantes
        """
        
        content = website_data['content'].lower()
        pain_indicators = icp_config.get('pain_indicators', [])
        detected_pains = []
        
        for pain_indicator in pain_indicators:
            # Check for pain point mentions
            pain_keywords = pain_indicator.split()
            if any(keyword in content for keyword in pain_keywords):
                detected_pains.append(pain_indicator)
        
        # Add implicit pain points by business type
        business_type = icp_config['name'].lower()
        
        if 'ecommerce' in business_type:
            # Check for e-commerce specific issues
            if 'mobile' in content and 'slow' in content:
                detected_pains.append('mobile_performance')
            if 'cart' in content and ('abandon' in content or 'drop' in content):
                detected_pains.append('cart_abandonment')
                
        elif 'saas' in business_type:
            # Check for SaaS specific issues
            if 'manual' in content or 'time-consuming' in content:
                detected_pains.append('manual_processes')
            if 'support' in content and ('overwhelmed' in content or 'busy' in content):
                detected_pains.append('customer_support_scaling')
                
        elif 'professional' in business_type:
            # Check for professional services issues
            if 'leads' in content and ('finding' in content or 'generating' in content):
                detected_pains.append('lead_generation')
            if 'clients' in content and ('managing' in content or 'tracking' in content):
                detected_pains.append('client_management')
        
        return detected_pains[:3]  # Max 3 pain points

    def _extract_company_name(self, website_data: Dict, domain: str) -> str:
        """Extract company name from website"""
        
        title = website_data.get('title', '')
        
        if title:
            # Clean up title to get company name
            clean_title = title.split('|')[0].split('-')[0].strip()
            if len(clean_title) > 3 and len(clean_title) < 50:
                return clean_title
        
        # Fallback to domain
        return domain.split('.')[0].replace('-', ' ').title()

    def _extract_contact_info(self, website_data: Dict) -> Dict:
        """Extract basic contact information"""
        
        content = website_data['content']
        
        contact_info = {
            'has_contact_page': 'contact' in content.lower(),
            'has_phone': bool(re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', content)),
            'has_email': bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)),
            'social_media': {}
        }
        
        # Social media detection
        if 'linkedin.com' in content:
            contact_info['social_media']['linkedin'] = True
        if 'twitter.com' in content or 'x.com' in content:
            contact_info['social_media']['twitter'] = True
        if 'facebook.com' in content:
            contact_info['social_media']['facebook'] = True
        
        return contact_info

    def _extract_title(self, content: str) -> str:
        """Extract page title"""
        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        return title_match.group(1) if title_match else ''

    def _extract_meta_description(self, content: str) -> str:
        """Extract meta description"""
        meta_match = re.search(r'<meta\s+name="description"\s+content="(.*?)"', content, re.IGNORECASE)
        return meta_match.group(1) if meta_match else ''

    async def generate_discovery_report(self, prospects: List[ICPProspect]) -> Dict:
        """
        Gera relatório de discovery focado em AÇÃO
        
        ELIMINA: Metrics irrelevantes
        FOCA: Info que ajuda vendas/outreach
        """
        
        if not prospects:
            return {'error': 'No prospects discovered'}
        
        # Group by ICP type
        by_icp = {}
        for prospect in prospects:
            if prospect.icp_type not in by_icp:
                by_icp[prospect.icp_type] = []
            by_icp[prospect.icp_type].append(prospect)
        
        # Calculate key metrics
        total_prospects = len(prospects)
        avg_confidence = sum(p.confidence_score for p in prospects) / total_prospects
        avg_revenue = sum(p.estimated_revenue for p in prospects) / total_prospects
        
        # Most common pain points
        all_pain_points = []
        for prospect in prospects:
            all_pain_points.extend(prospect.pain_points)
        
        pain_point_counts = {}
        for pain in all_pain_points:
            pain_point_counts[pain] = pain_point_counts.get(pain, 0) + 1
        
        top_pain_points = sorted(pain_point_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Ready-to-contact prospects (high confidence + contact info)
        ready_to_contact = [
            p for p in prospects 
            if p.confidence_score >= 80 and (
                p.contact_info.get('has_contact_page') or 
                p.contact_info.get('has_email')
            )
        ]
        
        report = {
            'summary': {
                'total_prospects_discovered': total_prospects,
                'average_confidence_score': avg_confidence,
                'average_estimated_revenue': avg_revenue,
                'ready_to_contact': len(ready_to_contact),
                'discovery_date': datetime.now().isoformat()
            },
            'icp_breakdown': {
                icp_type: {
                    'count': len(prospects_list),
                    'avg_confidence': sum(p.confidence_score for p in prospects_list) / len(prospects_list),
                    'avg_revenue': sum(p.estimated_revenue for p in prospects_list) / len(prospects_list)
                }
                for icp_type, prospects_list in by_icp.items()
            },
            'top_pain_points': [
                {'pain_point': pain, 'prospect_count': count}
                for pain, count in top_pain_points
            ],
            'immediate_action_prospects': [
                {
                    'company_name': p.company_name,
                    'domain': p.domain,
                    'icp_type': p.icp_type,
                    'confidence_score': p.confidence_score,
                    'estimated_revenue': p.estimated_revenue,
                    'top_pain_points': p.pain_points[:2],
                    'contact_available': p.contact_info.get('has_contact_page', False)
                }
                for p in ready_to_contact[:10]  # Top 10 ready-to-contact
            ]
        }
        
        return report

# Demo function
async def demo_icp_aligned_discovery():
    """Demo do ICP-aligned discovery engine"""
    
    print("\n🎯 ICP-ALIGNED DISCOVERY ENGINE DEMO")
    print("=" * 70)
    
    discovery = ICPAlignedDiscovery()
    
    # Test discovery for each ICP
    icp_types = ['P1_growth_ecommerce', 'P3_professional_services']
    
    all_prospects = []
    
    for icp_type in icp_types:
        print(f"\n{'='*60}")
        prospects = await discovery.discover_icp_prospects(icp_type, target_count=5)
        all_prospects.extend(prospects)
        
        print(f"\n🎯 {icp_type.upper()} RESULTS:")
        for i, prospect in enumerate(prospects[:3], 1):
            print(f"{i}. {prospect.company_name} ({prospect.domain})")
            print(f"   Revenue: ${prospect.estimated_revenue:,}")
            print(f"   Confidence: {prospect.confidence_score}/100")
            print(f"   Pain Points: {', '.join(prospect.pain_points[:2])}")
            print(f"   Contact: {'✅' if prospect.contact_info.get('has_contact_page') else '❌'}")
    
    # Generate discovery report
    if all_prospects:
        report = await discovery.generate_discovery_report(all_prospects)
        
        print(f"\n📊 DISCOVERY SUMMARY:")
        print(f"   Total Prospects: {report['summary']['total_prospects_discovered']}")
        print(f"   Avg Confidence: {report['summary']['average_confidence_score']:.1f}/100")
        print(f"   Avg Revenue: ${report['summary']['average_estimated_revenue']:,.0f}")
        print(f"   Ready to Contact: {report['summary']['ready_to_contact']}")
        
        print(f"\n🎯 TOP PAIN POINTS:")
        for pain_data in report['top_pain_points'][:3]:
            print(f"   • {pain_data['pain_point']}: {pain_data['prospect_count']} prospects")
        
        print(f"\n✅ ICP-Aligned Discovery Engine operational!")
        print(f"🚀 Focado EXCLUSIVAMENTE nos ICPs reais!")

if __name__ == "__main__":
    asyncio.run(demo_icp_aligned_discovery())
