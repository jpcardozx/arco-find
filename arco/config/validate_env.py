"""
Environment Variable Validation for ARCO.

This module provides utilities for validating environment variables for the ARCO system.
"""

import sys
import logging
from typing import List, Dict, Any, Optional

from .env_manager import get_env_manager

logger = logging.getLogger(__name__)

# Required environment variables for different components
REQUIRED_ENV_VARS = {
    "core": [
        "PATHS_CONFIG",
        "PATHS_OUTPUT",
        "PATHS_LOGS"
    ],
    "api": [
        "API_KEYS_GOOGLE_SEARCH",
        "API_KEYS_GOOGLE_PAGESPEED"
    ],
    "advanced": [
        "API_KEYS_META_ADS"
    ]
}

def validate_environment(components: Optional[List[str]] = None) -> Dict[str, List[str]]:
    """
    Validate that required environment variables are set.
    
    Args:
        components: List of components to validate. If None, validates all components.
        
    Returns:
        Dictionary of missing environment variables by component.
    """
    env_manager = get_env_manager()
    
    if components is None:
        components = list(REQUIRED_ENV_VARS.keys())
    
    missing = {}
    for component in components:
        if component in REQUIRED_ENV_VARS:
            missing_vars = env_manager.validate_required(REQUIRED_ENV_VARS[component])
            if missing_vars:
                missing[component] = missing_vars
    
    return missing

def print_validation_results(missing: Dict[str, List[str]]) -> bool:
    """
    Print validation results.
    
    Args:
        missing: Dictionary of missing environment variables by component.
        
    Returns:
        True if all required environment variables are set, False otherwise.
    """
    if not missing:
        print("✅ All required environment variables are set.")
        return True
    
    print("❌ Missing environment variables:")
    for component, vars in missing.items():
        print(f"  Component: {component}")
        for var in vars:
            print(f"    - ARCO_{var}")
    
    print("\nPlease set these environment variables in your .env file or system environment.")
    print("You can use the .env.template file as a reference.")
    
    return False

def main():
    """Main function for validating environment variables."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate ARCO environment variables")
    parser.add_argument(
        "--components",
        nargs="+",
        choices=list(REQUIRED_ENV_VARS.keys()),
        help="Components to validate"
    )
    
    args = parser.parse_args()
    
    missing = validate_environment(args.components)
    if not print_validation_results(missing):
        sys.exit(1)

if __name__ == "__main__":
    main()