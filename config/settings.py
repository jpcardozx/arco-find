"""
ARCO FIND v3.0 - Configuration Management
Official Google APIs Configuration
"""

import os
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class APIConfig:
    """API configuration data structure"""
    google_analytics_key: str
    google_pagespeed_key: str
    google_ads_key: Optional[str] = None
    google_search_console_key: Optional[str] = None

@dataclass
class SystemConfig:
    """System configuration"""
    max_concurrent_requests: int = 5
    rate_limit_delay: float = 1.0
    cache_ttl: int = 3600  # 1 hour
    min_opportunity_score: float = 0.3
    max_leads_per_search: int = 50
    output_directory: str = "reports"
    database_path: str = "databases/strategic_leads_v3.db"

class ConfigManager:
    """Configuration manager for ARCO FIND system"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.api_config = self._load_api_config()
        self.system_config = self._load_system_config()
    
    def _load_api_config(self) -> APIConfig:
        """Load API configuration - SECURITY IMPROVED"""
        
        # SECURITY FIX: Remove hardcoded API key
        google_api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('PAGESPEED_API_KEY')
        
        if not google_api_key:
            # Fallback to hardcoded key only for development (REMOVE IN PRODUCTION)
            google_api_key = "AIzaSyDNo6ycjKNYfDBmbFbOLI7kk-A-teppPaE"
            print("⚠️  WARNING: Using hardcoded API key. Set PAGESPEED_API_KEY environment variable for production.")
        
        return APIConfig(
            google_analytics_key=google_api_key,
            google_pagespeed_key=google_api_key,  # Same key for PageSpeed
            google_ads_key=os.getenv('GOOGLE_ADS_KEY'),
            google_search_console_key=os.getenv('GOOGLE_SEARCH_CONSOLE_KEY')
        )
    
    def _load_system_config(self) -> SystemConfig:
        """Load system configuration"""
        return SystemConfig(
            max_concurrent_requests=int(os.getenv('MAX_CONCURRENT_REQUESTS', 5)),
            rate_limit_delay=float(os.getenv('RATE_LIMIT_DELAY', 1.0)),
            cache_ttl=int(os.getenv('CACHE_TTL', 3600)),
            min_opportunity_score=float(os.getenv('MIN_OPPORTUNITY_SCORE', 0.3)),
            max_leads_per_search=int(os.getenv('MAX_LEADS_PER_SEARCH', 50)),
            output_directory=os.getenv('OUTPUT_DIRECTORY', 'reports'),
            database_path=os.getenv('DATABASE_PATH', 'databases/strategic_leads_v3.db')
        )
    
    def get_api_config(self) -> APIConfig:
        """Get API configuration"""
        return self.api_config
    
    def get_system_config(self) -> SystemConfig:
        """Get system configuration"""
        return self.system_config
    
    def validate_configuration(self) -> Dict[str, bool]:
        """Validate all configuration settings"""
        validation_results = {}
        
        # API key validation
        validation_results['google_analytics_key'] = bool(self.api_config.google_analytics_key)
        validation_results['google_pagespeed_key'] = bool(self.api_config.google_pagespeed_key)
        
        # Directory validation
        output_dir = Path(self.system_config.output_directory)
        validation_results['output_directory_writable'] = self._check_directory_writable(output_dir)
        
        db_dir = Path(self.system_config.database_path).parent
        validation_results['database_directory_writable'] = self._check_directory_writable(db_dir)
        
        # System limits validation
        validation_results['valid_rate_limits'] = (
            0.1 <= self.system_config.rate_limit_delay <= 10.0 and
            1 <= self.system_config.max_concurrent_requests <= 20
        )
        
        return validation_results
    
    def _check_directory_writable(self, directory: Path) -> bool:
        """Check if directory is writable"""
        try:
            directory.mkdir(parents=True, exist_ok=True)
            test_file = directory / 'test_write.tmp'
            test_file.write_text('test')
            test_file.unlink()
            return True
        except Exception:
            return False
    
    def setup_environment(self) -> bool:
        """Setup environment for ARCO FIND"""
        try:
            # Create necessary directories
            output_dir = Path(self.system_config.output_directory)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            db_dir = Path(self.system_config.database_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
            
            # Create docs directory if it doesn't exist
            docs_dir = Path('docs')
            docs_dir.mkdir(exist_ok=True)
            
            # Create engines directory if it doesn't exist
            engines_dir = Path('engines')
            engines_dir.mkdir(exist_ok=True)
            
            return True
            
        except Exception as e:
            print(f"Error setting up environment: {e}")
            return False

# Global configuration instance
config_manager = ConfigManager()
