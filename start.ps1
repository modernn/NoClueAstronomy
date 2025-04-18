#
# NoClueAstronomy API Startup Script for PowerShell
# 

# Show startup banner
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "   NoClueAstronomy API Launcher    " -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Create data directory if it doesn't exist
if (-not (Test-Path -Path "data")) {
    Write-Host "Creating data directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "data" | Out-Null
}

# Check if virtual environment exists
if (-not (Test-Path -Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if (-not $?) {
        Write-Host "Failed to create virtual environment. Please make sure Python is installed." -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt
if (-not $?) {
    Write-Host "Failed to install dependencies. Please check requirements.txt" -ForegroundColor Red
    exit 1
}

# Run database migrations (if applicable)
Write-Host "Initializing database..." -ForegroundColor Yellow
python -m api.models.init_db
if (-not $?) {
    Write-Host "Database initialization failed." -ForegroundColor Red
    exit 1
}

# Start the API server
Write-Host "Starting NoClueAstronomy API..." -ForegroundColor Green
try {
    uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
}
catch {
    Write-Host "Error starting API server: $_" -ForegroundColor Red
    exit 1
}
finally {
    # Deactivate virtual environment on exit
    deactivate
}