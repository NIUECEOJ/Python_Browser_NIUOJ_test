@echo off
set url=https://github.com/NIUECEOJ/Python_Browser_NIUOJ_test/archive/refs/heads/dev.zip
set filename=dev.zip
set folder=Python_Browser_NIUOJ_test-dev/Python_Browser_NIUOJ_test

:: Check if Python is installed
python --version
if errorlevel 1 (
    echo Python is not installed, please install Python first.
	pause
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
    echo Downloading dev branch from GitHub...
    powershell -Command "Invoke-WebRequest %url% -OutFile %filename%"

    :: Check if the download was successful
    if not exist %filename% (
        echo Failed to download the dev branch. Please check your internet connection and try again.
        exit /b
    )

    :: Check if the target folder exists, if it does then delete it
    if exist %folder% (
        echo Removing old dev environment...
        rmdir /S /Q %folder%
    )

    :: Unzip the file (Force)
    echo Extracting files...
    powershell -Command "Expand-Archive -Path %filename% -DestinationPath . -Force"

    :: Check if extraction was successful
    if not exist %folder% (
        echo Failed to extract files. The archive may be corrupted.
        exit /b
    )

    echo Dev environment setup complete!
    
    :: Change to the specified directory and run start.bat
    echo Starting the application in dev mode...
    cd %folder%
    start.bat
)
