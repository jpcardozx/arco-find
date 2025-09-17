"""
Tests for the Apollo CSV Integration.
"""

import unittest
import os
import tempfile
import csv
from unittest.mock import patch, MagicMock

from arco.integrations.apollo_csv import ApolloCSVParser, ApolloCSVIntegration
from arco.models.prospect import Prospect, Technology, Contact


class TestApolloCSVParser(unittest.TestCase):
    """Test cases for the ApolloCSVParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary CSV file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.csv_path = os.path.join(self.temp_dir.name, "test_apollo.csv")
        
        # Create test data
        self.test_data = [
            {
                "Company": "Test Company",
                "Website": "http://testcompany.com",
                "Industry": "Technology",
                "# Employees": "25",
                "Annual Revenue": "$1,500,000",
                "Company Country": "United States",
                "Company City": "San Francisco",
                "Short Description": "A test company description",
                "Technologies": "Shopify, Klaviyo, Google Analytics",
                "Account Owner": "test@example.com",
                "Company Linkedin Url": "http://linkedin.com/company/testcompany"
            },
            {
                "Company": "Another Company",
                "Website": "http://anothercompany.com",
                "Industry": "Retail",
                "# Employees": "50",
                "Annual Revenue": "$3M",
                "Company Country": "Canada",
                "Company City": "Toronto",
                "Short Description": "Another test company",
                "Technologies": "WooCommerce, Mailchimp, Hotjar",
                "Account Owner": "another@example.com",
                "Company Linkedin Url": "http://linkedin.com/company/anothercompany"
            }
        ]
        
        # Write test data to CSV
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.test_data[0].keys())
            writer.writeheader()
            writer.writerows(self.test_data)
        
        # Create parser
        self.parser = ApolloCSVParser(self.csv_path)
    
    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()
    
    def test_parse_csv(self):
        """Test parsing CSV file."""
        self.assertEqual(len(self.parser.data), 2)
        self.assertEqual(self.parser.data[0]["Company"], "Test Company")
        self.assertEqual(self.parser.data[1]["Company"], "Another Company")
    
    def test_get_all_records(self):
        """Test getting all records."""
        records = self.parser.get_all_records()
        self.assertEqual(len(records), 2)
    
    def test_get_record_by_domain(self):
        """Test getting record by domain."""
        record = self.parser.get_record_by_domain("testcompany.com")
        self.assertIsNotNone(record)
        self.assertEqual(record["Company"], "Test Company")
        
        # Test with full URL
        record = self.parser.get_record_by_domain("http://testcompany.com")
        self.assertIsNotNone(record)
        self.assertEqual(record["Company"], "Test Company")
        
        # Test non-existent domain
        record = self.parser.get_record_by_domain("nonexistent.com")
        self.assertIsNone(record)
    
    def test_search_records(self):
        """Test searching records."""
        # Search by company name
        results = self.parser.search_records("Test")
        self.assertEqual(len(results), 2)  # Both have "test" in company name or description
        
        # Search by industry
        results = self.parser.search_records("Technology")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["Company"], "Test Company")
        
        # Search by non-existent term
        results = self.parser.search_records("nonexistent")
        self.assertEqual(len(results), 0)
    
    def test_convert_to_prospect(self):
        """Test converting record to prospect."""
        record = self.parser.get_record_by_domain("testcompany.com")
        prospect = self.parser.convert_to_prospect(record)
        
        self.assertIsInstance(prospect, Prospect)
        self.assertEqual(prospect.domain, "testcompany.com")
        self.assertEqual(prospect.company_name, "Test Company")
        self.assertEqual(prospect.industry, "Technology")
        self.assertEqual(prospect.employee_count, 25)
        self.assertEqual(prospect.revenue, 1500000.0)
        self.assertEqual(prospect.country, "United States")
        self.assertEqual(prospect.city, "San Francisco")
        
        # Check technologies
        self.assertEqual(len(prospect.technologies), 3)
        tech_names = [tech.name for tech in prospect.technologies]
        self.assertIn("Shopify", tech_names)
        self.assertIn("Klaviyo", tech_names)
        self.assertIn("Google Analytics", tech_names)
        
        # Check contacts
        self.assertEqual(len(prospect.contacts), 1)
        self.assertEqual(prospect.contacts[0].name, "test@example.com")
        self.assertEqual(prospect.contacts[0].email, "test@example.com")
        self.assertEqual(prospect.contacts[0].linkedin, "http://linkedin.com/company/testcompany")
    
    def test_extract_domain(self):
        """Test extracting domain from URL."""
        self.assertEqual(self.parser._extract_domain("http://example.com"), "example.com")
        self.assertEqual(self.parser._extract_domain("https://www.example.com"), "example.com")
        self.assertEqual(self.parser._extract_domain("https://example.com/path"), "example.com")
        self.assertEqual(self.parser._extract_domain(""), "")
    
    def test_parse_employee_count(self):
        """Test parsing employee count."""
        self.assertEqual(self.parser._parse_employee_count("25"), 25)
        self.assertEqual(self.parser._parse_employee_count("10-50"), 10)
        self.assertEqual(self.parser._parse_employee_count("100+"), 100)
        self.assertIsNone(self.parser._parse_employee_count(""))
        self.assertIsNone(self.parser._parse_employee_count("unknown"))
    
    def test_parse_revenue(self):
        """Test parsing revenue."""
        self.assertEqual(self.parser._parse_revenue("$1,500,000"), 1500000.0)
        self.assertEqual(self.parser._parse_revenue("$3M"), 3000000.0)
        self.assertEqual(self.parser._parse_revenue("$500K"), 500000.0)
        self.assertIsNone(self.parser._parse_revenue(""))
        self.assertIsNone(self.parser._parse_revenue("unknown"))
    
    def test_parse_technologies(self):
        """Test parsing technologies."""
        tech_tuples = self.parser._parse_technologies("Shopify, Klaviyo, Google Analytics")
        self.assertEqual(len(tech_tuples), 3)
        
        # Check technology names
        tech_names = [t[0] for t in tech_tuples]
        self.assertIn("Shopify", tech_names)
        self.assertIn("Klaviyo", tech_names)
        self.assertIn("Google Analytics", tech_names)
        
        # Check technology categories
        tech_dict = dict(tech_tuples)
        self.assertEqual(tech_dict["Shopify"], "ecommerce_platform")
        self.assertEqual(tech_dict["Klaviyo"], "email_marketing")
        self.assertEqual(tech_dict["Google Analytics"], "analytics")
    
    def test_determine_tech_category(self):
        """Test determining technology category."""
        self.assertEqual(self.parser._determine_tech_category("Shopify"), "ecommerce_platform")
        self.assertEqual(self.parser._determine_tech_category("Klaviyo"), "email_marketing")
        self.assertEqual(self.parser._determine_tech_category("Google Analytics"), "analytics")
        self.assertEqual(self.parser._determine_tech_category("WordPress"), "cms")
        self.assertEqual(self.parser._determine_tech_category("AWS"), "hosting")
        self.assertEqual(self.parser._determine_tech_category("Stripe"), "payment")
        self.assertEqual(self.parser._determine_tech_category("Zendesk"), "support")
        self.assertEqual(self.parser._determine_tech_category("Yotpo"), "reviews")
        self.assertEqual(self.parser._determine_tech_category("ReCharge"), "subscriptions")
        self.assertEqual(self.parser._determine_tech_category("Unknown Technology"), "other")


class TestApolloCSVIntegration(unittest.TestCase):
    """Test cases for the ApolloCSVIntegration class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the ApolloCSVParser
        self.mock_parser = MagicMock()
        self.mock_parser.get_record_by_domain.return_value = {
            "Company": "Test Company",
            "Website": "http://testcompany.com",
            "Industry": "Technology",
            "# Employees": "25",
            "Annual Revenue": "$1,500,000",
            "Company Country": "United States",
            "Company City": "San Francisco",
            "Short Description": "A test company description",
            "Technologies": "Shopify, Klaviyo, Google Analytics",
            "Account Owner": "test@example.com",
            "Company Linkedin Url": "http://linkedin.com/company/testcompany"
        }
        self.mock_parser.get_all_records.return_value = [
            self.mock_parser.get_record_by_domain.return_value
        ]
        self.mock_parser.search_records.return_value = [
            self.mock_parser.get_record_by_domain.return_value
        ]
        self.mock_parser._extract_domain.return_value = "testcompany.com"
        self.mock_parser._parse_employee_count.return_value = 25
        self.mock_parser._parse_revenue.return_value = 1500000.0
        self.mock_parser._parse_technologies.return_value = [
            ("Shopify", "ecommerce_platform"),
            ("Klaviyo", "email_marketing"),
            ("Google Analytics", "analytics")
        ]
        self.mock_parser.convert_to_prospect.return_value = Prospect(
            domain="testcompany.com",
            company_name="Test Company",
            website="http://testcompany.com",
            description="A test company description",
            industry="Technology",
            employee_count=25,
            revenue=1500000.0,
            country="United States",
            city="San Francisco"
        )
        
        # Patch the ApolloCSVParser class
        self.patcher = patch('arco.integrations.apollo_csv.ApolloCSVParser', return_value=self.mock_parser)
        self.mock_parser_class = self.patcher.start()
        
        # Patch os.listdir to return mock CSV files
        self.listdir_patcher = patch('os.listdir', return_value=["apollo-accounts-export.csv"])
        self.mock_listdir = self.listdir_patcher.start()
        
        # Create integration
        self.integration = ApolloCSVIntegration()
    
    def tearDown(self):
        """Clean up after tests."""
        self.patcher.stop()
        self.listdir_patcher.stop()
    
    def test_load_csv_files(self):
        """Test loading CSV files."""
        self.assertEqual(len(self.integration.parsers), 1)
        self.assertIn("apollo-accounts-export.csv", self.integration.parsers)
    
    def test_get_company_info(self):
        """Test getting company information."""
        company_info = self.integration.get_company_info("testcompany.com")
        self.assertIsNotNone(company_info)
        self.assertEqual(company_info["name"], "Test Company")
        self.assertEqual(company_info["website"], "http://testcompany.com")
        self.assertEqual(company_info["industry"], "Technology")
        
        # Test non-existent domain
        self.mock_parser.get_record_by_domain.return_value = None
        company_info = self.integration.get_company_info("nonexistent.com")
        self.assertIsNone(company_info)
    
    def test_get_contacts(self):
        """Test getting contacts."""
        contacts = self.integration.get_contacts("testcompany.com")
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0]["name"], "test@example.com")
        self.assertEqual(contacts[0]["email"], "test@example.com")
        self.assertEqual(contacts[0]["linkedin"], "http://linkedin.com/company/testcompany")
        
        # Test non-existent domain
        self.mock_parser.get_record_by_domain.return_value = None
        contacts = self.integration.get_contacts("nonexistent.com")
        self.assertEqual(len(contacts), 0)
    
    def test_get_technologies(self):
        """Test getting technologies."""
        technologies = self.integration.get_technologies("testcompany.com")
        self.assertEqual(len(technologies), 3)
        tech_names = [tech["name"] for tech in technologies]
        self.assertIn("Shopify", tech_names)
        self.assertIn("Klaviyo", tech_names)
        self.assertIn("Google Analytics", tech_names)
        
        # Test non-existent domain
        self.mock_parser.get_record_by_domain.return_value = None
        technologies = self.integration.get_technologies("nonexistent.com")
        self.assertEqual(len(technologies), 0)
    
    def test_search_companies(self):
        """Test searching companies."""
        companies = self.integration.search_companies("Test")
        self.assertEqual(len(companies), 1)
        self.assertEqual(companies[0]["name"], "Test Company")
        self.assertEqual(companies[0]["domain"], "testcompany.com")
        
        # Test non-existent term
        self.mock_parser.search_records.return_value = []
        companies = self.integration.search_companies("nonexistent")
        self.assertEqual(len(companies), 0)
    
    def test_get_all_prospects(self):
        """Test getting all prospects."""
        prospects = self.integration.get_all_prospects()
        self.assertEqual(len(prospects), 1)
        self.assertEqual(prospects[0].domain, "testcompany.com")
        self.assertEqual(prospects[0].company_name, "Test Company")
    
    def test_get_prospect_by_domain(self):
        """Test getting prospect by domain."""
        prospect = self.integration.get_prospect_by_domain("testcompany.com")
        self.assertIsNotNone(prospect)
        self.assertEqual(prospect.domain, "testcompany.com")
        self.assertEqual(prospect.company_name, "Test Company")
        
        # Test non-existent domain
        self.mock_parser.get_record_by_domain.return_value = None
        prospect = self.integration.get_prospect_by_domain("nonexistent.com")
        self.assertIsNone(prospect)


if __name__ == "__main__":
    unittest.main()