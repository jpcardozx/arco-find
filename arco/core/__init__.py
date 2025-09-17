"""
ARCO Core Module.

This module contains the core infrastructure components including
dependency injection container, service configuration, and comprehensive
error handling system.
"""

from .container import ServiceContainer, get_container, configure_container
from .error_handler import (
    ProcessingErrorHandler,
    RetryConfig,
    CircuitBreakerConfig,
    ErrorSeverity,
    ErrorContext,
    CircuitBreaker,
    with_error_handling,
    get_error_handler,
    configure_error_handler,
    RateLimitError,
    APIError,
    CircuitBreakerOpenError
)
from .service_configuration import (
    configure_all_services,
    get_configured_container,
    get_business_intelligence_service,
    get_lead_scoring_service,
    get_prospect_orchestrator,
    get_processing_error_handler
)

__all__ = [
    # Container
    'ServiceContainer',
    'get_container',
    'configure_container',
    
    # Error Handling
    'ProcessingErrorHandler',
    'RetryConfig',
    'CircuitBreakerConfig',
    'ErrorSeverity',
    'ErrorContext',
    'CircuitBreaker',
    'with_error_handling',
    'get_error_handler',
    'configure_error_handler',
    'RateLimitError',
    'APIError',
    'CircuitBreakerOpenError',
    
    # Service Configuration
    'configure_all_services',
    'get_configured_container',
    'get_business_intelligence_service',
    'get_lead_scoring_service',
    'get_prospect_orchestrator',
    'get_processing_error_handler'
]