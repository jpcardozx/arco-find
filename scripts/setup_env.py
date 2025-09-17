"""
Setup Environment Variables for ARCO.

This script helps users set up environment variables for the ARCO system.
"""

import os
import sys
import shutil
from pathlib import Path

# Add the parent directory to the path so we can import arco
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from arco.config.env_manager import get_env_manager
from arco.utils.logger import setup_logger

logger = setup_logger("setup_env")

def setup_env():
    """Set up environment variables for ARCO."""
    # Get the environment manager
    env_manager = get_env_manager(load_env=False)
    
    # Check if .env file exists
    dotenv_path = ".env"
    template_path = ".env.template"
    
    if os.path.exists(dotenv_path):
        logger.info(f"Environment file already exists at {dotenv_path}")
        overwrite = input("Do you want to overwrite it? (y/N): ").lower() == "y"
        if not overwrite:
            logger.info("Keeping existing environment file.")
            return
    
    # Check if template exists
    if not os.path.exists(template_path):
        logger.error(f"Template file not found at {template_path}")
        return
    
    # Copy template to .env
    try:
        shutil.copy(template_path, dotenv_path)
        logger.info(f"Created environment file at {dotenv_path} from template")
    except Exception as e:
        logger.error(f"Error creating environment file: {e}")
        return
    
    # Ask user for required variables
    logger.info("Please provide values for the following environment variables:")
    
    # API keys
    google_search_key = input("Google Search API Key (leave empty to skip): ")
    if google_search_key:
        env_manager.set("API_KEYS_GOOGLE_SEARCH", google_search_key, export=True)
    
    google_pagespeed_key = input("Google PageSpeed API Key (leave empty to skip): ")
    if google_pagespeed_key:
        env_manager.set("API_KEYS_GOOGLE_PAGESPEED", google_pagespeed_key, export=True)
    
    meta_ads_key = input("Meta Ads API Key (leave empty to skip): ")
    if meta_ads_key:
        env_manager.set("API_KEYS_META_ADS", meta_ads_key, export=True)
    
    # Paths
    config_path = input("Configuration path (default: config/production.yml): ")
    if config_path:
        env_manager.set("PATHS_CONFIG", config_path, export=True)
    
    output_dir = input("Output directory (default: output): ")
    if output_dir:
        env_manager.set("PATHS_OUTPUT", output_dir, export=True)
    
    logs_dir = input("Logs directory (default: logs): ")
    if logs_dir:
        env_manager.set("PATHS_LOGS", logs_dir, export=True)
    
    # Logging
    log_level = input("Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) (default: INFO): ")
    if log_level:
        env_manager.set("LOGGING_LEVEL", log_level, export=True)
    
    logger.info(f"Environment variables set in {dotenv_path}")
    logger.info("You can edit this file directly to change or add more variables.")

if __name__ == "__main__":
    setup_env()