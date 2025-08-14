# API Handling & Documentation

Documentação crítica para handling de APIs no pipeline ARCO, incluindo rate limits, error handling e otimizações.

## 🔗 Meta Ad Library API

### Endpoints Utilizados
```
Official API: https://graph.facebook.com/v18.0/ads_archive
Web Interface: https://www.facebook.com/ads/library/
```

### Rate Limits & Constraints
- **Official API**: Limitado a anúncios políticos + UE/UK comerciais
- **Web Scraping**: Rate limit ~2 req/s, IP blocking após 100+ requests
- **Recommended**: 1 req/s com backoff exponencial

### Error Handling Strategy
```python
async def robust_request(url, session, max_retries=3):
    for attempt in range(max_retries):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:  # Rate limited
                    await asyncio.sleep(2 ** attempt)
                    continue
                elif response.status == 403:  # Blocked
                    # Switch user agent / proxy
                    pass
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(1)
```

### Data Extraction Points
- **Advertiser Discovery**: `view_all_page_id` from search results
- **Ad Details**: library_id, ad_text, landing_url, start_date, platforms
- **Media Assets**: Creative URLs from Facebook CDN

### Implementation Notes
- Use rotating user agents
- Maintain session cookies
- Parse DOM carefully (structure changes frequently)
- Cache results to avoid re-scraping

## 🚀 PageSpeed Insights API

### Endpoint & Auth
```
URL: https://www.googleapis.com/pagespeed/insights/v5/runPagespeed
Auth: API Key (FREE tier: 25k requests/day)
```

### Rate Limits
- **Free Tier**: 25,000 requests/day
- **Recommended**: 1 req/s to avoid throttling
- **Quota Monitoring**: Track daily usage

### Request Parameters
```python
params = {
    "url": domain,
    "key": API_KEY,
    "strategy": "mobile",  # or "desktop"
    "category": ["PERFORMANCE", "ACCESSIBILITY", "SEO"],
    "locale": "pt_BR"
}
```

### Response Parsing
```python
def extract_pagespeed_data(response):
    lighthouse = response.get('lighthouseResult', {})
    categories = lighthouse.get('categories', {})
    
    performance = categories.get('performance', {})
    score = int(performance.get('score', 0) * 100)
    
    # Core Web Vitals
    audits = lighthouse.get('audits', {})
    lcp = audits.get('largest-contentful-paint', {}).get('displayValue')
    cls = audits.get('cumulative-layout-shift', {}).get('displayValue')
    
    return {
        'performance_score': score,
        'lcp': lcp,
        'cls': cls,
        'opportunities': extract_opportunities(audits)
    }
```

### Error Scenarios
- **Invalid URL**: Return default low score
- **Timeout**: Retry once, then skip
- **Quota Exceeded**: Switch to manual analysis

## 🌐 OpenGraph Scraping

### Implementation
```python
async def enrich_landing_page(url, session):
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; ARCO-Bot/1.0)',
        'Accept': 'text/html,application/xhtml+xml'
    }
    
    try:
        async with session.get(url, headers=headers, timeout=10) as response:
            if response.status == 200:
                html = await response.text()
                return parse_metadata(html)
    except asyncio.TimeoutError:
        return None
    except Exception as e:
        logger.error(f"Error enriching {url}: {e}")
        return None
```

### Metadata Extraction
- **og:title** - Page title
- **og:description** - Meta description  
- **og:image** - Social image
- **canonical** - Canonical URL
- **viewport** - Mobile optimization
- **utm_source** - Tracking parameters

### Business Intelligence Signals
```python
def extract_business_signals(html, url):
    signals = {
        'has_whatsapp': bool(re.search(r'whatsapp|wa\.me', html, re.I)),
        'has_phone': bool(re.search(r'\(\d{2}\)\s*\d{4,5}-?\d{4}', html)),
        'has_address': bool(re.search(r'rua|avenida|street|avenue', html, re.I)),
        'has_reviews': bool(re.search(r'review|avaliação|estrela', html, re.I)),
        'has_booking': bool(re.search(r'agendar|schedule|book', html, re.I)),
        'has_utm_tracking': 'utm_' in url or 'utm_' in html,
        'domain_type': classify_domain(url)
    }
    return signals
```

## 💾 Database Schema & Optimization

### SQLite Schema
```sql
-- Prospects table with indexes
CREATE TABLE prospects (
    id INTEGER PRIMARY KEY,
    domain TEXT UNIQUE,
    company_name TEXT,
    vertical TEXT,
    page_id TEXT,
    discovered_at TIMESTAMP,
    last_updated TIMESTAMP
);

CREATE INDEX idx_prospects_vertical ON prospects(vertical);
CREATE INDEX idx_prospects_discovered ON prospects(discovered_at);

-- Ads table for tracking activity
CREATE TABLE ads (
    id INTEGER PRIMARY KEY,
    library_id TEXT UNIQUE,
    prospect_id INTEGER,
    ad_text TEXT,
    landing_url TEXT,
    start_date TEXT,
    platforms TEXT,
    FOREIGN KEY (prospect_id) REFERENCES prospects (id)
);

-- Enrichment data
CREATE TABLE enrichment (
    id INTEGER PRIMARY KEY,
    prospect_id INTEGER,
    pagespeed_mobile INTEGER,
    pagespeed_desktop INTEGER,
    business_signals JSON,
    analyzed_at TIMESTAMP,
    FOREIGN KEY (prospect_id) REFERENCES prospects (id)
);

-- Outreach tracking
CREATE TABLE outreach (
    id INTEGER PRIMARY KEY,
    prospect_id INTEGER,
    funnel_type TEXT,
    sequence_step INTEGER,
    sent_at TIMESTAMP,
    response_type TEXT,
    FOREIGN KEY (prospect_id) REFERENCES prospects (id)
);
```

### Query Optimization
```python
# Efficient prospect qualification query
query = """
SELECT p.*, e.pagespeed_mobile, e.business_signals
FROM prospects p
JOIN enrichment e ON p.id = e.prospect_id
WHERE p.vertical = ?
AND e.pagespeed_mobile < 70
AND json_extract(e.business_signals, '$.has_whatsapp') = 1
AND p.discovered_at > date('now', '-30 days')
ORDER BY e.pagespeed_mobile ASC
LIMIT 50
"""
```

## 🔍 Monitoring & Alerting

### Key Metrics to Track
- **API quotas**: PageSpeed API usage
- **Scraping success rate**: Meta Ad Library
- **Database growth**: Prospects/day
- **Qualification rates**: Gate passage %
- **Response rates**: Outreach performance

### Error Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('arco_pipeline.log'),
        logging.StreamHandler()
    ]
)

# Usage
logger = logging.getLogger(__name__)
logger.info(f"Scraped {len(ads)} ads for {advertiser}")
logger.error(f"Failed to analyze {url}: {error}")
```

### Performance Monitoring
```python
import time

class APIMonitor:
    def __init__(self):
        self.request_times = []
        self.error_count = 0
        
    def log_request(self, duration, success=True):
        self.request_times.append(duration)
        if not success:
            self.error_count += 1
            
    def get_stats(self):
        if not self.request_times:
            return None
            
        return {
            'avg_response_time': sum(self.request_times) / len(self.request_times),
            'total_requests': len(self.request_times),
            'error_rate': self.error_count / len(self.request_times),
            'requests_per_minute': len(self.request_times) / (max(self.request_times) / 60)
        }
```

## ⚡ Performance Optimizations

### Async/Concurrent Processing
```python
# Batch processing for efficiency
async def process_prospects_batch(prospects, batch_size=10):
    semaphore = asyncio.Semaphore(batch_size)
    
    async def process_single(prospect):
        async with semaphore:
            return await enrich_prospect(prospect)
    
    tasks = [process_single(p) for p in prospects]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return [r for r in results if not isinstance(r, Exception)]
```

### Caching Strategy
```python
import pickle
from datetime import datetime, timedelta

class ResultCache:
    def __init__(self, ttl_hours=24):
        self.cache = {}
        self.ttl = timedelta(hours=ttl_hours)
    
    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return data
            else:
                del self.cache[key]
        return None
    
    def set(self, key, value):
        self.cache[key] = (value, datetime.now())
```

## 🚨 Kill Rules Implementation

### Automated Monitoring
```python
def check_kill_rules():
    """Check if any funnel should be killed based on performance"""
    
    # Auditoria Express kill rule
    upgrade_rate = calculate_upgrade_rate(days=21)  # 3 weeks
    if upgrade_rate < 0.20:
        alert("KILL RULE TRIGGERED: Auditoria Express upgrade rate < 20%")
    
    # Teardown 60s kill rule  
    response_rate = calculate_response_rate(days=14)  # 2 weeks
    if response_rate < 0.06:
        alert("KILL RULE TRIGGERED: Teardown response rate < 6%")

def alert(message):
    """Send alert via email/Slack/etc"""
    logger.critical(message)
    # TODO: Implement actual alerting
```

---

## 📝 Next Steps

1. **Validate API Access**: Test Meta Ad Library scraping
2. **Setup Monitoring**: Implement logging and error tracking
3. **Performance Testing**: Benchmark scraping speed and accuracy
4. **Error Recovery**: Build robust retry mechanisms

*This document will be updated as APIs are implemented and tested.*