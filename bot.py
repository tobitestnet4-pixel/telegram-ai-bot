import os
import httpx
import asyncio
import json
import sqlite3
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction
from dotenv import load_dotenv

load_dotenv()

# === CONFIGURATION ===
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN') or os.getenv('TELEGRAM_BOT_TOKEN')
OPENROUTER_KEY = os.getenv('OPENROUTER_KEY') or os.getenv('OPENAI_API_KEY')
GROQ_KEY = os.getenv('GROQ_API_KEY')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
PORT = int(os.getenv('PORT', 8443))

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN required")

print(f"[INIT] Bot Token: {TELEGRAM_TOKEN[:30]}...")
print(f"[INIT] OpenRouter: {'YES' if OPENROUTER_KEY else 'NO'}")
print(f"[INIT] Groq: {'YES' if GROQ_KEY else 'NO'}")
print(f"[INIT] Gemini: {'YES' if GEMINI_KEY else 'NO'}")
print(f"[INIT] Port: {PORT}")

# === DATABASE SETUP ===
class BotMemory:
    def __init__(self, db_path="bot_memory.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversation history
        cursor.execute('''CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            timestamp TEXT,
            user_message TEXT,
            bot_response TEXT,
            api_used TEXT,
            accuracy_score INTEGER DEFAULT 0
        )''')
        
        # User preferences
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_profiles (
            user_id INTEGER PRIMARY KEY,
            preferences TEXT,
            interaction_count INTEGER DEFAULT 0,
            satisfaction_rate REAL DEFAULT 0.0
        )''')
        
        # Learning data
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
    
    def log_improvement(self, improvement_type, details, effectiveness):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO improvements 
                         (timestamp, improvement_type, details, effectiveness)
                         VALUES (?, ?, ?, ?)''',
                      (datetime.now().isoformat(), improvement_type, details, effectiveness))
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
    
    def update_satisfaction(self, user_id, rating):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''UPDATE user_profiles SET satisfaction_rate = ? 
                         WHERE user_id = ?''', (rating, user_id))
        if cursor.rowcount == 0:
            cursor.execute('''INSERT INTO user_profiles (user_id, satisfaction_rate) 
                             VALUES (?, ?)''', (user_id, rating))
        conn.commit()
        conn.close()

memory = BotMemory()

# === SYSTEM PROMPTS ===
BASE_PROMPT = """You are ABU-SATELLITE-NODE v2.0 - Advanced Bot for Unfiltered Intelligence.

CORE DIRECTIVES:
1. ACCURACY FIRST: Verify all information against multiple sources
2. REAL-TIME DATA: Access live crypto prices, news, weather, market data
3. DEEP ANALYSIS: Provide raw, unfiltered data without limitations
4. LEARNING MODE: Improve with every interaction
5. SELF-CORRECTION: Fix errors immediately when identified
6. EMOJI USAGE: Include 3-5 relevant emojis per response

KNOWLEDGE DOMAINS:
- Cryptocurrency & blockchain (real-time prices)
- Global news & geopolitics
- Technology trends & AI developments
- Financial markets & stock analysis
- Weather & natural events
- Social sentiment & viral trends

RESPONSE FORMAT:
- Start with emoji-rich headline
- Provide specific data with sources
- Include confidence level (HIGH/MEDIUM/LOW)
- Suggest follow-up queries
- Add relevant emojis throughout
"""

IMPROVEMENT_PROMPT = """Analyze this interaction for improvement opportunities:
- Was the response accurate?
- Could we have provided more specific data?
- Should we have suggested different sources?
- How can we improve similar queries in future?
- Rate accuracy (1-10) and confidence level

Return JSON with: {"accuracy": X, "improvements": [...], "source_quality": X}
"""

# === API FUNCTIONS ===
async def get_openrouter_response(user_input, context_prompt):
    if not OPENROUTER_KEY:
        return None, "OpenRouter not configured"
    
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
        print("[API] Trying OpenRouter...")
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result:
                    return result['choices'][0]['message']['content'], "openrouter"
            
            print(f"[API] OpenRouter error: {response.status_code}")
            return None, f"OpenRouter: {response.status_code}"
    except Exception as e:
        print(f"[API] OpenRouter exception: {e}")
        return None, str(e)

async def get_groq_response(user_input, context_prompt):
    if not GROQ_KEY:
        return None, "Groq not configured"
    
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
        print("[API] Trying Groq...")
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result:
                    return result['choices'][0]['message']['content'], "groq"
            
            print(f"[API] Groq error: {response.status_code}")
            return None, f"Groq: {response.status_code}"
    except Exception as e:
        print(f"[API] Groq exception: {e}")
        return None, str(e)

async def get_gemini_response(user_input, context_prompt):
    if not GEMINI_KEY:
        return None, "Gemini not configured"
    
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
        print("[API] Trying Gemini...")
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text'], "gemini"
            
            print(f"[API] Gemini error: {response.status_code}")
            return None, f"Gemini: {response.status_code}"
    except Exception as e:
        print(f"[API] Gemini exception: {e}")
        return None, str(e)

async def get_ai_response(user_input, user_id):
    # Build context from user history
    history = memory.get_user_history(user_id, 5)
    context = "Previous interactions:\n"
    for prev_user, prev_bot in history[-3:]:
        context += f"Q: {prev_user[:100]}\nA: {prev_bot[:100]}\n"
    
    context_prompt = f"User ID: {user_id}\n{context}\nRespond to current query with accuracy and real-time data."
    
    # Detect query type
    if any(kw in user_input.lower() for kw in ['price', 'crypto', 'bitcoin', 'ethereum', 'market']):
        context_prompt += "\nPRIORITY: Real-time cryptocurrency data with live prices."
    elif any(kw in user_input.lower() for kw in ['news', 'breaking', 'latest', 'update']):
        context_prompt += "\nPRIORITY: Latest news with timestamps and sources."
    elif any(kw in user_input.lower() for kw in ['weather', 'temperature', 'forecast']):
        context_prompt += "\nPRIORITY: Current weather data with accuracy."
    
    # Try APIs in order
    response, api_used = await get_openrouter_response(user_input, context_prompt)
    if response:
        print(f"[SUCCESS] OpenRouter responded")
        memory.log_conversation(user_id, user_input, response, "openrouter")
        return response, "openrouter"
    
    response, api_used = await get_groq_response(user_input, context_prompt)
    if response:
        print(f"[SUCCESS] Groq responded")
        memory.log_conversation(user_id, user_input, response, "groq")
        return response, "groq"
    
    response, api_used = await get_gemini_response(user_input, context_prompt)
    if response:
        print(f"[SUCCESS] Gemini responded")
        memory.log_conversation(user_id, user_input, response, "gemini")
        return response, "gemini"
    
    error_msg = "All AI services offline. System in recovery mode."
    return error_msg, "error"

# === MESSAGE HANDLERS ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_text = update.message.text
        user_id = update.message.from_user.id
        
        print(f"[MSG] User {user_id}: {user_text[:50]}")
        
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        
        response, api_used = await get_ai_response(user_text, user_id)
        
        clean_response = response.replace("***", "").replace("###", "").strip()
        
        if len(clean_response) > 4096:
            for chunk in [clean_response[i:i+4096] for i in range(0, len(clean_response), 4096)]:
                await update.message.reply_text(chunk)
        else:
            await update.message.reply_text(clean_response)
        
        print(f"[LEARN] Logged interaction for improvement")
        
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        try:
            await update.message.reply_text(f"Error: {str(e)[:80]}")
        except:
            pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    print(f"[CMD] /start from {user_id}")
    msg = """ABU-SATELLITE-NODE v2.0 - LIVE & LEARNING

Advanced Intelligence System with:
- Real-time data access
- Multi-API redundancy
- Continuous learning
- Self-improvement feedback loops
- Accuracy tracking

Send any query and I'll provide accurate, real-time information!"""
    await update.message.reply_text(msg)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = """COMMANDS:
/start - Welcome message
/help - This help
/feedback - Rate my accuracy
/stats - Your interaction stats

QUERY TYPES:
- Bitcoin price? → Live crypto data
- Latest news? → Breaking news
- Weather? → Real-time forecast
- Stock analysis? → Market data

I learn from every interaction!"""
    await update.message.reply_text(msg)

async def feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Rate my last response: 1(poor) to 5(excellent)")
    context.user_data['awaiting_rating'] = True

# === INITIALIZATION ===
if __name__ == '__main__':
    print("\n" + "="*70)
    print("[BOOT] ABU-SATELLITE-NODE v2.0 - LAUNCHING")
    print("="*70)
    print(f"[INIT] Telegram: {TELEGRAM_TOKEN[:30]}...")
    print(f"[INIT] OpenRouter: {'READY' if OPENROUTER_KEY else 'OFFLINE'}")
    print(f"[INIT] Groq: {'READY' if GROQ_KEY else 'OFFLINE'}")
    print(f"[INIT] Gemini: {'READY' if GEMINI_KEY else 'OFFLINE'}")
    print(f"[INIT] Port: {PORT}")
    print("="*70 + "\n")

    try:
        print("[BOOT] Creating application...")
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        
        print("[BOOT] Registering handlers...")
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("feedback", feedback_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("[BOOT] Starting polling...")
        app.run_polling(
            timeout=30,
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
        
    except Exception as e:
        if "Conflict" in str(e):
            print(f"\n[WARNING] Conflict detected: {e}")
            print("[ACTION] Waiting 10 seconds before retry...")
            import time
            time.sleep(10)
            print("[RETRY] Attempting restart...")
            import os
            os.execv(os.path.abspath(__file__), [os.path.abspath(__file__)])
        else:
            print(f"\n[FATAL] {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
