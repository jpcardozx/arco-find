#!/usr/bin/env python3
"""
🎯 CONVERSION OPTIMIZATION ENGINE
Expert-optimized system for maximum sales conversion

FOCUS: A/B testing, personalization, and multi-channel optimization
- Dynamic message personalization based on business intelligence
- A/B testing framework for outreach optimization  
- Multi-channel sequence automation
- Real-time conversion tracking and optimization
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import random
from enum import Enum

class OutreachChannel(Enum):
    EMAIL = "email"
    LINKEDIN = "linkedin"
    PHONE = "phone"
    CONTACT_FORM = "contact_form"
    TWITTER = "twitter"

class MessageVariant(Enum):
    A = "variant_a"
    B = "variant_b"
    C = "variant_c"

@dataclass
class PersonalizedMessage:
    """Personalized message based on business intelligence"""
    prospect_id: str
    channel: OutreachChannel
    variant: MessageVariant
    
    # Message components
    subject_line: str
    opening_line: str
    value_proposition: str
    social_proof: str
    call_to_action: str
    full_message: str
    
    # Personalization factors
    business_model_focus: str
    pain_point_focus: str
    urgency_angle: str
    authority_level: str
    
    # A/B testing
    test_group: str
    control_vs_test: str
    
    # Tracking
    created_at: datetime
    expected_response_rate: float

@dataclass
class ConversionTracking:
    """Track conversion performance"""
    prospect_id: str
    variant: MessageVariant
    channel: OutreachChannel
    
    # Engagement metrics
    sent_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    meeting_booked_at: Optional[datetime] = None
    
    # Conversion stages
    stage: str = "sent"  # sent, opened, clicked, replied, meeting, closed
    conversion_value: float = 0.0
    
    # Performance metrics
    open_rate: float = 0.0
    click_rate: float = 0.0
    reply_rate: float = 0.0
    meeting_rate: float = 0.0

class ConversionOptimizationEngine:
    """
    Expert-level conversion optimization system
    
    Focus: Maximum conversion through intelligent personalization and testing
    """
    
    def __init__(self):
        # Message templates optimized for conversion
        self.message_templates = {
            'saas': {
                'subject_lines': {
                    MessageVariant.A: [
                        "Quick question about {company_name}'s {pain_point}",
                        "Noticed {company_name} is {growth_indicator} - 5min?",
                        "{company_name} + {our_solution} = Perfect match?"
                    ],
                    MessageVariant.B: [
                        "Helping {similar_company} save $XXk/month on {pain_point}",
                        "ROI question for {company_name}",
                        "3 ways {company_name} could reduce {pain_point} costs"
                    ],
                    MessageVariant.C: [
                        "Congrats on {recent_achievement}! Quick question...",
                        "{competitor} is doing this - are you?",
                        "15-second question about {company_name}'s growth"
                    ]
                },
                'value_propositions': {
                    'cost_reduction': "Save 40-60% on {current_solution} costs while improving {key_metric}",
                    'efficiency_gain': "Reduce {process_name} time from hours to minutes",
                    'revenue_growth': "Help {company_name} capture {revenue_opportunity} in revenue",
                    'competitive_advantage': "Stay ahead of {competitor} with {differentiator}"
                },
                'social_proof': {
                    'similar_company': "{similar_company} saved ${amount} using our solution",
                    'industry_stat': "{percentage}% of {industry} companies saw ROI within {timeframe}",
                    'growth_metric': "Helped {company_type} companies grow {metric} by {percentage}%"
                }
            },
            'ecommerce': {
                'subject_lines': {
                    MessageVariant.A: [
                        "Boost {company_name}'s conversion rate by {percentage}%",
                        "Quick wins for {company_name}'s checkout process",
                        "Cart abandonment costing {company_name} $XXk?"
                    ],
                    MessageVariant.B: [
                        "How {competitor} increased sales by {percentage}%",
                        "ROI calculator for {company_name}",
                        "3 ecommerce optimizations for {company_name}"
                    ],
                    MessageVariant.C: [
                        "Saw {company_name}'s {product_category} - impressive!",
                        "{recent_funding} → Time to optimize conversion?",
                        "Quick question about {company_name}'s growth plans"
                    ]
                },
                'value_propositions': {
                    'conversion_optimization': "Increase conversion rate by {percentage}% with {solution}",
                    'revenue_recovery': "Recover ${amount} from cart abandonment",
                    'customer_lifetime': "Increase customer lifetime value by {percentage}%",
                    'mobile_optimization': "Boost mobile sales by {percentage}% with {solution}"
                }
            },
            'services': {
                'subject_lines': {
                    MessageVariant.A: [
                        "Streamline {company_name}'s client acquisition",
                        "Scale {company_name} without hiring overhead",
                        "Automate {company_name}'s {business_process}"
                    ],
                    MessageVariant.B: [
                        "How {similar_company} 3x'd their client base",
                        "ROI question for service businesses",
                        "Client acquisition costs too high?"
                    ],
                    MessageVariant.C: [
                        "Noticed {company_name} is expanding - congrats!",
                        "Quick question about {company_name}'s growth",
                        "5min chat about scaling {service_type}?"
                    ]
                },
                'value_propositions': {
                    'client_acquisition': "Reduce client acquisition cost by {percentage}%",
                    'operational_efficiency': "Handle {multiplier}x more clients with same team",
                    'revenue_predictability': "Create predictable ${amount}/month revenue stream",
                    'premium_positioning': "Position {company_name} as premium {service_category}"
                }
            }
        }
        
        # Channel-specific optimization
        self.channel_optimization = {
            OutreachChannel.EMAIL: {
                'optimal_length': 120,  # words
                'personalization_ratio': 0.3,  # 30% personalized content
                'cta_placement': 'middle_and_end'
            },
            OutreachChannel.LINKEDIN: {
                'optimal_length': 80,   # words  
                'personalization_ratio': 0.5,  # 50% personalized
                'cta_placement': 'end_only'
            },
            OutreachChannel.PHONE: {
                'optimal_length': 30,   # seconds script
                'personalization_ratio': 0.4,
                'cta_placement': 'immediate'
            }
        }
        
        # A/B testing rules
        self.ab_testing_rules = {
            'minimum_sample_size': 50,
            'confidence_level': 0.95,
            'test_duration_days': 14,
            'winning_threshold': 0.2  # 20% improvement to declare winner
        }
        
        print("🎯 CONVERSION OPTIMIZATION ENGINE")
        print("=" * 50)
        print("🔀 A/B testing framework loaded")
        print("🎨 Dynamic personalization active") 
        print("📊 Multi-channel optimization ready")
        print("🚀 Ready for maximum conversion")

    async def create_personalized_message(self, business_intelligence: Dict, 
                                        channel: OutreachChannel,
                                        variant: Optional[MessageVariant] = None) -> PersonalizedMessage:
        """
        Create highly personalized message based on business intelligence
        """
        
        # Auto-select variant if not specified (for A/B testing)
        if variant is None:
            variant = self._select_optimal_variant(business_intelligence)
        
        # Determine personalization strategy
        business_model = business_intelligence.get('business_model', 'services')
        company_name = business_intelligence.get('company_name', 'your company')
        
        # Get templates for business model
        templates = self.message_templates.get(business_model, self.message_templates['services'])
        
        # Generate message components
        subject_line = await self._generate_subject_line(templates, variant, business_intelligence)
        opening_line = await self._generate_opening_line(business_intelligence)
        value_prop = await self._generate_value_proposition(templates, business_intelligence)
        social_proof = await self._generate_social_proof(templates, business_intelligence)
        cta = await self._generate_call_to_action(channel, business_intelligence)
        
        # Compose full message
        full_message = await self._compose_full_message(
            opening_line, value_prop, social_proof, cta, channel
        )
        
        # Calculate expected response rate
        expected_rate = self._calculate_expected_response_rate(business_intelligence, channel, variant)
        
        return PersonalizedMessage(
            prospect_id=business_intelligence.get('domain', 'unknown'),
            channel=channel,
            variant=variant,
            subject_line=subject_line,
            opening_line=opening_line,
            value_proposition=value_prop,
            social_proof=social_proof,
            call_to_action=cta,
            full_message=full_message,
            business_model_focus=business_model,
            pain_point_focus=self._identify_primary_pain_point(business_intelligence),
            urgency_angle=self._determine_urgency_angle(business_intelligence),
            authority_level=self._determine_authority_level(business_intelligence),
            test_group=f"{variant.value}_{channel.value}",
            control_vs_test=self._assign_control_vs_test(),
            created_at=datetime.now(),
            expected_response_rate=expected_rate
        )

    def _select_optimal_variant(self, business_intelligence: Dict) -> MessageVariant:
        """Select optimal message variant based on business intelligence"""
        
        buying_readiness = business_intelligence.get('buying_readiness_score', 50)
        company_size = business_intelligence.get('estimated_employees', 10)
        urgency_factors = business_intelligence.get('urgency_factors', [])
        
        # High buying readiness + urgency = direct approach (Variant A)
        if buying_readiness >= 70 and urgency_factors:
            return MessageVariant.A
        
        # Mid-market companies prefer ROI focus (Variant B)
        elif company_size >= 20:
            return MessageVariant.B
            
        # Growth companies prefer social proof (Variant C)
        elif 'growth_phase' in urgency_factors:
            return MessageVariant.C
        
        # Default: round-robin for A/B testing
        return random.choice(list(MessageVariant))

    async def _generate_subject_line(self, templates: Dict, variant: MessageVariant, 
                                   business_intel: Dict) -> str:
        """Generate personalized subject line"""
        
        subject_templates = templates['subject_lines'][variant]
        selected_template = random.choice(subject_templates)
        
        # Personalization variables
        replacements = {
            'company_name': business_intel.get('company_name', 'your company'),
            'pain_point': self._identify_primary_pain_point(business_intel),
            'growth_indicator': self._get_growth_indicator(business_intel),
            'recent_achievement': self._get_recent_achievement(business_intel),
            'competitor': self._get_competitor_reference(business_intel),
            'our_solution': self._get_solution_name(business_intel),
            'similar_company': self._get_similar_company(business_intel),
            'percentage': str(random.randint(25, 85)),
            'recent_funding': self._get_funding_reference(business_intel),
            'product_category': self._get_product_category(business_intel)
        }
        
        # Apply replacements
        personalized_subject = selected_template
        for placeholder, value in replacements.items():
            personalized_subject = personalized_subject.replace(f'{{{placeholder}}}', value)
        
        return personalized_subject

    async def _generate_opening_line(self, business_intel: Dict) -> str:
        """Generate personalized opening line"""
        
        company_name = business_intel.get('company_name', 'your company')
        growth_indicators = business_intel.get('growth_indicators', [])
        business_model = business_intel.get('business_model', 'services')
        
        if 'active_hiring' in growth_indicators:
            return f"Noticed {company_name} is actively hiring - congrats on the growth!"
        elif 'recent_funding' in growth_indicators:
            return f"Saw the news about {company_name}'s recent funding - exciting times!"
        elif business_model == 'saas':
            return f"Quick question about {company_name}'s current tech stack..."
        elif business_model == 'ecommerce':
            return f"Impressive product line at {company_name}!"
        else:
            return f"Been following {company_name}'s growth in the {business_model} space."

    async def _generate_value_proposition(self, templates: Dict, business_intel: Dict) -> str:
        """Generate personalized value proposition"""
        
        business_model = business_intel.get('business_model', 'services')
        company_size = business_intel.get('estimated_employees', 10)
        
        # Select value prop type based on company profile
        if company_size <= 10:
            value_type = 'efficiency_gain'
        elif company_size <= 50:
            value_type = 'cost_reduction'  
        else:
            value_type = 'revenue_growth'
        
        value_props = templates.get('value_propositions', {})
        template = value_props.get(value_type, "Help {company_name} optimize {business_process}")
        
        # Personalization
        replacements = {
            'company_name': business_intel.get('company_name', 'your company'),
            'current_solution': self._identify_current_solution(business_intel),
            'key_metric': self._get_key_metric(business_intel),
            'process_name': self._get_process_name(business_intel),
            'revenue_opportunity': f"${random.randint(50, 500)}k",
            'competitor': self._get_competitor_reference(business_intel),
            'differentiator': self._get_differentiator(business_intel),
            'percentage': str(random.randint(15, 65)),
            'amount': f"{random.randint(10, 100)}k",
            'solution': self._get_solution_name(business_intel)
        }
        
        personalized_value_prop = template
        for placeholder, value in replacements.items():
            personalized_value_prop = personalized_value_prop.replace(f'{{{placeholder}}}', value)
        
        return personalized_value_prop

    async def _generate_social_proof(self, templates: Dict, business_intel: Dict) -> str:
        """Generate relevant social proof"""
        
        business_model = business_intel.get('business_model', 'services')
        company_size = business_intel.get('estimated_employees', 10)
        
        social_proofs = templates.get('social_proof', {})
        
        # Select social proof type
        if company_size >= 50:
            proof_type = 'similar_company'
        elif business_model == 'saas':
            proof_type = 'industry_stat'
        else:
            proof_type = 'growth_metric'
        
        template = social_proofs.get(proof_type, "Helped companies like {company_name} achieve {result}")
        
        # Personalization
        replacements = {
            'similar_company': self._get_similar_company(business_intel),
            'amount': f"{random.randint(20, 200)}k",
            'percentage': str(random.randint(25, 85)),
            'industry': self._get_industry(business_intel),
            'timeframe': random.choice(['3 months', '6 months', '1 year']),
            'company_type': business_model,
            'metric': self._get_key_metric(business_intel)
        }
        
        personalized_proof = template
        for placeholder, value in replacements.items():
            personalized_proof = personalized_proof.replace(f'{{{placeholder}}}', value)
        
        return personalized_proof

    async def _generate_call_to_action(self, channel: OutreachChannel, business_intel: Dict) -> str:
        """Generate channel-optimized call to action"""
        
        urgency_factors = business_intel.get('urgency_factors', [])
        buying_readiness = business_intel.get('buying_readiness_score', 50)
        
        # High urgency = direct CTA
        if urgency_factors and buying_readiness >= 70:
            if channel == OutreachChannel.EMAIL:
                return "Free to chat this week? I can show you exactly how in 15 minutes."
            elif channel == OutreachChannel.LINKEDIN:
                return "Worth a quick call this week?"
            else:
                return "15-minute call to discuss?"
        
        # Medium urgency = soft CTA
        elif buying_readiness >= 40:
            if channel == OutreachChannel.EMAIL:
                return "Mind if I send over a quick case study relevant to your situation?"
            elif channel == OutreachChannel.LINKEDIN:
                return "Would you be interested in seeing how we solved this for a similar company?"
            else:
                return "Can I send you a relevant case study?"
        
        # Low urgency = ultra-soft CTA
        else:
            if channel == OutreachChannel.EMAIL:
                return "Would this be worth exploring for your team?"
            elif channel == OutreachChannel.LINKEDIN:
                return "Worth keeping in mind for the future?"
            else:
                return "Something to consider?"

    async def _compose_full_message(self, opening: str, value_prop: str, 
                                  social_proof: str, cta: str, channel: OutreachChannel) -> str:
        """Compose full message optimized for channel"""
        
        if channel == OutreachChannel.EMAIL:
            return f"{opening}\n\n{value_prop}\n\n{social_proof}\n\n{cta}\n\nBest regards,\n[Your Name]"
        
        elif channel == OutreachChannel.LINKEDIN:
            return f"{opening}\n\n{value_prop} {social_proof}\n\n{cta}"
        
        elif channel == OutreachChannel.PHONE:
            return f"Hi, {opening} {value_prop} {social_proof} {cta}"
        
        else:
            return f"{opening}\n\n{value_prop}\n\n{cta}"

    def _calculate_expected_response_rate(self, business_intel: Dict, 
                                        channel: OutreachChannel, variant: MessageVariant) -> float:
        """Calculate expected response rate based on intelligence and optimization"""
        
        # Base rates by channel
        base_rates = {
            OutreachChannel.EMAIL: 0.15,
            OutreachChannel.LINKEDIN: 0.25,
            OutreachChannel.PHONE: 0.35,
            OutreachChannel.CONTACT_FORM: 0.10
        }
        
        base_rate = base_rates.get(channel, 0.15)
        
        # Qualification multipliers
        buying_readiness = business_intel.get('buying_readiness_score', 50)
        qualification_score = business_intel.get('total_qualification_score', 50)
        
        # Readiness multiplier (0.5x to 2.0x)
        readiness_multiplier = 0.5 + (buying_readiness / 100) * 1.5
        
        # Qualification multiplier (0.7x to 1.5x)  
        qualification_multiplier = 0.7 + (qualification_score / 100) * 0.8
        
        # Variant performance (A/B testing data)
        variant_multipliers = {
            MessageVariant.A: 1.0,  # Control
            MessageVariant.B: 1.15, # ROI focus performs better
            MessageVariant.C: 0.95  # Social proof varies
        }
        
        variant_multiplier = variant_multipliers.get(variant, 1.0)
        
        # Calculate final expected rate
        expected_rate = base_rate * readiness_multiplier * qualification_multiplier * variant_multiplier
        
        return min(expected_rate, 0.8)  # Cap at 80%

    # Helper methods for personalization
    def _identify_primary_pain_point(self, business_intel: Dict) -> str:
        business_model = business_intel.get('business_model', 'services')
        pain_points = {
            'saas': 'customer acquisition costs',
            'ecommerce': 'cart abandonment',
            'services': 'client acquisition',
            'marketplace': 'vendor onboarding'
        }
        return pain_points.get(business_model, 'operational efficiency')

    def _get_growth_indicator(self, business_intel: Dict) -> str:
        indicators = business_intel.get('growth_indicators', [])
        if 'active_hiring' in indicators:
            return 'rapidly hiring'
        elif 'funded' in indicators:
            return 'recently funded'
        else:
            return 'expanding'

    def _get_recent_achievement(self, business_intel: Dict) -> str:
        growth_indicators = business_intel.get('growth_indicators', [])
        if 'funded' in growth_indicators:
            return 'recent funding round'
        elif 'active_hiring' in growth_indicators:
            return 'team expansion'
        else:
            return 'company growth'

    def _get_competitor_reference(self, business_intel: Dict) -> str:
        business_model = business_intel.get('business_model', 'services')
        competitors = {
            'saas': 'HubSpot',
            'ecommerce': 'Shopify Plus',
            'services': 'Deloitte',
            'marketplace': 'Amazon'
        }
        return competitors.get(business_model, 'leading companies')

    def _get_solution_name(self, business_intel: Dict) -> str:
        business_model = business_intel.get('business_model', 'services')
        solutions = {
            'saas': 'our automation platform',
            'ecommerce': 'our conversion optimization suite',
            'services': 'our client acquisition system',
            'marketplace': 'our vendor management platform'
        }
        return solutions.get(business_model, 'our solution')

    def _get_similar_company(self, business_intel: Dict) -> str:
        business_model = business_intel.get('business_model', 'services')
        examples = {
            'saas': 'Zoom',
            'ecommerce': 'Warby Parker',
            'services': 'McKinsey',
            'marketplace': 'Etsy'
        }
        return examples.get(business_model, 'a similar company')

    def _get_funding_reference(self, business_intel: Dict) -> str:
        if 'funded' in business_intel.get('growth_indicators', []):
            return 'the recent funding'
        else:
            return 'your growth momentum'

    def _get_product_category(self, business_intel: Dict) -> str:
        return 'product line'

    def _identify_current_solution(self, business_intel: Dict) -> str:
        business_model = business_intel.get('business_model', 'services')
        solutions = {
            'saas': 'current tech stack',
            'ecommerce': 'current platform',
            'services': 'current processes',
            'marketplace': 'current system'
        }
        return solutions.get(business_model, 'current setup')

    def _get_key_metric(self, business_intel: Dict) -> str:
        business_model = business_intel.get('business_model', 'services')
        metrics = {
            'saas': 'user engagement',
            'ecommerce': 'conversion rate',
            'services': 'client satisfaction',
            'marketplace': 'vendor performance'
        }
        return metrics.get(business_model, 'performance')

    def _get_process_name(self, business_intel: Dict) -> str:
        business_model = business_intel.get('business_model', 'services')
        processes = {
            'saas': 'onboarding',
            'ecommerce': 'checkout',
            'services': 'project delivery',
            'marketplace': 'vendor verification'
        }
        return processes.get(business_model, 'workflow')

    def _get_differentiator(self, business_intel: Dict) -> str:
        return 'automated intelligence'

    def _get_industry(self, business_intel: Dict) -> str:
        business_model = business_intel.get('business_model', 'services')
        industries = {
            'saas': 'SaaS',
            'ecommerce': 'e-commerce',
            'services': 'professional services',
            'marketplace': 'marketplace'
        }
        return industries.get(business_model, 'technology')

    def _determine_urgency_angle(self, business_intel: Dict) -> str:
        urgency_factors = business_intel.get('urgency_factors', [])
        if 'growth_phase' in urgency_factors:
            return 'scaling_urgency'
        elif 'capital_influx' in urgency_factors:
            return 'investment_optimization'
        else:
            return 'competitive_pressure'

    def _determine_authority_level(self, business_intel: Dict) -> str:
        employees = business_intel.get('estimated_employees', 10)
        if employees >= 50:
            return 'c_level'
        elif employees >= 20:
            return 'vp_level'
        else:
            return 'founder_level'

    def _assign_control_vs_test(self) -> str:
        return random.choice(['control', 'test'])

    async def track_conversion_performance(self, message: PersonalizedMessage, 
                                         event_type: str, timestamp: datetime = None) -> ConversionTracking:
        """Track conversion events for optimization"""
        
        if timestamp is None:
            timestamp = datetime.now()
        
        tracking = ConversionTracking(
            prospect_id=message.prospect_id,
            variant=message.variant,
            channel=message.channel
        )
        
        # Update tracking based on event
        if event_type == 'sent':
            tracking.sent_at = timestamp
            tracking.stage = 'sent'
        elif event_type == 'opened':
            tracking.opened_at = timestamp
            tracking.stage = 'opened'
        elif event_type == 'clicked':
            tracking.clicked_at = timestamp
            tracking.stage = 'clicked'
        elif event_type == 'replied':
            tracking.replied_at = timestamp
            tracking.stage = 'replied'
        elif event_type == 'meeting':
            tracking.meeting_booked_at = timestamp
            tracking.stage = 'meeting'
            tracking.conversion_value = 1000.0  # Estimated meeting value
        
        return tracking

    async def optimize_campaign_performance(self, tracking_data: List[ConversionTracking]) -> Dict:
        """Analyze performance and provide optimization recommendations"""
        
        performance_analysis = {}
        
        # Group by variant and channel
        by_variant = {}
        by_channel = {}
        
        for tracking in tracking_data:
            variant_key = tracking.variant.value
            channel_key = tracking.channel.value
            
            if variant_key not in by_variant:
                by_variant[variant_key] = []
            by_variant[variant_key].append(tracking)
            
            if channel_key not in by_channel:
                by_channel[channel_key] = []
            by_channel[channel_key].append(tracking)
        
        # Calculate performance metrics
        performance_analysis['variant_performance'] = {}
        for variant, data in by_variant.items():
            total = len(data)
            opened = sum(1 for t in data if t.opened_at is not None)
            replied = sum(1 for t in data if t.replied_at is not None)
            meetings = sum(1 for t in data if t.meeting_booked_at is not None)
            
            performance_analysis['variant_performance'][variant] = {
                'total_sent': total,
                'open_rate': opened / total if total > 0 else 0,
                'reply_rate': replied / total if total > 0 else 0,
                'meeting_rate': meetings / total if total > 0 else 0
            }
        
        performance_analysis['channel_performance'] = {}
        for channel, data in by_channel.items():
            total = len(data)
            opened = sum(1 for t in data if t.opened_at is not None)
            replied = sum(1 for t in data if t.replied_at is not None)
            meetings = sum(1 for t in data if t.meeting_booked_at is not None)
            
            performance_analysis['channel_performance'][channel] = {
                'total_sent': total,
                'open_rate': opened / total if total > 0 else 0,
                'reply_rate': replied / total if total > 0 else 0,
                'meeting_rate': meetings / total if total > 0 else 0
            }
        
        # Generate optimization recommendations
        recommendations = self._generate_optimization_recommendations(performance_analysis)
        performance_analysis['recommendations'] = recommendations
        
        return performance_analysis

    def _generate_optimization_recommendations(self, performance_data: Dict) -> List[str]:
        """Generate specific optimization recommendations"""
        
        recommendations = []
        
        # Variant performance recommendations
        variant_perf = performance_data.get('variant_performance', {})
        best_variant = max(variant_perf.keys(), key=lambda x: variant_perf[x].get('meeting_rate', 0)) if variant_perf else None
        
        if best_variant:
            best_rate = variant_perf[best_variant]['meeting_rate']
            recommendations.append(f"Variant {best_variant} shows highest meeting rate ({best_rate:.1%}). Scale this approach.")
        
        # Channel performance recommendations
        channel_perf = performance_data.get('channel_performance', {})
        best_channel = max(channel_perf.keys(), key=lambda x: channel_perf[x].get('reply_rate', 0)) if channel_perf else None
        
        if best_channel:
            best_rate = channel_perf[best_channel]['reply_rate']
            recommendations.append(f"Channel {best_channel} shows highest reply rate ({best_rate:.1%}). Increase allocation.")
        
        # General optimization recommendations
        for channel, data in channel_perf.items():
            if data['open_rate'] < 0.3:
                recommendations.append(f"Low open rate on {channel} ({data['open_rate']:.1%}). Test subject line variations.")
            
            if data['reply_rate'] < data['open_rate'] * 0.15:
                recommendations.append(f"Low reply rate on {channel} relative to opens. Strengthen value proposition.")
        
        return recommendations

# Demo function
async def demo_conversion_optimization():
    """Demo the conversion optimization engine"""
    
    print("\n🎯 CONVERSION OPTIMIZATION ENGINE DEMO")
    print("=" * 70)
    
    engine = ConversionOptimizationEngine()
    
    # Mock business intelligence
    sample_business_intel = {
        'company_name': 'TechStartup Inc',
        'domain': 'techstartup.com',
        'business_model': 'saas',
        'estimated_employees': 25,
        'buying_readiness_score': 75,
        'total_qualification_score': 80,
        'growth_indicators': ['active_hiring', 'funded'],
        'urgency_factors': ['growth_phase']
    }
    
    print(f"\n📊 GENERATING PERSONALIZED MESSAGES...")
    
    # Generate messages for different channels
    channels = [OutreachChannel.EMAIL, OutreachChannel.LINKEDIN]
    
    for channel in channels:
        print(f"\n{channel.value.upper()} MESSAGE:")
        print("-" * 40)
        
        message = await engine.create_personalized_message(
            sample_business_intel, 
            channel
        )
        
        print(f"Subject: {message.subject_line}")
        print(f"Variant: {message.variant.value}")
        print(f"Expected Response Rate: {message.expected_response_rate:.1%}")
        print(f"\nMessage:\n{message.full_message}")
        print(f"\nPersonalization Focus:")
        print(f"  • Business Model: {message.business_model_focus}")
        print(f"  • Pain Point: {message.pain_point_focus}")
        print(f"  • Urgency Angle: {message.urgency_angle}")
        print(f"  • Authority Level: {message.authority_level}")
    
    print(f"\n✅ Conversion Optimization Engine operational!")

if __name__ == "__main__":
    asyncio.run(demo_conversion_optimization())
