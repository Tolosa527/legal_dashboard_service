#!/bin/bash

# Legal Dashboard Service - Deployment Management Script
# This script helps manage the deployment on EC2

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
COMPOSE_FILE="$APP_DIR/docker-compose.prod.yml"
ENV_FILE="$APP_DIR/.env.prod"

# Functions
show_usage() {
    echo -e "${BLUE}Legal Dashboard Service - Management Script${NC}"
    echo ""
    echo "Usage: $0 {start|stop|restart|status|logs|update|backup|cleanup}"
    echo ""
    echo "Commands:"
    echo "  start    - Start all services"
    echo "  stop     - Stop all services"
    echo "  restart  - Restart all services"
    echo "  status   - Show service status"
    echo "  logs     - Show service logs (follow mode)"
    echo "  update   - Pull latest images and restart"
    echo "  backup   - Create MongoDB backup"
    echo "  cleanup  - Clean up unused Docker resources"
    echo ""
}

check_requirements() {
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}Error: $COMPOSE_FILE not found${NC}"
        exit 1
    fi
    
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${RED}Error: $ENV_FILE not found${NC}"
        exit 1
    fi
}

start_services() {
    echo -e "${YELLOW}Starting Legal Dashboard services...${NC}"
    cd $APP_DIR
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d
    echo -e "${GREEN}Services started successfully!${NC}"
}

stop_services() {
    echo -e "${YELLOW}Stopping Legal Dashboard services...${NC}"
    cd $APP_DIR
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE down
    echo -e "${GREEN}Services stopped successfully!${NC}"
}

restart_services() {
    echo -e "${YELLOW}Restarting Legal Dashboard services...${NC}"
    stop_services
    sleep 5
    start_services
}

show_status() {
    echo -e "${BLUE}Legal Dashboard Service Status${NC}"
    echo -e "${BLUE}=============================${NC}"
    
    # Systemd service status
    echo -e "${YELLOW}Systemd Service:${NC}"
    systemctl status $SERVICE_NAME --no-pager || true
    echo ""
    
    # Docker containers status
    echo -e "${YELLOW}Docker Containers:${NC}"
    cd $APP_DIR
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE ps
    echo ""
    
    # Service health checks
    echo -e "${YELLOW}Health Checks:${NC}"
    echo -n "Frontend: "
    if curl -f -s http://localhost/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
    else
        echo -e "${RED}✗ Unhealthy${NC}"
    fi
    
    echo -n "Backend:  "
    if curl -f -s http://localhost:8000/ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
    else
        echo -e "${RED}✗ Unhealthy${NC}"
    fi
    
    echo -n "Atlas:    "
    # Test MongoDB Atlas connection through backend API
    if curl -f -s http://localhost:8000/api/health/db > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Connected${NC}"
    else
        echo -e "${RED}✗ Connection issues${NC}"
    fi
    
    # Resource usage
    echo ""
    echo -e "${YELLOW}Resource Usage:${NC}"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" | head -10
}

show_logs() {
    echo -e "${YELLOW}Showing Legal Dashboard logs (Ctrl+C to exit)...${NC}"
    cd $APP_DIR
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE logs -f
}

update_services() {
    echo -e "${YELLOW}Updating Legal Dashboard services...${NC}"
    
    # Pull latest images
    echo -e "${YELLOW}Pulling latest images...${NC}"
    cd $APP_DIR
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE pull
    
    # Restart services
    echo -e "${YELLOW}Restarting services with new images...${NC}"
    restart_services
    
    echo -e "${GREEN}Update completed successfully!${NC}"
}

backup_database() {
    echo -e "${YELLOW}Creating MongoDB Atlas backup...${NC}"
    if [ -f "$APP_DIR/backup-mongodb.sh" ]; then
        $APP_DIR/backup-mongodb.sh
    else
        echo -e "${RED}Error: backup-mongodb.sh not found in $APP_DIR${NC}"
        exit 1
    fi
}

cleanup_docker() {
    echo -e "${YELLOW}Cleaning up unused Docker resources...${NC}"
    
    # Remove unused images
    echo -e "${YELLOW}Removing unused images...${NC}"
    docker image prune -f
    
    # Remove unused volumes
    echo -e "${YELLOW}Removing unused volumes...${NC}"
    docker volume prune -f
    
    # Remove unused networks
    echo -e "${YELLOW}Removing unused networks...${NC}"
    docker network prune -f
    
    # Show remaining usage
    echo -e "${YELLOW}Remaining Docker usage:${NC}"
    docker system df
    
    echo -e "${GREEN}Cleanup completed successfully!${NC}"
}

# Main script logic
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

# Check if running as root (required for most operations)
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run this script as root (use sudo)${NC}"
    exit 1
fi

check_requirements

case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    update)
        update_services
        ;;
    backup)
        backup_database
        ;;
    cleanup)
        cleanup_docker
        ;;
    *)
        echo -e "${RED}Error: Unknown command '$1'${NC}"
        show_usage
        exit 1
        ;;
esac
