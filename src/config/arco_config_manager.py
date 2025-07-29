# src/config/arco_config_manager.py

import os
import logging
from dotenv import load_dotenv
from src.config.configuration import AppConfig, APIKeys, DatabaseConfig

logger = logging.getLogger(__name__)

class ARCOConfigManager:
    """
    Gerencia as configurações da aplicação, carregando-as de variáveis de ambiente
    com validação e logging de segurança.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ARCOConfigManager, cls).__new__(cls)
            cls._instance._config = None
        return cls._instance

    def _validate_api_key(self, key_name: str, key_value: str) -> bool:
        """
        Valida se uma chave API está presente e tem formato apropriado.
        """
        if not key_value:
            logger.warning(f"API key '{key_name}' not configured - engine functionality limited")
            return False
        
        if len(key_value) < 10:
            logger.warning(f"API key '{key_name}' appears too short - may be invalid")
            return False
            
        # Mask the key for logging (show only first/last few chars)
        masked_key = f"{key_value[:4]}...{key_value[-4:]}" if len(key_value) > 8 else "***"
        logger.info(f"API key '{key_name}' loaded: {masked_key}")
        return True

    def load_config(self):
        """
        Carrega as configurações da aplicação a partir de variáveis de ambiente
        com validação de segurança.
        """
        if self._config is None:
            load_dotenv() # Carrega variáveis do .env

            # Load and validate API keys
            google_ads_key = os.getenv("GOOGLE_ADS_API_KEY")
            meta_business_key = os.getenv("META_BUSINESS_API_KEY") 
            google_pagespeed_key = os.getenv("GOOGLE_PAGESPEED_API_KEY")

            self._validate_api_key("GOOGLE_ADS_API_KEY", google_ads_key)
            self._validate_api_key("META_BUSINESS_API_KEY", meta_business_key)
            self._validate_api_key("GOOGLE_PAGESPEED_API_KEY", google_pagespeed_key)

            api_keys = APIKeys(
                google_ads=google_ads_key,
                meta_business=meta_business_key,
                google_pagespeed=google_pagespeed_key
            )

            database_config = DatabaseConfig(
                url=os.getenv("DATABASE_URL")
            )

            environment = os.getenv("APP_ENV", "development")
            debug_mode = os.getenv("DEBUG_MODE", "False").lower() == "true"

            # Security validation for production
            if environment == "production":
                if not google_pagespeed_key:
                    logger.error("Production environment requires GOOGLE_PAGESPEED_API_KEY")
                if debug_mode:
                    logger.warning("Debug mode enabled in production - consider security implications")

            self._config = AppConfig(
                environment=environment,
                debug_mode=debug_mode,
                api_keys=api_keys,
                database=database_config
            )
            
            logger.info(f"Configuration loaded for environment: {environment}")
        return self._config

    def get_config(self) -> AppConfig:
        """
        Retorna a instância da configuração carregada.
        Carrega a configuração se ainda não tiver sido carregada.
        """
        if self._config is None:
            self.load_config()
        return self._config

# Exemplo de uso (para teste interno)
if __name__ == "__main__":
    # Crie um arquivo .env na raiz do projeto com:
    # GOOGLE_ADS_API_KEY=your_google_ads_key
    # META_BUSINESS_API_KEY=your_meta_business_key
    # DATABASE_URL=sqlite:///./test.db
    # APP_ENV=production
    # DEBUG_MODE=True

    config_manager = ARCOConfigManager()
    config = config_manager.get_config()

    print(f"Environment: {config.environment}")
    print(f"Debug Mode: {config.debug_mode}")
    print(f"Google Ads API Key: {config.api_keys.google_ads}")
    print(f"Database URL: {config.database.url}")