"""
Test module for the LeakResult model.

This module contains tests for the LeakResult model implementation.
"""

import pytest
from arco.models.leak_result import LeakResult
from arco.models.qualified_prospect import Leak

def test_leak_result_creation():
    """Test creating a LeakResult instance."""
    leak_result = LeakResult(
        domain="example.com",
        total_monthly_waste=1000.0,
        authority_score=0.8,
        has_ads=True,
        processing_time=1.5
    )
    
    assert leak_result.domain == "example.com"
    assert leak_result.total_monthly_waste == 1000.0
    assert leak_result.authority_score == 0.8
    assert leak_result.has_ads == True
    assert leak_result.processing_time == 1.5
    assert isinstance(leak_result.leaks, list)
    assert len(leak_result.leaks) == 0

def test_leak_result_with_leaks():
    """Test creating a LeakResult with leaks."""
    leak_result = LeakResult(
        domain="example.com",
        total_monthly_waste=1000.0
    )
    
    # Add leaks
    leak_result.leaks.append(Leak(
        type="performance",
        monthly_waste=500.0,
        annual_savings=6000.0,
        description="Slow page load times",
        severity="high"
    ))
    
    leak_result.leaks.append(Leak(
        type="ads",
        monthly_waste=300.0,
        annual_savings=3600.0,
        description="Inefficient ad spend",
        severity="medium"
    ))
    
    leak_result.leaks.append(Leak(
        type="conversion",
        monthly_waste=200.0,
        annual_savings=2400.0,
        description="Poor conversion funnel",
        severity="low"
    ))
    
    assert len(leak_result.leaks) == 3
    assert leak_result.leaks[0].type == "performance"
    assert leak_result.leaks[0].monthly_waste == 500.0
    assert leak_result.leaks[1].type == "ads"
    assert leak_result.leaks[1].monthly_waste == 300.0
    assert leak_result.leaks[2].type == "conversion"
    assert leak_result.leaks[2].monthly_waste == 200.0

def test_leak_result_properties():
    """Test LeakResult properties."""
    leak_result = LeakResult(
        domain="example.com",
        total_monthly_waste=1000.0
    )
    
    # Add leaks
    leak_result.leaks.append(Leak(
        type="performance",
        monthly_waste=500.0,
        annual_savings=6000.0,
        description="Slow page load times",
        severity="high"
    ))
    
    leak_result.leaks.append(Leak(
        type="ads",
        monthly_waste=300.0,
        annual_savings=3600.0,
        description="Inefficient ad spend",
        severity="medium"
    ))
    
    # Test properties
    assert leak_result.annual_savings == 12000.0  # 1000.0 * 12
    assert leak_result.leak_count == 2
    assert len(leak_result.top_leaks) == 2
    assert leak_result.top_leaks[0].type == "performance"  # Highest monthly waste
    assert leak_result.top_leaks[1].type == "ads"

def test_leak_result_to_dict():
    """Test converting a LeakResult to a dictionary."""
    leak_result = LeakResult(
        domain="example.com",
        total_monthly_waste=1000.0,
        authority_score=0.8,
        has_ads=True,
        processing_time=1.5
    )
    
    # Add a leak
    leak_result.leaks.append(Leak(
        type="performance",
        monthly_waste=500.0,
        annual_savings=6000.0,
        description="Slow page load times",
        severity="high"
    ))
    
    # Convert to dictionary
    leak_result_dict = leak_result.to_dict()
    
    # Check the dictionary
    assert leak_result_dict["domain"] == "example.com"
    assert leak_result_dict["total_monthly_waste"] == 1000.0
    assert leak_result_dict["authority_score"] == 0.8
    assert leak_result_dict["has_ads"] == True
    assert leak_result_dict["processing_time"] == 1.5
    assert len(leak_result_dict["leaks"]) == 1
    assert leak_result_dict["leaks"][0]["type"] == "performance"
    assert leak_result_dict["leaks"][0]["monthly_waste"] == 500.0
    assert leak_result_dict["leaks"][0]["annual_savings"] == 6000.0
    assert leak_result_dict["leaks"][0]["description"] == "Slow page load times"
    assert leak_result_dict["leaks"][0]["severity"] == "high"

def test_leak_result_from_dict():
    """Test creating a LeakResult from a dictionary."""
    leak_result_dict = {
        "domain": "example.com",
        "total_monthly_waste": 1000.0,
        "authority_score": 0.8,
        "has_ads": True,
        "processing_time": 1.5,
        "leaks": [
            {
                "type": "performance",
                "monthly_waste": 500.0,
                "annual_savings": 6000.0,
                "description": "Slow page load times",
                "severity": "high"
            }
        ]
    }
    
    # Create from dictionary
    leak_result = LeakResult.from_dict(leak_result_dict)
    
    # Check the leak result
    assert leak_result.domain == "example.com"
    assert leak_result.total_monthly_waste == 1000.0
    assert leak_result.authority_score == 0.8
    assert leak_result.has_ads == True
    assert leak_result.processing_time == 1.5
    assert len(leak_result.leaks) == 1
    assert leak_result.leaks[0].type == "performance"
    assert leak_result.leaks[0].monthly_waste == 500.0
    assert leak_result.leaks[0].annual_savings == 6000.0
    assert leak_result.leaks[0].description == "Slow page load times"
    assert leak_result.leaks[0].severity == "high"

if __name__ == "__main__":
    # Run the tests
    test_leak_result_creation()
    test_leak_result_with_leaks()
    test_leak_result_properties()
    test_leak_result_to_dict()
    test_leak_result_from_dict()
    print("All tests passed!")