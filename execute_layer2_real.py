"""
Execute Layer 2 Real - Advertiser Consolidation
===============================================

Executa Layer 2 com chamadas reais do SearchAPI usando dados do Layer 1
"""

import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime

from src.engines.searchapi_layer2_advertiser_consolidation import SearchAPILayer2AdvertiserConsolidation


async def execute_layer2_real():
    """Execute Layer 2 with real SearchAPI calls"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🔍 ARCO Layer 2 - Real Advertiser Consolidation")
    print("=" * 60)
    
    # Load Layer 1 results
    layer1_file = Path("data/exports/pipeline_europa_20250819_045740/layer1_seeds_20250819_045740.json")
    
    if not layer1_file.exists():
        print(f"❌ Layer 1 file not found: {layer1_file}")
        return
    
    print(f"📂 Loading Layer 1 data: {layer1_file}")
    
    with open(layer1_file, 'r', encoding='utf-8') as f:
        layer1_data = json.load(f)
    
    print(f"✅ Layer 1 loaded: {len(layer1_data.get('results_by_keyword', {}))} keyword results")
    
    # Initialize Layer 2 engine
    layer2 = SearchAPILayer2AdvertiserConsolidation()
    
    # Process Layer 1 seeds with real API calls
    print("\n🚀 Starting Layer 2 consolidation with real SearchAPI calls...")
    print("⏱️  This may take a few minutes due to rate limiting...")
    
    layer2_results = await layer2.process_layer1_seeds(layer1_data)
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"data/exports/layer2_real_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save results
    results_file = await layer2.save_results(layer2_results, output_dir)
    
    # Print summary
    print("\n✅ Layer 2 Complete!")
    print("=" * 60)
    print(f"📊 Summary:")
    print(f"   🌐 Input Domains: {layer2_results['summary']['total_domains_from_layer1']}")
    print(f"   🔄 Processed: {layer2_results['summary']['processed_count']}")
    print(f"   ⭐ High Quality: {layer2_results['summary']['high_quality_leads']}")
    print(f"   📋 Medium Quality: {layer2_results['summary']['medium_quality_leads']}")
    print(f"   🎯 Success Rate: {layer2_results['summary']['success_rate']:.1%}")
    print(f"   🔧 API Calls Used: {layer2_results['api_calls_used']}")
    print(f"   💾 Results saved to: {results_file}")
    
    # Show top results
    if layer2_results['high_priority']:
        print(f"\n🏆 Top High-Priority Leads:")
        for i, adv in enumerate(layer2_results['high_priority'][:5], 1):
            print(f"   {i}. {adv['advertiser_name']} ({adv['region']}) - Score: {adv['quality_score']:.2f}")
    
    if layer2_results['medium_priority']:
        print(f"\n📋 Top Medium-Priority Leads:")
        for i, adv in enumerate(layer2_results['medium_priority'][:3], 1):
            print(f"   {i}. {adv['advertiser_name']} ({adv['region']}) - Score: {adv['quality_score']:.2f}")
    
    return layer2_results


if __name__ == "__main__":
    asyncio.run(execute_layer2_real())
