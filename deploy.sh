#!/bin/bash
# Deployment script for AI Pricing Engine

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===== AI Pricing Engine Deployment =====${NC}"

# Function to check if command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check for required tools
if ! command_exists git; then
  echo -e "${RED}Error: git is not installed${NC}"
  exit 1
fi

if ! command_exists docker; then
  echo -e "${RED}Error: docker is not installed${NC}"
  exit 1
fi

# No longer need docker-compose for deployment

# Check if .env file exists
if [ ! -f .env ]; then
  echo -e "${RED}Error: .env file not found${NC}"
  echo "Please create a .env file with your API keys and configuration"
  exit 1
fi

# Git operations
echo -e "${YELLOW}Checking Git status...${NC}"
if [ -d .git ]; then
  git status
  
  read -p "Do you want to commit changes to Git? (y/n): " git_commit
  if [[ $git_commit == "y" || $git_commit == "Y" ]]; then
    read -p "Enter commit message: " commit_message
    git add .
    git commit -m "$commit_message"
    
    read -p "Do you want to push to remote repository? (y/n): " git_push
    if [[ $git_push == "y" || $git_push == "Y" ]]; then
      git push
      echo -e "${GREEN}Changes pushed to remote repository${NC}"
    fi
  fi
else
  echo -e "${YELLOW}Not a git repository. Skipping Git operations.${NC}"
fi

# Docker operations
echo -e "${YELLOW}Starting Docker deployment...${NC}"

# Set container name
CONTAINER_NAME="ai-pricing-api"

# Stop and remove any existing container
echo -e "${YELLOW}Stopping existing container if running...${NC}"
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# Build the Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
docker build -t ai-pricing:latest -f Dockerfile.deployment .

# Run the container
echo -e "${YELLOW}Starting container...${NC}"
docker run -d \
  --name $CONTAINER_NAME \
  --restart unless-stopped \
  -p 9000:8000 \
  --env-file .env \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/logs:/app/logs" \
  -v "$(pwd)/faiss_index:/app/faiss_index" \
  ai-pricing:latest

# Check container status
echo -e "${YELLOW}Checking container status...${NC}"
docker ps | grep $CONTAINER_NAME

# Check logs
echo -e "${YELLOW}Container logs (last 10 lines):${NC}"
docker logs $CONTAINER_NAME --tail 10

echo -e "${GREEN}Deployment completed!${NC}"
echo -e "${YELLOW}API is available at: http://localhost:9000${NC}"
echo -e "${YELLOW}Health check: http://localhost:9000/api/health${NC}"
