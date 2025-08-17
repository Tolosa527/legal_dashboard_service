# Legal Dashboard Service - EC2 Deployment Guide

This guide provides step-by-step instructions for deploying the Legal Dashboard Service MVP on an Amazon EC2 instance.

## Prerequisites

- AWS Account with EC2 access
- Basic knowledge of Linux command line
- SSH key pair for EC2 access
- Domain name (optional, for production setup)

## Table of Contents

1. [EC2 Instance Setup](#ec2-instance-setup)
2. [Server Preparation](#server-preparation)
3. [Application Deployment](#application-deployment)
4. [Production Configuration](#production-configuration)
5. [Security Setup](#security-setup)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)
7. [Troubleshooting](#troubleshooting)

## EC2 Instance Setup

### 1. Launch EC2 Instance

**Recommended Instance Configuration:**
- **Instance Type**: `t3.medium` (2 vCPU, 4 GB RAM) - minimum for MVP
- **Instance Type**: `t3.large` (2 vCPU, 8 GB RAM) - recommended for production
- **AMI**: Ubuntu Server 22.04 LTS (64-bit x86)
- **Storage**: 20-30 GB gp3 SSD
- **Security Group**: Create new security group (see security configuration below)

### 2. Security Group Configuration

Create a security group with the following inbound rules:

| Type | Protocol | Port Range | Source | Description |
|------|----------|------------|---------|-------------|
| SSH | TCP | 22 | Your IP/0.0.0.0/0 | SSH access |
| HTTP | TCP | 80 | 0.0.0.0/0 | HTTP web traffic |
| HTTPS | TCP | 443 | 0.0.0.0/0 | HTTPS web traffic |
| Custom TCP | TCP | 3000 | 0.0.0.0/0 | Reflex Frontend |
| Custom TCP | TCP | 8000 | 0.0.0.0/0 | Reflex Backend API |
| Custom TCP | TCP | 8081 | Your IP only | Mongo Express (optional) |

**Note**: For production, restrict port 3000, 8000, and 8081 to specific IPs or use a load balancer.

### 3. Connect to Instance

```bash
# Replace with your key file and instance public IP
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

## Server Preparation

### 1. Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Docker and Docker Compose

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### 3. Install Git and Essential Tools

```bash
sudo apt install -y git unzip curl wget htop
```

### 4. Configure Firewall (UFW)

```bash
# Enable UFW
sudo ufw enable

# Allow SSH, HTTP, HTTPS
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# Allow application ports
sudo ufw allow 3000  # Reflex Frontend
sudo ufw allow 8000  # Reflex Backend
sudo ufw allow 8081  # Mongo Express (optional)

# Check status
sudo ufw status
```

### 5. Log out and back in

```bash
exit
# SSH back in to reload group membership
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

## Application Deployment

### 1. Clone Repository

```bash
# Clone your repository (replace with your actual repo)
git clone <your-repository-url> legal-dashboard-service
cd legal-dashboard-service

# If you don't have a remote repository, you can upload files via SCP:
# scp -i your-key.pem -r /local/path/to/legal-dashboard-service ubuntu@your-ec2-ip:~/
```

### 2. Create Environment Configuration

```bash
# Create environment file for production
cp deployment/.env.example deployment/.env

# Edit environment variables
nano deployment/.env
```

Add the following to your `.env` file:

```bash
# PostgreSQL Configuration (your external database)
POSTGRES_HOST=read-replica-data-analysis.cmam0b4vdydl.eu-central-1.rds.amazonaws.com
POSTGRES_PORT=5432
POSTGRES_USER=readonly_user
POSTGRES_PASSWORD=pR-0l7chJy5tK1@n.r0_K
POSTGRES_DB=production-core

# MongoDB Configuration
MONGO_HOST=mongodb
MONGO_PORT=27017
MONGO_DB=legal_dashboard
MONGO_USERNAME=admin
MONGO_PASSWORD=your_secure_mongo_password_here

# Application Configuration
SYNC_HOURS=24
ENVIRONMENT=production

# Security - Generate strong passwords
MONGO_ROOT_PASSWORD=your_very_secure_root_password_here
MONGO_EXPRESS_PASSWORD=your_secure_express_password_here
```

### 3. Update Docker Compose for Production

Create a production Docker Compose override:

```bash
nano deployment/docker-compose.prod.yml
```

```yaml
services:
  mongodb:
    restart: always
    environment:
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_ROOT_PASSWORD}
    volumes:
      - /data/mongodb:/data/db

  mongo-express:
    restart: always
    environment:
      ME_CONFIG_BASICAUTH_PASSWORD: ${MONGO_EXPRESS_PASSWORD}
    # Comment out ports for security in production
    # ports:
    #   - "8081:8081"

  reflex-app:
    restart: always
    environment:
      MONGO_PASSWORD: ${MONGO_ROOT_PASSWORD}

  data-sync:
    restart: "no"  # Only run when needed
```

### 4. Create Data Directory

```bash
sudo mkdir -p /data/mongodb
sudo chown -R 999:999 /data/mongodb
```

### 5. Start Services

```bash
# Make scripts executable
chmod +x docker-manage.sh

# Start all services
./docker-manage.sh start

# Check status
./docker-manage.sh status
```

### 6. Verify Deployment

```bash
# Check if services are running
docker ps

# Check logs
./docker-manage.sh logs

# Test application
curl http://localhost:3000
```

## Production Configuration

### 1. Set up Reverse Proxy with Nginx

```bash
# Install Nginx
sudo apt install -y nginx

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/legal-dashboard
```

Nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;  # Replace with your domain

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
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
```

Enable the site:

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/legal-dashboard /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 2. Set up SSL with Let's Encrypt (Optional)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

### 3. Set up Systemd Service for Auto-start

```bash
sudo nano /etc/systemd/system/legal-dashboard.service
```

```ini
[Unit]
Description=Legal Dashboard Service
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/legal-dashboard-service
ExecStart=/home/ubuntu/legal-dashboard-service/docker-manage.sh start
ExecStop=/home/ubuntu/legal-dashboard-service/docker-manage.sh stop
User=ubuntu
Group=ubuntu

[Install]
WantedBy=multi-user.target
```

Enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable legal-dashboard.service
sudo systemctl start legal-dashboard.service
```

## Security Setup

### 1. Secure MongoDB

Update your MongoDB configuration to use authentication and secure passwords in `deployment/.env`:

```bash
# Generate secure passwords
MONGO_ROOT_PASSWORD=$(openssl rand -base64 32)
MONGO_EXPRESS_PASSWORD=$(openssl rand -base64 32)
echo "MongoDB Root Password: $MONGO_ROOT_PASSWORD"
echo "Mongo Express Password: $MONGO_EXPRESS_PASSWORD"
```

### 2. Disable Direct Port Access

Update security group to remove direct access to ports 3000, 8000, 8081 and only allow HTTP/HTTPS through Nginx.

### 3. Regular Security Updates

```bash
# Create update script
cat > /home/ubuntu/update-system.sh << 'EOF'
#!/bin/bash
sudo apt update && sudo apt upgrade -y
sudo apt autoremove -y
sudo apt autoclean
EOF

chmod +x /home/ubuntu/update-system.sh

# Add to cron for weekly updates
echo "0 2 * * 0 /home/ubuntu/update-system.sh" | sudo crontab -
```

## Monitoring and Maintenance

### 1. Set up Log Rotation

```bash
sudo nano /etc/logrotate.d/legal-dashboard
```

```
/var/log/legal-dashboard/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
    postrotate
        docker restart legal_dashboard_reflex || true
    endscript
}
```

### 2. Create Backup Script

```bash
nano /home/ubuntu/backup-mongodb.sh
```

```bash
#!/bin/bash

BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)
MONGO_CONTAINER="legal_dashboard_mongodb"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create MongoDB backup
docker exec $MONGO_CONTAINER mongodump --username admin --password adminpassword --authenticationDatabase admin --out /data/backup_$DATE

# Copy backup from container
docker cp $MONGO_CONTAINER:/data/backup_$DATE $BACKUP_DIR/

# Compress backup
tar -czf $BACKUP_DIR/mongodb_backup_$DATE.tar.gz -C $BACKUP_DIR backup_$DATE

# Remove uncompressed backup
rm -rf $BACKUP_DIR/backup_$DATE

# Keep only last 7 days of backups
find $BACKUP_DIR -name "mongodb_backup_*.tar.gz" -mtime +7 -delete

echo "MongoDB backup completed: mongodb_backup_$DATE.tar.gz"
```

```bash
chmod +x /home/ubuntu/backup-mongodb.sh

# Add to cron for daily backups
echo "0 3 * * * /home/ubuntu/backup-mongodb.sh" | crontab -
```

### 3. Monitoring Script

```bash
nano /home/ubuntu/monitor-services.sh
```

```bash
#!/bin/bash

# Check if services are running
cd /home/ubuntu/legal-dashboard-service

echo "=== Service Status $(date) ==="
./docker-manage.sh status

echo -e "\n=== Disk Usage ==="
df -h

echo -e "\n=== Memory Usage ==="
free -h

echo -e "\n=== CPU Load ==="
uptime

echo -e "\n=== Docker Stats ==="
docker stats --no-stream

# Check if application is responding
echo -e "\n=== Application Health Check ==="
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is responding"
else
    echo "❌ Frontend is not responding"
fi

if curl -f http://localhost:8000 > /dev/null 2>&1; then
    echo "✅ Backend is responding"
else
    echo "❌ Backend is not responding"
fi
```

```bash
chmod +x /home/ubuntu/monitor-services.sh
```

## Deployment Commands Reference

### Application Management

```bash
# Start all services
./docker-manage.sh start

# Stop all services
./docker-manage.sh stop

# Restart all services
./docker-manage.sh restart

# View logs
./docker-manage.sh logs

# Check status
./docker-manage.sh status

# Sync data only
./docker-manage.sh sync

# Rebuild and restart Reflex app
./docker-manage.sh reflex-rebuild
```

### System Management

```bash
# Check system resources
htop

# Check disk space
df -h

# Check service status
sudo systemctl status legal-dashboard

# Check nginx status
sudo systemctl status nginx

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Troubleshooting

### Common Issues

1. **Services won't start**
   ```bash
   # Check Docker daemon
   sudo systemctl status docker
   
   # Check logs
   ./docker-manage.sh logs
   
   # Restart Docker
   sudo systemctl restart docker
   ```

2. **MongoDB connection issues**
   ```bash
   # Check MongoDB container
   docker logs legal_dashboard_mongodb
   
   # Test MongoDB connection
   ./docker-manage.sh shell-mongo
   ```

3. **Application not accessible from browser**
   ```bash
   # Check if services are running on correct ports
   sudo netstat -tulpn | grep -E "(3000|8000)"
   
   # Check firewall
   sudo ufw status
   
   # Check nginx configuration
   sudo nginx -t
   ```

4. **High memory usage**
   ```bash
   # Check Docker memory usage
   docker stats
   
   # Restart services to free memory
   ./docker-manage.sh restart
   ```

5. **Data sync failures**
   ```bash
   # Check data sync logs
   docker logs legal_dashboard_data_sync
   
   # Verify PostgreSQL connection
   # Check environment variables in deployment/.env
   ```

### Getting Help

- Check application logs: `./docker-manage.sh logs`
- Monitor system resources: `htop` and `df -h`
- Check Docker status: `docker ps` and `docker stats`
- Review nginx logs: `sudo tail -f /var/log/nginx/error.log`

### Performance Optimization

For better performance on larger datasets:

1. **Upgrade Instance Type**: Consider t3.large or c5.large for production
2. **Optimize MongoDB**: Add proper indexes and configure memory settings
3. **Use CloudFront**: Set up AWS CloudFront for static asset caching
4. **Database Optimization**: Consider MongoDB Atlas for managed database
5. **Load Balancing**: Use AWS Application Load Balancer for high availability

## Next Steps

After successful deployment:

1. Set up monitoring with CloudWatch or external services
2. Implement automated deployments with GitHub Actions or AWS CodeDeploy
3. Configure database backups to S3
4. Set up health checks and alerts
5. Consider using AWS RDS for PostgreSQL if needed
6. Implement proper logging and error tracking

---

**Note**: Remember to replace placeholder values (domains, passwords, IPs) with your actual values before deployment.
