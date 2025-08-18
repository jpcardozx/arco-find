#!/usr/bin/env python3
"""
AUTOMATED S-TIER OUTREACH GENERATOR
==================================

Gera templates de outreach personalizados automáticamente para cada lead:
- Detecta idioma do prospect baseado no nome/região
- Personaliza pain points específicos 
- Adapta tom para o niche (aesthetics, legal, real estate, dental)
- Templates S-tier para primeiro contato
- Output pronto para email

Author: ARCO Intelligence
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class OutreachTemplate:
    subject_line: str
    email_body: str
    language: str
    tone: str
    pain_points: List[str]
    cta: str

class STierOutreachGenerator:
    """Gerador automático de outreach personalizado S-tier"""
    
    def __init__(self):
        self.language_patterns = {
            'spanish': [
                r'\.es$', r'españa', r'madrid', r'barcelona', r'sevilla',
                r'hernandez', r'garcia', r'rodriguez', r'martinez', r'lopez',
                r'pesaje', r'morales', r'alzate', r'adolfo', r'gustavo'
            ],
            'portuguese': [
                r'\.br$', r'brasil', r'ltda', r'rio', r'são paulo',
                r'silva', r'santos', r'oliveira', r'souza', r'costa',
                r'oral.*odontologia', r'natal', r'angelica.*maria'
            ],
            'italian': [
                r'\.it$', r'milano', r'roma', r'torino', r'italia',
                r'rossi', r'ferrari', r'romano', r'colombo', r'bruno',
                r'\.srl', r'implant.*s\.r\.l'
            ],
            'french': [
                r'\.fr$', r'paris', r'lyon', r'marseille', r'france',
                r'martin', r'bernard', r'dubois', r'moreau', r'laurent',
                r'diffusion', r'coral'
            ],
            'german': [
                r'\.de$', r'berlin', r'munich', r'hamburg', r'deutschland',
                r'müller', r'schmidt', r'schneider', r'fischer', r'weber',
                r'gmbh', r'caspar', r'christian'
            ],
            'english': [
                r'limited$', r'ltd$', r'inc$', r'llc$', r'co\.$',
                r'smith', r'johnson', r'williams', r'brown', r'jones',
                r'clinic', r'therapy', r'counselling', r'legal', r'realty'
            ]
        }
        
        self.niche_pain_points = {
            'Aesthetics': {
                'english': [
                    "creative fatigue hurting client acquisition",
                    "outdated ads not converting premium clients", 
                    "missing seasonal beauty trends in campaigns",
                    "competitors stealing market share with fresh creatives"
                ],
                'spanish': [
                    "fatiga creativa afectando la captación de clientes",
                    "anuncios desactualizados no convierten clientes premium",
                    "perdiendo tendencias de belleza estacional",
                    "competidores robando cuota de mercado con creativos frescos"
                ],
                'portuguese': [
                    "fadiga criativa prejudicando aquisição de clientes",
                    "anúncios desatualizados não convertem clientes premium",
                    "perdendo tendências sazonais de beleza",
                    "concorrentes roubando market share com criativos frescos"
                ],
                'german': [
                    "kreative Müdigkeit schadet der Kundenakquise",
                    "veraltete Anzeigen konvertieren keine Premium-Kunden",
                    "saisonale Beauty-Trends werden verpasst",
                    "Konkurrenten stehlen Marktanteile mit frischen Kreationen"
                ],
                'french': [
                    "fatigue créative nuit à l'acquisition de clients",
                    "annonces obsolètes ne convertissent pas les clients premium",
                    "manque les tendances beauté saisonnières",
                    "concurrents volent des parts de marché avec des créatifs frais"
                ],
                'italian': [
                    "affaticamento creativo danneggia l'acquisizione clienti",
                    "annunci obsoleti non convertono clienti premium",
                    "perdendo trend stagionali di bellezza",
                    "competitor rubano quote di mercato con creativi freschi"
                ]
            },
            'Real Estate': {
                'english': [
                    "stale property ads losing to fresh competitor listings",
                    "missing seasonal buying patterns in campaigns",
                    "outdated creative not matching current market conditions",
                    "potential buyers scrolling past tired property ads"
                ],
                'spanish': [
                    "anuncios de propiedades obsoletos perdiendo contra competidores frescos",
                    "perdiendo patrones estacionales de compra",
                    "creativos desactualizados no coinciden con condiciones actuales",
                    "compradores potenciales ignorando anuncios cansados"
                ],
                'portuguese': [
                    "anúncios de imóveis obsoletos perdendo para concorrentes frescos",
                    "perdendo padrões sazonais de compra",
                    "criativos desatualizados não combinam com condições atuais",
                    "compradores potenciais ignorando anúncios cansados"
                ]
            },
            'Legal': {
                'english': [
                    "outdated legal ads undermining professional credibility",
                    "missing client pain points in stagnant campaigns", 
                    "competitors capturing urgent legal needs with fresh messaging",
                    "potential clients questioning firm relevance from old ads"
                ],
                'spanish': [
                    "anuncios legales desactualizados socavan credibilidad profesional",
                    "perdiendo puntos de dolor del cliente en campañas estancadas",
                    "competidores capturan necesidades legales urgentes con mensajes frescos",
                    "clientes potenciales cuestionan relevancia del bufete por anuncios viejos"
                ]
            },
            'Dental': {
                'english': [
                    "outdated dental ads not reflecting modern practice standards",
                    "missing seasonal oral health awareness campaigns",
                    "competitors attracting patients with fresh, trust-building creatives",
                    "potential patients questioning practice modernity from stale ads"
                ],
                'portuguese': [
                    "anúncios dentários desatualizados não refletem padrões modernos",
                    "perdendo campanhas sazonais de conscientização oral",
                    "concorrentes atraindo pacientes com criativos frescos e confiáveis",
                    "pacientes potenciais questionando modernidade por anúncios obsoletos"
                ]
            }
        }

    def detect_language(self, business_name: str, region: str) -> str:
        """Detecta idioma baseado no nome da empresa e região"""
        
        text_to_analyze = f"{business_name} {region}".lower()
        
        language_scores = {}
        
        for language, patterns in self.language_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text_to_analyze):
                    score += 1
            language_scores[language] = score
        
        # Retorna idioma com maior score, default para inglês
        if language_scores:
            detected = max(language_scores, key=language_scores.get)
            if language_scores[detected] > 0:
                return detected
        
        return 'english'  # Default

    def get_pain_points(self, niche: str, language: str) -> List[str]:
        """Retorna pain points específicos do nicho e idioma"""
        
        if niche in self.niche_pain_points:
            if language in self.niche_pain_points[niche]:
                return self.niche_pain_points[niche][language]
            else:
                # Fallback para inglês se idioma não disponível
                return self.niche_pain_points[niche].get('english', [])
        
        return ["outdated advertising strategy hurting business growth"]

    def generate_subject_line(self, business_name: str, creative_age: int, language: str) -> str:
        """Gera subject line personalizada"""
        
        company = business_name.split()[0] if business_name else "Your Business"
        
        subjects = {
            'english': [
                f"Quick Win for {company}: Your {creative_age}-day ad refresh opportunity",
                f"{company}: Why your ads haven't changed in {creative_age} days (2-min read)",
                f"Fast competitive edge for {company} (spotted a gap in your ad strategy)"
            ],
            'spanish': [
                f"Victoria Rápida para {company}: Tu oportunidad de refresh de {creative_age} días",
                f"{company}: Por qué tus anuncios no han cambiado en {creative_age} días",
                f"Ventaja competitiva rápida para {company} (detectamos un gap)"
            ],
            'portuguese': [
                f"Vitória Rápida para {company}: Sua oportunidade de refresh de {creative_age} dias",
                f"{company}: Por que seus anúncios não mudaram em {creative_age} dias",
                f"Vantagem competitiva rápida para {company} (detectamos uma lacuna)"
            ],
            'german': [
                f"Schneller Erfolg für {company}: Ihre {creative_age}-Tage Anzeigen-Refresh Chance",
                f"{company}: Warum sich Ihre Anzeigen seit {creative_age} Tagen nicht geändert haben",
                f"Schneller Wettbewerbsvorteil für {company} (Lücke in Ihrer Strategie entdeckt)"
            ],
            'french': [
                f"Victoire Rapide pour {company}: Votre opportunité de refresh de {creative_age} jours",
                f"{company}: Pourquoi vos annonces n'ont pas changé depuis {creative_age} jours",
                f"Avantage concurrentiel rapide pour {company} (gap détecté dans votre stratégie)"
            ],
            'italian': [
                f"Vittoria Veloce per {company}: La tua opportunità di refresh di {creative_age} giorni",
                f"{company}: Perché i tuoi annunci non sono cambiati in {creative_age} giorni",
                f"Vantaggio competitivo veloce per {company} (gap individuato nella strategia)"
            ]
        }
        
        return subjects.get(language, subjects['english'])[0]

    def generate_email_body(self, business_name: str, niche: str, creative_age: int, 
                          language: str, pain_points: List[str]) -> str:
        """Gera corpo do email personalizado"""
        
        templates = {
            'english': f"""Hi there,

I noticed {business_name} has been running the same ad creatives for {creative_age} days.

While your {niche.lower()} business clearly has staying power, here's what this creative stagnation might be costing you:

• {pain_points[0] if pain_points else 'Decreased ad performance over time'}
• {pain_points[1] if len(pain_points) > 1 else 'Missed opportunities for seasonal messaging'}
• {pain_points[2] if len(pain_points) > 2 else 'Reduced competitive edge in your market'}

The good news? A quick creative refresh could unlock immediate performance gains.

I've helped {niche.lower()} businesses see 40-70% performance improvements within 2 weeks of implementing fresh, data-driven creatives.

Worth a 15-minute conversation to explore your specific situation?

Best regards,
ARCO Intelligence
Performance Marketing Specialists

P.S. I can share a case study from a similar {niche.lower()} business that went from stagnant to thriving in just 3 weeks.""",

            'spanish': f"""Hola,

Noté que {business_name} ha estado usando los mismos creativos publicitarios durante {creative_age} días.

Aunque tu negocio de {niche.lower()} claramente tiene resistencia, esto es lo que esta estancación creativa podría estar costándote:

• {pain_points[0] if pain_points else 'Rendimiento publicitario disminuido con el tiempo'}
• {pain_points[1] if len(pain_points) > 1 else 'Oportunidades perdidas para mensajes estacionales'}
• {pain_points[2] if len(pain_points) > 2 else 'Ventaja competitiva reducida en tu mercado'}

¿Las buenas noticias? Un refresh creativo rápido podría desbloquear ganancias de rendimiento inmediatas.

He ayudado a negocios de {niche.lower()} a ver mejoras de rendimiento del 40-70% dentro de 2 semanas de implementar creativos frescos y basados en datos.

¿Vale la pena una conversación de 15 minutos para explorar tu situación específica?

Saludos cordiales,
ARCO Intelligence
Especialistas en Marketing de Performance

P.D. Puedo compartir un caso de estudio de un negocio similar de {niche.lower()} que pasó de estancado a próspero en solo 3 semanas.""",

            'portuguese': f"""Olá,

Notei que {business_name} tem usado os mesmos criativos publicitários por {creative_age} dias.

Embora seu negócio de {niche.lower()} claramente tenha resistência, aqui está o que essa estagnação criativa pode estar custando:

• {pain_points[0] if pain_points else 'Performance publicitária diminuída ao longo do tempo'}
• {pain_points[1] if len(pain_points) > 1 else 'Oportunidades perdidas para mensagens sazonais'}
• {pain_points[2] if len(pain_points) > 2 else 'Vantagem competitiva reduzida no seu mercado'}

A boa notícia? Um refresh criativo rápido poderia liberar ganhos de performance imediatos.

Ajudei negócios de {niche.lower()} a verem melhorias de performance de 40-70% dentro de 2 semanas de implementar criativos frescos e baseados em dados.

Vale uma conversa de 15 minutos para explorar sua situação específica?

Cordialmente,
ARCO Intelligence
Especialistas em Marketing de Performance

P.S. Posso compartilhar um caso de estudo de um negócio similar de {niche.lower()} que foi do estagnado ao próspero em apenas 3 semanas."""
        }
        
        return templates.get(language, templates['english'])

    def generate_outreach(self, prospect_data: Dict) -> OutreachTemplate:
        """Gera outreach completo personalizado para um prospect"""
        
        business_name = prospect_data.get('business_name', '')
        niche = prospect_data.get('niche', '')
        region = prospect_data.get('location_region', '')
        creative_age = int(prospect_data.get('avg_creative_age_days', 0))
        
        # Detectar idioma
        language = self.detect_language(business_name, region)
        
        # Obter pain points específicos
        pain_points = self.get_pain_points(niche, language)
        
        # Gerar componentes
        subject = self.generate_subject_line(business_name, creative_age, language)
        body = self.generate_email_body(business_name, niche, creative_age, language, pain_points)
        
        return OutreachTemplate(
            subject_line=subject,
            email_body=body,
            language=language,
            tone="professional_consultative",
            pain_points=pain_points,
            cta=f"15-minute strategy conversation for {business_name}"
        )

def generate_all_outreach_templates(prospects_file: str) -> List[Dict]:
    """Gera templates para todos os prospects de um arquivo"""
    
    generator = STierOutreachGenerator()
    
    # Carregar prospects
    with open(prospects_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    prospects = data.get('prospects', [])
    
    outreach_campaigns = []
    
    for i, prospect in enumerate(prospects, 1):
        print(f"🎯 Gerando outreach {i}/{len(prospects)}: {prospect.get('business_name', 'Unknown')}")
        
        template = generator.generate_outreach(prospect)
        
        campaign = {
            "prospect_info": prospect,
            "outreach_template": {
                "subject_line": template.subject_line,
                "email_body": template.email_body,
                "language": template.language,
                "tone": template.tone,
                "pain_points": template.pain_points,
                "cta": template.cta
            },
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        outreach_campaigns.append(campaign)
    
    return outreach_campaigns

if __name__ == "__main__":
    # Gerar templates para os prospects SMB
    prospects_file = "data/ultra_qualified/smb_pain_signals_20250817_230837.json"
    
    print("🚀 Gerando templates de outreach S-tier personalizados...")
    
    campaigns = generate_all_outreach_templates(prospects_file)
    
    # Salvar resultado
    output_file = f"data/ultra_qualified/outreach_campaigns_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    output_data = {
        "summary": {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_campaigns": len(campaigns),
            "languages_detected": list(set(c["outreach_template"]["language"] for c in campaigns)),
            "niches_covered": list(set(c["prospect_info"]["niche"] for c in campaigns))
        },
        "campaigns": campaigns
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {len(campaigns)} templates gerados e salvos em: {output_file}")
    print(f"📊 Idiomas detectados: {output_data['summary']['languages_detected']}")
    print(f"🎯 Nichos cobertos: {output_data['summary']['niches_covered']}")
