# ARCO FIND S-Tier Configuration
# BigQuery public datasets with cost controls

import os
from typing import Dict, Any

class STierConfig:
    """Production configuration for S-Tier BigQuery pipeline"""
    
    # BigQuery Cost Controls
    BIGQUERY_FREE_TIER_BYTES = 1024**4  # 1TB per month
    BIGQUERY_SAFETY_THRESHOLD = 0.8     # Use max 80% of free tier
    BIGQUERY_MAX_QUERY_BYTES = 50 * 1024**3  # 50GB per query max
    
    # Verified Public Datasets (with citations)
    PUBLIC_DATASETS = {
        'HTTP_ARCHIVE': {
            'table': 'bigquery-public-data.httparchive.lighthouse',
            'citation': 'HTTP Archive - https://httparchive.org/',
            'description': 'Web performance data from 8M+ URLs monthly',
            'partitioning': 'date (YYYYMMDD)',
            'cost_optimization': 'Always filter by date partition'
        },
        'CHROME_UX_REPORT': {
            'table': 'bigquery-public-data.chrome_ux_report.materialized_country_summary',
            'citation': 'Chrome UX Report - https://developers.google.com/web/tools/chrome-user-experience-report',
            'description': 'Real user experience metrics from Chrome',
            'partitioning': 'date (YYYY-MM-DD)',
            'cost_optimization': 'Filter by country_code and date'
        },
        'ADS_TRANSPARENCY': {
            'table': 'bigquery-public-data.google_ads_transparency_center.advertiser_stats',
            'citation': 'Google Ads Transparency Center - https://adstransparency.google.com/',
            'description': 'Self-declared advertising spend data',
            'partitioning': '_PARTITIONTIME (daily)',
            'limitations': 'Self-declared data, may be incomplete'
        }
    }
    
    # Transparent Scoring Methodology
    SCORING_WEIGHTS = {
        'spend_efficiency': {
            'weight': 0.35,
            'rationale': 'Higher spend indicates larger optimization opportunity',
            'calculation': 'LOG(monthly_spend_usd) / 10'
        },
        'ux_performance': {
            'weight': 0.25,
            'rationale': 'Deloitte study: -9% conversion per 500ms LCP increase',
            'calculation': '(lcp_ms - 2500) / 4000'
        },
        'layout_stability': {
            'weight': 0.20,
            'rationale': 'Web.dev research: -15% conversion per 0.1 CLS increase',
            'calculation': 'cumulative_layout_shift * 4'
        },
        'creative_fatigue': {
            'weight': 0.20,
            'rationale': 'High creative-to-spend ratio indicates poor optimization',
            'calculation': 'creative_count / monthly_spend_usd'
        }
    }
    
    # Performance Thresholds (based on Core Web Vitals)
    PERFORMANCE_THRESHOLDS = {
        'LCP_GOOD': 2500,      # milliseconds
        'LCP_POOR': 4000,      # milliseconds
        'CLS_GOOD': 0.1,       # score
        'CLS_POOR': 0.25,      # score
        'FCP_GOOD_RATIO': 0.75 # percentage of fast FCP
    }
    
    # Spend Classification
    SPEND_TIERS = {
        'LOW': {'min': 0, 'max': 2000},
        'MEDIUM': {'min': 2000, 'max': 5000},
        'HIGH': {'min': 5000, 'max': float('inf')}
    }
    
    # Data Freshness Requirements
    DATA_FRESHNESS = {
        'http_archive_max_age_days': 45,  # Monthly updates
        'crux_max_age_days': 35,          # Monthly updates
        'ads_transparency_max_age_days': 7 # Daily updates
    }
    
    # Quality Controls
    QUALITY_CONTROLS = {
        'min_crux_samples': 1000,         # Minimum CrUX samples for reliability
        'min_creative_count': 3,          # Minimum creatives for analysis
        'min_opportunity_score': 0.55,    # Minimum score for inclusion
        'max_results_per_query': 1000     # Limit results for cost control
    }
    
    @classmethod
    def get_gcp_project_id(cls) -> str:
        """Get GCP project ID from environment"""
        project_id = os.getenv('GCP_PROJECT_ID')
        if not project_id:
            raise ValueError("GCP_PROJECT_ID environment variable must be set")
        return project_id
    
    @classmethod
    def get_bigquery_credentials_path(cls) -> str:
        """Get BigQuery credentials path"""
        return os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
    
    @classmethod
    def get_cost_budget_usd(cls) -> float:
        """Get monthly cost budget (default: free tier only)"""
        return float(os.getenv('BIGQUERY_MONTHLY_BUDGET', '0'))
    
    @classmethod
    def validate_configuration(cls) -> Dict[str, Any]:
        """Validate configuration and return status"""
        
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'configuration': {
                'project_id': None,
                'credentials_configured': False,
                'cost_budget': cls.get_cost_budget_usd(),
                'free_tier_only': cls.get_cost_budget_usd() == 0
            }
        }
        
        # Check project ID
        try:
            validation['configuration']['project_id'] = cls.get_gcp_project_id()
        except ValueError as e:
            validation['valid'] = False
            validation['errors'].append(str(e))
        
        # Check credentials
        creds_path = cls.get_bigquery_credentials_path()
        if creds_path and os.path.exists(creds_path):
            validation['configuration']['credentials_configured'] = True
        elif not creds_path:
            validation['warnings'].append("Using default credentials (may not work in all environments)")
        else:
            validation['valid'] = False
            validation['errors'].append(f"Credentials file not found: {creds_path}")
        
        # Budget warnings
        if validation['configuration']['free_tier_only']:
            validation['warnings'].append("Using BigQuery free tier only (1TB/month)")
        
        return validation

# Production environment check
def check_production_readiness():
    """Check if environment is ready for production"""
    
    config_status = STierConfig.validate_configuration()
    
    print("🔍 S-TIER CONFIGURATION VALIDATION")
    print("=" * 50)
    
    if config_status['valid']:
        print("✅ Configuration valid")
        print(f"📊 Project: {config_status['configuration']['project_id']}")
        print(f"🔐 Credentials: {'✅' if config_status['configuration']['credentials_configured'] else '⚠️ Default'}")
        print(f"💰 Budget: ${config_status['configuration']['cost_budget']}/month")
    else:
        print("❌ Configuration invalid")
        for error in config_status['errors']:
            print(f"   ❌ {error}")
    
    if config_status['warnings']:
        print("\n⚠️ Warnings:")
        for warning in config_status['warnings']:
            print(f"   ⚠️ {warning}")
    
    print(f"\n📋 Dataset Citations:")
    for name, dataset in STierConfig.PUBLIC_DATASETS.items():
        print(f"   📊 {name}: {dataset['citation']}")
    
    return config_status['valid']

if __name__ == "__main__":
    check_production_readiness()
