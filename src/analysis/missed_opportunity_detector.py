# src/analysis/missed_opportunity_detector.py

from src.utils.logger import logger
from typing import List, Dict, Any
import math

class MissedOpportunityDetector:
    """
    Detecta oportunidades perdidas com base em insights de otimização,
    gerando recomendações específicas e acionáveis para vendas e leads.
    """
    def __init__(self):
        self.industry_benchmarks = {
            'dental': {'avg_cpa': 120, 'good_conversion_rate': 0.08, 'avg_monthly_spend': 8000},
            'legal': {'avg_cpa': 200, 'good_conversion_rate': 0.05, 'avg_monthly_spend': 12000},
            'healthcare': {'avg_cpa': 150, 'good_conversion_rate': 0.06, 'avg_monthly_spend': 10000},
            'saas': {'avg_cpa': 80, 'good_conversion_rate': 0.12, 'avg_monthly_spend': 15000},
            'ecommerce': {'avg_cpa': 45, 'good_conversion_rate': 0.15, 'avg_monthly_spend': 20000}
        }
        logger.info("MissedOpportunityDetector initialized with industry benchmarks.")

    def detect_opportunities(self, insights: List[Dict[str, Any]], industry: str = 'general') -> List[Dict[str, Any]]:
        """
        Detecta oportunidades perdidas específicas e acionáveis com base nos insights fornecidos.
        
        Args:
            insights (List[Dict[str, Any]]): Lista de insights de otimização.
            industry (str): Indústria da empresa para benchmarking específico.
            
        Returns:
            List[Dict[str, Any]]: Lista de oportunidades específicas e acionáveis.
        """
        logger.info(f"Detecting missed opportunities for industry: {industry}")
        opportunities = []
        
        benchmarks = self.industry_benchmarks.get(industry, self.industry_benchmarks['saas'])

        for insight in insights:
            # Análise de custos SaaS com recomendações específicas
            if insight["category"] == "SaaS Cost Optimization":
                potential_savings = insight.get("potential_savings", 0)
                if potential_savings > 2000:
                    opportunities.append({
                        "type": "High-Impact SaaS Consolidation",
                        "description": f"Economia anual potencial de ${potential_savings * 12:,.0f} identificada em stack SaaS",
                        "action": "Conduzir auditoria de 48h das ferramentas ativas vs. licenças pagas",
                        "timeline": "2 semanas",
                        "roi_estimate": f"${potential_savings * 10:,.0f} economia em 12 meses",
                        "priority": "high",
                        "sales_angle": "Demonstrar ROI imediato através de stack optimization"
                    })
                elif potential_savings > 500:
                    opportunities.append({
                        "type": "SaaS License Optimization",
                        "description": f"Oportunidade moderada de ${potential_savings * 12:,.0f}/ano em otimização SaaS",
                        "action": "Revisar planos e usage metrics das top 5 ferramentas SaaS",
                        "timeline": "1 semana",
                        "roi_estimate": f"${potential_savings * 8:,.0f} economia estimada",
                        "priority": "medium",
                        "sales_angle": "Quick win para mostrar value da consultoria"
                    })
            
            # Análise de performance web com impacto no negócio
            if insight["category"] == "Website Performance Improvement":
                performance_score = insight.get("performance_score", 100)
                if performance_score and performance_score < 40:
                    conversion_loss = self._calculate_conversion_impact(performance_score)
                    opportunities.append({
                        "type": "Critical Performance Revenue Leak",
                        "description": f"Performance Score {performance_score}/100 está causando perda estimada de {conversion_loss}% em conversões",
                        "action": "Implementar Core Web Vitals optimization: largest contentful paint, cumulative layout shift",
                        "timeline": "3-4 semanas",
                        "roi_estimate": f"Aumento de 25-40% em conversion rate esperado",
                        "priority": "critical",
                        "sales_angle": "Performance = Revenue. Cada segundo perdido = leads perdidos"
                    })
                elif performance_score and performance_score < 60:
                    opportunities.append({
                        "type": "Performance Optimization Opportunity", 
                        "description": f"Score {performance_score}/100 indica oportunidade de melhoria significativa",
                        "action": "Otimizar imagens, implement lazy loading, revisar plugins desnecessários",
                        "timeline": "2 semanas",
                        "roi_estimate": "10-15% melhoria em user experience e SEO",
                        "priority": "high",
                        "sales_angle": "Performance optimization como competitive advantage"
                    })
            
            # Análise de anúncios com benchmarks da indústria
            if insight["category"] in ["Ad Performance Optimization", "Meta Ad Performance Optimization"]:
                ad_metrics = insight.get("ad_metrics", {})
                cpa = ad_metrics.get("cpa", 0)
                industry_avg_cpa = benchmarks['avg_cpa']
                
                if cpa > industry_avg_cpa * 1.5:
                    waste_percentage = ((cpa - industry_avg_cpa) / cpa) * 100
                    monthly_waste = ad_metrics.get('spend', benchmarks['avg_monthly_spend']) * (waste_percentage / 100)
                    
                    opportunities.append({
                        "type": "High-Impact Ad Spend Optimization",
                        "description": f"CPA de ${cpa:.0f} está {waste_percentage:.0f}% acima do benchmark da indústria (${industry_avg_cpa})",
                        "action": "Reestruturar campaign targeting, implementar negative keywords, otimizar landing pages",
                        "timeline": "1-2 semanas",
                        "roi_estimate": f"${monthly_waste * 12:,.0f}/ano em savings potenciais",
                        "priority": "critical",
                        "sales_angle": f"Redução imediata de waste em ads - savings mensal de ${monthly_waste:,.0f}"
                    })
                elif cpa > industry_avg_cpa * 1.2:
                    opportunities.append({
                        "type": "Ad Campaign Efficiency Improvement",
                        "description": f"CPA ${cpa:.0f} indica room for improvement vs benchmark ${industry_avg_cpa}",
                        "action": "A/B test ad copy, refinar audience targeting, implement conversion tracking",
                        "timeline": "2-3 semanas", 
                        "roi_estimate": "15-25% melhoria em ad efficiency esperada",
                        "priority": "medium",
                        "sales_angle": "Optimization incremental para scaling sustainable"
                    })
        
        # Detectar oportunidades de cross-sell baseadas no profile
        cross_sell_opportunities = self._detect_cross_sell_opportunities(insights, industry)
        opportunities.extend(cross_sell_opportunities)

        logger.info(f"Detected {len(opportunities)} specific missed opportunities.")
        return opportunities
    
    def _calculate_conversion_impact(self, performance_score: float) -> float:
        """
        Calcula o impacto estimado da performance no conversion rate
        baseado em estudos de web performance.
        """
        # Baseado em research: 1 segundo de delay = 7% drop in conversions
        # Score abaixo de 50 = ~3-4 segundos loading time = ~20-25% conversion loss
        if performance_score < 30:
            return 35
        elif performance_score < 50:
            return 25
        elif performance_score < 70:
            return 15
        else:
            return 5
    
    def _detect_cross_sell_opportunities(self, insights: List[Dict[str, Any]], industry: str) -> List[Dict[str, Any]]:
        """
        Detecta oportunidades de cross-sell baseadas no profile da empresa.
        """
        opportunities = []
        
        has_ads = any(insight["category"] in ["Ad Performance Optimization", "Meta Ad Performance Optimization"] for insight in insights)
        has_website_issues = any(insight["category"] == "Website Performance Improvement" and insight.get("performance_score", 100) < 70 for insight in insights)
        has_saas_spend = any(insight["category"] == "SaaS Cost Optimization" and insight.get("potential_savings", 0) > 1000 for insight in insights)
        
        if has_ads and has_website_issues:
            opportunities.append({
                "type": "Comprehensive Digital Optimization",
                "description": "Company tem ad spend + website performance issues = oportunidade full-stack optimization",
                "action": "Propor package: Ad optimization + website performance + conversion rate optimization",
                "timeline": "6-8 semanas",
                "roi_estimate": "Combined ROI 40-60% superior a initiatives isoladas",
                "priority": "high",
                "sales_angle": "Holistic approach - ads são waste se website não converte"
            })
        
        if has_saas_spend and industry in ['saas', 'tech']:
            opportunities.append({
                "type": "Tech Stack Audit & Optimization",
                "description": "Tech company com SaaS inefficiencies indica oportunidade de infrastructure review",
                "action": "Propor comprehensive tech audit: tools, processes, automation opportunities",
                "timeline": "4-6 semanas",
                "roi_estimate": "Typical ROI 300-500% em tech efficiency gains",
                "priority": "medium",
                "sales_angle": "Tech companies devem ser example de efficiency - não waste"
            })
        
        return opportunities

# Exemplo de uso (para teste interno)
if __name__ == "__main__":
    detector = MissedOpportunityDetector()
    sample_insights = [
        {
            "category": "SaaS Cost Optimization",
            "potential_savings": 2400.0,
            "details": "High SaaS spend identified",
            "recommendations": []
        },
        {
            "category": "Website Performance Improvement", 
            "performance_score": 35,
            "details": "Critical performance issues",
            "recommendations": []
        },
        {
            "category": "Ad Performance Optimization",
            "ad_metrics": {"cpa": 180.0, "spend": 8000},
            "details": "High CPA detected",
            "recommendations": []
        }
    ]
    opportunities = detector.detect_opportunities(sample_insights, industry='dental')
    logger.info(f"\nOportunidades Específicas Detectadas: {len(opportunities)}")
    for opp in opportunities:
        print(f"- {opp['type']}: {opp['sales_angle']}")

# Exemplo de uso (para teste interno)
if __name__ == "__main__":
    detector = MissedOpportunityDetector()
    sample_insights = [
        {
            "category": "SaaS Cost Optimization",
            "potential_savings": 1200.0,
            "details": "Detalhes de SaaS",
            "recommendations": []
        },
        {
            "category": "Website Performance Improvement",
            "performance_score": 55,
            "details": "Detalhes de Performance",
            "recommendations": []
        },
        {
            "category": "Ad Performance Optimization",
            "ad_metrics": {"cpa": 180.0},
            "details": "Detalhes de Ads",
            "recommendations": []
        }
    ]
    opportunities = detector.detect_opportunities(sample_insights)
    logger.info(f"\nOportunidades Detectadas: {opportunities}")