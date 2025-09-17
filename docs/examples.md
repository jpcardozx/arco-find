# Exemplos de Uso do ARCO

Este documento contém exemplos práticos de como utilizar o sistema ARCO para diferentes cenários de aquisição de clientes e otimização de receita.

## Exemplo 1: Pipeline Padrão com Arquivo de Entrada

Este exemplo demonstra como executar o pipeline padrão com um arquivo de entrada contendo uma lista de domínios.

```bash
python main.py --pipeline standard --input data/sample_domains.txt --output output/results.json
```

### Arquivo de Entrada

O arquivo de entrada deve conter um domínio por linha:

```
example.com
company.org
startup.io
```

### Saída

O resultado será salvo em `output/results.json` com o seguinte formato:

```json
{
  "results": [
    {
      "domain": "example.com",
      "company_name": "Example Inc.",
      "technologies": ["React", "Node.js", "AWS"],
      "contacts": [
        { "name": "John Doe", "position": "CTO", "email": "john@example.com" }
      ],
      "revenue_estimate": "$5M-10M",
      "employee_count": "50-100",
      "score": 85
    }
    // ... outros resultados
  ],
  "stats": {
    "processed": 3,
    "successful": 3,
    "failed": 0,
    "processing_time": "00:01:23"
  }
}
```

## Exemplo 2: Pipeline Avançado com Consulta de Busca

Este exemplo demonstra como executar o pipeline avançado com uma consulta de busca para descobrir novos prospectos.

```bash
python main.py --pipeline advanced --input "fintech startups in Brazil" --limit 50 --output output/fintech_brazil.json
```

### Parâmetros

- `--input`: Uma consulta de busca para encontrar empresas
- `--limit`: Número máximo de resultados a serem retornados (padrão: 20)
- `--output`: Arquivo de saída para os resultados

### Saída

O resultado incluirá empresas descobertas com base na consulta, enriquecidas com dados adicionais:

```json
{
  "results": [
    {
      "domain": "fintechbr.com.br",
      "company_name": "FinTech BR",
      "technologies": ["Java", "Spring", "GCP"],
      "contacts": [
        {
          "name": "Maria Silva",
          "position": "CEO",
          "email": "maria@fintechbr.com.br"
        }
      ],
      "revenue_estimate": "$1M-5M",
      "employee_count": "10-50",
      "score": 92,
      "discovery_source": "search",
      "discovery_query": "fintech startups in Brazil"
    }
    // ... outros resultados
  ],
  "stats": {
    "processed": 50,
    "successful": 48,
    "failed": 2,
    "processing_time": "00:03:45"
  }
}
```

## Exemplo 3: Configuração Personalizada

Este exemplo demonstra como usar um arquivo de configuração personalizado.

```bash
python main.py --pipeline standard --config config/custom_settings.yml --input data/enterprise_domains.txt
```

### Arquivo de Configuração

O arquivo de configuração personalizado (`config/custom_settings.yml`) pode conter:

```yaml
# Configurações de API
api:
  google_search:
    api_key: ${GOOGLE_API_KEY}
    cx: ${GOOGLE_CX}
  apollo:
    api_key: ${APOLLO_API_KEY}
  clearbit:
    api_key: ${CLEARBIT_API_KEY}

# Configurações de cache
cache:
  enabled: true
  ttl: 86400 # 24 horas em segundos
  max_size: 1000

# Configurações de logging
logging:
  level: INFO
  file: true
  console: true
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Configurações de pipeline
pipeline:
  standard:
    enrichment_level: full
    max_contacts_per_company: 5
  advanced:
    discovery_depth: 2
    min_score: 60
```

## Exemplo 4: Uso Programático

Este exemplo demonstra como usar o ARCO programaticamente em seu próprio código Python.

```python
import asyncio
from arco.pipelines.standard_pipeline import StandardPipeline
from arco.pipelines.advanced_pipeline import AdvancedPipeline

async def run_standard_pipeline():
    # Inicializar o pipeline padrão
    pipeline = StandardPipeline(config_path="config/production.yml")

    # Executar para uma lista de domínios
    domains = ["example.com", "company.org", "startup.io"]
    results = await pipeline.run(domains)

    # Processar resultados
    for result in results:
        print(f"Domain: {result['domain']}")
        print(f"Company: {result['company_name']}")
        print(f"Score: {result['score']}")
        print("---")

    return results

async def run_advanced_pipeline():
    # Inicializar o pipeline avançado
    pipeline = AdvancedPipeline(config_path="config/production.yml")

    # Executar com uma consulta de busca
    query = "saas companies in healthcare"
    results = await pipeline.run(query, limit=30)

    # Salvar resultados
    pipeline.save_results(results, "output/healthcare_saas.json")

    return results

# Executar os pipelines
if __name__ == "__main__":
    # Executar o pipeline padrão
    standard_results = asyncio.run(run_standard_pipeline())

    # Executar o pipeline avançado
    advanced_results = asyncio.run(run_advanced_pipeline())
```

## Exemplo 5: Integração com Webhook

Este exemplo demonstra como configurar o ARCO para enviar resultados para um webhook.

```bash
python main.py --pipeline advanced --input "cybersecurity startups" --webhook https://api.yourcompany.com/webhooks/arco
```

### Configuração do Webhook

No arquivo de configuração, você pode definir detalhes adicionais do webhook:

```yaml
webhook:
  enabled: true
  url: https://d20097e520ec.ngrok-free.app/webhook
  method: POST
  headers:
    Authorization: Bearer ${WEBHOOK_TOKEN}
    Content-Type: application/json
  batch_size: 10 # Enviar resultados em lotes de 10
  retry:
    max_attempts: 3
    backoff_factor: 2
```

### Formato do Payload do Webhook

```json
{
  "timestamp": "2025-07-17T13:45:30Z",
  "batch_id": "batch_12345",
  "query": "cybersecurity startups",
  "results": [
    {
      "domain": "securetech.io",
      "company_name": "SecureTech",
      "technologies": ["Python", "Django", "AWS"],
      "contacts": [
        {
          "name": "Alex Johnson",
          "position": "CISO",
          "email": "alex@securetech.io"
        }
      ],
      "score": 88
    }
    // ... outros resultados no lote
  ]
}
```
