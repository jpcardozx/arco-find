# Arco-Find

Arco-Find é uma plataforma de inteligência operacional e geração de leads projetada para empresas em crescimento (15-75 funcionários) que buscam otimizar custos de SaaS, melhorar a performance do site e eliminar ineficiências operacionais. Nós ajudamos a identificar gastos desnecessários, gargalos de desempenho e oportunidades de automação, transformando dados em economia e produtividade.

## 🎯 Motor Principal

O sistema está centralizado na pasta **`src/`** com integração real de APIs:

- **SearchAPI** - Meta Ads Library para dados reais de anúncios
- **PageSpeed API** - Performance real de websites
- **BigQuery** - Benchmarks e análises avançadas

## 🚀 Como Usar

### Execução Rápida (Demonstração)

```bash
python main.py --demo
```

### Análise Personalizada

```bash
python main.py --company "Empresa XYZ" --website "https://empresa.com" --saas-spend 5000
```

### Com Dados de Anúncios (Opcional)

```bash
python main.py --company "Empresa XYZ" --website "https://empresa.com" --saas-spend 5000 \
               --google-ads-customer-id "123456789" \
               --meta-ad-account-id "act_123456"
```

## 📁 Estrutura do Projeto

```
src/
├── core/
│   ├── arco_engine.py          # Motor principal (892 linhas)
│   └── ...
├── connectors/
│   ├── searchapi_connector.py   # SearchAPI Meta Ads
│   ├── google_pagespeed_api.py  # PageSpeed API
│   └── ...
├── pipeline/
│   └── run.py                   # Orquestrador principal
└── ...

main.py                         # Ponto de entrada principal
```

## ⚙️ Configuração

1. **Instalar dependências:**

```bash
pip install -r requirements.txt
```

2. **Configurar APIs (arquivo .env):**

```env
SEARCHAPI_KEY=sua_chave_searchapi
PAGESPEED_KEY=sua_chave_pagespeed
GOOGLE_CLOUD_PROJECT=prospection-463116
```

3. **Executar:**

```bash
python main.py --demo
```

## 🔧 APIs Integradas

- ✅ **SearchAPI** - Meta Ads Library (dados reais de anúncios)
- ✅ **PageSpeed API** - Performance real de websites
- ✅ **BigQuery** - Benchmarks e análises
- 🔄 **Google Ads API** - Em desenvolvimento
- 🔄 **LinkedIn API** - Em desenvolvimento

## License

This project is licensed under the [MIT License](LICENSE).
