import os
import httpx
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN') or os.getenv('TELEGRAM_BOT_TOKEN')
API_KEY = os.getenv('OPENROUTER_KEY') or os.getenv('OPENROUTER_API_KEY') or os.getenv('OPENAI_API_KEY')
MODEL_NAME = "openrouter/free"  # Free tier model

# Validation
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN not found in environment")
if not API_KEY:
    raise ValueError("OPENROUTER_KEY not found in environment")

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
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

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

    # This structure enables the "Internet Eyes" for the AI
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": enhanced_prompt},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7
    }

    # Add web search plugin for real-time queries
    if needs_search:
        data["plugins"] = [{"id": "web-search"}]

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, headers=headers, json=data)
            result = response.json()

            if response.status_code == 200 and 'choices' in result:
                ai_response = result['choices'][0]['message']['content']

                # Ensure emojis are included
                if not any(char in ai_response for char in ['🎯', '📊', '🌐', '💰', '📰', '🌍', '🔍', '💬', '⚡', '🚀']):
                    ai_response += " 🌟"

                return ai_response
            else:
                return f"🚨 API Error: {result.get('error', {}).get('message', 'Unknown error')} 😞"

        except Exception as e:
            return f"📡 Signal Error: {str(e)} 🔧"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 ABU-SATELLITE-NODE Online! 🌐\n\n📡 Ready for global research and real-time data retrieval!\n💬 Send me any query - I have internet access for live information! 🔍")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    print("Satellite is scanning... (Bot started)")
    print(f"Using model: {MODEL_NAME}")

    try:
        application = Application.builder().token(TELEGRAM_TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        print("Bot initialized successfully!")
        print("Ready for messages...")
        application.run_polling()

    except Exception as e:
        print(f"Bot failed to start: {e}")
        print("Check your environment variables")