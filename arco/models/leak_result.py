"""
LeakResult Model for ARCO.

This module contains the leak result model implementation for the ARCO system,
which represents the results of leak detection analysis.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from .qualified_prospect import Leak

@dataclass
class LeakResult:
    """Result of leak detection analysis."""
    
    domain: str
    total_monthly_waste: float
    leaks: List[Leak] = field(default_factory=list)
    authority_score: float = 0.0
    has_ads: bool = False
    processing_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "domain": self.domain,
            "total_monthly_waste": self.total_monthly_waste,
            "leaks": [leak.to_dict() for leak in self.leaks],
            "authority_score": self.authority_score,
            "has_ads": self.has_ads,
            "processing_time": self.processing_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LeakResult':
        """Create from dictionary."""
        result = cls(
            domain=data.get("domain", ""),
            total_monthly_waste=data.get("total_monthly_waste", 0.0),
            authority_score=data.get("authority_score", 0.0),
            has_ads=data.get("has_ads", False),
            processing_time=data.get("processing_time", 0.0)
        )
        
        # Add leaks
        for leak_data in data.get("leaks", []):
            result.leaks.append(Leak.from_dict(leak_data))
        
        return result
    
    @property
    def annual_savings(self) -> float:
        """Calculate annual savings based on monthly waste."""
        return self.total_monthly_waste * 12
    
    @property
    def leak_count(self) -> int:
        """Get the number of leaks."""
        return len(self.leaks)
    
    @property
    def top_leaks(self) -> List[Leak]:
        """Get the top leaks sorted by monthly waste."""
        return sorted(self.leaks, key=lambda leak: leak.monthly_waste, reverse=True)