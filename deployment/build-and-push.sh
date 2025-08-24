#!/bin/bash

# Legal Dashboard Service - Build and Push Docker Images Script
# This script builds and pushes Docker images to your registry

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f ".env.prod" ]; then
    export $(cat .env.prod | grep -v '^#' | xargs)
else
    echo -e "${RED}Error: .env.prod file not found. Please create it from .env.prod template.${NC}"
    exit 1
fi

# Validate required environment variables
if [ -z "$DOCKER_REGISTRY" ] || [ -z "$APP_NAME" ] || [ -z "$TAG" ]; then
    echo -e "${RED}Error: DOCKER_REGISTRY, APP_NAME, and TAG must be set in .env.prod${NC}"
    exit 1
fi

echo -e "${GREEN}Building and pushing Docker images...${NC}"

# Build platform (adjust for your EC2 instance architecture)
PLATFORM="linux/amd64"

# Build backend image
echo -e "${YELLOW}Building backend image...${NC}"
docker build \
    --platform $PLATFORM \
    -f deployment/Dockerfile.backend \
    -t $DOCKER_REGISTRY/$APP_NAME-backend:$TAG \
    .

# Build frontend image
echo -e "${YELLOW}Building frontend image...${NC}"
docker build \
    --platform $PLATFORM \
    -f deployment/Dockerfile.frontend \
    -t $DOCKER_REGISTRY/$APP_NAME-frontend:$TAG \
    .

# Build sync image
echo -e "${YELLOW}Building sync image...${NC}"
docker build \
    --platform $PLATFORM \
    -f deployment/Dockerfile.sync \
    -t $DOCKER_REGISTRY/$APP_NAME-sync:$TAG \
    .

# Push images
echo -e "${YELLOW}Pushing images to registry...${NC}"
docker push $DOCKER_REGISTRY/$APP_NAME-backend:$TAG
docker push $DOCKER_REGISTRY/$APP_NAME-frontend:$TAG
docker push $DOCKER_REGISTRY/$APP_NAME-sync:$TAG

echo -e "${GREEN}Successfully built and pushed all images!${NC}"
echo -e "${GREEN}Images:${NC}"
echo -e "  - $DOCKER_REGISTRY/$APP_NAME-backend:$TAG"
echo -e "  - $DOCKER_REGISTRY/$APP_NAME-frontend:$TAG"
echo -e "  - $DOCKER_REGISTRY/$APP_NAME-sync:$TAG"
