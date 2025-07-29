#!/usr/bin/env python3
"""
🚀 ARCO PIPELINE - EXECUTÁVEL PRINCIPAL
=====================================
Execute para 5 leads qualificados dentro do ICP
Isolated pipeline with all dependencies included
BigQuery integration enabled
"""

import asyncio
import sys
import os
from pathlib import Path

# Adicionar paths necessários
sys.path.append(str(Path(__file__).parent / 'core'))
sys.path.append(str(Path(__file__).parent / 'integrations'))

from core.icp_qualification_engine import ICPQualificationEngine, main as engine_main

# Import BigQuery com fallback
try:
    from integrations.bigquery_integration import ArcoBigQueryIntegration
    BIGQUERY_AVAILABLE = True
except ImportError:
    print("⚠️ BigQuery integration não disponível")
    BIGQUERY_AVAILABLE = False

def print_header():
    """Print cabeçalho do pipeline"""
    print("🚀 ARCO PIPELINE - ISOLATED EXECUTION")
    print("=" * 60)
    print("🎯 Target: 5 leads qualificados dentro do ICP")
    print("📍 Pipeline otimizado e isolado")
    print("⚡ Powered by SearchAPI + PageSpeed APIs")
    print("=" * 60)

def print_system_check():
    """Verificar sistema antes da execução"""
    print("\n🔍 SYSTEM CHECK:")
    
    # Verificar dependências
    try:
        import aiohttp
        print("✅ aiohttp: OK")
    except ImportError:
        print("❌ aiohttp: MISSING - Install with: pip install aiohttp")
        return False
    
    try:
        import requests
        print("✅ requests: OK")
    except ImportError:
        print("❌ requests: MISSING - Install with: pip install requests")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv: OK")
    except ImportError:
        print("❌ python-dotenv: MISSING - Install with: pip install python-dotenv")
        return False
    
    # Verificar configuração
    try:
        from config.api_keys import validate_api_keys
        validation = validate_api_keys()
        
        if validation['searchapi']:
            print("✅ SearchAPI: Configured")
        else:
            print("❌ SearchAPI: Missing key")
            return False
            
        if validation['pagespeed']:
            print("✅ PageSpeed API: Configured")
        else:
            print("❌ PageSpeed API: Missing key")
            return False
            
    except Exception as e:
        print(f"❌ Configuration Error: {e}")
        return False
    
    return True

def install_dependencies():
    """Instalar dependências se necessário"""
    print("\n🔧 Installing missing dependencies...")
    
    import subprocess
    
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', 
            'aiohttp', 'requests', 'python-dotenv'
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

async def execute_pipeline():
    """Executar pipeline principal com integração BigQuery"""
    print("\n🎯 EXECUTING ARCO PIPELINE...")
    print("-" * 40)
    
    # Inicializar BigQuery se disponível
    bigquery_integration = None
    execution_id = None
    start_time = None
    
    if BIGQUERY_AVAILABLE:
        try:
            # Tentar conectar BigQuery
            print("📊 Conectando BigQuery...")
            bigquery_integration = ArcoBigQueryIntegration()
            execution_id = bigquery_integration.log_execution_start()
            print(f"✅ BigQuery conectado - Execution ID: {execution_id}")
            
        except Exception as e:
            print(f"⚠️ BigQuery não disponível: {e}")
            print("🔄 Continuando execução sem BigQuery...")
    else:
        print("⚠️ BigQuery integration não disponível")
        print("🔄 Continuando execução sem BigQuery...")
    
    try:
        import time
        start_time = time.time()
        
        # Executar engine principal
        leads_data = await engine_main()
        
        execution_time = time.time() - start_time
        
        # Salvar no BigQuery se disponível
        if bigquery_integration and execution_id and leads_data:
            print("\n📊 Salvando resultados no BigQuery...")
            try:
                bigquery_integration.save_qualified_leads(leads_data, execution_id)
                bigquery_integration.log_execution_complete(
                    execution_id, execution_time, leads_data, success=True
                )
                print("✅ Dados salvos no BigQuery com sucesso!")
                
                # Mostrar estatísticas
                stats = bigquery_integration.get_execution_stats(days=7)
                if stats:
                    print(f"\n📈 ESTATÍSTICAS (últimos 7 dias):")
                    print(f"   - Total execuções: {stats.get('total_executions', 0)}")
                    print(f"   - Total leads qualificados: {stats.get('total_leads_qualified', 0)}")
                    print(f"   - Waste total detectado: ${stats.get('total_waste_detected', 0):,.2f}")
                    print(f"   - Taxa de sucesso: {stats.get('success_rate', 0):.1f}%")
                
            except Exception as e:
                print(f"⚠️ Erro ao salvar no BigQuery: {e}")
                if bigquery_integration and execution_id:
                    bigquery_integration.log_execution_complete(
                        execution_id, execution_time, leads_data, 
                        success=False, error_message=str(e)
                    )
        
        return True
        
    except Exception as e:
        if bigquery_integration and execution_id:
            execution_time = time.time() - start_time if start_time else 0
            bigquery_integration.log_execution_complete(
                execution_id, execution_time, [], 
                success=False, error_message=str(e)
            )
        
        print(f"❌ Pipeline execution failed: {e}")
        return False

def main():
    """Função principal"""
    print_header()
    
    # System check
    if not print_system_check():
        print("\n🔧 Attempting to fix dependencies...")
        if not install_dependencies():
            print("\n❌ System check failed. Please install dependencies manually:")
            print("   pip install -r requirements.txt")
            sys.exit(1)
        
        # Re-check após instalação
        print("\n🔍 Re-checking system...")
        if not print_system_check():
            print("❌ System still not ready. Please check configuration.")
            sys.exit(1)
    
    print("\n🚀 System ready! Starting pipeline execution...")
    
    # Executar pipeline
    try:
        success = asyncio.run(execute_pipeline())
        
        if success:
            print("\n🎉 PIPELINE EXECUTION COMPLETED!")
            print("📁 Check exports/ folder for results")
            print("🎯 5 leads qualificados exportados com sucesso")
        else:
            print("\n❌ Pipeline execution failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
