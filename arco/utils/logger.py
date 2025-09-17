"""
Logger for ARCO.

This module contains utilities for logging in the ARCO system.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional, Union, Dict
from functools import lru_cache

from arco.config.config_manager import get_config

def setup_logger(
    name: str = "arco",
    level: Optional[Union[int, str]] = None,
    log_file: Optional[str] = None,
    console: Optional[bool] = None
) -> logging.Logger:
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: Logger name.
        level: Logging level. If None, uses the level from configuration.
        log_file: Path to log file. If None, uses the path from configuration.
        console: Whether to log to console. If None, uses the setting from configuration.
        
    Returns:
        Configured logger.
    """
    # Get configuration
    config = get_config()
    
    # Use configuration values if parameters are not provided
    if level is None:
        level_str = config.get("logging.level", "INFO")
        level = getattr(logging, level_str.upper(), logging.INFO)
    elif isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    
    if log_file is None and config.get("logging.file", True):
        log_dir = config.get("paths.logs", "logs")
        log_file = os.path.join(log_dir, f"{name}.log")
    
    if console is None:
        console = config.get("logging.console", True)
    
    # Get the logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        config.get("logging.format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    
    # Create file handler if log_file is provided and logging to file is enabled
    if log_file and config.get("logging.file", True):
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Create console handler if console is True
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


@lru_cache(maxsize=32)
def get_logger(
    name: str = "arco",
    level: Optional[Union[int, str]] = None,
    log_file: Optional[str] = None,
    console: Optional[bool] = None
) -> logging.Logger:
    """
    Get a logger with the specified name and configuration.
    This function is cached to avoid creating multiple loggers with the same name.
    
    Args:
        name: Logger name.
        level: Logging level. If None, uses the level from configuration.
        log_file: Path to log file. If None, uses the path from configuration.
        console: Whether to log to console. If None, uses the setting from configuration.
        
    Returns:
        Configured logger.
    """
    return setup_logger(name=name, level=level, log_file=log_file, console=console)