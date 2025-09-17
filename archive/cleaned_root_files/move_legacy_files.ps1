$files = Get-ChildItem -Path "legacy" -File
foreach ($file in $files) {
    Copy-Item -Path $file.FullName -Destination "archive\legacy\"
}
Write-Host "Files copied successfully"