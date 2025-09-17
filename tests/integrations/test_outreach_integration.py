"""
Tests for the outreach integration.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime, timedelta

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from arco.integrations.outreach_integration import (
    OutreachIntegrationInterface,
    EmailOutreachIntegration,
    OutreachManager,
    outreach_manager
)
from arco.models.prospect import Prospect, Contact, Technology


class TestEmailOutreachIntegration(unittest.TestCase):
    """Test the email outreach integration."""
    
    def setUp(self):
        """Set up the test."""
        # Create a temporary directory for test data
        self.test_dir = os.path.join("tests", "data", "outreach")
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Create an instance with the test directory
        self.integration = EmailOutreachIntegration(self.test_dir)
        
        # Create a test prospect
        self.prospect = Prospect(
            domain="example.com",
            company_name="Example Inc.",
            website="https://example.com",
            description="Example company",
            industry="Technology",
            employee_count=100,
            revenue=1000000,
            country="United States",
            city="San Francisco"
        )
        
        # Add a contact
        self.prospect.contacts.append(Contact(
            name="John Doe",
            email="john@example.com",
            phone="123-456-7890",
            position="CEO"
        ))
    
    def test_initialize(self):
        """Test initializing the integration."""
        # Test with mock SMTP
        with patch('smtplib.SMTP') as mock_smtp:
            # Configure the mock
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            # Initialize with mock SMTP
            result = self.integration.initialize(
                smtp_server="smtp.example.com",
                smtp_port=587,
                username="user",
                password="pass",
                from_email="from@example.com",
                from_name="Test Sender"
            )
            
            # Check result
            self.assertTrue(result)
            
            # Check SMTP calls
            mock_smtp.assert_called_once_with("smtp.example.com", 587)
            mock_server.ehlo.assert_called()
            mock_server.starttls.assert_called()
            mock_server.login.assert_called_with("user", "pass")
    
    def test_create_template(self):
        """Test creating a template."""
        # Create a template
        template_id = self.integration.create_template(
            name="test_template",
            subject="Test Subject",
            body="Test Body",
            template_type="email"
        )
        
        # Check template ID
        self.assertIsNotNone(template_id)
        self.assertTrue(len(template_id) > 0)
        
        # Check template in templates
        self.assertIn(template_id, self.integration.templates)
        template = self.integration.templates[template_id]
        self.assertEqual(template["name"], "test_template")
        self.assertEqual(template["subject"], "Test Subject")
        self.assertEqual(template["body"], "Test Body")
        self.assertEqual(template["type"], "email")
    
    def test_get_templates(self):
        """Test getting templates."""
        # Create some templates
        template1_id = self.integration.create_template(
            name="template1",
            subject="Subject 1",
            body="Body 1"
        )
        
        template2_id = self.integration.create_template(
            name="template2",
            subject="Subject 2",
            body="Body 2"
        )
        
        # Get templates
        templates = self.integration.get_templates()
        
        # Check templates
        self.assertEqual(len(templates), 2)
        template_names = [t["name"] for t in templates]
        self.assertIn("template1", template_names)
        self.assertIn("template2", template_names)
    
    def test_send_message(self):
        """Test sending a message."""
        # Create a template
        template_id = self.integration.create_template(
            name="test_template",
            subject="Test Subject for {{company_name}}",
            body="Hello {{first_name}}, this is a test for {{company_name}}."
        )
        
        # Test with mock SMTP
        with patch('smtplib.SMTP') as mock_smtp:
            # Configure the mock
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            # Initialize with mock SMTP
            self.integration.initialize(
                smtp_server="smtp.example.com",
                smtp_port=587,
                username="user",
                password="pass",
                from_email="from@example.com",
                from_name="Test Sender"
            )
            
            # Send message
            message_id = self.integration.send_message(
                prospect=self.prospect,
                template_name="test_template",
                personalization={"custom_field": "Custom Value"}
            )
            
            # Check message ID
            self.assertIsNotNone(message_id)
            self.assertTrue(len(message_id) > 0)
            
            # Check message in messages
            self.assertIn(message_id, self.integration.messages)
            message = self.integration.messages[message_id]
            self.assertEqual(message["prospect_domain"], "example.com")
            self.assertEqual(message["contact_email"], "john@example.com")
            self.assertEqual(message["template_name"], "test_template")
            self.assertEqual(message["subject"], "Test Subject for Example Inc.")
            self.assertIn("Hello John", message["body"])
            self.assertIn("Example Inc.", message["body"])
    
    def test_get_message_status(self):
        """Test getting message status."""
        # Create a template
        template_id = self.integration.create_template(
            name="test_template",
            subject="Test Subject",
            body="Test Body"
        )
        
        # Send message (mock)
        message_id = self.integration.send_message(
            prospect=self.prospect,
            template_name="test_template"
        )
        
        # Get message status
        status = self.integration.get_message_status(message_id)
        
        # Check status
        self.assertIn("status", status)
        self.assertIn(status["status"], ["pending", "sent", "delivered", "opened", "clicked", "replied"])
    
    def tearDown(self):
        """Clean up after the test."""
        # Remove test files
        templates_path = os.path.join(self.test_dir, "templates.json")
        if os.path.exists(templates_path):
            os.remove(templates_path)
        
        messages_path = os.path.join(self.test_dir, "messages.json")
        if os.path.exists(messages_path):
            os.remove(messages_path)
        
        # Remove test directory if empty
        try:
            os.rmdir(self.test_dir)
        except OSError:
            pass


class TestOutreachManager(unittest.TestCase):
    """Test the outreach manager."""
    
    def setUp(self):
        """Set up the test."""
        # Create a test prospect
        self.prospect = Prospect(
            domain="example.com",
            company_name="Example Inc.",
            website="https://example.com",
            description="Example company",
            industry="Technology",
            employee_count=100,
            revenue=1000000,
            country="United States",
            city="San Francisco"
        )
        
        # Add a contact
        self.prospect.contacts.append(Contact(
            name="John Doe",
            email="john@example.com",
            phone="123-456-7890",
            position="CEO"
        ))
        
        # Mock analysis results
        self.analysis_results = {
            "best_icp": "shopify_dtc",
            "best_score": 85,
            "leak_results": {
                "summary": {
                    "total_monthly_waste": 500,
                    "total_annual_waste": 6000,
                    "total_monthly_savings": 400,
                    "total_annual_savings": 4800,
                    "roi_percentage": 25,
                    "priority_recommendations": [
                        "Consolidate analytics tools",
                        "Optimize hosting costs",
                        "Reduce redundant marketing tools"
                    ]
                }
            }
        }
    
    def test_select_template_for_prospect(self):
        """Test selecting a template for a prospect."""
        # Test with Shopify DTC ICP
        template_name = outreach_manager.select_template_for_prospect(
            prospect=self.prospect,
            analysis_results=self.analysis_results
        )
        self.assertEqual(template_name, "shopify_dtc_initial")
        
        # Test with Health Supplements ICP
        self.analysis_results["best_icp"] = "health_supplements"
        template_name = outreach_manager.select_template_for_prospect(
            prospect=self.prospect,
            analysis_results=self.analysis_results
        )
        self.assertEqual(template_name, "health_supplements_initial")
        
        # Test with Fitness Equipment ICP
        self.analysis_results["best_icp"] = "fitness_equipment"
        template_name = outreach_manager.select_template_for_prospect(
            prospect=self.prospect,
            analysis_results=self.analysis_results
        )
        self.assertEqual(template_name, "fitness_equipment_initial")
        
        # Test with high ROI
        self.analysis_results["best_icp"] = "other"
        self.analysis_results["leak_results"]["summary"]["roi_percentage"] = 30
        template_name = outreach_manager.select_template_for_prospect(
            prospect=self.prospect,
            analysis_results=self.analysis_results
        )
        self.assertEqual(template_name, "high_roi_initial")


if __name__ == "__main__":
    unittest.main()