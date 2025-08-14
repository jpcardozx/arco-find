"""
Core data models for ARCO V3 agent system
Based on AGENTS.md specifications
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum


class ServiceFit(Enum):
    """Service recommendations based on performance analysis"""
    CWV_RESCUE = "CWV_RESCUE"
    LP_EXPERIMENT = "LP_EXPERIMENT" 
    TRACKING_RELIABILITY = "TRACKING_RELIABILITY"


class Vertical(Enum):
    """Target verticals for lead generation"""
    HVAC_MULTI = "hvac_multi_location"
    URGENT_CARE = "urgent_care_express"
    DENTAL_CLINICS = "dental_clinics"
    MEDICAL_AESTHETICS = "medical_aesthetics"
    REAL_ESTATE = "real_estate_brokerages"
    AUTO_SERVICES = "auto_services"
    VETERINARY = "veterinary_pet_care"
    # Sunday-Active Verticals - Canada & EU Focus
    RESTAURANTS_CA = "restaurants_canada"
    HOTELS_EU = "hotels_europe"
    FITNESS_GYMS_CA = "fitness_gyms_canada"
    PHARMACIES_EU = "pharmacies_europe"
    GAS_STATIONS_CA = "gas_stations_canada"
    CONVENIENCE_EU = "convenience_stores_europe"
    EMERGENCY_SERVICES_CA = "emergency_services_canada"


@dataclass
class PSIMetrics:
    """PageSpeed Insights metrics"""
    lcp_p75: float  # Largest Contentful Paint
    inp_p75: float  # Interaction to Next Paint
    cls_p75: float  # Cumulative Layout Shift
    fcp_p75: float  # First Contentful Paint
    score: int      # Overall performance score
    device: str     # mobile or desktop


@dataclass
class DiscoveryOutput:
    """Output from Discovery Agent"""
    advertiser_id: str
    domain: str
    vertical: str
    currency: str
    last_seen: int
    creative_count: int
    demand_score: int  # 0-4
    fit_score: int     # 0-3
    discovery_timestamp: datetime
    company_name: Optional[str] = None
    city: Optional[str] = None
    geo_location: Optional[str] = None
    strategic_insights: Optional[Dict] = None  # Progressive disclosure insights


@dataclass 
class PerformanceOutput:
    """Output from Performance Agent"""
    domain: str
    analyzed_urls: List[str]
    performance_metrics: Dict[str, PSIMetrics]
    leak_indicators: List[str]
    leak_score: int  # 0-10
    evidence_screenshots: List[str]
    priority_fixes: List[str]
    estimated_impact: str  # "15-25% CVR improvement"
    analysis_timestamp: datetime
    

@dataclass
class ScoredProspect:
    """Output from Scoring Agent"""
    discovery_data: DiscoveryOutput
    performance_data: PerformanceOutput
    priority_score: int  # Combined total score
    service_fit: ServiceFit
    deal_size_range: Tuple[int, int]  # (min, max) USD
    estimated_monthly_loss: int
    confidence_level: float  # 0.0 to 1.0
    scoring_timestamp: datetime


@dataclass
class OutreachMessage:
    """Output from Outreach Agent"""
    prospect_id: str
    subject_line: str
    message_body: str
    evidence_package: str
    follow_up_sequence: List[str]
    personalization_score: float
    vertical_template: str
    primary_pain_point: str
    created_timestamp: datetime
    personalization_elements: Optional[Dict] = field(default_factory=dict)


@dataclass
class FollowupRecord:
    """Follow-up tracking record"""
    prospect_id: str
    sent_at: datetime
    responded: bool
    response_type: Optional[str]  # interested, not_interested, request_info
    next_followup_date: Optional[datetime]
    sequence_step: int
    

@dataclass
class AnalyticsReport:
    """Daily analytics report"""
    date: datetime
    prospects_discovered: int
    prospects_qualified: int
    outreach_sent: int
    responses_received: int
    audits_scheduled: int
    deals_closed: int
    response_rate: float
    qualification_rate: float
    revenue_generated: int
    optimization_recommendations: List[str]


@dataclass
class BatchJobConfig:
    """Configuration for batch processing jobs"""
    max_credits: int = 100
    target_prospects: int = 12
    vertical_focus: Optional[Vertical] = None
    geographic_focus: Optional[List[str]] = None
    min_priority_score: int = 6  # Aligned with scoring agent threshold
    service_filters: Optional[List[ServiceFit]] = None
    
    
@dataclass
class ProcessingResult:
    """Result of a batch processing job"""
    job_id: str
    start_time: datetime
    end_time: datetime
    config: BatchJobConfig
    prospects_discovered: int
    prospects_qualified: int
    outreach_generated: int
    credits_used: int
    success: bool
    error_message: Optional[str] = None