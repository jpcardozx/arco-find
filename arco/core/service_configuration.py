"""
Service Configuration for ARCO Dependency Injection Container.

This module configures all services including the new error handling system
for the professional service layer architecture.
"""

import logging
from arco.core.container import ServiceContainer
from arco.core.error_handler import (
    ProcessingErrorHandler, 
    RetryConfig, 
    CircuitBreakerConfig,
    get_error_handler
)

# Import services
from arco.services.business_intelligence_service import BusinessIntelligenceService
from arco.services.lead_scoring_service import LeadScoringService
from arco.services.prospect_orchestrator import ProspectOrchestrator
from arco.services.real_data_service import RealDataService

# Import integrations
from arco.integrations.ad_intelligence_collector import AdIntelligenceCollector
from arco.integrations.funding_intelligence_collector import FundingIntelligenceCollector
from arco.integrations.hiring_intelligence_collector import HiringIntelligenceCollector
from arco.integrations.technology_intelligence_collector import TechnologyIntelligenceCollector

logger = logging.getLogger(__name__)


def configure_error_handling(container: ServiceContainer) -> None:
    """
    Configure error handling services with appropriate retry and circuit breaker settings.
    
    Args:
        container: Service container to register error handling services
    """
    logger.info("Configuring error handling services...")
    
    # Configure retry settings for different service types
    api_retry_config = RetryConfig(
        max_retries=3,
        initial_delay=1.0,
        backoff_factor=2.0,
        max_delay=30.0,
        jitter=True
    )
    
    # Configure circuit breaker for external APIs
    api_circuit_breaker_config = CircuitBreakerConfig(
        failure_threshold=5,
        recovery_timeout=60.0,
        success_threshold=3
    )
    
    # Register main error handler
    container.register_singleton(
        ProcessingErrorHandler,
        lambda: ProcessingErrorHandler(
            retry_config=api_retry_config,
            circuit_breaker_config=api_circuit_breaker_config
        )
    )
    
    logger.info("✅ Error handling services configured")


def configure_intelligence_collectors(container: ServiceContainer) -> None:
    """
    Configure intelligence collector services with error handling.
    
    Args:
        container: Service container to register intelligence collectors
    """
    logger.info("Configuring intelligence collectors...")
    
    # Register intelligence collectors as singletons for efficiency
    container.register_singleton(AdIntelligenceCollector)
    container.register_singleton(FundingIntelligenceCollector)
    container.register_singleton(HiringIntelligenceCollector)
    container.register_singleton(TechnologyIntelligenceCollector)
    
    logger.info("✅ Intelligence collectors configured")


from arco.pipelines.standard_pipeline import StandardPipeline
from arco.pipelines.advanced_pipeline import AdvancedPipeline
from arco.pipelines.marketing_pipeline import MarketingPipeline

def configure_core_services(container: ServiceContainer) -> None:
    """
    Configure core business services with dependency injection.
    
    Args:
        container: Service container to register core services
    """
    logger.info("Configuring core services...")
    
    # Register core services
    container.register_singleton(BusinessIntelligenceService)
    container.register_singleton(LeadScoringService)
    container.register_singleton(RealDataService)
    container.register_singleton(ProspectOrchestrator)
    
    logger.info("✅ Core services configured")

def configure_pipelines(container: ServiceContainer) -> None:
    """
    Configure pipeline services with dependency injection.
    
    Args:
        container: Service container to register pipeline services
    """
    logger.info("Configuring pipeline services...")
    
    container.register_transient(StandardPipeline)
    container.register_transient(AdvancedPipeline)
    container.register_transient(MarketingPipeline)
    
    logger.info("✅ Pipeline services configured")


def configure_all_services(container: ServiceContainer) -> None:
    """
    Configure all services in the proper order with dependencies.
    
    Args:
        container: Service container to configure
    """
    logger.info("🚀 Starting service configuration...")
    
    # Configure in dependency order
    configure_error_handling(container)
    configure_intelligence_collectors(container)
    configure_core_services(container)
    configure_pipelines(container)
    
    # Validate all registrations
    try:
        container.validate_registrations()
        logger.info("✅ All service registrations validated successfully")
    except Exception as e:
        logger.error(f"❌ Service registration validation failed: {e}")
        raise
    
    logger.info("🎉 Service configuration completed successfully")


def get_configured_container() -> ServiceContainer:
    """
    Get a fully configured service container.
    
    Returns:
        Configured ServiceContainer instance
    """
    container = ServiceContainer()
    configure_all_services(container)
    return container


# Convenience functions for getting specific services
def get_business_intelligence_service(container: ServiceContainer) -> BusinessIntelligenceService:
    """Get configured business intelligence service."""
    return container.resolve(BusinessIntelligenceService)


def get_lead_scoring_service(container: ServiceContainer) -> LeadScoringService:
    """Get configured lead scoring service."""
    return container.resolve(LeadScoringService)


def get_prospect_orchestrator(container: ServiceContainer) -> ProspectOrchestrator:
    """Get configured prospect analysis orchestrator."""
    return container.resolve(ProspectOrchestrator)


def get_processing_error_handler(container: ServiceContainer) -> ProcessingErrorHandler:
    """Get configured processing error handler."""
    return container.resolve(ProcessingErrorHandler)