"""
⚡ PERFORMANCE ANALYSIS - STRATEGIC WEBSITE OPTIMIZATION INTELLIGENCE
Cost-efficient performance insights with actionable recommendations
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Optional
from datetime import datetime
from config.api_keys import APIConfig
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class PerformanceAnalyzer:
    """Strategic website performance analysis with cost optimization"""
    
    def __init__(self):
        self.config = APIConfig()
        self.pagespeed_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        
        # Cost control settings
        self.max_daily_analyses = 50  # Google PageSpeed API limit
        self.daily_analysis_count = 0
        self.analysis_tracking = {}
        
        # Performance thresholds (based on industry standards)
        self.performance_thresholds = {
            'excellent': 90,
            'good': 70,
            'fair': 50,
            'poor': 30
        }
        
        # Strategic performance metrics
        self.critical_metrics = [
            'first-contentful-paint',
            'largest-contentful-paint',
            'cumulative-layout-shift',
            'speed-index',
            'total-blocking-time'
        ]
    
    async def analyze_website_performance(self, website_url: str, strategy: str = 'mobile') -> Dict:
        """
        Comprehensive website performance analysis with business impact assessment
        """
        try:
            if self.daily_analysis_count >= self.max_daily_analyses:
                logger.warning(f"⚠️ Daily analysis limit reached: {self.daily_analysis_count}")
                return {'error': 'Daily analysis limit exceeded'}
            
            # Execute PageSpeed analysis
            performance_data = await self._execute_pagespeed_analysis(website_url, strategy)
            
            if 'error' in performance_data:
                return performance_data
            
            # Calculate business impact scores
            business_impact = self._calculate_business_impact(performance_data)
            
            # Generate actionable recommendations
            recommendations = self._generate_strategic_recommendations(performance_data, business_impact)
            
            # Track analysis for cost monitoring
            self._track_analysis(website_url, strategy)
            
            result = {
                'website_url': website_url,
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'strategy': strategy,
                'performance_score': performance_data.get('performance_score', 0),
                'business_impact': business_impact,
                'critical_issues': self._identify_critical_issues(performance_data),
                'recommendations': recommendations,
                'detailed_metrics': performance_data.get('metrics', {}),
                'competitive_position': self._assess_competitive_position(performance_data),
                'revenue_impact_estimate': self._estimate_revenue_impact(performance_data, business_impact)
            }
            
            logger.info(f"✅ Performance analysis completed for {website_url} - Score: {result['performance_score']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Performance analysis failed for {website_url}: {e}")
            return {'error': str(e), 'website_url': website_url}
    
    async def _execute_pagespeed_analysis(self, url: str, strategy: str) -> Dict:
        """Execute Google PageSpeed Insights analysis"""
        try:
            params = {
                'url': url,
                'key': self.config.GOOGLE_PAGESPEED_API_KEY,
                'strategy': strategy,
                'category': 'performance'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.pagespeed_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.daily_analysis_count += 1
                        return self._parse_pagespeed_results(data)
                    else:
                        error_data = await response.json() if response.content_type == 'application/json' else {}
                        logger.error(f"❌ PageSpeed API error: {response.status} - {error_data}")
                        return {'error': f'PageSpeed API error: {response.status}'}
                        
        except Exception as e:
            logger.error(f"❌ PageSpeed analysis execution failed: {e}")
            return {'error': str(e)}
    
    def _parse_pagespeed_results(self, data: Dict) -> Dict:
        """Parse PageSpeed Insights results into structured performance data"""
        try:
            lighthouse_result = data.get('lighthouseResult', {})
            categories = lighthouse_result.get('categories', {})
            audits = lighthouse_result.get('audits', {})
            
            # Extract performance score
            performance_category = categories.get('performance', {})
            performance_score = int(performance_category.get('score', 0) * 100)
            
            # Extract critical metrics
            metrics = {}
            for metric_key in self.critical_metrics:
                if metric_key in audits:
                    audit_data = audits[metric_key]
                    metrics[metric_key] = {
                        'value': audit_data.get('numericValue', 0),
                        'displayValue': audit_data.get('displayValue', ''),
                        'score': audit_data.get('score', 0),
                        'description': audit_data.get('description', '')
                    }
            
            # Extract opportunity insights
            opportunities = []
            for audit_key, audit_data in audits.items():
                if audit_data.get('details', {}).get('type') == 'opportunity':
                    opportunities.append({
                        'audit': audit_key,
                        'title': audit_data.get('title', ''),
                        'description': audit_data.get('description', ''),
                        'potential_savings': audit_data.get('numericValue', 0),
                        'impact': audit_data.get('score', 0)
                    })
            
            return {
                'performance_score': performance_score,
                'metrics': metrics,
                'opportunities': sorted(opportunities, key=lambda x: x['potential_savings'], reverse=True)[:5],
                'raw_data': data
            }
            
        except Exception as e:
            logger.error(f"❌ Error parsing PageSpeed results: {e}")
            return {'error': f'Failed to parse PageSpeed results: {e}'}
    
    def _calculate_business_impact(self, performance_data: Dict) -> Dict:
        """Calculate business impact based on performance metrics"""
        score = performance_data.get('performance_score', 0)
        metrics = performance_data.get('metrics', {})
        
        # Performance impact categories
        impact = {
            'user_experience_impact': self._calculate_ux_impact(score, metrics),
            'conversion_impact': self._calculate_conversion_impact(score, metrics),
            'seo_impact': self._calculate_seo_impact(score, metrics),
            'mobile_impact': self._calculate_mobile_impact(score, metrics),
            'overall_severity': self._calculate_overall_severity(score)
        }
        
        return impact
    
    def _calculate_ux_impact(self, score: int, metrics: Dict) -> Dict:
        """Calculate user experience impact"""
        # Based on Core Web Vitals and industry standards
        lcp = metrics.get('largest-contentful-paint', {}).get('value', 0) / 1000  # Convert to seconds
        cls = metrics.get('cumulative-layout-shift', {}).get('value', 0)
        
        ux_issues = []
        severity = 'low'
        
        if lcp > 4.0:  # Poor LCP
            ux_issues.append('Page loads too slowly, users likely to abandon')
            severity = 'high'
        elif lcp > 2.5:  # Needs improvement
            ux_issues.append('Page loading could be faster for better engagement')
            severity = 'medium'
        
        if cls > 0.25:  # Poor CLS
            ux_issues.append('Layout shifts cause frustrating user experience')
            severity = 'high'
        elif cls > 0.1:  # Needs improvement
            ux_issues.append('Some layout stability issues detected')
            severity = max(severity, 'medium') if severity != 'high' else severity
        
        if score < 50:
            ux_issues.append('Overall poor performance significantly impacts user satisfaction')
            severity = 'high'
        
        return {
            'severity': severity,
            'issues': ux_issues,
            'impact_description': f'Performance score of {score}/100 suggests {"critical" if score < 50 else "moderate" if score < 70 else "minor"} UX issues'
        }
    
    def _calculate_conversion_impact(self, score: int, metrics: Dict) -> Dict:
        """Calculate conversion rate impact"""
        # Based on Google's research on performance and conversions
        estimated_conversion_loss = 0
        
        if score < 30:
            estimated_conversion_loss = 25  # 25% conversion loss
        elif score < 50:
            estimated_conversion_loss = 15  # 15% conversion loss
        elif score < 70:
            estimated_conversion_loss = 8   # 8% conversion loss
        elif score < 90:
            estimated_conversion_loss = 3   # 3% conversion loss
        
        return {
            'estimated_conversion_loss_pct': estimated_conversion_loss,
            'severity': 'high' if estimated_conversion_loss > 15 else 'medium' if estimated_conversion_loss > 5 else 'low',
            'business_risk': f'Potential {estimated_conversion_loss}% loss in conversions due to performance issues'
        }
    
    def _calculate_seo_impact(self, score: int, metrics: Dict) -> Dict:
        """Calculate SEO impact"""
        # Google Core Web Vitals are ranking factors
        seo_issues = []
        severity = 'low'
        
        if score < 50:
            seo_issues.append('Poor performance negatively impacts search rankings')
            severity = 'high'
        elif score < 70:
            seo_issues.append('Performance improvements could boost search visibility')
            severity = 'medium'
        
        lcp = metrics.get('largest-contentful-paint', {}).get('value', 0) / 1000
        cls = metrics.get('cumulative-layout-shift', {}).get('value', 0)
        
        if lcp > 2.5 or cls > 0.1:
            seo_issues.append('Core Web Vitals need improvement for better rankings')
            severity = 'high'
        
        return {
            'severity': severity,
            'issues': seo_issues,
            'ranking_risk': 'High' if score < 50 else 'Medium' if score < 70 else 'Low'
        }
    
    def _calculate_mobile_impact(self, score: int, metrics: Dict) -> Dict:
        """Calculate mobile-specific impact"""
        # Mobile performance is critical for most businesses
        mobile_issues = []
        severity = 'low'
        
        if score < 40:
            mobile_issues.append('Critical mobile performance issues affecting user retention')
            severity = 'high'
        elif score < 60:
            mobile_issues.append('Mobile experience needs significant improvement')
            severity = 'medium'
        
        return {
            'severity': severity,
            'issues': mobile_issues,
            'mobile_optimization_score': score,
            'mobile_user_impact': 'High' if score < 50 else 'Medium' if score < 70 else 'Low'
        }
    
    def _calculate_overall_severity(self, score: int) -> str:
        """Calculate overall performance severity"""
        if score >= 90:
            return 'excellent'
        elif score >= 70:
            return 'good'
        elif score >= 50:
            return 'fair'
        elif score >= 30:
            return 'poor'
        else:
            return 'critical'
    
    def _identify_critical_issues(self, performance_data: Dict) -> List[Dict]:
        """Identify critical performance issues requiring immediate attention"""
        critical_issues = []
        metrics = performance_data.get('metrics', {})
        opportunities = performance_data.get('opportunities', [])
        
        # Check Core Web Vitals
        lcp = metrics.get('largest-contentful-paint', {}).get('value', 0) / 1000
        cls = metrics.get('cumulative-layout-shift', {}).get('value', 0)
        fcp = metrics.get('first-contentful-paint', {}).get('value', 0) / 1000
        
        if lcp > 4.0:
            critical_issues.append({
                'type': 'Core Web Vital',
                'metric': 'Largest Contentful Paint',
                'severity': 'critical',
                'current_value': f'{lcp:.2f}s',
                'target_value': '< 2.5s',
                'business_impact': 'High bounce rate, poor SEO ranking'
            })
        
        if cls > 0.25:
            critical_issues.append({
                'type': 'Core Web Vital',
                'metric': 'Cumulative Layout Shift',
                'severity': 'critical',
                'current_value': f'{cls:.3f}',
                'target_value': '< 0.1',
                'business_impact': 'Poor user experience, accidental clicks'
            })
        
        if fcp > 3.0:
            critical_issues.append({
                'type': 'Loading Performance',
                'metric': 'First Contentful Paint',
                'severity': 'high',
                'current_value': f'{fcp:.2f}s',
                'target_value': '< 1.8s',
                'business_impact': 'Users perceive site as slow'
            })
        
        # Add top opportunities as critical issues
        for opportunity in opportunities[:2]:
            if opportunity['potential_savings'] > 1000:  # More than 1 second savings
                critical_issues.append({
                    'type': 'Optimization Opportunity',
                    'metric': opportunity['title'],
                    'severity': 'high',
                    'potential_savings': f"{opportunity['potential_savings']/1000:.1f}s",
                    'business_impact': 'Significant performance improvement opportunity'
                })
        
        return critical_issues
    
    def _generate_strategic_recommendations(self, performance_data: Dict, business_impact: Dict) -> List[Dict]:
        """Generate strategic, actionable performance recommendations"""
        recommendations = []
        score = performance_data.get('performance_score', 0)
        opportunities = performance_data.get('opportunities', [])
        
        # Priority 1: Critical fixes
        if score < 50:
            recommendations.append({
                'priority': 'Critical',
                'category': 'Emergency Optimization',
                'action': 'Implement immediate performance fixes',
                'description': 'Website performance is critically poor and requires urgent attention',
                'expected_impact': 'Prevent further business loss, improve user retention',
                'timeline': 'Within 48 hours',
                'technical_focus': ['Server optimization', 'Critical resource optimization', 'Emergency caching']
            })
        
        # Priority 2: Core Web Vitals
        metrics = performance_data.get('metrics', {})
        lcp = metrics.get('largest-contentful-paint', {}).get('value', 0) / 1000
        if lcp > 2.5:
            recommendations.append({
                'priority': 'High',
                'category': 'Core Web Vitals',
                'action': 'Optimize Largest Contentful Paint',
                'description': f'LCP is {lcp:.2f}s, target is < 2.5s for good user experience',
                'expected_impact': 'Improve SEO rankings, reduce bounce rate',
                'timeline': '1-2 weeks',
                'technical_focus': ['Image optimization', 'Server response time', 'Resource loading']
            })
        
        # Priority 3: Top opportunities
        for i, opportunity in enumerate(opportunities[:3]):
            if opportunity['potential_savings'] > 500:  # Meaningful impact
                recommendations.append({
                    'priority': 'High' if i == 0 else 'Medium',
                    'category': 'Performance Optimization',
                    'action': opportunity['title'],
                    'description': opportunity['description'],
                    'expected_impact': f"Save {opportunity['potential_savings']/1000:.1f}s loading time",
                    'timeline': '1-3 weeks',
                    'potential_savings': opportunity['potential_savings']
                })
        
        # Priority 4: Strategic improvements
        if 50 <= score < 90:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Strategic Enhancement',
                'action': 'Implement advanced performance optimizations',
                'description': 'Move from good to excellent performance for competitive advantage',
                'expected_impact': 'Increase conversion rates, improve user satisfaction',
                'timeline': '2-4 weeks',
                'technical_focus': ['Advanced caching', 'CDN optimization', 'Code splitting']
            })
        
        return sorted(recommendations, key=lambda x: {'Critical': 0, 'High': 1, 'Medium': 2}.get(x['priority'], 3))
    
    def _assess_competitive_position(self, performance_data: Dict) -> Dict:
        """Assess competitive position based on performance score"""
        score = performance_data.get('performance_score', 0)
        
        if score >= 90:
            position = 'Industry Leader'
            description = 'Excellent performance puts you ahead of most competitors'
        elif score >= 70:
            position = 'Above Average'
            description = 'Good performance but room for competitive advantage'
        elif score >= 50:
            position = 'Below Average'
            description = 'Performance issues may be costing customers to competitors'
        else:
            position = 'Significantly Behind'
            description = 'Critical performance issues create major competitive disadvantage'
        
        return {
            'position': position,
            'description': description,
            'score_percentile': self._calculate_score_percentile(score),
            'competitive_risk': 'High' if score < 60 else 'Medium' if score < 80 else 'Low'
        }
    
    def _calculate_score_percentile(self, score: int) -> str:
        """Calculate rough percentile based on industry averages"""
        if score >= 90:
            return 'Top 10%'
        elif score >= 80:
            return 'Top 25%'
        elif score >= 70:
            return 'Top 50%'
        elif score >= 50:
            return 'Bottom 50%'
        else:
            return 'Bottom 25%'
    
    def _estimate_revenue_impact(self, performance_data: Dict, business_impact: Dict) -> Dict:
        """Estimate potential revenue impact from performance issues"""
        score = performance_data.get('performance_score', 0)
        conversion_impact = business_impact.get('conversion_impact', {})
        
        # Conservative estimates based on industry research
        estimated_monthly_loss_ranges = {
            'small_business': (500, 2000),      # $500-2k/month
            'medium_business': (2000, 10000),   # $2k-10k/month
            'large_business': (10000, 50000)    # $10k-50k/month
        }
        
        conversion_loss_pct = conversion_impact.get('estimated_conversion_loss_pct', 0)
        
        # Calculate potential savings from optimization
        optimization_value = {}
        for business_size, (min_loss, max_loss) in estimated_monthly_loss_ranges.items():
            potential_monthly_savings = (min_loss + max_loss) / 2 * (conversion_loss_pct / 100)
            optimization_value[business_size] = {
                'monthly_opportunity': round(potential_monthly_savings),
                'annual_opportunity': round(potential_monthly_savings * 12),
                'confidence': 'high' if score < 50 else 'medium' if score < 70 else 'low'
            }
        
        return optimization_value
    
    def _track_analysis(self, url: str, strategy: str):
        """Track analysis for cost monitoring"""
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in self.analysis_tracking:
            self.analysis_tracking[today] = []
        
        self.analysis_tracking[today].append({
            'url': url,
            'strategy': strategy,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def get_analysis_usage_stats(self) -> Dict:
        """Get current analysis usage statistics"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        return {
            'date': today,
            'analyses_used': self.daily_analysis_count,
            'daily_limit': self.max_daily_analyses,
            'remaining_analyses': self.max_daily_analyses - self.daily_analysis_count,
            'usage_percentage': (self.daily_analysis_count / self.max_daily_analyses) * 100,
            'analysis_history': self.analysis_tracking.get(today, [])
        }
    
    async def batch_analyze_websites(self, websites: List[str], max_concurrent: int = 3) -> List[Dict]:
        """
        Batch analyze multiple websites with concurrency control
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def analyze_with_semaphore(url):
            async with semaphore:
                return await self.analyze_website_performance(url)
        
        # Execute analyses with controlled concurrency
        tasks = [analyze_with_semaphore(url) for url in websites]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return successful analyses
        successful_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"❌ Batch analysis failed: {result}")
            else:
                successful_results.append(result)
        
        return successful_results
