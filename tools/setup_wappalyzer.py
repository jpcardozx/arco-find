#!/usr/bin/env python3
"""
🔧 ARCO Setup - Corrigir PATH do Wappalyzer no Windows

Detecta automaticamente onde o npm instalou o Wappalyzer-CLI e 
sugere como adicionar ao PATH do Windows.
"""

import os
import subprocess
import sys
from pathlib import Path

def detect_npm_global_path():
    """Detecta onde o npm instala executáveis globais."""
    try:
        result = subprocess.run(['npm', 'bin', '-g'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # Fallback: caminhos comuns no Windows
    user_home = Path.home()
    common_paths = [
        user_home / "AppData" / "Roaming" / "npm",
        user_home / "AppData" / "Local" / "npm",
        Path("C:/Program Files/nodejs"),
        Path("C:/Program Files (x86)/nodejs")
    ]
    
    for path in common_paths:
        if path.exists() and (path / "wappalyzer.cmd").exists():
            return str(path)
    
    return None

def check_wappalyzer_in_path():
    """Verifica se wappalyzer está no PATH."""
    try:
        result = subprocess.run(['wappalyzer', '--help'], 
                              capture_output=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def suggest_path_fix():
    """Sugere como corrigir o PATH no Windows."""
    print("🔧 CORRIGINDO PATH DO WAPPALYZER-CLI\n")
    
    # 1. Verificar se já está no PATH
    if check_wappalyzer_in_path():
        print("✅ Wappalyzer-CLI já está funcionando!")
        return True
    
    print("❌ Wappalyzer-CLI não encontrado no PATH")
    
    # 2. Detectar onde está instalado
    npm_path = detect_npm_global_path()
    
    if npm_path:
        print(f"📂 Wappalyzer encontrado em: {npm_path}")
        print(f"\n🛠️ COMO CORRIGIR NO WINDOWS:")
        print(f"1. Pressione Win + R, digite 'sysdm.cpl' e pressione Enter")
        print(f"2. Clique em 'Variáveis de Ambiente...'")
        print(f"3. Na seção 'Variáveis do usuário', encontre 'Path' e clique 'Editar...'")
        print(f"4. Clique 'Novo' e adicione: {npm_path}")
        print(f"5. Clique 'OK' em todas as janelas")
        print(f"6. Reinicie o terminal ou computador")
        print(f"\n🧪 TESTE: Abra novo terminal e digite: wappalyzer --help")
        return False
    else:
        print("❌ Wappalyzer-CLI não encontrado!")
        print("\n📥 INSTALAÇÃO NECESSÁRIA:")
        print("1. npm install -g wappalyzer-cli")
        print("2. Reinicie o terminal")
        print("3. Execute este script novamente")
        return False

def install_python_wappalyzer():
    """Instala o wappalyzer Python como fallback."""
    print("\n💡 ALTERNATIVA: Instalando Wappalyzer Python...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'wappalyzer'], 
                      check=True)
        print("✅ Wappalyzer Python instalado!")
        print("⚠️ Nota: Funcionalidade limitada comparado ao CLI Node.js")
        return True
    except subprocess.CalledProcessError:
        print("❌ Falha ao instalar Wappalyzer Python")
        return False

def main():
    """Função principal."""
    print("🎯 ARCO SETUP - VERIFICAÇÃO DE DEPENDÊNCIAS\n")
    
    # Verificar Node.js
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Node.js: {result.stdout.decode().strip()}")
        else:
            print("❌ Node.js não encontrado")
            return
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Node.js não encontrado - instale em https://nodejs.org")
        return
    
    # Verificar npm
    try:
        # Tentar npm direto primeiro
        result = subprocess.run(['npm', '--version'], 
                              capture_output=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ npm: {result.stdout.decode().strip()}")
        else:
            # Tentar com caminho completo do Node.js
            node_path = subprocess.run(['where', 'node'], 
                                     capture_output=True, text=True).stdout.strip()
            if node_path:
                npm_path = node_path.replace('node.exe', 'npm.cmd')
                result = subprocess.run([npm_path, '--version'], 
                                      capture_output=True, timeout=5)
                if result.returncode == 0:
                    print(f"✅ npm: {result.stdout.decode().strip()}")
                else:
                    print("❌ npm não encontrado")
                    return
            else:
                print("❌ npm não encontrado")
                return
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ npm não encontrado")
        return
    
    # Verificar/corrigir Wappalyzer
    if not suggest_path_fix():
        print("\n💾 Enquanto isso, instalar fallback Python?")
        choice = input("Digite 'y' para instalar Wappalyzer Python: ").lower()
        if choice in ['y', 'yes', 's', 'sim']:
            install_python_wappalyzer()

if __name__ == "__main__":
    main()
