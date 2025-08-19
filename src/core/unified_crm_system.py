#!/usr/bin/env python3
"""
ARCO Unified CRM Enrichment System
=================================
Consolida todos os layers de análise em um único sistema de enriquecimento CRM.
Substitui os outputs separados por camada por enriquecimento batch unificado.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class UnifiedLead:
    """Lead unificado com dados consolidados de todos os layers"""
    # Identificação básica
    company_name: str
    domain: str
    industry: str
    country: str
    
    # Layer 1: Seed data
    search_keywords: List[str]
    ad_volume_score: int
    estimated_monthly_spend: float
    
    # Layer 2: Advertiser consolidation  
    confirmed_advertiser: bool
    advertising_platforms: List[str]
    creative_diversity_score: float
    
    # Layer 3: Ad details analysis
    campaign_strategies: List[str]
    target_audiences: List[str]
    creative_themes: List[str]
    
    # Pain signals (strategic focus)
    pain_signals: List[Dict[str, Any]]
    growth_opportunities: List[Dict[str, Any]]
    urgency_score: float  # 0-100
    
    # Strategic scoring
    lead_quality_score: float  # 0-100 baseado em pain signals e growth
    outreach_priority: str  # "high", "medium", "low"
    recommended_approach: Dict[str, str]
    
    # Metadata
    enriched_timestamp: str
    data_sources: List[str]
    confidence_level: float  # 0-100

class PainSignalDetector:
    """Detecta sinais reais de dor baseados em dados técnicos e de mercado"""
    
    def __init__(self):
        self.pain_signal_rules = {
            "performance_issues": {
                "indicators": ["high_bounce_rate", "slow_loading", "mobile_issues"],
                "severity_multiplier": 1.5,
                "urgency_boost": 20
            },
            "advertising_inefficiency": {
                "indicators": ["high_cpa", "low_conversion_rate", "broad_targeting"],
                "severity_multiplier": 1.3,
                "urgency_boost": 15
            },
            "growth_stagnation": {
                "indicators": ["declining_traffic", "low_engagement", "outdated_creative"],
                "severity_multiplier": 1.2,
                "urgency_boost": 10
            },
            "competitive_pressure": {
                "indicators": ["competitor_surge", "market_saturation", "price_pressure"],
                "severity_multiplier": 1.4,
                "urgency_boost": 25
            }
        }
    
    def detect_pain_signals(self, lead_data: Dict) -> List[Dict[str, Any]]:
        """Detecta pain signals reais baseados nos dados do lead"""
        pain_signals = []
        
        # Performance pain signals
        if lead_data.get("performance_score", 100) < 60:
            pain_signals.append({
                "type": "performance_issues",
                "description": "Site performance below industry standards",
                "severity": "high",
                "estimated_revenue_impact": self._calculate_performance_impact(lead_data),
                "urgency_days": 30,
                "solution_category": "technical_optimization"
            })
        
        # Advertising efficiency pain signals
        if lead_data.get("estimated_cpa", 0) > 150:  # High CPA threshold
            pain_signals.append({
                "type": "advertising_inefficiency", 
                "description": "High cost per acquisition indicates targeting issues",
                "severity": "medium",
                "estimated_revenue_impact": self._calculate_ad_waste(lead_data),
                "urgency_days": 45,
                "solution_category": "campaign_optimization"
            })
        
        # Growth opportunity pain signals
        if lead_data.get("creative_diversity_score", 0) < 0.3:
            pain_signals.append({
                "type": "growth_stagnation",
                "description": "Low creative diversity suggests limited testing/optimization",
                "severity": "low",
                "estimated_revenue_impact": self._calculate_growth_opportunity(lead_data),
                "urgency_days": 90,
                "solution_category": "creative_strategy"
            })
        
        return pain_signals
    
    def _calculate_performance_impact(self, lead_data: Dict) -> float:
        """Calcula impacto financeiro de problemas de performance"""
        base_spend = lead_data.get("estimated_monthly_spend", 5000)
        performance_score = lead_data.get("performance_score", 100)
        
        # Performance ruim pode causar 20-40% de perda de conversões
        impact_factor = (100 - performance_score) / 100 * 0.3
        return base_spend * impact_factor
    
    def _calculate_ad_waste(self, lead_data: Dict) -> float:
        """Calcula desperdício em publicidade por targeting ruim"""
        monthly_spend = lead_data.get("estimated_monthly_spend", 5000)
        cpa = lead_data.get("estimated_cpa", 100)
        
        # CPA alto indica 15-30% de desperdício
        if cpa > 200:
            waste_factor = 0.3
        elif cpa > 150:
            waste_factor = 0.2
        else:
            waste_factor = 0.1
            
        return monthly_spend * waste_factor
    
    def _calculate_growth_opportunity(self, lead_data: Dict) -> float:
        """Calcula oportunidade de crescimento por otimização"""
        base_spend = lead_data.get("estimated_monthly_spend", 5000)
        
        # Otimização criativa pode gerar 10-25% de uplift
        return base_spend * 0.15

class GrowthOpportunityAnalyzer:
    """Analisa oportunidades reais de crescimento baseadas em gaps de mercado"""
    
    def analyze_growth_opportunities(self, lead_data: Dict) -> List[Dict[str, Any]]:
        """Identifica oportunidades reais de crescimento"""
        opportunities = []
        
        # Market expansion opportunities
        if len(lead_data.get("advertising_platforms", [])) < 3:
            opportunities.append({
                "type": "platform_expansion",
                "description": "Expand to additional advertising platforms",
                "potential_revenue_increase": self._calculate_platform_expansion(lead_data),
                "implementation_timeline": "4-8 weeks",
                "investment_required": "medium",
                "roi_timeline": "2-3 months"
            })
        
        # Creative optimization opportunities  
        if lead_data.get("creative_diversity_score", 0) < 0.5:
            opportunities.append({
                "type": "creative_optimization",
                "description": "Implement systematic creative testing framework",
                "potential_revenue_increase": self._calculate_creative_uplift(lead_data),
                "implementation_timeline": "2-4 weeks", 
                "investment_required": "low",
                "roi_timeline": "1-2 months"
            })
        
        # Audience expansion opportunities
        if len(lead_data.get("target_audiences", [])) < 5:
            opportunities.append({
                "type": "audience_expansion",
                "description": "Expand target audience segments with lookalike modeling",
                "potential_revenue_increase": self._calculate_audience_expansion(lead_data),
                "implementation_timeline": "3-6 weeks",
                "investment_required": "medium", 
                "roi_timeline": "2-4 months"
            })
        
        return opportunities
    
    def _calculate_platform_expansion(self, lead_data: Dict) -> float:
        """Calcula potencial de expansão para novas plataformas"""
        current_spend = lead_data.get("estimated_monthly_spend", 5000)
        # Expansão de plataforma pode gerar 30-60% de aumento
        return current_spend * 0.45
    
    def _calculate_creative_uplift(self, lead_data: Dict) -> float:
        """Calcula uplift de otimização criativa"""
        current_spend = lead_data.get("estimated_monthly_spend", 5000)
        # Otimização criativa gera 15-35% de improvement
        return current_spend * 0.25
    
    def _calculate_audience_expansion(self, lead_data: Dict) -> float:
        """Calcula potencial de expansão de audiência"""
        current_spend = lead_data.get("estimated_monthly_spend", 5000)
        # Expansão de audiência pode gerar 20-40% de aumento
        return current_spend * 0.30

class UnifiedCRMEnrichmentEngine:
    """Engine principal de enriquecimento CRM unificado"""
    
    def __init__(self, output_dir: str = "data/unified_crm"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.pain_detector = PainSignalDetector()
        self.opportunity_analyzer = GrowthOpportunityAnalyzer()
        
        # Configurações de scoring estratégico
        self.scoring_weights = {
            "pain_signals": 0.4,
            "growth_opportunities": 0.3,
            "advertising_volume": 0.2,
            "technical_readiness": 0.1
        }
    
    def enrich_lead_batch(self, raw_leads: List[Dict]) -> List[UnifiedLead]:
        """Enriquece um batch de leads com análise unificada"""
        logger.info(f"Starting unified enrichment for {len(raw_leads)} leads")
        
        enriched_leads = []
        
        for raw_lead in raw_leads:
            try:
                enriched_lead = self._enrich_single_lead(raw_lead)
                enriched_leads.append(enriched_lead)
                
            except Exception as e:
                logger.error(f"Error enriching lead {raw_lead.get('domain', 'unknown')}: {e}")
                continue
        
        # Save unified batch
        self._save_enriched_batch(enriched_leads)
        
        logger.info(f"Successfully enriched {len(enriched_leads)} leads")
        return enriched_leads
    
    def _enrich_single_lead(self, raw_lead: Dict) -> UnifiedLead:
        """Enriquece um lead individual com dados consolidados"""
        
        # Detectar pain signals
        pain_signals = self.pain_detector.detect_pain_signals(raw_lead)
        
        # Analisar growth opportunities  
        growth_opportunities = self.opportunity_analyzer.analyze_growth_opportunities(raw_lead)
        
        # Calcular scoring estratégico
        lead_quality_score = self._calculate_strategic_score(raw_lead, pain_signals, growth_opportunities)
        urgency_score = self._calculate_urgency_score(pain_signals)
        
        # Determinar abordagem recomendada
        recommended_approach = self._determine_outreach_approach(lead_quality_score, pain_signals, growth_opportunities)
        
        # Prioridade de outreach
        outreach_priority = self._determine_priority(lead_quality_score, urgency_score)
        
        return UnifiedLead(
            # Basic identification
            company_name=raw_lead.get("company_name", "Unknown"),
            domain=raw_lead.get("domain", ""),
            industry=raw_lead.get("industry", "Unknown"),
            country=raw_lead.get("country", "Unknown"),
            
            # Layer data consolidated
            search_keywords=raw_lead.get("search_keywords", []),
            ad_volume_score=raw_lead.get("ad_volume_score", 0),
            estimated_monthly_spend=raw_lead.get("estimated_monthly_spend", 0),
            
            confirmed_advertiser=raw_lead.get("confirmed_advertiser", False),
            advertising_platforms=raw_lead.get("advertising_platforms", []),
            creative_diversity_score=raw_lead.get("creative_diversity_score", 0),
            
            campaign_strategies=raw_lead.get("campaign_strategies", []),
            target_audiences=raw_lead.get("target_audiences", []),
            creative_themes=raw_lead.get("creative_themes", []),
            
            # Strategic analysis
            pain_signals=pain_signals,
            growth_opportunities=growth_opportunities,
            urgency_score=urgency_score,
            
            lead_quality_score=lead_quality_score,
            outreach_priority=outreach_priority,
            recommended_approach=recommended_approach,
            
            # Metadata
            enriched_timestamp=datetime.now().isoformat(),
            data_sources=raw_lead.get("data_sources", ["searchapi_layers"]),
            confidence_level=self._calculate_confidence_level(raw_lead)
        )
    
    def _calculate_strategic_score(self, raw_lead: Dict, pain_signals: List[Dict], growth_opportunities: List[Dict]) -> float:
        """Calcula score estratégico baseado em pain signals e oportunidades"""
        
        # Pain signals score (0-40 points)
        pain_score = min(len(pain_signals) * 15 + sum(
            20 if p["severity"] == "high" else 10 if p["severity"] == "medium" else 5 
            for p in pain_signals
        ), 40)
        
        # Growth opportunities score (0-30 points)
        growth_score = min(len(growth_opportunities) * 10 + sum(
            15 if "high" in str(g.get("potential_revenue_increase", 0)) else 10
            for g in growth_opportunities
        ), 30)
        
        # Advertising volume score (0-20 points)
        ad_volume = raw_lead.get("estimated_monthly_spend", 0)
        if ad_volume > 10000:
            volume_score = 20
        elif ad_volume > 5000:
            volume_score = 15
        elif ad_volume > 2000:
            volume_score = 10
        else:
            volume_score = 5
        
        # Technical readiness score (0-10 points) 
        tech_score = min(raw_lead.get("performance_score", 50) / 10, 10)
        
        total_score = pain_score + growth_score + volume_score + tech_score
        return min(total_score, 100)
    
    def _calculate_urgency_score(self, pain_signals: List[Dict]) -> float:
        """Calcula urgência baseada nos pain signals"""
        if not pain_signals:
            return 0
        
        urgency_days = [p.get("urgency_days", 90) for p in pain_signals]
        avg_urgency = sum(urgency_days) / len(urgency_days)
        
        # Converte dias em score 0-100 (menos dias = mais urgente)
        urgency_score = max(0, 100 - (avg_urgency / 2))
        return urgency_score
    
    def _determine_outreach_approach(self, quality_score: float, pain_signals: List[Dict], growth_opportunities: List[Dict]) -> Dict[str, str]:
        """Determina abordagem de outreach baseada na análise"""
        
        if quality_score >= 80:
            return {
                "approach": "consultative_strategic",
                "key_message": "Revenue optimization and growth acceleration", 
                "timeline": "immediate",
                "decision_maker": "VP Growth/CMO"
            }
        elif quality_score >= 60:
            return {
                "approach": "solution_focused",
                "key_message": "Solve specific pain points with measurable ROI",
                "timeline": "2-4 weeks",
                "decision_maker": "Marketing Manager"
            }
        else:
            return {
                "approach": "educational_nurture",
                "key_message": "Industry insights and best practices",
                "timeline": "6-8 weeks", 
                "decision_maker": "Marketing Team"
            }
    
    def _determine_priority(self, quality_score: float, urgency_score: float) -> str:
        """Determina prioridade de outreach"""
        combined_score = (quality_score * 0.7) + (urgency_score * 0.3)
        
        if combined_score >= 75:
            return "high"
        elif combined_score >= 50:
            return "medium"
        else:
            return "low"
    
    def _calculate_confidence_level(self, raw_lead: Dict) -> float:
        """Calcula nível de confiança dos dados"""
        confidence_factors = []
        
        # Data source diversity
        sources = raw_lead.get("data_sources", [])
        confidence_factors.append(min(len(sources) * 20, 40))
        
        # Advertising confirmation
        if raw_lead.get("confirmed_advertiser", False):
            confidence_factors.append(30)
        else:
            confidence_factors.append(10)
        
        # Technical data availability
        if raw_lead.get("performance_score") is not None:
            confidence_factors.append(20)
        else:
            confidence_factors.append(5)
        
        # Spend estimation accuracy
        if raw_lead.get("estimated_monthly_spend", 0) > 1000:
            confidence_factors.append(10)
        else:
            confidence_factors.append(3)
        
        return min(sum(confidence_factors), 100)
    
    def _save_enriched_batch(self, enriched_leads: List[UnifiedLead]) -> str:
        """Salva batch enriquecido em formato unificado"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"unified_crm_batch_{timestamp}.json"
        filepath = self.output_dir / filename
        
        # Convert to serializable format
        leads_data = [asdict(lead) for lead in enriched_leads]
        
        # Add batch metadata
        batch_data = {
            "batch_metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_leads": len(enriched_leads),
                "high_priority_leads": len([l for l in enriched_leads if l.outreach_priority == "high"]),
                "average_quality_score": sum(l.lead_quality_score for l in enriched_leads) / len(enriched_leads) if enriched_leads else 0,
                "total_estimated_opportunity": sum(
                    sum(opp.get("potential_revenue_increase", 0) for opp in l.growth_opportunities)
                    for l in enriched_leads
                )
            },
            "leads": leads_data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(batch_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Unified CRM batch saved: {filepath}")
        return str(filepath)

# Demo function for testing
def demo_unified_crm_system():
    """Demo do sistema unificado de CRM"""
    
    # Sample lead data (seria vindo dos layers consolidados)
    sample_leads = [
        {
            "company_name": "TechCorp Solutions",
            "domain": "techcorp.com",
            "industry": "Software",
            "country": "US",
            "search_keywords": ["crm software", "sales automation"],
            "ad_volume_score": 85,
            "estimated_monthly_spend": 15000,
            "confirmed_advertiser": True,
            "advertising_platforms": ["google", "meta"],
            "creative_diversity_score": 0.3,
            "campaign_strategies": ["lead_generation"],
            "target_audiences": ["business_owners"],
            "creative_themes": ["efficiency"],
            "performance_score": 45,
            "estimated_cpa": 180,
            "data_sources": ["searchapi_layer1", "searchapi_layer2", "searchapi_layer3"]
        }
    ]
    
    # Initialize unified CRM system
    crm_engine = UnifiedCRMEnrichmentEngine()
    
    # Enrich leads
    enriched_leads = crm_engine.enrich_lead_batch(sample_leads)
    
    # Display results
    print("\n🎯 UNIFIED CRM ENRICHMENT RESULTS")
    print("=" * 50)
    
    for lead in enriched_leads:
        print(f"\n Company: {lead.company_name}")
        print(f" Quality Score: {lead.lead_quality_score:.1f}/100")
        print(f" Priority: {lead.outreach_priority.upper()}")
        print(f" Pain Signals: {len(lead.pain_signals)}")
        print(f" Growth Opportunities: {len(lead.growth_opportunities)}")
        print(f" Recommended Approach: {lead.recommended_approach['approach']}")
        
        if lead.pain_signals:
            print(f" Top Pain Signal: {lead.pain_signals[0]['description']}")
        
        if lead.growth_opportunities:
            print(f" Top Opportunity: {lead.growth_opportunities[0]['description']}")

if __name__ == "__main__":
    demo_unified_crm_system()