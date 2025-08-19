"""
ARCO SearchAPI - Master Orchestrator Engine
==========================================

Orquestra as 3 camadas do SearchAPI para pipeline completo:
Layer 1: Seed Generation (advertiser search)
Layer 2: Advertiser Consolidation (transparency center)
Layer 3: Ad Details Analysis (ad details)

Pipeline completo: Keyword → Seeds → Qualification → Final Analysis → Outreach
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import logging
from pathlib import Path

# Importar as 3 camadas
from .searchapi_layer1_seed_generation import SearchAPILayer1SeedGeneration
from .searchapi_layer2_advertiser_consolidation import SearchAPILayer2AdvertiserConsolidation  
from .searchapi_layer3_ad_details_analysis import SearchAPILayer3AdDetailsAnalysis
from ..config.arco_config_simple import get_config, get_api_key

class ARCOSearchAPIMasterOrchestrator:
    def __init__(self, api_key: Optional[str] = None, output_dir: str = "data/searchapi_results"):
        self.config = get_config()
        self.api_key = api_key or get_api_key()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar as 3 camadas
        self.layer1 = SearchAPILayer1SeedGeneration(api_key)
        self.layer2 = SearchAPILayer2AdvertiserConsolidation(api_key)
        self.layer3 = SearchAPILayer3AdDetailsAnalysis(api_key)
        
        # Configurações do pipeline
        self.pipeline_config = {
            "verticals": ["dental_ortho", "estética_medspa", "real_estate_eu"],
            "regions": ["IE", "GB", "MT"],  # Europa anglófona prioritária
            "regions_backup": ["AU", "NZ"],  # Backup caso Europa não funcione
            "max_keywords_per_vertical": 4,
            "max_advertisers_per_batch": 30,
            "max_creatives_per_advertiser": 2,
            "save_intermediate_results": True,
            "rate_limit_delay": 1.0,
            "focus_strategy": "europa_anglofona"  # Estratégia atual
        }
        
        self.logger = logging.getLogger(__name__)
        
        # Tracking de uso da API
        self.api_usage = {
            "layer1_calls": 0,
            "layer2_calls": 0,
            "layer3_calls": 0,
            "total_calls": 0,
            "start_time": None,
            "end_time": None
        }
    
    def run_complete_pipeline(self, 
                            verticals: List[str] = None,
                            regions: List[str] = None,
                            save_results: bool = True) -> Dict:
        """
        Executa pipeline completo das 3 camadas
        
        Args:
            verticals: Lista de verticais para processar
            regions: Lista de regiões para processar
            save_results: Se deve salvar resultados intermediários
        
        Returns:
            Dict com resultados completos do pipeline
        """
        
        self.api_usage["start_time"] = datetime.now()
        
        if verticals is None:
            verticals = self.pipeline_config["verticals"]
        
        if regions is None:
            regions = self.pipeline_config["regions"]
        
        pipeline_results = {
            "pipeline_id": f"arco_searchapi_{int(time.time())}",
            "start_timestamp": self.api_usage["start_time"].isoformat(),
            "config": {
                "verticals": verticals,
                "regions": regions,
                **self.pipeline_config
            },
            "layer1_results": {},
            "layer2_results": {},
            "layer3_results": {},
            "final_outreach_data": [],
            "pipeline_summary": {},
            "api_usage": {}
        }
        
        try:
            # === LAYER 1: SEED GENERATION ===
            self.logger.info("🌱 Starting Layer 1: Seed Generation")
            
            layer1_results = self.layer1.generate_comprehensive_seeds(
                verticals=verticals,
                regions=regions
            )
            
            pipeline_results["layer1_results"] = layer1_results
            self.api_usage["layer1_calls"] = layer1_results["global_aggregation"]["total_api_calls"]
            
            if save_results:
                self._save_intermediate_results("layer1", layer1_results, pipeline_results["pipeline_id"])
            
            self.logger.info(f"Layer 1 complete: {layer1_results['global_aggregation']['total_unique_advertisers']} advertisers found")
            
            # === LAYER 2: ADVERTISER CONSOLIDATION ===
            self.logger.info("🔍 Starting Layer 2: Advertiser Consolidation")
            
            # Preparar lista de anunciantes para Layer 2
            advertisers_for_layer2 = []
            
            for vertical, data in layer1_results["results_by_vertical"].items():
                for advertiser_id, advertiser_data in data["aggregated_advertisers"].items():
                    advertisers_for_layer2.append({
                        "advertiser_id": advertiser_id,
                        "domain": advertiser_data.get("verified_domain"),
                        "vertical": vertical,
                        "first_seen_keyword": advertiser_data.get("first_seen_keyword"),
                        "first_seen_region": advertiser_data.get("first_seen_region")
                    })
            
            # Processar em batches
            all_layer2_results = {}
            batch_size = self.pipeline_config["max_advertisers_per_batch"]
            
            for i in range(0, len(advertisers_for_layer2), batch_size):
                batch = advertisers_for_layer2[i:i + batch_size]
                batch_id = f"batch_{i//batch_size + 1}"
                
                self.logger.info(f"Processing Layer 2 {batch_id}: {len(batch)} advertisers")
                
                # Rate limiting entre batches
                if i > 0:
                    time.sleep(2.0)
                
                batch_results = self.layer2.consolidate_advertisers_batch(
                    advertiser_list=batch,
                    region=regions[0],  # Usar primeira região como default
                    max_batch_size=batch_size
                )
                
                all_layer2_results[batch_id] = batch_results
                self.api_usage["layer2_calls"] += batch_results["summary"]["api_calls_used"]
            
            # Consolidar resultados do Layer 2
            pipeline_results["layer2_results"] = self._consolidate_layer2_batches(all_layer2_results)
            
            if save_results:
                self._save_intermediate_results("layer2", pipeline_results["layer2_results"], pipeline_results["pipeline_id"])
            
            qualified_count = pipeline_results["layer2_results"]["aggregated_summary"]["qualified_count"]
            self.logger.info(f"Layer 2 complete: {qualified_count} qualified advertisers")
            
            # === LAYER 3: AD DETAILS ANALYSIS ===
            self.logger.info("🎯 Starting Layer 3: Ad Details Analysis")
            
            # Preparar lista qualificada para Layer 3
            qualified_for_layer3 = self.layer2.get_qualified_advertisers_for_layer3(
                pipeline_results["layer2_results"]
            )
            
            # Limitar quantidade para controlar custos
            max_for_layer3 = min(20, len(qualified_for_layer3))
            qualified_for_layer3 = qualified_for_layer3[:max_for_layer3]
            
            layer3_results = self.layer3.process_qualified_advertisers(
                qualified_list=qualified_for_layer3,
                max_creatives_per_advertiser=self.pipeline_config["max_creatives_per_advertiser"]
            )
            
            pipeline_results["layer3_results"] = layer3_results
            self.api_usage["layer3_calls"] = layer3_results["summary"]["api_calls_used"]
            
            if save_results:
                self._save_intermediate_results("layer3", layer3_results, pipeline_results["pipeline_id"])
            
            # Gerar dados de outreach
            outreach_data = self.layer3.generate_outreach_data(layer3_results["outreach_ready"])
            pipeline_results["final_outreach_data"] = outreach_data
            
            self.logger.info(f"Layer 3 complete: {len(outreach_data)} ready for outreach")
            
            # === FINALIZAÇÃO ===
            self.api_usage["end_time"] = datetime.now()
            self.api_usage["total_calls"] = (
                self.api_usage["layer1_calls"] + 
                self.api_usage["layer2_calls"] + 
                self.api_usage["layer3_calls"]
            )
            
            pipeline_results["api_usage"] = self.api_usage.copy()
            pipeline_results["pipeline_summary"] = self._generate_pipeline_summary(pipeline_results)
            pipeline_results["end_timestamp"] = self.api_usage["end_time"].isoformat()
            
            if save_results:
                self._save_final_results(pipeline_results)
            
            self.logger.info(f"🎉 Pipeline complete! {len(outreach_data)} prospects ready, {self.api_usage['total_calls']} API calls used")
            
            return pipeline_results
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            pipeline_results["error"] = str(e)
            pipeline_results["status"] = "failed"
            return pipeline_results
    
    def _consolidate_layer2_batches(self, batch_results: Dict) -> Dict:
        """
        Consolida resultados de múltiplos batches do Layer 2
        """
        
        consolidated = {
            "consolidation_timestamp": datetime.now().isoformat(),
            "total_batches": len(batch_results),
            "qualified_advertisers": {},
            "potential_advertisers": {},
            "rejected_advertisers": {},
            "aggregated_summary": {
                "total_processed": 0,
                "qualified_count": 0,
                "potential_count": 0,
                "rejected_count": 0,
                "total_api_calls": 0
            }
        }
        
        for batch_id, batch_data in batch_results.items():
            # Merge qualified
            consolidated["qualified_advertisers"].update(batch_data.get("qualified_advertisers", {}))
            consolidated["potential_advertisers"].update(batch_data.get("potential_advertisers", {}))
            consolidated["rejected_advertisers"].update(batch_data.get("rejected_advertisers", {}))
            
            # Aggregate summary
            summary = batch_data.get("summary", {})
            consolidated["aggregated_summary"]["total_processed"] += summary.get("total_processed", 0)
            consolidated["aggregated_summary"]["qualified_count"] += summary.get("qualified_count", 0)
            consolidated["aggregated_summary"]["potential_count"] += summary.get("potential_count", 0)
            consolidated["aggregated_summary"]["rejected_count"] += summary.get("rejected_count", 0)
            consolidated["aggregated_summary"]["total_api_calls"] += summary.get("api_calls_used", 0)
        
        return consolidated
    
    def _generate_pipeline_summary(self, pipeline_results: Dict) -> Dict:
        """
        Gera sumário executivo do pipeline
        """
        
        layer1_data = pipeline_results["layer1_results"]
        layer2_data = pipeline_results["layer2_results"]
        layer3_data = pipeline_results["layer3_results"]
        
        summary = {
            "execution_time_minutes": self._calculate_execution_time(),
            "api_efficiency": {
                "total_calls": self.api_usage["total_calls"],
                "calls_per_final_prospect": 0,
                "cost_estimate_usd": self.api_usage["total_calls"] * 0.05  # Estimativa
            },
            "funnel_metrics": {
                "initial_advertisers": layer1_data["global_aggregation"]["total_unique_advertisers"],
                "qualified_after_layer2": layer2_data["aggregated_summary"]["qualified_count"],
                "outreach_ready": len(pipeline_results["final_outreach_data"]),
                "conversion_rate": 0
            },
            "vertical_breakdown": {},
            "top_prospects": []
        }
        
        # Calcular conversion rate
        if summary["funnel_metrics"]["initial_advertisers"] > 0:
            summary["funnel_metrics"]["conversion_rate"] = (
                summary["funnel_metrics"]["outreach_ready"] / 
                summary["funnel_metrics"]["initial_advertisers"] * 100
            )
        
        # Calcular calls per prospect
        if summary["funnel_metrics"]["outreach_ready"] > 0:
            summary["api_efficiency"]["calls_per_final_prospect"] = (
                self.api_usage["total_calls"] / 
                summary["funnel_metrics"]["outreach_ready"]
            )
        
        # Breakdown por vertical
        for vertical, data in layer1_data["results_by_vertical"].items():
            summary["vertical_breakdown"][vertical] = {
                "initial_advertisers": data["total_unique_advertisers"],
                "domains": data["total_unique_domains"]
            }
        
        # Top prospects
        summary["top_prospects"] = [
            {
                "domain": prospect.get("domain"),
                "arco_score": prospect.get("arco_score"),
                "priority": prospect.get("priority_level"),
                "outreach_angle": prospect.get("outreach_angle")
            }
            for prospect in pipeline_results["final_outreach_data"][:5]
        ]
        
        return summary
    
    def _calculate_execution_time(self) -> float:
        """
        Calcula tempo de execução em minutos
        """
        
        if self.api_usage["start_time"] and self.api_usage["end_time"]:
            delta = self.api_usage["end_time"] - self.api_usage["start_time"]
            return round(delta.total_seconds() / 60, 2)
        
        return 0
    
    def _save_intermediate_results(self, layer: str, data: Dict, pipeline_id: str):
        """
        Salva resultados intermediários
        """
        
        filename = f"{pipeline_id}_{layer}_results.json"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {layer} results to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to save {layer} results: {str(e)}")
    
    def _save_final_results(self, pipeline_results: Dict):
        """
        Salva resultados finais completos
        """
        
        pipeline_id = pipeline_results["pipeline_id"]
        
        # Resultados completos
        complete_filename = f"{pipeline_id}_complete_results.json"
        complete_filepath = self.output_dir / complete_filename
        
        # Sumário executivo
        summary_filename = f"{pipeline_id}_executive_summary.json"
        summary_filepath = self.output_dir / summary_filename
        
        # Dados de outreach (CSV-ready)
        outreach_filename = f"{pipeline_id}_outreach_data.json"
        outreach_filepath = self.output_dir / outreach_filename
        
        try:
            # Salvar completo
            with open(complete_filepath, 'w', encoding='utf-8') as f:
                json.dump(pipeline_results, f, indent=2, ensure_ascii=False)
            
            # Salvar sumário
            with open(summary_filepath, 'w', encoding='utf-8') as f:
                json.dump(pipeline_results["pipeline_summary"], f, indent=2, ensure_ascii=False)
            
            # Salvar outreach data
            with open(outreach_filepath, 'w', encoding='utf-8') as f:
                json.dump(pipeline_results["final_outreach_data"], f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved final results to {self.output_dir}")
            
        except Exception as e:
            self.logger.error(f"Failed to save final results: {str(e)}")
    
    def run_europa_real_estate_focus(self, save_results: bool = True) -> Dict:
        """
        Executa pipeline focado especificamente em Real Estate Europa
        
        Estratégia: Mercados anglófonos menos saturados com pain signals específicos
        Timing: Favorável (trabalham segundas, fuso europeu)
        """
        
        self.logger.info("🇪🇺 Iniciando pipeline Europa Real Estate Focus")
        
        europa_config = {
            "verticals": ["real_estate_eu"],
            "regions": ["IE", "GB", "MT"],  # Irlanda, Reino Unido, Malta
            "max_keywords_per_vertical": 3,  # Controlar custos
            "max_advertisers_per_batch": 20,  # Limite conservador
            "strategy_rationale": {
                "timing": "Trabalham segundas (fuso europeu)",
                "saturation": "Menos saturado que AU/NZ",
                "ticket_size": "€5-15k vs $3-8k",
                "pain_signals": "Brexit compliance, EU regulations"
            }
        }
        
        # Usar config Europa temporariamente
        original_config = self.pipeline_config.copy()
        self.pipeline_config.update(europa_config)
        
        try:
            results = self.run_complete_pipeline(
                verticals=europa_config["verticals"],
                regions=europa_config["regions"],
                save_results=save_results
            )
            
            # Adicionar contexto estratégico aos resultados
            results["strategy_context"] = europa_config["strategy_rationale"]
            results["market_analysis"] = {
                "focus": "Europa Anglófona Real Estate",
                "competitive_advantage": "Mercados menos saturados, tickets maiores",
                "timing_advantage": "Fuso europeu, trabalham segundas",
                "cost_efficiency": f"${results.get('api_usage', {}).get('total_calls', 0) * 0.05:.2f}"
            }
            
            self.logger.info(f"🎯 Europa focus complete: {len(results.get('final_outreach_data', []))} prospects")
            
            # Restaurar config original
            self.pipeline_config = original_config
            
            return results
            
        except Exception as e:
            self.pipeline_config = original_config
            self.logger.error(f"Europa pipeline failed: {str(e)}")
            raise e
    
    def run_quick_test(self, vertical: str = "real_estate_eu", region: str = "IE") -> Dict:
        """
        Executa teste rápido com parâmetros limitados
        """
        
        self.logger.info(f"🧪 Running quick test: {vertical} in {region}")
        
        # Configuração reduzida para teste
        test_config = {
            "verticals": [vertical],
            "regions": [region],
            "max_keywords_per_vertical": 2,
            "max_advertisers_per_batch": 10,
            "max_creatives_per_advertiser": 1
        }
        
        # Atualizar config temporariamente
        original_config = self.pipeline_config.copy()
        self.pipeline_config.update(test_config)
        
        try:
            results = self.run_complete_pipeline(
                verticals=[vertical],
                regions=[region],
                save_results=False
            )
            
            # Restaurar config original
            self.pipeline_config = original_config
            
            return results
            
        except Exception as e:
            self.pipeline_config = original_config
            raise e

# Exemplo de uso
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configuração
    API_KEY = "your_searchapi_key_here"
    
    # Inicializar orchestrator
    orchestrator = ARCOSearchAPIMasterOrchestrator(
        api_key=API_KEY,
        output_dir="data/searchapi_results"
    )
    
    # Teste Europa Real Estate
    test_results = orchestrator.run_quick_test(
        vertical="real_estate_eu",
        region="IE"  # Irlanda como teste
    )
    
    print(f"Europa test complete: {len(test_results['final_outreach_data'])} prospects found")
    
    # Pipeline Europa completo (descomente para execução real)
    # europa_results = orchestrator.run_europa_real_estate_focus()
    # print(f"Europa pipeline: {len(europa_results['final_outreach_data'])} prospects ready")
