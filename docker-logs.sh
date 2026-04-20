#!/bin/bash
# 📋 DOCKER LOGS SCRIPT
# View real-time logs from the bot container

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📋 TELEGRAM AI BOT - DOCKER LOGS${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}\n"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose not found${NC}"
    exit 1
fi

echo -e "${YELLOW}Fetching logs... (Press Ctrl+C to stop)${NC}\n"

# Follow logs with docker-compose
docker-compose logs -f --tail=50
