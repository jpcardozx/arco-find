#!/usr/bin/env python3
"""
ARCO FIND - VALIDAÇÃO COMPLETA DO SISTEMA
Testa todos os componentes disponíveis
"""

import subprocess
import sys
from pathlib import Path

def run_test(name, command):
    """Executa um teste e retorna o resultado"""
    print(f"\n{'='*60}")
    print(f"🧪 TESTANDO: {name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=300  # 5 minutos timeout
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        success = result.returncode == 0
        print(f"\n{'✅ PASSOU' if success else '❌ FALHOU'}: {name}")
        return success
        
    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT: {name}")
        return False
    except Exception as e:
        print(f"❌ ERRO: {name} - {e}")
        return False

def main():
    """Executa validação completa"""
    print("🚀 ARCO FIND - VALIDAÇÃO COMPLETA DO SISTEMA")
    print("=" * 60)
    
    # Lista de testes a executar
    tests = [
        ("Sistema Limpo - Teste de Estrutura", "python test_clean_simple.py"),
        ("Sistema Limpo - Demo", "python demo_clean.py"),
        ("Sistema S-Tier - Configuração", "python test_stier.py"),
    ]
    
    results = {}
    
    for test_name, command in tests:
        results[test_name] = run_test(test_name, command)
    
    # Resumo final
    print("\n" + "="*60)
    print("📊 RESUMO FINAL DA VALIDAÇÃO")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nRESULTADO: {passed}/{total} testes passaram")
    
    # Análise de sistemas disponíveis
    print("\n" + "="*60)
    print("🔧 SISTEMAS DISPONÍVEIS")
    print("="*60)
    
    files_status = {
        "arco_find_clean.py": "Sistema de Produção Limpo",
        "engines/bigquery_stier_pipeline.py": "Sistema S-Tier BigQuery",
        "requirements_clean.txt": "Dependências Mínimas",
        "requirements_stier.txt": "Dependências S-Tier",
        ".env.example": "Exemplo de Configuração"
    }
    
    for file, description in files_status.items():
        exists = Path(file).exists()
        status = "✅" if exists else "❌"
        print(f"{status} {description}: {file}")
    
    # Recomendações
    print("\n" + "="*60)
    print("💡 RECOMENDAÇÕES")
    print("="*60)
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema completamente funcional")
        print("✅ Pronto para uso em produção")
        
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Configure variáveis de ambiente (.env)")
        print("2. Escolha o sistema a usar:")
        print("   - Limpo: python arco_find_clean.py")
        print("   - S-Tier: python run_stier_pipeline.py")
    else:
        print(f"⚠️ {total - passed} teste(s) falharam")
        print("📋 Verifique os logs acima para detalhes")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Validação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro na validação: {e}")
        sys.exit(1)
