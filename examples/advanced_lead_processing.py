"""
Advanced Lead Processing Pipeline.

This script demonstrates the enhanced lead qualification and enrichment capabilities,
providing comprehensive lead scoring and detailed enrichment beyond basic technology detection.
"""

import sys
import os
import json
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
import argparse

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from arco.integrations.apollo_csv import ApolloCSVIntegration
from arco.integrations.crm_integration import crm_manager
from arco.models.icp import ShopifyDTCPremiumICP, HealthSupplementsICP, FitnessEquipmentICP
from arco.models.financial_leak import FinancialLeakDetector
from arco.engines.lead_enrichment_engine import LeadEnrichmentEngine
from arco.engines.lead_qualification_engine import LeadQualificationEngine, QualificationCriteria
from arco.models.prospect import Prospect
from arco.utils.progress_tracker import tracker, ProgressStage


async def advanced_enrich_prospect(prospect: Prospect, enrichment_engine: LeadEnrichmentEngine) -> Dict[str, Any]:
    """
    Perform advanced enrichment of a prospect.
    
    Args:
        prospect: Prospect to enrich
        enrichment_engine: Enrichment engine instance
        
    Returns:
        Enrichment results
    """
    try:
        # Get lead ID from tracker
        lead_id = tracker.add_lead(prospect.domain, prospect.company_name)
        
        # Update stage to enrichment
        tracker.update_stage(lead_id, ProgressStage.ENRICHED_ADVANCED, {
            "start_time": datetime.now().isoformat()
        })
        
        # Perform comprehensive enrichment
        enrichment_result = await enrichment_engine.enrich_prospect(prospect, deep_enrichment=True)
        
        # Update tracker with enrichment results
        tracker.update_stage(lead_id, ProgressStage.ENRICHED_ADVANCED, {
            "end_time": datetime.now().isoformat(),
            "success": enrichment_result.success,
            "enriched_fields": enrichment_result.enriched_fields,
            "new_technologies_count": len(enrichment_result.new_technologies),
            "new_contacts_count": len(enrichment_result.new_contacts),
            "confidence_scores": enrichment_result.confidence_scores,
            "errors": enrichment_result.errors
        })
        
        return {
            "success": enrichment_result.success,
            "enrichment_result": enrichment_result,
            "prospect": prospect
        }
        
    except Exception as e:
        # Log error
        if lead_id:
            tracker.add_error(lead_id, ProgressStage.ENRICHED_ADVANCED, str(e))
        return {
            "success": False,
            "error": str(e),
            "prospect": prospect
        }


async def advanced_qualify_prospect(prospect: Prospect, qualification_engine: LeadQualificationEngine, 
                                  icp: Any, analysis_results: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Perform advanced qualification of a prospect.
    
    Args:
        prospect: Prospect to qualify
        qualification_engine: Qualification engine instance
        icp: ICP to score against
        analysis_results: Previous analysis results
        
    Returns:
        Qualification results
    """
    try:
        # Get lead ID from tracker
        lead = tracker.get_lead_by_domain(prospect.domain)
        if not lead:
            lead_id = tracker.add_lead(prospect.domain, prospect.company_name)
        else:
            lead_id = lead.lead_id
        
        # Update stage to qualification
        tracker.update_stage(lead_id, ProgressStage.QUALIFIED, {
            "start_time": datetime.now().isoformat()
        })
        
        # Perform comprehensive qualification
        is_qualified, lead_score = qualification_engine.qualify_lead(prospect, icp, analysis_results)
        
        # Update tracker with qualification results
        tracker.update_stage(lead_id, ProgressStage.QUALIFIED, {
            "end_time": datetime.now().isoformat(),
            "qualified": is_qualified,
            "total_score": lead_score.total_score,
            "qualification_level": lead_score.qualification_level,
            "priority_level": lead_score.priority_level,
            "qualification_reasons": lead_score.qualification_reasons,
            "disqualification_reasons": lead_score.disqualification_reasons,
            "score_breakdown": {
                "icp_score": lead_score.icp_score,
                "financial_score": lead_score.financial_score,
                "technology_score": lead_score.technology_score,
                "contact_score": lead_score.contact_score,
                "company_score": lead_score.company_score,
                "engagement_score": lead_score.engagement_score
            },
            "success": True
        })
        
        return {
            "success": True,
            "qualified": is_qualified,
            "lead_score": lead_score,
            "prospect": prospect
        }
        
    except Exception as e:
        # Log error
        if lead_id:
            tracker.add_error(lead_id, ProgressStage.QUALIFIED, str(e))
        return {
            "success": False,
            "error": str(e),
            "prospect": prospect
        }


async def analyze_financial_opportunity(prospect: Prospect) -> Dict[str, Any]:
    """
    Analyze financial opportunity for a prospect.
    
    Args:
        prospect: Prospect to analyze
        
    Returns:
        Financial analysis results
    """
    try:
        # Get lead ID from tracker
        lead = tracker.get_lead_by_domain(prospect.domain)
        if not lead:
            lead_id = tracker.add_lead(prospect.domain, prospect.company_name)
        else:
            lead_id = lead.lead_id
        
        # Update stage to analysis
        tracker.update_stage(lead_id, ProgressStage.ANALYZED, {
            "start_time": datetime.now().isoformat()
        })
        
        # Detect financial leaks
        leak_detector = FinancialLeakDetector()
        leak_results = leak_detector.detect_financial_leaks(prospect)
        
        # Update tracker with analysis results
        summary = leak_results.get("summary", {})
        tracker.update_stage(lead_id, ProgressStage.ANALYZED, {
            "end_time": datetime.now().isoformat(),
            "monthly_waste": summary.get("total_monthly_waste", 0),
            "annual_waste": summary.get("total_annual_waste", 0),
            "monthly_savings": summary.get("total_monthly_savings", 0),
            "annual_savings": summary.get("total_annual_savings", 0),
            "roi_percentage": summary.get("roi_percentage", 0),
            "priority_recommendations": summary.get("priority_recommendations", []),
            "success": True
        })
        
        return {
            "success": True,
            "leak_results": leak_results,
            "prospect": prospect
        }
        
    except Exception as e:
        # Log error
        if lead_id:
            tracker.add_error(lead_id, ProgressStage.ANALYZED, str(e))
        return {
            "success": False,
            "error": str(e),
            "prospect": prospect
        }


async def process_prospect_advanced(prospect: Prospect, enrichment_engine: LeadEnrichmentEngine,
                                  qualification_engine: LeadQualificationEngine, 
                                  icps: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a prospect through the advanced pipeline.
    
    Args:
        prospect: Prospect to process
        enrichment_engine: Enrichment engine instance
        qualification_engine: Qualification engine instance
        icps: Dictionary of ICPs
        
    Returns:
        Processing results
    """
    results = {
        "domain": prospect.domain,
        "company_name": prospect.company_name,
        "success": False,
        "stages_completed": [],
        "final_qualified": False,
        "qualification_level": "D",
        "priority_level": 5
    }
    
    # 1. Advanced enrichment
    enrichment_results = await advanced_enrich_prospect(prospect, enrichment_engine)
    if enrichment_results["success"]:
        results["stages_completed"].append(ProgressStage.ENRICHED_ADVANCED)
        results["enrichment_summary"] = {
            "enriched_fields": enrichment_results["enrichment_result"].enriched_fields,
            "new_technologies": len(enrichment_results["enrichment_result"].new_technologies),
            "new_contacts": len(enrichment_results["enrichment_result"].new_contacts),
            "confidence_scores": enrichment_results["enrichment_result"].confidence_scores
        }
    else:
        results["error"] = f"Enrichment failed: {enrichment_results.get('error', 'Unknown error')}"
        return results
    
    # 2. Financial analysis
    financial_results = await analyze_financial_opportunity(prospect)
    if financial_results["success"]:
        results["stages_completed"].append(ProgressStage.ANALYZED)
        results["financial_summary"] = {
            "annual_savings": financial_results["leak_results"]["summary"]["total_annual_savings"],
            "roi_percentage": financial_results["leak_results"]["summary"]["roi_percentage"],
            "monthly_waste": financial_results["leak_results"]["summary"]["total_monthly_waste"]
        }
    else:
        results["error"] = f"Financial analysis failed: {financial_results.get('error', 'Unknown error')}"
        return results
    
    # 3. Advanced qualification against each ICP
    best_qualification = None
    best_score = 0
    
    for icp_name, icp in icps.items():
        qualification_results = await advanced_qualify_prospect(
            prospect, qualification_engine, icp, financial_results
        )
        
        if qualification_results["success"]:
            lead_score = qualification_results["lead_score"]
            
            if lead_score.total_score > best_score:
                best_score = lead_score.total_score
                best_qualification = {
                    "icp_name": icp_name,
                    "qualified": qualification_results["qualified"],
                    "lead_score": lead_score
                }
    
    if best_qualification:
        results["stages_completed"].append(ProgressStage.QUALIFIED)
        results["final_qualified"] = best_qualification["qualified"]
        results["qualification_level"] = best_qualification["lead_score"].qualification_level
        results["priority_level"] = best_qualification["lead_score"].priority_level
        results["best_icp"] = best_qualification["icp_name"]
        results["qualification_summary"] = {
            "total_score": best_qualification["lead_score"].total_score,
            "qualification_reasons": best_qualification["lead_score"].qualification_reasons,
            "disqualification_reasons": best_qualification["lead_score"].disqualification_reasons,
            "score_breakdown": {
                "icp_score": best_qualification["lead_score"].icp_score,
                "financial_score": best_qualification["lead_score"].financial_score,
                "technology_score": best_qualification["lead_score"].technology_score,
                "contact_score": best_qualification["lead_score"].contact_score,
                "company_score": best_qualification["lead_score"].company_score,
                "engagement_score": best_qualification["lead_score"].engagement_score
            }
        }
        
        # 4. Register qualified leads in CRM
        if best_qualification["qualified"]:
            try:
                crm_lead_id = crm_manager.register_prospect_with_leak_data(
                    prospect, financial_results["leak_results"]
                )
                if crm_lead_id:
                    results["stages_completed"].append(ProgressStage.REGISTERED_CRM)
                    results["crm_lead_id"] = crm_lead_id
            except Exception as e:
                results["crm_error"] = str(e)
    
    results["success"] = True
    return results


async def process_batch_advanced(prospects: List[Prospect], batch_size: int = 5) -> List[Dict[str, Any]]:
    """
    Process a batch of prospects through the advanced pipeline.
    
    Args:
        prospects: List of prospects to process
        batch_size: Number of prospects to process in parallel
        
    Returns:
        List of processing results
    """
    # Initialize engines
    enrichment_engine = LeadEnrichmentEngine()
    
    # Create qualification criteria for different scenarios (more lenient for testing)
    qualification_criteria = QualificationCriteria(
        min_employee_count=1,
        min_revenue=10000,
        max_revenue=100000000,
        min_icp_score=30.0,
        min_roi_percentage=5.0,
        min_annual_savings=1000.0,
        geographic_restrictions=["United States", "Canada", "United Kingdom", "Australia", "Brazil"]  # Include Brazil
    )
    qualification_engine = LeadQualificationEngine(qualification_criteria)
    
    # Create ICPs
    icps = {
        "shopify_dtc": ShopifyDTCPremiumICP(),
        "health_supplements": HealthSupplementsICP(),
        "fitness_equipment": FitnessEquipmentICP()
    }
    
    results = []
    
    # Process in batches
    for i in range(0, len(prospects), batch_size):
        batch = prospects[i:i+batch_size]
        tasks = [process_prospect_advanced(p, enrichment_engine, qualification_engine, icps) for p in batch]
        batch_results = await asyncio.gather(*tasks)
        results.extend(batch_results)
        print(f"Processed batch {i//batch_size + 1}/{(len(prospects)-1)//batch_size + 1}")
    
    return results


def generate_advanced_summary_report(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate an advanced summary report of processing results.
    
    Args:
        results: List of processing results
        
    Returns:
        Advanced summary report
    """
    # Get tracker summary
    tracker_summary = tracker.get_summary()
    
    # Calculate success rates
    total = len(results)
    successful = sum(1 for r in results if r.get("success", False))
    qualified = sum(1 for r in results if r.get("final_qualified", False))
    registered = sum(1 for r in results if ProgressStage.REGISTERED_CRM in r.get("stages_completed", []))
    
    # Qualification level distribution
    level_distribution = {"A": 0, "B": 0, "C": 0, "D": 0}
    priority_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    
    # Score analysis
    total_scores = []
    financial_scores = []
    icp_scores = []
    
    # Financial metrics
    total_annual_savings = 0
    total_monthly_waste = 0
    
    for result in results:
        if result.get("qualification_summary"):
            qual_summary = result["qualification_summary"]
            level_distribution[result.get("qualification_level", "D")] += 1
            priority_distribution[result.get("priority_level", 5)] += 1
            
            total_scores.append(qual_summary["total_score"])
            if "score_breakdown" in qual_summary:
                financial_scores.append(qual_summary["score_breakdown"]["financial_score"])
                icp_scores.append(qual_summary["score_breakdown"]["icp_score"])
        
        if result.get("financial_summary"):
            fin_summary = result["financial_summary"]
            total_annual_savings += fin_summary.get("annual_savings", 0)
            total_monthly_waste += fin_summary.get("monthly_waste", 0)
    
    # Calculate averages
    avg_total_score = sum(total_scores) / len(total_scores) if total_scores else 0
    avg_financial_score = sum(financial_scores) / len(financial_scores) if financial_scores else 0
    avg_icp_score = sum(icp_scores) / len(icp_scores) if icp_scores else 0
    avg_annual_savings = total_annual_savings / qualified if qualified > 0 else 0
    
    return {
        "timestamp": datetime.now().isoformat(),
        "processing_summary": {
            "total_prospects": total,
            "successful_prospects": successful,
            "success_rate": successful / total if total > 0 else 0,
            "qualified_prospects": qualified,
            "qualification_rate": qualified / successful if successful > 0 else 0,
            "registered_prospects": registered,
            "registration_rate": registered / qualified if qualified > 0 else 0
        },
        "qualification_analysis": {
            "level_distribution": level_distribution,
            "priority_distribution": priority_distribution,
            "average_scores": {
                "total_score": avg_total_score,
                "financial_score": avg_financial_score,
                "icp_score": avg_icp_score
            }
        },
        "financial_analysis": {
            "total_annual_savings": total_annual_savings,
            "average_annual_savings": avg_annual_savings,
            "total_monthly_waste": total_monthly_waste,
            "average_monthly_waste": total_monthly_waste / total if total > 0 else 0
        },
        "stage_performance": tracker_summary["stage_counts"],
        "conversion_rates": tracker_summary["conversion_rates"]
    }


def save_advanced_results(results: List[Dict[str, Any]], summary: Dict[str, Any], 
                         output_dir: str = "advanced_results") -> Tuple[str, str]:
    """
    Save advanced processing results and summary report.
    
    Args:
        results: List of processing results
        summary: Summary report
        output_dir: Output directory
        
    Returns:
        Tuple of (results_path, summary_path)
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_path = os.path.join(output_dir, f"advanced_results_{timestamp}.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    
    # Save summary
    summary_path = os.path.join(output_dir, f"advanced_summary_{timestamp}.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    
    return results_path, summary_path


async def main():
    """Main function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Advanced Lead Processing Pipeline")
    parser.add_argument("--limit", type=int, default=20, help="Maximum number of prospects to process")
    parser.add_argument("--batch-size", type=int, default=5, help="Number of prospects to process in parallel")
    parser.add_argument("--output-dir", type=str, default="advanced_results", help="Output directory")
    args = parser.parse_args()
    
    print("Advanced Lead Processing Pipeline")
    print("===============================")
    
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
    
    # Process prospects
    print("\nProcessing prospects with advanced pipeline...")
    start_time = time.time()
    results = await process_batch_advanced(prospects, args.batch_size)
    end_time = time.time()
    
    # Generate summary report
    print("\nGenerating advanced summary report...")
    summary = generate_advanced_summary_report(results)
    
    # Save results
    print("\nSaving results...")
    results_path, summary_path = save_advanced_results(results, summary, args.output_dir)
    
    # Print summary
    print("\nAdvanced Processing Summary:")
    print(f"- Total prospects: {summary['processing_summary']['total_prospects']}")
    print(f"- Successful: {summary['processing_summary']['successful_prospects']} ({summary['processing_summary']['success_rate']:.1%})")
    print(f"- Qualified: {summary['processing_summary']['qualified_prospects']} ({summary['processing_summary']['qualification_rate']:.1%})")
    print(f"- Registered in CRM: {summary['processing_summary']['registered_prospects']} ({summary['processing_summary']['registration_rate']:.1%})")
    
    print("\nQualification Level Distribution:")
    for level, count in summary['qualification_analysis']['level_distribution'].items():
        print(f"- Level {level}: {count}")
    
    print("\nPriority Distribution:")
    for priority, count in summary['qualification_analysis']['priority_distribution'].items():
        print(f"- Priority {priority}: {count}")
    
    print("\nAverage Scores:")
    scores = summary['qualification_analysis']['average_scores']
    print(f"- Total Score: {scores['total_score']:.1f}/100")
    print(f"- Financial Score: {scores['financial_score']:.1f}/100")
    print(f"- ICP Score: {scores['icp_score']:.1f}/100")
    
    print("\nFinancial Analysis:")
    financial = summary['financial_analysis']
    print(f"- Total Annual Savings: ${financial['total_annual_savings']:,.2f}")
    print(f"- Average Annual Savings: ${financial['average_annual_savings']:,.2f}")
    print(f"- Total Monthly Waste: ${financial['total_monthly_waste']:,.2f}")
    
    print(f"\nProcessing time: {end_time - start_time:.1f} seconds")
    
    print("\nResults saved to:")
    print(f"- {results_path}")
    print(f"- {summary_path}")
    
    print("\nAdvanced pipeline completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())