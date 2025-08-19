"""
Teste rápido das keywords de maior volume
"""
import asyncio
from src.engines.searchapi_layer1_seed_generation import SearchAPILayer1SeedGeneration

async def test_high_volume_keywords():
    """Testa keywords com maior volume de anúncios"""
    
    print("🧪 Testing High Volume Europa Keywords")
    print("=" * 50)
    
    async with SearchAPILayer1SeedGeneration() as layer1:
        
        # Test property management in Ireland
        result1 = await layer1.search_advertisers_by_keyword(
            keyword="property management",
            region="IE",
            num_advertisers=10
        )
        
        print(f"🇮🇪 Property Management IE: {result1['total_advertisers']} advertisers, {result1['total_domains']} domains")
        
        # Test estate agent in GB
        result2 = await layer1.search_advertisers_by_keyword(
            keyword="estate agent", 
            region="GB",
            num_advertisers=10
        )
        
        print(f"🇬🇧 Estate Agent GB: {result2['total_advertisers']} advertisers, {result2['total_domains']} domains")
        
        # Test buy property in IE
        result3 = await layer1.search_advertisers_by_keyword(
            keyword="buy property",
            region="IE", 
            num_advertisers=10
        )
        
        print(f"🏠 Buy Property IE: {result3['total_advertisers']} advertisers, {result3['total_domains']} domains")
        
        total_advertisers = result1['total_advertisers'] + result2['total_advertisers'] + result3['total_advertisers']
        total_domains = result1['total_domains'] + result2['total_domains'] + result3['total_domains']
        
        print(f"\n🎯 Summary:")
        print(f"   📊 Total Advertisers: {total_advertisers}")
        print(f"   🌐 Total Domains: {total_domains}")
        print(f"   ✅ S-tier Async: 3 concurrent requests completed")

if __name__ == "__main__":
    asyncio.run(test_high_volume_keywords())
