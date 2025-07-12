# src/analysis/missed_opportunity_detector.py

from src.utils.logger import logger
from typing import List, Dict, Any

class MissedOpportunityDetector:
    """
    Detecta oportunidades perdidas com base em insights de otimização.
    (Placeholder Conceitual: A lógica real de detecção de oportunidades seria complexa
    e baseada em regras de negócio, machine learning, etc.)
    """
    def __init__(self):
        logger.info("MissedOpportunityDetector initialized.")

    def detect_opportunities(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Simula a detecção de oportunidades perdidas com base nos insights fornecidos.
        
        Args:
            insights (List[Dict[str, Any]]): Lista de insights de otimização.
            
        Returns:
            List[Dict[str, Any]]: Lista de oportunidades perdidas detectadas.
        """
        logger.info("Detecting missed opportunities...")
        opportunities = []

        # Exemplo de lógica de detecção de oportunidade (simulada)
        for insight in insights:
            if insight["category"] == "SaaS Cost Optimization" and insight.get("potential_savings", 0) > 1000:
                opportunities.append({
                    "type": "High SaaS Savings Potential",
                    "description": f"Grande oportunidade de economia em SaaS: ${insight['potential_savings']:.2f} anuais.",
                    "action": "Priorizar revisão de contratos e consolidação de ferramentas."
                })
            
            if insight["category"] == "Website Performance Improvement" and insight.get("performance_score", 100) < 60:
                opportunities.append({
                    "type": "Critical Website Performance",
                    "description": f"Performance crítica do website: Score {insight['performance_score']}. Impacta SEO e experiência do usuário.",
                    "action": "Investir em otimização de imagens, cache e infraestrutura."
                })
            
            if insight["category"] == "Ad Performance Optimization" and insight.get("ad_metrics", {}).get("cpa", 0) > 150:
                opportunities.append({
                    "type": "High CPA in Ads",
                    "description": f"Custo por aquisição (CPA) muito alto em anúncios: ${insight['ad_metrics']['cpa']:.2f}. Desperdício de orçamento.",
                    "action": "Revisar segmentação, criativos e lances de campanha."
                })

        logger.info(f"Detected {len(opportunities)} missed opportunities.")
        return opportunities

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