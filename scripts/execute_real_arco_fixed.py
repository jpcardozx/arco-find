#!/usr/bin/env python3
"""
🎯 ARCO-FIND EXECUTOR - USANDO MÓDULOS REAIS CORRIGIDOS
Execução dos módulos Python existentes com correções de importação
"""

import sys
import os
import asyncio
import json
from datetime import datetime
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent.parent  # Go up from scripts/ to project root
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

def print_header():
    """Print execution header"""
    print("=" * 80)
    print("🎯 ARCO-FIND - LEAD DISCOVERY ENGINE")
    print("📊 Using Real Python Modules (Fixed Imports)")
    print("=" * 80)

def validate_environment():
    """Validate that we can import core modules"""
    print("\n🔍 VALIDATING ENVIRONMENT...")
    
    validation_results = {}
    
    # Test core module imports
    modules_to_test = [
        ("config.api_keys", "APIConfig"),
        ("src.config.arco_config_manager", "ARCOConfigManager"),
        ("src.core.lead_qualification_engine", "LeadQualificationEngine"),
        ("src.main", "StrategicLeadOrchestrator")
    ]
    
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            validation_results[module_name] = "✅ SUCCESS"
            print(f"  ✅ {module_name}.{class_name}")
        except ImportError as e:
            validation_results[module_name] = f"❌ IMPORT ERROR: {e}"
            print(f"  ❌ {module_name}.{class_name} - Import Error: {e}")
        except AttributeError as e:
            validation_results[module_name] = f"❌ ATTRIBUTE ERROR: {e}"
            print(f"  ❌ {module_name}.{class_name} - Attribute Error: {e}")
        except Exception as e:
            validation_results[module_name] = f"❌ ERROR: {e}"
            print(f"  ❌ {module_name}.{class_name} - Error: {e}")
    
    return validation_results

async def execute_real_lead_discovery():
    """Execute lead discovery using real ARCO modules"""
    print("\n🚀 EXECUTING REAL LEAD DISCOVERY...")
    
    try:
        # Import and initialize core modules
        from config.api_keys import APIConfig
        from src.core.lead_qualification_engine import LeadQualificationEngine
        from src.main import StrategicLeadOrchestrator
        
        print("  📋 Modules imported successfully")
        
        # Initialize API configuration
        api_config = APIConfig()
        print(f"  🔑 API Config loaded - Project: {api_config.GOOGLE_CLOUD_PROJECT}")
        
        # Initialize lead qualification engine
        lead_engine = LeadQualificationEngine()
        print("  🎯 LeadQualificationEngine initialized")
        
        # Initialize strategic orchestrator
        orchestrator = StrategicLeadOrchestrator()
        print("  🎼 StrategicLeadOrchestrator initialized")
        
        # Execute qualified lead discovery
        print("\n📊 DISCOVERING QUALIFIED LEADS...")
        start_time = datetime.now()
        
        qualified_leads = await lead_engine.discover_qualified_leads(target_count=5)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Display results
        print(f"\n✅ LEAD DISCOVERY COMPLETED ({execution_time:.2f}s)")
        print(f"🎯 Qualified Leads Found: {len(qualified_leads)}")
        
        if qualified_leads:
            print("\n📋 TOP QUALIFIED LEADS:")
            for i, lead in enumerate(qualified_leads[:3], 1):
                print(f"  {i}. {lead.company_name}")
                print(f"     Website: {lead.website}")
                print(f"     Industry: {lead.industry}")
                print(f"     Score: {lead.qualification_score}/100")
                print(f"     Priority: {lead.conversion_priority}")
                print()
        
        # Execute strategic intelligence (if available)
        try:
            print("🧠 EXECUTING STRATEGIC INTELLIGENCE...")
            intelligence_results = await orchestrator.execute_intelligent_lead_discovery(target_count=3)
            
            if 'discovery_summary' in intelligence_results:
                summary = intelligence_results['discovery_summary']
                print(f"  📊 Existing Hot Leads: {summary.get('existing_hot_leads', 0)}")
                print(f"  🔍 New Leads Discovered: {summary.get('new_leads_discovered', 0)}")
                print(f"  ✅ Total Actionable: {summary.get('total_actionable_leads', 0)}")
        
        except Exception as e:
            print(f"  ⚠️ Strategic intelligence execution warning: {e}")
        
        return {
            'status': 'SUCCESS',
            'execution_time': execution_time,
            'qualified_leads_count': len(qualified_leads),
            'qualified_leads': [
                {
                    'company_name': lead.company_name,
                    'website': lead.website,
                    'qualification_score': lead.qualification_score,
                    'conversion_priority': lead.conversion_priority
                } for lead in qualified_leads[:5]
            ]
        }
        
    except Exception as e:
        print(f"❌ EXECUTION ERROR: {e}")
        return {
            'status': 'ERROR',
            'error': str(e)
        }

def execute_fallback_demo():
    """Execute fallback demo if real modules fail"""
    print("\n🚨 FALLBACK DEMO MODE")
    print("Real modules unavailable - demonstrating with sample data")
    
    # Sample qualified leads
    demo_leads = [
        {
            'company_name': 'TechFlow Solutions',
            'website': 'techflow.ca',
            'industry': 'Digital Marketing',
            'qualification_score': 85,
            'conversion_priority': 'HOT - 48h Conversion Target',
            'estimated_monthly_loss': 15000.0
        },
        {
            'company_name': 'GrowthLab Inc',
            'website': 'growthlab.io',
            'industry': 'SaaS',
            'qualification_score': 78,
            'conversion_priority': 'WARM - 7-day Nurture',
            'estimated_monthly_loss': 8500.0
        },
        {
            'company_name': 'MetaMax Agency',
            'website': 'metamax.com',
            'industry': 'E-commerce',
            'qualification_score': 72,
            'conversion_priority': 'HOT - 48h Conversion Target',
            'estimated_monthly_loss': 12000.0
        }
    ]
    
    print(f"\n📊 DEMO QUALIFIED LEADS: {len(demo_leads)}")
    for i, lead in enumerate(demo_leads, 1):
        print(f"  {i}. {lead['company_name']}")
        print(f"     Industry: {lead['industry']}")
        print(f"     Score: {lead['qualification_score']}/100")
        print(f"     Priority: {lead['conversion_priority']}")
        print(f"     Est. Loss: ${lead['estimated_monthly_loss']:,.0f}/month")
        print()
    
    return {
        'status': 'DEMO_MODE',
        'demo_leads': demo_leads
    }

async def main():
    """Main execution function"""
    print_header()
    
    # Validate environment
    validation_results = validate_environment()
    
    # Check if core modules are available
    core_modules_available = all(
        "SUCCESS" in result for result in validation_results.values()
    )
    
    if core_modules_available:
        print("\n✅ All core modules available - executing real ARCO pipeline")
        results = await execute_real_lead_discovery()
    else:
        print("\n⚠️ Some modules unavailable - executing fallback demo")
        results = execute_fallback_demo()
    
    # Save results
    results_file = project_root / f"arco_execution_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'execution_timestamp': datetime.now().isoformat(),
            'validation_results': validation_results,
            'execution_results': results
        }, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {results_file.name}")
    print(f"📊 Status: {results.get('status', 'UNKNOWN')}")
    
    if results.get('status') == 'SUCCESS':
        print("🎯 ARCO-FIND executed successfully with real modules!")
    elif results.get('status') == 'DEMO_MODE':
        print("⚠️ ARCO-FIND executed in demo mode due to module issues")
    else:
        print("❌ ARCO-FIND execution encountered errors")

if __name__ == "__main__":
    asyncio.run(main())
