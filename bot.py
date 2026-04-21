#!/usr/bin/env python3
"""
ABU-SATELLITE-NODE v3.1 - FIXED FOR RENDER
Synchronous webhook handler without rate limit issues
"""

import os
import httpx
import json
import sqlite3
import logging
from datetime import datetime
from typing import Optional
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction
from dotenv import load_dotenv
from flask import Flask, request, jsonify

load_dotenv()

# === LOGGING ===
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN') or os.getenv('TELEGRAM_BOT_TOKEN')
OPENROUTER_KEY = os.getenv('OPENROUTER_KEY') or os.getenv('OPENAI_API_KEY')
GROQ_KEY = os.getenv('GROQ_API_KEY')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
PORT = int(os.getenv('PORT', 10000))

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN required")

logger.info(f"Starting with token: {TELEGRAM_TOKEN[:30]}...")

# === DATABASE ===
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
            api_used TEXT
        )''')
        
        conn.commit()
        conn.close()
        logger.info("[DB] Initialized")
    
    def log_conversation(self, user_id, user_msg, bot_response, api_used):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO conversations 
                             (user_id, timestamp, user_message, bot_response, api_used)
                             VALUES (?, ?, ?, ?, ?)''',
                          (user_id, datetime.now().isoformat(), user_msg, bot_response, api_used))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"[DB] Error: {e}")
    
    def get_user_history(self, user_id, limit=5):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''SELECT user_message, bot_response FROM conversations 
                             WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?''',
                          (user_id, limit))
            history = cursor.fetchall()
            conn.close()
            return history
        except:
            return []

memory = BotMemory()

# === API CALLS ===
def get_openrouter_response(user_input: str, context: str) -> Optional[str]:
    if not OPENROUTER_KEY:
        return None
    try:
        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/tobitestnet4-pixel/telegram-ai-bot",
                "X-Title": "ABU-SATELLITE-NODE"
            },
            json={
                "model": "openrouter/auto",
                "messages": [
                    {"role": "system", "content": "You are ABU-SATELLITE-NODE. Provide accurate responses with emojis."},
                    {"role": "user", "content": user_input}
                ],
                "temperature": 0.7,
                "max_tokens": 800
            },
            timeout=15
        )
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result:
                return result['choices'][0]['message']['content']
    except Exception as e:
        logger.warning(f"[API] OpenRouter error: {e}")
    return None

def get_groq_response(user_input: str, context: str) -> Optional[str]:
    if not GROQ_KEY:
        return None
    try:
        response = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mixtral-8x7b-32768",
                "messages": [
                    {"role": "system", "content": "You are ABU-SATELLITE-NODE. Provide accurate responses."},
                    {"role": "user", "content": user_input}
                ],
                "temperature": 0.7,
                "max_tokens": 800
            },
            timeout=15
        )
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result:
                return result['choices'][0]['message']['content']
    except Exception as e:
        logger.warning(f"[API] Groq error: {e}")
    return None

def get_gemini_response(user_input: str, context: str) -> Optional[str]:
    if not GEMINI_KEY:
        return None
    try:
        response = httpx.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_KEY}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{
                    "parts": [{"text": f"You are ABU-SATELLITE-NODE. Respond to: {user_input}"}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 800
                }
            },
            timeout=15
        )
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        logger.warning(f"[API] Gemini error: {e}")
    return None

def get_response(user_input: str, user_id: int) -> str:
    """Get response from any available API"""
    history = memory.get_user_history(user_id)
    context = "Previous: " + " | ".join([f"Q:{q[:20]}" for q, _ in history[-2:]])
    
    # Try APIs in order
    for api_func, api_name in [
        (get_openrouter_response, "openrouter"),
        (get_groq_response, "groq"),
        (get_gemini_response, "gemini")
    ]:
        try:
            response = api_func(user_input, context)
            if response:
                memory.log_conversation(user_id, user_input, response, api_name)
                logger.info(f"[API] {api_name} responded")
                return response
        except:
            continue
    
    return "All services temporarily unavailable. Please try again."

# === FLASK APP ===
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Telegram webhook"""
    try:
        update_json = request.get_json()
        if not update_json:
            return jsonify({'ok': True}), 200
        
        # Handle message
        if 'message' in update_json:
            message = update_json['message']
            user_id = message['from']['id']
            text = message.get('text', '')
            chat_id = message['chat']['id']
            
            logger.info(f"[MSG] User {user_id}: {text[:50]}")
            
            if text.startswith('/start'):
                reply_text = "ABU-SATELLITE-NODE v3.1 LIVE! Send any query."
            else:
                reply_text = get_response(text, user_id)
            
            # Send response
            httpx.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": reply_text},
                timeout=10
            )
            
            logger.info(f"[MSG] Response sent")
        
        return jsonify({'ok': True}), 200
    
    except Exception as e:
        logger.error(f"[WEBHOOK] Error: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'version': 'v3.1'}), 200

if __name__ == '__main__':
    logger.info("\n" + "="*70)
    logger.info("[BOOT] ABU-SATELLITE-NODE v3.1 - PRODUCTION STARTUP")
    logger.info("="*70)
    logger.info("[BOOT] Configuration: OK")
    logger.info("[BOOT] Database: OK")
    logger.info("[BOOT] APIs: Ready")
    logger.info(f"[BOOT] Flask server starting on {PORT}...")
    logger.info("[BOOT] Webhook: https://telegram-ai-bot-n3sb.onrender.com/webhook")
    logger.info("[BOOT] System ready for messages")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)
