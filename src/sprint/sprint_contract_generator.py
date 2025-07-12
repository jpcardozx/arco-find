#!/usr/bin/env python3
"""
ARCO Sprint Contract Generator
Gera contratos de 1 página para Sprint USD 997 com garantia risk-reversal
"""

from dataclasses import dataclass
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import json

@dataclass
class SprintContract:
    client_company: str
    client_contact: str
    client_email: str
    sprint_focus: str  # 'saas_optimization' ou 'performance_optimization'
    estimated_savings: int
    guarantee_threshold: int
    start_date: datetime
    delivery_date: datetime
    contract_id: str

class SprintContractGenerator:
    def __init__(self):
        self.sprint_fee = 997
        self.guarantee_days = 7
        self.min_guarantee_percentage = 10  # 10% mínimo de economia/ganho
        
    def generate_contract_terms(self, opportunity: Dict) -> Dict:
        """Gera termos específicos do contrato baseado na oportunidade"""
        company = opportunity['Company']
        estimated_savings = int(float(opportunity['Estimated_Savings'])) if opportunity['Estimated_Savings'] != '0' else 7500
        saas_tool = opportunity['SaaS_Tool']
        lighthouse_score = int(opportunity['Lighthouse_Mobile']) if opportunity['Lighthouse_Mobile'] != 'None' else 35
        
        # Define foco do sprint baseado nos sinais
        sprint_focus = 'hybrid'  # Padrão: SaaS + Performance
        primary_deliverable = f"Renegociação {saas_tool} + otimização performance"
        
        if opportunity['Days_to_Renewal'] and opportunity['Days_to_Renewal'] != 'None':
            sprint_focus = 'saas_optimization'
            primary_deliverable = f"Renegociação/downgrade {saas_tool}"
        elif lighthouse_score < 40:
            sprint_focus = 'performance_optimization'
            primary_deliverable = "Otimização performance (Next.js + Cloudflare)"
        
        # Calcula garantias
        guarantee_threshold = max(int(estimated_savings * 0.1), 1500)  # Mínimo $1,500
        
        terms = {
            'client_info': {
                'company': company,
                'contact': 'CEO',  # Em produção, seria extraído
                'email': f"ceo@{opportunity['Domain']}",
                'domain': opportunity['Domain']
            },
            'sprint_details': {
                'focus': sprint_focus,
                'primary_deliverable': primary_deliverable,
                'timeline': '5 dias úteis',
                'start_date': datetime.now() + timedelta(days=1),
                'delivery_date': datetime.now() + timedelta(days=6)
            },
            'deliverables': self._get_deliverables_by_focus(sprint_focus, saas_tool, lighthouse_score),
            'investment': {
                'fee': self.sprint_fee,
                'payment_terms': 'Upfront via Stripe no DocuSign',
                'refund_policy': f'Reembolso integral se economia/ganho ≤ {self.min_guarantee_percentage}%'
            },
            'guarantees': {
                'minimum_value': guarantee_threshold,
                'measurement_period': '90 dias',
                'refund_trigger': f'Saving < ${guarantee_threshold}',
                'delivery_timeline': f'{self.guarantee_days} dias'
            },
            'estimated_outcomes': {
                'year_1_savings': estimated_savings,
                'roi_multiple': f"{estimated_savings / self.sprint_fee:.1f}×",
                'payback_period': '30 dias'
            }
        }
        
        return terms
    
    def _get_deliverables_by_focus(self, focus: str, saas_tool: str, lighthouse_score: int) -> List[str]:
        """Define deliverables específicos baseado no foco do sprint"""
        deliverables = []
        
        if focus in ['saas_optimization', 'hybrid']:
            deliverables.extend([
                f"✓ Análise completa stack {saas_tool}",
                f"✓ Renegociação/downgrade {saas_tool}",
                "✓ Implementação ferramentas alternativas",
                "✓ Migração de dados (se necessário)",
                "✓ Documentação savings achieved"
            ])
        
        if focus in ['performance_optimization', 'hybrid']:
            improvement_points = min(25, 50 - lighthouse_score)
            deliverables.extend([
                "✓ Performance audit completo",
                f"✓ Implementação Next.js optimizations",
                "✓ Cloudflare CDN + rules setup",
                f"✓ Target: +{improvement_points} pontos Lighthouse",
                "✓ Core Web Vitals optimization"
            ])
        
        # Deliverables universais
        deliverables.extend([
            "✓ Handoff completo com documentation",
            "✓ 30 dias support pós-delivery",
            "✓ ROI measurement & reporting"
        ])
        
        return deliverables
    
    def generate_contract_document(self, terms: Dict) -> str:
        """Gera documento de contrato completo"""
        contract_id = f"ARCO-SPRINT-{datetime.now().strftime('%Y%m%d%H%M')}"
        
        contract_doc = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           ARCO SPRINT AGREEMENT                              ║
║                         Contract #{contract_id}                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

CLIENT INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Company:    {terms['client_info']['company']}
Contact:    {terms['client_info']['contact']}
Email:      {terms['client_info']['email']}
Domain:     {terms['client_info']['domain']}
Date:       {datetime.now().strftime('%B %d, %Y')}

SPRINT SCOPE & DELIVERABLES  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Primary Focus:      {terms['sprint_details']['focus'].replace('_', ' ').title()}
Timeline:           {terms['sprint_details']['timeline']}
Start Date:         {terms['sprint_details']['start_date'].strftime('%B %d, %Y')}
Delivery Date:      {terms['sprint_details']['delivery_date'].strftime('%B %d, %Y')}

PRIMARY DELIVERABLE:
{terms['sprint_details']['primary_deliverable']}

COMPLETE DELIVERABLES LIST:
"""
        
        for deliverable in terms['deliverables']:
            contract_doc += f"{deliverable}\n"
        
        contract_doc += f"""
INVESTMENT & PAYMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sprint Fee:         ${terms['investment']['fee']:,} USD
Payment:            {terms['investment']['payment_terms']}
Refund Policy:      {terms['investment']['refund_policy']}

PERFORMANCE GUARANTEES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Minimum Value:      ${terms['guarantees']['minimum_value']:,}
Measurement:        {terms['guarantees']['measurement_period']}
Refund Trigger:     {terms['guarantees']['refund_trigger']}
Timeline:           Delivered within {terms['guarantees']['delivery_timeline']}

ESTIMATED OUTCOMES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Year 1 Savings:     ${terms['estimated_outcomes']['year_1_savings']:,}
ROI Multiple:       {terms['estimated_outcomes']['roi_multiple']}
Payback Period:     {terms['estimated_outcomes']['payback_period']}

TERMS & CONDITIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. SCOPE: This Sprint focuses exclusively on the deliverables listed above.
   Additional work requires separate agreement.

2. TIMELINE: Work begins on Start Date and concludes on Delivery Date.
   Client provides necessary access within 24h of contract signing.

3. GUARANTEE: If measured savings/gains are below ${terms['guarantees']['minimum_value']:,}
   within {terms['guarantees']['measurement_period']}, full refund will be processed within 5 business days.

4. PAYMENT: Full payment due upon contract signing via Stripe link provided.
   No work begins until payment is confirmed.

5. DELIVERY: All deliverables provided via Loom video + documentation.
   30-day post-delivery support included.

6. MEASUREMENT: Savings measured through:
   - SaaS billing reduction (before/after invoices)
   - Performance improvements (Lighthouse scores)
   - Conversion rate improvements (where applicable)

7. REFUND PROCESS: Client submits refund request with evidence within
   {terms['guarantees']['measurement_period']}. ARCO reviews within 48h and processes if valid.

ACCEPTANCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
By signing below, both parties agree to the terms outlined above.

CLIENT SIGNATURE                           DATE
_________________________________          _______________

ARCO SIGNATURE                             DATE  
_________________________________          _______________
João Pedro - ARCO Strategic Intelligence

═══════════════════════════════════════════════════════════════════════════════
This agreement constitutes the complete understanding between parties.
Questions? Email: joao@arco.com | WhatsApp: +55 11 99999-9999
═══════════════════════════════════════════════════════════════════════════════
"""
        
        return contract_doc
    
    def generate_docusign_template(self, terms: Dict) -> Dict:
        """Gera template JSON para integração DocuSign"""
        template = {
            'emailSubject': f'ARCO Sprint Agreement - {terms["client_info"]["company"]}',
            'documents': [{
                'documentBase64': '',  # PDF seria convertido para base64
                'documentId': '1',
                'fileExtension': 'pdf',
                'name': f'ARCO_Sprint_Agreement_{terms["client_info"]["company"]}.pdf'
            }],
            'recipients': {
                'signers': [{
                    'email': terms['client_info']['email'],
                    'name': terms['client_info']['contact'],
                    'recipientId': '1',
                    'tabs': {
                        'signHereTabs': [{
                            'anchorString': 'CLIENT SIGNATURE',
                            'anchorXOffset': '20',
                            'anchorYOffset': '-10'
                        }],
                        'dateSignedTabs': [{
                            'anchorString': 'DATE',
                            'anchorXOffset': '20',
                            'anchorYOffset': '-10'
                        }]
                    }
                }]
            },
            'status': 'sent'
        }
        
        return template
    
    def export_contract_package(self, opportunity: Dict) -> Dict[str, str]:
        """Exporta pacote completo do contrato"""
        # Gera termos
        terms = self.generate_contract_terms(opportunity)
        
        # Gera documento
        contract_doc = self.generate_contract_document(terms)
        
        # Gera template DocuSign
        docusign_template = self.generate_docusign_template(terms)
        
        # Salva arquivos
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        company_clean = terms['client_info']['company'].replace(' ', '_').replace(',', '')
        
        # Contrato em texto
        contract_file = f"results/sprint_contract_{company_clean}_{timestamp}.txt"
        with open(contract_file, 'w', encoding='utf-8') as file:
            file.write(contract_doc)
        
        # Template DocuSign
        docusign_file = f"results/sprint_docusign_{company_clean}_{timestamp}.json"
        with open(docusign_file, 'w', encoding='utf-8') as file:
            json.dump(docusign_template, file, indent=2)
        
        # Stripe payment link (mock)
        stripe_link = f"https://buy.stripe.com/sprint-{company_clean.lower()}-997"
        
        return {
            'contract_file': contract_file,
            'docusign_template': docusign_file,
            'stripe_link': stripe_link,
            'estimated_value': terms['estimated_outcomes']['year_1_savings'],
            'roi_multiple': terms['estimated_outcomes']['roi_multiple']
        }

def main():
    generator = SprintContractGenerator()
    
    # Exemplo de oportunidade (normalmente viria do pipeline)
    example_opportunity = {
        'Company': 'TechFlow Solutions Inc.',
        'Domain': 'techflow.ca',
        'Lighthouse_Mobile': '32',
        'Days_to_Renewal': '45',
        'SaaS_Tool': 'HubSpot',
        'Estimated_Savings': '7480',
        'Priority': 'HIGH'
    }
    
    print("📄 ARCO Sprint Contract Generator")
    print(f"Gerando contrato para: {example_opportunity['Company']}")
    
    # Gera pacote completo
    contract_package = generator.export_contract_package(example_opportunity)
    
    print(f"\n✅ CONTRATO GERADO:")
    print(f"📄 Documento: {contract_package['contract_file']}")
    print(f"📧 DocuSign Template: {contract_package['docusign_template']}")
    print(f"💳 Stripe Link: {contract_package['stripe_link']}")
    print(f"💰 Valor Estimado: ${contract_package['estimated_value']:,}")
    print(f"📈 ROI: {contract_package['roi_multiple']}")
    
    print(f"\n🚀 PRÓXIMOS PASSOS:")
    print("1. Revisar contrato gerado")
    print("2. Converter para PDF via DocuSign")
    print("3. Configurar Stripe payment link")
    print("4. Enviar para assinatura")

if __name__ == "__main__":
    main()
