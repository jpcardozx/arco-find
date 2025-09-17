# Estrutura do Projeto ARCO

Este documento detalha a organização de diretórios e arquivos do projeto ARCO após a refatoração, explicando o propósito de cada componente.

## Visão Geral

O projeto ARCO segue uma estrutura modular com separação clara de responsabilidades, seguindo as melhores práticas de desenvolvimento Python.

```
arco/
├── main.py                  # Ponto de entrada principal
├── README.md                # Documentação principal
├── requirements.txt         # Dependências do projeto
├── setup.py                 # Script de instalação
├── .env.template            # Template para variáveis de ambiente
├── arco/                    # Pacote principal
├── config/                  # Arquivos de configuração externos
├── tests/                   # Testes unificados
├── docs/                    # Documentação
└── archive/                 # Código legado arquivado
```

## Diretórios Principais

### 1. Pacote Principal (`arco/`)

O pacote principal contém toda a lógica de negócios do sistema, organizada em módulos específicos:

```
arco/
├── __init__.py
├── pipelines/           # Implementações de pipeline
├── engines/             # Motores de processamento
├── models/              # Modelos de dados
├── integrations/        # Integrações com APIs externas
├── config/              # Configurações
└── utils/               # Utilitários
```

#### 1.1. Pipelines (`arco/pipelines/`)

Contém as implementações dos diferentes fluxos de trabalho do sistema:

```
pipelines/
├── __init__.py
├── standard_pipeline.py      # Pipeline padrão sem dependências externas
└── advanced_pipeline.py      # Pipeline avançado com integrações externas
```

- **standard_pipeline.py**: Implementa o pipeline padrão que utiliza apenas o SimplifiedEngine para análise rápida sem dependências externas.
- **advanced_pipeline.py**: Implementa o pipeline avançado que utiliza múltiplos engines e integrações externas para uma análise mais completa.

#### 1.2. Engines (`arco/engines/`)

Contém os motores de processamento que implementam a lógica de negócios principal:

```
engines/
├── __init__.py
├── simplified_engine.py      # Motor simplificado
├── discovery_engine.py       # Motor de descoberta
├── leak_engine.py            # Detector de vazamentos
└── validator_engine.py       # Motor de validação
```

- **simplified_engine.py**: Implementa o SimplifiedEngine, que realiza análises rápidas sem dependências externas.
- **discovery_engine.py**: Implementa o DiscoveryEngine, responsável por descobrir prospects potenciais.
- **leak_engine.py**: Implementa o LeakEngine, responsável por detectar vazamentos financeiros.
- **validator_engine.py**: Implementa o ValidatorEngine, responsável por validar e enriquecer dados.

#### 1.3. Models (`arco/models/`)

Contém os modelos de dados utilizados pelo sistema:

```
models/
├── __init__.py
├── prospect.py               # Modelo de prospect
└── leak.py                   # Modelo de vazamento
```

- **prospect.py**: Define os modelos Prospect e QualifiedProspect.
- **leak.py**: Define os modelos LeakResult e Leak.

#### 1.4. Integrations (`arco/integrations/`)

Contém adaptadores para serviços e APIs externos:

```
integrations/
├── __init__.py
├── wappalyzer.py             # Integração com Wappalyzer
└── google_api.py             # Integração com APIs Google
```

- **wappalyzer.py**: Implementa a integração com o Wappalyzer para detecção de tecnologias.
- **google_api.py**: Implementa integrações com APIs do Google (PageSpeed, Ads, etc.).

#### 1.5. Config (`arco/config/`)

Contém o código para gerenciamento de configurações:

```
config/
├── __init__.py
├── settings.py               # Gerenciador de configurações
└── defaults.py               # Valores padrão
```

- **settings.py**: Implementa o gerenciador de configurações que carrega configurações de arquivos YAML e variáveis de ambiente.
- **defaults.py**: Define valores padrão para configurações.

#### 1.6. Utils (`arco/utils/`)

Contém utilitários e helpers compartilhados:

```
utils/
├── __init__.py
├── logger.py                 # Configuração de logging
└── helpers.py                # Funções auxiliares
```

- **logger.py**: Implementa a configuração de logging centralizada.
- **helpers.py**: Contém funções auxiliares utilizadas em todo o projeto.

### 2. Configurações Externas (`config/`)

Contém arquivos de configuração externos em formato YAML:

```
config/
├── production.yml            # Configurações de produção
└── vendor_costs.yml          # Custos de fornecedores
```

- **production.yml**: Configurações padrão para ambiente de produção.
- **vendor_costs.yml**: Configurações de custos de fornecedores para cálculo de vazamentos.

### 3. Testes (`tests/`)

Contém todos os testes do sistema, organizados em uma estrutura que espelha a estrutura do código:

```
tests/
├── __init__.py
├── test_pipelines/           # Testes de pipelines
├── test_engines/             # Testes de engines
└── test_integrations/        # Testes de integrações
```

- **test_pipelines/**: Testes para os diferentes pipelines.
- **test_engines/**: Testes para os motores de processamento.
- **test_integrations/**: Testes para as integrações com serviços externos.

### 4. Documentação (`docs/`)

Contém toda a documentação do projeto:

```
docs/
├── architecture.md           # Documentação de arquitetura
├── usage.md                  # Guia de uso
├── installation.md           # Guia de instalação
├── contributing.md           # Guia de contribuição
└── project_structure.md      # Este documento
```

- **architecture.md**: Documentação detalhada da arquitetura do sistema.
- **usage.md**: Guia de uso do sistema.
- **installation.md**: Guia de instalação e configuração.
- **contributing.md**: Guia para contribuir com o projeto.
- **project_structure.md**: Documentação da estrutura do projeto.

### 5. Código Legado (`archive/`)

Contém código legado que foi arquivado durante a refatoração:

```
archive/
└── README.md                 # Explicação do conteúdo arquivado
```

- **README.md**: Explica o conteúdo da pasta archive e por que o código foi arquivado.

## Arquivos Principais

### 1. Ponto de Entrada (`main.py`)

O arquivo `main.py` é o ponto de entrada principal do sistema. Ele:

- Processa argumentos da linha de comando
- Configura o ambiente de execução
- Inicializa o pipeline apropriado
- Executa o pipeline e processa os resultados

### 2. Configuração de Ambiente (`.env.template`)

O arquivo `.env.template` é um template para o arquivo `.env` que contém variáveis de ambiente necessárias para o funcionamento do sistema, como chaves de API e configurações de ambiente.

### 3. Dependências (`requirements.txt`)

O arquivo `requirements.txt` lista todas as dependências Python necessárias para o projeto, incluindo versões específicas para garantir compatibilidade.

### 4. Instalação (`setup.py`)

O arquivo `setup.py` é um script de instalação que permite instalar o projeto como um pacote Python.

## Fluxo de Dados

O fluxo de dados típico no ARCO segue estas etapas:

1. O usuário executa `main.py` com argumentos específicos
2. `main.py` inicializa o pipeline apropriado (standard ou advanced)
3. O pipeline orquestra a execução dos engines necessários
4. Os engines processam os dados e utilizam integrações quando necessário
5. Os resultados são formatados e retornados ao usuário

## Convenções de Código

O projeto ARCO segue estas convenções de código:

- **Estilo**: PEP 8 para estilo de código Python
- **Docstrings**: Estilo Google para documentação de código
- **Imports**: Organizados por tipo (stdlib, third-party, local)
- **Nomenclatura**: CamelCase para classes, snake_case para funções e variáveis

## Conclusão

A estrutura do projeto ARCO foi projetada para ser modular, extensível e fácil de entender. A separação clara de responsabilidades e a organização lógica dos componentes facilitam a manutenção e a evolução do sistema.
