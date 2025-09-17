#!/usr/bin/env python3
"""
Validation script for the ARCO project refactoring.
This script verifies that all requirements have been met after the refactoring.
"""

import os
import sys
import subprocess
import logging
import importlib
import importlib.util
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("validation")

class ValidationResult:
    """Class to store validation results."""
    
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
    
    def add_pass(self, test_name: str, message: str = ""):
        """Add a passed test."""
        self.passed.append((test_name, message))
        logger.info(f"✅ PASS: {test_name} {message}")
    
    def add_fail(self, test_name: str, message: str = ""):
        """Add a failed test."""
        self.failed.append((test_name, message))
        logger.error(f"❌ FAIL: {test_name} {message}")
    
    def add_warning(self, test_name: str, message: str = ""):
        """Add a warning."""
        self.warnings.append((test_name, message))
        logger.warning(f"⚠️ WARNING: {test_name} {message}")
    
    def summary(self) -> str:
        """Generate a summary of the validation results."""
        total = len(self.passed) + len(self.failed)
        return (
            f"\nValidation Summary:\n"
            f"  Total Tests: {total}\n"
            f"  Passed: {len(self.passed)}\n"
            f"  Failed: {len(self.failed)}\n"
            f"  Warnings: {len(self.warnings)}\n"
        )


def run_command(command: List[str]) -> Tuple[int, str, str]:
    """Run a command and return the exit code, stdout, and stderr."""
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(timeout=300)  # 5 minute timeout
        return process.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        process.kill()
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def run_tests(result: ValidationResult) -> None:
    """Run all tests and record the results."""
    logger.info("Running tests...")
    
    # Check if pytest is installed
    returncode, _, _ = run_command(["pytest", "--version"])
    if returncode != 0:
        result.add_fail("pytest_installation", "pytest is not installed")
        return
    
    # Run all tests
    returncode, stdout, stderr = run_command(["pytest", "-v"])
    
    if returncode == 0:
        result.add_pass("all_tests", "All tests passed")
    else:
        result.add_fail("all_tests", "Some tests failed")
        logger.error(f"Test output:\n{stdout}\n{stderr}")


def check_directory_structure(result: ValidationResult) -> None:
    """Check that the directory structure meets the requirements."""
    logger.info("Checking directory structure...")
    
    # Check for required directories
    required_dirs = [
        "arco",
        "arco/pipelines",
        "arco/engines",
        "arco/models",
        "arco/integrations",
        "arco/config",
        "arco/utils",
        "tests",
        "docs",
        "config",
    ]
    
    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            result.add_pass(f"directory_{dir_path}", f"Directory {dir_path} exists")
        else:
            result.add_fail(f"directory_{dir_path}", f"Directory {dir_path} does not exist")
    
    # Check for required files
    required_files = [
        "main.py",
        "requirements.txt",
        "setup.py",
        ".env.template",
        "README.md",
    ]
    
    for file_path in required_files:
        if os.path.isfile(file_path):
            result.add_pass(f"file_{file_path}", f"File {file_path} exists")
        else:
            result.add_fail(f"file_{file_path}", f"File {file_path} does not exist")


def check_imports(result: ValidationResult) -> None:
    """Check that imports work correctly."""
    logger.info("Checking imports...")
    
    # List of modules to check
    modules_to_check = [
        "arco.pipelines.standard_pipeline",
        "arco.pipelines.advanced_pipeline",
        "arco.engines.simplified_engine",
        "arco.engines.discovery_engine",
        "arco.engines.leak_engine",
        "arco.engines.validator_engine",
    ]
    
    for module_name in modules_to_check:
        try:
            importlib.import_module(module_name)
            result.add_pass(f"import_{module_name}", f"Successfully imported {module_name}")
        except ImportError as e:
            result.add_fail(f"import_{module_name}", f"Failed to import {module_name}: {e}")


def check_cli_compatibility(result: ValidationResult) -> None:
    """Check that CLI commands are compatible with the refactored code."""
    logger.info("Checking CLI compatibility...")
    
    # Test standard pipeline with default settings
    returncode, stdout, stderr = run_command(["python", "main.py", "--pipeline", "standard", "--debug"])
    if returncode == 0:
        result.add_pass("cli_standard_pipeline", "Standard pipeline runs successfully")
    else:
        result.add_fail("cli_standard_pipeline", f"Standard pipeline failed: {stderr}")
    
    # Test advanced pipeline with default settings
    returncode, stdout, stderr = run_command(["python", "main.py", "--pipeline", "advanced", "--debug"])
    if returncode == 0:
        result.add_pass("cli_advanced_pipeline", "Advanced pipeline runs successfully")
    else:
        result.add_fail("cli_advanced_pipeline", f"Advanced pipeline failed: {stderr}")
    
    # Test with custom config
    if os.path.exists("config/production.yml"):
        returncode, stdout, stderr = run_command(["python", "main.py", "--config", "config/production.yml", "--debug"])
        if returncode == 0:
            result.add_pass("cli_custom_config", "Custom config works successfully")
        else:
            result.add_fail("cli_custom_config", f"Custom config failed: {stderr}")
    else:
        result.add_warning("cli_custom_config", "config/production.yml does not exist, skipping test")


def check_requirements_met(result: ValidationResult) -> None:
    """Check that all requirements have been met."""
    logger.info("Checking requirements...")
    
    # Requirement 1: Clean and organized project structure
    if all(os.path.isdir(d) for d in ["arco", "arco/pipelines", "arco/engines", "arco/models"]):
        result.add_pass("req1.1", "Project has a clear directory structure")
    else:
        result.add_fail("req1.1", "Project structure is incomplete")
    
    # Check directory depth
    max_depth = 0
    for root, dirs, files in os.walk("arco"):
        depth = root.count(os.sep)
        max_depth = max(max_depth, depth)
    
    if max_depth <= 3:
        result.add_pass("req1.2", f"Directory depth is {max_depth}, which is <= 3")
    else:
        result.add_fail("req1.2", f"Directory depth is {max_depth}, which is > 3")
    
    # Requirement 2: Legacy code removal
    if os.path.isdir("archive"):
        result.add_pass("req2.1", "Archive directory exists for legacy code")
    else:
        result.add_fail("req2.1", "Archive directory does not exist")
    
    # Requirement 3: Modular structure
    modules = ["arco/pipelines", "arco/engines", "arco/integrations", "arco/models"]
    if all(os.path.isdir(m) for m in modules):
        result.add_pass("req3.1", "Project has modular structure")
    else:
        result.add_fail("req3.1", "Project lacks modular structure")
    
    # Check for main.py as entry point
    if os.path.isfile("main.py"):
        result.add_pass("req3.4", "Project has a clear entry point (main.py)")
    else:
        result.add_fail("req3.4", "Project lacks a clear entry point")
    
    # Requirement 4: Documentation
    if os.path.isdir("docs"):
        doc_files = os.listdir("docs")
        if len(doc_files) > 0:
            result.add_pass("req4.1", f"Documentation exists with {len(doc_files)} files")
        else:
            result.add_fail("req4.1", "Documentation directory is empty")
    else:
        result.add_fail("req4.1", "Documentation directory does not exist")
    
    # Check for README.md
    if os.path.isfile("README.md"):
        result.add_pass("req4.2", "README.md exists")
    else:
        result.add_fail("req4.2", "README.md does not exist")
    
    # Requirement 5: Centralized configuration
    if os.path.isdir("config"):
        config_files = os.listdir("config")
        if len(config_files) > 0:
            result.add_pass("req5.1", f"Configuration directory exists with {len(config_files)} files")
        else:
            result.add_fail("req5.1", "Configuration directory is empty")
    else:
        result.add_fail("req5.1", "Configuration directory does not exist")
    
    # Check for .env.template
    if os.path.isfile(".env.template"):
        result.add_pass("req5.2", ".env.template exists")
    else:
        result.add_fail("req5.2", ".env.template does not exist")
    
    # Check for requirements.txt
    if os.path.isfile("requirements.txt"):
        result.add_pass("req5.3", "requirements.txt exists")
    else:
        result.add_fail("req5.3", "requirements.txt does not exist")
    
    # Requirement 6: Preserved functionality
    # This is partially covered by the CLI compatibility check
    # Additional checks for pipeline functionality
    pipeline_files = ["arco/pipelines/standard_pipeline.py", "arco/pipelines/advanced_pipeline.py"]
    if all(os.path.isfile(f) for f in pipeline_files):
        result.add_pass("req6.1", "Pipeline files exist")
    else:
        result.add_fail("req6.1", "Pipeline files are missing")
    
    # Check for integration files
    if os.path.isdir("arco/integrations"):
        integration_files = os.listdir("arco/integrations")
        if len(integration_files) > 1:  # At least __init__.py and one integration
            result.add_pass("req6.2", f"Integration files exist: {len(integration_files)} files")
        else:
            result.add_fail("req6.2", "Integration files are missing or insufficient")
    else:
        result.add_fail("req6.2", "Integrations directory does not exist")


def main():
    """Main function to run all validation checks."""
    logger.info("Starting validation...")
    result = ValidationResult()
    
    # Run all validation checks
    check_directory_structure(result)
    check_imports(result)
    check_cli_compatibility(result)
    check_requirements_met(result)
    run_tests(result)
    
    # Print summary
    logger.info(result.summary())
    
    # Return exit code based on validation results
    return 1 if result.failed else 0


if __name__ == "__main__":
    sys.exit(main())