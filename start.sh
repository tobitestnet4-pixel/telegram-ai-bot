#!/bin/bash
# Render deployment script for Telegram AI Bot

echo "[DEPLOY] Starting ABU-SATELLITE-NODE deployment..."

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo "[DEPLOY] Dependencies installed"

# Create necessary directories
mkdir -p logs
mkdir -p data

echo "[DEPLOY] Directories created"

# Start bot
echo "[DEPLOY] Starting bot..."
python bot.py
