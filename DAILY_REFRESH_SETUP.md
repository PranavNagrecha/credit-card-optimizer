# Daily Data Refresh Setup

## How It Works

✅ **Data is refreshed ONCE per day at midnight UTC** (automatic!)  
✅ **Stored in `.data/` directory** (cards.json, rules.json)  
✅ **API loads from cache instantly** - users never wait  
✅ **No scraping on user requests** - fast responses  
✅ **Works on FREE tier** - no scheduled jobs needed!  

## Architecture

```
┌─────────────────────┐
│  Built-in Scheduler │  ← Runs daily at 12:00 AM UTC
│  (in app.py)        │     Scrapes all 10 issuers
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

## Setup (Automatic - No Manual Steps!)

### ✅ It's Already Set Up!

The API now includes a **built-in scheduler** that:
1. **Automatically scrapes on first startup** if no data exists
2. **Runs daily refresh at midnight UTC** automatically
3. **Works on free tier** - no scheduled jobs or shell access needed!

### What Happens:

1. **First Startup**: If no data exists, API automatically runs scraper (takes 2-5 minutes)
2. **Daily**: Scheduler runs scraper at midnight UTC automatically
3. **Users**: Always get instant responses from cached data

### Manual Refresh (Optional)

If you need to refresh data manually, you can call:
```bash
curl -X POST https://your-app.onrender.com/api/refresh
```

But this is usually not needed - the scheduler handles it automatically!

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

