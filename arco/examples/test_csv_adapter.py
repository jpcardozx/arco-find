"""
Test script for the enhanced CSV Prospect Adapter.

This script tests the CSV adapter with the existing Apollo CSV files.
"""

import asyncio
import logging
from pathlib import Path

from arco.adapters.csv_prospect_adapter import CSVProspectAdapter, load_all_apollo_csvs
from arco.utils.logger import get_logger

logger = get_logger(__name__)


def test_single_csv():
    """Test loading a single Apollo CSV file."""
    logger.info("🧪 Testing single CSV loading...")
    
    csv_path = "arco/apollo-accounts-export.csv"
    
    if not Path(csv_path).exists():
        logger.error(f"CSV file not found: {csv_path}")
        return
    
    try:
        adapter = CSVProspectAdapter(csv_path)
        prospects = adapter.load_prospects()
        
        logger.info(f"✅ Loaded {len(prospects)} prospects")
        
        # Show sample prospects
        for i, prospect in enumerate(prospects[:3]):
            logger.info(f"Sample {i+1}: {prospect.company_name} ({prospect.domain})")
            logger.info(f"  Industry: {prospect.industry}")
            logger.info(f"  Employees: {prospect.employee_count}")
            logger.info(f"  Technologies: {len(prospect.technologies)} detected")
            if prospect.technologies:
                tech_names = [t.name for t in prospect.technologies[:3]]
                logger.info(f"  Top techs: {', '.join(tech_names)}")
            logger.info("")
        
    except Exception as e:
        logger.error(f"❌ Failed to test single CSV: {e}")


def test_all_apollo_csvs():
    """Test loading all Apollo CSV files."""
    logger.info("🧪 Testing all Apollo CSV loading...")
    
    try:
        prospects = load_all_apollo_csvs("arco")
        
        logger.info(f"✅ Loaded {len(prospects)} total unique prospects")
        
        # Analyze data
        industries = {}
        countries = {}
        tech_categories = {}
        
        for prospect in prospects:
            # Count industries
            if prospect.industry:
                industries[prospect.industry] = industries.get(prospect.industry, 0) + 1
            
            # Count countries
            if prospect.country:
                countries[prospect.country] = countries.get(prospect.country, 0) + 1
            
            # Count technology categories
            for tech in prospect.technologies:
                tech_categories[tech.category] = tech_categories.get(tech.category, 0) + 1
        
        # Show top industries
        logger.info("📊 Top Industries:")
        for industry, count in sorted(industries.items(), key=lambda x: x[1], reverse=True)[:5]:
            logger.info(f"  {industry}: {count} companies")
        
        # Show top countries
        logger.info("🌍 Top Countries:")
        for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:5]:
            logger.info(f"  {country}: {count} companies")
        
        # Show top tech categories
        logger.info("💻 Top Technology Categories:")
        for category, count in sorted(tech_categories.items(), key=lambda x: x[1], reverse=True)[:5]:
            logger.info(f"  {category}: {count} technologies")
        
        # Show prospects with most technologies
        tech_rich_prospects = sorted(prospects, key=lambda p: len(p.technologies), reverse=True)[:3]
        logger.info("🔧 Most Technology-Rich Prospects:")
        for prospect in tech_rich_prospects:
            logger.info(f"  {prospect.company_name}: {len(prospect.technologies)} technologies")
        
    except Exception as e:
        logger.error(f"❌ Failed to test all Apollo CSVs: {e}")


def main():
    """Run all tests."""
    logger.info("🚀 Starting CSV Adapter Tests")
    logger.info("=" * 50)
    
    test_single_csv()
    logger.info("-" * 50)
    test_all_apollo_csvs()
    
    logger.info("=" * 50)
    logger.info("🎉 CSV Adapter Tests Complete!")


if __name__ == "__main__":
    main()