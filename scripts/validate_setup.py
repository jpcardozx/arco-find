#!/usr/bin/env python3
"""
🔧 SCRIPT DE VALIDAÇÃO COMPLETA
Testa todas as APIs antes da execução do pipeline
"""

import os
import asyncio
import aiohttp
import sys
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from tech_stack_detector import TechStackDetector


async def test_pagespeed_api(api_key: str) -> bool:
    """Testa PageSpeed API com URL conhecida"""
    try:
        url = "https://www.googleapis.com/pagespeed/v5/runPagespeed"
        params = {
            'url': 'https://www.google.com',
            'key': api_key,
            'strategy': 'mobile',
            'category': 'performance'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    score = data.get('lighthouseResult', {}).get('categories', {}).get('performance', {}).get('score', 0)
                    print(f"    ✅ PageSpeed API funcionando (score: {score:.2f})")
                    return True
                else:
                    print(f"    ❌ PageSpeed API erro {response.status}")
                    return False
    except Exception as e:
        print(f"    ❌ PageSpeed API falhou: {e}")
        return False


async def test_search_api(api_key: str, search_cx: str) -> bool:
    """Testa Google Search API"""
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': search_cx,
            'q': 'site:google.com',
            'num': 1
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get('items', [])
                    print(f"    ✅ Search API funcionando ({len(items)} resultados)")
                    return True
                else:
                    print(f"    ❌ Search API erro {response.status}")
                    return False
    except Exception as e:
        print(f"    ❌ Search API falhou: {e}")
        return False


def test_builtwith() -> bool:
    """Testa BuiltWith detection"""
    try:
        detector = TechStackDetector()
        result = detector.detect_technologies("https://www.shopify.com")
        
        if result and isinstance(result, dict):
            print(f"    ✅ BuiltWith funcionando ({len(result)} categorias)")
            return True
        else:
            print(f"    ❌ BuiltWith retornou dados inválidos")
            return False
    except Exception as e:
        print(f"    ❌ BuiltWith falhou: {e}")
        return False


async def validate_complete_setup():
    """Validação completa do ambiente"""
    
    print("🔧 ARCO-FIND: VALIDAÇÃO COMPLETA DO SETUP")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Check .env file
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if not os.path.exists(env_path):
        print("❌ Arquivo .env não encontrado")
        print("🔧 Crie o arquivo .env com as variáveis necessárias")
        return False
    
    print("✅ Arquivo .env encontrado")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv(env_path)
    
    # Check required variables
    required_vars = {
        'GOOGLE_PAGESPEED_API_KEY': 'PageSpeed Insights API',
        'GOOGLE_SEARCH_API_KEY': 'Google Search API',
        'GOOGLE_SEARCH_CX': 'Google Search Engine ID'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            missing_vars.append(f"{var} ({description})")
        else:
            print(f"✅ {description}: configurado")
    
    if missing_vars:
        print("\n❌ VARIÁVEIS FALTANDO:")
        for var in missing_vars:
            print(f"   • {var}")
        print("\n🔧 Configure essas variáveis no arquivo .env")
        return False
    
    print("\n🔍 TESTANDO APIs...")
    
    # Test APIs
    api_results = {}
    
    # PageSpeed API
    print("  🧪 Testando PageSpeed API...")
    pagespeed_key = os.getenv('GOOGLE_PAGESPEED_API_KEY')
    api_results['pagespeed'] = await test_pagespeed_api(pagespeed_key)
    
    # Search API  
    print("  🧪 Testando Google Search API...")
    search_key = os.getenv('GOOGLE_SEARCH_API_KEY')
    search_cx = os.getenv('GOOGLE_SEARCH_CX')
    api_results['search'] = await test_search_api(search_key, search_cx)
    
    # BuiltWith
    print("  🧪 Testando BuiltWith detection...")
    api_results['builtwith'] = test_builtwith()
    
    # Summary
    print("\n📊 RESULTADO DA VALIDAÇÃO:")
    print("-" * 40)
    
    all_working = True
    for api, status in api_results.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {api.upper()}: {'Funcionando' if status else 'COM PROBLEMAS'}")
        if not status:
            all_working = False
    
    print()
    
    if all_working:
        print("🎉 SETUP COMPLETO E FUNCIONAL!")
        print("🚀 Pronto para executar: python main.py")
        return True
    else:
        print("⚠️  SETUP INCOMPLETO")
        print("🔧 Corrija os problemas antes de executar o pipeline")
        return False


async def main():
    """Entry point do script de validação"""
    success = await validate_complete_setup()
    
    if success:
        print("\n🎯 PRÓXIMO PASSO:")
        print("   python main.py")
    else:
        print("\n🔧 AÇÕES NECESSÁRIAS:")
        print("   1. Configure variáveis em .env")
        print("   2. Verifique conexão internet")
        print("   3. Execute novamente: python scripts/validate_setup.py")


if __name__ == "__main__":
    asyncio.run(main())
