from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class CompanyMetrics:
    """Representa as métricas de uma empresa para cálculo do score."""
    domain: str
    saas_tools_count: int = 0
    lcp: float = 0.0
    inp: float = 0.0
    ad_spend: float = 0.0
    estimated_saas_cost: float = 0.0
    recent_jobs_count: int = 0
    employee_count: int = 0 # Adicionado para cálculo de SaaS Cost

class ICP:
    """Define um Perfil de Cliente Ideal."""
    name: str
    firmographics: Dict[str, Any]
    technographics: Dict[str, Any]
    financial_indicators: Dict[str, Any]
    personas: List[Dict[str, Any]]

    def __init__(self, name: str, firmographics: Dict[str, Any], technographics: Dict[str, Any], financial_indicators: Dict[str, Any], personas: List[Dict[str, Any]]):
        self.name = name
        self.firmographics = firmographics
        self.technographics = technographics
        self.financial_indicators = financial_indicators
        self.personas = personas

# Definições dos ICPs (baseado no documento "Análise de Lançamento")
ICPS = {
    "Tech-Overwhelmed Growth Company": ICP(
        name="Tech-Overwhelmed Growth Company",
        firmographics={
            "Employee Count": "75-250 FTE",
            "Revenue": "$10M-50M ARR",
            "Industry": ["B2B SaaS", "E-commerce", "Digital Services", "FinTech"],
            "Growth Stage": "Series A/B, profitable scaling, or bootstrapped growth",
            "Geographic": ["North America", "UK", "DACH", "Australia"]
        },
        technographics={
            "SaaS Stack": "6+ marketing/sales tools",
            "Website Tech": "WordPress/Shopify + multiple plugins OR custom React/Next.js",
            "Performance Issues": "Core Web Vitals failing on 40%+ of pages",
            "Integration Complexity": "Multiple disconnected tools, manual data export/import"
        },
        financial_indicators={
            "Marketing Budget": "$15K-50K/month",
            "SaaS Spend": "$3K-8K/month across 8-15 tools",
            "Growth Pressure": "CAC increasing 20-50% YoY, need efficiency gains"
        },
        personas=[
            {
                "name": "Sarah - Marketing Operations Director",
                "title": ["Marketing Ops Director", "Growth Marketing Manager", "VP Marketing"],
                "frustrations": [
                    "I spend 3 hours/week manually pulling data from 8 different tools",
                    "Our website loads slow and I know it's hurting our Google Ads Quality Score",
                    "CEO keeps asking why our CAC went from $180 to $290 this year",
                    "Marketing team complains about Typeform being slow and limited"
                ],
                "success_metrics": {
                    "CAC": "<$200",
                    "Conversion Rate": "3.5%+",
                    "Marketing ROI": "4:1+",
                    "Lead Quality Score": "Increasing"
                },
                "buying_process": {
                    "Budget Authority": "$500-2,500 direct approval, $2,500-10K needs VP/CEO sign-off",
                    "Decision Timeline": "2-4 weeks for operational improvements",
                    "Key Objections": ["Will this integration break something?", "What if we need changes?"]
                }
            },
            {
                "name": "Mike - VP of Growth/Revenue",
                "title": ["VP Growth", "VP Revenue", "Chief Revenue Officer"],
                "strategic_concerns": [
                    "Our tech stack is becoming more expensive but not more effective",
                    "Site performance issues are definitely hurting our SEO rankings",
                    "Need to optimize our growth engine before next funding round",
                    "Board asks why we can't scale efficiently like [competitor]"
                ],
                "success_metrics": {
                    "Revenue Growth": "40-100% YoY targets",
                    "Customer LTV:CAC Ratio": "4:1+",
                    "Operational Efficiency": "Revenue per employee growth",
                    "Market Share": "Competitive positioning + brand metrics"
                },
                "buying_process": {
                    "Budget Authority": "$5K-25K direct approval for growth initiatives",
                    "Decision Timeline": "4-8 weeks, involves CEO for strategic changes",
                    "Key Drivers": ["ROI calculations", "competitive advantage", "team productivity"]
                }
            }
        ]
    )
}

# Lead Scoring Algorithm (baseado no documento "Análise de Lançamento")
def calculate_lead_score(company: CompanyMetrics) -> int:
    score = 0

    # SaaS Complexity (0-30 points)
    if company.saas_tools_count >= 6:
        score += 30
    elif company.saas_tools_count >= 4:
        score += 20
    elif company.saas_tools_count >= 2:
        score += 10

    # Performance Issues (0-25 points)
    # LCP > 4.0s (critical) -> 15 points
    # LCP > 2.5s (needs improvement) -> 10 points
    # INP > 300ms (critical) -> 15 points
    # INP > 200ms (needs improvement) -> 10 points
    if company.lcp > 4.0:
        score += 15
    elif company.lcp > 2.5:
        score += 10
    if company.inp > 300:
        score += 15
    elif company.inp > 200:
        score += 10

    # Ad Spend (0-20 points)
    if company.ad_spend > 15000:
        score += 20
    elif company.ad_spend > 8000:
        score += 15
    elif company.ad_spend > 3000:
        score += 10

    # SaaS Costs (0-15 points)
    if company.estimated_saas_cost > 5000:
        score += 15
    elif company.estimated_saas_cost > 2000:
        score += 10
    elif company.estimated_saas_cost > 1000:
        score += 5

    # Hiring Activity (0-10 points)
    if company.recent_jobs_count >= 3:
        score += 10
    elif company.recent_jobs_count >= 1:
        score += 5

    return min(score, 100)  # Cap at 100

# Helper function to estimate SaaS spend (simplified for now)
def estimate_saas_spend(saas_tools_count: int, employee_count: int) -> float:
    """
    Estimates SaaS spend based on number of tools and employee count.
    This is a simplified model and can be refined.
    """
    base_cost_per_tool = 50 # Average cost per tool per month
    cost_per_employee_factor = 5 # Additional cost per employee for tools

    estimated_cost = (saas_tools_count * base_cost_per_tool) + (employee_count * cost_per_employee_factor)
    return estimated_cost

