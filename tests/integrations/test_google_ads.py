"""
Unit tests for Google Ads Integration.

Tests the campaign metrics collection, keyword performance analysis,
and ad efficiency calculations with proper error handling and validation.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import aiohttp

from arco.integrations.google_ads import GoogleAdsIntegration
from arco.models.prospect import AdSpendData


class TestGoogleAdsIntegration:
    """Test suite for Google Ads integration functionality."""

    @pytest.fixture
    def ads_integration(self):
        """Create GoogleAdsIntegration instance for testing."""
        return GoogleAdsIntegration(
            developer_token="test_token",
            client_id="test_client_id",
            client_secret="test_client_secret",
            refresh_token="test_refresh_token"
        )

    @pytest.fixture
    def mock_campaign_response(self):
        """Mock Google Ads API campaign response."""
        return {
            "results": [
                {
                    "campaign": {
                        "id": "123456789",
                        "name": "Test Campaign",
                        "status": "ENABLED"
                    },
                    "metrics": {
                        "costMicros": "5000000000",  # $5000
                        "clicks": "2000",
                        "impressions": "100000",
                        "ctr": "0.02",
                        "averageCpc": "2500000",  # $2.50
                        "conversions": "60",
                        "conversionRate": "0.03",
                        "costPerConversion": "83333333",  # $83.33
                        "valuePerConversion": "150000000"  # $150
                    }
                }
            ]
        }

    @pytest.mark.asyncio
    async def test_get_campaign_metrics_with_api_data(self, ads_integration, mock_campaign_response):
        """Test campaign metrics collection with real API data."""
        customer_id = "1234567890"
        domain = "example.com"
        
        # Mock the API call
        with patch.object(ads_integration, '_get_access_token') as mock_token:
            mock_token.return_value = "test_access_token"
            
            with patch.object(ads_integration, '_init_session') as mock_session:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json.return_value = mock_campaign_response
                
                mock_session_obj = AsyncMock()
                mock_session_obj.post.return_value.__aenter__.return_value = mock_response
                ads_integration.session = mock_session_obj
                
                result = await ads_integration.get_campaign_metrics(customer_id, domain)
                
                # Verify the result structure
                assert isinstance(result, dict)
                assert "monthly_spend" in result
                assert "avg_cpc" in result
                assert "avg_ctr" in result
                assert "conversion_rate" in result
                assert "data_source" in result
                
                # Verify calculated values
                assert result["monthly_spend"] == 5000.0  # $5000
                assert result["avg_cpc"] == 2.5  # $2.50
                assert result["avg_ctr"] == 0.02  # 2%
                assert result["conversion_rate"] == 0.03  # 3%
                assert result["data_source"] == "google_ads_api"

    @pytest.mark.asyncio
    async def test_get_campaign_metrics_without_credentials(self, ads_integration):
        """Test campaign metrics collection without API credentials."""
        # Remove credentials
        ads_integration.developer_token = None
        
        customer_id = "1234567890"
        domain = "example.com"
        
        result = await ads_integration.get_campaign_metrics(customer_id, domain)
        
        # Should return estimated data
        assert isinstance(result, dict)
        assert result["data_source"] == "industry_estimates"
        assert "monthly_spend" in result
        assert "avg_cpc" in result
        assert result["confidence_level"] == "low"

    @pytest.mark.asyncio
    async def test_get_campaign_metrics_api_failure(self, ads_integration):
        """Test campaign metrics collection with API failure."""
        customer_id = "1234567890"
        domain = "example.com"
        
        # Mock API failure
        with patch.object(ads_integration, '_get_access_token') as mock_token:
            mock_token.return_value = "test_access_token"
            
            with patch.object(ads_integration, '_init_session') as mock_session:
                mock_response = AsyncMock()
                mock_response.status = 500  # Server error
                
                mock_session_obj = AsyncMock()
                mock_session_obj.post.return_value.__aenter__.return_value = mock_response
                ads_integration.session = mock_session_obj
                
                result = await ads_integration.get_campaign_metrics(customer_id, domain)
                
                # Should fallback to estimates
                assert isinstance(result, dict)
                assert result["data_source"] == "industry_estimates"

    def test_get_estimated_campaign_metrics_ecommerce(self, ads_integration):
        """Test estimated campaign metrics for e-commerce domain."""
        domain = "myshop.com"
        
        result = ads_integration._get_estimated_campaign_metrics(domain)
        
        assert isinstance(result, dict)
        assert result["data_source"] == "industry_estimates"
        assert result["avg_cpc"] == 1.16  # E-commerce CPC
        assert result["monthly_spend"] > 0
        assert "clicks" in result
        assert "impressions" in result

    def test_get_estimated_campaign_metrics_saas(self, ads_integration):
        """Test estimated campaign metrics for SaaS domain."""
        domain = "myapp-saas.com"
        
        result = ads_integration._get_estimated_campaign_metrics(domain)
        
        assert isinstance(result, dict)
        assert result["avg_cpc"] == 3.80  # SaaS CPC (higher)
        assert result["monthly_spend"] > 5000  # Higher spend for SaaS

    @pytest.mark.asyncio
    async def test_get_keyword_performance_with_estimates(self, ads_integration):
        """Test keyword performance analysis with estimates."""
        customer_id = "1234567890"
        domain = "example.com"
        
        # Mock no credentials to force estimates
        ads_integration.developer_token = None
        
        result = await ads_integration.get_keyword_performance(customer_id, domain)
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Check first keyword structure
        keyword = result[0]
        assert "keyword" in keyword
        assert "match_type" in keyword
        assert "cost" in keyword
        assert "clicks" in keyword
        assert "conversion_rate" in keyword
        assert "quality_score" in keyword

    def test_calculate_overall_efficiency(self, ads_integration):
        """Test overall advertising efficiency calculation."""
        campaign_metrics = {
            "avg_cpc": 2.00,  # Good CPC
            "avg_ctr": 0.035,  # Good CTR
            "conversion_rate": 0.04,  # Good conversion rate
            "cost_per_conversion": 50.00  # Good cost per conversion
        }
        
        result = ads_integration._calculate_overall_efficiency(campaign_metrics)
        
        assert isinstance(result, dict)
        assert "overall_score" in result
        assert "cpc_efficiency" in result
        assert "ctr_efficiency" in result
        assert "conversion_efficiency" in result
        assert "benchmarks" in result
        assert "current_metrics" in result
        
        # Should have high efficiency scores for good metrics
        assert result["overall_score"] > 80
        assert result["ctr_efficiency"] > 100  # Above benchmark

    def test_identify_waste_opportunities_high_cpc(self, ads_integration):
        """Test waste opportunity identification for high CPC."""
        campaign_metrics = {
            "avg_cpc": 5.00,  # High CPC
            "conversion_rate": 0.03,
            "monthly_spend": 10000
        }
        
        opportunities = ads_integration._identify_waste_opportunities(campaign_metrics, [])
        
        assert isinstance(opportunities, list)
        assert len(opportunities) > 0
        
        # Should identify high CPC opportunity
        high_cpc_opportunity = next((opp for opp in opportunities if opp["type"] == "high_cpc"), None)
        assert high_cpc_opportunity is not None
        assert high_cpc_opportunity["monthly_waste"] > 0
        assert high_cpc_opportunity["annual_waste"] > 0
        assert "recommendation" in high_cpc_opportunity

    def test_identify_waste_opportunities_low_conversion(self, ads_integration):
        """Test waste opportunity identification for low conversion rate."""
        campaign_metrics = {
            "avg_cpc": 2.00,
            "conversion_rate": 0.01,  # Low conversion rate
            "monthly_spend": 8000
        }
        
        opportunities = ads_integration._identify_waste_opportunities(campaign_metrics, [])
        
        # Should identify low conversion opportunity
        low_conversion_opportunity = next((opp for opp in opportunities if opp["type"] == "low_conversion_rate"), None)
        assert low_conversion_opportunity is not None
        assert low_conversion_opportunity["monthly_waste"] > 0

    def test_identify_waste_opportunities_poor_keywords(self, ads_integration):
        """Test waste opportunity identification for poor performing keywords."""
        campaign_metrics = {
            "avg_cpc": 2.00,
            "conversion_rate": 0.03,
            "monthly_spend": 5000
        }
        
        keyword_performance = [
            {
                "keyword": "expensive keyword",
                "cost": 500,  # High cost
                "conversion_rate": 0.005,  # Low conversion
                "clicks": 200,
                "impressions": 10000
            },
            {
                "keyword": "good keyword",
                "cost": 200,
                "conversion_rate": 0.04,  # Good conversion
                "clicks": 100,
                "impressions": 3000
            }
        ]
        
        opportunities = ads_integration._identify_waste_opportunities(campaign_metrics, keyword_performance)
        
        # Should identify poor keywords opportunity
        poor_keywords_opportunity = next((opp for opp in opportunities if opp["type"] == "poor_keywords"), None)
        assert poor_keywords_opportunity is not None
        assert poor_keywords_opportunity["monthly_waste"] == 500  # Cost of poor keyword

    def test_generate_optimization_recommendations(self, ads_integration):
        """Test optimization recommendations generation."""
        campaign_metrics = {
            "avg_cpc": 4.00,  # High CPC
            "avg_ctr": 0.02,  # Low CTR
            "conversion_rate": 0.015,  # Low conversion
            "monthly_spend": 10000
        }
        
        keyword_performance = [
            {"quality_score": 4},  # Low quality score
            {"quality_score": 8}   # Good quality score
        ]
        
        recommendations = ads_integration._generate_optimization_recommendations(campaign_metrics, keyword_performance)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Should include various types of recommendations
        recommendation_text = " ".join(recommendations).lower()
        assert "bidding" in recommendation_text or "cpc" in recommendation_text
        assert "ctr" in recommendation_text or "click-through" in recommendation_text
        assert "conversion" in recommendation_text or "landing page" in recommendation_text
        assert "quality score" in recommendation_text

    def test_calculate_potential_savings(self, ads_integration):
        """Test potential savings calculation."""
        campaign_metrics = {
            "avg_cpc": 4.00,  # Above benchmark
            "conversion_rate": 0.015,  # Below benchmark
            "monthly_spend": 10000
        }
        
        keyword_performance = [
            {
                "cost": 300,
                "conversion_rate": 0.005  # Poor conversion
            },
            {
                "cost": 200,
                "conversion_rate": 0.04  # Good conversion
            }
        ]
        
        savings = ads_integration._calculate_potential_savings(campaign_metrics, keyword_performance)
        
        assert isinstance(savings, dict)
        assert "monthly_savings" in savings
        assert "annual_savings" in savings
        assert "cpc_optimization_savings" in savings
        assert "conversion_optimization_savings" in savings
        assert "keyword_optimization_savings" in savings
        
        # Should have positive savings potential
        assert savings["monthly_savings"] > 0
        assert savings["annual_savings"] == savings["monthly_savings"] * 12

    @pytest.mark.asyncio
    async def test_analyze_ad_efficiency_complete(self, ads_integration):
        """Test complete ad efficiency analysis."""
        customer_id = "1234567890"
        domain = "example.com"
        
        # Mock the methods to return test data
        with patch.object(ads_integration, 'get_campaign_metrics') as mock_campaigns:
            mock_campaigns.return_value = {
                "avg_cpc": 3.50,
                "avg_ctr": 0.025,
                "conversion_rate": 0.02,
                "cost_per_conversion": 175,
                "monthly_spend": 8000
            }
            
            with patch.object(ads_integration, 'get_keyword_performance') as mock_keywords:
                mock_keywords.return_value = [
                    {"cost": 400, "conversion_rate": 0.005, "quality_score": 5},
                    {"cost": 300, "conversion_rate": 0.035, "quality_score": 8}
                ]
                
                result = await ads_integration.analyze_ad_efficiency(customer_id, domain)
                
                assert isinstance(result, dict)
                assert "overall_efficiency" in result
                assert "waste_opportunities" in result
                assert "optimization_recommendations" in result
                assert "potential_savings" in result
                
                # Check overall efficiency structure
                efficiency = result["overall_efficiency"]
                assert "overall_score" in efficiency
                assert isinstance(efficiency["overall_score"], (int, float))
                
                # Check waste opportunities
                opportunities = result["waste_opportunities"]
                assert isinstance(opportunities, list)
                
                # Check recommendations
                recommendations = result["optimization_recommendations"]
                assert isinstance(recommendations, list)
                
                # Check savings
                savings = result["potential_savings"]
                assert "monthly_savings" in savings
                assert "annual_savings" in savings

    def test_build_campaign_metrics_query(self, ads_integration):
        """Test Google Ads query building for campaign metrics."""
        domain = "example.com"
        
        query = ads_integration._build_campaign_metrics_query(domain)
        
        assert isinstance(query, str)
        assert "SELECT" in query
        assert "campaign.id" in query
        assert "metrics.cost_micros" in query
        assert "metrics.clicks" in query
        assert "metrics.conversions" in query
        assert "FROM campaign" in query
        assert "WHERE" in query
        assert domain in query

    def test_build_keyword_performance_query(self, ads_integration):
        """Test Google Ads query building for keyword performance."""
        domain = "example.com"
        
        query = ads_integration._build_keyword_performance_query(domain)
        
        assert isinstance(query, str)
        assert "SELECT" in query
        assert "ad_group_criterion.keyword.text" in query
        assert "metrics.cost_micros" in query
        assert "metrics.quality_score" in query
        assert "FROM keyword_view" in query
        assert "ORDER BY" in query
        assert "LIMIT" in query

    @pytest.mark.asyncio
    async def test_session_management(self, ads_integration):
        """Test HTTP session initialization and management."""
        # Test session initialization
        await ads_integration._init_session()
        
        assert ads_integration.session is not None
        assert not ads_integration.session.closed
        
        # Test session cleanup
        await ads_integration.close()
        
        assert ads_integration.session is None

    @pytest.mark.asyncio
    async def test_access_token_refresh(self, ads_integration):
        """Test OAuth2 access token refresh."""
        # Mock successful token refresh
        with patch.object(ads_integration, '_init_session'):
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                "access_token": "new_access_token",
                "expires_in": 3600
            }
            
            mock_session = AsyncMock()
            mock_session.post.return_value.__aenter__.return_value = mock_response
            ads_integration.session = mock_session
            
            token = await ads_integration._get_access_token()
            
            assert token == "new_access_token"
            assert ads_integration.access_token == "new_access_token"
            assert ads_integration.token_expires_at is not None

    @pytest.mark.asyncio
    async def test_access_token_refresh_failure(self, ads_integration):
        """Test OAuth2 access token refresh failure."""
        # Mock failed token refresh
        with patch.object(ads_integration, '_init_session'):
            mock_response = AsyncMock()
            mock_response.status = 400  # Bad request
            
            mock_session = AsyncMock()
            mock_session.post.return_value.__aenter__.return_value = mock_response
            ads_integration.session = mock_session
            
            token = await ads_integration._get_access_token()
            
            assert token is None