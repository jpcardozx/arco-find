
import json
import uuid
from datetime import datetime
from google.cloud import bigquery
from typing import List, Dict, Any

class ArcoBigQueryIntegration:
    """Integração BigQuery para o pipeline ARCO"""
    
    def __init__(self, project_id: str = "prospection-463116", dataset_id: str = "arco_intelligence"):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.client = bigquery.Client(project=project_id)
        
    def log_execution_start(self, pipeline_version: str = "v1.0_optimized") -> str:
        """Registra início de execução e retorna execution_id"""
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        execution_data = {
            "execution_id": execution_id,
            "timestamp": datetime.now().isoformat(),
            "pipeline_version": pipeline_version,
            "execution_time_seconds": 0.0,
            "leads_found": 0,
            "leads_qualified": 0,
            "total_waste_detected": 0.0,
            "avg_icp_score": 0.0,
            "avg_urgency_score": 0.0,
            "industries_covered": [],
            "success": False,
            "error_message": None,
            "metadata_json": json.dumps({"status": "started"})  # JSON como STRING
        }
        
        table_ref = f"{self.project_id}.{self.dataset_id}.pipeline_executions"
        table = self.client.get_table(table_ref)
        
        errors = self.client.insert_rows_json(table, [execution_data])
        if errors:
            print(f"❌ Erro ao log execution start: {errors}")
        else:
            print(f"📊 Execution {execution_id} registrada no BigQuery")
            
        return execution_id
    
    def save_qualified_leads(self, leads: List[Dict[str, Any]], execution_id: str, pipeline_version: str = "v1.0_optimized"):
        """Salva leads qualificados no BigQuery"""
        
        if not leads:
            return
            
        bigquery_leads = []
        for lead in leads:
            bq_lead = {
                "id": f"lead_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}",
                "timestamp": datetime.now().isoformat(),
                "company_name": lead.get("company_name", ""),
                "domain": lead.get("domain", ""),
                "industry": lead.get("industry", ""),
                "location": lead.get("location", ""),
                "icp_score": float(lead.get("icp_score", 0.0)),
                "urgency_score": float(lead.get("urgency_score", 0.0)),
                "estimated_waste": float(lead.get("estimated_waste", 0.0)),
                "p0_signals": lead.get("p0_signals", []),
                "approach_vector": lead.get("approach_vector", ""),
                "qualification_reason": lead.get("qualification_reason", ""),
                "contact_info_json": json.dumps(lead.get("contact_info", {})),  # JSON como STRING
                "performance_metrics_json": json.dumps(lead.get("performance_metrics", {})),  # JSON como STRING
                "pipeline_version": pipeline_version,
                "execution_batch": execution_id
            }
            bigquery_leads.append(bq_lead)
        
        table_ref = f"{self.project_id}.{self.dataset_id}.qualified_leads"
        table = self.client.get_table(table_ref)
        
        errors = self.client.insert_rows_json(table, bigquery_leads)
        if errors:
            print(f"❌ Erro ao salvar leads: {errors}")
        else:
            print(f"✅ {len(bigquery_leads)} leads salvos no BigQuery")
    
    def log_execution_complete(self, execution_id: str, execution_time: float, 
                             leads_data: List[Dict[str, Any]], success: bool = True, 
                             error_message: str = None):
        """Inserir nova linha ao invés de UPDATE (evita streaming buffer issues)"""
        
        if leads_data:
            total_waste = sum(lead.get("estimated_waste", 0.0) for lead in leads_data)
            avg_icp = sum(lead.get("icp_score", 0.0) for lead in leads_data) / len(leads_data)
            avg_urgency = sum(lead.get("urgency_score", 0.0) for lead in leads_data) / len(leads_data)
            industries = list(set(lead.get("industry", "") for lead in leads_data))
        else:
            total_waste = 0.0
            avg_icp = 0.0
            avg_urgency = 0.0
            industries = []
        
        # Inserir nova linha de completion ao invés de UPDATE
        completion_data = {
            "execution_id": f"{execution_id}_completed",
            "timestamp": datetime.now().isoformat(),
            "pipeline_version": "v1.0_optimized",
            "execution_time_seconds": execution_time,
            "leads_found": len(leads_data) if leads_data else 0,
            "leads_qualified": len(leads_data) if leads_data else 0,
            "total_waste_detected": total_waste,
            "avg_icp_score": avg_icp,
            "avg_urgency_score": avg_urgency,
            "industries_covered": industries,
            "success": success,
            "error_message": error_message,
            "metadata_json": json.dumps({"status": "completed", "timestamp": datetime.now().isoformat()})
        }
        
        try:
            table_ref = f"{self.project_id}.{self.dataset_id}.pipeline_executions"
            table = self.client.get_table(table_ref)
            
            errors = self.client.insert_rows_json(table, [completion_data])
            if errors:
                print(f"❌ Erro ao inserir completion: {errors}")
            else:
                print(f"✅ Execution {execution_id} completed no BigQuery")
        except Exception as e:
            print(f"❌ Erro ao inserir completion: {e}")
    
    def get_execution_stats(self, days: int = 30) -> Dict[str, Any]:
        """Retorna estatísticas das execuções dos últimos N dias"""
        
        query = f"""
        SELECT 
            COUNT(*) as total_executions,
            SUM(leads_qualified) as total_leads_qualified,
            AVG(leads_qualified) as avg_leads_per_execution,
            SUM(total_waste_detected) as total_waste_detected,
            AVG(total_waste_detected) as avg_waste_per_execution,
            AVG(execution_time_seconds) as avg_execution_time,
            AVG(avg_icp_score) as overall_avg_icp_score,
            COUNTIF(success = true) as successful_executions,
            COUNTIF(success = false) as failed_executions
        FROM `{self.project_id}.{self.dataset_id}.pipeline_executions`
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        AND execution_id LIKE '%_completed'
        """
        
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            
            for row in results:
                return {
                    "total_executions": row.total_executions or 0,
                    "total_leads_qualified": row.total_leads_qualified or 0,
                    "avg_leads_per_execution": row.avg_leads_per_execution or 0,
                    "total_waste_detected": row.total_waste_detected or 0,
                    "avg_waste_per_execution": row.avg_waste_per_execution or 0,
                    "avg_execution_time": row.avg_execution_time or 0,
                    "overall_avg_icp_score": row.overall_avg_icp_score or 0,
                    "successful_executions": row.successful_executions or 0,
                    "failed_executions": row.failed_executions or 0,
                    "success_rate": ((row.successful_executions or 0) / (row.total_executions or 1) * 100) if row.total_executions and row.total_executions > 0 else 0
                }
        except Exception as e:
            print(f"❌ Erro ao buscar stats: {e}")
            return {}
