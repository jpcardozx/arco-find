"""
Test module for the SimplifiedEngine.

This module contains tests for the SimplifiedEngine implementation.
"""

import asyncio
import pytest
from arco.engines.simplified_engine import SimplifiedEngine
from arco.models.prospect import Prospect

@pytest.mark.asyncio
async def test_simplified_engine_analyze():
    """Test the analyze method of SimplifiedEngine."""
    # Create a test prospect
    prospect = Prospect(
        domain="example.com",
        company_name="Example Company"
    )
    
    # Create the engine
    engine = SimplifiedEngine()
    
    # Analyze the prospect
    leak_result = await engine.analyze(prospect)
    
    # Check the result
    assert leak_result is not None
    assert leak_result.domain == "example.com"
    
    # Note: The actual leak detection might not find anything for example.com
    # This test just ensures the method runs without errors

@pytest.mark.asyncio
async def test_simplified_engine_qualify():
    """Test the qualify method of SimplifiedEngine."""
    # Create a test prospect
    prospect = Prospect(
        domain="example.com",
        company_name="Example Company"
    )
    
    # Create the engine
    engine = SimplifiedEngine()
    
    # Analyze the prospect
    leak_result = await engine.analyze(prospect)
    
    # Qualify the prospect
    qualified = await engine.qualify(prospect, leak_result)
    
    # Check the result
    assert qualified is not None
    assert qualified.domain == "example.com"
    assert qualified.company_name == "Example Company"
    assert qualified.monthly_waste == leak_result.total_monthly_waste
    assert qualified.annual_savings == leak_result.annual_savings

@pytest.mark.asyncio
async def test_simplified_engine_legacy_method():
    """Test the legacy discover_simplified_leaks method."""
    # Create the engine
    engine = SimplifiedEngine()
    
    # Test domains
    domains = ["example.com", "example.org"]
    
    # Run the legacy method
    results = await engine.discover_simplified_leaks(domains)
    
    # Check the results
    assert results is not None
    assert isinstance(results, list)
    
    # Note: The actual leak detection might not find anything for these domains
    # This test just ensures the method runs without errors

if __name__ == "__main__":
    # Run the tests
    asyncio.run(test_simplified_engine_analyze())
    asyncio.run(test_simplified_engine_qualify())
    asyncio.run(test_simplified_engine_legacy_method())
    print("All tests passed!")