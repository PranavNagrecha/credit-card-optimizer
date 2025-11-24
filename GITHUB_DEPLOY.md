# 🚀 Deploy to GitHub - Step by Step Guide

This guide will help you push your code to GitHub and then deploy it for free.

---

## Step 1: Create GitHub Account (if you don't have one)

1. Go to https://github.com
2. Click "Sign up"
3. Create your account (it's free!)

---

## Step 2: Create a New Repository on GitHub

1. After logging in, click the **"+"** icon in the top right
2. Click **"New repository"**
3. Fill in:
   - **Repository name**: `credit-card-optimizer` (or any name you want)
   - **Description**: "Credit card rewards optimizer API"
   - **Visibility**: Choose **Public** (free hosting requires public repo)
   - **DO NOT** check "Initialize with README" (we'll add files)
4. Click **"Create repository"**

---

## Step 3: Push Your Code to GitHub

Open Terminal (Mac) or Command Prompt (Windows) and run these commands **one by one**:

```bash
# Navigate to your project folder
cd "/Users/pranavnagrecha/Instagram Analysis /credit_card_optimizer"

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit - Credit Card Optimizer API"

# Add GitHub as remote (REPLACE YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/credit-card-optimizer.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Important:** Replace `YOUR_USERNAME` with your actual GitHub username!

**Example:** If your GitHub username is `johnsmith`, use:
```bash
git remote add origin https://github.com/johnsmith/credit-card-optimizer.git
```

---

## Step 4: Verify Code is on GitHub

1. Go to your GitHub repository page
2. You should see all your files there
3. If you see files, you're done with GitHub! ✅

---

## Step 5: Deploy for Free on Render.com

Now that your code is on GitHub, deploy it for free:

### 5.1 Sign Up for Render
1. Go to https://render.com
2. Click **"Get Started for Free"**
3. Sign up with your GitHub account (easiest way)

### 5.2 Create Web Service
1. In Render dashboard, click **"New +"** button
2. Click **"Web Service"**
3. Click **"Connect GitHub"** (if not already connected)
4. Select your repository: `credit-card-optimizer`

### 5.3 Configure Settings
Fill in these settings:

- **Name**: `credit-card-optimizer` (or any name)
- **Environment**: Select **"Python 3"**
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```
  uvicorn credit_card_optimizer.api:app --host 0.0.0.0 --port $PORT
  ```
- **Plan**: Select **"Free"**

### 5.4 Deploy
1. Scroll down and click **"Create Web Service"**
2. Wait 5-10 minutes (Render is building your app)
3. When it says "Live", your API is deployed! 🎉

### 5.5 Get Your URL
- Your API will be at: `https://your-app-name.onrender.com`
- API docs: `https://your-app-name.onrender.com/docs`
- Frontend: `https://your-app-name.onrender.com/`

---

## Step 6: Set Up Daily Scraper Job (Important!)

Your API needs fresh data. Set up automatic daily scraping:

### Option A: Render Scheduled Jobs (Easiest)
1. In Render dashboard, click **"New +"**
2. Click **"Cron Job"**
3. Configure:
   - **Name**: `scraper-job`
   - **Schedule**: `0 2 * * *` (runs daily at 2 AM)
   - **Command**: 
     ```
     python -m credit_card_optimizer.scraper_job
     ```
   - **Plan**: Free
4. Click **"Create Cron Job"**

### Option B: Manual First Run
Before the scheduled job runs, run it once manually:

1. In Render dashboard, go to your web service
2. Click **"Shell"** tab
3. Run:
   ```bash
   python -m credit_card_optimizer.scraper_job
   ```
4. Wait for it to finish (2-5 minutes)

---

## ✅ You're Done!

Your API is now:
- ✅ On GitHub
- ✅ Deployed for free on Render
- ✅ Accessible to users
- ✅ Auto-updates when you push to GitHub

---

## 🔄 Updating Your Code

Whenever you make changes:

```bash
cd "/Users/pranavnagrecha/Instagram Analysis /credit_card_optimizer"

# Add changes
git add .

# Commit changes
git commit -m "Description of your changes"

# Push to GitHub
git push
```

Render will automatically rebuild and deploy your changes!

---

## 🆘 Troubleshooting

### "Repository not found" error
- Check your GitHub username is correct
- Make sure repository exists on GitHub
- Make sure repository is public

### "Permission denied" error
- You might need to authenticate
- Try: `git push -u origin main` again
- Or use GitHub Desktop app (easier for beginners)

### Render deployment fails
- Check build logs in Render dashboard
- Make sure `requirements.txt` has all dependencies
- Check that start command is correct

### No cards loaded
- Run scraper job manually first (see Step 6)
- Check Render logs for errors

---

## 📞 Need Help?

- GitHub help: https://docs.github.com
- Render docs: https://render.com/docs
- Check your code is correct: See `QUICK_START.md`

---

## 🎯 Quick Checklist

- [ ] GitHub account created
- [ ] Repository created on GitHub
- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Web service deployed on Render
- [ ] Scraper job scheduled
- [ ] API is working (test at `/health` endpoint)

---

**That's it!** Your code is now on GitHub and deployed for free! 🎉

