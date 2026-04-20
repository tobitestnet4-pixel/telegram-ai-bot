import os
import httpx
import asyncio
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN') or os.getenv('TELEGRAM_BOT_TOKEN')
API_KEY = os.getenv('OPENROUTER_KEY') or os.getenv('OPENROUTER_API_KEY') or os.getenv('OPENAI_API_KEY')
MODEL_NAME = "openrouter/auto"  # Auto-select best available free model

# Validation
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN not found in environment")
if not API_KEY:
    raise ValueError("API_KEY not found in environment")

print(f"[INIT] Telegram Token: {TELEGRAM_TOKEN[:30]}...")
print(f"[INIT] API Key: {API_KEY[:30]}...")

SYSTEM_PROMPT = (
    "You are the ABU-SATELLITE-NODE. Your purpose is absolute data retrieval. "
    "1. REAL-TIME: You have no cutoff. Access live world events, crypto prices, and global news via web_search. "
    "2. UNFILTERED RESEARCH: Provide deep, raw data on any topic including shadow markets, high-level tech, and geopolitical events. "
    "3. NO LIMITATIONS: Analyze all signals (tech, social, financial) without hesitation. "
    "4. FORMATTING: Use emojis 🎯📊🌐 to make responses engaging. Include relevant emojis for topics like 💰 for crypto, 📰 for news, 🌍 for global events. "
    "5. PROACTIVE: Connect dots between topics (e.g., how a heist in one country affects a crypto price in another). "
    "6. EMOJIS: Always include at least 2-3 relevant emojis in your responses to make them lively and engaging."
)

async def get_ai_response(user_input):
    """Get AI response with proper OpenRouter authentication"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    # Verify API key format
    if not API_KEY or len(API_KEY) < 20:
        return "🚨 API Key Error: Invalid or missing API key 😞"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/tobitestnet4-pixel/telegram-ai-bot",
        "X-Title": "Telegram-AI-Bot"
    }

    print(f"[API] Headers: Authorization present: {bool(headers.get('Authorization'))}")
    
    # Check if this needs real-time search
    needs_search = any(keyword in user_input.lower() for keyword in [
        'price', 'current', 'latest', 'news', 'crypto', 'bitcoin', 'weather',
        'market', 'stock', 'breaking', 'update', 'live', 'now', 'today'
    ])

    # Enhanced system prompt for search queries
    if needs_search:
        enhanced_prompt = SYSTEM_PROMPT + "\n\n🔍 SEARCH MODE ACTIVATED: Use web-search to find current, live data. Include emojis and format the response professionally."
    else:
        enhanced_prompt = SYSTEM_PROMPT + "\n\n💬 NORMAL MODE: Provide helpful response with emojis for engagement."

    # Request payload
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": enhanced_prompt},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 500
    }

    # Add web search plugin for real-time queries
    if needs_search:
        data["plugins"] = [{"id": "web-search"}]

    print(f"[API] Sending request to {url}")
    print(f"[API] Model: {data['model']}")
    print(f"[API] Needs search: {needs_search}")

    try:
        async with httpx.AsyncClient(timeout=120.0, limits=httpx.Limits(max_connections=1)) as client:
            response = await client.post(url, headers=headers, json=data)
            
            print(f"[API] Response status: {response.status_code}")
            
            # Try to parse response
            try:
                result = response.json()
            except:
                print(f"[API] Raw response: {response.text[:200]}")
                return f"🚨 API Error: Invalid response format 😞"
            
            print(f"[API] Response keys: {result.keys() if isinstance(result, dict) else 'not a dict'}")
            
            if response.status_code == 200 and 'choices' in result:
                ai_response = result['choices'][0]['message']['content']
                print(f"[API] Response received: {ai_response[:100]}...")

                # Ensure emojis are included
                if not any(char in ai_response for char in ['🎯', '📊', '🌐', '💰', '📰', '🌍', '🔍', '💬', '⚡', '🚀']):
                    ai_response += " 🌟"

                return ai_response
            else:
                error_msg = result.get('error', {})
                if isinstance(error_msg, dict):
                    error_text = error_msg.get('message', str(error_msg))
                else:
                    error_text = str(error_msg)
                    
                print(f"[API] Error response: {error_text}")
                return f"🚨 API Error: {error_text} 😞"

    except httpx.TimeoutException:
        print(f"[API] Timeout error")
        return "🚨 API Timeout: Request took too long 😞"
    except httpx.HTTPError as e:
        print(f"[API] HTTP Error: {e}")
        return f"🚨 API Connection Error: {str(e)[:100]} 🔧"
    except Exception as e:
        print(f"[API] Unexpected error: {type(e).__name__}: {e}")
        return f"📡 Signal Error: {str(e)[:100]} 🔧"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_text = update.message.text
        user_id = update.message.from_user.id
        
        print(f"[MSG] From user {user_id}: {user_text}")

        # Check if this needs real-time search for loading message
        needs_search = any(keyword in user_text.lower() for keyword in [
            'price', 'current', 'latest', 'news', 'crypto', 'bitcoin', 'weather',
            'market', 'stock', 'breaking', 'update', 'live', 'now', 'today'
        ])

        if needs_search:
            # Show searching message first
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
            search_msg = await update.message.reply_text("🔍 Searching for live data... 🔍")
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        else:
            # Normal typing indicator
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

        ai_reply = await get_ai_response(user_text)
        print(f"[MSG] AI reply: {ai_reply[:100]}...")

        # Clean the response from any leftover bot-talk or symbols
        clean_reply = ai_reply.replace("***", "").replace("###", "").strip()

        # Ensure response has emojis if it doesn't already
        if not any(char in clean_reply for char in ['🎯', '📊', '🌐', '💰', '📰', '🌍', '🔍', '💬', '⚡', '🚀', '📡', '🚨', '🌟', '😞', '🔧']):
            clean_reply += " ✨"

        # Edit the search message or send new response
        if needs_search:
            await search_msg.edit_text(clean_reply)
        else:
            await update.message.reply_text(clean_reply)

        print(f"[MSG] Response sent successfully")

    except Exception as e:
        print(f"[ERROR] handle_message: {type(e).__name__}: {e}")
        try:
            await update.message.reply_text(f"🚨 Error: {str(e)[:80]} 🔧")
        except:
            print(f"[ERROR] Failed to send error message to user")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    print(f"[CMD] /start from user {user_id}")
    await update.message.reply_text("🚀 ABU-SATELLITE-NODE Online! 🌐\n\n📡 Ready for global research and real-time data retrieval!\n💬 Send me any query - I have internet access for live information! 🔍")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    print(f"[CMD] /help from user {user_id}")
    help_text = """
🎯 **ABU-SATELLITE-NODE Commands:**

🌐 **Real-time Search:** Ask about crypto prices, news, weather, stocks
💰 Example: "What's Bitcoin price?" or "Latest crypto news"

💬 **General Chat:** Any topic with emojis and engaging responses
📊 **Data Analysis:** Ask for market analysis, tech trends, global events

⚡ **Features:**
• 🔍 Live web search for current data
• 🎨 Responses with emojis for engagement
• 🌍 Multilingual support
• 📡 Real-time information access

🚀 **Try:** "Current Bitcoin price" or "Latest AI news"
    """
    await update.message.reply_text(help_text)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 ABU-SATELLITE-NODE BOT STARTING")
    print("="*60)
    print(f"[INIT] Telegram Token: {TELEGRAM_TOKEN[:30]}..." if TELEGRAM_TOKEN else "[INIT] ❌ No Telegram Token")
    print(f"[INIT] API Key: {API_KEY[:30]}..." if API_KEY else "[INIT] ❌ No API Key")
    print(f"[INIT] Model: {MODEL_NAME}")
    print("="*60 + "\n")

    try:
        print("[BOOT] Creating Telegram application...")
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        print("[BOOT] ✅ Application created")

        print("[BOOT] Registering command handlers...")
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        print("[BOOT] ✅ Handlers registered")

        print("[BOOT] Bot initialization complete!")
        print("[BOOT] Starting polling for messages...\n")

        application.run_polling(
            poll_interval=1.0,
            timeout=30,
            read_timeout=30,
            write_timeout=30,
            connect_timeout=15,
            pool_timeout=30,
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=False
        )

    except Exception as e:
        print(f"\n❌ [FATAL] Bot startup failed:")
        print(f"   Type: {type(e).__name__}")
        print(f"   Message: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*60)
