"""
Services module for ARCO prospect analysis system.

This module contains all business logic services and provides service
registration for dependency injection.
"""

import logging
from arco.core.container import ServiceContainer
from arco.services.business_intelligence_service import BusinessIntelligenceService
from arco.services.lead_scoring_service import LeadScoringService
from arco.services.prospect_orchestrator import ProspectOrchestrator
from arco.integrations.ad_intelligence_collector import AdIntelligenceCollector
from arco.integrations.funding_intelligence_collector import FundingIntelligenceCollector
from arco.integrations.hiring_intelligence_collector import HiringIntelligenceCollector
from arco.integrations.technology_intelligence_collector import TechnologyIntelligenceCollector


def register_services(container: ServiceContainer) -> None:
    """
    Register all services in the dependency injection container.
    
    This function sets up the complete service layer architecture with
    proper dependency injection patterns.
    
    Args:
        container: The service container to register services in
    """
    logger = logging.getLogger(__name__)
    logger.info("🔧 Registering services in dependency injection container")
    
    # Register integration layer collectors as singletons
    container.register_singleton(AdIntelligenceCollector)
    container.register_singleton(FundingIntelligenceCollector)
    container.register_singleton(HiringIntelligenceCollector)
    container.register_singleton(TechnologyIntelligenceCollector)
    
    # Register service layer services
    container.register_singleton(BusinessIntelligenceService)
    container.register_singleton(LeadScoringService)
    
    # Register orchestrator as transient (new instance per request)
    container.register_transient(ProspectOrchestrator)
    
    logger.info("✅ Successfully registered all services")


def get_prospect_orchestrator(container: ServiceContainer) -> ProspectOrchestrator:
    """
    Get a configured ProspectOrchestrator instance.
    
    Args:
        container: The service container
        
    Returns:
        Fully configured ProspectOrchestrator
    """
    return container.resolve(ProspectOrchestrator)


__all__ = [
    'BusinessIntelligenceService',
    'LeadScoringService', 
    'ProspectOrchestrator',
    'register_services',
    'get_prospect_orchestrator'
]