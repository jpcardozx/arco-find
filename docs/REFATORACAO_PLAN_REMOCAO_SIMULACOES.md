# 🔧 PLANO DE REFATORAÇÃO: REMOÇÃO DE SIMULAÇÕES E IMPLEMENTAÇÃO DE INTELIGÊNCIA REAL

**Objetivo:** Transformar sistema de simulações em engine baseado em dados reais  
**Timeline:** 5-7 dias de desenvolvimento focado  
**Prioridade:** CRÍTICA - sistema atual não é confiável para produção

---

## 🚫 CÓDIGO PARA REMOÇÃO IMEDIATA

### 1. **Thrash Index Simulado**

**Localização:** `_calculate_thrash_index()` linha ~461

```python
# REMOVER COMPLETAMENTE:
estimated_median_duration = max(14, len(creatives) * 7)  # Estimativa conservadora
return total_creatives / (estimated_median_duration / 7 + 1)
```

**SUBSTITUIR POR:**

```python
def _calculate_real_thrash_index(self, creatives: List[Dict]) -> Optional[float]:
    """Calcula instabilidade baseado em datas reais dos ads"""
    active_periods = []
    for creative in creatives:
        start = creative.get('start_date')
        end = creative.get('end_date')
        if start:
            # Parse real dates and calculate actual duration
            active_periods.append(self._parse_ad_duration(start, end))

    if not active_periods:
        return None  # Sem dados reais = sem score

    # Análise real de instabilidade
    return self._analyze_campaign_stability(active_periods)
```

### 2. **Median Duration Mock**

**Localização:** `_calculate_median_duration()` linha ~467

```python
# REMOVER:
return max(14, len(creatives) * 7)  # Estimativa: 1 semana por criativo
```

**SUBSTITUIR POR:**

```python
def _calculate_real_duration(self, creatives: List[Dict]) -> Optional[int]:
    """Calcula duração real baseado em start_date/end_date"""
    durations = []
    for creative in creatives:
        duration = self._parse_ad_duration(creative.get('start_date'), creative.get('end_date'))
        if duration:
            durations.append(duration)

    return statistics.median(durations) if durations else None
```

### 3. **LCP Fallback de 5000ms**

**Localização:** `_get_lcp_metric()` linha ~664

```python
# REMOVER:
return 5000  # Default alto se não tem API key
# E também:
return 5000  # Default
```

**SUBSTITUIR POR:**

```python
def _get_real_lcp_metric(self, url: str) -> Optional[float]:
    """Busca LCP real ou retorna None se indisponível"""
    try:
        # Implementação real com retry e cache
        return await self._fetch_pagespeed_with_retry(url)
    except Exception as e:
        logger.warning(f"LCP unavailable for {url}: {e}")
        return None  # Transparência: sem dados = sem score
```

### 4. **Format Diversity Mock**

**Localização:** `_analyze_format_diversity()` linha ~596

```python
# REMOVER:
text_only = 0
for creative in creatives:
    text = creative.get('text', '')
    if len(text) > 50 and not any(word in text.lower() for word in ['video', 'image', 'photo']):
        text_only += 1
```

**SUBSTITUIR POR:**

```python
def _analyze_real_format_diversity(self, creatives: List[Dict]) -> Optional[Dict]:
    """Analisa tipos de mídia reais do Meta Ad Library"""
    format_data = {
        'has_video': False,
        'has_image': False,
        'has_carousel': False,
        'text_only': False
    }

    for creative in creatives:
        snapshot = creative.get('snapshot', {})
        # Analisa campos reais: video_preview_image_url, images, etc.
        if snapshot.get('video_preview_image_url'):
            format_data['has_video'] = True
        if snapshot.get('images'):
            format_data['has_image'] = True
        # ... análise baseada em dados reais do Meta

    return format_data if any(format_data.values()) else None
```

### 5. **Message Match Superficial**

**Localização:** `_calculate_message_match()` linha ~629

```python
# REMOVER:
similarities = []
for i in range(len(texts)):
    for j in range(i+1, len(texts)):
        sim = self._calculate_text_similarity(texts[i], texts[j])
        similarities.append(sim)
```

**SUBSTITUIR POR:**

```python
def _calculate_semantic_message_match(self, creatives: List[Dict], html: str) -> Optional[float]:
    """Análise semântica real usando embeddings ou TF-IDF"""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        # Extrai textos dos ads
        ad_texts = [f"{c.get('headline', '')} {c.get('text', '')}" for c in creatives]

        # Extrai conteúdo relevante da landing page
        lp_content = self._extract_landing_content(html)

        if not ad_texts or not lp_content:
            return None

        # TF-IDF real em vez de Jaccard simplificado
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform(ad_texts + [lp_content])

        # Similaridade real
        similarity_matrix = cosine_similarity(tfidf_matrix)
        return float(similarity_matrix[-1, :-1].mean())  # LP vs ads average

    except ImportError:
        logger.warning("sklearn not available, skipping message match")
        return None
```

---

## 🔧 REFATORAÇÕES CRÍTICAS

### 1. **Sistema de Confiança por Métrica**

```python
@dataclass
class MetricConfidence:
    value: float
    confidence: float  # 0.0 to 1.0
    source: str       # 'real_data', 'estimated', 'fallback'

class ConfidenceBasedScoring:
    def calculate_weighted_score(self, metrics: Dict[str, MetricConfidence]) -> int:
        """Score apenas com métricas confiáveis"""
        total_score = 0
        total_weight = 0

        for metric_name, metric in metrics.items():
            if metric.confidence >= 0.7:  # Só métricas confiáveis
                weight = self.METRIC_WEIGHTS[metric_name] * metric.confidence
                total_score += metric.value * weight
                total_weight += weight

        return int(total_score / total_weight) if total_weight > 0 else 0
```

### 2. **Domain Resolution Inteligente**

```python
class SmartDomainResolver:
    def __init__(self):
        self.domain_cache = {}
        self.search_patterns = [
            '"{company}" {city} site:',
            '"{company}" contact site:',
            '"{company}" about site:'
        ]

    async def resolve_domain(self, company: str, city: str) -> Optional[str]:
        """Resolve domínio real da empresa"""
        cache_key = f"{company}_{city}"
        if cache_key in self.domain_cache:
            return self.domain_cache[cache_key]

        for pattern in self.search_patterns:
            domain = await self._search_company_domain(pattern.format(company=company, city=city))
            if domain and await self._validate_domain(domain, company):
                self.domain_cache[cache_key] = domain
                return domain

        return None
```

### 3. **Query Performance Intelligence**

```python
class QueryIntelligence:
    def __init__(self):
        self.query_performance = {}  # query -> {volume, quality, last_updated}

    async def optimize_queries_for_vertical(self, vertical: str, cities: List[str]) -> List[str]:
        """Retorna apenas queries que funcionam"""
        base_queries = self.VERTICAL_QUERIES[vertical]
        optimized = []

        for query_template in base_queries:
            avg_volume = 0
            for city in cities[:2]:  # Test with 2 cities
                query = query_template.format(city=city)
                volume = await self._test_query_volume(query)
                avg_volume += volume

            if avg_volume >= 5:  # Minimum viable volume
                optimized.append(query_template)
                self.query_performance[query_template] = {
                    'avg_volume': avg_volume / len(cities),
                    'last_tested': datetime.now()
                }

        return optimized
```

### 4. **Transparent Scoring System**

```python
class TransparentScoring:
    def generate_score_breakdown(self, lead: ActionableSMBLead) -> Dict:
        """Mostra exatamente de onde vem cada ponto"""
        breakdown = {
            'total_score': lead.qualification_score,
            'confidence_level': self._calculate_overall_confidence(lead),
            'score_sources': {
                'real_data_points': 0,
                'estimated_points': 0,
                'fallback_points': 0
            },
            'metric_details': {}
        }

        # Para cada métrica, documenta fonte e confiança
        for metric_name, value in lead.__dict__.items():
            if isinstance(value, (int, float)) and metric_name.endswith('_score'):
                source_info = self._get_metric_source_info(metric_name, value)
                breakdown['metric_details'][metric_name] = source_info

        return breakdown
```

---

## 📊 IMPLEMENTAÇÃO PHASE-BY-PHASE

### **Phase 1: Audit e Remoção (Dia 1-2)**

```bash
# Script de audit automático
grep -r "# ESTIMATIVA\|# MOCK\|# Default\|# Simulação" *.py
grep -r "max(14,\|return 5000\|estimated_" *.py
```

**Checklist:**

- [ ] Remove todos os fallbacks de 5000ms
- [ ] Remove estimativas baseadas em len(creatives)
- [ ] Remove análises de texto superficiais
- [ ] Implementa sistema de Optional[float] para métricas indisponíveis

### **Phase 2: Intelligence Implementation (Dia 3-4)**

**Prioridades:**

1. Domain resolution real
2. Query performance tracking
3. Confidence-based scoring
4. Real format analysis usando Meta Ad Library fields

### **Phase 3: Advanced Analytics (Dia 5-7)**

**Features:**

1. Semantic message match com TF-IDF
2. Landing page analysis com ferramentas reais
3. Predictive scoring baseado em padrões históricos
4. A/B testing de queries e verticais

---

## 🎯 SUCCESS METRICS PÓS-REFATORAÇÃO

### **Antes (Atual)**

- Domain resolution: 0%
- Score confidence: ~30% (muitos fallbacks)
- Query consistency: 40% (hvac fails, lawyer inconsistent)
- Qualification rate: 2.3%

### **Depois (Target)**

- Domain resolution: 80%+
- Score confidence: 85%+ (dados reais)
- Query consistency: 90%+ (performance tracking)
- Qualification rate: 10%+ (qualidade real)

### **Validation Checklist**

- [ ] Nenhum score pode ter fallback > 20% do total
- [ ] Métricas indisponíveis devem ser None, não 0 ou estimativa
- [ ] Logs devem mostrar source de cada ponto do score
- [ ] Qualification rate deve ser sustentável com volume

---

## ⚠️ MIGRATION PLAN

### **Backward Compatibility**

1. **Manter interface atual** do ActionableSMBLead
2. **Adicionar campo confidence** em cada métrica
3. **Logs detalhados** sobre source de dados
4. **Gradual rollout** - começar com 1 vertical

### **Risk Mitigation**

1. **Backup do sistema atual** antes de mudanças
2. **A/B testing** - rodar old vs new em paralelo
3. **Monitoring** de qualification rate durante rollout
4. **Rollback plan** se performance degradar

---

## 💡 INSIGHTS PARA IMPLEMENTAÇÃO

1. **Começar com professional_services_volume** - tem melhor consistência de dados
2. **Implementar domain resolution primeiro** - impacto mais alto
3. **Cache agressivo** para PageSpeed API - evitar rate limits
4. **Logging detalhado** durante migration para identificar issues
5. **Focus em Miami inicialmente** - geografia com melhor performance
