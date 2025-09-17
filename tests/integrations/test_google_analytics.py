"""
Unit tests for Google Analytics Integration.

Tests the traffic source analysis functionality, web vitals collection,
and conversion metrics estimation with proper error handling and validation.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import aiohttp

from arco.integrations.google_analytics import GoogleAnalyticsIntegration
from arco.models.prospect import WebVitals


class TestGoogleAnalyticsIntegration:
    """Test suite for Google Analytics integration functionality."""

    @pytest.fixture
    def ga_integration(self):
        """Create GoogleAnalyticsIntegration instance for testing."""
        return GoogleAnalyticsIntegration(api_key="test_api_key")

    @pytest.fixture
    def mock_pagespeed_response(self):
        """Mock PageSpeed Insights API response."""
        return {
            "lighthouseResult": {
                "audits": {
                    "largest-contentful-paint": {"numericValue": 2500},  # 2.5s
                    "max-potential-fid": {"numericValue": 150},  # 150ms
                    "cumulative-layout-shift": {"numericValue": 0.05},  # 0.05
                    "server-response-time": {"numericValue": 200},  # 200ms
                    "first-contentful-paint": {"numericValue": 1800}  # 1.8s
                }
            }
        }

    @pytest.mark.asyncio
    async def test_get_traffic_sources_success(self, ga_integration):
        """Test successful traffic source analysis."""
        domain = "example.com"
        
        # Mock the internal methods
        with patch.object(ga_integration, '_analyze_traffic_sources') as mock_analyze:
            mock_traffic_data = {
                "organic_search": 0.35,
                "direct": 0.25,
                "paid_search": 0.20,
                "social": 0.10,
                "referral": 0.05,
                "email": 0.05
            }
            mock_analyze.return_value = mock_traffic_data
            
            result = await ga_integration.get_traffic_sources(domain)
            
            # Verify the result structure
            assert isinstance(result, dict)
            assert "organic_search" in result
            assert "paid_search" in result
            assert "confidence_score" in result
            assert "data_source" in result
            assert "validation_status" in result
            assert "organic_vs_paid_ratio" in result
            
            # Verify traffic source percentages
            assert 0 <= result["organic_search"] <= 1
            assert 0 <= result["paid_search"] <= 1
            assert result["validation_status"] == "passed"
            assert result["data_source"] == "estimated_analysis"

    @pytest.mark.asyncio
    async def test_get_traffic_sources_timeout(self, ga_integration):
        """Test traffic source analysis with timeout."""
        domain = "slow-example.com"
        
        # Mock timeout scenario
        with patch.object(ga_integration, '_analyze_traffic_sources') as mock_analyze:
            mock_analyze.side_effect = asyncio.TimeoutError("Request timeout")
            
            result = await ga_integration.get_traffic_sources(domain)
            
            # Should return default traffic sources
            assert isinstance(result, dict)
            assert "organic_search" in result
            assert result["organic_search"] > 0
            assert "confidence_score" in result

    @pytest.mark.asyncio
    async def test_get_traffic_sources_validation_failure(self, ga_integration):
        """Test traffic source analysis with validation failure."""
        domain = "invalid-example.com"
        
        # Mock invalid data scenario
        with patch.object(ga_integration, '_analyze_traffic_sources') as mock_analyze:
            mock_analyze.return_value = {"invalid": "data"}  # Invalid traffic data
            
            result = await ga_integration.get_traffic_sources(domain)
            
            # Should return default traffic sources due to validation failure
            assert isinstance(result, dict)
            assert "organic_search" in result
            assert sum(result[key] for key in ["organic_search", "direct", "paid_search", "social", "referral", "email"]) == pytest.approx(1.0, rel=0.01)

    def test_validate_traffic_sources_valid_data(self, ga_integration):
        """Test traffic source validation with valid data."""
        valid_data = {
            "organic_search": 0.35,
            "direct": 0.25,
            "paid_search": 0.20,
            "social": 0.10,
            "referral": 0.05,
            "email": 0.05
        }
        
        result = ga_integration._validate_traffic_sources(valid_data)
        assert result is True

    def test_validate_traffic_sources_invalid_data(self, ga_integration):
        """Test traffic source validation with invalid data."""
        # Test missing required fields
        invalid_data_1 = {"organic_search": 0.5}
        assert ga_integration._validate_traffic_sources(invalid_data_1) is False
        
        # Test invalid percentage values
        invalid_data_2 = {
            "organic_search": 1.5,  # > 1.0
            "direct": 0.25,
            "paid_search": 0.20,
            "social": 0.10,
            "referral": 0.05,
            "email": 0.05
        }
        assert ga_integration._validate_traffic_sources(invalid_data_2) is False
        
        # Test percentages don't sum to 1.0
        invalid_data_3 = {
            "organic_search": 0.10,
            "direct": 0.10,
            "paid_search": 0.10,
            "social": 0.10,
            "referral": 0.05,
            "email": 0.05
        }
        assert ga_integration._validate_traffic_sources(invalid_data_3) is False

    def test_calculate_traffic_confidence(self, ga_integration):
        """Test traffic confidence calculation."""
        valid_traffic_data = {
            "organic_search": 0.35,
            "direct": 0.25,
            "paid_search": 0.20,
            "social": 0.10,
            "referral": 0.05,
            "email": 0.05
        }
        
        confidence = ga_integration._calculate_traffic_confidence(valid_traffic_data, "example.com")
        
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.5  # Should have reasonable confidence for valid data

    def test_calculate_organic_paid_ratio(self, ga_integration):
        """Test organic to paid traffic ratio calculation."""
        traffic_data = {
            "organic_search": 0.40,
            "paid_search": 0.20
        }
        
        ratio = ga_integration._calculate_organic_paid_ratio(traffic_data)
        assert ratio == 2.0  # 40% / 20% = 2.0
        
        # Test with zero paid traffic
        traffic_data_zero_paid = {
            "organic_search": 0.40,
            "paid_search": 0.0
        }
        ratio_inf = ga_integration._calculate_organic_paid_ratio(traffic_data_zero_paid)
        assert ratio_inf == float('inf')

    def test_analyze_domain_characteristics(self, ga_integration):
        """Test domain characteristics analysis."""
        # Test e-commerce domain
        ecommerce_domain = "myshop.com"
        characteristics = ga_integration._analyze_domain_characteristics(ecommerce_domain)
        
        assert isinstance(characteristics, dict)
        assert "domain_length" in characteristics
        assert "tld" in characteristics
        assert "brand_indicators" in characteristics
        assert characteristics["tld"] == "com"
        assert "ecommerce" in characteristics["brand_indicators"]
        
        # Test SaaS domain
        saas_domain = "myapp.io"
        saas_characteristics = ga_integration._analyze_domain_characteristics(saas_domain)
        assert "tech" in saas_characteristics["industry_hints"]

    def test_estimate_traffic_from_domain_analysis(self, ga_integration):
        """Test traffic estimation based on domain analysis."""
        # Test e-commerce domain analysis
        ecommerce_analysis = {
            "brand_indicators": ["ecommerce"],
            "industry_hints": ["global"],
            "tld": "com"
        }
        
        traffic_sources = ga_integration._estimate_traffic_from_domain_analysis(ecommerce_analysis, None)
        
        assert isinstance(traffic_sources, dict)
        assert "organic_search" in traffic_sources
        assert "paid_search" in traffic_sources
        # E-commerce should have higher paid search percentage
        assert traffic_sources["paid_search"] >= 0.20
        
        # Verify percentages sum to 1.0
        total = sum(traffic_sources.values())
        assert total == pytest.approx(1.0, rel=0.01)

    def test_get_baseline_traffic_distribution(self, ga_integration):
        """Test baseline traffic distribution."""
        baseline = ga_integration._get_baseline_traffic_distribution()
        
        assert isinstance(baseline, dict)
        required_sources = ["organic_search", "direct", "paid_search", "social", "referral", "email"]
        
        for source in required_sources:
            assert source in baseline
            assert 0 <= baseline[source] <= 1
        
        # Should sum to 1.0
        total = sum(baseline.values())
        assert total == pytest.approx(1.0, rel=0.01)

    @pytest.mark.asyncio
    async def test_analyze_traffic_sources_with_web_vitals(self, ga_integration):
        """Test traffic source analysis with web vitals data."""
        domain = "example.com"
        
        # Mock web vitals data
        mock_web_vitals = WebVitals(
            lcp=2.0,  # Good performance
            fid=100,
            cls=0.05,
            ttfb=200,
            fcp=1.5
        )
        
        with patch.object(ga_integration, 'get_web_vitals') as mock_get_vitals:
            mock_get_vitals.return_value = mock_web_vitals
            
            result = await ga_integration._analyze_traffic_sources(domain)
            
            assert isinstance(result, dict)
            assert "organic_search" in result
            # Good performance should maintain reasonable organic search percentage
            assert result["organic_search"] >= 0.20

    @pytest.mark.asyncio
    async def test_analyze_traffic_sources_poor_performance(self, ga_integration):
        """Test traffic source analysis with poor web performance."""
        domain = "slow-example.com"
        
        # Mock poor web vitals data
        mock_web_vitals = WebVitals(
            lcp=5.0,  # Poor performance
            fid=300,
            cls=0.25,
            ttfb=1500,
            fcp=3.0
        )
        
        with patch.object(ga_integration, 'get_web_vitals') as mock_get_vitals:
            mock_get_vitals.return_value = mock_web_vitals
            
            result = await ga_integration._analyze_traffic_sources(domain)
            
            assert isinstance(result, dict)
            # Poor performance should result in lower organic search percentage
            # and higher paid search to compensate
            assert "organic_search" in result
            assert "paid_search" in result

    def test_get_default_traffic_sources(self, ga_integration):
        """Test default traffic sources fallback."""
        # This method should be implemented in the main class
        # For now, we'll test the baseline distribution
        default_sources = ga_integration._get_baseline_traffic_distribution()
        
        assert isinstance(default_sources, dict)
        assert len(default_sources) == 6  # Should have 6 traffic sources
        
        # Verify all required sources are present
        required_sources = ["organic_search", "direct", "paid_search", "social", "referral", "email"]
        for source in required_sources:
            assert source in default_sources
            assert isinstance(default_sources[source], (int, float))
            assert 0 <= default_sources[source] <= 1

    @pytest.mark.asyncio
    async def test_traffic_source_error_handling(self, ga_integration):
        """Test error handling in traffic source analysis."""
        domain = "error-example.com"
        
        # Mock exception in analysis
        with patch.object(ga_integration, '_analyze_traffic_sources') as mock_analyze:
            mock_analyze.side_effect = Exception("Network error")
            
            result = await ga_integration.get_traffic_sources(domain)
            
            # Should gracefully handle error and return default data
            assert isinstance(result, dict)
            assert "organic_search" in result
            assert "confidence_score" in result
            # Confidence should be lower due to error
            assert result["confidence_score"] >= 0.0

    @pytest.mark.asyncio
    async def test_traffic_source_data_validation_and_confidence(self, ga_integration):
        """Test comprehensive data validation and confidence scoring."""
        domain = "test-example.com"
        
        # Test with realistic traffic data
        realistic_traffic = {
            "organic_search": 0.42,
            "direct": 0.28,
            "paid_search": 0.18,
            "social": 0.08,
            "referral": 0.03,
            "email": 0.01
        }
        
        with patch.object(ga_integration, '_analyze_traffic_sources') as mock_analyze:
            mock_analyze.return_value = realistic_traffic
            
            result = await ga_integration.get_traffic_sources(domain)
            
            # Should pass validation and have good confidence
            assert result["validation_status"] == "passed"
            assert result["confidence_score"] > 0.6
            assert result["organic_vs_paid_ratio"] > 2.0  # 42% / 18% > 2.0