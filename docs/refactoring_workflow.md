# 🎯 ARCO - Workflow de Unificação e Refatoração
**Data**: 16 de Julho de 2025  
**Status**: Proposta de Refatoração  
**Objetivo**: Unificar a lógica do projeto, eliminar redundâncias e criar um sistema coeso, manutenível e pronto para produção.

---

## 📜 **Princípios Orientadores**

1.  **Ponto de Entrada Único**: Todo o trabalho será orquestrado a partir de um `main.py` na raiz.
2.  **Separar Motores de Pipelines**: `engines/` conterá a lógica de análise de domínio; `pipelines/` conterá a lógica de orquestração de ponta a ponta.
3.  **Isolar Dependências**: A configuração de APIs e a instalação de ferramentas externas serão gerenciadas por scripts em `tools/`.
4.  **Arquivar o Legado**: Código antigo, de simulação ou redundante será movido para `legacy/` para preservar o histórico sem poluir o ambiente de desenvolvimento.
5.  **Clareza sobre Realidade**: O sistema deve ser explícito sobre o que é uma análise real (com APIs) versus uma análise simplificada (sem dependências externas).

---

## 🗺️ **Workflow de Refatoração em Patches**

### **Patch 0: Limpeza e Reorganização Foundacional**

**Objetivo**: Criar a estrutura de diretórios correta e mover os arquivos existentes, limpando a raiz do projeto.

**Ações Chave**:

1.  **Criar a Nova Estrutura de Diretórios**:
    ```bash
    mkdir engines pipelines config tools legacy
    ```

2.  **Mover Motores Funcionais para `engines/`**:
    - Mover `arco_simplified_engine.py` para `engines/simplified_engine.py` (Nosso motor funcional sem dependências).
    - Mover `core/leak_detector.py` para `engines/leak_engine.py` (Nosso melhor detector de vazamentos).
    - Mover `core/real_discovery.py` para `engines/discovery_engine.py` (Nossa melhor lógica de descoberta).

3.  **Mover Orquestradores para `pipelines/`**:
    - Mover `core/pipeline.py` para `pipelines/advanced_pipeline.py` (Ele usa o `discovery_engine` e o `leak_engine`).
    - Criaremos um novo `pipelines/standard_pipeline.py` no Patch 1.

4.  **Centralizar Configuração**:
    - Mover `data/vendor_costs.yml` para `config/vendor_costs.yml`.
    - Mover `config/production.yml` para `config/production_settings.yml`.

5.  **Arquivar TODO o Resto (Poluição e Legado)**:
    - Mover todos os outros arquivos `.py` da raiz para `legacy/`.
    - Mover o conteúdo de `core/` (exceto os arquivos já movidos) para `legacy/core_archive/`.
    - Mover `archive/` para `legacy/archive/`.

6.  **Criar o Ponto de Entrada Único (`main.py`)**:
    - Criar um arquivo `main.py` na raiz com a estrutura básica.

**Validação do Patch 0**:
- A raiz do projeto deve conter apenas `main.py`, `requirements.txt`, `README.md`, `.gitignore`, `LICENSE` e os novos diretórios.
- Os diretórios `engines/`, `pipelines/`, `config/` e `legacy/` devem conter os arquivos movidos.

---

### **Patch 1: Pipeline "Standard" - Funcionalidade Imediata**

**Objetivo**: Ter um pipeline de ponta a ponta 100% funcional e sem dependências externas, usando o motor mais confiável que temos.

**Ações Chave**:

1.  **Criar o Pipeline Padrão (`pipelines/standard_pipeline.py`)**:
    - Este pipeline irá importar e usar o `engines/simplified_engine.py`. Ele será responsável por receber uma lista de domínios e orquestrar a análise e a qualificação.

2.  **Atualizar `main.py` para Executar o Pipeline Padrão**:
    - Adicionar um comando ao `main.py` para executar o `standard_pipeline`.

**Código para `main.py` (Patch 1)**:
```python
import argparse
import asyncio
from pipelines.standard_pipeline import StandardPipeline

def main():
    parser = argparse.ArgumentParser(description="ARCO Unificado - Plataforma de Prospecção")
    parser.add_argument(
        'pipeline', 
        choices=['standard'], 
        default='standard', 
        help='Qual pipeline executar.'
    )
    parser.add_argument('--domains', nargs='+', required=True, help='Lista de domínios para analisar.')
    
    args = parser.parse_args()

    if args.pipeline == 'standard':
        print("🚀 Executando o Pipeline Padrão (Análise Simplificada)...")
        pipeline = StandardPipeline()
        results = asyncio.run(pipeline.run(args.domains))
        print(f"✅ Análise concluída. {len(results)} prospect(s) qualificado(s).")
        # Adicionar lógica para exibir ou salvar resultados

if __name__ == "__main__":
    main()
```

**Validação do Patch 1**:
- Executar `python main.py --domains kotn.com glossier.com` deve rodar o pipeline simplificado e gerar resultados, provando que o fluxo básico funciona.

---

### **Patch 2: Pipeline "Advanced" - Habilitando a Arquitetura Real**

**Objetivo**: Ativar o pipeline mais poderoso que depende de APIs e ferramentas externas, e fornecer um mecanismo claro para instalar suas dependências.

**Ações Chave**:

1.  **Refatorar `pipelines/advanced_pipeline.py`**:
    - Ajustar os imports para refletir as novas localizações (`engines/discovery_engine.py`, `engines/leak_engine.py`).

2.  **Criar Script de Setup de Dependências (`tools/setup_dependencies.py`)**:
    - Este script guiará o usuário na instalação do `Wappalyzer-CLI` e na configuração das chaves de API no arquivo `config/production_settings.yml`.

3.  **Atualizar `main.py` para Executar o Pipeline Avançado**:
    - Adicionar a opção `advanced` ao `main.py`.
    - O `main.py` deve verificar se as dependências estão configuradas antes de tentar executar este pipeline.

**Código para `main.py` (Patch 2)**:
```python
# ... (imports anteriores)
from pipelines.advanced_pipeline import AdvancedPipeline
from tools.check_dependencies import check_advanced_dependencies

def main():
    parser = argparse.ArgumentParser(description="ARCO Unificado - Plataforma de Prospecção")
    parser.add_argument(
        'pipeline', 
        choices=['standard', 'advanced'], 
        default='standard', 
        help='Qual pipeline executar.'
    )
    # ... (outros argumentos)

    args = parser.parse_args()

    if args.pipeline == 'standard':
        # ... (lógica do standard)
    elif args.pipeline == 'advanced':
        print("🚀 Executando o Pipeline Avançado (Análise Real com APIs)...")
        if not check_advanced_dependencies():
            print("❌ Dependências do pipeline avançado não estão configuradas.")
            print("👉 Por favor, execute 'python tools/setup_dependencies.py' primeiro.")
            return
            
        pipeline = AdvancedPipeline()
        results = asyncio.run(pipeline.run(count=10)) # O advanced descobre os próprios domínios
        print(f"✅ Análise concluída. {len(results)} prospect(s) qualificado(s).")

# ... (resto do main)
```

**Validação do Patch 2**:
- Executar `python main.py advanced` sem configurar as dependências deve falhar com uma mensagem clara.
- Após rodar o `tools/setup_dependencies.py` e configurar as APIs, `python main.py advanced` deve executar com sucesso.

---

### **Patch 3: Finalização e Documentação**

**Objetivo**: Limpar os detalhes finais e atualizar a documentação para refletir a nova estrutura coesa.

**Ações Chave**:

1.  **Refinar `main.py`**:
    - Adicionar melhor formatação de saída para os resultados.
    - Incluir a opção de salvar a saída em um arquivo JSON.

2.  **Atualizar `README.md`**:
    - Remover toda a informação antiga.
    - Adicionar uma seção "Como Começar" que explica a nova estrutura.
    - Documentar claramente os dois pipelines (`standard` e `advanced`) e como executá-los através do `main.py`.
    - Explicar a necessidade de rodar `tools/setup_dependencies.py` para o pipeline avançado.

3.  **Revisão Final**:
    - Fazer uma última varredura por arquivos perdidos ou código que possa ser arquivado no `legacy/`.

**Validação do Patch 3**:
- O `README.md` deve ser um guia claro e preciso para um novo desenvolvedor (ou para o seu "eu" do futuro).
- O projeto deve parecer limpo, profissional e fácil de usar.

---

## 🏛️ **Arquitetura Final Alvo**

```
ARCO-FIND/
├── main.py                 # Ponto de entrada único
├── requirements.txt
├── README.md               # Documentação atualizada
├── LICENSE
├── .gitignore
├── config/
│   ├── vendor_costs.yml
│   └── production_settings.yml
├── engines/
│   ├── simplified_engine.py
│   ├── discovery_engine.py
│   └── leak_engine.py
├── pipelines/
│   ├── standard_pipeline.py
│   └── advanced_pipeline.py
├── tools/
│   ├── setup_dependencies.py
│   └── check_dependencies.py
└── legacy/
    ├── (Todos os arquivos antigos e de simulação)
```
