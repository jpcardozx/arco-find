"""
Apollo Outreach Automation.

This script implements automated outreach for qualified prospects from the Apollo enrichment pipeline.
It integrates with the progress tracker to identify qualified prospects and sends personalized
outreach messages based on ICP and financial leak analysis.
"""

import sys
import os
import json
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
import argparse
import random

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from arco.integrations.apollo_csv import ApolloCSVIntegration
from arco.integrations.crm_integration import crm_manager
from arco.integrations.outreach_integration import outreach_manager
from arco.models.icp import ShopifyDTCPremiumICP, HealthSupplementsICP, FitnessEquipmentICP
from arco.models.financial_leak import FinancialLeakDetector
from arco.models.roi_report import ROIReportGenerator
from arco.engines.discovery_engine import DiscoveryEngine
from arco.models.prospect import Prospect, Technology
from arco.utils.progress_tracker import tracker, ProgressStage


async def send_initial_outreach(prospect: Prospect, analysis_results: Dict[str, Any]) -> str:
    """
    Send initial outreach to a qualified prospect.
    
    Args:
        prospect: Qualified prospect
        analysis_results: Analysis results
        
    Returns:
        Message ID if successful, empty string otherwise
    """
    try:
        # Get lead ID from tracker
        lead_id = tracker.get_lead_by_domain(prospect.domain).lead_id
        
        # Select template based on analysis results
        template_name = outreach_manager.select_template_for_prospect(prospect, analysis_results)
        
        # Prepare personalization data
        leak_results = analysis_results.get("leak_results", {})
        summary = leak_results.get("summary", {})
        
        personalization = {
            "monthly_waste": f"${summary.get('total_monthly_waste', 0):.2f}",
            "annual_waste": f"${summary.get('total_annual_waste', 0):.2f}",
            "monthly_savings": f"${summary.get('total_monthly_savings', 0):.2f}",
            "annual_savings": f"${summary.get('total_annual_savings', 0):.2f}",
            "roi_percentage": f"{summary.get('roi_percentage', 0):.1f}%",
            "top_recommendation": summary.get("priority_recommendations", [""])[0] if summary.get("priority_recommendations") else ""
        }
        
        # Send message
        message_id = outreach_manager.send_message(prospect, template_name, personalization)
        
        if message_id:
            print(f"Sent initial outreach to {prospect.company_name} ({prospect.domain}) using template: {template_name}")
            
            # Update tracker
            tracker.update_stage(lead_id, ProgressStage.CONTACTED, {
                "message_id": message_id,
                "template_name": template_name,
                "timestamp": datetime.now().isoformat(),
                "success": True
            })
        else:
            print(f"Failed to send outreach to {prospect.company_name} ({prospect.domain})")
            
            # Update tracker with error
            tracker.add_error(lead_id, ProgressStage.CONTACTED, "Failed to send outreach message")
        
        return message_id
    except Exception as e:
        print(f"Error sending outreach: {e}")
        return ""


async def send_follow_up_outreach(prospect: Prospect, days_since_contact: int = 3) -> str:
    """
    Send follow-up outreach to a prospect.
    
    Args:
        prospect: Prospect to follow up with
        days_since_contact: Days since initial contact
        
    Returns:
        Message ID if successful, empty string otherwise
    """
    try:
        # Send follow-up
        message_id = outreach_manager.send_follow_up(prospect, days_since_contact)
        
        if message_id:
            print(f"Sent follow-up to {prospect.company_name} ({prospect.domain})")
        
        return message_id
    except Exception as e:
        print(f"Error sending follow-up: {e}")
        return ""


async def check_message_status(message_id: str) -> Dict[str, Any]:
    """
    Check the status of a message.
    
    Args:
        message_id: Message ID
        
    Returns:
        Message status
    """
    return outreach_manager.get_message_status(message_id)


async def process_qualified_prospects(qualified_only: bool = True, days_since_contact: int = 3) -> Dict[str, Any]:
    """
    Process qualified prospects for outreach.
    
    Args:
        qualified_only: Only process qualified prospects
        days_since_contact: Days since initial contact for follow-ups
        
    Returns:
        Processing results
    """
    results = {
        "initial_outreach": [],
        "follow_ups": [],
        "total_processed": 0,
        "successful_outreach": 0,
        "successful_follow_ups": 0
    }
    
    # Get qualified prospects
    qualified_leads = tracker.get_leads_by_stage(ProgressStage.QUALIFIED)
    print(f"Found {len(qualified_leads)} qualified leads")
    
    # Get contacted prospects for follow-ups
    contacted_leads = tracker.get_leads_by_stage(ProgressStage.CONTACTED)
    print(f"Found {len(contacted_leads)} contacted leads for potential follow-up")
    
    # Initialize Apollo integration
    apollo_integration = ApolloCSVIntegration()
    all_prospects = apollo_integration.get_all_prospects()
    prospects_by_domain = {p.domain: p for p in all_prospects}
    
    # Process qualified prospects for initial outreach
    for lead in qualified_leads:
        if lead.domain in prospects_by_domain:
            prospect = prospects_by_domain[lead.domain]
            
            # Get analysis results from tracker metadata
            analysis_results = lead.metadata.get(ProgressStage.ANALYZED, {})
            
            # If analysis results are missing, recreate them
            if not analysis_results:
                leak_detector = FinancialLeakDetector()
                leak_results = leak_detector.detect_financial_leaks(prospect)
                
                # Create ICPs
                icps = {
                    "shopify_dtc": ShopifyDTCPremiumICP(),
                    "health_supplements": HealthSupplementsICP(),
                    "fitness_equipment": FitnessEquipmentICP()
                }
                
                # Calculate scores
                best_score = 0
                best_icp = None
                icp_results = {}
                
                for icp_name, icp in icps.items():
                    score = icp.calculate_match_score(prospect)
                    icp_results[icp_name] = {
                        "icp_name": icp.name,
                        "score": score,
                        "qualified": score >= icp.qualification_threshold
                    }
                    
                    if score > best_score:
                        best_score = score
                        best_icp = icp_name
                
                analysis_results = {
                    "icp_results": icp_results,
                    "best_icp": best_icp,
                    "best_score": best_score,
                    "leak_results": leak_results,
                    "qualified": True
                }
            
            # Send initial outreach
            message_id = await send_initial_outreach(prospect, analysis_results)
            
            if message_id:
                results["successful_outreach"] += 1
                results["initial_outreach"].append({
                    "domain": lead.domain,
                    "company_name": lead.company_name,
                    "message_id": message_id
                })
            
            results["total_processed"] += 1
    
    # Process contacted prospects for follow-ups
    for lead in contacted_leads:
        if lead.domain in prospects_by_domain:
            prospect = prospects_by_domain[lead.domain]
            
            # Check if enough time has passed for follow-up
            contact_metadata = lead.metadata.get(ProgressStage.CONTACTED, {})
            contact_timestamp = contact_metadata.get("timestamp")
            
            if contact_timestamp:
                contact_date = datetime.fromisoformat(contact_timestamp)
                days_elapsed = (datetime.now() - contact_date).days
                
                if days_elapsed >= days_since_contact:
                    # Send follow-up
                    message_id = await send_follow_up_outreach(prospect, days_since_contact)
                    
                    if message_id:
                        results["successful_follow_ups"] += 1
                        results["follow_ups"].append({
                            "domain": lead.domain,
                            "company_name": lead.company_name,
                            "message_id": message_id,
                            "days_since_contact": days_elapsed
                        })
                    
                    results["total_processed"] += 1
    
    return results


def generate_outreach_report(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate an outreach report.
    
    Args:
        results: Processing results
        
    Returns:
        Outreach report
    """
    # Get tracker summary
    tracker_summary = tracker.get_summary()
    
    # Calculate metrics
    total_qualified = tracker_summary["stage_counts"].get(ProgressStage.QUALIFIED, 0)
    total_contacted = tracker_summary["stage_counts"].get(ProgressStage.CONTACTED, 0)
    total_engaged = tracker_summary["stage_counts"].get(ProgressStage.ENGAGED, 0)
    
    contact_rate = total_contacted / total_qualified if total_qualified > 0 else 0
    engagement_rate = total_engaged / total_contacted if total_contacted > 0 else 0
    
    # Compile report
    return {
        "timestamp": datetime.now().isoformat(),
        "total_qualified_prospects": total_qualified,
        "total_contacted_prospects": total_contacted,
        "total_engaged_prospects": total_engaged,
        "contact_rate": contact_rate,
        "engagement_rate": engagement_rate,
        "new_outreach": len(results["initial_outreach"]),
        "new_follow_ups": len(results["follow_ups"]),
        "total_processed": results["total_processed"],
        "successful_outreach": results["successful_outreach"],
        "successful_follow_ups": results["successful_follow_ups"],
        "success_rate": (results["successful_outreach"] + results["successful_follow_ups"]) / results["total_processed"] if results["total_processed"] > 0 else 0
    }


def save_results(results: Dict[str, Any], report: Dict[str, Any], output_dir: str = "apollo_results") -> Tuple[str, str]:
    """
    Save outreach results and report.
    
    Args:
        results: Processing results
        report: Outreach report
        output_dir: Output directory
        
    Returns:
        Tuple of (results_path, report_path)
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_path = os.path.join(output_dir, f"outreach_results_{timestamp}.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    # Save report
    report_path = os.path.join(output_dir, f"outreach_report_{timestamp}.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    
    return results_path, report_path


async def main():
    """Main function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Apollo Outreach Automation")
    parser.add_argument("--qualified-only", action="store_true", help="Only process qualified prospects")
    parser.add_argument("--days-since-contact", type=int, default=3, help="Days since initial contact for follow-ups")
    parser.add_argument("--output-dir", type=str, default="apollo_results", help="Output directory")
    parser.add_argument("--smtp-server", type=str, help="SMTP server for sending emails")
    parser.add_argument("--smtp-port", type=int, default=587, help="SMTP port")
    parser.add_argument("--username", type=str, help="SMTP username")
    parser.add_argument("--password", type=str, help="SMTP password")
    parser.add_argument("--from-email", type=str, help="From email address")
    parser.add_argument("--from-name", type=str, default="ARCO Team", help="From name")
    args = parser.parse_args()
    
    print("Apollo Outreach Automation")
    print("=========================")
    
    # Initialize outreach integration
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
    
    # Process qualified prospects
    print("\nProcessing qualified prospects...")
    start_time = time.time()
    results = await process_qualified_prospects(args.qualified_only, args.days_since_contact)
    end_time = time.time()
    
    # Generate outreach report
    print("\nGenerating outreach report...")
    report = generate_outreach_report(results)
    
    # Save results
    print("\nSaving results...")
    results_path, report_path = save_results(results, report, args.output_dir)
    
    # Print summary
    print("\nOutreach Summary:")
    print(f"- Total qualified prospects: {report['total_qualified_prospects']}")
    print(f"- Total contacted prospects: {report['total_contacted_prospects']} ({report['contact_rate']:.1%})")
    print(f"- Total engaged prospects: {report['total_engaged_prospects']} ({report['engagement_rate']:.1%})")
    print(f"- New outreach messages: {report['new_outreach']}")
    print(f"- New follow-up messages: {report['new_follow_ups']}")
    print(f"- Success rate: {report['success_rate']:.1%}")
    print(f"- Processing time: {end_time - start_time:.1f} seconds")
    
    print("\nResults saved to:")
    print(f"- {results_path}")
    print(f"- {report_path}")
    
    print("\nOutreach automation completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())