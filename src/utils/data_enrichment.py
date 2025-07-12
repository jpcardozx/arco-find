#!/usr/bin/env python3
"""
📊 DATA ENRICHMENT UTILITIES - ADVANCED VALIDATION SYSTEM
Professional data enhancement with cross-validation and conflict resolution
Prevents duplicates, resolves data inconsistencies, and provides confidence scoring
"""

import json
import re
import logging
import hashlib
import os
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProspectTracker:
    """Tracks all prospects analyzed in the last 30 days to prevent reprocessing"""
    
    def __init__(self, cache_file_path: str = "cache/analyzed_prospects.json"):
        self.cache_file_path = cache_file_path
        self.cache_dir = os.path.dirname(cache_file_path)
        
        # Ensure cache directory exists
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        self.analyzed_prospects = self._load_cache()
        self._cleanup_old_entries()
    
    def _load_cache(self) -> Dict:
        """Load existing cache from disk"""
        if os.path.exists(self.cache_file_path):
            try:
                with open(self.cache_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading prospect cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save cache to disk"""
        try:
            with open(self.cache_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.analyzed_prospects, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving prospect cache: {e}")
    
    def _cleanup_old_entries(self):
        """Remove entries older than 30 days"""
        cutoff_date = datetime.now() - timedelta(days=30)
        cutoff_str = cutoff_date.isoformat()
        
        old_keys = []
        for key, data in self.analyzed_prospects.items():
            if data.get('analyzed_at', '') < cutoff_str:
                old_keys.append(key)
        
        for key in old_keys:
            del self.analyzed_prospects[key]        
        if old_keys:
            logger.info(f"Cleaned up {len(old_keys)} old prospect entries")
            self._save_cache()
    
    def generate_prospect_key(self, business_data: Dict) -> str:
        """Generate unique key for a prospect"""
        # Use multiple identifiers to create robust key
        website = (business_data.get('website') or '').lower().strip()
        name = (business_data.get('name') or '').lower().strip()
        phone = (business_data.get('phone') or '').strip()
        address = (business_data.get('address') or '').lower().strip()
        
        # Clean website (remove protocol, www, trailing slash)
        if website:
            website = re.sub(r'^https?://', '', website)
            website = re.sub(r'^www\.', '', website)
            website = website.rstrip('/')
        
        # Create composite key
        key_components = [website, name, phone[:10] if phone else '', address[:50]]
        key_str = '|'.join(filter(None, key_components))
        
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def was_analyzed_recently(self, business_data: Dict) -> bool:
        """Check if prospect was analyzed in the last 30 days"""
        key = self.generate_prospect_key(business_data)
        return key in self.analyzed_prospects
    
    def get_previous_analysis(self, business_data: Dict) -> Optional[Dict]:
        """Get previous analysis if it exists"""
        key = self.generate_prospect_key(business_data)
        return self.analyzed_prospects.get(key)
    
    def mark_as_analyzed(self, business_data: Dict, analysis_result: Dict = None):
        """Mark prospect as analyzed with optional result data"""
        key = self.generate_prospect_key(business_data)
        
        self.analyzed_prospects[key] = {
            'analyzed_at': datetime.now().isoformat(),
            'business_name': business_data.get('name', 'Unknown'),
            'website': business_data.get('website', ''),
            'phone': business_data.get('phone', ''),
            'address': business_data.get('address', ''),
            'analysis_result': analysis_result,
            'prospect_key': key
        }
        
        self._save_cache()
        logger.info(f"Marked as analyzed: {business_data.get('name', 'Unknown')}")
    
    def get_analytics(self) -> Dict:
        """Get analytics about analyzed prospects"""
        total_analyzed = len(self.analyzed_prospects)
        recent_24h = 0
        recent_7d = 0
        
        now = datetime.now()
        for data in self.analyzed_prospects.values():
            analyzed_at = datetime.fromisoformat(data['analyzed_at'])
            age = now - analyzed_at
            
            if age.days == 0:
                recent_24h += 1
            if age.days <= 7:
                recent_7d += 1
        
        return {
            'total_analyzed_30d': total_analyzed,
            'analyzed_24h': recent_24h,
            'analyzed_7d': recent_7d,
            'cache_file': self.cache_file_path
        }

@dataclass
class DataValidationResult:
    """Result of data validation with conflict resolution"""
    is_valid: bool
    confidence_score: float  # 0.0 to 1.0
    conflicts_detected: List[Dict]
    resolved_data: Dict
    validation_timestamp: str
    data_sources: List[str]

@dataclass
class BusinessIdentity:
    """Unique business identity for duplicate detection"""
    domain: str
    abn: Optional[str]  # Australian Business Number
    normalized_name: str
    phone_normalized: Optional[str]
    address_normalized: str
    
    def generate_fingerprint(self) -> str:
        """Generate unique fingerprint for duplicate detection"""
        components = [
            self.domain.lower(),
            self.normalized_name.lower(),
            self.phone_normalized or '',
            self.address_normalized.lower()
        ]
        fingerprint_str = '|'.join(components)
        return hashlib.md5(fingerprint_str.encode()).hexdigest()

class DataConflictResolver:
    """Resolve conflicts between different data sources"""
    
    def __init__(self):
        # Source reliability weights (higher = more reliable)
        self.source_weights = {
            'abn_lookup': 1.0,      # Official government data
            'linkedin': 0.9,        # Professional network data
            'asic': 0.9,           # Australian Securities data
            'website_analysis': 0.7, # Our analysis
            'builtwith': 0.6,      # Tech stack detection
            'social_media': 0.5,   # Social media signals
            'market_signals': 0.4  # Inferred signals
        }
        
        # Temporal decay factor (how much to discount old data)
        self.temporal_decay_months = 12
    
    def resolve_size_conflicts(self, data_points: List[Dict]) -> Dict:
        """Resolve conflicts in business size estimation"""
        
        size_votes = {}
        total_weight = 0
        conflicts = []
        
        for point in data_points:
            source = point.get('source', 'unknown')
            size = point.get('size', 'unknown')
            timestamp = point.get('timestamp')
            
            # Calculate source weight
            base_weight = self.source_weights.get(source, 0.3)
            
            # Apply temporal decay
            if timestamp:
                age_months = self._calculate_age_months(timestamp)
                temporal_weight = max(0.1, 1.0 - (age_months / self.temporal_decay_months))
            else:
                temporal_weight = 0.5  # Unknown age gets medium weight
            
            final_weight = base_weight * temporal_weight
            
            if size not in size_votes:
                size_votes[size] = 0
            size_votes[size] += final_weight
            total_weight += final_weight
        
        # Detect conflicts (when top 2 choices are close)
        sorted_votes = sorted(size_votes.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_votes) >= 2:
            top_ratio = sorted_votes[1][1] / sorted_votes[0][1] if sorted_votes[0][1] > 0 else 0
            if top_ratio > 0.7:  # Close competition indicates conflict
                conflicts.append({
                    'type': 'size_estimation',
                    'competing_values': [sorted_votes[0][0], sorted_votes[1][0]],
                    'confidence': 1.0 - top_ratio
                })
        
        # Return most weighted choice
        if sorted_votes:
            resolved_size = sorted_votes[0][0]
            confidence = sorted_votes[0][1] / total_weight if total_weight > 0 else 0.5
        else:
            resolved_size = 'unknown'
            confidence = 0.0
        
        return {
            'resolved_size': resolved_size,
            'confidence': confidence,
            'conflicts': conflicts,
            'vote_distribution': size_votes
        }
    
    def resolve_revenue_conflicts(self, data_points: List[Dict]) -> Dict:
        """Resolve conflicts in revenue estimation"""
        
        # Convert revenue ranges to numeric midpoints for comparison
        revenue_midpoints = {
            '<$100K': 50000,
            '<$500K': 250000,
            '$100K-$500K': 300000,
            '$500K-$2M': 1250000,
            '$2M-$10M': 6000000,
            '$10M-$50M': 30000000,
            '$50M+': 75000000,
            '2M+': 6000000,  # Legacy format
            'unknown': 0
        }
        
        weighted_sum = 0
        total_weight = 0
        conflicts = []
        
        for point in data_points:
            source = point.get('source', 'unknown')
            revenue = point.get('revenue', 'unknown')
            timestamp = point.get('timestamp')
            
            midpoint = revenue_midpoints.get(revenue, 0)
            if midpoint == 0:
                continue
            
            # Calculate weight
            base_weight = self.source_weights.get(source, 0.3)
            if timestamp:
                age_months = self._calculate_age_months(timestamp)
                temporal_weight = max(0.1, 1.0 - (age_months / self.temporal_decay_months))
            else:
                temporal_weight = 0.5
            
            final_weight = base_weight * temporal_weight
            weighted_sum += midpoint * final_weight
            total_weight += final_weight
        
        if total_weight > 0:
            weighted_average = weighted_sum / total_weight
            resolved_revenue = self._midpoint_to_range(weighted_average)
        else:
            resolved_revenue = 'unknown'
            weighted_average = 0
        
        # Check for major conflicts (>5x difference)
        ranges = [revenue_midpoints.get(p.get('revenue', 'unknown'), 0) for p in data_points if revenue_midpoints.get(p.get('revenue', 'unknown'), 0) > 0]
        if ranges:
            max_range = max(ranges)
            min_range = min(ranges)
            if max_range / min_range > 5:
                conflicts.append({
                    'type': 'revenue_estimation',
                    'range_conflict': f"{min_range:,} to {max_range:,}",
                    'ratio': max_range / min_range
                })
        
        return {
            'resolved_revenue': resolved_revenue,
            'weighted_average': weighted_average,
            'confidence': min(1.0, total_weight / 2.0),  # Normalize confidence
            'conflicts': conflicts
        }
    
    def resolve_tech_stack_conflicts(self, data_points: List[Dict]) -> Dict:
        """Resolve conflicts in technology stack detection"""
        
        confirmed_tech = {}
        conflicts = []
        
        for point in data_points:
            source = point.get('source', 'unknown')
            tech_stack = point.get('tech_stack', {})
            
            weight = self.source_weights.get(source, 0.3)
            
            for category, technologies in tech_stack.items():
                if category not in confirmed_tech:
                    confirmed_tech[category] = {}
                
                for tech in technologies:
                    if tech not in confirmed_tech[category]:
                        confirmed_tech[category][tech] = 0
                    confirmed_tech[category][tech] += weight
          # Resolve conflicts (e.g., WordPress + Squarespace)
        cms_detected = confirmed_tech.get('cms', {})
        if len(cms_detected) > 1:
            cms_list = [cms for cms in cms_detected.keys() if cms is not None]
            if (any('wordpress' in cms.lower() for cms in cms_list if cms) and 
                any('squarespace' in cms.lower() for cms in cms_list if cms)):
                conflicts.append({
                    'type': 'multiple_cms',
                    'detected_cms': cms_list,
                    'recommendation': 'Verify primary CMS - may indicate migration or subdomain setup'
                })
        
        # Keep only highest weighted tech in each category
        resolved_tech = {}
        for category, techs in confirmed_tech.items():
            if techs:
                best_tech = max(techs.items(), key=lambda x: x[1])
                if best_tech[1] > 0.5:  # Minimum confidence threshold
                    resolved_tech[category] = [best_tech[0]]
        
        return {
            'resolved_tech_stack': resolved_tech,
            'conflicts': conflicts,
            'confidence_scores': confirmed_tech
        }
    
    def _calculate_age_months(self, timestamp_str: str) -> float:
        """Calculate age in months from timestamp string"""
        try:
            if isinstance(timestamp_str, str):
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = timestamp_str
            
            age_delta = datetime.now() - timestamp.replace(tzinfo=None)
            return age_delta.days / 30.44  # Average days per month
        except:
            return 6.0  # Default to 6 months if parsing fails
    
    def _midpoint_to_range(self, midpoint: float) -> str:
        """Convert numeric midpoint back to revenue range"""
        if midpoint < 75000:
            return '<$100K'
        elif midpoint < 350000:
            return '$100K-$500K'
        elif midpoint < 1500000:
            return '$500K-$2M'
        elif midpoint < 8000000:
            return '$2M-$10M'
        elif midpoint < 40000000:
            return '$10M-$50M'
        else:
            return '$50M+'

class DuplicateDetectionSystem:
    """Prevent duplicate lead processing"""
    
    def __init__(self, storage_path: str = "results/processed_leads.json"):
        self.storage_path = storage_path
        self.processed_leads: Set[str] = set()
        self.business_registry: Dict[str, Dict] = {}
        self._load_processed_leads()
    
    def _load_processed_leads(self):
        """Load previously processed leads"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.processed_leads = set(data.get('fingerprints', []))
                    self.business_registry = data.get('businesses', {})
                logger.info(f"Loaded {len(self.processed_leads)} processed leads from storage")
        except Exception as e:
            logger.warning(f"Could not load processed leads: {e}")
    
    def _save_processed_leads(self):
        """Save processed leads to storage"""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            data = {
                'fingerprints': list(self.processed_leads),
                'businesses': self.business_registry,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save processed leads: {e}")
    
    def normalize_business_name(self, name: str) -> str:
        """Normalize business name for comparison"""        # Remove common business suffixes and normalize
        normalized = re.sub(r'\b(pty|ltd|llc|inc|corp|company|group|solutions|services|consulting|accountants?|tax)\b', '', (name or '').lower())
        normalized = re.sub(r'[^\w\s]', '', normalized)  # Remove punctuation
        normalized = re.sub(r'\s+', ' ', normalized).strip()  # Normalize whitespace
        return normalized
    
    def normalize_phone(self, phone: str) -> Optional[str]:
        """Normalize phone number for comparison"""
        if not phone:
            return None
        # Extract digits only
        digits = re.sub(r'\D', '', phone)
        # Handle Australian format
        if digits.startswith('61') and len(digits) > 10:
            digits = digits[2:]  # Remove country code
        elif digits.startswith('0') and len(digits) == 10:
            digits = digits[1:]  # Remove leading zero
        return digits if len(digits) >= 8 else None
    
    def normalize_address(self, address: str) -> str:
        """Normalize address for comparison"""
        # Basic address normalization
        normalized = re.sub(r'\b(street|st|road|rd|avenue|ave|drive|dr|lane|ln)\b', '', address.lower())
        normalized = re.sub(r'[^\w\s]', '', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    def create_business_identity(self, business_data: Dict) -> BusinessIdentity:
        """Create normalized business identity"""
        website = business_data.get('website', '')
        domain = urlparse(website).netloc.lower() if website else ''
        
        return BusinessIdentity(
            domain=domain,
            abn=business_data.get('abn'),  # If available from ASIC lookup
            normalized_name=self.normalize_business_name(business_data.get('name', '')),
            phone_normalized=self.normalize_phone(business_data.get('phone', '')),
            address_normalized=self.normalize_address(business_data.get('address', ''))
        )
    
    def is_duplicate(self, business_data: Dict) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """Check if business is a duplicate"""
        identity = self.create_business_identity(business_data)
        fingerprint = identity.generate_fingerprint()
        
        # Exact fingerprint match
        if fingerprint in self.processed_leads:
            existing_business = self.business_registry.get(fingerprint)
            return True, fingerprint, existing_business
        
        # Fuzzy matching for similar businesses
        for existing_fingerprint, existing_business in self.business_registry.items():
            similarity = self._calculate_similarity(identity, existing_business)
            if similarity > 0.85:  # High similarity threshold
                logger.warning(f"Potential duplicate detected: {business_data.get('name')} similar to {existing_business.get('name')}")
                return True, existing_fingerprint, existing_business
        
        return False, fingerprint, None
    
    def register_business(self, business_data: Dict, fingerprint: str):
        """Register a new business as processed"""
        self.processed_leads.add(fingerprint)
        self.business_registry[fingerprint] = {
            'name': business_data.get('name'),
            'website': business_data.get('website'),
            'phone': business_data.get('phone'),
            'address': business_data.get('address'),
            'processed_date': datetime.now().isoformat(),
            'business_type': business_data.get('business_type')
        }
        self._save_processed_leads()
    
    def _calculate_similarity(self, identity1: BusinessIdentity, business2: Dict) -> float:
        """Calculate similarity between two businesses"""
        scores = []
        
        # Domain similarity
        if identity1.domain and business2.get('website'):
            domain2 = urlparse(business2['website']).netloc.lower()
            if identity1.domain == domain2:
                scores.append(1.0)
            else:
                scores.append(0.0)
        
        # Name similarity (simple ratio)
        name2_normalized = self.normalize_business_name(business2.get('name', ''))
        if identity1.normalized_name and name2_normalized:
            name_similarity = len(set(identity1.normalized_name.split()) & set(name2_normalized.split())) / len(set(identity1.normalized_name.split()) | set(name2_normalized.split()))
            scores.append(name_similarity)
        
        # Phone similarity
        phone2_normalized = self.normalize_phone(business2.get('phone', ''))
        if identity1.phone_normalized and phone2_normalized:
            scores.append(1.0 if identity1.phone_normalized == phone2_normalized else 0.0)
        
        return sum(scores) / len(scores) if scores else 0.0

@dataclass
class EnrichedBusinessProfile:
    """Comprehensive enriched business profile"""
    # Core business data
    company_name: str
    website: str
    phone: Optional[str]
    address: str
    business_type: str
    
    # Enriched intelligence
    estimated_size: str
    employee_count_range: str
    revenue_estimate: str
    digital_maturity_score: int
    competitive_position: str
    
    # Market intelligence
    industry_context: Dict
    growth_indicators: List[str]
    risk_factors: List[str]
    opportunity_signals: List[str]
    
    # Strategic assessment
    qualification_score: int
    investment_capacity: str
    decision_timeline: str
    strategic_priorities: List[str]

class BusinessSizeClassifier:
    """Classify business size using multiple indicators"""
    
    def __init__(self):
        # Size classification matrix
        self.size_indicators = {
            'website_complexity': {
                'micro': (0, 10),      # Very simple sites
                'small': (10, 50),     # Basic business sites
                'medium': (50, 200),   # Complex business sites
                'large': (200, 1000),  # Enterprise sites
                'enterprise': (1000, float('inf'))
            },
            'content_volume': {
                'micro': (0, 5000),    # Characters
                'small': (5000, 25000),
                'medium': (25000, 100000),
                'large': (100000, 500000),
                'enterprise': (500000, float('inf'))
            },
            'feature_complexity': {
                'micro': (0, 3),       # Number of advanced features
                'small': (3, 8),
                'medium': (8, 15),
                'large': (15, 25),
                'enterprise': (25, float('inf'))
            }
        }
        
        # Employee count mappings
        self.employee_ranges = {
            'micro': '1-5',
            'small': '5-25',
            'medium': '25-100',
            'large': '100-500',
            'enterprise': '500+'
        }
        
        # Revenue estimates (conservative)
        self.revenue_estimates = {
            'micro': '<$500K',
            'small': '$500K-$2M',
            'medium': '$2M-$10M', 
            'large': '$10M-$50M',
            'enterprise': '$50M+'
        }
    
    def classify_by_website_signals(self, website_analysis: Dict) -> str:
        """Classify business size by website indicators"""
        
        # Calculate complexity scores
        complexity_score = 0
        
        # Technology stack complexity
        tech_stack = website_analysis.get('tech_stack', {})
        total_tech = sum(len(category) for category in tech_stack.values())
        complexity_score += total_tech * 2
        
        # Advanced features detected
        advanced_features = 0
        if tech_stack.get('ecommerce'):
            advanced_features += 3
        if tech_stack.get('analytics'):
            advanced_features += 2
        if len(tech_stack.get('javascript', [])) > 1:
            advanced_features += 2
        if tech_stack.get('cms') and 'WordPress' not in tech_stack.get('cms', []):
            advanced_features += 1
        
        complexity_score += advanced_features
        
        # Content analysis (if available)
        content_length = website_analysis.get('content_length', 0)
        if content_length > 100000:
            complexity_score += 10
        elif content_length > 50000:
            complexity_score += 5
        elif content_length > 25000:
            complexity_score += 2
        
        # Classify based on total score
        if complexity_score >= 25:
            return 'large'
        elif complexity_score >= 15:
            return 'medium'
        elif complexity_score >= 8:
            return 'small'
        else:
            return 'micro'
    
    def classify_by_intelligence_data(self, intelligence: Dict) -> str:
        """Classify using business intelligence data"""
        
        # Use intelligence estimates if available
        if intelligence.get('employee_count_estimate'):
            count = intelligence['employee_count_estimate']
            if count >= 100:
                return 'large'
            elif count >= 25:
                return 'medium'
            elif count >= 5:
                return 'small'
            else:
                return 'micro'
          # Use revenue signals
        revenue = intelligence.get('revenue_estimate', '') or ''
        if '$2M+' in revenue or 'enterprise' in revenue.lower():
            return 'large'
        elif '$500K-$2M' in revenue:
            return 'medium'
        elif '$100K-$500K' in revenue:
            return 'small'
        else:
            return 'micro'
    
    def get_final_classification(self, website_analysis: Dict, 
                               intelligence_data: Dict) -> Tuple[str, str, str]:
        """Get final size classification with employee and revenue estimates"""
        
        # Get classifications from different methods
        website_size = self.classify_by_website_signals(website_analysis)
        intelligence_size = self.classify_by_intelligence_data(intelligence_data)
        
        # Weighted decision (intelligence data is more reliable)
        if intelligence_size != 'micro':  # Trust intelligence over website
            final_size = intelligence_size
        else:
            final_size = website_size
        
        # Get corresponding ranges
        employee_range = self.employee_ranges.get(final_size, '1-5')
        revenue_estimate = self.revenue_estimates.get(final_size, '<$500K')
        
        return final_size, employee_range, revenue_estimate

class DigitalMaturityAssessor:
    """Assess digital maturity and competitive positioning"""
    
    def __init__(self):
        # Digital maturity scoring matrix
        self.maturity_factors = {
            'analytics_implementation': {'weight': 20, 'max_score': 20},
            'security_posture': {'weight': 15, 'max_score': 15},
            'performance_optimization': {'weight': 20, 'max_score': 20},
            'mobile_optimization': {'weight': 15, 'max_score': 15},
            'seo_foundation': {'weight': 10, 'max_score': 10},
            'content_strategy': {'weight': 10, 'max_score': 10},
            'technology_modernity': {'weight': 10, 'max_score': 10}
        }
    
    def assess_maturity(self, website_analysis: Dict, 
                       performance_data: Dict, 
                       intelligence_data: Dict) -> int:
        """Calculate digital maturity score (0-100)"""
        
        total_score = 0
        
        # Analytics implementation
        tech_stack = website_analysis.get('tech_stack', {})
        if tech_stack.get('analytics'):
            total_score += 20
        elif 'google' in str(tech_stack).lower():
            total_score += 10
        
        # Security posture
        if website_analysis.get('has_ssl', False):
            total_score += 10
        if 'cloudflare' in str(tech_stack).lower():
            total_score += 5
        
        # Performance optimization
        if performance_data:
            perf_score = performance_data.get('performance_score', 0)
            total_score += min(perf_score // 5, 20)  # Max 20 points
        
        # Mobile optimization (inferred from performance)
        if performance_data and performance_data.get('performance_score', 0) > 80:
            total_score += 15
        elif performance_data and performance_data.get('performance_score', 0) > 60:
            total_score += 10
        elif performance_data and performance_data.get('performance_score', 0) > 40:
            total_score += 5
        
        # SEO foundation
        if performance_data:
            seo_score = performance_data.get('seo_score', 0)
            total_score += min(seo_score // 10, 10)  # Max 10 points
        
        # Content strategy (from intelligence)
        if intelligence_data.get('social_media_presence', {}).get('platforms'):
            platform_count = len(intelligence_data['social_media_presence']['platforms'])
            total_score += min(platform_count * 2, 10)
        
        # Technology modernity
        modern_tech = ['react', 'vue', 'angular', 'next.js']
        if any(tech.lower() in str(tech_stack).lower() for tech in modern_tech):
            total_score += 10
        elif 'javascript' in tech_stack and len(tech_stack['javascript']) > 0:
            total_score += 5
        
        return min(total_score, 100)
    
    def determine_competitive_position(self, maturity_score: int, 
                                     intelligence_data: Dict) -> str:
        """Determine competitive position based on maturity"""
        
        # Base position on maturity score
        if maturity_score >= 80:
            base_position = 'leader'
        elif maturity_score >= 60:
            base_position = 'follower'
        elif maturity_score >= 40:
            base_position = 'laggard'
        else:
            base_position = 'vulnerable'
        
        # Adjust based on competitive intelligence
        competitive_data = intelligence_data.get('competitive_positioning', {})
        if competitive_data.get('position') == 'challenging':
            # Downgrade position if facing strong competition
            position_hierarchy = ['leader', 'follower', 'laggard', 'vulnerable']
            current_index = position_hierarchy.index(base_position)
            if current_index < len(position_hierarchy) - 1:
                base_position = position_hierarchy[current_index + 1]
        
        return base_position

class StrategicAssessmentEngine:
    """Assess strategic priorities and investment capacity"""
    
    def __init__(self):
        # Investment capacity indicators
        self.investment_indicators = {
            'high': {
                'business_size': ['large', 'enterprise'],
                'maturity_score': (60, 100),
                'growth_signals': 3
            },
            'medium': {
                'business_size': ['medium', 'large'],
                'maturity_score': (40, 80),
                'growth_signals': 1
            },
            'low': {
                'business_size': ['micro', 'small'],
                'maturity_score': (0, 60),
                'growth_signals': 0
            }
        }
    
    def assess_investment_capacity(self, business_size: str, 
                                 maturity_score: int,
                                 intelligence_data: Dict) -> str:
        """Assess investment capacity for digital initiatives"""
        
        # Count growth signals
        growth_signals = len(intelligence_data.get('market_signals', []))
        
        # Score against indicators
        capacity_scores = {}
        
        for capacity, indicators in self.investment_indicators.items():
            score = 0
            
            # Business size match
            if business_size in indicators['business_size']:
                score += 3
            
            # Maturity score range
            min_maturity, max_maturity = indicators['maturity_score']
            if min_maturity <= maturity_score <= max_maturity:
                score += 2
            
            # Growth signals
            if growth_signals >= indicators['growth_signals']:
                score += 1
            
            capacity_scores[capacity] = score
        
        # Return highest scoring capacity
        return max(capacity_scores.items(), key=lambda x: x[1])[0]
    
    def determine_strategic_priorities(self, maturity_score: int,
                                     competitive_position: str,
                                     business_size: str) -> List[str]:
        """Determine strategic priorities based on assessment"""
        
        priorities = []
        
        # Maturity-based priorities
        if maturity_score < 40:
            priorities.extend([
                'Digital foundation establishment',
                'Basic security implementation',
                'Performance optimization'
            ])
        elif maturity_score < 70:
            priorities.extend([
                'Competitive differentiation',
                'Customer experience enhancement',
                'Marketing automation'
            ])
        else:
            priorities.extend([
                'Market leadership establishment',
                'Innovation implementation',
                'Advanced analytics'
            ])
        
        # Position-based priorities
        if competitive_position in ['laggard', 'vulnerable']:
            priorities.insert(0, 'Urgent competitive catch-up')
        elif competitive_position == 'leader':
            priorities.append('Market leadership maintenance')
        
        # Size-based priorities
        if business_size in ['large', 'enterprise']:
            priorities.append('Scalability and integration')
        elif business_size == 'micro':
            priorities.insert(0, 'Essential business tools')
        
        return priorities[:5]  # Top 5 priorities
    
    def calculate_qualification_score(self, investment_capacity: str,
                                    strategic_priorities: List[str],
                                    maturity_score: int) -> int:
        """Calculate overall lead qualification score"""
        
        score = 0
        
        # Investment capacity scoring
        capacity_scores = {'high': 40, 'medium': 25, 'low': 10}
        score += capacity_scores.get(investment_capacity, 10)
          # Strategic urgency scoring
        urgent_keywords = ['urgent', 'competitive', 'foundation', 'essential']
        urgency_score = sum(1 for priority in strategic_priorities 
                          for keyword in urgent_keywords 
                          if priority and keyword in priority.lower())
        score += min(urgency_score * 10, 30)
        
        # Maturity gap scoring (bigger gap = higher opportunity)
        maturity_gap = 100 - maturity_score
        score += min(maturity_gap // 3, 30)
        
        return min(score, 100)

class DataEnrichmentOrchestrator:
    """Orchestrate the complete data enrichment process"""
    
    def __init__(self):
        self.size_classifier = BusinessSizeClassifier()
        self.maturity_assessor = DigitalMaturityAssessor()
        self.strategic_assessor = StrategicAssessmentEngine()
        self.duplicate_detector = DuplicateDetectionSystem()
        self.conflict_resolver = DataConflictResolver()
    
    def enrich_business_profile(self, basic_profile: Dict,
                              website_analysis: Dict,
                              performance_data: Optional[Dict],
                              intelligence_data: Optional[Dict]) -> EnrichedBusinessProfile:
        """Create comprehensive enriched business profile"""
        
        logger.info(f"🔍 Enriching profile for {basic_profile.get('name')}")
        
        # Handle missing data gracefully
        if not intelligence_data:
            intelligence_data = {'market_signals': [], 'competitive_positioning': {}}
        if not performance_data:
            performance_data = {'performance_score': 50, 'seo_score': 50}
        
        # Business size classification
        business_size, employee_range, revenue_estimate = self.size_classifier.get_final_classification(
            website_analysis, intelligence_data
        )
        
        # Digital maturity assessment
        maturity_score = self.maturity_assessor.assess_maturity(
            website_analysis, performance_data, intelligence_data
        )
        
        # Competitive positioning
        competitive_position = self.maturity_assessor.determine_competitive_position(
            maturity_score, intelligence_data
        )
        
        # Strategic assessment
        investment_capacity = self.strategic_assessor.assess_investment_capacity(
            business_size, maturity_score, intelligence_data
        )
        
        strategic_priorities = self.strategic_assessor.determine_strategic_priorities(
            maturity_score, competitive_position, business_size
        )
        
        qualification_score = self.strategic_assessor.calculate_qualification_score(
            investment_capacity, strategic_priorities, maturity_score
        )
        
        # Generate insights
        growth_indicators = intelligence_data.get('market_signals', [])
        risk_factors = self._identify_risk_factors(maturity_score, competitive_position)
        opportunity_signals = self._identify_opportunity_signals(
            maturity_score, business_size, strategic_priorities
        )
        
        # Create industry context
        industry_context = self._create_industry_context(
            basic_profile.get('business_type', ''), competitive_position
        )
        
        # Determine decision timeline
        decision_timeline = self._estimate_decision_timeline(
            qualification_score, investment_capacity, len(strategic_priorities)
        )
        
        enriched_profile = EnrichedBusinessProfile(
            company_name=basic_profile.get('name', ''),
            website=basic_profile.get('website', ''),
            phone=basic_profile.get('phone'),
            address=basic_profile.get('address', ''),
            business_type=basic_profile.get('business_type', ''),
            estimated_size=business_size,
            employee_count_range=employee_range,
            revenue_estimate=revenue_estimate,
            digital_maturity_score=maturity_score,
            competitive_position=competitive_position,
            industry_context=industry_context,
            growth_indicators=growth_indicators,
            risk_factors=risk_factors,
            opportunity_signals=opportunity_signals,
            qualification_score=qualification_score,
            investment_capacity=investment_capacity,
            decision_timeline=decision_timeline,
            strategic_priorities=strategic_priorities
        )
        
        # Validate and resolve conflicts
        self._validate_and_resolve(enriched_profile, intelligence_data)
        
        return enriched_profile
    
    def _validate_and_resolve(self, profile: EnrichedBusinessProfile, intelligence_data: Dict):
        """Validate profile data and resolve conflicts"""
        logger.info(f"Validating and resolving conflicts for {profile.company_name}")
        
        # Conflict detection examples (expand as needed)
        conflicts = []
        
        # Size and revenue conflicts
        if profile.estimated_size == 'micro' and profile.revenue_estimate != '<$500K':
            conflicts.append({
                'type': 'revenue_size_mismatch',
                'revenue': profile.revenue_estimate,
                'size': profile.estimated_size
            })
        
        # Strategic priority conflicts
        if 'Urgent competitive catch-up' in profile.strategic_priorities and profile.digital_maturity_score > 50:
            conflicts.append({
                'type': 'strategic_priority_conflict',
                'priority': 'Urgent competitive catch-up',
                'maturity_score': profile.digital_maturity_score
            })
        
        # Log conflicts
        for conflict in conflicts:
            logger.warning(f"Conflict detected: {conflict}")
        
        # Conflict resolution logic (expand as needed)
        if conflicts:
            # Example resolution: adjust size based on revenue
            if profile.revenue_estimate == 'unknown' and profile.employee_count_range != '1-5':
                logger.info("Resolving size conflict by adjusting estimated size based on employee count range")
                profile.estimated_size = 'small'
            
            # Recalculate strategic priorities
            profile.strategic_priorities = self.strategic_assessor.determine_strategic_priorities(
                profile.digital_maturity_score, profile.competitive_position, profile.estimated_size
            )
            
            logger.info("Recalculated strategic priorities after conflict resolution")
        
        # Register business to prevent duplicates
        fingerprint = profile.company_name.lower() + profile.website.lower()
        is_duplicate, existing_fingerprint, existing_profile = self.duplicate_detector.is_duplicate({
            'name': profile.company_name,
            'website': profile.website,
            'phone': profile.phone,
            'address': profile.address
        })
        
        if is_duplicate:
            logger.warning(f"Duplicate detected: {profile.company_name} - {existing_profile}")
            # Merge or choose existing profile logic here
            # NOTE: Don't overwrite profile object with dict - keep the original object
            pass  # For now, just log the duplicate but keep using the current profile
        else:
            # Register new business
            self.duplicate_detector.register_business(asdict(profile), fingerprint)
        
        logger.info(f"Enrichment and validation complete for {profile.company_name}")
    
    def _identify_risk_factors(self, maturity_score: int, competitive_position: str) -> List[str]:
        """Identify business risk factors"""
        risks = []
        
        if maturity_score < 30:
            risks.append('Critical digital infrastructure gaps')
        
        if competitive_position in ['laggard', 'vulnerable']:
            risks.append('Competitive displacement risk')
        
        if maturity_score < 50:
            risks.append('Customer experience deficiencies')
        
        return risks
    
    def _identify_opportunity_signals(self, maturity_score: int, 
                                   business_size: str, 
                                   strategic_priorities: List[str]) -> List[str]:
        """Identify business opportunity signals"""
        opportunities = []
        
        if maturity_score < 70:
            opportunities.append('Significant digital improvement potential')
        
        if business_size in ['medium', 'large']:
            opportunities.append('Scale advantages through technology')
        
        if any('competitive' in priority.lower() for priority in strategic_priorities if priority):
            opportunities.append('Competitive differentiation opportunity')
        
        return opportunities
    
    def _create_industry_context(self, business_type: str, competitive_position: str) -> Dict:
        """Create industry context analysis"""
        return {
            'industry': business_type,
            'digital_adoption_level': 'medium',  # Would be industry-specific
            'competitive_intensity': 'high' if competitive_position in ['laggard', 'vulnerable'] else 'medium',
            'technology_expectations': 'increasing'
        }
    
    def _estimate_decision_timeline(self, qualification_score: int,
                                  investment_capacity: str,
                                  priority_count: int) -> str:
        """Estimate decision-making timeline"""
        
        if qualification_score > 80 and investment_capacity == 'high':
            return '2-4 weeks'
        elif qualification_score > 60 and investment_capacity in ['medium', 'high']:
            return '1-2 months'
        elif qualification_score > 40:
            return '2-4 months'
        else:
            return '6+ months'

class EnhancedDataEnrichmentOrchestrator:
    """Advanced data enrichment with validation and conflict resolution"""
    
    def __init__(self):
        self.size_classifier = BusinessSizeClassifier()
        self.maturity_assessor = DigitalMaturityAssessor()
        self.strategic_assessor = StrategicAssessmentEngine()
        self.conflict_resolver = DataConflictResolver()
        self.duplicate_detector = DuplicateDetectionSystem()
        self.prospect_tracker = ProspectTracker()  # Track analyzed prospects        
        # Data source tracking
        self.data_sources = []
    
    def enrich_business_profile_with_validation(self, basic_profile: Dict, 
                                              website_analysis: Dict,
                                              performance_data: Dict, 
                                              intelligence_data: Dict) -> Tuple[EnrichedBusinessProfile, DataValidationResult]:
        """Enrich business profile with comprehensive validation"""
        
        # FIRST: Check if we already analyzed this prospect recently
        if self.prospect_tracker.was_analyzed_recently(basic_profile):
            previous_analysis = self.prospect_tracker.get_previous_analysis(basic_profile)
            logger.info(f"🔄 SKIPPING REANALYSIS: {basic_profile.get('name')} - Already analyzed on {previous_analysis['analyzed_at'][:10]}")
            
            # Return cached result if available
            if previous_analysis.get('analysis_result'):
                cached_result = previous_analysis['analysis_result']
                return None, DataValidationResult(
                    is_valid=False,
                    confidence_score=0.0,
                    conflicts_detected=[{'type': 'info', 'details': 'Prospect already analyzed recently - skipping to avoid duplicate work'}],
                    resolved_data={},
                    validation_timestamp=datetime.now().isoformat(),
                    data_sources=['prospect_cache']
                )
        
        # Check for duplicates 
        is_duplicate, fingerprint, existing_business = self.duplicate_detector.is_duplicate(basic_profile)
        if is_duplicate:
            logger.warning(f"Duplicate business detected: {basic_profile.get('name')} (fingerprint: {fingerprint})")
            
            # Mark as analyzed to prevent future reprocessing
            self.prospect_tracker.mark_as_analyzed(basic_profile, {
                'status': 'duplicate',
                'duplicate_of': existing_business.get('company_name') if existing_business else 'unknown'
            })
            
            return None, DataValidationResult(
                is_valid=False,
                confidence_score=0.0,
                conflicts_detected=[{'type': 'duplicate', 'existing_business': existing_business}],
                resolved_data={},
                validation_timestamp=datetime.now().isoformat(),
                data_sources=[]
            )
        
        # Collect data points from multiple sources
        size_data_points = self._collect_size_data_points(basic_profile, website_analysis, intelligence_data)
        revenue_data_points = self._collect_revenue_data_points(basic_profile, intelligence_data)
        tech_data_points = self._collect_tech_data_points(website_analysis)
        
        # Resolve conflicts
        size_resolution = self.conflict_resolver.resolve_size_conflicts(size_data_points)
        revenue_resolution = self.conflict_resolver.resolve_revenue_conflicts(revenue_data_points)
        tech_resolution = self.conflict_resolver.resolve_tech_stack_conflicts(tech_data_points)
        
        # Collect all conflicts
        all_conflicts = []
        all_conflicts.extend(size_resolution.get('conflicts', []))
        all_conflicts.extend(revenue_resolution.get('conflicts', []))
        all_conflicts.extend(tech_resolution.get('conflicts', []))
        
        # Perform cross-field sanity checks
        sanity_conflicts = self._perform_sanity_checks(size_resolution, revenue_resolution, intelligence_data)
        all_conflicts.extend(sanity_conflicts)
        
        # Calculate overall confidence
        confidence_scores = [
            size_resolution.get('confidence', 0.5),
            revenue_resolution.get('confidence', 0.5),
            tech_resolution.get('confidence', 0.5)
        ]
        overall_confidence = sum(confidence_scores) / len(confidence_scores)
        
        # Apply conflict penalty
        if all_conflicts:
            conflict_penalty = min(0.3, len(all_conflicts) * 0.1)
            overall_confidence = max(0.1, overall_confidence - conflict_penalty)
        
        # Determine if data is valid enough to proceed
        is_valid = overall_confidence >= 0.6 and len([c for c in all_conflicts if c.get('type') == 'critical']) == 0
        
        if not is_valid:
            logger.warning(f"Data validation failed for {basic_profile.get('name')}: confidence={overall_confidence:.2f}, conflicts={len(all_conflicts)}")
            return None, DataValidationResult(
                is_valid=False,
                confidence_score=overall_confidence,
                conflicts_detected=all_conflicts,
                resolved_data={},
                validation_timestamp=datetime.now().isoformat(),
                data_sources=self.data_sources
            )
        
        # Build resolved data
        resolved_data = {
            'business_size': size_resolution['resolved_size'],
            'revenue_estimate': revenue_resolution['resolved_revenue'],
            'tech_stack': tech_resolution['resolved_tech_stack'],
            'employee_count_range': self.size_classifier.employee_ranges.get(size_resolution['resolved_size'], '1-5')
        }
        
        # Continue with standard enrichment using resolved data
        enriched_profile = self._build_enriched_profile(
            basic_profile, website_analysis, performance_data, 
            intelligence_data, resolved_data
        )
          # Register business as processed
        if fingerprint:
            self.duplicate_detector.register_business(basic_profile, fingerprint)
        
        validation_result = DataValidationResult(
            is_valid=True,
            confidence_score=overall_confidence,
            conflicts_detected=all_conflicts,
            resolved_data=resolved_data,
            validation_timestamp=datetime.now().isoformat(),
            data_sources=self.data_sources
        )
        
        # 🔥 CRITICAL: Mark prospect as analyzed to prevent future reprocessing
        analysis_summary = {
            'status': 'completed',
            'qualification_score': enriched_profile.qualification_score,
            'confidence_score': overall_confidence,
            'business_size': resolved_data.get('business_size'),
            'revenue_estimate': resolved_data.get('revenue_estimate'),
            'conflicts_count': len(all_conflicts),
            'critical_conflicts': len([c for c in all_conflicts if c.get('type') == 'critical'])
        }
        self.prospect_tracker.mark_as_analyzed(basic_profile, analysis_summary)
        
        return enriched_profile, validation_result
    
    def _collect_size_data_points(self, basic_profile: Dict, website_analysis: Dict, intelligence_data: Dict) -> List[Dict]:
        """Collect business size data points from all sources"""
        data_points = []
        
        # From website analysis
        website_size = self.size_classifier.classify_by_website_signals(website_analysis)
        data_points.append({
            'source': 'website_analysis',
            'size': website_size,
            'timestamp': datetime.now().isoformat(),
            'confidence': 0.7
        })
        
        # From intelligence data
        if intelligence_data.get('employee_count_estimate'):
            emp_count = intelligence_data['employee_count_estimate']
            if emp_count >= 100:
                intel_size = 'large'
            elif emp_count >= 25:
                intel_size = 'medium'
            elif emp_count >= 5:
                intel_size = 'small'
            else:
                intel_size = 'micro'
            
            data_points.append({
                'source': 'linkedin',  # Assuming this comes from LinkedIn-style data
                'size': intel_size,
                'timestamp': datetime.now().isoformat(),
                'confidence': 0.9
            })
        
        # From basic profile (if contains size indicators)
        profile_size = basic_profile.get('estimated_size')
        if profile_size:
            data_points.append({
                'source': 'places_api',
                'size': profile_size,
                'timestamp': datetime.now().isoformat(),
                'confidence': 0.6
            })
        
        return data_points
    
    def _collect_revenue_data_points(self, basic_profile: Dict, intelligence_data: Dict) -> List[Dict]:
        """Collect revenue estimation data points"""
        data_points = []
        
        # From intelligence data
        intel_revenue = intelligence_data.get('revenue_estimate')
        if intel_revenue:
            data_points.append({
                'source': 'market_signals',
                'revenue': intel_revenue,
                'timestamp': datetime.now().isoformat(),
                'confidence': 0.5
            })
        
        # From basic profile
        profile_revenue = basic_profile.get('estimated_revenue')
        if profile_revenue:
            data_points.append({
                'source': 'places_api',
                'revenue': profile_revenue,
                'timestamp': datetime.now().isoformat(),
                'confidence': 0.6
            })
        
        return data_points
    
    def _collect_tech_data_points(self, website_analysis: Dict) -> List[Dict]:
        """Collect technology stack data points"""
        data_points = []
        
        tech_stack = website_analysis.get('tech_stack', {})
        if tech_stack:
            data_points.append({
                'source': 'builtwith',
                'tech_stack': tech_stack,
                'timestamp': datetime.now().isoformat(),
                'confidence': 0.8
            })
        
        return data_points
    
    def _perform_sanity_checks(self, size_resolution: Dict, revenue_resolution: Dict, intelligence_data: Dict) -> List[Dict]:
        """Perform cross-field sanity checks"""
        conflicts = []
        
        resolved_size = size_resolution.get('resolved_size', 'unknown')
        resolved_revenue = revenue_resolution.get('resolved_revenue', 'unknown')
        employee_count = intelligence_data.get('employee_count_estimate', 0)
        
        # Size vs Employee Count sanity check
        if employee_count and resolved_size:
            expected_ranges = {
                'micro': (1, 5),
                'small': (5, 25),
                'medium': (25, 100),
                'large': (100, 500),
                'enterprise': (500, float('inf'))
            }
            
            expected_range = expected_ranges.get(resolved_size, (1, 5))
            if not (expected_range[0] <= employee_count <= expected_range[1]):
                conflicts.append({
                    'type': 'critical',
                    'category': 'size_employee_mismatch',
                    'details': f"Size '{resolved_size}' conflicts with {employee_count} employees",
                    'recommendation': 'Manual review required - use employee count as primary source'
                })
        
        # Size vs Revenue sanity check
        if resolved_size != 'unknown' and resolved_revenue != 'unknown':
            size_revenue_expectations = {
                'micro': ['<$100K', '<$500K'],
                'small': ['<$500K', '$100K-$500K', '$500K-$2M'],
                'medium': ['$500K-$2M', '$2M-$10M'],
                'large': ['$2M-$10M', '$10M-$50M'],
                'enterprise': ['$10M-$50M', '$50M+']
            }
            
            expected_revenues = size_revenue_expectations.get(resolved_size, [])
            if resolved_revenue not in expected_revenues:
                conflicts.append({
                    'type': 'warning',
                    'category': 'size_revenue_mismatch',
                    'details': f"Size '{resolved_size}' typically doesn't match revenue '{resolved_revenue}'",
                    'recommendation': 'Verify business model - may be high-margin or low-margin operation'
                })
        
        # Growth signals vs competitive position check
        growth_signals = intelligence_data.get('market_signals', [])
        competitive_position = intelligence_data.get('competitive_positioning', {}).get('position', 'unknown')
        
        growth_indicators = [signal for signal in growth_signals if any(keyword in signal.lower() for keyword in ['growth', 'hiring', 'expansion', 'award'])]
        
        if growth_indicators and competitive_position == 'laggard':
            conflicts.append({
                'type': 'warning',
                'category': 'growth_position_mismatch',
                'details': f"Growth signals detected but competitive position marked as 'laggard'",
                'recommendation': 'Check data timestamps - growth may be recent, position assessment may be outdated'
            })
        
        return conflicts
    
    def _build_enriched_profile(self, basic_profile: Dict, website_analysis: Dict, 
                              performance_data: Dict, intelligence_data: Dict, 
                              resolved_data: Dict) -> EnrichedBusinessProfile:
        """Build enriched profile using resolved data"""
        
        # Use resolved data where available, fall back to original enrichment logic
        business_size = resolved_data.get('business_size', 'small')
        revenue_estimate = resolved_data.get('revenue_estimate', '<$500K')
        employee_range = resolved_data.get('employee_count_range', '1-5')
        
        # Calculate digital maturity
        maturity_score = self.maturity_assessor.assess_maturity(
            website_analysis, performance_data, intelligence_data
        )
        
        # Determine competitive position
        competitive_position = self._determine_competitive_position(maturity_score, intelligence_data)
        
        # Assess investment capacity
        investment_capacity = self.strategic_assessor.assess_investment_capacity(
            business_size, maturity_score, intelligence_data
        )
        
        # Generate strategic priorities
        strategic_priorities = self.strategic_assessor.determine_strategic_priorities(
            maturity_score, competitive_position, business_size
        )
        
        # Calculate qualification score
        qualification_score = self.strategic_assessor.calculate_qualification_score(
            investment_capacity, strategic_priorities, maturity_score
        )
        
        return EnrichedBusinessProfile(
            company_name=basic_profile.get('name', 'Unknown'),
            website=basic_profile.get('website', ''),
            phone=basic_profile.get('phone'),
            address=basic_profile.get('address', ''),
            business_type=basic_profile.get('business_type', ''),
            estimated_size=business_size,
            employee_count_range=employee_range,
            revenue_estimate=revenue_estimate,
            digital_maturity_score=maturity_score,
            competitive_position=competitive_position,
            industry_context={},  # Could be enhanced
            growth_indicators=intelligence_data.get('market_signals', []),
            risk_factors=[],  # Could be enhanced
            opportunity_signals=[],  # Could be enhanced
            qualification_score=qualification_score,
            investment_capacity=investment_capacity,
            decision_timeline=self._estimate_decision_timeline(investment_capacity, maturity_score),
            strategic_priorities=strategic_priorities
        )
    
    def _determine_competitive_position(self, maturity_score: int, intelligence_data: Dict) -> str:
        """Determine competitive position based on maturity and signals"""
        if maturity_score >= 80:
            return 'leader'
        elif maturity_score >= 60:
            return 'follower'
        elif maturity_score >= 40:
            return 'laggard'
        else:
            return 'vulnerable'
    
    def _estimate_decision_timeline(self, investment_capacity: str, maturity_score: int) -> str:
        """Estimate decision timeline based on capacity and urgency"""
        if investment_capacity == 'high' and maturity_score < 40:
            return '1-2 weeks'
        elif investment_capacity in ['high', 'medium'] and maturity_score < 60:
            return '2-4 weeks'
        elif investment_capacity == 'medium':
            return '1-2 months'
        else:
            return '3-6 months'

# Demo function
def demo_data_enrichment():
    """Demo the data enrichment system"""
    print("📊" + "="*60)
    print("   DATA ENRICHMENT DEMO")
    print("="*63)
    
    orchestrator = DataEnrichmentOrchestrator()
    
    # Test profile
    basic_profile = {
        'name': 'Test Restaurant Ltd',
        'website': 'https://testrestaurant.com',
        'phone': '+1-555-0123',
        'address': '123 Main St, Toronto, ON',
        'business_type': 'restaurant'
    }
    
    website_analysis = {
        'tech_stack': {
            'cms': ['WordPress'],
            'analytics': ['Google Analytics'],
            'javascript': ['jQuery']
        },
        'has_ssl': True,
        'content_length': 25000
    }
    
    performance_data = {
        'performance_score': 65,
        'seo_score': 75
    }
    
    intelligence_data = {
        'employee_count_estimate': 15,
        'revenue_estimate': '$500K-$2M',
        'market_signals': ['Growth indicators found', 'Active social media'],
        'competitive_positioning': {'position': 'competitive'}
    }
    
    # Enrich profile
    enriched = orchestrator.enrich_business_profile(
        basic_profile, website_analysis, performance_data, intelligence_data
    )
    
    print(f"🏢 Company: {enriched.company_name}")
    print(f"   • Size: {enriched.estimated_size} ({enriched.employee_count_range} employees)")
    print(f"   • Revenue: {enriched.revenue_estimate}")
    print(f"   • Digital Maturity: {enriched.digital_maturity_score}/100")
    print(f"   • Competitive Position: {enriched.competitive_position}")
    print(f"   • Investment Capacity: {enriched.investment_capacity}")
    print(f"   • Qualification Score: {enriched.qualification_score}/100")
    print(f"   • Decision Timeline: {enriched.decision_timeline}")
    print(f"   • Top Priority: {enriched.strategic_priorities[0] if enriched.strategic_priorities else 'None'}")
    
    print("\n" + "="*63)
    print("   DATA ENRICHMENT DEMO COMPLETE")
    print("="*63)

if __name__ == "__main__":
    demo_data_enrichment()