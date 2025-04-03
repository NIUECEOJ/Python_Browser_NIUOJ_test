@echo off
chcp 65001 > nul

del /F /Q .\status.log 2>nul || (echo error someone using files & exit /b)
del /F /Q .\cmdlog.log 2>nul || (echo error someone using files & exit /b)

:: Check if we already have admin privileges
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

:: If the previous command was successful, we already have admin privileges
if '%errorlevel%'=='0' (
    echo Already running with admin privileges, starting file deletion...
    goto del_status.log
) else (
    echo Admin privileges needed, requesting...
    goto get_admin
)

:get_admin
echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
"%temp%\getadmin.vbs"
exit /b

:del_status.log
del /F /Q C:\Windows\System32\status.log 2>nul || (echo error someone using files & exit /b)
del /F /Q C:\Windows\System32\cmdlog.log 2>nul || (echo error someone using files & exit /b)


