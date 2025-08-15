// MongoDB initialization script
// This script creates the legal_dashboard database and police_data collection

print('🚀 Initializing Legal Dashboard MongoDB...');

// Switch to legal_dashboard database
db = db.getSiblingDB('legal_dashboard');

// Create police_data collection with indexes
db.createCollection('police_data');

// Create useful indexes for better query performance
db.police_data.createIndex({ "id": 1 }, { unique: true });
db.police_data.createIndex({ "created_at": -1 });
db.police_data.createIndex({ "state": 1 });
db.police_data.createIndex({ "police_type": 1 });
db.police_data.createIndex({ "source_type": 1 });
db.police_data.createIndex({ "reservation_id": 1 });
db.police_data.createIndex({ "action": 1 });

// Create compound indexes for common queries
db.police_data.createIndex({ "state": 1, "police_type": 1 });
db.police_data.createIndex({ "source_type": 1, "created_at": -1 });

print('✅ Legal Dashboard MongoDB initialization completed!');
print('📊 Created police_data collection with indexes');
print('🔍 Available indexes:');
db.police_data.getIndexes().forEach(function(index) {
    print('   - ' + JSON.stringify(index.key));
});
