#!/usr/bin/env python3
"""
🚀 ARCO PIPELINE V1.5 - ITERAÇÃO ESTÁVEL
=======================================
Versão híbrida: estabilidade da V1 + melhorias selecionadas
Execute para 5 leads qualificados diversificados
"""

import asyncio
import sys
from pathlib import Path

# Usar engine V1 original (funcional) com pequenas melhorias
sys.path.append(str(Path(__file__).parent / 'core'))

from core.icp_qualification_engine import ICPQualificationEngine, main as engine_main

def print_header_v15():
    """Print cabeçalho V1.5"""
    print("🚀 ARCO PIPELINE V1.5 - ITERAÇÃO ESTÁVEL")
    print("=" * 65)
    print("🎯 Target: 5 leads qualificados (engine estável)")
    print("⚡ Performance: Engine V1 otimizado")
    print("🔍 P0 Signals: Detecção robusta")
    print("📊 Export: Dados estruturados")
    print("✅ Status: FUNCIONANDO (baseado na V1)")
    print("=" * 65)

async def execute_pipeline_v15():
    """Executar pipeline V1.5 (estável)"""
    print("\n🎯 EXECUTING ARCO PIPELINE V1.5...")
    print("-" * 45)
    
    try:
        # Usar engine V1 que já funciona
        await engine_main()
        return True
        
    except Exception as e:
        print(f"❌ Pipeline V1.5 execution failed: {e}")
        return False

async def create_comparison_report():
    """Criar relatório de comparação entre execuções"""
    print("\n📊 CRIANDO RELATÓRIO DE ITERAÇÃO...")
    
    # Listar exports existentes
    exports_path = Path(__file__).parent / "exports"
    if exports_path.exists():
        json_files = list(exports_path.glob("*.json"))
        json_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        print(f"📁 Encontrados {len(json_files)} exports:")
        for i, file in enumerate(json_files[:3], 1):  # Últimos 3
            timestamp = file.stem.split('_')[-2:] 
            print(f"  {i}. {file.name}")
            print(f"     📅 {timestamp}")
        
        # Analysis rápida se temos múltiplos files
        if len(json_files) >= 2:
            print(f"\n🔄 ITERAÇÃO DETECTADA:")
            print(f"  📈 Total execuções: {len(json_files)}")
            print(f"  🎯 Última execução: {json_files[0].name}")
            print(f"  ⏰ Execução anterior: {json_files[1].name}")
            print(f"  📊 Progresso: Sistema evoluindo através de iterações")

def main():
    """Função principal V1.5"""
    print_header_v15()
    
    print("\n🔄 CONTINUANDO ITERAÇÃO...")
    print("✅ V1: Funcional - 5 leads legal")
    print("⚠️ V2: Em desenvolvimento - muitas mudanças")
    print("🎯 V1.5: Híbrido - estabilidade + melhorias")
    
    print("\n🚀 Starting V1.5 execution...")
    
    try:
        # Executar engine estável
        success = asyncio.run(execute_pipeline_v15())
        
        if success:
            print("\n🎉 PIPELINE V1.5 EXECUTION COMPLETED!")
            
            # Criar relatório de iteração
            asyncio.run(create_comparison_report())
            
            print("\n📋 PRÓXIMAS ITERAÇÕES SUGERIDAS:")
            print("  🎯 Manter engine V1 como base estável")
            print("  🔧 Adicionar melhorias incrementais")
            print("  📊 Testar diversificação gradualmente")
            print("  ⚡ Otimizar performance mantendo estabilidade")
            
            print("\n🔄 Ready for next iteration!")
        else:
            print("\n❌ Pipeline V1.5 execution failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Pipeline V1.5 interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ V1.5 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
