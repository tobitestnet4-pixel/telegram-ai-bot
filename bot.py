#!/usr/bin/env python3
"""
ABU-SATELLITE-NODE v4.0 - ENTERPRISE PRODUCTION SYSTEM
Advanced Messenger System | Command Carriers | AI Division of Labor
Comprehensive Database | User AI Selection | Smart Routing
"""

import os
import httpx
import json
import sqlite3
import logging
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum
from telegram import Update, Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ChatAction, ParseMode
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import hashlib

load_dotenv()

# === LOGGING SETUP ===
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# === CONFIGURATION ===
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN') or os.getenv('TELEGRAM_BOT_TOKEN')
OPENROUTER_KEY = os.getenv('OPENROUTER_KEY') or os.getenv('OPENAI_API_KEY')
GROQ_KEY = os.getenv('GROQ_API_KEY')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
PORT = int(os.getenv('PORT', 10000))

if not TELEGRAM_TOKEN:
    raise ValueError("[FATAL] TELEGRAM_BOT_TOKEN required")

logger.info(f"System initialization: Token={TELEGRAM_TOKEN[:30]}... | Port={PORT}")

# === ENUMS ===
class AIProvider(Enum):
    GEMINI = "gemini"
    GROQ = "groq"
    OPENAI = "openai"

class QueryType(Enum):
    GENERAL = "general"
    CODING = "coding"
    RESEARCH = "research"
    ANALYSIS = "analysis"
    CREATIVE = "creative"

class MessageChannel(Enum):
    USER = "user"
    SYSTEM = "system"
    API = "api"
    DATABASE = "database"
    COMMAND = "command"

# === ADVANCED MESSENGER SYSTEM ===
class AdvancedMessenger:
    """Multi-channel messenger with event routing"""
    def __init__(self):
        self.channels = {channel.value: [] for channel in MessageChannel}
        self.subscribers = {}
        logger.info("[MESSENGER] Advanced Messenger System initialized")
    
    async def publish(self, channel: MessageChannel, message: Dict):
        """Publish to channel"""
        msg = {
            'timestamp': datetime.now().isoformat(),
            'channel': channel.value,
            'data': message
        }
        self.channels[channel.value].append(msg)
        
        # Notify subscribers
        if channel.value in self.subscribers:
            for callback in self.subscribers[channel.value]:
                await callback(msg)
        
        logger.info(f"[{channel.value.upper()}] {message}")
    
    def subscribe(self, channel: MessageChannel, callback):
        """Subscribe to channel"""
        if channel.value not in self.subscribers:
            self.subscribers[channel.value] = []
        self.subscribers[channel.value].append(callback)
    
    async def get_channel_history(self, channel: MessageChannel, limit: int = 50):
        """Get channel history"""
        return self.channels[channel.value][-limit:]

messenger = AdvancedMessenger()

# === COMMAND CARRIER SYSTEM ===
class CommandCarrier:
    """Route and execute commands"""
    def __init__(self):
        self.commands = {}
        self.command_history = []
        logger.info("[COMMANDS] Command Carrier System initialized")
    
    def register(self, name: str, handler):
        """Register command"""
        self.commands[name] = handler
        logger.info(f"[COMMANDS] Registered: /{name}")
    
    async def execute(self, command: str, user_id: int, args: List[str]):
        """Execute command"""
        if command in self.commands:
            self.command_history.append({
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'command': command,
                'args': args
            })
            return await self.commands[command](user_id, args)
        return f"Unknown command: /{command}"

command_carrier = CommandCarrier()

# === PRODUCTION DATABASE ===
class ProductionDatabase:
    """Enterprise-grade database with multiple tables and optimization"""
    def __init__(self, db_path="bot_production.db"):
        self.db_path = db_path
        self.init_db()
        logger.info("[DB] Production Database initialized")
    
    def init_db(self):
        """Initialize database with comprehensive schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            created_at TEXT,
            last_active TEXT,
            interaction_count INTEGER DEFAULT 0,
            preferred_ai TEXT DEFAULT 'gemini',
            language TEXT DEFAULT 'en'
        )''')
        
        # Conversations table
        cursor.execute('''CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            timestamp TEXT,
            query_type TEXT,
            user_message TEXT,
            ai_provider TEXT,
            bot_response TEXT,
            response_time REAL,
            user_rating INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )''')
        
        # Query analysis table
        cursor.execute('''CREATE TABLE IF NOT EXISTS query_analysis (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            timestamp TEXT,
            query TEXT,
            detected_type TEXT,
            complexity_score REAL,
            keywords TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )''')
        
        # AI performance table
        cursor.execute('''CREATE TABLE IF NOT EXISTS ai_performance (
            id INTEGER PRIMARY KEY,
            ai_provider TEXT,
            timestamp TEXT,
            response_time REAL,
            success_rate REAL,
            user_ratings TEXT,
            total_queries INTEGER
        )''')
        
        # User preferences table
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_preferences (
            user_id INTEGER PRIMARY KEY,
            preferred_ai TEXT,
            allow_ai_suggestions BOOLEAN DEFAULT 1,
            auto_select_ai BOOLEAN DEFAULT 0,
            response_format TEXT DEFAULT 'detailed',
            language TEXT DEFAULT 'en',
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )''')
        
        # Learning data table
        cursor.execute('''CREATE TABLE IF NOT EXISTS learning_data (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            timestamp TEXT,
            pattern TEXT,
            effectiveness REAL,
            category TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )''')
        
        # Command history table
        cursor.execute('''CREATE TABLE IF NOT EXISTS command_history (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            timestamp TEXT,
            command TEXT,
            status TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )''')
        
        # Create indexes for optimization
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON conversations(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON conversations(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ai_provider ON conversations(ai_provider)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_query_type ON conversations(query_type)')
        
        conn.commit()
        conn.close()
        logger.info("[DB] Schema created with indexes")
    
    def ensure_user(self, user_id: int, username: str = "", first_name: str = ""):
        """Create user if not exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        if not cursor.fetchone():
            cursor.execute('''INSERT INTO users (user_id, username, first_name, created_at, last_active)
                             VALUES (?, ?, ?, ?, ?)''',
                          (user_id, username, first_name, datetime.now().isoformat(), datetime.now().isoformat()))
            conn.commit()
        conn.close()
    
    def log_conversation(self, user_id: int, query_type: str, user_msg: str, ai_provider: str, response: str, response_time: float):
        """Log conversation"""
        self.ensure_user(user_id)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO conversations 
                         (user_id, timestamp, query_type, user_message, ai_provider, bot_response, response_time)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (user_id, datetime.now().isoformat(), query_type, user_msg, ai_provider, response, response_time))
        conn.commit()
        conn.close()
    
    def get_user_preference(self, user_id: int) -> str:
        """Get preferred AI"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT preferred_ai FROM user_preferences WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 'gemini'
    
    def set_user_preference(self, user_id: int, ai_provider: str):
        """Set preferred AI"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''INSERT OR REPLACE INTO user_preferences (user_id, preferred_ai)
                         VALUES (?, ?)''', (user_id, ai_provider))
        conn.commit()
        conn.close()
    
    def get_user_history(self, user_id: int, limit: int = 10):
        """Get user conversation history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''SELECT user_message, bot_response, ai_provider FROM conversations
                         WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?''',
                      (user_id, limit))
        history = cursor.fetchall()
        conn.close()
        return history
    
    def get_stats(self):
        """Get system statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(DISTINCT user_id) FROM users')
        total_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM conversations')
        total_conversations = cursor.fetchone()[0]
        
        cursor.execute('''SELECT ai_provider, COUNT(*) as count FROM conversations 
                         GROUP BY ai_provider''')
        ai_usage = dict(cursor.fetchall())
        
        conn.close()
        return {
            'total_users': total_users,
            'total_conversations': total_conversations,
            'ai_usage': ai_usage
        }

db = ProductionDatabase()

# === QUERY TYPE DETECTION ===
class QueryAnalyzer:
    """Detect query type and route appropriately"""
    
    @staticmethod
    def analyze(text: str) -> QueryType:
        """Analyze query type"""
        text_lower = text.lower()
        
        # Critical coding keywords
        coding_keywords = ['code', 'debug', 'error', 'function', 'class', 'algorithm', 
                         'bug', 'exception', 'syntax', 'python', 'javascript', 'java', 'c++']
        
        # Research keywords
        research_keywords = ['research', 'study', 'paper', 'analysis', 'data', 'statistics']
        
        # Analysis keywords
        analysis_keywords = ['analyze', 'compare', 'evaluate', 'pros', 'cons', 'trade-off']
        
        # Creative keywords
        creative_keywords = ['story', 'poem', 'creative', 'write', 'imagine', 'design']
        
        if any(kw in text_lower for kw in coding_keywords):
            return QueryType.CODING
        elif any(kw in text_lower for kw in research_keywords):
            return QueryType.RESEARCH
        elif any(kw in text_lower for kw in analysis_keywords):
            return QueryType.ANALYSIS
        elif any(kw in text_lower for kw in creative_keywords):
            return QueryType.CREATIVE
        else:
            return QueryType.GENERAL

# === AI DIVISION OF LABOR ===
class AIRouter:
    """Route queries to appropriate AI with smart logic"""
    
    @staticmethod
    async def get_response(user_id: int, query: str, force_ai: Optional[str] = None) -> tuple[str, str, float]:
        """Get response from appropriate AI"""
        import time
        start_time = time.time()
        
        # Get user preference or use forced AI
        preferred_ai = force_ai or db.get_user_preference(user_id)
        query_type = QueryAnalyzer.analyze(query)
        
        logger.info(f"[ROUTING] Query type: {query_type.value} | Preferred: {preferred_ai}")
        
        # Routing logic: Gemini → Groq → OpenAI (for coding)
        if query_type == QueryType.CODING:
            # Critical coding: Use OpenAI
            response = await AIRouter._get_openai_response(query)
            if response:
                elapsed = time.time() - start_time
                db.log_conversation(user_id, query_type.value, query, "openai", response, elapsed)
                return response, "openai", elapsed
        
        # Default: Gemini → Groq fallback
        response = await AIRouter._get_gemini_response(query)
        if response:
            elapsed = time.time() - start_time
            db.log_conversation(user_id, query_type.value, query, "gemini", response, elapsed)
            return response, "gemini", elapsed
        
        response = await AIRouter._get_groq_response(query)
        if response:
            elapsed = time.time() - start_time
            db.log_conversation(user_id, query_type.value, query, "groq", response, elapsed)
            return response, "groq", elapsed
        
        # Final fallback
        response = await AIRouter._get_openai_response(query)
        if response:
            elapsed = time.time() - start_time
            db.log_conversation(user_id, query_type.value, query, "openai", response, elapsed)
            return response, "openai", elapsed
        
        return "All AI services currently unavailable. Please try again.", "unavailable", time.time() - start_time
    
    @staticmethod
    async def _get_gemini_response(query: str) -> Optional[str]:
        """Gemini API call"""
        if not GEMINI_KEY:
            return None
        try:
            response = httpx.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_KEY}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": query}]}],
                    "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1000}
                },
                timeout=20
            )
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            logger.warning(f"[GEMINI] Error: {e}")
        return None
    
    @staticmethod
    async def _get_groq_response(query: str) -> Optional[str]:
        """Groq API call"""
        if not GROQ_KEY:
            return None
        try:
            response = httpx.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "mixtral-8x7b-32768",
                    "messages": [{"role": "user", "content": query}],
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=20
            )
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result:
                    return result['choices'][0]['message']['content']
        except Exception as e:
            logger.warning(f"[GROQ] Error: {e}")
        return None
    
    @staticmethod
    async def _get_openai_response(query: str) -> Optional[str]:
        """OpenAI/OpenRouter API call (for critical coding)"""
        if not OPENROUTER_KEY:
            return None
        try:
            response = httpx.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/tobitestnet4-pixel/telegram-ai-bot",
                    "X-Title": "ABU-SATELLITE-NODE-v4"
                },
                json={
                    "model": "openrouter/auto",
                    "messages": [{"role": "user", "content": query}],
                    "temperature": 0.3,
                    "max_tokens": 1000
                },
                timeout=20
            )
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result:
                    return result['choices'][0]['message']['content']
        except Exception as e:
            logger.warning(f"[OPENAI] Error: {e}")
        return None

# === COMMAND HANDLERS ===
async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    user_id = update.effective_user.id
    db.ensure_user(user_id, update.effective_user.username or "", update.effective_user.first_name or "")
    await messenger.publish(MessageChannel.COMMAND, {'command': 'start', 'user_id': user_id})
    
    msg = "ABU-SATELLITE-NODE v4.0 - ENTERPRISE AI SYSTEM\n\n"
    msg += "Features:\n"
    msg += "🤖 AI Division of Labor (Gemini→Groq→OpenAI)\n"
    msg += "🎯 Smart Query Routing\n"
    msg += "📊 Advanced Database\n"
    msg += "💬 Multi-AI Selection\n\n"
    msg += "Commands:\n"
    msg += "/start - Welcome\n"
    msg += "/stats - System statistics\n"
    msg += "/preference - Choose your AI\n"
    msg += "/help - Command guide\n"
    
    await update.message.reply_text(msg)

async def handle_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stats command"""
    stats = db.get_stats()
    msg = f"""📊 SYSTEM STATISTICS
    
Total Users: {stats['total_users']}
Total Conversations: {stats['total_conversations']}

AI Usage:
"""
    for ai, count in stats['ai_usage'].items():
        msg += f"  {ai.upper()}: {count}\n"
    
    await update.message.reply_text(msg)

async def handle_preference(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """AI preference selection"""
    user_id = update.effective_user.id
    
    keyboard = [
        [InlineKeyboardButton("🔵 Gemini", callback_data='ai_gemini'),
         InlineKeyboardButton("🟢 Groq", callback_data='ai_groq')],
        [InlineKeyboardButton("🟡 OpenAI", callback_data='ai_openai')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Choose your preferred AI for responses:",
        reply_markup=reply_markup
    )

async def handle_preference_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle AI preference selection"""
    query = update.callback_query
    user_id = query.from_user.id
    choice = query.data.split('_')[1]
    
    db.set_user_preference(user_id, choice)
    await query.answer(f"Preference set to {choice.upper()}")
    await query.edit_message_text(f"Your AI preference: {choice.upper()}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages"""
    user_id = update.effective_user.id
    text = update.message.text
    
    await update.message.chat.send_action(ChatAction.TYPING)
    
    await messenger.publish(MessageChannel.USER, {
        'user_id': user_id,
        'query': text
    })
    
    response, ai_used, response_time = await AIRouter.get_response(user_id, text)
    
    msg = f"{response}\n\n"
    msg += f"_🤖 Powered by {ai_used.upper()} ({response_time:.2f}s)_"
    
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
    
    await messenger.publish(MessageChannel.API, {
        'ai': ai_used,
        'response_time': response_time,
        'user_id': user_id
    })

# === FLASK APP ===
app = Flask(__name__)
application = Application.builder().token(TELEGRAM_TOKEN).build()

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook handler"""
    try:
        update_json = request.get_json()
        update = Update.de_json(update_json, application.bot)
        application.process_update(update)
        return jsonify({'ok': True}), 200
    except Exception as e:
        logger.error(f"[WEBHOOK] Error: {e}")
        return jsonify({'ok': False}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'version': 'v4.0'}), 200

@app.route('/stats', methods=['GET'])
def stats():
    return jsonify(db.get_stats()), 200

if __name__ == '__main__':
    logger.info("\n" + "="*70)
    logger.info("[BOOT] ABU-SATELLITE-NODE v4.0 - ENTERPRISE STARTUP")
    logger.info("="*70)
    
    # Register commands
    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(CommandHandler("stats", handle_stats))
    application.add_handler(CommandHandler("preference", handle_preference))
    application.add_handler(CallbackQueryHandler(handle_preference_callback, pattern='^ai_'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("[BOOT] Advanced Messenger: ✅")
    logger.info("[BOOT] Command Carriers: ✅")
    logger.info("[BOOT] AI Router: ✅")
    logger.info("[BOOT] Production Database: ✅")
    logger.info("[BOOT] User Preferences: ✅")
    logger.info(f"[BOOT] Starting Flask server on {PORT}...")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)
