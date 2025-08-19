"""
Test Layer 3 SearchAPI - Creative Details
==========================================

Testa diferentes abordagens para obter detalhes de criativos
"""

import asyncio
import aiohttp
import json
from src.config.arco_config_simple import get_config, get_api_key

async def test_creative_details():
    """
    Testa diferentes abordagens para creative details
    """
    config = get_config()
    api_key = get_api_key()
    base_url = config.searchapi.base_url
    
    # Creative ID de exemplo do Layer 2
    creative_id = "CR14121294243758604289"
    domain = "clareestateagents.com"
    
    print(f"Testing creative details for: {creative_id}")
    print(f"Domain: {domain}")
    
    # Teste 1: Usando creative_id diretamente
    print("\n1. Testing with creative_id parameter...")
    params1 = {
        "engine": "google_ads_transparency_center",
        "api_key": api_key,
        "creative_id": creative_id
    }
    
    await test_api_call(base_url, params1, "creative_id")
    
    # Teste 2: Usando advertiser search com domain
    print("\n2. Testing advertiser search with domain...")
    params2 = {
        "engine": "google_ads_transparency_center",
        "api_key": api_key,
        "domain": domain
    }
    
    await test_api_call(base_url, params2, "domain")
    
    # Teste 3: Usando query com creative ID
    print("\n3. Testing with query parameter...")
    params3 = {
        "engine": "google_ads_transparency_center",
        "api_key": api_key,
        "q": creative_id
    }
    
    await test_api_call(base_url, params3, "query")


async def test_api_call(base_url, params, test_name):
    """
    Executa chamada de teste para a API
    """
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            async with session.get(base_url, params=params) as response:
                print(f"Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Success for {test_name}")
                    print(f"Keys in response: {list(data.keys())}")
                    
                    # Mostrar estrutura resumida
                    if "ad_creatives" in data:
                        print(f"Found {len(data['ad_creatives'])} ad_creatives")
                    if "results" in data:
                        print(f"Found {len(data['results'])} results")
                    if "ad_variations" in data:
                        print(f"Found {len(data['ad_variations'])} ad_variations")
                    
                    # Salvar response para análise
                    with open(f"layer3_test_{test_name}.json", 'w') as f:
                        json.dump(data, f, indent=2)
                    
                else:
                    error_text = await response.text()
                    print(f"❌ Error {response.status} for {test_name}")
                    print(f"Error: {error_text[:200]}...")
                    
    except Exception as e:
        print(f"❌ Exception for {test_name}: {e}")


if __name__ == "__main__":
    asyncio.run(test_creative_details())
