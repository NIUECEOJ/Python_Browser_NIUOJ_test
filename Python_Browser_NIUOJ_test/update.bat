::[Bat To Exe Converter]
::
::YAwzoRdxOk+EWAnk
::fBw5plQjdG8=
::YAwzuBVtJxjWCl3EqQJgSA==
::ZR4luwNxJguZRRnk
::Yhs/ulQjdF+5
::cxAkpRVqdFKZSDk=
::cBs/ulQjdF+5
::ZR41oxFsdFKZSDk=
::eBoioBt6dFKZSDk=
::cRo6pxp7LAbNWATEpCI=
::egkzugNsPRvcWATEpCI=
::dAsiuh18IRvcCxnZtBJQ
::cRYluBh/LU+EWAnk
::YxY4rhs+aU+JeA==
::cxY6rQJ7JhzQF1fEqQJQ
::ZQ05rAF9IBncCkqN+0xwdVs0
::ZQ05rAF9IAHYFVzEqQJQ
::eg0/rx1wNQPfEVWB+kM9LVsJDGQ=
::fBEirQZwNQPfEVWB+kM9LVsJDGQ=
::cRolqwZ3JBvQF1fEqQJQ
::dhA7uBVwLU+EWDk=
::YQ03rBFzNR3SWATElA==
::dhAmsQZ3MwfNWATElA==
::ZQ0/vhVqMQ3MEVWAtB9wSA==
::Zg8zqx1/OA3MEVWAtB9wSA==
::dhA7pRFwIByZRRnk
::Zh4grVQjdCyDJGyX8VAjFD4CHFyxOXmsA6cgzOf4+ueCrFkOaMU2bKfO2Ii+OfQb5UvbV4QiwWlfivQiJS53VC2/axwglV5bomyKOfi+oQD2WU2b2WUZLkpeuHfVnz8HdcNsm9cGnSWm+S0=
::YB416Ek+ZG8=
::
::
::978f952a14a936cc963da21a135fa983
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
