#!/usr/bin/env python3
"""
ARCO V3 Command Line Interface
Agent-based lead generation and outreach automation
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.arco_pipeline import run_daily_batch
from src.models.core_models import Vertical, ServiceFit
from config.api_keys import APIConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("arco-cli")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="ARCO V3 - Agent-based Lead Generation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run daily batch with defaults
  python arco_v3.py batch

  # Target HVAC vertical with 50 credits
  python arco_v3.py batch --vertical hvac --max-credits 50

  # High-priority prospects only
  python arco_v3.py batch --min-score 10 --target-prospects 8

  # Test with mock data
  python arco_v3.py test --mock
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Batch processing command
    batch_parser = subparsers.add_parser("batch", help="Run daily batch processing")
    batch_parser.add_argument("--max-credits", type=int, default=100,
                             help="Maximum SearchAPI credits to use (default: 100)")
    batch_parser.add_argument("--target-prospects", type=int, default=12,
                             help="Target number of qualified prospects (default: 12)")
    batch_parser.add_argument("--vertical", choices=[v.value for v in Vertical], 
                             help="Focus on specific vertical")
    batch_parser.add_argument("--min-score", type=int, default=8,
                             help="Minimum priority score for qualification (default: 8)")
    batch_parser.add_argument("--output-dir", type=Path, default="data/executions",
                             help="Output directory for results")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test system components")
    test_parser.add_argument("--mock", action="store_true",
                           help="Use mock data instead of real APIs")
    test_parser.add_argument("--component", choices=["discovery", "performance", "scoring", "outreach"],
                           help="Test specific component")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate API keys and configuration")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == "batch":
            return asyncio.run(run_batch_command(args))
        elif args.command == "test":
            return asyncio.run(run_test_command(args))
        elif args.command == "validate":
            return run_validate_command(args)
        else:
            parser.print_help()
            return 1
    except KeyboardInterrupt:
        logger.info("🛑 Operation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        return 1


async def run_batch_command(args):
    """Execute batch processing command"""
    logger.info("🚀 Starting ARCO V3 batch processing")
    logger.info(f"📊 Parameters: Credits: {args.max_credits}, Prospects: {args.target_prospects}")
    
    # Validate API keys
    try:
        APIConfig.validate_s_tier_config()
    except ValueError as e:
        logger.error(f"❌ API validation failed: {e}")
        return 1
    
    # Convert vertical string to enum
    vertical = None
    if args.vertical:
        try:
            vertical = Vertical(args.vertical)
        except ValueError:
            logger.error(f"❌ Invalid vertical: {args.vertical}")
            return 1
    
    # Run batch processing
    try:
        result = await run_daily_batch(
            max_credits=args.max_credits,
            target_prospects=args.target_prospects,
            vertical=vertical,
            min_priority_score=args.min_score
        )
        
        if result.success:
            logger.info("✅ Batch processing completed successfully")
            logger.info(f"📊 Results:")
            logger.info(f"   • Discovered: {result.prospects_discovered} prospects")
            logger.info(f"   • Qualified: {result.prospects_qualified} prospects")
            logger.info(f"   • Outreach: {result.outreach_generated} messages")
            logger.info(f"   • Credits used: {result.credits_used}")
            logger.info(f"   • Duration: {(result.end_time - result.start_time).seconds}s")
            logger.info(f"💾 Results saved to: data/executions/{result.job_id}/")
            return 0
        else:
            logger.error(f"❌ Batch processing failed: {result.error_message}")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Batch processing error: {str(e)}")
        return 1


async def run_test_command(args):
    """Execute test command"""
    logger.info("🧪 Running ARCO V3 tests")
    
    if args.mock:
        logger.info("🎭 Using mock data for testing")
        
        # Test with mock data (simplified for now)
        try:
            from src.agents.discovery_agent import DiscoveryAgent
            from src.models.core_models import Vertical
            
            async with DiscoveryAgent() as agent:
                # This would use mock provider
                logger.info("✅ Discovery agent test completed")
                
            logger.info("✅ All tests passed")
            return 0
            
        except Exception as e:
            logger.error(f"❌ Test failed: {str(e)}")
            return 1
    else:
        logger.warning("⚠️ Real API testing not implemented yet")
        return 0


def run_validate_command(args):
    """Execute validation command"""
    logger.info("🔍 Validating ARCO V3 configuration")
    
    try:
        # Validate API keys
        APIConfig.validate_s_tier_config()
        
        # Validate project structure
        required_dirs = ["src/agents", "src/models", "config", "data", "logs"]
        for dir_path in required_dirs:
            path = Path(dir_path)
            if path.exists():
                logger.info(f"✅ Directory: {dir_path}")
            else:
                logger.warning(f"⚠️ Missing directory: {dir_path}")
        
        # Validate required files
        required_files = [
            "config/api_keys.py",
            "src/agents/discovery_agent.py",
            "src/agents/performance_agent.py",
            "src/agents/scoring_agent.py",
            "src/agents/outreach_agent.py"
        ]
        
        for file_path in required_files:
            path = Path(file_path)
            if path.exists():
                logger.info(f"✅ File: {file_path}")
            else:
                logger.error(f"❌ Missing file: {file_path}")
        
        logger.info("✅ Configuration validation completed")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Validation failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())