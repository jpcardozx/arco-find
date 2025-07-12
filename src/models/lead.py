# src/models/lead.py

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class OptimizationInsight:
    category: str
    details: str = ""
    potential_savings: Optional[float] = None
    performance_score: Optional[int] = None
    ad_metrics: Optional[Dict[str, Any]] = None  # Novas métricas para performance de anúncios
    recommendations: List[str] = field(default_factory=list)

@dataclass
class Lead:
    id: str
    company_name: str
    website: str
    employee_count: Optional[int] = None
    revenue_range: Optional[str] = None
    saas_spend: Optional[float] = None
    optimization_potential_score: Optional[int] = None # Score de 0-100
    insights: List[OptimizationInsight] = field(default_factory=list)
    missed_opportunities: List[Dict[str, Any]] = field(default_factory=list) # Adicionado para oportunidades perdidas
    status: str = "new" # new, analyzed, qualified, converted
    created_at: str = field(default_factory=lambda: "") # Placeholder for datetime

    def __post_init__(self):
        # Simples placeholder para data de criação
        import datetime
        self.created_at = datetime.datetime.now().isoformat()

    def add_insight(self, insight: OptimizationInsight):
        self.insights.append(insight)

    def calculate_optimization_score(self):
        """
        Calcula um score de otimização para o lead.
        (Placeholder: Esta é uma lógica simplificada e será expandida com base em análises reais.)
        """
        total_score = 0
        if self.saas_spend and self.saas_spend > 0:
            total_score += 30 # Base por ter gasto SaaS
        
        for insight in self.insights:
            if insight.potential_savings:
                total_score += 40 # Por ter economia potencial
            if insight.performance_score and insight.performance_score < 80:
                total_score += 30 # Por ter performance abaixo do ideal
        
        self.optimization_potential_score = min(total_score, 100)

# Exemplo de uso (para teste interno)
if __name__ == "__main__":
    insight1 = OptimizationInsight(
        category="SaaS Cost Optimization",
        potential_savings=1500.0,
        details="Consolidar ferramentas de CRM e automação de marketing.",
        recommendations=["Avaliar HubSpot vs Salesforce", "Negociar licenças em volume"]
    )

    insight2 = OptimizationInsight(
        category="Website Performance Improvement",
        performance_score=65,
        details="Otimizar imagens e habilitar cache de navegador.",
        recommendations=["Usar CDN", "Comprimir imagens"]
    )

    lead = Lead(
        id="lead_001",
        company_name="Tech Solutions Inc.",
        website="https://techsolutions.com",
        employee_count=45,
        revenue_range="$5M-$10M",
        saas_spend=8000.0
    )

    lead.add_insight(insight1)
    lead.add_insight(insight2)
    lead.calculate_optimization_score()

    print(f"Lead ID: {lead.id}")
    print(f"Company: {lead.company_name}")
    print(f"Website: {lead.website}")
    print(f"SaaS Spend: ${lead.saas_spend}")
    print(f"Optimization Potential Score: {lead.optimization_potential_score}")
    print("Insights:")
    for insight in lead.insights:
        print(f"  - Category: {insight.category}")
        print(f"    Details: {insight.details}")
        print(f"    Recommendations: {', '.join(insight.recommendations)}")