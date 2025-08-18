#!/usr/bin/env python3
"""
MICRO SMB PAIN SIGNAL ENGINE (V5.0 - ULTRA FOCUSED)
==================================================

FOCUS: MICRO businesses with REAL pain signals
- MICRO budget (1-9 ads total) = True SMBs
- SEVERE creative stagnation (6+ months old)  
- LOCAL businesses (not corporate giants)
- EXCLUDE: Agencies, platforms, big brands

TARGET: Mom & pop shops that truly NEED our help
"""

import asyncio
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List
from google.cloud import bigquery
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class MicroSMBProspect:
    # Core data
    business_name: str
    location_region: str
    niche: str
    
    # Micro SMB Indicators (1-9 ads = real small business)
    total_ads_count: int
    avg_creative_age_days: float
    business_size_category: str
    
    # Pain Signals
    pain_signal_summary: str
    opportunity_score: float
    suggested_service: str

class MicroSMBPainSignalEngine:
    """Identifies MICRO SMBs (1-9 ads) with severe pain signals."""

    def __init__(self):
        self.client = bigquery.Client()
        logger.info("Micro SMB Engine V5.0 - Focus on 1-9 ads businesses ONLY.")

    def _get_smb_qualified_query(self, niche_keywords: List[str], regions: List[str], limit: int) -> str:
        """Query designed to find SMBs with real pain signals, exclude giants."""
        
        keyword_filters = " OR ".join([f"LOWER(advertiser_disclosed_name) LIKE '%{kw}%'" for kw in niche_keywords])
        region_filters = ", ".join([f"'{region}'" for region in regions])
        
        # Exclusion patterns for big companies/agencies
        exclusions = [
            "LOWER(advertiser_disclosed_name) NOT LIKE '%google%'",
            "LOWER(advertiser_disclosed_name) NOT LIKE '%facebook%'", 
            "LOWER(advertiser_disclosed_name) NOT LIKE '%meta%'",
            "LOWER(advertiser_disclosed_name) NOT LIKE '%amazon%'",
            "LOWER(advertiser_disclosed_name) NOT LIKE '%microsoft%'",
            "LOWER(advertiser_disclosed_name) NOT LIKE '%apple%'",
            "LOWER(advertiser_disclosed_name) NOT LIKE '%agency%'",
            "LOWER(advertiser_disclosed_name) NOT LIKE '%marketing%'",
            "LOWER(advertiser_disclosed_name) NOT LIKE '%media%'",
            "LOWER(advertiser_disclosed_name) NOT LIKE '%digital%'",
            "LOWER(advertiser_disclosed_name) NOT LIKE '%group%'",
            "LOWER(advertiser_disclosed_name) NOT LIKE '%holdings%'",
            "LOWER(advertiser_disclosed_name) NOT LIKE '%international%'",
            "LOWER(advertiser_disclosed_name) NOT LIKE '%global%'",
            "LOWER(advertiser_disclosed_name) NOT LIKE '%worldwide%'",
            "LOWER(advertiser_disclosed_name) NOT LIKE '%platform%'",
            "LOWER(advertiser_disclosed_name) NOT LIKE '%network%'",
            "LOWER(advertiser_disclosed_name) NOT LIKE '%booking%'",
            "LOWER(advertiser_disclosed_name) NOT LIKE '%expedia%'",
            "LOWER(advertiser_disclosed_name) NOT LIKE '%trivago%'",
            "LOWER(advertiser_disclosed_name) NOT LIKE '%airbnb%'",
            "LOWER(advertiser_disclosed_name) NOT LIKE '%uber%'",
            "LOWER(advertiser_disclosed_name) NOT LIKE '%spa' AND LOWER(advertiser_disclosed_name) NOT LIKE 'spa %'",  # Exclude ".SPA" extensions
            "LOWER(advertiser_disclosed_name) NOT LIKE '% sa'",   # Exclude "S.A." companies (often large)
            "LOWER(advertiser_disclosed_name) NOT LIKE '% sl'",   # Exclude "S.L." companies 
            "LOWER(advertiser_disclosed_name) NOT LIKE '% ltd'",  # Exclude large LTDs
            "LOWER(advertiser_disclosed_name) NOT LIKE '% llc'"   # Exclude large LLCs
        ]
        
        exclusion_filter = " AND ".join(exclusions)

        return f"""
        WITH SMBProspectBase AS (
            -- Step 1: Find companies with SMB characteristics
            SELECT
                advertiser_disclosed_name,
                advertiser_id,
                -- Pain Signal: Average age of creatives
                AVG(DATE_DIFF(CURRENT_DATE(), DATE(region.first_shown), DAY)) as avg_creative_age_days,
                -- Primary region
                ARRAY_AGG(region.region_code ORDER BY region.times_shown_upper_bound DESC LIMIT 1)[OFFSET(0)] as primary_region,
                -- Total ads count (key SMB filter)
                COUNT(*) as total_ads_count,
                -- Activity pattern analysis
                MIN(DATE(region.first_shown)) as first_ad_date,
                MAX(DATE(region.last_shown)) as last_ad_date,
                -- Recent activity check
                COUNTIF(DATE_DIFF(CURRENT_DATE(), DATE(region.first_shown), DAY) <= 30) as recent_ads
            FROM `bigquery-public-data.google_ads_transparency_center.creative_stats`,
            UNNEST(region_stats) as region
            WHERE region.first_shown IS NOT NULL
            GROUP BY 1, 2
        ),
        QualifiedSMBs AS (
            SELECT 
                *,
                -- Opportunity score calculation
                CASE 
                    WHEN avg_creative_age_days > 365 THEN 3.0  -- Very stale
                    WHEN avg_creative_age_days > 180 THEN 2.0  -- Stale
                    WHEN avg_creative_age_days > 90 THEN 1.5   -- Getting stale
                    ELSE 1.0 
                END * 
                CASE 
                    WHEN total_ads_count BETWEEN 5 AND 9 THEN 3.0      -- Perfect micro SMB
                    WHEN total_ads_count BETWEEN 3 AND 4 THEN 2.5      -- Small but good
                    WHEN total_ads_count BETWEEN 1 AND 2 THEN 2.0      -- Very small
                    ELSE 1.0 
                END as opportunity_score,
                -- Business size categorization for MICRO SMBs
                CASE
                    WHEN total_ads_count BETWEEN 7 AND 9 THEN 'Active Micro Business'
                    WHEN total_ads_count BETWEEN 4 AND 6 THEN 'Small Micro Business'  
                    WHEN total_ads_count BETWEEN 2 AND 3 THEN 'Tiny Business'
                    WHEN total_ads_count = 1 THEN 'Solo Business'
                    ELSE 'Unknown'
                END as business_size_category
            FROM SMBProspectBase
            WHERE 
                -- MICRO SMB FILTERS: Only 1-9 ads (true small businesses)
                total_ads_count BETWEEN 1 AND 9  -- MICRO range: mom & pop shops
                AND primary_region IN ({region_filters})
                -- PAIN SIGNAL: Old creatives  
                AND avg_creative_age_days > 180  -- 6+ months old (severe stagnation)
                -- NICHE MATCH
                AND ({keyword_filters})
                -- EXCLUSIONS: Remove big companies and agencies
                AND {exclusion_filter}
                -- ACTIVITY CHECK: Not completely dead
                AND DATE_DIFF(CURRENT_DATE(), last_ad_date, DAY) <= 365  -- Active within last year
        )
        -- Final selection with quality ranking
        SELECT
            advertiser_disclosed_name,
            primary_region,
            total_ads_count,
            avg_creative_age_days,
            business_size_category,
            opportunity_score,
            first_ad_date,
            last_ad_date
        FROM QualifiedSMBs
        ORDER BY opportunity_score DESC, total_ads_count ASC  -- Prioritize high opportunity, smaller companies
        LIMIT {limit}
        """

    async def discover_qualified_smbs(self) -> List[MicroSMBProspect]:
        """Find real SMB prospects with genuine pain signals."""
        logger.info("🎯 Starting SMB discovery - targeting companies that NEED help.")
        
        niches = {
            'Aesthetics': {
                'keywords': ['clinic', 'aesthetic', 'beauty', 'laser', 'cosmetic', 'spa', 'dermal', 'botox', 'facial'],
                'regions': ['EEA', 'IE', 'DE', 'FR', 'ES', 'IT', 'NL', 'BE']
            },
            'Real Estate': {
                'keywords': ['estate', 'property', 'realty', 'homes', 'housing', 'realtor', 'broker'],
                'regions': ['EEA', 'IE', 'DE', 'FR', 'ES', 'IT', 'NL', 'BE']
            },
            'Legal': {
                'keywords': ['law', 'legal', 'attorney', 'lawyer', 'solicitor', 'advocate', 'counsel'],
                'regions': ['EEA', 'IE', 'DE', 'FR', 'ES', 'IT', 'NL', 'BE']
            },
            'Dental': {
                'keywords': ['dental', 'dentist', 'orthodontist', 'oral', 'tooth', 'implant', 'dentistry'],
                'regions': ['EEA', 'IE', 'DE', 'FR', 'ES', 'IT', 'NL', 'BE']
            }
        }
        
        all_prospects = []
        for niche_name, config in niches.items():
            logger.info(f"---")
            logger.info(f"🔍 Searching for SMB prospects in: {niche_name}")
            query = self._get_smb_qualified_query(config['keywords'], config['regions'], limit=5)
            
            try:
                query_job = self.client.query(query)
                results = await asyncio.to_thread(query_job.result)
                
                found_prospects = []
                for row in results:
                    # Pain signal analysis
                    if row.avg_creative_age_days > 365:
                        pain_level = "CRITICAL"
                        pain_desc = f"Creatives are {int(row.avg_creative_age_days)} days old (1+ year stagnation)"
                    elif row.avg_creative_age_days > 180:
                        pain_level = "HIGH" 
                        pain_desc = f"Creatives are {int(row.avg_creative_age_days)} days old (6+ months stale)"
                    else:
                        pain_level = "MODERATE"
                        pain_desc = f"Creatives are {int(row.avg_creative_age_days)} days old (needs refresh)"
                    
                    prospect = MicroSMBProspect(
                        business_name=row.advertiser_disclosed_name,
                        location_region=row.primary_region,
                        niche=niche_name,
                        total_ads_count=row.total_ads_count,
                        avg_creative_age_days=round(row.avg_creative_age_days, 1),
                        business_size_category=row.business_size_category,
                        pain_signal_summary=f"{pain_level}: {pain_desc}",
                        opportunity_score=round(row.opportunity_score, 2),
                        suggested_service="Creative Refresh & Ad Account Optimization"
                    )
                    found_prospects.append(prospect)
                
                logger.info(f"✅ Found {len(found_prospects)} qualified SMB prospects in {niche_name}.")
                if found_prospects:
                    avg_ads = sum(p.total_ads_count for p in found_prospects) / len(found_prospects)
                    avg_age = sum(p.avg_creative_age_days for p in found_prospects) / len(found_prospects)
                    logger.info(f"   📊 Avg ads: {avg_ads:.0f} | Avg age: {avg_age:.0f} days")
                
                all_prospects.extend(found_prospects)

            except Exception as e:
                logger.error(f"Query failed for niche {niche_name}: {e}")

        logger.info("---")
        logger.info(f"🎯 SMB Discovery complete. Qualified prospects found: {len(all_prospects)}")
        return all_prospects

    async def export_results(self, prospects: List[MicroSMBProspect]) -> str:
        """Export SMB prospects to JSON file."""
        
        export_data = {
            "summary": {
                "execution_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "engine_version": "4.0 (SMB Pain Signal Focus)",
                "methodology": "Target SMBs (10-500 ads) with real pain signals, exclude giants",
                "target_markets": "EU Premium (EEA, IE, DE, FR, ES, IT, NL, BE)",
                "total_prospects": len(prospects),
                "avg_ads_per_prospect": round(sum(p.total_ads_count for p in prospects) / len(prospects), 1) if prospects else 0,
                "avg_creative_age": round(sum(p.avg_creative_age_days for p in prospects) / len(prospects), 1) if prospects else 0,
                "avg_opportunity_score": round(sum(p.opportunity_score for p in prospects) / len(prospects), 2) if prospects else 0,
                "niches_covered": len(set(p.niche for p in prospects))
            },
            "prospects": [asdict(p) for p in prospects]
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = f"data/ultra_qualified/smb_pain_signals_{timestamp}.json"
        
        os.makedirs(os.path.dirname(export_file), exist_ok=True)
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 SMB prospects exported to: {export_file}")
        return export_file

async def main():
    """Main function to run the SMB engine."""
    engine = MicroSMBPainSignalEngine()
    prospects = await engine.discover_qualified_smbs()
    if prospects:
        await engine.export_results(prospects)
        
        # Summary stats
        logger.info("📈 SUMMARY STATISTICS:")
        logger.info(f"   Total qualified SMB prospects: {len(prospects)}")
        if prospects:
            avg_ads = sum(p.total_ads_count for p in prospects) / len(prospects)
            avg_age = sum(p.avg_creative_age_days for p in prospects) / len(prospects) 
            avg_score = sum(p.opportunity_score for p in prospects) / len(prospects)
            logger.info(f"   Average ads per prospect: {avg_ads:.0f}")
            logger.info(f"   Average creative age: {avg_age:.0f} days")
            logger.info(f"   Average opportunity score: {avg_score:.2f}")
    else:
        logger.warning("No qualified SMB prospects found in this run.")

if __name__ == "__main__":
    asyncio.run(main())
