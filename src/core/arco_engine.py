# src/core/arco_engine_simplified.py

from typing import Dict, List, Optional
from datetime import datetime
from src.core.http_client import HTTPClient
from src.core.cache import Cache
from src.config.arco_config_manager import ARCOConfigManager
from src.utils.logger import logger
from src.connectors.google_pagespeed_api import GooglePageSpeedAPI
from src.connectors.searchapi_connector import SearchAPIConnector
from src.integrations.bigquery_config import BigQueryConfig
from src.analysis.missed_opportunity_detector import MissedOpportunityDetector
from src.intelligence.technical_pain_detector import TechnicalPainDetector, TechnicalIntelligence
import os

class ARCOEngine:
    """
    Engine simplificado do Arco-Find focado no SearchAPI para lead generation
    Integra SearchAPI + PageSpeed + BigQuery para identificação de oportunidades
    """
    def __init__(self):
        self.http_client = HTTPClient()
        self.cache = Cache()
        self.config = ARCOConfigManager().get_config()
        
        # Initialize SearchAPI - nossa fonte principal de dados
        self.searchapi_key = os.getenv('SEARCHAPI_KEY')
        self.pagespeed_key = os.getenv('PAGESPEED_KEY') or os.getenv('GOOGLE_PAGESPEED_API_KEY')
        
        # SearchAPI para dados de Meta Ads Library
        try:
            if self.searchapi_key:
                self.searchapi = SearchAPIConnector(self.searchapi_key)
                logger.info("✅ SearchAPI (Meta Ads Library) connected")
            else:
                self.searchapi = None
                logger.warning("⚠️ SearchAPI not available - check SEARCHAPI_KEY")
        except Exception as e:
            logger.error(f"❌ SearchAPI initialization failed: {e}")
            self.searchapi = None
            
        # PageSpeed API para análise de performance
        try:
            if self.pagespeed_key:
                self.pagespeed_api = GooglePageSpeedAPI()
                logger.info("✅ PageSpeed API connected")
            else:
                self.pagespeed_api = None
                logger.warning("⚠️ PageSpeed API not available")
        except Exception as e:
            logger.error(f"❌ PageSpeed API failed: {e}")
            self.pagespeed_api = None
            
        # BigQuery para armazenamento e análise de dados
        try:
            self.bigquery = BigQueryConfig()
            if self.bigquery.setup_bigquery():
                logger.info("✅ BigQuery connected")
            else:
                logger.warning("⚠️ BigQuery setup failed")
                self.bigquery = None
        except Exception as e:
            logger.error(f"❌ BigQuery failed: {e}")
            self.bigquery = None
            
        # Detector de oportunidades
        self.missed_opportunity_detector = MissedOpportunityDetector()
        
        # Technical Pain Detector - core intelligence engine
        self.technical_pain_detector = TechnicalPainDetector()
        
        logger.info(f"ARCOEngine initialized with environment: {self.config.get('environment', 'development')}")
        
        # Log de APIs disponíveis
        available_apis = []
        if self.searchapi:
            available_apis.append("SearchAPI (Meta Ads)")
        if self.pagespeed_api:
            available_apis.append("PageSpeed")
        if self.bigquery:
            available_apis.append("BigQuery")
            
        logger.info(f"Available API services: {', '.join(available_apis)}")
    
    def discover_technical_intelligence(self, 
                                      company_name: str,
                                      website_url: str,
                                      industry: str = None) -> TechnicalIntelligence:
        """
        🎯 NEW: Discover technical pain points that cost money
        Replaces superficial data with actionable business intelligence
        
        Args:
            company_name: Nome da empresa
            website_url: URL do website  
            industry: Setor da empresa
            
        Returns:
            Technical intelligence with specific pain points and costs
        """
        logger.info(f"🧠 Technical intelligence discovery for {company_name}")
        
        # 1. Gather performance data (real technical metrics)
        performance_data = self._analyze_website_performance(website_url)
        
        # 2. Analyze digital presence (ads and spending patterns)
        digital_presence = self._analyze_digital_presence(company_name, website_url)
        
        # 3. Estimate business context for impact calculation
        business_context = self._estimate_business_context(company_name, industry, digital_presence)
        
        # 4. Use technical pain detector to identify real problems
        technical_intelligence = self.technical_pain_detector.analyze_technical_pain(
            company_name=company_name,
            website=website_url,
            performance_data=performance_data,
            digital_presence=digital_presence,
            business_context=business_context
        )
        
        logger.info(f"✅ Found ${technical_intelligence.total_monthly_pain_cost:,.0f}/month in technical debt")
        logger.info(f"🎯 Commercial urgency: {technical_intelligence.commercial_urgency.upper()}")
        logger.info(f"📈 Conversion probability: {technical_intelligence.conversion_probability:.1%}")
        
        return technical_intelligence
    
    def _estimate_business_context(self, company_name: str, industry: str, digital_presence: Dict) -> Dict:
        """Estimate business metrics needed for pain impact calculation"""
        # Base estimates on industry and digital activity
        ads_found = digital_presence.get('ads_found', 0)
        
        # Industry-based estimates
        industry_metrics = {
            'social_media': {'traffic': 15000, 'aov': 150, 'conversion': 0.025, 'ad_spend_mult': 2.0},
            'e_commerce': {'traffic': 25000, 'aov': 80, 'conversion': 0.035, 'ad_spend_mult': 2.5},
            'email_marketing': {'traffic': 12000, 'aov': 300, 'conversion': 0.020, 'ad_spend_mult': 1.8},
            'fintech': {'traffic': 8000, 'aov': 500, 'conversion': 0.015, 'ad_spend_mult': 3.0},
            'healthtech': {'traffic': 6000, 'aov': 400, 'conversion': 0.012, 'ad_spend_mult': 2.2},
            'saas': {'traffic': 10000, 'aov': 600, 'conversion': 0.018, 'ad_spend_mult': 2.8}
        }
        
        # Default to SaaS metrics if industry not found
        metrics = industry_metrics.get(industry, industry_metrics['saas'])
        
        # Adjust based on digital activity level
        activity_multiplier = 1.0
        if ads_found > 10:
            activity_multiplier = 1.5  # High activity = higher traffic/spend
        elif ads_found > 0:
            activity_multiplier = 1.2  # Some activity = moderate boost
        
        base_monthly_spend = ads_found * 800 if ads_found > 0 else 3000  # Default $3k/month
        
        return {
            'estimated_monthly_traffic': int(metrics['traffic'] * activity_multiplier),
            'avg_order_value': metrics['aov'],
            'conversion_rate': metrics['conversion'],
            'monthly_ad_spend': base_monthly_spend * metrics['ad_spend_mult'],
            'monthly_leads': int(metrics['traffic'] * activity_multiplier * 0.05),  # 5% lead rate
            'avg_lead_value': metrics['aov'] * 2.5  # Lead value = 2.5x AOV
        }
    
    def discover_and_qualify_leads(self, limit: int = 10, industry_filter: str = None) -> List[Dict]:
        """
        Método principal de descoberta e qualificação de leads usando SearchAPI
        """
        try:
            logger.info(f"🔍 Iniciando descoberta de leads (limit: {limit})")
            
            # 1. Buscar prospects do BigQuery
            prospects = self._fetch_qualified_prospects_bq(limit, industry_filter)
            
            if not prospects:
                logger.warning("⚠️ Nenhum prospect encontrado no BigQuery")
                return []
            
            # 2. Processar cada prospect com APIs
            qualified_leads = []
            for prospect in prospects:
                try:
                    processed_lead = self._process_prospect_complete(prospect)
                    if processed_lead:
                        qualified_leads.append(processed_lead)
                except Exception as e:
                    logger.warning(f"⚠️ Erro processando {prospect.get('name', 'Unknown')}: {e}")
                    continue
            
            logger.info(f"✅ Processamento completo: {len(qualified_leads)} leads qualificados")
            return qualified_leads
            
        except Exception as e:
            logger.error(f"❌ Erro na descoberta de leads: {e}")
            return []
    
    def _fetch_qualified_prospects_bq(self, limit: int, industry_filter: str = None) -> List[Dict]:
        """Busca prospects qualificados do BigQuery"""
        try:
            if not self.bigquery:
                # Fallback para dados demo
                return self._get_demo_prospects(limit)
            
            # Query para buscar empresas com alto potencial
            industry_clause = f"AND industry = '{industry_filter}'" if industry_filter else ""
            
            query = f"""
            SELECT 
                company_name as name,
                website,
                monthly_saas_spend as saas_spend,
                employee_count,
                industry,
                last_updated
            FROM `prospection-463116.arco_intelligence.prospect_companies`
            WHERE website IS NOT NULL 
                AND monthly_saas_spend > 2000
                AND employee_count BETWEEN 10 AND 100
                {industry_clause}
            ORDER BY monthly_saas_spend DESC
            LIMIT {limit}
            """
            
            results = self.bigquery.client.query(query).result()
            prospects = []
            
            for row in results:
                prospects.append({
                    "name": row.name,
                    "website": row.website,
                    "saas_spend": float(row.saas_spend) if row.saas_spend else 0,
                    "employee_count": int(row.employee_count) if row.employee_count else 0,
                    "industry": row.industry or "unknown"
                })
                
            logger.info(f"📊 Encontrados {len(prospects)} prospects no BigQuery")
            return prospects
            
        except Exception as e:
            logger.warning(f"⚠️ Erro no BigQuery: {e}, usando dados demo")
            return self._get_demo_prospects(limit)
    
    def _get_demo_prospects(self, limit: int) -> List[Dict]:
        """Dados demo para quando BigQuery não está disponível"""
        demo_prospects = [
            {
                "name": "Buffer",
                "website": "https://buffer.com",
                "saas_spend": 4200,
                "employee_count": 120,
                "industry": "social_media"
            },
            {
                "name": "Shopify",
                "website": "https://shopify.com", 
                "saas_spend": 8500,
                "employee_count": 10000,
                "industry": "e_commerce"
            },
            {
                "name": "Mailchimp",
                "website": "https://mailchimp.com",
                "saas_spend": 3800,
                "employee_count": 1200,
                "industry": "email_marketing"
            }
        ]
        
        return demo_prospects[:limit]
    
    def _process_prospect_complete(self, prospect: Dict) -> Optional[Dict]:
        """Processa um prospect completo com inteligência técnica real"""
        try:
            company_name = prospect["name"]
            website = prospect["website"]
            industry = prospect.get("industry", "unknown")
            
            # Use technical intelligence instead of superficial qualification
            technical_intelligence = self.discover_technical_intelligence(
                company_name=company_name,
                website_url=website,
                industry=industry
            )
            
            # Only proceed if there's meaningful technical pain identified
            if technical_intelligence.total_monthly_pain_cost < 1000:
                logger.info(f"⚠️ {company_name}: Insufficient technical pain (${technical_intelligence.total_monthly_pain_cost:.0f}/month)")
                return None
            
            # Calculate priority score based on technical intelligence
            priority_score = self._calculate_technical_priority_score(technical_intelligence, prospect)
            
            # Convert to enhanced lead format
            return {
                "name": company_name,
                "website": website,
                "saas_spend": prospect.get("saas_spend", 0),
                "employee_count": prospect.get("employee_count", 0),
                "industry": industry,
                "qualified": True,
                "score": priority_score,
                
                # NEW: Technical intelligence fields
                "monthly_pain_cost": technical_intelligence.total_monthly_pain_cost,
                "annual_opportunity": technical_intelligence.total_monthly_pain_cost * 12,
                "commercial_urgency": technical_intelligence.commercial_urgency,
                "conversion_probability": technical_intelligence.conversion_probability,
                "pain_points": [
                    {
                        "category": p.category,
                        "severity": p.severity,
                        "description": p.description,
                        "monthly_cost": p.monthly_cost,
                        "urgency": p.urgency_level,
                        "solution_fit": p.solution_fit
                    }
                    for p in technical_intelligence.pain_points
                ],
                "rationale": technical_intelligence.rationale,
                "next_action": technical_intelligence.next_action,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Erro processando prospect: {e}")
            return None
    
    def _calculate_technical_priority_score(self, technical_intelligence: TechnicalIntelligence, prospect: Dict) -> int:
        """Calculate priority score based on technical pain and business fit"""
        score = 0
        
        # Pain cost impact (0-40 points)
        monthly_cost = technical_intelligence.total_monthly_pain_cost
        if monthly_cost >= 10000:
            score += 40
        elif monthly_cost >= 5000:
            score += 35
        elif monthly_cost >= 2500:
            score += 25
        elif monthly_cost >= 1000:
            score += 15
        else:
            score += 5
        
        # Conversion probability (0-25 points)
        conversion_prob = technical_intelligence.conversion_probability
        score += int(conversion_prob * 25)
        
        # Urgency level (0-20 points)
        urgency_map = {'hot': 20, 'warm': 15, 'cold': 5}
        score += urgency_map.get(technical_intelligence.commercial_urgency, 5)
        
        # Solution fit (0-15 points) - based on pain point categories we can solve
        solvable_categories = ['performance', 'message_match', 'tracking']
        solvable_pain_points = [p for p in technical_intelligence.pain_points if p.category in solvable_categories]
        if solvable_pain_points:
            score += min(15, len(solvable_pain_points) * 5)
        
        return min(score, 100)
    
    def _analyze_website_performance(self, website: str) -> Dict:
        """Analisa performance do website usando PageSpeed API com análise de negócio"""
        try:
            if not self.pagespeed_api:
                return self._provide_estimated_performance_analysis(website)
            
            # Análise mobile com timeout
            try:
                mobile_data = self.pagespeed_api.analyze_url(website, strategy="mobile")
                mobile_score = 50  # Default
                
                if mobile_data and "lighthouseResult" in mobile_data:
                    lighthouse = mobile_data["lighthouseResult"]
                    if "categories" in lighthouse and "performance" in lighthouse["categories"]:
                        mobile_score = int(lighthouse["categories"]["performance"]["score"] * 100)
                
            except Exception as api_error:
                logger.warning(f"⚠️ PageSpeed API timeout/error: {api_error}")
                return self._provide_estimated_performance_analysis(website, error="API timeout")
            
            # Análise de impacto no negócio
            business_impact = self._calculate_performance_business_impact(mobile_score)
            recommendations = self._get_performance_recommendations(mobile_score)
            
            return {
                "mobile_score": mobile_score,
                "desktop_score": mobile_score + 10,  # Estimativa
                "business_impact": business_impact,
                "recommendations": recommendations,
                "analysis_date": datetime.now().isoformat(),
                "priority": business_impact.get('priority', 'medium')
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Erro na análise de performance: {e}")
            return self._provide_estimated_performance_analysis(website, error=str(e))
    
    def _provide_estimated_performance_analysis(self, website: str, error: str = None) -> Dict:
        """Análise estimada quando API não está disponível"""
        estimated_score = 65  # Estimativa conservadora
        business_impact = self._calculate_performance_business_impact(estimated_score)
        recommendations = self._get_performance_recommendations(estimated_score)
        
        return {
            "mobile_score": estimated_score,
            "desktop_score": estimated_score + 10,
            "business_impact": business_impact,
            "recommendations": recommendations,
            "analysis_date": datetime.now().isoformat(),
            "priority": "medium",
            "note": f"Estimated analysis (API issue: {error})" if error else "Estimated analysis"
        }
    
    def _calculate_performance_business_impact(self, score: int) -> Dict:
        """Calcula impacto no negócio baseado no score de performance"""
        if score >= 90:
            return {
                'impact_level': 'low',
                'priority': 'low',
                'impact_description': 'Excellent performance - minimal optimization needed',
                'conversion_impact': '0-2% potential gain',
                'revenue_impact': 'minimal'
            }
        elif score >= 70:
            return {
                'impact_level': 'medium',
                'priority': 'medium', 
                'impact_description': 'Good performance with room for improvement',
                'conversion_impact': '5-10% potential gain',
                'revenue_impact': 'moderate'
            }
        else:
            return {
                'impact_level': 'high',
                'priority': 'high',
                'impact_description': 'Poor performance significantly impacting user experience',
                'conversion_impact': '15-30% potential gain',
                'revenue_impact': 'significant'
            }
    
    def _get_performance_recommendations(self, score: int) -> List[str]:
        """Gera recomendações específicas baseadas no score"""
        recommendations = []
        
        if score < 60:
            recommendations.extend([
                "Optimize images (compress and use modern formats)",
                "Implement content delivery network (CDN)",
                "Minimize and compress CSS/JavaScript files",
                "Enable browser caching",
                "Reduce server response times"
            ])
        elif score < 80:
            recommendations.extend([
                "Optimize largest contentful paint (LCP)",
                "Reduce cumulative layout shift (CLS)", 
                "Improve first input delay (FID)",
                "Optimize web fonts loading"
            ])
        else:
            recommendations.extend([
                "Fine-tune Core Web Vitals",
                "Implement advanced caching strategies",
                "Monitor performance continuously"
            ])
            
        return recommendations
    
    def _analyze_digital_presence(self, company_name: str, website: str) -> Dict:
        """Analisa presença digital usando SearchAPI Meta Ads Library"""
        try:
            if not self.searchapi:
                return {"ads_found": 0, "estimated_spend": 0, "error": "SearchAPI not available"}
            
            # Buscar anúncios da empresa no Meta Ads Library
            ads_data = self.searchapi.search_ads_by_page(company_name)
            
            ads_count = 0
            estimated_spend = 0
            
            if ads_data and "data" in ads_data:
                ads_count = len(ads_data["data"])
                # Estimativa básica de gasto
                estimated_spend = ads_count * 500  # $500 por anúncio ativo estimado
            
            return {
                "ads_found": ads_count,
                "estimated_ad_spend": estimated_spend,
                "digital_activity": "high" if ads_count > 5 else "medium" if ads_count > 0 else "low",
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Erro na análise digital: {e}")
            return {"ads_found": 0, "estimated_spend": 0, "error": str(e)}
    
    def _qualify_prospect_integrated(self, prospect: Dict, performance: Dict, digital_presence: Dict) -> Dict:
        """Qualifica prospect baseado em todos os dados coletados"""
        reasons = []
        disqualifications = []
        score = 0
        
        # 1. Gasto SaaS (peso alto)
        saas_spend = prospect.get("saas_spend", 0)
        if saas_spend >= 3000:
            reasons.append(f"Alto gasto SaaS: ${saas_spend:,.0f}/mês")
            score += 30
        else:
            disqualifications.append(f"Gasto SaaS baixo: ${saas_spend:,.0f}")
        
        # 2. Performance do website
        mobile_score = performance.get("mobile_score", 100)
        if mobile_score < 70:
            reasons.append(f"Performance ruim: {mobile_score}/100")
            score += 25
        elif mobile_score < 85:
            reasons.append(f"Performance mediana: {mobile_score}/100")
            score += 15
        else:
            disqualifications.append("Performance do site já boa")
        
        # 3. Presença digital
        ads_found = digital_presence.get("ads_found", 0)
        if ads_found > 0:
            reasons.append(f"Ativo em ads: {ads_found} anúncios")
            score += 20
        
        # 4. Tamanho da empresa
        employee_count = prospect.get("employee_count", 0)
        if 15 <= employee_count <= 75:
            reasons.append(f"Tamanho ideal: {employee_count} funcionários")
            score += 15
        elif employee_count > 75:
            disqualifications.append("Empresa muito grande")
        
        qualified = len(disqualifications) == 0 and score >= 40
        
        return {
            "qualified": qualified,
            "score": score,
            "reasons": reasons,
            "disqualifications": disqualifications
        }
    
    def generate_optimization_insights(self, company_data: Dict) -> Dict:
        """
        Gera insights de otimização baseados em dados coletados
        """
        try:
            insights = {
                'company_name': company_data.get('name', 'Unknown'),
                'analysis_date': datetime.now().isoformat(),
                'performance_insights': {},
                'digital_insights': {},
                'optimization_opportunities': [],
                'estimated_roi': 0
            }
            
            # Performance insights
            if 'performance_data' in company_data:
                perf = company_data['performance_data']
                mobile_score = perf.get('mobile_score', 100)
                
                insights['performance_insights'] = {
                    'mobile_score': mobile_score,
                    'performance_grade': 'A' if mobile_score >= 90 else 'B' if mobile_score >= 70 else 'C',
                    'optimization_potential': max(0, 90 - mobile_score)
                }
                
                if mobile_score < 70:
                    insights['optimization_opportunities'].append({
                        'area': 'Website Performance',
                        'current_score': mobile_score,
                        'target_score': 85,
                        'potential_improvement': f"+{85 - mobile_score} points",
                        'estimated_value': 300
                    })
                    insights['estimated_roi'] += 300
            
            # Digital presence insights
            if 'digital_presence' in company_data:
                digital = company_data['digital_presence']
                ads_count = digital.get('ads_found', 0)
                
                insights['digital_insights'] = {
                    'ads_active': ads_count,
                    'digital_maturity': 'high' if ads_count > 10 else 'medium' if ads_count > 0 else 'low',
                    'market_presence': 'strong' if ads_count > 15 else 'moderate'
                }
                
                if ads_count > 0:
                    insights['optimization_opportunities'].append({
                        'area': 'Ad Spend Optimization',
                        'current_ads': ads_count,
                        'optimization_potential': '15-25% cost reduction',
                        'estimated_value': ads_count * 50
                    })
                    insights['estimated_roi'] += ads_count * 50
            
            # SaaS spend optimization
            saas_spend = company_data.get('saas_spend', 0)
            if saas_spend > 3000:
                potential_savings = saas_spend * 0.15
                insights['optimization_opportunities'].append({
                    'area': 'SaaS Stack Optimization',
                    'current_spend': saas_spend,
                    'optimization_potential': '10-20% cost reduction',
                    'estimated_value': potential_savings
                })
                insights['estimated_roi'] += potential_savings
            
            # Executive summary
            insights['executive_summary'] = {
                'total_opportunities': len(insights['optimization_opportunities']),
                'estimated_monthly_roi': insights['estimated_roi'],
                'priority': 'high' if insights['estimated_roi'] > 1000 else 'medium',
                'next_steps': [
                    'Website performance audit',
                    'Digital marketing review',
                    'SaaS audit and optimization'
                ][:len(insights['optimization_opportunities'])]
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error generating insights: {e}")
            return {'error': str(e)}
