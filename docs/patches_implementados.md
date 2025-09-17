# 🚀 SCRIPTS DE VALIDAÇÃO & SETUP

## Validação Completa do Ambiente

### 1. Testar APIs

```bash
# Validar PageSpeed API
python scripts/test_pagespeed.py

# Validar Google Search API
python scripts/test_search.py

# Validar BuiltWith
python scripts/test_builtwith.py
```

### 2. Correções Implementadas

#### ✅ PATCH A: TechStackDetector Fixed

- **Problema:** `builtwith.parse()` não existe
- **Fix:** Alterado para `builtwith.builtwith()`
- **Arquivo:** `src/tech_stack_detector.py:19`

#### ✅ PATCH B: Entry Point Unificado

- **Problema:** Múltiplos entry points quebrados
- **Fix:** Criado `main.py` unificado
- **Funcionalidade:** Pipeline completo para 7 dias

#### ✅ PATCH C: Documentação Estratégica

- **Criado:** `docs/plano_ataque_7_dias.md`
- **Criado:** `docs/arquitetura_otimizada.md`
- **Criado:** `docs/modelo_negocio_benchmarks.md`

### 3. Próximos Patches Críticos

#### PATCH D: API Validation Layer

```python
# File: scripts/validate_setup.py
import os
import asyncio
import aiohttp

async def validate_all_apis():
    """Valida todas as APIs necessárias"""

    results = {}

    # Test PageSpeed API
    pagespeed_key = os.getenv('GOOGLE_PAGESPEED_API_KEY')
    if pagespeed_key:
        results['pagespeed'] = await test_pagespeed_api(pagespeed_key)
    else:
        results['pagespeed'] = False

    # Test Search API
    search_key = os.getenv('GOOGLE_SEARCH_API_KEY')
    search_cx = os.getenv('GOOGLE_SEARCH_CX')
    if search_key and search_cx:
        results['search'] = await test_search_api(search_key, search_cx)
    else:
        results['search'] = False

    # Test BuiltWith
    results['builtwith'] = test_builtwith()

    return results

if __name__ == "__main__":
    results = asyncio.run(validate_all_apis())
    print("🔧 API Validation Results:")
    for api, status in results.items():
        print(f"  {'✅' if status else '❌'} {api}")
```

#### PATCH E: Prospect Filters

```python
# File: src/core/prospect_filters.py
class ProspectFilters:
    """Elimina false positives do boolean search"""

    INVALID_DOMAINS = {
        'instagram.com', 'facebook.com', 'twitter.com',
        'linkedin.com', 'reddit.com', 'youtube.com',
        'mailchimp.com', 'google.com', 'microsoft.com'
    }

    @classmethod
    def is_valid_smb_prospect(cls, domain: str, title: str, snippet: str) -> bool:
        """Valida se é prospect SMB real brasileiro"""

        # Filter giant tech companies
        if any(invalid in domain.lower() for invalid in cls.INVALID_DOMAINS):
            return False

        # Require Brazilian presence
        if not ('.com.br' in domain or 'brasil' in snippet.lower()):
            return False

        # Filter content vs actual companies
        content_words = ['artigo', 'post', 'guia', 'tutorial', 'como fazer']
        if any(word in title.lower() for word in content_words):
            return False

        return True
```

### 4. Execução Imediata

#### Teste o Sistema Atual

```bash
# Testar pipeline unificado
python main.py

# Verificar output
ls -la output/

# Validar relatório gerado
cat output/immediate_pipeline_*.json | jq '.summary'
```

#### Métricas de Sucesso

- ✅ Zero imports quebrados
- ✅ APIs funcionais (não retornar 404)
- ✅ Prospects reais (não Instagram/Reddit)
- ✅ Revenue calculations baseadas em benchmarks
- ✅ Pipeline completo E2E funcional

### 5. Deploy Checklist

#### Antes de Executar com Cliente Real:

- [ ] Validar todas as API keys
- [ ] Testar com domínios conhecidos
- [ ] Verificar false positive rate < 5%
- [ ] Confirmar revenue calculations
- [ ] Preparar templates de outreach

#### Configuração .env Mínima:

```bash
# APIs Essenciais (obrigatório)
GOOGLE_PAGESPEED_API_KEY=your_key
GOOGLE_SEARCH_API_KEY=your_key
GOOGLE_SEARCH_CX=your_cx

# Business Config
MIN_MONTHLY_LEAK_USD=2000
TARGET_PROSPECTS_PER_RUN=15
```

### 6. Troubleshooting Comum

#### Problema: PageSpeed API 404

```bash
# Verificar quota
curl "https://www.googleapis.com/pagespeed/v5/runPagespeed?url=https://google.com&key=YOUR_KEY"

# Se 404: verificar key, billing, quota
```

#### Problema: BuiltWith não funciona

```bash
# Reinstalar
pip uninstall builtwith
pip install builtwith

# Testar
python -c "import builtwith; print(builtwith.builtwith('https://google.com'))"
```

#### Problema: Prospects irrelevantes

```bash
# Implementar filtros mais rigorosos
# Verificar queries do boolean search
# Adicionar validation layer
```

---

## Status Atual do Sistema

### ✅ FUNCIONANDO:

- Entry point unificado (`main.py`)
- TechStackDetector corrigido
- Documentação estratégica completa
- Infraestrutura async HTTP

### ⚠️ NECESSITA VALIDAÇÃO:

- API keys configuração
- Boolean search filters
- Revenue calculations precisão

### ❌ PRÓXIMOS PATCHES:

- Implementar ProspectFilters
- API validation layer
- Revenue calculator com benchmarks reais
- Integration tests E2E

**Meta:** Sistema 100% funcional para execução do plano de 7 dias
