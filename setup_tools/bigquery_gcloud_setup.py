"""
🚀 BIGQUERY SETUP COM GCLOUD CLI - ULTRA RÁPIDO
==============================================
Setup automatizado aproveitando gcloud CLI existente
Configuração completa em 5-10 minutos
"""

import os
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import uuid

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

@dataclass
class GCloudSetupConfig:
    """Configuração para setup com gcloud CLI"""
    project_id: str
    project_name: str
    region: str = "us-central1"
    dataset_id: str = "facebook_ads"
    service_account_name: str = "arco-bigquery"
    billing_account: str = ""

class GCloudBigQuerySetup:
    """Setup automatizado usando gcloud CLI"""
    
    def __init__(self):
        self.config: Optional[GCloudSetupConfig] = None
        self.credentials_dir = Path(__file__).parent / "credentials"
        self.credentials_dir.mkdir(exist_ok=True)
        
    def print_header(self, text: str):
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
        print(f"🚀 {text}")
        print(f"{'='*60}{Colors.ENDC}")
    
    def print_success(self, text: str):
        print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")
    
    def print_warning(self, text: str):
        print(f"{Colors.WARNING}⚠️ {text}{Colors.ENDC}")
    
    def print_error(self, text: str):
        print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")
    
    def print_info(self, text: str):
        print(f"{Colors.CYAN}ℹ️ {text}{Colors.ENDC}")
    
    def run_gcloud_command(self, command: List[str], capture_output: bool = True) -> Tuple[bool, str]:
        """Executar comando gcloud e retornar resultado"""
        try:
            print(f"{Colors.CYAN}🔧 Executando: {' '.join(command)}{Colors.ENDC}")
            
            result = subprocess.run(
                command, 
                capture_output=capture_output, 
                text=True, 
                timeout=60
            )
            
            if result.returncode == 0:
                return True, result.stdout.strip() if capture_output else "Success"
            else:
                error_msg = result.stderr.strip() if capture_output else f"Exit code: {result.returncode}"
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            return False, "Timeout - comando demorou mais de 60 segundos"
        except FileNotFoundError:
            return False, "gcloud CLI não encontrado no PATH"
        except Exception as e:
            return False, f"Erro inesperado: {e}"
    
    def check_gcloud_auth(self) -> bool:
        """Verificar se usuário está autenticado"""
        self.print_info("Verificando autenticação gcloud...")
        
        success, output = self.run_gcloud_command(['gcloud', 'auth', 'list', '--format=json'])
        
        if not success:
            self.print_error(f"Erro ao verificar auth: {output}")
            return False
        
        try:
            auth_accounts = json.loads(output)
            active_accounts = [acc for acc in auth_accounts if acc.get('status') == 'ACTIVE']
            
            if active_accounts:
                account = active_accounts[0]['account']
                self.print_success(f"Autenticado como: {account}")
                return True
            else:
                self.print_warning("Nenhuma conta ativa encontrada")
                return False
                
        except (json.JSONDecodeError, KeyError):
            self.print_error("Erro ao parsear resposta de auth")
            return False
    
    def authenticate_if_needed(self) -> bool:
        """Autenticar se necessário"""
        if self.check_gcloud_auth():
            return True
        
        self.print_info("Iniciando processo de autenticação...")
        print(f"{Colors.CYAN}🔐 Uma janela do navegador será aberta para login{Colors.ENDC}")
        
        success, output = self.run_gcloud_command(['gcloud', 'auth', 'login'], capture_output=False)
        
        if success:
            self.print_success("Autenticação concluída")
            return True
        else:
            self.print_error(f"Falha na autenticação: {output}")
            return False
    
    def get_billing_accounts(self) -> List[Dict]:
        """Listar contas de billing disponíveis"""
        self.print_info("Buscando contas de billing...")
        
        success, output = self.run_gcloud_command([
            'gcloud', 'billing', 'accounts', 'list', '--format=json'
        ])
        
        if not success:
            self.print_warning(f"Erro ao listar billing accounts: {output}")
            return []
        
        try:
            accounts = json.loads(output)
            return accounts
        except json.JSONDecodeError:
            return []
    
    def collect_project_info(self) -> GCloudSetupConfig:
        """Coletar informações do projeto"""
        self.print_header("CONFIGURAÇÃO DO PROJETO")
        
        # Project ID
        project_id = input(f"{Colors.CYAN}🏷️ Project ID (deixe vazio para gerar): {Colors.ENDC}").strip()
        if not project_id:
            project_id = f"arco-pipeline-{str(uuid.uuid4())[:8]}"
            self.print_success(f"Project ID gerado: {project_id}")
        
        # Project Name
        project_name = input(f"{Colors.CYAN}📝 Project Name [ARCO Pipeline]: {Colors.ENDC}").strip()
        if not project_name:
            project_name = "ARCO Pipeline"
        
        # Region
        print(f"\n{Colors.BLUE}🌍 Regiões recomendadas:{Colors.ENDC}")
        regions = {
            '1': 'us-central1 (Iowa - Baixo custo)',
            '2': 'us-east1 (South Carolina - Baixo custo)',
            '3': 'europe-west1 (Belgium)'
        }
        
        for key, value in regions.items():
            print(f"  {key}. {value}")
        
        region_choice = input(f"{Colors.CYAN}Escolha (1-3) [1]: {Colors.ENDC}").strip()
        region_map = {'1': 'us-central1', '2': 'us-east1', '3': 'europe-west1'}
        region = region_map.get(region_choice, 'us-central1')
        
        # Billing account
        billing_accounts = self.get_billing_accounts()
        billing_account = ""
        
        if billing_accounts:
            print(f"\n{Colors.BLUE}💳 Contas de billing disponíveis:{Colors.ENDC}")
            for i, account in enumerate(billing_accounts, 1):
                name = account.get('displayName', 'N/A')
                account_id = account.get('name', '').split('/')[-1]
                status = "ATIVA" if account.get('open', False) else "INATIVA"
                print(f"  {i}. {name} ({account_id}) - {status}")
            
            choice = input(f"{Colors.CYAN}Escolha a conta (1-{len(billing_accounts)}) [1]: {Colors.ENDC}").strip()
            try:
                idx = int(choice) - 1 if choice else 0
                if 0 <= idx < len(billing_accounts):
                    billing_account = billing_accounts[idx]['name'].split('/')[-1]
            except ValueError:
                pass
        
        if not billing_account:
            self.print_warning("Billing account não selecionada - será necessário configurar manualmente")
        
        return GCloudSetupConfig(
            project_id=project_id,
            project_name=project_name,
            region=region,
            billing_account=billing_account
        )
    
    def create_project(self, config: GCloudSetupConfig) -> bool:
        """Criar projeto no Google Cloud"""
        self.print_info(f"Criando projeto: {config.project_name}")
        
        success, output = self.run_gcloud_command([
            'gcloud', 'projects', 'create', config.project_id,
            f'--name={config.project_name}'
        ])
        
        if success:
            self.print_success(f"Projeto criado: {config.project_id}")
        else:
            if "already exists" in output.lower():
                self.print_warning(f"Projeto já existe: {config.project_id}")
                return True
            else:
                self.print_error(f"Erro ao criar projeto: {output}")
                return False
        
        return True
    
    def set_active_project(self, config: GCloudSetupConfig) -> bool:
        """Definir projeto ativo"""
        self.print_info(f"Definindo projeto ativo: {config.project_id}")
        
        success, output = self.run_gcloud_command([
            'gcloud', 'config', 'set', 'project', config.project_id
        ])
        
        if success:
            self.print_success("Projeto ativo definido")
            return True
        else:
            self.print_error(f"Erro ao definir projeto ativo: {output}")
            return False
    
    def link_billing_account(self, config: GCloudSetupConfig) -> bool:
        """Vincular conta de billing"""
        if not config.billing_account:
            self.print_warning("Billing account não configurada - faça manualmente no console")
            return True
        
        self.print_info("Vinculando billing account...")
        
        success, output = self.run_gcloud_command([
            'gcloud', 'billing', 'projects', 'link', config.project_id,
            f'--billing-account={config.billing_account}'
        ])
        
        if success:
            self.print_success("Billing account vinculada")
            return True
        else:
            self.print_warning(f"Erro ao vincular billing: {output}")
            self.print_warning("Configure billing manualmente no console")
            return True  # Não falha o setup por causa disso
    
    def enable_apis(self, config: GCloudSetupConfig) -> bool:
        """Habilitar APIs necessárias"""
        apis = [
            'bigquery.googleapis.com',
            'bigquerystorage.googleapis.com',
            'iam.googleapis.com',
            'cloudresourcemanager.googleapis.com'
        ]
        
        self.print_info("Habilitando APIs...")
        
        for api in apis:
            print(f"  📡 Habilitando {api}...")
            success, output = self.run_gcloud_command([
                'gcloud', 'services', 'enable', api, 
                f'--project={config.project_id}'
            ])
            
            if success:
                print(f"    ✅ {api}")
            else:
                print(f"    ❌ {api}: {output}")
                return False
        
        self.print_success("Todas APIs habilitadas")
        return True
    
    def create_service_account(self, config: GCloudSetupConfig) -> bool:
        """Criar service account"""
        self.print_info("Criando service account...")
        
        # Criar service account
        success, output = self.run_gcloud_command([
            'gcloud', 'iam', 'service-accounts', 'create', config.service_account_name,
            '--description=Service account para ARCO BigQuery pipeline',
            '--display-name=ARCO BigQuery',
            f'--project={config.project_id}'
        ])
        
        if not success and "already exists" not in output.lower():
            self.print_error(f"Erro ao criar service account: {output}")
            return False
        
        service_account_email = f"{config.service_account_name}@{config.project_id}.iam.gserviceaccount.com"
        
        # Adicionar roles
        roles = [
            'roles/bigquery.admin',
            'roles/bigquery.dataEditor',
            'roles/bigquery.user'
        ]
        
        for role in roles:
            print(f"  🔐 Adicionando role: {role}")
            success, output = self.run_gcloud_command([
                'gcloud', 'projects', 'add-iam-policy-binding', config.project_id,
                f'--member=serviceAccount:{service_account_email}',
                f'--role={role}'
            ])
            
            if not success:
                self.print_warning(f"Erro ao adicionar role {role}: {output}")
        
        self.print_success(f"Service account configurado: {service_account_email}")
        return True
    
    def create_credentials_key(self, config: GCloudSetupConfig) -> bool:
        """Criar chave JSON do service account"""
        self.print_info("Gerando chave JSON...")
        
        service_account_email = f"{config.service_account_name}@{config.project_id}.iam.gserviceaccount.com"
        credentials_path = self.credentials_dir / "credentials.json"
        
        success, output = self.run_gcloud_command([
            'gcloud', 'iam', 'service-accounts', 'keys', 'create', str(credentials_path),
            f'--iam-account={service_account_email}',
            f'--project={config.project_id}'
        ])
        
        if success:
            self.print_success(f"Chave JSON criada: {credentials_path}")
            return True
        else:
            self.print_error(f"Erro ao criar chave: {output}")
            return False
    
    def create_bigquery_dataset(self, config: GCloudSetupConfig) -> bool:
        """Criar dataset no BigQuery"""
        self.print_info(f"Criando dataset: {config.dataset_id}")
        
        success, output = self.run_gcloud_command([
            'bq', 'mk', f'--location={config.region}', 
            f'--project_id={config.project_id}',
            config.dataset_id
        ])
        
        if success:
            self.print_success(f"Dataset criado: {config.dataset_id}")
        else:
            if "already exists" in output.lower():
                self.print_warning(f"Dataset já existe: {config.dataset_id}")
                return True
            else:
                self.print_error(f"Erro ao criar dataset: {output}")
                return False
        
        return True
    
    def create_sample_table(self, config: GCloudSetupConfig) -> bool:
        """Criar tabela de exemplo"""
        self.print_info("Criando tabela de campanhas...")
        
        # Schema da tabela
        schema = "account_id:STRING,campaign_id:STRING,campaign_name:STRING,date_start:DATE,date_stop:DATE,spend:FLOAT,impressions:INTEGER,clicks:INTEGER,conversions:INTEGER,ctr:FLOAT,cpc:FLOAT,conversion_rate:FLOAT,landing_page_url:STRING,industry:STRING,location:STRING,daily_budget:FLOAT,campaign_status:STRING,created_time:TIMESTAMP,updated_time:TIMESTAMP"
        
        table_id = f"{config.project_id}:{config.dataset_id}.campaigns_insights"
        
        success, output = self.run_gcloud_command([
            'bq', 'mk', '-t',
            f'--schema={schema}',
            f'--time_partitioning_field=date_start',
            f'--description=Facebook Ads campaign insights data for ARCO pipeline',
            table_id
        ])
        
        if success:
            self.print_success("Tabela campaigns_insights criada")
        else:
            if "already exists" in output.lower():
                self.print_warning("Tabela já existe")
                return True
            else:
                self.print_error(f"Erro ao criar tabela: {output}")
                return False
        
        return True
    
    def insert_sample_data(self, config: GCloudSetupConfig) -> bool:
        """Inserir dados de exemplo via SQL"""
        self.print_info("Inserindo dados de exemplo...")
        
        sql_query = f"""
        INSERT INTO `{config.project_id}.{config.dataset_id}.campaigns_insights` VALUES
        ('123456789', 'camp_001', 'Dallas Legal Services - Personal Injury', '2025-01-01', '2025-01-31', 2500.00, 45000, 890, 12, 1.98, 2.81, 1.35, 'https://dallaslegalpersonal.com/injury', 'Legal', 'Dallas, TX', 100.00, 'ACTIVE', '2025-01-01 10:00:00', '2025-01-31 23:59:59'),
        ('123456789', 'camp_002', 'Emergency Legal Help Dallas', '2025-01-01', '2025-01-31', 1800.00, 32000, 645, 8, 2.02, 2.79, 1.24, 'https://emergencylegaldallas.com', 'Legal', 'Dallas, TX', 75.00, 'ACTIVE', '2025-01-01 10:00:00', '2025-01-31 23:59:59'),
        ('123456789', 'camp_003', 'Best Dental Dallas - Implants', '2025-01-01', '2025-01-31', 3200.00, 55000, 1120, 28, 2.04, 2.86, 2.50, 'https://bestdentaldallas.com/implants', 'Dental', 'Dallas, TX', 120.00, 'ACTIVE', '2025-01-01 10:00:00', '2025-01-31 23:59:59')
        """
        
        success, output = self.run_gcloud_command([
            'bq', 'query', '--use_legacy_sql=false',
            f'--project_id={config.project_id}',
            sql_query
        ])
        
        if success:
            self.print_success("Dados de exemplo inseridos")
            return True
        else:
            self.print_warning(f"Erro ao inserir dados: {output}")
            return True  # Não falha por causa disso
    
    def create_env_file(self, config: GCloudSetupConfig) -> str:
        """Criar arquivo .env atualizado"""
        env_content = f"""# BIGQUERY CONFIGURATION - SETUP AUTOMÁTICO GCLOUD
# Projeto: {config.project_name}
# Configurado em: {time.strftime('%Y-%m-%d %H:%M:%S')}

# APIs Existentes (JÁ FUNCIONAIS)
SEARCHAPI_KEY=3sgTQQBwGfmtBR1WBW61MgnU
PAGESPEED_KEY=AIzaSyDNo6ycjKNYfDBmbFbOLI7kk-A-teppPaE

# BigQuery Configuration (CONFIGURADO AUTOMATICAMENTE)
GOOGLE_CLOUD_PROJECT={config.project_id}
GOOGLE_APPLICATION_CREDENTIALS=./credentials/credentials.json
BIGQUERY_DATASET={config.dataset_id}
BIGQUERY_REGION={config.region}

# Service Account
SERVICE_ACCOUNT_NAME={config.service_account_name}
SERVICE_ACCOUNT_EMAIL={config.service_account_name}@{config.project_id}.iam.gserviceaccount.com

# Environment
ENVIRONMENT=production
DEBUG=false
"""
        
        env_file = Path(__file__).parent / ".env.gcloud"
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        return str(env_file)
    
    def run_setup(self):
        """Executar setup completo"""
        self.print_header("BIGQUERY SETUP COM GCLOUD CLI")
        
        # 1. Verificar/fazer autenticação
        if not self.authenticate_if_needed():
            self.print_error("Falha na autenticação")
            return False
        
        # 2. Coletar informações
        config = self.collect_project_info()
        self.config = config
        
        # 3. Confirmar configuração
        self.print_header("CONFIRMAÇÃO")
        print(f"{Colors.BLUE}📋 CONFIGURAÇÃO:{Colors.ENDC}")
        print(f"  • Projeto: {config.project_name} ({config.project_id})")
        print(f"  • Região: {config.region}")
        print(f"  • Dataset: {config.dataset_id}")
        print(f"  • Service Account: {config.service_account_name}")
        if config.billing_account:
            print(f"  • Billing: {config.billing_account}")
        
        confirm = input(f"\n{Colors.CYAN}🤔 Confirma e executa setup automático? (s/n): {Colors.ENDC}").lower()
        if confirm != 's':
            self.print_warning("Setup cancelado")
            return False
        
        # 4. Executar setup
        self.print_header("EXECUTANDO SETUP AUTOMÁTICO")
        
        steps = [
            ("Criar projeto", lambda: self.create_project(config)),
            ("Definir projeto ativo", lambda: self.set_active_project(config)),
            ("Vincular billing", lambda: self.link_billing_account(config)),
            ("Habilitar APIs", lambda: self.enable_apis(config)),
            ("Criar service account", lambda: self.create_service_account(config)),
            ("Gerar chave JSON", lambda: self.create_credentials_key(config)),
            ("Criar dataset BigQuery", lambda: self.create_bigquery_dataset(config)),
            ("Criar tabela", lambda: self.create_sample_table(config)),
            ("Inserir dados exemplo", lambda: self.insert_sample_data(config))
        ]
        
        failed_steps = []
        
        for step_name, step_func in steps:
            print(f"\n🔄 {step_name}...")
            try:
                if step_func():
                    self.print_success(f"{step_name} ✅")
                else:
                    self.print_warning(f"{step_name} ⚠️")
                    failed_steps.append(step_name)
            except Exception as e:
                self.print_error(f"{step_name} ❌: {e}")
                failed_steps.append(step_name)
        
        # 5. Criar arquivo .env
        env_file = self.create_env_file(config)
        
        # 6. Relatório final
        self.print_header("SETUP CONCLUÍDO!")
        
        if not failed_steps:
            print(f"{Colors.GREEN}🎉 SETUP 100% AUTOMÁTICO CONCLUÍDO!{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}⚠️ Setup concluído com alguns avisos:{Colors.ENDC}")
            for step in failed_steps:
                print(f"  • {step}")
        
        print(f"\n{Colors.BLUE}📋 PRÓXIMOS PASSOS:{Colors.ENDC}")
        print(f"  1. 🔄 Atualize .env: {Colors.CYAN}copy {env_file} .env{Colors.ENDC}")
        print(f"  2. ✅ Teste: {Colors.CYAN}python bigquery_integration_tester.py{Colors.ENDC}")
        print(f"  3. 🚀 Execute pipeline: {Colors.CYAN}python pipeline_optimized/smb_pipeline_corrected.py{Colors.ENDC}")
        
        print(f"\n{Colors.GREEN}🔗 Links úteis:{Colors.ENDC}")
        print(f"  • Console: https://console.cloud.google.com/home/dashboard?project={config.project_id}")
        print(f"  • BigQuery: https://console.cloud.google.com/bigquery?project={config.project_id}")
        
        return True

def main():
    """Função principal"""
    setup = GCloudBigQuerySetup()
    setup.run_setup()

if __name__ == "__main__":
    main()
