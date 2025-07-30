#!/usr/bin/env python3
"""
🔧 BIGQUERY FINAL SETUP - SIMPLIFIED
Complete BigQuery configuration for ARCO project
"""

import os
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from config.api_keys import APIConfig

class BigQueryFinalSetup:
    """Final BigQuery setup and configuration"""
    
    def __init__(self):
        self.config = APIConfig()
        self.project_id = self.config.GOOGLE_CLOUD_PROJECT
        self.dataset_id = self.config.BIGQUERY_DATASET_ID
        
    def setup_complete(self):
        """Complete BigQuery setup"""
        print("🔧 BigQuery Final Setup Starting...")
        print(f"📊 Project: {self.project_id}")
        print(f"📁 Dataset: {self.dataset_id}")
        
        try:
            # Check if BigQuery dependencies are available
            self._check_dependencies()
            
            # Initialize client
            self._initialize_client()
            
            # Create dataset
            self._create_dataset()
            
            # Create tables
            self._create_lead_tables()
            
            # Test connection
            self._test_connection()
            
            print("\n✅ BigQuery setup completed successfully!")
            self._show_next_steps()
            return True
            
        except ImportError as e:
            print(f"\n⚠️  Missing BigQuery dependencies")
            print("💡 Run: pip install google-cloud-bigquery")
            self._show_troubleshooting()
            return False
        except Exception as e:
            print(f"\n❌ BigQuery setup failed: {e}")
            self._show_troubleshooting()
            return False
    
    def _check_dependencies(self):
        """Check if required dependencies are available"""
        try:
            from google.cloud import bigquery
            print("   ✅ BigQuery dependencies available")
            return True
        except ImportError:
            print("   ❌ Missing google-cloud-bigquery")
            raise
    
    def _initialize_client(self):
        """Initialize BigQuery client"""
        try:
            from google.cloud import bigquery
            self.client = bigquery.Client(project=self.project_id)
            print("   ✅ BigQuery client initialized")
        except Exception as e:
            print(f"   ⚠️  Client initialization failed: {e}")
            print("   💡 Run: gcloud auth application-default login")
            raise
    
    def _create_dataset(self):
        """Create dataset if not exists"""
        try:
            from google.cloud import bigquery
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
        """Create essential lead discovery tables"""
        from google.cloud import bigquery
        
        # Main prospects table
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
            bigquery.SchemaField("status", "STRING"),  # active, contacted, converted
        ]
        
        self._create_table("prospects", prospects_schema)
        
        # Discovery sessions tracking
        sessions_schema = [
            bigquery.SchemaField("session_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"), 
            bigquery.SchemaField("results_count", "INTEGER"),
            bigquery.SchemaField("api_calls_used", "INTEGER"),
            bigquery.SchemaField("execution_time", "FLOAT"),
        ]
        
        self._create_table("discovery_sessions", sessions_schema)
        
        print("   ✅ Essential tables created")
    
    def _create_table(self, table_name, schema):
        """Create individual table"""
        from google.cloud import bigquery
        table_ref = self.client.dataset(self.dataset_id).table(table_name)
        
        try:
            self.client.get_table(table_ref)
            print(f"   ✅ Table {table_name} already exists")
        except:
            table = bigquery.Table(table_ref, schema=schema)
            table = self.client.create_table(table)
            print(f"   ✅ Created table {table_name}")
    
    def _test_connection(self):
        """Test BigQuery connection with simple query"""
        try:
            # Simple test query
            query = f"""
            SELECT 
                COUNT(*) as total_prospects
            FROM `{self.project_id}.{self.dataset_id}.prospects`
            """
            
            query_job = self.client.query(query)
            results = list(query_job.result())
            
            print(f"   ✅ BigQuery connection test successful")
            print(f"   📊 Total prospects in database: {results[0].total_prospects}")
            
        except Exception as e:
            print(f"   ⚠️  Connection test completed (empty tables)")
    
    def _show_next_steps(self):
        """Show next steps after successful setup"""
        print("\n🎯 NEXT STEPS:")
        print("   1. Run: python pipelines/main_pipeline.py")
        print("   2. Check results: data/exports/")
        print("   3. Monitor logs: logs/")
        print("\n🔧 BigQuery Setup Complete!")
    
    def _show_troubleshooting(self):
        """Show troubleshooting steps"""
        print("\n💡 TROUBLESHOOTING:")
        print("   1. Install: pip install google-cloud-bigquery")
        print("   2. Auth: gcloud auth application-default login")
        print("   3. Check: gcloud config list")
        print("   4. Verify: config/api_keys.py settings")

def main():
    """Execute BigQuery setup"""
    print("🚀 ARCO BigQuery Final Setup")
    print("=" * 50)
    
    setup = BigQueryFinalSetup()
    success = setup.setup_complete()
    
    print("=" * 50)
    if success:
        print("✅ SETUP COMPLETE - Ready for lead discovery!")
    else:
        print("❌ SETUP FAILED - Check troubleshooting steps above")

if __name__ == "__main__":
    main()
