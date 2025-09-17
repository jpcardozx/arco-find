"""
Tests for the lead qualification engine.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from arco.engines.lead_qualification_engine import (
    LeadQualificationEngine,
    QualificationCriteria,
    LeadScore
)
from arco.models.prospect import Prospect, Contact, Technology
from arco.models.icp import ShopifyDTCPremiumICP


class TestLeadQualificationEngine(unittest.TestCase):
    """Test the lead qualification engine."""
    
    def setUp(self):
        """Set up the test."""
        self.criteria = QualificationCriteria(
            min_employee_count=10,
            min_revenue=500000,
            max_revenue=10000000,
            min_icp_score=60.0,
            min_roi_percentage=15.0,
            min_annual_savings=5000.0
        )
        self.engine = LeadQualificationEngine(self.criteria)
        self.icp = ShopifyDTCPremiumICP()
        
        # Create a test prospect
        self.prospect = Prospect(
            domain="example.com",
            company_name="Example Inc.",
            website="https://example.com",
            description="E-commerce company",
            industry="E-commerce",
            employee_count=50,
            revenue=2000000,
            country="United States",
            city="San Francisco"
        )
        
        # Add contacts
        self.prospect.contacts.append(Contact(
            name="John Doe",
            email="john@example.com",
            phone="123-456-7890",
            position="CEO"
        ))
        
        # Add technologies
        self.prospect.technologies.extend([
            Technology(name="Shopify", category="ecommerce"),
            Technology(name="Google Analytics", category="analytics"),
            Technology(name="Klaviyo", category="email_marketing")
        ])
    
    def test_qualify_lead_basic(self):
        """Test basic lead qualification."""
        is_qualified, lead_score = self.engine.qualify_lead(self.prospect, self.icp)
        
        # Check that we get a result
        self.assertIsInstance(is_qualified, bool)
        self.assertIsInstance(lead_score, LeadScore)
        
        # Check score structure
        self.assertGreaterEqual(lead_score.total_score, 0)
        self.assertLessEqual(lead_score.total_score, 100)
        self.assertIn(lead_score.qualification_level, ["A", "B", "C", "D"])
        self.assertIn(lead_score.priority_level, [1, 2, 3, 4, 5])
        
        # Check that reasons are provided
        self.assertIsInstance(lead_score.qualification_reasons, list)
        self.assertIsInstance(lead_score.disqualification_reasons, list)
    
    def test_qualify_lead_with_analysis_results(self):
        """Test lead qualification with financial analysis results."""
        analysis_results = {
            "leak_results": {
                "summary": {
                    "roi_percentage": 25.0,
                    "total_annual_savings": 10000.0,
                    "total_monthly_waste": 500.0
                }
            }
        }
        
        is_qualified, lead_score = self.engine.qualify_lead(
            self.prospect, self.icp, analysis_results
        )
        
        # Should have higher financial score with good analysis results
        self.assertGreater(lead_score.financial_score, 50)
        
        # Should be qualified with good financial metrics
        self.assertTrue(is_qualified or lead_score.qualification_level in ["A", "B"])
    
    def test_disqualification_criteria(self):
        """Test that disqualification criteria work."""
        # Create a prospect that should be disqualified
        bad_prospect = Prospect(
            domain="small-company.com",
            company_name="Small Company",
            employee_count=5,  # Below minimum
            revenue=100000,    # Below minimum
            country="Unsupported Country"  # Not in target geography
        )
        
        is_qualified, lead_score = self.engine.qualify_lead(bad_prospect, self.icp)
        
        # Should be disqualified
        self.assertFalse(is_qualified)
        self.assertEqual(lead_score.qualification_level, "D")
        self.assertGreater(len(lead_score.disqualification_reasons), 0)
    
    def test_contact_scoring(self):
        """Test contact quality scoring."""
        # Test with good contact
        good_prospect = Prospect(domain="good-contact.com")
        good_prospect.contacts.append(Contact(
            name="Jane Smith",
            email="jane@good-contact.com",
            phone="555-123-4567",
            position="CEO"
        ))
        
        _, good_score = self.engine.qualify_lead(good_prospect, self.icp)
        
        # Test with poor contact
        poor_prospect = Prospect(domain="poor-contact.com")
        poor_prospect.contacts.append(Contact(
            name="Unknown",
            email="",
            phone="",
            position=""
        ))
        
        _, poor_score = self.engine.qualify_lead(poor_prospect, self.icp)
        
        # Good contact should score higher
        self.assertGreater(good_score.contact_score, poor_score.contact_score)
    
    def test_technology_scoring(self):
        """Test technology stack scoring."""
        # Test with good technology stack
        tech_prospect = Prospect(domain="tech-company.com")
        tech_prospect.technologies.extend([
            Technology(name="Shopify", category="ecommerce"),
            Technology(name="HubSpot", category="crm"),
            Technology(name="Google Analytics", category="analytics"),
            Technology(name="Stripe", category="payments"),
            Technology(name="Klaviyo", category="email_marketing")
        ])
        
        _, tech_score = self.engine.qualify_lead(tech_prospect, self.icp)
        
        # Test with no technology stack
        no_tech_prospect = Prospect(domain="no-tech.com")
        
        _, no_tech_score = self.engine.qualify_lead(no_tech_prospect, self.icp)
        
        # Technology-rich prospect should score higher
        self.assertGreater(tech_score.technology_score, no_tech_score.technology_score)
    
    def test_batch_qualification(self):
        """Test batch qualification of multiple leads."""
        prospects = [self.prospect]
        
        # Create additional test prospects
        for i in range(3):
            prospect = Prospect(
                domain=f"test{i}.com",
                company_name=f"Test Company {i}",
                employee_count=25 + i * 10,
                revenue=1000000 + i * 500000
            )
            prospects.append(prospect)
        
        results = self.engine.batch_qualify_leads(prospects, self.icp)
        
        # Check that we get results for all prospects
        self.assertEqual(len(results), len(prospects))
        
        # Check that each result has the expected structure
        for domain, (is_qualified, lead_score) in results.items():
            self.assertIsInstance(is_qualified, bool)
            self.assertIsInstance(lead_score, LeadScore)
    
    def test_qualification_summary(self):
        """Test qualification summary generation."""
        prospects = [self.prospect]
        
        # Create additional test prospects with varying quality
        for i in range(5):
            prospect = Prospect(
                domain=f"test{i}.com",
                company_name=f"Test Company {i}",
                employee_count=10 + i * 20,
                revenue=500000 + i * 1000000
            )
            prospects.append(prospect)
        
        results = self.engine.batch_qualify_leads(prospects, self.icp)
        summary = self.engine.get_qualification_summary(results)
        
        # Check summary structure
        self.assertIn("total_leads", summary)
        self.assertIn("qualified_leads", summary)
        self.assertIn("qualification_rate", summary)
        self.assertIn("level_distribution", summary)
        self.assertIn("priority_distribution", summary)
        self.assertIn("average_scores", summary)
        
        # Check that counts make sense
        self.assertEqual(summary["total_leads"], len(prospects))
        self.assertLessEqual(summary["qualified_leads"], summary["total_leads"])
        
        # Check level distribution
        level_total = sum(summary["level_distribution"].values())
        self.assertEqual(level_total, summary["total_leads"])
        
        # Check priority distribution
        priority_total = sum(summary["priority_distribution"].values())
        self.assertEqual(priority_total, summary["total_leads"])


if __name__ == "__main__":
    unittest.main()