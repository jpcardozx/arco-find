"""
ARCO Pipeline Orchestrator - Optimized Lead Generation & Qualification
Consolidated pipeline for Sunday-active verticals with strategic intelligence
"""

import asyncio
import logging
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import asdict

from src.agents.discovery_agent import DiscoveryAgent
from src.agents.scoring_agent import ScoringAgent  
from src.agents.outreach_agent import OutreachAgent
from src.agents.analytics_agent import AnalyticsAgent
from src.models.core_models import Vertical, DiscoveryOutput, ScoredProspect, OutreachMessage
from config.api_keys import APIConfig

logger = logging.getLogger(__name__)

class ARCOPipelineOrchestrator:
    """
    Optimized pipeline orchestrator for quantitative and qualitative lead generation
    """
    
    def __init__(self):
        self.search_api_key = APIConfig.SEARCH_API_KEY
        self.execution_id = None
        self.base_output_dir = Path("outputs")
        self.execution_dir = None
        
        # Initialize agents
        self.discovery_agent = None
        self.scoring_agent = ScoringAgent()
        self.outreach_agent = OutreachAgent()
        self.analytics_agent = AnalyticsAgent()
        
        # Performance tracking
        self.metrics = {
            "execution_start": None,
            "prospects_discovered": 0,
            "prospects_qualified": 0,
            "outreach_generated": 0,
            "credits_used": 0,
            "qualification_rate": 0.0,
            "verticals_processed": []
        }
    
    async def execute_sunday_vertical_discovery(self, 
                                              vertical: Vertical,
                                              max_credits: int = 20,
                                              target_prospects: int = 30) -> Dict:
        """
        Execute optimized discovery for Sunday-active verticals
        """
        self.execution_id = f"sunday_{vertical.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.execution_dir = self.base_output_dir / "pipeline_executions" / "2025-08" / "sunday_verticals" / self.execution_id
        self.execution_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🚀 Starting optimized Sunday vertical discovery: {vertical.value}")
        logger.info(f"📊 Execution ID: {self.execution_id}")
        logger.info(f"🎯 Target: {target_prospects} prospects, Max credits: {max_credits}")
        
        self.metrics["execution_start"] = datetime.now(timezone.utc)
        self.metrics["verticals_processed"].append(vertical.value)
        
        try:
            # Phase 1: Strategic Discovery
            logger.info("🔍 Phase 1: Strategic Discovery")
            discovered_prospects = await self._execute_discovery_phase(vertical, max_credits, target_prospects)
            
            # Phase 2: Qualification & Scoring
            logger.info("🎯 Phase 2: Qualification & Scoring")
            qualified_prospects = await self._execute_scoring_phase(discovered_prospects)
            
            # Phase 3: Strategic Outreach Generation
            logger.info("📧 Phase 3: Strategic Outreach Generation")
            outreach_messages = await self._execute_outreach_phase(qualified_prospects)
            
            # Phase 4: Analytics & Reporting
            logger.info("📊 Phase 4: Analytics & Performance Analysis")
            analytics_report = await self._execute_analytics_phase(
                discovered_prospects, qualified_prospects, outreach_messages
            )
            
            # Phase 5: Output Organization
            logger.info("💾 Phase 5: Output Organization & Export")
            execution_summary = await self._organize_outputs(
                discovered_prospects, qualified_prospects, outreach_messages, analytics_report
            )
            
            logger.info(f"✅ Pipeline execution completed successfully")
            logger.info(f"📈 Results: {len(discovered_prospects)} discovered → {len(qualified_prospects)} qualified → {len(outreach_messages)} outreach")
            
            return execution_summary
            
        except Exception as e:
            logger.error(f"❌ Pipeline execution failed: {e}")
            raise
        
        finally:
            if self.discovery_agent:
                await self.discovery_agent.__aexit__(None, None, None)
    
    async def _execute_discovery_phase(self, vertical: Vertical, max_credits: int, target_prospects: int) -> List[DiscoveryOutput]:
        """Execute optimized discovery with strategic intelligence"""
        
        # Initialize discovery agent with session
        self.discovery_agent = DiscoveryAgent(self.search_api_key)
        await self.discovery_agent.__aenter__()
        
        # Execute discovery with strategic vulnerability analysis
        discovered_prospects = await self.discovery_agent.run_daily_queries(
            vertical=vertical,
            max_credits=max_credits,
            target_discoveries=target_prospects
        )
        
        self.metrics["prospects_discovered"] = len(discovered_prospects)
        self.metrics["credits_used"] = max_credits  # Approximate, could be tracked more precisely
        
        logger.info(f"✅ Discovery completed: {len(discovered_prospects)} prospects discovered")
        
        # Save discovery results
        discovery_file = self.execution_dir / "leads_discovered.json"
        with open(discovery_file, 'w', encoding='utf-8') as f:
            json.dump([prospect.__dict__ for prospect in discovered_prospects], f, indent=2, ensure_ascii=False, default=str)
        
        return discovered_prospects
    
    async def _execute_scoring_phase(self, discovered_prospects: List[DiscoveryOutput]) -> List[ScoredProspect]:
        """Execute qualification and scoring with growth potential focus"""
        
        qualified_prospects = []
        
        for prospect in discovered_prospects:
            try:
                # Score prospect with growth potential analysis
                scored_prospect = self.scoring_agent.score_prospect(prospect)
                
                if scored_prospect and scored_prospect.priority_score >= 6:  # Qualification threshold
                    qualified_prospects.append(scored_prospect)
                    logger.info(f"✅ QUALIFIED: {prospect.domain} (score: {scored_prospect.priority_score})")
                else:
                    logger.info(f"❌ FILTERED: {prospect.domain} (score: {scored_prospect.priority_score if scored_prospect else 0})")
                    
            except Exception as e:
                logger.warning(f"⚠️ Scoring failed for {prospect.domain}: {e}")
                continue
        
        self.metrics["prospects_qualified"] = len(qualified_prospects)
        self.metrics["qualification_rate"] = len(qualified_prospects) / len(discovered_prospects) if discovered_prospects else 0
        
        logger.info(f"✅ Qualification completed: {len(qualified_prospects)} prospects qualified ({self.metrics['qualification_rate']:.1%} rate)")
        
        return qualified_prospects
    
    async def _execute_outreach_phase(self, qualified_prospects: List[ScoredProspect]) -> List[OutreachMessage]:
        """Execute strategic outreach generation with vulnerability insights"""
        
        outreach_messages = []
        
        for prospect in qualified_prospects:
            try:
                # Generate personalized outreach with strategic insights
                outreach_message = self.outreach_agent.generate_message(prospect)
                outreach_messages.append(outreach_message)
                
                logger.info(f"📧 Outreach generated for {prospect.discovery_data.domain}")
                logger.info(f"   📝 Subject: {outreach_message.subject_line}")
                logger.info(f"   🎯 Template: {outreach_message.vertical_template}")
                logger.info(f"   💯 Personalization: {outreach_message.personalization_score:.2f}")
                
            except Exception as e:
                logger.warning(f"⚠️ Outreach generation failed for {prospect.discovery_data.domain}: {e}")
                continue
        
        self.metrics["outreach_generated"] = len(outreach_messages)
        
        logger.info(f"✅ Outreach completed: {len(outreach_messages)} messages generated")
        
        # Save outreach results
        outreach_file = self.execution_dir / "outreach_generated.json"
        
        # DEBUG: Check what we're serializing
        for i, msg in enumerate(outreach_messages[:2]):  # Check first 2
            logger.info(f"🔍 MSG {i}: evidence_package='{msg.evidence_package}'")
            logger.info(f"🔍 MSG {i}: personalization_elements={msg.personalization_elements}")
        
        with open(outreach_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(msg) for msg in outreach_messages], f, indent=2, ensure_ascii=False, default=str)
        
        return outreach_messages
    
    async def _execute_analytics_phase(self, 
                                     discovered_prospects: List[DiscoveryOutput],
                                     qualified_prospects: List[ScoredProspect], 
                                     outreach_messages: List[OutreachMessage]) -> Dict:
        """Execute performance analytics and optimization recommendations"""
        
        # Generate analytics report
        analytics_report = self.analytics_agent.generate_performance_report(
            prospects_discovered=discovered_prospects,
            prospects_qualified=qualified_prospects,
            outreach_messages=outreach_messages,
            execution_id=self.execution_id
        )
        
        logger.info(f"📊 Analytics generated:")
        logger.info(f"   📈 Qualification rate: {analytics_report.get('qualification_rate', 0):.1%}")
        logger.info(f"   💼 Revenue generated: ${analytics_report.get('revenue_generated', 0)}")
        logger.info(f"   🎯 Optimization recommendations: {len(analytics_report.get('optimization_recommendations', []))}")
        
        # Save analytics report
        analytics_file = self.execution_dir / "analytics_report.json"
        with open(analytics_file, 'w', encoding='utf-8') as f:
            json.dump(analytics_report, f, indent=2, ensure_ascii=False, default=str)
        
        return analytics_report
    
    async def _organize_outputs(self, 
                              discovered_prospects: List[DiscoveryOutput],
                              qualified_prospects: List[ScoredProspect],
                              outreach_messages: List[OutreachMessage],
                              analytics_report: Dict) -> Dict:
        """Organize outputs in intelligent directory structure"""
        
        # Create organized output structure
        prospects_dir = self.base_output_dir / "prospects" / datetime.now().strftime("%Y-%m")
        outreach_dir = self.base_output_dir / "outreach" / datetime.now().strftime("%Y-%m") 
        analytics_dir = self.base_output_dir / "analytics" / datetime.now().strftime("%Y-%m")
        
        for dir_path in [prospects_dir, outreach_dir, analytics_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Export qualified prospects summary
        qualified_summary = {
            "execution_id": self.execution_id,
            "execution_date": datetime.now(timezone.utc).isoformat(),
            "vertical": qualified_prospects[0].discovery_data.vertical if qualified_prospects else None,
            "total_discovered": len(discovered_prospects),
            "total_qualified": len(qualified_prospects),
            "qualification_rate": len(qualified_prospects) / len(discovered_prospects) if discovered_prospects else 0,
            "qualified_prospects": [
                {
                    "domain": p.discovery_data.domain,
                    "company_name": p.discovery_data.company_name,
                    "priority_score": p.priority_score,
                    "strategic_tier": p.discovery_data.strategic_insights.get("tier") if p.discovery_data.strategic_insights else None,
                    "revenue_opportunity": p.discovery_data.strategic_insights.get("revenue_opportunity") if p.discovery_data.strategic_insights else None
                }
                for p in qualified_prospects
            ]
        }
        
        prospects_file = prospects_dir / f"qualified_prospects_{self.execution_id}.json"
        with open(prospects_file, 'w', encoding='utf-8') as f:
            json.dump(qualified_summary, f, indent=2, ensure_ascii=False, default=str)
        
        # Export outreach for CRM import
        outreach_export = [
            {
                "prospect_domain": msg.prospect_id.split('_')[0],
                "subject_line": msg.subject_line,
                "message_body": msg.message_body,
                "evidence_package": msg.evidence_package,
                "vertical_template": msg.vertical_template,
                "personalization_score": msg.personalization_score,
                "primary_pain_point": msg.primary_pain_point,
                "follow_up_sequence": msg.follow_up_sequence,
                "personalization_elements": msg.personalization_elements
            }
            for msg in outreach_messages
        ]
        
        outreach_file = outreach_dir / f"outreach_ready_{self.execution_id}.json"
        with open(outreach_file, 'w', encoding='utf-8') as f:
            json.dump(outreach_export, f, indent=2, ensure_ascii=False, default=str)
        
        # Export analytics dashboard data
        analytics_export = {
            "execution_id": self.execution_id,
            "execution_date": datetime.now(timezone.utc).isoformat(),
            "performance_metrics": analytics_report,
            "pipeline_efficiency": {
                "discovery_rate": len(discovered_prospects),
                "qualification_rate": analytics_report.get("qualification_rate", 0),
                "outreach_completion_rate": len(outreach_messages) / len(qualified_prospects) if qualified_prospects else 0
            },
            "optimization_focus": analytics_report.get("optimization_recommendations", [])
        }
        
        analytics_file = analytics_dir / f"performance_dashboard_{self.execution_id}.json"
        with open(analytics_file, 'w', encoding='utf-8') as f:
            json.dump(analytics_export, f, indent=2, ensure_ascii=False, default=str)
        
        # Create execution summary
        execution_summary = {
            "execution_id": self.execution_id,
            "execution_date": datetime.now(timezone.utc).isoformat(),
            "execution_duration": (datetime.now(timezone.utc) - self.metrics["execution_start"]).total_seconds(),
            "results": {
                "prospects_discovered": len(discovered_prospects),
                "prospects_qualified": len(qualified_prospects),
                "outreach_generated": len(outreach_messages),
                "qualification_rate": len(qualified_prospects) / len(discovered_prospects) if discovered_prospects else 0,
                "credits_used": self.metrics["credits_used"]
            },
            "outputs": {
                "execution_directory": str(self.execution_dir),
                "prospects_export": str(prospects_file),
                "outreach_export": str(outreach_file),
                "analytics_export": str(analytics_file)
            },
            "optimization_recommendations": analytics_report.get("optimization_recommendations", [])
        }
        
        # Save execution summary
        summary_file = self.execution_dir / "execution_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(execution_summary, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"💾 Outputs organized successfully:")
        logger.info(f"   📁 Execution dir: {self.execution_dir}")
        logger.info(f"   📊 Prospects: {prospects_file}")
        logger.info(f"   📧 Outreach: {outreach_file}")
        logger.info(f"   📈 Analytics: {analytics_file}")
        
        return execution_summary


async def execute_sunday_vertical_pipeline(vertical: Vertical, max_credits: int = 40, target_prospects: int = 25):
    """
    Execute optimized pipeline for Sunday-active vertical
    """
    orchestrator = ARCOPipelineOrchestrator()
    
    try:
        execution_summary = await orchestrator.execute_sunday_vertical_discovery(
            vertical=vertical,
            max_credits=max_credits, 
            target_prospects=target_prospects
        )
        
        print(f"\n[SUCCESS] Pipeline execution completed successfully!")
        print(f"[EXEC-ID] Execution ID: {execution_summary['execution_id']}")
        print(f"[RESULTS] Results: {execution_summary['results']}")
        print(f"[OUTPUTS] Outputs: {execution_summary['outputs']}")
        
        return execution_summary
        
    except Exception as e:
        print(f"[ERROR] Pipeline execution failed: {e}")
        raise


if __name__ == "__main__":
    import sys
    import os
    
    # Force UTF-8 encoding for Windows
    if os.name == 'nt':  # Windows
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example usage
    if len(sys.argv) > 1:
        vertical_name = sys.argv[1]
        try:
            vertical = Vertical(vertical_name)
            asyncio.run(execute_sunday_vertical_pipeline(vertical))
        except ValueError:
            print(f"[ERROR] Invalid vertical: {vertical_name}")
            print(f"[INFO] Available verticals: {[v.value for v in Vertical]}")
    else:
        # Default: execute fitness_gyms_canada
        asyncio.run(execute_sunday_vertical_pipeline(Vertical.FITNESS_GYMS_CA))
