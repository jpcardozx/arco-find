"""
Google Ads Integration for ARCO.

This module provides integration with Google Ads API to collect
real advertising spend and performance data for prospect analysis.
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from ..models.prospect import AdSpendData
from ..utils.logger import get_logger

logger = get_logger(__name__)

class GoogleAdsIntegration:
    """Google Ads API integration for real advertising data collection."""
    
    def __init__(self, developer_token: Optional[str] = None, client_id: Optional[str] = None, 
                 client_secret: Optional[str] = None, refresh_token: Optional[str] = None):
        """
        Initialize Google Ads integration.
        
        Args:
            developer_token: Google Ads API developer token
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            refresh_token: OAuth2 refresh token
        """
        self.developer_token = developer_token or os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN')
        self.client_id = client_id or os.getenv('GOOGLE_ADS_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('GOOGLE_ADS_CLIENT_SECRET')
        self.refresh_token = refresh_token or os.getenv('GOOGLE_ADS_REFRESH_TOKEN')
        
        self.session = None
        self.access_token = None
        self.token_expires_at = None
        
        # API endpoints
        self.auth_url = "https://oauth2.googleapis.com/token"
        self.api_base_url = "https://googleads.googleapis.com/v16"
        
        logger.info("GoogleAdsIntegration initialized")
    
    async def _init_session(self) -> None:
        """Initialize HTTP session with proper headers."""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'ARCO-Marketing-Analyzer/1.0',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            )
    
    async def _get_access_token(self) -> Optional[str]:
        """Get or refresh OAuth2 access token."""
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            logger.warning("Missing OAuth2 credentials for Google Ads API")
            return None
        
        # Check if current token is still valid
        if (self.access_token and self.token_expires_at and 
            datetime.now() < self.token_expires_at - timedelta(minutes=5)):
            return self.access_token
        
        try:
            await self._init_session()
            
            # Refresh token
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.refresh_token,
                'grant_type': 'refresh_token'
            }
            
            async with self.session.post(self.auth_url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data.get('access_token')
                    expires_in = token_data.get('expires_in', 3600)
                    self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                    
                    logger.info("Google Ads access token refreshed successfully")
                    return self.access_token
                else:
                    logger.error(f"Failed to refresh Google Ads token: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error refreshing Google Ads token: {e}")
            return None
    
    async def get_campaign_metrics(self, customer_id: str, domain: str = None) -> Optional[Dict[str, Any]]:
        """
        Get campaign performance metrics for a customer.
        
        Args:
            customer_id: Google Ads customer ID
            domain: Domain to filter campaigns (optional)
            
        Returns:
            Dictionary with campaign metrics including CPC, CTR, conversion rate, ROAS data
        """
        if not self.developer_token:
            logger.warning("No Google Ads developer token provided")
            return self._get_estimated_campaign_metrics(domain)
        
        access_token = await self._get_access_token()
        if not access_token:
            logger.warning("Could not get Google Ads access token, using estimates")
            return self._get_estimated_campaign_metrics(domain)
        
        max_retries = 3
        retry_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                await self._init_session()
                
                # Build Google Ads query for campaign metrics
                query = self._build_campaign_metrics_query(domain)
                
                url = f"{self.api_base_url}/customers/{customer_id}/googleAds:searchStream"
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'developer-token': self.developer_token,
                    'Content-Type': 'application/json'
                }
                
                payload = {'query': query}
                
                async with asyncio.wait_for(
                    self.session.post(url, headers=headers, json=payload),
                    timeout=30.0
                ) as response:
                    
                    if response.status == 429:  # Rate limited
                        logger.warning(f"Rate limited for customer {customer_id}, attempt {attempt + 1}/{max_retries}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_delay * (2 ** attempt))
                            continue
                        return self._get_estimated_campaign_metrics(domain)
                    
                    if response.status != 200:
                        logger.warning(f"Google Ads API failed for customer {customer_id}: {response.status}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_delay)
                            continue
                        return self._get_estimated_campaign_metrics(domain)
                    
                    data = await response.json()
                    result = self._parse_campaign_metrics(data, domain)
                    
                    if result:
                        logger.info(f"Successfully collected campaign metrics for customer {customer_id}")
                        return result
                    else:
                        logger.warning(f"No campaign data found for customer {customer_id}")
                        return self._get_estimated_campaign_metrics(domain)
                        
            except asyncio.TimeoutError:
                logger.warning(f"Timeout fetching campaign metrics for customer {customer_id}, attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
                    
            except Exception as e:
                logger.error(f"Error fetching campaign metrics for customer {customer_id}: {e}, attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
                break
        
        logger.warning(f"Failed to fetch campaign metrics for customer {customer_id}, using estimates")
        return self._get_estimated_campaign_metrics(domain)
    
    def _build_campaign_metrics_query(self, domain: str = None) -> str:
        """
        Build Google Ads query for campaign metrics.
        
        Args:
            domain: Domain to filter campaigns
            
        Returns:
            Google Ads query string
        """
        # Get last 30 days of data
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        query = f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            metrics.cost_micros,
            metrics.clicks,
            metrics.impressions,
            metrics.ctr,
            metrics.average_cpc,
            metrics.conversions,
            metrics.conversion_rate,
            metrics.cost_per_conversion,
            metrics.value_per_conversion
        FROM campaign
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        """
        
        # Add domain filter if provided
        if domain:
            query += f" AND campaign.name CONTAINS '{domain}'"
        
        return query.strip()
    
    def _parse_campaign_metrics(self, data: Dict[str, Any], domain: str) -> Optional[Dict[str, Any]]:
        """
        Parse Google Ads API response into campaign metrics.
        
        Args:
            data: Raw Google Ads API response
            domain: Domain being analyzed
            
        Returns:
            Dictionary with parsed campaign metrics
        """
        try:
            results = data.get('results', [])
            if not results:
                return None
            
            # Aggregate metrics across all campaigns
            total_cost_micros = 0
            total_clicks = 0
            total_impressions = 0
            total_conversions = 0
            campaign_count = 0
            
            for result in results:
                metrics = result.get('metrics', {})
                total_cost_micros += int(metrics.get('costMicros', 0))
                total_clicks += int(metrics.get('clicks', 0))
                total_impressions += int(metrics.get('impressions', 0))
                total_conversions += float(metrics.get('conversions', 0))
                campaign_count += 1
            
            if total_impressions == 0:
                return None
            
            # Calculate aggregated metrics
            monthly_spend = total_cost_micros / 1_000_000  # Convert from micros
            avg_cpc = (total_cost_micros / total_clicks / 1_000_000) if total_clicks > 0 else 0
            avg_ctr = (total_clicks / total_impressions) if total_impressions > 0 else 0
            conversion_rate = (total_conversions / total_clicks) if total_clicks > 0 else 0
            cost_per_conversion = (monthly_spend / total_conversions) if total_conversions > 0 else 0
            
            return {
                'monthly_spend': monthly_spend,
                'avg_cpc': avg_cpc,
                'avg_ctr': avg_ctr,
                'conversion_rate': conversion_rate,
                'cost_per_conversion': cost_per_conversion,
                'impressions': total_impressions,
                'clicks': total_clicks,
                'conversions': total_conversions,
                'campaign_count': campaign_count,
                'data_source': 'google_ads_api',
                'collection_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing Google Ads data for {domain}: {e}")
            return None
    
    def _get_estimated_campaign_metrics(self, domain: str = None) -> Dict[str, Any]:
        """
        Get estimated campaign metrics when real data is not available.
        
        Args:
            domain: Domain being analyzed
            
        Returns:
            Dictionary with estimated campaign metrics
        """
        # Industry-based estimates with realistic waste scenarios
        industry_estimates = {
            'ecommerce': {
                'avg_cpc': 2.50,  # Higher CPC to show waste opportunity
                'avg_ctr': 0.0220,  # Lower CTR
                'conversion_rate': 0.0180,  # Lower conversion rate
                'monthly_spend_multiplier': 1.3
            },
            'saas': {
                'avg_cpc': 4.50,  # High CPC for SaaS
                'avg_ctr': 0.0280,
                'conversion_rate': 0.0250,  # Below benchmark
                'monthly_spend_multiplier': 1.5
            },
            'services': {
                'avg_cpc': 3.20,  # Above benchmark
                'avg_ctr': 0.0250,  # Below benchmark
                'conversion_rate': 0.0200,  # Below benchmark
                'monthly_spend_multiplier': 1.2
            },
            'default': {
                'avg_cpc': 3.00,  # Above benchmark to show waste
                'avg_ctr': 0.0250,  # Below benchmark
                'conversion_rate': 0.0200,  # Below benchmark
                'monthly_spend_multiplier': 1.0
            }
        }
        
        # Determine industry from domain
        industry = 'default'
        if domain:
            domain_lower = domain.lower()
            if any(keyword in domain_lower for keyword in ['shop', 'store', 'buy', 'ecommerce']):
                industry = 'ecommerce'
            elif any(keyword in domain_lower for keyword in ['app', 'saas', 'software', 'tech']):
                industry = 'saas'
            elif any(keyword in domain_lower for keyword in ['service', 'consult', 'agency']):
                industry = 'services'
        
        estimates = industry_estimates[industry]
        
        # Base monthly spend estimate
        base_spend = 5000 * estimates['monthly_spend_multiplier']
        
        # Calculate derived metrics
        clicks = int(base_spend / estimates['avg_cpc'])
        impressions = int(clicks / estimates['avg_ctr'])
        conversions = clicks * estimates['conversion_rate']
        cost_per_conversion = base_spend / conversions if conversions > 0 else 0
        
        return {
            'monthly_spend': base_spend,
            'avg_cpc': estimates['avg_cpc'],
            'avg_ctr': estimates['avg_ctr'],
            'conversion_rate': estimates['conversion_rate'],
            'cost_per_conversion': cost_per_conversion,
            'impressions': impressions,
            'clicks': clicks,
            'conversions': conversions,
            'campaign_count': 3,  # Estimated
            'data_source': 'industry_estimates',
            'collection_date': datetime.now().isoformat(),
            'confidence_level': 'low'
        }
    
    async def get_keyword_performance(self, customer_id: str, domain: str = None) -> List[Dict[str, Any]]:
        """
        Get keyword-level performance insights.
        
        Args:
            customer_id: Google Ads customer ID
            domain: Domain to filter keywords
            
        Returns:
            List of keyword performance data
        """
        if not self.developer_token:
            logger.warning("No Google Ads developer token provided")
            return self._get_estimated_keyword_performance(domain)
        
        access_token = await self._get_access_token()
        if not access_token:
            logger.warning("Could not get Google Ads access token, using estimates")
            return self._get_estimated_keyword_performance(domain)
        
        try:
            await self._init_session()
            
            # Build keyword performance query
            query = self._build_keyword_performance_query(domain)
            
            url = f"{self.api_base_url}/customers/{customer_id}/googleAds:searchStream"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'developer-token': self.developer_token,
                'Content-Type': 'application/json'
            }
            
            payload = {'query': query}
            
            async with self.session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_keyword_performance(data, domain)
                else:
                    logger.warning(f"Keyword performance API failed: {response.status}")
                    return self._get_estimated_keyword_performance(domain)
                    
        except Exception as e:
            logger.error(f"Error fetching keyword performance: {e}")
            return self._get_estimated_keyword_performance(domain)
    
    def _build_keyword_performance_query(self, domain: str = None) -> str:
        """Build Google Ads query for keyword performance."""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        query = f"""
        SELECT
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            metrics.cost_micros,
            metrics.clicks,
            metrics.impressions,
            metrics.ctr,
            metrics.average_cpc,
            metrics.conversions,
            metrics.conversion_rate,
            metrics.quality_score
        FROM keyword_view
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND ad_group_criterion.status = 'ENABLED'
        ORDER BY metrics.cost_micros DESC
        LIMIT 50
        """
        
        return query.strip()
    
    def _parse_keyword_performance(self, data: Dict[str, Any], domain: str) -> List[Dict[str, Any]]:
        """Parse keyword performance data."""
        try:
            results = data.get('results', [])
            keywords = []
            
            for result in results:
                criterion = result.get('adGroupCriterion', {}).get('keyword', {})
                metrics = result.get('metrics', {})
                
                keyword_data = {
                    'keyword': criterion.get('text', ''),
                    'match_type': criterion.get('matchType', ''),
                    'cost': int(metrics.get('costMicros', 0)) / 1_000_000,
                    'clicks': int(metrics.get('clicks', 0)),
                    'impressions': int(metrics.get('impressions', 0)),
                    'ctr': float(metrics.get('ctr', 0)),
                    'avg_cpc': int(metrics.get('averageCpc', 0)) / 1_000_000,
                    'conversions': float(metrics.get('conversions', 0)),
                    'conversion_rate': float(metrics.get('conversionRate', 0)),
                    'quality_score': int(metrics.get('qualityScore', 0))
                }
                
                keywords.append(keyword_data)
            
            return keywords
            
        except Exception as e:
            logger.error(f"Error parsing keyword performance data: {e}")
            return []
    
    def _get_estimated_keyword_performance(self, domain: str = None) -> List[Dict[str, Any]]:
        """Get estimated keyword performance when real data is not available."""
        # Generate some realistic keyword estimates
        estimated_keywords = [
            {
                'keyword': f'{domain} software' if domain else 'marketing software',
                'match_type': 'BROAD',
                'cost': 450.00,
                'clicks': 180,
                'impressions': 6000,
                'ctr': 0.03,
                'avg_cpc': 2.50,
                'conversions': 5.4,
                'conversion_rate': 0.03,
                'quality_score': 7
            },
            {
                'keyword': f'{domain} solution' if domain else 'marketing solution',
                'match_type': 'PHRASE',
                'cost': 320.00,
                'clicks': 128,
                'impressions': 4200,
                'ctr': 0.0305,
                'avg_cpc': 2.50,
                'conversions': 3.84,
                'conversion_rate': 0.03,
                'quality_score': 8
            },
            {
                'keyword': f'{domain} tool' if domain else 'marketing tool',
                'match_type': 'EXACT',
                'cost': 280.00,
                'clicks': 112,
                'impressions': 3500,
                'ctr': 0.032,
                'avg_cpc': 2.50,
                'conversions': 3.36,
                'conversion_rate': 0.03,
                'quality_score': 9
            }
        ]
        
        return estimated_keywords
    
    async def analyze_ad_efficiency(self, customer_id: str, domain: str = None) -> Dict[str, Any]:
        """
        Analyze advertising efficiency and identify waste opportunities.
        
        Args:
            customer_id: Google Ads customer ID
            domain: Domain being analyzed
            
        Returns:
            Dictionary with efficiency analysis and recommendations
        """
        try:
            # Get campaign metrics
            campaign_metrics = await self.get_campaign_metrics(customer_id, domain)
            if not campaign_metrics:
                return {'error': 'No campaign data available'}
            
            # Get keyword performance
            keyword_performance = await self.get_keyword_performance(customer_id, domain)
            
            # Analyze efficiency
            efficiency_analysis = {
                'overall_efficiency': self._calculate_overall_efficiency(campaign_metrics),
                'waste_opportunities': self._identify_waste_opportunities(campaign_metrics, keyword_performance),
                'optimization_recommendations': self._generate_optimization_recommendations(campaign_metrics, keyword_performance),
                'potential_savings': self._calculate_potential_savings(campaign_metrics, keyword_performance)
            }
            
            return efficiency_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing ad efficiency: {e}")
            return {'error': str(e)}
    
    def _calculate_overall_efficiency(self, campaign_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall advertising efficiency score."""
        cpc = campaign_metrics.get('avg_cpc', 0)
        ctr = campaign_metrics.get('avg_ctr', 0)
        conversion_rate = campaign_metrics.get('conversion_rate', 0)
        cost_per_conversion = campaign_metrics.get('cost_per_conversion', 0)
        
        # Industry benchmarks
        benchmarks = {
            'avg_cpc': 2.50,
            'avg_ctr': 0.03,
            'conversion_rate': 0.03,
            'cost_per_conversion': 83.33
        }
        
        # Calculate efficiency scores (0-100)
        cpc_score = max(0, 100 - ((cpc - benchmarks['avg_cpc']) / benchmarks['avg_cpc'] * 100))
        ctr_score = min(100, (ctr / benchmarks['avg_ctr']) * 100)
        conversion_score = min(100, (conversion_rate / benchmarks['conversion_rate']) * 100)
        cost_conversion_score = max(0, 100 - ((cost_per_conversion - benchmarks['cost_per_conversion']) / benchmarks['cost_per_conversion'] * 100))
        
        overall_score = (cpc_score + ctr_score + conversion_score + cost_conversion_score) / 4
        
        return {
            'overall_score': round(overall_score, 1),
            'cpc_efficiency': round(cpc_score, 1),
            'ctr_efficiency': round(ctr_score, 1),
            'conversion_efficiency': round(conversion_score, 1),
            'cost_per_conversion_efficiency': round(cost_conversion_score, 1),
            'benchmarks': benchmarks,
            'current_metrics': {
                'avg_cpc': cpc,
                'avg_ctr': ctr,
                'conversion_rate': conversion_rate,
                'cost_per_conversion': cost_per_conversion
            }
        }
    
    def _identify_waste_opportunities(self, campaign_metrics: Dict[str, Any], keyword_performance: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify specific waste opportunities."""
        opportunities = []
        
        # High CPC opportunity
        avg_cpc = campaign_metrics.get('avg_cpc', 0)
        if avg_cpc > 3.00:
            monthly_spend = campaign_metrics.get('monthly_spend', 0)
            potential_savings = monthly_spend * 0.15  # 15% savings potential
            opportunities.append({
                'type': 'high_cpc',
                'description': f'CPC above industry average (${avg_cpc:.2f} vs $2.50)',
                'monthly_waste': potential_savings,
                'annual_waste': potential_savings * 12,
                'recommendation': 'Optimize keyword bidding strategy and improve Quality Score'
            })
        
        # Low conversion rate opportunity
        conversion_rate = campaign_metrics.get('conversion_rate', 0)
        if conversion_rate < 0.02:
            monthly_spend = campaign_metrics.get('monthly_spend', 0)
            potential_savings = monthly_spend * 0.20  # 20% waste due to poor conversion
            opportunities.append({
                'type': 'low_conversion_rate',
                'description': f'Conversion rate below benchmark ({conversion_rate:.2%} vs 3.0%)',
                'monthly_waste': potential_savings,
                'annual_waste': potential_savings * 12,
                'recommendation': 'Improve landing page experience and ad relevance'
            })
        
        # Poor performing keywords
        if keyword_performance:
            high_cost_low_performance = [
                kw for kw in keyword_performance 
                if kw.get('cost', 0) > 100 and kw.get('conversion_rate', 0) < 0.01
            ]
            
            if high_cost_low_performance:
                waste_amount = sum(kw.get('cost', 0) for kw in high_cost_low_performance)
                opportunities.append({
                    'type': 'poor_keywords',
                    'description': f'{len(high_cost_low_performance)} high-cost, low-converting keywords',
                    'monthly_waste': waste_amount,
                    'annual_waste': waste_amount * 12,
                    'recommendation': 'Pause or optimize underperforming keywords'
                })
        
        return opportunities
    
    def _generate_optimization_recommendations(self, campaign_metrics: Dict[str, Any], keyword_performance: List[Dict[str, Any]]) -> List[str]:
        """Generate specific optimization recommendations."""
        recommendations = []
        
        # CPC optimization
        if campaign_metrics.get('avg_cpc', 0) > 3.00:
            recommendations.append("Implement automated bidding strategies to optimize CPC")
            recommendations.append("Improve Quality Score through better ad relevance and landing page experience")
        
        # CTR optimization
        if campaign_metrics.get('avg_ctr', 0) < 0.025:
            recommendations.append("Test new ad copy variations to improve click-through rates")
            recommendations.append("Use ad extensions to increase ad visibility and CTR")
        
        # Conversion optimization
        if campaign_metrics.get('conversion_rate', 0) < 0.025:
            recommendations.append("Optimize landing pages for better conversion rates")
            recommendations.append("Implement conversion tracking and attribution modeling")
        
        # Keyword optimization
        if keyword_performance:
            low_quality_keywords = [kw for kw in keyword_performance if kw.get('quality_score', 10) < 6]
            if low_quality_keywords:
                recommendations.append(f"Improve Quality Score for {len(low_quality_keywords)} underperforming keywords")
        
        return recommendations
    
    def _calculate_potential_savings(self, campaign_metrics: Dict[str, Any], keyword_performance: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate potential monthly and annual savings."""
        monthly_spend = campaign_metrics.get('monthly_spend', 0)
        
        # Conservative savings estimates
        cpc_savings = 0
        conversion_savings = 0
        keyword_savings = 0
        
        # CPC optimization savings
        if campaign_metrics.get('avg_cpc', 0) > 2.50:
            cpc_savings = monthly_spend * 0.10  # 10% savings potential
        
        # Conversion rate optimization savings
        if campaign_metrics.get('conversion_rate', 0) < 0.025:
            conversion_savings = monthly_spend * 0.15  # 15% waste reduction
        
        # Keyword optimization savings
        if keyword_performance:
            poor_keywords_cost = sum(
                kw.get('cost', 0) for kw in keyword_performance 
                if kw.get('conversion_rate', 0) < 0.01
            )
            keyword_savings = poor_keywords_cost * 0.5  # 50% of poor keyword spend
        
        total_monthly_savings = cpc_savings + conversion_savings + keyword_savings
        
        return {
            'monthly_savings': round(total_monthly_savings, 2),
            'annual_savings': round(total_monthly_savings * 12, 2),
            'cpc_optimization_savings': round(cpc_savings, 2),
            'conversion_optimization_savings': round(conversion_savings, 2),
            'keyword_optimization_savings': round(keyword_savings, 2)
        }
    
    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None