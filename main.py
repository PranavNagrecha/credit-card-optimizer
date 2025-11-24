"""
Main entry point for Render deployment.
This ensures proper Python path setup for imports.
"""

import os
import sys

# Get absolute paths
current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)
parent_dir = os.path.dirname(current_dir)

# Debug info
print(f"Current file: {current_file}")
print(f"Current dir: {current_dir}")
print(f"Parent dir: {parent_dir}")
print(f"Working dir: {os.getcwd()}")

# Add parent directory to Python path (so we can import credit_card_optimizer as package)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

print(f"Python path (first 3): {sys.path[:3]}")

# Import the app as a package
try:
    print("Attempting to import credit_card_optimizer.api...")
    from credit_card_optimizer.api import app
    print("✅ Successfully imported credit_card_optimizer.api")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Trying direct import...")
    # Fallback: add current dir and import directly
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    from api import app
    print("✅ Successfully imported api directly")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting Credit Card Optimizer API on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)

