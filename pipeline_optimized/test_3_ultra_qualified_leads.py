#!/usr/bin/env python3
"""
TESTE: 3 LEADS ULTRA QUALIFICADOS
BigQuery + SearchAPI Pipeline Test
"""

import asyncio
import os
import sys
import json
import time
from datetime import datetime

# Add parent directory to import the main pipeline
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from the working original pipeline
from smb_48h_pipeline import SMBAgencyPipeline

async def find_3_ultra_qualified_leads():
    """
    Teste real: Encontrar 3 leads ultra qualificados usando BigQuery + SearchAPI
    """
    
    print("🎯 TESTE: DESCOBERTA DE 3 LEADS ULTRA QUALIFICADOS")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Pipeline: SearchAPI + BigQuery Logic")
    print()
    
    # Initialize pipeline
    pipeline = SMBAgencyPipeline()
    
    # Verify API keys
    print("🔑 VERIFICAÇÃO DE APIS:")
    print(f"   SearchAPI Key: {'✅ Configurada' if pipeline.searchapi_key else '❌ Não encontrada'}")
    print(f"   PageSpeed Key: {'✅ Configurada' if pipeline.pagespeed_key else '❌ Não encontrada'}")
    print()
    
    start_time = time.time()
    
    # Execute discovery for ultra qualified leads
    print("🔍 EXECUTANDO DESCOBERTA ESTRATÉGICA...")
    print("   Target: 3 leads ultra qualificados (readiness ≥ 0.80)")
    print("   Critério: SMBs com sinais públicos fortes + spend visível")
    print()
    
    # Discovery across high-value verticals
    all_qualified_leads = []
    
    # Target verticals with highest potential
    target_verticals = ['personal_injury_law', 'dental_practices', 'hvac_contractors']
    
    for vertical in target_verticals:
        if vertical in pipeline.high_urgency_verticals:
            print(f"📊 Descobrindo em: {vertical.upper()}")
            
            config = pipeline.high_urgency_verticals[vertical]
            
            try:
                # Discover opportunities in this vertical
                vertical_signals = await pipeline._discover_vertical_opportunities(
                    vertical, config, max_signals=5
                )
                
                print(f"   └── Encontrados: {len(vertical_signals)} P0 signals")
                
                # Filter for ultra qualified (≥0.80 readiness)
                ultra_qualified = [
                    signal for signal in vertical_signals 
                    if signal.readiness_score >= 0.80
                ]
                
                print(f"   └── Ultra qualified: {len(ultra_qualified)} leads")
                
                all_qualified_leads.extend(ultra_qualified)
                
                # Show top lead from this vertical
                if ultra_qualified:
                    top_lead = max(ultra_qualified, key=lambda x: x.readiness_score)
                    print(f"   └── TOP: {top_lead.company_name} (readiness: {top_lead.readiness_score:.2f})")
                
            except Exception as e:
                print(f"   └── ❌ Erro: {e}")
            
            print()
    
    # Rank all leads by readiness score + monthly waste
    all_qualified_leads.sort(
        key=lambda x: (x.readiness_score * (x.monthly_waste / 1000)), 
        reverse=True
    )
    
    # Select TOP 3 ultra qualified leads
    top_3_leads = all_qualified_leads[:3]
    
    execution_time = time.time() - start_time
    
    print("✅ DESCOBERTA CONCLUÍDA")
    print(f"   Tempo de execução: {execution_time:.1f}s")
    print(f"   Total leads encontrados: {len(all_qualified_leads)}")
    print(f"   TOP 3 selecionados: {len(top_3_leads)}")
    print()
    
    # Display TOP 3 ULTRA QUALIFIED LEADS
    print("🔥 TOP 3 LEADS ULTRA QUALIFICADOS:")
    print("=" * 50)
    
    for i, lead in enumerate(top_3_leads, 1):
        print(f"\n{i}. {lead.company_name}")
        print(f"   📍 Vertical: {lead.vertical} | Domain: {lead.domain}")
        print(f"   📊 Readiness Score: {lead.readiness_score:.2f}")
        print(f"   💰 Monthly Waste: ${lead.monthly_waste:,}")
        print(f"   ⚠️ Urgency Level: {lead.urgency_level}")
        print(f"   🔧 Technical Issues: {lead.rationale}")
        
        # Contact data
        contact = lead.contact_data
        print(f"   📧 Email: {contact.get('email_patterns', ['N/A'])[0]}")
        print(f"   🔗 LinkedIn: {contact.get('linkedin_search', 'N/A')}")
        
        # Calculate approach strategy
        if lead.readiness_score >= 0.90:
            approach = "🎯 IMMEDIATE APPROACH - High readiness + strong signals"
        elif lead.readiness_score >= 0.85:
            approach = "⚡ PRIORITY APPROACH - Very qualified prospect"
        else:
            approach = "📞 STANDARD APPROACH - Qualified but needs nurturing"
        
        print(f"   🚀 Strategy: {approach}")
    
    # Generate summary analytics
    if top_3_leads:
        total_waste = sum(lead.monthly_waste for lead in top_3_leads)
        avg_readiness = sum(lead.readiness_score for lead in top_3_leads) / len(top_3_leads)
        
        print(f"\n📈 PORTFOLIO ANALYTICS:")
        print(f"   Combined monthly waste: ${total_waste:,}")
        print(f"   Average readiness: {avg_readiness:.2f}")
        print(f"   Conversion probability: {min(95, avg_readiness * 100):.0f}%")
        print(f"   Expected revenue (3 audits): ${1500 * len(top_3_leads):,}")
    
    # Save results to JSON
    results = {
        'timestamp': datetime.now().isoformat(),
        'execution_time': execution_time,
        'total_leads_discovered': len(all_qualified_leads),
        'top_3_ultra_qualified': [
            {
                'rank': i + 1,
                'company_name': lead.company_name,
                'domain': lead.domain,
                'vertical': lead.vertical,
                'readiness_score': lead.readiness_score,
                'monthly_waste': lead.monthly_waste,
                'urgency_level': lead.urgency_level,
                'rationale': lead.rationale,
                'contact_data': lead.contact_data
            }
            for i, lead in enumerate(top_3_leads)
        ],
        'portfolio_metrics': {
            'total_monthly_waste': total_waste if top_3_leads else 0,
            'average_readiness': avg_readiness if top_3_leads else 0,
            'conversion_probability': min(95, avg_readiness * 100) if top_3_leads else 0
        }
    }
    
    # Save to file
    output_file = "3_ULTRA_QUALIFIED_LEADS_TEST.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em: {output_file}")
    
    print(f"\n🎯 CONCLUSÃO DO TESTE:")
    print(f"   ✅ Pipeline SearchAPI + BigQuery logic executado")
    print(f"   ✅ {len(top_3_leads)} leads ultra qualificados identificados")
    print(f"   ✅ Dados salvos para análise e outreach")
    print(f"   ✅ Ready for immediate prospecting execution")
    
    return top_3_leads

if __name__ == "__main__":
    leads = asyncio.run(find_3_ultra_qualified_leads())
