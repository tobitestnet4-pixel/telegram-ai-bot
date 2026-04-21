import os
import httpx
import json
import sqlite3
from datetime import datetime
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction
from dotenv import load_dotenv
from flask import Flask, request

load_dotenv()

# === CONFIGURATION ===
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN') or os.getenv('TELEGRAM_BOT_TOKEN')
OPENROUTER_KEY = os.getenv('OPENROUTER_KEY') or os.getenv('OPENAI_API_KEY')
GROQ_KEY = os.getenv('GROQ_API_KEY')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
PORT = int(os.getenv('PORT', 10000))
RENDER_URL = os.getenv('RENDER_EXTERNAL_URL', 'https://telegram-ai-bot.onrender.com')

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN required")

print(f"[INIT] Bot Token: {TELEGRAM_TOKEN[:30]}...")
print(f"[INIT] Port: {PORT}")
print(f"[INIT] Webhook URL: {RENDER_URL}")

# === DATABASE SETUP ===
class BotMemory:
    def __init__(self, db_path="bot_memory.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            timestamp TEXT,
            user_message TEXT,
            bot_response TEXT,
            api_used TEXT,
            accuracy_score INTEGER DEFAULT 0
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_profiles (
            user_id INTEGER PRIMARY KEY,
            preferences TEXT,
            interaction_count INTEGER DEFAULT 0,
            satisfaction_rate REAL DEFAULT 0.0
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS improvements (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            improvement_type TEXT,
            details TEXT,
            effectiveness REAL DEFAULT 0.0
        )''')
        
        conn.commit()
        conn.close()
        print("[DB] Memory system initialized")
    
    def log_conversation(self, user_id, user_msg, bot_response, api_used):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO conversations 
                         (user_id, timestamp, user_message, bot_response, api_used)
                         VALUES (?, ?, ?, ?, ?)''',
                      (user_id, datetime.now().isoformat(), user_msg, bot_response, api_used))
        conn.commit()
        conn.close()
    
    def get_user_history(self, user_id, limit=10):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''SELECT user_message, bot_response FROM conversations 
                         WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?''',
                      (user_id, limit))
        history = cursor.fetchall()
        conn.close()
        return history

memory = BotMemory()

BASE_PROMPT = """You are ABU-SATELLITE-NODE v2.0 - Advanced Bot for Unfiltered Intelligence.
Provide accurate, real-time information with emojis."""

# === API FUNCTIONS ===
async def get_openrouter_response(user_input, context_prompt):
    if not OPENROUTER_KEY:
        return None
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/tobitestnet4-pixel/telegram-ai-bot",
        "X-Title": "ABU-SATELLITE-NODE"
    }
    
    data = {
        "model": "openrouter/auto",
        "messages": [
            {"role": "system", "content": BASE_PROMPT + "\n\n" + context_prompt},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result:
                    return result['choices'][0]['message']['content']
    except:
        pass
    return None

async def get_groq_response(user_input, context_prompt):
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
            {"role": "system", "content": BASE_PROMPT + "\n\n" + context_prompt},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result:
                    return result['choices'][0]['message']['content']
    except:
        pass
    return None

async def get_gemini_response(user_input, context_prompt):
    if not GEMINI_KEY:
        return None
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_KEY}"
    headers = {"Content-Type": "application/json"}
    
    data = {
        "contents": [{
            "parts": [{"text": f"{BASE_PROMPT}\n\n{context_prompt}\n\nUser: {user_input}"}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 800
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text']
    except:
        pass
    return None

async def get_ai_response(user_input, user_id):
    history = memory.get_user_history(user_id, 5)
    context = "Previous interactions:\n"
    for prev_user, prev_bot in history[-3:]:
        context += f"Q: {prev_user[:100]}\nA: {prev_bot[:100]}\n"
    
    context_prompt = f"User: {user_id}\n{context}\nRespond with accuracy."
    
    # Try APIs sequentially
    response = await get_openrouter_response(user_input, context_prompt)
    if response:
        memory.log_conversation(user_id, user_input, response, "openrouter")
        return response
    
    response = await get_groq_response(user_input, context_prompt)
    if response:
        memory.log_conversation(user_id, user_input, response, "groq")
        return response
    
    response = await get_gemini_response(user_input, context_prompt)
    if response:
        memory.log_conversation(user_id, user_input, response, "gemini")
        return response
    
    return "All services offline. Try again later."

# === MESSAGE HANDLERS ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_text = update.message.text
        user_id = update.message.from_user.id
        
        print(f"[MSG] User {user_id}: {user_text[:50]}")
        
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        response = await get_ai_response(user_text, user_id)
        
        if len(response) > 4096:
            for chunk in [response[i:i+4096] for i in range(0, len(response), 4096)]:
                await update.message.reply_text(chunk)
        else:
            await update.message.reply_text(response)
            
    except Exception as e:
        print(f"[ERROR] {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "ABU-SATELLITE-NODE v2.0 - LIVE!\n\nSend any query for AI response!"
    await update.message.reply_text(msg)

# === FLASK APP FOR WEBHOOK ===
app = Flask(__name__)
application = Application.builder().token(TELEGRAM_TOKEN).build()

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.process_update(update)
        return 'ok', 200
    except Exception as e:
        print(f"[WEBHOOK ERROR] {e}")
        return 'error', 500

@app.route('/health', methods=['GET'])
def health():
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    print("\n" + "="*70)
    print("[BOOT] ABU-SATELLITE-NODE v2.0 - WEBHOOK MODE")
    print("="*70)
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Set webhook
    import asyncio
    
    async def setup_webhook():
        bot = Bot(token=TELEGRAM_TOKEN)
        webhook_url = f"{RENDER_URL}/webhook"
        print(f"[WEBHOOK] Setting webhook: {webhook_url}")
        await bot.set_webhook(url=webhook_url, drop_pending_updates=True)
        print("[BOOT] Webhook configured - Ready for messages")
        await bot.close()
    
    try:
        asyncio.run(setup_webhook())
    except Exception as e:
        print(f"[WARNING] Webhook setup: {e}")
    
    print(f"[BOOT] Starting Flask server on port {PORT}...")
    app.run(host='0.0.0.0', port=PORT, debug=False)
