# Telegram AI Bot - Render Deployment Guide

Your bot is ready to deploy to Render.com for 24/7 hosting!

## Quick Deployment (5 minutes):

### 1. Go to Render Dashboard
Open https://render.com and log in with GitHub

### 2. Create New Web Service
- Click **+ New** → **Web Service**
- Select GitHub repository: `telegram-ai-bot`
- Click **Connect**

### 3. Configure Service
- **Name:** telegram-ai-bot
- **Runtime:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python bot.py`
- **Plan:** Free (sufficient for Telegram bot)

### 4. Add Environment Variables
In Render dashboard, click "Environment" and add these 4 variables:
- TELEGRAM_BOT_TOKEN (your bot token)
- OPENAI_API_KEY (OpenRouter key)
- GROQ_API_KEY (Groq key)
- GEMINI_API_KEY (Gemini key)

**Do NOT put secrets in GitHub - add them only in Render dashboard!**

### 5. Deploy
Click **Create Web Service**

Render will automatically:
- Clone your GitHub repo
- Install dependencies
- Start your bot
- Keep it running 24/7

### 6. Verify Bot is Live
- Watch the Logs tab in Render
- Look for: `[BOOT] Starting polling for messages...`
- If you see this, your bot is LIVE!

### 7. Test Your Bot
Open Telegram and send:
- `/start` → Welcome message
- `hello` → AI response
- `Bitcoin price` → Live search response

### 8. Auto-Updates
Update your bot anytime:
```powershell
git add .
git commit -m "Your changes"
git push origin main
```

Render auto-redeploys within 2 minutes!

## Your Bot Features:
- Multi-API with automatic fallback (OpenRouter → Groq → Gemini)
- Real-time web search
- Emoji-rich responses
- 24/7 uptime
- Auto-restart on crash

Your bot is production-ready! 🚀
