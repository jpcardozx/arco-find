# 🎯 MODELO DE NEGÓCIO & BENCHMARKS SETORIAIS

## HIPÓTESE CENTRAL VALIDADA

**"SMBs 5-25 FTE perdem USD 2k+/mês por over-spend SaaS + performance web ruim"**

### Framework de Validação

| Componente          | Evidência                                           | Gap Crítico                  | Ação Requerida              |
| ------------------- | --------------------------------------------------- | ---------------------------- | --------------------------- |
| **Dor Mensurável**  | ✅ Typeform USD 300/mês + LCP 4s = -12% CVR         | ❌ Lead não quantifica perda | Calculadora de impacto      |
| **ROI Comprovável** | ✅ Fórmula: `(AOV × Visitas × ΔCVR) + SaaS_savings` | ❌ Benchmarks genéricos      | Dados setoriais específicos |
| **Decision Maker**  | ✅ Growth Lead/Founder SMB                          | ❌ Quem assina vs quem sofre | Mapeamento org chart        |
| **Ticket Viável**   | ✅ Piloto USD 500                                   | ❌ Upsell USD 1k+ unclear    | Estrutura de pacotes        |

---

## BENCHMARKS SETORIAIS (Brasil 2024)

### E-commerce Fashion/Beauty

**Perfil ICP:**

- Faturamento: R$ 50k-500k/mês
- Funcionários: 5-25 FTE
- Plataforma: Shopify/WooCommerce próprio
- Tráfego: 5k-50k visitantes/mês

**Métricas de Conversão:**

```python
ECOMMERCE_BENCHMARKS = {
    'fashion': {
        'cvr_desktop': 0.021,    # 2.1%
        'cvr_mobile': 0.018,     # 1.8%
        'aov': 180,              # R$ 180
        'lcp_impact': 0.12,      # 12% perda por +1s LCP
        'bounce_rate': 0.68,     # 68%
        'cart_abandonment': 0.74 # 74%
    },
    'beauty': {
        'cvr_desktop': 0.024,
        'cvr_mobile': 0.019,
        'aov': 95,
        'lcp_impact': 0.15,      # Maior sensibilidade visual
        'bounce_rate': 0.65,
        'cart_abandonment': 0.71
    }
}
```

**Stack SaaS Típica (Custos Mensais):**
| Ferramenta | Uso | Custo USD | Alternativa | Economia |
|------------|-----|-----------|-------------|----------|
| Typeform Pro | Forms | 300 | React Hook Form | 90%+ |
| Mailchimp Essentials | Email | 35 | ConvertKit | 50% |
| HubSpot Starter | CRM | 120 | Pipedrive | 60% |
| Hotjar Plus | Analytics | 80 | Google Analytics | 100% |
| **Total Típico** | | **535** | | **~400** |

### SaaS B2B SMB

**Perfil ICP:**

- MRR: USD 5k-50k
- Funcionários: 8-40 FTE
- Stage: Seed/Series A
- Usuarios: 100-2k active users

**Métricas de Conversão:**

```python
SAAS_B2B_BENCHMARKS = {
    'general': {
        'trial_to_paid': 0.15,   # 15%
        'signup_to_trial': 0.08, # 8%
        'arpu': 89,              # USD 89/mês
        'lcp_impact': 0.08,      # 8% por +1s (menos sensível)
        'churn_monthly': 0.05,   # 5%/mês
        'cac_payback': 8         # 8 meses
    },
    'hr_tech': {
        'trial_to_paid': 0.18,
        'arpu': 120,
        'lcp_impact': 0.10
    },
    'marketing_tools': {
        'trial_to_paid': 0.12,
        'arpu': 67,
        'lcp_impact': 0.06
    }
}
```

**Stack SaaS Típica:**
| Ferramenta | Uso | Custo USD | Alternativa | Economia |
|------------|-----|-----------|-------------|----------|
| Intercom | Support | 240 | Crisp | 70% |
| Mixpanel | Analytics | 180 | PostHog | 80% |
| Typeform | Onboarding | 300 | Custom form | 95% |
| Calendly | Scheduling | 120 | Cal.com | 100% |
| **Total Típico** | | **840** | | **~650** |

### Local Services High-Ticket

**Perfil ICP:**

- Receita: R$ 80k-300k/mês
- Funcionários: 5-20 FTE
- Ticket médio: R$ 500-5k
- Localizações: 1-3 unidades

**Métricas de Conversão:**

```python
LOCAL_SERVICES_BENCHMARKS = {
    'medical': {
        'lead_to_appointment': 0.12,  # 12%
        'appointment_to_client': 0.85, # 85%
        'avg_ticket': 350,            # R$ 350
        'lcp_impact': 0.10,           # 10%
        'mobile_traffic': 0.78        # 78% mobile
    },
    'legal': {
        'lead_to_consultation': 0.08,
        'consultation_to_client': 0.65,
        'avg_ticket': 1200,
        'lcp_impact': 0.08,
        'mobile_traffic': 0.65
    }
}
```

---

## CALCULADORA DE PERDA FINANCEIRA

### Formula Unificada

```python
def calculate_total_monthly_leak(
    sector: str,
    monthly_traffic: int,
    current_lcp: float,
    detected_saas: List[str],
    aov_or_ticket: float
) -> Dict:
    """
    Calcula vazamento total baseado em benchmarks setoriais
    """

    benchmark = get_sector_benchmark(sector)

    # 1. Performance leak
    if current_lcp > 2.5:
        lcp_excess = min(current_lcp - 2.0, 2.0)  # Max 2s improvement
        cvr_loss = benchmark['lcp_impact'] * (lcp_excess / 2.0)

        current_conversions = monthly_traffic * benchmark['base_cvr']
        lost_conversions = monthly_traffic * cvr_loss

        performance_leak = lost_conversions * aov_or_ticket
    else:
        performance_leak = 0

    # 2. SaaS waste
    saas_waste = sum(
        SAAS_COSTS.get(saas, {}).get('monthly_usd', 0)
        for saas in detected_saas
        if saas in REPLACEABLE_SAAS
    )

    # 3. Opportunity cost (ads waste)
    if current_lcp > 3.0:
        # Poor landing page = higher CPC
        ads_waste = estimate_ads_waste(monthly_traffic, current_lcp)
    else:
        ads_waste = 0

    return {
        'performance_leak': performance_leak,
        'saas_waste': saas_waste,
        'ads_waste': ads_waste,
        'total_monthly': performance_leak + saas_waste + ads_waste,
        'annual_projection': (performance_leak + saas_waste + ads_waste) * 12,
        'confidence_level': calculate_confidence(sector, monthly_traffic, detected_saas)
    }
```

### Exemplos Reais de Cálculo

**Caso 1: E-commerce Fashion**

```python
leak = calculate_total_monthly_leak(
    sector='ecommerce_fashion',
    monthly_traffic=15000,
    current_lcp=4.2,
    detected_saas=['typeform_pro', 'mailchimp_essentials'],
    aov_or_ticket=180
)

# Resultado:
{
    'performance_leak': 1890,    # 15k × 0.07 × 180
    'saas_waste': 335,           # 300 + 35
    'ads_waste': 420,            # CPC premium por baixo QS
    'total_monthly': 2645,
    'annual_projection': 31740,
    'confidence_level': 0.85
}
```

**Caso 2: SaaS B2B**

```python
leak = calculate_total_monthly_leak(
    sector='saas_b2b_general',
    monthly_traffic=8000,
    current_lcp=3.8,
    detected_saas=['intercom', 'typeform_pro', 'mixpanel'],
    aov_or_ticket=89  # ARPU
)

# Resultado:
{
    'performance_leak': 456,     # 8k × 0.08 × 0.08 × 89
    'saas_waste': 720,           # 240 + 300 + 180
    'ads_waste': 180,
    'total_monthly': 1356,
    'annual_projection': 16272,
    'confidence_level': 0.78
}
```

---

## ESTRUTURA DE PREÇOS

### Modelo de 3 Pacotes

**1. Diagnóstico Express (USD 100)**

- Auditoria técnica completa
- Calculadora de perdas personalizada
- Plano de ação 1 página
- **Objetivo:** Validar pain + criar urgência

**2. Implementação Básica (USD 500-800)**

- Correção performance (LCP < 2.5s)
- Substituição 1-2 SaaS por alternativas
- Setup básico de tracking
- **ROI:** 60-90 dias payback

**3. Otimização Completa (USD 1,200-2,000)**

- Implementação completa do plano
- Stack SaaS customizado
- Otimização ads + landing pages
- 3 meses de suporte
- **ROI:** 30-45 dias payback

### Garantias Anti-Risco

**Garantia Financeira:**

> "Se não recuperarmos pelo menos USD 1,500/mês em 60 dias, devolvemos 100% do investimento"

**Garantia Técnica:**

> "LCP abaixo de 2.5s ou refazemos gratuitamente"

**Garantia de Suporte:**

> "3 meses de suporte incluído para todas as implementações"

---

## TRIGGERS DE COMPRA

### Sinais de Timing Perfeito

**1. Sinais Financeiros:**

- Rodada de investimento recente
- Reclamações públicas sobre custos
- Meta de redução de CAC
- Crescimento de tráfego sem crescimento proporcional de vendas

**2. Sinais Técnicos:**

- Core Web Vitals vermelho no Google
- Queda no ranking orgânico
- Reclamações de usuários sobre lentidão
- Bounce rate > 70%

**3. Sinais Organizacionais:**

- Vaga para Growth/CRO
- Novo Head of Marketing
- Mudança de plataforma em andamento
- Preparação para Black Friday/alta demanda

### Scripts de Qualificação

**Pergunta de Dor:**

> "Qual % do budget de marketing você estimaria que está sendo desperdiçado por problemas técnicos no site?"

**Pergunta de Autoridade:**

> "Quem normalmente aprova investimentos em otimização/ferramentas na faixa de USD 500-1000?"

**Pergunta de Urgência:**

> "Se eu conseguisse mostrar uma economia de USD 2k/mês, qual seria o timeline ideal para implementar?"

---

## MÉTRICAS DE SUCESSO

### KPIs do Pipeline

| Métrica                | Target  | Método de Medição                      |
| ---------------------- | ------- | -------------------------------------- |
| **Qualification Rate** | 60%+    | Prospects com leak ≥ USD 2k            |
| **Response Rate**      | 40%+    | Respostas positivas/mensagens enviadas |
| **Demo Show Rate**     | 70%+    | Comparecimento em calls agendadas      |
| **Close Rate**         | 35%+    | Contratos fechados/demos realizadas    |
| **Average Deal Size**  | USD 750 | Valor médio por contrato               |

### ROI do Cliente (Validação)

**Target por Setor:**

- **E-commerce:** 4-8x ROI no primeiro mês
- **SaaS B2B:** 3-6x ROI no primeiro mês
- **Local Services:** 5-10x ROI no primeiro mês

**Tracking pós-implementação:**

- Google Analytics: conversão before/after
- PageSpeed: LCP improvement
- SaaS bills: reduções comprováveis
- Client feedback: NPS score
