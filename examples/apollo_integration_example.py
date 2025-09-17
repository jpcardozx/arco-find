"""
Example script demonstrating the Apollo CSV Integration.

This script shows how to use the Apollo CSV Integration to import prospect data
and integrate it with the ARCO pipeline.
"""

import sys
import os
import json
from datetime import datetime

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from arco.integrations.apollo_csv import ApolloCSVIntegration
from arco.models.icp import ShopifyDTCPremiumICP, HealthSupplementsICP
from arco.models.financial_leak import FinancialLeakDetector
from arco.models.roi_report import ROIReportGenerator
from arco.engines.discovery_engine import DiscoveryEngine


def main():
    """Run the example."""
    print("Apollo CSV Integration Example")
    print("=============================")
    
    # Initialize the Apollo CSV integration
    print("\nInitializing Apollo CSV integration...")
    apollo_integration = ApolloCSVIntegration()
    
    # Get all prospects from Apollo CSV files
    print("\nLoading prospects from Apollo CSV files...")
    prospects = apollo_integration.get_all_prospects()
    print(f"Loaded {len(prospects)} prospects from Apollo CSV files")
    
    # Create an ICP for filtering
    print("\nCreating ICPs for filtering...")
    shopify_icp = ShopifyDTCPremiumICP()
    health_icp = HealthSupplementsICP()
    
    # Create a discovery engine with the Shopify ICP
    print(f"\nCreating discovery engine with ICP: {shopify_icp.name}")
    engine = DiscoveryEngine(icp=shopify_icp)
    
    # Filter prospects by ICP
    print("\nFiltering prospects by ICP...")
    filtered_prospects = engine._filter_prospects_by_icp(prospects)
    print(f"Found {len(filtered_prospects)} prospects matching the {shopify_icp.name} ICP")
    
    # Create a financial leak detector
    print("\nCreating financial leak detector...")
    leak_detector = FinancialLeakDetector()
    
    # Create a ROI report generator
    print("\nCreating ROI report generator...")
    report_generator = ROIReportGenerator()
    
    # Create output directory for reports
    reports_dir = "apollo_reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    # Process the top 3 prospects
    print("\nProcessing top prospects...")
    for i, prospect in enumerate(filtered_prospects[:3]):
        print(f"\nProcessing prospect {i+1}: {prospect.company_name} ({prospect.domain})")
        
        # Print prospect details
        print(f"- Industry: {prospect.industry}")
        print(f"- Employee Count: {prospect.employee_count}")
        print(f"- Revenue: ${prospect.revenue:,.2f}" if prospect.revenue else "- Revenue: Unknown")
        print(f"- Country: {prospect.country}")
        print(f"- Technologies: {len(prospect.technologies)}")
        
        # Calculate match score
        match_score = shopify_icp.calculate_match_score(prospect)
        print(f"- ICP Match Score: {match_score:.1f}/100")
        
        # Detect financial leaks
        print("\nDetecting financial leaks...")
        leak_results = leak_detector.detect_financial_leaks(prospect)
        
        # Print financial leak summary
        summary = leak_results["summary"]
        print("\nFinancial Leak Summary:")
        print(f"- Total Monthly Waste: ${summary['total_monthly_waste']:.2f}")
        print(f"- Total Annual Waste: ${summary['total_annual_waste']:.2f}")
        print(f"- Total Monthly Savings: ${summary['total_monthly_savings']:.2f}")
        print(f"- Total Annual Savings: ${summary['total_annual_savings']:.2f}")
        print(f"- Three-Year Savings: ${summary['total_three_year_savings']:.2f}")
        print(f"- ROI Percentage: {summary['roi_percentage']:.1f}%")
        
        # Generate ROI report
        print("\nGenerating ROI report...")
        report = report_generator.generate_roi_report(prospect)
        
        # Save report to file
        filepath = report_generator.save_report_to_file(report, reports_dir)
        print(f"Report saved to: {filepath}")
        
        # Generate HTML report
        html_content = report_generator.generate_html_report(report)
        html_filepath = filepath.replace(".md", ".html")
        with open(html_filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"HTML report saved to: {html_filepath}")
    
    # Try with a different ICP
    print(f"\n\nSwitching to ICP: {health_icp.name}")
    engine.set_icp(health_icp)
    
    # Filter prospects by new ICP
    print("\nFiltering prospects by new ICP...")
    filtered_prospects = engine._filter_prospects_by_icp(prospects)
    print(f"Found {len(filtered_prospects)} prospects matching the {health_icp.name} ICP")
    
    # Save all prospects to a JSON file for further analysis
    print("\nSaving all prospects to JSON file...")
    prospects_data = [prospect.to_dict() for prospect in prospects]
    with open(os.path.join(reports_dir, "apollo_prospects.json"), "w", encoding="utf-8") as f:
        json.dump(prospects_data, f, indent=2)
    
    print("\nExample completed!")
    print(f"Reports saved to directory: {os.path.abspath(reports_dir)}")


if __name__ == "__main__":
    main()