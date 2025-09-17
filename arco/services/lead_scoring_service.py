"""
Lead Scoring Service - Professional lead scoring with business justification.

This service implements enhanced lead scoring focused on budget verification,
urgency assessment, and buying intent indicators.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from arco.models.prospect import LeadScore, Prospect, LeadTemperature, PriorityClassification, BusinessModel, CompanyScale, ActionableInsight


class LeadScoringService:
    """
    Professional lead scoring with business justification.
    
    Implements enhanced scoring algorithm focused on:
    - Budget verification (40 points max)
    - Urgency assessment (30 points max) 
    - Project timing (20 points max)
    - Decision access (10 points max)
    """
    
    def __init__(self):
        """Initialize the lead scoring service."""
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def calculate_enhanced_score(self,
                                     company_name: str,
                                     business_model: BusinessModel,
                                     company_scale: CompanyScale,
                                     business_intelligence: BusinessIntelligence,
                                     technical_profile: Optional[TechnicalProfile] = None,
                                     competitive_analysis: Optional[CompetitiveAnalysis] = None) -> LeadScore:
        """
        Calculate comprehensive lead score with detailed breakdown.
        
        Args:
            company_name: Name of the company
            business_model: Business model classification
            company_scale: Company scale classification
            business_intelligence: Business intelligence data
            technical_profile: Technical analysis data
            competitive_analysis: Competitive analysis data
            
        Returns:
            LeadScore with detailed breakdown and justification
        """
        self._logger.debug(f"📊 Calculating enhanced lead score for {company_name}")
        
        # Calculate individual score components
        budget_score = self._calculate_budget_verification_score(business_intelligence)
        urgency_score = self._calculate_urgency_score(
            technical_profile, competitive_analysis, business_intelligence
        )
        timing_score = self._calculate_project_timing_score(business_intelligence)
        access_score = self._calculate_decision_access_score(business_intelligence)
        
        total_score = budget_score + urgency_score + timing_score + access_score
        
        # Calculate temperature and confidence
        temperature = self._calculate_enhanced_temperature(total_score)
        confidence = self._calculate_confidence(business_intelligence)
        
        # Generate scoring rationale
        rationale = self._generate_scoring_rationale(
            budget_score, urgency_score, timing_score, access_score,
            business_intelligence, technical_profile
        )
        
        # Generate risk and opportunity factors
        risk_factors = self._identify_risk_factors(
            business_intelligence, technical_profile, competitive_analysis
        )
        opportunity_factors = self._identify_opportunity_factors(
            business_intelligence, technical_profile, competitive_analysis
        )
        
        # Generate approach strategy
        approach_strategy = self._generate_approach_strategy(temperature, total_score)
        messaging_framework = self._generate_messaging_framework(
            temperature, business_intelligence, technical_profile
        )
        
        lead_score = LeadScore(
            total_score=total_score,
            temperature=temperature,
            confidence_level=confidence,
            budget_verification_score=budget_score,
            urgency_assessment_score=urgency_score,
            project_timing_score=timing_score,
            decision_access_score=access_score,
            scoring_rationale=rationale,
            risk_factors=risk_factors,
            opportunity_factors=opportunity_factors,
            recommended_approach=approach_strategy,
            messaging_framework=messaging_framework,
            calculated_at=datetime.now(),
            algorithm_version="2.0"
        )
        
        self._logger.info(
            f"🎯 Lead score for {company_name}: {total_score}/100 ({temperature.value}), "
            f"Budget: {budget_score}/40, Urgency: {urgency_score}/30, "
            f"Timing: {timing_score}/20, Access: {access_score}/10"
        )
        
        return lead_score
    
    def _calculate_budget_verification_score(self, business_intelligence: BusinessIntelligence) -> int:
        """
        Calculate budget verification score - most critical factor (0-40 points).
        
        This is the strongest indicator of buying intent and ability to purchase.
        """
        score = 0
        
        # Active Ad Campaigns (Strongest Budget Indicator) - 0-25 points
        ad_investment = business_intelligence.ad_investment
        
        if ad_investment.facebook_active and ad_investment.google_active:
            score += 25  # Multi-platform = confirmed significant budget
        elif ad_investment.facebook_active or ad_investment.google_active:
            score += 18  # Single platform = likely budget
        
        # Ad spend level bonus
        if ad_investment.estimated_monthly_spend >= 10000:
            score += 5  # High spend = substantial budget
        elif ad_investment.estimated_monthly_spend >= 5000:
            score += 3  # Medium spend = good budget
        elif ad_investment.estimated_monthly_spend >= 1000:
            score += 1  # Low spend = some budget
        
        # Recent Funding (Immediate Budget Availability) - 0-20 points
        funding = business_intelligence.funding_profile
        
        if funding.recent_funding_months:
            if funding.recent_funding_months <= 3:
                score += 20  # Very recent funding = immediate budget
            elif funding.recent_funding_months <= 6:
                score += 15  # Recent funding = likely budget
            elif funding.recent_funding_months <= 12:
                score += 10  # Funding within year = possible budget
        
        # Technology Leadership Hiring (Tech Budget Indicator) - 0-15 points
        hiring = business_intelligence.hiring_activity
        
        if hiring.tech_leadership_hiring >= 3:
            score += 15  # Major tech leadership hiring = significant tech budget
        elif hiring.tech_leadership_hiring >= 2:
            score += 10  # Multiple leadership hires = good tech budget
        elif hiring.tech_leadership_hiring >= 1:
            score += 5   # Single leadership hire = some tech budget
        
        # Technology Investment Signals - 0-10 points
        tech_investment = business_intelligence.technology_investment
        
        if tech_investment.major_tech_project_active:
            score += 5  # Active major project = allocated budget
        
        if tech_investment.recent_website_redesign:
            score += 3  # Recent redesign = tech investment
        
        if len(tech_investment.new_integrations_detected) >= 3:
            score += 2  # Multiple new integrations = ongoing tech investment
        
        return min(score, 40)
    
    def _calculate_urgency_score(self, 
                               technical_profile: Optional[TechnicalProfile],
                               competitive_analysis: Optional[CompetitiveAnalysis],
                               business_intelligence: BusinessIntelligence) -> int:
        """
        Calculate urgency assessment score (0-30 points).
        
        Urgency indicates how quickly they need to act.
        """
        score = 0
        
        # Security and Performance Issues (0-15 points)
        if technical_profile:
            if technical_profile.security_score < 50:
                score += 10  # Poor security = urgent need
            elif technical_profile.security_score < 70:
                score += 5   # Moderate security issues
            
            if technical_profile.page_speed_score < 50:
                score += 5   # Poor performance = urgent optimization need
            elif technical_profile.page_speed_score < 70:
                score += 3   # Moderate performance issues
        
        # Competitive Pressure (0-10 points)
        if competitive_analysis:
            if competitive_analysis.threat_level == "High":
                score += 10  # High competitive threat = urgent action needed
            elif competitive_analysis.threat_level == "Medium":
                score += 5   # Medium threat = some urgency
        
        # Growth Momentum Urgency (0-5 points)
        hiring = business_intelligence.hiring_activity
        
        if hiring.growth_signal_score >= 80:
            score += 5   # High growth = urgent scaling needs
        elif hiring.growth_signal_score >= 60:
            score += 3   # Medium growth = some urgency
        
        return min(score, 30)
    
    def _calculate_project_timing_score(self, business_intelligence: BusinessIntelligence) -> int:
        """
        Calculate project timing score (0-20 points).
        
        Active projects indicate immediate opportunity.
        """
        score = 0
        
        # Active Technology Projects (0-10 points)
        tech_investment = business_intelligence.technology_investment
        
        if tech_investment.major_tech_project_active:
            score += 10  # Major project = perfect timing
        elif tech_investment.recent_website_redesign:
            score += 6   # Recent redesign = good timing
        elif len(tech_investment.new_integrations_detected) > 0:
            score += 3   # New integrations = some project activity
        
        # Hiring Activity Timing (0-5 points)
        hiring = business_intelligence.hiring_activity
        
        if hiring.tech_job_postings >= 5:
            score += 5   # Heavy tech hiring = expansion phase
        elif hiring.tech_job_postings >= 2:
            score += 3   # Some tech hiring = growth phase
        elif hiring.tech_job_postings >= 1:
            score += 1   # Minimal hiring = stable phase
        
        # Funding Timing (0-5 points)
        funding = business_intelligence.funding_profile
        
        if funding.recent_funding_months and funding.recent_funding_months <= 6:
            score += 5   # Recent funding = investment phase
        elif funding.recent_funding_months and funding.recent_funding_months <= 12:
            score += 3   # Funding within year = possible investment phase
        
        return min(score, 20)
    
    def _calculate_decision_access_score(self, business_intelligence: BusinessIntelligence) -> int:
        """
        Calculate decision access score (0-10 points).
        
        Based on ability to reach decision makers.
        """
        score = 5  # Base score for any company
        
        # Leadership hiring indicates accessible leadership
        hiring = business_intelligence.hiring_activity
        
        if hiring.tech_leadership_hiring >= 2:
            score += 5   # Multiple leadership hires = accessible leadership
        elif hiring.tech_leadership_hiring >= 1:
            score += 3   # Some leadership hiring = somewhat accessible
        
        return min(score, 10)
    
    def _calculate_enhanced_temperature(self, score: int) -> LeadTemperature:
        """
        Calculate temperature with higher, more realistic thresholds.
        
        These thresholds are designed to identify truly qualified leads.
        """
        if score >= 90:
            return LeadTemperature.BLAZING  # Immediate action required
        elif score >= 70:
            return LeadTemperature.HOT      # High priority outreach
        elif score >= 50:
            return LeadTemperature.WARM     # Qualified outreach
        elif score >= 30:
            return LeadTemperature.LUKEWARM # Nurture sequence
        else:
            return LeadTemperature.COLD     # Low priority
    
    def _calculate_confidence(self, business_intelligence: BusinessIntelligence) -> float:
        """Calculate confidence level based on data quality."""
        return min(business_intelligence.data_quality_score, 1.0)
    
    def _generate_scoring_rationale(self, 
                                  budget_score: int,
                                  urgency_score: int, 
                                  timing_score: int,
                                  access_score: int,
                                  business_intelligence: BusinessIntelligence,
                                  technical_profile: Optional[TechnicalProfile]) -> List[str]:
        """Generate detailed scoring rationale."""
        rationale = []
        
        # Budget rationale
        if budget_score >= 30:
            rationale.append(f"Strong budget verification ({budget_score}/40 points)")
        elif budget_score >= 20:
            rationale.append(f"Good budget indicators ({budget_score}/40 points)")
        elif budget_score >= 10:
            rationale.append(f"Some budget signals ({budget_score}/40 points)")
        else:
            rationale.append(f"Limited budget verification ({budget_score}/40 points)")
        
        # Specific budget indicators
        ad_investment = business_intelligence.ad_investment
        if ad_investment.facebook_active or ad_investment.google_active:
            rationale.append(f"Active advertising campaigns (${ad_investment.estimated_monthly_spend:,}/month)")
        
        funding = business_intelligence.funding_profile
        if funding.recent_funding_months and funding.recent_funding_months <= 6:
            rationale.append(f"Recent funding ({funding.recent_funding_months} months ago)")
        
        hiring = business_intelligence.hiring_activity
        if hiring.tech_leadership_hiring > 0:
            rationale.append(f"Technology leadership hiring ({hiring.tech_leadership_hiring} positions)")
        
        # Urgency rationale
        if urgency_score >= 20:
            rationale.append(f"High urgency indicators ({urgency_score}/30 points)")
        elif urgency_score >= 10:
            rationale.append(f"Moderate urgency ({urgency_score}/30 points)")
        
        # Timing rationale
        if timing_score >= 15:
            rationale.append(f"Excellent project timing ({timing_score}/20 points)")
        elif timing_score >= 10:
            rationale.append(f"Good timing indicators ({timing_score}/20 points)")
        
        return rationale
    
    def _identify_risk_factors(self,
                             business_intelligence: BusinessIntelligence,
                             technical_profile: Optional[TechnicalProfile],
                             competitive_analysis: Optional[CompetitiveAnalysis]) -> List[str]:
        """Identify potential risk factors."""
        risks = []
        
        # Budget risks
        if business_intelligence.ad_investment.estimated_monthly_spend == 0:
            risks.append("No advertising spend detected - budget uncertainty")
        
        if not business_intelligence.funding_profile.recent_funding_months:
            risks.append("No recent funding - budget constraints possible")
        
        # Technical risks
        if technical_profile and technical_profile.security_score < 50:
            risks.append("Poor security posture - may indicate limited tech investment")
        
        # Competitive risks
        if competitive_analysis and competitive_analysis.threat_level == "Low":
            risks.append("Low competitive pressure - less urgency to act")
        
        return risks
    
    def _identify_opportunity_factors(self,
                                    business_intelligence: BusinessIntelligence,
                                    technical_profile: Optional[TechnicalProfile],
                                    competitive_analysis: Optional[CompetitiveAnalysis]) -> List[str]:
        """Identify opportunity factors."""
        opportunities = []
        
        # Budget opportunities
        if business_intelligence.ad_investment.estimated_monthly_spend >= 5000:
            opportunities.append("Significant ad spend indicates substantial marketing budget")
        
        if business_intelligence.funding_profile.recent_funding_months and business_intelligence.funding_profile.recent_funding_months <= 6:
            opportunities.append("Recent funding provides immediate budget availability")
        
        # Growth opportunities
        hiring = business_intelligence.hiring_activity
        if hiring.tech_job_postings >= 5:
            opportunities.append("Heavy tech hiring indicates rapid scaling")
        
        if hiring.tech_leadership_hiring >= 2:
            opportunities.append("Multiple leadership hires suggest major tech initiatives")
        
        # Technical opportunities
        if technical_profile and technical_profile.page_speed_score < 60:
            opportunities.append("Performance optimization opportunity with clear ROI")
        
        # Competitive opportunities
        if competitive_analysis and competitive_analysis.threat_level == "High":
            opportunities.append("High competitive pressure creates urgency for improvement")
        
        return opportunities
    
    def _generate_approach_strategy(self, temperature: LeadTemperature, score: int) -> str:
        """Generate approach strategy based on temperature and score."""
        if temperature == LeadTemperature.BLAZING:
            return "Immediate direct outreach with specific business impact focus and executive-level messaging"
        elif temperature == LeadTemperature.HOT:
            return "High-priority outreach with detailed value proposition and competitive analysis"
        elif temperature == LeadTemperature.WARM:
            return "Qualified outreach with educational content and proof of value demonstrations"
        elif temperature == LeadTemperature.LUKEWARM:
            return "Nurture sequence with valuable insights and gradual relationship building"
        else:
            return "Low-priority nurture with occasional valuable content and market updates"
    
    def _generate_messaging_framework(self,
                                    temperature: LeadTemperature,
                                    business_intelligence: BusinessIntelligence,
                                    technical_profile: Optional[TechnicalProfile]) -> str:
        """Generate messaging framework based on lead characteristics."""
        if temperature in [LeadTemperature.BLAZING, LeadTemperature.HOT]:
            # High-temperature leads get business impact messaging
            if business_intelligence.ad_investment.estimated_monthly_spend >= 5000:
                return "Budget-confirmed + competitive advantage messaging"
            elif business_intelligence.funding_profile.recent_funding_months and business_intelligence.funding_profile.recent_funding_months <= 6:
                return "Growth-phase + scaling efficiency messaging"
            else:
                return "Business impact + ROI-focused messaging"
        
        elif temperature == LeadTemperature.WARM:
            # Warm leads get educational messaging
            return "Educational + proof of value messaging"
        
        else:
            # Cool leads get nurture messaging
            return "Industry insights + thought leadership messaging"