# Deploy Your Bot - Choose Your Platform

Your GitHub repo is ready: https://github.com/tobitestnet4-pixel/telegram-ai-bot

## Option 1: Railway (Recommended - Easiest)

Click this button to deploy directly:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new?template=https%3A%2F%2Fgithub.com%2Ftobitestnet4-pixel%2Ftelegram-ai-bot&envs=TELEGRAM_BOT_TOKEN%2COPENAI_API_KEY&TELEGRAM_BOT_TOKEN=8740139600%3AAAEGJuDz1Fcaf-STLXZlO0eeAdN9lWNY5HY&OPENAI_API_KEY=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)

Or manual setup:
1. Go to https://railway.app
2. Click **+ New Project** → **Deploy from GitHub repo**
3. Select `telegram-ai-bot`
4. Environment variables will auto-fill, click **Deploy**

## Option 2: Render.com (Alternative - Also Free)

1. Go to https://render.com
2. Click **New +** → **Web Service**
3. Connect GitHub and select `telegram-ai-bot`
4. Fill in:
   - **Name:** telegram-ai-bot
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python -u bot.py`
5. Add Environment Variables:
   - `TELEGRAM_BOT_TOKEN` = `8740139600:AAEGJuDz1Fcaf-STLXZlO0eeAdN9lWNY5HY`
   - `OPENAI_API_KEY` = `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`
6. Click **Create Web Service**

## Option 3: Heroku (Free tier removed - paid only)

Heroku no longer offers free tier. Use Railway or Render instead.

## After Deployment

Your bot will be live in 2-5 minutes. Test it:
1. Open Telegram
2. Send `/start` to your bot
3. You should see: "🚀 ABU-SATELLITE-NODE Online! 🌐"

## Monitoring & Updates

**View Logs:**
- Railway: Dashboard → Logs tab
- Render: Dashboard → Logs tab

**Auto-Deploy Updates:**
```
git add .
git commit -m "Your changes"
git push origin main
```

Platform auto-redeploys within 2 minutes.

## Need Help?

- Railway support: https://railway.app/support
- Render support: https://render.com/docs
- Check GitHub: https://github.com/tobitestnet4-pixel/telegram-ai-bot
