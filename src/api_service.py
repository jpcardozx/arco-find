"""
ARCO API Service - Serviço centralizado para chamadas de API
Implementa caching, retry logic e rate limiting consistente
"""

import asyncio
import aiohttp
import json
import time
import logging
import os
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
import hashlib
import ssl
import certifi
from functools import wraps

# Configuração de logging
logger = logging.getLogger(__name__)

class APIRateLimiter:
    """Implementa rate limiting para APIs"""
    
    def __init__(self, calls_per_second: float = 1.0, max_concurrent: int = 5):
        self.calls_per_second = calls_per_second
        self.interval = 1.0 / calls_per_second
        self.max_concurrent = max_concurrent
        self.last_call_time = 0
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def acquire(self):
        """Adquire permissão para fazer uma chamada de API"""
        await self.semaphore.acquire()
        
        current_time = time.time()
        time_since_last = current_time - self.last_call_time
        
        if time_since_last < self.interval:
            await asyncio.sleep(self.interval - time_since_last)
        
        self.last_call_time = time.time()
    
    def release(self):
        """Libera o semáforo após a chamada"""
        self.semaphore.release()

class APICache:
    """Sistema de cache para respostas de API"""
    
    def __init__(self, cache_dir: str = "cache", ttl_seconds: int = 86400):
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_seconds
        
        # Cria diretório de cache se não existir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, url: str, params: Dict) -> str:
        """Gera uma chave de cache única baseada na URL e parâmetros"""
        cache_data = f"{url}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Retorna o caminho completo para o arquivo de cache"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, url: str, params: Dict) -> Optional[Dict]:
        """Recupera dados do cache se disponíveis e válidos"""
        cache_key = self._get_cache_key(url, params)
        cache_path = self._get_cache_path(cache_key)
        
        if os.path.exists(cache_path):
            try:
                # Verifica se o cache ainda é válido
                file_mtime = os.path.getmtime(cache_path)
                file_age = time.time() - file_mtime
                
                if file_age <= self.ttl_seconds:
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                else:
                    logger.debug(f"Cache expirado para {url}")
            except Exception as e:
                logger.warning(f"Erro ao ler cache: {e}")
        
        return None
    
    def set(self, url: str, params: Dict, data: Dict):
        """Salva dados no cache"""
        cache_key = self._get_cache_key(url, params)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
            logger.debug(f"Cache salvo para {url}")
        except Exception as e:
            logger.warning(f"Erro ao salvar cache: {e}")

class APIService:
    """Serviço centralizado para gerenciar chamadas de API"""
    
    def __init__(self, 
                 cache_enabled: bool = True, 
                 cache_ttl: int = 86400,
                 max_retries: int = 3,
                 retry_delay: float = 1.0):
        
        # Configurações
        self.cache_enabled = cache_enabled
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Componentes
        self.cache = APICache(ttl_seconds=cache_ttl)
        self.rate_limiters = {}
        self.session = None
        self._ssl_context = ssl.create_default_context(cafile=certifi.where())
    
    async def __aenter__(self):
        """Context manager entry"""
        connector = aiohttp.TCPConnector(ssl=self._ssl_context, limit=20)
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': 'ARCO-APIService/1.0'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()
    
    def register_api(self, api_name: str, calls_per_second: float = 1.0, max_concurrent: int = 5):
        """Registra uma nova API com suas configurações de rate limiting"""
        self.rate_limiters[api_name] = APIRateLimiter(
            calls_per_second=calls_per_second,
            max_concurrent=max_concurrent
        )
        logger.info(f"API registrada: {api_name} ({calls_per_second} calls/s, max {max_concurrent} concurrent)")
    
    async def query(self, 
                   api_name: str, 
                   url: str, 
                   params: Dict = None, 
                   method: str = "GET",
                   use_cache: bool = True,
                   response_processor: Callable = None) -> Dict:
        """
        Executa uma query para uma API com caching, rate limiting e retry
        
        Args:
            api_name: Nome da API registrada
            url: URL da requisição
            params: Parâmetros da requisição
            method: Método HTTP (GET, POST, etc)
            use_cache: Se deve usar cache para esta requisição
            response_processor: Função opcional para processar a resposta
            
        Returns:
            Dict com a resposta da API ou erro
        """
        if not self.session:
            raise RuntimeError("APIService não inicializado. Use 'async with APIService() as service:'")
        
        if api_name not in self.rate_limiters:
            logger.warning(f"API {api_name} não registrada. Registrando com configuração padrão.")
            self.register_api(api_name)
        
        rate_limiter = self.rate_limiters[api_name]
        params = params or {}
        
        # Tenta recuperar do cache
        if self.cache_enabled and use_cache and method.upper() == "GET":
            cached_data = self.cache.get(url, params)
            if cached_data:
                logger.debug(f"Cache hit para {url}")
                return {
                    'data': cached_data,
                    'from_cache': True,
                    'success': True
                }
        
        # Prepara para fazer a requisição
        result = {
            'success': False,
            'from_cache': False,
            'error': None,
            'data': None,
            'status': None
        }
        
        # Implementa retry logic
        for attempt in range(self.max_retries):
            try:
                # Aplica rate limiting
                await rate_limiter.acquire()
                
                try:
                    # Executa a requisição
                    if method.upper() == "GET":
                        async with self.session.get(url, params=params) as response:
                            result['status'] = response.status
                            
                            if response.status == 200:
                                data = await response.json()
                                
                                # Processa a resposta se necessário
                                if response_processor:
                                    data = response_processor(data)
                                
                                result['data'] = data
                                result['success'] = True
                                
                                # Salva no cache
                                if self.cache_enabled and use_cache:
                                    self.cache.set(url, params, data)
                                
                                return result
                            
                            elif response.status == 429:  # Rate limit
                                error_text = await response.text()
                                logger.warning(f"Rate limit atingido para {api_name}: {error_text}")
                                result['error'] = f"Rate limit: {error_text}"
                                
                                # Espera mais tempo antes do próximo retry
                                await asyncio.sleep(self.retry_delay * (2 ** attempt))
                                continue
                                
                            else:
                                error_text = await response.text()
                                logger.error(f"Erro na API {api_name}: {response.status} - {error_text}")
                                result['error'] = f"API Error: {response.status} - {error_text}"
                    
                    elif method.upper() == "POST":
                        # Implementação para POST
                        async with self.session.post(url, json=params) as response:
                            result['status'] = response.status
                            
                            if response.status == 200:
                                data = await response.json()
                                
                                if response_processor:
                                    data = response_processor(data)
                                
                                result['data'] = data
                                result['success'] = True
                                return result
                            
                            elif response.status == 429:  # Rate limit
                                error_text = await response.text()
                                logger.warning(f"Rate limit atingido para {api_name}: {error_text}")
                                result['error'] = f"Rate limit: {error_text}"
                                await asyncio.sleep(self.retry_delay * (2 ** attempt))
                                continue
                                
                            else:
                                error_text = await response.text()
                                logger.error(f"Erro na API {api_name}: {response.status} - {error_text}")
                                result['error'] = f"API Error: {response.status} - {error_text}"
                
                finally:
                    # Sempre libera o rate limiter
                    rate_limiter.release()
                
                # Se chegou aqui com erro mas não é rate limit, tenta retry
                if not result['success'] and result['status'] != 429:
                    logger.info(f"Retry {attempt+1}/{self.max_retries} para {url}")
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                
                # Se chegou aqui com sucesso, retorna
                if result['success']:
                    return result
            
            except asyncio.TimeoutError:
                logger.warning(f"Timeout na requisição para {api_name} (tentativa {attempt+1})")
                result['error'] = "Timeout"
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
            
            except Exception as e:
                logger.error(f"Erro na requisição para {api_name}: {str(e)}")
                result['error'] = str(e)
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
        
        # Se chegou aqui, todas as tentativas falharam
        logger.error(f"Todas as {self.max_retries} tentativas falharam para {url}")
        return result

# Exemplo de uso:
async def example_usage():
    async with APIService() as api_service:
        # Registra APIs com diferentes limites
        api_service.register_api("google_places", calls_per_second=0.5, max_concurrent=3)
        api_service.register_api("pagespeed", calls_per_second=0.2, max_concurrent=2)
        
        # Exemplo de chamada para Google Places API
        places_result = await api_service.query(
            api_name="google_places",
            url="https://maps.googleapis.com/maps/api/place/textsearch/json",
            params={
                'query': 'restaurante São Paulo',
                'key': os.getenv('GOOGLE_API_KEY')
            }
        )
        
        if places_result['success']:
            print(f"Places API success: {len(places_result['data'].get('results', []))} results")
        else:
            print(f"Places API error: {places_result['error']}")
        
        # Exemplo de chamada para PageSpeed API
        pagespeed_result = await api_service.query(
            api_name="pagespeed",
            url="https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
            params={
                'url': 'https://www.example.com',
                'key': os.getenv('GOOGLE_API_KEY'),
                'strategy': 'mobile'
            }
        )
        
        if pagespeed_result['success']:
            print(f"PageSpeed API success: Score {pagespeed_result['data'].get('lighthouseResult', {}).get('categories', {}).get('performance', {}).get('score', 0) * 100:.0f}/100")
        else:
            print(f"PageSpeed API error: {pagespeed_result['error']}")

if __name__ == "__main__":
    # Configuração de logging para testes
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Executa exemplo
    asyncio.run(example_usage())