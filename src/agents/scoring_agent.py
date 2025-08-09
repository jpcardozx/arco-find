"""
Scoring Agent - ARCO V3
Combines scores from Discovery, Performance, and Fit analysis
Based on AGENTS.md specification
"""

import logging
from datetime import datetime, timezone
from typing import Optional, Tuple

from ..models.core_models import (
    DiscoveryOutput, 
    PerformanceOutput, 
    ScoredProspect, 
    ServiceFit
)

logger = logging.getLogger(__name__)


class ScoringAgent:
    """
    Scoring Agent implementing the decision tree from AGENTS.md:
    - Combine scores from Discovery, Performance and Fit
    - Calculate Priority Score final
    - Determine service fit (CWV/LP/Tracking)
    - Estimate deal size and monthly loss
    """
    
    def __init__(self):
        # Priority threshold for outreach qualification
        self.priority_threshold = 8
        
        # Service fit definitions with deal size ranges
        self.service_definitions = {
            ServiceFit.CWV_RESCUE: {
                "min_leak_score": 6,
                "required_indicators": ["LCP_HIGH"],
                "deal_size_range": (700, 1200),
                "description": "2-week Core Web Vitals optimization sprint"
            },
            ServiceFit.LP_EXPERIMENT: {
                "min_leak_score": 6,
                "min_indicators": 3,
                "deal_size_range": (900, 1500),
                "description": "3-week Landing Page experiment package"
            },
            ServiceFit.TRACKING_RELIABILITY: {
                "max_leak_score": 5,
                "deal_size_range": (400, 600),
                "description": "Conversion tracking setup and optimization"
            }
        }
        
        # Monthly revenue loss estimates per leak indicator
        self.loss_multipliers = {
            "LCP_HIGH": 1500,      # High impact on conversions
            "INP_HIGH": 1200,      # User frustration
            "CLS_HIGH": 800,       # Layout shift disruption
            "MOBILE_UNFRIENDLY": 2000,  # 60% of traffic
            "NO_PHONE_CTA": 600,   # Missed lead capture
            "SSL_ISSUES": 1000,    # Trust and SEO impact
            "WEAK_FORM": 500       # Form abandonment
        }
    
    def calculate_priority(self, 
                          discovery_output: DiscoveryOutput,
                          performance_output: PerformanceOutput) -> Optional[ScoredProspect]:
        """
        Calculate priority score following the scoring decision flow
        """
        logger.info(f"🎯 Scoring prospect: {discovery_output.domain}")
        
        # Calculate total priority score
        total_score = (
            discovery_output.demand_score +
            discovery_output.fit_score +
            performance_output.leak_score
        )
        
        logger.debug(f"Score breakdown - Demand: {discovery_output.demand_score}, "
                    f"Fit: {discovery_output.fit_score}, Leak: {performance_output.leak_score}")
        
        # Gate 1: Priority Threshold
        if total_score < self.priority_threshold:
            logger.debug(f"❌ Priority threshold not met: {total_score} < {self.priority_threshold}")
            return None
        
        # Gate 2: Service Fit Logic
        service_fit, deal_size_range = self._determine_service_fit(performance_output)
        
        # Gate 3: Loss Estimation
        monthly_loss = self._estimate_revenue_leak(
            performance_output.leak_indicators,
            discovery_output.creative_count
        )
        
        # Calculate confidence level
        confidence_level = self._calculate_confidence(discovery_output, performance_output)
        
        prospect = ScoredProspect(
            discovery_data=discovery_output,
            performance_data=performance_output,
            priority_score=total_score,
            service_fit=service_fit,
            deal_size_range=deal_size_range,
            estimated_monthly_loss=monthly_loss,
            confidence_level=confidence_level,
            scoring_timestamp=datetime.now(timezone.utc)
        )
        
        logger.info(f"✅ Qualified prospect: {discovery_output.domain} - "
                   f"Score: {total_score}, Service: {service_fit.value}, "
                   f"Loss: ${monthly_loss}/month")
        
        return prospect
    
    def _determine_service_fit(self, 
                              performance_output: PerformanceOutput) -> Tuple[ServiceFit, Tuple[int, int]]:
        """
        Determine best service fit based on performance analysis
        """
        leak_score = performance_output.leak_score
        leak_indicators = performance_output.leak_indicators
        
        # High leak score with specific LCP issues = CWV Rescue
        if (leak_score >= self.service_definitions[ServiceFit.CWV_RESCUE]["min_leak_score"] and
            any(indicator in leak_indicators 
                for indicator in self.service_definitions[ServiceFit.CWV_RESCUE]["required_indicators"])):
            
            return ServiceFit.CWV_RESCUE, self.service_definitions[ServiceFit.CWV_RESCUE]["deal_size_range"]
        
        # High leak score with multiple indicators = LP Experiment
        elif (leak_score >= self.service_definitions[ServiceFit.LP_EXPERIMENT]["min_leak_score"] and
              len(leak_indicators) >= self.service_definitions[ServiceFit.LP_EXPERIMENT]["min_indicators"]):
            
            return ServiceFit.LP_EXPERIMENT, self.service_definitions[ServiceFit.LP_EXPERIMENT]["deal_size_range"]
        
        # Lower leak score = Tracking Reliability
        else:
            return ServiceFit.TRACKING_RELIABILITY, self.service_definitions[ServiceFit.TRACKING_RELIABILITY]["deal_size_range"]
    
    def _estimate_revenue_leak(self, 
                              leak_indicators: list,
                              creative_count: int) -> int:
        """
        Estimate monthly revenue loss based on performance leaks
        """
        base_loss = 0
        
        # Calculate base loss from leak indicators
        for indicator in leak_indicators:
            if indicator in self.loss_multipliers:
                base_loss += self.loss_multipliers[indicator]
            else:
                base_loss += 300  # Default loss for unknown indicators
        
        # Scale by advertising activity (more ads = more traffic = more loss)
        activity_multiplier = min(creative_count / 5.0, 2.0)  # Cap at 2x multiplier
        
        total_loss = int(base_loss * activity_multiplier)
        
        return min(total_loss, 10000)  # Cap at $10k/month loss estimate
    
    def _calculate_confidence(self, 
                            discovery_output: DiscoveryOutput,
                            performance_output: PerformanceOutput) -> float:
        """
        Calculate confidence level in the scoring (0.0 to 1.0)
        """
        confidence = 0.5  # Base confidence
        
        # Boost confidence based on data quality
        
        # Strong advertiser data
        if discovery_output.advertiser_id:
            confidence += 0.2
        
        # Recent activity
        if discovery_output.last_seen <= 3:
            confidence += 0.15
        elif discovery_output.last_seen <= 7:
            confidence += 0.1
        
        # Multiple creatives (indicates real advertiser)
        if discovery_output.creative_count >= 5:
            confidence += 0.15
        elif discovery_output.creative_count >= 3:
            confidence += 0.1
        
        # Successful performance analysis
        if len(performance_output.analyzed_urls) >= 2:
            confidence += 0.1
        
        # Clear performance issues identified
        if len(performance_output.leak_indicators) >= 3:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def get_service_description(self, service_fit: ServiceFit) -> str:
        """Get description for service recommendation"""
        return self.service_definitions[service_fit]["description"]
    
    def get_qualification_summary(self, prospect: ScoredProspect) -> dict:
        """Generate qualification summary for prospect"""
        return {
            "domain": prospect.discovery_data.domain,
            "company_name": prospect.discovery_data.company_name,
            "priority_score": prospect.priority_score,
            "service_recommendation": prospect.service_fit.value,
            "deal_size_range": f"${prospect.deal_size_range[0]:,}-${prospect.deal_size_range[1]:,}",
            "estimated_monthly_loss": f"${prospect.estimated_monthly_loss:,}",
            "confidence_level": f"{prospect.confidence_level:.1%}",
            "key_pain_points": prospect.performance_data.leak_indicators[:3],
            "priority_fixes": prospect.performance_data.priority_fixes[:2],
            "vertical": prospect.discovery_data.vertical,
            "last_seen": f"{prospect.discovery_data.last_seen} days ago",
            "creative_count": prospect.discovery_data.creative_count
        }
    
    def batch_score_prospects(self, 
                            discoveries: list[DiscoveryOutput],
                            performances: list[PerformanceOutput]) -> list[ScoredProspect]:
        """
        Score multiple prospects in batch
        """
        logger.info(f"📊 Batch scoring {len(discoveries)} prospects")
        
        scored_prospects = []
        
        # Match discoveries with performance data
        performance_by_domain = {p.domain: p for p in performances}
        
        for discovery in discoveries:
            performance = performance_by_domain.get(discovery.domain)
            
            if performance:
                prospect = self.calculate_priority(discovery, performance)
                if prospect:
                    scored_prospects.append(prospect)
            else:
                logger.warning(f"⚠️ No performance data for {discovery.domain}")
        
        # Sort by priority score (highest first)
        scored_prospects.sort(key=lambda p: p.priority_score, reverse=True)
        
        logger.info(f"✅ Qualified {len(scored_prospects)} prospects from {len(discoveries)} analyzed")
        
        return scored_prospects