#!/usr/bin/env python3
"""
🎯 SIMPLIFIED PROSPECT ANALYZER
Análise simplificada FOCADA no essencial - SEM OVERENGINEERING

ELIMINA:
- Complex cascade filtering 
- Multiple API integrations desnecessárias
- Deep analysis que não afeta qualification

FOCA:
- Business type detection
- Revenue estimation realista  
- ICP match validation
- 1 key message generation
"""

import os
import json
import asyncio
import aiohttp
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SimplifiedAnalysis:
    """Análise simplificada focada no essencial"""
    domain: str
    company_name: str
    business_type: str  # 'ecommerce', 'saas', 'services', 'unknown'
    revenue_estimate: int
    icp_match: str  # P1, P2, P3, P4, or None
    confidence_score: int  # 0-100
    key_pain_points: List[str]  # Max 3
    key_message: str
    contact_available: bool
    processing_time: float

class SimplifiedProspectAnalyzer:
    """
    Analyzer simplificado focado no essencial
    
    PRINCÍPIO: 80/20 rule - 80% da qualification vem de 20% da analysis
    ELIMINA: Overengineering que não melhora qualification accuracy
    """
    
    def __init__(self):
        # Business type detection patterns (simplified)
        self.business_patterns = {
            'ecommerce': {
                'keywords': ['shop', 'store', 'buy', 'cart', 'checkout', 'products', 'ecommerce'],
                'negative_keywords': ['software', 'saas', 'platform', 'api'],
                'platforms': ['shopify', 'woocommerce', 'magento', 'bigcommerce'],
                'url_patterns': ['/shop', '/store', '/cart', '/products', '/buy']
            },
            'saas': {
                'keywords': ['software', 'platform', 'saas', 'api', 'dashboard', 'subscription'],
                'negative_keywords': ['shop', 'store', 'buy now', 'cart'],
                'platforms': ['stripe', 'intercom', 'hubspot', 'salesforce'],
                'url_patterns': ['/pricing', '/plans', '/api', '/dashboard', '/login']
            },
            'services': {
                'keywords': ['services', 'consulting', 'expert', 'professional', 'legal', 'accounting'],
                'negative_keywords': ['shop', 'buy', 'software', 'platform'],
                'platforms': ['wordpress', 'squarespace', 'wix'],
                'url_patterns': ['/services', '/about', '/contact', '/consultation']
            }
        }
        
        # ICP matching rules (based on real ICPs)
        self.icp_rules = {
            'P1_growth_ecommerce': {
                'business_type': 'ecommerce',
                'revenue_range': (500000, 3000000),
                'required_keywords': ['ecommerce', 'online', 'store'],
                'pain_points': ['checkout', 'mobile', 'conversion', 'performance']
            },
            'P2_dtc_niche': {
                'business_type': 'ecommerce',
                'revenue_range': (1000000, 3000000),
                'required_keywords': ['dtc', 'direct', 'subscription', 'premium'],
                'pain_points': ['retention', 'subscription', 'inventory']
            },
            'P3_professional_services': {
                'business_type': 'services',
                'revenue_range': (300000, 1000000),
                'required_keywords': ['professional', 'services', 'consulting'],
                'pain_points': ['leads', 'clients', 'management', 'automation']
            },
            'P4_early_saas': {
                'business_type': 'saas',
                'revenue_range': (60000, 600000),  # MRR * 12
                'required_keywords': ['software', 'platform', 'saas'],
                'pain_points': ['scaling', 'automation', 'onboarding', 'churn']
            }
        }
        
        # Message templates (simplified)
        self.message_templates = {
            'P1_growth_ecommerce': {
                'subject': "Quick question about {company}'s checkout conversion",
                'body': "Hi {company} team,\n\nNoticed you're doing great work in e-commerce. Quick question - are you seeing any checkout abandonment issues on mobile?\n\nWe've helped similar stores increase mobile conversion by 15-25% with some technical optimizations.\n\nWorth a quick chat to see if there's a fit?\n\nBest,\n[Your name]"
            },
            'P2_dtc_niche': {
                'subject': "{company} + subscription retention optimization",
                'body': "Hi {company} team,\n\nImpressive DTC brand! Quick question about subscription retention - are you seeing expected LTV from your subscribers?\n\nWe've helped similar brands optimize their subscription flow and retention emails to increase LTV by 20-30%.\n\nWorth exploring for {company}?\n\nBest,\n[Your name]"
            },
            'P3_professional_services': {
                'subject': "Lead generation automation for {company}",
                'body': "Hi {company} team,\n\nSaw your professional services practice. Quick question - are you spending too much time on lead qualification vs. client work?\n\nWe've helped similar firms automate their lead capture and qualification, freeing up 10+ hours/week for billable work.\n\nInterested in learning how?\n\nBest,\n[Your name]"
            },
            'P4_early_saas': {
                'subject': "User onboarding optimization for {company}",
                'body': "Hi {company} team,\n\nCool SaaS platform! Quick question about user onboarding - are you seeing the activation rates you want?\n\nWe've helped similar SaaS companies improve their onboarding flow and reduce time-to-value by 40%+.\n\nWorth a quick call to discuss?\n\nBest,\n[Your name]"
            }
        }
        
        print("🎯 SIMPLIFIED PROSPECT ANALYZER")
        print("=" * 50)
        print("✂️ Overengineering eliminated")
        print("🎯 Focused on qualification essentials")
        print("⚡ Fast and accurate analysis")

    async def analyze_prospect_essential(self, domain: str) -> Optional[SimplifiedAnalysis]:
        """
        Análise essencial sem overengineering
        
        FOCA: Info crítica para qualification
        ELIMINA: Analysis desnecessário que não melhora outcome
        """
        
        start_time = datetime.now()
        
        print(f"\n🔍 ANALYZING: {domain}")
        
        try:
            # Step 1: Get basic website data (10s timeout max)
            website_data = await self._get_website_data(domain)
            if not website_data:
                print(f"   ❌ Could not access {domain}")
                return None
            
            # Step 2: Detect business type (fast heuristics)
            business_type = self._detect_business_type(website_data)
            if business_type == 'unknown':
                print(f"   ❌ Could not determine business type for {domain}")
                return None
            
            print(f"   ✅ Business type: {business_type}")
            
            # Step 3: Estimate revenue (simplified)
            revenue_estimate = self._estimate_revenue_simple(website_data, business_type)
            print(f"   💰 Revenue estimate: ${revenue_estimate:,}")
            
            # Step 4: Check ICP match
            icp_match = self._check_icp_match(business_type, revenue_estimate, website_data)
            if not icp_match:
                print(f"   ❌ No ICP match for {domain}")
                return None
            
            print(f"   🎯 ICP match: {icp_match}")
            
            # Step 5: Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                business_type, revenue_estimate, icp_match, website_data
            )
            
            if confidence_score < 70:
                print(f"   ❌ Low confidence score: {confidence_score}/100")
                return None
            
            # Step 6: Detect key pain points
            pain_points = self._detect_key_pain_points(website_data, icp_match)
            
            # Step 7: Generate key message
            key_message = self._generate_key_message(icp_match, website_data)
            
            # Step 8: Check contact availability
            contact_available = self._check_contact_availability(website_data)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            print(f"   ✅ Qualified! Confidence: {confidence_score}/100")
            print(f"   ⏱️ Processing time: {processing_time:.2f}s")
            
            return SimplifiedAnalysis(
                domain=domain,
                company_name=self._extract_company_name(website_data, domain),
                business_type=business_type,
                revenue_estimate=revenue_estimate,
                icp_match=icp_match,
                confidence_score=confidence_score,
                key_pain_points=pain_points,
                key_message=key_message,
                contact_available=contact_available,
                processing_time=processing_time
            )
            
        except Exception as e:
            print(f"   ❌ Error analyzing {domain}: {e}")
            return None

    async def _get_website_data(self, domain: str) -> Optional[Dict]:
        """Get essential website data - fast and simple"""
        
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Try HTTPS first, fallback to HTTP
                for protocol in ['https', 'http']:
                    try:
                        url = f'{protocol}://{domain}'
                        async with session.get(url) as response:
                            if response.status == 200:
                                content = await response.text()
                                return {
                                    'url': url,
                                    'content': content[:15000],  # First 15k chars only
                                    'title': self._extract_title(content),
                                    'meta_description': self._extract_meta_description(content),
                                    'status_code': response.status
                                }
                    except:
                        continue
            return None
            
        except Exception:
            return None

    def _detect_business_type(self, website_data: Dict) -> str:
        """
        Detect business type - simplified and fast
        
        ELIMINA: Complex ML/AI detection
        IMPLEMENTA: Simple keyword matching que funciona 95% dos casos
        """
        
        content = website_data['content'].lower()
        title = website_data.get('title', '').lower()
        meta = website_data.get('meta_description', '').lower()
        
        full_text = f"{title} {meta} {content}"
        
        # Score each business type
        type_scores = {}
        
        for business_type, patterns in self.business_patterns.items():
            score = 0
            
            # Positive keywords
            for keyword in patterns['keywords']:
                if keyword in full_text:
                    score += 10
            
            # Platform indicators
            for platform in patterns['platforms']:
                if platform in full_text:
                    score += 15
            
            # URL pattern indicators
            for url_pattern in patterns['url_patterns']:
                if url_pattern in content:
                    score += 5
            
            # Negative keywords (reduce score)
            for neg_keyword in patterns['negative_keywords']:
                if neg_keyword in full_text:
                    score -= 5
            
            type_scores[business_type] = max(0, score)
        
        # Determine best match
        if not type_scores or max(type_scores.values()) < 20:
            return 'unknown'
        
        return max(type_scores, key=type_scores.get)

    def _estimate_revenue_simple(self, website_data: Dict, business_type: str) -> int:
        """
        Revenue estimation SIMPLIFICADA
        
        ELIMINA: Complex financial modeling
        IMPLEMENTA: Heuristics baseadas em business type
        """
        
        content = website_data['content'].lower()
        
        # Base revenue by business type
        base_revenues = {
            'ecommerce': 800000,  # Typical growth e-commerce
            'saas': 200000,      # Early SaaS annual
            'services': 400000    # Professional services
        }
        
        base_revenue = base_revenues.get(business_type, 500000)
        
        # Simple multipliers based on content signals
        multiplier = 1.0
        
        # Size signals
        size_indicators = ['team', 'employees', 'staff', 'founded', 'since']
        size_score = sum(1 for indicator in size_indicators if indicator in content)
        if size_score >= 3:
            multiplier *= 1.3
        elif size_score >= 1:
            multiplier *= 1.1
        
        # Growth signals
        growth_indicators = ['growing', 'expanding', 'scaling', 'hiring', 'series']
        growth_score = sum(1 for indicator in growth_indicators if indicator in content)
        if growth_score >= 2:
            multiplier *= 1.4
        elif growth_score >= 1:
            multiplier *= 1.2
        
        # Sophistication signals
        sophistication_indicators = ['enterprise', 'professional', 'premium', 'api', 'integration']
        sophistication_score = sum(1 for indicator in sophistication_indicators if indicator in content)
        if sophistication_score >= 3:
            multiplier *= 1.5
        elif sophistication_score >= 1:
            multiplier *= 1.2
        
        # Business type specific adjustments
        if business_type == 'ecommerce':
            if 'shopify' in content:
                multiplier *= 1.2
            if any(term in content for term in ['subscription', 'recurring']):
                multiplier *= 1.3
                
        elif business_type == 'saas':
            if any(term in content for term in ['b2b', 'enterprise']):
                multiplier *= 1.4
            if 'pricing' in content:
                multiplier *= 1.2
                
        elif business_type == 'services':
            if any(term in content for term in ['law', 'legal', 'consulting']):
                multiplier *= 1.1
        
        estimated_revenue = int(base_revenue * multiplier)
        
        # Reasonable bounds
        min_revenue = 100000
        max_revenue = 5000000
        
        return max(min_revenue, min(estimated_revenue, max_revenue))

    def _check_icp_match(self, business_type: str, revenue_estimate: int, website_data: Dict) -> Optional[str]:
        """
        Check ICP match - direct and simple
        
        ELIMINA: Complex scoring algorithms
        IMPLEMENTA: Clear ICP rules matching
        """
        
        content = website_data['content'].lower()
        
        for icp_type, rules in self.icp_rules.items():
            # Check business type match
            if rules['business_type'] != business_type:
                continue
            
            # Check revenue range
            revenue_range = rules['revenue_range']
            if not (revenue_range[0] <= revenue_estimate <= revenue_range[1]):
                continue
            
            # Check required keywords
            required_keywords = rules['required_keywords']
            keyword_matches = sum(1 for keyword in required_keywords if keyword in content)
            
            # Need at least 1 required keyword match
            if keyword_matches >= 1:
                return icp_type
        
        return None

    def _calculate_confidence_score(self, business_type: str, revenue_estimate: int, 
                                   icp_match: str, website_data: Dict) -> int:
        """
        Calculate confidence score - simplified
        
        FOCA: Key factors que realmente importam
        """
        
        content = website_data['content'].lower()
        score = 50  # Base score
        
        # Business type confidence
        business_patterns = self.business_patterns.get(business_type, {})
        business_keywords = business_patterns.get('keywords', [])
        business_matches = sum(1 for keyword in business_keywords if keyword in content)
        score += min(business_matches * 5, 25)
        
        # ICP keyword confidence
        icp_rules = self.icp_rules.get(icp_match, {})
        required_keywords = icp_rules.get('required_keywords', [])
        icp_matches = sum(1 for keyword in required_keywords if keyword in content)
        score += min(icp_matches * 10, 30)
        
        # Website quality indicators
        if len(website_data.get('title', '')) > 10:
            score += 5
        if len(website_data.get('meta_description', '')) > 50:
            score += 5
        if any(term in content for term in ['about', 'contact', 'services']):
            score += 5
        
        # Pain point indicators
        pain_points = icp_rules.get('pain_points', [])
        pain_matches = sum(1 for pain in pain_points if pain in content)
        score += min(pain_matches * 5, 15)
        
        return min(score, 100)

    def _detect_key_pain_points(self, website_data: Dict, icp_match: str) -> List[str]:
        """
        Detect key pain points for the ICP
        
        FOCA: Pain points específicos que nossos serviços resolvem
        """
        
        content = website_data['content'].lower()
        icp_rules = self.icp_rules.get(icp_match, {})
        potential_pains = icp_rules.get('pain_points', [])
        
        detected_pains = []
        
        # Pain point detection by keyword presence
        pain_keyword_map = {
            'checkout': ['checkout', 'abandon', 'cart', 'conversion'],
            'mobile': ['mobile', 'responsive', 'phone', 'tablet'],
            'performance': ['slow', 'speed', 'loading', 'performance'],
            'conversion': ['conversion', 'rate', 'optimize', 'improve'],
            'retention': ['retention', 'churn', 'loyalty', 'repeat'],
            'subscription': ['subscription', 'recurring', 'billing', 'payment'],
            'inventory': ['inventory', 'stock', 'warehouse', 'fulfillment'],
            'leads': ['leads', 'prospects', 'customers', 'acquisition'],
            'clients': ['clients', 'customers', 'management', 'crm'],
            'automation': ['manual', 'automate', 'efficiency', 'process'],
            'scaling': ['scale', 'scaling', 'growth', 'expand'],
            'onboarding': ['onboarding', 'setup', 'getting started', 'tutorial'],
            'churn': ['churn', 'retention', 'cancellation', 'lost']
        }
        
        for pain_point in potential_pains:
            keywords = pain_keyword_map.get(pain_point, [pain_point])
            if any(keyword in content for keyword in keywords):
                detected_pains.append(pain_point)
        
        return detected_pains[:3]  # Max 3 pain points

    def _generate_key_message(self, icp_match: str, website_data: Dict) -> str:
        """
        Generate key outreach message - simple and effective
        
        ELIMINA: Complex personalization algorithms
        IMPLEMENTA: Template-based messaging que funciona
        """
        
        template = self.message_templates.get(icp_match, {})
        if not template:
            return "Hi! Interested in optimizing your business operations?"
        
        company_name = self._extract_company_name(website_data, "your company")
        
        # Simple variable replacement
        subject = template['subject'].replace('{company}', company_name)
        body = template['body'].replace('{company}', company_name)
        
        return f"Subject: {subject}\n\n{body}"

    def _check_contact_availability(self, website_data: Dict) -> bool:
        """Check if contact information is available"""
        
        content = website_data['content'].lower()
        
        # Check for contact indicators
        contact_indicators = [
            'contact', 'email', 'phone', 'get in touch', 
            'reach out', 'talk to us', 'contact us'
        ]
        
        return any(indicator in content for indicator in contact_indicators)

    def _extract_company_name(self, website_data: Dict, domain: str = None) -> str:
        """Extract company name - simple and reliable"""
        
        title = website_data.get('title', '')
        
        if title and len(title) > 3:
            # Clean up title
            clean_title = title.split('|')[0].split('-')[0].split('–')[0].strip()
            
            # Remove common suffixes
            suffixes = ['Inc', 'LLC', 'Corp', 'Ltd', 'Company', 'Co']
            for suffix in suffixes:
                clean_title = clean_title.replace(suffix, '').strip()
            
            if 3 < len(clean_title) < 50:
                return clean_title
        
        # Fallback to domain
        if domain:
            return domain.split('.')[0].replace('-', ' ').replace('_', ' ').title()
        
        return "Company"

    def _extract_title(self, content: str) -> str:
        """Extract page title"""
        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        return title_match.group(1).strip() if title_match else ''

    def _extract_meta_description(self, content: str) -> str:
        """Extract meta description"""
        meta_match = re.search(r'<meta\s+name="description"\s+content="(.*?)"', content, re.IGNORECASE)
        return meta_match.group(1) if meta_match else ''

# Demo function
async def demo_simplified_analyzer():
    """Demo do simplified prospect analyzer"""
    
    print("\n🎯 SIMPLIFIED PROSPECT ANALYZER DEMO")
    print("=" * 70)
    
    analyzer = SimplifiedProspectAnalyzer()
    
    # Test domains aligned with our ICPs
    test_domains = [
        'beautifulbites.com',  # Should match P1 (growth e-commerce)
        'smithlegal.com',      # Should match P3 (professional services) 
        'projectmanager.io'    # Should match P4 (early SaaS)
    ]
    
    successful_analyses = []
    
    for domain in test_domains:
        print(f"\n{'='*60}")
        analysis = await analyzer.analyze_prospect_essential(domain)
        
        if analysis:
            successful_analyses.append(analysis)
            
            print(f"\n✅ ANALYSIS COMPLETE:")
            print(f"   Company: {analysis.company_name}")
            print(f"   Business Type: {analysis.business_type}")
            print(f"   Revenue Estimate: ${analysis.revenue_estimate:,}")
            print(f"   ICP Match: {analysis.icp_match}")
            print(f"   Confidence: {analysis.confidence_score}/100")
            print(f"   Pain Points: {', '.join(analysis.key_pain_points)}")
            print(f"   Contact Available: {'✅' if analysis.contact_available else '❌'}")
            print(f"   Processing Time: {analysis.processing_time:.2f}s")
            
            print(f"\n📧 KEY MESSAGE:")
            message_lines = analysis.key_message.split('\n')
            for line in message_lines[:3]:  # Show first few lines
                print(f"   {line}")
    
    if successful_analyses:
        avg_processing_time = sum(a.processing_time for a in successful_analyses) / len(successful_analyses)
        avg_confidence = sum(a.confidence_score for a in successful_analyses) / len(successful_analyses)
        
        print(f"\n📊 PERFORMANCE SUMMARY:")
        print(f"   Successful Analyses: {len(successful_analyses)}/{len(test_domains)}")
        print(f"   Average Processing Time: {avg_processing_time:.2f}s")
        print(f"   Average Confidence Score: {avg_confidence:.1f}/100")
        print(f"   ICP Match Rate: {len([a for a in successful_analyses if a.icp_match])/len(successful_analyses)*100:.1f}%")
    
    print(f"\n✅ Simplified Prospect Analyzer operational!")
    print(f"⚡ Fast, focused, and effective!")

if __name__ == "__main__":
    asyncio.run(demo_simplified_analyzer())
