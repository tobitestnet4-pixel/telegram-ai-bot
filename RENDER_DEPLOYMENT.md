# Telegram AI Bot - Production Deployment Guide

## PRODUCTION FIX SUMMARY

Your bot was experiencing:
1. **Concurrent polling conflicts** — Two instances hitting Telegram's API simultaneously (409 CONFLICT)
2. **DNS resolution failures** — Network timeouts during peak load
3. **No graceful shutdown** — Abrupt termination causing state loss
4. **No retry logic** — Single-attempt API calls failing without fallback

### WHAT'S BEEN FIXED

✅ **Webhook Mode (Stateless)**
- Replaces polling with Telegram webhook callbacks
- Horizontal scaling ready (multiple instances supported)
- Zero concurrent conflicts

✅ **Exponential Backoff**
- Retry API calls with 2^n second delays (up to 3 attempts)
- Handles DNS failures, timeouts, 5xx errors gracefully

✅ **Graceful Shutdown**
- SIGTERM/SIGINT handling for Render deployments
- Proper resource cleanup on container stop

✅ **Health Checks**
- `/health` endpoint for Render monitoring
- Automatic restart on failure

✅ **Production Server**
- Gunicorn with 2 workers + threading for concurrency
- Proper logging and error handling

---

## DEPLOYMENT TO RENDER

### 1. **Push Code to GitHub**
```bash
git add .
git commit -m "Production fixes: webhook mode, exponential backoff, graceful shutdown"
git push origin main
```

### 2. **Connect Render to GitHub**
- Go to https://dashboard.render.com
- Click "New +" → "Web Service"
- Connect your GitHub repository
- Select your branch

### 3. **Configure Environment Variables on Render**
In the Render dashboard, add these as "Secret Files" or "Environment Variables":

```
TELEGRAM_BOT_TOKEN=your_token_from_botfather
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
OPENROUTER_KEY=your_openrouter_key
ENVIRONMENT=production
USE_WEBHOOK=true
```

### 4. **Configure Build & Deploy**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `./start.sh`
- **Instance Type:** Standard (minimum)
- **Region:** Oregon (or your closest)
- **Auto-Deploy:** Enabled

### 5. **Update Telegram Webhook on Deployment**
After Render assigns your URL (e.g., `https://telegram-ai-bot-xyz.onrender.com`):

Set `WEBHOOK_URL` environment variable to:
```
https://telegram-ai-bot-xyz.onrender.com/webhook
```

The bot will auto-register this webhook on startup.

### 6. **Verify Deployment**
```bash
# Check health endpoint
curl https://telegram-ai-bot-xyz.onrender.com/health

# Expected response:
# {"status":"ok","version":"v4.0","mode":"webhook","timestamp":"..."}

# Check stats
curl https://telegram-ai-bot-xyz.onrender.com/stats
```

---

## LOCAL TESTING (BEFORE RENDER)

### Test Webhook Mode Locally
```bash
# Set environment variables
export TELEGRAM_BOT_TOKEN=your_token
export USE_WEBHOOK=true
export WEBHOOK_URL=http://localhost:10000/webhook
export PORT=10000

# Run bot
python bot.py

# In another terminal, test health endpoint
curl http://localhost:10000/health

# Simulate incoming Telegram message
curl -X POST http://localhost:10000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123456789,
    "message": {
      "message_id": 1,
      "date": 1234567890,
      "chat": {"id": 123, "type": "private"},
      "from": {"id": 123, "first_name": "Test"},
      "text": "Hello bot"
    }
  }'
```

### Test Polling Mode (Development)
```bash
export USE_WEBHOOK=false
python bot.py
```

---

## MONITORING & DEBUGGING ON RENDER

### View Logs
```bash
# Render Dashboard → Your Service → Logs
# Or via Render CLI:
render logs --service telegram-ai-bot
```

### Common Issues

**Issue: 409 CONFLICT errors still appearing?**
- Ensure only ONE instance is running
- Check Render deployment → "Manual Deploy" should be clean
- Old polling session may still be active; restart service completely

**Issue: Webhook not receiving updates?**
- Verify `WEBHOOK_URL` is set correctly in environment
- Check Render logs for webhook registration
- Test: `curl https://your-service.onrender.com/health` returns 200

**Issue: Bot responds slowly?**
- Check API quota usage (Groq, Gemini, OpenRouter)
- Increase gunicorn workers: Edit `start.sh` → `--workers 4`
- Monitor Render CPU/Memory metrics

**Issue: Database locked errors?**
- SQLite doesn't handle high concurrency well
- For 100+ users: migrate to PostgreSQL
- Render offers free tier PostgreSQL

---

## PRODUCTION CHECKLIST

- [ ] Push code to GitHub
- [ ] Create Render account
- [ ] Set all environment variables
- [ ] Deploy from GitHub
- [ ] Set `WEBHOOK_URL` to your Render service URL
- [ ] Test `/health` endpoint
- [ ] Send test message to bot on Telegram
- [ ] Monitor logs for 10+ minutes
- [ ] Set up Render alerts for restart events
- [ ] Document your Render service URL for the team

---

## KEY CHANGES IN CODE

### bot.py
- Added `USE_WEBHOOK`, `WEBHOOK_URL`, `ENV` environment variables
- Converted API calls to async with `httpx.AsyncClient`
- Added 3x retry loop with exponential backoff for each API
- Added `GracefulShutdown` handler for SIGTERM
- Changed Flask route to async `/webhook` endpoint
- Added `initialize_application()` for lazy initialization

### docker-compose.yml
- Added `ports` mapping
- Added `healthcheck` configuration
- Added `deploy.restart_policy` for auto-recovery
- Added environment variables for webhook mode

### Dockerfile
- Added `curl` system dependency for healthcheck
- Added `HEALTHCHECK` instruction
- Changed `CMD` to use `start.sh` script

### start.sh (NEW)
- Gunicorn production server for webhook mode
- Python fallback for polling mode
- Proper signal handling

### render.yaml (NEW)
- Render-specific deployment configuration
- Auto-scales health checks
- Configures webhook URL injection

---

## NEXT STEPS FOR SCALE

1. **100+ Users**: Migrate to PostgreSQL (Render offers free tier)
   - SQLite hits contention limits
   - Keep SQLite as fallback for development

2. **Multi-Instance**: Use Redis for state sharing
   - Currently single instance (fine for <10k users)
   - Redis adds distributed session support

3. **Monitoring**: Integrate Sentry or DataDog
   - Track errors across instances
   - Performance analytics

4. **CI/CD**: Add GitHub Actions
   - Auto-test on push
   - Auto-deploy to Render

5. **Custom Domain**: Point DNS to Render service
   - More professional webhook URL
   - SSL auto-managed by Render

---

## SUPPORT

**Render Status**: https://status.render.com
**Telegram Bot API**: https://core.telegram.org/bots/api
**python-telegram-bot Docs**: https://docs.python-telegram-bot.org/
