# src/connectors/google_pagespeed_api.py

import requests
from src.config.arco_config_manager import ARCOConfigManager
from src.utils.logger import logger

class GooglePageSpeedAPI:
    BASE_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

    def __init__(self, api_key: str = None):
        if api_key:
            self.api_key = api_key
        else:
            self.config = ARCOConfigManager().get_config()
            self.api_key = self.config.get('pagespeed_key')
            if not self.api_key:
                logger.error("GOOGLE_PAGESPEED_API_KEY não configurada no .env")
                raise ValueError("GOOGLE_PAGESPEED_API_KEY é necessária para usar a API PageSpeed.")

    def analyze_url(self, url: str, strategy: str = "mobile") -> dict:
        """
        Alias para get_page_speed_score para compatibilidade
        """
        return self.get_page_speed_score(url, strategy)
    
    def get_page_speed_score(self, url: str, strategy: str = "desktop") -> dict:
        """
        Obtém o score de performance de uma URL usando a Google PageSpeed Insights API.
        
        Args:
            url (str): A URL da página a ser analisada.
            strategy (str): A estratégia de análise ('desktop' ou 'mobile').
            
        Returns:
            dict: Um dicionário contendo os resultados da API, ou um erro.
        """
        params = {
            "url": url,
            "key": self.api_key,
            "strategy": strategy
        }
        
        try:
            logger.info(f"Consultando PageSpeed Insights para URL: {url} com estratégia: {strategy}")
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status() # Levanta um HTTPError para códigos de status de erro (4xx ou 5xx)
            data = response.json()
            
            # Extrai o score de performance
            performance_score = data.get("lighthouseResult", {}).get("categories", {}).get("performance", {}).get("score")
            # O score da API é de 0 a 1, multiplicamos por 100 para obter de 0 a 100
            if performance_score is not None:
                performance_score = int(performance_score * 100)

            logger.info(f"PageSpeed Insights para {url} ({strategy}): Score = {performance_score}")
            return {"score": performance_score, "full_results": data}
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao consultar PageSpeed Insights para {url}: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Erro inesperado ao processar resposta da PageSpeed Insights para {url}: {e}")
            return {"error": str(e)}

# Exemplo de uso (para teste interno)
if __name__ == "__main__":
    # Para rodar este exemplo, você precisa de uma GOOGLE_PAGESPEED_API_KEY válida no seu arquivo .env
    # Crie um arquivo .env na raiz do projeto com:
    # GOOGLE_PAGESPEED_API_KEY=SUA_CHAVE_AQUI

    # Exemplo de URL para teste
    test_url = "https://www.google.com"

    try:
        pagespeed_api = GooglePageSpeedAPI()
        
        # Teste para desktop
        desktop_results = pagespeed_api.get_page_speed_score(test_url, strategy="desktop")
        if desktop_results.get("score") is not None:
            logger.info(f"Score de Performance Desktop para {test_url}: {desktop_results['score']}")
        else:
            logger.error(f"Não foi possível obter o score desktop: {desktop_results.get('error')}")

        # Teste para mobile
        mobile_results = pagespeed_api.get_page_speed_score(test_url, strategy="mobile")
        if mobile_results.get("score") is not None:
            logger.info(f"Score de Performance Mobile para {test_url}: {mobile_results['score']}")
        else:
            logger.error(f"Não foi possível obter o score mobile: {mobile_results.get('error')}")

    except ValueError as e:
        logger.error(f"Erro de configuração: {e}")
    except Exception as e:
        logger.error(f"Erro geral: {e}")
