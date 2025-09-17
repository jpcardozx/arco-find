"""
Test module for the StandardPipeline.

This module contains tests for the StandardPipeline implementation.
"""

import pytest
from unittest.mock import MagicMock, patch
from arco.pipelines.standard_pipeline import StandardPipeline
from arco.models.prospect import Prospect
from arco.models.qualified_prospect import QualifiedProspect
from arco.models.leak_result import LeakResult
from arco.engines.discovery_engine import DiscoveryEngine
from arco.engines.validator_engine import ValidatorEngine
from arco.engines.leak_engine import LeakEngine

@pytest.fixture
def mock_engines():
    """Create mock engines for testing."""
    discovery_engine = MagicMock(spec=DiscoveryEngine)
    validator_engine = MagicMock(spec=ValidatorEngine)
    leak_engine = MagicMock(spec=LeakEngine)
    
    # Configure discovery_engine mock
    discovery_engine.discover.return_value = [
        Prospect(domain="example.com", company_name="Example Company"),
        Prospect(domain="example.org", company_name="Example Organization")
    ]
    
    discovery_engine.enrich.return_value = Prospect(
        domain="example.com",
        company_name="Example Company",
        website="https://example.com",
        industry="Technology",
        employee_count=50,
        revenue=1000000.0
    )
    
    # Configure validator_engine mock
    def validate_mock(prospect):
        prospect.validation_score = 0.8
        return prospect
    
    validator_engine.validate.side_effect = validate_mock
    validator_engine.batch_validate.return_value = [
        Prospect(domain="example.com", company_name="Example Company", validation_score=0.8),
        Prospect(domain="example.org", company_name="Example Organization", validation_score=0.7)
    ]
    
    # Configure leak_engine mock
    leak_result = LeakResult(
        domain="example.com",
        total_monthly_waste=1000.0
    )
    
    qualified_prospect = QualifiedProspect(
        domain="example.com",
        company_name="Example Company",
        monthly_waste=1000.0,
        annual_savings=12000.0,
        leak_count=2,
        qualification_score=85,
        priority_tier="A"
    )
    
    leak_engine.analyze.return_value = leak_result
    leak_engine.qualify.return_value = qualified_prospect
    
    return {
        "discovery_engine": discovery_engine,
        "validator_engine": validator_engine,
        "leak_engine": leak_engine
    }

def test_standard_pipeline_init(mock_engines):
    """Test the initialization of StandardPipeline."""
    pipeline = StandardPipeline(
        discovery_engine=mock_engines["discovery_engine"],
        validator_engine=mock_engines["validator_engine"],
        leak_engine=mock_engines["leak_engine"]
    )
    
    assert pipeline is not None
    assert pipeline.discovery_engine == mock_engines["discovery_engine"]
    assert pipeline.validator_engine == mock_engines["validator_engine"]
    assert pipeline.leak_engine == mock_engines["leak_engine"]
    assert pipeline.stats == {
        "prospects_discovered": 0,
        "prospects_validated": 0,
        "prospects_qualified": 0,
        "total_monthly_waste": 0.0,
        "total_annual_savings": 0.0,
        "processing_time": 0.0
    }

def test_standard_pipeline_run_with_query(mock_engines):
    """Test running the StandardPipeline with a search query."""
    pipeline = StandardPipeline(
        discovery_engine=mock_engines["discovery_engine"],
        validator_engine=mock_engines["validator_engine"],
        leak_engine=mock_engines["leak_engine"]
    )
    
    # Run the pipeline with a query
    results = pipeline.run("test query")
    
    # Check that the engines were called correctly
    mock_engines["discovery_engine"].discover.assert_called_once_with("test query", limit=10)
    assert mock_engines["validator_engine"].batch_validate.call_count == 1
    assert mock_engines["leak_engine"].analyze.call_count == 2
    assert mock_engines["leak_engine"].qualify.call_count == 2
    
    # Check the results
    assert len(results) == 2
    assert all(isinstance(r, QualifiedProspect) for r in results)
    
    # Check the stats
    stats = pipeline.get_stats()
    assert stats["prospects_discovered"] == 2
    assert stats["prospects_validated"] == 2
    assert stats["prospects_qualified"] == 2
    assert stats["total_monthly_waste"] > 0
    assert stats["total_annual_savings"] > 0

def test_standard_pipeline_run_with_domains(mock_engines):
    """Test running the StandardPipeline with a list of domains."""
    pipeline = StandardPipeline(
        discovery_engine=mock_engines["discovery_engine"],
        validator_engine=mock_engines["validator_engine"],
        leak_engine=mock_engines["leak_engine"]
    )
    
    # Run the pipeline with domains
    domains = ["example.com", "example.org"]
    results = pipeline.run(domains)
    
    # Check that the engines were called correctly
    mock_engines["discovery_engine"].discover_multiple.assert_called_once_with(domains)
    assert mock_engines["validator_engine"].batch_validate.call_count == 1
    assert mock_engines["leak_engine"].analyze.call_count == 2
    assert mock_engines["leak_engine"].qualify.call_count == 2
    
    # Check the results
    assert len(results) == 2
    assert all(isinstance(r, QualifiedProspect) for r in results)

def test_standard_pipeline_process_prospect(mock_engines):
    """Test processing a single prospect through the StandardPipeline."""
    pipeline = StandardPipeline(
        discovery_engine=mock_engines["discovery_engine"],
        validator_engine=mock_engines["validator_engine"],
        leak_engine=mock_engines["leak_engine"]
    )
    
    # Create a test prospect
    prospect = Prospect(
        domain="example.com",
        company_name="Example Company"
    )
    
    # Process the prospect
    result = pipeline.process_prospect(prospect)
    
    # Check that the engines were called correctly
    mock_engines["discovery_engine"].enrich.assert_called_once_with(prospect)
    mock_engines["validator_engine"].validate.assert_called_once()
    mock_engines["leak_engine"].analyze.assert_called_once()
    mock_engines["leak_engine"].qualify.assert_called_once()
    
    # Check the result
    assert isinstance(result, QualifiedProspect)
    assert result.domain == "example.com"
    assert result.company_name == "Example Company"
    
    # Check the stats
    stats = pipeline.get_stats()
    assert stats["prospects_discovered"] == 0  # Not incremented for process_prospect
    assert stats["prospects_validated"] == 1
    assert stats["prospects_qualified"] == 1
    assert stats["total_monthly_waste"] > 0
    assert stats["total_annual_savings"] > 0

if __name__ == "__main__":
    # Run the tests
    pytest.main(["-v", __file__])