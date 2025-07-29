# 🚀 ARCO Pipeline Optimized - Isolated Execution

## 📋 Overview

Pipeline isolado e otimizado para descoberta e qualificação de **5 leads SMB dentro do ICP** com P0 signals detection e Meta Ads intelligence.

## 🎯 Quick Start

### Execução Simples

```bash
cd pipeline_optimized
python run_pipeline.py
```

### Execução Direta do Engine

```bash
cd pipeline_optimized
python core/icp_qualification_engine.py
```

## 📁 Estrutura

```
pipeline_optimized/
├── 🚀 run_pipeline.py              # Script principal executável
├── 📋 README.md                    # Esta documentação
├── ⚙️ requirements.txt             # Dependências isoladas
├── 🔑 .env                         # Configuração de ambiente
│
├── core/                           # Engine principal
│   └── icp_qualification_engine.py # Engine de qualificação ICP
│
├── config/                         # Configurações
│   └── api_keys.py                # Configuração de APIs
│
└── exports/                        # Resultados exportados
    └── icp_qualified_leads_*.json  # Leads qualificados
```

## 🔧 Configuração

### 1. Dependências

```bash
pip install -r requirements.txt
```

### 2. APIs (Já Configuradas)

- ✅ **SearchAPI**: `3sgTQQBwGfmtBR1WBW61MgnU`
- ✅ **PageSpeed API**: `AIzaSyDNo6ycjKNYfDBmbFbOLI7kk-A-teppPaE`

### 3. Validação

```bash
python config/api_keys.py
```

## 🎯 Funcionalidades

### ✅ ICP Qualification Engine

- **Target Industries**: Legal, Healthcare, Real Estate, Home Services
- **Qualification Threshold**: 0.7+ ICP score
- **P0 Signals Detection**: Performance, LCP, CLS issues
- **SMB Focus**: Local businesses with optimization needs

### ✅ P0 Signals Detection

- **Performance Score** < 60%
- **LCP (Largest Contentful Paint)** > 2.5s
- **CLS (Cumulative Layout Shift)** > 0.1
- **Waste Potential** calculation

### ✅ Meta Ads Intelligence

- **Industry Benchmarks** for spend estimation
- **Competition Analysis** by vertical
- **Waste Calculation** based on performance
- **Approach Vector** determination

### ✅ Export System

- **JSON Format** with complete lead profiles
- **Summary Statistics** and metrics
- **Timestamp Tracking** for all exports

## 📊 Output Example

### Qualified Lead Profile

```json
{
  "company_name": "Dallas Personal Injury Law",
  "domain": "dallasinjurylaw.com",
  "industry": "legal",
  "location": "Dallas",
  "icp_score": 0.85,
  "urgency_score": 0.9,
  "estimated_waste": 2100,
  "p0_signals": ["P0_PERFORMANCE", "P0_LCP"],
  "approach_vector": "PERFORMANCE_WASTE_COMBO",
  "qualification_reason": "High-value legal vertical | Local business focus | Multiple P0 signals detected"
}
```

### Summary Statistics

```json
{
  "total_leads": 5,
  "avg_icp_score": 0.82,
  "avg_urgency_score": 0.76,
  "total_estimated_waste": 8950,
  "industries": ["legal", "healthcare", "home_services"],
  "approach_vectors": ["PERFORMANCE_WASTE_COMBO", "AD_WASTE_FOCUS"]
}
```

## 🎯 Target Metrics

### Per Execution

- **5 leads qualificados** dentro do ICP
- **ICP Score** ≥ 0.7
- **Total Waste** $5,000-$15,000/mês detectado
- **P0 Signals** 80%+ dos leads

### Performance

- **Execution Time**: 30-60 segundos
- **API Calls**: ~20 SearchAPI + ~10 PageSpeed
- **Success Rate**: 95%+ lead qualification

## 🚨 Troubleshooting

### Dependencies Issues

```bash
# Install all dependencies
pip install aiohttp requests python-dotenv

# Or use requirements file
pip install -r requirements.txt
```

### API Configuration

```bash
# Check API status
python config/api_keys.py

# Expected output:
# ✅ SEARCHAPI: Configurado
# ✅ PAGESPEED: Configurado
```

### No Leads Found

- **Timeout Issues**: Check internet connection
- **API Rate Limits**: Wait 1-2 minutes and retry
- **ICP Threshold**: Leads might not meet 0.7+ score requirement

### Permission Errors

```bash
# On Windows
python run_pipeline.py

# On Unix/Mac
chmod +x run_pipeline.py
./run_pipeline.py
```

## 📈 Optimization Notes

### ICP Industries (High-Value)

1. **Legal**: High CPC ($8.50 avg), high waste potential
2. **Healthcare**: Compliance needs, optimization opportunities
3. **Real Estate**: Competitive market, performance critical
4. **Home Services**: Local focus, conversion optimization

### P0 Signal Priorities

1. **Performance < 60%**: Immediate optimization needed
2. **LCP > 2.5s**: User experience impact
3. **High Spend + Poor Performance**: Maximum waste potential

### Approach Vectors

- **PERFORMANCE_WASTE_COMBO**: High-value, urgent prospects
- **AD_WASTE_FOCUS**: Budget optimization focus
- **PERFORMANCE_OPTIMIZATION**: Technical optimization focus

## 🎉 Success Indicators

After successful execution, you should see:

```
🎯 RESULTADOS DA QUALIFICAÇÃO
==================================================
⏱️ Tempo de execução: 45.2s
🎯 Leads qualificados: 5/5

💾 Arquivo exportado: exports/icp_qualified_leads_20250728_194523.json

🎯 RESUMO EXECUTIVO:
  💰 Waste total estimado: $8,950/mês
  ⚡ Urgência média: 0.8
  🏢 Indústrias: legal, healthcare, home_services

📋 LEADS QUALIFICADOS:
  1. Dallas Personal Injury Law
     • Indústria: legal
     • Score ICP: 0.85
     • Waste estimado: $2,100/mês
     • P0 Signals: P0_PERFORMANCE, P0_LCP
     • Approach: PERFORMANCE_WASTE_COMBO

🎉 Qualificação ICP concluída com sucesso!
```

## 🔄 Regular Usage

### Daily Discovery

```bash
python run_pipeline.py
```

### Check Results

```bash
ls exports/
# View latest results
```

### Monitor Performance

```bash
# Check API status before running
python config/api_keys.py
```

---

🎯 **Ready to execute! Run `python run_pipeline.py` for 5 qualified leads.**
