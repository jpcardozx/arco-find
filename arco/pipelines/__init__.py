"""
ARCO Pipelines Module.

This module contains the pipeline implementations for the ARCO system,
including standard and advanced pipelines for customer acquisition and analysis.
"""

from .base import PipelineInterface
from .standard_pipeline import StandardPipeline
from .advanced_pipeline import AdvancedPipeline

__all__ = [
    'PipelineInterface',
    'StandardPipeline',
    'AdvancedPipeline'
]