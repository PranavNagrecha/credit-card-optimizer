"""
Import helper to fix relative imports in Render's flat structure.

On Render, files are directly in /opt/render/project/src/, not in a package.
This module ensures imports work in both package and flat structures.
"""

import sys
import os
from pathlib import Path

def setup_imports():
    """
    Setup Python path to handle both package and flat structures.
    
    This ensures that:
    - Relative imports (from ...models) work in scrapers
    - Direct imports (from models) also work
    """
    current_file = Path(__file__).resolve()
    current_dir = current_file.parent
    
    # Add current directory to path (for direct imports)
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    # Add parent directory to path (so current_dir can be imported as credit_card_optimizer)
    parent_dir = current_dir.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    
    # On Render: files are in /opt/render/project/src/
    # We need to make src/ act as the package root for relative imports
    # This is done by ensuring the parent is in PYTHONPATH
    
    return current_dir, parent_dir

# Auto-setup on import
setup_imports()

