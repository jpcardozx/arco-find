#!/usr/bin/env python3
"""
🎯 ENHANCED BUSINESS INTELLIGENCE ENGINE
Expert-optimized customer acquisition system with buying signals

FOCUS: Maximum conversion rate through business intelligence
- Company size and budget qualification
- Buying readiness signal detection  
- Competitive positioning analysis
- Revenue accuracy optimization via business model detection
"""

import os
import json
import asyncio
import aiohttp
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import re
from dotenv import load_dotenv

load_dotenv()

@dataclass
class BusinessIntelligence:
    """Comprehensive business intelligence for prospect qualification"""
    company_name: str
    domain: str
    
    # Business Model Intelligence
    business_model: str  # 'saas', 'ecommerce', 'services', 'marketplace'
    revenue_tier: str    # 'startup', 'small_business', 'mid_market', 'enterprise'
    
    # Company Size Intelligence
    estimated_employees: int
    growth_indicators: List[str]
    budget_tier: str  # 'low', 'medium', 'high', 'enterprise'
    
    # Buying Readiness Signals
    buying_signals: List[str]
    buying_readiness_score: int  # 0-100
    urgency_factors: List[str]
    
    # Competitive Intelligence
    tech_sophistication_score: int  # 0-100
    competitor_analysis: Dict
    market_position: str  # 'leader', 'challenger', 'follower', 'niche'
    
    # Contact Intelligence
    decision_maker_signals: Dict
    contact_channels: List[str]
    
    # Enhanced Scoring
    total_qualification_score: int  # 0-100
    conversion_probability: float   # 0.0-1.0
    recommended_approach: str

class EnhancedBusinessIntelligence:
    """
    Customer acquisition expert-optimized business intelligence
    
    Focus: Maximum qualification accuracy and conversion optimization
    """
    
    def __init__(self):
        # API configurations (freemium tiers)
        self.clearbit_key = os.getenv('CLEARBIT_API_KEY')
        self.hunter_key = os.getenv('HUNTER_API_KEY')
        self.linkedin_key = os.getenv('LINKEDIN_API_KEY')
        
        # Business model patterns
        self.business_model_patterns = {
            'saas': {
                'keywords': ['software', 'platform', 'api', 'cloud', 'subscription', 'dashboard'],
                'url_patterns': ['/pricing', '/plans', '/subscription', '/api'],
                'revenue_multiplier': 1.4,
                'budget_tier_base': 'medium'
            },
            'ecommerce': {
                'keywords': ['shop', 'store', 'buy', 'cart', 'checkout', 'products'],
                'url_patterns': ['/shop', '/store', '/cart', '/checkout', '/products'],
                'revenue_multiplier': 1.2,
                'budget_tier_base': 'medium'
            },
            'services': {
                'keywords': ['services', 'consulting', 'agency', 'studio', 'solutions'],
                'url_patterns': ['/services', '/consulting', '/contact', '/about'],
                'revenue_multiplier': 1.0,
                'budget_tier_base': 'low'
            },
            'marketplace': {
                'keywords': ['marketplace', 'vendors', 'sellers', 'buyers', 'commission'],
                'url_patterns': ['/vendors', '/sellers', '/marketplace'],
                'revenue_multiplier': 1.6,
                'budget_tier_base': 'high'
            }
        }
        
        # Buying signal patterns
        self.buying_signals = {
            'immediate': {
                'funding_keywords': ['funding', 'investment', 'series', 'raised', 'capital'],
                'hiring_keywords': ['hiring', 'join our team', 'careers', 'open positions'],
                'migration_keywords': ['migration', 'switching', 'upgrade', 'transition'],
                'growth_keywords': ['expansion', 'scaling', 'growing', 'new market']
            },
            'medium_term': {
                'planning_keywords': ['roadmap', 'planning', 'strategy', 'vision', 'goals'],
                'evaluation_keywords': ['evaluation', 'research', 'comparing', 'options'],
                'budget_keywords': ['budget', 'investment', 'ROI', 'cost-effective']
            },
            'long_term': {
                'awareness_keywords': ['learning', 'exploring', 'considering', 'investigating'],
                'education_keywords': ['guide', 'tutorial', 'best practices', 'how-to']
            }
        }
        
        print("🎯 ENHANCED BUSINESS INTELLIGENCE ENGINE")
        print("=" * 50)
        print(f"🔍 Clearbit API: {'✅' if self.clearbit_key else '❌'}")
        print(f"📧 Hunter API: {'✅' if self.hunter_key else '❌'}")
        print(f"💼 LinkedIn API: {'✅' if self.linkedin_key else '❌'}")
        print("🚀 Ready for enhanced business intelligence")

    async def analyze_comprehensive_business_intelligence(self, domain: str) -> BusinessIntelligence:
        """
        Comprehensive business intelligence analysis for maximum conversion
        """
        
        print(f"\n🎯 ANALYZING BUSINESS INTELLIGENCE: {domain}")
        
        # Parallel intelligence gathering
        tasks = [
            self._detect_business_model(domain),
            self._analyze_company_size(domain),
            self._detect_buying_signals(domain),
            self._analyze_competitive_position(domain),
            self._analyze_decision_maker_signals(domain)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results safely
        business_model = results[0] if not isinstance(results[0], Exception) else {'model': 'unknown', 'confidence': 0}
        company_size = results[1] if not isinstance(results[1], Exception) else {'employees': 10, 'tier': 'small_business'}
        buying_signals = results[2] if not isinstance(results[2], Exception) else {'signals': [], 'score': 20}
        competitive_pos = results[3] if not isinstance(results[3], Exception) else {'sophistication': 50, 'position': 'unknown'}
        decision_maker = results[4] if not isinstance(results[4], Exception) else {'signals': {}, 'channels': ['email']}
        
        # Calculate comprehensive qualification score
        qualification_score = self._calculate_qualification_score(
            business_model, company_size, buying_signals, competitive_pos
        )
        
        # Calculate conversion probability
        conversion_prob = self._calculate_conversion_probability(qualification_score, buying_signals)
        
        # Recommend approach
        approach = self._recommend_approach(business_model, buying_signals, company_size)
        
        company_name = await self._extract_company_name(domain)
        
        return BusinessIntelligence(
            company_name=company_name,
            domain=domain,
            business_model=business_model['model'],
            revenue_tier=company_size['tier'],
            estimated_employees=company_size['employees'],
            growth_indicators=company_size.get('growth_indicators', []),
            budget_tier=company_size.get('budget_tier', 'medium'),
            buying_signals=buying_signals['signals'],
            buying_readiness_score=buying_signals['score'],
            urgency_factors=buying_signals.get('urgency_factors', []),
            tech_sophistication_score=competitive_pos['sophistication'],
            competitor_analysis=competitive_pos.get('analysis', {}),
            market_position=competitive_pos['position'],
            decision_maker_signals=decision_maker['signals'],
            contact_channels=decision_maker['channels'],
            total_qualification_score=qualification_score,
            conversion_probability=conversion_prob,
            recommended_approach=approach
        )

    async def _detect_business_model(self, domain: str) -> Dict:
        """Enhanced business model detection with confidence scoring"""
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=8)) as session:
                async with session.get(f'https://{domain}') as response:
                    if response.status == 200:
                        content = await response.text()
                        return self._analyze_business_model_content(content, domain)
        except Exception as e:
            print(f"    Business model detection error: {e}")
        
        return {'model': 'unknown', 'confidence': 0, 'revenue_multiplier': 1.0}

    def _analyze_business_model_content(self, content: str, domain: str) -> Dict:
        """Analyze content to determine business model"""
        
        content_lower = content.lower()
        url_content = f"/{domain}/" + content_lower
        
        model_scores = {}
        
        for model, patterns in self.business_model_patterns.items():
            score = 0
            
            # Keyword matching
            keyword_matches = sum(1 for keyword in patterns['keywords'] if keyword in content_lower)
            score += keyword_matches * 10
            
            # URL pattern matching
            url_matches = sum(1 for pattern in patterns['url_patterns'] if pattern in url_content)
            score += url_matches * 15
            
            # Specific business model indicators
            if model == 'saas':
                if any(term in content_lower for term in ['free trial', 'demo', 'api documentation']):
                    score += 20
            elif model == 'ecommerce':
                if any(term in content_lower for term in ['add to cart', 'shopify', 'woocommerce']):
                    score += 20
            elif model == 'services':
                if any(term in content_lower for term in ['contact us', 'get quote', 'consultation']):
                    score += 15
            elif model == 'marketplace':
                if any(term in content_lower for term in ['seller dashboard', 'vendor portal']):
                    score += 25
            
            model_scores[model] = score
        
        # Determine best match
        best_model = max(model_scores, key=model_scores.get)
        confidence = min(model_scores[best_model], 100)
        
        if confidence < 30:
            best_model = 'unknown'
        
        return {
            'model': best_model,
            'confidence': confidence,
            'revenue_multiplier': self.business_model_patterns.get(best_model, {}).get('revenue_multiplier', 1.0),
            'budget_tier_base': self.business_model_patterns.get(best_model, {}).get('budget_tier_base', 'medium')
        }

    async def _analyze_company_size(self, domain: str) -> Dict:
        """Analyze company size through multiple signals"""
        
        size_signals = {}
        
        # Try Clearbit enrichment (if available)
        if self.clearbit_key:
            clearbit_data = await self._get_clearbit_data(domain)
            if clearbit_data:
                size_signals['clearbit_employees'] = clearbit_data.get('employees', 0)
                size_signals['clearbit_revenue'] = clearbit_data.get('annual_revenue', 0)
        
        # Website content analysis
        content_signals = await self._analyze_size_from_content(domain)
        size_signals.update(content_signals)
        
        # Calculate estimated size
        estimated_employees = self._calculate_company_size(size_signals)
        
        # Determine tier and budget
        if estimated_employees >= 100:
            tier = 'enterprise'
            budget_tier = 'enterprise'
        elif estimated_employees >= 50:
            tier = 'mid_market'
            budget_tier = 'high'
        elif estimated_employees >= 10:
            tier = 'small_business'
            budget_tier = 'medium'
        else:
            tier = 'startup'
            budget_tier = 'low'
        
        # Detect growth indicators
        growth_indicators = self._detect_growth_indicators(size_signals)
        
        return {
            'employees': estimated_employees,
            'tier': tier,
            'budget_tier': budget_tier,
            'growth_indicators': growth_indicators,
            'size_signals': size_signals
        }

    async def _get_clearbit_data(self, domain: str) -> Optional[Dict]:
        """Get company data from Clearbit API"""
        
        try:
            url = f"https://company.clearbit.com/v2/companies/find"
            headers = {'Authorization': f'Bearer {self.clearbit_key}'}
            params = {'domain': domain}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'employees': data.get('metrics', {}).get('employees', 0),
                            'annual_revenue': data.get('metrics', {}).get('annualRevenue', 0),
                            'industry': data.get('category', {}).get('industry', ''),
                            'funding': data.get('metrics', {}).get('raised', 0)
                        }
        except Exception as e:
            print(f"    Clearbit API error: {e}")
        
        return None

    async def _analyze_size_from_content(self, domain: str) -> Dict:
        """Analyze company size indicators from website content"""
        
        signals = {}
        
        try:
            async with aiohttp.ClientSession() as session:
                # Check main page
                async with session.get(f'https://{domain}') as response:
                    if response.status == 200:
                        content = await response.text()
                        signals.update(self._extract_size_signals_from_content(content))
                
                # Check about page
                async with session.get(f'https://{domain}/about') as response:
                    if response.status == 200:
                        about_content = await response.text()
                        about_signals = self._extract_size_signals_from_content(about_content)
                        # Merge signals with higher weight for about page
                        for key, value in about_signals.items():
                            signals[f"about_{key}"] = value
                
                # Check careers page
                async with session.get(f'https://{domain}/careers') as response:
                    if response.status == 200:
                        careers_content = await response.text()
                        job_count = self._count_job_postings(careers_content)
                        signals['active_job_postings'] = job_count
        
        except Exception as e:
            print(f"    Content size analysis error: {e}")
        
        return signals

    def _extract_size_signals_from_content(self, content: str) -> Dict:
        """Extract company size signals from content"""
        
        signals = {}
        content_lower = content.lower()
        
        # Team size indicators
        team_patterns = [
            (r'(\d+)\+?\s*employees', 'employees_mentioned'),
            (r'team of (\d+)', 'team_size'),
            (r'(\d+)\+?\s*people', 'people_count'),
            (r'over (\d+)\s*staff', 'staff_count')
        ]
        
        for pattern, signal_name in team_patterns:
            matches = re.findall(pattern, content_lower)
            if matches:
                signals[signal_name] = max(int(match) for match in matches)
        
        # Office/location indicators
        if len(re.findall(r'office|location|headquarter', content_lower)) >= 3:
            signals['multiple_locations'] = True
        
        # Department mentions (indicates larger org)
        departments = ['marketing', 'sales', 'engineering', 'hr', 'finance', 'operations']
        department_mentions = sum(1 for dept in departments if dept in content_lower)
        signals['department_diversity'] = department_mentions
        
        # Client/customer scale indicators
        scale_indicators = [
            (r'(\d+)\+?\s*customers', 'customers_mentioned'),
            (r'(\d+)\+?\s*clients', 'clients_mentioned'),
            (r'(\d+)k\+?\s*users', 'users_k_mentioned'),
            (r'(\d+)m\+?\s*users', 'users_m_mentioned')
        ]
        
        for pattern, signal_name in scale_indicators:
            matches = re.findall(pattern, content_lower)
            if matches:
                signals[signal_name] = max(int(match) for match in matches)
        
        return signals

    def _count_job_postings(self, careers_content: str) -> int:
        """Count active job postings on careers page"""
        
        job_indicators = [
            'position', 'role', 'job', 'opening', 'vacancy',
            'engineer', 'developer', 'manager', 'analyst', 'specialist'
        ]
        
        job_count = 0
        for indicator in job_indicators:
            job_count += careers_content.lower().count(indicator)
        
        # Rough estimate: divide by 3 to avoid overcounting
        return min(job_count // 3, 50)  # Cap at 50 to be realistic

    def _calculate_company_size(self, signals: Dict) -> int:
        """Calculate estimated company size from multiple signals"""
        
        estimates = []
        
        # Direct employee mentions
        if 'employees_mentioned' in signals:
            estimates.append(signals['employees_mentioned'])
        if 'clearbit_employees' in signals and signals['clearbit_employees'] > 0:
            estimates.append(signals['clearbit_employees'])
        
        # Indirect size indicators
        if 'team_size' in signals:
            estimates.append(signals['team_size'])
        
        if 'active_job_postings' in signals:
            # Active hiring suggests size
            job_based_estimate = signals['active_job_postings'] * 3  # Rough multiplier
            estimates.append(job_based_estimate)
        
        if 'department_diversity' in signals:
            # More departments = larger company
            dept_based_estimate = signals['department_diversity'] * 8
            estimates.append(dept_based_estimate)
        
        # Customer scale to employee ratio
        if 'customers_mentioned' in signals:
            customer_count = signals['customers_mentioned']
            if customer_count >= 10000:
                estimates.append(50)  # Large customer base = substantial team
            elif customer_count >= 1000:
                estimates.append(25)
            elif customer_count >= 100:
                estimates.append(15)
        
        # Calculate weighted average (favor direct mentions)
        if estimates:
            # Weight direct mentions higher
            weighted_estimates = []
            for estimate in estimates:
                if estimate <= 5:  # Very small
                    weighted_estimates.extend([estimate] * 1)
                elif estimate <= 20:  # Small
                    weighted_estimates.extend([estimate] * 2)
                else:  # Larger estimates get higher weight
                    weighted_estimates.extend([estimate] * 3)
            
            return int(sum(weighted_estimates) / len(weighted_estimates))
        
        return 10  # Default assumption

    def _detect_growth_indicators(self, signals: Dict) -> List[str]:
        """Detect indicators of company growth"""
        
        growth_indicators = []
        
        if signals.get('active_job_postings', 0) >= 3:
            growth_indicators.append('active_hiring')
        
        if signals.get('clearbit_revenue', 0) >= 1000000:  # $1M+ revenue
            growth_indicators.append('substantial_revenue')
        
        if signals.get('clearbit_funding', 0) > 0:
            growth_indicators.append('funded')
        
        if signals.get('multiple_locations', False):
            growth_indicators.append('geographic_expansion')
        
        if signals.get('department_diversity', 0) >= 4:
            growth_indicators.append('organizational_maturity')
        
        return growth_indicators

    async def _detect_buying_signals(self, domain: str) -> Dict:
        """Detect buying readiness signals"""
        
        signals = []
        urgency_factors = []
        
        try:
            # Analyze website content for buying signals
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://{domain}') as response:
                    if response.status == 200:
                        content = await response.text()
                        content_signals = self._analyze_buying_signals_content(content)
                        signals.extend(content_signals['signals'])
                        urgency_factors.extend(content_signals['urgency_factors'])
                
                # Check blog/news for recent activity
                blog_signals = await self._check_blog_activity(session, domain)
                signals.extend(blog_signals)
        
        except Exception as e:
            print(f"    Buying signals detection error: {e}")
        
        # Calculate buying readiness score
        readiness_score = self._calculate_buying_readiness_score(signals, urgency_factors)
        
        return {
            'signals': signals,
            'urgency_factors': urgency_factors,
            'score': readiness_score
        }

    def _analyze_buying_signals_content(self, content: str) -> Dict:
        """Analyze content for buying signals"""
        
        content_lower = content.lower()
        signals = []
        urgency_factors = []
        
        # Check for immediate buying signals
        for signal_type, keywords in self.buying_signals['immediate'].items():
            for keyword in keywords:
                if keyword in content_lower:
                    signals.append(f"immediate_{signal_type}")
                    urgency_factors.append(signal_type)
                    break
        
        # Check for medium-term signals
        for signal_type, keywords in self.buying_signals['medium_term'].items():
            for keyword in keywords:
                if keyword in content_lower:
                    signals.append(f"medium_{signal_type}")
                    break
        
        # Check for long-term signals
        for signal_type, keywords in self.buying_signals['long_term'].items():
            for keyword in keywords:
                if keyword in content_lower:
                    signals.append(f"long_term_{signal_type}")
                    break
        
        # Specific high-value signals
        if any(term in content_lower for term in ['we are hiring', 'join our team', 'careers']):
            signals.append('active_hiring')
            urgency_factors.append('growth_phase')
        
        if any(term in content_lower for term in ['recently funded', 'series', 'investment']):
            signals.append('recent_funding')
            urgency_factors.append('capital_influx')
        
        return {
            'signals': signals,
            'urgency_factors': urgency_factors
        }

    async def _check_blog_activity(self, session: aiohttp.ClientSession, domain: str) -> List[str]:
        """Check blog activity for engagement signals"""
        
        blog_signals = []
        
        blog_urls = [f'https://{domain}/blog', f'https://{domain}/news', f'https://{domain}/updates']
        
        for blog_url in blog_urls:
            try:
                async with session.get(blog_url) as response:
                    if response.status == 200:
                        blog_content = await response.text()
                        
                        # Check for recent posts (rough estimation)
                        current_year = str(datetime.now().year)
                        current_month = datetime.now().strftime('%B').lower()
                        
                        if current_year in blog_content and current_month in blog_content.lower():
                            blog_signals.append('recent_blog_activity')
                        
                        # Check for growth/announcement content
                        if any(term in blog_content.lower() for term in ['announcement', 'launch', 'release']):
                            blog_signals.append('recent_announcements')
                        
                        break  # Found active blog
            except:
                continue
        
        return blog_signals

    def _calculate_buying_readiness_score(self, signals: List[str], urgency_factors: List[str]) -> int:
        """Calculate 0-100 buying readiness score"""
        
        score = 0
        
        # Base score from signals
        for signal in signals:
            if signal.startswith('immediate_'):
                score += 25
            elif signal.startswith('medium_'):
                score += 15
            elif signal.startswith('long_term_'):
                score += 8
            elif signal in ['active_hiring', 'recent_funding']:
                score += 30
            elif signal in ['recent_blog_activity', 'recent_announcements']:
                score += 10
        
        # Urgency multiplier
        if urgency_factors:
            urgency_multiplier = 1 + (len(urgency_factors) * 0.2)  # 20% per urgency factor
            score = int(score * urgency_multiplier)
        
        return min(score, 100)

    async def _analyze_competitive_position(self, domain: str) -> Dict:
        """Analyze competitive position and tech sophistication"""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://{domain}') as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        tech_score = self._calculate_tech_sophistication(content)
                        market_position = self._determine_market_position(content)
                        
                        return {
                            'sophistication': tech_score,
                            'position': market_position,
                            'analysis': {
                                'tech_stack_complexity': tech_score,
                                'market_indicators': self._extract_market_indicators(content)
                            }
                        }
        except Exception as e:
            print(f"    Competitive analysis error: {e}")
        
        return {
            'sophistication': 50,
            'position': 'unknown',
            'analysis': {}
        }

    def _calculate_tech_sophistication(self, content: str) -> int:
        """Calculate technology sophistication score"""
        
        score = 0
        content_lower = content.lower()
        
        # Modern tech indicators
        modern_tech = ['react', 'vue', 'angular', 'api', 'cloud', 'aws', 'azure', 'microservices']
        score += sum(5 for tech in modern_tech if tech in content_lower)
        
        # Advanced features
        advanced_features = ['machine learning', 'ai', 'automation', 'integration', 'webhook']
        score += sum(10 for feature in advanced_features if feature in content_lower)
        
        # Enterprise indicators
        enterprise_indicators = ['enterprise', 'sso', 'saml', 'compliance', 'security']
        score += sum(8 for indicator in enterprise_indicators if indicator in content_lower)
        
        # Mobile/responsive design
        if any(term in content_lower for term in ['mobile', 'responsive', 'app']):
            score += 10
        
        return min(score, 100)

    def _determine_market_position(self, content: str) -> str:
        """Determine market position based on content analysis"""
        
        content_lower = content.lower()
        
        # Leader indicators
        if any(term in content_lower for term in ['leader', 'leading', 'industry standard', 'award']):
            return 'leader'
        
        # Challenger indicators
        if any(term in content_lower for term in ['innovative', 'disrupting', 'next generation']):
            return 'challenger'
        
        # Niche indicators
        if any(term in content_lower for term in ['specialized', 'niche', 'focused', 'expert']):
            return 'niche'
        
        return 'follower'

    def _extract_market_indicators(self, content: str) -> List[str]:
        """Extract market position indicators"""
        
        indicators = []
        content_lower = content.lower()
        
        if 'fortune 500' in content_lower:
            indicators.append('enterprise_clients')
        
        if any(term in content_lower for term in ['trusted by', 'used by']):
            indicators.append('social_proof')
        
        if any(term in content_lower for term in ['award', 'recognition', 'certified']):
            indicators.append('industry_recognition')
        
        return indicators

    async def _analyze_decision_maker_signals(self, domain: str) -> Dict:
        """Analyze decision maker accessibility and contact signals"""
        
        signals = {}
        channels = ['email']  # Default channel
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://{domain}') as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Contact information availability
                        if 'contact' in content.lower():
                            signals['contact_page_available'] = True
                            channels.append('contact_form')
                        
                        # Social media presence
                        social_platforms = ['linkedin', 'twitter', 'facebook']
                        for platform in social_platforms:
                            if platform in content.lower():
                                signals[f'{platform}_presence'] = True
                                channels.append(platform)
                        
                        # Direct phone/email visibility
                        if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', content):
                            signals['phone_visible'] = True
                            channels.append('phone')
                        
                        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content):
                            signals['email_visible'] = True
        
        except Exception as e:
            print(f"    Decision maker analysis error: {e}")
        
        return {
            'signals': signals,
            'channels': list(set(channels))  # Remove duplicates
        }

    async def _extract_company_name(self, domain: str) -> str:
        """Extract clean company name"""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://{domain}') as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Try to extract from title tag
                        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                        if title_match:
                            title = title_match.group(1).strip()
                            # Clean up title
                            company_name = title.split('|')[0].split('-')[0].strip()
                            if len(company_name) > 3 and len(company_name) < 50:
                                return company_name
        except:
            pass
        
        # Fallback to domain name
        return domain.split('.')[0].replace('-', ' ').title()

    def _calculate_qualification_score(self, business_model: Dict, company_size: Dict, 
                                     buying_signals: Dict, competitive_pos: Dict) -> int:
        """Calculate comprehensive qualification score"""
        
        score = 0
        
        # Business model score (30%)
        model_score = business_model.get('confidence', 0) * 0.3
        if business_model['model'] in ['saas', 'marketplace']:
            model_score *= 1.2  # Boost for high-value models
        score += model_score
        
        # Company size score (25%)
        employees = company_size['employees']
        if employees >= 50:
            size_score = 25
        elif employees >= 20:
            size_score = 20
        elif employees >= 10:
            size_score = 15
        else:
            size_score = 10
        score += size_score
        
        # Buying readiness score (25%)
        readiness_score = buying_signals['score'] * 0.25
        score += readiness_score
        
        # Tech sophistication score (20%)
        tech_score = competitive_pos['sophistication'] * 0.2
        score += tech_score
        
        return min(int(score), 100)

    def _calculate_conversion_probability(self, qualification_score: int, buying_signals: Dict) -> float:
        """Calculate conversion probability based on scores and signals"""
        
        base_probability = qualification_score / 100 * 0.3  # 30% max base rate
        
        # Boost based on buying signals
        urgency_boost = len(buying_signals.get('urgency_factors', [])) * 0.1
        signal_boost = min(len(buying_signals.get('signals', [])) * 0.05, 0.2)
        
        total_probability = base_probability + urgency_boost + signal_boost
        
        return min(total_probability, 0.8)  # Cap at 80%

    def _recommend_approach(self, business_model: Dict, buying_signals: Dict, company_size: Dict) -> str:
        """Recommend outreach approach based on intelligence"""
        
        urgency_factors = buying_signals.get('urgency_factors', [])
        company_tier = company_size.get('tier', 'small_business')
        
        if urgency_factors and 'growth_phase' in urgency_factors:
            return 'immediate_outreach_growth_angle'
        elif urgency_factors and 'capital_influx' in urgency_factors:
            return 'immediate_outreach_investment_angle'
        elif company_tier in ['enterprise', 'mid_market']:
            return 'enterprise_sales_process'
        elif business_model['model'] == 'saas':
            return 'technical_demonstration_focus'
        else:
            return 'standard_consultative_approach'

# Demo function
async def demo_enhanced_business_intelligence():
    """Demo the enhanced business intelligence system"""
    
    print("\n🎯 ENHANCED BUSINESS INTELLIGENCE DEMO")
    print("=" * 70)
    
    engine = EnhancedBusinessIntelligence()
    
    # Test domains
    test_domains = [
        'shopify.com',
        'exemplo-saas.io',
        'exemplo-agency.com.br'
    ]
    
    for domain in test_domains[:1]:  # Test one domain for demo
        print(f"\n" + "="*60)
        intelligence = await engine.analyze_comprehensive_business_intelligence(domain)
        
        print(f"\n🏢 BUSINESS INTELLIGENCE REPORT:")
        print(f"  Company: {intelligence.company_name}")
        print(f"  Domain: {intelligence.domain}")
        print(f"  Business Model: {intelligence.business_model}")
        print(f"  Company Size: {intelligence.estimated_employees} employees ({intelligence.revenue_tier})")
        print(f"  Budget Tier: {intelligence.budget_tier}")
        print(f"  Buying Readiness: {intelligence.buying_readiness_score}/100")
        print(f"  Tech Sophistication: {intelligence.tech_sophistication_score}/100")
        print(f"  Market Position: {intelligence.market_position}")
        print(f"  Qualification Score: {intelligence.total_qualification_score}/100")
        print(f"  Conversion Probability: {intelligence.conversion_probability:.1%}")
        print(f"  Recommended Approach: {intelligence.recommended_approach}")
        
        if intelligence.buying_signals:
            print(f"  Buying Signals: {', '.join(intelligence.buying_signals[:3])}")
        
        if intelligence.urgency_factors:
            print(f"  Urgency Factors: {', '.join(intelligence.urgency_factors)}")
    
    print(f"\n✅ Enhanced Business Intelligence operational!")

if __name__ == "__main__":
    asyncio.run(demo_enhanced_business_intelligence())
