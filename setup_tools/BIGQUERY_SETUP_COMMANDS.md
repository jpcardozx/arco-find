## 🔧 COMANDOS PARA CONFIGURAR BIGQUERY

### 📋 **SITUAÇÃO ATUAL**

- ✅ **Google Cloud SDK**: Instalado e detectado
- ⚠️ **PATH**: Precisa ser adicionado permanentemente
- 🎯 **Localização**: `C:\Users\João Pedro Cardozo\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin`

### 🚀 **EXECUTE ESTES COMANDOS**

#### **1. Adicionar ao PATH (PowerShell como Admin)**

```powershell
[Environment]::SetEnvironmentVariable("PATH", "$env:PATH;C:\Users\João Pedro Cardozo\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin", "Machine")
```

#### **2. Ou via Command Prompt (CMD como Admin)**

```cmd
setx PATH "%PATH%;C:\Users\João Pedro Cardozo\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin" /M
```

#### **3. Testar gcloud**

```cmd
gcloud --version
```

#### **4. Configurar BigQuery**

```cmd
python bigquery_gcloud_setup.py
```

### 📝 **INSTRUÇÕES DETALHADAS**

1. **Abrir PowerShell como Administrador**:

   - Pressione `Windows + X`
   - Clique em "Windows PowerShell (Admin)"

2. **Cole e execute o comando PowerShell acima**

3. **Feche e reabra o terminal**

4. **Teste**: `gcloud --version`

5. **Execute**: `python bigquery_gcloud_setup.py`

### ⚡ **COMANDO RÁPIDO TUDO-EM-UM**

Copie e cole no PowerShell Admin:

```powershell
# Adicionar gcloud ao PATH
[Environment]::SetEnvironmentVariable("PATH", "$env:PATH;C:\Users\João Pedro Cardozo\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin", "Machine")

# Atualizar PATH da sessão atual
$env:PATH = "$env:PATH;C:\Users\João Pedro Cardozo\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"

# Testar gcloud
gcloud --version

# Configurar BigQuery (se gcloud funcionar)
python bigquery_gcloud_setup.py
```

### 🎯 **APÓS CONFIGURAÇÃO**

O BigQuery será integrado ao pipeline e você terá:

- 📊 **Analytics avançadas**
- 📈 **Dados históricos de campanhas**
- 🎯 **Insights de performance**
- 💰 **Tracking de waste em tempo real**
