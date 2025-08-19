"""
ARCO Complete Real Pipeline - 3 Layers Integrated
===============================================

Pipeline completo real sem simulações:
- Layer 1: Seed generation (discovery + aggregation)
- Layer 2: Advertiser consolidation (domain-based)
- Layer 3: Ad details analysis (creative scoring)

S-tier async implementation com resultados reais
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

# Import all layers
from src.engines.searchapi_layer1_seed_generation import SearchAPILayer1SeedGeneration
from src.engines.searchapi_layer2_advertiser_consolidation import SearchAPILayer2AdvertiserConsolidation
from src.engines.searchapi_layer3_ad_details_analysis import SearchAPILayer3AdDetailsAnalysis


async def execute_complete_pipeline():
    """
    Executa o pipeline completo das 3 layers com dados reais
    """
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y%m%d_%H%M%S")
    
    logger.info("=" * 60)
    logger.info("ARCO COMPLETE REAL PIPELINE - 3 LAYERS")
    logger.info("=" * 60)
    
    # Criar diretório principal de resultados
    output_dir = Path(f"data/exports/pipeline_complete_real_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    pipeline_results = {
        "pipeline_start": start_time.isoformat(),
        "layer1_results": None,
        "layer2_results": None,
        "layer3_results": None,
        "final_summary": {}
    }
    
    try:
        # LAYER 1: Seed Generation
        logger.info("\\n🔍 EXECUTING LAYER 1: Seed Generation")
        logger.info("-" * 40)
        
        layer1_engine = SearchAPILayer1SeedGeneration()
        layer1_results = await layer1_engine.generate_seeds(
            target_markets=["UK", "US"],
            seed_keywords=[
                "estate agents", "property management", "real estate",
                "property services", "lettings agents", "property rental"
            ],
            max_seeds_per_keyword=20
        )
        
        pipeline_results["layer1_results"] = layer1_results
        
        # Salvar resultados Layer 1
        layer1_file = output_dir / "layer1_seeds.json"
        with open(layer1_file, 'w', encoding='utf-8') as f:
            json.dump(layer1_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Layer 1 completed: {len(layer1_results.get('aggregated_domains', []))} domains discovered")
        
        # LAYER 2: Advertiser Consolidation
        logger.info("\\n📊 EXECUTING LAYER 2: Advertiser Consolidation")
        logger.info("-" * 40)
        
        # Usar domains do Layer 1
        domains_for_layer2 = layer1_results.get("aggregated_domains", [])[:15]  # Limitar para teste
        
        if not domains_for_layer2:
            logger.error("No domains from Layer 1 to process in Layer 2")
            return
        
        layer2_engine = SearchAPILayer2AdvertiserConsolidation()
        layer2_results = await layer2_engine.consolidate_advertiser_info(domains_for_layer2)
        
        pipeline_results["layer2_results"] = layer2_results
        
        # Salvar resultados Layer 2
        layer2_file = output_dir / "layer2_consolidation.json"
        with open(layer2_file, 'w', encoding='utf-8') as f:
            json.dump(layer2_results, f, indent=2, ensure_ascii=False)
        
        qualified_advertisers = layer2_results.get("qualified_advertisers", [])
        logger.info(f"✅ Layer 2 completed: {len(qualified_advertisers)} qualified advertisers")
        
        # LAYER 3: Ad Details Analysis
        logger.info("\\n🎯 EXECUTING LAYER 3: Ad Details Analysis")
        logger.info("-" * 40)
        
        if not qualified_advertisers:
            logger.error("No qualified advertisers from Layer 2 to process in Layer 3")
            return
        
        # Converter para formato Layer 3
        layer3_input = []
        for advertiser in qualified_advertisers:
            if advertiser.get("is_qualified", False) and advertiser.get("creative_ids"):
                layer3_input.append({
                    "domain": advertiser.get("domain_searched", "unknown"),
                    "score": advertiser.get("quality_score", 0),
                    "creative_ids": advertiser.get("creative_ids", []),
                    "total_campaigns": advertiser.get("total_campaigns", 0),
                    "advertiser_name": advertiser.get("advertiser_name", ""),
                    "region": advertiser.get("region", "")
                })
        
        layer3_engine = SearchAPILayer3AdDetailsAnalysis()
        layer3_results = await layer3_engine.analyze_ad_details(layer3_input)
        
        pipeline_results["layer3_results"] = layer3_results
        
        # Salvar resultados Layer 3
        layer3_file = output_dir / "layer3_analysis.json"
        with open(layer3_file, 'w', encoding='utf-8') as f:
            json.dump(layer3_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Layer 3 completed: {len(layer3_results['layer3_analysis'])} creatives analyzed")
        
        # FINAL SUMMARY
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        pipeline_results["pipeline_end"] = end_time.isoformat()
        pipeline_results["total_duration"] = total_duration
        
        # Compilar summary final
        final_summary = {
            "execution_time": f"{total_duration:.2f}s",
            "layer1": {
                "domains_discovered": len(layer1_results.get('aggregated_domains', [])),
                "execution_time": layer1_results.get('execution_time', 0)
            },
            "layer2": {
                "domains_processed": layer2_results.get('processed_domains', 0),
                "qualified_advertisers": len(qualified_advertisers),
                "success_rate": f"{layer2_results.get('successful_consolidations', 0) / layer2_results.get('processed_domains', 1) * 100:.1f}%"
            },
            "layer3": {
                "creatives_analyzed": len(layer3_results['layer3_analysis']),
                "top_performers": len(layer3_results['summary']['top_performers']),
                "execution_time": layer3_results['summary']['execution_time']
            },
            "outreach_ready": len([p for p in layer3_results['summary']['top_performers'] if p.get('total_score', 0) >= 50])
        }
        
        pipeline_results["final_summary"] = final_summary
        
        # Salvar pipeline completo
        pipeline_file = output_dir / "complete_pipeline_results.json"
        with open(pipeline_file, 'w', encoding='utf-8') as f:
            json.dump(pipeline_results, f, indent=2, ensure_ascii=False)
        
        # Gerar relatório final
        report_file = output_dir / "pipeline_final_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("ARCO COMPLETE REAL PIPELINE REPORT\\n")
            f.write("=" * 50 + "\\n\\n")
            f.write(f"Total Execution Time: {total_duration:.2f}s\\n")
            f.write(f"Pipeline Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\\n")
            f.write(f"Pipeline End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\\n\\n")
            
            f.write("LAYER RESULTS:\\n")
            f.write("-" * 20 + "\\n")
            f.write(f"Layer 1 - Domains Discovered: {final_summary['layer1']['domains_discovered']}\\n")
            f.write(f"Layer 2 - Qualified Advertisers: {final_summary['layer2']['qualified_advertisers']}\\n")
            f.write(f"Layer 3 - Creatives Analyzed: {final_summary['layer3']['creatives_analyzed']}\\n")
            f.write(f"Final - Outreach Ready: {final_summary['outreach_ready']}\\n\\n")
            
            f.write("TOP PERFORMERS (Layer 3):\\n")
            f.write("-" * 30 + "\\n")
            for i, performer in enumerate(layer3_results['summary']['top_performers'], 1):
                f.write(f"{i}. {performer['domain']} - Score: {performer['total_score']} ({performer['grade']})\\n")
                f.write(f"   Advertiser: {performer.get('advertiser', 'N/A')}\\n")
                f.write(f"   Format: {performer.get('format', 'N/A')} | Days Active: {performer.get('days_shown', 0)}\\n\\n")
        
        # Log final results
        logger.info("\\n" + "=" * 60)
        logger.info("ARCO PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)
        logger.info(f"📁 Results saved to: {output_dir}")
        logger.info(f"⏱️  Total execution time: {total_duration:.2f}s")
        logger.info(f"🎯 Outreach ready leads: {final_summary['outreach_ready']}")
        logger.info(f"📊 Complete funnel: {final_summary['layer1']['domains_discovered']} → {final_summary['layer2']['qualified_advertisers']} → {final_summary['outreach_ready']}")
        
        if layer3_results['summary']['top_performers']:
            logger.info("\\n🏆 TOP 3 FINAL PERFORMERS:")
            for i, performer in enumerate(layer3_results['summary']['top_performers'][:3], 1):
                logger.info(f"{i}. {performer['domain']} - Score: {performer['total_score']} ({performer['grade']})")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(execute_complete_pipeline())
