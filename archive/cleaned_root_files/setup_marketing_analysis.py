"""
PIPELINE PARA ANALISAR OS LEADS REAIS DO APOLLO

Este script aplica o sistema de marketing analysis aos seus prospects reais
exportados do Apollo, focando em empresas brasileiras de e-commerce/retail.
"""

import asyncio
import sys
import os
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional
import json

# Add the arco directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'arco'))

from arco.engines.priority_engine import PriorityEngine, PriorityScore
from arco.engines.outreach_engine import OutreachEngine, OutreachContent
from arco.integrations.google_analytics import GoogleAnalyticsIntegration


@dataclass
class ApolloProspect:
    """Prospect model based on your Apollo export data."""
    company_name: str
    domain: str
    website: str = ""
    industry: str = ""
    employee_count: int = 0
    revenue: int = 0
    technologies: List[str] = None
    funding_stage: str = ""
    last_funding_date: Optional[datetime] = None
    job_postings_count: int = 0
    traffic_growth_rate: float = 0.0
    contact_email: str = ""
    decision_maker_emails: List[str] = None
    marketing_data: Optional[object] = None
    
    # Apollo-specific fields
    apollo_account_id: str = ""
    company_description: str = ""
    founded_year: Optional[int] = None
    company_address: str = ""
    company_phone: str = ""
    keywords: str = ""

    def __post_init__(self):
        if self.technologies is None:
            self.technologies = []
        if self.decision_maker_emails is None:
            self.decision_maker_emails = []
        if not self.website:
            self.website = f"https://{self.domain}"


def load_apollo_prospects() -> List[ApolloProspect]:
    """Load prospects from your Apollo CSV export."""
    try:
        # Read the consolidated prospects CSV
        df = pd.read_csv('arco/consolidated_prospects.csv')
        
        prospects = []
        
        for _, row in df.iterrows():
            # Extract domain from website
            website = str(row.get('Website', '')).strip()
            if website and website != 'nan':
                # Clean up domain
                domain = website.replace('http://', '').replace('https://', '').replace('www.', '')
                if '/' in domain:
                    domain = domain.split('/')[0]
            else:
                continue  # Skip if no website
            
            # Parse technologies
            tech_str = str(row.get('Technologies', ''))
            technologies = []
            if tech_str and tech_str != 'nan':
                technologies = [tech.strip() for tech in tech_str.split(',')]
            
            # Parse employee count
            employee_count = 0
            emp_str = str(row.get('# Employees', ''))
            if emp_str and emp_str != 'nan':
                try:
                    employee_count = int(emp_str)
                except:
                    employee_count = 0
            
            # Parse founded year
            founded_year = None
            founded_str = str(row.get('Founded Year', ''))
            if founded_str and founded_str != 'nan':
                try:
                    founded_year = int(float(founded_str))
                except:
                    founded_year = None
            
            # Create prospect
            prospect = ApolloProspect(
                company_name=str(row.get('Company', '')).strip(),
                domain=domain,
                website=website,
                industry=str(row.get('Industry', '')).strip().lower(),
                employee_count=employee_count,
                revenue=0,  # Not available in Apollo export
                technologies=technologies,
                funding_stage="unknown",
                contact_email=str(row.get('Account Owner', '')).strip(),
                apollo_account_id=str(row.get('Apollo Account Id', '')),
                company_description=str(row.get('Short Description', '')).strip(),
                founded_year=founded_year,
                company_address=str(row.get('Company Address', '')).strip(),
                company_phone=str(row.get('Company Phone', '')).strip(),
                keywords=str(row.get('Keywords', '')).strip()
            )
            
            # Estimate some missing data based on available info
            if prospect.founded_year and prospect.founded_year > 2015:
                prospect.traffic_growth_rate = 0.15  # Newer companies likely growing
            
            # Estimate job postings based on company size
            if prospect.employee_count > 50:
                prospect.job_postings_count = max(1, prospect.employee_count // 10)
            elif prospect.employee_count > 10:
                prospect.job_postings_count = 2
            else:
                prospect.job_postings_count = 1
            
            prospects.append(prospect)
        
        return prospects
        
    except Exception as e:
        print(f"Error loading Apollo prospects: {e}")
        return []


async def analyze_apollo_prospects():
    """Analyze your real Apollo prospects with the marketing system."""
    print("🚀 ANÁLISE DOS SEUS LEADS REAIS DO APOLLO")
    print("=" * 80)
    print("Aplicando o sistema de marketing analysis aos seus prospects brasileiros")
    print()
    
    # Step 1: Load your real prospects
    prospects = load_apollo_prospects()
    
    if not prospects:
        print("❌ Não foi possível carregar os prospects do Apollo")
        return
    
    print(f"📊 CARREGADOS {len(prospects)} PROSPECTS REAIS DO APOLLO:")
    print("-" * 60)
    for i, prospect in enumerate(prospects[:10], 1):  # Show first 10
        print(f"   {i:2d}. {prospect.company_name:<25} | {prospect.domain:<20} | {prospect.industry}")
    
    if len(prospects) > 10:
        print(f"   ... e mais {len(prospects) - 10} prospects")
    print()
    
    # Step 2: Priority scoring
    print("🎯 STEP 1: PRIORITY SCORING DOS SEUS LEADS")
    print("-" * 50)
    
    try:
        priority_engine = PriorityEngine()
    except:
        priority_engine = PriorityEngine.__new__(PriorityEngine)
        priority_engine.scoring_weights = {
            "company_size": 0.25,
            "revenue_potential": 0.30,
            "technology_maturity": 0.20,
            "growth_indicators": 0.15,
            "contact_accessibility": 0.10
        }
        priority_engine.industry_criteria = {}
    
    scored_prospects = await priority_engine.score_batch(prospects)
    
    # Get top 20% for analysis (more realistic for your leads)
    top_prospects = priority_engine.get_top_percentage(scored_prospects, percentage=0.2)
    
    print(f"✅ Scored {len(prospects)} prospects")
    print(f"🎯 TOP {len(top_prospects)} PROSPECTS (20% mais promissores):")
    
    for i, (prospect, score) in enumerate(top_prospects, 1):
        print(f"   {i:2d}. {prospect.company_name:<25} | Score: {score.total_score:5.1f} | {score.priority_tier}")
    print()
    
    # Step 3: Marketing analysis for top prospects
    print(f"🔍 STEP 2: ANÁLISE DE MARKETING DOS TOP {len(top_prospects)} LEADS")
    print("-" * 50)
    
    ga_integration = GoogleAnalyticsIntegration()
    analyzed_prospects = []
    
    for i, (prospect, priority_score) in enumerate(top_prospects, 1):
        print(f"📊 {i}/{len(top_prospects)} - Analisando {prospect.company_name} ({prospect.domain})...")
        
        try:
            # Collect real web vitals
            web_vitals = await ga_integration.get_web_vitals(prospect.domain)
            
            # Collect technical analysis
            technical_analysis = await ga_integration.get_technical_performance_analysis(prospect.domain)
            
            result = {
                "prospect": prospect,
                "priority_score": priority_score,
                "web_vitals": web_vitals,
                "technical_analysis": technical_analysis,
                "analysis_success": bool(web_vitals or technical_analysis)
            }
            
            if web_vitals:
                print(f"   ✅ Web Vitals: LCP={web_vitals.lcp:.2f}s")
            
            if technical_analysis:
                score = technical_analysis.get("performance_score", 0)
                grade = technical_analysis.get("performance_grade", "Unknown")
                print(f"   ✅ Performance: {score}/100 ({grade})")
            
            analyzed_prospects.append(result)
            
        except Exception as e:
            print(f"   ⚠️ Erro na análise: {e}")
            analyzed_prospects.append({
                "prospect": prospect,
                "priority_score": priority_score,
                "web_vitals": None,
                "technical_analysis": None,
                "analysis_success": False,
                "error": str(e)
            })
        
        print()
    
    # Step 4: Generate outreach for successful analyses
    print("📧 STEP 3: GERAÇÃO DE OUTREACH PERSONALIZADO")
    print("-" * 50)
    
    outreach_engine = OutreachEngine()
    final_results = []
    
    successful_analyses = [r for r in analyzed_prospects if r.get("analysis_success")]
    
    print(f"🎯 Gerando outreach para {len(successful_analyses)} prospects com dados coletados:")
    print()
    
    for i, result in enumerate(successful_analyses, 1):
        prospect = result["prospect"]
        priority_score = result["priority_score"]
        web_vitals = result["web_vitals"]
        technical_analysis = result["technical_analysis"]
        
        print(f"🎯 {i}. {prospect.company_name.upper()}")
        print(f"{'='*60}")
        
        # Company info
        print(f"📊 Informações da Empresa:")
        print(f"   • Nome: {prospect.company_name}")
        print(f"   • Website: {prospect.website}")
        print(f"   • Indústria: {prospect.industry}")
        print(f"   • Funcionários: {prospect.employee_count}")
        print(f"   • Fundada: {prospect.founded_year or 'N/A'}")
        print(f"   • Localização: {prospect.company_address}")
        
        # Technical analysis
        if technical_analysis:
            print(f"\n🔧 Análise Técnica (DADOS REAIS):")
            print(f"   • Performance Score: {technical_analysis.get('performance_score', 0)}/100")
            print(f"   • Performance Grade: {technical_analysis.get('performance_grade', 'Unknown')}")
            
            issues = technical_analysis.get("technical_issues", [])
            if issues:
                print(f"   • Problemas Técnicos: {len(issues)} identificados")
                for issue in issues[:2]:
                    print(f"     - {issue}")
            
            opportunities = technical_analysis.get("optimization_opportunities", [])
            if opportunities:
                print(f"   • Oportunidades: {len(opportunities)} identificadas")
                for opp in opportunities[:2]:
                    print(f"     - {opp}")
        
        # Business opportunity
        if web_vitals and web_vitals.lcp:
            print(f"\n💰 Oportunidade de Negócio:")
            print(f"   • LCP Atual: {web_vitals.lcp:.2f}s")
            
            if web_vitals.lcp > 2.5:
                delay = web_vitals.lcp - 2.5
                print(f"   • Delay de Performance: {delay:.1f}s além do ideal")
                print(f"   • Impacto: Degradação da experiência do usuário")
                print(f"   • Oportunidade: Otimização de velocidade da página")
            else:
                print(f"   • Performance excelente - foco em eficiência")
        
        # Generate outreach
        print(f"\n📧 Outreach Personalizado:")
        try:
            outreach_content = await outreach_engine.generate_outreach(
                prospect=prospect,
                priority_score=priority_score
            )
            
            print(f"   Assunto: {outreach_content.subject_line}")
            print(f"   Abertura: {outreach_content.opening_hook[:100]}...")
            
            if outreach_content.specific_insights:
                print(f"   Insights Chave:")
                for insight in outreach_content.specific_insights[:2]:
                    print(f"     • {insight}")
            
        except Exception as e:
            print(f"   ⚠️ Erro na geração de outreach: {e}")
        
        final_results.append(result)
        print()
    
    # Step 5: Summary and next steps
    print("📋 RESUMO EXECUTIVO - SEUS LEADS DO APOLLO")
    print("=" * 80)
    
    successful_count = len(successful_analyses)
    total_count = len(prospects)
    
    print(f"📊 Resultados da Análise:")
    print(f"   • Total de Prospects Analisados: {total_count}")
    print(f"   • Top 20% Selecionados: {len(top_prospects)}")
    print(f"   • Análises Técnicas Bem-sucedidas: {successful_count}")
    print(f"   • Taxa de Sucesso: {(successful_count/len(top_prospects))*100:.1f}%")
    
    # Performance insights
    if successful_analyses:
        performance_scores = []
        slow_sites = []
        
        for result in successful_analyses:
            if result["technical_analysis"]:
                score = result["technical_analysis"].get("performance_score", 0)
                performance_scores.append(score)
            
            if result["web_vitals"] and result["web_vitals"].lcp > 3.0:
                slow_sites.append(result["prospect"])
        
        if performance_scores:
            avg_performance = sum(performance_scores) / len(performance_scores)
            print(f"\n🔧 Insights Técnicos:")
            print(f"   • Performance Média: {avg_performance:.1f}/100")
            print(f"   • Sites com Performance Crítica: {len(slow_sites)}")
        
        if slow_sites:
            print(f"\n🎯 Oportunidades Imediatas:")
            for site in slow_sites[:3]:
                print(f"   • {site.company_name}: Otimização de performance necessária")
    
    print(f"\n🚀 PRÓXIMOS PASSOS:")
    print(f"   1. Focar outreach nos {successful_count} prospects com dados coletados")
    print(f"   2. Usar insights técnicos reais nas conversas")
    print(f"   3. Priorizar empresas com problemas de performance identificados")
    print(f"   4. Expandir análise para mais prospects do Apollo")
    
    # Save results
    summary = {
        "analysis_date": datetime.now().isoformat(),
        "data_source": "apollo_export",
        "total_prospects": total_count,
        "analyzed_prospects": len(top_prospects),
        "successful_analyses": successful_count,
        "results": [
            {
                "company_name": r["prospect"].company_name,
                "domain": r["prospect"].domain,
                "industry": r["prospect"].industry,
                "priority_score": r["priority_score"].total_score,
                "performance_score": r["technical_analysis"].get("performance_score", 0) if r["technical_analysis"] else 0,
                "lcp_seconds": r["web_vitals"].lcp if r["web_vitals"] else None,
                "analysis_success": r["analysis_success"]
            }
            for r in analyzed_prospects
        ]
    }
    
    with open("apollo_analysis_results.json", "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em 'apollo_analysis_results.json'")
    
    # Close session
    if ga_integration.session and not ga_integration.session.closed:
        await ga_integration.session.close()
    
    return final_results


if __name__ == "__main__":
    # Run analysis on your real Apollo prospects
    print("🚀 Iniciando análise dos seus leads reais do Apollo")
    results = asyncio.run(analyze_apollo_prospects())
    
    print(f"\n✅ ANÁLISE DOS SEUS LEADS APOLLO CONCLUÍDA!")
    if results:
        print(f"🎯 {len(results)} prospects analisados com dados reais")
        print(f"📧 Outreach personalizado gerado para cada prospect")
        print(f"🔧 Foco em oportunidades técnicas identificadas")
    else:
        print(f"⚠️ Verifique o arquivo CSV e tente novamente")