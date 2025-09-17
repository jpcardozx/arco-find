"""
ProspectOrchestrator - Main coordination service for comprehensive prospect analysis.

This orchestrator implements the professional service layer architecture,
coordinating multiple specialized services to analyze prospects with real data.
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from arco.models.prospect import Prospect, BusinessModel, CompanyScale, LeadScore, ActionableInsight, BusinessRecommendation, CRMProfile
from arco.services.business_intelligence_service import BusinessIntelligenceService
from arco.services.lead_scoring_service import LeadScoringService


class ProspectOrchestrator:
    """
    Main coordination service for comprehensive prospect analysis.
    
    Orchestrates the complete prospect analysis workflow using professional
    service layer architecture with dependency injection.
    """
    
    def __init__(self,
                 business_intelligence_service: BusinessIntelligenceService,
                 lead_scoring_service: LeadScoringService):
        """
        Initialize orchestrator with injected services.
        
        Args:
            business_intelligence_service: Service for collecting business intelligence
            lead_scoring_service: Service for calculating lead scores
        """
        self.business_intelligence_service = business_intelligence_service
        self.lead_scoring_service = lead_scoring_service
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def analyze_prospect_comprehensively(self, 
                                             prospect_data: Dict[str, Any]) -> ComprehensiveProspect:
        """
        Complete prospect analysis with all business intelligence.
        
        Args:
            prospect_data: Basic prospect data (domain, company_name, etc.)
            
        Returns:
            ComprehensiveProspect with complete analysis
        """
        company_name = prospect_data.get('company_name', '')
        domain = prospect_data.get('domain', '')
        
        self._logger.info(f"🔍 Analyzing {company_name} comprehensively")
        
        try:
            # 1. Collect Business Intelligence (Real Data Only)
            business_intel = await self.business_intelligence_service.collect_intelligence(
                domain, company_name
            )
            
            # 2. Classify business model and scale (placeholder - would be enhanced)
            business_model = self._classify_business_model(prospect_data)
            company_scale = self._classify_company_scale(prospect_data)
            
            # 3. Enhanced Lead Scoring (Budget Verification Focus)
            lead_score = await self.lead_scoring_service.calculate_enhanced_score(
                company_name=company_name,
                business_model=business_model,
                company_scale=company_scale,
                business_intelligence=business_intel
            )
            
            # 4. Create comprehensive prospect
            comprehensive_prospect = ComprehensiveProspect(
                id=prospect_data.get('id', f"{domain}_{company_name}"),
                company_name=company_name,
                domain=domain,
                industry=prospect_data.get('industry', ''),
                employee_count=prospect_data.get('employee_count', 0),
                country=prospect_data.get('country', ''),
                business_model=business_model,
                company_scale=company_scale,
                business_intelligence=business_intel,
                lead_score=lead_score,
                last_analyzed=datetime.now(),
                confidence_level=business_intel.data_quality_score
            )
            
            self._logger.info(
                f"✅ Analyzed {company_name}: "
                f"Score: {lead_score.total_score}/100 ({lead_score.temperature.value}), "
                f"Budget Signals: {len(await self.business_intelligence_service.get_budget_verification_signals(business_intel))}, "
                f"Data Quality: {business_intel.data_quality_score:.2f}"
            )
            
            return comprehensive_prospect
            
        except Exception as e:
            self._logger.error(f"❌ Failed to analyze {company_name}: {e}")
            raise
    
    async def process_prospects_batch(self, 
                                    prospects_data: List[Dict[str, Any]]) -> List[ComprehensiveProspect]:
        """
        Process multiple prospects with comprehensive analysis.
        
        Args:
            prospects_data: List of basic prospect data
            
        Returns:
            List of comprehensive prospects with analysis
        """
        self._logger.info(f"🚀 Processing {len(prospects_data)} prospects with comprehensive analysis")
        
        comprehensive_prospects = []
        
        # Process in batches to respect API rate limits
        batch_size = 5
        for i in range(0, len(prospects_data), batch_size):
            batch = prospects_data[i:i + batch_size]
            
            self._logger.info(f"📊 Processing batch {i//batch_size + 1}/{(len(prospects_data)-1)//batch_size + 1}")
            
            # Process batch concurrently
            batch_tasks = [
                self.analyze_prospect_comprehensively(prospect_data)
                for prospect_data in batch
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Handle results and exceptions
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    self._logger.error(f"❌ Failed to process {batch[j].get('company_name', 'Unknown')}: {result}")
                else:
                    comprehensive_prospects.append(result)
            
            # Rate limiting between batches
            if i + batch_size < len(prospects_data):
                await asyncio.sleep(2.0)
        
        # Sort by lead score
        comprehensive_prospects.sort(key=lambda p: p.lead_score.total_score, reverse=True)
        
        self._logger.info(
            f"🎯 Completed processing: {len(comprehensive_prospects)} prospects analyzed, "
            f"{len([p for p in comprehensive_prospects if p.is_hot_lead()])} hot leads identified"
        )
        
        return comprehensive_prospects
    
    def _classify_business_model(self, prospect_data: Dict[str, Any]) -> BusinessModel:
        """
        Classify business model based on prospect data.
        
        This is a placeholder implementation that would be enhanced with
        more sophisticated classification logic.
        """
        industry = prospect_data.get('industry', '').lower()
        domain = prospect_data.get('domain', '').lower()
        
        # Simple classification based on industry and domain patterns
        if 'saas' in industry or 'software' in industry:
            return BusinessModel.SAAS
        elif 'ecommerce' in industry or 'retail' in industry or 'shopify' in domain:
            return BusinessModel.ECOMMERCE
        elif 'service' in industry or 'consulting' in industry:
            return BusinessModel.SERVICE
        elif 'enterprise' in industry or prospect_data.get('employee_count', 0) > 1000:
            return BusinessModel.ENTERPRISE
        elif 'platform' in industry or 'marketplace' in industry:
            return BusinessModel.PLATFORM
        else:
            return BusinessModel.UNKNOWN
    
    def _classify_company_scale(self, prospect_data: Dict[str, Any]) -> CompanyScale:
        """
        Classify company scale based on employee count and other indicators.
        """
        employee_count = prospect_data.get('employee_count', 0)
        
        if employee_count >= 1000:
            return CompanyScale.MAJOR
        elif employee_count >= 200:
            return CompanyScale.ENTERPRISE
        elif employee_count >= 50:
            return CompanyScale.SMB
        else:
            return CompanyScale.STARTUP
    
    async def generate_executive_report(self, 
                                      prospects: List[ComprehensiveProspect]) -> Dict[str, Any]:
        """
        Generate executive summary report with key insights and ROI projections.
        
        Args:
            prospects: List of comprehensive prospects
            
        Returns:
            Executive report with strategic insights
        """
        hot_leads = [p for p in prospects if p.is_hot_lead()]
        blazing_leads = [p for p in prospects if p.lead_score.temperature.value == "BLAZING"]
        
        # Calculate aggregate metrics
        total_budget_signals = sum(
            len(await self.business_intelligence_service.get_budget_verification_signals(p.business_intelligence))
            for p in prospects
        )
        
        report = {
            'executive_summary': {
                'total_prospects_analyzed': len(prospects),
                'hot_leads_identified': len(hot_leads),
                'blazing_leads_identified': len(blazing_leads),
                'conversion_rate': round(len(hot_leads) / len(prospects) * 100, 1) if prospects else 0,
                'average_lead_score': round(sum(p.lead_score.total_score for p in prospects) / len(prospects), 1) if prospects else 0,
                'total_budget_signals': total_budget_signals
            },
            'top_prospects': [
                {
                    'company_name': p.company_name,
                    'domain': p.domain,
                    'lead_score': p.lead_score.total_score,
                    'temperature': p.lead_score.temperature.value,
                    'budget_verification_score': p.lead_score.budget_verification_score,
                    'partnership_potential': p.calculate_partnership_potential(),
                    'key_insights': [insight.title for insight in p.get_top_insights(3)],
                    'budget_signals': await self.business_intelligence_service.get_budget_verification_signals(p.business_intelligence)
                }
                for p in prospects[:10]  # Top 10
            ],
            'market_analysis': {
                'business_models': self._analyze_business_model_distribution(prospects),
                'company_scales': self._analyze_company_scale_distribution(prospects),
                'geographic_distribution': self._analyze_geographic_distribution(prospects)
            },
            'recommendations': self._generate_strategic_recommendations(prospects, hot_leads)
        }
        
        return report
    
    def _analyze_business_model_distribution(self, prospects: List[ComprehensiveProspect]) -> Dict[str, int]:
        """Analyze distribution of business models."""
        distribution = {}
        for prospect in prospects:
            model = prospect.business_model.value
            distribution[model] = distribution.get(model, 0) + 1
        return distribution
    
    def _analyze_company_scale_distribution(self, prospects: List[ComprehensiveProspect]) -> Dict[str, int]:
        """Analyze distribution of company scales."""
        distribution = {}
        for prospect in prospects:
            scale = prospect.company_scale.value
            distribution[scale] = distribution.get(scale, 0) + 1
        return distribution
    
    def _analyze_geographic_distribution(self, prospects: List[ComprehensiveProspect]) -> Dict[str, int]:
        """Analyze geographic distribution."""
        distribution = {}
        for prospect in prospects:
            country = prospect.country or 'Unknown'
            distribution[country] = distribution.get(country, 0) + 1
        return distribution
    
    def _generate_strategic_recommendations(self, 
                                         prospects: List[ComprehensiveProspect],
                                         hot_leads: List[ComprehensiveProspect]) -> List[str]:
        """Generate strategic recommendations based on analysis."""
        recommendations = []
        
        if len(hot_leads) > 0:
            recommendations.append(
                f"Immediate action required: {len(hot_leads)} hot leads identified with confirmed budget signals"
            )
        
        # Analyze budget verification patterns
        high_budget_prospects = [
            p for p in prospects 
            if p.lead_score.budget_verification_score >= 30
        ]
        
        if len(high_budget_prospects) > len(prospects) * 0.2:
            recommendations.append(
                "Strong market opportunity: 20%+ of prospects show strong budget verification signals"
            )
        
        # Analyze timing opportunities
        active_project_prospects = [
            p for p in prospects
            if p.business_intelligence.technology_investment.major_tech_project_active
        ]
        
        if len(active_project_prospects) > 0:
            recommendations.append(
                f"Timing opportunity: {len(active_project_prospects)} prospects have active technology projects"
            )
        
        return recommendations