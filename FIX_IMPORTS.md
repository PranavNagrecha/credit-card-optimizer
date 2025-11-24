# Import Fix Strategy

## Problem
Render deploys files to `/opt/render/project/src/` (flat structure), but scrapers use relative imports (`from ...models`) that require package structure.

## Solution
Fix imports in key files to handle both package and flat structures:

1. **scrapers/base.py** - Base class (fixed)
2. **scrapers/issuers/*.py** - All issuer scrapers (need fixing)
3. **scraper_job.py** - Entry point (already has fallback)

## Testing
Run `test_render_environment.py` to verify fixes work before deploying.

