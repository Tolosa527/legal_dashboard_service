#!/usr/bin/env python3
"""
Data synchronization script for Docker container

This script synchronizes police data from PostgreSQL to MongoDB
for the last 24 hours (or configurable timeframe).
"""

import os
import sys
import time
from datetime import datetime, timedelta
from database_manager import DatabaseManager
from services import (
    PoliceMovementService,
    PoliceRegistrationService,
    PoliceDataMongoService,
    StatDataMongoService,
    StatRegistrationService,
)
from settings import settings

SYNC_HOURS = int(os.getenv("SYNC_HOURS", "24"))
CUTOFF_TIME = datetime.now() - timedelta(hours=SYNC_HOURS)


def get_database() -> DatabaseManager:
    # Initialize database manager
    print("🔌 Connecting to databases...")
    try:
        db_manager = DatabaseManager()

        # Connect to databases
        postgres_conn = db_manager.connect_postgres(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
        )

        mongo_db = db_manager.connect_mongo(
            connection_string=settings.get_mongo_connection_string(),
            database=settings.get_mongo_database(),
        )
    except Exception as e:
        print(f"❌ Error connecting to databases: {e}")
        raise

    print("✅ Connected to both PostgreSQL and MongoDB")
    return db_manager


def wait_for_databases(max_retries=30, retry_delay=2):
    """Wait for databases to be ready"""
    print("Waiting for databases to be ready...")

    for attempt in range(max_retries):
        try:
            db_manager = get_database()

            print("✅ Both databases are ready!")
            db_manager.close_all()
            return True

        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries}: Databases not ready yet - {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                print("❌ Failed to connect to databases after all retries")
                return False

    return False


def sync_police_data():
    """Synchronize police data from PostgreSQL to MongoDB"""
    try:
        # Get sync timeframe from environment
        print(f"🔄 Starting data sync for last {SYNC_HOURS} hours...")
        print(f"📅 Cutoff time: {CUTOFF_TIME}")
        db_manager = get_database()
        # Initialize services
        movement_service = PoliceMovementService(db_manager)
        registration_service = PoliceRegistrationService(db_manager)
        mongo_service = PoliceDataMongoService(db_manager)
        # Clear existing data in MongoDB (optional for incremental syncs)
        clear_existing = os.getenv("CLEAR_EXISTING", "true").lower() == "true"
        if clear_existing:
            collection = mongo_service._get_collection()
            result = collection.delete_many({})
            print(f"🗑️  Cleared {result.deleted_count} existing records from MongoDB")
        else:
            print("📝 Performing incremental sync (not clearing existing data)")
        # Sync police movements
        print("📊 Syncing police movements...")
        movements = movement_service.get_movements_by_date_range(
            CUTOFF_TIME.date(), datetime.now().date()
        )
        movement_count = 0
        movement_errors = 0
        for movement in movements:
            try:
                mongo_service.store_police_movement(movement)
                movement_count += 1
                if movement_count % 1000 == 0:
                    print(f"🔄 Processed {movement_count} movements...")
            except Exception as e:
                print(f"❌ Error storing movement {movement.id}: {e}")
                movement_errors += 1
                # Continue processing other records instead of stopping
        print(f"✅ Synced {movement_count} police movements ({movement_errors} errors)")
        # Sync police registrations
        print("📋 Syncing police registrations...")
        registrations = registration_service.get_registrations_by_date_range(
            CUTOFF_TIME, datetime.now()
        )

        registration_count = 0
        registration_errors = 0

        for registration in registrations:
            try:
                mongo_service.store_police_registration(registration)
                registration_count += 1
                if registration_count % 1000 == 0:
                    print(f"🔄 Processed {registration_count} registrations...")
            except Exception as e:
                print(f"❌ Error storing registration {registration.id}: {e}")
                registration_errors += 1
                # Continue processing other records
        print(
            f"✅ Synced {registration_count} police registrations ({registration_errors} errors)"
        )
        # Display statistics
        print("\n📈 Sync Summary:")
        stats = mongo_service.get_statistics()
        print(f"   Total records: {stats['total_records']}")
        print(f"   Movements: {stats['movements']}")
        print(f"   Registrations: {stats['registrations']}")
        print(f"   State distribution: {stats['state_distribution']}")
        print(f"   Police type distribution: {stats['police_type_distribution']}")
    except Exception as e:
        print(f"💥 Error during sync: {e}")
        sys.exit(1)
    finally:
        try:
            db_manager.close_all()
            print("🔌 Database connections closed")
        except:
            pass


def sync_stat_data():
    """
    Sync statistical data between PostgreSQL and MongoDB.
    """
    try:
        db_manager = get_database()

        stat_mongo_service = StatDataMongoService(db_manager)
        stat_registration_service = StatRegistrationService(db_manager)

        # Clear existing data in MongoDB (optional for incremental syncs)
        clear_existing = os.getenv("CLEAR_EXISTING", "true").lower() == "true"
        if clear_existing:
            collection = stat_mongo_service._get_collection()
            result = collection.delete_many({})
            print(f"🗑️  Cleared {result.deleted_count} existing records from MongoDB")
        else:
            print("📝 Performing incremental sync (not clearing existing data)")
        # sync statistics
        print("📊 Syncing statistics...")
        stats = stat_registration_service.get_registrations_by_date_range(
            start_date=CUTOFF_TIME.date(), end_date=datetime.now().date()
        )

        stat_count = 0
        stat_errors = 0

        for stat in stats:
            try:
                stat_mongo_service.store_stat_data(stat)
                stat_count += 1
                if stat_count % 1000 == 0:
                    print(f"🔄 Processed {stat_count} statistics...")
            except Exception as e:
                print(f"❌ Error storing statistics {stat.id}: {e}")
                stat_errors += 1

        print(f"✅ Synced {stat_count} statistics ({stat_errors} errors)")
        # Display statistics
        print("\n📈 Sync Summary:")
        stats = stat_mongo_service.get_statistics()
        print(f"Total records: {stats['total_records']}")
        print(f"State distribution: {stats['state_distribution']}")
        print(f"Type distribution: {stats['stat_type_distribution']}")

    except Exception as e:
        print(f"💥 Error during stat data sync: {e}")
    finally:
        try:
            db_manager.close_all()
            print("🔌 Database connections closed")
        except:
            pass


def main():
    """Main function"""
    print("🚀 Legal Dashboard Data Sync Starting...")

    # Wait for databases to be ready
    if not wait_for_databases():
        print("💥 Failed to connect to databases. Exiting.")
        sys.exit(1)

    # Additional delay to ensure databases are fully ready
    print("⏳ Waiting additional 5 seconds for database initialization...")
    time.sleep(5)

    # Sync police data
    sync_police_data()

    # Sync stat data
    sync_stat_data()

    print("\n🎉 Data sync completed successfully!")
    print("🌐 MongoDB accessible at: mongodb://admin:adminpassword@localhost:27017")
    print("🖥️  Mongo Express UI: http://localhost:8081 (admin/express123)")


if __name__ == "__main__":
    main()
