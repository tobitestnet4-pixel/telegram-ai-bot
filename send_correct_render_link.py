#!/usr/bin/env python3
import asyncio
from telegram import Bot

async def send_correct_links():
    token = "8740139600:AAEGJuDz1Fcaf-STLXZlO0eeAdN9lWNY5HY"
    user_id = 8699483666
    
    msg = """
RENDER RESTART - CORRECT INSTRUCTIONS

STEP 1: Go to Render
Open in browser: https://render.com

STEP 2: Login
Click "Sign in" or "Dashboard"
Login with GitHub

STEP 3: Find Your Service
You should see: telegram-ai-bot
Click on it

STEP 4: Restart Service
Look for three dots menu (...)
Click it
Select: "Restart service"
Confirm restart

STEP 5: Watch Logs
Click "Logs" tab
Watch for deployment progress
Look for: "[BOOT] Starting polling..."

TIMING:
- Restart click: Immediate
- Rebuild: 2-3 minutes
- Bot live: Within 5 minutes

DIRECT LINKS:
https://render.com/dashboard
(Use this after login)

TEST YOUR BOT:
Send /start to your bot on Telegram
If it responds = SUCCESS!
"""
    
    try:
        bot = Bot(token=token)
        await bot.send_message(chat_id=user_id, text=msg)
        print("Correct instructions sent!")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(send_correct_links())
