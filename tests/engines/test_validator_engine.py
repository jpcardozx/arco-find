"""
Test module for the ValidatorEngine.

This module contains tests for the ValidatorEngine implementation.
"""

import pytest
import asyncio
from arco.engines.validator_engine import ValidatorEngine
from arco.models.prospect import Prospect, Technology, Contact

def test_validator_engine_init():
    """Test the initialization of ValidatorEngine."""
    engine = ValidatorEngine()
    assert engine is not None
    assert engine.validation_thresholds is not None
    assert engine.validation_thresholds['domain_existence'] == 0.4
    assert engine.validation_thresholds['company_info'] == 0.3
    assert engine.validation_thresholds['technology_info'] == 0.2
    assert engine.validation_thresholds['contact_info'] == 0.1

def test_validator_engine_validate():
    """Test the validate method of ValidatorEngine."""
    # Create a test prospect
    prospect = Prospect(
        domain="example.com",
        company_name="Example Company",
        website="https://example.com",
        industry="Technology",
        employee_count=50,
        revenue=1000000.0
    )
    
    # Add technologies
    prospect.technologies.append(Technology(name="Python", category="Programming Language"))
    prospect.technologies.append(Technology(name="React", category="Frontend Framework"))
    
    # Add contacts
    prospect.contacts.append(Contact(
        name="John Doe",
        email="john@example.com",
        phone="123-456-7890",
        position="CEO",
        linkedin="https://linkedin.com/in/johndoe"
    ))
    
    # Create the engine
    engine = ValidatorEngine()
    
    # Validate the prospect
    validated = engine.validate(prospect)
    
    # Check the result
    assert validated is not None
    assert validated.domain == "example.com"
    assert validated.validation_score > 0.0

def test_validator_engine_batch_validate():
    """Test the batch_validate method of ValidatorEngine."""
    # Create test prospects
    prospect1 = Prospect(
        domain="example.com",
        company_name="Example Company"
    )
    
    prospect2 = Prospect(
        domain="example.org",
        company_name="Example Organization",
        technologies=[Technology(name="Python", category="Programming Language")]
    )
    
    # Create the engine
    engine = ValidatorEngine()
    
    # Validate the prospects
    validated = engine.batch_validate([prospect1, prospect2])
    
    # Check the results
    assert len(validated) == 2
    assert validated[0].domain == "example.com"
    assert validated[1].domain == "example.org"
    assert validated[0].validation_score >= 0.0
    assert validated[1].validation_score >= 0.0

def test_validator_engine_validation_scoring():
    """Test the validation scoring of ValidatorEngine."""
    # Create test prospects with different levels of completeness
    
    # Minimal prospect
    minimal = Prospect(
        domain="minimal.com"
    )
    
    # Partial prospect
    partial = Prospect(
        domain="partial.com",
        company_name="Partial Company",
        website="https://partial.com"
    )
    
    # Complete prospect
    complete = Prospect(
        domain="complete.com",
        company_name="Complete Company",
        website="https://complete.com",
        industry="Technology",
        employee_count=100,
        revenue=5000000.0
    )
    complete.technologies.append(Technology(name="Python", category="Programming Language"))
    complete.technologies.append(Technology(name="React", category="Frontend Framework"))
    complete.contacts.append(Contact(
        name="John Doe",
        email="john@complete.com",
        position="CEO"
    ))
    
    # Create the engine
    engine = ValidatorEngine()
    
    # Validate the prospects
    validated_minimal = engine.validate(minimal)
    validated_partial = engine.validate(partial)
    validated_complete = engine.validate(complete)
    
    # Check the results
    assert validated_minimal.validation_score < validated_partial.validation_score
    assert validated_partial.validation_score < validated_complete.validation_score

if __name__ == "__main__":
    # Run the tests
    test_validator_engine_init()
    test_validator_engine_validate()
    test_validator_engine_batch_validate()
    test_validator_engine_validation_scoring()
    print("All tests passed!")