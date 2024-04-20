# 獲取 PowerShell 7 的路徑
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

# 如果找不到 PowerShell 7
if (-not $pwsh7Path) {
    Write-Error "無法找到 PowerShell 7 的可執行文件 pwsh.exe"
    exit 1
}

# 獲取當前腳本目錄
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 設置命令提示字元編碼為 UTF-8
chcp 65001

# 執行 contest.ps1
$outputEncoding = [console]::OutputEncoding
If ($outputEncoding -eq [System.Text.Encoding]::Default) { 
    [console]::OutputEncoding = [System.Text.Encoding]::UTF8
}
& $pwsh7Path (Join-Path $scriptDir 'contest.ps1') -encoding UTF8