@echo off
set url=https://github.com/NIUECEOJ/Python_Browser_NIUOJ_test/archive/refs/heads/main.zip
set filename=main.zip
set folder=Python_Browser_NIUOJ_test-main/Python_Browser_NIUOJ_test

:: 下載壓縮檔
powershell -Command "Invoke-WebRequest %url% -OutFile %filename%"

:: 解壓縮
powershell -Command "Expand-Archive -Path %filename% -DestinationPath ."

:: 切換到指定目錄並執行 start.bat
cd %folder%
start.bat
