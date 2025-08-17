#!/bin/bash

# Legal Dashboard Service - Quick Start Script for EC2
# This script provides a one-liner setup for EC2 deployment

set -e

echo "🚀 Legal Dashboard Service - EC2 Quick Start"
echo "============================================"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "📦 Installing git..."
    sudo apt update && sudo apt install -y git
fi

# Clone or update repository
if [ -d "legal-dashboard-service" ]; then
    echo "📁 Directory exists, updating..."
    cd legal-dashboard-service
    git pull
else
    echo "📥 Cloning repository..."
    # Replace with your actual repository URL
    # git clone https://github.com/your-username/legal-dashboard-service.git
    echo "❌ Please update this script with your actual repository URL"
    echo "   Edit the git clone command in quick-start-ec2.sh"
    exit 1
fi

# Make deployment script executable and run it
chmod +x deploy-ec2.sh
./deploy-ec2.sh

echo ""
echo "✅ Quick start completed!"
echo "🔧 Don't forget to:"
echo "   1. Update deployment/.env with your actual configuration"
echo "   2. Change MongoDB passwords for security"
echo "   3. Configure your domain name"
