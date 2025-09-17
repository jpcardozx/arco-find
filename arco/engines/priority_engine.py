"""
Priority Engine for rapid lead scoring and identification of top prospects.

This engine performs fast scoring of prospect batches to identify the top 10%
most promising leads for immediate outreach, based on company size, revenue
potential, technology maturity, and growth indicators.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime
import yaml

from ..models.prospect import Prospect
from ..utils.config_loader import ConfigLoader

logger = logging.getLogger(__name__)


@dataclass
class PriorityScore:
    """Priority scoring result for a prospect."""
    total_score: float
    company_size_score: float = 0.0
    revenue_potential_score: float = 0.0
    technology_maturity_score: float = 0.0
    growth_indicators_score: float = 0.0
    contact_accessibility_score: float = 0.0
    confidence_level: float = 0.0
    priority_tier: str = "LOW"  # "HIGH", "MEDIUM", "LOW"
    scoring_details: Dict[str, Any] = field(default_factory=dict)
    calculated_at: datetime = field(default_factory=datetime.now)


class PriorityEngine:
    """Rapid lead scoring and prioritization engine."""

    def __init__(self, config_path: str = "config/production.yml"):
        """Initialize the priority engine with configuration."""
        self.config_loader = ConfigLoader()
        self.config = self.config_loader.load_config(config_path)
        self.scoring_weights = self._load_scoring_weights()
        self.industry_criteria = self._load_industry_criteria()
        
        logger.info("PriorityEngine initialized with scoring weights")

    def _load_scoring_weights(self) -> Dict[str, float]:
        """Load scoring weights from configuration."""
        default_weights = {
            "company_size": 0.25,
            "revenue_potential": 0.30,
            "technology_maturity": 0.20,
            "growth_indicators": 0.15,
            "contact_accessibility": 0.10
        }
        
        return self.config.get("priority_scoring", {}).get("weights", default_weights)

    def _load_industry_criteria(self) -> Dict[str, Dict]:
        """Load industry-specific criteria."""
        return self.config.get("qualification_criteria", {})

    async def score_batch(self, prospects: List[Prospect]) -> List[Tuple[Prospect, PriorityScore]]:
        """Score a batch of prospects and return sorted by priority."""
        logger.info(f"Starting priority scoring for {len(prospects)} prospects")
        
        scored_prospects = []
        
        # Process prospects concurrently for speed
        tasks = [self._calculate_priority_score(prospect) for prospect in prospects]
        scores = await asyncio.gather(*tasks, return_exceptions=True)
        
        for prospect, score in zip(prospects, scores):
            if isinstance(score, Exception):
                logger.warning(f"Scoring failed for {prospect.domain}: {score}")
                # Create minimal score for failed prospects
                score = PriorityScore(
                    total_score=0.0,
                    confidence_level=0.0,
                    priority_tier="LOW"
                )
            
            scored_prospects.append((prospect, score))
        
        # Sort by total score descending
        scored_prospects.sort(key=lambda x: x[1].total_score, reverse=True)
        
        logger.info(f"Priority scoring completed. Top score: {scored_prospects[0][1].total_score:.2f}")
        return scored_prospects

    def get_top_percentage(self, 
                          scored_prospects: List[Tuple[Prospect, PriorityScore]],
                          percentage: float = 0.1) -> List[Tuple[Prospect, PriorityScore]]:
        """Get top percentage of prospects (default 10%)."""
        count = max(1, int(len(scored_prospects) * percentage))
        top_prospects = scored_prospects[:count]
        
        logger.info(f"Selected top {count} prospects ({percentage*100:.1f}%) for priority outreach")
        return top_prospects

    async def _calculate_priority_score(self, prospect: Prospect) -> PriorityScore:
        """Calculate comprehensive priority score for a prospect."""
        try:
            # Calculate individual scoring components
            company_size_score = self._score_company_size(prospect)
            revenue_potential_score = self._score_revenue_potential(prospect)
            technology_maturity_score = self._score_technology_maturity(prospect)
            growth_indicators_score = self._score_growth_indicators(prospect)
            contact_accessibility_score = self._score_contact_accessibility(prospect)
            
            # Apply industry-specific multipliers for realistic scoring
            industry_multiplier = self._get_industry_multiplier(prospect)
            
            # Calculate weighted total score with industry adjustment
            base_score = (
                company_size_score * self.scoring_weights["company_size"] +
                revenue_potential_score * self.scoring_weights["revenue_potential"] +
                technology_maturity_score * self.scoring_weights["technology_maturity"] +
                growth_indicators_score * self.scoring_weights["growth_indicators"] +
                contact_accessibility_score * self.scoring_weights["contact_accessibility"]
            )
            
            # Apply industry multiplier and market timing factors
            total_score = base_score * industry_multiplier
            total_score = self._apply_market_timing_factors(total_score, prospect)
            
            # Ensure score stays within bounds
            total_score = min(max(total_score, 0.0), 100.0)
            
            # Calculate confidence level based on data availability
            confidence_level = self._calculate_confidence_level(prospect)
            
            # Determine priority tier with realistic thresholds
            priority_tier = self._determine_priority_tier(total_score, confidence_level)
            
            return PriorityScore(
                total_score=total_score,
                company_size_score=company_size_score,
                revenue_potential_score=revenue_potential_score,
                technology_maturity_score=technology_maturity_score,
                growth_indicators_score=growth_indicators_score,
                contact_accessibility_score=contact_accessibility_score,
                confidence_level=confidence_level,
                priority_tier=priority_tier,
                scoring_details={
                    "company_name": prospect.company_name,
                    "domain": prospect.domain,
                    "industry": getattr(prospect, 'industry', 'unknown'),
                    "employee_count": getattr(prospect, 'employee_count', 0),
                    "revenue": getattr(prospect, 'revenue', 0),
                    "industry_multiplier": industry_multiplier,
                    "base_score": base_score
                }
            )
            
        except Exception as e:
            logger.error(f"Error calculating priority score for {prospect.domain}: {e}")
            raise

    def _score_company_size(self, prospect: Prospect) -> float:
        """Score based on company size (employees and revenue)."""
        score = 0.0
        
        # Employee count scoring (0-50 points)
        employee_count = getattr(prospect, 'employee_count', 0)
        if employee_count > 0:
            if employee_count >= 500:
                score += 50.0
            elif employee_count >= 100:
                score += 40.0
            elif employee_count >= 50:
                score += 30.0
            elif employee_count >= 20:
                score += 20.0
            elif employee_count >= 10:
                score += 15.0
            else:
                score += 10.0
        
        # Revenue scoring (0-50 points)
        revenue = getattr(prospect, 'revenue', 0)
        if revenue > 0:
            if revenue >= 50000000:  # $50M+
                score += 50.0
            elif revenue >= 10000000:  # $10M+
                score += 40.0
            elif revenue >= 5000000:   # $5M+
                score += 30.0
            elif revenue >= 1000000:   # $1M+
                score += 25.0
            elif revenue >= 500000:    # $500K+
                score += 20.0
            else:
                score += 10.0
        
        return min(score, 100.0)

    def _score_revenue_potential(self, prospect: Prospect) -> float:
        """Score based on potential revenue opportunity."""
        score = 0.0
        
        # Industry-based potential
        industry = getattr(prospect, 'industry', '').lower()
        high_value_industries = ['saas', 'software', 'technology', 'ecommerce', 'fintech']
        medium_value_industries = ['healthcare', 'manufacturing', 'retail', 'education']
        
        if any(ind in industry for ind in high_value_industries):
            score += 40.0
        elif any(ind in industry for ind in medium_value_industries):
            score += 25.0
        else:
            score += 15.0
        
        # Growth stage indicators
        funding_stage = getattr(prospect, 'funding_stage', '').lower()
        if 'series' in funding_stage or 'growth' in funding_stage:
            score += 30.0
        elif 'seed' in funding_stage or 'angel' in funding_stage:
            score += 20.0
        
        # Technology budget indicators
        tech_stack_size = len(getattr(prospect, 'technologies', []))
        if tech_stack_size >= 20:
            score += 30.0
        elif tech_stack_size >= 10:
            score += 20.0
        elif tech_stack_size >= 5:
            score += 10.0
        
        return min(score, 100.0)

    def _score_technology_maturity(self, prospect: Prospect) -> float:
        """Score based on technology stack maturity and sophistication."""
        score = 0.0
        
        technologies = getattr(prospect, 'technologies', [])
        if not technologies:
            return 20.0  # Default score for unknown tech stack
        
        # Enterprise technology indicators
        enterprise_tech = [
            'aws', 'azure', 'google cloud', 'kubernetes', 'docker',
            'salesforce', 'hubspot', 'marketo', 'tableau', 'snowflake'
        ]
        
        # Modern development stack
        modern_stack = [
            'react', 'vue', 'angular', 'node.js', 'python', 'go',
            'microservices', 'api', 'graphql', 'mongodb', 'postgresql'
        ]
        
        # Marketing technology stack
        martech_stack = [
            'google analytics', 'google ads', 'facebook ads', 'linkedin ads',
            'mailchimp', 'sendgrid', 'intercom', 'zendesk', 'stripe'
        ]
        
        tech_lower = [tech.lower() for tech in technologies]
        
        # Score enterprise technologies
        enterprise_matches = sum(1 for tech in enterprise_tech if any(t in tech_lower for t in [tech]))
        score += min(enterprise_matches * 15, 45)
        
        # Score modern development stack
        modern_matches = sum(1 for tech in modern_stack if any(t in tech_lower for t in [tech]))
        score += min(modern_matches * 10, 30)
        
        # Score marketing technology
        martech_matches = sum(1 for tech in martech_stack if any(t in tech_lower for t in [tech]))
        score += min(martech_matches * 8, 25)
        
        return min(score, 100.0)

    def _score_growth_indicators(self, prospect: Prospect) -> float:
        """Score based on growth and expansion indicators."""
        score = 0.0
        
        # Recent funding
        last_funding_date = getattr(prospect, 'last_funding_date', None)
        if last_funding_date:
            # Score higher for recent funding (within 2 years)
            days_since_funding = (datetime.now() - last_funding_date).days
            if days_since_funding <= 365:
                score += 40.0
            elif days_since_funding <= 730:
                score += 25.0
            else:
                score += 10.0
        
        # Job postings (hiring activity)
        job_postings = getattr(prospect, 'job_postings_count', 0)
        if job_postings >= 20:
            score += 30.0
        elif job_postings >= 10:
            score += 20.0
        elif job_postings >= 5:
            score += 15.0
        elif job_postings > 0:
            score += 10.0
        
        # Website traffic growth (if available)
        traffic_growth = getattr(prospect, 'traffic_growth_rate', 0)
        if traffic_growth > 0.5:  # 50%+ growth
            score += 30.0
        elif traffic_growth > 0.2:  # 20%+ growth
            score += 20.0
        elif traffic_growth > 0:
            score += 10.0
        
        return min(score, 100.0)

    def _score_contact_accessibility(self, prospect: Prospect) -> float:
        """Score based on how accessible decision makers are."""
        score = 0.0
        
        # Email availability
        if hasattr(prospect, 'decision_maker_emails') and prospect.decision_maker_emails:
            score += 40.0
        elif hasattr(prospect, 'contact_email') and prospect.contact_email:
            score += 25.0
        
        # LinkedIn profiles available
        if hasattr(prospect, 'linkedin_profiles') and prospect.linkedin_profiles:
            score += 30.0
        
        # Phone numbers available
        if hasattr(prospect, 'phone_numbers') and prospect.phone_numbers:
            score += 20.0
        
        # Company size factor (smaller companies = more accessible)
        employee_count = getattr(prospect, 'employee_count', 0)
        if employee_count <= 50:
            score += 10.0
        elif employee_count <= 200:
            score += 5.0
        
        return min(score, 100.0)

    def _calculate_confidence_level(self, prospect: Prospect) -> float:
        """Calculate confidence level based on data completeness."""
        data_points = 0
        total_points = 10
        
        # Check for key data availability
        if getattr(prospect, 'employee_count', 0) > 0:
            data_points += 1
        if getattr(prospect, 'revenue', 0) > 0:
            data_points += 1
        if getattr(prospect, 'industry', ''):
            data_points += 1
        if getattr(prospect, 'technologies', []):
            data_points += 1
        if getattr(prospect, 'funding_stage', ''):
            data_points += 1
        if getattr(prospect, 'last_funding_date', None):
            data_points += 1
        if getattr(prospect, 'job_postings_count', 0) > 0:
            data_points += 1
        if hasattr(prospect, 'contact_email') and prospect.contact_email:
            data_points += 1
        if hasattr(prospect, 'linkedin_profiles') and prospect.linkedin_profiles:
            data_points += 1
        if getattr(prospect, 'website', ''):
            data_points += 1
        
        return (data_points / total_points) * 100.0

    def _determine_priority_tier(self, total_score: float, confidence_level: float) -> str:
        """Determine priority tier based on score and confidence."""
        # Adjust score based on confidence
        adjusted_score = total_score * (confidence_level / 100.0)
        
        if adjusted_score >= 70.0:
            return "HIGH"
        elif adjusted_score >= 45.0:
            return "MEDIUM"
        else:
            return "LOW"

    def _get_industry_multiplier(self, prospect: Prospect) -> float:
        """Get industry-specific multiplier for realistic scoring."""
        industry = getattr(prospect, 'industry', '').lower()
        
        # High-value industries with strong ROI potential
        if any(ind in industry for ind in ['saas', 'software', 'fintech', 'ai', 'machine learning']):
            return 1.2
        
        # Medium-value industries with good potential
        elif any(ind in industry for ind in ['ecommerce', 'technology', 'healthcare', 'education']):
            return 1.1
        
        # Standard industries
        elif any(ind in industry for ind in ['manufacturing', 'retail', 'consulting', 'services']):
            return 1.0
        
        # Lower priority industries
        elif any(ind in industry for ind in ['non-profit', 'government', 'agriculture']):
            return 0.8
        
        # Unknown industry - neutral multiplier
        else:
            return 0.95

    def _apply_market_timing_factors(self, score: float, prospect: Prospect) -> float:
        """Apply market timing and urgency factors to the score."""
        timing_multiplier = 1.0
        
        # Recent funding indicates budget availability and growth phase
        last_funding_date = getattr(prospect, 'last_funding_date', None)
        if last_funding_date:
            days_since_funding = (datetime.now() - last_funding_date).days
            if days_since_funding <= 180:  # 6 months
                timing_multiplier += 0.15  # Hot timing
            elif days_since_funding <= 365:  # 1 year
                timing_multiplier += 0.10  # Good timing
        
        # High hiring activity indicates growth and budget
        job_postings = getattr(prospect, 'job_postings_count', 0)
        if job_postings >= 15:
            timing_multiplier += 0.10
        elif job_postings >= 5:
            timing_multiplier += 0.05
        
        # Technology debt indicators (older tech stack = more urgent need)
        technologies = getattr(prospect, 'technologies', [])
        legacy_tech = ['jquery', 'php', 'mysql', 'apache', 'wordpress', 'drupal']
        tech_lower = [tech.lower() for tech in technologies]
        
        legacy_matches = sum(1 for tech in legacy_tech if any(t in tech_lower for t in [tech]))
        if legacy_matches >= 3:
            timing_multiplier += 0.08  # Higher urgency for tech modernization
        
        # Seasonal factors (Q4 budget cycles, etc.)
        current_month = datetime.now().month
        if current_month in [10, 11, 12]:  # Q4 budget season
            timing_multiplier += 0.05
        elif current_month in [1, 2]:  # New year planning
            timing_multiplier += 0.03
        
        return score * timing_multiplier

    def _determine_priority_tier(self, total_score: float, confidence_level: float) -> str:
        """Determine priority tier based on score and confidence with realistic thresholds."""
        # Adjust score based on confidence - low confidence reduces effective score
        confidence_factor = max(0.5, confidence_level / 100.0)  # Minimum 50% factor
        adjusted_score = total_score * confidence_factor
        
        # Realistic thresholds based on market data
        if adjusted_score >= 65.0 and confidence_level >= 70.0:
            return "HIGH"
        elif adjusted_score >= 40.0 and confidence_level >= 50.0:
            return "MEDIUM"
        else:
            return "LOW"

    def get_decision_maker_insights(self, prospect: Prospect, score: PriorityScore) -> Dict[str, Any]:
        """Generate decision maker targeting insights for a high-priority prospect."""
        insights = {
            "primary_targets": [],
            "messaging_angles": [],
            "urgency_factors": [],
            "budget_indicators": []
        }
        
        industry = getattr(prospect, 'industry', '').lower()
        employee_count = getattr(prospect, 'employee_count', 0)
        technologies = getattr(prospect, 'technologies', [])
        
        # Determine primary decision maker targets based on company size and industry
        if employee_count <= 50:
            insights["primary_targets"] = ["CEO", "Founder", "CTO"]
        elif employee_count <= 200:
            insights["primary_targets"] = ["CTO", "VP Engineering", "Head of Marketing"]
        else:
            insights["primary_targets"] = ["VP Engineering", "Director of Technology", "CMO"]
        
        # Industry-specific messaging angles
        if any(ind in industry for ind in ['saas', 'software', 'technology']):
            insights["messaging_angles"] = [
                "Technical debt reduction",
                "Scalability improvements",
                "Developer productivity",
                "Infrastructure optimization"
            ]
        elif any(ind in industry for ind in ['ecommerce', 'retail']):
            insights["messaging_angles"] = [
                "Conversion rate optimization",
                "Customer experience improvement",
                "Marketing efficiency",
                "Revenue growth acceleration"
            ]
        
        # Urgency factors based on scoring components
        if score.growth_indicators_score > 60:
            insights["urgency_factors"].append("High growth phase - scaling challenges")
        if score.technology_maturity_score < 40:
            insights["urgency_factors"].append("Legacy technology stack - modernization needed")
        
        # Budget indicators
        funding_stage = getattr(prospect, 'funding_stage', '').lower()
        if 'series' in funding_stage:
            insights["budget_indicators"].append("Recent funding - budget available")
        if getattr(prospect, 'job_postings_count', 0) > 10:
            insights["budget_indicators"].append("Active hiring - growth budget allocated")
        
        return insights

    def get_priority_insights(self, scored_prospects: List[Tuple[Prospect, PriorityScore]]) -> Dict[str, Any]:
        """Generate insights about the prioritized prospects."""
        if not scored_prospects:
            return {}
        
        scores = [score.total_score for _, score in scored_prospects]
        high_priority = [p for p, s in scored_prospects if s.priority_tier == "HIGH"]
        medium_priority = [p for p, s in scored_prospects if s.priority_tier == "MEDIUM"]
        
        # Industry distribution analysis
        industries = {}
        for prospect, score in scored_prospects:
            industry = getattr(prospect, 'industry', 'unknown')
            if industry not in industries:
                industries[industry] = {"count": 0, "avg_score": 0, "scores": []}
            industries[industry]["count"] += 1
            industries[industry]["scores"].append(score.total_score)
        
        # Calculate average scores by industry
        for industry in industries:
            industries[industry]["avg_score"] = sum(industries[industry]["scores"]) / len(industries[industry]["scores"])
        
        return {
            "total_prospects": len(scored_prospects),
            "average_score": sum(scores) / len(scores),
            "highest_score": max(scores),
            "lowest_score": min(scores),
            "high_priority_count": len(high_priority),
            "medium_priority_count": len(medium_priority),
            "high_priority_percentage": (len(high_priority) / len(scored_prospects)) * 100,
            "top_10_percent_threshold": scored_prospects[int(len(scored_prospects) * 0.1)][1].total_score if len(scored_prospects) > 10 else scores[0],
            "industry_distribution": industries,
            "scoring_distribution": {
                "80_100": len([s for s in scores if s >= 80]),
                "60_79": len([s for s in scores if 60 <= s < 80]),
                "40_59": len([s for s in scores if 40 <= s < 60]),
                "20_39": len([s for s in scores if 20 <= s < 40]),
                "0_19": len([s for s in scores if s < 20])
            }
        }