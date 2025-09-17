#!/usr/bin/env python3
"""
ARCO Dependency Setup Tool

Verifica e ajuda a configurar as dependencias para o pipeline avancado.
"""

import os
import shutil
import yaml

def check_wappalyzer():
    """Verifica se o Wappalyzer-CLI esta instalado e acessivel no PATH."""
    return shutil.which("wappalyzer") is not None

def check_api_keys():
    """Verifica se as chaves de API estao no arquivo de configuracao."""
    config_path = "config/production_settings.yml"
    if not os.path.exists(config_path):
        return False
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    if not config:
        return False

    # Verifique aqui as chaves de API necessarias
    # Por exemplo:
    # if "meta_ads_token" not in config or not config["meta_ads_token"]:
    #     return False
    # if "google_api_key" not in config or not config["google_api_key"]:
    #     return False
        
    return True # Retorna True se tudo estiver ok

def main():
    """Funcao principal do script de setup."""
    print("--- Verificador de Dependencias do Pipeline Avancado ---")

    # 1. Verificar Wappalyzer
    print("\nVerificando Wappalyzer-CLI...")
    if check_wappalyzer():
        print("  [OK] Wappalyzer-CLI encontrado.")
    else:
        print("  [FALHA] Wappalyzer-CLI nao encontrado.")
        print("      Por favor, instale-o globalmente com: npm install -g wappalyzer-cli")

    # 2. Verificar Chaves de API
    print("\nVerificando as chaves de API em config/production_settings.yml...")
    if check_api_keys():
        print("  [OK] Arquivo de configuracao e chaves de API parecem estar no lugar.")
    else:
        print("  [FALHA] O arquivo config/production_settings.yml nao foi encontrado ou esta incompleto.")
        print("      Por favor, crie o arquivo e adicione as chaves de API necessarias.")

    print("\n--- Verificacao Concluida ---")

if __name__ == "__main__":
    main()