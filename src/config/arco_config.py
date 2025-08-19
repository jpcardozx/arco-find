"""
ARCO SearchAPI - Configuration Management (S-tier)
==================================================

Gerenciamento de configuração usando pydantic e dotenv
para validação de tipos e configuração robusta.
"""

import os
from typing import List, Optional, Dict, Any
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

class SearchAPIConfig(BaseSettings):
    """Configuração do SearchAPI com validação"""
    
    # API Configuration
    api_key: str = Field(..., env='SEARCHAPI_KEY', description="SearchAPI (SerpAPI) key")
    base_url: str = Field(default="https://serpapi.com/api/v1/search", description="Base URL da API")
    
    # Rate Limiting
    rate_limit_delay: float = Field(default=1.0, env='SEARCHAPI_RATE_LIMIT', ge=0.1, le=5.0)
    max_retries: int = Field(default=3, env='SEARCHAPI_MAX_RETRIES', ge=1, le=10)
    timeout_seconds: int = Field(default=30, ge=5, le=120)
    
    # Regions Configuration
    priority_regions: List[str] = Field(default=["IE", "GB", "MT", "CY", "AU", "NZ"])
    backup_regions: List[str] = Field(default=["US", "CA"])
    
    # Qualification Thresholds
    min_ads_threshold: int = Field(default=3, ge=1, le=100)
    max_ads_threshold: int = Field(default=80, ge=10, le=500)
    recency_days: int = Field(default=30, ge=1, le=365)
    min_arco_score: int = Field(default=50, ge=0, le=100)
    
    # Pipeline Limits
    max_keywords_per_vertical: int = Field(default=4, ge=1, le=10)
    max_advertisers_per_batch: int = Field(default=30, ge=5, le=100)
    max_creatives_per_advertiser: int = Field(default=2, ge=1, le=5)
    
    # Environment
    environment: str = Field(default="development", env='ENVIRONMENT')
    debug: bool = Field(default=False)
    
    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v):
        if not v or v == 'your_serpapi_key_here':
            raise ValueError('SearchAPI key é obrigatória')
        return v
    
    @field_validator('priority_regions', mode='before')
    @classmethod
    def parse_priority_regions(cls, v):
        if isinstance(v, str):
            # Handle comma-separated string: "IE,GB,MT,CY"
            if ',' in v:
                return [region.strip() for region in v.split(',')]
            # Handle single region
            return [v.strip()]
        return v
    
    @field_validator('priority_regions')
    @classmethod
    def validate_regions(cls, v):
        valid_regions = {
            'IE', 'GB', 'MT', 'CY',  # Europa anglófona
            'AU', 'NZ',              # Oceania
            'US', 'CA'               # América do Norte
        }
        invalid = set(v) - valid_regions
        if invalid:
            raise ValueError(f'Regiões inválidas: {invalid}')
        return v
    
    class Config:
        env_file = '.env'
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables

class VerticalConfig(BaseSettings):
    """Configuração das verticais com keywords otimizadas"""
    
    # Dental/Orthodontic Keywords (Pain signals)
    dental_ortho_keywords: List[str] = Field(default=[
        "invisalign", "dental implants", "veneers", "clear aligners",
        "orthodontist", "cosmetic dentistry", "dental emergency"
    ])
    
    # Medical Spa/Aesthetic Keywords (High-intent)
    medical_spa_keywords: List[str] = Field(default=[
        "botox", "dermal filler", "laser hair removal", "coolsculpting",
        "medical spa", "aesthetic clinic", "anti aging"
    ])
    
    # Real Estate EU Keywords (Specific pain points)
    real_estate_eu_keywords: List[str] = Field(default=[
        "buyers agent", "property investment advice", "commercial property valuation",
        "estate planning", "property settlement", "mortgage broker",
        "lettings agent", "property portfolio", "conveyancing"
    ])
    
    # Home Services Keywords (Premium)
    home_services_keywords: List[str] = Field(default=[
        "solar installation", "roof replacement", "hvac installation",
        "electrical services", "plumbing emergency", "home renovation"
    ])
    
    @field_validator('dental_ortho_keywords', 'medical_spa_keywords', 'real_estate_eu_keywords')
    @classmethod
    def validate_keywords(cls, v):
        if len(v) < 3:
            raise ValueError('Cada vertical deve ter pelo menos 3 keywords')
        return v

class ARCOConfig:
    """Classe principal de configuração S-tier"""
    
    def __init__(self):
        self.searchapi = SearchAPIConfig()
        self.verticals = VerticalConfig()
        self._validate_configuration()
    
    def _validate_configuration(self):
        """Validação adicional da configuração"""
        
        # Verificar se keywords não estão duplicadas
        all_keywords = (
            self.verticals.dental_ortho_keywords +
            self.verticals.medical_spa_keywords +
            self.verticals.real_estate_eu_keywords +
            self.verticals.home_services_keywords
        )
        
        if len(all_keywords) != len(set(all_keywords)):
            duplicates = [k for k in all_keywords if all_keywords.count(k) > 1]
            raise ValueError(f'Keywords duplicadas encontradas: {duplicates}')
    
    def get_keywords_by_vertical(self, vertical: str) -> List[str]:
        """Retorna keywords para uma vertical específica"""
        
        mapping = {
            'dental_ortho': self.verticals.dental_ortho_keywords,
            'medical_spa': self.verticals.medical_spa_keywords,
            'real_estate_eu': self.verticals.real_estate_eu_keywords,
            'home_services': self.verticals.home_services_keywords
        }
        
        if vertical not in mapping:
            raise ValueError(f'Vertical {vertical} não encontrada. Disponíveis: {list(mapping.keys())}')
        
        return mapping[vertical][:self.searchapi.max_keywords_per_vertical]
    
    def get_regions_by_strategy(self, strategy: str = 'europa') -> List[str]:
        """Retorna regiões baseadas na estratégia"""
        
        strategies = {
            'europa': ['IE', 'GB', 'MT'],
            'oceania': ['AU', 'NZ'],
            'americas': ['US', 'CA'],
            'global': self.searchapi.priority_regions
        }
        
        return strategies.get(strategy, self.searchapi.priority_regions)
    
    def get_cost_limits(self) -> Dict[str, float]:
        """Retorna limites de custo por layer"""
        
        return {
            'layer1_max_calls': len(self.get_regions_by_strategy()) * self.searchapi.max_keywords_per_vertical,
            'layer2_max_calls': self.searchapi.max_advertisers_per_batch,
            'layer3_max_calls': self.searchapi.max_advertisers_per_batch * self.searchapi.max_creatives_per_advertiser,
            'estimated_cost_per_call': 0.05,
            'max_total_cost': 15.0  # $15 máximo por pipeline completo
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Exporta configuração para dict"""
        
        return {
            'searchapi': self.searchapi.dict(),
            'verticals': self.verticals.dict(),
            'cost_limits': self.get_cost_limits()
        }

# Singleton instance
config = ARCOConfig()

# Convenience functions
def get_config() -> ARCOConfig:
    """Retorna instância da configuração"""
    return config

def get_api_key() -> str:
    """Retorna API key validada"""
    return config.searchapi.api_key

def get_keywords(vertical: str) -> List[str]:
    """Retorna keywords para uma vertical"""
    return config.get_keywords_by_vertical(vertical)

def get_regions(strategy: str = 'europa') -> List[str]:
    """Retorna regiões para uma estratégia"""
    return config.get_regions_by_strategy(strategy)

# Exemplo de uso
if __name__ == "__main__":
    try:
        cfg = get_config()
        print("✅ Configuração carregada com sucesso!")
        print(f"API Key: {cfg.searchapi.api_key[:10]}...")
        print(f"Regiões Europa: {get_regions('europa')}")
        print(f"Keywords Real Estate EU: {get_keywords('real_estate_eu')}")
        print(f"Limites de custo: {cfg.get_cost_limits()}")
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
