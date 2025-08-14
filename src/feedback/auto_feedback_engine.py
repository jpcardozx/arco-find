#!/usr/bin/env python3
"""
Auto Feedback Engine - Sistema de feedback maduro e crítico
Analisa performance do pipeline, detecta falhas e sugere melhorias
"""

import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Métricas de performance do pipeline"""
    execution_id: str
    start_time: datetime
    end_time: datetime
    total_credits_used: int
    prospects_discovered: int
    prospects_qualified: int
    qualification_rate: float
    cost_per_lead: float
    engines_used: List[str]
    errors_count: int
    warnings_count: int
    avg_response_time_ms: float

@dataclass
class CriticalFeedback:
    """Feedback crítico do sistema"""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # ENGINE_COVERAGE, QUALIFICATION_RATE, COST_EFFICIENCY, DATA_QUALITY
    issue: str
    evidence: List[str]
    recommendations: List[str]
    impact_score: int  # 1-10

class AutoFeedbackEngine:
    """
    Engine de auto feedback crítico para otimização contínua
    """
    
    def __init__(self):
        self.feedback_threshold = {
            'qualification_rate_min': 0.05,  # 5% mínimo
            'cost_per_lead_max': 10.0,       # $10 USD máximo
            'response_time_max': 5000,       # 5s máximo
            'min_engines_required': 2        # Mínimo 2 engines
        }
        
        # Engines obrigatórios para discovery com DADOS REAIS DE ADS
        self.required_engines = {
            'primary': [
                'google_ads_transparency_center_advertiser_search',
                'google_ads_transparency_center'
            ],
            'fallback': [
                'google'  # Apenas para SERP quando Transparency Center falha
            ]
            # REMOVIDO: reddit, youtube, bing = DELÍRIO
            # FOCO: Apenas engines que retornam advertiser_id e dados reais de ads
        }
    
    async def analyze_pipeline_performance(self, 
                                         execution_data: Dict,
                                         historical_data: List[Dict] = None) -> List[CriticalFeedback]:
        """
        Análise crítica da performance do pipeline
        """
        logger.info("🔬 Starting critical performance analysis")
        
        metrics = self._extract_metrics(execution_data)
        feedback_items = []
        
        # 1. ANÁLISE DE COBERTURA DE ENGINES
        engine_feedback = await self._analyze_engine_coverage(metrics)
        feedback_items.extend(engine_feedback)
        
        # 2. ANÁLISE DE TAXA DE QUALIFICAÇÃO
        qualification_feedback = self._analyze_qualification_rates(metrics, historical_data)
        feedback_items.extend(qualification_feedback)
        
        # 3. ANÁLISE DE EFICIÊNCIA DE CUSTO
        cost_feedback = self._analyze_cost_efficiency(metrics)
        feedback_items.extend(cost_feedback)
        
        # 4. ANÁLISE DE QUALIDADE DE DADOS
        data_quality_feedback = self._analyze_data_quality(execution_data)
        feedback_items.extend(data_quality_feedback)
        
        # 5. ANÁLISE DE PERFORMANCE TÉCNICA
        technical_feedback = self._analyze_technical_performance(metrics)
        feedback_items.extend(technical_feedback)
        
        # Ordenar por severidade e impacto
        feedback_items.sort(key=lambda x: (
            ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].index(x.severity),
            -x.impact_score
        ))
        
        logger.info(f"📊 Analysis complete: {len(feedback_items)} feedback items generated")
        
        # Log feedback crítico
        for feedback in feedback_items:
            if feedback.severity in ['CRITICAL', 'HIGH']:
                logger.warning(f"🚨 {feedback.severity}: {feedback.issue}")
        
        return feedback_items
    
    async def _analyze_engine_coverage(self, metrics: PerformanceMetrics) -> List[CriticalFeedback]:
        """Análise crítica da cobertura de engines"""
        feedback = []
        
        # Verificar engines primários
        missing_primary = [eng for eng in self.required_engines['primary'] 
                          if eng not in metrics.engines_used]
        
        if missing_primary:
            feedback.append(CriticalFeedback(
                severity='CRITICAL',
                category='ENGINE_COVERAGE',
                issue=f"Missing critical primary engines: {missing_primary}",
                evidence=[
                    f"Only {len(metrics.engines_used)} engines used: {metrics.engines_used}",
                    f"Required primary engines: {self.required_engines['primary']}"
                ],
                recommendations=[
                    "Implement missing primary engines immediately",
                    "Add fallback mechanisms for engine failures",
                    "Monitor engine availability in real-time"
                ],
                impact_score=10
            ))
        
        # Verificar diversidade de engines
        if len(metrics.engines_used) < self.feedback_threshold['min_engines_required']:
            feedback.append(CriticalFeedback(
                severity='HIGH',
                category='ENGINE_COVERAGE',
                issue=f"Insufficient engine diversity ({len(metrics.engines_used)}/{self.feedback_threshold['min_engines_required']})",
                evidence=[
                    f"Only using: {metrics.engines_used}",
                    f"Missing fallback engines: {[e for e in self.required_engines['fallback'] if e not in metrics.engines_used]}"
                ],
                recommendations=[
                    "Add Google SERP engine as fallback for when Transparency Center fails",
                    "Ensure both Transparency Center engines are operational",
                    "Focus on engines that return real advertiser_id data"
                ],
                impact_score=8
            ))
        
        # CRITICAL: Verificar se temos engines que retornam dados reais de ads
        transparency_engines = [eng for eng in metrics.engines_used 
                               if 'transparency_center' in eng]
        
        if not transparency_engines:
            feedback.append(CriticalFeedback(
                severity='CRITICAL',
                category='ENGINE_COVERAGE',
                issue="No Transparency Center engines - zero real ads data",
                evidence=[
                    f"Current engines: {metrics.engines_used}",
                    "No source for advertiser_id or real ad creatives",
                    "GATE 5 (Ad Investment Verification) will fail for all prospects"
                ],
                recommendations=[
                    "IMMEDIATELY implement google_ads_transparency_center_advertiser_search",
                    "Add google_ads_transparency_center as backup",
                    "Remove non-Transparency engines that don't provide advertiser_id",
                    "Focus exclusively on engines with real ads data"
                ],
                impact_score=10
            ))
        
        return feedback
    
    def _analyze_qualification_rates(self, 
                                   metrics: PerformanceMetrics,
                                   historical_data: List[Dict] = None) -> List[CriticalFeedback]:
        """Análise crítica das taxas de qualificação"""
        feedback = []
        
        # Taxa de qualificação muito baixa
        if metrics.qualification_rate < self.feedback_threshold['qualification_rate_min']:
            feedback.append(CriticalFeedback(
                severity='CRITICAL',
                category='QUALIFICATION_RATE',
                issue=f"Extremely low qualification rate: {metrics.qualification_rate:.1%}",
                evidence=[
                    f"Only {metrics.prospects_qualified}/{metrics.prospects_discovered} prospects qualified",
                    f"Below minimum threshold of {self.feedback_threshold['qualification_rate_min']:.1%}",
                    f"High discovery volume but low conversion suggests filter issues"
                ],
                recommendations=[
                    "Review and relax qualification gates - may be too restrictive",
                    "Analyze rejected prospects for pattern identification",
                    "Implement gradual scoring instead of binary gates",
                    "Add business legitimacy verification fallbacks"
                ],
                impact_score=9
            ))
        
        # Zero qualificações - pipeline crítico
        if metrics.prospects_qualified == 0:
            feedback.append(CriticalFeedback(
                severity='CRITICAL',
                category='QUALIFICATION_RATE',
                issue="ZERO prospects qualified - pipeline failure",
                evidence=[
                    f"Discovered {metrics.prospects_discovered} prospects but qualified none",
                    "Complete pipeline breakdown in qualification phase",
                    "System may be rejecting all legitimate prospects"
                ],
                recommendations=[
                    "Emergency review of qualification gates",
                    "Implement debug mode for gate analysis",
                    "Add manual qualification override capabilities",
                    "Review business quality scoring algorithm"
                ],
                impact_score=10
            ))
        
        return feedback
    
    def _analyze_cost_efficiency(self, metrics: PerformanceMetrics) -> List[CriticalFeedback]:
        """Análise de eficiência de custo"""
        feedback = []
        
        if metrics.cost_per_lead > self.feedback_threshold['cost_per_lead_max']:
            feedback.append(CriticalFeedback(
                severity='HIGH',
                category='COST_EFFICIENCY',
                issue=f"Cost per lead too high: ${metrics.cost_per_lead:.2f}",
                evidence=[
                    f"Above maximum threshold of ${self.feedback_threshold['cost_per_lead_max']:.2f}",
                    f"Credits used: {metrics.total_credits_used}",
                    f"Leads qualified: {metrics.prospects_qualified}"
                ],
                recommendations=[
                    "Optimize query strategies to reduce API calls",
                    "Implement better prospect pre-filtering",
                    "Use cache mechanisms for repeated queries",
                    "Prioritize higher-yield engine combinations"
                ],
                impact_score=7
            ))
        
        return feedback
    
    def _analyze_data_quality(self, execution_data: Dict) -> List[CriticalFeedback]:
        """Análise da qualidade dos dados"""
        feedback = []
        
        # Verificar dados de performance ausentes
        execution_str = str(execution_data)
        performance_keywords = ['performance', 'metrics', 'lcp', 'fcp', 'cls']
        performance_data_available = any(keyword in execution_str.lower() for keyword in performance_keywords)
        
        if not performance_data_available:
            feedback.append(CriticalFeedback(
                severity='HIGH',
                category='DATA_QUALITY',
                issue="Performance data unavailable for most prospects",
                evidence=[
                    "No Core Web Vitals data detected in execution",
                    "Performance analysis appears to be failing",
                    "Missing critical optimization opportunities"
                ],
                recommendations=[
                    "Debug PageSpeed API integration",
                    "Implement fallback performance estimation",
                    "Add performance data availability tracking",
                    "Consider alternative performance data sources"
                ],
                impact_score=8
            ))
        
        return feedback
    
    def _analyze_technical_performance(self, metrics: PerformanceMetrics) -> List[CriticalFeedback]:
        """Análise de performance técnica"""
        feedback = []
        
        if metrics.avg_response_time_ms > self.feedback_threshold['response_time_max']:
            feedback.append(CriticalFeedback(
                severity='MEDIUM',
                category='TECHNICAL_PERFORMANCE',
                issue=f"Slow API response times: {metrics.avg_response_time_ms:.0f}ms",
                evidence=[
                    f"Above threshold of {self.feedback_threshold['response_time_max']}ms",
                    "Impacting pipeline execution speed"
                ],
                recommendations=[
                    "Implement request timeout optimization",
                    "Add concurrent API call processing",
                    "Consider API response caching",
                    "Monitor API endpoint performance"
                ],
                impact_score=5
            ))
        
        if metrics.errors_count > 5:
            feedback.append(CriticalFeedback(
                severity='HIGH',
                category='TECHNICAL_PERFORMANCE',
                issue=f"High error count: {metrics.errors_count} errors",
                evidence=[
                    f"Error rate affecting pipeline reliability",
                    f"Warnings: {metrics.warnings_count}"
                ],
                recommendations=[
                    "Implement better error handling",
                    "Add retry mechanisms for transient failures",
                    "Monitor API error patterns",
                    "Add circuit breaker for failing services"
                ],
                impact_score=8
            ))
        
        return feedback
    
    def _extract_metrics(self, execution_data: Dict) -> PerformanceMetrics:
        """Extrai métricas da execução"""
        # Mock implementation - adapt based on actual execution data structure
        return PerformanceMetrics(
            execution_id=execution_data.get('execution_id', 'unknown'),
            start_time=datetime.now() - timedelta(hours=1),
            end_time=datetime.now(),
            total_credits_used=execution_data.get('credits_used', 0),
            prospects_discovered=execution_data.get('prospects_discovered', 0),
            prospects_qualified=execution_data.get('prospects_qualified', 0),
            qualification_rate=execution_data.get('qualification_rate', 0.0),
            cost_per_lead=execution_data.get('cost_per_lead', 0.0),
            engines_used=execution_data.get('engines_used', []),
            errors_count=execution_data.get('errors_count', 0),
            warnings_count=execution_data.get('warnings_count', 0),
            avg_response_time_ms=execution_data.get('avg_response_time_ms', 0.0)
        )
    
    async def generate_improvement_plan(self, feedback_items: List[CriticalFeedback]) -> Dict[str, Any]:
        """Gera plano de melhorias baseado no feedback"""
        
        critical_items = [f for f in feedback_items if f.severity == 'CRITICAL']
        high_items = [f for f in feedback_items if f.severity == 'HIGH']
        
        plan = {
            'immediate_actions': [],
            'short_term_improvements': [],
            'long_term_optimizations': [],
            'priority_matrix': {}
        }
        
        # Ações imediatas (críticas)
        for item in critical_items:
            plan['immediate_actions'].extend(item.recommendations)
        
        # Melhorias de curto prazo (altas)
        for item in high_items:
            plan['short_term_improvements'].extend(item.recommendations)
        
        # Matriz de prioridade
        for category in ['ENGINE_COVERAGE', 'QUALIFICATION_RATE', 'COST_EFFICIENCY', 'DATA_QUALITY']:
            category_items = [f for f in feedback_items if f.category == category]
            plan['priority_matrix'][category] = {
                'count': len(category_items),
                'max_severity': max([f.severity for f in category_items], default='LOW'),
                'total_impact': sum([f.impact_score for f in category_items])
            }
        
        return plan

async def run_feedback_analysis(execution_data: Dict) -> Dict[str, Any]:
    """Função principal para executar análise de feedback"""
    engine = AutoFeedbackEngine()
    feedback_items = await engine.analyze_pipeline_performance(execution_data)
    improvement_plan = await engine.generate_improvement_plan(feedback_items)
    
    return {
        'feedback_items': [
            {
                'severity': f.severity,
                'category': f.category,
                'issue': f.issue,
                'recommendations': f.recommendations,
                'impact_score': f.impact_score
            }
            for f in feedback_items
        ],
        'improvement_plan': improvement_plan,
        'summary': {
            'total_issues': len(feedback_items),
            'critical_issues': len([f for f in feedback_items if f.severity == 'CRITICAL']),
            'high_issues': len([f for f in feedback_items if f.severity == 'HIGH']),
            'overall_health_score': max(0, 100 - sum([f.impact_score for f in feedback_items]))
        }
    }
