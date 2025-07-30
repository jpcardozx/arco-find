#!/usr/bin/env python3
"""
🔧 BIGQUERY FINAL SETUP
Complete BigQuery configuration for ARCO project
"""

import os
import sys
import json
from pathlib import Path
from google.cloud import bigquery
from google.oauth2 import service_account

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import config from project root
sys.path.append(str(project_root))
from config.api_keys import APIConfig

class BigQueryFinalSetup:
    """Final BigQuery setup and configuration"""
    
    def __init__(self):
        self.config = APIConfig()
        self.project_id = self.config.GOOGLE_CLOUD_PROJECT
        self.dataset_id = self.config.BIGQUERY_DATASET_ID
        self.client = None
        
    def setup_complete(self):
        """Complete BigQuery setup"""
        print("🔧 BigQuery Final Setup Starting...")
        print(f"📊 Project: {self.project_id}")
        print(f"📁 Dataset: {self.dataset_id}")
        
        try:
            # Initialize client
            self._initialize_client()
            
            # Create dataset
            self._create_dataset()
            
            # Create tables
            self._create_lead_tables()
            
            # Test connection
            self._test_connection()
            
            print("\n✅ BigQuery setup completed successfully!")
            return True
            
        except Exception as e:
            print(f"\n❌ BigQuery setup failed: {e}")
            return False
    
    def _initialize_client(self):
        """Initialize BigQuery client"""
        try:
            # Try with default credentials first
            self.client = bigquery.Client(project=self.project_id)
            print("   ✅ BigQuery client initialized")
        except Exception as e:
            print(f"   ⚠️  Default auth failed: {e}")
            print("   💡 Please run: gcloud auth application-default login")
            raise
    
    def _create_dataset(self):
        """Create dataset if not exists"""
        try:
            dataset_ref = self.client.dataset(self.dataset_id)
            
            try:
                dataset = self.client.get_dataset(dataset_ref)
                print(f"   ✅ Dataset {self.dataset_id} already exists")
            except:
                dataset = bigquery.Dataset(dataset_ref)
                dataset.location = "US"
                dataset = self.client.create_dataset(dataset)
                print(f"   ✅ Created dataset {self.dataset_id}")
                
        except Exception as e:
            print(f"   ❌ Dataset creation failed: {e}")
            raise
    
    def _create_lead_tables(self):
        """Create lead discovery tables"""
        
        # Prospects table
        prospects_schema = [
            bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("company_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("website", "STRING"),
            bigquery.SchemaField("industry", "STRING"),
            bigquery.SchemaField("location", "STRING"),
            bigquery.SchemaField("employee_count", "INTEGER"),
            bigquery.SchemaField("revenue_estimate", "FLOAT"),
            bigquery.SchemaField("discovery_date", "TIMESTAMP"),
            bigquery.SchemaField("qualification_score", "FLOAT"),
            bigquery.SchemaField("contact_info", "JSON"),
            bigquery.SchemaField("tech_stack", "JSON"),
            bigquery.SchemaField("pain_signals", "JSON"),
        ]
        
        self._create_table("prospects", prospects_schema)
        
        # Discovery sessions table
        sessions_schema = [
            bigquery.SchemaField("session_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"), 
            bigquery.SchemaField("search_criteria", "JSON"),
            bigquery.SchemaField("results_count", "INTEGER"),
            bigquery.SchemaField("api_calls_used", "INTEGER"),
            bigquery.SchemaField("execution_time", "FLOAT"),
        ]
        
        self._create_table("discovery_sessions", sessions_schema)
        
        print("   ✅ Lead tables created")
    
    def _create_table(self, table_name, schema):
        """Create individual table"""
        table_ref = self.client.dataset(self.dataset_id).table(table_name)
        
        try:
            self.client.get_table(table_ref)
            print(f"   ✅ Table {table_name} already exists")
        except:
            table = bigquery.Table(table_ref, schema=schema)
            table = self.client.create_table(table)
            print(f"   ✅ Created table {table_name}")
    
    def _test_connection(self):
        """Test BigQuery connection"""
        try:
            query = f"""
            SELECT 
                COUNT(*) as prospect_count,
                COUNT(DISTINCT session_id) as session_count
            FROM `{self.project_id}.{self.dataset_id}.prospects` p
            LEFT JOIN `{self.project_id}.{self.dataset_id}.discovery_sessions` s
            ON DATE(p.discovery_date) = DATE(s.timestamp)
            """
            
            query_job = self.client.query(query)
            results = list(query_job.result())
            
            print(f"   ✅ BigQuery connection test successful")
            print(f"   📊 Current prospects: {results[0].prospect_count}")
            
        except Exception as e:
            print(f"   ⚠️  Connection test failed: {e}")

def main():
    """Main setup execution"""
    setup = BigQueryFinalSetup()
    success = setup.setup_complete()
    
    if success:
        print("\n🎯 Next steps:")
        print("   1. Run: pipelines/main_pipeline.py")
        print("   2. Check data/exports/ for results")
        print("   3. Monitor logs/ for execution details")
    else:
        print("\n💡 Setup troubleshooting:")
        print("   1. Run: gcloud auth application-default login")
        print("   2. Verify project permissions")
        print("   3. Check API keys in config/api_keys.py")

if __name__ == "__main__":
    main()
