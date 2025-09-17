"""
Marketing Benchmarks Loader for ARCO.

This module provides functionality to load and access marketing benchmarks
for different industries, used in leak detection and qualification.
"""

import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path

class MarketingBenchmarks:
    """Marketing benchmarks loader and accessor."""
    
    def __init__(self, config_path: str = "arco/config/marketing_benchmarks.yml"):
        """
        Initialize the benchmarks loader.
        
        Args:
            config_path: Path to the marketing benchmarks YAML file
        """
        self.config_path = config_path
        self._benchmarks = None
        self._load_benchmarks()
    
    def _load_benchmarks(self) -> None:
        """Load benchmarks from YAML file."""
        try:
            # Try multiple possible paths
            possible_paths = [
                self.config_path,
                os.path.join(os.path.dirname(__file__), "marketing_benchmarks.yml"),
                "config/marketing_benchmarks.yml",
                "arco/config/marketing_benchmarks.yml"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        self._benchmarks = yaml.safe_load(f)
                    return
            
            # If no file found, use minimal defaults
            self._benchmarks = self._get_default_benchmarks()
            
        except Exception as e:
            print(f"Warning: Could not load marketing benchmarks: {e}")
            self._benchmarks = self._get_default_benchmarks()
    
    def _get_default_benchmarks(self) -> Dict[str, Any]:
        """Get default benchmarks if file loading fails."""
        return {
            "industries": {
                "ecommerce": {
                    "avg_cpc": 1.16,
                    "avg_conversion_rate": 0.0268,
                    "avg_bounce_rate": 0.47,
                    "tech_costs": {
                        "shopify": {"basic": 29, "shopify": 79, "advanced": 299},
                        "klaviyo": {"growth": 150, "pro": 400}
                    }
                },
                "retail": {
                    "avg_cpc": 1.35,
                    "avg_conversion_rate": 0.0285,
                    "avg_bounce_rate": 0.45,
                    "tech_costs": {
                        "shopify": {"basic": 29, "shopify": 79, "advanced": 299}
                    }
                }
            },
            "leak_detection": {
                "min_monthly_waste": 50,
                "high_severity_threshold": 500,
                "medium_severity_threshold": 150
            }
        }
    
    def get_industry_benchmark(self, industry: str, metric: str) -> Optional[float]:
        """
        Get a specific benchmark for an industry.
        
        Args:
            industry: Industry name (e.g., 'ecommerce', 'saas')
            metric: Metric name (e.g., 'avg_cpc', 'avg_conversion_rate')
            
        Returns:
            Benchmark value or None if not found
        """
        if not self._benchmarks:
            return None
        
        industry_data = self._benchmarks.get("industries", {}).get(industry.lower())
        if not industry_data:
            return None
        
        return industry_data.get(metric)
    
    def get_tech_cost(self, industry: str, technology: str, tier: str = None) -> Optional[float]:
        """
        Get technology cost for a specific industry.
        
        Args:
            industry: Industry name
            technology: Technology name (e.g., 'shopify', 'klaviyo')
            tier: Technology tier (e.g., 'basic', 'pro')
            
        Returns:
            Monthly cost or None if not found
        """
        if not self._benchmarks:
            return None
        
        industry_data = self._benchmarks.get("industries", {}).get(industry.lower())
        if not industry_data:
            return None
        
        tech_costs = industry_data.get("tech_costs", {}).get(technology.lower())
        if not tech_costs:
            return None
        
        if tier:
            return tech_costs.get(tier.lower())
        else:
            # Return the first/default tier cost
            if isinstance(tech_costs, dict):
                return list(tech_costs.values())[0]
            return tech_costs
    
    def get_web_vitals_threshold(self, industry: str, metric: str, level: str = "good") -> Optional[float]:
        """
        Get web vitals threshold for an industry.
        
        Args:
            industry: Industry name
            metric: Web vital metric (e.g., 'lcp', 'fid', 'cls')
            level: Threshold level ('good' or 'poor')
            
        Returns:
            Threshold value or None if not found
        """
        if not self._benchmarks:
            return None
        
        industry_data = self._benchmarks.get("industries", {}).get(industry.lower())
        if not industry_data:
            return None
        
        thresholds = industry_data.get("web_vitals_thresholds", {})
        threshold_key = f"{metric.lower()}_{level.lower()}"
        
        return thresholds.get(threshold_key)
    
    def get_performance_impact(self, industry: str, impact_type: str) -> Optional[float]:
        """
        Get performance impact factor for an industry.
        
        Args:
            industry: Industry name
            impact_type: Type of impact (e.g., 'lcp_delay_conversion_loss')
            
        Returns:
            Impact factor or None if not found
        """
        if not self._benchmarks:
            return None
        
        industry_data = self._benchmarks.get("industries", {}).get(industry.lower())
        if not industry_data:
            return None
        
        return industry_data.get("performance_impact", {}).get(impact_type)
    
    def get_leak_threshold(self, threshold_type: str) -> Optional[float]:
        """
        Get leak detection threshold.
        
        Args:
            threshold_type: Type of threshold (e.g., 'min_monthly_waste')
            
        Returns:
            Threshold value or None if not found
        """
        if not self._benchmarks:
            return None
        
        return self._benchmarks.get("leak_detection", {}).get(threshold_type)
    
    def get_all_industries(self) -> list:
        """Get list of all available industries."""
        if not self._benchmarks:
            return []
        
        return list(self._benchmarks.get("industries", {}).keys())
    
    def normalize_industry_name(self, industry: str) -> str:
        """
        Normalize industry name to match benchmark keys.
        
        Args:
            industry: Raw industry name
            
        Returns:
            Normalized industry name
        """
        if not industry:
            return "retail"  # Default fallback
        
        industry_lower = industry.lower()
        
        # Map common variations to our benchmark keys
        mappings = {
            "e-commerce": "ecommerce",
            "ecom": "ecommerce",
            "online retail": "ecommerce",
            "software": "saas",
            "technology": "saas",
            "tech": "saas",
            "health": "health_supplements",
            "supplements": "health_supplements",
            "wellness": "health_supplements",
            "consumer services": "retail",
            "luxury goods & jewelry": "retail",
            "apparel & fashion": "retail",
            "wholesale": "retail"
        }
        
        return mappings.get(industry_lower, industry_lower)

# Global instance
_benchmarks_instance = None

def get_marketing_benchmarks() -> MarketingBenchmarks:
    """Get the global marketing benchmarks instance."""
    global _benchmarks_instance
    if _benchmarks_instance is None:
        _benchmarks_instance = MarketingBenchmarks()
    return _benchmarks_instance