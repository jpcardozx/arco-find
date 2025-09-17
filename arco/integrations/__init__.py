"""
Integration layer for ARCO prospect analysis system.

This module contains all external API integrations and data collectors
that gather real business intelligence from various sources.
"""

from arco.integrations.ad_intelligence_collector import AdIntelligenceCollector
from arco.integrations.funding_intelligence_collector import FundingIntelligenceCollector
from arco.integrations.hiring_intelligence_collector import HiringIntelligenceCollector
from arco.integrations.technology_intelligence_collector import TechnologyIntelligenceCollector

__all__ = [
    'AdIntelligenceCollector',
    'FundingIntelligenceCollector',
    'HiringIntelligenceCollector',
    'TechnologyIntelligenceCollector'
]