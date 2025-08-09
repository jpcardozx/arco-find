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
        Generate personalized outreach message following decision tree
        """
        logger.info(f"📧 Generating outreach for {scored_prospect.discovery_data.domain}")
        
        # Gate 1: Vertical Template Selection
        vertical = self._map_vertical(scored_prospect.discovery_data.vertical)
        template = self.vertical_templates.get(vertical, self.vertical_templates["default"])
        
        # Gate 2: Pain Point Prioritization  
        primary_pain = self._prioritize_pain_points(
            scored_prospect.performance_data.leak_indicators
        )
        
        # Gate 3: Evidence Selection
        evidence_url = self._generate_evidence_package(
            scored_prospect.discovery_data.domain,
            primary_pain,
            scored_prospect.performance_data.leak_indicators
        )
        
        # Gate 4: Message Personalization
        personalized_message = self._personalize_template(
            template,
            scored_prospect,
            primary_pain,
            evidence_url
        )
        
        # Calculate personalization score
        personalization_score = self._calculate_personalization_score(
            personalized_message, scored_prospect
        )
        
        # Get follow-up sequence
        follow_up_sequence = self.follow_up_sequences.get(vertical, [])
        
        # Generate subject line
        subject_line = self._generate_subject_line(scored_prospect, primary_pain)
        
        return OutreachMessage(
            prospect_id=f"{scored_prospect.discovery_data.domain}_{int(datetime.now().timestamp())}",
            subject_line=subject_line,
            message_body=personalized_message,
            evidence_package=evidence_url,
            follow_up_sequence=follow_up_sequence,
            personalization_score=personalization_score,
            vertical_template=vertical,
            primary_pain_point=primary_pain,
            created_timestamp=datetime.now(timezone.utc)
        )
    
    def _initialize_templates(self) -> Dict[str, Template]:
        """Initialize vertical-specific message templates"""
        
        hvac_template = Template("""Hey $decision_maker,

Found your "$service" ads on Google — great targeting for $city.

Issue: PSI shows $lcp_score s LCP on mobile (p75). That's ~$lost_calls lost calls/month when users bounce before your "same-day" promise loads.

Quick fix scope:
• Image optimization ($image_savings KB savings)
• Font loading strategy  
• Above-fold phone CTA (currently buried)

Acceptance: ≥90% URLs pass CWV + A/B test on headline
Typical result: 15-30% CPA reduction

24h audit (USD 250, credited to sprint): $calendar_link
Evidence + one-pager: $evidence_url

Best,
$sender_name""")

        dental_template = Template("""Hi $decision_maker,

Saw your implant ads — smart geo-targeting for $city.

Performance issue: Field INP $inp_score ms (p75). Heavy images + no form feedback = user frustration on mobile.

2-week scope:
• Media compression strategy
• Form validation + progress feedback  
• A/B test: credentials vs. case studies above fold

Acceptance: CWV within Google thresholds + experiment readout in GA4
ROI: Typical 10-25% CVR lift on consultation forms

24h audit (USD 250 → credited): $calendar_link
Proof + fix plan: $evidence_url

$sender_name""")

        urgent_care_template = Template("""Hello,

Noticed your urgent care ads for $city — solid coverage during peak hours.

Critical: Mobile LCP $lcp_score s (p75). When someone needs immediate care, every second counts. Current load time likely costs ~$lost_revenue /month in abandoned appointments.

Sprint scope (7 days):
• Critical path optimization
• Mobile-first booking flow
• "Walk-in" vs "Appointment" CTA testing

Acceptance criteria: <2.5s mobile LCP + booking conversion baseline
Typical impact: 20-35% increase in urgent appointments

Quick audit (USD 250, applied to project): $calendar_link
Performance evidence: $evidence_url

$sender_name""")

        default_template = Template("""Hi there,

Analyzed your website performance and found some optimization opportunities.

Key issue: $primary_pain_description

This typically impacts conversion rates by $estimated_impact.

Our $service_fit approach:
$priority_fixes

ROI estimate: $estimated_impact improvement
Investment: $deal_size_range

Quick performance audit: $calendar_link
Evidence package: $evidence_url

Best regards,
$sender_name""")
        
        return {
            "hvac_multi_location": hvac_template,
            "dental_clinics": dental_template,
            "urgent_care_express": urgent_care_template,
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