@echo off
cd /d "%~dp0"
echo Starting frontend... > startup_log.txt
npm start > frontend_log.txt 2>&1
if %errorlevel% neq 0 (
    echo NPM start failed with code %errorlevel% >> startup_error.txt
)
