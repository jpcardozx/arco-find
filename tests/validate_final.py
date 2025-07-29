#!/usr/bin/env python3
"""
ARCO FIND - VALIDAÇÃO FINAL COMPLETA
Testa todos os sistemas disponíveis
"""

import os
import sys
from pathlib import Path

def test_clean_system():
    """Testa o sistema limpo"""
    print("=" * 60)
    print("TESTANDO: SISTEMA LIMPO")
    print("=" * 60)
    
    try:
        # Testa imports
        from arco_find_clean import SecureConfig, RealPageSpeedClient, CleanLeadEngine
        print("[PASS] Imports do sistema limpo")
        
        # Testa instanciação
        config = SecureConfig()
        client = RealPageSpeedClient()
        engine = CleanLeadEngine()
        print("[PASS] Instanciação dos componentes")
        
        # Verifica métodos
        if hasattr(client, 'analyze_performance'):
            print("[PASS] Método analyze_performance existe")
        else:
            print("[FAIL] Método analyze_performance não encontrado")
            return False
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Erro no sistema limpo: {e}")
        return False

def test_stier_system():
    """Testa o sistema S-Tier"""
    print("\n" + "=" * 60)
    print("TESTANDO: SISTEMA S-TIER")
    print("=" * 60)
    
    try:
        # Testa configuração
        from config.stier_config import STierConfig
        print("[PASS] Import da configuração S-Tier")
        
        config = STierConfig()
        print("[PASS] Instanciação da configuração")
        
        # Testa pipeline
        from engines.bigquery_stier_pipeline import BigQuerySTierPipeline
        print("[PASS] Import do pipeline S-Tier")
        
        pipeline = BigQuerySTierPipeline()
        print("[PASS] Instanciação do pipeline")
        
        # Verifica se tem GCP_PROJECT_ID
        if not os.getenv('GCP_PROJECT_ID'):
            print("[WARN] GCP_PROJECT_ID não configurado (normal para teste)")
        else:
            print("[PASS] GCP_PROJECT_ID configurado")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Erro no sistema S-Tier: {e}")
        return False

def test_dependencies():
    """Testa dependências"""
    print("\n" + "=" * 60)
    print("TESTANDO: DEPENDÊNCIAS")
    print("=" * 60)
    
    # Dependências do sistema limpo
    clean_deps = ['aiohttp', 'pandas', 'openpyxl']
    stier_deps = ['structlog']
    
    results = {}
    
    for dep in clean_deps:
        try:
            __import__(dep)
            print(f"[PASS] {dep} (sistema limpo)")
            results[dep] = True
        except ImportError:
            print(f"[FAIL] {dep} (sistema limpo)")
            results[dep] = False
    
    for dep in stier_deps:
        try:
            __import__(dep)
            print(f"[PASS] {dep} (sistema S-Tier)")
            results[dep] = True
        except ImportError:
            print(f"[FAIL] {dep} (sistema S-Tier)")
            results[dep] = False
    
    # Testa dotenv separadamente
    try:
        from dotenv import load_dotenv
        print(f"[PASS] python-dotenv")
        results['dotenv'] = True
    except ImportError:
        print(f"[FAIL] python-dotenv")
        results['dotenv'] = False
    
    return all(results.values())

def test_files():
    """Testa arquivos necessários"""
    print("\n" + "=" * 60)
    print("TESTANDO: ARQUIVOS")
    print("=" * 60)
    
    required_files = {
        'arco_find_clean.py': 'Sistema principal limpo',
        'requirements_clean.txt': 'Dependências mínimas',
        'config/stier_config.py': 'Configuração S-Tier',
        'engines/bigquery_stier_pipeline.py': 'Pipeline S-Tier',
        '.env.example': 'Exemplo de configuração'
    }
    
    all_exist = True
    
    for file, description in required_files.items():
        if Path(file).exists():
            print(f"[PASS] {description}: {file}")
        else:
            print(f"[FAIL] {description}: {file}")
            all_exist = False
    
    return all_exist

def test_environment():
    """Testa configuração do ambiente"""
    print("\n" + "=" * 60)
    print("TESTANDO: AMBIENTE")
    print("=" * 60)
    
    # Variáveis opcionais
    optional_vars = {
        'GOOGLE_PAGESPEED_API_KEY': 'Sistema limpo funcional',
        'GCP_PROJECT_ID': 'Sistema S-Tier funcional'
    }
    
    configured_count = 0
    
    for var, description in optional_vars.items():
        if os.getenv(var):
            print(f"[PASS] {var} configurado - {description}")
            configured_count += 1
        else:
            print(f"[WARN] {var} não configurado - {description} em modo demo")
    
    print(f"\n[INFO] {configured_count}/{len(optional_vars)} variáveis configuradas")
    print("[INFO] Sistemas funcionam em modo demo sem configuração")
    
    return True  # Sempre retorna True pois modo demo é válido

def show_usage_instructions():
    """Mostra instruções de uso"""
    print("\n" + "=" * 60)
    print("INSTRUÇÕES DE USO")
    print("=" * 60)
    
    print("\n[SISTEMA LIMPO]")
    print("- Teste: python test_clean_simple.py")
    print("- Demo: python demo_clean_windows.py")
    print("- Produção: python arco_find_clean.py")
    print("- Requer: GOOGLE_PAGESPEED_API_KEY para funcionalidade completa")
    
    print("\n[SISTEMA S-TIER]")
    print("- Teste: python test_stier_windows.py")
    print("- Produção: python run_stier_pipeline.py")
    print("- Requer: GCP_PROJECT_ID e credenciais BigQuery")
    
    print("\n[CONFIGURAÇÃO]")
    print("1. Copie .env.example para .env")
    print("2. Configure as chaves de API necessárias")
    print("3. Execute o sistema desejado")

def main():
    """Função principal de validação"""
    print("ARCO FIND - VALIDAÇÃO FINAL COMPLETA")
    print("Testing all available systems and components")
    print("=" * 60)
    
    # Lista de testes
    tests = [
        ("Arquivos", test_files),
        ("Dependências", test_dependencies),
        ("Sistema Limpo", test_clean_system),
        ("Sistema S-Tier", test_stier_system),
        ("Ambiente", test_environment)
    ]
    
    results = {}
    
    # Executa testes
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO FINAL")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results.items():
        status = "[PASS]" if success else "[FAIL]"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nRESULTADO: {passed}/{total} testes passaram")
    
    # Status geral
    if passed >= 4:  # Pelo menos 4 de 5 testes devem passar
        print("\n[SUCCESS] SISTEMA APROVADO!")
        print("[INFO] Sistemas prontos para uso")
        show_usage_instructions()
        return True
    else:
        print(f"\n[FAIL] SISTEMA COM PROBLEMAS")
        print("[ERROR] Corrija os problemas listados acima")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[WARN] Validação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Erro na validação: {e}")
        sys.exit(1)
