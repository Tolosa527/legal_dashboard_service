# Legal Dashboard Service - EC2 Deployment

This directory contains everything needed to deploy the Legal Dashboard Service MVP on an Amazon EC2 instance.

## 📋 Quick Start

For a rapid deployment on a fresh EC2 instance:

```bash
# Option 1: Automated deployment (if repository is public)
curl -sSL https://raw.githubusercontent.com/your-repo/legal-dashboard-service/main/quick-start-ec2.sh | bash

# Option 2: Manual deployment
git clone <your-repository-url>
cd legal-dashboard-service
chmod +x deploy-ec2.sh
./deploy-ec2.sh
```

## 📁 Deployment Files

| File | Purpose |
|------|---------|
| `EC2_DEPLOYMENT_GUIDE.md` | Comprehensive deployment guide with all details |
| `deploy-ec2.sh` | Automated deployment script |
| `quick-start-ec2.sh` | One-liner deployment for fresh instances |
| `monitor.sh` | System monitoring and maintenance script |
| `deployment/.env.example` | Environment configuration template |
| `deployment/docker-compose.prod.yml` | Production Docker Compose overrides |

## 🚀 Deployment Options

### 1. Automated Deployment (Recommended)

The automated deployment script handles everything:

```bash
./deploy-ec2.sh
```

This script will:
- ✅ Install Docker and Docker Compose
- ✅ Configure firewall (UFW)
- ✅ Install and configure Nginx reverse proxy
- ✅ Create systemd service for auto-start
- ✅ Set up environment configuration
- ✅ Start all services
- ✅ Run health checks

### 2. Manual Deployment

Follow the detailed guide in `EC2_DEPLOYMENT_GUIDE.md` for step-by-step manual deployment.

### 3. Production Deployment

For production environments, use the production Docker Compose override:

```bash
# Copy and edit environment file
cp deployment/.env.example deployment/.env
nano deployment/.env

# Start with production configuration
docker-compose -f deployment/docker-compose.yml -f deployment/docker-compose.prod.yml up -d
```

## 🔧 Configuration

### Environment Variables

Edit `deployment/.env` with your configuration:

```bash
# Database configuration
POSTGRES_HOST=your-postgres-host
POSTGRES_USER=your-username
POSTGRES_PASSWORD=your-password

# Security (IMPORTANT: Change these!)
MONGO_ROOT_PASSWORD=your-secure-password
MONGO_EXPRESS_PASSWORD=your-express-password
```

### Production Considerations

- **Security**: Update all default passwords
- **SSL**: Set up SSL certificates with Let's Encrypt
- **Domain**: Configure your domain name in Nginx
- **Monitoring**: Set up CloudWatch or external monitoring
- **Backups**: Configure automated backups

## 📊 Monitoring and Maintenance

Use the monitoring script for system management:

```bash
# Check system status
./monitor.sh status

# Run health checks
./monitor.sh health

# Backup MongoDB
./monitor.sh backup

# Restart services
./monitor.sh restart

# View logs
./monitor.sh logs app

# Continuous monitoring
./monitor.sh monitor
```

## 🛠️ Service Management

### Docker Management

```bash
# Start all services
./docker-manage.sh start

# Stop all services
./docker-manage.sh stop

# View logs
./docker-manage.sh logs

# Check status
./docker-manage.sh status
```

### System Service Management

```bash
# Start/stop/restart the systemd service
sudo systemctl start legal-dashboard
sudo systemctl stop legal-dashboard
sudo systemctl restart legal-dashboard

# Check service status
sudo systemctl status legal-dashboard

# Enable/disable auto-start
sudo systemctl enable legal-dashboard
sudo systemctl disable legal-dashboard
```

## 🌐 Access URLs

After deployment, access your application at:

- **Frontend**: `http://your-ec2-ip/` or `http://your-domain.com/`
- **API**: `http://your-ec2-ip/api` or `http://your-domain.com/api`
- **MongoDB Admin**: `http://your-ec2-ip:8081` (if enabled)

## 🔒 Security Checklist

- [ ] Update default MongoDB passwords
- [ ] Configure SSL certificates
- [ ] Set up firewall rules
- [ ] Disable direct port access (use Nginx proxy only)
- [ ] Set up regular security updates
- [ ] Configure backup strategy
- [ ] Set up monitoring and alerting

## 🆘 Troubleshooting

### Common Issues

1. **Services not starting**
   ```bash
   ./monitor.sh health
   ./monitor.sh logs app
   ```

2. **Port conflicts**
   ```bash
   sudo netstat -tulpn | grep -E "(3000|8000|80)"
   ```

3. **Memory issues**
   ```bash
   ./monitor.sh status
   docker stats
   ```

4. **Database connection issues**
   ```bash
   ./docker-manage.sh logs
   ```

### Getting Help

- Check the comprehensive guide: `EC2_DEPLOYMENT_GUIDE.md`
- Run health checks: `./monitor.sh health`
- View application logs: `./monitor.sh logs app`
- Check system status: `./monitor.sh status`

## 📈 Scaling and Production

For production deployments, consider:

- **Load Balancer**: Use AWS Application Load Balancer
- **Auto Scaling**: Set up Auto Scaling Groups
- **Database**: Use managed MongoDB Atlas
- **CDN**: Configure CloudFront for static assets
- **Monitoring**: Implement comprehensive monitoring
- **CI/CD**: Set up automated deployments

## 📝 Notes

- Default MongoDB credentials are in the environment file
- Nginx serves as a reverse proxy for the application
- The application auto-starts on system boot
- Logs are rotated automatically
- Backups should be configured for production use

---

For detailed instructions and troubleshooting, see the complete guide in `EC2_DEPLOYMENT_GUIDE.md`.
