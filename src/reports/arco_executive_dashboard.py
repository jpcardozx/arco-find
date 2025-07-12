#!/usr/bin/env python3
"""
📊 ARCO EXECUTIVE DASHBOARD
Painel executivo para monitoramento da estratégia EEA+Turkey
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

class ARCOExecutiveDashboard:
    """
    📊 DASHBOARD EXECUTIVO ARCO
    Métricas críticas para tomada de decisão estratégica
    """
    
    def __init__(self):
        self.metrics = {
            'total_pipeline_value': 0,
            'active_markets': 0,
            'saturation_risk_markets': 0,
            'monthly_recurring_revenue': 0,
            'customer_acquisition_cost': 0,
            'expansion_opportunities': 0
        }
        
        self.market_performance = {
            'eea_dental': {
                'revenue': 125000,  # EUR/month
                'leads_qualified': 47,
                'conversion_rate': 0.18,
                'avg_deal_size': 15000,
                'saturation_level': 0.16,
                'trend': 'growing'
            },
            'turkey_aesthetic': {
                'revenue': 98000,
                'leads_qualified': 34,
                'conversion_rate': 0.22,
                'avg_deal_size': 18000,
                'saturation_level': 0.08,
                'trend': 'accelerating'
            },
            'spain_dental': {
                'revenue': 76000,
                'leads_qualified': 28,
                'conversion_rate': 0.15,
                'avg_deal_size': 12000,
                'saturation_level': 0.23,
                'trend': 'slowing'
            }
        }
        
        self.strategic_alerts = []
        self._calculate_kpis()
    
    def _calculate_kpis(self):
        """📈 Calcula KPIs executivos"""
        
        # Total pipeline value
        total_pipeline = 0
        total_leads = 0
        weighted_conversion = 0
        
        for market, data in self.market_performance.items():
            pipeline_value = data['leads_qualified'] * data['avg_deal_size'] * data['conversion_rate']
            total_pipeline += pipeline_value
            total_leads += data['leads_qualified']
            weighted_conversion += data['conversion_rate'] * data['leads_qualified']
        
        self.metrics['total_pipeline_value'] = total_pipeline
        self.metrics['active_markets'] = len(self.market_performance)
        self.metrics['monthly_recurring_revenue'] = sum(data['revenue'] for data in self.market_performance.values())
        
        # Calculate weighted average conversion
        avg_conversion = weighted_conversion / total_leads if total_leads > 0 else 0
        
        # Estimate CAC (Customer Acquisition Cost)
        total_ad_spend = self.metrics['monthly_recurring_revenue'] * 0.25  # 25% of revenue as ad spend
        total_customers = sum(data['leads_qualified'] * data['conversion_rate'] for data in self.market_performance.values())
        self.metrics['customer_acquisition_cost'] = total_ad_spend / total_customers if total_customers > 0 else 0
        
        # Count saturation risks
        self.metrics['saturation_risk_markets'] = sum(
            1 for data in self.market_performance.values() 
            if data['saturation_level'] > 0.20
        )
        
        # Expansion opportunities (simulated)
        self.metrics['expansion_opportunities'] = 4  # Vienna, Dublin, Barcelona, Rome
    
    def generate_alerts(self):
        """🚨 Gera alertas estratégicos"""
        self.strategic_alerts = []
        
        for market, data in self.market_performance.items():
            # Saturation alerts
            if data['saturation_level'] > 0.25:
                self.strategic_alerts.append({
                    'type': 'critical',
                    'market': market,
                    'message': f"Market saturation critical ({data['saturation_level']:.1%})",
                    'action': 'Implement cooling period & expand geography'
                })
            elif data['saturation_level'] > 0.20:
                self.strategic_alerts.append({
                    'type': 'warning',
                    'market': market,
                    'message': f"Approaching saturation ({data['saturation_level']:.1%})",
                    'action': 'Reduce spend by 30% & prepare expansion'
                })
            
            # Performance alerts
            if data['conversion_rate'] < 0.15:
                self.strategic_alerts.append({
                    'type': 'performance',
                    'market': market,
                    'message': f"Low conversion rate ({data['conversion_rate']:.1%})",
                    'action': 'Review ICP targeting & creative strategy'
                })
            
            # Trend alerts
            if data['trend'] == 'slowing':
                self.strategic_alerts.append({
                    'type': 'trend',
                    'market': market,
                    'message': f"Growth trend slowing",
                    'action': 'Investigate market dynamics & refresh approach'
                })
    
    def print_executive_summary(self):
        """📋 Relatório executivo formatado"""
        print("🎯 ARCO EXECUTIVE DASHBOARD")
        print("=" * 60)
        print(f"📅 Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC")
        print()
        
        # Key Metrics
        print("📊 KEY PERFORMANCE INDICATORS")
        print("-" * 40)
        print(f"💰 Total Pipeline Value:    €{self.metrics['total_pipeline_value']:,.0f}")
        print(f"🏆 Monthly Recurring Rev:   €{self.metrics['monthly_recurring_revenue']:,.0f}")
        print(f"🎯 Customer Acquisition:    €{self.metrics['customer_acquisition_cost']:,.0f}")
        print(f"🌍 Active Markets:          {self.metrics['active_markets']}")
        print(f"⚠️ Saturation Risk:         {self.metrics['saturation_risk_markets']} markets")
        print(f"🚀 Expansion Opportunities: {self.metrics['expansion_opportunities']}")
        print()
        
        # Market Performance
        print("🌍 MARKET PERFORMANCE BREAKDOWN")
        print("-" * 40)
        
        for market, data in self.market_performance.items():
            status_emoji = "🚨" if data['saturation_level'] > 0.25 else "⚠️" if data['saturation_level'] > 0.20 else "✅"
            trend_emoji = "📈" if data['trend'] == 'accelerating' else "📊" if data['trend'] == 'growing' else "📉"
            
            print(f"\n{status_emoji} {market.upper().replace('_', ' ')}")
            print(f"   Revenue:     €{data['revenue']:,.0f}/month")
            print(f"   Leads:       {data['leads_qualified']} qualified")
            print(f"   Conversion:  {data['conversion_rate']:.1%}")
            print(f"   Deal Size:   €{data['avg_deal_size']:,.0f}")
            print(f"   Saturation:  {data['saturation_level']:.1%}")
            print(f"   Trend:       {trend_emoji} {data['trend']}")
        
        # Strategic Alerts
        self.generate_alerts()
        if self.strategic_alerts:
            print(f"\n🚨 STRATEGIC ALERTS ({len(self.strategic_alerts)})")
            print("-" * 40)
            
            for alert in self.strategic_alerts:
                emoji = "🚨" if alert['type'] == 'critical' else "⚠️" if alert['type'] == 'warning' else "📊"
                print(f"\n{emoji} {alert['market'].upper()}")
                print(f"   Issue: {alert['message']}")
                print(f"   Action: {alert['action']}")
        
        # Strategic Recommendations
        print(f"\n🎯 STRATEGIC RECOMMENDATIONS")
        print("-" * 40)
        
        # Dynamic recommendations based on current state
        recommendations = []
        
        if self.metrics['saturation_risk_markets'] > 0:
            recommendations.append("🛡️ Activate anti-saturation protocols for high-penetration markets")
        
        if self.metrics['customer_acquisition_cost'] > 8000:
            recommendations.append("💰 Optimize targeting to reduce CAC below €8,000")
        
        recommendations.extend([
            "🌍 Prioritize Vienna & Dublin for Q3 expansion",
            "📊 Implement weekly saturation monitoring",
            "🔄 Test 60-day cooling periods in saturated markets",
            "🎯 Develop market-specific creative variations"
        ])
        
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        print(f"\n💡 NEXT ACTIONS (Next 30 Days)")
        print("-" * 40)
        print("1. 🔍 Conduct saturation audit for Spain Dental market")
        print("2. 🚀 Initiate expansion planning for Vienna dental sector")
        print("3. 📈 A/B test reduced frequency campaigns in high-penetration areas")
        print("4. 🎯 Develop Turkey Aesthetic scaling strategy (low saturation)")
        print("5. 📊 Implement automated saturation alerts & dashboards")

def simulate_monthly_trends():
    """📈 Simula tendências mensais para demonstração"""
    print("\n📈 MONTHLY TREND SIMULATION (6 months)")
    print("=" * 60)
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    base_revenue = 299000  # Total monthly revenue
    
    trends = {
        'Jan': {'revenue_growth': 0.15, 'saturation_increase': 0.02, 'new_leads': 42},
        'Feb': {'revenue_growth': 0.12, 'saturation_increase': 0.03, 'new_leads': 38},
        'Mar': {'revenue_growth': 0.08, 'saturation_increase': 0.04, 'new_leads': 35},
        'Apr': {'revenue_growth': 0.05, 'saturation_increase': 0.05, 'new_leads': 29},
        'May': {'revenue_growth': 0.02, 'saturation_increase': 0.06, 'new_leads': 23},
        'Jun': {'revenue_growth': -0.03, 'saturation_increase': 0.07, 'new_leads': 18}
    }
    
    for month in months:
        trend = trends[month]
        revenue = base_revenue * (1 + trend['revenue_growth'])
        
        print(f"\n📅 {month} 2025:")
        print(f"   💰 Revenue: €{revenue:,.0f} ({trend['revenue_growth']:+.1%})")
        print(f"   🎯 New Leads: {trend['new_leads']}")
        print(f"   ⚠️ Saturation: +{trend['saturation_increase']:.1%}")
        
        if trend['revenue_growth'] < 0:
            print(f"   🚨 Revenue decline detected - saturation impact")
        elif trend['saturation_increase'] > 0.05:
            print(f"   ⚠️ High saturation growth - expansion needed")

def run_executive_dashboard():
    """🚀 Executa dashboard executivo completo"""
    dashboard = ARCOExecutiveDashboard()
    dashboard.print_executive_summary()
    simulate_monthly_trends()
    
    print(f"\n🎯 EXECUTIVE SUMMARY")
    print("-" * 40)
    print("✅ EEA+Turkey strategy delivering €299K monthly revenue")
    print("⚠️ Spain market approaching saturation threshold")
    print("🚀 Turkey shows highest growth potential (8% saturation)")
    print("🌍 4 expansion markets ready for Q3 launch")
    print("💰 CAC optimization needed to maintain profitability")

if __name__ == "__main__":
    run_executive_dashboard()
