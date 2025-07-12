# Guia de Configuração

Este guia explica como configurar o Arco-Find para suas necessidades específicas.

## Arquivo de Configuração

O Arco-Find utiliza um arquivo de configuração para gerenciar as configurações da aplicação. Você pode encontrar um exemplo em `src/config/configuration.py`.

Crie um arquivo `.env` na raiz do projeto e adicione suas variáveis de ambiente, como chaves de API e credenciais de banco de dados.

Exemplo de `.env` (utilizado pelo `ARCOConfigManager`):

```
# Chaves de API
GOOGLE_ADS_API_KEY=sua_chave_google_ads_aqui # Necessária para análise de performance de anúncios (simulada)
META_BUSINESS_API_KEY=sua_chave_meta_business_aqui # Necessária para análise de performance de anúncios do Meta (simulada)
GOOGLE_PAGESPEED_API_KEY=sua_chave_pagespeed_aqui # Necessária para análise de performance de website

# Configurações de Banco de Dados
DATABASE_URL=sqlite:///./arco_find.db

# Configurações Gerais da Aplicação
APP_ENV=development # ou production, testing
DEBUG_MODE=True # ou False
```

O `ARCOConfigManager` (localizado em `src/config/arco_config_manager.py`) é responsável por carregar essas variáveis de ambiente e disponibilizá-las para a aplicação.

## Configurações Comuns

Para otimizar a análise e a identificação de ineficiências, é crucial configurar corretamente as seguintes seções:

*   **API Keys:** Configure as chaves de API para serviços externos (ex: Google Ads, Meta Business API). Isso permite que o Arco-Find analise o uso de suas ferramentas e identifique oportunidades de consolidação e economia, combatendo a proliferação de ferramentas.
*   **Credenciais de Banco de Dados:** Se o Arco-Find precisar acessar dados de seus sistemas internos para análise, configure as credenciais apropriadas. Isso é fundamental para uma visão completa do seu ecossistema de SaaS e para identificar silos de dados.
*   **Parâmetros de Análise:** Ajuste os parâmetros específicos para a análise de custos, desempenho e produtividade. Isso inclui definir limites de gastos, métricas de performance desejadas e critérios para identificar ineficiências.

Para mais detalhes sobre as configurações disponíveis e como elas se relacionam com a otimização operacional, consulte o código-fonte em `src/config/`.

Após a configuração, você pode prosseguir para o [Guia de Uso](usage.md).
