"""
Apollo CSV Integration for ARCO.

This module contains the implementation of the Apollo CSV integration,
which allows importing prospect data from Apollo CSV exports.
"""

import csv
import os
import re
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
import logging
from pathlib import Path

from arco.integrations.base import DataSourceInterface
from arco.models.prospect import Prospect, Technology, Contact
from arco.utils.logger import get_logger

logger = get_logger(__name__)

class ApolloCSVParser:
    """Parser for Apollo CSV exports."""
    
    def __init__(self, csv_path: str):
        """
        Initialize the Apollo CSV parser.
        
        Args:
            csv_path: Path to the Apollo CSV file
        """
        self.csv_path = csv_path
        self.data = []
        self._parse_csv()
    
    def _parse_csv(self) -> None:
        """Parse the CSV file."""
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.data = list(reader)
            logger.info(f"Successfully parsed {len(self.data)} records from {self.csv_path}")
        except Exception as e:
            logger.error(f"Error parsing CSV file {self.csv_path}: {e}")
            self.data = []
    
    def get_all_records(self) -> List[Dict[str, Any]]:
        """
        Get all records from the CSV file.
        
        Returns:
            List of all records
        """
        return self.data
    
    def get_record_by_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Get a record by domain.
        
        Args:
            domain: Domain to search for
            
        Returns:
            Record with the specified domain or None if not found
        """
        for record in self.data:
            if record.get('Website', '').lower() == domain.lower() or \
               record.get('Website', '').lower() == f"http://{domain.lower()}" or \
               record.get('Website', '').lower() == f"https://{domain.lower()}":
                return record
        return None
    
    def search_records(self, query: str) -> List[Dict[str, Any]]:
        """
        Search records by query.
        
        Args:
            query: Search query
            
        Returns:
            List of matching records
        """
        results = []
        query_lower = query.lower()
        
        for record in self.data:
            # Search in company name
            if query_lower in record.get('Company', '').lower():
                results.append(record)
                continue
            
            # Search in domain
            if query_lower in record.get('Website', '').lower():
                results.append(record)
                continue
            
            # Search in description
            if query_lower in record.get('Short Description', '').lower():
                results.append(record)
                continue
            
            # Search in industry
            if query_lower in record.get('Industry', '').lower():
                results.append(record)
                continue
            
            # Search in keywords
            if query_lower in record.get('Keywords', '').lower():
                results.append(record)
                continue
        
        return results
    
    def convert_to_prospect(self, record: Dict[str, Any]) -> Prospect:
        """
        Convert an Apollo record to a Prospect.
        
        Args:
            record: Apollo record
            
        Returns:
            Prospect object
        """
        # Extract domain from website
        website = record.get('Website', '')
        domain = self._extract_domain(website)
        
        # Extract employee count
        employee_count = self._parse_employee_count(record.get('# Employees', ''))
        
        # Extract revenue
        revenue = self._parse_revenue(record.get('Annual Revenue', ''))
        
        # Create prospect
        prospect = Prospect(
            domain=domain,
            company_name=record.get('Company', ''),
            website=website,
            description=record.get('Short Description', ''),
            industry=record.get('Industry', ''),
            employee_count=employee_count,
            revenue=revenue,
            country=record.get('Company Country', ''),
            city=record.get('Company City', '')
        )
        
        # Add technologies
        technologies = self._parse_technologies(record.get('Technologies', ''))
        for tech_name, tech_category in technologies:
            prospect.technologies.append(Technology(name=tech_name, category=tech_category))
        
        # Add contact (if available)
        if record.get('Account Owner', ''):
            prospect.contacts.append(Contact(
                name=record.get('Account Owner', ''),
                email=record.get('Account Owner', ''),  # Using account owner as email as a fallback
                linkedin=record.get('Company Linkedin Url', '')
            ))
        
        return prospect
    
    def _extract_domain(self, website: str) -> str:
        """
        Extract domain from website URL.
        
        Args:
            website: Website URL
            
        Returns:
            Domain name
        """
        if not website:
            return ""
        
        # Remove protocol
        domain = website.lower()
        domain = domain.replace('https://', '').replace('http://', '')
        
        # Remove www
        domain = domain.replace('www.', '')
        
        # Remove path
        domain = domain.split('/')[0]
        
        return domain
    
    def _parse_employee_count(self, employee_str: str) -> Optional[int]:
        """
        Parse employee count from string.
        
        Args:
            employee_str: Employee count string
            
        Returns:
            Employee count as integer or None if parsing fails
        """
        if not employee_str:
            return None
        
        try:
            return int(employee_str)
        except ValueError:
            # Try to extract number from string like "1-10" or "10+"
            match = re.search(r'(\d+)', employee_str)
            if match:
                return int(match.group(1))
            return None
    
    def _parse_revenue(self, revenue_str: str) -> Optional[float]:
        """
        Parse revenue from string.
        
        Args:
            revenue_str: Revenue string
            
        Returns:
            Revenue as float or None if parsing fails
        """
        if not revenue_str:
            return None
        
        try:
            # Remove currency symbols and commas
            clean_str = revenue_str.replace('$', '').replace(',', '')
            
            # Handle "M" for million and "K" for thousand
            if 'M' in clean_str:
                clean_str = clean_str.replace('M', '')
                return float(clean_str) * 1_000_000
            elif 'K' in clean_str:
                clean_str = clean_str.replace('K', '')
                return float(clean_str) * 1_000
            
            return float(clean_str)
        except ValueError:
            return None
    
    def _parse_technologies(self, tech_str: str) -> List[Tuple[str, str]]:
        """
        Parse technologies from string.
        
        Args:
            tech_str: Technologies string
            
        Returns:
            List of (technology name, category) tuples
        """
        if not tech_str:
            return []
        
        # Split by commas
        tech_list = [t.strip() for t in tech_str.split(',')]
        
        # Map technologies to categories
        tech_categories = []
        for tech in tech_list:
            if not tech:
                continue
            
            # Determine category based on technology name
            category = self._determine_tech_category(tech)
            tech_categories.append((tech, category))
        
        return tech_categories
    
    def _determine_tech_category(self, tech_name: str) -> str:
        """
        Determine technology category based on name.
        
        Args:
            tech_name: Technology name
            
        Returns:
            Technology category
        """
        tech_name_lower = tech_name.lower()
        
        # Email/Marketing
        if any(x in tech_name_lower for x in ['mailchimp', 'klaviyo', 'sendgrid', 'hubspot', 'marketo', 'mailgun']):
            return 'email_marketing'
        
        # Analytics
        if any(x in tech_name_lower for x in ['google analytics', 'mixpanel', 'amplitude', 'hotjar', 'segment']):
            return 'analytics'
        
        # E-commerce
        if any(x in tech_name_lower for x in ['shopify', 'magento', 'woocommerce', 'bigcommerce']):
            return 'ecommerce_platform'
        
        # CMS
        if any(x in tech_name_lower for x in ['wordpress', 'drupal', 'joomla', 'contentful']):
            return 'cms'
        
        # Hosting/Infrastructure
        if any(x in tech_name_lower for x in ['aws', 'cloudflare', 'heroku', 'netlify', 'vercel']):
            return 'hosting'
        
        # Payment
        if any(x in tech_name_lower for x in ['stripe', 'paypal', 'square', 'braintree', 'afterpay']):
            return 'payment'
        
        # Support
        if any(x in tech_name_lower for x in ['zendesk', 'intercom', 'gorgias', 'helpscout', 'freshdesk']):
            return 'support'
        
        # Reviews
        if any(x in tech_name_lower for x in ['yotpo', 'judge.me', 'reviews.io', 'okendo']):
            return 'reviews'
        
        # Subscriptions
        if any(x in tech_name_lower for x in ['recharge', 'bold', 'subscriptions']):
            return 'subscriptions'
        
        # Default
        return 'other'


class ApolloCSVIntegration(DataSourceInterface):
    """Integration for Apollo CSV exports."""
    
    def __init__(self, csv_dir: str = None):
        """
        Initialize the Apollo CSV integration.
        
        Args:
            csv_dir: Directory containing Apollo CSV files
        """
        self.csv_dir = csv_dir or os.path.join('arco')
        self.parsers = {}
        self._load_csv_files()
    
    def _load_csv_files(self) -> None:
        """Load all CSV files in the directory."""
        try:
            csv_files = [f for f in os.listdir(self.csv_dir) if f.endswith('.csv') and 'apollo' in f.lower()]
            
            for csv_file in csv_files:
                csv_path = os.path.join(self.csv_dir, csv_file)
                parser = ApolloCSVParser(csv_path)
                self.parsers[csv_file] = parser
            
            logger.info(f"Loaded {len(self.parsers)} Apollo CSV files")
        except Exception as e:
            logger.error(f"Error loading CSV files: {e}")
    
    def get_company_info(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Get company information by domain.
        
        Args:
            domain: Company domain name
            
        Returns:
            Company information or None if not found
        """
        for parser in self.parsers.values():
            record = parser.get_record_by_domain(domain)
            if record:
                return {
                    "name": record.get('Company', ''),
                    "website": record.get('Website', ''),
                    "description": record.get('Short Description', ''),
                    "industry": record.get('Industry', ''),
                    "employee_count": parser._parse_employee_count(record.get('# Employees', '')),
                    "revenue": parser._parse_revenue(record.get('Annual Revenue', '')),
                    "country": record.get('Company Country', ''),
                    "city": record.get('Company City', ''),
                    "keywords": record.get('Keywords', ''),
                    "founded_year": record.get('Founded Year', ''),
                    "technologies": record.get('Technologies', '')
                }
        return None
    
    def get_contacts(self, domain: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get company contacts by domain.
        
        Args:
            domain: Company domain name
            limit: Maximum number of contacts to return
            
        Returns:
            List of contacts
        """
        contacts = []
        
        for parser in self.parsers.values():
            record = parser.get_record_by_domain(domain)
            if record and record.get('Account Owner', ''):
                contacts.append({
                    "name": record.get('Account Owner', ''),
                    "email": record.get('Account Owner', ''),  # Using account owner as email as a fallback
                    "linkedin": record.get('Company Linkedin Url', '')
                })
        
        return contacts[:limit]
    
    def get_technologies(self, domain: str) -> List[Dict[str, Any]]:
        """
        Get technologies used by a company.
        
        Args:
            domain: Company domain name
            
        Returns:
            List of technologies
        """
        technologies = []
        
        for parser in self.parsers.values():
            record = parser.get_record_by_domain(domain)
            if record and record.get('Technologies', ''):
                tech_tuples = parser._parse_technologies(record.get('Technologies', ''))
                for tech_name, tech_category in tech_tuples:
                    technologies.append({
                        "name": tech_name,
                        "category": tech_category
                    })
        
        return technologies
    
    def search_companies(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search companies by query.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching companies
        """
        results = []
        
        for parser in self.parsers.values():
            records = parser.search_records(query)
            for record in records:
                results.append({
                    "name": record.get('Company', ''),
                    "domain": parser._extract_domain(record.get('Website', '')),
                    "website": record.get('Website', ''),
                    "description": record.get('Short Description', ''),
                    "industry": record.get('Industry', '')
                })
                
                if len(results) >= limit:
                    break
            
            if len(results) >= limit:
                break
        
        return results[:limit]
    
    def get_all_prospects(self) -> List[Prospect]:
        """
        Get all prospects from all CSV files.
        
        Returns:
            List of all prospects
        """
        prospects = []
        
        for parser in self.parsers.values():
            records = parser.get_all_records()
            for record in records:
                prospect = parser.convert_to_prospect(record)
                prospects.append(prospect)
        
        return prospects
    
    def get_prospect_by_domain(self, domain: str) -> Optional[Prospect]:
        """
        Get a prospect by domain.
        
        Args:
            domain: Domain to search for
            
        Returns:
            Prospect with the specified domain or None if not found
        """
        for parser in self.parsers.values():
            record = parser.get_record_by_domain(domain)
            if record:
                return parser.convert_to_prospect(record)
        return None