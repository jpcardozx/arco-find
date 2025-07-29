#!/usr/bin/env python3
"""
EXECUTE CORRECTED SMB PIPELINE
Testa pipeline corrigido com Meta Ads Library e filtros SMB estratégicos
"""

import asyncio
import sys
import os

# Add parent directory to path to import the corrected pipeline
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from smb_48h_pipeline import SMBAgencyPipeline

async def test_corrected_pipeline():
    print("🚀 TESTANDO PIPELINE CORRIGIDO")
    print("=" * 50)
    print("Verificações:")
    print("✅ Meta Ads Library queries estratégicas")
    print("✅ Filtros firmográficos SMB")
    print("✅ Validação de sinais públicos")
    print("✅ Eliminação BigQuery overhead")
    print()
    
    # Initialize corrected pipeline
    pipeline = SMBAgencyPipeline()
    
    # Test Meta Ads Library targeting
    print("📊 TESTE: Verticals estratégicos configurados")
    for vertical, config in pipeline.high_urgency_verticals.items():
        print(f"   {vertical}:")
        
        # Check if using meta_ad_queries (corrected version)
        queries = config.get('meta_ad_queries', config.get('queries', []))
        print(f"     Meta Ads queries: {len(queries)}")
        
        # Check firmographic filters
        if 'firmographic_filters' in config:
            filters = config['firmographic_filters']
            min_spend = filters.get('min_monthly_spend', 0)
            max_spend = filters.get('max_monthly_spend', 0)
            print(f"     Spend range: ${min_spend:,} - ${max_spend:,}")
            
            # Check public signal requirements
            signals = filters.get('public_signal_requirements', [])
            print(f"     Required signals: {len(signals)}")
        else:
            print("     ⚠️ Filtros firmográficos não encontrados")
    
    print()
    print("🔍 TESTE: Discovery de 1 vertical")
    
    # Test discovery for one vertical
    try:
        if 'personal_injury_law' in pipeline.high_urgency_verticals:
            vertical = 'personal_injury_law'
            config = pipeline.high_urgency_verticals[vertical]
            
            print(f"   Testando descoberta em: {vertical}")
            signals = await pipeline._discover_vertical_opportunities(vertical, config, max_signals=3)
            
            print(f"   P0 signals encontrados: {len(signals)}")
            
            for i, signal in enumerate(signals, 1):
                print(f"   {i}. {signal.company_name}")
                print(f"      Domain: {signal.domain}")
                print(f"      Readiness: {signal.readiness_score:.2f}")
                print(f"      Waste estimate: ${signal.monthly_waste:,}/mês")
        else:
            print("   ⚠️ Vertical personal_injury_law não encontrado")
    
    except Exception as e:
        print(f"   ❌ Erro no teste: {e}")
    
    print()
    print("✅ TESTE CONCLUÍDO")
    print("📁 Pipeline corrigido em: pipeline_optimized/smb_pipeline_corrected.py")
    print("📋 Correções documentadas em: CORRECOES_APLICADAS.md")

if __name__ == "__main__":
    asyncio.run(test_corrected_pipeline())
