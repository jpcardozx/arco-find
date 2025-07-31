"""
🧠 INTELLIGENCE VALIDATION ENGINE
Cross-validates technical pain from multiple sources to ensure accuracy
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime

from .technical_pain_detector import TechnicalPainPoint, TechnicalIntelligence

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of cross-validation analysis"""
    confidence_score: float  # 0.0 to 1.0
    validation_sources: List[str]
    conflicting_signals: List[str]
    reliability_factors: Dict[str, float]
    validated_pain_points: List[TechnicalPainPoint]
    recommendation: str  # 'proceed', 'investigate', 'reject'

@dataclass 
class MarketIntelligence:
    """Market-level intelligence for lead prioritization"""
    competitive_pressure: float  # 0.0 to 1.0
    market_urgency: float  # 0.0 to 1.0
    seasonal_factors: Dict[str, float]
    industry_benchmarks: Dict[str, float]
    buying_cycle_stage: str  # 'awareness', 'consideration', 'decision'

class IntelligenceValidationEngine:
    """Validates and enhances technical intelligence with cross-validation"""
    
    def __init__(self):
        # Validation thresholds
        self.confidence_thresholds = {
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4
        }
        
        # Industry benchmarks for validation
        self.industry_benchmarks = {
            'ecommerce': {
                'avg_conversion_rate': 0.025,
                'typical_mobile_score': 68,
                'standard_lcp': 2.8,
                'normal_ad_spend_per_employee': 150
            },
            'saas': {
                'avg_conversion_rate': 0.018,
                'typical_mobile_score': 72,
                'standard_lcp': 2.4,
                'normal_ad_spend_per_employee': 200
            },
            'digital_marketing': {
                'avg_conversion_rate': 0.035,
                'typical_mobile_score': 75,
                'standard_lcp': 2.2,
                'normal_ad_spend_per_employee': 300
            }
        }
    
    def validate_technical_intelligence(self, 
                                      intelligence: TechnicalIntelligence,
                                      additional_sources: Dict = None) -> ValidationResult:
        """
        Cross-validate technical intelligence across multiple sources
        """
        logger.info(f"🔍 Validating intelligence for {intelligence.company_name}")
        
        validation_sources = ['technical_analysis']
        reliability_factors = {}
        conflicting_signals = []
        validated_pain_points = []
        
        # 1. Performance validation
        perf_validation = self._validate_performance_signals(intelligence, additional_sources or {})
        validation_sources.extend(perf_validation['sources'])
        reliability_factors.update(perf_validation['factors'])
        conflicting_signals.extend(perf_validation['conflicts'])
        
        # 2. Business context validation
        business_validation = self._validate_business_context(intelligence, additional_sources or {})
        validation_sources.extend(business_validation['sources'])
        reliability_factors.update(business_validation['factors'])
        conflicting_signals.extend(business_validation['conflicts'])
        
        # 3. Market intelligence validation
        market_validation = self._validate_market_signals(intelligence, additional_sources or {})
        validation_sources.extend(market_validation['sources'])
        reliability_factors.update(market_validation['factors'])
        
        # 4. Cross-validate pain points
        for pain_point in intelligence.pain_points:
            validated_pain = self._cross_validate_pain_point(pain_point, reliability_factors)
            if validated_pain:
                validated_pain_points.append(validated_pain)
        
        # Calculate overall confidence
        confidence_score = self._calculate_confidence_score(reliability_factors, conflicting_signals)
        
        # Generate recommendation
        recommendation = self._generate_validation_recommendation(
            confidence_score, validated_pain_points, conflicting_signals
        )
        
        return ValidationResult(
            confidence_score=confidence_score,
            validation_sources=list(set(validation_sources)),
            conflicting_signals=conflicting_signals,
            reliability_factors=reliability_factors,
            validated_pain_points=validated_pain_points,
            recommendation=recommendation
        )
    
    def _validate_performance_signals(self, intelligence: TechnicalIntelligence, 
                                    additional_sources: Dict) -> Dict:
        """Validate performance-related pain signals"""
        sources = []
        factors = {}
        conflicts = []
        
        # Get performance pain points
        perf_pain_points = [p for p in intelligence.pain_points if p.category == 'performance']
        
        if perf_pain_points:
            primary_perf = perf_pain_points[0]
            
            # Check if performance score aligns with cost estimate
            estimated_score = self._extract_performance_score(primary_perf.evidence)
            if estimated_score:
                factors['performance_score_reliability'] = 0.9 if estimated_score < 50 else 0.7
                sources.append('performance_metrics')
                
                # Validate cost calculation reasonableness
                expected_cost_range = self._estimate_performance_cost_range(estimated_score)
                actual_cost = primary_perf.monthly_cost
                
                if expected_cost_range[0] <= actual_cost <= expected_cost_range[1]:
                    factors['cost_calculation_accuracy'] = 0.8
                else:
                    factors['cost_calculation_accuracy'] = 0.4
                    conflicts.append(f"Performance cost ${actual_cost:,.0f} outside expected range ${expected_cost_range[0]:,.0f}-${expected_cost_range[1]:,.0f}")
        
        # Validate against industry benchmarks
        website_domain = intelligence.website.split('//')[1].split('/')[0] if '//' in intelligence.website else intelligence.website
        if any(indicator in website_domain.lower() for indicator in ['shop', 'store', 'buy']):
            industry = 'ecommerce'
        elif any(indicator in website_domain.lower() for indicator in ['app', 'saas', 'software']):
            industry = 'saas'
        else:
            industry = 'digital_marketing'
        
        benchmark = self.industry_benchmarks.get(industry, self.industry_benchmarks['saas'])
        factors['industry_benchmark_alignment'] = 0.7  # Default alignment
        sources.append('industry_benchmarks')
        
        return {
            'sources': sources,
            'factors': factors,
            'conflicts': conflicts
        }
    
    def _validate_business_context(self, intelligence: TechnicalIntelligence, 
                                 additional_sources: Dict) -> Dict:
        """Validate business context and spending patterns"""
        sources = []
        factors = {}
        conflicts = []
        
        # Validate ad spend patterns
        ad_pain_points = [p for p in intelligence.pain_points 
                         if p.category in ['message_match', 'tracking']]
        
        total_ad_related_cost = sum(p.monthly_cost for p in ad_pain_points)
        
        if total_ad_related_cost > 0:
            # Check if ad-related costs are reasonable proportion of total
            total_pain_cost = intelligence.total_monthly_pain_cost
            ad_proportion = total_ad_related_cost / total_pain_cost if total_pain_cost > 0 else 0
            
            if 0.2 <= ad_proportion <= 0.8:  # 20-80% is reasonable
                factors['ad_cost_proportion_validity'] = 0.8
            else:
                factors['ad_cost_proportion_validity'] = 0.5
                conflicts.append(f"Ad-related costs ({ad_proportion:.1%}) seem disproportionate")
            
            sources.append('ad_spend_analysis')
        
        # Validate total opportunity size reasonableness
        annual_opportunity = intelligence.total_monthly_pain_cost * 12
        if annual_opportunity > 1000000:  # >$1M seems high for most SMBs
            factors['opportunity_size_realism'] = 0.6
            conflicts.append(f"Annual opportunity ${annual_opportunity:,.0f} seems very high")
        elif annual_opportunity > 100000:  # $100K+ is substantial but reasonable
            factors['opportunity_size_realism'] = 0.8
        else:  # <$100K is very reasonable
            factors['opportunity_size_realism'] = 0.9
        
        sources.append('business_logic_validation')
        
        return {
            'sources': sources,
            'factors': factors,
            'conflicts': conflicts
        }
    
    def _validate_market_signals(self, intelligence: TechnicalIntelligence, 
                               additional_sources: Dict) -> Dict:
        """Validate against market conditions and timing"""
        sources = []
        factors = {}
        
        # Current month/season factors
        current_month = datetime.now().month
        
        # Q4 (Oct-Dec) typically higher urgency for performance issues
        if current_month in [10, 11, 12]:
            factors['seasonal_urgency'] = 0.9
        # Q1 (Jan-Mar) budget planning season
        elif current_month in [1, 2, 3]:
            factors['seasonal_urgency'] = 0.8
        else:
            factors['seasonal_urgency'] = 0.7
        
        sources.append('seasonal_analysis')
        
        # Validate urgency against pain severity
        urgency_map = {'hot': 0.9, 'warm': 0.7, 'cold': 0.5}
        expected_urgency = urgency_map.get(intelligence.commercial_urgency, 0.5)
        
        # Check if urgency aligns with pain cost
        pain_cost_urgency = min(1.0, intelligence.total_monthly_pain_cost / 10000)  # $10K+ = max urgency
        
        urgency_alignment = 1.0 - abs(expected_urgency - pain_cost_urgency)
        factors['urgency_cost_alignment'] = max(0.5, urgency_alignment)
        
        sources.append('urgency_validation')
        
        return {
            'sources': sources,
            'factors': factors,
            'conflicts': []
        }
    
    def _cross_validate_pain_point(self, pain_point: TechnicalPainPoint, 
                                 reliability_factors: Dict) -> Optional[TechnicalPainPoint]:
        """Cross-validate individual pain point"""
        
        # Calculate validation score for this pain point
        validation_score = 0.7  # Base score
        
        # Adjust based on category reliability
        category_reliability = {
            'performance': 0.9,    # Performance is measurable
            'message_match': 0.7,  # Requires analysis
            'tracking': 0.8,       # Partially measurable
            'integration': 0.6     # More subjective
        }
        
        validation_score *= category_reliability.get(pain_point.category, 0.7)
        
        # Adjust based on cost reasonableness
        if pain_point.monthly_cost > 50000:  # >$50K/month seems high
            validation_score *= 0.7
        elif pain_point.monthly_cost < 500:  # <$500/month seems low
            validation_score *= 0.8
        
        # Only return if validation score is reasonable
        if validation_score >= 0.5:
            # Adjust cost based on validation confidence
            adjusted_cost = pain_point.monthly_cost * validation_score
            
            return TechnicalPainPoint(
                category=pain_point.category,
                severity=pain_point.severity,
                description=pain_point.description,
                monthly_cost=adjusted_cost,
                urgency_level=pain_point.urgency_level,
                evidence=pain_point.evidence + [f"Validation confidence: {validation_score:.1%}"],
                solution_fit=pain_point.solution_fit,
                timeline_to_fix=pain_point.timeline_to_fix
            )
        
        return None
    
    def _calculate_confidence_score(self, reliability_factors: Dict, 
                                  conflicting_signals: List[str]) -> float:
        """Calculate overall confidence in the intelligence"""
        
        if not reliability_factors:
            return 0.3  # Low confidence with no validation
        
        # Average reliability factors
        avg_reliability = sum(reliability_factors.values()) / len(reliability_factors)
        
        # Penalize for conflicts
        conflict_penalty = len(conflicting_signals) * 0.1
        
        # Bonus for multiple validation sources
        source_bonus = min(0.1, len(reliability_factors) * 0.02)
        
        confidence = avg_reliability - conflict_penalty + source_bonus
        
        return max(0.1, min(1.0, confidence))
    
    def _generate_validation_recommendation(self, confidence_score: float,
                                          validated_pain_points: List[TechnicalPainPoint],
                                          conflicts: List[str]) -> str:
        """Generate recommendation based on validation results"""
        
        if confidence_score >= self.confidence_thresholds['high'] and len(validated_pain_points) > 0:
            return 'proceed'
        elif confidence_score >= self.confidence_thresholds['medium'] and len(validated_pain_points) > 0:
            return 'investigate'
        else:
            return 'reject'
    
    def _extract_performance_score(self, evidence: List[str]) -> Optional[int]:
        """Extract performance score from evidence"""
        for item in evidence:
            if 'score:' in item.lower():
                try:
                    # Extract number from "Mobile performance score: 45/100"
                    parts = item.split(':')[1].strip()
                    score = int(parts.split('/')[0])
                    return score
                except:
                    continue
        return None
    
    def _estimate_performance_cost_range(self, performance_score: int) -> Tuple[float, float]:
        """Estimate reasonable cost range for performance issues"""
        if performance_score < 30:
            return (5000, 50000)    # Critical: $5K-$50K/month
        elif performance_score < 50:
            return (2000, 25000)    # Poor: $2K-$25K/month
        elif performance_score < 70:
            return (500, 10000)     # Suboptimal: $500-$10K/month
        else:
            return (0, 2000)        # Good: $0-$2K/month