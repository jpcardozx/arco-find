# 🎯 ARCO ENGINE V3: PERFORMANCE-DRIVEN LEAD GENERATION

## 📋 **EXECUTIVE SUMMARY**

**Objetivo:** Sistema de aquisição de clientes B2B focado em **CRO & Web Performance** para mercados USD/EUR/GBP, baseado em evidências objetivas de vazamento de receita.

**Tese:** Quando existe **gasto em mídia paga + páginas lentas/LPs desalinhadas**, há **vazamento direto de receita**. Nossa solução: sprints curtos (2-3 semanas) + aceite por métrica (Core Web Vitals + A/B) + rastreio confiável.

**ROI Esperado:**

- Redução de CPA: 15-30%
- Aumento de CVR: 10-25%
- Time to close: <21 dias (evidência objetiva acelera)

**Modelo Win-Win:**

- Auditoria 24h (paga e creditada no sprint)
- Pagamento 50/50 (kickoff/entrega)
- Aceite por métrica: p75 LCP<2.5s, INP<200ms, CLS<0.1 + 1 experimento A/B

---

## 🎯 **VERTICAIS PRIORITÁRIAS & ICPs**

### **Primary Targets (High-Intent + Performance Critical)**

1. **HVAC Multi-cidade (4-12 filiais)**

   - Decisor: owner-operator
   - Stack: WP/Elementor + Google Ads
   - Sinais: p75 LCP >2.8s, sem tel: above fold, LP ≠ anúncio

2. **Urgent Care/Clínicas Express (1-3 unidades)**

   - Decisor: ops/marketing lead
   - Sinais: INP alto por scripts, CLS de banners, CTA "find us now" fraca

3. **Clínicas Odontológicas (implantes/ortodontia)**

   - Decisor: practice manager
   - Sinais: imagens pesadas, INP >200ms, formulário sem feedback

4. **Estética/Dermato**

   - Decisor: owner/gestor marketing
   - Sinais: LCP alto por carrosséis, prova social fraca

5. **Imobiliária/Corretora Regional (10-40 corretores)**

   - Decisor: diretor comercial
   - Sinais: PLP/PDP lentas, CLS em galerias, GA4 inconsistente

6. **Auto Service (vidros/pneus/funilaria, 5-15 lojas)**

   - Decisor: COO/owner
   - Sinais: promessa "mesmo dia" sem click-to-call, CLS alto

7. **Veterinária/Pet Care (2-6 clínicas)**
   - Decisor: owner/gerente
   - Sinais: LCP mobile >2.5s, formulário frágil, CTA confusa

---

## 💼 **OFERTAS DE SERVIÇO (PRODUTIZADAS)**

### **A. CWV Rescue (2 semanas) - USD 700-1.200**

- **Entrega:** Remediação LCP/INP/CLS + Lighthouse CI + alertas
- **Aceite:** p75 LCP<2.5s, INP<200ms, CLS<0.1 + ≥90% URLs "Pass"

### **B. LP Experiment Pack (3 semanas) - USD 900-1.500**

- **Entrega:** 2-3 variações LP + GrowthBook/PostHog + readout CVR/CPA
- **Aceite:** 1 experimento lançado + readout estatístico + tracking validado

### **C. Tracking Reliability (add-on) - USD 400-600**

- **Entrega:** GA4→BigQuery + GTM-Server-Side + CAPI + data quality
- **Aceite:** Eventos críticos consistentes + relatórios sanidade (SQL)

---

## 🔍 **DISCOVERY ENGINE - SEARCHAPI INTEGRATION**

### **Lead Scoring Formula**

#### **DemandScore (0-4)**

```python
def calculate_demand_score(advertiser_data):
    score = 0
    if advertiser_data.last_seen <= 7:  # days
        score += 2
    if len(advertiser_data.creatives) >= 3:
        score += 1
    if advertiser_data.multi_network_geo:
        score += 1
    return score
```

#### **LeakScore (0-10)**

```python
def calculate_leak_score(performance_data, match_data, friction_data):
    # Performance (0-4)
    perf_score = 0
    if performance_data.lcp_p75 > 2.8: perf_score += 2
    if performance_data.inp_p75 > 200: perf_score += 1
    if performance_data.cls_p75 > 0.1: perf_score += 1

    # Message Match (0-3)
    match_score = 0
    if match_data.headline_similarity < 0.35: match_score += 2
    if match_data.cta_misaligned: match_score += 1

    # Friction (0-3)
    friction_score = 0
    if not friction_data.has_click_to_call: friction_score += 1
    if not friction_data.form_feedback: friction_score += 1
    if friction_data.broken_utm: friction_score += 1

    return perf_score + match_score + friction_score
```

#### **FitScore (0-3)**

```python
def calculate_fit_score(company_data):
    score = 0
    if company_data.currency in ['USD', 'EUR', 'GBP', 'CAD', 'AUD']: score += 1
    if company_data.vertical in PRIORITY_VERTICALS: score += 1
    if company_data.company_size in [10, 500]: score += 1  # SMB sweet spot
    return score
```

### **SearchAPI Workflow**

```python
# Orçamento: 5.000 créditos/mês
SEARCHAPI_BUDGET = {
    "serp_queries": 2300,      # engine=google
    "advertiser_info": 900,    # engine=google_ads_advertiser_info
    "transparency": 900,       # engine=google_ads_transparency_center
    "reserve": 900
}

# Operação: 250-350 créditos/dia → 8-12 leads qualificados
```

### **Discovery Process**

1. **SERP Collection**

   ```python
   queries = [
       "same-day {service} + {city}",
       "dental implants {city}",
       "urgent care {city}",
       # ... por vertical
   ]
   # engine=google → coletar ads.link + advertiser_info_token
   ```

2. **Advertiser Resolution**

   ```python
   # engine=google_ads_advertiser_info → nome/domínio/país
   # Filtrar apenas USD/EUR/GBP
   ```

3. **Recency Validation**

   ```python
   # engine=google_ads_transparency_center → last_seen ≤ 7 dias
   # Variety check: ≥3 criativos diferentes
   ```

4. **Performance Analysis**

   ```python
   # PSI + CrUX API nas 3-5 URLs de receita
   # p75 mobile: LCP/INP/CLS + diagnósticos
   ```

5. **Priority Calculation**
   ```python
   priority = demand_score + leak_score + fit_score
   # Atacar apenas ≥8 (ou ≥7 com last_seen ≤ 7 dias)
   ```

---

## 🏗️ **IMPLEMENTAÇÃO TÉCNICA**

### **Architecture Overview**

```
[Discovery Engine] → [Performance Analyzer] → [Leak Scorer] → [Outreach Generator]
      ↓                    ↓                     ↓                    ↓
[SearchAPI]         [PSI + CrUX APIs]      [Score Calculator]   [Message Templates]
[Transparency]      [Performance DB]       [Evidence Builder]   [Loom Generator]
```

### **Tech Stack**

```python
# APIs
- SearchAPI (discovery + transparency)
- PageSpeed Insights API
- Chrome UX Report (CrUX) API
- Meta Ad Library (scraping fallback)

# Storage
- PostgreSQL (prospects + performance history)
- Redis (API call cache)
- S3 (screenshots + evidence packages)

# Processing
- asyncio (concurrent API calls)
- aiohttp (HTTP client)
- Playwright (screenshot automation)
- pandas (scoring analysis)
```

### **Core Classes**

```python
@dataclass
class QualifiedProspect:
    # Company
    company_name: str
    domain: str
    vertical: str
    decision_maker: str

    # Evidence
    active_ads: List[AdCreative]
    performance_metrics: PerformanceData
    leak_indicators: List[LeakIndicator]

    # Scoring
    demand_score: int    # 0-4
    leak_score: int      # 0-10
    fit_score: int       # 0-3
    priority_score: int  # total

    # Business
    estimated_monthly_loss: int  # USD
    service_fit: str            # "CWV Rescue" | "LP Experiment" | "Tracking"
    deal_size_range: tuple      # (min, max) USD

    # Outreach
    pain_point_primary: str
    evidence_screenshot: str
    quick_wins: List[str]
    loom_script: str
```

### **Module Structure**

```
arco_v3/
├── discovery/
│   ├── searchapi_collector.py      # SearchAPI integration
│   ├── transparency_analyzer.py    # Ad recency + variety
│   └── domain_resolver.py          # Domain extraction + validation
├── performance/
│   ├── psi_analyzer.py            # PageSpeed Insights
│   ├── crux_analyzer.py           # Chrome UX Report
│   └── performance_scorer.py      # Leak calculation
├── scoring/
│   ├── demand_scorer.py           # Ad recency + variety scoring
│   ├── leak_scorer.py             # Performance + friction scoring
│   ├── fit_scorer.py              # Commercial fit scoring
│   └── priority_calculator.py     # Combined priority logic
├── outreach/
│   ├── message_generator.py       # Template-based messages
│   ├── evidence_packager.py       # Screenshots + reports
│   ├── loom_scripter.py          # Video script generation
│   └── followup_scheduler.py      # T+2, T+5 automation
└── validation/
    ├── vertical_validator.py      # ICP matching
    ├── currency_filter.py         # USD/EUR/GBP only
    └── size_filter.py             # SMB sweet spot
```

---

## 📝 **OUTREACH TEMPLATES**

### **HVAC (owner-operator)**

```
Subject: Your same-day LP is leaking calls — mobile LCP 3.6s

PSI for /same-day: p75 LCP 3.6s, INP 240ms; no tel: above the fold (screens).
Two fixes (image policy + font strategy) + tel: CTA aligned to "same-day".
Acceptance in 14 days: ≥90% URLs "Pass" + 1 A/B on headline; typical −15–30% CPA.
24-hour paid audit (USD 250), credited to the sprint. Loom attached.
```

### **Dental (practice manager)**

```
Subject: INP 260ms on your implants LP — clean A/B plan (GA4→BQ)

Field INP 260ms; heavy images; form without feedback (proof attached).
Media compression + font policy + form validation; A/B headline + proof (credentials/case).
Acceptance: CWV within thresholds + experiment readout in GA4→BQ (form submit/consultation).
24-hour audit (USD 250) → 2-week fix scope. Loom + one-pager attached.
```

### **Urgent Care (ops/marketing)**

```
Subject: INP is breaking "find us now" — 2-week INP-first fix

p75 INP 280ms; chat/pixels delaying tap; CLS from banners (screens).
Event prioritization, defer/idle, fixed "route/call" CTA; A/B "walk-in vs book now".
Acceptance: INP <200ms p75 + drop in abandonment on route/call funnel (RUM in GA4).
Audit in 24h (USD 250) credited. Loom + scope below.
```

---

## 📊 **KPIs & SUCCESS METRICS**

### **Discovery Metrics**

- **Active advertisers discovered**: >100/dia
- **Performance leaks identified**: >20/dia (score ≥7)
- **Priority prospects**: 8-12/dia (score ≥8)

### **Pipeline Metrics**

- **Outreach**: 8-12 abordagens/dia hiper-personalizadas
- **Response rate**: 12-20% (vs típico 5-8%)
- **Audit conversion**: 30-40% das respostas
- **Sprint conversion**: 50-70% das auditorias

### **Business Metrics**

- **Time to first deal**: ≤7 dias (2 auditorias + 1-2 sprints)
- **Average deal size**: $1,200-2,000 (CWV + LP + Tracking)
- **Monthly target**: $15K-25K revenue
- **Customer LTV**: 30%+ viram retainer (ongoing optimization)

---

## 🗓️ **ROADMAP DE IMPLEMENTAÇÃO**

### **Semana 1: Discovery Foundation**

- [ ] SearchAPI integration (SERP + Transparency)
- [ ] Domain extraction + deduplication
- [ ] Basic scoring (Demand + Fit)
- [ ] **Entrega**: 50+ prospects descobertos/dia

### **Semana 2: Performance Detection**

- [ ] PSI + CrUX API integration
- [ ] Leak scoring algorithm
- [ ] Evidence screenshot automation
- [ ] **Entrega**: Performance leaks identificados + evidências

### **Semana 3: Outreach Automation**

- [ ] Message template engine
- [ ] Loom script generation
- [ ] Evidence package assembly
- [ ] **Entrega**: Outreach 100% automatizado

### **Semana 4: Pipeline Optimization**

- [ ] Follow-up automation (T+2, T+5)
- [ ] Priority scoring refinement
- [ ] Dashboard + reporting
- [ ] **Entrega**: Sistema completo operacional

---

## 🛠️ **DELIVERABLES & ASSETS**

### **Required Assets**

- [ ] **One-pagers** (PDF por vertical) - escopo/aceite/preço
- [ ] **Loom templates** (60-75s) - "LCP em 3 passos", "A/B sem quebrar tracking"
- [ ] **Demo repo** - Next.js + RUM Web-Vitals + Lighthouse CI
- [ ] **Scoring spreadsheet** - Demand/Leak/Fit com pesos
- [ ] **Email templates** - T+0/T+2/T+5 sequences

### **Technical Deliverables**

- [ ] SearchAPI collector (fully functional)
- [ ] Performance analyzer (PSI + CrUX)
- [ ] Scoring engine (priority calculation)
- [ ] Outreach generator (evidence-based messages)
- [ ] Dashboard (pipeline tracking)

---

## 🚨 **RISKS & MITIGATIONS**

### **Technical Risks**

- **CrUX sampling insufficient**: Use origin-level for triage, page-level for final aceite
- **SearchAPI rate limits**: Implement smart caching + request batching
- **PSI quota exhaustion**: Batch requests + cache results for 24h

### **Business Risks**

- **Low response rates**: A/B test subject lines + evidence strength
- **Compliance issues**: Focus "low-friction" scope (images/fonts/cache)
- **Measurement disputes**: Validate GA4→BQ before making claims

### **Operational Risks**

- **Delivery dependency**: Create self-contained PRs + implementation checklists
- **Scope creep**: Fixed aceite criteria + change request process
- **Quality control**: Automated evidence validation + manual review

---

## 📋 **GO-LIVE CHECKLIST (7 DIAS)**

### **D0: Setup & Assets**

- [ ] SearchAPI keys + credit allocation
- [ ] One-pager finalization (all verticals)
- [ ] Loom recording (2 templates)
- [ ] Scoring spreadsheet validation

### **D1-D2: First Campaign**

- [ ] Run discovery queries (16-24 prospects)
- [ ] Performance analysis + evidence generation
- [ ] Send personalized outreach
- [ ] Schedule 1 audit call

### **D3: Delivery Start**

- [ ] Complete first 24h audit
- [ ] Close first sprint (CWV Rescue)
- [ ] Generate public case study (sanitized)

### **D4-D7: Scale & Optimize**

- [ ] Maintain 8-12 outreach/dia cadence
- [ ] Execute first sprint delivery
- [ ] Refine scoring based on response data
- [ ] Prepare month 2 expansion plan

---

## 🔗 **RELATED DOCUMENTATION**

- `BUSINESS_PROPOSAL.md` - Commercial terms & pricing strategy
- `AGENTS.md` - AI agent protocols & decision trees
- `SCORING_FORMULAS.md` - Detailed scoring algorithms
- `OUTREACH_PLAYBOOK.md` - Complete message templates & follow-up sequences
- `TECHNICAL_SPECS.md` - API integrations & architecture details

**Priority Score Formula**: `priority = demand_score + leak_score + fit_score` (Attack ≥8 only)

**Success Criteria**: 2 sprints closed in first 7 days + $15K-25K monthly revenue by month-end.
