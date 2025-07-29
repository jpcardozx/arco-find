# 🔧 GCLOUD CLI PATH SETUP - PowerShell
# ====================================
# Adiciona gcloud CLI ao PATH do Windows
# Requer execução como Administrador

Write-Host "🔧 GCLOUD CLI PATH SETUP - POWERSHELL" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "🎯 Adicionando gcloud CLI ao PATH do sistema" -ForegroundColor Yellow
Write-Host "⚠️  Requer permissões de administrador" -ForegroundColor Red
Write-Host "=======================================" -ForegroundColor Cyan

# Verificar se está executando como administrador
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ ERRO: Execute como Administrador" -ForegroundColor Red
    Write-Host "📝 Clique com botão direito e 'Executar como administrador'" -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Verificar se Google Cloud SDK está instalado
Write-Host "🔍 Verificando instalação do Google Cloud SDK..." -ForegroundColor Yellow

# Locais comuns de instalação
$GCloudPaths = @(
    "${env:ProgramFiles(x86)}\Google\Cloud SDK\google-cloud-sdk\bin",
    "${env:ProgramFiles}\Google\Cloud SDK\google-cloud-sdk\bin",
    "${env:USERPROFILE}\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin",
    "${env:LOCALAPPDATA}\Google\Cloud SDK\google-cloud-sdk\bin"
)

$FoundPath = $null
foreach ($path in $GCloudPaths) {
    if (Test-Path "$path\gcloud.cmd") {
        $FoundPath = $path
        break
    }
}

if (-not $FoundPath) {
    Write-Host "❌ Google Cloud SDK não encontrado nos locais padrão" -ForegroundColor Red
    Write-Host "📥 Baixe e instale em: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    Write-Host "🔗 Link direto: https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe" -ForegroundColor Cyan
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host "✅ Google Cloud SDK encontrado em: $FoundPath" -ForegroundColor Green

# Verificar se já está no PATH
$CurrentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
if ($CurrentPath -like "*$FoundPath*") {
    Write-Host "✅ gcloud já está no PATH do sistema" -ForegroundColor Green
    
    # Testar comando
    Write-Host "🧪 Testando comando gcloud..." -ForegroundColor Yellow
    try {
        & gcloud --version
        Write-Host "✅ gcloud funcionando corretamente!" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️ gcloud no PATH mas não executável. Verificando..." -ForegroundColor Yellow
    }
}
else {
    # Adicionar ao PATH do sistema
    Write-Host "🔧 Adicionando ao PATH do sistema..." -ForegroundColor Yellow
    
    $NewPath = "$CurrentPath;$FoundPath"
    [Environment]::SetEnvironmentVariable("PATH", $NewPath, "Machine")
    
    Write-Host "✅ PATH atualizado com sucesso!" -ForegroundColor Green
}

# Atualizar PATH da sessão atual
$env:PATH = "$env:PATH;$FoundPath"

# Testar gcloud
Write-Host "🧪 Testando gcloud command..." -ForegroundColor Yellow
try {
    & gcloud --version
    Write-Host "✅ gcloud configurado e funcionando!" -ForegroundColor Green
}
catch {
    Write-Host "❌ Erro ao executar gcloud" -ForegroundColor Red
    Write-Host "💡 Tente fechar e reabrir o PowerShell" -ForegroundColor Yellow
    Read-Host "Pressione Enter para continuar"
}

# Configuração BigQuery
Write-Host ""
Write-Host "🎯 CONFIGURAÇÃO BIGQUERY" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host "✅ gcloud CLI: Disponível" -ForegroundColor Green
Write-Host "🔧 Próximo passo: Configurar BigQuery" -ForegroundColor Yellow

$choice = Read-Host "Executar setup automático do BigQuery agora? (y/n)"
if ($choice -eq "y" -or $choice -eq "Y") {
    Write-Host "🚀 Executando setup BigQuery..." -ForegroundColor Cyan
    Set-Location $PSScriptRoot
    python bigquery_gcloud_setup.py
}
else {
    Write-Host "📝 Para configurar BigQuery depois, execute:" -ForegroundColor Yellow
    Write-Host "   python bigquery_gcloud_setup.py" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "🎉 CONFIGURAÇÃO CONCLUÍDA!" -ForegroundColor Green
Write-Host "✅ gcloud CLI adicionado ao PATH" -ForegroundColor Green
Write-Host "🔧 Reinicie o terminal se necessário" -ForegroundColor Yellow
Write-Host "🚀 Sistema pronto para BigQuery setup" -ForegroundColor Cyan
Read-Host "Pressione Enter para finalizar"
