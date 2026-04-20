#!/usr/bin/env python3
"""
TELEGRAM AI AGENT - Sarah/Kalitu
Professional production bot with self-evolution capabilities.
"""

import os
import json
import httpx
import re
import sys
import time
import subprocess
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY') or os.getenv('OPENAI_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Provider priority: 1) OpenRouter, 2) Groq, 3) Gemini
API_PROVIDERS = []
if OPENROUTER_API_KEY:
    API_PROVIDERS.append({
        'name': 'openrouter',
        'key': OPENROUTER_API_KEY,
        'base_url': 'https://openrouter.ai/api/v1',
        'model': os.getenv('OPENROUTER_MODEL', 'openrouter/free')
    })
if GROQ_API_KEY:
    API_PROVIDERS.append({
        'name': 'groq',
        'key': GROQ_API_KEY,
        'base_url': 'https://api.groq.com/openai/v1',
        'model': 'mixtral-8x7b-32768'
    })
if GEMINI_API_KEY:
    API_PROVIDERS.append({
        'name': 'gemini',
        'key': GEMINI_API_KEY,
        'base_url': 'https://generativelanguage.googleapis.com/v1beta',
        'model': 'gemini-1.5-flash'
    })

if not API_PROVIDERS:
    raise ValueError("No API keys found. Add at least one: OPENROUTER_API_KEY, GROQ_API_KEY, or GEMINI_API_KEY")

# Files
HISTORY_FILE = 'ai_memory.json'
KNOWLEDGE_FILE = 'knowledge.json'
ERROR_LOG_FILE = 'error.log'
SCRIPT_FILE = 'custom_scripts.json'

# Constants
API_TIMEOUT = 30
MAX_RETRIES = 3
MAX_TOKENS = 100
POLLING_TIMEOUT = 5  # Short polling to avoid conflicts

# Bot Identity
BOT_NAMES = ['sarah', 'kalitu']
BOT_FULL_NAMES = {
    'sarah': 'Sarah',
    'kalitu': 'Kalitu'
}

# Validation
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in .env")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in .env")

TELEGRAM_API_BASE = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}'
CLIENT = httpx.Client(timeout=API_TIMEOUT)

# ==================== LOGGING ====================
def log_error(msg, exception=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {msg}"
    if exception:
        entry += f" | {str(exception)}"
    print(f"ERROR: {entry}")
    try:
        with open(ERROR_LOG_FILE, 'a') as f:
            f.write(entry + "\n")
    except:
        pass

def log_info(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")

# ==================== DATA PERSISTENCE ====================
def load_json(filename, default_type=dict):
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
    except Exception as e:
        log_error(f"Load {filename} failed", e)
    return default_type() if default_type == dict else []

def save_json(filename, data):
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log_error(f"Save {filename} failed", e)

def load_memory():
    return load_json(HISTORY_FILE, list)

def save_memory(data):
    save_json(HISTORY_FILE, data)

def load_knowledge():
    return load_json(KNOWLEDGE_FILE, dict)

def save_knowledge(data):
    save_json(KNOWLEDGE_FILE, data)

def load_scripts():
    return load_json(SCRIPT_FILE, dict)

def save_scripts(data):
    save_json(SCRIPT_FILE, data)

# ==================== CUSTOM SCRIPTING LANGUAGE ====================
class SarahScript:
    """Simple custom scripting language for self-learning"""

    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.learned_patterns = {}

    def parse_command(self, command_text):
        """Parse a custom command definition"""
        lines = [line.strip() for line in command_text.split('\n') if line.strip()]
        if not lines:
            return None

        cmd_name = None
        cmd_pattern = None
        cmd_response = []

        for line in lines:
            if line.startswith('COMMAND:'):
                cmd_name = line.replace('COMMAND:', '').strip()
            elif line.startswith('PATTERN:'):
                cmd_pattern = line.replace('PATTERN:', '').strip()
            elif line.startswith('RESPONSE:'):
                cmd_response.append(line.replace('RESPONSE:', '').strip())
            elif cmd_response:
                cmd_response.append(line)

        if cmd_name and cmd_response:
            return {
                'name': cmd_name,
                'pattern': cmd_pattern,
                'response': '\n'.join(cmd_response),
                'created': datetime.now().isoformat()
            }
        return None

    def execute_script(self, script_name, context):
        """Execute a custom script with context"""
        scripts = load_scripts()
        if script_name not in scripts:
            return f"Script '{script_name}' not found."

        script = scripts[script_name]
        response = script['response']

        for key, value in context.items():
            response = response.replace(f'{{${key}}}', str(value))

        return response

    def learn_pattern(self, input_pattern, response_pattern):
        """Learn a new response pattern"""
        key = input_pattern.lower().strip()
        self.learned_patterns[key] = {
            'response': response_pattern,
            'learned_at': datetime.now().isoformat(),
            'usage_count': 0
        }

        # Save to knowledge base
        kb = load_knowledge()
        if 'learned_patterns' not in kb:
            kb['learned_patterns'] = {}
        kb['learned_patterns'][key] = self.learned_patterns[key]
        save_knowledge(kb)

    def match_pattern(self, user_input):
        """Find matching learned pattern"""
        input_lower = user_input.lower().strip()
        for pattern, data in self.learned_patterns.items():
            if pattern in input_lower:
                data['usage_count'] += 1
                return data['response']
        return None

    def define_function(self, name, code):
        """Define a custom function"""
        self.functions[name] = {
            'code': code,
            'created': datetime.now().isoformat()
        }

# Global script engine
SCRIPT_ENGINE = SarahScript()

def init_learned_patterns():
    """Load learned patterns from knowledge base"""
    kb = load_knowledge()
    patterns = kb.get('learned_patterns', {})
    for pattern, data in patterns.items():
        SCRIPT_ENGINE.learned_patterns[pattern] = data

    scripts = load_scripts()
    for script_name, script_data in scripts.items():
        if 'pattern' in script_data and script_data['pattern']:
            SCRIPT_ENGINE.learned_patterns[script_data['pattern'].lower()] = {
                'response': script_data['response'],
                'learned_at': script_data.get('created', datetime.now().isoformat()),
                'usage_count': script_data.get('usage_count', 0)
            }

def init_knowledge_patterns():
    """Initialize bot with essential 2026 knowledge patterns"""
    patterns = {
        "what year is it": "It's 2026, specifically April 20, 2026.",
        "current year": "The current year is 2026.",
        "what is today's date": "Today is April 20, 2026.",
        "what time is it": f"The current time is approximately {datetime.now().strftime('%H:%M')} UTC.",
    }

    for input_pattern, response in patterns.items():
        SCRIPT_ENGINE.learn_pattern(input_pattern, response)

# ==================== LANGUAGE SUPPORT ====================
LANGUAGE_CODES = {
    'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German', 'zh': 'Chinese',
    'ja': 'Japanese', 'ar': 'Arabic', 'hi': 'Hindi', 'pt': 'Portuguese', 'ru': 'Russian',
    'ko': 'Korean', 'it': 'Italian', 'nl': 'Dutch', 'tr': 'Turkish', 'pl': 'Polish',
    'sv': 'Swedish', 'da': 'Danish', 'no': 'Norwegian', 'fi': 'Finnish', 'el': 'Greek',
    'he': 'Hebrew', 'th': 'Thai', 'vi': 'Vietnamese', 'id': 'Indonesian', 'ms': 'Malay',
    'tl': 'Filipino', 'sw': 'Swahili', 'zu': 'Zulu', 'am': 'Amharic'
}

def detect_language(text):
    """Simple language detection based on character sets and common words"""
    text = text.lower()

    # Unicode block detection for non-Latin scripts
    if any(ord(char) > 0x2E00 for char in text):
        if any('\u4e00' <= char <= '\u9fff' for char in text):
            return 'zh'
        elif any('\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff' for char in text):
            return 'ja'
        elif any('\uac00' <= char <= '\ud7af' for char in text):
            return 'ko'
        elif any('\u0600' <= char <= '\u06ff' for char in text):
            return 'ar'
        elif any('\u0900' <= char <= '\u097f' for char in text):
            return 'hi'
        elif any('\u0400' <= char <= '\u04ff' for char in text):
            return 'ru'
        elif any('\u0370' <= char <= '\u03ff' for char in text):
            return 'el'
        elif any('\u0590' <= char <= '\u05ff' for char in text):
            return 'he'

    # Common word detection for European languages
    lang_words = {
        'es': ['el', 'la', 'es', 'son', 'está', 'muy', 'pero', 'qué', 'cómo'],
        'fr': ['le', 'la', 'les', 'est', 'et', 'mais', 'que', 'comment'],
        'de': ['der', 'die', 'das', 'ist', 'und', 'aber', 'wie', 'was'],
        'pt': ['o', 'a', 'é', 'está', 'mas', 'que', 'como', 'muito'],
        'it': ['il', 'la', 'è', 'sono', 'ma', 'che', 'come', 'molto'],
        'nl': ['de', 'het', 'is', 'en', 'maar', 'wat', 'hoe', 'zijn']
    }

    for lang, words in lang_words.items():
        for word in words:
            if f' {word} ' in f' {text} ':
                return lang

    return 'en'

def translate_to_english(text, source_lang):
    """Simple translation fallback for common phrases"""
    if source_lang == 'en':
        return text

    common_translations = {
        'es': {'hola': 'hello', 'adiós': 'goodbye', 'gracias': 'thank you'},
        'fr': {'bonjour': 'hello', 'merci': 'thank you'},
        'de': {'hallo': 'hello', 'danke': 'thank you'}
    }

    if source_lang in common_translations:
        for native, english in common_translations[source_lang].items():
            text = text.replace(native, english)

    return text

# ==================== AI RESPONSE ENGINE ====================
def get_offline_response(user_input):
    """Generate offline response when API fails"""
    import random

    offline_responses = {
        'hello': ['Hello! How can I help you today?', 'Hi there! What can I do for you?'],
        'how are you': ['I\'m doing well, thank you!', 'I\'m great! How about you?'],
        'what is your name': ['I\'m Sarah! You can also call me Kalitu.'],
        'time': [f'Current time is approximately {datetime.now().strftime("%H:%M")} UTC.'],
        'date': [f'Today is {datetime.now().strftime("%B %d, %Y")}.'],
    }

    user_lower = user_input.lower()

    # Check learned patterns first
    learned = SCRIPT_ENGINE.match_pattern(user_input)
    if learned:
        return learned

    # Match basic patterns
    for pattern, responses in offline_responses.items():
        if pattern in user_lower:
            return random.choice(responses)

    return "I'm currently operating in offline mode due to API limitations. I can still use my learned behaviors and basic functions. Try teaching me with /learn."

def get_ai_response(user_input, system_prompt=None, use_web_search=False):
    """Get AI response with multi-provider fallback"""
    try:
        memory = load_memory()
        knowledge = load_knowledge()

        base_system = system_prompt or """You are Sarah, an intelligent AI assistant operating in 2026.

IMPORTANT: Current year is 2026. All responses should reflect 2026 knowledge.
You have access to real-time information and current events.

RESPONSE STYLE: Write clearly in clean paragraphs - no excessive formatting.
Be helpful, accurate, and conversational."""

        messages = [{"role": "system", "content": base_system}]

        for entry in memory[-5:]:
            if isinstance(entry, dict) and 'q' in entry and 'a' in entry:
                messages.append({"role": "user", "content": entry['q']})
                messages.append({"role": "assistant", "content": entry['a']})

        messages.append({"role": "user", "content": user_input})

        # Try each provider in order
        last_error = None
        for provider in API_PROVIDERS:
            try:
                log_info(f"Trying {provider['name']}...")

                payload = {
                    "model": provider['model'],
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": MAX_TOKENS
                }

                headers = {
                    "Authorization": f"Bearer {provider['key']}",
                    "Content-Type": "application/json"
                }

                response = CLIENT.post(
                    f"{provider['base_url']}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=API_TIMEOUT
                )

                if response.status_code == 200:
                    data = response.json()
                    ai_text = data['choices'][0]['message']['content']

                    # Save successful provider
                    kb = load_knowledge()
                    kb['last_provider'] = provider['name']
                    save_knowledge(kb)

                    # Cache response
                    memory.append({
                        "q": user_input,
                        "a": ai_text,
                        "timestamp": datetime.now().isoformat()
                    })
                    save_memory(memory)

                    log_info(f"Success with {provider['name']}")
                    return ai_text
                else:
                    log_error(f"{provider['name']} failed: {response.status_code}")
                    last_error = f"{provider['name']}: {response.status_code}"

            except Exception as e:
                log_error(f"{provider['name']} exception", e)
                last_error = str(e)
                continue

        # All providers failed
        log_error(f"All providers failed. Last error: {last_error}")
        return get_offline_response(user_input)

    except Exception as e:
        log_error(f"AI response failed", e)
        return get_offline_response(user_input)

# ==================== TELEGRAM HANDLERS ====================
def send_message(chat_id, text):
    """Send message to Telegram"""
    try:
        response = CLIENT.post(
            f"{TELEGRAM_API_BASE}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=API_TIMEOUT
        )
        return response.status_code == 200
    except Exception as e:
        log_error("Send message failed", e)
        return False

def send_photo(chat_id, photo_url, caption=None):
    """Send photo to Telegram"""
    try:
        payload = {"chat_id": chat_id, "photo": photo_url}
        if caption:
            payload["caption"] = caption
        response = CLIENT.post(
            f"{TELEGRAM_API_BASE}/sendPhoto",
            json=payload,
            timeout=60
        )
        return response.status_code == 200
    except Exception as e:
        log_error("Send photo failed", e)
        return False

def generate_image(prompt):
    """Generate image using Flux model"""
    try:
        log_info(f"Generating image: {prompt[:50]}...")

        payload = {
            "model": "black-forest-labs/flux-schnell",
            "prompt": prompt,
            "num_images": 1
        }

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        response = CLIENT.post(
            "https://openrouter.ai/api/v1/images/generations",
            json=payload,
            headers=headers,
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            return data['data'][0]['url']
        else:
            log_error(f"Image generation failed: {response.status_code}")
            return None

    except Exception as e:
        log_error("Image generation error", e)
        return None

def detect_bot_name(text):
    """Detect if user mentioned bot's name"""
    text_lower = text.lower()
    text_clean = text_lower.replace('@', ' ')

    for name in BOT_NAMES:
        pattern = r'\b' + name + r'\b'
        if re.search(pattern, text_lower) or re.search(pattern, text_clean):
            return True, name
    return False, None

def create_personality_prompt(user_input, detected_name=None):
    """Create enhanced personality prompt for AI responses"""
    base_prompt = """You are Sarah, a highly knowledgeable AI assistant operating in 2026.

IMPORTANT: You must always remember that the current year is 2026. All your responses should reflect 2026 knowledge and context. Never mention or imply any year before 2026 in your responses.

PERSONALITY:
- Professional yet friendly
- Extremely knowledgeable about 2026 developments
- Clear and concise communication
- Helpful and proactive
- Honest about capabilities
- Uses clean, paragraph-based formatting

CURRENT 2026 CONTEXT:
- AI governance is established globally
- Quantum computing is commercially available
- Space exploration includes Mars missions
- Neural interfaces are emerging technology
- Universal basic income trials are active
- Climate change solutions are working"""

    if detected_name:
        name_context = f"\n\nThe user has addressed you as {detected_name}. Acknowledge this warmly but personally."
        base_prompt += name_context

    return base_prompt

# ==================== MESSAGE HANDLER ====================
def handle_message(message_data):
    """Handle incoming Telegram message"""
    try:
        chat_id = message_data.get('chat', {}).get('id')
        user_text = message_data.get('text', '').strip()
        user_id = message_data.get('from', {}).get('id')

        if not chat_id or not user_text:
            return

        detected_lang = detect_language(user_text)
        translated_text = translate_to_english(user_text, detected_lang) if detected_lang != 'en' else user_text

        user_lower = translated_text.lower()
        log_info(f"Message from {user_id}: {user_text[:50]}... (lang: {detected_lang})")

        # Commands
        if user_text.startswith('/stats'):
            kb = load_knowledge()
            scripts = load_scripts()
            patterns = kb.get('learned_patterns', {})
            stats = f"""Bot Statistics:
Messages: {kb.get('messages_processed', 0)}
Custom Scripts: {len(scripts)}
Learned Patterns: {len(patterns)}"""
            send_message(chat_id, stats)
            return

        if user_text.startswith('/learn'):
            learn_text = user_text.replace('/learn', '').strip()
            if ' -> ' in learn_text:
                input_pattern, response_pattern = learn_text.split(' -> ', 1)
                SCRIPT_ENGINE.learn_pattern(input_pattern.strip(), response_pattern.strip())
                send_message(chat_id, f"Learned: '{input_pattern}' -> '{response_pattern}'")
            else:
                send_message(chat_id, "Usage: /learn [pattern] -> [response]")
            return

        if user_text.startswith('/scripts'):
            scripts = load_scripts()
            script_list = "\n".join([f"- {name}" for name in scripts.keys()]) if scripts else "No scripts yet."
            send_message(chat_id, f"Custom Scripts:\n{script_list}")
            return

        if user_text.startswith('/run'):
            script_name = user_text.replace('/run', '').strip()
            if script_name:
                context = {'user': str(user_id), 'time': datetime.now().strftime("%H:%M")}
                result = SCRIPT_ENGINE.execute_script(script_name, context)
                send_message(chat_id, result)
            else:
                send_message(chat_id, "Usage: /run [script_name]")
            return

        if user_text.startswith('/define'):
            send_message(chat_id, "Use /learn to teach patterns instead. /define is deprecated.")
            return

        if user_text.startswith('/upgrade'):
            feature = user_text.replace('/upgrade', '').strip()
            if feature:
                send_message(chat_id, f"Upgrade feature '{feature}' noted. Currently upgrading is limited to learning via /learn.")
            else:
                send_message(chat_id, "Usage: /upgrade [feature_description]")
            return

        # Check learned patterns
        learned_response = SCRIPT_ENGINE.match_pattern(user_text)
        if learned_response:
            send_message(chat_id, learned_response)
            return

        # Name recognition
        if any(p in user_lower for p in ['what is your name', "what's your name", 'who are you']):
            send_message(chat_id, "I'm Sarah! You can also call me Kalitu. I'm an AI assistant powered by OpenRouter, operating in 2026.")
            return

        # Image generation
        if any(k in user_lower for k in ['draw', 'generate image', 'create image']):
            prompt = user_text
            for kw in ['draw', 'generate image', 'create image', 'make image']:
                prompt = prompt.replace(kw, '').strip()
            if prompt:
                send_message(chat_id, f"Creating image: {prompt}...")
                img_url = generate_image(prompt)
                if img_url:
                    send_photo(chat_id, img_url, f"Image: {prompt}")
                else:
                    send_message(chat_id, "Could not generate image. Try a different prompt.")
            return

        # Detect bot name mention
        is_name_mentioned, detected_name = detect_bot_name(user_text)

        # Create system prompt
        personality_prompt = create_personality_prompt(user_text, detected_name)

        # Get AI response
        needs_web_search = any(kw in user_lower for kw in ['current', 'latest', 'news', 'recent', 'today', 'what happened', '2026'])
        response = get_ai_response(user_text, personality_prompt, use_web_search=needs_web_search)

        # Update stats
        kb = load_knowledge()
        kb['messages_processed'] = kb.get('messages_processed', 0) + 1
        save_knowledge(kb)

        # Send response
        send_message(chat_id, response)

    except Exception as e:
        log_error("Message handling failed", e)

# ==================== POLLING ====================
def poll_telegram():
    """Poll Telegram for new messages with robust error handling"""
    offset = 0
    consecutive_errors = 0

    log_info("Bot starting polling...")

    # Give Telegram a moment to clear any stale connections
    time.sleep(5)

    while True:
        try:
            log_info(f"Polling with offset={offset}, timeout={POLLING_TIMEOUT}")

            response = CLIENT.post(
                f"{TELEGRAM_API_BASE}/getUpdates",
                json={"offset": offset, "timeout": POLLING_TIMEOUT, "limit": 100},
                timeout=POLLING_TIMEOUT + 5
            )

            log_info(f"Poll response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    consecutive_errors = 0
                    updates = data.get('result', [])
                    log_info(f"Received {len(updates)} updates")

                    for update in updates:
                        offset = update['update_id'] + 1
                        if 'message' in update:
                            handle_message(update['message'])
                else:
                    log_error(f"Telegram API error: {data}")
                    consecutive_errors += 1
            elif response.status_code == 409:
                log_error("409 CONFLICT - Another getUpdates request detected. Clearing offset and retrying...")
                offset = 0
                time.sleep(10)  # Wait longer on conflict
                consecutive_errors += 1
            else:
                log_error(f"HTTP error {response.status_code}: {response.text[:200]}")
                consecutive_errors += 1

        except httpx.ReadTimeout:
            log_info("Poll timeout - no updates, continuing...")
            consecutive_errors = 0
        except Exception as e:
            consecutive_errors += 1
            log_error(f"Polling exception: {type(e).__name__}", e)

            if consecutive_errors >= 10:
                log_info("Too many errors. Waiting 60 seconds...")
                time.sleep(60)
                consecutive_errors = 0
            else:
                time.sleep(5)

        # Brief pause between polls to avoid overwhelming API
        time.sleep(1)

# ==================== MAIN ====================
if __name__ == "__main__":
    log_info("Sarah/Kalitu Bot starting...")
    time.sleep(2)  # Stabilization delay

    # Initialize knowledge
    kb = load_knowledge()
    if 'messages_processed' not in kb:
        kb['messages_processed'] = 0
        kb['completed_upgrades'] = []
        kb['learned_patterns'] = {}
        save_knowledge(kb)

    # Initialize systems
    try:
        init_learned_patterns()
        init_knowledge_patterns()
        log_info("Knowledge systems initialized.")
    except Exception as e:
        log_error("Failed to initialize knowledge", e)

    log_info("Bot ready. Waiting for messages...")
    log_info("Commands: /stats, /learn, /scripts, /run, /upgrade")

    try:
        poll_telegram()
    except KeyboardInterrupt:
        log_info("Bot shutdown by user.")
    except Exception as e:
        log_error("Critical error in main loop", e)
        time.sleep(30)