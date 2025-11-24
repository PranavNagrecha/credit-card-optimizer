#!/bin/bash
# Start script for Render deployment

export PYTHONPATH="${PYTHONPATH}:/opt/render/project/src"

# Run the API
python -m uvicorn credit_card_optimizer.api:app --host 0.0.0.0 --port ${PORT:-8000}

