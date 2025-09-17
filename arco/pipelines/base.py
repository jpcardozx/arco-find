"""
Base Pipeline Interfaces for ARCO.

This module contains the abstract base classes that define the interfaces
for all pipeline implementations in the ARCO system.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from arco.models import Prospect, QualifiedProspect

class PipelineInterface(ABC):
    """Interface for all ARCO pipelines."""
    
    @abstractmethod
    def run(self, input_data: Any) -> List[QualifiedProspect]:
        """
        Run the pipeline with the given input data.
        
        Args:
            input_data: Input data for the pipeline (varies by implementation)
            
        Returns:
            List of qualified prospects
        """
        pass
    
    @abstractmethod
    def process_prospect(self, prospect: Prospect) -> Optional[QualifiedProspect]:
        """
        Process a single prospect through the pipeline.
        
        Args:
            prospect: The prospect to process
            
        Returns:
            Qualified prospect if successful, None otherwise
        """
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        Get pipeline execution statistics.
        
        Returns:
            Dictionary with pipeline statistics
        """
        pass