# Railway Deployment - Manual Setup Guide

Railway CLI is now installed. Follow these steps to deploy your bot:

## Step 1: Authenticate with Railway

Run this command in PowerShell:
```powershell
railway login
```

A browser window will open. Log in with your GitHub account (Tobitestnet4@gmail.com).

## Step 2: Create a New Railway Project

After login, go to https://railway.app and:
1. Click **+ New Project**
2. Select **Deploy from GitHub repo**
3. Search for `telegram-ai-bot`
4. Click **Deploy Now**

## Step 3: Add Environment Variables

In the Railway dashboard for your project:

1. Click **Variables** tab
2. Add these variables:

| Key | Value |
|-----|-------|
| TELEGRAM_BOT_TOKEN | 8740139600:AAEGJuDz1Fcaf-STLXZlO0eeAdN9lWNY5HY |
| OPENAI_API_KEY | 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 |

3. Click **Save** or **Deploy**

## Step 4: Verify Deployment

1. Go to your project logs on Railway
2. You should see: "Satellite is scanning... (Bot started)"
3. Send `/start` to your Telegram bot
4. You should see: "🚀 ABU-SATELLITE-NODE Online! 🌐"

## Step 5: Future Updates (Auto-Deploy)

Every time you update your bot:

```powershell
cd C:\Users\HP\Desktop\Telegram_AI_Project
git add .
git commit -m "Update: describe your changes"
git push origin main
```

Railway automatically redeploys within 2 minutes!

## Commands to Use

### Check Railway CLI Status
```powershell
railway status
```

### View Project Logs
```powershell
railway logs
```

### View Variables
```powershell
railway variables
```

## If You Need Help

1. Open Railway dashboard: https://railway.app
2. Select your project
3. Check the **Logs** tab for errors
4. Variables should show both TELEGRAM_BOT_TOKEN and OPENAI_API_KEY

Your bot is now ready to go live! 🚀
