#!/usr/bin/env python3
"""
🎯 INTEGRATED CUSTOMER ACQUISITION PIPELINE
Expert-optimized end-to-end customer acquisition system

INTEGRATES:
- Enhanced Business Intelligence Engine
- Conversion Optimization Engine  
- Financial Signal Orchestrator
- Multi-channel outreach automation

FOCUS: Maximum ROI customer acquisition without retrabalho
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import sys

# Import our expert-optimized engines
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from enhanced_business_intelligence import EnhancedBusinessIntelligence, BusinessIntelligence
from conversion_optimization_engine import (
    ConversionOptimizationEngine, 
    PersonalizedMessage, 
    ConversionTracking,
    OutreachChannel,
    MessageVariant
)
from financial_signal_orchestrator import FinancialSignalOrchestrator

@dataclass
class CustomerAcquisitionResult:
    """Complete customer acquisition pipeline result"""
    prospect_id: str
    domain: str
    
    # Intelligence Layer
    business_intelligence: BusinessIntelligence
    financial_signals: Dict
    
    # Optimization Layer
    personalized_messages: List[PersonalizedMessage]
    recommended_sequence: List[Dict]
    
    # Performance Prediction
    total_qualification_score: int
    predicted_conversion_rate: float
    estimated_deal_value: float
    roi_projection: float
    
    # Next Actions
    immediate_actions: List[str]
    recommended_timeline: Dict
    priority_level: str  # 'high', 'medium', 'low'
    
    # Metadata
    processed_at: datetime
    processing_time_seconds: float

class IntegratedCustomerAcquisition:
    """
    Expert-level integrated customer acquisition system
    
    Combines all optimization engines for maximum conversion ROI
    """
    
    def __init__(self):
        # Initialize expert engines
        self.business_intel = EnhancedBusinessIntelligence()
        self.conversion_optimizer = ConversionOptimizationEngine()
        self.financial_orchestrator = FinancialSignalOrchestrator()
        
        # Performance tracking
        self.performance_history = []
        self.optimization_metrics = {
            'total_prospects_processed': 0,
            'high_quality_prospects': 0,
            'conversion_rate': 0.0,
            'average_deal_value': 0.0,
            'roi_improvement': 0.0
        }
        
        # Multi-channel sequence templates
        self.sequence_templates = {
            'high_priority': {
                'channels': [OutreachChannel.LINKEDIN, OutreachChannel.EMAIL, OutreachChannel.PHONE],
                'timing': [0, 3, 7],  # days
                'variants': [MessageVariant.A, MessageVariant.B, MessageVariant.A]
            },
            'medium_priority': {
                'channels': [OutreachChannel.EMAIL, OutreachChannel.LINKEDIN],
                'timing': [0, 5],
                'variants': [MessageVariant.B, MessageVariant.C]
            },
            'low_priority': {
                'channels': [OutreachChannel.EMAIL],
                'timing': [0],
                'variants': [MessageVariant.C]
            }
        }
        
        print("🎯 INTEGRATED CUSTOMER ACQUISITION PIPELINE")
        print("=" * 60)
        print("🧠 Enhanced Business Intelligence: ✅")
        print("⚡ Conversion Optimization Engine: ✅")
        print("💰 Financial Signal Orchestrator: ✅") 
        print("🚀 Ready for expert-level customer acquisition")

    async def process_prospect_complete(self, domain: str) -> CustomerAcquisitionResult:
        """
        Complete customer acquisition pipeline processing
        Expert-optimized for maximum conversion ROI
        """
        
        start_time = datetime.now()
        print(f"\n🎯 PROCESSING PROSPECT: {domain}")
        print("=" * 50)
        
        try:
            # PHASE 1: Intelligence Gathering (Parallel)
            print("📊 Phase 1: Intelligence Gathering...")
            intelligence_tasks = [
                self.business_intel.analyze_comprehensive_business_intelligence(domain),
                self.financial_orchestrator.process_domain_financial_cascade(domain)
            ]
            
            intelligence_results = await asyncio.gather(*intelligence_tasks, return_exceptions=True)
            
            business_intelligence = intelligence_results[0] if not isinstance(intelligence_results[0], Exception) else None
            financial_signals_obj = intelligence_results[1] if not isinstance(intelligence_results[1], Exception) else None
            
            # Convert financial signals to dict format
            if financial_signals_obj:
                financial_signals = {
                    'revenue_leaks': [
                        {
                            'type': 'saas_optimization',
                            'monthly_cost': financial_signals_obj.saas_optimization_potential,
                            'potential_savings': financial_signals_obj.saas_optimization_potential
                        },
                        {
                            'type': 'performance_loss', 
                            'monthly_cost': financial_signals_obj.performance_loss,
                            'potential_savings': financial_signals_obj.performance_loss
                        }
                    ],
                    'total_monthly_cost': financial_signals_obj.saas_monthly_cost + financial_signals_obj.subscription_revenue,
                    'leak_score': financial_signals_obj.leak_score
                }
            else:
                financial_signals = {'revenue_leaks': [], 'total_monthly_cost': 0, 'leak_score': 0}
            
            if not business_intelligence:
                print(f"❌ Failed to gather business intelligence for {domain}")
                return self._create_failed_result(domain, start_time)
            
            print(f"   ✅ Business Intelligence: {business_intelligence.total_qualification_score}/100")
            print(f"   ✅ Financial Signals: {len(financial_signals.get('revenue_leaks', []))} signals detected")
            
            # PHASE 2: Conversion Optimization
            print("🎨 Phase 2: Conversion Optimization...")
            
            # Convert business intelligence to dict for conversion engine
            business_intel_dict = asdict(business_intelligence)
            
            # Determine optimal channel sequence
            priority_level = self._determine_priority_level(business_intelligence, financial_signals)
            sequence_template = self.sequence_templates[priority_level]
            
            # Generate personalized messages for sequence
            personalized_messages = []
            recommended_sequence = []
            
            for i, (channel, timing, variant) in enumerate(zip(
                sequence_template['channels'],
                sequence_template['timing'], 
                sequence_template['variants']
            )):
                message = await self.conversion_optimizer.create_personalized_message(
                    business_intel_dict, channel, variant
                )
                personalized_messages.append(message)
                
                recommended_sequence.append({
                    'step': i + 1,
                    'channel': channel.value,
                    'timing_days': timing,
                    'variant': variant.value,
                    'expected_response_rate': message.expected_response_rate,
                    'message_preview': message.subject_line[:50] + "..."
                })
            
            print(f"   ✅ Generated {len(personalized_messages)} optimized messages")
            print(f"   ✅ Sequence priority: {priority_level}")
            
            # PHASE 3: Performance Prediction & ROI Analysis
            print("📈 Phase 3: Performance Prediction...")
            
            predicted_conversion_rate = self._calculate_predicted_conversion_rate(
                business_intelligence, financial_signals, personalized_messages
            )
            
            estimated_deal_value = self._estimate_deal_value(
                business_intelligence, financial_signals
            )
            
            roi_projection = self._calculate_roi_projection(
                predicted_conversion_rate, estimated_deal_value, len(personalized_messages)
            )
            
            print(f"   ✅ Predicted conversion rate: {predicted_conversion_rate:.1%}")
            print(f"   ✅ Estimated deal value: ${estimated_deal_value:,.0f}")
            print(f"   ✅ ROI projection: {roi_projection:.1f}x")
            
            # PHASE 4: Action Planning
            print("🎯 Phase 4: Action Planning...")
            
            immediate_actions = self._generate_immediate_actions(
                business_intelligence, financial_signals, priority_level
            )
            
            recommended_timeline = self._create_timeline(sequence_template, immediate_actions)
            
            print(f"   ✅ {len(immediate_actions)} immediate actions identified")
            print(f"   ✅ {len(recommended_timeline)} timeline steps created")
            
            # Create complete result
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = CustomerAcquisitionResult(
                prospect_id=domain,
                domain=domain,
                business_intelligence=business_intelligence,
                financial_signals=financial_signals,
                personalized_messages=personalized_messages,
                recommended_sequence=recommended_sequence,
                total_qualification_score=business_intelligence.total_qualification_score,
                predicted_conversion_rate=predicted_conversion_rate,
                estimated_deal_value=estimated_deal_value,
                roi_projection=roi_projection,
                immediate_actions=immediate_actions,
                recommended_timeline=recommended_timeline,
                priority_level=priority_level,
                processed_at=datetime.now(),
                processing_time_seconds=processing_time
            )
            
            # Update performance tracking
            self._update_performance_metrics(result)
            
            print(f"\n✅ PROSPECT PROCESSING COMPLETE")
            print(f"   ⏱️  Processing time: {processing_time:.2f}s")
            print(f"   🎯 Priority level: {priority_level}")
            print(f"   📊 Qualification score: {business_intelligence.total_qualification_score}/100")
            print(f"   💰 Projected ROI: {roi_projection:.1f}x")
            
            return result
            
        except Exception as e:
            print(f"❌ Error processing prospect {domain}: {e}")
            return self._create_failed_result(domain, start_time)

    def _determine_priority_level(self, business_intel: BusinessIntelligence, 
                                financial_signals: Dict) -> str:
        """Determine prospect priority level for sequencing"""
        
        # Scoring factors
        qualification_score = business_intel.total_qualification_score
        buying_readiness = business_intel.buying_readiness_score
        revenue_leaks = len(financial_signals.get('revenue_leaks', []))
        urgency_factors = len(business_intel.urgency_factors)
        
        # Calculate priority score
        priority_score = (
            qualification_score * 0.4 +
            buying_readiness * 0.3 +
            revenue_leaks * 5 +  # Revenue leaks are high-value signals
            urgency_factors * 10  # Urgency factors boost priority
        )
        
        if priority_score >= 80:
            return 'high_priority'
        elif priority_score >= 50:
            return 'medium_priority'
        else:
            return 'low_priority'

    def _calculate_predicted_conversion_rate(self, business_intel: BusinessIntelligence,
                                           financial_signals: Dict, 
                                           messages: List[PersonalizedMessage]) -> float:
        """Calculate predicted conversion rate for the complete sequence"""
        
        # Base conversion rate from business intelligence
        base_rate = business_intel.conversion_probability
        
        # Sequence effectiveness multiplier
        sequence_length = len(messages)
        sequence_multiplier = 1 + (sequence_length - 1) * 0.15  # 15% boost per additional touchpoint
        
        # Financial signals boost (revenue leaks = buying urgency)
        financial_boost = len(financial_signals.get('revenue_leaks', [])) * 0.05
        
        # Message optimization boost
        avg_expected_rate = sum(msg.expected_response_rate for msg in messages) / len(messages)
        optimization_boost = avg_expected_rate * 0.3
        
        total_rate = base_rate * sequence_multiplier + financial_boost + optimization_boost
        
        return min(total_rate, 0.75)  # Cap at 75% to be realistic

    def _estimate_deal_value(self, business_intel: BusinessIntelligence, 
                           financial_signals: Dict) -> float:
        """Estimate potential deal value"""
        
        # Base deal value by company size and type
        company_size = business_intel.estimated_employees
        business_model = business_intel.business_model
        
        # Size-based multipliers
        if company_size >= 100:
            base_value = 50000
        elif company_size >= 50:
            base_value = 25000
        elif company_size >= 20:
            base_value = 15000
        else:
            base_value = 8000
        
        # Business model multipliers
        model_multipliers = {
            'saas': 1.5,
            'marketplace': 1.8,
            'ecommerce': 1.3,
            'services': 1.0
        }
        
        model_multiplier = model_multipliers.get(business_model, 1.0)
        
        # Revenue leak value (direct value proposition)
        revenue_leaks = financial_signals.get('revenue_leaks', [])
        leak_value = sum(leak.get('monthly_cost', 0) for leak in revenue_leaks) * 6  # 6 months value
        
        # Calculate total estimated value
        total_value = (base_value * model_multiplier) + leak_value
        
        return max(total_value, 5000)  # Minimum deal value

    def _calculate_roi_projection(self, conversion_rate: float, deal_value: float, 
                                sequence_length: int) -> float:
        """Calculate ROI projection for the acquisition sequence"""
        
        # Acquisition cost (time + tools)
        base_cost_per_touchpoint = 25  # $25 per message/call
        total_acquisition_cost = sequence_length * base_cost_per_touchpoint
        
        # Expected value
        expected_value = conversion_rate * deal_value
        
        # ROI calculation
        if total_acquisition_cost > 0:
            roi = expected_value / total_acquisition_cost
        else:
            roi = 0
        
        return max(roi, 0.1)  # Minimum 0.1x

    def _generate_immediate_actions(self, business_intel: BusinessIntelligence,
                                  financial_signals: Dict, priority_level: str) -> List[str]:
        """Generate immediate action items"""
        
        actions = []
        
        # Priority-based actions
        if priority_level == 'high_priority':
            actions.append("🚨 IMMEDIATE: Send LinkedIn connection request today")
            actions.append("📧 Schedule email sequence to start within 24 hours")
            actions.append("🔍 Research decision maker contact information")
            
        elif priority_level == 'medium_priority':
            actions.append("📧 Add to email nurture sequence")
            actions.append("🔍 Monitor for trigger events")
            
        else:
            actions.append("📚 Add to long-term nurture list")
        
        # Financial signals actions
        revenue_leaks = financial_signals.get('revenue_leaks', [])
        if revenue_leaks:
            actions.append(f"💰 Prepare revenue leak analysis ({len(revenue_leaks)} opportunities)")
        
        # Buying signals actions
        if business_intel.urgency_factors:
            urgency = ', '.join(business_intel.urgency_factors[:2])
            actions.append(f"⚡ Leverage urgency factors: {urgency}")
        
        # Company-specific actions
        if 'active_hiring' in business_intel.growth_indicators:
            actions.append("👥 Reference hiring growth in outreach")
        
        if 'funded' in business_intel.growth_indicators:
            actions.append("💸 Reference recent funding in messaging")
        
        return actions

    def _create_timeline(self, sequence_template: Dict, immediate_actions: List[str]) -> Dict:
        """Create recommended timeline for prospect engagement"""
        
        timeline = {}
        
        # Day 0 (Today)
        timeline['day_0'] = {
            'actions': immediate_actions[:3],  # Top 3 immediate actions
            'channels': [],
            'focus': 'Preparation and research'
        }
        
        # Sequence timeline
        for i, timing in enumerate(sequence_template['timing']):
            day_key = f"day_{timing}"
            channel = sequence_template['channels'][i]
            
            if day_key not in timeline:
                timeline[day_key] = {
                    'actions': [],
                    'channels': [],
                    'focus': ''
                }
            
            timeline[day_key]['channels'].append(channel.value)
            timeline[day_key]['actions'].append(f"Send {channel.value} message")
            
            if timing == 0:
                timeline[day_key]['focus'] = 'Initial outreach'
            elif timing <= 3:
                timeline[day_key]['focus'] = 'Follow-up engagement'
            else:
                timeline[day_key]['focus'] = 'Persistence outreach'
        
        # Follow-up timeline
        max_timing = max(sequence_template['timing'])
        timeline[f"day_{max_timing + 14}"] = {
            'actions': ['Review engagement status', 'Decide on next sequence'],
            'channels': [],
            'focus': 'Performance review'
        }
        
        return timeline

    def _update_performance_metrics(self, result: CustomerAcquisitionResult):
        """Update overall performance tracking"""
        
        self.optimization_metrics['total_prospects_processed'] += 1
        
        if result.total_qualification_score >= 70:
            self.optimization_metrics['high_quality_prospects'] += 1
        
        # Update running averages
        total_processed = self.optimization_metrics['total_prospects_processed']
        
        # Conversion rate (weighted average)
        current_conversion = self.optimization_metrics['conversion_rate']
        new_conversion = (current_conversion * (total_processed - 1) + result.predicted_conversion_rate) / total_processed
        self.optimization_metrics['conversion_rate'] = new_conversion
        
        # Deal value (weighted average)
        current_deal_value = self.optimization_metrics['average_deal_value']
        new_deal_value = (current_deal_value * (total_processed - 1) + result.estimated_deal_value) / total_processed
        self.optimization_metrics['average_deal_value'] = new_deal_value
        
        # ROI improvement
        self.optimization_metrics['roi_improvement'] = result.roi_projection

    def _create_failed_result(self, domain: str, start_time: datetime) -> CustomerAcquisitionResult:
        """Create failed result for error cases"""
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Create minimal business intelligence
        failed_business_intel = BusinessIntelligence(
            company_name=domain.split('.')[0].title(),
            domain=domain,
            business_model='unknown',
            revenue_tier='unknown',
            estimated_employees=0,
            growth_indicators=[],
            budget_tier='unknown',
            buying_signals=[],
            buying_readiness_score=0,
            urgency_factors=[],
            tech_sophistication_score=0,
            competitor_analysis={},
            market_position='unknown',
            decision_maker_signals={},
            contact_channels=['email'],
            total_qualification_score=0,
            conversion_probability=0.0,
            recommended_approach='skip'
        )
        
        return CustomerAcquisitionResult(
            prospect_id=domain,
            domain=domain,
            business_intelligence=failed_business_intel,
            financial_signals={},
            personalized_messages=[],
            recommended_sequence=[],
            total_qualification_score=0,
            predicted_conversion_rate=0.0,
            estimated_deal_value=0.0,
            roi_projection=0.0,
            immediate_actions=['❌ Unable to process - requires manual review'],
            recommended_timeline={'day_0': {'actions': ['Manual review required'], 'channels': [], 'focus': 'Error handling'}},
            priority_level='low_priority',
            processed_at=datetime.now(),
            processing_time_seconds=processing_time
        )

    async def generate_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        
        report = {
            'summary': self.optimization_metrics.copy(),
            'timestamp': datetime.now().isoformat(),
            'recommendations': []
        }
        
        # Performance analysis
        total_processed = self.optimization_metrics['total_prospects_processed']
        high_quality_rate = self.optimization_metrics['high_quality_prospects'] / total_processed if total_processed > 0 else 0
        
        report['analysis'] = {
            'high_quality_rate': high_quality_rate,
            'average_conversion_rate': self.optimization_metrics['conversion_rate'],
            'average_deal_value': self.optimization_metrics['average_deal_value'],
            'average_roi': self.optimization_metrics['roi_improvement']
        }
        
        # Generate recommendations
        if high_quality_rate < 0.3:
            report['recommendations'].append("🎯 Improve prospect targeting - quality rate below 30%")
        
        if self.optimization_metrics['conversion_rate'] < 0.2:
            report['recommendations'].append("📈 Optimize messaging - conversion rate below 20%")
        
        if self.optimization_metrics['roi_improvement'] < 3.0:
            report['recommendations'].append("💰 Focus on higher-value prospects - ROI below 3x")
        
        return report

# Demo function
async def demo_integrated_customer_acquisition():
    """Demo the integrated customer acquisition pipeline"""
    
    print("\n🎯 INTEGRATED CUSTOMER ACQUISITION PIPELINE DEMO")
    print("=" * 80)
    
    system = IntegratedCustomerAcquisition()
    
    # Test domains
    test_domains = [
        'shopify.com',
        'exemplo-startup.io'
    ]
    
    results = []
    
    for domain in test_domains[:1]:  # Test one domain for demo
        print(f"\n" + "="*80)
        result = await system.process_prospect_complete(domain)
        results.append(result)
        
        # Display comprehensive results
        print(f"\n📋 COMPLETE ACQUISITION ANALYSIS:")
        print(f"   🏢 Company: {result.business_intelligence.company_name}")
        print(f"   🎯 Priority: {result.priority_level}")
        print(f"   📊 Qualification: {result.total_qualification_score}/100")
        print(f"   📈 Conversion Rate: {result.predicted_conversion_rate:.1%}")
        print(f"   💰 Deal Value: ${result.estimated_deal_value:,.0f}")
        print(f"   📊 ROI Projection: {result.roi_projection:.1f}x")
        
        print(f"\n📧 PERSONALIZED SEQUENCE ({len(result.personalized_messages)} messages):")
        for i, msg in enumerate(result.personalized_messages[:2]):  # Show first 2
            print(f"   Step {i+1} ({msg.channel.value}): {msg.subject_line}")
            print(f"           Expected rate: {msg.expected_response_rate:.1%}")
        
        print(f"\n🎯 IMMEDIATE ACTIONS:")
        for action in result.immediate_actions[:3]:
            print(f"   {action}")
        
        print(f"\n⏱️ TIMELINE:")
        for day, info in list(result.recommended_timeline.items())[:3]:
            print(f"   {day}: {info['focus']}")
            print(f"       Actions: {', '.join(info['actions'][:2])}")
    
    # Generate performance report
    report = await system.generate_performance_report()
    
    print(f"\n📊 PERFORMANCE REPORT:")
    print(f"   Prospects processed: {report['summary']['total_prospects_processed']}")
    print(f"   High-quality rate: {report['analysis']['high_quality_rate']:.1%}")
    print(f"   Average conversion: {report['analysis']['average_conversion_rate']:.1%}")
    print(f"   Average deal value: ${report['analysis']['average_deal_value']:,.0f}")
    print(f"   Average ROI: {report['analysis']['average_roi']:.1f}x")
    
    if report['recommendations']:
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"   {rec}")
    
    print(f"\n✅ Integrated Customer Acquisition Pipeline operational!")
    print(f"🚀 Ready for expert-level customer acquisition at scale!")

if __name__ == "__main__":
    asyncio.run(demo_integrated_customer_acquisition())
