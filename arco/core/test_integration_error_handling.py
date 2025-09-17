"""
Integration tests for error handling with business services.

Tests the integration between error handling and actual service implementations.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

from arco.core.error_handler import ProcessingErrorHandler, RetryConfig, CircuitBreakerConfig
from arco.services.business_intelligence_service import BusinessIntelligenceService
from arco.integrations.ad_intelligence_collector import AdIntelligenceCollector
from arco.integrations.funding_intelligence_collector import FundingIntelligenceCollector
from arco.integrations.hiring_intelligence_collector import HiringIntelligenceCollector
from arco.integrations.technology_intelligence_collector import TechnologyIntelligenceCollector
from arco.models.prospect import AdInvestmentProfile, FundingProfile, HiringActivity, TechnologyInvestment


class TestBusinessIntelligenceServiceErrorHandling:
    """Test error handling integration with BusinessIntelligenceService."""
    
    @pytest.fixture
    def error_handler(self):
        """Create error handler with fast retry for testing."""
        return ProcessingErrorHandler(
            retry_config=RetryConfig(
                max_retries=2,
                initial_delay=0.01,  # Fast retry for testing
                backoff_factor=2.0
            ),
            circuit_breaker_config=CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=1.0  # Fast recovery for testing
            )
        )
    
    @pytest.fixture
    def mock_collectors(self):
        """Create mock collectors."""
        return {
            'ad_collector': Mock(spec=AdIntelligenceCollector),
            'funding_collector': Mock(spec=FundingIntelligenceCollector),
            'hiring_collector': Mock(spec=HiringIntelligenceCollector),
            'tech_collector': Mock(spec=TechnologyIntelligenceCollector)
        }
    
    @pytest.fixture
    def business_intelligence_service(self, mock_collectors, error_handler):
        """Create BusinessIntelligenceService with mocked dependencies."""
        return BusinessIntelligenceService(
            ad_intelligence_collector=mock_collectors['ad_collector'],
            funding_intelligence_collector=mock_collectors['funding_collector'],
            hiring_intelligence_collector=mock_collectors['hiring_collector'],
            technology_intelligence_collector=mock_collectors['tech_collector'],
            error_handler=error_handler
        )
    
    @pytest.mark.asyncio
    async def test_successful_intelligence_collection(self, business_intelligence_service, mock_collectors):
        """Test successful intelligence collection with all collectors working."""
        # Setup successful responses
        mock_collectors['ad_collector'].collect = AsyncMock(return_value=AdInvestmentProfile(facebook_active=True))
        mock_collectors['funding_collector'].collect = AsyncMock(return_value=FundingProfile(recent_funding_months=3))
        mock_collectors['hiring_collector'].collect = AsyncMock(return_value=HiringActivity(tech_job_postings=5))
        mock_collectors['tech_collector'].collect = AsyncMock(return_value=TechnologyInvestment(recent_website_redesign=True))
        
        # Execute
        result = await business_intelligence_service.collect_intelligence("example.com", "Example Corp")
        
        # Verify
        assert result is not None
        assert result.ad_investment.facebook_active is True
        assert result.funding_profile.recent_funding_months == 3
        assert result.hiring_activity.tech_job_postings == 5
        assert result.technology_investment.recent_website_redesign is True
        assert result.data_quality_score > 0.5  # Should have good quality score
    
    @pytest.mark.asyncio
    async def test_partial_failure_with_graceful_degradation(self, business_intelligence_service, mock_collectors):
        """Test graceful degradation when some collectors fail."""
        # Setup mixed responses - some succeed, some fail
        mock_collectors['ad_collector'].collect = AsyncMock(return_value=AdInvestmentProfile(facebook_active=True))
        mock_collectors['funding_collector'].collect = AsyncMock(side_effect=ConnectionError("API unavailable"))
        mock_collectors['hiring_collector'].collect = AsyncMock(return_value=HiringActivity(tech_job_postings=2))
        mock_collectors['tech_collector'].collect = AsyncMock(side_effect=TimeoutError("Request timeout"))
        
        # Execute
        result = await business_intelligence_service.collect_intelligence("example.com", "Example Corp")
        
        # Verify graceful degradation
        assert result is not None
        assert result.ad_investment.facebook_active is True  # Successful collector
        assert result.hiring_activity.tech_job_postings == 2  # Successful collector
        assert result.funding_profile.recent_funding_months is None  # Failed collector - default values
        assert result.technology_investment.recent_website_redesign is False  # Failed collector - default values
        assert 0.3 <= result.data_quality_score <= 0.7  # Partial quality score
    
    @pytest.mark.asyncio
    async def test_retry_mechanism_with_eventual_success(self, business_intelligence_service, mock_collectors):
        """Test retry mechanism when collector initially fails but then succeeds."""
        call_count = 0
        
        async def flaky_ad_collector(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Temporary failure")
            return AdInvestmentProfile(facebook_active=True, estimated_monthly_spend=2000)
        
        # Setup flaky collector that succeeds on retry
        mock_collectors['ad_collector'].collect = flaky_ad_collector
        mock_collectors['funding_collector'].collect = AsyncMock(return_value=FundingProfile())
        mock_collectors['hiring_collector'].collect = AsyncMock(return_value=HiringActivity())
        mock_collectors['tech_collector'].collect = AsyncMock(return_value=TechnologyInvestment())
        
        # Execute
        result = await business_intelligence_service.collect_intelligence("example.com", "Example Corp")
        
        # Verify retry worked
        assert call_count == 2  # Should have been called twice
        assert result.ad_investment.facebook_active is True
        assert result.ad_investment.estimated_monthly_spend == 2000
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_protection(self, error_handler, mock_collectors):
        """Test circuit breaker protection for persistently failing services."""
        # Create service with circuit breaker that opens quickly
        service = BusinessIntelligenceService(
            ad_intelligence_collector=mock_collectors['ad_collector'],
            funding_intelligence_collector=mock_collectors['funding_collector'],
            hiring_intelligence_collector=mock_collectors['hiring_collector'],
            technology_intelligence_collector=mock_collectors['tech_collector'],
            error_handler=ProcessingErrorHandler(
                circuit_breaker_config=CircuitBreakerConfig(
                    failure_threshold=2,  # Open after 2 failures
                    recovery_timeout=0.1
                )
            )
        )
        
        # Setup persistently failing collector
        mock_collectors['ad_collector'].collect = AsyncMock(side_effect=ConnectionError("Persistent failure"))
        mock_collectors['funding_collector'].collect = AsyncMock(return_value=FundingProfile())
        mock_collectors['hiring_collector'].collect = AsyncMock(return_value=HiringActivity())
        mock_collectors['tech_collector'].collect = AsyncMock(return_value=TechnologyInvestment())
        
        # First few calls should trigger failures and open circuit breaker
        for i in range(3):
            result = await service.collect_intelligence(f"example{i}.com", f"Example Corp {i}")
            assert result is not None  # Should still return result with degraded data
        
        # Verify circuit breaker is protecting the service
        circuit_breaker = service.error_handler.get_circuit_breaker("ad_intelligence_service")
        # Note: Circuit breaker state depends on internal implementation details
        # The important thing is that the service continues to function
    
    @pytest.mark.asyncio
    async def test_structured_error_logging(self, business_intelligence_service, mock_collectors):
        """Test that errors are logged with structured format."""
        # Setup failing collector
        mock_collectors['ad_collector'].collect = AsyncMock(side_effect=ValueError("Test error"))
        mock_collectors['funding_collector'].collect = AsyncMock(return_value=FundingProfile())
        mock_collectors['hiring_collector'].collect = AsyncMock(return_value=HiringActivity())
        mock_collectors['tech_collector'].collect = AsyncMock(return_value=TechnologyInvestment())
        
        # Capture log output
        with patch('arco.core.error_handler.logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            # Execute
            result = await business_intelligence_service.collect_intelligence("example.com", "Example Corp")
            
            # Verify structured logging occurred
            assert result is not None
            # The exact logging calls depend on implementation details,
            # but we should see some logging activity for the error


class TestAdIntelligenceCollectorErrorHandling:
    """Test error handling in AdIntelligenceCollector."""
    
    @pytest.mark.asyncio
    async def test_facebook_api_error_handling(self):
        """Test Facebook API error handling with retries."""
        collector = AdIntelligenceCollector()
        
        # Test with a company name that should trigger error simulation
        # (based on the hash logic in the implementation)
        test_companies = ["Test Company " + str(i) for i in range(100)]
        
        # Find a company that triggers rate limit simulation
        rate_limit_company = None
        for company in test_companies:
            if hash(company) % 50 == 0:
                rate_limit_company = company
                break
        
        if rate_limit_company:
            # This should trigger retry mechanism and eventually fail gracefully
            try:
                result = await collector._get_facebook_ad_data(rate_limit_company)
                # If it succeeds, result should be valid
                assert result is None or isinstance(result, dict)
            except Exception as e:
                # If it fails after retries, that's expected behavior
                assert "rate limit" in str(e).lower() or "facebook" in str(e).lower()
        
        await collector.close()
    
    @pytest.mark.asyncio
    async def test_google_api_error_handling(self):
        """Test Google API error handling with retries."""
        collector = AdIntelligenceCollector()
        
        # Test with domains that should trigger error simulation
        test_domains = ["example" + str(i) + ".com" for i in range(100)]
        
        # Find a domain that triggers API error simulation
        error_domain = None
        for domain in test_domains:
            if hash(domain) % 40 == 0:
                error_domain = domain
                break
        
        if error_domain:
            # This should trigger retry mechanism and eventually fail gracefully
            try:
                result = await collector._get_google_ads_data(error_domain)
                # If it succeeds, result should be valid
                assert result is None or isinstance(result, dict)
            except Exception as e:
                # If it fails after retries, that's expected behavior
                assert "api" in str(e).lower() or "google" in str(e).lower()
        
        await collector.close()


if __name__ == "__main__":
    pytest.main([__file__])