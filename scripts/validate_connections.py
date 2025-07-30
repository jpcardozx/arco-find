#!/usr/bin/env python3
"""
🔧 ARCO-FIND CONNECTION VALIDATOR
Valida conexões com BigQuery e SearchAPI e cria pipeline claro
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Add src to path
project_root = Path(__file__).parent.parent  # Go up one level from scripts/
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

async def validate_connections():
    """Valida todas as conexões API"""
    
    print("🔧 VALIDANDO CONEXÕES ARCO-FIND")
    print("=" * 50)
    
    results = {
        'bigquery': {'status': 'UNKNOWN', 'details': {}},
        'searchapi': {'status': 'UNKNOWN', 'details': {}},
        'connections_healthy': False
    }
    
    # 1. Validar BigQuery
    print("\n📊 VALIDANDO BIGQUERY...")
    try:
        from config.api_keys import APIConfig
        from google.cloud import bigquery
        
        api_config = APIConfig()
        
        # Tentar conectar ao BigQuery
        try:
            bq_client = bigquery.Client(project=api_config.GOOGLE_CLOUD_PROJECT)
            
            # Teste de query simples
            test_query = "SELECT 'BigQuery Connected' as status"
            query_job = bq_client.query(test_query)
            result = list(query_job.result())
            
            if result:
                results['bigquery']['status'] = 'CONNECTED'
                results['bigquery']['details'] = {
                    'project': api_config.GOOGLE_CLOUD_PROJECT,
                    'dataset': api_config.BIGQUERY_DATASET_ID,
                    'test_query_success': True
                }
                print(f"  ✅ BigQuery CONECTADO - Projeto: {api_config.GOOGLE_CLOUD_PROJECT}")
            else:
                results['bigquery']['status'] = 'ERROR'
                print("  ❌ BigQuery - Query test failed")
                
        except Exception as e:
            results['bigquery']['status'] = 'ERROR'
            results['bigquery']['details'] = {'error': str(e)}
            print(f"  ❌ BigQuery ERRO: {e}")
            
    except ImportError as e:
        results['bigquery']['status'] = 'MISSING_DEPS'
        print(f"  ⚠️ BigQuery dependencies missing: {e}")
    
    # 2. Validar SearchAPI
    print("\n🔍 VALIDANDO SEARCHAPI...")
    try:
        from src.connectors.searchapi_connector import SearchAPIConnector
        from config.api_keys import APIConfig
        
        api_config = APIConfig()
        search_api = SearchAPIConnector(api_key=api_config.SEARCH_API_KEY)
        
        # Teste de busca simples
        test_results = await search_api.search_companies("fintech", max_results=1)
        
        if test_results:
            results['searchapi']['status'] = 'CONNECTED'
            results['searchapi']['details'] = {
                'api_key_configured': bool(api_config.SEARCH_API_KEY),
                'test_search_success': True,
                'results_count': len(test_results)
            }
            print(f"  ✅ SearchAPI CONECTADO - {len(test_results)} results")
        else:
            results['searchapi']['status'] = 'NO_RESULTS'
            print("  ⚠️ SearchAPI conectado mas sem resultados de teste")
            
    except Exception as e:
        results['searchapi']['status'] = 'ERROR'
        results['searchapi']['details'] = {'error': str(e)}
        print(f"  ❌ SearchAPI ERRO: {e}")
    
    # 3. Status geral
    bq_ok = results['bigquery']['status'] == 'CONNECTED'
    search_ok = results['searchapi']['status'] in ['CONNECTED', 'NO_RESULTS']
    
    results['connections_healthy'] = bq_ok and search_ok
    
    print(f"\n🎯 STATUS GERAL: {'✅ SAUDÁVEL' if results['connections_healthy'] else '⚠️ NECESSITA ATENÇÃO'}")
    
    return results

async def test_lead_discovery_pipeline():
    """Testa o pipeline de descoberta de leads"""
    
    print("\n🚀 TESTANDO PIPELINE DE DESCOBERTA")
    print("=" * 50)
    
    try:
        from src.core.lead_qualification_engine import LeadQualificationEngine
        
        # Inicializar engine
        lead_engine = LeadQualificationEngine()
        print("  📋 LeadQualificationEngine inicializado")
        
        # Executar descoberta de leads
        print("  🔍 Executando descoberta de leads...")
        start_time = datetime.now()
        
        qualified_leads = await lead_engine.discover_qualified_leads(target_count=3)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        print(f"  ✅ Descoberta concluída em {execution_time:.2f}s")
        print(f"  🎯 Leads qualificados encontrados: {len(qualified_leads)}")
        
        if qualified_leads:
            print("\n  📊 SAMPLE LEADS:")
            for i, lead in enumerate(qualified_leads[:2], 1):
                print(f"    {i}. {lead.company_name}")
                print(f"       Score: {lead.qualification_score}/100")
                print(f"       Priority: {lead.conversion_priority}")
        
        return {
            'pipeline_working': True,
            'execution_time': execution_time,
            'leads_found': len(qualified_leads),
            'sample_leads': qualified_leads[:2] if qualified_leads else []
        }
        
    except Exception as e:
        print(f"  ❌ Pipeline ERROR: {e}")
        return {
            'pipeline_working': False,
            'error': str(e)
        }

def create_pipeline_documentation():
    """Cria documentação clara do pipeline"""
    
    doc_content = '''# 🎯 ARCO-FIND LEAD DISCOVERY PIPELINE

## 📊 ARQUITETURA ATUAL

### 1. Core Components
- **LeadQualificationEngine**: Engine principal de qualificação
- **StrategicLeadOrchestrator**: Orquestrador de descoberta inteligente
- **SearchAPIConnector**: Integração com Meta Ads Library
- **BigQueryIntelligence**: Analytics e armazenamento

### 2. Data Sources
- **SearchAPI**: Meta Ads Library (dados reais de anúncios)
- **BigQuery**: Google Cloud storage e analytics
- **PageSpeed API**: Performance analysis

### 3. Pipeline Flow
```
Input (Target Count) 
    ↓
LeadQualificationEngine.discover_qualified_leads()
    ↓
1. Check existing hot leads (BigQuery - FREE)
    ↓
2. If needed, discover new leads (SearchAPI)
    ↓
3. Qualify and score leads
    ↓
4. Store in BigQuery for future use
    ↓
Output (Qualified Leads List)
```

## 🔧 CURRENT STATUS

### ✅ Working Components
- ✅ API configurations loaded
- ✅ SearchAPI connector functional
- ✅ Lead qualification engine operational
- ✅ Basic BigQuery integration

### ⚠️ Needs Improvement
- ⚠️ BigQuery schema validation
- ⚠️ Missing discover_strategic_prospects method
- ⚠️ Enhanced error handling
- ⚠️ Performance optimization

## 🚀 NEXT ACTIONS

### 1. Immediate Fixes
- [ ] Implement discover_strategic_prospects in SearchAPIConnector
- [ ] Validate/create BigQuery tables
- [ ] Fix qualification_score field issues

### 2. Pipeline Enhancement
- [ ] Add intelligent caching
- [ ] Implement rate limiting
- [ ] Add cost monitoring
- [ ] Create comprehensive logging

### 3. Documentation
- [ ] API usage guidelines
- [ ] Cost optimization strategies
- [ ] Error handling procedures

## 📈 SUCCESS METRICS
- **Response Time**: < 2 seconds per lead discovery
- **API Cost**: < $1 per 100 qualified leads
- **Success Rate**: > 90% successful qualifications
- **Data Quality**: > 80% qualification score accuracy

## 🎯 ULTIMATE GOAL
Automated, cost-efficient lead discovery pipeline that:
1. Identifies high-value prospects using real Meta Ads data
2. Qualifies leads with actionable intelligence
3. Stores results for strategic analysis
4. Scales efficiently with controlled costs
'''

    with open(project_root / "PIPELINE_DOCUMENTATION.md", "w", encoding="utf-8") as f:
        f.write(doc_content)
    
    print("📄 Pipeline documentation created: PIPELINE_DOCUMENTATION.md")

async def main():
    """Main validation and testing function"""
    
    print("🎯 ARCO-FIND CONNECTION & PIPELINE VALIDATOR")
    print("=" * 60)
    print(f"📅 Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Validate connections
    connection_results = await validate_connections()
    
    # 2. Test pipeline
    pipeline_results = await test_lead_discovery_pipeline()
    
    # 3. Create documentation
    create_pipeline_documentation()
    
    # 4. Summary report
    print("\n" + "=" * 60)
    print("📋 VALIDATION SUMMARY")
    print("=" * 60)
    
    print(f"🔗 BigQuery: {connection_results['bigquery']['status']}")
    print(f"🔍 SearchAPI: {connection_results['searchapi']['status']}")
    print(f"🚀 Pipeline: {'✅ WORKING' if pipeline_results['pipeline_working'] else '❌ BROKEN'}")
    
    if pipeline_results['pipeline_working']:
        print(f"⏱️ Execution Time: {pipeline_results['execution_time']:.2f}s")
        print(f"🎯 Leads Found: {pipeline_results['leads_found']}")
    
    print(f"\n🎯 Overall Status: {'✅ OPERATIONAL' if connection_results['connections_healthy'] and pipeline_results['pipeline_working'] else '⚠️ NEEDS ATTENTION'}")
    
    # Save results
    import json
    results_file = project_root / f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'validation_timestamp': datetime.now().isoformat(),
            'connections': connection_results,
            'pipeline': pipeline_results
        }, f, indent=2, default=str)
    
    print(f"💾 Results saved: {results_file.name}")

if __name__ == "__main__":
    asyncio.run(main())
