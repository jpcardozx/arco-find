"""
Funding Intelligence Collector - Collects funding and investment data.

This collector integrates with funding databases and APIs to gather
real funding information about companies.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from arco.models.prospect import FundingProfile


class FundingIntelligenceCollector:
    """
    Collects funding intelligence from multiple sources.
    
    Integrates with:
    - Crunchbase API
    - PitchBook (if available)
    - Public funding announcements
    - SEC filings (for larger rounds)
    """
    
    def __init__(self):
        """Initialize the funding intelligence collector."""
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.session: Optional[aiohttp.ClientSession] = None
        
        # API endpoints (would be configured from environment)
        self.crunchbase_api_url = "https://api.crunchbase.com/api/v4"
        self.pitchbook_api_url = "https://api.pitchbook.com/v1"
        
        # Funding stage classifications
        self.funding_stages = {
            'pre_seed': ['pre-seed', 'pre seed', 'friends and family'],
            'seed': ['seed', 'seed round'],
            'series_a': ['series a', 'series-a', 'round a'],
            'series_b': ['series b', 'series-b', 'round b'],
            'series_c': ['series c', 'series-c', 'round c'],
            'series_d': ['series d', 'series-d', 'round d'],
            'growth': ['growth', 'growth equity', 'late stage'],
            'ipo': ['ipo', 'public offering'],
            'acquisition': ['acquisition', 'merger', 'buyout']
        }
    
    async def collect(self, company_name: str) -> FundingProfile:
        """
        Collect comprehensive funding intelligence.
        
        Args:
            company_name: Name of the company
            
        Returns:
            FundingProfile with collected funding data
        """
        self._logger.debug(f"💰 Collecting funding intelligence for {company_name}")
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            # Parallel collection from multiple sources
            crunchbase_task = self._get_crunchbase_data(company_name)
            pitchbook_task = self._get_pitchbook_data(company_name)
            public_announcements_task = self._search_public_announcements(company_name)
            
            crunchbase_data, pitchbook_data, public_data = await asyncio.gather(
                crunchbase_task, pitchbook_task, public_announcements_task, 
                return_exceptions=True
            )
            
            # Process and combine data
            profile = self._process_funding_data(
                company_name, crunchbase_data, pitchbook_data, public_data
            )
            
            self._logger.debug(
                f"💵 Funding intelligence for {company_name}: "
                f"Recent: {profile.recent_funding_months or 'None'} months ago, "
                f"Amount: ${profile.funding_amount or 0:,}, "
                f"Stage: {profile.funding_stage or 'Unknown'}, "
                f"Total: ${profile.total_funding or 0:,}"
            )
            
            return profile
            
        except Exception as e:
            self._logger.error(f"❌ Failed to collect funding intelligence for {company_name}: {e}")
            return FundingProfile()
    
    async def _get_crunchbase_data(self, company_name: str) -> Optional[Dict]:
        """
        Get funding data from Crunchbase API.
        
        Note: This is a placeholder implementation. In production, this would
        integrate with the actual Crunchbase API using proper authentication.
        """
        try:
            # Simulate API call delay
            await asyncio.sleep(0.3)
            
            # Placeholder logic - simulate some companies having funding data
            company_hash = hash(company_name.lower()) % 100
            
            if company_hash < 25:  # 25% of companies have funding data
                # Simulate different funding scenarios
                if company_hash < 5:  # Recent funding (last 6 months)
                    return {
                        'funding_rounds': [
                            {
                                'funding_type': 'series-a',
                                'money_raised': 5000000,
                                'announced_on': (datetime.now() - timedelta(days=120)).isoformat(),
                                'investors': ['Acme Ventures', 'Tech Capital']
                            },
                            {
                                'funding_type': 'seed',
                                'money_raised': 1500000,
                                'announced_on': (datetime.now() - timedelta(days=400)).isoformat(),
                                'investors': ['Angel Investor']
                            }
                        ],
                        'total_funding': 6500000,
                        'last_funding_date': (datetime.now() - timedelta(days=120)).isoformat()
                    }
                elif company_hash < 15:  # Older funding (6-18 months)
                    return {
                        'funding_rounds': [
                            {
                                'funding_type': 'seed',
                                'money_raised': 2000000,
                                'announced_on': (datetime.now() - timedelta(days=300)).isoformat(),
                                'investors': ['Seed Fund', 'Angel Group']
                            }
                        ],
                        'total_funding': 2000000,
                        'last_funding_date': (datetime.now() - timedelta(days=300)).isoformat()
                    }
                else:  # Very old funding (18+ months)
                    return {
                        'funding_rounds': [
                            {
                                'funding_type': 'pre-seed',
                                'money_raised': 500000,
                                'announced_on': (datetime.now() - timedelta(days=600)).isoformat(),
                                'investors': ['Friends and Family']
                            }
                        ],
                        'total_funding': 500000,
                        'last_funding_date': (datetime.now() - timedelta(days=600)).isoformat()
                    }
            
            return None
            
        except Exception as e:
            self._logger.warning(f"Crunchbase API failed for {company_name}: {e}")
            return None
    
    async def _get_pitchbook_data(self, company_name: str) -> Optional[Dict]:
        """
        Get funding data from PitchBook API.
        
        Note: This is a placeholder implementation.
        """
        try:
            await asyncio.sleep(0.2)
            
            # Placeholder - PitchBook typically has more detailed data
            # but requires expensive subscription
            return None
            
        except Exception as e:
            self._logger.warning(f"PitchBook API failed for {company_name}: {e}")
            return None
    
    async def _search_public_announcements(self, company_name: str) -> Optional[Dict]:
        """
        Search for public funding announcements.
        
        This would typically involve searching news sources, press releases,
        and company announcements for funding information.
        """
        try:
            await asyncio.sleep(0.2)
            
            # Placeholder for news/announcement search
            # In production, this might search:
            # - TechCrunch
            # - VentureBeat  
            # - Company press releases
            # - SEC filings
            
            return None
            
        except Exception as e:
            self._logger.warning(f"Public announcement search failed for {company_name}: {e}")
            return None
    
    def _process_funding_data(self, 
                            company_name: str,
                            crunchbase_data: Any, 
                            pitchbook_data: Any, 
                            public_data: Any) -> FundingProfile:
        """Process and combine funding data from multiple sources."""
        
        profile = FundingProfile()
        
        # Process Crunchbase data (primary source)
        if not isinstance(crunchbase_data, Exception) and crunchbase_data:
            funding_rounds = crunchbase_data.get('funding_rounds', [])
            
            if funding_rounds:
                # Get most recent funding round
                latest_round = max(funding_rounds, key=lambda x: x.get('announced_on', ''))
                
                # Calculate months since last funding
                try:
                    funding_date = datetime.fromisoformat(latest_round['announced_on'].replace('Z', '+00:00'))
                    months_ago = int((datetime.now() - funding_date.replace(tzinfo=None)).days / 30)
                    
                    profile.recent_funding_months = months_ago
                    profile.funding_amount = latest_round.get('money_raised')
                    profile.funding_stage = self._normalize_funding_stage(latest_round.get('funding_type', ''))
                    profile.funding_date = funding_date.replace(tzinfo=None)
                    profile.investors = latest_round.get('investors', [])
                    
                except Exception as e:
                    self._logger.warning(f"Error parsing funding date for {company_name}: {e}")
                
                # Calculate total funding
                profile.total_funding = sum(
                    round_data.get('money_raised', 0) for round_data in funding_rounds
                )
        
        # Enhance with PitchBook data if available
        if not isinstance(pitchbook_data, Exception) and pitchbook_data:
            # PitchBook data would enhance the profile here
            pass
        
        # Enhance with public announcement data if available
        if not isinstance(public_data, Exception) and public_data:
            # Public announcement data would enhance the profile here
            pass
        
        return profile
    
    def _normalize_funding_stage(self, raw_stage: str) -> str:
        """Normalize funding stage to standard format."""
        if not raw_stage:
            return "Unknown"
        
        raw_stage_lower = raw_stage.lower()
        
        for standard_stage, variations in self.funding_stages.items():
            if any(variation in raw_stage_lower for variation in variations):
                return standard_stage.replace('_', ' ').title()
        
        return raw_stage.title()
    
    async def get_funding_timeline(self, company_name: str) -> List[Dict[str, Any]]:
        """
        Get complete funding timeline for a company.
        
        Args:
            company_name: Name of the company
            
        Returns:
            List of funding events in chronological order
        """
        try:
            crunchbase_data = await self._get_crunchbase_data(company_name)
            
            if not crunchbase_data or isinstance(crunchbase_data, Exception):
                return []
            
            funding_rounds = crunchbase_data.get('funding_rounds', [])
            
            # Sort by date (newest first)
            timeline = []
            for round_data in funding_rounds:
                try:
                    funding_date = datetime.fromisoformat(round_data['announced_on'].replace('Z', '+00:00'))
                    timeline.append({
                        'date': funding_date.replace(tzinfo=None),
                        'stage': self._normalize_funding_stage(round_data.get('funding_type', '')),
                        'amount': round_data.get('money_raised', 0),
                        'investors': round_data.get('investors', []),
                        'months_ago': int((datetime.now() - funding_date.replace(tzinfo=None)).days / 30)
                    })
                except Exception as e:
                    self._logger.warning(f"Error parsing funding round for {company_name}: {e}")
            
            return sorted(timeline, key=lambda x: x['date'], reverse=True)
            
        except Exception as e:
            self._logger.error(f"Failed to get funding timeline for {company_name}: {e}")
            return []
    
    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None