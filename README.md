# 🎯 ARCO ENGINE V3: Agent-Based Lead Generation System

**Automated B2B lead generation and hyper-personalized outreach using AI agents**

## 🚀 **Quick Start**

```bash
# Install dependencies
pip install -r requirements.txt

# Validate configuration
python arco_v3.py validate

# Run daily batch processing
python arco_v3.py batch --max-credits 50 --target-prospects 10

# Test with mock data
python arco_v3.py test --mock
```

## 📋 **What This Does**

ARCO V3 identifies B2B companies with:

- **Active Google Ads spending** (last 7 days)
- **Performance leaks** (slow Core Web Vitals, poor UX)
- **Revenue impact** (quantified lost conversions)

**Output**: Prioritized prospects with evidence-based outreach messages

## 🎯 **Target Verticals**

1. **HVAC Multi-location** (4-12 branches)
2. **Urgent Care/Express Clinics** (1-3 units)
3. **Dental Clinics** (implants/orthodontics)
4. **Medical Aesthetics/Dermatology**
5. **Real Estate Brokerages** (10-40 agents)
6. **Auto Services** (glass/tires/body shops, 5-15 locations)
7. **Veterinary/Pet Care** (2-6 clinics)

## 💼 **Service Offerings**

- **CWV Rescue** (2 weeks): $700-1,200 USD
- **LP Experiment Pack** (3 weeks): $900-1,500 USD
- **Tracking Reliability** (add-on): $400-600 USD

## 📊 **Expected Performance**

- **Discovery**: 8-12 priority prospects/day
- **Response Rate**: 12-20% (vs typical 5-8%)
- **Time to Close**: <21 days
- **Monthly Revenue Target**: $15K-25K

## 🔧 **Agent Architecture**

### 🔍 **Discovery Agent**
- SearchAPI integration (SERP + Transparency Center)
- Active advertiser filtering (≤7 days)
- Currency validation (USD/EUR/GBP/CAD/AUD)
- Demand & Fit scoring

### 🚀 **Performance Agent**
- PageSpeed Insights analysis (mobile + desktop)
- Chrome UX Report (p75 Core Web Vitals)
- Evidence screenshot automation
- Leak score calculation

### 🎯 **Scoring Agent**
- Combined priority scoring
- Service fit determination (CWV/LP/Tracking)
- Deal size estimation
- Monthly loss calculation

### 📧 **Outreach Agent**
- Personalized message generation by vertical
- Evidence package creation
- Follow-up sequence planning
- Hyper-personalization with real data

### 📊 **Analytics Agent**
- Pipeline metrics tracking
- Response rate analysis
- Score calibration
- ROI reporting

## 📁 **Project Structure**

```
arco-find/
├── arco_v3.py                             # Main CLI interface
├── src/
│   ├── agents/                            # Agent implementations
│   │   ├── discovery_agent.py            # SearchAPI + filtering
│   │   ├── performance_agent.py          # PSI + performance analysis
│   │   ├── scoring_agent.py              # Priority scoring
│   │   ├── outreach_agent.py             # Message generation
│   │   ├── followup_agent.py             # Follow-up automation
│   │   └── analytics_agent.py            # Metrics & optimization
│   ├── models/
│   │   └── core_models.py                # Data structures
│   └── arco_pipeline.py                  # Pipeline orchestrator
├── config/
│   ├── api_keys.py                       # API credentials
│   └── discovery_config.json             # Discovery settings
├── data/
│   └── executions/                       # Batch processing results
├── docs/                                 # Technical documentation
├── AGENTS.md                             # AI automation protocols
└── legacy/
    └── arco_s_tier_merged.py             # Legacy monolithic script
```

## 🔑 **Configuration**

### Required API Keys:

```python
# config/api_keys.py
SEARCHAPI_KEY = "your_searchapi_key_here"
GOOGLE_PSI_KEY = "your_pagespeed_insights_key"  # Optional
```

### SearchAPI Budget:

- **Monthly Limit**: 5,000 credits
- **Daily Usage**: 250-350 credits
- **Per Lead**: ~25-30 credits average

## 📈 **Scoring System**

### Priority Formula:

```python
priority_score = demand_score + leak_score + fit_score
# Attack threshold: ≥8 points
```

### Score Components:

- **Demand Score** (0-4): Ad recency + variety + geo-targeting
- **Leak Score** (0-10): Core Web Vitals + UX friction + message mismatch
- **Fit Score** (0-3): Currency + vertical + company size

## 🎯 **Sample Output**

```json
{
  "company_name": "Express Dental Care",
  "domain": "expressdentalcare.com",
  "vertical": "dental_clinics",
  "priority_score": 9,
  "estimated_monthly_loss": 1850,
  "primary_pain_point": "INP 280ms mobile - form abandonment",
  "service_recommendation": "CWV_RESCUE",
  "evidence_url": "screenshots/expressdentalcare_performance.png"
}
```

## 📧 **Outreach Examples**

### HVAC Template:

```
Subject: Your same-day LP is leaking calls — mobile LCP 3.6s

Hey Mike,

Found your "Emergency HVAC" ads on Google — great targeting for Tampa.

Issue: PSI shows 3.6s LCP on mobile (p75). That's ~12 lost calls/month 
when users bounce before your "same-day" promise loads.

Quick fix scope:
• Image optimization (150KB savings)
• Font loading strategy
• Above-fold phone CTA (currently buried)

Acceptance: ≥90% URLs pass CWV + A/B test on headline
Typical result: 15-30% CPA reduction

24h audit (USD 250, credited to sprint): [calendar]
Evidence + one-pager: [evidence_url]

Best,
Alex
```

### Dental Template:

```
Subject: INP 280ms on your implants LP — clean A/B plan

Hi Dr. Smith,

Saw your implant ads — smart geo-targeting for Miami.

Performance issue: Field INP 280ms (p75). Heavy images + no form 
feedback = user frustration on mobile.

2-week scope:
• Media compression strategy
• Form validation + progress feedback
• A/B test: credentials vs. case studies above fold

Acceptance: CWV within Google thresholds + experiment readout in GA4
ROI: Typical 10-25% CVR lift on consultation forms

24h audit (USD 250 → credited): [calendar]
Proof + fix plan: [evidence_url]

Alex
```

## 🚨 **Important Notes**

### API Limitations:

- SearchAPI: 5,000 credits/month
- PSI: 25,000 queries/day (free tier)
- CrUX: 150 queries/minute

### Compliance:

- Focuses on "low-friction" technical optimizations
- Evidence-based claims only (no promises without data)
- 24h audit credited to sprint (risk-free trial)

## 📚 **Documentation**

- **[ARCO_V3_PERFORMANCE_LEAD_GENERATION.md](ARCO_V3_PERFORMANCE_LEAD_GENERATION.md)**: Complete business specification
- **[AGENTS.md](AGENTS.md)**: AI automation protocols and decision trees
- **[GIT_ISSUE_ARCO_V3_STIER.md](GIT_ISSUE_ARCO_V3_STIER.md)**: Production deployment roadmap

## 🔗 **Quick Links**

- **SearchAPI Documentation**: https://searchapi.io/docs
- **PageSpeed Insights API**: https://developers.google.com/speed/docs/insights/v5/get-started
- **Chrome UX Report**: https://developers.google.com/web/tools/chrome-user-experience-report

## 🤖 **Agent Automation**

### **Daily Automation Flow**

```
06:00 - Discovery Phase    → SearchAPI queries by vertical
07:00 - Performance Phase  → PSI + CrUX analysis  
08:00 - Scoring Phase      → Priority calculation + service fit
09:00 - Outreach Phase     → Personalized message generation
18:00 - Analytics Phase    → Pipeline metrics + optimization
```

### **Expected Performance**

- **Discovery**: 8-12 qualified prospects/day
- **Response Rate**: 12-20% (vs industry 5-8%)
- **Qualification Rate**: >15% (vs previous 2.3%)
- **Pipeline Velocity**: <21 days to close

---

**Success Criteria**: 12-20% response rate + $15K-25K monthly revenue

**Support**: Run `python arco_v3.py --help` or see [AGENTS.md](AGENTS.md)
