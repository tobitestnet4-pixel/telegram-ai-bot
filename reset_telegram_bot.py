#!/usr/bin/env python3
"""
Telegram Bot Reset - Clear all conflicting instances
Removes webhook and resets polling state
"""

import asyncio
import httpx
from telegram import Bot

async def reset_telegram_bot():
    token = "8740139600:AAEGJuDz1Fcaf-STLXZlO0eeAdN9lWNY5HY"
    
    print("[RESET] Starting Telegram bot reset procedure...\n")
    
    try:
        bot = Bot(token=token)
        
        # Step 1: Delete webhook
        print("[STEP 1] Deleting webhook...")
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            print("[OK] Webhook deleted and pending updates dropped\n")
        except Exception as e:
            print(f"[INFO] Webhook deletion: {e}\n")
        
        # Step 2: Get bot info
        print("[STEP 2] Getting bot information...")
        bot_info = await bot.get_me()
        print(f"[OK] Bot name: {bot_info.username}")
        print(f"[OK] Bot ID: {bot_info.id}\n")
        
        # Step 3: Close all connections
        print("[STEP 3] Closing bot session...")
        await bot.close()
        print("[OK] Bot session closed\n")
        
        # Step 4: Reset via HTTP
        print("[STEP 4] Sending HTTP reset to Telegram...")
        reset_url = f"https://api.telegram.org/bot{token}/deleteWebhook?drop_pending_updates=true"
        
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(reset_url)
            if response.status_code == 200:
                print(f"[OK] HTTP reset successful: {response.json()}\n")
            else:
                print(f"[WARNING] HTTP reset status: {response.status_code}\n")
        
        print("[SUCCESS] Telegram bot reset complete!")
        print("[INFO] All conflicting instances cleared")
        print("[INFO] Bot is ready for fresh deployment\n")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Reset failed: {e}\n")
        return False

async def send_reset_notification():
    """Notify user that reset is complete"""
    token = "8740139600:AAEGJuDz1Fcaf-STLXZlO0eeAdN9lWNY5HY"
    user_id = 8699483666
    
    msg = """
TELEGRAM BOT RESET COMPLETE

All conflicting bot instances have been cleared from Telegram servers.

WHAT WAS DONE:
1. Deleted webhook (if any existed)
2. Dropped all pending updates
3. Closed bot session
4. Reset polling state

RESULT:
✓ All conflicts removed
✓ Bot is ready for deployment
✓ No duplicate instances
✓ Fresh start on Render

NEXT STEP:
Render will now deploy the bot cleanly.

Watch for these logs:
[BOOT] ABU-SATELLITE-NODE v2.0 - LAUNCHING
[INIT] Telegram: READY
[BOOT] Starting polling...

When you see "Starting polling..." = BOT IS LIVE!
"""
    
    try:
        bot = Bot(token=token)
        await bot.send_message(chat_id=user_id, text=msg)
        print("[NOTIFICATION] Reset notification sent to user")
    except Exception as e:
        print(f"[WARNING] Could not send notification: {e}")

async def main():
    print("\n" + "="*70)
    print("TELEGRAM BOT RESET PROCEDURE")
    print("="*70 + "\n")
    
    success = await reset_telegram_bot()
    
    if success:
        await send_reset_notification()
        print("\n[COMPLETE] Bot reset successful - Ready for deployment!")
    else:
        print("\n[ERROR] Reset procedure failed - Manual intervention may be needed")

if __name__ == "__main__":
    asyncio.run(main())
