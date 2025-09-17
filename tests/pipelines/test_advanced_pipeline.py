"""
Test module for the AdvancedPipeline.

This module contains tests for the AdvancedPipeline implementation.
"""

import pytest
from unittest.mock import MagicMock, patch
from arco.pipelines.advanced_pipeline import AdvancedPipeline
from arco.models.prospect import Prospect, Technology
from arco.models.qualified_prospect import QualifiedProspect, Leak
from arco.models.leak_result import LeakResult
from arco.engines.discovery_engine import DiscoveryEngine
from arco.engines.validator_engine import ValidatorEngine
from arco.engines.leak_engine import LeakEngine
from arco.integrations import WappalyzerIntegration, GooglePageSpeedAPI

@pytest.fixture
def mock_engines_and_integrations():
    """Create mock engines and integrations for testing."""
    discovery_engine = MagicMock(spec=DiscoveryEngine)
    validator_engine = MagicMock(spec=ValidatorEngine)
    leak_engine = MagicMock(spec=LeakEngine)
    wappalyzer = MagicMock(spec=WappalyzerIntegration)
    pagespeed = MagicMock(spec=GooglePageSpeedAPI)
    
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
    
    # Configure wappalyzer mock
    wappalyzer.analyze_url.return_value = {
        "technologies": [
            {"name": "Shopify", "categories": ["E-commerce"]},
            {"name": "React", "categories": ["JavaScript Frameworks"]}
        ]
    }
    
    # Configure pagespeed mock
    pagespeed.analyze_url.return_value = {
        "performance_score": 85,
        "metrics": {
            "first-contentful-paint": {
                "score": 0.9,
                "value": 1200
            },
            "largest-contentful-paint": {
                "score": 0.8,
                "value": 2500
            }
        }
    }
    
    pagespeed.calculate_performance_loss.return_value = {
        "performance_score": 85,
        "conversion_impact_percentage": 1.5,
        "estimated_monthly_loss": 150,
        "estimated_annual_loss": 1800,
        "estimated_monthly_revenue": 10000
    }
    
    return {
        "discovery_engine": discovery_engine,
        "validator_engine": validator_engine,
        "leak_engine": leak_engine,
        "wappalyzer": wappalyzer,
        "pagespeed": pagespeed
    }

def test_advanced_pipeline_init(mock_engines_and_integrations):
    """Test the initialization of AdvancedPipeline."""
    pipeline = AdvancedPipeline(
        discovery_engine=mock_engines_and_integrations["discovery_engine"],
        validator_engine=mock_engines_and_integrations["validator_engine"],
        leak_engine=mock_engines_and_integrations["leak_engine"],
        wappalyzer=mock_engines_and_integrations["wappalyzer"],
        pagespeed=mock_engines_and_integrations["pagespeed"]
    )
    
    assert pipeline is not None
    assert pipeline.discovery_engine == mock_engines_and_integrations["discovery_engine"]
    assert pipeline.validator_engine == mock_engines_and_integrations["validator_engine"]
    assert pipeline.leak_engine == mock_engines_and_integrations["leak_engine"]
    assert pipeline.wappalyzer == mock_engines_and_integrations["wappalyzer"]
    assert pipeline.pagespeed == mock_engines_and_integrations["pagespeed"]
    assert pipeline.stats == {
        "prospects_discovered": 0,
        "prospects_validated": 0,
        "prospects_qualified": 0,
        "total_monthly_waste": 0.0,
        "total_annual_savings": 0.0,
        "processing_time": 0.0,
        "technologies_detected": 0,
        "performance_issues_detected": 0
    }

def test_advanced_pipeline_run_with_query(mock_engines_and_integrations):
    """Test running the AdvancedPipeline with a search query."""
    pipeline = AdvancedPipeline(
        discovery_engine=mock_engines_and_integrations["discovery_engine"],
        validator_engine=mock_engines_and_integrations["validator_engine"],
        leak_engine=mock_engines_and_integrations["leak_engine"],
        wappalyzer=mock_engines_and_integrations["wappalyzer"],
        pagespeed=mock_engines_and_integrations["pagespeed"]
    )
    
    # Run the pipeline with a query
    results = pipeline.run("test query")
    
    # Check that the engines were called correctly
    mock_engines_and_integrations["discovery_engine"].discover.assert_called_once_with("test query", limit=10)
    assert mock_engines_and_integrations["validator_engine"].batch_validate.call_count == 1
    assert mock_engines_and_integrations["leak_engine"].analyze.call_count == 2
    assert mock_engines_and_integrations["leak_engine"].qualify.call_count == 2
    
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
    assert "technologies_detected" in stats
    assert "performance_issues_detected" in stats

def test_advanced_pipeline_process_prospect(mock_engines_and_integrations):
    """Test processing a single prospect through the AdvancedPipeline."""
    pipeline = AdvancedPipeline(
        discovery_engine=mock_engines_and_integrations["discovery_engine"],
        validator_engine=mock_engines_and_integrations["validator_engine"],
        leak_engine=mock_engines_and_integrations["leak_engine"],
        wappalyzer=mock_engines_and_integrations["wappalyzer"],
        pagespeed=mock_engines_and_integrations["pagespeed"]
    )
    
    # Create a test prospect
    prospect = Prospect(
        domain="example.com",
        company_name="Example Company",
        website="https://example.com",
        revenue=10000.0
    )
    
    # Process the prospect
    result = pipeline.process_prospect(prospect)
    
    # Check that the engines and integrations were called correctly
    mock_engines_and_integrations["discovery_engine"].enrich.assert_called_once_with(prospect)
    mock_engines_and_integrations["validator_engine"].validate.assert_called_once()
    mock_engines_and_integrations["leak_engine"].analyze.assert_called_once()
    mock_engines_and_integrations["leak_engine"].qualify.assert_called_once()
    mock_engines_and_integrations["wappalyzer"].analyze_url.assert_called_once()
    mock_engines_and_integrations["pagespeed"].analyze_url.assert_called_once()
    mock_engines_and_integrations["pagespeed"].calculate_performance_loss.assert_called_once()
    
    # Check the result
    assert isinstance(result, QualifiedProspect)
    assert result.domain == "example.com"
    assert result.company_name == "Example Company"
    
    # Check the stats
    stats = pipeline.get_stats()
    assert stats["prospects_validated"] == 1
    assert stats["prospects_qualified"] == 1
    assert stats["total_monthly_waste"] > 0
    assert stats["total_annual_savings"] > 0
    assert stats["technologies_detected"] > 0
    assert stats["performance_issues_detected"] > 0

def test_advanced_pipeline_enrich_with_technologies(mock_engines_and_integrations):
    """Test enriching a prospect with technologies in the AdvancedPipeline."""
    pipeline = AdvancedPipeline(
        discovery_engine=mock_engines_and_integrations["discovery_engine"],
        validator_engine=mock_engines_and_integrations["validator_engine"],
        leak_engine=mock_engines_and_integrations["leak_engine"],
        wappalyzer=mock_engines_and_integrations["wappalyzer"],
        pagespeed=mock_engines_and_integrations["pagespeed"]
    )
    
    # Create a test prospect
    prospect = Prospect(
        domain="example.com",
        company_name="Example Company",
        website="https://example.com"
    )
    
    # Call the internal method to enrich with technologies
    pipeline._enrich_with_technologies(prospect)
    
    # Check that wappalyzer was called
    mock_engines_and_integrations["wappalyzer"].analyze_url.assert_called_once_with("https://example.com")
    
    # Check that technologies were added to the prospect
    assert len(prospect.technologies) == 2
    assert any(tech.name == "Shopify" for tech in prospect.technologies)
    assert any(tech.name == "React" for tech in prospect.technologies)

def test_advanced_pipeline_analyze_performance(mock_engines_and_integrations):
    """Test analyzing performance in the AdvancedPipeline."""
    pipeline = AdvancedPipeline(
        discovery_engine=mock_engines_and_integrations["discovery_engine"],
        validator_engine=mock_engines_and_integrations["validator_engine"],
        leak_engine=mock_engines_and_integrations["leak_engine"],
        wappalyzer=mock_engines_and_integrations["wappalyzer"],
        pagespeed=mock_engines_and_integrations["pagespeed"]
    )
    
    # Create a test prospect
    prospect = Prospect(
        domain="example.com",
        company_name="Example Company",
        website="https://example.com",
        revenue=10000.0
    )
    
    # Create a leak result
    leak_result = LeakResult(
        domain="example.com",
        total_monthly_waste=500.0
    )
    
    # Call the internal method to analyze performance
    pipeline._analyze_performance(prospect, leak_result)
    
    # Check that pagespeed was called
    mock_engines_and_integrations["pagespeed"].analyze_url.assert_called_once_with("https://example.com")
    mock_engines_and_integrations["pagespeed"].calculate_performance_loss.assert_called_once_with(85, 10000.0)
    
    # Check that a performance leak was added
    assert len(leak_result.leaks) == 1
    assert leak_result.leaks[0].type == "performance"
    assert leak_result.leaks[0].monthly_waste == 150.0
    assert leak_result.leaks[0].annual_savings == 1800.0
    assert leak_result.total_monthly_waste == 650.0  # 500 + 150

if __name__ == "__main__":
    # Run the tests
    pytest.main(["-v", __file__])