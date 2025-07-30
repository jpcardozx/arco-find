"""
📊 BIGQUERY INTELLIGENCE - COST-CONTROLLED LEAD INSIGHTS
Strategic BigQuery operations with dry-run cost validation
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from google.cloud import bigquery
from config.api_keys import APIConfig
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class BigQueryIntelligence:
    """Smart BigQuery operations with cost control and dry-run validation"""
    
    def __init__(self):
        self.config = APIConfig()
        self.client = bigquery.Client(project=self.config.GOOGLE_CLOUD_PROJECT)
        
        # Cost control settings
        self.max_daily_cost_usd = 5.0  # $5 daily limit
        self.cost_per_tb_processed = 5.0  # $5 per TB
        self.daily_usage_tracking = {}
        
    async def get_hot_leads_analysis(self) -> Dict:
        """
        Get actionable hot leads analysis with cost optimization
        """
        query = f"""
        -- Hot leads ready for immediate outreach
        WITH recent_qualified AS (
          SELECT 
            company_name,
            website,
            industry,
            qualification_score,
            estimated_monthly_loss,
            urgency_level,
            specific_pain_points,
            last_updated
          FROM `{self.config.GOOGLE_CLOUD_PROJECT}.{self.config.BIGQUERY_DATASET_ID}.qualified_leads`
          WHERE 
            last_updated >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
            AND qualification_score >= 70
        ),
        prioritized_leads AS (
          SELECT *,
            ROW_NUMBER() OVER (
              PARTITION BY urgency_level 
              ORDER BY qualification_score DESC, estimated_monthly_loss DESC
            ) as priority_rank
          FROM recent_qualified
        )
        SELECT 
          urgency_level,
          COUNT(*) as lead_count,
          AVG(qualification_score) as avg_score,
          SUM(estimated_monthly_loss) as total_monthly_opportunity,
          STRING_AGG(
            CASE WHEN priority_rank <= 3 THEN 
              CONCAT(company_name, ' ($', CAST(estimated_monthly_loss AS STRING), '/mo)') 
            END, 
            '; ' LIMIT 3
          ) as top_3_companies
        FROM prioritized_leads
        GROUP BY urgency_level
        ORDER BY 
          CASE urgency_level 
            WHEN 'HOT' THEN 1 
            WHEN 'WARM' THEN 2 
            ELSE 3 
          END
        """
        
        return await self._execute_query_with_cost_control(query, "hot_leads_analysis")
    
    async def get_industry_intelligence(self) -> Dict:
        """
        Get industry-specific intelligence for targeting
        """
        query = f"""
        -- Industry opportunity analysis
        SELECT 
          industry,
          COUNT(*) as total_prospects,
          AVG(qualification_score) as avg_qualification,
          SUM(estimated_monthly_loss) as total_opportunity,
          AVG(monthly_ad_spend) as avg_ad_spend,
          
          -- Performance issues distribution
          ROUND(AVG(CASE WHEN performance_score < 50 THEN 1 ELSE 0 END) * 100, 1) as critical_performance_pct,
          
          -- Urgency distribution
          COUNTIF(urgency_level = 'HOT') as hot_count,
          COUNTIF(urgency_level = 'WARM') as warm_count
          
        FROM `{self.config.GOOGLE_CLOUD_PROJECT}.{self.config.BIGQUERY_DATASET_ID}.qualified_leads`
        WHERE last_updated >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        GROUP BY industry
        HAVING COUNT(*) >= 3  -- Only industries with meaningful data
        ORDER BY total_opportunity DESC
        LIMIT 10
        """
        
        return await self._execute_query_with_cost_control(query, "industry_intelligence")
    
    async def get_conversion_pipeline_health(self) -> Dict:
        """
        Analyze conversion pipeline health and bottlenecks
        """
        query = f"""
        -- Pipeline health analysis
        WITH pipeline_stages AS (
          SELECT 
            DATE(last_updated) as analysis_date,
            COUNT(*) as total_leads,
            COUNTIF(qualification_score >= 80) as hot_leads,
            COUNTIF(qualification_score BETWEEN 60 AND 79) as warm_leads,
            COUNTIF(qualification_score < 60) as cold_leads,
            AVG(qualification_score) as avg_score,
            SUM(estimated_monthly_loss) as total_opportunity
          FROM `{self.config.GOOGLE_CLOUD_PROJECT}.{self.config.BIGQUERY_DATASET_ID}.qualified_leads`
          WHERE last_updated >= DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY)
          GROUP BY DATE(last_updated)
        )
        SELECT 
          analysis_date,
          total_leads,
          hot_leads,
          warm_leads,
          ROUND(hot_leads * 100.0 / NULLIF(total_leads, 0), 1) as hot_lead_percentage,
          ROUND(avg_score, 1) as avg_qualification_score,
          ROUND(total_opportunity, 0) as daily_opportunity_usd
        FROM pipeline_stages
        ORDER BY analysis_date DESC
        LIMIT 14
        """
        
        return await self._execute_query_with_cost_control(query, "pipeline_health")
    
    async def identify_market_gaps(self) -> Dict:
        """
        Identify market gaps and expansion opportunities
        """
        query = f"""
        -- Market gap identification
        WITH market_analysis AS (
          SELECT 
            industry,
            CASE 
              WHEN employee_count BETWEEN 10 AND 25 THEN 'Small (10-25)'
              WHEN employee_count BETWEEN 26 AND 50 THEN 'Medium (26-50)'
              WHEN employee_count BETWEEN 51 AND 100 THEN 'Large (51-100)'
              ELSE 'Other'
            END as company_size_bracket,
            COUNT(*) as prospect_count,
            AVG(qualification_score) as avg_qualification,
            SUM(estimated_monthly_loss) as total_opportunity,
            
            -- Market penetration indicators
            AVG(performance_score) as avg_performance,
            COUNTIF(performance_score < 50) as critical_performance_count
            
          FROM `{self.config.GOOGLE_CLOUD_PROJECT}.{self.config.BIGQUERY_DATASET_ID}.qualified_leads`
          WHERE 
            last_updated >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
            AND qualification_score >= 40  -- Focus on viable prospects
          GROUP BY industry, company_size_bracket
        )
        SELECT 
          industry,
          company_size_bracket,
          prospect_count,
          ROUND(avg_qualification, 1) as avg_qualification_score,
          ROUND(total_opportunity, 0) as market_opportunity_usd,
          ROUND(avg_performance, 1) as avg_performance_score,
          critical_performance_count,
          
          -- Market attractiveness score
          ROUND(
            (avg_qualification * 0.4) + 
            (LEAST(total_opportunity / 1000, 100) * 0.3) + 
            ((100 - avg_performance) * 0.3), 1
          ) as market_attractiveness_score
          
        FROM market_analysis
        WHERE prospect_count >= 2  -- Meaningful sample size
        ORDER BY market_attractiveness_score DESC
        LIMIT 15
        """
        
        return await self._execute_query_with_cost_control(query, "market_gaps")
    
    async def get_performance_benchmark_intelligence(self) -> Dict:
        """
        Performance benchmarking for competitive positioning
        """
        query = f"""
        -- Performance benchmarking intelligence
        WITH performance_benchmarks AS (
          SELECT 
            industry,
            
            -- Performance distribution
            APPROX_QUANTILES(performance_score, 4) as performance_quartiles,
            AVG(performance_score) as avg_performance,
            
            -- Business impact correlation
            CORR(performance_score, qualification_score) as performance_qualification_correlation,
            CORR(performance_score, estimated_monthly_loss) as performance_loss_correlation,
            
            -- Market opportunity
            COUNT(*) as total_prospects,
            COUNTIF(performance_score < 50) as critical_performance_prospects,
            SUM(CASE WHEN performance_score < 50 THEN estimated_monthly_loss ELSE 0 END) as critical_opportunity
            
          FROM `{self.config.GOOGLE_CLOUD_PROJECT}.{self.config.BIGQUERY_DATASET_ID}.qualified_leads`
          WHERE 
            last_updated >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
            AND performance_score > 0  -- Valid performance data
          GROUP BY industry
          HAVING COUNT(*) >= 5  -- Statistical significance
        )
        SELECT 
          industry,
          ROUND(avg_performance, 1) as avg_performance_score,
          performance_quartiles[OFFSET(1)] as bottom_quartile,
          performance_quartiles[OFFSET(2)] as median_performance,
          performance_quartiles[OFFSET(3)] as top_quartile,
          
          total_prospects,
          critical_performance_prospects,
          ROUND(critical_performance_prospects * 100.0 / total_prospects, 1) as critical_performance_rate,
          ROUND(critical_opportunity, 0) as critical_opportunity_usd,
          
          ROUND(performance_qualification_correlation, 3) as perf_qual_correlation,
          ROUND(performance_loss_correlation, 3) as perf_loss_correlation
          
        FROM performance_benchmarks
        ORDER BY critical_opportunity_usd DESC
        """
        
        return await self._execute_query_with_cost_control(query, "performance_benchmarks")
    
    async def _execute_query_with_cost_control(self, query: str, operation_name: str) -> Dict:
        """
        Execute BigQuery with dry-run cost validation and daily limit enforcement
        """
        try:
            # Step 1: Dry run to estimate cost
            dry_run_job = self._create_dry_run_job(query)
            cost_estimate = self._calculate_query_cost(dry_run_job)
            
            logger.info(f"💰 Query cost estimate for {operation_name}: ${cost_estimate:.4f}")
            
            # Step 2: Check daily limits
            today = datetime.now().strftime('%Y-%m-%d')
            daily_cost = self.daily_usage_tracking.get(today, 0.0)
            
            if daily_cost + cost_estimate > self.max_daily_cost_usd:
                logger.warning(f"⚠️ Query would exceed daily cost limit: ${daily_cost + cost_estimate:.2f} > ${self.max_daily_cost_usd}")
                return {
                    'error': 'Daily cost limit exceeded',
                    'estimated_cost': cost_estimate,
                    'daily_usage': daily_cost,
                    'limit': self.max_daily_cost_usd
                }
            
            # Step 3: Execute actual query
            if cost_estimate > 0.50:  # Extra confirmation for expensive queries
                logger.warning(f"🚨 Expensive query detected: ${cost_estimate:.2f} - proceeding with caution")
            
            query_job = self.client.query(query)
            results = query_job.result()
            
            # Step 4: Update daily usage tracking
            actual_cost = self._calculate_actual_cost(query_job)
            self.daily_usage_tracking[today] = daily_cost + actual_cost
            
            # Step 5: Format results
            formatted_results = self._format_query_results(results, operation_name)
            formatted_results['cost_info'] = {
                'estimated_cost': cost_estimate,
                'actual_cost': actual_cost,
                'daily_usage': self.daily_usage_tracking[today]
            }
            
            logger.info(f"✅ Query {operation_name} completed - Actual cost: ${actual_cost:.4f}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ BigQuery operation {operation_name} failed: {e}")
            return {'error': str(e), 'operation': operation_name}
    
    def _create_dry_run_job(self, query: str) -> bigquery.QueryJob:
        """Create dry run job to estimate costs"""
        job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        return self.client.query(query, job_config=job_config)
    
    def _calculate_query_cost(self, dry_run_job: bigquery.QueryJob) -> float:
        """Calculate estimated query cost from dry run"""
        if dry_run_job.total_bytes_processed:
            tb_processed = dry_run_job.total_bytes_processed / (1024**4)  # Convert to TB
            return tb_processed * self.cost_per_tb_processed
        return 0.0
    
    def _calculate_actual_cost(self, query_job: bigquery.QueryJob) -> float:
        """Calculate actual query cost after execution"""
        if query_job.total_bytes_processed:
            tb_processed = query_job.total_bytes_processed / (1024**4)
            return tb_processed * self.cost_per_tb_processed
        return 0.0
    
    def _format_query_results(self, results, operation_name: str) -> Dict:
        """Format BigQuery results into actionable intelligence"""
        formatted_data = []
        
        for row in results:
            row_dict = {}
            for key, value in row.items():
                # Handle different data types
                if isinstance(value, datetime):
                    row_dict[key] = value.isoformat()
                elif value is None:
                    row_dict[key] = None
                else:
                    row_dict[key] = value
            formatted_data.append(row_dict)
        
        return {
            'operation': operation_name,
            'timestamp': datetime.utcnow().isoformat(),
            'result_count': len(formatted_data),
            'data': formatted_data
        }
    
    async def get_daily_cost_usage(self) -> Dict:
        """Get current daily cost usage for monitoring"""
        today = datetime.now().strftime('%Y-%m-%d')
        daily_usage = self.daily_usage_tracking.get(today, 0.0)
        
        return {
            'date': today,
            'current_usage_usd': daily_usage,
            'daily_limit_usd': self.max_daily_cost_usd,
            'remaining_budget_usd': self.max_daily_cost_usd - daily_usage,
            'usage_percentage': (daily_usage / self.max_daily_cost_usd) * 100
        }
    
    async def optimize_qualification_criteria(self) -> Dict:
        """
        Analyze qualification criteria effectiveness to optimize scoring
        """
        query = f"""
        -- Qualification criteria optimization analysis
        WITH scoring_analysis AS (
          SELECT 
            qualification_score,
            COUNT(*) as lead_count,
            AVG(estimated_monthly_loss) as avg_opportunity,
            AVG(performance_score) as avg_performance,
            COUNTIF(urgency_level = 'HOT') as hot_leads,
            
            -- Conversion indicators (if we have them)
            COUNTIF(REGEXP_CONTAINS(LOWER(specific_pain_points), 'critical|urgent|immediate')) as urgent_pain_signals
            
          FROM `{self.config.GOOGLE_CLOUD_PROJECT}.{self.config.BIGQUERY_DATASET_ID}.qualified_leads`
          WHERE 
            last_updated >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
            AND qualification_score > 0
          GROUP BY qualification_score
        )
        SELECT 
          CASE 
            WHEN qualification_score >= 80 THEN 'Excellent (80+)'
            WHEN qualification_score >= 70 THEN 'Good (70-79)'
            WHEN qualification_score >= 60 THEN 'Fair (60-69)'
            WHEN qualification_score >= 40 THEN 'Poor (40-59)'
            ELSE 'Very Poor (<40)'
          END as score_category,
          
          SUM(lead_count) as total_leads,
          ROUND(AVG(avg_opportunity), 0) as avg_opportunity_per_lead,
          ROUND(AVG(avg_performance), 1) as avg_performance_score,
          SUM(hot_leads) as total_hot_leads,
          ROUND(SUM(hot_leads) * 100.0 / SUM(lead_count), 1) as hot_lead_percentage,
          SUM(urgent_pain_signals) as urgent_pain_count
          
        FROM scoring_analysis
        GROUP BY score_category
        ORDER BY 
          CASE score_category
            WHEN 'Excellent (80+)' THEN 1
            WHEN 'Good (70-79)' THEN 2
            WHEN 'Fair (60-69)' THEN 3
            WHEN 'Poor (40-59)' THEN 4
            ELSE 5
          END
        """
        
        return await self._execute_query_with_cost_control(query, "qualification_optimization")
    
    def generate_intelligence_summary(self, analyses: Dict) -> Dict:
        """
        Generate executive summary from multiple intelligence analyses
        """
        summary = {
            'generated_at': datetime.utcnow().isoformat(),
            'total_cost_usd': sum(
                analysis.get('cost_info', {}).get('actual_cost', 0) 
                for analysis in analyses.values() 
                if isinstance(analysis, dict)
            ),
            'key_insights': [],
            'action_items': [],
            'market_opportunities': []
        }
        
        # Extract key insights from hot leads analysis
        if 'hot_leads' in analyses and 'data' in analyses['hot_leads']:
            hot_data = analyses['hot_leads']['data']
            if hot_data:
                hot_leads = next((item for item in hot_data if item.get('urgency_level') == 'HOT'), None)
                if hot_leads:
                    summary['key_insights'].append(
                        f"🔥 {hot_leads.get('lead_count', 0)} HOT leads ready for immediate outreach "
                        f"with ${hot_leads.get('total_monthly_opportunity', 0):,.0f}/month opportunity"
                    )
                    summary['action_items'].append(
                        f"Immediate: Contact hot leads - {hot_leads.get('top_3_companies', 'See detailed report')}"
                    )
        
        # Extract industry opportunities
        if 'industry' in analyses and 'data' in analyses['industry']:
            industry_data = analyses['industry']['data']
            if industry_data:
                top_industry = industry_data[0]
                summary['market_opportunities'].append(
                    f"💰 {top_industry.get('industry', 'Unknown')} industry: "
                    f"${top_industry.get('total_opportunity', 0):,.0f} total opportunity "
                    f"({top_industry.get('critical_performance_pct', 0)}% have critical performance issues)"
                )
        
        return summary
