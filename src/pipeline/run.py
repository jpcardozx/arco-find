# src/pipeline/run.py

from src.core.arco_engine import ARCOEngine
from src.models.lead import Lead, OptimizationInsight
from src.utils.logger import logger
import json
import os
from datetime import datetime

def run_optimization_pipeline(company_name: str, website_url: str, saas_spend: float, google_ads_customer_id: str = None, google_ads_campaign_id: str = None, meta_ad_account_id: str = None):
    """
    Executa o pipeline de otimização para uma empresa específica.
    """
    logger.info(f"--- Iniciando Pipeline de Otimização para {company_name} ---")

    engine = ARCOEngine()
    
    # 1. Gerar insights de otimização
    raw_insights = engine.generate_optimization_insights(
        company_name, website_url, saas_spend,
        google_ads_customer_id=google_ads_customer_id,
        google_ads_campaign_id=google_ads_campaign_id,
        meta_ad_account_id=meta_ad_account_id
    )

    missed_opportunities = raw_insights.get("missed_opportunities", [])

    # 2. Criar um objeto Lead e popular com insights
    lead_id = f"lead_{datetime.now().strftime("%Y%m%d%H%M%S")}"
    lead = Lead(
        id=lead_id,
        company_name=company_name,
        website=website_url,
        saas_spend=saas_spend,
        employee_count=None, # Placeholder: Será preenchido por módulos de enriquecimento de dados
        revenue_range=None,   # Placeholder: Será preenchido por módulos de enriquecimento de dados
        missed_opportunities=missed_opportunities # Adicionado para oportunidades perdidas
    )

    for insight_data in raw_insights["insights"]:
        insight = OptimizationInsight(
            category=insight_data["category"],
            potential_savings=insight_data.get("potential_savings"),
            performance_score=insight_data.get("performance_score"),
            ad_metrics=insight_data.get("ad_metrics"), # Adicionado para métricas de anúncios
            details=insight_data["details"],
            recommendations=insight_data.get("recommendations", []) # Adicionado para recomendações
        )
        lead.add_insight(insight)
    
    lead.calculate_optimization_score()

    # 3. Salvar os resultados
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"optimization_results_{timestamp}.json"
    file_path = os.path.join(results_dir, file_name)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(lead.__dict__, f, ensure_ascii=False, indent=4, default=str)
        logger.info(f"Resultados salvos em: {file_path}")
    except IOError as e:
        logger.error(f"Erro ao salvar resultados em {file_path}: {e}")

    logger.info(f"--- Pipeline Concluído ---")
    logger.info(f"Score de Otimização para {company_name}: {lead.optimization_potential_score}")
    return lead

if __name__ == "__main__":
    # Exemplo de uso do pipeline
    logger.info("Executando exemplos de pipeline...")
    run_optimization_pipeline(
        company_name="Empresa Exemplo",
        website_url="https://empresaexemplo.com",
        saas_spend=7500.0,
        google_ads_customer_id="123-456-7890" # Exemplo de ID de cliente para análise de ads
    )

    run_optimization_pipeline(
        company_name="Startup Inovadora",
        website_url="https://startupinovadora.io",
        saas_spend=3000.0,
        google_ads_customer_id="987-654-3210", # Outro exemplo de ID de cliente
        google_ads_campaign_id="campaign_abc", # Exemplo de ID de campanha
        meta_ad_account_id="act_123456789" # Exemplo de ID de conta de anúncios Meta
    )
    logger.info("Exemplos de pipeline concluídos.")