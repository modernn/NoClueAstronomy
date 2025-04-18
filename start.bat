@echo off
echo Starting NoClueAstronomy API setup...

REM Create data directory if it doesn't exist
if not exist data mkdir data

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Run database migrations (if applicable)
echo Initializing database...
python -m api.models.init_db

REM Start the API server
echo Starting NoClueAstronomy API...
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

pause