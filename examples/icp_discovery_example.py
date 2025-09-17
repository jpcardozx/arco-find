"""
Example script demonstrating ICP integration with the Discovery Engine
and Financial Leak Detection System.
"""

import asyncio
import json
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from arco.engines.discovery_engine import DiscoveryEngine
from arco.models.icp import ShopifyDTCPremiumICP, HealthSupplementsICP, FitnessEquipmentICP
from arco.models.financial_leak import FinancialLeakDetector
from arco.models.prospect import Prospect, Technology

async def main():
    """Run the example."""
    print("ICP Discovery Engine and Financial Leak Detection Example")
    print("=======================================================")
    
    # Create ICPs
    shopify_icp = ShopifyDTCPremiumICP()
    health_icp = HealthSupplementsICP()
    fitness_icp = FitnessEquipmentICP()
    
    # Create discovery engine with Shopify ICP
    print(f"\nCreating discovery engine with ICP: {shopify_icp.name}")
    engine = DiscoveryEngine(icp=shopify_icp)
    
    # Create financial leak detector
    leak_detector = FinancialLeakDetector()
    
    # Create mock prospects for demonstration
    print("\nCreating mock prospects for demonstration...")
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
            domain="skincare-direct.com",
            company_name="Skincare Direct",
            industry="Skincare",
            employee_count=18,
            revenue=900_000,
            country="United States"
        ),
        Prospect(
            domain="makeup-heaven.com",
            company_name="Makeup Heaven",
            industry="Cosmetics",
            employee_count=32,
            revenue=2_200_000,
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
        Technology(name="shopify_plus", category="ecommerce_platform"),
        Technology(name="klaviyo", category="email_marketing"),
        Technology(name="recharge", category="subscriptions"),
        Technology(name="gorgias", category="support"),
        Technology(name="zendesk", category="support")  # Redundant
    ]
    
    prospects[2].technologies = [
        Technology(name="shopify", category="ecommerce_platform"),
        Technology(name="omnisend", category="email_marketing"),
        Technology(name="judge.me", category="reviews"),
        Technology(name="okendo", category="reviews")  # Redundant
    ]
    
    print(f"Created {len(prospects)} mock prospects")
    
    # Generate ICP report
    print("\nGenerating ICP report...")
    report = engine.generate_icp_report(prospects)
    
    # Print ICP report summary
    print("\nICP Report Summary:")
    print(f"- ICP: {report['icp']['name']}")
    print(f"- Total Prospects: {report['summary']['total_prospects']}")
    print(f"- Qualified Prospects: {report['summary']['qualified_prospects']}")
    print(f"- Qualification Rate: {report['summary']['qualification_rate']:.1%}")
    print(f"- Average Match Score: {report['summary']['avg_match_score']:.1f}")
    print(f"- Total Monthly Waste: ${report['summary']['total_monthly_waste']:.2f}")
    print(f"- Total Annual Savings: ${report['summary']['total_annual_savings']:.2f}")
    
    # Perform financial leak detection
    print("\nPerforming financial leak detection...")
    for prospect in prospects:
        print(f"\nAnalyzing financial leaks for: {prospect.company_name} ({prospect.domain})")
        
        # Detect financial leaks
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
        
        # Print redundant apps
        if leak_results["redundant_apps"]["redundancies_detected"]:
            print("\nRedundant Apps Detected:")
            for pattern in leak_results["redundant_apps"]["patterns_matched"]:
                print(f"- {pattern['name']}: {pattern['description']}")
                for category in pattern["redundant_categories"]:
                    tools = pattern["redundant_tools"][category]
                    print(f"  * {category}: {', '.join(tools)}")
                print(f"  * Monthly Waste: ${pattern['estimated_monthly_waste']:.2f}")
        
        # Print performance vs. conversion issues
        if leak_results["performance_conversion"]["issues_detected"]:
            print("\nPerformance vs. Conversion Issues:")
            for analysis in leak_results["performance_conversion"]["analyses"]:
                print(f"- {analysis['name']}: {analysis['description']}")
                for recommendation in analysis["recommendations"]:
                    print(f"  * {recommendation}")
        
        # Print priority recommendations
        if summary["priority_recommendations"]:
            print("\nPriority Recommendations:")
            for i, recommendation in enumerate(summary["priority_recommendations"]):
                print(f"{i+1}. {recommendation}")
    
    # Try with a different ICP
    print(f"\n\nSwitching to ICP: {health_icp.name}")
    engine.set_icp(health_icp)
    
    # Create mock prospects for health supplements ICP
    print("\nCreating mock prospects for health supplements ICP...")
    health_prospects = [
        Prospect(
            domain="vitamins-direct.com",
            company_name="Vitamins Direct",
            industry="Health",
            employee_count=15,
            revenue=800_000,
            country="United States"
        ),
        Prospect(
            domain="supplement-store.com",
            company_name="Supplement Store",
            industry="Supplements",
            employee_count=22,
            revenue=1_200_000,
            country="Canada"
        )
    ]
    
    # Add technologies to prospects
    health_prospects[0].technologies = [
        Technology(name="shopify", category="ecommerce_platform"),
        Technology(name="klaviyo", category="email_marketing"),
        Technology(name="convertkit", category="email_marketing"),  # Redundant
        Technology(name="recharge", category="subscriptions")
    ]
    
    health_prospects[1].technologies = [
        Technology(name="woocommerce", category="ecommerce_platform"),
        Technology(name="mailchimp", category="email_marketing"),
        Technology(name="yotpo", category="reviews")
    ]
    
    print(f"Created {len(health_prospects)} mock prospects")
    
    # Generate report
    print("\nGenerating ICP report...")
    report = engine.generate_icp_report(health_prospects)
    
    # Print summary
    print("\nReport Summary:")
    print(f"- ICP: {report['icp']['name']}")
    print(f"- Total Prospects: {report['summary']['total_prospects']}")
    print(f"- Qualified Prospects: {report['summary']['qualified_prospects']}")
    
    # Perform financial leak detection for health supplements prospects
    print("\nPerforming financial leak detection for health supplements prospects...")
    for prospect in health_prospects:
        print(f"\nAnalyzing financial leaks for: {prospect.company_name} ({prospect.domain})")
        
        # Detect financial leaks
        leak_results = leak_detector.detect_financial_leaks(prospect)
        
        # Print financial leak summary
        summary = leak_results["summary"]
        print("\nFinancial Leak Summary:")
        print(f"- Total Monthly Waste: ${summary['total_monthly_waste']:.2f}")
        print(f"- Total Annual Waste: ${summary['total_annual_waste']:.2f}")
        print(f"- Total Monthly Savings: ${summary['total_monthly_savings']:.2f}")
        print(f"- Total Annual Savings: ${summary['total_annual_savings']:.2f}")
        
        # Print priority recommendations
        if summary["priority_recommendations"]:
            print("\nPriority Recommendations:")
            for i, recommendation in enumerate(summary["priority_recommendations"]):
                print(f"{i+1}. {recommendation}")
    
    # Clean up
    await engine.close()
    
    print("\nExample completed!")

if __name__ == "__main__":
    asyncio.run(main())