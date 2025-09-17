"""
Google Custom Search API Integration
Confirms SaaS footprints via targeted search queries
"""

import httpx
import os
from typing import Dict, List, Optional


class GoogleCustomSearchAPI:
    """Google Custom Search for SaaS footprint confirmation"""
    
    def __init__(self, api_key: str, search_engine_id: str):
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.session = None
    
    async def __aenter__(self):
        self.session = httpx.AsyncClient(timeout=10.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def search_saas_footprint(self, domain: str, saas_tool: str) -> Dict:
        """Search for specific SaaS tool usage on domain"""
        
        # SaaS-specific search queries
        queries = {
            'typeform': f'site:{domain} typeform OR "typeform.com" OR "embed.typeform"',
            'klaviyo': f'site:{domain} klaviyo OR "klaviyo.com" OR "a.klaviyo"',
            'hubspot': f'site:{domain} hubspot OR "hs-scripts" OR "hsforms"',
            'shopify_plus': f'site:{domain} "shopify plus" OR "plus.shopify"',
            'recharge': f'site:{domain} recharge OR "rechargepayments"',
            'gorgias': f'site:{domain} gorgias OR "gorgias.com"'
        }
        
        query = queries.get(saas_tool.lower())
        if not query:
            return {'found': False, 'confidence': 0.0}
        
        params = {
            'key': self.api_key,
            'cx': self.search_engine_id,
            'q': query,
            'num': 3  # Only need few results to confirm
        }
        
        try:
            response = await self.session.get(self.base_url, params=params)
            
            if response.status_code != 200:
                return {'found': False, 'confidence': 0.0, 'error': response.status_code}
            
            data = response.json()
            items = data.get('items', [])
            
            # Analyze results
            confidence = min(len(items) * 0.4, 1.0)  # More results = higher confidence
            
            evidence = []
            for item in items:
                title = item.get('title', '')
                snippet = item.get('snippet', '')
                evidence.append({
                    'title': title,
                    'snippet': snippet,
                    'url': item.get('link', '')
                })
            
            return {
                'found': len(items) > 0,
                'confidence': confidence,
                'evidence_count': len(items),
                'evidence': evidence
            }
            
        except Exception as e:
            return {'found': False, 'confidence': 0.0, 'error': str(e)}


async def confirm_saas_usage(domain: str, detected_tools: List[str]) -> Dict:
    """Confirm detected SaaS tools via Google Search"""
    
    api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
    search_engine_id = os.getenv('GOOGLE_SEARCH_CX')
    
    if not api_key or not search_engine_id:
        return {'error': 'Missing Google Search API credentials'}
    
    confirmations = {}
    
    async with GoogleCustomSearchAPI(api_key, search_engine_id) as search_api:
        for tool in detected_tools:
            result = await search_api.search_saas_footprint(domain, tool)
            confirmations[tool] = result
    
    return confirmations
