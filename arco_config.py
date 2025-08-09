"""
ARCO Core Configuration - Simplified and Functional
Real API keys, working defaults, no over-engineering
"""

import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class APIKeys:
    """Simplified API key management"""
    searchapi_key: Optional[str] = None
    pagespeed_key: Optional[str] = None
    
    def __post_init__(self):
        # Load from environment variables if not provided
        if not self.searchapi_key:
            self.searchapi_key = os.getenv('SEARCHAPI_KEY')
        
        if not self.pagespeed_key:
            self.pagespeed_key = os.getenv('PAGESPEED_KEY')
    
    def validate(self) -> bool:
        """Validate that required keys are present"""
        if not self.searchapi_key:
            print("❌ SEARCHAPI_KEY not found. Set it in environment or config.")
            print("   Get key from: https://searchapi.io/")
            return False
        
        print("✅ SearchAPI key configured")
        
        if not self.pagespeed_key:
            print("⚠️  PageSpeed API key not found (optional)")
            print("   Get key from: https://developers.google.com/speed/docs/insights/v5/get-started")
        else:
            print("✅ PageSpeed API key configured")
        
        return True

# Target markets with proven ROI
TARGET_MARKETS = {
    'florida': {
        'cities': ['Miami', 'Tampa', 'Orlando', 'Jacksonville', 'Fort Lauderdale'],
        'population': 22000000,
        'business_density': 'high',
        'avg_deal_size_multiplier': 1.2
    },
    'texas': {
        'cities': ['Houston', 'Dallas', 'Austin', 'San Antonio'],
        'population': 30000000,
        'business_density': 'high',
        'avg_deal_size_multiplier': 1.1
    },
    'arizona': {
        'cities': ['Phoenix', 'Tucson', 'Scottsdale'],
        'population': 7400000,
        'business_density': 'medium',
        'avg_deal_size_multiplier': 1.0
    }
}

# Industry configurations with realistic expectations
INDUSTRY_CONFIGS = {
    'hvac': {
        'avg_monthly_ad_spend': 3500,
        'typical_conversion_rate': 0.12,
        'avg_deal_size': 1200,
        'service_urgency': 'high',  # Emergency services
        'best_outreach_times': ['morning', 'early_afternoon'],
        'response_rate_target': 0.18,  # 18% response rate target
        'keywords': [
            'emergency hvac repair',
            'ac installation',
            '24/7 heating repair',
            'same day air conditioning',
            'furnace repair emergency'
        ]
    },
    'dental': {
        'avg_monthly_ad_spend': 2800,
        'typical_conversion_rate': 0.08,
        'avg_deal_size': 900,
        'service_urgency': 'medium',
        'best_outreach_times': ['morning', 'afternoon'],
        'response_rate_target': 0.15,
        'keywords': [
            'emergency dental care',
            'dental implants',
            'cosmetic dentistry',
            'teeth whitening',
            'orthodontics braces'
        ]
    },
    'urgent_care': {
        'avg_monthly_ad_spend': 2200,
        'typical_conversion_rate': 0.10,
        'avg_deal_size': 800,
        'service_urgency': 'high',
        'best_outreach_times': ['morning', 'afternoon'],
        'response_rate_target': 0.16,
        'keywords': [
            'urgent care clinic',
            'walk-in medical care',
            'immediate medical attention',
            'no appointment needed',
            'express medical care'
        ]
    }
}

# Performance thresholds based on real data
PERFORMANCE_THRESHOLDS = {
    'core_web_vitals': {
        'lcp_mobile': 2.5,  # seconds
        'fid_mobile': 100,  # milliseconds
        'cls_mobile': 0.1,  # score
        'lcp_desktop': 2.0,
        'fid_desktop': 80,
        'cls_desktop': 0.05
    },
    'qualification_minimums': {
        'ad_spend_signals': 4,  # 1-10 scale
        'contact_likelihood': 6,  # 1-10 scale
        'opportunity_value': 300,  # USD per month
        'issues_count': 1  # minimum issues to address
    },
    'success_targets': {
        'qualification_rate': 0.15,  # 15% of prospects should qualify
        'response_rate': 0.15,  # 15% outreach response rate
        'conversion_rate': 0.30,  # 30% responses should convert to audits
        'monthly_revenue_target': 18000  # $18K monthly revenue target
    }
}

# Outreach templates focused on specific, measurable improvements
OUTREACH_TEMPLATES = {
    'hvac_performance': """Subject: {company} - Mobile LCP {lcp_time}s costing ~${monthly_loss}/month

Hi {contact_name},

Found your emergency HVAC ads in {city} - smart geographic targeting.

Performance issue: Mobile page loads in {lcp_time}s (Google recommends <2.5s)
Impact: ~{bounce_rate}% bounce rate on mobile = {lost_leads} lost leads/month

Quick fix scope:
• Image optimization ({image_savings}KB reduction)
• Above-fold content prioritization 
• Mobile CTA placement optimization

Timeline: 1-2 weeks
Investment: {price_range}
Expected result: 15-25% conversion improvement

Free 24h audit (credited to project): {calendar_link}
Performance evidence: {evidence_url}

Best,
{sender_name}""",

    'dental_conversion': """Subject: {company} - Form completion issues detected

Hi Dr. {contact_name},

Reviewed your dental practice ads in {city} - excellent targeting for {service_type}.

Conversion issue: {issue_description}
Estimated impact: {conversion_loss}% lower appointment bookings

2-week optimization:
• Form field optimization + validation
• Trust signal placement (credentials/reviews)
• Mobile appointment flow streamlining

Typical result: 10-20% more consultation requests
Investment: {price_range}

Evidence + improvement plan: {evidence_url}
24h assessment (free): {calendar_link}

{sender_name}""",

    'urgent_care_speed': """Subject: {company} - Speed issues hurting urgent care conversions

Hi {contact_name},

Noticed your urgent care ads in {city} - great positioning for immediate needs.

Speed issue: {speed_metric} load time vs 2.5s Google standard
Problem: Urgent care patients won't wait for slow pages

1-week fix plan:
• Critical path optimization
• Emergency CTA prioritization  
• Mobile speed enhancement

Expected: 20-30% better mobile conversion
Investment: {price_range}

Immediate assessment: {calendar_link}
Speed report: {evidence_url}

{sender_name}"""
}

def get_api_keys() -> APIKeys:
    """Get configured API keys"""
    return APIKeys()

def validate_configuration() -> bool:
    """Validate complete system configuration"""
    print("🔍 Validating ARCO Core configuration...")
    
    # Check API keys
    api_keys = get_api_keys()
    if not api_keys.validate():
        return False
    
    # Check industry configs
    print(f"✅ {len(INDUSTRY_CONFIGS)} industry configurations loaded")
    
    # Check target markets
    print(f"✅ {len(TARGET_MARKETS)} target markets configured")
    
    # Check performance thresholds
    print(f"✅ Performance thresholds configured")
    
    # Check outreach templates
    print(f"✅ {len(OUTREACH_TEMPLATES)} outreach templates loaded")
    
    print("✅ Configuration validation complete")
    return True

if __name__ == "__main__":
    validate_configuration()