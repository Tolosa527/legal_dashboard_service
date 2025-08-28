from dataclasses import dataclass
from database_manager import DatabaseManager


@dataclass
class StatDataMongoService:
    """Service for storing stat data in MongoDB"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.collection_name = "stat_data"

    def _get_collection(self):
        """Get MongoDB collection"""
        mongo_db = self.db_manager.mongo
        return mongo_db[self.collection_name]

    def store_stat_data(self, stat_data) -> str:
        """
        Store stat data in MongoDB

        Args:
            stat_data: StatData instance

        Returns:
            MongoDB document ID
        """
        collection = self._get_collection()
        doc = stat_data.to_dict()
        result = collection.replace_one({"id": doc["id"]}, doc, upsert=True)
        return str(result.upserted_id if result.upserted_id else doc["id"])

    def get_statistics(self):
        """
        Get statistics from MongoDB

        Returns:
            Dictionary with statistics
        """
        """Get optimized statistics about police data using aggregation."""
        collection = self._get_collection()

        # Basic counts
        total_count = collection.count_documents({})
        stat_count = collection.count_documents({"source_type": "stat_data"})

        status_check_in_pipeline = [
            {"$group": {"_id": "$status_check_in", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        status_check_out_pipeline = [
            {"$group": {"_id": "$status_check_out", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        status_result = list(collection.aggregate(
            status_check_in_pipeline + status_check_out_pipeline))

        status_distribution = {
            item["_id"]: item["count"] for item in status_result
        }

        type_pipeline = [
            {"$group": {"_id": "$type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]

        type_results = list(collection.aggregate(type_pipeline))
        status_type_distribution = {
            item["_id"]: item["count"] for item in type_results
        }

        return {
            "total_records": total_count,
            "stats": stat_count,
            "state_distribution": status_distribution,
            "type_distribution": status_type_distribution
        }
