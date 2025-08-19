#!/usr/bin/env python3
"""
ARCO Strategic Lead Generation - MASTER EXECUTION
===============================================
Script principal que demonstra o novo sistema unificado de geração de leads.
Substitui os múltiplos scripts fragmentados por abordagem estratégica consolidada.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('data/strategic_execution.log')
    ]
)

logger = logging.getLogger(__name__)

from src.pipelines.consolidated_searchapi_pipeline import ConsolidatedSearchAPIPipeline, SearchAPIConfig
from src.core.unified_crm_system import UnifiedCRMEnrichmentEngine
from src.scoring.strategic_lead_scorer import StrategicLeadScorer

class ARCOStrategicLeadGeneration:
    """Sistema estratégico unificado de geração de leads"""
    
    def __init__(self, api_key: str = None):
        # Initialize components
        self.config = SearchAPIConfig(
            api_key=api_key or "demo_api_key",
            target_regions=["US", "GB", "CA", "AU"],  # English-speaking focus
            target_verticals=["marketing_agencies", "ecommerce", "saas", "dental"],
            budget_per_execution=1.00,  # $1 budget control
            max_leads_per_batch=30,
            quality_threshold=70.0
        )
        
        self.crm_engine = UnifiedCRMEnrichmentEngine()
        self.strategic_scorer = StrategicLeadScorer()
        
        # Execution tracking
        self.execution_id = f"strategic_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.results_dir = Path("data/strategic_results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    async def execute_strategic_lead_generation(self, target_count: int = 25) -> dict:
        """
        Executa geração estratégica de leads com abordagem unificada:
        
        1. Consolidated SearchAPI Pipeline (substitui layers fragmentados)
        2. Strategic Pain Signal Detection (realistic pain points)
        3. Growth Opportunity Analysis (data-driven opportunities)
        4. Unified CRM Enrichment (single batch output instead of layer outputs)
        5. Strategic Scoring & Prioritization (actionable outreach strategy)
        """
        
        logger.info(f"🚀 Starting ARCO Strategic Lead Generation - ID: {self.execution_id}")
        logger.info(f"Target: {target_count} high-quality leads")
        logger.info(f"Budget: ${self.config.budget_per_execution}")
        
        execution_results = {
            "execution_id": self.execution_id,
            "timestamp": datetime.now().isoformat(),
            "target_count": target_count,
            "config": {
                "regions": self.config.target_regions,
                "verticals": self.config.target_verticals,
                "budget": self.config.budget_per_execution,
                "quality_threshold": self.config.quality_threshold
            },
            "pipeline_results": {},
            "strategic_analysis": {},
            "final_leads": [],
            "execution_summary": {}
        }
        
        try:
            # Phase 1: Consolidated SearchAPI Pipeline
            logger.info("Phase 1: Executing Consolidated SearchAPI Pipeline")
            
            async with ConsolidatedSearchAPIPipeline(self.config) as pipeline:
                pipeline_results = await pipeline.execute_strategic_pipeline(target_count)
                execution_results["pipeline_results"] = pipeline_results
                
                logger.info(f"Pipeline completed: {len(pipeline_results.get('final_leads', []))} leads generated")
            
            # Phase 2: Strategic Analysis & Scoring
            logger.info("Phase 2: Strategic Analysis & Lead Scoring")
            
            raw_leads = pipeline_results.get("final_leads", [])
            strategic_analysis = await self._perform_strategic_analysis(raw_leads)
            execution_results["strategic_analysis"] = strategic_analysis
            
            # Phase 3: Final Lead Prioritization
            logger.info("Phase 3: Final Lead Prioritization & Output")
            
            prioritized_leads = self._prioritize_leads(strategic_analysis["scored_leads"])
            execution_results["final_leads"] = prioritized_leads
            
            # Phase 4: Execution Summary
            execution_summary = self._generate_execution_summary(execution_results)
            execution_results["execution_summary"] = execution_summary
            
            # Save consolidated results
            output_file = await self._save_strategic_results(execution_results)
            execution_results["output_file"] = output_file
            
            logger.info(f"✅ Strategic Lead Generation Complete - {len(prioritized_leads)} qualified leads")
            return execution_results
            
        except Exception as e:
            logger.error(f"❌ Strategic Lead Generation Failed: {e}")
            execution_results["error"] = str(e)
            return execution_results
    
    async def _perform_strategic_analysis(self, raw_leads: list) -> dict:
        """Realiza análise estratégica completa dos leads"""
        
        strategic_analysis = {
            "total_leads_analyzed": len(raw_leads),
            "scored_leads": [],
            "pain_signal_summary": {
                "critical_signals": 0,
                "high_signals": 0,
                "total_impact_value": 0
            },
            "opportunity_summary": {
                "high_value_opportunities": 0,
                "quick_win_opportunities": 0,
                "total_opportunity_value": 0
            },
            "scoring_distribution": {
                "high_score": 0,    # 80+
                "medium_score": 0,  # 60-80
                "low_score": 0      # <60
            }
        }
        
        for lead_data in raw_leads:
            try:
                # Strategic scoring
                strategic_score, analysis_details = self.strategic_scorer.calculate_strategic_score(lead_data)
                
                # Enrich lead with strategic analysis
                enriched_lead = {
                    **lead_data,
                    "strategic_score": strategic_score,
                    "strategic_analysis": analysis_details,
                    "analysis_timestamp": datetime.now().isoformat()
                }
                
                strategic_analysis["scored_leads"].append(enriched_lead)
                
                # Update summaries
                self._update_analysis_summaries(strategic_analysis, analysis_details, strategic_score)
                
            except Exception as e:
                logger.error(f"Strategic analysis failed for lead: {e}")
                continue
        
        return strategic_analysis
    
    def _update_analysis_summaries(self, strategic_analysis: dict, analysis_details: dict, strategic_score: float):
        """Atualiza sumários da análise estratégica"""
        
        # Pain signal summary
        pain_signals = analysis_details.get("pain_signals", [])
        for signal in pain_signals:
            severity = signal.get("severity", "low")
            if severity == "critical":
                strategic_analysis["pain_signal_summary"]["critical_signals"] += 1
            elif severity == "high":
                strategic_analysis["pain_signal_summary"]["high_signals"] += 1
        
        strategic_analysis["pain_signal_summary"]["total_impact_value"] += analysis_details.get("total_pain_impact", 0)
        
        # Opportunity summary
        opportunities = analysis_details.get("growth_opportunities", [])
        for opp in opportunities:
            if opp.get("potential_monthly_uplift", 0) > 5000:
                strategic_analysis["opportunity_summary"]["high_value_opportunities"] += 1
            if "2-4 weeks" in opp.get("implementation_timeline", ""):
                strategic_analysis["opportunity_summary"]["quick_win_opportunities"] += 1
        
        strategic_analysis["opportunity_summary"]["total_opportunity_value"] += analysis_details.get("total_opportunity_value", 0)
        
        # Score distribution
        if strategic_score >= 80:
            strategic_analysis["scoring_distribution"]["high_score"] += 1
        elif strategic_score >= 60:
            strategic_analysis["scoring_distribution"]["medium_score"] += 1
        else:
            strategic_analysis["scoring_distribution"]["low_score"] += 1
    
    def _prioritize_leads(self, scored_leads: list) -> list:
        """Prioriza leads baseado na análise estratégica"""
        
        # Sort by strategic score and priority factors
        def prioritization_score(lead):
            strategic_score = lead.get("strategic_score", 0)
            analysis = lead.get("strategic_analysis", {})
            
            # Bonus points for critical pain signals
            critical_bonus = len([s for s in analysis.get("pain_signals", []) if s.get("severity") == "critical"]) * 5
            
            # Bonus points for high-value opportunities
            opportunity_bonus = len([o for o in analysis.get("growth_opportunities", []) if o.get("potential_monthly_uplift", 0) > 5000]) * 3
            
            # Bonus for quick wins
            quick_win_bonus = len([o for o in analysis.get("growth_opportunities", []) if "2-4 weeks" in o.get("implementation_timeline", "")]) * 2
            
            return strategic_score + critical_bonus + opportunity_bonus + quick_win_bonus
        
        # Sort and add final rankings
        sorted_leads = sorted(scored_leads, key=prioritization_score, reverse=True)
        
        for i, lead in enumerate(sorted_leads, 1):
            lead["final_ranking"] = i
            lead["outreach_priority"] = self._determine_outreach_priority(i, len(sorted_leads))
        
        return sorted_leads
    
    def _determine_outreach_priority(self, ranking: int, total_leads: int) -> str:
        """Determina prioridade de outreach baseada no ranking"""
        
        if ranking <= max(5, total_leads * 0.2):  # Top 20% or top 5
            return "immediate"
        elif ranking <= max(10, total_leads * 0.4):  # Top 40% or top 10
            return "high"
        elif ranking <= max(15, total_leads * 0.6):  # Top 60% or top 15
            return "medium"
        else:
            return "low"
    
    def _generate_execution_summary(self, execution_results: dict) -> dict:
        """Gera sumário executivo dos resultados"""
        
        pipeline_results = execution_results.get("pipeline_results", {})
        strategic_analysis = execution_results.get("strategic_analysis", {})
        final_leads = execution_results.get("final_leads", [])
        
        # Calculate ROI projections
        total_opportunity_value = strategic_analysis.get("opportunity_summary", {}).get("total_opportunity_value", 0)
        execution_cost = pipeline_results.get("execution_stats", {}).get("total_cost", 0)
        
        return {
            "execution_performance": {
                "target_leads": execution_results["target_count"],
                "leads_generated": len(final_leads),
                "success_rate": len(final_leads) / max(execution_results["target_count"], 1) * 100,
                "cost_per_lead": execution_cost / max(len(final_leads), 1),
                "budget_utilization": execution_cost / self.config.budget_per_execution * 100
            },
            "lead_quality_metrics": {
                "high_priority_leads": len([l for l in final_leads if l.get("outreach_priority") == "immediate"]),
                "average_strategic_score": sum(l.get("strategic_score", 0) for l in final_leads) / max(len(final_leads), 1),
                "leads_with_critical_pain": strategic_analysis.get("pain_signal_summary", {}).get("critical_signals", 0),
                "leads_with_quick_wins": strategic_analysis.get("opportunity_summary", {}).get("quick_win_opportunities", 0)
            },
            "business_impact_projection": {
                "total_opportunity_value": total_opportunity_value,
                "average_opportunity_per_lead": total_opportunity_value / max(len(final_leads), 1),
                "projected_3_month_roi": total_opportunity_value * 0.3 / max(execution_cost, 0.01),  # Conservative 30% capture
                "high_value_prospects": len([l for l in final_leads if l.get("strategic_analysis", {}).get("total_opportunity_value", 0) > 10000])
            },
            "strategic_insights": {
                "top_pain_categories": self._identify_top_pain_categories(final_leads),
                "top_opportunity_types": self._identify_top_opportunity_types(final_leads),
                "recommended_outreach_sequence": self._generate_outreach_sequence(final_leads),
                "market_insights": self._generate_market_insights(final_leads)
            }
        }
    
    def _identify_top_pain_categories(self, leads: list) -> list:
        """Identifica categorias de pain mais comuns"""
        
        pain_categories = {}
        
        for lead in leads:
            pain_signals = lead.get("strategic_analysis", {}).get("pain_signals", [])
            for signal in pain_signals:
                category = signal.get("solution_category", "unknown")
                if category not in pain_categories:
                    pain_categories[category] = 0
                pain_categories[category] += 1
        
        return sorted(pain_categories.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def _identify_top_opportunity_types(self, leads: list) -> list:
        """Identifica tipos de oportunidade mais comuns"""
        
        opportunity_types = {}
        
        for lead in leads:
            opportunities = lead.get("strategic_analysis", {}).get("growth_opportunities", [])
            for opp in opportunities:
                opp_type = opp.get("opportunity_type", "unknown")
                if opp_type not in opportunity_types:
                    opportunity_types[opp_type] = 0
                opportunity_types[opp_type] += 1
        
        return sorted(opportunity_types.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def _generate_outreach_sequence(self, leads: list) -> list:
        """Gera sequência recomendada de outreach"""
        
        immediate_leads = [l for l in leads if l.get("outreach_priority") == "immediate"]
        high_priority_leads = [l for l in leads if l.get("outreach_priority") == "high"]
        
        return [
            {
                "priority": "immediate",
                "count": len(immediate_leads),
                "timeline": "0-3 days",
                "approach": "direct_consultation",
                "message_focus": "critical_pain_resolution"
            },
            {
                "priority": "high",
                "count": len(high_priority_leads),
                "timeline": "4-10 days",
                "approach": "solution_presentation",
                "message_focus": "growth_opportunities"
            },
            {
                "priority": "medium",
                "count": len([l for l in leads if l.get("outreach_priority") == "medium"]),
                "timeline": "11-21 days",
                "approach": "educational_nurture",
                "message_focus": "industry_insights"
            }
        ]
    
    def _generate_market_insights(self, leads: list) -> dict:
        """Gera insights de mercado baseados nos dados dos leads"""
        
        industries = {}
        regions = {}
        avg_spend_by_industry = {}
        
        for lead in leads:
            # Industry distribution
            industry = lead.get("industry", "unknown")
            if industry not in industries:
                industries[industry] = 0
            industries[industry] += 1
            
            # Region distribution
            country = lead.get("country", "unknown")
            if country not in regions:
                regions[country] = 0
            regions[country] += 1
            
            # Spend by industry
            spend = lead.get("estimated_monthly_spend", 0)
            if industry not in avg_spend_by_industry:
                avg_spend_by_industry[industry] = []
            avg_spend_by_industry[industry].append(spend)
        
        # Calculate averages
        for industry in avg_spend_by_industry:
            spends = avg_spend_by_industry[industry]
            avg_spend_by_industry[industry] = sum(spends) / len(spends) if spends else 0
        
        return {
            "industry_distribution": sorted(industries.items(), key=lambda x: x[1], reverse=True),
            "region_distribution": sorted(regions.items(), key=lambda x: x[1], reverse=True),
            "average_spend_by_industry": avg_spend_by_industry,
            "total_market_size": sum(lead.get("estimated_monthly_spend", 0) for lead in leads)
        }
    
    async def _save_strategic_results(self, execution_results: dict) -> str:
        """Salva resultados estratégicos consolidados"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"strategic_lead_generation_{timestamp}.json"
        filepath = self.results_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(execution_results, f, indent=2, ensure_ascii=False)
        
        # Also save executive summary
        summary_filename = f"executive_summary_{timestamp}.json"
        summary_filepath = self.results_dir / summary_filename
        
        executive_summary = {
            "execution_id": execution_results["execution_id"],
            "timestamp": execution_results["timestamp"],
            "execution_summary": execution_results["execution_summary"],
            "top_10_leads": execution_results["final_leads"][:10]
        }
        
        with open(summary_filepath, 'w', encoding='utf-8') as f:
            json.dump(executive_summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Strategic results saved: {filepath}")
        logger.info(f"Executive summary saved: {summary_filepath}")
        
        return str(filepath)

async def main():
    """Função principal para execução do sistema estratégico"""
    
    print("\n" + "="*60)
    print("🚀 ARCO STRATEGIC LEAD GENERATION SYSTEM")
    print("="*60)
    print("Unified approach to lead generation with strategic focus")
    print("• Consolidated SearchAPI Pipeline")
    print("• Realistic Pain Signal Detection") 
    print("• Growth Opportunity Analysis")
    print("• Unified CRM Enrichment")
    print("• Strategic Scoring & Prioritization")
    print("="*60)
    
    # Initialize strategic system
    strategic_system = ARCOStrategicLeadGeneration(api_key="demo_key")
    
    # Execute strategic lead generation
    results = await strategic_system.execute_strategic_lead_generation(target_count=20)
    
    # Display executive summary
    if "execution_summary" in results:
        summary = results["execution_summary"]
        
        print(f"\n📊 EXECUTION RESULTS")
        print(f"Execution ID: {results['execution_id']}")
        print(f"Leads Generated: {summary['execution_performance']['leads_generated']}")
        print(f"Success Rate: {summary['execution_performance']['success_rate']:.1f}%")
        print(f"Cost per Lead: ${summary['execution_performance']['cost_per_lead']:.3f}")
        
        print(f"\n🎯 LEAD QUALITY")
        print(f"High Priority Leads: {summary['lead_quality_metrics']['high_priority_leads']}")
        print(f"Average Strategic Score: {summary['lead_quality_metrics']['average_strategic_score']:.1f}/100")
        print(f"Critical Pain Signals: {summary['lead_quality_metrics']['leads_with_critical_pain']}")
        print(f"Quick Win Opportunities: {summary['lead_quality_metrics']['leads_with_quick_wins']}")
        
        print(f"\n💰 BUSINESS IMPACT")
        print(f"Total Opportunity Value: ${summary['business_impact_projection']['total_opportunity_value']:,.0f}")
        print(f"Avg Opportunity/Lead: ${summary['business_impact_projection']['average_opportunity_per_lead']:,.0f}")
        print(f"Projected 3-Month ROI: {summary['business_impact_projection']['projected_3_month_roi']:.1f}x")
        print(f"High-Value Prospects: {summary['business_impact_projection']['high_value_prospects']}")
        
        print(f"\n📈 STRATEGIC INSIGHTS")
        print("Top Pain Categories:")
        for category, count in summary['strategic_insights']['top_pain_categories'][:3]:
            print(f"  • {category}: {count} leads")
        
        print("Recommended Outreach:")
        for sequence in summary['strategic_insights']['recommended_outreach_sequence']:
            print(f"  • {sequence['priority'].upper()}: {sequence['count']} leads ({sequence['timeline']})")
    
    print(f"\n✅ Results saved: {results.get('output_file', 'N/A')}")
    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(main())