"""
Exemplo de execução do pipeline ARCO com dados do Apollo.

Este script implementa a primeira parte do plano de execução do pipeline ARCO,
focando na importação e análise inicial dos dados do Apollo.
"""

import sys
import os
import json
from datetime import datetime
import asyncio
from typing import Dict, List, Any

# Adicionar o diretório pai ao Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from arco.integrations.apollo_csv import ApolloCSVIntegration
from arco.models.icp import ShopifyDTCPremiumICP, HealthSupplementsICP, FitnessEquipmentICP
from arco.models.financial_leak import FinancialLeakDetector
from arco.models.roi_report import ROIReportGenerator
from arco.engines.discovery_engine import DiscoveryEngine
from arco.integrations.wappalyzer import WappalyzerIntegration
from arco.models.prospect import Technology


async def enrich_prospect(prospect, wappalyzer):
    """
    Enriquece um prospecto com dados do Wappalyzer.
    
    Args:
        prospect: Objeto Prospect a ser enriquecido
        wappalyzer: Instância do WappalyzerIntegration
        
    Returns:
        bool: True se o enriquecimento foi bem-sucedido, False caso contrário
    """
    if prospect.website:
        try:
            tech_data = await wappalyzer.analyze_url(prospect.website)
            
            # Adicionar tecnologias que ainda não existem no prospecto
            existing_tech_names = {tech.name.lower() for tech in prospect.technologies}
            
            for tech_name, tech_info in tech_data.items():
                if tech_name.lower() not in existing_tech_names:
                    category = tech_info.get('category', 'other')
                    version = tech_info.get('version')
                    prospect.technologies.append(Technology(name=tech_name, category=category, version=version))
            
            return True
        except Exception as e:
            print(f"Erro ao enriquecer {prospect.domain}: {e}")
            return False
    return False


async def enrich_prospects_batch(prospects, batch_size=5):
    """
    Enriquece um lote de prospectos com dados do Wappalyzer.
    
    Args:
        prospects: Lista de objetos Prospect a serem enriquecidos
        batch_size: Tamanho do lote para processamento paralelo
        
    Returns:
        List[Prospect]: Lista de prospectos enriquecidos
    """
    # Inicializar integração Wappalyzer
    wappalyzer = WappalyzerIntegration()
    
    enriched_count = 0
    total_techs_before = sum(len(p.technologies) for p in prospects)
    
    # Processar em lotes para evitar sobrecarga
    for i in range(0, len(prospects), batch_size):
        batch = prospects[i:i+batch_size]
        tasks = [enrich_prospect(p, wappalyzer) for p in batch]
        results = await asyncio.gather(*tasks)
        enriched_count += sum(1 for r in results if r)
        print(f"Processado lote {i//batch_size + 1}/{(len(prospects)-1)//batch_size + 1}")
    
    total_techs_after = sum(len(p.technologies) for p in prospects)
    
    print(f"\nEnriquecimento concluído:")
    print(f"- Prospectos enriquecidos: {enriched_count}/{len(prospects)} ({enriched_count/len(prospects):.1%})")
    print(f"- Tecnologias antes: {total_techs_before}")
    print(f"- Tecnologias depois: {total_techs_after}")
    print(f"- Tecnologias adicionadas: {total_techs_after - total_techs_before}")
    print(f"- Média de tecnologias por prospecto: {total_techs_after/len(prospects):.1f}")
    
    return prospects


def analyze_prospect_distribution(prospects):
    """
    Analisa a distribuição dos prospectos por indústria, tamanho e país.
    
    Args:
        prospects: Lista de objetos Prospect
        
    Returns:
        Dict: Estatísticas de distribuição
    """
    industries = {}
    sizes = {"1-10": 0, "11-50": 0, "51-200": 0, "201+": 0}
    countries = {}
    tech_categories = {}
    
    for prospect in prospects:
        # Contagem por indústria
        if prospect.industry:
            industries[prospect.industry] = industries.get(prospect.industry, 0) + 1
        
        # Contagem por tamanho
        if prospect.employee_count:
            if prospect.employee_count <= 10:
                sizes["1-10"] += 1
            elif prospect.employee_count <= 50:
                sizes["11-50"] += 1
            elif prospect.employee_count <= 200:
                sizes["51-200"] += 1
            else:
                sizes["201+"] += 1
        
        # Contagem por país
        if prospect.country:
            countries[prospect.country] = countries.get(prospect.country, 0) + 1
        
        # Contagem por categoria de tecnologia
        for tech in prospect.technologies:
            tech_categories[tech.category] = tech_categories.get(tech.category, 0) + 1
    
    return {
        "industries": industries,
        "sizes": sizes,
        "countries": countries,
        "tech_categories": tech_categories
    }


def analyze_icp_match(prospects, icps):
    """
    Analisa o match dos prospectos com os ICPs definidos.
    
    Args:
        prospects: Lista de objetos Prospect
        icps: Dicionário de ICPs
        
    Returns:
        Dict: Resultados da análise de ICP
    """
    icp_results = {}
    
    for icp_name, icp in icps.items():
        # Criar engine com o ICP
        engine = DiscoveryEngine(icp=icp)
        
        # Filtrar prospectos qualificados
        qualified_prospects = engine._filter_prospects_by_icp(prospects)
        
        # Calcular scores para todos os prospectos
        all_scores = []
        for prospect in prospects:
            score = icp.calculate_match_score(prospect)
            all_scores.append(score)
        
        # Calcular métricas
        icp_results[icp_name] = {
            "icp_name": icp.name,
            "total_prospects": len(prospects),
            "qualified_prospects": len(qualified_prospects),
            "qualification_rate": len(qualified_prospects) / len(prospects) if prospects else 0,
            "avg_match_score": sum(all_scores) / len(all_scores) if all_scores else 0,
            "score_distribution": {
                "0-25": sum(1 for s in all_scores if s < 25),
                "25-50": sum(1 for s in all_scores if 25 <= s < 50),
                "50-75": sum(1 for s in all_scores if 50 <= s < 75),
                "75-100": sum(1 for s in all_scores if s >= 75)
            },
            "qualified_list": qualified_prospects
        }
    
    return icp_results


def analyze_financial_leaks(qualified_prospects_by_icp):
    """
    Analisa vazamentos financeiros para prospectos qualificados por ICP.
    
    Args:
        qualified_prospects_by_icp: Dicionário de prospectos qualificados por ICP
        
    Returns:
        Dict: Resultados da análise de vazamentos financeiros
    """
    # Criar detector de vazamentos financeiros
    leak_detector = FinancialLeakDetector()
    
    # Analisar vazamentos para cada ICP
    leak_results_by_icp = {}
    
    for icp_name, results in qualified_prospects_by_icp.items():
        qualified_prospects = results["qualified_list"]
        
        # Inicializar resultados para este ICP
        leak_results_by_icp[icp_name] = {
            "icp_name": results["icp_name"],
            "total_prospects": len(qualified_prospects),
            "total_monthly_waste": 0.0,
            "total_annual_waste": 0.0,
            "total_monthly_savings": 0.0,
            "total_annual_savings": 0.0,
            "avg_roi_percentage": 0.0,
            "redundancy_types": {},
            "prospect_results": []
        }
        
        # Analisar cada prospecto
        roi_percentages = []
        
        for prospect in qualified_prospects:
            # Detectar vazamentos financeiros
            leak_result = leak_detector.detect_financial_leaks(prospect)
            summary = leak_result["summary"]
            
            # Adicionar ao total
            leak_results_by_icp[icp_name]["total_monthly_waste"] += summary["total_monthly_waste"]
            leak_results_by_icp[icp_name]["total_annual_waste"] += summary["total_annual_waste"]
            leak_results_by_icp[icp_name]["total_monthly_savings"] += summary["total_monthly_savings"]
            leak_results_by_icp[icp_name]["total_annual_savings"] += summary["total_annual_savings"]
            
            # Adicionar ROI percentage à lista para cálculo de média
            if summary["roi_percentage"] > 0:
                roi_percentages.append(summary["roi_percentage"])
            
            # Contar tipos de redundância
            if "redundant_apps" in leak_result and leak_result["redundant_apps"]["redundancies_detected"]:
                for pattern in leak_result["redundant_apps"]["patterns_matched"]:
                    pattern_name = pattern["name"]
                    leak_results_by_icp[icp_name]["redundancy_types"][pattern_name] = leak_results_by_icp[icp_name]["redundancy_types"].get(pattern_name, 0) + 1
            
            # Adicionar resultado individual
            leak_results_by_icp[icp_name]["prospect_results"].append({
                "domain": prospect.domain,
                "company_name": prospect.company_name,
                "monthly_waste": summary["total_monthly_waste"],
                "annual_waste": summary["total_annual_waste"],
                "monthly_savings": summary["total_monthly_savings"],
                "annual_savings": summary["total_annual_savings"],
                "roi_percentage": summary["roi_percentage"]
            })
        
        # Calcular média de ROI
        if roi_percentages:
            leak_results_by_icp[icp_name]["avg_roi_percentage"] = sum(roi_percentages) / len(roi_percentages)
        
        # Ordenar prospectos por economia anual
        leak_results_by_icp[icp_name]["prospect_results"].sort(key=lambda x: x["annual_savings"], reverse=True)
    
    return leak_results_by_icp


def generate_roi_reports(leak_results_by_icp, prospects, limit=5):
    """
    Gera relatórios de ROI para os prospectos com maior potencial de economia.
    
    Args:
        leak_results_by_icp: Resultados da análise de vazamentos financeiros por ICP
        prospects: Lista completa de prospectos
        limit: Número máximo de relatórios por ICP
        
    Returns:
        Dict: Estatísticas dos relatórios gerados
    """
    # Criar gerador de relatórios ROI
    report_generator = ROIReportGenerator()
    
    # Criar diretório para relatórios
    reports_dir = "apollo_roi_reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    # Gerar relatórios para cada ICP
    report_stats = {}
    
    for icp_name, results in leak_results_by_icp.items():
        # Criar subdiretório para este ICP
        icp_dir = os.path.join(reports_dir, icp_name)
        os.makedirs(icp_dir, exist_ok=True)
        
        # Inicializar estatísticas
        report_stats[icp_name] = {
            "icp_name": results["icp_name"],
            "reports_generated": 0,
            "total_annual_savings": 0.0,
            "avg_annual_savings": 0.0,
            "recommendation_types": {},
            "report_paths": []
        }
        
        # Gerar relatórios para os top prospectos
        top_prospects = results["prospect_results"][:limit]
        
        for prospect_result in top_prospects:
            # Encontrar o objeto Prospect correspondente
            prospect = next((p for p in prospects if p.domain == prospect_result["domain"]), None)
            
            if prospect:
                # Gerar relatório
                report = report_generator.generate_roi_report(prospect)
                
                # Salvar relatório
                filepath = report_generator.save_report_to_file(report, icp_dir)
                
                # Gerar versão HTML
                html_content = report_generator.generate_html_report(report)
                html_filepath = filepath.replace(".md", ".html")
                with open(html_filepath, "w", encoding="utf-8") as f:
                    f.write(html_content)
                
                # Atualizar estatísticas
                report_stats[icp_name]["reports_generated"] += 1
                report_stats[icp_name]["total_annual_savings"] += prospect_result["annual_savings"]
                report_stats[icp_name]["report_paths"].append(filepath)
                
                # Contar tipos de recomendação
                for rec in report["financial_leaks"]["priority_recommendations"]:
                    rec_type = rec.split(":")[0] if ":" in rec else rec
                    report_stats[icp_name]["recommendation_types"][rec_type] = report_stats[icp_name]["recommendation_types"].get(rec_type, 0) + 1
        
        # Calcular média
        if report_stats[icp_name]["reports_generated"] > 0:
            report_stats[icp_name]["avg_annual_savings"] = report_stats[icp_name]["total_annual_savings"] / report_stats[icp_name]["reports_generated"]
    
    return report_stats


def save_analysis_results(distribution, icp_results, leak_results, report_stats):
    """
    Salva os resultados da análise em um arquivo JSON.
    
    Args:
        distribution: Resultados da análise de distribuição
        icp_results: Resultados da análise de ICP
        leak_results: Resultados da análise de vazamentos financeiros
        report_stats: Estatísticas dos relatórios gerados
        
    Returns:
        str: Caminho para o arquivo JSON
    """
    # Criar diretório para resultados
    results_dir = "apollo_analysis_results"
    os.makedirs(results_dir, exist_ok=True)
    
    # Preparar resultados para serialização
    serializable_icp_results = {}
    for icp_name, results in icp_results.items():
        serializable_icp_results[icp_name] = {k: v for k, v in results.items() if k != "qualified_list"}
        serializable_icp_results[icp_name]["qualified_count"] = len(results["qualified_list"])
    
    # Criar objeto de resultados
    analysis_results = {
        "timestamp": datetime.now().isoformat(),
        "distribution": distribution,
        "icp_results": serializable_icp_results,
        "leak_results": {k: {kk: vv for kk, vv in v.items() if kk != "qualified_list"} for k, v in leak_results.items()},
        "report_stats": report_stats
    }
    
    # Salvar resultados
    filepath = os.path.join(results_dir, f"apollo_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(analysis_results, f, indent=2)
    
    return filepath


async def main():
    """Função principal."""
    print("Pipeline ARCO com Dados Apollo")
    print("=============================")
    
    # Fase 1: Importação de Dados
    print("\n--- Fase 1: Importação de Dados ---")
    
    # Inicializar a integração Apollo
    print("\nInicializando integração Apollo...")
    apollo_integration = ApolloCSVIntegration()
    
    # Importar todos os prospectos
    print("\nImportando prospectos do Apollo...")
    prospects = apollo_integration.get_all_prospects()
    print(f"Importados {len(prospects)} prospectos do Apollo")
    
    # Analisar distribuição
    print("\nAnalisando distribuição dos prospectos...")
    distribution = analyze_prospect_distribution(prospects)
    
    # Exibir resultados de distribuição
    print("\nDistribuição por indústria (top 5):")
    for industry, count in sorted(distribution["industries"].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"- {industry}: {count}")
    
    print("\nDistribuição por tamanho:")
    for size, count in distribution["sizes"].items():
        print(f"- {size}: {count}")
    
    print("\nDistribuição por país (top 5):")
    for country, count in sorted(distribution["countries"].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"- {country}: {count}")
    
    # Fase 2: Enriquecimento e Análise
    print("\n--- Fase 2: Enriquecimento e Análise ---")
    
    # Limitar a 20 prospectos para o exemplo
    sample_prospects = prospects[:20]
    print(f"\nUsando amostra de {len(sample_prospects)} prospectos para análise")
    
    # Enriquecer prospectos
    print("\nEnriquecendo prospectos com dados do Wappalyzer...")
    enriched_prospects = await enrich_prospects_batch(sample_prospects)
    
    # Criar ICPs
    print("\nCriando ICPs para análise...")
    icps = {
        "shopify_dtc": ShopifyDTCPremiumICP(),
        "health_supplements": HealthSupplementsICP(),
        "fitness_equipment": FitnessEquipmentICP()
    }
    
    # Analisar match com ICPs
    print("\nAnalisando match com ICPs...")
    icp_results = analyze_icp_match(enriched_prospects, icps)
    
    # Exibir resultados de ICP
    for icp_name, results in icp_results.items():
        print(f"\nResultados para ICP: {results['icp_name']}")
        print(f"- Total de prospectos: {results['total_prospects']}")
        print(f"- Prospectos qualificados: {len(results['qualified_list'])} ({results['qualification_rate']:.1%})")
        print(f"- Score médio: {results['avg_match_score']:.1f}/100")
    
    # Analisar vazamentos financeiros
    print("\nAnalisando vazamentos financeiros...")
    leak_results = analyze_financial_leaks(icp_results)
    
    # Exibir resultados de vazamentos financeiros
    for icp_name, results in leak_results.items():
        if results["total_prospects"] > 0:
            print(f"\nResultados de vazamentos financeiros para ICP: {results['icp_name']}")
            print(f"- Total de prospectos analisados: {results['total_prospects']}")
            print(f"- Desperdício anual total: ${results['total_annual_waste']:,.2f}")
            print(f"- Economia anual total: ${results['total_annual_savings']:,.2f}")
            print(f"- ROI percentual médio: {results['avg_roi_percentage']:.1f}%")
            
            if results["prospect_results"]:
                print("\nTop 3 prospectos com maior potencial de economia:")
                for i, prospect_result in enumerate(results["prospect_results"][:3]):
                    print(f"{i+1}. {prospect_result['company_name']} ({prospect_result['domain']})")
                    print(f"   - Economia anual: ${prospect_result['annual_savings']:,.2f}")
                    print(f"   - ROI: {prospect_result['roi_percentage']:.1f}%")
    
    # Fase 3: Geração de Relatórios
    print("\n--- Fase 3: Geração de Relatórios ---")
    
    # Gerar relatórios de ROI
    print("\nGerando relatórios de ROI...")
    report_stats = generate_roi_reports(leak_results, enriched_prospects, limit=3)
    
    # Exibir estatísticas de relatórios
    for icp_name, stats in report_stats.items():
        if stats["reports_generated"] > 0:
            print(f"\nEstatísticas de relatórios para ICP: {stats['icp_name']}")
            print(f"- Relatórios gerados: {stats['reports_generated']}")
            print(f"- Economia anual total: ${stats['total_annual_savings']:,.2f}")
            print(f"- Economia anual média: ${stats['avg_annual_savings']:,.2f}")
            
            if stats["report_paths"]:
                print("\nRelatórios gerados:")
                for path in stats["report_paths"]:
                    print(f"- {path}")
    
    # Salvar resultados da análise
    print("\nSalvando resultados da análise...")
    results_file = save_analysis_results(distribution, icp_results, leak_results, report_stats)
    print(f"Resultados salvos em: {results_file}")
    
    print("\nPipeline concluído com sucesso!")


if __name__ == "__main__":
    asyncio.run(main())