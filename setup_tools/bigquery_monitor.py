"""
🔧 BIGQUERY DEBUG & MONITORING SYSTEM
=====================================
Sistema avançado para debugging e monitoramento da configuração BigQuery
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import subprocess

# Tentar importar BigQuery (graceful degradation)
try:
    from google.cloud import bigquery
    from google.oauth2 import service_account
    from google.api_core import exceptions as gcp_exceptions
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False

@dataclass
class HealthCheck:
    """Resultado de health check"""
    component: str
    status: str  # OK, WARNING, ERROR
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    response_time_ms: float = 0.0

class BigQueryMonitor:
    """Sistema de monitoramento avançado para BigQuery"""
    
    def __init__(self):
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        self.credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', './credentials/credentials.json')
        self.dataset_id = os.getenv('BIGQUERY_DATASET', 'facebook_ads')
        
        self.client: Optional[bigquery.Client] = None
        self.health_checks: List[HealthCheck] = []
        
    def log_health_check(self, component: str, status: str, message: str, details: Dict = None):
        """Registrar resultado de health check"""
        check = HealthCheck(
            component=component,
            status=status,
            message=message,
            details=details or {},
            timestamp=datetime.now()
        )
        self.health_checks.append(check)
        
        # Color coding para output
        colors = {
            'OK': '\033[92m✅',
            'WARNING': '\033[93m⚠️',
            'ERROR': '\033[91m❌'
        }
        color = colors.get(status, '🔍')
        
        print(f"{color} {component}: {message}\033[0m")
        
        if details:
            for key, value in details.items():
                print(f"   📋 {key}: {value}")
    
    def check_environment_variables(self) -> bool:
        """Verificar variáveis de ambiente"""
        start_time = time.time()
        
        required_vars = {
            'GOOGLE_CLOUD_PROJECT': self.project_id,
            'GOOGLE_APPLICATION_CREDENTIALS': self.credentials_path,
            'BIGQUERY_DATASET': self.dataset_id
        }
        
        missing_vars = []
        details = {}
        
        for var_name, var_value in required_vars.items():
            if not var_value:
                missing_vars.append(var_name)
            else:
                details[var_name] = var_value
        
        response_time = (time.time() - start_time) * 1000
        
        if missing_vars:
            self.log_health_check(
                'Environment Variables',
                'ERROR',
                f'Variáveis ausentes: {", ".join(missing_vars)}',
                details
            )
            return False
        else:
            self.log_health_check(
                'Environment Variables',
                'OK',
                'Todas variáveis configuradas',
                details
            )
            return True
    
    def check_credentials_file(self) -> bool:
        """Verificar arquivo de credenciais"""
        start_time = time.time()
        
        if not os.path.exists(self.credentials_path):
            self.log_health_check(
                'Credentials File',
                'ERROR',
                f'Arquivo não encontrado: {self.credentials_path}',
                {'expected_path': self.credentials_path}
            )
            return False
        
        try:
            with open(self.credentials_path, 'r') as f:
                cred_data = json.load(f)
            
            required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
            missing_fields = [field for field in required_fields if field not in cred_data]
            
            response_time = (time.time() - start_time) * 1000
            
            if missing_fields:
                self.log_health_check(
                    'Credentials File',
                    'ERROR',
                    f'Campos ausentes: {", ".join(missing_fields)}',
                    {
                        'file_path': self.credentials_path,
                        'missing_fields': missing_fields,
                        'response_time_ms': response_time
                    }
                )
                return False
            else:
                file_size = os.path.getsize(self.credentials_path)
                self.log_health_check(
                    'Credentials File',
                    'OK',
                    'Arquivo válido e completo',
                    {
                        'file_path': self.credentials_path,
                        'file_size_bytes': file_size,
                        'service_account': cred_data.get('client_email', 'N/A'),
                        'project_id': cred_data.get('project_id', 'N/A'),
                        'response_time_ms': response_time
                    }
                )
                return True
                
        except json.JSONDecodeError as e:
            self.log_health_check(
                'Credentials File',
                'ERROR',
                f'JSON inválido: {e}',
                {'file_path': self.credentials_path}
            )
            return False
        except Exception as e:
            self.log_health_check(
                'Credentials File',
                'ERROR',
                f'Erro inesperado: {e}',
                {'file_path': self.credentials_path}
            )
            return False
    
    def check_bigquery_connectivity(self) -> bool:
        """Testar conectividade com BigQuery"""
        if not BIGQUERY_AVAILABLE:
            self.log_health_check(
                'BigQuery SDK',
                'ERROR',
                'SDK não instalado',
                {'required_package': 'google-cloud-bigquery'}
            )
            return False
        
        start_time = time.time()
        
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path
            )
            self.client = bigquery.Client(
                credentials=credentials, 
                project=self.project_id
            )
            
            # Teste simples de conectividade
            query = "SELECT 1 as test_connection, CURRENT_TIMESTAMP() as test_time"
            job = self.client.query(query)
            results = list(job.result())
            
            response_time = (time.time() - start_time) * 1000
            
            if results:
                result = results[0]
                self.log_health_check(
                    'BigQuery Connectivity',
                    'OK',
                    'Conectividade confirmada',
                    {
                        'project_id': self.project_id,
                        'test_result': result.test_connection,
                        'server_time': str(result.test_time),
                        'response_time_ms': response_time,
                        'job_id': job.job_id
                    }
                )
                return True
            else:
                self.log_health_check(
                    'BigQuery Connectivity',
                    'ERROR',
                    'Query não retornou resultados',
                    {'response_time_ms': response_time}
                )
                return False
                
        except gcp_exceptions.Forbidden as e:
            self.log_health_check(
                'BigQuery Connectivity',
                'ERROR',
                'Acesso negado - verifique permissões',
                {
                    'error_code': e.code,
                    'error_message': str(e),
                    'project_id': self.project_id
                }
            )
            return False
        except gcp_exceptions.NotFound as e:
            self.log_health_check(
                'BigQuery Connectivity',
                'ERROR',
                'Projeto não encontrado',
                {
                    'error_code': e.code,
                    'error_message': str(e),
                    'project_id': self.project_id
                }
            )
            return False
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.log_health_check(
                'BigQuery Connectivity',
                'ERROR',
                f'Erro inesperado: {type(e).__name__}',
                {
                    'error_message': str(e),
                    'response_time_ms': response_time
                }
            )
            return False
    
    def check_dataset_access(self) -> bool:
        """Verificar acesso ao dataset"""
        if not self.client:
            self.log_health_check(
                'Dataset Access',
                'ERROR',
                'Cliente BigQuery não inicializado',
                {}
            )
            return False
        
        start_time = time.time()
        
        try:
            dataset_ref = self.client.dataset(self.dataset_id)
            dataset = self.client.get_dataset(dataset_ref)
            
            response_time = (time.time() - start_time) * 1000
            
            self.log_health_check(
                'Dataset Access',
                'OK',
                f'Dataset acessível: {self.dataset_id}',
                {
                    'dataset_id': self.dataset_id,
                    'location': dataset.location,
                    'created': str(dataset.created),
                    'modified': str(dataset.modified),
                    'response_time_ms': response_time
                }
            )
            return True
            
        except gcp_exceptions.NotFound:
            response_time = (time.time() - start_time) * 1000
            self.log_health_check(
                'Dataset Access',
                'WARNING',
                f'Dataset não encontrado: {self.dataset_id}',
                {
                    'dataset_id': self.dataset_id,
                    'response_time_ms': response_time,
                    'solution': 'Execute: bq mk --location=us-central1 ' + self.dataset_id
                }
            )
            return False
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.log_health_check(
                'Dataset Access',
                'ERROR',
                f'Erro ao acessar dataset: {e}',
                {
                    'dataset_id': self.dataset_id,
                    'error_type': type(e).__name__,
                    'response_time_ms': response_time
                }
            )
            return False
    
    def check_table_structure(self) -> bool:
        """Verificar estrutura das tabelas"""
        if not self.client:
            return False
            
        start_time = time.time()
        
        # Tabelas esperadas
        expected_tables = {
            'campaigns_insights': [
                'account_id', 'campaign_id', 'campaign_name', 'spend', 
                'impressions', 'clicks', 'conversions', 'landing_page_url'
            ]
        }
        
        tables_status = {}
        
        for table_name, expected_columns in expected_tables.items():
            try:
                table_ref = self.client.dataset(self.dataset_id).table(table_name)
                table = self.client.get_table(table_ref)
                
                actual_columns = [field.name for field in table.schema]
                missing_columns = [col for col in expected_columns if col not in actual_columns]
                
                if missing_columns:
                    tables_status[table_name] = {
                        'status': 'WARNING',
                        'message': f'Colunas ausentes: {missing_columns}',
                        'actual_columns': actual_columns,
                        'missing_columns': missing_columns
                    }
                else:
                    tables_status[table_name] = {
                        'status': 'OK',
                        'message': 'Estrutura correta',
                        'columns_count': len(actual_columns),
                        'rows_count': table.num_rows
                    }
                    
            except gcp_exceptions.NotFound:
                tables_status[table_name] = {
                    'status': 'WARNING',
                    'message': 'Tabela não encontrada',
                    'solution': f'Execute o SQL de setup para criar {table_name}'
                }
            except Exception as e:
                tables_status[table_name] = {
                    'status': 'ERROR',
                    'message': f'Erro: {e}',
                    'error_type': type(e).__name__
                }
        
        response_time = (time.time() - start_time) * 1000
        
        # Consolidar status
        has_errors = any(t['status'] == 'ERROR' for t in tables_status.values())
        has_warnings = any(t['status'] == 'WARNING' for t in tables_status.values())
        
        if has_errors:
            overall_status = 'ERROR'
            message = 'Erros na estrutura das tabelas'
        elif has_warnings:
            overall_status = 'WARNING'
            message = 'Algumas tabelas precisam ser criadas/ajustadas'
        else:
            overall_status = 'OK'
            message = 'Estrutura das tabelas válida'
        
        self.log_health_check(
            'Table Structure',
            overall_status,
            message,
            {
                'tables_checked': list(expected_tables.keys()),
                'tables_status': tables_status,
                'response_time_ms': response_time
            }
        )
        
        return overall_status == 'OK'
    
    def check_performance_metrics(self) -> bool:
        """Verificar métricas de performance"""
        if not self.client:
            return False
            
        start_time = time.time()
        
        try:
            # Query simples para testar performance
            query = """
            SELECT 
                COUNT(*) as total_campaigns,
                AVG(spend) as avg_spend,
                MAX(created_time) as latest_data
            FROM `{}.{}.campaigns_insights`
            WHERE DATE(created_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
            """.format(self.project_id, self.dataset_id)
            
            job = self.client.query(query)
            results = list(job.result())
            
            response_time = (time.time() - start_time) * 1000
            
            if results:
                result = results[0]
                
                # Analisar job statistics
                job_stats = job._properties.get('statistics', {})
                query_stats = job_stats.get('query', {})
                
                bytes_processed = int(query_stats.get('totalBytesProcessed', 0))
                slot_ms = int(query_stats.get('totalSlotMs', 0))
                
                self.log_health_check(
                    'Performance Metrics',
                    'OK',
                    'Métricas coletadas com sucesso',
                    {
                        'total_campaigns': result.total_campaigns,
                        'avg_spend': float(result.avg_spend) if result.avg_spend else 0,
                        'latest_data': str(result.latest_data) if result.latest_data else 'N/A',
                        'query_time_ms': response_time,
                        'bytes_processed': bytes_processed,
                        'slot_ms': slot_ms,
                        'cost_estimate_usd': (bytes_processed / 1024**4) * 6.25  # $6.25 per TB
                    }
                )
                return True
            else:
                self.log_health_check(
                    'Performance Metrics',
                    'WARNING',
                    'Nenhum dado encontrado para análise',
                    {'response_time_ms': response_time}
                )
                return False
                
        except gcp_exceptions.NotFound:
            self.log_health_check(
                'Performance Metrics',
                'WARNING',
                'Tabela de dados não encontrada',
                {'table_name': 'campaigns_insights'}
            )
            return False
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.log_health_check(
                'Performance Metrics',
                'ERROR',
                f'Erro na análise: {e}',
                {
                    'error_type': type(e).__name__,
                    'response_time_ms': response_time
                }
            )
            return False
    
    def run_comprehensive_check(self) -> Dict[str, Any]:
        """Executar verificação completa"""
        print("\n🔧 BIGQUERY COMPREHENSIVE HEALTH CHECK")
        print("=" * 60)
        
        # Lista de checks a executar
        checks = [
            ('Environment Variables', self.check_environment_variables),
            ('Credentials File', self.check_credentials_file),
            ('BigQuery Connectivity', self.check_bigquery_connectivity),
            ('Dataset Access', self.check_dataset_access),
            ('Table Structure', self.check_table_structure),
            ('Performance Metrics', self.check_performance_metrics)
        ]
        
        results = {}
        total_checks = len(checks)
        passed_checks = 0
        
        for check_name, check_func in checks:
            try:
                result = check_func()
                results[check_name] = result
                if result:
                    passed_checks += 1
            except Exception as e:
                self.log_health_check(
                    check_name,
                    'ERROR',
                    f'Falha na execução: {e}',
                    {'exception_type': type(e).__name__}
                )
                results[check_name] = False
        
        # Resumo final
        print(f"\n📊 RESUMO FINAL:")
        print("=" * 30)
        
        success_rate = (passed_checks / total_checks) * 100
        
        if success_rate >= 80:
            status_color = '\033[92m'  # Verde
            status_icon = '✅'
            status_text = 'SISTEMA SAUDÁVEL'
        elif success_rate >= 60:
            status_color = '\033[93m'  # Amarelo
            status_icon = '⚠️'
            status_text = 'REQUER ATENÇÃO'
        else:
            status_color = '\033[91m'  # Vermelho
            status_icon = '❌'
            status_text = 'CRÍTICO'
        
        print(f"{status_color}{status_icon} {status_text}: {passed_checks}/{total_checks} checks passaram ({success_rate:.1f}%)\033[0m")
        
        # Salvar relatório
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_checks': total_checks,
                'passed_checks': passed_checks,
                'success_rate': success_rate,
                'status': status_text
            },
            'check_results': results,
            'health_checks': [asdict(hc) for hc in self.health_checks]
        }
        
        report_path = Path(__file__).parent / 'bigquery_health_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📋 Relatório detalhado salvo: {report_path}")
        
        return report

def main():
    """Função principal do monitor"""
    monitor = BigQueryMonitor()
    report = monitor.run_comprehensive_check()
    
    # Exit code baseado no resultado
    success_rate = report['summary']['success_rate']
    exit_code = 0 if success_rate >= 80 else 1
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
