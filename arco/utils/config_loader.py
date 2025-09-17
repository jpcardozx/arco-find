"""
Configuration Loader for ARCO.

This module contains utilities for loading and managing configuration for the ARCO system.
"""

import logging
import os
from typing import Dict, Any, Optional
import yaml

logger = logging.getLogger(__name__)

class ConfigLoader:
    """Configuration loader for ARCO."""
    
    def __init__(self, config_path: str = "config/production.yml"):
        """
        Initialize the configuration loader.
        
        Args:
            config_path: Path to the configuration file.
        """
        self.config_path = config_path
        self.config = {}
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Dictionary with configuration.
        """
        logger.info(f"Loading configuration from: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            logger.info(f"Configuration loaded successfully from {self.config_path}")
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {self.config_path}")
            self.config = {}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {e}")
            self.config = {}
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self.config = {}
        
        return self.config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key.
            default: Default value if key is not found.
            
        Returns:
            Configuration value.
        """
        # Support nested keys with dot notation
        if '.' in key:
            parts = key.split('.')
            value = self.config
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return default
            return value
        
        return self.config.get(key, default)
    
    def get_nested(self, *keys: str, default: Any = None) -> Any:
        """
        Get a nested configuration value.
        
        Args:
            *keys: Sequence of keys to navigate the configuration.
            default: Default value if key is not found.
            
        Returns:
            Configuration value.
        """
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value