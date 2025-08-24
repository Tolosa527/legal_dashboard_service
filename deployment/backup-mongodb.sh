#!/bin/bash

# Legal Dashboard Service - MongoDB Atlas Backup Script
# Run this script to create backups of your MongoDB Atlas data

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Configuration
BACKUP_DIR="/opt/legal_dashboard/backups"
RETENTION_DAYS=30

# Load environment variables
if [ -f "/opt/legal_dashboard/.env.prod" ]; then
    export $(cat /opt/legal_dashboard/.env.prod | grep -v '^#' | xargs)
else
    echo -e "${RED}Error: /opt/legal_dashboard/.env.prod file not found.${NC}"
    exit 1
fi

# Check if required tools are installed
if ! command -v mongodump &> /dev/null; then
    echo -e "${YELLOW}Installing MongoDB tools...${NC}"
    # Install MongoDB tools for Ubuntu/Debian
    wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add -
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list
    apt-get update
    apt-get install -y mongodb-database-tools
fi

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Generate backup filename with timestamp
BACKUP_NAME="mongodb_atlas_backup_$(date +%Y%m%d_%H%M%S)"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

echo -e "${YELLOW}Starting MongoDB Atlas backup...${NC}"

# Validate MongoDB URI
if [ -z "$MONGO_URI" ] || [ -z "$MONGO_DB" ]; then
    echo -e "${RED}Error: MONGO_URI and MONGO_DB must be set in .env.prod${NC}"
    exit 1
fi

# Create backup using mongodump
echo -e "${YELLOW}Creating backup: $BACKUP_NAME${NC}"
mongodump \
    --uri="$MONGO_URI" \
    --db="$MONGO_DB" \
    --out="$BACKUP_PATH"

# Compress backup
echo -e "${YELLOW}Compressing backup...${NC}"
cd $BACKUP_DIR
tar -czf "$BACKUP_NAME.tar.gz" $BACKUP_NAME
rm -rf $BACKUP_NAME

# Set proper permissions
chmod 600 "$BACKUP_NAME.tar.gz"

# Calculate backup size
BACKUP_SIZE=$(du -h "$BACKUP_NAME.tar.gz" | cut -f1)

echo -e "${GREEN}Backup completed successfully!${NC}"
echo -e "Backup file: $BACKUP_PATH.tar.gz"
echo -e "Backup size: $BACKUP_SIZE"

# Clean up old backups (keep only last N days)
echo -e "${YELLOW}Cleaning up old backups (keeping last $RETENTION_DAYS days)...${NC}"
find $BACKUP_DIR -name "mongodb_atlas_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete

# List recent backups
echo -e "${YELLOW}Recent backups:${NC}"
ls -lah $BACKUP_DIR/mongodb_atlas_backup_*.tar.gz 2>/dev/null | tail -10 || echo "No backups found"

echo -e "${GREEN}Backup process completed!${NC}"
