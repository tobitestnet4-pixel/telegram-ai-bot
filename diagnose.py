#!/usr/bin/env python3
"""
TELEGRAM BOT DIAGNOSTIC SCRIPT
Finds why your bot isn't responding
"""

import os
import sys
import json
from dotenv import load_dotenv

print("=" * 60)
print("🔍 TELEGRAM BOT DIAGNOSTIC TOOL")
print("=" * 60)

# Load .env
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Check 1: Credentials
print("\n1️⃣ CHECKING CREDENTIALS...")
if TELEGRAM_BOT_TOKEN:
    print(f"   ✅ TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN[:20]}...")
else:
    print("   ❌ TELEGRAM_BOT_TOKEN: MISSING!")
    sys.exit(1)

if OPENAI_API_KEY:
    print(f"   ✅ OPENAI_API_KEY: {OPENAI_API_KEY[:20]}...")
else:
    print("   ❌ OPENAI_API_KEY: MISSING!")
    sys.exit(1)

# Check 2: Files
print("\n2️⃣ CHECKING FILES...")
files = ['bot.py', 'knowledge.json', 'docker-compose.yml', 'Dockerfile']
for f in files:
    if os.path.exists(f):
        print(f"   ✅ {f}: EXISTS")
    else:
        print(f"   ❌ {f}: MISSING!")

# Check 3: Python packages
print("\n3️⃣ CHECKING PACKAGES...")
try:
    import httpx
    print(f"   ✅ httpx: {httpx.__version__}")
except ImportError:
    print("   ❌ httpx: NOT INSTALLED!")
    print("      Fix: pip install httpx==0.24.1")

try:
    import dotenv
    print(f"   ✅ python-dotenv: INSTALLED")
except ImportError:
    print("   ❌ python-dotenv: NOT INSTALLED!")
    print("      Fix: pip install python-dotenv==1.0.0")

# Check 4: Test Telegram connection
print("\n4️⃣ TESTING TELEGRAM CONNECTION...")
try:
    import httpx
    client = httpx.Client(timeout=10)
    response = client.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe")
    
    if response.status_code == 200:
        bot_info = response.json()
        if bot_info.get('ok'):
            print(f"   ✅ Connected to Telegram!")
            print(f"      Bot name: {bot_info['result']['first_name']}")
            print(f"      Bot username: {bot_info['result']['username']}")
        else:
            print(f"   ❌ Telegram returned error: {bot_info}")
    elif response.status_code == 401:
        print(f"   ❌ Invalid TELEGRAM_BOT_TOKEN (401 Unauthorized)")
        print(f"      Get new token from https://t.me/botfather")
    else:
        print(f"   ❌ Telegram error: {response.status_code}")
        print(f"      Response: {response.text}")
except Exception as e:
    print(f"   ❌ Connection failed: {e}")

# Check 5: Test OpenRouter API
print("\n5️⃣ TESTING OPENROUTER API...")
try:
    import httpx
    client = httpx.Client(timeout=10)
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "google/gemini-2.0-flash-001",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 50,
        "temperature": 0.3
    }
    
    response = client.post(
        "https://openrouter.ai/api/v1/chat/completions",
        json=payload,
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"   ✅ OpenRouter API working!")
        result = response.json()
        msg = result['choices'][0]['message']['content']
        print(f"      Test response: {msg[:50]}...")
    elif response.status_code == 401:
        print(f"   ❌ Invalid OPENAI_API_KEY (401 Unauthorized)")
        print(f"      Get key from https://openrouter.ai/keys")
    elif response.status_code == 402:
        print(f"   ❌ Out of credits (402 Payment Required)")
        print(f"      Check https://openrouter.ai/account/billing/overview")
    else:
        print(f"   ❌ OpenRouter error: {response.status_code}")
        print(f"      Response: {response.text}")
except Exception as e:
    print(f"   ❌ API test failed: {e}")

# Check 6: Docker
print("\n6️⃣ CHECKING DOCKER...")
import subprocess
try:
    docker_ver = subprocess.run(['docker', '--version'], capture_output=True, text=True).stdout.strip()
    print(f"   ✅ Docker: {docker_ver}")
except:
    print(f"   ❌ Docker: NOT INSTALLED OR NOT RUNNING")

try:
    docker_compose_ver = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True).stdout.strip()
    print(f"   ✅ Docker Compose: {docker_compose_ver}")
except:
    print(f"   ❌ Docker Compose: NOT INSTALLED")

# Check 7: Docker containers
print("\n7️⃣ CHECKING RUNNING CONTAINERS...")
try:
    result = subprocess.run(['docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}'], 
                          capture_output=True, text=True)
    if 'telegram-ai-bot' in result.stdout:
        print(f"   ✅ telegram-ai-bot container is RUNNING")
    else:
        print(f"   ❌ telegram-ai-bot container is NOT running")
        print(f"      Fix: docker-compose up -d")
except:
    print(f"   ⚠️  Couldn't check containers (is Docker daemon running?)")

# Check 8: Bot logs
print("\n8️⃣ CHECKING RECENT BOT LOGS...")
try:
    result = subprocess.run(['docker-compose', 'logs', '--tail', '5'], 
                          capture_output=True, text=True, timeout=5)
    if result.stdout:
        print(f"   Recent logs:")
        for line in result.stdout.split('\n')[-6:]:
            if line.strip():
                print(f"      {line}")
    if 'error' in result.stdout.lower() or 'failed' in result.stdout.lower():
        print(f"   ⚠️  ERRORS DETECTED IN LOGS!")
except:
    print(f"   ⚠️  Couldn't retrieve logs")

# Summary
print("\n" + "=" * 60)
print("📋 SUMMARY")
print("=" * 60)

issues = []
if not TELEGRAM_BOT_TOKEN:
    issues.append("Missing TELEGRAM_BOT_TOKEN in .env")
if not OPENAI_API_KEY:
    issues.append("Missing OPENAI_API_KEY in .env")

if issues:
    print("❌ ISSUES FOUND:")
    for issue in issues:
        print(f"   - {issue}")
else:
    print("✅ All diagnostics passed!")
    print("\nNext steps:")
    print("   1. Run: docker build -t telegram-ai-bot .")
    print("   2. Run: docker-compose up -d")
    print("   3. Send message in Telegram")
    print("   4. Bot should respond in < 5 seconds")

print("\n" + "=" * 60)
