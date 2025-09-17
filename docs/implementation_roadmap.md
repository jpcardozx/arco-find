# Roadmap para Implementação da Versão Realista do Módulo /arco

## 1. Objetivo

Este documento descreve o plano de ação para evoluir o módulo `/arco` de sua implementação atual (simulação com dados estáticos) para um sistema de prospecção funcional e pronto para produção, que interage com APIs externas reais para descoberta e enriquecimento de dados.

A arquitetura existente, com separação de `engines` e `pipelines`, é um excelente ponto de partida e será mantida. O foco será substituir a lógica de simulação dentro do `DiscoveryEngine` por chamadas de API reais e robustas.

---

## 2. Fases do Projeto

### Fase 1: Fundamentos e Abstração de API

O objetivo desta fase é criar uma base sólida e desacoplada para interagir com serviços externos, facilitando a manutenção e os testes.

-   [ ] **2.1. Configuração Segura de APIs:**
    -   Validar que o `ConfigManager` e o `settings.py` carregam corretamente todas as chaves de API necessárias a partir do arquivo `.env`.
    -   Garantir que o `.env.template` liste todas as variáveis de ambiente necessárias para a operação real.

-   [ ] **2.2. Criação de Clientes de API Abstratos:**
    -   Criar um novo diretório: `arco/clients`.
    -   Dentro de `arco/clients`, desenvolver classes "clientes" dedicadas para cada serviço externo. Ex:
        -   `google_search_client.py`: Para interagir com a API de busca do Google.
        -   `crunchbase_client.py`: Para dados de financiamento.
        -   `hunter_client.py`: Para enriquecimento de contatos.
        -   `wappalyzer_client.py`: Para detecção de tecnologias.
    -   Cada cliente será responsável por:
        1.  Autenticação.
        2.  Construção de requests HTTP (`GET`, `POST`).
        3.  Tratamento de respostas (parsing de JSON).
        4.  Mapeamento dos dados da API para os modelos Pydantic do `arco`.

-   [ ] **2.3. Modelos de Dados com Pydantic:**
    -   Reforçar os modelos em `arco/models` (ex: `Prospect`, `Technology`, `Contact`) usando Pydantic para validação automática dos dados recebidos das APIs. Isso garante a integridade dos dados que fluem pelo sistema.

### Fase 2: Implementação do `DiscoveryEngine` Real

Nesta fase, substituiremos a lógica de simulação pelos clientes de API desenvolvidos na Fase 1.

-   [ ] **2.4. Refatorar Métodos de Descoberta:**
    -   Modificar `_discover_funding_prospects` para chamar o `CrunchbaseClient`.
    -   Modificar `_discover_job_posting_prospects` para interagir com uma API de vagas ou realizar scraping (com as devidas precauções de robustez).
    -   **Atenção ao LinkedIn:** A API do LinkedIn é restrita. A abordagem realista aqui é usar um serviço de terceiros que já tenha esses dados (ex: Apollo.io, ZoomInfo) e criar um cliente para ele, ou, como alternativa menos robusta, implementar um scraper com `Playwright` ou `Selenium`.

-   [ ] **2.5. Refatorar Métodos de Enriquecimento:**
    -   Modificar `_enrich_company_info` para usar APIs como Clearbit ou dados do próprio Google.
    -   Modificar `_enrich_technology_info` para chamar o `WappalyzerClient` ou similar (BuiltWith).
    -   Modificar `_enrich_contact_info` para usar o `HunterClient` ou Snov.io para encontrar contatos de decisão.

### Fase 3: Robustez e Preparação para Produção

Um sistema real precisa ser resiliente a falhas.

-   [ ] **2.6. Tratamento de Erros e Retentativas:**
    -   Implementar blocos `try...except` robustos em todos os clientes de API para lidar com erros de rede, timeouts e respostas de erro da API (ex: 401, 403, 429, 5xx).
    -   Utilizar a biblioteca `tenacity` para implementar uma política de retentativas (retry) com backoff exponencial nas chamadas de API, tornando o sistema resiliente a falhas transitórias.

-   [ ] **2.7. Caching de Respostas:**
    -   Implementar uma camada de cache (ex: usando `diskcache` para uma solução simples ou Redis para uma mais escalável) para armazenar os resultados das chamadas de API.
    -   Isso reduz custos, diminui a latência e evita atingir os limites de taxa (rate limits) das APIs.

-   [ ] **2.8. Logging Aprimorado:**
    -   Expandir o logging para registrar informações cruciais:
        -   Qual API foi chamada e com quais parâmetros.
        -   A latência da resposta da API.
        -   Sucesso ou falha da chamada.
        -   Uso do cache.

### Fase 4: Testes e Validação

-   [ ] **2.9. Testes Unitários com Mocking:**
    -   Expandir a suíte de testes em `tests/`.
    -   Utilizar `pytest` e `unittest.mock` para testar o `DiscoveryEngine` e os `pipelines` sem fazer chamadas de rede reais. "Mockar" as respostas dos clientes de API para simular cenários de sucesso e de falha.

-   [ ] **2.10. Testes de Integração:**
    -   Criar um conjunto separado de testes (ex: marcados com `@pytest.mark.integration`) que realizam chamadas reais a algumas APIs (usando chaves de teste, se disponíveis).
    -   O objetivo é validar o "contrato" com a API externa e garantir que nossa lógica de parsing continua funcionando.

---

## 3. Estrutura de Arquivos Proposta

A principal mudança será a adição do diretório `clients`.

```
arco/
├── __init__.py
├── clients/              <-- NOVO
│   ├── __init__.py
│   ├── base_client.py
│   ├── crunchbase_client.py
│   └── wappalyzer_client.py
├── config/
├── engines/
│   ├── __init__.py
│   ├── base.py
│   └── discovery_engine.py  <-- MODIFICADO
├── models/
├── pipelines/
└── utils/
```