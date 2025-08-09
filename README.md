# 🎯 ARCO ENGINE V3: Performance-Driven Lead Generation

**Evidence-based B2B lead generation system targeting performance optimization opportunities**

## 🚀 **Quick Start**

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp config/api_keys.py.example config/api_keys.py
# Edit config/api_keys.py with your SearchAPI key

# Run the discovery engine
python arco_engine_definitivo_calibrado.py
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

## 🔧 **Core Components**

### `arco_engine_definitivo_calibrado.py`

Production-ready discovery engine with:

- SearchAPI integration (SERP + Transparency Center)
- PageSpeed Insights + Chrome UX Report analysis
- Evidence-based scoring (Demand + Leak + Fit)
- Personalized outreach generation

### Key Classes:

- `CalibratedSearchAPI`: Multi-engine query optimization
- `CalibratedWasteAnalyzer`: Performance leak detection
- `LeakScoreCalculator`: Priority scoring algorithm

## 📁 **Project Structure**

```
arco-find/
├── arco_engine_definitivo_calibrado.py    # Main discovery engine
├── config/
│   ├── api_keys.py                        # API credentials
│   └── __init__.py
├── src/                                   # Core modules
├── data/                                  # Discovery results
├── exports/                               # Pipeline outputs
├── logs/                                  # Execution logs
├── docs/                                  # Technical documentation
├── ARCO_V3_PERFORMANCE_LEAD_GENERATION.md # Complete specification
├── AGENTS.md                              # AI automation protocols
└── GIT_ISSUE_ARCO_V3_STIER.md            # Production roadmap
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

PSI shows 3.6s LCP on mobile (p75). That's ~12 lost calls/month
when users bounce before your "same-day" promise loads.

Quick fix: image optimization + above-fold phone CTA
Acceptance: ≥90% URLs pass CWV + A/B test
Typical result: 15-30% CPA reduction

24h audit (USD 250, credited to sprint): [calendar]
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

---

**Success Criteria**: 2 sprints closed in first 7 days + $15K-25K monthly revenue by month-end.

**Support**: See documentation files or run `python arco_engine_definitivo_calibrado.py --help`
