#!/usr/bin/env python3
"""
ARCO Strategic Lead Scoring System
=================================
Sistema realista de scoring baseado em pain signals e growth opportunities.
Substitui abordagem genérica por análise estratégica focada em ROI.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class PainSeverity(Enum):
    """Severidade dos pain signals"""
    CRITICAL = "critical"  # Impacto imediato no revenue
    HIGH = "high"         # Impacto significativo
    MEDIUM = "medium"     # Impacto moderado
    LOW = "low"          # Impacto menor

class OpportunityType(Enum):
    """Tipos de oportunidades de crescimento"""
    REVENUE_OPTIMIZATION = "revenue_optimization"
    COST_REDUCTION = "cost_reduction"
    MARKET_EXPANSION = "market_expansion"
    OPERATIONAL_EFFICIENCY = "operational_efficiency"
    COMPETITIVE_ADVANTAGE = "competitive_advantage"

@dataclass
class PainSignal:
    """Pain signal individual com dados realistas"""
    signal_type: str
    description: str
    severity: PainSeverity
    confidence_level: float  # 0-100%
    estimated_monthly_impact: float  # $ valor de impacto
    urgency_days: int  # Dias até impacto crítico
    validation_data: Dict[str, Any]  # Dados que sustentam o signal
    solution_category: str
    detected_timestamp: str

@dataclass
class GrowthOpportunity:
    """Oportunidade de crescimento com projeções realistas"""
    opportunity_type: OpportunityType
    description: str
    potential_monthly_uplift: float  # $ valor potencial
    implementation_timeline: str  # "2-4 weeks", "1-3 months"
    investment_required: str  # "low", "medium", "high"
    success_probability: float  # 0-100%
    roi_projection: Dict[str, float]  # {"3_month": 1.5, "6_month": 2.3}
    supporting_data: Dict[str, Any]
    detected_timestamp: str

class RealisticPainDetector:
    """Detector de pain signals baseado em dados reais de mercado"""
    
    def __init__(self):
        # Industry benchmarks para validação realista
        self.industry_benchmarks = {
            "ecommerce": {
                "average_conversion_rate": 2.86,
                "average_cart_abandonment": 69.57,
                "average_cpa": 125,
                "average_roas": 4.0,
                "bounce_rate_threshold": 40
            },
            "saas": {
                "average_churn_rate": 5.0,  # Monthly
                "average_cac": 205,
                "average_ltv": 1500,
                "free_trial_conversion": 15,
                "bounce_rate_threshold": 35
            },
            "marketing_agencies": {
                "average_client_retention": 18,  # Months
                "average_profit_margin": 15,
                "average_cpa": 95,
                "utilization_rate": 75,
                "bounce_rate_threshold": 45
            },
            "dental": {
                "average_appointment_rate": 12,  # Per month
                "average_patient_value": 850,
                "patient_retention_rate": 80,
                "online_booking_rate": 35,
                "bounce_rate_threshold": 50
            }
        }
        
        # Pain signal detection rules
        self.pain_detection_rules = {
            "high_advertising_cost": {
                "condition": lambda data, benchmark: data.get("estimated_cpa", 0) > benchmark.get("average_cpa", 100) * 1.5,
                "severity": PainSeverity.HIGH,
                "urgency_days": 30,
                "solution": "campaign_optimization"
            },
            "poor_conversion_performance": {
                "condition": lambda data, benchmark: data.get("conversion_rate", 0) < benchmark.get("average_conversion_rate", 3) * 0.7,
                "severity": PainSeverity.CRITICAL,
                "urgency_days": 15,
                "solution": "conversion_optimization"
            },
            "high_bounce_rate": {
                "condition": lambda data, benchmark: data.get("bounce_rate", 0) > benchmark.get("bounce_rate_threshold", 50),
                "severity": PainSeverity.MEDIUM,
                "urgency_days": 45,
                "solution": "user_experience_optimization"
            },
            "low_creative_diversity": {
                "condition": lambda data, benchmark: data.get("creative_diversity_score", 1) < 0.3,
                "severity": PainSeverity.MEDIUM,
                "urgency_days": 60,
                "solution": "creative_strategy"
            },
            "poor_mobile_performance": {
                "condition": lambda data, benchmark: data.get("mobile_performance_score", 100) < 60,
                "severity": PainSeverity.HIGH,
                "urgency_days": 20,
                "solution": "technical_optimization"
            },
            "competitive_pressure": {
                "condition": lambda data, benchmark: data.get("competitor_density", 0) > 8,
                "severity": PainSeverity.MEDIUM,
                "urgency_days": 90,
                "solution": "competitive_strategy"
            }
        }
    
    def detect_pain_signals(self, lead_data: Dict) -> List[PainSignal]:
        """Detecta pain signals baseados em dados reais e benchmarks"""
        
        industry = lead_data.get("industry", "ecommerce").lower()
        benchmarks = self.industry_benchmarks.get(industry, self.industry_benchmarks["ecommerce"])
        
        detected_signals = []
        
        for signal_name, rule in self.pain_detection_rules.items():
            try:
                if rule["condition"](lead_data, benchmarks):
                    pain_signal = self._create_pain_signal(
                        signal_name, 
                        rule,
                        lead_data,
                        benchmarks,
                        industry
                    )
                    detected_signals.append(pain_signal)
                    
            except Exception as e:
                logger.error(f"Error detecting pain signal {signal_name}: {e}")
                continue
        
        # Sort by severity and impact
        detected_signals.sort(key=lambda x: (x.severity.value, x.estimated_monthly_impact), reverse=True)
        
        return detected_signals
    
    def _create_pain_signal(self, signal_name: str, rule: Dict, lead_data: Dict, benchmarks: Dict, industry: str) -> PainSignal:
        """Cria pain signal com dados realistas"""
        
        # Calculate realistic impact
        monthly_spend = lead_data.get("estimated_monthly_spend", 5000)
        impact_calculators = {
            "high_advertising_cost": lambda: self._calculate_ad_waste_impact(lead_data, benchmarks),
            "poor_conversion_performance": lambda: self._calculate_conversion_impact(lead_data, benchmarks, monthly_spend),
            "high_bounce_rate": lambda: self._calculate_bounce_impact(lead_data, benchmarks, monthly_spend),
            "low_creative_diversity": lambda: self._calculate_creative_impact(lead_data, monthly_spend),
            "poor_mobile_performance": lambda: self._calculate_mobile_impact(lead_data, monthly_spend),
            "competitive_pressure": lambda: self._calculate_competitive_impact(lead_data, monthly_spend)
        }
        
        estimated_impact = impact_calculators.get(signal_name, lambda: monthly_spend * 0.1)()
        
        # Generate realistic description
        descriptions = {
            "high_advertising_cost": f"CPA ${lead_data.get('estimated_cpa', 0):.0f} is {((lead_data.get('estimated_cpa', 0) / benchmarks.get('average_cpa', 100)) - 1) * 100:.0f}% above industry average",
            "poor_conversion_performance": f"Conversion rate {lead_data.get('conversion_rate', 0):.1f}% significantly below {benchmarks.get('average_conversion_rate', 3):.1f}% industry standard",
            "high_bounce_rate": f"Bounce rate {lead_data.get('bounce_rate', 0):.0f}% indicates poor user experience",
            "low_creative_diversity": f"Creative diversity score {lead_data.get('creative_diversity_score', 0):.1f} suggests limited A/B testing",
            "poor_mobile_performance": f"Mobile performance score {lead_data.get('mobile_performance_score', 0):.0f} hurts conversions and SEO",
            "competitive_pressure": f"High competitor density ({lead_data.get('competitor_density', 0)} competitors) in target keywords"
        }
        
        # Validation data
        validation_data = {
            "current_value": self._get_current_metric_value(signal_name, lead_data),
            "industry_benchmark": self._get_benchmark_value(signal_name, benchmarks),
            "variance_percentage": self._calculate_variance(signal_name, lead_data, benchmarks),
            "data_source": lead_data.get("data_sources", ["searchapi"]),
            "confidence_factors": self._get_confidence_factors(signal_name, lead_data)
        }
        
        # Confidence level
        confidence = self._calculate_confidence_level(signal_name, lead_data, validation_data)
        
        return PainSignal(
            signal_type=signal_name,
            description=descriptions[signal_name],
            severity=rule["severity"],
            confidence_level=confidence,
            estimated_monthly_impact=estimated_impact,
            urgency_days=rule["urgency_days"],
            validation_data=validation_data,
            solution_category=rule["solution"],
            detected_timestamp=datetime.now().isoformat()
        )
    
    def _calculate_ad_waste_impact(self, lead_data: Dict, benchmarks: Dict) -> float:
        """Calcula impacto financeiro de desperdício em ads"""
        cpa = lead_data.get("estimated_cpa", 0)
        benchmark_cpa = benchmarks.get("average_cpa", 100)
        monthly_spend = lead_data.get("estimated_monthly_spend", 5000)
        
        if cpa > benchmark_cpa:
            waste_percentage = (cpa - benchmark_cpa) / benchmark_cpa
            return monthly_spend * min(waste_percentage, 0.4)  # Cap at 40% waste
        
        return 0
    
    def _calculate_conversion_impact(self, lead_data: Dict, benchmarks: Dict, monthly_spend: float) -> float:
        """Calcula impacto de baixa conversão"""
        current_rate = lead_data.get("conversion_rate", 0)
        benchmark_rate = benchmarks.get("average_conversion_rate", 3)
        
        if benchmark_rate > current_rate:
            improvement_potential = (benchmark_rate - current_rate) / benchmark_rate
            # Revenue impact baseado no potential uplift
            return monthly_spend * improvement_potential * 2  # 2x multiplier for revenue impact
        
        return 0
    
    def _calculate_bounce_impact(self, lead_data: Dict, benchmarks: Dict, monthly_spend: float) -> float:
        """Calcula impacto de high bounce rate"""
        bounce_rate = lead_data.get("bounce_rate", 0)
        threshold = benchmarks.get("bounce_rate_threshold", 50)
        
        if bounce_rate > threshold:
            excess_bounce = (bounce_rate - threshold) / 100
            # High bounce rate indicates wasted traffic
            return monthly_spend * excess_bounce * 0.5
        
        return 0
    
    def _calculate_creative_impact(self, lead_data: Dict, monthly_spend: float) -> float:
        """Calcula oportunidade perdida por falta de diversidade criativa"""
        diversity_score = lead_data.get("creative_diversity_score", 0)
        
        if diversity_score < 0.5:
            opportunity_loss = (0.5 - diversity_score) * 0.3
            return monthly_spend * opportunity_loss
        
        return 0
    
    def _calculate_mobile_impact(self, lead_data: Dict, monthly_spend: float) -> float:
        """Calcula impacto de poor mobile performance"""
        mobile_score = lead_data.get("mobile_performance_score", 100)
        
        if mobile_score < 70:
            # Mobile traffic typically 50-70% of total
            mobile_traffic_percentage = 0.6
            performance_impact = (70 - mobile_score) / 70
            return monthly_spend * mobile_traffic_percentage * performance_impact
        
        return 0
    
    def _calculate_competitive_impact(self, lead_data: Dict, monthly_spend: float) -> float:
        """Calcula impacto de pressão competitiva"""
        competitor_density = lead_data.get("competitor_density", 0)
        
        if competitor_density > 6:
            # High competition increases costs and reduces efficiency
            pressure_factor = min((competitor_density - 6) / 10, 0.2)
            return monthly_spend * pressure_factor
        
        return 0
    
    def _get_current_metric_value(self, signal_name: str, lead_data: Dict) -> Any:
        """Pega valor atual da métrica"""
        metric_mappings = {
            "high_advertising_cost": lead_data.get("estimated_cpa", 0),
            "poor_conversion_performance": lead_data.get("conversion_rate", 0),
            "high_bounce_rate": lead_data.get("bounce_rate", 0),
            "low_creative_diversity": lead_data.get("creative_diversity_score", 0),
            "poor_mobile_performance": lead_data.get("mobile_performance_score", 0),
            "competitive_pressure": lead_data.get("competitor_density", 0)
        }
        return metric_mappings.get(signal_name, 0)
    
    def _get_benchmark_value(self, signal_name: str, benchmarks: Dict) -> Any:
        """Pega valor de benchmark"""
        benchmark_mappings = {
            "high_advertising_cost": benchmarks.get("average_cpa", 100),
            "poor_conversion_performance": benchmarks.get("average_conversion_rate", 3),
            "high_bounce_rate": benchmarks.get("bounce_rate_threshold", 50),
            "low_creative_diversity": 0.5,  # Standard threshold
            "poor_mobile_performance": 70,   # Performance threshold
            "competitive_pressure": 6        # Density threshold
        }
        return benchmark_mappings.get(signal_name, 0)
    
    def _calculate_variance(self, signal_name: str, lead_data: Dict, benchmarks: Dict) -> float:
        """Calcula variância percentual do benchmark"""
        current = self._get_current_metric_value(signal_name, lead_data)
        benchmark = self._get_benchmark_value(signal_name, benchmarks)
        
        if benchmark == 0:
            return 0
        
        return ((current - benchmark) / benchmark) * 100
    
    def _get_confidence_factors(self, signal_name: str, lead_data: Dict) -> List[str]:
        """Determina fatores que afetam confiança na detecção"""
        factors = []
        
        # Data source quality
        data_sources = lead_data.get("data_sources", [])
        if len(data_sources) > 1:
            factors.append("multiple_data_sources")
        
        # Data recency
        if "recent_data" in str(lead_data):
            factors.append("recent_data")
        
        # Sample size
        if lead_data.get("ad_volume_score", 0) > 50:
            factors.append("sufficient_ad_volume")
        
        return factors
    
    def _calculate_confidence_level(self, signal_name: str, lead_data: Dict, validation_data: Dict) -> float:
        """Calcula nível de confiança na detecção"""
        
        base_confidence = 60  # Base confidence
        
        # Data source quality boost
        data_sources = validation_data.get("data_source", [])
        if len(data_sources) > 1:
            base_confidence += 15
        
        # Variance strength boost
        variance = abs(validation_data.get("variance_percentage", 0))
        if variance > 50:
            base_confidence += 20
        elif variance > 25:
            base_confidence += 10
        
        # Confidence factors boost
        confidence_factors = validation_data.get("confidence_factors", [])
        base_confidence += len(confidence_factors) * 5
        
        return min(base_confidence, 95)  # Cap at 95%

class GrowthOpportunityDetector:
    """Detector de oportunidades reais de crescimento"""
    
    def __init__(self):
        self.opportunity_calculators = {
            OpportunityType.REVENUE_OPTIMIZATION: self._detect_revenue_opportunities,
            OpportunityType.COST_REDUCTION: self._detect_cost_reduction_opportunities,
            OpportunityType.MARKET_EXPANSION: self._detect_market_expansion_opportunities,
            OpportunityType.OPERATIONAL_EFFICIENCY: self._detect_efficiency_opportunities,
            OpportunityType.COMPETITIVE_ADVANTAGE: self._detect_competitive_opportunities
        }
    
    def detect_growth_opportunities(self, lead_data: Dict, pain_signals: List[PainSignal]) -> List[GrowthOpportunity]:
        """Detecta oportunidades reais de crescimento"""
        
        opportunities = []
        
        for opp_type, detector_func in self.opportunity_calculators.items():
            try:
                detected_opps = detector_func(lead_data, pain_signals)
                opportunities.extend(detected_opps)
            except Exception as e:
                logger.error(f"Error detecting {opp_type.value} opportunities: {e}")
        
        # Sort by potential value and probability
        opportunities.sort(
            key=lambda x: x.potential_monthly_uplift * (x.success_probability / 100), 
            reverse=True
        )
        
        return opportunities[:5]  # Top 5 opportunities
    
    def _detect_revenue_opportunities(self, lead_data: Dict, pain_signals: List[PainSignal]) -> List[GrowthOpportunity]:
        """Detecta oportunidades de otimização de revenue"""
        opportunities = []
        
        monthly_spend = lead_data.get("estimated_monthly_spend", 5000)
        
        # Conversion optimization opportunity
        conversion_rate = lead_data.get("conversion_rate", 0)
        if conversion_rate < 3:
            potential_uplift = monthly_spend * 0.25  # 25% revenue increase potential
            
            opportunities.append(GrowthOpportunity(
                opportunity_type=OpportunityType.REVENUE_OPTIMIZATION,
                description="Conversion rate optimization through landing page and funnel improvements",
                potential_monthly_uplift=potential_uplift,
                implementation_timeline="4-6 weeks",
                investment_required="medium",
                success_probability=75,
                roi_projection={"3_month": 1.8, "6_month": 2.5, "12_month": 3.2},
                supporting_data={
                    "current_conversion_rate": conversion_rate,
                    "industry_benchmark": 3.0,
                    "improvement_potential": "25-40%",
                    "implementation_approach": "A/B testing, UX optimization, funnel analysis"
                },
                detected_timestamp=datetime.now().isoformat()
            ))
        
        return opportunities
    
    def _detect_cost_reduction_opportunities(self, lead_data: Dict, pain_signals: List[PainSignal]) -> List[GrowthOpportunity]:
        """Detecta oportunidades de redução de custos"""
        opportunities = []
        
        monthly_spend = lead_data.get("estimated_monthly_spend", 5000)
        cpa = lead_data.get("estimated_cpa", 100)
        
        # High CPA optimization
        if cpa > 150:
            cost_reduction = monthly_spend * 0.2  # 20% cost reduction potential
            
            opportunities.append(GrowthOpportunity(
                opportunity_type=OpportunityType.COST_REDUCTION,
                description="Advertising cost optimization through targeting and keyword refinement",
                potential_monthly_uplift=cost_reduction,
                implementation_timeline="2-4 weeks",
                investment_required="low",
                success_probability=85,
                roi_projection={"3_month": 2.5, "6_month": 3.0, "12_month": 3.5},
                supporting_data={
                    "current_cpa": cpa,
                    "target_cpa": cpa * 0.8,
                    "optimization_methods": "negative keywords, audience refinement, bid optimization",
                    "expected_efficiency_gain": "20-30%"
                },
                detected_timestamp=datetime.now().isoformat()
            ))
        
        return opportunities
    
    def _detect_market_expansion_opportunities(self, lead_data: Dict, pain_signals: List[PainSignal]) -> List[GrowthOpportunity]:
        """Detecta oportunidades de expansão de mercado"""
        opportunities = []
        
        platforms = lead_data.get("advertising_platforms", [])
        monthly_spend = lead_data.get("estimated_monthly_spend", 5000)
        
        # Platform expansion opportunity
        if len(platforms) < 3:
            expansion_potential = monthly_spend * 0.4  # 40% growth potential
            
            opportunities.append(GrowthOpportunity(
                opportunity_type=OpportunityType.MARKET_EXPANSION,
                description="Expand to additional advertising platforms and audiences",
                potential_monthly_uplift=expansion_potential,
                implementation_timeline="6-8 weeks",
                investment_required="medium",
                success_probability=65,
                roi_projection={"3_month": 1.3, "6_month": 2.0, "12_month": 2.8},
                supporting_data={
                    "current_platforms": platforms,
                    "expansion_targets": ["linkedin", "tiktok", "youtube"],
                    "market_size_increase": "40-60%",
                    "audience_diversification": "high_value_segments"
                },
                detected_timestamp=datetime.now().isoformat()
            ))
        
        return opportunities
    
    def _detect_efficiency_opportunities(self, lead_data: Dict, pain_signals: List[PainSignal]) -> List[GrowthOpportunity]:
        """Detecta oportunidades de eficiência operacional"""
        opportunities = []
        
        creative_diversity = lead_data.get("creative_diversity_score", 0)
        monthly_spend = lead_data.get("estimated_monthly_spend", 5000)
        
        # Creative automation opportunity
        if creative_diversity < 0.4:
            efficiency_gain = monthly_spend * 0.15  # 15% efficiency improvement
            
            opportunities.append(GrowthOpportunity(
                opportunity_type=OpportunityType.OPERATIONAL_EFFICIENCY,
                description="Implement automated creative testing and optimization framework",
                potential_monthly_uplift=efficiency_gain,
                implementation_timeline="3-5 weeks",
                investment_required="low",
                success_probability=80,
                roi_projection={"3_month": 2.0, "6_month": 2.8, "12_month": 3.5},
                supporting_data={
                    "current_diversity_score": creative_diversity,
                    "automation_potential": "dynamic_creative_optimization",
                    "time_savings": "60-80%",
                    "performance_improvement": "15-25%"
                },
                detected_timestamp=datetime.now().isoformat()
            ))
        
        return opportunities
    
    def _detect_competitive_opportunities(self, lead_data: Dict, pain_signals: List[PainSignal]) -> List[GrowthOpportunity]:
        """Detecta oportunidades de vantagem competitiva"""
        opportunities = []
        
        competitor_density = lead_data.get("competitor_density", 0)
        monthly_spend = lead_data.get("estimated_monthly_spend", 5000)
        
        # Competitive differentiation opportunity
        if competitor_density > 6:
            competitive_advantage = monthly_spend * 0.3  # 30% advantage potential
            
            opportunities.append(GrowthOpportunity(
                opportunity_type=OpportunityType.COMPETITIVE_ADVANTAGE,
                description="Develop unique value proposition and competitive differentiation strategy",
                potential_monthly_uplift=competitive_advantage,
                implementation_timeline="8-12 weeks",
                investment_required="high",
                success_probability=55,
                roi_projection={"3_month": 1.1, "6_month": 1.8, "12_month": 2.9},
                supporting_data={
                    "competitor_count": competitor_density,
                    "differentiation_areas": ["messaging", "positioning", "targeting"],
                    "market_share_opportunity": "15-25%",
                    "long_term_moat": "brand_positioning"
                },
                detected_timestamp=datetime.now().isoformat()
            ))
        
        return opportunities

class StrategicLeadScorer:
    """Sistema de scoring estratégico consolidado"""
    
    def __init__(self):
        self.pain_detector = RealisticPainDetector()
        self.opportunity_detector = GrowthOpportunityDetector()
        
        # Weights para scoring final
        self.scoring_weights = {
            "pain_signal_value": 0.35,      # Valor dos pain signals
            "opportunity_potential": 0.30,   # Potencial das opportunities
            "implementation_feasibility": 0.20,  # Viabilidade de implementação
            "strategic_fit": 0.15           # Fit estratégico
        }
    
    def calculate_strategic_score(self, lead_data: Dict) -> Tuple[float, Dict[str, Any]]:
        """Calcula score estratégico completo com análise detalhada"""
        
        # Detect pain signals
        pain_signals = self.pain_detector.detect_pain_signals(lead_data)
        
        # Detect growth opportunities
        growth_opportunities = self.opportunity_detector.detect_growth_opportunities(lead_data, pain_signals)
        
        # Calculate component scores
        pain_score = self._calculate_pain_signal_score(pain_signals)
        opportunity_score = self._calculate_opportunity_score(growth_opportunities)
        feasibility_score = self._calculate_feasibility_score(lead_data, pain_signals, growth_opportunities)
        strategic_fit_score = self._calculate_strategic_fit_score(lead_data)
        
        # Weighted final score
        final_score = (
            pain_score * self.scoring_weights["pain_signal_value"] +
            opportunity_score * self.scoring_weights["opportunity_potential"] +
            feasibility_score * self.scoring_weights["implementation_feasibility"] +
            strategic_fit_score * self.scoring_weights["strategic_fit"]
        )
        
        # Detailed analysis
        analysis_details = {
            "final_score": final_score,
            "score_components": {
                "pain_signal_score": pain_score,
                "opportunity_score": opportunity_score,
                "feasibility_score": feasibility_score,
                "strategic_fit_score": strategic_fit_score
            },
            "pain_signals": [asdict(signal) for signal in pain_signals],
            "growth_opportunities": [asdict(opp) for opp in growth_opportunities],
            "total_pain_impact": sum(signal.estimated_monthly_impact for signal in pain_signals),
            "total_opportunity_value": sum(opp.potential_monthly_uplift for opp in growth_opportunities),
            "recommended_priority": self._determine_priority(final_score, pain_signals, growth_opportunities),
            "next_steps": self._generate_next_steps(pain_signals, growth_opportunities),
            "scoring_timestamp": datetime.now().isoformat()
        }
        
        return final_score, analysis_details
    
    def _calculate_pain_signal_score(self, pain_signals: List[PainSignal]) -> float:
        """Calcula score baseado nos pain signals"""
        if not pain_signals:
            return 0
        
        # Weight by severity and confidence
        severity_weights = {
            PainSeverity.CRITICAL: 1.0,
            PainSeverity.HIGH: 0.8,
            PainSeverity.MEDIUM: 0.6,
            PainSeverity.LOW: 0.4
        }
        
        total_weighted_impact = sum(
            signal.estimated_monthly_impact * 
            severity_weights[signal.severity] * 
            (signal.confidence_level / 100)
            for signal in pain_signals
        )
        
        # Normalize to 0-100 scale
        return min(total_weighted_impact / 100, 100)
    
    def _calculate_opportunity_score(self, opportunities: List[GrowthOpportunity]) -> float:
        """Calcula score baseado nas growth opportunities"""
        if not opportunities:
            return 0
        
        total_weighted_value = sum(
            opp.potential_monthly_uplift * (opp.success_probability / 100)
            for opp in opportunities
        )
        
        # Normalize to 0-100 scale
        return min(total_weighted_value / 150, 100)
    
    def _calculate_feasibility_score(self, lead_data: Dict, pain_signals: List[PainSignal], opportunities: List[GrowthOpportunity]) -> float:
        """Calcula score de viabilidade de implementação"""
        
        feasibility_factors = []
        
        # Budget availability (based on ad spend)
        monthly_spend = lead_data.get("estimated_monthly_spend", 0)
        if monthly_spend > 10000:
            feasibility_factors.append(30)  # High budget = high feasibility
        elif monthly_spend > 5000:
            feasibility_factors.append(20)
        else:
            feasibility_factors.append(10)
        
        # Technical readiness
        performance_score = lead_data.get("performance_score", 70)
        if performance_score > 70:
            feasibility_factors.append(25)  # Good tech foundation
        else:
            feasibility_factors.append(15)
        
        # Implementation complexity
        avg_implementation_weeks = self._calculate_avg_implementation_time(opportunities)
        if avg_implementation_weeks <= 4:
            feasibility_factors.append(25)  # Quick wins
        elif avg_implementation_weeks <= 8:
            feasibility_factors.append(20)
        else:
            feasibility_factors.append(10)
        
        # Data availability and confidence
        avg_confidence = sum(signal.confidence_level for signal in pain_signals) / len(pain_signals) if pain_signals else 70
        if avg_confidence > 80:
            feasibility_factors.append(20)
        elif avg_confidence > 60:
            feasibility_factors.append(15)
        else:
            feasibility_factors.append(10)
        
        return min(sum(feasibility_factors), 100)
    
    def _calculate_strategic_fit_score(self, lead_data: Dict) -> float:
        """Calcula fit estratégico do lead"""
        
        fit_factors = []
        
        # Market/region fit
        region = lead_data.get("country", "")
        if region in ["US", "GB", "CA", "AU"]:  # English-speaking markets
            fit_factors.append(25)
        else:
            fit_factors.append(10)
        
        # Industry expertise alignment
        industry = lead_data.get("industry", "").lower()
        target_industries = ["ecommerce", "saas", "marketing_agencies", "dental"]
        if any(target in industry for target in target_industries):
            fit_factors.append(25)
        else:
            fit_factors.append(15)
        
        # Company size/maturity
        platforms = lead_data.get("advertising_platforms", [])
        if len(platforms) >= 2:  # Multi-platform indicates sophistication
            fit_factors.append(25)
        else:
            fit_factors.append(15)
        
        # Growth stage indicators
        monthly_spend = lead_data.get("estimated_monthly_spend", 0)
        if 3000 <= monthly_spend <= 25000:  # Sweet spot for optimization
            fit_factors.append(25)
        else:
            fit_factors.append(15)
        
        return min(sum(fit_factors), 100)
    
    def _calculate_avg_implementation_time(self, opportunities: List[GrowthOpportunity]) -> float:
        """Calcula tempo médio de implementação em semanas"""
        if not opportunities:
            return 8  # Default
        
        time_mappings = {
            "2-4 weeks": 3,
            "3-5 weeks": 4,
            "4-6 weeks": 5,
            "6-8 weeks": 7,
            "8-12 weeks": 10,
            "1-3 months": 8,
            "3-6 months": 18
        }
        
        total_weeks = sum(
            time_mappings.get(opp.implementation_timeline, 8)
            for opp in opportunities
        )
        
        return total_weeks / len(opportunities)
    
    def _determine_priority(self, final_score: float, pain_signals: List[PainSignal], opportunities: List[GrowthOpportunity]) -> str:
        """Determina prioridade baseada no score e análise"""
        
        # High priority criteria
        critical_pain = any(signal.severity == PainSeverity.CRITICAL for signal in pain_signals)
        high_opportunity_value = any(opp.potential_monthly_uplift > 5000 for opp in opportunities)
        
        if final_score >= 80 or critical_pain or high_opportunity_value:
            return "high"
        elif final_score >= 60:
            return "medium"
        else:
            return "low"
    
    def _generate_next_steps(self, pain_signals: List[PainSignal], opportunities: List[GrowthOpportunity]) -> List[str]:
        """Gera próximos passos recomendados"""
        
        next_steps = []
        
        # Address critical pain signals first
        critical_signals = [s for s in pain_signals if s.severity == PainSeverity.CRITICAL]
        if critical_signals:
            next_steps.append(f"URGENT: Address {critical_signals[0].solution_category} - {critical_signals[0].description}")
        
        # High-value quick wins
        quick_wins = [opp for opp in opportunities if "2-4 weeks" in opp.implementation_timeline and opp.success_probability > 70]
        if quick_wins:
            next_steps.append(f"Quick Win: {quick_wins[0].description}")
        
        # Long-term strategic opportunities
        strategic_opps = [opp for opp in opportunities if opp.potential_monthly_uplift > 3000]
        if strategic_opps:
            next_steps.append(f"Strategic Initiative: {strategic_opps[0].description}")
        
        return next_steps

# Demo function
def demo_strategic_scoring():
    """Demo do sistema de scoring estratégico"""
    
    # Sample lead data
    sample_lead = {
        "company_name": "TechCorp Solutions",
        "domain": "techcorp.com",
        "industry": "ecommerce",
        "country": "US",
        "estimated_monthly_spend": 12000,
        "estimated_cpa": 180,
        "conversion_rate": 1.8,
        "bounce_rate": 65,
        "creative_diversity_score": 0.25,
        "mobile_performance_score": 45,
        "competitor_density": 9,
        "advertising_platforms": ["google", "meta"],
        "performance_score": 55,
        "data_sources": ["searchapi", "performance_analysis"]
    }
    
    # Initialize scorer
    scorer = StrategicLeadScorer()
    
    # Calculate strategic score
    final_score, analysis = scorer.calculate_strategic_score(sample_lead)
    
    # Display results
    print("\n🎯 STRATEGIC LEAD SCORING RESULTS")
    print("=" * 50)
    print(f"Final Score: {final_score:.1f}/100")
    print(f"Priority: {analysis['recommended_priority'].upper()}")
    print(f"Pain Signals: {len(analysis['pain_signals'])}")
    print(f"Growth Opportunities: {len(analysis['growth_opportunities'])}")
    print(f"Total Pain Impact: ${analysis['total_pain_impact']:,.0f}/month")
    print(f"Total Opportunity Value: ${analysis['total_opportunity_value']:,.0f}/month")
    
    print("\n🚨 TOP PAIN SIGNALS:")
    for signal in analysis['pain_signals'][:3]:
        print(f"  • {signal['description']} (${signal['estimated_monthly_impact']:,.0f}/month)")
    
    print("\n🚀 TOP OPPORTUNITIES:")
    for opp in analysis['growth_opportunities'][:3]:
        print(f"  • {opp['description']} (${opp['potential_monthly_uplift']:,.0f}/month)")
    
    print("\n📋 NEXT STEPS:")
    for step in analysis['next_steps']:
        print(f"  • {step}")

if __name__ == "__main__":
    demo_strategic_scoring()