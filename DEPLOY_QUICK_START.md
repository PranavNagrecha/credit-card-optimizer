# 🚀 Quick Deploy Guide - FREE Hosting

## Fastest Way: Render.com (5 minutes)

### 1. Push to GitHub
```bash
cd credit_card_optimizer
git init
git add .
git commit -m "Ready to deploy"
git branch -M main

# Create repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/credit-card-optimizer.git
git push -u origin main
```

### 2. Deploy on Render
1. Go to **https://render.com** → Sign up (free, no credit card)
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub → Select your repo
4. Settings:
   - **Name**: `credit-card-optimizer`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn credit_card_optimizer.api:app --host 0.0.0.0 --port $PORT`
   - **Plan**: **Free**
5. Click **"Create Web Service"**
6. Wait 5-10 minutes
7. **Done!** Your API: `https://your-app-name.onrender.com`

### 3. Test It
```bash
curl https://your-app-name.onrender.com/health
curl "https://your-app-name.onrender.com/api/recommend?query=Amazon"
```

### 4. Add Your Domain (Optional)
- Render dashboard → Settings → Custom Domain
- Add your domain
- Update DNS as instructed

---

## Alternative: Railway.app (Also Free)

1. Go to **https://railway.app** → Sign up
2. **"New Project"** → **"Deploy from GitHub"**
3. Select your repo
4. Railway auto-detects everything
5. **Done!** Your API: `https://your-app-name.up.railway.app`

---

## That's It! 🎉

Your API is now live and **100% FREE**.

- API: `https://your-app-url.com`
- Docs: `https://your-app-url.com/docs`
- Frontend: `https://your-app-url.com/` (if static files deployed)

See `FREE_HOSTING.md` for more options and details.

