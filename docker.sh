#!/bin/bash
# 🐳 Sarah AI Bot - Docker Management Script
# Unified script for all Docker operations

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Functions
show_help() {
    echo -e "${BLUE}🐳 Sarah AI Bot - Docker Management${NC}"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  build    - Build Docker image"
    echo "  start    - Start the bot container"
    echo "  stop     - Stop the bot container"
    echo "  restart  - Restart the bot container"
    echo "  logs     - Show container logs"
    echo "  status   - Show container status"
    echo "  shell    - Open shell in container"
    echo "  clean    - Remove unused Docker resources"
    echo "  help     - Show this help"
    echo ""
}

check_prerequisites() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed${NC}"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker daemon is not running${NC}"
        exit 1
    fi

    if [ ! -f .env ]; then
        echo -e "${RED}❌ .env file not found${NC}"
        echo "Please create .env file with:"
        echo "  TELEGRAM_BOT_TOKEN=your_token"
        echo "  OPENROUTER_API_KEY=your_key"
        exit 1
    fi
}

build_image() {
    echo -e "${BLUE}🐳 Building Sarah AI Bot image...${NC}"

    if docker-compose build; then
        echo -e "${GREEN}✅ Build successful!${NC}"

        # Show image info
        echo -e "${PURPLE}📊 Image Information:${NC}"
        docker images | grep telegram_ai_project
    else
        echo -e "${RED}❌ Build failed!${NC}"
        exit 1
    fi
}

start_container() {
    echo -e "${BLUE}🚀 Starting Sarah AI Bot...${NC}"

    if docker-compose up -d; then
        echo -e "${GREEN}✅ Bot started successfully!${NC}"

        # Wait a moment and show status
        sleep 3
        echo -e "${PURPLE}📊 Container Status:${NC}"
        docker-compose ps

        echo -e "${YELLOW}🎯 Useful commands:${NC}"
        echo "  View logs:    $0 logs"
        echo "  Check status: $0 status"
        echo "  Stop bot:     $0 stop"
    else
        echo -e "${RED}❌ Failed to start bot${NC}"
        exit 1
    fi
}

stop_container() {
    echo -e "${BLUE}🛑 Stopping Sarah AI Bot...${NC}"

    if docker-compose down; then
        echo -e "${GREEN}✅ Bot stopped successfully${NC}"
    else
        echo -e "${RED}❌ Failed to stop bot${NC}"
        exit 1
    fi
}

restart_container() {
    echo -e "${BLUE}🔄 Restarting Sarah AI Bot...${NC}"

    if docker-compose restart; then
        echo -e "${GREEN}✅ Bot restarted successfully${NC}"
        sleep 2
        docker-compose ps
    else
        echo -e "${RED}❌ Failed to restart bot${NC}"
        exit 1
    fi
}

show_logs() {
    echo -e "${BLUE}📋 Sarah AI Bot Logs${NC}"
    echo -e "${YELLOW}Press Ctrl+C to exit logs${NC}"
    echo ""

    docker-compose logs -f
}

show_status() {
    echo -e "${BLUE}📊 Sarah AI Bot Status${NC}"
    echo ""

    # Container status
    echo -e "${PURPLE}Container Status:${NC}"
    docker-compose ps
    echo ""

    # Resource usage
    echo -e "${PURPLE}Resource Usage:${NC}"
    CONTAINER_ID=$(docker-compose ps -q 2>/dev/null)
    if [ ! -z "$CONTAINER_ID" ]; then
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" "$CONTAINER_ID"
    fi
    echo ""

    # Recent logs
    echo -e "${PURPLE}Recent Logs:${NC}"
    docker-compose logs --tail=5
}

open_shell() {
    echo -e "${BLUE}🐚 Opening shell in Sarah AI Bot container${NC}"

    if docker-compose exec telegram-bot bash 2>/dev/null; then
        : # Success
    else
        echo -e "${YELLOW}bash not available, trying sh...${NC}"
        docker-compose exec telegram-bot sh
    fi
}

clean_docker() {
    echo -e "${BLUE}🧹 Cleaning Docker resources...${NC}"

    echo "Stopping containers..."
    docker-compose down 2>/dev/null || true

    echo "Removing unused images..."
    docker image prune -f

    echo "Removing unused volumes..."
    docker volume prune -f

    echo "Removing unused networks..."
    docker network prune -f

    echo -e "${GREEN}✅ Docker cleanup completed${NC}"
}

# Main script logic
case "${1:-help}" in
    build)
        check_prerequisites
        build_image
        ;;
    start)
        check_prerequisites
        start_container
        ;;
    stop)
        stop_container
        ;;
    restart)
        restart_container
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    shell)
        open_shell
        ;;
    clean)
        clean_docker
        ;;
    help|*)
        show_help
        ;;
esac