"""
🔧 BIGQUERY SETUP SEM ADMIN - SOLUÇÃO ALTERNATIVA
================================================
Configure BigQuery sem precisar de privilégios de administrador
Usa PATH da sessão atual + configuração manual simplificada
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
    print("🎯 Configurando BigQuery sem privilégios admin")
    print("⚡ Usando PATH da sessão atual")
    print("=" * 45)

def setup_session_path():
    """Configurar PATH para sessão atual"""
    gcloud_path = r"C:\Users\João Pedro Cardozo\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"
    
    # Adicionar ao PATH da sessão
    current_path = os.environ.get('PATH', '')
    if gcloud_path not in current_path:
        os.environ['PATH'] = f"{current_path};{gcloud_path}"
        print(f"✅ gcloud adicionado ao PATH da sessão")
    else:
        print("✅ gcloud já está no PATH")

def test_gcloud():
    """Testar se gcloud funciona"""
    try:
        result = subprocess.run(['gcloud', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ gcloud funcionando!")
            version_line = result.stdout.split('\n')[0]
            print(f"📋 {version_line}")
            return True
    except Exception as e:
        print(f"❌ Erro ao testar gcloud: {e}")
    
    return False

def create_bigquery_project_manually():
    """Criar projeto BigQuery manualmente (sem gcloud automation)"""
    print("\n🎯 CONFIGURAÇÃO BIGQUERY MANUAL")
    print("=" * 40)
    
    # Gerar project ID único
    import random
    import string
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    project_id = f"arco-pipeline-{suffix}"
    
    print(f"📋 Project ID sugerido: {project_id}")
    
    # Instruções manuais
    instructions = f"""
🔧 PASSOS MANUAIS PARA CONFIGURAÇÃO:

1. 🌐 Abra: https://console.cloud.google.com/

2. 📁 Crie um novo projeto:
   • Nome: ARCO Pipeline
   • ID: {project_id}
   • Organização: Sua conta pessoal

3. 🔧 Habilite APIs (em cada link, clique "ATIVAR"):
   • BigQuery API: https://console.cloud.google.com/apis/library/bigquery.googleapis.com
   • Cloud Resource Manager: https://console.cloud.google.com/apis/library/cloudresourcemanager.googleapis.com

4. 🔑 Criar Service Account:
   • Vá para: https://console.cloud.google.com/iam-admin/serviceaccounts
   • Clique "CRIAR CONTA DE SERVIÇO"
   • Nome: arco-bigquery
   • Descrição: ARCO Pipeline BigQuery Access
   • Clique "CRIAR E CONTINUAR"
   • Função: BigQuery Admin
   • Clique "CONTINUAR" e "CONCLUÍDO"

5. 📥 Baixar credenciais:
   • Na lista de service accounts, clique nos 3 pontos da conta criada
   • Clique "Gerenciar chaves"
   • Clique "ADICIONAR CHAVE" > "Criar nova chave"
   • Selecione "JSON" e clique "CRIAR"
   • Salve o arquivo como: credentials.json

6. 📁 Mover arquivo de credenciais:
   • Mova o arquivo baixado para: pipeline_optimized/credentials/credentials.json

7. ✅ Atualizar configuração
"""
    
    print(instructions)
    
    # Criar estrutura de credenciais
    creds_dir = Path(__file__).parent.parent / "pipeline_optimized" / "credentials"
    creds_dir.mkdir(parents=True, exist_ok=True)
    
    # Criar arquivo .env atualizado
    env_content = f"""# ARCO Pipeline - Environment Configuration
ENVIRONMENT=production
DEBUG=false

# API Keys (Operacionais)
SEARCHAPI_KEY=3sgTQQBwGfmtBR1WBW61MgnU
PAGESPEED_KEY=AIzaSyDNo6ycjKNYfDBmbFbOLI7kk-A-teppPaE

# BigQuery Configuration
GOOGLE_CLOUD_PROJECT={project_id}
GOOGLE_APPLICATION_CREDENTIALS=./credentials/credentials.json
BIGQUERY_DATASET=facebook_ads
BIGQUERY_REGION=us-central1

# Pipeline Configuration
MAX_LEADS=5
QUALIFICATION_THRESHOLD=0.7
ICP_FOCUS=true
"""
    
    env_file = Path(__file__).parent.parent / "pipeline_optimized" / ".env"
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Arquivo .env atualizado com project ID: {project_id}")
    
    return project_id

def create_bigquery_tables_sql(project_id):
    """Criar SQL para tabelas BigQuery"""
    sql_content = f"""-- ARCO BigQuery Tables Setup
-- Execute este SQL no BigQuery Console depois de configurar o projeto

-- 1. Criar dataset
CREATE SCHEMA IF NOT EXISTS `{project_id}.facebook_ads`
OPTIONS(
  description="Facebook Ads data for ARCO pipeline analysis",
  location="us-central1"
);

-- 2. Criar tabela de insights de campanhas
CREATE OR REPLACE TABLE `{project_id}.facebook_ads.campaigns_insights` (
  campaign_id STRING,
  campaign_name STRING,
  account_id STRING,
  account_name STRING,
  date_start DATE,
  date_stop DATE,
  impressions INT64,
  clicks INT64,
  spend FLOAT64,
  cpc FLOAT64,
  cpm FLOAT64,
  ctr FLOAT64,
  conversion_rate FLOAT64,
  conversions INT64,
  cost_per_conversion FLOAT64,
  landing_page_url STRING,
  audience_targeting STRING,
  ad_creative STRING,
  placement STRING,
  device_platform STRING,
  age_range STRING,
  gender STRING,
  location STRING,
  interests STRING,
  behaviors STRING,
  industry STRING,
  business_size STRING,
  campaign_status STRING,
  created_time TIMESTAMP,
  updated_time TIMESTAMP
)
PARTITION BY date_start
CLUSTER BY industry, location, campaign_status;

-- 3. Inserir dados de exemplo para teste
INSERT INTO `{project_id}.facebook_ads.campaigns_insights` VALUES
('camp_001', 'Dallas Personal Injury - Broad', 'acc_001', 'DFW Injury Lawyers', '2025-01-01', '2025-01-31', 15000, 450, 3825.50, 8.50, 255.03, 3.0, 2.2, 10, 382.55, 'https://dfwinjurylawyers.com/contact', 'Age: 25-65, Location: Dallas Metro', 'Free Consultation CTA', 'Facebook Feed', 'Mobile', '25-65', 'All', 'Dallas, TX', 'Legal Services', 'Recent Life Events', 'legal', 'smb', 'ACTIVE', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('camp_002', 'Houston DUI Defense - Targeted', 'acc_002', 'Texas DUI Experts', '2025-01-01', '2025-01-31', 8500, 280, 2380.00, 8.50, 280.00, 3.3, 1.8, 5, 476.00, 'https://texasduiexperts.com/dui-defense', 'Age: 21-55, DUI Related Keywords', 'Expert DUI Defense', 'Facebook Feed', 'Desktop', '21-55', 'All', 'Houston, TX', 'Legal Services', 'Legal Issues', 'legal', 'smb', 'ACTIVE', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('camp_003', 'Miami Plastic Surgery - Premium', 'acc_003', 'Miami Aesthetics Center', '2025-01-01', '2025-01-31', 12000, 320, 1600.00, 5.00, 133.33, 2.7, 3.1, 10, 160.00, 'https://miamiaesthetics.com/procedures', 'Age: 25-50, Income: Top 25%', 'Transform Your Look', 'Instagram Feed', 'Mobile', '25-50', 'Female', 'Miami, FL', 'Beauty & Wellness', 'Cosmetic Procedures', 'healthcare', 'smb', 'ACTIVE', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('camp_004', 'Phoenix Real Estate - Luxury', 'acc_004', 'Desert Elite Realty', '2025-01-01', '2025-01-31', 10500, 210, 1260.00, 6.00, 120.00, 2.0, 2.9, 6, 210.00, 'https://deserteliterealty.com/luxury-homes', 'Age: 35-65, Income: Top 10%', 'Luxury Desert Living', 'Facebook Feed', 'Desktop', '35-65', 'All', 'Phoenix, AZ', 'Real Estate', 'Home Buying', 'real_estate', 'smb', 'ACTIVE', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('camp_005', 'Atlanta Emergency HVAC - Local', 'acc_005', 'Atlanta Climate Solutions', '2025-01-01', '2025-01-31', 5500, 165, 825.00, 5.00, 150.00, 3.0, 4.2, 7, 117.86, 'https://atlantaclimate.com/emergency', 'Age: 25-65, Homeowners', '24/7 Emergency Service', 'Facebook Feed', 'Mobile', '25-65', 'All', 'Atlanta, GA', 'Home Services', 'Home Maintenance', 'home_services', 'smb', 'ACTIVE', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

-- 4. Criar view de análise P0 signals
CREATE OR REPLACE VIEW `{project_id}.facebook_ads.p0_analysis` AS
SELECT 
  campaign_name,
  landing_page_url,
  spend,
  cpc,
  conversion_rate,
  industry,
  location,
  -- P0 Signal Detection
  CASE 
    WHEN cpc > 8.0 AND conversion_rate < 2.0 THEN 'P0_CRITICAL'
    WHEN cpc > 6.0 AND conversion_rate < 2.5 THEN 'P0_HIGH'
    WHEN cpc > 4.0 AND conversion_rate < 3.0 THEN 'P0_MEDIUM'
    ELSE 'NORMAL'
  END as p0_signal_type,
  
  -- Waste Calculation
  CASE 
    WHEN cpc > 8.0 AND conversion_rate < 2.0 THEN spend * 0.5
    WHEN cpc > 6.0 AND conversion_rate < 2.5 THEN spend * 0.3
    WHEN cpc > 4.0 AND conversion_rate < 3.0 THEN spend * 0.2
    ELSE 0
  END as estimated_waste,
  
  -- Urgency Score
  CASE 
    WHEN cpc > 8.0 AND conversion_rate < 2.0 THEN 0.9
    WHEN cpc > 6.0 AND conversion_rate < 2.5 THEN 0.7
    WHEN cpc > 4.0 AND conversion_rate < 3.0 THEN 0.5
    ELSE 0.2
  END as urgency_score,
  
  -- Opportunity Score
  ROUND(
    (spend * 0.4) * 
    CASE WHEN cpc > 6.0 THEN 1.0 ELSE 0.6 END *
    CASE WHEN conversion_rate < 2.0 THEN 1.0 ELSE 0.7 END,
    2
  ) as opportunity_value
  
FROM `{project_id}.facebook_ads.campaigns_insights`
WHERE campaign_status = 'ACTIVE';

-- 5. Query de teste para validar setup
SELECT 
  'BigQuery Setup Validation' as test_name,
  COUNT(*) as total_campaigns,
  COUNT(CASE WHEN p0_signal_type != 'NORMAL' THEN 1 END) as p0_campaigns,
  ROUND(SUM(estimated_waste), 2) as total_waste,
  ROUND(AVG(urgency_score), 3) as avg_urgency
FROM `{project_id}.facebook_ads.p0_analysis`;
"""
    
    sql_file = Path(__file__).parent / "bigquery_setup.sql"
    with open(sql_file, 'w', encoding='utf-8') as f:
        f.write(sql_content)
    
    print(f"✅ SQL file criado: {sql_file}")
    return str(sql_file)

def create_validation_script(project_id):
    """Criar script de validação BigQuery"""
    validation_content = f'''"""
🧪 BIGQUERY VALIDATION - TESTE DE CONFIGURAÇÃO
=============================================
Valida se BigQuery foi configurado corretamente
"""

import os
import sys
from pathlib import Path

# Adicionar path do projeto
sys.path.append(str(Path(__file__).parent.parent / "pipeline_optimized"))

try:
    from google.cloud import bigquery
    from google.oauth2 import service_account
    print("✅ BigQuery SDK disponível")
except ImportError:
    print("❌ BigQuery SDK não instalado")
    print("📦 Execute: pip install google-cloud-bigquery")
    sys.exit(1)

def test_bigquery_connection():
    """Testar conexão BigQuery"""
    project_id = "{project_id}"
    credentials_path = Path(__file__).parent.parent / "pipeline_optimized" / "credentials" / "credentials.json"
    
    print(f"🔍 Testando conexão BigQuery...")
    print(f"📁 Project ID: {{project_id}}")
    print(f"🔑 Credentials: {{credentials_path}}")
    
    # Verificar se arquivo de credenciais existe
    if not credentials_path.exists():
        print("❌ Arquivo credentials.json não encontrado")
        print(f"📁 Esperado em: {{credentials_path}}")
        print("💡 Baixe do Google Cloud Console e coloque no local correto")
        return False
    
    try:
        # Conectar ao BigQuery
        credentials = service_account.Credentials.from_service_account_file(str(credentials_path))
        client = bigquery.Client(credentials=credentials, project=project_id)
        
        # Testar query simples
        query = f"""
        SELECT 
            'BigQuery Connection Test' as test_name,
            CURRENT_TIMESTAMP() as timestamp,
            '{{project_id}}' as project_id
        """
        
        job = client.query(query)
        results = list(job.result())
        
        if results:
            print("✅ Conexão BigQuery: SUCESSO!")
            result = results[0]
            print(f"📊 Test: {{result.test_name}}")
            print(f"⏰ Timestamp: {{result.timestamp}}")
            print(f"📁 Project: {{result.project_id}}")
            return True
        else:
            print("❌ Query não retornou resultados")
            return False
            
    except Exception as e:
        print(f"❌ Erro na conexão BigQuery: {{e}}")
        return False

def test_dataset_access():
    """Testar acesso ao dataset"""
    project_id = "{project_id}"
    dataset_id = "facebook_ads"
    credentials_path = Path(__file__).parent.parent / "pipeline_optimized" / "credentials" / "credentials.json"
    
    try:
        credentials = service_account.Credentials.from_service_account_file(str(credentials_path))
        client = bigquery.Client(credentials=credentials, project=project_id)
        
        # Testar acesso ao dataset
        dataset_ref = client.dataset(dataset_id)
        dataset = client.get_dataset(dataset_ref)
        
        print(f"✅ Dataset acesso: {{dataset.dataset_id}}")
        print(f"📍 Localização: {{dataset.location}}")
        
        # Listar tabelas
        tables = list(client.list_tables(dataset))
        print(f"📊 Tabelas encontradas: {{len(tables)}}")
        
        for table in tables:
            print(f"  📋 {{table.table_id}}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no acesso ao dataset: {{e}}")
        return False

def test_pipeline_integration():
    """Testar integração com pipeline"""
    project_id = "{project_id}"
    credentials_path = Path(__file__).parent.parent / "pipeline_optimized" / "credentials" / "credentials.json"
    
    try:
        credentials = service_account.Credentials.from_service_account_file(str(credentials_path))
        client = bigquery.Client(credentials=credentials, project=project_id)
        
        # Query de teste do pipeline
        query = f"""
        SELECT 
            COUNT(*) as total_campaigns,
            COUNT(CASE WHEN p0_signal_type != 'NORMAL' THEN 1 END) as p0_campaigns,
            ROUND(SUM(estimated_waste), 2) as total_waste,
            ROUND(AVG(urgency_score), 3) as avg_urgency
        FROM `{{project_id}}.facebook_ads.p0_analysis`
        """
        
        job = client.query(query)
        results = list(job.result())
        
        if results:
            result = results[0]
            print("✅ Pipeline Integration: SUCESSO!")
            print(f"📊 Total campaigns: {{result.total_campaigns}}")
            print(f"🚨 P0 campaigns: {{result.p0_campaigns}}")
            print(f"💰 Total waste: ${{result.total_waste:,.2f}}")
            print(f"⚡ Avg urgency: {{result.avg_urgency}}")
            return True
        else:
            print("❌ Pipeline query falhou")
            return False
            
    except Exception as e:
        print(f"❌ Erro na integração pipeline: {{e}}")
        return False

def main():
    """Função principal de validação"""
    print("🧪 BIGQUERY VALIDATION TEST")
    print("=" * 40)
    
    tests = [
        ("Connection Test", test_bigquery_connection),
        ("Dataset Access", test_dataset_access), 
        ("Pipeline Integration", test_pipeline_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\\n🧪 {{test_name}}:")
        try:
            if test_func():
                passed += 1
                print(f"✅ {{test_name}}: PASSOU")
            else:
                print(f"❌ {{test_name}}: FALHOU")
        except Exception as e:
            print(f"❌ {{test_name}}: ERRO - {{e}}")
    
    # Resultado final
    success_rate = (passed / total) * 100
    print(f"\\n📊 RESULTADO FINAL:")
    print(f"✅ Testes passou: {{passed}}/{{total}}")
    print(f"📈 Taxa de sucesso: {{success_rate:.1f}}%")
    
    if success_rate == 100:
        print("\\n🎉 BIGQUERY TOTALMENTE CONFIGURADO!")
        print("🚀 Pipeline pronto para execução com BigQuery")
    elif success_rate >= 50:
        print("\\n⚠️ CONFIGURAÇÃO PARCIAL")
        print("🔧 Alguns ajustes necessários")
    else:
        print("\\n❌ CONFIGURAÇÃO INCOMPLETA")
        print("🛠️ Revise os passos de configuração")

if __name__ == "__main__":
    main()
'''
    
    validation_file = Path(__file__).parent / "validate_bigquery.py"
    with open(validation_file, 'w', encoding='utf-8') as f:
        f.write(validation_content)
    
    print(f"✅ Script de validação criado: {validation_file}")
    return str(validation_file)

def main():
    """Função principal"""
    print_header()
    
    # Setup PATH da sessão
    setup_session_path()
    
    # Testar gcloud (opcional, pode falhar)
    gcloud_works = test_gcloud()
    
    if gcloud_works:
        print("✅ gcloud funcionando - você pode tentar setup automático depois")
    else:
        print("⚠️ gcloud não funcionando - usando setup manual")
    
    # Configuração manual BigQuery
    project_id = create_bigquery_project_manually()
    
    # Criar arquivos auxiliares
    sql_file = create_bigquery_tables_sql(project_id)
    validation_file = create_validation_script(project_id)
    
    print(f"\n🎯 PRÓXIMOS PASSOS:")
    print("=" * 20)
    print("1. 🌐 Complete a configuração manual no Google Cloud Console")
    print("2. 📥 Baixe credentials.json e mova para pipeline_optimized/credentials/")
    print(f"3. 📊 Execute SQL no BigQuery Console: {sql_file}")
    print(f"4. 🧪 Valide configuração: python {validation_file}")
    print("5. 🚀 Execute pipeline: python pipeline_optimized/run_pipeline.py")
    
    print(f"\n✅ ARQUIVOS CRIADOS:")
    print(f"📄 .env atualizado com project ID: {project_id}")
    print(f"📄 SQL setup: {sql_file}")
    print(f"📄 Validation script: {validation_file}")
    
    print(f"\n🎉 SETUP SEM ADMIN CONCLUÍDO!")
    print("⚠️ Requer configuração manual no Google Cloud Console")

if __name__ == "__main__":
    main()
