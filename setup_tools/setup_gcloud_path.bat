@echo off
echo 🔧 GCLOUD CLI PATH SETUP - WINDOWS
echo ========================================
echo 🎯 Adicionando gcloud CLI ao PATH do sistema
echo ⚠️  Requer permissões de administrador
echo ========================================

:: Verificar se está executando como administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ ERRO: Execute como Administrador
    echo 📝 Clique com botão direito e "Executar como administrador"
    pause
    exit /b 1
)

:: Verificar se Google Cloud SDK está instalado
echo 🔍 Verificando instalação do Google Cloud SDK...

:: Locais comuns de instalação
set "GCLOUD_PATHS="
set "GCLOUD_PATHS=%GCLOUD_PATHS%;C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin"
set "GCLOUD_PATHS=%GCLOUD_PATHS%;C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin"
set "GCLOUD_PATHS=%GCLOUD_PATHS%;%USERPROFILE%\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"
set "GCLOUD_PATHS=%GCLOUD_PATHS%;%LOCALAPPDATA%\Google\Cloud SDK\google-cloud-sdk\bin"

set "FOUND_PATH="
for %%p in (%GCLOUD_PATHS%) do (
    if exist "%%p\gcloud.cmd" (
        set "FOUND_PATH=%%p"
        goto :found
    )
)

echo ❌ Google Cloud SDK não encontrado nos locais padrão
echo 📥 Baixe e instale em: https://cloud.google.com/sdk/docs/install
echo 🔗 Link direto: https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe
pause
exit /b 1

:found
echo ✅ Google Cloud SDK encontrado em: %FOUND_PATH%

:: Verificar se já está no PATH
echo %PATH% | findstr /i /c:"%FOUND_PATH%" >nul
if %errorLevel% equ 0 (
    echo ✅ gcloud já está no PATH do sistema
    echo 🧪 Testando comando gcloud...
    gcloud --version
    if %errorLevel% equ 0 (
        echo ✅ gcloud funcionando corretamente!
        goto :test_bigquery_setup
    )
)

:: Adicionar ao PATH do sistema
echo 🔧 Adicionando ao PATH do sistema...
for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do set "SYSTEM_PATH=%%b"

:: Verificar se o path já contém o diretório
echo %SYSTEM_PATH% | findstr /i /c:"%FOUND_PATH%" >nul
if %errorLevel% neq 0 (
    echo 📝 Atualizando PATH do sistema...
    setx PATH "%SYSTEM_PATH%;%FOUND_PATH%" /M
    if %errorLevel% equ 0 (
        echo ✅ PATH atualizado com sucesso!
    ) else (
        echo ❌ Erro ao atualizar PATH do sistema
        pause
        exit /b 1
    )
) else (
    echo ✅ Path já configurado no sistema
)

:: Atualizar PATH da sessão atual
set "PATH=%PATH%;%FOUND_PATH%"

echo 🧪 Testando gcloud command...
gcloud --version
if %errorLevel% equ 0 (
    echo ✅ gcloud configurado e funcionando!
) else (
    echo ❌ Erro ao executar gcloud
    echo 💡 Tente fechar e reabrir o terminal
    pause
    exit /b 1
)

:test_bigquery_setup
echo.
echo 🎯 CONFIGURAÇÃO BIGQUERY
echo ========================
echo ✅ gcloud CLI: Disponível
echo 🔧 Próximo passo: Configurar BigQuery

choice /c YN /m "Executar setup automático do BigQuery agora?"
if %errorLevel% equ 1 (
    echo 🚀 Executando setup BigQuery...
    cd /d "%~dp0"
    python bigquery_gcloud_setup.py
) else (
    echo 📝 Para configurar BigQuery depois, execute:
    echo    python bigquery_gcloud_setup.py
)

echo.
echo 🎉 CONFIGURAÇÃO CONCLUÍDA!
echo ✅ gcloud CLI adicionado ao PATH
echo 🔧 Reinicie o terminal se necessário
echo 🚀 Sistema pronto para BigQuery setup
pause
