# src/utils/logger.py

import logging
import os
from datetime import datetime

def setup_logging(log_level=logging.INFO, log_file=None):
    """
    Configura o sistema de logging para o Arco-Find.
    
    Args:
        log_level (int): Nível mínimo de logging (e.g., logging.INFO, logging.DEBUG).
        log_file (str, optional): Caminho para o arquivo de log. Se None, loga apenas no console.
    """
    # Cria o diretório de logs se um arquivo for especificado
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

    # Configura o logger raiz
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file) if log_file else logging.StreamHandler(),
            logging.StreamHandler() # Sempre loga no console também
        ]
    )
    
    # Retorna um logger específico para o módulo principal
    return logging.getLogger('arco-find')

# Configuração padrão do logger para uso em outros módulos
# Pode ser sobrescrito chamando setup_logging() novamente com parâmetros diferentes
LOG_FILE_PATH = os.path.join("logs", f"arco_find_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log")
logger = setup_logging(log_level=logging.INFO, log_file=LOG_FILE_PATH)

# Exemplo de uso (para teste interno)
if __name__ == "__main__":
    logger.info("Este é um log de informação.")
    logger.warning("Este é um log de aviso.")
    logger.error("Este é um log de erro.")
    logger.debug("Este é um log de depuração (se o nível for DEBUG).")
