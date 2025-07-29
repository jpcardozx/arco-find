#!/usr/bin/env python3
"""
🚀 ARCO PIPELINE V2 - ITERAÇÃO OTIMIZADA
======================================
Execute para 5 leads qualificados com:
- Diversificação de indústrias
- Performance otimizada (<3min)
- P0 signals detalhados
- Análises competitivas
"""

import asyncio
import sys
from pathlib import Path

# Adicionar path do core
sys.path.append(str(Path(__file__).parent / 'core'))

from core.icp_qualification_engine_v2 import ICPQualificationEngineV2, main_v2

def print_header_v2():
    """Print cabeçalho V2"""
    print("🚀 ARCO PIPELINE V2 - ITERAÇÃO OTIMIZADA")
    print("=" * 70)
    print("🎯 Target: 5 leads diversificados por indústria")
    print("⚡ Performance: <3 minutos de execução")
    print("🔍 P0 Signals: Detecção crítica aprimorada")
    print("📊 Analytics: Análise competitiva incluída")
    print("🏢 Diversidade: Legal, Healthcare, Real Estate, Home Services")
    print("=" * 70)

def print_improvements():
    """Listar melhorias da V2"""
    print("\n🔧 MELHORIAS IMPLEMENTADAS V2:")
    print("  ✅ Diversificação automática por indústria")
    print("  ✅ Cache de performance para otimização")
    print("  ✅ Processamento paralelo de prospects")
    print("  ✅ P0 signals críticos vs normais")
    print("  ✅ Threshold ICP aumentado (0.75)")
    print("  ✅ Análise competitiva por indústria")
    print("  ✅ Scoring refinado com opportunity score")
    print("  ✅ Export com analytics avançadas")

async def execute_pipeline_v2():
    """Executar pipeline V2 otimizado"""
    print("\n🎯 EXECUTING ARCO PIPELINE V2...")
    print("-" * 50)
    
    try:
        # Executar engine V2
        await main_v2()
        return True
        
    except Exception as e:
        print(f"❌ Pipeline V2 execution failed: {e}")
        return False

def main():
    """Função principal V2"""
    print_header_v2()
    print_improvements()
    
    print("\n🚀 Starting V2 execution...")
    
    # Executar pipeline V2
    try:
        success = asyncio.run(execute_pipeline_v2())
        
        if success:
            print("\n🎉 PIPELINE V2 EXECUTION COMPLETED!")
            print("📁 Check exports/ folder for V2 results")
            print("🎯 Diversified leads with enhanced analytics")
            print("\n🔄 Ready for next iteration!")
        else:
            print("\n❌ Pipeline V2 execution failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Pipeline V2 interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ V2 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
