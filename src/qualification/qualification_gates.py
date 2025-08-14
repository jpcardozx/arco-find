#!/usr/bin/env python3
"""
Qualification Gates System
Sistema de gates rigorosos para qualificar prospects dos funis aprovados
"""

import sqlite3
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import logging
from urllib.parse import urlparse
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QualificationGates:
    def __init__(self, db_path="../../data/prospects.db"):
        self.db_path = db_path
        self.setup_qualification_tables()
    
    def setup_qualification_tables(self):
        """Setup tables for qualification tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Qualification results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS qualification_results (
                id INTEGER PRIMARY KEY,
                prospect_id INTEGER,
                gate_name TEXT,
                passed INTEGER,
                score INTEGER,
                details TEXT,
                analyzed_at TIMESTAMP,
                FOREIGN KEY (prospect_id) REFERENCES prospects (id)
            )
        """)
        
        # Enrichment data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enrichment_data (
                id INTEGER PRIMARY KEY,
                prospect_id INTEGER,
                pagespeed_mobile INTEGER,
                pagespeed_desktop INTEGER,
                has_whatsapp INTEGER,
                has_phone INTEGER,
                has_reviews INTEGER,
                has_utm_tracking INTEGER,
                domain_type TEXT,
                business_signals TEXT,
                analyzed_at TIMESTAMP,
                FOREIGN KEY (prospect_id) REFERENCES prospects (id)
            )
        """)
        
        # Prospect scoring
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prospect_scores (
                id INTEGER PRIMARY KEY,
                prospect_id INTEGER UNIQUE,
                activity_score INTEGER,
                technical_score INTEGER,
                business_score INTEGER,
                total_score INTEGER,
                qualification_tier TEXT,
                recommended_funnel TEXT,
                monthly_waste_estimate INTEGER,
                last_scored TIMESTAMP,
                FOREIGN KEY (prospect_id) REFERENCES prospects (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    async def run_qualification_pipeline(self, vertical='dental', batch_size=50):
        """
        Run complete qualification pipeline for prospects
        """
        logger.info(f"Starting qualification pipeline for {vertical} vertical")
        
        # Get unqualified prospects
        prospects = self._get_prospects_for_qualification(vertical, batch_size)
        logger.info(f"Found {len(prospects)} prospects to qualify")
        
        qualified_prospects = []
        
        for prospect in prospects:
            logger.info(f"Qualifying: {prospect['company_name']} ({prospect['domain']})")
            
            # Run all gates
            qualification_result = await self._run_all_gates(prospect)
            
            if qualification_result['passes_all_gates']:
                qualified_prospects.append({
                    **prospect,
                    **qualification_result
                })
                logger.info(f"✓ QUALIFIED: {prospect['company_name']} - Score: {qualification_result['total_score']}")
            else:
                logger.info(f"✗ REJECTED: {prospect['company_name']} - Failed: {qualification_result['failed_gates']}")
        
        logger.info(f"Qualification complete: {len(qualified_prospects)}/{len(prospects)} qualified")
        return qualified_prospects
    
    def _get_prospects_for_qualification(self, vertical, limit):
        """Get prospects that need qualification"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get prospects without recent qualification
        cursor.execute("""
            SELECT p.id, p.domain, p.company_name, p.page_id, p.vertical
            FROM prospects p
            LEFT JOIN prospect_scores ps ON p.id = ps.prospect_id
            WHERE p.vertical = ?
            AND (ps.last_scored IS NULL OR ps.last_scored < date('now', '-7 days'))
            AND p.domain IS NOT NULL
            ORDER BY p.discovered_at DESC
            LIMIT ?
        """, (vertical, limit))
        
        columns = [desc[0] for desc in cursor.description]
        prospects = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return prospects
    
    async def _run_all_gates(self, prospect):
        """Run all qualification gates for a prospect"""
        prospect_id = prospect['id']
        domain = prospect['domain']
        
        gate_results = {}
        
        # Gate 1: Ad Activity (check recent ads)
        gate_results['gate_1_activity'] = await self._gate_1_ad_activity(prospect_id)
        
        # Gate 2: Technical Issues (PageSpeed, mobile, etc)
        gate_results['gate_2_technical'] = await self._gate_2_technical_issues(domain)
        
        # Gate 3: Business Signals (budget indicators)
        gate_results['gate_3_business'] = await self._gate_3_business_signals(prospect_id, domain)
        
        # Gate 4: Contact Information (decision maker findable)
        gate_results['gate_4_contact'] = await self._gate_4_contact_info(prospect)
        
        # Calculate scores and determine qualification
        qualification_result = self._calculate_qualification_result(gate_results)
        
        # Save results to database
        self._save_qualification_results(prospect_id, gate_results, qualification_result)
        
        return qualification_result
    
    async def _gate_1_ad_activity(self, prospect_id):
        """Gate 1: Recent advertising activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count ads in last 30 days
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        
        cursor.execute("""
            SELECT COUNT(*), MIN(start_date), MAX(start_date)
            FROM ads 
            WHERE prospect_id = ? 
            AND discovered_at > ?
        """, (prospect_id, thirty_days_ago))
        
        result = cursor.fetchone()
        ad_count = result[0] if result else 0
        
        conn.close()
        
        # Scoring: Need at least 1 ad in last 30 days
        passed = ad_count > 0
        score = min(ad_count * 2, 10)  # Max score 10
        
        return {
            'passed': passed,
            'score': score,
            'details': f"{ad_count} ads in last 30 days",
            'ad_count': ad_count
        }
    
    async def _gate_2_technical_issues(self, domain):
        """Gate 2: Technical issues that create opportunity"""
        if not domain:
            return {'passed': False, 'score': 0, 'details': 'No domain available'}
        
        technical_analysis = await self._analyze_website_technical(domain)
        
        # Scoring based on technical problems (more problems = higher opportunity)
        issues_found = []
        score = 0
        
        if technical_analysis.get('pagespeed_mobile', 100) < 70:
            issues_found.append(f"Mobile speed: {technical_analysis['pagespeed_mobile']}")
            score += 3
        
        if technical_analysis.get('pagespeed_desktop', 100) < 80:
            issues_found.append(f"Desktop speed: {technical_analysis['pagespeed_desktop']}")
            score += 2
        
        if not technical_analysis.get('has_whatsapp', False):
            issues_found.append("No WhatsApp integration")
            score += 2
        
        if not technical_analysis.get('has_utm_tracking', False):
            issues_found.append("No UTM tracking detected")
            score += 2
        
        # Pass if we found significant issues (score >= 3)
        passed = score >= 3
        
        return {
            'passed': passed,
            'score': min(score, 10),
            'details': f"Issues: {', '.join(issues_found) if issues_found else 'None'}",
            'technical_data': technical_analysis
        }
    
    async def _analyze_website_technical(self, domain):
        """Analyze website for technical issues"""
        try:
            # Simple HTTP analysis (would integrate PageSpeed API here)
            url = f"https://{domain}" if not domain.startswith('http') else domain
            
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            html = await response.text()
                            return self._parse_technical_signals(html, url)
                        else:
                            return {'error': f"HTTP {response.status}"}
                except asyncio.TimeoutError:
                    return {'error': 'Timeout', 'pagespeed_mobile': 30}  # Assume slow if timeout
                except Exception as e:
                    return {'error': str(e), 'pagespeed_mobile': 35}
        
        except Exception as e:
            logger.error(f"Error analyzing {domain}: {e}")
            return {'error': str(e)}
    
    def _parse_technical_signals(self, html, url):
        """Parse HTML for technical and business signals"""
        html_lower = html.lower()
        
        signals = {
            'has_whatsapp': bool(re.search(r'whatsapp|wa\.me', html_lower)),
            'has_phone': bool(re.search(r'\(\d{2}\)\s*\d{4,5}-?\d{4}', html)),
            'has_reviews': bool(re.search(r'review|avaliação|estrela|rating', html_lower)),
            'has_utm_tracking': 'utm_' in url or 'utm_' in html_lower,
            'has_booking_system': bool(re.search(r'agendar|schedule|book|calendly', html_lower)),
            'has_contact_form': bool(re.search(r'<form|contact|contato', html_lower)),
            'domain_type': self._classify_domain(url)
        }
        
        # Estimate PageSpeed based on simple metrics (would use real API)
        page_size = len(html)
        if page_size > 500000:  # Large page
            signals['pagespeed_mobile'] = 45
            signals['pagespeed_desktop'] = 65
        elif page_size > 200000:  # Medium page
            signals['pagespeed_mobile'] = 60
            signals['pagespeed_desktop'] = 75
        else:  # Small page
            signals['pagespeed_mobile'] = 80
            signals['pagespeed_desktop'] = 90
        
        return signals
    
    def _classify_domain(self, url):
        """Classify domain type"""
        domain = urlparse(url).netloc.lower()
        
        if any(x in domain for x in ['linktree', 'linktr.ee', 'bit.ly']):
            return 'redirect_service'
        elif any(x in domain for x in ['wordpress', 'wix', 'squarespace']):
            return 'website_builder'
        else:
            return 'own_domain'
    
    async def _gate_3_business_signals(self, prospect_id, domain):
        """Gate 3: Business maturity and budget indicators"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Analyze ad sophistication
        cursor.execute("""
            SELECT COUNT(DISTINCT platforms), COUNT(*), 
                   GROUP_CONCAT(platforms) as all_platforms
            FROM ads 
            WHERE prospect_id = ?
        """, (prospect_id,))
        
        result = cursor.fetchone()
        platform_count = result[0] if result else 0
        total_ads = result[1] if result else 0
        platforms = result[2] if result else ""
        
        conn.close()
        
        score = 0
        indicators = []
        
        # Multi-platform advertising
        if platform_count >= 2:
            score += 3
            indicators.append(f"{platform_count} platforms")
        
        # Volume of ads
        if total_ads >= 5:
            score += 2
            indicators.append(f"{total_ads} total ads")
        
        # Platform sophistication
        if 'audience network' in platforms.lower():
            score += 2
            indicators.append("Audience Network")
        
        # Domain quality
        if domain and not any(x in domain for x in ['linktree', 'bit.ly']):
            score += 2
            indicators.append("Own domain")
        
        passed = score >= 4  # Need decent business maturity
        
        return {
            'passed': passed,
            'score': min(score, 10),
            'details': f"Indicators: {', '.join(indicators) if indicators else 'Basic setup'}",
            'platform_count': platform_count,
            'total_ads': total_ads
        }
    
    async def _gate_4_contact_info(self, prospect):
        """Gate 4: Decision maker identifiable"""
        company_name = prospect.get('company_name', '')
        domain = prospect.get('domain', '')
        
        score = 0
        contact_methods = []
        
        # Company name quality
        if company_name and len(company_name) > 5:
            score += 2
            contact_methods.append("Company name")
        
        # Domain available
        if domain and not any(x in domain for x in ['facebook.com', 'instagram.com']):
            score += 3
            contact_methods.append("Own domain")
        
        # TODO: LinkedIn search for decision maker
        # For now, assume findable if company has domain
        if domain:
            score += 3
            contact_methods.append("Searchable online")
        
        passed = score >= 5  # Need basic contact info
        
        return {
            'passed': passed,
            'score': min(score, 10),
            'details': f"Contact methods: {', '.join(contact_methods)}",
            'company_name': company_name,
            'domain': domain
        }
    
    def _calculate_qualification_result(self, gate_results):
        """Calculate overall qualification result"""
        gates_passed = sum(1 for result in gate_results.values() if result['passed'])
        total_gates = len(gate_results)
        
        # Calculate weighted score
        activity_score = gate_results['gate_1_activity']['score']
        technical_score = gate_results['gate_2_technical']['score'] 
        business_score = gate_results['gate_3_business']['score']
        contact_score = gate_results['gate_4_contact']['score']
        
        # Weighted total (technical issues are most important for our offering)
        total_score = (
            activity_score * 0.2 +
            technical_score * 0.4 +  # High weight - our main value prop
            business_score * 0.3 +
            contact_score * 0.1
        )
        
        # Determine qualification tier
        if total_score >= 7 and gates_passed >= 3:
            tier = 'S_TIER'
            recommended_funnel = 'auditoria_express'
        elif total_score >= 5 and gates_passed >= 2:
            tier = 'A_TIER' 
            recommended_funnel = 'teardown_60s'
        elif total_score >= 3:
            tier = 'B_TIER'
            recommended_funnel = 'teardown_60s'
        else:
            tier = 'REJECTED'
            recommended_funnel = None
        
        # Estimate monthly waste based on technical issues
        monthly_waste = self._estimate_monthly_waste(gate_results)
        
        passes_all_gates = gates_passed >= 3  # Need at least 3/4 gates
        failed_gates = [name for name, result in gate_results.items() if not result['passed']]
        
        return {
            'passes_all_gates': passes_all_gates,
            'gates_passed': gates_passed,
            'total_gates': total_gates,
            'failed_gates': failed_gates,
            'activity_score': activity_score,
            'technical_score': technical_score,
            'business_score': business_score,
            'contact_score': contact_score,
            'total_score': round(total_score, 1),
            'qualification_tier': tier,
            'recommended_funnel': recommended_funnel,
            'monthly_waste_estimate': monthly_waste
        }
    
    def _estimate_monthly_waste(self, gate_results):
        """Estimate monthly waste based on technical issues"""
        base_waste = 0
        
        technical_data = gate_results.get('gate_2_technical', {}).get('technical_data', {})
        business_data = gate_results.get('gate_3_business', {})
        
        # PageSpeed impact
        mobile_speed = technical_data.get('pagespeed_mobile', 100)
        if mobile_speed < 50:
            base_waste += 2500  # Critical mobile issues
        elif mobile_speed < 70:
            base_waste += 1200  # Poor mobile performance
        
        # Missing business features
        if not technical_data.get('has_whatsapp'):
            base_waste += 800  # Missing WhatsApp
        
        if not technical_data.get('has_utm_tracking'):
            base_waste += 600  # No tracking
        
        # Scale by ad volume (more ads = more waste)
        ad_count = gate_results.get('gate_1_activity', {}).get('ad_count', 1)
        scale_factor = min(ad_count / 5, 2.0)  # Max 2x multiplier
        
        return int(base_waste * scale_factor)
    
    def _save_qualification_results(self, prospect_id, gate_results, qualification_result):
        """Save qualification results to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        # Save individual gate results
        for gate_name, result in gate_results.items():
            cursor.execute("""
                INSERT OR REPLACE INTO qualification_results
                (prospect_id, gate_name, passed, score, details, analyzed_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (prospect_id, gate_name, result['passed'], result['score'], 
                  result['details'], timestamp))
        
        # Save enrichment data
        technical_data = gate_results.get('gate_2_technical', {}).get('technical_data', {})
        cursor.execute("""
            INSERT OR REPLACE INTO enrichment_data
            (prospect_id, pagespeed_mobile, pagespeed_desktop, has_whatsapp, 
             has_phone, has_reviews, has_utm_tracking, domain_type, analyzed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (prospect_id, 
              technical_data.get('pagespeed_mobile'),
              technical_data.get('pagespeed_desktop'),
              technical_data.get('has_whatsapp', 0),
              technical_data.get('has_phone', 0),
              technical_data.get('has_reviews', 0),
              technical_data.get('has_utm_tracking', 0),
              technical_data.get('domain_type'),
              timestamp))
        
        # Save overall score
        cursor.execute("""
            INSERT OR REPLACE INTO prospect_scores
            (prospect_id, activity_score, technical_score, business_score, 
             total_score, qualification_tier, recommended_funnel, 
             monthly_waste_estimate, last_scored)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (prospect_id,
              qualification_result['activity_score'],
              qualification_result['technical_score'], 
              qualification_result['business_score'],
              qualification_result['total_score'],
              qualification_result['qualification_tier'],
              qualification_result['recommended_funnel'],
              qualification_result['monthly_waste_estimate'],
              timestamp))
        
        conn.commit()
        conn.close()
    
    def get_qualified_prospects(self, tier='S_TIER', limit=50):
        """Get qualified prospects by tier"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.*, ps.total_score, ps.qualification_tier, 
                   ps.recommended_funnel, ps.monthly_waste_estimate
            FROM prospects p
            JOIN prospect_scores ps ON p.id = ps.prospect_id
            WHERE ps.qualification_tier = ?
            ORDER BY ps.total_score DESC, ps.monthly_waste_estimate DESC
            LIMIT ?
        """, (tier, limit))
        
        columns = [desc[0] for desc in cursor.description]
        prospects = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return prospects


async def run_qualification_demo():
    """Demo qualification system"""
    gates = QualificationGates()
    
    print("ARCO QUALIFICATION GATES DEMO")
    print("=" * 50)
    
    # Run qualification for dental vertical
    qualified = await gates.run_qualification_pipeline('dental', batch_size=20)
    
    print(f"\nQUALIFICATION RESULTS:")
    print(f"Qualified prospects: {len(qualified)}")
    
    for prospect in qualified[:5]:  # Show top 5
        print(f"\n{prospect['company_name']} ({prospect['domain']})")
        print(f"  Score: {prospect['total_score']}/10")
        print(f"  Tier: {prospect['qualification_tier']}")
        print(f"  Funnel: {prospect['recommended_funnel']}")
        print(f"  Waste: ${prospect['monthly_waste_estimate']}/month")


if __name__ == "__main__":
    asyncio.run(run_qualification_demo())