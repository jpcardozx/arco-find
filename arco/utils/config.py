"""
Configuration utilities for ARCO.

This module provides utilities for loading and managing configuration.
"""

import os
import yaml
from typing import Any, Dict, Optional, Union
from pathlib import Path
from dotenv import load_dotenv

class EnvLoader:
    """Load environment variables from .env file."""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize the environment loader.
        
        Args:
            env_file: Path to .env file. If None, uses .env in the current directory.
        """
        self.env_file = env_file or ".env"
        self._loaded = False
    
    def load(self) -> bool:
        """
        Load environment variables from .env file.
        
        Returns:
            True if the file was loaded successfully, False otherwise.
        """
        if self._loaded:
            return True
        
        if os.path.exists(self.env_file):
            load_dotenv(self.env_file)
            self._loaded = True
            return True
        
        return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get an environment variable.
        
        Args:
            key: Environment variable name.
            default: Default value if the variable is not set.
            
        Returns:
            The environment variable value or the default value.
        """
        self.load()
        return os.environ.get(key, default)


class ConfigLoader:
    """Load configuration from YAML files."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration loader.
        
        Args:
            config_path: Path to configuration file. If None, uses config/production.yml.
        """
        self.config_path = config_path or "config/production.yml"
        self._config = {}
        self._loaded = False
    
    def load(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Returns:
            The loaded configuration.
        """
        if self._loaded:
            return self._config
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    self._config = yaml.safe_load(f) or {}
                self._loaded = True
            except Exception as e:
                print(f"Error loading configuration from {self.config_path}: {e}")
                self._config = {}
        
        return self._config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key. Can be a dot-separated path (e.g., "logging.level").
            default: Default value if the key is not found.
            
        Returns:
            The configuration value or the default value.
        """
        self.load()
        
        # Handle dot notation
        if "." in key:
            parts = key.split(".")
            value = self._config
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return default
            return value
        
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key. Can be a dot-separated path (e.g., "logging.level").
            value: Value to set.
        """
        self.load()
        
        # Handle dot notation
        if "." in key:
            parts = key.split(".")
            config = self._config
            for part in parts[:-1]:
                if part not in config:
                    config[part] = {}
                config = config[part]
            config[parts[-1]] = value
        else:
            self._config[key] = value
    
    def save(self, path: Optional[str] = None) -> bool:
        """
        Save configuration to YAML file.
        
        Args:
            path: Path to save the configuration. If None, uses the original path.
            
        Returns:
            True if the configuration was saved successfully, False otherwise.
        """
        path = path or self.config_path
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, "w") as f:
                yaml.dump(self._config, f, default_flow_style=False)
            return True
        except Exception as e:
            print(f"Error saving configuration to {path}: {e}")
            return False