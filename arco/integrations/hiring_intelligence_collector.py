"""
Hiring Intelligence Collector - Collects hiring activity and growth signals.

This collector analyzes job postings and hiring patterns to identify
growth signals and technology budget indicators.
"""

import asyncio
import aiohttp
import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from arco.models.prospect import HiringActivity


class HiringIntelligenceCollector:
    """
    Collects hiring intelligence from job posting sources.
    
    Analyzes:
    - Job posting volume and trends
    - Technology-specific hiring
    - Leadership hiring patterns
    - Growth signal indicators
    """
    
    def __init__(self):
        """Initialize the hiring intelligence collector."""
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Technology job keywords
        self.tech_keywords = {
            'engineering': ['software engineer', 'developer', 'programmer', 'backend', 'frontend', 
                          'full stack', 'devops', 'sre', 'platform engineer'],
            'data': ['data scientist', 'data engineer', 'data analyst', 'machine learning', 
                    'ai engineer', 'analytics'],
            'product': ['product manager', 'product owner', 'ux designer', 'ui designer', 
                       'product designer'],
            'security': ['security engineer', 'cybersecurity', 'infosec', 'security analyst'],
            'infrastructure': ['cloud engineer', 'systems engineer', 'network engineer', 
                             'infrastructure engineer']
        }
        
        # Leadership keywords
        self.leadership_keywords = [
            'cto', 'chief technology officer', 'vp engineering', 'vp of engineering',
            'head of engineering', 'engineering director', 'technical director',
            'head of product', 'vp product', 'chief product officer',
            'head of data', 'vp data', 'chief data officer'
        ]
        
        # Job posting sources (would be configured)
        self.job_sources = {
            'linkedin': 'https://www.linkedin.com/jobs/search',
            'indeed': 'https://www.indeed.com/jobs',
            'glassdoor': 'https://www.glassdoor.com/Jobs',
            'company_careers': None  # Company career pages
        }
    
    async def collect(self, company_name: str) -> HiringActivity:
        """
        Collect comprehensive hiring intelligence.
        
        Args:
            company_name: Name of the company
            
        Returns:
            HiringActivity with collected hiring data
        """
        self._logger.debug(f"👥 Collecting hiring intelligence for {company_name}")
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            # Parallel collection from multiple sources
            linkedin_task = self._get_linkedin_jobs(company_name)
            indeed_task = self._get_indeed_jobs(company_name)
            company_careers_task = self._get_company_career_page_jobs(company_name)
            
            linkedin_data, indeed_data, careers_data = await asyncio.gather(
                linkedin_task, indeed_task, company_careers_task,
                return_exceptions=True
            )
            
            # Process and combine data
            activity = self._process_hiring_data(
                company_name, linkedin_data, indeed_data, careers_data
            )
            
            self._logger.debug(
                f"📊 Hiring intelligence for {company_name}: "
                f"Total Jobs: {activity.total_job_postings}, "
                f"Tech Jobs: {activity.tech_job_postings}, "
                f"Leadership: {activity.tech_leadership_hiring}, "
                f"Growth Score: {activity.growth_signal_score}/100"
            )
            
            return activity
            
        except Exception as e:
            self._logger.error(f"❌ Failed to collect hiring intelligence for {company_name}: {e}")
            return HiringActivity()
    
    async def _get_linkedin_jobs(self, company_name: str) -> Optional[Dict]:
        """
        Get job postings from LinkedIn.
        
        Note: This is a placeholder implementation. In production, this would
        integrate with LinkedIn's API or use web scraping (following ToS).
        """
        try:
            # Simulate API call delay
            await asyncio.sleep(0.3)
            
            # Placeholder logic - simulate job posting data
            company_hash = hash(company_name.lower()) % 100
            
            if company_hash < 40:  # 40% of companies have job postings
                # Simulate different hiring scenarios
                if company_hash < 10:  # High growth companies
                    return {
                        'total_jobs': 15,
                        'job_titles': [
                            'Senior Software Engineer',
                            'Product Manager',
                            'DevOps Engineer',
                            'Data Scientist',
                            'VP of Engineering',
                            'Frontend Developer',
                            'Backend Developer',
                            'UX Designer',
                            'Security Engineer',
                            'Cloud Architect'
                        ],
                        'posted_dates': [
                            (datetime.now() - timedelta(days=5)).isoformat(),
                            (datetime.now() - timedelta(days=10)).isoformat(),
                            (datetime.now() - timedelta(days=15)).isoformat()
                        ]
                    }
                elif company_hash < 25:  # Medium growth
                    return {
                        'total_jobs': 6,
                        'job_titles': [
                            'Software Engineer',
                            'Product Manager',
                            'Marketing Manager',
                            'Sales Representative',
                            'Customer Success Manager',
                            'Data Analyst'
                        ],
                        'posted_dates': [
                            (datetime.now() - timedelta(days=20)).isoformat(),
                            (datetime.now() - timedelta(days=30)).isoformat()
                        ]
                    }
                else:  # Low growth
                    return {
                        'total_jobs': 2,
                        'job_titles': [
                            'Junior Developer',
                            'Customer Support'
                        ],
                        'posted_dates': [
                            (datetime.now() - timedelta(days=45)).isoformat()
                        ]
                    }
            
            return None
            
        except Exception as e:
            self._logger.warning(f"LinkedIn jobs API failed for {company_name}: {e}")
            return None
    
    async def _get_indeed_jobs(self, company_name: str) -> Optional[Dict]:
        """
        Get job postings from Indeed.
        
        Note: This is a placeholder implementation.
        """
        try:
            await asyncio.sleep(0.2)
            
            # Placeholder - Indeed data would supplement LinkedIn data
            return None
            
        except Exception as e:
            self._logger.warning(f"Indeed jobs API failed for {company_name}: {e}")
            return None
    
    async def _get_company_career_page_jobs(self, company_name: str) -> Optional[Dict]:
        """
        Get job postings from company career page.
        
        This would involve finding and scraping the company's career page.
        """
        try:
            await asyncio.sleep(0.2)
            
            # Placeholder for career page scraping
            # In production, this would:
            # 1. Find company website
            # 2. Locate careers/jobs page
            # 3. Extract job listings
            # 4. Parse job titles and descriptions
            
            return None
            
        except Exception as e:
            self._logger.warning(f"Company career page scraping failed for {company_name}: {e}")
            return None
    
    def _process_hiring_data(self, 
                           company_name: str,
                           linkedin_data: Any,
                           indeed_data: Any,
                           careers_data: Any) -> HiringActivity:
        """Process and combine hiring data from multiple sources."""
        
        activity = HiringActivity()
        all_job_titles = []
        
        # Process LinkedIn data (primary source)
        if not isinstance(linkedin_data, Exception) and linkedin_data:
            activity.total_job_postings = linkedin_data.get('total_jobs', 0)
            all_job_titles.extend(linkedin_data.get('job_titles', []))
        
        # Process Indeed data (supplementary)
        if not isinstance(indeed_data, Exception) and indeed_data:
            activity.total_job_postings += indeed_data.get('total_jobs', 0)
            all_job_titles.extend(indeed_data.get('job_titles', []))
        
        # Process company careers data (supplementary)
        if not isinstance(careers_data, Exception) and careers_data:
            activity.total_job_postings += careers_data.get('total_jobs', 0)
            all_job_titles.extend(careers_data.get('job_titles', []))
        
        # Analyze job titles
        if all_job_titles:
            activity.tech_job_postings = self._count_tech_jobs(all_job_titles)
            activity.tech_leadership_hiring = self._count_leadership_jobs(all_job_titles)
            activity.key_positions = self._extract_key_positions(all_job_titles)
            activity.growth_signal_score = self._calculate_growth_signal_score(activity)
        
        return activity
    
    def _count_tech_jobs(self, job_titles: List[str]) -> int:
        """Count technology-related job postings."""
        tech_count = 0
        
        for title in job_titles:
            title_lower = title.lower()
            
            # Check against all tech keyword categories
            for category, keywords in self.tech_keywords.items():
                if any(keyword in title_lower for keyword in keywords):
                    tech_count += 1
                    break  # Don't double-count
        
        return tech_count
    
    def _count_leadership_jobs(self, job_titles: List[str]) -> int:
        """Count technology leadership job postings."""
        leadership_count = 0
        
        for title in job_titles:
            title_lower = title.lower()
            
            if any(keyword in title_lower for keyword in self.leadership_keywords):
                leadership_count += 1
        
        return leadership_count
    
    def _extract_key_positions(self, job_titles: List[str]) -> List[str]:
        """Extract key positions that indicate growth or investment."""
        key_positions = []
        
        # High-impact positions that indicate growth/investment
        high_impact_keywords = [
            'vp', 'vice president', 'head of', 'director', 'chief',
            'senior engineer', 'principal engineer', 'staff engineer',
            'product manager', 'engineering manager', 'tech lead'
        ]
        
        for title in job_titles:
            title_lower = title.lower()
            
            if any(keyword in title_lower for keyword in high_impact_keywords):
                key_positions.append(title)
        
        return key_positions[:10]  # Limit to top 10
    
    def _calculate_growth_signal_score(self, activity: HiringActivity) -> int:
        """Calculate growth signal score (0-100) based on hiring activity."""
        score = 0
        
        # Total job volume (30 points max)
        if activity.total_job_postings >= 20:
            score += 30
        elif activity.total_job_postings >= 10:
            score += 20
        elif activity.total_job_postings >= 5:
            score += 10
        elif activity.total_job_postings >= 1:
            score += 5
        
        # Tech job ratio (40 points max)
        if activity.total_job_postings > 0:
            tech_ratio = activity.tech_job_postings / activity.total_job_postings
            score += int(tech_ratio * 40)
        
        # Leadership hiring (30 points max)
        if activity.tech_leadership_hiring >= 3:
            score += 30
        elif activity.tech_leadership_hiring >= 2:
            score += 20
        elif activity.tech_leadership_hiring >= 1:
            score += 10
        
        return min(score, 100)
    
    async def analyze_hiring_trends(self, company_name: str) -> Dict[str, Any]:
        """
        Analyze hiring trends and patterns.
        
        Args:
            company_name: Name of the company
            
        Returns:
            Hiring trends analysis
        """
        try:
            activity = await self.collect(company_name)
            
            # Analyze trends
            trends = {
                'hiring_velocity': self._categorize_hiring_velocity(activity.total_job_postings),
                'tech_focus': activity.tech_job_postings / max(activity.total_job_postings, 1),
                'leadership_expansion': activity.tech_leadership_hiring > 0,
                'growth_indicators': [],
                'budget_signals': []
            }
            
            # Growth indicators
            if activity.total_job_postings >= 10:
                trends['growth_indicators'].append('High hiring volume')
            
            if activity.tech_job_postings >= 5:
                trends['growth_indicators'].append('Significant tech hiring')
            
            if activity.tech_leadership_hiring >= 1:
                trends['growth_indicators'].append('Leadership expansion')
            
            # Budget signals
            if activity.tech_leadership_hiring >= 2:
                trends['budget_signals'].append('Major tech investment (multiple leadership hires)')
            
            if activity.tech_job_postings >= 8:
                trends['budget_signals'].append('Substantial tech budget (large team expansion)')
            
            return trends
            
        except Exception as e:
            self._logger.error(f"Failed to analyze hiring trends for {company_name}: {e}")
            return {}
    
    def _categorize_hiring_velocity(self, total_jobs: int) -> str:
        """Categorize hiring velocity based on job count."""
        if total_jobs >= 20:
            return "Very High"
        elif total_jobs >= 10:
            return "High"
        elif total_jobs >= 5:
            return "Medium"
        elif total_jobs >= 1:
            return "Low"
        else:
            return "None"
    
    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None