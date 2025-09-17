"""
Technology Intelligence Collector - Collects technology investment and modernization data.

This collector monitors technology stack changes, website updates, and
modernization activities to identify technology investment signals.
"""

import asyncio
import aiohttp
import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from arco.models.prospect import TechnologyInvestment


class TechnologyIntelligenceCollector:
    """
    Collects technology intelligence and modernization signals.
    
    Monitors:
    - Website redesigns and updates
    - Technology stack changes
    - New integrations and services
    - Modernization activities
    """
    
    def __init__(self):
        """Initialize the technology intelligence collector."""
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Technology detection patterns
        self.tech_patterns = {
            'cms': {
                'shopify': [r'shopify', r'myshopify\.com'],
                'wordpress': [r'wp-content', r'wordpress'],
                'magento': [r'magento', r'mage'],
                'woocommerce': [r'woocommerce'],
                'squarespace': [r'squarespace'],
                'webflow': [r'webflow']
            },
            'analytics': {
                'google_analytics': [r'google-analytics\.com', r'gtag\('],
                'google_analytics_4': [r'gtag.*G-[A-Z0-9]+'],
                'mixpanel': [r'mixpanel\.com'],
                'amplitude': [r'amplitude\.com'],
                'segment': [r'segment\.com', r'analytics\.js']
            },
            'marketing': {
                'hubspot': [r'hubspot', r'hs-scripts\.com'],
                'marketo': [r'marketo', r'mktoresp\.com'],
                'pardot': [r'pardot', r'pi\.pardot\.com'],
                'mailchimp': [r'mailchimp', r'list-manage\.com'],
                'klaviyo': [r'klaviyo', r'a\.klaviyo\.com']
            },
            'ecommerce': {
                'stripe': [r'stripe', r'js\.stripe\.com'],
                'paypal': [r'paypal', r'paypalobjects\.com'],
                'shopify_payments': [r'shopifypay'],
                'square': [r'squareup\.com', r'square'],
                'braintree': [r'braintree']
            },
            'hosting': {
                'cloudflare': [r'cloudflare', r'cf-ray'],
                'aws': [r'amazonaws\.com', r'cloudfront'],
                'google_cloud': [r'googleapis\.com', r'gstatic\.com'],
                'azure': [r'azure', r'microsoft'],
                'netlify': [r'netlify'],
                'vercel': [r'vercel']
            }
        }
        
        # Modernization indicators
        self.modernization_indicators = {
            'spa_frameworks': [r'react', r'vue', r'angular', r'svelte'],
            'modern_css': [r'tailwind', r'styled-components', r'emotion'],
            'build_tools': [r'webpack', r'vite', r'parcel', r'rollup'],
            'cdn': [r'cdn\.', r'cloudfront', r'fastly'],
            'pwa': [r'service-worker', r'manifest\.json', r'workbox'],
            'modern_js': [r'es6', r'es2015', r'async/await', r'import.*from']
        }
    
    async def collect(self, domain: str) -> TechnologyInvestment:
        """
        Collect comprehensive technology intelligence.
        
        Args:
            domain: Company domain
            
        Returns:
            TechnologyInvestment with collected data
        """
        self._logger.debug(f"🔧 Collecting technology intelligence for {domain}")
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            # Parallel collection from multiple sources
            current_tech_task = self._analyze_current_tech_stack(domain)
            website_changes_task = self._detect_website_changes(domain)
            integration_task = self._detect_new_integrations(domain)
            
            current_tech, website_changes, integrations = await asyncio.gather(
                current_tech_task, website_changes_task, integration_task,
                return_exceptions=True
            )
            
            # Process and combine data
            investment = self._process_technology_data(
                domain, current_tech, website_changes, integrations
            )
            
            self._logger.debug(
                f"⚙️ Technology intelligence for {domain}: "
                f"Redesign: {'✓' if investment.recent_website_redesign else '✗'}, "
                f"Major Project: {'✓' if investment.major_tech_project_active else '✗'}, "
                f"New Integrations: {len(investment.new_integrations_detected)}, "
                f"Modernization Score: {investment.technology_modernization_score}/100"
            )
            
            return investment
            
        except Exception as e:
            self._logger.error(f"❌ Failed to collect technology intelligence for {domain}: {e}")
            return TechnologyInvestment()
    
    async def _analyze_current_tech_stack(self, domain: str) -> Optional[Dict]:
        """
        Analyze current technology stack of the website.
        
        This involves fetching the website and analyzing the HTML, CSS, and JavaScript
        to identify technologies in use.
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Fetch website homepage
            url = f"https://{domain}"
            async with self.session.get(url, timeout=15) as response:
                if response.status == 200:
                    content = await response.text()
                    headers = dict(response.headers)
                    
                    return {
                        'content': content,
                        'headers': headers,
                        'status': response.status,
                        'url': str(response.url)
                    }
            
            return None
            
        except Exception as e:
            self._logger.warning(f"Tech stack analysis failed for {domain}: {e}")
            return None
    
    async def _detect_website_changes(self, domain: str) -> Optional[Dict]:
        """
        Detect recent website changes and redesigns.
        
        This would typically involve:
        - Comparing current site with archived versions
        - Analyzing change patterns
        - Detecting major redesigns
        """
        try:
            await asyncio.sleep(0.2)
            
            # Placeholder for website change detection
            # In production, this might use:
            # - Wayback Machine API
            # - Website monitoring services
            # - Visual diff tools
            # - Change detection algorithms
            
            # Simulate some websites having recent changes
            domain_hash = hash(domain.lower()) % 100
            
            if domain_hash < 15:  # 15% have recent redesigns
                return {
                    'recent_redesign': True,
                    'last_major_change': (datetime.now() - timedelta(days=60)).isoformat(),
                    'change_indicators': ['New design system', 'Updated navigation', 'Modern layout']
                }
            elif domain_hash < 30:  # Additional 15% have minor updates
                return {
                    'recent_redesign': False,
                    'last_major_change': (datetime.now() - timedelta(days=180)).isoformat(),
                    'change_indicators': ['Content updates', 'Minor styling changes']
                }
            
            return None
            
        except Exception as e:
            self._logger.warning(f"Website change detection failed for {domain}: {e}")
            return None
    
    async def _detect_new_integrations(self, domain: str) -> Optional[Dict]:
        """
        Detect new integrations and third-party services.
        
        This analyzes the website for recently added third-party integrations.
        """
        try:
            await asyncio.sleep(0.2)
            
            # Placeholder for integration detection
            # In production, this would:
            # - Compare current integrations with historical data
            # - Detect new third-party scripts
            # - Identify new API integrations
            # - Monitor for new tracking pixels
            
            # Simulate some new integrations
            domain_hash = hash(domain.lower()) % 100
            
            if domain_hash < 20:  # 20% have new integrations
                return {
                    'new_integrations': ['Stripe', 'Intercom', 'Hotjar'],
                    'integration_dates': [
                        (datetime.now() - timedelta(days=30)).isoformat(),
                        (datetime.now() - timedelta(days=45)).isoformat(),
                        (datetime.now() - timedelta(days=60)).isoformat()
                    ]
                }
            
            return None
            
        except Exception as e:
            self._logger.warning(f"Integration detection failed for {domain}: {e}")
            return None
    
    def _process_technology_data(self, 
                               domain: str,
                               current_tech: Any,
                               website_changes: Any,
                               integrations: Any) -> TechnologyInvestment:
        """Process and combine technology data from multiple sources."""
        
        investment = TechnologyInvestment()
        
        # Process current tech stack
        if not isinstance(current_tech, Exception) and current_tech:
            content = current_tech.get('content', '')
            headers = current_tech.get('headers', {})
            
            # Detect technologies
            detected_tech = self._detect_technologies_in_content(content, headers)
            investment.technology_modernization_score = self._calculate_modernization_score(detected_tech)
            
            # Check for major tech projects
            investment.major_tech_project_active = self._detect_major_tech_project(content)
        
        # Process website changes
        if not isinstance(website_changes, Exception) and website_changes:
            investment.recent_website_redesign = website_changes.get('recent_redesign', False)
            
            if website_changes.get('last_major_change'):
                try:
                    change_date = datetime.fromisoformat(website_changes['last_major_change'].replace('Z', '+00:00'))
                    investment.last_major_update = change_date.replace(tzinfo=None)
                except:
                    pass
        
        # Process integrations
        if not isinstance(integrations, Exception) and integrations:
            investment.new_integrations_detected = integrations.get('new_integrations', [])
        
        return investment
    
    def _detect_technologies_in_content(self, content: str, headers: Dict) -> Dict[str, List[str]]:
        """Detect technologies in website content and headers."""
        detected = {}
        content_lower = content.lower()
        
        for category, technologies in self.tech_patterns.items():
            detected[category] = []
            
            for tech_name, patterns in technologies.items():
                for pattern in patterns:
                    if re.search(pattern, content_lower) or any(re.search(pattern, str(v).lower()) for v in headers.values()):
                        detected[category].append(tech_name)
                        break
        
        # Detect modernization indicators
        detected['modernization'] = []
        for indicator_type, patterns in self.modernization_indicators.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    detected['modernization'].append(indicator_type)
                    break
        
        return detected
    
    def _calculate_modernization_score(self, detected_tech: Dict[str, List[str]]) -> int:
        """Calculate technology modernization score (0-100)."""
        score = 0
        
        # Modern CMS/Platform (20 points)
        modern_cms = ['shopify', 'webflow', 'squarespace']
        if any(cms in detected_tech.get('cms', []) for cms in modern_cms):
            score += 20
        elif detected_tech.get('cms'):
            score += 10
        
        # Modern Analytics (15 points)
        modern_analytics = ['google_analytics_4', 'mixpanel', 'amplitude', 'segment']
        if any(analytics in detected_tech.get('analytics', []) for analytics in modern_analytics):
            score += 15
        elif detected_tech.get('analytics'):
            score += 8
        
        # Modern Payment Processing (15 points)
        modern_payments = ['stripe', 'square', 'braintree']
        if any(payment in detected_tech.get('ecommerce', []) for payment in modern_payments):
            score += 15
        
        # Cloud Hosting (15 points)
        cloud_hosting = ['cloudflare', 'aws', 'google_cloud', 'netlify', 'vercel']
        if any(host in detected_tech.get('hosting', []) for host in cloud_hosting):
            score += 15
        
        # Marketing Automation (10 points)
        modern_marketing = ['hubspot', 'marketo', 'klaviyo']
        if any(marketing in detected_tech.get('marketing', []) for marketing in modern_marketing):
            score += 10
        
        # Modernization Indicators (25 points)
        modernization_count = len(detected_tech.get('modernization', []))
        score += min(modernization_count * 5, 25)
        
        return min(score, 100)
    
    def _detect_major_tech_project(self, content: str) -> bool:
        """Detect if a major technology project is active."""
        # Look for indicators of major tech projects
        project_indicators = [
            'coming soon', 'under construction', 'beta', 'preview',
            'new version', 'upgrade', 'migration', 'modernization'
        ]
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in project_indicators)
    
    async def get_technology_timeline(self, domain: str) -> List[Dict[str, Any]]:
        """
        Get technology adoption timeline.
        
        Args:
            domain: Company domain
            
        Returns:
            List of technology changes over time
        """
        try:
            # This would typically involve historical analysis
            # For now, return current state
            investment = await self.collect(domain)
            
            timeline = []
            
            if investment.last_major_update:
                timeline.append({
                    'date': investment.last_major_update,
                    'type': 'Website Redesign' if investment.recent_website_redesign else 'Website Update',
                    'description': 'Major website changes detected',
                    'impact': 'High' if investment.recent_website_redesign else 'Medium'
                })
            
            for integration in investment.new_integrations_detected:
                timeline.append({
                    'date': datetime.now() - timedelta(days=30),  # Placeholder
                    'type': 'New Integration',
                    'description': f'Added {integration} integration',
                    'impact': 'Medium'
                })
            
            return sorted(timeline, key=lambda x: x['date'], reverse=True)
            
        except Exception as e:
            self._logger.error(f"Failed to get technology timeline for {domain}: {e}")
            return []
    
    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None