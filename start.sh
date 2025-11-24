#!/bin/bash
# Start script for Render deployment

# Set PYTHONPATH to include project root
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH

# Run main.py from the credit_card_optimizer directory
cd /opt/render/project/src/credit_card_optimizer
python main.py

