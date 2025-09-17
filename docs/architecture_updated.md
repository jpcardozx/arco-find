# Arquitetura do ARCO

## Visão Geral

O ARCO foi projetado com uma arquitetura modular e escalável, focada na descoberta e qualificação de prospects com base em vazamentos financeiros e sinais de intenção. A arquitetura segue princípios de design limpo, com separação clara de responsabilidades e interfaces bem definidas.

## Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                     ARCO PLATFORM                               │
├─────────────────────────────────────────────────────────────────┤
│  CLI Interface (main.py) → Pipeline Orchestration               │
│                                ↓                                │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│  │  Intelligence   │  │   Data Pipeline   │  │   Strategic     │ │
│  │    Engines      │  │   & Validation   │  │   Reporting     │ │
│  └─────────────────┘  └──────────────────┘  └─────────────────┘ │
│           │                     │                     │         │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│  │   External      │  │   Data Storage   │  │   Export &      │ │
│  │   Connectors    │  │   & Caching      │  │   Integration   │ │
│  └─────────────────┘  └──────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Camadas da Arquitetura

A arquitetura do ARCO é organizada em camadas lógicas, cada uma com responsabilidades específicas:

### 1. Camada de Interface (main.py)

O ponto de entrada principal do sistema, responsável por:

- Processar argumentos da linha de comando
- Configurar o ambiente de execução
- Orquestrar a execução dos pipelines
- Gerenciar o fluxo de dados entre componentes

### 2. Camada de Pipeline

Implementa os fluxos de trabalho principais do sistema:

- **StandardPipeline**: Pipeline simplificado sem dependências externas
- **AdvancedPipeline**: Pipeline completo com integrações externas

Cada pipeline é responsável por orquestrar a execução dos engines apropriados e gerenciar o fluxo de dados entre eles.

### 3. Camada de Engine

Contém os componentes core que implementam a lógica de negócios:

- **SimplifiedEngine**: Motor simplificado para análise rápida
- **DiscoveryEngine**: Motor de descoberta de prospects
- **LeakEngine**: Motor de detecção de vazamentos financeiros
- **ValidatorEngine**: Motor de validação de dados

### 4. Camada de Integração

Adaptadores para serviços e APIs externos:

- Integrações com Wappalyzer
- Integrações com Google APIs (PageSpeed, Ads)
- Integrações com Meta Business Platform
- Web scraping e coleta de dados

### 5. Camada de Configuração

Gerenciamento centralizado de configurações:

- Carregamento de configurações de arquivos YAML
- Gerenciamento de variáveis de ambiente
- Configurações específicas para diferentes ambientes

### 6. Camada de Utilidades

Ferramentas e helpers compartilhados:

- Logging
- Caching
- Helpers para HTTP
- Formatação de dados

## Fluxo de Dados

O fluxo de dados típico no ARCO segue estas etapas:

1. **Entrada de Dados**: Recebimento de domínios ou termos de busca via CLI
2. **Descoberta**: Identificação de prospects potenciais
3. **Análise**: Detecção de vazamentos financeiros e oportunidades
4. **Qualificação**: Pontuação e priorização de prospects
5. **Validação**: Verificação e enriquecimento de dados
6. **Saída**: Geração de relatórios e exportação de resultados

## Modelos de Dados

### Prospect

Representa um prospect básico identificado pelo sistema:

```python
@dataclass
class Prospect:
    domain: str
    company_name: str
```

### QualifiedProspect

Representa um prospect totalmente qualificado com dados de vazamento:

```python
@dataclass
class QualifiedProspect:
    # Discovery data
    domain: str
    company_name: str
    employee_count: int
    estimated_revenue: int

    # Leak detection data
    monthly_waste: float
    annual_savings: float
    leak_count: int
    top_leaks: List[Dict]

    # Qualification
    qualification_score: int  # 0-100
    priority_tier: str        # A, B, C
    outreach_ready: bool
```

### LeakResult

Representa o resultado da detecção de vazamentos para um domínio:

```python
@dataclass
class LeakResult:
    domain: str
    total_monthly_waste: float
    leaks: List[Leak]
    authority_score: float
    has_ads: bool
    processing_time: float
```

## Interfaces Principais

### Interface de Pipeline

```python
class Pipeline:
    """Interface base para todos os pipelines."""

    async def run(self, **kwargs):
        """Executa o pipeline com os parâmetros fornecidos."""
        raise NotImplementedError("Subclasses devem implementar este método")
```

### Interface de Engine

```python
class Engine:
    """Interface base para todos os motores de processamento."""

    async def process(self, input_data):
        """Processa os dados de entrada e retorna o resultado."""
        raise NotImplementedError("Subclasses devem implementar este método")
```

### Interface de Integração

```python
class Integration:
    """Interface base para integrações com serviços externos."""

    async def connect(self):
        """Estabelece conexão com o serviço externo."""
        raise NotImplementedError("Subclasses devem implementar este método")

    async def execute(self, request):
        """Executa uma requisição no serviço externo."""
        raise NotImplementedError("Subclasses devem implementar este método")
```

## Estratégia de Tratamento de Erros

O ARCO implementa uma estratégia robusta de tratamento de erros:

1. **Logging Centralizado**: Sistema de logging que captura erros em todos os níveis
2. **Exceções Específicas**: Exceções personalizadas para diferentes tipos de erros
3. **Graceful Degradation**: Continuidade de operação mesmo quando algumas integrações falham
4. **Retry Mechanism**: Mecanismos de retry para operações que podem falhar temporariamente

## Estratégia de Caching

Para otimizar o desempenho e reduzir chamadas de API, o ARCO implementa:

1. **Cache em Memória**: Para dados frequentemente acessados
2. **Cache em Disco**: Para resultados de análise que podem ser reutilizados
3. **TTL Configurável**: Tempo de vida configurável para diferentes tipos de dados

## Extensibilidade

A arquitetura do ARCO foi projetada para ser extensível:

1. **Novos Engines**: Facilidade para adicionar novos motores de análise
2. **Novas Integrações**: Interface padronizada para adicionar novas integrações
3. **Estratégias de Qualificação**: Possibilidade de implementar diferentes estratégias de qualificação
4. **Formatos de Saída**: Suporte para múltiplos formatos de relatório

## Considerações de Segurança

O ARCO implementa várias medidas de segurança:

1. **Gerenciamento Seguro de Credenciais**: Uso de variáveis de ambiente para credenciais
2. **Rate Limiting**: Controle de taxa para chamadas de API
3. **Validação de Entrada**: Validação rigorosa de dados de entrada
4. **Sanitização de Saída**: Sanitização de dados antes da geração de relatórios

## Conclusão

A arquitetura do ARCO foi projetada para ser modular, extensível e robusta, permitindo a descoberta e qualificação eficiente de prospects com base em vazamentos financeiros e sinais de intenção. A separação clara de responsabilidades e o uso de interfaces bem definidas facilitam a manutenção e a evolução do sistema.
