#!/usr/bin/env python3
"""
🚀 INTEGRATED ARCO ENGINE
Complete system integration with business intelligence and data enrichment
Production-ready lead generation with strategic intelligence
"""

import sys
import os
import time
import json
import logging
import glob
import hashlib
from dataclasses import asdict
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta

# Add src paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from arco_engine import ARCOEngine, QualifiedLead
from strategic_intelligence_engine import StrategicReportGenerator, MarketIntelligenceEngine
from business_intelligence_scraper import BusinessIntelligenceEngine
from data_enrichment import DataEnrichmentOrchestrator, ProspectTracker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataValidationEngine:
    """Critical data validation and consistency checking"""
    
    def __init__(self):
        self.conflict_thresholds = {
            'employee_size_mismatch': 5,  # Employee count vs size category
            'revenue_size_mismatch': 0.5,  # Revenue estimate vs size
            'tech_stack_conflicts': 2,    # Conflicting tech detection
            'temporal_data_age': 365      # Days before data is stale
        }
    
    def validate_business_profile(self, profile: Dict) -> Dict:
        """Validate business profile for critical inconsistencies"""
        
        validation_result = {
            'is_valid': True,
            'conflicts': [],
            'confidence_score': 100,
            'corrected_data': profile.copy()
        }
        
        # 1. Employee count vs business size consistency
        size_conflict = self._check_size_consistency(profile)
        if size_conflict:
            validation_result['conflicts'].append(size_conflict)
            validation_result['confidence_score'] -= 30
        
        # 2. Tech stack conflict resolution
        tech_conflict = self._resolve_tech_conflicts(profile)
        if tech_conflict:
            validation_result['conflicts'].append(tech_conflict)
            validation_result['corrected_data'].update(tech_conflict['corrections'])
            validation_result['confidence_score'] -= 20
        
        # 3. Market signals temporal consistency
        temporal_conflict = self._check_temporal_consistency(profile)
        if temporal_conflict:
            validation_result['conflicts'].append(temporal_conflict)
            validation_result['confidence_score'] -= 15
        
        # 4. Cross-field sanity checks
        sanity_conflicts = self._perform_sanity_checks(profile)
        for conflict in sanity_conflicts:
            validation_result['conflicts'].append(conflict)
            validation_result['confidence_score'] -= 10
        
        # Mark as invalid if confidence too low
        if validation_result['confidence_score'] < 60:
            validation_result['is_valid'] = False
            logger.warning(f"Profile validation failed: {len(validation_result['conflicts'])} conflicts")
        
        return validation_result
    
    def _check_size_consistency(self, profile: Dict) -> Optional[Dict]:
        """Check employee count vs estimated size consistency"""
        
        employee_count = profile.get('business_intelligence', {}).get('employee_count_estimate', 0)
        estimated_size = profile.get('basic_qualification', {}).get('business', {}).get('estimated_size', '')
        
        if not employee_count or not estimated_size:
            return None
        
        # Define expected ranges
        size_ranges = {
            'micro': (1, 4),
            'small': (5, 24),
            'medium': (25, 99),
            'large': (100, 999)
        }
        
        expected_range = size_ranges.get(estimated_size.lower())
        if not expected_range:
            return None
        
        min_emp, max_emp = expected_range
        
        if not (min_emp <= employee_count <= max_emp):
            return {
                'type': 'size_employee_mismatch',
                'severity': 'HIGH',
                'description': f"Employee count ({employee_count}) doesn't match size category ({estimated_size})",
                'suggested_correction': f"Size should be adjusted based on {employee_count} employees",
                'confidence_impact': -30
            }
        
        return None
    
    def _resolve_tech_conflicts(self, profile: Dict) -> Optional[Dict]:
        """Resolve technology stack conflicts (e.g., WordPress + Squarespace)"""
        
        tech_stack = profile.get('basic_qualification', {}).get('business', {}).get('tech_stack', {})
        cms_list = tech_stack.get('cms', [])
        
        # Check for conflicting CMS
        conflicting_cms = []
        wordpress_variants = ['WordPress', 'WooCommerce']
        hosted_solutions = ['Squarespace', 'Wix', 'Shopify']
        
        has_wordpress = any(cms in wordpress_variants for cms in cms_list)
        has_hosted = any(cms in hosted_solutions for cms in cms_list)
        
        if has_wordpress and has_hosted:
            conflicting_cms = [cms for cms in cms_list if cms in hosted_solutions]
            
            return {
                'type': 'cms_conflict',
                'severity': 'MEDIUM',
                'description': f"Conflicting CMS detected: WordPress + {conflicting_cms}",
                'suggested_investigation': "Check for subdomain migration or DNS artifacts",
                'corrections': {
                    'tech_stack_confidence': 'LOW',
                    'requires_manual_verification': True
                },
                'confidence_impact': -20
            }
        
        return None
    
    def _check_temporal_consistency(self, profile: Dict) -> Optional[Dict]:
        """Check for temporal inconsistencies in market signals"""
        
        market_signals = profile.get('business_intelligence', {}).get('market_signals', [])
        competitive_position = profile.get('enriched_profile', {}).get('competitive_position', '')
        
        # Look for conflicting signals
        growth_indicators = ['hiring', 'expanding', 'award', 'growth']
        decline_indicators = ['laggard', 'struggling', 'outdated']
        
        has_growth = any(signal.lower() in ' '.join(market_signals).lower() for signal in growth_indicators)
        has_decline = competitive_position.lower() in decline_indicators
        
        if has_growth and has_decline:
            return {
                'type': 'temporal_market_conflict',
                'severity': 'MEDIUM',
                'description': f"Growth signals conflict with competitive position ({competitive_position})",
                'suggested_investigation': "Verify data timestamps and current business status",
                'confidence_impact': -15
            }
        
        return None
    
    def _perform_sanity_checks(self, profile: Dict) -> List[Dict]:
        """Perform cross-field sanity checks"""
        
        conflicts = []
        
        # Check WooCommerce relevance for accounting firms
        business_type = profile.get('basic_qualification', {}).get('business', {}).get('business_type', '')
        tech_stack = profile.get('basic_qualification', {}).get('business', {}).get('tech_stack', {})
        ecommerce = tech_stack.get('ecommerce', [])
        
        if 'accounting' in business_type.lower() and 'WooCommerce' in ecommerce:
            conflicts.append({
                'type': 'irrelevant_ecommerce',
                'severity': 'LOW',
                'description': "WooCommerce detected for accounting firm - likely irrelevant or inactive",
                'suggested_action': "Verify if e-commerce is actually used or can be removed",
                'confidence_impact': -10
            })
        
        # Check social engagement vs awards
        social_engagement = profile.get('business_intelligence', {}).get('social_media_presence', {}).get('engagement_estimate', '')
        market_signals = profile.get('business_intelligence', {}).get('market_signals', [])
        
        has_award = any('award' in signal.lower() for signal in market_signals)
        if has_award and social_engagement == 'low':
            conflicts.append({
                'type': 'engagement_award_mismatch',
                'severity': 'LOW', 
                'description': "Recent award but low social engagement - data may be stale",
                'suggested_action': "Refresh social media metrics",
                'confidence_impact': -10
            })
        
        return conflicts

class DeduplicationEngine:
    """Prevents processing of already analyzed prospects"""
    
    def __init__(self, results_dir: str = "results"):
        self.results_dir = results_dir
        self.processed_businesses = self._load_processed_businesses()
    
    def _load_processed_businesses(self) -> Set[str]:
        """Load list of already processed businesses"""
        processed = set()
        
        # Look for existing result files
        if os.path.exists(self.results_dir):
            for file_path in glob.glob(os.path.join(self.results_dir, "*.json")):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        
                    # Extract business identifiers from various formats
                    if 'comprehensive_leads' in data:
                        for lead in data['comprehensive_leads']:
                            processed.add(self._get_business_key(lead))
                    
                    if 'ultra_qualified_leads' in data:
                        for lead in data['ultra_qualified_leads']:
                            processed.add(self._get_business_key(lead))
                            
                except Exception as e:
                    logger.warning(f"Error loading {file_path}: {e}")
        
        logger.info(f"Loaded {len(processed)} previously processed businesses")
        return processed
    
    def _get_business_key(self, business_data: Dict) -> str:
        """Generate unique key for business deduplication"""
        
        # Try different paths to get business info
        business_info = (
            business_data.get('business_profile') or
            business_data.get('basic_qualification', {}).get('business') or
            business_data.get('business_intelligence') or
            business_data
        )
        
        name = business_info.get('company_name') or business_info.get('name', '')
        website = business_info.get('website', '')
        
        # Create normalized key
        key_parts = []
        if name:
            key_parts.append(name.lower().strip())
        if website:
            # Normalize website URL
            website_clean = website.replace('http://', '').replace('https://', '').replace('www.', '').strip('/')
            key_parts.append(website_clean.lower())
        
        if not key_parts:
            return f"unknown_{hash(str(business_data))}"
        
        return hashlib.md5('|'.join(key_parts).encode()).hexdigest()
    
    def is_already_processed(self, business_data: Dict) -> bool:
        """Check if business was already processed"""
        key = self._get_business_key(business_data)
        return key in self.processed_businesses
    
    def mark_as_processed(self, business_data: Dict):
        """Mark business as processed"""
        key = self._get_business_key(business_data)
        self.processed_businesses.add(key)
    
    def get_processed_count(self) -> int:
        """Get count of processed businesses"""
        return len(self.processed_businesses)

class IntegratedARCOEngine:
    """Complete ARCO system with all components integrated"""
    
    def __init__(self):
        logger.info("🚀 Initializing Enhanced ARCO Engine with Data Validation")
        
        # Core engines
        self.lead_generator = ARCOEngine()
        self.intelligence_engine = BusinessIntelligenceEngine()
        self.market_intelligence = MarketIntelligenceEngine()
        self.report_generator = StrategicReportGenerator(self.market_intelligence)
        self.data_enricher = DataEnrichmentOrchestrator()
        
        # NEW: Critical validation and deduplication engines
        self.data_validator = DataValidationEngine()
        self.deduplicator = DeduplicationEngine()
        self.prospect_tracker = ProspectTracker()  # 🔥 PREVENTS API WASTE
        
        # Processing statistics
        self.stats = {
            'businesses_discovered': 0,
            'websites_analyzed': 0,
            'intelligence_gathered': 0,
            'profiles_enriched': 0,
            'qualified_leads': 0,
            'processing_time': 0,
            'duplicates_skipped': 0,            'validation_failures': 0,
            'data_conflicts_resolved': 0,
            'cached_prospects_skipped': 0  # New stat
        }
    
    def generate_comprehensive_leads(self, business_type: str, location: str, 
                                   target_count: int = 5) -> List[Dict]:
        """Generate leads with complete intelligence and enrichment"""
        
        start_time = time.time()
        logger.info(f"🎯 Starting comprehensive lead generation")
        logger.info(f"   Target: {target_count} {business_type} leads in {location}")
        
        # Phase 1: Discover businesses
        logger.info("📍 Phase 1: Business Discovery")
        businesses = self.lead_generator.discover_businesses(business_type, location, target_count * 2)
        self.stats['businesses_discovered'] = len(businesses)
        logger.info(f"   Discovered {len(businesses)} businesses")
        
        comprehensive_leads = []
        
        for i, business in enumerate(businesses):
            if len(comprehensive_leads) >= target_count:
                break
                
            logger.info(f"🔍 Processing {i+1}/{len(businesses)}: {business.get('name', 'Unknown')}")
            try:
                # 🔥 STEP 1: Check if prospect was analyzed recently (SAVES API CALLS!)
                if self.prospect_tracker.was_analyzed_recently(business):
                    previous_analysis = self.prospect_tracker.get_previous_analysis(business)
                    logger.info(f"   🔄 CACHED PROSPECT - analyzed on {previous_analysis['analyzed_at'][:10]} - SKIPPING to save API calls")
                    self.stats['cached_prospects_skipped'] += 1
                    continue
                
                # STEP 2: Check for duplicates in current session
                if self.deduplicator.is_already_processed(business):
                    logger.info(f"   🔁 DUPLICATE DETECTED - skipping {business.get('name', 'Unknown')}")
                    self.stats['duplicates_skipped'] += 1
                    continue
                
                # Check if business has website
                website = business.get('website')
                if not website:
                    logger.info(f"   ⚠️  No website - skipping")
                    continue
                
                # Phase 2: Basic qualification
                logger.info(f"   📊 Phase 2: Basic Qualification")
                qualified_lead = self.lead_generator.qualify_lead(business)
                if not qualified_lead:
                    logger.info(f"   ❌ Failed qualification")
                    continue
                
                self.stats['qualified_leads'] += 1
                
                # Phase 3: Business intelligence gathering
                logger.info(f"   🔍 Phase 3: Intelligence Gathering")
                intelligence = self.intelligence_engine.gather_intelligence(
                    qualified_lead.business.name,
                    qualified_lead.business.website,
                    qualified_lead.business.business_type,
                    location
                )
                self.stats['intelligence_gathered'] += 1
                
                # Phase 4: Website analysis (enhanced)
                logger.info(f"   🌐 Phase 4: Website Analysis")
                website_analysis = self.lead_generator.analyze_website(website)
                self.stats['websites_analyzed'] += 1
                
                # Phase 5: Performance analysis
                logger.info(f"   ⚡ Phase 5: Performance Analysis")
                performance_data = self.lead_generator.get_performance_data(website)
                
                # Phase 6: Data enrichment
                logger.info(f"   📈 Phase 6: Profile Enrichment")
                basic_profile = {
                    'name': qualified_lead.business.name,
                    'website': qualified_lead.business.website,                    'phone': qualified_lead.business.phone,
                    'address': qualified_lead.business.address,
                    'business_type': qualified_lead.business.business_type
                }
                
                # Phase 6: Data enrichment
                logger.info(f"   📈 Phase 6: Profile Enrichment")
                enriched_profile = self.data_enricher.enrich_business_profile(
                    basic_profile,
                    website_analysis if website_analysis.get('status') == 'success' else {},
                    performance_data,
                    asdict(intelligence) if intelligence else {}
                )
                self.stats['profiles_enriched'] += 1
                
                # CRITICAL: Create complete profile for validation
                complete_profile = {
                    'basic_qualification': {
                        'business': {
                            'name': qualified_lead.business.name,
                            'estimated_size': qualified_lead.business.estimated_size,
                            'estimated_revenue': qualified_lead.business.estimated_revenue,
                            'tech_stack': qualified_lead.business.tech_stack,
                            'business_type': qualified_lead.business.business_type
                        }
                    },
                    'business_intelligence': asdict(intelligence) if intelligence else {},
                    'enriched_profile': asdict(enriched_profile) if hasattr(enriched_profile, '__dict__') else enriched_profile
                }
                
                # CRITICAL: Data validation with conflict resolution
                logger.info(f"   🔍 Phase 6.5: Data Validation & Conflict Resolution")
                validation_result = self.data_validator.validate_business_profile(complete_profile)
                
                if not validation_result['is_valid']:
                    logger.warning(f"   ⚠️  VALIDATION FAILED for {qualified_lead.business.name}")
                    logger.warning(f"   Conflicts: {[c['type'] for c in validation_result['conflicts']]}")
                    self.stats['validation_failures'] += 1
                    continue
                
                if validation_result['conflicts']:
                    logger.info(f"   🔧 Data conflicts resolved: {len(validation_result['conflicts'])}")
                    self.stats['data_conflicts_resolved'] += len(validation_result['conflicts'])
                    # Use corrected data
                    complete_profile.update(validation_result['corrected_data'])
                
                # Mark as processed AFTER successful validation
                self.deduplicator.mark_as_processed(business)
                
                # Phase 7: Strategic intelligence reports
                logger.info(f"   🎯 Phase 7: Strategic Intelligence")
                
                # Generate all tier reports
                reports = {}
                
                # Tier 1: Diagnostic Teaser (always generated)
                reports['tier_1'] = self.report_generator.generate_diagnostic_teaser(
                    website_analysis if website_analysis.get('status') == 'success' else {},
                    performance_data or {}
                )
                
                # Get qualification score safely (handle both dict and object)
                qualification_score = getattr(enriched_profile, 'qualification_score', None) or enriched_profile.get('qualification_score', 0)
                estimated_size = getattr(enriched_profile, 'estimated_size', None) or enriched_profile.get('estimated_size', 'unknown')
                
                # Tier 2: Strategic Brief (for qualified leads)
                if qualification_score > 50:
                    reports['tier_2'] = self.report_generator.generate_strategic_brief(
                        website_analysis if website_analysis.get('status') == 'success' else {},
                        performance_data or {},
                        business_type,
                        location
                    )
                
                # Tier 3: Executive Report (for highly qualified leads)
                if qualification_score > 75:
                    reports['tier_3'] = self.report_generator.generate_executive_report(
                        website_analysis if website_analysis.get('status') == 'success' else {},
                        performance_data or {},
                        business_type,
                        location,
                        estimated_size
                    )
                
                # Phase 8: Compile comprehensive lead profile
                comprehensive_lead = {
                    'lead_id': f"ARCO_{datetime.now().strftime('%Y%m%d')}_{i+1:03d}",
                    'generation_timestamp': datetime.now().isoformat(),
                    
                    # Basic lead data
                    'basic_qualification': asdict(qualified_lead),
                    
                    # Enhanced intelligence
                    'business_intelligence': asdict(intelligence) if intelligence else {},
                    'website_analysis': website_analysis,
                    'performance_analysis': performance_data,
                    
                    # Enriched profile
                    'enriched_profile': asdict(enriched_profile),
                    
                    # Strategic reports
                    'strategic_reports': reports,
                    
                    # Summary metrics (handle both dict and object safely)
                    'summary': {
                        'qualification_score': getattr(enriched_profile, 'qualification_score', None) or enriched_profile.get('qualification_score', 0),
                        'digital_maturity_score': getattr(enriched_profile, 'digital_maturity_score', None) or enriched_profile.get('digital_maturity_score', 0),
                        'investment_capacity': getattr(enriched_profile, 'investment_capacity', None) or enriched_profile.get('investment_capacity', 'unknown'),
                        'decision_timeline': getattr(enriched_profile, 'decision_timeline', None) or enriched_profile.get('decision_timeline', 'unknown'),
                        'competitive_position': getattr(enriched_profile, 'competitive_position', None) or enriched_profile.get('competitive_position', 'unknown'),
                        'estimated_value_range': qualified_lead.total_value_range,
                        'likelihood_to_close': qualified_lead.likelihood_to_close,
                        'reports_available': list(reports.keys())
                    }
                }
                
                comprehensive_leads.append(comprehensive_lead)
                
                logger.info(f"   ✅ Complete: Qualification {qualification_score}/100, "
                          f"Maturity {getattr(enriched_profile, 'digital_maturity_score', None) or enriched_profile.get('digital_maturity_score', 0)}/100, "
                          f"Reports: {len(reports)}")
                
                # Mark as processed
                self.deduplicator.mark_as_processed(business)
                
                # Rate limiting for ethical processing
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"   ❌ Error processing {business.get('name')}: {e}")
                continue
        
        # Calculate final statistics
        end_time = time.time()
        self.stats['processing_time'] = end_time - start_time
        
        logger.info(f"🎯 Lead Generation Complete!")
        logger.info(f"   📊 Statistics:")
        logger.info(f"      • Businesses Discovered: {self.stats['businesses_discovered']}")
        logger.info(f"      • Websites Analyzed: {self.stats['websites_analyzed']}")
        logger.info(f"      • Intelligence Gathered: {self.stats['intelligence_gathered']}")
        logger.info(f"      • Profiles Enriched: {self.stats['profiles_enriched']}")
        logger.info(f"      • Qualified Leads: {len(comprehensive_leads)}")
        logger.info(f"      • Processing Time: {self.stats['processing_time']:.1f} seconds")
        logger.info(f"      • Average per Lead: {self.stats['processing_time']/max(len(comprehensive_leads), 1):.1f} seconds")
        
        return comprehensive_leads
    
    def export_comprehensive_results(self, leads: List[Dict], filename: str = None) -> str:
        """Export comprehensive results with metadata"""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comprehensive_leads_{timestamp}.json"
        
        # Prepare export data
        export_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'engine_version': 'Integrated ARCO v2.0',
                'total_leads': len(leads),
                'processing_statistics': self.stats,
                'data_sources': [
                    'Google Places API',
                    'Google PageSpeed Insights API',
                    'Custom Tech Detection',
                    'Business Intelligence Scraping',
                    'Strategic Market Analysis'
                ],
                'report_tiers_included': ['Tier 1 (Diagnostic)', 'Tier 2 (Strategic)', 'Tier 3 (Executive)']
            },
            'executive_summary': self._generate_executive_summary(leads),
            'lead_segments': self._segment_leads(leads),
            'comprehensive_leads': leads
        }
        
        # Export to results directory
        export_path = os.path.join('results', filename)
        os.makedirs('results', exist_ok=True)
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Comprehensive results exported to {export_path}")
        return export_path
    
    def _generate_executive_summary(self, leads: List[Dict]) -> Dict:
        """Generate executive summary of lead generation results"""
        
        if not leads:
            return {'total_leads': 0, 'message': 'No qualified leads generated'}
        
        # Calculate averages and distributions
        qualification_scores = [lead['summary']['qualification_score'] for lead in leads]
        maturity_scores = [lead['summary']['digital_maturity_score'] for lead in leads]
        
        investment_capacities = [lead['summary']['investment_capacity'] for lead in leads]
        capacity_distribution = {
            'high': sum(1 for c in investment_capacities if c == 'high'),
            'medium': sum(1 for c in investment_capacities if c == 'medium'),
            'low': sum(1 for c in investment_capacities if c == 'low')
        }
        
        competitive_positions = [lead['summary']['competitive_position'] for lead in leads]
        position_distribution = {}
        for position in competitive_positions:
            position_distribution[position] = position_distribution.get(position, 0) + 1
        
        return {
            'total_leads': len(leads),
            'average_qualification_score': sum(qualification_scores) / len(qualification_scores),
            'average_maturity_score': sum(maturity_scores) / len(maturity_scores),
            'investment_capacity_distribution': capacity_distribution,
            'competitive_position_distribution': position_distribution,
            'high_priority_leads': sum(1 for score in qualification_scores if score > 75),
            'medium_priority_leads': sum(1 for score in qualification_scores if 50 <= score <= 75),
            'tier_3_eligible_leads': sum(1 for lead in leads if 'tier_3' in lead['strategic_reports']),
            'processing_efficiency': f"{self.stats['processing_time']/len(leads):.1f} seconds per lead"
        }
    
    def _segment_leads(self, leads: List[Dict]) -> Dict:
        """Segment leads by various criteria for targeted approach"""
        
        segments = {
            'immediate_opportunity': [],  # High qualification + high investment capacity
            'strategic_development': [],  # Medium qualification + growth potential
            'long_term_nurture': [],     # Lower qualification but good fundamentals
            'competitive_rescue': []      # Vulnerable competitive position
        }
        
        for lead in leads:
            summary = lead['summary']
            
            # Immediate opportunity
            if (summary['qualification_score'] > 75 and 
                summary['investment_capacity'] == 'high'):
                segments['immediate_opportunity'].append(lead['lead_id'])
            
            # Strategic development
            elif (50 <= summary['qualification_score'] <= 75 and
                  summary['investment_capacity'] in ['medium', 'high']):
                segments['strategic_development'].append(lead['lead_id'])
            
            # Competitive rescue
            elif summary['competitive_position'] in ['vulnerable', 'laggard']:
                segments['competitive_rescue'].append(lead['lead_id'])
            
            # Long-term nurture
            else:
                segments['long_term_nurture'].append(lead['lead_id'])
        
        return segments

# Demo function
def demo_integrated_system():
    """Demo the complete integrated ARCO system"""
    print("🚀" + "="*60)
    print("   INTEGRATED ARCO SYSTEM DEMO")
    print("="*63)
    
    engine = IntegratedARCOEngine()
    
    # Generate comprehensive leads
    leads = engine.generate_comprehensive_leads(
        business_type="restaurant",
        location="Rio de Janeiro, Brazil",
        target_count=2  # Small number for demo
    )
    
    if leads:
        # Export results
        export_path = engine.export_comprehensive_results(leads)
        
        # Display summary
        print(f"\n📊 COMPREHENSIVE RESULTS:")
        for i, lead in enumerate(leads, 1):
            summary = lead['summary']
            print(f"\n🏢 Lead #{i}: {lead['basic_qualification']['business']['name']}")
            print(f"   • Qualification Score: {summary['qualification_score']}/100")
            print(f"   • Digital Maturity: {summary['digital_maturity_score']}/100")
            print(f"   • Investment Capacity: {summary['investment_capacity']}")
            print(f"   • Decision Timeline: {summary['decision_timeline']}")
            print(f"   • Value Range: {summary['estimated_value_range']}")
            print(f"   • Reports Available: {', '.join(summary['reports_available'])}")
        
        print(f"\n📄 Results exported to: {export_path}")
    
    print("\n" + "="*63)
    print("   INTEGRATED ARCO DEMO COMPLETE")
    print("="*63)

if __name__ == "__main__":
    demo_integrated_system()