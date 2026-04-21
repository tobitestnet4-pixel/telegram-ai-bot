#!/usr/bin/env python3
import asyncio
from telegram import Bot

async def send_restart_guide():
    token = "8740139600:AAEGJuDz1Fcaf-STLXZlO0eeAdN9lWNY5HY"
    user_id = 8699483666
    
    msg = """
RENDER DEPLOYMENT - RESTART GUIDE

The deployment was cancelled due to conflict.
Now that conflicts are cleared, restart is simple.

SOLUTION: Restart Render Deployment

Steps:
1. Go to: https://render.com/dashboard
2. Find: telegram-ai-bot service
3. Click: ... (three dots menu)
4. Select: "Restart service"
5. Wait: 2-3 minutes for rebuild

OR

Manual Deployment:
1. Go to: https://render.com/dashboard
2. Find: telegram-ai-bot service
3. Click: "Manual Deploy"
4. Select: Redeploy commit
5. Wait: 3-5 minutes for rebuild

WHAT HAPPENS:
- Code pulls from GitHub
- Dependencies install
- Bot starts fresh (no conflicts)
- Bot goes LIVE

EXPECT TO SEE:
[BOOT] Creating application...
[BOOT] Registering handlers...
[BOOT] Starting polling...

SUCCESS: When you see "Starting polling..."

TEST IMMEDIATELY:
1. Open Telegram
2. Send /start
3. Bot should respond
4. Send a message
5. Bot should reply with AI

YOUR BOT WILL BE LIVE!

Current Status: Ready to restart
Previous Conflicts: CLEARED
Solution: Click restart on Render
"""
    
    try:
        bot = Bot(token=token)
        await bot.send_message(chat_id=user_id, text=msg)
        print("Restart guide sent!")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(send_restart_guide())
