#!/bin/bash
# 🛑 DOCKER STOP SCRIPT
# Stops and cleans up Docker containers

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🛑 TELEGRAM AI BOT - DOCKER STOP${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}\n"

# Stop and remove containers
echo -e "${YELLOW}Stopping Docker containers...${NC}\n"

if docker-compose down; then
    echo -e "${GREEN}✅ Bot stopped successfully${NC}\n"
    
    echo -e "${BLUE}📊 Remaining Docker resources:${NC}"
    docker ps -a --filter "name=telegram" --format "table {{.Names}}\t{{.Status}}"
    
    echo -e "\n${YELLOW}To clean up images (optional):${NC}"
    echo -e "   ${YELLOW}docker rmi telegram-ai-bot:latest${NC}"
    
else
    echo -e "${RED}❌ Failed to stop bot${NC}"
    exit 1
fi
