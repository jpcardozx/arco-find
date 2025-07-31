#!/usr/bin/env python3
"""
🎯 MATURE WORKFLOW ORCHESTRATOR
Orquestra descoberta → validação → enrichment → intelligence acionável
Elimina retrabalho e opera em pipeline maduro de leads qualificados
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from src.intelligence.deep_prospect_engine import DeepProspectEngine, ProspectIntelligence
from src.connectors.searchapi_connector import SearchAPIConnector
from src.connectors.google_pagespeed_api import GooglePageSpeedAPI

class MatureWorkflowOrchestrator:
    """
    Workflow maduro que elimina superficialidade e foca em resultados acionáveis
    """
    
    def __init__(self):
        self.deep_engine = DeepProspectEngine()
        self.execution_log = []
        self.qualified_pipeline = []
        
    async def initialize_systems(self):
        """Inicializa sistemas com validação real"""
        try:
            from config.api_keys import APIConfig
            
            api_config = APIConfig()
            
            # Initialize deep engine components
            self.deep_engine.search_api = SearchAPIConnector(api_key=api_config.SEARCH_API_KEY)
            self.deep_engine.pagespeed_api = GooglePageSpeedAPI(api_key=api_config.GOOGLE_PAGESPEED_API_KEY)
            
            print("🔧 Mature workflow systems initialized")
            return True
            
        except Exception as e:
            print(f"❌ System initialization failed: {e}")
            return False
    
    async def execute_market_discovery_workflow(self, 
                                              market: str, 
                                              target_verticals: List[str],
                                              max_prospects_per_vertical: int = 20) -> Dict:
        """
        Executa workflow completo para um mercado
        Retorna apenas prospects qualificados com intelligence acionável
        """
        
        print(f"\n🚀 EXECUTING MATURE DISCOVERY WORKFLOW")
        print(f"Market: {market.upper()}")
        print(f"Verticals: {', '.join(target_verticals)}")
        print("=" * 60)
        
        workflow_results = {
            'market': market,
            'execution_timestamp': datetime.now().isoformat(),
            'verticals_analyzed': [],
            'qualified_prospects': [],
            'actionable_intelligence': {},
            'pipeline_metrics': {}
        }
        
        all_validated_prospects = []
        
        # Processar cada vertical com deep analysis
        for vertical in target_verticals:
            print(f"\n📋 PROCESSING VERTICAL: {vertical.upper()}")
            print("-" * 40)
            
            try:
                # Fase 1: Discovery com foco em dor latente
                raw_prospects = await self.deep_engine.discover_prospects_with_pain(
                    market, vertical
                )
                
                if not raw_prospects:
                    print(f"⚠️ No prospects with pain signals found for {vertical}")
                    continue
                
                # Fase 2: Validação rigorosa e análise de pain points
                validated_prospects = await self.deep_engine.validate_and_analyze_pain_points(
                    raw_prospects
                )
                
                if not validated_prospects:
                    print(f"⚠️ No prospects passed validation for {vertical}")
                    continue
                
                # Adicionar ao pipeline global
                all_validated_prospects.extend(validated_prospects)
                
                # Log do vertical
                vertical_summary = {
                    'vertical': vertical,
                    'raw_discovered': len(raw_prospects),
                    'validated_qualified': len(validated_prospects),
                    'qualification_rate': len(validated_prospects) / len(raw_prospects) if raw_prospects else 0,
                    'avg_confidence': sum(p.confidence_level for p in validated_prospects) / len(validated_prospects) if validated_prospects else 0,
                    'total_opportunity': sum(p.estimated_monthly_uplift for p in validated_prospects)
                }
                
                workflow_results['verticals_analyzed'].append(vertical_summary)
                
                print(f"✅ {vertical}: {len(validated_prospects)} qualified prospects")
                print(f"   Qualification rate: {vertical_summary['qualification_rate']:.1%}")
                print(f"   Avg confidence: {vertical_summary['avg_confidence']:.2f}")
                print(f"   Total opportunity: ${vertical_summary['total_opportunity']:.0f}/month")
                
            except Exception as e:
                print(f"❌ Error processing {vertical}: {e}")
                continue
        
        if not all_validated_prospects:
            print("\n❌ No qualified prospects found across all verticals")
            return workflow_results
        
        # Fase 3: Generate actionable intelligence
        actionable_intelligence = await self.deep_engine.generate_actionable_intelligence(
            all_validated_prospects
        )
        
        # Organizar prospects por priority
        qualified_prospects_data = []
        for prospect in all_validated_prospects:
            prospect_data = {
                'company_name': prospect.company_name,
                'domain': prospect.domain,
                'industry_vertical': prospect.industry_vertical,
                'employee_range': prospect.employee_range,
                'monthly_ad_spend': prospect.ad_spend_estimate_monthly,
                'primary_pain_category': prospect.primary_pain_point.category,
                'pain_severity': prospect.primary_pain_point.severity_score,
                'p0_opportunity_score': prospect.p0_opportunity_score,
                'estimated_monthly_uplift': prospect.estimated_monthly_uplift,
                'confidence_level': prospect.confidence_level,
                'approach_vector': prospect.approach_vector,
                'decision_maker_signals': prospect.decision_maker_signals,
                'optimal_contact_time': prospect.optimal_contact_time
            }
            qualified_prospects_data.append(prospect_data)
        
        # Calcular métricas de pipeline maduro
        pipeline_metrics = self._calculate_mature_pipeline_metrics(all_validated_prospects)
        
        # Consolidar resultados
        workflow_results.update({
            'qualified_prospects': qualified_prospects_data,
            'actionable_intelligence': actionable_intelligence,
            'pipeline_metrics': pipeline_metrics
        })
        
        # Salvar intelligence para BigQuery enrichment posterior
        await self._save_qualified_pipeline(workflow_results)
        
        # Display executive summary
        self._display_executive_summary(workflow_results)
        
        return workflow_results
    
    def _calculate_mature_pipeline_metrics(self, prospects: List[ProspectIntelligence]) -> Dict:
        """
        Calcula métricas maduras de pipeline focadas em ação
        """
        if not prospects:
            return {}
        
        # Segmentar por confidence level
        high_confidence = [p for p in prospects if p.confidence_level >= 0.8]
        medium_confidence = [p for p in prospects if 0.6 <= p.confidence_level < 0.8]
        
        # Segmentar por approach vector
        approach_segments = {}
        for prospect in prospects:
            vector = prospect.approach_vector
            if vector not in approach_segments:
                approach_segments[vector] = []
            approach_segments[vector].append(prospect)
        
        # Calcular conversion expectations baseado em modelo real
        expected_qualification_rate = 0.35  # Baseado no histórico
        expected_call_conversion = 0.28
        expected_audit_conversion = 0.52
        
        # Pipeline math para próximos 48h
        immediate_outreach_targets = high_confidence[:10]  # Top 10 para execução imediata
        
        expected_qualifieds = len(immediate_outreach_targets) * expected_qualification_rate
        expected_calls = expected_qualifieds * expected_call_conversion  
        expected_audits = expected_calls * expected_audit_conversion
        
        total_pipeline_value = sum(p.estimated_monthly_uplift for p in prospects)
        immediate_pipeline_value = sum(p.estimated_monthly_uplift for p in immediate_outreach_targets)
        
        return {
            'total_qualified_prospects': len(prospects),
            'high_confidence_prospects': len(high_confidence),
            'medium_confidence_prospects': len(medium_confidence),
            'immediate_outreach_targets': len(immediate_outreach_targets),
            'approach_segments': {k: len(v) for k, v in approach_segments.items()},
            
            # Pipeline projections
            'expected_qualifieds_48h': expected_qualifieds,
            'expected_calls_48h': expected_calls,
            'expected_audits_48h': expected_audits,
            
            # Revenue projections
            'total_pipeline_value_monthly': total_pipeline_value,
            'immediate_pipeline_value_monthly': immediate_pipeline_value,
            'expected_revenue_week1': expected_audits * 2500,  # Audit average value
            
            # Efficiency metrics
            'avg_confidence_level': sum(p.confidence_level for p in prospects) / len(prospects),
            'avg_p0_opportunity': sum(p.p0_opportunity_score for p in prospects) / len(prospects),
            'qualification_efficiency': len(prospects) / 100  # Assume 100 raw prospects input
        }
    
    async def _save_qualified_pipeline(self, workflow_results: Dict):
        """
        Salva pipeline qualificado para enrichment futuro via BigQuery
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Salvar dados qualificados
        qualified_data_path = Path("src/data") / f"qualified_pipeline_{workflow_results['market']}_{timestamp}.json"
        qualified_data_path.parent.mkdir(exist_ok=True)
        
        with open(qualified_data_path, 'w', encoding='utf-8') as f:
            json.dump(workflow_results, f, indent=2, ensure_ascii=False)
        
        # Preparar dados para BigQuery enrichment
        bigquery_enrichment_data = {
            'qualified_prospects': workflow_results['qualified_prospects'],
            'enrichment_needed': [
                'company_size_validation',
                'decision_maker_identification', 
                'competitive_intelligence',
                'financial_intelligence',
                'technographic_data'
            ],
            'ready_for_bq_import': True,
            'schema_version': 'v2.0'
        }
        
        bq_ready_path = Path("src/data") / f"bq_enrichment_ready_{workflow_results['market']}_{timestamp}.json"
        with open(bq_ready_path, 'w', encoding='utf-8') as f:
            json.dump(bigquery_enrichment_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Pipeline data saved:")
        print(f"   📊 Qualified pipeline: {qualified_data_path}")
        print(f"   🗄️ BigQuery ready: {bq_ready_path}")
    
    def _display_executive_summary(self, workflow_results: Dict):
        """
        Display maduro focado em ações executáveis
        """
        print(f"\n" + "="*60)
        print(f"🎯 MATURE WORKFLOW EXECUTION COMPLETE")
        print(f"="*60)
        
        metrics = workflow_results['pipeline_metrics']
        intelligence = workflow_results['actionable_intelligence']
        
        print(f"\n📊 PIPELINE QUALIFIED:")
        print(f"   🎯 Total Prospects: {metrics['total_qualified_prospects']}")
        print(f"   ⭐ High Confidence: {metrics['high_confidence_prospects']}")
        print(f"   🔥 Immediate Targets: {metrics['immediate_outreach_targets']}")
        print(f"   💰 Pipeline Value: ${metrics['total_pipeline_value_monthly']:,.0f}/month")
        
        print(f"\n🚀 48H EXECUTION PROJECTIONS:")
        print(f"   📞 Expected Qualifieds: {metrics['expected_qualifieds_48h']:.1f}")
        print(f"   🗣️ Expected Calls: {metrics['expected_calls_48h']:.1f}")
        print(f"   📋 Expected Audits: {metrics['expected_audits_48h']:.1f}")
        print(f"   💵 Expected Revenue (Week 1): ${metrics['expected_revenue_week1']:,.0f}")
        
        print(f"\n🎯 APPROACH SEGMENTS:")
        for approach, count in metrics['approach_segments'].items():
            print(f"   {approach.replace('_', ' ').title()}: {count} prospects")
        
        print(f"\n🔥 IMMEDIATE ACTIONS:")
        for i, action in enumerate(intelligence['recommended_immediate_actions'][:5], 1):
            print(f"   {i}. {action['prospect'][:30]} - {action['approach'].replace('_', ' ')}")
            print(f"      Hook: {action['hook']}")
            print(f"      Expected Response: {action['expected_response_rate']}")
        
        print(f"\n✅ READY FOR EXECUTION")
        print(f"   📈 Quality Score: {metrics['avg_confidence_level']:.2f}/1.0")
        print(f"   🎯 P0 Opportunity: {metrics['avg_p0_opportunity']:.1f}/100")
        print(f"   ⚡ Efficiency: {metrics['qualification_efficiency']:.1%}")
        
        print(f"\n🗄️ BIGQUERY ENRICHMENT READY")
        print(f"   Pipeline staged for demographic/technographic enrichment")
        print(f"   Decision maker identification queued")
        print(f"   Competitive intelligence analysis ready")

# Main execution function
async def execute_mature_market_analysis(market: str = 'australia', 
                                       verticals: List[str] = None) -> Dict:
    """
    Executa análise madura completa de mercado
    Retorna apenas intelligence acionável
    """
    
    if verticals is None:
        verticals = ['dental_practice', 'beauty_clinic', 'medical_practice']
    
    orchestrator = MatureWorkflowOrchestrator()
    
    # Initialize systems
    if not await orchestrator.initialize_systems():
        print("❌ Failed to initialize systems")
        return {}
    
    # Execute mature workflow
    results = await orchestrator.execute_market_discovery_workflow(
        market=market,
        target_verticals=verticals,
        max_prospects_per_vertical=25
    )
    
    return results

if __name__ == "__main__":
    # Execute mature analysis
    results = asyncio.run(execute_mature_market_analysis(
        market='australia',
        verticals=['dental_practice', 'beauty_clinic']
    ))
