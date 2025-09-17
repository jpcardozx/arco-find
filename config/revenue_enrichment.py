#!/usr/bin/env python3
"""
💰 REVENUE & ROAS ENRICHMENT - Layer 3
Financial Intelligence Engine

OBJETIVO: Transformar footprint em financial intelligence
- Revenue estimation com Shopify Storefront API
- ROAS inefficiency detection  
- Revenue leak scoring
- Financial impact quantification
"""

import asyncio
import aiohttp
import json
import time
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import math

# Import previous layers
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))
from icp_kernel import ICPKernel
from footprint_collector import FootprintCollector, FootprintResult

@dataclass
class RevenueEnrichment:
    """Resultado do enrichment de revenue"""
    domain: str
    
    # Revenue Analysis
    estimated_monthly_revenue: int
    confidence_score: float  # 0-100
    revenue_indicators: List[str]
    
    # ROAS Inefficiency
    roas_waste_score: int  # 0-100
    duplicate_apps: List[str]
    overpriced_tools: List[Dict[str, Any]]
    
    # Financial Impact
    monthly_saas_waste: int
    waste_percentage: float  # % of revenue
    annual_savings_potential: int
    
    # Enrichment Success
    enrichment_time: float
    success: bool
    error: Optional[str] = None

class RevenueROASEnrichment:
    """
    Revenue & ROAS Enrichment Engine
    
    Adiciona inteligência financeira ao footprint:
    - Revenue estimation (múltiplas fontes)
    - ROAS inefficiency detection
    - Savings potential calculation
    """
    
    def __init__(self):
        self.kernel = ICPKernel()
        self.footprint_collector = FootprintCollector()
        
        # API settings
        self.timeout = 5.0
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Revenue indicators (signals from page content)
        self.revenue_indicators = {
            'high_revenue': [
                'bestseller', 'sold out', 'limited edition', 'premium', 
                'luxury', 'exclusive', 'professional grade', 'award winning'
            ],
            'pricing_signals': [
                r'\$[0-9]+(?:\.[0-9]{2})?',  # Price patterns
                r'[0-9]+(?:\.[0-9]{2})?\s*USD',
                r'from\s+\$[0-9]+',
                r'starting\s+at\s+\$[0-9]+'
            ],
            'volume_signals': [
                'customers love', 'thousands sold', 'million sold',
                'customer reviews', 'testimonials', 'success stories',
                'join [0-9,]+', 'over [0-9,]+ customers'
            ],
            'subscription_signals': [
                'subscribe', 'monthly', 'quarterly', 'subscription box',
                'auto-ship', 'recurring', 'membership', 'vip access'
            ]
        }
        
        # ROAS inefficiency patterns
        self.roas_inefficiencies = {
            'duplicate_categories': {
                'email_marketing': ['klaviyo', 'mailchimp', 'sendgrid', 'campaign_monitor'],
                'analytics': ['google_analytics', 'mixpanel', 'hotjar', 'fullstory', 'amplitude'],
                'customer_support': ['zendesk', 'intercom', 'drift', 'help_scout'],
                'forms': ['typeform', 'jotform', 'gravity_forms'],
                'subscriptions': ['recharge', 'loop', 'yotpo_subscriptions', 'bold_subscriptions']
            },
            'overpriced_alternatives': {
                'hubspot': {'alternative': 'mailchimp', 'savings': 250},
                'optimizely': {'alternative': 'google_optimize', 'savings': 1950},  # Google Optimize is free
                'fullstory': {'alternative': 'hotjar', 'savings': 160},
                'zendesk': {'alternative': 'freshdesk', 'savings': 30}
            }
        }
        
        print("💰 REVENUE & ROAS ENRICHMENT INITIALIZED")
        print("=" * 45)
        print(f"📊 Revenue indicators: {sum(len(v) if isinstance(v, list) else 1 for v in self.revenue_indicators.values())}")
        print(f"🎯 ROAS inefficiency patterns: {len(self.roas_inefficiencies['duplicate_categories'])}")
        print(f"💡 Overpriced alternatives: {len(self.roas_inefficiencies['overpriced_alternatives'])}")

    async def enrich_revenue(self, footprint: FootprintResult) -> RevenueEnrichment:
        """
        Enriquece footprint com intelligence financeira
        
        Combina múltiplas fontes para revenue estimation
        """
        start_time = time.time()
        
        try:
            # Parallel enrichment tasks
            tasks = [
                self._estimate_revenue_multi_source(footprint),
                self._analyze_roas_inefficiency(footprint),
                self._fetch_additional_signals(footprint.domain)
            ]
            
            revenue_data, roas_analysis, additional_signals = await asyncio.gather(*tasks)
            
            # Calculate final metrics
            estimated_revenue = revenue_data['estimated_monthly_revenue']
            confidence = revenue_data['confidence_score']
            
            waste_percentage = (footprint.total_waste / estimated_revenue * 100) if estimated_revenue > 0 else 0
            annual_savings = roas_analysis['monthly_savings'] * 12
            
            enrichment_time = time.time() - start_time
            
            return RevenueEnrichment(
                domain=footprint.domain,
                estimated_monthly_revenue=estimated_revenue,
                confidence_score=confidence,
                revenue_indicators=revenue_data['indicators'],
                roas_waste_score=roas_analysis['waste_score'],
                duplicate_apps=roas_analysis['duplicates'],
                overpriced_tools=roas_analysis['overpriced'],
                monthly_saas_waste=footprint.total_waste,
                waste_percentage=waste_percentage,
                annual_savings_potential=annual_savings,
                enrichment_time=enrichment_time,
                success=True
            )
            
        except Exception as e:
            enrichment_time = time.time() - start_time
            return RevenueEnrichment(
                domain=footprint.domain,
                estimated_monthly_revenue=0,
                confidence_score=0,
                revenue_indicators=[],
                roas_waste_score=0,
                duplicate_apps=[],
                overpriced_tools=[],
                monthly_saas_waste=footprint.total_waste,
                waste_percentage=0,
                annual_savings_potential=0,
                enrichment_time=enrichment_time,
                success=False,
                error=str(e)
            )

    async def _estimate_revenue_multi_source(self, footprint: FootprintResult) -> Dict[str, Any]:
        """Estima revenue usando múltiplas fontes e heurísticas"""
        
        # Base estimate from ICP Kernel
        base_revenue = self.kernel.calculate_revenue_proxy(footprint.domain, "beauty_skincare")
        
        indicators = []
        confidence_factors = []
        
        # Factor 1: Ecommerce platform quality
        platform_multipliers = {
            'shopify': {'multiplier': 1.3, 'confidence': 0.8},
            'shopify_plus': {'multiplier': 3.0, 'confidence': 0.9},  # If Plus detected
            'woocommerce': {'multiplier': 0.8, 'confidence': 0.6},
            'squarespace': {'multiplier': 0.7, 'confidence': 0.5},
            'wix': {'multiplier': 0.5, 'confidence': 0.4}
        }
        
        platform_factor = 1.0
        if footprint.ecommerce_platform:
            platform_data = platform_multipliers.get(footprint.ecommerce_platform, {'multiplier': 1.0, 'confidence': 0.3})
            platform_factor = platform_data['multiplier']
            confidence_factors.append(platform_data['confidence'])
            indicators.append(f"ecommerce_platform: {footprint.ecommerce_platform}")
        
        # Factor 2: SaaS stack sophistication
        saas_sophistication = len(footprint.detected_apps)
        if saas_sophistication >= 8:
            saas_multiplier = 1.5
            confidence_factors.append(0.7)
            indicators.append("sophisticated_saas_stack")
        elif saas_sophistication >= 5:
            saas_multiplier = 1.2
            confidence_factors.append(0.5)
            indicators.append("moderate_saas_stack")
        else:
            saas_multiplier = 0.9
            confidence_factors.append(0.3)
        
        # Factor 3: Premium SaaS presence
        premium_apps = ['klaviyo', 'yotpo', 'recharge', 'optimizely', 'fullstory']
        premium_count = sum(1 for app in footprint.detected_apps if app in premium_apps)
        
        if premium_count >= 3:
            premium_multiplier = 1.8
            confidence_factors.append(0.8)
            indicators.append("premium_saas_stack")
        elif premium_count >= 1:
            premium_multiplier = 1.3
            confidence_factors.append(0.6)
            indicators.append("some_premium_tools")
        else:
            premium_multiplier = 1.0
            confidence_factors.append(0.2)
        
        # Factor 4: Marketing automation presence
        marketing_automation = ['klaviyo', 'mailchimp', 'hubspot', 'sendgrid']
        if any(app in footprint.detected_apps for app in marketing_automation):
            marketing_multiplier = 1.4
            confidence_factors.append(0.7)
            indicators.append("email_marketing_automation")
        else:
            marketing_multiplier = 0.8
            confidence_factors.append(0.3)
        
        # Calculate final estimate
        final_revenue = int(base_revenue * platform_factor * saas_multiplier * premium_multiplier * marketing_multiplier)
        
        # Ensure reasonable bounds
        final_revenue = max(5000, min(500000, final_revenue))  # $5k - $500k range
        
        # Calculate confidence (average of factors, with minimum threshold)
        avg_confidence = sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.2
        final_confidence = max(20, min(95, avg_confidence * 100))  # 20-95% range
        
        return {
            'estimated_monthly_revenue': final_revenue,
            'confidence_score': final_confidence,
            'indicators': indicators,
            'breakdown': {
                'base_revenue': base_revenue,
                'platform_factor': platform_factor,
                'saas_factor': saas_multiplier,
                'premium_factor': premium_multiplier,
                'marketing_factor': marketing_multiplier
            }
        }

    async def _analyze_roas_inefficiency(self, footprint: FootprintResult) -> Dict[str, Any]:
        """Analisa ineficiências de ROAS"""
        
        duplicates = []
        overpriced = []
        monthly_savings = 0
        
        # Detect duplicate categories
        detected_categories = {}
        for app in footprint.detected_apps:
            vendor_cost = self.kernel.get_vendor_cost(app)
            if vendor_cost:
                category = vendor_cost.category
                if category not in detected_categories:
                    detected_categories[category] = []
                detected_categories[category].append(app)
        
        # Find duplicates (multiple apps in same category)
        for category, apps in detected_categories.items():
            if len(apps) > 1:
                duplicates.extend(apps[1:])  # All except the first one
                # Calculate potential savings (keep cheapest, remove others)
                costs = [self.kernel.get_vendor_cost(app).monthly_cost for app in apps]
                monthly_savings += sum(costs) - min(costs)
        
        # Detect overpriced alternatives
        for app in footprint.detected_apps:
            if app in self.roas_inefficiencies['overpriced_alternatives']:
                alternative_data = self.roas_inefficiencies['overpriced_alternatives'][app]
                overpriced.append({
                    'current_app': app,
                    'alternative': alternative_data['alternative'],
                    'monthly_savings': alternative_data['savings']
                })
                monthly_savings += alternative_data['savings']
        
        # Calculate waste score (0-100)
        total_apps = len(footprint.detected_apps)
        duplicate_ratio = len(duplicates) / total_apps if total_apps > 0 else 0
        overpriced_ratio = len(overpriced) / total_apps if total_apps > 0 else 0
        
        waste_score = int((duplicate_ratio * 50) + (overpriced_ratio * 30) + (min(monthly_savings / 100, 20)))
        waste_score = max(0, min(100, waste_score))
        
        return {
            'waste_score': waste_score,
            'duplicates': duplicates,
            'overpriced': overpriced,
            'monthly_savings': monthly_savings,
            'duplicate_categories': {cat: apps for cat, apps in detected_categories.items() if len(apps) > 1}
        }

    async def _fetch_additional_signals(self, domain: str) -> Dict[str, Any]:
        """Fetch additional revenue signals from domain"""
        
        try:
            if not domain.startswith(('http://', 'https://')):
                url = f'https://{domain}'
            else:
                url = domain
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=3.0)) as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        content = await response.text()
                        return self._analyze_content_signals(content)
            
        except Exception:
            pass
        
        return {'signals': [], 'quality_score': 0}

    def _analyze_content_signals(self, content: str) -> Dict[str, Any]:
        """Analisa signals de revenue no conteúdo"""
        
        content_lower = content.lower()
        found_signals = []
        quality_score = 0
        
        # High revenue indicators
        for indicator in self.revenue_indicators['high_revenue']:
            if indicator in content_lower:
                found_signals.append(f"high_revenue: {indicator}")
                quality_score += 10
        
        # Pricing signals
        price_matches = 0
        for pattern in self.revenue_indicators['pricing_signals']:
            matches = re.findall(pattern, content, re.IGNORECASE)
            price_matches += len(matches)
        
        if price_matches > 0:
            found_signals.append(f"pricing_signals: {price_matches} prices found")
            quality_score += min(price_matches * 2, 20)
        
        # Volume signals
        for indicator in self.revenue_indicators['volume_signals']:
            if indicator in content_lower:
                found_signals.append(f"volume_signal: {indicator}")
                quality_score += 15
        
        # Subscription signals
        subscription_count = 0
        for indicator in self.revenue_indicators['subscription_signals']:
            if indicator in content_lower:
                subscription_count += 1
        
        if subscription_count > 0:
            found_signals.append(f"subscription_signals: {subscription_count}")
            quality_score += subscription_count * 5
        
        return {
            'signals': found_signals,
            'quality_score': min(quality_score, 100)
        }

    async def batch_enrich(self, domains: List[str]) -> List[RevenueEnrichment]:
        """Batch enrichment de múltiplos domains"""
        
        print(f"\n💰 BATCH REVENUE ENRICHMENT")
        print(f"📊 Domains: {len(domains)}")
        
        start_time = time.time()
        
        # First collect footprints
        footprints = await self.footprint_collector.batch_collect(domains)
        
        # Then enrich with revenue intelligence
        enrichment_tasks = [self.enrich_revenue(fp) for fp in footprints if fp.success]
        enrichments = await asyncio.gather(*enrichment_tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_enrichments = []
        for enrichment in enrichments:
            if isinstance(enrichment, Exception):
                processed_enrichments.append(RevenueEnrichment(
                    domain="unknown",
                    estimated_monthly_revenue=0,
                    confidence_score=0,
                    revenue_indicators=[],
                    roas_waste_score=0,
                    duplicate_apps=[],
                    overpriced_tools=[],
                    monthly_saas_waste=0,
                    waste_percentage=0,
                    annual_savings_potential=0,
                    enrichment_time=0,
                    success=False,
                    error=str(enrichment)
                ))
            else:
                processed_enrichments.append(enrichment)
        
        total_time = time.time() - start_time
        print(f"✅ Batch enrichment completed: {total_time:.2f}s")
        
        return processed_enrichments

    def generate_enrichment_report(self, enrichments: List[RevenueEnrichment]) -> Dict[str, Any]:
        """Gera relatório de revenue enrichment"""
        
        successful = [e for e in enrichments if e.success]
        
        if not successful:
            return {'error': 'No successful enrichments'}
        
        # Revenue analysis
        total_revenue = sum(e.estimated_monthly_revenue for e in successful)
        avg_revenue = total_revenue / len(successful)
        avg_confidence = sum(e.confidence_score for e in successful) / len(successful)
        
        # Savings analysis
        total_waste = sum(e.monthly_saas_waste for e in successful)
        total_annual_savings = sum(e.annual_savings_potential for e in successful)
        avg_waste_percentage = sum(e.waste_percentage for e in successful) / len(successful)
        
        # ROAS analysis
        avg_roas_score = sum(e.roas_waste_score for e in successful) / len(successful)
        total_duplicates = sum(len(e.duplicate_apps) for e in successful)
        total_overpriced = sum(len(e.overpriced_tools) for e in successful)
        
        return {
            'summary': {
                'total_domains': len(enrichments),
                'successful_enrichments': len(successful),
                'avg_enrichment_time': sum(e.enrichment_time for e in successful) / len(successful)
            },
            'revenue_intelligence': {
                'total_monthly_revenue': total_revenue,
                'avg_monthly_revenue': int(avg_revenue),
                'avg_confidence_score': avg_confidence,
                'revenue_range': {
                    'min': min(e.estimated_monthly_revenue for e in successful),
                    'max': max(e.estimated_monthly_revenue for e in successful)
                }
            },
            'savings_potential': {
                'total_monthly_waste': total_waste,
                'total_annual_savings': total_annual_savings,
                'avg_waste_percentage': avg_waste_percentage,
                'avg_roas_waste_score': avg_roas_score
            },
            'inefficiency_analysis': {
                'total_duplicate_apps': total_duplicates,
                'total_overpriced_tools': total_overpriced,
                'domains_with_duplicates': sum(1 for e in successful if e.duplicate_apps),
                'domains_with_overpriced': sum(1 for e in successful if e.overpriced_tools)
            }
        }

# Demo
async def demo_revenue_enrichment():
    """Demo do Revenue & ROAS Enrichment"""
    
    print("\n💰 REVENUE & ROAS ENRICHMENT DEMO")
    print("=" * 50)
    
    enricher = RevenueROASEnrichment()
    
    # Test domains
    test_domains = [
        'glossier.com',
        'sephora.com'
    ]
    
    print(f"\n🎯 Testing revenue enrichment: {test_domains[0]}")
    
    # Get footprint first
    footprint = await enricher.footprint_collector.collect_footprint(test_domains[0])
    
    if footprint.success:
        print(f"📊 Footprint: {len(footprint.detected_apps)} apps, ${footprint.total_waste} waste")
        
        # Enrich with revenue intelligence
        enrichment = await enricher.enrich_revenue(footprint)
        
        if enrichment.success:
            print(f"\n💰 REVENUE INTELLIGENCE:")
            print(f"  • Estimated revenue: ${enrichment.estimated_monthly_revenue:,}/month")
            print(f"  • Confidence: {enrichment.confidence_score:.1f}%")
            print(f"  • Waste percentage: {enrichment.waste_percentage:.1f}%")
            print(f"  • Annual savings: ${enrichment.annual_savings_potential:,}")
            print(f"  • ROAS waste score: {enrichment.roas_waste_score}/100")
            
            if enrichment.duplicate_apps:
                print(f"  • Duplicate apps: {', '.join(enrichment.duplicate_apps)}")
            
            if enrichment.overpriced_tools:
                for tool in enrichment.overpriced_tools:
                    print(f"  • Overpriced: {tool['current_app']} → {tool['alternative']} (save ${tool['monthly_savings']}/mo)")
        
        else:
            print(f"❌ Enrichment failed: {enrichment.error}")
    else:
        print(f"❌ Footprint failed: {footprint.error}")
    
    print(f"\n✅ Revenue & ROAS Enrichment ready!")

if __name__ == "__main__":
    asyncio.run(demo_revenue_enrichment())
