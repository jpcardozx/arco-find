"""
🎯 CONVERSION STRATEGY ENGINE
Generates industry-specific conversion strategies and talking points
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

from .technical_pain_detector import TechnicalIntelligence, TechnicalPainPoint

logger = logging.getLogger(__name__)

@dataclass
class ConversionStrategy:
    """Complete conversion strategy for a specific lead"""
    approach_type: str  # 'technical_demo', 'audit_offer', 'case_study', 'roi_analysis'
    primary_hook: str   # Opening statement/value proposition
    talking_points: List[str]
    objection_handlers: Dict[str, str]
    timeline_strategy: str
    success_metrics: List[str]
    follow_up_cadence: Dict[str, str]

@dataclass
class LeadProfile:
    """Conversion-ready lead profile with complete intelligence"""
    company_name: str
    website: str
    industry: str
    pain_profile: Dict[str, any]
    conversion_strategy: ConversionStrategy
    urgency_timeline: str
    decision_maker_profile: Dict[str, str]
    competitive_intel: Dict[str, any]
    roi_projection: Dict[str, float]
    next_steps: List[Dict[str, str]]

class ConversionStrategyEngine:
    """Generates conversion-ready strategies based on technical intelligence"""
    
    def __init__(self):
        # Industry-specific conversion strategies
        self.industry_strategies = {
            'ecommerce': {
                'primary_concerns': ['conversion_rate', 'cart_abandonment', 'mobile_performance'],
                'decision_makers': ['cmo', 'ecommerce_manager', 'cto'],
                'typical_timeline': '2-4 weeks',
                'budget_decision_factors': ['roi_timeline', 'competitive_pressure', 'seasonal_impact'],
                'preferred_approach': 'roi_analysis'
            },
            'saas': {
                'primary_concerns': ['customer_acquisition_cost', 'churn_rate', 'performance'],
                'decision_makers': ['cmo', 'vp_growth', 'cto'],
                'typical_timeline': '4-8 weeks',
                'budget_decision_factors': ['ltv_impact', 'scalability', 'technical_debt'],
                'preferred_approach': 'technical_demo'
            },
            'digital_marketing': {
                'primary_concerns': ['client_results', 'operational_efficiency', 'competitive_advantage'],
                'decision_makers': ['ceo', 'operations_manager', 'account_director'],
                'typical_timeline': '1-3 weeks',
                'budget_decision_factors': ['client_impact', 'time_savings', 'win_rate'],
                'preferred_approach': 'case_study'
            },
            'healthtech': {
                'primary_concerns': ['patient_experience', 'compliance', 'operational_efficiency'],
                'decision_makers': ['coo', 'cto', 'practice_manager'],
                'typical_timeline': '6-12 weeks',
                'budget_decision_factors': ['patient_satisfaction', 'operational_cost', 'compliance_risk'],
                'preferred_approach': 'audit_offer'
            }
        }
        
        # Pain-specific messaging frameworks
        self.pain_messaging = {
            'performance': {
                'urgency_triggers': ['mobile_abandonment', 'conversion_loss', 'competitive_disadvantage'],
                'value_props': ['revenue_recovery', 'user_experience', 'competitive_advantage'],
                'proof_points': ['industry_benchmarks', 'case_studies', 'technical_analysis']
            },
            'message_match': {
                'urgency_triggers': ['ad_waste', 'quality_score', 'conversion_disconnect'],
                'value_props': ['ad_efficiency', 'cost_reduction', 'conversion_improvement'],
                'proof_points': ['audit_results', 'a_b_test_data', 'industry_standards']
            },
            'tracking': {
                'urgency_triggers': ['blind_optimization', 'attribution_gaps', 'budget_waste'],
                'value_props': ['data_clarity', 'optimization_accuracy', 'roi_improvement'],
                'proof_points': ['tracking_analysis', 'attribution_models', 'optimization_results']
            },
            'integration': {
                'urgency_triggers': ['lead_leakage', 'manual_processes', 'conversion_friction'],
                'value_props': ['automation', 'lead_capture', 'process_efficiency'],
                'proof_points': ['integration_audit', 'automation_examples', 'efficiency_gains']
            }
        }
    
    def generate_conversion_strategy(self, 
                                   validated_intelligence: TechnicalIntelligence,
                                   confidence_level: str,
                                   industry: str = None) -> LeadProfile:
        """
        Generate complete conversion-ready lead profile
        """
        logger.info(f"🎯 Generating conversion strategy for {validated_intelligence.company_name}")
        
        # Determine industry strategy
        industry_key = self._map_industry(industry or 'saas')
        industry_config = self.industry_strategies.get(industry_key, self.industry_strategies['saas'])
        
        # Generate conversion strategy
        conversion_strategy = self._create_conversion_strategy(
            validated_intelligence, confidence_level, industry_config
        )
        
        # Build pain profile
        pain_profile = self._build_pain_profile(validated_intelligence)
        
        # Determine decision maker profile
        decision_maker_profile = self._profile_decision_maker(
            validated_intelligence, industry_config
        )
        
        # Generate competitive intelligence
        competitive_intel = self._generate_competitive_intel(
            validated_intelligence, industry_key
        )
        
        # Calculate ROI projections
        roi_projection = self._calculate_roi_projections(validated_intelligence)
        
        # Create urgency timeline
        urgency_timeline = self._determine_urgency_timeline(
            validated_intelligence, industry_config
        )
        
        # Generate next steps
        next_steps = self._create_next_steps(
            validated_intelligence, conversion_strategy, confidence_level
        )
        
        return LeadProfile(
            company_name=validated_intelligence.company_name,
            website=validated_intelligence.website,
            industry=industry_key,
            pain_profile=pain_profile,
            conversion_strategy=conversion_strategy,
            urgency_timeline=urgency_timeline,
            decision_maker_profile=decision_maker_profile,
            competitive_intel=competitive_intel,
            roi_projection=roi_projection,
            next_steps=next_steps
        )
    
    def _map_industry(self, industry: str) -> str:
        """Map industry to strategy category"""
        industry_lower = industry.lower()
        
        if any(term in industry_lower for term in ['ecommerce', 'retail', 'shop', 'store']):
            return 'ecommerce'
        elif any(term in industry_lower for term in ['saas', 'software', 'tech', 'app']):
            return 'saas'
        elif any(term in industry_lower for term in ['marketing', 'agency', 'advertising']):
            return 'digital_marketing'
        elif any(term in industry_lower for term in ['health', 'medical', 'clinic', 'dental']):
            return 'healthtech'
        else:
            return 'saas'  # Default
    
    def _create_conversion_strategy(self, 
                                  intelligence: TechnicalIntelligence,
                                  confidence_level: str,
                                  industry_config: Dict) -> ConversionStrategy:
        """Create specific conversion strategy"""
        
        # Determine approach type based on pain and industry
        primary_pain = max(intelligence.pain_points, key=lambda p: p.monthly_cost) if intelligence.pain_points else None
        approach_type = industry_config['preferred_approach']
        
        # Adjust approach based on confidence and pain severity
        if confidence_level == 'high' and primary_pain and primary_pain.monthly_cost > 5000:
            approach_type = 'technical_demo'
        elif confidence_level == 'medium':
            approach_type = 'audit_offer'
        
        # Generate primary hook
        primary_hook = self._generate_primary_hook(intelligence, primary_pain, approach_type)
        
        # Generate talking points
        talking_points = self._generate_talking_points(intelligence, primary_pain, industry_config)
        
        # Generate objection handlers
        objection_handlers = self._generate_objection_handlers(intelligence, industry_config)
        
        # Timeline strategy
        timeline_strategy = self._create_timeline_strategy(intelligence, industry_config)
        
        # Success metrics
        success_metrics = self._define_success_metrics(intelligence, primary_pain)
        
        # Follow-up cadence
        follow_up_cadence = self._create_follow_up_cadence(intelligence.commercial_urgency)
        
        return ConversionStrategy(
            approach_type=approach_type,
            primary_hook=primary_hook,
            talking_points=talking_points,
            objection_handlers=objection_handlers,
            timeline_strategy=timeline_strategy,
            success_metrics=success_metrics,
            follow_up_cadence=follow_up_cadence
        )
    
    def _generate_primary_hook(self, intelligence: TechnicalIntelligence, 
                             primary_pain: TechnicalPainPoint, approach_type: str) -> str:
        """Generate compelling opening statement"""
        
        if not primary_pain:
            return f"Our analysis indicates potential optimization opportunities for {intelligence.company_name}"
        
        monthly_cost = primary_pain.monthly_cost
        annual_cost = monthly_cost * 12
        
        hooks = {
            'technical_demo': f"We've identified a {primary_pain.category} issue that's costing {intelligence.company_name} approximately ${monthly_cost:,.0f} per month. I'd like to show you exactly how we can fix this.",
            'audit_offer': f"Our technical analysis reveals ${monthly_cost:,.0f}/month in potential savings from {primary_pain.category} optimization. Would you be interested in a complimentary audit to validate these findings?",
            'case_study': f"We helped a similar company recover ${annual_cost:,.0f}/year by solving the exact {primary_pain.category} issue we've identified at {intelligence.company_name}.",
            'roi_analysis': f"Based on our analysis, fixing your {primary_pain.category} issues could recover ${annual_cost:,.0f} annually with a 3-month payback period."
        }
        
        return hooks.get(approach_type, hooks['technical_demo'])
    
    def _generate_talking_points(self, intelligence: TechnicalIntelligence,
                               primary_pain: TechnicalPainPoint, 
                               industry_config: Dict) -> List[str]:
        """Generate specific talking points"""
        
        talking_points = []
        
        if primary_pain:
            # Pain-specific points
            pain_messaging = self.pain_messaging.get(primary_pain.category, {})
            
            # Cost impact point
            talking_points.append(
                f"Current {primary_pain.category} issues are costing ${primary_pain.monthly_cost:,.0f}/month"
            )
            
            # Solution fit point
            talking_points.append(primary_pain.solution_fit)
            
            # Timeline point
            talking_points.append(f"Implementation timeline: {primary_pain.timeline_to_fix}")
            
            # Industry-specific value props
            for concern in industry_config['primary_concerns']:
                if concern in primary_pain.description.lower():
                    talking_points.append(f"This directly impacts your {concern.replace('_', ' ')}")
        
        # Add confidence-based points
        talking_points.append("Our analysis is backed by multi-source validation")
        
        # Add urgency point
        if intelligence.commercial_urgency == 'hot':
            talking_points.append("This issue requires immediate attention to prevent further losses")
        
        return talking_points[:5]  # Limit to top 5
    
    def _generate_objection_handlers(self, intelligence: TechnicalIntelligence,
                                   industry_config: Dict) -> Dict[str, str]:
        """Generate responses to common objections"""
        
        return {
            "too_expensive": f"The cost of inaction is ${intelligence.total_monthly_pain_cost * 12:,.0f}/year. Our solution pays for itself in {industry_config.get('typical_timeline', '4-6 weeks')}.",
            "not_priority": f"This issue is currently costing ${intelligence.total_monthly_pain_cost:,.0f}/month. What would need to change for this to become a priority?",
            "need_to_think": f"I understand. While you're considering, you're losing ${intelligence.total_monthly_pain_cost/30:.0f} per day. Can we schedule a brief follow-up?",
            "working_with_someone": "Great! How are they addressing the specific technical debt we've identified? We'd be happy to complement their work.",
            "no_budget": f"This solution should be self-funding through the ${intelligence.total_monthly_pain_cost:,.0f}/month recovery. Can we explore a performance-based arrangement?"
        }
    
    def _create_timeline_strategy(self, intelligence: TechnicalIntelligence,
                                industry_config: Dict) -> str:
        """Create timeline-based strategy"""
        
        urgency = intelligence.commercial_urgency
        typical_timeline = industry_config.get('typical_timeline', '4-6 weeks')
        
        if urgency == 'hot':
            return f"Accelerated timeline due to immediate impact - target {typical_timeline} for full implementation"
        elif urgency == 'warm':
            return f"Standard timeline - {typical_timeline} from approval to results"
        else:
            return f"Flexible timeline - can accommodate {typical_timeline} or longer planning cycle"
    
    def _define_success_metrics(self, intelligence: TechnicalIntelligence,
                              primary_pain: TechnicalPainPoint) -> List[str]:
        """Define measurable success metrics"""
        
        metrics = []
        
        if primary_pain:
            if primary_pain.category == 'performance':
                metrics.extend([
                    "Mobile page speed improvement to 85+ score",
                    f"Conversion rate increase of 20-30%",
                    "User abandonment reduction"
                ])
            elif primary_pain.category == 'message_match':
                metrics.extend([
                    "Ad Quality Score improvement",
                    "Cost-per-click reduction",
                    "Landing page conversion improvement"
                ])
            elif primary_pain.category == 'tracking':
                metrics.extend([
                    "Attribution accuracy to 90%+",
                    "Data-driven optimization improvement",
                    "ROAS improvement of 15-25%"
                ])
            
        # Always include financial metrics
        metrics.append(f"Monthly cost recovery: ${intelligence.total_monthly_pain_cost:,.0f}")
        metrics.append(f"Annual ROI: {intelligence.total_monthly_pain_cost * 12 / 50000 * 100:.0f}%")  # Assuming $50k solution cost
        
        return metrics[:4]  # Top 4 metrics
    
    def _create_follow_up_cadence(self, urgency: str) -> Dict[str, str]:
        """Create follow-up schedule based on urgency"""
        
        cadences = {
            'hot': {
                'immediate': 'Same day follow-up if no response',
                'short_term': 'Daily follow-up for first week',
                'medium_term': 'Weekly follow-up for one month'
            },
            'warm': {
                'immediate': '24-48 hour follow-up',
                'short_term': 'Bi-weekly follow-up for first month',
                'medium_term': 'Monthly follow-up for quarter'
            },
            'cold': {
                'immediate': 'One week follow-up',
                'short_term': 'Monthly follow-up',
                'medium_term': 'Quarterly check-in'
            }
        }
        
        return cadences.get(urgency, cadences['warm'])
    
    def _build_pain_profile(self, intelligence: TechnicalIntelligence) -> Dict[str, any]:
        """Build comprehensive pain profile"""
        
        pain_categories = {}
        total_pain = intelligence.total_monthly_pain_cost
        
        for pain in intelligence.pain_points:
            pain_categories[pain.category] = {
                'monthly_cost': pain.monthly_cost,
                'severity': pain.severity,
                'urgency': pain.urgency_level,
                'description': pain.description,
                'percentage_of_total': (pain.monthly_cost / total_pain * 100) if total_pain > 0 else 0
            }
        
        return {
            'total_monthly_cost': total_pain,
            'total_annual_opportunity': total_pain * 12,
            'pain_categories': pain_categories,
            'primary_pain_category': max(intelligence.pain_points, key=lambda p: p.monthly_cost).category if intelligence.pain_points else None,
            'urgency_level': intelligence.commercial_urgency
        }
    
    def _profile_decision_maker(self, intelligence: TechnicalIntelligence,
                              industry_config: Dict) -> Dict[str, str]:
        """Profile likely decision maker"""
        
        primary_pain = max(intelligence.pain_points, key=lambda p: p.monthly_cost) if intelligence.pain_points else None
        
        # Determine likely decision maker based on pain type and cost
        if intelligence.total_monthly_pain_cost > 10000:
            likely_dm = 'ceo_or_cmo'
            influence_level = 'high'
        elif primary_pain and primary_pain.category in ['performance', 'tracking']:
            likely_dm = 'cto_or_technical_lead'
            influence_level = 'medium'
        else:
            likely_dm = 'marketing_manager'
            influence_level = 'medium'
        
        return {
            'likely_decision_maker': likely_dm,
            'influence_level': influence_level,
            'typical_concerns': ', '.join(industry_config.get('budget_decision_factors', [])),
            'decision_timeline': industry_config.get('typical_timeline', '4-6 weeks')
        }
    
    def _generate_competitive_intel(self, intelligence: TechnicalIntelligence,
                                  industry: str) -> Dict[str, any]:
        """Generate competitive positioning"""
        
        return {
            'competitive_advantage': f"Multi-source validated analysis vs. generic recommendations",
            'unique_value_prop': f"Specific ${intelligence.total_monthly_pain_cost:,.0f}/month recovery vs. vague optimization promises",
            'differentiation': "Technical intelligence-driven approach with confidence scoring",
            'proof_points': f"Cross-validated findings from {len(intelligence.pain_points)} specific issues"
        }
    
    def _calculate_roi_projections(self, intelligence: TechnicalIntelligence) -> Dict[str, float]:
        """Calculate ROI projections"""
        
        monthly_recovery = intelligence.total_monthly_pain_cost
        annual_recovery = monthly_recovery * 12
        estimated_solution_cost = 50000  # Typical engagement cost
        
        return {
            'monthly_recovery': monthly_recovery,
            'annual_recovery': annual_recovery,
            'solution_investment': estimated_solution_cost,
            'payback_months': (estimated_solution_cost / monthly_recovery) if monthly_recovery > 0 else 12,
            'first_year_roi': ((annual_recovery - estimated_solution_cost) / estimated_solution_cost * 100) if estimated_solution_cost > 0 else 0,
            'three_year_value': annual_recovery * 3 - estimated_solution_cost
        }
    
    def _determine_urgency_timeline(self, intelligence: TechnicalIntelligence,
                                  industry_config: Dict) -> str:
        """Determine urgency-based timeline"""
        
        current_date = datetime.now()
        urgency = intelligence.commercial_urgency
        
        if urgency == 'hot':
            target_date = current_date + timedelta(days=7)
            return f"Target decision by {target_date.strftime('%B %d')} - immediate action required"
        elif urgency == 'warm':
            target_date = current_date + timedelta(days=21)
            return f"Target decision by {target_date.strftime('%B %d')} - opportunity window closing"
        else:
            target_date = current_date + timedelta(days=60)
            return f"Target decision by {target_date.strftime('%B %d')} - strategic planning timeline"
    
    def _create_next_steps(self, intelligence: TechnicalIntelligence,
                         strategy: ConversionStrategy,
                         confidence_level: str) -> List[Dict[str, str]]:
        """Create specific next steps"""
        
        steps = []
        
        # Immediate step based on confidence
        if confidence_level == 'high':
            steps.append({
                'step': 'immediate_call',
                'action': 'Schedule technical demonstration call',
                'timeline': 'Within 24 hours',
                'owner': 'sales_rep'
            })
        else:
            steps.append({
                'step': 'validation_call',
                'action': 'Schedule audit validation call',
                'timeline': 'Within 48 hours',
                'owner': 'technical_consultant'
            })
        
        # Follow-up steps
        steps.append({
            'step': 'technical_audit',
            'action': 'Conduct detailed technical assessment',
            'timeline': '3-5 days post-call',
            'owner': 'technical_team'
        })
        
        steps.append({
            'step': 'proposal_delivery',
            'action': 'Present customized solution proposal',
            'timeline': '1 week post-audit',
            'owner': 'account_manager'
        })
        
        steps.append({
            'step': 'closing_meeting',
            'action': 'Final decision meeting with stakeholders',
            'timeline': f"2-3 weeks (based on {intelligence.commercial_urgency} urgency)",
            'owner': 'senior_sales'
        })
        
        return steps