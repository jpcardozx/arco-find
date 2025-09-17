# Design Document

## Overview

This design extends the existing /arco pipeline architecture to integrate real marketing data from Google Analytics and Google Ads APIs. The solution enhances the current leak detection engine with industry-benchmarked marketing waste analysis while maintaining compatibility with existing models, engines, and integrations.

The implementation follows the established /arco patterns:

- Extends existing models in /arco/models with marketing data fields
- Enhances /arco/engines/leak_engine.py with real marketing leak detection
- Adds new integrations in /arco/integrations following existing API client patterns
- Maintains compatibility with current /arco/pipelines and CRM integration

## Architecture

### Current /arco Architecture Integration

```
/arco/
├── models/
│   ├── prospect.py (EXTEND: add marketing_data field)
│   ├── qualified_prospect.py (EXTEND: add MarketingLeak type)
│   └── leak_result.py (EXTEND: marketing leak categories)
├── engines/
│   └── leak_engine.py (ENHANCE: add marketing leak detection)
├── integrations/
│   ├── google_analytics.py (NEW: GA4 API client)
│   ├── google_ads.py (NEW: Google Ads API client)
│   └── base.py (EXTEND: marketing data interface)
└── config/
    └── marketing_benchmarks.yml (NEW: industry benchmarks)
```

### Data Flow Enhancement

```
Existing Flow:
Prospect → LeakEngine → LeakResult → QualifiedProspect → CRM

Enhanced Two-Phase Flow:

Phase 1 - Rapid Scoring & Prioritization:
Prospect Batch → PriorityEngine → ScoredProspects → Top 10% Selection

Phase 2 - Deep Enrichment & Outreach:
Top 10% Leads → MarketingEnricher → EnhancedProspects →
LeakEngine (full analysis) → DetailedLeakResults →
OutreachGenerator → PersonalizedOutreach → CRM
```

## Components and Interfaces

### 1. Enhanced Prospect Model

Extends existing /arco/models/prospect.py:

```python
@dataclass
class MarketingData:
    """Marketing performance data for a prospect."""
    web_vitals: Optional[Dict[str, float]] = None
    conversion_metrics: Optional[Dict[str, float]] = None
    ad_spend_data: Optional[Dict[str, Any]] = None
    traffic_sources: Optional[Dict[str, float]] = None
    data_confidence: float = 0.0
    collection_date: datetime = field(default_factory=datetime.now)

# Extend existing Prospect class
@dataclass
class Prospect:
    # ... existing fields ...
    marketing_data: Optional[MarketingData] = None
```

### 2. Marketing Leak Types

Extends existing /arco/models/qualified_prospect.py:

```python
@dataclass
class MarketingLeak(Leak):
    """Marketing-specific leak information."""
    industry_benchmark: Optional[float] = None
    current_metric: Optional[float] = None
    improvement_potential: Optional[str] = None
    technical_recommendation: Optional[str] = None
```

### 3. Google Analytics Integration

New /arco/integrations/google_analytics.py following existing patterns:

```python
class GoogleAnalyticsIntegration(APIClientInterface):
    """Google Analytics 4 API integration."""

    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path
        self.client = None

    async def get_web_vitals(self, domain: str) -> Dict[str, float]:
        """Get Core Web Vitals for domain."""

    async def get_conversion_metrics(self, domain: str) -> Dict[str, float]:
        """Get conversion and engagement metrics."""

    async def get_traffic_sources(self, domain: str) -> Dict[str, float]:
        """Get traffic source breakdown."""
```

### 4. Google Ads Integration

New /arco/integrations/google_ads.py:

```python
class GoogleAdsIntegration(APIClientInterface):
    """Google Ads API integration."""

    async def get_campaign_metrics(self, domain: str) -> Dict[str, Any]:
        """Get campaign performance metrics."""

    async def get_keyword_performance(self, domain: str) -> List[Dict]:
        """Get keyword-level performance data."""
```

### 5. Priority Scoring Engine

New /arco/engines/priority_engine.py for rapid lead scoring:

```python
@dataclass
class PriorityScore:
    """Priority scoring result for a prospect."""
    total_score: float
    company_size_score: float
    revenue_potential_score: float
    technology_maturity_score: float
    growth_indicators_score: float
    contact_accessibility_score: float
    confidence_level: float
    priority_tier: str  # "HIGH", "MEDIUM", "LOW"

class PriorityEngine:
    """Rapid lead scoring and prioritization engine."""

    def __init__(self, config_path: str = "config/production.yml"):
        self.config = self._load_config(config_path)
        self.scoring_weights = self._load_scoring_weights()

    async def score_batch(self, prospects: List[Prospect]) -> List[Tuple[Prospect, PriorityScore]]:
        """Score a batch of prospects and return sorted by priority."""
        scored_prospects = []

        for prospect in prospects:
            score = await self._calculate_priority_score(prospect)
            scored_prospects.append((prospect, score))

        # Sort by total score descending
        scored_prospects.sort(key=lambda x: x[1].total_score, reverse=True)
        return scored_prospects

    def get_top_percentage(self, scored_prospects: List[Tuple[Prospect, PriorityScore]],
                          percentage: float = 0.1) -> List[Tuple[Prospect, PriorityScore]]:
        """Get top percentage of prospects (default 10%)."""
        count = max(1, int(len(scored_prospects) * percentage))
        return scored_prospects[:count]
```

### 6. Enhanced Leak Engine

Extends existing /arco/engines/leak_engine.py:

```python
class LeakEngine(LeakEngineInterface):
    def __init__(self, config_path: str = "config/production.yml"):
        # ... existing initialization ...
        self.ga_client = GoogleAnalyticsIntegration(config.get('ga_credentials'))
        self.ads_client = GoogleAdsIntegration(config.get('ads_credentials'))
        self.marketing_benchmarks = self._load_marketing_benchmarks()

    async def analyze(self, prospect: Prospect) -> LeakResult:
        # ... existing SaaS leak detection ...

        # NEW: Marketing leak detection
        marketing_leaks = await self._detect_marketing_leaks(prospect)

        # Combine with existing leaks
        all_leaks = saas_leaks + shopify_leaks + perf_leaks + marketing_leaks

    async def _detect_marketing_leaks(self, prospect: Prospect) -> List[MarketingLeak]:
        """Detect marketing inefficiencies using real data."""
        leaks = []

        if not prospect.marketing_data:
            return leaks

        # Performance affecting conversion
        perf_leaks = self._analyze_performance_impact(prospect)
        leaks.extend(perf_leaks)

        # Ad spend efficiency
        ad_leaks = self._analyze_ad_efficiency(prospect)
        leaks.extend(ad_leaks)

        return leaks
```

### 7. Outreach Generator

New /arco/engines/outreach_engine.py for personalized messaging:

```python
@dataclass
class OutreachContent:
    """Generated outreach content for a prospect."""
    subject_line: str
    opening_hook: str
    value_proposition: str
    specific_insights: List[str]
    call_to_action: str
    decision_maker_context: Optional[str] = None
    technical_talking_points: List[str] = field(default_factory=list)

class OutreachEngine:
    """Generate personalized outreach content based on prospect analysis."""

    def __init__(self, config_path: str = "config/production.yml"):
        self.config = self._load_config(config_path)
        self.templates = self._load_outreach_templates()

    async def generate_outreach(self, prospect: Prospect,
                               leak_result: LeakResult,
                               priority_score: PriorityScore) -> OutreachContent:
        """Generate personalized outreach content."""

        # Analyze prospect context
        industry_context = self._get_industry_context(prospect)
        pain_points = self._extract_pain_points(leak_result)
        roi_potential = self._calculate_roi_messaging(leak_result)

        # Generate content components
        subject = self._generate_subject_line(prospect, pain_points)
        hook = self._generate_opening_hook(prospect, priority_score)
        value_prop = self._generate_value_proposition(prospect, roi_potential)
        insights = self._generate_specific_insights(leak_result)
        cta = self._generate_call_to_action(prospect, industry_context)

        return OutreachContent(
            subject_line=subject,
            opening_hook=hook,
            value_proposition=value_prop,
            specific_insights=insights,
            call_to_action=cta,
            decision_maker_context=self._get_decision_maker_context(prospect),
            technical_talking_points=self._get_technical_talking_points(leak_result)
        )
```

## Data Models

### Marketing Benchmarks Configuration

New /arco/config/marketing_benchmarks.yml:

```yaml
industries:
  ecommerce:
    avg_cpc: 1.16
    avg_conversion_rate: 0.0268
    avg_bounce_rate: 0.47
    web_vitals_thresholds:
      lcp_good: 2.5
      fid_good: 100
      cls_good: 0.1

  saas:
    avg_cpc: 3.80
    avg_conversion_rate: 0.0363
    avg_bounce_rate: 0.42
    web_vitals_thresholds:
      lcp_good: 2.5
      fid_good: 100
      cls_good: 0.1

performance_impact:
  lcp_delay_conversion_loss: 0.07 # 7% per second
  bounce_rate_threshold: 0.60
  session_duration_minimum: 120 # seconds
```

### Industry-Specific Qualification Criteria

Extends existing /arco/config/production.yml:

```yaml
qualification_criteria:
  ecommerce:
    min_employee_count: 5
    min_revenue: 250000
    max_revenue: 50000000
    min_icp_score: 55.0
    min_roi_percentage: 20.0
    required_technologies: ["Shopify", "WooCommerce", "Magento"]

  saas:
    min_employee_count: 15
    min_revenue: 1000000
    max_revenue: 100000000
    min_icp_score: 65.0
    min_roi_percentage: 18.0
    required_technologies: ["AWS", "Google Cloud", "Azure"]
```

## Error Handling

### API Failure Patterns

Following existing /arco/engines patterns:

```python
async def _enrich_marketing_data(self, prospect: Prospect) -> MarketingData:
    """Enrich prospect with marketing data using fallback patterns."""
    marketing_data = MarketingData()

    try:
        # Primary: Google Analytics
        ga_data = await self.ga_client.get_web_vitals(prospect.domain)
        marketing_data.web_vitals = ga_data
        marketing_data.data_confidence += 0.4
    except Exception as e:
        logger.warning(f"GA enrichment failed for {prospect.domain}: {e}")
        # Fallback: Use PageSpeed Insights (existing integration)
        try:
            psi_data = await self.pagespeed_client.analyze(prospect.domain)
            marketing_data.web_vitals = self._extract_vitals_from_psi(psi_data)
            marketing_data.data_confidence += 0.2
        except Exception as e2:
            logger.warning(f"PSI fallback failed for {prospect.domain}: {e2}")

    # Continue with other data sources...
    return marketing_data
```

### Robust Technology Detection Fix

Enhances existing Wappalyzer integration:

```python
async def _enrich_technologies(self, prospect: Prospect) -> Dict[str, Any]:
    """Enhanced technology detection with robust fallbacks."""
    try:
        # Fix existing Wappalyzer coroutine issue
        tech_data = await asyncio.wait_for(
            self.wappalyzer.analyze_url(prospect.website),
            timeout=5.0
        )
        return self._process_wappalyzer_results(tech_data)

    except asyncio.TimeoutError:
        logger.warning(f"Wappalyzer timeout for {prospect.domain}, using HTTP fallback")
        return await self._analyze_http_headers(prospect.domain)

    except Exception as e:
        logger.warning(f"Wappalyzer failed for {prospect.domain}: {e}, using DNS fallback")
        return await self._analyze_dns_records(prospect.domain)
```

## Testing Strategy

### Unit Tests

Extends existing test patterns in /tests/:

```python
# /tests/integrations/test_google_analytics.py
class TestGoogleAnalyticsIntegration:
    async def test_web_vitals_collection(self):
        """Test web vitals data collection."""

    async def test_api_failure_handling(self):
        """Test graceful API failure handling."""

# /tests/engines/test_enhanced_leak_engine.py
class TestEnhancedLeakEngine:
    async def test_marketing_leak_detection(self):
        """Test marketing leak detection with real data."""

    async def test_industry_specific_benchmarks(self):
        """Test industry-specific benchmark application."""
```

### Integration Tests

```python
# /tests/pipelines/test_marketing_integration.py
class TestMarketingIntegration:
    async def test_end_to_end_marketing_enrichment(self):
        """Test complete marketing data enrichment flow."""

    async def test_crm_integration_with_marketing_data(self):
        """Test CRM receives marketing insights."""
```

### Performance Tests

```python
# /tests/performance/test_marketing_performance.py
class TestMarketingPerformance:
    async def test_api_rate_limiting(self):
        """Test API rate limit handling."""

    async def test_concurrent_enrichment(self):
        """Test concurrent marketing data collection."""
```

## Implementation Phases

### Phase 1: Core Infrastructure

- Extend Prospect model with marketing_data field
- Add MarketingLeak type to qualified_prospect.py
- Create base marketing integration interfaces
- Add marketing benchmarks configuration

### Phase 2: Google Analytics Integration

- Implement GoogleAnalyticsIntegration class
- Add web vitals collection
- Add conversion metrics collection
- Implement fallback to PageSpeed Insights

### Phase 3: Google Ads Integration

- Implement GoogleAdsIntegration class
- Add campaign metrics collection
- Add keyword performance analysis
- Implement rate limiting and error handling

### Phase 4: Enhanced Leak Detection

- Extend LeakEngine with marketing leak detection
- Implement performance impact calculations
- Add ad efficiency analysis
- Integrate industry benchmarks

### Phase 5: Industry-Specific Qualification

- Add industry-specific criteria configuration
- Update qualification logic in LeakEngine
- Implement technology requirement validation
- Add industry-based fallback technologies

### Phase 6: Robust Technology Detection

- Fix existing Wappalyzer coroutine issues
- Add HTTP header analysis fallback
- Add DNS record analysis fallback
- Add industry-based technology assignment

This design maintains full compatibility with the existing /arco architecture while adding powerful real marketing data analysis capabilities. The implementation follows established patterns and integrates seamlessly with current pipelines and CRM workflows.
