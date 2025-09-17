"""
Tests for the lead enrichment engine.
"""

import os
import sys
import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from arco.engines.lead_enrichment_engine import (
    LeadEnrichmentEngine,
    EnrichmentResult
)
from arco.models.prospect import Prospect, Contact, Technology


class TestLeadEnrichmentEngine(unittest.TestCase):
    """Test the lead enrichment engine."""
    
    def setUp(self):
        """Set up the test."""
        self.engine = LeadEnrichmentEngine()
        
        # Create a basic test prospect
        self.prospect = Prospect(
            domain="example.com",
            company_name="",  # Will be enriched
            website="https://example.com",
            description="",   # Will be enriched
            industry="",      # Will be enriched
            employee_count=None,  # Will be enriched
            revenue=None,     # Will be enriched
            country="",       # Will be enriched
            city=""
        )
    
    def test_improve_company_name(self):
        """Test company name improvement."""
        # Test basic domain to company name
        name = self.engine._improve_company_name("example-company.com")
        self.assertEqual(name, "Example Company")
        
        # Test with underscores
        name = self.engine._improve_company_name("my_great_company.com")
        self.assertEqual(name, "My Great Company")
        
        # Test with common abbreviations
        name = self.engine._improve_company_name("acme-corp.com")
        self.assertEqual(name, "Acme CORP")
    
    def test_infer_country_from_domain(self):
        """Test country inference from domain TLD."""
        # Test UK domain
        country = self.engine._infer_country_from_domain("example.co.uk")
        self.assertEqual(country, "United Kingdom")
        
        # Test Canadian domain
        country = self.engine._infer_country_from_domain("example.ca")
        self.assertEqual(country, "Canada")
        
        # Test US domain (default for .com)
        country = self.engine._infer_country_from_domain("example.com")
        self.assertEqual(country, "United States")
        
        # Test unknown TLD
        country = self.engine._infer_country_from_domain("example.xyz")
        self.assertIsNone(country)
    
    def test_classify_industry(self):
        """Test industry classification."""
        # Test e-commerce classification
        ecommerce_prospect = Prospect(
            domain="myshop.com",
            company_name="My Online Store",
            description="We sell products online"
        )
        
        result = self.engine._classify_industry(ecommerce_prospect)
        self.assertEqual(result["industry"], "E-commerce")
        self.assertGreater(result["confidence"], 0)
        
        # Test technology classification
        tech_prospect = Prospect(
            domain="techsoftware.com",
            company_name="Tech Software Solutions",
            description="We develop software applications"
        )
        
        result = self.engine._classify_industry(tech_prospect)
        self.assertEqual(result["industry"], "Technology")
        self.assertGreater(result["confidence"], 0)
        
        # Test no clear industry
        generic_prospect = Prospect(
            domain="generic.com",
            company_name="Generic Company",
            description="A business"
        )
        
        result = self.engine._classify_industry(generic_prospect)
        self.assertIsNone(result["industry"])
        self.assertEqual(result["confidence"], 0.0)
    
    def test_estimate_revenue(self):
        """Test revenue estimation."""
        # Test with employee count and industry
        prospect_with_employees = Prospect(
            domain="tech.com",
            employee_count=50,
            industry="Technology"
        )
        
        result = self.engine._estimate_revenue(prospect_with_employees)
        self.assertIsNotNone(result["revenue"])
        self.assertGreater(result["revenue"], 0)
        self.assertGreater(result["confidence"], 0)
        
        # Test without employee count
        prospect_without_employees = Prospect(domain="test.com")
        
        result = self.engine._estimate_revenue(prospect_without_employees)
        self.assertIsNone(result["revenue"])
        self.assertEqual(result["confidence"], 0.0)
    
    def test_generate_common_contacts(self):
        """Test generation of common contact patterns."""
        # Test normal domain
        contacts = self.engine._generate_common_contacts(self.prospect)
        self.assertGreater(len(contacts), 0)
        
        # Check that contacts have expected structure
        for contact in contacts:
            self.assertIsInstance(contact, Contact)
            self.assertTrue(contact.email.endswith("@example.com"))
            self.assertIsNotNone(contact.name)
            self.assertIsNotNone(contact.position)
        
        # Test with common email domain (should return empty)
        gmail_prospect = Prospect(domain="gmail.com")
        contacts = self.engine._generate_common_contacts(gmail_prospect)
        self.assertEqual(len(contacts), 0)
    
    def test_improve_contact_info(self):
        """Test contact information improvement."""
        # Test position standardization
        contact = Contact(
            name="John Doe",
            email="john@example.com",
            position="Chief Executive Officer"
        )
        
        self.engine._improve_contact_info(contact, self.prospect)
        self.assertEqual(contact.position, "CEO")
        
        # Test invalid email handling
        bad_contact = Contact(
            name="Jane Doe",
            email="invalid-email",
            position="Manager"
        )
        
        self.engine._improve_contact_info(bad_contact, self.prospect)
        self.assertIsNone(bad_contact.email)
    
    @patch('httpx.AsyncClient')
    async def test_analyze_http_headers(self, mock_client):
        """Test HTTP header analysis for technology detection."""
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.headers = {
            "server": "nginx/1.18.0",
            "x-powered-by": "PHP/7.4.0"
        }
        mock_response.text = "<html><body>Powered by WordPress</body></html>"
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        technologies = await self.engine._analyze_http_headers("https://example.com")
        
        # Should detect Nginx, PHP, and WordPress
        tech_names = [tech.name for tech in technologies]
        self.assertIn("Nginx", tech_names)
        self.assertIn("PHP", tech_names)
        self.assertIn("WordPress", tech_names)
    
    async def test_enrich_company_info(self):
        """Test company information enrichment."""
        # Test with minimal prospect
        minimal_prospect = Prospect(domain="test-company.com")
        
        result = await self.engine._enrich_company_info(minimal_prospect)
        
        # Should have enriched some fields
        self.assertGreater(len(result["enriched_fields"]), 0)
        self.assertIn("company_name", result["updated_fields"])
        self.assertIn("country", result["updated_fields"])
        
        # Check company name improvement
        self.assertEqual(result["updated_fields"]["company_name"], "Test Company")
        
        # Check country inference
        self.assertEqual(result["updated_fields"]["country"], "United States")
    
    @patch('arco.engines.lead_enrichment_engine.LeadEnrichmentEngine._enrich_technologies')
    @patch('arco.engines.lead_enrichment_engine.LeadEnrichmentEngine._enrich_company_info')
    @patch('arco.engines.lead_enrichment_engine.LeadEnrichmentEngine._enrich_contacts')
    async def test_enrich_prospect(self, mock_contacts, mock_company, mock_tech):
        """Test full prospect enrichment."""
        # Mock the individual enrichment methods
        mock_tech.return_value = {
            "success": True,
            "technologies": [Technology(name="Test Tech", category="test")],
            "confidence": 0.8,
            "errors": []
        }
        
        mock_company.return_value = {
            "updated_fields": {"industry": "Technology"},
            "enriched_fields": ["industry"],
            "confidence_scores": {"industry": 0.7}
        }
        
        mock_contacts.return_value = {
            "success": True,
            "contacts": [Contact(name="Test Contact", email="test@example.com")],
            "confidence": 0.6,
            "errors": []
        }
        
        # Test enrichment
        result = await self.engine.enrich_prospect(self.prospect, deep_enrichment=True)
        
        # Check result structure
        self.assertIsInstance(result, EnrichmentResult)
        self.assertTrue(result.success)
        self.assertGreater(len(result.enriched_fields), 0)
        self.assertGreater(len(result.new_technologies), 0)
        self.assertGreater(len(result.new_contacts), 0)
        
        # Check that prospect was updated
        self.assertEqual(self.prospect.industry, "Technology")
        self.assertGreater(len(self.prospect.technologies), 0)
        self.assertGreater(len(self.prospect.contacts), 0)
    
    async def test_batch_enrich_prospects(self):
        """Test batch enrichment of multiple prospects."""
        prospects = []
        
        # Create test prospects
        for i in range(3):
            prospect = Prospect(
                domain=f"test{i}.com",
                company_name="",
                industry=""
            )
            prospects.append(prospect)
        
        # Mock the individual enrichment to avoid external calls
        with patch.object(self.engine, 'enrich_prospect') as mock_enrich:
            mock_enrich.return_value = EnrichmentResult(
                success=True,
                enriched_fields=["industry"],
                new_technologies=[],
                new_contacts=[],
                updated_fields={"industry": "Technology"},
                confidence_scores={"industry": 0.7},
                errors=[]
            )
            
            results = await self.engine.batch_enrich_prospects(prospects, batch_size=2)
            
            # Check that we get results for all prospects
            self.assertEqual(len(results), len(prospects))
            
            # Check that each result is an EnrichmentResult
            for domain, result in results.items():
                self.assertIsInstance(result, EnrichmentResult)


if __name__ == "__main__":
    # Run async tests
    unittest.main()