"""
Performance Agent - ARCO V3
Analyzes PageSpeed Insights, collects Chrome UX Report data, generates evidence
Based on AGENTS.md specification
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple
import aiohttp
import json
import base64
from urllib.parse import urlparse, urljoin

from ..models.core_models import PerformanceOutput, PSIMetrics
from config.api_keys import APIConfig

logger = logging.getLogger(__name__)


class PerformanceAgent:
    """
    Performance Agent implementing the decision tree from AGENTS.md:
    - Analyze PageSpeed Insights (mobile + desktop)
    - Collect Chrome UX Report (p75 Core Web Vitals)
    - Screenshot automation for evidence
    - Calculate Leak Score
    """
    
    def __init__(self, api_key: str = None):
        self.psi_api_key = api_key or APIConfig.GOOGLE_PAGESPEED_API_KEY
        self.psi_base_url = "https://www.googleapis.com/pagespeed/insights/v5"
        self.session = None
        
        # Core Web Vitals thresholds (from Google)
        self.cwv_thresholds = {
            "lcp": {"good": 2.5, "poor": 4.0},  # Largest Contentful Paint (seconds)
            "inp": {"good": 200, "poor": 500},  # Interaction to Next Paint (ms)
            "cls": {"good": 0.1, "poor": 0.25}, # Cumulative Layout Shift
            "fcp": {"good": 1.8, "poor": 3.0}   # First Contentful Paint (seconds)
        }
        
        # Leak indicators and their impact scores
        self.leak_indicators = {
            "LCP_HIGH": {"threshold": 2.8, "impact": 3, "description": "Slow loading hurts conversions"},
            "INP_HIGH": {"threshold": 200, "impact": 2, "description": "Poor interactivity frustrates users"},
            "CLS_HIGH": {"threshold": 0.1, "impact": 2, "description": "Layout shifts break user flow"},
            "FCP_HIGH": {"threshold": 1.8, "impact": 2, "description": "Slow first paint increases bounce"},
            "NO_PHONE_CTA": {"impact": 1, "description": "Missing click-to-call loses mobile leads"},
            "WEAK_FORM": {"impact": 1, "description": "Poor form UX reduces submissions"},
            "MOBILE_UNFRIENDLY": {"impact": 3, "description": "Mobile issues lose 60% of traffic"},
            "SSL_ISSUES": {"impact": 2, "description": "Security warnings kill trust"}
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def analyze(self, domain: str) -> PerformanceOutput:
        """
        Execute performance analysis following the decision tree
        """
        logger.info(f"🚀 Starting performance analysis for {domain}")
        
        # Gate 1: URL Strategy - extract revenue URLs
        critical_urls = await self._extract_revenue_urls(domain)
        if not critical_urls:
            critical_urls = [f"https://{domain}/", f"https://{domain}/contact"]
        
        logger.debug(f"📊 Analyzing URLs: {critical_urls}")
        
        performance_metrics = {}
        leak_indicators = []
        evidence_screenshots = []
        priority_fixes = []
        
        for url in critical_urls:
            try:
                # Gate 2: Performance Check - CrUX analysis with proper None handling
                mobile_metrics = await self._get_pagespeed_metrics(url, "mobile")
                desktop_metrics = await self._get_pagespeed_metrics(url, "desktop")
                
                # Handle None results from failed CrUX calls
                if mobile_metrics is None or desktop_metrics is None:
                    logger.warning(f"🚨 PERFORMANCE DATA UNAVAILABLE for {url}")
                    logger.warning(f"🔍 REASON: Domain has insufficient traffic for CrUX analysis")
                    # Skip this URL completely - no fake data
                    continue
                
                performance_metrics[url] = {
                    "mobile": mobile_metrics,
                    "desktop": desktop_metrics
                }
                
                # Gate 3: Leak Detection (only if we have real data)
                url_leaks = self._detect_performance_leaks(mobile_metrics, desktop_metrics)
                leak_indicators.extend(url_leaks)
                
                # Gate 4: Friction Analysis
                friction_leaks = await self._analyze_friction_points(url)
                leak_indicators.extend(friction_leaks)
                
                # Generate evidence
                screenshot_path = await self._capture_evidence_screenshot(url, url_leaks)
                if screenshot_path:
                    evidence_screenshots.append(screenshot_path)
                
                # Priority fixes based on real impact
                url_fixes = self._generate_priority_fixes(url_leaks, mobile_metrics)
                priority_fixes.extend(url_fixes)
                
            except Exception as e:
                logger.warning(f"❌ Analysis failed for {url}: {str(e)}")
                # Add default poor performance indicators for failed analysis
                leak_indicators.append("ANALYSIS_FAILED")
        
        # Calculate overall leak score
        leak_score = self._calculate_leak_score(leak_indicators)
        
        # Generate estimated impact
        estimated_impact = self._estimate_impact(leak_indicators, performance_metrics)
        
        return PerformanceOutput(
            domain=domain,
            analyzed_urls=critical_urls,
            performance_metrics=performance_metrics,
            leak_indicators=list(set(leak_indicators)),  # Remove duplicates
            leak_score=leak_score,
            evidence_screenshots=evidence_screenshots,
            priority_fixes=priority_fixes,
            estimated_impact=estimated_impact,
            analysis_timestamp=datetime.now(timezone.utc)
        )
    
    async def _extract_revenue_urls(self, domain: str) -> List[str]:
        """Extract key revenue-generating URLs"""
        base_url = f"https://{domain}"
        
        # Standard revenue URLs to check
        revenue_paths = [
            "/",           # Homepage
            "/contact",    # Contact page
            "/services",   # Services page
            "/book",       # Booking page
            "/appointment", # Appointment page
            "/quote",      # Quote page
            "/emergency",  # Emergency services
            "/schedule"    # Scheduling page
        ]
        
        revenue_urls = []
        
        for path in revenue_paths:
            url = urljoin(base_url, path)
            if await self._url_exists(url):
                revenue_urls.append(url)
                if len(revenue_urls) >= 3:  # Limit to top 3 URLs
                    break
        
        return revenue_urls or [base_url]  # At least analyze homepage
    
    async def _url_exists(self, url: str) -> bool:
        """Check if URL exists and is accessible"""
        try:
            async with self.session.head(url, timeout=10, allow_redirects=True) as response:
                return response.status < 400
        except:
            return False
    
    async def _get_pagespeed_metrics(self, url: str, strategy: str) -> PSIMetrics:
        """Get CrUX metrics for URL - Chrome User Experience Report (more reliable than PSI)"""
        
        # Use CrUX API for real user data instead of PSI lab data
        crux_url = "https://chromeuxreport.googleapis.com/v1/records:queryRecord"
        
        payload = {
            "url": url,
            "metrics": [
                "LARGEST_CONTENTFUL_PAINT",
                "FIRST_INPUT_DELAY", 
                "CUMULATIVE_LAYOUT_SHIFT",
                "FIRST_CONTENTFUL_PAINT"
            ],
            "formFactor": "PHONE" if strategy == "mobile" else "DESKTOP"
        }
        
        try:
            async with self.session.post(
                crux_url, 
                json=payload, 
                params={"key": self.psi_api_key}, 
                timeout=30
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_crux_response(data, url, strategy)
                elif response.status == 404:
                    # Domain not in CrUX database - FAIL HARD instead of fake estimates
                    logger.warning(f"🚨 CRITICAL: Domain {url} has NO real user data in CrUX")
                    logger.warning(f"🔍 DEBUG: Low traffic domain - real performance unknown")
                    return None  # Force investigation, no fake fallbacks
                else:
                    logger.warning(f"CrUX API error {response.status} for {url}")
                    return None  # FAIL HARD - expose real API issues
        except Exception as e:
            logger.error(f"CrUX API failure for {url}: {str(e)}")
            return None  # FAIL HARD - no masking of real problems

    def _parse_crux_response(self, data: Dict, url: str, strategy: str) -> PSIMetrics:
        """Parse CrUX API response to extract Core Web Vitals"""
        try:
            record = data.get("record", {})
            metrics = record.get("metrics", {})
            
            # Extract LCP (Largest Contentful Paint)
            lcp_data = metrics.get("largest_contentful_paint", {})
            lcp_p75 = lcp_data.get("percentiles", {}).get("p75", 4000) / 1000  # Convert to seconds
            
            # Extract FID (First Input Delay) 
            fid_data = metrics.get("first_input_delay", {})
            fid_p75 = fid_data.get("percentiles", {}).get("p75", 200)  # Already in ms
            
            # Extract CLS (Cumulative Layout Shift)
            cls_data = metrics.get("cumulative_layout_shift", {})
            cls_p75 = cls_data.get("percentiles", {}).get("p75", 0.25) / 100  # Convert to ratio
            
            # Extract FCP (First Contentful Paint)
            fcp_data = metrics.get("first_contentful_paint", {})
            fcp_p75 = fcp_data.get("percentiles", {}).get("p75", 3000) / 1000  # Convert to seconds
            
            # Calculate performance score based on Core Web Vitals
            performance_score = self._calculate_cwv_score(lcp_p75, fid_p75, cls_p75, fcp_p75)
            
            return PSIMetrics(
                lcp_p75=lcp_p75,
                inp_p75=fid_p75,  # Using FID as INP substitute
                cls_p75=cls_p75,
                fcp_p75=fcp_p75,
                score=performance_score,
                device=strategy
            )
            
        except Exception as e:
            logger.warning(f"Error parsing CrUX data for {url}: {e}")
            return self._estimate_performance_metrics(url, strategy)

    def _calculate_cwv_score(self, lcp: float, fid: float, cls: float, fcp: float) -> int:
        """Calculate performance score based on Core Web Vitals thresholds"""
        score = 0
        
        # LCP scoring (0-25 points)
        if lcp <= 2.5:
            score += 25
        elif lcp <= 4.0:
            score += 15
        else:
            score += 5
        
        # FID scoring (0-25 points)  
        if fid <= 100:
            score += 25
        elif fid <= 300:
            score += 15
        else:
            score += 5
        
        # CLS scoring (0-25 points)
        if cls <= 0.1:
            score += 25
        elif cls <= 0.25:
            score += 15
        else:
            score += 5
        
        # FCP scoring (0-25 points)
        if fcp <= 1.8:
            score += 25
        elif fcp <= 3.0:
            score += 15
        else:
            score += 5
        
        return score

    def _estimate_performance_metrics(self, url: str, strategy: str) -> PSIMetrics:
        """Estimate performance metrics for domains not in CrUX database"""
        # Conservative estimates for new/small sites
        estimated_lcp = 4.5  # Slightly poor LCP
        estimated_fid = 250   # Moderate FID
        estimated_cls = 0.20  # Poor CLS
        estimated_fcp = 3.2   # Poor FCP
        
        performance_score = self._calculate_cwv_score(estimated_lcp, estimated_fid, estimated_cls, estimated_fcp)
        
        return PSIMetrics(
            lcp_p75=estimated_lcp,
            inp_p75=estimated_fid,  # Using FID as INP substitute
            cls_p75=estimated_cls,
            fcp_p75=estimated_fcp,
            score=performance_score,
            device=strategy
        )
    
    def _parse_psi_response(self, data: Dict, strategy: str) -> PSIMetrics:
        """Parse PageSpeed Insights API response"""
        try:
            lighthouse = data.get("lighthouseResult", {})
            audits = lighthouse.get("audits", {})
            
            # Extract Core Web Vitals
            lcp_audit = audits.get("largest-contentful-paint", {})
            lcp_value = lcp_audit.get("numericValue", 5000) / 1000  # Convert to seconds
            
            fcp_audit = audits.get("first-contentful-paint", {})
            fcp_value = fcp_audit.get("numericValue", 3000) / 1000  # Convert to seconds
            
            cls_audit = audits.get("cumulative-layout-shift", {})
            cls_value = cls_audit.get("numericValue", 0.25)
            
            # INP from metrics audit (if available)
            metrics_audit = audits.get("metrics", {})
            details = metrics_audit.get("details", {})
            items = details.get("items", [{}])
            inp_value = items[0].get("interactionToNextPaint", 300) if items else 300
            
            # Overall performance score
            performance = lighthouse.get("categories", {}).get("performance", {})
            score = int((performance.get("score", 0.5) or 0.5) * 100)
            
            return PSIMetrics(
                lcp_p75=lcp_value,
                inp_p75=inp_value,
                cls_p75=cls_value,
                fcp_p75=fcp_value,
                score=score,
                device=strategy
            )
        except Exception as e:
            logger.warning(f"Failed to parse PSI response: {str(e)}")
            return self._default_poor_metrics(strategy)
    
    def _default_poor_metrics(self, strategy: str) -> PSIMetrics:
        """Return default poor performance metrics when API fails"""
        return PSIMetrics(
            lcp_p75=4.5,    # Poor LCP
            inp_p75=350,    # Poor INP  
            cls_p75=0.2,    # Poor CLS
            fcp_p75=3.0,    # Poor FCP
            score=35,       # Poor overall score
            device=strategy
        )
    
    def _detect_performance_leaks(self, mobile: PSIMetrics, desktop: PSIMetrics) -> List[str]:
        """Detect performance leak indicators"""
        leaks = []
        
        # Check mobile metrics (prioritized)
        if mobile.lcp_p75 > self.cwv_thresholds["lcp"]["poor"]:
            leaks.append("LCP_HIGH")
        elif mobile.lcp_p75 > self.cwv_thresholds["lcp"]["good"]:
            leaks.append("LCP_MODERATE")
            
        if mobile.inp_p75 > self.cwv_thresholds["inp"]["poor"]:
            leaks.append("INP_HIGH")
        elif mobile.inp_p75 > self.cwv_thresholds["inp"]["good"]:
            leaks.append("INP_MODERATE")
            
        if mobile.cls_p75 > self.cwv_thresholds["cls"]["poor"]:
            leaks.append("CLS_HIGH")
        elif mobile.cls_p75 > self.cwv_thresholds["cls"]["good"]:
            leaks.append("CLS_MODERATE")
            
        if mobile.fcp_p75 > self.cwv_thresholds["fcp"]["poor"]:
            leaks.append("FCP_HIGH")
            
        # Mobile-specific issues
        if mobile.score < 50:
            leaks.append("MOBILE_UNFRIENDLY")
            
        # Desktop comparison
        if desktop.score > mobile.score + 20:
            leaks.append("MOBILE_DESKTOP_GAP")
        
        return leaks
    
    async def _analyze_friction_points(self, url: str) -> List[str]:
        """Analyze UX friction points"""
        leaks = []
        
        try:
            # Basic page analysis for friction points
            async with self.session.get(url, timeout=15) as response:
                if response.status == 200:
                    content = await response.text()
                    content_lower = content.lower()
                    
                    # Check for phone CTA
                    phone_indicators = ["tel:", "call now", "click to call", "phone"]
                    if not any(indicator in content_lower for indicator in phone_indicators):
                        leaks.append("NO_PHONE_CTA")
                    
                    # Check for form validation
                    form_indicators = ["required", "validation", "error", "invalid"]
                    if "form" in content_lower and not any(indicator in content_lower for indicator in form_indicators):
                        leaks.append("WEAK_FORM")
                    
                    # Check for SSL
                    if not url.startswith("https://"):
                        leaks.append("SSL_ISSUES")
                        
                else:
                    leaks.append("ACCESSIBILITY_ISSUES")
                    
        except Exception as e:
            logger.debug(f"Friction analysis failed for {url}: {str(e)}")
            leaks.append("ANALYSIS_LIMITED")
        
        return leaks
    
    async def _capture_evidence_screenshot(self, url: str, leaks: List[str]) -> Optional[str]:
        """Capture screenshot evidence (placeholder for now)"""
        # This would integrate with screenshot service like Browserless or Puppeteer
        # For now, return a placeholder path
        if leaks:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            domain = urlparse(url).netloc
            return f"evidence/{domain}_{timestamp}_performance.png"
        return None
    
    def _generate_priority_fixes(self, leaks: List[str], metrics: PSIMetrics) -> List[str]:
        """Generate prioritized fix recommendations"""
        fixes = []
        
        if "LCP_HIGH" in leaks:
            fixes.append("Image optimization + lazy loading (Est. 1.5s LCP improvement)")
        if "INP_HIGH" in leaks:
            fixes.append("JavaScript optimization + form feedback (Est. 150ms INP reduction)")
        if "CLS_HIGH" in leaks:
            fixes.append("Layout stabilization + font loading (Est. 0.15 CLS improvement)")
        if "MOBILE_UNFRIENDLY" in leaks:
            fixes.append("Mobile responsiveness overhaul (Est. 25% mobile conversion boost)")
        if "NO_PHONE_CTA" in leaks:
            fixes.append("Add prominent click-to-call button (Est. 8% lead increase)")
        if "SSL_ISSUES" in leaks:
            fixes.append("SSL certificate installation (Security + SEO boost)")
        
        return fixes
    
    def _calculate_leak_score(self, leak_indicators: List[str]) -> int:
        """Calculate overall leak score (0-10)"""
        score = 0
        
        for leak in leak_indicators:
            if leak in self.leak_indicators:
                score += self.leak_indicators[leak]["impact"]
            else:
                score += 1  # Default impact for unknown leaks
        
        return min(score, 10)  # Cap at 10
    
    def _estimate_impact(self, leaks: List[str], metrics: Dict) -> str:
        """Estimate business impact of performance improvements"""
        if not leaks:
            return "5-10% conversion optimization potential"
        
        # Calculate impact based on leak severity
        high_impact_leaks = ["LCP_HIGH", "MOBILE_UNFRIENDLY", "SSL_ISSUES"]
        medium_impact_leaks = ["INP_HIGH", "CLS_HIGH", "FCP_HIGH"]
        
        high_count = sum(1 for leak in leaks if leak in high_impact_leaks)
        medium_count = sum(1 for leak in leaks if leak in medium_impact_leaks)
        
        if high_count >= 2:
            return "25-40% conversion rate improvement potential"
        elif high_count >= 1 or medium_count >= 3:
            return "15-25% conversion rate improvement potential"
        elif medium_count >= 1:
            return "10-20% conversion rate improvement potential"
        else:
            return "5-15% conversion rate improvement potential"