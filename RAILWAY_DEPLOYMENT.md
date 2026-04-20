# Deploy Your Telegram Bot to Railway

Your code is now on GitHub: https://github.com/tobitestnet4-pixel/telegram-ai-bot

## Step 1: Deploy to Railway (1 minute)

1. Go to **https://railway.app**
2. Sign up with GitHub (click "Deploy with GitHub")
3. After login, click **+ New Project**
4. Select **Deploy from GitHub repo**
5. Find and select `telegram-ai-bot`
6. Click **Deploy Now**

## Step 2: Add Environment Variables

Railway will ask for environment variables. Fill in:

- **TELEGRAM_BOT_TOKEN**: `8740139600:AAEGJuDz1Fcaf-STLXZlO0eeAdN9lWNY5HY`
- **OPENAI_API_KEY**: `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`

Click **Save** and Railway will auto-deploy.

## Step 3: Verify Your Bot is Live

1. Open your Telegram app
2. Send `/start` to your bot
3. You should see: "🚀 ABU-SATELLITE-NODE Online! 🌐"

Your bot is now running 24/7 on Railway! 🎉

## Future Updates (Auto-Deploy)

Whenever you update `bot.py` or other files in Visual Studio:

```
git add .
git commit -m "Update: description of change"
git push origin main
```

Railway will automatically rebuild and deploy within 2 minutes.

## Monitor Logs on Railway

- Go to https://railway.app
- Select your project
- Click "Logs" to see real-time bot messages
- Check for errors or issues

## If Bot Goes Offline

Railway restarts crashed bots automatically. Check:
1. Railway dashboard logs for errors
2. Verify environment variables are correct
3. Make sure your bot token is still valid

Done! Your bot is now live and automatically deployed. 🚀
