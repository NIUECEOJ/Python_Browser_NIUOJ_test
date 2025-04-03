@echo off
chcp 65001 > nul

set "debug_mode=false"

for /f "delims=" %%i in ('where python') do set "python_exe=%%i"

if not defined python_exe (
    echo Python interpreter not found. >> cmdlog.log
    pause
    exit /b 1
)

set "python_path=%python_exe%"
set "script_path=.\Web_Browser.py"

echo Installing required Python libraries... >> cmdlog.log
python -m pip install --upgrade pip >> cmdlog.log 2>&1
python -m pip install PyQt5 >> cmdlog.log 2>&1
python -m pip install PyQtWebEngine >> cmdlog.log 2>&1
python -m pip install requests >> cmdlog.log 2>&1
python -m pip install psutil >> cmdlog.log 2>&1
python -m pip install keyboard >> cmdlog.log 2>&1
python -m pip install pywin32 >> cmdlog.log 2>&1

:restart
echo Running Python script with admin privileges... >> cmdlog.log
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

if %errorlevel% == 0 (
    goto run_script
) else (
    echo Requesting admin privileges... >> cmdlog.log
    goto get_admin
)

:get_admin
echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
"%temp%\getadmin.vbs"
exit /b

:run_script
echo %python_path% >> cmdlog.log
echo %script_path% >> cmdlog.log
python "%~dp0%script_path%" >> cmdlog.log 2>&1

if "%debug_mode%" == "true" exit /b

:check_script
timeout /t 1 > nul
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I "python.exe" >NUL
if %ERRORLEVEL% == 0 (
    goto check_script
) else (
    echo Python script stopped running. Restarting... >> cmdlog.log
    goto restart
)
