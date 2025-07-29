"""
🧪 BIGQUERY INTEGRATION TESTER
==============================
Testes progressivos durante e após configuração do BigQuery
Sistema adaptativo que funciona em qualquer estágio do setup
"""

import asyncio
import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import aiohttp

# Tentar importar BigQuery (graceful degradation)
try:
    from google.cloud import bigquery
    from google.oauth2 import service_account
    from google.api_core import exceptions as gcp_exceptions
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False

from dotenv import load_dotenv
load_dotenv()

@dataclass
class TestResult:
    """Resultado de um teste"""
    name: str
    status: str  # PASS, FAIL, SKIP, WARN
    message: str
    duration_ms: float
    details: Dict = None

class ProgressiveBigQueryTester:
    """Tester que adapta aos diferentes estágios de configuração"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.searchapi_key = os.getenv('SEARCHAPI_KEY')
        self.pagespeed_key = os.getenv('PAGESPEED_KEY')
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        self.credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', './credentials/credentials.json')
        self.dataset_id = os.getenv('BIGQUERY_DATASET', 'facebook_ads')
        
    def log_result(self, name: str, status: str, message: str, duration: float = 0, details: Dict = None):
        """Registrar resultado de teste"""
        result = TestResult(name, status, message, duration, details or {})
        self.results.append(result)
        
        # Color coding
        colors = {
            'PASS': '\033[92m✅',
            'FAIL': '\033[91m❌', 
            'SKIP': '\033[94m⏩',
            'WARN': '\033[93m⚠️'
        }
        
        color = colors.get(status, '🔍')
        print(f"{color} {name}: {message}\033[0m")
        
        if details and status in ['FAIL', 'WARN']:
            for key, value in details.items():
                print(f"   📋 {key}: {value}")
    
    async def test_environment_setup(self) -> bool:
        """Teste 1: Verificar setup do ambiente"""
        start_time = time.time()
        
        env_vars = {
            'SEARCHAPI_KEY': self.searchapi_key,
            'PAGESPEED_KEY': self.pagespeed_key,
            'GOOGLE_CLOUD_PROJECT': self.project_id,
            'GOOGLE_APPLICATION_CREDENTIALS': self.credentials_path
        }
        
        missing = [k for k, v in env_vars.items() if not v]
        configured = [k for k, v in env_vars.items() if v]
        
        duration = (time.time() - start_time) * 1000
        
        if not missing:
            self.log_result(
                "Environment Setup",
                "PASS", 
                "Todas variáveis configuradas",
                duration,
                {'configured': configured}
            )
            return True
        elif len(configured) >= 2:
            self.log_result(
                "Environment Setup",
                "WARN",
                f"Parcialmente configurado: {len(configured)}/4",
                duration,
                {'configured': configured, 'missing': missing}
            )
            return True
        else:
            self.log_result(
                "Environment Setup", 
                "FAIL",
                "Muitas variáveis ausentes",
                duration,
                {'missing': missing}
            )
            return False
    
    async def test_searchapi_connectivity(self) -> bool:
        """Teste 2: Conectividade SearchAPI"""
        if not self.searchapi_key:
            self.log_result("SearchAPI", "SKIP", "Chave não configurada")
            return False
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://www.searchapi.io/api/v1/search"
                params = {
                    'api_key': self.searchapi_key,
                    'engine': 'google',
                    'q': 'bigquery test',
                    'num': 1
                }
                
                async with session.get(url, params=params, timeout=10) as response:
                    duration = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        results_count = len(data.get('organic_results', []))
                        
                        self.log_result(
                            "SearchAPI",
                            "PASS",
                            f"Conectado - {results_count} resultados",
                            duration,
                            {'status_code': response.status, 'results': results_count}
                        )
                        return True
                    else:
                        self.log_result(
                            "SearchAPI",
                            "FAIL", 
                            f"Erro HTTP {response.status}",
                            duration,
                            {'status_code': response.status}
                        )
                        return False
                        
        except asyncio.TimeoutError:
            duration = (time.time() - start_time) * 1000
            self.log_result("SearchAPI", "FAIL", "Timeout", duration)
            return False
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self.log_result("SearchAPI", "FAIL", f"Exceção: {e}", duration)
            return False
    
    async def test_pagespeed_connectivity(self) -> bool:
        """Teste 3: Conectividade PageSpeed API"""
        if not self.pagespeed_key:
            self.log_result("PageSpeed API", "SKIP", "Chave não configurada")
            return False
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
                params = {
                    'url': 'https://example.com',
                    'key': self.pagespeed_key,
                    'category': 'performance',
                    'strategy': 'mobile'
                }
                
                async with session.get(url, params=params, timeout=20) as response:
                    duration = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        score = data.get('lighthouseResult', {}).get('categories', {}).get('performance', {}).get('score')
                        score_percent = int(score * 100) if score else 0
                        
                        self.log_result(
                            "PageSpeed API",
                            "PASS",
                            f"Conectado - Score: {score_percent}%",
                            duration,
                            {'status_code': response.status, 'performance_score': score_percent}
                        )
                        return True
                    else:
                        self.log_result(
                            "PageSpeed API",
                            "FAIL",
                            f"Erro HTTP {response.status}",
                            duration,
                            {'status_code': response.status}
                        )
                        return False
                        
        except asyncio.TimeoutError:
            duration = (time.time() - start_time) * 1000
            self.log_result("PageSpeed API", "FAIL", "Timeout", duration)
            return False
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self.log_result("PageSpeed API", "FAIL", f"Exceção: {e}", duration)
            return False
    
    def test_bigquery_sdk(self) -> bool:
        """Teste 4: SDK BigQuery"""
        start_time = time.time()
        
        if not BIGQUERY_AVAILABLE:
            duration = (time.time() - start_time) * 1000
            self.log_result(
                "BigQuery SDK",
                "FAIL",
                "SDK não instalado",
                duration,
                {'install_command': 'pip install google-cloud-bigquery'}
            )
            return False
        
        duration = (time.time() - start_time) * 1000
        self.log_result("BigQuery SDK", "PASS", "SDK disponível", duration)
        return True
    
    def test_credentials_file(self) -> bool:
        """Teste 5: Arquivo de credenciais"""
        start_time = time.time()
        
        if not os.path.exists(self.credentials_path):
            duration = (time.time() - start_time) * 1000
            self.log_result(
                "Credentials File",
                "FAIL",
                f"Arquivo não encontrado: {self.credentials_path}",
                duration,
                {'expected_path': self.credentials_path}
            )
            return False
        
        try:
            with open(self.credentials_path, 'r') as f:
                cred_data = json.load(f)
            
            required_fields = ['type', 'project_id', 'private_key', 'client_email']
            missing = [f for f in required_fields if f not in cred_data]
            
            duration = (time.time() - start_time) * 1000
            
            if missing:
                self.log_result(
                    "Credentials File",
                    "FAIL",
                    f"Campos ausentes: {missing}",
                    duration,
                    {'missing_fields': missing}
                )
                return False
            else:
                self.log_result(
                    "Credentials File",
                    "PASS",
                    "Arquivo válido",
                    duration,
                    {
                        'service_account': cred_data.get('client_email'),
                        'project_id': cred_data.get('project_id')
                    }
                )
                return True
                
        except json.JSONDecodeError:
            duration = (time.time() - start_time) * 1000
            self.log_result("Credentials File", "FAIL", "JSON inválido", duration)
            return False
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self.log_result("Credentials File", "FAIL", f"Erro: {e}", duration)
            return False
    
    def test_bigquery_connection(self) -> bool:
        """Teste 6: Conexão BigQuery"""
        if not BIGQUERY_AVAILABLE:
            self.log_result("BigQuery Connection", "SKIP", "SDK não disponível")
            return False
            
        if not self.project_id:
            self.log_result("BigQuery Connection", "SKIP", "Project ID não configurado")
            return False
            
        if not os.path.exists(self.credentials_path):
            self.log_result("BigQuery Connection", "SKIP", "Credenciais não encontradas")
            return False
        
        start_time = time.time()
        
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path
            )
            client = bigquery.Client(credentials=credentials, project=self.project_id)
            
            # Teste de conectividade simples
            query = "SELECT 1 as test, CURRENT_TIMESTAMP() as timestamp"
            job = client.query(query)
            results = list(job.result())
            
            duration = (time.time() - start_time) * 1000
            
            if results:
                result = results[0]
                self.log_result(
                    "BigQuery Connection",
                    "PASS",
                    "Conectado com sucesso",
                    duration,
                    {
                        'project_id': self.project_id,
                        'server_time': str(result.timestamp),
                        'job_id': job.job_id
                    }
                )
                return True
            else:
                self.log_result("BigQuery Connection", "FAIL", "Query sem resultados", duration)
                return False
                
        except gcp_exceptions.Forbidden:
            duration = (time.time() - start_time) * 1000
            self.log_result(
                "BigQuery Connection",
                "FAIL", 
                "Acesso negado - verifique permissões",
                duration,
                {'project_id': self.project_id}
            )
            return False
        except gcp_exceptions.NotFound:
            duration = (time.time() - start_time) * 1000
            self.log_result(
                "BigQuery Connection",
                "FAIL",
                "Projeto não encontrado",
                duration,
                {'project_id': self.project_id}
            )
            return False
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self.log_result(
                "BigQuery Connection",
                "FAIL",
                f"Erro: {type(e).__name__}",
                duration,
                {'error': str(e)}
            )
            return False
    
    def test_dataset_access(self) -> bool:
        """Teste 7: Acesso ao dataset"""
        if not BIGQUERY_AVAILABLE or not self.project_id or not os.path.exists(self.credentials_path):
            self.log_result("Dataset Access", "SKIP", "Pré-requisitos não atendidos")
            return False
        
        start_time = time.time()
        
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path
            )
            client = bigquery.Client(credentials=credentials, project=self.project_id)
            
            dataset_ref = client.dataset(self.dataset_id)
            dataset = client.get_dataset(dataset_ref)
            
            duration = (time.time() - start_time) * 1000
            
            self.log_result(
                "Dataset Access",
                "PASS",
                f"Dataset acessível: {self.dataset_id}",
                duration,
                {
                    'dataset_id': self.dataset_id,
                    'location': dataset.location,
                    'created': str(dataset.created)
                }
            )
            return True
            
        except gcp_exceptions.NotFound:
            duration = (time.time() - start_time) * 1000
            self.log_result(
                "Dataset Access",
                "WARN",
                f"Dataset não encontrado: {self.dataset_id}",
                duration,
                {
                    'dataset_id': self.dataset_id,
                    'solution': f'Execute: bq mk --location=us-central1 {self.dataset_id}'
                }
            )
            return False
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self.log_result(
                "Dataset Access",
                "FAIL",
                f"Erro: {e}",
                duration,
                {'dataset_id': self.dataset_id}
            )
            return False
    
    def test_table_access(self) -> bool:
        """Teste 8: Acesso às tabelas"""
        if not BIGQUERY_AVAILABLE or not self.project_id or not os.path.exists(self.credentials_path):
            self.log_result("Table Access", "SKIP", "Pré-requisitos não atendidos")
            return False
        
        start_time = time.time()
        
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path
            )
            client = bigquery.Client(credentials=credentials, project=self.project_id)
            
            table_ref = client.dataset(self.dataset_id).table('campaigns_insights')
            table = client.get_table(table_ref)
            
            duration = (time.time() - start_time) * 1000
            
            self.log_result(
                "Table Access",
                "PASS",
                f"Tabela acessível: campaigns_insights",
                duration,
                {
                    'table_name': 'campaigns_insights',
                    'schema_fields': len(table.schema),
                    'num_rows': table.num_rows
                }
            )
            return True
            
        except gcp_exceptions.NotFound:
            duration = (time.time() - start_time) * 1000
            self.log_result(
                "Table Access",
                "WARN",
                "Tabela não encontrada: campaigns_insights",
                duration,
                {'solution': 'Execute os SQLs de criação da tabela'}
            )
            return False
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self.log_result(
                "Table Access",
                "FAIL",
                f"Erro: {e}",
                duration
            )
            return False
    
    async def test_pipeline_integration(self) -> bool:
        """Teste 9: Integração completa do pipeline"""
        if not all([self.searchapi_key, self.pagespeed_key, BIGQUERY_AVAILABLE, 
                   self.project_id, os.path.exists(self.credentials_path)]):
            self.log_result("Pipeline Integration", "SKIP", "Nem todos componentes disponíveis")
            return False
        
        start_time = time.time()
        
        try:
            # Teste de query combinada (simulando pipeline real)
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path
            )
            client = bigquery.Client(credentials=credentials, project=self.project_id)
            
            query = f"""
            SELECT 
                campaign_name,
                landing_page_url,
                spend,
                cpc,
                conversion_rate,
                CASE 
                    WHEN cpc > 3.0 AND conversion_rate < 2.0 THEN 'P0_CRITICAL'
                    WHEN cpc > 2.5 AND conversion_rate < 2.5 THEN 'P0_WARNING'
                    ELSE 'NORMAL'
                END as p0_signal
            FROM `{self.project_id}.{self.dataset_id}.campaigns_insights`
            WHERE campaign_status = 'ACTIVE'
            LIMIT 5
            """
            
            job = client.query(query)
            results = list(job.result())
            
            duration = (time.time() - start_time) * 1000
            
            # Contar P0 signals
            p0_signals = [r for r in results if r.p0_signal != 'NORMAL']
            
            self.log_result(
                "Pipeline Integration",
                "PASS",
                f"Query de pipeline executada - {len(p0_signals)} P0 signals",
                duration,
                {
                    'total_campaigns': len(results),
                    'p0_signals': len(p0_signals),
                    'query_time_ms': duration
                }
            )
            return True
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self.log_result(
                "Pipeline Integration",
                "FAIL",
                f"Erro na integração: {e}",
                duration
            )
            return False
    
    async def run_progressive_tests(self):
        """Executar todos os testes progressivamente"""
        print("\n🧪 BIGQUERY PROGRESSIVE INTEGRATION TESTS")
        print("=" * 60)
        print("Testando configuração em estágios progressivos...\n")
        
        # Lista de testes em ordem progressiva
        tests = [
            ("Environment Setup", self.test_environment_setup),
            ("SearchAPI Connectivity", self.test_searchapi_connectivity),
            ("PageSpeed API", self.test_pagespeed_connectivity),
            ("BigQuery SDK", lambda: self.test_bigquery_sdk()),
            ("Credentials File", lambda: self.test_credentials_file()),
            ("BigQuery Connection", lambda: self.test_bigquery_connection()),
            ("Dataset Access", lambda: self.test_dataset_access()),
            ("Table Access", lambda: self.test_table_access()),
            ("Pipeline Integration", self.test_pipeline_integration)
        ]
        
        passed = 0
        failed = 0
        skipped = 0
        warnings = 0
        
        for test_name, test_func in tests:
            try:
                if asyncio.iscoroutinefunction(test_func):
                    result = await test_func()
                else:
                    result = test_func()
                
                # Contar baseado no último resultado registrado
                last_result = self.results[-1] if self.results else None
                if last_result:
                    if last_result.status == 'PASS':
                        passed += 1
                    elif last_result.status == 'FAIL':
                        failed += 1
                    elif last_result.status == 'SKIP':
                        skipped += 1
                    elif last_result.status == 'WARN':
                        warnings += 1
                        
            except Exception as e:
                self.log_result(test_name, "FAIL", f"Exceção inesperada: {e}")
                failed += 1
        
        # Resumo final
        total = len(tests)
        print(f"\n📊 RESUMO DOS TESTES:")
        print("=" * 30)
        print(f"✅ Passou: {passed}")
        print(f"❌ Falhou: {failed}")
        print(f"⚠️ Avisos: {warnings}")
        print(f"⏩ Pulou: {skipped}")
        print(f"📈 Taxa de sucesso: {(passed/(total-skipped)*100):.1f}%" if total > skipped else "N/A")
        
        # Status geral
        if passed >= 6:
            print(f"\n🎉 \033[92mSISTEMA PRONTO PARA PRODUÇÃO!\033[0m")
            status = "READY"
        elif passed >= 3:
            print(f"\n⚡ \033[93mSISTEMA PARCIALMENTE FUNCIONAL\033[0m")
            status = "PARTIAL"
        else:
            print(f"\n🔧 \033[91mREQUER CONFIGURAÇÃO ADICIONAL\033[0m")
            status = "NEEDS_SETUP"
        
        # Salvar relatório
        report = {
            'timestamp': time.time(),
            'status': status,
            'summary': {
                'passed': passed,
                'failed': failed,
                'warnings': warnings,
                'skipped': skipped,
                'total': total
            },
            'test_results': [
                {
                    'name': r.name,
                    'status': r.status,
                    'message': r.message,
                    'duration_ms': r.duration_ms,
                    'details': r.details
                }
                for r in self.results
            ]
        }
        
        report_path = Path(__file__).parent / 'integration_test_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📋 Relatório detalhado: {report_path}")
        
        return status

async def main():
    """Função principal"""
    tester = ProgressiveBigQueryTester()
    status = await tester.run_progressive_tests()
    
    # Exit codes
    exit_codes = {
        'READY': 0,
        'PARTIAL': 1, 
        'NEEDS_SETUP': 2
    }
    
    sys.exit(exit_codes.get(status, 2))

if __name__ == "__main__":
    asyncio.run(main())
