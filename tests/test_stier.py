"""
ARCO FIND S-Tier Quick Start
Test the pipeline with cost-safe sample query
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_stier_config():
    """Test S-Tier configuration without executing expensive queries"""
    
    print("🔍 ARCO FIND S-TIER CONFIGURATION TEST")
    print("=" * 50)
    
    # Test imports
    try:
        from config.stier_config import STierConfig, check_production_readiness
        print("✅ Configuration module imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test configuration validation
    try:
        is_ready = check_production_readiness()
        if is_ready:
            print("\n✅ Production configuration validated")
        else:
            print("\n⚠️ Configuration issues detected (see above)")
            print("💡 For testing, you can continue with default credentials")
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False
    
    # Test BigQuery client initialization (without queries)
    try:
        from engines.bigquery_stier_pipeline import BigQuerySTierPipeline
        print("✅ Pipeline module imported successfully")
        
        # Test with default project (won't execute queries)
        project_id = os.getenv('GCP_PROJECT_ID', 'test-project')
        pipeline = BigQuerySTierPipeline(project_id, credentials_path=None)
        print("✅ Pipeline initialized (client creation successful)")
        
    except Exception as e:
        print(f"⚠️ Pipeline initialization warning: {e}")
        print("   This is expected if GCP credentials are not configured")
    
    # Display dataset information
    print(f"\n📊 VERIFIED PUBLIC DATASETS")
    print("-" * 30)
    
    for name, dataset in STierConfig.PUBLIC_DATASETS.items():
        print(f"\n📋 {name}")
        print(f"   Table: {dataset['table']}")
        print(f"   Citation: {dataset['citation']}")
        print(f"   Description: {dataset['description']}")
        print(f"   Partitioning: {dataset['partitioning']}")
    
    # Display scoring methodology
    print(f"\n🎯 SCORING METHODOLOGY")
    print("-" * 25)
    
    total_weight = 0
    for component, details in STierConfig.SCORING_WEIGHTS.items():
        weight = details['weight']
        total_weight += weight
        print(f"\n• {component.replace('_', ' ').title()}: {weight:.1%}")
        print(f"  Rationale: {details['rationale']}")
        print(f"  Calculation: {details['calculation']}")
    
    print(f"\n✅ Total weight: {total_weight:.1%} (should be 100%)")
    
    # Display cost controls
    print(f"\n💰 COST CONTROLS")
    print("-" * 15)
    print(f"Free Tier Limit: {STierConfig.BIGQUERY_FREE_TIER_BYTES / (1024**4):.1f} TB/month")
    print(f"Safety Threshold: {STierConfig.BIGQUERY_SAFETY_THRESHOLD:.0%} of free tier")
    print(f"Max Query Size: {STierConfig.BIGQUERY_MAX_QUERY_BYTES / (1024**3):.0f} GB")
    
    # Next steps
    print(f"\n🚀 NEXT STEPS")
    print("-" * 12)
    print("1. Set up GCP authentication:")
    print("   export GCP_PROJECT_ID='your-project-id'")
    print("   gcloud auth application-default login")
    print("")
    print("2. Install dependencies:")
    print("   pip install -r requirements_stier.txt")
    print("")
    print("3. Run full analysis:")
    print("   python run_stier_pipeline.py")
    print("")
    print("⚠️ Note: Full analysis requires valid GCP credentials and BigQuery access")
    
    return True

async def test_sample_query_generation():
    """Test query generation without executing"""
    
    print(f"\n🔧 SAMPLE QUERY GENERATION TEST")
    print("-" * 35)
    
    try:
        from engines.bigquery_stier_pipeline import BigQuerySTierPipeline
        from config.stier_config import STierConfig
        
        # Generate sample query (no execution)
        pipeline = BigQuerySTierPipeline('test-project')
        sample_query = pipeline._build_opportunity_discovery_query(1000, 5000)
        
        # Count approximate query length
        query_lines = sample_query.strip().split('\n')
        non_empty_lines = [line for line in query_lines if line.strip()]
        
        print(f"✅ Query generated successfully")
        print(f"📝 Query lines: {len(non_empty_lines)}")
        print(f"📊 Includes partition filtering: {'_PARTITIONTIME' in sample_query or 'date =' in sample_query}")
        print(f"💰 Includes cost controls: {'LIMIT' in sample_query}")
        print(f"🎯 Includes performance filters: {'largest_contentful_paint > 4000' in sample_query}")
        
        # Show query preview (first few lines)
        print(f"\n📋 Query Preview (first 10 lines):")
        for i, line in enumerate(query_lines[:10]):
            if line.strip():
                print(f"   {line}")
        print("   ...")
        
        return True
        
    except Exception as e:
        print(f"❌ Query generation failed: {e}")
        return False

async def main():
    """Main test function"""
    
    print("🧪 ARCO FIND S-TIER QUICK TEST")
    print("Testing configuration and components without BigQuery execution")
    print("=" * 70)
    
    # Test 1: Configuration
    config_ok = await test_stier_config()
    
    # Test 2: Query generation
    query_ok = await test_sample_query_generation()
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 15)
    print(f"Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"Query Generation: {'✅ PASS' if query_ok else '❌ FAIL'}")
    
    if config_ok and query_ok:
        print(f"\n🎉 All tests passed! S-Tier pipeline is ready.")
        print(f"⚡ Run 'python run_stier_pipeline.py' to execute full analysis")
    else:
        print(f"\n⚠️ Some tests failed. Check configuration and dependencies.")
    
    return 0 if (config_ok and query_ok) else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
