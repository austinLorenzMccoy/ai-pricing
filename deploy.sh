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

if ! command_exists docker-compose; then
  echo -e "${RED}Error: docker-compose is not installed${NC}"
  exit 1
fi

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

# Stop any running containers
echo -e "${YELLOW}Stopping existing containers...${NC}"
docker-compose -f docker-compose.production.yml down

# Build and start containers
echo -e "${YELLOW}Building and starting containers...${NC}"
docker-compose -f docker-compose.production.yml up --build -d

# Check container status
echo -e "${YELLOW}Checking container status...${NC}"
docker ps | grep ai-pricing

# Check logs
echo -e "${YELLOW}Container logs (last 10 lines):${NC}"
docker logs ai-pricing-api --tail 10

echo -e "${GREEN}Deployment completed!${NC}"
echo -e "${YELLOW}API is available at: http://localhost:8000${NC}"
echo -e "${YELLOW}Health check: http://localhost:8000/api/health${NC}"
