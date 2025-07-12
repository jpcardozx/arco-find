#!/usr/bin/env python3
"""
ARCO Sprint Outreach Engine
Gera mensagens personalizadas para LinkedIn e email baseadas nos 3 sinais detectados
"""

import json
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import csv

@dataclass
class OutreachMessage:
    prospect_name: str
    company_name: str
    channel: str  # 'linkedin_video' ou 'email_followup'
    message_type: str  # 'touch_1' ou 'touch_2'
    subject: Optional[str]
    message_body: str
    urgency_trigger: str
    value_prop: str
    cta: str

class SprintOutreachEngine:
    def __init__(self):
        self.sprint_fee = 997
        self.guarantee_days = 7
        self.min_savings_guarantee = 1500
        
    def load_qualified_opportunities(self, csv_file: str) -> List[Dict]:
        """Carrega oportunidades qualificadas do CSV"""
        opportunities = []
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                opportunities.append(row)
        return opportunities
    
    def generate_linkedin_video_script(self, opportunity: Dict) -> OutreachMessage:
        """Gera script para vídeo LinkedIn (Toque 1 - 35 segundos)"""
        company = opportunity['Company']
        domain = opportunity['Domain']
        lighthouse_score = opportunity['Lighthouse_Mobile']
        days_to_renewal = opportunity['Days_to_Renewal']
        saas_tool = opportunity['SaaS_Tool']
        estimated_savings = opportunity['Estimated_Savings']
        
        # Personaliza baseado nos sinais principais
        urgency_trigger = ""
        value_specific = ""
        
        if days_to_renewal and days_to_renewal != 'None':
            urgency_trigger = f"seu contrato {saas_tool} renova em {days_to_renewal} dias"
            value_specific = f"corto a fatura do {saas_tool}"
        elif lighthouse_score and int(lighthouse_score) < 40:
            urgency_trigger = f"seu site carrega em {lighthouse_score}/100 mobile"
            value_specific = "subo page-speed 15+ pontos"
        else:
            urgency_trigger = "sua stack de ferramentas tem vazamentos"
            value_specific = "encontro economias escondidas"
        
        # Nome do contato (extrair do email ou usar CEO genérico)
        contact_name = "CEO"  # Em produção, seria extraído de LinkedIn/email
        
        message_body = f"""Hey {contact_name}, {urgency_trigger}.

Gravei esse diagnóstico rápido: {lighthouse_score}/100 mobile – você está pagando por leads que não carregem.

Eu faço um sprint de 5 dias: {value_specific} + otimizo a conversão.
Se não entregar em {self.guarantee_days} dias, devolvo os USD {self.sprint_fee}.

15 min amanhã às 14h para mostrar o plano específico?"""

        return OutreachMessage(
            prospect_name=contact_name,
            company_name=company,
            channel='linkedin_video',
            message_type='touch_1',
            subject=None,
            message_body=message_body,
            urgency_trigger=urgency_trigger,
            value_prop=value_specific,
            cta="15 min amanhã às 14h?"
        )
    
    def generate_email_followup(self, opportunity: Dict) -> OutreachMessage:
        """Gera email follow-up (Toque 2 - 48h depois)"""
        company = opportunity['Company']
        domain = opportunity['Domain']
        lighthouse_score = int(opportunity['Lighthouse_Mobile']) if opportunity['Lighthouse_Mobile'] != 'None' else 30
        days_to_renewal = opportunity['Days_to_Renewal']
        saas_tool = opportunity['SaaS_Tool']
        estimated_savings = int(float(opportunity['Estimated_Savings'])) if opportunity['Estimated_Savings'] != '0' else 12000
        sprint_roi = opportunity['Sprint_ROI']
        
        # Calcula data de renovação
        renewal_date = "30 jul 25"  # Simulado
        if days_to_renewal and days_to_renewal != 'None':
            future_date = datetime.now() + timedelta(days=int(days_to_renewal))
            renewal_date = future_date.strftime("%d %b %y")
        
        subject = f"Saving de ${estimated_savings//1000}k antes do dia {renewal_date}"
        
        # Monta tabela de métricas
        current_lighthouse = lighthouse_score
        target_lighthouse = min(85, current_lighthouse + 25)
        current_lcp = round(4.8 - (current_lighthouse * 0.03), 1)  # Correlação simulada
        target_lcp = max(2.5, current_lcp - 1.5)
        
        saas_annual = estimated_savings if estimated_savings > 5000 else 18228
        saas_optimized = int(saas_annual * 0.6)  # 40% economia
        
        message_body = f"""Olá!

Como prometido, anexo o diagnóstico específico para {company}.

MÉTRICAS PRÉ vs PÓS-SPRINT:

| Métrica                    | Agora      | Meta pós-sprint | Fonte                     |
|---------------------------|------------|-----------------|---------------------------|
| {saas_tool} Renewal (12m) | ${saas_annual:,} | ${saas_optimized:,}     | Proposta {saas_tool}, tier downgrade |
| Mobile LCP                | {current_lcp}s     | {target_lcp}s           | Lighthouse {datetime.now().strftime('%d %b %y')}    |
| ROI sprint                | —          | {sprint_roi} em 90d    | Planilha anexa            |

GARANTIA SPRINT:
✓ Se economia/ganho ≤ 10%, reembolso integral no D6
✓ Kickoff amanhã → handoff completo em 5 dias úteis  
✓ Fee: ${self.sprint_fee} (Stripe no DocuSign)

Tenho horário livre amanhã 14h ou quinta 10h.
Qual prefere para 15-min quick-win review?

[CALENDLY LINK]

Abs,
João Pedro"""

        return OutreachMessage(
            prospect_name="CEO",  # Em produção, seria extraído
            company_name=company,
            channel='email_followup',
            message_type='touch_2',
            subject=subject,
            message_body=message_body,
            urgency_trigger=f"renovação em {days_to_renewal} dias",
            value_prop=f"${estimated_savings//1000}k economia",
            cta="Calendly - 15-min quick-win review"
        )
    
    def generate_slide_proposal(self, opportunity: Dict) -> Dict:
        """Gera slide de proposta (1 página) para anexar no email"""
        company = opportunity['Company']
        lighthouse_score = int(opportunity['Lighthouse_Mobile']) if opportunity['Lighthouse_Mobile'] != 'None' else 30
        estimated_savings = int(float(opportunity['Estimated_Savings'])) if opportunity['Estimated_Savings'] != '0' else 12000
        saas_tool = opportunity['SaaS_Tool']
        
        proposal_data = {
            'company': company,
            'analysis_date': datetime.now().strftime('%d %b %Y'),
            'current_metrics': {
                'lighthouse_mobile': lighthouse_score,
                'lcp_seconds': round(4.8 - (lighthouse_score * 0.03), 1),
                'saas_annual_cost': estimated_savings if estimated_savings > 5000 else 18228,
                'saas_tool': saas_tool or 'HubSpot'
            },
            'sprint_targets': {
                'lighthouse_improvement': min(85, lighthouse_score + 25),
                'lcp_improvement': 2.5,
                'saas_savings': int((estimated_savings if estimated_savings > 5000 else 18228) * 0.4),
                'timeline': '5 dias úteis'
            },
            'sprint_details': {
                'fee': self.sprint_fee,
                'guarantee': f'Reembolso integral se saving < ${self.min_savings_guarantee}',
                'deliverables': [
                    f'Renegociação/downgrade {saas_tool or "SaaS principal"}',
                    'Performance patch (Next.js + Cloudflare rules)',
                    'Handoff completo com documentação'
                ]
            },
            'roi_calculation': {
                'sprint_cost': self.sprint_fee,
                'year_1_value': estimated_savings if estimated_savings > 5000 else 7480,
                'roi_multiple': f"{((estimated_savings if estimated_savings > 5000 else 7480) / self.sprint_fee):.1f}×"
            }
        }
        
        return proposal_data
    
    def generate_outreach_sequence(self, csv_file: str) -> List[Dict]:
        """Gera sequência completa de outreach para todas as oportunidades"""
        opportunities = self.load_qualified_opportunities(csv_file)
        outreach_sequence = []
        
        for opportunity in opportunities:
            # Mensagem 1: LinkedIn Video
            linkedin_msg = self.generate_linkedin_video_script(opportunity)
            
            # Mensagem 2: Email Follow-up
            email_msg = self.generate_email_followup(opportunity)
            
            # Proposta anexa
            proposal = self.generate_slide_proposal(opportunity)
            
            outreach_sequence.append({
                'opportunity': opportunity,
                'touch_1_linkedin': linkedin_msg.__dict__,
                'touch_2_email': email_msg.__dict__,
                'proposal_slide': proposal
            })
        
        return outreach_sequence
    
    def export_outreach_scripts(self, outreach_sequence: List[Dict]) -> str:
        """Exporta scripts de outreach para execução"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/sprint_outreach_scripts_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(outreach_sequence, file, indent=2, ensure_ascii=False)
        
        # Também exporta versão CSV para execução rápida
        csv_filename = f"results/sprint_outreach_execution_{timestamp}.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                'Company', 'Priority', 'LinkedIn_Script', 'Email_Subject', 
                'Email_Body', 'Estimated_Value', 'Status', 'Notes'
            ])
            
            for seq in outreach_sequence:
                opp = seq['opportunity']
                touch1 = seq['touch_1_linkedin']
                touch2 = seq['touch_2_email']
                
                writer.writerow([
                    opp['Company'],
                    opp['Priority'],
                    touch1['message_body'].replace('\n', ' | '),
                    touch2['subject'],
                    touch2['message_body'][:200] + '...',
                    opp['Estimated_Savings'],
                    'READY',
                    f"Signals: {opp['Signals']}/3"
                ])
        
        return filename, csv_filename

def main():
    # Verifica se existe arquivo de oportunidades
    import os
    results_dir = "results"
    csv_files = [f for f in os.listdir(results_dir) if f.startswith("sprint_opportunities_")]
    
    if not csv_files:
        print("❌ Nenhum arquivo de oportunidades encontrado.")
        print("Execute primeiro: python src/sprint/sprint_opportunity_detector.py")
        return
    
    # Pega o arquivo mais recente
    latest_file = max([f"{results_dir}/{f}" for f in csv_files], key=os.path.getctime)
    
    print("🎯 ARCO Sprint Outreach Generator")
    print(f"Carregando oportunidades de: {latest_file}")
    
    engine = SprintOutreachEngine()
    
    # Gera sequência de outreach
    outreach_sequence = engine.generate_outreach_sequence(latest_file)
    
    # Exporta scripts
    json_file, csv_file = engine.export_outreach_scripts(outreach_sequence)
    
    print(f"\n📊 OUTREACH GERADO:")
    print(f"Total de sequências: {len(outreach_sequence)}")
    print(f"Scripts completos: {json_file}")
    print(f"Execução rápida: {csv_file}")
    
    # Mostra preview dos primeiros 3 scripts
    print("\n🎬 PREVIEW - TOP 3 LINKEDIN SCRIPTS:")
    for i, seq in enumerate(outreach_sequence[:3]):
        opp = seq['opportunity']
        script = seq['touch_1_linkedin']['message_body']
        print(f"\n{i+1}. {opp['Company']} ({opp['Signals']} sinais)")
        print("-" * 50)
        print(script)
    
    print(f"\n✅ Pronto para execução!")
    print("1. Grave videos Loom com os scripts LinkedIn")
    print("2. Envie DMs personalizados") 
    print("3. Monitore opens para follow-up email")
    print("4. Agende calls através Calendly")

if __name__ == "__main__":
    main()
