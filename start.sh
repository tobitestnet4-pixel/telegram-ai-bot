#!/bin/bash
# Render production entrypoint with gunicorn

set -e

echo "[STARTUP] Initializing bot container..."
echo "[STARTUP] Python version: $(python --version)"
echo "[STARTUP] Environment: ${ENVIRONMENT:-development}"

# Verify required environment variables
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "[ERROR] TELEGRAM_BOT_TOKEN is not set"
    exit 1
fi

echo "[STARTUP] TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN:0:20}..."
echo "[STARTUP] USE_WEBHOOK: ${USE_WEBHOOK:-true}"
echo "[STARTUP] PORT: ${PORT:-10000}"

# Run the application with gunicorn for Render
if [ "$USE_WEBHOOK" = "true" ]; then
    echo "[STARTUP] Starting with Gunicorn (webhook mode)..."
    exec gunicorn \
        --bind 0.0.0.0:${PORT:-10000} \
        --workers 2 \
        --threads 2 \
        --worker-class sync \
        --timeout 120 \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        "bot:app"
else
    echo "[STARTUP] Starting with Python (polling mode)..."
    exec python -u bot.py
fi
