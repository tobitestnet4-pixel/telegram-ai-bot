#!/usr/bin/env python3
"""
Render Webhook Configuration Fix
Ensures bot uses polling instead of webhook for better compatibility
"""

import os

# Read current bot.py
with open("C:\\Users\\HP\\Desktop\\Telegram_AI_Project\\bot.py", "r") as f:
    bot_code = f.read()

# Check if it's using webhook or polling
if "run_polling" in bot_code:
    print("[OK] Bot is configured for polling - Good!")
else:
    print("[WARNING] Bot might be using webhook mode")

# Ensure proper polling configuration
if "allowed_updates=['message']" in bot_code:
    print("[OK] Message updates configured")
    
    # This is the issue - too restrictive
    print("[FIX] Changing allowed_updates to be less restrictive...")
    
    bot_code = bot_code.replace(
        "allowed_updates=['message']",
        "allowed_updates=Update.ALL_TYPES"
    )
    
    with open("C:\\Users\\HP\\Desktop\\Telegram_AI_Project\\bot.py", "w") as f:
        f.write(bot_code)
    
    print("[SUCCESS] Updated bot.py for better compatibility")
else:
    print("[OK] Update configuration is flexible")

print("\n[RECOMMENDATION] Bot should:")
print("✓ Use polling (not webhook)")
print("✓ Accept all update types")
print("✓ Have error handling for connection issues")
print("✓ Auto-retry on failures")
