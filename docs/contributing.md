# Guia de Contribuição

Obrigado por considerar contribuir para o projeto ARCO! Este guia fornece informações sobre como você pode contribuir para o desenvolvimento e melhoria do projeto.

## Código de Conduta

Ao contribuir para este projeto, você concorda em respeitar todos os colaboradores e manter um ambiente positivo e inclusivo.

## Como Contribuir

Existem várias maneiras de contribuir para o projeto ARCO:

1. **Reportar bugs**: Abra issues para reportar bugs ou problemas encontrados.
2. **Sugerir melhorias**: Compartilhe suas ideias para novas funcionalidades ou melhorias.
3. **Enviar código**: Contribua com código através de pull requests.
4. **Melhorar a documentação**: Ajude a manter a documentação atualizada e clara.

## Processo de Desenvolvimento

### 1. Fork e Clone

Comece fazendo um fork do repositório e clonando-o localmente:

```bash
git clone https://github.com/seu-usuario/arco-find.git
cd arco-find
```

### 2. Configure o Ambiente de Desenvolvimento

Siga as instruções no [Guia de Instalação](installation.md) para configurar seu ambiente de desenvolvimento.

### 3. Crie uma Branch

Crie uma branch para suas alterações:

```bash
git checkout -b feature/nome-da-feature
```

Use prefixos como `feature/`, `bugfix/`, `docs/` ou `refactor/` para indicar o tipo de alteração.

### 4. Desenvolva e Teste

Desenvolva suas alterações seguindo as convenções de código do projeto:

- Use docstrings para documentar funções e classes
- Escreva testes para novas funcionalidades
- Mantenha a cobertura de testes existente
- Siga o estilo de código PEP 8

Execute os testes para garantir que suas alterações não quebrem a funcionalidade existente:

```bash
python -m pytest tests/
```

### 5. Commit e Push

Faça commits das suas alterações com mensagens claras e descritivas:

```bash
git add .
git commit -m "Adiciona funcionalidade X que resolve o problema Y"
git push origin feature/nome-da-feature
```

### 6. Abra um Pull Request

Abra um pull request no GitHub com as seguintes informações:

- Descrição clara do que suas alterações fazem
- Referência a issues relacionadas
- Detalhes sobre como testar suas alterações
- Quaisquer notas adicionais relevantes

## Estrutura do Projeto

Familiarize-se com a estrutura do projeto antes de contribuir:

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

## Convenções de Código

### Estilo de Código

- Siga o [PEP 8](https://www.python.org/dev/peps/pep-0008/) para estilo de código Python
- Use 4 espaços para indentação (não tabs)
- Limite as linhas a 88 caracteres (compatível com Black)
- Use docstrings no estilo Google para documentação

### Nomenclatura

- Classes: `CamelCase`
- Funções e variáveis: `snake_case`
- Constantes: `UPPER_CASE_WITH_UNDERSCORES`
- Arquivos: `snake_case.py`

### Imports

Organize os imports na seguinte ordem:

1. Bibliotecas padrão do Python
2. Bibliotecas de terceiros
3. Imports locais do projeto

Exemplo:

```python
import os
import sys
from typing import List, Dict

import numpy as np
import pandas as pd

from arco.models import Prospect
from arco.utils import helpers
```

## Testes

- Escreva testes para todas as novas funcionalidades
- Mantenha a cobertura de testes existente
- Use pytest para testes
- Organize os testes em uma estrutura que espelha a estrutura do código

## Documentação

- Mantenha a documentação atualizada
- Documente todas as funções, classes e módulos públicos
- Atualize o README.md e outros documentos relevantes quando necessário

## Processo de Revisão

- Todos os pull requests serão revisados por pelo menos um mantenedor do projeto
- Feedback será fornecido para melhorias quando necessário
- As alterações podem precisar ser atualizadas com base no feedback antes de serem mescladas

## Recursos Adicionais

- [Guia de Instalação](installation.md)
- [Guia de Uso](usage.md)
- [Arquitetura do Sistema](architecture.md)
- [Estrutura do Projeto](project_structure.md)

Obrigado por contribuir para o projeto ARCO!
