#!/bin/bash
# 🐳 DOCKER BUILD SCRIPT
# Builds the Telegram AI Bot Docker image with proper tagging and optimization

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🐳 TELEGRAM AI BOT - DOCKER BUILD SCRIPT${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}\n"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker daemon is not running. Please start Docker.${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found!${NC}"
    echo "Please create .env file with:"
    echo "  TELEGRAM_BOT_TOKEN=your_token"
    echo "  OPENAI_API_KEY=your_key"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites checked${NC}\n"

# Get version from date
VERSION=$(date +%Y%m%d_%H%M%S)
IMAGE_NAME="telegram-ai-bot"
IMAGE_TAG="${IMAGE_NAME}:${VERSION}"
LATEST_TAG="${IMAGE_NAME}:latest"

echo -e "${YELLOW}📦 Building image...${NC}"
echo -e "   Image: ${IMAGE_TAG}"
echo -e "   Latest: ${LATEST_TAG}\n"

# Build the image
if docker build \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    -t "$IMAGE_TAG" \
    -t "$LATEST_TAG" \
    -f Dockerfile \
    .; then
    
    echo -e "\n${GREEN}✅ Build successful!${NC}\n"
    
    # Show image info
    echo -e "${BLUE}📊 Image Information:${NC}"
    docker images "$IMAGE_NAME" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    
    echo -e "\n${BLUE}🚀 Next steps:${NC}"
    echo -e "   1. Test locally:    ${YELLOW}docker-compose up -d${NC}"
    echo -e "   2. View logs:       ${YELLOW}docker-compose logs -f${NC}"
    echo -e "   3. Stop bot:        ${YELLOW}docker-compose down${NC}"
    echo -e "   4. Deploy to cloud: See ${YELLOW}DOCKER_SETUP.md${NC}"
    
else
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ Docker build completed!${NC}"
