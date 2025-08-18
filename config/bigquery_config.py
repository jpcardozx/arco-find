#!/usr/bin/env python3
"""
🔧 BIGQUERY CONFIGURATION FOR ARCO S-TIER
=========================================

Configuration for BigQuery S-tier lead discovery:
- Project setup
- Dataset management  
- Query optimization settings
- Cost control parameters

Author: ARCO Intelligence
Date: August 2025
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class BigQueryConfig:
    """BigQuery configuration settings"""
    
    # Project settings
    project_id: str = "prospection-463116"  # Our project for billing
    dataset_id: str = "arco_intelligence"
    location: str = "US"  # Must match public data location
    
    # Query optimization
    max_bytes_billed: int = 1_000_000_000  # 1GB limit
    use_cache: bool = True
    use_standard_sql: bool = True
    
    # Cost control
    dry_run_first: bool = True
    job_timeout_ms: int = 300_000  # 5 minutes
    
    # CrUX settings - CORRECTED PROJECT REFERENCES
    crux_project: str = "chrome-ux-report"     # ✅ PROJETO CORRETO
    crux_dataset: str = "all"                  # ✅ DATASET CORRETO  
    crux_form_factor: str = "phone"            # mobile-first
    
    # HTTP Archive settings - CORRECTED PROJECT REFERENCES
    httparchive_project: str = "httparchive"   # ✅ PROJETO CORRETO
    httparchive_dataset: str = "summary_pages" # ✅ DATASET CORRETO
    
    # Creative stats settings - JÁ ESTAVA CORRETO
    creative_stats_table: str = "bigquery-public-data.google_ads_transparency_center.creative_stats"
    
    # Performance thresholds
    lcp_good_threshold: float = 2500  # ms
    inp_good_threshold: float = 200   # ms  
    cls_good_threshold: float = 0.1   # score
    
    # Quality thresholds
    lcp_pct_threshold: float = 0.60   # 60% fast
    inp_pct_threshold: float = 0.70   # 70% good
    cls_pct_threshold: float = 0.75   # 75% good

# BigQuery authentication
def get_bigquery_credentials() -> Optional[str]:
    """Get BigQuery credentials path"""
    
    # Check for explicit credential path
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if cred_path and os.path.exists(cred_path):
        return cred_path
    
    # Check common locations
    common_paths = [
        "config/gcp-credentials.json",
        "config/bigquery-credentials.json", 
        "~/.config/gcloud/application_default_credentials.json",
        "C:\\Users\\{user}\\AppData\\Roaming\\gcloud\\application_default_credentials.json".format(
            user=os.getenv("USERNAME", "")
        )
    ]
    
    for path in common_paths:
        expanded_path = os.path.expanduser(path)
        if os.path.exists(expanded_path):
            return expanded_path
    
    return None

# Query templates
QUERY_TEMPLATES = {
    "media_discovery": """
    WITH recent_month AS (
      SELECT FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)) AS start_date
    ),
    base_advertisers AS (
      SELECT
        advertiser_id,
        advertiser_disclosed_name,
        advertiser_legal_name,
        advertiser_location,
        MAX(PARSE_DATE('%Y%m%d', last_shown)) AS last_shown_date,
        COUNT(DISTINCT creative_id) AS total_creatives,
        COUNT(DISTINCT CASE WHEN surfaces LIKE '%SEARCH%' THEN creative_id END) AS search_creatives,
        COUNT(DISTINCT CASE WHEN surfaces LIKE '%YOUTUBE%' THEN creative_id END) AS youtube_creatives,
        COUNT(DISTINCT CASE WHEN surfaces LIKE '%DISPLAY%' THEN creative_id END) AS display_creatives,
        AVG(CASE WHEN impressions_enabled_min IS NOT NULL THEN impressions_enabled_min ELSE 0 END) AS avg_impressions_min,
        AVG(CASE WHEN impressions_enabled_max IS NOT NULL THEN impressions_enabled_max ELSE 0 END) AS avg_impressions_max
      FROM `{creative_stats_table}`
      WHERE advertiser_location IN ({countries_filter})
        AND PARSE_DATE('%Y%m%d', last_shown) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        AND verification_type IS NOT NULL
      GROUP BY 1,2,3,4
    ),
    scored_advertisers AS (
      SELECT *,
        DATE_DIFF(CURRENT_DATE(), last_shown_date, DAY) AS days_since_last,
        SAFE_DIVIDE(total_creatives, 30.0) AS rotation_score,
        SAFE_DIVIDE(search_creatives, total_creatives) AS search_share,
        SAFE_DIVIDE(youtube_creatives, total_creatives) AS youtube_share,
        SAFE_DIVIDE(display_creatives, total_creatives) AS display_share,
        (avg_impressions_min + avg_impressions_max) / 2 AS avg_impressions
      FROM base_advertisers
      WHERE total_creatives >= 3  -- Active advertisers only
    ),
    pain_signals AS (
      SELECT *,
        -- Pain signal flags
        CASE WHEN rotation_score < 0.5 THEN 1 ELSE 0 END AS low_rotation_flag,
        CASE WHEN search_share >= 0.85 OR youtube_share >= 0.8 THEN 1 ELSE 0 END AS mono_surface_flag,
        CASE WHEN days_since_last <= 7 THEN 1 ELSE 0 END AS active_7d_flag,
        
        -- Priority score (0-100)
        LEAST(100, 
          (CASE WHEN days_since_last <= 7 THEN 30 ELSE GREATEST(0, 30 - days_since_last) END) +
          (CASE WHEN rotation_score < 0.5 THEN 25 ELSE 0 END) +
          (CASE WHEN search_share >= 0.85 OR youtube_share >= 0.8 THEN 20 ELSE 0 END) +
          (LEAST(avg_impressions / 1000, 25))
        ) AS priority_score
      FROM scored_advertisers
    )
    SELECT *
    FROM pain_signals
    WHERE priority_score >= 40  -- Only qualified leads
    ORDER BY priority_score DESC, avg_impressions DESC
    LIMIT {limit}
    """,
    
    "crux_analysis": """
    WITH origins AS (
      SELECT origin FROM UNNEST([{origins_filter}]) AS origin
    ),
    crux_data AS (
      SELECT
        origin,
        SUM(CASE WHEN lcp.start < {lcp_threshold} THEN lcp.density ELSE 0 END) AS pct_fast_lcp,
        SUM(CASE WHEN inp.start < {inp_threshold} THEN inp.density ELSE 0 END) AS pct_good_inp,
        SUM(CASE WHEN cls.start < {cls_threshold} THEN cls.density ELSE 0 END) AS pct_good_cls
      FROM `chrome-ux-report.all.*`,
           UNNEST(largest_contentful_paint.histogram.bin) AS lcp,
           UNNEST(interaction_to_next_paint.histogram.bin) AS inp,
           UNNEST(layout_instability.cumulative_layout_shift.histogram.bin) AS cls
      WHERE _TABLE_SUFFIX = '{yyyymm}'
        AND origin IN (SELECT origin FROM origins)
        AND form_factor.name = '{form_factor}'
      GROUP BY origin
    )
    SELECT 
      origin,
      pct_fast_lcp, pct_good_inp, pct_good_cls,
      IF(pct_fast_lcp < {lcp_pct_threshold}, true, false) AS lcp_poor_flag,
      IF(pct_good_inp < {inp_pct_threshold}, true, false) AS inp_poor_flag,
      IF(pct_good_cls < {cls_pct_threshold}, true, false) AS cls_poor_flag
    FROM crux_data
    """
}

# Cost estimation helpers
def estimate_query_cost(query: str) -> str:
    """Estimate BigQuery query cost"""
    # Simple heuristic based on query complexity
    if "chrome-ux-report" in query:
        return "~$0.01-0.05 (CrUX data)"
    elif "google_ads_transparency_center" in query:
        return "~$0.01-0.10 (Creative stats)" 
    elif "httparchive" in query:
        return "~$0.05-0.20 (HTTP Archive)"
    else:
        return "~$0.001-0.01 (Small query)"

# Validation helpers
def validate_countries(countries: List[str]) -> bool:
    """Validate country codes"""
    valid_countries = {"AU", "NZ", "US", "CA", "GB", "DE", "FR", "IT", "ES", "JP"}
    return all(country in valid_countries for country in countries)

def validate_vertical(vertical: str) -> bool:
    """Validate business vertical"""
    valid_verticals = {
        "real_estate", "legal", "dental", "medical", "automotive", 
        "finance", "tech", "saas", "ecommerce", "home_services"
    }
    return vertical in valid_verticals

# Default configuration instance
config = BigQueryConfig()

# Export for easy import
__all__ = [
    "BigQueryConfig", 
    "config",
    "get_bigquery_credentials",
    "QUERY_TEMPLATES",
    "estimate_query_cost",
    "validate_countries",
    "validate_vertical"
]
