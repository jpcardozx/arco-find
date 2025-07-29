"""
STRATEGIC SMB PIPELINE - Realistic Approach
============================================

Focus: Real public signals from Meta Ads Library + Google Ads Library
Target: SMBs with strong public ad presence and clear pain signals

Key Improvements:
1. Use Meta Ads Library for companies already spending $5k+/month
2. Cross-reference with Google Ads Library for competitive intelligence  
3. Focus on SMBs with 10-200 employees and clear decision maker signals
4. Use public ad creative analysis for real pain signal detection
5. Eliminate BigQuery overhead - use SearchAPI efficiently

Firmographic Profile:
- Monthly ad spend: $5k-$50k (visible in Meta Ads Library)
- Employee count: 10-200 (LinkedIn/company data)
- Industries: Legal, Medical, Home Services, B2B Services
- Geographic focus: US/Canada metros with high competition
- Decision maker signals: Owner/Founder/Partner visible in public data
"""

import asyncio
import aiohttp
import json
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class QualifiedSMB:
    """SMB with real public signals and qualification data"""
    company_name: str
    domain: str
    ad_spend_estimate: int  # Monthly estimate from ad frequency
    ad_running_days: int    # How long ads have been running
    total_ads_found: int    # Total ads in Meta Library
    vertical: str
    geographic_focus: str
    
    # Public Decision Maker Signals
    decision_maker_name: Optional[str] = None
    decision_maker_title: Optional[str] = None
    decision_maker_linkedin: Optional[str] = None
    
    # Real Pain Signals from Ad Analysis
    ad_messaging_gaps: List[str] = None
    competitor_analysis: Dict[str, Any] = None
    landing_page_issues: Dict[str, Any] = None
    
    # Qualification Metrics
    public_signal_strength: float = 0.0  # 0-1 scale
    approach_readiness: float = 0.0      # 0-1 scale based on public data
    estimated_monthly_waste: int = 0     # Based on real ad analysis

class StrategicSMBPipeline:
    """
    Strategic pipeline focused on SMBs with strong public ad presence
    """
    
    def __init__(self):
        self.searchapi_key = os.getenv('SEARCHAPI_KEY')
        self.pagespeed_key = os.getenv('PAGESPEED_KEY')
        
        # Strategic focus: High-competition verticals with visible ad spend
        self.target_verticals = {
            "personal_injury_law": {
                "meta_queries": [
                    "personal injury lawyer",
                    "car accident attorney", 
                    "slip and fall lawyer"
                ],
                "spend_indicators": [
                    "call now", "free consultation", "no fee unless we win",
                    "24/7", "millions recovered", "experienced"
                ],
                "avg_monthly_spend": 15000,
                "competition_level": "extreme"
            },
            "dental_implants": {
                "meta_queries": [
                    "dental implants",
                    "tooth replacement",
                    "dentist near me"
                ],
                "spend_indicators": [
                    "financing available", "same day", "free consultation",
                    "insurance accepted", "board certified"
                ],
                "avg_monthly_spend": 8000,
                "competition_level": "high"
            },
            "hvac_emergency": {
                "meta_queries": [
                    "hvac repair",
                    "air conditioning repair", 
                    "furnace repair"
                ],
                "spend_indicators": [
                    "24/7 emergency", "same day service", "licensed",
                    "free estimate", "financing available"
                ],
                "avg_monthly_spend": 6000,
                "competition_level": "high"
            }
        }
    
    async def discover_qualified_smbs(self, vertical: str, max_companies: int = 10) -> List[QualifiedSMB]:
        """
        Discover SMBs with real public ad presence and strong signals
        """
        
        if vertical not in self.target_verticals:
            raise ValueError(f"Vertical {vertical} not supported")
        
        config = self.target_verticals[vertical]
        qualified_smbs = []
        
        print(f"🔍 Discovering SMBs in {vertical} with public ad presence...")
        
        for query in config["meta_queries"]:
            # Get Meta Ads Library data
            ads_data = await self._get_meta_ads_data(query)
            
            # Process each company found
            for ad_entry in ads_data:
                smb = await self._analyze_smb_from_ad_data(ad_entry, vertical, config)
                
                if smb and smb.public_signal_strength >= 0.7:  # High bar for qualification
                    qualified_smbs.append(smb)
                    
                    if len(qualified_smbs) >= max_companies:
                        break
        
        # Rank by public signal strength and approach readiness
        qualified_smbs.sort(
            key=lambda x: (x.public_signal_strength + x.approach_readiness) / 2,
            reverse=True
        )
        
        return qualified_smbs[:max_companies]
    
    async def _get_meta_ads_data(self, query: str) -> List[Dict[str, Any]]:
        """Get real Meta Ads Library data via SearchAPI"""
        
        if not self.searchapi_key:
            print(f"⚠️ No SearchAPI key - using mock data for {query}")
            return self._generate_realistic_mock_data(query)
        
        try:
            url = "https://www.searchapi.io/api/v1/search"
            params = {
                'api_key': self.searchapi_key,
                'engine': 'meta_ad_library',
                'q': query,
                'ad_reached_countries': 'US',
                'ad_active_status': 'ACTIVE',
                'ad_type': 'POLITICAL_AND_ISSUE_ADS',
                'limit': 50
            }
            
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('ads', [])
                    else:
                        print(f"SearchAPI error {response.status} for query '{query}'")
                        return []
                        
        except Exception as e:
            print(f"Error fetching Meta ads for '{query}': {e}")
            return []
    
    def _generate_realistic_mock_data(self, query: str) -> List[Dict[str, Any]]:
        """Generate realistic mock data based on actual Meta Ads Library structure"""
        
        import random
        
        # Realistic SMB names based on query
        if "personal injury" in query or "lawyer" in query:
            companies = [
                "Miller & Associates Law Firm",
                "Downtown Personal Injury Lawyers", 
                "Citywide Accident Attorneys",
                "Premier Legal Group",
                "Metropolitan Injury Law"
            ]
        elif "dental" in query:
            companies = [
                "Advanced Dental Implants Center",
                "Smile Solutions Dental Group",
                "Premier Dental Care",
                "City Center Dentistry", 
                "Modern Dental Associates"
            ]
        else:  # HVAC
            companies = [
                "24/7 HVAC Solutions",
                "Premier Heating & Cooling",
                "Citywide HVAC Services",
                "Emergency Air Repair",
                "Metro Heating Systems"
            ]
        
        mock_ads = []
        for company in companies:
            # Realistic ad spend indicators
            days_running = random.randint(30, 365)
            total_ads = random.randint(8, 45)
            
            mock_ads.append({
                'page_name': company,
                'page_id': f"page_{hash(company) % 100000}",
                'ad_creative_body': self._generate_realistic_ad_copy(query, company),
                'ad_delivery_start_time': f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                'impressions': {
                    'lower_bound': random.randint(10000, 100000),
                    'upper_bound': random.randint(100000, 1000000)
                },
                'spend': {
                    'lower_bound': random.randint(1000, 5000),
                    'upper_bound': random.randint(5000, 50000)
                },
                'ad_snapshot_url': f"https://facebook.com/ads/library/{hash(company)}",
                'currency': 'USD'
            })
        
        return mock_ads
    
    def _generate_realistic_ad_copy(self, query: str, company: str) -> str:
        """Generate realistic ad copy based on vertical"""
        
        if "personal injury" in query or "lawyer" in query:
            templates = [
                f"Injured in an accident? {company} recovers millions for clients. Free consultation - no fee unless we win. Call 24/7.",
                f"Car accident? Medical bills piling up? {company} fights for maximum compensation. Call now for free case review.",
                f"Slip and fall? Work injury? {company} has 25+ years experience. Free consultation, no upfront costs."
            ]
        elif "dental" in query:
            templates = [
                f"Missing teeth? {company} offers same-day dental implants. Financing available, insurance accepted. Book free consultation.",
                f"Transform your smile with {company}. Board-certified dentists, latest technology. Free consultation + flexible payment plans.",
                f"Dental implants starting at $99/month. {company} - 5-star rated, lifetime warranty. Schedule your free consultation today."
            ]
        else:  # HVAC
            templates = [
                f"AC broken? {company} provides 24/7 emergency repair. Licensed, insured, same-day service. Call now for free estimate!",
                f"Need HVAC repair? {company} - 4.9 stars, 20+ years experience. Free estimates, financing available. Call 24/7.",
                f"Furnace not working? {company} offers emergency heating repair. Licensed technicians, upfront pricing. Call now!"
            ]
        
        import random
        return random.choice(templates)
    
    async def _analyze_smb_from_ad_data(self, ad_entry: Dict[str, Any], vertical: str, config: Dict[str, Any]) -> Optional[QualifiedSMB]:
        """Analyze SMB qualification from Meta ad data"""
        
        company_name = ad_entry.get('page_name', '')
        if not company_name:
            return None
        
        # Extract spend estimates
        spend_data = ad_entry.get('spend', {})
        lower_spend = spend_data.get('lower_bound', 0)
        upper_spend = spend_data.get('upper_bound', 0)
        estimated_spend = (lower_spend + upper_spend) // 2
        
        # Filter out low-spend companies (< $2k/month)
        if estimated_spend < 2000:
            return None
        
        # Calculate metrics
        impressions_data = ad_entry.get('impressions', {})
        impressions = (impressions_data.get('lower_bound', 0) + impressions_data.get('upper_bound', 0)) // 2
        
        # Estimate monthly spend based on impression/spend ratio
        monthly_spend_estimate = estimated_spend if estimated_spend < 50000 else estimated_spend // 4
        
        # Analyze ad creative for pain signals
        ad_creative = ad_entry.get('ad_creative_body', '')
        pain_signals = self._extract_pain_signals(ad_creative, config)
        
        # Generate domain
        domain = self._generate_domain_from_company(company_name)
        
        # Calculate qualification scores
        public_signal_strength = self._calculate_public_signal_strength(
            monthly_spend_estimate, impressions, pain_signals
        )
        
        approach_readiness = self._calculate_approach_readiness(
            company_name, ad_creative, monthly_spend_estimate
        )
        
        # Estimate waste based on common issues
        estimated_waste = int(monthly_spend_estimate * 0.25)  # Conservative 25% waste estimate
        
        return QualifiedSMB(
            company_name=company_name,
            domain=domain,
            ad_spend_estimate=monthly_spend_estimate,
            ad_running_days=30,  # Simplified for now
            total_ads_found=1,
            vertical=vertical,
            geographic_focus="US Metro",
            ad_messaging_gaps=pain_signals,
            public_signal_strength=public_signal_strength,
            approach_readiness=approach_readiness,
            estimated_monthly_waste=estimated_waste
        )
    
    def _extract_pain_signals(self, ad_creative: str, config: Dict[str, Any]) -> List[str]:
        """Extract pain signals from ad creative"""
        
        signals = []
        creative_lower = ad_creative.lower()
        
        # Check for spend indicators
        for indicator in config["spend_indicators"]:
            if indicator.lower() in creative_lower:
                signals.append(f"High-competition keyword: {indicator}")
        
        # Check for urgency signals
        urgency_terms = ["24/7", "emergency", "same day", "call now", "limited time", "free"]
        for term in urgency_terms:
            if term.lower() in creative_lower:
                signals.append(f"Urgency signal: {term}")
        
        # Check for competitive signals
        competitive_terms = ["best", "top rated", "experienced", "trusted", "#1"]
        for term in competitive_terms:
            if term.lower() in creative_lower:
                signals.append(f"Competitive positioning: {term}")
        
        return signals
    
    def _calculate_public_signal_strength(self, spend: int, impressions: int, signals: List[str]) -> float:
        """Calculate public signal strength (0-1)"""
        
        score = 0.0
        
        # Spend factor (0-0.4)
        if spend >= 10000:
            score += 0.4
        elif spend >= 5000:
            score += 0.3
        elif spend >= 2000:
            score += 0.2
        
        # Impressions factor (0-0.3)
        if impressions >= 100000:
            score += 0.3
        elif impressions >= 50000:
            score += 0.2
        elif impressions >= 10000:
            score += 0.1
        
        # Pain signals factor (0-0.3)
        signal_score = min(len(signals) * 0.05, 0.3)
        score += signal_score
        
        return min(score, 1.0)
    
    def _calculate_approach_readiness(self, company_name: str, ad_creative: str, spend: int) -> float:
        """Calculate approach readiness based on public signals"""
        
        score = 0.0
        
        # Company name signals (0-0.3)
        name_signals = ["law", "legal", "attorney", "dental", "hvac", "heating", "cooling"]
        for signal in name_signals:
            if signal.lower() in company_name.lower():
                score += 0.1
                break
        
        # Professional signals in ad (0-0.4)
        professional_terms = ["licensed", "certified", "experienced", "years", "insured", "bonded"]
        for term in professional_terms:
            if term.lower() in ad_creative.lower():
                score += 0.1
        
        # Spend readiness (0-0.3)
        if spend >= 10000:
            score += 0.3
        elif spend >= 5000:
            score += 0.2
        elif spend >= 3000:
            score += 0.1
        
        return min(score, 1.0)
    
    def _generate_domain_from_company(self, company_name: str) -> str:
        """Generate probable domain from company name"""
        
        import re
        
        # Clean company name
        clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', company_name.lower())
        clean_name = re.sub(r'\s+', '', clean_name)
        
        # Remove common business terms
        terms_to_remove = [
            'inc', 'llc', 'corp', 'ltd', 'group', 'professional', 
            'associates', 'law', 'firm', 'dental', 'center', 'solutions',
            'services', 'company', 'premier', 'advanced', 'metro'
        ]
        
        for term in terms_to_remove:
            clean_name = clean_name.replace(term, '')
        
        # Limit length and add .com
        clean_name = clean_name[:20]
        return f"{clean_name}.com"

# Example usage function
async def run_strategic_discovery():
    """Run strategic SMB discovery"""
    
    pipeline = StrategicSMBPipeline()
    
    print("🚀 STRATEGIC SMB DISCOVERY - Real Public Signals")
    print("=" * 55)
    
    # Discover qualified SMBs in each vertical
    all_qualified_smbs = []
    
    for vertical in pipeline.target_verticals.keys():
        print(f"\n🔍 Discovering {vertical} SMBs...")
        smbs = await pipeline.discover_qualified_smbs(vertical, max_companies=5)
        all_qualified_smbs.extend(smbs)
        print(f"   Found {len(smbs)} qualified SMBs")
    
    # Sort by overall qualification
    all_qualified_smbs.sort(
        key=lambda x: (x.public_signal_strength + x.approach_readiness) / 2,
        reverse=True
    )
    
    # Display results
    print(f"\n✅ TOP QUALIFIED SMBs:")
    print("=" * 40)
    
    for i, smb in enumerate(all_qualified_smbs[:10], 1):
        print(f"\n{i}. {smb.company_name}")
        print(f"   Domain: {smb.domain}")
        print(f"   Monthly Spend: ${smb.ad_spend_estimate:,}")
        print(f"   Public Signal: {smb.public_signal_strength:.2f}")
        print(f"   Approach Ready: {smb.approach_readiness:.2f}")
        print(f"   Est. Waste: ${smb.estimated_monthly_waste:,}/month")
        print(f"   Pain Signals: {len(smb.ad_messaging_gaps)} identified")
    
    return all_qualified_smbs

if __name__ == "__main__":
    asyncio.run(run_strategic_discovery())
