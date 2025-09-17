"""
Outreach Engine for generating personalized outreach content.

This engine creates data-driven, personalized messaging for high-priority prospects
based on their technology stack, marketing inefficiencies, and growth indicators.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import random

from ..models.prospect import Prospect
from ..models.leak_result import LeakResult
from ..engines.priority_engine import PriorityScore

logger = logging.getLogger(__name__)


@dataclass
class OutreachContent:
    """Generated outreach content for a prospect."""
    subject_line: str
    opening_hook: str
    value_proposition: str
    specific_insights: List[str]
    call_to_action: str
    decision_maker_context: Optional[str] = None
    technical_talking_points: List[str] = field(default_factory=list)
    roi_projections: Dict[str, Any] = field(default_factory=dict)
    urgency_factors: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)


class OutreachEngine:
    """Generate personalized outreach content based on prospect analysis."""

    def __init__(self, config_path: str = "config/production.yml"):
        """Initialize the outreach engine."""
        self.config_path = config_path
        self.templates = self._load_outreach_templates()
        self.industry_messaging = self._load_industry_messaging()
        
        logger.info("OutreachEngine initialized with personalized messaging templates")

    def _load_outreach_templates(self) -> Dict[str, Dict]:
        """Load outreach templates by industry and role."""
        return {
            "saas": {
                "cto": {
                    "subject_templates": [
                        "Quick question about {company_name}'s scaling challenges",
                        "Helping {company_name} optimize engineering efficiency",
                        "{company_name}: Reducing technical debt while scaling",
                        "Performance optimization insights for {company_name}"
                    ],
                    "opening_hooks": [
                        "I noticed {company_name} recently raised {funding_stage} funding and is actively hiring engineers.",
                        "Saw that {company_name} is scaling rapidly with {employee_count}+ team members.",
                        "Your tech stack at {company_name} caught my attention - particularly your use of {key_technology}."
                    ],
                    "value_props": [
                        "help your engineering team focus on building features instead of fighting performance issues",
                        "reduce infrastructure costs while improving user experience",
                        "accelerate development velocity by eliminating technical bottlenecks"
                    ]
                },
                "ceo": {
                    "subject_templates": [
                        "{company_name}: Converting more visitors into customers",
                        "Quick ROI question for {company_name}",
                        "Helping {company_name} scale more efficiently"
                    ],
                    "opening_hooks": [
                        "Congratulations on {company_name}'s recent growth and {funding_stage} funding.",
                        "I've been following {company_name}'s impressive trajectory in the {industry} space."
                    ],
                    "value_props": [
                        "increase revenue per visitor without increasing marketing spend",
                        "improve customer acquisition efficiency and reduce churn",
                        "scale operations more cost-effectively"
                    ]
                }
            },
            "ecommerce": {
                "cmo": {
                    "subject_templates": [
                        "{company_name}: Recovering lost revenue from slow pages",
                        "Quick conversion optimization question",
                        "Helping {company_name} improve marketing ROI"
                    ],
                    "opening_hooks": [
                        "I noticed {company_name} has been growing rapidly in the {industry} space.",
                        "Your marketing approach at {company_name} is impressive - particularly your focus on {marketing_channel}."
                    ],
                    "value_props": [
                        "recover revenue lost to slow page speeds and poor user experience",
                        "improve conversion rates across all marketing channels",
                        "get more value from your existing marketing spend"
                    ]
                }
            },
            "fintech": {
                "cto": {
                    "subject_templates": [
                        "{company_name}: Ensuring optimal performance for financial transactions",
                        "Security and performance optimization for {company_name}",
                        "Quick question about {company_name}'s infrastructure scaling"
                    ],
                    "opening_hooks": [
                        "I noticed {company_name} is handling increasingly complex financial transactions.",
                        "Your approach to {key_technology} at {company_name} is interesting."
                    ],
                    "value_props": [
                        "ensure optimal performance and security for financial transactions",
                        "reduce infrastructure costs while maintaining compliance",
                        "improve system reliability and customer trust"
                    ]
                }
            }
        }

    def _load_industry_messaging(self) -> Dict[str, Dict]:
        """Load industry-specific messaging frameworks."""
        return {
            "saas": {
                "pain_points": [
                    "Technical debt slowing down development",
                    "Performance issues affecting user experience",
                    "Infrastructure costs growing faster than revenue",
                    "Engineering team spending time on maintenance vs features"
                ],
                "success_metrics": [
                    "Development velocity",
                    "User engagement and retention",
                    "Infrastructure efficiency",
                    "Time to market for new features"
                ]
            },
            "ecommerce": {
                "pain_points": [
                    "Slow page speeds causing cart abandonment",
                    "Poor mobile experience losing customers",
                    "High bounce rates from performance issues",
                    "Marketing spend not converting efficiently"
                ],
                "success_metrics": [
                    "Conversion rate optimization",
                    "Average order value",
                    "Customer lifetime value",
                    "Marketing ROI"
                ]
            },
            "fintech": {
                "pain_points": [
                    "Performance issues affecting user trust",
                    "Compliance requirements increasing complexity",
                    "Security concerns with scaling",
                    "Infrastructure costs for high availability"
                ],
                "success_metrics": [
                    "Transaction success rates",
                    "System uptime and reliability",
                    "Security and compliance",
                    "Customer trust and retention"
                ]
            }
        }

    async def generate_outreach(self, 
                               prospect: Prospect, 
                               leak_result: Optional[LeakResult] = None,
                               priority_score: Optional[PriorityScore] = None) -> OutreachContent:
        """Generate personalized outreach content for a prospect."""
        logger.info(f"Generating personalized outreach for {prospect.company_name}")
        
        # Determine target decision maker and role
        target_role = self._determine_target_role(prospect, priority_score)
        
        # Get industry context
        industry_context = self._get_industry_context(prospect)
        
        # Extract specific insights and pain points
        specific_insights = self._extract_specific_insights(prospect, leak_result)
        
        # Generate content components
        subject_line = self._generate_subject_line(prospect, target_role, specific_insights)
        opening_hook = self._generate_opening_hook(prospect, target_role, priority_score)
        value_proposition = self._generate_value_proposition(prospect, target_role, specific_insights)
        call_to_action = self._generate_call_to_action(prospect, target_role)
        
        # Generate technical talking points
        technical_points = self._get_technical_talking_points(prospect, leak_result)
        
        # Calculate ROI projections
        roi_projections = self._calculate_roi_projections(prospect, leak_result)
        
        # Identify urgency factors
        urgency_factors = self._identify_urgency_factors(prospect, priority_score)
        
        # Get decision maker context
        dm_context = self._get_decision_maker_context(prospect, target_role)
        
        outreach_content = OutreachContent(
            subject_line=subject_line,
            opening_hook=opening_hook,
            value_proposition=value_proposition,
            specific_insights=specific_insights,
            call_to_action=call_to_action,
            decision_maker_context=dm_context,
            technical_talking_points=technical_points,
            roi_projections=roi_projections,
            urgency_factors=urgency_factors
        )
        
        logger.info(f"Generated personalized outreach for {prospect.company_name} targeting {target_role}")
        return outreach_content

    def _determine_target_role(self, prospect: Prospect, priority_score: Optional[PriorityScore]) -> str:
        """Determine the best decision maker role to target."""
        employee_count = getattr(prospect, 'employee_count', 0)
        industry = getattr(prospect, 'industry', '').lower()
        
        # Check if we have specific decision maker emails
        if hasattr(prospect, 'decision_maker_emails') and prospect.decision_maker_emails:
            for email in prospect.decision_maker_emails:
                if 'cto' in email.lower():
                    return 'cto'
                elif 'ceo' in email.lower():
                    return 'ceo'
                elif 'cmo' in email.lower():
                    return 'cmo'
        
        # Determine based on company size and industry
        if employee_count <= 50:
            return 'ceo'  # Smaller companies - go to the top
        elif employee_count <= 200:
            if 'ecommerce' in industry or 'retail' in industry:
                return 'cmo'  # Marketing-focused for ecommerce
            else:
                return 'cto'  # Technical for SaaS/tech
        else:
            return 'cto'  # Larger companies - technical decision maker

    def _get_industry_context(self, prospect: Prospect) -> Dict[str, Any]:
        """Get industry-specific context for messaging."""
        industry = getattr(prospect, 'industry', 'software').lower()
        
        # Map similar industries
        if any(ind in industry for ind in ['saas', 'software', 'technology']):
            industry_key = 'saas'
        elif any(ind in industry for ind in ['ecommerce', 'retail']):
            industry_key = 'ecommerce'
        elif any(ind in industry for ind in ['fintech', 'financial']):
            industry_key = 'fintech'
        else:
            industry_key = 'saas'  # Default
        
        return self.industry_messaging.get(industry_key, self.industry_messaging['saas'])

    def _extract_specific_insights(self, prospect: Prospect, leak_result: Optional[LeakResult]) -> List[str]:
        """Extract specific, actionable insights about the prospect."""
        insights = []
        
        # Marketing data insights
        if hasattr(prospect, 'marketing_data') and prospect.marketing_data:
            md = prospect.marketing_data
            
            if hasattr(md, 'web_vitals') and md.web_vitals:
                if md.web_vitals.lcp > 2.5:
                    improvement = (md.web_vitals.lcp - 2.5) * 7  # 7% per second
                    insights.append(f"Page speed optimization could improve conversions by {improvement:.1f}%")
                
                if md.web_vitals.cls > 0.1:
                    insights.append("Layout shift issues are likely causing user frustration and abandonment")
            
            if hasattr(md, 'bounce_rate') and md.bounce_rate and md.bounce_rate > 0.55:
                insights.append(f"High bounce rate ({md.bounce_rate:.1%}) indicates UX optimization opportunity")
            
            if hasattr(md, 'paid_traffic_share') and md.paid_traffic_share and md.paid_traffic_share > 0.4:
                insights.append("Heavy reliance on paid traffic - SEO optimization could reduce acquisition costs")
        
        # Technology stack insights
        technologies = getattr(prospect, 'technologies', [])
        if technologies:
            legacy_tech = ['jquery', 'php', 'mysql', 'apache', 'wordpress']
            modern_tech = ['react', 'vue', 'node.js', 'kubernetes', 'aws', 'google cloud']
            
            legacy_count = sum(1 for tech in technologies if any(leg in tech.lower() for leg in legacy_tech))
            modern_count = sum(1 for tech in technologies if any(mod in tech.lower() for mod in modern_tech))
            
            if legacy_count > modern_count:
                insights.append("Technology stack modernization could improve development velocity")
            
            if 'kubernetes' in [t.lower() for t in technologies]:
                insights.append("Kubernetes infrastructure suggests sophisticated scaling needs")
        
        # Growth indicators
        if hasattr(prospect, 'job_postings_count') and prospect.job_postings_count > 10:
            insights.append(f"Active hiring ({prospect.job_postings_count} open positions) indicates rapid scaling")
        
        if hasattr(prospect, 'traffic_growth_rate') and prospect.traffic_growth_rate > 0.3:
            insights.append(f"High traffic growth ({prospect.traffic_growth_rate:.0%}) creates scaling challenges")
        
        return insights[:3]  # Limit to top 3 most relevant insights

    def _generate_subject_line(self, prospect: Prospect, target_role: str, insights: List[str]) -> str:
        """Generate a personalized subject line."""
        industry = getattr(prospect, 'industry', 'software').lower()
        company_name = prospect.company_name
        
        # Get industry-specific templates
        if 'saas' in industry or 'software' in industry:
            industry_key = 'saas'
        elif 'ecommerce' in industry:
            industry_key = 'ecommerce'
        elif 'fintech' in industry:
            industry_key = 'fintech'
        else:
            industry_key = 'saas'
        
        templates = self.templates.get(industry_key, {}).get(target_role, {}).get('subject_templates', [
            "Quick question about {company_name}",
            "Helping {company_name} optimize performance"
        ])
        
        # Choose template and personalize
        template = random.choice(templates)
        
        # Get key technology for personalization
        technologies = getattr(prospect, 'technologies', [])
        key_technology = technologies[0] if technologies else "your tech stack"
        
        # Get funding stage
        funding_stage = getattr(prospect, 'funding_stage', 'recent growth')
        
        return template.format(
            company_name=company_name,
            key_technology=key_technology,
            funding_stage=funding_stage
        )

    def _generate_opening_hook(self, prospect: Prospect, target_role: str, priority_score: Optional[PriorityScore]) -> str:
        """Generate a personalized opening hook."""
        industry = getattr(prospect, 'industry', 'software').lower()
        company_name = prospect.company_name
        employee_count = getattr(prospect, 'employee_count', 0)
        
        # Map industry for templates
        if 'saas' in industry or 'software' in industry:
            industry_key = 'saas'
        elif 'ecommerce' in industry:
            industry_key = 'ecommerce'
        elif 'fintech' in industry:
            industry_key = 'fintech'
        else:
            industry_key = 'saas'
        
        hooks = self.templates.get(industry_key, {}).get(target_role, {}).get('opening_hooks', [
            "I noticed {company_name} is growing rapidly in the {industry} space."
        ])
        
        hook_template = random.choice(hooks)
        
        # Get personalization data
        funding_stage = getattr(prospect, 'funding_stage', 'growth phase')
        technologies = getattr(prospect, 'technologies', [])
        key_technology = technologies[0] if technologies else "modern tech stack"
        
        return hook_template.format(
            company_name=company_name,
            industry=industry,
            employee_count=employee_count,
            funding_stage=funding_stage,
            key_technology=key_technology
        )

    def _generate_value_proposition(self, prospect: Prospect, target_role: str, insights: List[str]) -> str:
        """Generate a value proposition based on specific insights."""
        industry = getattr(prospect, 'industry', 'software').lower()
        
        # Map industry
        if 'saas' in industry or 'software' in industry:
            industry_key = 'saas'
        elif 'ecommerce' in industry:
            industry_key = 'ecommerce'
        elif 'fintech' in industry:
            industry_key = 'fintech'
        else:
            industry_key = 'saas'
        
        value_props = self.templates.get(industry_key, {}).get(target_role, {}).get('value_props', [
            "improve performance and user experience"
        ])
        
        base_value_prop = random.choice(value_props)
        
        # Add specific insight if available
        if insights:
            specific_insight = insights[0]  # Use the most relevant insight
            return f"I believe we can help {prospect.company_name} {base_value_prop}. Specifically, {specific_insight.lower()}."
        else:
            return f"I believe we can help {prospect.company_name} {base_value_prop}."

    def _generate_call_to_action(self, prospect: Prospect, target_role: str) -> str:
        """Generate an appropriate call to action."""
        cta_options = [
            "Would you be open to a brief 15-minute conversation about this?",
            "Are you available for a quick call this week to discuss?",
            "Would it make sense to schedule a brief call to explore this further?",
            "Could we set up a short conversation to discuss how this might apply to your situation?"
        ]
        
        return random.choice(cta_options)

    def _get_technical_talking_points(self, prospect: Prospect, leak_result: Optional[LeakResult]) -> List[str]:
        """Generate technical talking points based on prospect's stack and issues."""
        talking_points = []
        
        technologies = getattr(prospect, 'technologies', [])
        tech_lower = [t.lower() for t in technologies]
        
        # Technology-specific talking points
        if any('kubernetes' in t for t in tech_lower):
            talking_points.append("Kubernetes optimization and resource efficiency")
        
        if any('aws' in t for t in tech_lower):
            talking_points.append("AWS cost optimization and performance tuning")
        
        if any('react' in t for t in tech_lower):
            talking_points.append("React application performance and bundle optimization")
        
        if any('node' in t for t in tech_lower):
            talking_points.append("Node.js performance optimization and scaling")
        
        # Marketing data talking points
        if hasattr(prospect, 'marketing_data') and prospect.marketing_data:
            md = prospect.marketing_data
            if hasattr(md, 'web_vitals') and md.web_vitals:
                if md.web_vitals.lcp > 2.5:
                    talking_points.append("Core Web Vitals optimization for better SEO and conversions")
                if md.web_vitals.cls > 0.1:
                    talking_points.append("Layout stability improvements to reduce user frustration")
        
        return talking_points[:4]  # Limit to top 4 points

    def _calculate_roi_projections(self, prospect: Prospect, leak_result: Optional[LeakResult]) -> Dict[str, Any]:
        """Calculate potential ROI projections."""
        projections = {
            "monthly_savings": 0,
            "annual_savings": 0,
            "conversion_improvement": 0,
            "confidence_level": "medium"
        }
        
        # Base calculations on company size and industry
        revenue = getattr(prospect, 'revenue', 0)
        employee_count = getattr(prospect, 'employee_count', 0)
        
        if revenue > 0:
            # Conservative estimate: 0.5-2% revenue improvement
            monthly_revenue = revenue / 12
            improvement_percentage = 0.01  # 1% conservative estimate
            
            projections["monthly_savings"] = monthly_revenue * improvement_percentage
            projections["annual_savings"] = projections["monthly_savings"] * 12
        
        # Marketing data specific projections
        if hasattr(prospect, 'marketing_data') and prospect.marketing_data:
            md = prospect.marketing_data
            if hasattr(md, 'web_vitals') and md.web_vitals and md.web_vitals.lcp > 2.5:
                # Speed improvement projections
                speed_improvement = (md.web_vitals.lcp - 2.5) * 0.07  # 7% per second
                projections["conversion_improvement"] = speed_improvement
                projections["confidence_level"] = "high"
        
        return projections

    def _identify_urgency_factors(self, prospect: Prospect, priority_score: Optional[PriorityScore]) -> List[str]:
        """Identify factors that create urgency for the prospect."""
        urgency_factors = []
        
        # Recent funding
        if hasattr(prospect, 'last_funding_date') and prospect.last_funding_date:
            days_since_funding = (datetime.now() - prospect.last_funding_date).days
            if days_since_funding <= 180:
                urgency_factors.append("Recent funding provides budget for optimization initiatives")
        
        # High growth
        if hasattr(prospect, 'traffic_growth_rate') and prospect.traffic_growth_rate > 0.3:
            urgency_factors.append("Rapid growth creating scaling challenges that need immediate attention")
        
        # Active hiring
        if hasattr(prospect, 'job_postings_count') and prospect.job_postings_count > 10:
            urgency_factors.append("Active hiring indicates need to optimize team productivity")
        
        # Performance issues
        if hasattr(prospect, 'marketing_data') and prospect.marketing_data:
            md = prospect.marketing_data
            if hasattr(md, 'web_vitals') and md.web_vitals and md.web_vitals.lcp > 3.0:
                urgency_factors.append("Performance issues directly impacting customer experience and revenue")
        
        return urgency_factors

    def _get_decision_maker_context(self, prospect: Prospect, target_role: str) -> str:
        """Get context about the decision maker and their priorities."""
        industry = getattr(prospect, 'industry', '').lower()
        employee_count = getattr(prospect, 'employee_count', 0)
        
        if target_role == 'cto':
            if employee_count <= 50:
                return "As CTO of a growing company, you're likely balancing technical debt with feature development."
            else:
                return "As CTO, you're focused on scaling engineering efficiency and maintaining system reliability."
        
        elif target_role == 'ceo':
            return "As CEO, you're focused on growth metrics, customer satisfaction, and operational efficiency."
        
        elif target_role == 'cmo':
            return "As CMO, you're focused on conversion optimization, customer acquisition costs, and marketing ROI."
        
        return "As a key decision maker, you're focused on driving growth while maintaining operational efficiency."

    def format_email(self, outreach_content: OutreachContent, prospect: Prospect) -> str:
        """Format the outreach content into a complete email."""
        email_parts = [
            f"Subject: {outreach_content.subject_line}",
            "",
            f"Hi there,",
            "",
            outreach_content.opening_hook,
            "",
            outreach_content.value_proposition,
            ""
        ]
        
        # Add specific insights
        if outreach_content.specific_insights:
            email_parts.append("Based on my research, I noticed a few areas where we might be able to help:")
            for insight in outreach_content.specific_insights:
                email_parts.append(f"• {insight}")
            email_parts.append("")
        
        # Add ROI projection if significant
        if outreach_content.roi_projections.get("monthly_savings", 0) > 1000:
            monthly_savings = outreach_content.roi_projections["monthly_savings"]
            email_parts.append(f"This could potentially save ${monthly_savings:,.0f}+ per month in improved efficiency and conversions.")
            email_parts.append("")
        
        # Add call to action
        email_parts.append(outreach_content.call_to_action)
        email_parts.append("")
        email_parts.append("Best regards,")
        email_parts.append("[Your Name]")
        
        return "\n".join(email_parts)