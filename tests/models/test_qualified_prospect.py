"""
Test module for the QualifiedProspect model.

This module contains tests for the QualifiedProspect model implementation.
"""

import pytest
from datetime import datetime
from arco.models.prospect import Prospect, Technology, Contact
from arco.models.qualified_prospect import QualifiedProspect, Leak

def test_qualified_prospect_creation():
    """Test creating a QualifiedProspect instance."""
    qualified = QualifiedProspect(
        domain="example.com",
        company_name="Example Company",
        website="https://example.com",
        industry="Technology",
        employee_count=50,
        revenue=1000000.0,
        estimated_revenue=1200000.0,
        monthly_waste=5000.0,
        annual_savings=60000.0,
        leak_count=3,
        qualification_score=85,
        priority_tier="A",
        outreach_ready=True
    )
    
    # Check base Prospect attributes
    assert qualified.domain == "example.com"
    assert qualified.company_name == "Example Company"
    assert qualified.website == "https://example.com"
    assert qualified.industry == "Technology"
    assert qualified.employee_count == 50
    assert qualified.revenue == 1000000.0
    
    # Check QualifiedProspect specific attributes
    assert qualified.estimated_revenue == 1200000.0
    assert qualified.monthly_waste == 5000.0
    assert qualified.annual_savings == 60000.0
    assert qualified.leak_count == 3
    assert qualified.qualification_score == 85
    assert qualified.priority_tier == "A"
    assert qualified.outreach_ready == True
    assert isinstance(qualified.qualification_date, datetime)
    assert isinstance(qualified.top_leaks, list)

def test_qualified_prospect_with_leaks():
    """Test creating a QualifiedProspect with leaks."""
    qualified = QualifiedProspect(
        domain="example.com",
        company_name="Example Company"
    )
    
    # Add leaks
    qualified.top_leaks.append(Leak(
        type="performance",
        monthly_waste=500.0,
        annual_savings=6000.0,
        description="Slow page load times",
        severity="high"
    ))
    
    qualified.top_leaks.append(Leak(
        type="ads",
        monthly_waste=300.0,
        annual_savings=3600.0,
        description="Inefficient ad spend",
        severity="medium"
    ))
    
    assert len(qualified.top_leaks) == 2
    assert qualified.top_leaks[0].type == "performance"
    assert qualified.top_leaks[0].monthly_waste == 500.0
    assert qualified.top_leaks[0].annual_savings == 6000.0
    assert qualified.top_leaks[1].type == "ads"
    assert qualified.top_leaks[1].monthly_waste == 300.0
    assert qualified.top_leaks[1].annual_savings == 3600.0

def test_leak_to_dict():
    """Test converting a Leak to a dictionary."""
    leak = Leak(
        type="performance",
        monthly_waste=500.0,
        annual_savings=6000.0,
        description="Slow page load times",
        severity="high"
    )
    
    leak_dict = leak.to_dict()
    
    assert leak_dict["type"] == "performance"
    assert leak_dict["monthly_waste"] == 500.0
    assert leak_dict["annual_savings"] == 6000.0
    assert leak_dict["description"] == "Slow page load times"
    assert leak_dict["severity"] == "high"

def test_leak_from_dict():
    """Test creating a Leak from a dictionary."""
    leak_dict = {
        "type": "performance",
        "monthly_waste": 500.0,
        "annual_savings": 6000.0,
        "description": "Slow page load times",
        "severity": "high"
    }
    
    leak = Leak.from_dict(leak_dict)
    
    assert leak.type == "performance"
    assert leak.monthly_waste == 500.0
    assert leak.annual_savings == 6000.0
    assert leak.description == "Slow page load times"
    assert leak.severity == "high"

def test_qualified_prospect_to_dict():
    """Test converting a QualifiedProspect to a dictionary."""
    qualified = QualifiedProspect(
        domain="example.com",
        company_name="Example Company",
        monthly_waste=5000.0,
        annual_savings=60000.0,
        leak_count=2,
        qualification_score=85,
        priority_tier="A"
    )
    
    # Add a technology
    qualified.technologies.append(Technology(name="Python", category="Programming Language"))
    
    # Add a contact
    qualified.contacts.append(Contact(name="John Doe", email="john@example.com"))
    
    # Add a leak
    qualified.top_leaks.append(Leak(
        type="performance",
        monthly_waste=500.0,
        annual_savings=6000.0,
        description="Slow page load times",
        severity="high"
    ))
    
    # Convert to dictionary
    qualified_dict = qualified.to_dict()
    
    # Check base Prospect attributes
    assert qualified_dict["domain"] == "example.com"
    assert qualified_dict["company_name"] == "Example Company"
    assert len(qualified_dict["technologies"]) == 1
    assert qualified_dict["technologies"][0]["name"] == "Python"
    assert len(qualified_dict["contacts"]) == 1
    assert qualified_dict["contacts"][0]["name"] == "John Doe"
    
    # Check QualifiedProspect specific attributes
    assert qualified_dict["monthly_waste"] == 5000.0
    assert qualified_dict["annual_savings"] == 60000.0
    assert qualified_dict["leak_count"] == 2
    assert qualified_dict["qualification_score"] == 85
    assert qualified_dict["priority_tier"] == "A"
    assert len(qualified_dict["top_leaks"]) == 1
    assert qualified_dict["top_leaks"][0]["type"] == "performance"
    assert "qualification_date" in qualified_dict

def test_qualified_prospect_from_dict():
    """Test creating a QualifiedProspect from a dictionary."""
    qualified_dict = {
        "domain": "example.com",
        "company_name": "Example Company",
        "website": "https://example.com",
        "industry": "Technology",
        "employee_count": 50,
        "revenue": 1000000.0,
        "technologies": [
            {"name": "Python", "category": "Programming Language"}
        ],
        "contacts": [
            {"name": "John Doe", "email": "john@example.com"}
        ],
        "discovery_date": "2023-01-01T12:00:00",
        "validation_score": 0.8,
        "leak_potential": 0.6,
        "estimated_revenue": 1200000.0,
        "monthly_waste": 5000.0,
        "annual_savings": 60000.0,
        "leak_count": 2,
        "top_leaks": [
            {
                "type": "performance",
                "monthly_waste": 500.0,
                "annual_savings": 6000.0,
                "description": "Slow page load times",
                "severity": "high"
            }
        ],
        "qualification_score": 85,
        "priority_tier": "A",
        "outreach_ready": True,
        "qualification_date": "2023-01-02T12:00:00"
    }
    
    # Create from dictionary
    qualified = QualifiedProspect.from_dict(qualified_dict)
    
    # Check base Prospect attributes
    assert qualified.domain == "example.com"
    assert qualified.company_name == "Example Company"
    assert qualified.website == "https://example.com"
    assert qualified.industry == "Technology"
    assert qualified.employee_count == 50
    assert qualified.revenue == 1000000.0
    assert len(qualified.technologies) == 1
    assert qualified.technologies[0].name == "Python"
    assert len(qualified.contacts) == 1
    assert qualified.contacts[0].name == "John Doe"
    assert qualified.validation_score == 0.8
    assert qualified.leak_potential == 0.6
    
    # Check QualifiedProspect specific attributes
    assert qualified.estimated_revenue == 1200000.0
    assert qualified.monthly_waste == 5000.0
    assert qualified.annual_savings == 60000.0
    assert qualified.leak_count == 2
    assert qualified.qualification_score == 85
    assert qualified.priority_tier == "A"
    assert qualified.outreach_ready == True
    assert len(qualified.top_leaks) == 1
    assert qualified.top_leaks[0].type == "performance"
    assert qualified.top_leaks[0].monthly_waste == 500.0

def test_qualified_prospect_from_prospect():
    """Test creating a QualifiedProspect from a Prospect."""
    # Create a base prospect
    prospect = Prospect(
        domain="example.com",
        company_name="Example Company",
        website="https://example.com",
        industry="Technology",
        employee_count=50,
        revenue=1000000.0,
        validation_score=0.8,
        leak_potential=0.6
    )
    
    # Add a technology
    prospect.technologies.append(Technology(name="Python", category="Programming Language"))
    
    # Add a contact
    prospect.contacts.append(Contact(name="John Doe", email="john@example.com"))
    
    # Create QualifiedProspect from Prospect
    qualified = QualifiedProspect.from_prospect(prospect)
    
    # Check that base attributes were copied
    assert qualified.domain == "example.com"
    assert qualified.company_name == "Example Company"
    assert qualified.website == "https://example.com"
    assert qualified.industry == "Technology"
    assert qualified.employee_count == 50
    assert qualified.revenue == 1000000.0
    assert qualified.validation_score == 0.8
    assert qualified.leak_potential == 0.6
    assert len(qualified.technologies) == 1
    assert qualified.technologies[0].name == "Python"
    assert len(qualified.contacts) == 1
    assert qualified.contacts[0].name == "John Doe"
    
    # Check that QualifiedProspect specific attributes have default values
    assert qualified.estimated_revenue is None
    assert qualified.monthly_waste == 0.0
    assert qualified.annual_savings == 0.0
    assert qualified.leak_count == 0
    assert qualified.qualification_score == 0
    assert qualified.priority_tier == "C"
    assert qualified.outreach_ready == False
    assert len(qualified.top_leaks) == 0

if __name__ == "__main__":
    # Run the tests
    test_qualified_prospect_creation()
    test_qualified_prospect_with_leaks()
    test_leak_to_dict()
    test_leak_from_dict()
    test_qualified_prospect_to_dict()
    test_qualified_prospect_from_dict()
    test_qualified_prospect_from_prospect()
    print("All tests passed!")