FROM python:3.13-slim

WORKDIR /app

# Install system dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py start.sh ./
RUN chmod +x start.sh

# Initialize data files
RUN echo '{"free_tier": true, "fallback_mode": false, "current_year": 2026}' > knowledge.json && \
    echo "[]" > ai_memory.json && \
    echo "" > error.log && \
    echo "{}" > custom_scripts.json && \
    echo '{"last_restart_time": 0, "restart_count": 0}' > restart_tracking.json

ENV PYTHONUNBUFFERED=1
ENV PORT=10000

EXPOSE 10000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

CMD ["./start.sh"]