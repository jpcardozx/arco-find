# BigQuery Implementation Guide - ARCO FIND

## 🎯 Guia Prático de Implementação

### Fase 1: Setup do Ambiente BigQuery

#### 1.1 Pré-requisitos GCP

```bash
# Install Google Cloud CLI (se não tiver)
# Windows: https://cloud.google.com/sdk/docs/install
# Ou via chocolatey:
choco install gcloudsdk

# Authenticate
gcloud auth login
gcloud auth application-default login

# Set project
gcloud config set project YOUR_PROJECT_ID
```

#### 1.2 BigQuery Datasets Necessários

```sql
-- Create main datasets
CREATE SCHEMA `your-project.marketing_intelligence`
OPTIONS(
  description="Marketing intelligence data for lead discovery",
  location="US"
);

CREATE SCHEMA `your-project.business_intelligence`
OPTIONS(
  description="Business directory and company information",
  location="US"
);

CREATE SCHEMA `your-project.lead_intelligence`
OPTIONS(
  description="Processed lead intelligence and scoring",
  location="US"
);
```

#### 1.3 Core Tables Setup

```sql
-- Google Ads Performance Data
CREATE TABLE `your-project.marketing_intelligence.google_ads_performance` (
    date DATE,
    domain STRING,
    company_name STRING,
    vertical STRING,
    campaign_name STRING,
    cost FLOAT64,
    clicks INT64,
    impressions INT64,
    conversions FLOAT64,
    conversion_rate FLOAT64,
    cost_per_click FLOAT64,
    cost_per_conversion FLOAT64,
    quality_score FLOAT64,
    impression_share FLOAT64,
    search_impression_share FLOAT64,
    search_rank_lost_impression_share FLOAT64
)
PARTITION BY date
CLUSTER BY domain, vertical;

-- Business Directory
CREATE TABLE `your-project.business_intelligence.company_directory` (
    domain STRING,
    company_name STRING,
    vertical STRING,
    estimated_revenue FLOAT64,
    estimated_ltv FLOAT64,
    employee_count INT64,
    location STRING,
    phone STRING,
    website_technology ARRAY<STRING>,
    social_media STRUCT<
        linkedin STRING,
        facebook STRING,
        twitter STRING
    >,
    last_updated TIMESTAMP
)
CLUSTER BY domain, vertical;
```

### Fase 2: Data Sources & Integration

#### 2.1 Google Ads Data Integration

```python
from google.ads.googleads.client import GoogleAdsClient
from google.cloud import bigquery
import pandas as pd

class GoogleAdsToBigQuery:
    def __init__(self, developer_token, client_id, client_secret, refresh_token):
        self.ads_client = GoogleAdsClient.load_from_dict({
            "developer_token": developer_token,
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "use_proto_plus": True
        })
        self.bq_client = bigquery.Client()

    def extract_campaign_performance(self, customer_id: str, date_range: str = "LAST_30_DAYS"):
        """Extract campaign performance data from Google Ads API"""

        query = f"""
        SELECT
            campaign.name,
            campaign.advertising_channel_type,
            segments.date,
            metrics.cost_micros,
            metrics.clicks,
            metrics.impressions,
            metrics.conversions,
            metrics.cost_per_conversion,
            metrics.ctr,
            metrics.search_impression_share,
            metrics.search_rank_lost_impression_share
        FROM campaign
        WHERE segments.date DURING {date_range}
        AND campaign.status = 'ENABLED'
        """

        ga_service = self.ads_client.get_service("GoogleAdsService")
        response = ga_service.search(customer_id=customer_id, query=query)

        # Process and upload to BigQuery
        data = []
        for row in response:
            data.append({
                'date': row.segments.date,
                'campaign_name': row.campaign.name,
                'cost': row.metrics.cost_micros / 1_000_000,  # Convert micros
                'clicks': row.metrics.clicks,
                'impressions': row.metrics.impressions,
                'conversions': row.metrics.conversions,
                'conversion_rate': row.metrics.conversions / max(row.metrics.clicks, 1),
                'cost_per_click': row.metrics.cost_micros / 1_000_000 / max(row.metrics.clicks, 1),
                'impression_share': row.metrics.search_impression_share
            })

        return pd.DataFrame(data)

    def upload_to_bigquery(self, df: pd.DataFrame, table_id: str):
        """Upload data to BigQuery"""
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND",
            schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION]
        )

        job = self.bq_client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()  # Wait for completion

        print(f"Loaded {len(df)} rows to {table_id}")
```

#### 2.2 Business Directory Enrichment

```python
import requests
from typing import Dict, Optional

class BusinessEnrichment:
    def __init__(self, clearbit_api_key: str):
        self.clearbit_key = clearbit_api_key

    def enrich_company_data(self, domain: str) -> Optional[Dict]:
        """Enrich company data using Clearbit API"""

        url = f"https://company.clearbit.com/v2/companies/find?domain={domain}"
        headers = {"Authorization": f"Bearer {self.clearbit_key}"}

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return {
                    'domain': domain,
                    'company_name': data.get('name'),
                    'estimated_revenue': data.get('metrics', {}).get('annualRevenue'),
                    'employee_count': data.get('metrics', {}).get('employees'),
                    'vertical': data.get('category', {}).get('industry'),
                    'location': data.get('geo', {}).get('city'),
                    'technology': data.get('tech', [])
                }
        except Exception as e:
            print(f"Error enriching {domain}: {e}")

        return None
```

### Fase 3: Core Intelligence Queries

#### 3.1 Poor Ad Performance Detection

```sql
-- Identifica empresas com performance ruim mas alto investimento
CREATE OR REPLACE VIEW `your-project.lead_intelligence.poor_ad_performers` AS
WITH market_benchmarks AS (
  SELECT
    vertical,
    APPROX_QUANTILES(conversion_rate, 100)[OFFSET(75)] as top_quartile_conversion,
    APPROX_QUANTILES(cost_per_click, 100)[OFFSET(25)] as efficient_cpc,
    AVG(quality_score) as avg_quality_score
  FROM `your-project.marketing_intelligence.google_ads_performance`
  WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
  GROUP BY vertical
),
company_performance AS (
  SELECT
    domain,
    company_name,
    vertical,
    AVG(conversion_rate) as current_conversion_rate,
    AVG(cost_per_click) as current_cpc,
    AVG(quality_score) as current_quality_score,
    SUM(cost) as total_spend_90d,
    COUNT(DISTINCT date) as active_days
  FROM `your-project.marketing_intelligence.google_ads_performance`
  WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
  GROUP BY domain, company_name, vertical
  HAVING total_spend_90d >= 5000 AND active_days >= 30
)
SELECT
  cp.*,
  mb.top_quartile_conversion,
  mb.efficient_cpc,
  -- Performance gaps
  GREATEST(0, mb.top_quartile_conversion - cp.current_conversion_rate) as conversion_gap,
  GREATEST(0, cp.current_cpc - mb.efficient_cpc) as cpc_excess,

  -- Opportunity calculations
  (mb.top_quartile_conversion - cp.current_conversion_rate) *
  (cp.total_spend_90d / cp.current_cpc) as potential_additional_leads_90d,

  -- Opportunity scoring
  CASE
    WHEN mb.top_quartile_conversion - cp.current_conversion_rate > 0.03
         AND cp.total_spend_90d > 15000 THEN 0.95
    WHEN cp.current_cpc - mb.efficient_cpc > 5.0
         AND cp.total_spend_90d > 10000 THEN 0.85
    WHEN cp.current_quality_score < 5
         AND cp.total_spend_90d > 8000 THEN 0.75
    ELSE 0.4
  END as opportunity_score,

  CURRENT_TIMESTAMP() as analysis_date
FROM company_performance cp
JOIN market_benchmarks mb ON cp.vertical = mb.vertical
WHERE
  (mb.top_quartile_conversion - cp.current_conversion_rate > 0.02
   OR cp.current_cpc - mb.efficient_cpc > 2.0
   OR cp.current_quality_score < 6)
  AND cp.total_spend_90d >= 5000;
```

#### 3.2 Market Share Analysis

```sql
-- Análise de market share e competitive intelligence
CREATE OR REPLACE VIEW `your-project.lead_intelligence.market_share_analysis` AS
WITH vertical_totals AS (
  SELECT
    vertical,
    SUM(cost) as total_vertical_spend,
    COUNT(DISTINCT domain) as total_companies
  FROM `your-project.marketing_intelligence.google_ads_performance`
  WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
  GROUP BY vertical
),
company_market_position AS (
  SELECT
    domain,
    company_name,
    vertical,
    SUM(cost) as company_spend,
    AVG(impression_share) as avg_impression_share,
    RANK() OVER (PARTITION BY vertical ORDER BY SUM(cost) DESC) as spend_rank
  FROM `your-project.marketing_intelligence.google_ads_performance`
  WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
  GROUP BY domain, company_name, vertical
)
SELECT
  cmp.*,
  vt.total_vertical_spend,
  vt.total_companies,
  (cmp.company_spend / vt.total_vertical_spend) * 100 as market_share_percent,
  CASE
    WHEN cmp.spend_rank <= 5 THEN 'MARKET_LEADER'
    WHEN cmp.spend_rank <= 15 THEN 'MAJOR_PLAYER'
    WHEN cmp.spend_rank <= 50 THEN 'ESTABLISHED'
    ELSE 'EMERGING'
  END as market_position,

  -- Opportunity indicators
  CASE
    WHEN cmp.avg_impression_share < 0.3 AND cmp.company_spend > 10000 THEN 'GROWTH_POTENTIAL'
    WHEN cmp.spend_rank > 20 AND cmp.company_spend > 5000 THEN 'EXPANSION_OPPORTUNITY'
    ELSE 'STABLE'
  END as growth_opportunity
FROM company_market_position cmp
JOIN vertical_totals vt ON cmp.vertical = vt.vertical
ORDER BY cmp.vertical, cmp.spend_rank;
```

#### 3.3 ROI Opportunity Calculator

```sql
-- Calcula oportunidades precisas de ROI baseado em dados reais
CREATE OR REPLACE VIEW `your-project.lead_intelligence.roi_opportunities` AS
WITH industry_benchmarks AS (
  SELECT
    vertical,
    APPROX_QUANTILES(conversion_rate, 100)[OFFSET(90)] as top_10_percent_conversion,
    APPROX_QUANTILES(cost_per_conversion, 100)[OFFSET(10)] as efficient_cost_per_conversion
  FROM `your-project.marketing_intelligence.google_ads_performance`
  WHERE
    date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
    AND conversions > 0
  GROUP BY vertical
)
SELECT
  gap.domain,
  gap.company_name,
  gap.vertical,
  gap.total_spend_90d as current_quarterly_spend,
  gap.current_conversion_rate,
  ib.top_10_percent_conversion as benchmark_conversion_rate,
  bd.estimated_ltv,

  -- Current performance
  (gap.total_spend_90d / gap.current_cpc) as current_clicks_90d,
  (gap.total_spend_90d / gap.current_cpc) * gap.current_conversion_rate as current_leads_90d,

  -- Potential with optimization
  (gap.total_spend_90d / gap.current_cpc) * ib.top_10_percent_conversion as potential_leads_90d,

  -- Opportunity calculations
  ((gap.total_spend_90d / gap.current_cpc) * ib.top_10_percent_conversion) -
  ((gap.total_spend_90d / gap.current_cpc) * gap.current_conversion_rate) as additional_leads_90d,

  -- Revenue impact
  (((gap.total_spend_90d / gap.current_cpc) * ib.top_10_percent_conversion) -
   ((gap.total_spend_90d / gap.current_cpc) * gap.current_conversion_rate)) *
   bd.estimated_ltv as quarterly_revenue_opportunity,

  -- Annual projection
  (((gap.total_spend_90d / gap.current_cpc) * ib.top_10_percent_conversion) -
   ((gap.total_spend_90d / gap.current_cpc) * gap.current_conversion_rate)) *
   bd.estimated_ltv * 4 as annual_revenue_opportunity,

  -- Priority classification
  CASE
    WHEN (((gap.total_spend_90d / gap.current_cpc) * ib.top_10_percent_conversion) -
          ((gap.total_spend_90d / gap.current_cpc) * gap.current_conversion_rate)) *
          bd.estimated_ltv * 4 > 200000 THEN 'TIER_1_PRIORITY'
    WHEN (((gap.total_spend_90d / gap.current_cpc) * ib.top_10_percent_conversion) -
          ((gap.total_spend_90d / gap.current_cpc) * gap.current_conversion_rate)) *
          bd.estimated_ltv * 4 > 100000 THEN 'TIER_2_QUALIFIED'
    WHEN (((gap.total_spend_90d / gap.current_cpc) * ib.top_10_percent_conversion) -
          ((gap.total_spend_90d / gap.current_cpc) * gap.current_conversion_rate)) *
          bd.estimated_ltv * 4 > 50000 THEN 'TIER_3_PROSPECT'
    ELSE 'MONITOR'
  END as priority_tier

FROM `your-project.lead_intelligence.poor_ad_performers` gap
JOIN industry_benchmarks ib ON gap.vertical = ib.vertical
JOIN `your-project.business_intelligence.company_directory` bd ON gap.domain = bd.domain
WHERE
  gap.opportunity_score >= 0.6
  AND ib.top_10_percent_conversion > gap.current_conversion_rate
ORDER BY annual_revenue_opportunity DESC;
```

### Fase 4: Automated Pipeline

#### 4.1 Daily Intelligence Update

```python
from google.cloud import bigquery
from google.cloud import scheduler_v1
import json

class DailyIntelligenceUpdate:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.bq_client = bigquery.Client()

    def refresh_intelligence_views(self):
        """Refresh all intelligence views with latest data"""

        views_to_refresh = [
            "lead_intelligence.poor_ad_performers",
            "lead_intelligence.market_share_analysis",
            "lead_intelligence.roi_opportunities"
        ]

        for view in views_to_refresh:
            query = f"SELECT COUNT(*) as row_count FROM `{self.project_id}.{view}`"

            try:
                query_job = self.bq_client.query(query)
                result = list(query_job.result())[0]
                print(f"✅ {view}: {result.row_count} records")
            except Exception as e:
                print(f"❌ Error refreshing {view}: {e}")

    def generate_daily_leads(self, min_opportunity: float = 50000) -> List[Dict]:
        """Generate daily qualified leads report"""

        query = f"""
        SELECT
            domain,
            company_name,
            vertical,
            annual_revenue_opportunity,
            priority_tier,
            current_conversion_rate,
            benchmark_conversion_rate,
            current_quarterly_spend
        FROM `{self.project_id}.lead_intelligence.roi_opportunities`
        WHERE
            annual_revenue_opportunity >= {min_opportunity}
            AND priority_tier IN ('TIER_1_PRIORITY', 'TIER_2_QUALIFIED')
        ORDER BY annual_revenue_opportunity DESC
        LIMIT 25
        """

        query_job = self.bq_client.query(query)
        results = query_job.result()

        leads = []
        for row in results:
            leads.append({
                'domain': row.domain,
                'company_name': row.company_name,
                'vertical': row.vertical,
                'annual_opportunity': float(row.annual_revenue_opportunity),
                'priority': row.priority_tier,
                'current_conversion': float(row.current_conversion_rate),
                'benchmark_conversion': float(row.benchmark_conversion_rate),
                'quarterly_spend': float(row.current_quarterly_spend)
            })

        return leads

# Cloud Function for daily execution
def daily_intelligence_pipeline(request):
    """Cloud Function entry point for daily intelligence update"""

    updater = DailyIntelligenceUpdate("your-project-id")

    # Refresh views
    updater.refresh_intelligence_views()

    # Generate leads
    leads = updater.generate_daily_leads()

    # Send to CRM or email
    # ... integration code here ...

    return json.dumps({
        'status': 'success',
        'leads_generated': len(leads),
        'total_opportunity': sum(lead['annual_opportunity'] for lead in leads)
    })
```

### Fase 5: Monitoring & Optimization

#### 5.1 Query Cost Monitoring

```sql
-- Monitor BigQuery costs and optimize
SELECT
    job_id,
    creation_time,
    total_bytes_processed / 1024 / 1024 / 1024 as gb_processed,
    (total_bytes_processed / 1024 / 1024 / 1024) * 5 as estimated_cost_usd,
    query,
    state
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE
    creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
    AND job_type = 'QUERY'
ORDER BY gb_processed DESC
LIMIT 20;
```

#### 5.2 Data Quality Checks

```sql
-- Data quality monitoring
CREATE OR REPLACE VIEW `your-project.monitoring.data_quality_dashboard` AS
SELECT
    'google_ads_performance' as table_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT domain) as unique_domains,
    MIN(date) as earliest_date,
    MAX(date) as latest_date,
    COUNTIF(cost IS NULL OR cost <= 0) as invalid_cost_rows,
    COUNTIF(conversion_rate < 0 OR conversion_rate > 1) as invalid_conversion_rates,
    CURRENT_TIMESTAMP() as check_timestamp
FROM `your-project.marketing_intelligence.google_ads_performance`

UNION ALL

SELECT
    'company_directory' as table_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT domain) as unique_domains,
    NULL as earliest_date,
    NULL as latest_date,
    COUNTIF(company_name IS NULL) as invalid_cost_rows,
    COUNTIF(estimated_ltv <= 0) as invalid_conversion_rates,
    CURRENT_TIMESTAMP() as check_timestamp
FROM `your-project.business_intelligence.company_directory`;
```

## 🚀 Migration Strategy

### Step 1: Proof of Concept (Week 1)

- [ ] Setup minimal BigQuery environment
- [ ] Import sample Google Ads data
- [ ] Test core intelligence queries
- [ ] Validate data quality and insights

### Step 2: Data Pipeline (Week 2-3)

- [ ] Implement Google Ads data integration
- [ ] Build business directory enrichment
- [ ] Setup automated data refresh
- [ ] Create monitoring dashboards

### Step 3: Intelligence Engine (Week 3-4)

- [ ] Deploy production intelligence views
- [ ] Build lead scoring pipeline
- [ ] Create strategic reporting
- [ ] Setup alerting for high-value opportunities

### Step 4: Scale & Optimize (Week 4+)

- [ ] Optimize query performance
- [ ] Implement cost controls
- [ ] Add additional data sources
- [ ] Build automated outreach integration

---

**ROI Expectation**: Com BigQuery, esperamos:

- **10x mais leads qualificados** (50+ vs 5 com scraping)
- **95% accuracy** vs 30% com APIs públicas
- **Minutos vs horas** de processamento
- **3-5% conversion rate** vs <1% atual
- **$200K+ annual opportunities** identificadas por dia

**Investment**: ~$500-2000/month BigQuery costs vs desenvolvimento infinito de scrapers
