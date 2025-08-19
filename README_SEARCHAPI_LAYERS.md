# ARCO SearchAPI - Sistema de 3 Camadas para Geração de Leads

## Visão Geral

Sistema completo para descoberta e qualificação de prospects usando Google Ads Transparency Center via SearchAPI. Focado nos nichos verticais da ARCO (Dental/Ortho, Estética/Medspa, Real Estate) com perfil firmográfico específico: SMBs com ticket alto, LTV longo, presença ativa em Google Ads e landing pages com oportunidades de CRO.

## Arquitetura das 3 Camadas

### Layer 1: Seed Generation (`searchapi_layer1_seed_generation.py`)
**Engine:** `google_ads_transparency_center_advertiser_search`

**Função:** Gerar "sementes" de anunciantes por keyword/vertical/geo
- Busca geral por termos de high-intent por vertical
- Mapeia densidade de criativos e recência
- Output: listas de `advertiser_ids` e `domains` para Layer 2

**Verticais e Keywords:**
```python
{
    "dental_ortho": ["invisalign", "dental implants", "veneers"],
    "estética_medspa": ["botox", "laser hair removal", "dermal filler"],
    "real_estate": ["property management", "real estate agent"],
    "home_services": ["solar install", "roof replacement"]
}
```

**Regiões Prioritárias:** IE, GB, MT (Europa anglófona - prioridade 1), AU, NZ (backup)

### Layer 2: Advertiser Consolidation (`searchapi_layer2_advertiser_consolidation.py`)
**Engine:** `google_ads_transparency_center`

**Função:** Consolidar por domínio, filtrar atividade recente e qualificar prospects
- Deduplicação por domínio
- Filtros: 3-80 ads, atividade ≤ 30 dias
- Score de qualificação (0-100 pontos)
- Remove marketplaces/franquias centralizadas

**Critérios de Qualificação:**
- **Activity Score (30pts):** Volume de anúncios no sweet spot
- **Volume Score (25pts):** 3-80 ads (evita muito pequenos e muito grandes)
- **Recency Score (25pts):** Atividade nos últimos 30 dias
- **Diversity Score (20pts):** Variedade de platforms/formatos

### Layer 3: Ad Details Analysis (`searchapi_layer3_ad_details_analysis.py`)
**Engine:** `google_ads_transparency_center_ad_details`

**Função:** Análise detalhada de criativos + landing pages + score ARCO final
- Extrai payload completo dos anúncios (headlines, descriptions, final_url)
- Análise de CRO dos criativos (CTAs, urgência, trust signals)
- Cruza com análise técnica da landing page
- Score ARCO final (0-100): Atividade (30%) + Técnico (40%) + CRO (30%)

## Score ARCO Final (0-100 pontos)

### Componentes:
1. **Ad Activity (30 pontos)** - Do Layer 2
2. **Technical (40 pontos)** - Core Web Vitals + stack analysis
3. **CRO Signals (30 pontos)** - Coerência anúncio→LP + elementos de conversão

### Tiers de Qualificação:
- **≥ 70:** Premium (outreach imediato)
- **50-69:** Qualified (outreach programado)
- **30-49:** Potential (nutrição)
- **< 30:** Rejected

## Instalação e Configuração

### 1. Instalar Dependências
```bash
pip install requests python-dotenv
```

### 2. Configurar API Key
```bash
# .env file
SEARCHAPI_KEY=your_serpapi_key_here
```

### 3. Atualizar Configuração
```json
// config/discovery_config.json
{
  "searchapi_config": {
    "api_key": "${SEARCHAPI_KEY}",
    "qualification_thresholds": {
      "min_ads_threshold": 3,
      "max_ads_threshold": 80,
      "recency_days": 30,
      "min_arco_score": 50
    }
  }
}
```

## Como Usar

### Teste Europa Real Estate
```bash
python test_searchapi_layers.py --test europa
```

### Pipeline Europa Completo
```python
from src.engines.searchapi_master_orchestrator import ARCOSearchAPIMasterOrchestrator

orchestrator = ARCOSearchAPIMasterOrchestrator(api_key="sua_chave")

# Pipeline focado em Europa
europa_results = orchestrator.run_europa_real_estate_focus()
print(f"Europa: {len(europa_results['final_outreach_data'])} prospects")
```

### Pipeline Completo
```python
from src.engines.searchapi_master_orchestrator import ARCOSearchAPIMasterOrchestrator

# Inicializar
orchestrator = ARCOSearchAPIMasterOrchestrator(
    api_key="your_key",
    output_dir="data/results"
)

# Executar pipeline completo
results = orchestrator.run_complete_pipeline(
    verticals=["dental_ortho", "estética_medspa"],
    regions=["AU", "NZ"]
)

# Dados prontos para outreach
outreach_data = results["final_outreach_data"]
print(f"{len(outreach_data)} prospects ready for outreach")
```

### Uso Individual das Camadas

#### Layer 1 - Seed Generation
```python
from src.engines.searchapi_layer1_seed_generation import SearchAPILayer1SeedGeneration

layer1 = SearchAPILayer1SeedGeneration(api_key)

# Busca por keyword específica
seeds = layer1.search_advertisers_by_keyword(
    keyword="invisalign",
    region="AU",
    num_advertisers=50
)

# Geração por vertical completa
vertical_seeds = layer1.generate_seeds_by_vertical(
    vertical="dental_ortho",
    regions=["AU", "NZ"],
    max_keywords=4
)
```

#### Layer 2 - Advertiser Consolidation
```python
from src.engines.searchapi_layer2_advertiser_consolidation import SearchAPILayer2AdvertiserConsolidation

layer2 = SearchAPILayer2AdvertiserConsolidation(api_key)

# Lista de anunciantes do Layer 1
advertisers = [
    {"advertiser_id": "AR123456", "domain": "dental-clinic.com.au"},
    {"domain": "medspa-example.com.au"}
]

# Consolidar e qualificar
results = layer2.consolidate_advertisers_batch(
    advertiser_list=advertisers,
    region="AU"
)

qualified = results["qualified_advertisers"]
```

#### Layer 3 - Ad Details Analysis
```python
from src.engines.searchapi_layer3_ad_details_analysis import SearchAPILayer3AdDetailsAnalysis

layer3 = SearchAPILayer3AdDetailsAnalysis(api_key)

# Anunciantes qualificados do Layer 2
qualified_list = [
    {
        "advertiser_id": "AR123456",
        "creative_ids": ["CR111", "CR222"],
        "qualification_score": 75
    }
]

# Análise detalhada
final_results = layer3.process_qualified_advertisers(qualified_list)

# Dados de outreach
outreach_ready = layer3.generate_outreach_data(final_results["outreach_ready"])
```

## Estrutura de Output

### Dados de Outreach Finais
```json
{
  "advertiser_id": "AR123456789",
  "domain": "example-dental.com.au",
  "arco_score": 78,
  "priority_level": "high",
  "pain_points": [
    "Add stronger call-to-action",
    "Optimize Core Web Vitals for mobile"
  ],
  "headlines_used": [
    "Get Your Perfect Smile Today",
    "Free Invisalign Consultation"
  ],
  "landing_page": "https://example-dental.com.au/invisalign",
  "outreach_angle": "Landing page conversion optimization",
  "estimated_opportunity": "High - Active advertiser with significant spend"
}
```

### Métricas do Pipeline
```json
{
  "funnel_metrics": {
    "initial_advertisers": 145,
    "qualified_after_layer2": 23,
    "outreach_ready": 8,
    "conversion_rate": 5.5
  },
  "api_efficiency": {
    "total_calls": 67,
    "calls_per_final_prospect": 8.4,
    "cost_estimate_usd": 3.35
  }
}
```

## Controle de Custos

### Rate Limiting
- **Layer 1:** 0.5s entre calls
- **Layer 2:** 0.8s entre calls
- **Layer 3:** 1.0s entre calls

### Limites Conservadores
- Máximo 50 advertisers por batch (Layer 2)
- Máximo 2-3 criativos por advertiser (Layer 3)
- Teste rápido: 1 vertical, 1 região, 2 keywords

### Estimativa de Custos
- **Teste rápido:** ~10-15 calls (~$0.50-0.75)
- **Pipeline vertical completo:** ~50-80 calls (~$2.50-4.00)
- **Pipeline full (3 verticais):** ~150-250 calls (~$7.50-12.50)

## ROI e Casos de Uso

### Caso Dental Típico
- **Input:** 150 leads/mês, conversão 7%
- **Output pós-ARCO:** +20-40% conversão LP
- **Resultado:** 3-4 procedimentos extras/mês
- **Ticket:** Implantes 3-8k AUD, Invisalign 5-8k AUD
- **ROI:** Sprint ARCO se paga facilmente

### Sinais de Oportunidade ARCO
1. **Anúncios ativos** nos últimos 30 dias
2. **Volume útil** (3-80 ads, não muito pequeno nem muito grande)
3. **Landing page lenta** (CrUX p75 mobile ruim)
4. **CRO básico faltando** (CTA fraco, sem prova social)
5. **Stack improvável** (WordPress+Elementor desregulado)

## Arquivos do Sistema

```
src/engines/
├── searchapi_layer1_seed_generation.py       # Layer 1: Seed Generation
├── searchapi_layer2_advertiser_consolidation.py  # Layer 2: Consolidation
├── searchapi_layer3_ad_details_analysis.py   # Layer 3: Details Analysis
└── searchapi_master_orchestrator.py          # Master Orchestrator

config/
└── discovery_config.json                     # Configurações SearchAPI

test_searchapi_layers.py                      # Script de teste
```

## Integração com Sistema Existente

O sistema SearchAPI complementa outros engines da ARCO:
- **BigQuery Discovery:** Para análise técnica profunda
- **Meta Ads Scraper:** Para diversificar fontes de dados
- **CrUX/HTTP Archive:** Para métricas técnicas reais

## Troubleshooting

### Problemas Comuns

1. **"Import could not be resolved"**
   ```bash
   # Execute do diretório raiz do projeto
   cd arco-find
   python test_searchapi_layers.py --test quick
   ```

2. **"SearchAPI key not found"**
   ```bash
   export SEARCHAPI_KEY=your_actual_key
   # ou adicione no .env file
   ```

3. **Rate limiting errors**
   - Aumentar delays no config
   - Reduzir batch sizes
   - Usar modo teste primeiro

### Logs
```bash
# Logs automáticos em:
logs/searchapi_test_YYYYMMDD_HHMMSS.log

# Resultados em:
data/searchapi_results/
```

## Roadmap

### Próximas Integrações
- [ ] CrUX API para Core Web Vitals reais
- [ ] HTTP Archive para stack detection
- [ ] PageSpeed Insights para mobile-friendly
- [ ] Outreach automation (email templates)
- [ ] CRM integration (HubSpot/Pipedrive)

### Melhorias
- [ ] ML para score de qualificação
- [ ] Análise de competidores
- [ ] Tracking de campanhas de outreach
- [ ] Dashboard de resultados
