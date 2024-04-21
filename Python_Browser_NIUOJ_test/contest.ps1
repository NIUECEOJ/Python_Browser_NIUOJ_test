$OutputEncoding = New-Object -typename System.Text.UTF8Encoding

$password = "jefery"

$python_exe = (Get-Command python).Path

if (-not $python_exe) {
    Write-Error "無法找到 Python 解釋器。"
    exit 1
}

$python_path = $python_exe.Trim()
$script_path = ".\Web_Browser.py"

while ($true) {
    $process = Get-Process -Name python -ErrorAction SilentlyContinue

    Start-Process -FilePath $python_path -ArgumentList $script_path

    if (-not $process) {
        $password_input = ""
        while ($password_input -ne $password) {
            $password_input = Read-Host "請輸入密碼以重啟 Web 瀏覽器" -AsSecureString
            $password_string = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($password_input))

            if ($password_string -ne $password) {
                Write-Warning "密碼錯誤，請重新輸入。"
            } else {
                # 重啟 Web 瀏覽器
                Start-Process -FilePath $python_path -ArgumentList $script_path
            }
        }
    }

    Start-Sleep -Seconds 5
}

# 禁止所有包含 Ctrl、Win 和 Alt 的快捷鍵
Import-Module AppLocker

$keyboardRule = New-Object -TypeName Microsoft.Security.ApplicationId.PolicyManageStore.PolicyRule
$keyboardRule.SourceType = "Microsoft.Security.ApplicationId.PolicyManageStoreSourceType.PackageExecutableType"
$keyboardRule.PolicyRuleType = "Microsoft.Security.ApplicationId.PolicyManageStore.PolicyRuleType.Msi"
$keyboardRule.SecurityLevel = "Disallowed"
$keyboardRule.UserOrGroupIdsSidsList = "S-1-1-0" # 對所有用戶生效
$keyboardRule.Conditions.Add("Microsoft.Security.ApplicationId.PolicyManageStore.PolicyRunFlags", "CTRL")
$keyboardRule.Conditions.Add("Microsoft.Security.ApplicationId.PolicyManageStore.PolicyRunFlags", "ALT")
$keyboardRule.Conditions.Add("Microsoft.Security.ApplicationId.PolicyManageStore.PolicyRunFlags", "WIN")

$appLockerPolicyObject = Get-AppLockerPolicy -Effective
$appLockerPolicyObject.Rules.Add($keyboardRule)
Set-AppLockerPolicy -Policy $appLockerPolicyObject -Ldp applockerexample.xmlfile
Set-AppLockerPolicy -XMLPolicy applockerexample.xmlfile