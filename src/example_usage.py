"""
ARCO Lead Pipeline - Exemplo de Uso dos Componentes Otimizados
Este script demonstra como utilizar os novos serviços de API e configuração
"""

import asyncio
import os
import logging
from datetime import datetime

# Importa os serviços otimizados
from config_service import config_service
from api_service import APIService

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def demonstrate_api_service():
    """Demonstra o uso do APIService com diferentes APIs"""
    logger.info("Demonstrando APIService...")
    
    # Obtém a API key do serviço de configuração
    api_key = config_service.get_api_key('google')
    if not api_key:
        logger.error("API key não configurada. Execute 'python src/config_service.py' primeiro.")
        return False
    
    async with APIService(cache_enabled=True) as api_service:
        # Registra as APIs com diferentes limites
        api_service.register_api("google_places", calls_per_second=0.5, max_concurrent=3)
        api_service.register_api("pagespeed", calls_per_second=0.2, max_concurrent=2)
        
        # 1. Exemplo: Google Places API
        logger.info("Consultando Google Places API...")
        places_result = await api_service.query(
            api_name="google_places",
            url="https://maps.googleapis.com/maps/api/place/textsearch/json",
            params={
                'query': 'restaurante São Paulo',
                'key': api_key
            }
        )
        
        if places_result['success']:
            places = places_result['data'].get('results', [])
            logger.info(f"✅ Places API: {len(places)} resultados encontrados")
            
            if places:
                # Mostra o primeiro resultado
                first_place = places[0]
                logger.info(f"Primeiro resultado: {first_place.get('name')}")
                logger.info(f"Endereço: {first_place.get('formatted_address')}")
                logger.info(f"Rating: {first_place.get('rating', 'N/A')}")
        else:
            logger.error(f"❌ Places API erro: {places_result['error']}")
        
        # 2. Exemplo: PageSpeed API (com cache)
        if places_result['success'] and places:
            # Usa o primeiro resultado para testar PageSpeed
            first_place = places[0]
            place_id = first_place.get('place_id')
            
            # Primeiro, obtém detalhes do lugar para pegar o website
            logger.info(f"Obtendo detalhes do lugar {place_id}...")
            details_result = await api_service.query(
                api_name="google_places",
                url="https://maps.googleapis.com/maps/api/place/details/json",
                params={
                    'place_id': place_id,
                    'fields': 'website',
                    'key': api_key
                }
            )
            
            if details_result['success'] and details_result['data'].get('result', {}).get('website'):
                website = details_result['data']['result']['website']
                logger.info(f"Website encontrado: {website}")
                
                # Agora analisa o website com PageSpeed
                logger.info(f"Analisando performance de {website}...")
                pagespeed_result = await api_service.query(
                    api_name="pagespeed",
                    url="https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
                    params={
                        'url': website,
                        'key': api_key,
                        'strategy': 'mobile'
                    }
                )
                
                if pagespeed_result['success']:
                    # Extrai métricas de performance
                    lighthouse = pagespeed_result['data'].get('lighthouseResult', {})
                    categories = lighthouse.get('categories', {})
                    performance = categories.get('performance', {}).get('score', 0) * 100
                    
                    logger.info(f"✅ PageSpeed API: Score de performance {performance:.0f}/100")
                    
                    # Verifica se veio do cache
                    if pagespeed_result.get('from_cache'):
                        logger.info("📦 Resultado obtido do cache")
                    
                    # Segunda chamada (deve vir do cache)
                    logger.info("Repetindo análise (deve usar cache)...")
                    repeat_result = await api_service.query(
                        api_name="pagespeed",
                        url="https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
                        params={
                            'url': website,
                            'key': api_key,
                            'strategy': 'mobile'
                        }
                    )
                    
                    if repeat_result.get('from_cache'):
                        logger.info("✅ Cache funcionando corretamente!")
                    else:
                        logger.warning("⚠️ Cache não funcionou como esperado")
                else:
                    logger.error(f"❌ PageSpeed API erro: {pagespeed_result['error']}")
            else:
                logger.warning("⚠️ Não foi possível obter o website do lugar")
    
    return True

def demonstrate_config_service():
    """Demonstra o uso do ConfigService"""
    logger.info("\nDemonstrando ConfigService...")
    
    # Mostra configurações atuais
    logger.info("Configurações carregadas:")
    logger.info(f"Ambiente: {config_service.config.environment}")
    logger.info(f"API Key configurada: {'Sim' if config_service.get_api_key() else 'Não'}")
    
    # Obtém configurações específicas
    target_leads = config_service.config.pipeline.default_target_leads
    min_score = config_service.config.pipeline.min_qualification_score
    locations = config_service.get_target_locations(limit=2)
    
    logger.info(f"Target leads: {target_leads}")
    logger.info(f"Score mínimo: {min_score}")
    logger.info(f"Localizações: {', '.join(locations)}")
    
    # Demonstra validação
    validation = config_service.validate_config()
    logger.info(f"Validação: {validation}")
    
    return True

async def main():
    """Função principal"""
    print("🚀 ARCO Lead Pipeline - Demonstração dos Componentes Otimizados")
    print("=" * 70)
    print("Este script demonstra o uso dos novos serviços de API e configuração")
    print()
    
    # Demonstra o serviço de configuração
    config_success = demonstrate_config_service()
    
    if config_success:
        # Demonstra o serviço de API
        await demonstrate_api_service()
    
    print("\n✅ Demonstração concluída!")
    print("Consulte o código fonte para ver como utilizar os componentes em seu projeto.")

if __name__ == "__main__":
    # Executa a demonstração
    asyncio.run(main())