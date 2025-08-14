# ARCO Pipeline Completo 2025

Pipeline de aquisição ponta a ponta baseado nos funis aprovados: **Auditoria Express** e **Teardown 60s**.

## 🎯 Objetivos Estratégicos

- **Revenue Target**: $2,800/mês ($1,312 Auditoria + $1,500 Teardown)
- **Lead Volume**: 600 prospects contactados/mês
- **Qualification Rate**: 25% passam pelos gates
- **Close Rate**: 20-30% dependendo do funil

## 📊 Funis Aprovados

### Funil A: Auditoria Express 48h → Sprint 7 dias
- **Entrada**: $250 (100% abatível)
- **Upgrade**: $750 
- **Kill Rule**: Upgrade rate < 20% por 3 semanas
- **Economics**: 4.3x margem vs CAC (sustentável)

### Funil B: Teardown 60s → Agenda Imediata  
- **Entrada**: $0 (pré-valor)
- **Close**: $750
- **Kill Rule**: Response rate < 6% por 2 semanas
- **Economics**: CAC negativo (precisa otimização)

## 🛠️ Stack Tecnológico

### APIs e Ferramentas
- **Meta Ad Library API** - descoberta de anunciantes (FREE)
- **PageSpeed Insights API** - análise técnica (FREE)
- **OpenGraph Scraper** - enriquecimento landing pages (FREE)
- **Playwright** - automação browser para scraping
- **SQLite** - storage de intelligence local

### Estrutura do Projeto
```
arco-pipeline/
├── docs/                    # Documentação completa
├── src/
│   ├── discovery/          # Meta Ad Library scraping
│   ├── qualification/      # Gates e scoring
│   ├── enrichment/        # Landing page analysis
│   ├── outreach/          # Email automation
│   └── monitoring/        # Metrics e kill rules
├── data/
│   ├── prospects.db       # SQLite database
│   └── exports/           # CSVs para outreach
├── config/
│   ├── api_keys.py        # Configurações API
│   └── settings.py        # Parâmetros do pipeline
└── templates/             # Email templates por vertical
```

## 🔄 Pipeline Flow

### Phase 1: Discovery (Meta Ad Library)
1. **Search por vertical** usando terms específicos
2. **Extract advertiser data** (page_id, view_all_page_id)
3. **Scrape ads individuais** por advertiser
4. **Parse landing URLs** dos anúncios

### Phase 2: Qualification Gates
1. **Gate 1 - Ad Activity**: Anúncios ativos últimos 30d
2. **Gate 2 - Budget Indicators**: >3 criativos OU multi-região  
3. **Gate 3 - Technical Issues**: PageSpeed < 70 OU mobile problems
4. **Gate 4 - Decision Maker**: LinkedIn do proprietário identificado

### Phase 3: Enrichment & Scoring
1. **Landing page analysis** (speed, UX, tracking)
2. **Business intelligence** (LinkedIn, GMB)
3. **Opportunity scoring** (1-10 based on waste potential)
4. **Funnel assignment** (Auditoria vs Teardown)

### Phase 4: Outreach Execution
1. **Template selection** por vertical e funnel
2. **Personalization** com dados coletados
3. **Sequence automation** (D0, D1, D3, D7)
4. **Response tracking** e follow-up

### Phase 5: Monitoring & Optimization
1. **Kill rule monitoring** automático
2. **A/B testing** de templates
3. **Conversion tracking** por vertical
4. **ROI analysis** mensal

## 📋 Implementation Roadmap

### Week 1: Foundation
- [ ] Setup project structure
- [ ] Implement Meta Ad Library scraper
- [ ] Create SQLite schema
- [ ] Basic qualification gates

### Week 2: Testing & Validation  
- [ ] Test scraper com 50 prospects dental
- [ ] Validate qualification gates
- [ ] Create email templates
- [ ] Setup PageSpeed analysis

### Week 3: Automation & Scale
- [ ] Implement outreach sequences
- [ ] Add monitoring dashboard
- [ ] Create kill rule automation
- [ ] A/B test initial templates

### Week 4: Full Pipeline
- [ ] Scale to 500 prospects/week
- [ ] Optimize conversion rates
- [ ] Document learnings
- [ ] Plan next vertical expansion

## 🎯 Próximos Passos

1. **API Consultation**: Validar acesso Meta Ad Library API
2. **Terminal Setup**: Instalar dependências (playwright, aiohttp)
3. **Database Schema**: Criar estrutura SQLite
4. **First Scrape**: Testar discovery com vertical dental

---

*Este documento será atualizado conforme implementação progride.*