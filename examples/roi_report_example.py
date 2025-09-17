"""
Example script demonstrating the ROI Report Generation System.
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from arco.models.roi_report import ROIReportGenerator
from arco.models.prospect import Prospect, Technology
from arco.models.financial_leak import FinancialLeakDetector
from arco.models.icp import ShopifyDTCPremiumICP, HealthSupplementsICP


def main():
    """Run the example."""
    print("ROI Report Generation Example")
    print("============================")
    
    # Create a report generator
    generator = ROIReportGenerator()
    
    # Create sample prospects for demonstration
    print("\nCreating sample prospects for demonstration...")
    prospects = [
        Prospect(
            domain="beauty-store.com",
            company_name="Beauty Store",
            industry="Beauty",
            employee_count=25,
            revenue=1_500_000,
            country="United States"
        ),
        Prospect(
            domain="tech-saas.com",
            company_name="Tech SaaS",
            industry="SaaS",
            employee_count=42,
            revenue=2_800_000,
            country="United States"
        ),
        Prospect(
            domain="direct-consumer.com",
            company_name="Direct Consumer",
            industry="Direct-to-Consumer",
            employee_count=18,
            revenue=950_000,
            country="Canada"
        )
    ]
    
    # Add technologies to prospects
    prospects[0].technologies = [
        Technology(name="shopify", category="ecommerce_platform"),
        Technology(name="klaviyo", category="email_marketing"),
        Technology(name="mailchimp", category="email_marketing"),  # Redundant
        Technology(name="yotpo", category="reviews"),
        Technology(name="google_analytics", category="analytics"),
        Technology(name="hotjar", category="analytics")  # Redundant
    ]
    
    prospects[1].technologies = [
        Technology(name="wordpress", category="cms"),
        Technology(name="hubspot", category="marketing"),
        Technology(name="mailchimp", category="email_marketing"),
        Technology(name="intercom", category="support"),
        Technology(name="zendesk", category="support"),  # Redundant
        Technology(name="google_analytics", category="analytics"),
        Technology(name="mixpanel", category="analytics"),  # Redundant
        Technology(name="amplitude", category="analytics")  # Redundant
    ]
    
    prospects[2].technologies = [
        Technology(name="shopify", category="ecommerce_platform"),
        Technology(name="omnisend", category="email_marketing"),
        Technology(name="judge.me", category="reviews"),
        Technology(name="okendo", category="reviews")  # Redundant
    ]
    
    print(f"Created {len(prospects)} sample prospects")
    
    # Create output directory for reports
    reports_dir = "example_reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    # Generate reports for each prospect with different templates
    templates = [
        "14-Day Revenue Recovery Pilot",
        "Quarterly ROI Projection",
        "3-Year ROI Analysis"
    ]
    
    for i, prospect in enumerate(prospects):
        # Select a template for this prospect
        template = templates[i % len(templates)]
        
        print(f"\nGenerating {template} report for {prospect.company_name}...")
        
        # Generate report
        report = generator.generate_roi_report(prospect, template)
        
        # Save report to file
        filepath = generator.save_report_to_file(report, reports_dir)
        print(f"Report saved to: {filepath}")
        
        # Generate HTML report
        html_content = generator.generate_html_report(report)
        html_filepath = filepath.replace(".md", ".html")
        with open(html_filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"HTML report saved to: {html_filepath}")
        
        # Print report summary
        print("\nReport Summary:")
        print(f"- Template: {report['template']['name']}")
        print(f"- Monthly Waste: ${report['financial_leaks']['total_monthly_waste']:.2f}")
        print(f"- Annual Waste: ${report['financial_leaks']['total_annual_waste']:.2f}")
        print(f"- Pilot Savings: ${report['projected_savings']['pilot_savings']:.2f}")
        print(f"- First Year Savings: ${report['projected_savings']['annual_projections']['year1']:.2f}")
        print(f"- Three Year Savings: ${report['projected_savings']['three_year_projections']['total']:.2f}")
        print(f"- ROI Percentage: {report['projected_savings']['roi_metrics']['first_year_roi_percentage']:.1f}%")
        
        # Print priority recommendations
        print("\nPriority Recommendations:")
        for i, rec in enumerate(report['financial_leaks']['priority_recommendations'], 1):
            print(f"{i}. {rec}")
    
    print("\nExample completed!")
    print(f"Reports saved to directory: {os.path.abspath(reports_dir)}")


if __name__ == "__main__":
    main()