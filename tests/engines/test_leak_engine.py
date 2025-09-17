"""
Test module for the LeakEngine.

This module contains tests for the LeakEngine implementation.
"""

import pytest
import asyncio
from arco.engines.leak_engine import LeakEngine
from arco.models.prospect import Prospect
from arco.models.leak_result import LeakResult
from arco.models.qualified_prospect import QualifiedProspect

@pytest.mark.asyncio
async def test_leak_engine_analyze():
    """Test the analyze method of LeakEngine."""
    # Create a test prospect
    prospect = Prospect(
        domain="example.com",
        company_name="Example Company"
    )
    
    # Create the engine
    engine = LeakEngine()
    
    # Analyze the prospect
    leak_result = await engine.analyze(prospect)
    
    # Check the result
    assert leak_result is not None
    assert leak_result.domain == "example.com"
    assert isinstance(leak_result, LeakResult)
    
    # Clean up
    await engine.close()

@pytest.mark.asyncio
async def test_leak_engine_qualify():
    """Test the qualify method of LeakEngine."""
    # Create a test prospect
    prospect = Prospect(
        domain="example.com",
        company_name="Example Company"
    )
    
    # Create the engine
    engine = LeakEngine()
    
    # Analyze the prospect
    leak_result = await engine.analyze(prospect)
    
    # Qualify the prospect
    qualified = await engine.qualify(prospect, leak_result)
    
    # Check the result
    assert qualified is not None
    assert qualified.domain == "example.com"
    assert qualified.company_name == "Example Company"
    assert isinstance(qualified, QualifiedProspect)
    assert qualified.monthly_waste == leak_result.total_monthly_waste
    assert qualified.annual_savings == leak_result.annual_savings
    assert qualified.leak_count == leak_result.leak_count
    
    # Clean up
    await engine.close()

@pytest.mark.asyncio
async def test_leak_engine_with_real_domain():
    """Test the LeakEngine with a real domain."""
    # Create a test prospect with a real domain
    prospect = Prospect(
        domain="shopify.com",
        company_name="Shopify"
    )
    
    # Create the engine
    engine = LeakEngine()
    
    # Analyze the prospect
    leak_result = await engine.analyze(prospect)
    
    # Check the result
    assert leak_result is not None
    assert leak_result.domain == "shopify.com"
    
    # Qualify the prospect
    qualified = await engine.qualify(prospect, leak_result)
    
    # Check the qualification
    assert qualified is not None
    assert qualified.domain == "shopify.com"
    assert qualified.priority_tier in ["A", "B", "C"]
    
    # Clean up
    await engine.close()

if __name__ == "__main__":
    # Run the tests
    asyncio.run(test_leak_engine_analyze())
    asyncio.run(test_leak_engine_qualify())
    asyncio.run(test_leak_engine_with_real_domain())
    print("All tests passed!")