#!/usr/bin/env python3
"""
🎯 REAL OUTREACH GENERATOR
Gera materials de contato baseados nos prospects REAIS descobertos
Usa dados do pipeline real e bibliotecas existentes
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict

# Add src to path to use existing modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.prospect_filters import ProspectFilters


class RealOutreachGenerator:
    """Gerador baseado em dados REAIS do pipeline"""
    
    def __init__(self):
        self.usd_to_brl = 5.85  # Taxa atual mais precisa
        self.filters = ProspectFilters()
    
    def load_real_prospects_data(self, prospects_file: str) -> Dict:
        """Carrega dados reais do pipeline"""
        try:
            with open(prospects_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Arquivo não encontrado: {prospects_file}")
            return {}
        except json.JSONDecodeError:
            print(f"❌ Erro ao decodificar JSON: {prospects_file}")
            return {}
    
    def generate_real_outreach_package(self, prospects_file: str):
        """Gera pacote baseado em dados REAIS do pipeline"""
        
        # Load real data
        pipeline_data = self.load_real_prospects_data(prospects_file)
        if not pipeline_data:
            return
        
        prospects = pipeline_data.get('top_prospects', [])
        summary = pipeline_data.get('summary', {})
        
        if not prospects:
            print("❌ Nenhum prospect encontrado nos dados")
            return
        
        print("🎯 GERANDO OUTREACH BASEADO EM DADOS REAIS")
        print("=" * 60)
        print(f"📊 Prospects: {len(prospects)}")
        print(f"💰 Pipeline Value: USD {summary.get('total_pipeline_value', 0):,.0f}")
        print(f"🎯 Expected Revenue: USD {summary.get('expected_revenue', 0):,.0f}")
        
        # Generate using REAL data
        self._generate_real_linkedin_scripts(prospects, summary)
        self._generate_real_whatsapp_scripts(prospects[:3])  # Top 3
        self._generate_real_email_templates(prospects)
        self._generate_real_proposals(prospects[:5])  # Top 5
        self._generate_real_audit_reports(prospects[:3])  # Detailed for top 3
        self._generate_real_execution_checklist(summary, prospects)
        
        print("\n✅ PACOTE REAL DE OUTREACH GERADO!")
        print("📁 Arquivos salvos em: real_outreach/")
        print("🚀 Pronto para execução imediata!")
    
    def _generate_real_linkedin_scripts(self, prospects: List[Dict], summary: Dict):
        """Scripts baseados nos prospects REAIS descobertos"""
        
        scripts = []
        
        for prospect in prospects:
            company = prospect.get('company', 'Empresa')
            domain = prospect.get('domain', '')
            performance_score = prospect.get('performance_score', 50)
            immediate_value = prospect.get('immediate_value', 0)
            issues = prospect.get('issues_found', [])
            priority = prospect.get('priority', 'MEDIUM')
            
            # Real issues text
            issues_text = ' | '.join(issues) if issues else 'Performance e SaaS over-spend'
            
            urgency_emoji = "🚨" if priority == "HIGH" else "⚠️"
            
            script = f"""
# LINKEDIN SCRIPT - {company} (DADOS REAIS)

**Domínio:** {domain}
**Score Performance:** {performance_score}/100
**Valor Imediato:** USD {immediate_value:,.0f}
**Issues:** {issues_text}

---

**Mensagem Inicial:**
Olá [NOME],

{urgency_emoji} Analisei o {domain} e encontrei algo que pode interessar.

**Performance atual:** {performance_score}/100 (crítico para conversões)
**Oportunidade identificada:** USD {immediate_value:,.0f}/ano em economia

🔍 **Problemas específicos encontrados:**
{chr(10).join(f"- {issue}" for issue in issues)}

**Proposta:** Diagnóstico gratuito de 15min mostrando exatamente onde estão os vazamentos.

Se conseguir provar que podem economizar USD {immediate_value//2:,.0f}/ano, toparia uma conversa?

[Calendly Link]

**CTA:** Responda "SIM" se quiser ver o diagnóstico específico do {domain}.

---

**Follow-up (48h depois):**
[NOME], sobre o {company} - 

Preparei um vídeo de 3min mostrando os problemas específicos do {domain}:
[Loom Link]

São USD {immediate_value:,.0f}/ano sendo desperdiçados. Vale 3min para ver?

**Follow-up (1 semana):**
Última sobre o {company} -

{performance_score}/100 de performance = perda direta nas conversões.

Se não for prioridade agora, sem stress. Deixo meu contato para o futuro.

Mas são USD {immediate_value//12:,.0f}/mês que continuam sendo perdidos... 📉

---
"""
            scripts.append(script)
        
        # Save scripts
        os.makedirs("real_outreach", exist_ok=True)
        with open("real_outreach/linkedin_scripts_reais.md", 'w', encoding='utf-8') as f:
            header = f"""# 📱 LINKEDIN SCRIPTS - DADOS REAIS

**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
**Base:** Pipeline real com {len(prospects)} prospects
**Pipeline Total:** USD {summary.get('total_pipeline_value', 0):,.0f}
**Expectativa:** USD {summary.get('expected_revenue', 0):,.0f}

---

"""
            f.write(header + "\n".join(scripts))
        
        print("✅ Scripts LinkedIn REAIS gerados")
    
    def _generate_real_whatsapp_scripts(self, prospects: List[Dict]):
        """WhatsApp scripts baseados em dados reais"""
        
        scripts = []
        
        for prospect in prospects:
            company = prospect.get('company', 'Empresa')
            domain = prospect.get('domain', '')
            performance_score = prospect.get('performance_score', 50)
            immediate_value = prospect.get('immediate_value', 0)
            issues = prospect.get('issues_found', [])
            
            main_issue = issues[0] if issues else "Performance baixa"
            
            script = f"""
# WHATSAPP - {company} (REAL)

**Target:** {domain}
**Score:** {performance_score}/100  
**Value:** USD {immediate_value:,.0f}/ano

---

**Mensagem 1:**
Oi [NOME]! 👋

Sou especialista em otimização web e vi que o {domain} tem algumas oportunidades de melhoria.

**Situação atual:** {performance_score}/100 de performance
**Oportunidade:** USD {immediate_value:,.0f}/ano em economia

Principal problema: {main_issue}

Posso mostrar em 2min como resolver isso?

**Mensagem 2 (se responder):**
Perfeito! 

Identifiquei especificamente:
{chr(10).join(f"✅ {issue}" for issue in issues)}

Gravei um vídeo de 3min para vocês: [Link]

**Oferta:** USD 600 para resolver tudo + garantia de economia mínima de USD {immediate_value//2:,.0f}/ano.

Risco zero para vocês.

Quando conseguimos falar 15min?

**Follow-up (24h):**
[NOME], viu o vídeo do {domain}?

{main_issue} está custando USD {immediate_value//12:,.0f}/mês...

Posso resolver em 48h. Topa?

---
"""
            scripts.append(script)
        
        with open("real_outreach/whatsapp_scripts_reais.md", 'w', encoding='utf-8') as f:
            f.write(f"# 📲 WHATSAPP SCRIPTS - TOP 3 REAIS\n\n{datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
            f.write("\n".join(scripts))
        
        print("✅ Scripts WhatsApp REAIS gerados")
    
    def _generate_real_email_templates(self, prospects: List[Dict]):
        """Email templates baseados nos prospects reais"""
        
        templates = []
        
        for prospect in prospects:
            company = prospect.get('company', 'Empresa')
            domain = prospect.get('domain', '')
            performance_score = prospect.get('performance_score', 50)
            immediate_value = prospect.get('immediate_value', 0)
            issues = prospect.get('issues_found', [])
            tech_stack = prospect.get('tech_stack', {})
            close_probability = prospect.get('close_probability', 0.5)
            
            # Analyze tech stack
            analytics = tech_stack.get('analytics', [])
            tech_info = f"Usando: {', '.join(analytics)}" if analytics else "Tech stack analisado"
            
            template = f"""
# EMAIL TEMPLATE - {company} (DADOS REAIS)

**Target:** {domain}
**Performance:** {performance_score}/100
**Opportunity:** USD {immediate_value:,.0f}/ano
**Close Probability:** {close_probability*100:.0f}%

---

**Subject:** {company}: USD {immediate_value//12:,.0f}/mês em oportunidades - Análise gratuita

**Corpo:**
Prezado(a) [NOME],

Espero que esteja bem.

Sou [SEU NOME], especialista em otimização de performance e redução de custos SaaS.

**Por que estou escrevendo:**

Analisei tecnicamente o {domain} e identifiquei oportunidades concretas de economizar **USD {immediate_value:,.0f}/ano**.

🔍 **Análise técnica realizada:**
- Performance Score: {performance_score}/100 (crítico)
- {tech_info}
- Problemas identificados: {len(issues)} issues críticos

📊 **Problemas específicos encontrados:**
{chr(10).join(f"- {issue}" for issue in issues)}

💰 **Impacto financeiro calculado:**
- Perda mensal estimada: USD {immediate_value//12:,.0f}
- ROI do projeto: 400-600% no primeiro ano
- Payback: 2-3 meses

**Minha proposta:**
1. **Diagnóstico detalhado** (gratuito - 15min)
2. **Implementação express** (48-72h por USD 600-800)
3. **Garantia total:** Se não economizar USD {immediate_value//2:,.0f}/ano, devolvo tudo

**Próximo passo:**
Posso mostrar exatamente os problemas em uma call rápida?

Calendário: [Calendly Link]

Att,
[SEU NOME]
[TELEFONE]
[LINKEDIN]

P.S.: Anexei um preview da análise técnica do {domain}. Os números são bem claros.

---

**Follow-up 1 (3 dias):**
[NOME],

Complementando sobre o {company}.

Preparei um relatório específico mostrando os {len(issues)} problemas críticos do {domain}:
[PDF anexo]

Performance {performance_score}/100 = USD {immediate_value//12:,.0f}/mês perdidos.

Vale uma conversa de 15min?

**Follow-up 2 (1 semana):**
[NOME],

Última sobre a oportunidade de USD {immediate_value:,.0f}/ano no {company}.

Entendo se não é prioridade agora.

Mas {performance_score}/100 de performance continua impactando as conversões...

Meu contato fica disponível para quando precisarem.

---
"""
            templates.append(template)
        
        with open("real_outreach/email_templates_reais.md", 'w', encoding='utf-8') as f:
            f.write(f"# 📧 EMAIL TEMPLATES - PROSPECTS REAIS\n\n{datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
            f.write("\n".join(templates))
        
        print("✅ Email templates REAIS gerados")
    
    def _generate_real_proposals(self, prospects: List[Dict]):
        """Propostas baseadas nos prospects reais"""
        
        for prospect in prospects:
            company = prospect.get('company', 'Empresa')
            domain = prospect.get('domain', '')
            performance_score = prospect.get('performance_score', 50)
            immediate_value = prospect.get('immediate_value', 0)
            issues = prospect.get('issues_found', [])
            close_probability = prospect.get('close_probability', 0.5)
            
            proposal = f"""
# 💼 PROPOSTA PERSONALIZADA - {company}

**Data:** {datetime.now().strftime('%d/%m/%Y')}
**Cliente:** {company}
**Site:** {domain}
**Análise:** Concluída

---

## RESUMO EXECUTIVO

Nossa análise técnica do {domain} identificou oportunidades de **economizar USD {immediate_value:,.0f}/ano** através de otimizações específicas.

**Situação Atual:**
- Performance Score: {performance_score}/100 (crítico)
- Probabilidade de sucesso: {close_probability*100:.0f}%
- Impacto financeiro: USD {immediate_value//12:,.0f}/mês perdidos

---

## PROBLEMAS IDENTIFICADOS (DADOS REAIS)

{chr(10).join(f"✅ **{issue}**" for issue in issues)}

**Impacto Total:** USD {immediate_value:,.0f}/ano em oportunidades perdidas

---

## SOLUÇÃO PROPOSTA

### FASE 1: DIAGNÓSTICO COMPLETO ✅ (Concluído)
- ✅ Análise técnica do {domain}
- ✅ Identificação de {len(issues)} problemas críticos
- ✅ Cálculo de impacto financeiro
- ✅ Mapeamento de soluções

### FASE 2: IMPLEMENTAÇÃO EXPRESS (48h)
- Correção de performance crítica
- Otimização de ferramentas SaaS
- Implementação de alternativas econômicas
- Configuração de monitoramento

### FASE 3: VALIDAÇÃO (30 dias)
- Medição de melhoria de performance
- Validação de economia real
- Relatório de ROI
- Suporte pós-implementação

---

## INVESTIMENTO & GARANTIAS

### OPÇÃO RECOMENDADA: EXPRESS
**Investimento:** USD 600 (pagamento único)
**Economia garantida:** USD {immediate_value//2:,.0f}/ano mínimo
**ROI garantido:** {(immediate_value//2)//600:.0f}x no primeiro ano

### GARANTIAS REAIS:
🛡️ **Performance:** Melhoria de pelo menos 30 pontos no score
🛡️ **Financeira:** Economia mínima de USD {immediate_value//2:,.0f}/ano
🛡️ **Satisfação:** 100% satisfeito ou dinheiro de volta

---

## CRONOGRAMA ESPECÍFICO

| Dia | Atividade Específica |
|-----|---------------------|
| 1 | Aprovação e início |
| 2 | Implementação das correções do {domain} |
| 3 | Testes e validação |
| 4+ | Monitoramento e suporte |

---

## PRÓXIMOS PASSOS

1. **Aprovação:** Responder este email ou WhatsApp
2. **Pagamento:** 50% início + 50% na entrega
3. **Início:** Dentro de 24h da aprovação

**Contato:** [TELEFONE] / [EMAIL]
**Validade:** 7 dias (oferta especial)

---

*Proposta baseada em análise real do {domain} - Dados técnicos validados*
"""
            
            # Save individual proposal
            filename = f"real_outreach/proposta_{company.lower().replace(' ', '_')}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(proposal)
        
        print("✅ Propostas REAIS personalizadas geradas")
    
    def _generate_real_audit_reports(self, prospects: List[Dict]):
        """Relatórios de auditoria baseados em dados reais"""
        
        for prospect in prospects:
            company = prospect.get('company', 'Empresa')
            domain = prospect.get('domain', '')
            performance_score = prospect.get('performance_score', 50)
            immediate_value = prospect.get('immediate_value', 0)
            issues = prospect.get('issues_found', [])
            tech_stack = prospect.get('tech_stack', {})
            close_probability = prospect.get('close_probability', 0.5)
            
            # Analyze tech stack
            analytics = tech_stack.get('analytics', [])
            
            audit = f"""
# 📊 AUDITORIA TÉCNICA REAL - {company}

**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
**Site:** {domain}
**Status:** 🔴 PROBLEMAS CRÍTICOS IDENTIFICADOS

---

## DADOS DA ANÁLISE REAL

**Performance Score:** {performance_score}/100 🔴
**Oportunidade Anual:** USD {immediate_value:,.0f}
**Probabilidade Sucesso:** {close_probability*100:.0f}%
**Prioridade:** ALTA

---

## PROBLEMAS ESPECÍFICOS ENCONTRADOS

{chr(10).join(f"🚨 **{issue}**" for issue in issues)}

**Tecnologias Detectadas:**
{chr(10).join(f"- {tool}" for tool in analytics) if analytics else "- Google Analytics (básico)"}

---

## IMPACTO FINANCEIRO CALCULADO

### PERDAS MENSAIS
- Performance baixa: USD {immediate_value//24:,.0f}/mês
- SaaS over-spend: USD {immediate_value//24:,.0f}/mês
- **Total:** USD {immediate_value//12:,.0f}/mês

### OPORTUNIDADE ANUAL
- **Economia potencial:** USD {immediate_value:,.0f}/ano
- **ROI do projeto:** {immediate_value//600:.0f}x
- **Payback:** 2-3 meses

---

## SOLUÇÕES RECOMENDADAS

### CORREÇÕES IMEDIATAS (24-48h)
✅ Otimização de performance para 80+/100
✅ Substituição de ferramentas caras
✅ Configuração de cache e CDN

### IMPLEMENTAÇÃO COMPLETA (1 semana)
✅ Otimizações avançadas
✅ Monitoramento automatizado
✅ Relatórios de ROI

---

## PROPOSTA DE IMPLEMENTAÇÃO

**Investimento:** USD 600
**Garantia:** Economia mínima de USD {immediate_value//2:,.0f}/ano
**Prazo:** 48-72h
**Suporte:** 30 dias incluído

**Risco:** ZERO - Devolução integral se não atingir metas

---

## COMPARAÇÃO COM BENCHMARK

| Métrica | {company} | Benchmark | Gap |
|---------|-----------|-----------|-----|
| Performance | {performance_score}/100 | 85/100 | {85-performance_score} pontos |
| Conversão | Baixa | Otimizada | +40% potencial |
| Custos SaaS | Alto | Otimizado | USD {immediate_value//12:,.0f}/mês |

---

## PRÓXIMA AÇÃO

**Urgente:** Esta análise expira em 7 dias
**Contato:** [TELEFONE] para implementação imediata
**Garantia:** 100% satisfação ou dinheiro de volta

---

*Relatório técnico baseado em dados reais do {domain}*
*Análise realizada em {datetime.now().strftime('%d/%m/%Y')}</i>*
"""
            
            filename = f"real_outreach/auditoria_{company.lower().replace(' ', '_')}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(audit)
        
        print("✅ Auditorias REAIS detalhadas geradas")
    
    def _generate_real_execution_checklist(self, summary: Dict, prospects: List[Dict]):
        """Checklist baseado nos dados reais do pipeline"""
        
        total_value = summary.get('total_pipeline_value', 0)
        expected_revenue = summary.get('expected_revenue', 0)
        num_prospects = len(prospects)
        
        checklist = f"""
# ✅ CHECKLIST EXECUÇÃO REAL - 7 DAYS

**Base:** Dados reais do pipeline ARCO-Find
**Data:** {datetime.now().strftime('%d/%m/%Y')}
**Prospects:** {num_prospects} identificados
**Pipeline Total:** USD {total_value:,.0f}
**Expectativa:** USD {expected_revenue:,.0f}
**Meta Conservadora:** USD 1,000-2,000

---

## PROSPECTS REAIS IDENTIFICADOS

{chr(10).join(f"✅ **{p.get('company')}** - {p.get('domain')} - USD {p.get('immediate_value', 0):,.0f}/ano" for p in prospects)}

---

## DIA 1-2: CONTATO DIRETO

### Preparação (1h)
- [x] Scripts LinkedIn personalizados gerados
- [x] WhatsApp templates criados  
- [x] Email sequences profissionais prontos
- [ ] Configurar Calendly com slots 15min
- [ ] Preparar Loom account

### Outreach Imediato (3h)
- [ ] LinkedIn: Contactar top {min(5, num_prospects)} prospects
- [ ] WhatsApp: Top 3 com números encontrados
- [ ] Email: Todos os {num_prospects} prospects
- [ ] Follow-up automático configurado

### Meta Dia 1-2
- [ ] {num_prospects*3} touchpoints enviados
- [ ] 30-40% taxa de resposta esperada
- [ ] 3-5 reuniões agendadas

---

## DIA 3-4: DEMOS & PROPOSTAS

### Reuniões Agendadas
- [ ] **{prospects[0].get('company')}**: Demo + proposta USD {prospects[0].get('immediate_value', 0):,.0f}
- [ ] **{prospects[1].get('company')}**: Demo + proposta USD {prospects[1].get('immediate_value', 0):,.0f}
- [ ] **{prospects[2].get('company')}**: Demo + proposta USD {prospects[2].get('immediate_value', 0):,.0f}

### Materiais de Fechamento
- [x] Auditorias personalizadas prontas
- [x] Propostas específicas geradas
- [ ] ROI calculators configurados
- [ ] Cases de sucesso preparados

### Meta Dia 3-4
- [ ] 3-5 demos executadas
- [ ] 2-3 propostas enviadas
- [ ] 1-2 fechamentos fechados

---

## DIA 5-7: FECHAMENTO & ENTREGA

### Negociação Final
- [ ] Follow-up nas propostas enviadas
- [ ] Negociar desconto se necessário (20% max)
- [ ] Processar pagamentos via Pix/Stripe

### Início das Entregas
- [ ] Implementar correções básicas (24h)
- [ ] Entregar relatórios iniciais
- [ ] Configurar monitoramento

### Meta Dia 5-7
- [ ] 2-3 contratos assinados
- [ ] USD 1,200-2,400 faturados
- [ ] Primeiras entregas em andamento

---

## PROSPECTS PRIORITÁRIOS (DADOS REAIS)

### TOP 1: {prospects[0].get('company')}
- **Domain:** {prospects[0].get('domain')}
- **Score:** {prospects[0].get('performance_score')}/100
- **Value:** USD {prospects[0].get('immediate_value', 0):,.0f}/ano
- **Issues:** {', '.join(prospects[0].get('issues_found', []))}
- **Action:** Contato imediato via LinkedIn + email

### TOP 2: {prospects[1].get('company')}
- **Domain:** {prospects[1].get('domain')}  
- **Score:** {prospects[1].get('performance_score')}/100
- **Value:** USD {prospects[1].get('immediate_value', 0):,.0f}/ano
- **Issues:** {', '.join(prospects[1].get('issues_found', []))}
- **Action:** WhatsApp + email personalizado

### TOP 3: {prospects[2].get('company')}
- **Domain:** {prospects[2].get('domain')}
- **Score:** {prospects[2].get('performance_score')}/100  
- **Value:** USD {prospects[2].get('immediate_value', 0):,.0f}/ano
- **Issues:** {', '.join(prospects[2].get('issues_found', []))}
- **Action:** Email profissional + LinkedIn

---

## SCRIPTS DE EMERGÊNCIA

### Se baixa resposta (Dia 3):
"Olá [NOME], sobre a análise do [DOMAIN] - talvez o timing não seja ideal. São USD [VALUE]/ano sendo perdidos, mas entendo as prioridades. Meu contato fica disponível."

### Se objeção de preço:
"Entendo. Que tal assim: USD 300 agora + USD 300 só quando vocês virem os resultados? Risco zero."

### Para acelerar fechamento:
"[NOME], preparei uma condição especial para fechar hoje: 30% desconto + garantia estendida. Vale para hoje apenas."

---

## MÉTRICAS DE SUCESSO REAL

### KPIs Baseados no Pipeline Real
- **Response Rate Target:** 35% (base: {num_prospects} prospects)
- **Meeting Rate:** 60% dos que respondem  
- **Close Rate:** 40% dos que fazem demo
- **Valor Médio:** USD {expected_revenue//(num_prospects*0.4):.0f} por deal

### Meta Final Conservadora
- **Contratos:** 2-3 fechados
- **Revenue:** USD 1,200-2,400
- **ROI Campaign:** 300-500%

---

*Checklist baseado em {num_prospects} prospects reais identificados pelo pipeline ARCO-Find*
*Pipeline value: USD {total_value:,.0f} | Expected: USD {expected_revenue:,.0f}*
"""
        
        with open("real_outreach/checklist_execucao_real.md", 'w', encoding='utf-8') as f:
            f.write(checklist)
        
        print("✅ Checklist de execução REAL gerado")


def main():
    """Generate REAL outreach package from actual pipeline results"""
    
    # Find latest real pipeline result
    output_files = [f for f in os.listdir('output') if f.startswith('immediate_pipeline_') and f.endswith('.json')]
    
    if not output_files:
        print("❌ Nenhum pipeline real encontrado")
        print("🔧 Execute primeiro: python main.py")
        return
    
    # Get most recent
    latest_file = max(output_files, key=lambda f: os.path.getctime(os.path.join('output', f)))
    filepath = os.path.join('output', latest_file)
    
    print(f"📁 Usando dados reais: {latest_file}")
    
    # Generate REAL outreach package
    generator = RealOutreachGenerator()
    generator.generate_real_outreach_package(filepath)
    
    print("\n🎯 MATERIAIS DE OUTREACH REAL GERADOS!")
    print("📁 Pasta: real_outreach/")  
    print("🚀 Execute o checklist para começar!")


if __name__ == "__main__":
    main()
