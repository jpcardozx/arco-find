#!/usr/bin/env python3
"""
Test script for the Enhanced CSV Prospect Adapter.

This script tests the new batch processing, rate limiting, and integration features
of the enhanced CSV adapter.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from arco.adapters.csv_prospect_adapter import (
    EnhancedCSVProspectAdapter, 
    BatchProcessingConfig,
    load_all_apollo_csvs_async,
    load_all_apollo_csvs
)
from arco.utils.logger import get_logger

logger = get_logger(__name__)


async def test_single_csv_async():
    """Test processing a single CSV file asynchronously."""
    logger.info("🧪 Testing single CSV file processing (async)")
    
    # Find first Apollo CSV file
    csv_files = list(Path("arco").glob("apollo-*.csv"))
    if not csv_files:
        logger.error("No Apollo CSV files found for testing")
        return False
    
    test_file = csv_files[0]
    logger.info(f"📄 Testing with file: {test_file}")
    
    # Create config for testing
    config = BatchProcessingConfig(
        batch_size=10,  # Small batch for testing
        rate_limit_delay=0.05,  # Fast for testing
        enable_progress_tracking=True,
        enable_duplicate_detection=True
    )
    
    try:
        # Create adapter and process
        adapter = EnhancedCSVProspectAdapter(str(test_file), config)
        prospects, stats = await adapter.load_prospects_async()
        
        # Verify results
        logger.info(f"✅ Successfully processed {len(prospects)} prospects")
        logger.info(f"📊 Success rate: {stats.get_success_rate():.1f}%")
        logger.info(f"⏱️  Processing time: {stats.processing_time:.2f}s")
        logger.info(f"📦 Batches processed: {stats.batches_processed}")
        
        # Get processing report
        report = adapter.get_processing_report()
        logger.info(f"📋 Report session ID: {report['session_id']}")
        
        return len(prospects) > 0
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


def test_single_csv_sync():
    """Test processing a single CSV file synchronously."""
    logger.info("🧪 Testing single CSV file processing (sync)")
    
    # Find first Apollo CSV file
    csv_files = list(Path("arco").glob("apollo-*.csv"))
    if not csv_files:
        logger.error("No Apollo CSV files found for testing")
        return False
    
    test_file = csv_files[0]
    logger.info(f"📄 Testing with file: {test_file}")
    
    # Create config for testing
    config = BatchProcessingConfig(
        batch_size=15,  # Small batch for testing
        rate_limit_delay=0.02,  # Fast for testing
        enable_progress_tracking=True,
        enable_duplicate_detection=True
    )
    
    try:
        # Create adapter and process
        adapter = EnhancedCSVProspectAdapter(str(test_file), config)
        prospects = adapter.load_prospects()
        
        # Verify results
        logger.info(f"✅ Successfully processed {len(prospects)} prospects")
        
        # Check some prospect data
        if prospects:
            sample_prospect = prospects[0]
            logger.info(f"📋 Sample prospect: {sample_prospect.company_name} ({sample_prospect.domain})")
            logger.info(f"🏭 Industry: {sample_prospect.industry}")
            logger.info(f"👥 Employees: {sample_prospect.employee_count}")
            logger.info(f"🔧 Technologies: {len(sample_prospect.technologies)}")
        
        return len(prospects) > 0
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


async def test_all_csvs_async():
    """Test processing all Apollo CSV files asynchronously."""
    logger.info("🧪 Testing all Apollo CSV files processing (async)")
    
    # Create config for testing
    config = BatchProcessingConfig(
        batch_size=20,
        rate_limit_delay=0.1,
        enable_progress_tracking=True,
        enable_duplicate_detection=True
    )
    
    try:
        # Process all CSV files
        prospects, report = await load_all_apollo_csvs_async("arco", config)
        
        # Verify results
        logger.info(f"✅ Successfully processed all CSV files")
        logger.info(f"📊 Total prospects: {len(prospects)}")
        
        # Log summary from report
        summary = report.get("session_summary", {})
        logger.info(f"📁 Files processed: {summary.get('files_processed', 0)}")
        logger.info(f"🔄 Duplicates removed: {summary.get('global_duplicates_removed', 0)}")
        logger.info(f"📈 Success rate: {summary.get('overall_success_rate', 0):.1f}%")
        logger.info(f"⏱️  Total time: {summary.get('total_processing_time', 0):.2f}s")
        
        return len(prospects) > 0
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


def test_all_csvs_sync():
    """Test processing all Apollo CSV files synchronously."""
    logger.info("🧪 Testing all Apollo CSV files processing (sync)")
    
    # Create config for testing
    config = BatchProcessingConfig(
        batch_size=25,
        rate_limit_delay=0.05,
        enable_progress_tracking=True,
        enable_duplicate_detection=True
    )
    
    try:
        # Process all CSV files
        prospects = load_all_apollo_csvs("arco", config)
        
        # Verify results
        logger.info(f"✅ Successfully processed all CSV files")
        logger.info(f"📊 Total prospects: {len(prospects)}")
        
        # Analyze prospect data
        if prospects:
            industries = {}
            countries = {}
            tech_counts = {}
            
            for prospect in prospects:
                # Count industries
                if prospect.industry:
                    industries[prospect.industry] = industries.get(prospect.industry, 0) + 1
                
                # Count countries
                if prospect.country:
                    countries[prospect.country] = countries.get(prospect.country, 0) + 1
                
                # Count technologies
                for tech in prospect.technologies:
                    tech_counts[tech.category] = tech_counts.get(tech.category, 0) + 1
            
            # Log top categories
            logger.info("📊 Data Analysis:")
            logger.info(f"   Top industries: {sorted(industries.items(), key=lambda x: x[1], reverse=True)[:3]}")
            logger.info(f"   Top countries: {sorted(countries.items(), key=lambda x: x[1], reverse=True)[:3]}")
            logger.info(f"   Top tech categories: {sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:3]}")
        
        return len(prospects) > 0
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


async def run_all_tests():
    """Run all tests."""
    logger.info("🚀 Starting Enhanced CSV Adapter Tests")
    logger.info("=" * 60)
    
    tests = [
        ("Single CSV Async", test_single_csv_async()),
        ("Single CSV Sync", test_single_csv_sync()),
        ("All CSVs Async", test_all_csvs_async()),
        ("All CSVs Sync", test_all_csvs_sync())
    ]
    
    results = []
    
    for test_name, test_coro in tests:
        logger.info(f"\n🧪 Running: {test_name}")
        logger.info("-" * 40)
        
        try:
            if asyncio.iscoroutine(test_coro):
                result = await test_coro
            else:
                result = test_coro
            
            results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{status}: {test_name}")
            
        except Exception as e:
            results.append((test_name, False))
            logger.error(f"❌ FAILED: {test_name} - {e}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📋 TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"   {status}: {test_name}")
    
    logger.info(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Enhanced CSV Adapter is working correctly.")
        return True
    else:
        logger.error("💥 Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    # Run tests
    success = asyncio.run(run_all_tests())
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)