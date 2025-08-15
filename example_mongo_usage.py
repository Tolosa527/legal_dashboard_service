"""
Example usage of the PoliceDataMongoService

This script demonstrates how to:
1. Connect to both PostgreSQL and MongoDB
2. Retrieve data from PostgreSQL services
3. Store unified data in MongoDB
4. Query the unified data
"""

from database_manager import DatabaseManager
from services import PoliceMovementService, PoliceRegistrationService, PoliceDataMongoService
from services.police_data_mongo_service import UnifiedPoliceState, UnifiedPoliceType


def main():
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Connect to databases
    try:
        # Connect to PostgreSQL
        postgres_conn = db_manager.connect_postgres(
            host="localhost",
            port=5432,
            database="legal_dashboard",
            user="postgres",
            password="your_password"
        )
        print("Connected to PostgreSQL")
        
        # Connect to MongoDB
        mongo_db = db_manager.connect_mongo(
            host="localhost",
            port=27017,
            database="legal_dashboard"
        )
        print("Connected to MongoDB")
        
        # Initialize services
        movement_service = PoliceMovementService(db_manager)
        registration_service = PoliceRegistrationService(db_manager)
        mongo_service = PoliceDataMongoService(db_manager)
        
        # Example 1: Store police movements in MongoDB
        print("\n--- Storing Police Movements ---")
        movements = movement_service.get_all_movements(limit=5)
        for movement in movements:
            try:
                mongo_id = mongo_service.store_police_movement(movement)
                print(f"Stored movement {movement.id} with MongoDB ID: {mongo_id}")
            except Exception as e:
                print(f"Error storing movement {movement.id}: {e}")
        
        # Example 2: Store police registrations in MongoDB
        print("\n--- Storing Police Registrations ---")
        registrations = registration_service.get_all_registrations(limit=5)
        for registration in registrations:
            try:
                mongo_id = mongo_service.store_police_registration(registration)
                print(f"Stored registration {registration.id} with MongoDB ID: {mongo_id}")
            except Exception as e:
                print(f"Error storing registration {registration.id}: {e}")
        
        # Example 3: Query unified data from MongoDB
        print("\n--- Querying Unified Data ---")
        
        # Get all data
        all_data = mongo_service.get_all_police_data(limit=10)
        print(f"Total unified records: {len(all_data)}")
        
        # Get data by state
        success_data = mongo_service.get_police_data_by_state(UnifiedPoliceState.SUCCESS)
        print(f"SUCCESS state records: {len(success_data)}")
        
        # Get data by police type
        pol_data = mongo_service.get_police_data_by_police_type(UnifiedPoliceType.POL)
        print(f"POL type records: {len(pol_data)}")
        
        # Get data by source
        movements_data = mongo_service.get_police_data_by_source("movement")
        registrations_data = mongo_service.get_police_data_by_source("registration")
        print(f"Movement records: {len(movements_data)}")
        print(f"Registration records: {len(registrations_data)}")
        
        # Example 4: Get statistics
        print("\n--- Statistics ---")
        stats = mongo_service.get_statistics()
        print(f"Total records: {stats['total_records']}")
        print(f"Movements: {stats['movements']}")
        print(f"Registrations: {stats['registrations']}")
        print("State distribution:", stats['state_distribution'])
        print("Police type distribution:", stats['police_type_distribution'])
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Close connections
        db_manager.close_all()
        print("\nClosed all database connections")


if __name__ == "__main__":
    main()
