#!/bin/bash
# 🚀 TELEGRAM AI BOT - ULTIMATE ONE-COMMAND DEPLOYMENT
# Fully autonomous DevOps script
# Usage: ./deploy.sh [action]
# Actions: build, run, test, stop, logs, clean

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
BOT_NAME="telegram-ai-bot"
IMAGE_TAG="${BOT_NAME}:latest"
CONTAINER_NAME="${BOT_NAME}"

# Functions
print_header() {
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}🚀 TELEGRAM AI BOT - DEVOPS AUTOMATION${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}\n"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker not installed${NC}"
        exit 1
    fi
    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker daemon not running${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Docker ready${NC}"
}

check_env() {
    if [ ! -f .env ]; then
        echo -e "${RED}❌ .env file not found${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ .env configured${NC}"
}

build_image() {
    echo -e "${YELLOW}Building Docker image...${NC}\n"
    docker build -t "$IMAGE_TAG" .
    echo -e "\n${GREEN}✅ Build complete${NC}"
    docker images | grep "$BOT_NAME"
}

start_bot() {
    echo -e "${YELLOW}Starting bot...${NC}\n"
    docker-compose up -d
    sleep 2
    
    echo -e "\n${GREEN}✅ Bot started${NC}\n"
    docker-compose ps
    
    echo -e "\n${BLUE}📋 Next steps:${NC}"
    echo -e "   View logs: ${YELLOW}./deploy.sh logs${NC}"
    echo -e "   Test bot: Send message in Telegram"
    echo -e "   Stop bot: ${YELLOW}./deploy.sh stop${NC}"
}

test_bot() {
    echo -e "${YELLOW}Testing bot connectivity...${NC}\n"
    
    # Check container is running
    if docker-compose ps | grep -q "Up"; then
        echo -e "${GREEN}✅ Container running${NC}"
    else
        echo -e "${RED}❌ Container not running${NC}"
        exit 1
    fi
    
    # Check health
    HEALTH=$(docker inspect "$CONTAINER_NAME" --format='{{.State.Health.Status}}' 2>/dev/null || echo "unknown")
    if [ "$HEALTH" = "healthy" ]; then
        echo -e "${GREEN}✅ Health check: HEALTHY${NC}"
    else
        echo -e "${YELLOW}⚠️  Health check: $HEALTH (may be starting)${NC}"
    fi
    
    # Check API connectivity
    echo -e "\n${YELLOW}Testing OpenRouter API...${NC}"
    docker exec "$CONTAINER_NAME" python -c "import httpx; r=httpx.get('https://openrouter.ai'); print(f'✅ API reachable (HTTP {r.status_code})')" || echo -e "${RED}❌ API check failed${NC}"
    
    echo -e "\n${GREEN}✅ Tests complete${NC}"
    echo -e "${BLUE}Send a message to your Telegram bot to test!${NC}"
}

view_logs() {
    echo -e "${YELLOW}Following logs (Press Ctrl+C to exit)...${NC}\n"
    docker-compose logs -f --tail=50
}

stop_bot() {
    echo -e "${YELLOW}Stopping bot...${NC}\n"
    docker-compose down
    echo -e "${GREEN}✅ Bot stopped${NC}"
}

clean_all() {
    echo -e "${YELLOW}Cleaning up Docker resources...${NC}\n"
    
    docker-compose down
    
    if docker images | grep -q "$BOT_NAME"; then
        docker rmi "$IMAGE_TAG"
        echo -e "${GREEN}✅ Image removed${NC}"
    fi
    
    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

show_status() {
    echo -e "${BLUE}📊 System Status:${NC}\n"
    
    echo -e "${CYAN}Docker Status:${NC}"
    docker --version
    docker-compose --version
    
    echo -e "\n${CYAN}Container Status:${NC}"
    docker-compose ps || echo "No containers running"
    
    echo -e "\n${CYAN}Image Status:${NC}"
    docker images | grep "$BOT_NAME" || echo "No image built"
    
    echo -e "\n${CYAN}Configuration:${NC}"
    if [ -f .env ]; then
        echo "✅ .env exists"
        echo "   TELEGRAM_BOT_TOKEN: $(grep TELEGRAM_BOT_TOKEN .env | cut -d'=' -f2 | cut -c1-10)..."
        echo "   OPENAI_API_KEY: $(grep OPENAI_API_KEY .env | cut -d'=' -f2 | cut -c1-10)..."
    fi
}

show_help() {
    echo -e "${CYAN}📖 Available Commands:${NC}\n"
    echo -e "   ${YELLOW}./deploy.sh build${NC}   - Build Docker image"
    echo -e "   ${YELLOW}./deploy.sh run${NC}     - Start bot"
    echo -e "   ${YELLOW}./deploy.sh test${NC}    - Test connectivity"
    echo -e "   ${YELLOW}./deploy.sh logs${NC}    - View real-time logs"
    echo -e "   ${YELLOW}./deploy.sh stop${NC}    - Stop bot"
    echo -e "   ${YELLOW}./deploy.sh status${NC}  - Show system status"
    echo -e "   ${YELLOW}./deploy.sh clean${NC}   - Remove Docker resources"
    echo -e "   ${YELLOW}./deploy.sh help${NC}    - Show this help"
    echo ""
    echo -e "${CYAN}🚀 Quick Start (3 commands):${NC}"
    echo -e "   1. ${YELLOW}./deploy.sh build${NC}"
    echo -e "   2. ${YELLOW}./deploy.sh run${NC}"
    echo -e "   3. ${YELLOW}./deploy.sh logs${NC}"
}

# Main
print_header

ACTION="${1:-help}"

case "$ACTION" in
    build)
        check_docker
        check_env
        build_image
        ;;
    run)
        check_docker
        check_env
        start_bot
        ;;
    test)
        test_bot
        ;;
    logs)
        view_logs
        ;;
    stop)
        stop_bot
        ;;
    status)
        show_status
        ;;
    clean)
        clean_all
        ;;
    help)
        show_help
        ;;
    *)
        echo -e "${RED}❌ Unknown action: $ACTION${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac

echo ""
