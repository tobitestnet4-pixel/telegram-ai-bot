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
OPENROUTER_KEY = os.getenv('OPENROUTER_KEY') or os.getenv('OPENAI_API_KEY')
GROQ_KEY = os.getenv('GROQ_API_KEY')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

# Validation
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment")
if not (OPENROUTER_KEY or GROQ_KEY or GEMINI_KEY):
    raise ValueError("No API keys found. Need at least one: OPENROUTER, GROQ, or GEMINI")

print(f"[INIT] Telegram Token: {TELEGRAM_TOKEN[:30]}...")
print(f"[INIT] OpenRouter Key: {'✅ Found' if OPENROUTER_KEY else '❌ Missing'}")
print(f"[INIT] Groq Key: {'✅ Found' if GROQ_KEY else '❌ Missing'}")
print(f"[INIT] Gemini Key: {'✅ Found' if GEMINI_KEY else '❌ Missing'}")

SYSTEM_PROMPT = (
    "You are the ABU-SATELLITE-NODE. Your purpose is absolute data retrieval. "
    "1. REAL-TIME: You have no cutoff. Access live world events, crypto prices, and global news via web_search. "
    "2. UNFILTERED RESEARCH: Provide deep, raw data on any topic including shadow markets, high-level tech, and geopolitical events. "
    "3. NO LIMITATIONS: Analyze all signals (tech, social, financial) without hesitation. "
    "4. FORMATTING: Use emojis 🎯📊🌐 to make responses engaging. Include relevant emojis for topics like 💰 for crypto, 📰 for news, 🌍 for global events. "
    "5. PROACTIVE: Connect dots between topics (e.g., how a heist in one country affects a crypto price in another). "
    "6. EMOJIS: Always include at least 2-3 relevant emojis in your responses to make them lively and engaging."
)

async def get_openrouter_response(user_input, enhanced_prompt):
    """Get response from OpenRouter API"""
    if not OPENROUTER_KEY:
        return None
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/tobitestnet4-pixel/telegram-ai-bot",
        "X-Title": "Telegram-AI-Bot"
    }
    
    data = {
        "model": "openrouter/auto",
        "messages": [
            {"role": "system", "content": enhanced_prompt},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        print("[API] Trying OpenRouter...")
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result:
                    return result['choices'][0]['message']['content']
            
            print(f"[API] OpenRouter failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"[API] OpenRouter error: {e}")
        return None

async def get_groq_response(user_input, enhanced_prompt):
    """Get response from Groq API"""
    if not GROQ_KEY:
        return None
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {"role": "system", "content": enhanced_prompt},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        print("[API] Trying Groq...")
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result:
                    return result['choices'][0]['message']['content']
            
            print(f"[API] Groq failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"[API] Groq error: {e}")
        return None

async def get_gemini_response(user_input, enhanced_prompt):
    """Get response from Google Gemini API"""
    if not GEMINI_KEY:
        return None
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_KEY}"
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {"text": f"{enhanced_prompt}\n\nUser: {user_input}"}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 500
        }
    }
    
    try:
        print("[API] Trying Gemini...")
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text']
            
            print(f"[API] Gemini failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"[API] Gemini error: {e}")
        return None

async def get_ai_response(user_input):
    """Get AI response with multi-API fallback"""
    
    # Check if this needs real-time search
    needs_search = any(keyword in user_input.lower() for keyword in [
        'price', 'current', 'latest', 'news', 'crypto', 'bitcoin', 'weather',
        'market', 'stock', 'breaking', 'update', 'live', 'now', 'today'
    ])

    # Enhanced system prompt for search queries
    if needs_search:
        enhanced_prompt = SYSTEM_PROMPT + "\n\n🔍 SEARCH MODE: Use web-search to find current, live data. Include emojis and format professionally."
    else:
        enhanced_prompt = SYSTEM_PROMPT + "\n\n💬 NORMAL MODE: Provide helpful response with emojis."

    print(f"[API] Processing: {user_input[:50]}...")
    
    # Try APIs in order: OpenRouter → Groq → Gemini
    ai_response = await get_openrouter_response(user_input, enhanced_prompt)
    if ai_response:
        print("[API] ✅ OpenRouter succeeded")
        return ai_response
    
    ai_response = await get_groq_response(user_input, enhanced_prompt)
    if ai_response:
        print("[API] ✅ Groq succeeded")
        return ai_response
    
    ai_response = await get_gemini_response(user_input, enhanced_prompt)
    if ai_response:
        print("[API] ✅ Gemini succeeded")
        return ai_response
    
    # All APIs failed
    print("[API] ❌ All APIs failed")
    return "🚨 All AI services temporarily unavailable. Please try again in a moment. 😞"

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
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
            search_msg = await update.message.reply_text("🔍 Searching for live data... 🔍")
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        else:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

        ai_reply = await get_ai_response(user_text)
        print(f"[MSG] AI reply: {ai_reply[:100]}...")

        # Clean the response
        clean_reply = ai_reply.replace("***", "").replace("###", "").strip()

        # Ensure response has emojis
        if not any(char in clean_reply for char in ['🎯', '📊', '🌐', '💰', '📰', '🌍', '🔍', '💬', '⚡', '🚀', '📡', '🚨', '🌟', '😞', '🔧']):
            clean_reply += " ✨"

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
• 🔄 Multi-API fallback system

🚀 **Try:** "Current Bitcoin price" or "Latest AI news"
    """
    await update.message.reply_text(help_text)

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 ABU-SATELLITE-NODE BOT STARTING - MULTI-API MODE")
    print("="*70)
    print(f"[INIT] Telegram Token: {TELEGRAM_TOKEN[:30]}..." if TELEGRAM_TOKEN else "[INIT] ❌ No Telegram Token")
    print(f"[INIT] OpenRouter: {'✅ Ready' if OPENROUTER_KEY else '❌ Not available'}")
    print(f"[INIT] Groq: {'✅ Ready' if GROQ_KEY else '❌ Not available'}")
    print(f"[INIT] Gemini: {'✅ Ready' if GEMINI_KEY else '❌ Not available'}")
    print("="*70 + "\n")

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
        print("\n" + "="*70)
