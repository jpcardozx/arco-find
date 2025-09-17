"""
Outreach Integration for ARCO.

This module provides integration with outreach tools for automated follow-up
with qualified prospects.
"""

import os
import json
import logging
import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from abc import ABC, abstractmethod
import uuid
import time

from arco.utils.logger import get_logger
from arco.models.prospect import Prospect, Contact
from arco.utils.progress_tracker import tracker, ProgressStage

logger = get_logger(__name__)

class OutreachIntegrationInterface(ABC):
    """Interface for outreach integrations."""
    
    @abstractmethod
    def initialize(self, api_key: str, **kwargs) -> bool:
        """
        Initialize the outreach integration.
        
        Args:
            api_key: API key for authentication
            **kwargs: Additional configuration parameters
            
        Returns:
            True if initialization was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def send_message(self, prospect: Prospect, template_name: str, 
                    personalization: Dict[str, Any] = None) -> str:
        """
        Send a message to a prospect.
        
        Args:
            prospect: Prospect to message
            template_name: Name of the template to use
            personalization: Personalization variables
            
        Returns:
            Message ID if successful, empty string otherwise
        """
        pass
    
    @abstractmethod
    def get_templates(self) -> List[Dict[str, Any]]:
        """
        Get available templates.
        
        Returns:
            List of templates
        """
        pass
    
    @abstractmethod
    def create_template(self, name: str, subject: str, body: str, 
                       template_type: str = "email") -> str:
        """
        Create a new template.
        
        Args:
            name: Template name
            subject: Email subject
            body: Email body
            template_type: Type of template (email, linkedin, etc.)
            
        Returns:
            Template ID if successful, empty string otherwise
        """
        pass
    
    @abstractmethod
    def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """
        Get the status of a message.
        
        Args:
            message_id: Message ID
            
        Returns:
            Message status
        """
        pass


class EmailOutreachIntegration(OutreachIntegrationInterface):
    """Email-based outreach integration."""
    
    def __init__(self, storage_dir: str = None):
        """
        Initialize the email outreach integration.
        
        Args:
            storage_dir: Directory to store outreach data
        """
        self.storage_dir = storage_dir or os.path.join("data", "outreach")
        os.makedirs(self.storage_dir, exist_ok=True)
        
        self.smtp_server = None
        self.smtp_port = None
        self.username = None
        self.password = None
        self.from_email = None
        self.from_name = None
        
        self.templates = {}
        self.messages = {}
        
        self._load_data()
    
    def _get_templates_file_path(self) -> str:
        """
        Get the path to the templates file.
        
        Returns:
            Path to the templates file
        """
        return os.path.join(self.storage_dir, "templates.json")
    
    def _get_messages_file_path(self) -> str:
        """
        Get the path to the messages file.
        
        Returns:
            Path to the messages file
        """
        return os.path.join(self.storage_dir, "messages.json")
    
    def _load_data(self) -> None:
        """Load templates and messages from files."""
        # Load templates
        templates_path = self._get_templates_file_path()
        if os.path.exists(templates_path):
            try:
                with open(templates_path, 'r', encoding='utf-8') as f:
                    self.templates = json.load(f)
                logger.info(f"Loaded {len(self.templates)} templates")
            except Exception as e:
                logger.error(f"Error loading templates: {e}")
        
        # Load messages
        messages_path = self._get_messages_file_path()
        if os.path.exists(messages_path):
            try:
                with open(messages_path, 'r', encoding='utf-8') as f:
                    self.messages = json.load(f)
                logger.info(f"Loaded {len(self.messages)} messages")
            except Exception as e:
                logger.error(f"Error loading messages: {e}")
    
    def _save_templates(self) -> None:
        """Save templates to file."""
        templates_path = self._get_templates_file_path()
        try:
            with open(templates_path, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, indent=2)
            logger.info(f"Saved {len(self.templates)} templates")
        except Exception as e:
            logger.error(f"Error saving templates: {e}")
    
    def _save_messages(self) -> None:
        """Save messages to file."""
        messages_path = self._get_messages_file_path()
        try:
            with open(messages_path, 'w', encoding='utf-8') as f:
                json.dump(self.messages, f, indent=2)
            logger.info(f"Saved {len(self.messages)} messages")
        except Exception as e:
            logger.error(f"Error saving messages: {e}")
    
    def initialize(self, api_key: str = None, **kwargs) -> bool:
        """
        Initialize the email outreach integration.
        
        Args:
            api_key: Not used for email integration
            **kwargs: SMTP configuration parameters
            
        Returns:
            True if initialization was successful, False otherwise
        """
        self.smtp_server = kwargs.get("smtp_server")
        self.smtp_port = kwargs.get("smtp_port", 587)
        self.username = kwargs.get("username")
        self.password = kwargs.get("password")
        self.from_email = kwargs.get("from_email")
        self.from_name = kwargs.get("from_name", "ARCO")
        
        # Test SMTP connection if real credentials provided
        if all([self.smtp_server, self.username, self.password, self.from_email]):
            try:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(self.username, self.password)
                logger.info("SMTP connection successful")
                return True
            except Exception as e:
                logger.error(f"SMTP connection failed: {e}")
                return False
        
        # For testing without real SMTP
        logger.warning("Using mock email sending (no real emails will be sent)")
        return True
    
    def get_templates(self) -> List[Dict[str, Any]]:
        """
        Get available templates.
        
        Returns:
            List of templates
        """
        return list(self.templates.values())
    
    def create_template(self, name: str, subject: str, body: str, 
                       template_type: str = "email") -> str:
        """
        Create a new template.
        
        Args:
            name: Template name
            subject: Email subject
            body: Email body
            template_type: Type of template (email, linkedin, etc.)
            
        Returns:
            Template ID if successful, empty string otherwise
        """
        template_id = str(uuid.uuid4())
        
        template = {
            "id": template_id,
            "name": name,
            "subject": subject,
            "body": body,
            "type": template_type,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.templates[template_id] = template
        self._save_templates()
        
        return template_id
    
    def send_message(self, prospect: Prospect, template_name: str, 
                    personalization: Dict[str, Any] = None) -> str:
        """
        Send a message to a prospect.
        
        Args:
            prospect: Prospect to message
            template_name: Name of the template to use
            personalization: Personalization variables
            
        Returns:
            Message ID if successful, empty string otherwise
        """
        # Find template by name
        template = None
        for t in self.templates.values():
            if t["name"] == template_name:
                template = t
                break
        
        if not template:
            logger.warning(f"Template not found: {template_name}")
            return ""
        
        # Find contact to email
        contact = None
        for c in prospect.contacts:
            if c.email:
                contact = c
                break
        
        if not contact:
            logger.warning(f"No contact with email found for prospect: {prospect.domain}")
            return ""
        
        # Prepare personalization
        if not personalization:
            personalization = {}
        
        personalization.update({
            "first_name": contact.name.split()[0] if contact.name and " " in contact.name else contact.name or "there",
            "last_name": contact.name.split()[-1] if contact.name and " " in contact.name else "",
            "full_name": contact.name or "",
            "company_name": prospect.company_name or prospect.domain,
            "domain": prospect.domain,
            "website": prospect.website or f"https://{prospect.domain}",
            "position": contact.position or "",
            "date": datetime.now().strftime("%B %d, %Y"),
            "sender_name": self.from_name
        })
        
        # Personalize subject and body
        subject = template["subject"]
        body = template["body"]
        
        for key, value in personalization.items():
            subject = subject.replace(f"{{{{{key}}}}}", str(value))
            body = body.replace(f"{{{{{key}}}}}", str(value))
        
        # Create message
        message_id = str(uuid.uuid4())
        
        message = {
            "id": message_id,
            "prospect_domain": prospect.domain,
            "contact_email": contact.email,
            "contact_name": contact.name,
            "template_id": template["id"],
            "template_name": template["name"],
            "subject": subject,
            "body": body,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "sent_at": None,
            "delivered_at": None,
            "opened_at": None,
            "clicked_at": None,
            "replied_at": None
        }
        
        self.messages[message_id] = message
        self._save_messages()
        
        # Send email
        try:
            if all([self.smtp_server, self.username, self.password, self.from_email]):
                # Create email message
                msg = MIMEMultipart()
                msg["From"] = f"{self.from_name} <{self.from_email}>"
                msg["To"] = contact.email
                msg["Subject"] = subject
                
                # Add body
                msg.attach(MIMEText(body, "html"))
                
                # Send email
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(self.username, self.password)
                    server.send_message(msg)
                
                # Update message status
                self.messages[message_id]["status"] = "sent"
                self.messages[message_id]["sent_at"] = datetime.now().isoformat()
                self._save_messages()
                
                logger.info(f"Email sent to {contact.email}")
            else:
                # Mock sending for testing
                logger.info(f"Mock email to {contact.email}: {subject}")
                
                # Simulate sending
                self.messages[message_id]["status"] = "sent"
                self.messages[message_id]["sent_at"] = datetime.now().isoformat()
                
                # Simulate delivery (50% chance)
                if uuid.uuid4().int % 2 == 0:
                    self.messages[message_id]["status"] = "delivered"
                    self.messages[message_id]["delivered_at"] = (
                        datetime.fromisoformat(self.messages[message_id]["sent_at"]) + 
                        timedelta(seconds=30)
                    ).isoformat()
                    
                    # Simulate open (30% chance)
                    if uuid.uuid4().int % 10 < 3:
                        self.messages[message_id]["status"] = "opened"
                        self.messages[message_id]["opened_at"] = (
                            datetime.fromisoformat(self.messages[message_id]["delivered_at"]) + 
                            timedelta(minutes=5)
                        ).isoformat()
                        
                        # Simulate click (20% chance)
                        if uuid.uuid4().int % 10 < 2:
                            self.messages[message_id]["status"] = "clicked"
                            self.messages[message_id]["clicked_at"] = (
                                datetime.fromisoformat(self.messages[message_id]["opened_at"]) + 
                                timedelta(minutes=2)
                            ).isoformat()
                            
                            # Simulate reply (10% chance)
                            if uuid.uuid4().int % 10 < 1:
                                self.messages[message_id]["status"] = "replied"
                                self.messages[message_id]["replied_at"] = (
                                    datetime.fromisoformat(self.messages[message_id]["clicked_at"]) + 
                                    timedelta(hours=2)
                                ).isoformat()
                
                self._save_messages()
            
            return message_id
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            
            # Update message status
            self.messages[message_id]["status"] = "failed"
            self._save_messages()
            
            return ""
    
    def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """
        Get the status of a message.
        
        Args:
            message_id: Message ID
            
        Returns:
            Message status
        """
        if message_id not in self.messages:
            return {"status": "not_found"}
        
        return {
            "status": self.messages[message_id]["status"],
            "sent_at": self.messages[message_id]["sent_at"],
            "delivered_at": self.messages[message_id]["delivered_at"],
            "opened_at": self.messages[message_id]["opened_at"],
            "clicked_at": self.messages[message_id]["clicked_at"],
            "replied_at": self.messages[message_id]["replied_at"]
        }


class OutreachManager:
    """Manager for outreach integrations."""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(OutreachManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the outreach manager."""
        if self._initialized:
            return
        
        self.integrations = {}
        self.active_integration = None
        
        # Register built-in integrations
        self.register_integration("email", EmailOutreachIntegration())
        
        # Set default active integration
        self.set_active_integration("email")
        
        # Create default templates
        self._create_default_templates()
        
        self._initialized = True
    
    def _create_default_templates(self) -> None:
        """Create default templates for each ICP."""
        email_integration = self.get_integration("email")
        
        # Check if templates already exist
        existing_templates = {t["name"]: t for t in email_integration.get_templates()}
        
        # Shopify DTC Premium template
        if "shopify_dtc_initial" not in existing_templates:
            email_integration.create_template(
                name="shopify_dtc_initial",
                subject="Boost {{company_name}}'s ROI with our Shopify optimization",
                body="""
                <p>Hi {{first_name}},</p>
                
                <p>I noticed {{company_name}} is running on Shopify and wanted to reach out because we've helped similar DTC brands reduce their tech stack costs while improving conversion rates.</p>
                
                <p>Our analysis shows that companies like yours typically have:</p>
                <ul>
                    <li>Redundant apps costing $500-1,500/month</li>
                    <li>Performance issues affecting conversion rates</li>
                    <li>Opportunities to increase AOV by 15-25%</li>
                </ul>
                
                <p>Would you be open to a quick 15-minute call to see if we can help {{company_name}} achieve similar results?</p>
                
                <p>Best regards,<br>
                {{sender_name}}</p>
                """
            )
        
        # Health Supplements template
        if "health_supplements_initial" not in existing_templates:
            email_integration.create_template(
                name="health_supplements_initial",
                subject="Scaling {{company_name}}'s supplement business more efficiently",
                body="""
                <p>Hi {{first_name}},</p>
                
                <p>I came across {{company_name}} and was impressed by your supplement offerings. Having worked with several health supplement brands, I noticed some opportunities that might help you scale more efficiently.</p>
                
                <p>Our clients in the supplement space typically see:</p>
                <ul>
                    <li>30% reduction in customer acquisition costs</li>
                    <li>25% increase in subscription retention rates</li>
                    <li>Significant savings on tech and marketing tools</li>
                </ul>
                
                <p>I'd love to share some specific insights about how {{company_name}} could benefit from our approach. Would you be available for a brief call this week?</p>
                
                <p>Best regards,<br>
                {{sender_name}}</p>
                """
            )
        
        # Fitness Equipment template
        if "fitness_equipment_initial" not in existing_templates:
            email_integration.create_template(
                name="fitness_equipment_initial",
                subject="Optimizing {{company_name}}'s fitness equipment sales funnel",
                body="""
                <p>Hi {{first_name}},</p>
                
                <p>I've been researching the fitness equipment space and was particularly interested in {{company_name}}'s approach. Based on our work with similar companies, I believe there are some significant opportunities to optimize your sales and marketing stack.</p>
                
                <p>Our fitness equipment clients typically achieve:</p>
                <ul>
                    <li>40% reduction in abandoned carts</li>
                    <li>35% improvement in ROAS on ad spend</li>
                    <li>$1,000-2,500 monthly savings on redundant SaaS tools</li>
                </ul>
                
                <p>I'd be happy to share a quick analysis of specific opportunities for {{company_name}}. Would you have 15 minutes for a call this week?</p>
                
                <p>Best regards,<br>
                {{sender_name}}</p>
                """
            )
        
        # Generic high ROI template
        if "high_roi_initial" not in existing_templates:
            email_integration.create_template(
                name="high_roi_initial",
                subject="{{company_name}} - Significant cost savings opportunity identified",
                body="""
                <p>Hi {{first_name}},</p>
                
                <p>I recently analyzed {{company_name}}'s tech stack and identified several opportunities to reduce costs while improving performance.</p>
                
                <p>Based on our analysis, we believe we can help you:</p>
                <ul>
                    <li>Reduce SaaS spending by 20-30%</li>
                    <li>Consolidate redundant tools</li>
                    <li>Improve site performance and conversion rates</li>
                </ul>
                
                <p>Companies similar to yours typically see an ROI of 300-500% in the first year. Would you be interested in a brief call to discuss these opportunities?</p>
                
                <p>Best regards,<br>
                {{sender_name}}</p>
                """
            )
        
        # Follow-up template
        if "follow_up_template" not in existing_templates:
            email_integration.create_template(
                name="follow_up_template",
                subject="Following up on {{company_name}}'s optimization opportunity",
                body="""
                <p>Hi {{first_name}},</p>
                
                <p>I wanted to follow up on my previous email about helping {{company_name}} optimize your tech stack and improve performance.</p>
                
                <p>I understand you're busy, so I thought I'd share a quick case study of how we helped a similar company save over $25,000 annually while increasing their conversion rate by 18%.</p>
                
                <p>Would you be interested in seeing if we could achieve similar results for {{company_name}}?</p>
                
                <p>Best regards,<br>
                {{sender_name}}</p>
                """
            )
    
    def register_integration(self, name: str, integration: OutreachIntegrationInterface) -> None:
        """
        Register an outreach integration.
        
        Args:
            name: Integration name
            integration: Integration instance
        """
        self.integrations[name] = integration
        logger.info(f"Registered outreach integration: {name}")
    
    def set_active_integration(self, name: str) -> bool:
        """
        Set the active outreach integration.
        
        Args:
            name: Integration name
            
        Returns:
            True if successful, False otherwise
        """
        if name not in self.integrations:
            logger.warning(f"Outreach integration not found: {name}")
            return False
        
        self.active_integration = name
        logger.info(f"Set active outreach integration: {name}")
        return True
    
    def get_integration(self, name: str = None) -> Optional[OutreachIntegrationInterface]:
        """
        Get an outreach integration.
        
        Args:
            name: Integration name, or None for active integration
            
        Returns:
            Outreach integration or None if not found
        """
        if name is None:
            name = self.active_integration
        
        return self.integrations.get(name)
    
    def initialize_integration(self, name: str, api_key: str = None, **kwargs) -> bool:
        """
        Initialize an outreach integration.
        
        Args:
            name: Integration name
            api_key: API key
            **kwargs: Additional configuration parameters
            
        Returns:
            True if successful, False otherwise
        """
        integration = self.get_integration(name)
        if not integration:
            return False
        
        return integration.initialize(api_key, **kwargs)
    
    def get_templates(self, integration_name: str = None) -> List[Dict[str, Any]]:
        """
        Get available templates.
        
        Args:
            integration_name: Integration name, or None for active integration
            
        Returns:
            List of templates
        """
        integration = self.get_integration(integration_name)
        if not integration:
            logger.warning("No active outreach integration")
            return []
        
        return integration.get_templates()
    
    def create_template(self, name: str, subject: str, body: str, 
                       template_type: str = "email", integration_name: str = None) -> str:
        """
        Create a new template.
        
        Args:
            name: Template name
            subject: Email subject
            body: Email body
            template_type: Type of template (email, linkedin, etc.)
            integration_name: Integration name, or None for active integration
            
        Returns:
            Template ID if successful, empty string otherwise
        """
        integration = self.get_integration(integration_name)
        if not integration:
            logger.warning("No active outreach integration")
            return ""
        
        return integration.create_template(name, subject, body, template_type)
    
    def send_message(self, prospect: Prospect, template_name: str, 
                    personalization: Dict[str, Any] = None, integration_name: str = None) -> str:
        """
        Send a message to a prospect.
        
        Args:
            prospect: Prospect to message
            template_name: Name of the template to use
            personalization: Personalization variables
            integration_name: Integration name, or None for active integration
            
        Returns:
            Message ID if successful, empty string otherwise
        """
        integration = self.get_integration(integration_name)
        if not integration:
            logger.warning("No active outreach integration")
            return ""
        
        # Get lead ID from tracker
        lead = tracker.get_lead_by_domain(prospect.domain)
        if not lead:
            logger.warning(f"Lead not found in tracker: {prospect.domain}")
            return ""
        
        # Send message
        message_id = integration.send_message(prospect, template_name, personalization)
        
        if message_id:
            # Update tracker
            tracker.update_stage(lead.lead_id, ProgressStage.CONTACTED, {
                "message_id": message_id,
                "template_name": template_name,
                "timestamp": datetime.now().isoformat()
            })
        
        return message_id
    
    def get_message_status(self, message_id: str, integration_name: str = None) -> Dict[str, Any]:
        """
        Get the status of a message.
        
        Args:
            message_id: Message ID
            integration_name: Integration name, or None for active integration
            
        Returns:
            Message status
        """
        integration = self.get_integration(integration_name)
        if not integration:
            logger.warning("No active outreach integration")
            return {"status": "error", "message": "No active outreach integration"}
        
        return integration.get_message_status(message_id)
    
    def select_template_for_prospect(self, prospect: Prospect, analysis_results: Dict[str, Any]) -> str:
        """
        Select the best template for a prospect based on analysis results.
        
        Args:
            prospect: Prospect to select template for
            analysis_results: Analysis results
            
        Returns:
            Template name
        """
        # Get best ICP
        best_icp = analysis_results.get("best_icp")
        
        # Get ROI percentage
        roi_percentage = analysis_results.get("leak_results", {}).get("summary", {}).get("roi_percentage", 0)
        
        # Select template based on ICP and ROI
        if best_icp == "shopify_dtc":
            return "shopify_dtc_initial"
        elif best_icp == "health_supplements":
            return "health_supplements_initial"
        elif best_icp == "fitness_equipment":
            return "fitness_equipment_initial"
        elif roi_percentage >= 20:
            return "high_roi_initial"
        else:
            return "high_roi_initial"  # Default to high ROI template
    
    def send_follow_up(self, prospect: Prospect, days_since_contact: int = 3) -> str:
        """
        Send a follow-up message to a prospect.
        
        Args:
            prospect: Prospect to message
            days_since_contact: Days since initial contact
            
        Returns:
            Message ID if successful, empty string otherwise
        """
        # Get lead from tracker
        lead = tracker.get_lead_by_domain(prospect.domain)
        if not lead:
            logger.warning(f"Lead not found in tracker: {prospect.domain}")
            return ""
        
        # Check if lead is in CONTACTED stage
        if lead.current_stage != ProgressStage.CONTACTED:
            logger.warning(f"Lead not in CONTACTED stage: {prospect.domain}")
            return ""
        
        # Get contact timestamp
        contact_metadata = lead.metadata.get(ProgressStage.CONTACTED, {})
        contact_timestamp = contact_metadata.get("timestamp")
        
        if not contact_timestamp:
            logger.warning(f"Contact timestamp not found for lead: {prospect.domain}")
            return ""
        
        # Calculate days since contact
        contact_date = datetime.fromisoformat(contact_timestamp)
        days_elapsed = (datetime.now() - contact_date).days
        
        if days_elapsed < days_since_contact:
            logger.info(f"Not enough time elapsed for follow-up: {days_elapsed} days (need {days_since_contact})")
            return ""
        
        # Send follow-up
        personalization = {
            "days_since_contact": days_elapsed
        }
        
        return self.send_message(prospect, "follow_up_template", personalization)


# Global instance
outreach_manager = OutreachManager()