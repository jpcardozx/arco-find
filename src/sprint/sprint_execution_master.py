#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARCO Sprint Execution Master
Orquestra todo o pipeline Sprint USD 997 em um comando
"""

import os
import sys
import subprocess
import time
from datetime import datetime
import json
import csv

class SprintExecutionMaster:
    def __init__(self):
        self.sprint_dir = "src/sprint"
        self.results_dir = "results"
        self.target_prospects = 50
        self.target_calls = 5
        self.target_deals = 2
        
    def ensure_directories(self):
        """Garante que diretorios necessarios existem"""
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
            print(f"✅ Diretorio {self.results_dir} criado")
    
    def run_simple_detector(self):
        """Executa deteccao simples sem APIs externas"""
        print("Executando detector simplificado...")
        
        # Importa lista de prospects
        prospects_file = os.path.join(self.sprint_dir, "prospects_seed.py")
        if os.path.exists(prospects_file):
            sys.path.append(self.sprint_dir)
            from prospects_seed import prospects_seed
            
            # Simula analise com dados mock para demonstracao
            qualified_prospects = []
            
            for i, prospect in enumerate(prospects_seed[:10]):  # Limita a 10 para demo
                # Simula sinais detectados
                mock_signals = {
                    'lighthouse_mobile': 35 + (i * 5),  # Scores variaveis
                    'days_to_renewal': 45 if i % 3 == 0 else None,  # 1/3 tem renewal
                    'saas_tool': 'HubSpot' if i % 3 == 0 else 'WordPress',
                    'estimated_savings': 5000 + (i * 1000)
                }
                
                # Conta sinais (≥2 para qualificar)
                signal_count = 0
                if mock_signals['days_to_renewal'] and mock_signals['days_to_renewal'] <= 60:
                    signal_count += 1
                if mock_signals['lighthouse_mobile'] < 40:
                    signal_count += 1
                if i % 4 == 0:  # Simula novo CFO
                    signal_count += 1
                
                if signal_count >= 2:
                    qualified_prospects.append({
                        'Company': prospect['company_name'],
                        'Domain': prospect['domain'],
                        'Signals': signal_count,
                        'Lighthouse_Mobile': mock_signals['lighthouse_mobile'],
                        'Days_to_Renewal': mock_signals['days_to_renewal'],
                        'SaaS_Tool': mock_signals['saas_tool'],
                        'Estimated_Savings': mock_signals['estimated_savings'],
                        'Priority': 'HIGH' if signal_count == 3 else 'MEDIUM'
                    })
            
            # Exporta resultados
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.results_dir}/sprint_opportunities_{timestamp}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                if qualified_prospects:
                    writer = csv.DictWriter(file, fieldnames=qualified_prospects[0].keys())
                    writer.writeheader()
                    writer.writerows(qualified_prospects)
            
            print(f"✅ {len(qualified_prospects)} oportunidades qualificadas")
            print(f"📄 Resultados: {filename}")
            return True, filename
        
        return False, None
    
    def generate_outreach_scripts(self, opportunities_file):
        """Gera scripts de outreach baseados nas oportunidades"""
        print("Gerando scripts de outreach...")
        
        if not opportunities_file or not os.path.exists(opportunities_file):
            print("❌ Arquivo de oportunidades nao encontrado")
            return False
        
        # Le oportunidades
        opportunities = []
        with open(opportunities_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            opportunities = list(reader)
          # Gera scripts
        scripts = []
        for opp in opportunities[:min(len(opportunities), 10)]:  # Top 10 ou todos se menos
            # Determina urgency trigger
            urgency = ""
            if opp['Days_to_Renewal'] and opp['Days_to_Renewal'] != 'None':
                urgency = f"seu {opp['SaaS_Tool']} renova em {opp['Days_to_Renewal']} dias"
            elif int(opp['Lighthouse_Mobile']) < 40:
                urgency = f"site carregando {opp['Lighthouse_Mobile']}/100 mobile"
            else:
                urgency = "stack SaaS com vazamentos detectados"
            
            # Script LinkedIn personalizado
            linkedin_script = f"""Hey CEO da {opp['Company']}, {urgency}.

Gravei diagnostico rapido - voce esta perdendo conversoes/savings.

Sprint 5 dias: economizo ${int(float(opp['Estimated_Savings'])//1000)}k + otimizo performance.
Se nao entregar valor, devolvo USD 997.

15 min amanha 14h para mostrar plano especifico?"""

            # Email follow-up
            savings_k = int(float(opp['Estimated_Savings'])//1000)
            current_cost = int(float(opp['Estimated_Savings']))
            optimized_cost = int(current_cost * 0.6)
            
            email_script = f"""Subject: Saving ${savings_k}k antes do renewal

Ola!

Conforme prometido, diagnostico especifico {opp['Company']}:

METRICAS PRE vs POS-SPRINT:
• {opp['SaaS_Tool']}: ${current_cost:,} → ${optimized_cost:,} (40% economia)
• Lighthouse: {opp['Lighthouse_Mobile']}/100 → 65+/100
• ROI Sprint: 7.5x em 90 dias

GARANTIA RISK-REVERSAL:
✓ Se economia < 10%, reembolso integral D6
✓ Fee: $997 (Stripe no DocuSign)

Tenho slot amanha 14h ou quinta 10h.
Qual prefere para 15-min quick-win review?

[CALENDLY LINK]

Abs,
Joao Pedro"""

            scripts.append({
                'company': opp['Company'],
                'priority': opp['Priority'],
                'signals': opp['Signals'],
                'contact_email': opp.get('Contact_Email', f"ceo@{opp['Domain']}"),
                'linkedin_script': linkedin_script,
                'email_script': email_script,
                'estimated_value': opp['Estimated_Savings'],
                'urgency_trigger': urgency
            })
        
        # Exporta scripts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scripts_file = f"{self.results_dir}/sprint_outreach_scripts_{timestamp}.json"
        
        with open(scripts_file, 'w', encoding='utf-8') as file:
            json.dump(scripts, file, indent=2, ensure_ascii=False)
        
        print(f"✅ {len(scripts)} scripts gerados")
        print(f"📄 Scripts: {scripts_file}")
        return True, scripts_file
    
    def create_tracking_template(self):
        """Cria template de tracking"""
        print("Criando template de tracking...")
        
        timestamp = datetime.now().strftime("%Y%m%d")
        template_file = f"{self.results_dir}/sprint_pipeline_tracker_{timestamp}.csv"
        
        headers = [
            'Company', 'Contact_Name', 'Stage', 'Touch_1_Date', 'Touch_2_Date',
            'Reply_Date', 'Call_Date', 'Close_Date', 'Signal_Count', 
            'Estimated_Value', 'Actual_Value', 'Notes'
        ]
        
        with open(template_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            
            # Adiciona linhas exemplo
            example_data = [
                ['TechFlow Solutions', 'John CEO', 'contacted', '2025-06-18', '', '', '', '', '3', '7500', '', 'LinkedIn video sent'],
                ['MapleLeaf Consulting', 'Sarah CFO', 'replied', '2025-06-18', '2025-06-20', '2025-06-19', '', '', '2', '5200', '', 'Positive response'],
                ['Northern Digital', 'Mike Ops', 'call_scheduled', '2025-06-18', '2025-06-20', '2025-06-19', '2025-06-21', '', '3', '8900', '', 'Call Thu 2pm']
            ]
            
            for row in example_data:
                writer.writerow(row)
        
        print(f"✅ Template criado: {template_file}")
        return True, template_file
    
    def generate_execution_guide(self):
        """Gera guia de execucao"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        guide_file = f"{self.results_dir}/sprint_execution_guide_{timestamp}.md"
        
        guide_content = f"""# 🎯 ARCO SPRINT EXECUTION GUIDE
Generated: {datetime.now().strftime('%d/%m/%Y %H:%M')}

## ⚡ OBJETIVO: 5 CALLS / 2 VENDAS EM 14 DIAS

### CHECKLIST DIARIO

#### DIA 1-2: SETUP & PRIMEIRA ONDA
- [x] Sistema Sprint configurado
- [ ] Gravar 10 Looms LinkedIn (35s cada)
- [ ] Enviar 10 DMs personalizados
- [ ] Configurar Calendly
- [ ] Update tracking CSV

#### DIA 3-4: FOLLOW-UP
- [ ] Monitorar opens/replies
- [ ] Gravar mais 10 Looms  
- [ ] Enviar follow-up emails
- [ ] Agendar calls

#### DIA 5-7: CALL EXECUTION
- [ ] Executar calls
- [ ] Enviar contratos
- [ ] Process payments

### SCRIPTS PRONTOS

Scripts personalizados foram gerados nos arquivos JSON.
Use copy/paste para LinkedIn DMs e emails.

### METRICAS ALVO

- Prospects: 50
- Reply rate: ≥20%
- Calls: ≥5
- Deals: ≥2
- Revenue: $1,994+

### PROXIMOS PASSOS

1. Gravar Looms com scripts
2. Enviar DMs LinkedIn
3. Monitorar tracking CSV
4. Executar calls estruturadas
"""
        
        with open(guide_file, 'w', encoding='utf-8') as file:
            file.write(guide_content)
        
        return guide_file

def main():
    print("🚀 ARCO SPRINT EXECUTION MASTER")
    print("━" * 60)
    print("Objetivo: 5 calls / 2 Sprint USD 997 em 14 dias")
    print("━" * 60)
    
    master = SprintExecutionMaster()
    master.ensure_directories()
    
    success_count = 0
    
    # Fase 1: Deteccao simplificada
    print("\n🔍 FASE 1: DETECCAO DE OPORTUNIDADES")
    print("━" * 50)
    success, opp_file = master.run_simple_detector()
    if success:
        success_count += 1
    
    # Fase 2: Outreach
    print("\n📧 FASE 2: GERACAO DE OUTREACH")
    print("━" * 50)
    success, scripts_file = master.generate_outreach_scripts(opp_file)
    if success:
        success_count += 1
    
    # Fase 3: Tracking
    print("\n📊 FASE 3: SETUP TRACKING")
    print("━" * 50)
    success, tracking_file = master.create_tracking_template()
    if success:
        success_count += 1
    
    # Gera guia
    guide_file = master.generate_execution_guide()
    
    print(f"\n🎯 EXECUTION MASTER COMPLETED")
    print(f"Fases concluidas: {success_count}/3")
    print(f"📋 Execution Guide: {guide_file}")
    
    if success_count >= 2:
        print(f"\n✅ SISTEMA READY FOR EXECUTION!")
        print("🎬 Proximo passo: Gravar primeiro Loom")
        print("📱 Scripts personalizados prontos")
        print("⏰ Meta: 2 deals em 14 dias")
        print("\n🚀 QUICK START:")
        print("1. Gravar 10 Looms (35s cada)")
        print("2. Enviar DMs LinkedIn")
        print("3. Monitorar replies")
        print("4. Schedule calls")
    else:
        print(f"\n⚠️ Sistema parcialmente configurado")
        print("Use execution guide para proximos passos")

if __name__ == "__main__":
    main()
