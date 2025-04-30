#!/bin/bash
# Test script for the standalone Docker deployment of AI Pricing Engine

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===== Testing AI Pricing Engine Docker Deployment =====${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo -e "${RED}Error: Docker is not running${NC}"
  exit 1
fi

# Build the Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
docker build -t ai-pricing:test -f Dockerfile.deployment .

# Set container name
CONTAINER_NAME="ai-pricing-test"

# Stop and remove any existing container
echo -e "${YELLOW}Stopping existing container if running...${NC}"
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# Run the container
echo -e "${YELLOW}Starting container...${NC}"
docker run -d \
  --name $CONTAINER_NAME \
  -p 9000:8000 \
  --env-file .env \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/logs:/app/logs" \
  -v "$(pwd)/faiss_index:/app/faiss_index" \
  ai-pricing:test

# Wait for the container to start
echo -e "${YELLOW}Waiting for the API to start...${NC}"
sleep 20

# Check container logs
echo -e "${YELLOW}Container logs:${NC}"
docker logs $CONTAINER_NAME

# Test the API endpoints
echo -e "${YELLOW}Testing API endpoints...${NC}"

# Base URL for the API
BASE_URL="http://localhost:9000"

# 1. Health Check - Verify API is running
echo -e "\n1. Health Check:"
HEALTH_CHECK=$(curl -s -X GET ${BASE_URL}/api/health)
echo $HEALTH_CHECK

if [[ ! -z "$HEALTH_CHECK" ]]; then
  echo -e "${GREEN}✓ Health check passed${NC}"
else
  echo -e "${RED}✗ Health check failed${NC}"
fi

# 2. Generate Price for an NFT
echo -e "\n2. Generate Price for an NFT:"
PRICE_CHECK=$(curl -s -X POST ${BASE_URL}/api/price \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "asset_id": "bored_ape_1234",
    "current_price": 120000
  }')
echo $PRICE_CHECK

if [[ ! -z "$PRICE_CHECK" ]]; then
  echo -e "${GREEN}✓ Price generation passed${NC}"
else
  echo -e "${RED}✗ Price generation failed${NC}"
fi

# Clean up
echo -e "\n${YELLOW}Cleaning up...${NC}"
docker stop $CONTAINER_NAME
docker rm $CONTAINER_NAME

echo -e "\n${GREEN}Test completed!${NC}"
