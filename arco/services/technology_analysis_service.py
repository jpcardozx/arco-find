"""
Technology Analysis Service for detecting harmful technologies and outdated stacks.

This service analyzes websites to identify:
- Outdated frameworks and libraries
- Known vulnerabilities
- Performance issues
- Security vulnerabilities
"""

import asyncio
import re
import json
import logging
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import aiohttp
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


@dataclass
class TechnologyDetection:
    """Represents a detected technology with version and risk assessment."""
    name: str
    version: Optional[str] = None
    category: str = ""  # framework, library, cms, server, etc.
    risk_level: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL
    risk_reasons: List[str] = field(default_factory=list)
    is_outdated: bool = False
    latest_version: Optional[str] = None
    vulnerability_count: int = 0
    confidence: float = 0.0  # 0.0-1.0


@dataclass
class PerformanceIssue:
    """Represents a performance issue detected on the website."""
    issue_type: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    impact: str
    recommendation: str
    metric_value: Optional[float] = None
    threshold: Optional[float] = None


@dataclass
class SecurityVulnerability:
    """Represents a security vulnerability detected."""
    vulnerability_type: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    cve_id: Optional[str] = None
    fix_recommendation: str
    affected_component: str = ""


@dataclass
class TechnologyAnalysisResult:
    """Complete technology analysis result."""
    domain: str
    analyzed_at: datetime = field(default_factory=datetime.now)
    
    # Technology stack analysis
    technologies_detected: List[TechnologyDetection] = field(default_factory=list)
    outdated_technologies: List[TechnologyDetection] = field(default_factory=list)
    
    # Performance analysis
    performance_issues: List[PerformanceIssue] = field(default_factory=list)
    performance_score: int = 0  # 0-100
    
    # Security analysis
    security_vulnerabilities: List[SecurityVulnerability] = field(default_factory=list)
    security_score: int = 0  # 0-100
    
    # Overall scoring
    harmful_tech_score: int = 0  # 0-25 points as per requirements
    total_risk_factors: int = 0
    
    # Analysis metadata
    analysis_success: bool = True
    error_messages: List[str] = field(default_factory=list)
    confidence_level: float = 0.0


class TechnologyAnalysisService:
    """Service for analyzing harmful technologies and outdated stacks."""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Technology version databases
        self.outdated_versions = {
            'react': {'min_version': '16.0.0', 'current': '18.2.0'},
            'angular': {'min_version': '10.0.0', 'current': '16.0.0'},
            'vue': {'min_version': '2.6.0', 'current': '3.3.0'},
            'jquery': {'min_version': '3.0.0', 'current': '3.7.0'},
            'bootstrap': {'min_version': '4.0.0', 'current': '5.3.0'},
            'wordpress': {'min_version': '5.0.0', 'current': '6.3.0'},
            'drupal': {'min_version': '8.0.0', 'current': '10.1.0'},
            'joomla': {'min_version': '3.9.0', 'current': '4.3.0'},
        }
        
        # Deprecated/discontinued technologies
        self.deprecated_technologies = {
            'flash', 'silverlight', 'java-applet', 'activex',
            'internet-explorer', 'jquery-1', 'jquery-2',
            'angular-1', 'angularjs', 'backbone', 'knockout'
        }
        
        # Known vulnerable libraries patterns
        self.vulnerable_patterns = {
            r'jquery-(\d+\.\d+\.\d+)': {'name': 'jQuery', 'vulnerable_versions': ['<3.0.0']},
            r'bootstrap-(\d+\.\d+\.\d+)': {'name': 'Bootstrap', 'vulnerable_versions': ['<4.0.0']},
            r'lodash-(\d+\.\d+\.\d+)': {'name': 'Lodash', 'vulnerable_versions': ['<4.17.12']},
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'ARCO-TechAnalyzer/1.0'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def analyze_harmful_technologies(self, domain: str) -> TechnologyAnalysisResult:
        """
        Analyze a domain for harmful technologies, outdated stacks, and vulnerabilities.
        
        Args:
            domain: The domain to analyze
            
        Returns:
            TechnologyAnalysisResult with complete analysis
        """
        result = TechnologyAnalysisResult(domain=domain)
        
        try:
            # Ensure we have a session
            if not self.session:
                async with self:
                    return await self._perform_analysis(domain, result)
            else:
                return await self._perform_analysis(domain, result)
                
        except Exception as e:
            logger.error(f"Technology analysis failed for {domain}: {e}")
            result.analysis_success = False
            result.error_messages.append(str(e))
            return result
    
    async def _perform_analysis(self, domain: str, result: TechnologyAnalysisResult) -> TechnologyAnalysisResult:
        """Perform the actual technology analysis."""
        
        # Normalize domain
        if not domain.startswith(('http://', 'https://')):
            domain = f'https://{domain}'
        
        # Run all analysis tasks in parallel
        tasks = [
            self._detect_technologies(domain),
            self._analyze_performance_issues(domain),
            self._analyze_security_vulnerabilities(domain)
        ]
        
        tech_results, perf_results, sec_results = await asyncio.gather(
            *tasks, return_exceptions=True
        )
        
        # Process technology detection results
        if not isinstance(tech_results, Exception):
            result.technologies_detected = tech_results
            result.outdated_technologies = [
                tech for tech in tech_results 
                if tech.is_outdated or tech.risk_level in ['HIGH', 'CRITICAL']
            ]
        
        # Process performance results
        if not isinstance(perf_results, Exception):
            result.performance_issues, result.performance_score = perf_results
        
        # Process security results
        if not isinstance(sec_results, Exception):
            result.security_vulnerabilities, result.security_score = sec_results
        
        # Calculate overall harmful technology score
        result.harmful_tech_score = self._calculate_harmful_tech_score(result)
        result.total_risk_factors = len(result.outdated_technologies) + len(result.performance_issues) + len(result.security_vulnerabilities)
        result.confidence_level = self._calculate_confidence(result)
        
        return result
    
    async def _detect_technologies(self, domain: str) -> List[TechnologyDetection]:
        """Detect technologies used on the website."""
        technologies = []
        
        try:
            # Fetch the main page
            async with self.session.get(domain) as response:
                if response.status != 200:
                    return technologies
                
                html_content = await response.text()
                headers = dict(response.headers)
            
            # Detect technologies from HTML content
            technologies.extend(self._detect_from_html(html_content))
            
            # Detect technologies from HTTP headers
            technologies.extend(self._detect_from_headers(headers))
            
            # Detect JavaScript libraries
            technologies.extend(await self._detect_js_libraries(domain))
            
            # Check for outdated versions and vulnerabilities
            for tech in technologies:
                self._assess_technology_risk(tech)
            
        except Exception as e:
            logger.error(f"Technology detection failed for {domain}: {e}")
        
        return technologies
    
    def _detect_from_html(self, html_content: str) -> List[TechnologyDetection]:
        """Detect technologies from HTML content."""
        technologies = []
        
        # WordPress detection
        if 'wp-content' in html_content or 'wordpress' in html_content.lower():
            version_match = re.search(r'wp-includes/js/wp-embed\.min\.js\?ver=(\d+\.\d+(?:\.\d+)?)', html_content)
            version = version_match.group(1) if version_match else None
            technologies.append(TechnologyDetection(
                name='WordPress',
                version=version,
                category='cms',
                confidence=0.9
            ))
        
        # React detection
        if 'react' in html_content.lower():
            version_match = re.search(r'react@(\d+\.\d+\.\d+)', html_content)
            version = version_match.group(1) if version_match else None
            technologies.append(TechnologyDetection(
                name='React',
                version=version,
                category='framework',
                confidence=0.8
            ))
        
        # Angular detection
        if 'angular' in html_content.lower() or 'ng-' in html_content:
            version_match = re.search(r'angular/(\d+\.\d+\.\d+)', html_content)
            version = version_match.group(1) if version_match else None
            technologies.append(TechnologyDetection(
                name='Angular',
                version=version,
                category='framework',
                confidence=0.8
            ))
        
        # jQuery detection
        jquery_match = re.search(r'jquery[/-](\d+\.\d+\.\d+)', html_content, re.IGNORECASE)
        if jquery_match:
            technologies.append(TechnologyDetection(
                name='jQuery',
                version=jquery_match.group(1),
                category='library',
                confidence=0.9
            ))
        
        # Bootstrap detection
        if 'bootstrap' in html_content.lower():
            version_match = re.search(r'bootstrap[/-](\d+\.\d+\.\d+)', html_content)
            version = version_match.group(1) if version_match else None
            technologies.append(TechnologyDetection(
                name='Bootstrap',
                version=version,
                category='framework',
                confidence=0.8
            ))
        
        # Deprecated technology detection
        deprecated_found = []
        if 'flash' in html_content.lower() or '.swf' in html_content:
            deprecated_found.append('Flash')
        if 'silverlight' in html_content.lower():
            deprecated_found.append('Silverlight')
        if 'java-applet' in html_content.lower() or '<applet' in html_content:
            deprecated_found.append('Java Applet')
        
        for dep_tech in deprecated_found:
            technologies.append(TechnologyDetection(
                name=dep_tech,
                category='deprecated',
                risk_level='CRITICAL',
                risk_reasons=[f'{dep_tech} is deprecated and no longer supported'],
                confidence=0.95
            ))
        
        return technologies
    
    def _detect_from_headers(self, headers: Dict[str, str]) -> List[TechnologyDetection]:
        """Detect technologies from HTTP headers."""
        technologies = []
        
        # Server detection
        server = headers.get('server', '').lower()
        if server:
            if 'apache' in server:
                version_match = re.search(r'apache/(\d+\.\d+\.\d+)', server)
                version = version_match.group(1) if version_match else None
                technologies.append(TechnologyDetection(
                    name='Apache',
                    version=version,
                    category='server',
                    confidence=0.9
                ))
            elif 'nginx' in server:
                version_match = re.search(r'nginx/(\d+\.\d+\.\d+)', server)
                version = version_match.group(1) if version_match else None
                technologies.append(TechnologyDetection(
                    name='Nginx',
                    version=version,
                    category='server',
                    confidence=0.9
                ))
        
        # X-Powered-By detection
        powered_by = headers.get('x-powered-by', '').lower()
        if powered_by:
            if 'php' in powered_by:
                version_match = re.search(r'php/(\d+\.\d+\.\d+)', powered_by)
                version = version_match.group(1) if version_match else None
                technologies.append(TechnologyDetection(
                    name='PHP',
                    version=version,
                    category='language',
                    confidence=0.9
                ))
        
        return technologies
    
    async def _detect_js_libraries(self, domain: str) -> List[TechnologyDetection]:
        """Detect JavaScript libraries by analyzing common paths."""
        technologies = []
        
        # Common library paths to check
        common_paths = [
            '/wp-includes/js/jquery/jquery.min.js',
            '/assets/js/jquery.min.js',
            '/js/jquery.min.js',
            '/node_modules/react/package.json',
            '/assets/js/bootstrap.min.js'
        ]
        
        for path in common_paths:
            try:
                url = urljoin(domain, path)
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Extract version from content
                        if 'jquery' in path.lower():
                            version_match = re.search(r'jQuery v(\d+\.\d+\.\d+)', content)
                            if version_match:
                                technologies.append(TechnologyDetection(
                                    name='jQuery',
                                    version=version_match.group(1),
                                    category='library',
                                    confidence=0.95
                                ))
                        
                        elif 'bootstrap' in path.lower():
                            version_match = re.search(r'Bootstrap v(\d+\.\d+\.\d+)', content)
                            if version_match:
                                technologies.append(TechnologyDetection(
                                    name='Bootstrap',
                                    version=version_match.group(1),
                                    category='framework',
                                    confidence=0.95
                                ))
            
            except Exception:
                continue  # Path not found or inaccessible
        
        return technologies
    
    def _assess_technology_risk(self, tech: TechnologyDetection) -> None:
        """Assess the risk level of a detected technology."""
        
        # Check if technology is deprecated
        if tech.name.lower() in self.deprecated_technologies:
            tech.risk_level = 'CRITICAL'
            tech.risk_reasons.append(f'{tech.name} is deprecated and no longer supported')
            tech.is_outdated = True
            return
        
        # Check version-specific risks
        tech_key = tech.name.lower()
        if tech_key in self.outdated_versions and tech.version:
            min_version = self.outdated_versions[tech_key]['min_version']
            current_version = self.outdated_versions[tech_key]['current']
            
            if self._is_version_outdated(tech.version, min_version):
                tech.is_outdated = True
                tech.latest_version = current_version
                
                # Determine risk level based on how outdated
                if self._is_version_critically_outdated(tech.version, min_version):
                    tech.risk_level = 'HIGH'
                    tech.risk_reasons.append(f'{tech.name} {tech.version} is critically outdated (minimum recommended: {min_version})')
                else:
                    tech.risk_level = 'MEDIUM'
                    tech.risk_reasons.append(f'{tech.name} {tech.version} is outdated (current: {current_version})')
        
        # Check for known vulnerabilities
        self._check_vulnerabilities(tech)
    
    def _is_version_outdated(self, current: str, minimum: str) -> bool:
        """Check if current version is older than minimum required."""
        try:
            current_parts = [int(x) for x in current.split('.')]
            minimum_parts = [int(x) for x in minimum.split('.')]
            
            # Pad shorter version with zeros
            max_len = max(len(current_parts), len(minimum_parts))
            current_parts.extend([0] * (max_len - len(current_parts)))
            minimum_parts.extend([0] * (max_len - len(minimum_parts)))
            
            return current_parts < minimum_parts
        except (ValueError, AttributeError):
            return False
    
    def _is_version_critically_outdated(self, current: str, minimum: str) -> bool:
        """Check if version is critically outdated (major version behind)."""
        try:
            current_major = int(current.split('.')[0])
            minimum_major = int(minimum.split('.')[0])
            return current_major < minimum_major
        except (ValueError, AttributeError, IndexError):
            return False
    
    def _check_vulnerabilities(self, tech: TechnologyDetection) -> None:
        """Check for known vulnerabilities in the technology."""
        
        # Known vulnerability patterns
        vulnerability_db = {
            'jquery': {
                'versions': ['<3.0.0'],
                'cve': 'CVE-2020-11022',
                'description': 'Cross-site scripting vulnerability'
            },
            'bootstrap': {
                'versions': ['<4.0.0'],
                'cve': 'CVE-2019-8331',
                'description': 'XSS vulnerability in tooltip and popover'
            },
            'wordpress': {
                'versions': ['<5.0.0'],
                'cve': 'Multiple CVEs',
                'description': 'Multiple security vulnerabilities'
            }
        }
        
        tech_key = tech.name.lower()
        if tech_key in vulnerability_db and tech.version:
            vuln_info = vulnerability_db[tech_key]
            
            # Simple version check (could be enhanced with proper semver)
            if any(self._version_matches_pattern(tech.version, pattern) 
                   for pattern in vuln_info['versions']):
                tech.vulnerability_count += 1
                tech.risk_reasons.append(f'Known vulnerability: {vuln_info["description"]} ({vuln_info["cve"]})')
                
                if tech.risk_level == 'LOW':
                    tech.risk_level = 'MEDIUM'
    
    def _version_matches_pattern(self, version: str, pattern: str) -> bool:
        """Check if version matches vulnerability pattern."""
        if pattern.startswith('<'):
            threshold = pattern[1:]
            return self._is_version_outdated(version, threshold)
        return False
    
    async def _analyze_performance_issues(self, domain: str) -> Tuple[List[PerformanceIssue], int]:
        """Analyze performance issues on the website."""
        issues = []
        performance_score = 100  # Start with perfect score and deduct
        
        try:
            # Measure page load time
            start_time = asyncio.get_event_loop().time()
            async with self.session.get(domain) as response:
                content = await response.text()
                load_time = asyncio.get_event_loop().time() - start_time
            
            # Check First Contentful Paint equivalent (load time)
            if load_time > 3.0:
                issues.append(PerformanceIssue(
                    issue_type="slow_loading",
                    severity="HIGH" if load_time > 5.0 else "MEDIUM",
                    description=f"Page load time is {load_time:.2f}s (threshold: 3.0s)",
                    impact="Poor user experience and SEO ranking",
                    recommendation="Optimize images, minify CSS/JS, use CDN",
                    metric_value=load_time,
                    threshold=3.0
                ))
                performance_score -= 20 if load_time > 5.0 else 10
            
            # Check for unoptimized resources
            if self._has_unoptimized_resources(content):
                issues.append(PerformanceIssue(
                    issue_type="unoptimized_resources",
                    severity="MEDIUM",
                    description="Unminified CSS/JS files detected",
                    impact="Slower page load times",
                    recommendation="Minify and compress CSS/JS files",
                ))
                performance_score -= 15
            
            # Check for missing CDN
            if not self._has_cdn(content, dict(response.headers)):
                issues.append(PerformanceIssue(
                    issue_type="no_cdn",
                    severity="MEDIUM",
                    description="No CDN detected for static assets",
                    impact="Slower global content delivery",
                    recommendation="Implement CDN for static assets",
                ))
                performance_score -= 10
            
            # Check for large images
            large_images = self._detect_large_images(content)
            if large_images:
                issues.append(PerformanceIssue(
                    issue_type="large_images",
                    severity="MEDIUM",
                    description=f"Large unoptimized images detected: {len(large_images)} images",
                    impact="Increased bandwidth usage and slower loading",
                    recommendation="Optimize images, use WebP format, implement lazy loading",
                ))
                performance_score -= 15
        
        except Exception as e:
            logger.error(f"Performance analysis failed for {domain}: {e}")
            issues.append(PerformanceIssue(
                issue_type="analysis_error",
                severity="LOW",
                description=f"Performance analysis failed: {str(e)}",
                impact="Unable to assess performance",
                recommendation="Manual performance audit recommended",
            ))
            performance_score = 50  # Default score when analysis fails
        
        return issues, max(performance_score, 0)
    
    def _has_unoptimized_resources(self, content: str) -> bool:
        """Check for unminified CSS/JS resources."""
        # Look for non-minified file references
        unminified_patterns = [
            r'\.css(?!\?|\#)',  # CSS files without .min
            r'\.js(?!\?|\#)',   # JS files without .min
        ]
        
        minified_patterns = [
            r'\.min\.css',
            r'\.min\.js',
        ]
        
        # Count total vs minified resources
        total_resources = 0
        minified_resources = 0
        
        for pattern in unminified_patterns:
            total_resources += len(re.findall(pattern, content))
        
        for pattern in minified_patterns:
            minified_resources += len(re.findall(pattern, content))
        
        # If less than 50% of resources are minified, consider it unoptimized
        if total_resources > 0:
            minification_ratio = minified_resources / total_resources
            return minification_ratio < 0.5
        
        return False
    
    def _has_cdn(self, content: str, headers: Dict[str, str]) -> bool:
        """Check if CDN is being used."""
        cdn_indicators = [
            'cloudflare', 'cloudfront', 'fastly', 'maxcdn',
            'jsdelivr', 'unpkg', 'cdnjs', 'googleapis'
        ]
        
        # Check in content
        content_lower = content.lower()
        for indicator in cdn_indicators:
            if indicator in content_lower:
                return True
        
        # Check in headers
        for header_value in headers.values():
            for indicator in cdn_indicators:
                if indicator in header_value.lower():
                    return True
        
        return False
    
    def _detect_large_images(self, content: str) -> List[str]:
        """Detect potentially large images."""
        # This is a simplified detection - in reality, you'd fetch image headers
        img_patterns = re.findall(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', content, re.IGNORECASE)
        
        # Filter for potentially large images (non-optimized formats)
        large_images = []
        for img_src in img_patterns:
            if any(ext in img_src.lower() for ext in ['.jpg', '.jpeg', '.png', '.bmp']):
                if not any(opt in img_src.lower() for opt in ['thumb', 'small', 'icon']):
                    large_images.append(img_src)
        
        return large_images[:10]  # Return first 10 for analysis
    
    async def _analyze_security_vulnerabilities(self, domain: str) -> Tuple[List[SecurityVulnerability], int]:
        """Analyze security vulnerabilities."""
        vulnerabilities = []
        security_score = 100  # Start with perfect score
        
        try:
            async with self.session.get(domain) as response:
                headers = dict(response.headers)
                content = await response.text()
            
            # Check SSL/TLS
            if not domain.startswith('https://'):
                vulnerabilities.append(SecurityVulnerability(
                    vulnerability_type="no_ssl",
                    severity="HIGH",
                    description="Website not using HTTPS",
                    fix_recommendation="Implement SSL/TLS certificate",
                    affected_component="Transport Layer"
                ))
                security_score -= 30
            
            # Check security headers
            security_headers = {
                'strict-transport-security': 'HSTS header missing',
                'x-frame-options': 'X-Frame-Options header missing (clickjacking protection)',
                'x-content-type-options': 'X-Content-Type-Options header missing',
                'x-xss-protection': 'X-XSS-Protection header missing',
                'content-security-policy': 'Content Security Policy header missing'
            }
            
            missing_headers = []
            for header, description in security_headers.items():
                if header not in [h.lower() for h in headers.keys()]:
                    missing_headers.append(header)
                    vulnerabilities.append(SecurityVulnerability(
                        vulnerability_type="missing_security_header",
                        severity="MEDIUM",
                        description=description,
                        fix_recommendation=f"Add {header} header to server configuration",
                        affected_component="HTTP Headers"
                    ))
            
            security_score -= len(missing_headers) * 10
            
            # Check for exposed sensitive information
            sensitive_patterns = [
                (r'password\s*[:=]\s*["\'][^"\']+["\']', 'Exposed password in source'),
                (r'api[_-]?key\s*[:=]\s*["\'][^"\']+["\']', 'Exposed API key in source'),
                (r'secret\s*[:=]\s*["\'][^"\']+["\']', 'Exposed secret in source'),
            ]
            
            for pattern, description in sensitive_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    vulnerabilities.append(SecurityVulnerability(
                        vulnerability_type="information_exposure",
                        severity="HIGH",
                        description=description,
                        fix_recommendation="Remove sensitive information from client-side code",
                        affected_component="Source Code"
                    ))
                    security_score -= 20
            
            # Check for CSRF protection (simplified)
            forms = re.findall(r'<form[^>]*>', content, re.IGNORECASE)
            csrf_protected_forms = re.findall(r'csrf|_token', content, re.IGNORECASE)
            
            if forms and not csrf_protected_forms:
                vulnerabilities.append(SecurityVulnerability(
                    vulnerability_type="csrf_vulnerability",
                    severity="MEDIUM",
                    description="Forms detected without apparent CSRF protection",
                    fix_recommendation="Implement CSRF tokens for all forms",
                    affected_component="Forms"
                ))
                security_score -= 15
        
        except Exception as e:
            logger.error(f"Security analysis failed for {domain}: {e}")
            security_score = 50  # Default score when analysis fails
        
        return vulnerabilities, max(security_score, 0)
    
    def _calculate_harmful_tech_score(self, result: TechnologyAnalysisResult) -> int:
        """Calculate the harmful technology score (0-25 points)."""
        score = 0
        
        # Deduct points for outdated technologies
        for tech in result.outdated_technologies:
            if tech.risk_level == 'CRITICAL':
                score += 8  # Major deduction for critical issues
            elif tech.risk_level == 'HIGH':
                score += 5
            elif tech.risk_level == 'MEDIUM':
                score += 3
            else:
                score += 1
        
        # Deduct points for performance issues
        for issue in result.performance_issues:
            if issue.severity == 'CRITICAL':
                score += 6
            elif issue.severity == 'HIGH':
                score += 4
            elif issue.severity == 'MEDIUM':
                score += 2
            else:
                score += 1
        
        # Deduct points for security vulnerabilities
        for vuln in result.security_vulnerabilities:
            if vuln.severity == 'CRITICAL':
                score += 7
            elif vuln.severity == 'HIGH':
                score += 5
            elif vuln.severity == 'MEDIUM':
                score += 3
            else:
                score += 1
        
        # Cap at 25 points as per requirements
        return min(score, 25)
    
    def _calculate_confidence(self, result: TechnologyAnalysisResult) -> float:
        """Calculate confidence level of the analysis."""
        confidence_factors = []
        
        # Technology detection confidence
        if result.technologies_detected:
            avg_tech_confidence = sum(tech.confidence for tech in result.technologies_detected) / len(result.technologies_detected)
            confidence_factors.append(avg_tech_confidence)
        
        # Analysis success factor
        if result.analysis_success:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.3)
        
        # Error factor
        error_factor = max(0.1, 1.0 - (len(result.error_messages) * 0.2))
        confidence_factors.append(error_factor)
        
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.0


# Convenience function for standalone usage
async def analyze_domain_technologies(domain: str) -> TechnologyAnalysisResult:
    """Analyze a domain for harmful technologies (standalone function)."""
    async with TechnologyAnalysisService() as service:
        return await service.analyze_harmful_technologies(domain)