#!/usr/bin/env python3
"""
Script de validação final para o projeto ARCO.

Este script executa uma validação completa do projeto ARCO,
verificando a estrutura de diretórios, importações, configurações e testes.
"""

import os
import sys
import logging
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("final_validation")

def run_command(command: List[str], timeout: int = 300) -> Tuple[int, str, str]:
    """
    Executar um comando e retornar o código de saída, stdout e stderr.
    
    Args:
        command: Comando a ser executado.
        timeout: Tempo limite em segundos.
        
    Returns:
        Tupla com código de saída, stdout e stderr.
    """
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(timeout=timeout)
        return process.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        process.kill()
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def clean_project():
    """
    Limpar arquivos temporários e caches do projeto.
    
    Returns:
        bool: True se a limpeza foi bem-sucedida, False caso contrário.
    """
    logger.info("Cleaning project...")
    
    # Executar script de limpeza
    returncode, stdout, stderr = run_command(["python", "cleanup_script.py"])
    
    if returncode == 0:
        logger.info("Project cleaned successfully")
        return True
    else:
        logger.error(f"Failed to clean project: {stderr}")
        return False


def run_validation():
    """
    Executar validação do projeto.
    
    Returns:
        bool: True se a validação foi bem-sucedida, False caso contrário.
    """
    logger.info("Running validation...")
    
    # Adicionar o diretório raiz ao sys.path
    root_dir = os.path.abspath(os.path.dirname(__file__))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)
    
    try:
        # Importar módulo de validação
        from arco.utils.validation import generate_validation_report
        
        # Gerar relatório de validação
        report = generate_validation_report()
        
        # Salvar relatório em arquivo
        with open("validation_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        
        logger.info("Validation report saved to validation_report.md")
        
        return True
    except ImportError as e:
        logger.error(f"Failed to import validation module: {e}")
        return False
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return False


def run_tests():
    """
    Executar testes do projeto.
    
    Returns:
        bool: True se os testes foram bem-sucedidos, False caso contrário.
    """
    logger.info("Running tests...")
    
    # Executar testes
    returncode, stdout, stderr = run_command(["pytest", "-v"])
    
    if returncode == 0:
        logger.info("All tests passed")
        return True
    else:
        logger.error(f"Some tests failed: {stderr}")
        return False


def main():
    """
    Função principal.
    
    Returns:
        int: Código de saída.
    """
    parser = argparse.ArgumentParser(description="Final validation for ARCO project")
    parser.add_argument("--skip-clean", action="store_true", help="Skip cleaning project")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    args = parser.parse_args()
    
    logger.info("Starting final validation...")
    
    # Limpar projeto
    if not args.skip_clean:
        if not clean_project():
            logger.warning("Project cleaning failed, continuing with validation")
    
    # Executar validação
    validation_success = run_validation()
    
    # Executar testes
    tests_success = True
    if not args.skip_tests:
        tests_success = run_tests()
    
    # Verificar resultados
    if validation_success and tests_success:
        logger.info("Final validation completed successfully")
        return 0
    else:
        logger.error("Final validation failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())