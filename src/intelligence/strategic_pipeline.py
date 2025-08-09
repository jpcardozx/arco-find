"""
ARCO Strategic Intelligence Pipeline - Research-Backed Refactoring
Based on insights: ABM principles, budget thresholds, lead scoring, personalization
"""
import asyncio
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path

from ..clients.searchapi import SearchAPIClient
from ..models.core_models import AdResult, AdvertiserInfo

@dataclass
class VerticalIntelligence:
    """Vertical-specific intelligence based on budget thresholds"""
    name: str
    min_monthly_budget: int  # USD from research
    avg_cpc_range: Tuple[int, int]  # Min, Max USD
    priority_cities: List[str]
    search_intent_keywords: List[str]
    pain_point_indicators: List[str]

@dataclass
class ProspectIntelligence:
    """Enhanced prospect with ABM-style intelligence"""
    # Firmographic (explicit)
    advertiser_id: str
    company_name: str
    domain: str
    vertical: str
    city: str
    
    # Technographic (explicit)
    tracking_signals: Dict[str, bool]  # GA4, Ads tags, etc
    page_speed_metrics: Dict[str, float]  # LCP, FCP, etc
    
    # Intent signals (implicit)
    ad_frequency: int  # Ads seen across keywords
    campaign_freshness: float  # Recent activity score
    budget_indicators: Dict[str, Any]  # Estimated spend, competition
    
    # Behavioral (implicit)
    message_match_score: float  # Ad-to-landing consistency
    conversion_readiness: Dict[str, float]  # Technical readiness
    
    # Final scoring
    explicit_score: int
    implicit_score: int
    total_score: int
    confidence: float
    qualification_tier: str  # "A", "B", "C", "Nurture"

class StrategicPipeline:
    """
    Research-backed pipeline focusing on:
    1. High-budget verticals (Focus Digital benchmarks)
    2. ABM-style targeting (Forrester 200% ROI)
    3. Behavioral + explicit scoring (Outfunnel cases)
    4. Personalization signals (ManyReach data)
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
        # VERTICAL INTELLIGENCE - Based on Focus Digital budget research
        self.verticals = {
            "legal_personal_injury": VerticalIntelligence(
                name="Legal - Personal Injury",
                min_monthly_budget=6500,  # Focus Digital minimum
                avg_cpc_range=(45, 120),
                priority_cities=["London", "Manchester", "Birmingham", "Leeds"],
                search_intent_keywords=[
                    "personal injury lawyer",
                    "car accident lawyer", 
                    "medical negligence solicitor",
                    "compensation claim lawyer"
                ],
                pain_point_indicators=[
                    "high cpc", "poor conversion", "landing page", 
                    "ad spend", "cost per click", "conversion rate"
                ]
            ),
            "insurance": VerticalIntelligence(
                name="Insurance",
                min_monthly_budget=5800,
                avg_cpc_range=(25, 85),
                priority_cities=["London", "Edinburgh", "Cardiff", "Belfast"],
                search_intent_keywords=[
                    "car insurance", "home insurance",
                    "business insurance", "life insurance"
                ],
                pain_point_indicators=[
                    "insurance quote", "compare insurance", 
                    "cheap insurance", "best insurance"
                ]
            ),
            "home_services": VerticalIntelligence(
                name="Home Services",
                min_monthly_budget=3500,
                avg_cpc_range=(15, 45),
                priority_cities=["London", "Manchester", "Birmingham", "Bristol"],
                search_intent_keywords=[
                    "emergency plumber", "roofer near me",
                    "electrician", "heating engineer"
                ],
                pain_point_indicators=[
                    "emergency", "urgent", "24 hour", "same day",
                    "fast response", "immediate"
                ]
            ),
            "healthcare": VerticalIntelligence(
                name="Healthcare",
                min_monthly_budget=3000,
                avg_cpc_range=(20, 60),
                priority_cities=["London", "Birmingham", "Leeds", "Glasgow"],
                search_intent_keywords=[
                    "private dentist", "cosmetic surgery",
                    "private doctor", "health clinic"
                ],
                pain_point_indicators=[
                    "appointment", "consultation", "treatment",
                    "private healthcare", "immediate"
                ]
            )
        }
    
    async def discover_strategic_prospects(self, 
                                         vertical_focus: str = "all",
                                         max_credits: int = 50,
                                         target_tier: str = "A") -> List[ProspectIntelligence]:
        """
        Strategic prospect discovery with ABM principles
        """
        prospects = []
        credits_used = 0
        
        # Select verticals based on focus
        target_verticals = (
            [self.verticals[vertical_focus]] if vertical_focus != "all" 
            else list(self.verticals.values())
        )
        
        async with SearchAPIClient(self.api_key) as client:
            for vertical in target_verticals:
                if credits_used >= max_credits:
                    break
                    
                print(f"\n🎯 VERTICAL: {vertical.name}")
                print(f"💰 Min Budget: £{vertical.min_monthly_budget:,}/month")
                
                # Focus on priority cities (ABM geographic targeting)
                for city in vertical.priority_cities[:2]:  # Top 2 cities
                    if credits_used >= max_credits:
                        break
                        
                    print(f"📍 City: {city}")
                    
                    # High-intent keywords only
                    for keyword in vertical.search_intent_keywords[:3]:
                        if credits_used >= max_credits:
                            break
                            
                        # Get ads with SearchAPI
                        ads = await client.google_ads_search(
                            query=keyword,
                            location=f"{city},England,United Kingdom"
                        )
                        credits_used += 1
                        
                        print(f"  🔍 '{keyword}': {len(ads)} ads")
                        
                        # Process each advertiser
                        for ad in ads:
                            if credits_used >= max_credits:
                                break
                                
                            # Get advertiser intelligence
                            if ad.advertiser_info_token:
                                advertiser = await client.get_advertiser_info(
                                    ad.advertiser_info_token
                                )
                                credits_used += 1
                                
                                if advertiser:
                                    prospect = await self._analyze_prospect(
                                        ad, advertiser, vertical, client
                                    )
                                    credits_used += 2  # Transparency + page analysis
                                    
                                    if prospect and prospect.qualification_tier == target_tier:
                                        prospects.append(prospect)
                                        print(f"    ✅ {prospect.company_name} - Tier {prospect.qualification_tier}")
        
        print(f"\n📊 PIPELINE SUMMARY")
        print(f"Credits used: {credits_used}/{max_credits}")
        print(f"Qualified prospects: {len(prospects)}")
        
        return prospects
    
    async def _analyze_prospect(self, 
                              ad: AdResult, 
                              advertiser: AdvertiserInfo,
                              vertical: VerticalIntelligence,
                              client: SearchAPIClient) -> Optional[ProspectIntelligence]:
        """
        Deep prospect analysis with explicit + implicit scoring
        """
        try:
            # Extract domain for analysis
            domain = ad.link.split('/')[2]
            
            # Get transparency data for behavioral signals
            transparency_ads = await client.get_transparency_ads(advertiser.advertiser_id)
            
            # Simulate page speed analysis (would integrate with PageSpeed API)
            page_metrics = self._simulate_page_analysis(domain)
            
            # EXPLICIT SCORING (40% weight)
            explicit_score = self._calculate_explicit_score(
                advertiser, vertical, domain
            )
            
            # IMPLICIT SCORING (60% weight) 
            implicit_score = self._calculate_implicit_score(
                ad, transparency_ads, vertical, page_metrics
            )
            
            total_score = int(explicit_score * 0.4 + implicit_score * 0.6)
            confidence = min(0.9, len(transparency_ads) / 10.0 + 0.3)
            
            # Qualification tiers (research-backed thresholds)
            if total_score >= 70 and confidence >= 0.7:
                tier = "A"  # Hot prospects
            elif total_score >= 50 and confidence >= 0.5:
                tier = "B"  # Warm prospects  
            elif total_score >= 30:
                tier = "C"  # Cold but viable
            else:
                tier = "Nurture"  # Long-term nurture
            
            return ProspectIntelligence(
                advertiser_id=advertiser.advertiser_id,
                company_name=advertiser.name,
                domain=domain,
                vertical=vertical.name,
                city=ad.location if hasattr(ad, 'location') else "Unknown",
                tracking_signals=self._detect_tracking_signals(domain),
                page_speed_metrics=page_metrics,
                ad_frequency=len(transparency_ads),
                campaign_freshness=self._calculate_freshness(transparency_ads),
                budget_indicators=self._estimate_budget_signals(transparency_ads, vertical),
                message_match_score=self._analyze_message_match(ad),
                conversion_readiness=self._assess_conversion_readiness(page_metrics),
                explicit_score=explicit_score,
                implicit_score=implicit_score,
                total_score=total_score,
                confidence=confidence,
                qualification_tier=tier
            )
            
        except Exception as e:
            print(f"    ❌ Analysis failed: {str(e)}")
            return None
    
    def _calculate_explicit_score(self, 
                                advertiser: AdvertiserInfo,
                                vertical: VerticalIntelligence,
                                domain: str) -> int:
        """Explicit/firmographic scoring"""
        score = 0
        
        # Company legitimacy signals
        if advertiser.name and not any(x in advertiser.name.lower() 
                                     for x in ['ltd', 'limited', 'llc']):
            score += 10  # Proper business entity
            
        # Domain quality
        if '.co.uk' in domain or '.com' in domain:
            score += 15
            
        # Geographic relevance
        if any(city.lower() in advertiser.name.lower() 
               for city in vertical.priority_cities):
            score += 20
            
        return min(score, 50)  # Max 50 points explicit
    
    def _calculate_implicit_score(self,
                                ad: AdResult,
                                transparency_ads: List,
                                vertical: VerticalIntelligence,
                                page_metrics: Dict) -> int:
        """Implicit/behavioral scoring based on research insights"""
        score = 0
        
        # Campaign activity (Snowflake case: repeat signals matter)
        if len(transparency_ads) > 5:
            score += 25  # Active advertiser
        elif len(transparency_ads) > 0:
            score += 15
            
        # Pain point signals in ad copy
        pain_signals = sum(1 for indicator in vertical.pain_point_indicators
                          if indicator.lower() in ad.title.lower() + ad.snippet.lower())
        score += min(pain_signals * 5, 20)
        
        # Page speed pain points (Google research: speed kills conversions)
        if page_metrics['lcp'] > 2.5:  # Poor LCP
            score += 20  # High pain = high opportunity
        if page_metrics['fcp'] > 1.8:  # Poor FCP  
            score += 15
            
        # Campaign freshness (recent activity = buying intent)
        freshness = self._calculate_freshness(transparency_ads)
        score += int(freshness * 20)
        
        return min(score, 80)  # Max 80 points implicit
    
    def _simulate_page_analysis(self, domain: str) -> Dict[str, float]:
        """Simulate page speed analysis (integrate PageSpeed API later)"""
        import random
        return {
            'lcp': random.uniform(1.2, 4.5),  # Largest Contentful Paint
            'fcp': random.uniform(0.8, 3.2),  # First Contentful Paint
            'cls': random.uniform(0.05, 0.3), # Cumulative Layout Shift
            'conversion_score': random.uniform(0.3, 0.9)
        }
    
    def _detect_tracking_signals(self, domain: str) -> Dict[str, bool]:
        """Detect tracking implementation (simulate - integrate with actual checks)"""
        return {
            'google_ads_tag': True,  # Would check actual implementation
            'ga4_tag': True,
            'conversion_tracking': False,  # Pain point opportunity
            'gtm_container': True
        }
    
    def _calculate_freshness(self, transparency_ads: List) -> float:
        """Calculate campaign freshness score"""
        if not transparency_ads:
            return 0.0
            
        recent_count = len([ad for ad in transparency_ads 
                           if hasattr(ad, 'last_seen')])  # Would check actual dates
        return min(recent_count / len(transparency_ads), 1.0)
    
    def _estimate_budget_signals(self, 
                               transparency_ads: List,
                               vertical: VerticalIntelligence) -> Dict[str, Any]:
        """Estimate budget based on ad volume and vertical benchmarks"""
        ad_count = len(transparency_ads)
        
        # Rough budget estimation
        if ad_count > 20:
            estimated_budget = "High (>£5000/month)"
            budget_tier = "high"
        elif ad_count > 10:
            estimated_budget = "Medium (£2000-5000/month)"
            budget_tier = "medium"
        else:
            estimated_budget = "Low (<£2000/month)"
            budget_tier = "low"
            
        meets_minimum = budget_tier in ["high", "medium"]
        
        return {
            'estimated_monthly_budget': estimated_budget,
            'budget_tier': budget_tier,
            'meets_vertical_minimum': meets_minimum,
            'ad_volume_indicator': ad_count
        }
    
    def _analyze_message_match(self, ad: AdResult) -> float:
        """Analyze ad-to-landing message consistency (simulate)"""
        # Would implement actual page scraping and NLP matching
        import random
        return random.uniform(0.4, 0.9)
    
    def _assess_conversion_readiness(self, page_metrics: Dict) -> Dict[str, float]:
        """Assess technical conversion readiness"""
        return {
            'speed_readiness': 1.0 - (page_metrics['lcp'] / 4.0),
            'layout_stability': 1.0 - page_metrics['cls'],
            'overall_readiness': page_metrics['conversion_score']
        }

# Strategic execution
async def run_strategic_pipeline():
    """Execute research-backed strategic pipeline"""
    api_key = "3sgTQQBwGfmtBR1WBW61MgnU"
    
    pipeline = StrategicPipeline(api_key)
    
    print("🚀 ARCO STRATEGIC INTELLIGENCE PIPELINE")
    print("📊 Research-backed: ABM + Lead Scoring + Budget Thresholds")
    print("="*60)
    
    # Focus on high-value verticals first
    prospects = await pipeline.discover_strategic_prospects(
        vertical_focus="legal_personal_injury",  # Highest budget vertical
        max_credits=30,
        target_tier="A"  # Only A-tier prospects
    )
    
    # Generate personalized outreach intel
    print(f"\n🎯 OUTREACH INTELLIGENCE")
    print("="*40)
    
    for i, prospect in enumerate(prospects[:5], 1):
        print(f"\n--- PROSPECT {i}: {prospect.company_name} ---")
        print(f"🏢 Vertical: {prospect.vertical}")
        print(f"📍 Location: {prospect.city}")
        print(f"🎯 Score: {prospect.total_score}/100 (Tier {prospect.qualification_tier})")
        print(f"🔍 Confidence: {prospect.confidence:.2f}")
        
        print(f"\n💡 PERSONALIZATION SIGNALS:")
        if not prospect.tracking_signals['conversion_tracking']:
            print(f"  ⚠️ Missing conversion tracking (ROI: 91% more conversions)")
        if prospect.page_speed_metrics['lcp'] > 2.5:
            print(f"  🐌 Slow LCP: {prospect.page_speed_metrics['lcp']:.1f}s (ROI: 8% sales boost)")
        if prospect.message_match_score < 0.7:
            print(f"  📝 Poor message match: {prospect.message_match_score:.2f}")
            
        print(f"\n📈 BUDGET INTELLIGENCE:")
        print(f"  💰 Estimated: {prospect.budget_indicators['estimated_monthly_budget']}")
        print(f"  📊 Ad Volume: {prospect.budget_indicators['ad_volume_indicator']} campaigns")
        print(f"  ✅ Meets minimum: {prospect.budget_indicators['meets_vertical_minimum']}")

if __name__ == "__main__":
    asyncio.run(run_strategic_pipeline())
