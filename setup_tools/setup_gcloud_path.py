"""
🔧 GCLOUD PATH SETUP - PYTHON
============================
Script para configurar gcloud CLI no PATH do Windows
Funciona no terminal atual sem precisar de admin
"""

import os
import subprocess
import sys
from pathlib import Path

def print_header():
    print("🔧 GCLOUD CLI PATH SETUP")
    print("=" * 40)
    print("🎯 Configurando gcloud CLI para BigQuery")
    print("=" * 40)

def find_gcloud_installation():
    """Encontrar instalação do gcloud CLI"""
    print("🔍 Procurando Google Cloud SDK...")
    
    # Locais comuns de instalação
    search_paths = [
        Path(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')) / 'Google' / 'Cloud SDK' / 'google-cloud-sdk' / 'bin',
        Path(os.environ.get('ProgramFiles', 'C:\\Program Files')) / 'Google' / 'Cloud SDK' / 'google-cloud-sdk' / 'bin',
        Path(os.environ.get('USERPROFILE', '')) / 'AppData' / 'Local' / 'Google' / 'Cloud SDK' / 'google-cloud-sdk' / 'bin',
        Path(os.environ.get('LOCALAPPDATA', '')) / 'Google' / 'Cloud SDK' / 'google-cloud-sdk' / 'bin'
    ]
    
    for path in search_paths:
        gcloud_exe = path / 'gcloud.cmd'
        if gcloud_exe.exists():
            print(f"✅ Encontrado em: {path}")
            return str(path)
    
    return None

def test_gcloud_in_path():
    """Testar se gcloud está no PATH"""
    try:
        result = subprocess.run(['gcloud', '--version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        if result.returncode == 0:
            print("✅ gcloud já está no PATH e funcionando!")
            print(f"📋 Versão: {result.stdout.split()[3] if len(result.stdout.split()) > 3 else 'Detectada'}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError, IndexError):
        pass
    
    return False

def add_to_session_path(gcloud_path):
    """Adicionar ao PATH da sessão atual"""
    current_path = os.environ.get('PATH', '')
    
    if gcloud_path not in current_path:
        new_path = f"{current_path};{gcloud_path}"
        os.environ['PATH'] = new_path
        print(f"✅ Adicionado ao PATH da sessão: {gcloud_path}")
        return True
    else:
        print("✅ Já está no PATH da sessão")
        return False

def generate_path_commands(gcloud_path):
    """Gerar comandos para adicionar permanentemente ao PATH"""
    print("\n🔧 COMANDOS PARA ADICIONAR PERMANENTEMENTE:")
    print("=" * 50)
    
    print("\n📝 OPÇÃO 1: PowerShell (Execute como Administrador)")
    print("``` powershell")
    print(f'[Environment]::SetEnvironmentVariable("PATH", "$env:PATH;{gcloud_path}", "Machine")')
    print("```")
    
    print("\n📝 OPÇÃO 2: Command Prompt (Execute como Administrador)")
    print("``` cmd")
    print(f'setx PATH "%PATH%;{gcloud_path}" /M')
    print("```")
    
    print("\n📝 OPÇÃO 3: Manualmente via Interface Gráfica")
    print("1. Windows + R → sysdm.cpl")
    print("2. Aba 'Avançado' → 'Variáveis de Ambiente'")
    print("3. Em 'Variáveis do Sistema', selecione 'Path' → 'Editar'")
    print(f"4. Adicione: {gcloud_path}")

def download_gcloud():
    """Instruções para baixar gcloud CLI"""
    print("\n❌ Google Cloud SDK não encontrado!")
    print("📥 INSTALAÇÃO NECESSÁRIA:")
    print("=" * 30)
    print("🔗 Link: https://cloud.google.com/sdk/docs/install")
    print("📦 Installer: https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe")
    print("\n📋 PASSOS:")
    print("1. Baixe o installer acima")
    print("2. Execute o installer")
    print("3. Siga o wizard de instalação")
    print("4. Execute este script novamente")

def main():
    print_header()
    
    # Verificar se já está funcionando
    if test_gcloud_in_path():
        print("\n🚀 GCLOUD PRONTO!")
        print("🎯 Próximo passo: Configurar BigQuery")
        
        choice = input("\n🔧 Executar setup BigQuery agora? (y/n): ").lower()
        if choice == 'y':
            print("🚀 Executando BigQuery setup...")
            try:
                subprocess.run([sys.executable, 'bigquery_gcloud_setup.py'], check=True)
            except subprocess.CalledProcessError:
                print("❌ Erro no setup BigQuery")
        return
    
    # Procurar instalação
    gcloud_path = find_gcloud_installation()
    
    if not gcloud_path:
        download_gcloud()
        return
    
    # Adicionar ao PATH da sessão
    add_to_session_path(gcloud_path)
    
    # Testar novamente
    if test_gcloud_in_path():
        print("\n🎉 SUCESSO! gcloud configurado para esta sessão")
        
        # Gerar comandos para PATH permanente
        generate_path_commands(gcloud_path)
        
        print("\n🎯 PRÓXIMO PASSO: BIGQUERY SETUP")
        choice = input("\n🔧 Executar setup BigQuery agora? (y/n): ").lower()
        if choice == 'y':
            print("🚀 Executando BigQuery setup...")
            try:
                subprocess.run([sys.executable, 'bigquery_gcloud_setup.py'], check=True)
            except subprocess.CalledProcessError:
                print("❌ Erro no setup BigQuery")
    else:
        print("❌ Erro ao configurar gcloud")
        generate_path_commands(gcloud_path)

if __name__ == "__main__":
    main()
