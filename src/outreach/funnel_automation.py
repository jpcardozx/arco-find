#!/usr/bin/env python3
"""
Funnel Automation System
Outreach automatizado para os funis aprovados: Auditoria Express + Teardown 60s
"""

import sqlite3
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
import logging
import re
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FunnelAutomation:
    def __init__(self, db_path="../../data/prospects.db"):
        self.db_path = db_path
        self.setup_outreach_tables()
        self.email_templates = self._load_email_templates()
    
    def setup_outreach_tables(self):
        """Setup tables for outreach tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Outreach campaigns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS outreach_campaigns (
                id INTEGER PRIMARY KEY,
                prospect_id INTEGER,
                funnel_type TEXT,
                sequence_step INTEGER,
                template_used TEXT,
                sent_at TIMESTAMP,
                status TEXT,
                response_type TEXT,
                response_date TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (prospect_id) REFERENCES prospects (id)
            )
        """)
        
        # Email sequences config
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_sequences (
                id INTEGER PRIMARY KEY,
                funnel_type TEXT,
                step_number INTEGER,
                delay_days INTEGER,
                template_name TEXT,
                subject_template TEXT,
                active INTEGER DEFAULT 1
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Insert default sequences
        self._setup_default_sequences()
    
    def _setup_default_sequences(self):
        """Setup default email sequences for each funnel"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Auditoria Express sequence
        auditoria_sequence = [
            (0, 'auditoria_intro', 'R$ {waste_estimate} desperdiçados mensalmente - {company_name}'),
            (2, 'auditoria_followup', '3 ganhos rápidos que não estão no seu radar - {company_name}'),
            (5, 'auditoria_urgency', 'Última chance: Auditoria Express - {company_name}'),
            (7, 'auditoria_final', 'Case study relevante + convite final - {company_name}')
        ]
        
        # Teardown 60s sequence  
        teardown_sequence = [
            (0, 'teardown_video', 'Analisei {company_name} em 60 segundos'),
            (1, 'teardown_sms', 'Viu o vídeo sobre {primary_issue}? 15min?'),
            (3, 'teardown_competitor', 'Teardown de competidor + quer o seu também?'),
            (7, 'teardown_case', 'Case study + última chance agenda')
        ]
        
        # Insert sequences
        for delay, template, subject in auditoria_sequence:
            cursor.execute("""
                INSERT OR REPLACE INTO email_sequences 
                (funnel_type, step_number, delay_days, template_name, subject_template)
                VALUES (?, ?, ?, ?, ?)
            """, ('auditoria_express', len(auditoria_sequence) - auditoria_sequence.index((delay, template, subject)), delay, template, subject))
        
        for delay, template, subject in teardown_sequence:
            cursor.execute("""
                INSERT OR REPLACE INTO email_sequences 
                (funnel_type, step_number, delay_days, template_name, subject_template)
                VALUES (?, ?, ?, ?, ?)
            """, ('teardown_60s', len(teardown_sequence) - teardown_sequence.index((delay, template, subject)), delay, template, subject))
        
        conn.commit()
        conn.close()
    
    def _load_email_templates(self):
        """Load email templates for both funnels"""
        return {
            'auditoria_intro': {
                'subject': 'R$ {waste_estimate} desperdiçados mensalmente - {company_name}',
                'body': """Olá {decision_maker},

Quick question antes do final do expediente.

Analisei {domain} e identifiquei R$ {waste_estimate} desperdiçados mensalmente em {primary_issue}.

Problema específico: {technical_detail}

Seus concorrentes {competitor_advantage} e capturam essas oportunidades.

Auditoria Express 48h mostra exatamente como corrigir + recuperar esses R$ {waste_estimate}/mês.

Vale 15min amanhã de manhã?

Abs,
João Pedro

P.S. {vertical_insight}"""
            },
            
            'auditoria_followup': {
                'subject': '3 ganhos rápidos que não estão no seu radar - {company_name}',
                'body': """Olá {decision_maker},

Seguindo nossa conversa sobre {domain}, identifiquei 3 ganhos rápidos:

1. {issue_1}
2. {issue_2} 
3. {issue_3}

Cada um desses está custando R$ {monthly_impact}/mês em oportunidades perdidas.

A Auditoria Express 48h prioriza essas correções por impacto x esforço.

{proof_element}

Quer que eu prepare a análise completa?

Abs,
João Pedro"""
            },
            
            'teardown_video': {
                'subject': 'Analisei {company_name} em 60 segundos',
                'body': """Olá {decision_maker},

Gravei análise rápida de {domain} identificando onde seus R$ estão vazando.

{video_description}

[VÍDEO ANEXO - 60s mostrando {primary_issue} + impacto estimado]

Vale agendar 15min para mostrar como corrigir?

Abs,
João Pedro

P.S. {competitive_insight}"""
            },
            
            'teardown_sms': {
                'subject': 'WhatsApp follow-up',
                'body': """Olá {decision_maker}, viu o vídeo sobre {primary_issue}? 

15min para mostrar solução? 

João Pedro - ARCO"""
            }
        }
    
    def start_outreach_campaign(self, prospect_id: int, funnel_type: str):
        """Start outreach campaign for qualified prospect"""
        logger.info(f"Starting {funnel_type} campaign for prospect {prospect_id}")
        
        # Get prospect data
        prospect = self._get_prospect_data(prospect_id)
        if not prospect:
            logger.error(f"Prospect {prospect_id} not found")
            return False
        
        # Check if campaign already started
        if self._campaign_exists(prospect_id, funnel_type):
            logger.warning(f"Campaign already exists for prospect {prospect_id}")
            return False
        
        # Send first email immediately
        success = self._send_sequence_email(prospect, funnel_type, step=1)
        
        if success:
            self._log_outreach(prospect_id, funnel_type, 1, 'sent')
            logger.info(f"Campaign started successfully for {prospect['company_name']}")
        
        return success
    
    def process_scheduled_emails(self):
        """Process scheduled follow-up emails"""
        logger.info("Processing scheduled follow-up emails")
        
        # Get campaigns that need follow-up
        pending_campaigns = self._get_pending_campaigns()
        
        for campaign in pending_campaigns:
            prospect = self._get_prospect_data(campaign['prospect_id'])
            
            success = self._send_sequence_email(
                prospect, 
                campaign['funnel_type'], 
                campaign['next_step']
            )
            
            if success:
                self._log_outreach(
                    campaign['prospect_id'], 
                    campaign['funnel_type'], 
                    campaign['next_step'], 
                    'sent'
                )
    
    def _get_prospect_data(self, prospect_id: int):
        """Get complete prospect data for personalization"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get prospect + qualification + enrichment data
        cursor.execute("""
            SELECT p.*, ps.total_score, ps.qualification_tier, ps.recommended_funnel,
                   ps.monthly_waste_estimate, e.pagespeed_mobile, e.has_whatsapp,
                   e.has_utm_tracking, e.business_signals
            FROM prospects p
            LEFT JOIN prospect_scores ps ON p.id = ps.prospect_id
            LEFT JOIN enrichment_data e ON p.id = e.prospect_id
            WHERE p.id = ?
        """, (prospect_id,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return None
        
        columns = [desc[0] for desc in cursor.description]
        prospect = dict(zip(columns, result))
        
        # Get recent ads for context
        cursor.execute("""
            SELECT ad_text, landing_url, platforms, start_date
            FROM ads
            WHERE prospect_id = ?
            ORDER BY discovered_at DESC
            LIMIT 3
        """, (prospect_id,))
        
        prospect['recent_ads'] = cursor.fetchall()
        
        conn.close()
        return prospect
    
    def _campaign_exists(self, prospect_id: int, funnel_type: str):
        """Check if campaign already exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM outreach_campaigns
            WHERE prospect_id = ? AND funnel_type = ?
        """, (prospect_id, funnel_type))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def _get_pending_campaigns(self):
        """Get campaigns that need follow-up emails"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get campaigns where next step is due
        cursor.execute("""
            WITH campaign_progress AS (
                SELECT prospect_id, funnel_type, 
                       MAX(sequence_step) as last_step,
                       MAX(sent_at) as last_sent
                FROM outreach_campaigns
                WHERE status = 'sent' AND response_type IS NULL
                GROUP BY prospect_id, funnel_type
            )
            SELECT cp.*, es.step_number as next_step, es.delay_days
            FROM campaign_progress cp
            JOIN email_sequences es ON cp.funnel_type = es.funnel_type
            WHERE es.step_number = cp.last_step + 1
            AND datetime(cp.last_sent, '+' || es.delay_days || ' days') <= datetime('now')
            AND es.active = 1
        """)
        
        columns = [desc[0] for desc in cursor.description]
        campaigns = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return campaigns
    
    def _send_sequence_email(self, prospect: Dict, funnel_type: str, step: int):
        """Send specific sequence email"""
        try:
            # Get template for this step
            template_name = self._get_template_for_step(funnel_type, step)
            if not template_name or template_name not in self.email_templates:
                logger.error(f"Template not found: {template_name}")
                return False
            
            template = self.email_templates[template_name]
            
            # Personalize email
            personalized_email = self._personalize_email(template, prospect)
            
            # For demo, just log the email (would send via SMTP in production)
            logger.info(f"EMAIL SENT TO {prospect['company_name']}:")
            logger.info(f"Subject: {personalized_email['subject']}")
            logger.info(f"Body preview: {personalized_email['body'][:200]}...")
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def _get_template_for_step(self, funnel_type: str, step: int):
        """Get template name for specific funnel step"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT template_name FROM email_sequences
            WHERE funnel_type = ? AND step_number = ?
        """, (funnel_type, step))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def _personalize_email(self, template: Dict, prospect: Dict):
        """Personalize email template with prospect data"""
        # Extract personalization data
        personalization = self._extract_personalization_data(prospect)
        
        # Replace placeholders in subject and body
        subject = template['subject'].format(**personalization)
        body = template['body'].format(**personalization)
        
        return {
            'subject': subject,
            'body': body,
            'to_email': self._extract_email(prospect),
            'to_name': personalization['decision_maker']
        }
    
    def _extract_personalization_data(self, prospect: Dict):
        """Extract personalization data from prospect"""
        # Estimate decision maker name
        company_name = prospect.get('company_name', '')
        decision_maker = self._extract_decision_maker(company_name)
        
        # Determine primary issue
        primary_issue = self._identify_primary_issue(prospect)
        
        # Generate technical details
        technical_detail = self._generate_technical_detail(prospect)
        
        # Vertical-specific insights
        vertical_insight = self._get_vertical_insight(prospect.get('vertical'))
        
        return {
            'company_name': company_name,
            'domain': prospect.get('domain', ''),
            'decision_maker': decision_maker,
            'waste_estimate': prospect.get('monthly_waste_estimate', 1500),
            'primary_issue': primary_issue,
            'technical_detail': technical_detail,
            'vertical_insight': vertical_insight,
            'competitor_advantage': self._get_competitor_advantage(prospect),
            'monthly_impact': prospect.get('monthly_waste_estimate', 1500),
            'video_description': self._generate_video_description(prospect),
            'competitive_insight': self._get_competitive_insight(prospect)
        }
    
    def _extract_decision_maker(self, company_name: str):
        """Extract likely decision maker name from company name"""
        # Simple heuristics for Brazilian names
        if 'dr.' in company_name.lower():
            return 'Doutor'
        elif 'dra.' in company_name.lower():
            return 'Doutora'
        elif any(name in company_name for name in ['silva', 'santos', 'oliveira', 'souza']):
            return 'Dr.'
        else:
            return 'Prezado'
    
    def _identify_primary_issue(self, prospect: Dict):
        """Identify primary issue based on qualification data"""
        mobile_speed = prospect.get('pagespeed_mobile', 100)
        has_whatsapp = prospect.get('has_whatsapp', False)
        has_utm = prospect.get('has_utm_tracking', False)
        
        if mobile_speed < 50:
            return 'performance mobile crítica'
        elif not has_whatsapp:
            return 'falta de WhatsApp para conversão'
        elif not has_utm:
            return 'tracking deficiente'
        else:
            return 'oportunidades de otimização'
    
    def _generate_technical_detail(self, prospect: Dict):
        """Generate specific technical detail"""
        mobile_speed = prospect.get('pagespeed_mobile', 100)
        
        if mobile_speed < 50:
            return f"PageSpeed mobile {mobile_speed}/100 = {4.5 - (mobile_speed/50)}s loading = 60%+ visitantes desistem"
        else:
            return "Site sem otimização para conversão mobile"
    
    def _get_vertical_insight(self, vertical: str):
        """Get vertical-specific insight"""
        insights = {
            'dental': 'Otimização mobile é crítica para dental - 70% das buscas por dentista acontecem no celular',
            'real_estate': 'No mercado imobiliário, cada segundo de delay custa leads qualificados',
            'fitness': 'Academias dependem de conversão rápida - pessoas decidem por impulso'
        }
        return insights.get(vertical, 'Performance web impacta diretamente no ROI de mídia paga')
    
    def _get_competitor_advantage(self, prospect: Dict):
        """Generate competitor advantage statement"""
        return "carregam 3x mais rápido"
    
    def _generate_video_description(self, prospect: Dict):
        """Generate video description for teardown"""
        issue = self._identify_primary_issue(prospect)
        return f"Identifiquei {issue} custando R$ {prospect.get('monthly_waste_estimate', 1500)}/mês"
    
    def _get_competitive_insight(self, prospect: Dict):
        """Generate competitive insight"""
        vertical = prospect.get('vertical', '')
        if vertical == 'dental':
            return 'Seus competidores já otimizaram mobile e capturam esses agendamentos'
        return 'Mercado competitivo - cada vantagem conta'
    
    def _extract_email(self, prospect: Dict):
        """Extract or estimate email for prospect"""
        domain = prospect.get('domain', '')
        company_name = prospect.get('company_name', '')
        
        if domain:
            # Common patterns
            return f"contato@{domain}"
        else:
            return "email_not_found@example.com"
    
    def _log_outreach(self, prospect_id: int, funnel_type: str, step: int, status: str):
        """Log outreach activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        template_name = self._get_template_for_step(funnel_type, step)
        
        cursor.execute("""
            INSERT INTO outreach_campaigns
            (prospect_id, funnel_type, sequence_step, template_used, sent_at, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (prospect_id, funnel_type, step, template_name, datetime.now().isoformat(), status))
        
        conn.commit()
        conn.close()
    
    def get_campaign_stats(self):
        """Get outreach campaign statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Overall stats
        cursor.execute("""
            SELECT funnel_type, COUNT(*) as sent_count,
                   SUM(CASE WHEN response_type IS NOT NULL THEN 1 ELSE 0 END) as responses
            FROM outreach_campaigns
            WHERE sent_at > date('now', '-30 days')
            GROUP BY funnel_type
        """)
        
        stats = {}
        for row in cursor.fetchall():
            funnel, sent, responses = row
            stats[funnel] = {
                'emails_sent': sent,
                'responses': responses,
                'response_rate': (responses / sent * 100) if sent > 0 else 0
            }
        
        conn.close()
        return stats
    
    def run_daily_outreach(self, max_new_campaigns=20):
        """Run daily outreach process"""
        logger.info("Starting daily outreach process")
        
        # 1. Process scheduled follow-ups
        self.process_scheduled_emails()
        
        # 2. Start new campaigns for qualified prospects
        new_campaigns_started = self._start_new_campaigns(max_new_campaigns)
        
        # 3. Update campaign stats
        stats = self.get_campaign_stats()
        
        logger.info(f"Daily outreach completed:")
        logger.info(f"  New campaigns started: {new_campaigns_started}")
        logger.info(f"  Campaign stats: {stats}")
        
        return {
            'new_campaigns': new_campaigns_started,
            'stats': stats
        }
    
    def _start_new_campaigns(self, max_campaigns: int):
        """Start new campaigns for qualified prospects"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get qualified prospects without campaigns
        cursor.execute("""
            SELECT p.id, ps.recommended_funnel
            FROM prospects p
            JOIN prospect_scores ps ON p.id = ps.prospect_id
            LEFT JOIN outreach_campaigns oc ON p.id = oc.prospect_id
            WHERE ps.qualification_tier IN ('S_TIER', 'A_TIER')
            AND oc.id IS NULL
            ORDER BY ps.total_score DESC
            LIMIT ?
        """, (max_campaigns,))
        
        prospects = cursor.fetchall()
        conn.close()
        
        campaigns_started = 0
        for prospect_id, funnel_type in prospects:
            if self.start_outreach_campaign(prospect_id, funnel_type):
                campaigns_started += 1
        
        return campaigns_started


def demo_outreach_system():
    """Demo the outreach system"""
    automation = FunnelAutomation()
    
    print("ARCO OUTREACH AUTOMATION DEMO")
    print("=" * 50)
    
    # Run daily outreach
    result = automation.run_daily_outreach(max_new_campaigns=5)
    
    print(f"\nDaily outreach results:")
    print(f"New campaigns started: {result['new_campaigns']}")
    print(f"Campaign performance: {result['stats']}")


if __name__ == "__main__":
    demo_outreach_system()