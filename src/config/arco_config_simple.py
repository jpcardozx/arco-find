"""
ARCO S-tier Configuration - Simplified version that works
"""
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SearchAPIConfig:
    """Configuração simplificada para SearchAPI"""
    
    def __init__(self):
        self.api_key = os.getenv('SEARCHAPI_KEY') or os.getenv('API_KEY', '3sgTQQBwGfmtBR1WBW61MgnU')
        self.base_url = os.getenv('BASE_URL', 'https://www.searchapi.io/api/v1/search')
        self.max_requests_per_minute = int(os.getenv('MAX_REQUESTS_PER_MINUTE', '60'))
        self.max_concurrent = int(os.getenv('MAX_CONCURRENT', '3'))
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', '30'))
        self.max_keywords_per_vertical = int(os.getenv('MAX_KEYWORDS_PER_VERTICAL', '5'))
        
        # Parse priority regions
        regions_str = os.getenv('PRIORITY_REGIONS', 'IE,GB,MT,CY')
        self.priority_regions = [r.strip() for r in regions_str.split(',')]
        
        # Rate limiting
        self.rate_limit_delay = 1.0  # 1 second between requests
        self.max_retries = 3  # Maximum retry attempts
        
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'

class VerticalConfig:
    """Configuração das verticais ARCO"""
    
    def __init__(self):
        # Pain signal keywords for dental/ortho
        self.dental_ortho_keywords = [
            "emergency dentist", "tooth pain relief", "dental implants cost",
            "orthodontist near me", "wisdom tooth removal", "dental emergency"
        ]
        
        # Pain signal keywords for medical spa
        self.medical_spa_keywords = [
            "botox near me", "laser hair removal cost", "coolsculpting results",
            "lip filler prices", "anti aging treatments", "medical aesthetics"
        ]
        
        # Pain signal keywords for real estate (Europa focus) - Higher volume terms
        self.real_estate_eu_keywords = [
            "property management", "estate agent", "buy property",
            "property investment", "mortgage advice", "house buying"
        ]

class ARCOConfig:
    """Configuração principal ARCO S-tier"""
    
    def __init__(self):
        self.searchapi = SearchAPIConfig()
        self.verticals = VerticalConfig()

# Global config instance
config = ARCOConfig()

# Helper functions
def get_config() -> ARCOConfig:
    """Get global configuration instance"""
    return config

def get_api_key() -> str:
    """Get SearchAPI key"""
    return config.searchapi.api_key

def get_keywords(vertical: str) -> List[str]:
    """Get keywords for a vertical"""
    vertical_map = {
        'dental_ortho': config.verticals.dental_ortho_keywords,
        'medical_spa': config.verticals.medical_spa_keywords,
        'real_estate_eu': config.verticals.real_estate_eu_keywords
    }
    return vertical_map.get(vertical, [])

def get_regions(region_set: str = 'europa') -> List[str]:
    """Get regions for a geographic area"""
    region_sets = {
        'europa': ['IE', 'GB', 'MT', 'CY'],
        'oceania': ['AU', 'NZ'],
        'north_america': ['US', 'CA']
    }
    return region_sets.get(region_set, config.searchapi.priority_regions)

if __name__ == "__main__":
    # Test configuration loading
    cfg = get_config()
    print(f"✅ API Key: {cfg.searchapi.api_key[:10]}...")
    print(f"✅ Priority Regions: {cfg.searchapi.priority_regions}")
    print(f"✅ Max Concurrent: {cfg.searchapi.max_concurrent}")
    print(f"✅ Europa Keywords: {get_keywords('real_estate_eu')[:3]}")
