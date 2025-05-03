#!/bin/bash
# Script to clean up unnecessary Docker files after migrating to standalone Docker

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===== Cleaning up unnecessary Docker files =====${NC}"

# Files to be removed
FILES_TO_REMOVE=(
  "docker-compose.yml"
  "docker-compose.production.yml"
  "Dockerfile"
  "Dockerfile.custom"
  "Dockerfile.production"
  "requirements.docker.txt"
)

# List files that will be removed
echo -e "${YELLOW}The following files will be removed:${NC}"
for file in "${FILES_TO_REMOVE[@]}"; do
  if [ -f "$file" ]; then
    echo "  - $file"
  fi
done

# Ask for confirmation
read -p "Do you want to proceed with deletion? (y/n): " confirm
if [[ $confirm != "y" && $confirm != "Y" ]]; then
  echo -e "${YELLOW}Cleanup canceled.${NC}"
  exit 0
fi

# Remove files
for file in "${FILES_TO_REMOVE[@]}"; do
  if [ -f "$file" ]; then
    rm "$file"
    echo -e "${GREEN}Removed: $file${NC}"
  else
    echo -e "${YELLOW}File not found: $file${NC}"
  fi
done

echo -e "\n${GREEN}Cleanup completed!${NC}"
echo -e "${YELLOW}Remaining Docker files:${NC}"
echo -e "  - Dockerfile.deployment (optimized for standalone deployment)"
echo -e "  - DOCKER_DEPLOYMENT.md (deployment guide)"
echo -e "  - deploy.sh (deployment script)"
echo -e "  - test_docker_deployment.sh (test script)"
