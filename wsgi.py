"""
WSGI entry point for Render deployment.
This file allows Render to import the app directly.
"""

import sys
import os

# Add the current directory's parent to Python path
# Render structure: /opt/render/project/src/credit_card_optimizer/
# We need /opt/render/project/src in the path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the app
from credit_card_optimizer.api import app

# WSGI application
application = app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

