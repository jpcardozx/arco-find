"""
Lead Enrichment Engine for ARCO.

This module provides comprehensive lead enrichment capabilities,
going beyond basic technology detection to provide detailed company
and contact information enrichment.
"""

import logging
import asyncio
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import httpx
from dataclasses import dataclass

from arco.models.prospect import Prospect, Contact, Technology
from arco.integrations.wappalyzer import WappalyzerIntegration
from arco.utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class EnrichmentResult:
    """Result of enrichment process."""
    success: bool
    enriched_fields: List[str]
    new_technologies: List[Technology]
    new_contacts: List[Contact]
    updated_fields: Dict[str, Any]
    confidence_scores: Dict[str, float]
    errors: List[str]

class LeadEnrichmentEngine:
    """Comprehensive lead enrichment engine."""
    
    def __init__(self):
        """Initialize the enrichment engine."""
        self.wappalyzer = WappalyzerIntegration()
        self.common_domains = {
            "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", 
            "aol.com", "icloud.com", "protonmail.com"
        }
        
        # Industry keywords for classification
        self.industry_keywords = {
            "E-commerce": ["shop", "store", "retail", "commerce", "buy", "sell", "marketplace"],
            "Technology": ["tech", "software", "app", "digital", "cloud", "saas", "platform"],
            "Healthcare": ["health", "medical", "clinic", "hospital", "pharma", "wellness"],
            "Finance": ["bank", "finance", "invest", "capital", "fund", "credit", "loan"],
            "Education": ["edu", "school", "university", "college", "learn", "academy"],
            "Real Estate": ["real estate", "property", "realty", "homes", "housing"],
            "Food & Beverage": ["food", "restaurant", "cafe", "kitchen", "dining", "beverage"],
            "Fitness": ["fitness", "gym", "workout", "health", "sport", "exercise"],
            "Beauty": ["beauty", "cosmetic", "skincare", "makeup", "salon", "spa"],
            "Travel": ["travel", "hotel", "booking", "vacation", "tourism", "flight"]
        }
    
    async def enrich_prospect(self, prospect: Prospect, deep_enrichment: bool = True) -> EnrichmentResult:
        """
        Perform comprehensive prospect enrichment.
        
        Args:
            prospect: Prospect to enrich
            deep_enrichment: Whether to perform deep enrichment (slower but more comprehensive)
            
        Returns:
            EnrichmentResult with details of what was enriched
        """
        enriched_fields = []
        new_technologies = []
        new_contacts = []
        updated_fields = {}
        confidence_scores = {}
        errors = []
        
        try:
            # 1. Website and technology enrichment
            if prospect.website or prospect.domain:
                tech_result = await self._enrich_technologies(prospect)
                new_technologies.extend(tech_result["technologies"])
                if tech_result["success"]:
                    enriched_fields.append("technologies")
                    confidence_scores["technologies"] = tech_result["confidence"]
                else:
                    errors.extend(tech_result["errors"])
            
            # 2. Company information enrichment
            company_result = await self._enrich_company_info(prospect)
            if company_result["updated_fields"]:
                updated_fields.update(company_result["updated_fields"])
                enriched_fields.extend(company_result["enriched_fields"])
                confidence_scores.update(company_result["confidence_scores"])
            
            # 3. Contact enrichment
            if deep_enrichment:
                contact_result = await self._enrich_contacts(prospect)
                new_contacts.extend(contact_result["contacts"])
                if contact_result["success"]:
                    enriched_fields.append("contacts")
                    confidence_scores["contacts"] = contact_result["confidence"]
                else:
                    errors.extend(contact_result["errors"])
            
            # 4. Industry classification
            if not prospect.industry or prospect.industry == "Other":
                industry_result = self._classify_industry(prospect)
                if industry_result["industry"]:
                    updated_fields["industry"] = industry_result["industry"]
                    enriched_fields.append("industry")
                    confidence_scores["industry"] = industry_result["confidence"]
            
            # 5. Company size estimation
            if not prospect.employee_count:
                size_result = await self._estimate_company_size(prospect)
                if size_result["employee_count"]:
                    updated_fields["employee_count"] = size_result["employee_count"]
                    enriched_fields.append("employee_count")
                    confidence_scores["employee_count"] = size_result["confidence"]
            
            # 6. Revenue estimation
            if not prospect.revenue and prospect.employee_count:
                revenue_result = self._estimate_revenue(prospect)
                if revenue_result["revenue"]:
                    updated_fields["revenue"] = revenue_result["revenue"]
                    enriched_fields.append("revenue")
                    confidence_scores["revenue"] = revenue_result["confidence"]
            
            # Apply updates to prospect
            for field, value in updated_fields.items():
                setattr(prospect, field, value)
            
            prospect.technologies.extend(new_technologies)
            prospect.contacts.extend(new_contacts)
            
            success = len(enriched_fields) > 0
            
            return EnrichmentResult(
                success=success,
                enriched_fields=enriched_fields,
                new_technologies=new_technologies,
                new_contacts=new_contacts,
                updated_fields=updated_fields,
                confidence_scores=confidence_scores,
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"Error enriching prospect {prospect.domain}: {e}")
            errors.append(str(e))
            
            return EnrichmentResult(
                success=False,
                enriched_fields=[],
                new_technologies=[],
                new_contacts=[],
                updated_fields={},
                confidence_scores={},
                errors=errors
            )
    
    async def _enrich_technologies(self, prospect: Prospect) -> Dict[str, Any]:
        """Enrich technology stack information."""
        try:
            url = prospect.website or f"https://{prospect.domain}"
            
            # Get existing technology names for deduplication
            existing_tech_names = {tech.name.lower() for tech in prospect.technologies}
            
            # Use Wappalyzer for technology detection
            tech_data = await self.wappalyzer.analyze_url(url)
            
            new_technologies = []
            if "technologies" in tech_data:
                for tech_info in tech_data["technologies"]:
                    tech_name = tech_info.get("name", "")
                    if tech_name and tech_name.lower() not in existing_tech_names:
                        categories = tech_info.get("categories", [])
                        category = categories[0] if categories else "other"
                        version = tech_info.get("version", "")
                        confidence = tech_info.get("confidence", 50) / 100.0
                        
                        new_technologies.append(Technology(
                            name=tech_name,
                            category=category,
                            version=version
                        ))
            
            # If no technologies found, try HTTP header analysis
            if not new_technologies:
                header_techs = await self._analyze_http_headers(url)
                new_technologies.extend(header_techs)
            
            return {
                "success": len(new_technologies) > 0,
                "technologies": new_technologies,
                "confidence": 0.8 if new_technologies else 0.0,
                "errors": []
            }
            
        except Exception as e:
            logger.warning(f"Technology enrichment failed for {prospect.domain}: {e}")
            return {
                "success": False,
                "technologies": [],
                "confidence": 0.0,
                "errors": [str(e)]
            }
    
    async def _analyze_http_headers(self, url: str) -> List[Technology]:
        """Analyze HTTP headers for technology indicators."""
        technologies = []
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url, follow_redirects=True)
                headers = response.headers
                
                # Server header analysis
                server = headers.get("server", "").lower()
                if "nginx" in server:
                    technologies.append(Technology(name="Nginx", category="web_servers"))
                elif "apache" in server:
                    technologies.append(Technology(name="Apache", category="web_servers"))
                elif "cloudflare" in server:
                    technologies.append(Technology(name="Cloudflare", category="cdn"))
                
                # X-Powered-By header
                powered_by = headers.get("x-powered-by", "").lower()
                if "php" in powered_by:
                    technologies.append(Technology(name="PHP", category="programming_languages"))
                elif "asp.net" in powered_by:
                    technologies.append(Technology(name="ASP.NET", category="web_frameworks"))
                
                # Content analysis for common platforms
                content = response.text.lower()
                if "shopify" in content:
                    technologies.append(Technology(name="Shopify", category="ecommerce"))
                elif "wordpress" in content or "wp-content" in content:
                    technologies.append(Technology(name="WordPress", category="cms"))
                elif "woocommerce" in content:
                    technologies.append(Technology(name="WooCommerce", category="ecommerce"))
                
        except Exception as e:
            logger.debug(f"HTTP header analysis failed for {url}: {e}")
        
        return technologies
    
    async def _enrich_company_info(self, prospect: Prospect) -> Dict[str, Any]:
        """Enrich company information."""
        updated_fields = {}
        enriched_fields = []
        confidence_scores = {}
        
        # Improve company name if missing or generic
        if not prospect.company_name or prospect.company_name == prospect.domain:
            improved_name = self._improve_company_name(prospect.domain)
            if improved_name != prospect.domain:
                updated_fields["company_name"] = improved_name
                enriched_fields.append("company_name")
                confidence_scores["company_name"] = 0.7
        
        # Infer location from domain TLD
        if not prospect.country:
            country = self._infer_country_from_domain(prospect.domain)
            if country:
                updated_fields["country"] = country
                enriched_fields.append("country")
                confidence_scores["country"] = 0.6
        
        # Generate description if missing
        if not prospect.description:
            description = self._generate_description(prospect)
            if description:
                updated_fields["description"] = description
                enriched_fields.append("description")
                confidence_scores["description"] = 0.5
        
        return {
            "updated_fields": updated_fields,
            "enriched_fields": enriched_fields,
            "confidence_scores": confidence_scores
        }
    
    def _improve_company_name(self, domain: str) -> str:
        """Improve company name based on domain."""
        # Remove common TLDs and subdomains
        name = domain.replace("www.", "").split(".")[0]
        
        # Convert to title case and handle common patterns
        name = name.replace("-", " ").replace("_", " ")
        
        # Handle common abbreviations
        words = name.split()
        improved_words = []
        
        for word in words:
            if word.lower() in ["inc", "llc", "ltd", "corp", "co"]:
                improved_words.append(word.upper())
            else:
                improved_words.append(word.capitalize())
        
        return " ".join(improved_words)
    
    def _infer_country_from_domain(self, domain: str) -> Optional[str]:
        """Infer country from domain TLD."""
        tld_country_map = {
            ".uk": "United Kingdom",
            ".ca": "Canada",
            ".au": "Australia",
            ".de": "Germany",
            ".fr": "France",
            ".jp": "Japan",
            ".br": "Brazil",
            ".in": "India",
            ".mx": "Mexico",
            ".es": "Spain",
            ".it": "Italy",
            ".nl": "Netherlands",
            ".se": "Sweden",
            ".no": "Norway",
            ".dk": "Denmark"
        }
        
        for tld, country in tld_country_map.items():
            if domain.endswith(tld):
                return country
        
        # Default to US for .com, .org, .net
        if any(domain.endswith(tld) for tld in [".com", ".org", ".net"]):
            return "United States"
        
        return None
    
    def _generate_description(self, prospect: Prospect) -> Optional[str]:
        """Generate a basic description based on available data."""
        if prospect.industry and prospect.company_name:
            return f"{prospect.company_name} is a company in the {prospect.industry} industry."
        elif prospect.industry:
            return f"A company operating in the {prospect.industry} industry."
        elif prospect.company_name:
            return f"{prospect.company_name} is a business organization."
        
        return None
    
    async def _enrich_contacts(self, prospect: Prospect) -> Dict[str, Any]:
        """Enrich contact information."""
        new_contacts = []
        
        try:
            # If no contacts exist, try to generate common ones
            if not prospect.contacts:
                common_contacts = self._generate_common_contacts(prospect)
                new_contacts.extend(common_contacts)
            else:
                # Improve existing contacts
                for contact in prospect.contacts:
                    self._improve_contact_info(contact, prospect)
            
            return {
                "success": len(new_contacts) > 0,
                "contacts": new_contacts,
                "confidence": 0.3,  # Low confidence for generated contacts
                "errors": []
            }
            
        except Exception as e:
            return {
                "success": False,
                "contacts": [],
                "confidence": 0.0,
                "errors": [str(e)]
            }
    
    def _generate_common_contacts(self, prospect: Prospect) -> List[Contact]:
        """Generate common contact patterns."""
        contacts = []
        domain = prospect.domain
        
        # Skip if it's a common email domain
        if any(common_domain in domain for common_domain in self.common_domains):
            return contacts
        
        # Common email patterns
        common_patterns = [
            ("info", "General Information"),
            ("contact", "General Contact"),
            ("hello", "General Inquiry"),
            ("sales", "Sales Team"),
            ("support", "Support Team")
        ]
        
        for email_prefix, name in common_patterns:
            contacts.append(Contact(
                name=name,
                email=f"{email_prefix}@{domain}",
                position=name
            ))
        
        return contacts
    
    def _improve_contact_info(self, contact: Contact, prospect: Prospect) -> None:
        """Improve existing contact information."""
        # Standardize position titles
        if contact.position:
            position_lower = contact.position.lower()
            
            # Standardize common titles
            title_mappings = {
                "chief executive officer": "CEO",
                "chief technology officer": "CTO",
                "chief marketing officer": "CMO",
                "chief financial officer": "CFO",
                "vice president": "VP",
                "president": "President",
                "founder": "Founder",
                "co-founder": "Co-Founder",
                "owner": "Owner"
            }
            
            for full_title, short_title in title_mappings.items():
                if full_title in position_lower:
                    contact.position = short_title
                    break
        
        # Validate email format
        if contact.email and "@" in contact.email:
            email_parts = contact.email.split("@")
            if len(email_parts) == 2 and "." in email_parts[1]:
                # Email looks valid
                pass
            else:
                # Invalid email format
                contact.email = None
    
    def _classify_industry(self, prospect: Prospect) -> Dict[str, Any]:
        """Classify industry based on available data."""
        text_to_analyze = " ".join(filter(None, [
            prospect.domain,
            prospect.company_name,
            prospect.description,
            prospect.website
        ])).lower()
        
        industry_scores = {}
        
        for industry, keywords in self.industry_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_to_analyze:
                    score += 1
            
            if score > 0:
                industry_scores[industry] = score
        
        if industry_scores:
            best_industry = max(industry_scores, key=industry_scores.get)
            confidence = min(industry_scores[best_industry] / len(self.industry_keywords[best_industry]), 1.0)
            
            return {
                "industry": best_industry,
                "confidence": confidence
            }
        
        return {"industry": None, "confidence": 0.0}
    
    async def _estimate_company_size(self, prospect: Prospect) -> Dict[str, Any]:
        """Estimate company size based on available indicators."""
        # This is a simplified estimation - in a real system, you'd use
        # external APIs like Clearbit, ZoomInfo, etc.
        
        size_indicators = []
        
        # Technology stack size indicator
        tech_count = len(prospect.technologies)
        if tech_count > 20:
            size_indicators.append(200)  # Large tech stack suggests larger company
        elif tech_count > 10:
            size_indicators.append(50)
        elif tech_count > 5:
            size_indicators.append(20)
        else:
            size_indicators.append(10)
        
        # Industry-based estimation
        if prospect.industry:
            industry_size_map = {
                "Technology": 75,
                "Finance": 100,
                "Healthcare": 150,
                "E-commerce": 25,
                "Education": 200,
                "Real Estate": 15
            }
            
            if prospect.industry in industry_size_map:
                size_indicators.append(industry_size_map[prospect.industry])
        
        if size_indicators:
            estimated_size = int(sum(size_indicators) / len(size_indicators))
            confidence = 0.4  # Low confidence for estimation
            
            return {
                "employee_count": estimated_size,
                "confidence": confidence
            }
        
        return {"employee_count": None, "confidence": 0.0}
    
    def _estimate_revenue(self, prospect: Prospect) -> Dict[str, Any]:
        """Estimate revenue based on employee count and industry."""
        if not prospect.employee_count:
            return {"revenue": None, "confidence": 0.0}
        
        # Industry revenue per employee multipliers (rough estimates)
        industry_multipliers = {
            "Technology": 200000,
            "Finance": 300000,
            "Healthcare": 150000,
            "E-commerce": 100000,
            "Education": 80000,
            "Real Estate": 120000,
            "Food & Beverage": 90000,
            "Fitness": 70000,
            "Beauty": 110000
        }
        
        multiplier = industry_multipliers.get(prospect.industry, 150000)  # Default multiplier
        estimated_revenue = prospect.employee_count * multiplier
        
        return {
            "revenue": estimated_revenue,
            "confidence": 0.3  # Low confidence for estimation
        }
    
    async def batch_enrich_prospects(self, prospects: List[Prospect], 
                                   deep_enrichment: bool = True,
                                   batch_size: int = 10) -> Dict[str, EnrichmentResult]:
        """
        Enrich multiple prospects in batches.
        
        Args:
            prospects: List of prospects to enrich
            deep_enrichment: Whether to perform deep enrichment
            batch_size: Number of prospects to process in parallel
            
        Returns:
            Dictionary mapping domain to EnrichmentResult
        """
        results = {}
        
        for i in range(0, len(prospects), batch_size):
            batch = prospects[i:i+batch_size]
            tasks = [self.enrich_prospect(prospect, deep_enrichment) for prospect in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for prospect, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Error enriching {prospect.domain}: {result}")
                    results[prospect.domain] = EnrichmentResult(
                        success=False,
                        enriched_fields=[],
                        new_technologies=[],
                        new_contacts=[],
                        updated_fields={},
                        confidence_scores={},
                        errors=[str(result)]
                    )
                else:
                    results[prospect.domain] = result
        
        return results