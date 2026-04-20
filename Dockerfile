FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .

RUN echo '{"free_tier": true, "fallback_mode": false, "current_year": 2026, "supported_languages": ["en","es","fr","de","zh","ja","ar","hi","pt","ru","ko","it","nl","tr","pl","sv","da","no","fi","el","he","th","vi","id","ms","tl","sw","zu","am"], "world_knowledge": {"year": 2026, "major_events": ["AI governance agreements", "quantum computing deployment", "space exploration milestones"], "technologies": ["AGI development", "neural implants", "sustainable energy"]}}' > knowledge.json && \
    echo "[]" > ai_memory.json && \
    echo "" > error.log && \
    echo "{}" > custom_scripts.json && \
    echo '{"last_restart_time": 0, "restart_count": 0, "last_restart_user": null}' > restart_tracking.json

ENV PYTHONUNBUFFERED=1

CMD ["python", "-u", "bot.py"]