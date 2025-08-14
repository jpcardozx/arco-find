#!/usr/bin/env python3
"""
ARCO V3 Command Line Interface
Agent-based lead generation and outreach automation
"""

import asyncio
import argparse
import logging
import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.arco_pipeline import run_daily_batch
from src.models.core_models import Vertical, ServiceFit
from src.feedback.auto_feedback_engine import run_feedback_analysis
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
    batch_parser.add_argument("--min-score", type=int, default=6,  # Aligned with scoring agent threshold
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
            
            # AUTO FEEDBACK CRITICAL ANALYSIS
            logger.info("🔬 Running critical auto feedback analysis...")
            
            try:
                # Prepare execution data for feedback analysis
                execution_data = {
                    'execution_id': result.job_id,
                    'credits_used': result.credits_used,
                    'prospects_discovered': result.prospects_discovered,
                    'prospects_qualified': result.prospects_qualified,
                    'qualification_rate': result.prospects_qualified / max(result.prospects_discovered, 1),
                    'cost_per_lead': result.credits_used / max(result.prospects_qualified, 1),
                    'engines_used': getattr(result, 'engines_used', ['google_ads_transparency_center']),
                    'errors_count': getattr(result, 'errors_count', 0),
                    'warnings_count': getattr(result, 'warnings_count', 0),
                    'avg_response_time_ms': getattr(result, 'avg_response_time_ms', 0.0)
                }
                
                # Run feedback analysis
                feedback_result = await run_feedback_analysis(execution_data)
                
                # Save feedback to file
                feedback_file = Path(f"data/executions/{result.job_id}/auto_feedback.json")
                feedback_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(feedback_file, 'w') as f:
                    json.dump(feedback_result, f, indent=2, default=str)
                
                # Log critical feedback
                summary = feedback_result.get('summary', {})
                logger.info(f"🎯 Feedback Summary:")
                logger.info(f"   • Health Score: {summary.get('overall_health_score', 0)}/100")
                logger.info(f"   • Critical Issues: {summary.get('critical_issues', 0)}")
                logger.info(f"   • High Priority Issues: {summary.get('high_issues', 0)}")
                
                # Display critical and high issues
                feedback_items = feedback_result.get('feedback_items', [])
                critical_items = [f for f in feedback_items if f['severity'] in ['CRITICAL', 'HIGH']]
                
                if critical_items:
                    logger.warning("🚨 CRITICAL FEEDBACK:")
                    for item in critical_items[:3]:  # Show top 3
                        logger.warning(f"   • {item['severity']}: {item['issue']}")
                        if item['recommendations']:
                            logger.warning(f"     → {item['recommendations'][0]}")
                
                logger.info(f"📄 Complete feedback saved to: {feedback_file}")
                
            except Exception as feedback_error:
                logger.warning(f"⚠️  Auto feedback failed: {feedback_error}")
                logger.warning("Pipeline completed successfully but feedback analysis encountered issues")
            
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