"""
Templates de Outreach 2025 - Baseados em Evidências
Foco em conversão real para os 3 funis principais

Benchmarks:
- Response rate B2B email: 6-12%
- Video engagement: +65% vs texto
- Call conversion: 20-35% de respostas positivas
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json


@dataclass
class OutreachMessage:
    """Mensagem de outreach estruturada"""
    template_type: str  # "audit_express", "teardown_60s", "landing_relampago"
    subject: str
    body: str
    follow_up_sequence: List[str]
    video_script: Optional[str] = None
    cta: str = ""
    personalization_fields: List[str] = None
    
    def __post_init__(self):
        if self.personalization_fields is None:
            self.personalization_fields = []


class OutreachTemplates2025:
    """Templates otimizados para conversão em 2025"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def generate_audit_express_sequence(self, prospect_data: Dict) -> List[OutreachMessage]:
        """
        Funil A: Sequência de Auditoria Express
        Meta: 15-25% CVR da landing page
        """
        
        # Email 1: Introdução + Lead Magnet
        email_1 = OutreachMessage(
            template_type="audit_express",
            subject=f"ROI de Velocidade para {prospect_data.get('company_name', 'sua empresa')}",
            body=f"""Olá {prospect_data.get('contact_name', 'time')},

Vi que a {prospect_data.get('company_name')} investe em Google Ads e notei algumas oportunidades rápidas no {prospect_data.get('domain')}.

Criei uma calculadora que mostra como pequenas melhorias de velocidade podem aumentar suas conversões em 8-10% (dados de 2025).

**ROI da Velocidade - Kit Gratuito:**
→ Planilha com cálculo automático do impacto
→ Vídeo 2min mostrando como usar
→ Checklist de implementação

[BAIXAR KIT GRATUITO]

Se quiser uma análise específica do seu site, ofereço uma Auditoria Express 48h por $250 (100% abatida se seguirmos com a Sprint 7 dias).

Disponível para implementar ainda esta semana?

{prospect_data.get('sender_name', 'João')}""",
            follow_up_sequence=[],
            cta="Auditoria Express 48h - $250 (100% abatida na Sprint)",
            personalization_fields=["company_name", "domain", "contact_name"]
        )
        
        # Email 2: Follow-up com urgência
        email_2 = OutreachMessage(
            template_type="audit_express",
            subject=f"Re: ROI de Velocidade para {prospect_data.get('company_name')}",
            body=f"""Oi {prospect_data.get('contact_name', 'time')},

Quick follow-up sobre a auditoria do {prospect_data.get('domain')}.

Analisei rapidamente e identifiquei 3 vazamentos principais:
• Performance mobile crítica (impacto: ~15% das conversões)
• Core Web Vitals fora do padrão Google
• Otimizações de carregamento perdidas

**Ainda tenho 2 slots esta semana** para a Auditoria Express 48h.

Resultados garantidos ou devolvo 100% + você fica com a análise.

Posso reservar um slot hoje?

{prospect_data.get('sender_name', 'João')}""",
            follow_up_sequence=[],
            cta="Reservar slot - Auditoria 48h",
            personalization_fields=["company_name", "domain", "contact_name"]
        )
        
        # Email 3: Social proof + última chance
        email_3 = OutreachMessage(
            template_type="audit_express",
            subject="Case: +23% conversões em 5 dias",
            body=f"""Oi {prospect_data.get('contact_name', 'time')},

Case rápido que pode interessar:

**Cliente do setor {prospect_data.get('industry', 'similar')}:**
• Auditoria Express: identificamos 4 problemas críticos
• Sprint 7 dias: +23% conversões, economia $1.200/mês em ads
• ROI: 340% no primeiro mês

**Última semana de janeiro** - ainda tenho 1 slot disponível.

Se não fizer sentido agora, tudo bem. Mas se velocidade e conversão são prioridade, é uma oportunidade que aparece pouco.

Link direto para agendar: [CALENDLY_LINK]

{prospect_data.get('sender_name', 'João')}""",
            follow_up_sequence=[],
            cta="Agendar Auditoria Express - Último slot",
            personalization_fields=["company_name", "industry", "contact_name"]
        )
        
        return [email_1, email_2, email_3]
    
    def generate_teardown_60s_sequence(self, prospect_data: Dict, teardown_insights: Dict) -> List[OutreachMessage]:
        """
        Funil B: Sequência com Teardown em Vídeo
        Meta: 6-12% response rate + 20-35% call conversion
        """
        
        # Email 1: Vídeo ungated
        email_1 = OutreachMessage(
            template_type="teardown_60s",
            subject=f"3 vazamentos no {prospect_data.get('domain')} [vídeo 60s]",
            body=f"""Oi {prospect_data.get('contact_name', 'time')},

Analisei o {prospect_data.get('domain')} e gravei um vídeo de 60s mostrando 3 vazamentos que estão custando conversões.

**[VÍDEO - 60 SEGUNDOS]** 
👆 Sem cadastro, clica e assiste

Os 3 problemas que identifiquei:
1. {teardown_insights.get('issue_1', 'Performance mobile crítica')}
2. {teardown_insights.get('issue_2', 'CLS alto prejudicando UX')}
3. {teardown_insights.get('issue_3', 'Falta de otimização de imagens')}

Se quiser a análise completa + plano de ação detalhado, responde este email que mando em 24h.

{prospect_data.get('sender_name', 'João')}

PS: Identifico esses problemas porque resolvo exatamente isso para empresas do setor {prospect_data.get('industry', 'digital')}.

[LINK_VIDEO_LOOM]""",
            video_script=self._generate_loom_script(teardown_insights),
            follow_up_sequence=[],
            cta="Responder para análise completa",
            personalization_fields=["company_name", "domain", "contact_name", "industry"]
        )
        
        # Email 2: Follow-up para quem viu o vídeo
        email_2 = OutreachMessage(
            template_type="teardown_60s",
            subject=f"Viu o vídeo do {prospect_data.get('domain')}?",
            body=f"""Oi {prospect_data.get('contact_name')},

Vi que você assistiu o vídeo sobre os vazamentos no {prospect_data.get('domain')}.

Tenho 2 perguntas rápidas:
1. Dos 3 problemas mostrados, qual impacta mais o negócio?
2. Já tentaram resolver a questão de performance mobile?

**Próximo passo:** análise completa + estimativa de impacto financeiro.

Demora 30min de call. Disponível amanhã 14h ou quinta 10h?

{prospect_data.get('sender_name', 'João')}""",
            follow_up_sequence=[],
            cta="Agendar 30min - Análise completa",
            personalization_fields=["company_name", "domain", "contact_name"]
        )
        
        return [email_1, email_2]
    
    def generate_landing_relampago_sequence(self, prospect_data: Dict) -> List[OutreachMessage]:
        """
        Funil C: Sequência para Landing Relâmpago
        Meta: CPL ≤$25 + ≥20% pedindo demo
        """
        
        # Email 1: Kit ungated
        email_1 = OutreachMessage(
            template_type="landing_relampago",
            subject="Kit: Página de Alta Conversão [download direto]",
            body=f"""Oi {prospect_data.get('contact_name', 'pessoal')},

Criei um kit completo para otimizar páginas de conversão baseado em dados de 2025.

**Kit de Página de Alta Conversão:**
• Wireframe Figma com 10 blocos prontos
• 7 erros comuns que matam conversão
• Exemplos antes/depois com dados reais
• Checklist mobile-first

[BAIXAR KIT GRATUITO - SEM CADASTRO]

Se implementar só 30% do que está no kit, vai ver diferença nas métricas em 48h.

Para empresas que querem resultados mais rápidos, ofereço a **Sprint 7 dias** - implementação completa com garantia de achados acionáveis por $750.

Vale uma conversa?

{prospect_data.get('sender_name', 'João')}""",
            follow_up_sequence=[],
            cta="Sprint 7 dias - $750 com garantia",
            personalization_fields=["contact_name"]
        )
        
        # Email 2: Case study
        email_2 = OutreachMessage(
            template_type="landing_relampago",
            subject="Case: De 2.1% para 4.8% conversão em 6 dias",
            body=f"""Oi {prospect_data.get('contact_name')},

Case que acabou de sair do forno:

**E-commerce - Setor similar ao de vocês:**
• Baseline: 2.1% conversão mobile
• Sprint 7 dias: 4.8% conversão (aumento de 128%)
• Impacto mensal: +$8.400 receita adicional
• Custo da Sprint: $750

**O que fizemos:**
→ Otimizamos velocidade (de 3.2s para 1.1s)
→ Redesenhamos CTA e checkout mobile
→ Implementamos lazy loading inteligente

**Garantia:** se não identificarmos pelo menos 3 oportunidades acionáveis, devolvemos 100%.

Disponível para uma Sprint ainda em janeiro?

[CALENDLY_DEMO_30MIN]

{prospect_data.get('sender_name', 'João')}""",
            follow_up_sequence=[],
            cta="Demo 30min - Sprint garantida",
            personalization_fields=["contact_name"]
        )
        
        return [email_1, email_2]
    
    def _generate_loom_script(self, teardown_insights: Dict) -> str:
        """Script estruturado para vídeo Loom 60-90s"""
        return f"""
SCRIPT LOOM - TEARDOWN 60-90s

[0-15s] ABERTURA:
"Oi, sou o João e analisei o {teardown_insights.get('domain', 'site')} de vocês. 
Identifiquei 3 problemas que estão custando conversões. Vou mostrar na tela."

[15-45s] PROBLEMAS:
"Primeiro: [MOSTRAR PAGESPEED] performance mobile está em {teardown_insights.get('performance_score', 65)}/100. 
Isso significa que vocês perdem cerca de 15% das conversões por lentidão.

Segundo: [MOSTRAR ISSUES] Core Web Vitals fora do padrão Google. 
Impacta ranking e experiência do usuário.

Terceiro: [MOSTRAR MOBILE] otimização mobile insuficiente. 
67% do tráfego vem do mobile hoje."

[45-75s] QUICK WIN:
"Quick win: otimizar as 3 imagens principais da home reduz 40% do tempo de carregamento. 
Simples, mas efetivo."

[75-90s] CTA:
"Se quiser a análise completa com plano de ação detalhado, 
responde este email que mando em 24h. Implementação leva 7 dias."

FIM.
"""
    
    def _load_templates(self) -> Dict:
        """Carrega templates base do sistema"""
        return {
            "kill_rules": {
                "no_response_after_days": 7,
                "max_follow_ups": 3,
                "pause_if_unsubscribe": True
            },
            "scheduling": {
                "email_1_delay": 0,      # Imediato
                "email_2_delay": 3,      # 3 dias
                "email_3_delay": 7,      # 7 dias
                "max_sequence_days": 14
            },
            "personalization_required": [
                "company_name",
                "domain", 
                "contact_name",
                "industry"
            ]
        }
    
    def generate_weekly_outreach_plan(self, prospects_by_funnel: Dict) -> Dict:
        """
        Plano semanal de outreach baseado nos 3 funis
        """
        plan = {
            "monday": {
                "action": "Gerar lista + gravar Looms",
                "targets": "100-150 anunciantes ativos",
                "deliverable": "10-15 vídeos Loom prontos"
            },
            "tuesday": {
                "action": "Disparar Email 1 + subir retarget",
                "targets": "Todos os prospects da lista",
                "deliverable": "Sequência inicial ativada"
            },
            "wednesday": {
                "action": "2 variações de LP do magnet",
                "targets": "A/B test header + prova social",
                "deliverable": "Landing pages otimizadas"
            },
            "thursday": {
                "action": "Email 2 + CTA de agenda",
                "targets": "Prospects que não responderam",
                "deliverable": "Follow-up com slots da semana"
            },
            "friday": {
                "action": "Email 3 + micro-case",
                "targets": "Última chance + social proof",
                "deliverable": "Case antes/depois publicado"
            }
        }
        
        return plan
    
    def calculate_outreach_metrics(self, sent: int, opened: int, replied: int, calls: int) -> Dict:
        """Calcula métricas de outreach baseadas em benchmarks 2025"""
        
        open_rate = opened / sent if sent > 0 else 0
        response_rate = replied / sent if sent > 0 else 0
        call_conversion = calls / replied if replied > 0 else 0
        
        # Benchmarks 2025
        benchmarks = {
            "open_rate_benchmark": 0.25,      # 25% open rate B2B
            "response_rate_benchmark": 0.09,   # 9% response rate
            "call_conversion_benchmark": 0.30  # 30% call conversion
        }
        
        performance = {
            "open_rate": open_rate,
            "response_rate": response_rate,
            "call_conversion_rate": call_conversion,
            "performance_vs_benchmark": {
                "open_rate": "ABOVE" if open_rate > benchmarks["open_rate_benchmark"] else "BELOW",
                "response_rate": "ABOVE" if response_rate > benchmarks["response_rate_benchmark"] else "BELOW",
                "call_conversion": "ABOVE" if call_conversion > benchmarks["call_conversion_benchmark"] else "BELOW"
            },
            "recommendations": []
        }
        
        # Recomendações baseadas em performance
        if open_rate < 0.20:
            performance["recommendations"].append("Melhorar subject lines - usar números e urgência")
        
        if response_rate < 0.06:
            performance["recommendations"].append("Aumentar personalização e reduzir pitch inicial")
        
        if call_conversion < 0.25:
            performance["recommendations"].append("Melhorar qualificação antes da call + agenda específica")
        
        return performance


# Templates prontos para uso
READY_TO_USE_TEMPLATES = {
    "audit_express_subject_lines": [
        "ROI de Velocidade para {company_name}",
        "{company_name}: 3 vazamentos custando conversões",
        "Auditoria Express 48h - {company_name}",
        "Performance mobile crítica no {domain}",
        "Última semana: slots Auditoria Express"
    ],
    
    "teardown_60s_subject_lines": [
        "3 vazamentos no {domain} [vídeo 60s]",
        "Analisei o {domain} - vídeo pronto",
        "Viu o vídeo do {domain}?",
        "{company_name}: problemas custando 15% conversões",
        "Quick fix: +8% conversões em 48h"
    ],
    
    "landing_relampago_subject_lines": [
        "Kit: Página de Alta Conversão [download direto]",
        "Case: De 2.1% para 4.8% conversão em 6 dias",
        "Sprint 7 dias - {company_name}",
        "Wireframe + checklist mobile [gratuito]",
        "Garantia: achados acionáveis ou devolvo 100%"
    ]
}


if __name__ == "__main__":
    # Teste dos templates
    templates = OutreachTemplates2025()
    
    # Prospect de exemplo
    prospect_data = {
        "company_name": "TechStart Solutions",
        "domain": "techstart.com",
        "contact_name": "Maria",
        "industry": "saas",
        "sender_name": "João"
    }
    
    # Teardown insights de exemplo
    teardown_insights = {
        "domain": "techstart.com",
        "performance_score": 58,
        "issue_1": "Performance mobile crítica (58/100)",
        "issue_2": "CLS alto prejudicando UX",
        "issue_3": "Imagens não otimizadas (2.3MB total)"
    }
    
    # Gerar sequências
    audit_sequence = templates.generate_audit_express_sequence(prospect_data)
    teardown_sequence = templates.generate_teardown_60s_sequence(prospect_data, teardown_insights)
    landing_sequence = templates.generate_landing_relampago_sequence(prospect_data)
    
    print("TEMPLATES DE OUTREACH 2025 - GERADOS")
    print("="*50)
    print(f"Audit Express: {len(audit_sequence)} emails")
    print(f"Teardown 60s: {len(teardown_sequence)} emails") 
    print(f"Landing Relâmpago: {len(landing_sequence)} emails")
    
    # Salvar templates
    output = {
        "audit_express_sequence": [msg.__dict__ for msg in audit_sequence],
        "teardown_60s_sequence": [msg.__dict__ for msg in teardown_sequence],
        "landing_relampago_sequence": [msg.__dict__ for msg in landing_sequence],
        "ready_templates": READY_TO_USE_TEMPLATES,
        "weekly_plan": templates.generate_weekly_outreach_plan({})
    }
    
    with open("outputs/outreach_templates_2025.json", "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)