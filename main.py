#!/usr/bin/env python3
"""
ARCO - Customer Acquisition and Revenue Optimization System
Main entry point for the ARCO system.
"""

import argparse
import logging
import sys
import asyncio
from pathlib import Path
from typing import List, Optional

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/arco.main.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("arco.main")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="ARCO - Customer Acquisition and Revenue Optimization System"
    )
    parser.add_argument(
        "--config", 
        type=str, 
        default="config/production.yml",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--pipeline", 
        type=str, 
        choices=["standard", "advanced"], 
        default="standard",
        help="Pipeline type to run"
    )
    parser.add_argument(
        "--input", 
        type=str, 
        help="Input file with domains or companies, or search query for advanced pipeline"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default=None,
        help="Output file for results (default: auto-generated in output/ directory)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Limit the number of results (for search queries in advanced pipeline)"
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Enable debug logging"
    )
    
    return parser.parse_args()

from arco.core.container import get_container
from arco.core.service_configuration import get_configured_container

async def run_pipeline(pipeline_type: str, config_path: str, input_data: Optional[str], 
                      output_path: Optional[str], limit: int = 20):
    """
    Run the specified pipeline with the given parameters.
    
    Args:
        pipeline_type: Type of pipeline to run ('standard' or 'advanced')
        config_path: Path to the configuration file
        input_data: Input file path or search query
        output_path: Output file path
        limit: Maximum number of results for search queries
    """
    logger.info(f"Running {pipeline_type} pipeline")
    
    container = get_configured_container()

    # Import and initialize the appropriate pipeline
    if pipeline_type == "standard":
        pipeline = container.resolve(StandardPipeline)
    else:
        pipeline = container.resolve(AdvancedPipeline)
    
    # Run the pipeline
    if input_data:
        # Check if input is a file or a search query
        if Path(input_data).exists():
            logger.info(f"Using input file: {input_data}")
            results = pipeline.run_from_file(input_data, output_path)
        else:
            # For advanced pipeline, treat as search query
            if pipeline_type == "advanced":
                logger.info(f"Using search query: {input_data} (limit: {limit})")
                results = pipeline.run(input_data)
            else:
                logger.error(f"Input file not found: {input_data}")
                return None
    else:
        # Run with default settings
        logger.info("Running with default settings")
        results = pipeline.run([])
    
    # Save results if not already saved by run_from_file
    if results and output_path:
        pipeline.save_results(results, output_path)
    
    # Display statistics
    stats = pipeline.get_stats()
    logger.info("Pipeline execution statistics:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")
    
    return results

def main():
    """Main entry point for the ARCO system."""
    args = parse_arguments()
    
    # Configure logging level
    if args.debug:
        logging.getLogger("arco").setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    # Ensure required directories exist
    Path("logs").mkdir(exist_ok=True)
    Path("output").mkdir(exist_ok=True)
    
    logger.info(f"Starting ARCO with pipeline: {args.pipeline}")
    logger.info(f"Using configuration from: {args.config}")
    
    try:
        # Run the pipeline
        results = asyncio.run(run_pipeline(
            pipeline_type=args.pipeline,
            config_path=args.config,
            input_data=args.input,
            output_path=args.output,
            limit=args.limit
        ))
        
        if results:
            logger.info(f"Pipeline execution completed successfully")
        else:
            logger.warning("Pipeline execution completed with no results")
        
    except Exception as e:
        logger.exception(f"Error during pipeline execution: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())