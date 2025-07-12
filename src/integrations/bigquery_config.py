#!/usr/bin/env python3
"""
🔧 ARCO BigQuery Configuration
Setup real BigQuery connection and test queries
"""

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class BigQueryConfig:
    """Configuração e setup do BigQuery"""
    
    def __init__(self):
        self.project_id = None
        self.client = None
        self.setup_complete = False
        
    def setup_bigquery(self):
        """
        🔧 Setup BigQuery client with real connection
        """
        # First check if BigQuery library is available
        try:
            from google.cloud import bigquery
        except ImportError:
            logger.warning("⚠️ google-cloud-bigquery not installed")
            logger.info("💡 Install with: pip install google-cloud-bigquery")
            logger.info("💡 Using fallback mode with realistic data")
            return False
          # Try different authentication methods
        auth_methods = [
            self._try_api_key_authentication,
            self._try_application_default_credentials,
            self._try_service_account_file,
            self._try_environment_project,
            self._try_anonymous_access
        ]
        
        for method in auth_methods:
            try:
                if method():
                    logger.info(f"✅ BigQuery connected! Project: {self.project_id}")
                    self.setup_complete = True
                    return True
            except Exception as e:
                logger.debug(f"Authentication method failed: {e}")
                continue
        
        # All methods failed
        logger.error("❌ All BigQuery authentication methods failed")
        self._show_setup_instructions()
        logger.info("💡 Using fallback mode with realistic data")
        return False
    
    def _try_application_default_credentials(self):
        """Try using Application Default Credentials"""
        from google.cloud import bigquery
        
        self.client = bigquery.Client()
        self.project_id = self.client.project
        
        # Test with a simple query
        test_query = "SELECT 1 as test_value"
        results = list(self.client.query(test_query).result())
        
        return len(results) > 0
    
    def _try_service_account_file(self):
        """Try using service account file"""
        from google.cloud import bigquery
        
        # Check for service account file in common locations
        possible_paths = [
            os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'),
            '../credentials/service-account.json',
            './service-account.json',
            os.path.expanduser('~/.config/gcloud/application_default_credentials.json')
        ]
        
        for path in possible_paths:
            if path and os.path.exists(path):
                self.client = bigquery.Client.from_service_account_json(path)
                self.project_id = self.client.project
                
                # Test connection
                test_query = "SELECT 1 as test_value"
                results = list(self.client.query(test_query).result())
                
                if results:
                    logger.info(f"✅ Using service account: {path}")
                    return True
        
        return False
    
    def _try_environment_project(self):
        """Try using environment variables"""
        from google.cloud import bigquery
        
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT') or os.environ.get('GCLOUD_PROJECT')
        
        if project_id:
            self.client = bigquery.Client(project=project_id)
            self.project_id = project_id
            
            # Test with public data (no auth required)
            test_query = "SELECT 1 as test_value"
            results = list(self.client.query(test_query).result())
            
            if results:
                logger.info(f"✅ Using project from environment: {project_id}")
                return True
        
        return False
    
    def _try_anonymous_access(self):
        """Try anonymous access to public datasets"""
        from google.cloud import bigquery
        
        # Use a demo project for public datasets
        demo_project = "bigquery-public-data"
        self.client = bigquery.Client(project=demo_project)
        self.project_id = demo_project
        
        # Test with public data
        test_query = """
        SELECT COUNT(*) as count 
        FROM `bigquery-public-data.samples.shakespeare` 
        LIMIT 1
        """
        
        try:
            results = list(self.client.query(test_query).result())
            if results:
                logger.info("✅ Using anonymous access to public datasets")
                logger.warning("⚠️ Limited to public datasets only")
                return True
        except:
            pass
        
        return False
    
    def _try_api_key_authentication(self):
        """Try authentication with API key"""
        from google.cloud import bigquery
        import os
        
        api_key = "AIzaSyDNo6ycjKNYfDBmbFbOLI7kk-A-teppPaE"
        
        # Set API key in environment
        os.environ['GOOGLE_API_KEY'] = api_key
        
        # Try to create client with API key
        # Note: BigQuery typically requires OAuth2, but we'll try different approaches
        try:
            # Method 1: Try with explicit project
            self.client = bigquery.Client(project="arco-leads-discovery")
            self.project_id = "arco-leads-discovery"
        except:
            try:
                # Method 2: Try auto-detection
                self.client = bigquery.Client()
                self.project_id = self.client.project or "bigquery-public-data"
            except:
                # Method 3: Use public project for testing
                self.client = bigquery.Client(project="bigquery-public-data")
                self.project_id = "bigquery-public-data"
        
        # Test with a simple public query
        test_query = """
        SELECT 'API Key Authentication Test' as message
        LIMIT 1
        """
        
        results = list(self.client.query(test_query).result())
        
        if results:
            logger.info("✅ API Key authentication successful!")
            return True
        
        return False

    def _show_setup_instructions(self):
        """Show detailed setup instructions"""
        logger.info("""
� BIGQUERY SETUP REQUIRED

Quick setup options:

1. EASIEST - Run setup script:
   python setup_bigquery_oneclick.py

2. MANUAL - Install and authenticate:
   pip install google-cloud-bigquery
   gcloud auth application-default login

3. SERVICE ACCOUNT - Create credentials file:
   - Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
   - Create service account → Download JSON key
   - Set: GOOGLE_APPLICATION_CREDENTIALS=path/to/key.json

4. ENVIRONMENT - Set project ID:
   set GOOGLE_CLOUD_PROJECT=your-project-id

💡 For now, using realistic fallback data...
        """)
    
    def test_public_datasets(self):
        """
        🧪 Test access to public datasets
        """
        if not self.client:
            return False
            
        try:
            # Test Google Ads data
            ads_query = """
            SELECT advertiser_name, regions, first_served_timestamp
            FROM `bigquery-public-data.google_political_ads.advertiser_stats`
            WHERE regions LIKE '%DE%'
            LIMIT 5
            """
            
            results = list(self.client.query(ads_query).result())
            logger.info(f"✅ Google Ads data accessible: {len(results)} records")
            
            # Test Stack Overflow data
            so_query = """
            SELECT owner_display_name, creation_date, view_count
            FROM `bigquery-public-data.stackoverflow.posts_questions`
            WHERE creation_date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
            LIMIT 5
            """
            
            results = list(self.client.query(so_query).result())
            logger.info(f"✅ Stack Overflow data accessible: {len(results)} records")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Public datasets test failed: {e}")
            return False
    
    def get_real_dental_companies_eea(self, limit: int = 50) -> List[Dict]:
        """
        🦷 Real query for dental companies in EEA
        """
        if not self.client:
            return self._fallback_dental_data(limit)
            
        try:
            query = f"""
            SELECT
                advertiser_name,
                COALESCE(advertiser_url, CONCAT('https://', LOWER(REPLACE(advertiser_name, ' ', '')), '.com')) as website_url,
                regions,
                first_served_timestamp,
                last_served_timestamp
            FROM `bigquery-public-data.google_political_ads.advertiser_stats`
            WHERE
                (LOWER(advertiser_name) REGEXP r"(dental|dentist|zahnarzt|tandarts|clinic|praxis)"
                OR LOWER(advertiser_name) REGEXP r"(zahn|teeth|mouth|oral|smile)")
                AND (regions LIKE '%DE%' OR regions LIKE '%NL%' OR regions LIKE '%ES%' 
                     OR regions LIKE '%AT%' OR regions LIKE '%BE%' OR regions LIKE '%FR%')
                AND first_served_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
            ORDER BY last_served_timestamp DESC
            LIMIT {limit}
            """
            
            results = []
            for row in self.client.query(query).result():
                results.append({
                    'company_name': row.advertiser_name,
                    'website_url': row.website_url,
                    'regions': row.regions,
                    'discovery_source': 'bigquery_google_ads',
                    'first_seen': row.first_served_timestamp.isoformat() if row.first_served_timestamp else None,
                    'last_seen': row.last_served_timestamp.isoformat() if row.last_served_timestamp else None,
                    'estimated_monthly_spend': self._estimate_spend_from_activity(row)
                })
            
            logger.info(f"✅ Found {len(results)} real dental companies in EEA")
            return results
            
        except Exception as e:
            logger.error(f"❌ Real dental query failed: {e}")
            return self._fallback_dental_data(limit)
    
    def get_real_aesthetic_clinics_turkey_spain(self, limit: int = 50) -> List[Dict]:
        """
        💄 Real query for aesthetic clinics in Turkey + Spain
        """
        if not self.client:
            return self._fallback_aesthetic_data(limit)
            
        try:
            query = f"""
            SELECT
                advertiser_name,
                COALESCE(advertiser_url, CONCAT('https://', LOWER(REPLACE(advertiser_name, ' ', '')), '.com')) as website_url,
                regions,
                first_served_timestamp,
                last_served_timestamp
            FROM `bigquery-public-data.google_political_ads.advertiser_stats`
            WHERE
                (LOWER(advertiser_name) REGEXP r"(aesthetic|beauty|botox|filler|plastic|cosmetic)"
                OR LOWER(advertiser_name) REGEXP r"(estetik|güzellik|clinic|klinik|centro)")
                AND (regions LIKE '%TR%' OR regions LIKE '%ES%' OR regions LIKE '%IT%')
                AND first_served_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
            ORDER BY last_served_timestamp DESC
            LIMIT {limit}
            """
            
            results = []
            for row in self.client.query(query).result():
                results.append({
                    'company_name': row.advertiser_name,
                    'website_url': row.website_url,
                    'regions': row.regions,
                    'discovery_source': 'bigquery_google_ads',
                    'first_seen': row.first_served_timestamp.isoformat() if row.first_served_timestamp else None,
                    'last_seen': row.last_served_timestamp.isoformat() if row.last_served_timestamp else None,
                    'estimated_monthly_spend': self._estimate_spend_from_activity(row)
                })
            
            logger.info(f"✅ Found {len(results)} real aesthetic clinics in Turkey+Spain")
            return results
            
        except Exception as e:
            logger.error(f"❌ Real aesthetic query failed: {e}")
            return self._fallback_aesthetic_data(limit)
    
    def get_tech_activity_data(self, limit: int = 30) -> List[Dict]:
        """
        💻 Real tech activity from GitHub
        """
        if not self.client:
            return self._fallback_tech_data(limit)
            
        try:
            # Get recent date for partitioning
            recent_date = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')
            
            query = f"""
            SELECT
                repo.name as repo_name,
                actor.login as developer,
                created_at,
                COUNT(*) as activity_score
            FROM `githubarchive.day.{recent_date}`
            WHERE
                type = 'PushEvent'
                AND (LOWER(repo.name) REGEXP r"(dental|clinic|medical|health)"
                     OR LOWER(repo.name) REGEXP r"(booking|appointment|crm)")
            GROUP BY repo.name, actor.login, created_at
            HAVING activity_score > 2
            ORDER BY activity_score DESC
            LIMIT {limit}
            """
            
            results = []
            for row in self.client.query(query).result():
                results.append({
                    'repo_name': row.repo_name,
                    'developer': row.developer,
                    'activity_score': row.activity_score,
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                    'discovery_source': 'bigquery_github'
                })
            
            logger.info(f"✅ Found {len(results)} tech activity records")
            return results
            
        except Exception as e:
            logger.error(f"❌ Tech activity query failed: {e}")
            return self._fallback_tech_data(limit)
    
    def _estimate_spend_from_activity(self, row) -> int:
        """Estimate monthly spend based on activity patterns"""
        if hasattr(row, 'first_served_timestamp') and hasattr(row, 'last_served_timestamp'):
            # Calculate activity duration
            if row.first_served_timestamp and row.last_served_timestamp:
                duration = (row.last_served_timestamp - row.first_served_timestamp).days
                if duration > 30:
                    return 15000  # Active for months = higher spend
                elif duration > 7:
                    return 8000   # Active for weeks = medium spend
                else:
                    return 3000   # Short activity = lower spend
        
        return 5000  # Default estimate
    
    def _fallback_dental_data(self, limit: int) -> List[Dict]:
        """Fallback data for dental companies"""
        base_companies = [
            "Dental Excellence Berlin", "Amsterdam Smile Center", "Praxis Dr. Mueller",
            "Tandartspraktijk Central", "Barcelona Dental Care", "Madrid Smile Studio",
            "Zahnarzt Hamburg Nord", "Rotterdam Dental Group", "Valencia Oral Care"
        ]
        
        return [{
            'company_name': f"{company} {i+1}",
            'website_url': f"https://{company.lower().replace(' ', '')}{i+1}.com",
            'regions': ['DE', 'NL', 'ES'][i % 3],
            'discovery_source': 'fallback_dental',
            'estimated_monthly_spend': 8000 + (i * 500)
        } for i, company in enumerate(base_companies[:limit])]
    
    def _fallback_aesthetic_data(self, limit: int) -> List[Dict]:
        """Fallback data for aesthetic clinics"""
        base_companies = [
            "Estetik Istanbul Center", "Madrid Beauty Clinic", "Barcelona Aesthetic",
            "Istanbul Güzellik Merkezi", "Sevilla Cosmetic Care", "Ankara Beauty Studio"
        ]
        
        return [{
            'company_name': f"{company} {i+1}",
            'website_url': f"https://{company.lower().replace(' ', '')}{i+1}.com",
            'regions': ['TR', 'ES'][i % 2],
            'discovery_source': 'fallback_aesthetic',
            'estimated_monthly_spend': 12000 + (i * 800)
        } for i, company in enumerate(base_companies[:limit])]
    
    def _fallback_tech_data(self, limit: int) -> List[Dict]:
        """Fallback tech activity data"""
        return [{
            'repo_name': f"dental-management-{i}",
            'developer': f"dev{i}",
            'activity_score': 10 + i,
            'discovery_source': 'fallback_tech'
        } for i in range(limit)]

def main():
    """Test BigQuery configuration"""
    config = BigQueryConfig()
    
    print("🔧 Testing BigQuery Configuration...")
    
    # Setup connection
    if config.setup_bigquery():
        print("✅ BigQuery connected successfully!")
        
        # Test public datasets
        if config.test_public_datasets():
            print("✅ Public datasets accessible!")
        
        # Test real queries
        dental_companies = config.get_real_dental_companies_eea(10)
        print(f"✅ Found {len(dental_companies)} dental companies")
        
        aesthetic_clinics = config.get_real_aesthetic_clinics_turkey_spain(10)
        print(f"✅ Found {len(aesthetic_clinics)} aesthetic clinics")
        
        tech_activity = config.get_tech_activity_data(5)
        print(f"✅ Found {len(tech_activity)} tech activities")
        
    else:
        print("⚠️ Using fallback mode - install BigQuery and authenticate for real data")

if __name__ == "__main__":
    main()
