# 🔥 REFATORAÇÃO CRÍTICA - ENGINE SMB COM SINAIS ACIONÁVEIS

## ❌ FRAGILIDADES IDENTIFICADAS NO CÓDIGO ANTERIOR:

### **1. SEED INVÁLIDO**

- ❌ `local{pattern}services.com` não existe
- ❌ Busca retorna vazio e vicia pipeline
- ✅ **SOLUÇÃO**: Use `q=` por intenção+geo ("emergency dentist tampa")

### **2. CAMPOS FANTASMAS**

- ❌ `total_days_shown`, `target_domain`, `impressions` raramente existem
- ❌ Score dependente de dados ausentes
- ✅ **SOLUÇÃO**: Usar apenas campos que SEMPRE aparecem

### **3. CLASSIFICAÇÃO SMB FRACA**

- ❌ Heurística por "LLC/Inc." elimina SMBs legítimos
- ❌ Faltam proxies melhores
- ✅ **SOLUÇÃO**: Volume/recência de criativos, densidade geo, mix formatos

### **4. EXECUÇÃO/PERFORMANCE INEXATA**

- ❌ `load_time_ms` por GET não mede LCP/INP/TTFB
- ❌ "has_issues" com falso-positivo
- ✅ **SOLUÇÃO**: PSI/CrUX para métricas reais

### **5. OPORTUNIDADE/WASTE ESTÁTICO**

- ❌ "$500-2k/mês" sem cálculo
- ❌ Não sustentável no outreach
- ✅ **SOLUÇÃO**: Cálculo baseado em sinais reais

## 🎯 SINAIS ACIONÁVEIS EXTRAÍVEIS DO ADS LIBRARY

### **CAMPOS TÍPICOS DISPONÍVEIS:**

```json
{
  "advertiser": { "id": "...", "name": "..." },
  "ad_creatives": [
    {
      "text": "...",
      "headline": "...",
      "last_seen": "...",
      "first_seen": "...",
      "media_type": "text|image|video",
      "region": "...",
      "country": "..."
    }
  ]
}
```

## 📊 SCORING REAL BASEADO EM DADOS DISPONÍVEIS

### **S1. INSTABILIDADE (Thrash Index)**

```python
thrash = (#criativos últimos 30 dias) / (mediana dias ativos por criativo + 1)
# thrash ≥ 0.5 = forte instabilidade (testagem caótica) = +12 pontos
```

### **S2. DURAÇÃO CURTA**

```python
duration = last_seen - first_seen por criativo
# mediana < 14 dias = "desliga rápido" = +10 pontos
```

### **S3. COERÊNCIA DE OFERTA**

```python
# Clustering n-grama em headline/text
# Baixa similaridade média (<0.55) = narrativa inconsistente = +10 pontos
```

### **S4. GENERICIDADE DE CÓPIA**

```python
genericity_score = % stop-phrases vs termos específicos
# "best in town", "quality service", "shop now"
# >30% = copy fraca = +8 pontos
```

### **S5. GEO-ADERÊNCIA (Local Services)**

```python
geo_tokens = city/neighborhood presentes no texto
# Ausência sistemática = desperdício geográfico = +8 pontos
```

### **S6. FORMATO E INVESTIMENTO**

```python
# media_type majoritariamente text/static sem variação
# = baixo investimento criativo = +6 pontos
```

### **S7. RECÊNCIA**

```python
# Sem criativos últimos 30 dias + presença passado recente
# = liga/desliga sem continuidade = +6 pontos
```

### **S8. MESSAGE-MATCH ADS→LP**

```python
# Termos-chave criativos vs <title>/<h1>/CTA da LP
# jaccard <0.6 = +15 pontos
```

### **S9. LANDING PAGE QUALITY**

```python
# Landing = home page = +12 pontos
# PSI/CrUX: LCP>3.2s ou INP>300ms = +13 pontos
```

## 🎯 SCORE REFATORADO (GATE ARCO: ≥75)

| Bloco             | Regra                        | Pontos |
| ----------------- | ---------------------------- | ------ |
| **Thrash**        | thrash ≥ 0.5                 | +12    |
| **Duração**       | mediana <14d                 | +10    |
| **Coerência**     | similaridade <0.55           | +10    |
| **Genericidade**  | genericity >30%              | +8     |
| **Geo-aderência** | sem geo_tokens               | +8     |
| **Recência**      | inativo <30d após ativo <90d | +6     |
| **Formato**       | media_type pobre/repetitivo  | +6     |
| **Message-match** | jaccard <0.6 (Ads↔H1/CTA)    | +15    |
| **LP Quality**    | landing = home               | +12    |
| **PSI/CrUX**      | LCP>3.2s ou INP>300ms        | +13    |

**TOTAL MÁXIMO: 100 pontos**
**GATE ARCO: ≥75 pontos = Lead qualificado**

## 🔧 IMPLEMENTAÇÃO REFATORADA

### **1. DISCOVERY POR INTENÇÃO+GEO**

```python
STRATEGIC_QUERIES = [
    "emergency dentist tampa",
    "urgent care miami",
    "plumber repair phoenix",
    "attorney consultation dallas",
    "marketing agency austin"
]
```

### **2. ANÁLISE DE INSTABILIDADE**

```python
def calculate_thrash_index(creatives: List[Dict]) -> float:
    """Calcula instabilidade baseado em dados reais"""
    last_30_days = datetime.now() - timedelta(days=30)

    recent_creatives = [
        c for c in creatives
        if parse_date(c.get('last_seen')) >= last_30_days
    ]

    median_duration = calculate_median_duration(creatives)

    return len(recent_creatives) / (median_duration + 1)
```

### **3. ANÁLISE DE COERÊNCIA**

```python
def analyze_message_coherence(creatives: List[Dict]) -> float:
    """Analisa coerência narrativa dos ads"""
    texts = [c.get('text', '') + ' ' + c.get('headline', '') for c in creatives]

    # N-gram similarity matrix
    similarities = []
    for i in range(len(texts)):
        for j in range(i+1, len(texts)):
            sim = calculate_ngram_similarity(texts[i], texts[j])
            similarities.append(sim)

    return np.mean(similarities) if similarities else 0
```

### **4. ANÁLISE DE GENERICIDADE**

```python
def calculate_genericity_score(text: str) -> float:
    """Calcula % de frases genéricas vs específicas"""

    generic_phrases = [
        "best in town", "quality service", "shop now",
        "welcome", "contact us", "learn more", "get started"
    ]

    specific_indicators = [
        # Será detectado por domínio/contexto específico
    ]

    total_words = len(text.split())
    generic_words = sum(len(phrase.split()) for phrase in generic_phrases if phrase in text.lower())

    return (generic_words / total_words) * 100 if total_words > 0 else 0
```

### **5. PSI/CrUX REAL**

```python
async def get_real_performance_metrics(url: str) -> Dict:
    """Busca métricas reais via PageSpeed Insights API"""

    psi_url = "https://www.googleapis.com/pagespeed/api/v5/runPagespeed"
    params = {
        'url': url,
        'key': os.getenv('GOOGLE_PAGESPEED_API_KEY'),
        'category': 'performance',
        'strategy': 'mobile'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(psi_url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                metrics = data['lighthouseResult']['audits']

                return {
                    'lcp': metrics['largest-contentful-paint']['numericValue'],
                    'inp': metrics.get('interaction-to-next-paint', {}).get('numericValue', 0),
                    'cls': metrics['cumulative-layout-shift']['numericValue'],
                    'ttfb': metrics['server-response-time']['numericValue']
                }
```

## 🎯 QUERIES ESTRATÉGICAS REFINADAS

### **LOCAL SERVICES:**

```python
'local_services_queries': [
    "emergency dentist {city}",
    "urgent care {city}",
    "plumber repair {city}",
    "attorney consultation {city}",
    "accountant tax {city}"
]
```

### **SMALL ECOMMERCE:**

```python
'ecommerce_queries': [
    "boutique clothing store {city}",
    "local jewelry shop {city}",
    "pet supplies {city}",
    "fitness equipment {city}"
]
```

### **PROFESSIONAL SERVICES:**

```python
'professional_queries': [
    "marketing agency {city}",
    "web design {city}",
    "consulting services {city}",
    "accounting firm {city}"
]
```

## 💡 RESULTADO ESPERADO

**LEADS QUALIFICADOS COM:**

- ✅ **Sinais reais de má execução** (thrash, duração, coerência)
- ✅ **Problemas mensuráveis** (PSI/CrUX, message-match)
- ✅ **Oportunidades calculáveis** (baseado em sinais específicos)
- ✅ **Outreach acionável** (problemas específicos identificados)

**SEM DEPENDÊNCIA DE:**

- ❌ Campos fantasmas (impressions, targeting)
- ❌ Heurísticas fracas (LLC/Inc)
- ❌ Performance fake (GET timing)
- ❌ Estimativas estáticas ($500-2k)

**FOCO TOTAL EM DADOS DISPONÍVEIS E ACIONÁVEIS.**
