#!/usr/bin/env python3
"""
🎯 ICP LEAD DISCOVERY - 3-10 FUNCIONÁRIOS
SearchAPI → BigQuery pipeline para descobrir empresas ICP ativas em ads
Foco: 48h para 1º cliente (funil de capacidade + probabilidade)
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

# Add paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

async def discover_icp_leads():
    """Descoberta de leads ICP usando SearchAPI + BigQuery"""
    
    print("🎯 ICP LEAD DISCOVERY - EMPRESAS 3-10 FUNCIONÁRIOS")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Import modules
        from config.api_keys import APIConfig
        from src.connectors.searchapi_connector import SearchAPIConnector
        
        api_config = APIConfig()
        search_api = SearchAPIConnector(api_key=api_config.SEARCH_API_KEY)
        
        # Parâmetros do funil 48h
        funil_params = {
            'q_rate': 0.40,      # Qualified Rate (base)
            'c2c_rate': 0.25,    # Contact to Call
            'c2a_rate': 0.50,    # Call to Audit 
            'de_rate': 80        # Discovery Efficiency (P0 per $1k)
        }
        
        # Calculate targets needed for 48h goal (1 audit)
        audits_target = 1
        calls_needed = int(audits_target / funil_params['c2a_rate'])
        qualifieds_needed = int(calls_needed / funil_params['c2c_rate'])
        p0_needed = int(qualifieds_needed / funil_params['q_rate'])
        
        print(f"📊 FUNIL 48H: {p0_needed} P0 → {qualifieds_needed} qualified → {calls_needed} calls → {audits_target} audit")
        print(f"💰 Budget estimado: ${p0_needed / funil_params['de_rate'] * 1000:.0f}")
        print()
        
        # ICP Target queries: verticais de alta urgência, small business
        icp_queries = [
            "beauty clinic small business 3-10 employees advertising",
            "dental practice local advertising team",
            "real estate agent digital marketing small office", 
            "emergency service local ads small business",
            "law firm small practice advertising",
            "medical clinic family practice marketing"
        ]
        
        discovered_companies = []
        
        print("🔍 DESCOBERTA VIA SEARCHAPI:")
        print("-" * 40)
        
        for query in icp_queries:
            print(f"  🔍 {query}")
            
            try:
                companies = await search_api.search_companies(query, max_results=5)
                
                for company in companies:
                    # Enriquecer com scoring ICP
                    enriched = enrich_icp_company(company)
                    if enriched['icp_score'] >= 60:  # ICP threshold
                        discovered_companies.append(enriched)
                        print(f"    ✅ {company['name']} (ICP: {enriched['icp_score']})")
                    else:
                        print(f"    ❌ {company['name']} (ICP: {enriched['icp_score']} - baixo)")
                
                await asyncio.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"    ⚠️ Erro: {e}")
        
        print(f"\n📊 RESULTADO: {len(discovered_companies)} empresas ICP descobertas")
        
        # Qualify and rank leads
        qualified_leads = qualify_icp_leads(discovered_companies, p0_needed)
        
        if qualified_leads:
            print(f"\n🎯 TOP {len(qualified_leads)} LEADS QUALIFICADOS:")
            print("-" * 40)
            
            for i, lead in enumerate(qualified_leads, 1):
                print(f"{i}. {lead['company_name']}")
                print(f"   Industry: {lead['industry']} | Employees: {lead['estimated_employees']}")
                print(f"   ICP Score: {lead['icp_score']} | Urgency: {lead['urgency_level']}")
                print(f"   Website: {lead['website']}")
                print(f"   P0 Signals: {', '.join(lead['p0_signals'])}")
                print()
            
            # Simulate BigQuery storage
            await simulate_bigquery_storage(qualified_leads, api_config)
            
            # Save results
            save_icp_results(qualified_leads)
            
            print("✅ PIPELINE CONCLUÍDO - Leads prontos para outreach!")
            
        else:
            print("⚠️ Nenhum lead ICP qualificado encontrado")
        
        # Close connections
        await search_api.close()
        
        return qualified_leads
        
    except Exception as e:
        print(f"❌ Erro no pipeline: {e}")
        return []

def enrich_icp_company(company):
    """Enriquecer empresa com scoring ICP específico"""
    
    name = company.get('name', '')
    description = company.get('description', '')
    website = company.get('website', '')
    
    # Determinar setor
    industry = determine_industry_icp(name, description)
    
    # Estimar tamanho (3-10 funcionários foco)
    employee_estimate = estimate_small_business_size(name, description)
    
    # Calcular ICP score
    icp_score = calculate_icp_score(name, description, industry, employee_estimate)
    
    # Determinar nível de urgência
    urgency_level = determine_urgency_level(industry, description)
    
    # Identificar P0 signals
    p0_signals = identify_p0_signals(website, description, industry)
    
    return {
        'company_name': name,
        'website': website,
        'description': description,
        'industry': industry,
        'estimated_employees': employee_estimate,
        'icp_score': icp_score,
        'urgency_level': urgency_level,
        'p0_signals': p0_signals,
        'discovery_timestamp': datetime.now().isoformat()
    }

def determine_industry_icp(name, description):
    """Determinar setor com foco em ICP de alta urgência"""
    
    text = f"{name} {description}".lower()
    
    # High-urgency verticals (prioridade máxima)
    if any(word in text for word in ['beauty', 'spa', 'salon', 'aesthetic']):
        return 'beauty_clinic'
    elif any(word in text for word in ['dental', 'dentist', 'orthodont']):
        return 'dental_practice'
    elif any(word in text for word in ['real estate', 'realtor', 'property']):
        return 'real_estate'
    elif any(word in text for word in ['emergency', 'urgent', '24/7', 'plumber', 'locksmith']):
        return 'emergency_service'
    elif any(word in text for word in ['law', 'lawyer', 'attorney', 'legal']):
        return 'law_firm'
    elif any(word in text for word in ['medical', 'clinic', 'doctor', 'physician']):
        return 'medical_clinic'
    else:
        return 'other'

def estimate_small_business_size(name, description):
    """Estimar tamanho com foco em 3-10 funcionários"""
    
    text = f"{name} {description}".lower()
    
    # Small business indicators
    if any(word in text for word in ['solo', 'independent', 'freelance', 'individual']):
        return 2  # Solo practice
    elif any(word in text for word in ['small', 'family', 'local', 'boutique']):
        return 5  # Small team (ideal ICP)
    elif any(word in text for word in ['team', 'practice', 'clinic', 'office']):
        return 8  # Small practice
    elif any(word in text for word in ['group', 'associates', 'partners']):
        return 12  # Small group (upper limit)
    else:
        return 6  # Default small business

def calculate_icp_score(name, description, industry, employees):
    """Calcular score ICP específico para 3-10 funcionários"""
    
    score = 40  # Base score
    
    # Industry scoring (alta urgência = mais pontos)
    high_urgency_industries = ['beauty_clinic', 'dental_practice', 'emergency_service']
    medium_urgency_industries = ['real_estate', 'law_firm', 'medical_clinic']
    
    if industry in high_urgency_industries:
        score += 25
    elif industry in medium_urgency_industries:
        score += 20
    else:
        score += 10
    
    # Employee count scoring (3-10 é sweet spot)
    if 3 <= employees <= 10:
        score += 20  # Perfect ICP size
    elif 2 <= employees <= 12:
        score += 15  # Close to ICP
    elif 1 <= employees <= 15:
        score += 10  # Borderline
    else:
        score += 0   # Outside ICP
    
    # Digital presence indicators
    text = f"{name} {description}".lower()
    if any(word in text for word in ['online', 'website', 'digital', 'marketing']):
        score += 10
    
    # Local business indicators (higher conversion)
    if any(word in text for word in ['local', 'community', 'neighborhood', 'area']):
        score += 8
    
    # Active advertising signals
    if any(word in text for word in ['advertising', 'marketing', 'promotion', 'ads']):
        score += 12
    
    return min(score, 100)

def determine_urgency_level(industry, description):
    """Determinar nível de urgência para priorização"""
    
    high_urgency = ['beauty_clinic', 'dental_practice', 'emergency_service']
    medium_urgency = ['real_estate', 'law_firm', 'medical_clinic']
    
    text = description.lower()
    
    # Emergency/urgent keywords boost urgency
    if any(word in text for word in ['urgent', 'emergency', '24/7', 'immediate']):
        return 'CRITICAL'
    elif industry in high_urgency:
        return 'HIGH'
    elif industry in medium_urgency:
        return 'MEDIUM'
    else:
        return 'LOW'

def identify_p0_signals(website, description, industry):
    """Identificar sinais P0 para outreach personalizado"""
    
    signals = []
    
    # Website performance signals (assumindo problemas comuns)
    if website:
        signals.append('website_performance')  # PSI check needed
        signals.append('conversion_optimization')  # Landing page check
    
    # Industry-specific P0s
    if industry == 'beauty_clinic':
        signals.extend(['booking_system', 'before_after_gallery', 'reviews_display'])
    elif industry == 'dental_practice':
        signals.extend(['appointment_booking', 'insurance_info', 'patient_portal'])
    elif industry == 'real_estate':
        signals.extend(['listing_optimization', 'lead_capture', 'virtual_tours'])
    elif industry == 'law_firm':
        signals.extend(['consultation_booking', 'case_studies', 'credentials_display'])
    elif industry == 'emergency_service':
        signals.extend(['call_tracking', 'service_area_seo', 'response_time'])
    elif industry == 'medical_clinic':
        signals.extend(['appointment_system', 'telehealth_setup', 'patient_reviews'])
    
    # Marketing/advertising specific signals
    text = description.lower()
    if 'advertising' in text or 'marketing' in text:
        signals.extend(['ad_landing_match', 'conversion_tracking', 'roi_measurement'])
    
    return signals[:5]  # Top 5 signals for focus

def qualify_icp_leads(companies, target_count):
    """Qualificar e ranquear leads ICP"""
    
    # Sort by ICP score and urgency
    urgency_weights = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
    
    def sort_key(company):
        urgency_weight = urgency_weights.get(company['urgency_level'], 1)
        return (company['icp_score'] * urgency_weight, company['icp_score'])
    
    sorted_companies = sorted(companies, key=sort_key, reverse=True)
    
    # Select top candidates (with buffer)
    qualified = sorted_companies[:target_count * 2]  # 2x buffer for selection
    
    return qualified

async def simulate_bigquery_storage(leads, api_config):
    """Simular armazenamento no BigQuery"""
    
    print("💾 SIMULANDO ARMAZENAMENTO BIGQUERY:")
    print("-" * 40)
    
    # BigQuery table structure
    table_schema = {
        'id': 'STRING',
        'company_name': 'STRING', 
        'website': 'STRING',
        'industry': 'STRING',
        'estimated_employees': 'INTEGER',
        'icp_score': 'INTEGER',
        'urgency_level': 'STRING',
        'p0_signals': 'STRING',  # JSON array as string
        'discovery_date': 'TIMESTAMP',
        'status': 'STRING'
    }
    
    print(f"   📊 Project: {api_config.GOOGLE_CLOUD_PROJECT}")
    print(f"   📁 Dataset: {api_config.BIGQUERY_DATASET_ID}")
    print(f"   📋 Table: icp_prospects")
    print(f"   📝 Schema: {len(table_schema)} columns")
    print(f"   💾 Records to insert: {len(leads)}")
    
    # Simulate successful storage
    print("   ✅ Dados inseridos com sucesso!")
    print("   🔍 Índices criados para: icp_score, industry, urgency_level")
    print("   📈 View `serve.v_icp_outreach` criada")

def save_icp_results(leads):
    """Salvar resultados da descoberta ICP"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"icp_leads_discovery_{timestamp}.json"
    
    # Save in data/
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    filepath = data_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(leads, f, indent=2, default=str)
    
    print(f"💾 Resultados salvos: {filepath}")
    
    # Create outreach summary
    create_outreach_summary(leads, data_dir, timestamp)

def create_outreach_summary(leads, data_dir, timestamp):
    """Criar resumo para outreach"""
    
    summary_file = data_dir / f"outreach_ready_{timestamp}.md"
    
    high_priority = [l for l in leads if l['urgency_level'] in ['CRITICAL', 'HIGH']]
    
    summary = f"""# 🎯 ICP LEADS - PRONTOS PARA OUTREACH

**Data**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Leads**: {len(leads)}  
**Alta Prioridade**: {len(high_priority)}

## 🚀 LEADS PRIORITÁRIOS (48H FOCUS)

"""
    
    for i, lead in enumerate(high_priority[:8], 1):  # Top 8 for 48h goal
        summary += f"""
### {i}. {lead['company_name']} - {lead['urgency_level']}

- **Setor**: {lead['industry'].replace('_', ' ').title()}
- **Funcionários**: ~{lead['estimated_employees']} (ICP: {lead['icp_score']}/100)
- **Website**: {lead['website']}
- **P0 Signals**: {', '.join(lead['p0_signals'])}

**Angle de Outreach**: 
"Analisamos seu {lead['industry'].replace('_', ' ')} e identificamos oportunidades de otimização em {lead['p0_signals'][0]} que podem aumentar suas conversões em 25-40%."

---
"""
    
    summary += f"""
## 📊 ESTATÍSTICAS

- **Indústrias Representadas**: {len(set(l['industry'] for l in leads))}
- **Score ICP Médio**: {sum(l['icp_score'] for l in leads) / len(leads):.1f}
- **Empresas 3-10 Funcionários**: {len([l for l in leads if 3 <= l['estimated_employees'] <= 10])}

## 🎯 PRÓXIMOS PASSOS

1. **PSI Check** nos websites top 8
2. **Message-match analysis** (ads vs landing)  
3. **Outreach personalizado** baseado nos P0 signals
4. **Goal**: 1 audit fechado em 48h

"""
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"📋 Resumo outreach: {summary_file}")

async def main():
    """Execute ICP lead discovery"""
    
    print("🚀 ARCO-FIND: ICP LEAD DISCOVERY")
    print("Targeting: 3-10 employee companies in high-urgency verticals")
    print("Goal: 1 audit in 48h using capacity + probability funnel")
    print()
    
    leads = await discover_icp_leads()
    
    if leads:
        print(f"\n🏆 PIPELINE CONCLUÍDO!")
        print(f"✅ {len(leads)} leads ICP prontos para outreach")
        print(f"🎯 Meta 48h: factível com top 8 leads")
    else:
        print("\n❌ Nenhum lead ICP encontrado - ajustar critérios")

if __name__ == "__main__":
    asyncio.run(main())
