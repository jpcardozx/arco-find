# SSD Reset Tool - Emergency Recovery
# Execute quando o disco aparecer

$maxAttempts = 5
$attempt = 1

while ($attempt -le $maxAttempts) {
    Write-Host "Tentativa $attempt de $maxAttempts..." -ForegroundColor Yellow
    
    try {
        $disk = Get-Disk | Where-Object FriendlyName -like "*INFOKIT*"
        if ($disk) {
            Write-Host "Disco encontrado! Executando formatação rápida..." -ForegroundColor Green
            
            # Método 1: Força bruta
            try {
                $disk | Clear-Disk -RemoveData -Confirm:$false -ErrorAction Stop
                $disk | Initialize-Disk -PartitionStyle MBR -ErrorAction Stop  
                $partition = $disk | New-Partition -UseMaximumSize -AssignDriveLetter -ErrorAction Stop
                Format-Volume -DriveLetter $partition.DriveLetter -FileSystem NTFS -NewFileSystemLabel "INFOKIT_FIXED" -Force -Confirm:$false -ErrorAction Stop
                
                Write-Host "✅ SUCESSO! SSD formatado com letra $($partition.DriveLetter)" -ForegroundColor Green
                break
            }
            catch {
                Write-Host "Método 1 falhou: $($_.Exception.Message)" -ForegroundColor Red
                
                # Método 2: DiskPart via script
                try {
                    $script = @"
select disk $($disk.Number)
clean
convert mbr
create partition primary
format fs=ntfs quick label="INFOKIT_FIXED"
assign
"@
                    $script | diskpart
                    Write-Host "✅ DiskPart executado!" -ForegroundColor Green
                    break
                }
                catch {
                    Write-Host "Método 2 também falhou" -ForegroundColor Red
                }
            }
        } else {
            Write-Host "Disco não encontrado. Aguardando..." -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "Erro na tentativa $attempt : $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 3
    $attempt++
}

if ($attempt -gt $maxAttempts) {
    Write-Host "❌ Todas as tentativas falharam. SSD pode ter defeito físico." -ForegroundColor Red
} else {
    Write-Host "🎉 Operação concluída!" -ForegroundColor Green
}