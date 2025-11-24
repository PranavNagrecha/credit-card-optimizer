# 🚀 Quick Start Guide

## The Problem I Fixed

**BEFORE (Bad):**
- ❌ API scraped websites **every time it started**
- ❌ Every user = scraping all 10+ issuers
- ❌ Slow, unreliable, rate-limited
- ❌ Wasted resources

**NOW (Good):**
- ✅ Scrapes **once per day** (background job)
- ✅ API loads from saved data (fast!)
- ✅ Users get instant results
- ✅ No rate limiting issues

---

## 🎯 How It Works Now

1. **Background Job** runs daily → Scrapes → Saves to `.data/`
2. **API** loads from `.data/` → Fast startup (< 1 second)
3. **Users** get instant recommendations → No scraping!

---

## 📋 Setup Steps

### 1. Initial Setup (One Time)

```bash
cd credit_card_optimizer

# Install dependencies
pip install -r requirements.txt

# Run scraper job ONCE to populate data
python -m credit_card_optimizer.scraper_job
```

This creates `.data/cards.json` and `.data/rules.json`

### 2. Start the API

```bash
# API loads from .data/ automatically (fast!)
python -m credit_card_optimizer.api
```

Or with uvicorn:
```bash
uvicorn credit_card_optimizer.api:app --host 0.0.0.0 --port 8000
```

### 3. Schedule Daily Refresh

**Option A: Cron (Linux/Mac)**
```bash
crontab -e

# Add this line (runs daily at 2 AM)
0 2 * * * cd /path/to/credit_card_optimizer && python -m credit_card_optimizer.scraper_job
```

**Option B: Render.com Scheduled Jobs**
1. Dashboard → New Scheduled Job
2. Command: `python -m credit_card_optimizer.scraper_job`
3. Schedule: Daily at 2 AM

**Option C: Manual (for testing)**
```bash
# Run whenever you want to refresh
python -m credit_card_optimizer.scraper_job
```

---

## 🌐 Using the API

### Web Interface
Visit: http://localhost:8000

### API Endpoints
```bash
# Get recommendations
curl "http://localhost:8000/api/recommend?query=Amazon"

# Check health/status
curl http://localhost:8000/health

# Manual refresh (admin)
curl -X POST http://localhost:8000/api/refresh
```

---

## ✅ What Changed

### Files Created:
- `data_manager.py` - Saves/loads cards to disk
- `scraper_job.py` - Background scraper (runs daily)
- `HOW_IT_WORKS.md` - Detailed architecture docs

### Files Updated:
- `api.py` - Now loads from disk, not scraping
- `static/index.html` - Better UI with status indicators

### New Directories:
- `.data/` - Stores cards.json and rules.json (gitignored)

---

## 🔍 Verify It Works

1. **Check data exists:**
```bash
ls -la .data/
# Should see: cards.json, rules.json, metadata.json
```

2. **Check API health:**
```bash
curl http://localhost:8000/health
# Should show cards_loaded > 0
```

3. **Test recommendation:**
```bash
curl "http://localhost:8000/api/recommend?query=Amazon"
# Should return card recommendations
```

---

## 🐛 Troubleshooting

### "No cards loaded"
**Fix:** Run `python -m credit_card_optimizer.scraper_job` once

### API is slow
**Check:** Is it loading from `.data/` or scraping? Check logs.

### Data is old
**Fix:** Run scraper job manually or wait for scheduled run

---

## 📚 More Info

- **Architecture details**: See `HOW_IT_WORKS.md`
- **Deployment**: See `FREE_HOSTING.md` and `DEPLOYMENT.md`
- **API docs**: Visit http://localhost:8000/docs

---

## 🎉 Summary

**Before:** Scrape every time = Slow, unreliable  
**After:** Scrape daily, load from disk = Fast, reliable

**Key Point:** The API **never scrapes**. It only loads pre-scraped data from `.data/`.

