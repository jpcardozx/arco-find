"""
ARCO Places API Seed Engine
Fonte primária: Places API para seed de empresas por vertical/região
Pipeline: Places -> Ad Confirmation -> Web Vitals -> Sprint Match
"""

import googlemaps
import requests
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
import time

logger = logging.getLogger(__name__)

class PlacesSeedEngine:
    """
    Engine de seed usando Places API (New)
    Focus: Volume local qualificado com dados confiáveis
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = googlemaps.Client(key=api_key)
        
        # Mapeamento estratégico vertical -> query terms
        self.vertical_queries = {
            'dental': [
                'dentist', 'dental clinic', 'orthodontist', 
                'dental surgery', 'cosmetic dentist'
            ],
            'legal': [
                'lawyer', 'law firm', 'attorney', 'solicitor', 
                'legal services', 'barrister'
            ],
            'aesthetic': [
                'cosmetic clinic', 'aesthetic clinic', 'botox clinic',
                'beauty clinic', 'cosmetic surgery', 'med spa'
            ],
            'estate': [
                'real estate agent', 'property management', 'estate agent',
                'property developer', 'real estate agency'
            ],
            'fitness': [
                'gym', 'fitness center', 'personal trainer',
                'crossfit', 'yoga studio', 'pilates studio'
            ]
        }
        
        # Regiões alvo com coordenadas
        self.target_regions = {
            'sydney': {'lat': -33.8688, 'lng': 151.2093, 'radius': 50000},
            'melbourne': {'lat': -37.8136, 'lng': 144.9631, 'radius': 50000},
            'brisbane': {'lat': -27.4698, 'lng': 153.0251, 'radius': 40000},
            'perth': {'lat': -31.9505, 'lng': 115.8605, 'radius': 40000},
            'auckland': {'lat': -36.8485, 'lng': 174.7633, 'radius': 40000},
            'wellington': {'lat': -41.2865, 'lng': 174.7762, 'radius': 30000}
        }
    
    def discover_seed_prospects(self, 
                               vertical: str,
                               region: str,
                               max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Descoberta seed usando Places API com field mask otimizado
        """
        
        if vertical not in self.vertical_queries:
            raise ValueError(f"Vertical {vertical} não suportado")
        
        if region not in self.target_regions:
            raise ValueError(f"Região {region} não suportada")
        
        logger.info("Iniciando discovery seed: %s em %s", vertical, region)
        
        all_prospects = []
        region_config = self.target_regions[region]
        query_terms = self.vertical_queries[vertical]
        
        for query_term in query_terms:
            try:
                # Rate limiting
                time.sleep(0.1)
                
                prospects = self._search_places_optimized(
                    query=query_term,
                    location=(region_config['lat'], region_config['lng']),
                    radius=region_config['radius'],
                    max_results=min(20, max_results // len(query_terms))
                )
                
                # Adicionar metadados
                for prospect in prospects:
                    prospect.update({
                        'seed_vertical': vertical,
                        'seed_region': region,
                        'seed_query': query_term,
                        'discovered_at': datetime.now().isoformat(),
                        'data_source': 'places_api_seed'
                    })
                
                all_prospects.extend(prospects)
                logger.info("Query '%s': %d prospects encontrados", query_term, len(prospects))
                
            except Exception as e:
                logger.error("Erro na query '%s': %s", query_term, e)
                continue
        
        # Deduplicação por place_id
        unique_prospects = self._deduplicate_by_place_id(all_prospects)
        
        logger.info("Seed discovery concluído: %d prospects únicos", len(unique_prospects))
        return unique_prospects[:max_results]
    
    def _search_places_optimized(self, 
                                query: str,
                                location: tuple,
                                radius: int,
                                max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Busca otimizada com field mask para reduzir custos
        """
        
        try:
            # Field mask otimizado - só campos essenciais
            fields = [
                'place_id', 'name', 'formatted_address', 'website',
                'international_phone_number', 'rating', 'user_ratings_total',
                'types', 'business_status', 'geometry/location'
            ]
            
            # Text search com filtros geográficos
            result = self.client.places_nearby(
                location=location,
                radius=radius,
                keyword=query,
                type='establishment'
            )
            
            prospects = []
            
            for place in result.get('results', [])[:max_results]:
                # Enriquecer com Place Details se necessário
                place_details = self._get_essential_details(place['place_id'])
                
                prospect = {
                    'place_id': place['place_id'],
                    'company_name': place.get('name', ''),
                    'address': place.get('vicinity', ''),
                    'location': f"{location[0]},{location[1]}",
                    'website': place_details.get('website'),
                    'phone': place_details.get('international_phone_number'),
                    'rating': place.get('rating'),
                    'review_count': place.get('user_ratings_total', 0),
                    'business_status': place.get('business_status', 'OPERATIONAL'),
                    'types': place.get('types', []),
                    'geometry': place.get('geometry', {}).get('location', {})
                }
                
                # Filtro de qualidade
                if self._is_quality_prospect(prospect):
                    prospects.append(prospect)
            
            return prospects
            
        except Exception as e:
            logger.error("Erro Places API search: %s", e)
            return []
    
    def _get_essential_details(self, place_id: str) -> Dict[str, Any]:
        """
        Busca detalhes essenciais com field mask mínimo
        """
        
        try:
            # Rate limiting
            time.sleep(0.05)
            
            fields = ['website', 'international_phone_number', 'url']
            
            result = self.client.place(
                place_id=place_id,
                fields=fields
            )
            
            return result.get('result', {})
            
        except Exception as e:
            logger.warning("Erro buscando detalhes %s: %s", place_id, e)
            return {}
    
    def _is_quality_prospect(self, prospect: Dict[str, Any]) -> bool:
        """
        Filtro de qualidade para prospects seed
        """
        
        # Filtros básicos de qualidade
        if not prospect.get('company_name'):
            return False
        
        if prospect.get('business_status') != 'OPERATIONAL':
            return False
        
        # Excluir chains conhecidos (não SME)
        excluded_chains = [
            'mcdonald', 'kfc', 'subway', 'domino', 'pizza hut',
            'woolworths', 'coles', 'bunnings', 'jb hi-fi'
        ]
        
        name_lower = prospect['company_name'].lower()
        if any(chain in name_lower for chain in excluded_chains):
            return False
        
        # Preferir prospects com website (maior chance de anunciar)
        if prospect.get('website'):
            return True
        
        # Aceitar se tem reviews boas (indicador de atividade)
        if prospect.get('rating', 0) >= 4.0 and prospect.get('review_count', 0) >= 10:
            return True
        
        return False
    
    def _deduplicate_by_place_id(self, prospects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicatas por place_id
        """
        
        seen_ids = set()
        unique_prospects = []
        
        for prospect in prospects:
            place_id = prospect.get('place_id')
            if place_id and place_id not in seen_ids:
                seen_ids.add(place_id)
                unique_prospects.append(prospect)
        
        return unique_prospects
    
    def enrich_with_web_presence(self, prospects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enriquece prospects com análise básica de presença web
        """
        
        enriched = []
        
        for prospect in prospects:
            website = prospect.get('website')
            if not website:
                # Tentar inferir website a partir do nome
                website = self._infer_website(prospect['company_name'])
                prospect['inferred_website'] = website
            
            if website:
                # Análise básica de presença web
                web_analysis = self._analyze_web_presence(website)
                prospect['web_presence'] = web_analysis
            
            enriched.append(prospect)
        
        return enriched
    
    def _infer_website(self, company_name: str) -> Optional[str]:
        """
        Tenta inferir website a partir do nome da empresa
        """
        
        # Limpeza básica do nome
        clean_name = company_name.lower()
        clean_name = clean_name.replace(' ', '').replace('-', '')
        clean_name = ''.join(c for c in clean_name if c.isalnum())
        
        # Tentativas comuns
        common_domains = ['.com.au', '.co.nz', '.com']
        
        for domain in common_domains:
            potential_url = f"https://{clean_name}{domain}"
            # Nota: Aqui você poderia fazer uma verificação HTTP HEAD
            # Por ora, apenas retornamos a tentativa mais provável
            if domain == '.com.au':  # Mais provável para AU
                return potential_url
        
        return None
    
    def _analyze_web_presence(self, website: str) -> Dict[str, Any]:
        """
        Análise básica de presença web (sem PageSpeed ainda)
        """
        
        try:
            # HEAD request simples para verificar se responde
            response = requests.head(website, timeout=5, allow_redirects=True)
            
            return {
                'accessible': response.status_code == 200,
                'final_url': response.url,
                'https_enabled': response.url.startswith('https://'),
                'response_time_ms': response.elapsed.total_seconds() * 1000,
                'analyzed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'accessible': False,
                'error': str(e),
                'analyzed_at': datetime.now().isoformat()
            }
    
    def save_seed_results(self, prospects: List[Dict[str, Any]], 
                         vertical: str, region: str) -> str:
        """
        Salva resultados do seed discovery
        """
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"data/seeds/places_seed_{vertical}_{region}_{timestamp}.json"
        
        os.makedirs('data/seeds', exist_ok=True)
        
        save_data = {
            'seed_metadata': {
                'timestamp': datetime.now().isoformat(),
                'vertical': vertical,
                'region': region,
                'engine': 'places_api_seed_v1.0',
                'total_prospects': len(prospects)
            },
            'prospects': prospects,
            'statistics': {
                'with_website': len([p for p in prospects if p.get('website')]),
                'with_phone': len([p for p in prospects if p.get('phone')]),
                'avg_rating': sum(p.get('rating', 0) for p in prospects) / len(prospects) if prospects else 0,
                'business_types': list(set(
                    t for p in prospects for t in p.get('types', [])
                ))[:10]  # Top 10 tipos
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2, default=str)
        
        logger.info("Seed results salvos: %s", filename)
        return filename

def main():
    """Teste do Places Seed Engine"""
    
    print("ARCO Places API Seed Engine")
    print("=" * 40)
    
    # Configuração
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        print("ERRO: GOOGLE_MAPS_API_KEY não configurada")
        return
    
    engine = PlacesSeedEngine(api_key)
    
    # Teste: dental em Sydney
    try:
        prospects = engine.discover_seed_prospects(
            vertical='dental',
            region='sydney',
            max_results=20
        )
        
        print(f"Seed discovery concluído: {len(prospects)} prospects")
        
        # Estatísticas
        with_website = len([p for p in prospects if p.get('website')])
        with_phone = len([p for p in prospects if p.get('phone')])
        
        print(f"  Com website: {with_website}")
        print(f"  Com telefone: {with_phone}")
        
        # Enriquecer com presença web
        enriched = engine.enrich_with_web_presence(prospects)
        
        # Top 5
        print("\nTop 5 prospects:")
        for i, prospect in enumerate(enriched[:5], 1):
            print(f"{i}. {prospect['company_name']}")
            print(f"   Website: {prospect.get('website', 'N/A')}")
            print(f"   Rating: {prospect.get('rating', 'N/A')}")
            print(f"   Reviews: {prospect.get('review_count', 'N/A')}")
            
        # Salvar
        output_file = engine.save_seed_results(enriched, 'dental', 'sydney')
        print(f"\nResultados salvos: {output_file}")
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()