#!/usr/bin/env python3
"""
Análise Profunda de Leads - Top 10 Prospects
Análise baseada em 8 critérios de negócio reais, não apenas Web Vitals superficiais.
"""

import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Tuple, Any
import re

class DeepLeadAnalyzer:
    """Analisador profundo de leads com critérios de negócio reais."""
    
    def __init__(self):
        self.retail_segments = {
            'ecommerce_puro': {
                'keywords': ['shopify', 'woocommerce', 'magento', 'vtex', 'ecommerce'],
                'priority_multiplier': 1.4,
                'avg_contract_value': 80000,
                'conversion_rate': 0.25
            },
            'omnichannel': {
                'keywords': ['pos', 'erp', 'crm', 'inventory', 'omnichannel', 'retail locations'],
                'priority_multiplier': 1.6,
                'avg_contract_value': 150000,
                'conversion_rate': 0.35
            },
            'marketplace': {
                'keywords': ['marketplace', 'multi-vendor', 'commission', 'platform'],
                'priority_multiplier': 1.5,
                'avg_contract_value': 200000,
                'conversion_rate': 0.30
            },
            'b2b_retail': {
                'keywords': ['wholesale', 'distributor', 'b2b', 'bulk'],
                'priority_multiplier': 1.3,
                'avg_contract_value': 120000,
                'conversion_rate': 0.20
            },
            'fashion_lifestyle': {
                'keywords': ['fashion', 'clothing', 'apparel', 'jewelry', 'accessories', 'moda'],
                'priority_multiplier': 1.2,
                'avg_contract_value': 60000,
                'conversion_rate': 0.18
            },
            'health_wellness': {
                'keywords': ['health', 'wellness', 'supplements', 'nutrition', 'organic', 'natural'],
                'priority_multiplier': 1.3,
                'avg_contract_value': 90000,
                'conversion_rate': 0.22
            },
            'specialty_retail': {
                'keywords': ['specialty', 'niche', 'premium', 'luxury', 'artisan'],
                'priority_multiplier': 1.1,
                'avg_contract_value': 70000,
                'conversion_rate': 0.15
            }
        }
        
        self.geography_multipliers = {
            'brazil': 1.5,  # Prioridade máxima
            'latin_america': 1.2,
            'north_america': 1.0,
            'europe': 0.9,
            'asia': 0.8,
            'others': 0.7
        }
        
        self.technology_indicators = {
            'modern_ecommerce': ['shopify plus', 'magento', 'vtex', 'woocommerce'],
            'analytics_advanced': ['google analytics', 'hotjar', 'mixpanel', 'amplitude'],
            'marketing_automation': ['klaviyo', 'mailchimp', 'active campaign', 'hubspot'],
            'performance_tools': ['cloudflare', 'aws', 'cdn', 'new relic'],
            'conversion_optimization': ['optimizely', 'unbounce', 'google optimize'],
            'legacy_indicators': ['jquery', 'php', 'mysql', 'apache', 'wordpress']
        }

    def load_and_clean_data(self, file_path: str) -> pd.DataFrame:
        """Carrega e limpa os dados dos prospects."""
        try:
            df = pd.read_csv(file_path)
            print(f"✅ Carregados {len(df)} leads do arquivo")
            
            # Limpar e padronizar dados
            df['Company'] = df['Company'].fillna('Unknown')
            df['# Employees'] = pd.to_numeric(df['# Employees'], errors='coerce').fillna(0)
            df['Industry'] = df['Industry'].fillna('unknown')
            df['Company Country'] = df['Company Country'].fillna('unknown')
            df['Technologies'] = df['Technologies'].fillna('')
            df['Keywords'] = df['Keywords'].fillna('')
            df['Short Description'] = df['Short Description'].fillna('')
            df['Founded Year'] = pd.to_numeric(df['Founded Year'], errors='coerce').fillna(2000)
            
            return df
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return pd.DataFrame()

    def analyze_retail_segment(self, row: pd.Series) -> Dict[str, Any]:
        """1. Análise de segmento específico dentro do retail."""
        keywords = str(row['Keywords']).lower()
        description = str(row['Short Description']).lower()
        technologies = str(row['Technologies']).lower()
        
        combined_text = f"{keywords} {description} {technologies}"
        
        segment_scores = {}
        for segment, config in self.retail_segments.items():
            score = 0
            for keyword in config['keywords']:
                if keyword in combined_text:
                    score += 1
            segment_scores[segment] = score
        
        # Determinar segmento principal
        best_segment = max(segment_scores, key=segment_scores.get)
        segment_confidence = segment_scores[best_segment] / len(self.retail_segments[best_segment]['keywords'])
        
        return {
            'segment': best_segment,
            'confidence': min(segment_confidence, 1.0),
            'priority_multiplier': self.retail_segments[best_segment]['priority_multiplier'],
            'avg_contract_value': self.retail_segments[best_segment]['avg_contract_value'],
            'conversion_rate': self.retail_segments[best_segment]['conversion_rate'],
            'segment_scores': segment_scores
        }

    def analyze_revenue_potential(self, row: pd.Series, segment_info: Dict) -> Dict[str, Any]:
        """2. Análise de potencial real de receita."""
        employees = int(row['# Employees']) if pd.notna(row['# Employees']) else 0
        founded_year = int(row['Founded Year']) if pd.notna(row['Founded Year']) else 2000
        company_age = 2025 - founded_year
        
        # Base revenue estimation
        base_revenue = 0
        if employees >= 50:
            base_revenue = employees * 100000  # $100k per employee for larger companies
        elif employees >= 20:
            base_revenue = employees * 80000   # $80k per employee for medium companies
        elif employees >= 10:
            base_revenue = employees * 60000   # $60k per employee for small companies
        else:
            base_revenue = employees * 40000   # $40k per employee for micro companies
        
        # Adjust for company maturity
        maturity_multiplier = 1.0
        if company_age >= 10:
            maturity_multiplier = 1.3  # Established companies
        elif company_age >= 5:
            maturity_multiplier = 1.1  # Growing companies
        elif company_age <= 2:
            maturity_multiplier = 0.8  # Very new companies
        
        estimated_revenue = base_revenue * maturity_multiplier
        
        # Contract value potential based on segment
        contract_potential = segment_info['avg_contract_value']
        
        # Customer Lifetime Value estimation
        clv_multiplier = 3.5  # Average 3.5 years retention
        estimated_clv = contract_potential * clv_multiplier
        
        return {
            'estimated_annual_revenue': estimated_revenue,
            'contract_potential': contract_potential,
            'estimated_clv': estimated_clv,
            'revenue_score': min((estimated_revenue / 1000000) * 20, 100),  # Score out of 100
            'maturity_multiplier': maturity_multiplier
        }

    def analyze_solution_fit(self, row: pd.Series) -> Dict[str, Any]:
        """3. Análise de fit com nossa solução."""
        technologies = str(row['Technologies']).lower()
        keywords = str(row['Keywords']).lower()
        
        fit_score = 0
        fit_details = {}
        
        # Modern e-commerce platform indicators (high fit)
        modern_ecommerce_score = 0
        for tech in self.technology_indicators['modern_ecommerce']:
            if tech in technologies:
                modern_ecommerce_score += 25
                fit_details[f'modern_ecommerce_{tech}'] = True
        
        # Analytics and optimization tools (medium fit)
        analytics_score = 0
        for tech in self.technology_indicators['analytics_advanced']:
            if tech in technologies:
                analytics_score += 15
                fit_details[f'analytics_{tech}'] = True
        
        # Performance optimization needs (high fit)
        performance_score = 0
        performance_needs = ['slow', 'performance', 'speed', 'optimization', 'loading']
        for need in performance_needs:
            if need in keywords:
                performance_score += 20
                fit_details[f'performance_need_{need}'] = True
        
        # Legacy technology indicators (very high fit - modernization opportunity)
        legacy_score = 0
        for tech in self.technology_indicators['legacy_indicators']:
            if tech in technologies:
                legacy_score += 30  # Higher score for modernization opportunities
                fit_details[f'legacy_{tech}'] = True
        
        total_fit_score = min(modern_ecommerce_score + analytics_score + performance_score + legacy_score, 100)
        
        # Implementation complexity assessment
        complexity = 'low'
        if legacy_score > 60:
            complexity = 'high'
        elif modern_ecommerce_score > 50:
            complexity = 'medium'
        
        return {
            'fit_score': total_fit_score,
            'implementation_complexity': complexity,
            'modernization_opportunity': legacy_score > 30,
            'fit_details': fit_details,
            'component_scores': {
                'modern_ecommerce': modern_ecommerce_score,
                'analytics': analytics_score,
                'performance_needs': performance_score,
                'legacy_modernization': legacy_score
            }
        }

    def analyze_geography_priority(self, row: pd.Series) -> Dict[str, Any]:
        """4. Análise de priorização geográfica."""
        country = str(row['Company Country']).lower()
        state = str(row['Company State']).lower()
        city = str(row['Company City']).lower()
        
        # Determine geographic region
        region = 'others'
        if 'brazil' in country or 'brasil' in country:
            region = 'brazil'
        elif any(lat_country in country for lat_country in ['argentina', 'chile', 'colombia', 'mexico', 'peru']):
            region = 'latin_america'
        elif any(na_country in country for na_country in ['united states', 'canada', 'usa']):
            region = 'north_america'
        elif any(eu_country in country for eu_country in ['germany', 'france', 'uk', 'spain', 'italy']):
            region = 'europe'
        
        geography_multiplier = self.geography_multipliers.get(region, 0.7)
        
        # Additional scoring for Brazilian market specifics
        brazil_bonus = 0
        if region == 'brazil':
            # Major Brazilian cities get additional priority
            major_cities = ['sao paulo', 'rio de janeiro', 'belo horizonte', 'brasilia', 'salvador']
            if any(city_name in city for city_name in major_cities):
                brazil_bonus = 20
            else:
                brazil_bonus = 10
        
        return {
            'region': region,
            'geography_multiplier': geography_multiplier,
            'brazil_bonus': brazil_bonus,
            'geography_score': (geography_multiplier * 50) + brazil_bonus,
            'market_accessibility': 'high' if region == 'brazil' else 'medium' if region == 'latin_america' else 'low'
        }

    def analyze_competitive_landscape(self, row: pd.Series) -> Dict[str, Any]:
        """5. Análise competitiva."""
        technologies = str(row['Technologies']).lower()
        
        # Identify existing solutions
        existing_solutions = []
        competitive_threats = []
        
        # Performance monitoring tools
        performance_tools = ['new relic', 'datadog', 'pingdom', 'gtmetrix']
        for tool in performance_tools:
            if tool in technologies:
                existing_solutions.append(tool)
                competitive_threats.append('performance_monitoring')
        
        # CDN and optimization
        cdn_tools = ['cloudflare', 'aws cloudfront', 'fastly', 'maxcdn']
        for tool in cdn_tools:
            if tool in technologies:
                existing_solutions.append(tool)
                competitive_threats.append('cdn_optimization')
        
        # Analytics and optimization
        analytics_tools = ['google optimize', 'optimizely', 'unbounce', 'hotjar']
        for tool in analytics_tools:
            if tool in technologies:
                existing_solutions.append(tool)
                competitive_threats.append('conversion_optimization')
        
        # Determine competitive intensity
        competitive_intensity = 'low'
        if len(existing_solutions) >= 3:
            competitive_intensity = 'high'
        elif len(existing_solutions) >= 1:
            competitive_intensity = 'medium'
        
        # Switching cost assessment
        switching_cost = 'low'
        if 'enterprise' in technologies or len(existing_solutions) >= 2:
            switching_cost = 'high'
        elif len(existing_solutions) == 1:
            switching_cost = 'medium'
        
        # Opportunity score (higher when less competition)
        opportunity_score = 100 - (len(existing_solutions) * 20)
        opportunity_score = max(opportunity_score, 20)  # Minimum 20 points
        
        return {
            'existing_solutions': existing_solutions,
            'competitive_threats': list(set(competitive_threats)),
            'competitive_intensity': competitive_intensity,
            'switching_cost': switching_cost,
            'opportunity_score': opportunity_score,
            'green_field_opportunity': len(existing_solutions) == 0
        }

    def calculate_roi_potential(self, row: pd.Series, revenue_info: Dict, segment_info: Dict) -> Dict[str, Any]:
        """6. Análise de ROI real."""
        estimated_revenue = revenue_info['estimated_annual_revenue']
        employees = int(row['# Employees']) if pd.notna(row['# Employees']) else 0
        
        # Performance improvement ROI
        # Assume 2-5% revenue impact from performance optimization
        performance_roi = estimated_revenue * 0.03  # Conservative 3%
        
        # Conversion optimization ROI
        # Assume 10-25% improvement in conversion rates
        conversion_roi = estimated_revenue * 0.15  # 15% improvement
        
        # Operational efficiency ROI
        # Cost savings from automation and efficiency
        operational_savings = employees * 5000  # $5k per employee annually
        
        # Total annual benefit
        total_annual_benefit = performance_roi + conversion_roi + operational_savings
        
        # Investment required (our solution cost)
        investment_required = segment_info['avg_contract_value']
        
        # ROI calculation
        roi_percentage = ((total_annual_benefit - investment_required) / investment_required) * 100
        payback_months = (investment_required / (total_annual_benefit / 12))
        
        return {
            'performance_roi': performance_roi,
            'conversion_roi': conversion_roi,
            'operational_savings': operational_savings,
            'total_annual_benefit': total_annual_benefit,
            'investment_required': investment_required,
            'roi_percentage': roi_percentage,
            'payback_months': payback_months,
            'roi_score': min(max(roi_percentage / 2, 0), 100)  # Score out of 100
        }

    def analyze_root_causes(self, row: pd.Series) -> Dict[str, Any]:
        """7. Análise de causa raiz."""
        technologies = str(row['Technologies']).lower()
        keywords = str(row['Keywords']).lower()
        
        root_causes = []
        technical_debt_score = 0
        
        # Legacy technology stack
        legacy_tech_found = []
        for tech in self.technology_indicators['legacy_indicators']:
            if tech in technologies:
                legacy_tech_found.append(tech)
                technical_debt_score += 15
        
        if legacy_tech_found:
            root_causes.append({
                'category': 'legacy_technology',
                'description': f'Legacy technologies detected: {", ".join(legacy_tech_found)}',
                'impact': 'high',
                'solution': 'Technology stack modernization'
            })
        
        # Performance issues indicators
        performance_issues = []
        perf_keywords = ['slow', 'loading', 'speed', 'performance', 'optimization']
        for keyword in perf_keywords:
            if keyword in keywords:
                performance_issues.append(keyword)
                technical_debt_score += 10
        
        if performance_issues:
            root_causes.append({
                'category': 'performance_bottlenecks',
                'description': f'Performance concerns: {", ".join(performance_issues)}',
                'impact': 'medium',
                'solution': 'Performance optimization and CDN implementation'
            })
        
        # Missing modern tools
        missing_tools = []
        if 'google analytics' not in technologies:
            missing_tools.append('Advanced Analytics')
        if not any(tool in technologies for tool in ['klaviyo', 'mailchimp', 'hubspot']):
            missing_tools.append('Marketing Automation')
        if not any(tool in technologies for tool in ['cloudflare', 'aws', 'cdn']):
            missing_tools.append('Performance Infrastructure')
        
        if missing_tools:
            root_causes.append({
                'category': 'missing_capabilities',
                'description': f'Missing modern tools: {", ".join(missing_tools)}',
                'impact': 'medium',
                'solution': 'Modern toolstack implementation'
            })
        
        return {
            'root_causes': root_causes,
            'technical_debt_score': min(technical_debt_score, 100),
            'modernization_urgency': 'high' if technical_debt_score > 50 else 'medium' if technical_debt_score > 20 else 'low',
            'implementation_priority': len(root_causes)
        }

    def analyze_technology_stack(self, row: pd.Series) -> Dict[str, Any]:
        """8. Análise profunda do stack tecnológico."""
        technologies = str(row['Technologies']).lower()
        
        stack_analysis = {
            'ecommerce_platform': [],
            'analytics_tools': [],
            'marketing_tools': [],
            'performance_tools': [],
            'legacy_components': [],
            'modern_components': []
        }
        
        # Categorize technologies
        tech_list = [tech.strip() for tech in technologies.split(',')]
        
        for tech in tech_list:
            tech_lower = tech.lower()
            
            # E-commerce platforms
            if any(platform in tech_lower for platform in ['shopify', 'magento', 'woocommerce', 'vtex']):
                stack_analysis['ecommerce_platform'].append(tech)
                stack_analysis['modern_components'].append(tech)
            
            # Analytics
            elif any(analytics in tech_lower for analytics in ['google analytics', 'hotjar', 'mixpanel']):
                stack_analysis['analytics_tools'].append(tech)
                stack_analysis['modern_components'].append(tech)
            
            # Marketing tools
            elif any(marketing in tech_lower for marketing in ['klaviyo', 'mailchimp', 'hubspot', 'active campaign']):
                stack_analysis['marketing_tools'].append(tech)
                stack_analysis['modern_components'].append(tech)
            
            # Performance tools
            elif any(perf in tech_lower for perf in ['cloudflare', 'aws', 'cdn', 'new relic']):
                stack_analysis['performance_tools'].append(tech)
                stack_analysis['modern_components'].append(tech)
            
            # Legacy indicators
            elif any(legacy in tech_lower for legacy in ['jquery', 'php', 'mysql', 'apache', 'wordpress']):
                stack_analysis['legacy_components'].append(tech)
        
        # Calculate technology maturity score
        modern_score = len(stack_analysis['modern_components']) * 10
        legacy_penalty = len(stack_analysis['legacy_components']) * 5
        technology_maturity_score = max(modern_score - legacy_penalty, 0)
        
        # Integration complexity assessment
        integration_points = len(stack_analysis['ecommerce_platform']) + len(stack_analysis['analytics_tools'])
        integration_complexity = 'low' if integration_points <= 2 else 'medium' if integration_points <= 4 else 'high'
        
        return {
            'stack_breakdown': stack_analysis,
            'technology_maturity_score': min(technology_maturity_score, 100),
            'integration_complexity': integration_complexity,
            'modernization_potential': len(stack_analysis['legacy_components']) > 2,
            'total_technologies': len(tech_list),
            'modern_vs_legacy_ratio': len(stack_analysis['modern_components']) / max(len(stack_analysis['legacy_components']), 1)
        }

    def calculate_final_score(self, analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula score final ponderado."""
        weights = {
            'segment_fit': 0.20,      # 20% - Fit do segmento
            'revenue_potential': 0.18, # 18% - Potencial de receita
            'solution_fit': 0.15,     # 15% - Fit da solução
            'geography': 0.15,        # 15% - Prioridade geográfica
            'competitive': 0.12,      # 12% - Vantagem competitiva
            'roi_potential': 0.10,    # 10% - Potencial de ROI
            'technical_urgency': 0.05, # 5% - Urgência técnica
            'technology_maturity': 0.05 # 5% - Maturidade tecnológica
        }
        
        # Extract scores
        segment_score = analyses['segment']['confidence'] * 100
        revenue_score = analyses['revenue']['revenue_score']
        fit_score = analyses['solution_fit']['fit_score']
        geography_score = analyses['geography']['geography_score']
        competitive_score = analyses['competitive']['opportunity_score']
        roi_score = analyses['roi']['roi_score']
        urgency_score = analyses['root_causes']['technical_debt_score']
        tech_score = analyses['technology']['technology_maturity_score']
        
        # Calculate weighted final score
        final_score = (
            segment_score * weights['segment_fit'] +
            revenue_score * weights['revenue_potential'] +
            fit_score * weights['solution_fit'] +
            geography_score * weights['geography'] +
            competitive_score * weights['competitive'] +
            roi_score * weights['roi_potential'] +
            urgency_score * weights['technical_urgency'] +
            tech_score * weights['technology_maturity']
        )
        
        # Apply geography multiplier
        final_score *= analyses['geography']['geography_multiplier']
        
        # Apply segment multiplier
        final_score *= analyses['segment']['priority_multiplier']
        
        # Ensure score is within bounds
        final_score = min(max(final_score, 0), 100)
        
        return {
            'final_score': final_score,
            'component_scores': {
                'segment_fit': segment_score,
                'revenue_potential': revenue_score,
                'solution_fit': fit_score,
                'geography': geography_score,
                'competitive_advantage': competitive_score,
                'roi_potential': roi_score,
                'technical_urgency': urgency_score,
                'technology_maturity': tech_score
            },
            'applied_multipliers': {
                'geography': analyses['geography']['geography_multiplier'],
                'segment': analyses['segment']['priority_multiplier']
            }
        }

    def generate_approach_strategy(self, row: pd.Series, analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Gera estratégia de abordagem personalizada."""
        company_name = row['Company']
        employees = int(row['# Employees']) if pd.notna(row['# Employees']) else 0
        segment = analyses['segment']['segment']
        
        # Determine decision maker targets
        if employees <= 20:
            decision_makers = ['CEO', 'Founder', 'Owner']
        elif employees <= 50:
            decision_makers = ['CEO', 'CTO', 'Marketing Director']
        else:
            decision_makers = ['CTO', 'VP Engineering', 'CMO', 'Digital Director']
        
        # Key pain points based on analysis
        pain_points = []
        if analyses['root_causes']['technical_debt_score'] > 50:
            pain_points.append('Legacy technology limiting growth')
        if analyses['competitive']['competitive_intensity'] == 'high':
            pain_points.append('Competitive pressure requiring differentiation')
        if analyses['solution_fit']['fit_score'] > 60:
            pain_points.append('Performance optimization opportunities')
        
        # Value proposition
        roi_percentage = analyses['roi']['roi_percentage']
        payback_months = analyses['roi']['payback_months']
        
        value_prop = f"Podemos ajudar {company_name} a aumentar receita em {roi_percentage:.1f}% com payback em {payback_months:.1f} meses através de otimização de performance e conversão."
        
        # Timing recommendations
        urgency = analyses['root_causes']['modernization_urgency']
        timing = 'immediate' if urgency == 'high' else 'short_term' if urgency == 'medium' else 'medium_term'
        
        return {
            'decision_makers': decision_makers,
            'key_pain_points': pain_points,
            'value_proposition': value_prop,
            'optimal_timing': timing,
            'primary_message_angle': f'{segment.replace("_", " ").title()} optimization specialist',
            'expected_objections': ['Budget constraints', 'Implementation complexity', 'ROI uncertainty'],
            'success_probability': analyses['scoring']['final_score'] / 100
        }

    def analyze_single_lead(self, row: pd.Series) -> Dict[str, Any]:
        """Análise completa de um único lead."""
        try:
            # Execute all 8 analysis criteria
            segment_analysis = self.analyze_retail_segment(row)
            revenue_analysis = self.analyze_revenue_potential(row, segment_analysis)
            fit_analysis = self.analyze_solution_fit(row)
            geography_analysis = self.analyze_geography_priority(row)
            competitive_analysis = self.analyze_competitive_landscape(row)
            roi_analysis = self.calculate_roi_potential(row, revenue_analysis, segment_analysis)
            root_cause_analysis = self.analyze_root_causes(row)
            technology_analysis = self.analyze_technology_stack(row)
            
            # Combine all analyses
            all_analyses = {
                'segment': segment_analysis,
                'revenue': revenue_analysis,
                'solution_fit': fit_analysis,
                'geography': geography_analysis,
                'competitive': competitive_analysis,
                'roi': roi_analysis,
                'root_causes': root_cause_analysis,
                'technology': technology_analysis
            }
            
            # Calculate final score
            scoring = self.calculate_final_score(all_analyses)
            all_analyses['scoring'] = scoring
            
            # Generate approach strategy
            strategy = self.generate_approach_strategy(row, all_analyses)
            all_analyses['approach_strategy'] = strategy
            
            return all_analyses
            
        except Exception as e:
            print(f"❌ Erro na análise do lead {row.get('Company', 'Unknown')}: {e}")
            return {}

    def analyze_all_leads(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Analisa todos os leads e retorna resultados ordenados."""
        print(f"\n🔍 Iniciando análise profunda de {len(df)} leads...")
        
        results = []
        
        for idx, row in df.iterrows():
            print(f"Analisando {idx+1}/{len(df)}: {row['Company']}")
            
            analysis = self.analyze_single_lead(row)
            if analysis:
                # Add basic company info
                analysis['company_info'] = {
                    'name': row['Company'],
                    'domain': row.get('Website', ''),
                    'employees': int(row['# Employees']) if pd.notna(row['# Employees']) else 0,
                    'industry': row['Industry'],
                    'location': f"{row.get('Company City', '')}, {row.get('Company Country', '')}",
                    'founded_year': int(row['Founded Year']) if pd.notna(row['Founded Year']) else None
                }
                
                results.append(analysis)
        
        # Sort by final score
        results.sort(key=lambda x: x.get('scoring', {}).get('final_score', 0), reverse=True)
        
        print(f"✅ Análise concluída. {len(results)} leads analisados com sucesso.")
        return results

    def generate_top_10_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Gera relatório detalhado dos top 10 leads."""
        top_10 = results[:10]
        
        report = {
            'analysis_date': datetime.now().isoformat(),
            'total_leads_analyzed': len(results),
            'top_10_leads': [],
            'summary_insights': {
                'average_score': sum(r['scoring']['final_score'] for r in top_10) / 10,
                'geographic_distribution': {},
                'segment_distribution': {},
                'total_revenue_potential': 0,
                'total_contract_value': 0
            }
        }
        
        for i, result in enumerate(top_10, 1):
            company_info = result['company_info']
            scoring = result['scoring']
            strategy = result['approach_strategy']
            
            lead_summary = {
                'rank': i,
                'company_name': company_info['name'],
                'domain': company_info['domain'],
                'location': company_info['location'],
                'employees': company_info['employees'],
                'final_score': round(scoring['final_score'], 2),
                'segment': result['segment']['segment'],
                'revenue_potential': result['revenue']['estimated_annual_revenue'],
                'contract_value': result['revenue']['contract_potential'],
                'roi_percentage': round(result['roi']['roi_percentage'], 1),
                'payback_months': round(result['roi']['payback_months'], 1),
                'decision_makers': strategy['decision_makers'],
                'key_pain_points': strategy['key_pain_points'],
                'value_proposition': strategy['value_proposition'],
                'success_probability': round(strategy['success_probability'] * 100, 1),
                'why_top_10': self.generate_ranking_justification(result),
                'approach_recommendations': {
                    'timing': strategy['optimal_timing'],
                    'message_angle': strategy['primary_message_angle'],
                    'expected_objections': strategy['expected_objections']
                },
                'detailed_scores': scoring['component_scores']
            }
            
            report['top_10_leads'].append(lead_summary)
            
            # Update summary insights
            location = company_info['location']
            if 'Brazil' in location:
                region = 'Brazil'
            elif any(country in location for country in ['Argentina', 'Chile', 'Colombia']):
                region = 'Latin America'
            else:
                region = 'Other'
            
            report['summary_insights']['geographic_distribution'][region] = \
                report['summary_insights']['geographic_distribution'].get(region, 0) + 1
            
            segment = result['segment']['segment']
            report['summary_insights']['segment_distribution'][segment] = \
                report['summary_insights']['segment_distribution'].get(segment, 0) + 1
            
            report['summary_insights']['total_revenue_potential'] += result['revenue']['estimated_annual_revenue']
            report['summary_insights']['total_contract_value'] += result['revenue']['contract_potential']
        
        return report

    def generate_ranking_justification(self, result: Dict[str, Any]) -> str:
        """Gera justificativa detalhada para o ranking."""
        reasons = []
        
        # Geographic advantage
        if result['geography']['region'] == 'brazil':
            reasons.append(f"🇧🇷 Localização prioritária no Brasil (multiplicador {result['geography']['geography_multiplier']}x)")
        
        # Segment fit
        segment = result['segment']['segment'].replace('_', ' ').title()
        confidence = result['segment']['confidence']
        reasons.append(f"🎯 Excelente fit no segmento {segment} (confiança: {confidence:.1%})")
        
        # Revenue potential
        revenue = result['revenue']['estimated_annual_revenue']
        reasons.append(f"💰 Alto potencial de receita: ${revenue:,.0f} anuais")
        
        # ROI attractiveness
        roi = result['roi']['roi_percentage']
        if roi > 100:
            reasons.append(f"📈 ROI excepcional: {roi:.1f}% ao ano")
        elif roi > 50:
            reasons.append(f"📊 ROI atrativo: {roi:.1f}% ao ano")
        
        # Technical opportunity
        if result['root_causes']['technical_debt_score'] > 50:
            reasons.append("⚡ Alta urgência de modernização tecnológica")
        
        # Competitive advantage
        if result['competitive']['green_field_opportunity']:
            reasons.append("🆕 Oportunidade green field (sem concorrentes diretos)")
        elif result['competitive']['opportunity_score'] > 70:
            reasons.append("🎪 Baixa intensidade competitiva")
        
        return " | ".join(reasons)

def main():
    """Função principal de execução."""
    print("🚀 ANÁLISE PROFUNDA DE LEADS - TOP 10 PROSPECTS")
    print("=" * 60)
    
    analyzer = DeepLeadAnalyzer()
    
    # Load data
    df = analyzer.load_and_clean_data('arco/consolidated_prospects.csv')
    if df.empty:
        print("❌ Não foi possível carregar os dados. Verifique o arquivo.")
        return
    
    # Analyze all leads
    results = analyzer.analyze_all_leads(df)
    if not results:
        print("❌ Nenhum lead foi analisado com sucesso.")
        return
    
    # Generate top 10 report
    report = analyzer.generate_top_10_report(results)
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save full analysis
    with open(f'deep_analysis_results_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    # Save top 10 report
    with open(f'top_10_leads_analysis_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    # Generate executive summary
    print("\n" + "=" * 80)
    print("📊 TOP 10 LEADS MAIS PROMISSORES - RESUMO EXECUTIVO")
    print("=" * 80)
    
    for i, lead in enumerate(report['top_10_leads'], 1):
        print(f"\n{i}. {lead['company_name']} ({lead['domain']})")
        print(f"   📍 {lead['location']} | 👥 {lead['employees']} funcionários")
        print(f"   🎯 Score Final: {lead['final_score']}/100 | 🏆 Segmento: {lead['segment'].replace('_', ' ').title()}")
        print(f"   💰 Potencial: ${lead['revenue_potential']:,.0f} | 📈 ROI: {lead['roi_percentage']}% | ⏱️ Payback: {lead['payback_months']:.1f} meses")
        print(f"   🎪 Probabilidade de Sucesso: {lead['success_probability']}%")
        print(f"   💡 {lead['why_top_10']}")
        print(f"   🎯 Decisores: {', '.join(lead['decision_makers'])}")
        print(f"   📝 Proposta: {lead['value_proposition']}")
    
    print(f"\n" + "=" * 80)
    print("📈 INSIGHTS GERAIS")
    print("=" * 80)
    print(f"Score médio dos top 10: {report['summary_insights']['average_score']:.1f}/100")
    print(f"Potencial total de receita: ${report['summary_insights']['total_revenue_potential']:,.0f}")
    print(f"Valor total de contratos: ${report['summary_insights']['total_contract_value']:,.0f}")
    
    print("\n🌎 Distribuição Geográfica:")
    for region, count in report['summary_insights']['geographic_distribution'].items():
        print(f"   {region}: {count} leads ({count/10*100:.0f}%)")
    
    print("\n🎯 Distribuição por Segmento:")
    for segment, count in report['summary_insights']['segment_distribution'].items():
        print(f"   {segment.replace('_', ' ').title()}: {count} leads ({count/10*100:.0f}%)")
    
    print(f"\n✅ Análise completa salva em:")
    print(f"   📄 Resultados detalhados: deep_analysis_results_{timestamp}.json")
    print(f"   📊 Relatório Top 10: top_10_leads_analysis_{timestamp}.json")

if __name__ == "__main__":
    main()