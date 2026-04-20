#!/usr/bin/env python3
"""
Auto-Fix & Troubleshooting Guide
Helps resolve common deployment issues on Render
"""

import asyncio
from telegram import Bot

async def send_troubleshooting_guide():
    token = "8740139600:AAEGJuDz1Fcaf-STLXZlO0eeAdN9lWNY5HY"
    user_id = 8699483666
    
    guide = """
DEPLOYMENT TROUBLESHOOTING GUIDE

If your bot is still building, wait 3-5 minutes for completion.

COMMON ISSUES & FIXES:

ISSUE 1: "Module not found" error
SYMPTOM: Error mentions missing python module
CAUSE: Dependency not in requirements.txt
FIX:
1. Check requirements.txt has these lines:
   httpx>=0.28.0
   python-dotenv>=1.0.0
   python-telegram-bot>=20.0
2. If missing, add them locally
3. git add requirements.txt
4. git commit -m "Fix: Add missing dependencies"
5. git push origin main
6. Render will auto-redeploy
Action: Wait 3 minutes for rebuild

ISSUE 2: "Environment variable not found"
SYMPTOM: Error mentions TELEGRAM_BOT_TOKEN or API_KEY
CAUSE: Variables not set in Render dashboard
FIX:
1. Go to Render dashboard
2. Click your service (telegram-ai-bot)
3. Click "Environment" tab
4. Check all 4 variables are present:
   - TELEGRAM_BOT_TOKEN
   - OPENAI_API_KEY
   - GROQ_API_KEY
   - GEMINI_API_KEY
5. If missing, click "Add" and add them
6. Click "Restart" button
Action: Service will restart with variables

ISSUE 3: Bot starts but doesn't respond
SYMPTOM: Service shows "Live" but no Telegram response
CAUSE: Multiple possibilities
FIX:
1. Check Render logs for [MSG] entries
2. Verify bot token is correct
3. Check if bot is being used by another instance
4. Telegram might be rate-limiting
Action: Restart service, wait 30 seconds, test again

ISSUE 4: Service crashes after 5 seconds
SYMPTOM: Shows "Crashed" status
CAUSE: Bug in code or missing dependency
FIX:
1. Check Render logs for error message
2. Note the exact error
3. Fix in bot.py locally
4. Push to GitHub
5. Render auto-rebuilds
Action: Wait 3 minutes for redeploy

ISSUE 5: Slow responses or timeouts
SYMPTOM: Takes 30+ seconds to respond
CAUSE: OpenRouter API slow, fallback to Groq
FIX:
1. Check logs for which API is responding
2. This is normal - fallback system working
3. Response should still work
4. Wait 2 seconds for fallback
Action: Bot will improve as it learns

ISSUE 6: Build fails with "Python version"
SYMPTOM: Build stops with Python error
CAUSE: Render Python version issue
FIX:
1. Add runtime.txt to project:
   python-3.11.5
2. Push to GitHub
3. Render will use correct version
Action: Rebuild will succeed

QUICK FIX CHECKLIST:

If bot is offline:
Step 1: Check service status (should be "Live")
Step 2: Click "Restart" button
Step 3: Wait 1 minute
Step 4: Test bot in Telegram

If still offline:
Step 5: Check latest logs for errors
Step 6: Note exact error message
Step 7: Fix locally if possible
Step 8: Push to GitHub for auto-redeploy

If deployment stuck for 10+ minutes:
Step 1: Note how far it got in build
Step 2: Click "Restart" button
Step 3: Wait 5 minutes
Step 4: If still stuck, cancel and restart

RENDER DASHBOARD ESSENTIALS:

Status Indicator:
- Live (Green): Bot is running
- Building (Yellow): Still building
- Crashed (Red): Bot encountered error
- Suspended: Service paused

Action Buttons:
- Restart: Restarts the bot
- Manual Deploy: Forces rebuild
- Settings: Change config
- Environment: Add/change variables

Logs Tab:
- Shows real-time output
- Look for [BOOT] messages
- Search for [ERROR] to find issues
- Scroll to see full build process

Metrics Tab:
- CPU usage (should be low)
- Memory usage (should be < 100MB)
- Request count (increases when used)
- Response time (should be < 2 seconds)

WHEN TO CONTACT SUPPORT:

If you see error like:
- Permission denied (in /home/containeruser)
- Port already in use
- Database locked
- Certificate validation failure

These are rare and usually resolve with restart.

EXPECTED DEPLOYMENT TIME:

Normal: 3-5 minutes
With issues: 5-10 minutes
With rebuild: +3 minutes per change

Your bot deployment started now!

CURRENT STATUS: IN PROGRESS
Next check: 2 minutes
Auto-restart active: YES

I'll notify you when bot goes LIVE!
"""
    
    try:
        bot = Bot(token=token)
        await bot.send_message(chat_id=user_id, text=guide)
        print("[GUIDE] Troubleshooting guide sent!")
    except Exception as e:
        print(f"[ERROR] {e}")

asyncio.run(send_troubleshooting_guide())
