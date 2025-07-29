"""
ARCO Pipeline Enhanced com BigQuery Integration
Pipeline principal atualizado para incluir integração automática com BigQuery
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Importar componentes core
from search_intelligence import SearchIntelligenceEngine
from lead_qualification import QualificationEngine
from competitive_analysis import CompetitiveAnalysisEngine
from bigquery_integration import ARCOBigQueryIntegration

class ARCOPipelineEnhanced:
    def __init__(self):
        """
        Inicializa pipeline ARCO com integração BigQuery
        """
        self.setup_logging()
        
        # Inicializar engines
        self.search_engine = SearchIntelligenceEngine()
        self.qualification_engine = QualificationEngine()
        self.competitive_engine = CompetitiveAnalysisEngine()
        
        # Inicializar BigQuery Integration
        try:
            self.bigquery_integration = ARCOBigQueryIntegration()
            self.bigquery_enabled = True
            logging.info("✅ BigQuery Integration habilitada")
        except Exception as e:
            logging.warning(f"⚠️ BigQuery Integration desabilitada: {e}")
            self.bigquery_integration = None
            self.bigquery_enabled = False
        
        # Métricas de execução
        self.execution_metrics = {
            "start_time": None,
            "end_time": None,
            "duration_seconds": 0,
            "leads_discovered": 0,
            "leads_qualified": 0,
            "api_calls_made": 0,
            "success_rate": 0.0,
            "total_opportunity_value": 0.0,
            "average_qualification_score": 0.0,
        }
        
        # ID único da execução
        self.execution_id = f"arco_exec_{int(datetime.utcnow().timestamp())}"
        
    def setup_logging(self):
        """Configurar logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('arco_pipeline_enhanced.log'),
                logging.StreamHandler()
            ]
        )

    def discover_prospects(self, search_queries: List[str], max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Descobrir prospects usando SearchAPI
        
        Args:
            search_queries: Lista de queries de busca
            max_results: Máximo de resultados por query
            
        Returns:
            Lista de prospects descobertos
        """
        logging.info(f"🔍 Iniciando descoberta de prospects - {len(search_queries)} queries")
        
        all_prospects = []
        
        for query in search_queries:
            try:
                prospects = self.search_engine.discover_prospects(query, max_results)
                all_prospects.extend(prospects)
                self.execution_metrics["api_calls_made"] += 1
                
                logging.info(f"✅ Query '{query}': {len(prospects)} prospects encontrados")
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"❌ Erro na query '{query}': {e}")
                continue
        
        # Remover duplicatas por domínio
        unique_prospects = {}
        for prospect in all_prospects:
            domain = prospect.get('domain')
            if domain and domain not in unique_prospects:
                unique_prospects[domain] = prospect
        
        prospects_list = list(unique_prospects.values())
        self.execution_metrics["leads_discovered"] = len(prospects_list)
        
        logging.info(f"🎯 Descoberta concluída: {len(prospects_list)} prospects únicos")
        return prospects_list

    def qualify_leads(self, prospects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Qualificar leads usando engine de qualificação
        
        Args:
            prospects: Lista de prospects para qualificação
            
        Returns:
            Lista de leads qualificados
        """
        logging.info(f"⚖️ Iniciando qualificação de {len(prospects)} prospects")
        
        qualified_leads = []
        
        for i, prospect in enumerate(prospects, 1):
            try:
                logging.info(f"Qualificando prospect {i}/{len(prospects)}: {prospect.get('domain', 'N/A')}")
                
                # Qualificar prospect
                qualification_result = self.qualification_engine.qualify_prospect(prospect)
                
                if qualification_result and qualification_result.get('is_qualified', False):
                    # Enriquecer com análise competitiva
                    competitive_analysis = self.competitive_engine.analyze_competitor(
                        prospect.get('domain', ''),
                        prospect.get('industry', 'legal')
                    )
                    
                    # Combinar dados
                    qualified_lead = {
                        **prospect,
                        **qualification_result,
                        'competitive_analysis': competitive_analysis,
                        'discovery_timestamp': datetime.utcnow().isoformat(),
                    }
                    
                    qualified_leads.append(qualified_lead)
                    
                    logging.info(f"✅ Lead qualificado: {prospect.get('domain')} (Score: {qualification_result.get('qualification_score', 0)})")
                
                self.execution_metrics["api_calls_made"] += 2  # Qualificação + Análise Competitiva
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                logging.error(f"❌ Erro ao qualificar {prospect.get('domain', 'N/A')}: {e}")
                continue
        
        self.execution_metrics["leads_qualified"] = len(qualified_leads)
        
        # Calcular métricas
        if qualified_leads:
            total_opportunity = sum(lead.get('opportunity_value', 0) for lead in qualified_leads)
            avg_score = sum(lead.get('qualification_score', 0) for lead in qualified_leads) / len(qualified_leads)
            
            self.execution_metrics["total_opportunity_value"] = total_opportunity
            self.execution_metrics["average_qualification_score"] = avg_score
        
        logging.info(f"🎯 Qualificação concluída: {len(qualified_leads)} leads qualificados")
        return qualified_leads

    def save_results(self, qualified_leads: List[Dict[str, Any]]) -> str:
        """
        Salvar resultados localmente e no BigQuery
        
        Args:
            qualified_leads: Lista de leads qualificados
            
        Returns:
            Caminho do arquivo salvo
        """
        # Salvar localmente
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"arco_enhanced_leads_{timestamp}.json"
        filepath = Path("exports") / filename
        
        # Criar diretório se não existir
        filepath.parent.mkdir(exist_ok=True)
        
        # Preparar dados para salvamento
        export_data = {
            "execution_id": self.execution_id,
            "generated_at": datetime.utcnow().isoformat(),
            "pipeline_version": "v1.1_enhanced",
            "execution_metrics": self.execution_metrics,
            "qualified_leads_count": len(qualified_leads),
            "qualified_leads": qualified_leads,
        }
        
        # Salvar arquivo JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logging.info(f"💾 Resultados salvos em: {filepath}")
        
        # Upload para BigQuery se habilitado
        if self.bigquery_enabled and self.bigquery_integration:
            try:
                # Configurar tabelas
                self.bigquery_integration.create_tables_if_not_exist()
                
                # Upload leads
                self.bigquery_integration.upload_qualified_leads(qualified_leads, self.execution_id)
                
                # Upload métricas
                self.bigquery_integration.upload_pipeline_metrics(self.execution_metrics, self.execution_id)
                
                logging.info("☁️ Dados carregados no BigQuery com sucesso!")
                
            except Exception as e:
                logging.error(f"❌ Erro ao carregar dados no BigQuery: {e}")
        
        return str(filepath)

    def generate_execution_report(self, qualified_leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Gerar relatório detalhado da execução
        
        Args:
            qualified_leads: Lista de leads qualificados
            
        Returns:
            Relatório da execução
        """
        # Calcular taxa de sucesso
        if self.execution_metrics["leads_discovered"] > 0:
            qualification_rate = self.execution_metrics["leads_qualified"] / self.execution_metrics["leads_discovered"]
        else:
            qualification_rate = 0.0
        
        # Análise por indústria
        industry_analysis = {}
        for lead in qualified_leads:
            industry = lead.get('industry', 'Unknown')
            if industry not in industry_analysis:
                industry_analysis[industry] = {
                    'count': 0,
                    'total_opportunity': 0,
                    'avg_score': 0,
                }
            
            industry_analysis[industry]['count'] += 1
            industry_analysis[industry]['total_opportunity'] += lead.get('opportunity_value', 0)
        
        # Calcular médias
        for industry, data in industry_analysis.items():
            if data['count'] > 0:
                industry_leads = [l for l in qualified_leads if l.get('industry') == industry]
                data['avg_score'] = sum(l.get('qualification_score', 0) for l in industry_leads) / len(industry_leads)
        
        report = {
            "execution_summary": {
                "execution_id": self.execution_id,
                "duration_seconds": self.execution_metrics["duration_seconds"],
                "leads_discovered": self.execution_metrics["leads_discovered"],
                "leads_qualified": self.execution_metrics["leads_qualified"],
                "qualification_rate": qualification_rate,
                "api_calls_made": self.execution_metrics["api_calls_made"],
            },
            "financial_analysis": {
                "total_opportunity_value": self.execution_metrics["total_opportunity_value"],
                "average_qualification_score": self.execution_metrics["average_qualification_score"],
                "estimated_monthly_waste_identified": sum(lead.get('estimated_monthly_waste', 0) for lead in qualified_leads),
            },
            "industry_breakdown": industry_analysis,
            "top_opportunities": sorted(
                qualified_leads,
                key=lambda x: x.get('opportunity_value', 0),
                reverse=True
            )[:5],
            "bigquery_status": "Enabled" if self.bigquery_enabled else "Disabled",
        }
        
        return report

    def run_pipeline(self, 
                    search_queries: Optional[List[str]] = None, 
                    max_results_per_query: int = 30) -> Dict[str, Any]:
        """
        Executar pipeline completo ARCO Enhanced
        
        Args:
            search_queries: Queries customizadas ou usar padrão
            max_results_per_query: Máximo de resultados por query
            
        Returns:
            Relatório completo da execução
        """
        self.execution_metrics["start_time"] = datetime.utcnow()
        
        logging.info(f"🚀 Iniciando ARCO Pipeline Enhanced - Execução: {self.execution_id}")
        
        # Queries padrão se não fornecidas
        if not search_queries:
            search_queries = [
                "lawyers meta ads facebook advertising legal services",
                "law firm digital marketing facebook ads legal",
                "attorney meta advertising lawyers facebook marketing",
                "legal services facebook ads law firm marketing",
                "lawyers digital advertising meta ads legal marketing",
            ]
        
        try:
            # 1. Descobrir Prospects
            prospects = self.discover_prospects(search_queries, max_results_per_query)
            
            # 2. Qualificar Leads
            qualified_leads = self.qualify_leads(prospects)
            
            # 3. Salvar Resultados
            export_path = self.save_results(qualified_leads)
            
            # 4. Gerar Relatório
            execution_report = self.generate_execution_report(qualified_leads)
            
            # Finalizar métricas
            self.execution_metrics["end_time"] = datetime.utcnow()
            self.execution_metrics["duration_seconds"] = (
                self.execution_metrics["end_time"] - self.execution_metrics["start_time"]
            ).total_seconds()
            
            # Taxa de sucesso
            if self.execution_metrics["api_calls_made"] > 0:
                self.execution_metrics["success_rate"] = 1.0  # Simplificado - pode ser refinado
            
            # Relatório final
            final_report = {
                "status": "SUCCESS",
                "execution_id": self.execution_id,
                "export_path": export_path,
                "execution_report": execution_report,
                "qualified_leads": qualified_leads,
                "bigquery_integration": self.bigquery_enabled,
            }
            
            logging.info(f"✅ Pipeline Enhanced concluído com sucesso!")
            logging.info(f"📊 {len(qualified_leads)} leads qualificados identificados")
            logging.info(f"💰 ${execution_report['financial_analysis']['total_opportunity_value']:,.2f} em oportunidades")
            
            return final_report
            
        except Exception as e:
            logging.error(f"❌ Erro crítico no pipeline: {e}")
            
            # Finalizar métricas mesmo com erro
            self.execution_metrics["end_time"] = datetime.utcnow()
            self.execution_metrics["duration_seconds"] = (
                self.execution_metrics["end_time"] - self.execution_metrics["start_time"]
            ).total_seconds()
            
            return {
                "status": "ERROR",
                "execution_id": self.execution_id,
                "error": str(e),
                "execution_metrics": self.execution_metrics,
            }


def main():
    """
    Função principal para executar pipeline
    """
    # Inicializar pipeline
    pipeline = ARCOPipelineEnhanced()
    
    # Executar pipeline
    result = pipeline.run_pipeline()
    
    # Mostrar resultado
    if result["status"] == "SUCCESS":
        print(f"\n🎉 ARCO Pipeline Enhanced - Execução Bem-Sucedida!")
        print(f"📁 Resultados salvos em: {result['export_path']}")
        print(f"🎯 Leads qualificados: {len(result['qualified_leads'])}")
        print(f"💰 Valor total de oportunidades: ${result['execution_report']['financial_analysis']['total_opportunity_value']:,.2f}")
        print(f"☁️ BigQuery Integration: {'✅ Ativo' if result['bigquery_integration'] else '❌ Inativo'}")
    else:
        print(f"\n❌ Pipeline falhou: {result.get('error', 'Erro desconhecido')}")
    
    return result


if __name__ == "__main__":
    main()
