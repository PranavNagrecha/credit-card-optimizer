"""
Entry point for running the API as a module.

Usage:
    python -m credit_card_optimizer.api
"""

import uvicorn
import os

if __name__ == "__main__":
    from .api import app
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
