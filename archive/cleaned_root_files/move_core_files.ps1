$files = Get-ChildItem -Path "core" -File
foreach ($file in $files) {
    Copy-Item -Path $file.FullName -Destination "archive\core_legacy\"
}
Write-Host "Core files copied successfully"