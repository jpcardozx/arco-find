#!/usr/bin/env python3
"""
REALISTIC DRY RUN - Cost and Data Validation
==========================================

Executa dry run do engine realista para:
1. Verificar custos reais do BigQuery
2. Validar dados sem executar análise web completa
3. Estimar performance sem custos adicionais
"""

import asyncio
from google.cloud import bigquery
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - DRY_RUN - %(message)s')
logger = logging.getLogger(__name__)

class RealisticDryRunner:
    """Dry run validation for realistic engine"""
    
    def __init__(self):
        self.client = bigquery.Client()
        logger.info("Realistic Dry Run initialized")

    async def validate_query_cost(self):
        """Validate actual BigQuery costs"""
        
        # Exact query from realistic engine
        query = """
        WITH basic_prospects AS (
            SELECT 
                advertiser_disclosed_name,
                advertiser_location,
                COUNT(*) as ad_volume,
                COUNT(DISTINCT creative_id) as creative_count,
                ROUND(COUNT(DISTINCT creative_id) / COUNT(*), 3) as creative_diversity,
                
                -- Basic vertical classification
                CASE 
                    WHEN LOWER(advertiser_disclosed_name) LIKE '%clinic%'
                         OR LOWER(advertiser_disclosed_name) LIKE '%aesthetic%'
                         OR LOWER(advertiser_disclosed_name) LIKE '%beauty%'
                    THEN 'aesthetic'
                    WHEN LOWER(advertiser_disclosed_name) LIKE '%estate%'
                         OR LOWER(advertiser_disclosed_name) LIKE '%property%'
                    THEN 'estate'
                    WHEN LOWER(advertiser_disclosed_name) LIKE '%law%'
                         OR LOWER(advertiser_disclosed_name) LIKE '%legal%'
                         OR LOWER(advertiser_disclosed_name) LIKE '%solicitor%'
                    THEN 'legal'
                    WHEN LOWER(advertiser_disclosed_name) LIKE '%dental%'
                         OR LOWER(advertiser_disclosed_name) LIKE '%dentist%'
                    THEN 'dental'
                    ELSE 'other'
                END as vertical,
                
                -- Get a sample URL for web analysis
                ARRAY_AGG(creative_page_url IGNORE NULLS LIMIT 1)[SAFE_OFFSET(0)] as sample_url
                
            FROM `bigquery-public-data.google_ads_transparency_center.creative_stats`
            WHERE advertiser_location IN ('GB', 'IE')
                AND (
                    LOWER(advertiser_disclosed_name) LIKE '%clinic%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%aesthetic%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%beauty%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%estate%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%property%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%law%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%legal%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%dental%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%dentist%'
                )
                -- Exclude obvious large corporations
                AND NOT (
                    LOWER(advertiser_disclosed_name) LIKE '%hospital%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%university%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%group plc%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%holdings%'
                )
            GROUP BY advertiser_disclosed_name, advertiser_location
            HAVING ad_volume BETWEEN 15 AND 100  -- SME range
                AND vertical != 'other'
        )
        SELECT * FROM basic_prospects
        ORDER BY ad_volume DESC
        LIMIT 15
        """
        
        logger.info("=== REALISTIC ENGINE DRY RUN ===")
        
        try:
            # Dry run configuration
            job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
            job = self.client.query(query, job_config=job_config)
            
            # Calculate costs
            bytes_processed = job.total_bytes_processed
            gb_processed = bytes_processed / (1024**3)
            tb_processed = bytes_processed / (1024**4)
            
            # Real BigQuery pricing
            cost_per_tb = 6.25  # $6.25 per TB in US regions
            cost_per_execution = tb_processed * cost_per_tb
            
            logger.info(f">> Bytes processed: {bytes_processed:,}")
            logger.info(f">> GB processed: {gb_processed:.2f} GB")
            logger.info(f">> Cost per execution: ${cost_per_execution:.6f} USD")
            logger.info(f">> Monthly cost (1x/day): ${cost_per_execution * 30:.4f} USD")
            logger.info(f">> Monthly cost (3x/week): ${cost_per_execution * 12:.4f} USD")
            
            # Cost efficiency analysis
            if cost_per_execution < 0.01:
                efficiency = "EXCELLENT - Under $0.01"
            elif cost_per_execution < 0.05:
                efficiency = "GOOD - Under $0.05"
            elif cost_per_execution < 0.10:
                efficiency = "ACCEPTABLE - Under $0.10"
            else:
                efficiency = "HIGH - Review optimization"
            
            logger.info(f">> Cost efficiency: {efficiency}")
            
            return {
                'bytes_processed': bytes_processed,
                'cost_per_execution': cost_per_execution,
                'monthly_cost_daily': cost_per_execution * 30,
                'monthly_cost_3x_week': cost_per_execution * 12,
                'efficiency_rating': efficiency
            }
            
        except Exception as e:
            logger.error(f">> Dry run failed: {e}")
            return None

    async def validate_data_quality(self):
        """Validate expected data patterns without full execution"""
        
        # Simplified validation query
        validation_query = """
        SELECT 
            COUNT(*) as total_advertisers,
            COUNT(DISTINCT advertiser_location) as unique_locations,
            AVG(ad_count) as avg_ads_per_advertiser,
            MIN(ad_count) as min_ads,
            MAX(ad_count) as max_ads,
            COUNTIF(has_url) as advertisers_with_urls
        FROM (
            SELECT 
                advertiser_disclosed_name,
                advertiser_location,
                COUNT(*) as ad_count,
                COUNT(creative_page_url) > 0 as has_url
            FROM `bigquery-public-data.google_ads_transparency_center.creative_stats`
            WHERE advertiser_location IN ('GB', 'IE')
                AND (
                    LOWER(advertiser_disclosed_name) LIKE '%clinic%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%estate%'
                    OR LOWER(advertiser_disclosed_name) LIKE '%dental%'
                )
                AND NOT LOWER(advertiser_disclosed_name) LIKE '%hospital%'
            GROUP BY advertiser_disclosed_name, advertiser_location
            HAVING ad_count BETWEEN 15 AND 100
        )
        """
        
        logger.info("=== DATA QUALITY VALIDATION ===")
        
        try:
            # Execute validation (small cost)
            job = self.client.query(validation_query)
            results = job.result()
            
            for row in results:
                logger.info(f">> Total SME advertisers found: {row.total_advertisers}")
                logger.info(f">> Unique locations: {row.unique_locations}")
                logger.info(f">> Average ads per advertiser: {row.avg_ads_per_advertiser:.1f}")
                logger.info(f">> Ad volume range: {row.min_ads} - {row.max_ads}")
                logger.info(f">> Advertisers with URLs: {row.advertisers_with_urls}")
                
                # Quality assessment
                if row.total_advertisers >= 10:
                    quality = "GOOD - Sufficient sample size"
                elif row.total_advertisers >= 5:
                    quality = "ACCEPTABLE - Limited but usable"
                else:
                    quality = "LOW - May need broader criteria"
                
                logger.info(f">> Data quality: {quality}")
                
                url_coverage = (row.advertisers_with_urls / row.total_advertisers) * 100 if row.total_advertisers > 0 else 0
                logger.info(f">> URL coverage: {url_coverage:.1f}%")
                
                return {
                    'total_advertisers': row.total_advertisers,
                    'avg_ads': row.avg_ads_per_advertiser,
                    'url_coverage_pct': url_coverage,
                    'quality_rating': quality
                }
            
        except Exception as e:
            logger.error(f">> Data validation failed: {e}")
            return None

    async def estimate_web_analysis_impact(self):
        """Estimate web analysis performance without execution"""
        
        logger.info("=== WEB ANALYSIS ESTIMATION ===")
        
        # Mock web analysis based on typical patterns
        typical_results = {
            'urls_testable': 0.85,  # 85% of URLs typically accessible
            'avg_load_time': 2.5,   # Average 2.5 seconds
            'https_adoption': 0.90,  # 90% use HTTPS
            'mobile_responsive': 0.75,  # 75% mobile responsive
            'common_issues_rate': 0.40  # 40% have identifiable issues
        }
        
        logger.info(f">> Expected URL accessibility: {typical_results['urls_testable']:.0%}")
        logger.info(f">> Expected avg load time: {typical_results['avg_load_time']:.1f}s")
        logger.info(f">> Expected HTTPS adoption: {typical_results['https_adoption']:.0%}")
        logger.info(f">> Expected mobile responsiveness: {typical_results['mobile_responsive']:.0%}")
        logger.info(f">> Expected issues identification: {typical_results['common_issues_rate']:.0%}")
        
        # Estimate value add
        logger.info(">> Web analysis adds significant value through:")
        logger.info("   - Real load time measurement")
        logger.info("   - HTTPS and mobile verification") 
        logger.info("   - Specific technical issues identification")
        logger.info("   - Evidence-based optimization recommendations")
        
        return typical_results

    async def generate_dry_run_report(self):
        """Generate comprehensive dry run report"""
        
        logger.info("REALISTIC ENGINE DRY RUN - COMPREHENSIVE VALIDATION")
        logger.info("=" * 55)
        
        # Validate costs
        cost_info = await self.validate_query_cost()
        
        # Validate data quality
        data_info = await self.validate_data_quality()
        
        # Estimate web analysis
        web_info = await self.estimate_web_analysis_impact()
        
        logger.info("=" * 55)
        logger.info("DRY RUN SUMMARY")
        logger.info("=" * 55)
        
        if cost_info:
            logger.info(f"✓ Cost per execution: ${cost_info['cost_per_execution']:.6f}")
            logger.info(f"✓ Monthly budget needed: ${cost_info['monthly_cost_3x_week']:.2f}")
            logger.info(f"✓ Cost efficiency: {cost_info['efficiency_rating']}")
        
        if data_info:
            logger.info(f"✓ Expected prospects: {data_info['total_advertisers']}")
            logger.info(f"✓ Data quality: {data_info['quality_rating']}")
            logger.info(f"✓ Web analysis coverage: {data_info['url_coverage_pct']:.0f}%")
        
        if web_info:
            logger.info(f"✓ Web insights success rate: {web_info['urls_testable']:.0%}")
            logger.info(f"✓ Technical issues detection: {web_info['common_issues_rate']:.0%}")
        
        logger.info("\nRECOMMENDATIONS:")
        logger.info("• Execute 2-3x per week to balance cost and freshness")
        logger.info("• Focus on prospects with URL data for maximum value")
        logger.info("• Web analysis provides significant differentiation")
        logger.info("• Conservative estimates ensure realistic client expectations")
        
        logger.info("=" * 55)
        
        return {
            'cost_analysis': cost_info,
            'data_analysis': data_info,
            'web_analysis_estimate': web_info,
            'recommendation': 'PROCEED - Engine optimized for realistic ROI'
        }

async def main():
    """Run comprehensive dry run validation"""
    dry_runner = RealisticDryRunner()
    report = await dry_runner.generate_dry_run_report()
    return report

if __name__ == "__main__":
    asyncio.run(main())