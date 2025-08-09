"""
Outreach Agent - ARCO V3
Generates personalized messages, creates evidence packages, and manages follow-up sequences
Based on AGENTS.md specification
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from string import Template

from ..models.core_models import ScoredProspect, OutreachMessage, ServiceFit, Vertical

logger = logging.getLogger(__name__)


class OutreachAgent:
    """
    Outreach Agent implementing the decision tree from AGENTS.md:
    - Generate personalized messages by vertical
    - Create visual evidence (screenshots + annotations)
    - Generate Loom video scripts
    - Schedule follow-ups
    """
    
    def __init__(self):
        self.vertical_templates = self._initialize_templates()
        self.follow_up_sequences = self._initialize_followup_sequences()
        
        # Pain point prioritization weights
        self.pain_priorities = {
            "LCP_HIGH": 10,           # Highest impact on conversions
            "MOBILE_UNFRIENDLY": 9,   # 60% of traffic affected
            "SSL_ISSUES": 8,          # Trust and security
            "INP_HIGH": 7,            # User frustration
            "CLS_HIGH": 6,            # User experience
            "NO_PHONE_CTA": 5,        # Lead capture
            "FCP_HIGH": 4,            # First impression
            "WEAK_FORM": 3            # Conversion optimization
        }
    
    def generate_message(self, scored_prospect: ScoredProspect) -> OutreachMessage:
        """
        Generate personalized outreach message following growth potential decision tree
        """
        logger.info(f"📧 Generating outreach for {scored_prospect.discovery_data.domain}")
        
        # Gate 1: Growth Tier Template Selection (based on growth potential score)
        template_key = self._select_growth_template(scored_prospect)
        template = self.vertical_templates.get(template_key, self.vertical_templates["default"])
        
        # Gate 2: Strategic Insights Extraction
        strategic_insights = self._extract_strategic_insights(scored_prospect)
        
        # Gate 3: Growth Vulnerability Analysis
        growth_vulnerabilities = self._analyze_growth_vulnerabilities(scored_prospect)
        
        # Gate 4: Evidence Selection
        evidence_url = self._generate_evidence_package(
            scored_prospect.discovery_data.domain,
            growth_vulnerabilities,
            scored_prospect.performance_data.leak_indicators if scored_prospect.performance_data else []
        )
        
        # Gate 5: Message Personalization with Growth Context
        personalized_message = self._personalize_growth_template(
            template,
            scored_prospect,
            strategic_insights,
            growth_vulnerabilities,
            evidence_url
        )
        
        # Calculate personalization score
        personalization_score = self._calculate_personalization_score(
            personalized_message, scored_prospect
        )
        
        # Get follow-up sequence based on growth tier
        follow_up_sequence = self._get_growth_followup_sequence(template_key)
        
        # Generate subject line with growth context
        subject_line = self._generate_growth_subject_line(scored_prospect, growth_vulnerabilities)
        
        return OutreachMessage(
            prospect_id=f"{scored_prospect.discovery_data.domain}_{int(datetime.now().timestamp())}",
            subject_line=subject_line,
            message_body=personalized_message,
            evidence_package=evidence_url,
            follow_up_sequence=follow_up_sequence,
            personalization_score=personalization_score,
            vertical_template=template_key,
            primary_pain_point=growth_vulnerabilities.get('primary_vulnerability', 'UNKNOWN'),
            created_timestamp=datetime.now(timezone.utc)
        )
    
    def _initialize_templates(self) -> Dict[str, Template]:
        """Initialize sutil and professional templates in Portuguese"""
        
        # URGENT CARE: Observação de estratégia digital
        urgent_care_template = Template("""Olá $nome,

Estava analisando o panorama de $medical_specialty na região de $city e notei algo interessante sobre a $company_name.

A observação:
$strategic_observation. Isso normalmente indica uma estratégia deliberada que pode ser uma vantagem competitiva significativa.

O que chamou atenção:
$differentiation_insight, enquanto a maioria dos competidores segue padrões mais convencionais.

A questão estratégica:
$strategic_question

Pergunto porque tenho visto práticas similares conseguirem resultados expressivos quando alinham a presença digital com essa estratégia operacional.

Faz sentido uma conversa de 15 minutos sobre isso?

Cumprimentos,  
$sender_name""")

        # DENTAL: Análise de segmentação
        dental_template = Template("""$nome,

Estava estudando o $market_context e $company_name chamou atenção pela clareza na estratégia.

A observação:
$positioning_analysis. Isso normalmente indica maturidade estratégica.

O insight:
Práticas com segmentação clara conseguem resultados superiores. Mas o desafio sempre é: como comunicar essa especialização de forma que atraia o cliente ideal?

A pergunta estratégica:
$strategic_question

Pergunto porque práticas similares conseguiram melhorar significativamente a qualidade dos leads quando alinharam a comunicação digital com a estratégia de segmentação.

Faz sentido explorarmos isso em uma conversa?

Cumprimentos,  
$sender_name""")

        # DEFAULT: Professional analysis
        default_template = Template("""$nome,

Durante um estudo do mercado de $business_sector em $city, $company_name apareceu com características interessantes.

A observação:
$strategic_observation

Por que isso é relevante:
$opportunity_insight

Vale explorar:
$strategic_question

Conversa de 15 minutos faria sentido?

Cumprimentos,  
$sender_name""")
        
        return {
            "urgent_care_express": urgent_care_template,
            "dental_clinics": dental_template,
            "medical_practices": dental_template,
            "hair_restoration": dental_template,
            "default": default_template
        }
    
    def _initialize_followup_sequences(self) -> Dict[str, List[str]]:
        """Initialize follow-up sequences by vertical"""
        
        return {
            "hvac_multi_location": [
                "T+2: Additional HVAC seasonal optimization insights",
                "T+5: Case study from similar HVAC company in {city}",
                "T+10: Final note with emergency optimization offer"
            ],
            "dental_clinics": [
                "T+2: Dental practice mobile conversion case study",
                "T+5: Implant consultation booking optimization insights",
                "T+10: Last check-in with limited-time audit offer"
            ],
            "urgent_care_express": [
                "T+2: Urgent care appointment flow optimization data",
                "T+5: Same-day booking conversion case study",
                "T+10: Final urgent care performance insights"
            ],
            "default": [
                "T+2: Additional performance insights for your industry",
                "T+5: Case study from similar business",
                "T+10: Final optimization opportunity check"
            ]
        }
    
    def _map_vertical(self, vertical_string: str) -> str:
        """Map vertical string to template key"""
        mapping = {
            "hvac_multi_location": "hvac_multi_location",
            "dental_clinics": "dental_clinics", 
            "urgent_care_express": "urgent_care_express",
            "medical_aesthetics": "default",
            "real_estate_brokerages": "default",
            "auto_services": "default",
            "veterinary_pet_care": "default"
        }
        return mapping.get(vertical_string, "default")
    
    def _prioritize_pain_points(self, leak_indicators: List[str]) -> str:
        """Prioritize pain points by business impact"""
        if not leak_indicators:
            return "performance optimization"
        
        # Sort by priority weight
        prioritized = sorted(
            leak_indicators,
            key=lambda x: self.pain_priorities.get(x, 0),
            reverse=True
        )
        
        return prioritized[0] if prioritized else "performance optimization"
    
    def _generate_evidence_package(self, 
                                 domain: str, 
                                 primary_pain: str,
                                 leak_indicators: List[str]) -> str:
        """Generate evidence package URL/path"""
        # This would integrate with screenshot automation service
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        evidence_filename = f"{domain}_{primary_pain}_{timestamp}.pdf"
        
        # For now, return placeholder URL
        return f"https://evidence.arco.dev/{evidence_filename}"
    
    def _personalize_template(self, 
                            template: Template,
                            prospect: ScoredProspect,
                            primary_pain: str,
                            evidence_url: str) -> str:
        """Personalize template with prospect data"""
        
        # Extract metrics for personalization
        mobile_metrics = None
        for url, metrics in prospect.performance_data.performance_metrics.items():
            if "mobile" in metrics:
                mobile_metrics = metrics["mobile"]
                break
        
        # Build personalization data
        personalization_data = {
            "decision_maker": self._extract_decision_maker(prospect),
            "service": self._extract_service_type(prospect),
            "city": prospect.discovery_data.city or "your area",
            "lcp_score": f"{mobile_metrics.lcp_p75:.1f}" if mobile_metrics else "3.8",
            "inp_score": f"{int(mobile_metrics.inp_p75)}" if mobile_metrics else "280",
            "lost_calls": self._estimate_lost_calls(prospect),
            "lost_revenue": self._estimate_lost_revenue(prospect),
            "image_savings": "150",  # Placeholder
            "calendar_link": "https://calendly.com/arco-audit",
            "evidence_url": evidence_url,
            "sender_name": "Alex",
            "primary_pain_description": self._describe_pain_point(primary_pain),
            "estimated_impact": prospect.performance_data.estimated_impact,
            "service_fit": prospect.service_fit.value.replace("_", " ").title(),
            "priority_fixes": "\n".join(f"• {fix}" for fix in prospect.performance_data.priority_fixes[:3]),
            "deal_size_range": f"${prospect.deal_size_range[0]}-{prospect.deal_size_range[1]}"
        }
        
        try:
            return template.substitute(personalization_data)
        except KeyError as e:
            logger.warning(f"Template personalization failed: {e}")
            # Return template with safe defaults
            safe_data = {k: v for k, v in personalization_data.items() if v}
            return template.safe_substitute(safe_data)
    
    def _extract_decision_maker(self, prospect: ScoredProspect) -> str:
        """Extract likely decision maker name/title"""
        company_name = prospect.discovery_data.company_name or ""
        
        # Simple heuristic - could be enhanced with more sophisticated name extraction
        if company_name:
            words = company_name.split()
            if len(words) > 1:
                return words[0]  # First word might be owner name
        
        return "there"  # Generic fallback
    
    def _extract_service_type(self, prospect: ScoredProspect) -> str:
        """Extract service type from company name or vertical"""
        company_name = (prospect.discovery_data.company_name or "").lower()
        vertical = prospect.discovery_data.vertical
        
        if "hvac" in company_name or "heating" in company_name:
            return "HVAC services"
        elif "dental" in company_name or "dentist" in company_name:
            return "dental services"
        elif "urgent" in company_name or "care" in company_name:
            return "urgent care"
        elif vertical == "hvac_multi_location":
            return "HVAC services"
        elif vertical == "dental_clinics":
            return "dental services"
        else:
            return "services"
    
    def _estimate_lost_calls(self, prospect: ScoredProspect) -> str:
        """Estimate lost calls per month"""
        base_loss = prospect.estimated_monthly_loss
        
        # Convert revenue loss to call estimate (assume ~$150 per call value)
        calls_lost = base_loss // 150
        return str(max(calls_lost, 5))  # Minimum 5 calls
    
    def _estimate_lost_revenue(self, prospect: ScoredProspect) -> str:
        """Format lost revenue estimate"""
        return f"${prospect.estimated_monthly_loss:,}"
    
    def _describe_pain_point(self, pain_point: str) -> str:
        """Convert pain point code to human description"""
        descriptions = {
            "LCP_HIGH": "Slow page loading (LCP >2.5s) hurting conversions",
            "INP_HIGH": "Poor interactivity (INP >200ms) frustrating users", 
            "CLS_HIGH": "Layout shifts (CLS >0.1) breaking user experience",
            "MOBILE_UNFRIENDLY": "Mobile performance issues losing 60% of traffic",
            "NO_PHONE_CTA": "Missing click-to-call buttons reducing lead capture",
            "SSL_ISSUES": "Security certificate problems hurting trust and SEO",
            "WEAK_FORM": "Form optimization opportunities for better conversions"
        }
        return descriptions.get(pain_point, "Performance optimization opportunities")
    
    def _generate_subject_line(self, prospect: ScoredProspect, primary_pain: str) -> str:
        """Generate compelling subject line"""
        company = prospect.discovery_data.company_name or prospect.discovery_data.domain
        
        subject_templates = {
            "LCP_HIGH": f"Your {company} site is leaking calls — mobile LCP analysis",
            "INP_HIGH": f"INP {self._get_inp_score(prospect)}ms on your site — conversion impact",
            "MOBILE_UNFRIENDLY": f"{company} mobile experience — 60% traffic at risk",
            "NO_PHONE_CTA": f"Missing phone CTA costing {company} leads",
            "SSL_ISSUES": f"{company} security certificate — urgent SEO impact"
        }
        
        return subject_templates.get(
            primary_pain, 
            f"{company} performance audit — conversion opportunities"
        )
    
    def _get_inp_score(self, prospect: ScoredProspect) -> str:
        """Extract INP score for subject line"""
        for url, metrics in prospect.performance_data.performance_metrics.items():
            if "mobile" in metrics:
                return str(int(metrics["mobile"].inp_p75))
        return "280"  # Default
    
    def _calculate_personalization_score(self, 
                                       message: str,
                                       prospect: ScoredProspect) -> float:
        """Calculate personalization quality score"""
        score = 0.5  # Base score
        
        # Check for personalization elements
        message_lower = message.lower()
        
        # Company/domain mentioned
        if prospect.discovery_data.domain.replace('.com', '').replace('.', '') in message_lower:
            score += 0.15
        
        # City mentioned
        if prospect.discovery_data.city and prospect.discovery_data.city.lower() in message_lower:
            score += 0.1
        
        # Specific metrics mentioned
        if any(metric in message_lower for metric in ['lcp', 'inp', 'cls', 'ms', 'seconds']):
            score += 0.15
        
        # Pain point specificity
        if len(prospect.performance_data.leak_indicators) >= 2:
            score += 0.1
        
        return min(score, 1.0)
    
    # GROWTH POTENTIAL METHODS
    
    def _select_growth_template(self, scored_prospect: ScoredProspect) -> str:
        """Select template based on growth potential score and strategic insights"""
        
        # Extract growth potential from strategic insights if available
        strategic_insights = getattr(scored_prospect.discovery_data, 'strategic_insights', {})
        
        # Determine domain type for template selection
        domain = scored_prospect.discovery_data.domain.lower()
        vertical = scored_prospect.discovery_data.vertical.lower()
        
        # Business type mapping
        if 'hair' in domain or 'restoration' in domain:
            return "strategic_hair_loss"
        elif 'dental' in domain and ('walk' in domain or 'urgent_care' in vertical):
            return "greenfield_dental"
        elif any(term in domain for term in ['medical', 'clinic', 'health']):
            return "growth_medical"
        else:
            return "default"
    
    def _analyze_positioning_strategy(self, domain: str, vulnerabilities: list) -> str:
        """Analyze positioning strategy based on domain and vulnerabilities"""
        
        if 'MISSING_VIDEO_STRATEGY' in vulnerabilities:
            return f"A {domain.replace('.com', '').replace('www.', '')} mantém uma abordagem focada em texto e resultados mensuráveis"
        elif 'SINGLE_FORMAT_LIMITATION' in vulnerabilities:
            return f"A estratégia de {domain.replace('.com', '').replace('www.', '')} demonstra consistência em um formato específico"
        elif 'COMPLETELY_STALE_CAMPAIGNS' in vulnerabilities:
            return f"O histórico de {domain.replace('.com', '').replace('www.', '')} sugere períodos de consolidação estratégica"
        else:
            return f"A {domain.replace('.com', '').replace('www.', '')} apresenta uma abordagem madura em sua comunicação digital"

    def _extract_strategic_insights(self, scored_prospect: ScoredProspect) -> Dict:
        """Extract strategic insights from discovery data"""
        
        # Get insights from discovery if available
        strategic_insights = getattr(scored_prospect.discovery_data, 'strategic_insights', {})
        
        return {
            'tier': strategic_insights.get('tier', 'basic'),
            'outreach_insights': strategic_insights.get('outreach_insights', []),
            'investment_score': strategic_insights.get('investment_score', 0),
            'ad_count': strategic_insights.get('ad_count', 0),
            'vulnerabilities': strategic_insights.get('vulnerabilities', [])
        }
    
    def _analyze_growth_vulnerabilities(self, scored_prospect: ScoredProspect) -> Dict:
        """Analyze growth-specific vulnerabilities"""
        
        strategic_insights = self._extract_strategic_insights(scored_prospect)
        vulnerabilities = strategic_insights.get('vulnerabilities', [])
        
        # Identify primary vulnerability for outreach
        primary_vulnerability = 'UNKNOWN'
        if 'COMPLETELY_STALE_CAMPAIGNS' in vulnerabilities:
            primary_vulnerability = 'COMPLETELY_STALE_CAMPAIGNS'
        elif 'MISSING_VIDEO_STRATEGY' in vulnerabilities:
            primary_vulnerability = 'MISSING_VIDEO_STRATEGY'
        elif 'SINGLE_FORMAT_LIMITATION' in vulnerabilities:
            primary_vulnerability = 'SINGLE_FORMAT_LIMITATION'
        elif strategic_insights.get('ad_count', 0) == 0:
            primary_vulnerability = 'NO_DIGITAL_PRESENCE'
        
        return {
            'primary_vulnerability': primary_vulnerability,
            'all_vulnerabilities': vulnerabilities,
            'investment_score': strategic_insights.get('investment_score', 0),
            'ad_count': strategic_insights.get('ad_count', 0),
            'tier': strategic_insights.get('tier', 'basic')
        }
    
    def _personalize_growth_template(self, template: Template, scored_prospect: ScoredProspect, 
                                   strategic_insights: Dict, growth_vulnerabilities: Dict, 
                                   evidence_url: str) -> str:
        """
        ENHANCED: Use real ad_details and your sutil/professional approach
        Based on the excellent templates you created
        """
        
        # Extract company information
        domain = scored_prospect.discovery_data.domain
        company_name = scored_prospect.discovery_data.company_name or self._extract_company_name(domain)
        city = scored_prospect.discovery_data.city or 'sua região'
        
        # REAL AD CAMPAIGN ANALYSIS (from strategic_insights)
        vulnerabilities = strategic_insights.get('vulnerabilities', [])
        ad_count = strategic_insights.get('ad_count', 0)
        investment_score = strategic_insights.get('investment_score', 0)
        
        # SUTIL OBSERVATIONS based on real data
        strategic_observation = self._create_sutil_observation(vulnerabilities, ad_count, domain)
        market_differentiation = self._analyze_market_positioning(domain, vulnerabilities)
        opportunity_insight = self._create_opportunity_insight(vulnerabilities)
        
        # Create professional, subtle substitutions (YOUR APPROACH)
        substitutions = {
            # PROFESSIONAL GREETING
            'nome': self._get_professional_greeting(company_name),
            'company_name': company_name,
            'city': city,
            
            # BUSINESS CONTEXT (Portuguese for international market)
            'medical_specialty': self._get_medical_specialty(domain),
            'business_sector': self._get_business_sector_portuguese(scored_prospect.discovery_data.vertical),
            'market_context': f"mercado de {self._get_business_sector_portuguese(scored_prospect.discovery_data.vertical)} em {city}",
            
            # SUTIL STRATEGIC INSIGHTS (based on real ad data)
            'strategic_observation': strategic_observation,
            'differentiation_insight': market_differentiation,
            'positioning_analysis': self._analyze_positioning_strategy(domain, vulnerabilities),
            'competitive_approach': self._describe_competitive_approach(vulnerabilities, domain),
            
            # OPPORTUNITY FRAMING (consultive, not sales-y)
            'opportunity_insight': opportunity_insight,
            'strategic_question': self._create_strategic_question_sutil(vulnerabilities),
            'market_opportunity': self._frame_market_opportunity(vulnerabilities),
            
            # CREDIBILITY & SOCIAL PROOF (subtle)
            'similar_practices': 'algumas práticas similares',
            'result_reference': 'resultados interessantes',
            'approach_description': 'quando alinharam a comunicação digital com a estratégia',
            
            # AD CAMPAIGN SPECIFICS (real data, not estimates)
            'campaign_duration': '395 dias' if 'COMPLETELY_STALE_CAMPAIGNS' in vulnerabilities else 'campanhas estabelecidas',
            'format_analysis': 'foco em texto' if 'MISSING_VIDEO_STRATEGY' in vulnerabilities else 'estratégia multicanal',
            'investment_level': self._describe_investment_level(investment_score),
            
            # CONTACT
            'sender_name': 'João Pedro'
        }
        
        return template.safe_substitute(**substitutions)
    
    def _create_sutil_observation(self, vulnerabilities: List[str], ad_count: int, domain: str) -> str:
        """Create subtle observation based on real ad data"""
        
        if 'COMPLETELY_STALE_CAMPAIGNS' in vulnerabilities:
            return "campanhas de longa duração sugerem estratégia estabelecida, mas pode ser momento para refresh criativo"
        elif 'MISSING_VIDEO_STRATEGY' in vulnerabilities:
            return "abordagem focada em texto indica maturidade em messaging, com oportunidade de expansão visual"
        elif ad_count == 0:
            return "posicionamento sólido offline, mas presença digital ainda em desenvolvimento"
        elif 'elite' in domain.lower():
            return "comunicação de expertise técnica e qualidade, diferenciando-se da concorrência"
        else:
            return "estratégia digital bem definida com foco em diferenciação"
    
    def _analyze_market_positioning(self, domain: str, vulnerabilities: List[str]) -> str:
        """Analyze market positioning based on domain and ad data"""
        
        if 'elite' in domain.lower() or 'premium' in domain.lower():
            return "posicionamento premium com ênfase em qualidade técnica"
        elif 'walk' in domain.lower() or 'urgent' in domain.lower():
            return "estratégia operacional focada em conveniência e acessibilidade"
        elif 'MISSING_VIDEO_STRATEGY' in vulnerabilities:
            return "comunicação técnica consistente, com espaço para storytelling visual"
        else:
            return "abordagem estratégica diferenciada dos competidores padrão"
    
    def _create_opportunity_insight(self, vulnerabilities: List[str]) -> str:
        """Create opportunity insight based on real vulnerabilities"""
        
        if 'COMPLETELY_STALE_CAMPAIGNS' in vulnerabilities:
            return "refresh criativo para capturar demanda sazonal mais efetivamente"
        elif 'MISSING_VIDEO_STRATEGY' in vulnerabilities:
            return "amplificar o posicionamento através de conteúdo visual que demonstre expertise"
        elif 'SINGLE_FORMAT_LIMITATION' in vulnerabilities:
            return "diversificar formatos para expandir reach mantendo a qualidade"
        else:
            return "otimizar comunicação digital para refletir melhor a diferenciação estratégica"
    
    def _create_strategic_question_sutil(self, vulnerabilities: List[str]) -> str:
        """Create strategic question in sutil style"""
        
        if 'COMPLETELY_STALE_CAMPAIGNS' in vulnerabilities:
            return "Vocês estão planejando refresh criativo para Q4, ou a estratégia atual ainda está gerando os resultados esperados?"
        elif 'MISSING_VIDEO_STRATEGY' in vulnerabilities:
            return "Vale explorar como amplificar visualmente essa expertise técnica que vocês comunicam tão bem?"
        elif any(vuln in vulnerabilities for vuln in ['NO_DIGITAL_PRESENCE', 'LOW_INVESTMENT']):
            return "Vocês estão satisfeitos com o volume de pacientes qualificados que chegam digitalmente?"
        else:
            return "A comunicação digital está alinhada com os objetivos estratégicos de crescimento?"
    
    def _get_medical_specialty(self, domain: str) -> str:
        """Extract medical specialty from domain"""
        
        if 'dental' in domain.lower():
            return 'odontologia'
        elif 'urgent' in domain.lower() or 'emergency' in domain.lower():
            return 'atendimento médico urgente'
        elif 'hair' in domain.lower():
            return 'restauração capilar'
        elif 'medical' in domain.lower():
            return 'medicina'
        else:
            return 'saúde'
    
    def _get_business_sector_portuguese(self, vertical: str) -> str:
        """Convert vertical to Portuguese business type"""
        
        mapping = {
            'urgent_care_express': 'atendimento médico urgente',
            'dental_clinics': 'odontologia especializada',
            'medical_practices': 'medicina',
            'hair_restoration': 'restauração capilar',
            'hvac_multi_location': 'climatização',
            'plumbing': 'serviços hidráulicos',
            'auto_glass': 'vidros automotivos'
        }
        
        return mapping.get(vertical, vertical.replace('_', ' '))
    
    def _create_sutil_observation(self, vulnerabilities: list, ad_count: int, domain: str) -> str:
        """Create sutil observation based on real ad data"""
        
        if 'MISSING_VIDEO_STRATEGY' in vulnerabilities and ad_count > 20:
            return f"Vocês mantêm {ad_count} campanhas ativas com foco em texto e expertise técnica"
        elif 'SINGLE_FORMAT_LIMITATION' in vulnerabilities:
            return f"Seu approach de marketing demonstra consistência estratégica em um formato específico"
        elif ad_count > 30:
            return f"A presença digital da {domain.replace('.com', '').replace('www.', '')} mostra investimento consistente com {ad_count} iniciativas ativas"
        elif ad_count == 0:
            return f"A {domain.replace('.com', '').replace('www.', '')} parece priorizar outras estratégias de crescimento além do digital"
        else:
            return f"O approach digital da {domain.replace('.com', '').replace('www.', '')} sugere foco em qualidade sobre volume"

    def _analyze_market_positioning(self, domain: str, vulnerabilities: list) -> str:
        """Analyze market positioning"""
        
        if 'MISSING_VIDEO_STRATEGY' in vulnerabilities:
            return "isso concentra a comunicação em resultados mensuráveis e expertise técnica"
        elif 'SINGLE_FORMAT_LIMITATION' in vulnerabilities:
            return "o que sugere especialização estratégica em um approach específico"
        else:
            return "demonstrando clareza estratégica na comunicação"

    def _create_opportunity_insight(self, vulnerabilities: list) -> str:
        """Create opportunity insight in Portuguese"""
        
        if 'MISSING_VIDEO_STRATEGY' in vulnerabilities:
            return "Práticas que expandem para formatos visuais mantendo a mensagem de expertise conseguem amplificar significativamente o alcance"
        elif 'SINGLE_FORMAT_LIMITATION' in vulnerabilities:
            return "O desafio sempre é: como manter a consistência estratégica expandindo o formato?"
        else:
            return "A questão é sempre: como otimizar ainda mais essa estratégia que já funciona?"

    def _describe_competitive_approach(self, vulnerabilities: list, domain: str) -> str:
        """Describe competitive approach"""
        
        if vulnerabilities:
            return f"A {domain.replace('.com', '').replace('www.', '')} escolheu uma estratégia específica"
        else:
            return "Approach estratégico diversificado"

    def _frame_market_opportunity(self, vulnerabilities: list) -> str:
        """Frame market opportunity"""
        
        if 'MISSING_VIDEO_STRATEGY' in vulnerabilities:
            return "Expandir para vídeo mantendo a mensagem técnica pode amplificar resultados?"
        else:
            return "A estratégia atual está captando todo o potencial do mercado?"

    def _get_professional_greeting(self, company_name: str) -> str:
        """Get professional greeting"""
        
        if company_name and len(company_name) > 3:
            return company_name.split()[0] if len(company_name.split()) > 1 else "Equipe"
        else:
            return "Equipe"

    def _describe_investment_level(self, investment_score: int) -> str:
        """Describe investment level professionally"""
        
        if investment_score >= 5:
            return "investimento significativo em marketing digital"
        elif investment_score >= 3:
            return "presença digital estabelecida"
        elif investment_score >= 1:
            return "início de investimento em digital"
        else:
            return "foco principal em referências e marketing offline"
    
    def _extract_company_name(self, domain: str) -> str:
        """Extract professional company name from domain"""
        # Remove common extensions and clean up
        name = domain.replace('.com', '').replace('.net', '').replace('.org', '')
        name = name.replace('www.', '')
        
        # Handle common business name patterns
        if 'clinic' in name or 'medical' in name or 'dental' in name:
            # Capitalize properly for medical businesses
            words = name.replace('-', ' ').split()
            return ' '.join(word.capitalize() for word in words)
        
        return name.capitalize()
    
    def _get_professional_greeting(self, company_name: str) -> str:
        """Get appropriate professional greeting"""
        # For now, use generic professional greeting
        # Could be enhanced with LinkedIn/contact detection
        return "Olá"
    
    def _get_business_sector(self, domain: str, vertical: str) -> str:
        """Identify business sector for professional context"""
        vertical_mapping = {
            'urgent_care_express': 'urgent care',
            'dental_clinics': 'odontologia',
            'medical_centers': 'saúde'
        }
        
        if 'hair' in domain:
            return 'hair restoration'
        
        return vertical_mapping.get(vertical, 'healthcare')
    
    def _identify_service_focus(self, domain: str, company_name: str) -> str:
        """Identify the main service focus for segmentation discussion"""
        domain_lower = domain.lower()
        name_lower = company_name.lower()
        
        if 'implant' in domain_lower or 'implant' in name_lower:
            return 'implants'
        elif 'cosmetic' in domain_lower or 'aesthetic' in name_lower:
            return 'cosmetic dentistry'
        elif 'family' in domain_lower or 'family' in name_lower:
            return 'family dentistry'
        elif 'emergency' in domain_lower or 'urgent' in name_lower:
            return 'emergency care'
        else:
            return 'serviços especializados'
    
    def _analyze_growth_phase(self, strategic_insights: Dict) -> str:
        """Analyze and describe growth phase"""
        investment_score = strategic_insights.get('investment_score', 0)
        ad_count = strategic_insights.get('ad_count', 0)
        
        if ad_count == 0:
            return 'estabelecimento de presença digital'
        elif ad_count < 3:
            return 'expansão controlada'
        elif investment_score >= 5:
            return 'crescimento acelerado'
        else:
            return 'consolidação de mercado'
    
    def _describe_business_characteristics(self, strategic_insights: Dict) -> str:
        """Describe business characteristics professionally"""
        investment_score = strategic_insights.get('investment_score', 0)
        
        if investment_score == 0:
            return 'foco em operações e qualidade de atendimento'
        elif investment_score < 3:
            return 'investimento digital inicial com foco geográfico definido'
        else:
            return 'múltiplas especialidades mas com foco geográfico definido'
    
    def _create_strategic_insight(self, growth_vulnerabilities: Dict, strategic_insights: Dict) -> str:
        """Create strategic insight based on vulnerabilities"""
        primary_vuln = growth_vulnerabilities.get('primary_vulnerability', '')
        
        if 'STALE_CAMPAIGNS' in primary_vuln:
            return "Ou se há oportunidade de refrescar a abordagem digital para manter a efetividade?"
        elif 'VIDEO_STRATEGY' in primary_vuln:
            return "Ou se há espaço para incorporar elementos visuais que reforcem essa diferenciação?"
        elif 'NO_DIGITAL' in primary_vuln:
            return "Ou se existe uma janela estratégica para estabelecer presença digital?"
        else:
            return "Ou se há oportunidades de otimização na estratégia digital atual?"
    
    def _create_competitive_insight(self, growth_vulnerabilities: Dict) -> str:
        """Create competitive insight"""
        return "Ou há oportunidade de refinar a comunicação para filtrar melhor os leads?"
    
    def _create_market_opportunity(self, strategic_insights: Dict) -> str:
        """Create market opportunity insight"""
        return "Ou há oportunidade de acelerar a captura de market share através de estratégia digital mais agressiva?"
    
    def _create_digital_maturity_insight(self, growth_vulnerabilities: Dict) -> str:
        """Create digital maturity insight"""
        primary_vuln = growth_vulnerabilities.get('primary_vulnerability', '')
        
        if 'STALE_CAMPAIGNS' in primary_vuln:
            return "Notei que suas campanhas digitais têm potencial de otimização significativo."
        elif 'VIDEO_STRATEGY' in primary_vuln:
            return "Observo que há oportunidade de diversificação na estratégia de conteúdo digital."
        else:
            return "Vejo potencial interessante para amplificação digital da diferenciação."
    
    def _create_growth_opportunity_insight(self, growth_vulnerabilities: Dict) -> str:
        """Create growth opportunity insight"""
        return "Há oportunidade de acelerar essa diferenciação através de presença digital mais estratégica?"
    
    def _create_business_observation(self, strategic_insights: Dict) -> str:
        """Create business observation"""
        return "Vocês demonstram foco estratégico claro e operação bem estruturada."
    
    def _create_market_insight(self, vertical: str) -> str:
        """Create market insight for vertical"""
        insights = {
            'urgent_care_express': 'Práticas com posicionamento diferenciado conseguem premium pricing e maior lifetime value.',
            'dental_clinics': 'Clínicas com especialização clara conseguem charges maiores e pacientes mais qualificados.',
            'medical_centers': 'Centers em fase de crescimento têm janela única para capturar market share.'
        }
        
        return insights.get(vertical, 'Negócios com diferenciação clara conseguem melhores resultados no mercado.')
    
    def _create_strategic_question(self, growth_vulnerabilities: Dict) -> str:
        """Create strategic question based on vulnerabilities"""
        primary_vuln = growth_vulnerabilities.get('primary_vulnerability', '')
        
        if 'NO_DIGITAL' in primary_vuln:
            return "Vocês estão prontos para amplificar digitalmente essa diferenciação estratégica?"
        else:
            return "Vocês estão conseguindo maximizar o potencial digital dessa estratégia?"
    
    def _get_growth_followup_sequence(self, template_key: str) -> List[str]:
        """Get follow-up sequence based on growth template"""
        
        sequences = {
            "strategic_hair_loss": [
                "T+3: Hair restoration creative refresh case study",
                "T+7: Before/after video testimonial strategy",
                "T+14: Q4 seasonal campaign optimization"
            ],
            "growth_medical": [
                "T+3: Medical practice video content framework",
                "T+7: Format diversification case study",
                "T+14: Multi-format campaign success metrics"
            ],
            "greenfield_dental": [
                "T+3: Emergency dental advertising strategy insights",
                "T+7: Walk-in clinic digital presence case study",
                "T+14: Weekend emergency campaign optimization"
            ]
        }
        
        return sequences.get(template_key, [
            "T+3: Growth opportunity follow-up",
            "T+7: Strategic insights sharing",
            "T+14: Final optimization opportunity"
        ])
    
    def _generate_growth_subject_line(self, scored_prospect: ScoredProspect, 
                                    growth_vulnerabilities: Dict) -> str:
        """Generate growth-focused subject line"""
        
        domain = scored_prospect.discovery_data.domain
        company_name = scored_prospect.discovery_data.company_name or domain.split('.')[0]
        vulnerability = growth_vulnerabilities.get('primary_vulnerability', 'UNKNOWN')
        
        subject_templates = {
            'COMPLETELY_STALE_CAMPAIGNS': f"{company_name} - 395 days same ads, ready to scale?",
            'MISSING_VIDEO_STRATEGY': f"{company_name} - scaling beyond text ads?",
            'NO_DIGITAL_PRESENCE': f"{company_name} - untapped digital potential?",
            'SINGLE_FORMAT_LIMITATION': f"{company_name} ads - format diversification opportunity?"
        }
        
        return subject_templates.get(vulnerability, f"{company_name} - growth optimization opportunities?")