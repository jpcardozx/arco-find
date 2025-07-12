# Estrutura do Projeto

Esta seção descreve a estrutura de diretórios e a organização do código do projeto Arco-Find.

```
arco-find/
├───scraper.py
├───TESTING_GUIDE.md
├───USER_GUIDE.md
├───__pycache__/
├───.idea/
├───.venv/
├───.vscode/
├───cache/
├───docs/             # Documentação do projeto
│   ├───index.md
│   ├───installation.md
│   ├───configuration.md
│   ├───usage.md
│   ├───project_structure.md
│   └───contributing.md
├───results/          # Resultados gerados pelo pipeline
└───src/              # Código fonte principal da aplicação
    ├───__init__.py
    ├───api_service.py
    ├───config_service.py
    ├───example_usage.py
    ├───README.md
    ├───__pycache__/
    ├───ads/          # Módulos relacionados a anúncios e inteligência de ads
    ├───analysis/     # Módulos para análise de dados e oportunidades
    ├───config/       # Módulos de configuração da aplicação
    ├───connectors/   # Conectores para APIs externas (ex: Google Ads, Meta Business)
    ├───consolidation/ # Módulos para consolidação de evidências
    ├───core/         # Módulos centrais do motor Arco-Find
    ├───demo/         # Exemplos de demonstração e uso
    ├───detectors/    # Módulos para detecção de oportunidades e tecnologias
    ├───engines/      # Motores de qualificação e inteligência de leads
    ├───integration/  # Módulos de integração e validação de API
    ├───integrations/ # Módulos de integração com outros sistemas (ex: BigQuery)
    ├───intelligence/ # Módulos de inteligência de mercado e benchmarking
    ├───models/       # Definições de modelos de dados (ex: Lead)
    ├───pipeline/     # Módulos que compõem o pipeline de geração de leads
    ├───presentation/ # Módulos para geração de apresentações e resumos executivos
    ├───reports/      # Módulos para geração de relatórios
    ├───results/      # Resultados específicos de módulos (não confundir com a pasta raiz results/)
    ├───scrapers/     # Módulos para web scraping e coleta de dados
    ├───specialist/   # Módulos especializados para análises específicas
    ├───sprint/       # Módulos relacionados a sprints e automação de vendas
    ├───utils/        # Funções utilitárias e de suporte
    └───validation/   # Módulos para validação de dados e evidências
```

Esta estrutura visa organizar o código de forma modular e facilitar a manutenção e expansão do projeto.
