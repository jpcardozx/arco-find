"""
Base Integration Interfaces for ARCO.

This module contains the abstract base classes that define the interfaces
for all external service integrations in the ARCO system.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, TypeVar, Union

from arco.utils.retry import RetryConfig

T = TypeVar('T')

class APIClientInterface(ABC):
    """Interface for API clients that connect to external services."""
    
    @abstractmethod
    def initialize(self, api_key: str, **kwargs) -> bool:
        """
        Initialize the API client with credentials.
        
        Args:
            api_key: API key for authentication
            **kwargs: Additional configuration parameters
            
        Returns:
            True if initialization was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search for data using the API.
        
        Args:
            query: Search query
            **kwargs: Additional search parameters
            
        Returns:
            List of search results
        """
        pass
    
    @abstractmethod
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get the current rate limit status.
        
        Returns:
            Dictionary with rate limit information
        """
        pass


class DataSourceInterface(ABC):
    """Interface for data sources that provide prospect information."""
    
    @abstractmethod
    def get_company_info(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Get company information by domain.
        
        Args:
            domain: Company domain name
            
        Returns:
            Company information or None if not found
        """
        pass
    
    @abstractmethod
    def get_contacts(self, domain: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get company contacts by domain.
        
        Args:
            domain: Company domain name
            limit: Maximum number of contacts to return
            
        Returns:
            List of contacts
        """
        pass
    
    @abstractmethod
    def get_technologies(self, domain: str) -> List[Dict[str, Any]]:
        """
        Get technologies used by a company.
        
        Args:
            domain: Company domain name
            
        Returns:
            List of technologies
        """
        pass