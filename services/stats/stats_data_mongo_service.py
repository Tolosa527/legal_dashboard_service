from dataclasses import dataclass
from collections import defaultdict
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

        status_check_in_pipeline = [
            {"$group": {"_id": "$status_check_in", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        status_check_out_pipeline = [
            {"$group": {"_id": "$status_check_out", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        status_result_check_out = list(collection.aggregate(status_check_out_pipeline))
        status_result_check_in = list(collection.aggregate(status_check_in_pipeline))

        result = defaultdict(int)
        # Sum counts grouped by _id
        for d in status_result_check_out + status_result_check_in:
            result[d["_id"]] += d["count"]

        # Return a mapping of state -> count (not a list) so callers can
        # use .items()
        status_distribution = dict(result)

        type_pipeline = [
            {"$group": {"_id": "$stat_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]

        type_results = list(collection.aggregate(type_pipeline))
        statistics_type_distribution = {
            item["_id"]: item["count"] for item in type_results
        }

        # Provide both the new key and the legacy key to avoid breaking
        # other modules
        return {
            "total_records": total_count,
            "state_distribution": status_distribution,
            "statistics_type_distribution": statistics_type_distribution,
            "stat_type_distribution": statistics_type_distribution,
        }
