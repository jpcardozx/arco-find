#!/usr/bin/env python3
"""
Test script to validate existing engines functionality.

This script tests all the key engines mentioned in the advanced lead analysis spec:
- MarketingPipeline
- LeadEnrichmentEngine  
- LeakEngine
- LeadQualificationEngine
- PriorityEngine
"""

import asyncio
import sys
import os
import logging
from datetime import datetime
from typing import Dict, Any, List

# Add arco to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'arco'))

from arco.pipelines.marketing_pipeline import MarketingPipeline
from arco.engines.lead_enrichment_engine import LeadEnrichmentEngine
from arco.engines.leak_engine import LeakEngine
from arco.engines.lead_qualification_engine import LeadQualificationEngine
from arco.engines.priority_engine import PriorityEngine
from arco.models.prospect import Prospect

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EngineValidator:
    """Validates all engines functionality with sample data."""
    
    def __init__(self):
        self.test_results = {}
        self.sample_domain = "shopify.com"  # Known domain with good data
        
    def create_sample_prospect(self) -> Prospect:
        """Create a sample prospect for testing."""
        return Prospect(
            domain=self.sample_domain,
            company_name="Shopify Inc",
            website=f"https://{self.sample_domain}",
            industry="Technology",
            employee_count=10000,
            revenue=5000000000,
            country="Canada"
        )
    
    async def test_marketing_pipeline(self) -> Dict[str, Any]:
        """Test MarketingPipeline functionality."""
        logger.info("Testing MarketingPipeline...")
        
        try:
            # Initialize pipeline
            pipeline = MarketingPipeline()
            
            # Create sample prospect
            prospect = self.create_sample_prospect()
            
            # Test processing
            result = await pipeline.process_prospect_async(prospect)
            
            success = result is not None
            
            return {
                "engine": "MarketingPipeline",
                "success": success,
                "result_type": type(result).__name__ if result else None,
                "has_marketing_data": hasattr(prospect, 'marketing_data') and prospect.marketing_data is not None,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"MarketingPipeline test failed: {e}")
            return {
                "engine": "MarketingPipeline",
                "success": False,
                "result_type": None,
                "has_marketing_data": False,
                "error": str(e)
            }
    
    async def test_lead_enrichment_engine(self) -> Dict[str, Any]:
        """Test LeadEnrichmentEngine functionality."""
        logger.info("Testing LeadEnrichmentEngine...")
        
        try:
            # Initialize engine
            engine = LeadEnrichmentEngine()
            
            # Create sample prospect
            prospect = self.create_sample_prospect()
            
            # Test enrichment
            result = await engine.enrich_prospect(prospect)
            
            success = result.success if result else False
            
            return {
                "engine": "LeadEnrichmentEngine",
                "success": success,
                "enriched_fields": result.enriched_fields if result else [],
                "new_technologies_count": len(result.new_technologies) if result else 0,
                "confidence_scores": result.confidence_scores if result else {},
                "error": result.errors[0] if result and result.errors else None
            }
            
        except Exception as e:
            logger.error(f"LeadEnrichmentEngine test failed: {e}")
            return {
                "engine": "LeadEnrichmentEngine",
                "success": False,
                "enriched_fields": [],
                "new_technologies_count": 0,
                "confidence_scores": {},
                "error": str(e)
            }
    
    async def test_leak_engine(self) -> Dict[str, Any]:
        """Test LeakEngine functionality."""
        logger.info("Testing LeakEngine...")
        
        try:
            # Initialize engine
            engine = LeakEngine()
            
            # Create sample prospect
            prospect = self.create_sample_prospect()
            
            # Test analysis
            leak_result = await engine.analyze(prospect)
            
            success = leak_result is not None
            
            # Test qualification
            qualified_prospect = None
            if success and leak_result.total_monthly_waste >= 60:
                qualified_prospect = await engine.qualify(prospect, leak_result)
            
            return {
                "engine": "LeakEngine",
                "success": success,
                "total_monthly_waste": leak_result.total_monthly_waste if leak_result else 0,
                "leak_count": len(leak_result.leaks) if leak_result else 0,
                "authority_score": leak_result.authority_score if leak_result else 0,
                "qualified": qualified_prospect is not None,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"LeakEngine test failed: {e}")
            return {
                "engine": "LeakEngine",
                "success": False,
                "total_monthly_waste": 0,
                "leak_count": 0,
                "authority_score": 0,
                "qualified": False,
                "error": str(e)
            }
    
    def test_lead_qualification_engine(self) -> Dict[str, Any]:
        """Test LeadQualificationEngine functionality."""
        logger.info("Testing LeadQualificationEngine...")
        
        try:
            # Initialize engine
            engine = LeadQualificationEngine()
            
            # Create sample prospect
            prospect = self.create_sample_prospect()
            
            # Test qualification
            is_qualified, lead_score = engine.qualify_lead(prospect)
            
            success = lead_score is not None
            
            return {
                "engine": "LeadQualificationEngine",
                "success": success,
                "is_qualified": is_qualified,
                "total_score": lead_score.total_score if lead_score else 0,
                "qualification_level": lead_score.qualification_level if lead_score else "Unknown",
                "priority_level": lead_score.priority_level if lead_score else 0,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"LeadQualificationEngine test failed: {e}")
            return {
                "engine": "LeadQualificationEngine",
                "success": False,
                "is_qualified": False,
                "total_score": 0,
                "qualification_level": "Unknown",
                "priority_level": 0,
                "error": str(e)
            }
    
    async def test_priority_engine(self) -> Dict[str, Any]:
        """Test PriorityEngine functionality."""
        logger.info("Testing PriorityEngine...")
        
        try:
            # Initialize engine
            engine = PriorityEngine()
            
            # Create sample prospects
            prospects = [self.create_sample_prospect()]
            
            # Test scoring
            scored_prospects = await engine.score_batch(prospects)
            
            success = len(scored_prospects) > 0
            
            if success:
                prospect, score = scored_prospects[0]
                return {
                    "engine": "PriorityEngine",
                    "success": success,
                    "total_score": score.total_score,
                    "priority_tier": score.priority_tier,
                    "confidence_level": score.confidence_level,
                    "error": None
                }
            else:
                return {
                    "engine": "PriorityEngine",
                    "success": False,
                    "total_score": 0,
                    "priority_tier": "Unknown",
                    "confidence_level": 0,
                    "error": "No scored prospects returned"
                }
            
        except Exception as e:
            logger.error(f"PriorityEngine test failed: {e}")
            return {
                "engine": "PriorityEngine",
                "success": False,
                "total_score": 0,
                "priority_tier": "Unknown",
                "confidence_level": 0,
                "error": str(e)
            }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all engine tests."""
        logger.info("Starting comprehensive engine validation...")
        
        # Test all engines
        results = {}
        
        # Test MarketingPipeline
        results["marketing_pipeline"] = await self.test_marketing_pipeline()
        
        # Test LeadEnrichmentEngine
        results["lead_enrichment_engine"] = await self.test_lead_enrichment_engine()
        
        # Test LeakEngine
        results["leak_engine"] = await self.test_leak_engine()
        
        # Test LeadQualificationEngine
        results["lead_qualification_engine"] = self.test_lead_qualification_engine()
        
        # Test PriorityEngine
        results["priority_engine"] = await self.test_priority_engine()
        
        # Generate summary
        total_engines = len(results)
        successful_engines = sum(1 for result in results.values() if result["success"])
        
        summary = {
            "test_timestamp": datetime.now().isoformat(),
            "sample_domain": self.sample_domain,
            "total_engines_tested": total_engines,
            "successful_engines": successful_engines,
            "success_rate": successful_engines / total_engines,
            "all_engines_functional": successful_engines == total_engines,
            "detailed_results": results
        }
        
        return summary
    
    def print_results(self, results: Dict[str, Any]):
        """Print test results in a readable format."""
        print("\n" + "="*60)
        print("ENGINE FUNCTIONALITY VALIDATION RESULTS")
        print("="*60)
        
        print(f"Test Date: {results['test_timestamp']}")
        print(f"Sample Domain: {results['sample_domain']}")
        print(f"Success Rate: {results['successful_engines']}/{results['total_engines_tested']} ({results['success_rate']:.1%})")
        print(f"All Engines Functional: {'✅ YES' if results['all_engines_functional'] else '❌ NO'}")
        
        print("\nDETAILED RESULTS:")
        print("-" * 40)
        
        for engine_key, result in results["detailed_results"].items():
            engine_name = result["engine"]
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            
            print(f"\n{engine_name}: {status}")
            
            if result["success"]:
                # Print success details
                if engine_key == "marketing_pipeline":
                    print(f"  - Result Type: {result['result_type']}")
                    print(f"  - Has Marketing Data: {result['has_marketing_data']}")
                elif engine_key == "lead_enrichment_engine":
                    print(f"  - Enriched Fields: {len(result['enriched_fields'])}")
                    print(f"  - New Technologies: {result['new_technologies_count']}")
                elif engine_key == "leak_engine":
                    print(f"  - Monthly Waste: ${result['total_monthly_waste']:.2f}")
                    print(f"  - Leaks Found: {result['leak_count']}")
                    print(f"  - Qualified: {result['qualified']}")
                elif engine_key == "lead_qualification_engine":
                    print(f"  - Qualified: {result['is_qualified']}")
                    print(f"  - Score: {result['total_score']:.1f}")
                    print(f"  - Tier: {result['qualification_level']}")
                elif engine_key == "priority_engine":
                    print(f"  - Score: {result['total_score']:.1f}")
                    print(f"  - Priority: {result['priority_tier']}")
            else:
                # Print error details
                print(f"  - Error: {result['error']}")
        
        print("\n" + "="*60)

async def main():
    """Main test execution."""
    validator = EngineValidator()
    results = await validator.run_all_tests()
    validator.print_results(results)
    
    # Return exit code based on success
    return 0 if results["all_engines_functional"] else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)