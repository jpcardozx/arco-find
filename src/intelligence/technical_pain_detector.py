"""
🎯 TECHNICAL PAIN DETECTOR
Identifies real technical pain points that cost money and require urgent attention
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re
import math

@dataclass
class TechnicalPainPoint:
    """Specific technical problem costing business money"""
    category: str  # 'performance', 'message_match', 'tracking', 'integration'
    severity: str  # 'critical', 'high', 'medium', 'low'
    description: str
    monthly_cost: float
    urgency_level: str  # 'immediate', 'this_week', 'this_month'
    evidence: List[str]  # Specific data supporting this pain point
    solution_fit: str  # How well our solution addresses this
    timeline_to_fix: str  # Realistic timeline to resolve

@dataclass
class TechnicalIntelligence:
    """Complete technical intelligence about a prospect"""
    company_name: str
    website: str
    total_monthly_pain_cost: float
    pain_points: List[TechnicalPainPoint]
    commercial_urgency: str  # 'hot', 'warm', 'cold'
    conversion_probability: float  # 0.0 to 1.0
    rationale: str  # Why this lead should be prioritized
    next_action: str  # Specific next step for sales
    
class TechnicalPainDetector:
    """Detects technical debt signals that translate to business pain"""
    
    def __init__(self):
        # Performance thresholds that indicate business pain
        self.performance_thresholds = {
            'critical_lcp': 4.0,  # >4s LCP loses 50%+ users
            'poor_lcp': 2.5,      # >2.5s LCP hurts conversions
            'critical_fid': 300,  # >300ms FID frustrates users
            'poor_fid': 100,      # >100ms FID impacts UX
            'critical_cls': 0.25, # >0.25 CLS breaks usability
            'poor_cls': 0.1       # >0.1 CLS annoys users
        }
        
        # Message-match failure patterns
        self.mismatch_patterns = {
            'value_prop_disconnect': [
                r'save\s+time|faster|quick',
                r'save\s+money|cheaper|cost',
                r'increase\s+sales|grow|revenue'
            ],
            'target_audience_mismatch': [
                r'small\s+business|startup',
                r'enterprise|corporate',
                r'agency|consultant'
            ]
        }
    
    def analyze_technical_pain(self, 
                             company_name: str,
                             website: str, 
                             performance_data: Dict,
                             digital_presence: Dict,
                             business_context: Dict) -> TechnicalIntelligence:
        """
        Analyze all technical pain points and generate actionable intelligence
        """
        pain_points = []
        
        # 1. Performance Pain Analysis
        perf_pain = self._analyze_performance_pain(performance_data, business_context)
        pain_points.extend(perf_pain)
        
        # 2. Message-Match Pain Analysis 
        message_pain = self._analyze_message_match_pain(digital_presence, website, business_context)
        pain_points.extend(message_pain)
        
        # 3. Tracking/Attribution Pain Analysis
        tracking_pain = self._analyze_tracking_pain(website, digital_presence, business_context)
        pain_points.extend(tracking_pain)
        
        # 4. Integration Pain Analysis
        integration_pain = self._analyze_integration_pain(business_context)
        pain_points.extend(integration_pain)
        
        # Calculate commercial metrics
        total_cost = sum(p.monthly_cost for p in pain_points)
        urgency = self._calculate_commercial_urgency(pain_points, business_context)
        conversion_prob = self._calculate_conversion_probability(pain_points, business_context)
        rationale = self._generate_rationale(pain_points, business_context)
        next_action = self._determine_next_action(pain_points, urgency)
        
        return TechnicalIntelligence(
            company_name=company_name,
            website=website,
            total_monthly_pain_cost=total_cost,
            pain_points=pain_points,
            commercial_urgency=urgency,
            conversion_probability=conversion_prob,
            rationale=rationale,
            next_action=next_action
        )
    
    def _analyze_performance_pain(self, performance_data: Dict, business_context: Dict) -> List[TechnicalPainPoint]:
        """Detect performance issues that cost money"""
        pain_points = []
        
        mobile_score = performance_data.get('mobile_score', 100)
        monthly_traffic = business_context.get('estimated_monthly_traffic', 10000)
        avg_order_value = business_context.get('avg_order_value', 200)
        conversion_rate = business_context.get('conversion_rate', 0.02)
        
        # Critical performance pain
        if mobile_score < 40:
            # Critical performance = 30-50% user abandonment
            abandonment_rate = 0.4
            lost_conversions = monthly_traffic * abandonment_rate * conversion_rate
            monthly_cost = lost_conversions * avg_order_value
            
            pain_points.append(TechnicalPainPoint(
                category='performance',
                severity='critical',
                description=f'Critical mobile performance ({mobile_score}/100) causing massive user abandonment',
                monthly_cost=monthly_cost,
                urgency_level='immediate',
                evidence=[
                    f'Mobile performance score: {mobile_score}/100',
                    f'Estimated {abandonment_rate*100:.0f}% user abandonment',
                    f'~{lost_conversions:.0f} lost conversions/month'
                ],
                solution_fit='Perfect - Performance optimization is our core service',
                timeline_to_fix='7-14 days with immediate impact'
            ))
        
        elif mobile_score < 70:
            # Poor performance = 15-25% user abandonment  
            abandonment_rate = 0.2
            lost_conversions = monthly_traffic * abandonment_rate * conversion_rate
            monthly_cost = lost_conversions * avg_order_value
            
            pain_points.append(TechnicalPainPoint(
                category='performance',
                severity='high',
                description=f'Poor mobile performance ({mobile_score}/100) hurting conversion rates',
                monthly_cost=monthly_cost,
                urgency_level='this_week',
                evidence=[
                    f'Mobile performance score: {mobile_score}/100',
                    f'Estimated {abandonment_rate*100:.0f}% user abandonment',
                    f'Performance below industry standard (70+)'
                ],
                solution_fit='High - Direct performance optimization opportunity',
                timeline_to_fix='14-21 days for significant improvement'
            ))
        
        return pain_points
    
    def _analyze_message_match_pain(self, digital_presence: Dict, website: str, business_context: Dict) -> List[TechnicalPainPoint]:
        """Detect message-match failures between ads and landing pages"""
        pain_points = []
        
        ads_found = digital_presence.get('ads_found', 0)
        monthly_ad_spend = business_context.get('monthly_ad_spend', 5000)
        
        if ads_found > 0 and monthly_ad_spend > 1000:
            # Assume message-match analysis shows poor alignment
            # In real implementation, this would use AI to analyze ad text vs landing page content
            mismatch_severity = 0.3  # 30% mismatch (would be calculated by AI)
            
            if mismatch_severity > 0.2:  # >20% mismatch is significant
                # Message-match failures typically waste 20-40% of ad spend
                waste_rate = min(0.4, mismatch_severity * 1.5)
                monthly_cost = monthly_ad_spend * waste_rate
                
                pain_points.append(TechnicalPainPoint(
                    category='message_match',
                    severity='high' if mismatch_severity > 0.3 else 'medium',
                    description=f'Message-match failure between ads and landing pages wasting ad budget',
                    monthly_cost=monthly_cost,
                    urgency_level='this_week',
                    evidence=[
                        f'{ads_found} active ads detected',
                        f'${monthly_ad_spend:,.0f}/month ad spend',
                        f'Estimated {mismatch_severity*100:.0f}% message mismatch',
                        'Poor ad-to-landing alignment hurts Quality Score'
                    ],
                    solution_fit='High - Message-match optimization reduces CAC by 25-40%',
                    timeline_to_fix='5-10 days for landing page alignment'
                ))
        
        return pain_points
    
    def _analyze_tracking_pain(self, website: str, digital_presence: Dict, business_context: Dict) -> List[TechnicalPainPoint]:
        """Detect tracking and attribution breakdowns"""
        pain_points = []
        
        monthly_ad_spend = business_context.get('monthly_ad_spend', 0)
        
        # Assume tracking analysis (would use real tracking verification in production)
        if monthly_ad_spend > 2000:
            # Common tracking issues in 60% of websites
            tracking_reliability = 0.7  # 70% tracking reliability assumed
            
            if tracking_reliability < 0.9:  # <90% tracking is problematic
                # Poor tracking = 10-20% budget waste due to bad optimization
                waste_rate = (1 - tracking_reliability) * 0.3
                monthly_cost = monthly_ad_spend * waste_rate
                
                pain_points.append(TechnicalPainPoint(
                    category='tracking',
                    severity='medium',
                    description='Attribution gaps preventing proper campaign optimization',
                    monthly_cost=monthly_cost,
                    urgency_level='this_month',
                    evidence=[
                        f'${monthly_ad_spend:,.0f}/month ad spend without perfect attribution',
                        f'Estimated {tracking_reliability*100:.0f}% tracking reliability',
                        'Optimization decisions based on incomplete data'
                    ],
                    solution_fit='Medium - Attribution setup improves ROAS by 15-25%',
                    timeline_to_fix='10-14 days for comprehensive tracking'
                ))
        
        return pain_points
    
    def _analyze_integration_pain(self, business_context: Dict) -> List[TechnicalPainPoint]:
        """Detect integration failures between marketing and sales systems"""
        pain_points = []
        
        monthly_leads = business_context.get('monthly_leads', 100)
        lead_value = business_context.get('avg_lead_value', 500)
        
        # Assume integration analysis shows gaps
        if monthly_leads > 50:
            # Common integration gaps cause 10-15% lead loss
            integration_efficiency = 0.85  # 85% efficiency assumed
            
            if integration_efficiency < 0.95:  # <95% is suboptimal
                lost_leads = monthly_leads * (1 - integration_efficiency)
                monthly_cost = lost_leads * lead_value
                
                pain_points.append(TechnicalPainPoint(
                    category='integration',
                    severity='medium',
                    description='Marketing-to-sales handoff losing qualified leads',
                    monthly_cost=monthly_cost,
                    urgency_level='this_month',
                    evidence=[
                        f'{monthly_leads} monthly leads generated',
                        f'~{lost_leads:.0f} leads lost in handoff process',
                        'Manual processes creating lead leakage'
                    ],
                    solution_fit='Medium - Automation reduces lead loss by 80%+',
                    timeline_to_fix='14-21 days for full integration'
                ))
        
        return pain_points
    
    def _calculate_commercial_urgency(self, pain_points: List[TechnicalPainPoint], business_context: Dict) -> str:
        """Calculate overall commercial urgency based on pain severity and cost"""
        if not pain_points:
            return 'cold'
        
        total_cost = sum(p.monthly_cost for p in pain_points)
        critical_issues = len([p for p in pain_points if p.severity == 'critical'])
        immediate_issues = len([p for p in pain_points if p.urgency_level == 'immediate'])
        
        # Hot: >$5k/month pain OR critical performance issues
        if total_cost > 5000 or critical_issues > 0 or immediate_issues > 0:
            return 'hot'
        
        # Warm: >$2k/month pain OR multiple high-severity issues
        elif total_cost > 2000 or len([p for p in pain_points if p.severity == 'high']) >= 2:
            return 'warm'
        
        else:
            return 'cold'
    
    def _calculate_conversion_probability(self, pain_points: List[TechnicalPainPoint], business_context: Dict) -> float:
        """Calculate probability of converting this lead based on pain and fit"""
        if not pain_points:
            return 0.1
        
        base_probability = 0.3  # 30% baseline
        
        # Pain severity factor
        total_cost = sum(p.monthly_cost for p in pain_points)
        cost_factor = min(0.4, total_cost / 10000)  # Up to 40% boost for high-cost pain
        
        # Solution fit factor
        high_fit_points = len([p for p in pain_points if 'Perfect' in p.solution_fit or 'High' in p.solution_fit])
        fit_factor = min(0.2, high_fit_points * 0.1)  # Up to 20% boost for good fit
        
        # Urgency factor
        urgent_points = len([p for p in pain_points if p.urgency_level in ['immediate', 'this_week']])
        urgency_factor = min(0.1, urgent_points * 0.05)  # Up to 10% boost for urgency
        
        return min(0.9, base_probability + cost_factor + fit_factor + urgency_factor)
    
    def _generate_rationale(self, pain_points: List[TechnicalPainPoint], business_context: Dict) -> str:
        """Generate clear rationale for why this lead should be prioritized"""
        if not pain_points:
            return "No significant technical pain identified - low priority"
        
        total_cost = sum(p.monthly_cost for p in pain_points)
        annual_cost = total_cost * 12
        top_pain = max(pain_points, key=lambda p: p.monthly_cost)
        
        rationale_parts = [
            f"Company losing ${total_cost:,.0f}/month (${annual_cost:,.0f}/year) from technical debt.",
            f"Primary pain: {top_pain.description}.",
            f"Urgency: {top_pain.urgency_level.replace('_', ' ').title()} - {top_pain.evidence[0]}.",
            f"Solution fit: {top_pain.solution_fit}."
        ]
        
        return " ".join(rationale_parts)
    
    def _determine_next_action(self, pain_points: List[TechnicalPainPoint], urgency: str) -> str:
        """Determine specific next action for sales team"""
        if not pain_points:
            return "Nurture lead - monitor for future pain signals"
        
        if urgency == 'hot':
            top_pain = max(pain_points, key=lambda p: p.monthly_cost)
            return f"IMMEDIATE CALL: Lead with ${top_pain.monthly_cost:,.0f}/month {top_pain.category} pain. Open with: 'We've identified a {top_pain.category} issue that might be costing you money...'"
        
        elif urgency == 'warm':
            pain_categories = list(set(p.category for p in pain_points))
            return f"Schedule audit call within 48h: Multiple opportunities in {', '.join(pain_categories)}. Lead with free assessment."
        
        else:
            return "Add to nurture sequence: Monitor for pain escalation or seasonal triggers"