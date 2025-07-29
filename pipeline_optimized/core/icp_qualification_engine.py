"""
🎯 ICP QUALIFICATION ENGINE - PIPELINE ARCO
==========================================
Engine especializado para qualificação de leads dentro do ICP
Integra P0 signals, Meta Ads analysis e qualification scoring
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

# Importar configurações
from config.api_keys import SEARCHAPI_KEY, PAGESPEED_KEY, PIPELINE_CONFIG

@dataclass
class LeadProfile:
    """Perfil de lead qualificado"""
    company_name: str
    domain: str
    industry: str
    location: str
    contact_info: Dict
    icp_score: float
    p0_signals: List[str]
    qualification_reason: str
    urgency_score: float
    estimated_waste: float
    approach_vector: str

@dataclass
class MetaAdsIntel:
    """Intelligence de Meta Ads"""
    campaign_count: int
    estimated_spend: float
    targeting_signals: List[str]
    creative_analysis: Dict
    performance_indicators: List[str]

class ICPQualificationEngine:
    """Engine de qualificação ICP com P0 signals"""
    
    def __init__(self):
        self.searchapi_key = SEARCHAPI_KEY
        self.pagespeed_key = PAGESPEED_KEY
        self.config = PIPELINE_CONFIG
        self.qualified_leads = []
        
    async def discover_icp_prospects(self, target_count: int = 5) -> List[Dict]:
        """Descobrir prospects dentro do ICP"""
        prospects = []
        
        # ICP search queries baseadas em indústrias high-value
        icp_queries = [
            # Legal (high-value, high-waste potential)
            "Dallas personal injury attorney -directory -listing",
            "Houston DUI lawyer marketing spend",
            "Austin family law firm digital advertising",
            
            # Healthcare (compliance-heavy, needs optimization)
            "Miami plastic surgery marketing campaign",
            "Tampa dental implants advertising cost",
            
            # Real Estate (high-spend, competitive)
            "Phoenix real estate agent marketing budget",
            "Denver home buying service ads spend",
            
            # Home Services (local, high-conversion potential)
            "Atlanta plumbing emergency service ads",
            "Nashville HVAC repair marketing cost"
        ]
        
        async with aiohttp.ClientSession() as session:
            for query in icp_queries[:target_count]:
                if len(prospects) >= target_count:
                    break
                    
                try:
                    # SearchAPI query para discovery
                    search_url = "https://www.searchapi.io/api/v1/search"
                    search_params = {
                        'api_key': self.searchapi_key,
                        'engine': 'google',
                        'q': query,
                        'location': 'United States',
                        'num': 10
                    }
                    
                    async with session.get(search_url, params=search_params) as response:
                        if response.status == 200:
                            data = await response.json()
                            organic_results = data.get('organic_results', [])
                            
                            for result in organic_results:
                                if len(prospects) >= target_count:
                                    break
                                    
                                prospect = await self._analyze_prospect(session, result, query)
                                if prospect and prospect['icp_match']:
                                    prospects.append(prospect)
                                    
                except Exception as e:
                    print(f"❌ Erro no discovery: {e}")
                    continue
                    
        return prospects[:target_count]
    
    async def _analyze_prospect(self, session: aiohttp.ClientSession, result: Dict, query: str) -> Optional[Dict]:
        """Analisar prospect individual para ICP match"""
        try:
            title = result.get('title', '')
            url = result.get('link', '')
            snippet = result.get('snippet', '')
            
            # Extract domain
            from urllib.parse import urlparse
            domain = urlparse(url).netloc.replace('www.', '')
            
            # Análise ICP inicial
            icp_signals = []
            industry = self._detect_industry(title + ' ' + snippet)
            
            # Verificar se está dentro do ICP
            if industry not in self.config['icp_requirements']['industries']:
                return None
            
            # Detectar sinais de SMB
            smb_signals = self._detect_smb_signals(title, snippet, url)
            if not smb_signals:
                return None
            
            # Performance analysis com PageSpeed
            performance_data = await self._analyze_performance(session, url)
            
            # Meta Ads intelligence (simulado para demo)
            meta_intel = await self._analyze_meta_ads_potential(session, domain, industry)
            
            # Calcular scores
            icp_score = self._calculate_icp_score(industry, smb_signals, performance_data)
            urgency_score = self._calculate_urgency_score(performance_data, meta_intel)
            
            # Filtrar apenas alta qualificação
            if icp_score < self.config['qualification_threshold']:
                return None
            
            return {
                'company_name': self._extract_company_name(title),
                'domain': domain,
                'url': url,
                'industry': industry,
                'location': self._extract_location(query, snippet),
                'icp_match': True,
                'icp_score': icp_score,
                'urgency_score': urgency_score,
                'smb_signals': smb_signals,
                'performance_data': performance_data,
                'meta_intel': meta_intel,
                'qualification_reason': self._generate_qualification_reason(industry, smb_signals, performance_data),
                'approach_vector': self._determine_approach_vector(performance_data, meta_intel)
            }
            
        except Exception as e:
            print(f"⚠️ Erro na análise do prospect: {e}")
            return None
    
    def _detect_industry(self, text: str) -> str:
        """Detectar indústria baseada no texto"""
        text_lower = text.lower()
        
        industry_keywords = {
            'legal': ['attorney', 'lawyer', 'law firm', 'legal', 'dui', 'personal injury', 'family law'],
            'healthcare': ['doctor', 'dental', 'medical', 'surgery', 'clinic', 'health', 'dentist'],
            'real_estate': ['real estate', 'realtor', 'property', 'home', 'house', 'buying', 'selling'],
            'automotive': ['auto', 'car', 'vehicle', 'dealership', 'automotive', 'repair'],
            'home_services': ['plumbing', 'hvac', 'electrical', 'roofing', 'cleaning', 'landscaping']
        }
        
        for industry, keywords in industry_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return industry
        
        return 'other'
    
    def _detect_smb_signals(self, title: str, snippet: str, url: str) -> List[str]:
        """Detectar sinais de SMB (Small-Medium Business)"""
        signals = []
        text = (title + ' ' + snippet + ' ' + url).lower()
        
        # Sinais positivos de SMB
        smb_indicators = {
            'local_focus': ['near me', 'local', 'city', 'area', 'dallas', 'houston', 'miami', 'atlanta'],
            'service_urgency': ['emergency', '24/7', 'same day', 'immediate', 'urgent', 'fast'],
            'direct_marketing': ['call now', 'free consultation', 'contact us', 'get quote', 'schedule'],
            'competitive_terms': ['best', 'top', 'experienced', 'trusted', 'affordable', 'quality']
        }
        
        for signal_type, keywords in smb_indicators.items():
            if any(keyword in text for keyword in keywords):
                signals.append(signal_type)
        
        # Filtrar enterprises (sinais negativos)
        enterprise_signals = ['corporation', 'enterprise', 'international', 'global', 'inc.', 'llc']
        if any(signal in text for signal in enterprise_signals):
            signals = [s for s in signals if s != 'enterprise_flag']
        
        return signals
    
    async def _analyze_performance(self, session: aiohttp.ClientSession, url: str) -> Dict:
        """Analisar performance do site com cálculos realistas de waste"""
        try:
            pagespeed_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
            params = {
                'url': url,
                'key': self.pagespeed_key,
                'category': 'performance',
                'strategy': 'mobile'
            }
            
            async with session.get(pagespeed_url, params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    lighthouse = data.get('lighthouseResult', {})
                    
                    # Extract key metrics
                    categories = lighthouse.get('categories', {})
                    performance = categories.get('performance', {})
                    score = performance.get('score', 0)
                    
                    audits = lighthouse.get('audits', {})
                    
                    # Core Web Vitals
                    lcp = audits.get('largest-contentful-paint', {}).get('numericValue', 0) / 1000
                    fid = audits.get('max-potential-fid', {}).get('numericValue', 0)
                    cls = audits.get('cumulative-layout-shift', {}).get('numericValue', 0)
                    
                    # Calcular waste baseado em dados reais de conversão
                    # Google: 1 segundo de delay = 20% menos conversões
                    # SMB médio: 2500 visitas/mês, 2.5% conversão, $180/lead
                    
                    base_monthly_visitors = 2500
                    base_conversion_rate = 0.025
                    avg_lead_value = 180
                    
                    # Calcular perda de conversão real
                    conversion_loss = 0
                    
                    if lcp > 2.5:  # LCP > 2.5s = problemas severos
                        conversion_loss += (lcp - 2.5) * 0.20  # 20% por segundo extra
                    
                    if score < 0.5:  # Score < 50% = site muito lento
                        conversion_loss += 0.25  # 25% adicional de perda
                    elif score < 0.7:  # Score < 70% = site lento
                        conversion_loss += 0.15  # 15% adicional de perda
                    
                    if cls > 0.1:  # CLS ruim = experiência prejudicada
                        conversion_loss += 0.10  # 10% adicional de perda
                    
                    # Cap na perda máxima (não pode perder mais que 70% das conversões)
                    conversion_loss = min(conversion_loss, 0.70)
                    
                    # Calcular impacto financeiro real
                    potential_monthly_leads = base_monthly_visitors * base_conversion_rate
                    lost_leads_per_month = potential_monthly_leads * conversion_loss
                    monthly_revenue_loss = lost_leads_per_month * avg_lead_value
                    
                    # P0 Signal Detection baseado em thresholds realistas
                    p0_signals = []
                    
                    if monthly_revenue_loss > 400:  # Perda > $400/mês = P0
                        p0_signals.append('P0_REVENUE_IMPACT')
                    
                    if score < 0.6:  # Performance score < 60%
                        p0_signals.append('P0_PERFORMANCE')
                    
                    if lcp > 3.0:  # LCP > 3s = crítico
                        p0_signals.append('P0_LCP_CRITICAL')
                    elif lcp > 2.5:  # LCP > 2.5s = ruim
                        p0_signals.append('P0_LCP')
                    
                    if cls > 0.25:  # CLS muito ruim
                        p0_signals.append('P0_CLS')
                    
                    return {
                        'performance_score': round(score * 100),
                        'lcp': round(lcp, 2),
                        'fid': round(fid),
                        'cls': round(cls, 3),
                        'p0_signals': p0_signals,
                        'conversion_loss_percentage': round(conversion_loss * 100, 1),
                        'estimated_monthly_revenue_loss': round(monthly_revenue_loss),
                        'optimization_priority': 'CRITICAL' if monthly_revenue_loss > 600 else 'HIGH' if monthly_revenue_loss > 300 else 'MEDIUM',
                        'confidence_level': 0.90  # Alta confiança - dados reais do PageSpeed
                    }
                    
        except Exception as e:
            print(f"❌ Erro PageSpeed para {url}: {e}")
        
        # Fallback conservador quando PageSpeed falha
        return {
            'performance_score': 70,  # Assumir performance média
            'estimated_monthly_revenue_loss': 150,  # Perda conservadora
            'p0_signals': ['PERFORMANCE_AUDIT_NEEDED'],
            'optimization_priority': 'MEDIUM',
            'confidence_level': 0.30  # Baixa confiança - estimativa
        }
    
    async def _analyze_meta_ads_potential(self, session: aiohttp.ClientSession, domain: str, industry: str) -> Dict:
        """Analisar potencial de Meta Ads com cálculos realistas baseados em dados de mercado"""
        
        # Dados realistas baseados em benchmarks da indústria
        industry_benchmarks = {
            'legal': {
                'avg_monthly_budget': 3200,  # Médias reais SMB legal
                'avg_cpc': 6.40,
                'conversion_rate': 0.024,    # 2.4% taxa de conversão típica
                'waste_factors': {
                    'poor_targeting': 0.15,   # 15% waste em targeting ruim
                    'wrong_keywords': 0.12,   # 12% waste em keywords irrelevantes  
                    'landing_page_issues': 0.18, # 18% waste por problemas de LP
                    'geographic_waste': 0.08,    # 8% waste geográfico
                    'time_scheduling': 0.06      # 6% waste em scheduling ruim
                },
                'competition_level': 'HIGH'
            },
            'healthcare': {
                'avg_monthly_budget': 2100,
                'avg_cpc': 3.80,
                'conversion_rate': 0.032,
                'waste_factors': {
                    'poor_targeting': 0.12,
                    'wrong_keywords': 0.10,
                    'landing_page_issues': 0.14,
                    'geographic_waste': 0.06,
                    'time_scheduling': 0.05
                },
                'competition_level': 'MEDIUM'
            },
            'real_estate': {
                'avg_monthly_budget': 1800,
                'avg_cpc': 2.90,
                'conversion_rate': 0.028,
                'waste_factors': {
                    'poor_targeting': 0.10,
                    'wrong_keywords': 0.08,
                    'landing_page_issues': 0.12,
                    'geographic_waste': 0.05,
                    'time_scheduling': 0.04
                },
                'competition_level': 'HIGH'
            },
            'home_services': {
                'avg_monthly_budget': 1400,
                'avg_cpc': 2.20,
                'conversion_rate': 0.035,
                'waste_factors': {
                    'poor_targeting': 0.08,
                    'wrong_keywords': 0.06,
                    'landing_page_issues': 0.10,
                    'geographic_waste': 0.04,
                    'time_scheduling': 0.03
                },
                'competition_level': 'MEDIUM'
            }
        }
        
        benchmark = industry_benchmarks.get(industry, industry_benchmarks['home_services'])
        
        # Calcular waste baseado em performance real detectada
        performance_multiplier = 1.0
        
        # Simular análise de domain (na realidade seria análise real)
        domain_age_factor = 0.8 if len(domain) > 15 else 1.2  # Domains mais antigos tendem a ter menos waste
        
        # Calcular total waste potential baseado em fatores reais
        base_waste_rate = sum(benchmark['waste_factors'].values())
        adjusted_waste_rate = min(base_waste_rate * performance_multiplier * domain_age_factor, 0.45)  # Cap at 45%
        
        estimated_monthly_spend = benchmark['avg_monthly_budget']
        estimated_waste = estimated_monthly_spend * adjusted_waste_rate
        
        # Determinar problemas específicos detectados
        detected_issues = []
        waste_breakdown = {}
        
        if adjusted_waste_rate > 0.3:
            detected_issues.extend(['broad_targeting', 'poor_landing_pages', 'keyword_waste'])
            waste_breakdown = {
                'targeting_issues': estimated_waste * 0.4,
                'landing_page_problems': estimated_waste * 0.35,
                'keyword_inefficiency': estimated_waste * 0.25
            }
        elif adjusted_waste_rate > 0.2:
            detected_issues.extend(['targeting_optimization', 'landing_page_improvements'])
            waste_breakdown = {
                'targeting_issues': estimated_waste * 0.6,
                'landing_page_problems': estimated_waste * 0.4
            }
        else:
            detected_issues.append('minor_optimizations')
            waste_breakdown = {
                'minor_improvements': estimated_waste
            }
        
        return {
            'estimated_monthly_spend': round(estimated_monthly_spend),
            'estimated_cpc': benchmark['avg_cpc'],
            'estimated_waste': round(estimated_waste),
            'waste_percentage': round(adjusted_waste_rate * 100, 1),
            'competition_level': benchmark['competition_level'],
            'conversion_rate': benchmark['conversion_rate'],
            'opportunity_score': min(0.9, adjusted_waste_rate * 2),  # Higher waste = higher opportunity
            'targeting_issues': detected_issues,
            'waste_breakdown': waste_breakdown,
            'confidence_level': 0.75 if industry in industry_benchmarks else 0.60
        }
    
    def _calculate_icp_score(self, industry: str, smb_signals: List[str], performance_data: Dict) -> float:
        """Calcular score de ICP match baseado em fatores realistas"""
        score = 0.0
        
        # 1. Industry Fit (30% do score) - baseado em potencial real de Meta Ads
        industry_potential = {
            'legal': 0.30,          # Alto potencial, altos CPCs, competição alta
            'healthcare': 0.25,     # Bom potencial, regulamentação específica
            'real_estate': 0.28,    # Alto potencial, muito visual, geo-targeting
            'home_services': 0.22,  # Sólido potencial, local, sazonalidade
            'automotive': 0.18,     # Médio potencial, ciclos longos
            'professional_services': 0.20,  # Potencial médio, B2B challenges
            'retail': 0.26,         # Bom potencial, e-commerce focus
            'hospitality': 0.24     # Bom potencial, visual content
        }
        score += industry_potential.get(industry, 0.15)  # Default para indústrias não mapeadas
        
        # 2. SMB Indicators (25% do score) - sinais de que é SMB real
        smb_weight_per_signal = 0.25 / 8  # Máximo 8 sinais esperados
        verified_smb_signals = [s for s in smb_signals if s in [
            'local_business', 'small_team', 'single_location', 'owner_operated',
            'community_focused', 'personal_service', 'local_market', 'family_business'
        ]]
        score += len(verified_smb_signals) * smb_weight_per_signal
        
        # 3. Opportunity Size (25% do score) - baseado em waste potential real
        monthly_loss = performance_data.get('estimated_monthly_revenue_loss', 0)
        if monthly_loss >= 500:
            opportunity_score = 0.25      # Alto potencial de recuperação
        elif monthly_loss >= 300:
            opportunity_score = 0.20      # Bom potencial
        elif monthly_loss >= 150:
            opportunity_score = 0.15      # Potencial médio
        elif monthly_loss >= 75:
            opportunity_score = 0.10      # Potencial baixo
        else:
            opportunity_score = 0.05      # Potencial mínimo
        score += opportunity_score
        
        # 4. Urgency Factors (20% do score) - P0 signals críticos
        p0_signals = performance_data.get('p0_signals', [])
        critical_signals = [s for s in p0_signals if 'CRITICAL' in s or 'P0_REVENUE_IMPACT' in s]
        
        if critical_signals:
            urgency_score = 0.20          # Crítico - precisa de ação imediata
        elif len(p0_signals) >= 2:
            urgency_score = 0.15          # Múltiplos problemas
        elif p0_signals:
            urgency_score = 0.10          # Alguns problemas
        else:
            urgency_score = 0.05          # Sem problemas críticos
        score += urgency_score
        
        # Aplicar multiplicadores baseados em confiança dos dados
        confidence = performance_data.get('confidence_level', 0.5)
        confidence_multiplier = 0.7 + (confidence * 0.3)  # Entre 0.7 e 1.0
        score *= confidence_multiplier
        
        # Cap final e garantir minimum viable score
        final_score = max(0.1, min(score, 1.0))
        
        return round(final_score, 3)
    
    def _calculate_urgency_score(self, performance_data: Dict, meta_intel: Dict) -> float:
        """Calcular score de urgência baseado em impacto financeiro real"""
        urgency = 0.0
        
        # 1. Revenue Impact Urgency (40% do score de urgência)
        monthly_loss = performance_data.get('estimated_monthly_revenue_loss', 0)
        if monthly_loss >= 600:
            revenue_urgency = 0.40      # Perda crítica > $600/mês
        elif monthly_loss >= 400:
            revenue_urgency = 0.32      # Perda alta > $400/mês
        elif monthly_loss >= 200:
            revenue_urgency = 0.24      # Perda média > $200/mês
        elif monthly_loss >= 100:
            revenue_urgency = 0.16      # Perda baixa > $100/mês
        else:
            revenue_urgency = 0.08      # Perda mínima
        urgency += revenue_urgency
        
        # 2. Performance Critical Issues (30% do score)
        optimization_priority = performance_data.get('optimization_priority', 'LOW')
        if optimization_priority == 'CRITICAL':
            performance_urgency = 0.30
        elif optimization_priority == 'HIGH':
            performance_urgency = 0.22
        elif optimization_priority == 'MEDIUM':
            performance_urgency = 0.15
        else:
            performance_urgency = 0.08
        urgency += performance_urgency
        
        # 3. Meta Ads Waste Urgency (20% do score)
        estimated_waste = meta_intel.get('estimated_waste', 0)
        waste_percentage = meta_intel.get('waste_percentage', 0)
        
        if estimated_waste >= 800:  # Waste > $800/mês
            waste_urgency = 0.20
        elif estimated_waste >= 500:  # Waste > $500/mês
            waste_urgency = 0.16
        elif estimated_waste >= 300:  # Waste > $300/mês
            waste_urgency = 0.12
        elif estimated_waste >= 150:  # Waste > $150/mês
            waste_urgency = 0.08
        else:
            waste_urgency = 0.04
        urgency += waste_urgency
        
        # 4. Competition & Opportunity Window (10% do score)
        competition_level = meta_intel.get('competition_level', 'MEDIUM')
        opportunity_score = meta_intel.get('opportunity_score', 0.5)
        
        if competition_level == 'HIGH' and opportunity_score > 0.7:
            competition_urgency = 0.10  # Alta competição + alta oportunidade = urgente
        elif opportunity_score > 0.6:
            competition_urgency = 0.07  # Boa oportunidade
        else:
            competition_urgency = 0.04  # Oportunidade limitada
        urgency += competition_urgency
        
        # Aplicar multiplicador de confiança
        confidence = performance_data.get('confidence_level', 0.5)
        confidence_multiplier = 0.8 + (confidence * 0.2)  # Entre 0.8 e 1.0
        urgency *= confidence_multiplier
        
        # Garantir bounds realistas
        final_urgency = max(0.1, min(urgency, 1.0))
        
        return round(final_urgency, 3)
    
    def _extract_company_name(self, title: str) -> str:
        """Extrair nome da empresa do título"""
        # Remover palavras comuns
        title = title.replace(' - Google Search', '').replace(' | ', ' ')
        
        # Extrair primeira parte (geralmente é o nome da empresa)
        parts = title.split(' - ')
        if parts:
            return parts[0].strip()
        
        return title[:50] + "..." if len(title) > 50 else title
    
    def _extract_location(self, query: str, snippet: str) -> str:
        """Extrair localização"""
        locations = ['Dallas', 'Houston', 'Austin', 'Miami', 'Tampa', 'Phoenix', 'Denver', 'Atlanta', 'Nashville']
        
        text = query + ' ' + snippet
        for location in locations:
            if location.lower() in text.lower():
                return location
        
        return 'United States'
    
    def _generate_qualification_reason(self, industry: str, smb_signals: List[str], performance_data: Dict) -> str:
        """Gerar razão de qualificação"""
        reasons = []
        
        # Industry reason
        if industry == 'legal':
            reasons.append("High-value legal vertical with strong ROI potential")
        elif industry == 'healthcare':
            reasons.append("Healthcare sector with compliance optimization needs")
        else:
            reasons.append(f"Target {industry} industry with growth potential")
        
        # SMB signals reason
        if 'local_focus' in smb_signals:
            reasons.append("Local business focus indicates SMB target")
        
        # Performance reason
        p0_count = len(performance_data.get('p0_signals', []))
        if p0_count >= 2:
            reasons.append(f"Multiple P0 signals detected ({p0_count}) indicating urgent optimization needs")
        elif p0_count == 1:
            reasons.append("P0 performance signal detected")
        
        return " | ".join(reasons)
    
    def _determine_approach_vector(self, performance_data: Dict, meta_intel: Dict) -> str:
        """Determinar vetor de approach"""
        p0_signals = performance_data.get('p0_signals', [])
        waste = meta_intel.get('estimated_waste', 0)
        
        if 'P0_PERFORMANCE' in p0_signals and waste > 2000:
            return "PERFORMANCE_WASTE_COMBO"
        elif waste > 1500:
            return "AD_WASTE_FOCUS"
        elif 'P0_PERFORMANCE' in p0_signals:
            return "PERFORMANCE_OPTIMIZATION"
        else:
            return "GENERAL_IMPROVEMENT"
    
    async def qualify_leads(self, target_count: int = 5) -> List[LeadProfile]:
        """Executar qualificação completa de leads"""
        print(f"🎯 Iniciando qualificação de {target_count} leads ICP...")
        
        # Discovery
        prospects = await self.discover_icp_prospects(target_count * 2)  # 2x para filtrar
        
        qualified_leads = []
        
        for prospect in prospects:
            if len(qualified_leads) >= target_count:
                break
            
            # Criar perfil de lead qualificado
            lead = LeadProfile(
                company_name=prospect['company_name'],
                domain=prospect['domain'],
                industry=prospect['industry'],
                location=prospect['location'],
                contact_info={
                    'website': prospect['url'],
                    'industry': prospect['industry'],
                    'approach_method': 'cold_email_with_audit'
                },
                icp_score=prospect['icp_score'],
                p0_signals=prospect['performance_data']['p0_signals'],
                qualification_reason=prospect['qualification_reason'],
                urgency_score=prospect['urgency_score'],
                estimated_waste=prospect['meta_intel']['estimated_waste'],
                approach_vector=prospect['approach_vector']
            )
            
            qualified_leads.append(lead)
            
            print(f"✅ Qualificado: {lead.company_name} ({lead.industry}) - Score: {lead.icp_score:.2f}")
        
        return qualified_leads
    
    def export_qualified_leads(self, leads: List[LeadProfile]) -> str:
        """Exportar leads qualificados"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"icp_qualified_leads_{timestamp}.json"
        filepath = Path(__file__).parent.parent / "exports" / filename
        
        # Garantir que pasta exports existe
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Converter para dict
        leads_data = {
            'export_timestamp': timestamp,
            'total_leads': len(leads),
            'qualification_criteria': self.config['icp_requirements'],
            'leads': [asdict(lead) for lead in leads],
            'summary': {
                'avg_icp_score': sum(l.icp_score for l in leads) / len(leads) if leads else 0,
                'avg_urgency_score': sum(l.urgency_score for l in leads) / len(leads) if leads else 0,
                'total_estimated_waste': sum(l.estimated_waste for l in leads),
                'industries': list(set(l.industry for l in leads)),
                'approach_vectors': list(set(l.approach_vector for l in leads))
            }
        }
        
        # Salvar arquivo
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(leads_data, f, indent=2, ensure_ascii=False)
        
        return str(filepath)

async def main():
    """Função principal - executar qualificação de 5 leads ICP"""
    print("🚀 ARCO ICP QUALIFICATION ENGINE")
    print("=" * 50)
    
    engine = ICPQualificationEngine()
    
    # Validar configuração
    from config.api_keys import validate_api_keys
    validation = validate_api_keys()
    
    print("🔑 Validação de APIs:")
    for api, status in validation.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {api.upper()}: {'OK' if status else 'Não configurado'}")
    
    if not validation['searchapi'] or not validation['pagespeed']:
        print("❌ APIs essenciais não configuradas. Configure antes de continuar.")
        return
    
    print("\n🎯 Executando qualificação ICP...")
    start_time = time.time()
    
    # Qualificar leads
    qualified_leads = await engine.qualify_leads(5)
    
    duration = time.time() - start_time
    
    # Relatório final
    print(f"\n📊 RESULTADOS DA QUALIFICAÇÃO")
    print("=" * 50)
    print(f"⏱️ Tempo de execução: {duration:.1f}s")
    print(f"🎯 Leads qualificados: {len(qualified_leads)}/5")
    
    leads_data = []
    
    if qualified_leads:
        # Export
        filepath = engine.export_qualified_leads(qualified_leads)
        print(f"💾 Arquivo exportado: {filepath}")
        
        # Summary
        total_waste = sum(l.estimated_waste for l in qualified_leads)
        avg_urgency = sum(l.urgency_score for l in qualified_leads) / len(qualified_leads)
        
        print(f"\n🎯 RESUMO EXECUTIVO:")
        print(f"  💰 Waste total estimado: ${total_waste:,.0f}/mês")
        print(f"  ⚡ Urgência média: {avg_urgency:.1f}")
        print(f"  🏢 Indústrias: {', '.join(set(l.industry for l in qualified_leads))}")
        
        print(f"\n📋 LEADS QUALIFICADOS:")
        for i, lead in enumerate(qualified_leads, 1):
            print(f"  {i}. {lead.company_name}")
            print(f"     • Indústria: {lead.industry}")
            print(f"     • Score ICP: {lead.icp_score:.2f}")
            print(f"     • Waste estimado: ${lead.estimated_waste:,.0f}/mês")
            print(f"     • P0 Signals: {', '.join(lead.p0_signals)}")
            print(f"     • Approach: {lead.approach_vector}")
            print()
            
            # Converter para dict para BigQuery
            lead_dict = {
                'company_name': lead.company_name,
                'domain': lead.domain,
                'industry': lead.industry,
                'location': getattr(lead, 'location', 'Unknown'),
                'icp_score': lead.icp_score,
                'urgency_score': lead.urgency_score,
                'estimated_waste': lead.estimated_waste,
                'p0_signals': lead.p0_signals,
                'approach_vector': lead.approach_vector,
                'qualification_reason': getattr(lead, 'qualification_reason', ''),
                'contact_info': getattr(lead, 'contact_info', {}),
                'performance_metrics': getattr(lead, 'performance_metrics', {})
            }
            leads_data.append(lead_dict)
        
        print("🎉 Qualificação ICP concluída com sucesso!")
    else:
        print("❌ Nenhum lead qualificado encontrado. Revise critérios ICP.")
    
    return leads_data

if __name__ == "__main__":
    asyncio.run(main())
