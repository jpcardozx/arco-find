"""
Base Engine Interfaces for ARCO.

This module contains the abstract base classes that define the interfaces
for all engine implementations in the ARCO system.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from arco.models import Prospect, QualifiedProspect, LeakResult

class DiscoveryEngineInterface(ABC):
    """Interface for discovery engines that find prospects."""
    
    @abstractmethod
    def discover(self, query: str, limit: int = 10) -> List[Prospect]:
        """
        Discover prospects based on search query.
        
        Args:
            query: Search query to find prospects
            limit: Maximum number of prospects to return
            
        Returns:
            List of discovered prospects
        """
        pass
    
    @abstractmethod
    def enrich(self, prospect: Prospect) -> Prospect:
        """
        Enrich a prospect with additional information.
        
        Args:
            prospect: The prospect to enrich
            
        Returns:
            Enriched prospect
        """
        pass


class ValidatorEngineInterface(ABC):
    """Interface for validator engines that validate prospects."""
    
    @abstractmethod
    def validate(self, prospect: Prospect) -> Prospect:
        """
        Validate a prospect and update its validation score.
        
        Args:
            prospect: The prospect to validate
            
        Returns:
            Validated prospect with updated validation score
        """
        pass
    
    @abstractmethod
    def batch_validate(self, prospects: List[Prospect]) -> List[Prospect]:
        """
        Validate multiple prospects in batch.
        
        Args:
            prospects: List of prospects to validate
            
        Returns:
            List of validated prospects with updated validation scores
        """
        pass


class LeakEngineInterface(ABC):
    """Interface for leak engines that detect revenue leaks."""
    
    @abstractmethod
    def analyze(self, prospect: Prospect) -> LeakResult:
        """
        Analyze a prospect for potential revenue leaks.
        
        Args:
            prospect: The prospect to analyze
            
        Returns:
            Leak analysis result
        """
        pass
    
    @abstractmethod
    def qualify(self, prospect: Prospect, leak_result: LeakResult) -> QualifiedProspect:
        """
        Qualify a prospect based on leak analysis.
        
        Args:
            prospect: The prospect to qualify
            leak_result: Leak analysis result
            
        Returns:
            Qualified prospect
        """
        pass