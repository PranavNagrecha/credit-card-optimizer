"""
Main entry point for Render deployment.
This ensures credit_card_optimizer is imported as a package.
"""

import os
import sys

# Get the directory containing this file (credit_card_optimizer/)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get parent directory (should be /opt/render/project/src/)
parent_dir = os.path.dirname(current_dir)

# Add parent directory to Python path so we can import credit_card_optimizer as a package
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Now import as a package (this allows relative imports in api.py to work)
from credit_card_optimizer.api import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Credit Card Optimizer API on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)

