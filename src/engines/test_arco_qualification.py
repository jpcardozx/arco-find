#!/usr/bin/env python3
"""
🧪 Test ARCO Qualification Logic
Direct test of ARCO qualification without hybrid engine import issues
"""

import sys
import os
import logging
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Mock company data similar to what hybrid engine would provide
test_companies = [
    {
        'company_name': 'Test Dental Clinic Berlin',
        'page_id': 'dental_de_1000',
        'website_url': 'https://facebook.com/dental_de_1000',
        'discovery_source': 'meta_ads_intelligent_fallback',
        'industry': 'dental',
        'country': 'DE',
        'city': 'Berlin',
        'estimated_monthly_spend': 2500,
        'platforms_active': ['Facebook', 'Instagram'],
        'ad_active_since': (datetime.now() - timedelta(days=45)).isoformat(),
        'last_seen': datetime.now().isoformat(),
        'impressions_range': {
            'lower_bound': 75000,  # 2500 * 30
            'upper_bound': 150000  # 2500 * 60
        },
        'spend_range': {
            'lower_bound': 2000,   # 2500 * 0.8
            'upper_bound': 3000    # 2500 * 1.2
        }
    },
    {
        'company_name': 'Test Aesthetic Clinic Istanbul',
        'page_id': 'aesthetic_tr_2000',
        'website_url': 'https://facebook.com/aesthetic_tr_2000',
        'discovery_source': 'meta_ads_intelligent_fallback',
        'industry': 'aesthetic',
        'country': 'TR',
        'city': 'Istanbul',
        'estimated_monthly_spend': 4500,
        'platforms_active': ['Facebook', 'Instagram'],
        'ad_active_since': (datetime.now() - timedelta(days=60)).isoformat(),
        'last_seen': datetime.now().isoformat(),
        'impressions_range': {
            'lower_bound': 112500,  # 4500 * 25
            'upper_bound': 225000   # 4500 * 50
        },
        'spend_range': {
            'lower_bound': 3600,    # 4500 * 0.8
            'upper_bound': 5400     # 4500 * 1.2
        }
    }
]

# ICP configurations
dental_icp = {
    'discovery_method': 'meta_ads',
    'target_countries': ['DE', 'NL'],
    'keywords': ['zahnarzt', 'tandarts', 'dental'],
    'min_monthly_spend': 800,
    'target_platforms': ['Facebook', 'Instagram'],
    'qualification_signals': [
        {'signal': 'ad_frequency_analysis', 'weight': 30},
        {'signal': 'audience_targeting_precision', 'weight': 25},
        {'signal': 'creative_performance_gap', 'weight': 20},
        {'signal': 'cross_platform_waste', 'weight': 15},
        {'signal': 'competitor_overlap', 'weight': 10}
    ],
    'qualification_threshold': 10
}

aesthetic_icp = {
    'discovery_method': 'meta_ads',
    'target_countries': ['TR', 'ES'],
    'keywords': ['estetik', 'estética', 'güzellik', 'belleza'],
    'min_monthly_spend': 1000,
    'target_platforms': ['Facebook', 'Instagram'],
    'qualification_signals': [
        {'signal': 'ad_frequency_analysis', 'weight': 30},
        {'signal': 'audience_targeting_precision', 'weight': 25},
        {'signal': 'creative_performance_gap', 'weight': 20},
        {'signal': 'cross_platform_waste', 'weight': 15},
        {'signal': 'competitor_overlap', 'weight': 10}
    ],
    'qualification_threshold': 10
}

def analyze_ad_frequency(company):
    """Analisar frequência de anúncios"""
    impressions = company.get('impressions_range', {})
    if impressions:
        avg_impressions = (impressions.get('lower_bound', 0) + impressions.get('upper_bound', 0)) / 2
        spend = company.get('estimated_monthly_spend', 1)
        frequency_ratio = avg_impressions / spend if spend > 0 else 0
        score = min(int(frequency_ratio / 10), 25)
        logger.info(f"📊 Ad Frequency: avg_impressions={avg_impressions}, spend={spend}, ratio={frequency_ratio:.1f}, score={score}")
        return score
    return 15

def analyze_audience_targeting(company):
    """Analisar precisão do targeting"""
    spend = company.get('estimated_monthly_spend', 1000)
    if spend > 3000:
        score = 25
    elif spend > 2000:
        score = 20
    else:
        score = 10
    logger.info(f"🎯 Audience Targeting: spend={spend}, score={score}")
    return score

def analyze_creative_performance(company):
    """Analisar performance dos criativos"""
    ad_start = company.get('ad_active_since', '')
    if ad_start:
        try:
            start_date = datetime.fromisoformat(ad_start.replace('Z', '+00:00'))
            days_active = (datetime.now() - start_date.replace(tzinfo=None)).days
            if days_active > 60:
                score = 20
            elif days_active > 30:
                score = 15
            else:
                score = 10
        except:
            score = 10
    else:
        score = 10
    logger.info(f"🎨 Creative Performance: days_active={days_active if 'days_active' in locals() else 'N/A'}, score={score}")
    return score

def analyze_platform_efficiency(company):
    """Analisar eficiência cross-platform"""
    platforms = company.get('platforms_active', [])
    score = 15 if len(platforms) > 1 else 5
    logger.info(f"📱 Platform Efficiency: platforms={platforms}, score={score}")
    return score

def analyze_competitor_overlap(company):
    """Analisar sobreposição com competidores"""
    spend = company.get('estimated_monthly_spend', 1000)
    industry = company.get('industry', '')
    
    if industry == 'aesthetic' and spend > 2500:
        score = 12
    elif industry == 'dental' and spend > 2000:
        score = 10
    else:
        score = 5
    logger.info(f"🏆 Competitor Overlap: industry={industry}, spend={spend}, score={score}")
    return score

def test_arco_qualification(company, icp_config):
    """Test ARCO qualification logic"""
    logger.info(f"\n🔍 Testing qualification for: {company['company_name']}")
    
    # Check minimum spend threshold
    spend = company['estimated_monthly_spend']
    min_spend = icp_config['min_monthly_spend']
    logger.info(f"💰 Spend check: {spend} >= {min_spend}")
    
    if spend < min_spend:
        logger.info(f"❌ Failed spend threshold: {spend} < {min_spend}")
        return None
    
    # Calculate ARCO score
    qualification_score = 0
    signals_detected = []
    
    # Signal 1: Ad Frequency Analysis
    frequency_score = analyze_ad_frequency(company)
    weighted_frequency = frequency_score * 0.30
    qualification_score += weighted_frequency
    
    if frequency_score > 15:
        signals_detected.append({
            'signal': 'ad_frequency_analysis',
            'score': frequency_score
        })
    
    # Signal 2: Audience Targeting Precision
    targeting_score = analyze_audience_targeting(company)
    weighted_targeting = targeting_score * 0.25
    qualification_score += weighted_targeting
    
    if targeting_score > 20:
        signals_detected.append({
            'signal': 'audience_targeting_precision',
            'score': targeting_score
        })
    
    # Signal 3: Creative Performance Gap
    creative_score = analyze_creative_performance(company)
    weighted_creative = creative_score * 0.20
    qualification_score += weighted_creative
    
    if creative_score > 15:
        signals_detected.append({
            'signal': 'creative_performance_gap',
            'score': creative_score
        })
    
    # Signal 4: Cross-Platform Waste
    platform_score = analyze_platform_efficiency(company)
    weighted_platform = platform_score * 0.15
    qualification_score += weighted_platform
    
    if platform_score > 10:
        signals_detected.append({
            'signal': 'cross_platform_waste',
            'score': platform_score
        })
    
    # Signal 5: Competitor Overlap
    competitor_score = analyze_competitor_overlap(company)
    weighted_competitor = competitor_score * 0.10
    qualification_score += weighted_competitor
    
    if competitor_score > 8:
        signals_detected.append({
            'signal': 'competitor_overlap',
            'score': competitor_score
        })
    
    # Final qualification check
    threshold = icp_config['qualification_threshold']
    logger.info(f"🎯 Final Score: {qualification_score:.1f} vs threshold {threshold}")
    logger.info(f"📊 Signals detected: {len(signals_detected)}")
    
    if qualification_score >= threshold:
        logger.info(f"✅ QUALIFIED! {company['company_name']} passed with score {qualification_score:.1f}")
        return {
            'company_name': company['company_name'],
            'qualification_score': int(qualification_score),
            'signals_detected': len(signals_detected)
        }
    else:
        logger.info(f"❌ Not qualified: {qualification_score:.1f} < {threshold}")
        return None

def main():
    """Run ARCO qualification tests"""
    print("🧪 Testing ARCO Qualification Logic")
    print("=" * 50)
    
    # Test dental company
    dental_result = test_arco_qualification(test_companies[0], dental_icp)
    
    # Test aesthetic company  
    aesthetic_result = test_arco_qualification(test_companies[1], aesthetic_icp)
    
    print("\n🎯 Results Summary:")
    print(f"Dental qualification: {'✅ PASSED' if dental_result else '❌ FAILED'}")
    print(f"Aesthetic qualification: {'✅ PASSED' if aesthetic_result else '❌ FAILED'}")
    
    if dental_result:
        print(f"  - Dental score: {dental_result['qualification_score']}")
    if aesthetic_result:
        print(f"  - Aesthetic score: {aesthetic_result['qualification_score']}")

if __name__ == "__main__":
    main()
