"""
Settings for ARCO.

This module contains settings and configuration utilities for the ARCO system.
It provides a simplified interface to the ConfigManager for backward compatibility.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

from .config_manager import get_config

def get_config_path() -> str:
    """
    Get the configuration path from environment or default.
    
    Returns:
        Path to configuration file.
    """
    return get_config().get("paths.config")

def get_output_dir() -> str:
    """
    Get the output directory from environment or default.
    
    Returns:
        Path to output directory.
    """
    return get_config().get("paths.output")

def get_log_dir() -> str:
    """
    Get the log directory from environment or default.
    
    Returns:
        Path to log directory.
    """
    return get_config().get("paths.logs")

def is_debug_mode() -> bool:
    """
    Check if debug mode is enabled.
    
    Returns:
        True if debug mode is enabled, False otherwise.
    """
    return get_config().get("logging.level", "").upper() == "DEBUG"

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from file.
    
    Args:
        config_path: Path to configuration file.
        
    Returns:
        Dictionary with configuration.
    """
    if config_path is not None:
        # Reinitialize config with new path
        return get_config(config_path).to_dict()
    
    return get_config().to_dict()

def ensure_directories():
    """Ensure that required directories exist."""
    get_config().ensure_directories()