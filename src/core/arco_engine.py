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
    
    def discover_real_opportunities(self, 
                                  company_name: str,
                                  website_url: str,
                                  industry: str = None) -> Dict[str, any]:
        """
        🎯 Descoberta de oportunidades usando dados reais
        Integra SearchAPI + PageSpeed + BigQuery
        
        Args:
            company_name: Nome da empresa
            website_url: URL do website  
            industry: Setor da empresa
            
        Returns:
            Análise completa com dados reais
        """
        logger.info(f"🚀 Real opportunity discovery for {company_name}")
        
        opportunities = {
            'company_name': company_name,
            'website_url': website_url,
            'industry': industry or 'unknown',
            'analysis_timestamp': datetime.now().isoformat(),
            'data_sources': [],
            'insights': {},
            'opportunities': [],
            'potential_savings': 0
        }
        
        # 1. Website Performance Analysis
        if self.pagespeed_api:
            try:
                logger.info("🔍 Analyzing website performance...")
                performance_data = self._analyze_website_performance(website_url)
                opportunities['data_sources'].append('Google PageSpeed Insights')
                opportunities['insights']['performance'] = performance_data
                
                # Calculate performance opportunities
                mobile_score = performance_data.get('mobile_score', 100)
                if mobile_score < 70:
                    opportunities['opportunities'].append({
                        'type': 'Website Performance',
                        'description': f"Mobile performance score is only {mobile_score}/100",
                        'potential_impact': 'High - Could improve conversion rates by 20-30%',
                        'estimated_monthly_value': 500
                    })
                    opportunities['potential_savings'] += 500
                    
            except Exception as e:
                logger.warning(f"⚠️ Performance analysis failed: {e}")
        
        # 2. Digital Presence Analysis
        if self.searchapi:
            try:
                logger.info("🔍 Analyzing digital presence...")
                digital_data = self._analyze_digital_presence(company_name, website_url)
                opportunities['data_sources'].append('SearchAPI Meta Ads Library')
                opportunities['insights']['digital_presence'] = digital_data
                
                # Calculate digital opportunities
                ads_found = digital_data.get('ads_found', 0)
                if ads_found == 0:
                    opportunities['opportunities'].append({
                        'type': 'Digital Marketing Opportunity',
                        'description': "No active Meta ads found - untapped market",
                        'potential_impact': 'Medium - Could capture market share',
                        'estimated_monthly_value': 1000
                    })
                    opportunities['potential_savings'] += 1000
                elif ads_found > 10:
                    opportunities['opportunities'].append({
                        'type': 'Ad Optimization Opportunity', 
                        'description': f"Found {ads_found} active ads - optimization potential",
                        'potential_impact': 'High - Could reduce ad spend by 15-25%',
                        'estimated_monthly_value': 800
                    })
                    opportunities['potential_savings'] += 800
                    
            except Exception as e:
                logger.warning(f"⚠️ Digital analysis failed: {e}")
        
        # 3. Use missed opportunity detector
        try:
            missed_opps = self.missed_opportunity_detector.detect_missed_opportunities(
                website_url, industry or 'technology'
            )
            opportunities['insights']['missed_opportunities'] = missed_opps
            opportunities['potential_savings'] += len(missed_opps) * 200
            
        except Exception as e:
            logger.warning(f"⚠️ Missed opportunity detection failed: {e}")
        
        # Generate executive summary
        opportunities['executive_summary'] = {
            'total_opportunities': len(opportunities['opportunities']),
            'potential_monthly_savings': opportunities['potential_savings'],
            'data_quality': 'high' if len(opportunities['data_sources']) > 1 else 'medium',
            'priority_actions': [opp['type'] for opp in opportunities['opportunities'][:3]]
        }
        
        logger.info(f"✅ Found {len(opportunities['opportunities'])} opportunities worth ${opportunities['potential_savings']}/month")
        return opportunities
    
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
        """Processa um prospect completo com todas as APIs"""
        try:
            # 1. Análise de performance do website
            performance_data = self._analyze_website_performance(prospect["website"])
            
            # 2. Análise de presença digital (SearchAPI)
            digital_presence = self._analyze_digital_presence(prospect["name"], prospect["website"])
            
            # 3. Qualificação baseada em dados reais
            qualification = self._qualify_prospect_integrated(prospect, performance_data, digital_presence)
            
            if not qualification["qualified"]:
                return None
            
            # 4. Calcular potencial de economia
            potential_savings = prospect["saas_spend"] * 0.15  # 15% economia típica
            
            return {
                "name": prospect["name"],
                "website": prospect["website"],
                "saas_spend": prospect["saas_spend"],
                "employee_count": prospect["employee_count"],
                "industry": prospect["industry"],
                "performance_data": performance_data,
                "digital_presence": digital_presence,
                "qualified": True,
                "score": qualification["score"],
                "potential_savings": potential_savings,
                "qualification_reasons": qualification["reasons"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Erro processando prospect: {e}")
            return None
    
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
