"""
ICP (Ideal Customer Profile) Model for ARCO.

This module contains the ICP model implementation for the ARCO system,
which represents different ideal customer profiles for targeting.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Tuple
from enum import Enum
import math
from datetime import datetime


class ICPType(Enum):
    """Enum for ICP types."""
    BEAUTY_SKINCARE = "beauty_skincare"
    HEALTH_SUPPLEMENTS = "health_supplements"
    FITNESS_EQUIPMENT = "fitness_equipment"
    CUSTOM = "custom"


@dataclass
class TechnologyRequirement:
    """Technology requirement for an ICP."""
    
    category: str
    tools: List[str]
    required: bool = False
    weight: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "category": self.category,
            "tools": self.tools,
            "required": self.required,
            "weight": self.weight
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TechnologyRequirement':
        """Create from dictionary."""
        return cls(
            category=data.get("category", ""),
            tools=data.get("tools", []),
            required=data.get("required", False),
            weight=data.get("weight", 1.0)
        )


@dataclass
class RevenueIndicator:
    """Revenue indicator for an ICP."""
    
    name: str
    keywords: List[str]
    multiplier: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "keywords": self.keywords,
            "multiplier": self.multiplier
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RevenueIndicator':
        """Create from dictionary."""
        return cls(
            name=data.get("name", ""),
            keywords=data.get("keywords", []),
            multiplier=data.get("multiplier", 1.0)
        )


@dataclass
class SaaSWastePattern:
    """Pattern for detecting SaaS waste specific to an ICP."""
    
    name: str
    description: str
    detection_pattern: Dict[str, Any]
    estimated_monthly_waste: float
    priority: int = 1  # 1-5, with 5 being highest priority
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "detection_pattern": self.detection_pattern,
            "estimated_monthly_waste": self.estimated_monthly_waste,
            "priority": self.priority
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SaaSWastePattern':
        """Create from dictionary."""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            detection_pattern=data.get("detection_pattern", {}),
            estimated_monthly_waste=data.get("estimated_monthly_waste", 0.0),
            priority=data.get("priority", 1)
        )
        
    def matches(self, prospect_tech: List[Any]) -> bool:
        """
        Check if this waste pattern matches the prospect's technology stack.
        
        Args:
            prospect_tech: List of Technology objects from the prospect
            
        Returns:
            bool: True if the pattern matches, False otherwise
        """
        tech_by_category = {}
        for tech in prospect_tech:
            if tech.category not in tech_by_category:
                tech_by_category[tech.category] = []
            tech_by_category[tech.category].append(tech.name)
        
        # Check for redundant tools in the same category
        if "redundant_categories" in self.detection_pattern:
            for category in self.detection_pattern["redundant_categories"]:
                if category in tech_by_category and len(tech_by_category[category]) > 1:
                    return True
        
        # Check for specific tool combinations
        if "tool_combinations" in self.detection_pattern:
            for combo in self.detection_pattern["tool_combinations"]:
                all_found = True
                for tool_info in combo:
                    category = tool_info["category"]
                    tool = tool_info["tool"]
                    if category not in tech_by_category or tool not in tech_by_category[category]:
                        all_found = False
                        break
                if all_found:
                    return True
        
        return False


@dataclass
class ICP:
    """Ideal Customer Profile model for ARCO."""
    
    name: str
    icp_type: ICPType
    description: str
    
    # Business criteria
    min_revenue: float
    max_revenue: float
    min_employees: Optional[int] = None
    max_employees: Optional[int] = None
    
    # Industry and categories
    industries: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    
    # Geographic targeting
    target_countries: List[str] = field(default_factory=list)
    
    # Technology stack
    tech_requirements: List[TechnologyRequirement] = field(default_factory=list)
    
    # Revenue indicators
    revenue_indicators: List[RevenueIndicator] = field(default_factory=list)
    
    # SaaS waste patterns specific to this ICP
    saas_waste_patterns: List[SaaSWastePattern] = field(default_factory=list)
    
    # Search criteria
    search_dorks: List[str] = field(default_factory=list)
    
    # Scoring thresholds
    qualification_threshold: int = 75
    
    # ROI calculation parameters
    avg_monthly_saas_spend: float = 0.0
    avg_waste_percentage: float = 0.0
    avg_recovery_percentage: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "icp_type": self.icp_type.value,
            "description": self.description,
            "min_revenue": self.min_revenue,
            "max_revenue": self.max_revenue,
            "min_employees": self.min_employees,
            "max_employees": self.max_employees,
            "industries": self.industries,
            "categories": self.categories,
            "target_countries": self.target_countries,
            "tech_requirements": [tech.to_dict() for tech in self.tech_requirements],
            "revenue_indicators": [indicator.to_dict() for indicator in self.revenue_indicators],
            "saas_waste_patterns": [pattern.to_dict() for pattern in self.saas_waste_patterns],
            "search_dorks": self.search_dorks,
            "qualification_threshold": self.qualification_threshold,
            "avg_monthly_saas_spend": self.avg_monthly_saas_spend,
            "avg_waste_percentage": self.avg_waste_percentage,
            "avg_recovery_percentage": self.avg_recovery_percentage
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ICP':
        """Create from dictionary."""
        icp = cls(
            name=data.get("name", ""),
            icp_type=ICPType(data.get("icp_type", ICPType.CUSTOM.value)),
            description=data.get("description", ""),
            min_revenue=data.get("min_revenue", 0.0),
            max_revenue=data.get("max_revenue", 0.0),
            min_employees=data.get("min_employees"),
            max_employees=data.get("max_employees"),
            industries=data.get("industries", []),
            categories=data.get("categories", []),
            target_countries=data.get("target_countries", []),
            qualification_threshold=data.get("qualification_threshold", 75),
            avg_monthly_saas_spend=data.get("avg_monthly_saas_spend", 0.0),
            avg_waste_percentage=data.get("avg_waste_percentage", 0.0),
            avg_recovery_percentage=data.get("avg_recovery_percentage", 0.0)
        )
        
        # Add tech requirements
        for tech_data in data.get("tech_requirements", []):
            icp.tech_requirements.append(TechnologyRequirement.from_dict(tech_data))
        
        # Add revenue indicators
        for indicator_data in data.get("revenue_indicators", []):
            icp.revenue_indicators.append(RevenueIndicator.from_dict(indicator_data))
        
        # Add SaaS waste patterns
        for pattern_data in data.get("saas_waste_patterns", []):
            icp.saas_waste_patterns.append(SaaSWastePattern.from_dict(pattern_data))
        
        # Add search dorks
        icp.search_dorks = data.get("search_dorks", [])
        
        return icp
    
    def matches_prospect(self, prospect: Any) -> bool:
        """
        Check if a prospect matches this ICP.
        
        Args:
            prospect: A Prospect object to check against this ICP
            
        Returns:
            bool: True if the prospect matches this ICP, False otherwise
        """
        # Check revenue range
        if prospect.revenue:
            if not (self.min_revenue <= prospect.revenue <= self.max_revenue):
                return False
        
        # Check employee count if available
        if prospect.employee_count and self.min_employees and self.max_employees:
            if not (self.min_employees <= prospect.employee_count <= self.max_employees):
                return False
        
        # Check industry if available
        if prospect.industry and self.industries:
            if prospect.industry not in self.industries:
                return False
        
        # Check country if available
        if prospect.country and self.target_countries:
            if prospect.country not in self.target_countries:
                return False
        
        # Check required technologies
        if self.tech_requirements:
            prospect_tech_categories = {tech.category for tech in prospect.technologies}
            
            for tech_req in self.tech_requirements:
                if tech_req.required:
                    # Check if the prospect has any of the required tools in this category
                    if tech_req.category not in prospect_tech_categories:
                        return False
                    
                    # Check if the prospect has any of the required tools
                    prospect_tools = {
                        tech.name for tech in prospect.technologies 
                        if tech.category == tech_req.category
                    }
                    
                    if not any(tool in prospect_tools for tool in tech_req.tools):
                        return False
        
        return True
    
    def calculate_match_score(self, prospect: Any) -> float:
        """
        Calculate a match score between 0 and 100 for how well a prospect matches this ICP.
        
        Args:
            prospect: A Prospect object to score against this ICP
            
        Returns:
            float: A score between 0 and 100
        """
        score = 0.0
        total_points = 0
        
        # Revenue match (25 points)
        if prospect.revenue:
            total_points += 25
            if self.min_revenue <= prospect.revenue <= self.max_revenue:
                score += 25
            else:
                # Partial score based on how close to the range
                if prospect.revenue < self.min_revenue:
                    ratio = prospect.revenue / self.min_revenue
                    score += 25 * min(ratio, 0.8)  # Max 80% of points if below range
                else:  # prospect.revenue > self.max_revenue
                    ratio = self.max_revenue / prospect.revenue
                    score += 25 * min(ratio, 0.9)  # Max 90% of points if above range
        
        # Employee count match (15 points)
        if prospect.employee_count and self.min_employees and self.max_employees:
            total_points += 15
            if self.min_employees <= prospect.employee_count <= self.max_employees:
                score += 15
            else:
                # Partial score based on how close to the range
                if prospect.employee_count < self.min_employees:
                    ratio = prospect.employee_count / self.min_employees
                    score += 15 * min(ratio, 0.8)
                else:  # prospect.employee_count > self.max_employees
                    ratio = self.max_employees / prospect.employee_count
                    score += 15 * min(ratio, 0.9)
        
        # Industry match (20 points)
        if prospect.industry and self.industries:
            total_points += 20
            if prospect.industry in self.industries:
                score += 20
        
        # Country match (15 points)
        if prospect.country and self.target_countries:
            total_points += 15
            if prospect.country in self.target_countries:
                score += 15
        
        # Technology match (25 points)
        if self.tech_requirements and prospect.technologies:
            total_points += 25
            tech_score = 0
            
            prospect_tech_map = {
                tech.category: {t.name for t in prospect.technologies if t.category == tech.category}
                for tech in prospect.technologies
            }
            
            for tech_req in self.tech_requirements:
                weight = tech_req.weight * (2 if tech_req.required else 1)
                if tech_req.category in prospect_tech_map:
                    # Check how many of the tools in this category match
                    matching_tools = sum(1 for tool in tech_req.tools if tool in prospect_tech_map[tech_req.category])
                    if matching_tools > 0:
                        tech_score += weight * (matching_tools / len(tech_req.tools))
            
            # Normalize tech score to 25 points
            total_weight = sum((req.weight * 2) if req.required else req.weight for req in self.tech_requirements)
            if total_weight > 0:
                tech_score = (tech_score / total_weight) * 25
                score += tech_score
        
        # If we have no points to award, return 0
        if total_points == 0:
            return 0
        
        # Normalize score to 100 points
        normalized_score = (score / total_points) * 100
        
        return normalized_score
        
    def calculate_technical_footprint_score(self, prospect: Any) -> Dict[str, Any]:
        """
        Calculate a detailed technical footprint score for a prospect based on this ICP.
        
        Args:
            prospect: A Prospect object to score against this ICP
            
        Returns:
            Dict: A dictionary with detailed scoring information
        """
        if not prospect.technologies:
            return {
                "total_score": 0,
                "max_score": 100,
                "percentage": 0,
                "details": [],
                "missing_critical": [],
                "recommendations": ["No technology stack detected. Recommend manual verification."]
            }
            
        # Map prospect technologies by category for easier lookup
        prospect_tech_map = {
            tech.category: {t.name for t in prospect.technologies if t.category == tech.category}
            for tech in prospect.technologies
        }
        
        # Calculate scores for each technology requirement
        details = []
        total_score = 0
        max_score = 0
        missing_critical = []
        
        for tech_req in self.tech_requirements:
            req_score = 0
            req_max = tech_req.weight * 10  # Scale weight to points out of 10 per requirement
            max_score += req_max
            
            if tech_req.category in prospect_tech_map:
                # Check how many of the tools in this category match
                matching_tools = [tool for tool in tech_req.tools if tool in prospect_tech_map[tech_req.category]]
                match_ratio = len(matching_tools) / len(tech_req.tools) if tech_req.tools else 0
                req_score = req_max * match_ratio
                
                details.append({
                    "category": tech_req.category,
                    "required": tech_req.required,
                    "weight": tech_req.weight,
                    "matching_tools": matching_tools,
                    "expected_tools": tech_req.tools,
                    "score": req_score,
                    "max_score": req_max
                })
            else:
                details.append({
                    "category": tech_req.category,
                    "required": tech_req.required,
                    "weight": tech_req.weight,
                    "matching_tools": [],
                    "expected_tools": tech_req.tools,
                    "score": 0,
                    "max_score": req_max
                })
                
                if tech_req.required:
                    missing_critical.append(tech_req.category)
            
            total_score += req_score
        
        # Generate recommendations
        recommendations = []
        
        if missing_critical:
            recommendations.append(f"Missing critical technology categories: {', '.join(missing_critical)}")
        
        # Find categories where prospect has tools but not the recommended ones
        for tech_req in self.tech_requirements:
            if tech_req.category in prospect_tech_map:
                prospect_tools = prospect_tech_map[tech_req.category]
                if not any(tool in prospect_tools for tool in tech_req.tools):
                    recommendations.append(
                        f"Consider upgrading {tech_req.category} tools to recommended options: {', '.join(tech_req.tools)}"
                    )
        
        # Calculate percentage score
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        return {
            "total_score": total_score,
            "max_score": max_score,
            "percentage": percentage,
            "details": details,
            "missing_critical": missing_critical,
            "recommendations": recommendations
        }
        
    def detect_saas_waste(self, prospect: Any) -> Dict[str, Any]:
        """
        Detect potential SaaS waste for a prospect based on this ICP's waste patterns.
        
        Args:
            prospect: A Prospect object to analyze for waste
            
        Returns:
            Dict: A dictionary with waste detection results
        """
        if not prospect.technologies or not self.saas_waste_patterns:
            return {
                "total_monthly_waste": 0.0,
                "total_annual_waste": 0.0,
                "detected_patterns": [],
                "recommendations": []
            }
        
        # Check each waste pattern against the prospect's technology stack
        detected_patterns = []
        total_monthly_waste = 0.0
        
        for pattern in self.saas_waste_patterns:
            if pattern.matches(prospect.technologies):
                detected_patterns.append({
                    "name": pattern.name,
                    "description": pattern.description,
                    "estimated_monthly_waste": pattern.estimated_monthly_waste,
                    "priority": pattern.priority
                })
                total_monthly_waste += pattern.estimated_monthly_waste
        
        # Sort detected patterns by priority (highest first)
        detected_patterns.sort(key=lambda x: x["priority"], reverse=True)
        
        # Generate recommendations
        recommendations = []
        for pattern in detected_patterns:
            recommendations.append(f"Fix {pattern['name']}: {pattern['description']}")
        
        return {
            "total_monthly_waste": total_monthly_waste,
            "total_annual_waste": total_monthly_waste * 12,
            "detected_patterns": detected_patterns,
            "recommendations": recommendations
        }
        
    def calculate_roi(self, prospect: Any) -> Dict[str, Any]:
        """
        Calculate potential ROI for a prospect based on this ICP.
        
        Args:
            prospect: A Prospect object to calculate ROI for
            
        Returns:
            Dict: A dictionary with ROI calculation results
        """
        # Estimate monthly SaaS spend based on company size if not provided
        estimated_monthly_spend = self.avg_monthly_saas_spend
        
        if prospect.employee_count:
            # Adjust based on company size
            if prospect.employee_count < 10:
                size_factor = 0.5
            elif prospect.employee_count < 50:
                size_factor = 1.0
            elif prospect.employee_count < 200:
                size_factor = 2.0
            else:
                size_factor = 3.0
                
            estimated_monthly_spend = self.avg_monthly_saas_spend * size_factor
        
        # Estimate revenue if not provided
        estimated_revenue = prospect.revenue if prospect.revenue else self.min_revenue
        
        # Calculate waste based on detected patterns or average
        waste_detection = self.detect_saas_waste(prospect)
        monthly_waste = waste_detection["total_monthly_waste"]
        
        # If no specific waste detected, use average percentage
        if monthly_waste == 0 and self.avg_waste_percentage > 0:
            monthly_waste = estimated_monthly_spend * self.avg_waste_percentage
        
        # Calculate recoverable amount
        monthly_recoverable = monthly_waste * self.avg_recovery_percentage
        annual_recoverable = monthly_recoverable * 12
        
        # Calculate ROI metrics
        three_year_savings = annual_recoverable * 3
        
        # Calculate ROI as percentage of revenue
        roi_percentage = (annual_recoverable / estimated_revenue) * 100 if estimated_revenue > 0 else 0
        
        return {
            "estimated_monthly_saas_spend": estimated_monthly_spend,
            "estimated_annual_saas_spend": estimated_monthly_spend * 12,
            "estimated_monthly_waste": monthly_waste,
            "estimated_annual_waste": monthly_waste * 12,
            "monthly_recoverable": monthly_recoverable,
            "annual_recoverable": annual_recoverable,
            "three_year_savings": three_year_savings,
            "roi_percentage": roi_percentage,
            "waste_percentage": (monthly_waste / estimated_monthly_spend) * 100 if estimated_monthly_spend > 0 else 0
        }


@dataclass
class ShopifyDTCPremiumICP(ICP):
    """Shopify DTC Premium ICP for beauty/skincare businesses."""
    
    def __init__(self):
        super().__init__(
            name="Shopify DTC Premium (Beauty/Skincare)",
            icp_type=ICPType.BEAUTY_SKINCARE,
            description="Premium direct-to-consumer beauty and skincare brands using Shopify",
            min_revenue=500000,
            max_revenue=5000000,
            min_employees=5,
            max_employees=50,
            industries=["Beauty", "Skincare", "Cosmetics", "Personal Care"],
            categories=["skincare", "makeup", "beauty_tools", "supplements", "haircare"],
            target_countries=["United States", "Canada", "Australia", "United Kingdom"],
            avg_monthly_saas_spend=2500.0,
            avg_waste_percentage=0.18,
            avg_recovery_percentage=0.65
        )
        
        # Add tech requirements
        self.tech_requirements = [
            TechnologyRequirement(
                category="ecommerce_platform",
                tools=["shopify", "shopify_plus"],
                required=True,
                weight=1.5
            ),
            TechnologyRequirement(
                category="email_marketing",
                tools=["klaviyo", "mailchimp"],
                required=False,
                weight=1.2
            ),
            TechnologyRequirement(
                category="reviews",
                tools=["yotpo", "okendo", "judge.me"],
                required=False,
                weight=1.0
            ),
            TechnologyRequirement(
                category="subscriptions",
                tools=["recharge", "bold_subscriptions"],
                required=False,
                weight=1.3
            ),
            TechnologyRequirement(
                category="support",
                tools=["zendesk", "gorgias"],
                required=False,
                weight=0.8
            ),
            TechnologyRequirement(
                category="analytics",
                tools=["hotjar", "google_analytics"],
                required=False,
                weight=1.0
            ),
            TechnologyRequirement(
                category="forms",
                tools=["typeform", "klaviyo_forms"],
                required=False,
                weight=0.7
            )
        ]
        
        # Add SaaS waste patterns
        self.saas_waste_patterns = [
            SaaSWastePattern(
                name="Multiple Email Marketing Tools",
                description="Using multiple email marketing platforms leads to redundant costs and fragmented customer data",
                detection_pattern={"redundant_categories": ["email_marketing"]},
                estimated_monthly_waste=250.0,
                priority=4
            ),
            SaaSWastePattern(
                name="Redundant Analytics Tools",
                description="Multiple analytics tools with overlapping functionality",
                detection_pattern={"redundant_categories": ["analytics"]},
                estimated_monthly_waste=150.0,
                priority=3
            ),
            SaaSWastePattern(
                name="Expensive Review Platform Combination",
                description="Using both Yotpo and Okendo creates unnecessary expense",
                detection_pattern={
                    "tool_combinations": [
                        [
                            {"category": "reviews", "tool": "yotpo"},
                            {"category": "reviews", "tool": "okendo"}
                        ]
                    ]
                },
                estimated_monthly_waste=200.0,
                priority=3
            ),
            SaaSWastePattern(
                name="Underutilized Support Tools",
                description="Multiple customer support platforms that could be consolidated",
                detection_pattern={"redundant_categories": ["support"]},
                estimated_monthly_waste=300.0,
                priority=4
            )
        ]
        
        # Add revenue indicators
        self.revenue_indicators = [
            RevenueIndicator(
                name="premium_positioning",
                keywords=["premium skincare", "luxury beauty", "clinical grade", "dermatologist"],
                multiplier=1.5
            ),
            RevenueIndicator(
                name="subscription_model",
                keywords=["subscription box", "monthly", "subscribe and save"],
                multiplier=1.3
            ),
            RevenueIndicator(
                name="bundle_offers",
                keywords=["bundle", "kit", "set", "collection"],
                multiplier=1.2
            )
        ]
        
        # Add search dorks
        self.search_dorks = [
            '"Add to cart" site:myshopify.com "serum"',
            '"$25.00 USD" "skincare" site:shopifycdn.com',
            '"beauty" "subscription" site:myshopify.com',
            '"anti-aging" "cart" inurl:products',
            '"vitamin c" "buy now" site:shopify.com',
            '"moisturizer" "$" site:myshopify.com',
            '"cleanser" "add to bag" shopify'
        ]


@dataclass
class HealthSupplementsICP(ICP):
    """Health Supplements ICP for vitamin and wellness businesses."""
    
    def __init__(self):
        super().__init__(
            name="Health Supplements DTC",
            icp_type=ICPType.HEALTH_SUPPLEMENTS,
            description="Direct-to-consumer health supplement and vitamin brands",
            min_revenue=350000,
            max_revenue=3000000,
            min_employees=3,
            max_employees=30,
            industries=["Health", "Wellness", "Supplements", "Nutrition"],
            categories=["vitamins", "protein", "wellness", "fitness"],
            target_countries=["United States", "Canada", "Australia", "United Kingdom"],
            avg_monthly_saas_spend=1800.0,
            avg_waste_percentage=0.22,
            avg_recovery_percentage=0.70
        )
        
        # Add tech requirements
        self.tech_requirements = [
            TechnologyRequirement(
                category="ecommerce_platform",
                tools=["shopify", "woocommerce"],
                required=True,
                weight=1.4
            ),
            TechnologyRequirement(
                category="email_marketing",
                tools=["klaviyo", "convertkit"],
                required=False,
                weight=1.2
            ),
            TechnologyRequirement(
                category="subscriptions",
                tools=["recharge", "loop_subscriptions"],
                required=False,
                weight=1.5
            ),
            TechnologyRequirement(
                category="reviews",
                tools=["yotpo", "trustpilot"],
                required=False,
                weight=1.0
            ),
            TechnologyRequirement(
                category="analytics",
                tools=["google_analytics", "segment"],
                required=False,
                weight=0.8
            )
        ]
        
        # Add SaaS waste patterns
        self.saas_waste_patterns = [
            SaaSWastePattern(
                name="Multiple Subscription Tools",
                description="Using multiple subscription management tools creates redundant costs",
                detection_pattern={"redundant_categories": ["subscriptions"]},
                estimated_monthly_waste=180.0,
                priority=4
            ),
            SaaSWastePattern(
                name="Underutilized Analytics",
                description="Multiple analytics platforms with overlapping functionality",
                detection_pattern={"redundant_categories": ["analytics"]},
                estimated_monthly_waste=120.0,
                priority=3
            ),
            SaaSWastePattern(
                name="Expensive Email Marketing Combination",
                description="Using both Klaviyo and ConvertKit creates unnecessary expense",
                detection_pattern={
                    "tool_combinations": [
                        [
                            {"category": "email_marketing", "tool": "klaviyo"},
                            {"category": "email_marketing", "tool": "convertkit"}
                        ]
                    ]
                },
                estimated_monthly_waste=150.0,
                priority=3
            )
        ]
        
        # Add revenue indicators
        self.revenue_indicators = [
            RevenueIndicator(
                name="subscription_model",
                keywords=["subscription", "monthly", "subscribe and save"],
                multiplier=1.5
            ),
            RevenueIndicator(
                name="premium_positioning",
                keywords=["premium", "organic", "natural", "vegan"],
                multiplier=1.3
            )
        ]
        
        # Add search dorks
        self.search_dorks = [
            '"supplement" "buy now" site:myshopify.com',
            '"protein" "$" "add to cart"',
            '"vitamin" "subscription" shopify'
        ]


@dataclass
class FitnessEquipmentICP(ICP):
    """Fitness Equipment ICP for home gym and fitness accessory businesses."""
    
    def __init__(self):
        super().__init__(
            name="Fitness Equipment DTC",
            icp_type=ICPType.FITNESS_EQUIPMENT,
            description="Direct-to-consumer fitness equipment and accessory brands",
            min_revenue=300000,
            max_revenue=3000000,
            min_employees=3,
            max_employees=30,
            industries=["Fitness", "Sports", "Health", "Wellness"],
            categories=["home_gym", "accessories", "wearables"],
            target_countries=["United States", "Canada", "Australia", "United Kingdom"],
            avg_monthly_saas_spend=2000.0,
            avg_waste_percentage=0.20,
            avg_recovery_percentage=0.60
        )
        
        # Add tech requirements
        self.tech_requirements = [
            TechnologyRequirement(
                category="ecommerce_platform",
                tools=["shopify", "woocommerce", "bigcommerce"],
                required=True,
                weight=1.5
            ),
            TechnologyRequirement(
                category="email_marketing",
                tools=["klaviyo", "mailchimp", "omnisend"],
                required=False,
                weight=1.0
            ),
            TechnologyRequirement(
                category="analytics",
                tools=["google_analytics", "hotjar", "mixpanel"],
                required=False,
                weight=0.8
            ),
            TechnologyRequirement(
                category="reviews",
                tools=["yotpo", "trustpilot", "reviews.io"],
                required=False,
                weight=0.9
            ),
            TechnologyRequirement(
                category="shipping",
                tools=["shipstation", "shippo", "easyship"],
                required=False,
                weight=1.2
            )
        ]
        
        # Add SaaS waste patterns
        self.saas_waste_patterns = [
            SaaSWastePattern(
                name="Multiple Shipping Solutions",
                description="Using multiple shipping platforms creates unnecessary costs",
                detection_pattern={"redundant_categories": ["shipping"]},
                estimated_monthly_waste=180.0,
                priority=4
            ),
            SaaSWastePattern(
                name="Excessive Analytics Tools",
                description="Multiple analytics platforms with overlapping functionality",
                detection_pattern={"redundant_categories": ["analytics"]},
                estimated_monthly_waste=120.0,
                priority=3
            ),
            SaaSWastePattern(
                name="Expensive Email Marketing Combination",
                description="Using both Klaviyo and Mailchimp creates unnecessary expense",
                detection_pattern={
                    "tool_combinations": [
                        [
                            {"category": "email_marketing", "tool": "klaviyo"},
                            {"category": "email_marketing", "tool": "mailchimp"}
                        ]
                    ]
                },
                estimated_monthly_waste=200.0,
                priority=4
            ),
            SaaSWastePattern(
                name="Redundant Review Platforms",
                description="Multiple review platforms that could be consolidated",
                detection_pattern={"redundant_categories": ["reviews"]},
                estimated_monthly_waste=150.0,
                priority=3
            )
        ]
        
        # Add search dorks
        self.search_dorks = [
            '"fitness equipment" "cart" site:myshopify.com',
            '"home gym" "$" "buy"',
            '"workout" "add to cart" shopify'
        ]


def get_all_icps() -> List[ICP]:
    """Get all predefined ICPs."""
    return [
        ShopifyDTCPremiumICP(),
        HealthSupplementsICP(),
        FitnessEquipmentICP()
    ]


def get_icp_by_name(name: str) -> Optional[ICP]:
    """Get an ICP by name."""
    for icp in get_all_icps():
        if icp.name == name:
            return icp
    return None


def get_icp_by_type(icp_type: ICPType) -> Optional[ICP]:
    """Get an ICP by type."""
    for icp in get_all_icps():
        if icp.icp_type == icp_type:
            return icp
    return None