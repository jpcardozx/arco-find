# Guia de Instalação

Este guia detalha os passos para instalar e configurar o ARCO em seu ambiente local.

## Pré-requisitos

Certifique-se de ter os seguintes softwares instalados em sua máquina:

- Python 3.8 ou superior
- Git
- Pip (gerenciador de pacotes Python)

## Passos de Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/arco-find.git
cd arco-find
```

### 2. Crie e Ative um Ambiente Virtual (Recomendado)

```bash
# No Windows
python -m venv .venv
.venv\Scripts\activate

# No macOS/Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o Ambiente

Copie o arquivo de template de variáveis de ambiente e configure-o com suas chaves de API:

```bash
cp .env.template .env
```

Edite o arquivo `.env` com um editor de texto e adicione suas chaves de API e configurações:

```
# Google Services
GOOGLE_PAGESPEED_API_KEY=sua_chave_aqui
GOOGLE_ADS_DEVELOPER_TOKEN=seu_token_aqui

# Meta Business Platform
META_BUSINESS_API_KEY=sua_chave_aqui
META_BUSINESS_APP_ID=seu_app_id
META_BUSINESS_APP_SECRET=seu_app_secret

# Application Configuration
DEBUG_MODE=false
LOG_LEVEL=INFO
```

### 5. Configuração Adicional para o Pipeline Avançado

Se você planeja usar o pipeline avançado, execute o script de configuração para verificar e instalar dependências adicionais:

```bash
python tools/setup_dependencies.py
```

Este script irá:

- Verificar a instalação do Wappalyzer-CLI (se necessário)
- Validar suas chaves de API
- Configurar o ambiente para o pipeline avançado

## Estrutura de Diretórios

Após a instalação, você terá a seguinte estrutura de diretórios:

```
arco/
├── main.py                  # Ponto de entrada principal
├── arco/                    # Pacote principal
│   ├── pipelines/           # Implementações de pipeline
│   ├── engines/             # Motores de processamento
│   ├── models/              # Modelos de dados
│   ├── integrations/        # Integrações com APIs externas
│   ├── config/              # Configurações
│   └── utils/               # Utilitários
├── config/                  # Arquivos de configuração externos
├── tests/                   # Testes unificados
├── docs/                    # Documentação
└── archive/                 # Código legado arquivado
```

## Verificação da Instalação

Para verificar se a instalação foi bem-sucedida, execute:

```bash
python -m pytest tests/test_simplified.py
```

Se os testes passarem, sua instalação está correta e pronta para uso.

## Próximos Passos

Após a instalação, você pode prosseguir para o [Guia de Uso](usage.md) para aprender como utilizar o ARCO para descoberta e qualificação de prospects.
