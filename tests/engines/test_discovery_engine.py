"""
Test module for the DiscoveryEngine.

This module contains tests for the DiscoveryEngine implementation.
"""

import pytest
from arco.engines.discovery_engine import DiscoveryEngine
from arco.models.prospect import Prospect

def test_discovery_engine_init():
    """Test the initialization of DiscoveryEngine."""
    engine = DiscoveryEngine()
    assert engine is not None
    assert engine.icp_filters is not None
    assert engine.icp_filters['min_revenue'] == 500_000
    assert engine.icp_filters['max_revenue'] == 3_000_000

def test_discovery_engine_discover():
    """Test the discover method of DiscoveryEngine."""
    engine = DiscoveryEngine()
    
    # Test with different queries
    shopify_prospects = engine.discover("shopify stores", limit=2)
    assert len(shopify_prospects) <= 2
    assert all(isinstance(p, Prospect) for p in shopify_prospects)
    
    linkedin_prospects = engine.discover("linkedin sales", limit=2)
    assert len(linkedin_prospects) <= 2
    assert all(isinstance(p, Prospect) for p in linkedin_prospects)
    
    job_prospects = engine.discover("hiring growth", limit=2)
    assert len(job_prospects) <= 2
    assert all(isinstance(p, Prospect) for p in job_prospects)
    
    funding_prospects = engine.discover("series a funding", limit=2)
    assert len(funding_prospects) <= 2
    assert all(isinstance(p, Prospect) for p in funding_prospects)
    
    # Test with mixed query
    mixed_prospects = engine.discover("b2b saas companies", limit=4)
    assert len(mixed_prospects) <= 4
    assert all(isinstance(p, Prospect) for p in mixed_prospects)

def test_discovery_engine_enrich():
    """Test the enrich method of DiscoveryEngine."""
    engine = DiscoveryEngine()
    
    # Create a basic prospect
    prospect = Prospect(
        domain="example.com",
        company_name="Example Company"
    )
    
    # Enrich the prospect
    enriched = engine.enrich(prospect)
    
    # Check that the prospect was enriched
    assert enriched.domain == "example.com"
    assert enriched.company_name == "Example Company"
    assert enriched.industry is not None
    assert len(enriched.technologies) > 0
    assert len(enriched.contacts) > 0

def test_discovery_engine_discover_multiple():
    """Test the discover_multiple method of DiscoveryEngine."""
    engine = DiscoveryEngine()
    
    # Test with multiple domains
    domains = ["example.com", "example.org"]
    results = engine.discover_multiple(domains)
    
    # Check the results
    assert len(results) == 2
    assert results[0]["domain"] == "example.com"
    assert results[1]["domain"] == "example.org"
    assert "company_name" in results[0]
    assert "website" in results[0]

if __name__ == "__main__":
    # Run the tests
    test_discovery_engine_init()
    test_discovery_engine_discover()
    test_discovery_engine_enrich()
    test_discovery_engine_discover_multiple()
    print("All tests passed!")