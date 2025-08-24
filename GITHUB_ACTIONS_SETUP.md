# GitHub Actions CI/CD Setup

This document explains how to set up GitHub Actions for automated building and deployment of the Legal Dashboard Service.

## Overview

The project includes two GitHub Actions workflows:

1. **Build and Push** (`build-and-push.yml`) - Automatically builds and pushes Docker images
2. **Deploy to EC2** (`deploy-ec2.yml`) - Manually triggered deployment to EC2 instances

## Setup Instructions

### 1. GitHub Container Registry

The workflows are configured to use GitHub Container Registry (ghcr.io) by default. This provides:
- Free hosting for public repositories
- Automatic authentication using `GITHUB_TOKEN`
- Integration with GitHub packages

### 2. Required Secrets

For the deployment workflow to work, you need to set up the following secrets in your GitHub repository:

#### Repository Secrets

Go to your repository → Settings → Secrets and variables → Actions, then add:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `EC2_SSH_PRIVATE_KEY` | Private SSH key for EC2 access | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `EC2_HOST` | EC2 instance public IP or domain | `52.123.456.789` or `my-app.example.com` |
| `EC2_USER` | SSH username for EC2 | `ubuntu` (for Ubuntu) or `ec2-user` (for Amazon Linux) |

#### Environment Secrets (Optional)

You can also create environment-specific secrets:
- Go to Settings → Environments
- Create environments: `production`, `staging`
- Add environment-specific secrets if needed

### 3. Setting up SSH Access

#### Generate SSH Key Pair

```bash
# Generate a new SSH key pair (don't use a passphrase for automation)
ssh-keygen -t ed25519 -f ~/.ssh/legal_dashboard_deploy -N ""

# Copy the public key to your EC2 instance
ssh-copy-id -i ~/.ssh/legal_dashboard_deploy.pub ubuntu@YOUR_EC2_IP
```

#### Add Private Key to GitHub Secrets

```bash
# Display the private key (copy this to GitHub secrets)
cat ~/.ssh/legal_dashboard_deploy
```

Copy the entire private key (including the `-----BEGIN` and `-----END` lines) and add it as the `EC2_SSH_PRIVATE_KEY` secret.

## Workflows

### Build and Push Workflow

**Trigger:** Automatically runs on:
- Push to `main` or `master` branches
- Push of version tags (e.g., `v1.0.0`)
- Pull requests (builds only, doesn't push)

**What it does:**
- Builds three Docker images: backend, frontend, and sync
- Pushes images to GitHub Container Registry
- Supports multi-platform builds (amd64, arm64)
- Uses build caching for faster builds

**Image naming:**
- Backend: `ghcr.io/tolosa527/legal_dashboard_service-backend:latest`
- Frontend: `ghcr.io/tolosa527/legal_dashboard_service-frontend:latest`
- Sync: `ghcr.io/tolosa527/legal_dashboard_service-sync:latest`

### Deploy to EC2 Workflow

**Trigger:** Manual dispatch from GitHub Actions tab

**Inputs:**
- `environment`: Choose between `production` or `staging`
- `tag`: Docker image tag to deploy (default: `latest`)

**What it does:**
- Copies deployment files to EC2
- Updates environment configuration
- Pulls latest Docker images
- Restarts services
- Verifies deployment health

## Using the Workflows

### 1. Automatic Build and Push

Simply push your code to the main branch:

```bash
git add .
git commit -m "Update application"
git push origin main
```

The workflow will automatically build and push new Docker images.

### 2. Manual Deployment

1. Go to your repository on GitHub
2. Click on the "Actions" tab
3. Select "Deploy to EC2" from the workflows list
4. Click "Run workflow"
5. Choose the environment and tag
6. Click "Run workflow" button

### 3. Version Releases

For versioned releases:

```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0
```

This will build images with both `latest` and `v1.0.0` tags.

## EC2 Preparation

### Initial Setup

Before using the deployment workflow, your EC2 instance should be prepared:

1. **Install Docker and Docker Compose**
2. **Create application directory structure**
3. **Set up the initial environment file**

You can use the `deploy-ec2.sh` script for initial setup:

```bash
# Upload and run the initial deployment script
scp deployment/deploy-ec2.sh ubuntu@YOUR_EC2_IP:/tmp/
ssh ubuntu@YOUR_EC2_IP "sudo /tmp/deploy-ec2.sh"
```

### Environment File Setup

Create `/opt/legal_dashboard/.env.prod` on your EC2 instance:

```bash
# Copy the template and customize it
sudo cp deployment/.env.prod /opt/legal_dashboard/.env.prod

# Edit with your specific configuration
sudo nano /opt/legal_dashboard/.env.prod
```

Make sure to update:
- `MONGO_URI`: Your MongoDB Atlas connection string
- `API_URL`: Your EC2 instance public IP or domain
- Other environment-specific settings

## Security Considerations

### SSH Key Security

- Use a dedicated SSH key pair for deployment
- Don't use a passphrase for automation keys
- Regularly rotate SSH keys
- Limit SSH key permissions on EC2

### GitHub Secrets

- Never commit secrets to the repository
- Use environment-specific secrets when possible
- Regularly audit and rotate secrets
- Enable secret scanning in repository settings

### Container Registry

- GitHub Container Registry is free for public repositories
- Consider using private repositories for sensitive applications
- Regularly update base images for security patches

## Troubleshooting

### Common Issues

1. **SSH Connection Failed**
   - Verify EC2 security group allows SSH (port 22)
   - Check that the SSH key is correct
   - Ensure EC2 instance is running

2. **Docker Build Failed**
   - Check the Dockerfile syntax
   - Verify all required files are included
   - Review build logs in GitHub Actions

3. **Deployment Failed**
   - Check EC2 instance has enough resources
   - Verify MongoDB Atlas connectivity
   - Review application logs on EC2

### Viewing Logs

```bash
# View GitHub Actions logs
# Go to Actions tab → Select workflow run → View job details

# View application logs on EC2
ssh ubuntu@YOUR_EC2_IP
sudo /opt/legal_dashboard/manage.sh logs
```

## Monitoring and Maintenance

### Health Checks

The workflows include health checks to verify:
- Services are running
- Health endpoints respond correctly
- Database connectivity works

### Automated Backups

Consider setting up automated backups:

```bash
# Add to crontab on EC2
sudo crontab -e

# Add this line for daily backups at 2 AM
0 2 * * * /opt/legal_dashboard/backup-mongodb.sh
```

### Monitoring

Set up monitoring for:
- Application uptime
- Resource usage (CPU, memory, disk)
- Database connectivity
- SSL certificate expiration

## Best Practices

1. **Version Tagging**: Use semantic versioning for releases
2. **Environment Separation**: Use different environments for testing and production
3. **Rollback Strategy**: Keep previous image versions for quick rollbacks
4. **Security Updates**: Regularly update base images and dependencies
5. **Monitoring**: Implement comprehensive monitoring and alerting
6. **Documentation**: Keep deployment documentation updated
