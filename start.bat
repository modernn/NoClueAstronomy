@echo off
REM Startup script for NoClueAstronomy API (Windows)

echo ===================================================
echo        NoClueAstronomy API Startup Script
echo ===================================================

REM Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher and try again
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist venv\ (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo WARNING: Please edit the .env file to set your API credentials:
    echo - ASTRONOMY_APP_ID and ASTRONOMY_APP_SECRET from astronomyapi.com
    echo - NASA_API_KEY from api.nasa.gov
    echo.
)

REM Create directories if they don't exist
if not exist data\ (
    echo Creating data directory...
    mkdir data
)

if not exist logs\ (
    echo Creating logs directory...
    mkdir logs
)

REM Initialize database with sample data
echo Initializing database...
python -m scripts.init_data
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Database initialization failed
    echo The application may still work but some functionality may be limited
)

REM Set environment variable for development
set PYTHONPATH=%CD%

REM Start the API server
echo.
echo ===================================================
echo Starting NoClueAstronomy API server...
echo.
echo API will be available at: http://localhost:8000
echo API documentation at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ===================================================
echo.

uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload --log-level info

REM This section will run when the server is stopped
echo.
echo Server stopped
pause