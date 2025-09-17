"""
QualifiedProspect Model for ARCO.

This module contains the qualified prospect model implementation for the ARCO system,
which represents a fully qualified potential customer.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from .prospect import Prospect

@dataclass
class Leak:
    """Individual leak information."""
    
    type: str
    monthly_waste: float
    annual_savings: float
    description: str
    severity: str  # 'high', 'medium', 'low'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type,
            "monthly_waste": self.monthly_waste,
            "annual_savings": self.annual_savings,
            "description": self.description,
            "severity": self.severity
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Leak':
        """Create from dictionary."""
        return cls(
            type=data.get("type", ""),
            monthly_waste=data.get("monthly_waste", 0.0),
            annual_savings=data.get("annual_savings", 0.0),
            description=data.get("description", ""),
            severity=data.get("severity", "medium")
        )

@dataclass
class MarketingLeak(Leak):
    """Marketing-specific leak information with benchmarks and recommendations."""
    
    industry_benchmark: Optional[float] = None
    current_metric: Optional[float] = None
    improvement_potential: Optional[str] = None
    technical_recommendation: Optional[str] = None
    data_source: str = "unknown"  # google_analytics, pagespeed, crux, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        base_dict = super().to_dict()
        marketing_dict = {
            "industry_benchmark": self.industry_benchmark,
            "current_metric": self.current_metric,
            "improvement_potential": self.improvement_potential,
            "technical_recommendation": self.technical_recommendation,
            "data_source": self.data_source
        }
        return {**base_dict, **marketing_dict}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MarketingLeak':
        """Create from dictionary."""
        return cls(
            type=data.get("type", ""),
            monthly_waste=data.get("monthly_waste", 0.0),
            annual_savings=data.get("annual_savings", 0.0),
            description=data.get("description", ""),
            severity=data.get("severity", "medium"),
            industry_benchmark=data.get("industry_benchmark"),
            current_metric=data.get("current_metric"),
            improvement_potential=data.get("improvement_potential"),
            technical_recommendation=data.get("technical_recommendation"),
            data_source=data.get("data_source", "unknown")
        )

@dataclass
class QualifiedProspect(Prospect):
    """Qualified prospect model for ARCO."""
    
    # Discovery data (extends Prospect)
    estimated_revenue: Optional[float] = None
    
    # Leak detection data
    monthly_waste: float = 0.0
    annual_savings: float = 0.0
    leak_count: int = 0
    top_leaks: List[Leak] = field(default_factory=list)
    
    # Qualification
    qualification_score: int = 0  # 0-100
    priority_tier: str = "C"      # A, B, C
    outreach_ready: bool = False
    qualification_date: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        base_dict = super().to_dict()
        qualified_dict = {
            "estimated_revenue": self.estimated_revenue,
            "monthly_waste": self.monthly_waste,
            "annual_savings": self.annual_savings,
            "leak_count": self.leak_count,
            "top_leaks": [leak.to_dict() for leak in self.top_leaks],
            "qualification_score": self.qualification_score,
            "priority_tier": self.priority_tier,
            "outreach_ready": self.outreach_ready,
            "qualification_date": self.qualification_date.isoformat()
        }
        return {**base_dict, **qualified_dict}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QualifiedProspect':
        """Create from dictionary."""
        # First create the base Prospect
        prospect = Prospect.from_dict(data)
        
        # Then create the QualifiedProspect with the base prospect's attributes
        qualified = cls(
            domain=prospect.domain,
            company_name=prospect.company_name,
            website=prospect.website,
            description=prospect.description,
            industry=prospect.industry,
            employee_count=prospect.employee_count,
            revenue=prospect.revenue,
            country=prospect.country,
            city=prospect.city,
            technologies=prospect.technologies,
            contacts=prospect.contacts,
            marketing_data=prospect.marketing_data,
            discovery_date=prospect.discovery_date,
            validation_score=prospect.validation_score,
            leak_potential=prospect.leak_potential,
            
            # QualifiedProspect specific fields
            estimated_revenue=data.get("estimated_revenue"),
            monthly_waste=data.get("monthly_waste", 0.0),
            annual_savings=data.get("annual_savings", 0.0),
            leak_count=data.get("leak_count", 0),
            qualification_score=data.get("qualification_score", 0),
            priority_tier=data.get("priority_tier", "C"),
            outreach_ready=data.get("outreach_ready", False)
        )
        
        # Add top leaks
        for leak_data in data.get("top_leaks", []):
            qualified.top_leaks.append(Leak.from_dict(leak_data))
        
        # Parse qualification date
        if "qualification_date" in data:
            try:
                qualified.qualification_date = datetime.fromisoformat(data["qualification_date"])
            except (ValueError, TypeError):
                pass
        
        return qualified
    
    @classmethod
    def from_prospect(cls, prospect: Prospect) -> 'QualifiedProspect':
        """Create a QualifiedProspect from a Prospect."""
        return cls(
            domain=prospect.domain,
            company_name=prospect.company_name,
            website=prospect.website,
            description=prospect.description,
            industry=prospect.industry,
            employee_count=prospect.employee_count,
            revenue=prospect.revenue,
            country=prospect.country,
            city=prospect.city,
            technologies=prospect.technologies.copy(),
            contacts=prospect.contacts.copy(),
            marketing_data=prospect.marketing_data,
            discovery_date=prospect.discovery_date,
            validation_score=prospect.validation_score,
            leak_potential=prospect.leak_potential
        )