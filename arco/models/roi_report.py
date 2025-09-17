"""
ROI Report Generation System for ARCO.

This module contains the implementation of the ROI report generation system,
which creates templates for "14-Day Revenue Recovery Pilot", calculates
projected savings, and visualizes performance vs. competitors.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Tuple
from enum import Enum
import math
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

from arco.models.financial_leak import FinancialLeakDetector
from arco.models.icp import ICP


@dataclass
class ReportTemplate:
    """Template for ROI reports."""
    
    name: str
    description: str
    sections: List[str]
    placeholders: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "sections": self.sections,
            "placeholders": self.placeholders
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReportTemplate':
        """Create from dictionary."""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            sections=data.get("sections", []),
            placeholders=data.get("placeholders", {})
        )


@dataclass
class ProjectedSavings:
    """Projected savings calculation."""
    
    name: str
    description: str
    baseline_monthly_waste: float
    growth_factors: Dict[str, float]
    confidence_levels: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "baseline_monthly_waste": self.baseline_monthly_waste,
            "growth_factors": self.growth_factors,
            "confidence_levels": self.confidence_levels
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectedSavings':
        """Create from dictionary."""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            baseline_monthly_waste=data.get("baseline_monthly_waste", 0.0),
            growth_factors=data.get("growth_factors", {}),
            confidence_levels=data.get("confidence_levels", {})
        )
    
    def calculate(self, prospect_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate projected savings for a prospect.
        
        Args:
            prospect_data: Dictionary with prospect data
            
        Returns:
            Dict with projected savings calculation results
        """
        results = {
            "name": self.name,
            "description": self.description,
            "baseline_monthly_waste": self.baseline_monthly_waste,
            "monthly_projections": {},
            "quarterly_projections": {},
            "annual_projections": {},
            "three_year_projections": {},
            "roi_metrics": {}
        }
        
        # Adjust baseline waste based on company size
        adjusted_baseline = self.baseline_monthly_waste
        if "employee_count" in prospect_data:
            size_factor = self._calculate_size_factor(prospect_data["employee_count"])
            adjusted_baseline *= size_factor
        
        # Adjust baseline waste based on revenue
        if "revenue" in prospect_data:
            revenue_factor = self._calculate_revenue_factor(prospect_data["revenue"])
            adjusted_baseline *= revenue_factor
        
        # Calculate monthly projections (14-day pilot and beyond)
        monthly_projections = {}
        
        # 14-day pilot (half a month)
        pilot_savings = adjusted_baseline * 0.5 * self.confidence_levels.get("pilot", 0.6)
        monthly_projections["pilot"] = pilot_savings
        
        # Month 1 (after pilot)
        month1_savings = adjusted_baseline * self.confidence_levels.get("month1", 0.7)
        monthly_projections["month1"] = month1_savings
        
        # Month 2
        month2_factor = 1.0 + self.growth_factors.get("month2", 0.1)
        month2_savings = month1_savings * month2_factor * self.confidence_levels.get("month2", 0.8)
        monthly_projections["month2"] = month2_savings
        
        # Month 3
        month3_factor = 1.0 + self.growth_factors.get("month3", 0.15)
        month3_savings = month2_savings * month3_factor * self.confidence_levels.get("month3", 0.85)
        monthly_projections["month3"] = month3_savings
        
        # Month 6
        month6_factor = 1.0 + self.growth_factors.get("month6", 0.25)
        month6_savings = month3_savings * month6_factor * self.confidence_levels.get("month6", 0.9)
        monthly_projections["month6"] = month6_savings
        
        # Month 12
        month12_factor = 1.0 + self.growth_factors.get("month12", 0.4)
        month12_savings = month6_savings * month12_factor * self.confidence_levels.get("month12", 0.95)
        monthly_projections["month12"] = month12_savings
        
        results["monthly_projections"] = monthly_projections
        
        # Calculate quarterly projections
        quarterly_projections = {
            "q1": month1_savings + month2_savings + month3_savings,
            "q2": month3_savings * 1.1 * 3,  # Estimate for months 4-6
            "q3": month6_savings * 1.2 * 3,  # Estimate for months 7-9
            "q4": month12_savings * 0.9 * 3  # Estimate for months 10-12
        }
        results["quarterly_projections"] = quarterly_projections
        
        # Calculate annual projections
        annual_projections = {
            "year1": sum(quarterly_projections.values()),
            "year2": sum(quarterly_projections.values()) * 1.3,
            "year3": sum(quarterly_projections.values()) * 1.5
        }
        results["annual_projections"] = annual_projections
        
        # Calculate three-year projection
        results["three_year_projections"] = {
            "total": sum(annual_projections.values()),
            "average_annual": sum(annual_projections.values()) / 3
        }
        
        # Calculate ROI metrics
        if "revenue" in prospect_data and prospect_data["revenue"] > 0:
            results["roi_metrics"] = {
                "pilot_roi_percentage": (pilot_savings / prospect_data["revenue"]) * 100 * 24,  # Annualized
                "first_year_roi_percentage": (annual_projections["year1"] / prospect_data["revenue"]) * 100,
                "three_year_roi_percentage": (results["three_year_projections"]["total"] / (prospect_data["revenue"] * 3)) * 100
            }
        else:
            results["roi_metrics"] = {
                "pilot_roi_percentage": 0.0,
                "first_year_roi_percentage": 0.0,
                "three_year_roi_percentage": 0.0
            }
        
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


@dataclass
class CompetitorBenchmark:
    """Benchmark data for competitor comparison."""
    
    name: str
    description: str
    metrics: Dict[str, Dict[str, float]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "metrics": self.metrics
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompetitorBenchmark':
        """Create from dictionary."""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            metrics=data.get("metrics", {})
        )
    
    def compare(self, prospect_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare prospect performance against benchmarks.
        
        Args:
            prospect_data: Dictionary with prospect performance data
            
        Returns:
            Dict with comparison results
        """
        results = {
            "name": self.name,
            "description": self.description,
            "comparisons": {},
            "summary": {
                "ahead_count": 0,
                "behind_count": 0,
                "total_gap": 0.0,
                "average_gap_percentage": 0.0
            }
        }
        
        # Compare each metric category
        for category, metrics in self.metrics.items():
            category_results = {
                "metrics": {},
                "ahead_count": 0,
                "behind_count": 0,
                "average_gap": 0.0
            }
            
            if category in prospect_data:
                prospect_metrics = prospect_data[category]
                
                for metric_name, benchmark_value in metrics.items():
                    if metric_name in prospect_metrics:
                        prospect_value = prospect_metrics[metric_name]
                        
                        # Determine if higher or lower is better for this metric
                        higher_is_better = self._is_higher_better(category, metric_name)
                        
                        # Calculate gap and determine if ahead or behind
                        if higher_is_better:
                            gap = prospect_value - benchmark_value
                            ahead = gap >= 0
                        else:
                            gap = benchmark_value - prospect_value
                            ahead = gap <= 0
                        
                        # Calculate gap percentage
                        if benchmark_value != 0:
                            gap_percentage = (abs(gap) / benchmark_value) * 100
                        else:
                            gap_percentage = 0.0
                        
                        metric_result = {
                            "prospect_value": prospect_value,
                            "benchmark_value": benchmark_value,
                            "gap": gap,
                            "gap_percentage": gap_percentage,
                            "ahead": ahead
                        }
                        
                        category_results["metrics"][metric_name] = metric_result
                        
                        if ahead:
                            category_results["ahead_count"] += 1
                        else:
                            category_results["behind_count"] += 1
                            category_results["average_gap"] += gap_percentage
            
            # Calculate average gap for this category
            if category_results["behind_count"] > 0:
                category_results["average_gap"] /= category_results["behind_count"]
            
            results["comparisons"][category] = category_results
            
            # Update summary
            results["summary"]["ahead_count"] += category_results["ahead_count"]
            results["summary"]["behind_count"] += category_results["behind_count"]
            results["summary"]["total_gap"] += category_results["average_gap"] * category_results["behind_count"]
        
        # Calculate overall average gap percentage
        if results["summary"]["behind_count"] > 0:
            results["summary"]["average_gap_percentage"] = results["summary"]["total_gap"] / results["summary"]["behind_count"]
        
        return results
    
    def _is_higher_better(self, category: str, metric_name: str) -> bool:
        """Determine if a higher value is better for a given metric."""
        # Performance metrics where lower is better
        lower_better_performance = {
            "load_time", "ttfb", "fcp", "lcp", "cls", "fid", 
            "checkout_steps", "checkout_load_time"
        }
        
        # Conversion metrics where higher is better
        higher_better_conversion = {
            "conversion_rate", "add_to_cart_rate", "checkout_completion"
        }
        
        if category == "performance" and metric_name in lower_better_performance:
            return False
        elif category == "conversion" and metric_name in higher_better_conversion:
            return True
        elif category == "conversion":  # Most other conversion metrics (like bounce rate) lower is better
            return False
        
        # Default: higher is better
        return True


class ROIReportGenerator:
    """ROI report generation system."""
    
    def __init__(self):
        """Initialize the ROI report generator."""
        # Initialize default report templates
        self.report_templates = [
            ReportTemplate(
                name="14-Day Revenue Recovery Pilot",
                description="Short-term pilot program to demonstrate immediate ROI",
                sections=[
                    "Executive Summary",
                    "Current State Analysis",
                    "Waste Detection Results",
                    "14-Day Pilot Plan",
                    "Expected Outcomes",
                    "Implementation Timeline",
                    "Next Steps"
                ],
                placeholders={
                    "COMPANY_NAME": "Client company name",
                    "CURRENT_DATE": "Current date",
                    "TOTAL_WASTE": "Total detected waste amount",
                    "PILOT_SAVINGS": "Expected savings during pilot",
                    "ANNUAL_PROJECTION": "Projected annual savings",
                    "TOP_RECOMMENDATIONS": "Top 3 recommendations"
                }
            ),
            ReportTemplate(
                name="Quarterly ROI Projection",
                description="Medium-term ROI projection for quarterly planning",
                sections=[
                    "Executive Summary",
                    "Q1 Projections",
                    "Q2 Projections",
                    "Q3 Projections",
                    "Q4 Projections",
                    "Implementation Roadmap",
                    "Success Metrics"
                ],
                placeholders={
                    "COMPANY_NAME": "Client company name",
                    "CURRENT_DATE": "Current date",
                    "Q1_SAVINGS": "Q1 projected savings",
                    "Q2_SAVINGS": "Q2 projected savings",
                    "Q3_SAVINGS": "Q3 projected savings",
                    "Q4_SAVINGS": "Q4 projected savings",
                    "ANNUAL_TOTAL": "Total annual projected savings"
                }
            ),
            ReportTemplate(
                name="3-Year ROI Analysis",
                description="Long-term ROI analysis for strategic planning",
                sections=[
                    "Executive Summary",
                    "Current State Analysis",
                    "Year 1 Projections",
                    "Year 2 Projections",
                    "Year 3 Projections",
                    "Cumulative Benefits",
                    "Strategic Recommendations"
                ],
                placeholders={
                    "COMPANY_NAME": "Client company name",
                    "CURRENT_DATE": "Current date",
                    "YEAR1_SAVINGS": "Year 1 projected savings",
                    "YEAR2_SAVINGS": "Year 2 projected savings",
                    "YEAR3_SAVINGS": "Year 3 projected savings",
                    "TOTAL_SAVINGS": "Total 3-year projected savings",
                    "ROI_PERCENTAGE": "3-year ROI percentage"
                }
            )
        ]
        
        # Initialize default projected savings calculations
        self.projected_savings_calculations = [
            ProjectedSavings(
                name="Standard SaaS Waste Recovery",
                description="Projected savings from eliminating redundant SaaS tools",
                baseline_monthly_waste=500.0,
                growth_factors={
                    "month2": 0.1,
                    "month3": 0.15,
                    "month6": 0.25,
                    "month12": 0.4
                },
                confidence_levels={
                    "pilot": 0.6,
                    "month1": 0.7,
                    "month2": 0.8,
                    "month3": 0.85,
                    "month6": 0.9,
                    "month12": 0.95
                }
            ),
            ProjectedSavings(
                name="Performance Optimization",
                description="Projected savings from performance and conversion optimization",
                baseline_monthly_waste=800.0,
                growth_factors={
                    "month2": 0.15,
                    "month3": 0.2,
                    "month6": 0.3,
                    "month12": 0.5
                },
                confidence_levels={
                    "pilot": 0.5,
                    "month1": 0.6,
                    "month2": 0.7,
                    "month3": 0.8,
                    "month6": 0.85,
                    "month12": 0.9
                }
            ),
            ProjectedSavings(
                name="Enterprise Waste Elimination",
                description="Projected savings for larger enterprises with complex tech stacks",
                baseline_monthly_waste=1500.0,
                growth_factors={
                    "month2": 0.12,
                    "month3": 0.18,
                    "month6": 0.28,
                    "month12": 0.45
                },
                confidence_levels={
                    "pilot": 0.55,
                    "month1": 0.65,
                    "month2": 0.75,
                    "month3": 0.8,
                    "month6": 0.85,
                    "month12": 0.9
                }
            )
        ]
        
        # Initialize default competitor benchmarks
        self.competitor_benchmarks = [
            CompetitorBenchmark(
                name="E-commerce Industry Benchmarks",
                description="Performance and conversion benchmarks for e-commerce companies",
                metrics={
                    "performance": {
                        "load_time": 2.5,  # seconds
                        "ttfb": 0.8,       # seconds
                        "fcp": 1.8,        # seconds
                        "lcp": 2.5,        # seconds
                        "cls": 0.1,        # cumulative layout shift
                        "fid": 100         # first input delay (ms)
                    },
                    "conversion": {
                        "bounce_rate": 35.0,       # percent
                        "conversion_rate": 3.2,    # percent
                        "add_to_cart_rate": 8.5,   # percent
                        "cart_abandonment": 70.0,  # percent
                        "checkout_completion": 65.0 # percent
                    }
                }
            ),
            CompetitorBenchmark(
                name="SaaS Industry Benchmarks",
                description="Performance and conversion benchmarks for SaaS companies",
                metrics={
                    "performance": {
                        "load_time": 2.0,  # seconds
                        "ttfb": 0.6,       # seconds
                        "fcp": 1.5,        # seconds
                        "lcp": 2.2,        # seconds
                        "cls": 0.08,       # cumulative layout shift
                        "fid": 80          # first input delay (ms)
                    },
                    "conversion": {
                        "bounce_rate": 40.0,       # percent
                        "conversion_rate": 2.5,    # percent
                        "trial_signup_rate": 15.0, # percent
                        "trial_conversion": 25.0,  # percent
                        "churn_rate": 5.0          # percent
                    }
                }
            ),
            CompetitorBenchmark(
                name="Direct-to-Consumer Benchmarks",
                description="Performance and conversion benchmarks for DTC brands",
                metrics={
                    "performance": {
                        "load_time": 2.2,  # seconds
                        "ttfb": 0.7,       # seconds
                        "fcp": 1.6,        # seconds
                        "lcp": 2.3,        # seconds
                        "cls": 0.09,       # cumulative layout shift
                        "fid": 90          # first input delay (ms)
                    },
                    "conversion": {
                        "bounce_rate": 32.0,       # percent
                        "conversion_rate": 3.5,    # percent
                        "add_to_cart_rate": 9.0,   # percent
                        "cart_abandonment": 68.0,  # percent
                        "repeat_purchase_rate": 35.0 # percent
                    }
                }
            )
        ]
    
    def generate_roi_report(self, prospect: Any, template_name: str = "14-Day Revenue Recovery Pilot") -> Dict[str, Any]:
        """
        Generate an ROI report for a prospect.
        
        Args:
            prospect: A Prospect object
            template_name: Name of the report template to use
            
        Returns:
            Dict with the generated report
        """
        # Find the requested template
        template = next((t for t in self.report_templates if t.name == template_name), self.report_templates[0])
        
        # Create a financial leak detector
        leak_detector = FinancialLeakDetector()
        
        # Detect financial leaks
        leak_results = leak_detector.detect_financial_leaks(prospect)
        
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
        
        # Calculate projected savings
        # Choose appropriate savings calculation based on company size
        if prospect.employee_count and prospect.employee_count > 100:
            savings_calc = self.projected_savings_calculations[2]  # Enterprise
        elif prospect.revenue and prospect.revenue > 2000000:
            savings_calc = self.projected_savings_calculations[1]  # Performance
        else:
            savings_calc = self.projected_savings_calculations[0]  # Standard
        
        projected_savings = savings_calc.calculate(prospect_data)
        
        # Compare against benchmarks
        # Choose appropriate benchmark based on industry
        if prospect.industry and "saas" in prospect.industry.lower():
            benchmark = self.competitor_benchmarks[1]  # SaaS
        elif prospect.industry and any(x in prospect.industry.lower() for x in ["dtc", "direct", "consumer"]):
            benchmark = self.competitor_benchmarks[2]  # DTC
        else:
            benchmark = self.competitor_benchmarks[0]  # E-commerce
        
        benchmark_comparison = benchmark.compare(prospect_data)
        
        # Generate the report
        report = {
            "template": template.to_dict(),
            "prospect": {
                "domain": prospect.domain,
                "company_name": prospect.company_name,
                "industry": prospect.industry,
                "employee_count": prospect.employee_count,
                "revenue": prospect.revenue,
                "country": prospect.country
            },
            "generation_date": datetime.now().isoformat(),
            "financial_leaks": {
                "total_monthly_waste": leak_results["summary"]["total_monthly_waste"],
                "total_annual_waste": leak_results["summary"]["total_annual_waste"],
                "total_monthly_savings": leak_results["summary"]["total_monthly_savings"],
                "total_annual_savings": leak_results["summary"]["total_annual_savings"],
                "roi_percentage": leak_results["summary"]["roi_percentage"],
                "priority_recommendations": leak_results["summary"]["priority_recommendations"][:3]
            },
            "projected_savings": {
                "pilot_savings": projected_savings["monthly_projections"]["pilot"],
                "monthly_projections": projected_savings["monthly_projections"],
                "quarterly_projections": projected_savings["quarterly_projections"],
                "annual_projections": projected_savings["annual_projections"],
                "three_year_projections": projected_savings["three_year_projections"],
                "roi_metrics": projected_savings["roi_metrics"]
            },
            "benchmark_comparison": {
                "benchmark_name": benchmark.name,
                "ahead_count": benchmark_comparison["summary"]["ahead_count"],
                "behind_count": benchmark_comparison["summary"]["behind_count"],
                "average_gap_percentage": benchmark_comparison["summary"]["average_gap_percentage"],
                "performance_comparison": benchmark_comparison["comparisons"].get("performance", {}),
                "conversion_comparison": benchmark_comparison["comparisons"].get("conversion", {})
            },
            "content": self._generate_report_content(template, prospect, leak_results, projected_savings, benchmark_comparison)
        }
        
        return report
    
    def _generate_report_content(self, template: ReportTemplate, prospect: Any, 
                                leak_results: Dict[str, Any], projected_savings: Dict[str, Any], 
                                benchmark_comparison: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate the content for each section of the report.
        
        Args:
            template: Report template
            prospect: Prospect object
            leak_results: Financial leak detection results
            projected_savings: Projected savings calculations
            benchmark_comparison: Benchmark comparison results
            
        Returns:
            Dict with content for each section
        """
        content = {}
        
        # Format currency values
        total_waste = f"${leak_results['summary']['total_annual_waste']:,.2f}"
        pilot_savings = f"${projected_savings['monthly_projections']['pilot']:,.2f}"
        annual_projection = f"${projected_savings['annual_projections']['year1']:,.2f}"
        
        # Get top recommendations
        top_recommendations = leak_results["summary"]["priority_recommendations"][:3]
        recommendations_text = "\n".join([f"- {rec}" for rec in top_recommendations])
        
        # Generate content for each section
        for section in template.sections:
            if section == "Executive Summary":
                content[section] = f"""# Executive Summary for {prospect.company_name}

Our analysis has identified {total_waste} in annual SaaS waste and optimization opportunities for {prospect.company_name}. 
Through our 14-Day Revenue Recovery Pilot, we project immediate savings of {pilot_savings}, with potential annual 
recovery of {annual_projection}.

**Top Opportunities:**
{recommendations_text}

This report outlines our findings and proposed implementation plan to capture these savings.
"""
            
            elif section == "Current State Analysis":
                content[section] = f"""# Current State Analysis

## Company Profile
- **Company:** {prospect.company_name}
- **Industry:** {prospect.industry or "Not specified"}
- **Size:** {prospect.employee_count or "Unknown"} employees
- **Location:** {prospect.country or "Not specified"}

## Technology Stack
{self._format_tech_stack(prospect)}

## Performance vs. Industry Benchmarks
{self._format_benchmark_summary(benchmark_comparison)}
"""
            
            elif section == "Waste Detection Results":
                content[section] = f"""# Waste Detection Results

## Summary
- **Total Monthly Waste:** ${leak_results['summary']['total_monthly_waste']:,.2f}
- **Total Annual Waste:** ${leak_results['summary']['total_annual_waste']:,.2f}
- **ROI Percentage:** {leak_results['summary']['roi_percentage']:.1f}%

## Detected Issues
{self._format_detected_issues(leak_results)}
"""
            
            elif section == "14-Day Pilot Plan":
                content[section] = f"""# 14-Day Revenue Recovery Pilot

## Pilot Overview
The 14-Day Revenue Recovery Pilot is designed to demonstrate immediate ROI by addressing the highest-impact 
opportunities identified in our analysis.

## Pilot Objectives
1. Validate waste detection findings
2. Implement quick-win optimizations
3. Establish baseline metrics for ongoing optimization
4. Demonstrate measurable ROI within 14 days

## Implementation Focus Areas
{self._format_pilot_focus_areas(leak_results)}

## Resource Requirements
- Minimal time commitment: 2-3 hours total over 14 days
- No technical changes required during pilot phase
- Access to analytics and SaaS subscription data
"""
            
            elif section == "Expected Outcomes":
                content[section] = f"""# Expected Outcomes

## Pilot Phase (14 Days)
- **Expected Savings:** {pilot_savings}
- **ROI Percentage:** {projected_savings['roi_metrics']['pilot_roi_percentage']:.1f}%
- **Validation of:** {len(leak_results['summary']['priority_recommendations'][:3])} key optimization opportunities

## First Quarter
- **Projected Savings:** ${projected_savings['quarterly_projections']['q1']:,.2f}
- **Key Milestones:** Implementation of top 3 recommendations, baseline establishment

## First Year
- **Projected Annual Savings:** {annual_projection}
- **ROI Percentage:** {projected_savings['roi_metrics']['first_year_roi_percentage']:.1f}%
- **Cumulative Impact:** Elimination of {len(leak_results.get('redundant_apps', {}).get('patterns_matched', []))} redundant tools, optimization of {len(leak_results.get('performance_conversion', {}).get('analyses', []))} performance issues

## Three-Year Projection
- **Total 3-Year Savings:** ${projected_savings['three_year_projections']['total']:,.2f}
- **Average Annual Savings:** ${projected_savings['three_year_projections']['average_annual']:,.2f}
- **ROI Percentage:** {projected_savings['roi_metrics']['three_year_roi_percentage']:.1f}%
"""
            
            elif section == "Implementation Timeline":
                content[section] = f"""# Implementation Timeline

## Phase 1: 14-Day Pilot (Days 1-14)
- Day 1: Kickoff and data access setup
- Days 2-5: Deep analysis and opportunity validation
- Days 6-10: Quick-win implementation
- Days 11-14: Results measurement and report preparation

## Phase 2: Expansion (Months 1-3)
- Week 3-4: Implementation of top 3 recommendations
- Month 2: Rollout of additional optimizations
- Month 3: Full implementation review and adjustment

## Phase 3: Optimization (Months 4-12)
- Quarterly review and optimization cycles
- Ongoing monitoring and adjustment
- Expansion to additional opportunity areas
"""
            
            elif section == "Next Steps":
                content[section] = f"""# Next Steps

1. **Schedule Pilot Kickoff:** Set up a 30-minute kickoff call to initiate the 14-Day Revenue Recovery Pilot
2. **Provide Access:** Grant limited access to necessary systems for analysis
3. **Review Initial Findings:** Schedule a mid-pilot review (Day 7)
4. **Evaluate Results:** Final review meeting on Day 14 to present results and recommendations

To proceed with the 14-Day Revenue Recovery Pilot, please contact your account representative or reply to this report.
"""
            
            elif "Projections" in section:
                # Handle various projection sections (Q1, Year 1, etc.)
                if section == "Q1 Projections":
                    content[section] = f"""# Q1 Projections

- **Total Q1 Savings:** ${projected_savings['quarterly_projections']['q1']:,.2f}
- **Month 1:** ${projected_savings['monthly_projections']['month1']:,.2f}
- **Month 2:** ${projected_savings['monthly_projections']['month2']:,.2f}
- **Month 3:** ${projected_savings['monthly_projections']['month3']:,.2f}

## Key Focus Areas for Q1
1. Consolidation of redundant tools
2. Performance optimization for critical pages
3. Conversion funnel optimization
"""
                elif section == "Year 1 Projections":
                    content[section] = f"""# Year 1 Projections

- **Total Year 1 Savings:** ${projected_savings['annual_projections']['year1']:,.2f}
- **Q1:** ${projected_savings['quarterly_projections']['q1']:,.2f}
- **Q2:** ${projected_savings['quarterly_projections']['q2']:,.2f}
- **Q3:** ${projected_savings['quarterly_projections']['q3']:,.2f}
- **Q4:** ${projected_savings['quarterly_projections']['q4']:,.2f}

## Year 1 Implementation Roadmap
1. **Q1:** Initial optimizations and quick wins
2. **Q2:** Expanded tool consolidation and performance improvements
3. **Q3:** Advanced conversion optimization
4. **Q4:** Strategic review and planning for Year 2
"""
                else:
                    # Generic projection section
                    content[section] = f"""# {section}

This section contains projections for {section}.

- **Estimated Savings:** ${projected_savings['monthly_projections'].get('month6', 0):,.2f} per month
- **Focus Areas:** Continued optimization and consolidation
- **Expected Outcomes:** Improved efficiency and reduced waste
"""
            
            else:
                # Generic section
                content[section] = f"""# {section}

This section contains information about {section.lower()} for {prospect.company_name}.

## Key Points
- Point 1
- Point 2
- Point 3
"""
        
        return content
    
    def _format_tech_stack(self, prospect: Any) -> str:
        """Format the prospect's technology stack for the report."""
        if not hasattr(prospect, 'technologies') or not prospect.technologies:
            return "No technology data available."
        
        # Group technologies by category
        tech_by_category = {}
        for tech in prospect.technologies:
            if tech.category not in tech_by_category:
                tech_by_category[tech.category] = []
            tech_by_category[tech.category].append(tech.name)
        
        # Format as markdown
        result = []
        for category, tools in tech_by_category.items():
            result.append(f"- **{category.capitalize()}:** {', '.join(tools)}")
        
        return "\n".join(result)
    
    def _format_benchmark_summary(self, benchmark_comparison: Dict[str, Any]) -> str:
        """Format the benchmark comparison summary for the report."""
        summary = benchmark_comparison["summary"]
        
        result = [
            f"Compared to {benchmark_comparison['benchmark_name']}:",
            f"- **Ahead in {summary['ahead_count']} metrics**",
            f"- **Behind in {summary['behind_count']} metrics**",
            f"- **Average gap when behind:** {summary['average_gap_percentage']:.1f}%"
        ]
        
        # Add some specific metrics if available
        if "performance" in benchmark_comparison["comparisons"]:
            perf = benchmark_comparison["comparisons"]["performance"]
            if "metrics" in perf and "load_time" in perf["metrics"]:
                load_time = perf["metrics"]["load_time"]
                result.append(f"- **Page Load Time:** {load_time['prospect_value']:.1f}s vs {load_time['benchmark_value']:.1f}s benchmark")
        
        if "conversion" in benchmark_comparison["comparisons"]:
            conv = benchmark_comparison["comparisons"]["conversion"]
            if "metrics" in conv and "conversion_rate" in conv["metrics"]:
                conv_rate = conv["metrics"]["conversion_rate"]
                result.append(f"- **Conversion Rate:** {conv_rate['prospect_value']:.1f}% vs {conv_rate['benchmark_value']:.1f}% benchmark")
        
        return "\n".join(result)
    
    def _format_detected_issues(self, leak_results: Dict[str, Any]) -> str:
        """Format the detected issues for the report."""
        result = []
        
        # Add redundant apps
        if leak_results.get("redundant_apps", {}).get("redundancies_detected", False):
            result.append("### Redundant Applications")
            for pattern in leak_results["redundant_apps"]["patterns_matched"]:
                result.append(f"- **{pattern['name']}:** {pattern['description']}")
                for category in pattern["redundant_categories"]:
                    tools = pattern["redundant_tools"][category]
                    result.append(f"  * {category.capitalize()}: {', '.join(tools)}")
                result.append(f"  * Monthly Waste: ${pattern['estimated_monthly_waste']:.2f}")
        
        # Add performance vs. conversion issues
        if leak_results.get("performance_conversion", {}).get("issues_detected", False):
            result.append("\n### Performance & Conversion Issues")
            for analysis in leak_results["performance_conversion"]["analyses"]:
                result.append(f"- **{analysis['name']}:** {analysis['description']}")
                for recommendation in analysis["recommendations"]:
                    result.append(f"  * {recommendation}")
        
        if not result:
            return "No significant issues detected."
        
        return "\n".join(result)
    
    def _format_pilot_focus_areas(self, leak_results: Dict[str, Any]) -> str:
        """Format the pilot focus areas for the report."""
        # Get top 3 recommendations
        recommendations = leak_results["summary"]["priority_recommendations"][:3]
        
        result = []
        for i, rec in enumerate(recommendations, 1):
            result.append(f"{i}. **{rec}**")
        
        if not result:
            return "No specific focus areas identified."
        
        return "\n".join(result)
    
    def _generate_mock_performance_data(self, prospect: Any) -> Dict[str, float]:
        """Generate mock performance data for a prospect."""
        # In a real implementation, this would come from actual analytics
        return {
            "load_time": 3.5,
            "ttfb": 1.2,
            "fcp": 2.5,
            "lcp": 3.8,
            "cls": 0.15,
            "fid": 120,
            "checkout_steps": 4,
            "checkout_load_time": 2.5
        }
    
    def _generate_mock_conversion_data(self, prospect: Any) -> Dict[str, float]:
        """Generate mock conversion data for a prospect."""
        # In a real implementation, this would come from actual analytics
        return {
            "bounce_rate": 45.0,
            "conversion_rate": 2.8,
            "add_to_cart_rate": 7.5,
            "cart_abandonment": 75.0,
            "checkout_completion": 55.0
        }
    
    def save_report_to_file(self, report: Dict[str, Any], output_dir: str = "reports") -> str:
        """
        Save a generated report to a file.
        
        Args:
            report: The generated report
            output_dir: Directory to save the report
            
        Returns:
            Path to the saved report file
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        prospect_name = report["prospect"]["company_name"].lower().replace(" ", "_")
        template_name = report["template"]["name"].lower().replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prospect_name}_{template_name}_{timestamp}.md"
        filepath = os.path.join(output_dir, filename)
        
        # Generate markdown content
        markdown_content = f"# {report['template']['name']} for {report['prospect']['company_name']}\n\n"
        markdown_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Add each section
        for section, content in report["content"].items():
            markdown_content += f"{content}\n\n"
        
        # Write to file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        return filepath
    
    def generate_html_report(self, report: Dict[str, Any]) -> str:
        """
        Generate an HTML version of the report.
        
        Args:
            report: The generated report
            
        Returns:
            HTML content of the report
        """
        # This is a simplified HTML generation
        # In a real implementation, you would use a proper template engine
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{report['template']['name']} for {report['prospect']['company_name']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 1000px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
        h2 {{ color: #3498db; margin-top: 30px; }}
        h3 {{ color: #2980b9; }}
        .summary {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .metrics {{ display: flex; flex-wrap: wrap; gap: 20px; margin: 20px 0; }}
        .metric {{ background-color: #e8f4fc; padding: 15px; border-radius: 5px; flex: 1; min-width: 200px; }}
        .metric h4 {{ margin-top: 0; color: #2980b9; }}
        .recommendations {{ background-color: #e8fcf5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .chart {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0; height: 300px; display: flex; align-items: center; justify-content: center; }}
        .chart p {{ color: #777; }}
    </style>
</head>
<body>
    <h1>{report['template']['name']} for {report['prospect']['company_name']}</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="summary">
        <h2>Executive Summary</h2>
        <p>Our analysis has identified ${report['financial_leaks']['total_annual_waste']:,.2f} in annual SaaS waste and optimization opportunities for {report['prospect']['company_name']}.</p>
        <p>Through our 14-Day Revenue Recovery Pilot, we project immediate savings of ${report['projected_savings']['pilot_savings']:,.2f}, with potential annual recovery of ${report['projected_savings']['annual_projections']['year1']:,.2f}.</p>
    </div>
    
    <div class="metrics">
        <div class="metric">
            <h4>Monthly Waste</h4>
            <p>${report['financial_leaks']['total_monthly_waste']:,.2f}</p>
        </div>
        <div class="metric">
            <h4>Annual Waste</h4>
            <p>${report['financial_leaks']['total_annual_waste']:,.2f}</p>
        </div>
        <div class="metric">
            <h4>ROI Percentage</h4>
            <p>{report['financial_leaks']['roi_percentage']:.1f}%</p>
        </div>
        <div class="metric">
            <h4>3-Year Savings</h4>
            <p>${report['projected_savings']['three_year_projections']['total']:,.2f}</p>
        </div>
    </div>
    
    <div class="recommendations">
        <h2>Priority Recommendations</h2>
        <ul>
"""
        
        # Add recommendations
        for rec in report['financial_leaks']['priority_recommendations']:
            html_content += f"            <li>{rec}</li>\n"
        
        html_content += """        </ul>
    </div>
    
    <div class="chart">
        <p>Projected Savings Chart would be displayed here</p>
    </div>
"""
        
        # Add each section
        for section, content in report["content"].items():
            # Convert markdown headers to HTML
            html_section = content.replace("# ", "<h2>").replace("\n## ", "</h2>\n<h3>").replace("\n### ", "</h3>\n<h4>")
            html_section = html_section.replace("</h2>\n", "</h2>").replace("</h3>\n", "</h3>").replace("</h4>\n", "</h4>")
            
            # Convert markdown lists to HTML
            html_section = html_section.replace("\n- ", "\n<li>").replace("\n  * ", "\n<li>")
            html_section = html_section.replace("\n<li>", "\n<ul>\n<li>").replace("\n</ul>", "</li>\n</ul>")
            
            # Add paragraph tags
            paragraphs = html_section.split("\n\n")
            html_paragraphs = []
            for p in paragraphs:
                if not p.startswith("<h") and not p.startswith("<ul") and p.strip():
                    html_paragraphs.append(f"<p>{p}</p>")
                else:
                    html_paragraphs.append(p)
            
            html_section = "\n\n".join(html_paragraphs)
            
            html_content += f"""
    <div class="section">
        {html_section}
    </div>
"""
        
        html_content += """
</body>
</html>
"""
        
        return html_content