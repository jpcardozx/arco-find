"""
📊 BIGQUERY QUERIES - GOOGLE ADS TRANSPARENCY CENTER + ANALYTICS CROSS-REFERENCE
Queries estratégicas para identificar leads altamente qualificados usando transparência publicitária
"""

import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from google.cloud import bigquery
import logging

class TransparencyAnalyticsBigQueryEngine:
    """
    Engine BigQuery especializado em cruzar dados de transparência publicitária
    com analytics para identificar leads ultra-qualificados
    """
    
    def __init__(self, project_id: str = "prospection-463116"):
        self.client = bigquery.Client(project=project_id)
        self.project_id = project_id
        self.logger = logging.getLogger(__name__)
        
        # Dataset for transparency + analytics intelligence
        self.dataset_id = "arco_transparency_intelligence"
        self.ensure_transparency_dataset()
    
    def ensure_transparency_dataset(self):
        """Ensure transparency intelligence dataset exists"""
        dataset_ref = f"{self.project_id}.{self.dataset_id}"
        
        try:
            self.client.get_dataset(dataset_ref)
            self.logger.info(f"✅ Transparency dataset {dataset_ref} exists")
        except Exception:
            # Create dataset
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"
            dataset.description = "Google Ads Transparency Center + Analytics Cross-Reference Intelligence"
            
            self.client.create_dataset(dataset)
            self.logger.info(f"🎯 Created transparency intelligence dataset: {dataset_ref}")
    
    def create_transparency_analytics_tables(self):
        """Create specialized tables for transparency + analytics intelligence"""
        
        tables_schema = {
            'ads_transparency_data': [
                bigquery.SchemaField('advertiser_id', 'STRING', mode='REQUIRED'),
                bigquery.SchemaField('advertiser_name', 'STRING', mode='REQUIRED'),
                bigquery.SchemaField('domain', 'STRING', mode='REQUIRED'),
                bigquery.SchemaField('industry_vertical', 'STRING', mode='REQUIRED'),
                bigquery.SchemaField('geographic_scope', 'STRING', mode='REPEATED'),
                bigquery.SchemaField('campaign_types', 'STRING', mode='REPEATED'),
                bigquery.SchemaField('keyword_categories', 'STRING', mode='REPEATED'),
                bigquery.SchemaField('spend_volume_tier', 'STRING', mode='NULLABLE'),
                bigquery.SchemaField('targeting_intelligence', 'JSON', mode='NULLABLE'),
                bigquery.SchemaField('discovery_timestamp', 'TIMESTAMP', mode='REQUIRED'),
                bigquery.SchemaField('last_seen_advertising', 'TIMESTAMP', mode='NULLABLE')
            ],
            
            'analytics_performance_signals': [
                bigquery.SchemaField('domain', 'STRING', mode='REQUIRED'),
                bigquery.SchemaField('monthly_visitors', 'INTEGER', mode='NULLABLE'),
                bigquery.SchemaField('traffic_sources', 'JSON', mode='NULLABLE'),
                bigquery.SchemaField('bounce_rate', 'FLOAT', mode='NULLABLE'),
                bigquery.SchemaField('avg_session_duration', 'INTEGER', mode='NULLABLE'),
                bigquery.SchemaField('conversion_rate', 'FLOAT', mode='NULLABLE'),
                bigquery.SchemaField('core_web_vitals', 'JSON', mode='NULLABLE'),
                bigquery.SchemaField('mobile_performance', 'JSON', mode='NULLABLE'),
                bigquery.SchemaField('conversion_tracking_quality', 'FLOAT', mode='NULLABLE'),
                bigquery.SchemaField('attribution_accuracy', 'FLOAT', mode='NULLABLE'),
                bigquery.SchemaField('analysis_timestamp', 'TIMESTAMP', mode='REQUIRED')
            ],
            
            'competitive_intelligence': [
                bigquery.SchemaField('domain', 'STRING', mode='REQUIRED'),
                bigquery.SchemaField('branded_keyword_defense', 'FLOAT', mode='NULLABLE'),
                bigquery.SchemaField('competitor_keyword_overlap', 'FLOAT', mode='NULLABLE'),
                bigquery.SchemaField('market_share_estimate', 'FLOAT', mode='NULLABLE'),
                bigquery.SchemaField('cost_efficiency_vs_competitors', 'FLOAT', mode='NULLABLE'),
                bigquery.SchemaField('message_uniqueness_score', 'FLOAT', mode='NULLABLE'),
                bigquery.SchemaField('competitive_vulnerabilities', 'STRING', mode='REPEATED'),
                bigquery.SchemaField('analysis_timestamp', 'TIMESTAMP', mode='REQUIRED')
            ],
            
            'qualified_transparency_leads': [
                bigquery.SchemaField('lead_id', 'STRING', mode='REQUIRED'),
                bigquery.SchemaField('company_name', 'STRING', mode='REQUIRED'),
                bigquery.SchemaField('domain', 'STRING', mode='REQUIRED'),
                bigquery.SchemaField('advertiser_id', 'STRING', mode='REQUIRED'),
                bigquery.SchemaField('qualification_score', 'FLOAT', mode='REQUIRED'),
                bigquery.SchemaField('urgency_indicators', 'STRING', mode='REPEATED'),
                bigquery.SchemaField('estimated_monthly_ad_spend', 'FLOAT', mode='NULLABLE'),
                bigquery.SchemaField('estimated_monthly_waste', 'FLOAT', mode='NULLABLE'),
                bigquery.SchemaField('primary_issues', 'STRING', mode='REPEATED'),
                bigquery.SchemaField('discovery_method', 'STRING', mode='REQUIRED'),
                bigquery.SchemaField('discovery_timestamp', 'TIMESTAMP', mode='REQUIRED'),
                bigquery.SchemaField('last_updated', 'TIMESTAMP', mode='REQUIRED')
            ]
        }
        
        for table_name, schema in tables_schema.items():
            table_ref = f"{self.project_id}.{self.dataset_id}.{table_name}"
            
            try:
                self.client.get_table(table_ref)
                self.logger.info(f"✅ Table {table_name} exists")
            except Exception:
                table = bigquery.Table(table_ref, schema=schema)
                self.client.create_table(table)
                self.logger.info(f"🎯 Created table: {table_name}")
    
    def insert_transparency_data(self, transparency_leads: List[Dict]) -> bool:
        """Insert transparency center data"""
        
        ads_transparency_rows = []
        analytics_performance_rows = []
        competitive_intelligence_rows = []
        qualified_leads_rows = []
        
        for lead in transparency_leads:
            # Extract and structure data for different tables
            
            # Ads transparency data
            ads_transparency_rows.append({
                'advertiser_id': lead['advertiser_id'],
                'advertiser_name': lead['company_name'],
                'domain': lead['domain'],
                'industry_vertical': self._extract_industry(lead['company_name'], lead['domain']),
                'geographic_scope': lead.get('transparency_data', {}).get('spend_indicators', {}).get('geographic_scope', []),
                'campaign_types': lead.get('transparency_data', {}).get('spend_indicators', {}).get('campaign_types', []),
                'keyword_categories': lead.get('transparency_data', {}).get('spend_indicators', {}).get('keyword_categories', []),
                'spend_volume_tier': lead.get('current_ad_spend_signals', {}).get('volume_tier', 'unknown'),
                'targeting_intelligence': json.dumps(lead.get('transparency_data', {}).get('targeting_intelligence', {})),
                'discovery_timestamp': datetime.utcnow(),
                'last_seen_advertising': datetime.utcnow()
            })
            
            # Analytics performance signals
            analytics_signals = lead.get('analytics_signals', {})
            traffic_analysis = analytics_signals.get('traffic_analysis', {})
            technical_performance = analytics_signals.get('technical_performance', {})
            conversion_signals = analytics_signals.get('conversion_signals', {})
            
            analytics_performance_rows.append({
                'domain': lead['domain'],
                'monthly_visitors': traffic_analysis.get('monthly_visitors'),
                'traffic_sources': json.dumps(traffic_analysis.get('traffic_sources', {})),
                'bounce_rate': traffic_analysis.get('bounce_rate_estimate'),
                'avg_session_duration': traffic_analysis.get('avg_session_duration'),
                'conversion_rate': traffic_analysis.get('conversion_rate_estimate'),
                'core_web_vitals': json.dumps(technical_performance.get('core_web_vitals', {})),
                'mobile_performance': json.dumps(technical_performance.get('mobile_performance', {})),
                'conversion_tracking_quality': self._calculate_tracking_quality(conversion_signals),
                'attribution_accuracy': conversion_signals.get('attribution_problems', {}).get('tracking_accuracy'),
                'analysis_timestamp': datetime.utcnow()
            })
            
            # Competitive intelligence
            competitive_analysis = analytics_signals.get('competitive_analysis', {})
            keyword_competition = competitive_analysis.get('keyword_competition', {})
            ad_creative_analysis = competitive_analysis.get('ad_creative_analysis', {})
            
            competitive_intelligence_rows.append({
                'domain': lead['domain'],
                'branded_keyword_defense': keyword_competition.get('branded_keyword_defense'),
                'competitor_keyword_overlap': keyword_competition.get('competitor_keyword_overlap'),
                'market_share_estimate': keyword_competition.get('market_share_estimate'),
                'cost_efficiency_vs_competitors': keyword_competition.get('cost_efficiency_vs_competitors'),
                'message_uniqueness_score': ad_creative_analysis.get('message_uniqueness_score'),
                'competitive_vulnerabilities': competitive_analysis.get('market_opportunity_signals', []),
                'analysis_timestamp': datetime.utcnow()
            })
            
            # Qualified leads summary
            qualified_leads_rows.append({
                'lead_id': f"TRANS_{lead['advertiser_id']}_{int(datetime.utcnow().timestamp())}",
                'company_name': lead['company_name'],
                'domain': lead['domain'],
                'advertiser_id': lead['advertiser_id'],
                'qualification_score': lead['qualification_score'],
                'urgency_indicators': lead.get('urgency_indicators', []),
                'estimated_monthly_ad_spend': self._estimate_monthly_spend(lead.get('current_ad_spend_signals', {})),
                'estimated_monthly_waste': self._calculate_monthly_waste(analytics_signals),
                'primary_issues': self._extract_primary_issues(analytics_signals),
                'discovery_method': 'TRANSPARENCY_CENTER_ANALYTICS_CROSS_REFERENCE',
                'discovery_timestamp': datetime.utcnow(),
                'last_updated': datetime.utcnow()
            })
        
        # Insert data into tables
        success = True
        
        try:
            # Insert ads transparency data
            table_ref = f"{self.project_id}.{self.dataset_id}.ads_transparency_data"
            errors = self.client.insert_rows_json(table_ref, ads_transparency_rows)
            if errors:
                self.logger.error(f"❌ Errors inserting transparency data: {errors}")
                success = False
            
            # Insert analytics performance data
            table_ref = f"{self.project_id}.{self.dataset_id}.analytics_performance_signals"
            errors = self.client.insert_rows_json(table_ref, analytics_performance_rows)
            if errors:
                self.logger.error(f"❌ Errors inserting analytics data: {errors}")
                success = False
            
            # Insert competitive intelligence
            table_ref = f"{self.project_id}.{self.dataset_id}.competitive_intelligence"
            errors = self.client.insert_rows_json(table_ref, competitive_intelligence_rows)
            if errors:
                self.logger.error(f"❌ Errors inserting competitive data: {errors}")
                success = False
            
            # Insert qualified leads
            table_ref = f"{self.project_id}.{self.dataset_id}.qualified_transparency_leads"
            errors = self.client.insert_rows_json(table_ref, qualified_leads_rows)
            if errors:
                self.logger.error(f"❌ Errors inserting qualified leads: {errors}")
                success = False
            
            if success:
                self.logger.info(f"✅ Successfully inserted {len(transparency_leads)} transparency leads into BigQuery")
        
        except Exception as e:
            self.logger.error(f"❌ Error inserting transparency data: {e}")
            success = False
        
        return success
    
    def query_high_value_transparency_leads(self, min_qualification_score: float = 0.7,
                                          min_monthly_waste: float = 2000) -> List[Dict]:
        """
        Query para leads de alto valor descobertos via transparency center + analytics
        """
        
        query = f"""
        WITH transparency_analytics_combined AS (
            SELECT 
                qtl.lead_id,
                qtl.company_name,
                qtl.domain,
                qtl.advertiser_id,
                qtl.qualification_score,
                qtl.urgency_indicators,
                qtl.estimated_monthly_ad_spend,
                qtl.estimated_monthly_waste,
                qtl.primary_issues,
                
                -- Ads transparency data
                atd.industry_vertical,
                atd.geographic_scope,
                atd.campaign_types,
                atd.keyword_categories,
                atd.spend_volume_tier,
                
                -- Analytics performance
                aps.monthly_visitors,
                aps.bounce_rate,
                aps.conversion_rate,
                JSON_EXTRACT_SCALAR(aps.core_web_vitals, '$.overall_score') as cwv_score,
                JSON_EXTRACT_SCALAR(aps.mobile_performance, '$.mobile_speed_score') as mobile_score,
                aps.attribution_accuracy,
                
                -- Competitive intelligence
                ci.branded_keyword_defense,
                ci.competitor_keyword_overlap,
                ci.market_share_estimate,
                ci.message_uniqueness_score,
                ci.competitive_vulnerabilities,
                
                qtl.discovery_timestamp,
                qtl.last_updated
            
            FROM `{self.project_id}.{self.dataset_id}.qualified_transparency_leads` qtl
            
            LEFT JOIN `{self.project_id}.{self.dataset_id}.ads_transparency_data` atd
                ON qtl.domain = atd.domain
                
            LEFT JOIN `{self.project_id}.{self.dataset_id}.analytics_performance_signals` aps
                ON qtl.domain = aps.domain
                
            LEFT JOIN `{self.project_id}.{self.dataset_id}.competitive_intelligence` ci
                ON qtl.domain = ci.domain
            
            WHERE qtl.qualification_score >= {min_qualification_score}
                AND qtl.estimated_monthly_waste >= {min_monthly_waste}
                AND qtl.discovery_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
        ),
        
        urgency_scoring AS (
            SELECT *,
                CASE 
                    WHEN 'CRITICAL_CORE_WEB_VITALS' IN UNNEST(urgency_indicators) THEN 3
                    WHEN 'ATTRIBUTION_CRISIS' IN UNNEST(urgency_indicators) THEN 3
                    WHEN 'AD_SPEND_WASTE' IN UNNEST(urgency_indicators) THEN 2
                    WHEN 'BRAND_VULNERABILITY' IN UNNEST(urgency_indicators) THEN 2
                    ELSE 1
                END as urgency_score,
                
                CASE
                    WHEN spend_volume_tier = 'high' THEN 3
                    WHEN spend_volume_tier = 'medium' THEN 2
                    ELSE 1
                END as spend_tier_score,
                
                CASE
                    WHEN CAST(cwv_score AS FLOAT64) < 30 THEN 3
                    WHEN CAST(cwv_score AS FLOAT64) < 50 THEN 2
                    ELSE 1
                END as technical_urgency_score
                
            FROM transparency_analytics_combined
        ),
        
        final_prioritization AS (
            SELECT *,
                (urgency_score + spend_tier_score + technical_urgency_score) as total_priority_score,
                
                -- Calculate ROI potential
                CASE 
                    WHEN estimated_monthly_waste > 10000 AND qualification_score > 0.8 THEN 'ULTRA_HIGH_ROI'
                    WHEN estimated_monthly_waste > 5000 AND qualification_score > 0.7 THEN 'HIGH_ROI'
                    WHEN estimated_monthly_waste > 2000 AND qualification_score > 0.6 THEN 'MEDIUM_ROI'
                    ELSE 'STANDARD_ROI'
                END as roi_category,
                
                -- Extract key pain points for outreach
                CASE
                    WHEN attribution_accuracy < 0.5 THEN 'Attribution tracking crisis'
                    WHEN bounce_rate > 0.7 THEN 'User experience problems'
                    WHEN CAST(cwv_score AS FLOAT64) < 30 THEN 'Critical performance issues'
                    WHEN branded_keyword_defense < 0.4 THEN 'Brand vulnerability'
                    ELSE 'Conversion optimization opportunity'
                END as primary_pain_point
                
            FROM urgency_scoring
        )
        
        SELECT 
            lead_id,
            company_name,
            domain,
            advertiser_id,
            qualification_score,
            total_priority_score,
            roi_category,
            primary_pain_point,
            estimated_monthly_ad_spend,
            estimated_monthly_waste,
            industry_vertical,
            spend_volume_tier,
            urgency_indicators,
            primary_issues,
            
            -- Key metrics for outreach
            monthly_visitors,
            bounce_rate,
            conversion_rate,
            cwv_score,
            mobile_score,
            attribution_accuracy,
            branded_keyword_defense,
            
            -- Discovery metadata
            discovery_timestamp,
            last_updated
            
        FROM final_prioritization
        ORDER BY total_priority_score DESC, estimated_monthly_waste DESC
        LIMIT 50
        """
        
        try:
            self.logger.info("🎯 Executing high-value transparency leads query...")
            
            query_job = self.client.query(query)
            results = query_job.result()
            
            leads = []
            for row in results:
                lead_data = dict(row)
                
                # Convert timestamps to ISO format
                if lead_data.get('discovery_timestamp'):
                    lead_data['discovery_timestamp'] = lead_data['discovery_timestamp'].isoformat()
                if lead_data.get('last_updated'):
                    lead_data['last_updated'] = lead_data['last_updated'].isoformat()
                
                leads.append(lead_data)
            
            self.logger.info(f"✅ Found {len(leads)} high-value transparency leads")
            return leads
            
        except Exception as e:
            self.logger.error(f"❌ Error querying transparency leads: {e}")
            return []
    
    def query_industry_transparency_analysis(self, industry: str = None) -> Dict:
        """
        Análise de transparência por indústria
        """
        
        industry_filter = f"WHERE industry_vertical = '{industry}'" if industry else ""
        
        query = f"""
        WITH industry_transparency_metrics AS (
            SELECT 
                atd.industry_vertical,
                COUNT(DISTINCT qtl.lead_id) as total_leads,
                AVG(qtl.qualification_score) as avg_qualification_score,
                SUM(qtl.estimated_monthly_waste) as total_monthly_waste_opportunity,
                AVG(qtl.estimated_monthly_ad_spend) as avg_monthly_ad_spend,
                
                -- Transparency patterns
                COUNTIF(atd.spend_volume_tier = 'high') as high_spend_advertisers,
                COUNTIF(atd.spend_volume_tier = 'medium') as medium_spend_advertisers,
                COUNTIF(atd.spend_volume_tier = 'low') as low_spend_advertisers,
                
                -- Performance patterns
                AVG(aps.bounce_rate) as avg_bounce_rate,
                AVG(aps.conversion_rate) as avg_conversion_rate,
                AVG(CAST(JSON_EXTRACT_SCALAR(aps.core_web_vitals, '$.overall_score') AS FLOAT64)) as avg_cwv_score,
                AVG(aps.attribution_accuracy) as avg_attribution_accuracy,
                
                -- Competitive patterns
                AVG(ci.branded_keyword_defense) as avg_branded_defense,
                AVG(ci.market_share_estimate) as avg_market_share,
                AVG(ci.message_uniqueness_score) as avg_message_uniqueness,
                
                -- Urgency distribution
                COUNTIF('CRITICAL_CORE_WEB_VITALS' IN UNNEST(qtl.urgency_indicators)) as critical_performance_count,
                COUNTIF('ATTRIBUTION_CRISIS' IN UNNEST(qtl.urgency_indicators)) as attribution_crisis_count,
                COUNTIF('AD_SPEND_WASTE' IN UNNEST(qtl.urgency_indicators)) as ad_waste_count,
                COUNTIF('BRAND_VULNERABILITY' IN UNNEST(qtl.urgency_indicators)) as brand_vulnerability_count
                
            FROM `{self.project_id}.{self.dataset_id}.qualified_transparency_leads` qtl
            
            LEFT JOIN `{self.project_id}.{self.dataset_id}.ads_transparency_data` atd
                ON qtl.domain = atd.domain
                
            LEFT JOIN `{self.project_id}.{self.dataset_id}.analytics_performance_signals` aps
                ON qtl.domain = aps.domain
                
            LEFT JOIN `{self.project_id}.{self.dataset_id}.competitive_intelligence` ci
                ON qtl.domain = ci.domain
            
            {industry_filter}
            GROUP BY atd.industry_vertical
        ),
        
        industry_rankings AS (
            SELECT *,
                RANK() OVER (ORDER BY total_monthly_waste_opportunity DESC) as waste_opportunity_rank,
                RANK() OVER (ORDER BY avg_qualification_score DESC) as qualification_rank,
                RANK() OVER (ORDER BY total_leads DESC) as volume_rank
            FROM industry_transparency_metrics
        )
        
        SELECT * FROM industry_rankings
        ORDER BY total_monthly_waste_opportunity DESC
        """
        
        try:
            self.logger.info(f"🎯 Analyzing transparency data by industry: {industry or 'ALL'}")
            
            query_job = self.client.query(query)
            results = query_job.result()
            
            analysis = {}
            for row in results:
                industry_data = dict(row)
                industry_name = industry_data['industry_vertical']
                analysis[industry_name] = industry_data
            
            self.logger.info(f"✅ Completed industry transparency analysis for {len(analysis)} industries")
            return analysis
            
        except Exception as e:
            self.logger.error(f"❌ Error in industry transparency analysis: {e}")
            return {}
    
    def query_competitive_vulnerability_opportunities(self) -> List[Dict]:
        """
        Query para oportunidades baseadas em vulnerabilidades competitivas
        """
        
        query = f"""
        WITH competitive_vulnerabilities AS (
            SELECT 
                qtl.lead_id,
                qtl.company_name,
                qtl.domain,
                qtl.qualification_score,
                qtl.estimated_monthly_waste,
                
                ci.branded_keyword_defense,
                ci.competitor_keyword_overlap,
                ci.market_share_estimate,
                ci.message_uniqueness_score,
                ci.competitive_vulnerabilities,
                
                atd.spend_volume_tier,
                atd.keyword_categories,
                
                aps.conversion_rate,
                JSON_EXTRACT_SCALAR(aps.traffic_sources, '$.paid_search') as paid_dependency,
                
                -- Calculate vulnerability score
                (
                    (1 - COALESCE(ci.branded_keyword_defense, 0.5)) * 0.3 +
                    (1 - COALESCE(ci.message_uniqueness_score, 0.5)) * 0.3 +
                    (COALESCE(ci.competitor_keyword_overlap, 0.5) - 0.5) * 0.2 +
                    (CAST(JSON_EXTRACT_SCALAR(aps.traffic_sources, '$.paid_search') AS FLOAT64) - 0.4) * 0.2
                ) as vulnerability_score
                
            FROM `{self.project_id}.{self.dataset_id}.qualified_transparency_leads` qtl
            
            LEFT JOIN `{self.project_id}.{self.dataset_id}.competitive_intelligence` ci
                ON qtl.domain = ci.domain
                
            LEFT JOIN `{self.project_id}.{self.dataset_id}.ads_transparency_data` atd
                ON qtl.domain = atd.domain
                
            LEFT JOIN `{self.project_id}.{self.dataset_id}.analytics_performance_signals` aps
                ON qtl.domain = aps.domain
                
            WHERE ci.branded_keyword_defense < 0.5  -- Weak brand defense
                OR ci.message_uniqueness_score < 0.4  -- Generic messaging
                OR CAST(JSON_EXTRACT_SCALAR(aps.traffic_sources, '$.paid_search') AS FLOAT64) > 0.6  -- High paid dependency
        ),
        
        vulnerability_insights AS (
            SELECT *,
                CASE
                    WHEN vulnerability_score > 0.7 THEN 'CRITICAL_VULNERABILITY'
                    WHEN vulnerability_score > 0.5 THEN 'HIGH_VULNERABILITY'
                    WHEN vulnerability_score > 0.3 THEN 'MODERATE_VULNERABILITY'
                    ELSE 'LOW_VULNERABILITY'
                END as vulnerability_category,
                
                CASE
                    WHEN branded_keyword_defense < 0.3 THEN 'Brand defense crisis'
                    WHEN message_uniqueness_score < 0.3 THEN 'Generic messaging problem'
                    WHEN CAST(paid_dependency AS FLOAT64) > 0.7 THEN 'Dangerous paid dependency'
                    ELSE 'Multiple competitive weaknesses'
                END as primary_vulnerability
                
            FROM competitive_vulnerabilities
        )
        
        SELECT 
            lead_id,
            company_name,
            domain,
            qualification_score,
            vulnerability_score,
            vulnerability_category,
            primary_vulnerability,
            estimated_monthly_waste,
            spend_volume_tier,
            keyword_categories,
            
            -- Specific vulnerability metrics
            branded_keyword_defense,
            message_uniqueness_score,
            competitor_keyword_overlap,
            paid_dependency,
            conversion_rate,
            
            competitive_vulnerabilities
            
        FROM vulnerability_insights
        WHERE vulnerability_score > 0.3  -- Focus on actionable vulnerabilities
        ORDER BY vulnerability_score DESC, estimated_monthly_waste DESC
        LIMIT 30
        """
        
        try:
            self.logger.info("🎯 Analyzing competitive vulnerability opportunities...")
            
            query_job = self.client.query(query)
            results = query_job.result()
            
            opportunities = []
            for row in results:
                opportunity = dict(row)
                opportunities.append(opportunity)
            
            self.logger.info(f"✅ Found {len(opportunities)} competitive vulnerability opportunities")
            return opportunities
            
        except Exception as e:
            self.logger.error(f"❌ Error analyzing competitive vulnerabilities: {e}")
            return []
    
    # Helper methods
    def _extract_industry(self, company_name: str, domain: str) -> str:
        """Extract industry from company name/domain"""
        text = f"{company_name} {domain}".lower()
        
        if any(term in text for term in ['legal', 'law', 'attorney', 'lawyer']):
            return 'legal'
        elif any(term in text for term in ['auto', 'car', 'vehicle', 'repair', 'collision']):
            return 'automotive'
        elif any(term in text for term in ['medical', 'health', 'doctor', 'clinic']):
            return 'healthcare'
        elif any(term in text for term in ['real estate', 'realtor', 'property']):
            return 'real_estate'
        elif any(term in text for term in ['restaurant', 'food', 'dining']):
            return 'restaurant'
        else:
            return 'other'
    
    def _calculate_tracking_quality(self, conversion_signals: Dict) -> float:
        """Calculate overall tracking quality score"""
        attribution_problems = conversion_signals.get('attribution_problems', {})
        issues_count = len(attribution_problems.get('issues_detected', []))
        
        # Base quality starts at 1.0, decreases with issues
        quality_score = max(0.1, 1.0 - (issues_count * 0.15))
        return quality_score
    
    def _estimate_monthly_spend(self, spend_signals: Dict) -> float:
        """Estimate monthly ad spend"""
        volume_tier = spend_signals.get('volume_tier', 'low')
        
        estimates = {
            'high': 75000,
            'medium': 25000,
            'low': 5000
        }
        
        return estimates.get(volume_tier, 2500)
    
    def _calculate_monthly_waste(self, analytics_signals: Dict) -> float:
        """Calculate estimated monthly waste"""
        traffic = analytics_signals.get('traffic_analysis', {})
        conversion = analytics_signals.get('conversion_signals', {})
        
        monthly_visitors = traffic.get('monthly_visitors', 5000)
        conversion_rate = traffic.get('conversion_rate_estimate', 0.03)
        paid_percentage = traffic.get('traffic_sources', {}).get('paid_search', 0.4)
        
        # Potential improvement estimate
        potential_improvement = 0.5  # 50%
        
        monthly_paid_visitors = monthly_visitors * paid_percentage
        current_conversions = monthly_paid_visitors * conversion_rate
        potential_conversions = monthly_paid_visitors * (conversion_rate * (1 + potential_improvement))
        
        # Estimate waste (avg $200 cost per conversion)
        avg_cost_per_conversion = 200
        monthly_waste = (potential_conversions - current_conversions) * avg_cost_per_conversion
        
        return max(monthly_waste, 500)
    
    def _extract_primary_issues(self, analytics_signals: Dict) -> List[str]:
        """Extract primary issues from analytics"""
        issues = []
        
        # Technical issues
        technical = analytics_signals.get('technical_performance', {})
        cwv_score = technical.get('core_web_vitals', {}).get('overall_score', 50)
        
        if cwv_score < 30:
            issues.append('Critical Core Web Vitals')
        
        # Conversion issues
        conversion = analytics_signals.get('conversion_signals', {})
        tracking_accuracy = conversion.get('attribution_problems', {}).get('tracking_accuracy', 0.5)
        
        if tracking_accuracy < 0.5:
            issues.append('Poor Conversion Tracking')
        
        # Traffic quality
        traffic = analytics_signals.get('traffic_analysis', {})
        bounce_rate = traffic.get('bounce_rate_estimate', 0.5)
        
        if bounce_rate > 0.7:
            issues.append('High Bounce Rate')
        
        return issues
