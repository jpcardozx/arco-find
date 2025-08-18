"""
🔑 API CONFIGURATION - S-TIER LEAD GENERATION
Configuração consolidada para BigQuery + SearchAPI + Google Ads Library
Foco em insights premium para prospecção e aquisição de clientes piloto
"""

import os
from typing import Optional
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")

class APIConfig:
    """S-Tier API configuration for lead generation and conversion"""
    
    # === CORE APIS FOR LEAD GENERATION ===
    
    # SearchAPI - Meta Ads + Google Ads Library
    SEARCHAPI_KEY: str = os.getenv('SEARCHAPI_KEY')
    SEARCH_API_KEY: str = os.getenv('SEARCH_API_KEY', SEARCHAPI_KEY)  # Alias for compatibility
    SEARCHAPI_BASE_URL = "https://www.searchapi.io/api/v1/search"
    SEARCHAPI_DAILY_LIMIT = 1000
    
    # Google PageSpeed Insights API
    GOOGLE_PAGESPEED_API_KEY: str = os.getenv('GOOGLE_PAGESPEED_API_KEY') or os.getenv('PAGESPEED_KEY')
    PAGESPEED_BASE_URL = "https://www.googleapis.com/pagespeed/insights/v5/runPagespeed"
    
    # === BIGQUERY FOR LEAD STORAGE & ANALYTICS ===
    
    # BigQuery Project Configuration
    GOOGLE_CLOUD_PROJECT: str = os.getenv('GOOGLE_CLOUD_PROJECT', 'prospection-463116')
    BIGQUERY_DATASET_ID: str = os.getenv('BIGQUERY_DATASET_ID', 'arco_intelligence')
    BIGQUERY_LOCATION: str = os.getenv('BIGQUERY_LOCATION', 'US')
    
    # Service Account Details
    GOOGLE_CLIENT_ID: str = os.getenv('GOOGLE_CLIENT_ID', '738463274374-e26rpibop3g2ss6mer141mbt2q2sgn6h.apps.googleusercontent.com')
    GOOGLE_SERVICE_ACCOUNT_EMAIL: str = os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL', 'arco-prospection@prospection-463116.iam.gserviceaccount.com')
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
    
    # === S-TIER PROSPECT QUALIFICATION CRITERIA ===
    
    # Professional Services Targets (7-14 day sprint conversion)
    MIN_MONTHLY_SPEND = int(os.getenv('MIN_MONTHLY_SPEND', '5000'))  # $5k+/month
    MIN_EMPLOYEE_COUNT = int(os.getenv('MIN_EMPLOYEE_COUNT', '8'))  # 8+ employees
    MAX_EMPLOYEE_COUNT = int(os.getenv('MAX_EMPLOYEE_COUNT', '50'))  # 50 employees max
    MIN_WEBSITE_PERFORMANCE_SCORE = int(os.getenv('MIN_PERFORMANCE_SCORE', '60'))  # Performance issues
    
    # Target Industries for Pilot Conversion
    TARGET_INDUSTRIES = [
        'dental', 'orthodontics', 'cosmetic_dentistry', 'oral_surgery',
        'ecommerce', 'online_retail', 'dropshipping', 'shopify_stores',
        'fitness', 'personal_training', 'yoga', 'nutrition_coaching',
        'real_estate', 'property_management', 'construction'
    ]
    
    # === PERFORMANCE & CACHING ===
    
    # Redis Cache for API optimization
    REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379')
    REDIS_PASSWORD: Optional[str] = os.getenv('REDIS_PASSWORD')
    REDIS_DB: int = int(os.getenv('REDIS_DB', '0'))
    
    # Rate Limiting for API efficiency
    API_RATE_LIMIT_PER_SECOND = int(os.getenv('API_RATE_LIMIT_PER_SECOND', '5'))
    MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', '3'))
    
    # === S-TIER CONVERSION METRICS ===
    
    # Sprint targets (7-14 days)
    TARGET_PILOT_CONVERSIONS_PER_SPRINT = int(os.getenv('TARGET_PILOTS_PER_SPRINT', '3'))
    MIN_MONTHLY_SAVINGS_FOR_PILOT = int(os.getenv('MIN_SAVINGS_FOR_PILOT', '1000'))  # $1k+ savings
    TARGET_ROI_MULTIPLIER = float(os.getenv('TARGET_ROI_MULTIPLIER', '3.0'))  # 3x ROI minimum
    
    @classmethod
    def validate_s_tier_config(cls) -> bool:
        """Validate S-tier lead generation configuration"""
        required_keys = [
            cls.SEARCHAPI_KEY,
            cls.GOOGLE_PAGESPEED_API_KEY,
            cls.GOOGLE_CLOUD_PROJECT,
            cls.GOOGLE_SERVICE_ACCOUNT_EMAIL
        ]
        
        missing = []
        for i, key in enumerate(['SEARCHAPI_KEY', 'GOOGLE_PAGESPEED_API_KEY', 'GOOGLE_CLOUD_PROJECT', 'GOOGLE_SERVICE_ACCOUNT_EMAIL']):
            if not required_keys[i] or required_keys[i] == '':
                missing.append(key)
        
        if missing:
            raise ValueError(f"Missing S-tier API keys in .env: {missing}")
        
        print("S-Tier Lead Generation APIs Validated:")
        print(f"   SearchAPI: {cls.SEARCHAPI_KEY[:8]}...")
        print(f"   PageSpeed: {cls.GOOGLE_PAGESPEED_API_KEY[:8]}...")
        print(f"   BigQuery Project: {cls.GOOGLE_CLOUD_PROJECT}")
        print(f"   Target Industries: {len(cls.TARGET_INDUSTRIES)} sectors")
        print(f"   Sprint Target: {cls.TARGET_PILOT_CONVERSIONS_PER_SPRINT} pilot conversions")
        
        return True
    
    @classmethod
    def get_qualification_criteria(cls) -> dict:
        """Get S-tier qualification criteria for prospects"""
        return {
            'min_monthly_spend': cls.MIN_MONTHLY_SPEND,
            'employee_range': (cls.MIN_EMPLOYEE_COUNT, cls.MAX_EMPLOYEE_COUNT),
            'min_performance_score': cls.MIN_WEBSITE_PERFORMANCE_SCORE,
            'target_industries': cls.TARGET_INDUSTRIES,
            'min_monthly_savings': cls.MIN_MONTHLY_SAVINGS_FOR_PILOT,
            'target_roi': cls.TARGET_ROI_MULTIPLIER
        }
    
    @classmethod
    def get_sprint_conversion_settings(cls) -> dict:
        """Get sprint conversion settings"""
        return {
            "target_pilot_conversions_per_sprint": cls.TARGET_PILOT_CONVERSIONS_PER_SPRINT,
            "target_prospect_discovery_per_sprint": 15,  # 15 prospects per sprint
            "sprint_duration_days": 14,  # 14-day sprints
            "micro_audit_max_duration_days": 3,  # 3 days for micro audit
            "proposal_response_timeout_days": 7,  # 7 days for proposal response
            "pilot_execution_max_days": 14,  # 14 days max for pilot execution
            "conversion_targets": {
                "contact_rate": 0.70,  # 70% contact rate
                "audit_conversion_rate": 0.80,  # 80% audit acceptance
                "proposal_conversion_rate": 0.40,  # 40% proposal to pilot
                "pilot_completion_rate": 0.90  # 90% pilot completion
            }
        }
    
    @classmethod
    def get_roi_tracking_settings(cls) -> dict:
        """Get ROI tracking settings"""
        return {
            "target_roi_percentage": 250,  # 250% ROI target
            "cost_per_prospect": 150,  # $150 cost per prospect
            "conversion_tracking_enabled": True,
            "alert_thresholds": {
                "low_conversion_rate": 0.15,  # 15% overall conversion
                "high_value_conversion": 5000,  # $5k+ conversions
                "pipeline_health_threshold": 70  # 70/100 health score
            }
        }

# Helper function to get configuration values
def get_config(key: str, default=None):
    """Get configuration value with fallback to environment variables"""
    # First try to get from environment
    env_value = os.getenv(key, default)
    
    # Then try to get from APIConfig class
    if hasattr(APIConfig, key):
        return getattr(APIConfig, key) or env_value
    
    return env_value

def validate_required_keys():
    """Validate that all required API keys are present"""
    required_keys = {
        'SEARCHAPI_KEY': APIConfig.SEARCHAPI_KEY,
        'GOOGLE_PAGESPEED_API_KEY': APIConfig.GOOGLE_PAGESPEED_API_KEY or os.getenv('PAGESPEED_KEY'),
    }
    
    missing = []
    for key, value in required_keys.items():
        if not value or value.strip() == '':
            missing.append(key)
    
    if missing:
        print(f"⚠️  Missing API keys: {', '.join(missing)}")
        print("💡 Add them to your .env file or set as environment variables")
        return False
    
    print("✅ All required API keys are configured")
    return True

# Validate S-tier configuration on import
try:
    APIConfig.validate_s_tier_config()
except ValueError as e:
    print(f"S-Tier API Configuration Error: {e}")
    print("Check your .env file or update the API keys above")
