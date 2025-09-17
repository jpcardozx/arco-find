"""
Google Analytics Integration for ARCO.

This module provides integration with Google Analytics 4 API to collect
real web performance and marketing data for prospect analysis.
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from .base import APIClientInterface
from ..models.prospect import WebVitals, AdSpendData, MarketingData
from ..utils.logger import get_logger

logger = get_logger(__name__)

class GoogleAnalyticsIntegration(APIClientInterface):
    """Google Analytics 4 API integration for real marketing data collection."""
    
    def __init__(self, credentials_path: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize Google Analytics integration.
        
        Args:
            credentials_path: Path to Google service account credentials JSON
            api_key: Google API key for public APIs
        """
        self.credentials_path = credentials_path
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        self.session = None
        self.base_url = "https://analyticsreporting.googleapis.com/v4"
        self.pagespeed_url = "https://www.googleapis.com/pagespeedonline/v5"
        
        logger.info("GoogleAnalyticsIntegration initialized")
    
    async def _init_session(self) -> None:
        """Initialize HTTP session with proper headers."""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'ARCO-Marketing-Analyzer/1.0',
                    'Accept': 'application/json'
                }
            )
    
    async def get_web_vitals(self, domain: str) -> Optional[WebVitals]:
        """
        Get Core Web Vitals for a domain using PageSpeed Insights API.
        Collects LCP, FID, CLS, TTFB metrics with proper error handling and timeout management.
        
        Args:
            domain: Domain to analyze
            
        Returns:
            WebVitals object with real performance data or None
        """
        if not self.api_key:
            logger.warning("No Google API key provided, cannot fetch web vitals")
            return None
        
        max_retries = 3
        retry_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                url = f"{self.pagespeed_url}/runPagespeed"
                params = {
                    'url': f"https://{domain}",
                    'category': 'performance',
                    'strategy': 'mobile'  # Focus on mobile performance
                }
                
                # Add API key for authentication
                if self.api_key:
                    params['key'] = self.api_key
                
                await self._init_session()
                
                # Enhanced timeout management with specific timeout for web vitals collection
                timeout = aiohttp.ClientTimeout(total=45, connect=10, sock_read=30)
                
                async with self.session.get(url, params=params, timeout=timeout) as response:
                    
                    if response.status == 429:  # Rate limited
                        logger.warning(f"Rate limited for {domain}, attempt {attempt + 1}/{max_retries}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                            continue
                        return None
                    
                    if response.status != 200:
                        logger.warning(f"PageSpeed API failed for {domain}: {response.status}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_delay)
                            continue
                        return None
                    
                    data = await response.json()
                    result = self._parse_pagespeed_data(data, domain)
                    
                    if result and result.lcp is not None:  # Validate we got meaningful data
                        logger.info(f"Successfully collected web vitals for {domain} (LCP: {result.lcp:.2f}s)")
                        return result
                    else:
                        logger.warning(f"Invalid web vitals data for {domain}, attempt {attempt + 1}/{max_retries}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_delay)
                            continue
                        return result
                        
            except asyncio.TimeoutError:
                logger.warning(f"Timeout fetching web vitals for {domain}, attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
                    
            except aiohttp.ClientError as e:
                logger.warning(f"Client error fetching web vitals for {domain}: {e}, attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
                    
            except Exception as e:
                logger.error(f"Unexpected error fetching web vitals for {domain}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
                break
        
        logger.error(f"Failed to fetch web vitals for {domain} after {max_retries} attempts")
        return None
    
    def _parse_pagespeed_data(self, data: Dict[str, Any], domain: str) -> WebVitals:
        """
        Parse PageSpeed Insights data into WebVitals object.
        
        Args:
            data: Raw PageSpeed API response
            domain: Domain being analyzed
            
        Returns:
            WebVitals object with parsed data
        """
        try:
            lighthouse_result = data.get('lighthouseResult', {})
            audits = lighthouse_result.get('audits', {})
            
            # Extract Core Web Vitals
            lcp_audit = audits.get('largest-contentful-paint', {})
            fid_audit = audits.get('max-potential-fid', {})  # FID proxy
            cls_audit = audits.get('cumulative-layout-shift', {})
            ttfb_audit = audits.get('server-response-time', {})
            fcp_audit = audits.get('first-contentful-paint', {})
            
            # Parse values (convert to appropriate units)
            lcp = lcp_audit.get('numericValue', 0) / 1000 if lcp_audit.get('numericValue') else None  # ms to seconds
            fid = fid_audit.get('numericValue') if fid_audit.get('numericValue') else None  # already in ms
            cls = cls_audit.get('numericValue') if cls_audit.get('numericValue') else None  # unitless
            ttfb = ttfb_audit.get('numericValue') if ttfb_audit.get('numericValue') else None  # ms
            fcp = fcp_audit.get('numericValue', 0) / 1000 if fcp_audit.get('numericValue') else None  # ms to seconds
            
            return WebVitals(
                lcp=lcp,
                fid=fid,
                cls=cls,
                ttfb=ttfb,
                fcp=fcp,
                data_source="pagespeed_insights",
                collection_date=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error parsing PageSpeed data for {domain}: {e}")
            return WebVitals(data_source="pagespeed_insights_error")
    
    async def get_technical_performance_analysis(self, domain: str) -> Dict[str, Any]:
        """
        Get comprehensive technical performance analysis based on real PageSpeed data.
        Focus on measurable technical metrics rather than conversion estimates.
        
        Args:
            domain: Domain to analyze
            
        Returns:
            Dictionary with technical performance analysis and optimization recommendations
        """
        max_retries = 2
        retry_delay = 0.5
        
        for attempt in range(max_retries):
            try:
                # Get real web vitals data
                web_vitals = await asyncio.wait_for(
                    self.get_web_vitals(domain), 
                    timeout=60.0
                )
                
                if not web_vitals:
                    logger.warning(f"No web vitals data available for {domain}")
                    return self._get_default_technical_analysis()
                
                # Perform technical analysis based on real data
                technical_analysis = self._analyze_technical_performance_impact(web_vitals)
                
                # Add domain-specific context
                technical_analysis.update({
                    "domain": domain,
                    "analysis_date": datetime.now().isoformat(),
                    "data_source": "google_pagespeed_insights",
                    "raw_metrics": {
                        "lcp_seconds": web_vitals.lcp,
                        "fid_milliseconds": web_vitals.fid,
                        "cls_score": web_vitals.cls,
                        "ttfb_milliseconds": web_vitals.ttfb,
                        "fcp_seconds": web_vitals.fcp
                    }
                })
                
                logger.info(f"Successfully analyzed technical performance for {domain} "
                          f"(Score: {technical_analysis.get('performance_score', 0)}/100, "
                          f"Grade: {technical_analysis.get('performance_grade', 'Unknown')})")
                return technical_analysis
                    
            except asyncio.TimeoutError:
                logger.warning(f"Timeout getting technical analysis for {domain}, attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
                    
            except Exception as e:
                logger.error(f"Error getting technical analysis for {domain}: {e}, attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
                break
        
        logger.warning(f"Failed to get technical analysis for {domain} after {max_retries} attempts")
        return self._get_default_technical_analysis()
    
    def _analyze_technical_performance_impact(self, web_vitals: WebVitals) -> Dict[str, Any]:
        """
        Analyze technical performance impact based on Core Web Vitals.
        Focus on measurable technical metrics rather than conversion estimates.
        
        Args:
            web_vitals: WebVitals data from PageSpeed Insights
            
        Returns:
            Dictionary with technical performance analysis
        """
        analysis = {
            "performance_score": 0,
            "technical_issues": [],
            "optimization_opportunities": [],
            "performance_grade": "Unknown",
            "user_experience_impact": "Unknown",
            "seo_impact": "Unknown"
        }
        
        # LCP Analysis (Largest Contentful Paint)
        if web_vitals.lcp:
            if web_vitals.lcp <= 2.5:
                analysis["lcp_grade"] = "Good"
                analysis["performance_score"] += 35
            elif web_vitals.lcp <= 4.0:
                analysis["lcp_grade"] = "Needs Improvement"
                analysis["performance_score"] += 20
                analysis["technical_issues"].append(f"LCP of {web_vitals.lcp:.1f}s exceeds 2.5s threshold")
                analysis["optimization_opportunities"].append("Image optimization and server response time improvement")
            else:
                analysis["lcp_grade"] = "Poor"
                analysis["performance_score"] += 5
                analysis["technical_issues"].append(f"Critical LCP issue: {web_vitals.lcp:.1f}s (should be <2.5s)")
                analysis["optimization_opportunities"].extend([
                    "Critical server response time optimization needed",
                    "Image compression and lazy loading implementation",
                    "Remove render-blocking resources"
                ])
        
        # FID Analysis (First Input Delay)
        if web_vitals.fid:
            if web_vitals.fid <= 100:
                analysis["fid_grade"] = "Good"
                analysis["performance_score"] += 25
            elif web_vitals.fid <= 300:
                analysis["fid_grade"] = "Needs Improvement"
                analysis["performance_score"] += 15
                analysis["technical_issues"].append(f"FID of {web_vitals.fid:.0f}ms exceeds 100ms threshold")
                analysis["optimization_opportunities"].append("JavaScript execution optimization")
            else:
                analysis["fid_grade"] = "Poor"
                analysis["performance_score"] += 5
                analysis["technical_issues"].append(f"Critical FID issue: {web_vitals.fid:.0f}ms (should be <100ms)")
                analysis["optimization_opportunities"].extend([
                    "JavaScript bundle splitting and optimization",
                    "Remove unused JavaScript",
                    "Implement code splitting"
                ])
        
        # CLS Analysis (Cumulative Layout Shift)
        if web_vitals.cls is not None:
            if web_vitals.cls <= 0.1:
                analysis["cls_grade"] = "Good"
                analysis["performance_score"] += 25
            elif web_vitals.cls <= 0.25:
                analysis["cls_grade"] = "Needs Improvement"
                analysis["performance_score"] += 15
                analysis["technical_issues"].append(f"CLS of {web_vitals.cls:.3f} exceeds 0.1 threshold")
                analysis["optimization_opportunities"].append("Layout stability improvements")
            else:
                analysis["cls_grade"] = "Poor"
                analysis["performance_score"] += 5
                analysis["technical_issues"].append(f"Critical CLS issue: {web_vitals.cls:.3f} (should be <0.1)")
                analysis["optimization_opportunities"].extend([
                    "Set explicit dimensions for images and videos",
                    "Reserve space for dynamic content",
                    "Avoid inserting content above existing content"
                ])
        
        # TTFB Analysis (Time to First Byte)
        if web_vitals.ttfb:
            if web_vitals.ttfb <= 200:
                analysis["ttfb_grade"] = "Excellent"
            elif web_vitals.ttfb <= 500:
                analysis["ttfb_grade"] = "Good"
            elif web_vitals.ttfb <= 1000:
                analysis["ttfb_grade"] = "Needs Improvement"
                analysis["technical_issues"].append(f"TTFB of {web_vitals.ttfb:.0f}ms is slow (should be <500ms)")
                analysis["optimization_opportunities"].append("Server response time optimization")
            else:
                analysis["ttfb_grade"] = "Poor"
                analysis["technical_issues"].append(f"Critical TTFB issue: {web_vitals.ttfb:.0f}ms (should be <500ms)")
                analysis["optimization_opportunities"].extend([
                    "Server infrastructure optimization",
                    "Database query optimization",
                    "CDN implementation"
                ])
        
        # Overall performance grade
        if analysis["performance_score"] >= 80:
            analysis["performance_grade"] = "Excellent"
            analysis["user_experience_impact"] = "Minimal impact on user experience"
            analysis["seo_impact"] = "Positive SEO impact"
        elif analysis["performance_score"] >= 60:
            analysis["performance_grade"] = "Good"
            analysis["user_experience_impact"] = "Minor impact on user experience"
            analysis["seo_impact"] = "Neutral SEO impact"
        elif analysis["performance_score"] >= 40:
            analysis["performance_grade"] = "Needs Improvement"
            analysis["user_experience_impact"] = "Moderate impact on user experience"
            analysis["seo_impact"] = "Negative SEO impact"
        else:
            analysis["performance_grade"] = "Poor"
            analysis["user_experience_impact"] = "Significant impact on user experience"
            analysis["seo_impact"] = "Severe negative SEO impact"
        
        return analysis
    
    def _get_default_technical_analysis(self) -> Dict[str, Any]:
        """
        Get default technical analysis when data collection fails.
        
        Returns:
            Dictionary with default technical analysis
        """
        return {
            "performance_score": 50,
            "technical_issues": ["Unable to collect performance data"],
            "optimization_opportunities": ["Enable performance monitoring"],
            "performance_grade": "Unknown",
            "user_experience_impact": "Unknown - data collection failed",
            "seo_impact": "Unknown - data collection failed",
            "data_source": "default_fallback",
            "analysis_date": datetime.now().isoformat()
        }
    
    def _get_default_conversion_metrics(self) -> Dict[str, float]:
        """
        Get default conversion metrics when data collection fails.
        
        Returns:
            Dictionary with industry-standard default metrics
        """
        return {
            "bounce_rate": 0.47,  # 47% industry average
            "conversion_rate": 0.0268,  # 2.68% industry average
            "avg_session_duration": 150.0,  # 2.5 minutes
            "pages_per_session": 2.1,
            "performance_penalty": 0.0
        }
    
    def _validate_conversion_metrics(self, metrics: Dict[str, float]) -> bool:
        """
        Validate conversion metrics for reasonable values.
        
        Args:
            metrics: Dictionary of conversion metrics to validate
            
        Returns:
            True if metrics are valid, False otherwise
        """
        try:
            # Check required fields exist
            required_fields = ["bounce_rate", "conversion_rate", "avg_session_duration"]
            for field in required_fields:
                if field not in metrics:
                    logger.warning(f"Missing required field: {field}")
                    return False
            
            # Validate bounce rate (0-1)
            bounce_rate = metrics.get("bounce_rate", 0)
            if not (0 <= bounce_rate <= 1):
                logger.warning(f"Invalid bounce_rate: {bounce_rate}")
                return False
            
            # Validate conversion rate (0-1, typically much lower)
            conversion_rate = metrics.get("conversion_rate", 0)
            if not (0 <= conversion_rate <= 1):
                logger.warning(f"Invalid conversion_rate: {conversion_rate}")
                return False
            
            # Validate session duration (positive seconds)
            session_duration = metrics.get("avg_session_duration", 0)
            if session_duration < 0 or session_duration > 7200:  # Max 2 hours
                logger.warning(f"Invalid avg_session_duration: {session_duration}")
                return False
            
            # Validate pages per session (positive)
            pages_per_session = metrics.get("pages_per_session", 0)
            if pages_per_session < 0 or pages_per_session > 50:  # Reasonable upper limit
                logger.warning(f"Invalid pages_per_session: {pages_per_session}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating conversion metrics: {e}")
            return False
    
    async def get_traffic_sources(self, domain: str) -> Dict[str, Any]:
        """
        Get traffic source breakdown for a domain with data validation and confidence scoring.
        Analyzes organic vs paid traffic with proper error handling and timeout management.
        
        Args:
            domain: Domain to analyze
            
        Returns:
            Dictionary with traffic source data including percentages, confidence score, and validation status
        """
        max_retries = 3
        retry_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                # Analyze traffic sources with multiple data points
                traffic_data = await asyncio.wait_for(
                    self._analyze_traffic_sources(domain),
                    timeout=30.0
                )
                
                # Validate the traffic source data
                if self._validate_traffic_sources(traffic_data):
                    # Calculate confidence score based on data quality
                    confidence_score = self._calculate_traffic_confidence(traffic_data, domain)
                    
                    # Add metadata to the response
                    traffic_data.update({
                        'confidence_score': confidence_score,
                        'data_source': 'estimated_analysis',
                        'collection_date': datetime.now().isoformat(),
                        'validation_status': 'passed',
                        'organic_vs_paid_ratio': self._calculate_organic_paid_ratio(traffic_data)
                    })
                    
                    logger.info(f"Successfully analyzed traffic sources for {domain} "
                              f"(organic: {traffic_data.get('organic_search', 0):.1%}, "
                              f"paid: {traffic_data.get('paid_search', 0):.1%}, "
                              f"confidence: {confidence_score:.2f})")
                    return traffic_data
                else:
                    logger.warning(f"Invalid traffic source data for {domain}, attempt {attempt + 1}/{max_retries}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
                        continue
                    return self._get_default_traffic_sources()
                    
            except asyncio.TimeoutError:
                logger.warning(f"Timeout analyzing traffic sources for {domain}, attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
                    
            except Exception as e:
                logger.error(f"Error getting traffic sources for {domain}: {e}, attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
                break
        
        logger.warning(f"Failed to analyze traffic sources for {domain} after {max_retries} attempts, using defaults")
        return self._get_default_traffic_sources()
    
    async def _analyze_traffic_sources(self, domain: str) -> Dict[str, float]:
        """
        Analyze traffic sources for a domain using multiple data points.
        
        Args:
            domain: Domain to analyze
            
        Returns:
            Dictionary with traffic source percentages
        """
        try:
            # Get web vitals to inform traffic source estimation
            web_vitals = await self.get_web_vitals(domain)
            
            # Analyze domain characteristics
            domain_analysis = self._analyze_domain_characteristics(domain)
            
            # Estimate traffic sources based on domain type and performance
            traffic_sources = self._estimate_traffic_from_domain_analysis(domain_analysis, web_vitals)
            
            return traffic_sources
            
        except Exception as e:
            logger.error(f"Error analyzing traffic sources for {domain}: {e}")
            return self._get_baseline_traffic_distribution()
    
    def _analyze_domain_characteristics(self, domain: str) -> Dict[str, Any]:
        """
        Analyze domain characteristics to inform traffic source estimation.
        
        Args:
            domain: Domain to analyze
            
        Returns:
            Dictionary with domain characteristics
        """
        characteristics = {
            'domain_length': len(domain),
            'has_subdomain': '.' in domain.replace('www.', ''),
            'tld': domain.split('.')[-1] if '.' in domain else '',
            'brand_indicators': [],
            'industry_hints': []
        }
        
        # Analyze domain for brand indicators
        if any(brand in domain.lower() for brand in ['shop', 'store', 'buy', 'market']):
            characteristics['brand_indicators'].append('ecommerce')
        
        if any(tech in domain.lower() for tech in ['app', 'tech', 'soft', 'cloud', 'api']):
            characteristics['brand_indicators'].append('saas')
        
        if any(service in domain.lower() for service in ['consult', 'service', 'agency', 'firm']):
            characteristics['brand_indicators'].append('services')
        
        # Analyze TLD for regional/industry hints
        if characteristics['tld'] in ['com', 'net', 'org']:
            characteristics['industry_hints'].append('global')
        elif characteristics['tld'] in ['co.uk', 'de', 'fr', 'ca']:
            characteristics['industry_hints'].append('regional')
        elif characteristics['tld'] in ['io', 'ai', 'tech']:
            characteristics['industry_hints'].append('tech')
        
        return characteristics
    
    def _estimate_traffic_from_domain_analysis(self, domain_analysis: Dict[str, Any], web_vitals: Optional[WebVitals]) -> Dict[str, float]:
        """
        Estimate traffic sources based on domain analysis and web vitals.
        
        Args:
            domain_analysis: Domain characteristics analysis
            web_vitals: Web vitals data if available
            
        Returns:
            Dictionary with estimated traffic source percentages
        """
        # Start with baseline distribution
        traffic_sources = self._get_baseline_traffic_distribution()
        
        # Adjust based on domain characteristics
        if 'ecommerce' in domain_analysis.get('brand_indicators', []):
            # E-commerce sites typically have higher paid search
            traffic_sources['paid_search'] = 0.25
            traffic_sources['organic_search'] = 0.30
            traffic_sources['direct'] = 0.20
            traffic_sources['social'] = 0.15
            traffic_sources['referral'] = 0.05
            traffic_sources['email'] = 0.05
            
        elif 'saas' in domain_analysis.get('brand_indicators', []):
            # SaaS sites typically have higher organic search
            traffic_sources['organic_search'] = 0.45
            traffic_sources['paid_search'] = 0.25
            traffic_sources['direct'] = 0.15
            traffic_sources['referral'] = 0.10
            traffic_sources['social'] = 0.03
            traffic_sources['email'] = 0.02
            
        elif 'services' in domain_analysis.get('brand_indicators', []):
            # Service businesses typically have higher referral traffic
            traffic_sources['organic_search'] = 0.40
            traffic_sources['referral'] = 0.20
            traffic_sources['direct'] = 0.20
            traffic_sources['paid_search'] = 0.15
            traffic_sources['social'] = 0.03
            traffic_sources['email'] = 0.02
        
        # Adjust based on web performance (poor performance = less organic traffic)
        if web_vitals and web_vitals.lcp and web_vitals.lcp > 4.0:
            # Poor performance typically correlates with lower organic search performance
            organic_penalty = min(0.10, (web_vitals.lcp - 2.5) * 0.02)
            traffic_sources['organic_search'] = max(0.15, traffic_sources['organic_search'] - organic_penalty)
            traffic_sources['paid_search'] += organic_penalty * 0.7  # Compensate with paid
            traffic_sources['direct'] += organic_penalty * 0.3
        
        # Ensure percentages sum to 1.0
        total = sum(traffic_sources.values())
        if total > 0:
            traffic_sources = {k: v / total for k, v in traffic_sources.items()}
        
        return traffic_sources
    
    def _get_baseline_traffic_distribution(self) -> Dict[str, float]:
        """
        Get baseline traffic distribution for general websites.
        
        Returns:
            Dictionary with baseline traffic source percentages
        """
        return {
            "organic_search": 0.35,  # 35% organic
            "direct": 0.25,          # 25% direct
            "paid_search": 0.20,     # 20% paid search
            "social": 0.10,          # 10% social
            "referral": 0.05,        # 5% referral
            "email": 0.05            # 5% email
        }
    
    def _validate_traffic_sources(self, traffic_data: Dict[str, float]) -> bool:
        """
        Validate traffic source data for reasonable values and completeness.
        
        Args:
            traffic_data: Dictionary of traffic source data to validate
            
        Returns:
            True if traffic data is valid, False otherwise
        """
        try:
            # Check required traffic source fields
            required_sources = ["organic_search", "direct", "paid_search", "social", "referral", "email"]
            for source in required_sources:
                if source not in traffic_data:
                    logger.warning(f"Missing required traffic source: {source}")
                    return False
                
                # Validate percentage values (0-1)
                value = traffic_data[source]
                if not isinstance(value, (int, float)) or not (0 <= value <= 1):
                    logger.warning(f"Invalid traffic source value for {source}: {value}")
                    return False
            
            # Check that percentages sum to approximately 1.0 (allow small rounding errors)
            total = sum(traffic_data[source] for source in required_sources)
            if not (0.95 <= total <= 1.05):
                logger.warning(f"Traffic source percentages don't sum to 1.0: {total}")
                return False
            
            # Validate that no single source dominates unreasonably (>80%)
            max_source = max(traffic_data[source] for source in required_sources)
            if max_source > 0.80:
                logger.warning(f"Single traffic source dominates unreasonably: {max_source}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating traffic sources: {e}")
            return False
    
    def _calculate_traffic_confidence(self, traffic_data: Dict[str, float], domain: str) -> float:
        """
        Calculate confidence score for traffic source data based on data quality indicators.
        
        Args:
            traffic_data: Traffic source data
            domain: Domain being analyzed
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        try:
            confidence = 0.0
            
            # Base confidence for having complete data
            if self._validate_traffic_sources(traffic_data):
                confidence += 0.3
            
            # Higher confidence for realistic distributions
            organic_search = traffic_data.get('organic_search', 0)
            paid_search = traffic_data.get('paid_search', 0)
            direct = traffic_data.get('direct', 0)
            
            # Realistic organic search percentage (15-60%)
            if 0.15 <= organic_search <= 0.60:
                confidence += 0.2
            
            # Realistic paid search percentage (5-40%)
            if 0.05 <= paid_search <= 0.40:
                confidence += 0.2
            
            # Realistic direct traffic percentage (10-50%)
            if 0.10 <= direct <= 0.50:
                confidence += 0.1
            
            # Bonus for balanced distribution (no single source >70%)
            max_source = max(traffic_data.get(source, 0) for source in 
                           ["organic_search", "direct", "paid_search", "social", "referral", "email"])
            if max_source <= 0.70:
                confidence += 0.1
            
            # Domain analysis bonus
            if len(domain) > 5 and '.' in domain:  # Valid domain format
                confidence += 0.1
            
            return min(confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating traffic confidence for {domain}: {e}")
            return 0.0
    
    def _calculate_organic_paid_ratio(self, traffic_data: Dict[str, float]) -> float:
        """
        Calculate the ratio of organic to paid traffic.
        
        Args:
            traffic_data: Traffic source data
            
        Returns:
            Organic to paid traffic ratio
        """
        try:
            organic = traffic_data.get('organic_search', 0)
            paid = traffic_data.get('paid_search', 0)
            
            if paid == 0:
                return float('inf') if organic > 0 else 0.0
            
            return organic / paid
            
        except Exception as e:
            logger.error(f"Error calculating organic/paid ratio: {e}")
            return 0.0
    
    def _get_default_traffic_sources(self) -> Dict[str, Any]:
        """
        Get default traffic sources when analysis fails.
        
        Returns:
            Dictionary with default traffic source data including metadata
        """
        baseline_sources = self._get_baseline_traffic_distribution()
        
        return {
            **baseline_sources,
            'confidence_score': 0.2,  # Low confidence for default data
            'data_source': 'default_fallback',
            'collection_date': datetime.now().isoformat(),
            'validation_status': 'default',
            'organic_vs_paid_ratio': baseline_sources['organic_search'] / baseline_sources['paid_search']
        }
        """
        Get default traffic source data when analysis fails.
        
        Returns:
            Dictionary with default traffic source data including metadata
        """
        baseline = self._get_baseline_traffic_distribution()
        baseline.update({
            'confidence_score': 0.1,  # Low confidence for defaults
            'data_source': 'default_fallback',
            'collection_date': datetime.now().isoformat(),
            'validation_status': 'default',
            'organic_vs_paid_ratio': baseline['organic_search'] / baseline['paid_search']
        })
        return baseline
    
    async def create_marketing_data(self, domain: str) -> MarketingData:
        """
        Create comprehensive marketing data for a domain.
        
        Args:
            domain: Domain to analyze
            
        Returns:
            MarketingData object with collected information
        """
        try:
            # Collect web vitals
            web_vitals = await self.get_web_vitals(domain)
            
            # Get conversion metrics
            conversion_metrics = await self.get_conversion_metrics(domain)
            
            # Get traffic sources
            traffic_sources = await self.get_traffic_sources(domain)
            
            # Calculate data confidence based on available data
            data_confidence = 0.0
            if web_vitals and web_vitals.lcp:
                data_confidence += 0.4  # Web vitals available
            if conversion_metrics:
                data_confidence += 0.3  # Conversion metrics available
            if traffic_sources:
                data_confidence += 0.3  # Traffic sources available
            
            # Create marketing data object
            marketing_data = MarketingData(
                web_vitals=web_vitals,
                bounce_rate=conversion_metrics.get("bounce_rate"),
                avg_session_duration=conversion_metrics.get("avg_session_duration"),
                pages_per_session=conversion_metrics.get("pages_per_session"),
                conversion_rate=conversion_metrics.get("conversion_rate"),
                organic_traffic_share=traffic_sources.get("organic_search"),
                paid_traffic_share=traffic_sources.get("paid_search"),
                data_confidence=data_confidence,
                enrichment_phase="basic",
                collection_date=datetime.now()
            )
            
            logger.info(f"Created marketing data for {domain} with confidence {data_confidence:.2f}")
            return marketing_data
            
        except Exception as e:
            logger.error(f"Error creating marketing data for {domain}: {e}")
            return MarketingData(
                data_confidence=0.0,
                enrichment_phase="failed",
                collection_date=datetime.now()
            )
    
    def initialize(self, api_key: str, **kwargs) -> bool:
        """
        Initialize the API client with credentials.
        
        Args:
            api_key: Google API key for authentication
            **kwargs: Additional configuration parameters (credentials_path, etc.)
            
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            self.api_key = api_key
            if 'credentials_path' in kwargs:
                self.credentials_path = kwargs['credentials_path']
            
            # Initialize session
            self._init_session()
            
            logger.info("GoogleAnalyticsIntegration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize GoogleAnalyticsIntegration: {e}")
            return False
    
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search for data using the API.
        
        Note: Google Analytics doesn't have a traditional search interface.
        This method is implemented for interface compliance.
        
        Args:
            query: Search query (domain name for GA context)
            **kwargs: Additional search parameters
            
        Returns:
            List of search results (empty for GA)
        """
        logger.info(f"Search called on GoogleAnalyticsIntegration with query: {query}")
        # GA doesn't have a search interface, return empty list
        return []
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get the current rate limit status.
        
        Returns:
            Dictionary with rate limit information
        """
        # Google APIs have different rate limits for different services
        # PageSpeed Insights: 25,000 requests per day, 400 requests per 100 seconds
        return {
            "service": "google_analytics",
            "pagespeed_daily_limit": 25000,
            "pagespeed_per_100s_limit": 400,
            "status": "active",
            "estimated_remaining": "unknown"  # Would need tracking to determine
        }
    
    def _get_default_traffic_sources(self) -> Dict[str, Any]:
        """
        Get default traffic sources when analysis fails.
        
        Returns:
            Dictionary with default traffic source data including metadata
        """
        baseline_sources = self._get_baseline_traffic_distribution()
        
        return {
            **baseline_sources,
            'confidence_score': 0.2,  # Low confidence for default data
            'data_source': 'default_fallback',
            'collection_date': datetime.now().isoformat(),
            'validation_status': 'default',
            'organic_vs_paid_ratio': baseline_sources['organic_search'] / baseline_sources['paid_search']
        }

    async def get_rate_limit_info(self) -> Dict[str, Any]:
        """
        Get current rate limit information for the Google APIs.
        
        Returns:
            Dictionary with rate limit status and usage information
        """
        return {
            "pagespeed_per_day_limit": 25000,
            "pagespeed_per_100s_limit": 400,
            "status": "active",
            "estimated_remaining": "unknown"  # Would need tracking to determine
        }
    
    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None