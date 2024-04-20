# Set output encoding to UTF-8
[System.Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Get the current script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Set command prompt encoding to UTF-8
chcp 65001

# Get PowerShell 7 path
$pwsh7Path = & {
    $path = [Environment]::GetEnvironmentVariable('PATH', 'Machine')
    $paths = $path -split ';'
    foreach ($p in $paths) {
        if (Test-Path (Join-Path $p 'pwsh.exe')) {
            $pwshPath = Join-Path $p 'pwsh.exe'
            return $pwshPath
        }
    }
    return $null
}

# If PowerShell 7 is not found, attempt to install it
if (-not $pwsh7Path) {
    Write-Host "PowerShell 7 was not found, attempting to install PowerShell 7.4.2"

    # Download PowerShell 7.4.2 installer
    $installerUrl = "https://github.com/PowerShell/PowerShell/releases/download/v7.4.2/PowerShell-7.4.2-win-x64.msi"
    $installerPath = Join-Path $env:TEMP "PowerShell-7.4.2-win-x64.msi"
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath

    # Install PowerShell 7.4.2
    $arguments = "/i `"$installerPath`" /quiet ADD_EXPLORER_CONTEXT_MENU_OPENPWSHHERE=1 ADD_FILE_CONTEXT_MENU_RUNPOWERSHELL=1 REGISTER_MANIFEST=1"
    Start-Process msiexec.exe -ArgumentList $arguments -Wait

    # Re-get PowerShell 7 path
    $pwsh7Path = & {
        $path = [Environment]::GetEnvironmentVariable('PATH', 'Machine')
        $paths = $path -split ';'
        foreach ($p in $paths) {
            if (Test-Path (Join-Path $p 'pwsh.exe')) {
                $pwshPath = Join-Path $p 'pwsh.exe'
                return $pwshPath
            }
        }
        return $null
    }

    # If PowerShell 7 is still not found after installation, exit with error
    if (-not $pwsh7Path) {
        Write-Error "Failed to install PowerShell 7, please install manually and try again"
        exit 1
    }
}

# Run contest.ps1
& $pwsh7Path (Join-Path $scriptDir 'contest.ps1') -encoding UTF8