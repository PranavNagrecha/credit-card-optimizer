#!/bin/bash
# Quick start script for the Credit Card Optimizer API

set -e

echo "Starting Credit Card Optimizer API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create cache directory
mkdir -p .cache/scrapers

# Run the API
echo "Starting API server on http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Frontend: http://localhost:8000/"
echo ""
uvicorn credit_card_optimizer.api:app --host 0.0.0.0 --port 8000 --reload

