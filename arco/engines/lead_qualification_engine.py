"""
Lead Qualification Engine for ARCO.

This module provides advanced lead qualification and scoring capabilities,
going beyond basic ICP matching to provide detailed lead assessment.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import asyncio
from dataclasses import dataclass

from arco.models.prospect import Prospect, Contact, Technology
from arco.models.icp import ICP
from arco.models.financial_leak import FinancialLeakDetector
from arco.utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class QualificationCriteria:
    """Criteria for lead qualification."""
    min_employee_count: int = 10
    min_revenue: int = 500000
    max_revenue: int = 50000000
    required_technologies: List[str] = None
    excluded_technologies: List[str] = None
    min_icp_score: float = 60.0
    min_roi_percentage: float = 15.0
    min_annual_savings: float = 5000.0
    required_contact_types: List[str] = None
    geographic_restrictions: List[str] = None
    industry_focus: List[str] = None
    
    def __post_init__(self):
        if self.required_technologies is None:
            self.required_technologies = []
        if self.excluded_technologies is None:
            self.excluded_technologies = []
        if self.required_contact_types is None:
            self.required_contact_types = ["CEO", "CTO", "CMO", "Founder", "Owner"]
        if self.geographic_restrictions is None:
            self.geographic_restrictions = ["United States", "Canada", "United Kingdom", "Australia"]
        if self.industry_focus is None:
            self.industry_focus = []

@dataclass
class LeadScore:
    """Comprehensive lead scoring."""
    total_score: float
    icp_score: float
    financial_score: float
    technology_score: float
    contact_score: float
    company_score: float
    engagement_score: float
    qualification_level: str  # "A", "B", "C", "D"
    qualification_reasons: List[str]
    disqualification_reasons: List[str]
    priority_level: int  # 1-5, where 1 is highest priority

class LeadQualificationEngine:
    """Advanced lead qualification and scoring engine."""
    
    def __init__(self, criteria: QualificationCriteria = None):
        """
        Initialize the qualification engine.
        
        Args:
            criteria: Qualification criteria to use
        """
        self.criteria = criteria or QualificationCriteria()
        self.leak_detector = FinancialLeakDetector()
    
    def qualify_lead(self, prospect: Prospect, icp: ICP = None, 
                    analysis_results: Dict[str, Any] = None) -> Tuple[bool, LeadScore]:
        """
        Perform comprehensive lead qualification.
        
        Args:
            prospect: Prospect to qualify
            icp: ICP to score against
            analysis_results: Previous analysis results
            
        Returns:
            Tuple of (is_qualified, lead_score)
        """
        # Calculate individual scores
        icp_score = self._calculate_icp_score(prospect, icp)
        financial_score = self._calculate_financial_score(prospect, analysis_results)
        technology_score = self._calculate_technology_score(prospect)
        contact_score = self._calculate_contact_score(prospect)
        company_score = self._calculate_company_score(prospect)
        engagement_score = self._calculate_engagement_score(prospect)
        
        # Calculate total score (weighted average)
        total_score = (
            icp_score * 0.25 +
            financial_score * 0.25 +
            technology_score * 0.15 +
            contact_score * 0.15 +
            company_score * 0.15 +
            engagement_score * 0.05
        )
        
        # Determine qualification level and reasons
        qualification_level, qualification_reasons, disqualification_reasons = self._determine_qualification_level(
            prospect, total_score, icp_score, financial_score, technology_score, 
            contact_score, company_score, engagement_score, analysis_results
        )
        
        # Determine priority level
        priority_level = self._calculate_priority_level(total_score, financial_score, icp_score)
        
        # Create lead score
        lead_score = LeadScore(
            total_score=total_score,
            icp_score=icp_score,
            financial_score=financial_score,
            technology_score=technology_score,
            contact_score=contact_score,
            company_score=company_score,
            engagement_score=engagement_score,
            qualification_level=qualification_level,
            qualification_reasons=qualification_reasons,
            disqualification_reasons=disqualification_reasons,
            priority_level=priority_level
        )
        
        # Determine if qualified (include level C for testing)
        is_qualified = qualification_level in ["A", "B", "C"] and len(disqualification_reasons) == 0
        
        return is_qualified, lead_score
    
    def _calculate_icp_score(self, prospect: Prospect, icp: ICP = None) -> float:
        """Calculate ICP match score."""
        if not icp:
            return 50.0  # Neutral score if no ICP provided
        
        try:
            return icp.calculate_match_score(prospect)
        except Exception as e:
            logger.warning(f"Error calculating ICP score for {prospect.domain}: {e}")
            return 0.0
    
    def _calculate_financial_score(self, prospect: Prospect, analysis_results: Dict[str, Any] = None) -> float:
        """Calculate financial opportunity score."""
        if analysis_results and "leak_results" in analysis_results:
            leak_results = analysis_results["leak_results"]
            summary = leak_results.get("summary", {})
            
            roi_percentage = summary.get("roi_percentage", 0)
            annual_savings = summary.get("total_annual_savings", 0)
            
            # Score based on ROI and savings potential
            roi_score = min(roi_percentage / 50.0 * 100, 100)  # Cap at 100
            savings_score = min(annual_savings / 10000.0 * 100, 100)  # Cap at 100
            
            return (roi_score + savings_score) / 2
        
        # Fallback scoring based on company size and revenue
        size_score = 0
        if prospect.employee_count:
            if prospect.employee_count >= 100:
                size_score = 80
            elif prospect.employee_count >= 50:
                size_score = 60
            elif prospect.employee_count >= 20:
                size_score = 40
            else:
                size_score = 20
        
        revenue_score = 0
        if prospect.revenue:
            if prospect.revenue >= 5000000:
                revenue_score = 80
            elif prospect.revenue >= 1000000:
                revenue_score = 60
            elif prospect.revenue >= 500000:
                revenue_score = 40
            else:
                revenue_score = 20
        
        return (size_score + revenue_score) / 2
    
    def _calculate_technology_score(self, prospect: Prospect) -> float:
        """Calculate technology stack score."""
        if not prospect.technologies:
            return 20.0  # Low score for no tech data
        
        score = 0
        tech_names = [tech.name.lower() for tech in prospect.technologies]
        
        # Positive indicators
        positive_techs = [
            "shopify", "woocommerce", "magento",  # E-commerce platforms
            "hubspot", "salesforce", "marketo",   # CRM/Marketing
            "google analytics", "mixpanel", "amplitude",  # Analytics
            "stripe", "paypal", "square",         # Payments
            "mailchimp", "klaviyo", "sendgrid",   # Email marketing
            "zendesk", "intercom", "freshdesk"    # Support
        ]
        
        # Count positive indicators
        positive_count = sum(1 for tech in positive_techs if any(pt in tech for pt in tech_names))
        
        # Base score from technology diversity
        diversity_score = min(len(prospect.technologies) * 5, 50)
        
        # Bonus for relevant technologies
        relevance_score = min(positive_count * 10, 50)
        
        return diversity_score + relevance_score
    
    def _calculate_contact_score(self, prospect: Prospect) -> float:
        """Calculate contact quality score."""
        if not prospect.contacts:
            return 10.0  # Very low score for no contacts
        
        score = 0
        
        for contact in prospect.contacts:
            contact_score = 0
            
            # Score based on position
            if contact.position:
                position_lower = contact.position.lower()
                if any(title in position_lower for title in ["ceo", "founder", "owner", "president"]):
                    contact_score += 40
                elif any(title in position_lower for title in ["cto", "cmo", "cfo", "vp", "director"]):
                    contact_score += 30
                elif any(title in position_lower for title in ["manager", "head", "lead"]):
                    contact_score += 20
                else:
                    contact_score += 10
            
            # Score based on having email
            if contact.email and "@" in contact.email:
                contact_score += 30
            
            # Score based on having phone
            if contact.phone:
                contact_score += 20
            
            # Score based on having name
            if contact.name:
                contact_score += 10
            
            score = max(score, contact_score)  # Take the best contact
        
        return min(score, 100)
    
    def _calculate_company_score(self, prospect: Prospect) -> float:
        """Calculate company profile score."""
        score = 0
        
        # Company size score
        if prospect.employee_count:
            if self.criteria.min_employee_count <= prospect.employee_count <= 1000:
                score += 30
            elif prospect.employee_count > 1000:
                score += 20
            else:
                score += 10
        
        # Revenue score
        if prospect.revenue:
            if self.criteria.min_revenue <= prospect.revenue <= self.criteria.max_revenue:
                score += 30
            elif prospect.revenue > self.criteria.max_revenue:
                score += 15  # Too big might be harder to sell to
            else:
                score += 10
        
        # Industry score
        if prospect.industry:
            if not self.criteria.industry_focus or prospect.industry in self.criteria.industry_focus:
                score += 20
            else:
                score += 10
        
        # Geographic score
        if prospect.country:
            if prospect.country in self.criteria.geographic_restrictions:
                score += 20
            else:
                score += 5  # Lower score for non-target geographies
        
        return min(score, 100)
    
    def _calculate_engagement_score(self, prospect: Prospect) -> float:
        """Calculate engagement potential score."""
        score = 50  # Base score
        
        # Website quality indicator
        if prospect.website:
            if prospect.website.startswith("https://"):
                score += 20
            else:
                score += 10
        
        # Company description quality
        if prospect.description and len(prospect.description) > 50:
            score += 20
        elif prospect.description:
            score += 10
        
        # Social presence (inferred from having multiple contacts)
        if len(prospect.contacts) > 1:
            score += 20
        
        return min(score, 100)
    
    def _determine_qualification_level(self, prospect: Prospect, total_score: float, 
                                     icp_score: float, financial_score: float, 
                                     technology_score: float, contact_score: float,
                                     company_score: float, engagement_score: float,
                                     analysis_results: Dict[str, Any] = None) -> Tuple[str, List[str], List[str]]:
        """Determine qualification level and reasons."""
        qualification_reasons = []
        disqualification_reasons = []
        
        # Check hard disqualifiers
        if prospect.employee_count and prospect.employee_count < self.criteria.min_employee_count:
            disqualification_reasons.append(f"Company too small ({prospect.employee_count} employees)")
        
        if prospect.revenue and prospect.revenue < self.criteria.min_revenue:
            disqualification_reasons.append(f"Revenue too low (${prospect.revenue:,})")
        
        if prospect.country and prospect.country not in self.criteria.geographic_restrictions:
            disqualification_reasons.append(f"Outside target geography ({prospect.country})")
        
        # Check for excluded technologies
        if self.criteria.excluded_technologies:
            tech_names = [tech.name.lower() for tech in prospect.technologies]
            for excluded_tech in self.criteria.excluded_technologies:
                if any(excluded_tech.lower() in tech_name for tech_name in tech_names):
                    disqualification_reasons.append(f"Uses excluded technology ({excluded_tech})")
        
        # Check contact quality
        if contact_score < 30:
            disqualification_reasons.append("Poor contact information quality")
        
        # If disqualified, return D
        if disqualification_reasons:
            return "D", [], disqualification_reasons
        
        # Determine qualification level based on scores
        if total_score >= 80:
            qualification_level = "A"
            qualification_reasons.append("High overall score")
        elif total_score >= 65:
            qualification_level = "B"
            qualification_reasons.append("Good overall score")
        elif total_score >= 50:
            qualification_level = "C"
            qualification_reasons.append("Moderate overall score")
        else:
            qualification_level = "D"
            disqualification_reasons.append("Low overall score")
        
        # Add specific qualification reasons
        if icp_score >= 70:
            qualification_reasons.append("Strong ICP match")
        if financial_score >= 70:
            qualification_reasons.append("High financial opportunity")
        if technology_score >= 70:
            qualification_reasons.append("Good technology stack")
        if contact_score >= 70:
            qualification_reasons.append("Quality contact information")
        
        # Check financial criteria
        if analysis_results and "leak_results" in analysis_results:
            summary = analysis_results["leak_results"].get("summary", {})
            roi_percentage = summary.get("roi_percentage", 0)
            annual_savings = summary.get("total_annual_savings", 0)
            
            if roi_percentage >= self.criteria.min_roi_percentage:
                qualification_reasons.append(f"High ROI potential ({roi_percentage:.1f}%)")
            
            if annual_savings >= self.criteria.min_annual_savings:
                qualification_reasons.append(f"Significant savings potential (${annual_savings:,.0f})")
        
        return qualification_level, qualification_reasons, disqualification_reasons
    
    def _calculate_priority_level(self, total_score: float, financial_score: float, icp_score: float) -> int:
        """Calculate priority level (1-5, where 1 is highest)."""
        # Weighted priority calculation
        priority_score = (total_score * 0.4 + financial_score * 0.4 + icp_score * 0.2)
        
        if priority_score >= 85:
            return 1  # Highest priority
        elif priority_score >= 75:
            return 2  # High priority
        elif priority_score >= 65:
            return 3  # Medium priority
        elif priority_score >= 50:
            return 4  # Low priority
        else:
            return 5  # Lowest priority
    
    def batch_qualify_leads(self, prospects: List[Prospect], icp: ICP = None,
                           analysis_results_map: Dict[str, Dict[str, Any]] = None) -> Dict[str, Tuple[bool, LeadScore]]:
        """
        Qualify multiple leads in batch.
        
        Args:
            prospects: List of prospects to qualify
            icp: ICP to score against
            analysis_results_map: Map of domain to analysis results
            
        Returns:
            Dictionary mapping domain to (is_qualified, lead_score)
        """
        results = {}
        
        for prospect in prospects:
            analysis_results = None
            if analysis_results_map:
                analysis_results = analysis_results_map.get(prospect.domain)
            
            is_qualified, lead_score = self.qualify_lead(prospect, icp, analysis_results)
            results[prospect.domain] = (is_qualified, lead_score)
        
        return results
    
    def get_qualification_summary(self, qualification_results: Dict[str, Tuple[bool, LeadScore]]) -> Dict[str, Any]:
        """
        Generate a summary of qualification results.
        
        Args:
            qualification_results: Results from batch_qualify_leads
            
        Returns:
            Summary statistics
        """
        total_leads = len(qualification_results)
        qualified_leads = sum(1 for is_qualified, _ in qualification_results.values() if is_qualified)
        
        # Count by qualification level
        level_counts = {"A": 0, "B": 0, "C": 0, "D": 0}
        priority_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        total_score_sum = 0
        financial_score_sum = 0
        icp_score_sum = 0
        
        for is_qualified, lead_score in qualification_results.values():
            level_counts[lead_score.qualification_level] += 1
            priority_counts[lead_score.priority_level] += 1
            total_score_sum += lead_score.total_score
            financial_score_sum += lead_score.financial_score
            icp_score_sum += lead_score.icp_score
        
        return {
            "total_leads": total_leads,
            "qualified_leads": qualified_leads,
            "qualification_rate": qualified_leads / total_leads if total_leads > 0 else 0,
            "level_distribution": level_counts,
            "priority_distribution": priority_counts,
            "average_scores": {
                "total": total_score_sum / total_leads if total_leads > 0 else 0,
                "financial": financial_score_sum / total_leads if total_leads > 0 else 0,
                "icp": icp_score_sum / total_leads if total_leads > 0 else 0
            }
        }