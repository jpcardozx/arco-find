#!/usr/bin/env python3
"""
Script para limpar arquivos temporários e de debug do projeto ARCO.
Este script identifica e remove arquivos temporários, logs vazios e código de debug não essencial.
"""

import os
import shutil
import re
import logging
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Diretórios a serem ignorados (não serão limpos)
IGNORE_DIRS = ['.git', '.idea', '.venv', '__pycache__', '.kiro']

# Padrões de arquivos temporários
TEMP_FILE_PATTERNS = [
    r'\.tmp$',
    r'\.bak$',
    r'\.swp$',
    r'\.pyc$',
    r'\.DS_Store$',
    r'~$',
]

# Arquivos de log vazios que podem ser removidos
EMPTY_LOG_FILES = [
    'logs/arco_main.log',
    'logs/arco.main.log',
]

# Arquivos de debug específicos que podem ser removidos
DEBUG_FILES = [
    'legacy/debug.py',
    'legacy/step_debug.py',
    'archive/step_debug.py',
    'archive/demo_debug.py',
    'archive/blueprint21_debug.py',
]

def is_temp_file(filename):
    """Verifica se o arquivo corresponde a um padrão de arquivo temporário."""
    for pattern in TEMP_FILE_PATTERNS:
        if re.search(pattern, filename):
            return True
    return False

def remove_empty_logs():
    """Remove arquivos de log vazios."""
    for log_file in EMPTY_LOG_FILES:
        if os.path.exists(log_file) and os.path.getsize(log_file) == 0:
            try:
                os.remove(log_file)
                logger.info(f"Arquivo de log vazio removido: {log_file}")
            except Exception as e:
                logger.error(f"Erro ao remover arquivo de log {log_file}: {e}")

def remove_debug_files():
    """Remove arquivos de debug específicos."""
    for debug_file in DEBUG_FILES:
        if os.path.exists(debug_file):
            try:
                os.remove(debug_file)
                logger.info(f"Arquivo de debug removido: {debug_file}")
            except Exception as e:
                logger.error(f"Erro ao remover arquivo de debug {debug_file}: {e}")

def clean_temp_files():
    """Limpa arquivos temporários em todo o projeto."""
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=True):
        # Ignorar diretórios específicos
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        
        for filename in filenames:
            if is_temp_file(filename):
                file_path = os.path.join(dirpath, filename)
                try:
                    os.remove(file_path)
                    logger.info(f"Arquivo temporário removido: {file_path}")
                except Exception as e:
                    logger.error(f"Erro ao remover arquivo temporário {file_path}: {e}")

def clean_pycache_dirs():
    """Remove diretórios __pycache__ em todo o projeto."""
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    for dirpath, dirnames, _ in os.walk(root_dir, topdown=True):
        for dirname in dirnames:
            if dirname == '__pycache__':
                pycache_path = os.path.join(dirpath, dirname)
                try:
                    shutil.rmtree(pycache_path)
                    logger.info(f"Diretório __pycache__ removido: {pycache_path}")
                except Exception as e:
                    logger.error(f"Erro ao remover diretório __pycache__ {pycache_path}: {e}")

def main():
    """Função principal para executar a limpeza."""
    logger.info("Iniciando limpeza de arquivos temporários e de debug...")
    
    # Remover arquivos de log vazios
    remove_empty_logs()
    
    # Remover arquivos de debug específicos
    remove_debug_files()
    
    # Limpar arquivos temporários
    clean_temp_files()
    
    # Limpar diretórios __pycache__
    clean_pycache_dirs()
    
    logger.info("Limpeza concluída com sucesso!")

if __name__ == "__main__":
    main()