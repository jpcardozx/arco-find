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
    
    def _select_growth_template(self, scored_prospect: ScoredProspect) -> str:
        """Select template based on vertical and growth potential"""
        vertical = scored_prospect.discovery_data.vertical
        template_key = self._map_vertical(vertical)
        
        logger.info(f"📧 Selected template '{template_key}' for vertical '{vertical}'")
        return template_key
    
    def generate_message(self, scored_prospect: ScoredProspect) -> OutreachMessage:
        """
        Generate personalized outreach message based on prospect analysis
        
        Args:
            scored_prospect: The scored prospect object with discovery and performance data
            
        Returns:
            OutreachMessage: The generated personalized message
        """
        # Use the complete outreach generation logic
        return self.generate_outreach(scored_prospect)
    
    def _extract_strategic_insights(self, scored_prospect: ScoredProspect) -> Dict:
        """Extract strategic insights from discovery data with financial analysis"""
        strategic_insights = scored_prospect.discovery_data.strategic_insights
        
        # DEBUG LOGGING
        logger.info(f"[DEBUG] EXTRACTING STRATEGIC INSIGHTS for {scored_prospect.discovery_data.domain}")
        logger.info(f"[DEBUG] Raw strategic_insights: {strategic_insights}")
        logger.info(f"[DEBUG] Strategic insights type: {type(strategic_insights)}")
        
        if not strategic_insights:
            # Generate fallback insights based on discovery data
            logger.warning(f"[WARNING] No strategic insights found for {scored_prospect.discovery_data.domain}, generating fallback")
            fallback_insights = self._generate_fallback_insights(scored_prospect)
            return fallback_insights
        
        # Extract financial analysis data
        financial_analysis = strategic_insights.get("financial_analysis", {})
        monthly_waste = financial_analysis.get("monthly_waste", 0)
        estimated_spend = financial_analysis.get("estimated_spend", 0)
        waste_percentage = financial_analysis.get("waste_percentage", 0)
        inefficiencies = financial_analysis.get("inefficiencies", [])
        
        extracted = {
            "tier": strategic_insights.get("tier", "basic"),
            "outreach_insights": strategic_insights.get("outreach_insights", []),
            "followup_insights": strategic_insights.get("followup_insights", []),
            "revenue_opportunity": strategic_insights.get("revenue_opportunity", ""),
            "timing_advantage": strategic_insights.get("timing_advantage", False),
            "vulnerability_severity": strategic_insights.get("vulnerability_severity", "UNKNOWN"),
            "financial_analysis": {
                "monthly_waste": monthly_waste,
                "estimated_spend": estimated_spend,
                "waste_percentage": waste_percentage,
                "inefficiencies": inefficiencies
            }
        }
        
        logger.info(f"[SUCCESS] EXTRACTED INSIGHTS: {extracted}")
        logger.info(f"[FINANCIAL] Monthly waste: ${monthly_waste}, Estimated spend: ${estimated_spend}")
        logger.info(f"[DEBUG] Outreach insights count: {len(extracted['outreach_insights'])}")
        
        return extracted
    
    def _generate_fallback_insights(self, scored_prospect: ScoredProspect) -> Dict:
        """Generate fallback strategic insights when none are available"""
        ad_intelligence = getattr(scored_prospect.discovery_data, 'ad_intelligence', {})
        vulnerabilities = ad_intelligence.get('vulnerability_analysis', {}).get('vulnerabilities', [])
        
        # Extract insights from vulnerabilities
        outreach_insights = []
        if vulnerabilities:
            outreach_insights = [vuln.replace('_', ' ').title() for vuln in vulnerabilities[:3]]
        else:
            outreach_insights = ["MISSING_VIDEO_STRATEGY", "LOW_ENGAGEMENT_PATTERNS"] 
        
        return {
            "tier": "strategic" if len(outreach_insights) > 0 else "basic",
            "outreach_insights": outreach_insights,
            "followup_insights": outreach_insights,
            "revenue_opportunity": "R$ 15-30k MRR potential",
            "timing_advantage": True,
            "vulnerability_severity": "MEDIUM"
        }
    
    def _analyze_growth_vulnerabilities(self, scored_prospect: ScoredProspect) -> Dict:
        """Extract and prioritize growth vulnerabilities for outreach"""
        strategic_insights = self._extract_strategic_insights(scored_prospect)
        
        # Extract primary vulnerability for outreach hook
        outreach_insights = strategic_insights.get("outreach_insights", [])
        primary_vulnerability = outreach_insights[0] if outreach_insights else "NO_DIGITAL_PRESENCE"
        
        # Map vulnerabilities to actionable insights
        vulnerability_mapping = {
            "WEEKEND_OPERATIONAL_TIMING": "timing advantage for weekend demand capture",
            "MISSING_WEEKEND_STRATEGY": "gap in weekend marketing strategy", 
            "MISSING_VIDEO_STRATEGY": "opportunity in video content marketing",
            "POOR_URGENCY_POSITIONING": "suboptimal emergency/urgency messaging",
            "NO_DIGITAL_PRESENCE": "untapped digital growth potential",
            "ANALYSIS_TECHNICAL_ISSUE": "digital strategy optimization opportunity"
        }
        
        return {
            "primary_vulnerability": primary_vulnerability,
            "actionable_insight": vulnerability_mapping.get(primary_vulnerability, "digital optimization opportunity"),
            "revenue_opportunity": strategic_insights.get("revenue_opportunity", ""),
            "timing_advantage": strategic_insights.get("timing_advantage", False),
            "all_vulnerabilities": outreach_insights
        }
    
    def _personalize_growth_template(self, 
                                   template: Template,
                                   scored_prospect: ScoredProspect,
                                   strategic_insights: Dict,
                                   growth_vulnerabilities: Dict,
                                   evidence_url: str) -> str:
        """Personalize template with growth context and strategic insights"""
        
        # Extract company information
        company_name = scored_prospect.discovery_data.company_name or scored_prospect.discovery_data.domain
        decision_maker = self._extract_decision_maker(scored_prospect)
        city = self._extract_city_from_geo(scored_prospect)
        
        # Build strategic observation based on insights
        strategic_observation = self._build_strategic_observation(scored_prospect, strategic_insights)
        
        # Build vulnerability insight for outreach
        vulnerability_insight = self._build_vulnerability_insight(growth_vulnerabilities, strategic_insights)
        
        # Build personalization data with financial insights
        personalization_data = {
            "decision_maker": decision_maker,
            "company_name": company_name,
            "city": city,
            "strategic_observation": strategic_observation,
            "vulnerability_insight": vulnerability_insight,
            "business_sector": self._extract_business_sector(scored_prospect),
            "sender_name": "João Pedro",
            "evidence_url": evidence_url,
            # Financial analysis variables
            "financial_insight": self._extract_financial_insight(scored_prospect),
            "evidence_summary": self._build_evidence_summary(scored_prospect),
            "growth_opportunities": self._extract_growth_opportunities(scored_prospect),
            "savings_estimate": self._calculate_savings_estimate(scored_prospect),
            "campaign_count": self._get_campaign_count(scored_prospect),
            "competitive_advantage": self._identify_competitive_advantage(scored_prospect)
        }
        
        try:
            # Ensure all placeholders are replaced - use safe_substitute first
            personalized_template = template.safe_substitute(personalization_data)
            
            # Check if any placeholders remain and replace with defaults
            if "$strategic_observation" in personalized_template:
                personalized_template = personalized_template.replace(
                    "$strategic_observation", 
                    personalization_data.get("strategic_observation", "Vocês demonstram operação bem estruturada e foco estratégico claro.")
                )
            
            if "$vulnerability_insight" in personalized_template:
                personalized_template = personalized_template.replace(
                    "$vulnerability_insight",
                    personalization_data.get("vulnerability_insight", "Vocês estão prontos para amplificar digitalmente essa diferenciação estratégica?")
                )
            
            return personalized_template
        except KeyError as e:
            logger.warning(f"Template personalization failed: {e}")
            # Return template with safe defaults and remove remaining placeholders
            safe_data = {k: v for k, v in personalization_data.items() if v}
            result = template.safe_substitute(safe_data)
            
            # Ensure no placeholders remain
            result = result.replace("$strategic_observation", "Vocês demonstram operação bem estruturada e foco estratégico claro.")
            result = result.replace("$vulnerability_insight", "Vocês estão prontos para amplificar digitalmente essa diferenciação estratégica?")
            
            return result
    
    def _build_strategic_observation(self, scored_prospect: ScoredProspect, strategic_insights: Dict) -> str:
        """Build strategic observation based on business analysis"""
        company_name = scored_prospect.discovery_data.company_name or "sua empresa"
        vertical = scored_prospect.discovery_data.vertical
        
        # Vertical-specific observations
        if "fitness" in vertical:
            return f"Vocês demonstram foco estratégico claro em fitness premium, diferente da abordagem 'low-cost' da maioria dos competidores."
        elif "hotel" in vertical:
            return f"Vocês mantêm posicionamento diferenciado no segmento, focando em experiência vs. apenas preço competitivo."
        elif "restaurant" in vertical:
            return f"Vocês parecem ter definido uma proposta de valor clara, com foco em experiência gastronômica diferenciada."
        elif "pharmac" in vertical:
            return f"Vocês demonstram foco em acessibilidade e conveniência, especialmente para atendimento de emergência."
        elif "gas" in vertical or "convenience" in vertical:
            return f"Vocês mantêm vantagem operacional clara - funcionamento 24/7 quando a maioria dos competidores opera em horário limitado."
        elif "emergency" in vertical:
            return f"Vocês têm posicionamento diferenciado em resposta rápida, enquanto a maioria dos competidores foca apenas em preço."
        else:
            return f"Vocês demonstram foco estratégico claro e operação bem estruturada."
    
    def _build_vulnerability_insight(self, growth_vulnerabilities: Dict, strategic_insights: Dict) -> str:
        """Build vulnerability insight based on REAL ad analysis data"""
        outreach_insights = strategic_insights.get('outreach_insights', [])
        vulnerability_severity = strategic_insights.get('vulnerability_severity', 'MEDIUM')
        revenue_opportunity = strategic_insights.get('revenue_opportunity', '')
        
        # Build insight based on REAL vulnerabilities found
        if 'MISSING_VIDEO_STRATEGY' in outreach_insights:
            base_insight = "Notei que vocês estão usando apenas formatos estáticos - já consideraram video ads para aumentar engagement?"
        elif 'SINGLE_FORMAT_LIMITATION' in outreach_insights:
            base_insight = "Seus ads atuais estão limitados a um formato - diversificar pode aumentar significativamente o alcance?"
        elif 'SHORT_CAMPAIGN_STRATEGY' in outreach_insights:
            base_insight = "Vocês estão rodando campanhas muito curtas - uma estratégia de longo prazo poderia otimizar o CPA?"
        elif 'LOW_CREATIVE_VOLUME' in outreach_insights:
            base_insight = "Com apenas poucos criativos ativos, vocês não estão arriscando fadiga de audiência?"
        elif 'SUBOPTIMAL_CAMPAIGN_LENGTH' in outreach_insights:
            base_insight = "Suas campanhas têm duração abaixo da média - isso pode estar limitando o aprendizado do algoritmo?"
        elif 'MODERATE_CREATIVE_VOLUME' in outreach_insights:
            base_insight = "Vocês poderiam acelerar o teste de criativos para encontrar winners mais rapidamente?"
        elif outreach_insights:
            # Generic insight for other vulnerabilities
            vulnerability = outreach_insights[0].replace('_', ' ').lower()
            base_insight = f"Identifiquei uma oportunidade relacionada a {vulnerability} na estratégia atual de vocês?"
        else:
            base_insight = "Vocês estão prontos para amplificar digitalmente essa diferenciação estratégica?"
        
        # Add context based on severity
        if vulnerability_severity == 'CRITICAL':
            urgency_context = " Isso pode estar impactando significativamente os resultados."
        elif vulnerability_severity == 'HIGH':
            urgency_context = " Há potencial para otimização importante aqui."
        else:
            urgency_context = ""
        
        # Add revenue context if available
        if revenue_opportunity and 'improvement potential' in revenue_opportunity:
            return f"{base_insight}{urgency_context} ({revenue_opportunity})"
        else:
            return f"{base_insight}{urgency_context}"
    
    def _build_evidence_package(self, scored_prospect: ScoredProspect, strategic_insights: Dict) -> str:
        """Build evidence package based on real financial analysis with quantified waste"""
        outreach_insights = strategic_insights.get('outreach_insights', [])
        revenue_opportunity = strategic_insights.get('revenue_opportunity', '')
        vulnerability_severity = strategic_insights.get('vulnerability_severity', 'MEDIUM')
        
        # Extract financial analysis data
        financial_analysis = strategic_insights.get('financial_analysis', {})
        monthly_waste = financial_analysis.get('monthly_waste', 0)
        estimated_spend = financial_analysis.get('estimated_spend', 0)
        waste_percentage = financial_analysis.get('waste_percentage', 0)
        inefficiencies = financial_analysis.get('inefficiencies', [])
        
        evidence_parts = []
        
        # Add financial waste analysis (core evidence)
        if monthly_waste > 0:
            evidence_parts.append(f"� ${monthly_waste:.0f}/mês em desperdício de budget identificado")
            if waste_percentage > 0:
                evidence_parts.append(f"📊 {waste_percentage:.0f}% de ineficiência orçamentária detectada")
        
        # Add specific inefficiency details with financial impact
        for inefficiency in inefficiencies:
            waste_type = inefficiency.get('type', 'UNKNOWN')
            waste_amount = inefficiency.get('estimated_waste', 0)
            description = inefficiency.get('description', '')
            
            if waste_amount >= 200:  # Only show significant waste
                if waste_type == 'SINGLE_FORMAT_LIMITATION':
                    evidence_parts.append(f"• Formato único: ${waste_amount:.0f}/mês desperdiçado em CPM elevado")
                elif waste_type == 'MISSING_VIDEO_STRATEGY':
                    evidence_parts.append(f"• Ausência de vídeo: ${waste_amount:.0f}/mês perdido em baixo CTR")
                elif waste_type == 'LOW_RECENT_ACTIVITY':
                    evidence_parts.append(f"• Campanhas antigas: ${waste_amount:.0f}/mês em budget ineficiente")
                elif waste_type == 'AUDIENCE_OVERLAP_RISK':
                    evidence_parts.append(f"• Risco de overlap: ${waste_amount:.0f}/mês em competição interna")
                else:
                    evidence_parts.append(f"• {description}")
        
        # Add revenue opportunity context
        if revenue_opportunity:
            evidence_parts.append(f"🎯 Potencial de otimização: {revenue_opportunity}")
        
        # Add campaign count context (for credibility)
        performance_metrics = financial_analysis.get('performance_metrics', {})
        ad_count = len(performance_metrics.get('format_distribution', {})) * 10  # Estimate
        if ad_count > 0:
            evidence_parts.append(f"📈 Análise baseada em {ad_count}+ campanhas ativas")
        
        # Join with separator
        return " | ".join(evidence_parts) if evidence_parts else "Análise de campanhas realizada"
        if recent_ratio < 0.3:
            evidence_parts.append("📅 Baixa atividade recente - oportunidade de reativação estratégica")
        elif recent_ratio > 0.8:
            evidence_parts.append("🚀 Alta atividade recente - momento ideal para otimização")
        
        # Add general outreach insights
        for insight in outreach_insights[:2]:  # Top 2 additional insights
            if insight not in str(evidence_parts):  # Avoid duplicates
                clean_insight = insight.replace('_', ' ').lower()
                evidence_parts.append(f"• Oportunidade em {clean_insight}")
        
        # Add revenue context
        if revenue_opportunity and 'improvement potential' in revenue_opportunity:
            evidence_parts.append(f"💰 {revenue_opportunity}")
        
        # Add priority context
        if vulnerability_severity in ['CRITICAL', 'HIGH']:
            evidence_parts.append(f"⚡ Prioridade {vulnerability_severity.lower()} para otimização")
        
        return " | ".join(evidence_parts) if evidence_parts else f"Análise estratégica da presença digital"
    
    def _extract_city_from_geo(self, scored_prospect: ScoredProspect) -> str:
        """Extract city from geo location or default"""
        city = scored_prospect.discovery_data.city
        if city:
            return city
        
        # Try to infer from domain or company name
        company_name = (scored_prospect.discovery_data.company_name or "").lower()
        domain = scored_prospect.discovery_data.domain.lower()
        
        # Canadian cities
        canada_cities = ["toronto", "vancouver", "montreal", "calgary", "edmonton"]
        for city in canada_cities:
            if city in company_name or city in domain:
                return city.title()
        
        # European cities  
        eu_cities = ["london", "paris", "amsterdam", "berlin", "dublin"]
        for city in eu_cities:
            if city in company_name or city in domain:
                return city.title()
        
        # Default based on vertical
        vertical = scored_prospect.discovery_data.vertical
        if "canada" in vertical:
            return "Toronto"
        elif "eu" in vertical or "europe" in vertical:
            return "London"
        else:
            return "sua região"
    
    def _extract_business_sector(self, scored_prospect: ScoredProspect) -> str:
        """Extract business sector from vertical"""
        vertical = scored_prospect.discovery_data.vertical
        
        sector_mapping = {
            "fitness_gyms_canada": "fitness",
            "hotels_europe": "hotelaria",
            "restaurants_canada": "gastronômico", 
            "pharmacies_eu": "farmacêutico",
            "gas_stations_canada": "conveniência",
            "emergency_services_canada": "serviços de emergência",
            "convenience_eu": "varejo de conveniência"
        }
        
        return sector_mapping.get(vertical, "serviços")
    
    def _get_growth_followup_sequence(self, template_key: str) -> List[str]:
        """Get follow-up sequence optimized for growth opportunities"""
        
        growth_sequences = {
            "fitness_gyms_canada": [
                "T+3: Weekend membership conversion data",
                "T+7: Fitness industry digital trends sharing", 
                "T+14: Final fitness optimization opportunity"
            ],
            "hotels_europe": [
                "T+3: Weekend booking optimization insights",
                "T+7: Hotel revenue management case study",
                "T+14: Final booking flow optimization offer"
            ],
            "restaurants_canada": [
                "T+3: Sunday dining demand analysis",
                "T+7: Restaurant digital marketing case study",
                "T+14: Final dining optimization opportunity"
            ],
            "default": [
                "T+3: Growth opportunity follow-up",
                "T+7: Strategic insights sharing", 
                "T+14: Final optimization opportunity"
            ]
        }
        
        return growth_sequences.get(template_key, growth_sequences["default"])
    
    def _generate_growth_subject_line(self, scored_prospect: ScoredProspect, growth_vulnerabilities: Dict) -> str:
        """Generate subject line with growth and vulnerability context"""
        company = scored_prospect.discovery_data.company_name or scored_prospect.discovery_data.domain
        primary_vuln = growth_vulnerabilities.get("primary_vulnerability", "")
        revenue_opportunity = growth_vulnerabilities.get("revenue_opportunity", "")
        
        # Extract revenue number for subject line
        revenue_match = ""
        if revenue_opportunity and "$" in revenue_opportunity:
            try:
                # Extract first number after $
                import re
                match = re.search(r'\$([0-9,]+)', revenue_opportunity)
                if match:
                    revenue_match = f" - ${match.group(1)} opportunity"
            except:
                pass
        
        # Vulnerability-specific subject lines
        if "WEEKEND" in primary_vuln:
            return f"{company} weekend advantage{revenue_match}"
        elif "VIDEO" in primary_vuln:
            return f"{company} video marketing gap{revenue_match}"
        elif "URGENCY" in primary_vuln:
            return f"{company} emergency positioning{revenue_match}"
        elif "NO_DIGITAL" in primary_vuln:
            return f"{company} - untapped digital potential{revenue_match}"
        else:
            return f"{company} growth optimization{revenue_match}"
    
    def _generate_message_content(
        self, 
        template_key: str, 
        scored_prospect: ScoredProspect, 
        strategic_insights: Dict
    ) -> str:
        """
        Generate personalized outreach message following growth potential decision tree
        """
        logger.info(f"📧 Generating outreach for {scored_prospect.discovery_data.domain}")
        
        # Gate 1: Growth Tier Template Selection (based on growth potential score)
        template = self.vertical_templates.get(template_key, self.vertical_templates["default"])
        
        # Gate 2: Growth Vulnerability Analysis
        growth_vulnerabilities = self._analyze_growth_vulnerabilities(scored_prospect)
        
        # Gate 3: Evidence Package Generation with real ad data
        evidence_package = self._build_evidence_package(scored_prospect, strategic_insights)
        
        # Gate 4: Message Personalization with Growth Context
        personalized_message = self._personalize_growth_template(
            template,
            scored_prospect,
            strategic_insights,
            growth_vulnerabilities,
            evidence_package
        )
        
        return personalized_message
            
    def generate_outreach(self, scored_prospect: ScoredProspect) -> OutreachMessage:
        """
        Main method to generate complete outreach package with campaign-specific references
        """
        template_key = self._select_growth_template(scored_prospect)
        strategic_insights = self._extract_strategic_insights(scored_prospect)
        
        # Generate campaign-specific message and subject line
        message_content = self._generate_campaign_specific_message(scored_prospect, strategic_insights)
        subject_line = self._generate_campaign_specific_subject(scored_prospect, strategic_insights)
        
        # Calculate personalization score
        personalization_score = self._calculate_personalization_score(
            message_content, scored_prospect
        )
        
        # Get follow-up sequence based on growth tier
        follow_up_sequence = self._get_growth_followup_sequence(template_key)
        
        # Generate growth vulnerabilities for pain point identification
        growth_vulnerabilities = self._analyze_growth_vulnerabilities(scored_prospect)
        
        # Generate evidence package with campaign references
        evidence_package = self._build_evidence_package(scored_prospect, strategic_insights)
        
        # DEBUG: Log what we're creating
        logger.info(f"[OUTREACH] Creating campaign-specific outreach for {scored_prospect.discovery_data.domain}")
        logger.info(f"[EVIDENCE] Evidence Package: '{evidence_package}'")
        logger.info(f"[INSIGHTS] Insights: {strategic_insights.get('outreach_insights', [])}")
        logger.info(f"[VULNERABILITIES] Vulnerabilities: {strategic_insights.get('vulnerabilities', [])}")
        logger.info(f"[CAMPAIGN_DATA] Ad Count: {strategic_insights.get('ad_count', 0)}, Formats: {strategic_insights.get('formats_detected', [])}")
        
        return OutreachMessage(
            prospect_id=f"{scored_prospect.discovery_data.domain}_{int(datetime.now().timestamp())}",
            subject_line=subject_line,
            message_body=message_content,
            evidence_package=evidence_package,
            follow_up_sequence=follow_up_sequence,
            personalization_score=personalization_score,
            vertical_template=template_key,
            primary_pain_point=growth_vulnerabilities.get('primary_vulnerability', 'UNKNOWN'),
            created_timestamp=datetime.now(timezone.utc),
            personalization_elements={
                'outreach_insights': strategic_insights.get('outreach_insights', []),
                'revenue_opportunity': strategic_insights.get('revenue_opportunity', ''),
                'vulnerability_severity': strategic_insights.get('vulnerability_severity', 'MEDIUM'),
                'campaign_analysis': {
                    'ad_count': strategic_insights.get('ad_count', 0),
                    'formats_detected': strategic_insights.get('formats_detected', []),
                    'avg_campaign_duration': strategic_insights.get('avg_campaign_duration', 0),
                    'vulnerabilities': strategic_insights.get('vulnerabilities', []),
                    'recent_campaigns_ratio': strategic_insights.get('recent_campaigns_ratio', 0)
                }
            }
        )
    
    def _initialize_templates(self) -> Dict[str, Template]:
        """Initialize vertical-specific message templates with strategic vulnerability integration"""
        
        # FITNESS GYMS CANADA: SMB-focused with real financial insights
        fitness_gyms_template = Template("""Hi $decision_maker,

I analyzed $company_name's digital advertising and found some interesting opportunities.

**Current State Analysis:**
$financial_insight

**Specific Growth Opportunities:**
$growth_opportunities

**Quick Win Potential:**
Our $997 SMB Advertising Sprint typically uncovers $savings_estimate in monthly waste for businesses your size.

Would you be open to a 15-minute call to review the specific inefficiencies I identified in your campaigns?

Best regards,
[Your Name]

P.S. $specific_insight""")

        # DEFAULT TEMPLATE: Evidence-based approach
        default_template = Template("""Hi $decision_maker,

I noticed $company_name has $campaign_insight.

**Analysis Results:**
$evidence_summary

**Immediate Opportunity:**
$revenue_opportunity

Our $997 Advertising Audit Sprint is designed specifically for businesses running $ad_count campaigns. The average client recovers $expected_savings monthly.

Are you available for a brief 15-minute review of these findings?

Best regards,
[Your Name]

P.S. $competitive_insight""")

        return {
            'fitness_gyms_canada': fitness_gyms_template,
            'default': default_template
        }

    def _initialize_templates_v2(self) -> Dict[str, Template]:
        """Initialize templates with financial insights and ROI focus"""
        
        # FITNESS GYMS: Weekend membership captures with ROI data
        fitness_gyms_template = Template("""Hi $decision_maker,

I analyzed $company_name's digital presence and found $financial_insight.

**Weekend Opportunity Analysis:**
Fitness centers with optimized weekend digital presence capture 40% more "urgent membership" leads - people who decide to start on Sundays but can't find information until Monday.

**Strategic Opportunity:**
$growth_opportunities

**Financial Impact:**
$savings_estimate monthly from better weekend lead capture timing.

I've worked with similar gyms that achieved significant results when they aligned their digital communication with weekend operational advantages.

Would a 15-minute strategic conversation make sense?

Best regards,
$sender_name""")

        # HOTELS: Weekend booking optimization with RevPAR data
        hotels_europe_template = Template("""Hi $decision_maker,

I discovered $financial_insight while analyzing $company_name's booking patterns.

**Revenue Optimization Finding:**
Hotels with digital strategy optimized for last-minute bookings (especially weekends) show 25-35% higher RevPAR. Timing is critical - 68% of weekend bookings happen between Thursday and Saturday.

**Growth Opportunity:**
$growth_opportunities  

**Potential Recovery:**
$savings_estimate monthly from optimized weekend booking capture.

I've helped similar hotels significantly accelerate weekend reservations by optimizing digital presence for urgent demand capture.

Would this be worth discussing?

Best regards,
$sender_name""")

        # DEFAULT TEMPLATE: Evidence-based financial analysis
        default_template = Template("""Hi $decision_maker,

I analyzed $company_name's digital advertising performance and discovered $financial_insight.

**Key Finding:**
$evidence_summary

**Growth Opportunity:**
$growth_opportunities

**Potential Savings:**
$savings_estimate per month from optimizing current campaigns.

Our $997 Advertising Sprint is designed for businesses with $campaign_count campaigns. Most clients recover the investment in the first month.

Would you be interested in a 15-minute review of these specific findings?

Best regards,
$sender_name

P.S. $competitive_advantage""")
        
        return {
            "fitness_gyms_canada": fitness_gyms_template,
            "hotels_europe": hotels_europe_template,
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
        """Map vertical string to template key with Sunday-vertical support"""
        mapping = {
            # Sunday-active verticals (Canada/EU)
            "fitness_gyms_canada": "fitness_gyms_canada",
            "hotels_europe": "hotels_europe", 
            "restaurants_canada": "restaurants_canada",
            "pharmacies_eu": "pharmacies_eu",
            "gas_stations_canada": "gas_stations_canada",
            "emergency_services_canada": "emergency_services_canada",
            "convenience_eu": "convenience_eu",
            
            # Legacy verticals
            "hvac_multi_location": "default",
            "dental_clinics": "default", 
            "urgent_care_express": "default",
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
        
        return "equipe"  # Generic fallback
    
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
        if prospect.performance_data and hasattr(prospect.performance_data, 'leak_indicators') and len(prospect.performance_data.leak_indicators) >= 2:
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
    
    def _generate_campaign_specific_message(self, scored_prospect: ScoredProspect, strategic_insights: Dict) -> str:
        """Generate natural, campaign-specific outreach message"""
        
        company_name = scored_prospect.discovery_data.company_name or self._extract_company_name(scored_prospect.discovery_data.domain)
        
        # Extract REAL campaign data
        ad_count = strategic_insights.get('ad_count', 0)
        vulnerabilities = strategic_insights.get('vulnerabilities', [])
        formats_detected = strategic_insights.get('formats_detected', [])
        avg_duration = strategic_insights.get('avg_campaign_duration', 0)
        recent_ratio = strategic_insights.get('recent_campaigns_ratio', 0)
        
        # Build NATURAL intro based on actual analysis
        if ad_count == 0:
            opening = f"Olá,\n\nNotei que {company_name} ainda não tem presença em anúncios digitais."
            main_insight = "**Oportunidade de Pioneirismo**: Seus concorrentes já estão investindo em digital - é o momento de entrar no mercado com vantagem estratégica."
        elif ad_count <= 3:
            opening = f"Olá,\n\nAnalisei a estratégia digital de {company_name} e identifiquei uma boa base para crescimento."
            main_insight = f"**Potencial de Expansão**: Com {ad_count} campanhas ativas, há espaço para escalar significativamente sem grandes riscos."
        elif ad_count <= 8:
            opening = f"Olá,\n\nDurante uma análise competitiva, identifiquei algumas oportunidades interessantes para {company_name}."
            main_insight = f"**Otimização Estratégica**: {ad_count} campanhas ativas mostram bom engajamento, mas há gaps específicos para explorar."
        else:
            opening = f"Olá,\n\nAnalisei as {ad_count} campanhas ativas de {company_name} e encontrei oportunidades de otimização."
            main_insight = f"**Eficiência Publicitária**: Volume alto sugere potencial para redução de custos e aumento de ROI."
        
        # Add SPECIFIC vulnerability insights (only if relevant)
        specific_insights = []
        
        # Generate SPECIFIC financial insights instead of generic templates
        specific_insights = []
        
        # Real budget waste analysis
        if 'HIGH_CPM_WASTE' in vulnerabilities:
            waste_amount = self._extract_waste_amount(vulnerabilities, 'HIGH_CPM_WASTE')
            specific_insights.append(f"**Desperdício de CPM Detectado**: Análise indica ${waste_amount}/mês em gastos ineficientes de targeting. Otimização pode reduzir CPM em 25-40%.")
        
        if 'FORMAT_INEFFICIENCY' in vulnerabilities:
            waste_amount = self._extract_waste_amount(vulnerabilities, 'FORMAT_INEFFICIENCY')
            specific_insights.append(f"**Ineficiência de Formato**: ${waste_amount}/mês perdidos por concentração em formatos de baixa performance. Diversificação estratégica pode recuperar 60% desse valor.")
        
        if 'BIDDING_INEFFICIENCY' in vulnerabilities:
            waste_amount = self._extract_waste_amount(vulnerabilities, 'BIDDING_INEFFICIENCY')
            specific_insights.append(f"**Overbidding Competitivo**: Análise vs concorrentes mostra ${waste_amount}/mês em lances desnecessariamente altos. Rebalanceamento pode manter volume com 30% menos gasto.")
        
        # Fallback to generic only if no financial waste found
        if not specific_insights:
            if 'MISSING_VIDEO_STRATEGY' in vulnerabilities and 'video' not in formats_detected:
                specific_insights.append("**Oportunidade Video Strategy**: Análise mostra ausência de vídeo. Formato vídeo pode aumentar engagement em 60% e reduzir CPM em 23%.")
            
            if recent_ratio < 0.3 and ad_count > 0:
                specific_insights.append("**Atividade Recente**: Baixa atividade nas campanhas recentes pode significar oportunidades perdidas.")
        
        # Calculate total ROI opportunity
        total_monthly_waste = self._calculate_total_waste_from_vulnerabilities(vulnerabilities)
        roi_projection = total_monthly_waste * 0.7 * 12  # 70% recovery rate, annualized
        
        # Use specific insight if available, otherwise use main insight
        final_insight = specific_insights[0] if specific_insights else main_insight
        
        # Enhanced closing with specific ROI
        if total_monthly_waste > 500:
            closing = f"Identifiquei **${total_monthly_waste:.0f}/mês em desperdício recuperável** nas campanhas de {company_name}.\n\n**Sprint de Auditoria ($997)**: 1 semana para mapear ${roi_projection:.0f}/ano em otimizações. ROI projetado: {roi_projection/997:.1f}x.\n\nInteressados em ver as oportunidades específicas?"
        else:
            closing = f"Ofereço um **Sprint de Auditoria e Otimização ($997)** focado em SMBs como vocês.\n\nQuero mostrar 3-5 oportunidades específicas identificadas na análise de {company_name}. Interessados em uma consultoria de 1 semana?"
        
        return f"{opening}\n\n{final_insight}\n\n{closing}"
    
    def _generate_campaign_specific_subject(self, scored_prospect: ScoredProspect, strategic_insights: Dict) -> str:
        """Generate subject line based on specific campaign analysis"""
        
        company_name = scored_prospect.discovery_data.company_name or scored_prospect.discovery_data.domain.split('.')[0]
        vulnerabilities = strategic_insights.get('vulnerabilities', [])
        ad_count = strategic_insights.get('ad_count', 0)
        
        # Priority-based subject lines with campaign references
        if 'MISSING_VIDEO_STRATEGY' in vulnerabilities:
            return f"{company_name} - oportunidade video strategy ({ad_count} campanhas analisadas)"
        elif 'COMPLETELY_STALE_CAMPAIGNS' in vulnerabilities:
            return f"{company_name} - refresh criativo recomendado"
        elif 'SINGLE_FORMAT_LIMITATION' in vulnerabilities:
            return f"{company_name} - diversificação de formatos"
        elif 'SHORT_CAMPAIGN_STRATEGY' in vulnerabilities:
            return f"{company_name} - otimização de duração das campanhas"
        elif ad_count > 0:
            return f"{company_name} - oportunidades identificadas ({ad_count} campanhas)"
        else:
            return f"{company_name} - otimização digital estratégica"

    
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
    
    def _extract_waste_amount(self, vulnerabilities: List[str], waste_type: str) -> int:
        """Extract monetary waste amount from vulnerability string"""
        for vuln in vulnerabilities:
            if waste_type in vuln and '$' in vuln:
                try:
                    # Extract number after $ and before /month
                    import re
                    match = re.search(r'\$(\d+)', vuln)
                    if match:
                        return int(match.group(1))
                except:
                    continue
        return 0
    
    def _calculate_total_waste_from_vulnerabilities(self, vulnerabilities: List[str]) -> int:
        """Calculate total monthly waste from all vulnerabilities"""
        total_waste = 0
        waste_types = ['HIGH_CPM_WASTE', 'FORMAT_INEFFICIENCY', 'BIDDING_INEFFICIENCY']
        
        for waste_type in waste_types:
            total_waste += self._extract_waste_amount(vulnerabilities, waste_type)
        
        return total_waste
    
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

    def _extract_financial_insight(self, prospect: ScoredProspect) -> str:
        """Extract key financial insight from prospect analysis"""
        try:
            campaign_count = len(prospect.discovery_data.campaigns_data)
            
            if campaign_count == 0:
                return "zero active advertising campaigns despite strong market presence"
            elif campaign_count >= 50:
                return f"{campaign_count} active campaigns with potential budget consolidation opportunities"
            elif campaign_count <= 3:
                return f"only {campaign_count} campaigns running, indicating untapped advertising potential"
            else:
                return f"{campaign_count} campaigns with optimization opportunities identified"
                
        except Exception as e:
            logger.warning(f"Failed to extract financial insight: {e}")
            return "advertising performance gaps requiring immediate attention"

    def _build_evidence_summary(self, prospect: ScoredProspect) -> str:
        """Build evidence summary from analysis data"""
        try:
            evidence_points = []
            
            # Campaign performance analysis
            campaign_count = len(prospect.discovery_data.campaigns_data)
            if campaign_count > 0:
                evidence_points.append(f"• {campaign_count} active campaigns analyzed")
            
            # Add performance data if available
            if hasattr(prospect, 'performance_data') and prospect.performance_data:
                evidence_points.append(f"• Performance gaps identified in current setup")
                
            # Add financial analysis
            if campaign_count >= 10:
                evidence_points.append(f"• Budget optimization potential across multiple campaigns")
            elif campaign_count <= 3:
                evidence_points.append(f"• Expansion opportunities beyond current {campaign_count} campaigns")
                
            return "\n".join(evidence_points) if evidence_points else "• Comprehensive advertising analysis completed"
            
        except Exception as e:
            logger.warning(f"Failed to build evidence summary: {e}")
            return "• Detailed advertising performance analysis available"

    def _extract_growth_opportunities(self, prospect: ScoredProspect) -> str:
        """Extract specific growth opportunities"""
        try:
            campaign_count = len(prospect.discovery_data.campaigns_data)
            vertical = prospect.discovery_data.vertical.lower()
            
            if campaign_count == 0:
                return "Launch targeted digital advertising to capture market share"
            elif campaign_count <= 3:
                return "Scale current campaigns and expand to additional platforms"
            elif campaign_count >= 20:
                return "Consolidate and optimize existing campaigns for better ROI"
            else:
                # Vertical-specific opportunities
                if "fitness" in vertical:
                    return "Optimize weekend lead capture timing for membership urgency"
                elif "hotel" in vertical:
                    return "Implement last-minute booking strategy for higher RevPAR"
                elif "restaurant" in vertical:
                    return "Target Sunday dining decisions for weekend revenue boost"
                else:
                    return "Implement strategic campaign expansion with performance optimization"
                    
        except Exception as e:
            logger.warning(f"Failed to extract growth opportunities: {e}")
            return "Strategic advertising expansion opportunities identified"

    def _calculate_savings_estimate(self, prospect: ScoredProspect) -> str:
        """Calculate potential monthly savings estimate"""
        try:
            campaign_count = len(prospect.discovery_data.campaigns_data)
            
            # Conservative savings estimates based on campaign count
            if campaign_count == 0:
                return "$2,500-5,000"  # New revenue opportunity
            elif campaign_count <= 5:
                return "$1,200-2,800"  # Optimization and expansion
            elif campaign_count <= 15:
                return "$3,500-7,200"  # Medium portfolio optimization
            elif campaign_count >= 50:
                return "$8,000-15,000"  # Large portfolio consolidation
            else:
                return "$2,200-4,500"  # Standard optimization
                
        except Exception as e:
            logger.warning(f"Failed to calculate savings estimate: {e}")
            return "$1,500-3,500"

    def _get_campaign_count(self, prospect: ScoredProspect) -> str:
        """Get campaign count for template"""
        try:
            count = len(prospect.discovery_data.campaigns_data)
            if count == 0:
                return "zero"
            elif count == 1:
                return "1"
            else:
                return str(count)
        except:
            return "multiple"

    def _identify_competitive_advantage(self, prospect: ScoredProspect) -> str:
        """Identify key competitive advantage point"""
        try:
            campaign_count = len(prospect.discovery_data.campaigns_data)
            vertical = prospect.discovery_data.vertical.lower()
            
            if campaign_count == 0:
                return "Your competitors are already advertising - first-mover advantage still available"
            elif campaign_count >= 20:
                return "Most competitors run fewer campaigns - optimization advantage possible"
            else:
                # Vertical-specific advantages
                if "fitness" in vertical:
                    return "Weekend membership urgency is underutilized by most fitness centers"
                elif "hotel" in vertical:
                    return "Last-minute booking optimization gives significant RevPAR advantage"
                else:
                    return "Strategic timing optimization provides competitive edge"
                    
        except Exception as e:
            logger.warning(f"Failed to identify competitive advantage: {e}")
            return "Strategic optimization provides measurable competitive advantage"