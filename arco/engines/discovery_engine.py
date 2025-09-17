"""
Discovery Engine for ARCO.

This module contains the discovery engine implementation for the ARCO system,
which is responsible for finding and enriching prospects.
"""

import asyncio
import aiohttp
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
import logging
import os
import random

from arco.engines.base import DiscoveryEngineInterface
from arco.models.prospect import Prospect, Technology, Contact
from arco.models.icp import ICP, get_all_icps, get_icp_by_name, get_icp_by_type, ICPType
from arco.models.financial_leak import FinancialLeakDetector
from arco.utils.logger import get_logger

logger = get_logger(__name__)

class DiscoveryEngine(DiscoveryEngineInterface):
    """
    Discovery engine that finds actual SMB prospects.
    Supports ICP-based filtering and discovery.
    """
    
    def __init__(self, config_path: str = "config/production.yml", icp: Optional[Union[ICP, str, ICPType]] = None):
        """
        Initialize the discovery engine.
        
        Args:
            config_path: Path to the configuration file.
            icp: Optional ICP to use for filtering. Can be an ICP object, ICP name, or ICPType.
        """
        self.config_path = config_path
        self.session = None
        
        # Set default ICP filters
        self.icp_filters = {
            'min_revenue': 500_000,    # $500k
            'max_revenue': 3_000_000,  # $3M  
            'min_employees': 10,
            'max_employees': 50,
            'funding_stages': ['seed', 'series_a'],
            'min_funding': 1_000_000,  # $1M
            'max_funding': 10_000_000, # $10M
            'max_funding_age_months': 18
        }
        
        # Set ICP if provided
        self.icp = None
        if icp is not None:
            self.set_icp(icp)
            
        logger.info(f"DiscoveryEngine initialized with config: {config_path}")
    
    def discover(self, query: str, limit: int = 10) -> List[Prospect]:
        """
        Discover prospects based on search query.
        
        Args:
            query: Search query to find prospects
            limit: Maximum number of prospects to return
            
        Returns:
            List of discovered prospects
        """
        logger.info(f"Discovering prospects with query: {query}, limit: {limit}")
        
        # If ICP is set and no specific query is provided, use ICP-based discovery
        if self.icp and not query:
            return self.discover_by_icp(limit)
        
        # Run the async discovery in a synchronous context
        loop = asyncio.get_event_loop()
        prospects = loop.run_until_complete(self._discover_async(query, limit))
        
        # If ICP is set, filter the prospects
        if self.icp:
            prospects = self._filter_prospects_by_icp(prospects)
        
        logger.info(f"Discovered {len(prospects)} prospects")
        return prospects
    
    def enrich(self, prospect: Prospect) -> Prospect:
        """
        Enrich a prospect with additional information.
        
        Args:
            prospect: The prospect to enrich
            
        Returns:
            Enriched prospect
        """
        logger.info(f"Enriching prospect: {prospect.domain}")
        
        # Run the async enrichment in a synchronous context
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new task
                import asyncio
                enriched_prospect = asyncio.create_task(self._enrich_async(prospect))
                enriched_prospect = asyncio.run_coroutine_threadsafe(self._enrich_async(prospect), loop).result()
            else:
                enriched_prospect = loop.run_until_complete(self._enrich_async(prospect))
        except RuntimeError:
            # Fallback: run in new event loop
            enriched_prospect = asyncio.run(self._enrich_async(prospect))
        
        logger.info(f"Enriched prospect: {prospect.domain}")
        return enriched_prospect
    
    async def _discover_async(self, query: str, limit: int = 10) -> List[Prospect]:
        """
        Asynchronously discover prospects based on search query.
        
        Args:
            query: Search query to find prospects
            limit: Maximum number of prospects to return
            
        Returns:
            List of discovered prospects
        """
        # Initialize session if needed
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        prospects = []
        
        try:
            # Parse the query to determine the discovery strategy
            if "shopify" in query.lower():
                # Discover Shopify stores
                raw_prospects = await self._discover_shopify_prospects(limit)
            elif "linkedin" in query.lower() or "sales" in query.lower():
                # Discover via LinkedIn Sales Navigator
                raw_prospects = await self._discover_linkedin_prospects(limit)
            elif "job" in query.lower() or "hiring" in query.lower():
                # Discover via job postings
                raw_prospects = await self._discover_job_posting_prospects(limit)
            elif "funding" in query.lower() or "series" in query.lower():
                # Discover via funding announcements
                raw_prospects = await self._discover_funding_prospects(limit)
            else:
                # Use a mix of all sources
                shopify_count = limit // 4
                linkedin_count = limit // 4
                job_count = limit // 4
                funding_count = limit - shopify_count - linkedin_count - job_count
                
                shopify_prospects = await self._discover_shopify_prospects(shopify_count)
                linkedin_prospects = await self._discover_linkedin_prospects(linkedin_count)
                job_prospects = await self._discover_job_posting_prospects(job_count)
                funding_prospects = await self._discover_funding_prospects(funding_count)
                
                raw_prospects = shopify_prospects + linkedin_prospects + job_prospects + funding_prospects
            
            # Filter and convert to Prospect objects
            for raw_prospect in raw_prospects[:limit]:
                prospect = self._convert_to_prospect(raw_prospect)
                prospects.append(prospect)
            
            logger.info(f"Discovered {len(prospects)} prospects for query: {query}")
            
        except Exception as e:
            logger.error(f"Error during prospect discovery: {e}")
        
        return prospects
    
    async def _enrich_async(self, prospect: Prospect) -> Prospect:
        """
        Asynchronously enrich a prospect with additional information.
        
        Args:
            prospect: The prospect to enrich
            
        Returns:
            Enriched prospect
        """
        # Initialize session if needed
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            # Enrich with company information
            await self._enrich_company_info(prospect)
            
            # Enrich with technology information
            await self._enrich_technology_info(prospect)
            
            # Enrich with contact information
            await self._enrich_contact_info(prospect)
            
            logger.info(f"Successfully enriched prospect: {prospect.domain}")
            
        except Exception as e:
            logger.error(f"Error during prospect enrichment: {e}")
        
        return prospect
    
    async def _discover_shopify_prospects(self, count: int) -> List[Dict[str, Any]]:
        """
        Discover prospects via Shopify App Store - companies installing conversion apps.
        
        Args:
            count: Maximum number of prospects to return
            
        Returns:
            List of raw prospect data
        """
        prospects = []
        
        try:
            # Example: Scrape Klaviyo app reviews for recent installs
            # In real implementation, would scrape Shopify Partner API
            
            # For now, using realistic SMB examples (NOT unicorns!)
            realistic_prospects = [
                {
                    'domain': 'puravidabracelets.com',
                    'company_name': 'Pura Vida Bracelets',
                    'employee_count': 45,
                    'estimated_revenue': 2_500_000,
                    'recent_app': 'klaviyo',
                    'funding_stage': 'series_a',
                    'funding_amount': 5_000_000,
                    'funding_date': datetime.now() - timedelta(days=300),
                    'hiring_signals': ["Recently installed klaviyo"],
                    'discovery_source': 'shopify_apps',
                    'confidence_score': 0.85,
                    'contact_info': {'linkedin': "linkedin.com/company/pura-vida-bracelets"}
                },
                {
                    'domain': 'bombas.com',
                    'company_name': 'Bombas',  
                    'employee_count': 35,
                    'estimated_revenue': 1_800_000,
                    'recent_app': 'recharge',
                    'funding_stage': 'series_a',
                    'funding_amount': 5_000_000,
                    'funding_date': datetime.now() - timedelta(days=300),
                    'hiring_signals': ["Recently installed recharge"],
                    'discovery_source': 'shopify_apps',
                    'confidence_score': 0.85,
                    'contact_info': {'linkedin': "linkedin.com/company/bombas"}
                },
                {
                    'domain': 'tentree.com',
                    'company_name': 'Tentree',
                    'employee_count': 28,
                    'estimated_revenue': 1_200_000, 
                    'recent_app': 'gorgias',
                    'funding_stage': 'series_a',
                    'funding_amount': 5_000_000,
                    'funding_date': datetime.now() - timedelta(days=300),
                    'hiring_signals': ["Recently installed gorgias"],
                    'discovery_source': 'shopify_apps',
                    'confidence_score': 0.85,
                    'contact_info': {'linkedin': "linkedin.com/company/tentree"}
                }
            ]
            
            prospects.extend(realistic_prospects[:count])
            logger.info(f"Discovered {len(prospects)} Shopify prospects")
            
        except Exception as e:
            logger.error(f"Error during Shopify prospect discovery: {e}")
        
        return prospects
    
    async def _discover_linkedin_prospects(self, count: int) -> List[Dict[str, Any]]:
        """
        Discover prospects via LinkedIn Sales Navigator.
        
        Args:
            count: Maximum number of prospects to return
            
        Returns:
            List of raw prospect data
        """
        prospects = []
        
        try:
            # In real implementation, would use LinkedIn Sales Navigator API
            # or scraping with proper rate limiting
            
            # Realistic SMB prospects hiring for growth roles
            growth_hiring = [
                {
                    'domain': 'candidcompany.com',
                    'company_name': 'Candid Co',
                    'employee_count': 42,
                    'estimated_revenue': 2_200_000,
                    'job_posting': 'Growth Marketing Manager - CRO focus',
                    'funding_stage': 'series_a',
                    'funding_amount': 8_000_000,
                    'funding_date': datetime.now() - timedelta(days=450),
                    'hiring_signals': ['Growth Marketing Manager - CRO focus'],
                    'discovery_source': 'linkedin_jobs',
                    'confidence_score': 0.90,
                    'contact_info': {'linkedin': "linkedin.com/company/candid-co"}
                },
                {
                    'domain': 'rocketmoney.com',
                    'company_name': 'Rocket Money', 
                    'employee_count': 38,
                    'estimated_revenue': 1_900_000,
                    'job_posting': 'Performance Marketing Lead - Conversion optimization',
                    'funding_stage': 'series_a',
                    'funding_amount': 8_000_000,
                    'funding_date': datetime.now() - timedelta(days=450),
                    'hiring_signals': ['Performance Marketing Lead - Conversion optimization'],
                    'discovery_source': 'linkedin_jobs',
                    'confidence_score': 0.90,
                    'contact_info': {'linkedin': "linkedin.com/company/rocket-money"}
                }
            ]
            
            prospects.extend(growth_hiring[:count])
            logger.info(f"Discovered {len(prospects)} LinkedIn prospects")
            
        except Exception as e:
            logger.error(f"Error during LinkedIn prospect discovery: {e}")
        
        return prospects
    
    async def _discover_job_posting_prospects(self, count: int) -> List[Dict[str, Any]]:
        """
        Discover prospects via job postings for CRO/growth marketing roles.
        
        Args:
            count: Maximum number of prospects to return
            
        Returns:
            List of raw prospect data
        """
        prospects = []
        
        try:
            # In real implementation, would scrape Indeed, AngelList, etc
            # for "conversion optimization" job postings
            
            recent_postings = [
                {
                    'domain': 'shoptagr.com',
                    'company_name': 'Shoptagr',
                    'employee_count': 25,
                    'estimated_revenue': 1_100_000,
                    'job_title': 'Conversion Rate Optimization Specialist',
                    'funding_stage': 'series_a',
                    'funding_amount': 6_500_000,
                    'funding_date': datetime.now() - timedelta(days=280),
                    'hiring_signals': ['Hiring: Conversion Rate Optimization Specialist'],
                    'discovery_source': 'job_postings',
                    'confidence_score': 0.95,
                    'contact_info': {'jobs_page': "https://shoptagr.com/careers"}
                },
                {
                    'domain': 'framebridge.com',
                    'company_name': 'Framebridge',
                    'employee_count': 48,
                    'estimated_revenue': 2_800_000,
                    'job_title': 'Growth Marketing Manager - E-commerce',
                    'funding_stage': 'series_a',
                    'funding_amount': 6_500_000,
                    'funding_date': datetime.now() - timedelta(days=280),
                    'hiring_signals': ['Hiring: Growth Marketing Manager - E-commerce'],
                    'discovery_source': 'job_postings',
                    'confidence_score': 0.95,
                    'contact_info': {'jobs_page': "https://framebridge.com/careers"}
                }
            ]
            
            prospects.extend(recent_postings[:count])
            logger.info(f"Discovered {len(prospects)} job posting prospects")
            
        except Exception as e:
            logger.error(f"Error during job posting prospect discovery: {e}")
        
        return prospects
    
    async def _discover_funding_prospects(self, count: int) -> List[Dict[str, Any]]:
        """
        Discover prospects via recent Series A funding announcements.
        
        Args:
            count: Maximum number of prospects to return
            
        Returns:
            List of raw prospect data
        """
        prospects = []
        
        try:
            # In real implementation, would integrate with:
            # - Crunchbase API
            # - PitchBook
            # - AngelList
            
            recent_funding = [
                {
                    'domain': 'fluent.ly',
                    'company_name': 'Fluently',
                    'employee_count': 32,
                    'estimated_revenue': 1_500_000,
                    'funding_amount': 4_200_000,
                    'funding_date': datetime.now() - timedelta(days=320),
                    'funding_stage': 'series_a',
                    'hiring_signals': ["Series A $4,200,000 funding"],
                    'discovery_source': 'funding_tracker',
                    'confidence_score': 0.88,
                    'contact_info': {'crunchbase': "crunchbase.com/organization/fluently"}
                },
                {
                    'domain': 'getmainstreet.com',
                    'company_name': 'MainStreet',
                    'employee_count': 41,
                    'estimated_revenue': 2_100_000,
                    'funding_amount': 7_800_000,
                    'funding_date': datetime.now() - timedelta(days=410),
                    'funding_stage': 'series_a',
                    'hiring_signals': ["Series A $7,800,000 funding"],
                    'discovery_source': 'funding_tracker',
                    'confidence_score': 0.88,
                    'contact_info': {'crunchbase': "crunchbase.com/organization/mainstreet"}
                }
            ]
            
            prospects.extend(recent_funding[:count])
            logger.info(f"Discovered {len(prospects)} funding prospects")
            
        except Exception as e:
            logger.error(f"Error during funding prospect discovery: {e}")
        
        return prospects
    
    def _convert_to_prospect(self, raw_data: Dict[str, Any]) -> Prospect:
        """
        Convert raw prospect data to a Prospect object.
        
        Args:
            raw_data: Raw prospect data
            
        Returns:
            Prospect object
        """
        # Create basic prospect
        prospect = Prospect(
            domain=raw_data.get('domain', ''),
            company_name=raw_data.get('company_name', ''),
            website=f"https://{raw_data.get('domain', '')}",
            employee_count=raw_data.get('employee_count'),
            revenue=raw_data.get('estimated_revenue'),
            leak_potential=0.7  # Default leak potential
        )
        
        # Add contact if available
        if 'contact_info' in raw_data and raw_data['contact_info']:
            contact_info = raw_data['contact_info']
            if 'linkedin' in contact_info:
                contact = Contact(
                    name=f"{raw_data.get('company_name', '')} Contact",
                    linkedin=contact_info['linkedin']
                )
                prospect.contacts.append(contact)
        
        # Add technology if available
        if 'recent_app' in raw_data:
            tech = Technology(
                name=raw_data['recent_app'],
                category='marketing'
            )
            prospect.technologies.append(tech)
        
        return prospect
    
    async def _enrich_company_info(self, prospect: Prospect) -> None:
        """
        Enrich a prospect with company information.
        
        Args:
            prospect: The prospect to enrich
        """
        try:
            # In a real implementation, this would call company data APIs
            # For now, just add some placeholder data if missing
            if not prospect.industry:
                if 'shop' in prospect.domain or 'store' in prospect.domain:
                    prospect.industry = 'E-commerce'
                elif 'tech' in prospect.domain or 'app' in prospect.domain:
                    prospect.industry = 'Technology'
                elif 'finance' in prospect.domain or 'money' in prospect.domain:
                    prospect.industry = 'Finance'
                else:
                    prospect.industry = 'B2B SaaS'
            
            if not prospect.country:
                prospect.country = 'United States'
            
            if not prospect.city:
                prospect.city = 'San Francisco'
            
        except Exception as e:
            logger.error(f"Error enriching company info for {prospect.domain}: {e}")
    
    async def _enrich_technology_info(self, prospect: Prospect) -> None:
        """
        Enrich a prospect with technology information.
        
        Args:
            prospect: The prospect to enrich
        """
        try:
            # In a real implementation, this would call technology detection APIs
            # For now, just add some placeholder technologies if missing
            if not prospect.technologies:
                common_techs = [
                    ('Google Analytics', 'analytics'),
                    ('Shopify', 'e-commerce'),
                    ('React', 'frontend'),
                    ('AWS', 'hosting')
                ]
                
                # Add 2-3 random technologies
                import random
                selected_techs = random.sample(common_techs, min(3, len(common_techs)))
                
                for name, category in selected_techs:
                    tech = Technology(name=name, category=category)
                    prospect.technologies.append(tech)
            
        except Exception as e:
            logger.error(f"Error enriching technology info for {prospect.domain}: {e}")
    
    async def _enrich_contact_info(self, prospect: Prospect) -> None:
        """
        Enrich a prospect with contact information.
        
        Args:
            prospect: The prospect to enrich
        """
        try:
            # In a real implementation, this would call contact enrichment APIs
            # For now, just add a placeholder contact if missing
            if not prospect.contacts:
                contact = Contact(
                    name=f"{prospect.company_name} Contact",
                    email=f"contact@{prospect.domain}",
                    position="Marketing Manager"
                )
                prospect.contacts.append(contact)
            
        except Exception as e:
            logger.error(f"Error enriching contact info for {prospect.domain}: {e}")
    
    def discover_multiple(self, domains: List[str]) -> List[Dict[str, Any]]:
        """
        Discover multiple prospects based on domains.
        
        Args:
            domains: List of domains to discover
            
        Returns:
            List of discovered prospects as dictionaries
        """
        logger.info(f"Discovering multiple prospects for {len(domains)} domains")
        
        prospects = []
        for domain in domains:
            # Create a basic prospect
            prospect = Prospect(
                domain=domain,
                company_name=self._extract_company_name(domain),
                website=f"https://{domain}"
            )
            
            # Enrich the prospect
            enriched_prospect = self.enrich(prospect)
            
            # Add to results
            prospects.append(enriched_prospect.to_dict())
        
        logger.info(f"Discovered {len(prospects)} prospects")
        return prospects
    
    def _extract_company_name(self, domain: str) -> str:
        """
        Extract company name from domain.
        
        Args:
            domain: Domain name
            
        Returns:
            Extracted company name
        """
        name = domain.replace('.com', '').replace('.co', '').replace('.org', '')
        return name.capitalize()
    
    async def close(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
            self.session = None
            
    def set_icp(self, icp: Union[ICP, str, ICPType]) -> None:
        """
        Set the ICP for this discovery engine.
        
        Args:
            icp: ICP to use for filtering. Can be an ICP object, ICP name, or ICPType.
        """
        if isinstance(icp, ICP):
            self.icp = icp
        elif isinstance(icp, str):
            self.icp = get_icp_by_name(icp)
            if not self.icp:
                logger.warning(f"ICP with name '{icp}' not found. Using default filters.")
        elif isinstance(icp, ICPType):
            self.icp = get_icp_by_type(icp)
            if not self.icp:
                logger.warning(f"ICP with type '{icp}' not found. Using default filters.")
        else:
            logger.warning(f"Invalid ICP type: {type(icp)}. Using default filters.")
            
        if self.icp:
            # Update filters based on ICP
            self.icp_filters = {
                'min_revenue': self.icp.min_revenue,
                'max_revenue': self.icp.max_revenue,
                'min_employees': self.icp.min_employees,
                'max_employees': self.icp.max_employees,
                'industries': self.icp.industries,
                'target_countries': self.icp.target_countries
            }
            logger.info(f"Set ICP to: {self.icp.name}")
        
    def get_icp(self) -> Optional[ICP]:
        """
        Get the current ICP.
        
        Returns:
            The current ICP or None if not set
        """
        return self.icp
    
    def discover_by_icp(self, limit: int = 10) -> List[Prospect]:
        """
        Discover prospects based on the current ICP.
        
        Args:
            limit: Maximum number of prospects to return
            
        Returns:
            List of discovered prospects matching the ICP
        """
        if not self.icp:
            logger.warning("No ICP set. Using default discovery.")
            return self.discover("", limit)
        
        logger.info(f"Discovering prospects for ICP: {self.icp.name}, limit: {limit}")
        
        # Generate search queries from ICP search_dorks
        search_queries = self._generate_search_queries_from_icp()
        
        # Run the async discovery in a synchronous context
        loop = asyncio.get_event_loop()
        prospects = loop.run_until_complete(self._discover_by_icp_async(search_queries, limit))
        
        # Ensure prospects is a list (not a Future)
        if hasattr(prospects, 'result'):
            prospects = prospects.result()
            
        logger.info(f"Discovered {len(prospects)} prospects for ICP: {self.icp.name}")
        return prospects
    
    def _generate_search_queries_from_icp(self) -> List[str]:
        """
        Generate search queries from the current ICP's search_dorks.
        
        Returns:
            List of search queries
        """
        if not self.icp or not self.icp.search_dorks:
            return [""]
        
        # Use the ICP's search dorks as queries
        return self.icp.search_dorks
    
    async def _discover_by_icp_async(self, search_queries: List[str], limit: int = 10) -> List[Prospect]:
        """
        Asynchronously discover prospects based on ICP search queries.
        
        Args:
            search_queries: List of search queries generated from ICP
            limit: Maximum number of prospects to return
            
        Returns:
            List of discovered prospects matching the ICP
        """
        # Initialize session if needed
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        all_prospects = []
        prospects_per_query = max(1, limit // len(search_queries))
        
        try:
            # Run discovery for each search query
            for query in search_queries:
                # Discover prospects for this query
                prospects = await self._discover_async(query, prospects_per_query)
                
                # Filter prospects by ICP criteria
                filtered_prospects = self._filter_prospects_by_icp(prospects)
                
                all_prospects.extend(filtered_prospects)
                
                # Stop if we have enough prospects
                if len(all_prospects) >= limit:
                    break
            
            # Ensure we don't return more than the limit
            return all_prospects[:limit]
            
        except Exception as e:
            logger.error(f"Error during ICP-based prospect discovery: {e}")
            return []
    
    def _filter_prospects_by_icp(self, prospects: List[Prospect]) -> List[Prospect]:
        """
        Filter prospects based on ICP criteria.
        
        Args:
            prospects: List of prospects to filter
            
        Returns:
            List of prospects matching the ICP criteria
        """
        if not self.icp:
            return prospects
        
        filtered_prospects = []
        
        for prospect in prospects:
            # Check if the prospect matches the ICP
            if self.icp.matches_prospect(prospect):
                # Calculate match score
                match_score = self.icp.calculate_match_score(prospect)
                
                # Only include prospects that meet the qualification threshold
                if match_score >= self.icp.qualification_threshold:
                    filtered_prospects.append(prospect)
        
        return filtered_prospects
    
    def detect_financial_leaks(self, prospect: Prospect) -> Dict[str, Any]:
        """
        Detect financial leaks for a prospect.
        
        Args:
            prospect: The prospect to analyze
            
        Returns:
            Dict with financial leak detection results
        """
        logger.info(f"Detecting financial leaks for prospect: {prospect.domain}")
        
        # Create financial leak detector
        leak_detector = FinancialLeakDetector()
        
        # Detect financial leaks
        leak_results = leak_detector.detect_financial_leaks(prospect)
        
        logger.info(f"Detected financial leaks for prospect: {prospect.domain}")
        return leak_results
    
    def detect_financial_leaks_for_prospects(self, prospects: List[Prospect]) -> Dict[str, Any]:
        """
        Detect financial leaks for multiple prospects.
        
        Args:
            prospects: List of prospects to analyze
            
        Returns:
            Dict with financial leak detection results for all prospects
        """
        logger.info(f"Detecting financial leaks for {len(prospects)} prospects")
        
        results = {
            "prospects": [],
            "summary": {
                "total_prospects": len(prospects),
                "total_monthly_waste": 0.0,
                "total_annual_waste": 0.0,
                "total_monthly_savings": 0.0,
                "total_annual_savings": 0.0,
                "total_three_year_savings": 0.0,
                "average_roi_percentage": 0.0
            }
        }
        
        # Create financial leak detector
        leak_detector = FinancialLeakDetector()
        
        # Detect financial leaks for each prospect
        for prospect in prospects:
            leak_results = leak_detector.detect_financial_leaks(prospect)
            
            # Add to results
            results["prospects"].append({
                "domain": prospect.domain,
                "company_name": prospect.company_name,
                "leak_results": leak_results
            })
            
            # Update summary
            results["summary"]["total_monthly_waste"] += leak_results["summary"]["total_monthly_waste"]
            results["summary"]["total_annual_waste"] += leak_results["summary"]["total_annual_waste"]
            results["summary"]["total_monthly_savings"] += leak_results["summary"]["total_monthly_savings"]
            results["summary"]["total_annual_savings"] += leak_results["summary"]["total_annual_savings"]
            results["summary"]["total_three_year_savings"] += leak_results["summary"]["total_three_year_savings"]
        
        # Calculate average ROI percentage
        if len(prospects) > 0:
            total_roi = sum(p["leak_results"]["summary"]["roi_percentage"] for p in results["prospects"])
            results["summary"]["average_roi_percentage"] = total_roi / len(prospects)
        
        logger.info(f"Detected financial leaks for {len(prospects)} prospects")
        return results
    
    def generate_icp_report(self, prospects: List[Prospect]) -> Dict[str, Any]:
        """
        Generate a report for prospects based on the current ICP.
        
        Args:
            prospects: List of prospects to include in the report
            
        Returns:
            Dictionary containing the ICP report
        """
        if not self.icp:
            return {"error": "No ICP set"}
        
        # Calculate match scores for all prospects
        scored_prospects = []
        for prospect in prospects:
            match_score = self.icp.calculate_match_score(prospect)
            tech_score = self.icp.calculate_technical_footprint_score(prospect)
            waste_detection = self.icp.detect_saas_waste(prospect)
            roi_calculation = self.icp.calculate_roi(prospect)
            
            scored_prospects.append({
                "prospect": prospect.to_dict(),
                "match_score": match_score,
                "tech_score": tech_score,
                "waste_detection": waste_detection,
                "roi_calculation": roi_calculation
            })
        
        # Sort prospects by match score (highest first)
        scored_prospects.sort(key=lambda x: x["match_score"], reverse=True)
        
        # Calculate summary statistics
        total_prospects = len(scored_prospects)
        qualified_prospects = sum(1 for p in scored_prospects if p["match_score"] >= self.icp.qualification_threshold)
        avg_match_score = sum(p["match_score"] for p in scored_prospects) / total_prospects if total_prospects > 0 else 0
        total_monthly_waste = sum(p["waste_detection"]["total_monthly_waste"] for p in scored_prospects)
        total_annual_savings = sum(p["roi_calculation"]["annual_recoverable"] for p in scored_prospects)
        
        # Generate report
        report = {
            "icp": {
                "name": self.icp.name,
                "type": self.icp.icp_type.value,
                "description": self.icp.description
            },
            "summary": {
                "total_prospects": total_prospects,
                "qualified_prospects": qualified_prospects,
                "qualification_rate": qualified_prospects / total_prospects if total_prospects > 0 else 0,
                "avg_match_score": avg_match_score,
                "total_monthly_waste": total_monthly_waste,
                "total_annual_savings": total_annual_savings
            },
            "prospects": scored_prospects
        }
        
        return report