"""
Marketing Data Pipeline for ARCO.

Pipeline especializado para análise de marketing data dos prospects,
integrando Google Analytics, web vitals e traffic source analysis.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from arco.pipelines.advanced_pipeline import AdvancedPipeline
from arco.integrations.google_analytics import GoogleAnalyticsIntegration
from arco.models.prospect import Prospect, MarketingData, WebVitals
from arco.models.qualified_prospect import QualifiedProspect
from arco.utils.logger import get_logger

logger = get_logger(__name__)

class MarketingPipeline(AdvancedPipeline):
    """
    Pipeline especializado para análise de marketing data.
    
    Integra dados reais de performance web, traffic sources e conversion metrics
    para qualificação avançada de prospects.
    """
    
    def __init__(self, config_path: str = "config/production.yml", google_api_key: Optional[str] = None):
        """
        Initialize the marketing pipeline.
        
        Args:
            config_path: Path to the configuration file
            google_api_key: Google API key for PageSpeed Insights
        """
        super().__init__(config_path=config_path)
        logger.info("Initializing MarketingPipeline with Google Analytics integration")
        
        # Initialize Google Analytics integration
        self.ga_integration = GoogleAnalyticsIntegration(api_key=google_api_key)
        
        # Marketing pipeline statistics
        self.stats.update({
            "marketing_enriched": 0,
            "web_vitals_collected": 0,
            "traffic_sources_analyzed": 0,
            "conversion_metrics_estimated": 0,
            "performance_issues_detected": 0,
            "avg_lcp": 0.0,
            "avg_confidence_score": 0.0
        })
    
    async def process_prospect_async(self, prospect: Prospect) -> Optional[QualifiedProspect]:
        """
        Process a single prospect with marketing data enrichment.
        
        Args:
            prospect: The prospect to process
            
        Returns:
            Qualified prospect with marketing insights
        """
        logger.info(f"Processing prospect with marketing data: {prospect.domain}")
        self.stats["processed_count"] += 1
        
        try:
            # Enrich with marketing data
            enriched_prospect = await self._enrich_with_marketing_data(prospect)
            
            # Continue with standard advanced pipeline processing
            qualified = await self._process_with_leak_engine(enriched_prospect)
            
            if qualified:
                # Add marketing insights to qualification
                qualified = self._add_marketing_insights(qualified, enriched_prospect)
                
                self.stats["qualified_count"] += 1
                logger.info(f"Qualified {prospect.domain} with marketing insights")
                
            return qualified
            
        except Exception as e:
            logger.error(f"Error processing {prospect.domain} with marketing pipeline: {e}")
            return None
    
    def process_prospect(self, prospect: Prospect) -> Optional[QualifiedProspect]:
        """
        Synchronous wrapper for async prospect processing.
        
        Args:
            prospect: The prospect to process
            
        Returns:
            Qualified prospect with marketing insights
        """
        return asyncio.run(self.process_prospect_async(prospect))
    
    async def _enrich_with_marketing_data(self, prospect: Prospect) -> Prospect:
        """
        Enrich prospect with comprehensive marketing data.
        
        Args:
            prospect: Prospect to enrich
            
        Returns:
            Enriched prospect with marketing data
        """
        logger.info(f"Enriching {prospect.domain} with marketing data")
        
        # Initialize marketing data
        marketing_data = MarketingData()
        
        try:
            # Collect web vitals (PageSpeed Insights)
            web_vitals = await self.ga_integration.get_web_vitals(prospect.domain)
            if web_vitals:
                marketing_data.web_vitals = web_vitals
                self.stats["web_vitals_collected"] += 1
                
                # Track average LCP for statistics
                if web_vitals.lcp:
                    current_avg = self.stats["avg_lcp"]
                    count = self.stats["web_vitals_collected"]
                    self.stats["avg_lcp"] = ((current_avg * (count - 1)) + web_vitals.lcp) / count
                
                logger.info(f"Collected web vitals for {prospect.domain}: LCP={web_vitals.lcp}s")
            
            # Get conversion metrics (estimated from performance)
            conversion_metrics = await self.ga_integration.get_conversion_metrics(prospect.domain)
            if conversion_metrics:
                marketing_data.bounce_rate = conversion_metrics.get("bounce_rate")
                marketing_data.avg_session_duration = conversion_metrics.get("avg_session_duration")
                marketing_data.pages_per_session = conversion_metrics.get("pages_per_session")
                marketing_data.conversion_rate = conversion_metrics.get("conversion_rate")
                self.stats["conversion_metrics_estimated"] += 1
                
                logger.info(f"Estimated conversion metrics for {prospect.domain}: "
                          f"bounce_rate={marketing_data.bounce_rate:.3f}, "
                          f"conversion_rate={marketing_data.conversion_rate:.4f}")
            
            # Analyze traffic sources
            traffic_sources = await self.ga_integration.get_traffic_sources(prospect.domain)
            if traffic_sources:
                marketing_data.organic_traffic_share = traffic_sources.get("organic_search")
                marketing_data.paid_traffic_share = traffic_sources.get("paid_search")
                marketing_data.data_confidence = traffic_sources.get("confidence_score", 0.0)
                self.stats["traffic_sources_analyzed"] += 1
                
                # Track average confidence score
                current_avg = self.stats["avg_confidence_score"]
                count = self.stats["traffic_sources_analyzed"]
                self.stats["avg_confidence_score"] = ((current_avg * (count - 1)) + marketing_data.data_confidence) / count
                
                logger.info(f"Analyzed traffic sources for {prospect.domain}: "
                          f"organic={marketing_data.organic_traffic_share:.1%}, "
                          f"paid={marketing_data.paid_traffic_share:.1%}, "
                          f"confidence={marketing_data.data_confidence:.2f}")
            
            # Detect performance issues
            if self._has_performance_issues(marketing_data):
                self.stats["performance_issues_detected"] += 1
                logger.info(f"Performance issues detected for {prospect.domain}")
            
            # Set enrichment phase and collection date
            marketing_data.enrichment_phase = "advanced"
            marketing_data.collection_date = datetime.now()
            
            # Attach marketing data to prospect
            prospect.marketing_data = marketing_data
            self.stats["marketing_enriched"] += 1
            
        except Exception as e:
            logger.error(f"Error enriching {prospect.domain} with marketing data: {e}")
            # Set basic marketing data even if enrichment fails
            marketing_data.enrichment_phase = "failed"
            marketing_data.collection_date = datetime.now()
            prospect.marketing_data = marketing_data
        
        return prospect
    
    async def _process_with_leak_engine(self, prospect: Prospect) -> Optional[QualifiedProspect]:
        """
        Process prospect with leak engine analysis.
        
        Args:
            prospect: Enriched prospect
            
        Returns:
            Qualified prospect or None
        """
        try:
            # Analyze with leak engine
            leak_result = await self.leak_engine.analyze(prospect)
            
            # Skip if no significant waste found
            if leak_result.total_monthly_waste < self.config.get("min_monthly_waste", 60):
                logger.info(f"Skipping {prospect.domain}: Insufficient waste detected")
                return None
            
            # Qualify prospect
            qualified = await self.leak_engine.qualify(prospect, leak_result)
            
            # Update statistics
            self.stats["total_monthly_waste"] += qualified.monthly_waste
            self.stats["total_annual_savings"] += qualified.annual_savings
            
            return qualified
            
        except Exception as e:
            logger.error(f"Error processing {prospect.domain} with leak engine: {e}")
            return None
    
    def _add_marketing_insights(self, qualified: QualifiedProspect, prospect: Prospect) -> QualifiedProspect:
        """
        Add marketing insights to qualified prospect.
        
        Args:
            qualified: Qualified prospect
            prospect: Original prospect with marketing data
            
        Returns:
            Enhanced qualified prospect
        """
        if not prospect.marketing_data:
            return qualified
        
        marketing_data = prospect.marketing_data
        
        # Add marketing-specific insights to the qualification
        marketing_insights = []
        
        # Web performance insights
        if marketing_data.web_vitals and marketing_data.web_vitals.lcp:
            if marketing_data.web_vitals.lcp > 4.0:
                marketing_insights.append(f"Site muito lento (LCP: {marketing_data.web_vitals.lcp:.1f}s) - impacto direto nas conversões")
            elif marketing_data.web_vitals.lcp > 2.5:
                marketing_insights.append(f"Performance web abaixo do ideal (LCP: {marketing_data.web_vitals.lcp:.1f}s)")
        
        # Traffic source insights
        if marketing_data.organic_traffic_share and marketing_data.paid_traffic_share:
            organic_ratio = marketing_data.organic_traffic_share / (marketing_data.paid_traffic_share or 0.01)
            if organic_ratio < 1.0:
                marketing_insights.append(f"Dependência alta de tráfego pago ({marketing_data.paid_traffic_share:.1%} vs {marketing_data.organic_traffic_share:.1%} orgânico)")
            elif organic_ratio > 5.0:
                marketing_insights.append(f"Oportunidade de diversificar com tráfego pago (muito dependente de orgânico)")
        
        # Conversion insights
        if marketing_data.bounce_rate and marketing_data.bounce_rate > 0.7:
            marketing_insights.append(f"Taxa de rejeição alta ({marketing_data.bounce_rate:.1%}) - possível problema de UX")
        
        if marketing_data.conversion_rate and marketing_data.conversion_rate < 0.02:
            marketing_insights.append(f"Taxa de conversão baixa ({marketing_data.conversion_rate:.2%}) - oportunidade de otimização")
        
        # Add insights to qualified prospect
        if marketing_insights:
            if not hasattr(qualified, 'marketing_insights'):
                qualified.marketing_insights = []
            qualified.marketing_insights.extend(marketing_insights)
        
        return qualified
    
    def _has_performance_issues(self, marketing_data: MarketingData) -> bool:
        """
        Check if prospect has significant performance issues.
        
        Args:
            marketing_data: Marketing data to analyze
            
        Returns:
            True if performance issues detected
        """
        if not marketing_data.web_vitals:
            return False
        
        web_vitals = marketing_data.web_vitals
        
        # Check Core Web Vitals thresholds
        issues = []
        
        if web_vitals.lcp and web_vitals.lcp > 2.5:
            issues.append("LCP")
        
        if web_vitals.fid and web_vitals.fid > 100:
            issues.append("FID")
        
        if web_vitals.cls and web_vitals.cls > 0.1:
            issues.append("CLS")
        
        if web_vitals.ttfb and web_vitals.ttfb > 800:
            issues.append("TTFB")
        
        return len(issues) >= 2  # Consider it an issue if 2+ metrics are poor
    
    def save_results(self, qualified_prospects: List[QualifiedProspect], output_path: Optional[str] = None) -> str:
        """
        Save marketing pipeline results with enhanced statistics.
        
        Args:
            qualified_prospects: List of qualified prospects
            output_path: Path to the output file (optional)
            
        Returns:
            Path to the saved file
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"output/marketing_results_{timestamp}.json"
        
        logger.info(f"Saving marketing pipeline results to: {output_path}")
        
        # Ensure the output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare export data with marketing statistics
        export_data = {
            "pipeline_type": "marketing",
            "stats": self.stats,
            "marketing_summary": {
                "total_prospects_analyzed": self.stats["processed_count"],
                "marketing_data_collected": self.stats["marketing_enriched"],
                "web_vitals_success_rate": self.stats["web_vitals_collected"] / max(self.stats["processed_count"], 1),
                "avg_lcp_seconds": round(self.stats["avg_lcp"], 2),
                "avg_confidence_score": round(self.stats["avg_confidence_score"], 2),
                "performance_issues_rate": self.stats["performance_issues_detected"] / max(self.stats["processed_count"], 1)
            },
            "prospects": [prospect.to_dict() for prospect in qualified_prospects]
        }
        
        # Save results as JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str, ensure_ascii=False)
        
        # Also save a summary file
        summary_path = output_path.replace('.json', '_summary.json')
        summary_data = {
            "pipeline_type": "marketing",
            "execution_date": datetime.now().isoformat(),
            "stats": self.stats,
            "marketing_summary": export_data["marketing_summary"],
            "top_prospects": [
                {
                    "domain": p.domain,
                    "company_name": p.company_name,
                    "qualification_score": p.qualification_score,
                    "priority_tier": p.priority_tier,
                    "monthly_waste": p.monthly_waste,
                    "annual_savings": p.annual_savings,
                    "marketing_insights": getattr(p, 'marketing_insights', [])
                }
                for p in sorted(qualified_prospects, key=lambda x: x.qualification_score, reverse=True)[:10]
            ]
        }
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, default=str, ensure_ascii=False)
        
        logger.info(f"Marketing results saved: {output_path}")
        logger.info(f"Marketing summary saved: {summary_path}")
        
        return output_path
    
    async def close(self):
        """Close the pipeline and cleanup resources."""
        if self.ga_integration:
            await self.ga_integration.close()
        logger.info("MarketingPipeline closed")