# SSD Recovery Tool - Simplified Version
param(
    [Parameter(Mandatory = $true)]
    [int]$DiskNumber,
    [string]$Mode = "Diagnose"
)

Write-Host "SSD Recovery Tool" -ForegroundColor Green
Write-Host "=================" -ForegroundColor Green

function Write-Status {
    param([string]$Message, [string]$Type = "INFO")
    $colors = @{
        "INFO"    = "White"
        "SUCCESS" = "Green" 
        "ERROR"   = "Red"
        "WARN"    = "Yellow"
    }
    Write-Host "[$Type] $Message" -ForegroundColor $colors[$Type]
}

# Check admin rights
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Status "Must run as Administrator!" "ERROR"
    exit 1
}

Write-Status "Accessing Disk $DiskNumber..." "INFO"

try {
    $disk = Get-Disk -Number $DiskNumber -ErrorAction Stop
    Write-Status "Found: $($disk.FriendlyName) - $([math]::Round($disk.Size/1GB,2)) GB" "SUCCESS"
    
    Write-Status "Health: $($disk.HealthStatus)" "INFO"
    Write-Status "Status: $($disk.OperationalStatus)" "INFO"
    Write-Status "ReadOnly: $($disk.IsReadOnly)" "INFO"
    Write-Status "PartitionStyle: $($disk.PartitionStyle)" "INFO"
    
    # Check partitions
    try {
        $partitions = Get-Partition -DiskNumber $DiskNumber -ErrorAction SilentlyContinue
        if ($partitions) {
            Write-Status "Found $($partitions.Count) partition(s):" "INFO"
            foreach ($p in $partitions) {
                Write-Status "  Partition $($p.PartitionNumber): $([math]::Round($p.Size/1GB,2)) GB" "INFO"
            }
        }
        else {
            Write-Status "No partitions detected" "WARN"
        }
    }
    catch {
        Write-Status "Cannot read partitions: $($_.Exception.Message)" "WARN"
    }
    
    if ($Mode -eq "Recover") {
        Write-Status "Starting recovery process..." "WARN"
        
        # Bring online if offline
        if ($disk.OperationalStatus -eq "Offline") {
            Set-Disk -Number $DiskNumber -IsOffline $false
            Write-Status "Disk brought online" "SUCCESS"
        }
        
        # Remove read-only
        if ($disk.IsReadOnly) {
            Set-Disk -Number $DiskNumber -IsReadOnly $false
            Write-Status "Read-only removed" "SUCCESS"
        }
        
        # Clear and format
        Write-Status "Clearing disk..." "INFO"
        Clear-Disk -Number $DiskNumber -RemoveData -Confirm:$false
        
        Write-Status "Initializing disk..." "INFO"
        Initialize-Disk -Number $DiskNumber -PartitionStyle GPT
        
        Write-Status "Creating partition..." "INFO"
        $partition = New-Partition -DiskNumber $DiskNumber -UseMaximumSize -AssignDriveLetter
        
        Write-Status "Formatting..." "INFO"
        Format-Volume -DriveLetter $partition.DriveLetter -FileSystem NTFS -NewFileSystemLabel "RecoveredSSD" -Confirm:$false
        
        Write-Status "Recovery completed successfully!" "SUCCESS"
        Write-Status "Drive letter: $($partition.DriveLetter)" "SUCCESS"
    }
    
}
catch {
    Write-Status "Error: $($_.Exception.Message)" "ERROR"
}

Write-Status "Operation completed." "INFO"