@echo off
chcp 65001 > nul

for /f "delims=" %%i in ('where python') do set "python_exe=%%i"

if not defined python_exe (
    echo Python interpreter not found.
    pause
    exit /b 1
)

set "python_path=%python_exe%"
set "script_path=.\Web_Browser.py"

echo Installing required Python libraries...
python -m pip install --upgrade pip
python -m pip install PyQt5
python -m pip install PyQtWebEngine
python -m pip install requests

:restart
echo Running Python script with admin privileges...
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

if '%errorlevel%' == '0' (
    goto run_script
) else (
    echo Requesting admin privileges...
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