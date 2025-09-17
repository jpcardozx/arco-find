#!/usr/bin/env python3
"""
ARCO Dependency Check

Função para verificar se as dependências do pipeline avançado estão prontas.
Se não estiverem, sugere usar o pipeline standard.
"""

import os
import shutil
import yaml
import subprocess

def check_wappalyzer_cli():
    """Verifica se Wappalyzer-CLI está funcionando."""
    try:
        result = subprocess.run(['wappalyzer', '--help'], 
                              capture_output=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def check_python_wappalyzer():
    """Verifica se o pacote Python wappalyzer está disponível."""
    try:
        import wappalyzer
        return True
    except ImportError:
        return False

def check_advanced_dependencies():
    """Verifica as dependências e retorna True se estiverem prontas, False caso contrário."""
    
    print("🔍 Verificando dependências do pipeline avançado...")
    
    # Verificar Wappalyzer-CLI primeiro
    if check_wappalyzer_cli():
        print("✅ Wappalyzer-CLI encontrado e funcionando!")
        return True
    
    print("❌ Wappalyzer-CLI não encontrado no PATH")
    
    # Verificar fallback Python
    if check_python_wappalyzer():
        print("⚠️ Usando Wappalyzer Python como fallback (funcionalidade limitada)")
        return True
    
    print("❌ Nenhuma versão do Wappalyzer disponível")
    print("\n💡 RECOMENDAÇÃO:")
    print("Use o pipeline 'standard' que é 100% funcional sem dependências externas:")
    print("python main.py standard --domains kotn.com")
    
    return False

def suggest_wappalyzer_setup():
    """Sugere como instalar/configurar Wappalyzer."""
    print("\n🛠️ PARA USAR O PIPELINE AVANÇADO:")
    print("1. OPÇÃO RÁPIDA - Instalar Python Wappalyzer:")
    print("   pip install wappalyzer")
    print("\n2. OPÇÃO COMPLETA - Corrigir PATH do Wappalyzer-CLI:")
    print("   python tools/setup_wappalyzer.py")
    print("\n3. OPÇÃO IMEDIATA - Usar pipeline standard:")
    print("   python main.py standard --domains seus_domains")

if __name__ == "__main__":
    if not check_advanced_dependencies():
        suggest_wappalyzer_setup()
