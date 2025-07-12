# Guia de Uso

Este guia descreve como usar o Arco-Find para otimizar seus custos de SaaS, melhorar a performance e aumentar a produtividade operacional.

## Executando o Pipeline de Otimização Operacional

Para iniciar o processo de análise e otimização, você pode executar o script `run.py` diretamente, passando os parâmetros da empresa:

```bash
python src/pipeline/run.py
```

O script `run.py` contém exemplos de como chamar a função `run_optimization_pipeline` com `company_name`, `website_url` e `saas_spend`. Este comando iniciará o pipeline principal, que inclui as etapas de coleta de dados, análise de custos e performance, identificação de ineficiências e geração de recomendações.

## Visualizando os Resultados

Os resultados da análise e otimização serão salvos na pasta `results/` na raiz do projeto. Você encontrará arquivos JSON com os insights de otimização, recomendações e relatórios gerados.

Exemplo de arquivo de resultados:

* `results/optimization_insights_YYYYMMDD_HHMMSS.json`
* `results/performance_report.json`

## Exemplos de Uso

Para exemplos mais detalhados de como interagir com as diferentes funcionalidades do Arco-Find, consulte os arquivos na pasta `src/demo/` e `src/example_usage.py`.

