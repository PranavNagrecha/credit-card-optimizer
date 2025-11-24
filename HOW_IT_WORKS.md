# How It Works - Architecture Overview

## 🎯 The Problem (Before)

**OLD WAY (BAD):**
- API scrapes websites **every time it starts**
- Every user request = scraping all 10+ issuers
- Slow, unreliable, gets rate-limited
- Wastes resources

## ✅ The Solution (Now)

**NEW WAY (GOOD):**
- **Scrape once per day** → Save to disk
- **API loads from disk** → Fast, no scraping
- **Background job** → Runs automatically
- **Users get instant results** → No waiting

---

## 📊 Architecture

```
┌─────────────────┐
│  scraper_job.py │  ← Runs once per day (cron/scheduler)
│  (Background)   │     Scrapes all issuers
└────────┬────────┘     Saves to .data/cards.json
         │
         ▼
┌─────────────────┐
│  .data/         │  ← Persistent storage
│  ├─ cards.json  │     Cards and rules saved here
│  └─ rules.json  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  api.py         │  ← Web API (FastAPI)
│  (Fast Startup) │     Loads from .data/
└────────┬────────┘     Serves users instantly
         │
         ▼
┌─────────────────┐
│  Users/Browser  │  ← Gets recommendations
│                 │     No scraping, fast!
└─────────────────┘
```

---

## 🔄 Data Flow

### 1. **Scraping Job** (Daily)
```bash
# Runs automatically via cron/systemd/scheduler
python -m credit_card_optimizer.scraper_job
```

**What it does:**
- Scrapes all 10+ issuers (Chase, Amex, Citi, etc.)
- Extracts cards and earning rules
- Saves to `.data/cards.json` and `.data/rules.json`
- Takes 2-5 minutes (runs once per day)

### 2. **API Startup** (Fast)
```python
# api.py loads from disk, not scraping
cards, rules = data_manager.load_cards_and_rules()
```

**What it does:**
- Reads JSON files from `.data/`
- Loads into memory
- Takes < 1 second
- **No web scraping!**

### 3. **User Request** (Instant)
```bash
GET /api/recommend?query=Amazon
```

**What it does:**
- Uses in-memory data (already loaded)
- Finds best cards
- Returns results instantly
- **No scraping!**

---

## ⚙️ Components

### `data_manager.py`
- **Purpose**: Save/load cards and rules to/from disk
- **Files**: `.data/cards.json`, `.data/rules.json`, `.data/metadata.json`
- **Features**:
  - JSON serialization
  - Cache expiration (24 hours)
  - Last updated tracking

### `scraper_job.py`
- **Purpose**: Background job to refresh data
- **When**: Runs once per day (or manually)
- **Output**: Updates `.data/` files
- **Usage**: 
  ```bash
  python -m credit_card_optimizer.scraper_job
  ```

### `api.py` (Updated)
- **Purpose**: Web API for users
- **Startup**: Loads from `.data/` (not scraping)
- **Endpoints**:
  - `GET /api/recommend` - Get recommendations
  - `POST /api/refresh` - Manually trigger refresh
  - `GET /health` - Check status

---

## 🚀 Deployment Setup

### Step 1: Initial Data Load
```bash
# Run once to populate initial data
python -m credit_card_optimizer.scraper_job
```

### Step 2: Schedule Daily Refresh
**Option A: Cron (Linux/Mac)**
```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 2 AM)
0 2 * * * cd /path/to/project && python -m credit_card_optimizer.scraper_job
```

**Option B: Systemd Timer (Linux)**
```bash
# Create timer service (see systemd example below)
```

**Option C: Render/Railway Cron Jobs**
- Use platform's scheduled jobs feature
- Set to run `scraper_job.py` daily

### Step 3: Start API
```bash
# API loads from .data/ automatically
uvicorn credit_card_optimizer.api:app --host 0.0.0.0 --port 8000
```

---

## 📅 Scheduling Examples

### Cron (Every Day at 2 AM)
```bash
0 2 * * * cd /path/to/credit_card_optimizer && python -m credit_card_optimizer.scraper_job >> /var/log/scraper.log 2>&1
```

### Systemd Timer
Create `/etc/systemd/system/credit-card-scraper.service`:
```ini
[Unit]
Description=Credit Card Scraper Job
After=network.target

[Service]
Type=oneshot
User=www-data
WorkingDirectory=/path/to/credit_card_optimizer
ExecStart=/usr/bin/python3 -m credit_card_optimizer.scraper_job
```

Create `/etc/systemd/system/credit-card-scraper.timer`:
```ini
[Unit]
Description=Run credit card scraper daily
Requires=credit-card-scraper.service

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable:
```bash
sudo systemctl enable credit-card-scraper.timer
sudo systemctl start credit-card-scraper.timer
```

### Render.com Scheduled Jobs
1. Go to Render dashboard
2. Create new **Scheduled Job**
3. Command: `python -m credit_card_optimizer.scraper_job`
4. Schedule: Daily at 2 AM

---

## 🔍 Monitoring

### Check Last Update
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "cards_loaded": 150,
  "rules_loaded": 500,
  "last_updated": "2024-01-15T02:00:00",
  "cache_expired": false
}
```

### Manual Refresh
```bash
curl -X POST http://localhost:8000/api/refresh
```

---

## 💡 Benefits

1. **Fast API Startup**: < 1 second (vs 2-5 minutes)
2. **No Rate Limiting**: Scrapes once per day, not per request
3. **Reliable**: Works even if scraping fails (uses cached data)
4. **Scalable**: Can handle thousands of requests
5. **Cost Effective**: Minimal API calls

---

## 🐛 Troubleshooting

### "No cards loaded" error
**Problem**: `.data/` files don't exist  
**Solution**: Run `python -m credit_card_optimizer.scraper_job` once

### "Cache expired" warning
**Problem**: Data is > 24 hours old  
**Solution**: Run scraper job to refresh

### Scraper job fails
**Problem**: Network issues, site changes  
**Solution**: 
- Check logs
- API still works with old data
- Fix scraper, then re-run job

---

## 📝 Summary

**Before**: Scrape → Parse → Serve (slow, unreliable)  
**After**: Scrape (daily) → Save → Load → Serve (fast, reliable)

**Key Point**: API never scrapes. It only loads pre-scraped data.

