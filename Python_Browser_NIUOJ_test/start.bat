@echo off
chcp 65001 > nul

for /f "delims=" %%i in ('where python') do set "python_exe=%%i"

if not defined python_exe (
    echo 無法找到 Python 解釋器。
    pause
    exit /b 1
)

set "python_path=%python_exe%"
set "script_path=.\Web_Browser.py"

echo 正在安裝必要的 Python 庫...
%python_path% -m pip install PyQt5
%python_path% -m pip install PyQtWebEngine

:restart
echo 正在以系統管理員身份運行 Python 腳本...

>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

if '%errorlevel%' == '0' (
    goto run_script
) else (
    echo 請求管理員權限...
    goto get_admin
)

:get_admin
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"

    "%temp%\getadmin.vbs"
    exit /b

:run_script
echo %python_path%
echo %script_path%
python "%~dp0%script_path%"

:check_script
timeout /t 0.1 > nul
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
if "%ERRORLEVEL%"=="0" (
    goto check_script
) else (
    echo Python script stopped running. Restarting...
    goto restart
)
