'''
HYBRID ENGINE (V3.2 - Final BQF)
==================================

METHODOLOGY: BQF (BigQuery-First) - Final Version
✓ Uses a single, accessible table (`creative_stats`) to avoid permission errors.
✓ Uses ad volume (`total_ads_count`) as a reliable proxy for investment.
✓ All other advanced BQF logic (creative age, city targeting) remains.
✓ Targets AU/NZ for 3 leads in Aesthetics & Real Estate niches.
'''

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
class HybridProspect:
    # Core data
    business_name: str
    location_city: str
    landing_page: str
    niche: str

    # BQF Proxies & Signals
    business_size_proxy: str
    total_ads_count: int
    avg_creative_age_days: float

    # Opportunity
    pain_signal_summary: str
    suggested_service: str

class HybridEngine:
    """Implements the BigQuery-First methodology using a single, accessible table."""

    def __init__(self):
        # Configure BigQuery client - using default project which works fine
        self.client = bigquery.Client()  # No need to specify location, default project works
        logger.info("Hybrid Engine V3.2 (BQF - Single Table) initialized successfully.")

    def _get_base_query(self, niche_keywords: List[str], regions: List[str], limit: int) -> str:
        """Constructs the powerful BQF query using only the creative_stats table."""
        
        keyword_filters = " OR ".join([f"LOWER(advertiser_disclosed_name) LIKE '%{kw}%'" for kw in niche_keywords])
        region_filters = ", ".join([f"'{region}'" for region in regions])

        return f"""
        WITH ProspectBase AS (
            -- Step 1: Aggregate all data from the single accessible table
            SELECT
                advertiser_disclosed_name,
                advertiser_id,
                -- Pain Signal: Average age of creatives in days (using first_shown from region_stats)
                AVG(DATE_DIFF(CURRENT_DATE(), DATE(region.first_shown), DAY)) as avg_creative_age_days,
                -- Get the most targeted region
                ARRAY_AGG(region.region_code ORDER BY region.times_shown_upper_bound DESC LIMIT 1)[OFFSET(0)] as primary_region,
                -- Use the creative page URL as landing page (best available proxy)
                ARRAY_AGG(creative_page_url LIMIT 1)[OFFSET(0)] as primary_landing_page,
                COUNT(*) as total_ads_count
            FROM `bigquery-public-data.google_ads_transparency_center.creative_stats`,
            UNNEST(region_stats) as region
            WHERE region.first_shown IS NOT NULL
            GROUP BY 1, 2
        )
        -- Final Step: Filter for our target criteria
        SELECT
            advertiser_disclosed_name,
            primary_landing_page,
            total_ads_count,
            primary_region,
            avg_creative_age_days,
            -- Proxy for business size based on ad volume
            CASE
                WHEN total_ads_count > 200 THEN 'Medium SME'
                WHEN total_ads_count > 50 THEN 'Small SME'
                ELSE 'Micro Business'
            END as business_size_proxy
        FROM ProspectBase
        WHERE 
            primary_region IN ({region_filters})
            AND primary_landing_page IS NOT NULL
            -- Filter for the pain signal: old creatives (reduced from 120 to 90 days)
            AND avg_creative_age_days > 90 -- Creatives are on average over 3 months old
            AND ({keyword_filters})
        ORDER BY total_ads_count DESC -- Focus on those with higher activity
        LIMIT {limit}
        """

    async def discover_leads(self) -> List[HybridProspect]:
        """Runs the discovery process for all configured niches."""
        logger.info("🚀 Starting lead discovery for all niches.")
        
        niches = {
            'Aesthetics': {
                'keywords': ['clinic', 'aesthetic', 'beauty', 'laser', 'cosmetic', 'spa', 'dermal', 'botox'],
                'regions': ['EEA', 'IE', 'DE', 'FR', 'ES', 'IT', 'NL']  # Focar nos top mercados
            },
            'Real Estate': {
                'keywords': ['estate', 'property', 'realty', 'real estate', 'homes', 'housing'],
                'regions': ['EEA', 'IE', 'DE', 'FR', 'ES', 'IT', 'NL']  # Mercados premium
            },
            'Legal': {
                'keywords': ['law', 'legal', 'attorney', 'lawyer', 'solicitor', 'barrister'],
                'regions': ['EEA', 'IE', 'DE', 'FR', 'ES', 'IT', 'NL']  # Compliance-heavy markets
            }
        }
        
        all_prospects = []
        for niche_name, config in niches.items():
            logger.info(f"---")
            logger.info(f"🔍 Searching for 5 leads in niche: {niche_name}")  # Aumentar para 5 leads
            query = self._get_base_query(config['keywords'], config['regions'], limit=5)
            
            try:
                query_job = self.client.query(query)
                results = await asyncio.to_thread(query_job.result)
                
                found_prospects = []
                for row in results:
                    prospect = HybridProspect(
                        business_name=row.advertiser_disclosed_name,
                        location_city=row.primary_region,  # Using region instead of city
                        landing_page=row.primary_landing_page,
                        niche=niche_name,
                        business_size_proxy=row.business_size_proxy,
                        total_ads_count=row.total_ads_count,
                        avg_creative_age_days=round(row.avg_creative_age_days, 1),
                        pain_signal_summary=f"Creative Stagnation: Ads are on average {round(row.avg_creative_age_days, 0)} days old.",
                        suggested_service="Creative Refresh & Performance Optimization Sprint"
                    )
                    found_prospects.append(prospect)
                
                logger.info(f"✅ Found {len(found_prospects)} leads in {niche_name}.")
                all_prospects.extend(found_prospects)

            except Exception as e:
                logger.error(f"Query failed for niche {niche_name}: {e}")

        logger.info("---")
        logger.info(f"Discovery complete. Total leads found: {len(all_prospects)}")
        return all_prospects

    async def export_results(self, prospects: List[HybridProspect]) -> str:
        """Exports the found leads to a JSON file."""
        
        export_data = {
            "summary": {
                "execution_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "engine_version": "3.2 (BQF - Strategic Europe Focus)",
                "target_markets": "EU Premium (EEA, IE, DE, FR, ES, IT, NL)",
                "total_leads": len(prospects),
                "aesthetics_leads": len([p for p in prospects if p.niche == 'Aesthetics']),
                "real_estate_leads": len([p for p in prospects if p.niche == 'Real Estate']),
                "legal_leads": len([p for p in prospects if p.niche == 'Legal']),
                "avg_creative_age": round(sum(p.avg_creative_age_days for p in prospects) / len(prospects), 1) if prospects else 0
            },
            "leads": [asdict(p) for p in prospects]
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = f"data/ultra_qualified/bqf_leads_{timestamp}.json"
        
        os.makedirs(os.path.dirname(export_file), exist_ok=True)
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Results exported to: {export_file}")
        return export_file

async def main():
    """Main function to run the engine."""
    engine = HybridEngine()
    leads = await engine.discover_leads()
    if leads:
        await engine.export_results(leads)
    else:
        logger.warning("No leads were generated in this run.")

if __name__ == "__main__":
    asyncio.run(main())
