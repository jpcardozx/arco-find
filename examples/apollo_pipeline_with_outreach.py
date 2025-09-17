"""
Apollo Pipeline with Outreach Automation.

This script combines the Apollo enrichment pipeline with outreach automation,
creating a complete end-to-end workflow from lead import to automated outreach.
"""

import sys
import os
import json
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
import argparse
import random

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from arco.integrations.apollo_csv import ApolloCSVIntegration
from arco.integrations.wappalyzer import WappalyzerIntegration
from arco.integrations.crm_integration import crm_manager
from arco.integrations.outreach_integration import outreach_manager
from arco.models.icp import ShopifyDTCPremiumICP, HealthSupplementsICP, FitnessEquipmentICP
from arco.models.financial_leak import FinancialLeakDetector
from arco.models.roi_report import ROIReportGenerator
from arco.engines.discovery_engine import DiscoveryEngine
from arco.models.prospect import Prospect, Technology
from arco.utils.progress_tracker import tracker, ProgressStage

# Import functions from enrichment pipeline
from examples.apollo_enrichment_pipeline import (
    enrich_prospect_basic,
    enrich_prospect_advanced,
    analyze_prospect,
    qualify_prospect,
    register_in_crm,
    process_prospect,
    process_batch,
    generate_summary_report,
    save_results as save_pipeline_results
)

# Import functions from outreach automation
from examples.apollo_outreach_automation import (
    send_initial_outreach,
    send_follow_up_outreach,
    process_qualified_prospects,
    generate_outreach_report,
    save_results as save_outreach_results
)


async def process_prospect_with_outreach(prospect: Prospect, icps: Dict[str, Any], auto_outreach: bool = False) -> Dict[str, Any]:
    """
    Process a prospect through the entire pipeline including outreach.
    
    Args:
        prospect: Prospect to process
        icps: Dictionary of ICPs
        auto_outreach: Whether to automatically send outreach messages
        
    Returns:
        Processing results
    """
    # Process through enrichment pipeline
    pipeline_results = await process_prospect(prospect, icps)
    
    # If qualified and auto_outreach is enabled, send outreach
    if pipeline_results.get("qualified", False) and auto_outreach:
        analysis_results = pipeline_results.get("analysis_results", {})
        message_id = await send_initial_outreach(prospect, analysis_results)
        
        if message_id:
            pipeline_results["outreach"] = {
                "message_id": message_id,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
    
    return pipeline_results


async def process_batch_with_outreach(prospects: List[Prospect], icps: Dict[str, Any], batch_size: int = 5, auto_outreach: bool = False) -> List[Dict[str, Any]]:
    """
    Process a batch of prospects including outreach.
    
    Args:
        prospects: List of prospects to process
        icps: Dictionary of ICPs
        batch_size: Number of prospects to process in parallel
        auto_outreach: Whether to automatically send outreach messages
        
    Returns:
        List of processing results
    """
    results = []
    
    # Process in batches
    for i in range(0, len(prospects), batch_size):
        batch = prospects[i:i+batch_size]
        tasks = [process_prospect_with_outreach(p, icps, auto_outreach) for p in batch]
        batch_results = await asyncio.gather(*tasks)
        results.extend(batch_results)
        print(f"Processed batch {i//batch_size + 1}/{(len(prospects)-1)//batch_size + 1}")
    
    return results


async def main():
    """Main function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Apollo Pipeline with Outreach Automation")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of prospects to process")
    parser.add_argument("--batch-size", type=int, default=5, help="Number of prospects to process in parallel")
    parser.add_argument("--output-dir", type=str, default="apollo_results", help="Output directory")
    parser.add_argument("--auto-outreach", action="store_true", help="Automatically send outreach messages")
    parser.add_argument("--follow-up-days", type=int, default=3, help="Days since initial contact for follow-ups")
    parser.add_argument("--smtp-server", type=str, help="SMTP server for sending emails")
    parser.add_argument("--smtp-port", type=int, default=587, help="SMTP port")
    parser.add_argument("--username", type=str, help="SMTP username")
    parser.add_argument("--password", type=str, help="SMTP password")
    parser.add_argument("--from-email", type=str, help="From email address")
    parser.add_argument("--from-name", type=str, default="ARCO Team", help="From name")
    args = parser.parse_args()
    
    print("Apollo Pipeline with Outreach Automation")
    print("======================================")
    
    # Initialize Apollo integration
    print("\nInitializing Apollo integration...")
    apollo_integration = ApolloCSVIntegration()
    
    # Import prospects
    print("\nImporting prospects from Apollo...")
    all_prospects = apollo_integration.get_all_prospects()
    print(f"Imported {len(all_prospects)} prospects from Apollo")
    
    # Limit number of prospects
    prospects = all_prospects[:args.limit]
    print(f"Processing {len(prospects)} prospects")
    
    # Create ICPs
    print("\nInitializing ICPs...")
    icps = {
        "shopify_dtc": ShopifyDTCPremiumICP(),
        "health_supplements": HealthSupplementsICP(),
        "fitness_equipment": FitnessEquipmentICP()
    }
    
    # Initialize outreach integration if auto_outreach is enabled
    if args.auto_outreach:
        print("\nInitializing outreach integration...")
        outreach_manager.initialize_integration(
            "email",
            smtp_server=args.smtp_server,
            smtp_port=args.smtp_port,
            username=args.username,
            password=args.password,
            from_email=args.from_email,
            from_name=args.from_name
        )
    
    # Process prospects
    print("\nProcessing prospects...")
    start_time = time.time()
    results = await process_batch_with_outreach(prospects, icps, args.batch_size, args.auto_outreach)
    pipeline_end_time = time.time()
    
    # Generate summary report
    print("\nGenerating pipeline summary report...")
    summary = generate_summary_report(results)
    
    # Save pipeline results
    print("\nSaving pipeline results...")
    pipeline_results_path, pipeline_summary_path = save_pipeline_results(results, summary, args.output_dir)
    
    # Process follow-ups for previously qualified prospects
    if args.auto_outreach:
        print("\nProcessing follow-ups for previously qualified prospects...")
        outreach_results = await process_qualified_prospects(True, args.follow_up_days)
        
        # Generate outreach report
        print("\nGenerating outreach report...")
        outreach_report = generate_outreach_report(outreach_results)
        
        # Save outreach results
        print("\nSaving outreach results...")
        outreach_results_path, outreach_report_path = save_outreach_results(outreach_results, outreach_report, args.output_dir)
    
    outreach_end_time = time.time()
    
    # Print pipeline summary
    print("\nPipeline Summary:")
    print(f"- Total prospects: {summary['total_prospects']}")
    print(f"- Successful: {summary['successful_prospects']} ({summary['success_rate']:.1%})")
    print(f"- Qualified: {summary['qualified_prospects']} ({summary['qualification_rate']:.1%})")
    print(f"- Registered in CRM: {summary['registered_prospects']} ({summary['registration_rate']:.1%})")
    print(f"- Average ICP score: {summary['average_score']:.1f}/100")
    print(f"- Total annual savings: ${summary['total_annual_savings']:,.2f}")
    print(f"- Average annual savings: ${summary['average_annual_savings']:,.2f}")
    print(f"- Average ROI: {summary['average_roi_percentage']:.1f}%")
    print(f"- Pipeline processing time: {pipeline_end_time - start_time:.1f} seconds")
    
    # Print outreach summary if auto_outreach is enabled
    if args.auto_outreach:
        print("\nOutreach Summary:")
        print(f"- Total qualified prospects: {outreach_report['total_qualified_prospects']}")
        print(f"- Total contacted prospects: {outreach_report['total_contacted_prospects']} ({outreach_report['contact_rate']:.1%})")
        print(f"- Total engaged prospects: {outreach_report['total_engaged_prospects']} ({outreach_report['engagement_rate']:.1%})")
        print(f"- New outreach messages: {outreach_report['new_outreach']}")
        print(f"- New follow-up messages: {outreach_report['new_follow_ups']}")
        print(f"- Outreach processing time: {outreach_end_time - pipeline_end_time:.1f} seconds")
    
    print(f"\nTotal processing time: {outreach_end_time - start_time:.1f} seconds")
    
    print("\nResults saved to:")
    print(f"- {pipeline_results_path}")
    print(f"- {pipeline_summary_path}")
    
    if args.auto_outreach:
        print(f"- {outreach_results_path}")
        print(f"- {outreach_report_path}")
    
    print("\nPipeline completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())