#!/bin/bash

# Legal Dashboard Service - Monitoring and Maintenance Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
LOG_FILE="/var/log/legal-dashboard-monitor.log"
ALERT_EMAIL=""  # Set email for alerts
BACKUP_DIR="/home/ubuntu/backups"

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> $LOG_FILE 2>/dev/null || true
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1" >> $LOG_FILE 2>/dev/null || true
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1" >> $LOG_FILE 2>/dev/null || true
}

# Function to check service health
check_health() {
    log "🏥 Running health checks..."
    
    local issues=0
    
    # Check if Docker is running
    if ! systemctl is-active --quiet docker; then
        error "Docker service is not running"
        ((issues++))
    else
        log "✅ Docker service is running"
    fi
    
    # Check if containers are running
    local containers=$(docker ps --filter "name=legal_dashboard" --format "table {{.Names}}\t{{.Status}}" 2>/dev/null)
    if [ -z "$containers" ]; then
        error "No Legal Dashboard containers are running"
        ((issues++))
    else
        log "✅ Legal Dashboard containers are running:"
        echo "$containers"
    fi
    
    # Check if frontend is responding
    if curl -f -s http://localhost:3000 > /dev/null; then
        log "✅ Frontend is responding (port 3000)"
    else
        error "Frontend is not responding (port 3000)"
        ((issues++))
    fi
    
    # Check if backend is responding
    if curl -f -s http://localhost:8000 > /dev/null; then
        log "✅ Backend is responding (port 8000)"
    else
        error "Backend is not responding (port 8000)"
        ((issues++))
    fi
    
    # Check if Nginx is running
    if systemctl is-active --quiet nginx; then
        log "✅ Nginx is running"
        
        # Test Nginx configuration
        if nginx -t &>/dev/null; then
            log "✅ Nginx configuration is valid"
        else
            error "Nginx configuration has errors"
            ((issues++))
        fi
    else
        error "Nginx is not running"
        ((issues++))
    fi
    
    # Check disk space
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 80 ]; then
        warn "Disk usage is high: ${disk_usage}%"
        ((issues++))
    else
        log "✅ Disk usage is normal: ${disk_usage}%"
    fi
    
    # Check memory usage
    local mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    if [ "$mem_usage" -gt 90 ]; then
        warn "Memory usage is high: ${mem_usage}%"
    else
        log "✅ Memory usage is normal: ${mem_usage}%"
    fi
    
    return $issues
}

# Function to show system status
show_status() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Legal Dashboard System Status ${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    
    # System information
    echo -e "${YELLOW}System Information:${NC}"
    echo "Uptime: $(uptime -p)"
    echo "Load: $(uptime | awk -F'load average:' '{print $2}')"
    echo "Disk Usage: $(df -h / | tail -1 | awk '{print $5 " used of " $2}')"
    echo "Memory: $(free -h | grep Mem | awk '{print $3 " used of " $2}')"
    echo ""
    
    # Docker status
    echo -e "${YELLOW}Docker Containers:${NC}"
    docker ps --filter "name=legal_dashboard" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "No containers running"
    echo ""
    
    # Service status
    echo -e "${YELLOW}Service Status:${NC}"
    echo -n "Docker: "
    systemctl is-active docker
    echo -n "Nginx: "
    systemctl is-active nginx
    echo -n "Legal Dashboard: "
    systemctl is-active legal-dashboard 2>/dev/null || echo "inactive"
    echo ""
    
    # Port status
    echo -e "${YELLOW}Port Status:${NC}"
    echo -n "Port 3000 (Frontend): "
    if curl -f -s http://localhost:3000 > /dev/null; then
        echo -e "${GREEN}✅ Active${NC}"
    else
        echo -e "${RED}❌ Not responding${NC}"
    fi
    
    echo -n "Port 8000 (Backend): "
    if curl -f -s http://localhost:8000 > /dev/null; then
        echo -e "${GREEN}✅ Active${NC}"
    else
        echo -e "${RED}❌ Not responding${NC}"
    fi
    
    echo -n "Port 80 (Nginx): "
    if curl -f -s http://localhost > /dev/null; then
        echo -e "${GREEN}✅ Active${NC}"
    else
        echo -e "${RED}❌ Not responding${NC}"
    fi
}

# Function to backup MongoDB
backup_mongodb() {
    log "🗃️ Starting MongoDB backup..."
    
    mkdir -p "$BACKUP_DIR"
    local date=$(date +%Y%m%d_%H%M%S)
    local backup_name="mongodb_backup_$date"
    
    # Create backup
    if docker exec legal_dashboard_mongodb mongodump \
        --username admin \
        --password adminpassword \
        --authenticationDatabase admin \
        --out "/data/$backup_name" &>/dev/null; then
        
        # Copy backup from container
        docker cp "legal_dashboard_mongodb:/data/$backup_name" "$BACKUP_DIR/"
        
        # Compress backup
        tar -czf "$BACKUP_DIR/$backup_name.tar.gz" -C "$BACKUP_DIR" "$backup_name"
        rm -rf "$BACKUP_DIR/$backup_name"
        
        # Clean old backups (keep last 7 days)
        find "$BACKUP_DIR" -name "mongodb_backup_*.tar.gz" -mtime +7 -delete
        
        log "✅ MongoDB backup completed: $backup_name.tar.gz"
    else
        error "MongoDB backup failed"
        return 1
    fi
}

# Function to restart services
restart_services() {
    log "🔄 Restarting Legal Dashboard services..."
    
    cd "$(dirname "$0")"
    
    if [ -f "docker-manage.sh" ]; then
        ./docker-manage.sh restart
        log "✅ Services restarted"
    else
        error "docker-manage.sh not found"
        return 1
    fi
}

# Function to update system
update_system() {
    log "🔄 Updating system packages..."
    
    sudo apt update && sudo apt upgrade -y
    sudo apt autoremove -y
    sudo apt autoclean
    
    log "✅ System update completed"
}

# Function to clean up Docker
cleanup_docker() {
    log "🧹 Cleaning up Docker..."
    
    # Remove unused containers, networks, images
    docker system prune -f
    
    log "✅ Docker cleanup completed"
}

# Function to view logs
view_logs() {
    local service="$1"
    
    cd "$(dirname "$0")"
    
    if [ -z "$service" ]; then
        echo "Available log commands:"
        echo "  app          - Application logs"
        echo "  nginx        - Nginx logs"
        echo "  system       - System logs"
        echo "  monitor      - Monitor logs"
        return
    fi
    
    case "$service" in
        "app")
            if [ -f "docker-manage.sh" ]; then
                ./docker-manage.sh logs
            else
                error "docker-manage.sh not found"
            fi
            ;;
        "nginx")
            sudo tail -f /var/log/nginx/access.log /var/log/nginx/error.log
            ;;
        "system")
            sudo journalctl -f -u legal-dashboard
            ;;
        "monitor")
            tail -f "$LOG_FILE" 2>/dev/null || echo "No monitor log file found"
            ;;
        *)
            error "Unknown log service: $service"
            ;;
    esac
}

# Main script logic
case "${1:-status}" in
    "health"|"check")
        check_health
        ;;
    "status")
        show_status
        ;;
    "backup")
        backup_mongodb
        ;;
    "restart")
        restart_services
        ;;
    "update")
        update_system
        ;;
    "cleanup")
        cleanup_docker
        ;;
    "logs")
        view_logs "$2"
        ;;
    "monitor")
        log "🔍 Starting continuous monitoring (Ctrl+C to stop)..."
        while true; do
            check_health > /dev/null
            sleep 300  # Check every 5 minutes
        done
        ;;
    *)
        echo "Legal Dashboard Monitoring Script"
        echo "Usage: $0 {health|status|backup|restart|update|cleanup|logs|monitor}"
        echo ""
        echo "Commands:"
        echo "  health       - Run health checks"
        echo "  status       - Show system status"
        echo "  backup       - Backup MongoDB"
        echo "  restart      - Restart services"
        echo "  update       - Update system packages"
        echo "  cleanup      - Clean up Docker"
        echo "  logs [type]  - View logs (app|nginx|system|monitor)"
        echo "  monitor      - Continuous monitoring"
        exit 1
        ;;
esac
