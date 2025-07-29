"""
🔧 BIGQUERY SETUP SEM ADMIN - SOLUÇÃO ALTERNATIVA
================================================
Configura BigQuery usando gcloud da sessão atual
Não requer privilégios de administrador
"""

import os
import subprocess
import sys
import json
import time
from pathlib import Path

def print_header():
    print("🔧 BIGQUERY SETUP - SEM ADMIN")
    print("=" * 45)
    print("🎯 Configuração BigQuery sem privilégios admin")
    print("💡 Usando gcloud da sessão atual")
    print("=" * 45)

def setup_session_gcloud():
    """Configurar gcloud para sessão atual"""
    print("🔧 Configurando gcloud para esta sessão...")
    
    # Path do gcloud
    gcloud_path = r"C:\Users\João Pedro Cardozo\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"
    
    # Adicionar ao PATH da sessão
    current_path = os.environ.get('PATH', '')
    if gcloud_path not in current_path:
        os.environ['PATH'] = f"{current_path};{gcloud_path}"
        print(f"✅ Adicionado ao PATH da sessão: {gcloud_path}")
    
    return gcloud_path

def test_gcloud():
    """Testar se gcloud funciona"""
    print("🧪 Testando gcloud...")
    
    try:
        result = subprocess.run(['gcloud', '--version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        if result.returncode == 0:
            version_info = result.stdout.split('\n')[0]
            print(f"✅ gcloud funcionando: {version_info}")
            return True
        else:
            print(f"❌ Erro gcloud: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ gcloud não encontrado no PATH")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Timeout ao testar gcloud")
        return False

def gcloud_auth():
    """Fazer login no Google Cloud"""
    print("🔑 Fazendo login no Google Cloud...")
    
    try:
        # Verificar se já está logado
        result = subprocess.run(['gcloud', 'auth', 'list'], 
                              capture_output=True, 
                              text=True)
        
        if "ACTIVE" in result.stdout:
            print("✅ Já logado no Google Cloud")
            return True
        
        # Fazer login
        print("🌐 Abrindo navegador para login...")
        result = subprocess.run(['gcloud', 'auth', 'login'], 
                              timeout=120)
        
        if result.returncode == 0:
            print("✅ Login realizado com sucesso")
            return True
        else:
            print("❌ Erro no login")
            return False
            
    except Exception as e:
        print(f"❌ Erro no auth: {e}")
        return False

def create_or_select_project():
    """Criar ou selecionar projeto"""
    print("📁 Configurando projeto Google Cloud...")
    
    try:
        # Listar projetos existentes
        result = subprocess.run(['gcloud', 'projects', 'list'], 
                              capture_output=True, 
                              text=True)
        
        if result.returncode == 0 and result.stdout:
            print("📋 Projetos existentes encontrados:")
            lines = result.stdout.split('\n')
            projects = []
            for line in lines[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        projects.append(parts[0])
                        print(f"  • {parts[0]}")
            
            if projects:
                choice = input(f"\n🔧 Usar projeto existente? (1-{len(projects)}) ou 'n' para criar novo: ")
                
                if choice.isdigit() and 1 <= int(choice) <= len(projects):
                    selected_project = projects[int(choice) - 1]
                    
                    # Configurar projeto
                    result = subprocess.run(['gcloud', 'config', 'set', 'project', selected_project])
                    if result.returncode == 0:
                        print(f"✅ Projeto configurado: {selected_project}")
                        return selected_project
        
        # Criar novo projeto
        project_id = f"arco-pipeline-{int(time.time())}"
        print(f"🆕 Criando novo projeto: {project_id}")
        
        result = subprocess.run(['gcloud', 'projects', 'create', project_id, 
                               '--name=ARCO Pipeline'])
        
        if result.returncode == 0:
            # Configurar como projeto ativo
            subprocess.run(['gcloud', 'config', 'set', 'project', project_id])
            print(f"✅ Projeto criado e configurado: {project_id}")
            return project_id
        else:
            print("❌ Erro ao criar projeto")
            return None
            
    except Exception as e:
        print(f"❌ Erro no projeto: {e}")
        return None

def enable_apis(project_id):
    """Habilitar APIs necessárias"""
    print("🔌 Habilitando APIs do BigQuery...")
    
    apis = [
        'bigquery.googleapis.com',
        'bigquerystorage.googleapis.com'
    ]
    
    for api in apis:
        print(f"🔧 Habilitando {api}...")
        try:
            result = subprocess.run(['gcloud', 'services', 'enable', api], 
                                  timeout=60)
            if result.returncode == 0:
                print(f"✅ {api} habilitada")
            else:
                print(f"⚠️ Erro ao habilitar {api}")
        except subprocess.TimeoutExpired:
            print(f"⚠️ Timeout ao habilitar {api}")

def create_service_account(project_id):
    """Criar service account"""
    print("👤 Criando service account...")
    
    sa_name = "arco-bigquery"
    sa_email = f"{sa_name}@{project_id}.iam.gserviceaccount.com"
    
    try:
        # Criar service account
        result = subprocess.run([
            'gcloud', 'iam', 'service-accounts', 'create', sa_name,
            '--display-name=ARCO BigQuery Service Account'
        ])
        
        if result.returncode == 0:
            print("✅ Service account criada")
            
            # Adicionar roles
            roles = [
                'roles/bigquery.admin',
                'roles/bigquery.dataEditor',
                'roles/bigquery.user'
            ]
            
            for role in roles:
                subprocess.run([
                    'gcloud', 'projects', 'add-iam-policy-binding', project_id,
                    '--member=serviceAccount:' + sa_email,
                    '--role=' + role
                ])
            
            print("✅ Roles adicionadas ao service account")
            
            # Criar chave JSON
            key_path = Path(__file__).parent.parent / 'pipeline_optimized' / 'credentials' / 'credentials.json'
            key_path.parent.mkdir(parents=True, exist_ok=True)
            
            result = subprocess.run([
                'gcloud', 'iam', 'service-accounts', 'keys', 'create',
                str(key_path),
                '--iam-account=' + sa_email
            ])
            
            if result.returncode == 0:
                print(f"✅ Chave JSON criada: {key_path}")
                return str(key_path), sa_email
        
        return None, None
        
    except Exception as e:
        print(f"❌ Erro no service account: {e}")
        return None, None

def create_bigquery_dataset(project_id):
    """Criar dataset BigQuery"""
    print("📊 Criando dataset BigQuery...")
    
    dataset_name = "facebook_ads"
    
    try:
        result = subprocess.run([
            'gcloud', 'alpha', 'bq', 'datasets', 'create',
            dataset_name,
            '--location=us-central1',
            '--description=Facebook Ads data for ARCO pipeline'
        ])
        
        if result.returncode == 0:
            print(f"✅ Dataset criado: {dataset_name}")
            return dataset_name
        else:
            print("⚠️ Dataset pode já existir ou erro na criação")
            return dataset_name
            
    except Exception as e:
        print(f"❌ Erro no dataset: {e}")
        return None

def update_env_file(project_id, credentials_path):
    """Atualizar arquivo .env"""
    print("⚙️ Atualizando configuração...")
    
    env_path = Path(__file__).parent.parent / 'pipeline_optimized' / '.env'
    
    # Ler .env atual
    env_content = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_content[key] = value
    
    # Atualizar configurações BigQuery
    env_content['GOOGLE_CLOUD_PROJECT'] = project_id
    env_content['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    env_content['BIGQUERY_DATASET'] = 'facebook_ads'
    env_content['BIGQUERY_REGION'] = 'us-central1'
    
    # Escrever .env atualizado
    with open(env_path, 'w') as f:
        f.write("# ARCO Pipeline - Environment Configuration\n")
        f.write("ENVIRONMENT=production\n")
        f.write("DEBUG=false\n\n")
        
        f.write("# API Keys (Operacionais)\n")
        f.write(f"SEARCHAPI_KEY={env_content.get('SEARCHAPI_KEY', '3sgTQQBwGfmtBR1WBW61MgnU')}\n")
        f.write(f"PAGESPEED_KEY={env_content.get('PAGESPEED_KEY', 'AIzaSyDNo6ycjKNYfDBmbFbOLI7kk-A-teppPaE')}\n\n")
        
        f.write("# BigQuery (Configurado)\n")
        f.write(f"GOOGLE_CLOUD_PROJECT={project_id}\n")
        f.write(f"GOOGLE_APPLICATION_CREDENTIALS={credentials_path}\n")
        f.write("BIGQUERY_DATASET=facebook_ads\n")
        f.write("BIGQUERY_REGION=us-central1\n\n")
        
        f.write("# Pipeline Configuration\n")
        f.write("MAX_LEADS=5\n")
        f.write("QUALIFICATION_THRESHOLD=0.7\n")
        f.write("ICP_FOCUS=true\n")
    
    print(f"✅ Arquivo .env atualizado: {env_path}")

def test_bigquery_connection(project_id):
    """Testar conexão BigQuery"""
    print("🧪 Testando conexão BigQuery...")
    
    try:
        # Testar bq command
        result = subprocess.run(['gcloud', 'alpha', 'bq', 'query', 
                               '--use_legacy_sql=false',
                               '--format=json',
                               'SELECT 1 as test'], 
                              capture_output=True, 
                              text=True)
        
        if result.returncode == 0:
            print("✅ Conexão BigQuery funcionando!")
            return True
        else:
            print(f"⚠️ Erro no teste: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def main():
    print_header()
    
    # 1. Configurar gcloud na sessão
    setup_session_gcloud()
    
    # 2. Testar gcloud
    if not test_gcloud():
        print("❌ gcloud não funcionando. Verifique instalação.")
        return
    
    # 3. Fazer login
    if not gcloud_auth():
        print("❌ Erro no login. Tente novamente.")
        return
    
    # 4. Configurar projeto
    project_id = create_or_select_project()
    if not project_id:
        print("❌ Erro ao configurar projeto.")
        return
    
    # 5. Habilitar APIs
    enable_apis(project_id)
    
    # 6. Criar service account
    credentials_path, sa_email = create_service_account(project_id)
    if not credentials_path:
        print("❌ Erro ao criar service account.")
        return
    
    # 7. Criar dataset
    dataset_name = create_bigquery_dataset(project_id)
    
    # 8. Atualizar configuração
    update_env_file(project_id, credentials_path)
    
    # 9. Testar conexão
    if test_bigquery_connection(project_id):
        print("\n🎉 BIGQUERY CONFIGURADO COM SUCESSO!")
        print("=" * 50)
        print(f"📁 Projeto: {project_id}")
        print(f"📊 Dataset: {dataset_name}")
        print(f"🔑 Credentials: {credentials_path}")
        print(f"👤 Service Account: {sa_email}")
        
        print("\n🚀 PRÓXIMO PASSO:")
        print("cd ../pipeline_optimized")
        print("python run_pipeline.py")
        
    else:
        print("\n⚠️ BigQuery configurado mas teste falhou")
        print("💡 Pode funcionar depois da propagação das configurações")

if __name__ == "__main__":
    main()
