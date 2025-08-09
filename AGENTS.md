# 🤖 ARCO V3: AI AGENTS & AUTOMATION PROTOCOLS

## 📋 **OVERVIEW**

Sistema de agentes inteligentes para automação completa do pipeline de geração de leads baseado em Performance & CRO. Cada agente tem responsabilidades específicas com protocolos de tomada de decisão bem definidos.

---

## 🔍 **DISCOVERY AGENT**

### **Responsabilidades**

- Executar queries SearchAPI por vertical
- Filtrar anunciantes ativos (≤7 dias)
- Validar domínios e currency (USD/EUR/GBP)
- Calcular Demand Score e Fit Score

### **Decision Tree**

```python
def discovery_decision_flow():
    advertisers = searchapi.get_active_advertisers()

    for ad in advertisers:
        # Gate 1: Currency Filter
        if ad.currency not in ['USD', 'EUR', 'GBP', 'CAD', 'AUD']:
            continue

        # Gate 2: Recency Check
        if ad.last_seen > 7:  # days
            continue

        # Gate 3: Vertical Match
        if not matches_priority_vertical(ad.landing_page):
            continue

        # Gate 4: Spend Indicator
        if len(ad.creatives) < 2:  # Low variety = low spend
            continue

        yield QualifiedAdvertiser(ad)
```

### **Output Protocols**

```python
@dataclass
class DiscoveryOutput:
    advertiser_id: str
    domain: str
    vertical: str
    currency: str
    last_seen: int
    creative_count: int
    demand_score: int  # 0-4
    fit_score: int     # 0-3
    discovery_timestamp: datetime
```

---

## 🚀 **PERFORMANCE AGENT**

### **Responsabilidades**

- Análise PageSpeed Insights (móvel + desktop)
- Coleta Chrome UX Report (p75 Core Web Vitals)
- Screenshot automation para evidências
- Cálculo de Leak Score

### **Decision Tree**

```python
def performance_analysis_flow(domain):
    # Gate 1: URL Strategy
    critical_urls = extract_revenue_urls(domain)
    if len(critical_urls) == 0:
        critical_urls = [f"{domain}/", f"{domain}/contact"]

    leak_indicators = []

    for url in critical_urls:
        # Gate 2: Performance Check
        psi_data = pagespeed_insights.analyze(url, device='mobile')
        crux_data = chrome_ux_report.get_metrics(url)

        # Gate 3: Leak Detection
        if psi_data.lcp_p75 > 2.8:
            leak_indicators.append("LCP_HIGH")
        if psi_data.inp_p75 > 200:
            leak_indicators.append("INP_HIGH")
        if psi_data.cls_p75 > 0.1:
            leak_indicators.append("CLS_HIGH")

        # Gate 4: Friction Analysis
        if not has_click_to_call(url):
            leak_indicators.append("NO_PHONE_CTA")
        if not has_form_validation(url):
            leak_indicators.append("WEAK_FORM")

    return calculate_leak_score(leak_indicators)
```

### **Output Protocols**

```python
@dataclass
class PerformanceOutput:
    domain: str
    analyzed_urls: List[str]
    performance_metrics: Dict[str, PSIMetrics]
    leak_indicators: List[str]
    leak_score: int  # 0-10
    evidence_screenshots: List[str]
    priority_fixes: List[str]
    estimated_impact: str  # "15-25% CVR improvement"
```

---

## 🎯 **SCORING AGENT**

### **Responsabilidades**

- Combinar scores de Discovery, Performance e Fit
- Calcular Priority Score final
- Determinar service fit (CWV/LP/Tracking)
- Estimar deal size e monthly loss

### **Decision Tree**

```python
def scoring_decision_flow(discovery_output, performance_output):
    total_score = (
        discovery_output.demand_score +
        discovery_output.fit_score +
        performance_output.leak_score
    )

    # Gate 1: Priority Threshold
    if total_score < 8:
        return None  # Skip outreach

    # Gate 2: Service Fit Logic
    if performance_output.leak_score >= 6:
        if "LCP_HIGH" in performance_output.leak_indicators:
            service_fit = "CWV_RESCUE"
            deal_size = (700, 1200)
        elif len(performance_output.leak_indicators) >= 3:
            service_fit = "LP_EXPERIMENT"
            deal_size = (900, 1500)
    else:
        service_fit = "TRACKING_RELIABILITY"
        deal_size = (400, 600)

    # Gate 3: Loss Estimation
    monthly_loss = estimate_revenue_leak(
        performance_output.leak_indicators,
        discovery_output.creative_count
    )

    return ScoredProspect(
        priority_score=total_score,
        service_fit=service_fit,
        deal_size_range=deal_size,
        estimated_monthly_loss=monthly_loss
    )
```

---

## 📧 **OUTREACH AGENT**

### **Responsabilidades**

- Geração de mensagens personalizadas por vertical
- Criação de evidências visuais (screenshots + annotations)
- Scripts para Loom videos
- Scheduling follow-ups

### **Decision Tree**

```python
def outreach_message_flow(scored_prospect):
    # Gate 1: Vertical Template Selection
    vertical = scored_prospect.vertical
    template = VERTICAL_TEMPLATES[vertical]

    # Gate 2: Pain Point Prioritization
    primary_pain = prioritize_pain_points(
        scored_prospect.leak_indicators
    )

    # Gate 3: Evidence Selection
    evidence_type = select_evidence_type(primary_pain)
    if evidence_type == "SCREENSHOT_ANNOTATED":
        evidence_url = generate_annotated_screenshot(
            scored_prospect.domain, primary_pain
        )
    elif evidence_type == "PERFORMANCE_REPORT":
        evidence_url = generate_psi_report(scored_prospect.domain)

    # Gate 4: Message Personalization
    message = template.render(
        company_name=scored_prospect.company_name,
        primary_pain=primary_pain,
        evidence_url=evidence_url,
        estimated_impact=scored_prospect.estimated_impact,
        service_fit=scored_prospect.service_fit
    )

    return OutreachMessage(
        message=message,
        evidence_package=evidence_url,
        follow_up_sequence=FOLLOW_UP_SEQUENCES[vertical]
    )
```

### **Vertical Templates**

#### **HVAC Template**

```python
HVAC_TEMPLATE = """
Subject: Your same-day LP is leaking calls — mobile LCP {lcp_score}s

Hey {decision_maker},

Found your "{service}" ads on Google — great targeting for {city}.

Issue: PSI shows {lcp_score}s LCP on mobile (p75). That's ~{lost_calls} lost calls/month when users bounce before your "same-day" promise loads.

Quick fix scope:
• Image optimization ({image_savings}KB savings)
• Font loading strategy
• Above-fold phone CTA (currently buried)

Acceptance: ≥90% URLs pass CWV + A/B test on headline
Typical result: 15-30% CPA reduction

24h audit (USD 250, credited to sprint): {calendar_link}
Evidence + one-pager: {evidence_url}

Best,
{sender_name}
"""
```

#### **Dental Template**

```python
DENTAL_TEMPLATE = """
Subject: INP {inp_score}ms on your implants LP — clean A/B plan

Hi {decision_maker},

Saw your implant ads — smart geo-targeting for {city}.

Performance issue: Field INP {inp_score}ms (p75). Heavy images + no form feedback = user frustration on mobile.

2-week scope:
• Media compression strategy
• Form validation + progress feedback
• A/B test: credentials vs. case studies above fold

Acceptance: CWV within Google thresholds + experiment readout in GA4
ROI: Typical 10-25% CVR lift on consultation forms

24h audit (USD 250 → credited): {calendar_link}
Proof + fix plan: {evidence_url}

{sender_name}
"""
```

---

## 🔄 **FOLLOW-UP AGENT**

### **Responsabilidades**

- T+2 follow-up automation
- T+5 value-add follow-up
- Objection handling sequences
- Audit call scheduling

### **Decision Tree**

```python
def followup_decision_flow(outreach_record):
    days_since_send = (datetime.now() - outreach_record.sent_at).days

    # Gate 1: Response Check
    if outreach_record.responded:
        return schedule_audit_call(outreach_record)

    # Gate 2: Follow-up Timing
    if days_since_send == 2:
        return generate_t2_followup(outreach_record)
    elif days_since_send == 5:
        return generate_t5_followup(outreach_record)
    elif days_since_send >= 14:
        return mark_closed_lost(outreach_record)

def generate_t2_followup(record):
    return f"""
    Quick follow-up on the {record.primary_pain} analysis.

    Added one more insight: {additional_insight}

    Still offering the 24h audit (credited to sprint) if the timing works.

    {calendar_link}
    """

def generate_t5_followup(record):
    return f"""
    Last note on this — sharing a case study from {similar_vertical}.

    Similar issue ({record.primary_pain}) → {case_study_result}

    If Q4 performance is a priority, happy to run the audit.
    Otherwise, keeping this for reference.

    {case_study_link}
    """
```

---

## 📊 **ANALYTICS AGENT**

### **Responsabilidades**

- Tracking de pipeline metrics
- Response rate analysis
- Score calibration
- ROI reporting

### **Decision Tree**

```python
def analytics_decision_flow():
    # Daily reporting
    pipeline_metrics = calculate_daily_metrics()

    # Gate 1: Response Rate Analysis
    if pipeline_metrics.response_rate < 0.12:  # Below 12%
        trigger_message_optimization()

    # Gate 2: Conversion Analysis
    if pipeline_metrics.audit_conversion < 0.30:  # Below 30%
        trigger_qualification_tightening()

    # Gate 3: Score Calibration
    if len(pipeline_metrics.closed_won) >= 10:
        recalibrate_scoring_weights()

    return AnalyticsReport(
        daily_metrics=pipeline_metrics,
        optimization_recommendations=get_recommendations(),
        score_calibration_status=get_calibration_status()
    )
```

---

## 🛠️ **OPERATIONAL PROTOCOLS**

### **Daily Automation Flow**

```python
def daily_automation_pipeline():
    # 06:00 - Discovery Phase
    discovered_advertisers = discovery_agent.run_daily_queries()

    # 07:00 - Performance Analysis
    performance_results = []
    for advertiser in discovered_advertisers:
        result = performance_agent.analyze(advertiser.domain)
        performance_results.append(result)

    # 08:00 - Scoring & Prioritization
    scored_prospects = []
    for i, discovery in enumerate(discovered_advertisers):
        score = scoring_agent.calculate_priority(
            discovery, performance_results[i]
        )
        if score and score.priority_score >= 8:
            scored_prospects.append(score)

    # 09:00 - Outreach Generation
    for prospect in scored_prospects:
        message = outreach_agent.generate_message(prospect)
        send_email(message)
        schedule_followups(prospect)

    # 18:00 - Analytics & Optimization
    analytics_agent.generate_daily_report()
```

### **Error Handling Protocols**

```python
def error_handling_flow(error_type, context):
    if error_type == "SEARCHAPI_QUOTA_EXCEEDED":
        switch_to_backup_discovery_mode()
        alert_human_operator("SearchAPI quota exceeded")

    elif error_type == "PSI_RATE_LIMIT":
        implement_exponential_backoff()
        queue_analysis_for_retry()

    elif error_type == "DOMAIN_UNREACHABLE":
        mark_prospect_invalid()
        log_domain_issue(context.domain)

    elif error_type == "SCORING_ANOMALY":
        flag_for_manual_review()
        continue_with_conservative_score()
```

### **Quality Assurance Protocols**

```python
def quality_assurance_checks():
    # Check 1: Message Quality
    for message in daily_outreach:
        if message.personalization_score < 0.7:
            flag_for_human_review(message)

    # Check 2: Evidence Accuracy
    for evidence in daily_evidence:
        if not validate_screenshot_accuracy(evidence):
            regenerate_evidence(evidence.prospect_id)

    # Check 3: Score Consistency
    score_distribution = analyze_daily_scores()
    if score_distribution.std_dev > 2.0:
        trigger_score_calibration()
```

---

## 🚨 **ESCALATION PROCEDURES**

### **Human Intervention Triggers**

- Response rate drops below 8% for 3 consecutive days
- Audit conversion rate drops below 20%
- Technical errors persist for >2 hours
- Prospect complaints or compliance issues

### **Manual Override Protocols**

- Scoring agent decisions can be overridden with manual priority flags
- Message templates can be A/B tested with manual variants
- Evidence generation can be supplemented with custom screenshots
- Follow-up timing can be adjusted based on vertical-specific data

---

## 📈 **CONTINUOUS IMPROVEMENT**

### **Weekly Optimization Cycle**

1. **Monday**: Analyze previous week's response rates by vertical
2. **Tuesday**: Update message templates based on performance data
3. **Wednesday**: Recalibrate scoring weights if sample size >50
4. **Thursday**: Review evidence quality and regenerate low-performers
5. **Friday**: Plan next week's target verticals and query expansion

### **Monthly Strategic Review**

- Vertical performance analysis (which ICPs convert best)
- Service fit accuracy (are we recommending the right solutions)
- Deal size optimization (pricing strategy refinement)
- Geographic expansion opportunities (new cities/regions)

**Agent Success Metrics**: 8-12 personalized outreach/dia, 12-20% response rate, 30-40% audit conversion, $15K-25K monthly revenue.
