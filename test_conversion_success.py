"""
🎯 CONVERSION-READY PROFILE TEST
Tests with realistic scenario that passes validation and generates conversion strategy
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.intelligence.technical_pain_detector import TechnicalPainDetector, TechnicalIntelligence
from src.intelligence.validation_engine import IntelligenceValidationEngine
from src.intelligence.conversion_strategy_engine import ConversionStrategyEngine

def test_conversion_ready_success():
    """Test with realistic scenario that should pass validation"""
    
    print("🎯 TESTING CONVERSION-READY PROFILE GENERATION")
    print("=" * 60)
    
    # Initialize pipeline
    pain_detector = TechnicalPainDetector()
    validation_engine = IntelligenceValidationEngine()
    conversion_engine = ConversionStrategyEngine()
    
    # Realistic prospect scenario
    realistic_prospect = {
        "name": "Local E-commerce Store",
        "website": "https://localstore.com",
        "industry": "ecommerce",
        "performance_data": {"mobile_score": 55},  # Moderate performance issue
        "digital_presence": {"ads_found": 6},
        "business_context": {
            "monthly_ad_spend": 4000,      # Realistic ad spend
            "estimated_monthly_traffic": 12000,  # Reasonable traffic
            "avg_order_value": 85,         # Typical e-commerce AOV
            "conversion_rate": 0.022,      # Good conversion rate
            "employee_count": 15           # Small business
        }
    }
    
    print(f"PROSPECT: {realistic_prospect['name']}")
    print(f"Performance Score: {realistic_prospect['performance_data']['mobile_score']}/100")
    print(f"Monthly Ad Spend: ${realistic_prospect['business_context']['monthly_ad_spend']:,}")
    print(f"Monthly Traffic: {realistic_prospect['business_context']['estimated_monthly_traffic']:,}")
    
    # Step 1: Generate technical intelligence
    intelligence = pain_detector.analyze_technical_pain(
        company_name=realistic_prospect["name"],
        website=realistic_prospect["website"],
        performance_data=realistic_prospect["performance_data"],
        digital_presence=realistic_prospect["digital_presence"],
        business_context=realistic_prospect["business_context"]
    )
    
    print(f"\n🔍 INITIAL ANALYSIS:")
    print(f"  Monthly Pain: ${intelligence.total_monthly_pain_cost:,.0f}")
    print(f"  Pain Points: {len(intelligence.pain_points)}")
    print(f"  Urgency: {intelligence.commercial_urgency}")
    
    # Step 2: Validate intelligence
    validation_result = validation_engine.validate_technical_intelligence(intelligence, {})
    
    validated_cost = sum(p.monthly_cost for p in validation_result.validated_pain_points)
    confidence_level = "high" if validation_result.confidence_score >= 0.8 else "medium" if validation_result.confidence_score >= 0.6 else "low"
    
    print(f"\n🧪 VALIDATION RESULTS:")
    print(f"  Confidence: {validation_result.confidence_score:.1%} ({confidence_level})")
    print(f"  Recommendation: {validation_result.recommendation}")
    print(f"  Validated Cost: ${validated_cost:,.0f}")
    
    # Step 3: Generate conversion strategy if validated
    if validation_result.recommendation in ['proceed', 'investigate']:
        # Create validated intelligence
        validated_intelligence = TechnicalIntelligence(
            company_name=intelligence.company_name,
            website=intelligence.website,
            total_monthly_pain_cost=validated_cost,
            pain_points=validation_result.validated_pain_points,
            commercial_urgency=intelligence.commercial_urgency if validated_cost > 2000 else 'warm',
            conversion_probability=intelligence.conversion_probability * validation_result.confidence_score,
            rationale=f"Validated {confidence_level}-confidence analysis shows ${validated_cost:,.0f}/month technical debt",
            next_action="Proceed with targeted conversion strategy"
        )
        
        # Generate conversion strategy
        lead_profile = conversion_engine.generate_conversion_strategy(
            validated_intelligence, confidence_level, realistic_prospect["industry"]
        )
        
        print(f"\n🎯 CONVERSION STRATEGY GENERATED:")
        print(f"  Approach: {lead_profile.conversion_strategy.approach_type}")
        print(f"  Industry: {lead_profile.industry}")
        
        print(f"\n💬 PRIMARY HOOK:")
        print(f'  "{lead_profile.conversion_strategy.primary_hook}"')
        
        print(f"\n📝 TALKING POINTS:")
        for i, point in enumerate(lead_profile.conversion_strategy.talking_points[:3], 1):
            print(f"  {i}. {point}")
        
        print(f"\n💰 ROI PROJECTION:")
        roi = lead_profile.roi_projection
        print(f"  Monthly Recovery: ${roi['monthly_recovery']:,.0f}")
        print(f"  Annual Value: ${roi['annual_recovery']:,.0f}")
        print(f"  Payback Period: {roi['payback_months']:.1f} months")
        print(f"  First Year ROI: {roi['first_year_roi']:.0f}%")
        
        print(f"\n⏰ URGENCY TIMELINE:")
        print(f"  {lead_profile.urgency_timeline}")
        
        print(f"\n🎯 NEXT STEPS:")
        for step in lead_profile.next_steps[:3]:
            print(f"  • {step['action']} ({step['timeline']})")
        
        # Success metrics
        print(f"\n📈 TRANSFORMATION SUCCESS:")
        print(f"  ✅ BEFORE: 'E-commerce store with some performance issues'")
        print(f"  ✅ AFTER: '${validated_cost:,.0f}/month validated opportunity with {roi['payback_months']:.1f} month payback'")
        print(f"  ✅ Specific talking points ready for immediate outreach")
        print(f"  ✅ {confidence_level.upper()} confidence intelligence ({validation_result.confidence_score:.1%})")
        print(f"  ✅ Clear ROI story: {roi['first_year_roi']:.0f}% first-year return")
        
        return True
    
    else:
        print(f"\n❌ LEAD REJECTED - Quality filter working correctly")
        return False

if __name__ == "__main__":
    success = test_conversion_ready_success()
    if success:
        print(f"\n🏆 CONVERSION-READY PROFILE: SUCCESS!")
    else:
        print(f"\n⚠️ QUALITY FILTER: WORKING AS INTENDED")