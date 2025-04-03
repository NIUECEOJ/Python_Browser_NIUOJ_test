@echo off
chcp 65001 > nul

for /f "delims=" %%i in ('where python') do set "python_exe=%%i"

if not defined python_exe (
	echo Python interpreter not found.
    echo Python interpreter not found. >> cmdlog.log
    pause
    exit /b 1
)

set "python_path=%python_exe%"
set "script_path=.\Web_Browser.py"


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

echo Installing required Python libraries...
echo Installing required Python libraries... >> cmdlog.log
python -m pip install --upgrade pip >> cmdlog.log 2>&1
python -m pip install PyQt5 >> cmdlog.log 2>&1
python -m pip install PyQtWebEngine >> cmdlog.log 2>&1
python -m pip install requests >> cmdlog.log 2>&1
python -m pip install psutil >> cmdlog.log 2>&1
python -m pip install keyboard >> cmdlog.log 2>&1
python -m pip install pywin32 >> cmdlog.log 2>&1

:run_script
echo %python_path% >> cmdlog.log
echo %script_path% >> cmdlog.log
start pythonw "%~dp0%script_path%" >> cmdlog.log 2>&1

