"""
ARCO Config Service - Serviço centralizado de configuração
Gerencia configurações do sistema e chaves de API de forma segura
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from pathlib import Path
import dotenv

# Carrega variáveis de ambiente do arquivo .env se existir
dotenv.load_dotenv()

# Configuração de logging
logger = logging.getLogger(__name__)

@dataclass
class APIConfig:
    """Configurações de APIs"""
    # Google APIs
    google_api_key: str = ""
    google_places_enabled: bool = True
    pagespeed_insights_enabled: bool = True
    
    # Rate limiting
    request_delay: float = 1.5
    batch_size: int = 8
    max_retries: int = 3
    
    # Configurações específicas por API
    api_rate_limits: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        "google_places": {"calls_per_second": 0.5, "max_concurrent": 3},
        "pagespeed": {"calls_per_second": 0.2, "max_concurrent": 2}
    })
    
    # Cache
    cache_enabled: bool = True
    cache_ttl_seconds: int = 86400  # 24 horas

@dataclass
class PipelineConfig:
    """Configurações do pipeline"""
    # Metas de leads
    default_target_leads: int = 15
    min_qualification_score: int = 65
    
    # Localizações prioritárias
    target_locations: List[str] = field(default_factory=lambda: [
        'São Paulo, SP, Brasil',
        'Rio de Janeiro, RJ, Brasil', 
        'Belo Horizonte, MG, Brasil',
        'Brasília, DF, Brasil',
        'Curitiba, PR, Brasil'
    ])
    
    # ICPs ativos
    active_icps: List[str] = field(default_factory=lambda: [
        'ecommerce_growth',
        'saas_early', 
        'services_professional',
        'dtc_niche'
    ])
    
    # Outputs
    save_json: bool = True
    save_csv: bool = True
    save_report: bool = True
    
    # Diretórios
    cache_dir: str = "cache"
    results_dir: str = "results"

@dataclass
class AppConfig:
    """Configuração completa da aplicação"""
    api: APIConfig = field(default_factory=APIConfig)
    pipeline: PipelineConfig = field(default_factory=PipelineConfig)
    environment: str = "development"
    debug: bool = False

class ConfigService:
    """Serviço centralizado de configuração"""
    
    def __init__(self, config_file: str = None):
        """
        Inicializa o serviço de configuração
        
        Args:
            config_file: Caminho para arquivo de configuração JSON (opcional)
        """
        self.config = AppConfig()
        self.config_file = config_file
        
        # Carrega configurações
        self._load_config()
    
    def _load_config(self):
        """Carrega configurações de múltiplas fontes na ordem correta"""
        
        # 1. Carrega defaults (já definidos nas dataclasses)
        
        # 2. Carrega do arquivo de configuração se existir
        if self.config_file and os.path.exists(self.config_file):
            self._load_from_file()
        
        # 3. Sobrescreve com variáveis de ambiente (maior prioridade)
        self._load_from_env()
        
        # 4. Cria diretórios necessários
        self._ensure_directories()
        
        # Log de configuração carregada
        logger.info(f"Configuração carregada: ambiente={self.config.environment}")
    
    def _load_from_file(self):
        """Carrega configurações de arquivo JSON"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
                # Atualiza API config
                if 'api' in config_data:
                    for key, value in config_data['api'].items():
                        if hasattr(self.config.api, key):
                            setattr(self.config.api, key, value)
                
                # Atualiza Pipeline config
                if 'pipeline' in config_data:
                    for key, value in config_data['pipeline'].items():
                        if hasattr(self.config.pipeline, key):
                            setattr(self.config.pipeline, key, value)
                
                # Atualiza config geral
                if 'environment' in config_data:
                    self.config.environment = config_data['environment']
                
                if 'debug' in config_data:
                    self.config.debug = config_data['debug']
                    
                logger.info(f"Configurações carregadas de {self.config_file}")
                
        except Exception as e:
            logger.error(f"Erro ao carregar configurações do arquivo {self.config_file}: {e}")
    
    def _load_from_env(self):
        """Carrega configurações de variáveis de ambiente"""
        
        # API Keys
        if os.getenv('GOOGLE_API_KEY'):
            self.config.api.google_api_key = os.getenv('GOOGLE_API_KEY')
        
        # Rate limiting
        if os.getenv('API_REQUEST_DELAY'):
            self.config.api.request_delay = float(os.getenv('API_REQUEST_DELAY'))
        
        if os.getenv('API_BATCH_SIZE'):
            self.config.api.batch_size = int(os.getenv('API_BATCH_SIZE'))
        
        if os.getenv('API_MAX_RETRIES'):
            self.config.api.max_retries = int(os.getenv('API_MAX_RETRIES'))
        
        # Pipeline
        if os.getenv('PIPELINE_TARGET_LEADS'):
            self.config.pipeline.default_target_leads = int(os.getenv('PIPELINE_TARGET_LEADS'))
        
        if os.getenv('PIPELINE_MIN_SCORE'):
            self.config.pipeline.min_qualification_score = int(os.getenv('PIPELINE_MIN_SCORE'))
        
        # Ambiente
        if os.getenv('ENVIRONMENT'):
            self.config.environment = os.getenv('ENVIRONMENT')
        
        if os.getenv('DEBUG'):
            self.config.debug = os.getenv('DEBUG').lower() in ('true', '1', 't', 'yes')
    
    def _ensure_directories(self):
        """Garante que os diretórios necessários existam"""
        os.makedirs(self.config.pipeline.cache_dir, exist_ok=True)
        os.makedirs(self.config.pipeline.results_dir, exist_ok=True)
    
    def save_config(self, file_path: str = None):
        """Salva configuração atual em arquivo JSON"""
        save_path = file_path or self.config_file
        
        if not save_path:
            logger.warning("Nenhum arquivo de configuração especificado para salvar")
            return False
        
        try:
            # Converte para dict
            config_dict = {
                'api': asdict(self.config.api),
                'pipeline': asdict(self.config.pipeline),
                'environment': self.config.environment,
                'debug': self.config.debug
            }
            
            # Remove a API key antes de salvar por segurança
            if 'google_api_key' in config_dict['api']:
                config_dict['api']['google_api_key'] = ""
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Configuração salva em {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar configuração: {e}")
            return False
    
    def get_api_key(self, service: str = 'google') -> str:
        """Retorna API key para serviço específico"""
        if service.lower() in ['google', 'places', 'pagespeed']:
            return self.config.api.google_api_key
        return ""
    
    def update_api_key(self, key: str, service: str = 'google'):
        """Atualiza API key"""
        if service.lower() in ['google', 'places', 'pagespeed']:
            self.config.api.google_api_key = key
    
    def get_api_rate_limit(self, api_name: str) -> Dict[str, float]:
        """Retorna configurações de rate limit para uma API específica"""
        return self.config.api.api_rate_limits.get(api_name, {
            "calls_per_second": 0.5, 
            "max_concurrent": 3
        })
    
    def get_target_locations(self, limit: int = None) -> List[str]:
        """Retorna localizações alvo"""
        locations = self.config.pipeline.target_locations
        if limit:
            return locations[:limit]
        return locations
    
    def validate_config(self) -> Dict[str, bool]:
        """Valida se as configurações estão corretas"""
        results = {
            'google_api_key': bool(self.config.api.google_api_key),
            'valid_api_key_length': len(self.config.api.google_api_key) > 30 if self.config.api.google_api_key else False,
            'directories_exist': os.path.exists(self.config.pipeline.cache_dir) and os.path.exists(self.config.pipeline.results_dir)
        }
        
        return results
    
    def print_config_status(self):
        """Imprime status das configurações"""
        
        print("🔧 CONFIGURAÇÕES DO SISTEMA")
        print("=" * 50)
        
        # Ambiente
        print(f"🌐 Ambiente: {self.config.environment}")
        print(f"🐞 Debug: {'Ativado' if self.config.debug else 'Desativado'}")
        
        # APIs
        validation = self.validate_config()
        print("\n📡 APIs:")
        print(f"   Google API Key: {'✅' if validation['google_api_key'] else '❌'}")
        if validation['google_api_key']:
            key_preview = f"{self.config.api.google_api_key[:5]}...{self.config.api.google_api_key[-4:]}"
            print(f"   Preview: {key_preview}")
        
        # Rate limiting
        print(f"   Request Delay: {self.config.api.request_delay}s")
        print(f"   Batch Size: {self.config.api.batch_size}")
        print(f"   Max Retries: {self.config.api.max_retries}")
        
        # Cache
        print(f"   Cache: {'✅' if self.config.api.cache_enabled else '❌'}")
        if self.config.api.cache_enabled:
            print(f"   Cache TTL: {self.config.api.cache_ttl_seconds // 3600} horas")
        
        # Pipeline
        print("\n🎯 Pipeline:")
        print(f"   Target Leads: {self.config.pipeline.default_target_leads}")
        print(f"   Min Score: {self.config.pipeline.min_qualification_score}")
        print(f"   Locations: {len(self.config.pipeline.target_locations)}")
        print(f"   ICPs Ativos: {len(self.config.pipeline.active_icps)}")
        
        # Diretórios
        print("\n📁 Diretórios:")
        print(f"   Cache: {self.config.pipeline.cache_dir}")
        print(f"   Results: {self.config.pipeline.results_dir}")
        
        print()

# Instância global
config_service = ConfigService()

def setup_google_api_key() -> str:
    """Helper para configurar Google API Key interativamente"""
    
    print("🔑 CONFIGURAÇÃO DA GOOGLE API KEY")
    print("=" * 40)
    print()
    
    current_key = config_service.get_api_key()
    if current_key and len(current_key) > 30:
        preview = f"{current_key[:5]}...{current_key[-4:]}"
        print(f"✅ API Key atual: {preview}")
        
        use_current = input("Usar API key atual? (y/n): ").lower().strip()
        if use_current == 'y':
            return current_key
    
    print("\n📋 Para obter uma Google API Key:")
    print("1. Acesse: https://console.cloud.google.com/")
    print("2. Crie um projeto ou selecione existente")
    print("3. Vá em 'APIs & Services' > 'Credentials'")
    print("4. Clique 'Create Credentials' > 'API Key'")
    print("5. Ative as APIs: Places API e PageSpeed Insights API")
    print()
    
    new_key = input("Cole sua Google API Key: ").strip()
    
    if len(new_key) < 30:
        print("❌ API Key muito curta. Verifique se copiou corretamente.")
        return None
    
    # Testa a key
    print("🧪 Testando API Key...")
    try:
        import asyncio
        import aiohttp
        
        async def test_key():
            async with aiohttp.ClientSession() as session:
                # Test Places API
                url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
                params = {
                    'query': 'restaurante São Paulo',
                    'key': new_key
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        print("✅ Google Places API: OK")
                        return True
                    else:
                        print(f"❌ Google Places API: Erro {response.status}")
                        return False
        
        if asyncio.run(test_key()):
            config_service.update_api_key(new_key)
            
            # Salva em .env para persistir
            env_path = Path('.env')
            if env_path.exists():
                with open(env_path, 'r') as f:
                    lines = f.readlines()
                
                # Atualiza ou adiciona a variável
                key_updated = False
                for i, line in enumerate(lines):
                    if line.startswith('GOOGLE_API_KEY='):
                        lines[i] = f'GOOGLE_API_KEY={new_key}\n'
                        key_updated = True
                        break
                
                if not key_updated:
                    lines.append(f'GOOGLE_API_KEY={new_key}\n')
                
                with open(env_path, 'w') as f:
                    f.writelines(lines)
            else:
                with open(env_path, 'w') as f:
                    f.write(f'GOOGLE_API_KEY={new_key}\n')
            
            print("✅ API Key configurada e salva com sucesso!")
            return new_key
        else:
            print("❌ Falha no teste da API Key")
            return None
            
    except Exception as e:
        print(f"⚠️ Não foi possível testar a API Key: {e}")
        print("API Key salva mesmo assim.")
        config_service.update_api_key(new_key)
        return new_key

if __name__ == "__main__":
    # Configuração de logging para testes
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Testa configuração
    config_service.print_config_status()
    
    # Setup interativo se necessário
    validation = config_service.validate_config()
    if not validation['google_api_key'] or not validation['valid_api_key_length']:
        print("\n⚠️ Google API Key não configurada ou inválida")
        setup_google_api_key()
        
        # Mostra configuração atualizada
        config_service.print_config_status()