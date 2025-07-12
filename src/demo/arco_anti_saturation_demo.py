#!/usr/bin/env python3
"""
🎯 ARCO ANTI-SATURATION STRATEGY DEMO
Demonstração da estratégia anti-saturação para EEA+Turkey
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

class AntiSaturationStrategy:
    """
    🛡️ ESTRATÉGIA ANTI-SATURAÇÃO ARCO
    - Market penetration tracking
    - Geographic expansion logic
    - Timing optimization
    """
    
    def __init__(self):
        self.market_penetration = {
            'dental_berlin': {'penetration': 0.15, 'last_campaign': '2025-05-15'},
            'dental_amsterdam': {'penetration': 0.08, 'last_campaign': '2025-04-20'},
            'aesthetic_istanbul': {'penetration': 0.03, 'last_campaign': '2025-03-10'},
            'aesthetic_madrid': {'penetration': 0.12, 'last_campaign': '2025-05-01'}
        }
        
        self.expansion_priorities = [
            {'market': 'dental_vienna', 'potential': 0.85, 'difficulty': 0.3},
            {'market': 'aesthetic_barcelona', 'potential': 0.78, 'difficulty': 0.4},
            {'market': 'dental_dublin', 'potential': 0.92, 'difficulty': 0.2},
            {'market': 'aesthetic_rome', 'potential': 0.71, 'difficulty': 0.5}
        ]
    
    def should_campaign_market(self, market: str, campaign_type: str) -> Dict:
        """
        🎯 DECISÃO INTELIGENTE: Deve fazer campanha neste mercado?
        """
        penetration_data = self.market_penetration.get(market, {'penetration': 0, 'last_campaign': None})
        
        # Critical thresholds
        saturation_threshold = 0.25  # 25% penetration = saturação crítica
        cooling_period = 60  # 60 days cooling period
        
        current_penetration = penetration_data['penetration']
        last_campaign = penetration_data.get('last_campaign')
        
        # Calculate cooling period
        days_since_campaign = 999
        if last_campaign:
            last_date = datetime.strptime(last_campaign, '%Y-%m-%d')
            days_since_campaign = (datetime.now() - last_date).days
        
        # Decision logic
        decision = {
            'should_campaign': False,
            'reason': '',
            'alternative_action': '',
            'risk_level': 'low',
            'recommended_spend': 0
        }
        
        if current_penetration >= saturation_threshold:
            decision.update({
                'should_campaign': False,
                'reason': f'Market saturated ({current_penetration:.1%} penetration)',
                'alternative_action': 'expand_geography',
                'risk_level': 'high'
            })
        elif days_since_campaign < cooling_period:
            decision.update({
                'should_campaign': False,
                'reason': f'Cooling period active ({days_since_campaign}/{cooling_period} days)',
                'alternative_action': 'wait_or_expand',
                'risk_level': 'medium'
            })
        else:
            # Safe to campaign
            penetration_factor = 1 - current_penetration  # Less penetration = more spend
            base_spend = 15000 if 'aesthetic' in market else 12000
            
            decision.update({
                'should_campaign': True,
                'reason': f'Market ready ({current_penetration:.1%} penetration, {days_since_campaign} days cool)',
                'alternative_action': 'execute_campaign',
                'risk_level': 'low',
                'recommended_spend': int(base_spend * penetration_factor)
            })
        
        return decision
    
    def get_expansion_recommendations(self, blocked_markets: List[str]) -> List[Dict]:
        """
        🌍 RECOMENDAÇÕES DE EXPANSÃO: Onde expandir quando mercados estão saturados
        """
        recommendations = []
        
        for expansion in self.expansion_priorities:
            market = expansion['market']
            if market not in [m.replace('_', ' ') for m in blocked_markets]:
                
                roi_score = (expansion['potential'] * 0.7) + ((1 - expansion['difficulty']) * 0.3)
                
                recommendations.append({
                    'market': market,
                    'potential_revenue': expansion['potential'] * 50000,  # EUR/month potential
                    'setup_difficulty': expansion['difficulty'],
                    'roi_score': roi_score,
                    'estimated_setup_time': int(expansion['difficulty'] * 30),  # days
                    'recommended_initial_spend': int(10000 + (expansion['potential'] * 8000))
                })
        
        return sorted(recommendations, key=lambda x: x['roi_score'], reverse=True)

def simulate_market_data():
    """
    📊 SIMULAÇÃO: Dados de mercado realistas para demonstração
    """
    markets = {
        'dental_berlin': {
            'total_clinics': 450,
            'ads_active': 68,
            'our_penetration': 0.15,
            'avg_monthly_spend': 8500,
            'competition_intensity': 0.82
        },
        'dental_amsterdam': {
            'total_clinics': 320,
            'ads_active': 48,
            'our_penetration': 0.08,
            'avg_monthly_spend': 7200,
            'competition_intensity': 0.71
        },
        'aesthetic_istanbul': {
            'total_clinics': 890,
            'ads_active': 134,
            'our_penetration': 0.03,
            'avg_monthly_spend': 12800,
            'competition_intensity': 0.45
        },
        'aesthetic_madrid': {
            'total_clinics': 380,
            'ads_active': 57,
            'our_penetration': 0.12,
            'avg_monthly_spend': 9600,
            'competition_intensity': 0.78
        }
    }
    
    return markets

def run_anti_saturation_demo():
    """
    🚀 DEMO PRINCIPAL: Estratégia anti-saturação em ação
    """
    print("🛡️ ARCO ANTI-SATURATION STRATEGY DEMO")
    print("=" * 60)
    
    # Initialize strategy
    strategy = AntiSaturationStrategy()
    market_data = simulate_market_data()
    
    # Test each market
    blocked_markets = []
    available_spend = 50000  # EUR/month total budget
    
    print("\n📊 MARKET ANALYSIS & CAMPAIGN DECISIONS")
    print("-" * 50)
    
    for market, data in market_data.items():
        print(f"\n🎯 {market.upper().replace('_', ' ')}")
        
        decision = strategy.should_campaign_market(market, "ads_optimization")
        
        print(f"  Penetração atual: {data['our_penetration']:.1%}")
        print(f"  Competição: {data['competition_intensity']:.1%}")
        print(f"  Decisão: {'✅ CAMPAIGN' if decision['should_campaign'] else '❌ BLOCK'}")
        print(f"  Razão: {decision['reason']}")
        print(f"  Risco: {decision['risk_level'].upper()}")
        
        if decision['should_campaign']:
            print(f"  💰 Spend recomendado: €{decision['recommended_spend']:,}")
        else:
            print(f"  🔄 Ação alternativa: {decision['alternative_action']}")
            blocked_markets.append(market)
    
    # Expansion recommendations
    if blocked_markets:
        print(f"\n🌍 EXPANSION RECOMMENDATIONS")
        print("-" * 50)
        print(f"Mercados bloqueados: {len(blocked_markets)}")
        
        expansions = strategy.get_expansion_recommendations(blocked_markets)
        
        for i, expansion in enumerate(expansions[:3], 1):
            print(f"\n{i}. {expansion['market'].upper().replace('_', ' ')}")
            print(f"   💰 Potencial: €{expansion['potential_revenue']:,}/mês")
            print(f"   ⚡ ROI Score: {expansion['roi_score']:.2f}")
            print(f"   ⏱️ Setup: {expansion['estimated_setup_time']} dias")
            print(f"   🎯 Initial spend: €{expansion['recommended_initial_spend']:,}")
    
    # Market saturation simulation
    print(f"\n⚠️ SATURATION RISK SIMULATION")
    print("-" * 50)
    
    # Simulate 6 months of campaigning
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    
    for month in months:
        print(f"\n📅 {month} 2025:")
        
        # Simulate penetration increase
        for market in ['dental_berlin', 'aesthetic_madrid']:
            current = strategy.market_penetration[market]['penetration']
            
            # Simulate monthly penetration growth
            growth = random.uniform(0.02, 0.05)  # 2-5% monthly growth
            new_penetration = min(current + growth, 0.35)  # Cap at 35%
            
            strategy.market_penetration[market]['penetration'] = new_penetration
            
            # Check if hitting saturation
            if new_penetration >= 0.25 and current < 0.25:
                print(f"  🚨 {market}: SATURATION ALERT! ({new_penetration:.1%})")
            elif new_penetration >= 0.20:
                print(f"  ⚠️ {market}: High penetration ({new_penetration:.1%})")
            else:
                print(f"  ✅ {market}: Safe levels ({new_penetration:.1%})")
    
    print(f"\n🎯 STRATEGIC RECOMMENDATIONS")
    print("-" * 50)
    print("1. 🛡️ Implement 60-day cooling periods between campaigns")
    print("2. 🌍 Prepare 3 expansion markets before saturation")
    print("3. 📊 Monitor penetration weekly, not monthly")
    print("4. 💰 Reduce spend by 50% when penetration > 20%")
    print("5. 🔄 Rotate between markets to maintain freshness")

if __name__ == "__main__":
    run_anti_saturation_demo()
