#!/usr/bin/env python3
"""
🎯 TESTE: DESCOBERTA DE LEADS VIA BIGQUERY
Testing lead discovery using BigQuery as the data source
"""

import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pipelines.bigquery.setup_final import BigQueryLeadDiscovery

def test_bigquery_lead_discovery():
    """Test lead discovery from BigQuery"""
    
    print("🎯 TESTE: DESCOBERTA DE LEADS VIA BIGQUERY")
    print("=" * 60)
    
    # Initialize BigQuery lead discovery
    discovery = BigQueryLeadDiscovery()
    
    try:
        # Setup BigQuery connection
        print("🔧 Configurando conexão BigQuery...")
        setup_success = discovery.setup_complete()
        
        if not setup_success:
            print("❌ Falha na configuração BigQuery")
            return False
        
        print("\n🔍 TESTANDO DESCOBERTA DE LEADS...")
        print("-" * 40)
        
        # Test 1: High-value fintech leads
        print("📊 Teste 1: Leads Fintech de alto valor")
        fintech_leads = discovery.discover_qualified_leads(
            industry='fintech',
            min_score=80
        )
        print(f"   Resultado: {len(fintech_leads)} leads encontrados")
        
        # Test 2: Geographic targeting - Canada
        print("\n🌍 Teste 2: Leads no Canadá")
        canada_leads = discovery.discover_qualified_leads(
            location='Canada',
            min_score=70
        )
        print(f"   Resultado: {len(canada_leads)} leads encontrados")
        
        # Test 3: SaaS companies
        print("\n💼 Teste 3: Empresas SaaS")
        saas_leads = discovery.discover_qualified_leads(
            industry='saas',
            min_score=75
        )
        print(f"   Resultado: {len(saas_leads)} leads encontrados")
        
        # Test 4: All qualified leads (general)
        print("\n🎯 Teste 4: Todos os leads qualificados")
        all_qualified = discovery.discover_qualified_leads(min_score=60)
        print(f"   Resultado: {len(all_qualified)} leads encontrados")
        
        # Show sample results if any found
        if all_qualified:
            print("\n🏆 TOP 3 LEADS ENCONTRADOS:")
            for i, lead in enumerate(all_qualified[:3], 1):
                print(f"{i}. {lead['company_name']}")
                print(f"   Score: {lead['qualification_score']}")
                print(f"   Setor: {lead['industry']}")
                print(f"   Localização: {lead['location']}")
                print(f"   Website: {lead['website']}")
                print()
        
        print("=" * 60)
        print("✅ TESTE CONCLUÍDO - BigQuery como fonte de descoberta de leads")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")
        print("\n💡 POSSÍVEIS SOLUÇÕES:")
        print("   1. Verificar conexão BigQuery")
        print("   2. Verificar se tabelas existem")
        print("   3. Verificar dados na tabela prospects")
        return False

if __name__ == "__main__":
    test_bigquery_lead_discovery()
