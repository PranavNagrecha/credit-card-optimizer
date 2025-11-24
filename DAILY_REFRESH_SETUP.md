# Daily Data Refresh Setup

## How It Works

✅ **Data is refreshed ONCE per day at midnight**  
✅ **Stored in `.data/` directory** (cards.json, rules.json)  
✅ **API loads from cache instantly** - users never wait  
✅ **No scraping on user requests** - fast responses  

## Architecture

```
┌─────────────────────┐
│  Scheduled Job      │  ← Runs daily at 12:00 AM
│  (scraper_job.py)   │     Scrapes all 10 issuers
└──────────┬──────────┘     Saves to .data/
           │
           ▼
┌─────────────────────┐
│  .data/            │  ← Storage (JSON files)
│  ├─ cards.json     │     Cards and rules
│  └─ rules.json     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  API (app.py)       │  ← Loads from .data/
│  (Fast Startup)     │     Users get instant results
└─────────────────────┘     NO scraping on requests!
```

## Setup on Render.com

### Step 1: Create Scheduled Job

1. Go to Render Dashboard: https://dashboard.render.com
2. Click **"New +"** → **"Cron Job"**
3. Configure:
   - **Name**: `credit-card-scraper-daily`
   - **Schedule**: `0 0 * * *` (runs daily at midnight UTC)
   - **Command**: `cd credit_card_optimizer && python scraper_job.py`
   - **Plan**: **Free**
4. Click **"Create Cron Job"**

### Step 2: Initial Data Load

Before the scheduled job runs, populate initial data:

**Option A: Run manually via Render Shell**
1. Go to your web service in Render
2. Click **"Shell"** tab
3. Run:
   ```bash
   cd credit_card_optimizer
   python scraper_job.py
   ```
4. Wait 2-5 minutes for it to complete

**Option B: Run locally and commit data**
1. Run locally: `python scraper_job.py`
2. This creates `.data/` directory with JSON files
3. Commit and push (optional - data will be regenerated on Render)

### Step 3: Verify

Check that data is loaded:
```bash
curl https://credit-card-optimizer-es1e.onrender.com/health
```

Should show:
```json
{
  "status": "healthy",
  "cards_loaded": 150,
  "rules_loaded": 500,
  "last_updated": "2024-11-24T00:00:00",
  "cache_expired": false
}
```

## How It Works

1. **Midnight (12:00 AM UTC)**: Scheduled job runs `scraper_job.py`
2. **Scraping**: Scrapes all 10 issuers (Chase, Amex, Citi, etc.)
3. **Save**: Writes to `.data/cards.json` and `.data/rules.json`
4. **API**: Loads from `.data/` on startup (fast, < 1 second)
5. **Users**: Get instant responses from cached data

## Important Notes

- ✅ **Users NEVER trigger scraping** - `/api/refresh` is disabled
- ✅ **Data refreshes automatically** - once per day
- ✅ **API is fast** - loads from cache, not scraping
- ✅ **Free tier friendly** - minimal API calls

## Troubleshooting

**No data loaded?**
- Run `scraper_job.py` manually once to populate initial data
- Check Render logs for scheduled job errors

**Data not updating?**
- Check scheduled job logs in Render dashboard
- Verify cron schedule is correct: `0 0 * * *` (midnight UTC)

**Cache expired warning?**
- Scheduled job may have failed
- Check logs and re-run manually if needed

