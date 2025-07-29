"""
BigQuery Integration for ARCO Pipeline
Integra os resultados do pipeline com BigQuery para análises avançadas e relatórios estratégicos
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import pandas as pd
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import os

class ARCOBigQueryIntegration:
    def __init__(self, project_id: str = "prospection-463116", dataset_id: str = "arco_intelligence"):
        """
        Inicializa integração BigQuery para ARCO Pipeline
        
        Args:
            project_id: ID do projeto Google Cloud
            dataset_id: ID do dataset BigQuery
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_qualified_leads = "qualified_leads"
        self.table_pipeline_metrics = "pipeline_metrics"
        self.table_discovery_analytics = "discovery_analytics"
        
        # Configurar credenciais via gcloud SDK
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = ''  # Usar gcloud auth
        
        try:
            self.client = bigquery.Client(project=project_id)
            self.dataset_ref = self.client.dataset(dataset_id)
            logging.info(f"✅ BigQuery client inicializado - Projeto: {project_id}, Dataset: {dataset_id}")
        except Exception as e:
            logging.error(f"❌ Erro ao inicializar BigQuery: {e}")
            raise

    def create_tables_if_not_exist(self) -> bool:
        """
        Cria tabelas necessárias se não existirem
        
        Returns:
            bool: True se tabelas foram criadas/verificadas com sucesso
        """
        try:
            # Schema para qualified_leads
            qualified_leads_schema = [
                bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("company_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("website", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("domain", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("industry", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("annual_revenue", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("employee_count", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("location", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("contact_email", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("contact_phone", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("meta_ads_potential", "FLOAT", mode="NULLABLE"),
                bigquery.SchemaField("current_advertising", "JSON", mode="NULLABLE"),
                bigquery.SchemaField("competitive_analysis", "JSON", mode="NULLABLE"),
                bigquery.SchemaField("discovery_insights", "JSON", mode="NULLABLE"),
                bigquery.SchemaField("qualification_score", "FLOAT", mode="NULLABLE"),
                bigquery.SchemaField("estimated_monthly_waste", "FLOAT", mode="NULLABLE"),
                bigquery.SchemaField("opportunity_value", "FLOAT", mode="NULLABLE"),
                bigquery.SchemaField("discovery_timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("pipeline_version", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("data_sources", "JSON", mode="NULLABLE"),
            ]

            # Schema para pipeline_metrics
            pipeline_metrics_schema = [
                bigquery.SchemaField("execution_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("execution_timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("pipeline_version", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("total_leads_discovered", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("qualified_leads_count", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("qualification_rate", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("total_opportunity_value", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("average_qualification_score", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("execution_duration_seconds", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("api_calls_made", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("success_rate", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("configuration", "JSON", mode="NULLABLE"),
                bigquery.SchemaField("performance_metrics", "JSON", mode="NULLABLE"),
            ]

            # Schema para discovery_analytics
            discovery_analytics_schema = [
                bigquery.SchemaField("analysis_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("analysis_timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("analysis_type", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("target_domain", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("search_query", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("results_found", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("processing_time_ms", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("data_quality_score", "FLOAT", mode="NULLABLE"),
                bigquery.SchemaField("insights_extracted", "JSON", mode="NULLABLE"),
                bigquery.SchemaField("competitive_intel", "JSON", mode="NULLABLE"),
                bigquery.SchemaField("market_indicators", "JSON", mode="NULLABLE"),
            ]

            # Criar tabelas
            tables_to_create = [
                (self.table_qualified_leads, qualified_leads_schema),
                (self.table_pipeline_metrics, pipeline_metrics_schema),
                (self.table_discovery_analytics, discovery_analytics_schema),
            ]

            for table_name, schema in tables_to_create:
                table_ref = self.dataset_ref.table(table_name)
                try:
                    self.client.get_table(table_ref)
                    logging.info(f"✅ Tabela {table_name} já existe")
                except NotFound:
                    table = bigquery.Table(table_ref, schema=schema)
                    table = self.client.create_table(table)
                    logging.info(f"✅ Tabela {table_name} criada com sucesso")

            return True

        except Exception as e:
            logging.error(f"❌ Erro ao criar tabelas: {e}")
            return False

    def upload_qualified_leads(self, leads_data: List[Dict[str, Any]], execution_id: str) -> bool:
        """
        Faz upload dos leads qualificados para BigQuery
        
        Args:
            leads_data: Lista de leads qualificados
            execution_id: ID da execução do pipeline
            
        Returns:
            bool: True se upload foi bem-sucedido
        """
        try:
            if not leads_data:
                logging.warning("Nenhum lead para upload")
                return True

            # Preparar dados para BigQuery
            processed_leads = []
            current_timestamp = datetime.utcnow()

            for lead in leads_data:
                processed_lead = {
                    "id": f"{execution_id}_{lead.get('domain', 'unknown')}_{int(current_timestamp.timestamp())}",
                    "company_name": lead.get("company_name", ""),
                    "website": lead.get("website", ""),
                    "domain": lead.get("domain", ""),
                    "industry": lead.get("industry"),
                    "annual_revenue": lead.get("annual_revenue"),
                    "employee_count": lead.get("employee_count"),
                    "location": lead.get("location"),
                    "contact_email": lead.get("contact_email"),
                    "contact_phone": lead.get("contact_phone"),
                    "meta_ads_potential": lead.get("meta_ads_potential"),
                    "current_advertising": json.dumps(lead.get("current_advertising", {})),
                    "competitive_analysis": json.dumps(lead.get("competitive_analysis", {})),
                    "discovery_insights": json.dumps(lead.get("discovery_insights", {})),
                    "qualification_score": lead.get("qualification_score"),
                    "estimated_monthly_waste": lead.get("estimated_monthly_waste"),
                    "opportunity_value": lead.get("opportunity_value"),
                    "discovery_timestamp": current_timestamp,
                    "pipeline_version": "v1.0",
                    "data_sources": json.dumps(lead.get("data_sources", [])),
                }
                processed_leads.append(processed_lead)

            # Upload para BigQuery
            table_ref = self.dataset_ref.table(self.table_qualified_leads)
            table = self.client.get_table(table_ref)
            
            errors = self.client.insert_rows_json(table, processed_leads)
            
            if errors:
                logging.error(f"❌ Erros ao inserir leads: {errors}")
                return False
            else:
                logging.info(f"✅ {len(processed_leads)} leads carregados com sucesso no BigQuery")
                return True

        except Exception as e:
            logging.error(f"❌ Erro ao fazer upload de leads: {e}")
            return False

    def upload_pipeline_metrics(self, metrics: Dict[str, Any], execution_id: str) -> bool:
        """
        Faz upload das métricas do pipeline para BigQuery
        
        Args:
            metrics: Métricas da execução do pipeline
            execution_id: ID da execução
            
        Returns:
            bool: True se upload foi bem-sucedido
        """
        try:
            processed_metrics = {
                "execution_id": execution_id,
                "execution_timestamp": datetime.utcnow(),
                "pipeline_version": "v1.0",
                "total_leads_discovered": metrics.get("total_leads_discovered", 0),
                "qualified_leads_count": metrics.get("qualified_leads_count", 0),
                "qualification_rate": metrics.get("qualification_rate", 0.0),
                "total_opportunity_value": metrics.get("total_opportunity_value", 0.0),
                "average_qualification_score": metrics.get("average_qualification_score", 0.0),
                "execution_duration_seconds": metrics.get("execution_duration_seconds", 0.0),
                "api_calls_made": metrics.get("api_calls_made", 0),
                "success_rate": metrics.get("success_rate", 0.0),
                "configuration": json.dumps(metrics.get("configuration", {})),
                "performance_metrics": json.dumps(metrics.get("performance_metrics", {})),
            }

            table_ref = self.dataset_ref.table(self.table_pipeline_metrics)
            table = self.client.get_table(table_ref)
            
            errors = self.client.insert_rows_json(table, [processed_metrics])
            
            if errors:
                logging.error(f"❌ Erros ao inserir métricas: {errors}")
                return False
            else:
                logging.info(f"✅ Métricas do pipeline carregadas com sucesso no BigQuery")
                return True

        except Exception as e:
            logging.error(f"❌ Erro ao fazer upload de métricas: {e}")
            return False

    def get_analytics_dashboard_data(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Recupera dados para dashboard de analytics
        
        Args:
            days_back: Número de dias para análise retroativa
            
        Returns:
            Dict com dados para dashboard
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Query para métricas gerais
            metrics_query = f"""
            SELECT 
                COUNT(*) as total_executions,
                SUM(qualified_leads_count) as total_qualified_leads,
                AVG(qualification_rate) as avg_qualification_rate,
                SUM(total_opportunity_value) as total_opportunity_value,
                AVG(execution_duration_seconds) as avg_execution_time,
                AVG(success_rate) as avg_success_rate
            FROM `{self.project_id}.{self.dataset_id}.{self.table_pipeline_metrics}`
            WHERE execution_timestamp >= @start_date
            """

            # Query para top leads
            top_leads_query = f"""
            SELECT 
                company_name,
                domain,
                qualification_score,
                opportunity_value,
                estimated_monthly_waste,
                industry
            FROM `{self.project_id}.{self.dataset_id}.{self.table_qualified_leads}`
            WHERE discovery_timestamp >= @start_date
            ORDER BY qualification_score DESC
            LIMIT 10
            """

            # Query para análise por indústria
            industry_analysis_query = f"""
            SELECT 
                industry,
                COUNT(*) as lead_count,
                AVG(qualification_score) as avg_score,
                SUM(opportunity_value) as total_opportunity
            FROM `{self.project_id}.{self.dataset_id}.{self.table_qualified_leads}`
            WHERE discovery_timestamp >= @start_date AND industry IS NOT NULL
            GROUP BY industry
            ORDER BY total_opportunity DESC
            """

            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", start_date)
                ]
            )

            # Executar queries
            metrics_result = list(self.client.query(metrics_query, job_config=job_config))
            top_leads_result = list(self.client.query(top_leads_query, job_config=job_config))
            industry_result = list(self.client.query(industry_analysis_query, job_config=job_config))

            dashboard_data = {
                "period": f"Últimos {days_back} dias",
                "generated_at": datetime.utcnow().isoformat(),
                "metrics": {
                    "total_executions": metrics_result[0].total_executions if metrics_result else 0,
                    "total_qualified_leads": metrics_result[0].total_qualified_leads if metrics_result else 0,
                    "avg_qualification_rate": float(metrics_result[0].avg_qualification_rate) if metrics_result and metrics_result[0].avg_qualification_rate else 0.0,
                    "total_opportunity_value": float(metrics_result[0].total_opportunity_value) if metrics_result and metrics_result[0].total_opportunity_value else 0.0,
                    "avg_execution_time": float(metrics_result[0].avg_execution_time) if metrics_result and metrics_result[0].avg_execution_time else 0.0,
                    "avg_success_rate": float(metrics_result[0].avg_success_rate) if metrics_result and metrics_result[0].avg_success_rate else 0.0,
                },
                "top_leads": [
                    {
                        "company_name": row.company_name,
                        "domain": row.domain,
                        "qualification_score": float(row.qualification_score) if row.qualification_score else 0.0,
                        "opportunity_value": float(row.opportunity_value) if row.opportunity_value else 0.0,
                        "estimated_monthly_waste": float(row.estimated_monthly_waste) if row.estimated_monthly_waste else 0.0,
                        "industry": row.industry,
                    }
                    for row in top_leads_result
                ],
                "industry_analysis": [
                    {
                        "industry": row.industry,
                        "lead_count": row.lead_count,
                        "avg_score": float(row.avg_score) if row.avg_score else 0.0,
                        "total_opportunity": float(row.total_opportunity) if row.total_opportunity else 0.0,
                    }
                    for row in industry_result
                ]
            }

            logging.info(f"✅ Dashboard data gerado com sucesso")
            return dashboard_data

        except Exception as e:
            logging.error(f"❌ Erro ao gerar dashboard data: {e}")
            return {}

    def export_leads_to_csv(self, output_path: str, days_back: int = 30) -> bool:
        """
        Exporta leads para CSV para análise externa
        
        Args:
            output_path: Caminho para salvar o arquivo CSV
            days_back: Número de dias para exportação
            
        Returns:
            bool: True se exportação foi bem-sucedida
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days_back)
            
            query = f"""
            SELECT 
                company_name,
                website,
                domain,
                industry,
                annual_revenue,
                employee_count,
                location,
                contact_email,
                contact_phone,
                qualification_score,
                opportunity_value,
                estimated_monthly_waste,
                discovery_timestamp
            FROM `{self.project_id}.{self.dataset_id}.{self.table_qualified_leads}`
            WHERE discovery_timestamp >= @start_date
            ORDER BY qualification_score DESC
            """

            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", start_date)
                ]
            )

            df = self.client.query(query, job_config=job_config).to_dataframe()
            
            if not df.empty:
                df.to_csv(output_path, index=False, encoding='utf-8-sig')
                logging.info(f"✅ {len(df)} leads exportados para {output_path}")
                return True
            else:
                logging.warning("Nenhum lead encontrado para exportação")
                return False

        except Exception as e:
            logging.error(f"❌ Erro ao exportar leads para CSV: {e}")
            return False


def test_bigquery_integration():
    """
    Teste da integração BigQuery
    """
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Inicializar integração
        bq_integration = ARCOBigQueryIntegration()
        
        # Criar tabelas
        if not bq_integration.create_tables_if_not_exist():
            logging.error("Falha ao criar tabelas")
            return False
        
        # Dados de teste
        test_leads = [
            {
                "company_name": "Teste Company Ltd",
                "website": "https://teste.com",
                "domain": "teste.com",
                "industry": "Legal Services",
                "qualification_score": 8.5,
                "opportunity_value": 15000.0,
                "estimated_monthly_waste": 3000.0,
                "discovery_insights": {"test": "data"},
            }
        ]
        
        test_metrics = {
            "total_leads_discovered": 10,
            "qualified_leads_count": 1,
            "qualification_rate": 0.1,
            "total_opportunity_value": 15000.0,
            "average_qualification_score": 8.5,
            "execution_duration_seconds": 45.0,
            "api_calls_made": 25,
            "success_rate": 1.0,
        }
        
        execution_id = f"test_{int(datetime.utcnow().timestamp())}"
        
        # Testar uploads
        if not bq_integration.upload_qualified_leads(test_leads, execution_id):
            logging.error("Falha ao fazer upload de leads")
            return False
            
        if not bq_integration.upload_pipeline_metrics(test_metrics, execution_id):
            logging.error("Falha ao fazer upload de métricas")
            return False
        
        logging.info("✅ Teste BigQuery Integration concluído com sucesso!")
        return True
        
    except Exception as e:
        logging.error(f"❌ Erro no teste: {e}")
        return False


if __name__ == "__main__":
    test_bigquery_integration()
