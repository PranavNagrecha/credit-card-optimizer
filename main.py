"""
Main entry point for Render deployment.
This file runs from within the credit_card_optimizer directory.
"""

import os
import sys

# Add parent directory to path so we can import as a package
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Add parent to path
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the app - try both ways
try:
    from credit_card_optimizer.api import app
except ImportError:
    # Fallback: import directly if we're already in the package
    from api import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Credit Card Optimizer API on port {port}...")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}")
    uvicorn.run(app, host="0.0.0.0", port=port)

