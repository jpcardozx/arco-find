"""
Financial Leak Detection System for ARCO.

This module contains the implementation of the financial leak detection system,
which identifies redundant apps, analyzes performance vs. conversion,
and calculates verified savings.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Tuple
from enum import Enum
import math
from datetime import datetime


@dataclass
class AppRedundancyPattern:
    """Pattern for detecting redundant apps."""
    
    name: str
    description: str
    categories: List[str]
    max_tools_per_category: int = 1
    estimated_monthly_waste: float = 0.0
    priority: int = 1  # 1-5, with 5 being highest priority
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "categories": self.categories,
            "max_tools_per_category": self.max_tools_per_category,
            "estimated_monthly_waste": self.estimated_monthly_waste,
            "priority": self.priority
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppRedundancyPattern':
        """Create from dictionary."""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            categories=data.get("categories", []),
            max_tools_per_category=data.get("max_tools_per_category", 1),
            estimated_monthly_waste=data.get("estimated_monthly_waste", 0.0),
            priority=data.get("priority", 1)
        )
    
    def detect(self, technologies: List[Any]) -> Dict[str, Any]:
        """
        Detect redundant apps based on this pattern.
        
        Args:
            technologies: List of Technology objects
            
        Returns:
            Dict with detection results
        """
        results = {
            "detected": False,
            "redundant_categories": [],
            "redundant_tools": {},
            "estimated_waste": 0.0
        }
        
        # Group technologies by category
        tech_by_category = {}
        for tech in technologies:
            if tech.category not in tech_by_category:
                tech_by_category[tech.category] = []
            tech_by_category[tech.category].append(tech.name)
        
        # Check for redundancies in specified categories
        for category in self.categories:
            if category in tech_by_category and len(tech_by_category[category]) > self.max_tools_per_category:
                results["detected"] = True
                results["redundant_categories"].append(category)
                results["redundant_tools"][category] = tech_by_category[category]
                results["estimated_waste"] += self.estimated_monthly_waste
        
        return results


@dataclass
class PerformanceConversionAnalysis:
    """Analysis of performance vs. conversion."""
    
    name: str
    description: str
    performance_metrics: Dict[str, Any]
    conversion_metrics: Dict[str, Any]
    benchmark_data: Dict[str, Any]
    estimated_monthly_waste: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "performance_metrics": self.performance_metrics,
            "conversion_metrics": self.conversion_metrics,
            "benchmark_data": self.benchmark_data,
            "estimated_monthly_waste": self.estimated_monthly_waste
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PerformanceConversionAnalysis':
        """Create from dictionary."""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            performance_metrics=data.get("performance_metrics", {}),
            conversion_metrics=data.get("conversion_metrics", {}),
            benchmark_data=data.get("benchmark_data", {}),
            estimated_monthly_waste=data.get("estimated_monthly_waste", 0.0)
        )
    
    def analyze(self, prospect_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze performance vs. conversion for a prospect.
        
        Args:
            prospect_data: Dictionary with prospect performance and conversion data
            
        Returns:
            Dict with analysis results
        """
        results = {
            "name": self.name,
            "description": self.description,
            "issues_detected": False,
            "performance_issues": [],
            "conversion_issues": [],
            "recommendations": [],
            "estimated_waste": 0.0
        }
        
        # Check performance metrics
        for metric, benchmark in self.benchmark_data.get("performance", {}).items():
            if metric in prospect_data.get("performance", {}):
                prospect_value = prospect_data["performance"][metric]
                if self._is_performance_issue(metric, prospect_value, benchmark):
                    results["issues_detected"] = True
                    issue = {
                        "metric": metric,
                        "current_value": prospect_value,
                        "benchmark": benchmark,
                        "gap": self._calculate_gap(metric, prospect_value, benchmark)
                    }
                    results["performance_issues"].append(issue)
                    
                    # Add recommendation
                    recommendation = self._generate_recommendation(metric, prospect_value, benchmark)
                    if recommendation:
                        results["recommendations"].append(recommendation)
        
        # Check conversion metrics
        for metric, benchmark in self.benchmark_data.get("conversion", {}).items():
            if metric in prospect_data.get("conversion", {}):
                prospect_value = prospect_data["conversion"][metric]
                if self._is_conversion_issue(metric, prospect_value, benchmark):
                    results["issues_detected"] = True
                    issue = {
                        "metric": metric,
                        "current_value": prospect_value,
                        "benchmark": benchmark,
                        "gap": self._calculate_gap(metric, prospect_value, benchmark)
                    }
                    results["conversion_issues"].append(issue)
                    
                    # Add recommendation
                    recommendation = self._generate_recommendation(metric, prospect_value, benchmark)
                    if recommendation:
                        results["recommendations"].append(recommendation)
        
        # Calculate estimated waste if issues detected
        if results["issues_detected"]:
            results["estimated_waste"] = self._calculate_estimated_waste(
                results["performance_issues"], 
                results["conversion_issues"]
            )
        
        return results
    
    def _is_performance_issue(self, metric: str, value: float, benchmark: float) -> bool:
        """Check if a performance metric indicates an issue."""
        # For performance metrics, higher is usually worse (e.g., load time)
        if metric in ["load_time", "ttfb", "fcp", "lcp", "cls", "fid"]:
            return value > benchmark
        # For some metrics, lower is worse (e.g., performance score)
        elif metric in ["performance_score", "accessibility_score"]:
            return value < benchmark
        return False
    
    def _is_conversion_issue(self, metric: str, value: float, benchmark: float) -> bool:
        """Check if a conversion metric indicates an issue."""
        # For conversion metrics, lower is usually worse
        if metric in ["conversion_rate", "add_to_cart_rate", "checkout_completion"]:
            return value < benchmark
        # For some metrics, higher is worse (e.g., bounce rate)
        elif metric in ["bounce_rate", "cart_abandonment"]:
            return value > benchmark
        return False
    
    def _calculate_gap(self, metric: str, value: float, benchmark: float) -> float:
        """Calculate the gap between current value and benchmark."""
        if metric in ["conversion_rate", "add_to_cart_rate", "checkout_completion", 
                     "performance_score", "accessibility_score"]:
            # For these metrics, gap is how much lower the value is than benchmark
            return max(0, benchmark - value)
        else:
            # For other metrics, gap is how much higher the value is than benchmark
            return max(0, value - benchmark)
    
    def _generate_recommendation(self, metric: str, value: float, benchmark: float) -> str:
        """Generate a recommendation based on the metric and gap."""
        if metric == "load_time":
            return f"Optimize page load time from {value:.2f}s to target {benchmark:.2f}s"
        elif metric == "conversion_rate":
            return f"Improve conversion rate from {value:.2f}% to industry benchmark {benchmark:.2f}%"
        elif metric == "bounce_rate":
            return f"Reduce bounce rate from {value:.2f}% to target {benchmark:.2f}%"
        elif metric == "cart_abandonment":
            return f"Reduce cart abandonment from {value:.2f}% to target {benchmark:.2f}%"
        return ""
    
    def _calculate_estimated_waste(self, performance_issues: List[Dict], conversion_issues: List[Dict]) -> float:
        """Calculate estimated waste based on performance and conversion issues."""
        # Start with base waste estimate
        waste = self.estimated_monthly_waste
        
        # Adjust based on severity of issues
        performance_factor = sum(issue["gap"] for issue in performance_issues) / len(performance_issues) if performance_issues else 0
        conversion_factor = sum(issue["gap"] for issue in conversion_issues) / len(conversion_issues) if conversion_issues else 0
        
        # Apply factors to base waste
        waste_multiplier = 1.0 + (performance_factor * 0.1) + (conversion_factor * 0.2)
        return waste * waste_multiplier


@dataclass
class VerifiedSavings:
    """Calculation of verified savings."""
    
    name: str
    description: str
    savings_type: str  # "cost_reduction", "revenue_increase", "efficiency_gain"
    monthly_amount: float
    verification_method: str
    verification_data: Dict[str, Any]
    confidence_level: float  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "savings_type": self.savings_type,
            "monthly_amount": self.monthly_amount,
            "verification_method": self.verification_method,
            "verification_data": self.verification_data,
            "confidence_level": self.confidence_level
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VerifiedSavings':
        """Create from dictionary."""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            savings_type=data.get("savings_type", ""),
            monthly_amount=data.get("monthly_amount", 0.0),
            verification_method=data.get("verification_method", ""),
            verification_data=data.get("verification_data", {}),
            confidence_level=data.get("confidence_level", 0.0)
        )
    
    def calculate(self, prospect_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate verified savings for a prospect.
        
        Args:
            prospect_data: Dictionary with prospect data
            
        Returns:
            Dict with savings calculation results
        """
        results = {
            "name": self.name,
            "description": self.description,
            "savings_type": self.savings_type,
            "monthly_savings": 0.0,
            "annual_savings": 0.0,
            "three_year_savings": 0.0,
            "verification_method": self.verification_method,
            "confidence_level": self.confidence_level,
            "verification_details": {}
        }
        
        # Calculate base monthly savings
        monthly_savings = self.monthly_amount
        
        # Adjust based on prospect data
        if self.savings_type == "cost_reduction":
            # Adjust based on company size
            if "employee_count" in prospect_data:
                size_factor = self._calculate_size_factor(prospect_data["employee_count"])
                monthly_savings *= size_factor
        
        elif self.savings_type == "revenue_increase":
            # Adjust based on current revenue
            if "revenue" in prospect_data:
                revenue_factor = self._calculate_revenue_factor(prospect_data["revenue"])
                monthly_savings *= revenue_factor
        
        # Apply confidence level
        verified_monthly_savings = monthly_savings * self.confidence_level
        
        # Calculate annual and three-year savings
        annual_savings = verified_monthly_savings * 12
        three_year_savings = annual_savings * 3
        
        # Update results
        results["monthly_savings"] = verified_monthly_savings
        results["annual_savings"] = annual_savings
        results["three_year_savings"] = three_year_savings
        
        # Add verification details
        results["verification_details"] = self._generate_verification_details(prospect_data)
        
        return results
    
    def _calculate_size_factor(self, employee_count: int) -> float:
        """Calculate size factor based on employee count."""
        if employee_count < 10:
            return 0.5
        elif employee_count < 50:
            return 1.0
        elif employee_count < 200:
            return 2.0
        else:
            return 3.0
    
    def _calculate_revenue_factor(self, revenue: float) -> float:
        """Calculate revenue factor based on company revenue."""
        if revenue < 500000:
            return 0.5
        elif revenue < 2000000:
            return 1.0
        elif revenue < 10000000:
            return 2.0
        else:
            return 3.0
    
    def _generate_verification_details(self, prospect_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate verification details based on prospect data."""
        details = {
            "methodology": self.verification_method,
            "data_sources": [],
            "calculations": [],
            "assumptions": []
        }
        
        # Add data sources
        if "technologies" in prospect_data:
            details["data_sources"].append("Technology stack analysis")
        if "performance" in prospect_data:
            details["data_sources"].append("Performance metrics analysis")
        if "conversion" in prospect_data:
            details["data_sources"].append("Conversion metrics analysis")
        
        # Add calculations based on savings type
        if self.savings_type == "cost_reduction":
            details["calculations"].append(f"Base monthly savings: ${self.monthly_amount:.2f}")
            if "employee_count" in prospect_data:
                size_factor = self._calculate_size_factor(prospect_data["employee_count"])
                details["calculations"].append(f"Size adjustment factor: {size_factor:.2f}x")
            details["calculations"].append(f"Confidence level: {self.confidence_level:.0%}")
        
        elif self.savings_type == "revenue_increase":
            details["calculations"].append(f"Base monthly revenue increase: ${self.monthly_amount:.2f}")
            if "revenue" in prospect_data:
                revenue_factor = self._calculate_revenue_factor(prospect_data["revenue"])
                details["calculations"].append(f"Revenue adjustment factor: {revenue_factor:.2f}x")
            details["calculations"].append(f"Confidence level: {self.confidence_level:.0%}")
        
        # Add assumptions
        details["assumptions"] = self.verification_data.get("assumptions", [])
        
        return details


class FinancialLeakDetector:
    """Financial leak detection system."""
    
    def __init__(self):
        """Initialize the financial leak detector."""
        # Initialize default redundancy patterns
        self.redundancy_patterns = [
            AppRedundancyPattern(
                name="Multiple Email Marketing Tools",
                description="Using multiple email marketing platforms leads to redundant costs and fragmented customer data",
                categories=["email_marketing"],
                estimated_monthly_waste=250.0,
                priority=4
            ),
            AppRedundancyPattern(
                name="Redundant Analytics Tools",
                description="Multiple analytics tools with overlapping functionality",
                categories=["analytics"],
                estimated_monthly_waste=150.0,
                priority=3
            ),
            AppRedundancyPattern(
                name="Multiple Customer Support Platforms",
                description="Using multiple customer support platforms creates inefficiencies and increases costs",
                categories=["support"],
                estimated_monthly_waste=300.0,
                priority=4
            ),
            AppRedundancyPattern(
                name="Redundant Form Tools",
                description="Multiple form tools with overlapping functionality",
                categories=["forms"],
                estimated_monthly_waste=100.0,
                priority=2
            ),
            AppRedundancyPattern(
                name="Multiple Review Platforms",
                description="Using multiple review platforms increases costs and fragments social proof",
                categories=["reviews"],
                estimated_monthly_waste=200.0,
                priority=3
            )
        ]
        
        # Initialize default performance-conversion analyses
        self.performance_analyses = [
            PerformanceConversionAnalysis(
                name="Page Speed vs. Conversion",
                description="Analysis of page load speed impact on conversion rates",
                performance_metrics={
                    "load_time": "Time in seconds for page to fully load",
                    "ttfb": "Time to First Byte",
                    "fcp": "First Contentful Paint",
                    "lcp": "Largest Contentful Paint"
                },
                conversion_metrics={
                    "bounce_rate": "Percentage of visitors who leave after viewing only one page",
                    "conversion_rate": "Percentage of visitors who complete a desired action"
                },
                benchmark_data={
                    "performance": {
                        "load_time": 2.5,  # seconds
                        "ttfb": 0.8,       # seconds
                        "fcp": 1.8,        # seconds
                        "lcp": 2.5         # seconds
                    },
                    "conversion": {
                        "bounce_rate": 35.0,  # percent
                        "conversion_rate": 3.2 # percent
                    }
                },
                estimated_monthly_waste=500.0
            ),
            PerformanceConversionAnalysis(
                name="Checkout Experience Analysis",
                description="Analysis of checkout flow and its impact on cart abandonment",
                performance_metrics={
                    "checkout_steps": "Number of steps in checkout process",
                    "checkout_load_time": "Time to load checkout page",
                    "payment_options": "Number of payment options available"
                },
                conversion_metrics={
                    "cart_abandonment": "Percentage of users who add items to cart but don't complete purchase",
                    "checkout_completion": "Percentage of users who complete checkout after starting it"
                },
                benchmark_data={
                    "performance": {
                        "checkout_steps": 3,      # steps
                        "checkout_load_time": 1.5, # seconds
                        "payment_options": 4      # options
                    },
                    "conversion": {
                        "cart_abandonment": 70.0, # percent
                        "checkout_completion": 65.0 # percent
                    }
                },
                estimated_monthly_waste=750.0
            )
        ]
        
        # Initialize default verified savings calculations
        self.savings_calculations = [
            VerifiedSavings(
                name="App Consolidation Savings",
                description="Verified savings from consolidating redundant SaaS applications",
                savings_type="cost_reduction",
                monthly_amount=350.0,
                verification_method="Direct cost comparison",
                verification_data={
                    "assumptions": [
                        "Average SaaS tool costs $150/month",
                        "Consolidation eliminates 2-3 redundant tools",
                        "Implementation requires 5-10 hours of work"
                    ]
                },
                confidence_level=0.9
            ),
            VerifiedSavings(
                name="Conversion Rate Optimization",
                description="Revenue increase from optimizing conversion rates",
                savings_type="revenue_increase",
                monthly_amount=1200.0,
                verification_method="A/B testing results",
                verification_data={
                    "assumptions": [
                        "Average conversion rate increase of 0.5-1.5%",
                        "Average order value remains constant",
                        "Traffic levels remain consistent"
                    ]
                },
                confidence_level=0.7
            ),
            VerifiedSavings(
                name="Performance Optimization",
                description="Revenue increase from improving site performance",
                savings_type="revenue_increase",
                monthly_amount=800.0,
                verification_method="Before/after performance comparison",
                verification_data={
                    "assumptions": [
                        "1 second page speed improvement leads to 7% conversion increase",
                        "Bounce rate decreases by 5-10%",
                        "Implementation requires 10-20 hours of development work"
                    ]
                },
                confidence_level=0.8
            )
        ]
    
    def detect_redundant_apps(self, technologies: List[Any]) -> Dict[str, Any]:
        """
        Detect redundant apps in a prospect's technology stack.
        
        Args:
            technologies: List of Technology objects
            
        Returns:
            Dict with redundancy detection results
        """
        results = {
            "redundancies_detected": False,
            "patterns_matched": [],
            "total_monthly_waste": 0.0,
            "total_annual_waste": 0.0,
            "recommendations": []
        }
        
        for pattern in self.redundancy_patterns:
            detection_result = pattern.detect(technologies)
            
            if detection_result["detected"]:
                results["redundancies_detected"] = True
                
                pattern_result = {
                    "name": pattern.name,
                    "description": pattern.description,
                    "redundant_categories": detection_result["redundant_categories"],
                    "redundant_tools": detection_result["redundant_tools"],
                    "estimated_monthly_waste": detection_result["estimated_waste"],
                    "priority": pattern.priority
                }
                
                results["patterns_matched"].append(pattern_result)
                results["total_monthly_waste"] += detection_result["estimated_waste"]
                
                # Generate recommendation
                for category in detection_result["redundant_categories"]:
                    tools = detection_result["redundant_tools"][category]
                    recommendation = f"Consolidate {category} tools: Currently using {', '.join(tools)}"
                    results["recommendations"].append(recommendation)
        
        # Calculate annual waste
        results["total_annual_waste"] = results["total_monthly_waste"] * 12
        
        # Sort recommendations by priority
        results["patterns_matched"].sort(key=lambda x: x["priority"], reverse=True)
        
        return results
    
    def analyze_performance_conversion(self, prospect_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze performance vs. conversion for a prospect.
        
        Args:
            prospect_data: Dictionary with prospect performance and conversion data
            
        Returns:
            Dict with analysis results
        """
        results = {
            "issues_detected": False,
            "analyses": [],
            "total_monthly_waste": 0.0,
            "total_annual_waste": 0.0,
            "recommendations": []
        }
        
        for analysis in self.performance_analyses:
            analysis_result = analysis.analyze(prospect_data)
            
            if analysis_result["issues_detected"]:
                results["issues_detected"] = True
                results["analyses"].append(analysis_result)
                results["total_monthly_waste"] += analysis_result["estimated_waste"]
                results["recommendations"].extend(analysis_result["recommendations"])
        
        # Calculate annual waste
        results["total_annual_waste"] = results["total_monthly_waste"] * 12
        
        return results
    
    def calculate_verified_savings(self, prospect_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate verified savings for a prospect.
        
        Args:
            prospect_data: Dictionary with prospect data
            
        Returns:
            Dict with savings calculation results
        """
        results = {
            "calculations": [],
            "total_monthly_savings": 0.0,
            "total_annual_savings": 0.0,
            "total_three_year_savings": 0.0,
            "roi_percentage": 0.0
        }
        
        for calculation in self.savings_calculations:
            calculation_result = calculation.calculate(prospect_data)
            
            results["calculations"].append(calculation_result)
            results["total_monthly_savings"] += calculation_result["monthly_savings"]
            results["total_annual_savings"] += calculation_result["annual_savings"]
            results["total_three_year_savings"] += calculation_result["three_year_savings"]
        
        # Calculate ROI percentage if revenue is available
        if "revenue" in prospect_data and prospect_data["revenue"] > 0:
            results["roi_percentage"] = (results["total_annual_savings"] / prospect_data["revenue"]) * 100
        
        return results
    
    def detect_financial_leaks(self, prospect: Any) -> Dict[str, Any]:
        """
        Detect all financial leaks for a prospect.
        
        Args:
            prospect: A Prospect object
            
        Returns:
            Dict with comprehensive financial leak detection results
        """
        results = {
            "domain": prospect.domain,
            "company_name": prospect.company_name,
            "detection_date": datetime.now().isoformat(),
            "redundant_apps": {},
            "performance_conversion": {},
            "verified_savings": {},
            "summary": {
                "total_monthly_waste": 0.0,
                "total_annual_waste": 0.0,
                "total_monthly_savings": 0.0,
                "total_annual_savings": 0.0,
                "total_three_year_savings": 0.0,
                "roi_percentage": 0.0,
                "priority_recommendations": []
            }
        }
        
        # Create prospect data dictionary
        prospect_data = {
            "domain": prospect.domain,
            "company_name": prospect.company_name,
            "employee_count": prospect.employee_count,
            "revenue": prospect.revenue,
            "industry": prospect.industry,
            "country": prospect.country
        }
        
        # Add mock performance and conversion data for demonstration
        # In a real implementation, this would come from actual analytics
        prospect_data["performance"] = self._generate_mock_performance_data(prospect)
        prospect_data["conversion"] = self._generate_mock_conversion_data(prospect)
        
        # Detect redundant apps
        if hasattr(prospect, "technologies") and prospect.technologies:
            results["redundant_apps"] = self.detect_redundant_apps(prospect.technologies)
            results["summary"]["total_monthly_waste"] += results["redundant_apps"]["total_monthly_waste"]
            results["summary"]["total_annual_waste"] += results["redundant_apps"]["total_annual_waste"]
            
            # Add priority recommendations
            if results["redundant_apps"]["redundancies_detected"]:
                # Get top 2 recommendations by priority
                top_patterns = sorted(results["redundant_apps"]["patterns_matched"], 
                                     key=lambda x: x["priority"], reverse=True)[:2]
                for pattern in top_patterns:
                    results["summary"]["priority_recommendations"].append(
                        f"Fix {pattern['name']}: {pattern['description']}"
                    )
        
        # Analyze performance vs. conversion
        results["performance_conversion"] = self.analyze_performance_conversion(prospect_data)
        results["summary"]["total_monthly_waste"] += results["performance_conversion"]["total_monthly_waste"]
        results["summary"]["total_annual_waste"] += results["performance_conversion"]["total_annual_waste"]
        
        # Add priority recommendations from performance analysis
        if results["performance_conversion"]["issues_detected"]:
            # Get top 2 recommendations
            top_recommendations = results["performance_conversion"]["recommendations"][:2]
            results["summary"]["priority_recommendations"].extend(top_recommendations)
        
        # Calculate verified savings
        results["verified_savings"] = self.calculate_verified_savings(prospect_data)
        results["summary"]["total_monthly_savings"] = results["verified_savings"]["total_monthly_savings"]
        results["summary"]["total_annual_savings"] = results["verified_savings"]["total_annual_savings"]
        results["summary"]["total_three_year_savings"] = results["verified_savings"]["total_three_year_savings"]
        results["summary"]["roi_percentage"] = results["verified_savings"]["roi_percentage"]
        
        return results
    
    def _generate_mock_performance_data(self, prospect: Any) -> Dict[str, float]:
        """Generate mock performance data for demonstration purposes."""
        import random
        
        # Base performance metrics
        performance = {
            "load_time": 3.2,  # seconds
            "ttfb": 1.1,       # seconds
            "fcp": 2.3,        # seconds
            "lcp": 3.5,        # seconds
            "cls": 0.15,       # Cumulative Layout Shift
            "fid": 120,        # First Input Delay (ms)
            "performance_score": 65,  # Lighthouse score
            "accessibility_score": 78, # Lighthouse score
            "checkout_steps": 4,      # steps
            "checkout_load_time": 2.2, # seconds
            "payment_options": 3      # options
        }
        
        # Adjust based on technologies
        if hasattr(prospect, "technologies"):
            for tech in prospect.technologies:
                # Shopify sites tend to be slower
                if tech.name == "shopify" and tech.category == "ecommerce_platform":
                    performance["load_time"] += 0.5
                    performance["lcp"] += 0.7
                
                # Sites with many marketing tools tend to be slower
                if tech.category in ["analytics", "marketing", "advertising"]:
                    performance["load_time"] += 0.2
                    performance["fcp"] += 0.2
                    performance["lcp"] += 0.3
                
                # Sites with optimization tools tend to be faster
                if tech.name in ["cloudflare", "fastly", "akamai"]:
                    performance["load_time"] -= 0.5
                    performance["ttfb"] -= 0.3
        
        # Add some randomness
        for key in performance:
            if isinstance(performance[key], (int, float)):
                # Add +/- 10% randomness
                performance[key] *= random.uniform(0.9, 1.1)
        
        return performance
    
    def _generate_mock_conversion_data(self, prospect: Any) -> Dict[str, float]:
        """Generate mock conversion data for demonstration purposes."""
        import random
        
        # Base conversion metrics
        conversion = {
            "bounce_rate": 45.0,  # percent
            "conversion_rate": 2.5, # percent
            "add_to_cart_rate": 8.0, # percent
            "cart_abandonment": 75.0, # percent
            "checkout_completion": 55.0 # percent
        }
        
        # Adjust based on technologies
        if hasattr(prospect, "technologies"):
            for tech in prospect.technologies:
                # Sites with good email marketing tend to have better conversion
                if tech.name in ["klaviyo", "omnisend"] and tech.category == "email_marketing":
                    conversion["conversion_rate"] += 0.5
                    conversion["bounce_rate"] -= 3.0
                
                # Sites with good review platforms tend to have better conversion
                if tech.name in ["yotpo", "okendo"] and tech.category == "reviews":
                    conversion["conversion_rate"] += 0.3
                    conversion["add_to_cart_rate"] += 1.5
                
                # Sites with subscription tools tend to have better retention
                if tech.name in ["recharge", "bold_subscriptions"] and tech.category == "subscriptions":
                    conversion["conversion_rate"] += 0.4
                
                # Sites with abandoned cart recovery tend to have lower cart abandonment
                if tech.name in ["carthook", "klaviyo"] and tech.category in ["cart_recovery", "email_marketing"]:
                    conversion["cart_abandonment"] -= 5.0
        
        # Add some randomness
        for key in conversion:
            if isinstance(conversion[key], (int, float)):
                # Add +/- 15% randomness
                conversion[key] *= random.uniform(0.85, 1.15)
        
        return conversion