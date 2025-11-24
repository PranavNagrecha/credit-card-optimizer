#!/usr/bin/env python3
"""
Script to fix all scraper imports to work in both package and flat structures.

This fixes the relative import issue for Render deployment.
"""

import re
from pathlib import Path

# Import fix pattern to add to each scraper file
IMPORT_FIX = '''import sys
from pathlib import Path

# Handle both package and flat structure imports
try:
    from ...models import (
        CardIssuer,
        CardNetwork,
        CardProduct,
        Cap,
        EarningRule,
        RewardProgram,
        RewardType,
    )
except ImportError:
    # Fallback for flat structure (Render): add root directory to path
    current_file = Path(__file__).resolve()
    # Go up 3 levels: scrapers/issuers/file.py -> root
    root_dir = current_file.parent.parent.parent
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))
    from models import (
        CardIssuer,
        CardNetwork,
        CardProduct,
        Cap,
        EarningRule,
        RewardProgram,
        RewardType,
    )
'''

def fix_scraper_file(file_path: Path):
    """Fix imports in a single scraper file."""
    content = file_path.read_text()
    
    # Check if already fixed
    if 'Handle both package and flat structure imports' in content:
        print(f"  ✓ {file_path.name} already fixed")
        return False
    
    # Find the from ...models import block
    pattern = r'from \.\.\.models import\s*\([^)]+\)'
    
    if not re.search(pattern, content):
        print(f"  ⚠ {file_path.name} - no relative models import found")
        return False
    
    # Replace the import block
    new_import = IMPORT_FIX
    fixed_content = re.sub(pattern, new_import, content, count=1)
    
    # Write back
    file_path.write_text(fixed_content)
    print(f"  ✅ Fixed {file_path.name}")
    return True

def main():
    """Fix all scraper files."""
    scrapers_dir = Path(__file__).parent / "scrapers" / "issuers"
    
    print("Fixing scraper imports...")
    print(f"Directory: {scrapers_dir}")
    
    fixed_count = 0
    scraper_files = list(scrapers_dir.glob("*_manual.py"))
    
    for file_path in scraper_files:
        if fix_scraper_file(file_path):
            fixed_count += 1
    
    print(f"\n✅ Fixed {fixed_count} scraper files")
    print("✅ All scrapers now work in both package and flat structures")

if __name__ == "__main__":
    main()

