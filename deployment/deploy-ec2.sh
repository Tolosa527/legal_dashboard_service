#!/bin/bash

# Legal Dashboard Service - EC2 Deployment Script
# Run this script on your EC2 instance to deploy the application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/opt/legal_dashboard"
SERVICE_NAME="legal-dashboard"

echo -e "${BLUE}Legal Dashboard Service - EC2 Deployment${NC}"
echo -e "${BLUE}=======================================${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run this script as root (use sudo)${NC}"
    exit 1
fi

# Update system packages
echo -e "${YELLOW}Updating system packages...${NC}"
apt-get update && apt-get upgrade -y

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Installing Docker...${NC}"
    apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io
    systemctl enable docker
    systemctl start docker
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Installing Docker Compose...${NC}"
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Create application directory
echo -e "${YELLOW}Creating application directory...${NC}"
mkdir -p $APP_DIR
mkdir -p $APP_DIR/ssl

# Copy configuration files (you need to upload these to your EC2 instance first)
echo -e "${YELLOW}Setting up configuration files...${NC}"
if [ ! -f "$APP_DIR/.env.prod" ]; then
    echo -e "${RED}Error: $APP_DIR/.env.prod not found. Please upload your environment file.${NC}"
    echo -e "${YELLOW}You can copy the .env.prod template and modify it for your EC2 instance.${NC}"
    echo -e "${YELLOW}Make sure to configure your MongoDB Atlas connection string.${NC}"
    exit 1
fi

if [ ! -f "$APP_DIR/docker-compose.prod.yml" ]; then
    echo -e "${RED}Error: $APP_DIR/docker-compose.prod.yml not found. Please upload the production compose file.${NC}"
    exit 1
fi

if [ ! -f "$APP_DIR/nginx.conf" ]; then
    echo -e "${RED}Error: $APP_DIR/nginx.conf not found. Please upload the nginx configuration.${NC}"
    exit 1
fi

# Set proper permissions for configuration files
chmod 600 $APP_DIR/.env.prod

# Pull latest images
echo -e "${YELLOW}Pulling Docker images...${NC}"
cd $APP_DIR
docker-compose -f docker-compose.prod.yml --env-file .env.prod pull

# Stop existing services
echo -e "${YELLOW}Stopping existing services...${NC}"
docker-compose -f docker-compose.prod.yml --env-file .env.prod down

# Start services
echo -e "${YELLOW}Starting services...${NC}"
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Wait for services to be healthy
echo -e "${YELLOW}Waiting for services to be healthy...${NC}"
sleep 30

# Check service status
echo -e "${YELLOW}Checking service status...${NC}"
docker-compose -f docker-compose.prod.yml --env-file .env.prod ps

# Create systemd service for auto-restart
echo -e "${YELLOW}Creating systemd service...${NC}"
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Legal Dashboard Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$APP_DIR
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml --env-file .env.prod down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Enable and start systemd service
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME

# Configure firewall (assuming UFW)
if command -v ufw &> /dev/null; then
    echo -e "${YELLOW}Configuring firewall...${NC}"
    ufw allow 22/tcp   # SSH
    ufw allow 80/tcp   # HTTP
    ufw allow 443/tcp  # HTTPS
    ufw --force enable
fi

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}==============================${NC}"
echo -e "${GREEN}Your Legal Dashboard is now running on:${NC}"
echo -e "  HTTP:  http://$(curl -s ifconfig.me)"
echo -e "  Local: http://localhost"
echo -e ""
echo -e "${YELLOW}To check service status:${NC}"
echo -e "  sudo systemctl status $SERVICE_NAME"
echo -e "  sudo docker-compose -f $APP_DIR/docker-compose.prod.yml ps"
echo -e ""
echo -e "${YELLOW}To view logs:${NC}"
echo -e "  sudo docker-compose -f $APP_DIR/docker-compose.prod.yml logs -f"
echo -e ""
echo -e "${YELLOW}To update the application:${NC}"
echo -e "  sudo docker-compose -f $APP_DIR/docker-compose.prod.yml pull"
echo -e "  sudo systemctl restart $SERVICE_NAME"
