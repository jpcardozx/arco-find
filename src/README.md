# ARCO Lead Pipeline - Componentes Otimizados

Este diretório contém os componentes otimizados para o ARCO Lead Pipeline, implementando as melhorias recomendadas na análise do sistema.

## Componentes Implementados

### 1. API Service (`api_service.py`)

Serviço centralizado para gerenciar chamadas de API com recursos avançados:

- **Caching**: Armazena respostas de API para reduzir chamadas redundantes
- **Rate Limiting**: Controle preciso de taxa de requisições por API
- **Retry Logic**: Implementa backoff exponencial para falhas temporárias
- **Error Handling**: Tratamento abrangente de erros com logging detalhado

#### Exemplo de Uso:

```python
from src.api_service import APIService

async with APIService() as api_service:
    # Registra APIs com diferentes limites
    api_service.register_api("google_places", calls_per_second=0.5, max_concurrent=3)
    
    # Faz uma chamada de API com caching automático
    result = await api_service.query(
        api_name="google_places",
        url="https://maps.googleapis.com/maps/api/place/textsearch/json",
        params={
            'query': 'restaurante São Paulo',
            'key': os.getenv('GOOGLE_API_KEY')
        }
    )
    
    if result['success']:
        # Processa os dados
        places = result['data'].get('results', [])
    else:
        # Trata o erro
        print(f"Erro: {result['error']}")
```

### 2. Config Service (`config_service.py`)

Serviço centralizado para gerenciar configurações do sistema:

- **Múltiplas Fontes**: Carrega configurações de arquivos JSON, variáveis de ambiente e defaults
- **Gerenciamento Seguro de API Keys**: Armazena e gerencia chaves de API de forma segura
- **Validação**: Valida configurações e garante que diretórios necessários existam
- **Configuração por Ambiente**: Suporte para diferentes ambientes (dev, prod)

#### Exemplo de Uso:

```python
from src.config_service import config_service

# Obtém uma API key
api_key = config_service.get_api_key('google')

# Obtém configurações de rate limit para uma API
rate_limits = config_service.get_api_rate_limit('google_places')

# Obtém localizações alvo
locations = config_service.get_target_locations(limit=3)

# Valida configuração
validation = config_service.validate_config()
if not validation['google_api_key']:
    # Configura API key interativamente
    from src.config_service import setup_google_api_key
    setup_google_api_key()
```

## Benefícios das Melhorias

1. **Eficiência**:
   - Redução de chamadas de API redundantes através de caching
   - Melhor gerenciamento de rate limits para evitar bloqueios
   - Paralelização controlada de requisições

2. **Robustez**:
   - Tratamento abrangente de erros
   - Retry logic com backoff exponencial
   - Validação de configurações

3. **Segurança**:
   - Remoção de chaves de API hardcoded
   - Armazenamento seguro de credenciais
   - Separação de configuração e código

4. **Manutenibilidade**:
   - Código modular e bem estruturado
   - Interfaces claras entre componentes
   - Logging detalhado para diagnóstico

## Como Integrar

Para integrar estes componentes otimizados ao pipeline existente:

1. **Configuração**:
   ```python
   from src.config_service import config_service
   
   # Carrega configurações
   api_key = config_service.get_api_key('google')
   ```

2. **Chamadas de API**:
   ```python
   from src.api_service import APIService
   
   async with APIService() as api_service:
       # Substitua chamadas diretas de API por chamadas através do serviço
       result = await api_service.query(...)
   ```

3. **Migração Gradual**:
   - Comece substituindo as chamadas de API mais críticas
   - Migre gradualmente para o novo sistema de configuração
   - Mantenha compatibilidade com código existente durante a transição

## Próximos Passos

1. **Refatoração do Pipeline Principal**:
   - Migrar `real_lead_pipeline.py` para usar os novos serviços
   - Separar lógica de negócio da lógica de API/dados

2. **Testes Automatizados**:
   - Implementar testes unitários para os novos componentes
   - Adicionar testes de integração para o pipeline completo

3. **Monitoramento e Logging**:
   - Implementar sistema de logging estruturado
   - Adicionar métricas de performance e uso de API