@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo First run: follow the Windows setup steps in README.md to create .venv.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" racer.py %*
if errorlevel 1 (
    echo See README.md for Windows setup and terminal requirements.
    pause
    exit /b 1
)
