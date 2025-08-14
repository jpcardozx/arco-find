"""
Analytics Agent - ARCO V3
Tracks pipeline metrics, analyzes performance, and provides optimization recommendations
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict

from ..models.core_models import AnalyticsReport, ScoredProspect, OutreachMessage

logger = logging.getLogger(__name__)


class AnalyticsAgent:
    """Pipeline analytics and optimization"""
    
    def __init__(self):
        self.response_rate_threshold = 0.12  # 12%
        self.audit_conversion_threshold = 0.30  # 30%
    
    def generate_daily_report(self, 
                            prospects: List[ScoredProspect],
                            outreach: List[OutreachMessage],
                            responses: List = None) -> AnalyticsReport:
        """Generate daily analytics report"""
        
        responses = responses or []
        
        # Calculate metrics
        prospects_discovered = len(prospects)
        prospects_qualified = sum(1 for p in prospects if p.priority_score >= 8)
        outreach_sent = len(outreach)
        responses_received = len(responses)
        
        response_rate = responses_received / outreach_sent if outreach_sent > 0 else 0
        qualification_rate = prospects_qualified / prospects_discovered if prospects_discovered > 0 else 0
        
        # Calculate revenue
        revenue_generated = sum(p.deal_size_range[0] for p in prospects if p.priority_score >= 10)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            response_rate, qualification_rate, prospects
        )
        
        report = AnalyticsReport(
            date=datetime.now(timezone.utc),
            prospects_discovered=prospects_discovered,
            prospects_qualified=prospects_qualified,
            outreach_sent=outreach_sent,
            responses_received=responses_received,
            audits_scheduled=0,  # Would track from CRM
            deals_closed=0,      # Would track from CRM
            response_rate=response_rate,
            qualification_rate=qualification_rate,
            revenue_generated=revenue_generated,
            optimization_recommendations=recommendations
        )
        
        logger.info(f"📊 Daily report generated: {prospects_qualified} qualified from {prospects_discovered} discovered")
        return report
    
    def _generate_recommendations(self, 
                                response_rate: float,
                                qualification_rate: float,
                                prospects: List[ScoredProspect]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        if response_rate < self.response_rate_threshold:
            recommendations.append("Response rate below 12% - review message personalization")
        
        if qualification_rate < 0.15:
            recommendations.append("Low qualification rate - tighten discovery criteria")
        
        # Analyze prospect quality
        high_score_count = sum(1 for p in prospects if p.priority_score >= 12)
        if high_score_count / len(prospects) < 0.1 if prospects else True:
            recommendations.append("Few high-priority prospects - expand vertical targeting")
        
        return recommendations
    
    def generate_performance_report(self, 
                                  prospects_discovered: List,
                                  prospects_qualified: List,
                                  outreach_messages: List,
                                  execution_id: str) -> Dict:
        """
        Generate performance report for pipeline execution
        """
        logger.info(f"📊 Generating performance report for execution: {execution_id}")
        
        discovery_count = len(prospects_discovered)
        qualified_count = len(prospects_qualified) 
        outreach_count = len(outreach_messages)
        
        qualification_rate = qualified_count / discovery_count if discovery_count > 0 else 0
        
        # Calculate revenue potential
        total_revenue_potential = 0
        if prospects_qualified:
            for prospect in prospects_qualified:
                if hasattr(prospect, 'deal_size_range') and prospect.deal_size_range:
                    total_revenue_potential += prospect.deal_size_range[0]
        
        performance_report = {
            "execution_id": execution_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "qualification_rate": qualification_rate,
            "revenue_generated": total_revenue_potential,
            "optimization_recommendations": self._generate_execution_recommendations(
                qualification_rate, outreach_count, qualified_count
            ),
            "discovery": {
                "prospects_found": discovery_count,
                "success_rate": 1.0 if discovery_count > 0 else 0.0
            },
            "qualification": {
                "prospects_qualified": qualified_count,
                "qualification_rate": qualification_rate,
                "target_rate": 0.25  # 25% target
            },
            "outreach": {
                "messages_generated": outreach_count,
                "personalization_rate": 0.8 if outreach_count > 0 else 0.0
            },
            "revenue": {
                "total_potential": total_revenue_potential,
                "average_deal_size": total_revenue_potential / qualified_count if qualified_count > 0 else 0
            }
        }
        
        logger.info(f"✅ Performance report completed: {qualified_count}/{discovery_count} qualified ({qualification_rate:.1%})")
        return performance_report
    
    def _generate_execution_recommendations(self, 
                                          qualification_rate: float,
                                          outreach_count: int,
                                          qualified_count: int) -> List[str]:
        """Generate recommendations for pipeline execution"""
        recommendations = []
        
        if qualification_rate < 0.15:
            recommendations.append("Qualification rate below 15% - review discovery criteria")
        elif qualification_rate > 0.40:
            recommendations.append("High qualification rate - consider expanding discovery volume")
        
        if outreach_count == 0 and qualified_count > 0:
            recommendations.append("Qualified prospects without outreach - check outreach generation")
        
        if qualified_count > 8:
            recommendations.append("High prospect volume - prioritize by strategic tier")
        
        return recommendations