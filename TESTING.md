# Testing Guide

This document explains how to test the code to ensure it works in both local and Render environments.

## The Problem

On Render, files are deployed directly to `/opt/render/project/src/`, not in a `credit_card_optimizer` package structure. This causes issues with relative imports (`from ...models`) used in the scrapers.

## Test Script

Run `test_render_environment.py` to simulate Render's environment:

```bash
python3 test_render_environment.py
```

This will:
1. Create a temporary directory structure matching Render
2. Copy all necessary files
3. Test imports and subprocess execution
4. Report if the code will work on Render

## Current Status

The test reveals that relative imports fail because Python doesn't recognize the package structure. The solution requires one of:

1. **Fix scrapers to use absolute imports** (requires changing many files)
2. **Create package structure on Render** (via symlink or wrapper)
3. **Modify import system at runtime** (complex but works)

## Running Tests

```bash
# Test Render environment simulation
python3 test_render_environment.py

# Test local environment
python3 scraper_job.py

# Test as package
cd ..
python3 -m credit_card_optimizer.scraper_job
```

