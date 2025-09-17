"""
Test module for the main entry point.

This module contains tests for the main entry point of the ARCO system.
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import main
from arco.pipelines import StandardPipeline, AdvancedPipeline

@patch('arco.pipelines.StandardPipeline')
@patch('arco.pipelines.AdvancedPipeline')
def test_main_standard_pipeline(mock_standard_pipeline, mock_advanced_pipeline):
    """Test running the main module with the standard pipeline."""
    # Mock the pipeline instance
    pipeline_instance = MagicMock()
    mock_standard_pipeline.return_value = pipeline_instance
    pipeline_instance.run.return_value = [MagicMock(), MagicMock()]
    
    # Mock sys.argv
    with patch.object(sys, 'argv', ['main.py', 'standard', 'test query']):
        # Run the main function
        main.main()
        
        # Check that the standard pipeline was created
        mock_standard_pipeline.assert_called_once()
        
        # Check that the pipeline was run with the correct query
        pipeline_instance.run.assert_called_once_with('test query')
        
        # Check that the advanced pipeline was not created
        mock_advanced_pipeline.assert_not_called()

@patch('arco.pipelines.StandardPipeline')
@patch('arco.pipelines.AdvancedPipeline')
def test_main_advanced_pipeline(mock_standard_pipeline, mock_advanced_pipeline):
    """Test running the main module with the advanced pipeline."""
    # Mock the pipeline instance
    pipeline_instance = MagicMock()
    mock_advanced_pipeline.return_value = pipeline_instance
    pipeline_instance.run.return_value = [MagicMock(), MagicMock()]
    
    # Mock sys.argv
    with patch.object(sys, 'argv', ['main.py', 'advanced', 'test query']):
        # Run the main function
        main.main()
        
        # Check that the advanced pipeline was created
        mock_advanced_pipeline.assert_called_once()
        
        # Check that the pipeline was run with the correct query
        pipeline_instance.run.assert_called_once_with('test query')
        
        # Check that the standard pipeline was not created
        mock_standard_pipeline.assert_not_called()

@patch('arco.pipelines.StandardPipeline')
@patch('arco.pipelines.AdvancedPipeline')
def test_main_with_domains(mock_standard_pipeline, mock_advanced_pipeline):
    """Test running the main module with a list of domains."""
    # Mock the pipeline instance
    pipeline_instance = MagicMock()
    mock_standard_pipeline.return_value = pipeline_instance
    pipeline_instance.run.return_value = [MagicMock(), MagicMock()]
    
    # Mock sys.argv
    with patch.object(sys, 'argv', ['main.py', 'standard', '--domains', 'example.com,example.org']):
        # Run the main function
        main.main()
        
        # Check that the standard pipeline was created
        mock_standard_pipeline.assert_called_once()
        
        # Check that the pipeline was run with the correct domains
        pipeline_instance.run.assert_called_once_with(['example.com', 'example.org'])

@patch('arco.pipelines.StandardPipeline')
@patch('arco.pipelines.AdvancedPipeline')
def test_main_with_limit(mock_standard_pipeline, mock_advanced_pipeline):
    """Test running the main module with a limit."""
    # Mock the pipeline instance
    pipeline_instance = MagicMock()
    mock_standard_pipeline.return_value = pipeline_instance
    pipeline_instance.run.return_value = [MagicMock(), MagicMock()]
    
    # Mock sys.argv
    with patch.object(sys, 'argv', ['main.py', 'standard', 'test query', '--limit', '5']):
        # Run the main function
        main.main()
        
        # Check that the standard pipeline was created
        mock_standard_pipeline.assert_called_once()
        
        # Check that the pipeline was run with the correct query
        pipeline_instance.run.assert_called_once_with('test query', limit=5)

@patch('arco.pipelines.StandardPipeline')
@patch('arco.pipelines.AdvancedPipeline')
def test_main_with_output(mock_standard_pipeline, mock_advanced_pipeline):
    """Test running the main module with an output file."""
    # Mock the pipeline instance
    pipeline_instance = MagicMock()
    mock_standard_pipeline.return_value = pipeline_instance
    pipeline_instance.run.return_value = [MagicMock(), MagicMock()]
    
    # Mock open
    mock_open_obj = MagicMock()
    with patch('builtins.open', mock_open_obj):
        # Mock sys.argv
        with patch.object(sys, 'argv', ['main.py', 'standard', 'test query', '--output', 'results.json']):
            # Run the main function
            main.main()
            
            # Check that the standard pipeline was created
            mock_standard_pipeline.assert_called_once()
            
            # Check that the pipeline was run with the correct query
            pipeline_instance.run.assert_called_once_with('test query')
            
            # Check that the output file was opened
            mock_open_obj.assert_called_once_with('results.json', 'w')

@patch('arco.pipelines.StandardPipeline')
@patch('arco.pipelines.AdvancedPipeline')
def test_main_invalid_pipeline(mock_standard_pipeline, mock_advanced_pipeline):
    """Test running the main module with an invalid pipeline."""
    # Mock sys.argv
    with patch.object(sys, 'argv', ['main.py', 'invalid_pipeline', 'test query']):
        # Run the main function and check for SystemExit
        with pytest.raises(SystemExit):
            main.main()
        
        # Check that no pipeline was created
        mock_standard_pipeline.assert_not_called()
        mock_advanced_pipeline.assert_not_called()

@patch('arco.pipelines.StandardPipeline')
@patch('arco.pipelines.AdvancedPipeline')
def test_main_no_arguments(mock_standard_pipeline, mock_advanced_pipeline):
    """Test running the main module with no arguments."""
    # Mock sys.argv
    with patch.object(sys, 'argv', ['main.py']):
        # Run the main function and check for SystemExit
        with pytest.raises(SystemExit):
            main.main()
        
        # Check that no pipeline was created
        mock_standard_pipeline.assert_not_called()
        mock_advanced_pipeline.assert_not_called()

if __name__ == "__main__":
    # Run the tests
    pytest.main(["-v", __file__])