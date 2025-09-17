# 🎯 ARCO - Plataforma Unificada de Descoberta de Prospects

Bem-vindo ao ARCO, sua plataforma otimizada para descoberta e qualificação de prospects com base em vazamentos financeiros e sinais de intenção.

---

## 🚀 Visão Geral

O ARCO foi refatorado para oferecer dois pipelines principais, cada um atendendo a diferentes necessidades de análise:

1. **Pipeline Padrão (`standard`)**: Ideal para análises rápidas e sem dependências externas. Perfeito para validação inicial e cenários onde a configuração de APIs não é viável ou necessária.
2. **Pipeline Avançado (`advanced`)**: Utiliza integrações com APIs e ferramentas externas para uma análise mais profunda e precisa, identificando vazamentos financeiros reais e prospects de alto potencial.

---

## 🏁 Primeiros Passos

Para começar a usar o ARCO, siga os passos abaixo:

1. **Clone o Repositório**:

   ```bash
   git clone https://github.com/your-username/arco-find.git
   cd arco-find
   ```

2. **Instale as Dependências Python**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure o Ambiente**:

   ```bash
   # Copie o template de variáveis de ambiente
   cp .env.template .env
   # Edite o arquivo .env com suas chaves de API
   ```

4. **Execute o Pipeline de Sua Escolha**:

   ### a) **Pipeline Padrão (Standard)**

   Este pipeline não requer nenhuma configuração adicional de API ou ferramentas externas. Ele usa análise baseada em HTTP e padrões conhecidos para identificar vazamentos.

   **Uso**:

   ```bash
   python main.py --pipeline standard --input dominio1.com,dominio2.com
   ```

   **Exemplo**:

   ```bash
   python main.py --pipeline standard --input kotn.com,glossier.com,semrush.com
   ```

   **Opções**:

   - `--input <lista de domínios>`: **Obrigatório**. Forneça um ou mais domínios para análise, separados por vírgula.
   - `--output <caminho/arquivo.json>`: **Opcional**. Salva os resultados da análise em um arquivo JSON.
   - `--config <caminho/arquivo.yml>`: **Opcional**. Especifica um arquivo de configuração personalizado.

   ### b) **Pipeline Avançado (Advanced)**

   Este pipeline oferece uma análise mais robusta, integrando-se com ferramentas como Wappalyzer-CLI e APIs externas (Meta Ads, Google PageSpeed, etc.).

   **Configuração Necessária**:

   Antes de executar o pipeline avançado pela primeira vez, você precisa configurar suas dependências e chaves de API:

   1. Execute o script de setup:

      ```bash
      python tools/setup_dependencies.py
      ```

   2. Configure suas chaves de API no arquivo `.env` conforme o template fornecido.

   **Uso**:

   ```bash
   python main.py --pipeline advanced --input "empresas de tecnologia"
   ```

   **Opções**:

   - `--input <termo de busca>`: **Opcional**. Termo de busca para descoberta de prospects.
   - `--output <caminho/arquivo.json>`: **Opcional**. Salva os resultados da análise em um arquivo JSON.
   - `--limit <número>`: **Opcional**. Limita o número de resultados (padrão: 20).
   - `--config <caminho/arquivo.yml>`: **Opcional**. Especifica um arquivo de configuração personalizado.

---

## 🧩 Arquitetura Modular

O ARCO foi refatorado para seguir uma arquitetura modular com separação clara de responsabilidades:

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

A estrutura do projeto segue as melhores práticas de desenvolvimento Python, com módulos claramente separados:

- **Pipelines**: Orquestração dos fluxos de trabalho
- **Engines**: Componentes core que implementam a lógica de negócios
- **Models**: Modelos de dados e interfaces
- **Integrations**: Adaptadores para serviços e APIs externos
- **Config**: Configurações centralizadas e gerenciamento de ambiente
- **Utils**: Ferramentas e helpers compartilhados

---

## 📚 Documentação

Para informações detalhadas sobre o projeto, consulte a documentação na pasta `docs/`:

- [Guia de Instalação](docs/installation.md) - Instruções detalhadas de instalação
- [Guia de Uso](docs/usage.md) - Como usar o ARCO no dia a dia
- [Arquitetura](docs/architecture.md) - Visão geral da arquitetura do sistema
- [Estrutura do Projeto](docs/project_structure.md) - Organização de diretórios e arquivos

---

## 🧪 Testes

O ARCO inclui uma suíte de testes abrangente para garantir a qualidade e a confiabilidade do código:

```bash
# Executar todos os testes
python -m pytest tests/

# Executar testes específicos
python -m pytest tests/test_pipelines/
```

---

## 🧹 Manutenção

O ARCO inclui scripts para manutenção e limpeza do projeto:

```bash
# Limpar arquivos temporários e caches
python cleanup_script.py
```

Este script remove:

- Diretórios de cache (`__pycache__`, `.pytest_cache`, etc.)
- Arquivos temporários (`.pyc`, `.tmp`, `.bak`, etc.)
- Logs vazios

Execute este script periodicamente para manter o projeto limpo e organizado.

---

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Faça commit das suas alterações (`git commit -am 'Adiciona nova feature'`)
4. Faça push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

Consulte o [Guia de Contribuição](docs/contributing.md) para mais detalhes.

---

## 📄 Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo `LICENSE` para detalhes.

---

## ❓ Suporte

Para dúvidas ou suporte, abra uma issue no repositório GitHub ou consulte a [documentação](docs/index.md).
