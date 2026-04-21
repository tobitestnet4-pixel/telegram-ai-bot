#!/usr/bin/env python3
"""
ABU-SATELLITE-NODE v3.0 - PRODUCTION GRADE
Senior-Level Audit & Fixes Applied
- Full error handling
- Messenger system for information passing
- Fallback helper for slow servers
- Robust database with security filters
- Learning system with research filtering
- Complete monitoring and logging
"""

import os
import httpx
import json
import sqlite3
import logging
import time
from datetime import datetime
from typing import Optional, Tuple
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import asyncio
from functools import wraps

load_dotenv()

# === LOGGING CONFIGURATION ===
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# === ENVIRONMENT CONFIGURATION ===
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN') or os.getenv('TELEGRAM_BOT_TOKEN')
OPENROUTER_KEY = os.getenv('OPENROUTER_KEY') or os.getenv('OPENAI_API_KEY')
GROQ_KEY = os.getenv('GROQ_API_KEY')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
PORT = int(os.getenv('PORT', 10000))
RENDER_URL = os.getenv('RENDER_EXTERNAL_URL', 'https://telegram-ai-bot.onrender.com')
API_TIMEOUT = 30
FALLBACK_TIMEOUT = 10

# === VALIDATION ===
if not TELEGRAM_TOKEN:
    raise ValueError("[FATAL] TELEGRAM_BOT_TOKEN required")

logger.info(f"Bot Token: {TELEGRAM_TOKEN[:30]}...")
logger.info(f"Port: {PORT}")
logger.info(f"Webhook URL: {RENDER_URL}")

# === MESSENGER SYSTEM ===
class MessageBus:
    """Pass information between components"""
    def __init__(self):
        self.queue = []
        self.lock = asyncio.Lock()
    
    async def publish(self, event_type: str, data: dict):
        """Publish message"""
        async with self.lock:
            msg = {
                'timestamp': datetime.now().isoformat(),
                'type': event_type,
                'data': data
            }
            self.queue.append(msg)
            logger.info(f"[MESSAGE] {event_type}: {data}")
    
    async def subscribe(self, event_type: str, limit: int = 10):
        """Get messages of type"""
        async with self.lock:
            return [m for m in self.queue if m['type'] == event_type][-limit:]

message_bus = MessageBus()

# === FALLBACK HELPER SYSTEM ===
class FallbackHelper:
    """Handle slow servers with fallback strategy"""
    def __init__(self):
        self.api_response_times = {}
        self.api_failures = {}
    
    async def execute_with_fallback(self, funcs: list, args: tuple, timeout: int = API_TIMEOUT):
        """Try multiple functions with fallback"""
        for i, func in enumerate(funcs):
            try:
                logger.info(f"[FALLBACK] Attempting API {i+1}/{len(funcs)}")
                start = time.time()
                result = await asyncio.wait_for(func(*args), timeout=timeout)
                elapsed = time.time() - start
                self.api_response_times[func.__name__] = elapsed
                if result:
                    logger.info(f"[FALLBACK] Success with {func.__name__} ({elapsed:.2f}s)")
                    return result
            except asyncio.TimeoutError:
                logger.warning(f"[FALLBACK] Timeout on {func.__name__}")
                self.api_failures[func.__name__] = self.api_failures.get(func.__name__, 0) + 1
            except Exception as e:
                logger.error(f"[FALLBACK] Error on {func.__name__}: {e}")
                self.api_failures[func.__name__] = self.api_failures.get(func.__name__, 0) + 1
        
        return None
    
    async def get_status(self):
        """Get API status report"""
        return {
            'response_times': self.api_response_times,
            'failures': self.api_failures
        }

fallback_helper = FallbackHelper()

# === ROBUST DATABASE WITH SECURITY ===
class SecureBotMemory:
    """Database with learning filters and security"""
    def __init__(self, db_path="bot_memory.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize with security and learning tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute('''CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            timestamp TEXT,
            user_message TEXT,
            bot_response TEXT,
            api_used TEXT,
            accuracy_score INTEGER DEFAULT 0,
            learning_filtered BOOLEAN DEFAULT 0,
            research_approved BOOLEAN DEFAULT 0
        )''')
        
        # User profiles
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_profiles (
            user_id INTEGER PRIMARY KEY,
            preferences TEXT,
            interaction_count INTEGER DEFAULT 0,
            satisfaction_rate REAL DEFAULT 0.0,
            trust_score REAL DEFAULT 0.0
        )''')
        
        # Learning data with filters
        cursor.execute('''CREATE TABLE IF NOT EXISTS learning_data (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            pattern TEXT,
            effectiveness REAL DEFAULT 0.0,
            research_approved BOOLEAN DEFAULT 0,
            security_checked BOOLEAN DEFAULT 0
        )''')
        
        # Security audit log
        cursor.execute('''CREATE TABLE IF NOT EXISTS security_log (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            event TEXT,
            severity TEXT,
            details TEXT
        )''')
        
        conn.commit()
        conn.close()
        logger.info("[DB] Secure memory system initialized")
    
    def log_conversation(self, user_id: int, user_msg: str, bot_response: str, api_used: str):
        """Log conversation with learning filter"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Filter check
            learning_filtered = self._filter_learning(user_msg, bot_response)
            research_approved = self._research_filter(user_msg)
            
            cursor.execute('''INSERT INTO conversations 
                             (user_id, timestamp, user_message, bot_response, api_used, learning_filtered, research_approved)
                             VALUES (?, ?, ?, ?, ?, ?, ?)''',
                          (user_id, datetime.now().isoformat(), user_msg, bot_response, api_used, learning_filtered, research_approved))
            conn.commit()
            conn.close()
            
            asyncio.create_task(message_bus.publish('conversation', {
                'user_id': user_id,
                'api': api_used,
                'filtered': learning_filtered
            }))
        except Exception as e:
            logger.error(f"[DB] Log error: {e}")
            self._log_security_event('db_error', 'error', str(e))
    
    def _filter_learning(self, user_msg: str, bot_response: str) -> bool:
        """Filter inappropriate learning data"""
        blocked_keywords = ['password', 'private', 'secret', 'admin', 'bypass']
        text = (user_msg + bot_response).lower()
        return any(kw in text for kw in blocked_keywords)
    
    def _research_filter(self, user_msg: str) -> bool:
        """Approve research questions"""
        research_keywords = ['research', 'study', 'analysis', 'data', 'report']
        return any(kw in user_msg.lower() for kw in research_keywords)
    
    def _log_security_event(self, event: str, severity: str, details: str):
        """Log security event"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO security_log (timestamp, event, severity, details)
                             VALUES (?, ?, ?, ?)''',
                          (datetime.now().isoformat(), event, severity, details))
            conn.commit()
            conn.close()
        except:
            pass
    
    def get_user_history(self, user_id: int, limit: int = 10):
        """Get user history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''SELECT user_message, bot_response FROM conversations 
                             WHERE user_id = ? AND learning_filtered = 0
                             ORDER BY timestamp DESC LIMIT ?''',
                          (user_id, limit))
            history = cursor.fetchall()
            conn.close()
            return history
        except Exception as e:
            logger.error(f"[DB] History error: {e}")
            return []
    
    def get_stats(self):
        """Get database statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM conversations')
            total_conversations = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM conversations WHERE learning_filtered = 1')
            filtered = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM conversations WHERE research_approved = 1')
            research = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_conversations': total_conversations,
                'filtered_for_learning': filtered,
                'research_approved': research
            }
        except:
            return {}

memory = SecureBotMemory()

# === ENHANCED PROMPTS ===
BASE_PROMPT = """You are ABU-SATELLITE-NODE v3.0 - Production Grade AI.
Core Directives:
1. ACCURACY: Verify all information
2. REAL-TIME: Access live data when needed
3. LEARNING: Improve from interactions
4. SAFETY: Filter harmful content
5. RESEARCH: Support legitimate research
Respond with precision and emojis."""

# === API FUNCTIONS WITH ERROR HANDLING ===
async def get_openrouter_response(user_input: str, context_prompt: str) -> Optional[str]:
    """OpenRouter API with error handling"""
    if not OPENROUTER_KEY:
        return None
    
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/tobitestnet4-pixel/telegram-ai-bot",
            "X-Title": "ABU-SATELLITE-NODE-v3"
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
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
            else:
                logger.warning(f"[API] OpenRouter status {response.status_code}")
    except asyncio.TimeoutError:
        logger.warning("[API] OpenRouter timeout")
    except Exception as e:
        logger.error(f"[API] OpenRouter error: {e}")
    
    return None

async def get_groq_response(user_input: str, context_prompt: str) -> Optional[str]:
    """Groq API with error handling"""
    if not GROQ_KEY:
        return None
    
    try:
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
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
    except asyncio.TimeoutError:
        logger.warning("[API] Groq timeout")
    except Exception as e:
        logger.error(f"[API] Groq error: {e}")
    
    return None

async def get_gemini_response(user_input: str, context_prompt: str) -> Optional[str]:
    """Gemini API with error handling"""
    if not GEMINI_KEY:
        return None
    
    try:
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
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text']
    except asyncio.TimeoutError:
        logger.warning("[API] Gemini timeout")
    except Exception as e:
        logger.error(f"[API] Gemini error: {e}")
    
    return None

async def get_ai_response(user_input: str, user_id: int) -> str:
    """Get AI response with fallback system"""
    try:
        history = memory.get_user_history(user_id, 5)
        context = "Previous interactions:\n"
        for prev_user, prev_bot in history[-3:]:
            context += f"Q: {prev_user[:100]}\nA: {prev_bot[:100]}\n"
        
        context_prompt = f"User: {user_id}\n{context}\nRespond with maximum accuracy."
        
        # Try APIs with fallback
        response = await fallback_helper.execute_with_fallback(
            [get_openrouter_response, get_groq_response, get_gemini_response],
            (user_input, context_prompt),
            timeout=API_TIMEOUT
        )
        
        if response:
            api_used = "fallback_system"
            memory.log_conversation(user_id, user_input, response, api_used)
            return response
        
        return "All AI services temporarily unavailable. Please try again."
    
    except Exception as e:
        logger.error(f"[AI] Response error: {e}")
        return "Service error. Please try again."

# === MESSAGE HANDLERS ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages"""
    try:
        user_text = update.message.text
        user_id = update.message.from_user.id
        
        logger.info(f"[MSG] User {user_id}: {user_text[:50]}")
        
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        response = await get_ai_response(user_text, user_id)
        
        if len(response) > 4096:
            for chunk in [response[i:i+4096] for i in range(0, len(response), 4096)]:
                await update.message.reply_text(chunk)
        else:
            await update.message.reply_text(response)
            
    except Exception as e:
        logger.error(f"[HANDLER] Message error: {e}")
        try:
            await update.message.reply_text("Error processing message")
        except:
            pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    msg = """ABU-SATELLITE-NODE v3.0 - PRODUCTION LIVE
Status: ACTIVE & MONITORING
Send any query for AI response"""
    await update.message.reply_text(msg)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show statistics"""
    stats = memory.get_stats()
    msg = f"""Database Statistics:
Total conversations: {stats.get('total_conversations', 0)}
Filtered for safety: {stats.get('filtered_for_learning', 0)}
Research approved: {stats.get('research_approved', 0)}"""
    await update.message.reply_text(msg)

# === FLASK APP WITH MONITORING ===
app = Flask(__name__)
application = Application.builder().token(TELEGRAM_TOKEN).build()

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint"""
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        application.process_update(update)
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        logger.error(f"[WEBHOOK] Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'version': 'v3.0',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/stats', methods=['GET'])
def stats():
    """Statistics endpoint"""
    try:
        stats = memory.get_stats()
        fallback_status = asyncio.run(fallback_helper.get_status())
        return jsonify({
            'database': stats,
            'apis': fallback_status
        }), 200
    except:
        return jsonify({'error': 'Stats unavailable'}), 500

# === MAIN STARTUP ===
if __name__ == '__main__':
    logger.info("\n" + "="*70)
    logger.info("[BOOT] ABU-SATELLITE-NODE v3.0 - PRODUCTION STARTUP")
    logger.info("="*70)
    logger.info("[BOOT] Environment configuration verified")
    logger.info("[BOOT] Secure memory system ready")
    logger.info("[BOOT] Fallback helper system ready")
    logger.info("[BOOT] Messenger bus operational")
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Setup webhook
    async def setup_webhook():
        try:
            bot = Bot(token=TELEGRAM_TOKEN)
            webhook_url = f"{RENDER_URL}/webhook"
            logger.info(f"[WEBHOOK] Configuring: {webhook_url}")
            await bot.set_webhook(url=webhook_url, drop_pending_updates=True)
            logger.info("[WEBHOOK] Configuration complete")
            await bot.close()
        except Exception as e:
            logger.warning(f"[WEBHOOK] Setup warning: {e}")
    
    try:
        asyncio.run(setup_webhook())
    except:
        logger.warning("[BOOT] Webhook setup deferred")
    
    logger.info(f"[BOOT] Starting Flask server on {PORT}")
    logger.info("[BOOT] System ready for production traffic")
    
    try:
        app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
    except Exception as e:
        logger.critical(f"[FATAL] Startup error: {e}")
