"""
Performance Analyzer for critical performance issues detection.

This module provides detailed performance analysis including:
- First Contentful Paint measurement
- Resource optimization analysis
- Image optimization detection
- CDN and caching analysis
"""

import asyncio
import re
import logging
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import aiohttp
from urllib.parse import urljoin, urlparse
import json

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Represents a performance metric measurement."""
    name: str
    value: float
    unit: str
    threshold: float
    status: str  # GOOD, NEEDS_IMPROVEMENT, POOR
    impact: str
    recommendation: str


@dataclass
class ResourceAnalysis:
    """Analysis of website resources."""
    total_resources: int = 0
    minified_resources: int = 0
    compressed_resources: int = 0
    cdn_resources: int = 0
    large_resources: List[str] = fiel