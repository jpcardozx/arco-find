# 🔑 CONFIGURAÇÃO DAS APIS - DADOS REAIS

## ⚠️ IMPORTANTE: APIs REAIS NECESSÁRIAS

Este sistema usa apenas APIs oficiais do Google. Você precisa configurar:

## 1. 🗝️ Google API Key

### Obter a API Key:
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um projeto ou selecione um existente
3. Ative as seguintes APIs:
   - **Places API (New)**
   - **PageSpeed Insights API**
   - **Geocoding API**
4. Vá em "Credentials" → "Create Credentials" → "API Key"
5. **Restringir a API Key** por IPs/referrers (segurança)

### Configurar no Sistema:

#### Windows PowerShell:
```powershell
$env:GOOGLE_API_KEY="AIzaSy..."
```

#### Windows CMD:
```cmd
set GOOGLE_API_KEY=AIzaSy...
```

#### Linux/Mac:
```bash
export GOOGLE_API_KEY="AIzaSy..."
```

#### Permanente (Windows):
```powershell
[System.Environment]::SetEnvironmentVariable("GOOGLE_API_KEY", "AIzaSy...", "User")
```

## 2. 💰 Custos das APIs (2025)

### Places API (New):
- **Text Search**: $17 per 1000 requests
- **Place Details**: $17 per 1000 requests  
- **Nearby Search**: $32 per 1000 requests
- **FREE TIER**: Sem mais $200 crédito, mas caps gratuitos por SKU

### PageSpeed Insights API:
- **GRATUITO**: 25,000 requests/dia
- **Rate Limit**: 400 requests/100 segundos

### Geocoding API:
- **$5 per 1000 requests**
- **FREE TIER**: Algumas consultas grátis

## 3. 🎯 Otimização de Custos

### Para 100 prospects/dia:
```
- Geocoding: 4-5 calls/dia = ~$0.02
- Places Search: 100 calls = ~$1.70  
- Place Details: 100 calls = ~$1.70
- PageSpeed: 100 calls = FREE
- TOTAL: ~$3.50/dia para 100 prospects
```

### Estratégias de Economia:
1. **Cache** de geocoding por cidade
2. **Fields mask** no Places (só campos necessários)
3. **Batch processing** quando possível
4. **Rate limiting** para evitar overage

## 4. 🔒 Segurança

### Restricções Recomendadas:
```json
{
  "restrictions": {
    "apiKeyRestrictions": {
      "allowedApis": [
        "places-backend.googleapis.com",
        "pagespeedonline.googleapis.com",
        "geocoding-backend.googleapis.com"
      ]
    }
  }
}
```

### Monitoramento:
- ✅ Ative **billing alerts** 
- ✅ Configure **quotas** por API
- ✅ Monitor **usage** diariamente

## 5. 🧪 Teste de Configuração

```python
import os
from advertising_intelligence_real import RealAdvertisingIntelligence

# Verificar se a API key está configurada
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    print("❌ Configure GOOGLE_API_KEY primeiro")
else:
    print("✅ API Key configurada")
    
    # Teste rápido
    engine = RealAdvertisingIntelligence(api_key)
    businesses = engine.search_businesses_by_niche(
        query="dental clinic", 
        location="Sydney, Australia"
    )
    print(f"Encontradas: {len(businesses)} empresas")
```

## 6. 🚨 Troubleshooting

### Erro: "API_KEY_INVALID"
- ✅ Verifique se a key está correta
- ✅ Confirme que as APIs estão ativadas
- ✅ Aguarde alguns minutos após criar a key

### Erro: "QUOTA_EXCEEDED" 
- ✅ Verifique usage no Console
- ✅ Aumente quotas se necessário
- ✅ Implemente rate limiting

### Erro: "REQUEST_DENIED"
- ✅ Verifique restrições da API key
- ✅ Confirme IPs/referrers autorizados
- ✅ Verifique billing ativo

## 7. 📊 Monitoramento de Costs

### Dashboard Recomendado:
```
📈 API Usage (diário):
- Places API calls: XX/1000
- PageSpeed calls: XX/25000  
- Cost estimate: $X.XX
- Prospects qualified: XX
- Cost per qualified lead: $X.XX
```

### Alertas:
- 🔔 **80% do budget diário** atingido
- 🔔 **Quota limit** se aproximando
- 🔔 **Error rate > 5%** em qualquer API

---

> ⚠️ **NOTA**: Este sistema usa apenas dados públicos e APIs oficiais. Sem scraping, sem violação de ToS, sem dados fictícios.
