"""
🎯 PREMIUM LEAD QUALIFICATION PIPELINE
Final refinement for leads with score ≥ 75 and waste ≥ $1,000/month

Focus: PageSpeed analysis + performance loss calculation
Output: 40 hyper-qualified leads ready for outreach
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import httpx
from urllib.parse import urlparse, urljoin
from .revenue_leak_intelligence import LeadProfile, RevenueLakeIntelligenceEngine


@dataclass
class PerformanceMetrics:
    """PageSpeed Insights performance data"""
    lcp_seconds: float
    fcp_seconds: float
    cls_score: float
    js_bytes: int
    css_bytes: int
    image_bytes: int
    total_bytes: int
    performance_score: int


@dataclass
class PerformanceLoss:
    """Calculated performance-based revenue loss"""
    monthly_visitors: int
    current_conversion_rate: float
    benchmark_conversion_rate: float
    average_order_value: float
    monthly_loss_usd: int
    performance_penalty_percent: float


@dataclass
class PremiumLeadProfile:
    """Enhanced lead profile with performance analysis"""
    base_profile: LeadProfile
    performance_metrics: PerformanceMetrics
    performance_loss: PerformanceLoss
    final_score: float
    premium_qualified: bool
    dashboard_url: str
    outreach_priority: int


class PageSpeedAnalyzer:
    """Google PageSpeed Insights API integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = None
        self.base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    
    async def __aenter__(self):
        self.session = httpx.AsyncClient(timeout=30.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def analyze_performance(self, url: str) -> Optional[PerformanceMetrics]:
        """Analyze website performance using PageSpeed Insights"""
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        params = {
            'url': url,
            'key': self.api_key,
            'category': 'performance',
            'strategy': 'mobile',
            'locale': 'en'  # Consistent language
        }
        
        # Retry logic for rate limiting
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await self.session.get(self.base_url, params=params)
                
                # Handle specific status codes
                if response.status_code == 429:  # Rate limited
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"⏱️  Rate limited, waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                
                if response.status_code == 400:
                    print(f"❌ Invalid URL for PageSpeed: {url}")
                    return None
                
                if response.status_code != 200:
                    print(f"❌ PageSpeed API error {response.status_code} for {url}")
                    if attempt == max_retries - 1:
                        return None
                    continue
                
                data = response.json()
                
                # Check for API errors in response
                if 'error' in data:
                    error_msg = data['error'].get('message', 'Unknown error')
                    print(f"❌ PageSpeed API error: {error_msg}")
                    return None
                
                lighthouse_result = data.get('lighthouseResult', {})
                if not lighthouse_result:
                    print(f"❌ No lighthouse data for {url}")
                    return None
                
                audits = lighthouse_result.get('audits', {})
                
                # Extract Core Web Vitals with validation
                lcp_audit = audits.get('largest-contentful-paint', {})
                lcp = lcp_audit.get('numericValue', 0) / 1000 if lcp_audit.get('numericValue') else 0
                
                fcp_audit = audits.get('first-contentful-paint', {})
                fcp = fcp_audit.get('numericValue', 0) / 1000 if fcp_audit.get('numericValue') else 0
                
                cls_audit = audits.get('cumulative-layout-shift', {})
                cls = cls_audit.get('numericValue', 0) if cls_audit.get('numericValue') else 0
                
                # Extract resource sizes with validation
                resource_summary = audits.get('resource-summary', {}).get('details', {}).get('items', [])
                js_bytes = 0
                css_bytes = 0
                image_bytes = 0
                total_bytes = 0
                
                for resource in resource_summary:
                    resource_type = resource.get('resourceType', '')
                    transfer_size = resource.get('transferSize', 0)
                    
                    if resource_type == 'script':
                        js_bytes += transfer_size
                    elif resource_type == 'stylesheet':
                        css_bytes += transfer_size
                    elif resource_type == 'image':
                        image_bytes += transfer_size
                    
                    total_bytes += transfer_size
                
                # Performance score validation
                performance_category = lighthouse_result.get('categories', {}).get('performance', {})
                performance_score = performance_category.get('score', 0)
                if performance_score is not None:
                    performance_score = int(performance_score * 100)
                else:
                    performance_score = 0
                
                # Validate critical metrics
                if lcp == 0 and fcp == 0:
                    print(f"⚠️  No performance metrics for {url}")
                    return None
                
                return PerformanceMetrics(
                    lcp_seconds=round(lcp, 2),
                    fcp_seconds=round(fcp, 2),
                    cls_score=round(cls, 3),
                    js_bytes=js_bytes,
                    css_bytes=css_bytes,
                    image_bytes=image_bytes,
                    total_bytes=total_bytes,
                    performance_score=performance_score
                )
                
            except asyncio.TimeoutError:
                print(f"⏱️  Timeout for {url}, attempt {attempt + 1}")
                if attempt == max_retries - 1:
                    return None
                await asyncio.sleep(1)
                continue
                
            except Exception as e:
                print(f"❌ Unexpected error analyzing {url}: {e}")
                if attempt == max_retries - 1:
                    return None
                await asyncio.sleep(1)
                continue
        
        return None


class PerformanceLossCalculator:
    """Calculate revenue loss from poor performance"""
    
    def __init__(self):
        # Industry benchmarks
        self.benchmarks = {
            'conversion_rate_baseline': 2.8,  # E-commerce baseline %
            'lcp_benchmark': 2.5,  # Seconds
            'performance_score_benchmark': 85,
            'conversion_loss_per_second': 7.0,  # % loss per second of LCP delay
            'js_weight_threshold': 900000,  # 900KB threshold from playbook
        }
    
    def calculate_performance_loss(self, profile: LeadProfile, 
                                 metrics: PerformanceMetrics) -> PerformanceLoss:
        """Calculate monthly revenue loss from performance issues"""
        
        # Estimate monthly visitors based on revenue
        estimated_monthly_visitors = profile.revenue_proxy.est_monthly_revenue / 50  # $50 AOV estimate
        
        # Calculate performance penalty
        lcp_delay = max(0, metrics.lcp_seconds - self.benchmarks['lcp_benchmark'])
        js_weight_penalty = 0
        
        if metrics.js_bytes > self.benchmarks['js_weight_threshold']:
            js_weight_penalty = 7  # 7% loss from playbook
        
        # Total performance penalty
        lcp_penalty = lcp_delay * self.benchmarks['conversion_loss_per_second']
        total_penalty_percent = min(50, lcp_penalty + js_weight_penalty)  # Cap at 50%
        
        # Current vs benchmark conversion rates
        current_conversion_rate = self.benchmarks['conversion_rate_baseline'] * (1 - total_penalty_percent / 100)
        benchmark_conversion_rate = self.benchmarks['conversion_rate_baseline']
        
        # Calculate loss
        current_revenue = estimated_monthly_visitors * current_conversion_rate / 100 * profile.revenue_proxy.median_price
        potential_revenue = estimated_monthly_visitors * benchmark_conversion_rate / 100 * profile.revenue_proxy.median_price
        
        monthly_loss = int(potential_revenue - current_revenue)
        
        return PerformanceLoss(
            monthly_visitors=int(estimated_monthly_visitors),
            current_conversion_rate=round(current_conversion_rate, 1),
            benchmark_conversion_rate=benchmark_conversion_rate,
            average_order_value=profile.revenue_proxy.median_price,
            monthly_loss_usd=max(0, monthly_loss),
            performance_penalty_percent=round(total_penalty_percent, 1)
        )


class PremiumQualificationEngine:
    """Final qualification engine for premium leads"""
    
    def __init__(self, pagespeed_api_key: str):
        self.pagespeed_api_key = pagespeed_api_key
        self.performance_calculator = PerformanceLossCalculator()
        self.qualified_leads = []
    
    async def refine_leads(self, pre_qualified_leads: List[LeadProfile]) -> List[PremiumLeadProfile]:
        """Refine pre-qualified leads with PageSpeed analysis"""
        
        print(f"🔬 Refining {len(pre_qualified_leads)} pre-qualified leads...")
        
        premium_leads = []
        
        async with PageSpeedAnalyzer(self.pagespeed_api_key) as analyzer:
            for lead in pre_qualified_leads:
                print(f"   📊 Analyzing performance: {lead.domain}")
                
                # Get performance metrics
                url = f"https://{lead.domain}"
                metrics = await analyzer.analyze_performance(url)
                
                if not metrics:
                    continue
                
                # Calculate performance loss
                perf_loss = self.performance_calculator.calculate_performance_loss(lead, metrics)
                
                # Calculate final score
                final_score = self._calculate_final_score(lead, metrics, perf_loss)
                
                # Check premium qualification
                total_waste = lead.total_monthly_waste + perf_loss.monthly_loss_usd
                premium_qualified = final_score >= 75 and total_waste >= 1000
                
                if premium_qualified:
                    premium_profile = PremiumLeadProfile(
                        base_profile=lead,
                        performance_metrics=metrics,
                        performance_loss=perf_loss,
                        final_score=final_score,
                        premium_qualified=True,
                        dashboard_url=self._generate_dashboard_url(lead),
                        outreach_priority=self._calculate_priority(final_score, total_waste)
                    )
                    
                    premium_leads.append(premium_profile)
                    print(f"   ✅ QUALIFIED: {lead.domain} (Score: {final_score}, Waste: ${total_waste}/mo)")
                else:
                    print(f"   ❌ Not qualified: {lead.domain} (Score: {final_score}, Waste: ${total_waste}/mo)")
                
                # Rate limiting for PageSpeed API
                await asyncio.sleep(1.0)
        
        # Sort by priority
        premium_leads.sort(key=lambda x: x.outreach_priority, reverse=True)
        
        return premium_leads
    
    def _calculate_final_score(self, lead: LeadProfile, metrics: PerformanceMetrics, 
                             perf_loss: PerformanceLoss) -> float:
        """Calculate final qualification score"""
        base_score = lead.pre_psi_score
        
        # Performance loss bonus (higher loss = higher score)
        perf_bonus = min(25, perf_loss.monthly_loss_usd / 100)  # $100 loss = 1 point
        
        # JS weight penalty bonus
        js_bonus = 15 if metrics.js_bytes > 900000 else 0  # From playbook threshold
        
        # LCP penalty bonus
        lcp_bonus = max(0, (metrics.lcp_seconds - 2.5) * 5)  # 5 points per second over 2.5s
        
        final_score = base_score + perf_bonus + js_bonus + lcp_bonus
        
        return round(min(100, final_score), 1)
    
    def _calculate_priority(self, score: float, total_waste: int) -> int:
        """Calculate outreach priority (1-10, 10 = highest)"""
        # Weight: 60% waste amount, 40% score
        waste_score = min(10, total_waste / 500)  # $500 waste = 1 priority point
        score_normalized = score / 10
        
        priority = (waste_score * 0.6) + (score_normalized * 0.4)
        return round(priority)
    
    def _generate_dashboard_url(self, lead: LeadProfile) -> str:
        """Generate Looker Studio dashboard URL"""
        # This would generate a real dashboard URL in production
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"https://lookerstudio.google.com/arco-dashboard/{lead.domain.replace('.', '-')}-{timestamp}"


class DashboardGenerator:
    """Generate comprehensive dashboards for qualified leads"""
    
    def generate_lead_dashboard(self, premium_lead: PremiumLeadProfile) -> Dict:
        """Generate complete dashboard data for lead"""
        base = premium_lead.base_profile
        metrics = premium_lead.performance_metrics
        perf_loss = premium_lead.performance_loss
        
        # SaaS leaks summary
        saas_leaks = [
            {
                'tool': leak.footprint.split('.')[0].title(),
                'monthly_cost': f"US$ {leak.monthly_cost}/mo",
                'replacement': leak.replacement
            }
            for leak in base.detected_leaks
        ]
        
        # Performance issues
        performance_issues = []
        if metrics.lcp_seconds > 2.5:
            performance_issues.append(f"LCP slow: {metrics.lcp_seconds:.1f}s (target: <2.5s)")
        if metrics.js_bytes > 900000:
            performance_issues.append(f"JS weight: {metrics.js_bytes/1000:.0f}KB (target: <900KB)")
        if metrics.performance_score < 85:
            performance_issues.append(f"Performance score: {metrics.performance_score} (target: >85)")
        
        # ROAS issues
        roas_issues = []
        if base.roas_flag.is_high_spend:
            roas_issues.append(f"High ad spend with {base.roas_flag.conversion_rate}% conversion (benchmark: 2.8%)")
        
        total_waste = base.total_monthly_waste + perf_loss.monthly_loss_usd
        
        dashboard = {
            'brand': base.domain,
            'brand_name': base.brand_name,
            'revenue_proxy': f"US$ {base.revenue_proxy.est_monthly_revenue:,}/mo",
            'confidence': base.revenue_proxy.confidence,
            
            'waste_breakdown': {
                'saas_leaks': saas_leaks,
                'saas_total': f"US$ {base.total_monthly_waste}/mo",
                'performance_loss': f"US$ {perf_loss.monthly_loss_usd}/mo",
                'performance_details': performance_issues,
                'roas_issues': roas_issues,
                'total_waste': f"US$ {total_waste:,}/month"
            },
            
            'arco_opportunity': {
                'total_savings': f"US$ {total_waste}/mo",
                'arco_fee_25_percent': f"US$ {int(total_waste * 0.25)}/mo",
                'annual_client_savings': f"US$ {int(total_waste * 0.75 * 12):,}/year",
                'roi_multiple': f"{total_waste / max(1, int(total_waste * 0.25)):.1f}x"
            },
            
            'technical_metrics': {
                'lcp_seconds': metrics.lcp_seconds,
                'performance_score': metrics.performance_score,
                'js_bytes': metrics.js_bytes,
                'total_bytes': metrics.total_bytes,
                'estimated_visitors': f"{perf_loss.monthly_visitors:,}/mo"
            },
            
            'qualification': {
                'final_score': premium_lead.final_score,
                'premium_qualified': premium_lead.premium_qualified,
                'outreach_priority': premium_lead.outreach_priority,
                'dashboard_url': premium_lead.dashboard_url
            }
        }
        
        return dashboard


class ArcoRevenueLakeEngine:
    """Complete ARCO Revenue Leak Detection Engine"""
    
    def __init__(self, pagespeed_api_key: str):
        self.base_engine = RevenueLakeIntelligenceEngine()
        self.premium_engine = PremiumQualificationEngine(pagespeed_api_key)
        self.dashboard_generator = DashboardGenerator()
    
    async def process_domains_to_qualified_leads(self, domains: List[str]) -> Dict:
        """Complete pipeline: domains → qualified leads with dashboards"""
        
        print("🎯 ARCO REVENUE LEAK PIPELINE")
        print("=" * 50)
        
        # Phase 1: Pre-qualification (leak scan + revenue proxy)
        print("\n📊 Phase 1: Pre-qualification scan...")
        pre_qualified = await self.base_engine.process_domain_list(domains, max_concurrent=5)
        
        print(f"   ✅ Pre-qualified: {len(pre_qualified)} leads (score ≥ 40)")
        
        # Phase 2: Premium qualification (PageSpeed + final scoring)
        print("\n🔬 Phase 2: Premium qualification...")
        premium_leads = await self.premium_engine.refine_leads(pre_qualified)
        
        print(f"   ✅ Premium qualified: {len(premium_leads)} leads (score ≥ 75, waste ≥ $1K)")
        
        # Phase 3: Dashboard generation
        print("\n📋 Phase 3: Dashboard generation...")
        dashboards = []
        for lead in premium_leads:
            dashboard = self.dashboard_generator.generate_lead_dashboard(lead)
            dashboards.append(dashboard)
        
        # Final results
        results = {
            'pipeline_summary': {
                'domains_processed': len(domains),
                'pre_qualified': len(pre_qualified),
                'premium_qualified': len(premium_leads),
                'qualification_rate': f"{len(premium_leads)/len(domains)*100:.1f}%",
                'total_waste_detected': sum(
                    lead.base_profile.total_monthly_waste + lead.performance_loss.monthly_loss_usd
                    for lead in premium_leads
                ),
                'avg_waste_per_lead': sum(
                    lead.base_profile.total_monthly_waste + lead.performance_loss.monthly_loss_usd
                    for lead in premium_leads
                ) // max(1, len(premium_leads))
            },
            'qualified_leads': dashboards,
            'processing_stats': self.base_engine.stats,
            'timestamp': datetime.now().isoformat()
        }
        
        return results


# Export results
def export_qualified_leads(results: Dict, filename: str = None) -> str:
    """Export qualified leads to JSON file"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"qualified_leads_{timestamp}.json"
    
    filepath = os.path.join('output', filename)
    os.makedirs('output', exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results exported to: {filepath}")
    return filepath


# Demo usage - REMOVED  
async def demo_premium_qualification():
    """Demo removed - use real data only"""
    print("❌ Use real domains with revenue_leak_attack.py")

if __name__ == "__main__":
    print("🎯 Use revenue_leak_attack.py for real execution")
