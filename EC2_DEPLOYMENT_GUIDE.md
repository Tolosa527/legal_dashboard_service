# Legal Dashboard Service - EC2 Deployment Guide

This guide will help you deploy the Legal Dashboard Service to an AWS EC2 instance using Docker.

## Prerequisites

1. **AWS EC2 Instance**
   - Recommended: t3.medium or larger (2 vCPU, 4GB RAM minimum)
   - Operating System: Ubuntu 22.04 LTS or Amazon Linux 2
   - Storage: At least 20GB SSD
   - Security Group: Allow inbound traffic on ports 22 (SSH), 80 (HTTP), and 443 (HTTPS)

2. **GitHub Repository with Actions**
   - Repository with GitHub Actions enabled
   - SSH access configured for EC2 deployment
   - See `GITHUB_ACTIONS_SETUP.md` for detailed setup

3. **MongoDB Atlas Cluster**
   - MongoDB Atlas account with a configured cluster
   - Database user with read/write permissions
   - Network access configured (whitelist your EC2 IP or use 0.0.0.0/0)

4. **Domain Name (Optional)**
   - For HTTPS/SSL configuration

## Deployment Steps

### Step 1: Prepare Your Local Environment

1. **Configure Environment Variables**
   ```bash
   cd deployment
   cp .env.prod .env.prod.local
   # Edit .env.prod.local with your specific configuration
   ```

2. **Update Configuration in .env.prod.local**
   ```bash
   # Application Configuration
   APP_NAME=legal-dashboard
   DOCKER_REGISTRY=ghcr.io/tolosa527/legal_dashboard_service  # GitHub Container Registry
   TAG=latest
   
   # API Configuration - Replace with your EC2 instance public IP or domain
   API_URL=http://YOUR-EC2-PUBLIC-IP:8000
   
   # MongoDB Atlas Configuration
   MONGO_URI=mongodb+srv://your_username:your_password@your-cluster.mongodb.net/legal_dashboard?retryWrites=true&w=majority
   MONGO_DB=legal_dashboard
   ```

### Step 2: Build and Push Docker Images (GitHub Actions)

**Note:** Images are automatically built and pushed using GitHub Actions. See `GITHUB_ACTIONS_SETUP.md` for configuration.

1. **Push your code to trigger builds**
   ```bash
   git add .
   git commit -m "Deploy to production"
   git push origin main
   ```

2. **Or create a release tag**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

The GitHub Actions workflow will automatically build and push the Docker images to GitHub Container Registry.

### Step 3: Set Up EC2 Instance

1. **Connect to your EC2 instance**
   ```bash
   ssh -i your-key.pem ubuntu@YOUR-EC2-PUBLIC-IP
   ```

2. **Upload deployment files**
   ```bash
   # From your local machine, upload necessary files
   scp -i your-key.pem .env.prod.local ubuntu@YOUR-EC2-PUBLIC-IP:/tmp/.env.prod
   scp -i your-key.pem docker-compose.prod.yml ubuntu@YOUR-EC2-PUBLIC-IP:/tmp/
   scp -i your-key.pem nginx.conf ubuntu@YOUR-EC2-PUBLIC-IP:/tmp/
   scp -i your-key.pem deploy-ec2.sh ubuntu@YOUR-EC2-PUBLIC-IP:/tmp/
   ```

3. **Run deployment script on EC2**
   ```bash
   # On your EC2 instance
   sudo cp /tmp/.env.prod /opt/legal_dashboard/
   sudo cp /tmp/docker-compose.prod.yml /opt/legal_dashboard/
   sudo cp /tmp/nginx.conf /opt/legal_dashboard/
   sudo cp /tmp/deploy-ec2.sh /opt/legal_dashboard/
   
   cd /opt/legal_dashboard
   sudo ./deploy-ec2.sh
   ```

### Step 5: Verify Deployment

1. **Check service status**
   ```bash
   sudo systemctl status legal-dashboard
   sudo docker-compose -f /opt/legal_dashboard/docker-compose.prod.yml ps
   ```

2. **View logs**
   ```bash
   sudo docker-compose -f /opt/legal_dashboard/docker-compose.prod.yml logs -f
   ```

3. **Test the application**
   - Open your browser and navigate to `http://YOUR-EC2-PUBLIC-IP`
   - You should see the Legal Dashboard interface
   ```

### Step 4: Deploy Using GitHub Actions (Recommended)

**Option A: Automated Deployment via GitHub Actions**

1. **Set up GitHub Actions secrets** (see `GITHUB_ACTIONS_SETUP.md`)
   - `EC2_SSH_PRIVATE_KEY`
   - `EC2_HOST`
   - `EC2_USER`

2. **Deploy from GitHub**
   - Go to your repository's Actions tab
   - Select "Deploy to EC2" workflow
   - Click "Run workflow"
   - Choose environment and tag
   - Click "Run workflow"

**Option B: Manual Deployment on EC2**

1. **Initial setup on EC2**

1. **Check service status**
   ```bash
   sudo systemctl status legal-dashboard
   sudo docker-compose -f /opt/legal_dashboard/docker-compose.prod.yml ps
   ```

2. **View logs**
   ```bash
   sudo docker-compose -f /opt/legal_dashboard/docker-compose.prod.yml logs -f
   ```

3. **Test the application**
   - Open your browser and navigate to `http://YOUR-EC2-PUBLIC-IP`
   - You should see the Legal Dashboard interface

## SSL/HTTPS Configuration (Optional)

### Option 1: Using Let's Encrypt with Certbot

1. **Install Certbot**
   ```bash
   sudo apt-get update
   sudo apt-get install certbot python3-certbot-nginx
   ```

2. **Obtain SSL certificate**
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

3. **Update nginx configuration**
   The certbot will automatically update your nginx configuration for HTTPS.

### Option 2: Manual SSL Certificate

1. **Upload your SSL certificates to EC2**
   ```bash
   sudo mkdir -p /opt/legal_dashboard/ssl
   sudo cp your-certificate.crt /opt/legal_dashboard/ssl/cert.pem
   sudo cp your-private-key.key /opt/legal_dashboard/ssl/key.pem
   ```

2. **Update nginx.conf**
   Uncomment the HTTPS server block in the nginx.conf file and update the server_name.

3. **Restart services**
   ```bash
   sudo systemctl restart legal-dashboard
   ```

## Monitoring and Maintenance

### Health Checks

The deployment includes health checks for all services:
- Frontend: `http://YOUR-EC2-IP/health`
- Backend: `http://YOUR-EC2-IP:8000/ping`
- MongoDB: Built-in Docker health check

### Log Management

- **Application logs**: `sudo docker-compose -f /opt/legal_dashboard/docker-compose.prod.yml logs`
- **Nginx logs**: `sudo docker logs legal_dashboard_nginx_prod`
- **System logs**: `sudo journalctl -u legal-dashboard`

### Backup Strategy

1. **MongoDB Atlas Automated Backups**
   - MongoDB Atlas provides automatic backups (Point-in-Time Recovery)
   - Configure backup schedule in Atlas dashboard
   - Download backups as needed through Atlas UI

2. **Manual Database Backup**
   ```bash
   # Create manual backup using the backup script
   sudo /opt/legal_dashboard/backup-mongodb.sh
   ```

3. **Automated Backup Script**
   ```bash
   # Create a cron job for additional local backups
   sudo crontab -e
   # Add: 0 2 * * * /opt/legal_dashboard/backup-mongodb.sh
   ```

### Updates

1. **Update application**
   ```bash
   # Pull new images
   sudo docker-compose -f /opt/legal_dashboard/docker-compose.prod.yml pull
   
   # Restart services
   sudo systemctl restart legal-dashboard
   ```

2. **Update system packages**
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   sudo reboot  # If kernel updates were installed
   ```

## Troubleshooting

### Common Issues

1. **Service won't start**
   - Check logs: `sudo docker-compose -f /opt/legal_dashboard/docker-compose.prod.yml logs`
   - Verify environment variables in `.env.prod`
   - Ensure images are accessible from your registry

2. **Database connection issues**
   - Check MongoDB Atlas network access settings
   - Verify MongoDB URI in environment file
   - Ensure EC2 instance IP is whitelisted in Atlas
   - Test connectivity: `mongosh "your-atlas-connection-string"`

3. **Frontend/Backend communication issues**
   - Verify API_URL in environment file
   - Check nginx configuration
   - Ensure security groups allow traffic on required ports

### Useful Commands

```bash
# View all container status
sudo docker ps -a

# View Docker images
sudo docker images

# Clean up unused Docker resources
sudo docker system prune -a

# Restart specific service
sudo docker-compose -f /opt/legal_dashboard/docker-compose.prod.yml restart reflex-backend

# Test MongoDB Atlas connection
mongosh "your-atlas-connection-string"

# Check application connectivity to Atlas
curl -f http://localhost:8000/api/health/db
```

## Security Considerations

1. **Change default passwords** in `.env.prod`
2. **Use strong passwords** for all services
3. **Enable firewall** (UFW) with only necessary ports open
4. **Regular security updates** for the OS and Docker
5. **Monitor access logs** regularly
6. **Use HTTPS** in production
7. **Restrict SSH access** to specific IP addresses if possible

## Performance Optimization

1. **Monitor resource usage**
   ```bash
   sudo docker stats
   htop
   ```

2. **Adjust container resources** if needed in docker-compose.prod.yml
3. **Consider using** AWS RDS for MongoDB in production
4. **Set up CloudWatch** monitoring for EC2 instance
5. **Use Application Load Balancer** for high availability

## Support

For issues specific to the Legal Dashboard Service, check:
- Application logs for backend errors
- Browser console for frontend issues
- MongoDB logs for database issues
- Nginx logs for proxy/routing issues
