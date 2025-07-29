"""
🚀 BIGQUERY SETUP WIZARD - WORKFLOW INTERATIVO
==============================================
Assistente inteligente para configuração completa do BigQuery
Sistema maduro e otimizado para produção
"""

import os
import json
import asyncio
import getpass
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import urllib.request
import tempfile

# Cores para output
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
class BigQueryConfig:
    """Configuração completa do BigQuery"""
    project_id: str
    project_name: str
    billing_account: str
    region: str
    dataset_id: str
    service_account_name: str
    service_account_email: str
    credentials_file_path: str
    apis_enabled: List[str]
    estimated_monthly_cost: float
    setup_completed: bool = False

class BigQuerySetupWizard:
    """Assistente interativo para configuração completa do BigQuery"""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent / "config"
        self.config_dir.mkdir(exist_ok=True)
        
        self.credentials_dir = Path(__file__).parent / "credentials"
        self.credentials_dir.mkdir(exist_ok=True)
        
        self.config: Optional[BigQueryConfig] = None
        self.gcloud_available = False
        
    def print_header(self, text: str):
        """Print colorido para headers"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
        print(f"🚀 {text}")
        print(f"{'='*60}{Colors.ENDC}")
    
    def print_success(self, text: str):
        """Print verde para sucesso"""
        print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")
    
    def print_warning(self, text: str):
        """Print amarelo para warnings"""
        print(f"{Colors.WARNING}⚠️ {text}{Colors.ENDC}")
    
    def print_error(self, text: str):
        """Print vermelho para erros"""
        print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")
    
    def print_info(self, text: str):
        """Print azul para informações"""
        print(f"{Colors.CYAN}ℹ️ {text}{Colors.ENDC}")
    
    def check_prerequisites(self) -> bool:
        """Verificar pré-requisitos do sistema"""
        self.print_header("VERIFICANDO PRÉ-REQUISITOS")
        
        # Verificar Python
        python_version = sys.version_info
        if python_version >= (3, 7):
            self.print_success(f"Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        else:
            self.print_error("Python 3.7+ requerido")
            return False
        
        # Verificar pip
        try:
            import pip
            self.print_success("pip disponível")
        except ImportError:
            self.print_error("pip não encontrado")
            return False
        
        # Verificar gcloud CLI
        try:
            result = subprocess.run(['gcloud', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.print_success("Google Cloud CLI disponível")
                self.gcloud_available = True
            else:
                self.print_warning("Google Cloud CLI não encontrado")
                self.gcloud_available = False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.print_warning("Google Cloud CLI não encontrado")
            self.gcloud_available = False
        
        # Verificar dependências Python
        try:
            import google.cloud.bigquery
            self.print_success("google-cloud-bigquery instalado")
        except ImportError:
            self.print_warning("google-cloud-bigquery será instalado")
        
        return True
    
    def install_dependencies(self) -> bool:
        """Instalar dependências necessárias"""
        self.print_header("INSTALANDO DEPENDÊNCIAS")
        
        dependencies = [
            "google-cloud-bigquery>=3.35.0",
            "google-auth>=2.40.0", 
            "google-oauth2-tool>=0.0.3",
            "pandas>=1.5.0",
            "python-dotenv>=1.0.0"
        ]
        
        for dep in dependencies:
            try:
                print(f"📦 Instalando {dep}...")
                result = subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    self.print_success(f"{dep} instalado")
                else:
                    self.print_error(f"Erro ao instalar {dep}: {result.stderr}")
                    return False
            except Exception as e:
                self.print_error(f"Exceção ao instalar {dep}: {e}")
                return False
        
        return True
    
    def setup_gcloud_cli(self) -> bool:
        """Configurar Google Cloud CLI se necessário"""
        if self.gcloud_available:
            self.print_success("Google Cloud CLI já disponível")
            return True
            
        self.print_header("CONFIGURAÇÃO GOOGLE CLOUD CLI")
        
        install_gcloud = input(f"{Colors.CYAN}🤔 Deseja instalar o Google Cloud CLI? (s/n): {Colors.ENDC}").lower()
        
        if install_gcloud == 's':
            self.print_info("📥 Baixando Google Cloud CLI...")
            
            # URLs para download
            if sys.platform.startswith('win'):
                url = "https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe"
                filename = "GoogleCloudSDKInstaller.exe"
            elif sys.platform == 'darwin':
                url = "https://dl.google.com/dl/cloudsdk/channels/rapid/google-cloud-cli-darwin-x86_64.tar.gz"
                filename = "google-cloud-cli-darwin.tar.gz"
            else:
                url = "https://dl.google.com/dl/cloudsdk/channels/rapid/google-cloud-cli-linux-x86_64.tar.gz"
                filename = "google-cloud-cli-linux.tar.gz"
            
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    filepath = Path(temp_dir) / filename
                    urllib.request.urlretrieve(url, filepath)
                    
                    self.print_success(f"Download concluído: {filename}")
                    self.print_warning("Execute o instalador e reinicie este script")
                    
                    if sys.platform.startswith('win'):
                        os.startfile(filepath)
                    
                    return False
                    
            except Exception as e:
                self.print_error(f"Erro no download: {e}")
                return False
        else:
            self.print_warning("Google Cloud CLI não será instalado - funcionalidade limitada")
            return True
    
    def collect_project_info(self) -> Dict[str, str]:
        """Coletar informações do projeto interativamente"""
        self.print_header("CONFIGURAÇÃO DO PROJETO GOOGLE CLOUD")
        
        info = {}
        
        # Project ID
        print(f"\n{Colors.BLUE}📋 INFORMAÇÕES DO PROJETO:{Colors.ENDC}")
        info['project_id'] = input(f"{Colors.CYAN}🏷️ Project ID (ex: arco-pipeline-12345): {Colors.ENDC}").strip()
        
        if not info['project_id']:
            import uuid
            suffix = str(uuid.uuid4())[:8]
            info['project_id'] = f"arco-pipeline-{suffix}"
            self.print_info(f"Usando Project ID gerado: {info['project_id']}")
        
        # Project Name
        info['project_name'] = input(f"{Colors.CYAN}📝 Project Name (ex: ARCO Pipeline): {Colors.ENDC}").strip()
        if not info['project_name']:
            info['project_name'] = "ARCO Pipeline Production"
        
        # Region
        print(f"\n{Colors.BLUE}🌍 REGIÕES DISPONÍVEIS:{Colors.ENDC}")
        regions = {
            '1': 'us-central1 (Iowa - Baixo custo)',
            '2': 'us-east1 (South Carolina - Baixo custo)', 
            '3': 'europe-west1 (Belgium - Médio custo)',
            '4': 'asia-southeast1 (Singapore - Alto custo)'
        }
        
        for key, value in regions.items():
            print(f"  {key}. {value}")
        
        region_choice = input(f"{Colors.CYAN}🌍 Escolha a região (1-4) [1]: {Colors.ENDC}").strip()
        region_map = {
            '1': 'us-central1', '2': 'us-east1', 
            '3': 'europe-west1', '4': 'asia-southeast1'
        }
        info['region'] = region_map.get(region_choice, 'us-central1')
        
        # Dataset
        info['dataset_id'] = input(f"{Colors.CYAN}📊 Dataset ID [facebook_ads]: {Colors.ENDC}").strip()
        if not info['dataset_id']:
            info['dataset_id'] = 'facebook_ads'
        
        # Service Account
        info['service_account_name'] = input(f"{Colors.CYAN}🔑 Service Account Name [arco-bigquery]: {Colors.ENDC}").strip()
        if not info['service_account_name']:
            info['service_account_name'] = 'arco-bigquery'
        
        info['service_account_email'] = f"{info['service_account_name']}@{info['project_id']}.iam.gserviceaccount.com"
        
        return info
    
    def estimate_costs(self, project_info: Dict[str, str]) -> float:
        """Estimar custos mensais do BigQuery"""
        self.print_header("ESTIMATIVA DE CUSTOS")
        
        print(f"{Colors.BLUE}💰 CALCULADORA DE CUSTOS BIGQUERY:{Colors.ENDC}")
        
        # Queries estimadas por mês
        queries_month = input(f"{Colors.CYAN}🔍 Queries por mês [10000]: {Colors.ENDC}").strip()
        queries_month = int(queries_month) if queries_month.isdigit() else 10000
        
        # Dados processados por query (GB)
        gb_per_query = input(f"{Colors.CYAN}📊 GB processados por query [0.1]: {Colors.ENDC}").strip()
        gb_per_query = float(gb_per_query) if gb_per_query.replace('.', '').isdigit() else 0.1
        
        # Storage estimado (GB)
        storage_gb = input(f"{Colors.CYAN}💾 Storage estimado (GB) [50]: {Colors.ENDC}").strip()
        storage_gb = int(storage_gb) if storage_gb.isdigit() else 50
        
        # Cálculos (preços do BigQuery 2025)
        query_cost = (queries_month * gb_per_query * 6.25) / 1000  # $6.25 per TB
        storage_cost = storage_gb * 0.023  # $0.023 per GB per month
        total_cost = query_cost + storage_cost
        
        print(f"\n{Colors.GREEN}📈 ESTIMATIVA MENSAL:{Colors.ENDC}")
        print(f"  • Queries: ${query_cost:.2f}")
        print(f"  • Storage: ${storage_cost:.2f}")
        print(f"  • Total: ${total_cost:.2f}")
        
        if total_cost > 100:
            self.print_warning(f"Custo estimado alto: ${total_cost:.2f}/mês")
        else:
            self.print_success(f"Custo estimado aceitável: ${total_cost:.2f}/mês")
        
        return total_cost
    
    def generate_setup_commands(self, project_info: Dict[str, str]) -> List[str]:
        """Gerar comandos de setup do Google Cloud"""
        commands = [
            f"# 1. Fazer login no Google Cloud",
            f"gcloud auth login",
            f"",
            f"# 2. Criar projeto",
            f"gcloud projects create {project_info['project_id']} --name=\"{project_info['project_name']}\"",
            f"",
            f"# 3. Definir projeto ativo",
            f"gcloud config set project {project_info['project_id']}",
            f"",
            f"# 4. Habilitar APIs necessárias",
            f"gcloud services enable bigquery.googleapis.com",
            f"gcloud services enable bigquerystorage.googleapis.com", 
            f"gcloud services enable iam.googleapis.com",
            f"",
            f"# 5. Criar service account",
            f"gcloud iam service-accounts create {project_info['service_account_name']} \\",
            f"    --description=\"Service account para ARCO BigQuery pipeline\" \\",
            f"    --display-name=\"ARCO BigQuery\"",
            f"",
            f"# 6. Adicionar roles necessárias",
            f"gcloud projects add-iam-policy-binding {project_info['project_id']} \\",
            f"    --member=\"serviceAccount:{project_info['service_account_email']}\" \\",
            f"    --role=\"roles/bigquery.admin\"",
            f"",
            f"gcloud projects add-iam-policy-binding {project_info['project_id']} \\",
            f"    --member=\"serviceAccount:{project_info['service_account_email']}\" \\",
            f"    --role=\"roles/bigquery.dataEditor\"",
            f"",
            f"# 7. Gerar chave JSON",
            f"gcloud iam service-accounts keys create credentials.json \\",
            f"    --iam-account={project_info['service_account_email']}",
            f"",
            f"# 8. Criar dataset",
            f"bq mk --location={project_info['region']} {project_info['dataset_id']}"
        ]
        
        return commands
    
    def save_setup_script(self, commands: List[str], project_info: Dict[str, str]) -> str:
        """Salvar script de setup"""
        script_path = self.config_dir / "bigquery_setup.sh"
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write("#!/bin/bash\n")
            f.write("# BIGQUERY SETUP SCRIPT - GERADO AUTOMATICAMENTE\n")
            f.write(f"# Projeto: {project_info['project_name']}\n")
            f.write(f"# Data: {asyncio.get_event_loop().time()}\n\n")
            
            for command in commands:
                f.write(command + "\n")
        
        return str(script_path)
    
    def create_env_template(self, project_info: Dict[str, str]) -> str:
        """Criar template .env atualizado"""
        env_path = Path(__file__).parent / ".env.bigquery"
        
        env_content = f"""# BIGQUERY CONFIGURATION - GERADO AUTOMATICAMENTE
# Projeto: {project_info['project_name']}

# APIs Existentes
SEARCHAPI_KEY=3sgTQQBwGfmtBR1WBW61MgnU
PAGESPEED_KEY=AIzaSyDNo6ycjKNYfDBmbFbOLI7kk-A-teppPaE

# BigQuery Configuration
GOOGLE_CLOUD_PROJECT={project_info['project_id']}
GOOGLE_APPLICATION_CREDENTIALS=./credentials/credentials.json
BIGQUERY_DATASET={project_info['dataset_id']}
BIGQUERY_REGION={project_info['region']}

# Service Account
SERVICE_ACCOUNT_EMAIL={project_info['service_account_email']}

# Environment
ENVIRONMENT=production
DEBUG=false
"""
        
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        return str(env_path)
    
    def create_validation_script(self, project_info: Dict[str, str]) -> str:
        """Criar script de validação"""
        validation_path = self.config_dir / "validate_bigquery.py"
        
        validation_code = f'''"""
SCRIPT DE VALIDAÇÃO BIGQUERY - GERADO AUTOMATICAMENTE
====================================================
Testa conexão completa com BigQuery após setup
"""

import os
import sys
from google.cloud import bigquery
from google.oauth2 import service_account

def validate_bigquery_setup():
    """Validar setup completo do BigQuery"""
    
    print("🧪 VALIDANDO CONFIGURAÇÃO BIGQUERY...")
    print("=" * 50)
    
    # Verificar variáveis de ambiente
    project_id = "{project_info['project_id']}"
    credentials_path = "./credentials/credentials.json"
    dataset_id = "{project_info['dataset_id']}"
    
    print(f"📋 Projeto: {{project_id}}")
    print(f"🔑 Credentials: {{credentials_path}}")
    print(f"📊 Dataset: {{dataset_id}}")
    
    # Testar credenciais
    try:
        if not os.path.exists(credentials_path):
            print("❌ Arquivo credentials.json não encontrado")
            return False
            
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        client = bigquery.Client(credentials=credentials, project=project_id)
        
        # Teste 1: Listar datasets
        datasets = list(client.list_datasets())
        print(f"✅ Datasets encontrados: {{len(datasets)}}")
        
        # Teste 2: Query simples
        query = "SELECT 1 as test_number, 'success' as test_result"
        job = client.query(query)
        results = list(job.result())
        
        if results:
            print("✅ Query de teste executada com sucesso")
            print(f"   Resultado: {{results[0]}}")
        
        # Teste 3: Verificar dataset específico
        try:
            dataset_ref = client.dataset(dataset_id)
            dataset = client.get_dataset(dataset_ref)
            print(f"✅ Dataset '{{dataset_id}}' acessível")
            print(f"   Localização: {{dataset.location}}")
            print(f"   Criado em: {{dataset.created}}")
        except Exception as e:
            print(f"⚠️ Dataset '{{dataset_id}}' não encontrado: {{e}}")
        
        print("\\n🎯 BIGQUERY CONFIGURADO COM SUCESSO!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na validação: {{e}}")
        return False

if __name__ == "__main__":
    success = validate_bigquery_setup()
    sys.exit(0 if success else 1)
'''
        
        with open(validation_path, 'w', encoding='utf-8') as f:
            f.write(validation_code)
        
        return str(validation_path)
    
    def generate_sql_setup(self, project_info: Dict[str, str]) -> str:
        """Gerar SQL para setup inicial"""
        sql_path = self.config_dir / "bigquery_initial_setup.sql"
        
        sql_content = f"""-- BIGQUERY INITIAL SETUP SQL
-- Projeto: {project_info['project_name']}
-- Dataset: {project_info['dataset_id']}

-- 1. Criar tabela de campanhas Meta Ads
CREATE TABLE `{project_info['project_id']}.{project_info['dataset_id']}.campaigns_insights` (
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

-- 2. Inserir dados de exemplo para teste
INSERT INTO `{project_info['project_id']}.{project_info['dataset_id']}.campaigns_insights` VALUES
('123456789', 'camp_001', 'Dallas Legal Services - Personal Injury', '2025-01-01', '2025-01-31', 2500.00, 45000, 890, 12, 1.98, 2.81, 1.35, 'https://dallaslegalpersonal.com/injury', 'Legal', 'Dallas, TX', 100.00, 'ACTIVE', '2025-01-01 10:00:00', '2025-01-31 23:59:59'),
('123456789', 'camp_002', 'Emergency Legal Help Dallas', '2025-01-01', '2025-01-31', 1800.00, 32000, 645, 8, 2.02, 2.79, 1.24, 'https://emergencylegaldallas.com', 'Legal', 'Dallas, TX', 75.00, 'ACTIVE', '2025-01-01 10:00:00', '2025-01-31 23:59:59'),
('123456789', 'camp_003', 'Best Dental Dallas - Implants', '2025-01-01', '2025-01-31', 3200.00, 55000, 1120, 28, 2.04, 2.86, 2.50, 'https://bestdentaldallas.com/implants', 'Dental', 'Dallas, TX', 120.00, 'ACTIVE', '2025-01-01 10:00:00', '2025-01-31 23:59:59');

-- 3. Criar view para análise de waste
CREATE VIEW `{project_info['project_id']}.{project_info['dataset_id']}.waste_analysis` AS
SELECT 
  industry,
  location,
  AVG(cpc) as avg_cpc,
  AVG(conversion_rate) as avg_conversion_rate,
  SUM(spend) as total_spend,
  COUNT(*) as campaign_count,
  -- Waste estimation (high CPC + low conversion rate)
  CASE 
    WHEN AVG(cpc) > 3.0 AND AVG(conversion_rate) < 2.0 THEN 'HIGH_WASTE'
    WHEN AVG(cpc) > 2.0 AND AVG(conversion_rate) < 3.0 THEN 'MEDIUM_WASTE'
    ELSE 'LOW_WASTE'
  END as waste_level
FROM `{project_info['project_id']}.{project_info['dataset_id']}.campaigns_insights`
WHERE campaign_status = 'ACTIVE'
GROUP BY industry, location;

-- 4. Query de exemplo para ARCO pipeline
SELECT 
  campaign_name,
  landing_page_url,
  spend,
  cpc,
  conversion_rate,
  -- P0 Signal calculation
  CASE 
    WHEN cpc > 3.0 AND conversion_rate < 2.0 THEN 'P0_PERFORMANCE'
    WHEN cpc > 2.5 AND conversion_rate < 2.5 THEN 'P0_SCENT'
    ELSE 'NORMAL'
  END as p0_signal_type
FROM `{project_info['project_id']}.{project_info['dataset_id']}.campaigns_insights`
WHERE campaign_status = 'ACTIVE'
  AND industry IN ('Legal', 'Dental', 'Home Services')
  AND spend > 1000
ORDER BY spend DESC
LIMIT 10;
"""
        
        with open(sql_path, 'w', encoding='utf-8') as f:
            f.write(sql_content)
        
        return str(sql_path)
    
    async def run_wizard(self):
        """Executar wizard completo"""
        self.print_header("BIGQUERY SETUP WIZARD - ARCO PIPELINE")
        
        # 1. Verificar pré-requisitos
        if not self.check_prerequisites():
            self.print_error("Pré-requisitos não atendidos")
            return False
        
        # 2. Instalar dependências
        if not self.install_dependencies():
            self.print_error("Falha na instalação de dependências")
            return False
        
        # 3. Setup gcloud CLI
        if not self.setup_gcloud_cli():
            self.print_warning("Configuração manual necessária")
        
        # 4. Coletar informações do projeto
        project_info = self.collect_project_info()
        
        # 5. Estimar custos
        estimated_cost = self.estimate_costs(project_info)
        
        # 6. Confirmação final
        self.print_header("CONFIRMAÇÃO FINAL")
        print(f"{Colors.BLUE}📋 RESUMO DA CONFIGURAÇÃO:{Colors.ENDC}")
        print(f"  • Projeto: {project_info['project_name']} ({project_info['project_id']})")
        print(f"  • Região: {project_info['region']}")
        print(f"  • Dataset: {project_info['dataset_id']}")
        print(f"  • Service Account: {project_info['service_account_email']}")
        print(f"  • Custo estimado: ${estimated_cost:.2f}/mês")
        
        confirm = input(f"\n{Colors.CYAN}🤔 Confirma configuração? (s/n): {Colors.ENDC}").lower()
        
        if confirm != 's':
            self.print_warning("Configuração cancelada")
            return False
        
        # 7. Gerar arquivos de configuração
        self.print_header("GERANDO ARQUIVOS DE CONFIGURAÇÃO")
        
        # Commands script
        commands = self.generate_setup_commands(project_info)
        script_path = self.save_setup_script(commands, project_info)
        self.print_success(f"Script salvo: {script_path}")
        
        # Environment file
        env_path = self.create_env_template(project_info)
        self.print_success(f"Template .env salvo: {env_path}")
        
        # Validation script
        validation_path = self.create_validation_script(project_info)
        self.print_success(f"Script de validação: {validation_path}")
        
        # SQL setup
        sql_path = self.generate_sql_setup(project_info)
        self.print_success(f"SQL inicial: {sql_path}")
        
        # 8. Salvar configuração
        config = BigQueryConfig(
            project_id=project_info['project_id'],
            project_name=project_info['project_name'],
            billing_account='',
            region=project_info['region'],
            dataset_id=project_info['dataset_id'],
            service_account_name=project_info['service_account_name'],
            service_account_email=project_info['service_account_email'],
            credentials_file_path='./credentials/credentials.json',
            apis_enabled=['bigquery.googleapis.com', 'bigquerystorage.googleapis.com'],
            estimated_monthly_cost=estimated_cost
        )
        
        config_path = self.config_dir / "bigquery_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(config), f, indent=2)
        
        self.print_success(f"Configuração salva: {config_path}")
        
        # 9. Próximos passos
        self.print_header("PRÓXIMOS PASSOS")
        print(f"{Colors.GREEN}🎯 SETUP CONCLUÍDO! Execute os comandos abaixo:{Colors.ENDC}")
        print(f"")
        print(f"1. 🚀 Execute o script de setup:")
        print(f"   {Colors.CYAN}bash {script_path}{Colors.ENDC}")
        print(f"")
        print(f"2. 📁 Mova o arquivo credentials.json para:")
        print(f"   {Colors.CYAN}./credentials/credentials.json{Colors.ENDC}")
        print(f"")
        print(f"3. 🔄 Atualize seu .env:")
        print(f"   {Colors.CYAN}cp {env_path} .env{Colors.ENDC}")
        print(f"")
        print(f"4. ✅ Valide a configuração:")
        print(f"   {Colors.CYAN}python {validation_path}{Colors.ENDC}")
        print(f"")
        print(f"5. 📊 Execute o SQL inicial no BigQuery Console")
        print(f"")
        
        self.print_success("🎉 WIZARD CONCLUÍDO COM SUCESSO!")
        return True

async def main():
    """Função principal do wizard"""
    wizard = BigQuerySetupWizard()
    await wizard.run_wizard()

if __name__ == "__main__":
    asyncio.run(main())
