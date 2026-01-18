@echo off
cd /d "%~dp0"
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo Failed to activate venv > startup_error.txt
    exit /b 1
)
echo Venv activated >> startup_log.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 > backend_log.txt 2>&1
if %errorlevel% neq 0 (
    echo Uvicorn failed with code %errorlevel% >> startup_error.txt
)
