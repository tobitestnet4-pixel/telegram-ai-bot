#!/bin/bash
# 🚀 DOCKER RUN SCRIPT
# Quickly run the bot locally for testing

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🚀 TELEGRAM AI BOT - DOCKER RUN${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}\n"

# Check prerequisites
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not installed${NC}"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker daemon not running${NC}"
    exit 1
fi

if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Checks passed\n${NC}"

# Get container name
CONTAINER_NAME="telegram-ai-bot"

# Check if container already running
if docker ps --filter "name=${CONTAINER_NAME}" --format '{{.Names}}' | grep -q "${CONTAINER_NAME}"; then
    echo -e "${YELLOW}⚠️  Container ${CONTAINER_NAME} is already running${NC}"
    echo -e "   Stop it first: ${YELLOW}docker stop ${CONTAINER_NAME}${NC}"
    exit 1
fi

# Use docker-compose (recommended)
echo -e "${YELLOW}🐳 Starting bot with docker-compose...${NC}\n"

if docker-compose up -d; then
    echo -e "\n${GREEN}✅ Bot started!${NC}\n"
    
    # Give it a moment to start
    sleep 2
    
    # Show status
    echo -e "${BLUE}📊 Container Status:${NC}"
    docker-compose ps
    
    echo -e "\n${BLUE}📋 Useful Commands:${NC}"
    echo -e "   View logs:          ${YELLOW}docker-compose logs -f${NC}"
    echo -e "   Check health:       ${YELLOW}docker-compose exec telegram-bot python -c 'print(\"✅ Bot running\")'${NC}"
    echo -e "   Stop bot:           ${YELLOW}docker-compose down${NC}"
    echo -e "   Restart bot:        ${YELLOW}docker-compose restart${NC}"
    
    echo -e "\n${GREEN}🎉 Bot is now running!${NC}"
    echo -e "   Send a message to your Telegram bot to test."
    
else
    echo -e "${RED}❌ Failed to start bot${NC}"
    exit 1
fi
