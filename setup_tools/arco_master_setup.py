"""
🚀 ARCO SETUP COMPLETO - ORQUESTRADOR MASTER
===========================================
Executa todo o setup e validação do sistema ARCO em sequência
Detecta automaticamente o que está configurado e o que precisa ser feito
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class ARCOOrchestrator:
    """Orquestrador completo do setup ARCO"""
    
    def __init__(self):
        self.root_path = Path(__file__).parent
        self.setup_status = {}
        
    def print_header(self, text: str):
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
        print(f"🚀 {text}")
        print(f"{'='*70}{Colors.ENDC}")
    
    def print_step(self, step: str, status: str = "INFO"):
        colors = {
            'INFO': f'{Colors.CYAN}ℹ️',
            'SUCCESS': f'{Colors.GREEN}✅',
            'WARNING': f'{Colors.WARNING}⚠️',
            'ERROR': f'{Colors.FAIL}❌',
            'RUNNING': f'{Colors.BLUE}🔄'
        }
        
        color = colors.get(status, '🔍')
        print(f"{color} {step}{Colors.ENDC}")
    
    def run_script(self, script_name: str, description: str, required: bool = True) -> Tuple[bool, str]:
        """Executar script Python e retornar status"""
        script_path = self.root_path / script_name
        
        if not script_path.exists():
            self.print_step(f"{description}: Script não encontrado", "ERROR")
            return False, f"Script {script_name} não encontrado"
        
        self.print_step(f"Executando: {description}", "RUNNING")
        
        try:
            # Executar script
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            if result.returncode == 0:
                self.print_step(f"{description}: Sucesso", "SUCCESS")
                return True, result.stdout
            else:
                self.print_step(f"{description}: Falhou (código {result.returncode})", "ERROR")
                if result.stderr:
                    print(f"   {Colors.FAIL}Erro: {result.stderr[:200]}...{Colors.ENDC}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            self.print_step(f"{description}: Timeout (>5min)", "ERROR")
            return False, "Timeout"
        except Exception as e:
            self.print_step(f"{description}: Exceção - {e}", "ERROR")
            return False, str(e)
    
    def check_prerequisites(self) -> Dict[str, bool]:
        """Verificar pré-requisitos do sistema"""
        self.print_header("VERIFICAÇÃO DE PRÉ-REQUISITOS")
        
        checks = {}
        
        # 1. Python dependencies
        self.print_step("Verificando dependências Python...", "RUNNING")
        try:
            import google.cloud.bigquery
            import aiohttp
            import requests
            from dotenv import load_dotenv
            checks['python_deps'] = True
            self.print_step("Dependências Python: OK", "SUCCESS")
        except ImportError as e:
            checks['python_deps'] = False
            self.print_step(f"Dependências Python: Faltando {e}", "ERROR")
        
        # 2. Environment variables
        self.print_step("Verificando variáveis de ambiente...", "RUNNING")
        env_vars = ['SEARCHAPI_KEY', 'PAGESPEED_KEY']
        missing_vars = [var for var in env_vars if not os.getenv(var)]
        
        if not missing_vars:
            checks['env_vars'] = True
            self.print_step("Variáveis de ambiente: OK", "SUCCESS")
        else:
            checks['env_vars'] = False
            self.print_step(f"Variáveis faltando: {', '.join(missing_vars)}", "WARNING")
        
        # 3. gcloud CLI
        self.print_step("Verificando gcloud CLI...", "RUNNING")
        try:
            result = subprocess.run(['gcloud', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                checks['gcloud_cli'] = True
                self.print_step("gcloud CLI: Disponível", "SUCCESS")
            else:
                checks['gcloud_cli'] = False
                self.print_step("gcloud CLI: Não encontrado", "WARNING")
        except:
            checks['gcloud_cli'] = False
            self.print_step("gcloud CLI: Não encontrado", "WARNING")
        
        # 4. BigQuery credentials
        creds_path = self.root_path / 'credentials' / 'credentials.json'
        if creds_path.exists():
            checks['bigquery_creds'] = True
            self.print_step("Credenciais BigQuery: Encontradas", "SUCCESS")
        else:
            checks['bigquery_creds'] = False
            self.print_step("Credenciais BigQuery: Não encontradas", "WARNING")
        
        return checks
    
    def execute_setup_sequence(self, checks: Dict[str, bool]) -> bool:
        """Executar sequência de setup baseada nos checks"""
        self.print_header("SEQUÊNCIA DE SETUP AUTOMÁTICO")
        
        success_count = 0
        total_steps = 0
        
        # Etapa 1: Setup BigQuery (se necessário)
        if not checks.get('bigquery_creds', False):
            total_steps += 1
            if checks.get('gcloud_cli', False):
                self.print_step("BigQuery não configurado - usando setup automático gcloud", "INFO")
                success, output = self.run_script('bigquery_gcloud_setup.py', 'Setup BigQuery Automático')
                if success:
                    success_count += 1
                    # Aguardar um pouco para APIs se propagarem
                    time.sleep(5)
            else:
                self.print_step("BigQuery não configurado - execute setup manual", "WARNING")
                print(f"   {Colors.CYAN}Execute: python bigquery_setup_wizard.py{Colors.ENDC}")
        else:
            self.print_step("BigQuery já configurado - pulando setup", "INFO")
        
        # Etapa 2: Teste de conectividade de APIs
        total_steps += 1
        success, output = self.run_script('test_api_connections.py', 'Teste de Conectividade APIs')
        if success:
            success_count += 1
        
        # Etapa 3: Teste de integração BigQuery
        total_steps += 1
        success, output = self.run_script('bigquery_integration_tester.py', 'Teste Integração BigQuery')
        if success:
            success_count += 1
        
        # Etapa 4: Validação completa do pipeline
        total_steps += 1
        success, output = self.run_script('arco_pipeline_validator.py', 'Validação Completa Pipeline')
        if success:
            success_count += 1
        
        # Calcular taxa de sucesso
        success_rate = (success_count / total_steps) * 100 if total_steps > 0 else 0
        
        self.print_header("RESULTADO DO SETUP")
        print(f"📊 {Colors.BOLD}RESUMO:{Colors.ENDC}")
        print(f"  ✅ Etapas concluídas: {success_count}/{total_steps}")
        print(f"  📈 Taxa de sucesso: {success_rate:.1f}%")
        
        return success_rate >= 75
    
    def provide_next_steps(self, setup_successful: bool, checks: Dict[str, bool]):
        """Fornecer próximos passos baseados no status"""
        self.print_header("PRÓXIMOS PASSOS")
        
        if setup_successful:
            print(f"{Colors.GREEN}🎉 SISTEMA ARCO PRONTO PARA USO!{Colors.ENDC}")
            print(f"\n{Colors.CYAN}📋 COMANDOS PARA EXECUTAR:{Colors.ENDC}")
            print(f"  1. 🔍 Discovery de leads:")
            print(f"     {Colors.CYAN}python real_lead_discovery.py{Colors.ENDC}")
            print(f"  2. 🎯 Pipeline SMB completo:")
            print(f"     {Colors.CYAN}python pipeline_optimized/smb_pipeline_corrected.py{Colors.ENDC}")
            print(f"  3. 🚀 Engine de produção:")
            print(f"     {Colors.CYAN}python production/engines/arco_core.py{Colors.ENDC}")
            
            print(f"\n{Colors.CYAN}📊 MONITORAMENTO:{Colors.ENDC}")
            print(f"  • Health reports em: bigquery_health_report.json")
            print(f"  • Validation reports em: arco_pipeline_validation_report.json")
            
        else:
            print(f"{Colors.WARNING}⚠️ CONFIGURAÇÃO PARCIAL - AÇÕES NECESSÁRIAS{Colors.ENDC}")
            
            if not checks.get('python_deps', False):
                print(f"\n{Colors.FAIL}❌ DEPENDÊNCIAS PYTHON:{Colors.ENDC}")
                print(f"   {Colors.CYAN}pip install -r requirements.txt{Colors.ENDC}")
            
            if not checks.get('env_vars', False):
                print(f"\n{Colors.FAIL}❌ VARIÁVEIS DE AMBIENTE:{Colors.ENDC}")
                print(f"   1. Copie .env.example para .env")
                print(f"   2. Configure SEARCHAPI_KEY e PAGESPEED_KEY")
            
            if not checks.get('bigquery_creds', False):
                print(f"\n{Colors.FAIL}❌ BIGQUERY CONFIGURAÇÃO:{Colors.ENDC}")
                if checks.get('gcloud_cli', False):
                    print(f"   {Colors.CYAN}python bigquery_gcloud_setup.py{Colors.ENDC}")
                else:
                    print(f"   {Colors.CYAN}python bigquery_setup_wizard.py{Colors.ENDC}")
            
            print(f"\n{Colors.CYAN}🔁 APÓS CORRIGIR:{Colors.ENDC}")
            print(f"   {Colors.CYAN}python arco_master_setup.py{Colors.ENDC}")
    
    def create_status_file(self, checks: Dict[str, bool], setup_successful: bool):
        """Criar arquivo de status do setup"""
        status = {
            'timestamp': time.time(),
            'setup_completed': setup_successful,
            'prerequisites': checks,
            'next_action': 'production' if setup_successful else 'configuration',
            'ready_for_production': setup_successful
        }
        
        status_file = self.root_path / 'arco_setup_status.json'
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        self.print_step(f"Status salvo em: {status_file}", "INFO")
    
    def run_complete_setup(self):
        """Executar setup completo do ARCO"""
        self.print_header("ARCO - SETUP COMPLETO AUTOMÁTICO")
        
        print(f"{Colors.BLUE}🎯 Inicializando setup completo do sistema ARCO...{Colors.ENDC}")
        print(f"{Colors.BLUE}Este processo irá configurar e validar todo o pipeline.{Colors.ENDC}")
        
        # 1. Verificar pré-requisitos
        checks = self.check_prerequisites()
        
        # 2. Executar setup
        setup_successful = self.execute_setup_sequence(checks)
        
        # 3. Fornecer próximos passos
        self.provide_next_steps(setup_successful, checks)
        
        # 4. Salvar status
        self.create_status_file(checks, setup_successful)
        
        return setup_successful

def main():
    """Função principal"""
    orchestrator = ARCOOrchestrator()
    success = orchestrator.run_complete_setup()
    
    # Exit code baseado no sucesso
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
