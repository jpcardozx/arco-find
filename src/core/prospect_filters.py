#!/usr/bin/env python3
"""
🎯 PROSPECT FILTERS
Elimina false positives e foca em SMBs brasileiras reais
"""

import re
from typing import List, Dict
from urllib.parse import urlparse


class ProspectFilters:
    """Filtros inteligentes para qualificação de prospects"""
    
    # Giants e plataformas que não são prospects
    INVALID_DOMAINS = {
        'instagram.com', 'facebook.com', 'twitter.com', 'linkedin.com',
        'reddit.com', 'youtube.com', 'tiktok.com', 'mailchimp.com',
        'google.com', 'microsoft.com', 'amazon.com', 'apple.com',
        'shopify.com', 'wordpress.com', 'wix.com', 'squarespace.com',
        'github.com', 'stackoverflow.com', 'medium.com'
    }
    
    # Indicadores de conteúdo (não são empresas)
    CONTENT_INDICATORS = {
        'artigo', 'post', 'blog', 'guia', 'tutorial', 'como fazer',
        'dicas', 'review', 'avaliação', 'comparação', 'análise',
        '5 dicas', '10 melhores', 'ultimate guide', 'best practices'
    }
    
    # Indicadores de empresa grande (evitar)
    ENTERPRISE_INDICATORS = {
        'magazine luiza', 'mercado livre', 'americanas', 'submarino',
        'b2w', 'via varejo', 'carrefour', 'pão de açúcar', 'extra',
        'casas bahia', 'pontofrio', 'fastshop', 'ricardo eletro'
    }
    
    @classmethod
    def is_valid_smb_prospect(cls, domain: str, title: str, snippet: str) -> bool:
        """
        Valida se é prospect SMB real brasileiro
        
        Args:
            domain: Domínio do site
            title: Título da página/resultado
            snippet: Snippet/descrição
            
        Returns:
            bool: True se é prospect válido
        """
        
        # Clean inputs
        domain = domain.lower().strip()
        title = title.lower().strip()
        snippet = snippet.lower().strip()
        
        # Filter 1: Invalid domains
        if cls._is_invalid_domain(domain):
            return False
        
        # Filter 2: Content indicators
        if cls._is_content_page(title, snippet):
            return False
        
        # Filter 3: Enterprise companies
        if cls._is_enterprise_company(title, snippet):
            return False
        
        # Filter 4: Must have Brazilian presence
        if not cls._has_brazilian_presence(domain, title, snippet):
            return False
        
        return True
    
    @classmethod
    def _is_invalid_domain(cls, domain: str) -> bool:
        """Verifica se domínio é de plataforma/giant"""
        
        # Check exact matches
        if domain in cls.INVALID_DOMAINS:
            return True
        
        # Check subdomains
        for invalid in cls.INVALID_DOMAINS:
            if invalid in domain:
                return True
        
        return False
    
    @classmethod
    def _is_content_page(cls, title: str, snippet: str) -> bool:
        """Verifica se é página de conteúdo (não empresa)"""
        
        text = f"{title} {snippet}"
        
        for indicator in cls.CONTENT_INDICATORS:
            if indicator in text:
                return True
        
        # Padrões específicos de conteúdo
        content_patterns = [
            r'\d+\s+(dicas|formas|maneiras|jeitos)',
            r'como\s+(fazer|criar|otimizar|melhorar)',
            r'(melhores|piores|top)\s+\d+',
            r'(guia|tutorial|passo a passo)',
            r'(review|análise|comparação)\s+de'
        ]
        
        for pattern in content_patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    @classmethod
    def _is_enterprise_company(cls, title: str, snippet: str) -> bool:
        """Verifica se é empresa grande (não SMB)"""
        
        text = f"{title} {snippet}"
        
        for enterprise in cls.ENTERPRISE_INDICATORS:
            if enterprise in text:
                return True
        
        # Indicadores de tamanho
        enterprise_size_indicators = [
            'maior empresa', 'líder do mercado', 'multinacional',
            'bilhões em receita', 'milhares de funcionários',
            'holding', 'grupo empresarial', 'conglomerado'
        ]
        
        for indicator in enterprise_size_indicators:
            if indicator in text:
                return True
        
        return False
    
    @classmethod
    def _has_brazilian_presence(cls, domain: str, title: str, snippet: str) -> bool:
        """Verifica presença brasileira"""
        
        # Brazilian TLD
        if '.com.br' in domain or '.org.br' in domain:
            return True
        
        # Brazilian content indicators
        text = f"{title} {snippet}"
        brazilian_indicators = [
            'brasil', 'brazil', 'brasileiro', 'brasileira',
            'são paulo', 'rio de janeiro', 'belo horizonte',
            'brasília', 'salvador', 'fortaleza', 'curitiba',
            'recife', 'porto alegre', 'goiânia', 'belém'
        ]
        
        for indicator in brazilian_indicators:
            if indicator in text:
                return True
        
        return False
    
    @classmethod
    def calculate_prospect_quality_score(cls, domain: str, title: str, snippet: str,
                                       performance_score: int = 0, saas_tools: List[str] = None) -> int:
        """
        Calcula score de qualidade do prospect (0-100)
        
        Args:
            domain: Domínio
            title: Título
            snippet: Snippet
            performance_score: Score de performance (0-100)
            saas_tools: Lista de ferramentas SaaS detectadas
            
        Returns:
            int: Score de qualidade (0-100)
        """
        
        if not cls.is_valid_smb_prospect(domain, title, snippet):
            return 0
        
        score = 30  # Base score para prospects válidos
        saas_tools = saas_tools or []
        
        # Performance points
        if performance_score < 50:
            score += 25  # Performance crítica
        elif performance_score < 70:
            score += 15  # Performance ruim
        elif performance_score < 85:
            score += 5   # Performance mediana
        
        # SaaS tools points (over-spend indicators)
        expensive_tools = ['typeform', 'hubspot', 'salesforce', 'marketo']
        for tool in expensive_tools:
            if tool in [t.lower() for t in saas_tools]:
                score += 15
        
        # Brazilian TLD bonus
        if '.com.br' in domain:
            score += 10
        
        # Size indicators (SMB sweet spot)
        text = f"{title} {snippet}".lower()
        smb_indicators = [
            'pequena empresa', 'startup', 'pme', 'empreendedor',
            'fundador', 'sócio', 'proprietário', 'familiar'
        ]
        
        for indicator in smb_indicators:
            if indicator in text:
                score += 10
                break
        
        return min(score, 100)


class LeadQualificationEngine:
    """Engine de qualificação de leads para 7-day attack plan"""
    
    def __init__(self):
        self.filters = ProspectFilters()
        
    def qualify_prospects_for_attack_plan(self, prospects: List[Dict]) -> List[Dict]:
        """
        Qualifica prospects para o plano de ataque de 7 dias
        
        Args:
            prospects: Lista de prospects descobertos
            
        Returns:
            List[Dict]: Prospects qualificados com scores
        """
        
        qualified = []
        
        for prospect in prospects:
            # Calculate quality score
            quality_score = self.filters.calculate_prospect_quality_score(
                prospect.get('domain', ''),
                prospect.get('title', ''),
                prospect.get('snippet', ''),
                prospect.get('performance_score', 0),
                prospect.get('saas_tools', [])
            )
            
            # Only qualify if score >= 60
            if quality_score >= 60:
                prospect['quality_score'] = quality_score
                prospect['priority'] = self._determine_priority(quality_score)
                prospect['estimated_monthly_leak'] = self._estimate_monthly_leak(prospect)
                qualified.append(prospect)
        
        # Sort by quality score (highest first)
        qualified.sort(key=lambda x: x['quality_score'], reverse=True)
        
        return qualified
    
    def _determine_priority(self, quality_score: int) -> str:
        """Determina prioridade baseada no score"""
        if quality_score >= 85:
            return "IMMEDIATE"
        elif quality_score >= 70:
            return "HIGH"
        else:
            return "MEDIUM"
    
    def _estimate_monthly_leak(self, prospect: Dict) -> float:
        """Estima vazamento mensal em USD"""
        
        base_leak = 500  # Base minimum
        
        # Performance impact
        performance_score = prospect.get('performance_score', 70)
        if performance_score < 40:
            performance_leak = 2000
        elif performance_score < 60:
            performance_leak = 1200
        elif performance_score < 80:
            performance_leak = 800
        else:
            performance_leak = 0
        
        # SaaS waste
        saas_tools = prospect.get('saas_tools', [])
        saas_waste = 0
        
        expensive_saas = {
            'typeform': 300,
            'hubspot': 500,
            'salesforce': 700,
            'marketo': 800,
            'mailchimp': 100
        }
        
        for tool in saas_tools:
            tool_lower = tool.lower()
            for expensive_tool, waste in expensive_saas.items():
                if expensive_tool in tool_lower:
                    saas_waste += waste
        
        total_leak = base_leak + performance_leak + saas_waste
        
        return round(total_leak, 2)


if __name__ == "__main__":
    # Test filters
    filters = ProspectFilters()
    
    test_cases = [
        # Valid SMB
        ("lojamalu.com.br", "Loja Malu - Fashion Online", "Loja de roupas femininas brasileira"),
        
        # Invalid - content
        ("medium.com", "10 dicas para otimizar seu e-commerce", "Artigo sobre otimização"),
        
        # Invalid - platform
        ("instagram.com", "Instagram Business", "Plataforma social"),
        
        # Invalid - enterprise
        ("magazineluiza.com.br", "Magazine Luiza", "Maior varejista do Brasil")
    ]
    
    print("🧪 TESTE DOS FILTROS DE PROSPECTS")
    print("=" * 50)
    
    for domain, title, snippet in test_cases:
        is_valid = filters.is_valid_smb_prospect(domain, title, snippet)
        score = filters.calculate_prospect_quality_score(domain, title, snippet, 45, ['typeform'])
        
        print(f"\nDomínio: {domain}")
        print(f"Válido: {'✅' if is_valid else '❌'}")
        print(f"Score: {score}/100")
        print(f"Título: {title[:50]}...")
