#!/usr/bin/env python3
"""
🔒 ARCO Meta Ads Secure Engine
Implementação segura e bem estruturada para descoberta via Meta Ads API
"""

import os
import sys
import logging
import json
import requests
import time
from typing import Dict, List, Optional, Protocol
from datetime import datetime, timedelta
from dataclasses import dataclass
from abc import ABC, abstractmethod
import hashlib
from functools import wraps
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# ============================================================================
# Data Models
# ============================================================================

@dataclass
class ProspectData:
    """Modelo de dados para prospect"""
    company_name: str
    page_id: str
    website_url: str
    discovery_source: str
    industry: str
    country: str
    estimated_monthly_spend: int
    platforms_active: List[str]
    confidence_score: float
    metadata: Dict = None

@dataclass
class APIResponse:
    """Modelo de resposta de API"""
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    rate_limit_remaining: Optional[int] = None

# ============================================================================
# Protocols and Interfaces
# ============================================================================

class APIClientProtocol(Protocol):
    """Protocol para clientes de API"""
    
    def make_request(self, endpoint: str, params: Dict) -> APIResponse:
        """Fazer requisição para API"""
        ...

class CacheProtocol(Protocol):
    """Protocol para cache"""
    
    def get(self, key: str) -> Optional[Dict]:
        """Obter dados do cache"""
        ...
    
    def set(self, key: str, value: Dict, ttl: int = 3600) -> None:
        """Armazenar dados no cache"""
        ...

# ============================================================================
# Security and Configuration
# ============================================================================

class SecureConfig:
    """Gestão segura de configurações"""
    
    def __init__(self):
        self._validate_environment()
    
    def _validate_environment(self) -> None:
        """Validar variáveis de ambiente obrigatórias"""
        required_vars = [
            'META_ACCESS_TOKEN',
            'GOOGLE_PAGESPEED_API_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    @property
    def meta_access_token(self) -> str:
        """Token de acesso Meta (de variável de ambiente)"""
        token = os.getenv('META_ACCESS_TOKEN')
        if not token:
            raise ValueError("META_ACCESS_TOKEN not found in environment")
        return token
    
    @property
    def google_api_key(self) -> str:
        """Chave API Google (de variável de ambiente)"""
        key = os.getenv('GOOGLE_PAGESPEED_API_KEY')
        if not key:
            raise ValueError("GOOGLE_PAGESPEED_API_KEY not found in environment")
        return key

def rate_limit(calls_per_minute: int = 30):
    """Decorator para rate limiting"""
    def decorator(func):
        last_called = []
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove calls older than 1 minute
            last_called[:] = [call_time for call_time in last_called if now - call_time < 60]
            
            if len(last_called) >= calls_per_minute:
                sleep_time = 60 - (now - last_called[0])
                if sleep_time > 0:
                    logger.info(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
                    time.sleep(sleep_time)
                    last_called.clear()
            
            last_called.append(now)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def validate_input(func):
    """Decorator para validação de input"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Validar argumentos básicos
        for key, value in kwargs.items():
            if isinstance(value, str):
                # Sanitizar strings
                kwargs[key] = value.strip()[:1000]  # Limitar tamanho
        
        return func(*args, **kwargs)
    return wrapper

# ============================================================================
# Cache Implementation
# ============================================================================

class MemoryCache:
    """Cache em memória simples com TTL"""
    
    def __init__(self):
        self._cache: Dict[str, Dict] = {}
        self._timestamps: Dict[str, float] = {}
    
    def get(self, key: str) -> Optional[Dict]:
        """Obter dados do cache"""
        if key not in self._cache:
            return None
        
        # Verificar TTL
        if time.time() - self._timestamps[key] > 3600:  # 1 hora
            del self._cache[key]
            del self._timestamps[key]
            return None
        
        return self._cache[key]
    
    def set(self, key: str, value: Dict, ttl: int = 3600) -> None:
        """Armazenar dados no cache"""
        self._cache[key] = value
        self._timestamps[key] = time.time()
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """Gerar chave de cache"""
        data = json.dumps(kwargs, sort_keys=True)
        hash_obj = hashlib.md5(data.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"

# ============================================================================
# API Clients
# ============================================================================

class MetaAPIClient:
    """Cliente seguro para Meta Graph API"""
    
    def __init__(self, access_token: str, cache: CacheProtocol):
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
        self.cache = cache
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        })
    
    @rate_limit(calls_per_minute=200)  # Meta's actual rate limit
    def make_request(self, endpoint: str, params: Dict) -> APIResponse:
        """Fazer requisição segura para Meta API"""
        try:
            # Gerar chave de cache
            cache_key = self._generate_cache_key(endpoint, params)
            cached_result = self.cache.get(cache_key)
            
            if cached_result:
                logger.debug(f"Cache hit for {endpoint}")
                return APIResponse(success=True, data=cached_result)
            
            # Sanitizar parâmetros
            safe_params = self._sanitize_params(params)
            safe_params['access_token'] = self.access_token
            
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=safe_params, timeout=10)
            
            # Parse rate limit headers
            rate_limit_remaining = response.headers.get('X-App-Usage')
            
            if response.status_code == 200:
                data = response.json()
                # Cache successful responses
                self.cache.set(cache_key, data)
                return APIResponse(
                    success=True, 
                    data=data, 
                    rate_limit_remaining=rate_limit_remaining
                )
            elif response.status_code == 401:
                logger.error("Meta API: Unauthorized - Invalid access token")
                return APIResponse(success=False, error="Unauthorized")
            elif response.status_code == 429:
                logger.warning("Meta API: Rate limit exceeded")
                return APIResponse(success=False, error="Rate limited")
            else:
                logger.warning(f"Meta API error: {response.status_code} - {response.text[:200]}")
                return APIResponse(success=False, error=f"API error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.warning(f"Meta API timeout for {endpoint}")
            return APIResponse(success=False, error="Timeout")
        except requests.exceptions.RequestException as e:
            logger.error(f"Meta API request failed: {e}")
            return APIResponse(success=False, error=str(e))
    
    def _sanitize_params(self, params: Dict) -> Dict:
        """Sanitizar parâmetros da API"""
        safe_params = {}
        for key, value in params.items():
            if isinstance(value, str):
                # Remover caracteres perigosos
                safe_value = ''.join(c for c in value if c.isalnum() or c in ' -_.')
                safe_params[key] = safe_value[:100]  # Limitar tamanho
            elif isinstance(value, (int, float)):
                safe_params[key] = value
            elif isinstance(value, list):
                safe_params[key] = value[:10]  # Limitar tamanho da lista
        
        return safe_params
    
    def _generate_cache_key(self, endpoint: str, params: Dict) -> str:
        """Gerar chave de cache"""
        cache_data = {'endpoint': endpoint, 'params': params}
        data_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()

class PageSpeedAPIClient:
    """Cliente seguro para Google PageSpeed API"""
    
    def __init__(self, api_key: str, cache: CacheProtocol):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        self.cache = cache
        self.session = requests.Session()
    
    @rate_limit(calls_per_minute=60)  # Conservative rate limit
    @validate_input
    def analyze_url(self, url: str, strategy: str = 'mobile') -> APIResponse:
        """Analisar URL com PageSpeed API"""
        try:
            # Validar URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return APIResponse(success=False, error="Invalid URL")
            
            # Gerar chave de cache
            cache_key = f"pagespeed:{hashlib.md5(f'{url}:{strategy}'.encode()).hexdigest()}"
            cached_result = self.cache.get(cache_key)
            
            if cached_result:
                return APIResponse(success=True, data=cached_result)
            
            params = {
                'url': url,
                'key': self.api_key,
                'strategy': strategy,
                'category': ['performance'],
                'locale': 'en'
            }
            
            response = self.session.get(self.base_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                # Cache por 6 horas (dados de performance mudam lentamente)
                self.cache.set(cache_key, data, ttl=21600)
                return APIResponse(success=True, data=data)
            else:
                logger.warning(f"PageSpeed API error: {response.status_code}")
                return APIResponse(success=False, error=f"API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"PageSpeed API error: {e}")
            return APIResponse(success=False, error=str(e))

# ============================================================================
# Business Logic Services
# ============================================================================

class ProspectAnalyzer:
    """Serviço para análise de prospects"""
    
    # Pesos baseados em dados históricos (exemplo)
    SCORE_WEIGHTS = {
        'funding_signal': 0.25,
        'ad_activity': 0.30,
        'performance_issues': 0.25,
        'market_size': 0.20
    }
    
    def calculate_prospect_score(self, prospect_data: Dict) -> float:
        """Calcular score do prospect baseado em métricas objetivas"""
        try:
            scores = {
                'funding_signal': self._calculate_funding_score(prospect_data),
                'ad_activity': self._calculate_ad_activity_score(prospect_data),
                'performance_issues': self._calculate_performance_score(prospect_data),
                'market_size': self._calculate_market_score(prospect_data)
            }
            
            # Calcular score ponderado
            total_score = sum(
                scores[metric] * self.SCORE_WEIGHTS[metric] 
                for metric in scores
            )
            
            # Normalizar para 0-1
            return min(max(total_score, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating prospect score: {e}")
            return 0.0
    
    def _calculate_funding_score(self, data: Dict) -> float:
        """Score baseado em sinais de funding"""
        # Placeholder - implementar com dados reais
        return 0.5
    
    def _calculate_ad_activity_score(self, data: Dict) -> float:
        """Score baseado em atividade de ads"""
        # Placeholder - implementar com dados reais
        return 0.5
    
    def _calculate_performance_score(self, data: Dict) -> float:
        """Score baseado em problemas de performance"""
        # Placeholder - implementar com dados reais
        return 0.5
    
    def _calculate_market_score(self, data: Dict) -> float:
        """Score baseado em tamanho de mercado"""
        # Placeholder - implementar com dados reais
        return 0.5

# ============================================================================
# Main Engine
# ============================================================================

class MetaAdsSecureEngine:
    """Engine principal - orquestração de serviços"""
    
    def __init__(self, config: SecureConfig, cache: CacheProtocol = None):
        self.config = config
        self.cache = cache or MemoryCache()
        
        # Inicializar clientes de API
        self.meta_client = MetaAPIClient(config.meta_access_token, self.cache)
        self.pagespeed_client = PageSpeedAPIClient(config.google_api_key, self.cache)
        
        # Inicializar serviços
        self.analyzer = ProspectAnalyzer()
        
        logger.info("🔒 Meta Ads Secure Engine initialized")
    
    @validate_input
    def discover_prospects(self, industry: str, country: str, limit: int = 50) -> List[ProspectData]:
        """Descobrir prospects de forma segura"""
        try:
            prospects = []
            
            # Implementar descoberta real aqui
            # Por agora, retornar dados de fallback seguros
            prospects = self._generate_safe_fallback_data(industry, country, limit)
            
            logger.info(f"✅ Found {len(prospects)} prospects for {industry} in {country}")
            return prospects
            
        except Exception as e:
            logger.error(f"❌ Error discovering prospects: {e}")
            return []
    
    def _generate_safe_fallback_data(self, industry: str, country: str, limit: int) -> List[ProspectData]:
        """Gerar dados de fallback seguros (para demonstração)"""
        prospects = []
        
        for i in range(min(limit, 10)):  # Limitar a 10 para demo
            prospect = ProspectData(
                company_name=f"{industry.title()} Company {i+1}",
                page_id=f"safe_{industry}_{country}_{i}",
                website_url=f"https://example.com/{industry}_{i}",
                discovery_source="secure_fallback",
                industry=industry,
                country=country,
                estimated_monthly_spend=1000 + (i * 500),
                platforms_active=["Facebook", "Instagram"],
                confidence_score=0.7 + (i * 0.02),
                metadata={
                    "generated_at": datetime.now().isoformat(),
                    "engine_version": "secure_v1.0"
                }
            )
            prospects.append(prospect)
        
        return prospects

# ============================================================================
# Testing and Validation
# ============================================================================

def test_secure_engine():
    """Teste básico do engine seguro"""
    try:
        # Verificar se variáveis de ambiente estão configuradas
        if not os.getenv('META_ACCESS_TOKEN'):
            print("⚠️  META_ACCESS_TOKEN not set - using test mode")
            return
        
        config = SecureConfig()
        engine = MetaAdsSecureEngine(config)
        
        # Testar descoberta
        prospects = engine.discover_prospects("dental", "DE", limit=5)
        
        print(f"✅ Found {len(prospects)} prospects")
        
        if prospects:
            print("\n📋 Sample prospect:")
            prospect = prospects[0]
            print(f"   Company: {prospect.company_name}")
            print(f"   Industry: {prospect.industry}")
            print(f"   Country: {prospect.country}")
            print(f"   Confidence: {prospect.confidence_score:.2f}")
            print(f"   Source: {prospect.discovery_source}")
        
        return prospects
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return []

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run test
    test_secure_engine()
