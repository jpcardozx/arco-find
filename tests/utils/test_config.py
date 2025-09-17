"""
Test module for the configuration utilities.

This module contains tests for the configuration utilities.
"""

import os
import pytest
import tempfile
import yaml
from unittest.mock import patch, mock_open
from arco.utils.config import ConfigLoader, EnvLoader

def test_config_loader_load_yaml():
    """Test loading a YAML configuration file."""
    # Create a temporary YAML file
    config_data = {
        "test_key": "test_value",
        "nested": {
            "key1": "value1",
            "key2": "value2"
        },
        "list": [1, 2, 3]
    }
    
    # Mock open to return our test data
    with patch("builtins.open", mock_open(read_data=yaml.dump(config_data))):
        # Load the configuration
        config = ConfigLoader.load_yaml("dummy_path.yml")
        
        # Check the loaded configuration
        assert config["test_key"] == "test_value"
        assert config["nested"]["key1"] == "value1"
        assert config["nested"]["key2"] == "value2"
        assert config["list"] == [1, 2, 3]

def test_config_loader_load_yaml_file_not_found():
    """Test loading a non-existent YAML file."""
    # Mock open to raise FileNotFoundError
    with patch("builtins.open", side_effect=FileNotFoundError()):
        # Load the configuration
        config = ConfigLoader.load_yaml("non_existent.yml")
        
        # Check that an empty dict was returned
        assert config == {}

def test_config_loader_load_yaml_invalid_yaml():
    """Test loading an invalid YAML file."""
    # Mock open to return invalid YAML
    with patch("builtins.open", mock_open(read_data="invalid: yaml: content:")):
        # Load the configuration
        config = ConfigLoader.load_yaml("invalid.yml")
        
        # Check that an empty dict was returned
        assert config == {}

def test_config_loader_merge_configs():
    """Test merging multiple configurations."""
    # Create test configurations
    config1 = {
        "key1": "value1",
        "nested": {
            "key1": "value1",
            "key2": "value2"
        }
    }
    
    config2 = {
        "key2": "value2",
        "nested": {
            "key2": "new_value2",
            "key3": "value3"
        }
    }
    
    # Merge the configurations
    merged = ConfigLoader.merge_configs(config1, config2)
    
    # Check the merged configuration
    assert merged["key1"] == "value1"
    assert merged["key2"] == "value2"
    assert merged["nested"]["key1"] == "value1"
    assert merged["nested"]["key2"] == "new_value2"  # Overwritten by config2
    assert merged["nested"]["key3"] == "value3"

def test_env_loader_load_env():
    """Test loading environment variables."""
    # Create a temporary .env file
    env_content = """
    TEST_VAR1=value1
    TEST_VAR2=value2
    # This is a comment
    TEST_VAR3="quoted value"
    """
    
    # Mock open to return our test data
    with patch("builtins.open", mock_open(read_data=env_content)):
        # Mock os.environ to be a clean dict
        with patch.dict(os.environ, {}, clear=True):
            # Load the environment variables
            EnvLoader.load_env("dummy_path.env")
            
            # Check that the variables were loaded
            assert os.environ["TEST_VAR1"] == "value1"
            assert os.environ["TEST_VAR2"] == "value2"
            assert os.environ["TEST_VAR3"] == "quoted value"

def test_env_loader_load_env_file_not_found():
    """Test loading a non-existent .env file."""
    # Mock open to raise FileNotFoundError
    with patch("builtins.open", side_effect=FileNotFoundError()):
        # Mock os.environ to be a clean dict
        with patch.dict(os.environ, {}, clear=True):
            # Load the environment variables
            EnvLoader.load_env("non_existent.env")
            
            # Check that no variables were loaded
            assert len(os.environ) == 0

def test_env_loader_get_env():
    """Test getting environment variables with defaults."""
    # Mock os.environ
    with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
        # Get existing variable
        value = EnvLoader.get_env("TEST_VAR")
        assert value == "test_value"
        
        # Get non-existent variable with default
        value = EnvLoader.get_env("NON_EXISTENT", default="default_value")
        assert value == "default_value"
        
        # Get non-existent variable without default
        value = EnvLoader.get_env("NON_EXISTENT")
        assert value is None

if __name__ == "__main__":
    # Run the tests
    pytest.main(["-v", __file__])