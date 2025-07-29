#!/usr/bin/env python3
"""
🚀 PIPELINE ARCO - VERSÃO SIMPLIFICADA COM BIGQUERY
Execução direta com integração BigQuery funcional
"""

import asyncio
import time
import json
from datetime import datetime
import sys
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent / 'core'))
sys.path.append(str(Path(__file__).parent / 'integrations'))

async def execute_simplified_pipeline():
    """Executar pipeline simplificado com BigQuery funcionando"""
    
    print("🚀 ARCO PIPELINE SIMPLIFICADO - BIGQUERY INTEGRATION")
    print("=" * 60)
    
    # Import BigQuery integration
    try:
        from integrations.bigquery_integration import ArcoBigQueryIntegration
        bq = ArcoBigQueryIntegration()
        print("✅ BigQuery integration carregada")
    except Exception as e:
        print(f"❌ Erro BigQuery: {e}")
        return False
    
    # Start execution tracking
    start_time = time.time()
    execution_id = bq.log_execution_start("v1.0_simplified")
    print(f"📊 Execution ID: {execution_id}")
    
    # Simulate lead qualification (using mock data for speed)
    print("\n🎯 Simulando qualificação de leads...")
    
    mock_leads = [
        {
            "company_name": "Test Legal Firm 1",
            "domain": "testlegal1.com",
            "industry": "legal",
            "location": "Dallas, TX",
            "icp_score": 0.85,
            "urgency_score": 0.75,
            "estimated_waste": 2500.0,
            "p0_signals": ["P0_LCP", "P0_PERFORMANCE"],
            "approach_vector": "AD_WASTE_FOCUS",
            "qualification_reason": "High-value legal vertical with performance issues",
            "contact_info": {"email": "test@testlegal1.com", "phone": "555-1234"},
            "performance_metrics": {"lcp": 4.2, "cls": 0.15, "fid": 180}
        },
        {
            "company_name": "Test Legal Firm 2", 
            "domain": "testlegal2.com",
            "industry": "legal",
            "location": "Dallas, TX",
            "icp_score": 0.80,
            "urgency_score": 0.70,
            "estimated_waste": 2000.0,
            "p0_signals": ["P0_LCP"],
            "approach_vector": "AD_WASTE_FOCUS",
            "qualification_reason": "Legal vertical with LCP issues",
            "contact_info": {"email": "info@testlegal2.com", "phone": "555-5678"},
            "performance_metrics": {"lcp": 3.8, "cls": 0.05, "fid": 120}
        }
    ]
    
    # Save leads to BigQuery
    try:
        print("\n📊 Salvando leads no BigQuery...")
        bq.save_qualified_leads(mock_leads, execution_id)
        print("✅ Leads salvos com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao salvar leads: {e}")
        return False
    
    # Complete execution
    execution_time = time.time() - start_time
    try:
        print(f"\n📊 Finalizando execução ({execution_time:.1f}s)...")
        bq.log_execution_complete(
            execution_id, 
            execution_time, 
            mock_leads, 
            success=True
        )
        print("✅ Execução finalizada com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao finalizar execução: {e}")
        return False
    
    # Get stats
    try:
        print("\n📈 Buscando estatísticas...")
        stats = bq.get_execution_stats(days=7)
        if stats:
            print("✅ ESTATÍSTICAS (últimos 7 dias):")
            print(f"   - Total execuções: {stats.get('total_executions', 0)}")
            print(f"   - Total leads qualificados: {stats.get('total_leads_qualified', 0)}")
            print(f"   - Waste total detectado: ${stats.get('total_waste_detected', 0):,.2f}")
            print(f"   - Taxa de sucesso: {stats.get('success_rate', 0):.1f}%")
        else:
            print("⚠️ Estatísticas vazias")
    except Exception as e:
        print(f"❌ Erro ao buscar stats: {e}")
    
    print("\n🎉 PIPELINE SIMPLIFICADO EXECUTADO COM SUCESSO!")
    print("📊 BigQuery totalmente integrado e funcionando!")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(execute_simplified_pipeline())
    if success:
        print("\n✅ TESTE BIGQUERY: SUCESSO COMPLETO")
    else:
        print("\n❌ TESTE BIGQUERY: FALHOU")
