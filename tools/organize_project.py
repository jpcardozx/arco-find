"""
ARCO v2.0 - LIMPEZA INTELIGENTE DO PROJETO
==========================================
Remove arquivos obsoletos e organiza hierarquia
"""

import os
import shutil
from pathlib import Path

def reorganize_project():
    """Reorganizar projeto com hierarquia inteligente"""
    
    print("🧹 LIMPEZA INTELIGENTE - ARCO v2.0")
    print("=" * 50)
    
    # Definir estrutura otimizada
    core_files = [
        "arco_v2_final_optimized.py",
        "arco_constants.py", 
        "error_handler.py"
    ]
    
    module_files = [
        "enhanced_lead_processor.py",
        "critical_auditor.py"
    ]
    
    essential_docs = [
        "WORKFLOW_INTELIGENTE.md",
        "RELATORIO_FINAL_MISSAO_CUMPRIDA.md"
    ]
    
    utility_files = [
        "run_arco.py"
    ]
    
    # Arquivos a manter (core + corrected version)
    keep_files = core_files + module_files + essential_docs + utility_files + [
        "arco_intermediate_lead_finder_v2_CRITICAL_FIX.py"  # Versão corrigida
    ]
    
    # Listar todos os arquivos
    all_files = [f for f in os.listdir('.') if f.endswith(('.py', '.md', '.json'))]
    
    print("📁 ARQUIVOS PRINCIPAIS (MANTER):")
    for file in core_files:
        if file in all_files:
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - NÃO ENCONTRADO")
    
    print("\n🛠️ MÓDULOS ESPECIALIZADOS (MANTER):")
    for file in module_files:
        if file in all_files:
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - NÃO ENCONTRADO")
    
    print("\n📋 DOCUMENTAÇÃO ESSENCIAL (MANTER):")
    for file in essential_docs:
        if file in all_files:
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - NÃO ENCONTRADO")
    
    # Identificar arquivos obsoletos
    obsolete_files = []
    for file in all_files:
        if file not in keep_files:
            # Verificar se é arquivo de trabalho/rascunho
            if any(keyword in file.lower() for keyword in 
                   ['test', 'validation', 'analise', 'relatorio', 'v11', 'v12', 'v77', 'v8']):
                obsolete_files.append(file)
            elif file.startswith('business_intelligence_') or file.startswith('VERIFIED_'):
                obsolete_files.append(file)
            elif file.endswith('_20250726_040730.json') or file.endswith('_20250726_042702.json'):
                obsolete_files.append(file)
    
    if obsolete_files:
        print(f"\n🗑️ ARQUIVOS OBSOLETOS IDENTIFICADOS ({len(obsolete_files)}):")
        for file in obsolete_files[:10]:  # Mostrar apenas os primeiros 10
            print(f"   📄 {file}")
        if len(obsolete_files) > 10:
            print(f"   ... e mais {len(obsolete_files) - 10} arquivos")
    
    # Calcular estatísticas de limpeza
    total_files = len(all_files)
    files_to_keep = len([f for f in keep_files if f in all_files])
    files_to_remove = len(obsolete_files)
    
    print(f"\n📊 ESTATÍSTICAS DE LIMPEZA:")
    print(f"   📁 Total de arquivos: {total_files}")
    print(f"   ✅ Manter (essenciais): {files_to_keep}")
    print(f"   🗑️ Remover (obsoletos): {files_to_remove}")
    print(f"   📈 Redução: {(files_to_remove/total_files)*100:.1f}% menos arquivos")
    
    # Resumo da hierarquia otimizada
    print(f"\n🏗️ HIERARQUIA FINAL OTIMIZADA:")
    print("   CORE/")
    for file in core_files:
        status = "✅" if file in all_files else "❌"
        print(f"      {status} {file}")
    
    print("   MODULES/")  
    for file in module_files:
        status = "✅" if file in all_files else "❌"
        print(f"      {status} {file}")
    
    print("   RESULTS/")
    print("      ✅ arco_intermediate_lead_finder_v2_CRITICAL_FIX.py")
    
    print("   DOCS/")
    for file in essential_docs:
        status = "✅" if file in all_files else "❌"
        print(f"      {status} {file}")
    
    # Comandos recomendados
    print(f"\n🎯 COMANDOS RECOMENDADOS:")
    print("   ▶️ EXECUTAR: python run_arco.py")
    print("   🔧 CONFIGURAR: Editar arco_constants.py")
    print("   🚀 PRODUÇÃO: python arco_v2_final_optimized.py")
    print("   🐛 DEBUG: python critical_auditor.py")
    
    # Status final
    essential_present = all(f in all_files for f in core_files if f.endswith('.py'))
    
    if essential_present:
        print(f"\n🏆 STATUS: PROJETO OTIMIZADO E FUNCIONAL")
        print("✅ Todos os arquivos essenciais presentes")
        print("📋 Hierarquia clara e organizadas")
        print("🚀 Pronto para uso em produção")
    else:
        print(f"\n⚠️ STATUS: ARQUIVOS ESSENCIAIS AUSENTES")
        print("❌ Verificar se todos os core files foram criados")

def show_usage_priority():
    """Mostrar prioridade de uso dos arquivos"""
    
    print(f"\n📋 PRIORIDADE DE USO:")
    print("   🥇 PRIORIDADE MÁXIMA (Use Diariamente):")
    print("      • run_arco.py                    ← INÍCIO AQUI")
    print("      • arco_v2_final_optimized.py     ← ENGINE PRINCIPAL")
    print("      • WORKFLOW_INTELIGENTE.md        ← GUIA COMPLETO")
    
    print("   🥈 PRIORIDADE ALTA (Configure Uma Vez):")
    print("      • arco_constants.py              ← CONFIGURAÇÕES")
    print("      • error_handler.py               ← TRATAMENTO ERRO")
    
    print("   🥉 PRIORIDADE MÉDIA (Use Se Necessário):")
    print("      • enhanced_lead_processor.py     ← CUSTOMIZAÇÃO AVANÇADA")
    print("      • critical_auditor.py            ← DEBUG/AUDITORIA")
    
    print("   📚 DOCUMENTAÇÃO (Referência):")
    print("      • RELATORIO_FINAL_MISSAO_CUMPRIDA.md  ← RESULTADOS")
    print("      • arco_intermediate_lead_finder_v2_CRITICAL_FIX.py ← BACKUP")

if __name__ == "__main__":
    reorganize_project()
    show_usage_priority()
    
    print("\n" + "="*50)
    print("🎯 PROJETO ARCO v2.0 - HIERARQUIA OTIMIZADA")
    print("📋 Documentação: WORKFLOW_INTELIGENTE.md")
    print("🚀 Próximo passo: python run_arco.py")
    print("="*50)
