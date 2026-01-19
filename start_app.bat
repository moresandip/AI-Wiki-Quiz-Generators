@echo off
echo ========================================
echo AI Wiki Quiz Generator - Starting...
echo ========================================
echo.

:: Check if .env file exists
if not exist "backend\.env" (
    echo [WARNING] .env file not found in backend folder!
    echo Please create backend\.env file with your API key
    echo Example: OPENROUTER_API_KEY=your_key OR GOOGLE_API_KEY=your_key
    echo.
    echo You can run setup_api_key.bat to set it up automatically.
    echo.
    pause
    exit /b 1
)

:: Check for API key in .env (simple check)
findstr "GOOGLE_API_KEY" "backend\.env" >nul
if %errorlevel% neq 0 (
    findstr "OPENROUTER_API_KEY" "backend\.env" >nul
    if %errorlevel% neq 0 (
        echo [WARNING] No API key found in backend\.env!
        echo Please add GOOGLE_API_KEY or OPENROUTER_API_KEY to backend\.env
        echo.
        pause
        exit /b 1
    )
)

:: Check if port 8000 is already in use
netstat -an | findstr ":8000" >nul
if %errorlevel% == 0 (
    echo [WARNING] Port 8000 is already in use!
    echo Please close the application using port 8000 or change the port.
    echo.
    pause
    exit /b 1
)

:: Start Backend
echo [1/2] Starting Backend Server...
cd /d "%~dp0backend"
start "Backend Server" cmd /k "cd /d %~dp0backend && if exist venv\Scripts\activate.bat (venv\Scripts\activate && echo Backend starting on http://localhost:8000 && uvicorn main:app --reload --host 0.0.0.0 --port 8000) else (echo ERROR: Virtual environment not found! && echo Please run: python -m venv venv && pause)"
cd /d "%~dp0"

:: Wait a bit for backend to start
echo Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

:: Check if backend is responding (using PowerShell)
echo Checking backend health...
set /a retry_count=0
:check_backend
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -TimeoutSec 2 -UseBasicParsing; exit 0 } catch { exit 1 }" >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Backend is running on http://localhost:8000
) else (
    set /a retry_count+=1
    if %retry_count% geq 15 (
        echo [WARNING] Backend did not respond after 30 seconds
        echo The backend window should show any errors.
        echo Continuing anyway...
        goto :skip_check
    )
    echo [WAIT] Backend is still starting, waiting... (%retry_count%/15)
    timeout /t 2 /nobreak >nul
    goto check_backend
)
:skip_check

:: Start Frontend
echo [2/2] Starting Frontend Server...
cd /d "%~dp0frontend"
start "Frontend Server" cmd /k "cd /d %~dp0frontend && if exist node_modules (npm start) else (echo Installing dependencies... && npm install && npm start)"
cd /d "%~dp0"

echo.
echo ========================================
echo Servers are starting!
echo ========================================
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000 (will open automatically)
echo.
echo Keep these windows open while using the app.
echo Press any key to exit this window (servers will keep running)...
pause >nul
