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
from services import PoliceMovementService, PoliceRegistrationService, PoliceDataMongoService


def wait_for_databases(max_retries=30, retry_delay=2):
    """Wait for databases to be ready"""
    print("Waiting for databases to be ready...")
    
    for attempt in range(max_retries):
        try:
            db_manager = DatabaseManager()
            
            # Test PostgreSQL connection
            postgres_conn = db_manager.connect_postgres(
                host=os.getenv('POSTGRES_HOST', 'localhost'),
                port=int(os.getenv('POSTGRES_PORT', '5432')),
                database=os.getenv('POSTGRES_DB', 'legal_dashboard'),
                user=os.getenv('POSTGRES_USER', 'postgres'),
                password=os.getenv('POSTGRES_PASSWORD', 'postgres123')
            )
            
            # Test MongoDB connection
            mongo_db = db_manager.connect_mongo(
                host=os.getenv('MONGO_HOST', 'localhost'),
                port=int(os.getenv('MONGO_PORT', '27017')),
                database=os.getenv('MONGO_DB', 'legal_dashboard'),
                username=os.getenv('MONGO_USERNAME', 'admin'),
                password=os.getenv('MONGO_PASSWORD', 'adminpassword')
            )
            
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
        sync_hours = int(os.getenv('SYNC_HOURS', '24'))
        cutoff_time = datetime.now() - timedelta(hours=sync_hours)
        
        print(f"🔄 Starting data sync for last {sync_hours} hours...")
        print(f"📅 Cutoff time: {cutoff_time}")
        
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Connect to databases
        postgres_conn = db_manager.connect_postgres(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=int(os.getenv('POSTGRES_PORT', '5432')),
            database=os.getenv('POSTGRES_DB', 'legal_dashboard'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', 'postgres123')
        )
        
        mongo_db = db_manager.connect_mongo(
            host=os.getenv('MONGO_HOST', 'localhost'),
            port=int(os.getenv('MONGO_PORT', '27017')),
            database=os.getenv('MONGO_DB', 'legal_dashboard'),
            username=os.getenv('MONGO_USERNAME', 'admin'),
            password=os.getenv('MONGO_PASSWORD', 'adminpassword')
        )
        
        # Initialize services
        movement_service = PoliceMovementService(db_manager)
        registration_service = PoliceRegistrationService(db_manager)
        mongo_service = PoliceDataMongoService(db_manager)
        
        # Clear existing data in MongoDB
        collection = mongo_service._get_collection()
        result = collection.delete_many({})
        print(f"🗑️  Cleared {result.deleted_count} existing records from MongoDB")
        
        # Sync police movements
        print("📊 Syncing police movements...")
        movements = movement_service.get_movements_by_date_range(
            cutoff_time.date(), 
            datetime.now().date()
        )
        
        movement_count = 0
        movement_errors = 0
        
        for movement in movements:
            try:
                print(f"🔄 Processing movement {movement.id}...")
                mongo_service.store_police_movement(movement)
                movement_count += 1
            except Exception as e:
                print(f"❌ Error storing movement {movement.id}: {e}")
                print(f"🔍 Movement details - ID: {type(movement.id)}, reservation_id: {type(movement.reservation_id) if movement.reservation_id else None}")
                movement_errors += 1
                # Stop after first error for debugging
                raise e
        
        print(f"✅ Synced {movement_count} police movements ({movement_errors} errors)")
        
        # Sync police registrations
        print("📋 Syncing police registrations...")
        registrations = registration_service.get_registrations_by_date_range(
            cutoff_time.date(),
            datetime.now().date()
        )
        
        registration_count = 0
        registration_errors = 0
        
        for registration in registrations:
            try:
                mongo_service.store_police_registration(registration)
                registration_count += 1
            except Exception as e:
                print(f"❌ Error storing registration {registration.id}: {e}")
                registration_errors += 1
        
        print(f"✅ Synced {registration_count} police registrations ({registration_errors} errors)")
        
        # Display statistics
        print("\n📈 Sync Summary:")
        stats = mongo_service.get_statistics()
        print(f"   Total records: {stats['total_records']}")
        print(f"   Movements: {stats['movements']}")
        print(f"   Registrations: {stats['registrations']}")
        print(f"   State distribution: {stats['state_distribution']}")
        print(f"   Police type distribution: {stats['police_type_distribution']}")
        
        print(f"\n🎉 Data sync completed successfully!")
        print(f"🌐 MongoDB accessible at: mongodb://admin:adminpassword@localhost:27017")
        print(f"🖥️  Mongo Express UI: http://localhost:8081 (admin/express123)")
        
    except Exception as e:
        print(f"💥 Error during sync: {e}")
        sys.exit(1)
    
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
    
    # Sync data
    sync_police_data()


if __name__ == "__main__":
    main()
