"""
Test Layer 2 API Call
"""

import asyncio
import aiohttp
import json
from src.config.arco_config_simple import get_config, get_api_key

async def test_transparency_center():
    """Test direct call to transparency center"""
    
    config = get_config()
    api_key = get_api_key()
    base_url = config.searchapi.base_url
    
    # Test with shorter domain from Layer 1
    params = {
        "engine": "google_ads_transparency_center",
        "api_key": api_key,
        "domain": "propertymanagement.ae",  # Shorter domain
        "gl": "ae"
    }
    
    print("🔍 Testing SearchAPI Google Ads Transparency Center")
    print(f"📡 URL: {base_url}")
    print(f"🔑 API Key: {api_key[:10]}...")
    print(f"🎯 Domain: {params['domain']}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(base_url, params=params, timeout=30) as response:
                print(f"📊 Status: {response.status}")
                
                result = await response.json()
                print(f"📄 Response keys: {list(result.keys())}")
                
                if 'ads_results' in result:
                    print(f"✅ Found {len(result['ads_results'])} ads")
                    if result['ads_results']:
                        print(f"📝 Sample ad: {result['ads_results'][0]}")
                else:
                    print("❌ No ads_results found")
                    print(f"📄 Full response: {json.dumps(result, indent=2)}")
                        
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_transparency_center())
