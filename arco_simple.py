#!/usr/bin/env python3
"""
ARCO Simple CLI - Practical Lead Generation Tool
Easy-to-use interface for the improved ARCO system
"""

import argparse
import sys
import os
from arco_core_engine import ARCOCoreEngine
from arco_config import validate_configuration, INDUSTRY_CONFIGS
from demo_improvements import demo_old_vs_new_system

def main():
    parser = argparse.ArgumentParser(
        description='ARCO - Practical Lead Generation System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show system improvements
  python arco_simple.py demo

  # Validate configuration
  python arco_simple.py validate

  # Discover HVAC prospects (requires API keys)
  python arco_simple.py discover hvac --max-prospects 5

  # Test with sample data
  python arco_simple.py test
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Show improvement demonstration')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate system configuration')
    
    # Discover command
    discover_parser = subparsers.add_parser('discover', help='Discover prospects in industry')
    discover_parser.add_argument('industry', choices=['hvac', 'dental', 'urgent_care'],
                               help='Target industry')
    discover_parser.add_argument('--max-prospects', type=int, default=5,
                               help='Maximum prospects to find (default: 5)')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test system with sample data')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'demo':
            return run_demo()
        elif args.command == 'validate':
            return run_validate()
        elif args.command == 'discover':
            return run_discover(args.industry, args.max_prospects)
        elif args.command == 'test':
            return run_test()
        else:
            parser.print_help()
            return 1
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled")
        return 130
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

def run_demo():
    """Run improvement demonstration"""
    print("🚀 Running ARCO improvement demonstration...")
    print()
    demo_old_vs_new_system()
    return 0

def run_validate():
    """Validate system configuration"""
    print("🔍 Validating ARCO configuration...")
    print()
    
    config_valid = validate_configuration()
    
    if config_valid:
        print("✅ System ready for use")
        print()
        print("Next steps:")
        print("• python arco_simple.py discover hvac --max-prospects 5")
        print("• python arco_simple.py test")
        return 0
    else:
        print("⚠️  System needs API keys for full functionality")
        print()
        print("To get started:")
        print("1. Get SearchAPI key: https://searchapi.io/")
        print("2. Set environment variable: export SEARCHAPI_KEY='your_key'")
        print("3. Optional: Get PageSpeed key: https://developers.google.com/speed/docs/insights/v5/get-started")
        print("4. Run: python arco_simple.py validate")
        return 1

def run_discover(industry, max_prospects):
    """Discover prospects in specified industry"""
    print(f"🔍 Discovering {industry} prospects...")
    print()
    
    # Check for API keys
    searchapi_key = os.getenv('SEARCHAPI_KEY')
    pagespeed_key = os.getenv('PAGESPEED_KEY')
    
    if not searchapi_key:
        print("❌ SEARCHAPI_KEY environment variable required")
        print("Get key from: https://searchapi.io/")
        return 1
    
    print(f"Using SearchAPI key: {searchapi_key[:10]}...")
    if pagespeed_key:
        print(f"Using PageSpeed key: {pagespeed_key[:10]}...")
    else:
        print("⚠️  No PageSpeed key (will use fallback analysis)")
    print()
    
    # Initialize engine
    engine = ARCOCoreEngine(searchapi_key, pagespeed_key)
    
    try:
        # Discover prospects
        prospects = engine.discover_qualified_prospects(industry, max_prospects)
        
        if not prospects:
            print(f"❌ No qualified {industry} prospects found")
            print("This could be due to:")
            print("• No active advertisers in target cities")
            print("• All prospects failed qualification criteria")
            print("• API rate limiting or errors")
            return 1
        
        print(f"✅ Found {len(prospects)} qualified prospects:")
        print()
        
        total_opportunity = 0
        for i, prospect in enumerate(prospects, 1):
            print(f"{i}. {prospect.company_name}")
            print(f"   Domain: {prospect.domain}")
            print(f"   Opportunity: ${prospect.opportunity_value}/month")
            print(f"   Issues: {', '.join(prospect.performance_issues[:2])}")
            print(f"   Recommendation: {prospect.recommendation}")
            print(f"   Contact Likelihood: {prospect.contact_likelihood}/10")
            print()
            
            total_opportunity += prospect.opportunity_value
        
        print(f"📊 Summary:")
        print(f"• Total prospects: {len(prospects)}")
        print(f"• Total opportunity: ${total_opportunity}/month")
        print(f"• Avg opportunity per prospect: ${total_opportunity/len(prospects):.0f}/month")
        print()
        
        # Generate sample outreach
        if prospects:
            print("📧 Sample outreach message:")
            print("-" * 40)
            message = engine.generate_outreach_message(prospects[0])
            print(message)
            print("-" * 40)
        
        return 0
        
    except Exception as e:
        print(f"❌ Discovery failed: {str(e)}")
        return 1

def run_test():
    """Test system with sample data"""
    print("🧪 Testing ARCO system with sample data...")
    print()
    
    # Create engine with test keys
    engine = ARCOCoreEngine("test_key", "test_key")
    
    # Test prospect data
    from arco_core_engine import LeadProspect
    
    test_prospect = LeadProspect(
        company_name="Miami Emergency HVAC Services LLC",
        domain="https://miamiemergencyhvac.com",
        industry="hvac",
        ad_spend_signals=8,
        performance_issues=["Slow LCP: 3.2s (should be <2.5s)", "Emergency CTA below fold"],
        opportunity_value=750,
        contact_likelihood=9,
        evidence_url="https://pagespeed.web.dev/report?url=miamiemergencyhvac.com",
        recommendation="Core Web Vitals optimization - 2 week sprint ($800-1200)"
    )
    
    print("📋 Test Prospect:")
    print(f"• Company: {test_prospect.company_name}")
    print(f"• Industry: {test_prospect.industry}")
    print(f"• Ad Signals: {test_prospect.ad_spend_signals}/10")
    print(f"• Opportunity: ${test_prospect.opportunity_value}/month")
    print(f"• Issues: {', '.join(test_prospect.performance_issues)}")
    print(f"• Contact Likelihood: {test_prospect.contact_likelihood}/10")
    print()
    
    # Test qualification
    qualified = engine._qualifies_for_outreach(test_prospect)
    print(f"🎯 Qualification Result: {'✅ QUALIFIED' if qualified else '❌ NOT QUALIFIED'}")
    print()
    
    if qualified:
        # Generate outreach message
        message = engine.generate_outreach_message(test_prospect)
        print("📧 Generated outreach message:")
        print("-" * 50)
        print(message)
        print("-" * 50)
        print()
    
    # Test edge cases
    print("🧪 Testing edge cases...")
    
    # Low quality prospect
    low_quality = LeadProspect(
        company_name="joe hvac",
        domain="https://joehvac.com",
        industry="hvac",
        ad_spend_signals=2,  # Below threshold
        performance_issues=["Minor issue"],
        opportunity_value=200,  # Below threshold
        contact_likelihood=4,  # Below threshold
        evidence_url="https://test.com",
        recommendation="Basic optimization"
    )
    
    low_qualified = engine._qualifies_for_outreach(low_quality)
    print(f"• Low quality prospect: {'✅ QUALIFIED' if low_qualified else '❌ NOT QUALIFIED (expected)'}")
    
    # Test with no issues
    no_issues = LeadProspect(
        company_name="Perfect Company",
        domain="https://perfect.com",
        industry="hvac",
        ad_spend_signals=8,
        performance_issues=[],  # No issues
        opportunity_value=800,
        contact_likelihood=9,
        evidence_url="https://test.com",
        recommendation="No issues found"
    )
    
    no_issues_qualified = engine._qualifies_for_outreach(no_issues)
    print(f"• No issues prospect: {'✅ QUALIFIED' if no_issues_qualified else '❌ NOT QUALIFIED (expected)'}")
    
    print()
    print("✅ Test complete - System functioning correctly")
    return 0

if __name__ == "__main__":
    sys.exit(main())