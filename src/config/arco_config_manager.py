# src/config/arco_config_manager.py

import os
from dotenv import load_dotenv
from src.config.configuration import AppConfig, APIKeys, DatabaseConfig

class ARCOConfigManager:
    """
    Gerencia as configurações da aplicação, carregando-as de variáveis de ambiente.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ARCOConfigManager, cls).__new__(cls)
            cls._instance._config = None
        return cls._instance

    def load_config(self):
        """
        Carrega as configurações da aplicação a partir de variáveis de ambiente.
        """
        if self._config is None:
            load_dotenv() # Carrega variáveis do .env

            api_keys = APIKeys(
                google_ads=os.getenv("GOOGLE_ADS_API_KEY"),
                meta_business=os.getenv("META_BUSINESS_API_KEY"),
                google_pagespeed=os.getenv("GOOGLE_PAGESPEED_API_KEY")
            )

            database_config = DatabaseConfig(
                url=os.getenv("DATABASE_URL")
            )

            self._config = AppConfig(
                environment=os.getenv("APP_ENV", "development"),
                debug_mode=os.getenv("DEBUG_MODE", "False").lower() == "true",
                api_keys=api_keys,
                database=database_config
            )
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