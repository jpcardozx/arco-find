"""
🎯 ARCO CONFIG MANAGER
Centralized configuration management for ARCO-FIND system
"""

import os
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class ARCOConfig:
    """Core ARCO configuration settings"""
    
    # API Settings
    search_api_key: str
    google_pagespeed_api_key: str
    
    # BigQuery Settings
    google_cloud_project: str
    bigquery_dataset_id: str
    bigquery_credentials_path: str
    
    # Performance Settings
    max_concurrent_requests: int = 5
    request_timeout: int = 30
    retry_attempts: int = 3
    
    # Cost Control
    max_daily_api_calls: int = 1000
    max_bigquery_slots: int = 500

class ARCOConfigManager:
    """Manages ARCO-FIND configuration and environment settings"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> ARCOConfig:
        """Load configuration from environment variables"""
        return ARCOConfig(
            search_api_key=os.getenv('SEARCH_API_KEY', '3sgTQQBwGfmtBR1WBW61MgnU'),
            google_pagespeed_api_key=os.getenv('GOOGLE_PAGESPEED_API_KEY', 'AIzaSyAcnfSgKqR6QEKKm6lY8u-8Q3vKzWOkY9c'),
            google_cloud_project=os.getenv('GOOGLE_CLOUD_PROJECT', 'prospection-463116'),
            bigquery_dataset_id=os.getenv('BIGQUERY_DATASET_ID', 'lead_intelligence'),
            bigquery_credentials_path=os.getenv('GOOGLE_APPLICATION_CREDENTIALS', ''),
            max_concurrent_requests=int(os.getenv('MAX_CONCURRENT_REQUESTS', '5')),
            request_timeout=int(os.getenv('REQUEST_TIMEOUT', '30')),
            retry_attempts=int(os.getenv('RETRY_ATTEMPTS', '3')),
            max_daily_api_calls=int(os.getenv('MAX_DAILY_API_CALLS', '1000')),
            max_bigquery_slots=int(os.getenv('MAX_BIGQUERY_SLOTS', '500'))
        )
    
    def get_config(self) -> ARCOConfig:
        """Get current configuration"""
        return self.config
    
    def update_config(self, updates: Dict[str, any]) -> None:
        """Update configuration dynamically"""
        for key, value in updates.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
    
    def validate_config(self) -> bool:
        """Validate that all required config is present"""
        required_fields = [
            'search_api_key', 
            'google_pagespeed_api_key',
            'google_cloud_project',
            'bigquery_dataset_id'
        ]
        
        for field in required_fields:
            if not getattr(self.config, field, None):
                return False
        
        return True

# Global instance
arco_config_manager = ARCOConfigManager()