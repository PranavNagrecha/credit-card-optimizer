#!/bin/bash
# Start script for Render deployment

# Set PYTHONPATH to include the project root
export PYTHONPATH="/opt/render/project/src:${PYTHONPATH}"

# Change to the project root directory
cd /opt/render/project/src

# Run the API
python -m uvicorn credit_card_optimizer.api:app --host 0.0.0.0 --port ${PORT:-8000}

