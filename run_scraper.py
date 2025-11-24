#!/usr/bin/env python3
"""
Wrapper script to run scraper_job.py with proper package structure.

This ensures relative imports work in both local and Render environments.
"""

import sys
import os
from pathlib import Path

# Get the directory containing this script
script_dir = Path(__file__).parent.resolve()

# On Render: files are in /opt/render/project/src/
# We need to make src/ act as credit_card_optimizer package
# Solution: Add parent to PYTHONPATH and import as module

# Add parent directory to path
parent_dir = script_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Add current directory to path
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

# Set environment variable to indicate we're running as a module
os.environ['SCRAPER_RUNNING'] = '1'

# Now import and run the scraper
try:
    # Try importing as package first
    from credit_card_optimizer.scraper_job import scrape_all_cards_and_rules
    success = scrape_all_cards_and_rules()
    sys.exit(0 if success else 1)
except ImportError:
    # Fallback: run scraper_job.py directly
    import subprocess
    scraper_script = script_dir / "scraper_job.py"
    
    env = os.environ.copy()
    env['PYTHONPATH'] = f"{parent_dir}:{script_dir}:{env.get('PYTHONPATH', '')}"
    
    result = subprocess.run(
        [sys.executable, str(scraper_script)],
        cwd=str(script_dir),
        env=env
    )
    sys.exit(result.returncode)

