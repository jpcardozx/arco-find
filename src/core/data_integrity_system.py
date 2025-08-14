"""
ARCO Find: Entity Resolution and Quality Control System
Professional-grade data integrity and validation pipeline
"""

import hashlib
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse
import difflib
import logging

logger = logging.getLogger(__name__)

@dataclass
class EntityProfile:
    """Standardized entity representation with quality metrics"""
    domain: str
    company_name: str
    vertical: str
    region: str
    confidence_score: float
    data_sources: List[str]
    first_discovered: str
    last_updated: str
    validation_status: str

class EntityResolver:
    """Enterprise-grade entity deduplication and resolution system"""
    
    def __init__(self):
        self.master_entities = {}
        self.domain_aliases = {}
        self.company_name_variants = {}
        
    def normalize_domain(self, domain: str) -> str:
        """Normalize domain for consistent matching"""
        if not domain:
            return ""
        
        # Remove protocol and www
        domain = domain.lower().strip()
        domain = re.sub(r'^https?://', '', domain)
        domain = re.sub(r'^www\.', '', domain)
        domain = domain.split('/')[0]  # Remove path
        
        return domain
    
    def normalize_company_name(self, name: str) -> str:
        """Normalize company name for fuzzy matching"""
        if not name:
            return ""
        
        # Remove common business suffixes and normalize
        name = name.lower().strip()
        suffixes = ['inc', 'llc', 'ltd', 'corp', 'corporation', 'company', 'co', '&', 'and']
        
        for suffix in suffixes:
            name = re.sub(f'\\b{suffix}\\b', '', name)
        
        # Remove special characters and extra spaces
        name = re.sub(r'[^\w\s]', '', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between company names"""
        norm1 = self.normalize_company_name(name1)
        norm2 = self.normalize_company_name(name2)
        
        if not norm1 or not norm2:
            return 0.0
        
        return difflib.SequenceMatcher(None, norm1, norm2).ratio()
    
    def generate_entity_key(self, domain: str, company_name: str) -> str:
        """Generate unique key for entity identification"""
        normalized_domain = self.normalize_domain(domain)
        normalized_name = self.normalize_company_name(company_name)
        
        # Use domain as primary key, fallback to normalized name
        if normalized_domain:
            return f"domain:{normalized_domain}"
        elif normalized_name:
            return f"name:{hashlib.md5(normalized_name.encode()).hexdigest()[:12]}"
        else:
            return f"unknown:{hashlib.md5(str(hash(f'{domain}{company_name}')).encode()).hexdigest()[:12]}"
    
    def resolve_entity(self, prospect: dict) -> dict:
        """Resolve entity to master record or create new one"""
        domain = prospect.get('domain', '')
        company_name = prospect.get('company_name', '')
        vertical = prospect.get('vertical', '')
        region = prospect.get('region', '')
        
        entity_key = self.generate_entity_key(domain, company_name)
        
        if entity_key in self.master_entities:
            # Update existing entity
            entity = self.master_entities[entity_key]
            entity.last_updated = self._get_timestamp()
            entity.data_sources = list(set(entity.data_sources + ['current_analysis']))
            
            # Validate consistency
            if entity.vertical != vertical:
                logger.warning(f"Vertical mismatch for {entity_key}: {entity.vertical} vs {vertical}")
                entity.confidence_score *= 0.9
            
            # Return updated prospect with entity data
            updated_prospect = prospect.copy()
            updated_prospect.update({
                'entity_id': entity_key,
                'normalized_domain': entity.domain,
                'normalized_name': entity.company_name,
                'entity_confidence': entity.confidence_score
            })
            return updated_prospect
        else:
            # Create new entity
            entity = EntityProfile(
                domain=self.normalize_domain(domain),
                company_name=company_name,
                vertical=vertical,
                region=region,
                confidence_score=0.8,
                data_sources=['current_analysis'],
                first_discovered=self._get_timestamp(),
                last_updated=self._get_timestamp(),
                validation_status='pending'
            )
            
            self.master_entities[entity_key] = entity
            
            # Return prospect with new entity data
            updated_prospect = prospect.copy()
            updated_prospect.update({
                'entity_id': entity_key,
                'normalized_domain': entity.domain,
                'normalized_name': entity.company_name,
                'entity_confidence': entity.confidence_score
            })
            return updated_prospect
    
    def remove_duplicates(self, prospects: List[Dict]) -> List[Dict]:
        """Remove duplicate prospects from list"""
        seen_entities = set()
        unique_prospects = []
        
        for prospect in prospects:
            domain = prospect.get('domain', '')
            company_name = prospect.get('company_name', '')
            entity_key = self.generate_entity_key(domain, company_name)
            
            if entity_key not in seen_entities:
                seen_entities.add(entity_key)
                unique_prospects.append(prospect)
        
        logger.info(f"Removed {len(prospects) - len(unique_prospects)} duplicates")
        return unique_prospects
    
    def detect_duplicates(self, prospects: List[Dict]) -> List[Tuple[int, int, float]]:
        """Detect duplicate prospects in dataset"""
        duplicates = []
        
        for i, prospect1 in enumerate(prospects):
            for j, prospect2 in enumerate(prospects[i+1:], i+1):
                similarity_score = self._calculate_prospect_similarity(prospect1, prospect2)
                
                if similarity_score > 0.85:  # High similarity threshold
                    duplicates.append((i, j, similarity_score))
        
        return duplicates
    
    def _calculate_prospect_similarity(self, prospect1: Dict, prospect2: Dict) -> float:
        """Calculate overall similarity between two prospects"""
        domain1 = self.normalize_domain(prospect1.get('domain', ''))
        domain2 = self.normalize_domain(prospect2.get('domain', ''))
        
        # If domains match exactly, it's the same entity
        if domain1 and domain2 and domain1 == domain2:
            return 1.0
        
        # Calculate name similarity
        name_sim = self.calculate_name_similarity(
            prospect1.get('company_name', ''),
            prospect2.get('company_name', '')
        )
        
        # Calculate other attribute similarities
        vertical_match = 1.0 if prospect1.get('vertical') == prospect2.get('vertical') else 0.0
        region_match = 1.0 if prospect1.get('region') == prospect2.get('region') else 0.0
        
        # Weighted similarity score
        weights = {'name': 0.6, 'vertical': 0.2, 'region': 0.2}
        total_similarity = (
            name_sim * weights['name'] +
            vertical_match * weights['vertical'] +
            region_match * weights['region']
        )
        
        return total_similarity
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for tracking"""
        from datetime import datetime
        return datetime.now().isoformat()

class QualityController:
    """Quality assessment and validation system"""
    
    def __init__(self):
        self.quality_thresholds = {
            'entity_validity': 0.8,
            'vertical_alignment': 0.9,
            'financial_realism': 0.7,
            'contact_probability': 0.6,
            'competitive_context': 0.5
        }
    
    def assess_quality(self, prospect: Dict) -> Dict[str, float]:
        """Main quality assessment method"""
        return self.calculate_quality_score(prospect)
    
    def calculate_quality_score(self, prospect: Dict) -> Dict[str, float]:
        """Calculate comprehensive quality score for prospect"""
        scores = {
            'entity_validity': self.validate_business(prospect),
            'vertical_alignment': self.verify_vertical_classification(prospect),
            'financial_realism': self.validate_spend_patterns(prospect),
            'contact_probability': self.assess_contact_likelihood(prospect),
            'competitive_context': self.evaluate_market_position(prospect)
        }
        
        # Calculate weighted overall score
        weights = {
            'entity_validity': 0.25,
            'vertical_alignment': 0.20,
            'financial_realism': 0.25,
            'contact_probability': 0.20,
            'competitive_context': 0.10
        }
        
        overall_score = sum(scores[metric] * weights[metric] for metric in scores)
        scores['overall_score'] = overall_score
        
        return scores
    
    def validate_business(self, prospect: Dict) -> float:
        """Validate that prospect represents a real business"""
        score = 0.0
        
        # Domain validation
        domain = prospect.get('domain', '')
        if domain and self._is_valid_domain(domain):
            score += 0.4
        
        # Company name validation
        company_name = prospect.get('company_name', '')
        if company_name and self._is_valid_company_name(company_name):
            score += 0.3
        
        # Advertiser ID validation
        advertiser_id = prospect.get('advertiser_id', '')
        if advertiser_id and len(advertiser_id) > 10:
            score += 0.3
        
        return min(score, 1.0)
    
    def verify_vertical_classification(self, prospect: Dict) -> float:
        """Verify vertical classification accuracy"""
        company_name = prospect.get('company_name', '').lower()
        vertical = prospect.get('vertical', '').lower()
        
        # Vertical-specific keywords
        vertical_keywords = {
            'dental': ['dental', 'dentist', 'orthodontic', 'oral', 'smile'],
            'fitness': ['fitness', 'gym', 'workout', 'training', 'health'],
            'legal': ['law', 'legal', 'attorney', 'lawyer', 'counsel'],
            'accounting': ['accounting', 'tax', 'bookkeeping', 'financial'],
            'hvac': ['hvac', 'heating', 'cooling', 'air', 'plumbing'],
            'medical': ['medical', 'clinic', 'doctor', 'healthcare', 'urgent']
        }
        
        if vertical in vertical_keywords:
            keywords = vertical_keywords[vertical]
            keyword_matches = sum(1 for keyword in keywords if keyword in company_name)
            return min(keyword_matches / len(keywords) * 2, 1.0)
        
        return 0.5  # Default score if vertical not recognized
    
    def validate_spend_patterns(self, prospect: Dict) -> float:
        """Validate financial data realism"""
        monthly_spend = prospect.get('estimated_monthly_spend', 0)
        campaign_count = prospect.get('total_ads', 0)
        
        # Spend per campaign ratio
        if campaign_count > 0:
            spend_per_campaign = monthly_spend / campaign_count
            
            # Realistic spend per campaign: $50-$2000
            if 50 <= spend_per_campaign <= 2000:
                ratio_score = 1.0
            elif spend_per_campaign < 50:
                ratio_score = spend_per_campaign / 50
            else:
                ratio_score = max(0.1, 2000 / spend_per_campaign)
        else:
            ratio_score = 0.0
        
        # Overall spend realism
        if 500 <= monthly_spend <= 50000:
            spend_score = 1.0
        elif monthly_spend < 500:
            spend_score = monthly_spend / 500
        else:
            spend_score = max(0.1, 50000 / monthly_spend)
        
        return (ratio_score + spend_score) / 2
    
    def assess_contact_likelihood(self, prospect: Dict) -> float:
        """Assess likelihood of successful contact"""
        score = 0.0
        
        # Company size indicators
        campaign_count = prospect.get('total_ads', 0)
        if 5 <= campaign_count <= 25:
            score += 0.4  # Sweet spot for responsiveness
        elif campaign_count > 25:
            score += 0.2  # Large companies, harder to reach
        else:
            score += 0.1  # Very small, may not have budget
        
        # Regional factors
        region = prospect.get('region', '').upper()
        region_scores = {'US': 0.3, 'CA': 0.3, 'AU': 0.25, 'UK': 0.25, 'EU': 0.2}
        score += region_scores.get(region, 0.1)
        
        # Vertical responsiveness
        vertical = prospect.get('vertical', '').lower()
        vertical_scores = {
            'dental': 0.3, 'medical': 0.3, 'legal': 0.25,
            'accounting': 0.25, 'fitness': 0.2, 'hvac': 0.2
        }
        score += vertical_scores.get(vertical, 0.1)
        
        return min(score, 1.0)
    
    def evaluate_market_position(self, prospect: Dict) -> float:
        """Evaluate competitive market position"""
        # This would integrate with competitive analysis
        # For now, use campaign volume as proxy
        campaign_count = prospect.get('total_ads', 0)
        
        if 8 <= campaign_count <= 20:
            return 0.8  # Good market position, not too small or too large
        elif 5 <= campaign_count <= 30:
            return 0.6  # Acceptable position
        else:
            return 0.3  # Either too small or too large for optimal targeting
    
    def _is_valid_domain(self, domain: str) -> bool:
        """Validate domain format"""
        try:
            result = urlparse(f"http://{domain}")
            return bool(result.netloc) and '.' in result.netloc
        except:
            return False
    
    def _is_valid_company_name(self, name: str) -> bool:
        """Validate company name format"""
        if not name or len(name) < 3:
            return False
        
        # Check for obvious invalid patterns
        invalid_patterns = ['unknown', 'test', 'sample', 'example']
        return not any(pattern in name.lower() for pattern in invalid_patterns)

class DataIntegrationPipeline:
    """Pipeline for integrating and validating prospect data"""
    
    def __init__(self):
        self.entity_resolver = EntityResolver()
        self.quality_controller = QualityController()
        self.processing_stats = {
            'total_processed': 0,
            'duplicates_removed': 0,
            'quality_filtered': 0,
            'entities_created': 0
        }
    
    def process_prospects(self, raw_prospects: List[Dict]) -> Dict:
        """Process raw prospects through complete pipeline"""
        logger.info(f"Processing {len(raw_prospects)} raw prospects")
        
        # Step 1: Entity resolution and deduplication
        resolved_prospects = []
        seen_entities = set()
        
        for prospect in raw_prospects:
            entity_key = self.entity_resolver.generate_entity_key(
                prospect.get('domain', ''),
                prospect.get('company_name', '')
            )
            
            if entity_key not in seen_entities:
                entity = self.entity_resolver.resolve_entity(
                    prospect.get('domain', ''),
                    prospect.get('company_name', ''),
                    prospect.get('vertical', ''),
                    prospect.get('region', '')
                )
                
                # Merge prospect data with entity
                enhanced_prospect = {**prospect}
                enhanced_prospect['entity_key'] = entity_key
                enhanced_prospect['confidence_score'] = entity.confidence_score
                
                resolved_prospects.append(enhanced_prospect)
                seen_entities.add(entity_key)
                self.processing_stats['entities_created'] += 1
            else:
                self.processing_stats['duplicates_removed'] += 1
        
        # Step 2: Quality assessment and filtering
        qualified_prospects = []
        
        for prospect in resolved_prospects:
            quality_scores = self.quality_controller.calculate_quality_score(prospect)
            prospect['quality_scores'] = quality_scores
            
            # Apply quality threshold
            if quality_scores['overall'] >= 0.6:
                qualified_prospects.append(prospect)
            else:
                self.processing_stats['quality_filtered'] += 1
        
        self.processing_stats['total_processed'] = len(raw_prospects)
        
        # Step 3: Ranking and prioritization
        qualified_prospects.sort(key=lambda x: x['quality_scores']['overall'], reverse=True)
        
        return {
            'qualified_prospects': qualified_prospects,
            'processing_stats': self.processing_stats,
            'quality_summary': self._generate_quality_summary(qualified_prospects)
        }
    
    def _generate_quality_summary(self, prospects: List[Dict]) -> Dict:
        """Generate quality summary statistics"""
        if not prospects:
            return {}
        
        quality_scores = [p['quality_scores']['overall'] for p in prospects]
        
        return {
            'total_qualified': len(prospects),
            'average_quality_score': sum(quality_scores) / len(quality_scores),
            'high_quality_count': len([s for s in quality_scores if s >= 0.8]),
            'medium_quality_count': len([s for s in quality_scores if 0.6 <= s < 0.8]),
            'quality_distribution': {
                'excellent': len([s for s in quality_scores if s >= 0.9]),
                'good': len([s for s in quality_scores if 0.8 <= s < 0.9]),
                'acceptable': len([s for s in quality_scores if 0.6 <= s < 0.8])
            }
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize pipeline
    pipeline = DataIntegrationPipeline()
    
    # Sample data for testing
    sample_prospects = [
        {
            "company_name": "Pure Dentistry",
            "domain": "puredentistry.com.au",
            "vertical": "dental",
            "region": "AU",
            "estimated_monthly_spend": 7250,
            "total_ads": 20
        },
        {
            "company_name": "Pure Dental Services",  # Similar name
            "domain": "puredentistry.com.au",  # Same domain
            "vertical": "dental",
            "region": "AU",
            "estimated_monthly_spend": 7250,
            "total_ads": 20
        },
        {
            "company_name": "DM Fitness",
            "domain": "dmfitness.com",
            "vertical": "fitness",
            "region": "US",
            "estimated_monthly_spend": 2375,
            "total_ads": 19
        }
    ]
    
    # Process prospects
    results = pipeline.process_prospects(sample_prospects)
    
    print("Processing Results:")
    print(f"Qualified Prospects: {len(results['qualified_prospects'])}")
    print(f"Duplicates Removed: {results['processing_stats']['duplicates_removed']}")
    print(f"Quality Filtered: {results['processing_stats']['quality_filtered']}")
    print(f"Average Quality Score: {results['quality_summary'].get('average_quality_score', 0):.2f}")
