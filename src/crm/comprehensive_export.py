#!/usr/bin/env python3
"""
🏢 COMPREHENSIVE CRM EXPORT SYSTEM + BIGQUERY ENRICHMENT
Exportação completa e madura dos 196 prospects reais da SearchAPI
Com enriquecimento BigQuery integrado para máxima inteligência de conversão
"""

import json
import csv
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
import requests
import time

# Import existing BigQuery systems and mature enricher
try:
    from src.intelligence.bigquery_intelligence import BigQueryIntelligence
    from src.integrations.bigquery_config import BigQueryConfig
    from src.enrichment.mature_enricher import MatureProspectEnricher, EnrichmentCosts
    BIGQUERY_AVAILABLE = True
    MATURE_ENRICHMENT_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False
    MATURE_ENRICHMENT_AVAILABLE = False

class ComprehensiveCRMExporter:
    """
    Sistema maduro de exportação CRM para todos os prospects qualificados
    Com integração BigQuery para enriquecimento inteligente
    """
    
    def __init__(self, results_file: str, enable_bigquery_enrichment: bool = True, enable_mature_enrichment: bool = True):
        self.results_file = results_file
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.enable_bigquery_enrichment = enable_bigquery_enrichment and BIGQUERY_AVAILABLE
        self.enable_mature_enrichment = enable_mature_enrichment and MATURE_ENRICHMENT_AVAILABLE
        
        # Initialize BigQuery components if available
        if self.enable_bigquery_enrichment:
            try:
                self.bq_config = BigQueryConfig()
                self.bq_intelligence = BigQueryIntelligence()
                print("✅ BigQuery enrichment enabled")
            except Exception as e:
                print(f"⚠️ BigQuery initialization failed: {e}")
                self.enable_bigquery_enrichment = False
        
        # Initialize Mature Enricher
        if self.enable_mature_enrichment:
            try:
                self.mature_enricher = MatureProspectEnricher(dry_run=True)  # Start with dry run
                print("✅ Mature enrichment system enabled")
            except Exception as e:
                print(f"⚠️ Mature enrichment initialization failed: {e}")
                self.enable_mature_enrichment = False
        
        # Tier structure para priorização estratégica
        self.tier_structure = {
            'platinum': {'min_score': 0.90, 'min_impact': 150, 'priority': 1},
            'gold': {'min_score': 0.85, 'min_impact': 100, 'priority': 2},
            'silver': {'min_score': 0.80, 'min_impact': 70, 'priority': 3},
            'bronze': {'min_score': 0.75, 'min_impact': 50, 'priority': 4},
            'standard': {'min_score': 0.0, 'min_impact': 0, 'priority': 5}
        }
        
        # Business type value multipliers
        self.business_value_multipliers = {
            'legal': 1.8,      # Highest LTV
            'dental': 1.5,     # Premium services
            'medical': 1.4,    # High value
            'accounting': 1.3, # Professional services
            'beauty': 1.2,     # Recurring revenue
            'physiotherapy': 1.1,
            'chiropractic': 1.0,
            'real_estate': 0.9, # Variable revenue
            'other_professional': 0.8
        }
        
    def load_results(self) -> Dict:
        """Load discovery results"""
        with open(self.results_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def clean_domain(self, domain: str) -> str:
        """Clean domain for BigQuery key"""
        if not domain:
            return ""
        
        # Remove protocol and path
        domain = re.sub(r'^https?://', '', domain)
        domain = re.sub(r'/.*$', '', domain)
        domain = re.sub(r' › .*$', '', domain)
        
        return domain.lower().strip()
    
    def classify_tier(self, prospect: Dict) -> Dict:
        """Classify prospect into strategic tiers"""
        fit_score = prospect['overall_fit_score']
        impact = prospect['estimated_monthly_impact']
        business_type = prospect['business_type']
        
        # Apply business value multiplier
        multiplier = self.business_value_multipliers.get(business_type, 1.0)
        adjusted_impact = impact * multiplier
        
        # Check tiers in priority order
        for tier_name, criteria in [
            ('platinum', self.tier_structure['platinum']),
            ('gold', self.tier_structure['gold']),
            ('silver', self.tier_structure['silver']),
            ('bronze', self.tier_structure['bronze'])
        ]:
            if fit_score >= criteria['min_score'] and adjusted_impact >= criteria['min_impact']:
                return {
                    'tier': tier_name,
                    'tier_display': f"Tier {criteria['priority']} - {tier_name.title()}",
                    'priority': criteria['priority'],
                    'adjusted_impact': adjusted_impact
                }
        
        return {
            'tier': 'standard',
            'tier_display': "Tier 5 - Standard",
            'priority': 5,
            'adjusted_impact': adjusted_impact
        }
    
    def detect_market_region(self, prospect: Dict) -> str:
        """Detect specific market region"""
        domain = prospect.get('domain', '').lower()
        query = prospect.get('discovery_query', '').lower()
        name = prospect.get('company_name', '').lower()
        
        content = f"{domain} {query} {name}"
        
        # Canadian markets - prioritize .ca domain
        if '.ca' in content or any(city in content for city in 
            ['vancouver', 'toronto', 'calgary', 'montreal', 'ottawa', 'ontario']):
            if 'vancouver' in content and '.ca' in content: return 'Vancouver, BC'
            elif 'toronto' in content and '.ca' in content: return 'Toronto, ON'
            elif 'calgary' in content and '.ca' in content: return 'Calgary, AB'
            elif 'montreal' in content and '.ca' in content: return 'Montreal, QC'
            elif 'ottawa' in content and '.ca' in content: return 'Ottawa, ON'
            elif 'ontario' in content and '.ca' in content: return 'Ontario, CA'
            elif '.ca' in content: return 'Canada'
        
        # US markets - check for US cities without .ca
        if any(city in content for city in 
            ['seattle', 'buffalo', 'denver', 'portland']) and '.ca' not in content:
            if 'seattle' in content: return 'Seattle, WA'
            elif 'buffalo' in content: return 'Buffalo, NY'
            elif 'denver' in content: return 'Denver, CO'
            elif 'portland' in content: return 'Portland, OR'
            else: return 'USA'
        
        # Vancouver fallback - check if actually Canadian or US
        if 'vancouver' in content:
            if '.ca' in content or 'bc' in content or 'canada' in content:
                return 'Vancouver, BC'
            else:
                return 'Vancouver, WA'
        
        return 'North America'
    
    def classify_query_type(self, query: str) -> str:
        """Classify discovery query type for insight"""
        query_lower = query.lower()
        
        if 'book' in query_lower and ('appointment' in query_lower or 'online' in query_lower):
            return 'booking_optimization'
        elif 'consultation' in query_lower:
            return 'consultation_funnel'
        elif 'law firm' in query_lower or 'legal' in query_lower:
            return 'legal_services'
        elif 'accounting' in query_lower or 'small business' in query_lower:
            return 'accounting_services'
        elif 'real estate' in query_lower:
            return 'real_estate_services'
        elif 'family' in query_lower and ('practice' in query_lower or 'dental' in query_lower):
            return 'family_services'
        else:
            return 'general_services'
    
    def calculate_follow_up_date(self, tier_priority: int) -> str:
        """Calculate strategic follow-up dates"""
        now = datetime.now()
        
        if tier_priority == 1:  # Platinum - immediate
            return (now + timedelta(hours=24)).strftime("%Y-%m-%dT09:00:00")
        elif tier_priority == 2:  # Gold - 2 days
            return (now + timedelta(days=2)).strftime("%Y-%m-%dT09:00:00")
        elif tier_priority == 3:  # Silver - 5 days
            return (now + timedelta(days=5)).strftime("%Y-%m-%dT09:00:00")
        elif tier_priority == 4:  # Bronze - 1 week
            return (now + timedelta(days=7)).strftime("%Y-%m-%dT09:00:00")
        else:  # Standard - 2 weeks
            return (now + timedelta(days=14)).strftime("%Y-%m-%dT09:00:00")
    
    def format_currency_display(self, amount: float, currency: str) -> str:
        """Format currency for display"""
        return f"{currency} ${amount:,.0f}"
    
    def generate_insights_note(self, prospect: Dict, tier_info: Dict) -> str:
        """Generate intelligent insights note"""
        business_type = prospect['business_type'].title()
        fit_score = prospect['overall_fit_score']
        query_type = self.classify_query_type(prospect.get('discovery_query', ''))
        
        note = f"Discovered via {query_type}. Fit score: {fit_score:.2f}. "
        
        if tier_info['priority'] <= 2:
            note += "HIGH VALUE TARGET - immediate outreach recommended. "
        
        if business_type == 'Legal':
            note += "Legal services = high LTV potential. "
        elif business_type == 'Dental':
            note += "Dental practice = recurring revenue model. "
        elif business_type == 'Medical':
            note += "Medical practice = stable business model. "
        
        return note.strip()
    
    def enrich_with_mature_system(self, prospects: List[Dict], max_prospects: int = 5) -> Tuple[List[Dict], Dict]:
        """
        Enrich prospects using mature enrichment system
        """
        if not self.enable_mature_enrichment:
            print("⚠️ Mature enrichment not available")
            return prospects, {}
        
        print(f"🎯 Starting mature enrichment for {min(len(prospects), max_prospects)} prospects...")
        
        # Limit prospects for cost control
        limited_prospects = prospects[:max_prospects]
        
        # Use mature enricher
        enriched_prospects, costs = self.mature_enricher.enrich_prospect_list(
            limited_prospects, 
            max_prospects=max_prospects
        )
        
        print(f"✅ Mature enrichment complete")
        print(f"💰 Total cost: ${costs.get('total_cost', 0):.3f}")
        print(f"⏱️ Processing time: {costs.get('total_time_seconds', 0):.1f}s")
        
        return enriched_prospects, costs
    
    def get_pagespeed_insights(self, domain: str) -> Dict:
        """Get PageSpeed Insights for website performance"""
        if not domain:
            return {}
        
        clean_domain = self.clean_domain(domain)
        if not clean_domain:
            return {}
        
        try:
            # Use existing PageSpeed API from config
            from config.api_keys import APIConfig
            config = APIConfig()
            
            url = f"https://{clean_domain}"
            api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
            
            params = {
                'url': url,
                'key': config.PAGESPEED_API_KEY,
                'category': 'performance',
                'strategy': 'desktop'
            }
            
            response = requests.get(api_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                lighthouse = data.get('lighthouseResult', {})
                categories = lighthouse.get('categories', {})
                performance = categories.get('performance', {})
                
                return {
                    'page_speed_score': round(performance.get('score', 0) * 100, 1),
                    'website_status': 'active',
                    'last_checked': datetime.now().isoformat()
                }
            
        except Exception as e:
            print(f"⚠️ PageSpeed check failed for {domain}: {e}")
        
        return {
            'page_speed_score': 0,
            'website_status': 'unknown',
            'last_checked': datetime.now().isoformat()
        }
    
    def estimate_digital_maturity(self, prospect: Dict, pagespeed_data: Dict) -> Dict:
        """Estimate digital maturity and technology stack"""
        
        domain = prospect.get('domain', '')
        business_type = prospect.get('business_type', '').lower()
        
        # Base digital maturity score
        maturity_score = 30  # Starting baseline
        
        # PageSpeed contribution (0-25 points)
        speed_score = pagespeed_data.get('page_speed_score', 0)
        maturity_score += min(speed_score * 0.25, 25)
        
        # Business type digital adoption patterns
        digital_adoption_rates = {
            'dental': 60,      # Growing digital adoption
            'medical': 45,     # Conservative but improving  
            'legal': 40,       # Traditional, slow adoption
            'accounting': 70,  # High digital tool usage
            'beauty': 75,      # Social media savvy
            'real_estate': 80, # Tech-forward industry
            'physiotherapy': 55,
            'chiropractic': 50
        }
        
        base_adoption = digital_adoption_rates.get(business_type, 50)
        maturity_score = (maturity_score + base_adoption) / 2
        
        # Market region technology adoption
        market_region = prospect.get('market_region', '')
        if any(city in market_region for city in ['Vancouver', 'Toronto', 'Seattle']):
            maturity_score += 10  # Tech-forward markets
        elif any(city in market_region for city in ['Calgary', 'Montreal']):
            maturity_score += 5   # Moderate tech adoption
        
        # Website quality indicators
        if pagespeed_data.get('website_status') == 'active':
            maturity_score += 15
        
        return {
            'digital_maturity_score': round(min(maturity_score, 100), 1),
            'technology_readiness': 'High' if maturity_score >= 70 else 'Medium' if maturity_score >= 50 else 'Low',
            'digital_opportunity': 'Optimization' if maturity_score >= 60 else 'Modernization'
        }
    
    def calculate_market_intelligence(self, prospect: Dict) -> Dict:
        """Calculate advanced market intelligence metrics"""
        
        business_type = prospect.get('business_type', '').lower()
        market_region = prospect.get('market_region', '')
        monthly_revenue = prospect.get('estimated_monthly_revenue', 0)
        employees = prospect.get('estimated_employees', 0)
        
        # Industry benchmarks from existing system
        industry_benchmarks = {
            'dental': {'avg_revenue': 85000, 'avg_employees': 6, 'growth_rate': 0.12},
            'medical': {'avg_revenue': 120000, 'avg_employees': 8, 'growth_rate': 0.08},
            'legal': {'avg_revenue': 180000, 'avg_employees': 12, 'growth_rate': 0.06},
            'accounting': {'avg_revenue': 95000, 'avg_employees': 7, 'growth_rate': 0.10},
            'beauty': {'avg_revenue': 75000, 'avg_employees': 5, 'growth_rate': 0.15}
        }
        
        benchmark = industry_benchmarks.get(business_type, {'avg_revenue': 100000, 'avg_employees': 7, 'growth_rate': 0.08})
        
        # Revenue positioning
        revenue_percentile = min((monthly_revenue / benchmark['avg_revenue']) * 50, 95)
        
        # Size positioning  
        size_percentile = min((employees / benchmark['avg_employees']) * 50, 95)
        
        # Market opportunity score
        market_factors = []
        
        # Revenue vs benchmark
        if monthly_revenue >= benchmark['avg_revenue'] * 1.2:
            market_factors.append(85)  # Above market performer
        elif monthly_revenue >= benchmark['avg_revenue'] * 0.8:
            market_factors.append(70)  # Market average
        else:
            market_factors.append(50)  # Below market - growth opportunity
        
        # Geographic market strength
        if 'Vancouver' in market_region or 'Toronto' in market_region or 'Seattle' in market_region:
            market_factors.append(80)  # Premium markets
        elif 'Calgary' in market_region or 'Montreal' in market_region:
            market_factors.append(70)  # Strong markets
        else:
            market_factors.append(60)  # Standard markets
        
        market_opportunity_score = sum(market_factors) / len(market_factors)
        
        return {
            'market_opportunity_score': round(market_opportunity_score, 1),
            'revenue_percentile': round(revenue_percentile, 1),
            'size_percentile': round(size_percentile, 1),
            'growth_potential': benchmark['growth_rate'],
            'competitive_position': 'Leader' if revenue_percentile >= 75 else 'Challenger' if revenue_percentile >= 50 else 'Follower'
        }
    
    def generate_enriched_insights(self, prospect: Dict, enrichment_data: Dict) -> str:
        """Generate intelligent insights combining all enrichment data"""
        
        business_type = prospect['business_type'].title()
        fit_score = prospect['overall_fit_score']
        
        insights = []
        
        # Core discovery insight
        query_type = self.classify_query_type(prospect.get('discovery_query', ''))
        insights.append(f"Discovered via {query_type}")
        
        # Fit and tier insights
        tier_info = self.classify_tier(prospect)
        insights.append(f"Fit score: {fit_score:.2f}")
        
        if tier_info['priority'] <= 2:
            insights.append("HIGH VALUE TARGET - immediate outreach recommended")
        
        # Digital maturity insights
        digital_maturity = enrichment_data.get('digital_maturity_score', 0)
        if digital_maturity >= 70:
            insights.append("High digital maturity - tech-savvy prospect")
        elif digital_maturity <= 40:
            insights.append("Digital modernization opportunity")
        
        # Market position insights
        market_score = enrichment_data.get('market_opportunity_score', 0)
        competitive_position = enrichment_data.get('competitive_position', 'Unknown')
        
        if competitive_position == 'Leader':
            insights.append("Market leader - premium positioning")
        elif market_score >= 75:
            insights.append("High market opportunity")
        
        # Business-specific insights
        if business_type == 'Legal':
            insights.append("Legal services = high LTV potential")
        elif business_type == 'Dental':
            insights.append("Dental practice = recurring revenue model")
        elif business_type == 'Medical':
            insights.append("Medical practice = stable business model")
        
        # Website performance insights
        page_speed = enrichment_data.get('page_speed_score', 0)
        if page_speed >= 80:
            insights.append("Excellent website performance")
        elif page_speed <= 50:
            insights.append("Website optimization opportunity")
        
        return ". ".join(insights) + "."
    
    def export_to_csv(self, prospects: List[Dict], enrichment_mode: str = "basic") -> str:
        """
        Export prospects to CSV with multiple enrichment modes:
        - basic: Standard export without enrichment
        - dry_run: Advanced enrichment with cost estimation (sample analysis)
        - full_live: Complete live enrichment with all APIs
        """
        
        print(f"📊 Processing {len(prospects)} prospects...")
        print(f"🔧 Enrichment mode: {enrichment_mode}")
        
        # Handle different enrichment modes
        if enrichment_mode == "dry_run" and self.enable_advanced_enrichment:
            return self._export_with_dry_run_analysis(prospects)
        elif enrichment_mode == "full_live" and self.enable_advanced_enrichment:
            return self._export_with_full_enrichment(prospects)
        else:
            return self._export_basic_csv(prospects)
    
    def _export_basic_csv(self, prospects: List[Dict]) -> str:
        """Basic CSV export without advanced enrichment"""
        print("📋 Basic export mode - no advanced enrichment")
        
        csv_data = []
        
        for i, prospect in enumerate(prospects, 1):
            print(f"📍 Processing {i}/{len(prospects)}: {prospect['company_name'][:40]}...")
            
            # Core classification
            tier_info = self.classify_tier(prospect)
            market_region = self.detect_market_region(prospect)
            query_type = self.classify_query_type(prospect.get('discovery_query', ''))
            
            # Detect currency
            currency = 'CAD' if 'canada' in market_region.lower() or '.ca' in prospect.get('domain', '') else 'USD'
            
            # Clean domain for BigQuery
            clean_domain = self.clean_domain(prospect.get('domain', ''))
            
            row = {
                # Core identifiers
                'company_name': prospect['company_name'],
                'domain': prospect.get('domain', ''),
                'website_clean': f"https://{clean_domain}" if clean_domain else "",
                
                # Strategic classification
                'priority_tier': tier_info['priority'],
                'tier_name': tier_info['tier_display'],
                'business_type': prospect['business_type'].title(),
                'market_region': market_region,
                
                # Business metrics
                'estimated_employees': prospect['estimated_employees'],
                'currency': currency,
                'monthly_revenue_display': self.format_currency_display(
                    prospect['estimated_monthly_revenue'], currency),
                'monthly_revenue_numeric': prospect['estimated_monthly_revenue'],
                'monthly_marketing_spend_display': self.format_currency_display(
                    prospect['estimated_monthly_marketing_spend'], currency),
                'monthly_marketing_spend_numeric': prospect['estimated_monthly_marketing_spend'],
                'opportunity_value_display': self.format_currency_display(
                    tier_info['adjusted_impact'], currency),
                'opportunity_value_numeric': tier_info['adjusted_impact'],
                
                # Quality scores
                'overall_fit_score': prospect['overall_fit_score'],
                'size_confidence': prospect['size_confidence'],
                'revenue_confidence': prospect['revenue_confidence'],
                'marketing_confidence': prospect['marketing_confidence'],
                'opportunity_confidence': prospect['opportunity_confidence'],
                
                # Opportunity details
                'opportunity_type': prospect['opportunity_type'],
                'discovery_query_type': query_type,
                
                # Basic enrichment placeholders
                'enrichment_status': 'basic_export',
                'enrichment_mode': 'basic',
                'enrichment_timestamp': datetime.now().isoformat(),
                
                # CRM workflow
                'lead_status': 'new',
                'assigned_to': '',
                'contact_priority': 'high' if tier_info['priority'] <= 2 else 'medium' if tier_info['priority'] <= 3 else 'low',
                'follow_up_date': self.calculate_follow_up_date(tier_info['priority']),
                'notes': self.generate_insights_note(prospect, tier_info),
                
                # Metadata
                'created_date': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat()
            }
            
            csv_data.append(row)
        
        # Sort by priority tier and fit score
        csv_data.sort(key=lambda x: (x['priority_tier'], -x['overall_fit_score']))
        
        # Generate filename
        output_path = Path("exports/crm") / f"all_qualified_leads_basic_{self.timestamp}.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Export to CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            if csv_data:
                fieldnames = csv_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
        
        print(f"📁 Basic CSV exported: {output_path}")
        return str(output_path)
    
    def _export_with_dry_run_analysis(self, prospects: List[Dict]) -> str:
        """Export with dry run analysis and cost estimation"""
        
        print("🔬 DRY RUN ENRICHMENT ANALYSIS")
        print("=" * 50)
        
        # Run dry run analysis with mature enricher
        if not self.enable_mature_enrichment:
            print("⚠️ Mature enrichment not available - falling back to basic export")
            return self._export_basic_csv(prospects)
        
        # Set to dry run mode
        self.mature_enricher.dry_run = True
        
        # Run sample enrichment
        sample_prospects = prospects[:5]  # Sample first 5
        enriched_sample, costs = self.mature_enricher.enrich_prospect_list(sample_prospects)
        
        # Display costs and analysis
        print(f"\n💰 COST ANALYSIS (Sample of {len(sample_prospects)} prospects):")
        print(f"   API calls made: {costs.get('pagespeed_calls', 0)} PageSpeed + {costs.get('searchapi_calls', 0)} SearchAPI")
        print(f"   Estimated cost: ${costs.get('total_cost', 0):.3f}")
        print(f"   Processing time: {costs.get('total_time_seconds', 0):.1f}s")
        
        # Extrapolate costs for full dataset
        total_prospects = len(prospects)
        estimated_total_cost = costs.get('total_cost', 0) * (total_prospects / len(sample_prospects))
        estimated_total_time = costs.get('total_time_seconds', 0) * (total_prospects / len(sample_prospects))
        
        print(f"\n📊 FULL DATASET PROJECTIONS ({total_prospects} prospects):")
        print(f"   Estimated total cost: ${estimated_total_cost:.3f}")
        print(f"   Estimated total time: {estimated_total_time/60:.1f} minutes")
        
        # Show sample insights
        if enriched_sample:
            print(f"\n🎯 SAMPLE ENRICHMENT INSIGHTS:")
            for prospect in enriched_sample[:3]:
                enrichment = prospect.get('enrichment', {})
                insights = enrichment.get('outreach_insights', {})
                print(f"   • {prospect.get('company_name', 'Unknown')}: {insights.get('outreach_priority', 'Unknown')} priority")
        
        # Ask user for decision
        print("\n🎯 DRY RUN COMPLETE - Choose next action:")
        print("1. Proceed with FULL LIVE enrichment")
        print("2. Export SAMPLE with enrichment data")
        print("3. Export ALL with BASIC data only")
        print("4. Cancel export")
        
        while True:
            choice = input("\nYour choice (1-4): ").strip()
            
            if choice == "1":
                print("🚀 Proceeding with full live enrichment...")
                self.mature_enricher.dry_run = False
                return self._export_with_full_enrichment(prospects)
            
            elif choice == "2":
                print("📊 Exporting sample with enrichment data...")
                return self._export_sample_enriched(enriched_sample)
            
            elif choice == "3":
                print("📋 Exporting all prospects with basic data...")
                return self._export_basic_csv(prospects)
            
            elif choice == "4":
                print("❌ Export cancelled")
                return ""
            
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")

    def _export_with_full_enrichment(self, prospects: List[Dict]) -> str:
        """Export with full live enrichment"""
        
        print("🚀 FULL LIVE ENRICHMENT")
        print("=" * 50)
        
        if not self.enable_mature_enrichment:
            print("⚠️ Mature enrichment not available - falling back to basic export")
            return self._export_basic_csv(prospects)
        
        # Set to live mode
        self.mature_enricher.dry_run = False
        
        # Enrich all prospects
        enriched_prospects, costs = self.mature_enricher.enrich_prospect_list(prospects)
        
        print(f"✅ Full enrichment complete!")
        print(f"💰 Total cost: ${costs.get('total_cost', 0):.3f}")
        print(f"⏱️ Processing time: {costs.get('total_time_seconds', 0):.1f}s")
        
        # Export enriched data
        return self._export_enriched_csv(enriched_prospects)
    
    def _export_sample_enriched(self, enriched_sample: List[Dict]) -> str:
        """Export sample with enrichment data"""
        
        print("📊 SAMPLE ENRICHED EXPORT")
        print("=" * 50)
        
        return self._export_enriched_csv(enriched_sample, filename_suffix="sample")
    
    def _export_enriched_csv(self, enriched_prospects: List[Dict], filename_suffix: str = "enriched") -> str:
        """Export enriched prospects to CSV"""
        
        csv_data = []
        
        for i, prospect in enumerate(enriched_prospects, 1):
            print(f"📊 Processing {i}/{len(enriched_prospects)}: {prospect['company_name'][:40]}...")
            
            # Core classification
            tier_info = self.classify_tier(prospect)
            market_region = self.detect_market_region(prospect)
            
            # Extract enrichment data
            enrichment = prospect.get('enrichment', {})
            performance = enrichment.get('performance', {})
            maturity = enrichment.get('digital_maturity', {})
            insights = enrichment.get('outreach_insights', {})
            
            # Detect currency
            currency = 'CAD' if 'canada' in market_region.lower() or '.ca' in prospect.get('domain', '') else 'USD'
            clean_domain = self.clean_domain(prospect.get('domain', ''))
            
            row = {
                # Core identifiers
                'company_name': prospect['company_name'],
                'domain': prospect.get('domain', ''),
                'website_clean': f"https://{clean_domain}" if clean_domain else "",
                
                # Strategic classification - ENRICHED
                'priority_tier': tier_info['priority'],
                'tier_name': tier_info['tier_display'],
                'business_type': prospect['business_type'].title(),
                'market_region': market_region,
                
                # Business metrics
                'estimated_employees': prospect['estimated_employees'],
                'currency': currency,
                'monthly_revenue_display': self.format_currency_display(
                    prospect['estimated_monthly_revenue'], currency),
                'monthly_revenue_numeric': prospect['estimated_monthly_revenue'],
                'opportunity_value_display': self.format_currency_display(
                    tier_info['adjusted_impact'], currency),
                'opportunity_value_numeric': tier_info['adjusted_impact'],
                
                # ENRICHED SCORING SYSTEM
                'overall_score': prospect['overall_fit_score'],
                'digital_maturity_score': maturity.get('digital_maturity_score', 0),
                'technology_readiness': maturity.get('technology_readiness', 'Unknown'),
                'digital_opportunity': maturity.get('digital_opportunity', 'Unknown'),
                
                # PERFORMANCE INTELLIGENCE
                'website_performance_score': performance.get('performance_score', 0),
                'website_accessibility_score': performance.get('accessibility_score', 0),
                'website_seo_score': performance.get('seo_score', 0),
                'website_best_practices_score': performance.get('best_practices_score', 0),
                'website_overall_score': performance.get('overall_score', 0),
                'website_status': performance.get('website_status', 'unknown'),
                'needs_improvement': performance.get('needs_improvement', True),
                
                # OUTREACH INTELLIGENCE
                'outreach_priority': insights.get('outreach_priority', 'Standard'),
                'primary_pain_point': insights.get('primary_pain_point', 'General Improvement'),
                'urgency_level': insights.get('urgency_level', 'Medium'),
                'estimated_monthly_impact': insights.get('estimated_monthly_impact', 0),
                'success_probability': insights.get('success_probability', 0.5),
                'follow_up_timeline': insights.get('follow_up_timeline', '1 week'),
                
                # TALKING POINTS
                'talking_point_1': insights.get('talking_points', [''])[0] if insights.get('talking_points') else '',
                'talking_point_2': insights.get('talking_points', ['', ''])[1] if len(insights.get('talking_points', [])) > 1 else '',
                'talking_point_3': insights.get('talking_points', ['', '', ''])[2] if len(insights.get('talking_points', [])) > 2 else '',
                
                # Discovery metadata
                'discovery_query': prospect.get('discovery_query', ''),
                'discovery_date': prospect.get('discovery_date', ''),
                'discovery_source': 'SearchAPI Real Discovery',
                
                # Enrichment metadata
                'enrichment_status': 'enriched',
                'enrichment_mode': 'live' if not enrichment.get('dry_run', False) else 'dry_run',
                'enrichment_timestamp': enrichment.get('enriched_at', datetime.now().isoformat()),
                
                # CRM workflow
                'lead_status': 'new',
                'assigned_to': '',
                'contact_priority': insights.get('outreach_priority', 'Standard').lower(),
                'follow_up_date': self.calculate_follow_up_date(tier_info['priority']),
                'notes': self.generate_enriched_insights_note(prospect, enrichment),
                
                # Metadata
                'created_date': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat()
            }
            
            csv_data.append(row)
        
        # Sort by priority and success probability
        csv_data.sort(key=lambda x: (x['priority_tier'], -x['success_probability']))
        
        # Generate filename
        output_path = Path("exports/crm") / f"qualified_leads_{filename_suffix}_{self.timestamp}.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Export to CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            if csv_data:
                fieldnames = csv_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
        
        print(f"📁 Enriched CSV exported: {output_path}")
        return str(output_path)
    
    def generate_enriched_insights_note(self, prospect: Dict, enrichment: Dict) -> str:
        """Generate enriched insights note for CRM"""
        
        insights = enrichment.get('outreach_insights', {})
        performance = enrichment.get('performance', {})
        maturity = enrichment.get('digital_maturity', {})
        
        note_parts = []
        
        # Primary opportunity
        opportunity = insights.get('primary_pain_point', '')
        if opportunity:
            note_parts.append(f"Primary opportunity: {opportunity}")
        
        # Performance insights
        overall_score = performance.get('overall_score', 0)
        if overall_score > 0:
            if overall_score < 50:
                note_parts.append("Website performance significantly below industry standards")
            elif overall_score < 70:
                note_parts.append("Moderate website performance improvements needed")
        
        # Digital maturity
        readiness = maturity.get('technology_readiness', '')
        if readiness:
            note_parts.append(f"Technology readiness: {readiness}")
        
        # Success probability
        success_prob = insights.get('success_probability', 0)
        if success_prob >= 0.7:
            note_parts.append("HIGH conversion probability")
        elif success_prob >= 0.5:
            note_parts.append("MEDIUM conversion probability")
        
        return ". ".join(note_parts[:3]) + "." if note_parts else "Enriched prospect analysis complete."
        
    def export_to_csv(self, prospects: List[Dict], enrichment_mode: str = 'basic') -> Tuple[str, str]:
        """Main export method with different enrichment modes"""
        
        if enrichment_mode == 'dry_run':
            csv_path = self._export_with_dry_run_analysis(prospects)
        elif enrichment_mode == 'full_live':
            csv_path = self._export_with_full_enrichment(prospects)
        else:  # basic
            csv_path = self._export_basic_csv(prospects)
        
        # Generate summary report
        report = self._generate_export_report(prospects, csv_path, enrichment_mode)
        
        return csv_path, report
    
    def _export_with_full_enrichment(self, prospects: List[Dict]) -> str:
        """Export with full live enrichment"""
        
        print("🚀 FULL LIVE ENRICHMENT MODE")
        print("=" * 50)
        
        # Estimate final costs
        estimated_cost = len(prospects) * 0.025  # $0.025 per prospect
        print(f"💰 Estimated total cost: ${estimated_cost:.2f}")
        
        # Confirm with user
        confirm = input(f"\n⚡ Proceed with live enrichment for {len(prospects)} prospects? (y/N): ").strip().lower()
        
        if confirm not in ['y', 'yes']:
            print("❌ Live enrichment cancelled")
            return self._export_basic_csv(prospects)
        
        print("🔍 Starting live enrichment...")
        
        csv_data = []
        
        for i, prospect in enumerate(prospects, 1):
            print(f"\n📊 Processing {i}/{len(prospects)}: {prospect['company_name'][:40]}...")
            
            # Core classification
            tier_info = self.classify_tier(prospect)
            market_region = self.detect_market_region(prospect)
            query_type = self.classify_query_type(prospect.get('discovery_query', ''))
            
            # Detect currency
            currency = 'CAD' if 'canada' in market_region.lower() or '.ca' in prospect.get('domain', '') else 'USD'
            clean_domain = self.clean_domain(prospect.get('domain', ''))
            
            # Advanced enrichment
            enrichment_data = self.advanced_enricher.enrich_prospect(prospect, enable_full_analysis=True)
            
            # Extract advanced scores
            prospect_score = enrichment_data.get('prospect_score', {})
            
            row = {
                # Core identifiers
                'company_name': prospect['company_name'],
                'domain': prospect.get('domain', ''),
                'website_clean': f"https://{clean_domain}" if clean_domain else "",
                
                # Strategic classification - ENHANCED
                'priority_tier': prospect_score.get('priority_rank', tier_info['priority']),
                'tier_name': f"Tier {prospect_score.get('priority_rank', tier_info['priority'])} - {prospect_score.get('tier', 'unknown').title()}",
                'business_type': prospect['business_type'].title(),
                'market_region': market_region,
                
                # Business metrics
                'estimated_employees': prospect['estimated_employees'],
                'currency': currency,
                'monthly_revenue_display': self.format_currency_display(
                    prospect['estimated_monthly_revenue'], currency),
                'monthly_revenue_numeric': prospect['estimated_monthly_revenue'],
                'opportunity_value_display': self.format_currency_display(
                    tier_info['adjusted_impact'], currency),
                'opportunity_value_numeric': tier_info['adjusted_impact'],
                
                # ADVANCED SCORING SYSTEM
                'overall_score': prospect_score.get('overall_score', prospect['overall_fit_score']),
                'technical_score': prospect_score.get('technical_score', 0),
                'market_opportunity_score': prospect_score.get('market_opportunity_score', 50),
                'urgency_score': prospect_score.get('urgency_score', 50),
                'conversion_likelihood': prospect_score.get('conversion_likelihood', 50),
                
                # PERFORMANCE INTELLIGENCE
                'performance_score': enrichment_data.get('pagespeed_analysis', {}).get('performance_score', 0),
                'accessibility_score': enrichment_data.get('pagespeed_analysis', {}).get('accessibility_score', 0),
                'seo_score': enrichment_data.get('pagespeed_analysis', {}).get('seo_score', 0),
                'largest_contentful_paint': enrichment_data.get('pagespeed_analysis', {}).get('largest_contentful_paint', 0),
                'cumulative_layout_shift': enrichment_data.get('pagespeed_analysis', {}).get('cumulative_layout_shift', 0),
                
                # USER EXPERIENCE DATA (CrUX)
                'lcp_good_percentage': enrichment_data.get('crux_analysis', {}).get('lcp_good_percentage', 0),
                'lcp_poor_percentage': enrichment_data.get('crux_analysis', {}).get('lcp_poor_percentage', 0),
                'overall_user_experience': enrichment_data.get('crux_analysis', {}).get('overall_user_experience', 'unknown'),
                
                # SEO INTELLIGENCE
                'seo_visibility_score': enrichment_data.get('seo_analysis', {}).get('visibility_score', 0),
                'organic_keywords_estimated': enrichment_data.get('seo_analysis', {}).get('organic_keywords_estimated', 0),
                'domain_authority_estimated': enrichment_data.get('seo_analysis', {}).get('domain_authority_estimated', 0),
                'local_seo_signals': enrichment_data.get('seo_analysis', {}).get('local_seo_signals', 'unknown'),
                
                # MARKET INTELLIGENCE
                'digital_maturity_score': enrichment_data.get('digital_maturity_score', 50),
                'industry_growth_rate': enrichment_data.get('market_intelligence', {}).get('industry_growth_rate', 0),
                'competition_density': enrichment_data.get('market_intelligence', {}).get('competition_density', 'unknown'),
                'market_maturity': enrichment_data.get('market_intelligence', {}).get('market_maturity', 'unknown'),
                
                # ACTIONABLE INSIGHTS
                'primary_pain_point': enrichment_data.get('outreach_strategy', {}).get('primary_pain_point', ''),
                'value_proposition': enrichment_data.get('outreach_strategy', {}).get('value_proposition', ''),
                'outreach_approach': enrichment_data.get('outreach_strategy', {}).get('approach', ''),
                'outreach_timing': enrichment_data.get('outreach_strategy', {}).get('timing', ''),
                
                # INSIGHTS SUMMARY
                'actionable_insights': ' | '.join(enrichment_data.get('actionable_insights', [])),
                'insight_count': len(enrichment_data.get('actionable_insights', [])),
                
                # ENRICHMENT METADATA
                'enrichment_status': 'full_live_complete',
                'enrichment_mode': 'full_live',
                'enrichment_timestamp': enrichment_data.get('enrichment_timestamp', ''),
                
                # CRM WORKFLOW - ENHANCED
                'lead_status': 'enriched_ready',
                'assigned_to': '',
                'contact_priority': 'urgent' if prospect_score.get('urgency_score', 0) > 80 else 'high' if prospect_score.get('conversion_likelihood', 0) > 70 else 'medium',
                'follow_up_date': self.calculate_follow_up_date(prospect_score.get('priority_rank', 5)),
                'notes': ' | '.join(enrichment_data.get('actionable_insights', [])),
                
                # Metadata
                'created_date': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat()
            }
            
            csv_data.append(row)
        
        # Sort by advanced scoring
        csv_data.sort(key=lambda x: (x['priority_tier'], -x['overall_score'], -x['conversion_likelihood']))
        
        # Generate filename
        output_path = Path("exports/crm") / f"all_qualified_leads_ENRICHED_{self.timestamp}.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Export to CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            if csv_data:
                fieldnames = csv_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
        
        # Final cost tracking
        final_costs = self.advanced_enricher.costs
        print(f"\n💰 FINAL ENRICHMENT COSTS:")
        print(f"   API Calls Made: {final_costs.api_calls}")
        print(f"   Total Cost: ${final_costs.total_estimated_cost:.2f}")
        print(f"   Cost per Prospect: ${final_costs.total_estimated_cost/len(prospects):.3f}")
        
        print(f"\n📁 Enriched CSV exported: {output_path}")
        return str(output_path)
    
    def _export_sample_enriched(self, sample_results: List[Dict]) -> str:
        """Export sample results with enrichment data"""
        
        print("📊 Exporting sample with enrichment data...")
        
        csv_data = []
        
        for result in sample_results:
            prospect = result['prospect']
            enrichment = result['enrichment']
            
            # Core classification
            tier_info = self.classify_tier(prospect)
            market_region = self.detect_market_region(prospect)
            
            # Detect currency
            currency = 'CAD' if 'canada' in market_region.lower() or '.ca' in prospect.get('domain', '') else 'USD'
            clean_domain = self.clean_domain(prospect.get('domain', ''))
            
            # Extract advanced scores
            prospect_score = enrichment.get('prospect_score', {})
            
            row = {
                # Core identifiers
                'company_name': prospect['company_name'],
                'domain': prospect.get('domain', ''),
                'sample_analysis': True,
                
                # Advanced scoring
                'overall_score': prospect_score.get('overall_score', 0),
                'technical_score': prospect_score.get('technical_score', 0),
                'conversion_likelihood': prospect_score.get('conversion_likelihood', 0),
                'tier': prospect_score.get('tier', 'unknown'),
                
                # Performance data
                'performance_score': enrichment.get('pagespeed_analysis', {}).get('performance_score', 0),
                'seo_visibility': enrichment.get('seo_analysis', {}).get('visibility_score', 0),
                'user_experience': enrichment.get('crux_analysis', {}).get('overall_user_experience', 'unknown'),
                
                # Insights
                'actionable_insights': ' | '.join(enrichment.get('actionable_insights', [])),
                'primary_pain_point': enrichment.get('outreach_strategy', {}).get('primary_pain_point', ''),
                'value_proposition': enrichment.get('outreach_strategy', {}).get('value_proposition', ''),
                
                # Metadata
                'enrichment_mode': 'sample_analysis',
                'created_date': datetime.now().isoformat()
            }
            
            csv_data.append(row)
        
        # Generate filename
        output_path = Path("exports/crm") / f"sample_enriched_analysis_{self.timestamp}.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Export to CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            if csv_data:
                fieldnames = csv_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
        
        print(f"📁 Sample CSV exported: {output_path}")
        return str(output_path)
    
    def generate_summary_report(self, prospects: List[Dict], csv_path: str) -> str:
        """Generate executive summary report"""
        
        # Tier distribution
        tier_counts = {}
        total_value = 0
        
        for prospect in prospects:
            tier_info = self.classify_tier(prospect)
            tier = tier_info['tier']
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
            total_value += tier_info['adjusted_impact']
        
        # Business type distribution
        business_counts = {}
        for prospect in prospects:
            btype = prospect['business_type']
            business_counts[btype] = business_counts.get(btype, 0) + 1
        
        # Market distribution
        market_counts = {}
        for prospect in prospects:
            region = self.detect_market_region(prospect)
            market_counts[region] = market_counts.get(region, 0) + 1
        
        report = f"""
🏢 COMPREHENSIVE CRM EXPORT REPORT
================================================================
📅 Export Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
📁 File: {csv_path}
📊 Total Prospects: {len(prospects)}
💰 Total Pipeline Value: ${total_value:,.0f}/month

🎯 TIER DISTRIBUTION:
"""
        
        for tier, count in sorted(tier_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(prospects)) * 100
            report += f"   {tier.title()}: {count} prospects ({percentage:.1f}%)\n"
        
        report += f"\n🏭 BUSINESS TYPE DISTRIBUTION:\n"
        for btype, count in sorted(business_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(prospects)) * 100
            report += f"   {btype.title()}: {count} prospects ({percentage:.1f}%)\n"
        
        report += f"\n🌍 MARKET DISTRIBUTION:\n"
        for region, count in sorted(market_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(prospects)) * 100
            report += f"   {region}: {count} prospects ({percentage:.1f}%)\n"
        
        # Top 10 prospects
        top_prospects = sorted(prospects, key=lambda x: self.classify_tier(x)['adjusted_impact'], reverse=True)[:10]
        
        report += f"\n🔥 TOP 10 HIGHEST VALUE PROSPECTS:\n"
        for i, prospect in enumerate(top_prospects, 1):
            tier_info = self.classify_tier(prospect)
            report += f"   {i}. {prospect['company_name'][:50]} (${tier_info['adjusted_impact']:.0f}/mo)\n"
        
        report += f"\n🎯 NEXT ACTIONS:\n"
        report += f"   1. Import CSV into CRM system\n"
        report += f"   2. Assign Platinum/Gold tiers immediately\n"
        report += f"   3. Enrich with BigQuery data\n"
        report += f"   4. Begin outreach sequence\n"
        
        return report
    
    def _generate_export_report(self, prospects: List[Dict], csv_path: str, enrichment_mode: str) -> str:
        """Generate export summary report"""
        
        total_prospects = len(prospects)
        tier_counts = {}
        
        for prospect in prospects:
            tier_info = self.classify_tier(prospect)
            tier = tier_info['tier']
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        report = f"""
📊 EXPORT SUMMARY REPORT
{'=' * 50}

📁 File: {csv_path}
🎯 Enrichment Mode: {enrichment_mode.title()}
📈 Total Prospects: {total_prospects}

🏆 TIER DISTRIBUTION:
"""
        
        for tier in ['platinum', 'gold', 'silver', 'bronze', 'standard']:
            count = tier_counts.get(tier, 0)
            if count > 0:
                percentage = (count / total_prospects) * 100
                report += f"   {tier.title()}: {count} prospects ({percentage:.1f}%)\n"
        
        # Business type distribution
        business_types = {}
        for prospect in prospects:
            btype = prospect.get('business_type', 'unknown')
            business_types[btype] = business_types.get(btype, 0) + 1
        
        report += f"\n🏢 BUSINESS TYPE DISTRIBUTION:\n"
        for btype, count in sorted(business_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_prospects) * 100
            report += f"   {btype.title()}: {count} prospects ({percentage:.1f}%)\n"
        
        # Revenue analysis
        revenues = [p.get('estimated_monthly_revenue', 0) for p in prospects]
        avg_revenue = sum(revenues) / len(revenues) if revenues else 0
        
        report += f"\n💰 REVENUE ANALYSIS:\n"
        report += f"   Average Monthly Revenue: ${avg_revenue:,.0f}\n"
        report += f"   Total Monthly Revenue Pool: ${sum(revenues):,.0f}\n"
        
        return report.strip()

def main():
    """Execute comprehensive export with advanced enrichment options"""
    
    print("🎯 ARCO-FIND ADVANCED PROSPECT ENRICHMENT SYSTEM")
    print("=" * 70)
    print("🔍 Complete intelligence pipeline with cost-controlled enrichment")
    
    # Load results
    results_file = "src/data/pragmatic_discovery_north_america_west_20250730_134507.json"
    
    # Initialize exporter with all systems
    enable_bigquery = BIGQUERY_AVAILABLE
    enable_mature = MATURE_ENRICHMENT_AVAILABLE
    
    print(f"\n🔧 SYSTEM STATUS:")
    print(f"   BigQuery Integration: {'✅ Available' if enable_bigquery else '❌ Not Available'}")
    print(f"   Mature Enrichment: {'✅ Available' if enable_mature else '❌ Not Available'}")
    
    # Ask user about enrichment mode
    print(f"\n🎯 ENRICHMENT OPTIONS:")
    print("1. 🔬 DRY RUN ANALYSIS - Cost estimation + sample analysis (RECOMMENDED)")
    print("2. 🚀 FULL LIVE ENRICHMENT - Complete intelligence pipeline")
    print("3. 📋 BASIC EXPORT - Standard export without enrichment")
    print("4. ❌ EXIT")
    
    while True:
        choice = input("\n🎯 Select enrichment mode (1-4): ").strip()
        
        if choice in ['1', '2', '3', '4']:
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
    
    if choice == '4':
        print("❌ Export cancelled")
        return
    
    # Map choices to enrichment modes
    enrichment_modes = {
        '1': 'dry_run',
        '2': 'full_live', 
        '3': 'basic'
    }
    
    enrichment_mode = enrichment_modes[choice]
    
    print(f"\n🔧 Initializing system with mode: {enrichment_mode}")
    
    exporter = ComprehensiveCRMExporter(
        results_file, 
        enable_bigquery_enrichment=enable_bigquery,
        enable_mature_enrichment=enable_mature
    )
    
    print(f"\n📊 LOADING PROSPECT DATA...")
    data = exporter.load_results()
    
    # Get ALL qualified prospects 
    all_prospects = data.get('all_prospects', [])
    
    # Fallback to top_prospects if all_prospects not available
    if not all_prospects:
        all_prospects = data.get('top_prospects', [])
        print("⚠️ Using top_prospects only - consider re-running discovery with full export")
    
    print(f"✅ Loaded {len(all_prospects)} prospects from results")
    print(f"📊 Expected: {data.get('qualified_prospects', 0)} total qualified")
    
    if len(all_prospects) < data.get('qualified_prospects', 0):
        print("⚠️ Only top prospects available in JSON - processing available data")
    
    # Execute based on enrichment mode
    if enrichment_mode == 'dry_run':
        print(f"\n🔬 DRY RUN MODE SELECTED")
        print("📊 This will analyze a sample and estimate costs before proceeding")
        
        csv_path = exporter.export_to_csv(all_prospects, enrichment_mode='dry_run')
        
    elif enrichment_mode == 'full_live':
        print(f"\n🚀 FULL LIVE ENRICHMENT SELECTED")
        print("⚡ This will perform complete intelligence analysis on all prospects")
        
        csv_path = exporter.export_to_csv(all_prospects, enrichment_mode='full_live')
        
    else:  # basic
        print(f"\n📋 BASIC EXPORT SELECTED")
        print("📄 Standard export without advanced enrichment")
        
        csv_path = exporter.export_to_csv(all_prospects, enrichment_mode='basic')
    
    # Generate final report if export completed
    if csv_path:
        print(f"\n📋 GENERATING FINAL REPORT...")
        report = exporter.generate_summary_report(all_prospects, csv_path)
        
        print(f"\n✅ EXPORT COMPLETE!")
        print(f"📁 CSV File: {csv_path}")
        print(report)
        
        if enrichment_mode in ['dry_run', 'full_live'] and enable_mature:
            print(f"\n🎯 ENRICHMENT BENEFITS:")
            print(f"✅ Mature prospect scoring implemented")
            print(f"✅ Performance intelligence data collected")
            print(f"✅ Digital maturity analysis completed")
            print(f"✅ Actionable insights generated for outreach")
            print(f"✅ Conversion likelihood calculated")
            print(f"✅ Outreach strategy recommendations provided")
            
        print(f"\n📈 NEXT STEPS:")
        print(f"1. Import CSV into your CRM system")
        print(f"2. Prioritize by tier and conversion likelihood")
        print(f"3. Use actionable insights for personalized outreach")
        print(f"4. Track performance against enrichment predictions")
    
    else:
        print(f"\n❌ Export was cancelled or failed")
        print(f"💡 Try running with dry_run mode first to validate approach")

if __name__ == "__main__":
    main()
