@echo off
cd /d "%~dp0"

echo Starting SecureCare Hospital Management System...
echo.

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: .venv was not found.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" manage.py runserver

pause