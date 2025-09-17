"""
Validator Engine for ARCO.

This module contains the validator engine implementation for the ARCO system,
which is responsible for validating prospects.
"""

import logging
import yaml
import os
import asyncio
import aiohttp
import socket
from typing import Dict, List, Any, Optional
from datetime import datetime

from arco.engines.base import ValidatorEngineInterface
from arco.models.prospect import Prospect
from arco.utils.logger import get_logger

logger = get_logger(__name__)

class ValidatorEngine(ValidatorEngineInterface):
    """
    Validator engine implementation for ARCO.
    Validates prospects to ensure data accuracy and quality.
    """
    
    def __init__(self, config_path: str = "config/production.yml"):
        """
        Initialize the validator engine.
        
        Args:
            config_path: Path to the configuration file.
        """
        self.config_path = config_path
        self.session = None
        self.validation_thresholds = {
            'domain_existence': 0.4,  # 40% of score
            'company_info': 0.3,      # 30% of score
            'technology_info': 0.2,   # 20% of score
            'contact_info': 0.1       # 10% of score
        }
        
        logger.info(f"ValidatorEngine initialized with config: {config_path}")
        
        # Load configuration
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file."""
        try:
            # Try to load from config directory
            config_paths = [
                self.config_path,
                'config/production.yml',
                os.path.join(os.path.dirname(__file__), '../../config/production.yml')
            ]
            
            for path in config_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        config = yaml.safe_load(f)
                    
                    # Update validation thresholds if specified in config
                    if 'validation' in config and 'thresholds' in config['validation']:
                        self.validation_thresholds.update(config['validation']['thresholds'])
                    
                    logger.info(f"Loaded configuration from {path}")
                    return
            
            logger.warning(f"Configuration file not found, using default settings")
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    
    def validate(self, prospect: Prospect) -> Prospect:
        """
        Validate a prospect and update its validation score.
        
        Args:
            prospect: The prospect to validate
            
        Returns:
            Validated prospect with updated validation score
        """
        logger.info(f"Validating prospect: {prospect.domain}")
        
        # Run the async validation in a synchronous context
        loop = asyncio.get_event_loop()
        validated_prospect = loop.run_until_complete(self._validate_async(prospect))
        
        logger.info(f"Validated prospect: {prospect.domain}, score: {validated_prospect.validation_score:.2f}")
        return validated_prospect
    
    def batch_validate(self, prospects: List[Prospect]) -> List[Prospect]:
        """
        Validate multiple prospects in batch.
        
        Args:
            prospects: List of prospects to validate
            
        Returns:
            List of validated prospects with updated validation scores
        """
        logger.info(f"Batch validating {len(prospects)} prospects")
        
        # Run the async batch validation in a synchronous context
        loop = asyncio.get_event_loop()
        validated_prospects = loop.run_until_complete(self._batch_validate_async(prospects))
        
        logger.info(f"Batch validation complete for {len(validated_prospects)} prospects")
        return validated_prospects
    
    async def _validate_async(self, prospect: Prospect) -> Prospect:
        """
        Asynchronously validate a prospect.
        
        Args:
            prospect: The prospect to validate
            
        Returns:
            Validated prospect with updated validation score
        """
        # Ensure session is created if not already
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
        
        try:
            # Validate domain existence
            domain_score = await self._validate_domain(prospect.domain)
            
            # Validate company information
            company_score = self._validate_company_info(prospect)
            
            # Validate technology information
            technology_score = self._validate_technology_info(prospect)
            
            # Validate contact information
            contact_score = self._validate_contact_info(prospect)
            
            # Calculate overall validation score
            validation_score = (
                domain_score * self.validation_thresholds['domain_existence'] +
                company_score * self.validation_thresholds['company_info'] +
                technology_score * self.validation_thresholds['technology_info'] +
                contact_score * self.validation_thresholds['contact_info']
            )
            
            # Update prospect with validation score
            prospect.validation_score = validation_score
            
            logger.info(f"Validation complete for {prospect.domain}: score {validation_score:.2f}")
            
        except Exception as e:
            logger.error(f"Error during prospect validation for {prospect.domain}: {e}")
            prospect.validation_score = 0.0
        
        return prospect
    
    async def _batch_validate_async(self, prospects: List[Prospect]) -> List[Prospect]:
        """
        Asynchronously validate multiple prospects in batch.
        
        Args:
            prospects: List of prospects to validate
            
        Returns:
            List of validated prospects with updated validation scores
        """
        # Ensure session is created if not already
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
        
        # Create tasks for all prospects
        tasks = [self._validate_async(prospect) for prospect in prospects]
        
        # Run all validation tasks concurrently
        validated_prospects = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        result = []
        for i, prospect_or_exception in enumerate(validated_prospects):
            if isinstance(prospect_or_exception, Exception):
                logger.error(f"Error validating prospect {prospects[i].domain}: {prospect_or_exception}")
                # Return the original prospect with zero validation score
                prospects[i].validation_score = 0.0
                result.append(prospects[i])
            else:
                result.append(prospect_or_exception)
        
        return result
    
    async def _validate_domain(self, domain: str) -> float:
        """
        Validate domain existence.
        
        Args:
            domain: Domain to validate
            
        Returns:
            Validation score for domain existence (0.0-1.0)
        """
        try:
            # Check if domain resolves
            try:
                socket.gethostbyname(domain)
                dns_resolves = True
            except socket.gaierror:
                dns_resolves = False
            
            # Check if website responds
            try:
                async with self.session.get(f"https://{domain}", timeout=10, ssl=False) as response:
                    website_responds = response.status == 200
            except Exception:
                website_responds = False
            
            # Calculate score
            if dns_resolves and website_responds:
                return 1.0
            elif dns_resolves:
                return 0.7
            else:
                return 0.0
            
        except Exception as e:
            logger.error(f"Error validating domain {domain}: {e}")
            return 0.0
    
    def _validate_company_info(self, prospect: Prospect) -> float:
        """
        Validate company information.
        
        Args:
            prospect: Prospect to validate
            
        Returns:
            Validation score for company information (0.0-1.0)
        """
        score = 0.0
        
        # Check if company name is present
        if prospect.company_name:
            score += 0.3
        
        # Check if website is present
        if prospect.website:
            score += 0.2
        
        # Check if industry is present
        if prospect.industry:
            score += 0.2
        
        # Check if employee count is present
        if prospect.employee_count is not None:
            score += 0.15
        
        # Check if revenue is present
        if prospect.revenue is not None:
            score += 0.15
        
        return score
    
    def _validate_technology_info(self, prospect: Prospect) -> float:
        """
        Validate technology information.
        
        Args:
            prospect: Prospect to validate
            
        Returns:
            Validation score for technology information (0.0-1.0)
        """
        # Check if technologies are present
        if not prospect.technologies:
            return 0.0
        
        # Calculate score based on number of technologies
        tech_count = len(prospect.technologies)
        if tech_count >= 5:
            return 1.0
        elif tech_count >= 3:
            return 0.8
        elif tech_count >= 1:
            return 0.5
        else:
            return 0.0
    
    def _validate_contact_info(self, prospect: Prospect) -> float:
        """
        Validate contact information.
        
        Args:
            prospect: Prospect to validate
            
        Returns:
            Validation score for contact information (0.0-1.0)
        """
        # Check if contacts are present
        if not prospect.contacts:
            return 0.0
        
        # Calculate score based on contact information completeness
        total_score = 0.0
        for contact in prospect.contacts:
            contact_score = 0.0
            
            # Check if name is present
            if contact.name:
                contact_score += 0.2
            
            # Check if email is present
            if contact.email:
                contact_score += 0.3
            
            # Check if phone is present
            if contact.phone:
                contact_score += 0.2
            
            # Check if position is present
            if contact.position:
                contact_score += 0.15
            
            # Check if LinkedIn is present
            if contact.linkedin:
                contact_score += 0.15
            
            total_score = max(total_score, contact_score)
        
        return total_score
    
    async def close(self):
        """Clean up resources."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None