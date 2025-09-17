"""
Tests for ICP integration with the Discovery Engine and Financial Leak Detection.
"""

import unittest
from unittest.mock import patch, MagicMock
import asyncio
from datetime import datetime

from arco.engines.discovery_engine import DiscoveryEngine
from arco.models.icp import ICP, ICPType, ShopifyDTCPremiumICP
from arco.models.prospect import Prospect, Technology
from arco.models.financial_leak import FinancialLeakDetector

# Helper function to create a completed future
def create_future(result):
    """Create a completed future with the given result."""
    future = asyncio.Future()
    future.set_result(result)
    return future


class TestICPDiscoveryIntegration(unittest.TestCase):
    """Test cases for ICP integration with the Discovery Engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a discovery engine with ICP
        self.icp = ShopifyDTCPremiumICP()
        self.engine = DiscoveryEngine(icp=self.icp)
        
        # Create sample prospects for testing
        self.matching_prospect = Prospect(
            domain="beauty-store.com",
            company_name="Beauty Store",
            industry="Beauty",
            employee_count=25,
            revenue=1_500_000,
            country="United States"
        )
        self.matching_prospect.technologies = [
            Technology(name="shopify", category="ecommerce_platform"),
            Technology(name="klaviyo", category="email_marketing")
        ]
        
        self.non_matching_prospect = Prospect(
            domain="tech-company.com",
            company_name="Tech Company",
            industry="Technology",
            employee_count=100,
            revenue=10_000_000,
            country="Germany"
        )
        self.non_matching_prospect.technologies = [
            Technology(name="wordpress", category="cms"),
            Technology(name="mailchimp", category="email_marketing")
        ]
    
    def test_set_icp(self):
        """Test setting an ICP on the discovery engine."""
        # Test with ICP object
        engine = DiscoveryEngine()
        engine.set_icp(self.icp)
        self.assertEqual(engine.get_icp().name, "Shopify DTC Premium (Beauty/Skincare)")
        
        # Test with ICP name
        engine = DiscoveryEngine()
        engine.set_icp("Shopify DTC Premium (Beauty/Skincare)")
        self.assertIsNotNone(engine.get_icp())
        
        # Test with ICP type
        engine = DiscoveryEngine()
        engine.set_icp(ICPType.BEAUTY_SKINCARE)
        self.assertIsNotNone(engine.get_icp())
    
    def test_filter_prospects_by_icp(self):
        """Test filtering prospects by ICP criteria."""
        prospects = [self.matching_prospect, self.non_matching_prospect]
        
        filtered = self.engine._filter_prospects_by_icp(prospects)
        
        # Should only include the matching prospect
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].domain, "beauty-store.com")
    
    @patch.object(DiscoveryEngine, '_discover_async')
    def test_discover_with_icp(self, mock_discover_async):
        """Test discover method with ICP filtering."""
        # Setup mock to return both prospects
        mock_discover_async.return_value = create_future([self.matching_prospect, self.non_matching_prospect])
        
        # Patch the _filter_prospects_by_icp method to return only the matching prospect
        with patch.object(self.engine, '_filter_prospects_by_icp') as mock_filter:
            mock_filter.return_value = [self.matching_prospect]
            
            # Call discover with a query
            results = self.engine.discover("test query", limit=10)
            
            # Should filter out non-matching prospects
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].domain, "beauty-store.com")
    
    @patch.object(DiscoveryEngine, '_generate_search_queries_from_icp')
    @patch.object(DiscoveryEngine, '_discover_by_icp_async')
    def test_discover_by_icp(self, mock_discover_by_icp_async, mock_generate_queries):
        """Test discover_by_icp method."""
        # Setup mocks
        mock_generate_queries.return_value = ["test dork 1", "test dork 2"]
        mock_discover_by_icp_async.return_value = create_future([self.matching_prospect])
        
        # Call discover_by_icp
        results = self.engine.discover_by_icp(limit=5)
        
        # Should use the ICP search dorks and return matching prospects
        mock_generate_queries.assert_called_once()
        mock_discover_by_icp_async.assert_called_once()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].domain, "beauty-store.com")
    
    def test_generate_search_queries_from_icp(self):
        """Test generating search queries from ICP search_dorks."""
        # The ShopifyDTCPremiumICP has predefined search_dorks
        queries = self.engine._generate_search_queries_from_icp()
        
        # Should return the ICP's search dorks
        self.assertTrue(len(queries) > 0)
        self.assertTrue(any("skincare" in query for query in queries))
    
    def test_generate_icp_report(self):
        """Test generating an ICP report for prospects."""
        prospects = [self.matching_prospect]
        
        report = self.engine.generate_icp_report(prospects)
        
        # Check report structure
        self.assertIn("icp", report)
        self.assertIn("summary", report)
        self.assertIn("prospects", report)
        
        # Check ICP info
        self.assertEqual(report["icp"]["name"], "Shopify DTC Premium (Beauty/Skincare)")
        
        # Check summary stats
        self.assertEqual(report["summary"]["total_prospects"], 1)
        
        # Check prospect details
        self.assertEqual(len(report["prospects"]), 1)
        self.assertIn("match_score", report["prospects"][0])
        self.assertIn("tech_score", report["prospects"][0])
        self.assertIn("waste_detection", report["prospects"][0])
        self.assertIn("roi_calculation", report["prospects"][0])
    
    def test_detect_financial_leaks(self):
        """Test detecting financial leaks for a prospect."""
        # Add more technologies to the prospect to trigger leak detection
        self.matching_prospect.technologies.extend([
            Technology(name="mailchimp", category="email_marketing"),  # Redundant with klaviyo
            Technology(name="hotjar", category="analytics"),
            Technology(name="google_analytics", category="analytics")  # Redundant analytics
        ])
        
        # Detect financial leaks
        leak_results = self.engine.detect_financial_leaks(self.matching_prospect)
        
        # Check structure
        self.assertEqual(leak_results["domain"], self.matching_prospect.domain)
        self.assertEqual(leak_results["company_name"], self.matching_prospect.company_name)
        self.assertIn("detection_date", leak_results)
        self.assertIn("redundant_apps", leak_results)
        self.assertIn("performance_conversion", leak_results)
        self.assertIn("verified_savings", leak_results)
        self.assertIn("summary", leak_results)
        
        # Check redundant apps detection
        self.assertTrue(leak_results["redundant_apps"]["redundancies_detected"])
        self.assertTrue(len(leak_results["redundant_apps"]["patterns_matched"]) > 0)
        self.assertTrue(leak_results["redundant_apps"]["total_monthly_waste"] > 0)
        
        # Check summary
        summary = leak_results["summary"]
        self.assertTrue(summary["total_monthly_waste"] > 0)
        self.assertEqual(summary["total_annual_waste"], summary["total_monthly_waste"] * 12)
        self.assertTrue(summary["total_monthly_savings"] > 0)
        self.assertTrue(len(summary["priority_recommendations"]) > 0)
    
    def test_detect_financial_leaks_for_prospects(self):
        """Test detecting financial leaks for multiple prospects."""
        # Add technologies to both prospects to trigger leak detection
        self.matching_prospect.technologies.append(
            Technology(name="mailchimp", category="email_marketing")  # Redundant with klaviyo
        )
        self.non_matching_prospect.technologies.append(
            Technology(name="sendgrid", category="email_marketing")  # Redundant with mailchimp
        )
        
        prospects = [self.matching_prospect, self.non_matching_prospect]
        
        # Detect financial leaks
        results = self.engine.detect_financial_leaks_for_prospects(prospects)
        
        # Check structure
        self.assertIn("prospects", results)
        self.assertIn("summary", results)
        self.assertEqual(len(results["prospects"]), 2)
        
        # Check summary
        summary = results["summary"]
        self.assertEqual(summary["total_prospects"], 2)
        self.assertTrue(summary["total_monthly_waste"] > 0)
        self.assertAlmostEqual(summary["total_annual_waste"], summary["total_monthly_waste"] * 12, places=2)
        self.assertTrue(summary["total_monthly_savings"] > 0)
        self.assertTrue(summary["average_roi_percentage"] > 0)
        
        # Check individual prospect results
        for prospect_result in results["prospects"]:
            self.assertIn("domain", prospect_result)
            self.assertIn("company_name", prospect_result)
            self.assertIn("leak_results", prospect_result)


if __name__ == "__main__":
    unittest.main()