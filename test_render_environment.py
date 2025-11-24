#!/usr/bin/env python3
"""
Test script that simulates Render's environment to verify scraper works.

This simulates:
- Render's directory structure: /opt/render/project/src/
- Files are directly in src/, not in src/credit_card_optimizer/
- Python environment constraints
"""

import sys
import os
import subprocess
import tempfile
import shutil
from pathlib import Path

def simulate_render_environment():
    """Create a temporary directory structure that mimics Render."""
    
    # Create temp directory structure like Render
    # Render: /opt/render/project/src/ contains all files directly
    temp_dir = tempfile.mkdtemp(prefix="render_test_")
    src_dir = os.path.join(temp_dir, "src")
    os.makedirs(src_dir)
    
    print(f"📁 Created test environment: {temp_dir}")
    print(f"   Simulating Render structure: {src_dir}/")
    
    # Copy all necessary files to src/ (simulating Render's structure)
    project_root = Path(__file__).parent
    files_to_copy = [
        "scraper_job.py",
        "config.py",
        "data_manager.py",
        "models.py",
        "__init__.py",
        "scrapers",
        "normalization.py",
        "valuation.py",
        "engine.py",
    ]
    
    for item in files_to_copy:
        src_path = project_root / item
        dst_path = Path(src_dir) / item
        if src_path.is_dir():
            shutil.copytree(src_path, dst_path, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        elif src_path.exists():
            shutil.copy2(src_path, dst_path)
            print(f"   Copied: {item}")
    
    # Ensure __init__.py exists in src/ to make it a package
    init_file = Path(src_dir) / "__init__.py"
    if not init_file.exists():
        init_file.touch()
        print(f"   Created: __init__.py in src/")
    
    return temp_dir, src_dir

def test_scraper_in_render_environment():
    """Test scraper_job.py in Render-like environment."""
    
    temp_dir, src_dir = simulate_render_environment()
    
    try:
        print("\n🧪 Testing scraper_job.py in Render-like environment...")
        
        # On Render: files are in /opt/render/project/src/ directly
        # So src_dir IS the working directory, and we need to import directly
        env = os.environ.copy()
        parent_of_src = os.path.dirname(src_dir)  # /opt/render/project/
        # PYTHONPATH should include parent so we can import as credit_card_optimizer
        # BUT files are directly in src/, so we need src/ itself in path
        env['PYTHONPATH'] = f"{parent_of_src}:{src_dir}"
        
        scraper_script = os.path.join(src_dir, "scraper_job.py")
        
        print(f"   Working directory: {src_dir}")
        print(f"   PYTHONPATH: {env['PYTHONPATH']}")
        print(f"   Script: {scraper_script}")
        
        # Test import first - simulate what app.py does
        print("\n   Testing imports (as app.py would)...")
        sys.path.insert(0, parent_of_src)
        sys.path.insert(0, src_dir)
        
        # On Render, files are directly in src/, so we import directly
        # But scraper_job.py uses relative imports, so we need to run it as module
        try:
            # Test direct import (what app.py tries)
            import scraper_job
            print("   ✅ Direct import works!")
        except ImportError as e:
            print(f"   ❌ Direct import failed: {e}")
            # Try package import
            try:
                from credit_card_optimizer.scraper_job import scrape_all_cards_and_rules
                print("   ✅ Package import works!")
            except ImportError as e2:
                print(f"   ❌ Package import also failed: {e2}")
                return False
        
        # Test running as subprocess (what app.py does)
        print("\n   Testing subprocess execution...")
        result = subprocess.run(
            [sys.executable, scraper_script],
            cwd=src_dir,
            env=env,
            capture_output=True,
            text=True,
            timeout=30  # Short timeout for testing
        )
        
        print(f"   Return code: {result.returncode}")
        
        if result.returncode == 0:
            print("   ✅ Scraper executed successfully!")
            if "Starting card and rule scraping job" in result.stdout:
                print("   ✅ Scraper started correctly")
            return True
        else:
            print(f"   ❌ Scraper failed")
            if result.stderr:
                error_lines = result.stderr.split('\n')[:10]
                print(f"   Error output:")
                for line in error_lines:
                    if line.strip():
                        print(f"     {line}")
            return False
            
    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up test environment...")
        shutil.rmtree(temp_dir)
        print("   ✅ Cleanup complete")

if __name__ == "__main__":
    print("=" * 60)
    print("Render Environment Simulation Test")
    print("=" * 60)
    
    success = test_scraper_in_render_environment()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED - Code should work on Render")
    else:
        print("❌ TESTS FAILED - Code needs fixes before deploying")
    print("=" * 60)
    
    sys.exit(0 if success else 1)

