"""
🎯 LEAD QUALIFICATION ENGINE
Core engine for identifying and qualifying hot leads using BigQuery + SearchAPI
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from google.cloud import bigquery
from config.api_keys import APIConfig

try:
    from src.connectors.searchapi_connector import SearchAPIConnector
    from src.connectors.google_pagespeed_api import GooglePageSpeedAPI
    from src.utils.logger import setup_logger
except ImportError:
    # Fallback for missing modules
    class SearchAPIConnector:
        def __init__(self, *args, **kwargs): pass
        async def search_companies(self, *args, **kwargs): return []
    
    class GooglePageSpeedAPI:
        def __init__(self, *args, **kwargs): pass
        async def analyze_page(self, *args, **kwargs): return {}
    
    def setup_logger(name): 
        import logging
        return logging.getLogger(name)

logger = setup_logger(__name__)

@dataclass
class QualifiedLead:
    """Qualified lead with actionable intelligence"""
    company_name: str
    website: str
    industry: str
    employee_count: int
    monthly_ad_spend: float
    performance_score: int
    message_match_score: float
    qualification_score: int
    urgency_level: str  # HOT, WARM, COLD
    estimated_monthly_loss: float
    specific_pain_points: List[str]
    conversion_priority: str

class LeadQualificationEngine:
    """Smart lead qualification using BigQuery intelligence + SearchAPI data"""
    
    def __init__(self):
        self.config = APIConfig()
        self.bq_client = bigquery.Client(project=self.config.GOOGLE_CLOUD_PROJECT)
        
        # Initialize with proper API key
        try:
            self.search_api = SearchAPIConnector(api_key=self.config.SEARCH_API_KEY)
        except:
            self.search_api = SearchAPIConnector()
        
        try:
            self.pagespeed_api = GooglePageSpeedAPI()
        except:
            self.pagespeed_api = None
        
        # Cost control
        self.max_bq_queries_per_day = 10  # Conservative limit
        self.queries_used_today = 0
        
    async def discover_qualified_leads(self, target_count: int = 10) -> List[QualifiedLead]:
        """
        Main method: Discover qualified leads using intelligent BigQuery + SearchAPI
        """
        logger.info(f"🎯 Starting qualified lead discovery for {target_count} leads")
        
        try:
            # 1. Check existing hot leads in BigQuery first (free query)
            hot_leads = await self._get_existing_hot_leads(target_count)
            
            if len(hot_leads) >= target_count:
                logger.info(f"✅ Found {len(hot_leads)} existing hot leads - no API calls needed")
                return hot_leads
            
            # 2. Need more leads - strategic SearchAPI discovery
            needed_leads = target_count - len(hot_leads)
            new_leads = await self._discover_new_leads_searchapi(needed_leads)
            
            # 3. Qualify and store new leads
            qualified_new = await self._qualify_and_store_leads(new_leads)
            
            all_qualified = hot_leads + qualified_new
            
            logger.info(f"✅ Total qualified leads discovered: {len(all_qualified)}")
            return all_qualified[:target_count]
            
        except Exception as e:
            logger.error(f"❌ Lead discovery failed: {e}")
            return []
    
    async def _get_existing_hot_leads(self, limit: int) -> List[QualifiedLead]:
        """
        Get existing hot leads from BigQuery - no cost, immediate results
        """
        # This query is free - just reading existing data
        query = f"""
        SELECT 
            company_name,
            website,
            industry,
            employee_count,
            monthly_ad_spend,
            performance_score,
            message_match_score,
            qualification_score,
            urgency_level,
            estimated_monthly_loss,
            specific_pain_points,
            conversion_priority
        FROM `{self.config.GOOGLE_CLOUD_PROJECT}.{self.config.BIGQUERY_DATASET_ID}.qualified_leads`
        WHERE 
            qualification_score >= 70
            AND last_updated >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
            AND conversion_priority IN ('HOT - 48h Conversion Target', 'WARM - 7-day Nurture')
        ORDER BY qualification_score DESC, estimated_monthly_loss DESC
        LIMIT {limit}
        """
        
        try:
            query_job = self.bq_client.query(query)
            results = query_job.result()
            
            leads = []
            for row in results:
                leads.append(QualifiedLead(
                    company_name=row.company_name,
                    website=row.website,
                    industry=row.industry,
                    employee_count=row.employee_count,
                    monthly_ad_spend=row.monthly_ad_spend,
                    performance_score=row.performance_score,
                    message_match_score=row.message_match_score,
                    qualification_score=row.qualification_score,
                    urgency_level=row.urgency_level,
                    estimated_monthly_loss=row.estimated_monthly_loss,
                    specific_pain_points=json.loads(row.specific_pain_points) if row.specific_pain_points else [],
                    conversion_priority=row.conversion_priority
                ))
            
            logger.info(f"📊 Found {len(leads)} existing qualified leads in BigQuery")
            return leads
            
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch existing leads: {e}")
            return []
    
    async def _discover_new_leads_searchapi(self, needed_count: int) -> List[Dict]:
        """
        Strategic SearchAPI discovery focusing on high-value, actionable leads
        """
        # Strategic search queries focusing on pain signals
        search_queries = [
            "site:linkedin.com/company fintech brasil employees 15..100",
            "site:linkedin.com/company healthtech portugal employees 20..80", 
            "site:linkedin.com/company saas canada employees 25..75",
            "site:linkedin.com/company digital marketing agency employees 10..50"
        ]
        
        discovered_companies = []
        
        for query in search_queries:
            if len(discovered_companies) >= needed_count * 2:  # 2x buffer for qualification
                break
                
            try:
                logger.info(f"🔍 SearchAPI query: {query}")
                results = await self.search_api.search_companies(
                    query=query,
                    max_results=10  # Conservative to control costs
                )
                
                for result in results:
                    if len(discovered_companies) >= needed_count * 2:
                        break
                    
                    # Basic validation - only proceed with real websites
                    if result.get('website') and self._is_valid_website(result['website']):
                        discovered_companies.append(result)
                
            except Exception as e:
                logger.warning(f"⚠️ SearchAPI query failed: {e}")
                continue
        
        logger.info(f"🔍 Discovered {len(discovered_companies)} companies via SearchAPI")
        return discovered_companies
    
    async def _qualify_and_store_leads(self, companies: List[Dict]) -> List[QualifiedLead]:
        """
        Qualify leads using strategic analysis and store in BigQuery
        """
        qualified_leads = []
        
        for company in companies:
            try:
                # Strategic qualification - focus on actionable insights
                qualification = await self._strategic_qualify_lead(company)
                
                if qualification and qualification.qualification_score >= 60:
                    qualified_leads.append(qualification)
                    
                    # Store in BigQuery for future use
                    await self._store_qualified_lead(qualification)
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to qualify {company.get('name', 'unknown')}: {e}")
                continue
        
        logger.info(f"✅ Qualified {len(qualified_leads)} leads for storage")
        return qualified_leads
    
    async def _strategic_qualify_lead(self, company: Dict) -> Optional[QualifiedLead]:
        """
        Strategic qualification focusing on actionable business intelligence
        """
        try:
            website = company.get('website', '').strip()
            company_name = company.get('name', 'Unknown')
            
            if not website:
                return None
            
            # Performance analysis (strategic - only when needed)
            performance_data = await self._analyze_performance_strategic(website)
            
            # Estimate business metrics from available data
            business_metrics = self._estimate_business_metrics(company, performance_data)
            
            # Calculate qualification score
            qualification_score = self._calculate_qualification_score(business_metrics)
            
            if qualification_score < 60:  # Don't waste storage on low-quality leads
                return None
            
            return QualifiedLead(
                company_name=company_name,
                website=website,
                industry=company.get('industry', 'unknown'),
                employee_count=business_metrics.get('employee_count', 0),
                monthly_ad_spend=business_metrics.get('monthly_ad_spend', 0),
                performance_score=performance_data.get('performance_score', 0),
                message_match_score=business_metrics.get('message_match_score', 0),
                qualification_score=qualification_score,
                urgency_level=self._determine_urgency_level(qualification_score, performance_data),
                estimated_monthly_loss=business_metrics.get('estimated_monthly_loss', 0),
                specific_pain_points=performance_data.get('pain_points', []),
                conversion_priority=self._determine_conversion_priority(qualification_score)
            )
            
        except Exception as e:
            logger.error(f"❌ Strategic qualification failed for {company.get('name')}: {e}")
            return None
    
    async def _analyze_performance_strategic(self, website: str) -> Dict:
        """
        Strategic performance analysis - only critical metrics
        """
        try:
            # Use PageSpeed API strategically - only for qualifying leads
            performance_data = await self.pagespeed_api.analyze_url(website, strategy="mobile")
            
            if not performance_data:
                return {'performance_score': 50, 'pain_points': ['Could not analyze performance']}
            
            # Extract critical metrics
            lighthouse = performance_data.get('lighthouseResult', {})
            categories = lighthouse.get('categories', {})
            
            performance_score = 0
            pain_points = []
            
            if 'performance' in categories:
                performance_score = int(categories['performance']['score'] * 100)
                
                if performance_score < 50:
                    pain_points.append('Critical performance issues affecting conversions')
                elif performance_score < 70:
                    pain_points.append('Performance issues hurting user experience')
            
            # Core Web Vitals analysis
            audits = lighthouse.get('audits', {})
            if 'largest-contentful-paint' in audits:
                lcp = audits['largest-contentful-paint'].get('numericValue', 0) / 1000
                if lcp > 4:
                    pain_points.append(f'Page load too slow ({lcp:.1f}s) - losing customers')
            
            return {
                'performance_score': performance_score,
                'pain_points': pain_points,
                'has_critical_issues': performance_score < 50
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Performance analysis failed for {website}: {e}")
            return {'performance_score': 50, 'pain_points': ['Performance analysis unavailable']}
    
    def _estimate_business_metrics(self, company: Dict, performance_data: Dict) -> Dict:
        """
        Estimate business metrics for qualification scoring
        """
        # Conservative estimates based on company size and industry
        employee_count = company.get('employee_count', 25)  # Default mid-range
        industry = company.get('industry', 'unknown').lower()
        
        # Estimate monthly ad spend based on company size and industry
        base_spend = employee_count * 100  # $100 per employee baseline
        
        # Industry multipliers for ad spend
        industry_multipliers = {
            'fintech': 2.5,
            'saas': 2.0,
            'healthtech': 1.8,
            'digital_marketing': 3.0,
            'e_commerce': 2.2,
            'consulting': 1.5
        }
        
        multiplier = 1.0
        for key, mult in industry_multipliers.items():
            if key in industry:
                multiplier = mult
                break
        
        estimated_ad_spend = base_spend * multiplier
        
        # Estimate monthly loss from performance issues
        performance_score = performance_data.get('performance_score', 100)
        performance_impact = max(0, (100 - performance_score) / 100)
        estimated_monthly_loss = estimated_ad_spend * performance_impact * 0.3  # 30% waste from poor performance
        
        return {
            'employee_count': employee_count,
            'monthly_ad_spend': estimated_ad_spend,
            'estimated_monthly_loss': estimated_monthly_loss,
            'message_match_score': 70  # Default - would need ad data to calculate
        }
    
    def _calculate_qualification_score(self, metrics: Dict) -> int:
        """
        Calculate qualification score (0-100) based on business potential
        """
        score = 0
        
        # Budget potential (0-30 points)
        ad_spend = metrics.get('monthly_ad_spend', 0)
        if ad_spend >= 10000:
            score += 30
        elif ad_spend >= 5000:
            score += 25
        elif ad_spend >= 2000:
            score += 20
        elif ad_spend >= 1000:
            score += 15
        else:
            score += 5
        
        # Company size (0-25 points)
        employees = metrics.get('employee_count', 0)
        if 25 <= employees <= 75:  # Sweet spot
            score += 25
        elif 15 <= employees <= 100:
            score += 20
        elif 10 <= employees <= 150:
            score += 15
        else:
            score += 5
        
        # Opportunity size (0-25 points)
        monthly_loss = metrics.get('estimated_monthly_loss', 0)
        if monthly_loss >= 3000:
            score += 25
        elif monthly_loss >= 1500:
            score += 20
        elif monthly_loss >= 500:
            score += 15
        else:
            score += 5
        
        # Implementation feasibility (0-20 points)
        score += 20  # Default - assume feasible
        
        return min(score, 100)
    
    def _determine_urgency_level(self, qualification_score: int, performance_data: Dict) -> str:
        """Determine urgency level for sales prioritization"""
        if qualification_score >= 80 and performance_data.get('has_critical_issues'):
            return 'HOT'
        elif qualification_score >= 70:
            return 'WARM'
        else:
            return 'COLD'
    
    def _determine_conversion_priority(self, qualification_score: int) -> str:
        """Determine conversion priority for sales process"""
        if qualification_score >= 80:
            return 'HOT - 48h Conversion Target'
        elif qualification_score >= 60:
            return 'WARM - 7-day Nurture'
        else:
            return 'COLD - Long-term Pipeline'
    
    def _is_valid_website(self, website: str) -> bool:
        """Basic website validation"""
        if not website:
            return False
        
        website = website.lower().strip()
        
        # Exclude obvious non-business websites
        invalid_patterns = [
            'linkedin.com', 'facebook.com', 'twitter.com', 'instagram.com',
            'example.com', 'test.com', 'localhost'
        ]
        
        return not any(pattern in website for pattern in invalid_patterns)
    
    async def _store_qualified_lead(self, lead: QualifiedLead):
        """Store qualified lead in BigQuery for future reference"""
        try:
            table_id = f"{self.config.GOOGLE_CLOUD_PROJECT}.{self.config.BIGQUERY_DATASET_ID}.qualified_leads"
            
            row = {
                'company_name': lead.company_name,
                'website': lead.website,
                'industry': lead.industry,
                'employee_count': lead.employee_count,
                'monthly_ad_spend': lead.monthly_ad_spend,
                'performance_score': lead.performance_score,
                'message_match_score': lead.message_match_score,
                'qualification_score': lead.qualification_score,
                'urgency_level': lead.urgency_level,
                'estimated_monthly_loss': lead.estimated_monthly_loss,
                'specific_pain_points': json.dumps(lead.specific_pain_points),
                'conversion_priority': lead.conversion_priority,
                'created_date': datetime.utcnow().isoformat(),
                'last_updated': datetime.utcnow().isoformat()
            }
            
            errors = self.bq_client.insert_rows_json(
                self.bq_client.get_table(table_id), 
                [row]
            )
            
            if not errors:
                logger.info(f"✅ Stored qualified lead: {lead.company_name}")
            else:
                logger.error(f"❌ Failed to store lead: {errors}")
                
        except Exception as e:
            logger.error(f"❌ Storage error for {lead.company_name}: {e}")

    def get_qualification_summary(self, leads: List[QualifiedLead]) -> Dict:
        """Generate actionable summary for sales team"""
        if not leads:
            return {'message': 'No qualified leads found'}
        
        hot_leads = [l for l in leads if l.urgency_level == 'HOT']
        warm_leads = [l for l in leads if l.urgency_level == 'WARM']
        
        total_opportunity = sum(l.estimated_monthly_loss * 12 for l in leads)
        
        return {
            'total_qualified_leads': len(leads),
            'hot_leads_count': len(hot_leads),
            'warm_leads_count': len(warm_leads),
            'total_annual_opportunity': total_opportunity,
            'average_qualification_score': sum(l.qualification_score for l in leads) / len(leads),
            'top_3_hot_leads': [
                {
                    'company': l.company_name,
                    'opportunity': f"${l.estimated_monthly_loss * 12:,.0f}/year",
                    'score': l.qualification_score,
                    'pain_points': l.specific_pain_points[:2]  # Top 2 pain points
                }
                for l in sorted(hot_leads, key=lambda x: x.qualification_score, reverse=True)[:3]
            ]
        }
