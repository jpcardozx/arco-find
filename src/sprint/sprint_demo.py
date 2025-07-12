#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARCO Sprint Demo - Demonstra o sistema completo funcionando
"""

import json
import os
from datetime import datetime

def show_system_demo():
    """Mostra demo completa do sistema Sprint"""
    
    print("🎯 ARCO SPRINT USD 997 - SISTEMA EXECUTADO COM SUCESSO!")
    print("═" * 70)
    print()
    
    # Verifica arquivos gerados
    results_dir = "results"
    today = datetime.now().strftime("%Y%m%d")
    
    # Encontra arquivos mais recentes
    opp_files = [f for f in os.listdir(results_dir) if f.startswith("sprint_opportunities_")]
    script_files = [f for f in os.listdir(results_dir) if f.startswith("sprint_outreach_scripts_")]
    
    if opp_files and script_files:
        latest_opp = max(opp_files, key=lambda x: x.split("_")[-1].split(".")[0])
        latest_scripts = max(script_files, key=lambda x: x.split("_")[-1].split(".")[0])
        
        print("📊 RESULTADOS GERADOS:")
        print(f"✅ Oportunidades: {latest_opp}")
        print(f"✅ Scripts: {latest_scripts}")
        print()
        
        # Mostra conteudo dos scripts
        with open(f"{results_dir}/{latest_scripts}", 'r', encoding='utf-8') as f:
            scripts = json.load(f)
        
        print("🎬 SCRIPTS PERSONALIZADOS PRONTOS:")
        print("━" * 50)
        
        for i, script in enumerate(scripts[:3], 1):  # Mostra os primeiros 3
            print(f"\n{i}. PROSPECT: {script['company']} ({script['priority']} priority)")
            print(f"   Sinais: {script['signals']}/3")
            print(f"   Valor estimado: ${script['estimated_value']}")
            print(f"   Urgency: {script['urgency_trigger']}")
            print()
            
            print("📱 LINKEDIN SCRIPT:")
            print("─" * 30)
            print(script['linkedin_script'])
            print()
            
            print("📧 EMAIL FOLLOW-UP:")
            print("─" * 30)
            print(script['email_script'][:300] + "..." if len(script['email_script']) > 300 else script['email_script'])
            print("\n" + "━" * 50)
    
    print("\n🚀 PROXIMOS PASSOS PARA EXECUCAO:")
    print("1. 🎬 Gravar Looms com scripts LinkedIn")
    print("2. 📱 Enviar DMs LinkedIn personalizados") 
    print("3. 👀 Monitorar replies e opens")
    print("4. 📧 Follow-up com emails estruturados")
    print("5. 📞 Agendar e executar calls")
    print("6. 📄 Fechar com contratos DocuSign")
    
    print("\n📈 METRICAS DE SUCESSO:")
    print("• Target: 5 calls / 2 deals em 14 dias")
    print("• Revenue alvo: $1,994")
    print("• ROI cliente: 7.5× average")
    print("• Close rate esperado: 40%+")
    
    print("\n💡 DIFERENCIAIS COMPETITIVOS:")
    print("✓ Dados específicos vs generic pitches")
    print("✓ Urgency real vs manufactured scarcity")  
    print("✓ Risk reversal elimina objeções")
    print("✓ ROI imediato vs promises futuras")
    print("✓ Low ticket reduz friction")
    
    print("\n" + "═" * 70)
    print("🎯 SISTEMA PRONTO PARA VALIDAR MODELO EM 14 DIAS")
    print("═" * 70)

if __name__ == "__main__":
    show_system_demo()
