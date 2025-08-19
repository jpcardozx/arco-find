#!/usr/bin/env python3
"""
ARCO ADVERTISING INTELLIGENCE - DETECÇÃO 100% GRATUITA
=====================================================
Análise HTTP, pixels, tracking e elementos básicos - SEM CUSTOS
Métodos: HTML parsing, pixel detection, UTM analysis, script detection
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
            }
        }
        
        # UTM Sources que indicam tráfego pago
        self.paid_traffic_sources = {
            'google_ads': ['google', 'adwords', 'googleads', 'cpc', 'sem'],
            'meta': ['facebook', 'instagram', 'fb', 'ig', 'meta'],
            'tiktok': ['tiktok', 'tt', 'bytedance'],
            'linkedin': ['linkedin', 'li']
        }
        
        # Mediums que sempre indicam tráfego pago
        self.paid_mediums = [
            'cpc', 'ppc', 'paid', 'ads', 'adwords', 'cost-per-click',
            'facebook-ads', 'instagram-ads', 'tiktok-ads', 'linkedin-ads',
            'display', 'banner', 'retargeting', 'remarketing', 'social-paid'
        ]
    
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
        timeout = aiohttp.ClientTimeout(total=15)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def analyze_website_free(self, website: str) -> FreeAdAnalysis:
        """Análise gratuita completa de sinais publicitários"""
        try:
            logger.info(f"🔍 Análise gratuita: {website}")
            
            # Buscar conteúdo
            html_content, headers = await self._fetch_website_content(website)
            
            if not html_content:
                return self._create_empty_analysis(website, "Não foi possível acessar")
            
            # Análises gratuitas
            pixel_signals = self._detect_advertising_pixels(html_content)
            utm_signals = self._detect_utm_campaigns(html_content)
            script_signals = self._detect_advertising_scripts(html_content)
            header_signals = self._analyze_response_headers(headers)
            
            # Combinar todos os sinais
            all_signals = pixel_signals + utm_signals + script_signals + header_signals
            platforms = list(set([signal.platform for signal in all_signals]))
            
            # Scoring
            sophistication = self._calculate_pixel_sophistication(all_signals)
            investment_level = self._determine_investment_level(all_signals, sophistication)
            
            analysis = FreeAdAnalysis(
                website=website,
                has_advertising=len(all_signals) > 0,
                platforms_detected=platforms,
                technical_signals=all_signals,
                utm_campaigns=len(utm_signals),
                pixel_sophistication=sophistication,
                investment_level=investment_level,
                analysis_timestamp=datetime.now().isoformat()
            )
            
            logger.info(f"✅ {website}: {len(platforms)} plataformas, score {sophistication:.1f}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erro: {e}")
            return self._create_empty_analysis(website, str(e))
    
    async def _fetch_website_content(self, website: str) -> Tuple[str, Dict]:
        """Buscar conteúdo do website"""
        try:
            if not website.startswith(('http://', 'https://')):
                website = f"https://{website}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with self.session.get(website, headers=headers, allow_redirects=True) as response:
                if response.status == 200:
                    content = await response.text()
                    return content, dict(response.headers)
                return "", {}
                
        except Exception as e:
            logger.debug(f"Erro HTTP {website}: {e}")
            return "", {}
    
    def _detect_advertising_pixels(self, html_content: str) -> List[TechnicalAdSignal]:
        """Detectar pixels de advertising nos padrões conhecidos"""
        signals = []
        
        for platform, patterns in self.free_detection_patterns.items():
            for pattern_name, regex_pattern in patterns.items():
                matches = re.finditer(regex_pattern, html_content, re.IGNORECASE | re.MULTILINE)
                
                for match in matches:
                    confidence = self._calculate_pattern_confidence(pattern_name, match.group())
                    
                    signals.append(TechnicalAdSignal(
                        platform=platform,
                        signal_type=f'pixel_{pattern_name}',
                        confidence=confidence,
                        evidence=match.group()[:150],
                        technical_details=f"Regex: {pattern_name} | Match: {match.group()}"
                    ))
        
        return signals
    
    def _detect_utm_campaigns(self, html_content: str) -> List[TechnicalAdSignal]:
        """Detectar campanhas UTM que indicam tráfego pago"""
        signals = []
        
        # Buscar todos os links com UTM
        utm_pattern = r'href=[\'"][^\'\"]*\?[^\'\"]*utm_([^\'\"]*)[\'"]'
        utm_matches = re.finditer(utm_pattern, html_content, re.IGNORECASE)
        
        found_sources = set()
        
        for match in utm_matches:
            full_url = match.group()
            
            # Extrair utm_source e utm_medium
            source_match = re.search(r'utm_source=([^&\'\"]*)', full_url, re.IGNORECASE)
            medium_match = re.search(r'utm_medium=([^&\'\"]*)', full_url, re.IGNORECASE)
            
            if source_match:
                source = source_match.group(1).lower()
                medium = medium_match.group(1).lower() if medium_match else ""
                
                # Verificar se indica tráfego pago
                platform = self._identify_paid_platform(source, medium)
                
                if platform and f"{platform}_{source}" not in found_sources:
                    found_sources.add(f"{platform}_{source}")
                    
                    confidence = 0.9 if medium in self.paid_mediums else 0.7
                    
                    signals.append(TechnicalAdSignal(
                        platform=platform,
                        signal_type='utm_campaign',
                        confidence=confidence,
                        evidence=f"source={source}, medium={medium}",
                        technical_details=full_url[:200]
                    ))
        
        return signals
    
    def _detect_advertising_scripts(self, html_content: str) -> List[TechnicalAdSignal]:
        """Detectar scripts relacionados a advertising"""
        signals = []
        
        # Scripts específicos
        script_domains = {
            'google_ads': [
                r'googleadservices\.com',
                r'googlesyndication\.com',
                r'googletagservices\.com'
            ],
            'meta': [
                r'connect\.facebook\.net',
                r'facebook\.com/tr'
            ],
            'tiktok': [
                r'analytics\.tiktok\.com'
            ]
        }
        
        for platform, domains in script_domains.items():
            for domain_pattern in domains:
                if re.search(domain_pattern, html_content, re.IGNORECASE):
                    signals.append(TechnicalAdSignal(
                        platform=platform,
                        signal_type='advertising_script',
                        confidence=0.8,
                        evidence=f"Script: {domain_pattern}",
                        technical_details=f"Advertising script for {platform}"
                    ))
        
        return signals
    
    def _analyze_response_headers(self, headers: Dict) -> List[TechnicalAdSignal]:
        """Analisar headers HTTP para sinais de advertising"""
        signals = []
        
        # Headers que podem indicar pixels/tracking
        tracking_headers = {
            'set-cookie': r'(_ga|_gid|_fbp|_fbc|_ttp)',
            'x-fb-debug': r'.*',
            'x-ads-debug': r'.*'
        }
        
        for header_name, pattern in tracking_headers.items():
            if header_name in headers:
                header_value = headers[header_name]
                if re.search(pattern, header_value, re.IGNORECASE):
                    
                    platform = 'google_ads' if '_ga' in header_value else \
                              'meta' if '_fb' in header_value else \
                              'tiktok' if '_ttp' in header_value else 'unknown'
                    
                    if platform != 'unknown':
                        signals.append(TechnicalAdSignal(
                            platform=platform,
                            signal_type='tracking_header',
                            confidence=0.6,
                            evidence=f"{header_name}: {header_value[:100]}",
                            technical_details=f"HTTP header analysis"
                        ))
        
        return signals
    
    def _calculate_pattern_confidence(self, pattern_name: str, match_text: str) -> float:
        """Calcular confiança baseada no tipo de pattern"""
        confidence_map = {
            'gtag_ads': 0.95,          # Muito específico
            'pixel_base': 0.95,        # Facebook pixel específico
            'conversion_tracking': 0.90,
            'pixel_events': 0.85,
            'pixel_init': 0.85,
            'advertising_script': 0.75,
            'utm_campaign': 0.70
        }
        
        base_confidence = confidence_map.get(pattern_name, 0.5)
        
        # Ajustes baseados no conteúdo
        if 'conversion' in match_text.lower():
            base_confidence += 0.1
        if 'track' in match_text.lower():
            base_confidence += 0.05
        
        return min(1.0, base_confidence)
    
    def _identify_paid_platform(self, source: str, medium: str) -> Optional[str]:
        """Identificar se UTM indica tráfego pago"""
        
        # Verificar medium primeiro
        if medium not in self.paid_mediums and medium not in ['cpc', 'paid', 'ads']:
            return None
        
        # Mapear source para plataforma
        for platform, sources in self.paid_traffic_sources.items():
            if source in sources:
                return platform
        
        # Se medium indica pago mas source é desconhecido
        return 'unknown_paid' if medium in self.paid_mediums else None
    
    def _calculate_pixel_sophistication(self, signals: List[TechnicalAdSignal]) -> float:
        """Calcular score de sophistication (0-100)"""
        if not signals:
            return 0.0
        
        score = 0
        
        # Pontuação por tipo de sinal
        for signal in signals:
            if signal.signal_type.startswith('pixel_'):
                score += signal.confidence * 25  # Pixels valem mais
            elif signal.signal_type == 'utm_campaign':
                score += signal.confidence * 15  # UTMs importantes
            elif signal.signal_type == 'advertising_script':
                score += signal.confidence * 20  # Scripts específicos
            else:
                score += signal.confidence * 10  # Outros sinais
        
        # Bonus por diversidade de plataformas
        platforms = set([signal.platform for signal in signals])
        platform_bonus = len(platforms) * 8
        
        # Bonus por múltiplos sinais na mesma plataforma
        high_confidence_signals = [s for s in signals if s.confidence >= 0.8]
        quality_bonus = len(high_confidence_signals) * 5
        
        total_score = score + platform_bonus + quality_bonus
        return min(100.0, total_score)
    
    def _determine_investment_level(self, signals: List[TechnicalAdSignal], sophistication: float) -> str:
        """Determinar nível de investimento baseado em evidências"""
        
        if sophistication >= 75:
            return 'advanced'      # Múltiplas plataformas, tracking sofisticado
        elif sophistication >= 50:
            return 'intermediate'  # Algumas plataformas, tracking básico
        elif sophistication >= 25:
            return 'basic'         # Sinais mínimos de advertising
        else:
            return 'none'          # Sem evidências significativas
    
    def _create_empty_analysis(self, website: str, reason: str) -> FreeAdAnalysis:
        """Criar análise vazia para casos de erro"""
        return FreeAdAnalysis(
            website=website,
            has_advertising=False,
            platforms_detected=[],
            technical_signals=[],
            utm_campaigns=0,
            pixel_sophistication=0.0,
            investment_level='none',
            analysis_timestamp=datetime.now().isoformat()
        )

# TESTE DO SISTEMA GRATUITO
async def test_free_advertising_detection():
    """Teste do detector gratuito"""
    
    test_websites = [
        ("E-commerce Global", "https://www.amazon.com/"),
        ("SaaS Platform", "https://www.canva.com/"),
        ("Government Website", "https://www.melbourne.vic.gov.au/"),
    ]
    
    async with FreeAdvertisingDetector() as detector:
        
        for company_name, website in test_websites:
            print(f"\n🔍 ANÁLISE GRATUITA: {company_name}")
            print("=" * 60)
            
            analysis = await detector.analyze_website_free(website)
            
            print(f"📊 Score Sophistication: {analysis.pixel_sophistication:.1f}/100")
            print(f"🎯 Nível Investimento: {analysis.investment_level}")
            print(f"🔧 Plataformas: {', '.join(analysis.platforms_detected) if analysis.platforms_detected else 'Nenhuma'}")
            print(f"📈 UTM Campaigns: {analysis.utm_campaigns}")
            
            if analysis.technical_signals:
                print(f"\n✅ Sinais Técnicos ({len(analysis.technical_signals)}):")
                for signal in analysis.technical_signals[:5]:  # Top 5
                    print(f"  • {signal.platform}: {signal.signal_type}")
                    print(f"    Confiança: {signal.confidence:.2f} | {signal.evidence}")
            else:
                print("\n❌ Nenhum sinal publicitário detectado")
            
            print(f"\n📊 CONCLUSÃO: {'TEM investimento em ads' if analysis.has_advertising else 'SEM evidências de ads'}")

if __name__ == "__main__":
    print("🚀 ARCO ADVERTISING INTELLIGENCE - DETECÇÃO GRATUITA")
    print("=" * 60)
    asyncio.run(test_free_advertising_detection())
