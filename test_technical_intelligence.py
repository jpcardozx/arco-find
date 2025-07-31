"""
🧪 TEST TECHNICAL INTELLIGENCE PIPELINE
Validates the new technical pain detection system
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.intelligence.technical_pain_detector import TechnicalPainDetector

def test_technical_intelligence():
    """Test the technical intelligence system with sample data"""
    
    print("🧪 Testing Technical Intelligence Pipeline")
    print("=" * 50)
    
    # Initialize detector
    pain_detector = TechnicalPainDetector()
    
    # Test scenarios
    scenarios = [
        {
            "name": "Critical Performance Issue",
            "company": "E-commerce Store ABC",
            "website": "https://store-abc.com",
            "performance_data": {"mobile_score": 25},
            "digital_presence": {"ads_found": 8},
            "business_context": {
                "monthly_ad_spend": 8000,
                "estimated_monthly_traffic": 25000,
                "avg_order_value": 120,
                "conversion_rate": 0.025
            }
        },
        {
            "name": "Message-Match Failure",
            "company": "Digital Agency XYZ", 
            "website": "https://agency-xyz.com",
            "performance_data": {"mobile_score": 75},
            "digital_presence": {"ads_found": 15},
            "business_context": {
                "monthly_ad_spend": 12000,
                "estimated_monthly_traffic": 15000,
                "avg_order_value": 3000,
                "conversion_rate": 0.02
            }
        },
        {
            "name": "Low-Impact Scenario",
            "company": "Small Business 123",
            "website": "https://smallbiz123.com", 
            "performance_data": {"mobile_score": 85},
            "digital_presence": {"ads_found": 2},
            "business_context": {
                "monthly_ad_spend": 1500,
                "estimated_monthly_traffic": 5000,
                "avg_order_value": 80,
                "conversion_rate": 0.015
            }
        }
    ]
    
    results = []
    
    for scenario in scenarios:
        print(f"\n🔍 Analyzing: {scenario['name']}")
        print("-" * 30)
        
        intelligence = pain_detector.analyze_technical_pain(
            company_name=scenario["company"],
            website=scenario["website"],
            performance_data=scenario["performance_data"],
            digital_presence=scenario["digital_presence"],
            business_context=scenario["business_context"]
        )
        
        results.append({
            "scenario": scenario["name"],
            "company": scenario["company"],
            "intelligence": intelligence
        })
        
        # Display results
        print(f"Company: {intelligence.company_name}")
        print(f"Monthly Pain Cost: ${intelligence.total_monthly_pain_cost:,.0f}")
        print(f"Annual Opportunity: ${intelligence.total_monthly_pain_cost * 12:,.0f}")
        print(f"Commercial Urgency: {intelligence.commercial_urgency.upper()}")
        print(f"Conversion Probability: {intelligence.conversion_probability:.1%}")
        print(f"Pain Points Found: {len(intelligence.pain_points)}")
        print(f"Rationale: {intelligence.rationale}")
        print(f"Next Action: {intelligence.next_action}")
        
        # Show top pain points
        if intelligence.pain_points:
            print("\nTop Pain Points:")
            for i, pain in enumerate(intelligence.pain_points[:2], 1):
                print(f"  {i}. {pain.category.title()}: ${pain.monthly_cost:,.0f}/month")
                print(f"     {pain.description}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TECHNICAL INTELLIGENCE SUMMARY")
    print("=" * 50)
    
    total_opportunity = sum(r["intelligence"].total_monthly_pain_cost * 12 for r in results)
    hot_leads = len([r for r in results if r["intelligence"].commercial_urgency == "hot"])
    avg_conversion = sum(r["intelligence"].conversion_probability for r in results) / len(results)
    
    print(f"Total Annual Opportunity: ${total_opportunity:,.0f}")
    print(f"Hot Leads (Immediate Action): {hot_leads}/{len(results)}")
    print(f"Average Conversion Probability: {avg_conversion:.1%}")
    
    # Show conversion-ready outputs
    print(f"\n🎯 CONVERSION-READY OUTPUTS:")
    for result in results:
        intelligence = result["intelligence"]
        if intelligence.commercial_urgency in ["hot", "warm"]:
            print(f"\n• {result['company']}")
            print(f"  Problem: Losing ${intelligence.total_monthly_pain_cost:,.0f}/month")
            print(f"  Action: {intelligence.next_action}")
            if intelligence.pain_points:
                top_pain = max(intelligence.pain_points, key=lambda p: p.monthly_cost)
                print(f"  Primary Issue: {top_pain.description}")
    
    print(f"\n✅ Test completed - {len(results)} scenarios analyzed")
    return results

if __name__ == "__main__":
    test_technical_intelligence()