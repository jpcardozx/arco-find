#!/usr/bin/env python3
"""
🔍 BIGQUERY ENRICHMENT SYSTEM
Sistema avançado de enriquecimento de prospects com dados BigQuery
Adiciona inteligência de mercado, métricas de website e informações financeiras
"""

import json
import pandas as pd
from google.cloud import bigquery
from datetime import datetime, timedelta
import requests
import time
from typing import Dict, List, Optional
import re
from pathlib import Path

class BigQueryEnricher:
    """
    Sistema de enriquecimento de prospects usando BigQuery + APIs externas
    """
    
    def __init__(self, project_id: str = "prospection-463116"):
        self.project_id = project_id
        self.client = bigquery.Client(project=project_id)
        self.dataset_id = "prospect_intelligence"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Industry benchmarks para comparação
        self.industry_benchmarks = {
            'dental': {
                'avg_monthly_revenue': 85000,
                'avg_employees': 6,
                'conversion_rate': 0.035,
                'avg_marketing_spend_pct': 0.04
            },
            'medical': {
                'avg_monthly_revenue': 120000,
                'avg_employees': 8,
                'conversion_rate': 0.025,
                'avg_marketing_spend_pct': 0.03
            },
            'legal': {
                'avg_monthly_revenue': 180000,
                'avg_employees': 12,
                'conversion_rate': 0.015,
                'avg_marketing_spend_pct': 0.06
            },
            'accounting': {
                'avg_monthly_revenue': 95000,
                'avg_employees': 7,
                'conversion_rate': 0.028,
                'avg_marketing_spend_pct': 0.035
            },
            'beauty': {
                'avg_monthly_revenue': 75000,
                'avg_employees': 5,
                'conversion_rate': 0.045,
                'avg_marketing_spend_pct': 0.08
            }
        }
    
    def setup_bigquery_tables(self):
        """Setup BigQuery tables for enrichment data"""
        
        # Create dataset if not exists
        dataset_ref = self.client.dataset(self.dataset_id)
        try:
            self.client.get_dataset(dataset_ref)
            print(f"✅ Dataset {self.dataset_id} already exists")
        except:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"
            self.client.create_dataset(dataset)
            print(f"✅ Created dataset {self.dataset_id}")
        
        # Create enrichment table
        table_id = f"{self.project_id}.{self.dataset_id}.prospect_enrichment"
        
        schema = [
            bigquery.SchemaField("domain", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("company_name", "STRING"),
            bigquery.SchemaField("enrichment_date", "TIMESTAMP"),
            
            # Website metrics
            bigquery.SchemaField("page_speed_score", "FLOAT"),
            bigquery.SchemaField("mobile_speed_score", "FLOAT"),
            bigquery.SchemaField("seo_score", "FLOAT"),
            bigquery.SchemaField("website_technologies", "STRING"),
            
            # Business intelligence
            bigquery.SchemaField("linkedin_company_size", "STRING"),
            bigquery.SchemaField("linkedin_industry", "STRING"),
            bigquery.SchemaField("estimated_annual_revenue", "FLOAT"),
            bigquery.SchemaField("employee_count_estimate", "INTEGER"),
            
            # Market analysis
            bigquery.SchemaField("competitive_landscape", "STRING"),
            bigquery.SchemaField("market_opportunity_score", "FLOAT"),
            bigquery.SchemaField("digital_maturity_score", "FLOAT"),
            
            # Contact intelligence
            bigquery.SchemaField("decision_maker_emails", "STRING"),
            bigquery.SchemaField("phone_numbers", "STRING"),
            bigquery.SchemaField("social_media_presence", "STRING"),
            
            # Risk assessment
            bigquery.SchemaField("business_stability_score", "FLOAT"),
            bigquery.SchemaField("payment_capability_score", "FLOAT"),
            bigquery.SchemaField("growth_potential_score", "FLOAT")
        ]
        
        try:
            table_ref = bigquery.TableReference(dataset_ref, "prospect_enrichment")
            table = bigquery.Table(table_ref, schema=schema)
            self.client.create_table(table)
            print(f"✅ Created table prospect_enrichment")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"✅ Table prospect_enrichment already exists")
            else:
                print(f"⚠️ Error creating table: {e}")
    
    def clean_domain(self, domain: str) -> str:
        """Clean domain for consistent processing"""
        if not domain:
            return ""
        
        # Remove protocol, paths, and parameters
        domain = re.sub(r'^https?://', '', domain)
        domain = re.sub(r'/.*$', '', domain)
        domain = re.sub(r' › .*$', '', domain)
        domain = re.sub(r'\?.*$', '', domain)
        
        return domain.lower().strip()
    
    def get_pagespeed_metrics(self, domain: str) -> Dict:
        """Get PageSpeed Insights metrics"""
        
        clean_domain = self.clean_domain(domain)
        if not clean_domain:
            return {}
        
        url = f"https://{clean_domain}"
        api_key = "AIzaSyDNzQ9CqKhyJhGy5H9F7K8rF2N3mP5tR4s"  # From config
        
        try:
            # Desktop metrics
            desktop_api = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
            desktop_params = {
                'url': url,
                'key': api_key,
                'category': 'performance',
                'strategy': 'desktop'
            }
            
            desktop_response = requests.get(desktop_api, params=desktop_params, timeout=30)
            
            # Mobile metrics
            mobile_params = desktop_params.copy()
            mobile_params['strategy'] = 'mobile'
            mobile_response = requests.get(desktop_api, params=mobile_params, timeout=30)
            
            metrics = {}
            
            if desktop_response.status_code == 200:
                desktop_data = desktop_response.json()
                metrics['page_speed_score'] = desktop_data.get('lighthouseResult', {}).get('categories', {}).get('performance', {}).get('score', 0) * 100
            
            if mobile_response.status_code == 200:
                mobile_data = mobile_response.json()
                metrics['mobile_speed_score'] = mobile_data.get('lighthouseResult', {}).get('categories', {}).get('performance', {}).get('score', 0) * 100
            
            # Calculate SEO score based on technical metrics
            metrics['seo_score'] = self.calculate_seo_score(url)
            
            time.sleep(1)  # Rate limiting
            return metrics
            
        except Exception as e:
            print(f"⚠️ PageSpeed error for {domain}: {e}")
            return {
                'page_speed_score': 0,
                'mobile_speed_score': 0,
                'seo_score': 0
            }
    
    def calculate_seo_score(self, url: str) -> float:
        """Calculate basic SEO score based on website analysis"""
        try:
            response = requests.get(url, timeout=10)
            html = response.text.lower()
            
            score = 0
            max_score = 100
            
            # Title tag (20 points)
            if '<title>' in html and len(re.findall(r'<title>([^<]+)', html)) > 0:
                title = re.findall(r'<title>([^<]+)', html)[0]
                if 30 <= len(title) <= 60:
                    score += 20
                elif len(title) > 0:
                    score += 10
            
            # Meta description (20 points)
            if 'meta name="description"' in html:
                desc_match = re.search(r'meta name="description" content="([^"]+)"', html)
                if desc_match and 120 <= len(desc_match.group(1)) <= 160:
                    score += 20
                elif desc_match:
                    score += 10
            
            # H1 tags (15 points)
            h1_count = len(re.findall(r'<h1[^>]*>', html))
            if h1_count == 1:
                score += 15
            elif h1_count > 0:
                score += 8
            
            # SSL (15 points)
            if url.startswith('https://'):
                score += 15
            
            # Mobile responsive (15 points)
            if 'viewport' in html:
                score += 15
            
            # Schema markup (15 points)
            if 'schema.org' in html or 'application/ld+json' in html:
                score += 15
            
            return min(score, max_score)
            
        except:
            return 0
    
    def get_website_technologies(self, domain: str) -> str:
        """Detect website technologies (simplified)"""
        try:
            url = f"https://{self.clean_domain(domain)}"
            response = requests.get(url, timeout=10)
            html = response.text.lower()
            headers = {k.lower(): v.lower() for k, v in response.headers.items()}
            
            technologies = []
            
            # CMS Detection
            if 'wordpress' in html or 'wp-content' in html:
                technologies.append('WordPress')
            elif 'shopify' in html or 'shopify' in headers.get('server', ''):
                technologies.append('Shopify')
            elif 'squarespace' in html:
                technologies.append('Squarespace')
            elif 'wix' in html:
                technologies.append('Wix')
            
            # Analytics
            if 'google-analytics' in html or 'gtag' in html:
                technologies.append('Google Analytics')
            
            # Marketing tools
            if 'hubspot' in html:
                technologies.append('HubSpot')
            elif 'salesforce' in html:
                technologies.append('Salesforce')
            
            # Payment processing
            if 'stripe' in html:
                technologies.append('Stripe')
            elif 'paypal' in html:
                technologies.append('PayPal')
            
            return ', '.join(technologies) if technologies else 'Unknown'
            
        except:
            return 'Unknown'
    
    def estimate_business_metrics(self, prospect: Dict) -> Dict:
        """Estimate advanced business metrics"""
        business_type = prospect.get('business_type', '').lower()
        current_revenue = prospect.get('estimated_monthly_revenue', 0)
        employees = prospect.get('estimated_employees', 0)
        
        benchmark = self.industry_benchmarks.get(business_type, {})
        
        # Business stability score (0-100)
        stability_factors = []
        
        # Revenue vs industry benchmark
        if benchmark.get('avg_monthly_revenue'):
            revenue_ratio = current_revenue / benchmark['avg_monthly_revenue']
            stability_factors.append(min(revenue_ratio * 50, 80))
        
        # Employee count stability
        if employees >= 3:
            stability_factors.append(70)
        elif employees >= 1:
            stability_factors.append(50)
        else:
            stability_factors.append(20)
        
        stability_score = sum(stability_factors) / len(stability_factors) if stability_factors else 50
        
        # Payment capability score
        payment_score = min(stability_score * 1.2, 100)
        
        # Growth potential score
        growth_factors = []
        if business_type in ['dental', 'medical', 'beauty']:
            growth_factors.append(75)  # Recurring revenue models
        elif business_type in ['legal', 'accounting']:
            growth_factors.append(65)  # Professional services
        else:
            growth_factors.append(55)
        
        # Market opportunity based on location
        market_region = prospect.get('market_region', '')
        if any(city in market_region.lower() for city in ['vancouver', 'toronto', 'seattle']):
            growth_factors.append(80)  # Major markets
        else:
            growth_factors.append(60)
        
        growth_score = sum(growth_factors) / len(growth_factors)
        
        return {
            'estimated_annual_revenue': current_revenue * 12,
            'employee_count_estimate': employees,
            'business_stability_score': round(stability_score, 1),
            'payment_capability_score': round(payment_score, 1),
            'growth_potential_score': round(growth_score, 1),
            'market_opportunity_score': round((stability_score + growth_score) / 2, 1)
        }
    
    def generate_competitive_analysis(self, prospect: Dict) -> str:
        """Generate competitive landscape analysis"""
        business_type = prospect.get('business_type', '').lower()
        market_region = prospect.get('market_region', '')
        
        # Competitive density by market and type
        competitive_factors = {
            'dental': {
                'Vancouver, BC': 'High',
                'Toronto, ON': 'Very High', 
                'Seattle, WA': 'High',
                'Calgary, AB': 'Medium'
            },
            'medical': {
                'Vancouver, BC': 'Very High',
                'Toronto, ON': 'Extremely High',
                'Seattle, WA': 'High',
                'Calgary, AB': 'Medium'
            },
            'legal': {
                'Vancouver, BC': 'High',
                'Toronto, ON': 'Very High',
                'Seattle, WA': 'High',
                'Calgary, AB': 'Medium'
            }
        }
        
        density = competitive_factors.get(business_type, {}).get(market_region, 'Medium')
        
        analysis = f"Market: {market_region} | Competitive Density: {density} | "
        
        if business_type == 'dental':
            analysis += "Growing demand for cosmetic/specialty services. Digital booking increasingly important."
        elif business_type == 'medical':
            analysis += "Telehealth integration opportunity. Patient experience differentiation key."
        elif business_type == 'legal':
            analysis += "Digital transformation lagging. Online presence critical for client acquisition."
        elif business_type == 'accounting':
            analysis += "Cloud-based services standard. Tax season surge opportunity."
        else:
            analysis += "Digital marketing optimization opportunities identified."
        
        return analysis
    
    def estimate_contact_intelligence(self, domain: str, company_name: str) -> Dict:
        """Estimate contact information (simplified approach)"""
        clean_domain = self.clean_domain(domain)
        
        # Common email patterns
        common_patterns = [
            'info@', 'contact@', 'hello@', 'admin@',
            'office@', 'reception@', 'appointments@'
        ]
        
        estimated_emails = [f"{pattern}{clean_domain}" for pattern in common_patterns]
        
        # Social media presence estimation
        social_platforms = []
        if any(term in company_name.lower() for term in ['dental', 'clinic', 'medical']):
            social_platforms = ['Facebook', 'Google My Business']
        elif 'law' in company_name.lower() or 'legal' in company_name.lower():
            social_platforms = ['LinkedIn', 'Google My Business']
        else:
            social_platforms = ['Facebook', 'LinkedIn']
        
        return {
            'decision_maker_emails': ', '.join(estimated_emails[:3]),
            'phone_numbers': 'Requires phone verification',
            'social_media_presence': ', '.join(social_platforms)
        }
    
    def enrich_prospect(self, prospect: Dict) -> Dict:
        """Enrich single prospect with BigQuery data"""
        domain = prospect.get('domain', '')
        company_name = prospect.get('company_name', '')
        
        print(f"🔍 Enriching: {company_name[:50]}...")
        
        enrichment = {
            'domain': self.clean_domain(domain),
            'company_name': company_name,
            'enrichment_date': datetime.now().isoformat()
        }
        
        # Website metrics
        print(f"  📊 Analyzing website performance...")
        website_metrics = self.get_pagespeed_metrics(domain)
        enrichment.update(website_metrics)
        
        # Website technologies
        print(f"  🔧 Detecting technologies...")
        enrichment['website_technologies'] = self.get_website_technologies(domain)
        
        # Business intelligence
        print(f"  💼 Calculating business metrics...")
        business_metrics = self.estimate_business_metrics(prospect)
        enrichment.update(business_metrics)
        
        # Competitive analysis
        print(f"  🏆 Generating competitive analysis...")
        enrichment['competitive_landscape'] = self.generate_competitive_analysis(prospect)
        
        # Contact intelligence
        print(f"  📧 Estimating contact info...")
        contact_info = self.estimate_contact_intelligence(domain, company_name)
        enrichment.update(contact_info)
        
        # Digital maturity score (composite)
        digital_score = (
            enrichment.get('page_speed_score', 0) * 0.3 +
            enrichment.get('seo_score', 0) * 0.4 +
            (50 if enrichment.get('website_technologies', 'Unknown') != 'Unknown' else 20) * 0.3
        )
        enrichment['digital_maturity_score'] = round(digital_score, 1)
        
        print(f"  ✅ Enrichment complete")
        return enrichment
    
    def save_to_bigquery(self, enrichments: List[Dict]):
        """Save enrichment data to BigQuery"""
        if not enrichments:
            return
        
        table_id = f"{self.project_id}.{self.dataset_id}.prospect_enrichment"
        
        # Convert to DataFrame for easier handling
        df = pd.DataFrame(enrichments)
        
        # Ensure proper data types
        float_columns = [
            'page_speed_score', 'mobile_speed_score', 'seo_score',
            'estimated_annual_revenue', 'market_opportunity_score',
            'digital_maturity_score', 'business_stability_score',
            'payment_capability_score', 'growth_potential_score'
        ]
        
        for col in float_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
        
        if 'employee_count_estimate' in df.columns:
            df['employee_count_estimate'] = pd.to_numeric(df['employee_count_estimate'], errors='coerce').fillna(0)
        
        # Upload to BigQuery
        job_config = bigquery.LoadJobConfig()
        job_config.write_disposition = "WRITE_TRUNCATE"  # Replace existing data
        
        job = self.client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()  # Wait for completion
        
        print(f"✅ Saved {len(enrichments)} enrichments to BigQuery")
    
    def enrich_prospects_from_csv(self, csv_path: str, max_prospects: int = 50) -> str:
        """Enrich prospects from CSV file"""
        
        print(f"🚀 BIGQUERY ENRICHMENT STARTING...")
        print(f"📁 Source: {csv_path}")
        print(f"🎯 Max prospects: {max_prospects}")
        
        # Setup BigQuery
        self.setup_bigquery_tables()
        
        # Load prospects from CSV
        df = pd.read_csv(csv_path)
        prospects = df.head(max_prospects).to_dict('records')
        
        print(f"📊 Loaded {len(prospects)} prospects for enrichment")
        
        # Enrich each prospect
        enrichments = []
        
        for i, prospect in enumerate(prospects, 1):
            print(f"\n📍 Progress: {i}/{len(prospects)}")
            
            try:
                enrichment = self.enrich_prospect(prospect)
                enrichments.append(enrichment)
                
                # Save periodically to avoid data loss
                if i % 10 == 0:
                    print(f"💾 Saving batch to BigQuery...")
                    self.save_to_bigquery(enrichments[-10:])
                
            except Exception as e:
                print(f"❌ Error enriching {prospect.get('company_name', 'Unknown')}: {e}")
                continue
            
            # Rate limiting
            time.sleep(2)
        
        # Final save
        if enrichments:
            print(f"\n💾 Final save to BigQuery...")
            self.save_to_bigquery(enrichments)
        
        # Generate enriched CSV
        enriched_csv_path = self.generate_enriched_csv(csv_path, enrichments)
        
        print(f"\n✅ ENRICHMENT COMPLETE!")
        print(f"📊 Enriched: {len(enrichments)} prospects")
        print(f"📁 Enhanced CSV: {enriched_csv_path}")
        
        return enriched_csv_path
    
    def generate_enriched_csv(self, original_csv_path: str, enrichments: List[Dict]) -> str:
        """Generate new CSV with enrichment data"""
        
        # Load original CSV
        df_original = pd.read_csv(original_csv_path)
        
        # Create enrichment DataFrame
        df_enrichment = pd.DataFrame(enrichments)
        
        # Merge on cleaned domain
        df_original['domain_clean'] = df_original['domain'].apply(self.clean_domain)
        df_enriched = df_original.merge(
            df_enrichment, 
            left_on='domain_clean', 
            right_on='domain',
            how='left',
            suffixes=('', '_enriched')
        )
        
        # Add enrichment columns
        enrichment_columns = [
            'page_speed_score', 'mobile_speed_score', 'seo_score',
            'website_technologies', 'estimated_annual_revenue',
            'business_stability_score', 'payment_capability_score',
            'growth_potential_score', 'market_opportunity_score',
            'digital_maturity_score', 'competitive_landscape',
            'decision_maker_emails', 'social_media_presence'
        ]
        
        # Fill missing enrichment data
        for col in enrichment_columns:
            if col not in df_enriched.columns:
                df_enriched[col] = 'Not Available'
        
        # Update BigQuery status
        df_enriched['bigquery_enrichment_status'] = df_enriched.apply(
            lambda row: 'completed' if pd.notna(row.get('page_speed_score')) else 'pending',
            axis=1
        )
        df_enriched['bigquery_last_update'] = datetime.now().isoformat()
        
        # Generate output path
        original_path = Path(original_csv_path)
        enriched_path = original_path.parent / f"enriched_{original_path.stem}_{self.timestamp}.csv"
        
        # Clean up temporary columns
        df_enriched = df_enriched.drop(['domain_clean', 'domain_enriched'], axis=1, errors='ignore')
        
        # Save enriched CSV
        df_enriched.to_csv(enriched_path, index=False)
        
        return str(enriched_path)

def main():
    """Execute BigQuery enrichment"""
    
    # Most recent CSV file
    csv_path = "exports/crm/all_qualified_leads_north_america_west_20250730_154915.csv"
    
    enricher = BigQueryEnricher()
    
    # Enrich prospects (limit to 25 for testing)
    enriched_csv = enricher.enrich_prospects_from_csv(csv_path, max_prospects=25)
    
    print(f"\n🎯 ENRICHMENT SUMMARY:")
    print(f"📁 Original: {csv_path}")
    print(f"📁 Enriched: {enriched_csv}")
    print(f"🔍 BigQuery Project: prospection-463116")
    print(f"📊 Dataset: prospect_intelligence")

if __name__ == "__main__":
    main()
