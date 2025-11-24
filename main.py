"""
Main entry point for Render deployment.
This file is at the root level so Render can find it easily.
"""

import sys
import os

# Add parent directory to path so we can import credit_card_optimizer
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Also add current directory
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import and run the API
try:
    # Try importing as package first (if running from parent directory)
    from credit_card_optimizer.api import app
except ImportError:
    # Fallback: import directly (if running from within the directory)
    from api import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

