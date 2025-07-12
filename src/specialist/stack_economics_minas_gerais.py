#!/usr/bin/env python3
"""
🎯 MINAS GERAIS STACK ECONOMICS ENGINE
Integrated ARCO system focused on R$ 1,997 cost reduction package
Using sophisticated infrastructure for stack waste detection

Business Model: Identify R$ 500+/month SaaS waste for ROI in 4 months
Target: 5-50 employee businesses with over-engineered stacks
"""

import sys
import os
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Add paths for ARCO infrastructure
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'detectors'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'archive'))

from integrated_arco_engine import IntegratedARCOEngine
from custom_tech_detector import CustomTechDetector
from arco_saas_overspending_detector import WebDevOpportunityDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class StackEconomicsLead:
    """Lead qualificado por stack economics"""
    place_id: str
    name: str
    business_type: str
    address: str
    phone: Optional[str]
    website: Optional[str]
    rating: float
    reviews: int
    
    # Stack Economics Analysis
    monthly_stack_waste: int  # R$/month
    annual_savings: int       # R$/year
    roi_months: float        # Months to ROI for R$ 1,997
    migration_complexity: str # low/medium/high
    
    # Business Qualification
    estimated_employees: int
    estimated_revenue: str
    business_maturity: str   # startup/established/enterprise
    tech_sophistication: str # basic/intermediate/advanced
    
    # Package Qualification
    package_roi_score: int   # 0-100 for R$ 1,997 package
    priority_level: str      # ULTRA_HIGH/HIGH/MEDIUM/LOW
    qualification_rationale: str
    
    # Detected Stack Issues
    expensive_tools: List[Dict]
    recommended_replacements: List[Dict]
    quick_wins: List[str]
    
    # Sales Intelligence
    approach_strategy: str
    key_savings_pitch: str
    objection_handling: Dict
    
class StackEconomicsEngine:
    """Engine focado em stack economics para pacote R$ 1,997"""
    
    def __init__(self):
        logger.info("🎯 Initializing Stack Economics Engine for R$ 1,997 Package")
        
        # Core ARCO infrastructure
        self.integrated_engine = IntegratedARCOEngine()
        self.tech_detector = CustomTechDetector()
        self.saas_detector = WebDevOpportunityDetector()
        
        # Target profile for R$ 1,997 package
        self.ideal_target_profile = {
            'min_monthly_waste': 500,    # R$ 500/mês minimum for ROI
            'max_roi_months': 6,         # ROI within 6 months
            'ideal_employees': (5, 50),  # Sweet spot
            'target_business_types': [
                'accounting', 'legal', 'healthcare', 'marketing_agency', 
                'consulting', 'real_estate', 'architecture'
            ],
            'stack_complexity_indicators': [
                'multiple_cms_tools', 'premium_plugins', 'redundant_tools',
                'enterprise_tools_small_business', 'legacy_hosting'
            ]
        }
        
        # MG specific business context
        self.mg_business_queries = [
            {
                'query': 'escritorio contabilidade Belo Horizonte MG',
                'business_type': 'accounting',
                'expected_stack_waste': (800, 2000),  # R$/month
                'common_overspends': ['accounting_software', 'hosting', 'wordpress_plugins']
            },
            {
                'query': 'consultorio medico dentista Belo Horizonte MG',
                'business_type': 'healthcare', 
                'expected_stack_waste': (600, 1500),
                'common_overspends': ['medical_software', 'appointment_tools', 'website_builders']
            },
            {
                'query': 'escritorio advocacia juridico Belo Horizonte MG',
                'business_type': 'legal',
                'expected_stack_waste': (700, 1800),
                'common_overspends': ['legal_software', 'crm_systems', 'document_tools']
            },
            {
                'query': 'agencia marketing consultoria Belo Horizonte MG',
                'business_type': 'marketing_agency',
                'expected_stack_waste': (1000, 3000),
                'common_overspends': ['marketing_automation', 'design_tools', 'analytics']
            },
            {
                'query': 'empresa arquitetura engenharia Belo Horizonte MG',
                'business_type': 'architecture',
                'expected_stack_waste': (500, 1200),
                'common_overspends': ['design_software', 'project_management', 'hosting']
            }
        ]
    
    def analyze_stack_economics(self, business_data: Dict, website: str) -> Dict:
        """Análise econômica detalhada do stack tecnológico"""
        
        if not website:
            return {
                'monthly_waste': 0,
                'tools': [],
                'analysis_possible': False,
                'reason': 'No website for analysis'
            }
        
        logger.info(f"   💰 Analyzing stack economics for {website}")
        
        # ARCO SaaS Detection (sophisticated)
        saas_analysis = self.saas_detector.analyze_saas_overspending(website)
          # Custom tech detection  
        tech_analysis = self.tech_detector.detect_tech_stack(website)
        
        # Calculate real stack waste
        monthly_waste = 0
        expensive_tools = []
        recommended_replacements = []
        
        if saas_analysis:
            for opportunity in saas_analysis.overspending_opportunities:
                monthly_waste += opportunity.monthly_savings
                expensive_tools.append({
                    'tool': opportunity.tool_name,
                    'category': opportunity.category,
                    'current_cost': opportunity.estimated_monthly_cost,
                    'alternative_cost': opportunity.alternative_cost,
                    'monthly_savings': opportunity.monthly_savings,
                    'difficulty': opportunity.replacement_difficulty,
                    'alternative': opportunity.recommended_alternative
                })
        
        # Add tech debt costs (hosting, outdated tech)
        if tech_analysis:
            # Hosting overpay detection
            if any(expensive_host in str(tech_analysis) for expensive_host in ['wpengine', 'kinsta']):
                monthly_waste += 200  # R$ 200/month hosting overpay
                expensive_tools.append({
                    'tool': 'Premium Hosting',
                    'category': 'Infrastructure',
                    'current_cost': 300,
                    'alternative_cost': 80,
                    'monthly_savings': 220,
                    'difficulty': 'Medium',
                    'alternative': 'SiteGround Business'
                })
            
            # WordPress plugin bloat
            wordpress_indicators = ['elementor', 'wpforms', 'yoast-premium']
            detected_plugins = sum(1 for plugin in wordpress_indicators if plugin in str(tech_analysis).lower())
            if detected_plugins >= 2:
                plugin_waste = detected_plugins * 30  # R$ 30/month per premium plugin
                monthly_waste += plugin_waste
                expensive_tools.append({
                    'tool': f'{detected_plugins} Premium WordPress Plugins',
                    'category': 'Website Tools',
                    'current_cost': detected_plugins * 40,
                    'alternative_cost': 0,
                    'monthly_savings': plugin_waste,
                    'difficulty': 'Easy',
                    'alternative': 'Free plugin alternatives'
                })
        
        return {
            'monthly_waste': monthly_waste,
            'annual_savings': monthly_waste * 12,
            'expensive_tools': expensive_tools,
            'recommended_replacements': recommended_replacements,
            'analysis_possible': True,
            'saas_analysis': saas_analysis,
            'tech_analysis': tech_analysis
        }
    
    def estimate_business_size(self, business_data: Dict) -> Dict:
        """Estimar tamanho e sofisticação do negócio"""
        
        rating = business_data.get('rating', 0) or 0
        reviews = business_data.get('user_ratings_total', 0) or 0
        
        # Employee estimation based on reviews and business type
        if reviews >= 100:
            estimated_employees = 25
            business_maturity = 'established'
        elif reviews >= 50:
            estimated_employees = 15
            business_maturity = 'established'
        elif reviews >= 20:
            estimated_employees = 8
            business_maturity = 'growing'
        else:
            estimated_employees = 3
            business_maturity = 'startup'
        
        # Revenue estimation
        if estimated_employees >= 20:
            revenue_range = 'R$ 100K-500K/month'
        elif estimated_employees >= 10:
            revenue_range = 'R$ 50K-200K/month'
        elif estimated_employees >= 5:
            revenue_range = 'R$ 20K-100K/month'
        else:
            revenue_range = 'R$ 5K-50K/month'
        
        return {
            'estimated_employees': estimated_employees,
            'business_maturity': business_maturity,
            'revenue_range': revenue_range,
            'reviews': reviews,
            'rating': rating
        }
    
    def calculate_package_roi_score(self, monthly_waste: int, business_size: Dict, migration_complexity: str) -> int:
        """Calcular score ROI para pacote R$ 1,997"""
        
        if monthly_waste < 300:
            return 0  # ROI insuficiente
        
        score = 0
        package_price = 1997
        
        # ROI timing (max 40 pontos)
        roi_months = package_price / monthly_waste if monthly_waste > 0 else 12
        if roi_months <= 2:
            score += 40
        elif roi_months <= 4:
            score += 30
        elif roi_months <= 6:
            score += 20
        elif roi_months <= 8:
            score += 10
        
        # Monthly savings amount (max 30 pontos)
        if monthly_waste >= 1000:
            score += 30
        elif monthly_waste >= 700:
            score += 25
        elif monthly_waste >= 500:
            score += 20
        elif monthly_waste >= 300:
            score += 15
        
        # Business size fit (max 20 pontos)
        employees = business_size.get('estimated_employees', 0)
        if 5 <= employees <= 50:  # Sweet spot
            score += 20
        elif 3 <= employees <= 70:  # Acceptable
            score += 15
        elif employees > 70:  # Too big
            score += 5
        else:  # Too small
            score += 10
        
        # Migration complexity (max 10 pontos)
        if migration_complexity == 'low':
            score += 10
        elif migration_complexity == 'medium':
            score += 7
        else:  # high
            score += 3
        
        return min(score, 100)
    
    def determine_migration_complexity(self, expensive_tools: List[Dict], business_type: str) -> str:
        """Determinar complexidade de migração"""
        
        complexity_factors = []
        
        # Number of tools to replace
        if len(expensive_tools) >= 5:
            complexity_factors.append('many_tools')
        
        # Critical business tools
        critical_categories = ['accounting', 'crm', 'ecommerce']
        has_critical = any(tool['category'].lower() in critical_categories for tool in expensive_tools)
        if has_critical:
            complexity_factors.append('critical_tools')
        
        # Custom integrations
        high_difficulty_tools = [tool for tool in expensive_tools if tool.get('difficulty') == 'Hard']
        if len(high_difficulty_tools) >= 2:
            complexity_factors.append('complex_integrations')
        
        # Business type specific
        if business_type in ['accounting', 'legal'] and len(expensive_tools) >= 3:
            complexity_factors.append('compliance_requirements')
        
        # Determine overall complexity
        if len(complexity_factors) >= 3:
            return 'high'
        elif len(complexity_factors) >= 1:
            return 'medium'
        else:
            return 'low'
    
    def generate_sales_intelligence(self, monthly_waste: int, expensive_tools: List[Dict], 
                                   business_type: str, roi_months: float) -> Dict:
        """Gerar inteligência para vendas"""
        
        # Key savings pitch
        top_savings = sorted(expensive_tools, key=lambda x: x['monthly_savings'], reverse=True)[:3]
        savings_pitch = f"Identificamos R$ {monthly_waste:,}/mês em gastos desnecessários. "
        
        if top_savings:
            biggest_waste = top_savings[0]
            savings_pitch += f"Maior desperdício: {biggest_waste['tool']} custando "
            savings_pitch += f"R$ {biggest_waste['current_cost']}/mês quando poderia custar "
            savings_pitch += f"R$ {biggest_waste['alternative_cost']}/mês."
        
        # Approach strategy
        if roi_months <= 3:
            approach = f"ROI em {roi_months:.1f} meses - investimento se paga rapidamente"
        elif roi_months <= 6:
            approach = f"ROI sólido em {roi_months:.1f} meses com economia garantida"
        else:
            approach = f"Economia de R$ {monthly_waste * 12:,}/ano justifica investimento"
        
        # Objection handling
        objections = {
            'price': f"R$ 1,997 se paga em {roi_months:.1f} meses com economia de R$ {monthly_waste}/mês",
            'disruption': "Migração sem fricção - mantemos operações durante transição",
            'risk': "Economia garantida desde o primeiro mês, sem risco operacional",
            'timing': f"Cada mês de atraso custa R$ {monthly_waste} em desperdício"
        }
        
        return {
            'key_savings_pitch': savings_pitch,
            'approach_strategy': approach,
            'objection_handling': objections,
            'top_savings_opportunities': top_savings
        }
    
    def qualify_for_package(self, business_data: Dict) -> bool:
        """Filtro inicial para qualificação do pacote"""
        
        # Must have website
        if not business_data.get('website'):
            return False
        
        # Must be in Minas Gerais
        address = business_data.get('formatted_address', '')
        if not any(mg_indicator in address for mg_indicator in ['MG', 'Minas Gerais', 'Belo Horizonte']):
            return False
        
        # Must have minimum business activity
        reviews = business_data.get('user_ratings_total', 0) or 0
        if reviews < 5:
            return False
        
        # Must have decent rating
        rating = business_data.get('rating', 0) or 0
        if rating < 3.5:
            return False
        
        return True
    
    def generate_stack_economics_leads(self) -> List[StackEconomicsLead]:
        """Gerar leads focados em stack economics"""
        
        logger.info("🎯 GENERATING STACK ECONOMICS LEADS FOR R$ 1,997 PACKAGE")
        logger.info("=" * 80)
        
        qualified_leads = []
        
        for query_config in self.mg_business_queries:
            logger.info(f"\n🔍 Analyzing {query_config['business_type']} niche")
            logger.info(f"Expected waste: R$ {query_config['expected_stack_waste'][0]}-{query_config['expected_stack_waste'][1]}/month")
            
            # Use integrated ARCO engine for business discovery
            businesses = self.integrated_engine.lead_generator.discover_businesses(
                query_config['business_type'], 
                query_config['query'], 
                10  # Get more options
            )
            
            for business in businesses:
                if not self.qualify_for_package(business):
                    continue
                
                name = business.get('name', 'Unknown')
                website = business.get('website')
                
                logger.info(f"   📊 Analyzing: {name}")
                
                try:
                    # Business size estimation
                    business_size = self.estimate_business_size(business)
                    
                    # Stack economics analysis
                    stack_analysis = self.analyze_stack_economics(business, website)
                    
                    if not stack_analysis['analysis_possible']:
                        logger.info(f"   ❌ Cannot analyze stack: {stack_analysis['reason']}")
                        continue
                    
                    monthly_waste = stack_analysis['monthly_waste']
                    
                    # Must meet minimum threshold
                    if monthly_waste < 300:
                        logger.info(f"   ❌ Insufficient waste: R$ {monthly_waste}/month (min: R$ 300)")
                        continue
                    
                    # Calculate package ROI
                    migration_complexity = self.determine_migration_complexity(
                        stack_analysis['expensive_tools'], 
                        query_config['business_type']
                    )
                    
                    roi_score = self.calculate_package_roi_score(
                        monthly_waste, 
                        business_size, 
                        migration_complexity
                    )
                    
                    # Must meet minimum ROI threshold
                    if roi_score < 40:
                        logger.info(f"   ❌ ROI score too low: {roi_score}/100")
                        continue
                    
                    # ROI calculation
                    roi_months = 1997 / monthly_waste if monthly_waste > 0 else 12
                    
                    # Priority determination
                    if roi_score >= 80:
                        priority = "🔥 ULTRA HIGH"
                    elif roi_score >= 65:
                        priority = "⚡ HIGH"
                    elif roi_score >= 50:
                        priority = "📊 MEDIUM"
                    else:
                        priority = "📋 LOW"
                    
                    # Sales intelligence
                    sales_intel = self.generate_sales_intelligence(
                        monthly_waste,
                        stack_analysis['expensive_tools'],
                        query_config['business_type'],
                        roi_months
                    )
                    
                    # Qualification rationale
                    rationale = f"ROI em {roi_months:.1f} meses, economia R$ {monthly_waste}/mês, "
                    rationale += f"{len(stack_analysis['expensive_tools'])} ferramentas caras identificadas, "
                    rationale += f"migração {migration_complexity} complexidade"
                    
                    lead = StackEconomicsLead(
                        place_id=business.get('place_id', ''),
                        name=name,
                        business_type=query_config['business_type'],
                        address=business.get('formatted_address', ''),
                        phone=business.get('formatted_phone_number'),
                        website=website,
                        rating=business.get('rating', 0),
                        reviews=business.get('user_ratings_total', 0),
                        monthly_stack_waste=monthly_waste,
                        annual_savings=monthly_waste * 12,
                        roi_months=roi_months,
                        migration_complexity=migration_complexity,
                        estimated_employees=business_size['estimated_employees'],
                        estimated_revenue=business_size['revenue_range'],
                        business_maturity=business_size['business_maturity'],
                        tech_sophistication='intermediate',  # Default
                        package_roi_score=roi_score,
                        priority_level=priority,
                        qualification_rationale=rationale,
                        expensive_tools=stack_analysis['expensive_tools'],
                        recommended_replacements=stack_analysis['recommended_replacements'],
                        quick_wins=[f"Substituir {tool['tool']}" for tool in stack_analysis['expensive_tools'][:3]],
                        approach_strategy=sales_intel['approach_strategy'],
                        key_savings_pitch=sales_intel['key_savings_pitch'],
                        objection_handling=sales_intel['objection_handling']
                    )
                    
                    qualified_leads.append(lead)
                    
                    logger.info(f"   ✅ QUALIFIED: ROI {roi_months:.1f}m | R$ {monthly_waste}/m waste | {priority}")
                    
                    # Rate limiting
                    time.sleep(3)
                    
                except Exception as e:
                    logger.error(f"   ❌ Error analyzing {name}: {e}")
                    continue
            
            # Small delay between niches
            time.sleep(2)
        
        # Sort by ROI score
        qualified_leads.sort(key=lambda x: x.package_roi_score, reverse=True)
        
        return qualified_leads[:5]  # Top 5
    
    def export_results(self, leads: List[StackEconomicsLead]) -> str:
        """Export results with business model focus"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/stack_economics_minas_gerais_{timestamp}.json"
        
        export_data = {
            'generated_at': datetime.now().isoformat(),
            'business_model': 'R$ 1,997 Stack Cost Reduction Package',
            'target_roi_threshold': '6 months or less',
            'min_monthly_savings': 'R$ 500/month',
            'total_leads': len(leads),
            'leads': [asdict(lead) for lead in leads],
            'economics_summary': {
                'total_monthly_waste_identified': sum(lead.monthly_stack_waste for lead in leads),
                'total_annual_savings': sum(lead.annual_savings for lead in leads),
                'average_roi_months': sum(lead.roi_months for lead in leads) / len(leads) if leads else 0,
                'total_package_revenue_potential': len(leads) * 1997,
                'priority_distribution': {
                    'ultra_high': len([l for l in leads if 'ULTRA HIGH' in l.priority_level]),
                    'high': len([l for l in leads if 'HIGH' in l.priority_level and 'ULTRA' not in l.priority_level]),
                    'medium': len([l for l in leads if 'MEDIUM' in l.priority_level]),
                    'low': len([l for l in leads if 'LOW' in l.priority_level])
                }
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return filename

def main():
    """Execute stack economics lead generation"""
    engine = StackEconomicsEngine()
    
    try:
        leads = engine.generate_stack_economics_leads()
        
        if leads:
            filename = engine.export_results(leads)
            
            print(f"\n🎯 STACK ECONOMICS ANALYSIS COMPLETE")
            print(f"✅ {len(leads)} qualified leads for R$ 1,997 package")
            print(f"📁 Results: {filename}")
            
            # Executive summary
            total_waste = sum(lead.monthly_stack_waste for lead in leads)
            avg_roi = sum(lead.roi_months for lead in leads) / len(leads)
            total_revenue = len(leads) * 1997
            
            print(f"\n💰 ECONOMICS SUMMARY:")
            print(f"• Total monthly waste identified: R$ {total_waste:,}")
            print(f"• Total annual savings potential: R$ {total_waste * 12:,}")
            print(f"• Average ROI timeline: {avg_roi:.1f} months")
            print(f"• Package revenue potential: R$ {total_revenue:,}")
            
            print(f"\n🏆 TOP QUALIFIED LEADS:")
            for i, lead in enumerate(leads, 1):
                print(f"{i}. {lead.name}")
                print(f"   ROI: {lead.roi_months:.1f} months | Waste: R$ {lead.monthly_stack_waste}/month | {lead.priority_level}")
                print(f"   Employees: ~{lead.estimated_employees} | Complexity: {lead.migration_complexity}")
                
        else:
            print("❌ No leads qualified for R$ 1,997 package with current criteria")
            print("💡 Consider:")
            print("   • Reduce minimum monthly waste threshold")
            print("   • Expand to other MG cities")
            print("   • Adjust ROI requirements")
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
