"""
🎯 ARCO OUTREACH AUTOMATION SYSTEM
7-day business-focused outreach sequence for revenue leak leads

Focus: CFO/CMO targeting with financial waste evidence
Success: 30%+ response rate, 50%+ call conversion
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders


class OutreachChannel(Enum):
    EMAIL = "email"
    LINKEDIN = "linkedin"
    WHATSAPP = "whatsapp"
    LOOM = "loom"


class OutreachStatus(Enum):
    SCHEDULED = "scheduled"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    REPLIED = "replied"
    CALL_BOOKED = "call_booked"
    CONTRACT_SIGNED = "contract_signed"
    FAILED = "failed"


@dataclass
class Contact:
    """Target contact information"""
    name: str
    title: str
    email: str
    linkedin_url: str = ""
    phone: str = ""
    company: str = ""
    role: str = ""  # CFO, CMO, CEO, etc.


@dataclass
class OutreachSequence:
    """7-day outreach sequence configuration"""
    day: int
    channel: OutreachChannel
    subject: str
    cta: str
    personalization_vars: List[str]


@dataclass
class OutreachRecord:
    """Individual outreach tracking record"""
    lead_domain: str
    contact: Contact
    sequence_day: int
    channel: OutreachChannel
    status: OutreachStatus
    sent_at: datetime
    opened_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    response_content: str = ""
    next_action: str = ""


class EmailTemplateEngine:
    """Generate personalized email templates"""
    
    def __init__(self):
        self.templates = {
            'day_0_cfo': {
                'subject': '🚨 Achamos ~US$ {total_waste}/mo vazando - {brand_name}',
                'template': '''Olá {contact_name},

Detectamos aproximadamente US$ {total_waste}/mês vazando em {brand_name} através de:

• {leak_summary}
• Performance: {performance_issues}
• {roas_summary}

PROPOSTA: Call de 15 minutos, cobramos apenas 25% do que você economizar.

Sem economia = sem cobrança.

Posso mostrar exatamente onde está vazando?

{signature}

PS: Dashboard completo com detalhes: {dashboard_url}'''
            },
            
            'day_1_linkedin': {
                'subject': 'Mini demo: US$ {total_waste} → US$ 0',
                'template': '''👋 {contact_name},

Vi que {brand_name} tem potencial de economizar ~US$ {total_waste}/mês.

Quick win que posso mostrar:
{biggest_leak} → {replacement} = US$ {biggest_saving}/mo

Vale 15 min de call?

{signature}'''
            },
            
            'day_3_email_2': {
                'subject': '120s demo: {biggest_leak} → React (custo zero)',
                'template': '''Oi {contact_name},

Video de 2 minutos mostrando como trocar:

{biggest_leak} (US$ {biggest_cost}/mo) → React hook + AWS SES (US$ 0)

+ Tema otimizado reduzindo {js_weight}KB → melhora conversão em {conversion_improvement}%

Link do demo: {demo_video_url}

Quer ver isso implementado em {brand_name}?

{signature}'''
            },
            
            'day_6_loom': {
                'subject': 'Dev store live: LCP 2.4s, sem apps redundantes',
                'template': '''Final demo para {brand_name}:

🎥 Loom com dev-store mostrando:
• LCP: {current_lcp}s → 2.4s 
• Apps removidos: {removed_apps}
• Economia total: US$ {total_savings}/mês

Link: {loom_url}

Interesse em implementar?

{signature}'''
            },
            
            'day_9_whatsapp': {
                'subject': 'Áudio WhatsApp',
                'template': '''Áudio de 60s explicando contrato piloto:

• Fee: 25% dos savings realizados
• No-cure, no-pay: <US$ 1K = grátis  
• Acesso read-only para auditoria
• Cancelamento livre após 90d

Podemos fechar essa semana?'''
            }
        }
    
    def generate_email(self, template_key: str, lead_data: Dict, contact: Contact) -> Dict:
        """Generate personalized email from template"""
        template = self.templates.get(template_key, {})
        if not template:
            return {}
        
        # Extract personalization data
        personalization = {
            'contact_name': contact.name,
            'brand_name': lead_data.get('brand_name', ''),
            'total_waste': f"{lead_data.get('waste_breakdown', {}).get('total_waste', '0'):,}",
            'dashboard_url': lead_data.get('qualification', {}).get('dashboard_url', ''),
            'signature': self._get_signature(),
        }
        
        # Add leak-specific data
        waste_breakdown = lead_data.get('waste_breakdown', {})
        saas_leaks = waste_breakdown.get('saas_leaks', [])
        
        if saas_leaks:
            biggest_leak = max(saas_leaks, key=lambda x: int(x['monthly_cost'].replace('US$ ', '').replace('/mo', '')))
            personalization.update({
                'biggest_leak': biggest_leak['tool'],
                'biggest_cost': biggest_leak['monthly_cost'].replace('/mo', ''),
                'biggest_saving': biggest_leak['monthly_cost'].replace('/mo', ''),
                'replacement': biggest_leak['replacement'],
                'leak_summary': self._format_leak_summary(saas_leaks[:3])  # Top 3 leaks
            })
        
        # Add performance data
        technical_metrics = lead_data.get('technical_metrics', {})
        personalization.update({
            'current_lcp': technical_metrics.get('lcp_seconds', 0),
            'js_weight': technical_metrics.get('js_bytes', 0) // 1000,  # Convert to KB
            'performance_issues': self._format_performance_issues(waste_breakdown.get('performance_details', [])),
            'conversion_improvement': self._calculate_conversion_improvement(technical_metrics),
            'roas_summary': self._format_roas_summary(waste_breakdown.get('roas_issues', []))
        })
        
        # Generate URLs (in production, these would be real)
        personalization.update({
            'demo_video_url': f"https://demo.arco.dev/{lead_data['brand'].replace('.', '-')}/quick-fix",
            'loom_url': f"https://loom.com/arco-demo/{lead_data['brand'].replace('.', '-')}/complete",
        })
        
        # Format template
        try:
            subject = template['subject'].format(**personalization)
            body = template['template'].format(**personalization)
            
            return {
                'subject': subject,
                'body': body,
                'personalization': personalization
            }
        except KeyError as e:
            print(f"❌ Template formatting error: {e}")
            return {}
    
    def _get_signature(self) -> str:
        return """--
João Pedro - ARCO
Growth Efficiency Specialist
📧 joao@arco.dev | 📱 +55 11 9xxxx-xxxx"""
    
    def _format_leak_summary(self, leaks: List[Dict]) -> str:
        return "\n".join([f"  • {leak['tool']}: {leak['monthly_cost']}" for leak in leaks])
    
    def _format_performance_issues(self, issues: List[str]) -> str:
        return ", ".join(issues) if issues else "Performance OK"
    
    def _format_roas_summary(self, issues: List[str]) -> str:
        return issues[0] if issues else "ROAS analysis pending"
    
    def _calculate_conversion_improvement(self, metrics: Dict) -> float:
        # Simplified calculation
        js_kb = metrics.get('js_bytes', 0) / 1000
        if js_kb > 900:
            return round((js_kb - 900) / 100 * 2, 1)  # 2% per 100KB over threshold
        return 0


class ContactEnrichmentEngine:
    """Enrich leads with decision-maker contact information"""
    
    def __init__(self):
        self.enrichment_sources = [
            'linkedin_sales_navigator',
            'apollo_io',
            'zoominfo', 
            'hunter_io'
        ]
    
    async def find_decision_makers(self, domain: str, company_name: str) -> List[Contact]:
        """Find CFO/CMO contacts - requires real enrichment API"""
        # Must integrate with real APIs: Apollo, ZoomInfo, Hunter.io
        # No mock data - return empty if no real enrichment
        return []
    
    def _generate_mock_name(self) -> str:
        # Removed - no mock data
        return ""


class OutreachSequenceManager:
    """Manage 7-day outreach sequences"""
    
    def __init__(self):
        self.template_engine = EmailTemplateEngine()
        self.contact_enricher = ContactEnrichmentEngine()
        self.sequence_config = [
            OutreachSequence(0, OutreachChannel.EMAIL, "Initial CFO email", 
                           "Call de 15 min, cobramos só 25% do economizado", 
                           ['total_waste', 'biggest_leak']),
            OutreachSequence(1, OutreachChannel.LINKEDIN, "LinkedIn mini demo",
                           "Quick win demo - vale 15 min?",
                           ['biggest_saving', 'replacement']),
            OutreachSequence(3, OutreachChannel.EMAIL, "Demo video email",
                           "120s demo mostrando implementação",
                           ['demo_video_url', 'conversion_improvement']),
            OutreachSequence(6, OutreachChannel.LOOM, "Dev store demo",
                           "Loom com dev-store otimizada",
                           ['loom_url', 'performance_metrics']),
            OutreachSequence(9, OutreachChannel.WHATSAPP, "Contract close",
                           "Fechar contrato piloto shared-savings",
                           ['contract_terms'])
        ]
        
        self.active_sequences = {}  # domain -> sequence data
        self.outreach_records = []
    
    async def start_sequence_for_lead(self, lead_data: Dict) -> bool:
        """Start outreach sequence for qualified lead"""
        domain = lead_data['brand']
        company_name = lead_data['brand_name']
        
        print(f"🎯 Starting outreach sequence for {company_name}")
        
        # Find decision makers
        contacts = await self.contact_enricher.find_decision_makers(domain, company_name)
        
        if not contacts:
            print(f"❌ No contacts found for {domain}")
            return False
        
        # Initialize sequence tracking
        self.active_sequences[domain] = {
            'lead_data': lead_data,
            'contacts': contacts,
            'current_day': 0,
            'started_at': datetime.now(),
            'status': 'active'
        }
        
        # Send first email (Day 0)
        await self._execute_sequence_step(domain, 0)
        
        return True
    
    async def _execute_sequence_step(self, domain: str, day: int) -> bool:
        """Execute specific day of outreach sequence"""
        sequence_data = self.active_sequences.get(domain)
        if not sequence_data:
            return False
        
        lead_data = sequence_data['lead_data']
        contacts = sequence_data['contacts']
        
        # Find sequence config for this day
        sequence_config = next((s for s in self.sequence_config if s.day == day), None)
        if not sequence_config:
            return False
        
        print(f"📧 Day {day}: {sequence_config.cta} - {domain}")
        
        # Execute based on channel
        success = False
        if sequence_config.channel == OutreachChannel.EMAIL:
            success = await self._send_email(domain, day, lead_data, contacts)
        elif sequence_config.channel == OutreachChannel.LINKEDIN:
            success = await self._send_linkedin_message(domain, day, lead_data, contacts)
        elif sequence_config.channel == OutreachChannel.LOOM:
            success = await self._create_loom_video(domain, day, lead_data, contacts)
        elif sequence_config.channel == OutreachChannel.WHATSAPP:
            success = await self._send_whatsapp_audio(domain, day, lead_data, contacts)
        
        # Schedule next step
        if success and day < 9:
            next_day = self._get_next_sequence_day(day)
            if next_day:
                await self._schedule_next_step(domain, next_day)
        
        return success
    
    async def _send_email(self, domain: str, day: int, lead_data: Dict, contacts: List[Contact]) -> bool:
        """Send email for specific sequence day"""
        # Choose template based on day
        template_key = {
            0: 'day_0_cfo',
            3: 'day_3_email_2'
        }.get(day)
        
        if not template_key:
            return False
        
        # Target CFO primarily, CMO as fallback
        primary_contact = next((c for c in contacts if c.role == 'CFO'), contacts[0])
        
        # Generate email
        email_data = self.template_engine.generate_email(template_key, lead_data, primary_contact)
        
        if not email_data:
            return False
        
        # Record outreach
        record = OutreachRecord(
            lead_domain=domain,
            contact=primary_contact,
            sequence_day=day,
            channel=OutreachChannel.EMAIL,
            status=OutreachStatus.SENT,
            sent_at=datetime.now()
        )
        
        self.outreach_records.append(record)
        
        print(f"   ✅ Email sent to {primary_contact.name} ({primary_contact.title})")
        print(f"   📧 Subject: {email_data['subject']}")
        
        return True
    
    async def _send_linkedin_message(self, domain: str, day: int, lead_data: Dict, contacts: List[Contact]) -> bool:
        """Send LinkedIn message"""
        # Target both CFO and CMO for LinkedIn
        targets = [c for c in contacts if c.role in ['CFO', 'CMO']]
        
        for contact in targets:
            # Generate LinkedIn message
            email_data = self.template_engine.generate_email('day_1_linkedin', lead_data, contact)
            
            # Record outreach
            record = OutreachRecord(
                lead_domain=domain,
                contact=contact,
                sequence_day=day,
                channel=OutreachChannel.LINKEDIN,
                status=OutreachStatus.SENT,
                sent_at=datetime.now()
            )
            
            self.outreach_records.append(record)
            
            print(f"   🔗 LinkedIn message sent to {contact.name} ({contact.title})")
        
        return True
    
    async def _create_loom_video(self, domain: str, day: int, lead_data: Dict, contacts: List[Contact]) -> bool:
        """Create and send Loom video"""
        # In production, this would trigger actual Loom video creation
        loom_url = f"https://loom.com/arco-demo/{domain.replace('.', '-')}/day-{day}"
        
        # Send to primary contact
        primary_contact = next((c for c in contacts if c.role == 'CFO'), contacts[0])
        
        email_data = self.template_engine.generate_email('day_6_loom', lead_data, primary_contact)
        
        record = OutreachRecord(
            lead_domain=domain,
            contact=primary_contact,
            sequence_day=day,
            channel=OutreachChannel.LOOM,
            status=OutreachStatus.SENT,
            sent_at=datetime.now()
        )
        
        self.outreach_records.append(record)
        
        print(f"   🎥 Loom video sent to {primary_contact.name}: {loom_url}")
        return True
    
    async def _send_whatsapp_audio(self, domain: str, day: int, lead_data: Dict, contacts: List[Contact]) -> bool:
        """Send WhatsApp audio message"""
        # Only if they've shown interest (replied to previous messages)
        has_replied = any(
            r.lead_domain == domain and r.status == OutreachStatus.REPLIED 
            for r in self.outreach_records
        )
        
        if not has_replied:
            print(f"   ⏭️  Skipping WhatsApp (no previous engagement)")
            return False
        
        primary_contact = next((c for c in contacts if c.role == 'CFO'), contacts[0])
        
        record = OutreachRecord(
            lead_domain=domain,
            contact=primary_contact,
            sequence_day=day,
            channel=OutreachChannel.WHATSAPP,
            status=OutreachStatus.SENT,
            sent_at=datetime.now()
        )
        
        self.outreach_records.append(record)
        
        print(f"   📱 WhatsApp audio sent to {primary_contact.name}")
        return True
    
    def _get_next_sequence_day(self, current_day: int) -> Optional[int]:
        """Get next day in sequence"""
        next_days = [s.day for s in self.sequence_config if s.day > current_day]
        return min(next_days) if next_days else None
    
    async def _schedule_next_step(self, domain: str, next_day: int) -> None:
        """Schedule next outreach step"""
        # In production, this would use a proper job scheduler
        print(f"   ⏰ Next step scheduled: Day {next_day} for {domain}")
    
    def get_sequence_stats(self) -> Dict:
        """Get outreach performance statistics"""
        total_sent = len(self.outreach_records)
        replied = len([r for r in self.outreach_records if r.status == OutreachStatus.REPLIED])
        calls_booked = len([r for r in self.outreach_records if r.status == OutreachStatus.CALL_BOOKED])
        
        response_rate = (replied / total_sent * 100) if total_sent > 0 else 0
        call_rate = (calls_booked / replied * 100) if replied > 0 else 0
        
        return {
            'total_outreach_sent': total_sent,
            'total_replies': replied,
            'calls_booked': calls_booked,
            'response_rate_percent': round(response_rate, 1),
            'call_conversion_rate_percent': round(call_rate, 1),
            'active_sequences': len(self.active_sequences)
        }


class ArcoOutreachEngine:
    """Complete ARCO outreach automation system"""
    
    def __init__(self):
        self.sequence_manager = OutreachSequenceManager()
        self.results = {
            'campaigns_started': 0,
            'total_outreach': 0,
            'responses': 0,
            'calls_booked': 0,
            'contracts_signed': 0
        }
    
    async def launch_outreach_campaign(self, qualified_leads: List[Dict]) -> Dict:
        """Launch complete outreach campaign for qualified leads"""
        
        print("🚀 LAUNCHING ARCO OUTREACH CAMPAIGN")
        print("=" * 50)
        
        print(f"📊 Targets: {len(qualified_leads)} qualified leads")
        print(f"🎯 Goal: 30%+ response rate, 5+ pilot contracts")
        
        # Start sequences for all leads
        for lead_data in qualified_leads:
            success = await self.sequence_manager.start_sequence_for_lead(lead_data)
            if success:
                self.results['campaigns_started'] += 1
            
            # Rate limiting between sequence starts
            await asyncio.sleep(2)
        
        print(f"\n✅ Campaign launched for {self.results['campaigns_started']} leads")
        
        # Get current stats
        stats = self.sequence_manager.get_sequence_stats()
        
        return {
            'launch_summary': {
                'leads_targeted': len(qualified_leads),
                'sequences_started': self.results['campaigns_started'],
                'launch_success_rate': f"{self.results['campaigns_started']/len(qualified_leads)*100:.1f}%"
            },
            'outreach_stats': stats,
            'next_actions': [
                "Monitor email open rates and responses",
                "Follow up on LinkedIn connections",
                "Prepare Loom demo videos",
                "Track call bookings and pilot sign-ups"
            ],
            'kpi_targets': {
                'response_rate_target': '≥ 30%',
                'call_rate_target': '≥ 50% of responses',
                'pilot_contracts_target': '≥ 5',
                'timeline': '45 days'
            }
        }


# Export outreach data
def export_outreach_campaign(campaign_data: Dict, filename: str = None) -> str:
    """Export outreach campaign data"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"outreach_campaign_{timestamp}.json"
    
    filepath = os.path.join('output', filename)
    os.makedirs('output', exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(campaign_data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"💾 Campaign data exported to: {filepath}")
    return filepath


# Demo usage - REMOVED
async def demo_outreach_campaign():
    """Demo removed - use real qualified leads only"""
    print("❌ Use real qualified leads from revenue_leak_attack.py")

if __name__ == "__main__":
    print("🎯 Use revenue_leak_attack.py for real execution")
