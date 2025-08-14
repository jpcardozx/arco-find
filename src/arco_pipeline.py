"""
ARCO V3 Batch Pipeline Orchestrator
Coordinates all agents for automated lead generation and outreach
"""

import asyncio
import logging
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
import uuid

from .agents import (
    DiscoveryAgent, 
    PerformanceAgent, 
    ScoringAgent, 
    OutreachAgent,
    FollowupAgent,
    AnalyticsAgent
)
from .models.core_models import (
    BatchJobConfig, 
    ProcessingResult, 
    Vertical,
    ServiceFit
)

logger = logging.getLogger(__name__)


class ARCOPipeline:
    """
    Main pipeline orchestrator implementing the daily automation flow from AGENTS.md:
    06:00 - Discovery Phase
    07:00 - Performance Analysis  
    08:00 - Scoring & Prioritization
    09:00 - Outreach Generation
    18:00 - Analytics & Optimization
    """
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("data/executions")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize agents
        self.discovery_agent = None
        self.performance_agent = None
        self.scoring_agent = ScoringAgent()
        self.outreach_agent = OutreachAgent()
        self.followup_agent = FollowupAgent()
        self.analytics_agent = AnalyticsAgent()
    
    async def run_daily_pipeline(self, config: BatchJobConfig = None) -> ProcessingResult:
        """
        Execute the complete daily automation pipeline
        """
        config = config or BatchJobConfig()
        job_id = str(uuid.uuid4())
        start_time = datetime.now(timezone.utc)
        
        logger.info(f"🚀 Starting ARCO V3 daily pipeline - Job ID: {job_id}")
        logger.info(f"📊 Config: Max credits: {config.max_credits}, Target prospects: {config.target_prospects}")
        
        try:
            # Create job output directory
            job_dir = self.output_dir / job_id
            job_dir.mkdir(exist_ok=True)
            
            # 06:00 - Discovery Phase
            logger.info("🔍 Phase 1: Discovery")
            discovered_advertisers = await self._discovery_phase(config)
            self._save_results(job_dir / "leads_discovered.json", discovered_advertisers)
            
            if not discovered_advertisers:
                logger.warning("❌ No advertisers discovered - ending pipeline")
                return self._create_failed_result(job_id, start_time, "No advertisers discovered")
            
            # 07:00 - Performance Analysis
            logger.info("🚀 Phase 2: Performance Analysis")
            performance_results = await self._performance_phase(discovered_advertisers)
            self._save_results(job_dir / "performance_analysis.json", performance_results)
            
            # 08:00 - Scoring & Prioritization
            logger.info("🎯 Phase 3: Scoring & Prioritization")
            scored_prospects = await self._scoring_phase(discovered_advertisers, performance_results, config)
            self._save_results(job_dir / "leads_qualified.json", scored_prospects)
            
            if not scored_prospects:
                logger.warning("❌ No prospects qualified - check scoring criteria")
                return self._create_failed_result(job_id, start_time, "No prospects qualified")
            
            # 09:00 - Outreach Generation
            logger.info("📧 Phase 4: Outreach Generation")
            outreach_messages = await self._outreach_phase(scored_prospects)
            self._save_results(job_dir / "outreach_generated.json", outreach_messages)
            
            # Follow-up Scheduling
            logger.info("📅 Phase 5: Follow-up Scheduling")
            followup_records = await self._followup_phase(outreach_messages)
            self._save_results(job_dir / "followups_scheduled.json", followup_records)
            
            # 18:00 - Analytics & Optimization
            logger.info("📊 Phase 6: Analytics & Reporting")
            analytics_report = await self._analytics_phase(scored_prospects, outreach_messages)
            self._save_results(job_dir / "analytics_report.json", analytics_report)
            
            # Calculate credits used (simplified)
            credits_used = len(discovered_advertisers) * 3  # Rough estimate
            
            end_time = datetime.now(timezone.utc)
            result = ProcessingResult(
                job_id=job_id,
                start_time=start_time,
                end_time=end_time,
                config=config,
                prospects_discovered=len(discovered_advertisers),
                prospects_qualified=len(scored_prospects),
                outreach_generated=len(outreach_messages),
                credits_used=credits_used,
                success=True
            )
            
            self._save_results(job_dir / "processing_results.json", result)
            
            logger.info(f"✅ Pipeline completed successfully")
            logger.info(f"📊 Results: {len(discovered_advertisers)} discovered → {len(scored_prospects)} qualified → {len(outreach_messages)} outreach")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {str(e)}")
            return self._create_failed_result(job_id, start_time, str(e))
    
    async def _discovery_phase(self, config: BatchJobConfig) -> List:
        """Execute discovery phase"""
        async with DiscoveryAgent() as agent:
            self.discovery_agent = agent
            
            discoveries = await agent.run_daily_queries(
                vertical=config.vertical_focus,
                max_credits=config.max_credits // 2,  # Reserve half credits for discovery
                target_discoveries=config.target_prospects * 3  # Allow more discoveries for better filtering
            )
            
            logger.info(f"🔍 Discovery complete: {len(discoveries)} advertisers found")
            return discoveries
    
    async def _performance_phase(self, discovered_advertisers: List) -> List:
        """Execute performance analysis phase"""
        performance_results = []
        
        async with PerformanceAgent() as agent:
            self.performance_agent = agent
            
            for advertiser in discovered_advertisers:
                try:
                    result = await agent.analyze(advertiser.domain)
                    performance_results.append(result)
                    logger.debug(f"✅ Performance analyzed: {advertiser.domain}")
                except Exception as e:
                    logger.warning(f"❌ Performance analysis failed for {advertiser.domain}: {str(e)}")
        
        logger.info(f"🚀 Performance analysis complete: {len(performance_results)} domains analyzed")
        return performance_results
    
    async def _scoring_phase(self, discoveries: List, performances: List, config: BatchJobConfig) -> List:
        """Execute scoring and prioritization phase"""
        scored_prospects = self.scoring_agent.batch_score_prospects(discoveries, performances)
        logger.info(f"📊 Initial scoring results: {len(scored_prospects)} prospects qualified")
        
        # Apply filters
        initial_count = len(scored_prospects)
        
        if config.min_priority_score:
            scored_prospects = [p for p in scored_prospects if p.priority_score >= config.min_priority_score]
            logger.info(f"📊 After min_priority_score filter ({config.min_priority_score}): {len(scored_prospects)} prospects")

        if config.service_filters:
            scored_prospects = [p for p in scored_prospects if p.service_fit in config.service_filters]
            logger.info(f"📊 After service_filters: {len(scored_prospects)} prospects")

        # Limit to target count
        scored_prospects = scored_prospects[:config.target_prospects]
        logger.info(f"📊 After target limit ({config.target_prospects}): {len(scored_prospects)} prospects")

        logger.info(f"🎯 Scoring complete: {len(scored_prospects)} prospects qualified")
        return scored_prospects
    
    async def _outreach_phase(self, scored_prospects: List) -> List:
        """Execute outreach generation phase"""
        outreach_messages = []
        
        for prospect in scored_prospects:
            try:
                message = self.outreach_agent.generate_message(prospect)
                outreach_messages.append(message)
                logger.debug(f"📧 Outreach generated: {prospect.discovery_data.domain}")
            except Exception as e:
                logger.warning(f"❌ Outreach generation failed for {prospect.discovery_data.domain}: {str(e)}")
        
        logger.info(f"📧 Outreach generation complete: {len(outreach_messages)} messages created")
        return outreach_messages
    
    async def _followup_phase(self, outreach_messages: List) -> List:
        """Execute follow-up scheduling phase"""
        all_followups = []
        
        for message in outreach_messages:
            followups = self.followup_agent.schedule_followups(message)
            all_followups.extend(followups)
        
        logger.info(f"📅 Follow-up scheduling complete: {len(all_followups)} follow-ups scheduled")
        return all_followups
    
    async def _analytics_phase(self, prospects: List, outreach: List) -> dict:
        """Execute analytics and reporting phase"""
        report = self.analytics_agent.generate_daily_report(prospects, outreach)
        
        logger.info(f"📊 Analytics complete: {report.qualification_rate:.1%} qualification rate")
        return report
    
    def _save_results(self, filepath: Path, data) -> None:
        """Save results to JSON file"""
        try:
            if hasattr(data, '__dict__'):
                # Handle dataclass objects
                json_data = self._to_json_serializable(data)
            elif isinstance(data, list):
                # Handle list of objects
                json_data = [self._to_json_serializable(item) for item in data]
            else:
                json_data = data
            
            with open(filepath, 'w') as f:
                json.dump(json_data, f, indent=2, default=str)
                
            logger.debug(f"💾 Saved results to {filepath}")
        except Exception as e:
            logger.warning(f"❌ Failed to save results to {filepath}: {str(e)}")
    
    def _to_json_serializable(self, obj):
        """Convert object to JSON serializable format"""
        if hasattr(obj, '__dict__'):
            result = {}
            for key, value in obj.__dict__.items():
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif hasattr(value, '__dict__'):
                    result[key] = self._to_json_serializable(value)
                elif isinstance(value, list):
                    result[key] = [self._to_json_serializable(item) for item in value]
                elif isinstance(value, (ServiceFit, Vertical)):
                    result[key] = value.value
                else:
                    result[key] = value
            return result
        else:
            return obj
    
    def _create_failed_result(self, job_id: str, start_time: datetime, error: str) -> ProcessingResult:
        """Create failed processing result"""
        return ProcessingResult(
            job_id=job_id,
            start_time=start_time,
            end_time=datetime.now(timezone.utc),
            config=BatchJobConfig(),
            prospects_discovered=0,
            prospects_qualified=0,
            outreach_generated=0,
            credits_used=0,
            success=False,
            error_message=error
        )


# Convenience function for running pipeline
async def run_daily_batch(
    max_credits: int = 100,
    target_prospects: int = 12,
    vertical: Vertical = None,
    min_priority_score: int = 6  # Aligned with scoring agent threshold
) -> ProcessingResult:
    """
    Run daily batch processing with specified parameters
    """
    config = BatchJobConfig(
        max_credits=max_credits,
        target_prospects=target_prospects,
        vertical_focus=vertical,
        min_priority_score=min_priority_score
    )
    
    pipeline = ARCOPipeline()
    return await pipeline.run_daily_pipeline(config)


if __name__ == "__main__":
    # Example usage
    asyncio.run(run_daily_batch(
        max_credits=50,
        target_prospects=10,
        vertical=Vertical.HVAC_MULTI,
        min_priority_score=6  # Aligned with scoring agent threshold
    ))