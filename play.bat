@echo off
setlocal
cd /d "%~dp0"
py -3 racer_windows.py %*
if errorlevel 1 (
    echo Install Python 3.10 or newer with the Python launcher enabled.
    echo See README.md for instructions.
    pause
    exit /b 1
)
