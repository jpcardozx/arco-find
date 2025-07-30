#!/usr/bin/env python3
"""
🎯 ARCO MAIN PIPELINE - CLEAN & FOCUSED
Single entry point for all lead discovery operations
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from config.api_keys import APIConfig
from src.core.arco_engine import ArcoEngine
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ArcoMainPipeline:
    """Main pipeline for lead discovery and analysis"""
    
    def __init__(self):
        self.config = APIConfig()
        self.engine = ArcoEngine()
        
    async def discover_leads(self, target_count: int = 10):
        """Main lead discovery method"""
        logger.info(f"🚀 Starting lead discovery for {target_count} leads")
        
        try:
            # Validate configuration
            self.config.validate_s_tier_config()
            
            # Execute discovery
            leads = await self.engine.discover_qualified_leads(
                target_count=target_count,
                use_real_apis=True
            )
            
            logger.info(f"✅ Discovered {len(leads)} qualified leads")
            return leads
            
        except Exception as e:
            logger.error(f"❌ Discovery failed: {e}")
            return []

async def main():
    """Main execution"""
    pipeline = ArcoMainPipeline()
    leads = await pipeline.discover_leads(target_count=10)
    
    if leads:
        print(f"\n🎉 Successfully discovered {len(leads)} leads!")
        for i, lead in enumerate(leads[:3], 1):
            print(f"   {i}. {lead.get('company_name', 'Unknown')} - {lead.get('website', 'N/A')}")
    else:
        print("\n❌ No leads discovered")

if __name__ == "__main__":
    asyncio.run(main())
