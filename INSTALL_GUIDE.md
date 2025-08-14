# ARCO Pipeline Installation Guide

## Dependências Necessárias

Antes de executar o pipeline, instale as seguintes dependências:

### 1. Playwright (para scraping Meta Ad Library)
```bash
pip install playwright>=1.40.0
playwright install chromium
```

### 2. HTTP e Async Libraries
```bash
pip install aiohttp>=3.8.0
pip install requests>=2.31.0
```

### 3. HTML Parsing
```bash
pip install beautifulsoup4>=4.12.0
```

### 4. Configuration
```bash
pip install python-dotenv>=1.0.0
```

### 5. Email Validation (para outreach)
```bash
pip install email-validator>=2.0.0
```

## Instalação Completa

```bash
# Instalar todas as dependências de uma vez
pip install playwright aiohttp requests beautifulsoup4 python-dotenv email-validator

# Instalar browsers do Playwright
playwright install chromium
```

## Verificação da Instalação

Para verificar se tudo está funcionando:

```bash
python -c "import playwright; import aiohttp; import sqlite3; print('All dependencies installed successfully')"
```

## Próximos Passos

1. **Testar Meta Ad Library Scraper**: 
   ```bash
   cd src/discovery
   python meta_ads_discovery.py dental_br 10
   ```

2. **Verificar Database Creation**:
   ```bash
   # Verificar se database foi criado
   ls -la data/prospects.db
   ```

3. **Review Logs**:
   ```bash
   # Verificar logs de discovery
   tail -f data/discovery.log
   ```

## Troubleshooting

### Erro: "playwright executable not found"
```bash
playwright install chromium
```

### Erro: "Permission denied" 
```bash
# No Windows, executar como administrador
# No Linux/Mac:
chmod +x src/discovery/meta_ads_discovery.py
```

### Erro de encoding no Windows
Adicionar no início dos scripts Python:
```python
import sys
sys.stdout.reconfigure(encoding='utf-8')
```