"""
🚀 EXECUTOR REAL ARCO-FIND - USANDO MÓDULOS EXISTENTES
Executar pipeline real usando LeadQualificationEngine e BigQuery existentes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import asyncio
import json
from datetime import datetime
from pathlib import Path

# Import existing real modules
try:
    from config.api_keys import APIConfig
    from src.utils.logger import setup_logger, cost_tracker, performance_monitor
    from src.core.lead_qualification_engine import LeadQualificationEngine
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🔄 Trying alternative imports...")
    try:
        import sys
        sys.path.append('src')
        from utils.logger import setup_logger, cost_tracker, performance_monitor
        from core.lead_qualification_engine import LeadQualificationEngine
        from config.api_keys import APIConfig
    except ImportError as e2:
        print(f"❌ Alternative import also failed: {e2}")
        print("🚨 Running in fallback mode...")
        # Fallback mode without real modules
        class MockLogger:
            def info(self, msg): print(f"INFO: {msg}")
            def warning(self, msg): print(f"WARNING: {msg}")
            def error(self, msg): print(f"ERROR: {msg}")
        
        def setup_logger(name): return MockLogger()
        
        class MockTracker:
            def track_operation_cost(self, op, cost, details): pass
            def get_daily_summary(self): return {"total_cost": 0.0}
        
        class MockMonitor:
            def start_operation(self, op): return "mock_id"
            def end_operation(self, op_id, details): pass
        
        cost_tracker = MockTracker()
        performance_monitor = MockMonitor()
        
        class MockEngine:
            async def discover_qualified_leads(self, count): return []
        
        LeadQualificationEngine = MockEngine
        
        class APIConfig:
            GOOGLE_CLOUD_PROJECT = "mock-project"

logger = setup_logger(__name__)

class ArcoFindRealExecutor:
    """
    Executor real usando módulos existentes do ARCO-FIND
    """
    
    def __init__(self):
        self.config = APIConfig()
        self.logger = logger
        
        # Initialize real components
        try:
            self.lead_engine = LeadQualificationEngine()
            self.real_modules = True
            self.logger.info("✅ Real ARCO-FIND modules loaded successfully")
        except Exception as e:
            self.logger.warning(f"⚠️ Could not initialize real modules: {e}")
            self.real_modules = False
    
    async def execute_real_pipeline(self) -> dict:
        """
        Execute real ARCO-FIND pipeline using existing modules
        """
        
        pipeline_id = performance_monitor.start_operation("real_arco_pipeline")
        
        try:
            self.logger.info("🚀 Starting REAL ARCO-FIND Pipeline Execution")
            self.logger.info("📊 Using existing LeadQualificationEngine + BigQuery + SearchAPI")
            
            if not self.real_modules:
                return await self._execute_fallback_demo()
            
            # Stage 1: Use real LeadQualificationEngine
            self.logger.info("🎯 Stage 1: Real Lead Discovery via LeadQualificationEngine")
            qualified_leads = await self.lead_engine.discover_qualified_leads(target_count=10)
            
            cost_tracker.track_operation_cost("lead_qualification_engine", 1.50, {
                "leads_discovered": len(qualified_leads),
                "engine": "real"
            })
            
            # Stage 2: Process and analyze real leads
            self.logger.info("📈 Stage 2: Real Lead Analysis and Scoring")
            analyzed_leads = await self._analyze_real_leads(qualified_leads)
            
            # Stage 3: Generate real business intelligence
            self.logger.info("🧠 Stage 3: Business Intelligence Generation")
            intelligence_report = await self._generate_real_intelligence(analyzed_leads)
            
            # Stage 4: Create actionable results
            final_report = await self._create_actionable_report(intelligence_report, analyzed_leads)
            
            performance_monitor.end_operation(pipeline_id, {
                "total_leads": len(qualified_leads),
                "analyzed_leads": len(analyzed_leads),
                "success": True,
                "real_modules": True
            })
            
            return final_report
            
        except Exception as e:
            self.logger.error(f"❌ Real pipeline execution failed: {e}")
            performance_monitor.end_operation(pipeline_id, {"error": str(e), "success": False})
            
            # Fallback to demo mode
            return await self._execute_fallback_demo()
    
    async def _analyze_real_leads(self, qualified_leads) -> list:
        """
        Analyze real leads from LeadQualificationEngine
        """
        
        analyzed_leads = []
        
        for lead in qualified_leads:
            try:
                # Extract real data from QualifiedLead dataclass
                analyzed_lead = {
                    "company_name": getattr(lead, 'company_name', 'Unknown Company'),
                    "website": getattr(lead, 'website', 'unknown.com'),
                    "industry": getattr(lead, 'industry', 'unknown'),
                    "employee_count": getattr(lead, 'employee_count', 0),
                    "monthly_ad_spend": getattr(lead, 'monthly_ad_spend', 0.0),
                    "performance_score": getattr(lead, 'performance_score', 0),
                    "qualification_score": getattr(lead, 'qualification_score', 0),
                    "urgency_level": getattr(lead, 'urgency_level', 'UNKNOWN'),
                    "estimated_monthly_loss": getattr(lead, 'estimated_monthly_loss', 0.0),
                    "specific_pain_points": getattr(lead, 'specific_pain_points', []),
                    "conversion_priority": getattr(lead, 'conversion_priority', 'STANDARD')
                }
                
                # Add ARCO-FIND specific analysis
                arco_analysis = await self._perform_arco_analysis(analyzed_lead)
                analyzed_lead.update(arco_analysis)
                
                analyzed_leads.append(analyzed_lead)
                
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to analyze lead: {e}")
                continue
        
        self.logger.info(f"✅ Analyzed {len(analyzed_leads)} real leads")
        return analyzed_leads
    
    async def _perform_arco_analysis(self, lead_data: dict) -> dict:
        """
        Perform ARCO-FIND specific analysis on real lead data
        """
        
        # Calculate ARCO-FIND metrics
        arco_metrics = {
            "arco_opportunity_score": self._calculate_arco_opportunity_score(lead_data),
            "cost_optimization_potential": self._calculate_cost_optimization(lead_data),
            "performance_improvement_value": self._calculate_performance_value(lead_data),
            "saas_efficiency_score": self._calculate_saas_efficiency(lead_data),
            "operational_automation_potential": self._calculate_automation_potential(lead_data)
        }
        
        # ARCO priority classification
        arco_priority = self._classify_arco_priority(arco_metrics, lead_data)
        
        # ARCO approach recommendation
        arco_approach = self._recommend_arco_approach(arco_metrics, lead_data)
        
        return {
            "arco_metrics": arco_metrics,
            "arco_priority_tier": arco_priority,
            "arco_recommended_approach": arco_approach,
            "arco_estimated_value": arco_metrics["cost_optimization_potential"] + arco_metrics["performance_improvement_value"],
            "arco_implementation_timeline": self._estimate_arco_timeline(arco_priority)
        }
    
    def _calculate_arco_opportunity_score(self, lead: dict) -> float:
        """Calculate ARCO opportunity score based on real data"""
        
        base_score = lead.get("qualification_score", 0) / 100.0
        
        # Boost for performance issues
        performance_boost = max(0, (100 - lead.get("performance_score", 100)) / 100.0) * 0.3
        
        # Boost for high ad spend (indicates budget)
        spend_boost = min(0.2, lead.get("monthly_ad_spend", 0) / 50000.0)
        
        # Company size in ARCO sweet spot
        size_boost = 0.1 if 15 <= lead.get("employee_count", 0) <= 75 else 0
        
        return min(1.0, base_score + performance_boost + spend_boost + size_boost)
    
    def _calculate_cost_optimization(self, lead: dict) -> float:
        """Calculate cost optimization potential"""
        
        # Base on ad spend and performance issues
        ad_spend = lead.get("monthly_ad_spend", 0)
        performance_score = lead.get("performance_score", 100)
        
        # Estimate waste based on poor performance
        performance_waste = ad_spend * (max(0, 100 - performance_score) / 100.0) * 0.4
        
        # SaaS optimization estimate (typical 20-30% savings)
        employee_count = lead.get("employee_count", 0)
        estimated_saas_spend = employee_count * 150  # $150/employee/month typical
        saas_optimization = estimated_saas_spend * 0.25
        
        return performance_waste + saas_optimization
    
    def _calculate_performance_value(self, lead: dict) -> float:
        """Calculate performance improvement value"""
        
        performance_score = lead.get("performance_score", 100)
        
        if performance_score < 50:
            # Critical performance issues - high value opportunity
            return lead.get("estimated_monthly_loss", 0) * 1.5
        elif performance_score < 70:
            # Moderate performance issues
            return lead.get("estimated_monthly_loss", 0) * 1.0
        else:
            # Minor performance issues
            return lead.get("estimated_monthly_loss", 0) * 0.5
    
    def _calculate_saas_efficiency(self, lead: dict) -> float:
        """Calculate SaaS efficiency score"""
        
        employee_count = lead.get("employee_count", 0)
        
        if employee_count >= 20:
            # Likely has SaaS stack inefficiencies
            return 0.7
        elif employee_count >= 10:
            # Some SaaS optimization potential
            return 0.5
        else:
            # Limited SaaS stack
            return 0.3
    
    def _calculate_automation_potential(self, lead: dict) -> float:
        """Calculate operational automation potential"""
        
        employee_count = lead.get("employee_count", 0)
        
        # Automation value scales with company size
        if employee_count >= 50:
            return employee_count * 200  # $200/employee automation value
        elif employee_count >= 20:
            return employee_count * 150
        else:
            return employee_count * 100
    
    def _classify_arco_priority(self, metrics: dict, lead: dict) -> str:
        """Classify ARCO priority tier"""
        
        opportunity_score = metrics["arco_opportunity_score"]
        total_value = metrics["cost_optimization_potential"] + metrics["performance_improvement_value"]
        
        if opportunity_score > 0.8 and total_value > 10000:
            return "S_TIER_IMMEDIATE"
        elif opportunity_score > 0.7 and total_value > 5000:
            return "A_TIER_HIGH_PRIORITY"
        elif opportunity_score > 0.6 and total_value > 2000:
            return "B_TIER_STANDARD"
        else:
            return "C_TIER_NURTURE"
    
    def _recommend_arco_approach(self, metrics: dict, lead: dict) -> str:
        """Recommend ARCO approach based on metrics"""
        
        cost_opt = metrics["cost_optimization_potential"]
        perf_value = metrics["performance_improvement_value"]
        saas_score = metrics["saas_efficiency_score"]
        
        if cost_opt > perf_value and saas_score > 0.6:
            return "COST_OPTIMIZATION_LEAD"
        elif perf_value > cost_opt * 1.5:
            return "PERFORMANCE_OPTIMIZATION_LEAD"
        elif saas_score > 0.7:
            return "SAAS_EFFICIENCY_LEAD"
        else:
            return "COMPREHENSIVE_ARCO_AUDIT"
    
    def _estimate_arco_timeline(self, priority: str) -> str:
        """Estimate ARCO implementation timeline"""
        
        timelines = {
            "S_TIER_IMMEDIATE": "2_WEEK_SPRINT",
            "A_TIER_HIGH_PRIORITY": "1_MONTH_PROGRAM",
            "B_TIER_STANDARD": "2_MONTH_PROGRAM",
            "C_TIER_NURTURE": "3_MONTH_PLANNING"
        }
        
        return timelines.get(priority, "STANDARD_PROGRAM")
    
    async def _generate_real_intelligence(self, analyzed_leads: list) -> dict:
        """Generate business intelligence from real lead data"""
        
        if not analyzed_leads:
            return {"error": "No leads to analyze"}
        
        # Aggregate metrics
        total_leads = len(analyzed_leads)
        total_opportunity_value = sum(lead.get("arco_estimated_value", 0) for lead in analyzed_leads)
        avg_qualification_score = sum(lead.get("qualification_score", 0) for lead in analyzed_leads) / total_leads
        
        # Priority distribution
        priority_dist = {}
        for lead in analyzed_leads:
            tier = lead.get("arco_priority_tier", "UNKNOWN")
            priority_dist[tier] = priority_dist.get(tier, 0) + 1
        
        # Industry analysis
        industry_analysis = {}
        for lead in analyzed_leads:
            industry = lead.get("industry", "unknown")
            if industry not in industry_analysis:
                industry_analysis[industry] = {
                    "count": 0,
                    "total_value": 0,
                    "avg_qualification": 0
                }
            industry_analysis[industry]["count"] += 1
            industry_analysis[industry]["total_value"] += lead.get("arco_estimated_value", 0)
            industry_analysis[industry]["avg_qualification"] += lead.get("qualification_score", 0)
        
        # Calculate averages
        for industry in industry_analysis:
            count = industry_analysis[industry]["count"]
            if count > 0:
                industry_analysis[industry]["avg_qualification"] /= count
        
        return {
            "summary": {
                "total_qualified_leads": total_leads,
                "total_opportunity_value": total_opportunity_value,
                "avg_qualification_score": avg_qualification_score,
                "priority_distribution": priority_dist
            },
            "industry_analysis": industry_analysis,
            "strategic_insights": self._generate_strategic_insights(analyzed_leads),
            "execution_recommendations": self._generate_execution_recommendations(analyzed_leads)
        }
    
    def _generate_strategic_insights(self, leads: list) -> list:
        """Generate strategic insights from real data"""
        
        insights = []
        
        # High-value opportunities
        s_tier_count = len([l for l in leads if l.get("arco_priority_tier") == "S_TIER_IMMEDIATE"])
        if s_tier_count > 0:
            insights.append(f"{s_tier_count} S-Tier immediate opportunities identified with high conversion potential")
        
        # Performance issues prevalence
        poor_performance_count = len([l for l in leads if l.get("performance_score", 100) < 60])
        if poor_performance_count > 0:
            insights.append(f"{poor_performance_count} companies have critical performance issues requiring immediate attention")
        
        # Cost optimization potential
        total_cost_savings = sum(l.get("arco_metrics", {}).get("cost_optimization_potential", 0) for l in leads)
        if total_cost_savings > 0:
            insights.append(f"${total_cost_savings:,.0f}/month total cost optimization opportunity identified")
        
        return insights
    
    def _generate_execution_recommendations(self, leads: list) -> list:
        """Generate execution recommendations"""
        
        recommendations = []
        
        # Immediate actions
        immediate_leads = [l for l in leads if l.get("arco_priority_tier") == "S_TIER_IMMEDIATE"]
        if immediate_leads:
            recommendations.append(f"Priority outreach to {len(immediate_leads)} S-Tier prospects within 48 hours")
        
        # Performance audit approach
        performance_leads = [l for l in leads if l.get("arco_recommended_approach") == "PERFORMANCE_OPTIMIZATION_LEAD"]
        if performance_leads:
            recommendations.append(f"Lead with performance audit for {len(performance_leads)} prospects showing critical site issues")
        
        # Cost optimization approach
        cost_leads = [l for l in leads if l.get("arco_recommended_approach") == "COST_OPTIMIZATION_LEAD"]
        if cost_leads:
            recommendations.append(f"Position cost optimization audit for {len(cost_leads)} prospects with high spend waste")
        
        return recommendations
    
    async def _create_actionable_report(self, intelligence: dict, leads: list) -> dict:
        """Create final actionable report"""
        
        timestamp = datetime.utcnow().isoformat()
        
        report = {
            "execution_summary": {
                "timestamp": timestamp,
                "pipeline_version": "ARCO_FIND_REAL_v1.0",
                "real_modules_used": self.real_modules,
                "execution_status": "SUCCESS"
            },
            "business_intelligence": intelligence,
            "qualified_prospects": [
                {
                    "prospect_id": f"ARCO_REAL_{i+1}_{int(datetime.utcnow().timestamp())}",
                    "company_name": lead.get("company_name", "Unknown"),
                    "website": lead.get("website", "unknown.com"),
                    "industry": lead.get("industry", "unknown"),
                    "qualification_score": lead.get("qualification_score", 0),
                    "arco_priority_tier": lead.get("arco_priority_tier", "C_TIER"),
                    "arco_estimated_value": lead.get("arco_estimated_value", 0),
                    "arco_recommended_approach": lead.get("arco_recommended_approach", "STANDARD"),
                    "implementation_timeline": lead.get("arco_implementation_timeline", "STANDARD"),
                    "urgency_level": lead.get("urgency_level", "MEDIUM"),
                    "discovery_method": "LeadQualificationEngine_Real"
                }
                for i, lead in enumerate(leads)
            ],
            "cost_tracking": cost_tracker.get_daily_summary(),
            "next_actions": intelligence.get("execution_recommendations", [])
        }
        
        # Export results
        await self._export_real_results(report)
        
        return report
    
    async def _export_real_results(self, report: dict):
        """Export real results"""
        
        exports_dir = Path("exports")
        exports_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Main report
        report_path = exports_dir / f"arco_real_execution_{timestamp}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📁 Real ARCO-FIND results exported to: {report_path}")
    
    async def _execute_fallback_demo(self) -> dict:
        """Fallback demo when real modules aren't available"""
        
        self.logger.info("🔄 Executing fallback demo mode")
        
        # Simulated results to show structure
        demo_results = {
            "execution_summary": {
                "timestamp": datetime.utcnow().isoformat(),
                "pipeline_version": "ARCO_FIND_DEMO_v1.0",
                "real_modules_used": False,
                "execution_status": "DEMO_MODE"
            },
            "business_intelligence": {
                "summary": {
                    "total_qualified_leads": 0,
                    "total_opportunity_value": 0,
                    "avg_qualification_score": 0,
                    "priority_distribution": {}
                },
                "strategic_insights": ["Demo mode - real modules not available"],
                "execution_recommendations": ["Set up BigQuery and SearchAPI for real execution"]
            },
            "qualified_prospects": [],
            "cost_tracking": {"total_cost": 0.0},
            "next_actions": ["Configure real ARCO-FIND modules for production use"]
        }
        
        return demo_results

async def main():
    """Main execution function"""
    
    print("🚀 ARCO-FIND REAL PIPELINE EXECUTOR")
    print("=" * 60)
    print("🎯 Using existing LeadQualificationEngine + BigQuery")
    print("📊 Real business intelligence generation")
    print("💰 Cost optimization and performance analysis")
    print("=" * 60)
    
    executor = ArcoFindRealExecutor()
    results = await executor.execute_real_pipeline()
    
    if results.get("execution_summary", {}).get("execution_status") != "DEMO_MODE":
        intelligence = results.get("business_intelligence", {})
        summary = intelligence.get("summary", {})
        
        print(f"\n🎯 REAL ARCO-FIND RESULTS:")
        print(f"✅ Qualified prospects: {summary.get('total_qualified_leads', 0)}")
        print(f"💰 Total opportunity value: ${summary.get('total_opportunity_value', 0):,.0f}")
        print(f"📊 Avg qualification score: {summary.get('avg_qualification_score', 0):.1f}")
        
        priorities = summary.get('priority_distribution', {})
        print(f"\n🏆 PRIORITY DISTRIBUTION:")
        for tier, count in priorities.items():
            print(f"   • {tier}: {count} prospect(s)")
        
        insights = intelligence.get('strategic_insights', [])
        print(f"\n💡 STRATEGIC INSIGHTS:")
        for insight in insights[:3]:
            print(f"   • {insight}")
        
        recommendations = intelligence.get('execution_recommendations', [])
        print(f"\n🎯 EXECUTION RECOMMENDATIONS:")
        for rec in recommendations[:3]:
            print(f"   • {rec}")
    else:
        print(f"\n⚠️ DEMO MODE EXECUTED")
        print("Set up BigQuery credentials and SearchAPI for real execution")
    
    print("\n" + "=" * 60)
    print("✅ ARCO-FIND Real Pipeline completed!")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
