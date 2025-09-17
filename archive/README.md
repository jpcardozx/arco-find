# Arquivos Legados do Projeto ARCO

Este diretório contém arquivos legados do projeto ARCO que foram preservados para referência histórica, mas não são mais utilizados ativamente no código principal.

## Propósito

- Manter um histórico de implementações anteriores
- Preservar código que pode ser útil para referência futura
- Evitar a perda de conhecimento institucional
- Manter testes e implementações que podem ser úteis para futuras iterações

## Organização

Os arquivos neste diretório estão organizados por categoria:

- `engines/`: Implementações antigas de motores de processamento
- `pipelines/`: Pipelines legados
- `scripts/`: Scripts utilitários que não são mais utilizados
- `prototypes/`: Protótipos e provas de conceito iniciais
- `tests/`: Testes legados que não são mais compatíveis com a estrutura atual

## Arquivos Arquivados

Os seguintes arquivos foram arquivados durante a refatoração do projeto:

- `test_apicache.py`: Teste para o sistema de cache de API legado
- `test_arco_engine.py`: Teste para o motor ARCO legado
- `test_framework.py`: Framework de teste abrangente para o ARCO V2.0

## Uso

Este código é mantido apenas para referência e não deve ser importado ou utilizado no código de produção. Se você precisar reutilizar alguma funcionalidade destes arquivos, considere refatorá-la e integrá-la adequadamente na estrutura atual do projeto.

## Nota

Ao adicionar arquivos a este diretório, por favor inclua um comentário no início do arquivo explicando:

1. Quando e por que o arquivo foi movido para o arquivo
2. Qual funcionalidade ele implementava
3. Qual é a implementação atual que o substitui
