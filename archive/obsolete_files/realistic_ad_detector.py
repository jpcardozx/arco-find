#!/usr/bin/env python3
"""
ARCO ADVERTISING INTELLIGENCE - DETECÇÃO GRATUITA 100%
=====================================================
Análise HTTP, pixels, tracking e elementos básicos - SEM CUSTOS
Métodos: HTTP headers, HTML parsing, pixel detection, UTM analysis
"""
import asyncio
import aiohttp
import re
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import sqlite3
import os

# Configuração
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TechnicalAdSignal:
    """Sinal técnico de publicidade detectado gratuitamente"""
    platform: str          # google_ads, meta, tiktok, linkedin
    signal_type: str        # pixel, gtag, utm, script, header
    confidence: float       # 0.0-1.0 baseado na qualidade do sinal
    evidence: str          # Evidência técnica encontrada
    technical_details: str # Detalhes da implementação

@dataclass 
class FreeAdAnalysis:
    """Análise completa usando apenas métodos gratuitos"""
    website: str
    has_advertising: bool
    platforms_detected: List[str]
    technical_signals: List[TechnicalAdSignal]
    utm_campaigns: int
    pixel_sophistication: float  # 0-100
    investment_level: str        # none, basic, intermediate, advanced
    analysis_timestamp: str

class FreeAdvertisingDetector:
    """Detector 100% gratuito de atividade publicitária"""
    
    def __init__(self):
        self.session = None
        
        # PADRÕES GRATUITOS - Regex para análise HTML/HTTP
        self.free_detection_patterns = {
            
            # GOOGLE ADS - Padrões específicos sem API
            'google_ads': {
                'gtag_ads': r'gtag\([\'"]config[\'"],\s*[\'"]AW-(\d+)[\'"]',
                'conversion_tracking': r'google_trackConversion|googleadservices\.com/pagead/conversion',
                'gtm_ads': r'GTM-[A-Z0-9]{7}.*?(ads|adwords|conversion)',
                'remarketing_tag': r'googlesyndication\.com/pagead/conversion_async\.js',
                'enhanced_conversions': r'gtag.*?enhanced_conversions[\'"]:\s*true',
                'ads_script': r'googleadservices\.com/pagead/js/adsbygoogle\.js'
            },
            
            # META/FACEBOOK - Padrões de pixel
            'meta': {
                'pixel_base': r'fbq\([\'"]init[\'"],\s*[\'"](\d{15,16})[\'"]',
                'pixel_events': r'fbq\([\'"]track[\'"],\s*[\'"]([^\'\"]+)[\'"]',
                'conversions_api': r'facebook\.com/tr\?id=(\d+)',
                'pixel_script': r'connect\.facebook\.net/[^/]+/fbevents\.js',
                'custom_audiences': r'fbq\([\'"]trackCustom[\'"]',
                'dynamic_ads': r'fbq.*?content_type|fbq.*?content_ids'
            },
            
            # TIKTOK ADS - Padrões de pixel
            'tiktok': {
                'pixel_init': r'ttq\.load\([\'"]([A-Z0-9]{20})[\'"]',
                'event_tracking': r'ttq\.track\([\'"](\w+)[\'"]',
                'analytics_script': r'analytics\.tiktok\.com/i18n/pixel',
                'conversion_tracking': r'ttq\.page\(\)|ttq\.identify\('
            },
            
            # LINKEDIN ADS
            'linkedin': {
                'insight_tag': r'_linkedin_partner_id\s*=\s*[\'"](\d+)[\'"]',
                'conversion_tag': r'snap\.licdn\.com/li\.lms-analytics',
                'retargeting': r'linkedin\.com/.*?insight'
            },
            
            # OUTRAS PLATAFORMAS
            'twitter': {
                'universal_tag': r'twq\([\'"]init[\'"],\s*[\'"]([^\'\"]+)[\'"]',
                'conversion': r'static\.ads-twitter\.com/uwt\.js'
            },
            
            'bing': {
                'uet_tag': r'window\.uetq.*?UET-(\d+)',
                'conversion': r'bat\.bing\.com/bat\.js'
            }
        }
        
        # UTM Sources que indicam tráfego pago
        self.paid_traffic_sources = {
            'google_ads': ['google', 'adwords', 'googleads', 'cpc', 'sem'],
            'meta': ['facebook', 'instagram', 'fb', 'ig', 'meta'],
            'tiktok': ['tiktok', 'tt', 'bytedance'],
            'linkedin': ['linkedin', 'li'],
            'twitter': ['twitter', 'tw', 'x'],
            'bing': ['bing', 'bingads', 'msn'],
            'generic_paid': ['ads', 'paid', 'ppc', 'cpc', 'display', 'retargeting']
        }
        
        # Mediums que sempre indicam tráfego pago
        self.paid_mediums = [
            'cpc', 'ppc', 'paid', 'ads', 'adwords', 'cost-per-click',
            'facebook-ads', 'instagram-ads', 'tiktok-ads', 'linkedin-ads',
            'display', 'banner', 'retargeting', 'remarketing', 'social-paid'
        ]

@dataclass
class RealAdActivity:
    """Atividade publicitária real detectada"""
    platform: str
    is_likely_active: bool
    confidence_score: float
    signals: List[AdSignal]
    estimated_investment_level: str  # 'low', 'medium', 'high', 'unknown'
    detection_date: str

class RealisticAdDetector:
    """Detector realista de atividade publicitária"""
    
    def __init__(self):
        self.session = None
        
        # Padrões de detecção para diferentes plataformas
        self.detection_patterns = {
            'google_ads': {
                'pixels': [
                    r'googleadservices\.com/pagead/conversion',
                    r'google-analytics\.com/collect',
                    r'googletagmanager\.com/gtag',
                    r'gtag\([\'"]config[\'"],\s*[\'"]AW-\d+[\'"]',
                    r'gtag\([\'"]event[\'"],\s*[\'"]conversion[\'"]'
                ],
                'scripts': [
                    r'adsbygoogle',
                    r'googlesyndication',
                    r'goog_snippet_vars'
                ],
                'utm_sources': ['google', 'adwords', 'cpc']
            },
            'meta': {
                'pixels': [
                    r'facebook\.com/tr\?',
                    r'fbq\([\'"]track[\'"]',
                    r'fbq\([\'"]init[\'"]',
                    r'connect\.facebook\.net/.*?/fbevents\.js'
                ],
                'scripts': [
                    r'fbq\(',
                    r'facebook\.com/tr'
                ],
                'utm_sources': ['facebook', 'instagram', 'fb', 'ig']
            },
            'tiktok': {
                'pixels': [
                    r'analytics\.tiktok\.com',
                    r'ttq\.track\(',
                    r'ttq\.page\('
                ],
                'scripts': [
                    r'analytics\.tiktok\.com/i18n/pixel'
                ],
                'utm_sources': ['tiktok', 'tt']
            },
            'linkedin': {
                'pixels': [
                    r'snap\.licdn\.com/li\.lms-analytics',
                    r'linkedin\.com/collect'
                ],
                'scripts': [
                    r'linkedin\.com/collect'
                ],
                'utm_sources': ['linkedin', 'li']
            }
        }
    
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=10)
        timeout = aiohttp.ClientTimeout(total=20)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def analyze_website_for_ads(self, website: str) -> List[RealAdActivity]:
        """Análise realista de atividade publicitária"""
        try:
            # Buscar página principal
            page_content, headers = await self._fetch_page_content(website)
            
            if not page_content:
                return []
            
            # Analisar cada plataforma
            activities = []
            
            for platform, patterns in self.detection_patterns.items():
                signals = await self._detect_platform_signals(
                    page_content, headers, platform, patterns, website
                )
                
                if signals:
                    activity = self._evaluate_platform_activity(platform, signals)
                    activities.append(activity)
            
            return activities
            
        except Exception as e:
            logger.error(f"Erro analisando {website}: {e}")
            return []
    
    async def _fetch_page_content(self, website: str) -> Tuple[str, Dict]:
        """Buscar conteúdo da página com headers"""
        try:
            # Normalizar URL
            if not website.startswith(('http://', 'https://')):
                website = f"https://{website}"
            
            async with self.session.get(
                website, 
                headers={'User-Agent': 'Mozilla/5.0 (compatible; AdAnalyzer/1.0)'},
                allow_redirects=True
            ) as response:
                
                if response.status == 200:
                    content = await response.text()
                    headers = dict(response.headers)
                    return content, headers
                
                return "", {}
                
        except Exception as e:
            logger.debug(f"Erro fetching {website}: {e}")
            return "", {}
    
    async def _detect_platform_signals(self, content: str, headers: Dict, 
                                     platform: str, patterns: Dict, website: str) -> List[AdSignal]:
        """Detectar sinais de uma plataforma específica"""
        signals = []
        
        # 1. Detectar pixels e tracking codes
        for pixel_pattern in patterns.get('pixels', []):
            matches = re.findall(pixel_pattern, content, re.IGNORECASE)
            if matches:
                signals.append(AdSignal(
                    signal_type='pixel',
                    platform=platform,
                    confidence=0.9,
                    evidence=f"Pixel pattern: {pixel_pattern}",
                    detection_method='regex_content'
                ))
        
        # 2. Detectar scripts de conversão
        for script_pattern in patterns.get('scripts', []):
            if re.search(script_pattern, content, re.IGNORECASE):
                signals.append(AdSignal(
                    signal_type='conversion_script',
                    platform=platform,
                    confidence=0.8,
                    evidence=f"Script pattern: {script_pattern}",
                    detection_method='regex_content'
                ))
        
        # 3. Analisar UTM parameters em links
        utm_signals = self._analyze_utm_parameters(content, platform, patterns)
        signals.extend(utm_signals)
        
        # 4. Detectar redirects e meta tags
        meta_signals = self._analyze_meta_elements(content, platform)
        signals.extend(meta_signals)
        
        return signals
    
    def _analyze_utm_parameters(self, content: str, platform: str, patterns: Dict) -> List[AdSignal]:
        """Analisar parâmetros UTM para detectar campanhas"""
        signals = []
        
        # Buscar links com UTM
        utm_pattern = r'utm_source=([^&\s"\']+)'
        utm_matches = re.findall(utm_pattern, content, re.IGNORECASE)
        
        for utm_source in utm_matches:
            if utm_source.lower() in patterns.get('utm_sources', []):
                signals.append(AdSignal(
                    signal_type='utm_campaign',
                    platform=platform,
                    confidence=0.7,
                    evidence=f"UTM source: {utm_source}",
                    detection_method='utm_analysis'
                ))
        
        # Analisar UTM medium para identificar paid traffic
        paid_mediums = ['cpc', 'ppc', 'paid', 'ads', 'adwords', 'facebook-ads']
        medium_pattern = r'utm_medium=([^&\s"\']+)'
        medium_matches = re.findall(medium_pattern, content, re.IGNORECASE)
        
        for medium in medium_matches:
            if medium.lower() in paid_mediums:
                signals.append(AdSignal(
                    signal_type='paid_medium',
                    platform='generic',
                    confidence=0.6,
                    evidence=f"Paid medium: {medium}",
                    detection_method='utm_analysis'
                ))
        
        return signals
    
    def _analyze_meta_elements(self, content: str, platform: str) -> List[AdSignal]:
        """Analisar meta tags para detecção de pixels"""
        signals = []
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Facebook/Meta verification
            if platform == 'meta':
                fb_metas = soup.find_all('meta', property=re.compile(r'fb:|og:'))
                if fb_metas:
                    signals.append(AdSignal(
                        signal_type='meta_verification',
                        platform='meta',
                        confidence=0.5,
                        evidence=f"Found {len(fb_metas)} FB meta tags",
                        detection_method='meta_analysis'
                    ))
            
            # Google verification
            if platform == 'google_ads':
                google_metas = soup.find_all('meta', attrs={'name': re.compile(r'google')})
                if google_metas:
                    signals.append(AdSignal(
                        signal_type='meta_verification',
                        platform='google_ads',
                        confidence=0.4,
                        evidence=f"Found {len(google_metas)} Google meta tags",
                        detection_method='meta_analysis'
                    ))
                    
        except Exception as e:
            logger.debug(f"Erro analisando meta tags: {e}")
        
        return signals
    
    def _evaluate_platform_activity(self, platform: str, signals: List[AdSignal]) -> RealAdActivity:
        """Avaliar se uma plataforma está realmente ativa"""
        
        # Calcular score baseado nos sinais
        total_confidence = sum(signal.confidence for signal in signals)
        avg_confidence = total_confidence / len(signals) if signals else 0
        
        # Determinar se é provável que esteja ativo
        high_confidence_signals = [s for s in signals if s.confidence >= 0.8]
        pixel_signals = [s for s in signals if s.signal_type == 'pixel']
        
        is_likely_active = (
            len(high_confidence_signals) >= 1 or
            len(pixel_signals) >= 1 or
            avg_confidence >= 0.7
        )
        
        # Estimar nível de investimento baseado na quantidade e tipo de sinais
        investment_level = self._estimate_investment_level(signals)
        
        return RealAdActivity(
            platform=platform,
            is_likely_active=is_likely_active,
            confidence_score=avg_confidence,
            signals=signals,
            estimated_investment_level=investment_level,
            detection_date=datetime.now().isoformat()
        )
    
    def _estimate_investment_level(self, signals: List[AdSignal]) -> str:
        """Estimar nível de investimento baseado nos sinais"""
        
        pixel_count = len([s for s in signals if s.signal_type == 'pixel'])
        script_count = len([s for s in signals if s.signal_type == 'conversion_script'])
        utm_count = len([s for s in signals if s.signal_type in ['utm_campaign', 'paid_medium']])
        
        total_sophistication = pixel_count * 3 + script_count * 2 + utm_count * 1
        
        if total_sophistication >= 8:
            return 'high'
        elif total_sophistication >= 4:
            return 'medium'
        elif total_sophistication >= 1:
            return 'low'
        else:
            return 'unknown'

class OptimizedAdIntelligenceEngine:
    """Engine principal com detecção realista"""
    
    def __init__(self):
        self.detector = RealisticAdDetector()
    
    async def analyze_company_ads(self, company_name: str, website: str) -> List[RealAdActivity]:
        """Analisar atividade publicitária de uma empresa"""
        
        async with self.detector as detector:
            activities = await detector.analyze_website_for_ads(website)
        
        # Log dos resultados
        if activities:
            logger.info(f"✅ {company_name}: {len(activities)} plataformas detectadas")
            for activity in activities:
                logger.info(f"   {activity.platform}: {activity.confidence_score:.2f} confidence, {activity.estimated_investment_level} investment")
        else:
            logger.info(f"❌ {company_name}: Nenhuma atividade publicitária detectada")
        
        return activities
    
    def calculate_realistic_ad_score(self, activities: List[RealAdActivity]) -> float:
        """Scoring realista baseado em detecção real"""
        
        if not activities:
            return 0
        
        score = 0
        
        # Pontuação baseada em plataformas com atividade real
        active_platforms = [a for a in activities if a.is_likely_active]
        
        for activity in active_platforms:
            # Base score por plataforma ativa
            platform_score = 15
            
            # Bonus por confidence
            confidence_bonus = activity.confidence_score * 10
            
            # Bonus por nível de investimento
            investment_bonus = {
                'high': 15,
                'medium': 10,
                'low': 5,
                'unknown': 0
            }.get(activity.estimated_investment_level, 0)
            
            # Bonus por sophistication (número de sinais)
            signal_bonus = min(10, len(activity.signals) * 2)
            
            platform_total = platform_score + confidence_bonus + investment_bonus + signal_bonus
            score += platform_total
        
        return min(100, score)

# Exemplo de uso
async def test_realistic_detection():
    """Teste do sistema realista"""
    
    engine = OptimizedAdIntelligenceEngine()
    
    test_companies = [
        ("Spa Dental Sydney CBD", "https://www.spadentalsydneycbd.com.au/"),
        ("Amazon Australia", "https://www.amazon.com.au/"),
        ("Canva", "https://www.canva.com/"),
    ]
    
    for company_name, website in test_companies:
        print(f"\n🔍 Analisando: {company_name}")
        print("=" * 50)
        
        activities = await engine.analyze_company_ads(company_name, website)
        score = engine.calculate_realistic_ad_score(activities)
        
        print(f"📊 Score realista: {score:.1f}/100")
        
        if activities:
            print("🎯 Atividades detectadas:")
            for activity in activities:
                print(f"  • {activity.platform}: {activity.confidence_score:.2f} confidence")
                print(f"    Investment: {activity.estimated_investment_level}")
                print(f"    Sinais: {len(activity.signals)}")
                for signal in activity.signals[:3]:  # Top 3 signals
                    print(f"      - {signal.signal_type}: {signal.evidence}")
        else:
            print("❌ Nenhuma atividade publicitária detectada")

if __name__ == "__main__":
    asyncio.run(test_realistic_detection())
