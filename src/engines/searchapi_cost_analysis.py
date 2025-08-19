"""
ARCO SearchAPI - Análise de Custos por Layer
==========================================

Análise detalhada de créditos/custos para otimizar estratégia real estate
em regiões menos saturadas de AU/NZ.
"""

def calculate_api_costs():
    """
    Calcula custos estimados por layer baseado na estrutura atual
    """
    
    costs_analysis = {
        "searchapi_pricing": {
            "cost_per_call": 0.05,  # USD por chamada (estimativa conservadora)
            "rate_limits": {
                "layer1": 0.5,  # segundos entre calls
                "layer2": 0.8,
                "layer3": 1.0
            }
        },
        
        "layer1_costs": {
            "engine": "google_ads_transparency_center_advertiser_search",
            "calls_per_keyword_region": 1,
            "typical_scenario": {
                "keywords": 4,
                "regions": 2,  # AU + NZ
                "total_calls": 8,
                "cost_usd": 0.40
            },
            "real_estate_focused": {
                "keywords": 6,  # Keywords otimizadas
                "regions": 4,   # AU metro + regional, NZ metro + regional
                "total_calls": 24,
                "cost_usd": 1.20
            }
        },
        
        "layer2_costs": {
            "engine": "google_ads_transparency_center",
            "calls_per_advertiser": 1,
            "typical_scenario": {
                "advertisers_from_layer1": 50,
                "batch_processing": True,
                "total_calls": 50,
                "cost_usd": 2.50
            },
            "optimized_scenario": {
                "advertisers_after_filtering": 30,  # Filtro pré-layer2
                "total_calls": 30,
                "cost_usd": 1.50
            }
        },
        
        "layer3_costs": {
            "engine": "google_ads_transparency_center_ad_details",
            "calls_per_creative": 1,
            "typical_scenario": {
                "qualified_advertisers": 15,
                "creatives_per_advertiser": 2,
                "total_calls": 30,
                "cost_usd": 1.50
            },
            "focused_scenario": {
                "top_qualified": 10,
                "creatives_per_advertiser": 1,  # Apenas o melhor criativo
                "total_calls": 10,
                "cost_usd": 0.50
            }
        },
        
        "total_pipeline_costs": {
            "standard_run": {
                "layer1": 0.40,
                "layer2": 2.50,
                "layer3": 1.50,
                "total": 4.40
            },
            "optimized_real_estate": {
                "layer1": 1.20,  # Mais keywords/regiões
                "layer2": 1.50,  # Filtros otimizados
                "layer3": 0.50,  # Foco nos melhores
                "total": 3.20
            },
            "roi_projection": {
                "cost_per_qualified_lead": 0.32,  # 3.20/10 leads
                "real_estate_ticket_aud": "5000-50000",  # Comissão típica
                "break_even_conversion": "0.01%"  # 1 em 10.000 calls
            }
        }
    }
    
    return costs_analysis

def get_optimized_real_estate_keywords():
    """
    Keywords otimizadas para real estate AU/NZ menos saturadas
    """
    
    optimized_keywords = {
        "high_value_niches": [
            "buyers agent",           # Menos saturado que "real estate agent"
            "property investment advice",  # Ticket alto
            "commercial property valuation",  # Menos competição
            "strata management",      # AU específico, nicho
            "property settlement services",  # Serviço especializado
            "building inspection services"   # Complementar, ticket médio
        ],
        
        "regional_opportunities": {
            "au_regional": [
                "property management gold coast",
                "real estate agent sunshine coast", 
                "buyers agent melbourne regional",
                "property valuation tasmania"
            ],
            "nz_regional": [
                "property management wellington",
                "real estate agent christchurch",
                "property valuation dunedin",
                "buyers agent hamilton"
            ]
        },
        
        "keyword_rationale": {
            "buyers_agent": {
                "why": "Nicho crescente, ticket alto (2-3% de 500k+ = 10-15k AUD)",
                "saturation": "Média (vs alta para 'real estate agent')",
                "arco_fit": "Alto - precisam LP convincentes para justificar fee"
            },
            "strata_management": {
                "why": "AU específico, recurring revenue, B2B",
                "saturation": "Baixa",
                "arco_fit": "Alto - sites corporativos ruins, oportunidade CRO"
            },
            "commercial_valuation": {
                "why": "Ticket alto, menos players",
                "saturation": "Baixa",
                "arco_fit": "Alto - sites técnicos com UX horrível"
            }
        }
    }
    
    return optimized_keywords

# Estratégia para segunda-feira (cultura de trabalho AU/NZ)
def monday_strategy_aunz():
    """
    Análise da cultura de trabalho de segunda-feira em AU/NZ
    """
    
    strategy = {
        "cultural_analysis": {
            "australia": {
                "monday_work_culture": "Moderado - início gradual da semana",
                "email_response_rate": "60-70% (vs 80% terça-quinta)",
                "decision_making": "Mais lento às segundas",
                "optimal_approach": "Soft touch, educational content"
            },
            "new_zealand": {
                "monday_work_culture": "Relaxado - 'steady as she goes'",
                "email_response_rate": "50-60%",
                "decision_making": "Evitam decisões grandes às segundas",
                "optimal_approach": "Relationship building, não pitch direto"
            }
        },
        
        "monday_outreach_strategy": {
            "avoid": [
                "Hard sales pitches",
                "Urgency language",
                "Deadline pressure",
                "Complex technical details"
            ],
            "optimize_for": [
                "Educational value",
                "Soft relationship building",
                "'Thinking of you' approach",
                "Valuable insights sharing"
            ],
            "ideal_subject_lines": [
                "Quick insight about your property site performance",
                "Noticed something interesting about your online presence",
                "Brief analysis of your competition (no strings attached)"
            ]
        },
        
        "timing_optimization": {
            "best_days_aunz": ["Tuesday", "Wednesday", "Thursday"],
            "monday_use_case": "Research and preparation day",
            "monday_activities": [
                "Gather data and insights",
                "Prepare personalized research",
                "Set up Tuesday outreach campaigns",
                "Soft 'value-first' touchpoints"
            ]
        }
    }
    
    return strategy

if __name__ == "__main__":
    costs = calculate_api_costs()
    keywords = get_optimized_real_estate_keywords()
    monday_strategy = monday_strategy_aunz()
    
    print("💰 Custos otimizados para Real Estate AU/NZ:")
    print(f"Pipeline total: ${costs['total_pipeline_costs']['optimized_real_estate']['total']}")
    print(f"Custo por lead qualificado: ${costs['total_pipeline_costs']['roi_projection']['cost_per_qualified_lead']}")
    
    print("\n🎯 Keywords otimizadas:")
    for keyword in keywords['high_value_niches']:
        print(f"  • {keyword}")
    
    print("\n📅 Estratégia segunda-feira:")
    print("  • AU/NZ: Cultura de trabalho relaxada às segundas")
    print("  • Foco: Research e preparação, não outreach direto")
    print("  • Melhor para: Análise de dados e insights preparation")
