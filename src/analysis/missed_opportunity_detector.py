"""
📊 MISSED OPPORTUNITY DETECTOR
Simple detector for missed opportunities in lead qualification
"""

from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class MissedOpportunityDetector:
    """Detects missed opportunities in lead analysis"""
    
    def __init__(self):
        self.opportunity_patterns = {
            'technology': [
                'Performance optimization needed',
                'Mobile experience issues', 
                'SEO improvement potential'
            ],
            'ecommerce': [
                'Conversion rate optimization',
                'Cart abandonment reduction',
                'Product page optimization'
            ],
            'saas': [
                'Customer acquisition cost reduction',
                'Churn rate improvement',
                'Onboarding optimization'
            ]
        }
    
    def detect_missed_opportunities(self, website: str, industry: str) -> List[Dict]:
        """Detect potential missed opportunities for a website"""
        try:
            opportunities = []
            
            # Get industry-specific patterns
            patterns = self.opportunity_patterns.get(industry.lower(), 
                                                   self.opportunity_patterns['technology'])
            
            # Create basic opportunities based on industry
            for i, pattern in enumerate(patterns[:2]):  # Limit to 2 opportunities
                opportunities.append({
                    'type': 'optimization_opportunity',
                    'description': pattern,
                    'potential_impact': 'medium',
                    'estimated_value': 200 + (i * 100)  # $200-$300 range
                })
            
            logger.debug(f"Detected {len(opportunities)} opportunities for {website}")
            return opportunities
            
        except Exception as e:
            logger.warning(f"Error detecting opportunities: {e}")
            return []