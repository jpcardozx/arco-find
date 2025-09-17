# 🔍 Google Cloud Console Services Analysis for ARCO

## Serviços Google Cloud Úteis para Prospecção

### ✅ **1. PageSpeed Insights API** (Implementado)

- **URL**: `https://www.googleapis.com/pagespeedonline/v5/runPagespeed`
- **Limites**: 25,000 queries/day (grátis), depois $5/1000 queries
- **Dados**: LCP, FCP, CLS, JS/CSS bytes, performance score
- **Revenue Impact**: 1s de LCP delay = 7% perda conversão

### ⚠️ **2. Custom Search API** (Implementado agora)

- **URL**: `https://www.googleapis.com/customsearch/v1`
- **Limites**: 100 queries/day (grátis), depois $5/1000 queries
- **Uso**: Confirmar footprints SaaS via `site:domain.com typeform`
- **Revenue Impact**: Confirma vazamentos SaaS detectados

### 🔧 **3. Safe Browsing API** (Útil para filtrar)

- **URL**: `https://safebrowsing.googleapis.com/v4/threatMatches:find`
- **Limites**: 10,000 queries/day
- **Uso**: Verificar se domain é seguro/confiável
- **Revenue Impact**: Filtra prospects problemáticos

### 📍 **4. Geocoding API** (Útil para segmentação)

- **URL**: `https://maps.googleapis.com/maps/api/geocode/json`
- **Limites**: $200 credit/month free
- **Uso**: Validar localização da empresa
- **Revenue Impact**: Targeting geográfico

### 💭 **5. Natural Language API** (Opcional)

- **URL**: `https://language.googleapis.com/v1/documents:analyzeSentiment`
- **Limites**: 5,000 units/month free
- **Uso**: Analisar sentiment de reviews/content
- **Revenue Impact**: Qualificação por sentiment score

---

## 🚨 Fragilidades Identificadas e Corrigidas

### ❌ **FRAGILIDADE 1: PageSpeed API Error Handling**

**Problema**: Falhas não documentadas, rate limiting não respeitado

**Correção**:
