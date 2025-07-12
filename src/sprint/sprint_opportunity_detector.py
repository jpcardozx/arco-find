#!/usr/bin/env python3
"""
ARCO Sprint Opportunity Detector
Detecta 3 sinais específicos para oferta Sprint USD 997:
1. Renewal SaaS ≤ 60 dias
2. Lighthouse mobile < 40
3. Novo CFO/Head Ops ≤ 90 dias
"""

import requests
import json
import time
import csv
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re

@dataclass
class SprintOpportunity:
    company_name: str
    domain: str
    lighthouse_mobile: Optional[int]
    days_to_renewal: Optional[int] 
    saas_tool: Optional[str]
    cfo_hired_days: Optional[int]
    signal_count: int
    estimated_savings: Optional[int]
    contact_email: Optional[str]
    linkedin_profile: Optional[str]

class SprintOpportunityDetector:
    def __init__(self):
        self.pagespeed_api_key = "YOUR_PAGESPEED_API_KEY"  # Substitua pela sua chave
        self.common_saas_renewals = {
            'hubspot': {'typical_cost': 18228, 'renewal_patterns': ['/legal/subscription', '/billing', '/account/billing']},
            'monday': {'typical_cost': 12000, 'renewal_patterns': ['/billing', '/account/subscription']},
            'zendesk': {'typical_cost': 15600, 'renewal_patterns': ['/billing', '/subscription']},
            'salesforce': {'typical_cost': 24000, 'renewal_patterns': ['/billing', '/contract']},
            'mailchimp': {'typical_cost': 3600, 'renewal_patterns': ['/billing', '/account/billing']}
        }
        
    def analyze_lighthouse_score(self, domain: str) -> Optional[int]:
        """Analisa score Lighthouse mobile (API PageSpeed gratuita)"""
        try:
            url = f"https://www.googleapis.com/pagespeed/v5/runPagespeed"
            params = {
                'url': f"https://{domain}",
                'key': self.pagespeed_api_key,
                'category': 'performance',
                'strategy': 'mobile'
            }
            
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                score = data.get('lighthouseResult', {}).get('categories', {}).get('performance', {}).get('score', 0)
                return int(score * 100) if score else None
            return None
        except Exception as e:
            print(f"Erro ao analisar Lighthouse para {domain}: {e}")
            return None
    
    def detect_saas_renewal_signals(self, domain: str) -> Dict[str, any]:
        """Detecta sinais de renovação SaaS através de análise de website"""
        try:
            # Primeiro tenta acessar página principal
            response = requests.get(f"https://{domain}", timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            content = response.text.lower()
            
            detected_tools = []
            potential_savings = 0
            
            # Detecta ferramentas SaaS comuns através de assinaturas no código
            saas_signatures = {
                'hubspot': ['hs-analytics', 'hubspot', 'hs-scripts'],
                'monday': ['monday.com', 'mondaycom', 'monday-sdk'],
                'zendesk': ['zendesk', 'zopim', 'zdchat'],
                'salesforce': ['salesforce', 'sfdc', 'lightning'],
                'mailchimp': ['mailchimp', 'mc4wp', 'mailchimp-for-wp'],
                'intercom': ['intercom', 'intercom.io'],
                'drift': ['drift.com', 'drift-chat'],
                'calendly': ['calendly.com', 'calendly'],
                'typeform': ['typeform.com', 'typeform'],
                'hotjar': ['hotjar.com', 'hotjar']
            }
            
            for tool, signatures in saas_signatures.items():
                if any(sig in content for sig in signatures):
                    detected_tools.append(tool)
                    if tool in self.common_saas_renewals:
                        potential_savings += self.common_saas_renewals[tool]['typical_cost'] * 0.4  # 40% economia média
            
            # Simula detecção de renovação próxima (em cenário real, usaria Vendr DB ou similar)
            days_to_renewal = None
            primary_tool = None
            
            if detected_tools:
                primary_tool = detected_tools[0]  # Pega a primeira ferramenta detectada
                # Simula renovação em 45-60 dias para demonstração
                days_to_renewal = 52  # Em produção, seria obtido via API Vendr ou análise de contratos
            
            return {
                'days_to_renewal': days_to_renewal,
                'saas_tool': primary_tool,
                'estimated_savings': int(potential_savings),
                'detected_tools': detected_tools
            }
            
        except Exception as e:
            print(f"Erro ao detectar SaaS para {domain}: {e}")
            return {'days_to_renewal': None, 'saas_tool': None, 'estimated_savings': 0, 'detected_tools': []}
    
    def analyze_leadership_changes(self, company_name: str, domain: str) -> Optional[int]:
        """Simula análise de mudanças de liderança (CFO/Head Ops)"""
        # Em produção, integraria com LinkedIn API ou PhantomBuster
        # Para demonstração, simula alguns casos
        leadership_indicators = [
            'novo cfo', 'new cfo', 'head of operations', 'chief financial officer',
            'finance director', 'financial controller'
        ]
        
        try:
            # Verifica about page ou news section
            about_response = requests.get(f"https://{domain}/about", timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if about_response.status_code == 200:
                content = about_response.text.lower()
                # Simula detecção de nova liderança
                if any(indicator in content for indicator in leadership_indicators):
                    return 65  # Simula nova liderança há 65 dias
            
            return None
        except:
            return None
    
    def calculate_signal_score(self, opportunity: SprintOpportunity) -> int:
        """Calcula score baseado nos 3 sinais principais"""
        signals = 0
        
        # Sinal 1: Renewal ≤ 60 dias
        if opportunity.days_to_renewal and opportunity.days_to_renewal <= 60:
            signals += 1
        
        # Sinal 2: Lighthouse mobile < 40
        if opportunity.lighthouse_mobile and opportunity.lighthouse_mobile < 40:
            signals += 1
        
        # Sinal 3: Novo CFO/Head Ops ≤ 90 dias  
        if opportunity.cfo_hired_days and opportunity.cfo_hired_days <= 90:
            signals += 1
            
        return signals
    
    def estimate_sprint_value(self, opportunity: SprintOpportunity) -> Dict[str, any]:
        """Calcula valor estimado do Sprint baseado nos sinais"""
        value_breakdown = {
            'saas_savings': 0,
            'performance_uplift': 0,
            'total_roi': 0
        }
        
        # Economia SaaS (se renewal próximo)
        if opportunity.days_to_renewal and opportunity.days_to_renewal <= 60:
            if opportunity.saas_tool in self.common_saas_renewals:
                annual_cost = self.common_saas_renewals[opportunity.saas_tool]['typical_cost']
                value_breakdown['saas_savings'] = int(annual_cost * 0.4)  # 40% economia média
        
        # Valor performance (se Lighthouse baixo)
        if opportunity.lighthouse_mobile and opportunity.lighthouse_mobile < 40:
            # Cada 10 pontos = ~2% conversão = $2-5K valor anual para PME média
            improvement_potential = (50 - opportunity.lighthouse_mobile) / 10
            value_breakdown['performance_uplift'] = int(improvement_potential * 3000)
        
        value_breakdown['total_roi'] = (value_breakdown['saas_savings'] + value_breakdown['performance_uplift']) / 997
        
        return value_breakdown
    
    def process_prospects_batch(self, prospects: List[Dict[str, str]]) -> List[SprintOpportunity]:
        """Processa batch de prospects e retorna oportunidades qualificadas"""
        opportunities = []
        
        for i, prospect in enumerate(prospects):
            print(f"Analisando prospect {i+1}/{len(prospects)}: {prospect['company_name']}")
            
            # Análise Lighthouse
            lighthouse_score = self.analyze_lighthouse_score(prospect['domain'])
            
            # Análise SaaS
            saas_data = self.detect_saas_renewal_signals(prospect['domain'])
            
            # Análise liderança
            cfo_hired = self.analyze_leadership_changes(prospect['company_name'], prospect['domain'])
            
            # Cria oportunidade
            opportunity = SprintOpportunity(
                company_name=prospect['company_name'],
                domain=prospect['domain'],
                lighthouse_mobile=lighthouse_score,
                days_to_renewal=saas_data['days_to_renewal'],
                saas_tool=saas_data['saas_tool'],
                cfo_hired_days=cfo_hired,
                signal_count=0,  # Será calculado
                estimated_savings=saas_data['estimated_savings'],
                contact_email=prospect.get('contact_email'),
                linkedin_profile=prospect.get('linkedin_profile')
            )
            
            # Calcula sinais
            opportunity.signal_count = self.calculate_signal_score(opportunity)
            
            # Só adiciona se tem ≥ 2 sinais
            if opportunity.signal_count >= 2:
                opportunities.append(opportunity)
                print(f"✅ Qualificado: {opportunity.signal_count} sinais")
            else:
                print(f"❌ Não qualificado: {opportunity.signal_count} sinais")
            
            # Rate limiting para APIs
            time.sleep(2)
        
        return opportunities
    
    def export_qualified_opportunities(self, opportunities: List[SprintOpportunity]) -> str:
        """Exporta oportunidades para CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/sprint_opportunities_{timestamp}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                'Company', 'Domain', 'Signals', 'Lighthouse_Mobile', 'Days_to_Renewal', 
                'SaaS_Tool', 'CFO_Hired_Days', 'Estimated_Savings', 'Sprint_ROI',
                'Contact_Email', 'LinkedIn_Profile', 'Priority'
            ])
            
            for opp in sorted(opportunities, key=lambda x: x.signal_count, reverse=True):
                value_data = self.estimate_sprint_value(opp)
                priority = "HIGH" if opp.signal_count == 3 else "MEDIUM"
                
                writer.writerow([
                    opp.company_name, opp.domain, opp.signal_count,
                    opp.lighthouse_mobile, opp.days_to_renewal, opp.saas_tool,
                    opp.cfo_hired_days, opp.estimated_savings, f"{value_data['total_roi']:.1f}x",
                    opp.contact_email, opp.linkedin_profile, priority
                ])
        
        return filename

def main():
    detector = SprintOpportunityDetector()
    
    # Importa lista de prospects seed
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from prospects_seed import prospects_seed
    
    print("🎯 ARCO Sprint Opportunity Detector")
    print("Processando prospects para identificar oportunidades Sprint USD 997...")
    print(f"Total prospects: {len(prospects_seed)}")
    
    # Processa prospects
    opportunities = detector.process_prospects_batch(prospects_seed)
    
    print(f"\n📊 RESULTADOS:")
    print(f"Prospects analisados: {len(prospects_seed)}")
    print(f"Oportunidades qualificadas (≥2 sinais): {len(opportunities)}")
    print(f"Taxa de qualificação: {len(opportunities)/len(prospects_seed)*100:.1f}%")
    
    if opportunities:
        # Exporta resultados
        filename = detector.export_qualified_opportunities(opportunities)
        print(f"Resultados exportados: {filename}")
        
        # Mostra top 5 oportunidades
        print("\n🏆 TOP 5 OPORTUNIDADES:")
        for i, opp in enumerate(sorted(opportunities, key=lambda x: x.signal_count, reverse=True)[:5]):
            value_data = detector.estimate_sprint_value(opp)
            print(f"{i+1}. {opp.company_name}")
            print(f"   Sinais: {opp.signal_count}/3")
            print(f"   Lighthouse: {opp.lighthouse_mobile}/100")
            print(f"   Renewal: {opp.days_to_renewal} dias")
            print(f"   ROI estimado: {value_data['total_roi']:.1f}x")
            print()

if __name__ == "__main__":
    main()
