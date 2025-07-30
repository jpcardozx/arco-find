"""
🎯 STRATEGIC LEAD ORCHESTRATOR - MAIN ENTRY POINT
Intelligent lead generation with cost optimization and BigQuery analytics
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Core modules with fallback handling
try:
    from core.lead_qualification_engine import LeadQualificationEngine
except ImportError:
    print("⚠️ LeadQualificationEngine import failed - using fallback")
    class LeadQualificationEngine:
        def __init__(self): pass
        async def discover_qualified_leads(self, *args, **kwargs): return []

try:
    from intelligence.bigquery_intelligence import BigQueryIntelligence
except ImportError:
    print("⚠️ BigQueryIntelligence import failed - using fallback")
    class BigQueryIntelligence:
        def __init__(self): pass
        async def get_hot_leads_analysis(self): return {'data': []}

try:
    from connectors.searchapi_connector import SearchAPIConnector
except ImportError:
    print("⚠️ SearchAPIConnector import failed - using fallback")
    class SearchAPIConnector:
        def __init__(self): pass
        async def discover_strategic_prospects(self, *args, **kwargs): return []

try:
    from analysis.performance_analyzer import PerformanceAnalyzer
except ImportError:
    print("⚠️ PerformanceAnalyzer import failed - using fallback")
    class PerformanceAnalyzer:
        def __init__(self): pass

try:
    from utils.logger import setup_logger
    from utils.logger import cost_tracker, performance_monitor
except ImportError:
    import logging
    def setup_logger(name): return logging.getLogger(name)
    # Fallback classes for monitoring
    class FallbackMonitor:
        def start_operation(self, name): return f"op_{datetime.now().timestamp()}"
        def end_operation(self, op_id, data): pass
        def get_daily_summary(self): return {}
    
    cost_tracker = FallbackMonitor()
    performance_monitor = FallbackMonitor()

# Fallback SearchTarget
class SearchTarget:
    def __init__(self, industry="", pain_point_keywords=None, company_size_range=(0,0), location_focus="", priority_score=0):
        self.industry = industry
        self.pain_point_keywords = pain_point_keywords or []
        self.company_size_range = company_size_range
        self.location_focus = location_focus
        self.priority_score = priority_score

logger = setup_logger(__name__)

class StrategicLeadOrchestrator:
    """
    Main orchestrator for strategic lead generation with cost optimization
    """
    
    def __init__(self):
        self.lead_engine = LeadQualificationEngine()
        self.bigquery = BigQueryIntelligence()
        self.search_connector = SearchAPIConnector()
        self.performance_analyzer = PerformanceAnalyzer()
        
        # Operational settings
        self.max_daily_cost = 10.0  # $10 daily budget
        self.current_session_cost = 0.0
        
    async def execute_intelligent_lead_discovery(self, target_count: int = 20) -> Dict:
        """
        Execute intelligent lead discovery with cost optimization
        """
        operation_id = performance_monitor.start_operation("intelligent_lead_discovery")
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"🚀 Starting intelligent lead discovery - Target: {target_count} qualified leads")
            
            # Step 1: Check existing hot leads (FREE - no API cost)
            logger.info("📊 Step 1: Analyzing existing hot leads...")
            hot_leads_analysis = await self.bigquery.get_hot_leads_analysis()
            
            existing_hot_count = 0
            if 'data' in hot_leads_analysis:
                for urgency_group in hot_leads_analysis['data']:
                    if urgency_group.get('urgency_level') == 'HOT':
                        existing_hot_count = urgency_group.get('lead_count', 0)
                        break
            
            logger.info(f"🔥 Found {existing_hot_count} existing HOT leads ready for immediate outreach")
            
            # Step 2: Strategic new lead discovery if needed
            new_leads_needed = max(0, target_count - existing_hot_count)
            discovered_leads = []
            
            if new_leads_needed > 0:
                logger.info(f"🔍 Step 2: Discovering {new_leads_needed} new strategic leads...")
                
                # Prioritize search targets based on S-tier analysis
                priority_targets = self._get_priority_search_targets()
                
                for target in priority_targets:
                    if len(discovered_leads) >= new_leads_needed:
                        break
                    
                    # Check cost limits before expensive operations
                    if await self._check_cost_limits():
                        target_leads = await self.search_connector.discover_strategic_prospects(
                            target, max_results=min(new_leads_needed - len(discovered_leads), 5)
                        )
                        discovered_leads.extend(target_leads)
                    else:
                        logger.warning("⚠️ Cost limit reached, stopping new lead discovery")
                        break
            
            # Step 3: Qualify and analyze new discoveries
            qualified_new_leads = []
            if discovered_leads:
                logger.info(f"🎯 Step 3: Qualifying {len(discovered_leads)} discovered prospects...")
                
                for lead in discovered_leads:
                    if await self._check_cost_limits():
                        qualified_lead = await self.lead_engine.qualify_lead_comprehensive(lead)
                        if qualified_lead.get('qualification_score', 0) >= 60:
                            qualified_new_leads.append(qualified_lead)
                    else:
                        break
            
            # Step 4: Generate strategic intelligence summary
            logger.info("📈 Step 4: Generating strategic intelligence summary...")
            intelligence_summary = await self._generate_intelligence_summary()
            
            # Step 5: Create actionable results
            results = {
                'operation': 'intelligent_lead_discovery',
                'timestamp': datetime.utcnow().isoformat(),
                'execution_time_seconds': (datetime.utcnow() - start_time).total_seconds(),
                
                'discovery_summary': {
                    'existing_hot_leads': existing_hot_count,
                    'new_leads_discovered': len(discovered_leads),
                    'new_leads_qualified': len(qualified_new_leads),
                    'total_actionable_leads': existing_hot_count + len(qualified_new_leads)
                },
                
                'cost_analysis': await self._get_session_cost_analysis(),
                'strategic_intelligence': intelligence_summary,
                'qualified_new_leads': qualified_new_leads[:10],  # Top 10 for immediate action
                
                'immediate_actions': self._generate_immediate_actions(
                    existing_hot_count, qualified_new_leads, intelligence_summary
                )
            }
            
            # Save results
            await self._save_discovery_results(results)
            
            performance_monitor.end_operation(operation_id, {
                'leads_discovered': len(discovered_leads),
                'leads_qualified': len(qualified_new_leads),
                'total_cost': self.current_session_cost
            })
            
            logger.info(f"✅ Intelligent lead discovery completed - {results['discovery_summary']['total_actionable_leads']} actionable leads")
            return results
            
        except Exception as e:
            logger.error(f"❌ Intelligent lead discovery failed: {e}")
            performance_monitor.end_operation(operation_id, {'error': str(e)})
            return {'error': str(e), 'operation': 'intelligent_lead_discovery'}
    
    def _get_priority_search_targets(self) -> List[SearchTarget]:
        """Get prioritized search targets based on S-tier market analysis"""
        return [
            SearchTarget(
                industry="Digital Marketing Agency",
                pain_point_keywords=["conversion tracking issues", "meta ads problems", "low ROAS"],
                company_size_range=(10, 50),
                location_focus="United States",
                priority_score=10
            ),
            SearchTarget(
                industry="E-commerce",
                pain_point_keywords=["abandoned cart", "low conversion rate", "facebook ads not working"],
                company_size_range=(15, 100),
                location_focus="United States",
                priority_score=9
            ),
            SearchTarget(
                industry="SaaS",
                pain_point_keywords=["customer acquisition cost", "churn rate", "marketing attribution"],
                company_size_range=(20, 200),
                location_focus="United States",
                priority_score=8
            )
        ]
    
    async def _check_cost_limits(self) -> bool:
        """Check if we can proceed with cost-incurring operations"""
        return self.current_session_cost < self.max_daily_cost
    
    async def _generate_intelligence_summary(self) -> Dict:
        """Generate strategic intelligence summary with cost control"""
        try:
            # Collect intelligence with cost awareness
            analyses = {}
            
            if await self._check_cost_limits():
                analyses['industry'] = await self.bigquery.get_industry_intelligence()
                self.current_session_cost += analyses['industry'].get('cost_info', {}).get('actual_cost', 0)
            
            if await self._check_cost_limits():
                analyses['pipeline'] = await self.bigquery.get_conversion_pipeline_health()
                self.current_session_cost += analyses['pipeline'].get('cost_info', {}).get('actual_cost', 0)
            
            if await self._check_cost_limits():
                analyses['market_gaps'] = await self.bigquery.identify_market_gaps()
                self.current_session_cost += analyses['market_gaps'].get('cost_info', {}).get('actual_cost', 0)
            
            # Generate summary
            return self.bigquery.generate_intelligence_summary(analyses)
            
        except Exception as e:
            logger.error(f"❌ Intelligence summary generation failed: {e}")
            return {'error': str(e)}
    
    async def _get_session_cost_analysis(self) -> Dict:
        """Get current session cost analysis"""
        bigquery_usage = await self.bigquery.get_daily_cost_usage()
        search_usage = await self.search_connector.get_search_usage_stats()
        performance_usage = await self.performance_analyzer.get_analysis_usage_stats()
        
        return {
            'total_session_cost': self.current_session_cost,
            'daily_budget': self.max_daily_cost,
            'remaining_budget': self.max_daily_cost - self.current_session_cost,
            'bigquery_usage': bigquery_usage,
            'search_usage': search_usage,
            'performance_usage': performance_usage
        }
    
    def _generate_immediate_actions(self, hot_leads: int, new_qualified: List[Dict], 
                                   intelligence: Dict) -> List[Dict]:
        """Generate immediate actionable recommendations"""
        actions = []
        
        # Hot leads immediate action
        if hot_leads > 0:
            actions.append({
                'priority': 'IMMEDIATE',
                'action': 'Contact existing hot leads',
                'description': f'{hot_leads} hot leads ready for outreach within 24 hours',
                'expected_outcome': 'Quick wins, immediate revenue opportunities',
                'timeline': 'Next 24 hours'
            })
        
        # New qualified leads action
        if new_qualified:
            top_qualified = sorted(new_qualified, key=lambda x: x.get('qualification_score', 0), reverse=True)[:3]
            actions.append({
                'priority': 'HIGH',
                'action': 'Engage top new prospects',
                'description': f'Contact top 3 newly qualified leads (scores: {[l.get("qualification_score", 0) for l in top_qualified]})',
                'expected_outcome': 'Build pipeline, establish new relationships',
                'timeline': 'Next 3-5 days'
            })
        
        # Strategic intelligence actions
        if 'key_insights' in intelligence:
            for insight in intelligence['key_insights'][:2]:
                actions.append({
                    'priority': 'STRATEGIC',
                    'action': 'Market intelligence follow-up',
                    'description': insight,
                    'expected_outcome': 'Informed targeting, competitive advantage',
                    'timeline': 'Next 1-2 weeks'
                })
        
        return actions
    
    async def _save_discovery_results(self, results: Dict):
        """Save discovery results to file and BigQuery"""
        try:
            # Save to file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"strategic_lead_discovery_{timestamp}.json"
            
            exports_dir = Path("exports")
            exports_dir.mkdir(exist_ok=True)
            
            with open(exports_dir / filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"📁 Results saved to {filename}")
            
            # Save qualified leads to BigQuery (if cost allows)
            if await self._check_cost_limits() and results.get('qualified_new_leads'):
                await self.lead_engine.save_qualified_leads_to_bigquery(results['qualified_new_leads'])
            
        except Exception as e:
            logger.error(f"❌ Failed to save discovery results: {e}")

    async def execute_performance_audit(self, websites: List[str]) -> Dict:
        """Execute performance audit for discovered leads"""
        operation_id = performance_monitor.start_operation("performance_audit")
        
        try:
            logger.info(f"⚡ Starting performance audit for {len(websites)} websites")
            
            # Batch analyze with cost control
            performance_results = []
            for website in websites:
                if await self._check_cost_limits():
                    result = await self.performance_analyzer.analyze_website_performance(website)
                    performance_results.append(result)
                else:
                    logger.warning("⚠️ Cost limit reached, stopping performance audit")
                    break
            
            # Generate performance intelligence
            performance_summary = self._generate_performance_summary(performance_results)
            
            results = {
                'operation': 'performance_audit',
                'timestamp': datetime.utcnow().isoformat(),
                'websites_analyzed': len(performance_results),
                'performance_summary': performance_summary,
                'detailed_results': performance_results,
                'cost_analysis': await self._get_session_cost_analysis()
            }
            
            performance_monitor.end_operation(operation_id, {
                'websites_analyzed': len(performance_results),
                'total_cost': self.current_session_cost
            })
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Performance audit failed: {e}")
            performance_monitor.end_operation(operation_id, {'error': str(e)})
            return {'error': str(e)}
    
    def _generate_performance_summary(self, results: List[Dict]) -> Dict:
        """Generate performance audit summary"""
        if not results:
            return {'error': 'No performance data available'}
        
        scores = [r.get('performance_score', 0) for r in results if 'performance_score' in r]
        critical_issues = []
        high_opportunities = []
        
        for result in results:
            # Collect critical issues
            critical_issues.extend(result.get('critical_issues', []))
            
            # Collect high-impact opportunities
            recommendations = result.get('recommendations', [])
            high_opportunities.extend([r for r in recommendations if r.get('priority') == 'Critical'])
        
        return {
            'avg_performance_score': sum(scores) / len(scores) if scores else 0,
            'performance_distribution': {
                'excellent': len([s for s in scores if s >= 90]),
                'good': len([s for s in scores if 70 <= s < 90]),
                'poor': len([s for s in scores if s < 70])
            },
            'critical_issues_count': len(critical_issues),
            'high_priority_opportunities': len(high_opportunities),
            'total_websites_analyzed': len(results)
        }

async def main():
    """Main execution function for strategic lead discovery"""
    orchestrator = StrategicLeadOrchestrator()
    
    logger.info("🎯 ARCO Strategic Lead Discovery System - Starting...")
    
    try:
        # Execute intelligent lead discovery
        discovery_results = await orchestrator.execute_intelligent_lead_discovery(target_count=15)
        
        if 'error' not in discovery_results:
            logger.info("✅ Strategic lead discovery completed successfully")
            
            # Extract websites for performance audit
            qualified_leads = discovery_results.get('qualified_new_leads', [])
            websites = [lead.get('website') for lead in qualified_leads if lead.get('website')]
            
            if websites:
                logger.info(f"⚡ Starting performance audit for {len(websites)} websites...")
                performance_results = await orchestrator.execute_performance_audit(websites)
                
                if 'error' not in performance_results:
                    logger.info("✅ Performance audit completed successfully")
                else:
                    logger.error(f"❌ Performance audit failed: {performance_results['error']}")
        else:
            logger.error(f"❌ Strategic lead discovery failed: {discovery_results['error']}")
    
    except Exception as e:
        logger.error(f"❌ Main execution failed: {e}")
    
    finally:
        # Final cost summary
        final_stats = cost_tracker.get_daily_summary()
        logger.info(f"💰 Session completed - Total cost: ${final_stats.get('total_cost', 0):.4f}")

if __name__ == "__main__":
    asyncio.run(main())
