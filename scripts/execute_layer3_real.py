"""
ARCO Layer 3 Execution - Real SearchAPI Ad Details Analysis
==========================================================

Executa Layer 3 com dados reais do Layer 2:
- Carrega resultados qualificados do Layer 2
- Analisa creative_ids com SearchAPI real calls
- Calcula scores ARCO finais
- Identifica top performers para outreach

S-tier async implementation integrado com Layer 2 results
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the S-tier Layer 3 engine
from src.engines.searchapi_layer3_ad_details_analysis import SearchAPILayer3AdDetailsAnalysis


async def load_layer2_results():
    """
    Carrega os resultados mais recentes do Layer 2
    """
    exports_dir = Path("data/exports")
    
    # Encontrar a pasta mais recente do Layer 2
    layer2_dirs = [d for d in exports_dir.glob("layer2_real_*") if d.is_dir()]
    
    if not layer2_dirs:
        logger.error("No Layer 2 results found in data/exports/")
        return None
    
    # Pegar a mais recente
    latest_dir = sorted(layer2_dirs, key=lambda x: x.name)[-1]
    
    # Procurar pelo arquivo de consolidação
    consolidation_files = list(latest_dir.glob("layer2_consolidation_*.json"))
    
    if not consolidation_files:
        logger.error(f"No consolidation file found in {latest_dir}")
        return None
    
    results_file = consolidation_files[0]
    logger.info(f"Loading Layer 2 results from: {results_file}")
    
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extrair apenas os anunciantes qualificados
    qualified_advertisers = data.get("qualified_advertisers", [])
    
    # Converter para o formato esperado pelo Layer 3
    qualified_leads = []
    for advertiser in qualified_advertisers:
        if advertiser.get("is_qualified", False) and advertiser.get("creative_ids"):
            qualified_leads.append({
                "domain": advertiser.get("domain_searched", "unknown"),
                "score": advertiser.get("quality_score", 0),
                "creative_ids": advertiser.get("creative_ids", []),
                "total_campaigns": advertiser.get("total_campaigns", 0),
                "advertiser_name": advertiser.get("advertiser_name", ""),
                "region": advertiser.get("region", "")
            })
    
    logger.info(f"Found {len(qualified_leads)} qualified leads from Layer 2")
    
    return qualified_leads


async def execute_layer3_analysis():
    """
    Executa análise Layer 3 com dados reais do Layer 2
    """
    logger.info("Starting Layer 3 Real Execution with Layer 2 Integration")
    
    # Carregar resultados do Layer 2
    layer2_leads = await load_layer2_results()
    
    if not layer2_leads:
        logger.error("Cannot proceed without Layer 2 results")
        return
    
    # Inicializar Layer 3 engine
    layer3_engine = SearchAPILayer3AdDetailsAnalysis()
    
    # Executar análise Layer 3
    logger.info("Executing S-tier async Layer 3 analysis...")
    layer3_results = await layer3_engine.analyze_ad_details(layer2_leads)
    
    # Criar diretório de output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"data/exports/layer3_real_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Salvar resultados detalhados
    results_file = output_dir / "layer3_ad_analysis.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(layer3_results, f, indent=2, ensure_ascii=False)
    
    # Salvar top performers para outreach
    top_performers = layer3_results["summary"]["top_performers"]
    outreach_file = output_dir / "outreach_ready_leads.json"
    
    outreach_data = {
        "timestamp": datetime.now().isoformat(),
        "total_top_performers": len(top_performers),
        "outreach_ready": [
            lead for lead in top_performers 
            if lead["total_score"] >= 50  # Score mínimo para outreach
        ],
        "analysis_summary": layer3_results["summary"]
    }
    
    with open(outreach_file, 'w', encoding='utf-8') as f:
        json.dump(outreach_data, f, indent=2, ensure_ascii=False)
    
    # Summary report
    summary_file = output_dir / "layer3_summary_report.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("ARCO Layer 3 - Real Ad Details Analysis Report\\n")
        f.write("=" * 50 + "\\n\\n")
        f.write(f"Execution Time: {layer3_results['summary']['execution_time']}s\\n")
        f.write(f"Leads Analyzed: {layer3_results['summary']['total_leads_analyzed']}\\n")
        f.write(f"Successful Analyses: {layer3_results['summary']['successful_analyses']}\\n")
        f.write(f"Failed Analyses: {layer3_results['summary']['failed_analyses']}\\n")
        f.write(f"Outreach Ready: {len(outreach_data['outreach_ready'])}\\n\\n")
        
        f.write("TOP PERFORMERS:\\n")
        f.write("-" * 30 + "\\n")
        for i, performer in enumerate(top_performers, 1):
            f.write(f"{i}. {performer['domain']} (Score: {performer['total_score']}, Grade: {performer['grade']})\\n")
            f.write(f"   Creative ID: {performer['creative_id']}\\n")
            f.write(f"   Landing Page: {performer.get('primary_landing_page', 'N/A')}\\n\\n")
    
    # Log final results
    logger.info("Layer 3 Analysis Completed!")
    logger.info(f"Results saved to: {output_dir}")
    logger.info(f"Total creatives analyzed: {layer3_results['summary']['successful_analyses']}")
    logger.info(f"Top performers identified: {len(top_performers)}")
    logger.info(f"Outreach ready leads: {len(outreach_data['outreach_ready'])}")
    
    # Mostrar top 3 performers
    if top_performers:
        logger.info("\\nTOP 3 PERFORMERS:")
        for i, performer in enumerate(top_performers[:3], 1):
            logger.info(f"{i}. {performer['domain']} - Score: {performer['total_score']} ({performer['grade']})")


if __name__ == "__main__":
    asyncio.run(execute_layer3_analysis())
