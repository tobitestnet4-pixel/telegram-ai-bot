# Telegram AI Bot - Cloud Deployment Guide

Your project is now ready for GitHub and cloud deployment!

## Step 1: Create GitHub Repository

1. Go to **https://github.com/new**
2. Repository name: `telegram-ai-bot`
3. Description: "ABU-SATELLITE-NODE - AI Telegram Bot with Real-time Search"
4. Choose **Private** (recommended for security)
5. Click **Create repository**

## Step 2: Push to GitHub

In PowerShell, navigate to your project:

```powershell
cd C:\Users\HP\Desktop\Telegram_AI_Project
git push -u origin main
```

When prompted, authenticate using your GitHub account (Tobitestnet4@gmail.com / tobitestnet4-pixel).

## Step 3: Deploy to Railway

Railway is the easiest free option for hosting Telegram bots.

1. Go to **https://railway.app**
2. Sign up with GitHub (use your account)
3. Click **+ New Project** → **Deploy from GitHub repo**
4. Select `telegram-ai-bot` repository
5. Configure environment variables:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
   - `OPENAI_API_KEY`: Your OpenRouter API key
6. Click **Deploy**

Railway will:
- ✅ Auto-detect Python project from Procfile
- ✅ Install dependencies from requirements.txt
- ✅ Start your bot with `python -u bot.py`
- ✅ Keep it running 24/7
- ✅ Auto-restart on crashes
- ✅ Auto-deploy on git push

## Step 4: Auto-Updates on GitHub Push

Now whenever you make changes in Visual Studio:

1. Commit and push to GitHub
2. GitHub Actions triggers deployment
3. Railway pulls the new code and restarts your bot
4. **No manual steps needed!**

## Alternative: Render.com

If Railway doesn't work, Render is similar:

1. Go to **https://render.com**
2. Sign up with GitHub
3. **New** → **Web Service** → Connect GitHub repo
4. Select `telegram-ai-bot`
5. Set Environment Variables (same as Railway)
6. Runtime: Python 3.13
7. Build command: `pip install -r requirements.txt`
8. Start command: `python -u bot.py`
9. **Create Web Service**

## Environment Variables Setup

Create a `.env.example` file with your secrets:

```
TELEGRAM_BOT_TOKEN=your_token_here
OPENAI_API_KEY=your_key_here
```

On Railway/Render, add these in the dashboard (they won't be in git).

## Monitor Your Bot

- Railway dashboard: See logs, memory usage, restart events
- Render dashboard: Similar monitoring
- Telegram: Send `/help` to verify bot is online

## Git Workflow for Future Updates

```powershell
# Make changes in Visual Studio
git add .
git commit -m "Update: Add new feature"
git push origin main
# Railway auto-deploys within 2 minutes!
```

## Troubleshooting

- **Bot not responding?** Check Railway logs for errors
- **API key invalid?** Verify in environment variables on Railway dashboard
- **Out of free tier?** Railway gives $5/month free credit, usually enough for a bot

Your bot is now deployed! 🚀
