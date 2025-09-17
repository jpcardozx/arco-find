"""
Configuration Manager for ARCO.

This module provides a centralized configuration management system for the ARCO system,
handling environment variables, configuration files, and default settings.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dotenv import load_dotenv

from arco.utils.config_loader import ConfigLoader

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Centralized configuration manager for ARCO.
    
    This class handles loading configuration from multiple sources:
    1. Default values
    2. Configuration files
    3. Environment variables
    
    Configuration is loaded in the order above, with later sources
    overriding earlier ones.
    """
    
    # Default configuration values
    DEFAULT_CONFIG = {
        "paths": {
            "config": "config/production.yml",
            "output": "output",
            "logs": "logs",
            "cache": "cache",
            "data": "data"
        },
        "api": {
            "timeout": 30,
            "retries": 3,
            "retry_delay": 2
        },
        "discovery": {
            "batch_size": 10,
            "max_results": 100
        },
        "validation": {
            "min_score": 0.5,
            "timeout": 60
        },
        "leak_detection": {
            "threshold": 0.7,
            "min_monthly_waste": 1000
        },
        "logging": {
            "level": "INFO",
            "console": True,
            "file": True
        }
    }
    
    # Environment variable prefix
    ENV_PREFIX = "ARCO_"
    
    def __init__(self, config_path: Optional[str] = None, load_env: bool = True):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the main configuration file.
            load_env: Whether to load environment variables from .env file.
        """
        # Load environment variables from .env file if requested
        if load_env:
            load_dotenv()
        
        # Start with default configuration
        self.config = self.DEFAULT_CONFIG.copy()
        
        # Determine config path
        self.config_path = config_path or os.environ.get(
            f"{self.ENV_PREFIX}CONFIG_PATH", 
            self.DEFAULT_CONFIG["paths"]["config"]
        )
        
        # Load configuration from file
        self._load_from_file()
        
        # Override with environment variables
        self._load_from_env()
        
        # Ensure required directories exist
        self.ensure_directories()
        
        logger.debug(f"Configuration initialized: {self.config_path}")
    
    def _load_from_file(self):
        """Load configuration from file."""
        try:
            loader = ConfigLoader(self.config_path)
            file_config = loader.config
            
            # Merge file configuration with current configuration
            self._merge_configs(self.config, file_config)
            logger.debug(f"Loaded configuration from {self.config_path}")
        except Exception as e:
            logger.warning(f"Error loading configuration from {self.config_path}: {e}")
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # Get all environment variables with the prefix
        for key, value in os.environ.items():
            if key.startswith(self.ENV_PREFIX):
                # Remove prefix and convert to lowercase
                config_key = key[len(self.ENV_PREFIX):].lower()
                
                # Convert dot notation to nested keys
                if "." in config_key:
                    self._set_nested_value(self.config, config_key.split("."), value)
                else:
                    self.config[config_key] = self._convert_value(value)
    
    def _set_nested_value(self, config: Dict[str, Any], keys: List[str], value: Any):
        """
        Set a nested value in the configuration.
        
        Args:
            config: Configuration dictionary.
            keys: List of keys representing the path to the value.
            value: Value to set.
        """
        if len(keys) == 1:
            config[keys[0]] = self._convert_value(value)
            return
        
        key = keys[0]
        if key not in config or not isinstance(config[key], dict):
            config[key] = {}
        
        self._set_nested_value(config[key], keys[1:], value)
    
    def _convert_value(self, value: str) -> Union[str, int, float, bool]:
        """
        Convert string value to appropriate type.
        
        Args:
            value: String value to convert.
            
        Returns:
            Converted value.
        """
        # Try to convert to boolean
        if value.lower() in ("true", "yes", "y", "1"):
            return True
        if value.lower() in ("false", "no", "n", "0"):
            return False
        
        # Try to convert to integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try to convert to float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def _merge_configs(self, target: Dict[str, Any], source: Dict[str, Any]):
        """
        Recursively merge source configuration into target configuration.
        
        Args:
            target: Target configuration dictionary.
            source: Source configuration dictionary.
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_configs(target[key], value)
            else:
                target[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (supports dot notation for nested keys).
            default: Default value if key is not found.
            
        Returns:
            Configuration value.
        """
        if "." in key:
            parts = key.split(".")
            value = self.config
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return default
            return value
        
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (supports dot notation for nested keys).
            value: Value to set.
        """
        if "." in key:
            self._set_nested_value(self.config, key.split("."), value)
        else:
            self.config[key] = value
    
    def ensure_directories(self):
        """Ensure that required directories exist."""
        for dir_key in ["output", "logs", "cache", "data"]:
            path = self.get(f"paths.{dir_key}")
            if path:
                Path(path).mkdir(parents=True, exist_ok=True)
                logger.debug(f"Ensured directory exists: {path}")
    
    def reload(self):
        """Reload configuration from file and environment."""
        # Reset to defaults
        self.config = self.DEFAULT_CONFIG.copy()
        
        # Reload from file and environment
        self._load_from_file()
        self._load_from_env()
        
        logger.debug("Configuration reloaded")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Get the complete configuration as a dictionary.
        
        Returns:
            Configuration dictionary.
        """
        return self.config.copy()


# Global configuration instance
_config_instance = None

def get_config(config_path: Optional[str] = None, load_env: bool = True) -> ConfigManager:
    """
    Get the global configuration instance.
    
    Args:
        config_path: Path to the main configuration file.
        load_env: Whether to load environment variables from .env file.
        
    Returns:
        ConfigManager instance.
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager(config_path, load_env)
    return _config_instance