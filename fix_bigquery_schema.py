#!/usr/bin/env python3
"""
🔧 BIGQUERY SCHEMA CORRIGIDO
Corrige problemas de schema JSON
"""

from google.cloud import bigquery
import json

def fix_bigquery_schema():
    """Corrigir schema BigQuery com tipos corretos"""
    
    print("🔧 CORRIGINDO BIGQUERY SCHEMA...")
    
    project_id = "prospection-463116"
    dataset_id = "arco_intelligence"
    client = bigquery.Client(project=project_id)
    
    # Schema corrigido para leads - usando STRING para JSON
    leads_schema = [
        bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("company_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("domain", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("industry", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("location", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("icp_score", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("urgency_score", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("estimated_waste", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("p0_signals", "STRING", mode="REPEATED"),
        bigquery.SchemaField("approach_vector", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("qualification_reason", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("contact_info_json", "STRING", mode="NULLABLE"),  # Mudou para STRING
        bigquery.SchemaField("performance_metrics_json", "STRING", mode="NULLABLE"),  # Mudou para STRING
        bigquery.SchemaField("pipeline_version", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("execution_batch", "STRING", mode="REQUIRED")
    ]
    
    # Schema corrigido para executions - usando STRING para JSON
    executions_schema = [
        bigquery.SchemaField("execution_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("pipeline_version", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("execution_time_seconds", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("leads_found", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("leads_qualified", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("total_waste_detected", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("avg_icp_score", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("avg_urgency_score", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("industries_covered", "STRING", mode="REPEATED"),
        bigquery.SchemaField("success", "BOOLEAN", mode="REQUIRED"),
        bigquery.SchemaField("error_message", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("metadata_json", "STRING", mode="NULLABLE")  # Mudou para STRING
    ]
    
    # Criar tabelas com schema corrigido
    dataset_ref = client.dataset(dataset_id)
    
    # Tabela qualified_leads
    table_ref = dataset_ref.table("qualified_leads")
    table = bigquery.Table(table_ref, schema=leads_schema)
    table.description = "Leads qualificados pelo pipeline ARCO"
    client.create_table(table)
    print("✅ Tabela qualified_leads criada com schema corrigido")
    
    # Tabela pipeline_executions  
    table_ref = dataset_ref.table("pipeline_executions")
    table = bigquery.Table(table_ref, schema=executions_schema)
    table.description = "Histórico de execuções do pipeline ARCO"
    client.create_table(table)
    print("✅ Tabela pipeline_executions criada com schema corrigido")
    
    print("🎉 BigQuery schema corrigido com sucesso!")

if __name__ == "__main__":
    fix_bigquery_schema()
