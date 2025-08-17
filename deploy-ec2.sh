#!/bin/bash

# Legal Dashboard Service - EC2 Deployment Script
# This script automates the deployment process on a fresh EC2 instance

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root. Please run as ubuntu user."
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Docker
install_docker() {
    log "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    
    # Install Docker Compose
    log "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    log "Docker installation completed. Please log out and back in to apply group changes."
}

# Function to setup environment
setup_environment() {
    log "Setting up environment..."
    
    # Check if .env exists
    if [[ ! -f "deployment/.env" ]]; then
        log "Creating .env file from template..."
        cp deployment/.env.example deployment/.env
        warn "Please edit deployment/.env with your actual configuration values!"
        warn "Especially update the MongoDB passwords for security!"
    fi
    
    # Create data directory for MongoDB
    log "Creating MongoDB data directory..."
    sudo mkdir -p /data/mongodb
    sudo chown -R 999:999 /data/mongodb
}

# Function to configure firewall
setup_firewall() {
    log "Configuring UFW firewall..."
    
    # Enable UFW if not already enabled
    if ! sudo ufw status | grep -q "Status: active"; then
        sudo ufw enable
    fi
    
    # Allow necessary ports
    sudo ufw allow ssh
    sudo ufw allow 80
    sudo ufw allow 443
    sudo ufw allow 3000  # Reflex Frontend
    sudo ufw allow 8000  # Reflex Backend
    
    log "Firewall configuration completed"
}

# Function to install Nginx
install_nginx() {
    log "Installing and configuring Nginx..."
    
    sudo apt update
    sudo apt install -y nginx
    
    # Create Nginx configuration
    cat > /tmp/legal-dashboard-nginx << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    
    server_name _;
    
    # Frontend (Reflex)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }
    
    # API Backend
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline' 'unsafe-eval'" always;
}
EOF
    
    sudo mv /tmp/legal-dashboard-nginx /etc/nginx/sites-available/legal-dashboard
    sudo ln -sf /etc/nginx/sites-available/legal-dashboard /etc/nginx/sites-enabled/default
    
    # Test nginx configuration
    sudo nginx -t
    sudo systemctl restart nginx
    sudo systemctl enable nginx
    
    log "Nginx configuration completed"
}

# Function to create systemd service
create_systemd_service() {
    log "Creating systemd service..."
    
    cat > /tmp/legal-dashboard.service << EOF
[Unit]
Description=Legal Dashboard Service
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/docker-manage.sh start
ExecStop=$(pwd)/docker-manage.sh stop
User=$USER
Group=$USER
Environment=PATH=/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=multi-user.target
EOF
    
    sudo mv /tmp/legal-dashboard.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable legal-dashboard.service
    
    log "Systemd service created and enabled"
}

# Function to start services
start_services() {
    log "Starting Legal Dashboard services..."
    
    # Make sure docker-manage.sh is executable
    chmod +x docker-manage.sh
    
    # Start services
    ./docker-manage.sh start
    
    log "Services started successfully"
}

# Function to run health checks
health_check() {
    log "Running health checks..."
    
    # Wait for services to start
    sleep 30
    
    # Check if containers are running
    if ! docker ps | grep -q "legal_dashboard"; then
        error "Legal Dashboard containers are not running"
    fi
    
    # Check if frontend is responding
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        log "✅ Frontend is responding"
    else
        warn "❌ Frontend is not responding yet"
    fi
    
    # Check if backend is responding
    if curl -f http://localhost:8000 > /dev/null 2>&1; then
        log "✅ Backend is responding"
    else
        warn "❌ Backend is not responding yet"
    fi
    
    log "Health check completed"
}

# Function to display deployment info
show_deployment_info() {
    local public_ip=$(curl -s http://checkip.amazonaws.com/ || echo "unknown")
    
    echo ""
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Legal Dashboard Deployed!     ${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    echo -e "${GREEN}🌐 Frontend URL:${NC} http://$public_ip"
    echo -e "${GREEN}🔌 API URL:${NC} http://$public_ip/api"
    echo -e "${GREEN}📊 MongoDB Admin:${NC} http://$public_ip:8081 (if enabled)"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Edit deployment/.env with your actual configuration"
    echo "2. Update MongoDB passwords for security"
    echo "3. Configure domain name and SSL certificate"
    echo "4. Set up monitoring and backups"
    echo ""
    echo -e "${YELLOW}Useful Commands:${NC}"
    echo "./docker-manage.sh status    - Check service status"
    echo "./docker-manage.sh logs      - View service logs"
    echo "./docker-manage.sh restart   - Restart services"
    echo "sudo systemctl status legal-dashboard - Check systemd service"
    echo ""
}

# Main deployment function
main() {
    log "Starting Legal Dashboard EC2 deployment..."
    
    # Check if we're in the right directory
    if [[ ! -f "docker-manage.sh" ]] || [[ ! -d "deployment" ]]; then
        error "Please run this script from the legal-dashboard-service directory"
    fi
    
    # Update system
    log "Updating system packages..."
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y curl wget unzip git htop
    
    # Install Docker if not present
    if ! command_exists docker; then
        install_docker
        warn "Docker installed. Please log out and back in, then run this script again."
        exit 0
    fi
    
    # Setup environment
    setup_environment
    
    # Configure firewall
    setup_firewall
    
    # Install and configure Nginx
    install_nginx
    
    # Create systemd service
    create_systemd_service
    
    # Start services
    start_services
    
    # Run health checks
    health_check
    
    # Show deployment information
    show_deployment_info
    
    log "Deployment completed successfully!"
}

# Script arguments handling
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "health-check")
        health_check
        ;;
    "nginx")
        install_nginx
        ;;
    "firewall")
        setup_firewall
        ;;
    "info")
        show_deployment_info
        ;;
    *)
        echo "Usage: $0 [deploy|health-check|nginx|firewall|info]"
        echo ""
        echo "Commands:"
        echo "  deploy      - Full deployment (default)"
        echo "  health-check - Run health checks only"
        echo "  nginx       - Install and configure Nginx only"
        echo "  firewall    - Configure firewall only"
        echo "  info        - Show deployment information"
        exit 1
        ;;
esac
