"""
🔑 CONFIGURAÇÃO DE APIs - PIPELINE INTEGRADO
==========================================
Configurações centralizadas para o pipeline ARCO
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar .env da pasta pipeline_optimized
pipeline_path = Path(__file__).parent.parent
env_path = pipeline_path / '.env'
load_dotenv(env_path)

# APIs Operacionais
SEARCHAPI_KEY = os.getenv('SEARCHAPI_KEY', '3sgTQQBwGfmtBR1WBW61MgnU')
PAGESPEED_KEY = os.getenv('PAGESPEED_KEY', 'AIzaSyDNo6ycjKNYfDBmbFbOLI7kk-A-teppPaE')

# BigQuery (opcional)
GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
BIGQUERY_DATASET = os.getenv('BIGQUERY_DATASET', 'facebook_ads')

# Configurações do Pipeline
PIPELINE_CONFIG = {
    'max_leads': 5,
    'qualification_threshold': 0.7,
    'icp_requirements': {
        'industries': ['legal', 'healthcare', 'real_estate', 'automotive', 'home_services'],
        'min_spend': 1000,
        'location_types': ['local', 'regional'],
        'business_size': ['smb', 'small_medium']
    },
    'p0_signals': {
        'performance_threshold': 0.6,
        'waste_threshold': 0.2,
        'urgency_threshold': 0.7
    }
}

# Validação de APIs
def validate_api_keys():
    """Validar se as chaves de API estão configuradas"""
    validation = {
        'searchapi': bool(SEARCHAPI_KEY),
        'pagespeed': bool(PAGESPEED_KEY),
        'bigquery': bool(GOOGLE_CLOUD_PROJECT and GOOGLE_APPLICATION_CREDENTIALS)
    }
    return validation

if __name__ == "__main__":
    print("🔑 Configuração de APIs - ARCO Pipeline")
    validation = validate_api_keys()
    
    for api, status in validation.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {api.upper()}: {'Configurado' if status else 'Não configurado'}")
