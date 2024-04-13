@echo off
setlocal

rem Get the current directory of the batch file
set "current_dir=%~dp0"

rem Navigate to the current directory
cd /d "%current_dir%"

rem Install the requirements
pip install -r requirements.txt

start cmd /k "python main.py"

:waitloop
timeout /t 2 /nobreak >nul
tasklist /fi "imagename eq python.exe" /v | find /i "main.py" >nul
if errorlevel 1 goto end
goto waitloop

:end
echo Exiting...