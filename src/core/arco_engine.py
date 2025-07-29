# src/core/arco_engine.py

from src.core.http_client import HTTPClient
from src.core.cache import Cache
from src.config.arco_config_manager import ARCOConfigManager
from src.utils.logger import logger
from src.connectors.google_pagespeed_api import GooglePageSpeedAPI
from src.connectors.google_ads_api import GoogleAdsAPI
from src.connectors.meta_business_api import MetaBusinessAPI
from src.analysis.missed_opportunity_detector import MissedOpportunityDetector

class ARCOEngine:
    """
    O motor principal do Arco-Find, responsável por orquestrar a coleta de dados,
    análise e identificação de oportunidades de otimização.
    """
    def __init__(self):
        self.http_client = HTTPClient()
        self.cache = Cache()
        self.config = ARCOConfigManager().get_config()
        
        # Initialize APIs only if keys are available
        try:
            self.pagespeed_api = GooglePageSpeedAPI() if self.config.api_keys.google_pagespeed else None
        except ValueError:
            logger.warning("Google PageSpeed API not available - API key missing")
            self.pagespeed_api = None
            
        try:
            self.google_ads_api = GoogleAdsAPI() if self.config.api_keys.google_ads else None
        except (ValueError, Exception):
            logger.warning("Google Ads API not available - API key missing or invalid")
            self.google_ads_api = None
            
        try:
            self.meta_business_api = MetaBusinessAPI() if self.config.api_keys.meta_business else None
        except (ValueError, Exception):
            logger.warning("Meta Business API not available - API key missing or invalid")
            self.meta_business_api = None
            
        self.missed_opportunity_detector = MissedOpportunityDetector()
        logger.info(f"ARCOEngine initialized with environment: {self.config.environment}")
        
        # Log available services
        available_services = []
        if self.pagespeed_api: available_services.append("PageSpeed")
        if self.google_ads_api: available_services.append("Google Ads")
        if self.meta_business_api: available_services.append("Meta Business")
        
        logger.info(f"Available API services: {', '.join(available_services) if available_services else 'None (demo mode)'}")

    def analyze_saas_costs(self, company_data):
        """
        Analisa os custos de SaaS com base nos dados da empresa.
        Fornece insights específicos e acionáveis para otimização de custos.
        """
        logger.info(f"ARCOEngine: Analyzing SaaS costs for {company_data.get('name')}")
        
        saas_spend = company_data.get('saas_spend', 0)
        company_size = company_data.get('employee_count', 50)  # Default assumption
        
        # Calculate realistic savings based on company profile
        if saas_spend == 0:
            # Estimate based on company size if no data provided
            estimated_saas_spend = self._estimate_saas_spend_by_size(company_size)
            potential_savings = estimated_saas_spend * 0.15  # Conservative 15%
            confidence = "estimated"
        else:
            potential_savings = min(saas_spend * 0.25, saas_spend * 0.35 if saas_spend > 10000 else saas_spend * 0.20)
            confidence = "calculated"
        
        # Generate specific, actionable recommendations
        recommendations = []
        savings_breakdown = {}
        
        if potential_savings > 500:  # Lowered threshold from 2000
            if potential_savings > 2000:
                recommendations.extend([
                    "Audit immediate: Identificar usuários inativos em ferramentas pagas (savings típico: 20-30%)",
                    "Consolidação de tools: Substituir 3-4 ferramentas por 1-2 soluções integradas",
                    "Renegociação anual: Leverage renewal periods para discounts (5-15% típico)",
                    "Downgrade analysis: Review feature usage vs plan costs"
                ])
                savings_breakdown = {
                    "unused_licenses": potential_savings * 0.4,
                    "tool_consolidation": potential_savings * 0.35,
                    "plan_optimization": potential_savings * 0.25
                }
            else:
                recommendations.extend([
                    "License utilization review: Identify inactive users and downgrade",
                    "Annual vs monthly billing switch (typical 10-20% savings)",
                    "Feature audit: Ensure you're not paying for unused premium features"
                ])
                savings_breakdown = {
                    "license_optimization": potential_savings * 0.6,
                    "billing_optimization": potential_savings * 0.4
                }
        else:
            # Always provide at least basic recommendations
            recommendations.extend([
                "Basic SaaS review: Check for duplicate tools and unused subscriptions",
                "Consider annual billing for active tools (typical 10-15% discount)",
                "Monitor usage monthly to prevent overprovisioning"
            ])
            savings_breakdown = {
                "basic_optimization": potential_savings
            }
        
        return {
            "category": "SaaS Cost Optimization",
            "potential_monthly_savings": potential_savings,
            "annual_savings_potential": potential_savings * 12,
            "confidence_level": confidence,
            "details": f"Analysis based on {confidence} spend of ${saas_spend:,.0f}/month. Conservative savings estimate.",
            "savings_breakdown": savings_breakdown,
            "recommendations": recommendations,
            "implementation_timeline": "2-4 weeks",
            "roi_timeline": "immediate"
        }

    def _estimate_saas_spend_by_size(self, employee_count):
        """Estimate SaaS spend based on company size"""
        if employee_count < 10:
            return 2000  # Small team basics
        elif employee_count < 25:
            return 5000  # Growing company
        elif employee_count < 50:
            return 8000  # Mid-size
        elif employee_count < 100:
            return 15000  # Large team
        else:
            return 25000  # Enterprise

    def analyze_website_performance(self, website_url):
        """
        Analisa a performance de website usando a Google PageSpeed Insights API.
        Fornece insights específicos e acionáveis para melhoria de performance.
        """
        logger.info(f"ARCOEngine: Analyzing website performance for {website_url}")
        
        if not self.pagespeed_api:
            logger.warning("PageSpeed API not available - providing estimated analysis")
            return self._provide_estimated_performance_analysis(website_url)
        
        pagespeed_results = self.pagespeed_api.get_page_speed_score(website_url, strategy="mobile")

        if pagespeed_results and pagespeed_results.get("score") is not None:
            performance_score = pagespeed_results["score"]
            
            # Generate business impact analysis
            impact_analysis = self._calculate_performance_business_impact(performance_score)
            
            # Specific recommendations based on score
            recommendations = self._get_performance_recommendations(performance_score)
            
            return {
                "category": "Website Performance Improvement",
                "performance_score": performance_score,
                "business_impact": impact_analysis,
                "details": f"PageSpeed Mobile Score: {performance_score}/100. {impact_analysis['impact_description']}",
                "recommendations": recommendations,
                "full_results": pagespeed_results,
                "implementation_priority": impact_analysis['priority']
            }
        else:
            logger.error(f"Não foi possível obter o score de performance para {website_url}: {pagespeed_results.get('error', 'Erro desconhecido')}")
            return self._provide_estimated_performance_analysis(website_url, error=pagespeed_results.get('error'))

    def _provide_estimated_performance_analysis(self, website_url, error=None):
        """Provide estimated performance analysis when API is not available"""
        estimated_score = 65  # Conservative estimate for typical websites
        impact_analysis = self._calculate_performance_business_impact(estimated_score)
        recommendations = self._get_performance_recommendations(estimated_score)
        
        details = f"Estimated performance analysis (PageSpeed API not available). "
        if error:
            details += f"API Error: {error}. "
        details += "Recommendations based on common performance issues."
        
        return {
            "category": "Website Performance Improvement",
            "performance_score": estimated_score,
            "business_impact": impact_analysis,
            "details": details,
            "recommendations": recommendations + [
                "Note: Get Google PageSpeed API key for detailed performance analysis",
                "Manual performance audit recommended for accurate insights"
            ],
            "implementation_priority": "medium",
            "data_source": "estimated"
        }

    def _calculate_performance_business_impact(self, score):
        """Calculate business impact of website performance"""
        if score >= 90:
            return {
                "impact_description": "Excellent performance - minimal revenue impact",
                "conversion_impact": "0-2%",
                "revenue_impact": "minimal",
                "priority": "low"
            }
        elif score >= 70:
            return {
                "impact_description": "Good performance with minor optimization opportunities",
                "conversion_impact": "3-8%",
                "revenue_impact": "low",
                "priority": "medium"
            }
        elif score >= 50:
            return {
                "impact_description": "Moderate performance issues affecting user experience",
                "conversion_impact": "10-20%",
                "revenue_impact": "moderate",
                "priority": "high"
            }
        else:
            return {
                "impact_description": "Critical performance issues causing significant revenue leakage",
                "conversion_impact": "25-40%",
                "revenue_impact": "critical",
                "priority": "critical"
            }

    def _get_performance_recommendations(self, score):
        """Get specific recommendations based on performance score"""
        if score >= 90:
            return [
                "Monitor Core Web Vitals monthly to maintain performance",
                "Consider advanced optimizations like service workers",
                "Benchmark against competitors quarterly"
            ]
        elif score >= 70:
            return [
                "Optimize largest contentful paint (LCP) - target under 2.5s",
                "Review and compress images - WebP format implementation", 
                "Minimize unused JavaScript and CSS",
                "Implement browser caching strategies"
            ]
        elif score >= 50:
            return [
                "PRIORITY: Fix Core Web Vitals - LCP, FID, CLS",
                "Implement lazy loading for images and videos",
                "Optimize server response time - consider CDN",
                "Remove render-blocking resources",
                "Compress and minify all assets"
            ]
        else:
            return [
                "CRITICAL: Complete performance overhaul needed",
                "Server optimization - upgrade hosting if needed",
                "Image optimization - compress all images by 70-80%",
                "Remove unnecessary plugins and scripts",
                "Implement aggressive caching strategy",
                "Consider website rebuild with performance-first approach"
            ]

    def analyze_ad_performance(self, customer_id: str, campaign_id: str = None):
        """
        Analisa a performance de anúncios usando a Google Ads API.
        Fornece insights específicos e acionáveis sobre otimização de campanhas.
        """
        logger.info(f"ARCOEngine: Analyzing ad performance for customer_id: {customer_id}, campaign_id: {campaign_id}")
        
        if not self.google_ads_api:
            logger.warning("Google Ads API not available - providing estimated analysis")
            return self._provide_estimated_google_ads_analysis(customer_id)
        
        ad_performance_data = self.google_ads_api.get_campaign_performance(customer_id, campaign_id)

        # Calculate efficiency metrics and industry benchmarks
        efficiency_analysis = self._analyze_ad_efficiency(ad_performance_data)
        
        # Generate specific, actionable recommendations
        recommendations = self._generate_ad_recommendations(ad_performance_data, efficiency_analysis)
        
        # Calculate potential savings/improvements
        optimization_potential = self._calculate_ad_optimization_potential(ad_performance_data)

        return {
            "category": "Ad Performance Optimization",
            "ad_metrics": ad_performance_data,
            "efficiency_analysis": efficiency_analysis,
            "optimization_potential": optimization_potential,
            "recommendations": recommendations,
            "details": f"Ad Analysis: Spend=${ad_performance_data.get('cost', 0):,.0f}, CPA=${ad_performance_data.get('cpa', 0):.2f}, ROAS={efficiency_analysis.get('roas', 0):.2f}x"
        }

    def analyze_meta_ad_performance(self, ad_account_id: str):
        """
        Analisa a performance de anúncios usando a Meta Business API.
        Fornece insights específicos e acionáveis sobre otimização de campanhas Meta.
        """
        logger.info(f"ARCOEngine: Analyzing Meta ad performance for ad_account_id: {ad_account_id}")
        
        if not self.meta_business_api:
            logger.warning("Meta Business API not available - providing estimated analysis")
            return self._provide_estimated_meta_ads_analysis(ad_account_id)
        
        meta_ad_performance_data = self.meta_business_api.get_ad_account_performance(ad_account_id)

        # Calculate efficiency metrics and industry benchmarks
        efficiency_analysis = self._analyze_meta_ad_efficiency(meta_ad_performance_data)
        
        # Generate specific, actionable recommendations
        recommendations = self._generate_meta_ad_recommendations(meta_ad_performance_data, efficiency_analysis)
        
        # Calculate potential improvements
        optimization_potential = self._calculate_meta_optimization_potential(meta_ad_performance_data)

        return {
            "category": "Meta Ad Performance Optimization",
            "ad_metrics": meta_ad_performance_data,
            "efficiency_analysis": efficiency_analysis,
            "optimization_potential": optimization_potential,
            "recommendations": recommendations,
            "details": f"Meta Analysis: Spend=${meta_ad_performance_data.get('spend', 0):,.0f}, CPA=${meta_ad_performance_data.get('cpa', 0):.2f}, CTR={efficiency_analysis.get('ctr', 0):.2f}%"
        }

    def _provide_estimated_google_ads_analysis(self, customer_id):
        """Provide estimated Google Ads analysis when API is not available"""
        # Realistic estimates for demo purposes
        estimated_data = {
            'cost': 8000,
            'clicks': 800,
            'conversions': 40,
            'revenue': 16000,
            'cpa': 200
        }
        
        efficiency_analysis = self._analyze_ad_efficiency(estimated_data)
        recommendations = self._generate_ad_recommendations(estimated_data, efficiency_analysis)
        optimization_potential = self._calculate_ad_optimization_potential(estimated_data)
        
        recommendations.append("Note: Connect Google Ads API for real-time campaign data")
        
        return {
            "category": "Ad Performance Optimization",
            "ad_metrics": estimated_data,
            "efficiency_analysis": efficiency_analysis,
            "optimization_potential": optimization_potential,
            "recommendations": recommendations,
            "details": f"Estimated Ad Analysis (API not connected): Spend=${estimated_data['cost']:,.0f}, CPA=${estimated_data['cpa']:.2f}",
            "data_source": "estimated"
        }

    def _provide_estimated_meta_ads_analysis(self, ad_account_id):
        """Provide estimated Meta Ads analysis when API is not available"""
        # Realistic estimates for demo purposes
        estimated_data = {
            'spend': 6000,
            'clicks': 1200,
            'conversions': 60,
            'impressions': 120000,
            'cpa': 100
        }
        
        efficiency_analysis = self._analyze_meta_ad_efficiency(estimated_data)
        recommendations = self._generate_meta_ad_recommendations(estimated_data, efficiency_analysis)
        optimization_potential = self._calculate_meta_optimization_potential(estimated_data)
        
        recommendations.append("Note: Connect Meta Business API for real-time campaign data")
        
        return {
            "category": "Meta Ad Performance Optimization",
            "ad_metrics": estimated_data,
            "efficiency_analysis": efficiency_analysis,
            "optimization_potential": optimization_potential,
            "recommendations": recommendations,
            "details": f"Estimated Meta Analysis (API not connected): Spend=${estimated_data['spend']:,.0f}, CPA=${estimated_data['cpa']:.2f}",
            "data_source": "estimated"
        }

    def _analyze_ad_efficiency(self, ad_data):
        """Analyze Google Ads efficiency metrics"""
        cost = ad_data.get('cost', 0)
        clicks = ad_data.get('clicks', 1)
        conversions = ad_data.get('conversions', 0)
        revenue = ad_data.get('revenue', 0)
        
        cpa = cost / max(conversions, 1)
        cpc = cost / max(clicks, 1)
        conversion_rate = (conversions / max(clicks, 1)) * 100
        roas = revenue / max(cost, 1)
        
        # Industry benchmark comparison
        return {
            "cpa": cpa,
            "cpc": cpc,
            "conversion_rate": conversion_rate,
            "roas": roas,
            "efficiency_grade": self._get_efficiency_grade(cpa, conversion_rate, roas)
        }

    def _analyze_meta_ad_efficiency(self, meta_data):
        """Analyze Meta Ads efficiency metrics"""
        spend = meta_data.get('spend', 0)
        clicks = meta_data.get('clicks', 1)
        conversions = meta_data.get('conversions', 0)
        impressions = meta_data.get('impressions', 1)
        
        cpa = spend / max(conversions, 1)
        cpc = spend / max(clicks, 1)
        ctr = (clicks / max(impressions, 1)) * 100
        conversion_rate = (conversions / max(clicks, 1)) * 100
        
        return {
            "cpa": cpa,
            "cpc": cpc,
            "ctr": ctr,
            "conversion_rate": conversion_rate,
            "efficiency_grade": self._get_meta_efficiency_grade(cpa, ctr, conversion_rate)
        }

    def _get_efficiency_grade(self, cpa, conversion_rate, roas):
        """Grade Google Ads efficiency"""
        if cpa < 50 and conversion_rate > 8 and roas > 4:
            return "A - Excellent"
        elif cpa < 100 and conversion_rate > 5 and roas > 2:
            return "B - Good"
        elif cpa < 150 and conversion_rate > 3:
            return "C - Average"
        else:
            return "D - Needs Improvement"

    def _get_meta_efficiency_grade(self, cpa, ctr, conversion_rate):
        """Grade Meta Ads efficiency"""
        if cpa < 40 and ctr > 2 and conversion_rate > 6:
            return "A - Excellent"
        elif cpa < 80 and ctr > 1.5 and conversion_rate > 4:
            return "B - Good"
        elif cpa < 120 and ctr > 1:
            return "C - Average"
        else:
            return "D - Needs Improvement"

    def _generate_ad_recommendations(self, ad_data, efficiency_analysis):
        """Generate specific Google Ads recommendations"""
        recommendations = []
        cpa = efficiency_analysis['cpa']
        conversion_rate = efficiency_analysis['conversion_rate']
        roas = efficiency_analysis['roas']
        
        if cpa > 100:
            recommendations.extend([
                f"HIGH PRIORITY: CPA ${cpa:.0f} - Pause bottom 20% performing keywords",
                "Implement negative keyword strategy to reduce wasted spend",
                "Optimize landing page relevance - ensure message match with ads"
            ])
        
        if conversion_rate < 3:
            recommendations.extend([
                f"Conversion rate {conversion_rate:.1f}% is below benchmark - Landing page optimization needed",
                "A/B test different call-to-action buttons and forms",
                "Review traffic quality - adjust audience targeting"
            ])
        
        if roas < 2:
            recommendations.extend([
                f"ROAS {roas:.1f}x is unprofitable - Immediate campaign review needed",
                "Focus budget on top-performing campaigns only",
                "Consider pausing underperforming ad groups"
            ])
        
        return recommendations

    def _generate_meta_ad_recommendations(self, meta_data, efficiency_analysis):
        """Generate specific Meta Ads recommendations"""
        recommendations = []
        cpa = efficiency_analysis['cpa']
        ctr = efficiency_analysis['ctr']
        conversion_rate = efficiency_analysis['conversion_rate']
        
        if cpa > 50:
            recommendations.extend([
                f"HIGH PRIORITY: Meta CPA ${cpa:.0f} - Optimize audience targeting",
                "Test different creative formats (video vs image vs carousel)",
                "Implement lookalike audiences based on best customers"
            ])
        
        if ctr < 1.5:
            recommendations.extend([
                f"CTR {ctr:.2f}% indicates poor ad relevance - Creative refresh needed",
                "Test different ad copy angles and value propositions",
                "Update visuals to be more engaging and scroll-stopping"
            ])
        
        if conversion_rate < 4:
            recommendations.extend([
                f"Conversion rate {conversion_rate:.1f}% suggests traffic-landing page mismatch",
                "Create dedicated landing pages for Meta traffic",
                "Implement Facebook Pixel for better conversion tracking"
            ])
        
        return recommendations

    def _calculate_ad_optimization_potential(self, ad_data):
        """Calculate potential improvements for Google Ads"""
        current_cost = ad_data.get('cost', 0)
        current_conversions = ad_data.get('conversions', 0)
        
        # Conservative estimates based on typical optimization results
        potential_cpa_reduction = 0.20  # 20% improvement typical
        potential_conversion_increase = 0.15  # 15% more conversions
        
        return {
            "monthly_savings_potential": current_cost * potential_cpa_reduction,
            "conversion_increase_potential": current_conversions * potential_conversion_increase,
            "timeline": "4-6 weeks",
            "confidence": "medium"
        }

    def _calculate_meta_optimization_potential(self, meta_data):
        """Calculate potential improvements for Meta Ads"""
        current_spend = meta_data.get('spend', 0)
        current_conversions = meta_data.get('conversions', 0)
        
        # Conservative estimates
        potential_efficiency_gain = 0.25  # 25% efficiency improvement typical for Meta
        
        return {
            "monthly_savings_potential": current_spend * 0.18,
            "conversion_increase_potential": current_conversions * potential_efficiency_gain,
            "timeline": "3-5 weeks",
            "confidence": "medium"
        }

    def generate_optimization_insights(self, company_name, website_url, saas_spend=0, employee_count=50, industry="general", google_ads_customer_id: str = None, google_ads_campaign_id: str = None, meta_ad_account_id: str = None):
        """
        Gera insights de otimização específicos e acionáveis para uma empresa.
        """
        logger.info(f"ARCOEngine: Generating optimization insights for {company_name} in {industry} industry")
        company_data = {
            "name": company_name,
            "website": website_url,
            "saas_spend": saas_spend,
            "employee_count": employee_count,
            "industry": industry
        }

        insights = []
        missed_opportunities = []
        
        # SaaS cost analysis
        saas_insights = self.analyze_saas_costs(company_data)
        insights.append(saas_insights)
        
        # Website performance analysis
        performance_insights = self.analyze_website_performance(company_data['website'])
        insights.append(performance_insights)
        
        # Ad performance analysis if provided
        if google_ads_customer_id:
            google_ads_insights = self.analyze_ad_performance(google_ads_customer_id, google_ads_campaign_id)
            insights.append(google_ads_insights)
        
        if meta_ad_account_id:
            meta_insights = self.analyze_meta_ad_performance(meta_ad_account_id)
            insights.append(meta_insights)

        # Generate missed opportunities with industry context
        missed_opportunities = self.missed_opportunity_detector.detect_opportunities(insights, industry)
        
        # Calculate overall business impact
        business_impact = self._calculate_overall_business_impact(insights)
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(company_name, insights, missed_opportunities, business_impact)

        return {
            "company": company_name,
            "industry": industry,
            "analysis_timestamp": logger.info("Analysis completed"),
            "executive_summary": executive_summary,
            "business_impact": business_impact,
            "insights": insights,
            "missed_opportunities": missed_opportunities,
            "next_steps": self._generate_next_steps(missed_opportunities)
        }

    def _calculate_overall_business_impact(self, insights):
        """Calculate overall business impact across all insights"""
        total_monthly_savings = 0
        total_revenue_impact = 0
        critical_issues = 0
        
        for insight in insights:
            if insight["category"] == "SaaS Cost Optimization":
                total_monthly_savings += insight.get("potential_monthly_savings", 0)
            elif insight["category"] == "Website Performance Improvement":
                if insight.get("business_impact", {}).get("priority") == "critical":
                    critical_issues += 1
                    total_revenue_impact += 0.25  # 25% revenue impact for critical performance
            elif "Ad" in insight["category"]:
                optimization_potential = insight.get("optimization_potential", {})
                total_monthly_savings += optimization_potential.get("monthly_savings_potential", 0)
        
        return {
            "total_monthly_savings_potential": total_monthly_savings,
            "annual_savings_potential": total_monthly_savings * 12,
            "estimated_revenue_impact": total_revenue_impact,
            "critical_issues_count": critical_issues,
            "overall_health_score": max(1, 10 - critical_issues * 2 - (total_monthly_savings / 1000))
        }

    def _generate_executive_summary(self, company_name, insights, opportunities, business_impact):
        """Generate executive summary for leadership"""
        summary = f"## Executive Summary - {company_name}\n\n"
        
        # Key metrics
        annual_savings = business_impact["annual_savings_potential"]
        health_score = business_impact["overall_health_score"]
        
        summary += f"**Annual Savings Opportunity:** ${annual_savings:,.0f}\n"
        summary += f"**Digital Health Score:** {health_score:.1f}/10\n"
        summary += f"**Priority Issues:** {len([opp for opp in opportunities if opp.get('priority') == 'critical'])}\n\n"
        
        # Top 3 opportunities
        top_opportunities = sorted(opportunities, key=lambda x: {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}.get(x.get('priority', 'low'), 1), reverse=True)[:3]
        
        summary += "**Top 3 Opportunities:**\n"
        for i, opp in enumerate(top_opportunities, 1):
            summary += f"{i}. {opp['type']} - {opp.get('roi_estimate', 'High ROI potential')}\n"
        
        return summary

    def _generate_next_steps(self, opportunities):
        """Generate prioritized next steps"""
        next_steps = []
        
        # Group by priority
        critical = [opp for opp in opportunities if opp.get('priority') == 'critical']
        high = [opp for opp in opportunities if opp.get('priority') == 'high']
        medium = [opp for opp in opportunities if opp.get('priority') == 'medium']
        
        if critical:
            next_steps.append({
                "phase": "Immediate (Week 1-2)",
                "actions": [opp['action'] for opp in critical[:2]],
                "expected_impact": "Critical revenue leakage mitigation"
            })
        
        if high:
            next_steps.append({
                "phase": "Short-term (Week 3-6)",
                "actions": [opp['action'] for opp in high[:3]],
                "expected_impact": "Significant efficiency gains"
            })
        
        if medium:
            next_steps.append({
                "phase": "Medium-term (Month 2-3)",
                "actions": [opp['action'] for opp in medium[:2]],
                "expected_impact": "Optimization and scaling"
            })
        
        return next_steps

# Exemplo de uso (para teste interno)
if __name__ == "__main__":
    # Para rodar este exemplo, você precisa de uma GOOGLE_PAGESPEED_API_KEY válida no seu arquivo .env
    # E opcionalmente GOOGLE_ADS_API_KEY e META_BUSINESS_API_KEY para simulação de dados de anúncios.
    # Crie um arquivo .env na raiz do projeto com:
    # GOOGLE_PAGESPEED_API_KEY=SUA_CHAVE_AQUI
    # GOOGLE_ADS_API_KEY=SUA_CHAVE_AQUI (opcional, para simulação de ads)
    # META_BUSINESS_API_KEY=SUA_CHAVE_AQUI (opcional, para simulação de ads do Meta)

    engine = ARCOEngine()
    insights = engine.generate_optimization_insights(
        "Minha Empresa de Teste", "https://www.google.com", 5000,
        google_ads_customer_id="123-456-7890", # Exemplo de ID de cliente para análise de ads
        meta_ad_account_id="act_987654321" # Exemplo de ID de conta de anúncios Meta
    )
    logger.info(f"\nGenerated Insights: {insights}")


