#!/usr/bin/env python3
"""
Script para executar análise de marketing nos prospects.

Executa o MarketingPipeline nos prospects existentes, coletando:
- Web Vitals (PageSpeed Insights)
- Traffic Source Analysis
- Conversion Metrics Estimation
- Performance Issue Detection

Usage:
    python run_marketing_analysis.py
    python run_marketing_analysis.py --api-key YOUR_GOOGLE_API_KEY
    python run_marketing_analysis.py --limit 50
"""

import asyncio
import argparse
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from arco.pipelines.marketing_pipeline import MarketingPipeline
from arco.models.prospect import Prospect
from arco.utils.logger import get_logger

logger = get_logger(__name__)

def load_prospects_from_csv(csv_path: str) -> list:
    """
    Load prospects from CSV file.
    
    Args:
        csv_path: Path to CSV file with prospect data
        
    Returns:
        List of Prospect objects
    """
    import pandas as pd
    
    logger.info(f"Loading prospects from: {csv_path}")
    
    try:
        df = pd.read_csv(csv_path)
        prospects = []
        
        for _, row in df.iterrows():
            # Create prospect from CSV row
            prospect = Prospect(
                domain=row.get('domain', '').strip(),
                company_name=row.get('company_name', row.get('Company', '')),
                website=row.get('website', row.get('Website', '')),
                description=row.get('description', ''),
                industry=row.get('industry', row.get('Industry', '')),
                employee_count=row.get('employee_count', row.get('Employees', 0)),
                revenue=row.get('revenue', 0),
                country=row.get('country', row.get('Country', '')),
                city=row.get('city', row.get('City', ''))
            )
            
            # Skip if no domain
            if not prospect.domain:
                continue
                
            prospects.append(prospect)
        
        logger.info(f"Loaded {len(prospects)} prospects from CSV")
        return prospects
        
    except Exception as e:
        logger.error(f"Error loading prospects from CSV: {e}")
        return []

def find_prospect_files() -> list:
    """
    Find prospect files in the project.
    
    Returns:
        List of potential prospect file paths
    """
    potential_files = [
        "arco/consolidated_prospects.csv",
        "data/prospects.csv",
        "prospects.csv",
        "arco/apollo-accounts-export.csv"
    ]
    
    existing_files = []
    for file_path in potential_files:
        if os.path.exists(file_path):
            existing_files.append(file_path)
    
    # Also check for Apollo exports
    arco_dir = Path("arco")
    if arco_dir.exists():
        apollo_files = list(arco_dir.glob("apollo-accounts-export*.csv"))
        existing_files.extend([str(f) for f in apollo_files])
    
    return existing_files

async def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Run marketing analysis on prospects")
    parser.add_argument("--api-key", help="Google API key for PageSpeed Insights")
    parser.add_argument("--limit", type=int, help="Limit number of prospects to process")
    parser.add_argument("--file", help="Specific CSV file to process")
    parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    # Get Google API key
    api_key = args.api_key or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        logger.warning("No Google API key provided. Web vitals collection will be limited.")
        logger.info("Set GOOGLE_API_KEY environment variable or use --api-key parameter")
    
    # Find prospect files
    if args.file:
        prospect_files = [args.file] if os.path.exists(args.file) else []
    else:
        prospect_files = find_prospect_files()
    
    if not prospect_files:
        logger.error("No prospect files found!")
        logger.info("Expected files: consolidated_prospects.csv, apollo-accounts-export.csv, etc.")
        return
    
    logger.info(f"Found prospect files: {prospect_files}")
    
    # Load prospects
    all_prospects = []
    for file_path in prospect_files:
        prospects = load_prospects_from_csv(file_path)
        all_prospects.extend(prospects)
    
    # Remove duplicates by domain
    unique_prospects = {}
    for prospect in all_prospects:
        if prospect.domain and prospect.domain not in unique_prospects:
            unique_prospects[prospect.domain] = prospect
    
    prospects_to_process = list(unique_prospects.values())
    
    # Apply limit if specified
    if args.limit:
        prospects_to_process = prospects_to_process[:args.limit]
    
    logger.info(f"Processing {len(prospects_to_process)} unique prospects")
    
    # Initialize marketing pipeline
    pipeline = MarketingPipeline(google_api_key=api_key)
    
    try:
        # Process prospects
        logger.info("Starting marketing analysis...")
        qualified_prospects = []
        
        for i, prospect in enumerate(prospects_to_process, 1):
            logger.info(f"Processing {i}/{len(prospects_to_process)}: {prospect.domain}")
            
            try:
                qualified = await pipeline.process_prospect_async(prospect)
                if qualified:
                    qualified_prospects.append(qualified)
                    logger.info(f"✅ Qualified: {prospect.domain} (Score: {qualified.qualification_score})")
                else:
                    logger.info(f"❌ Not qualified: {prospect.domain}")
                    
            except Exception as e:
                logger.error(f"Error processing {prospect.domain}: {e}")
                continue
            
            # Add small delay to respect API rate limits
            if i % 10 == 0:
                logger.info(f"Processed {i} prospects, taking a short break...")
                await asyncio.sleep(2)
        
        # Save results
        output_path = args.output or None
        results_file = pipeline.save_results(qualified_prospects, output_path)
        
        # Print summary
        stats = pipeline.stats
        print("\n" + "="*60)
        print("MARKETING ANALYSIS SUMMARY")
        print("="*60)
        print(f"Total prospects processed: {stats['processed_count']}")
        print(f"Marketing data collected: {stats['marketing_enriched']}")
        print(f"Web vitals collected: {stats['web_vitals_collected']}")
        print(f"Traffic sources analyzed: {stats['traffic_sources_analyzed']}")
        print(f"Performance issues detected: {stats['performance_issues_detected']}")
        print(f"Qualified prospects: {stats['qualified_count']}")
        print(f"Average LCP: {stats['avg_lcp']:.2f}s")
        print(f"Average confidence score: {stats['avg_confidence_score']:.2f}")
        print(f"\nResults saved to: {results_file}")
        
        # Show top prospects
        if qualified_prospects:
            print(f"\nTOP 5 QUALIFIED PROSPECTS:")
            print("-" * 60)
            top_prospects = sorted(qualified_prospects, key=lambda x: x.qualification_score, reverse=True)[:5]
            
            for i, prospect in enumerate(top_prospects, 1):
                marketing_insights = getattr(prospect, 'marketing_insights', [])
                insights_text = "; ".join(marketing_insights[:2]) if marketing_insights else "No specific insights"
                
                print(f"{i}. {prospect.domain}")
                print(f"   Company: {prospect.company_name or 'N/A'}")
                print(f"   Score: {prospect.qualification_score}/100 (Tier {prospect.priority_tier})")
                print(f"   Monthly Waste: ${prospect.monthly_waste:,.2f}")
                print(f"   Annual Savings: ${prospect.annual_savings:,.2f}")
                print(f"   Marketing Insights: {insights_text}")
                print()
        
    finally:
        # Cleanup
        await pipeline.close()

if __name__ == "__main__":
    asyncio.run(main())