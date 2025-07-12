#!/usr/bin/env python3
"""
ARCO Sprint Pipeline Tracker
Monitora KPIs e progressão do pipeline Sprint USD 997
"""

import json
import csv
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, timedelta

@dataclass
class SprintLead:
    company_name: str
    contact_name: str
    stage: str  # 'contacted', 'replied', 'call_scheduled', 'proposal_sent', 'closed_won', 'closed_lost'
    touch_1_date: Optional[datetime]
    touch_2_date: Optional[datetime]
    reply_date: Optional[datetime]
    call_date: Optional[datetime]
    close_date: Optional[datetime]
    signal_count: int
    estimated_value: int
    actual_value: Optional[int]
    notes: str

class SprintPipelineTracker:
    def __init__(self):
        self.target_metrics = {
            'total_prospects': 50,
            'reply_rate_target': 0.20,  # 20%
            'calls_target': 5,
            'close_rate_target': 0.40,  # 40%
            'closed_deals_target': 2,
            'timeline_days': 14
        }
        
    def load_pipeline_data(self, csv_file: str) -> List[SprintLead]:
        """Carrega dados do pipeline de um CSV tracking"""
        leads = []
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    lead = SprintLead(
                        company_name=row['Company'],
                        contact_name=row.get('Contact_Name', 'CEO'),
                        stage=row['Stage'],
                        touch_1_date=datetime.fromisoformat(row['Touch_1_Date']) if row['Touch_1_Date'] else None,
                        touch_2_date=datetime.fromisoformat(row['Touch_2_Date']) if row['Touch_2_Date'] else None,
                        reply_date=datetime.fromisoformat(row['Reply_Date']) if row['Reply_Date'] else None,
                        call_date=datetime.fromisoformat(row['Call_Date']) if row['Call_Date'] else None,
                        close_date=datetime.fromisoformat(row['Close_Date']) if row['Close_Date'] else None,
                        signal_count=int(row['Signal_Count']),
                        estimated_value=int(row['Estimated_Value']),
                        actual_value=int(row['Actual_Value']) if row['Actual_Value'] else None,
                        notes=row.get('Notes', '')
                    )
                    leads.append(lead)
        except FileNotFoundError:
            print("Arquivo de pipeline não encontrado. Criando novo...")
            return []
        
        return leads
    
    def calculate_pipeline_metrics(self, leads: List[SprintLead]) -> Dict:
        """Calcula métricas atuais do pipeline"""
        total_contacted = len([l for l in leads if l.touch_1_date])
        total_replied = len([l for l in leads if l.reply_date])
        total_calls = len([l for l in leads if l.call_date])
        total_closed_won = len([l for l in leads if l.stage == 'closed_won'])
        total_closed_lost = len([l for l in leads if l.stage == 'closed_lost'])
        
        # Calcula taxas
        reply_rate = total_replied / max(total_contacted, 1)
        call_rate = total_calls / max(total_replied, 1)
        close_rate = total_closed_won / max(total_calls, 1) if total_calls > 0 else 0
        
        # Revenue metrics
        total_revenue = sum([l.actual_value for l in leads if l.actual_value])
        avg_deal_size = total_revenue / max(total_closed_won, 1) if total_closed_won > 0 else 0
        
        return {
            'total_prospects': len(leads),
            'total_contacted': total_contacted,
            'total_replied': total_replied,
            'total_calls': total_calls,
            'total_closed_won': total_closed_won,
            'total_closed_lost': total_closed_lost,
            'reply_rate': reply_rate,
            'call_rate': call_rate,
            'close_rate': close_rate,
            'total_revenue': total_revenue,
            'avg_deal_size': avg_deal_size
        }
    
    def generate_daily_tracker_template(self) -> str:
        """Gera template CSV para tracking diário"""
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"results/sprint_pipeline_tracker_{timestamp}.csv"
        
        # Cabeçalhos do tracking
        headers = [
            'Company', 'Contact_Name', 'Stage', 'Touch_1_Date', 'Touch_2_Date',
            'Reply_Date', 'Call_Date', 'Close_Date', 'Signal_Count', 
            'Estimated_Value', 'Actual_Value', 'Notes'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            
            # Adiciona algumas linhas exemplo para demonstração
            example_data = [
                ['TechFlow Solutions', 'John CEO', 'contacted', '2025-06-18', '', '', '', '', '3', '7500', '', 'LinkedIn video sent'],
                ['MapleLeaf Consulting', 'Sarah CFO', 'replied', '2025-06-18', '2025-06-20', '2025-06-19', '', '', '2', '5200', '', 'Positive response, scheduling call'],
                ['Northern Digital', 'Mike Ops', 'call_scheduled', '2025-06-18', '2025-06-20', '2025-06-19', '2025-06-21', '', '3', '8900', '', 'Call Thu 2pm - very interested']
            ]
            
            for row in example_data:
                writer.writerow(row)
        
        return filename
    
    def analyze_performance_vs_targets(self, leads: List[SprintLead]) -> Dict:
        """Analisa performance atual vs targets"""
        current_metrics = self.calculate_pipeline_metrics(leads)
        
        performance = {}
        
        # Compara com targets
        performance['reply_rate'] = {
            'current': current_metrics['reply_rate'],
            'target': self.target_metrics['reply_rate_target'],
            'status': '✅' if current_metrics['reply_rate'] >= self.target_metrics['reply_rate_target'] else '⚠️',
            'gap': current_metrics['reply_rate'] - self.target_metrics['reply_rate_target']
        }
        
        performance['calls_scheduled'] = {
            'current': current_metrics['total_calls'],
            'target': self.target_metrics['calls_target'],
            'status': '✅' if current_metrics['total_calls'] >= self.target_metrics['calls_target'] else '⚠️',
            'gap': current_metrics['total_calls'] - self.target_metrics['calls_target']
        }
        
        performance['deals_closed'] = {
            'current': current_metrics['total_closed_won'],
            'target': self.target_metrics['closed_deals_target'],
            'status': '✅' if current_metrics['total_closed_won'] >= self.target_metrics['closed_deals_target'] else '⚠️',
            'gap': current_metrics['total_closed_won'] - self.target_metrics['closed_deals_target']
        }
        
        performance['close_rate'] = {
            'current': current_metrics['close_rate'],
            'target': self.target_metrics['close_rate_target'],
            'status': '✅' if current_metrics['close_rate'] >= self.target_metrics['close_rate_target'] else '⚠️',
            'gap': current_metrics['close_rate'] - self.target_metrics['close_rate_target']
        }
        
        return performance
    
    def generate_daily_checklist(self, day_number: int) -> Dict:
        """Gera checklist diário baseado no dia do sprint"""
        checklists = {
            1: {
                'day': 1,
                'focus': 'Setup & First Wave',
                'tasks': [
                    '✅ Rodar workflow 50 domínios (sprint_opportunity_detector.py)',
                    '⏳ Gravar 10 primeiros Looms (35s cada)',
                    '⏳ Enviar 10 DMs LinkedIn (manual)',
                    '📋 Setup tracking CSV',
                    '📋 Configurar Calendly para calls'
                ]
            },
            2: {
                'day': 2,
                'focus': 'Monitor & Follow-up Setup',
                'tasks': [
                    '✅ Monitorar opens LinkedIn',
                    '⏳ Gravar + enviar mais 10 Looms',
                    '📧 Preparar templates email follow-up',
                    '📊 Update tracking sheet',
                    '📞 Responder primeiras replies'
                ]
            },
            3: {
                'day': 3,
                'focus': 'Follow-up Wave',
                'tasks': [
                    '📧 Enviar follow-up emails (quem abriu)',
                    '⏳ Completar 20 Looms restantes',
                    '📞 Agendar calls dos interessados',
                    '📊 Análise mid-week performance',
                    '🔧 Ajustar messaging se necessário'
                ]
            },
            4: {
                'day': 4,
                'focus': 'Call Preparation',
                'tasks': [
                    '📞 Preparar materials para calls',
                    '📧 Mais follow-ups email',
                    '📊 Update pipeline metrics',
                    '🎯 Priorizar top prospects',
                    '📋 DocuSign + Stripe setup'
                ]
            },
            5: {
                'day': 5,
                'focus': 'Call Execution',
                'tasks': [
                    '📞 Executar calls agendadas',
                    '📄 Enviar propostas DocuSign',
                    '📊 Track conversion rates',
                    '📧 Follow-up pós-call',
                    '🎯 Focus em closing'
                ]
            }
        }
        
        return checklists.get(day_number, {
            'day': day_number,
            'focus': 'Follow-up & Optimization',
            'tasks': [
                '📞 Continue call execution',
                '📄 Process signed contracts',
                '📊 Update metrics daily',
                '🔧 Optimize based on feedback',
                '🎯 Push for closes'
            ]
        })
    
    def export_performance_dashboard(self, leads: List[SprintLead]) -> str:
        """Exporta dashboard de performance"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/sprint_dashboard_{timestamp}.txt"
        
        metrics = self.calculate_pipeline_metrics(leads)
        performance = self.analyze_performance_vs_targets(leads)
        
        dashboard = f"""
🎯 ARCO SPRINT PERFORMANCE DASHBOARD
Generated: {datetime.now().strftime('%d/%m/%Y %H:%M')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 CURRENT METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Prospects Analyzed: {metrics['total_prospects']}
Total Contacted (Touch 1): {metrics['total_contacted']}
Total Replies: {metrics['total_replied']}
Total Calls Scheduled: {metrics['total_calls']}
Total Deals Closed: {metrics['total_closed_won']}
Total Revenue: ${metrics['total_revenue']:,}

Conversion Rates:
• Reply Rate: {metrics['reply_rate']:.1%}
• Call Rate: {metrics['call_rate']:.1%} (replies → calls)
• Close Rate: {metrics['close_rate']:.1%} (calls → deals)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 TARGET vs ACTUAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Reply Rate:         {performance['reply_rate']['status']} {performance['reply_rate']['current']:.1%} (target: {performance['reply_rate']['target']:.1%})
Calls Scheduled:    {performance['calls_scheduled']['status']} {performance['calls_scheduled']['current']} (target: {performance['calls_scheduled']['target']})
Deals Closed:       {performance['deals_closed']['status']} {performance['deals_closed']['current']} (target: {performance['deals_closed']['target']})
Close Rate:         {performance['close_rate']['status']} {performance['close_rate']['current']:.1%} (target: {performance['close_rate']['target']:.1%})

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 PROJECTED OUTCOMES (if current rates hold)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Expected Replies from 50 prospects: {50 * metrics['reply_rate']:.0f}
Expected Calls from replies: {metrics['total_replied'] * metrics['call_rate']:.0f}
Expected Deals from calls: {metrics['total_calls'] * metrics['close_rate']:.0f}
Projected Revenue: ${metrics['total_calls'] * metrics['close_rate'] * 997:.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 NEXT ACTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        # Adiciona recomendações baseadas na performance
        if metrics['reply_rate'] < 0.15:
            dashboard += "\n⚠️  REPLY RATE BAIXA: Revisar messaging/targeting\n"
        if metrics['call_rate'] < 0.4:
            dashboard += "\n⚠️  CALL CONVERSION BAIXA: Melhorar follow-up\n"
        if metrics['close_rate'] < 0.3:
            dashboard += "\n⚠️  CLOSE RATE BAIXA: Revisar oferta/garantias\n"

        dashboard += f"\n🎯 Para atingir meta: precisa de {max(0, 5 - metrics['total_calls'])} calls adicionais"
        dashboard += f"\n💰 Para atingir meta: precisa de {max(0, 2 - metrics['total_closed_won'])} deals adicionais"
        
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(dashboard)
        
        return filename

def main():
    tracker = SprintPipelineTracker()
    
    print("🎯 ARCO Sprint Pipeline Tracker")
    
    # Gera template se não existir
    template_file = tracker.generate_daily_tracker_template()
    print(f"📋 Template de tracking gerado: {template_file}")
    
    # Carrega dados existentes (ou usa exemplos)
    leads = tracker.load_pipeline_data(template_file)
    
    # Gera dashboard
    dashboard_file = tracker.export_performance_dashboard(leads)
    print(f"📊 Dashboard exportado: {dashboard_file}")
    
    # Mostra checklist do dia
    day_number = int(input("\nQual dia do sprint (1-14)? ") or "1")
    checklist = tracker.generate_daily_checklist(day_number)
    
    print(f"\n📅 CHECKLIST DIA {checklist['day']} - {checklist['focus']}")
    print("━" * 50)
    for task in checklist['tasks']:
        print(task)
    
    print(f"\n✅ Sistema pronto para tracking diário!")
    print("1. Update o CSV com progresso real")
    print("2. Execute script diariamente para métricas")
    print("3. Ajuste estratégia baseado nos dados")

if __name__ == "__main__":
    main()
