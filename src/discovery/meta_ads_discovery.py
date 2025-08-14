#!/usr/bin/env python3
"""
Meta Ad Library Discovery Engine
Descoberta inteligente de anunciantes por vertical usando Meta Ad Library
"""

import asyncio
import aiohttp
from playwright.async_api import async_playwright
import json
import sqlite3
from datetime import datetime
import logging
from urllib.parse import urlparse, parse_qs
import re
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../../data/discovery.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MetaAdsDiscovery:
    def __init__(self, db_path="../../data/prospects.db"):
        self.db_path = db_path
        self.setup_database()
        self.session_stats = {
            'advertisers_found': 0,
            'ads_scraped': 0,
            'errors': 0,
            'start_time': time.time()
        }
    
    def setup_database(self):
        """Initialize SQLite database with optimized schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Prospects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prospects (
                id INTEGER PRIMARY KEY,
                domain TEXT UNIQUE,
                company_name TEXT,
                page_id TEXT,
                view_all_page_id TEXT,
                vertical TEXT,
                country TEXT,
                category TEXT,
                discovered_at TIMESTAMP,
                last_scraped TIMESTAMP,
                status TEXT DEFAULT 'discovered'
            )
        """)
        
        # Ads table for activity tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ads (
                id INTEGER PRIMARY KEY,
                library_id TEXT UNIQUE,
                prospect_id INTEGER,
                ad_text TEXT,
                landing_url TEXT,
                start_date TEXT,
                end_date TEXT,
                platforms TEXT,
                countries TEXT,
                media_urls TEXT,
                discovered_at TIMESTAMP,
                FOREIGN KEY (prospect_id) REFERENCES prospects (id)
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prospects_vertical ON prospects(vertical)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prospects_discovered ON prospects(discovered_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ads_prospect ON ads(prospect_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ads_start_date ON ads(start_date)")
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    async def discover_advertisers_by_vertical(self, vertical_config, max_advertisers=100):
        """
        Discover advertisers for specific vertical with rate limiting
        
        Args:
            vertical_config: Dict with 'name', 'search_terms', 'country'
            max_advertisers: Maximum advertisers to discover
        """
        vertical_name = vertical_config['name']
        search_terms = vertical_config['search_terms']
        country = vertical_config.get('country', 'BR')
        
        logger.info(f"Starting discovery for {vertical_name} vertical")
        
        advertisers = []
        
        async with async_playwright() as p:
            # Launch browser with stealth settings
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage'
                ]
            )
            
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            page = await context.new_page()
            
            for term in search_terms:
                if len(advertisers) >= max_advertisers:
                    break
                    
                logger.info(f"Searching for: {term} in {country}")
                
                try:
                    # Build search URL
                    search_url = self._build_search_url(term, country)
                    
                    await page.goto(search_url)
                    await page.wait_for_timeout(3000)
                    
                    # Extract advertisers from search results
                    term_advertisers = await self._extract_advertisers_from_page(page, vertical_name, term, country)
                    advertisers.extend(term_advertisers)
                    
                    logger.info(f"Found {len(term_advertisers)} advertisers for term: {term}")
                    
                    # Rate limiting
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error searching for term {term}: {e}")
                    self.session_stats['errors'] += 1
                    continue
            
            await browser.close()
        
        # Save to database
        self._save_advertisers(advertisers)
        self.session_stats['advertisers_found'] = len(advertisers)
        
        logger.info(f"Discovery completed: {len(advertisers)} advertisers found for {vertical_name}")
        return advertisers
    
    def _build_search_url(self, term, country):
        """Build Meta Ad Library search URL"""
        base_url = "https://www.facebook.com/ads/library/"
        params = {
            'active_status': 'active',
            'ad_type': 'all',
            'country': country,
            'search_type': 'keyword_unordered',
            'q': term
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"
    
    async def _extract_advertisers_from_page(self, page, vertical, search_term, country):
        """Extract advertiser data from Meta Ad Library search results"""
        advertisers = []
        max_pages = 5
        
        for page_num in range(max_pages):
            try:
                # Wait for content to load
                await page.wait_for_selector('[data-testid="pagination_display_count"]', timeout=10000)
                
                # Look for advertiser page cards
                page_cards = await page.query_selector_all('[data-testid="search_result_ad"]')
                
                if not page_cards:
                    logger.warning(f"No advertiser cards found on page {page_num + 1}")
                    break
                
                for card in page_cards:
                    try:
                        advertiser_data = await self._extract_advertiser_from_card(card, vertical, search_term, country)
                        if advertiser_data:
                            advertisers.append(advertiser_data)
                    except Exception as e:
                        logger.error(f"Error extracting advertiser from card: {e}")
                        continue
                
                # Try to go to next page
                next_button = await page.query_selector('[aria-label="Next"]')
                if next_button and await next_button.is_enabled():
                    await next_button.click()
                    await page.wait_for_timeout(2000)
                else:
                    break
                    
            except Exception as e:
                logger.error(f"Error on page {page_num + 1}: {e}")
                break
        
        return advertisers
    
    async def _extract_advertiser_from_card(self, card, vertical, search_term, country):
        """Extract advertiser data from individual search result card"""
        try:
            # Get advertiser name
            name_elem = await card.query_selector('[data-testid="advertiser_name"]')
            company_name = await name_elem.inner_text() if name_elem else None
            
            if not company_name:
                return None
            
            # Get page link to extract page ID
            page_link = await card.query_selector('a[href*="view_all_page_id"]')
            if not page_link:
                return None
            
            href = await page_link.get_attribute('href')
            view_all_page_id = self._extract_page_id_from_url(href)
            
            if not view_all_page_id:
                return None
            
            # Extract domain from any visible ads
            domain = await self._extract_domain_from_card(card)
            
            advertiser_data = {
                'company_name': company_name.strip(),
                'page_id': view_all_page_id,  # Using view_all_page_id as primary ID
                'view_all_page_id': view_all_page_id,
                'domain': domain,
                'vertical': vertical,
                'country': country,
                'search_term': search_term,
                'discovered_at': datetime.now().isoformat()
            }
            
            return advertiser_data
            
        except Exception as e:
            logger.error(f"Error extracting advertiser data: {e}")
            return None
    
    async def _extract_domain_from_card(self, card):
        """Extract domain from ad preview in search result card"""
        try:
            # Look for destination URL or domain display
            domain_elems = await card.query_selector_all('a[href*="l.facebook.com"]')
            
            for elem in domain_elems:
                href = await elem.get_attribute('href')
                if href:
                    actual_url = self._extract_landing_url_from_redirect(href)
                    if actual_url:
                        domain = urlparse(actual_url).netloc
                        if domain and not domain.startswith('www.'):
                            return domain
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting domain: {e}")
            return None
    
    def _extract_page_id_from_url(self, url):
        """Extract view_all_page_id from Meta Ad Library URL"""
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            return params.get('view_all_page_id', [None])[0]
        except Exception as e:
            logger.error(f"Error extracting page ID: {e}")
            return None
    
    def _extract_landing_url_from_redirect(self, facebook_redirect_url):
        """Extract actual landing URL from Facebook redirect"""
        try:
            parsed = urlparse(facebook_redirect_url)
            params = parse_qs(parsed.query)
            return params.get('u', [None])[0]
        except Exception as e:
            return facebook_redirect_url
    
    async def scrape_ads_for_advertiser(self, view_all_page_id, max_ads=30):
        """
        Scrape individual ads for specific advertiser
        
        Args:
            view_all_page_id: Facebook page ID for advertiser
            max_ads: Maximum ads to scrape per advertiser
        """
        logger.info(f"Scraping ads for advertiser: {view_all_page_id}")
        
        ads = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Build advertiser-specific URL
                ads_url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&view_all_page_id={view_all_page_id}"
                
                await page.goto(ads_url)
                await page.wait_for_timeout(3000)
                
                ads_scraped = 0
                scroll_attempts = 0
                max_scrolls = 10
                
                while ads_scraped < max_ads and scroll_attempts < max_scrolls:
                    # Find ad cards
                    ad_cards = await page.query_selector_all('[data-testid="search_result_ad"]')
                    
                    for card in ad_cards[ads_scraped:]:
                        if ads_scraped >= max_ads:
                            break
                            
                        ad_data = await self._extract_ad_data_from_card(card, view_all_page_id)
                        if ad_data:
                            ads.append(ad_data)
                            ads_scraped += 1
                    
                    # Scroll for more ads
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(2000)
                    scroll_attempts += 1
                
            except Exception as e:
                logger.error(f"Error scraping ads for {view_all_page_id}: {e}")
            
            finally:
                await browser.close()
        
        # Save ads to database
        self._save_ads(ads, view_all_page_id)
        self.session_stats['ads_scraped'] += len(ads)
        
        logger.info(f"Scraped {len(ads)} ads for advertiser {view_all_page_id}")
        return ads
    
    async def _extract_ad_data_from_card(self, card, page_id):
        """Extract ad data from individual ad card"""
        try:
            ad_data = {
                'page_id': page_id,
                'discovered_at': datetime.now().isoformat()
            }
            
            # Ad text
            text_elem = await card.query_selector('[data-testid="ad_snapshot_body_text"]')
            ad_data['ad_text'] = await text_elem.inner_text() if text_elem else ""
            
            # Landing URL
            link_elem = await card.query_selector('a[href*="l.facebook.com"]')
            if link_elem:
                href = await link_elem.get_attribute('href')
                ad_data['landing_url'] = self._extract_landing_url_from_redirect(href)
            
            # Start date
            date_elem = await card.query_selector('[data-testid="ad_start_date"]')
            ad_data['start_date'] = await date_elem.inner_text() if date_elem else ""
            
            # Platforms
            platform_elems = await card.query_selector_all('[data-testid="platforms"] img')
            platforms = []
            for platform_elem in platform_elems:
                alt = await platform_elem.get_attribute('alt')
                if alt:
                    platforms.append(alt)
            ad_data['platforms'] = ','.join(platforms)
            
            # Generate unique library ID
            ad_data['library_id'] = self._generate_library_id(ad_data)
            
            return ad_data
            
        except Exception as e:
            logger.error(f"Error extracting ad data: {e}")
            return None
    
    def _generate_library_id(self, ad_data):
        """Generate unique identifier for ad"""
        import hashlib
        content = f"{ad_data.get('ad_text', '')}{ad_data.get('landing_url', '')}{ad_data.get('start_date', '')}{ad_data.get('page_id', '')}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _save_advertisers(self, advertisers):
        """Save advertisers to database with conflict resolution"""
        if not advertisers:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for advertiser in advertisers:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO prospects 
                    (domain, company_name, page_id, view_all_page_id, vertical, country, discovered_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    advertiser.get('domain'),
                    advertiser['company_name'],
                    advertiser['page_id'],
                    advertiser['view_all_page_id'],
                    advertiser['vertical'],
                    advertiser['country'],
                    advertiser['discovered_at']
                ))
            except Exception as e:
                logger.error(f"Error saving advertiser {advertiser.get('company_name', 'Unknown')}: {e}")
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(advertisers)} advertisers to database")
    
    def _save_ads(self, ads, page_id):
        """Save ads to database"""
        if not ads:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get prospect_id for page_id
        cursor.execute("SELECT id FROM prospects WHERE page_id = ?", (page_id,))
        result = cursor.fetchone()
        if not result:
            logger.error(f"No prospect found for page_id: {page_id}")
            conn.close()
            return
        
        prospect_id = result[0]
        
        for ad in ads:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO ads 
                    (library_id, prospect_id, ad_text, landing_url, start_date, platforms, discovered_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    ad['library_id'],
                    prospect_id,
                    ad.get('ad_text', ''),
                    ad.get('landing_url', ''),
                    ad.get('start_date', ''),
                    ad.get('platforms', ''),
                    ad['discovered_at']
                ))
            except Exception as e:
                logger.error(f"Error saving ad {ad.get('library_id', 'Unknown')}: {e}")
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(ads)} ads for prospect {page_id}")
    
    def get_discovery_stats(self):
        """Get discovery session statistics"""
        duration = time.time() - self.session_stats['start_time']
        
        return {
            'advertisers_found': self.session_stats['advertisers_found'],
            'ads_scraped': self.session_stats['ads_scraped'],
            'errors': self.session_stats['errors'],
            'duration_minutes': round(duration / 60, 2),
            'advertisers_per_minute': round(self.session_stats['advertisers_found'] / (duration / 60), 2) if duration > 0 else 0
        }


# Vertical configurations
VERTICAL_CONFIGS = {
    'dental_br': {
        'name': 'dental',
        'search_terms': [
            'dentista',
            'consultório dental', 
            'odontologia',
            'implante dental',
            'ortodontia'
        ],
        'country': 'BR'
    },
    'real_estate_br': {
        'name': 'real_estate',
        'search_terms': [
            'imóveis',
            'corretor de imóveis',
            'imobiliária',
            'apartamento venda',
            'casa venda'
        ],
        'country': 'BR'
    },
    'fitness_br': {
        'name': 'fitness',
        'search_terms': [
            'academia',
            'personal trainer',
            'nutrição',
            'crossfit',
            'musculação'
        ],
        'country': 'BR'
    }
}


async def run_discovery_pipeline(vertical_name='dental_br', max_advertisers=50):
    """
    Run complete discovery pipeline for specified vertical
    """
    if vertical_name not in VERTICAL_CONFIGS:
        logger.error(f"Unknown vertical: {vertical_name}")
        return
    
    config = VERTICAL_CONFIGS[vertical_name]
    discovery = MetaAdsDiscovery()
    
    logger.info(f"Starting discovery pipeline for {vertical_name}")
    
    # Phase 1: Discover advertisers
    advertisers = await discovery.discover_advertisers_by_vertical(config, max_advertisers)
    
    # Phase 2: Scrape ads for top advertisers (limited to avoid rate limits)
    top_advertisers = advertisers[:10]  # Limit to top 10 for initial scraping
    
    for i, advertiser in enumerate(top_advertisers, 1):
        logger.info(f"Scraping ads {i}/{len(top_advertisers)}: {advertiser['company_name']}")
        
        await discovery.scrape_ads_for_advertiser(
            advertiser['view_all_page_id'], 
            max_ads=20  # Limit ads per advertiser
        )
        
        # Rate limiting between advertisers
        await asyncio.sleep(5)
    
    # Print statistics
    stats = discovery.get_discovery_stats()
    logger.info(f"Discovery completed: {stats}")
    
    return stats


if __name__ == "__main__":
    import sys
    
    # Default to dental if no vertical specified
    vertical = sys.argv[1] if len(sys.argv) > 1 else 'dental_br'
    max_advertisers = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    print(f"ARCO META ADS DISCOVERY")
    print(f"Vertical: {vertical}")
    print(f"Max advertisers: {max_advertisers}")
    print("-" * 50)
    
    stats = asyncio.run(run_discovery_pipeline(vertical, max_advertisers))
    
    print(f"\nDISCOVERY COMPLETED:")
    print(f"Advertisers found: {stats['advertisers_found']}")
    print(f"Ads scraped: {stats['ads_scraped']}")
    print(f"Duration: {stats['duration_minutes']} minutes")
    print(f"Rate: {stats['advertisers_per_minute']} advertisers/minute")