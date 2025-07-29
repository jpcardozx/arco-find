"""
⚡ BIGQUERY QUICK SETUP - SEM GCLOUD CLI
=======================================
Setup rápido usando apenas o console web do Google Cloud
Workflow otimizado para configuração manual guiada
"""

import os
import json
import webbrowser
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass
import urllib.parse

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
class QuickSetupConfig:
    """Configuração para setup rápido"""
    project_id: str
    project_name: str
    region: str = "us-central1"
    dataset_id: str = "facebook_ads"
    service_account_name: str = "arco-bigquery"

class BigQueryQuickSetup:
    """Setup rápido do BigQuery via console web"""
    
    def __init__(self):
        self.config: QuickSetupConfig = None
        self.base_url = "https://console.cloud.google.com"
        
    def print_header(self, text: str):
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
        print(f"⚡ {text}")
        print(f"{'='*60}{Colors.ENDC}")
    
    def print_step(self, step_num: int, text: str):
        print(f"\n{Colors.CYAN}{Colors.BOLD}PASSO {step_num}: {text}{Colors.ENDC}")
    
    def print_action(self, text: str):
        print(f"{Colors.GREEN}👆 {text}{Colors.ENDC}")
    
    def print_info(self, text: str):
        print(f"{Colors.BLUE}ℹ️ {text}{Colors.ENDC}")
    
    def print_warning(self, text: str):
        print(f"{Colors.WARNING}⚠️ {text}{Colors.ENDC}")
    
    def collect_project_info(self) -> QuickSetupConfig:
        """Coletar informações básicas do projeto"""
        self.print_header("CONFIGURAÇÃO RÁPIDA DO PROJETO")
        
        # Project ID
        project_id = input(f"{Colors.CYAN}🏷️ Project ID (deixe vazio para gerar): {Colors.ENDC}").strip()
        if not project_id:
            import uuid
            project_id = f"arco-pipeline-{str(uuid.uuid4())[:8]}"
            print(f"{Colors.GREEN}✅ Project ID gerado: {project_id}{Colors.ENDC}")
        
        # Project Name
        project_name = input(f"{Colors.CYAN}📝 Project Name [ARCO Pipeline]: {Colors.ENDC}").strip()
        if not project_name:
            project_name = "ARCO Pipeline"
        
        # Region
        print(f"\n{Colors.BLUE}🌍 Regiões recomendadas (baixo custo):{Colors.ENDC}")
        print("  1. us-central1 (Iowa)")
        print("  2. us-east1 (South Carolina)")
        
        region_choice = input(f"{Colors.CYAN}Escolha (1 ou 2) [1]: {Colors.ENDC}").strip()
        region = "us-east1" if region_choice == "2" else "us-central1"
        
        return QuickSetupConfig(
            project_id=project_id,
            project_name=project_name,
            region=region
        )
    
    def generate_urls(self, config: QuickSetupConfig) -> Dict[str, str]:
        """Gerar URLs para console do Google Cloud"""
        base = self.base_url
        
        urls = {
            # 1. Criar projeto
            'create_project': f"{base}/projectcreate",
            
            # 2. Billing
            'billing': f"{base}/billing/projects",
            
            # 3. APIs & Services
            'enable_apis': f"{base}/apis/dashboard?project={config.project_id}",
            
            # 4. IAM Service Accounts
            'service_accounts': f"{base}/iam-admin/serviceaccounts?project={config.project_id}",
            
            # 5. BigQuery
            'bigquery': f"{base}/bigquery?project={config.project_id}",
            
            # 6. Logs (para troubleshooting)
            'logs': f"{base}/logs/query?project={config.project_id}"
        }
        
        return urls
    
    def step_1_create_project(self, config: QuickSetupConfig, urls: Dict[str, str]):
        """Passo 1: Criar projeto"""
        self.print_step(1, "CRIAR PROJETO NO GOOGLE CLOUD")
        
        self.print_action("Clique no link abaixo para abrir o console:")
        print(f"🔗 {urls['create_project']}")
        
        print(f"\n{Colors.BLUE}📋 No console, faça:{Colors.ENDC}")
        print(f"  1. Clique em 'CREATE PROJECT'")
        print(f"  2. Project name: {Colors.BOLD}{config.project_name}{Colors.ENDC}")
        print(f"  3. Project ID: {Colors.BOLD}{config.project_id}{Colors.ENDC}")
        print(f"  4. Clique em 'CREATE'")
        
        input(f"\n{Colors.CYAN}Pressione ENTER após criar o projeto...{Colors.ENDC}")
        
        # Abrir automaticamente
        try:
            webbrowser.open(urls['create_project'])
            self.print_info("Console aberto no navegador")
        except:
            self.print_warning("Não foi possível abrir automaticamente")
    
    def step_2_enable_billing(self, config: QuickSetupConfig, urls: Dict[str, str]):
        """Passo 2: Habilitar billing"""
        self.print_step(2, "HABILITAR BILLING")
        
        self.print_action("Clique no link abaixo para configurar billing:")
        print(f"🔗 {urls['billing']}")
        
        print(f"\n{Colors.BLUE}📋 No console, faça:{Colors.ENDC}")
        print(f"  1. Selecione o projeto: {Colors.BOLD}{config.project_name}{Colors.ENDC}")
        print(f"  2. Clique em 'LINK A BILLING ACCOUNT'")
        print(f"  3. Crie ou selecione uma conta de billing")
        print(f"  4. Confirme a vinculação")
        
        self.print_warning("💳 Billing é necessário para usar BigQuery")
        
        input(f"\n{Colors.CYAN}Pressione ENTER após configurar billing...{Colors.ENDC}")
        
        try:
            webbrowser.open(urls['billing'])
        except:
            pass
    
    def step_3_enable_apis(self, config: QuickSetupConfig, urls: Dict[str, str]):
        """Passo 3: Habilitar APIs"""
        self.print_step(3, "HABILITAR APIS NECESSÁRIAS")
        
        self.print_action("Clique no link abaixo para habilitar APIs:")
        print(f"🔗 {urls['enable_apis']}")
        
        apis_to_enable = [
            "BigQuery API",
            "BigQuery Storage API", 
            "Cloud Resource Manager API",
            "Identity and Access Management (IAM) API"
        ]
        
        print(f"\n{Colors.BLUE}📋 Habilite as seguintes APIs:{Colors.ENDC}")
        for i, api in enumerate(apis_to_enable, 1):
            print(f"  {i}. {api}")
        
        print(f"\n{Colors.BLUE}🔍 Como habilitar:{Colors.ENDC}")
        print(f"  1. Clique em '+ ENABLE APIS AND SERVICES'")
        print(f"  2. Pesquise pelo nome da API")
        print(f"  3. Clique na API e depois em 'ENABLE'")
        print(f"  4. Repita para todas as APIs")
        
        input(f"\n{Colors.CYAN}Pressione ENTER após habilitar todas as APIs...{Colors.ENDC}")
        
        try:
            webbrowser.open(urls['enable_apis'])
        except:
            pass
    
    def step_4_create_service_account(self, config: QuickSetupConfig, urls: Dict[str, str]):
        """Passo 4: Criar service account"""
        self.print_step(4, "CRIAR SERVICE ACCOUNT")
        
        self.print_action("Clique no link abaixo para criar service account:")
        print(f"🔗 {urls['service_accounts']}")
        
        print(f"\n{Colors.BLUE}📋 No console, faça:{Colors.ENDC}")
        print(f"  1. Clique em '+ CREATE SERVICE ACCOUNT'")
        print(f"  2. Service account name: {Colors.BOLD}{config.service_account_name}{Colors.ENDC}")
        print(f"  3. Description: 'Service account para ARCO BigQuery pipeline'")
        print(f"  4. Clique em 'CREATE AND CONTINUE'")
        
        print(f"\n{Colors.BLUE}🔐 Adicione as seguintes roles:{Colors.ENDC}")
        roles = [
            "BigQuery Admin",
            "BigQuery Data Editor", 
            "BigQuery User"
        ]
        for role in roles:
            print(f"  • {role}")
        
        print(f"\n{Colors.BLUE}🔑 Gerar chave JSON:{Colors.ENDC}")
        print(f"  1. Clique no service account criado")
        print(f"  2. Vá para a aba 'KEYS'")
        print(f"  3. Clique em 'ADD KEY' > 'Create new key'")
        print(f"  4. Selecione 'JSON' e clique em 'CREATE'")
        print(f"  5. Salve o arquivo como 'credentials.json'")
        
        input(f"\n{Colors.CYAN}Pressione ENTER após criar service account e baixar JSON...{Colors.ENDC}")
        
        try:
            webbrowser.open(urls['service_accounts'])
        except:
            pass
    
    def step_5_setup_bigquery(self, config: QuickSetupConfig, urls: Dict[str, str]):
        """Passo 5: Configurar BigQuery"""
        self.print_step(5, "CONFIGURAR BIGQUERY")
        
        self.print_action("Clique no link abaixo para acessar BigQuery:")
        print(f"🔗 {urls['bigquery']}")
        
        print(f"\n{Colors.BLUE}📊 Criar dataset:{Colors.ENDC}")
        print(f"  1. No painel lateral, clique no seu projeto")
        print(f"  2. Clique em '⋮' (três pontos) > 'Create dataset'")
        print(f"  3. Dataset ID: {Colors.BOLD}{config.dataset_id}{Colors.ENDC}")
        print(f"  4. Location: {Colors.BOLD}{config.region}{Colors.ENDC}")
        print(f"  5. Clique em 'CREATE DATASET'")
        
        input(f"\n{Colors.CYAN}Pressione ENTER após criar o dataset...{Colors.ENDC}")
        
        try:
            webbrowser.open(urls['bigquery'])
        except:
            pass
    
    def step_6_create_tables(self, config: QuickSetupConfig):
        """Passo 6: Criar tabelas"""
        self.print_step(6, "CRIAR TABELAS INICIAIS")
        
        sql_create_table = f"""
CREATE TABLE `{config.project_id}.{config.dataset_id}.campaigns_insights` (
  account_id STRING,
  campaign_id STRING,
  campaign_name STRING,
  date_start DATE,
  date_stop DATE,
  spend FLOAT64,
  impressions INT64,
  clicks INT64,
  conversions INT64,
  ctr FLOAT64,
  cpc FLOAT64,
  conversion_rate FLOAT64,
  landing_page_url STRING,
  industry STRING,
  location STRING,
  daily_budget FLOAT64,
  campaign_status STRING,
  created_time TIMESTAMP,
  updated_time TIMESTAMP
)
PARTITION BY date_start
OPTIONS(
  description="Facebook Ads campaign insights data for ARCO pipeline"
);
"""
        
        sql_insert_sample = f"""
INSERT INTO `{config.project_id}.{config.dataset_id}.campaigns_insights` VALUES
('123456789', 'camp_001', 'Dallas Legal Services - Personal Injury', '2025-01-01', '2025-01-31', 2500.00, 45000, 890, 12, 1.98, 2.81, 1.35, 'https://dallaslegalpersonal.com/injury', 'Legal', 'Dallas, TX', 100.00, 'ACTIVE', '2025-01-01 10:00:00', '2025-01-31 23:59:59'),
('123456789', 'camp_002', 'Emergency Legal Help Dallas', '2025-01-01', '2025-01-31', 1800.00, 32000, 645, 8, 2.02, 2.79, 1.24, 'https://emergencylegaldallas.com', 'Legal', 'Dallas, TX', 75.00, 'ACTIVE', '2025-01-01 10:00:00', '2025-01-31 23:59:59'),
('123456789', 'camp_003', 'Best Dental Dallas - Implants', '2025-01-01', '2025-01-31', 3200.00, 55000, 1120, 28, 2.04, 2.86, 2.50, 'https://bestdentaldallas.com/implants', 'Dental', 'Dallas, TX', 120.00, 'ACTIVE', '2025-01-01 10:00:00', '2025-01-31 23:59:59');
"""
        
        print(f"{Colors.BLUE}📋 Execute os SQLs abaixo no BigQuery:{Colors.ENDC}")
        
        print(f"\n{Colors.GREEN}1. SQL para criar tabela:{Colors.ENDC}")
        print("─" * 40)
        print(sql_create_table)
        
        print(f"\n{Colors.GREEN}2. SQL para inserir dados de exemplo:{Colors.ENDC}")
        print("─" * 40)
        print(sql_insert_sample)
        
        # Salvar SQLs em arquivo
        sql_dir = Path(__file__).parent / "config"
        sql_dir.mkdir(exist_ok=True)
        
        sql_file = sql_dir / "bigquery_setup.sql"
        with open(sql_file, 'w', encoding='utf-8') as f:
            f.write("-- CRIAR TABELA\n")
            f.write(sql_create_table)
            f.write("\n-- INSERIR DADOS DE EXEMPLO\n")
            f.write(sql_insert_sample)
        
        print(f"\n{Colors.INFO}💾 SQLs salvos em: {sql_file}{Colors.ENDC}")
        
        input(f"\n{Colors.CYAN}Pressione ENTER após executar os SQLs...{Colors.ENDC}")
    
    def create_config_files(self, config: QuickSetupConfig):
        """Criar arquivos de configuração"""
        self.print_step(7, "CRIAR ARQUIVOS DE CONFIGURAÇÃO")
        
        # Criar diretório credentials
        cred_dir = Path(__file__).parent / "credentials"
        cred_dir.mkdir(exist_ok=True)
        
        # Template .env
        env_content = f"""# BIGQUERY CONFIGURATION - SETUP RÁPIDO
# Projeto: {config.project_name}

# APIs Existentes
SEARCHAPI_KEY=3sgTQQBwGfmtBR1WBW61MgnU
PAGESPEED_KEY=AIzaSyDNo6ycjKNYfDBmbFbOLI7kk-A-teppPaE

# BigQuery Configuration
GOOGLE_CLOUD_PROJECT={config.project_id}
GOOGLE_APPLICATION_CREDENTIALS=./credentials/credentials.json
BIGQUERY_DATASET={config.dataset_id}
BIGQUERY_REGION={config.region}

# Service Account
SERVICE_ACCOUNT_NAME={config.service_account_name}

# Environment
ENVIRONMENT=production
DEBUG=false
"""
        
        env_file = Path(__file__).parent / ".env.new"
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"{Colors.GREEN}✅ Arquivo .env criado: {env_file}{Colors.ENDC}")
        
        # Instruções finais
        print(f"\n{Colors.BLUE}📁 IMPORTANTE - Mova o arquivo credentials.json:{Colors.ENDC}")
        print(f"  De: Downloads/credentials.json")
        print(f"  Para: {cred_dir}/credentials.json")
        
        print(f"\n{Colors.BLUE}🔄 Atualize seu .env principal:{Colors.ENDC}")
        print(f"  {Colors.CYAN}copy {env_file} .env{Colors.ENDC}")
        
        return env_file
    
    def run_quick_setup(self):
        """Executar setup rápido completo"""
        self.print_header("BIGQUERY QUICK SETUP - SEM GCLOUD CLI")
        
        print(f"{Colors.BLUE}🚀 Este wizard vai guiá-lo através da configuração do BigQuery")
        print(f"usando apenas o console web do Google Cloud.{Colors.ENDC}")
        
        # Coletar informações
        config = self.collect_project_info()
        self.config = config
        
        # Gerar URLs
        urls = self.generate_urls(config)
        
        print(f"\n{Colors.GREEN}📋 RESUMO DA CONFIGURAÇÃO:{Colors.ENDC}")
        print(f"  • Projeto: {config.project_name}")
        print(f"  • Project ID: {config.project_id}")
        print(f"  • Região: {config.region}")
        print(f"  • Dataset: {config.dataset_id}")
        
        confirm = input(f"\n{Colors.CYAN}Continuar com esta configuração? (s/n): {Colors.ENDC}").lower()
        if confirm != 's':
            print(f"{Colors.WARNING}Setup cancelado{Colors.ENDC}")
            return
        
        # Executar passos
        self.step_1_create_project(config, urls)
        self.step_2_enable_billing(config, urls)
        self.step_3_enable_apis(config, urls)
        self.step_4_create_service_account(config, urls)
        self.step_5_setup_bigquery(config, urls)
        self.step_6_create_tables(config)
        env_file = self.create_config_files(config)
        
        # Finalização
        self.print_header("SETUP CONCLUÍDO!")
        
        print(f"{Colors.GREEN}🎉 Configuração básica do BigQuery finalizada!{Colors.ENDC}")
        
        print(f"\n{Colors.BLUE}📝 PRÓXIMOS PASSOS:{Colors.ENDC}")
        print(f"  1. 📁 Mova credentials.json para ./credentials/")
        print(f"  2. 🔄 Atualize .env: copy {env_file} .env")
        print(f"  3. ✅ Teste: python bigquery_monitor.py")
        
        print(f"\n{Colors.CYAN}🔧 Para debug: python bigquery_monitor.py{Colors.ENDC}")
        print(f"{Colors.CYAN}⚡ Para teste rápido: python test_api_connections.py{Colors.ENDC}")

def main():
    """Função principal"""
    setup = BigQueryQuickSetup()
    setup.run_quick_setup()

if __name__ == "__main__":
    main()
