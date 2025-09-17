"""
Business Intelligence Service - Collects and analyzes real business intelligence data.

This service implements the BusinessIntelligenceService from the design document,
collecting real data from multiple sources to replace fake calculations.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from arco.models.prospect import BusinessIntelligence, AdInvestmentProfile, FundingProfile, HiringActivity, TechnologyInvestment, Prospect
from arco.integrations.ad_intelligence_collector import AdIntelligenceCollector
from arco.integrations.funding_intelligence_collector import FundingIntelligenceCollector
from arco.integrations.hiring_intelligence_collector import HiringIntelligenceCollector
from arco.integrations.technology_intelligence_collector import TechnologyIntelligenceCollector
from arco.core.error_handler import ProcessingErrorHandler, RetryConfig, CircuitBreakerConfig


class BusinessIntelligenceService:
    """
    Collects and analyzes real business intelligence data.
    
    This service coordinates multiple intelligence collectors to gather
    comprehensive business data about prospects, focusing on budget
    verification and growth signals.
    """
    
    def __init__(self,
                 ad_intelligence_collector: AdIntelligenceCollector,
                 funding_intelligence_collector: FundingIntelligenceCollector,
                 hiring_intelligence_collector: HiringIntelligenceCollector,
                 technology_intelligence_collector: TechnologyIntelligenceCollector,
                 error_handler: Optional[ProcessingErrorHandler] = None):
        """
        Initialize the business intelligence service.
        
        Args:
            ad_intelligence_collector: Collector for advertising intelligence
            funding_intelligence_collector: Collector for funding intelligence
            hiring_intelligence_collector: Collector for hiring intelligence
            technology_intelligence_collector: Collector for technology intelligence
            error_handler: Error handler for robust API interactions
        """
        self.ad_intelligence_collector = ad_intelligence_collector
        self.funding_intelligence_collector = funding_intelligence_collector
        self.hiring_intelligence_collector = hiring_intelligence_collector
        self.technology_intelligence_collector = technology_intelligence_collector
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize error handler with business intelligence specific configuration
        self.error_handler = error_handler or ProcessingErrorHandler(
            retry_config=RetryConfig(
                max_retries=3,
                initial_delay=1.0,
                backoff_factor=2.0,
                max_delay=30.0
            ),
            circuit_breaker_config=CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60.0
            )
        )
    
    async def collect_intelligence(self, prospect_domain: str, company_name: str) -> BusinessIntelligence:
        """
        Collect comprehensive business intelligence from real sources with robust error handling.
        
        Args:
            prospect_domain: Domain of the prospect company
            company_name: Name of the prospect company
            
        Returns:
            BusinessIntelligence object with collected data
        """
        self._logger.info(f"🔍 Collecting business intelligence for {company_name}")
        
        # Collect intelligence data with error handling for each collector
        ad_investment = await self._collect_ad_intelligence_safely(prospect_domain, company_name)
        funding_profile = await self._collect_funding_intelligence_safely(company_name)
        hiring_activity = await self._collect_hiring_intelligence_safely(company_name)
        technology_investment = await self._collect_technology_intelligence_safely(prospect_domain)
        
        # Calculate data quality score
        data_quality_score = self._calculate_data_quality_score(
            ad_investment, funding_profile, hiring_activity, technology_investment
        )
        
        business_intelligence = BusinessIntelligence(
            ad_investment=ad_investment,
            funding_profile=funding_profile,
            hiring_activity=hiring_activity,
            technology_investment=technology_investment,
            data_quality_score=data_quality_score,
            last_updated=datetime.now()
        )
        
        self._logger.info(
            f"✅ Collected intelligence for {company_name}: "
            f"Quality Score: {data_quality_score:.2f}, "
            f"Ad Active: {'✓' if ad_investment.facebook_active or ad_investment.google_active else '✗'}, "
            f"Recent Funding: {'✓' if funding_profile.recent_funding_months else '✗'}, "
            f"Tech Hiring: {hiring_activity.tech_job_postings}"
        )
        
        return business_intelligence
    
    async def _collect_ad_intelligence_safely(self, prospect_domain: str, company_name: str) -> AdInvestmentProfile:
        """Collect ad intelligence with comprehensive error handling."""
        try:
            return await self.error_handler.process_with_retry(
                self.ad_intelligence_collector.collect,
                "collect_ad_intelligence",
                "ad_intelligence_service",
                prospect_domain,
                company_name
            )
        except Exception as e:
            self._logger.warning(f"⚠️ Ad intelligence collection failed for {company_name}: {e}")
            return AdInvestmentProfile()
    
    async def _collect_funding_intelligence_safely(self, company_name: str) -> FundingProfile:
        """Collect funding intelligence with comprehensive error handling."""
        try:
            return await self.error_handler.process_with_retry(
                self.funding_intelligence_collector.collect,
                "collect_funding_intelligence",
                "funding_intelligence_service",
                company_name
            )
        except Exception as e:
            self._logger.warning(f"⚠️ Funding intelligence collection failed for {company_name}: {e}")
            return FundingProfile()
    
    async def _collect_hiring_intelligence_safely(self, company_name: str) -> HiringActivity:
        """Collect hiring intelligence with comprehensive error handling."""
        try:
            return await self.error_handler.process_with_retry(
                self.hiring_intelligence_collector.collect,
                "collect_hiring_intelligence",
                "hiring_intelligence_service",
                company_name
            )
        except Exception as e:
            self._logger.warning(f"⚠️ Hiring intelligence collection failed for {company_name}: {e}")
            return HiringActivity()
    
    async def _collect_technology_intelligence_safely(self, prospect_domain: str) -> TechnologyInvestment:
        """Collect technology intelligence with comprehensive error handling."""
        try:
            return await self.error_handler.process_with_retry(
                self.technology_intelligence_collector.collect,
                "collect_technology_intelligence",
                "technology_intelligence_service",
                prospect_domain
            )
        except Exception as e:
            self._logger.warning(f"⚠️ Technology intelligence collection failed for {prospect_domain}: {e}")
            return TechnologyInvestment()
    
    def _calculate_data_quality_score(self, 
                                    ad_investment: AdInvestmentProfile,
                                    funding_profile: FundingProfile,
                                    hiring_activity: HiringActivity,
                                    technology_investment: TechnologyInvestment) -> float:
        """
        Calculate data quality score based on available intelligence.
        
        Args:
            ad_investment: Ad investment profile
            funding_profile: Funding profile
            hiring_activity: Hiring activity
            technology_investment: Technology investment
            
        Returns:
            Data quality score (0.0-1.0)
        """
        score = 0.0
        
        # Ad intelligence (30% weight)
        if ad_investment.facebook_active or ad_investment.google_active:
            score += 0.3
        elif ad_investment.estimated_monthly_spend > 0:
            score += 0.15
        
        # Funding intelligence (25% weight)
        if funding_profile.recent_funding_months is not None:
            score += 0.25
        elif funding_profile.total_funding is not None:
            score += 0.1
        
        # Hiring intelligence (25% weight)
        if hiring_activity.tech_job_postings > 0:
            score += 0.25
        elif hiring_activity.total_job_postings > 0:
            score += 0.1
        
        # Technology intelligence (20% weight)
        if technology_investment.recent_website_redesign or technology_investment.major_tech_project_active:
            score += 0.2
        elif len(technology_investment.new_integrations_detected) > 0:
            score += 0.1
        
        return min(score, 1.0)
    
    async def get_budget_verification_signals(self, business_intelligence: BusinessIntelligence) -> List[str]:
        """
        Extract budget verification signals from business intelligence.
        
        Args:
            business_intelligence: Business intelligence data
            
        Returns:
            List of budget verification signals
        """
        signals = []
        
        # Ad investment signals (strongest budget indicators)
        if business_intelligence.ad_investment.facebook_active:
            signals.append(f"Active Facebook advertising (${business_intelligence.ad_investment.estimated_monthly_spend:,}/month)")
        
        if business_intelligence.ad_investment.google_active:
            signals.append(f"Active Google advertising")
        
        # Funding signals (immediate budget availability)
        if business_intelligence.funding_profile.recent_funding_months:
            if business_intelligence.funding_profile.recent_funding_months <= 6:
                signals.append(f"Recent funding ({business_intelligence.funding_profile.recent_funding_months} months ago)")
            elif business_intelligence.funding_profile.recent_funding_months <= 12:
                signals.append(f"Funding within last year")
        
        # Hiring signals (tech budget confirmation)
        if business_intelligence.hiring_activity.tech_leadership_hiring > 0:
            signals.append(f"Hiring tech leadership ({business_intelligence.hiring_activity.tech_leadership_hiring} positions)")
        
        if business_intelligence.hiring_activity.tech_job_postings > 0:
            signals.append(f"Active tech hiring ({business_intelligence.hiring_activity.tech_job_postings} positions)")
        
        # Technology investment signals
        if business_intelligence.technology_investment.major_tech_project_active:
            signals.append("Major technology project in progress")
        
        if business_intelligence.technology_investment.recent_website_redesign:
            signals.append("Recent website redesign/modernization")
        
        return signals
    
    async def analyze_growth_momentum(self, business_intelligence: BusinessIntelligence) -> Dict[str, Any]:
        """
        Analyze growth momentum based on business intelligence.
        
        Args:
            business_intelligence: Business intelligence data
            
        Returns:
            Growth momentum analysis
        """
        momentum_score = 0
        momentum_indicators = []
        
        # Funding momentum
        if business_intelligence.funding_profile.recent_funding_months:
            if business_intelligence.funding_profile.recent_funding_months <= 3:
                momentum_score += 40
                momentum_indicators.append("Very recent funding (high growth phase)")
            elif business_intelligence.funding_profile.recent_funding_months <= 6:
                momentum_score += 25
                momentum_indicators.append("Recent funding (growth phase)")
        
        # Hiring momentum
        if business_intelligence.hiring_activity.tech_job_postings >= 3:
            momentum_score += 30
            momentum_indicators.append("Aggressive tech hiring")
        elif business_intelligence.hiring_activity.tech_job_postings > 0:
            momentum_score += 15
            momentum_indicators.append("Active tech hiring")
        
        # Technology momentum
        if business_intelligence.technology_investment.technology_modernization_score > 70:
            momentum_score += 20
            momentum_indicators.append("High technology modernization activity")
        
        # Ad investment momentum
        if business_intelligence.ad_investment.estimated_monthly_spend > 5000:
            momentum_score += 10
            momentum_indicators.append("Significant advertising investment")
        
        return {
            "momentum_score": min(momentum_score, 100),
            "momentum_level": self._get_momentum_level(momentum_score),
            "indicators": momentum_indicators,
            "analysis_date": datetime.now()
        }
    
    def _get_momentum_level(self, score: int) -> str:
        """Get momentum level based on score."""
        if score >= 80:
            return "Very High"
        elif score >= 60:
            return "High"
        elif score >= 40:
            return "Medium"
        elif score >= 20:
            return "Low"
        else:
            return "Very Low"