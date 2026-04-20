#!/usr/bin/env python3
import asyncio
from telegram import Bot

async def send_deployment_ready():
    token = "8740139600:AAEGJuDz1Fcaf-STLXZlO0eeAdN9lWNY5HY"
    user_id = 8699483666
    
    msg = """
=== READY FOR RENDER DEPLOYMENT ===

Your bot is 100% configured and ready for production!

WHAT YOU HAVE:
- v2.0 AI bot with learning system
- Multi-API support (OpenRouter, Groq, Gemini)
- Conversation memory database
- Self-improvement engine
- Real-time data access
- Production-grade code

HOW TO DEPLOY (5 MINUTES):

1. Go to https://render.com
2. Click "Sign up with GitHub"
3. Click "+ New" then "Web Service"
4. Select "telegram-ai-bot" repo
5. Fill in:
   - Name: telegram-ai-bot
   - Runtime: Python 3
   - Build: pip install -r requirements.txt
   - Start: python bot.py
   - Plan: Free

6. Click "Advanced"
7. Add 4 environment variables:
   TELEGRAM_BOT_TOKEN = [from .env]
   OPENAI_API_KEY = [from .env]
   GROQ_API_KEY = [from .env]
   GEMINI_API_KEY = [from .env]

8. Click "Create Web Service"
9. Wait 3-5 minutes for build
10. When you see "[BOOT] Starting polling..." - BOT IS LIVE!

TEST YOUR BOT:
- /start (welcome)
- hello (response)
- bitcoin price (real-time data)

DEPLOYMENT GUIDE: RENDER_LIVE_DEPLOYMENT.md

Your bot will then:
- Run 24/7 automatically
- Learn from every message
- Improve accuracy daily
- Auto-update when you push code
- Auto-restart if it crashes

STATUS: PRODUCTION READY

Repository: github.com/tobitestnet4-pixel/telegram-ai-bot

GO DEPLOY NOW AT https://render.com!
"""
    
    try:
        bot = Bot(token=token)
        await bot.send_message(chat_id=user_id, text=msg)
        print("Deployment ready message sent!")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(send_deployment_ready())
