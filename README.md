# 🤖 Sarah AI Bot - 2026 Self-Evolving Telegram Agent

![Status](https://img.shields.io/badge/status-production--ready-green)
![Version](https://img.shields.io/badge/version-2026.4.20-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**A 24/7 cloud-hosted Telegram AI bot with self-evolution capabilities, powered by 2026's latest OpenRouter models.**

## 🚀 Quick Start (2 minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your tokens

# 3. Run locally
python bot.py

# 4. Deploy to cloud (optional)
docker-compose up -d
```

## ✨ Key Features

- **🧠 Self-Learning**: Learns from conversations, patterns, and user feedback
- **🔄 Self-Evolution**: `/upgrade` command researches and implements improvements
- **🌍 Multilingual**: Supports 30+ languages with automatic detection
- **🔍 Real-time Web Search**: Automatic search for live prices, news, and current data
- **🎨 Image Generation**: Create images with AI
- **☁️ Cloud Ready**: Deploy to Railway, Heroku, or any Docker platform
- **🛡️ Error Resilient**: Graceful handling of API limits and network issues

## 📋 Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/stats` | View bot statistics and performance | `/stats` |
| `/search [query]` | Search across multiple web engines | `/search latest AI news 2026` |
| `/learn [pattern] -> [response]` | Teach the bot response patterns | `/learn hello -> Hi there!` |
| `/define [script]` | Create custom command scripts | `/define greeting` |
| `/run [script]` | Execute learned scripts | `/run greeting` |
| `/upgrade [feature]` | Research and implement new features | `/upgrade add weather command` |
| `/restart` | Restart bot (admin only, confirmation required) | `/restart confirm` |

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Required
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENROUTER_API_KEY=sk-or-v1-your_openrouter_key_here

# Optional
OPENROUTER_MODEL=google/gemini-2.0-flash-thinking-exp:free  # Tool-enabled model for real-time data
```

### Data Files
- `knowledge.json` - Bot's learned knowledge and statistics
- `ai_memory.json` - Conversation history
- `custom_scripts.json` - User-defined scripts and patterns

## 🏗️ Architecture

```
Telegram Bot (Sarah)
├── 🤖 AI Engine (OpenRouter API)
│   ├── Free models (unlimited)
│   ├── Web search integration
│   └── Multi-language support
├── 🧠 Learning System
│   ├── Pattern recognition
│   ├── Script execution
│   └── Knowledge persistence
└── ☁️ Cloud Deployment
    ├── Docker container
    ├── Auto-restart
    └── 24/7 uptime
```

## 🚀 Deployment Options

### Railway (Recommended - 5 minutes)
```bash
# 1. Connect GitHub repo to Railway
# 2. Set environment variables
# 3. Deploy automatically
railway up
```

### Docker (Universal)
```bash
# Build and run
docker-compose build
docker-compose up -d

# Check status
docker-compose logs -f
```

### Manual Python
```bash
# Run directly
python bot.py
```

## 🔍 Troubleshooting

### Bot Not Responding?
```bash
# Check environment
docker exec sarah-ai-bot env | grep -E "(TELEGRAM|OPENROUTER)"

# Test API connection
docker exec sarah-ai-bot python -c "
import httpx
response = httpx.get('https://api.telegram.org/bot{YOUR_TOKEN}/getMe')
print('Telegram:', response.status_code)
"
```

### API Issues?
- **402 Error**: Credits exhausted → Bot automatically uses free models
- **401 Error**: Invalid API key → Check `.env` file
- **Network**: Connection issues → Bot falls back to offline mode

### Common Issues
- **"Offline mode"**: API temporarily unavailable, bot uses learned patterns
- **No responses**: Check Telegram bot token and permissions
- **Slow responses**: Free models may be slower than premium ones

## 📊 Performance

- **Response Time**: 2-8 seconds (depends on model and search)
- **Uptime**: 99.9% (Docker + cloud platform)
- **Cost**: FREE (OpenRouter free tier)
- **Languages**: 30+ supported
- **Memory**: ~100MB persistent knowledge

## 🔐 Security

- **API Keys**: Stored securely in environment variables
- **Permissions**: Admin-only commands require confirmation
- **Data**: All conversations and knowledge stored locally
- **Access**: Bot responds only to configured Telegram chats

## 🎯 Advanced Features

### Self-Learning
```bash
# Teach patterns
/learn "how are you" -> "I'm doing great! How about you?"

# Define scripts
/define
COMMAND: weather
PATTERN: weather in *
RESPONSE: I'd check the weather for {location} but I need real-time access. Try /search weather in {location}
```

### Web Search Integration
```bash
# Multi-engine search
/search latest developments in AI 2026
/search current news about space exploration
```

### Image Generation
```bash
# Automatic image creation
draw a sunset over mountains
generate image of a futuristic city
```

## 🤝 Contributing

The bot is designed to improve itself! Use `/upgrade` to suggest enhancements:

```
/upgrade Add support for voice messages
/upgrade Implement user preferences system
/upgrade Add integration with external APIs
```

## 📝 License

MIT License - Free for personal and commercial use.

## 🆘 Support

- **Issues**: Check `knowledge.json` for learned solutions
- **Logs**: `docker-compose logs -f` for real-time monitoring
- **Status**: `/stats` command for bot health

---

**Made with ❤️ for the 2026 AI era**

*Sarah AI Bot - Learning, evolving, and helping users since 2026*