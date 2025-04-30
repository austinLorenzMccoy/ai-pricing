#!/bin/bash
# Simple test script for Docker deployment

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===== Simple Docker Deployment Test =====${NC}"

# Clean up any existing test containers
echo -e "${YELLOW}Cleaning up any existing test containers...${NC}"
docker stop ai-pricing-simple-test 2>/dev/null || true
docker rm ai-pricing-simple-test 2>/dev/null || true

# Build the Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
docker build -t ai-pricing:simple-test -f Dockerfile.deployment .

# Run the Docker container
echo -e "${YELLOW}Running Docker container...${NC}"
docker run -d --name ai-pricing-simple-test -p 9000:8000 --env-file .env.test ai-pricing:simple-test

# Wait for the container to start
echo -e "${YELLOW}Waiting for the container to start...${NC}"
sleep 15

# Check if the container is running
echo -e "${YELLOW}Checking container status...${NC}"
if docker ps | grep -q ai-pricing-simple-test; then
  echo -e "${GREEN}✓ Container is running${NC}"
else
  echo -e "${RED}✗ Container failed to start${NC}"
  docker logs ai-pricing-simple-test
  exit 1
fi

# Show container logs
echo -e "${YELLOW}Container logs:${NC}"
docker logs ai-pricing-simple-test

echo -e "\n${GREEN}Docker deployment test completed successfully!${NC}"
echo -e "${YELLOW}The Docker image is ready for deployment.${NC}"
echo -e "${YELLOW}Use the deploy.sh script to deploy the application.${NC}"

# Clean up
echo -e "\n${YELLOW}Cleaning up test container...${NC}"
docker stop ai-pricing-simple-test
docker rm ai-pricing-simple-test
