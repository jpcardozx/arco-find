"""
CRM Integration for ARCO.

This module contains the implementation of the CRM integration,
which allows registering leads in a CRM system.
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional, Union
import logging
from datetime import datetime
import time
from abc import ABC, abstractmethod

from arco.utils.logger import get_logger
from arco.models.prospect import Prospect
from arco.models.financial_leak import FinancialLeakDetector

logger = get_logger(__name__)

class CRMIntegrationInterface(ABC):
    """Interface for CRM integrations."""
    
    @abstractmethod
    def initialize(self, api_key: str, **kwargs) -> bool:
        """
        Initialize the CRM integration.
        
        Args:
            api_key: API key for authentication
            **kwargs: Additional configuration parameters
            
        Returns:
            True if initialization was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def register_lead(self, prospect: Prospect, additional_data: Dict[str, Any] = None) -> str:
        """
        Register a lead in the CRM.
        
        Args:
            prospect: Prospect to register
            additional_data: Additional data to include
            
        Returns:
            CRM lead ID
        """
        pass
    
    @abstractmethod
    def update_lead(self, crm_lead_id: str, data: Dict[str, Any]) -> bool:
        """
        Update a lead in the CRM.
        
        Args:
            crm_lead_id: CRM lead ID
            data: Data to update
            
        Returns:
            True if update was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_lead(self, crm_lead_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a lead from the CRM.
        
        Args:
            crm_lead_id: CRM lead ID
            
        Returns:
            Lead data or None if not found
        """
        pass
    
    @abstractmethod
    def search_leads(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for leads in the CRM.
        
        Args:
            query: Search query
            
        Returns:
            List of matching leads
        """
        pass


class HubSpotIntegration(CRMIntegrationInterface):
    """Integration with HubSpot CRM."""
    
    def __init__(self):
        """Initialize the HubSpot integration."""
        self.api_key = None
        self.base_url = "https://api.hubapi.com"
        self.initialized = False
        self.rate_limit_remaining = 100
        self.rate_limit_reset = 0
    
    def initialize(self, api_key: str, **kwargs) -> bool:
        """
        Initialize the HubSpot integration.
        
        Args:
            api_key: HubSpot API key
            **kwargs: Additional configuration parameters
            
        Returns:
            True if initialization was successful, False otherwise
        """
        self.api_key = api_key
        
        # Test the API key
        try:
            response = self._make_request("GET", "/crm/v3/objects/contacts")
            self.initialized = response.status_code == 200
            return self.initialized
        except Exception as e:
            logger.error(f"Error initializing HubSpot integration: {e}")
            return False
    
    def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> requests.Response:
        """
        Make a request to the HubSpot API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            
        Returns:
            Response object
        """
        if not self.initialized:
            raise ValueError("HubSpot integration not initialized")
        
        # Check rate limit
        if self.rate_limit_remaining <= 0:
            wait_time = max(0, self.rate_limit_reset - time.time())
            if wait_time > 0:
                logger.warning(f"Rate limit reached, waiting {wait_time:.1f} seconds")
                time.sleep(wait_time)
        
        # Make request
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=data
        )
        
        # Update rate limit info
        self.rate_limit_remaining = int(response.headers.get("X-HubSpot-RateLimit-Remaining", "100"))
        self.rate_limit_reset = int(response.headers.get("X-HubSpot-RateLimit-Reset", "0"))
        
        # Check for errors
        if response.status_code >= 400:
            logger.error(f"HubSpot API error: {response.status_code} - {response.text}")
        
        return response
    
    def register_lead(self, prospect: Prospect, additional_data: Dict[str, Any] = None) -> str:
        """
        Register a lead in HubSpot.
        
        Args:
            prospect: Prospect to register
            additional_data: Additional data to include
            
        Returns:
            HubSpot lead ID
        """
        # Check if lead already exists
        existing_leads = self.search_leads(f"domain:{prospect.domain}")
        if existing_leads:
            return existing_leads[0]["id"]
        
        # Prepare company data
        company_data = {
            "properties": {
                "domain": prospect.domain,
                "name": prospect.company_name or prospect.domain,
                "description": prospect.description or "",
                "industry": prospect.industry or "",
                "numberofemployees": str(prospect.employee_count) if prospect.employee_count else "",
                "annualrevenue": str(prospect.revenue) if prospect.revenue else "",
                "country": prospect.country or "",
                "city": prospect.city or "",
                "website": prospect.website or f"https://{prospect.domain}",
                "hubspot_owner_id": "1"  # Default owner
            }
        }
        
        # Add additional data
        if additional_data:
            for key, value in additional_data.items():
                if isinstance(value, (str, int, float, bool)) or value is None:
                    company_data["properties"][key] = str(value) if value is not None else ""
        
        # Create company
        response = self._make_request("POST", "/crm/v3/objects/companies", company_data)
        
        if response.status_code == 201:
            company_id = response.json()["id"]
            logger.info(f"Created company in HubSpot: {company_id}")
            
            # Create contacts if available
            for contact in prospect.contacts:
                contact_data = {
                    "properties": {
                        "firstname": contact.name.split()[0] if contact.name and " " in contact.name else contact.name or "",
                        "lastname": contact.name.split()[-1] if contact.name and " " in contact.name else "",
                        "email": contact.email or f"contact@{prospect.domain}",
                        "phone": contact.phone or "",
                        "jobtitle": contact.position or "",
                        "company": prospect.company_name or prospect.domain,
                        "website": prospect.website or f"https://{prospect.domain}",
                        "hubspot_owner_id": "1"  # Default owner
                    },
                    "associations": [
                        {
                            "to": {"id": company_id},
                            "types": [
                                {
                                    "associationCategory": "HUBSPOT_DEFINED",
                                    "associationTypeId": 1
                                }
                            ]
                        }
                    ]
                }
                
                contact_response = self._make_request("POST", "/crm/v3/objects/contacts", contact_data)
                
                if contact_response.status_code == 201:
                    logger.info(f"Created contact in HubSpot: {contact_response.json()['id']}")
                else:
                    logger.error(f"Error creating contact in HubSpot: {contact_response.status_code} - {contact_response.text}")
            
            # Create deal
            deal_data = {
                "properties": {
                    "dealname": f"ARCO Opportunity - {prospect.company_name or prospect.domain}",
                    "pipeline": "default",
                    "dealstage": "appointmentscheduled",
                    "amount": str(additional_data.get("estimated_annual_savings", "0")) if additional_data else "0",
                    "closedate": (datetime.now().replace(day=1) + timedelta(days=30)).strftime("%Y-%m-%d"),
                    "hubspot_owner_id": "1"  # Default owner
                },
                "associations": [
                    {
                        "to": {"id": company_id},
                        "types": [
                            {
                                "associationCategory": "HUBSPOT_DEFINED",
                                "associationTypeId": 3
                            }
                        ]
                    }
                ]
            }
            
            deal_response = self._make_request("POST", "/crm/v3/objects/deals", deal_data)
            
            if deal_response.status_code == 201:
                logger.info(f"Created deal in HubSpot: {deal_response.json()['id']}")
            else:
                logger.error(f"Error creating deal in HubSpot: {deal_response.status_code} - {deal_response.text}")
            
            return company_id
        else:
            logger.error(f"Error creating company in HubSpot: {response.status_code} - {response.text}")
            return ""
    
    def update_lead(self, crm_lead_id: str, data: Dict[str, Any]) -> bool:
        """
        Update a lead in HubSpot.
        
        Args:
            crm_lead_id: HubSpot company ID
            data: Data to update
            
        Returns:
            True if update was successful, False otherwise
        """
        # Prepare update data
        update_data = {
            "properties": {}
        }
        
        for key, value in data.items():
            if isinstance(value, (str, int, float, bool)) or value is None:
                update_data["properties"][key] = str(value) if value is not None else ""
        
        # Update company
        response = self._make_request("PATCH", f"/crm/v3/objects/companies/{crm_lead_id}", update_data)
        
        return response.status_code == 200
    
    def get_lead(self, crm_lead_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a lead from HubSpot.
        
        Args:
            crm_lead_id: HubSpot company ID
            
        Returns:
            Lead data or None if not found
        """
        response = self._make_request("GET", f"/crm/v3/objects/companies/{crm_lead_id}")
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error getting company from HubSpot: {response.status_code} - {response.text}")
            return None
    
    def search_leads(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for leads in HubSpot.
        
        Args:
            query: Search query
            
        Returns:
            List of matching leads
        """
        # Prepare search data
        search_data = {
            "filterGroups": [
                {
                    "filters": [
                        {
                            "propertyName": "domain",
                            "operator": "CONTAINS_TOKEN",
                            "value": query.replace("domain:", "")
                        }
                    ]
                }
            ],
            "sorts": [
                {
                    "propertyName": "createdate",
                    "direction": "DESCENDING"
                }
            ],
            "limit": 10
        }
        
        # Search companies
        response = self._make_request("POST", "/crm/v3/objects/companies/search", search_data)
        
        if response.status_code == 200:
            return response.json().get("results", [])
        else:
            logger.error(f"Error searching companies in HubSpot: {response.status_code} - {response.text}")
            return []


class MockCRMIntegration(CRMIntegrationInterface):
    """Mock CRM integration for testing."""
    
    def __init__(self, storage_dir: str = None):
        """
        Initialize the mock CRM integration.
        
        Args:
            storage_dir: Directory to store mock CRM data
        """
        self.storage_dir = storage_dir or os.path.join("data", "mock_crm")
        os.makedirs(self.storage_dir, exist_ok=True)
        self.leads = {}
        self.initialized = False
        self._load_leads()
    
    def _get_leads_file_path(self) -> str:
        """
        Get the path to the leads file.
        
        Returns:
            Path to the leads file
        """
        return os.path.join(self.storage_dir, "leads.json")
    
    def _load_leads(self) -> None:
        """Load leads from file."""
        file_path = self._get_leads_file_path()
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.leads = json.load(f)
                logger.info(f"Loaded {len(self.leads)} leads from mock CRM")
            except Exception as e:
                logger.error(f"Error loading leads from mock CRM: {e}")
    
    def _save_leads(self) -> None:
        """Save leads to file."""
        file_path = self._get_leads_file_path()
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.leads, f, indent=2)
            logger.info(f"Saved {len(self.leads)} leads to mock CRM")
        except Exception as e:
            logger.error(f"Error saving leads to mock CRM: {e}")
    
    def initialize(self, api_key: str = None, **kwargs) -> bool:
        """
        Initialize the mock CRM integration.
        
        Args:
            api_key: Not used
            **kwargs: Not used
            
        Returns:
            True
        """
        self.initialized = True
        return True
    
    def register_lead(self, prospect: Prospect, additional_data: Dict[str, Any] = None) -> str:
        """
        Register a lead in the mock CRM.
        
        Args:
            prospect: Prospect to register
            additional_data: Additional data to include
            
        Returns:
            Mock CRM lead ID
        """
        # Check if lead already exists
        for lead_id, lead in self.leads.items():
            if lead.get("domain") == prospect.domain:
                return lead_id
        
        # Generate lead ID
        from uuid import uuid4
        lead_id = str(uuid4())
        
        # Create lead
        lead = {
            "id": lead_id,
            "domain": prospect.domain,
            "company_name": prospect.company_name or prospect.domain,
            "description": prospect.description or "",
            "industry": prospect.industry or "",
            "employee_count": prospect.employee_count,
            "revenue": prospect.revenue,
            "country": prospect.country or "",
            "city": prospect.city or "",
            "website": prospect.website or f"https://{prospect.domain}",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "contacts": [contact.__dict__ for contact in prospect.contacts],
            "technologies": [tech.__dict__ for tech in prospect.technologies]
        }
        
        # Add additional data
        if additional_data:
            lead.update(additional_data)
        
        # Add to leads
        self.leads[lead_id] = lead
        
        # Save leads
        self._save_leads()
        
        return lead_id
    
    def update_lead(self, crm_lead_id: str, data: Dict[str, Any]) -> bool:
        """
        Update a lead in the mock CRM.
        
        Args:
            crm_lead_id: Mock CRM lead ID
            data: Data to update
            
        Returns:
            True if update was successful, False otherwise
        """
        if crm_lead_id not in self.leads:
            logger.warning(f"Lead not found in mock CRM: {crm_lead_id}")
            return False
        
        # Update lead
        self.leads[crm_lead_id].update(data)
        self.leads[crm_lead_id]["updated_at"] = datetime.now().isoformat()
        
        # Save leads
        self._save_leads()
        
        return True
    
    def get_lead(self, crm_lead_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a lead from the mock CRM.
        
        Args:
            crm_lead_id: Mock CRM lead ID
            
        Returns:
            Lead data or None if not found
        """
        return self.leads.get(crm_lead_id)
    
    def search_leads(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for leads in the mock CRM.
        
        Args:
            query: Search query
            
        Returns:
            List of matching leads
        """
        results = []
        
        # Parse query
        if "domain:" in query:
            domain = query.replace("domain:", "").strip()
            for lead_id, lead in self.leads.items():
                if domain.lower() in lead.get("domain", "").lower():
                    results.append(lead)
        else:
            # Simple text search
            query_lower = query.lower()
            for lead_id, lead in self.leads.items():
                if (query_lower in lead.get("domain", "").lower() or
                    query_lower in lead.get("company_name", "").lower() or
                    query_lower in lead.get("description", "").lower() or
                    query_lower in lead.get("industry", "").lower()):
                    results.append(lead)
        
        return results


class CRMManager:
    """Manager for CRM integrations."""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(CRMManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the CRM manager."""
        if self._initialized:
            return
        
        self.integrations = {}
        self.active_integration = None
        
        # Register built-in integrations
        self.register_integration("hubspot", HubSpotIntegration())
        self.register_integration("mock", MockCRMIntegration())
        
        # Set default active integration
        self.set_active_integration("mock")
        
        self._initialized = True
    
    def register_integration(self, name: str, integration: CRMIntegrationInterface) -> None:
        """
        Register a CRM integration.
        
        Args:
            name: Integration name
            integration: Integration instance
        """
        self.integrations[name] = integration
        logger.info(f"Registered CRM integration: {name}")
    
    def set_active_integration(self, name: str) -> bool:
        """
        Set the active CRM integration.
        
        Args:
            name: Integration name
            
        Returns:
            True if successful, False otherwise
        """
        if name not in self.integrations:
            logger.warning(f"CRM integration not found: {name}")
            return False
        
        self.active_integration = name
        logger.info(f"Set active CRM integration: {name}")
        return True
    
    def get_integration(self, name: str = None) -> Optional[CRMIntegrationInterface]:
        """
        Get a CRM integration.
        
        Args:
            name: Integration name, or None for active integration
            
        Returns:
            CRM integration or None if not found
        """
        if name is None:
            name = self.active_integration
        
        return self.integrations.get(name)
    
    def initialize_integration(self, name: str, api_key: str, **kwargs) -> bool:
        """
        Initialize a CRM integration.
        
        Args:
            name: Integration name
            api_key: API key
            **kwargs: Additional configuration parameters
            
        Returns:
            True if successful, False otherwise
        """
        integration = self.get_integration(name)
        if not integration:
            return False
        
        return integration.initialize(api_key, **kwargs)
    
    def register_lead(self, prospect: Prospect, additional_data: Dict[str, Any] = None, integration_name: str = None) -> str:
        """
        Register a lead in the CRM.
        
        Args:
            prospect: Prospect to register
            additional_data: Additional data to include
            integration_name: Integration name, or None for active integration
            
        Returns:
            CRM lead ID
        """
        integration = self.get_integration(integration_name)
        if not integration:
            logger.warning("No active CRM integration")
            return ""
        
        return integration.register_lead(prospect, additional_data)
    
    def update_lead(self, crm_lead_id: str, data: Dict[str, Any], integration_name: str = None) -> bool:
        """
        Update a lead in the CRM.
        
        Args:
            crm_lead_id: CRM lead ID
            data: Data to update
            integration_name: Integration name, or None for active integration
            
        Returns:
            True if successful, False otherwise
        """
        integration = self.get_integration(integration_name)
        if not integration:
            logger.warning("No active CRM integration")
            return False
        
        return integration.update_lead(crm_lead_id, data)
    
    def get_lead(self, crm_lead_id: str, integration_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Get a lead from the CRM.
        
        Args:
            crm_lead_id: CRM lead ID
            integration_name: Integration name, or None for active integration
            
        Returns:
            Lead data or None if not found
        """
        integration = self.get_integration(integration_name)
        if not integration:
            logger.warning("No active CRM integration")
            return None
        
        return integration.get_lead(crm_lead_id)
    
    def search_leads(self, query: str, integration_name: str = None) -> List[Dict[str, Any]]:
        """
        Search for leads in the CRM.
        
        Args:
            query: Search query
            integration_name: Integration name, or None for active integration
            
        Returns:
            List of matching leads
        """
        integration = self.get_integration(integration_name)
        if not integration:
            logger.warning("No active CRM integration")
            return []
        
        return integration.search_leads(query)
    
    def register_prospect_with_leak_data(self, prospect: Prospect, leak_results: Dict[str, Any] = None) -> str:
        """
        Register a prospect in the CRM with financial leak data.
        
        Args:
            prospect: Prospect to register
            leak_results: Financial leak detection results
            
        Returns:
            CRM lead ID
        """
        # Detect financial leaks if not provided
        if leak_results is None:
            leak_detector = FinancialLeakDetector()
            leak_results = leak_detector.detect_financial_leaks(prospect)
        
        # Extract key data for CRM
        additional_data = {
            "arco_analysis_date": datetime.now().isoformat(),
            "arco_technologies": ", ".join([tech.name for tech in prospect.technologies]),
            "arco_monthly_waste": leak_results["summary"]["total_monthly_waste"],
            "arco_annual_waste": leak_results["summary"]["total_annual_waste"],
            "arco_monthly_savings": leak_results["summary"]["total_monthly_savings"],
            "arco_annual_savings": leak_results["summary"]["total_annual_savings"],
            "arco_three_year_savings": leak_results["summary"]["total_three_year_savings"],
            "arco_roi_percentage": leak_results["summary"]["roi_percentage"],
            "arco_recommendations": "\n".join(leak_results["summary"]["priority_recommendations"][:3])
        }
        
        # Register lead
        return self.register_lead(prospect, additional_data)


# Global instance
crm_manager = CRMManager()