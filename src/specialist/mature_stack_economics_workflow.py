#!/usr/bin/env python3
"""
🎯 MATURE STACK ECONOMICS WORKFLOW - R$ 1,997 PACKAGE
Advanced implementation following strategic review and business model insights

BUSINESS MODEL FOCUS:
- Detect R$ 500+/month stack waste for 4-month ROI
- Target: Over-engineered stacks in 5-50 employee businesses  
- Approach: Stack economics, not performance optimization
- Value Prop: "Pague uma vez, economize todo mês"

INTEGRATION:
- ARCO Infrastructure (IntegratedARCOEngine, CustomTechDetector, SaaS Detection)
- Business size validation (avoid over/under-engineering)
- Migration complexity analysis (low friction = higher priority)
- ROI-focused qualification (defensible economics)
"""

import sys
import os
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# Add paths for ARCO infrastructure
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'detectors'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'archive'))

from integrated_arco_engine import IntegratedARCOEngine
from custom_tech_detector import CustomTechDetector
from arco_saas_overspending_detector import WebDevOpportunityDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class StackWasteAnalysis:
    """Análise detalhada de desperdício de stack"""
    monthly_waste: float
    annual_waste: float
    expensive_tools: List[Dict]
    quick_wins: List[Dict]  # Easy migrations
    strategic_moves: List[Dict]  # Larger savings, more complex
    migration_complexity: str  # low/medium/high
    implementation_timeline: str

@dataclass
class BusinessSizeProfile:
    """Profile do tamanho e maturidade do negócio"""
    estimated_employees: int
    estimated_revenue_range: str
    business_maturity: str  # startup/growing/established/enterprise
    tech_sophistication: str  # basic/intermediate/advanced
    budget_capacity: str  # low/medium/high
    decision_maker_profile: str

@dataclass
class ROICalculation:
    """Cálculo detalhado de ROI para o pacote R$ 1,997"""
    package_price: float = 1997.0
    monthly_savings: float = 0.0
    roi_months: float = 0.0
    roi_category: str = ""  # IMMEDIATE/FAST/GOOD/MARGINAL
    payback_timeline: str = ""
    net_benefit_year_1: float = 0.0
    confidence_level: str = ""  # HIGH/MEDIUM/LOW

@dataclass
class QualificationProfile:
    """Profile completo de qualificação para R$ 1,997"""
    overall_score: int  # 0-100
    priority_level: str  # ULTRA_HIGH/HIGH/MEDIUM/LOW/DISQUALIFIED
    qualification_reasons: List[str]
    red_flags: List[str]
    sweet_spot_indicators: List[str]
    competitive_positioning: str

@dataclass
class SalesIntelligence:
    """Inteligência comercial para abordagem"""
    primary_value_prop: str
    key_pain_points: List[str]
    decision_triggers: List[str] 
    objection_anticipation: Dict[str, str]
    competitive_advantages: List[str]
    recommended_approach: str
    urgency_factors: List[str]

@dataclass
class MatureStackEconomicsLead:
    """Lead ultra-qualificado com intelligence completa"""
    # Basic Info
    place_id: str
    name: str
    business_type: str
    address: str
    phone: Optional[str]
    website: Optional[str]
    rating: float
    reviews: int
    
    # Stack Economics
    stack_analysis: StackWasteAnalysis
    business_profile: BusinessSizeProfile
    roi_calculation: ROICalculation
    qualification: QualificationProfile
    sales_intelligence: SalesIntelligence
    
    # Execution Ready
    next_actions: List[str]
    timeline_recommendation: str
    success_probability: float

class MatureStackEconomicsEngine:
    """Engine amadurecido seguindo strategic review"""
    
    def __init__(self):
        logger.info("🎯 Initializing Mature Stack Economics Engine - Strategic Approach")
        
        # Core ARCO infrastructure
        self.integrated_engine = IntegratedARCOEngine()
        self.tech_detector = CustomTechDetector()
        self.saas_detector = WebDevOpportunityDetector()
        
        # Strategic thresholds based on business model
        self.thresholds = {
            'min_monthly_savings': 500,  # R$ 500/mês minimum
            'max_roi_months': 6,         # 6 months maximum ROI
            'ideal_roi_months': 3,       # 3 months ideal ROI
            'min_confidence': 0.7,       # 70% confidence minimum
            'min_overall_score': 60      # 60/100 minimum score
        }
        
        # Business size sweet spots
        self.sweet_spots = {
            'employees': (5, 50),        # 5-50 employees
            'revenue_monthly': (20000, 500000),  # R$ 20K-500K monthly
            'tech_spend_monthly': (1000, 5000)   # R$ 1K-5K tech spend
        }
        
        # Stack complexity indicators for over-engineering detection  
        self.over_engineering_patterns = {
            'hubspot_small_business': {
                'indicator': 'hubspot',
                'employee_threshold': 20,
                'monthly_cost': 1200,
                'alternative_cost': 100,
                'complexity': 'medium'
            },
            'salesforce_sme': {
                'indicator': 'salesforce', 
                'employee_threshold': 50,
                'monthly_cost': 900,
                'alternative_cost': 50,
                'complexity': 'high'
            },
            'enterprise_hosting_small': {
                'indicator': ['wpengine', 'kinsta'],
                'traffic_threshold': 10000,
                'monthly_cost': 300,
                'alternative_cost': 80,
                'complexity': 'low'
            },
            'premium_plugins_bloat': {
                'indicator': ['elementor', 'wpforms', 'yoast_premium'],
                'monthly_cost': 200,
                'alternative_cost': 50,
                'complexity': 'low'
            }
        }
        
        # ROI categories for clear positioning
        self.roi_categories = {
            'IMMEDIATE': (0, 2),      # 0-2 months
            'FAST': (2, 3),           # 2-3 months  
            'GOOD': (3, 6),           # 3-6 months
            'MARGINAL': (6, 12)       # 6-12 months
        }

    def analyze_stack_waste_advanced(self, website: str) -> StackWasteAnalysis:
        """Análise avançada de desperdício de stack baseada em business model"""
        
        if not website:
            return StackWasteAnalysis(
                monthly_waste=0, annual_waste=0, expensive_tools=[],
                quick_wins=[], strategic_moves=[], 
                migration_complexity="unknown",
                implementation_timeline="Cannot analyze without website"
            )
        
        logger.info(f"   🔍 Advanced stack waste analysis for {website}")
        
        # SaaS overspending detection
        saas_analysis = self.saas_detector.analyze_saas_overspending(website)
        tech_analysis = self.tech_detector.detect_tech_stack(website)
        
        monthly_waste = 0
        expensive_tools = []
        quick_wins = []
        strategic_moves = []
        complexity_factors = []
        
        # Process SaaS overspending 
        if saas_analysis and saas_analysis.overspending_opportunities:
            for opportunity in saas_analysis.overspending_opportunities:
                monthly_waste += opportunity.monthly_savings
                
                tool_info = {
                    'tool': opportunity.tool_name,
                    'category': opportunity.category,
                    'current_cost': opportunity.estimated_monthly_cost,
                    'alternative_cost': opportunity.alternative_cost,
                    'monthly_savings': opportunity.monthly_savings,
                    'annual_savings': opportunity.annual_savings,
                    'difficulty': opportunity.replacement_difficulty,
                    'alternative': opportunity.recommended_alternative
                }
                expensive_tools.append(tool_info)
                
                # Categorize by implementation complexity
                if opportunity.replacement_difficulty == 'Easy':
                    quick_wins.append(tool_info)
                    complexity_factors.append('low')
                elif opportunity.annual_savings > 5000:  # Strategic if high savings
                    strategic_moves.append(tool_info)
                    complexity_factors.append('medium' if opportunity.replacement_difficulty == 'Medium' else 'high')
        
        # Detect over-engineering patterns
        for pattern_name, pattern in self.over_engineering_patterns.items():
            if self._detect_over_engineering(tech_analysis, pattern):
                monthly_waste += (pattern['monthly_cost'] - pattern['alternative_cost'])
                
                over_eng_tool = {
                    'tool': pattern_name.replace('_', ' ').title(),
                    'category': 'Over-engineering',
                    'current_cost': pattern['monthly_cost'],
                    'alternative_cost': pattern['alternative_cost'],
                    'monthly_savings': pattern['monthly_cost'] - pattern['alternative_cost'],
                    'annual_savings': (pattern['monthly_cost'] - pattern['alternative_cost']) * 12,
                    'difficulty': pattern['complexity'],
                    'alternative': 'Right-sized solution'
                }
                expensive_tools.append(over_eng_tool)
                
                if pattern['complexity'] == 'low':
                    quick_wins.append(over_eng_tool)
                else:
                    strategic_moves.append(over_eng_tool)
                
                complexity_factors.append(pattern['complexity'])
        
        # Determine overall migration complexity
        if not complexity_factors:
            migration_complexity = "low"
        elif 'high' in complexity_factors:
            migration_complexity = "high"  
        elif 'medium' in complexity_factors:
            migration_complexity = "medium"
        else:
            migration_complexity = "low"
        
        # Implementation timeline
        if migration_complexity == "low":
            timeline = "2-4 weeks"
        elif migration_complexity == "medium":
            timeline = "1-2 months"
        else:
            timeline = "2-3 months"
        
        return StackWasteAnalysis(
            monthly_waste=monthly_waste,
            annual_waste=monthly_waste * 12,
            expensive_tools=expensive_tools,
            quick_wins=quick_wins,
            strategic_moves=strategic_moves,
            migration_complexity=migration_complexity,
            implementation_timeline=timeline
        )

    def _detect_over_engineering(self, tech_analysis: Dict, pattern: Dict) -> bool:
        """Detectar over-engineering baseado em padrões"""
        if not tech_analysis or tech_analysis.get('status') != 'success':
            return False
            
        detected_tech = tech_analysis.get('detected_technologies', {})
        tech_string = str(detected_tech).lower()
        
        indicator = pattern['indicator']
        if isinstance(indicator, list):
            return any(ind in tech_string for ind in indicator)
        else:
            return indicator in tech_string

    def estimate_business_profile(self, business_data: Dict) -> BusinessSizeProfile:
        """Estimar profile do negócio para qualification"""
        
        # Estimate employees based on business type and reviews
        reviews = business_data.get('user_ratings_total', 0)
        rating = business_data.get('rating', 0)
        business_type = business_data.get('business_type', 'unknown')
        
        # Employee estimation heuristics
        if reviews < 10:
            employees = 3  # Very small
        elif reviews < 30:
            employees = 8  # Small  
        elif reviews < 100:
            employees = 15  # Medium
        elif reviews < 300:
            employees = 25  # Medium-large
        else:
            employees = 40  # Large
        
        # Revenue estimation based on business type and size
        if business_type in ['accounting', 'legal']:
            revenue_range = f"R$ {employees * 3000}-{employees * 8000}/month"
        elif business_type == 'marketing_agency':
            revenue_range = f"R$ {employees * 5000}-{employees * 15000}/month"  
        elif business_type == 'healthcare':
            revenue_range = f"R$ {employees * 4000}-{employees * 12000}/month"
        else:
            revenue_range = f"R$ {employees * 2000}-{employees * 6000}/month"
        
        # Business maturity
        if reviews < 15 or rating < 4.0:
            maturity = "startup"
        elif reviews < 50:
            maturity = "growing"
        elif reviews < 200:
            maturity = "established"
        else:
            maturity = "enterprise"
        
        # Tech sophistication based on business type
        if business_type == 'marketing_agency':
            tech_sophistication = "advanced"
        elif business_type in ['accounting', 'legal']:
            tech_sophistication = "intermediate"
        else:
            tech_sophistication = "basic"
        
        # Budget capacity
        if employees < 10:
            budget_capacity = "low"
        elif employees < 30:
            budget_capacity = "medium"  
        else:
            budget_capacity = "high"
        
        # Decision maker profile
        if employees < 15:
            decision_maker = "owner_operator"
        elif employees < 50:
            decision_maker = "small_team_leader"
        else:
            decision_maker = "department_manager"
        
        return BusinessSizeProfile(
            estimated_employees=employees,
            estimated_revenue_range=revenue_range,
            business_maturity=maturity,
            tech_sophistication=tech_sophistication,
            budget_capacity=budget_capacity,
            decision_maker_profile=decision_maker
        )

    def calculate_roi_advanced(self, stack_analysis: StackWasteAnalysis, 
                             business_profile: BusinessSizeProfile) -> ROICalculation:
        """Cálculo avançado de ROI com confidence levels"""
        
        monthly_savings = stack_analysis.monthly_waste
        package_price = self.thresholds['min_monthly_savings'] * 4  # R$ 1,997 base
        
        if monthly_savings <= 0:
            return ROICalculation(
                package_price=package_price,
                monthly_savings=0,
                roi_months=999,
                roi_category="DISQUALIFIED", 
                payback_timeline="No savings identified",
                net_benefit_year_1=-package_price,
                confidence_level="LOW"
            )
        
        roi_months = package_price / monthly_savings
        net_benefit_year_1 = (monthly_savings * 12) - package_price
        
        # ROI category classification
        roi_category = "MARGINAL"
        for category, (min_months, max_months) in self.roi_categories.items():
            if min_months <= roi_months < max_months:
                roi_category = category
                break
        
        # Confidence level based on multiple factors
        confidence_factors = []
        
        # Stack analysis confidence
        if len(stack_analysis.expensive_tools) >= 2:
            confidence_factors.append(0.3)  # Multiple tools = higher confidence
        elif len(stack_analysis.expensive_tools) == 1:
            confidence_factors.append(0.2)
        
        # Quick wins confidence  
        if stack_analysis.quick_wins:
            confidence_factors.append(0.2)
        
        # Business profile confidence
        if business_profile.business_maturity in ['growing', 'established']:
            confidence_factors.append(0.3)
        
        # Migration complexity confidence
        if stack_analysis.migration_complexity == 'low':
            confidence_factors.append(0.2)
        elif stack_analysis.migration_complexity == 'medium':
            confidence_factors.append(0.1)
        
        confidence_score = sum(confidence_factors)
        
        if confidence_score >= 0.8:
            confidence_level = "HIGH"
        elif confidence_score >= 0.5:
            confidence_level = "MEDIUM"  
        else:
            confidence_level = "LOW"
        
        # Payback timeline description
        if roi_months <= 2:
            payback_timeline = f"ROI em {roi_months:.1f} meses - INVESTIMENTO EXCEPCIONAL"
        elif roi_months <= 3:
            payback_timeline = f"ROI em {roi_months:.1f} meses - MUITO ATRATIVO"
        elif roi_months <= 6:
            payback_timeline = f"ROI em {roi_months:.1f} meses - ATRATIVO" 
        else:
            payback_timeline = f"ROI em {roi_months:.1f} meses - MARGINAL"
        
        return ROICalculation(
            package_price=package_price,
            monthly_savings=monthly_savings,
            roi_months=roi_months,
            roi_category=roi_category,
            payback_timeline=payback_timeline,
            net_benefit_year_1=net_benefit_year_1,
            confidence_level=confidence_level
        )

    def qualify_for_package(self, stack_analysis: StackWasteAnalysis,
                           business_profile: BusinessSizeProfile,
                           roi_calculation: ROICalculation) -> QualificationProfile:
        """Qualification avançada baseada em múltiplos fatores"""
        
        score = 0
        qualification_reasons = []
        red_flags = []
        sweet_spot_indicators = []
        
        # ROI Score (40 points maximum)
        if roi_calculation.roi_category == "IMMEDIATE":
            score += 40
            qualification_reasons.append("ROI imediato (< 2 meses)")
            sweet_spot_indicators.append("ROI excepcional")
        elif roi_calculation.roi_category == "FAST":
            score += 30
            qualification_reasons.append("ROI rápido (2-3 meses)")
            sweet_spot_indicators.append("ROI muito atrativo")
        elif roi_calculation.roi_category == "GOOD":
            score += 20
            qualification_reasons.append("ROI bom (3-6 meses)")
        else:
            red_flags.append("ROI muito longo (> 6 meses)")
        
        # Savings Amount Score (25 points maximum)
        monthly_savings = stack_analysis.monthly_waste
        if monthly_savings >= 1000:
            score += 25
            qualification_reasons.append(f"Economia alta (R$ {monthly_savings:.0f}/mês)")
            sweet_spot_indicators.append("Economia substancial")
        elif monthly_savings >= 500:
            score += 15  
            qualification_reasons.append(f"Economia moderada (R$ {monthly_savings:.0f}/mês)")
        else:
            red_flags.append(f"Economia insuficiente (R$ {monthly_savings:.0f}/mês)")
        
        # Business Size Score (20 points maximum)
        employees = business_profile.estimated_employees
        if self.sweet_spots['employees'][0] <= employees <= self.sweet_spots['employees'][1]:
            score += 20
            qualification_reasons.append(f"Tamanho ideal ({employees} funcionários)")
            sweet_spot_indicators.append("Sweet spot de tamanho")
        elif employees < self.sweet_spots['employees'][0]:
            score += 5
            red_flags.append("Negócio muito pequeno")
        else:
            score += 10
            red_flags.append("Negócio muito grande")
        
        # Implementation Complexity Score (10 points maximum)
        if stack_analysis.migration_complexity == 'low':
            score += 10
            qualification_reasons.append("Migração simples")
            sweet_spot_indicators.append("Baixa fricção")
        elif stack_analysis.migration_complexity == 'medium':
            score += 5
            qualification_reasons.append("Migração moderada")
        else:
            red_flags.append("Migração complexa")
        
        # Confidence Score (5 points maximum)
        if roi_calculation.confidence_level == "HIGH":
            score += 5
            qualification_reasons.append("Alta confiança na análise")
        elif roi_calculation.confidence_level == "MEDIUM":
            score += 3
        else:
            red_flags.append("Baixa confiança na análise")
        
        # Priority level determination
        if score >= 85 and not red_flags:
            priority_level = "🔥 ULTRA HIGH"
        elif score >= 70:
            priority_level = "⚡ HIGH"
        elif score >= 60:
            priority_level = "📊 MEDIUM"
        elif score >= 40:
            priority_level = "📋 LOW"
        else:
            priority_level = "❌ DISQUALIFIED"
        
        # Competitive positioning
        if monthly_savings >= 1000 and roi_calculation.roi_months <= 2:
            competitive_positioning = "Proposta irresistível - ROI imediato com economia substancial"
        elif monthly_savings >= 500 and roi_calculation.roi_months <= 4:
            competitive_positioning = "Proposta muito competitiva - ROI rápido"
        elif monthly_savings >= 300:
            competitive_positioning = "Proposta válida - economia defensável"
        else:
            competitive_positioning = "Proposta marginal - considerar outros fatores"
        
        return QualificationProfile(
            overall_score=score,
            priority_level=priority_level,
            qualification_reasons=qualification_reasons,
            red_flags=red_flags,
            sweet_spot_indicators=sweet_spot_indicators,
            competitive_positioning=competitive_positioning
        )

    def generate_sales_intelligence(self, stack_analysis: StackWasteAnalysis,
                                   business_profile: BusinessSizeProfile,
                                   roi_calculation: ROICalculation,
                                   qualification: QualificationProfile,
                                   business_data: Dict) -> SalesIntelligence:
        """Gerar intelligence comercial para abordagem"""
        
        business_name = business_data.get('name', 'Business')
        business_type = business_data.get('business_type', 'business')
        monthly_savings = stack_analysis.monthly_waste
        
        # Primary value proposition
        if roi_calculation.roi_months <= 2:
            primary_value_prop = f"ROI imediato: economizem R$ {monthly_savings:.0f}/mês pagando apenas R$ 1.997"
        elif roi_calculation.roi_months <= 4:
            primary_value_prop = f"Investimento se paga em {roi_calculation.roi_months:.1f} meses, depois é lucro puro"
        else:
            primary_value_prop = f"Redução de custos operacionais: R$ {monthly_savings:.0f}/mês de economia"
        
        # Key pain points based on detected tools
        pain_points = []
        for tool in stack_analysis.expensive_tools:
            pain_points.append(f"Gastando R$ {tool['current_cost']}/mês em {tool['tool']} quando poderia custar R$ {tool['alternative_cost']}")
        
        if not pain_points:
            pain_points.append("Stack tecnológico com potencial de otimização")
        
        # Decision triggers
        decision_triggers = [
            f"Economia de R$ {monthly_savings * 12:.0f}/ano",
            f"ROI em {roi_calculation.roi_months:.1f} meses",
            "Implementação sem fricção operacional"
        ]
        
        if stack_analysis.quick_wins:
            decision_triggers.append("Resultados imediatos disponíveis")
        
        # Objection anticipation 
        objections = {
            "price": f"R$ 1.997 se paga em {roi_calculation.roi_months:.1f} meses com economia de R$ {monthly_savings:.0f}/mês",
            "timing": f"Cada mês de atraso custa R$ {monthly_savings:.0f} em desperdício",
            "risk": "Análise prévia + implementação reversível + garantia de economia",
            "disruption": f"Migração {stack_analysis.migration_complexity} complexidade - operações mantidas"
        }
        
        # Competitive advantages
        advantages = [
            "Economia mensurável e garantida",
            "ROI defensável com análise técnica",
            "Implementação sem downtime",
            "Foco em stack economics, não cosmético"
        ]
        
        # Recommended approach strategy
        if qualification.priority_level == "🔥 ULTRA HIGH":
            approach = "IMMEDIATE CONTACT - proposta irresistível, agendar demo em 48h"
        elif qualification.priority_level == "⚡ HIGH":
            approach = "PRIORITY CONTACT - ROI atrativo, agendar em 1 semana"
        elif qualification.priority_level == "📊 MEDIUM":
            approach = "QUALIFIED CONTACT - apresentar análise e agendar meeting"
        else:
            approach = "NURTURE - manter no pipeline, reavaliar em 3 meses"
        
        # Urgency factors
        urgency_factors = [
            f"R$ {monthly_savings:.0f}/mês de desperdício contínuo",
            "Competitors podem otimizar custos primeiro",
            "Implementação leva " + stack_analysis.implementation_timeline
        ]
        
        return SalesIntelligence(
            primary_value_prop=primary_value_prop,
            key_pain_points=pain_points,
            decision_triggers=decision_triggers,
            objection_anticipation=objections,
            competitive_advantages=advantages,
            recommended_approach=approach,
            urgency_factors=urgency_factors
        )

    def process_lead_complete(self, business_data: Dict, website: str) -> Optional[MatureStackEconomicsLead]:
        """Processamento completo de lead com todas as análises"""
        
        logger.info(f"   📊 Complete analysis: {business_data.get('name', 'Unknown')}")
        
        try:
            # 1. Stack waste analysis 
            stack_analysis = self.analyze_stack_waste_advanced(website)
            
            # 2. Business profile estimation
            business_profile = self.estimate_business_profile(business_data)
            
            # 3. ROI calculation
            roi_calculation = self.calculate_roi_advanced(stack_analysis, business_profile)
            
            # 4. Qualification
            qualification = self.qualify_for_package(stack_analysis, business_profile, roi_calculation)
            
            # 5. Early disqualification
            if (stack_analysis.monthly_waste < self.thresholds['min_monthly_savings'] or
                roi_calculation.roi_months > self.thresholds['max_roi_months'] or
                qualification.overall_score < self.thresholds['min_overall_score']):
                
                logger.info(f"   ❌ Disqualified: R$ {stack_analysis.monthly_waste:.0f}/month waste (min: R$ {self.thresholds['min_monthly_savings']})")
                return None
            
            # 6. Sales intelligence
            sales_intelligence = self.generate_sales_intelligence(
                stack_analysis, business_profile, roi_calculation, qualification, business_data
            )
            
            # 7. Next actions
            next_actions = []
            if qualification.priority_level == "🔥 ULTRA HIGH":
                next_actions = [
                    "IMMEDIATE: Contact within 24h",
                    "Prepare detailed cost analysis",
                    "Schedule demo call",
                    "Prepare case study materials"
                ]
                timeline_recommendation = "Contact this week"
                success_probability = 0.6
            elif qualification.priority_level == "⚡ HIGH":
                next_actions = [
                    "PRIORITY: Contact within 1 week", 
                    "Send preliminary analysis",
                    "Schedule discovery call",
                    "Gather technical requirements"
                ]
                timeline_recommendation = "Contact within 2 weeks"
                success_probability = 0.4
            else:
                next_actions = [
                    "QUALIFIED: Contact within 1 month",
                    "Add to nurture sequence", 
                    "Monitor for trigger events"
                ]
                timeline_recommendation = "Contact within 1 month"
                success_probability = 0.2
            
            # 8. Create complete lead
            lead = MatureStackEconomicsLead(
                place_id=business_data.get('place_id', ''),
                name=business_data.get('name', ''),
                business_type=business_data.get('business_type', ''),
                address=business_data.get('vicinity', ''),
                phone=business_data.get('formatted_phone_number'),
                website=website,
                rating=business_data.get('rating', 0),
                reviews=business_data.get('user_ratings_total', 0),
                stack_analysis=stack_analysis,
                business_profile=business_profile,
                roi_calculation=roi_calculation,
                qualification=qualification,
                sales_intelligence=sales_intelligence,
                next_actions=next_actions,
                timeline_recommendation=timeline_recommendation,
                success_probability=success_probability
            )
            
            logger.info(f"   ✅ QUALIFIED: {qualification.priority_level} | ROI {roi_calculation.roi_months:.1f}m | R$ {stack_analysis.monthly_waste:.0f}/m savings")
            
            return lead
            
        except Exception as e:
            logger.error(f"   ❌ Error processing {business_data.get('name', 'Unknown')}: {e}")
            return None

    def generate_mature_leads(self, niches: List[str] = None, 
                            max_leads_per_niche: int = 10) -> List[MatureStackEconomicsLead]:
        """Geração madura de leads com inteligência completa"""
        
        if niches is None:
            niches = [
                'accounting', 'legal', 'healthcare', 
                'marketing_agency', 'consulting', 'architecture'
            ]
        
        logger.info("🎯 GENERATING MATURE STACK ECONOMICS LEADS")
        logger.info("=" * 60)
        
        all_leads = []
        
        for niche in niches:
            logger.info(f"\n🔍 Analyzing {niche} niche")
            
            # Expected waste by niche
            expected_waste = {
                'accounting': 'R$ 600-1500/month',
                'legal': 'R$ 700-1800/month', 
                'healthcare': 'R$ 500-1200/month',
                'marketing_agency': 'R$ 1000-3000/month',
                'consulting': 'R$ 400-1000/month',
                'architecture': 'R$ 500-1200/month'
            }
            
            logger.info(f"Expected waste: {expected_waste.get(niche, 'R$ 500-1500/month')}")
            
            # Search queries by niche
            queries = {
                'accounting': [
                    f'escritorio contabilidade Belo Horizonte MG',
                    f'contador Belo Horizonte MG'
                ],
                'legal': [
                    f'advogado escritorio juridico Belo Horizonte MG',
                    f'advocacia Belo Horizonte MG'  
                ],
                'healthcare': [
                    f'clinica medica Belo Horizonte MG',
                    f'consultorio dentista Belo Horizonte MG'
                ],
                'marketing_agency': [
                    f'agencia marketing digital Belo Horizonte MG',
                    f'agencia publicidade Belo Horizonte MG'
                ],
                'consulting': [
                    f'consultoria empresarial Belo Horizonte MG',
                    f'consultoria gestao Belo Horizonte MG'
                ],
                'architecture': [
                    f'escritorio arquitetura Belo Horizonte MG',
                    f'arquiteto Belo Horizonte MG'
                ]
            }
            
            niche_leads = []
            
            for query in queries.get(niche, [f'{niche} Belo Horizonte MG']):
                try:                    # Use ARCO engine for business discovery
                    businesses = self.integrated_engine.lead_generator.discover_businesses(
                        niche, "Belo Horizonte MG", max_leads_per_niche//2
                    )
                    
                    if not businesses:
                        continue
                    
                    # Limit businesses per query  
                    businesses = businesses[:max_leads_per_niche//2]
                    
                    for business in businesses:
                        if len(niche_leads) >= max_leads_per_niche:
                            break
                        
                        business['business_type'] = niche
                        website = business.get('website')
                        
                        if not website:
                            continue
                        
                        # Complete lead processing
                        lead = self.process_lead_complete(business, website)
                        
                        if lead:
                            niche_leads.append(lead)
                    
                    if len(niche_leads) >= max_leads_per_niche:
                        break
                        
                except Exception as e:
                    logger.error(f"Error processing {niche} query '{query}': {e}")
                    continue
            
            all_leads.extend(niche_leads)
            logger.info(f"   ✅ {len(niche_leads)} qualified leads from {niche}")
        
        # Sort by priority and ROI
        all_leads.sort(key=lambda x: (
            x.qualification.overall_score, 
            -x.roi_calculation.roi_months
        ), reverse=True)
        
        return all_leads

def main():
    """Main execution function"""
    
    engine = MatureStackEconomicsEngine()
    
    # Generate mature leads
    leads = engine.generate_mature_leads(max_leads_per_niche=6)
    
    if not leads:
        logger.warning("❌ No qualified leads found")
        return
    
    # Generate report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results/mature_stack_economics_{timestamp}.json"
    
    # Prepare output data
    output_data = {
        'generated_at': datetime.now().isoformat(),
        'business_model': 'R$ 1,997 Mature Stack Economics Package',
        'methodology': 'Integrated ARCO + Stack Economics + ROI Analysis',
        'total_leads': len(leads),
        'leads': [asdict(lead) for lead in leads]
    }
    
    # Calculate summary statistics
    total_monthly_waste = sum(lead.stack_analysis.monthly_waste for lead in leads)
    total_annual_savings = sum(lead.stack_analysis.annual_waste for lead in leads)
    avg_roi_months = sum(lead.roi_calculation.roi_months for lead in leads) / len(leads)
    package_revenue_potential = len(leads) * 1997
    
    ultra_high_leads = [l for l in leads if l.qualification.priority_level == "🔥 ULTRA HIGH"]
    high_leads = [l for l in leads if l.qualification.priority_level == "⚡ HIGH"]
    
    # Print summary
    logger.info(f"\n🎯 MATURE STACK ECONOMICS ANALYSIS COMPLETE")
    logger.info(f"✅ {len(leads)} ultra-qualified leads generated")
    logger.info(f"📁 Results: {filename}")
    logger.info(f"\n💰 COMPREHENSIVE ECONOMICS:")
    logger.info(f"• Total monthly waste identified: R$ {total_monthly_waste:,.0f}")
    logger.info(f"• Total annual savings potential: R$ {total_annual_savings:,.0f}")
    logger.info(f"• Average ROI timeline: {avg_roi_months:.1f} months")
    logger.info(f"• Package revenue potential: R$ {package_revenue_potential:,.0f}")
    logger.info(f"• Success probability weighted: {sum(l.success_probability for l in leads) * 1997:.0f}")
    
    logger.info(f"\n🏆 PRIORITY BREAKDOWN:")
    logger.info(f"• 🔥 ULTRA HIGH: {len(ultra_high_leads)} leads")
    logger.info(f"• ⚡ HIGH: {len(high_leads)} leads")
    logger.info(f"• 📊 MEDIUM+: {len(leads) - len(ultra_high_leads) - len(high_leads)} leads")
    
    # Show top leads
    logger.info(f"\n🌟 TOP 5 ULTRA-QUALIFIED LEADS:")
    for i, lead in enumerate(leads[:5], 1):
        logger.info(f"{i}. {lead.name}")
        logger.info(f"   ROI: {lead.roi_calculation.roi_months:.1f} months | Waste: R$ {lead.stack_analysis.monthly_waste:.0f}/month | {lead.qualification.priority_level}")
        logger.info(f"   Employees: ~{lead.business_profile.estimated_employees} | Complexity: {lead.stack_analysis.migration_complexity}")
    
    # Save results
    os.makedirs('results', exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\n✅ Mature analysis complete. Ready for strategic execution!")

if __name__ == "__main__":
    main()
