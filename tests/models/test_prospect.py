"""
Test module for the Prospect model.

This module contains tests for the Prospect model implementation.
"""

import pytest
from datetime import datetime
from arco.models.prospect import Prospect, Technology, Contact

def test_prospect_creation():
    """Test creating a Prospect instance."""
    prospect = Prospect(
        domain="example.com",
        company_name="Example Company",
        website="https://example.com",
        industry="Technology",
        employee_count=50,
        revenue=1000000.0
    )
    
    assert prospect.domain == "example.com"
    assert prospect.company_name == "Example Company"
    assert prospect.website == "https://example.com"
    assert prospect.industry == "Technology"
    assert prospect.employee_count == 50
    assert prospect.revenue == 1000000.0
    assert isinstance(prospect.technologies, list)
    assert isinstance(prospect.contacts, list)
    assert isinstance(prospect.discovery_date, datetime)
    assert prospect.validation_score == 0.0
    assert prospect.leak_potential == 0.0

def test_prospect_with_technologies():
    """Test creating a Prospect with technologies."""
    prospect = Prospect(
        domain="example.com",
        company_name="Example Company"
    )
    
    # Add technologies
    prospect.technologies.append(Technology(name="Python", category="Programming Language"))
    prospect.technologies.append(Technology(name="React", category="Frontend Framework"))
    
    assert len(prospect.technologies) == 2
    assert prospect.technologies[0].name == "Python"
    assert prospect.technologies[0].category == "Programming Language"
    assert prospect.technologies[1].name == "React"
    assert prospect.technologies[1].category == "Frontend Framework"

def test_prospect_with_contacts():
    """Test creating a Prospect with contacts."""
    prospect = Prospect(
        domain="example.com",
        company_name="Example Company"
    )
    
    # Add contacts
    prospect.contacts.append(Contact(
        name="John Doe",
        email="john@example.com",
        phone="123-456-7890",
        position="CEO",
        linkedin="https://linkedin.com/in/johndoe"
    ))
    
    assert len(prospect.contacts) == 1
    assert prospect.contacts[0].name == "John Doe"
    assert prospect.contacts[0].email == "john@example.com"
    assert prospect.contacts[0].phone == "123-456-7890"
    assert prospect.contacts[0].position == "CEO"
    assert prospect.contacts[0].linkedin == "https://linkedin.com/in/johndoe"

def test_prospect_to_dict():
    """Test converting a Prospect to a dictionary."""
    prospect = Prospect(
        domain="example.com",
        company_name="Example Company",
        website="https://example.com",
        industry="Technology",
        employee_count=50,
        revenue=1000000.0
    )
    
    # Add a technology
    prospect.technologies.append(Technology(name="Python", category="Programming Language"))
    
    # Add a contact
    prospect.contacts.append(Contact(
        name="John Doe",
        email="john@example.com",
        position="CEO"
    ))
    
    # Convert to dictionary
    prospect_dict = prospect.to_dict()
    
    # Check the dictionary
    assert prospect_dict["domain"] == "example.com"
    assert prospect_dict["company_name"] == "Example Company"
    assert prospect_dict["website"] == "https://example.com"
    assert prospect_dict["industry"] == "Technology"
    assert prospect_dict["employee_count"] == 50
    assert prospect_dict["revenue"] == 1000000.0
    assert len(prospect_dict["technologies"]) == 1
    assert prospect_dict["technologies"][0]["name"] == "Python"
    assert len(prospect_dict["contacts"]) == 1
    assert prospect_dict["contacts"][0]["name"] == "John Doe"
    assert "discovery_date" in prospect_dict
    assert prospect_dict["validation_score"] == 0.0
    assert prospect_dict["leak_potential"] == 0.0

def test_prospect_from_dict():
    """Test creating a Prospect from a dictionary."""
    prospect_dict = {
        "domain": "example.com",
        "company_name": "Example Company",
        "website": "https://example.com",
        "industry": "Technology",
        "employee_count": 50,
        "revenue": 1000000.0,
        "technologies": [
            {"name": "Python", "category": "Programming Language", "version": "3.9"}
        ],
        "contacts": [
            {"name": "John Doe", "email": "john@example.com", "position": "CEO"}
        ],
        "discovery_date": "2023-01-01T12:00:00",
        "validation_score": 0.8,
        "leak_potential": 0.6
    }
    
    # Create from dictionary
    prospect = Prospect.from_dict(prospect_dict)
    
    # Check the prospect
    assert prospect.domain == "example.com"
    assert prospect.company_name == "Example Company"
    assert prospect.website == "https://example.com"
    assert prospect.industry == "Technology"
    assert prospect.employee_count == 50
    assert prospect.revenue == 1000000.0
    assert len(prospect.technologies) == 1
    assert prospect.technologies[0].name == "Python"
    assert prospect.technologies[0].category == "Programming Language"
    assert prospect.technologies[0].version == "3.9"
    assert len(prospect.contacts) == 1
    assert prospect.contacts[0].name == "John Doe"
    assert prospect.contacts[0].email == "john@example.com"
    assert prospect.contacts[0].position == "CEO"
    assert prospect.discovery_date.year == 2023
    assert prospect.discovery_date.month == 1
    assert prospect.discovery_date.day == 1
    assert prospect.validation_score == 0.8
    assert prospect.leak_potential == 0.6

if __name__ == "__main__":
    # Run the tests
    test_prospect_creation()
    test_prospect_with_technologies()
    test_prospect_with_contacts()
    test_prospect_to_dict()
    test_prospect_from_dict()
    print("All tests passed!")