#!/usr/bin/env python3
"""
🎯 PRAGMATIC PROSPECT DISCOVERY
Otimizado, sem overengineering, focado em resultados acionáveis
Multi-vertical com cálculos conservadores e maduros
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class PragmaticProspectDiscovery:
    """
    Discovery pragmático e maduro para prospects qualificados
    """
    
    def __init__(self):
        self.search_api = None
        
    async def initialize_apis(self):
        """Initialize SearchAPI"""
        try:
            from config.api_keys import APIConfig
            from src.connectors.searchapi_connector import SearchAPIConnector
            
            api_config = APIConfig()
            self.search_api = SearchAPIConnector(api_key=api_config.SEARCH_API_KEY)
            
            print("🔧 Pragmatic discovery systems initialized")
            return True
            
        except Exception as e:
            print(f"❌ System initialization failed: {e}")
            return False
    
    def get_pragmatic_queries(self, market: str) -> List[str]:
        """
        Queries otimizadas para Costa Oeste Norte-Americana: Canadá + EUA fallback
        Foco em Vancouver, Toronto, Ontario + mercados premium menos saturados
        """
        market_queries = {
            'north_america_west': [
                # Canada Premium Markets (Primary)
                'site:*.ca "vancouver" ("dental clinic" OR "dental practice") "book appointment" -chain -franchise',
                'site:*.ca "toronto" ("medical practice" OR "medical clinic") "consultation" -hospital -network',
                'site:*.ca "ontario" ("beauty clinic" OR "aesthetic clinic") "treatments" -spa -chain',
                'site:*.ca "calgary" "physiotherapy" "sports therapy" -franchise',
                'site:*.ca "montreal" ("chiropractor" OR "chiropractic") "wellness" -chain',
                
                # Canada + USA Cross-Border Fallback
                '("vancouver" OR "seattle") "dental practice" "book online" -directory',
                '("toronto" OR "buffalo") "medical clinic" "new patients" -hospital',
                '("calgary" OR "denver") "beauty treatments" "consultation" -chain',
                '("ottawa" OR "portland") "physiotherapy clinic" -franchise -network',
                
                # Universal North American SMB Patterns
                'site:*.ca "family practice" "independent" "established" -corporate',
                'site:*.ca "local clinic" "book appointment" "call" -booking.com',
                'inurl:about site:*.ca "years experience" "practice" -university',
                
                # High-Intent Service Queries (CA + US fallback)
                '"family dental practice" (vancouver OR seattle) -chain -corporate',
                '"medical clinic" (toronto OR "upstate new york") "new patient"',
                '"beauty clinic" (montreal OR "new england") "consultation"',
                
                # Professional Services Premium Markets
                'site:*.ca "law firm" "consultation" vancouver -directory -lawyer.com',
                'site:*.ca "accounting firm" toronto "small business" -corporate',
                'site:*.ca "real estate" calgary "independent" -remax -coldwell'
            ]
        }
        
        return market_queries.get(market, [])
    
    async def discover_prospects(self, market: str = 'north_america_west', max_per_query: int = 10) -> List[Dict]:
        """
        Discovery inteligente Costa Oeste Norte-Americana: Canadá + EUA fallback
        Otimizado para Vancouver, Toronto, Ontario e mercados premium
        """
        print(f"\n🎯 NORTH AMERICA WEST COAST DISCOVERY: {market.upper()}")
        print("🇨🇦 Primary: Canada Premium Markets | 🇺🇸 Fallback: USA Cross-Border")
        print("=" * 70)
        
        queries = self.get_pragmatic_queries(market)
        raw_prospects = []
        
        for i, query in enumerate(queries, 1):
            print(f"\nQuery {i}/{len(queries)}: {query[:80]}...")
            
            try:
                results = await self.search_api.search_companies(query, max_results=max_per_query)
                print(f"✅ Found {len(results)} companies for this query")
                
                for company in results:
                    if self._validate_basic_prospect(company, market):
                        raw_prospects.append({
                            'company_data': company,
                            'discovery_query': query,
                            'market': market,
                            'discovery_timestamp': datetime.now().isoformat()
                        })
                        print(f"  ✅ {company.get('name', 'Unknown')[:50]}")
                    else:
                        print(f"  ❌ {company.get('name', 'Unknown')[:50]} - Filtered out")
                
                await asyncio.sleep(0.3)  # Faster rate limiting for premium market
                
            except Exception as e:
                print(f"  ⚠️ Query error: {e}")
                continue
        
        # Deduplicate
        unique_prospects = self._deduplicate_prospects(raw_prospects)
        
        print(f"\n📊 Discovery Summary:")
        print(f"   Queries executed: {len(queries)}")
        print(f"   Raw prospects found: {len(raw_prospects)}")
        print(f"   Unique prospects: {len(unique_prospects)}")
        
        return unique_prospects
    
    def _validate_basic_prospect(self, company: Dict, market: str) -> bool:
        """
        Validação inteligente para mercado norte-americano premium
        Foca em SMBs independentes com potencial de receita
        """
        try:
            name = company.get('name', '').strip()
            description = company.get('description', '').strip()
            website = company.get('website', '').strip()
            
            if not name:
                return False
            
            content = f"{name} {description}".lower()
            
            # Hard excludes - corporações e diretórios
            hard_excludes = [
                'wikipedia', 'linkedin', 'facebook', 'youtube', 'instagram',
                'yelp', 'yellowpages', 'directory', 'marketplace', 'booking.com',
                'government', 'university', 'hospital', 'healthline.com',
                'webmd', 'mayoclinic', 'canada.ca', 'gov.ca'
            ]
            
            for exclude in hard_excludes:
                if exclude in content:
                    return False
            
            # Premium market indicators (positivos)
            positive_signals = [
                'clinic', 'practice', 'dental', 'medical', 'beauty',
                'physiotherapy', 'chiropractic', 'optometry', 'wellness',
                'family', 'independent', 'consultation', 'appointment',
                'treatment', 'therapy', 'law firm', 'accounting',
                'real estate', 'professional services'
            ]
            
            # Deve ter pelo menos um sinal positivo
            has_positive = any(signal in content for signal in positive_signals)
            
            # Validação de domínio para mercado norte-americano
            domain_valid = False
            if website:
                if '.ca' in website.lower() or any(city in content for city in 
                    ['vancouver', 'toronto', 'calgary', 'montreal', 'ottawa', 'ontario']):
                    domain_valid = True
                elif any(us_city in content for us_city in 
                    ['seattle', 'buffalo', 'denver', 'portland', 'new england']):
                    domain_valid = True
            
            return has_positive and (domain_valid or not website)
            
        except Exception:
            return False
    
    def _deduplicate_prospects(self, prospects: List[Dict]) -> List[Dict]:
        """Deduplicate by domain"""
        seen_domains = set()
        unique = []
        
        for prospect in prospects:
            domain = self._extract_domain(prospect['company_data'].get('website', ''))
            if domain and domain not in seen_domains:
                seen_domains.add(domain)
                unique.append(prospect)
        
        return unique
    
    async def analyze_prospects_conservative(self, prospects: List[Dict]) -> List[Dict]:
        """
        Análise conservadora e madura dos prospects
        """
        print(f"\n🧠 CONSERVATIVE PROSPECT ANALYSIS")
        print("=" * 50)
        
        analyzed_prospects = []
        
        for prospect in prospects:
            try:
                company = prospect['company_data']
                domain = self._extract_domain(company.get('website', ''))
                
                print(f"\nAnalyzing: {company['name'][:35]}...")
                
                # Business size estimation
                size_analysis = self._estimate_business_size(company)
                if size_analysis['employees'] < 3 or size_analysis['employees'] > 20:
                    print(f"  ❌ Size outside target: {size_analysis['employees']} employees")
                    continue
                
                # Business type classification
                business_type = self._classify_business_type(company)
                
                # Revenue estimation (conservative)
                revenue_analysis = self._estimate_business_revenue_conservative(
                    size_analysis, business_type, company
                )
                
                if revenue_analysis['monthly_revenue'] < 15000:
                    print(f"  ❌ Revenue too low: ${revenue_analysis['monthly_revenue']:,.0f}/month")
                    continue
                
                # Marketing spend estimation
                marketing_analysis = self._estimate_marketing_spend_conservative(
                    revenue_analysis, business_type, company
                )
                
                if marketing_analysis['monthly_spend'] < 500:
                    print(f"  ❌ Marketing spend too low: ${marketing_analysis['monthly_spend']:.0f}/month")
                    continue
                
                # Pain point opportunity (conservative)
                opportunity_analysis = self._analyze_opportunity_conservative(
                    business_type, marketing_analysis, prospect['discovery_query']
                )
                
                # Build analyzed prospect
                analyzed_prospect = {
                    'company_name': company['name'],
                    'domain': domain,
                    'business_type': business_type,
                    'market': prospect['market'],
                    
                    # Size metrics
                    'estimated_employees': size_analysis['employees'],
                    'size_confidence': size_analysis['confidence'],
                    
                    # Financial metrics (conservative)
                    'estimated_monthly_revenue': revenue_analysis['monthly_revenue'],
                    'revenue_confidence': revenue_analysis['confidence'],
                    'estimated_monthly_marketing_spend': marketing_analysis['monthly_spend'],
                    'marketing_confidence': marketing_analysis['confidence'],
                    
                    # Opportunity metrics
                    'opportunity_type': opportunity_analysis['opportunity_type'],
                    'estimated_monthly_impact': opportunity_analysis['conservative_impact'],
                    'opportunity_confidence': opportunity_analysis['confidence'],
                    
                    # Meta
                    'overall_fit_score': self._calculate_overall_fit_score(
                        size_analysis, revenue_analysis, marketing_analysis, opportunity_analysis
                    ),
                    'analysis_timestamp': datetime.now().isoformat(),
                    'discovery_query': prospect['discovery_query']
                }
                
                analyzed_prospects.append(analyzed_prospect)
                print(f"  ✅ QUALIFIED - Fit: {analyzed_prospect['overall_fit_score']:.2f}, Impact: ${opportunity_analysis['conservative_impact']:.0f}/mo")
                
            except Exception as e:
                print(f"  ❌ Analysis error: {e}")
                continue
        
        # Sort by fit score
        analyzed_prospects.sort(key=lambda x: x['overall_fit_score'], reverse=True)
        
        print(f"\n📊 Analysis Complete: {len(analyzed_prospects)} qualified prospects")
        return analyzed_prospects
    
    def _estimate_business_size(self, company: Dict) -> Dict:
        """Conservative business size estimation"""
        description = company.get('description', '').lower()
        name = company.get('name', '').lower()
        
        # Size indicators
        small_indicators = ['family', 'local', 'independent', 'solo', 'private practice']
        medium_indicators = ['clinic', 'centre', 'practice', 'group', 'associates']
        large_indicators = ['hospital', 'corporation', 'enterprise', 'chain', 'network']
        
        text = description + ' ' + name
        
        small_count = sum(1 for indicator in small_indicators if indicator in text)
        medium_count = sum(1 for indicator in medium_indicators if indicator in text)
        large_count = sum(1 for indicator in large_indicators if indicator in text)
        
        if large_count > 0:
            return {'employees': 25, 'confidence': 0.8}  # Too large
        elif medium_count > small_count:
            return {'employees': 8, 'confidence': 0.7}
        elif small_count > 0:
            return {'employees': 5, 'confidence': 0.8}
        else:
            return {'employees': 6, 'confidence': 0.5}  # Default conservative
    
    def _classify_business_type(self, company: Dict) -> str:
        """
        Enhanced business classification for North American premium market
        Includes professional services beyond healthcare
        """
        name = company.get('name', '').lower()
        description = company.get('description', '').lower()
        website = company.get('website', '').lower()
        
        text = f"{name} {description} {website}"
        
        # Healthcare services
        if any(term in text for term in ['dental', 'dentist', 'orthodont', 'periodon']):
            return 'dental'
        elif any(term in text for term in ['medical', 'physician', 'doctor', 'clinic', 'family practice']):
            return 'medical'
        elif any(term in text for term in ['beauty', 'aesthetic', 'cosmetic', 'med spa', 'botox']):
            return 'beauty'
        elif any(term in text for term in ['physio', 'physical therapy', 'rehabilitation', 'sports therapy']):
            return 'physiotherapy'
        elif any(term in text for term in ['chiropract', 'chiro', 'spinal', 'wellness center']):
            return 'chiropractic'
        elif any(term in text for term in ['optometry', 'optometrist', 'eye care', 'vision']):
            return 'optometry'
        
        # Professional services (high-value North American market)
        elif any(term in text for term in ['law firm', 'lawyer', 'attorney', 'legal', 'barrister']):
            return 'legal'
        elif any(term in text for term in ['accounting', 'accountant', 'cpa', 'bookkeeping', 'tax']):
            return 'accounting'
        elif any(term in text for term in ['real estate', 'realtor', 'property', 'realty']):
            return 'real_estate'
        elif any(term in text for term in ['consulting', 'consultant', 'advisory', 'professional services']):
            return 'consulting'
        elif any(term in text for term in ['financial', 'investment', 'wealth management', 'financial planning']):
            return 'financial_services'
        
        # Default professional services
        else:
            return 'other_professional'
    
    def _estimate_business_revenue_conservative(self, size_analysis: Dict, business_type: str, company: Dict) -> Dict:
        """
        Conservative revenue estimation for North American premium market
        CAD/USD with higher purchasing power and premium positioning
        """
        employees = size_analysis['employees']
        
        # Detect market (Canadian or US fallback)
        website = company.get('website', '').lower()
        description = company.get('description', '').lower()
        name = company.get('name', '').lower()
        
        content = f"{website} {description} {name}"
        is_canadian = '.ca' in content or any(city in content for city in 
                                            ['vancouver', 'toronto', 'calgary', 'montreal', 'ottawa', 'ontario'])
        
        # Revenue per employee by business type (premium North American market)
        if is_canadian:
            # Canadian market - higher purchasing power, less competition
            revenue_multipliers = {
                'dental': 145000,      # CAD $12k/month per employee
                'medical': 120000,     # CAD $10k/month per employee
                'beauty': 85000,       # CAD $7.1k/month per employee
                'physiotherapy': 95000, # CAD $7.9k/month per employee
                'chiropractic': 105000, # CAD $8.8k/month per employee
                'optometry': 125000,   # CAD $10.4k/month per employee
                'legal': 180000,       # CAD $15k/month per employee
                'accounting': 130000,  # CAD $10.8k/month per employee
                'real_estate': 110000, # CAD $9.2k/month per employee
                'other_professional': 95000  # CAD $7.9k/month per employee
            }
            currency = 'CAD'
        else:
            # US fallback market - cross-border premium
            revenue_multipliers = {
                'dental': 130000,      # USD $10.8k/month per employee
                'medical': 110000,     # USD $9.2k/month per employee
                'beauty': 75000,       # USD $6.25k/month per employee
                'physiotherapy': 85000, # USD $7.1k/month per employee
                'chiropractic': 95000,  # USD $7.9k/month per employee
                'optometry': 115000,   # USD $9.6k/month per employee
                'legal': 165000,       # USD $13.8k/month per employee
                'accounting': 120000,  # USD $10k/month per employee
                'real_estate': 100000, # USD $8.3k/month per employee
                'other_professional': 85000  # USD $7.1k/month per employee
            }
            currency = 'USD'
        
        annual_revenue_per_employee = revenue_multipliers.get(business_type, revenue_multipliers['other_professional'])
        annual_revenue = employees * annual_revenue_per_employee
        monthly_revenue = annual_revenue / 12
        
        # Higher confidence for North American market due to better data
        confidence = size_analysis['confidence'] * 0.85
        
        return {
            'monthly_revenue': monthly_revenue,
            'annual_revenue': annual_revenue,
            'currency': currency,
            'market_premium': 'canadian' if is_canadian else 'us_cross_border',
            'confidence': confidence
        }
    
    def _estimate_marketing_spend_conservative(self, revenue_analysis: Dict, business_type: str, company: Dict) -> Dict:
        """Conservative marketing spend estimation"""
        monthly_revenue = revenue_analysis['monthly_revenue']
        
        # Marketing spend as % of revenue (conservative)
        spend_percentages = {
            'dental': 0.03,        # 3%
            'beauty': 0.04,        # 4%
            'medical': 0.02,       # 2%
            'physiotherapy': 0.025, # 2.5%
            'chiropractic': 0.03,   # 3%
            'optometry': 0.025,     # 2.5%
            'veterinary': 0.025,    # 2.5%
            'other_healthcare': 0.025  # 2.5%
        }
        
        base_percentage = spend_percentages.get(business_type, 0.025)
        
        # Adjust based on digital sophistication signals
        description = company.get('description', '').lower()
        digital_signals = ['website', 'online', 'digital', 'booking', 'appointment']
        signal_count = sum(1 for signal in digital_signals if signal in description)
        
        # Boost spend if more digital signals
        adjusted_percentage = base_percentage * (1 + signal_count * 0.1)
        
        monthly_spend = monthly_revenue * adjusted_percentage
        confidence = revenue_analysis['confidence'] * 0.9  # Slightly more uncertain
        
        return {
            'monthly_spend': monthly_spend,
            'percentage_of_revenue': adjusted_percentage,
            'confidence': confidence
        }
    
    def _analyze_opportunity_conservative(self, business_type: str, marketing_analysis: Dict, discovery_query: str) -> Dict:
        """Conservative opportunity analysis"""
        monthly_spend = marketing_analysis['monthly_spend']
        
        # Opportunity types based on discovery query patterns
        if 'book appointment' in discovery_query and 'contact' in discovery_query:
            opportunity_type = 'Booking conversion optimization'
            impact_multiplier = 0.15  # 15% improvement potential
        elif 'consultation' in discovery_query and 'call' in discovery_query:
            opportunity_type = 'Lead qualification optimization'
            impact_multiplier = 0.12  # 12% improvement potential
        elif 'phone' in discovery_query or 'contact form' in discovery_query:
            opportunity_type = 'Contact method optimization'
            impact_multiplier = 0.10  # 10% improvement potential
        else:
            opportunity_type = 'General conversion optimization'
            impact_multiplier = 0.08  # 8% improvement potential
        
        # Conservative impact calculation
        conservative_impact = monthly_spend * impact_multiplier * 0.7  # 70% of theoretical
        
        # Confidence based on business type and discovery pattern match
        business_confidence = {
            'dental': 0.8,
            'beauty': 0.7,
            'medical': 0.8,
            'physiotherapy': 0.6,
            'chiropractic': 0.6,
            'optometry': 0.7,
            'veterinary': 0.6,
            'other_healthcare': 0.5
        }
        
        confidence = business_confidence.get(business_type, 0.5) * marketing_analysis['confidence']
        
        return {
            'opportunity_type': opportunity_type,
            'conservative_impact': conservative_impact,
            'impact_multiplier': impact_multiplier,
            'confidence': confidence
        }
    
    def _calculate_overall_fit_score(self, size_analysis: Dict, revenue_analysis: Dict, 
                                   marketing_analysis: Dict, opportunity_analysis: Dict) -> float:
        """Calculate overall prospect fit score (0-1)"""
        
        # Size score (optimal around 5-8 employees)
        employees = size_analysis['employees']
        if 4 <= employees <= 9:
            size_score = 1.0
        elif 3 <= employees <= 12:
            size_score = 0.8
        else:
            size_score = 0.5
        
        # Revenue score (higher is better, up to a point)
        monthly_revenue = revenue_analysis['monthly_revenue']
        if monthly_revenue >= 50000:
            revenue_score = 1.0
        elif monthly_revenue >= 30000:
            revenue_score = 0.9
        elif monthly_revenue >= 20000:
            revenue_score = 0.8
        elif monthly_revenue >= 15000:
            revenue_score = 0.6
        else:
            revenue_score = 0.3
        
        # Marketing spend score
        monthly_spend = marketing_analysis['monthly_spend']
        if monthly_spend >= 2000:
            marketing_score = 1.0
        elif monthly_spend >= 1500:
            marketing_score = 0.9
        elif monthly_spend >= 1000:
            marketing_score = 0.8
        elif monthly_spend >= 500:
            marketing_score = 0.6
        else:
            marketing_score = 0.3
        
        # Opportunity score
        opportunity_score = opportunity_analysis['confidence']
        
        # Weighted average
        overall_score = (
            size_score * 0.2 +
            revenue_score * 0.3 +
            marketing_score * 0.3 +
            opportunity_score * 0.2
        )
        
        return round(overall_score, 3)
    
    # Utility methods
    def _extract_domain(self, url: str) -> str:
        """Extract clean domain from URL"""
        if not url:
            return ""
        
        # Remove protocol and www
        domain = url.lower().replace('https://', '').replace('http://', '').replace('www.', '')
        domain = domain.split('/')[0].split('?')[0]
        
        return domain
    
    def _validate_market_domain(self, domain: str, market: str) -> bool:
        """Validate domain belongs to target market"""
        market_tlds = {
            'australia': ['.au', '.com.au'],
            'canada': ['.ca'],
            'new_zealand': ['.nz', '.co.nz'],
            'ireland': ['.ie']
        }
        
        return any(domain.endswith(tld) for tld in market_tlds.get(market, []))

# Main execution function
async def execute_pragmatic_discovery(market: str = 'north_america_west') -> Dict:
    """
    Execute pragmatic prospect discovery for North America West Coast
    Primary: Canada (Vancouver, Toronto, Ontario, Calgary, Montreal)
    Fallback: USA Cross-Border (Seattle, Buffalo, Denver, Portland)
    """
    
    discovery = PragmaticProspectDiscovery()
    
    # Initialize
    if not await discovery.initialize_apis():
        return {}
    
    # Discover prospects with higher yield for premium market
    prospects = await discovery.discover_prospects(market, max_per_query=12)
    
    if not prospects:
        print("No prospects found")
        return {}
    
    # Analyze conservatively
    analyzed_prospects = await discovery.analyze_prospects_conservative(prospects)
    
    if not analyzed_prospects:
        print("No prospects passed conservative analysis")
        return {}
    
    # Generate summary
    summary = {
        'market': market,
        'total_prospects_found': len(prospects),
        'qualified_prospects': len(analyzed_prospects),
        'qualification_rate': len(analyzed_prospects) / len(prospects),
        'top_prospects': analyzed_prospects[:10],
        'all_prospects': analyzed_prospects,  # SAVE ALL PROSPECTS FOR CRM
        'total_pipeline_value': sum(p['estimated_monthly_impact'] for p in analyzed_prospects),
        'avg_fit_score': sum(p['overall_fit_score'] for p in analyzed_prospects) / len(analyzed_prospects),
        'execution_timestamp': datetime.now().isoformat()
    }
    
    # Display results
    print(f"\n" + "="*60)
    print(f"🎯 PRAGMATIC DISCOVERY COMPLETE - {market.upper()}")
    print(f"="*60)
    print(f"📊 Prospects Found: {len(prospects)}")
    print(f"✅ Qualified: {len(analyzed_prospects)} ({summary['qualification_rate']:.1%})")
    print(f"💰 Total Pipeline Value: ${summary['total_pipeline_value']:,.0f}/month")
    print(f"⭐ Avg Fit Score: {summary['avg_fit_score']:.2f}/1.0")
    
    print(f"\n🔥 TOP 5 PROSPECTS:")
    for i, prospect in enumerate(analyzed_prospects[:5], 1):
        print(f"   {i}. {prospect['company_name'][:35]}")
        print(f"      Business: {prospect['business_type']} | Employees: {prospect['estimated_employees']}")
        print(f"      Revenue: ${prospect['estimated_monthly_revenue']:,.0f}/mo | Marketing: ${prospect['estimated_monthly_marketing_spend']:,.0f}/mo")
        print(f"      Opportunity: {prospect['opportunity_type']}")
        print(f"      Impact: ${prospect['estimated_monthly_impact']:,.0f}/mo | Fit: {prospect['overall_fit_score']:.2f}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_path = Path("src/data") / f"pragmatic_discovery_{market}_{timestamp}.json"
    results_path.parent.mkdir(exist_ok=True)
    
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved: {results_path}")
    
    return summary

if __name__ == "__main__":
    # Execute optimized North America West Coast discovery
    results = asyncio.run(execute_pragmatic_discovery('north_america_west'))
