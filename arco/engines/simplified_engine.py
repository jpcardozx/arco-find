"""
Simplified Engine for ARCO.

This module contains the simplified engine implementation for the ARCO system,
which provides basic leak detection functionality without external dependencies.
"""

import asyncio
import json
import yaml
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
import httpx
import os

from arco.engines.base import LeakEngineInterface
from arco.models.prospect import Prospect
from arco.models.leak_result import LeakResult
from arco.models.qualified_prospect import QualifiedProspect, Leak
from arco.utils.logger import get_logger

logger = get_logger(__name__)

class SimplifiedEngine(LeakEngineInterface):
    """
    Simplified Engine for leak detection.
    Python-only implementation with no external CLI dependencies.
    """
    
    def __init__(self):
        """Initialize the SimplifiedEngine."""
        self.vendor_costs = self._load_vendor_database()
        self.min_monthly_waste = 40
        self.min_qualification_score = 60
        
        logger.info("SimplifiedEngine initialized")
        logger.info(f"Vendor database: {len(self.vendor_costs)} vendors loaded")

    def _load_vendor_database(self) -> Dict:
        """Load vendor cost database."""
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
                    return vendor_db
            
            # If no file found, use default values
            logger.warning("⚠️ Vendor database not found, using minimal set")
            return {
                'klaviyo': {'growth': 150, 'categories': ['email_marketing']},
                'typeform': {'plus': 50, 'categories': ['forms']},
                'gorgias': {'basic': 150, 'categories': ['customer_support']},
                'recharge': {'growth': 300, 'categories': ['subscriptions']}
            }
        except Exception as e:
            logger.error(f"Error loading vendor database: {e}")
            # Fallback to minimal set
            return {
                'klaviyo': {'growth': 150, 'categories': ['email_marketing']},
                'typeform': {'plus': 50, 'categories': ['forms']}
            }

    async def analyze(self, prospect: Prospect) -> LeakResult:
        """
        Analyze a prospect for potential revenue leaks.
        
        Args:
            prospect: The prospect to analyze
            
        Returns:
            Leak analysis result
        """
        logger.info(f"Analyzing domain: {prospect.domain}")
        
        start_time = asyncio.get_event_loop().time()
        all_leaks = []
        
        try:
            # 1. HTTP-based technology detection
            tech_leaks = await self._detect_via_http(prospect.domain)
            all_leaks.extend(tech_leaks)
            
            # 2. Shopify storefront analysis
            shopify_leaks = await self._detect_shopify_costs(prospect.domain)
            all_leaks.extend(shopify_leaks)
            
            # 3. Common e-commerce patterns
            pattern_leaks = await self._detect_common_patterns(prospect.domain)
            all_leaks.extend(pattern_leaks)
            
        except Exception as e:
            logger.error(f"Error during leak analysis: {e}")
        
        # Calculate processing time
        processing_time = asyncio.get_event_loop().time() - start_time
        
        # Create LeakResult
        total_monthly_waste = sum(leak.monthly_waste for leak in all_leaks)
        
        leak_result = LeakResult(
            domain=prospect.domain,
            total_monthly_waste=total_monthly_waste,
            leaks=all_leaks,
            authority_score=self._calculate_authority_score(prospect),
            has_ads=False,  # Simplified implementation doesn't detect ads
            processing_time=processing_time
        )
        
        logger.info(f"Analysis complete for {prospect.domain}: ${total_monthly_waste:.2f}/month waste detected")
        return leak_result

    async def qualify(self, prospect: Prospect, leak_result: LeakResult) -> QualifiedProspect:
        """
        Qualify a prospect based on leak analysis.
        
        Args:
            prospect: The prospect to qualify
            leak_result: Leak analysis result
            
        Returns:
            Qualified prospect
        """
        # Create qualified prospect from base prospect
        qualified = QualifiedProspect.from_prospect(prospect)
        
        # Add leak detection data
        qualified.monthly_waste = leak_result.total_monthly_waste
        qualified.annual_savings = leak_result.annual_savings
        qualified.leak_count = leak_result.leak_count
        qualified.top_leaks = leak_result.top_leaks[:5]  # Top 5 leaks
        
        # Calculate qualification score
        qualification_score = self._calculate_qualification_score(leak_result.leaks)
        qualified.qualification_score = qualification_score
        
        # Determine priority tier
        if qualification_score >= 80:
            qualified.priority_tier = "A"
        elif qualification_score >= 60:
            qualified.priority_tier = "B"
        else:
            qualified.priority_tier = "C"
        
        # Determine if ready for outreach
        qualified.outreach_ready = (
            leak_result.total_monthly_waste >= 100 and 
            qualification_score >= self.min_qualification_score
        )
        
        # Set qualification date to now
        qualified.qualification_date = datetime.now()
        
        logger.info(f"Qualified {prospect.domain}: Score {qualification_score}/100, Tier {qualified.priority_tier}")
        return qualified

    async def _detect_via_http(self, domain: str) -> List[Leak]:
        """Detect technologies via HTTP analysis."""
        leaks = []
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Check main page
                response = await client.get(f"https://{domain}")
                html_content = response.text.lower()
                
                # Common technology patterns
                tech_patterns = {
                    'klaviyo': {'cost': 150, 'category': 'email_marketing'},
                    'typeform': {'cost': 50, 'category': 'forms'},
                    'gorgias': {'cost': 150, 'category': 'customer_support'},
                    'hotjar': {'cost': 99, 'category': 'analytics'},
                    'intercom': {'cost': 99, 'category': 'live_chat'},
                }
                
                for tech_name, tech_data in tech_patterns.items():
                    if tech_name in html_content:
                        leak = Leak(
                            type='vendor_waste',
                            monthly_waste=tech_data['cost'],
                            annual_savings=tech_data['cost'] * 12,
                            description=f"{tech_name.capitalize()} subscription detected via HTTP analysis",
                            severity='medium'
                        )
                        leaks.append(leak)
                        logger.info(f"Detected {tech_name}: ${tech_data['cost']}/month (HTTP detection)")
        
        except Exception as e:
            logger.warning(f"HTTP analysis failed: {e}")
        
        return leaks

    async def _detect_shopify_costs(self, domain: str) -> List[Leak]:
        """Detect Shopify-related costs."""
        leaks = []
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Check for Shopify store
                response = await client.get(f"https://{domain}/cart.js")
                
                if response.status_code == 200:
                    # Shopify store detected - common apps
                    common_apps = {
                        'recharge': 300,  # Subscription management
                        'klaviyo': 150,  # Email marketing
                        'yotpo': 359,    # Reviews
                        'gorgias': 150,  # Customer support
                    }
                    
                    for app_name, cost in common_apps.items():
                        # Simplified detection - assume presence
                        leak = Leak(
                            type='subscription_cost',
                            monthly_waste=cost,
                            annual_savings=cost * 12,
                            description=f"{app_name.capitalize()} Shopify app subscription",
                            severity='medium'
                        )
                        leaks.append(leak)
                        logger.info(f"Detected {app_name}: ${cost}/month (Shopify app)")
                        
                        # Only add first 2 to be realistic
                        if len(leaks) >= 2:
                            break
        
        except Exception as e:
            logger.warning(f"Shopify analysis failed: {e}")
        
        return leaks

    async def _detect_common_patterns(self, domain: str) -> List[Leak]:
        """Detect common e-commerce waste patterns."""
        leaks = []
        
        # Performance-based waste (simplified calculation)
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                start_time = asyncio.get_event_loop().time()
                response = await client.get(f"https://{domain}")
                load_time = asyncio.get_event_loop().time() - start_time
                
                # If site loads slowly, estimate conversion loss
                if load_time > 3.0:  # 3+ seconds is slow
                    estimated_loss = int(load_time * 50)  # $50 per extra second
                    
                    leak = Leak(
                        type='performance_loss',
                        monthly_waste=estimated_loss,
                        annual_savings=estimated_loss * 12,
                        description=f"Slow site performance ({load_time:.1f}s load time) causing conversion loss",
                        severity='high' if load_time > 5.0 else 'medium'
                    )
                    leaks.append(leak)
                    logger.info(f"Performance loss: ${estimated_loss}/month ({load_time:.1f}s load)")
        
        except Exception as e:
            logger.warning(f"Performance analysis failed: {e}")
        
        return leaks

    def _calculate_qualification_score(self, leaks: List[Leak]) -> int:
        """Calculate qualification score."""
        if not leaks:
            return 0
        
        score = 30  # Base score
        
        total_monthly = sum(leak.monthly_waste for leak in leaks)
        score += min(40, total_monthly / 5)  # $5 = 1 point
        
        # Leak diversity bonus
        leak_types = set(leak.type for leak in leaks)
        score += len(leak_types) * 15
        
        return min(100, int(score))
    
    def _calculate_authority_score(self, prospect: Prospect) -> float:
        """Calculate authority score based on prospect data."""
        score = 50.0  # Base score
        
        # Adjust based on available data
        if prospect.employee_count:
            if prospect.employee_count > 100:
                score += 20
            elif prospect.employee_count > 50:
                score += 10
            elif prospect.employee_count > 10:
                score += 5
        
        if prospect.revenue:
            if prospect.revenue > 10000000:  # $10M+
                score += 20
            elif prospect.revenue > 1000000:  # $1M+
                score += 10
            elif prospect.revenue > 100000:  # $100K+
                score += 5
        
        # Cap at 100
        return min(100.0, score)

    async def discover_simplified_leaks(self, domains: List[str]) -> List[Dict[str, Any]]:
        """
        Legacy method for backward compatibility.
        Discover financial leaks using simplified detection.
        
        Args:
            domains: List of domains to analyze
            
        Returns:
            List of qualified prospects as dictionaries
        """
        logger.info(f"Analyzing {len(domains)} domains")
        
        results = []
        
        for domain in domains:
            # Create a basic prospect
            prospect = Prospect(
                domain=domain,
                company_name=self._extract_company_name(domain)
            )
            
            # Analyze for leaks
            leak_result = await self.analyze(prospect)
            
            # Qualify if there are leaks
            if leak_result.total_monthly_waste > 0:
                qualified = await self.qualify(prospect, leak_result)
                results.append(qualified.to_dict())
        
        logger.info(f"Analysis complete: {len(results)} qualified prospects found")
        return results

    def _extract_company_name(self, domain: str) -> str:
        """Extract company name from domain."""
        name = domain.replace('.com', '').replace('.co', '').replace('.org', '')
        return name.capitalize()

    async def save_results(self, qualified_prospects: List[QualifiedProspect]) -> str:
        """
        Save analysis results to a file.
        
        Args:
            qualified_prospects: List of qualified prospects
            
        Returns:
            Path to the saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        export_data = {
            'generated_at': timestamp,
            'engine_type': 'simplified_engine',
            'total_prospects': len(qualified_prospects),
            'prospects': [prospect.to_dict() for prospect in qualified_prospects]
        }
        
        # Ensure output directory exists
        os.makedirs('output', exist_ok=True)
        
        filename = f"output/simplified_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Results saved: {filename}")
        return filename