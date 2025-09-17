#!/usr/bin/env python3
"""
🎯 ICP KERNEL - Config & Intelligence Core
Camada 0: Mantém taxonomia de nicho, vendor costs, scoring weights

OBJETIVO: Centralizar toda configuração de negócio para Financial-Leak Intelligence
- Vendor costs database
- Niches taxonomy & search dorks  
- Scoring weights & thresholds
- A/B testing variants
"""

import os
import yaml
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class VendorCost:
    """Custo de vendor SaaS"""
    name: str
    tier: str
    monthly_cost: int
    category: str

@dataclass
class NicheConfig:
    """Configuração de nicho"""
    name: str
    categories: List[str]
    search_dorks: List[str]
    revenue_keywords: List[str]
    typical_saas_stack: Dict[str, List[str]]
    base_revenue_estimate: int

@dataclass
class ScoringWeights:
    """Pesos para scoring algorithm"""
    saas_waste: float
    revenue_capability: float
    performance_impact: float
    roas_inefficiency: float
    duplicate_apps: float

class ICPKernel:
    """
    Kernel central de configuração para Financial-Leak Intelligence
    
    Carrega e mantém:
    - Vendor costs database
    - Niches configuration  
    - Scoring weights
    - A/B testing variants
    """
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        
        # Load configurations
        self.vendor_costs = self._load_vendor_costs()
        self.niches = self._load_niches()
        self.scoring_weights = self._load_scoring_weights()
        
        print("🔧 ICP KERNEL INITIALIZED")
        print("=" * 40)
        print(f"📊 Vendor costs: {len(self.vendor_costs)} apps loaded")
        print(f"🎯 Niches: {len(self.niches)} niches configured")
        print(f"⚖️ Scoring: {len(self.scoring_weights)} weight sets")

    def _load_vendor_costs(self) -> Dict[str, VendorCost]:
        """Carrega database de custos de vendors"""
        
        costs_file = self.config_dir / "vendor_costs.yml"
        
        if not costs_file.exists():
            print(f"⚠️ Vendor costs file not found: {costs_file}")
            return {}
        
        with open(costs_file, 'r', encoding='utf-8') as f:
            costs_data = yaml.safe_load(f)
        
        vendor_costs = {}
        
        # Parse nested structure (app -> tier -> cost)
        for app_name, app_data in costs_data.items():
            if app_name.startswith('#'):  # Skip comments
                continue
                
            if isinstance(app_data, dict):
                # Multi-tier app (e.g., klaviyo: {250: 45, 500: 75})
                for tier, cost in app_data.items():
                    if isinstance(cost, (int, float)):
                        key = f"{app_name}_{tier}".lower()
                        vendor_costs[key] = VendorCost(
                            name=app_name,
                            tier=str(tier),
                            monthly_cost=int(cost),
                            category=self._categorize_app(app_name)
                        )
            elif isinstance(app_data, (int, float)):
                # Single-tier app (e.g., typeform: 79)
                key = app_name.lower()
                vendor_costs[key] = VendorCost(
                    name=app_name,
                    tier="standard",
                    monthly_cost=int(app_data),
                    category=self._categorize_app(app_name)
                )
        
        return vendor_costs

    def _load_niches(self) -> Dict[str, NicheConfig]:
        """Carrega configuração de nichos"""
        
        niches_file = self.config_dir / "niches.yml"
        
        if not niches_file.exists():
            print(f"⚠️ Niches file not found: {niches_file}")
            return {}
        
        with open(niches_file, 'r', encoding='utf-8') as f:
            niches_data = yaml.safe_load(f)
        
        niches = {}
        
        # Parse niche configurations
        for niche_name, niche_data in niches_data.items():
            if niche_name in ['geo_focus', 'revenue_estimation', 'roas_indicators', 
                            'competitor_detection', 'qualification_criteria']:
                continue  # Skip global configs
            
            if isinstance(niche_data, dict) and 'categories' in niche_data:
                niches[niche_name] = NicheConfig(
                    name=niche_name,
                    categories=niche_data.get('categories', []),
                    search_dorks=niche_data.get('search_dorks', []),
                    revenue_keywords=niche_data.get('revenue_keywords', []),
                    typical_saas_stack=niche_data.get('typical_saas_stack', {}),
                    base_revenue_estimate=niches_data.get('revenue_estimation', {}).get('base_estimates', {}).get(niche_name, 25000)
                )
        
        return niches

    def _load_scoring_weights(self) -> Dict[str, ScoringWeights]:
        """Carrega pesos para scoring"""
        
        weights_file = self.config_dir / "scoring_weights.yml"
        
        if not weights_file.exists():
            print(f"⚠️ Scoring weights file not found: {weights_file}")
            # Return default weights
            return {
                'default': ScoringWeights(
                    saas_waste=0.40,
                    revenue_capability=0.25,
                    performance_impact=0.20,
                    roas_inefficiency=0.10,
                    duplicate_apps=0.05
                )
            }
        
        with open(weights_file, 'r', encoding='utf-8') as f:
            weights_data = yaml.safe_load(f)
        
        weights = {}
        
        # Default weights
        primary = weights_data.get('primary_weights', {})
        weights['default'] = ScoringWeights(
            saas_waste=primary.get('saas_waste', 0.40),
            revenue_capability=primary.get('revenue_capability', 0.25),
            performance_impact=primary.get('performance_impact', 0.20),
            roas_inefficiency=primary.get('roas_inefficiency', 0.10),
            duplicate_apps=primary.get('duplicate_apps', 0.05)
        )
        
        # A/B testing variants
        ab_variants = weights_data.get('ab_testing', {}).get('scoring_variants', {})
        for variant_name, variant_weights in ab_variants.items():
            weights[variant_name] = ScoringWeights(
                saas_waste=variant_weights.get('saas_waste', 0.40),
                revenue_capability=variant_weights.get('revenue_capability', 0.25),
                performance_impact=variant_weights.get('performance_impact', 0.20),
                roas_inefficiency=variant_weights.get('roas_inefficiency', 0.10),
                duplicate_apps=variant_weights.get('duplicate_apps', 0.05)
            )
        
        return weights

    def _categorize_app(self, app_name: str) -> str:
        """Categoriza app SaaS por nome"""
        
        app_lower = app_name.lower()
        
        if any(keyword in app_lower for keyword in ['klaviyo', 'mailchimp', 'sendgrid', 'mailgun', 'campaign']):
            return 'email_marketing'
        elif any(keyword in app_lower for keyword in ['typeform', 'jotform', 'gravity']):
            return 'forms'
        elif any(keyword in app_lower for keyword in ['recharge', 'loop', 'bold', 'yotpo']):
            return 'subscriptions'
        elif any(keyword in app_lower for keyword in ['zendesk', 'intercom', 'freshdesk', 'drift']):
            return 'customer_support'
        elif any(keyword in app_lower for keyword in ['mixpanel', 'amplitude', 'segment', 'hotjar', 'fullstory']):
            return 'analytics'
        elif any(keyword in app_lower for keyword in ['optimizely', 'vwo', 'unbounce']):
            return 'optimization'
        elif any(keyword in app_lower for keyword in ['calendly', 'acuity']):
            return 'scheduling'
        elif any(keyword in app_lower for keyword in ['zapier', 'integromat', 'make']):
            return 'automation'
        elif any(keyword in app_lower for keyword in ['shopify', 'woocommerce']):
            return 'ecommerce'
        else:
            return 'other'

    def get_vendor_cost(self, app_name: str, tier: str = "standard") -> Optional[VendorCost]:
        """Obtém custo de vendor específico"""
        
        # Try exact match first
        key = f"{app_name}_{tier}".lower()
        if key in self.vendor_costs:
            return self.vendor_costs[key]
        
        # Try just app name
        key = app_name.lower()
        if key in self.vendor_costs:
            return self.vendor_costs[key]
        
        # Try partial match
        for vendor_key, vendor_cost in self.vendor_costs.items():
            if app_name.lower() in vendor_key:
                return vendor_cost
        
        return None

    def get_niche_config(self, niche_name: str) -> Optional[NicheConfig]:
        """Obtém configuração de nicho"""
        return self.niches.get(niche_name)

    def get_scoring_weights(self, variant: str = "default") -> ScoringWeights:
        """Obtém pesos para scoring"""
        return self.scoring_weights.get(variant, self.scoring_weights['default'])

    def get_search_dorks(self, niche: str = "beauty_skincare") -> List[str]:
        """Obtém dorks de busca para nicho"""
        niche_config = self.get_niche_config(niche)
        return niche_config.search_dorks if niche_config else []

    def estimate_saas_waste(self, detected_apps: List[str]) -> Dict[str, Any]:
        """Estima waste de SaaS baseado em apps detectados"""
        
        total_waste = 0
        app_costs = {}
        categories = {}
        
        for app in detected_apps:
            vendor_cost = self.get_vendor_cost(app)
            if vendor_cost:
                total_waste += vendor_cost.monthly_cost
                app_costs[app] = vendor_cost.monthly_cost
                
                category = vendor_cost.category
                if category not in categories:
                    categories[category] = []
                categories[category].append(app)
        
        # Detect duplicates (multiple apps in same category)
        duplicates = sum(len(apps) - 1 for apps in categories.values() if len(apps) > 1)
        
        return {
            'total_monthly_waste': total_waste,
            'app_costs': app_costs,
            'categories': categories,
            'duplicate_apps': duplicates,
            'waste_by_category': {cat: sum(self.get_vendor_cost(app).monthly_cost for app in apps if self.get_vendor_cost(app)) 
                                for cat, apps in categories.items()}
        }

    def calculate_revenue_proxy(self, domain: str, niche: str = "beauty_skincare") -> int:
        """Calcula revenue proxy baseado em domain + niche"""
        
        niche_config = self.get_niche_config(niche)
        base_revenue = niche_config.base_revenue_estimate if niche_config else 25000
        
        # TLD adjustments
        if domain.endswith('.com'):
            base_revenue = int(base_revenue * 1.2)
        elif domain.endswith('.co'):
            base_revenue = int(base_revenue * 1.1)
        elif domain.endswith('.io'):
            base_revenue = int(base_revenue * 0.9)
        
        # Domain length heuristic
        domain_name = domain.split('.')[0]
        if len(domain_name) <= 6:
            base_revenue = int(base_revenue * 1.3)
        elif len(domain_name) <= 10:
            base_revenue = int(base_revenue * 1.1)
        
        return base_revenue

    def get_qualification_thresholds(self) -> Dict[str, int]:
        """Obtém thresholds de qualificação"""
        
        weights_file = self.config_dir / "scoring_weights.yml"
        
        if weights_file.exists():
            with open(weights_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data.get('qualification_gates', {
                    'pre_qualification': 40,
                    'final_qualification': 75,
                    'priority_thresholds': {
                        'immediate': 90,
                        'high': 75,
                        'medium': 60,
                        'low': 40
                    }
                })
        
        # Default thresholds
        return {
            'pre_qualification': 40,
            'final_qualification': 75,
            'priority_thresholds': {
                'immediate': 90,
                'high': 75,
                'medium': 60,
                'low': 40
            }
        }

    def export_config_summary(self) -> Dict[str, Any]:
        """Exporta resumo da configuração"""
        
        return {
            'vendor_costs': {
                'total_apps': len(self.vendor_costs),
                'categories': list(set(vc.category for vc in self.vendor_costs.values())),
                'cost_range': {
                    'min': min(vc.monthly_cost for vc in self.vendor_costs.values()),
                    'max': max(vc.monthly_cost for vc in self.vendor_costs.values()),
                    'avg': sum(vc.monthly_cost for vc in self.vendor_costs.values()) / len(self.vendor_costs)
                }
            },
            'niches': {
                'total_niches': len(self.niches),
                'niche_names': list(self.niches.keys()),
                'total_dorks': sum(len(n.search_dorks) for n in self.niches.values())
            },
            'scoring': {
                'weight_variants': list(self.scoring_weights.keys()),
                'default_weights': {
                    'saas_waste': self.scoring_weights['default'].saas_waste,
                    'revenue_capability': self.scoring_weights['default'].revenue_capability,
                    'performance_impact': self.scoring_weights['default'].performance_impact
                }
            }
        }

# Demo do ICP Kernel
def demo_icp_kernel():
    """Demo do ICP Kernel"""
    
    print("\n🎯 ICP KERNEL DEMO")
    print("=" * 50)
    
    # Initialize kernel
    kernel = ICPKernel()
    
    # Test vendor cost lookup
    print(f"\n💰 VENDOR COST EXAMPLES:")
    test_apps = ["klaviyo", "typeform", "zendesk", "recharge"]
    for app in test_apps:
        cost = kernel.get_vendor_cost(app)
        if cost:
            print(f"  • {cost.name}: ${cost.monthly_cost}/month ({cost.category})")
        else:
            print(f"  • {app}: Not found")
    
    # Test SaaS waste estimation
    detected_apps = ["klaviyo", "typeform", "zendesk", "hotjar", "mailchimp"]
    waste_analysis = kernel.estimate_saas_waste(detected_apps)
    print(f"\n📊 SAAS WASTE ANALYSIS:")
    print(f"  • Total waste: ${waste_analysis['total_monthly_waste']}/month")
    print(f"  • Duplicate apps: {waste_analysis['duplicate_apps']}")
    print(f"  • Categories: {list(waste_analysis['categories'].keys())}")
    
    # Test revenue proxy
    test_domains = ["beautystore.com", "skincare.co", "cosmetics.io"]
    print(f"\n💵 REVENUE PROXY EXAMPLES:")
    for domain in test_domains:
        revenue = kernel.calculate_revenue_proxy(domain)
        print(f"  • {domain}: ${revenue:,}/month")
    
    # Test niche configuration
    beauty_niche = kernel.get_niche_config("beauty_skincare")
    if beauty_niche:
        print(f"\n🎯 BEAUTY/SKINCARE NICHE:")
        print(f"  • Categories: {beauty_niche.categories}")
        print(f"  • Search dorks: {len(beauty_niche.search_dorks)} configured")
        print(f"  • Base revenue: ${beauty_niche.base_revenue_estimate:,}/month")
    
    # Export configuration summary
    summary = kernel.export_config_summary()
    print(f"\n📋 CONFIG SUMMARY:")
    print(f"  • Vendor apps: {summary['vendor_costs']['total_apps']}")
    print(f"  • Cost range: ${summary['vendor_costs']['cost_range']['min']}-${summary['vendor_costs']['cost_range']['max']}")
    print(f"  • Niches: {summary['niches']['total_niches']}")
    print(f"  • Search dorks: {summary['niches']['total_dorks']}")
    
    print(f"\n✅ ICP Kernel operational and ready!")

if __name__ == "__main__":
    demo_icp_kernel()
