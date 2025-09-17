"""
Environment Variable Manager for ARCO.

This module provides utilities for managing environment variables for the ARCO system.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv, find_dotenv, set_key

logger = logging.getLogger(__name__)

class EnvManager:
    """
    Environment variable manager for ARCO.
    
    This class provides utilities for loading, getting, and setting
    environment variables for the ARCO system.
    """
    
    # Environment variable prefix
    ENV_PREFIX = "ARCO_"
    
    def __init__(self, dotenv_path: Optional[str] = None, load_env: bool = True):
        """
        Initialize the environment variable manager.
        
        Args:
            dotenv_path: Path to the .env file.
            load_env: Whether to load environment variables from .env file.
        """
        self.dotenv_path = dotenv_path or find_dotenv()
        
        # Load environment variables from .env file if requested
        if load_env and self.dotenv_path:
            load_dotenv(self.dotenv_path)
            logger.debug(f"Loaded environment variables from {self.dotenv_path}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get an environment variable.
        
        Args:
            key: Environment variable key (without prefix).
            default: Default value if key is not found.
            
        Returns:
            Environment variable value.
        """
        env_key = f"{self.ENV_PREFIX}{key.upper()}"
        return os.environ.get(env_key, default)
    
    def set(self, key: str, value: str, export: bool = False) -> bool:
        """
        Set an environment variable.
        
        Args:
            key: Environment variable key (without prefix).
            value: Value to set.
            export: Whether to export the variable to the current process.
            
        Returns:
            True if successful, False otherwise.
        """
        env_key = f"{self.ENV_PREFIX}{key.upper()}"
        
        # Set in current process
        if export:
            os.environ[env_key] = value
        
        # Set in .env file if available
        if self.dotenv_path:
            try:
                set_key(self.dotenv_path, env_key, value)
                logger.debug(f"Set environment variable {env_key} in {self.dotenv_path}")
                return True
            except Exception as e:
                logger.error(f"Error setting environment variable {env_key}: {e}")
                return False
        
        return export
    
    def list(self, include_prefix: bool = False) -> Dict[str, str]:
        """
        List all ARCO environment variables.
        
        Args:
            include_prefix: Whether to include the prefix in the keys.
            
        Returns:
            Dictionary of environment variables.
        """
        result = {}
        for key, value in os.environ.items():
            if key.startswith(self.ENV_PREFIX):
                if include_prefix:
                    result[key] = value
                else:
                    result[key[len(self.ENV_PREFIX):]] = value
        return result
    
    def validate_required(self, required_keys: List[str]) -> List[str]:
        """
        Validate that required environment variables are set.
        
        Args:
            required_keys: List of required environment variable keys (without prefix).
            
        Returns:
            List of missing environment variable keys.
        """
        missing = []
        for key in required_keys:
            env_key = f"{self.ENV_PREFIX}{key.upper()}"
            if env_key not in os.environ:
                missing.append(key)
        return missing
    
    def create_template(self, template_path: str, variables: Dict[str, str]) -> bool:
        """
        Create a template .env file.
        
        Args:
            template_path: Path to the template file.
            variables: Dictionary of variables and their descriptions.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            with open(template_path, "w") as f:
                f.write("# ARCO Environment Variables Template\n")
                f.write("# Copy this file to .env and fill in the values\n\n")
                
                for key, description in variables.items():
                    f.write(f"# {description}\n")
                    f.write(f"{self.ENV_PREFIX}{key.upper()}=\n\n")
            
            logger.debug(f"Created environment variable template at {template_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating environment variable template: {e}")
            return False


# Global environment variable manager instance
_env_manager_instance = None

def get_env_manager(dotenv_path: Optional[str] = None, load_env: bool = True) -> EnvManager:
    """
    Get the global environment variable manager instance.
    
    Args:
        dotenv_path: Path to the .env file.
        load_env: Whether to load environment variables from .env file.
        
    Returns:
        EnvManager instance.
    """
    global _env_manager_instance
    if _env_manager_instance is None:
        _env_manager_instance = EnvManager(dotenv_path, load_env)
    return _env_manager_instance