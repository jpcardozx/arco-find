"""
🔑 API CONFIGURATION - PRODUCTION KEYS
Secure credential management for all external APIs
"""

import os
from typing import Optional

class APIConfig:
    """Production API configuration"""
    
    # Google Chrome UX Report API
    CRUX_API_KEY: Optional[str] = os.getenv('CRUX_API_KEY')
    CRUX_BASE_URL = "https://chromeuxreport.googleapis.com/v1/records:queryRecord"
    CRUX_DAILY_LIMIT = 25000
    
    # Google Ads API
    GOOGLE_ADS_DEVELOPER_TOKEN: Optional[str] = os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN')
    GOOGLE_ADS_CLIENT_ID: Optional[str] = os.getenv('GOOGLE_ADS_CLIENT_ID')
    GOOGLE_ADS_CLIENT_SECRET: Optional[str] = os.getenv('GOOGLE_ADS_CLIENT_SECRET')
    GOOGLE_ADS_REFRESH_TOKEN: Optional[str] = os.getenv('GOOGLE_ADS_REFRESH_TOKEN')
    
    # Redis Cache
    REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379')
    REDIS_PASSWORD: Optional[str] = os.getenv('REDIS_PASSWORD')
    REDIS_DB: int = int(os.getenv('REDIS_DB', '0'))
    
    # Rate Limiting
    PLAYWRIGHT_MAX_CONCURRENT = int(os.getenv('PLAYWRIGHT_MAX_CONCURRENT', '3'))
    API_RATE_LIMIT_PER_SECOND = int(os.getenv('API_RATE_LIMIT_PER_SECOND', '10'))
    
    @classmethod
    def validate_required_keys(cls) -> bool:
        """Validate all required API keys are present"""
        required = [
            cls.CRUX_API_KEY,
            cls.REDIS_URL
        ]
        
        missing = [key for key in required if not key]
        
        if missing:
            raise ValueError(f"Missing required API keys: {missing}")
        
        return True

# Validate on import
try:
    APIConfig.validate_required_keys()
    print("✅ API configuration validated")
except ValueError as e:
    print(f"⚠️  API configuration warning: {e}")
