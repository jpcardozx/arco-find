from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

# Enums from arco/domain/models.py
class LeadTemperature(Enum):
    """Lead temperature classification based on buying intent."""
    BLAZING = "BLAZING"  # 90+ score - Immediate action required
    HOT = "HOT"          # 70+ score - High priority outreach
    WARM = "WARM"        # 50+ score - Qualified outreach
    LUKEWARM = "LUKEWARM"  # 30+ score - Nurture sequence
    COLD = "COLD"        # <30 score - Low priority


class PriorityClassification(Enum):
    """Priority classification for CRM organization."""
    P0 = "P0"  # Top 5% - Immediate action
    P1 = "P1"  # Top 15% - High priority
    P2 = "P2"  # Top 35% - Qualified
    P3 = "P3"  # Remainder - Nurture


class BusinessModel(Enum):
    """Business model classification."""
    SAAS = "SaaS"
    ECOMMERCE = "E-commerce"
    SERVICE = "Service"
    ENTERPRISE = "Enterprise"
    PLATFORM = "Platform"
    UNKNOWN = "Unknown"


class CompanyScale(Enum):
    """Company scale classification."""
    STARTUP = "Startup"
    SMB = "SMB"
    ENTERPRISE = "Enterprise"
    MAJOR = "Major"


# Granular models from original arco/models/prospect.py
@dataclass
class Contact:
    """Contact information for a prospect."""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    linkedin: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "position": self.position,
            "linkedin": self.linkedin
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Contact':
        """Create from dictionary."""
        return cls(
            name=data.get("name", ""),
            email=data.get("email"),
            phone=data.get("phone"),
            position=data.get("position"),
            linkedin=data.get("linkedin")
        )

@dataclass
class Technology:
    """Technology information for a prospect."""
    name: str
    category: str
    version: Optional[str] = None
    monthly_cost: Optional[float] = None
    detection_confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "category": self.category,
            "version": self.version,
            "monthly_cost": self.monthly_cost,
            "detection_confidence": self.detection_confidence
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Technology':
        """Create from dictionary."""
        return cls(
            name=data.get("name", ""),
            category=data.get("category", ""),
            version=data.get("version"),
            monthly_cost=data.get("monthly_cost"),
            detection_confidence=data.get("detection_confidence", 0.0)
        )

@dataclass
class WebVitals:
    """Core Web Vitals data from real performance APIs."""
    lcp: Optional[float] = None  # Largest Contentful Paint (seconds)
    fid: Optional[float] = None  # First Input Delay (milliseconds)
    cls: Optional[float] = None  # Cumulative Layout Shift
    ttfb: Optional[float] = None  # Time to First Byte (milliseconds)
    fcp: Optional[float] = None  # First Contentful Paint (seconds)
    data_source: str = "unknown"  # crux, pagespeed, lighthouse
    collection_date: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "lcp": self.lcp,
            "fid": self.fid,
            "cls": self.cls,
            "ttfb": self.ttfb,
            "fcp": self.fcp,
            "data_source": self.data_source,
            "collection_date": self.collection_date.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebVitals':
        """Create from dictionary."""
        vitals = cls(
            lcp=data.get("lcp"),
            fid=data.get("fid"),
            cls=data.get("cls"),
            ttfb=data.get("ttfb"),
            fcp=data.get("fcp"),
            data_source=data.get("data_source", "unknown")
        )
        if "collection_date" in data:
            try:
                vitals.collection_date = datetime.fromisoformat(data["collection_date"])
            except (ValueError, TypeError):
                pass
        return vitals

@dataclass
class AdSpendData:
    """Real advertising spend data from Google Ads, Facebook Ads, etc."""
    monthly_spend: Optional[float] = None
    avg_cpc: Optional[float] = None
    avg_ctr: Optional[float] = None
    conversion_rate: Optional[float] = None
    cost_per_conversion: Optional[float] = None
    roas: Optional[float] = None  # Return on Ad Spend
    impressions: Optional[int] = None
    clicks: Optional[int] = None
    conversions: Optional[int] = None
    platform: str = "unknown"  # google_ads, facebook_ads, etc.
    data_confidence: float = 0.0
    collection_date: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "monthly_spend": self.monthly_spend,
            "avg_cpc": self.avg_cpc,
            "avg_ctr": self.avg_ctr,
            "conversion_rate": self.conversion_rate,
            "cost_per_conversion": self.cost_per_conversion,
            "roas": self.roas,
            "impressions": self.impressions,
            "clicks": self.clicks,
            "conversions": self.conversions,
            "platform": self.platform,
            "data_confidence": self.data_confidence,
            "collection_date": self.collection_date.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AdSpendData':
        """Create from dictionary."""
        ad_data = cls(
            monthly_spend=data.get("monthly_spend"),
            avg_cpc=data.get("avg_cpc"),
            avg_ctr=data.get("avg_ctr"),
            conversion_rate=data.get("conversion_rate"),
            cost_per_conversion=data.get("cost_per_conversion"),
            roas=data.get("roas"),
            impressions=data.get("impressions"),
            clicks=data.get("clicks"),
            conversions=data.get("conversions"),
            platform=data.get("platform", "unknown"),
            data_confidence=data.get("data_confidence", 0.0)
        )
        if "collection_date" in data:
            try:
                ad_data.collection_date = datetime.fromisoformat(data["collection_date"])
            except (ValueError, TypeError):
                pass
        return ad_data

@dataclass
class MarketingData:
    """Comprehensive marketing performance data for a prospect."""
    web_vitals: Optional[WebVitals] = None
    ad_spend: List[AdSpendData] = field(default_factory=list)
    bounce_rate: Optional[float] = None
    avg_session_duration: Optional[float] = None
    pages_per_session: Optional[float] = None
    organic_traffic_share: Optional[float] = None
    paid_traffic_share: Optional[float] = None
    monthly_visitors: Optional[int] = None
    conversion_rate: Optional[float] = None
    data_confidence: float = 0.0
    enrichment_phase: str = "basic"  # basic, advanced, complete
    collection_date: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "web_vitals": self.web_vitals.to_dict() if self.web_vitals else None,
            "ad_spend": [ad.to_dict() for ad in self.ad_spend],
            "bounce_rate": self.bounce_rate,
            "avg_session_duration": self.avg_session_duration,
            "pages_per_session": self.pages_per_session,
            "organic_traffic_share": self.organic_traffic_share,
            "paid_traffic_share": self.paid_traffic_share,
            "monthly_visitors": self.monthly_visitors,
            "conversion_rate": self.conversion_rate,
            "data_confidence": self.data_confidence,
            "enrichment_phase": self.enrichment_phase,
            "collection_date": self.collection_date.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MarketingData':
        """Create from dictionary."""
        marketing_data = cls(
            bounce_rate=data.get("bounce_rate"),
            avg_session_duration=data.get("avg_session_duration"),
            pages_per_session=data.get("pages_per_session"),
            organic_traffic_share=data.get("organic_traffic_share"),
            paid_traffic_share=data.get("paid_traffic_share"),
            monthly_visitors=data.get("monthly_visitors"),
            conversion_rate=data.get("conversion_rate"),
            data_confidence=data.get("data_confidence", 0.0),
            enrichment_phase=data.get("enrichment_phase", "basic")
        )
        if data.get("web_vitals"):
            marketing_data.web_vitals = WebVitals.from_dict(data["web_vitals"])
        for ad_data in data.get("ad_spend", []):
            marketing_data.ad_spend.append(AdSpendData.from_dict(ad_data))
        if "collection_date" in data:
            try:
                marketing_data.collection_date = datetime.fromisoformat(data["collection_date"])
            except (ValueError, TypeError):
                pass
        return marketing_data


# Nested dataclasses from arco/domain/models.py
@dataclass
class AdInvestmentProfile:
    """Ad investment analysis profile."""
    facebook_active: bool = False
    google_active: bool = False
    estimated_monthly_spend: int = 0
    sophistication_score: int = 0  # 0-100
    campaign_duration_months: int = 0
    ad_tech_detected: List[str] = field(default_factory=list)
    pixels_detected: List[str] = field(default_factory=list)


@dataclass
class FundingProfile:
    """Funding and investment profile."""
    recent_funding_months: Optional[int] = None
    funding_amount: Optional[int] = None
    funding_stage: Optional[str] = None
    total_funding: Optional[int] = None
    investors: List[str] = field(default_factory=list)
    funding_date: Optional[datetime] = None


@dataclass
class HiringActivity:
    """Hiring activity and growth signals."""
    total_job_postings: int = 0
    tech_job_postings: int = 0
    tech_leadership_hiring: int = 0
    recent_hires: int = 0
    growth_signal_score: int = 0  # 0-100
    key_positions: List[str] = field(default_factory=list)


@dataclass
class TechnologyInvestment:
    """Technology investment and modernization tracking."""
    recent_website_redesign: bool = False
    major_tech_project_active: bool = False
    new_integrations_detected: List[str] = field(default_factory=list)
    technology_modernization_score: int = 0  # 0-100
    stack_changes: List[str] = field(default_factory=list)
    last_major_update: Optional[datetime] = None


@dataclass
class BusinessIntelligence:
    """Comprehensive business intelligence from real sources."""
    ad_investment: AdInvestmentProfile = field(default_factory=AdInvestmentProfile)
    funding_profile: FundingProfile = field(default_factory=FundingProfile)
    hiring_activity: HiringActivity = field(default_factory=HiringActivity)
    technology_investment: TechnologyInvestment = field(default_factory=TechnologyInvestment)
    press_mentions_count: int = 0
    social_media_activity: int = 0
    partnership_announcements: int = 0
    product_launches: int = 0
    data_quality_score: float = 0.0  # 0.0-1.0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class TechnicalProfile:
    """Technical analysis profile with real performance data."""
    page_speed_score: int = 0  # 0-100
    core_web_vitals: Dict[str, float] = field(default_factory=dict)
    mobile_score: int = 0  # 0-100
    security_score: int = 0  # 0-100
    vulnerabilities_detected: List[str] = field(default_factory=list)
    ssl_grade: str = ""
    technologies_detected: List[str] = field(default_factory=list)
    cms_platform: Optional[str] = None
    hosting_provider: Optional[str] = None
    seo_score: int = 0  # 0-100
    accessibility_score: int = 0  # 0-100
    last_analyzed: datetime = field(default_factory=datetime.now)
    analysis_confidence: float = 0.0  # 0.0-1.0


@dataclass
class CompetitiveAnalysis:
    """Competitive analysis and market positioning."""
    market_position: str = ""  # Leader, Challenger, Follower, Niche
    competitive_threats: List[str] = field(default_factory=list)
    competitive_advantages: List[str] = field(default_factory=list)
    performance_vs_competitors: Dict[str, Any] = field(default_factory=dict)
    market_gaps: List[str] = field(default_factory=list)
    growth_opportunities: List[str] = field(default_factory=list)
    threat_level: str = "Low"  # Low, Medium, High
    competitors_analyzed: List[str] = field(default_factory=list)
    analysis_date: datetime = field(default_factory=datetime.now)


@dataclass
class LeadScore:
    """Comprehensive lead scoring with business justification."""
    total_score: int = 0  # 0-100
    temperature: LeadTemperature = LeadTemperature.COLD
    confidence_level: float = 0.0  # 0.0-1.0
    budget_verification_score: int = 0  # 0-40 (ads, funding, hiring)
    urgency_assessment_score: int = 0   # 0-30 (security, compliance, competition)
    project_timing_score: int = 0       # 0-20 (active projects, RFPs)
    decision_access_score: int = 0      # 0-10 (contact quality)
    scoring_rationale: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    opportunity_factors: List[str] = field(default_factory=list)
    recommended_approach: str = ""
    messaging_framework: str = ""
    calculated_at: datetime = field(default_factory=datetime.now)
    algorithm_version: str = "1.0"


@dataclass
class ActionableInsight:
    """Specific actionable business insight."""
    title: str
    description: str
    business_impact: str
    urgency_level: str  # Low, Medium, High, Critical
    category: str  # Technical, Competitive, Growth, Risk
    recommended_action: str
    expected_outcome: str
    implementation_effort: str  # Low, Medium, High
    supporting_evidence: List[str] = field(default_factory=list)
    confidence_score: float = 0.0  # 0.0-1.0
    generated_at: datetime = field(default_factory=datetime.now)
    insight_id: str = ""


@dataclass
class BusinessRecommendation:
    """Strategic business recommendation with ROI projections."""
    title: str
    description: str
    strategic_value: str
    estimated_roi: Optional[float] = None
    implementation_cost: Optional[int] = None
    time_to_value: str = ""  # e.g., "3-6 months"
    implementation_steps: List[str] = field(default_factory=list)
    success_metrics: List[str] = field(default_factory=list)
    risk_mitigation: List[str] = field(default_factory=list)
    recommendation_type: str = ""  # Technical, Strategic, Operational
    priority_level: str = "Medium"  # Low, Medium, High
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CRMProfile:
    """CRM organization and workflow profile."""
    priority_classification: PriorityClassification = PriorityClassification.P3
    workflow_type: str = ""  # Immediate, Qualified, Nurture
    primary_contact: Optional[str] = None
    contact_quality_score: int = 0  # 0-100
    decision_maker_access: bool = False
    recommended_timing: str = ""
    follow_up_sequence: List[str] = field(default_factory=list)
    messaging_strategy: str = ""
    crm_tags: List[str] = field(default_factory=list)
    pipeline_stage: str = "Prospect"
    next_action: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class Prospect:
    """Rich domain model with complete business intelligence."""
    # Core Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    company_name: str
    domain: str
    industry: str = ""
    employee_count: int = 0
    country: str = ""

    # Business classification
    business_model: BusinessModel = BusinessModel.UNKNOWN
    company_scale: CompanyScale = CompanyScale.STARTUP

    # Granular data from original Prospect
    technologies: List[Technology] = field(default_factory=list)
    contacts: List[Contact] = field(default_factory=list)
    marketing_data: Optional[MarketingData] = None

    # Business Intelligence
    business_intelligence: BusinessIntelligence = field(default_factory=BusinessIntelligence)
    technical_profile: TechnicalProfile = field(default_factory=TechnicalProfile)
    competitive_analysis: CompetitiveAnalysis = field(default_factory=CompetitiveAnalysis)

    # Scoring & Classification
    lead_score: LeadScore = field(default_factory=LeadScore)
    priority_classification: PriorityClassification = PriorityClassification.P3

    # Actionable Intelligence
    insights: List[ActionableInsight] = field(default_factory=list)
    recommendations: List[BusinessRecommendation] = field(default_factory=list)

    # CRM Integration
    crm_profile: CRMProfile = field(default_factory=CRMProfile)

    # Analysis Metadata
    last_analyzed: datetime = field(default_factory=datetime.now)
    confidence_level: float = 0.0  # 0.0-1.0
    analysis_version: str = "1.0"

    # Methods from original ComprehensiveProspect
    def calculate_partnership_potential(self) -> float:
        """Calculate strategic partnership potential score (0.0-1.0)."""
        score = 0.0
        if self.business_intelligence.ad_investment.facebook_active or \
           self.business_intelligence.ad_investment.google_active:
            score += 0.4
        if self.business_intelligence.hiring_activity.tech_job_postings > 0:
            score += 0.3
        if self.technical_profile.page_speed_score > 70:
            score += 0.2
        if self.competitive_analysis.market_position in ["Leader", "Challenger"]:
            score += 0.1
        return min(score, 1.0)

    def generate_proof_of_value(self) -> Dict[str, Any]:
        """Generate specific proof of value for this prospect."""
        return {
            "partnership_potential": self.calculate_partnership_potential(),
            "budget_indicators": {
                "ad_spend_detected": self.business_intelligence.ad_investment.estimated_monthly_spend > 0,
                "recent_funding": self.business_intelligence.funding_profile.recent_funding_months is not None,
                "tech_hiring": self.business_intelligence.hiring_activity.tech_job_postings > 0
            },
            "technical_opportunities": {
                "performance_score": self.technical_profile.page_speed_score,
                "security_score": self.technical_profile.security_score,
                "improvement_potential": 100 - max(self.technical_profile.page_speed_score, 0)
            },
            "competitive_position": {
                "market_position": self.competitive_analysis.market_position,
                "threat_level": self.competitive_analysis.threat_level,
                "growth_opportunities": len(self.competitive_analysis.growth_opportunities)
            }
        }

    def get_top_insights(self, limit: int = 3) -> List['ActionableInsight']:
        """Get top insights by confidence score and urgency."""
        sorted_insights = sorted(
            self.insights,
            key=lambda x: (x.confidence_score, x.urgency_level == "Critical", x.urgency_level == "High"),
            reverse=True
        )
        return sorted_insights[:limit]

    def is_hot_lead(self) -> bool:
        """Check if this is a hot lead (BLAZING or HOT temperature)."""
        return self.lead_score.temperature in [LeadTemperature.BLAZING, LeadTemperature.HOT]

    def get_budget_verification_signals(self) -> List[str]:
        """Get list of budget verification signals."""
        signals = []
        if self.business_intelligence.ad_investment.facebook_active:
            signals.append("Active Facebook advertising")
        if self.business_intelligence.ad_investment.google_active:
            signals.append("Active Google advertising")
        if self.business_intelligence.funding_profile.recent_funding_months:
            signals.append(f"Recent funding ({self.business_intelligence.funding_profile.recent_funding_months} months ago)")
        if self.business_intelligence.hiring_activity.tech_job_postings > 0:
            signals.append(f"Active tech hiring ({self.business_intelligence.hiring_activity.tech_job_postings} positions)")
        return signals

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "id": self.id,
            "company_name": self.company_name,
            "domain": self.domain,
            "industry": self.industry,
            "employee_count": self.employee_count,
            "country": self.country,
            "business_model": self.business_model.value,
            "company_scale": self.company_scale.value,
            "technologies": [tech.to_dict() for tech in self.technologies],
            "contacts": [contact.to_dict() for contact in self.contacts],
            "marketing_data": self.marketing_data.to_dict() if self.marketing_data else None,
            "business_intelligence": self.business_intelligence.to_dict(),
            "technical_profile": self.technical_profile.to_dict(),
            "competitive_analysis": self.competitive_analysis.to_dict(),
            "lead_score": self.lead_score.to_dict(),
            "priority_classification": self.priority_classification.value,
            "insights": [insight.to_dict() for insight in self.insights],
            "recommendations": [rec.to_dict() for rec in self.recommendations],
            "crm_profile": self.crm_profile.to_dict(),
            "last_analyzed": self.last_analyzed.isoformat(),
            "confidence_level": self.confidence_level,
            "analysis_version": self.analysis_version,
        }
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Prospect':
        # Handle Enums
        business_model = BusinessModel(data.get("business_model", BusinessModel.UNKNOWN.value))
        company_scale = CompanyScale(data.get("company_scale", CompanyScale.STARTUP.value))
        priority_classification = PriorityClassification(data.get("priority_classification", PriorityClassification.P3.value))

        # Handle nested dataclasses
        business_intelligence = BusinessIntelligence.from_dict(data.get("business_intelligence", {})) if data.get("business_intelligence") else BusinessIntelligence()
        technical_profile = TechnicalProfile.from_dict(data.get("technical_profile", {})) if data.get("technical_profile") else TechnicalProfile()
        competitive_analysis = CompetitiveAnalysis.from_dict(data.get("competitive_analysis", {})) if data.get("competitive_analysis") else CompetitiveAnalysis()
        lead_score = LeadScore.from_dict(data.get("lead_score", {})) if data.get("lead_score") else LeadScore()
        crm_profile = CRMProfile.from_dict(data.get("crm_profile", {})) if data.get("crm_profile") else CRMProfile()

        # Handle lists of dataclasses
        technologies = [Technology.from_dict(t) for t in data.get("technologies", [])]
        contacts = [Contact.from_dict(c) for c in data.get("contacts", [])]
        insights = [ActionableInsight.from_dict(i) for i in data.get("insights", [])]
        recommendations = [BusinessRecommendation.from_dict(r) for r in data.get("recommendations", [])]

        # Handle MarketingData
        marketing_data = MarketingData.from_dict(data["marketing_data"]) if data.get("marketing_data") else None

        prospect = cls(
            id=data.get("id", str(uuid.uuid4())),
            company_name=data.get("company_name", ""),
            domain=data.get("domain", ""),
            industry=data.get("industry", ""),
            employee_count=data.get("employee_count", 0),
            country=data.get("country", ""),
            business_model=business_model,
            company_scale=company_scale,
            technologies=technologies,
            contacts=contacts,
            marketing_data=marketing_data,
            business_intelligence=business_intelligence,
            technical_profile=technical_profile,
            competitive_analysis=competitive_analysis,
            lead_score=lead_score,
            priority_classification=priority_classification,
            insights=insights,
            recommendations=recommendations,
            crm_profile=crm_profile,
            confidence_level=data.get("confidence_level", 0.0),
            analysis_version=data.get("analysis_version", "1.0"),
        )
        if "last_analyzed" in data:
            try:
                prospect.last_analyzed = datetime.fromisoformat(data["last_analyzed"])
            except (ValueError, TypeError):
                pass
        return prospect
