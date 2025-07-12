# src/config/configuration.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class APIKeys:
    google_ads: Optional[str] = None
    meta_business: Optional[str] = None
    google_pagespeed: Optional[str] = None
    # Adicione outras chaves de API conforme necessário

@dataclass
class DatabaseConfig:
    url: Optional[str] = None
    # Adicione outras configurações de banco de dados

@dataclass
class AppConfig:
    environment: str = "development"
    debug_mode: bool = False
    api_keys: APIKeys = APIKeys()
    database: DatabaseConfig = DatabaseConfig()
    # Adicione outras configurações gerais da aplicação