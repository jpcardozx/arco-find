"""
ARCO SearchAPI - Script de Teste e Demonstração
==============================================

Demonstra como usar os 3 engines do SearchAPI para geração de leads
focados nos nichos e perfil firmográfico da ARCO.

Uso:
python test_searchapi_layers.py --test quick
python test_searchapi_layers.py --test full
python test_searchapi_layers.py --test layer1
"""

import sys
import json
import argparse
import logging
from pathlib import Path
import os
from datetime import datetime
from typing import Dict

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent / "src" / "engines"))

try:
    from searchapi_layer1_seed_generation import SearchAPILayer1SeedGeneration
    from searchapi_layer2_advertiser_consolidation import SearchAPILayer2AdvertiserConsolidation
    from searchapi_layer3_ad_details_analysis import SearchAPILayer3AdDetailsAnalysis
    from searchapi_master_orchestrator import ARCOSearchAPIMasterOrchestrator
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

def setup_logging():
    """Configure logging for test script"""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f'logs/searchapi_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        ]
    )
    
    return logging.getLogger(__name__)

def load_config():
    """Load SearchAPI configuration"""
    
    try:
        config_path = Path("config/discovery_config.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Get API key from environment or config
        api_key = os.getenv('SEARCHAPI_KEY')
        if not api_key:
            api_key = config.get('searchapi_config', {}).get('api_key', '').replace('${SEARCHAPI_KEY}', '')
        
        if not api_key or api_key == '':
            raise ValueError("SearchAPI key not found. Set SEARCHAPI_KEY environment variable.")
        
        return api_key, config.get('searchapi_config', {})
        
    except Exception as e:
        raise Exception(f"Failed to load config: {str(e)}")

def test_layer1_seed_generation(api_key: str, logger: logging.Logger):
    """Test Layer 1: Seed Generation"""
    
    logger.info("🌱 Testing Layer 1: Seed Generation")
    
    # Initialize engine
    layer1 = SearchAPILayer1SeedGeneration(api_key)
    
    # Test single keyword search
    logger.info("Testing single keyword search...")
    single_result = layer1.search_advertisers_by_keyword(
        keyword="invisalign",
        region="AU",
        num_advertisers=10,
        num_domains=10
    )
    
    logger.info(f"Single keyword result: {single_result['total_advertisers']} advertisers, {single_result['total_domains']} domains")
    
    # Test vertical seed generation
    logger.info("Testing vertical seed generation...")
    vertical_seeds = layer1.generate_seeds_by_vertical(
        vertical="dental_ortho",
        regions=["AU"],
        max_keywords=2
    )
    
    logger.info(f"Vertical seeds: {vertical_seeds['total_unique_advertisers']} unique advertisers")
    
    # Save results
    output_file = f"data/test_layer1_seeds_{int(datetime.now().timestamp())}.json"
    Path("data").mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(vertical_seeds, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Layer 1 results saved to {output_file}")
    
    return vertical_seeds

def test_layer2_consolidation(api_key: str, layer1_data: Dict, logger: logging.Logger):
    """Test Layer 2: Advertiser Consolidation"""
    
    logger.info("🔍 Testing Layer 2: Advertiser Consolidation")
    
    # Initialize engine
    layer2 = SearchAPILayer2AdvertiserConsolidation(api_key)
    
    # Prepare advertiser list from Layer 1
    advertisers_for_test = []
    
    for advertiser_id, advertiser_data in list(layer1_data["aggregated_advertisers"].items())[:5]:  # Test with first 5
        advertisers_for_test.append({
            "advertiser_id": advertiser_id,
            "domain": advertiser_data.get("verified_domain")
        })
    
    if not advertisers_for_test:
        logger.warning("No advertisers from Layer 1 to test Layer 2")
        return {}
    
    # Test batch consolidation
    logger.info(f"Testing consolidation with {len(advertisers_for_test)} advertisers...")
    
    consolidation_results = layer2.consolidate_advertisers_batch(
        advertiser_list=advertisers_for_test,
        region="AU",
        max_batch_size=5
    )
    
    summary = consolidation_results["summary"]
    logger.info(f"Consolidation results: {summary['qualified_count']} qualified, {summary['potential_count']} potential, {summary['rejected_count']} rejected")
    
    # Save results
    output_file = f"data/test_layer2_consolidation_{int(datetime.now().timestamp())}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(consolidation_results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Layer 2 results saved to {output_file}")
    
    return consolidation_results

def test_layer3_details(api_key: str, layer2_data: Dict, logger: logging.Logger):
    """Test Layer 3: Ad Details Analysis"""
    
    logger.info("🎯 Testing Layer 3: Ad Details Analysis")
    
    # Initialize engine
    layer3 = SearchAPILayer3AdDetailsAnalysis(api_key)
    
    # Get qualified advertisers from Layer 2
    qualified_advertisers = []
    
    for key, advertiser_data in layer2_data.get("qualified_advertisers", {}).items():
        # Mock creative IDs for testing (normally from Layer 2)
        mock_creative_ids = [f"CR{i}" for i in range(1, 4)]  # Mock IDs
        
        qualified_advertisers.append({
            "advertiser_id": advertiser_data.get("advertiser_id"),
            "domain": advertiser_data.get("domain"),
            "qualification_score": advertiser_data["qualification_scores"]["total_score"],
            "creative_ids": mock_creative_ids,
            "total_ads": advertiser_data.get("total_ads", 0)
        })
    
    if not qualified_advertisers:
        logger.warning("No qualified advertisers from Layer 2 to test Layer 3")
        return {}
    
    # Test with first qualified advertiser only (to save API calls)
    test_advertiser = qualified_advertisers[0]
    
    logger.info(f"Testing ad details for advertiser: {test_advertiser['advertiser_id']}")
    
    # Test single ad details (mock since we don't have real creative IDs)
    try:
        ad_details = layer3.get_ad_details(
            advertiser_id=test_advertiser["advertiser_id"],
            creative_id=test_advertiser["creative_ids"][0]
        )
        
        logger.info(f"Ad details extracted: {len(ad_details.get('ad_variations', []))} variations")
        
    except Exception as e:
        logger.warning(f"Ad details test failed (expected with mock IDs): {str(e)}")
        ad_details = {"mock_test": True}
    
    # Test CRO analysis with sample data
    sample_ad_data = {
        "ad_variations": [
            {
                "headlines": ["Get Your Perfect Smile Today", "Free Invisalign Consultation"],
                "descriptions": ["Book now for a free consultation. Certified orthodontist."],
                "final_url": "https://example-dental.com.au/invisalign"
            }
        ]
    }
    
    cro_analysis = layer3._analyze_cro_signals(sample_ad_data)
    logger.info(f"CRO analysis sample: {cro_analysis['total_cro_score']} points")
    
    # Save results
    test_results = {
        "ad_details": ad_details,
        "cro_analysis_sample": cro_analysis,
        "test_advertiser": test_advertiser
    }
    
    output_file = f"data/test_layer3_details_{int(datetime.now().timestamp())}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Layer 3 results saved to {output_file}")
    
    return test_results

def test_europa_real_estate_pipeline(api_key: str, logger: logging.Logger):
    """Test Europa Real Estate pipeline específico"""
    
    logger.info("🇪🇺 Testing Europa Real Estate Pipeline")
    
    # Initialize orchestrator
    orchestrator = ARCOSearchAPIMasterOrchestrator(
        api_key=api_key,
        output_dir="data/searchapi_test_results"
    )
    
    logger.info("Running Europa Real Estate focus pipeline...")
    
    try:
        results = orchestrator.run_europa_real_estate_focus(save_results=False)
        
        summary = results.get("pipeline_summary", {})
        strategy = results.get("strategy_context", {})
        market = results.get("market_analysis", {})
        
        logger.info(f"Europa pipeline complete:")
        logger.info(f"  - Strategy: {market.get('focus', 'N/A')}")
        logger.info(f"  - Timing advantage: {strategy.get('timing', 'N/A')}")
        logger.info(f"  - Initial advertisers: {summary.get('funnel_metrics', {}).get('initial_advertisers', 0)}")
        logger.info(f"  - Outreach ready: {summary.get('funnel_metrics', {}).get('outreach_ready', 0)}")
        logger.info(f"  - Cost efficiency: {market.get('cost_efficiency', 'N/A')}")
        
        return results
        
    except Exception as e:
        logger.error(f"Europa pipeline test failed: {str(e)}")
        return {"error": str(e)}

def test_full_pipeline(api_key: str, logger: logging.Logger):
    """Test complete pipeline orchestration"""
    
    logger.info("🚀 Testing Full Pipeline")
    
    # Initialize orchestrator
    orchestrator = ARCOSearchAPIMasterOrchestrator(
        api_key=api_key,
        output_dir="data/searchapi_test_results"
    )
    
    # Run quick test
    logger.info("Running quick pipeline test...")
    
    try:
        results = orchestrator.run_quick_test(
            vertical="dental_ortho",
            region="AU"
        )
        
        summary = results.get("pipeline_summary", {})
        logger.info(f"Pipeline test complete:")
        logger.info(f"  - Initial advertisers: {summary.get('funnel_metrics', {}).get('initial_advertisers', 0)}")
        logger.info(f"  - Qualified after Layer 2: {summary.get('funnel_metrics', {}).get('qualified_after_layer2', 0)}")
        logger.info(f"  - Outreach ready: {summary.get('funnel_metrics', {}).get('outreach_ready', 0)}")
        logger.info(f"  - Total API calls: {summary.get('api_efficiency', {}).get('total_calls', 0)}")
        logger.info(f"  - Execution time: {summary.get('execution_time_minutes', 0)} minutes")
        
        return results
        
    except Exception as e:
        logger.error(f"Full pipeline test failed: {str(e)}")
        return {"error": str(e)}

def main():
    """Main test function"""
    
    parser = argparse.ArgumentParser(description='Test ARCO SearchAPI Layers')
    parser.add_argument('--test', choices=['quick', 'full', 'layer1', 'layer2', 'layer3', 'europa'], 
                       default='quick', help='Type of test to run')
    
    args = parser.parse_args()
    
    # Setup
    logger = setup_logging()
    logger.info(f"Starting SearchAPI test: {args.test}")
    
    try:
        # Load configuration
        api_key, config = load_config()
        logger.info("Configuration loaded successfully")
        
        # Create data directory
        Path("data").mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        
        if args.test == 'quick' or args.test == 'full':
            # Test full pipeline
            results = test_full_pipeline(api_key, logger)
            
            if "error" not in results:
                logger.info("✅ Full pipeline test completed successfully")
            else:
                logger.error("❌ Full pipeline test failed")
        
        elif args.test == 'europa':
            # Test Europa Real Estate specific pipeline
            results = test_europa_real_estate_pipeline(api_key, logger)
            
            if "error" not in results:
                logger.info("✅ Europa Real Estate pipeline test completed successfully")
            else:
                logger.error("❌ Europa pipeline test failed")
        
        elif args.test == 'layer1':
            # Test Layer 1 only
            layer1_results = test_layer1_seed_generation(api_key, logger)
            logger.info("✅ Layer 1 test completed")
        
        elif args.test == 'layer2':
            # Test Layer 1 + 2
            layer1_results = test_layer1_seed_generation(api_key, logger)
            layer2_results = test_layer2_consolidation(api_key, layer1_results, logger)
            logger.info("✅ Layer 1 + 2 test completed")
        
        elif args.test == 'layer3':
            # Test all 3 layers
            layer1_results = test_layer1_seed_generation(api_key, logger)
            layer2_results = test_layer2_consolidation(api_key, layer1_results, logger)
            layer3_results = test_layer3_details(api_key, layer2_results, logger)
            logger.info("✅ All 3 layers test completed")
        
        logger.info("🎉 Test execution completed!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
