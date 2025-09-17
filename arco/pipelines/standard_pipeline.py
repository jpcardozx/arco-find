"""
Standard Pipeline Implementation for ARCO.

This module contains the standard pipeline implementation for the ARCO system,
which provides the basic functionality for customer acquisition and analysis.
"""

import logging
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
import os

from arco.pipelines.base import PipelineInterface
from arco.engines.simplified_engine import SimplifiedEngine
from arco.models.prospect import Prospect
from arco.models.qualified_prospect import QualifiedProspect
from arco.utils.logger import get_logger
from arco.config.settings import load_config

logger = get_logger(__name__)

class StandardPipeline(PipelineInterface):
    """
    Standard pipeline implementation for ARCO.
    
    This pipeline uses the SimplifiedEngine for basic prospect analysis
    without requiring external API integrations.
    """
    
    def __init__(self, config_path: str = "config/production.yml"):
        """
        Initialize the standard pipeline.
        
        Args:
            config_path: Path to the configuration file.
        """
        self.config_path = config_path
        self.config = load_config(config_path)
        logger.info(f"Initializing StandardPipeline with config: {config_path}")
        
        # Initialize engines
        self.simplified_engine = SimplifiedEngine()
        
        # Pipeline statistics
        self.stats = {
            "processed_count": 0,
            "qualified_count": 0,
            "total_monthly_waste": 0.0,
            "total_annual_savings": 0.0,
            "average_qualification_score": 0.0,
            "processing_time": 0.0
        }
    
    def run(self, input_data: Any) -> List[QualifiedProspect]:
        """
        Run the pipeline with the given input data.
        
        Args:
            input_data: Can be a list of domains or a path to a file with domains
            
        Returns:
            List of qualified prospects
        """
        logger.info("Running standard pipeline")
        
        # Reset statistics
        self._reset_stats()
        
        # Handle different input types
        domains = []
        if isinstance(input_data, str):
            # Assume it's a file path
            domains = self._load_domains(input_data)
        elif isinstance(input_data, list):
            # Assume it's a list of domains
            domains = input_data
        else:
            logger.error(f"Unsupported input type: {type(input_data)}")
            return []
        
        logger.info(f"Processing {len(domains)} domains")
        
        # Process domains
        qualified_prospects = []
        for domain in domains:
            # Create prospect
            prospect = Prospect(
                domain=domain,
                company_name=self._extract_company_name(domain)
            )
            
            # Process prospect
            qualified = self.process_prospect(prospect)
            if qualified:
                qualified_prospects.append(qualified)
                
                # Update statistics
                self.stats["qualified_count"] += 1
                self.stats["total_monthly_waste"] += qualified.monthly_waste
                self.stats["total_annual_savings"] += qualified.annual_savings
        
        # Calculate average qualification score
        if self.stats["qualified_count"] > 0:
            self.stats["average_qualification_score"] = sum(
                p.qualification_score for p in qualified_prospects
            ) / self.stats["qualified_count"]
        
        logger.info(f"Pipeline completed: {len(qualified_prospects)} qualified prospects")
        return qualified_prospects
    
    def process_prospect(self, prospect: Prospect) -> Optional[QualifiedProspect]:
        """
        Process a single prospect through the pipeline.
        
        Args:
            prospect: The prospect to process
            
        Returns:
            Qualified prospect if successful, None otherwise
        """
        logger.info(f"Processing prospect: {prospect.domain}")
        self.stats["processed_count"] += 1
        
        try:
            # Run leak analysis
            leak_result = asyncio.run(self.simplified_engine.analyze(prospect))
            
            # Skip if no significant waste found
            if leak_result.total_monthly_waste < self.config.get("min_monthly_waste", 40):
                logger.info(f"Skipping {prospect.domain}: Insufficient waste detected")
                return None
            
            # Qualify prospect
            qualified = asyncio.run(self.simplified_engine.qualify(prospect, leak_result))
            
            logger.info(f"Qualified {prospect.domain}: Score {qualified.qualification_score}/100, Tier {qualified.priority_tier}")
            return qualified
            
        except Exception as e:
            logger.error(f"Error processing {prospect.domain}: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get pipeline execution statistics.
        
        Returns:
            Dictionary with pipeline statistics
        """
        return self.stats
    
    def save_results(self, qualified_prospects: List[QualifiedProspect], output_path: Optional[str] = None) -> str:
        """
        Save the pipeline results to a file.
        
        Args:
            qualified_prospects: List of qualified prospects
            output_path: Path to the output file (optional)
            
        Returns:
            Path to the saved file
        """
        if not output_path:
            timestamp = asyncio.run(self._get_timestamp())
            output_path = f"output/standard_results_{timestamp}.json"
        
        logger.info(f"Saving results to: {output_path}")
        
        # Ensure the output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare export data
        export_data = {
            "pipeline_type": "standard",
            "stats": self.stats,
            "prospects": [prospect.to_dict() for prospect in qualified_prospects]
        }
        
        # Save results as JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        logger.info(f"Results saved: {output_path}")
        return output_path
    
    def run_from_file(self, input_file: str, output_file: Optional[str] = None) -> List[QualifiedProspect]:
        """
        Run the standard pipeline with domains from a file.
        
        Args:
            input_file: Path to the input file with domains
            output_file: Path to the output file (optional)
            
        Returns:
            List of qualified prospects
        """
        logger.info(f"Running standard pipeline with input file: {input_file}")
        
        # Run pipeline
        qualified_prospects = self.run(input_file)
        
        # Save results if output file specified
        if output_file:
            self.save_results(qualified_prospects, output_file)
        
        return qualified_prospects
    
    def _load_domains(self, input_file: str) -> List[str]:
        """
        Load domains from a file.
        
        Args:
            input_file: Path to the input file
            
        Returns:
            List of domains
        """
        logger.info(f"Loading domains from: {input_file}")
        
        domains = []
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                for line in f:
                    domain = line.strip()
                    if domain and not domain.startswith('#'):
                        domains.append(domain)
        except Exception as e:
            logger.error(f"Error loading domains from {input_file}: {e}")
            raise
        
        logger.info(f"Loaded {len(domains)} domains")
        return domains
    
    def _extract_company_name(self, domain: str) -> str:
        """Extract company name from domain."""
        name = domain.split('.')[0]
        return name.capitalize()
    
    async def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _reset_stats(self) -> None:
        """Reset pipeline statistics."""
        self.stats = {
            "processed_count": 0,
            "qualified_count": 0,
            "total_monthly_waste": 0.0,
            "total_annual_savings": 0.0,
            "average_qualification_score": 0.0,
            "processing_time": 0.0
        }