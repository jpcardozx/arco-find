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
    from core.arco_engine import ARCOEngine
    from intelligence.technical_pain_detector import TechnicalPainDetector
except ImportError:
    print("⚠️ ARCO Engine import failed - using fallback")
    class ARCOEngine:
        def __init__(self): pass
        def discover_technical_intelligence(self, *args, **kwargs): 
            return type('TechnicalIntelligence', (), {
                'total_monthly_pain_cost': 0,
                'commercial_urgency': 'cold',
                'conversion_probability': 0.1,
                'rationale': 'No technical analysis available',
                'next_action': 'Manual qualification needed'
            })()
        def discover_and_qualify_leads(self, *args, **kwargs): return []

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
    Main orchestrator for intelligent lead generation using technical pain detection
    """
    
    def __init__(self):
        self.arco_engine = ARCOEngine()
        self.lead_engine = LeadQualificationEngine()
        self.bigquery = BigQueryIntelligence()
        self.search_connector = SearchAPIConnector()
        self.performance_analyzer = PerformanceAnalyzer()
        
        # Operational settings
        self.max_daily_cost = 10.0  # $10 daily budget
        self.current_session_cost = 0.0
        
    async def execute_intelligent_lead_discovery(self, target_count: int = 20) -> Dict:
        """
        Execute intelligent lead discovery using technical pain detection
        """
        operation_id = performance_monitor.start_operation("intelligent_lead_discovery")
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"🧠 Starting intelligent lead discovery with technical pain detection - Target: {target_count} leads")
            
            # Step 1: Use ARCO engine to discover and qualify leads with technical intelligence
            logger.info("🔍 Step 1: Technical intelligence discovery...")
            qualified_leads = self.arco_engine.discover_and_qualify_leads(
                limit=target_count * 2,  # 2x buffer for qualification
                industry_filter=None
            )
            
            # Step 2: Filter leads based on technical pain thresholds
            logger.info("🎯 Step 2: Filtering leads by technical pain criteria...")
            high_value_leads = []
            warm_leads = []
            cold_leads = []
            
            for lead in qualified_leads:
                monthly_pain_cost = lead.get('monthly_pain_cost', 0)
                urgency = lead.get('commercial_urgency', 'cold')
                
                if monthly_pain_cost >= 5000 or urgency == 'hot':
                    high_value_leads.append(lead)
                elif monthly_pain_cost >= 2000 or urgency == 'warm':
                    warm_leads.append(lead)
                else:
                    cold_leads.append(lead)
            
            # Step 3: Prioritize leads by technical intelligence
            logger.info("📊 Step 3: Prioritizing by commercial impact...")
            prioritized_leads = self._prioritize_by_technical_intelligence(
                high_value_leads, warm_leads, cold_leads, target_count
            )
            
            # Step 4: Generate actionable intelligence summary
            logger.info("🧠 Step 4: Generating actionable intelligence...")
            intelligence_summary = self._generate_technical_intelligence_summary(prioritized_leads)
            
            # Step 5: Create conversion-ready results
            results = {
                'operation': 'intelligent_technical_discovery',
                'timestamp': datetime.utcnow().isoformat(),
                'execution_time_seconds': (datetime.utcnow() - start_time).total_seconds(),
                
                'technical_discovery_summary': {
                    'total_leads_analyzed': len(qualified_leads),
                    'high_value_leads': len(high_value_leads),
                    'warm_leads': len(warm_leads),
                    'cold_leads': len(cold_leads),
                    'final_prioritized_count': len(prioritized_leads)
                },
                
                'commercial_intelligence': {
                    'total_monthly_pain_identified': sum(l.get('monthly_pain_cost', 0) for l in prioritized_leads),
                    'total_annual_opportunity': sum(l.get('annual_opportunity', 0) for l in prioritized_leads),
                    'average_conversion_probability': sum(l.get('conversion_probability', 0) for l in prioritized_leads) / len(prioritized_leads) if prioritized_leads else 0,
                    'hot_leads_ready_for_immediate_contact': len([l for l in prioritized_leads if l.get('commercial_urgency') == 'hot'])
                },
                
                'prioritized_leads': prioritized_leads,
                'technical_intelligence_summary': intelligence_summary,
                'cost_analysis': await self._get_session_cost_analysis(),
                
                'immediate_actions': self._generate_technical_action_plan(prioritized_leads)
            }
            
            # Save results
            await self._save_discovery_results(results)
            
            performance_monitor.end_operation(operation_id, {
                'leads_qualified': len(qualified_leads),
                'high_value_leads': len(high_value_leads),
                'total_cost': self.current_session_cost
            })
            
            logger.info(f"✅ Technical intelligence discovery completed - {len(prioritized_leads)} actionable leads with ${results['commercial_intelligence']['total_monthly_pain_identified']:,.0f}/month pain identified")
            return results
            
        except Exception as e:
            logger.error(f"❌ Intelligent lead discovery failed: {e}")
            performance_monitor.end_operation(operation_id, {'error': str(e)})
            return {'error': str(e), 'operation': 'intelligent_technical_discovery'}
    
    def _prioritize_by_technical_intelligence(self, high_value: List[Dict], warm: List[Dict], 
                                            cold: List[Dict], target_count: int) -> List[Dict]:
        """Prioritize leads based on technical pain and commercial impact"""
        
        # Sort each category by priority score (highest first)
        high_value_sorted = sorted(high_value, key=lambda x: x.get('score', 0), reverse=True)
        warm_sorted = sorted(warm, key=lambda x: x.get('score', 0), reverse=True)
        cold_sorted = sorted(cold, key=lambda x: x.get('score', 0), reverse=True)
        
        # Prioritize: All high-value, then warm up to remaining slots, then cold if needed
        prioritized = []
        
        # Take all high-value leads (they have >$5k/month pain or hot urgency)
        prioritized.extend(high_value_sorted)
        
        # Fill remaining slots with warm leads
        remaining_slots = target_count - len(prioritized)
        if remaining_slots > 0:
            prioritized.extend(warm_sorted[:remaining_slots])
        
        # If still need more, take top cold leads
        remaining_slots = target_count - len(prioritized)
        if remaining_slots > 0:
            prioritized.extend(cold_sorted[:remaining_slots])
        
        return prioritized[:target_count]
    
    def _generate_technical_intelligence_summary(self, leads: List[Dict]) -> Dict:
        """Generate summary of technical intelligence findings"""
        if not leads:
            return {'message': 'No qualified leads with technical pain identified'}
        
        # Aggregate pain point categories
        pain_categories = {}
        total_pain_cost = 0
        urgent_leads = 0
        high_conversion_leads = 0
        
        for lead in leads:
            # Aggregate costs
            monthly_cost = lead.get('monthly_pain_cost', 0)
            total_pain_cost += monthly_cost
            
            # Count urgency levels
            if lead.get('commercial_urgency') == 'hot':
                urgent_leads += 1
            
            # Count high-conversion probability leads
            if lead.get('conversion_probability', 0) > 0.6:
                high_conversion_leads += 1
            
            # Aggregate pain point categories
            for pain_point in lead.get('pain_points', []):
                category = pain_point.get('category', 'unknown')
                if category not in pain_categories:
                    pain_categories[category] = {
                        'count': 0,
                        'total_cost': 0,
                        'avg_severity': []
                    }
                
                pain_categories[category]['count'] += 1
                pain_categories[category]['total_cost'] += pain_point.get('monthly_cost', 0)
                severity_score = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}.get(pain_point.get('severity', 'low'), 1)
                pain_categories[category]['avg_severity'].append(severity_score)
        
        # Calculate averages
        for category in pain_categories.values():
            if category['avg_severity']:
                category['avg_severity'] = sum(category['avg_severity']) / len(category['avg_severity'])
            else:
                category['avg_severity'] = 0
        
        return {
            'leads_analyzed': len(leads),
            'total_monthly_pain_cost': total_pain_cost,
            'total_annual_opportunity': total_pain_cost * 12,
            'urgent_leads_requiring_immediate_action': urgent_leads,
            'high_conversion_probability_leads': high_conversion_leads,
            'pain_categories_breakdown': pain_categories,
            'average_pain_per_lead': total_pain_cost / len(leads) if leads else 0,
            'key_insights': self._generate_key_insights(leads, pain_categories)
        }
    
    def _generate_key_insights(self, leads: List[Dict], pain_categories: Dict) -> List[str]:
        """Generate key actionable insights from technical analysis"""
        insights = []
        
        # Top pain category insight
        if pain_categories:
            top_category = max(pain_categories.items(), key=lambda x: x[1]['total_cost'])
            insights.append(
                f"Primary opportunity: {top_category[0]} issues affecting {top_category[1]['count']} leads "
                f"(${top_category[1]['total_cost']:,.0f}/month total pain)"
            )
        
        # Urgency insight
        hot_leads = [l for l in leads if l.get('commercial_urgency') == 'hot']
        if hot_leads:
            avg_hot_cost = sum(l.get('monthly_pain_cost', 0) for l in hot_leads) / len(hot_leads)
            insights.append(
                f"Immediate action required: {len(hot_leads)} hot leads with average "
                f"${avg_hot_cost:,.0f}/month pain each"
            )
        
        # Conversion probability insight
        high_conv_leads = [l for l in leads if l.get('conversion_probability', 0) > 0.7]
        if high_conv_leads:
            insights.append(
                f"High-probability conversions: {len(high_conv_leads)} leads with >70% conversion probability"
            )
        
        # Solution fit insight
        performance_issues = len([l for l in leads 
                                for p in l.get('pain_points', []) 
                                if p.get('category') == 'performance'])
        if performance_issues > len(leads) * 0.6:  # >60% have performance issues
            insights.append(
                f"Market opportunity: {performance_issues} prospects with performance issues "
                f"(our core strength)"
            )
        
        return insights
    
    def _generate_technical_action_plan(self, leads: List[Dict]) -> List[Dict]:
        """Generate specific action plan based on technical intelligence"""
        actions = []
        
        # Immediate actions for hot leads
        hot_leads = [l for l in leads if l.get('commercial_urgency') == 'hot']
        if hot_leads:
            for lead in hot_leads[:3]:  # Top 3 hot leads
                primary_pain = max(lead.get('pain_points', []), 
                                 key=lambda p: p.get('monthly_cost', 0), 
                                 default={})
                
                actions.append({
                    'priority': 'IMMEDIATE',
                    'timeline': 'Next 24 hours',
                    'action': f"Contact {lead.get('name', 'Unknown')}",
                    'approach': lead.get('next_action', 'Technical demonstration call'),
                    'talking_points': [
                        f"We identified ${primary_pain.get('monthly_cost', 0):,.0f}/month loss from {primary_pain.get('category', 'technical')} issues",
                        f"Specific problem: {primary_pain.get('description', 'Performance optimization needed')}",
                        f"Our solution: {primary_pain.get('solution_fit', 'Direct technical optimization')}"
                    ],
                    'expected_outcome': f"${lead.get('annual_opportunity', 0):,.0f} annual opportunity"
                })
        
        # Warm lead nurture actions
        warm_leads = [l for l in leads if l.get('commercial_urgency') == 'warm']
        if warm_leads:
            total_warm_opportunity = sum(l.get('annual_opportunity', 0) for l in warm_leads)
            actions.append({
                'priority': 'HIGH',
                'timeline': 'Next 3-5 days',
                'action': f"Nurture {len(warm_leads)} warm leads",
                'approach': 'Technical audit offer with specific pain point analysis',
                'talking_points': [
                    "Free technical audit focusing on revenue impact",
                    "Benchmark against industry performance standards",
                    "ROI calculation for optimization improvements"
                ],
                'expected_outcome': f"${total_warm_opportunity:,.0f} annual pipeline value"
            })
        
        # Strategic market intelligence action
        pain_categories = {}
        for lead in leads:
            for pain_point in lead.get('pain_points', []):
                category = pain_point.get('category', 'unknown')
                pain_categories[category] = pain_categories.get(category, 0) + 1
        
        if pain_categories:
            top_category = max(pain_categories.items(), key=lambda x: x[1])
            actions.append({
                'priority': 'STRATEGIC',
                'timeline': 'Next 1-2 weeks',
                'action': f"Develop {top_category[0]} specialization",
                'approach': 'Create targeted content and case studies',
                'talking_points': [
                    f"{top_category[0]} optimization is market's #1 pain point",
                    f"{top_category[1]} prospects identified with this issue",
                    "Opportunity to become category specialist"
                ],
                'expected_outcome': 'Market positioning and competitive advantage'
            })
        
        return actions
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
