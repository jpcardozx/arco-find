"""
Tests for the Financial Leak Detection System.
"""

import unittest
from datetime import datetime
from arco.models.financial_leak import (
    AppRedundancyPattern, PerformanceConversionAnalysis, 
    VerifiedSavings, FinancialLeakDetector
)
from arco.models.prospect import Prospect, Technology


class TestFinancialLeakDetection(unittest.TestCase):
    """Test cases for the Financial Leak Detection System."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a sample prospect for testing
        self.prospect = Prospect(
            domain="example-store.com",
            company_name="Example Store",
            website="https://example-store.com",
            description="E-commerce store selling premium products",
            industry="E-commerce",
            employee_count=25,
            revenue=1500000.0,
            country="United States",
            city="New York",
            discovery_date=datetime.now(),
            validation_score=85.0,
            leak_potential=0.75
        )
        
        # Add technologies to the prospect with redundancies
        self.prospect.technologies = [
            Technology(name="shopify", category="ecommerce_platform", version="2.0"),
            Technology(name="klaviyo", category="email_marketing"),
            Technology(name="mailchimp", category="email_marketing"),  # Redundant
            Technology(name="recharge", category="subscriptions"),
            Technology(name="yotpo", category="reviews"),
            Technology(name="okendo", category="reviews"),  # Redundant
            Technology(name="google_analytics", category="analytics"),
            Technology(name="hotjar", category="analytics"),  # Redundant
            Technology(name="segment", category="analytics")  # Redundant
        ]
        
        # Create a detector
        self.detector = FinancialLeakDetector()
    
    def test_app_redundancy_pattern(self):
        """Test the AppRedundancyPattern class."""
        pattern = AppRedundancyPattern(
            name="Multiple Email Tools",
            description="Using multiple email marketing tools",
            categories=["email_marketing"],
            estimated_monthly_waste=250.0,
            priority=4
        )
        
        # Test detection
        result = pattern.detect(self.prospect.technologies)
        
        self.assertTrue(result["detected"])
        self.assertEqual(result["redundant_categories"], ["email_marketing"])
        self.assertEqual(len(result["redundant_tools"]["email_marketing"]), 2)
        self.assertEqual(result["estimated_waste"], 250.0)
        
        # Test to_dict and from_dict
        pattern_dict = pattern.to_dict()
        reconstructed = AppRedundancyPattern.from_dict(pattern_dict)
        
        self.assertEqual(reconstructed.name, pattern.name)
        self.assertEqual(reconstructed.categories, pattern.categories)
        self.assertEqual(reconstructed.estimated_monthly_waste, pattern.estimated_monthly_waste)
    
    def test_performance_conversion_analysis(self):
        """Test the PerformanceConversionAnalysis class."""
        analysis = PerformanceConversionAnalysis(
            name="Page Speed Analysis",
            description="Analysis of page load speed impact on conversion",
            performance_metrics={"load_time": "Time to load page"},
            conversion_metrics={"bounce_rate": "Bounce rate percentage"},
            benchmark_data={
                "performance": {"load_time": 2.5},
                "conversion": {"bounce_rate": 40.0}
            },
            estimated_monthly_waste=500.0
        )
        
        # Test analysis with issues
        prospect_data = {
            "performance": {"load_time": 4.2},
            "conversion": {"bounce_rate": 55.0}
        }
        
        result = analysis.analyze(prospect_data)
        
        self.assertTrue(result["issues_detected"])
        self.assertTrue(len(result["performance_issues"]) > 0)
        self.assertTrue(len(result["conversion_issues"]) > 0)
        self.assertTrue(len(result["recommendations"]) > 0)
        self.assertTrue(result["estimated_waste"] > 0)
        
        # Test analysis without issues
        good_data = {
            "performance": {"load_time": 2.0},
            "conversion": {"bounce_rate": 35.0}
        }
        
        good_result = analysis.analyze(good_data)
        self.assertFalse(good_result["issues_detected"])
    
    def test_verified_savings(self):
        """Test the VerifiedSavings class."""
        savings = VerifiedSavings(
            name="App Consolidation",
            description="Savings from consolidating apps",
            savings_type="cost_reduction",
            monthly_amount=300.0,
            verification_method="Direct cost comparison",
            verification_data={"assumptions": ["Test assumption"]},
            confidence_level=0.9
        )
        
        # Test calculation
        prospect_data = {
            "employee_count": 25,
            "revenue": 1500000.0
        }
        
        result = savings.calculate(prospect_data)
        
        self.assertEqual(result["name"], "App Consolidation")
        self.assertEqual(result["savings_type"], "cost_reduction")
        self.assertTrue(result["monthly_savings"] > 0)
        self.assertEqual(result["annual_savings"], result["monthly_savings"] * 12)
        self.assertEqual(result["three_year_savings"], result["annual_savings"] * 3)
        self.assertEqual(result["confidence_level"], 0.9)
        self.assertTrue("verification_details" in result)
    
    def test_detect_redundant_apps(self):
        """Test the detect_redundant_apps method."""
        result = self.detector.detect_redundant_apps(self.prospect.technologies)
        
        self.assertTrue(result["redundancies_detected"])
        self.assertTrue(len(result["patterns_matched"]) > 0)
        self.assertTrue(result["total_monthly_waste"] > 0)
        self.assertEqual(result["total_annual_waste"], result["total_monthly_waste"] * 12)
        self.assertTrue(len(result["recommendations"]) > 0)
        
        # Test with no redundancies
        clean_technologies = [
            Technology(name="shopify", category="ecommerce_platform"),
            Technology(name="klaviyo", category="email_marketing"),
            Technology(name="recharge", category="subscriptions")
        ]
        
        clean_result = self.detector.detect_redundant_apps(clean_technologies)
        self.assertFalse(clean_result["redundancies_detected"])
        self.assertEqual(clean_result["total_monthly_waste"], 0)
    
    def test_analyze_performance_conversion(self):
        """Test the analyze_performance_conversion method."""
        # Create prospect data with performance issues
        prospect_data = {
            "domain": "example-store.com",
            "company_name": "Example Store",
            "employee_count": 25,
            "revenue": 1500000.0,
            "performance": {
                "load_time": 4.5,
                "ttfb": 1.5,
                "fcp": 3.0,
                "lcp": 4.2,
                "checkout_steps": 5,
                "checkout_load_time": 3.0
            },
            "conversion": {
                "bounce_rate": 60.0,
                "conversion_rate": 1.8,
                "cart_abandonment": 85.0,
                "checkout_completion": 45.0
            }
        }
        
        result = self.detector.analyze_performance_conversion(prospect_data)
        
        self.assertTrue(result["issues_detected"])
        self.assertTrue(len(result["analyses"]) > 0)
        self.assertTrue(result["total_monthly_waste"] > 0)
        self.assertEqual(result["total_annual_waste"], result["total_monthly_waste"] * 12)
        self.assertTrue(len(result["recommendations"]) > 0)
    
    def test_calculate_verified_savings(self):
        """Test the calculate_verified_savings method."""
        prospect_data = {
            "domain": "example-store.com",
            "company_name": "Example Store",
            "employee_count": 25,
            "revenue": 1500000.0
        }
        
        result = self.detector.calculate_verified_savings(prospect_data)
        
        self.assertTrue(len(result["calculations"]) > 0)
        self.assertTrue(result["total_monthly_savings"] > 0)
        self.assertEqual(result["total_annual_savings"], result["total_monthly_savings"] * 12)
        self.assertEqual(result["total_three_year_savings"], result["total_annual_savings"] * 3)
        self.assertTrue(result["roi_percentage"] > 0)
    
    def test_detect_financial_leaks(self):
        """Test the detect_financial_leaks method."""
        result = self.detector.detect_financial_leaks(self.prospect)
        
        # Check structure
        self.assertEqual(result["domain"], self.prospect.domain)
        self.assertEqual(result["company_name"], self.prospect.company_name)
        self.assertIn("detection_date", result)
        self.assertIn("redundant_apps", result)
        self.assertIn("performance_conversion", result)
        self.assertIn("verified_savings", result)
        self.assertIn("summary", result)
        
        # Check summary
        summary = result["summary"]
        self.assertTrue(summary["total_monthly_waste"] > 0)
        self.assertAlmostEqual(summary["total_annual_waste"], summary["total_monthly_waste"] * 12, places=2)
        self.assertTrue(summary["total_monthly_savings"] > 0)
        self.assertAlmostEqual(summary["total_annual_savings"], summary["total_monthly_savings"] * 12, places=2)
        self.assertTrue(summary["total_three_year_savings"] > 0)
        self.assertTrue(summary["roi_percentage"] > 0)
        self.assertTrue(len(summary["priority_recommendations"]) > 0)


if __name__ == "__main__":
    unittest.main()