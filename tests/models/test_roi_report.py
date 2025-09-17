"""
Tests for the ROI Report Generation System.
"""

import unittest
from datetime import datetime
import os
import shutil
from pathlib import Path

from arco.models.roi_report import (
    ReportTemplate, ProjectedSavings, CompetitorBenchmark, ROIReportGenerator
)
from arco.models.prospect import Prospect, Technology
from arco.models.financial_leak import FinancialLeakDetector


class TestROIReportGeneration(unittest.TestCase):
    """Test cases for the ROI Report Generation System."""
    
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
            Technology(name="hotjar", category="analytics")  # Redundant
        ]
        
        # Create a report generator
        self.generator = ROIReportGenerator()
        
        # Create test output directory
        self.test_output_dir = "test_reports"
        os.makedirs(self.test_output_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove test output directory
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)
    
    def test_report_template(self):
        """Test the ReportTemplate class."""
        template = ReportTemplate(
            name="Test Template",
            description="Test description",
            sections=["Section 1", "Section 2"],
            placeholders={"KEY": "Value"}
        )
        
        # Test to_dict and from_dict
        template_dict = template.to_dict()
        reconstructed = ReportTemplate.from_dict(template_dict)
        
        self.assertEqual(reconstructed.name, template.name)
        self.assertEqual(reconstructed.sections, template.sections)
        self.assertEqual(reconstructed.placeholders, template.placeholders)
    
    def test_projected_savings(self):
        """Test the ProjectedSavings class."""
        savings = ProjectedSavings(
            name="Test Savings",
            description="Test description",
            baseline_monthly_waste=500.0,
            growth_factors={"month2": 0.1, "month3": 0.15},
            confidence_levels={"pilot": 0.6, "month1": 0.7}
        )
        
        # Test calculation
        prospect_data = {
            "employee_count": 25,
            "revenue": 1500000.0
        }
        
        result = savings.calculate(prospect_data)
        
        self.assertEqual(result["name"], "Test Savings")
        self.assertTrue("monthly_projections" in result)
        self.assertTrue("pilot" in result["monthly_projections"])
        self.assertTrue("month1" in result["monthly_projections"])
        self.assertTrue("month2" in result["monthly_projections"])
        self.assertTrue("quarterly_projections" in result)
        self.assertTrue("annual_projections" in result)
        self.assertTrue("three_year_projections" in result)
        self.assertTrue("roi_metrics" in result)
    
    def test_competitor_benchmark(self):
        """Test the CompetitorBenchmark class."""
        benchmark = CompetitorBenchmark(
            name="Test Benchmark",
            description="Test description",
            metrics={
                "performance": {"load_time": 2.5},
                "conversion": {"bounce_rate": 40.0}
            }
        )
        
        # Test comparison
        prospect_data = {
            "performance": {"load_time": 3.5},
            "conversion": {"bounce_rate": 45.0}
        }
        
        result = benchmark.compare(prospect_data)
        
        self.assertEqual(result["name"], "Test Benchmark")
        self.assertTrue("comparisons" in result)
        self.assertTrue("performance" in result["comparisons"])
        self.assertTrue("conversion" in result["comparisons"])
        self.assertTrue("summary" in result)
        self.assertEqual(result["summary"]["ahead_count"], 0)
        self.assertEqual(result["summary"]["behind_count"], 2)
        self.assertTrue(result["summary"]["average_gap_percentage"] > 0)
    
    def test_generate_roi_report(self):
        """Test the generate_roi_report method."""
        report = self.generator.generate_roi_report(self.prospect)
        
        # Check structure
        self.assertTrue("template" in report)
        self.assertTrue("prospect" in report)
        self.assertTrue("generation_date" in report)
        self.assertTrue("financial_leaks" in report)
        self.assertTrue("projected_savings" in report)
        self.assertTrue("benchmark_comparison" in report)
        self.assertTrue("content" in report)
        
        # Check content
        self.assertEqual(report["prospect"]["domain"], self.prospect.domain)
        self.assertEqual(report["prospect"]["company_name"], self.prospect.company_name)
        self.assertTrue(report["financial_leaks"]["total_monthly_waste"] > 0)
        self.assertTrue(report["projected_savings"]["pilot_savings"] > 0)
        self.assertTrue(len(report["content"]) > 0)
    
    def test_save_report_to_file(self):
        """Test the save_report_to_file method."""
        report = self.generator.generate_roi_report(self.prospect)
        
        # Save report to file
        filepath = self.generator.save_report_to_file(report, self.test_output_dir)
        
        # Check that file exists
        self.assertTrue(os.path.exists(filepath))
        
        # Check file content
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn(self.prospect.company_name, content)
            self.assertIn("Executive Summary", content)
    
    def test_generate_html_report(self):
        """Test the generate_html_report method."""
        report = self.generator.generate_roi_report(self.prospect)
        
        # Generate HTML report
        html_content = self.generator.generate_html_report(report)
        
        # Check HTML content
        self.assertIn("<!DOCTYPE html>", html_content)
        self.assertIn(self.prospect.company_name, html_content)
        self.assertIn("<h2>Executive Summary</h2>", html_content)
        self.assertIn("Priority Recommendations", html_content)
    
    def test_different_report_templates(self):
        """Test generating reports with different templates."""
        # Test 14-Day Revenue Recovery Pilot
        report1 = self.generator.generate_roi_report(self.prospect, "14-Day Revenue Recovery Pilot")
        self.assertEqual(report1["template"]["name"], "14-Day Revenue Recovery Pilot")
        
        # Test Quarterly ROI Projection
        report2 = self.generator.generate_roi_report(self.prospect, "Quarterly ROI Projection")
        self.assertEqual(report2["template"]["name"], "Quarterly ROI Projection")
        
        # Test 3-Year ROI Analysis
        report3 = self.generator.generate_roi_report(self.prospect, "3-Year ROI Analysis")
        self.assertEqual(report3["template"]["name"], "3-Year ROI Analysis")
    
    def test_integration_with_financial_leak_detector(self):
        """Test integration with the FinancialLeakDetector."""
        # Create a financial leak detector
        leak_detector = FinancialLeakDetector()
        
        # Detect financial leaks
        leak_results = leak_detector.detect_financial_leaks(self.prospect)
        
        # Generate report
        report = self.generator.generate_roi_report(self.prospect)
        
        # Check that financial leak results are included in the report
        self.assertAlmostEqual(
            report["financial_leaks"]["total_monthly_waste"],
            leak_results["summary"]["total_monthly_waste"],
            places=2
        )
        self.assertAlmostEqual(
            report["financial_leaks"]["total_annual_waste"],
            leak_results["summary"]["total_annual_waste"],
            places=2
        )


if __name__ == "__main__":
    unittest.main()