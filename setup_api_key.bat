



@echo off
echo ========================================
echo API Key Setup for AI Wiki Quiz Generator
echo ========================================
echo.
echo This script will help you set up your Google Gemini API key.
echo.
echo To get your API key:
echo 1. Visit: https://makersuite.google.com/app/apikey
echo 2. Sign in with your Google account
echo 3. Create a new API key
echo 4. Copy the API key
echo.
set /p API_KEY="Enter your Google Gemini API key: "
echo.
if "%API_KEY%"=="" (
    echo Error: API key cannot be empty!
    pause
    exit /b 1
)
echo.
echo Creating .env file in backend folder...
(
    echo GOOGLE_API_KEY=%API_KEY%
) > backend\.env
echo.
echo API key saved successfully!
echo.
echo You can now run start_app.bat to start the application.
echo.
pause

