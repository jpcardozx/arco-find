#!/usr/bin/env python3
"""
ARCO Funis Aprovados 2025 - Plano de Aquisição Ponta a Ponta
Sem espuma, sem romance de growth hacker. Só o que converte.
"""

from datetime import datetime
import json

def define_funis_aprovados():
    """
    2 funis que merecem viver + kill rules
    """
    
    funis = {
        "funil_a_auditoria_express": {
            "nome": "Auditoria Express 48h to Sprint 7 dias",
            "ticket_entrada": 250,  # USD
            "ticket_upgrade": 750,  # USD (com desconto integral)
            "promessa": "Em 48h, te entrego 5 correções priorizadas que recuperam 10× o fee em mídia desperdiçada",
            "garantia": "Se a conta não fecha, você não paga o upgrade",
            
            "arquitetura": {
                "landing_page": {
                    "headline": "Seus anúncios convertem 40% menos por culpa da landing page",
                    "subheadline": "Auditoria Express identifica 5 vazamentos críticos em 48h",
                    "provas": [
                        "Prints WebPageTest/PSI com scores reais",
                        "Antes/depois com impacto mensurável na conversão",
                        "Depoimento curto de cliente que recuperou $X/mês"
                    ],
                    "cta_unico": "Quero Auditoria 48h - $250 (100% abatível)"
                },
                
                "entrega": {
                    "formato": "PDF de 3-5 páginas",
                    "conteudo": [
                        "1. Velocidade e impacto na conversão (PageSpeed + estimativa perda)",
                        "2. Clareza da oferta/UX (screenshots + sugestões específicas)",
                        "3. Tracking (pixels, eventos, attribution gaps)",
                        "4. Riscos de confiança (social proof, garantias, transparência)",
                        "5. Backlog Sprint 7 dias (impacto estimado × esforço)"
                    ],
                    "upgrade_offer": "Link final: Agendar Sprint em até 5 dias com desconto integral"
                }
            },
            
            "aquisicao": {
                "canais_primarios": [
                    "Outbound qualificado (100-150 emails/semana)",
                    "Retarget 7 dias (quem viu >50% do Loom)",
                    "Brand search barato (Google Ads)"
                ],
                "sequencia_outbound": {
                    "d0": "Email com Loom 90s personalizado + CTA 'Quero Auditoria 48h'",
                    "d2": "Email '3 ganhos rápidos que não estão no seu radar' + proof/print",
                    "d5": "SMS/WhatsApp curto para quem abriu + agenda direta",
                    "d7": "Email final com case study relevante + último convite"
                }
            },
            
            "kill_rules": {
                "upgrade_rate": {
                    "metrica": "Taxa de upgrade Auditoria → Sprint",
                    "limite": "< 20% por 3 semanas seguidas",
                    "acao": "MATAR funil"
                },
                "lead_magnet": {
                    "metrica": "Conversão LP → Lead",
                    "limite": "< 10% mesmo após 2 iterações",
                    "acao": "MATAR funil"
                }
            }
        },
        
        "funil_b_teardown_60s": {
            "nome": "Teardown 60s to Agenda Imediata",
            "ticket_entrada": 0,  # Pré-valor ungated
            "ticket_upgrade": 750,  # Sprint direto
            "promessa": "Vídeo 60s mostra exatamente onde seus R$ estão vazando + como corrigir",
            "mecanismo": "Corta objeção 'confio em quem?' na raiz - prova competência em 90s",
            
            "arquitetura": {
                "assets": {
                    "video_teardown": {
                        "duracao": "60-90 segundos",
                        "roteiro": [
                            "0-15s: Hook específico do nicho ('Analisei 50 dentistas e 80% cometem esse erro')",
                            "15-45s: Screen share da landing/anúncio com problemas visíveis",
                            "45-60s: Solução rápida + impacto financeiro estimado",
                            "60-90s: CTA forte para agenda Sprint"
                        ],
                        "personalizacao": "Nome da empresa + problema específico identificado"
                    }
                },
                
                "distribuicao": {
                    "outbound": "Email + vídeo anexo + texto mínimo",
                    "retarget": "Facebook/LinkedIn para quem assistiu >50%",
                    "social_proof": "Postar teardowns genéricos (sem nome) como content marketing"
                }
            },
            
            "aquisicao": {
                "canais_primarios": [
                    "Outbound direto (150-200 emails/semana)",
                    "LinkedIn outreach com vídeo nativo",
                    "Retarget para visualizações >50%"
                ],
                "sequencia_outbound": {
                    "d0": "Email: 'Analisei [empresa] em 60s' + vídeo + CTA agenda",
                    "d1": "SMS/WhatsApp: 'Viu o vídeo sobre [problema específico]? 15min?'",
                    "d3": "Email: Teardown de competidor + 'Quer o seu também?'",
                    "d7": "Email final: Case study + última chance agenda"
                }
            },
            
            "kill_rules": {
                "response_rate": {
                    "metrica": "Resposta positiva por email",
                    "limite": "< 6% por 2 semanas com lista qualificada",
                    "acao": "MATAR funil"
                },
                "conversion_rate": {
                    "metrica": "Visualização >50% → Booked calls",
                    "limite": "< 15% sem melhora após ajustar CTA/slots",
                    "acao": "MATAR funil"
                }
            }
        }
    }
    
    return funis


def create_acquisition_plan_by_niche():
    """
    Plano de aquisição ponta a ponta por nicho
    Baseado em dados da Meta Ad Library + qualificação rigorosa
    """
    
    niches = {
        "dental_br": {
            "profile": {
                "decision_maker": "Dentista proprietário ou sócio",
                "budget_range": "$2k-8k/mês em ads",
                "pain_points": [
                    "PageSpeed mobile crítico (agendamentos mobile)",
                    "Landing page sem financiamento claro",
                    "Tracking deficiente (não sabe ROI real)"
                ],
                "best_approach": "Auditoria Express",
                "timing": "Terça-Quinta 14h-16h"
            },
            
            "qualification_gates": {
                "gate_1_meta_ads": {
                    "criteria": "Anúncios ativos últimos 30 dias",
                    "tools": ["Meta Ad Library scraper"],
                    "elimination": "70% prospects"
                },
                "gate_2_website_problems": {
                    "criteria": "PageSpeed < 70 OU mobile issues óbvios",
                    "tools": ["PageSpeed API", "Manual audit"],
                    "elimination": "50% remaining"
                },
                "gate_3_budget_indicators": {
                    "criteria": ">3 criativos diferentes OU campanha multi-região",
                    "tools": ["Meta ads analysis"],
                    "elimination": "30% remaining"
                },
                "gate_4_decision_maker": {
                    "criteria": "LinkedIn do proprietário identificado",
                    "tools": ["LinkedIn search", "Website about"],
                    "elimination": "20% remaining"
                }
            },
            
            "outreach_templates": {
                "auditoria_express": {
                    "subject": "$X desperdiçados mensalmente - [Clínica]",
                    "body": """Dr. [Nome],

Quick question antes do final do expediente.

Analisei [clinica].com.br e identifiquei R$ [valor] desperdiçados mensalmente em agendamentos perdidos.

Problema específico: PageSpeed mobile [score]/100 = [tempo]s loading = 60%+ visitantes desistem antes de agendar.

Seus concorrentes carregam 3x mais rápido e capturam esses agendamentos.

Auditoria Express 48h mostra exatamente como corrigir + recuperar esses R$ [valor]/mês.

Vale 15min amanhã de manhã?

Abs,
João Pedro

P.S. Otimização mobile é crítica para dental - 70% das buscas por dentista acontecem no celular."""
                },
                
                "teardown_60s": {
                    "subject": "Analisei [Clínica] em 60 segundos",
                    "body": """Dr. [Nome],

Gravei análise rápida de [clinica].com.br identificando onde seus R$ estão vazando.

[VÍDEO - 60s mostrando problema específico + impacto estimado]

Vale agendar 15min para mostrar como corrigir?

Abs,
João Pedro"""
                }
            },
            
            "lead_sources": {
                "meta_ad_library": {
                    "search_terms": ["dentista", "odontologia", "consultório dental"],
                    "filters": ["BR", "active_last_30d"],
                    "expected_volume": "200-300 prospects/week"
                },
                "linkedin_sales_nav": {
                    "search": "Dentista AND (proprietário OR sócio) AND Brasil",
                    "expected_volume": "50-100 prospects/week"
                },
                "local_directories": {
                    "sources": ["Google My Business", "doctoralia.com.br"],
                    "expected_volume": "100-200 prospects/week"
                }
            }
        },
        
        "real_estate_br": {
            "profile": {
                "decision_maker": "Corretor ou dono de imobiliária",
                "budget_range": "$1k-5k/mês em ads",
                "pain_points": [
                    "Landing genérica (residencial + comercial confuso)",
                    "Formulário longo demais",
                    "Sem urgência/escassez nos anúncios"
                ],
                "best_approach": "Teardown 60s",
                "timing": "Segunda-Quarta 10h-12h ou 15h-17h"
            },
            
            "qualification_gates": {
                "gate_1_meta_ads": {
                    "criteria": "Anúncios imóveis ativos últimos 30 dias",
                    "elimination": "75% prospects"
                },
                "gate_2_portfolio_size": {
                    "criteria": ">10 imóveis anunciados OU equipe >3 pessoas",
                    "elimination": "40% remaining"
                },
                "gate_3_website_quality": {
                    "criteria": "Site próprio (não só Facebook/Instagram)",
                    "elimination": "30% remaining"
                },
                "gate_4_contact_method": {
                    "criteria": "WhatsApp business OU telefone fixo",
                    "elimination": "10% remaining"
                }
            }
        },
        
        "fitness_br": {
            "profile": {
                "decision_maker": "Dono da academia ou personal trainer",
                "budget_range": "$500-3k/mês em ads",
                "pain_points": [
                    "Não trackea trial → matrícula conversion",
                    "Landing page sem social proof local",
                    "Anúncios genéricos (não segmentam por objetivo)"
                ],
                "best_approach": "Teardown 60s",
                "timing": "Sexta-Domingo 9h-11h (planning week)"
            }
        }
    }
    
    return niches


def calculate_funnel_economics():
    """
    Econômicas dos funis - sem romance, só números
    """
    
    economics = {
        "auditoria_express": {
            "inputs": {
                "leads_needed_per_month": 20,
                "conversion_rate_lead_to_audit": 0.15,  # 15%
                "conversion_rate_audit_to_sprint": 0.25,  # 25%
                "avg_sprint_value": 750
            },
            "calculations": {
                "audits_per_month": 20 * 0.15,  # 3 audits
                "sprints_per_month": 3 * 0.25,  # 0.75 sprints
                "monthly_revenue": (3 * 250) + (0.75 * 750),  # $1312.5
                "leads_required": 133  # Para chegar em 20 qualificados
            },
            "cac_analysis": {
                "max_cac_sustainable": 65,  # $1312.5 / 20 leads
                "outbound_cost_per_lead": 15,  # Email + tools + time
                "margin_safety": "4.3x"
            }
        },
        
        "teardown_60s": {
            "inputs": {
                "leads_contacted_per_month": 600,  # 150/week
                "response_rate": 0.08,  # 8%
                "video_view_rate": 0.70,  # 70% 
                "booking_rate": 0.20,  # 20% of viewers
                "close_rate": 0.30,  # 30% of booked calls
                "avg_sprint_value": 750
            },
            "calculations": {
                "responses_per_month": 600 * 0.08,  # 48 responses
                "video_views": 48 * 0.70,  # 33.6 views
                "booked_calls": 33.6 * 0.20,  # 6.7 calls
                "closed_deals": 6.7 * 0.30,  # 2 deals
                "monthly_revenue": 2 * 750  # $1500
            },
            "cac_analysis": {
                "cost_per_lead": 8,  # Video creation + outbound
                "total_monthly_cost": 600 * 8,  # $4800
                "roi": 1500 / 4800,  # 31% (não sustentável)
            }
        }
    }
    
    return economics


def generate_implementation_roadmap():
    """
    Roadmap de implementação - primeiros 30 dias
    """
    
    roadmap = {
        "week_1_setup": {
            "tech_stack": [
                "Implementar Meta Ad Library scraper",
                "Setup PageSpeed API para audits automáticas",
                "Configurar banco SQLite para prospects",
                "Criar templates Loom para Teardown 60s"
            ],
            "content_creation": [
                "Landing page Auditoria Express",
                "Templates de email para cada vertical",
                "Roteiro Teardown 60s por nicho",
                "Proof elements (cases, prints, depoimentos)"
            ]
        },
        
        "week_2_testing": {
            "validation": [
                "Testar scraper Meta Ads com 50 prospects dental",
                "Qualificar 20 prospects pelos gates",
                "Enviar 50 emails Auditoria Express",
                "Criar 10 Teardown videos personalizado"
            ],
            "metrics": [
                "Response rate por template",
                "Video view rate por nicho", 
                "Booking rate por approach",
                "Time to create cada asset"
            ]
        },
        
        "week_3_optimization": {
            "improvements": [
                "Ajustar templates baseado em responses",
                "Otimizar qualification gates",
                "A/B test subject lines",
                "Refinar video scripts"
            ]
        },
        
        "week_4_scale": {
            "scaling": [
                "Aumentar volume outbound para 500 prospects/week",
                "Automatizar qualification gates",
                "Criar process para video creation em batch",
                "Setup retarget campaigns"
            ]
        }
    }
    
    return roadmap


if __name__ == "__main__":
    funis = define_funis_aprovados()
    niches = create_acquisition_plan_by_niche()
    economics = calculate_funnel_economics()
    roadmap = generate_implementation_roadmap()
    
    print("ARCO FUNIS APROVADOS 2025")
    print("=" * 50)
    
    print("\nFUNIS QUE MERECEM VIVER:")
    for funil_id, funil in funis.items():
        print(f"\n{funil['nome']} (${funil['ticket_entrada']} to ${funil['ticket_upgrade']})")
        print(f"Kill rule: {list(funil['kill_rules'].keys())}")
    
    print(f"\nECONOMICS:")
    for funil_id, data in economics.items():
        calc = data['calculations']
        print(f"\n{funil_id.upper()}:")
        print(f"  Monthly revenue: ${calc.get('monthly_revenue', 'N/A')}")
        print(f"  CAC vs Margin: {data['cac_analysis'].get('margin_safety', 'NEGATIVE')}")
    
    print(f"\nIMPLEMENTATION:")
    print(f"Week 1: {len(roadmap['week_1_setup']['tech_stack'])} tech tasks")
    print(f"Week 2: {len(roadmap['week_2_testing']['validation'])} validation tests")
    print(f"Week 4: Scale to 500 prospects/week")
    
    # Save complete plan
    complete_plan = {
        "funis_aprovados": funis,
        "niches_plan": niches,
        "economics": economics,
        "implementation_roadmap": roadmap,
        "generated_at": datetime.now().isoformat()
    }
    
    with open("ARCO_FUNIS_APROVADOS_2025.json", "w", encoding="utf-8") as f:
        json.dump(complete_plan, f, indent=2, ensure_ascii=False)
    
    print(f"\nPLANO COMPLETO SALVO: ARCO_FUNIS_APROVADOS_2025.json")