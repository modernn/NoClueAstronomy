#!/bin/bash

# Set script to exit on error
set -e

# Create data directory if it doesn't exist
mkdir -p data

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations (if applicable)
echo "Initializing database..."
python -m api.models.init_db

# Start the API server
echo "Starting NoClueAstronomy API..."
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload