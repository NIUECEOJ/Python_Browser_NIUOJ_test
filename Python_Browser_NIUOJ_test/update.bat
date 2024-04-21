@echo off
set url=https://github.com/NIUECEOJ/Python_Browser_NIUOJ_test/archive/refs/heads/main.zip
set filename=main.zip
set folder=Python_Browser_NIUOJ_test-main/Python_Browser_NIUOJ_test

:: Check if Python is installed
python --version
if errorlevel 1 (
    echo Python is not installed, please install Python first.
    exit /b
)

:: Check internet connection
ping -n 1 www.github.com >nul 2>nul
if errorlevel 1 (
    echo Unable to connect to the internet, will check if the target folder exists locally.
    if exist %folder% (
        cd %folder%
        start.bat
    ) else (
        echo The target folder does not exist locally, please ensure internet connection and rerun this script.
        exit /b
    )
) else (

	:: Check if the zip file exists, if it does then delete it
	if exist %filename% (
		del /F %filename%
	)

	:: Download the zip file
	powershell -Command "Invoke-WebRequest %url% -OutFile %filename%"

	:: Check if the target folder exists, if it does then delete it
	if exist %folder% (
		rmdir /S /Q %folder%
	)

	:: Unzip the file (Force)
	powershell -Command "Expand-Archive -Path %filename% -DestinationPath . -Force"

	:: Change to the specified directory and run start.bat
	cd %folder%
	start.bat
)
