#!/usr/bin/env python3
"""
ARCO V3 System Demo
Demonstrates the complete agent-based lead generation workflow
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("arco-demo")

async def demo_agent_workflow():
    """Demonstrate the complete agent workflow"""
    
    print("🚀 ARCO V3 AGENT SYSTEM DEMONSTRATION")
    print("="*50)
    
    try:
        # Import the agents
        from src.agents.discovery_agent import DiscoveryAgent
        from src.agents.performance_agent import PerformanceAgent
        from src.agents.scoring_agent import ScoringAgent
        from src.agents.outreach_agent import OutreachAgent
        from src.agents.analytics_agent import AnalyticsAgent
        from src.models.core_models import Vertical, DiscoveryOutput, PerformanceOutput
        
        print("✅ Agent modules imported successfully")
        
        # Create sample data to demonstrate workflow
        sample_discovery = DiscoveryOutput(
            advertiser_id="test_advertiser_123",
            domain="example-hvac.com",
            vertical="hvac_multi_location",
            currency="USD",
            last_seen=3,
            creative_count=8,
            demand_score=3,
            fit_score=2,
            discovery_timestamp=datetime.now(),
            company_name="Example HVAC Services",
            city="Tampa",
            geo_location="Tampa, FL"
        )
        
        print(f"🔍 Discovery Agent: Found {sample_discovery.company_name}")
        print(f"   • Domain: {sample_discovery.domain}")
        print(f"   • Vertical: {sample_discovery.vertical}")
        print(f"   • Demand Score: {sample_discovery.demand_score}")
        print(f"   • Fit Score: {sample_discovery.fit_score}")
        
        # Simulate performance analysis
        from src.models.core_models import PSIMetrics
        
        sample_performance = PerformanceOutput(
            domain=sample_discovery.domain,
            analyzed_urls=["https://example-hvac.com/", "https://example-hvac.com/contact"],
            performance_metrics={
                "https://example-hvac.com/": {
                    "mobile": PSIMetrics(lcp_p75=3.2, inp_p75=280, cls_p75=0.15, fcp_p75=2.1, score=45, device="mobile"),
                    "desktop": PSIMetrics(lcp_p75=2.1, inp_p75=180, cls_p75=0.08, fcp_p75=1.5, score=72, device="desktop")
                }
            },
            leak_indicators=["LCP_HIGH", "INP_HIGH", "NO_PHONE_CTA"],
            leak_score=6,
            evidence_screenshots=["evidence/example-hvac_20250809_performance.png"],
            priority_fixes=[
                "Image optimization + lazy loading (Est. 1.5s LCP improvement)",
                "JavaScript optimization + form feedback (Est. 150ms INP reduction)",
                "Add prominent click-to-call button (Est. 8% lead increase)"
            ],
            estimated_impact="20-30% conversion rate improvement potential",
            analysis_timestamp=datetime.now()
        )
        
        print(f"🚀 Performance Agent: Analyzed {sample_performance.domain}")
        print(f"   • Leak Score: {sample_performance.leak_score}/10")
        print(f"   • Key Issues: {', '.join(sample_performance.leak_indicators)}")
        print(f"   • Impact: {sample_performance.estimated_impact}")
        
        # Score the prospect
        scoring_agent = ScoringAgent()
        scored_prospect = scoring_agent.calculate_priority(sample_discovery, sample_performance)
        
        if scored_prospect:
            print(f"🎯 Scoring Agent: Prospect qualified!")
            print(f"   • Priority Score: {scored_prospect.priority_score}")
            print(f"   • Service Fit: {scored_prospect.service_fit.value}")
            print(f"   • Deal Size: ${scored_prospect.deal_size_range[0]}-${scored_prospect.deal_size_range[1]}")
            print(f"   • Monthly Loss: ${scored_prospect.estimated_monthly_loss:,}")
            print(f"   • Confidence: {scored_prospect.confidence_level:.1%}")
            
            # Generate outreach
            outreach_agent = OutreachAgent()
            outreach_message = outreach_agent.generate_message(scored_prospect)
            
            print(f"📧 Outreach Agent: Message generated")
            print(f"   • Subject: {outreach_message.subject_line}")
            print(f"   • Personalization Score: {outreach_message.personalization_score:.1%}")
            print(f"   • Primary Pain: {outreach_message.primary_pain_point}")
            print(f"   • Template: {outreach_message.vertical_template}")
            
            print("\n📩 Sample Message Preview:")
            print("-" * 40)
            lines = outreach_message.message_body.split('\n')
            for line in lines[:10]:  # Show first 10 lines
                print(line)
            if len(lines) > 10:
                print("... [message continues]")
            print("-" * 40)
            
            # Analytics
            analytics_agent = AnalyticsAgent()
            report = analytics_agent.generate_daily_report([scored_prospect], [outreach_message])
            
            print(f"📊 Analytics Agent: Daily report generated")
            print(f"   • Prospects Discovered: {report.prospects_discovered}")
            print(f"   • Prospects Qualified: {report.prospects_qualified}")
            print(f"   • Qualification Rate: {report.qualification_rate:.1%}")
            print(f"   • Outreach Sent: {report.outreach_sent}")
            
            if report.optimization_recommendations:
                print(f"   • Recommendations: {', '.join(report.optimization_recommendations)}")
            
        else:
            print("❌ Prospect did not qualify")
        
        print("\n✅ WORKFLOW DEMONSTRATION COMPLETE")
        print(f"🎯 System ready for production batch processing")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Run from project root: python demo/workflow_demo.py")
    except Exception as e:
        print(f"❌ Demo error: {e}")

if __name__ == "__main__":
    asyncio.run(demo_agent_workflow())