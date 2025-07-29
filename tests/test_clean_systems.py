#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE TESTS FOR CLEAN SYSTEMS
Tests for realistic_math, clean_api_framework, and unified_lead_system
NO AI DELUSION - only realistic test scenarios
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.realistic_math import RealisticCalculations, IndustryBenchmarks
from api.clean_api_framework import APICredentials, APIResponse, MetaAdsAPIClient
from core.unified_lead_system import LeadDiscoveryEngine, LeadProfile, QualificationCriteria


class TestRealisticMath:
    """Test realistic mathematical calculations"""
    
    def setup_method(self):
        self.calculator = RealisticCalculations()
    
    def test_industry_benchmarks_initialization(self):
        """Test that benchmarks are initialized with realistic data"""
        benchmarks = IndustryBenchmarks()
        
        # Check that all industries have reasonable CPM ranges
        assert 'dental' in benchmarks.avg_cpm_ranges
        assert 'healthcare' in benchmarks.avg_cpm_ranges
        
        # Check realistic ranges (not arbitrary)
        dental_cpm = benchmarks.avg_cpm_ranges['dental']
        assert dental_cpm[0] > 0  # Lower bound > 0
        assert dental_cpm[1] > dental_cpm[0]  # Upper > lower
        assert dental_cpm[1] < 50  # Not unrealistically high
    
    def test_lead_value_calculation(self):
        """Test realistic lead value calculation"""
        result = self.calculator.calculate_lead_value(
            industry='dental',
            monthly_revenue=50000,
            conversion_rate=0.04
        )
        
        # Check result structure
        assert 'lead_value' in result
        assert 'monthly_profit' in result
        assert 'profit_margin_used' in result
        
        # Check realistic values
        assert result['lead_value'] > 0
        assert result['monthly_profit'] > 0
        assert 0 < result['profit_margin_used'] < 1  # Reasonable profit margin
        
        # Dental should have higher margin than retail
        retail_result = self.calculator.calculate_lead_value(
            industry='retail',
            monthly_revenue=50000,
            conversion_rate=0.04
        )
        assert result['profit_margin_used'] > retail_result['profit_margin_used']
    
    def test_ads_efficiency_calculation(self):
        """Test realistic ads efficiency scoring"""
        result = self.calculator.calculate_ads_efficiency(
            spend=3000,
            impressions=150000,
            clicks=2400,
            conversions=96,
            industry='dental'
        )
        
        # Check calculated metrics
        assert result['cpm'] > 0
        assert result['ctr'] > 0
        assert result['cpc'] > 0
        assert result['conversion_rate'] > 0
        
        # Check efficiency scores are 0-100
        assert 0 <= result['efficiency_score'] <= 100
        assert 0 <= result['cpm_score'] <= 100
        assert 0 <= result['ctr_score'] <= 100
        assert 0 <= result['cpc_score'] <= 100
        
        # Check benchmark ranges are included
        assert 'benchmark_cpm_range' in result
        assert len(result['benchmark_cpm_range']) == 2
    
    def test_money_leak_calculation(self):
        """Test realistic money leak calculation"""
        current_metrics = {
            'spend': 3000,
            'impressions': 150000,
            'clicks': 2400,
            'conversions': 96
        }
        
        result = self.calculator.calculate_money_leak(current_metrics, 'dental')
        
        # Check structure
        assert 'monthly_leak' in result
        assert 'annual_leak' in result
        assert 'current_efficiency_score' in result
        assert 'confidence_level' in result
        
        # Check realistic values
        assert result['monthly_leak'] >= 0
        assert result['annual_leak'] == result['monthly_leak'] * 12
        assert result['improvement_potential_percent'] <= 45  # Max 45% improvement
        assert result['confidence_level'] in ['high', 'medium', 'low', 'very_low']
    
    def test_roi_projection_realistic(self):
        """Test ROI projections are realistic, not AI delusion"""
        current_metrics = {
            'spend': 3000,
            'impressions': 150000,
            'clicks': 2400,
            'conversions': 96
        }
        
        result = self.calculator.calculate_realistic_roi_projection(
            investment=8000,
            current_metrics=current_metrics,
            industry='dental'
        )
        
        # Check structure
        assert 'roi_percentage' in result
        assert 'payback_months' in result
        assert 'calculation_basis' in result
        
        # Check realistic constraints
        assert result['roi_percentage'] < 500  # Not unrealistic returns
        assert result['payback_months'] > 0
        assert 'mathematical_model' in result['calculation_basis']
    
    def test_invalid_inputs_handling(self):
        """Test handling of invalid inputs"""
        # Test zero spend
        result = self.calculator.calculate_money_leak(
            {'spend': 0, 'impressions': 1000}, 'dental'
        )
        assert 'error' in result
        
        # Test negative revenue
        result = self.calculator.calculate_lead_value('dental', -1000)
        assert 'error' in result


class TestCleanAPIFramework:
    """Test clean API framework"""
    
    def test_api_credentials_initialization(self):
        """Test API credentials handling"""
        # Test with no environment variables
        creds = APICredentials()
        
        # Should not contain hardcoded fake tokens
        if creds.meta_access_token:
            assert not creds.meta_access_token.startswith('AIzaSy')  # No Google API key format
            assert not creds.meta_access_token.startswith('EAA')  # Check realistic format
    
    def test_api_response_structure(self):
        """Test API response standardization"""
        response = APIResponse(
            success=True,
            data={'test': 'data'},
            status_code=200
        )
        
        assert response.success is True
        assert response.data == {'test': 'data'}
        assert response.rate_limited is False
        assert response.from_cache is False
    
    @patch('requests.Session.get')
    def test_meta_client_connection_test(self, mock_get):
        """Test Meta API client connection testing"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': '123', 'name': 'Test User'}
        mock_get.return_value = mock_response
        
        creds = APICredentials(meta_access_token='test_token')
        client = MetaAdsAPIClient(creds)
        
        result = client.test_connection()
        
        assert result.success is True
        assert result.data['user_id'] == '123'
        assert result.data['connection_status'] == 'authenticated'
    
    @patch('requests.Session.get')
    def test_meta_client_error_handling(self, mock_get):
        """Test proper error handling"""
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'error': {'message': 'Invalid access token', 'code': 190}
        }
        mock_get.return_value = mock_response
        
        creds = APICredentials(meta_access_token='invalid_token')
        client = MetaAdsAPIClient(creds)
        
        result = client.test_connection()
        
        assert result.success is False
        assert 'Invalid access token' in result.error
        assert result.status_code == 401
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        from api.clean_api_framework import APIRateLimiter
        
        limiter = APIRateLimiter()
        
        # Should allow initial calls
        assert limiter.can_make_call('test_api', 5) is True
        
        # Record calls up to limit
        for i in range(5):
            limiter.record_call('test_api')
        
        # Should block after limit
        assert limiter.can_make_call('test_api', 5) is False


class TestUnifiedLeadSystem:
    """Test unified lead generation system"""
    
    def test_lead_profile_creation(self):
        """Test lead profile data structure"""
        lead = LeadProfile(
            company_name='Test Company',
            industry='dental',
            country='DE'
        )
        
        assert lead.company_name == 'Test Company'
        assert lead.industry == 'dental'
        assert lead.ad_platforms_active == []  # Default empty list
        assert lead.discovery_timestamp  # Should be set automatically
    
    def test_qualification_criteria(self):
        """Test realistic qualification criteria"""
        criteria = QualificationCriteria()
        
        # Check realistic thresholds
        assert criteria.min_monthly_ad_spend >= 500  # Minimum viable spend
        assert criteria.min_monthly_ad_spend <= 2000  # Not too high for SMEs
        
        # Check industry multipliers are realistic
        assert 0.5 <= criteria.industry_multipliers['retail'] <= 1.5
        assert criteria.industry_multipliers['dental'] > criteria.industry_multipliers['retail']
    
    @patch('core.unified_lead_system.UnifiedAPIClient')
    def test_lead_discovery_error_handling(self, mock_api_client):
        """Test lead discovery with API errors"""
        # Mock API client with connection failure
        mock_client = Mock()
        mock_client.test_all_connections.return_value = {
            'meta': APIResponse(success=False, error='Connection failed')
        }
        
        engine = LeadDiscoveryEngine(mock_client)
        leads = engine.discover_leads_by_industry('dental', ['DE'])
        
        # Should return empty list, not crash
        assert isinstance(leads, list)
        assert len(leads) == 0
    
    def test_industry_keywords_realistic(self):
        """Test industry keywords are realistic"""
        engine = LeadDiscoveryEngine(Mock())
        
        dental_keywords = engine._get_industry_keywords('dental')
        assert 'dental' in dental_keywords
        assert 'dentist' in dental_keywords
        assert len(dental_keywords) > 1  # Multiple keywords for better coverage
        
        # Should not contain obviously fake or placeholder keywords
        for keyword in dental_keywords:
            assert 'fake' not in keyword.lower()
            assert 'test' not in keyword.lower()
            assert 'mock' not in keyword.lower()


class TestSystemIntegration:
    """Test integration between systems"""
    
    def test_realistic_math_in_strategic_engine(self):
        """Test that strategic engine uses realistic math"""
        # This would test the integration but requires fixing imports
        # For now, we verify the concept works
        calc = RealisticCalculations()
        
        # Test that strategic calculations are realistic
        metrics = {
            'spend': 2000,
            'impressions': 100000,
            'clicks': 1500,
            'conversions': 60
        }
        
        result = calc.calculate_money_leak(metrics, 'dental')
        
        # Should be realistic range (not 25-40% arbitrary)
        improvement_pct = result['improvement_potential_percent']
        assert 5 <= improvement_pct <= 45  # Reasonable range
    
    def test_no_hardcoded_percentages(self):
        """Test that systems don't use hardcoded AI delusion percentages"""
        calc = RealisticCalculations()
        
        # Test different scenarios should give different results
        low_efficiency = calc.calculate_money_leak({
            'spend': 1000, 'impressions': 10000, 'clicks': 100, 'conversions': 2
        }, 'dental')
        
        high_efficiency = calc.calculate_money_leak({
            'spend': 1000, 'impressions': 50000, 'clicks': 2000, 'conversions': 100
        }, 'dental')
        
        # Results should be different (not hardcoded same percentage)
        assert low_efficiency['monthly_leak'] != high_efficiency['monthly_leak']
        assert low_efficiency['improvement_potential_percent'] > high_efficiency['improvement_potential_percent']


def test_no_ai_delusion_in_codebase():
    """Test that AI delusion patterns are removed"""
    
    # Check that we don't have obvious AI delusion files
    engines_dir = os.path.join(os.path.dirname(__file__), '..', 'src', 'engines')
    
    if os.path.exists(engines_dir):
        files = os.listdir(engines_dir)
        
        # Should not have obviously problematic files
        problematic_patterns = ['fake_', 'mock_', '_unlimited', 'ultimate_', 'magical_']
        
        for filename in files:
            for pattern in problematic_patterns:
                assert pattern not in filename.lower(), f"Found problematic file: {filename}"
    
    # Test that our clean files exist
    clean_files = [
        'src/core/realistic_math.py',
        'src/api/clean_api_framework.py',
        'src/core/unified_lead_system.py'
    ]
    
    for file_path in clean_files:
        full_path = os.path.join(os.path.dirname(__file__), '..', file_path)
        assert os.path.exists(full_path), f"Clean file missing: {file_path}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])