#!/usr/bin/env python3
"""
📊 CRM EXPORT MANAGER - QUALIFIED LEADS ORGANIZATION
Sistema maduro para organização e enriquecimento de prospects qualificados
Costa Oeste Norte-Americana: Canadá + EUA Cross-Border
"""

import csv
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

class CRMExportManager:
    """
    Gerenciador de exportação de leads qualificados para CRM
    Com preparação para enriquecimento BigQuery
    """
    
    def __init__(self):
        self.export_path = Path("exports/crm")
        self.export_path.mkdir(parents=True, exist_ok=True)
        
    def organize_qualified_leads(self, discovery_results: Dict) -> Dict:
        """
        Organiza leads qualificados por prioridade e mercado para CRM
        """
        prospects = discovery_results.get('top_prospects', [])
        
        if not prospects:
            print("❌ No qualified prospects to organize")
            return {}
        
        # Organização estratégica por prioridade
        organized_leads = {
            'tier_1_immediate': [],    # Top prospects - ação imediata
            'tier_2_priority': [],     # High-value prospects - 48h
            'tier_3_pipeline': [],     # Pipeline prospects - 1 semana
            'metadata': {
                'total_prospects': len(prospects),
                'export_timestamp': datetime.now().isoformat(),
                'market_focus': 'north_america_west',
                'currency_primary': 'CAD',
                'currency_secondary': 'USD'
            }
        }
        
        for prospect in prospects:
            # Classificação por Tier baseada em fit score e impact
            fit_score = prospect.get('overall_fit_score', 0)
            monthly_impact = prospect.get('estimated_monthly_impact', 0)
            monthly_revenue = prospect.get('estimated_monthly_revenue', 0)
            
            # Tier 1: Top performance (Fit > 0.85 + Impact > $150 OU Revenue > $80k/mês)
            if (fit_score > 0.85 and monthly_impact > 150) or monthly_revenue > 80000:
                organized_leads['tier_1_immediate'].append(prospect)
            
            # Tier 2: High potential (Fit > 0.80 + Impact > $90 OU Revenue > $40k/mês)
            elif (fit_score > 0.80 and monthly_impact > 90) or monthly_revenue > 40000:
                organized_leads['tier_2_priority'].append(prospect)
            
            # Tier 3: Pipeline (resto dos qualificados)
            else:
                organized_leads['tier_3_pipeline'].append(prospect)
        
        # Sort each tier by fit score
        for tier in ['tier_1_immediate', 'tier_2_priority', 'tier_3_pipeline']:
            organized_leads[tier].sort(key=lambda x: x['overall_fit_score'], reverse=True)
        
        print(f"\n📊 LEAD ORGANIZATION SUMMARY:")
        print(f"🔥 Tier 1 (Immediate): {len(organized_leads['tier_1_immediate'])} prospects")
        print(f"⚡ Tier 2 (Priority): {len(organized_leads['tier_2_priority'])} prospects")
        print(f"📈 Tier 3 (Pipeline): {len(organized_leads['tier_3_pipeline'])} prospects")
        
        return organized_leads
    
    def export_to_crm_csv(self, organized_leads: Dict) -> str:
        """
        Exporta leads organizados para CSV otimizado para CRM
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"qualified_leads_north_america_west_{timestamp}.csv"
        csv_path = self.export_path / csv_filename
        
        # Preparar dados para CSV com colunas estratégicas
        csv_data = []
        
        for tier_name, prospects in organized_leads.items():
            if tier_name == 'metadata':
                continue
                
            # Mapear tier para prioridade numérica
            priority_mapping = {
                'tier_1_immediate': 1,
                'tier_2_priority': 2, 
                'tier_3_pipeline': 3
            }
            
            for prospect in prospects:
                # Preparar row otimizada para CRM
                row = self._prepare_crm_row(prospect, priority_mapping[tier_name])
                csv_data.append(row)
        
        # Escrever CSV com colunas otimizadas
        fieldnames = [
            # Identificação
            'company_name', 'domain', 'website_clean', 'priority_tier', 'tier_name',
            
            # Negócio
            'business_type', 'market_region', 'estimated_employees', 'currency',
            
            # Financeiro (valores em formato CRM-friendly)
            'monthly_revenue_display', 'monthly_revenue_numeric', 
            'monthly_marketing_spend_display', 'monthly_marketing_spend_numeric',
            'opportunity_value_display', 'opportunity_value_numeric',
            
            # Scoring e Confiança
            'overall_fit_score', 'size_confidence', 'revenue_confidence', 
            'marketing_confidence', 'opportunity_confidence',
            
            # Oportunidade
            'opportunity_type', 'discovery_query_type',
            
            # Enriquecimento BigQuery (campos preparados)
            'bigquery_domain_key', 'bigquery_enrichment_status', 'bigquery_last_update',
            
            # CRM Management
            'lead_status', 'assigned_to', 'contact_priority', 'follow_up_date',
            'notes', 'created_date', 'last_modified'
        ]
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_data)
        
        print(f"\n💾 CRM CSV exported: {csv_path}")
        print(f"📊 Total records: {len(csv_data)}")
        
        # Gerar resumo por tier
        self._generate_export_summary(csv_data, csv_path)
        
        return str(csv_path)
    
    def _prepare_crm_row(self, prospect: Dict, priority: int) -> Dict:
        """
        Prepara uma linha otimizada para CRM com todos os campos necessários
        """
        # Detectar moeda e região
        monthly_revenue = prospect.get('estimated_monthly_revenue', 0)
        monthly_marketing = prospect.get('estimated_monthly_marketing_spend', 0)
        opportunity_value = prospect.get('estimated_monthly_impact', 0)
        
        # Determinar moeda baseada no contexto
        business_type = prospect.get('business_type', '')
        company_name = prospect.get('company_name', '')
        domain = prospect.get('domain', '')
        
        # Detectar se é Canadá ou EUA
        is_canadian = (
            '.ca' in domain.lower() or 
            any(city in company_name.lower() for city in ['vancouver', 'toronto', 'calgary', 'montreal', 'ottawa']) or
            'ca' in domain.lower()
        )
        
        currency = 'CAD' if is_canadian else 'USD'
        market_region = 'Canada' if is_canadian else 'USA_CrossBorder'
        
        # Determinar tipo de query para classificação
        discovery_query = prospect.get('discovery_query', '')
        if 'book appointment' in discovery_query:
            query_type = 'booking_optimization'
        elif 'consultation' in discovery_query:
            query_type = 'consultation_conversion'
        elif 'law firm' in discovery_query:
            query_type = 'legal_services'
        elif 'accounting' in discovery_query:
            query_type = 'accounting_services'
        else:
            query_type = 'general_services'
        
        # Calcular follow-up date baseado na prioridade
        follow_up_days = {1: 1, 2: 2, 3: 7}  # Tier 1: 1 dia, Tier 2: 2 dias, Tier 3: 1 semana
        follow_up_date = (datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + 
                         pd.Timedelta(days=follow_up_days[priority])).isoformat()
        
        # Preparar domain key para BigQuery
        bigquery_domain_key = domain.lower().replace('www.', '') if domain else ''
        
        return {
            # Identificação
            'company_name': prospect.get('company_name', ''),
            'domain': domain,
            'website_clean': f"https://{domain}" if domain and not domain.startswith('http') else domain,
            'priority_tier': priority,
            'tier_name': f"Tier {priority} - {'Immediate' if priority == 1 else 'Priority' if priority == 2 else 'Pipeline'}",
            
            # Negócio
            'business_type': business_type.title().replace('_', ' '),
            'market_region': market_region,
            'estimated_employees': prospect.get('estimated_employees', 0),
            'currency': currency,
            
            # Financeiro
            'monthly_revenue_display': f"{currency} ${monthly_revenue:,.0f}",
            'monthly_revenue_numeric': monthly_revenue,
            'monthly_marketing_spend_display': f"{currency} ${monthly_marketing:,.0f}",
            'monthly_marketing_spend_numeric': monthly_marketing,
            'opportunity_value_display': f"{currency} ${opportunity_value:,.0f}",
            'opportunity_value_numeric': opportunity_value,
            
            # Scoring
            'overall_fit_score': prospect.get('overall_fit_score', 0),
            'size_confidence': prospect.get('size_confidence', 0),
            'revenue_confidence': prospect.get('revenue_confidence', 0),
            'marketing_confidence': prospect.get('marketing_confidence', 0),
            'opportunity_confidence': prospect.get('opportunity_confidence', 0),
            
            # Oportunidade
            'opportunity_type': prospect.get('opportunity_type', ''),
            'discovery_query_type': query_type,
            
            # BigQuery preparação
            'bigquery_domain_key': bigquery_domain_key,
            'bigquery_enrichment_status': 'pending',
            'bigquery_last_update': '',
            
            # CRM Management
            'lead_status': 'new',
            'assigned_to': '',  # Para ser preenchido pelo CRM
            'contact_priority': 'high' if priority == 1 else 'medium' if priority == 2 else 'normal',
            'follow_up_date': follow_up_date,
            'notes': f"Discovered via {query_type}. Fit score: {prospect.get('overall_fit_score', 0):.2f}",
            'created_date': datetime.now().isoformat(),
            'last_modified': datetime.now().isoformat()
        }
    
    def _generate_export_summary(self, csv_data: List[Dict], csv_path: Path) -> None:
        """
        Gera resumo executivo da exportação
        """
        summary_path = csv_path.with_suffix('.summary.txt')
        
        # Análise dos dados
        total_prospects = len(csv_data)
        tier_1_count = len([r for r in csv_data if r['priority_tier'] == 1])
        tier_2_count = len([r for r in csv_data if r['priority_tier'] == 2])
        tier_3_count = len([r for r in csv_data if r['priority_tier'] == 3])
        
        # Análise por vertical
        business_types = {}
        market_regions = {}
        total_opportunity_value = 0
        
        for row in csv_data:
            # Business types
            bt = row['business_type']
            business_types[bt] = business_types.get(bt, 0) + 1
            
            # Market regions
            mr = row['market_region']
            market_regions[mr] = market_regions.get(mr, 0) + 1
            
            # Total opportunity
            total_opportunity_value += row.get('opportunity_value_numeric', 0)
        
        # Escrever resumo
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("🎯 CRM EXPORT SUMMARY - NORTH AMERICA WEST COAST\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"📊 LEAD DISTRIBUTION:\n")
            f.write(f"   🔥 Tier 1 (Immediate): {tier_1_count} prospects\n")
            f.write(f"   ⚡ Tier 2 (Priority):  {tier_2_count} prospects\n")
            f.write(f"   📈 Tier 3 (Pipeline):  {tier_3_count} prospects\n")
            f.write(f"   📋 Total:              {total_prospects} prospects\n\n")
            
            f.write(f"🌍 MARKET DISTRIBUTION:\n")
            for region, count in sorted(market_regions.items()):
                percentage = (count / total_prospects) * 100
                f.write(f"   {region}: {count} prospects ({percentage:.1f}%)\n")
            
            f.write(f"\n🏢 BUSINESS TYPE DISTRIBUTION:\n")
            for business_type, count in sorted(business_types.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_prospects) * 100
                f.write(f"   {business_type}: {count} prospects ({percentage:.1f}%)\n")
            
            f.write(f"\n💰 PIPELINE VALUE:\n")
            f.write(f"   Total Monthly Opportunity: ${total_opportunity_value:,.0f}\n")
            f.write(f"   Average per Prospect: ${total_opportunity_value/total_prospects:,.0f}\n")
            
            f.write(f"\n📅 FOLLOW-UP SCHEDULE:\n")
            f.write(f"   Tomorrow: {tier_1_count} immediate prospects\n")
            f.write(f"   48h: {tier_2_count} priority prospects\n")
            f.write(f"   7 days: {tier_3_count} pipeline prospects\n")
            
            f.write(f"\n🔧 BIGQUERY ENRICHMENT:\n")
            f.write(f"   Ready for enrichment: {total_prospects} domains\n")
            f.write(f"   Status: pending\n")
            f.write(f"   Next step: Run BigQuery enrichment pipeline\n")
            
            f.write(f"\n📁 FILES GENERATED:\n")
            f.write(f"   CRM CSV: {csv_path.name}\n")
            f.write(f"   Summary: {summary_path.name}\n")
            f.write(f"   Export timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print(f"📋 Export summary: {summary_path}")
    
    def prepare_bigquery_enrichment_config(self, csv_path: str) -> Dict:
        """
        Prepara configuração para enriquecimento BigQuery
        """
        config = {
            'source_csv': csv_path,
            'enrichment_fields': [
                'website_performance_score',
                'mobile_performance_score',
                'seo_authority_score',
                'social_media_presence',
                'technology_stack',
                'estimated_monthly_traffic',
                'competitor_analysis',
                'local_search_ranking',
                'review_score_aggregate',
                'business_registration_data'
            ],
            'bigquery_tables': [
                'prospects_enriched',
                'website_performance_metrics',
                'competitive_intelligence',
                'local_market_data'
            ],
            'matching_strategy': 'domain_based',
            'confidence_threshold': 0.7,
            'update_strategy': 'append_new_enrich_existing'
        }
        
        # Salvar config
        config_path = Path(csv_path).with_suffix('.bigquery_config.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"🔧 BigQuery config: {config_path}")
        return config

def export_discovery_to_crm(discovery_results_path: str) -> str:
    """
    Função principal para exportar resultados de discovery para CRM
    """
    # Carregar resultados de discovery
    with open(discovery_results_path, 'r', encoding='utf-8') as f:
        discovery_results = json.load(f)
    
    # Inicializar gerenciador de exportação
    crm_manager = CRMExportManager()
    
    # Organizar leads
    organized_leads = crm_manager.organize_qualified_leads(discovery_results)
    
    if not organized_leads or not any(organized_leads.get(tier, []) for tier in ['tier_1_immediate', 'tier_2_priority', 'tier_3_pipeline']):
        print("❌ No leads to export")
        return ""
    
    # Exportar para CSV
    csv_path = crm_manager.export_to_crm_csv(organized_leads)
    
    # Preparar configuração BigQuery
    bigquery_config = crm_manager.prepare_bigquery_enrichment_config(csv_path)
    
    return csv_path

if __name__ == "__main__":
    # Buscar o arquivo de discovery mais recente
    discovery_files = list(Path("src/data").glob("pragmatic_discovery_north_america_west_*.json"))
    
    if discovery_files:
        latest_file = max(discovery_files, key=lambda x: x.stat().st_mtime)
        print(f"📂 Using discovery file: {latest_file}")
        
        csv_export = export_discovery_to_crm(str(latest_file))
        
        if csv_export:
            print(f"\n✅ CRM export completed successfully!")
            print(f"📊 CSV file: {csv_export}")
            print(f"🔧 Ready for BigQuery enrichment")
        else:
            print("❌ Export failed")
    else:
        print("❌ No discovery files found. Run pragmatic_discovery.py first.")
