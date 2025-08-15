# Legal Dashboard Docker Setup

This Docker Compose setup provides a complete environment for the Legal Dashboard with MongoDB, PostgreSQL, and data synchronization.

## Services

- **MongoDB**: Document database for unified police data storage
- **Mongo Express**: Web-based MongoDB admin interface  
- **Data Sync**: Service that connects to external PostgreSQL and synchronizes data to MongoDB

## Quick Start

```bash
# Start all services and sync data
./docker-manage.sh start

# View service status
./docker-manage.sh status

# View logs
./docker-manage.sh logs

# Stop services
./docker-manage.sh stop
```

## Access URLs

- **Mongo Express**: http://localhost:8081
  - Username: `admin`
  - Password: `express123`

- **MongoDB**: mongodb://localhost:27017
  - Username: `admin`
  - Password: `adminpassword`
  - Database: `legal_dashboard`

**Note**: The sync service connects to your external PostgreSQL database to fetch data.

## Data Synchronization

The data sync service automatically:
1. Connects to your external PostgreSQL database
2. Connects to the MongoDB container
3. Retrieves police movements and registrations from the last 24 hours
4. Stores unified data in MongoDB `police_data` collection
5. Creates useful indexes for performance

**PostgreSQL Configuration**: Update the environment variables in `docker-compose.yml` to match your external PostgreSQL settings.

## Management Commands

```bash
./docker-manage.sh start      # Start all services
./docker-manage.sh stop       # Stop all services
./docker-manage.sh restart    # Restart all services
./docker-manage.sh sync       # Re-sync data only
./docker-manage.sh logs       # View all logs
./docker-manage.sh status     # Show service status
./docker-manage.sh clean      # Remove containers and volumes
./docker-manage.sh shell-mongo    # Open MongoDB shell
```

## MongoDB Collection Structure

The `police_data` collection contains unified documents with:

```javascript
{
  "id": "uuid",
  "created_at": "2025-08-16T10:30:00Z",
  "updated_at": "2025-08-16T10:30:00Z",
  "action": "CHECK_IN",
  "state": "SUCCESS",
  "movement_type": "NEW_BOOKING",
  "police_type": "POL",
  "data": "...",
  "reason": "...",
  "source_type": "movement",
  "reservation_id": "uuid",
  // ... other fields
}
```

## Environment Variables

The data sync service can be configured with:

- `SYNC_HOURS`: Hours of historical data to sync (default: 24)
- `POSTGRES_HOST`: PostgreSQL hostname (default: host.docker.internal)
- `MONGO_HOST`: MongoDB hostname (default: mongodb)

## Troubleshooting

### Services not starting
```bash
# Check service status
./docker-manage.sh status

# View logs for specific service
./docker-manage.sh logs mongodb
./docker-manage.sh logs data-sync
```

### Data sync issues
```bash
# Re-run data sync
./docker-manage.sh sync

# Check sync logs
./docker-manage.sh logs data-sync
```

### Database connection issues
```bash
# Test MongoDB connection
./docker-manage.sh shell-mongo
```
