#!/usr/bin/env python3
"""
Quick test script for Telegram bot
"""

import os
import asyncio
from telegram import Bot

async def test_bot():
    token = "8740139600:AAEGJuDz1Fcaf-STLXZlO0eeAdN9lWNY5HY"
    chat_id = "8699483666"

    try:
        bot = Bot(token=token)
        print("Bot created successfully")

        # Test sending a message
        result = await bot.send_message(chat_id=chat_id, text="🤖 Bot test message! 🎯")
        print(f"Message sent successfully: {result.message_id}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_bot())