# Advanced SSD Recovery Tool for Windows
# Comprehensive solution for corrupted SSD recovery

param(
    [Parameter(Mandatory = $true)]
    [int]$DiskNumber,
    
    [string]$Mode = "Diagnose", # Diagnose, Recover, ForceFormat
    [switch]$Force,
    [switch]$Verbose
)

Write-Host "🔧 Advanced SSD Recovery Tool" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan

# Logging function
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "SUCCESS" { "Green" }
        default { "White" }
    }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

# Check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Administrator)) {
    Write-Log "This script requires administrator privileges. Please run as administrator." "ERROR"
    exit 1
}

# Get disk information
function Get-DiskInfo {
    param([int]$DiskNum)
    
    try {
        $disk = Get-Disk -Number $DiskNum -ErrorAction Stop
        Write-Log "Disk found: $($disk.FriendlyName) - $($disk.Size/1GB)GB" "SUCCESS"
        return $disk
    }
    catch {
        Write-Log "Failed to access disk $DiskNum`: $_" "ERROR"
        return $null
    }
}

# Advanced disk diagnostics
function Invoke-DiskDiagnostics {
    param([object]$Disk)
    
    Write-Log "🔍 Running advanced diagnostics..." "INFO"
    
    # Check disk health
    $healthStatus = $Disk.HealthStatus
    $operationalStatus = $Disk.OperationalStatus
    
    Write-Log "Health Status: $healthStatus" "INFO"
    Write-Log "Operational Status: $operationalStatus" "INFO"
    
    # Check for existing partitions
    try {
        $partitions = Get-Partition -DiskNumber $Disk.Number -ErrorAction SilentlyContinue
        if ($partitions) {
            Write-Log "Found $($partitions.Count) partition(s)" "INFO"
            foreach ($partition in $partitions) {
                Write-Log "  Partition $($partition.PartitionNumber): $($partition.Size/1GB)GB - $($partition.Type)" "INFO"
            }
        }
        else {
            Write-Log "No readable partitions found" "WARN"
        }
    }
    catch {
        Write-Log "Cannot read partition table: $_" "WARN"
    }
    
    # Check if disk is read-only
    if ($Disk.IsReadOnly) {
        Write-Log "Disk is currently READ-ONLY" "WARN"
        return $false
    }
    
    # Check if disk is offline
    if ($Disk.OperationalStatus -eq "Offline") {
        Write-Log "Disk is OFFLINE" "WARN"
        try {
            Set-Disk -Number $Disk.Number -IsOffline $false
            Write-Log "Brought disk online" "SUCCESS"
        }
        catch {
            Write-Log "Failed to bring disk online: $_" "ERROR"
            return $false
        }
    }
    
    return $true
}

# Low-level disk operations
function Invoke-LowLevelOperations {
    param([object]$Disk)
    
    Write-Log "🛠️  Performing low-level operations..." "INFO"
    
    # Remove read-only attribute if present
    if ($Disk.IsReadOnly) {
        try {
            Set-Disk -Number $Disk.Number -IsReadOnly $false
            Write-Log "Removed read-only attribute" "SUCCESS"
        }
        catch {
            Write-Log "Failed to remove read-only: $_" "ERROR"
        }
    }
    
    # Clear disk attributes using diskpart
    $diskpartScript = @"
select disk $($Disk.Number)
attributes disk clear readonly
attributes disk clear hidden
attributes disk clear nodefaultdriveletter
clean
"@
    
    try {
        $diskpartScript | diskpart
        Write-Log "Cleared disk attributes and partition table" "SUCCESS"
        Start-Sleep -Seconds 2
    }
    catch {
        Write-Log "Diskpart operations failed: $_" "ERROR"
    }
}

# Advanced formatting with multiple attempts
function Invoke-AdvancedFormat {
    param([object]$Disk, [string]$FileSystem = "NTFS", [string]$Label = "Recovered_SSD")
    
    Write-Log "💾 Starting advanced formatting process..." "INFO"
    
    # Method 1: PowerShell native commands
    Write-Log "Attempt 1: PowerShell native formatting..." "INFO"
    try {
        Initialize-Disk -Number $Disk.Number -PartitionStyle GPT -Confirm:$false
        $partition = New-Partition -DiskNumber $Disk.Number -UseMaximumSize -AssignDriveLetter
        Format-Volume -DriveLetter $partition.DriveLetter -FileSystem $FileSystem -NewFileSystemLabel $Label -Confirm:$false
        Write-Log "PowerShell formatting completed successfully!" "SUCCESS"
        return $true
    }
    catch {
        Write-Log "PowerShell formatting failed: $_" "WARN"
    }
    
    # Method 2: Diskpart with detailed steps
    Write-Log "Attempt 2: Diskpart detailed formatting..." "INFO"
    $diskpartScript = @"
select disk $($Disk.Number)
clean
convert gpt
create partition primary
active
format fs=$FileSystem quick label="$Label"
assign
"@
    
    try {
        $diskpartScript | diskpart
        Write-Log "Diskpart formatting completed!" "SUCCESS"
        return $true
    }
    catch {
        Write-Log "Diskpart formatting failed: $_" "WARN"
    }
    
    # Method 3: Low-level format using cipher
    Write-Log "Attempt 3: Low-level secure erase..." "INFO"
    try {
        $diskpartClean = @"
select disk $($Disk.Number)
clean all
"@
        $diskpartClean | diskpart
        Start-Sleep -Seconds 5
        
        # Reinitialize after clean all
        Initialize-Disk -Number $Disk.Number -PartitionStyle MBR -Confirm:$false
        $partition = New-Partition -DiskNumber $Disk.Number -UseMaximumSize -AssignDriveLetter
        Format-Volume -DriveLetter $partition.DriveLetter -FileSystem $FileSystem -NewFileSystemLabel $Label -Force -Confirm:$false
        
        Write-Log "Low-level format completed!" "SUCCESS"
        return $true
    }
    catch {
        Write-Log "Low-level format failed: $_" "ERROR"
    }
    
    return $false
}

# Main execution logic
Write-Log "Starting SSD recovery for Disk $DiskNumber..." "INFO"

$targetDisk = Get-DiskInfo -DiskNum $DiskNumber
if (-not $targetDisk) {
    Write-Log "Cannot proceed without valid disk access" "ERROR"
    exit 1
}

switch ($Mode.ToLower()) {
    "diagnose" {
        Write-Log "🔍 DIAGNOSTIC MODE" "INFO"
        $diagResult = Invoke-DiskDiagnostics -Disk $targetDisk
        if ($diagResult) {
            Write-Log "Diagnostics completed. Disk appears recoverable." "SUCCESS"
        }
        else {
            Write-Log "Diagnostics revealed serious issues. Consider 'Recover' mode." "WARN"
        }
    }
    
    "recover" {
        Write-Log "🛠️  RECOVERY MODE" "INFO"
        $diagResult = Invoke-DiskDiagnostics -Disk $targetDisk
        if ($diagResult -or $Force) {
            Invoke-LowLevelOperations -Disk $targetDisk
            # Refresh disk info after operations
            Start-Sleep -Seconds 3
            $targetDisk = Get-Disk -Number $DiskNumber
            $formatResult = Invoke-AdvancedFormat -Disk $targetDisk
            if ($formatResult) {
                Write-Log "🎉 SSD recovery completed successfully!" "SUCCESS"
            }
            else {
                Write-Log "Recovery attempts failed. Disk may have hardware failure." "ERROR"
            }
        }
        else {
            Write-Log "Diagnostics failed. Use -Force to override safety checks." "ERROR"
        }
    }
    
    "forceformat" {
        Write-Log "⚠️  FORCE FORMAT MODE" "WARN"
        Write-Log "This will DESTROY ALL DATA on the disk!" "WARN"
        if ($Force) {
            Invoke-LowLevelOperations -Disk $targetDisk
            Start-Sleep -Seconds 3
            $targetDisk = Get-Disk -Number $DiskNumber
            Invoke-AdvancedFormat -Disk $targetDisk
        }
        else {
            Write-Log "Use -Force parameter to confirm destructive operation" "ERROR"
        }
    }
    
    default {
        Write-Log "Invalid mode. Use: Diagnose, Recover, or ForceFormat" "ERROR"
    }
}

Write-Log "SSD Recovery Tool execution completed." "INFO"