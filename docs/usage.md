# Guia de Uso

Este guia descreve como usar o ARCO para a descoberta e qualificação de prospects com base em vazamentos financeiros e sinais de intenção.

## Interface de Linha de Comando

O ARCO é executado através de uma interface de linha de comando (CLI) no arquivo `main.py`. A CLI oferece várias opções para personalizar a execução dos pipelines.

### Sintaxe Básica

```bash
python main.py --pipeline <tipo_pipeline> --input <entrada> --output <saida> [opções]
```

### Parâmetros Comuns

- `--pipeline <tipo>`: Especifica o tipo de pipeline a ser executado (`standard` ou `advanced`). Padrão: `standard`.
- `--input <entrada>`: Especifica os domínios para análise (para o pipeline standard) ou o termo de busca (para o pipeline advanced).
- `--output <caminho>`: Define o arquivo de saída para os resultados. Se não for especificado, os resultados serão salvos em um arquivo com nome gerado automaticamente no diretório `output/`.
- `--config <caminho>`: Especifica um arquivo de configuração personalizado. Padrão: `config/production.yml`.
- `--limit <número>`: Limita o número de resultados para o pipeline advanced. Padrão: `20`.
- `--debug`: Ativa o modo de depuração com logs mais detalhados.

## Pipeline Padrão (Standard)

O pipeline padrão é ideal para análises rápidas e não requer configuração de APIs externas. Ele usa análise baseada em HTTP e padrões conhecidos para identificar vazamentos financeiros.

### Exemplo de Uso

```bash
# Analisar um único domínio
python main.py --pipeline standard --input kotn.com

# Analisar múltiplos domínios
python main.py --pipeline standard --input kotn.com,glossier.com,semrush.com

# Especificar arquivo de saída
python main.py --pipeline standard --input kotn.com --output output/resultados.json

# Usar configuração personalizada
python main.py --pipeline standard --input kotn.com --config config/minha_config.yml
```

### Entrada de Arquivo

Você também pode fornecer um arquivo contendo uma lista de domínios, um por linha:

```bash
python main.py --pipeline standard --input data/dominios.txt
```

## Pipeline Avançado (Advanced)

O pipeline avançado oferece uma análise mais robusta, integrando-se com ferramentas como Wappalyzer-CLI e APIs externas (Meta Ads, Google PageSpeed, etc.).

### Pré-requisitos

Antes de usar o pipeline avançado, certifique-se de ter:

1. Configurado suas chaves de API no arquivo `.env`
2. Executado o script de configuração: `python tools/setup_dependencies.py`

### Exemplo de Uso

```bash
# Descobrir prospects com base em um termo de busca
python main.py --pipeline advanced --input "empresas de tecnologia"

# Limitar o número de resultados
python main.py --pipeline advanced --input "agências de marketing" --limit 10

# Especificar arquivo de saída
python main.py --pipeline advanced --input "e-commerce" --output output/ecommerce_prospects.json
```

## Interpretando os Resultados

Os resultados da análise são salvos em formato JSON e contêm informações detalhadas sobre os prospects qualificados.

### Exemplo de Resultado (Pipeline Padrão)

```json
[
  {
    "domain": "kotn.com",
    "company_name": "Kotn",
    "monthly_waste": 1250.0,
    "annual_savings": 15000.0,
    "score": 85
  },
  {
    "domain": "glossier.com",
    "company_name": "Glossier",
    "monthly_waste": 2100.0,
    "annual_savings": 25200.0,
    "score": 92
  }
]
```

### Campos Principais

- `domain`: O domínio do prospect
- `company_name`: Nome da empresa
- `monthly_waste`: Estimativa de desperdício financeiro mensal (em USD)
- `annual_savings`: Economia anual potencial (em USD)
- `score`: Pontuação de qualificação (0-100)

## Visualização de Resultados

Os resultados podem ser visualizados de várias formas:

1. **Diretamente no terminal**: Os resultados básicos são exibidos no terminal após a execução.
2. **Arquivo JSON**: Os resultados completos são salvos em um arquivo JSON para análise posterior.
3. **Relatórios**: Para análises mais detalhadas, você pode gerar relatórios usando o módulo de relatórios:

```bash
python -m arco.utils.report_generator --input output/resultados.json --format markdown
```

## Exemplos de Fluxos de Trabalho

### 1. Qualificação Rápida de Domínios Conhecidos

```bash
# Passo 1: Executar o pipeline padrão
python main.py --pipeline standard --input dominios.txt --output output/qualificacao_inicial.json

# Passo 2: Filtrar os prospects de alta pontuação
python -m arco.utils.filter_prospects --input output/qualificacao_inicial.json --min-score 70 --output output/prospects_premium.json
```

### 2. Descoberta e Qualificação Completa

```bash
# Passo 1: Descobrir prospects com o pipeline avançado
python main.py --pipeline advanced --input "empresas de tecnologia" --limit 50 --output output/tech_prospects.json

# Passo 2: Analisar os resultados e gerar relatório
python -m arco.utils.report_generator --input output/tech_prospects.json --format markdown --output output/relatorio_tech.md
```

## Solução de Problemas

### Erros Comuns

1. **Erro de API**: Verifique se suas chaves de API estão configuradas corretamente no arquivo `.env`.
2. **Domínio Inválido**: Certifique-se de que os domínios fornecidos são válidos e acessíveis.
3. **Timeout**: Para domínios que demoram muito para responder, aumente o timeout nas configurações.

### Logs

Os logs detalhados são salvos no diretório `logs/`. Em caso de problemas, verifique o arquivo `logs/arco.main.log` para obter informações de diagnóstico.

## Próximos Passos

Para informações mais detalhadas sobre a arquitetura do sistema e como contribuir para o projeto, consulte:

- [Arquitetura do Sistema](architecture.md)
- [Estrutura do Projeto](project_structure.md)
- [Guia de Contribuição](contributing.md)
