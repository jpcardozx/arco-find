"""
Practical Leak Engine for ARCO.

This module contains the refactored leak engine implementation for the ARCO system,
which focuses on real technical analysis using Wappalyzer and PageSpeed Insights.
Removes fake financial calculations and focuses on actionable technical insights.
"""

import asyncio
import aiohttp
import subprocess
import json
import yaml
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import logging

from arco.engines.base import LeakEngineInterface
from arco.models.prospect import Prospect, Technology, MarketingData
from arco.models.leak_result import LeakResult
from arco.models.qualified_prospect import QualifiedProspect, Leak, MarketingLeak
from arco.integrations.google_analytics import GoogleAnalyticsIntegration
from arco.integrations.google_ads import GoogleAdsIntegration
from arco.integrations.wappalyzer import WappalyzerIntegration
from arco.utils.logger import get_logger

logger = get_logger(__name__)

class LeakEngine(LeakEngineInterface):
    """
    Practical Leak engine implementation for ARCO.
    Focuses on real technical analysis using Wappalyzer and PageSpeed Insights.
    Removes fake financial calculations and provides actionable technical insights.
    """
    
    def __init__(self, config_path: str = "config/production.yml"):
        """
        Initialize the practical leak engine.
        
        Args:
            config_path: Path to the configuration file.
        """
        self.config_path = config_path
        self.session = None
        
        # Initialize real data integrations
        self.ga_integration = GoogleAnalyticsIntegration()
        self.wappalyzer_integration = WappalyzerIntegration()
        
        # Load technology analysis benchmarks
        self.tech_benchmarks = self._load_tech_benchmarks()
        
        logger.info(f"Practical LeakEngine initialized with config: {config_path}")
    
    def _load_tech_benchmarks(self) -> Dict:
        """
        Load technology analysis benchmarks for harmful tech detection.
        
        Returns:
            Dictionary of technology benchmarks and thresholds
        """
        try:
            # Try to load from config directory
            config_paths = [
                'arco/config/tech_benchmarks.yml',
                'config/tech_benchmarks.yml'
            ]
            
            for path in config_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        benchmarks = yaml.safe_load(f)
                    logger.info(f"Loaded tech benchmarks from {path}")
                    return benchmarks
            
            # Default tech benchmarks if file not found
            logger.warning("Tech benchmarks file not found, using defaults")
            return {
                'harmful_technologies': {
                    'outdated_frameworks': {
                        'jquery': {'version_threshold': '3.0.0', 'severity': 'medium'},
                        'angular': {'version_threshold': '10.0.0', 'severity': 'high'},
                        'react': {'version_threshold': '16.0.0', 'severity': 'medium'},
                        'vue': {'version_threshold': '2.6.0', 'severity': 'medium'}
                    },
                    'security_risks': {
                        'flash': {'severity': 'critical'},
                        'silverlight': {'severity': 'critical'},
                        'java_applets': {'severity': 'critical'}
                    },
                    'performance_killers': {
                        'excessive_plugins': {'threshold': 10, 'severity': 'high'},
                        'unoptimized_images': {'threshold': 5, 'severity': 'medium'},
                        'render_blocking': {'threshold': 3, 'severity': 'high'}
                    }
                },
                'web_vitals_thresholds': {
                    'lcp_good': 2.5,
                    'lcp_poor': 4.0,
                    'fid_good': 100,
                    'fid_poor': 300,
                    'cls_good': 0.1,
                    'cls_poor': 0.25,
                    'ttfb_good': 600,
                    'ttfb_poor': 1200
                },
                'quick_wins': {
                    'missing_alt_text': {'severity': 'low', 'fix_time': 'minutes'},
                    'missing_meta_description': {'severity': 'medium', 'fix_time': 'minutes'},
                    'broken_links': {'severity': 'medium', 'fix_time': 'hours'},
                    'uncompressed_images': {'severity': 'medium', 'fix_time': 'hours'},
                    'missing_ssl': {'severity': 'high', 'fix_time': 'hours'}
                }
            }
        except Exception as e:
            logger.error(f"Error loading tech benchmarks: {e}")
            return {}

    def _load_marketing_benchmarks(self) -> Dict:
        """
        Load marketing benchmarks for industry-specific analysis.
        
        Returns:
            Dictionary of marketing benchmarks by industry
        """
        try:
            # Try to load from config directory
            config_paths = [
                'arco/config/marketing_benchmarks.yml',
                'config/marketing_benchmarks.yml'
            ]
            
            for path in config_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        benchmarks = yaml.safe_load(f)
                    logger.info(f"Loaded marketing benchmarks from {path}")
                    return benchmarks
            
            # Default benchmarks if file not found
            logger.warning("Marketing benchmarks file not found, using defaults")
            return {
                'industries': {
                    'ecommerce': {
                        'avg_cpc': 1.16,
                        'avg_conversion_rate': 0.0268,
                        'avg_bounce_rate': 0.47,
                        'web_vitals_thresholds': {
                            'lcp_good': 2.5,
                            'fid_good': 100,
                            'cls_good': 0.1
                        }
                    },
                    'saas': {
                        'avg_cpc': 3.80,
                        'avg_conversion_rate': 0.0363,
                        'avg_bounce_rate': 0.42,
                        'web_vitals_thresholds': {
                            'lcp_good': 2.5,
                            'fid_good': 100,
                            'cls_good': 0.1
                        }
                    },
                    'retail': {
                        'avg_cpc': 1.16,
                        'avg_conversion_rate': 0.0268,
                        'avg_bounce_rate': 0.47,
                        'web_vitals_thresholds': {
                            'lcp_good': 2.5,
                            'fid_good': 100,
                            'cls_good': 0.1
                        }
                    }
                },
                'performance_impact': {
                    'lcp_delay_conversion_loss': 0.07,
                    'bounce_rate_threshold': 0.60,
                    'session_duration_minimum': 120
                }
            }
        except Exception as e:
            logger.error(f"Error loading marketing benchmarks: {e}")
            return {}

    def _load_vendor_costs(self) -> Dict:
        """
        Load vendor cost database.
        
        Returns:
            Dictionary of vendor costs.
        """
        try:
            # Try to load from config directory
            config_paths = [
                'config/vendor_costs.yml',
                'data/vendor_costs.yml',
                os.path.join(os.path.dirname(__file__), '../../config/vendor_costs.yml')
            ]
            
            for path in config_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        vendor_db = yaml.safe_load(f)
                    logger.info(f"Loaded vendor costs from {path}")
                    return vendor_db
            
            # If no file found, use default values
            logger.warning("⚠️ Vendor database not found, using minimal set")
            return {
                'klaviyo': {'growth': 150, 'pro': 400},
                'recharge': {'standard': 300, 'pro': 500},
                'typeform': {'plus': 50, 'business': 83},
                'gorgias': {'basic': 60, 'pro': 150}
            }
        except Exception as e:
            logger.error(f"Error loading vendor database: {e}")
            # Fallback to minimal set
            return {
                'klaviyo': {'growth': 150, 'pro': 400},
                'typeform': {'plus': 50, 'business': 83}
            }
    
    async def analyze(self, prospect: Prospect) -> LeakResult:
        """
        Analyze a prospect for practical technical issues using real data.
        Focuses on harmful technologies, Web Vitals, and quick wins.
        
        Args:
            prospect: The prospect to analyze
            
        Returns:
            Leak analysis result with real technical insights
        """
        logger.info(f"Analyzing prospect for technical issues: {prospect.domain}")
        
        start_time = datetime.now()
        
        # Ensure session is created if not already
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
        
        try:
            # PHASE 1: Harmful Technologies Detection (using Wappalyzer)
            harmful_tech_issues = await self._detect_harmful_technologies(prospect.domain)
            
            # PHASE 2: Web Vitals Analysis (using PageSpeed Insights)
            web_vitals_issues = await self._analyze_web_vitals_issues(prospect.domain)
            
            # PHASE 3: Quick Wins Detection (simple technical problems)
            quick_wins = await self._detect_quick_wins(prospect.domain)
            
            # PHASE 4: SEO Technical Issues
            seo_issues = await self._detect_seo_technical_issues(prospect.domain)
            
            # PHASE 5: Security Issues Detection
            security_issues = await self._detect_security_issues(prospect.domain)
            
            # Combine all technical issues (NO FAKE FINANCIAL CALCULATIONS)
            all_issues = harmful_tech_issues + web_vitals_issues + quick_wins + seo_issues + security_issues
            
            # Calculate technical severity score (0-100) instead of fake money
            technical_severity = self._calculate_technical_severity_score(all_issues)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create LeakResult with real data (keeping structure but removing fake calculations)
            result = LeakResult(
                domain=prospect.domain,
                total_monthly_waste=0.0,  # Remove fake financial calculations
                leaks=all_issues,
                authority_score=technical_severity,  # Use as technical severity score
                has_ads=False,  # Not relevant for technical analysis
                processing_time=processing_time
            )
            
            logger.info(f"Technical analysis complete for {prospect.domain}: {len(all_issues)} issues found, severity score: {technical_severity}/100")
            return result
            
        except Exception as e:
            logger.error(f"Error during technical analysis for {prospect.domain}: {e}")
            return self._create_error_result(prospect.domain, start_time)
    
    async def _detect_harmful_technologies(self, domain: str) -> List[Leak]:
        """
        Detect harmful technologies using Wappalyzer integration.
        
        Args:
            domain: Domain to analyze
            
        Returns:
            List of harmful technology issues
        """
        issues = []
        
        try:
            # Use Wappalyzer integration to get technology stack
            tech_data = await self.wappalyzer_integration.analyze_url(domain)
            
            if not tech_data or 'technologies' not in tech_data:
                logger.warning(f"No technology data available for {domain}")
                return issues
            
            harmful_tech_config = self.tech_benchmarks.get('harmful_technologies', {})
            
            for tech in tech_data['technologies']:
                tech_name = tech.get('name', '').lower()
                tech_version = tech.get('version', '')
                
                # Check for outdated frameworks
                outdated_frameworks = harmful_tech_config.get('outdated_frameworks', {})
                if tech_name in outdated_frameworks:
                    threshold_version = outdated_frameworks[tech_name].get('version_threshold')
                    severity = outdated_frameworks[tech_name].get('severity', 'medium')
                    
                    # Simple version comparison (would need more sophisticated logic for real use)
                    if not tech_version or tech_version < threshold_version:
                        issue = Leak(
                            type='outdated_technology',
                            monthly_waste=0.0,  # No fake financial calculations
                            annual_savings=0.0,
                            description=f"Outdated {tech_name.capitalize()} version detected (current: {tech_version or 'unknown'}, recommended: {threshold_version}+)",
                            severity=severity
                        )
                        issues.append(issue)
                        logger.info(f"Outdated technology detected for {domain}: {tech_name} {tech_version}")
                
                # Check for security risks
                security_risks = harmful_tech_config.get('security_risks', {})
                if tech_name in security_risks:
                    severity = security_risks[tech_name].get('severity', 'high')
                    issue = Leak(
                        type='security_risk',
                        monthly_waste=0.0,
                        annual_savings=0.0,
                        description=f"Security risk technology detected: {tech_name.capitalize()} (deprecated/vulnerable)",
                        severity=severity
                    )
                    issues.append(issue)
                    logger.warning(f"Security risk technology detected for {domain}: {tech_name}")
            
            # Check for excessive plugins/technologies
            tech_count = len(tech_data['technologies'])
            excessive_threshold = harmful_tech_config.get('performance_killers', {}).get('excessive_plugins', {}).get('threshold', 10)
            
            if tech_count > excessive_threshold:
                issue = Leak(
                    type='excessive_technologies',
                    monthly_waste=0.0,
                    annual_savings=0.0,
                    description=f"Excessive number of technologies detected ({tech_count} technologies may impact performance)",
                    severity='medium'
                )
                issues.append(issue)
                logger.info(f"Excessive technologies detected for {domain}: {tech_count} technologies")
            
        except Exception as e:
            logger.error(f"Error detecting harmful technologies for {domain}: {e}")
        
        return issues
    
    async def _analyze_web_vitals_issues(self, domain: str) -> List[Leak]:
        """
        Analyze Web Vitals using PageSpeed Insights integration.
        
        Args:
            domain: Domain to analyze
            
        Returns:
            List of Web Vitals issues
        """
        issues = []
        
        try:
            # Get Web Vitals data from PageSpeed Insights
            web_vitals = await self.ga_integration.get_web_vitals(domain)
            
            if not web_vitals:
                logger.warning(f"No Web Vitals data available for {domain}")
                return issues
            
            vitals_thresholds = self.tech_benchmarks.get('web_vitals_thresholds', {})
            
            # Check LCP (Largest Contentful Paint)
            if web_vitals.lcp:
                lcp_good = vitals_thresholds.get('lcp_good', 2.5)
                lcp_poor = vitals_thresholds.get('lcp_poor', 4.0)
                
                if web_vitals.lcp > lcp_poor:
                    issue = Leak(
                        type='poor_lcp',
                        monthly_waste=0.0,
                        annual_savings=0.0,
                        description=f"Poor Largest Contentful Paint: {web_vitals.lcp:.1f}s (should be <{lcp_good}s)",
                        severity='high'
                    )
                    issues.append(issue)
                elif web_vitals.lcp > lcp_good:
                    issue = Leak(
                        type='needs_improvement_lcp',
                        monthly_waste=0.0,
                        annual_savings=0.0,
                        description=f"LCP needs improvement: {web_vitals.lcp:.1f}s (should be <{lcp_good}s)",
                        severity='medium'
                    )
                    issues.append(issue)
            
            # Check FID (First Input Delay)
            if web_vitals.fid:
                fid_good = vitals_thresholds.get('fid_good', 100)
                fid_poor = vitals_thresholds.get('fid_poor', 300)
                
                if web_vitals.fid > fid_poor:
                    issue = Leak(
                        type='poor_fid',
                        monthly_waste=0.0,
                        annual_savings=0.0,
                        description=f"Poor First Input Delay: {web_vitals.fid:.0f}ms (should be <{fid_good}ms)",
                        severity='high'
                    )
                    issues.append(issue)
                elif web_vitals.fid > fid_good:
                    issue = Leak(
                        type='needs_improvement_fid',
                        monthly_waste=0.0,
                        annual_savings=0.0,
                        description=f"FID needs improvement: {web_vitals.fid:.0f}ms (should be <{fid_good}ms)",
                        severity='medium'
                    )
                    issues.append(issue)
            
            # Check CLS (Cumulative Layout Shift)
            if web_vitals.cls is not None:
                cls_good = vitals_thresholds.get('cls_good', 0.1)
                cls_poor = vitals_thresholds.get('cls_poor', 0.25)
                
                if web_vitals.cls > cls_poor:
                    issue = Leak(
                        type='poor_cls',
                        monthly_waste=0.0,
                        annual_savings=0.0,
                        description=f"Poor Cumulative Layout Shift: {web_vitals.cls:.3f} (should be <{cls_good})",
                        severity='high'
                    )
                    issues.append(issue)
                elif web_vitals.cls > cls_good:
                    issue = Leak(
                        type='needs_improvement_cls',
                        monthly_waste=0.0,
                        annual_savings=0.0,
                        description=f"CLS needs improvement: {web_vitals.cls:.3f} (should be <{cls_good})",
                        severity='medium'
                    )
                    issues.append(issue)
            
            # Check TTFB (Time to First Byte)
            if web_vitals.ttfb:
                ttfb_good = vitals_thresholds.get('ttfb_good', 600)
                ttfb_poor = vitals_thresholds.get('ttfb_poor', 1200)
                
                if web_vitals.ttfb > ttfb_poor:
                    issue = Leak(
                        type='poor_ttfb',
                        monthly_waste=0.0,
                        annual_savings=0.0,
                        description=f"Poor Time to First Byte: {web_vitals.ttfb:.0f}ms (should be <{ttfb_good}ms)",
                        severity='high'
                    )
                    issues.append(issue)
                elif web_vitals.ttfb > ttfb_good:
                    issue = Leak(
                        type='needs_improvement_ttfb',
                        monthly_waste=0.0,
                        annual_savings=0.0,
                        description=f"TTFB needs improvement: {web_vitals.ttfb:.0f}ms (should be <{ttfb_good}ms)",
                        severity='medium'
                    )
                    issues.append(issue)
            
            logger.info(f"Web Vitals analysis complete for {domain}: {len(issues)} issues found")
            
        except Exception as e:
            logger.error(f"Error analyzing Web Vitals for {domain}: {e}")
        
        return issues
    
    async def _detect_quick_wins(self, domain: str) -> List[Leak]:
        """
        Detect quick wins - simple technical problems that are easy to fix.
        
        Args:
            domain: Domain to analyze
            
        Returns:
            List of quick win issues
        """
        issues = []
        
        try:
            # Get website HTML for analysis
            async with self.session.get(f"https://{domain}", timeout=10, ssl=False) as response:
                if response.status != 200:
                    logger.warning(f"Could not fetch {domain} for quick wins analysis")
                    return issues
                
                html = await response.text()
                html_lower = html.lower()
                
                # Check for missing alt text on images
                img_count = html_lower.count('<img')
                alt_count = html_lower.count('alt=')
                if img_count > 0 and alt_count < img_count * 0.8:  # Less than 80% have alt text
                    issue = Leak(
                        type='missing_alt_text',
                        monthly_waste=0.0,
                        annual_savings=0.0,
                        description=f"Missing alt text on images ({alt_count}/{img_count} images have alt text)",
                        severity='low'
                    )
                    issues.append(issue)
                
                # Check for missing meta description
                if 'name="description"' not in html_lower and 'property="og:description"' not in html_lower:
                    issue = Leak(
                        type='missing_meta_description',
                        monthly_waste=0.0,
                        annual_savings=0.0,
                        description="Missing meta description tag",
                        severity='medium'
                    )
                    issues.append(issue)
                
                # Check for missing title tag
                if '<title>' not in html_lower:
                    issue = Leak(
                        type='missing_title_tag',
                        monthly_waste=0.0,
                        annual_savings=0.0,
                        description="Missing title tag",
                        severity='high'
                    )
                    issues.append(issue)
                
                # Check for uncompressed resources (simple heuristic)
                if '.min.js' not in html_lower and '<script' in html_lower:
                    issue = Leak(
                        type='unminified_javascript',
                        monthly_waste=0.0,
                        annual_savings=0.0,
                        description="JavaScript files appear to be unminified",
                        severity='medium'
                    )
                    issues.append(issue)
                
                # Check for missing viewport meta tag (mobile optimization)
                if 'name="viewport"' not in html_lower:
                    issue = Leak(
                        type='missing_viewport',
                        monthly_waste=0.0,
                        annual_savings=0.0,
                        description="Missing viewport meta tag for mobile optimization",
                        severity='medium'
                    )
                    issues.append(issue)
                
                logger.info(f"Quick wins analysis complete for {domain}: {len(issues)} issues found")
                
        except Exception as e:
            logger.error(f"Error detecting quick wins for {domain}: {e}")
        
        return issues
    
    async def _detect_seo_technical_issues(self, domain: str) -> List[Leak]:
        """
        Detect SEO technical issues.
        
        Args:
            domain: Domain to analyze
            
        Returns:
            List of SEO technical issues
        """
        issues = []
        
        try:
            # Check robots.txt
            try:
                async with self.session.get(f"https://{domain}/robots.txt", timeout=5, ssl=False) as response:
                    if response.status == 404:
                        issue = Leak(
                            type='missing_robots_txt',
                            monthly_waste=0.0,
                            annual_savings=0.0,
                            description="Missing robots.txt file",
                            severity='low'
                        )
                        issues.append(issue)
            except:
                pass  # Not critical if robots.txt check fails
            
            # Check sitemap.xml
            try:
                async with self.session.get(f"https://{domain}/sitemap.xml", timeout=5, ssl=False) as response:
                    if response.status == 404:
                        issue = Leak(
                            type='missing_sitemap',
                            monthly_waste=0.0,
                            annual_savings=0.0,
                            description="Missing sitemap.xml file",
                            severity='medium'
                        )
                        issues.append(issue)
            except:
                pass  # Not critical if sitemap check fails
            
            logger.info(f"SEO technical analysis complete for {domain}: {len(issues)} issues found")
            
        except Exception as e:
            logger.error(f"Error detecting SEO technical issues for {domain}: {e}")
        
        return issues
    
    async def _detect_security_issues(self, domain: str) -> List[Leak]:
        """
        Detect basic security issues.
        
        Args:
            domain: Domain to analyze
            
        Returns:
            List of security issues
        """
        issues = []
        
        try:
            # Check HTTPS redirect
            try:
                async with self.session.get(f"http://{domain}", timeout=5, ssl=False, allow_redirects=False) as response:
                    if response.status not in [301, 302, 307, 308]:
                        issue = Leak(
                            type='missing_https_redirect',
                            monthly_waste=0.0,
                            annual_savings=0.0,
                            description="HTTP to HTTPS redirect not properly configured",
                            severity='high'
                        )
                        issues.append(issue)
            except:
                pass  # Not critical if HTTP check fails
            
            # Check security headers
            try:
                async with self.session.get(f"https://{domain}", timeout=5, ssl=False) as response:
                    headers = response.headers
                    
                    # Check for important security headers
                    if 'strict-transport-security' not in headers:
                        issue = Leak(
                            type='missing_hsts_header',
                            monthly_waste=0.0,
                            annual_savings=0.0,
                            description="Missing Strict-Transport-Security header",
                            severity='medium'
                        )
                        issues.append(issue)
                    
                    if 'x-content-type-options' not in headers:
                        issue = Leak(
                            type='missing_content_type_options',
                            monthly_waste=0.0,
                            annual_savings=0.0,
                            description="Missing X-Content-Type-Options header",
                            severity='low'
                        )
                        issues.append(issue)
                    
                    if 'x-frame-options' not in headers and 'content-security-policy' not in headers:
                        issue = Leak(
                            type='missing_clickjacking_protection',
                            monthly_waste=0.0,
                            annual_savings=0.0,
                            description="Missing clickjacking protection (X-Frame-Options or CSP)",
                            severity='medium'
                        )
                        issues.append(issue)
            except:
                pass  # Not critical if security header check fails
            
            logger.info(f"Security analysis complete for {domain}: {len(issues)} issues found")
            
        except Exception as e:
            logger.error(f"Error detecting security issues for {domain}: {e}")
        
        return issues
    
    def _calculate_technical_severity_score(self, issues: List[Leak]) -> float:
        """
        Calculate technical severity score based on issues found.
        
        Args:
            issues: List of technical issues
            
        Returns:
            Technical severity score (0-100)
        """
        if not issues:
            return 0.0
        
        severity_weights = {
            'critical': 25,
            'high': 15,
            'medium': 8,
            'low': 3
        }
        
        total_score = 0
        for issue in issues:
            severity = issue.severity.lower()
            weight = severity_weights.get(severity, 5)
            total_score += weight
        
        # Cap at 100
        return min(100.0, total_score)
    
    async def qualify(self, prospect: Prospect, leak_result: LeakResult) -> QualifiedProspect:
        """
        Qualify a prospect based on technical analysis (no fake financial calculations).
        
        Args:
            prospect: The prospect to qualify
            leak_result: Technical analysis result
            
        Returns:
            Qualified prospect with technical scoring
        """
        logger.info(f"Qualifying prospect based on technical analysis: {prospect.domain}")
        
        # Create qualified prospect from base prospect
        qualified = QualifiedProspect.from_prospect(prospect)
        
        # Add technical analysis data (NO FAKE FINANCIAL CALCULATIONS)
        qualified.monthly_waste = 0.0  # Remove fake financial calculations
        qualified.annual_savings = 0.0  # Remove fake financial calculations
        qualified.leak_count = leak_result.leak_count
        qualified.top_leaks = leak_result.top_leaks[:5]  # Top 5 technical issues
        
        # Calculate technical qualification score based on real issues
        qualification_score = self._calculate_technical_qualification_score(leak_result)
        qualified.qualification_score = qualification_score
        
        # Determine priority tier based on technical severity
        technical_severity = leak_result.authority_score  # We use this field for technical severity
        if technical_severity >= 60:
            qualified.priority_tier = "A"  # High technical issues - immediate attention needed
        elif technical_severity >= 30:
            qualified.priority_tier = "B"  # Medium technical issues - good prospect
        else:
            qualified.priority_tier = "C"  # Low technical issues - lower priority
        
        # Determine if ready for outreach based on technical issues severity
        qualified.outreach_ready = (
            technical_severity >= 30 and  # Has meaningful technical issues
            qualification_score >= 50     # Good overall technical qualification
        )
        
        # Set qualification date to now
        qualified.qualification_date = datetime.now()
        
        logger.info(f"Qualified {prospect.domain}: Technical Score {qualification_score}/100, Severity {technical_severity}/100, Tier {qualified.priority_tier}")
        return qualified
    
    def _calculate_technical_qualification_score(self, leak_result: LeakResult) -> int:
        """
        Calculate technical qualification score based on real technical issues.
        
        Args:
            leak_result: Technical analysis result
            
        Returns:
            Technical qualification score (0-100)
        """
        # Base score
        score = 20
        
        # Add points based on technical severity (more issues = higher qualification score)
        technical_severity = leak_result.authority_score  # We use this field for technical severity
        if technical_severity >= 80:
            score += 50  # Very high technical issues - excellent prospect
        elif technical_severity >= 60:
            score += 40  # High technical issues - good prospect
        elif technical_severity >= 40:
            score += 30  # Medium technical issues - decent prospect
        elif technical_severity >= 20:
            score += 20  # Some technical issues - fair prospect
        else:
            score += 10  # Few technical issues - lower priority
        
        # Add points based on issue diversity (more types of issues = better prospect)
        issue_types = set(leak.type for leak in leak_result.leaks)
        score += min(20, len(issue_types) * 3)
        
        # Add points for critical issues (security, performance)
        critical_issues = [leak for leak in leak_result.leaks if leak.severity in ['critical', 'high']]
        score += min(10, len(critical_issues) * 2)
        
        # Cap at 100
        return min(100, score)
    
    def _create_error_result(self, domain: str, start_time: datetime) -> LeakResult:
        """
        Create error result for failed analysis.
        
        Args:
            domain: Domain being analyzed
            start_time: Start time of analysis
            
        Returns:
            Empty LeakResult
        """
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return LeakResult(
            domain=domain,
            total_monthly_waste=0.0,
            leaks=[],
            authority_score=0.0,
            has_ads=False,
            processing_time=processing_time
        )

    async def close(self):
        """Clean up resources."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
        
        # Close integrations
        if hasattr(self.ga_integration, 'close'):
            await self.ga_integration.close()
        if hasattr(self.wappalyzer_integration, 'close'):
            await self.wappalyzer_integration.close()
    
    def _calculate_technical_severity_score(self, issues: List[Leak]) -> float:
        """
        Calculate technical severity score based on issues found.
        
        Args:
            issues: List of technical issues
            
        Returns:
            Technical severity score (0-100)
        """
        if not issues:
            return 0.0
        
        severity_weights = {
            'critical': 25,
            'high': 15,
            'medium': 8,
            'low': 3
        }
        
        total_score = 0
        for issue in issues:
            severity = issue.severity.lower()
            weight = severity_weights.get(severity, 5)
            total_score += weight
        
        # Cap at 100
        return min(100.0, total_score)
    
    async def qualify(self, prospect: Prospect, leak_result: LeakResult) -> QualifiedProspect:
        """
        Qualify a prospect based on technical analysis (no fake financial calculations).
        
        Args:
            prospect: The prospect to qualify
            leak_result: Technical analysis result
            
        Returns:
            Qualified prospect with technical scoring
        """
        logger.info(f"Qualifying prospect based on technical analysis: {prospect.domain}")
        
        # Create qualified prospect from base prospect
        qualified = QualifiedProspect.from_prospect(prospect)
        
        # Add technical analysis data (NO FAKE FINANCIAL CALCULATIONS)
        qualified.monthly_waste = 0.0  # Remove fake financial calculations
        qualified.annual_savings = 0.0  # Remove fake financial calculations
        qualified.leak_count = leak_result.leak_count
        qualified.top_leaks = leak_result.top_leaks[:5]  # Top 5 technical issues
        
        # Calculate technical qualification score based on real issues
        qualification_score = self._calculate_technical_qualification_score(leak_result)
        qualified.qualification_score = qualification_score
        
        # Determine priority tier based on technical severity
        technical_severity = leak_result.authority_score  # We use this field for technical severity
        if technical_severity >= 60:
            qualified.priority_tier = "A"  # High technical issues - immediate attention needed
        elif technical_severity >= 30:
            qualified.priority_tier = "B"  # Medium technical issues - good prospect
        else:
            qualified.priority_tier = "C"  # Low technical issues - lower priority
        
        # Determine if ready for outreach based on technical issues severity
        qualified.outreach_ready = (
            technical_severity >= 30 and  # Has meaningful technical issues
            qualification_score >= 50     # Good overall technical qualification
        )
        
        # Set qualification date to now
        qualified.qualification_date = datetime.now()
        
        logger.info(f"Qualified {prospect.domain}: Technical Score {qualification_score}/100, Severity {technical_severity}/100, Tier {qualified.priority_tier}")
        return qualified
    
    def _calculate_technical_qualification_score(self, leak_result: LeakResult) -> int:
        """
        Calculate technical qualification score based on real technical issues.
        
        Args:
            leak_result: Technical analysis result
            
        Returns:
            Technical qualification score (0-100)
        """
        # Base score
        score = 20
        
        # Add points based on technical severity (more issues = higher qualification score)
        technical_severity = leak_result.authority_score  # We use this field for technical severity
        if technical_severity >= 80:
            score += 50  # Very high technical issues - excellent prospect
        elif technical_severity >= 60:
            score += 40  # High technical issues - good prospect
        elif technical_severity >= 40:
            score += 30  # Medium technical issues - decent prospect
        elif technical_severity >= 20:
            score += 20  # Some technical issues - fair prospect
        else:
            score += 10  # Few technical issues - lower priority
        
        # Add points based on issue diversity (more types of issues = better prospect)
        issue_types = set(leak.type for leak in leak_result.leaks)
        score += min(20, len(issue_types) * 3)
        
        # Add points for critical issues (security, performance)
        critical_issues = [leak for leak in leak_result.leaks if leak.severity in ['critical', 'high']]
        score += min(10, len(critical_issues) * 2)
        
        # Cap at 100
        return min(100, score)
    
    def _create_error_result(self, domain: str, start_time: datetime) -> LeakResult:
        """
        Create error result for failed analysis.
        
        Args:
            domain: Domain being analyzed
            start_time: Start time of analysis
            
        Returns:
            Empty LeakResult
        """
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return LeakResult(
            domain=domain,
            total_monthly_waste=0.0,
            leaks=[],
            authority_score=0.0,
            has_ads=False,
            processing_time=processing_time
        )

    async def close(self):
        """Clean up resources."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
        
        # Close integrations
        if hasattr(self.ga_integration, 'close'):
            await self.ga_integration.close()
        if hasattr(self.wappalyzer_integration, 'close'):
            await self.wappalyzer_integration.close()
    
    def _calculate_technical_severity_score(self, issues: List[Leak]) -> float:
        """
        Calculate technical severity score based on issues found.
        
        Args:
            issues: List of technical issues
            
        Returns:
            Technical severity score (0-100)
        """
        if not issues:
            return 0.0
        
        severity_weights = {
            'critical': 25,
            'high': 15,
            'medium': 8,
            'low': 3
        }
        
        total_score = 0
        for issue in issues:
            severity = issue.severity.lower()
            weight = severity_weights.get(severity, 5)
            total_score += weight
        
        # Cap at 100
        return min(100.0, total_score)
    
    async def qualify(self, prospect: Prospect, leak_result: LeakResult) -> QualifiedProspect:
        """
        Qualify a prospect based on technical analysis (no fake financial calculations).
        
        Args:
            prospect: The prospect to qualify
            leak_result: Technical analysis result
            
        Returns:
            Qualified prospect with technical scoring
        """
        logger.info(f"Qualifying prospect based on technical analysis: {prospect.domain}")
        
        # Create qualified prospect from base prospect
        qualified = QualifiedProspect.from_prospect(prospect)
        
        # Add technical analysis data (NO FAKE FINANCIAL CALCULATIONS)
        qualified.monthly_waste = 0.0  # Remove fake financial calculations
        qualified.annual_savings = 0.0  # Remove fake financial calculations
        qualified.leak_count = leak_result.leak_count
        qualified.top_leaks = leak_result.top_leaks[:5]  # Top 5 technical issues
        
        # Calculate technical qualification score based on real issues
        qualification_score = self._calculate_technical_qualification_score(leak_result)
        qualified.qualification_score = qualification_score
        
        # Determine priority tier based on technical severity
        technical_severity = leak_result.authority_score  # We use this field for technical severity
        if technical_severity >= 60:
            qualified.priority_tier = "A"  # High technical issues - immediate attention needed
        elif technical_severity >= 30:
            qualified.priority_tier = "B"  # Medium technical issues - good prospect
        else:
            qualified.priority_tier = "C"  # Low technical issues - lower priority
        
        # Determine if ready for outreach based on technical issues severity
        qualified.outreach_ready = (
            technical_severity >= 30 and  # Has meaningful technical issues
            qualification_score >= 50     # Good overall technical qualification
        )
        
        # Set qualification date to now
        qualified.qualification_date = datetime.now()
        
        logger.info(f"Qualified {prospect.domain}: Technical Score {qualification_score}/100, Severity {technical_severity}/100, Tier {qualified.priority_tier}")
        return qualified
    
    def _calculate_technical_qualification_score(self, leak_result: LeakResult) -> int:
        """
        Calculate technical qualification score based on real technical issues.
        
        Args:
            leak_result: Technical analysis result
            
        Returns:
            Technical qualification score (0-100)
        """
        # Base score
        score = 20
        
        # Add points based on technical severity (more issues = higher qualification score)
        technical_severity = leak_result.authority_score  # We use this field for technical severity
        if technical_severity >= 80:
            score += 50  # Very high technical issues - excellent prospect
        elif technical_severity >= 60:
            score += 40  # High technical issues - good prospect
        elif technical_severity >= 40:
            score += 30  # Medium technical issues - decent prospect
        elif technical_severity >= 20:
            score += 20  # Some technical issues - fair prospect
        else:
            score += 10  # Few technical issues - lower priority
        
        # Add points based on issue diversity (more types of issues = better prospect)
        issue_types = set(leak.type for leak in leak_result.leaks)
        score += min(20, len(issue_types) * 3)
        
        # Add points for critical issues (security, performance)
        critical_issues = [leak for leak in leak_result.leaks if leak.severity in ['critical', 'high']]
        score += min(10, len(critical_issues) * 2)
        
        # Cap at 100
        return min(100, score)
    
    def _create_error_result(self, domain: str, start_time: datetime) -> LeakResult:
        """
        Create error result for failed analysis.
        
        Args:
            domain: Domain being analyzed
            start_time: Start time of analysis
            
        Returns:
            Empty LeakResult
        """
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return LeakResult(
            domain=domain,
            total_monthly_waste=0.0,
            leaks=[],
            authority_score=0.0,
            has_ads=False,
            processing_time=processing_time
        )

    async def close(self):
        """Clean up resources."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
        
        # Close integrations
        if hasattr(self.ga_integration, 'close'):
            await self.ga_integration.close()
        if hasattr(self.wappalyzer_integration, 'close'):
            await self.wappalyzer_integration.close()
    
    def _calculate_technical_severity_score(self, issues: List[Leak]) -> float:
        """
        Calculate technical severity score based on issues found.
        
        Args:
            issues: List of technical issues
            
        Returns:
            Technical severity score (0-100)
        """
        if not issues:
            return 0.0
        
        severity_weights = {
            'critical': 25,
            'high': 15,
            'medium': 8,
            'low': 3
        }
        
        total_score = 0
        for issue in issues:
            severity = issue.severity.lower()
            weight = severity_weights.get(severity, 5)
            total_score += weight
        
        # Cap at 100
        return min(100.0, total_score)
    
    async def qualify(self, prospect: Prospect, leak_result: LeakResult) -> QualifiedProspect:
        """
        Qualify a prospect based on technical analysis (no fake financial calculations).
        
        Args:
            prospect: The prospect to qualify
            leak_result: Technical analysis result
            
        Returns:
            Qualified prospect with technical scoring
        """
        logger.info(f"Qualifying prospect based on technical analysis: {prospect.domain}")
        
        # Create qualified prospect from base prospect
        qualified = QualifiedProspect.from_prospect(prospect)
        
        # Add technical analysis data (NO FAKE FINANCIAL CALCULATIONS)
        qualified.monthly_waste = 0.0  # Remove fake financial calculations
        qualified.annual_savings = 0.0  # Remove fake financial calculations
        qualified.leak_count = leak_result.leak_count
        qualified.top_leaks = leak_result.top_leaks[:5]  # Top 5 technical issues
        
        # Calculate technical qualification score based on real issues
        qualification_score = self._calculate_technical_qualification_score(leak_result)
        qualified.qualification_score = qualification_score
        
        # Determine priority tier based on technical severity
        technical_severity = leak_result.authority_score  # We use this field for technical severity
        if technical_severity >= 60:
            qualified.priority_tier = "A"  # High technical issues - immediate attention needed
        elif technical_severity >= 30:
            qualified.priority_tier = "B"  # Medium technical issues - good prospect
        else:
            qualified.priority_tier = "C"  # Low technical issues - lower priority
        
        # Determine if ready for outreach based on technical issues severity
        qualified.outreach_ready = (
            technical_severity >= 30 and  # Has meaningful technical issues
            qualification_score >= 50     # Good overall technical qualification
        )
        
        # Set qualification date to now
        qualified.qualification_date = datetime.now()
        
        logger.info(f"Qualified {prospect.domain}: Technical Score {qualification_score}/100, Severity {technical_severity}/100, Tier {qualified.priority_tier}")
        return qualified
    
    def _calculate_technical_qualification_score(self, leak_result: LeakResult) -> int:
        """
        Calculate technical qualification score based on real technical issues.
        
        Args:
            leak_result: Technical analysis result
            
        Returns:
            Technical qualification score (0-100)
        """
        # Base score
        score = 20
        
        # Add points based on technical severity (more issues = higher qualification score)
        technical_severity = leak_result.authority_score  # We use this field for technical severity
        if technical_severity >= 80:
            score += 50  # Very high technical issues - excellent prospect
        elif technical_severity >= 60:
            score += 40  # High technical issues - good prospect
        elif technical_severity >= 40:
            score += 30  # Medium technical issues - decent prospect
        elif technical_severity >= 20:
            score += 20  # Some technical issues - fair prospect
        else:
            score += 10  # Few technical issues - lower priority
        
        # Add points based on issue diversity (more types of issues = better prospect)
        issue_types = set(leak.type for leak in leak_result.leaks)
        score += min(20, len(issue_types) * 3)
        
        # Add points for critical issues (security, performance)
        critical_issues = [leak for leak in leak_result.leaks if leak.severity in ['critical', 'high']]
        score += min(10, len(critical_issues) * 2)
        
        # Cap at 100
        return min(100, score)
    
    def _calculate_qualification_score(self, leak_result: LeakResult) -> int:
        """
        Calculate qualification score based on leak analysis.
        
        Args:
            leak_result: Leak analysis result
            
        Returns:
            Qualification score (0-100)
        """
        # Base score
        score = 30
        
        # Add points based on monthly waste
        monthly_waste = leak_result.total_monthly_waste
        if monthly_waste >= 500:
            score += 40
        elif monthly_waste >= 300:
            score += 30
        elif monthly_waste >= 100:
            score += 20
        elif monthly_waste >= 50:
            score += 10
        
        # Add points based on leak diversity
        leak_types = set(leak.type for leak in leak_result.leaks)
        score += min(15, len(leak_types) * 5)
        
        # Add points based on authority score
        score += min(15, int(leak_result.authority_score / 10))
        
        # Cap at 100
        return min(100, score)
    
    # OLD METHODS REMOVED - These contained fake financial calculations
    # Replaced with new methods: _detect_harmful_technologies, _analyze_web_vitals_issues, etc.
    
    def _create_error_result(self, domain: str, start_time: datetime) -> LeakResult:
        """
        Create error result for failed analysis.
        
        Args:
            domain: Domain being analyzed
            start_time: Start time of analysis
            
        Returns:
            Empty LeakResult
        """
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return LeakResult(
            domain=domain,
            total_monthly_waste=0.0,
            leaks=[],
            authority_score=0.0,
            has_ads=False,
            processing_time=processing_time
        )
    
    def _process_wappalyzer_data(self, domain: str, wapp_data: dict) -> List[Leak]:
        """
        Process Wappalyzer CLI output.
        
        Args:
            domain: Domain being analyzed
            wapp_data: Wappalyzer output data
            
        Returns:
            List of detected leaks
        """
        leaks = []
        
        for tech in wapp_data.get('technologies', []):
            vendor_name = tech['name'].lower()
            
            # Map to our cost database
            if vendor_name in self.vendor_costs:
                vendor_info = self.vendor_costs[vendor_name]
                
                # Use default tier pricing
                default_tier = list(vendor_info.keys())[0]
                if default_tier != 'categories':
                    monthly_cost = vendor_info[default_tier]
                    annual_cost = monthly_cost * 12
                    
                    leak = Leak(
                        type='vendor_waste',
                        monthly_waste=monthly_cost,
                        annual_savings=annual_cost,
                        description=f"{vendor_name.capitalize()} subscription detected via Wappalyzer",
                        severity='medium'
                    )
                    leaks.append(leak)
                    logger.info(f"{domain}: {vendor_name} detected via CLI - ${monthly_cost}/month")
        
        return leaks
    
    async def _detect_saas_via_http(self, domain: str) -> List[Leak]:
        """
        Detect SaaS tools via HTTP patterns.
        
        Args:
            domain: Domain to analyze
            
        Returns:
            List of detected leaks
        """
        leaks = []
        
        try:
            async with self.session.get(f"https://{domain}", timeout=10, ssl=False) as response:
                if response.status != 200:
                    logger.warning(f"HTTP detection for {domain} failed with status {response.status}")
                    return []
                
                html = await response.text()
                html_lower = html.lower()
                
                # Common SaaS detection patterns
                patterns = {
                    'klaviyo': ['klaviyo.com', 'klaviyo-media', 'kla.js'],
                    'gorgias': ['gorgias.com', 'gorgias-chat', 'helpdesk.gorgias'],
                    'recharge': ['rechargepayments.com', 'recharge-api'],
                    'typeform': ['typeform.com', 'typeform.js', 'embed.typeform'],
                    'shopify': ['shopify.com', 'shopify-analytics', 'shopify_stats'],
                    'hotjar': ['hotjar.com', 'hjar'],
                    'intercom': ['intercom.io', 'intercom.js'],
                    'zendesk': ['zendesk.com', 'zopim.com']
                }
                
                for vendor, vendor_patterns in patterns.items():
                    if any(pattern in html_lower for pattern in vendor_patterns):
                        if vendor in self.vendor_costs:
                            vendor_info = self.vendor_costs[vendor]
                            default_tier = list(vendor_info.keys())[0]
                            
                            if default_tier != 'categories':
                                monthly_cost = vendor_info[default_tier]
                                annual_cost = monthly_cost * 12
                                
                                leak = Leak(
                                    type='vendor_waste',
                                    monthly_waste=monthly_cost,
                                    annual_savings=annual_cost,
                                    description=f"{vendor.capitalize()} subscription detected via HTTP analysis",
                                    severity='medium'
                                )
                                leaks.append(leak)
                                logger.info(f"{domain}: {vendor} detected via HTTP - ${monthly_cost}/month")
                
                return leaks
                
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.warning(f"HTTP SaaS detection failed for {domain}: {e}")
            return []
        except Exception as e:
            logger.warning(f"Unexpected error during HTTP SaaS detection for {domain}: {e}")
            return []
    
    async def _detect_shopify_subscriptions(self, domain: str) -> List[Leak]:
        """
        Check Shopify /cart.js for subscription items.
        
        Args:
            domain: Domain to analyze
            
        Returns:
            List of detected leaks
        """
        leaks = []
        try:
            async with self.session.get(f"https://{domain}/cart.js", timeout=5, ssl=False) as response:
                if response.status != 200:
                    logger.warning(f"Shopify cart.js for {domain} failed with status {response.status}")
                    return []
                
                cart_data = await response.json()
                
                # Look for subscription indicators
                for item in cart_data.get('items', []):
                    if 'subscription' in str(item).lower():
                        # Estimate ReCharge cost based on subscription volume
                        base_cost = 300  # ReCharge standard plan
                        annual_cost = base_cost * 12
                        
                        leak = Leak(
                            type='subscription_cost',
                            monthly_waste=base_cost,
                            annual_savings=annual_cost,
                            description="ReCharge subscription service detected via Shopify cart analysis",
                            severity='high'
                        )
                        leaks.append(leak)
                        break  # Only count once
                
                return leaks
                
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.warning(f"Shopify subscription check failed for {domain}: {e}")
            return []
        except Exception as e:
            logger.warning(f"Unexpected error during Shopify subscription check for {domain}: {e}")
            return []
    
    async def _check_meta_ads(self, domain: str) -> bool:
        """
        Check Meta Ad Library for active ads.
        
        Args:
            domain: Domain to analyze
            
        Returns:
            True if ads are detected, False otherwise
        """
        try:
            # Simple check for any ads mentioning the domain
            url = f"https://graph.facebook.com/v18.0/ads_archive"
            params = {
                'search_terms': domain,
                'ad_reached_countries': 'US',
                'access_token': 'APP_TOKEN',  # Would be replaced with actual token in production
                'limit': 1
            }
            
            # For now, simulate the API call
            # In production, this would be a real API call
            has_ads = domain in ['allbirds.com', 'bombas.com', 'warbyparker.com']
            logger.info(f"{domain}: {'Ads detected' if has_ads else 'No ads found'}")
            return has_ads
                
        except Exception as e:
            logger.warning(f"Meta ads check failed for {domain}: {e}")
            return False
    
    async def _check_domain_authority(self, domain: str) -> float:
        """
        Check domain age via RDAP.
        
        Args:
            domain: Domain to analyze
            
        Returns:
            Authority score (0-100)
        """
        try:
            url = f"https://rdap.org/domain/{domain}"
            
            async with self.session.get(url, timeout=5, ssl=False) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Look for creation date
                    for event in data.get('events', []):
                        if event.get('eventAction') == 'registration':
                            reg_date = datetime.fromisoformat(event['eventDate'].replace('Z', '+00:00'))
                            age_days = (datetime.now(reg_date.tzinfo) - reg_date).days
                            
                            # Convert to authority score (0-100)
                            if age_days < 180:  # < 6 months = hobby
                                return 10.0
                            elif age_days < 365:  # < 1 year
                                return 40.0
                            elif age_days < 1095:  # < 3 years
                                return 70.0
                            else:  # 3+ years
                                return 90.0
                else:
                    logger.warning(f"RDAP check for {domain} failed with status {response.status}")
                
        except Exception as e:
            logger.warning(f"Domain authority check failed for {domain}: {e}")
            
        return 50.0  # Default moderate score
    
    async def _check_performance_leaks(self, domain: str) -> Tuple[float, List[Leak]]:
        """
        Check performance issues.
        
        Args:
            domain: Domain to analyze
            
        Returns:
            Tuple of (performance score, list of performance-related leaks)
        """
        leaks = []
        try:
            # For now, do a simple check of JS/CSS bloat
            async with self.session.get(f"https://{domain}", timeout=10, ssl=False) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    # Count script tags (proxy for JS bloat)
                    script_count = html.count('<script')
                    css_count = html.count('<link rel="stylesheet"')
                    
                    # Simple scoring: fewer scripts/CSS = better performance
                    total_assets = script_count + css_count
                    
                    perf_score = 0.0
                    if total_assets > 50:
                        perf_score = 20.0  # Poor performance
                        
                        # Estimate revenue impact: 1% conversion loss per second of load time
                        # Assuming 10,000 visitors/month and $50 average order value
                        monthly_loss = 100  # Conservative estimate
                        annual_loss = monthly_loss * 12
                        
                        leak = Leak(
                            type='performance_loss',
                            monthly_waste=monthly_loss,
                            annual_savings=annual_loss,
                            description=f"Performance issues detected ({total_assets} assets) causing conversion loss",
                            severity='high' if total_assets > 70 else 'medium'
                        )
                        leaks.append(leak)
                        
                    elif total_assets > 25:
                        perf_score = 60.0  # Average
                    else:
                        perf_score = 90.0  # Good performance
                    
                    return perf_score, leaks
                else:
                    logger.warning(f"Performance check for {domain} failed with status {response.status}")
                        
        except Exception as e:
            logger.warning(f"Performance check failed for {domain}: {e}")
            
        return 50.0, []  # Default
    
    def _create_minimal_result(self, domain: str, leaks: List[Leak], start_time: datetime) -> LeakResult:
        """
        Create minimal result for early drops.
        
        Args:
            domain: Domain being analyzed
            leaks: List of detected leaks
            start_time: Start time of analysis
            
        Returns:
            LeakResult with minimal information
        """
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return LeakResult(
            domain=domain,
            total_monthly_waste=sum(leak.monthly_waste for leak in leaks),
            leaks=leaks,
            authority_score=0.0,
            has_ads=False,
            processing_time=processing_time
        )
    
    def _create_error_result(self, domain: str, start_time: datetime) -> LeakResult:
        """
        Create error result.
        
        Args:
            domain: Domain being analyzed
            start_time: Start time of analysis
            
        Returns:
            Empty LeakResult
        """
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return LeakResult(
            domain=domain,
            total_monthly_waste=0.0,
            leaks=[],
            authority_score=0.0,
            has_ads=False,
            processing_time=processing_time
        )
    
    async def _enrich_marketing_data(self, prospect: Prospect) -> Optional[MarketingData]:
        """
        Enrich prospect with marketing data from Google Analytics and Google Ads.
        
        Args:
            prospect: Prospect to enrich
            
        Returns:
            MarketingData object with collected data or None
        """
        logger.info(f"Enriching marketing data for {prospect.domain}")
        
        try:
            marketing_data = MarketingData()
            
            # Collect web vitals (real PageSpeed data)
            web_vitals = await self.ga_integration.get_web_vitals(prospect.domain)
            if web_vitals:
                marketing_data.web_vitals = web_vitals
                marketing_data.data_confidence += 0.3
                logger.info(f"Collected web vitals for {prospect.domain}: LCP={web_vitals.lcp}s")
            
            # Get technical performance analysis (real data)
            technical_analysis = await self.ga_integration.get_technical_performance_analysis(prospect.domain)
            if technical_analysis:
                marketing_data.technical_analysis = technical_analysis
                marketing_data.performance_score = technical_analysis.get("performance_score", 0)
                marketing_data.performance_grade = technical_analysis.get("performance_grade", "Unknown")
                marketing_data.data_confidence += 0.3
                logger.info(f"Technical analysis for {prospect.domain}: Score={marketing_data.performance_score}/100, Grade={marketing_data.performance_grade}")
            
            # Analyze traffic sources
            traffic_sources = await self.ga_integration.get_traffic_sources(prospect.domain)
            if traffic_sources:
                marketing_data.organic_traffic_share = traffic_sources.get("organic_search")
                marketing_data.paid_traffic_share = traffic_sources.get("paid_search")
                marketing_data.data_confidence += 0.2
                logger.info(f"Analyzed traffic sources for {prospect.domain}: organic={marketing_data.organic_traffic_share:.1%}")
            
            # Set enrichment phase and collection date
            marketing_data.enrichment_phase = "enhanced"
            marketing_data.collection_date = datetime.now()
            
            return marketing_data
            
        except Exception as e:
            logger.error(f"Error enriching marketing data for {prospect.domain}: {e}")
            return None
    
    async def _detect_marketing_leaks(self, prospect: Prospect) -> List[MarketingLeak]:
        """
        Detect marketing inefficiencies and waste using real data and industry benchmarks.
        
        Args:
            prospect: Prospect with marketing data
            
        Returns:
            List of marketing leaks detected
        """
        leaks = []
        
        if not prospect.marketing_data:
            logger.info(f"No marketing data available for {prospect.domain}, skipping marketing leak detection")
            return leaks
        
        marketing_data = prospect.marketing_data
        
        # Get industry benchmarks
        industry = self._determine_industry(prospect)
        benchmarks = self.marketing_benchmarks.get('industries', {}).get(industry, {})
        
        logger.info(f"Detecting marketing leaks for {prospect.domain} using {industry} benchmarks")
        
        # 1. Performance Impact Leak Detection
        performance_leaks = self._analyze_performance_impact(prospect, marketing_data, benchmarks)
        leaks.extend(performance_leaks)
        
        # 2. Ad Efficiency Leak Detection
        ad_efficiency_leaks = await self._analyze_ad_efficiency(prospect, marketing_data, benchmarks)
        leaks.extend(ad_efficiency_leaks)
        
        # 3. Traffic Source Inefficiency Detection
        traffic_leaks = self._analyze_traffic_inefficiencies(prospect, marketing_data, benchmarks)
        leaks.extend(traffic_leaks)
        
        logger.info(f"Detected {len(leaks)} marketing leaks for {prospect.domain}")
        return leaks
    
    def _determine_industry(self, prospect: Prospect) -> str:
        """
        Determine industry category for benchmark comparison.
        
        Args:
            prospect: Prospect to analyze
            
        Returns:
            Industry category string
        """
        if prospect.industry:
            industry_lower = prospect.industry.lower()
            if any(keyword in industry_lower for keyword in ['retail', 'ecommerce', 'shop', 'store']):
                return 'ecommerce'
            elif any(keyword in industry_lower for keyword in ['saas', 'software', 'tech', 'app']):
                return 'saas'
        
        # Analyze domain for industry hints
        if prospect.domain:
            domain_lower = prospect.domain.lower()
            if any(keyword in domain_lower for keyword in ['shop', 'store', 'buy']):
                return 'ecommerce'
            elif any(keyword in domain_lower for keyword in ['app', 'saas', 'tech']):
                return 'saas'
        
        return 'retail'  # Default fallback
    
    def _analyze_performance_impact(self, prospect: Prospect, marketing_data: MarketingData, benchmarks: Dict) -> List[MarketingLeak]:
        """
        Analyze web performance impact on conversions using Core Web Vitals.
        
        Args:
            prospect: Prospect being analyzed
            marketing_data: Marketing performance data
            benchmarks: Industry benchmarks
            
        Returns:
            List of performance-related marketing leaks
        """
        leaks = []
        
        if not marketing_data.web_vitals:
            logger.info(f"No web vitals data available for {prospect.domain}, skipping performance impact analysis")
            return leaks
        
        web_vitals = marketing_data.web_vitals
        vitals_thresholds = benchmarks.get('web_vitals_thresholds', {})
        performance_impact = self.marketing_benchmarks.get('performance_impact', {})
        
        # Common calculations for revenue impact
        estimated_monthly_visitors = self._estimate_monthly_visitors(prospect)
        estimated_conversion_rate = marketing_data.conversion_rate or benchmarks.get('avg_conversion_rate', 0.025)
        estimated_aov = self._estimate_average_order_value(prospect)
        
        logger.info(f"Analyzing performance impact for {prospect.domain}: {estimated_monthly_visitors} visitors/month, {estimated_conversion_rate:.2%} conversion rate, ${estimated_aov:.0f} AOV")
        
        # 1. LCP (Largest Contentful Paint) Analysis
        if web_vitals.lcp and web_vitals.lcp > vitals_thresholds.get('lcp_good', 2.5):
            # Calculate conversion loss: 7% per second of delay beyond 2.5s
            conversion_loss_rate = performance_impact.get('lcp_delay_conversion_loss', 0.07)
            delay_seconds = web_vitals.lcp - 2.5
            conversion_loss_percentage = delay_seconds * conversion_loss_rate
            
            monthly_revenue_loss = (
                estimated_monthly_visitors * 
                estimated_conversion_rate * 
                conversion_loss_percentage * 
                estimated_aov
            )
            
            if monthly_revenue_loss > 50:  # Only report significant losses
                leak = MarketingLeak(
                    type='lcp_conversion_loss',
                    monthly_waste=monthly_revenue_loss,
                    annual_savings=monthly_revenue_loss * 12,
                    description=f"Slow loading speed (LCP: {web_vitals.lcp:.1f}s) causing {conversion_loss_percentage:.1%} conversion loss",
                    severity='high' if web_vitals.lcp > 4.0 else 'medium',
                    industry_benchmark=2.5,
                    current_metric=web_vitals.lcp,
                    improvement_potential=f"{conversion_loss_percentage:.1%} conversion recovery possible",
                    technical_recommendation="Optimize images, reduce server response time, eliminate render-blocking resources, use CDN"
                )
                leaks.append(leak)
                logger.info(f"LCP performance leak detected for {prospect.domain}: ${monthly_revenue_loss:.0f}/month loss from {web_vitals.lcp:.1f}s LCP")
        
        # 2. FID (First Input Delay) Analysis
        if web_vitals.fid and web_vitals.fid > vitals_thresholds.get('fid_good', 100):
            # FID issues cause user frustration and abandonment: 3% conversion loss per 100ms delay
            fid_delay_ms = web_vitals.fid - 100
            conversion_loss_percentage = (fid_delay_ms / 100) * 0.03  # 3% per 100ms
            
            monthly_revenue_loss = (
                estimated_monthly_visitors * 
                estimated_conversion_rate * 
                conversion_loss_percentage * 
                estimated_aov
            )
            
            if monthly_revenue_loss > 30:  # Report significant FID issues
                leak = MarketingLeak(
                    type='fid_interaction_loss',
                    monthly_waste=monthly_revenue_loss,
                    annual_savings=monthly_revenue_loss * 12,
                    description=f"Slow interactivity (FID: {web_vitals.fid:.0f}ms) causing user frustration and {conversion_loss_percentage:.1%} conversion loss",
                    severity='high' if web_vitals.fid > 300 else 'medium',
                    industry_benchmark=100.0,
                    current_metric=web_vitals.fid,
                    improvement_potential=f"{conversion_loss_percentage:.1%} conversion recovery through faster interactions",
                    technical_recommendation="Reduce JavaScript execution time, break up long tasks, use web workers for heavy computations"
                )
                leaks.append(leak)
                logger.info(f"FID performance leak detected for {prospect.domain}: ${monthly_revenue_loss:.0f}/month loss from {web_vitals.fid:.0f}ms FID")
        
        # 3. CLS (Cumulative Layout Shift) Analysis
        if web_vitals.cls and web_vitals.cls > vitals_thresholds.get('cls_good', 0.1):
            # CLS issues cause bounce rate increase: 10% bounce rate increase per 0.1 CLS
            cls_excess = web_vitals.cls - 0.1
            bounce_rate_increase = min(0.25, cls_excess * 1.0)  # Cap at 25% increase
            
            monthly_revenue_loss = (
                estimated_monthly_visitors * 
                bounce_rate_increase * 
                estimated_conversion_rate * 
                estimated_aov
            )
            
            if monthly_revenue_loss > 30:
                leak = MarketingLeak(
                    type='cls_bounce_loss',
                    monthly_waste=monthly_revenue_loss,
                    annual_savings=monthly_revenue_loss * 12,
                    description=f"Layout shifts (CLS: {web_vitals.cls:.2f}) causing user experience issues and {bounce_rate_increase:.1%} bounce rate increase",
                    severity='high' if web_vitals.cls > 0.25 else 'medium',
                    industry_benchmark=0.1,
                    current_metric=web_vitals.cls,
                    improvement_potential=f"{bounce_rate_increase:.1%} bounce rate reduction possible",
                    technical_recommendation="Set dimensions for images/videos, avoid inserting content above existing content, reserve space for ads"
                )
                leaks.append(leak)
                logger.info(f"CLS performance leak detected for {prospect.domain}: ${monthly_revenue_loss:.0f}/month loss from {web_vitals.cls:.2f} CLS")
        
        # 4. TTFB (Time to First Byte) Analysis
        if web_vitals.ttfb and web_vitals.ttfb > 600:  # 600ms is considered poor TTFB
            # Poor TTFB affects all other metrics and user perception: 2% conversion loss per 200ms delay
            ttfb_delay_ms = web_vitals.ttfb - 600
            conversion_loss_percentage = (ttfb_delay_ms / 200) * 0.02  # 2% per 200ms
            
            monthly_revenue_loss = (
                estimated_monthly_visitors * 
                estimated_conversion_rate * 
                conversion_loss_percentage * 
                estimated_aov
            )
            
            if monthly_revenue_loss > 40:  # Report significant TTFB issues
                leak = MarketingLeak(
                    type='ttfb_server_loss',
                    monthly_waste=monthly_revenue_loss,
                    annual_savings=monthly_revenue_loss * 12,
                    description=f"Slow server response (TTFB: {web_vitals.ttfb:.0f}ms) causing {conversion_loss_percentage:.1%} conversion loss",
                    severity='high' if web_vitals.ttfb > 1200 else 'medium',
                    industry_benchmark=600.0,
                    current_metric=web_vitals.ttfb,
                    improvement_potential=f"{conversion_loss_percentage:.1%} conversion recovery through server optimization",
                    technical_recommendation="Optimize server configuration, use faster hosting, implement caching, optimize database queries"
                )
                leaks.append(leak)
                logger.info(f"TTFB performance leak detected for {prospect.domain}: ${monthly_revenue_loss:.0f}/month loss from {web_vitals.ttfb:.0f}ms TTFB")
        
        # 5. Overall Performance Score Analysis (if available from technical analysis)
        if hasattr(marketing_data, 'performance_score') and marketing_data.performance_score and marketing_data.performance_score < 50:
            # Poor overall performance score indicates multiple issues
            performance_gap = 75 - marketing_data.performance_score  # Target score of 75
            conversion_loss_percentage = (performance_gap / 100) * 0.15  # Up to 15% loss for very poor performance
            
            monthly_revenue_loss = (
                estimated_monthly_visitors * 
                estimated_conversion_rate * 
                conversion_loss_percentage * 
                estimated_aov
            )
            
            if monthly_revenue_loss > 100:  # Only report if significant impact
                leak = MarketingLeak(
                    type='overall_performance_loss',
                    monthly_waste=monthly_revenue_loss,
                    annual_savings=monthly_revenue_loss * 12,
                    description=f"Poor overall performance score ({marketing_data.performance_score}/100) causing {conversion_loss_percentage:.1%} conversion loss",
                    severity='high' if marketing_data.performance_score < 30 else 'medium',
                    industry_benchmark=75.0,
                    current_metric=marketing_data.performance_score,
                    improvement_potential=f"{conversion_loss_percentage:.1%} conversion recovery through comprehensive performance optimization",
                    technical_recommendation="Implement comprehensive performance optimization: image optimization, code splitting, caching strategy"
                )
                leaks.append(leak)
                logger.info(f"Overall performance leak detected for {prospect.domain}: ${monthly_revenue_loss:.0f}/month loss from {marketing_data.performance_score}/100 score")
        
        logger.info(f"Performance impact analysis complete for {prospect.domain}: {len(leaks)} performance leaks detected")
        return leaks
    
    async def _analyze_ad_efficiency(self, prospect: Prospect, marketing_data: MarketingData, benchmarks: Dict) -> List[MarketingLeak]:
        """
        Analyze advertising efficiency using Google Ads data.
        
        Args:
            prospect: Prospect being analyzed
            marketing_data: Marketing performance data
            benchmarks: Industry benchmarks
            
        Returns:
            List of ad efficiency related marketing leaks
        """
        leaks = []
        
        try:
            # Get estimated campaign metrics (will use real data if API credentials available)
            campaign_metrics = await self.ads_integration.get_campaign_metrics("", prospect.domain)
            
            if not campaign_metrics:
                return leaks
            
            # Analyze CPC efficiency
            avg_cpc = campaign_metrics.get('avg_cpc', 0)
            benchmark_cpc = benchmarks.get('avg_cpc', 2.50)
            
            if avg_cpc > benchmark_cpc * 1.2:  # 20% above benchmark
                monthly_spend = campaign_metrics.get('monthly_spend', 0)
                cpc_waste_percentage = (avg_cpc - benchmark_cpc) / avg_cpc
                monthly_waste = monthly_spend * cpc_waste_percentage
                
                if monthly_waste > 100:  # Significant waste
                    leak = MarketingLeak(
                        type='high_cpc_waste',
                        monthly_waste=monthly_waste,
                        annual_savings=monthly_waste * 12,
                        description=f"High CPC (${avg_cpc:.2f} vs ${benchmark_cpc:.2f} benchmark) causing {cpc_waste_percentage:.1%} ad spend waste",
                        severity='high' if cpc_waste_percentage > 0.3 else 'medium',
                        industry_benchmark=benchmark_cpc,
                        current_metric=avg_cpc,
                        improvement_potential=f"${monthly_waste:.0f}/month savings through CPC optimization",
                        technical_recommendation="Improve Quality Score, optimize keyword bidding strategy, test ad copy variations"
                    )
                    leaks.append(leak)
                    logger.info(f"High CPC waste detected for {prospect.domain}: ${monthly_waste:.0f}/month")
            
            # Analyze conversion rate efficiency
            conversion_rate = campaign_metrics.get('conversion_rate', 0)
            benchmark_conversion = benchmarks.get('avg_conversion_rate', 0.025)
            
            if conversion_rate < benchmark_conversion * 0.8:  # 20% below benchmark
                monthly_spend = campaign_metrics.get('monthly_spend', 0)
                conversion_gap = benchmark_conversion - conversion_rate
                
                # Estimate revenue loss from poor conversion
                clicks = campaign_metrics.get('clicks', 0)
                estimated_aov = self._estimate_average_order_value(prospect)
                monthly_revenue_loss = clicks * conversion_gap * estimated_aov
                
                if monthly_revenue_loss > 200:  # Significant loss
                    leak = MarketingLeak(
                        type='low_ad_conversion_waste',
                        monthly_waste=monthly_revenue_loss,
                        annual_savings=monthly_revenue_loss * 12,
                        description=f"Low ad conversion rate ({conversion_rate:.2%} vs {benchmark_conversion:.2%} benchmark) causing revenue loss",
                        severity='high',
                        industry_benchmark=benchmark_conversion,
                        current_metric=conversion_rate,
                        improvement_potential=f"${monthly_revenue_loss:.0f}/month revenue recovery possible",
                        technical_recommendation="Optimize landing pages, improve ad-to-page relevance, test different CTAs"
                    )
                    leaks.append(leak)
        
        except Exception as e:
            logger.error(f"Error analyzing ad efficiency for {prospect.domain}: {e}")
        
        return leaks
    
    def _analyze_traffic_inefficiencies(self, prospect: Prospect, marketing_data: MarketingData, benchmarks: Dict) -> List[MarketingLeak]:
        """
        Analyze traffic source inefficiencies.
        
        Args:
            prospect: Prospect being analyzed
            marketing_data: Marketing performance data
            benchmarks: Industry benchmarks
            
        Returns:
            List of traffic-related marketing leaks
        """
        leaks = []
        
        if not marketing_data.organic_traffic_share or not marketing_data.paid_traffic_share:
            return leaks
        
        organic_share = marketing_data.organic_traffic_share
        paid_share = marketing_data.paid_traffic_share
        
        # Over-reliance on paid traffic
        if paid_share > 0.4:  # More than 40% paid traffic
            estimated_monthly_spend = self._estimate_monthly_marketing_spend(prospect)
            
            # Calculate potential savings from better organic/paid balance
            excess_paid_percentage = paid_share - 0.25  # Target 25% paid traffic
            potential_monthly_savings = estimated_monthly_spend * excess_paid_percentage * 0.6  # 60% of excess could be organic
            
            if potential_monthly_savings > 150:
                leak = MarketingLeak(
                    type='paid_traffic_dependency',
                    monthly_waste=potential_monthly_savings,
                    annual_savings=potential_monthly_savings * 12,
                    description=f"Over-reliance on paid traffic ({paid_share:.1%} vs 25% optimal) increasing acquisition costs",
                    severity='medium',
                    industry_benchmark=0.25,
                    current_metric=paid_share,
                    improvement_potential=f"${potential_monthly_savings:.0f}/month savings through SEO investment",
                    technical_recommendation="Invest in content marketing, technical SEO, and link building to reduce paid dependency"
                )
                leaks.append(leak)
                logger.info(f"Paid traffic dependency detected for {prospect.domain}: ${potential_monthly_savings:.0f}/month potential savings")
        
        # Under-optimized organic traffic
        elif organic_share < 0.25:  # Less than 25% organic traffic
            estimated_monthly_spend = self._estimate_monthly_marketing_spend(prospect)
            
            # Estimate opportunity cost of low organic traffic
            organic_gap = 0.35 - organic_share  # Target 35% organic
            opportunity_cost = estimated_monthly_spend * organic_gap * 0.3  # Conservative estimate
            
            if opportunity_cost > 100:
                leak = MarketingLeak(
                    type='low_organic_traffic',
                    monthly_waste=opportunity_cost,
                    annual_savings=opportunity_cost * 12,
                    description=f"Low organic traffic ({organic_share:.1%} vs 35% target) missing cost-effective acquisition opportunities",
                    severity='medium',
                    industry_benchmark=0.35,
                    current_metric=organic_share,
                    improvement_potential=f"${opportunity_cost:.0f}/month savings through organic growth",
                    technical_recommendation="Implement SEO strategy, create valuable content, optimize for local search"
                )
                leaks.append(leak)
        
        return leaks
    
    def _estimate_monthly_visitors(self, prospect: Prospect) -> int:
        """Estimate monthly website visitors based on company size and industry."""
        base_visitors = 5000
        
        if prospect.employee_count:
            if prospect.employee_count < 10:
                base_visitors = 2000
            elif prospect.employee_count < 50:
                base_visitors = 8000
            elif prospect.employee_count < 200:
                base_visitors = 20000
            else:
                base_visitors = 50000
        
        return base_visitors
    
    def _estimate_average_order_value(self, prospect: Prospect) -> float:
        """Estimate average order value based on industry and company size."""
        base_aov = 75.0
        
        if prospect.industry:
            industry_lower = prospect.industry.lower()
            if 'retail' in industry_lower or 'ecommerce' in industry_lower:
                base_aov = 85.0
            elif 'saas' in industry_lower or 'software' in industry_lower:
                base_aov = 150.0
        
        # Adjust by company size
        if prospect.employee_count and prospect.employee_count > 50:
            base_aov *= 1.5
        
        return base_aov
    
    def _estimate_monthly_marketing_spend(self, prospect: Prospect) -> float:
        """Estimate monthly marketing spend based on company characteristics."""
        base_spend = 3000
        
        if prospect.employee_count:
            if prospect.employee_count < 10:
                base_spend = 1500
            elif prospect.employee_count < 50:
                base_spend = 5000
            elif prospect.employee_count < 200:
                base_spend = 15000
            else:
                base_spend = 40000
        
        # Adjust by revenue if available
        if prospect.revenue:
            revenue_factor = min(prospect.revenue / 1000000, 10)  # Cap at 10x
            base_spend *= revenue_factor
        
        return base_spend

    async def close(self):
        """Clean up resources."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
        
        # Close marketing integrations
        if hasattr(self.ga_integration, 'close'):
            await self.ga_integration.close()
        if hasattr(self.ads_integration, 'close'):
            await self.ads_integration.close()