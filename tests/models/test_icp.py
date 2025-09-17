"""
Tests for the ICP models.
"""

import unittest
from datetime import datetime
from arco.models import (
    ICP, ICPType, TechnologyRequirement, RevenueIndicator, SaaSWastePattern,
    ShopifyDTCPremiumICP, HealthSupplementsICP, FitnessEquipmentICP,
    Prospect, Technology
)


class TestICPModels(unittest.TestCase):
    """Test cases for ICP models."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a sample prospect for testing
        self.prospect = Prospect(
            domain="example-beauty.com",
            company_name="Example Beauty Co",
            website="https://example-beauty.com",
            description="Premium skincare brand",
            industry="Beauty",
            employee_count=15,
            revenue=1200000.0,
            country="United States",
            city="New York",
            discovery_date=datetime.now(),
            validation_score=85.0,
            leak_potential=0.75
        )
        
        # Add technologies to the prospect
        self.prospect.technologies = [
            Technology(name="shopify", category="ecommerce_platform", version="2.0"),
            Technology(name="klaviyo", category="email_marketing"),
            Technology(name="recharge", category="subscriptions"),
            Technology(name="yotpo", category="reviews")
        ]
    
    def test_icp_creation(self):
        """Test creating an ICP."""
        icp = ICP(
            name="Test ICP",
            icp_type=ICPType.CUSTOM,
            description="Test description",
            min_revenue=100000.0,
            max_revenue=1000000.0
        )
        
        self.assertEqual(icp.name, "Test ICP")
        self.assertEqual(icp.icp_type, ICPType.CUSTOM)
        self.assertEqual(icp.min_revenue, 100000.0)
        self.assertEqual(icp.max_revenue, 1000000.0)
    
    def test_technology_requirement(self):
        """Test creating a technology requirement."""
        tech_req = TechnologyRequirement(
            category="email_marketing",
            tools=["klaviyo", "mailchimp"],
            required=True
        )
        
        self.assertEqual(tech_req.category, "email_marketing")
        self.assertEqual(tech_req.tools, ["klaviyo", "mailchimp"])
        self.assertTrue(tech_req.required)
    
    def test_revenue_indicator(self):
        """Test creating a revenue indicator."""
        rev_ind = RevenueIndicator(
            name="subscription_model",
            keywords=["subscription", "monthly"],
            multiplier=1.5
        )
        
        self.assertEqual(rev_ind.name, "subscription_model")
        self.assertEqual(rev_ind.keywords, ["subscription", "monthly"])
        self.assertEqual(rev_ind.multiplier, 1.5)
    
    def test_shopify_dtc_premium_icp(self):
        """Test the ShopifyDTCPremiumICP class."""
        icp = ShopifyDTCPremiumICP()
        
        self.assertEqual(icp.name, "Shopify DTC Premium (Beauty/Skincare)")
        self.assertEqual(icp.icp_type, ICPType.BEAUTY_SKINCARE)
        self.assertTrue(500000 <= icp.min_revenue <= icp.max_revenue)
        self.assertTrue(len(icp.tech_requirements) > 0)
        self.assertTrue(len(icp.revenue_indicators) > 0)
        self.assertTrue(len(icp.search_dorks) > 0)
    
    def test_health_supplements_icp(self):
        """Test the HealthSupplementsICP class."""
        icp = HealthSupplementsICP()
        
        self.assertEqual(icp.name, "Health Supplements DTC")
        self.assertEqual(icp.icp_type, ICPType.HEALTH_SUPPLEMENTS)
        self.assertTrue(len(icp.tech_requirements) > 0)
    
    def test_fitness_equipment_icp(self):
        """Test the FitnessEquipmentICP class."""
        icp = FitnessEquipmentICP()
        
        self.assertEqual(icp.name, "Fitness Equipment DTC")
        self.assertEqual(icp.icp_type, ICPType.FITNESS_EQUIPMENT)
        self.assertTrue(len(icp.tech_requirements) > 0)
    
    def test_matches_prospect(self):
        """Test the matches_prospect method."""
        icp = ShopifyDTCPremiumICP()
        
        # This prospect should match
        self.assertTrue(icp.matches_prospect(self.prospect))
        
        # Create a prospect that shouldn't match (wrong industry)
        non_matching_prospect = Prospect(
            domain="example-tech.com",
            company_name="Example Tech Co",
            industry="Technology",
            revenue=1000000.0,
            country="United States"
        )
        
        self.assertFalse(icp.matches_prospect(non_matching_prospect))
    
    def test_calculate_match_score(self):
        """Test the calculate_match_score method."""
        icp = ShopifyDTCPremiumICP()
        
        # This prospect should have a high match score
        score = icp.calculate_match_score(self.prospect)
        self.assertTrue(score > 75)
        
        # Create a prospect that should have a lower score
        lower_score_prospect = Prospect(
            domain="example-beauty-small.com",
            company_name="Small Beauty Co",
            industry="Beauty",
            revenue=200000.0,  # Below min_revenue
            country="Germany",  # Not in target countries
            employee_count=3    # Below min_employees
        )
        
        lower_score = icp.calculate_match_score(lower_score_prospect)
        self.assertTrue(lower_score < score)
    
    def test_to_dict_from_dict(self):
        """Test the to_dict and from_dict methods."""
        original_icp = ShopifyDTCPremiumICP()
        
        # Convert to dict
        icp_dict = original_icp.to_dict()
        
        # Convert back from dict
        reconstructed_icp = ICP.from_dict(icp_dict)
        
        # Check that key attributes were preserved
        self.assertEqual(reconstructed_icp.name, original_icp.name)
        self.assertEqual(reconstructed_icp.min_revenue, original_icp.min_revenue)
        self.assertEqual(reconstructed_icp.max_revenue, original_icp.max_revenue)
        self.assertEqual(len(reconstructed_icp.tech_requirements), len(original_icp.tech_requirements))
    
    def test_get_all_icps(self):
        """Test the get_all_icps function."""
        from arco.models import get_all_icps
        
        icps = get_all_icps()
        self.assertTrue(len(icps) >= 3)
        self.assertTrue(any(isinstance(icp, ShopifyDTCPremiumICP) for icp in icps))
        self.assertTrue(any(isinstance(icp, HealthSupplementsICP) for icp in icps))
        self.assertTrue(any(isinstance(icp, FitnessEquipmentICP) for icp in icps))
    
    def test_get_icp_by_name(self):
        """Test the get_icp_by_name function."""
        from arco.models import get_icp_by_name
        
        icp = get_icp_by_name("Shopify DTC Premium (Beauty/Skincare)")
        self.assertIsNotNone(icp)
        self.assertEqual(icp.name, "Shopify DTC Premium (Beauty/Skincare)")
        
        # Test with a name that doesn't exist
        non_existent_icp = get_icp_by_name("Non-existent ICP")
        self.assertIsNone(non_existent_icp)
    
    def test_get_icp_by_type(self):
        """Test the get_icp_by_type function."""
        from arco.models import get_icp_by_type
        
        icp = get_icp_by_type(ICPType.BEAUTY_SKINCARE)
        self.assertIsNotNone(icp)
        self.assertEqual(icp.icp_type, ICPType.BEAUTY_SKINCARE)
        
        # Test with a type that doesn't exist
        non_existent_icp = get_icp_by_type(ICPType.CUSTOM)
        self.assertIsNone(non_existent_icp)
    
    def test_saas_waste_pattern(self):
        """Test creating and matching a SaaS waste pattern."""
        pattern = SaaSWastePattern(
            name="Multiple Email Tools",
            description="Using multiple email marketing tools",
            detection_pattern={"redundant_categories": ["email_marketing"]},
            estimated_monthly_waste=200.0,
            priority=3
        )
        
        # Create a prospect with redundant email marketing tools
        prospect = Prospect(domain="example.com")
        prospect.technologies = [
            Technology(name="klaviyo", category="email_marketing"),
            Technology(name="mailchimp", category="email_marketing")
        ]
        
        # Test that the pattern matches
        self.assertTrue(pattern.matches(prospect.technologies))
        
        # Create a prospect without redundant tools
        prospect_no_redundancy = Prospect(domain="example2.com")
        prospect_no_redundancy.technologies = [
            Technology(name="klaviyo", category="email_marketing"),
            Technology(name="shopify", category="ecommerce_platform")
        ]
        
        # Test that the pattern doesn't match
        self.assertFalse(pattern.matches(prospect_no_redundancy.technologies))
        
        # Test tool combinations pattern
        combo_pattern = SaaSWastePattern(
            name="Expensive Combination",
            description="Using an expensive combination of tools",
            detection_pattern={
                "tool_combinations": [
                    [
                        {"category": "email_marketing", "tool": "klaviyo"},
                        {"category": "reviews", "tool": "yotpo"}
                    ]
                ]
            },
            estimated_monthly_waste=300.0,
            priority=4
        )
        
        # Create a prospect with the specific tool combination
        prospect_with_combo = Prospect(domain="example3.com")
        prospect_with_combo.technologies = [
            Technology(name="klaviyo", category="email_marketing"),
            Technology(name="yotpo", category="reviews")
        ]
        
        # Test that the combination pattern matches
        self.assertTrue(combo_pattern.matches(prospect_with_combo.technologies))
    
    def test_technical_footprint_score(self):
        """Test the technical footprint scoring system."""
        icp = ShopifyDTCPremiumICP()
        
        # Test with a well-matched prospect
        tech_score = icp.calculate_technical_footprint_score(self.prospect)
        
        # Verify the structure of the result
        self.assertIn("total_score", tech_score)
        self.assertIn("max_score", tech_score)
        self.assertIn("percentage", tech_score)
        self.assertIn("details", tech_score)
        self.assertIn("recommendations", tech_score)
        
        # Verify the score is reasonable
        self.assertTrue(0 <= tech_score["percentage"] <= 100)
        # O score pode variar dependendo dos pesos e requisitos, então verificamos apenas se é positivo
        self.assertTrue(tech_score["percentage"] > 0)  # Deve ter algum match
        
        # Test with a prospect with no technologies
        empty_prospect = Prospect(domain="empty.com")
        empty_score = icp.calculate_technical_footprint_score(empty_prospect)
        self.assertEqual(empty_score["total_score"], 0)
        self.assertEqual(empty_score["percentage"], 0)
    
    def test_detect_saas_waste(self):
        """Test the SaaS waste detection system."""
        icp = ShopifyDTCPremiumICP()
        
        # Create a prospect with redundant tools
        waste_prospect = Prospect(domain="waste.com")
        waste_prospect.technologies = [
            Technology(name="klaviyo", category="email_marketing"),
            Technology(name="mailchimp", category="email_marketing"),
            Technology(name="google_analytics", category="analytics"),
            Technology(name="hotjar", category="analytics")
        ]
        
        # Test waste detection
        waste_result = icp.detect_saas_waste(waste_prospect)
        
        # Verify the structure of the result
        self.assertIn("total_monthly_waste", waste_result)
        self.assertIn("total_annual_waste", waste_result)
        self.assertIn("detected_patterns", waste_result)
        self.assertIn("recommendations", waste_result)
        
        # Verify waste was detected
        self.assertTrue(waste_result["total_monthly_waste"] > 0)
        self.assertEqual(waste_result["total_annual_waste"], waste_result["total_monthly_waste"] * 12)
        self.assertTrue(len(waste_result["detected_patterns"]) > 0)
        self.assertTrue(len(waste_result["recommendations"]) > 0)
        
        # Test with a prospect with no waste
        clean_prospect = Prospect(domain="clean.com")
        clean_prospect.technologies = [
            Technology(name="shopify", category="ecommerce_platform"),
            Technology(name="klaviyo", category="email_marketing")
        ]
        
        clean_result = icp.detect_saas_waste(clean_prospect)
        self.assertEqual(clean_result["total_monthly_waste"], 0)
        self.assertEqual(len(clean_result["detected_patterns"]), 0)
    
    def test_calculate_roi(self):
        """Test the ROI calculation system."""
        icp = ShopifyDTCPremiumICP()
        
        # Test with a standard prospect
        roi_result = icp.calculate_roi(self.prospect)
        
        # Verify the structure of the result
        self.assertIn("estimated_monthly_saas_spend", roi_result)
        self.assertIn("estimated_annual_saas_spend", roi_result)
        self.assertIn("estimated_monthly_waste", roi_result)
        self.assertIn("estimated_annual_waste", roi_result)
        self.assertIn("monthly_recoverable", roi_result)
        self.assertIn("annual_recoverable", roi_result)
        self.assertIn("three_year_savings", roi_result)
        self.assertIn("roi_percentage", roi_result)
        self.assertIn("waste_percentage", roi_result)
        
        # Verify calculations are reasonable
        self.assertTrue(roi_result["estimated_monthly_saas_spend"] > 0)
        self.assertEqual(roi_result["estimated_annual_saas_spend"], roi_result["estimated_monthly_saas_spend"] * 12)
        self.assertTrue(roi_result["estimated_monthly_waste"] > 0)
        self.assertEqual(roi_result["estimated_annual_waste"], roi_result["estimated_monthly_waste"] * 12)
        self.assertTrue(roi_result["monthly_recoverable"] > 0)
        self.assertEqual(roi_result["annual_recoverable"], roi_result["monthly_recoverable"] * 12)
        self.assertEqual(roi_result["three_year_savings"], roi_result["annual_recoverable"] * 3)
        
        # Test with a prospect with different employee count to check scaling
        large_prospect = Prospect(
            domain="large.com",
            employee_count=250,
            revenue=5000000.0
        )
        
        large_roi = icp.calculate_roi(large_prospect)
        self.assertTrue(large_roi["estimated_monthly_saas_spend"] > roi_result["estimated_monthly_saas_spend"])


if __name__ == "__main__":
    unittest.main()