#!/usr/bin/env python3
"""
Meta Ad Library Scraper - Alternativa FREE ao SearchAPI
Pipeline completo: descoberta → enriquecimento → qualificação
"""

import asyncio
import aiohttp
from playwright.async_api import async_playwright
import json
from datetime import datetime
import sqlite3
from urllib.parse import urlparse, parse_qs
import re
import time

class MetaAdLibraryScraper:
    def __init__(self, db_path="meta_ads_intelligence.db"):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """Setup SQLite database for storing intelligence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Advertisers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS advertisers (
                id INTEGER PRIMARY KEY,
                page_name TEXT,
                page_id TEXT UNIQUE,
                view_all_page_id TEXT,
                category TEXT,
                country TEXT,
                discovered_at TEXT,
                last_scraped TEXT
            )
        """)
        
        # Ads table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ads (
                id INTEGER PRIMARY KEY,
                library_id TEXT UNIQUE,
                page_id TEXT,
                ad_text TEXT,
                media_urls TEXT,
                landing_url TEXT,
                start_date TEXT,
                platforms TEXT,
                countries TEXT,
                status TEXT,
                discovered_at TEXT,
                FOREIGN KEY (page_id) REFERENCES advertisers (page_id)
            )
        """)
        
        # Landing page enrichment
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS landing_pages (
                id INTEGER PRIMARY KEY,
                url TEXT UNIQUE,
                domain TEXT,
                title TEXT,
                description TEXT,
                has_whatsapp INTEGER,
                has_utm_tracking INTEGER,
                is_own_domain INTEGER,
                page_speed_score INTEGER,
                analyzed_at TEXT
            )
        """)
        
        # Prospect scoring
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prospect_scores (
                id INTEGER PRIMARY KEY,
                page_id TEXT UNIQUE,
                activity_score INTEGER,
                creative_intensity INTEGER,
                platform_maturity INTEGER,
                landing_quality INTEGER,
                total_score INTEGER,
                qualification_tier TEXT,
                last_scored TEXT,
                FOREIGN KEY (page_id) REFERENCES advertisers (page_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    async def discover_advertisers_by_vertical(self, vertical_terms, country="BR", max_pages=5):
        """
        Descobrir anunciantes ativos por vertical usando Meta Ad Library
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            advertisers = []
            
            for term in vertical_terms:
                print(f"Searching for advertisers: {term} in {country}")
                
                # Build Ad Library search URL
                search_url = f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country={country}&search_type=keyword_unordered&q={term}"
                
                await page.goto(search_url)
                await page.wait_for_timeout(3000)  # Wait for load
                
                # Extract advertiser pages
                for page_num in range(max_pages):
                    try:
                        # Look for advertiser page links
                        page_links = await page.query_selector_all('[data-testid="pages_tab_ads_by_page_card"]')
                        
                        for link_elem in page_links:
                            try:
                                # Extract page info
                                page_name = await link_elem.query_selector('[data-testid="page_name"]')
                                page_name_text = await page_name.inner_text() if page_name else "Unknown"
                                
                                # Extract view_all_page_id from href
                                href_elem = await link_elem.query_selector('a[href*="view_all_page_id"]')
                                if href_elem:
                                    href = await href_elem.get_attribute('href')
                                    view_all_page_id = self.extract_page_id_from_url(href)
                                    
                                    if view_all_page_id:
                                        advertiser = {
                                            "page_name": page_name_text,
                                            "view_all_page_id": view_all_page_id,
                                            "category": vertical_terms[0],  # Primary vertical
                                            "country": country,
                                            "discovered_at": datetime.now().isoformat(),
                                            "search_term": term
                                        }
                                        advertisers.append(advertiser)
                                        print(f"  Found: {page_name_text} (ID: {view_all_page_id})")
                            
                            except Exception as e:
                                print(f"Error extracting advertiser: {e}")
                                continue
                        
                        # Try to go to next page
                        next_button = await page.query_selector('[aria-label="Next"]')
                        if next_button:
                            await next_button.click()
                            await page.wait_for_timeout(2000)
                        else:
                            break
                    
                    except Exception as e:
                        print(f"Error on page {page_num}: {e}")
                        break
                
                await page.wait_for_timeout(2000)  # Rate limiting
            
            await browser.close()
            
            # Save to database
            self.save_advertisers(advertisers)
            return advertisers
    
    def extract_page_id_from_url(self, url):
        """Extract view_all_page_id from Meta Ad Library URL"""
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            return params.get('view_all_page_id', [None])[0]
        except:
            return None
    
    async def scrape_ads_for_advertiser(self, view_all_page_id, max_ads=50):
        """
        Scrape ads for specific advertiser using view_all_page_id
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            ads = []
            
            # Build URL for advertiser's ads
            ads_url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&view_all_page_id={view_all_page_id}"
            
            print(f"Scraping ads for advertiser: {view_all_page_id}")
            await page.goto(ads_url)
            await page.wait_for_timeout(3000)
            
            ads_scraped = 0
            scroll_attempts = 0
            max_scrolls = 10
            
            while ads_scraped < max_ads and scroll_attempts < max_scrolls:
                try:
                    # Find ad cards
                    ad_cards = await page.query_selector_all('[data-testid="political_ad_library_ad_card"]')
                    
                    for card in ad_cards[ads_scraped:]:
                        try:
                            ad_data = await self.extract_ad_data(card)
                            if ad_data:
                                ad_data['page_id'] = view_all_page_id
                                ad_data['discovered_at'] = datetime.now().isoformat()
                                ads.append(ad_data)
                                ads_scraped += 1
                                
                                print(f"  Scraped ad {ads_scraped}: {ad_data.get('ad_text', '')[:50]}...")
                        
                        except Exception as e:
                            print(f"Error extracting ad data: {e}")
                            continue
                    
                    # Scroll to load more ads
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(2000)
                    scroll_attempts += 1
                
                except Exception as e:
                    print(f"Error scraping ads: {e}")
                    break
            
            await browser.close()
            
            # Save to database
            self.save_ads(ads)
            return ads
    
    async def extract_ad_data(self, card_element):
        """Extract ad data from Meta Ad Library card"""
        try:
            ad_data = {}
            
            # Ad text
            text_elem = await card_element.query_selector('[data-testid="ad_snapshot_body_text"]')
            ad_data['ad_text'] = await text_elem.inner_text() if text_elem else ""
            
            # Landing URL
            link_elem = await card_element.query_selector('a[href*="l.facebook.com"]')
            if link_elem:
                href = await link_elem.get_attribute('href')
                ad_data['landing_url'] = self.extract_landing_url(href)
            
            # Start date
            date_elem = await card_element.query_selector('[data-testid="ad_snapshot_metadata"] span')
            ad_data['start_date'] = await date_elem.inner_text() if date_elem else ""
            
            # Platforms (Facebook, Instagram, etc.)
            platform_elems = await card_element.query_selector_all('[data-testid="platforms"] img')
            platforms = []
            for platform_elem in platform_elems:
                alt = await platform_elem.get_attribute('alt')
                if alt:
                    platforms.append(alt)
            ad_data['platforms'] = ','.join(platforms)
            
            # Media URLs
            media_elems = await card_element.query_selector_all('img, video')
            media_urls = []
            for media_elem in media_elems:
                src = await media_elem.get_attribute('src')
                if src and 'scontent' in src:  # Facebook CDN
                    media_urls.append(src)
            ad_data['media_urls'] = ','.join(media_urls[:3])  # Limit to 3
            
            # Generate library_id (unique identifier)
            ad_data['library_id'] = self.generate_library_id(ad_data)
            
            return ad_data
            
        except Exception as e:
            print(f"Error extracting ad data: {e}")
            return None
    
    def extract_landing_url(self, facebook_redirect_url):
        """Extract actual landing URL from Facebook redirect"""
        try:
            # Parse l.facebook.com redirect
            parsed = urlparse(facebook_redirect_url)
            params = parse_qs(parsed.query)
            actual_url = params.get('u', [None])[0]
            return actual_url
        except:
            return facebook_redirect_url
    
    def generate_library_id(self, ad_data):
        """Generate unique library ID for ad"""
        import hashlib
        content = f"{ad_data.get('ad_text', '')}{ad_data.get('landing_url', '')}{ad_data.get('start_date', '')}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    async def enrich_landing_pages(self, urls):
        """
        Enrich landing page data using open graph scraping
        """
        enriched = []
        
        async with aiohttp.ClientSession() as session:
            for url in urls:
                try:
                    print(f"Enriching: {url}")
                    
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            html = await response.text()
                            enrichment = self.parse_landing_page(url, html)
                            enriched.append(enrichment)
                            
                            # Save to database
                            self.save_landing_page(enrichment)
                
                except Exception as e:
                    print(f"Error enriching {url}: {e}")
                    continue
                
                await asyncio.sleep(1)  # Rate limiting
        
        return enriched
    
    def parse_landing_page(self, url, html):
        """Parse landing page for strategic signals"""
        domain = urlparse(url).netloc
        
        enrichment = {
            "url": url,
            "domain": domain,
            "title": self.extract_og_tag(html, "og:title") or self.extract_title_tag(html),
            "description": self.extract_og_tag(html, "og:description"),
            "has_whatsapp": 1 if "whatsapp" in html.lower() else 0,
            "has_utm_tracking": 1 if ("utm_" in url or "utm_" in html) else 0,
            "is_own_domain": 1 if not any(x in domain for x in ["linktree", "linktr.ee", "bit.ly"]) else 0,
            "analyzed_at": datetime.now().isoformat()
        }
        
        return enrichment
    
    def extract_og_tag(self, html, property_name):
        """Extract Open Graph meta tag"""
        pattern = f'<meta[^>]*property=["\']?{property_name}["\']?[^>]*content=["\']?([^"\']*)["\']?'
        match = re.search(pattern, html, re.IGNORECASE)
        return match.group(1) if match else None
    
    def extract_title_tag(self, html):
        """Extract HTML title tag"""
        match = re.search(r'<title[^>]*>([^<]*)</title>', html, re.IGNORECASE)
        return match.group(1) if match else None
    
    def save_advertisers(self, advertisers):
        """Save advertisers to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for advertiser in advertisers:
            cursor.execute("""
                INSERT OR REPLACE INTO advertisers 
                (page_name, view_all_page_id, category, country, discovered_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                advertiser['page_name'],
                advertiser['view_all_page_id'], 
                advertiser['category'],
                advertiser['country'],
                advertiser['discovered_at']
            ))
        
        conn.commit()
        conn.close()
    
    def save_ads(self, ads):
        """Save ads to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for ad in ads:
            cursor.execute("""
                INSERT OR REPLACE INTO ads 
                (library_id, page_id, ad_text, media_urls, landing_url, start_date, platforms, discovered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ad['library_id'],
                ad['page_id'],
                ad['ad_text'],
                ad['media_urls'],
                ad.get('landing_url', ''),
                ad['start_date'],
                ad['platforms'],
                ad['discovered_at']
            ))
        
        conn.commit()
        conn.close()
    
    def save_landing_page(self, enrichment):
        """Save landing page enrichment to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO landing_pages 
            (url, domain, title, description, has_whatsapp, has_utm_tracking, is_own_domain, analyzed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            enrichment['url'],
            enrichment['domain'],
            enrichment['title'],
            enrichment['description'],
            enrichment['has_whatsapp'],
            enrichment['has_utm_tracking'],
            enrichment['is_own_domain'],
            enrichment['analyzed_at']
        ))
        
        conn.commit()
        conn.close()


async def run_intelligence_pipeline():
    """
    Pipeline completo de intelligence gathering
    """
    scraper = MetaAdLibraryScraper()
    
    # Define verticals to target
    verticals = {
        "dental": ["dentista", "consultorio dental", "odontologia"],
        "real_estate": ["imoveis", "corretor", "imobiliaria"],
        "fitness": ["academia", "personal trainer", "nutricao"]
    }
    
    print("META AD LIBRARY INTELLIGENCE PIPELINE")
    print("=" * 50)
    
    for vertical, terms in verticals.items():
        print(f"\n🎯 DISCOVERING {vertical.upper()} ADVERTISERS")
        
        # Step 1: Discover advertisers
        advertisers = await scraper.discover_advertisers_by_vertical(terms, country="BR", max_pages=3)
        print(f"Found {len(advertisers)} advertisers")
        
        # Step 2: Scrape ads for top advertisers
        for i, advertiser in enumerate(advertisers[:5], 1):  # Limit to top 5
            print(f"\n📱 SCRAPING ADS {i}/5: {advertiser['page_name']}")
            
            ads = await scraper.scrape_ads_for_advertiser(
                advertiser['view_all_page_id'], 
                max_ads=20
            )
            print(f"Scraped {len(ads)} ads")
            
            # Step 3: Enrich landing pages
            landing_urls = [ad['landing_url'] for ad in ads if ad.get('landing_url')]
            if landing_urls:
                print(f"🔍 ENRICHING {len(landing_urls)} LANDING PAGES")
                await scraper.enrich_landing_pages(landing_urls[:5])  # Limit enrichment
            
            await asyncio.sleep(5)  # Rate limiting between advertisers
    
    print(f"\n✅ INTELLIGENCE PIPELINE COMPLETE")
    print(f"Database saved: {scraper.db_path}")


if __name__ == "__main__":
    asyncio.run(run_intelligence_pipeline())