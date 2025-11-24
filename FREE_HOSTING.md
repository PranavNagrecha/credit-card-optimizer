# Free Hosting Guide

This guide covers **100% FREE** ways to deploy your Credit Card Optimizer API.

## 🎯 Best Free Options (Ranked)

### 1. **Render.com** ⭐ (Easiest, GitHub Integration)
- **Free Tier**: 750 hours/month (enough for 24/7)
- **Auto-deploys from GitHub**
- **Free SSL certificate**
- **Perfect for this project**

### 2. **Railway.app** ⭐
- **Free Tier**: $5 credit/month (usually enough)
- **GitHub integration**
- **Auto-deploys**

### 3. **Fly.io**
- **Free Tier**: 3 shared VMs
- **Good performance**

### 4. **PythonAnywhere**
- **Free Tier**: Limited but works
- **Good for simple deployments**

### 5. **Your Own Hosting** (If you have cPanel/shared hosting)
- **Free** (you already pay for it)
- **Use if you have hosting**

---

## 🚀 Option 1: Render.com (RECOMMENDED)

### Step 1: Push to GitHub
```bash
cd credit_card_optimizer
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/credit-card-optimizer.git
git push -u origin main
```

### Step 2: Deploy on Render
1. Go to https://render.com and sign up (free)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your repository
5. Configure:
   - **Name**: `credit-card-optimizer` (or any name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn credit_card_optimizer.api:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
6. Click **"Create Web Service"**
7. Wait 5-10 minutes for deployment
8. Your API will be live at: `https://your-app-name.onrender.com`

### Step 3: Connect Your Domain (Optional)
1. In Render dashboard, go to **Settings**
2. Scroll to **"Custom Domain"**
3. Add your domain
4. Update DNS records as instructed

**Done!** Your API is live and free!

---

## 🚂 Option 2: Railway.app

### Step 1: Push to GitHub (same as above)

### Step 2: Deploy on Railway
1. Go to https://railway.app and sign up (free)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Select your repository
5. Railway auto-detects Python and deploys
6. If needed, set start command: `uvicorn credit_card_optimizer.api:app --host 0.0.0.0 --port $PORT`
7. Your API will be live at: `https://your-app-name.up.railway.app`

**Done!**

---

## ✈️ Option 3: Fly.io

### Step 1: Install Fly CLI
```bash
# macOS
brew install flyctl

# Or download from https://fly.io/docs/getting-started/installing-flyctl/
```

### Step 2: Create fly.toml
Create `fly.toml` in `credit_card_optimizer/`:
```toml
app = "your-app-name"
primary_region = "iad"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8080"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
  processes = ["app"]

[[http_service.checks]]
  interval = "10s"
  timeout = "2s"
  grace_period = "5s"
  method = "GET"
  path = "/health"
```

### Step 3: Deploy
```bash
flyctl launch
flyctl deploy
```

**Done!**

---

## 🐍 Option 4: PythonAnywhere

### Step 1: Sign up
1. Go to https://www.pythonanywhere.com
2. Sign up for free account

### Step 2: Upload code
1. Go to **Files** tab
2. Upload your `credit_card_optimizer` folder
3. Or use Git: `git clone https://github.com/YOUR_USERNAME/credit-card-optimizer.git`

### Step 3: Install dependencies
1. Go to **Tasks** tab
2. Create new task:
```bash
cd ~/credit-card-optimizer/credit_card_optimizer
pip3.10 install --user -r requirements.txt
```

### Step 4: Create web app
1. Go to **Web** tab
2. Click **"Add a new web app"**
3. Select **"Manual configuration"**
4. Select **Python 3.10**
5. Click **"Next"** → **"Finish"**

### Step 5: Configure WSGI
1. Click **"WSGI configuration file"**
2. Replace content with:
```python
import sys
path = '/home/YOUR_USERNAME/credit-card-optimizer'
if path not in sys.path:
    sys.path.insert(0, path)

from credit_card_optimizer.api import app as application
```

### Step 6: Reload
1. Click **"Reload"** button
2. Your API: `https://YOUR_USERNAME.pythonanywhere.com`

**Done!**

---

## 🏠 Option 5: Your Own Hosting (cPanel/Shared Hosting)

If you have hosting with cPanel or similar:

### Method A: Using Python (if available)
1. Upload files via FTP/cPanel File Manager
2. SSH into your server
3. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
4. Run with screen/tmux:
```bash
screen -S api
uvicorn credit_card_optimizer.api:app --host 0.0.0.0 --port 8000
# Press Ctrl+A then D to detach
```

### Method B: Using Passenger (if available)
1. Create `public/` folder
2. Create `public/passenger_wsgi.py`:
```python
import sys
import os
sys.path.insert(0, os.path.dirname(__file__) + '/..')
from credit_card_optimizer.api import app as application
```
3. Configure in cPanel → Passenger

---

## 🔧 Quick Fixes for Deployment

### Fix 1: Update API for Render/Railway
The API needs to use `$PORT` environment variable. Update `api.py`:

```python
# At the bottom of api.py, change:
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

### Fix 2: Create render.yaml (Optional, for Render)
Create `render.yaml` in project root:
```yaml
services:
  - type: web
    name: credit-card-optimizer
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn credit_card_optimizer.api:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: USE_CACHE
        value: true
      - key: OFFLINE_MODE
        value: false
```

### Fix 3: Create railway.json (Optional, for Railway)
Create `railway.json` in project root:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn credit_card_optimizer.api:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

## 📝 Environment Variables

Set these in your hosting platform:

- `USE_CACHE=true` - Enable caching
- `OFFLINE_MODE=false` - Allow network requests
- `PORT` - Usually auto-set by platform

---

## ✅ Testing Your Deployment

Once deployed, test:

```bash
# Health check
curl https://your-app-url.com/health

# Get recommendations
curl "https://your-app-url.com/api/recommend?query=Amazon"

# View API docs
# Visit: https://your-app-url.com/docs
```

---

## 🎯 Recommended: Render.com

**Why Render?**
- ✅ Easiest setup
- ✅ Free tier is generous
- ✅ Auto-deploys from GitHub
- ✅ Free SSL
- ✅ No credit card required
- ✅ Works perfectly for this project

**Steps Summary:**
1. Push code to GitHub
2. Sign up at Render.com
3. Connect GitHub repo
4. Deploy (takes 5-10 minutes)
5. Done!

---

## 💡 Tips

1. **Enable caching**: Set `USE_CACHE=true` to reduce API calls
2. **Use offline mode**: Pre-populate cache, then set `OFFLINE_MODE=true` for faster responses
3. **Monitor usage**: Free tiers have limits - check your platform's dashboard
4. **Custom domain**: Most platforms let you add your domain for free

---

## 🆘 Troubleshooting

### "Module not found" error
- Make sure `requirements.txt` includes all dependencies
- Check build logs in your hosting platform

### "Port already in use"
- Use `$PORT` environment variable (auto-set by platform)
- Don't hardcode port 8000

### Slow responses
- Enable caching: `USE_CACHE=true`
- Consider pre-populating cache in offline mode

### Deployment fails
- Check build logs
- Ensure Python 3.9+ is selected
- Verify all files are in repository

---

## 📞 Need Help?

- Check platform documentation
- Review build/deployment logs
- Test locally first: `python -m credit_card_optimizer.api`

