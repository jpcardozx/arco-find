"""
Advanced Pipeline Implementation for ARCO.

This module contains the advanced pipeline implementation for the ARCO system,
which provides enhanced functionality for customer acquisition and analysis.
"""

import logging
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
import os
import time

from arco.pipelines.standard_pipeline import StandardPipeline
from arco.engines.leak_engine import LeakEngine
from arco.engines.discovery_engine import DiscoveryEngine
from arco.models.prospect import Prospect
from arco.models.qualified_prospect import QualifiedProspect
from arco.utils.logger import get_logger
from arco.config.settings import load_config

logger = get_logger(__name__)

class AdvancedPipeline(StandardPipeline):
    """
    Advanced pipeline implementation for ARCO.
    
    This pipeline extends the StandardPipeline with additional capabilities
    using more sophisticated engines for deeper analysis.
    """
    
    def __init__(self, config_path: str = "config/production.yml"):
        """
        Initialize the advanced pipeline.
        
        Args:
            config_path: Path to the configuration file.
        """
        super().__init__(config_path=config_path)
        logger.info(f"Initializing AdvancedPipeline with config: {config_path}")
        
        # Initialize additional engines
        self.leak_engine = LeakEngine(config_path=config_path)
        self.discovery_engine = DiscoveryEngine(config_path=config_path)
        
        # Advanced pipeline statistics
        self.stats.update({
            "enriched_count": 0,
            "high_value_prospects": 0,
            "average_authority_score": 0.0,
            "discovery_time": 0.0
        })
    
    def run(self, input_data: Any) -> List[QualifiedProspect]:
        """
        Run the advanced pipeline with the given input data.
        
        Args:
            input_data: Can be a list of domains, a path to a file with domains,
                       or a search query string
            
        Returns:
            List of qualified prospects
        """
        logger.info("Running advanced pipeline")
        
        # Reset statistics
        self._reset_stats()
        start_time = time.time()
        
        # Handle different input types
        if isinstance(input_data, str) and not os.path.exists(input_data):
            # Assume it's a search query
            logger.info(f"Processing search query: {input_data}")
            qualified_prospects = self._process_search_query(input_data)
        else:
            # Use standard pipeline processing for file or domain list
            qualified_prospects = super().run(input_data)
            
            # Enhance prospects with additional data
            qualified_prospects = self._enhance_prospects(qualified_prospects)
        
        # Update processing time
        self.stats["processing_time"] = time.time() - start_time
        
        logger.info(f"Advanced pipeline completed: {len(qualified_prospects)} qualified prospects")
        return qualified_prospects
    
    def process_prospect(self, prospect: Prospect) -> Optional[QualifiedProspect]:
        """
        Process a single prospect through the advanced pipeline.
        
        Args:
            prospect: The prospect to process
            
        Returns:
            Qualified prospect if successful, None otherwise
        """
        logger.info(f"Processing prospect with advanced pipeline: {prospect.domain}")
        self.stats["processed_count"] += 1
        
        try:
            # First enrich the prospect with additional data
            enriched_prospect = self.discovery_engine.enrich(prospect)
            self.stats["enriched_count"] += 1
            
            # Then use the more advanced leak engine for analysis
            leak_result = asyncio.run(self.leak_engine.analyze(enriched_prospect))
            
            # Skip if no significant waste found
            if leak_result.total_monthly_waste < self.config.get("min_monthly_waste", 60):
                logger.info(f"Skipping {prospect.domain}: Insufficient waste detected")
                return None
            
            # Qualify prospect using the advanced leak engine
            qualified = asyncio.run(self.leak_engine.qualify(enriched_prospect, leak_result))
            
            # Update statistics
            self.stats["qualified_count"] += 1
            self.stats["total_monthly_waste"] += qualified.monthly_waste
            self.stats["total_annual_savings"] += qualified.annual_savings
            
            # Track high-value prospects (A tier)
            if qualified.priority_tier == "A":
                self.stats["high_value_prospects"] += 1
            
            logger.info(f"Qualified {prospect.domain}: Score {qualified.qualification_score}/100, Tier {qualified.priority_tier}")
            return qualified
            
        except Exception as e:
            logger.error(f"Error processing {prospect.domain} with advanced pipeline: {e}")
            return None
    
    def save_results(self, qualified_prospects: List[QualifiedProspect], output_path: Optional[str] = None) -> str:
        """
        Save the advanced pipeline results to a file.
        
        Args:
            qualified_prospects: List of qualified prospects
            output_path: Path to the output file (optional)
            
        Returns:
            Path to the saved file
        """
        if not output_path:
            timestamp = asyncio.run(self._get_timestamp())
            output_path = f"output/advanced_results_{timestamp}.json"
        
        logger.info(f"Saving advanced results to: {output_path}")
        
        # Ensure the output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Calculate additional metrics
        if qualified_prospects:
            self.stats["average_authority_score"] = sum(
                getattr(p, "authority_score", 0) for p in qualified_prospects
            ) / len(qualified_prospects)
        
        # Prepare export data
        export_data = {
            "pipeline_type": "advanced",
            "stats": self.stats,
            "prospects": [prospect.to_dict() for prospect in qualified_prospects]
        }
        
        # Save results as JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        logger.info(f"Advanced results saved: {output_path}")
        return output_path
    
    def _process_search_query(self, query: str, limit: int = 20) -> List[QualifiedProspect]:
        """
        Process a search query to discover and qualify prospects.
        
        Args:
            query: Search query to find prospects
            limit: Maximum number of prospects to return
            
        Returns:
            List of qualified prospects
        """
        logger.info(f"Processing search query: {query}, limit: {limit}")
        discovery_start = time.time()
        
        # Discover prospects based on query
        discovered_prospects = self.discovery_engine.discover(query, limit=limit)
        
        # Update discovery time
        self.stats["discovery_time"] = time.time() - discovery_start
        
        logger.info(f"Discovered {len(discovered_prospects)} prospects from search query")
        
        # Process each discovered prospect
        qualified_prospects = []
        for prospect in discovered_prospects:
            qualified = self.process_prospect(prospect)
            if qualified:
                qualified_prospects.append(qualified)
        
        return qualified_prospects
    
    def _enhance_prospects(self, prospects: List[QualifiedProspect]) -> List[QualifiedProspect]:
        """
        Enhance prospects with additional data.
        
        Args:
            prospects: List of prospects to enhance
            
        Returns:
            Enhanced prospects
        """
        logger.info(f"Enhancing {len(prospects)} prospects with additional data")
        
        enhanced_prospects = []
        for prospect in prospects:
            try:
                # Enrich with additional data
                enriched = self.discovery_engine.enrich(prospect)
                
                # Re-analyze with the more advanced leak engine
                leak_result = asyncio.run(self.leak_engine.analyze(enriched))
                
                # Re-qualify with the more advanced leak engine
                requalified = asyncio.run(self.leak_engine.qualify(enriched, leak_result))
                
                enhanced_prospects.append(requalified)
                self.stats["enriched_count"] += 1
                
                # Track high-value prospects (A tier)
                if requalified.priority_tier == "A":
                    self.stats["high_value_prospects"] += 1
                
            except Exception as e:
                logger.error(f"Error enhancing prospect {prospect.domain}: {e}")
                # Keep the original prospect if enhancement fails
                enhanced_prospects.append(prospect)
        
        logger.info(f"Enhanced {self.stats['enriched_count']} prospects")
        return enhanced_prospects
    
    def _reset_stats(self) -> None:
        """Reset pipeline statistics."""
        super()._reset_stats()
        self.stats.update({
            "enriched_count": 0,
            "high_value_prospects": 0,
            "average_authority_score": 0.0,
            "discovery_time": 0.0
        })