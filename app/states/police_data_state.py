import os
import reflex as rx
from services.police_data_mongo_service import PoliceDataMongoService
from database_manager import DatabaseManager
from typing import Dict, Any
from app.states.success_rate_calculator import calculate_success_rate
from settings import settings


class PoliceDataState(rx.State):
    """State to manage police data."""
    # Store aggregated statistics instead of all raw data
    stats_cache: Dict[str, Any] = {}
    police_type_data: Dict[str, Any] = {}
    loading: bool = True
    error_message: str = ""
    selected_police_type: str = ""
    cache_timestamp: float = 0
    
    # Cache timeout in seconds (5 minutes)
    CACHE_TIMEOUT: float = 300

    @rx.event(background=True)
    async def fetch_dashboard_stats(self):
        """Fetch only dashboard statistics (much faster than full data)."""
        import time

        # Check if cache is still valid
        current_time = time.time()
        if self.stats_cache and (current_time - self.cache_timestamp) < self.CACHE_TIMEOUT:
            async with self:
                self.loading = False
            return
        
        # Use singleton database manager for connection pooling
        db_manager = DatabaseManager.get_instance()
        db_manager.connect_mongo(
            connection_string=settings.get_mongo_connection_string(),
            database=settings.get_mongo_database()
        )
        
        # Create service locally
        police_data_service = PoliceDataMongoService(db_manager=db_manager)
        
        # Use context manager to modify state in background task
        async with self:
            try:
                # Get aggregated statistics instead of all data
                stats = police_data_service.get_statistics()
                self.stats_cache = stats
                self.cache_timestamp = current_time
                
                # Get police type status data
                self.police_type_data = await self._get_police_type_statistics(police_data_service)
                
                self.loading = False
            except Exception as e:
                self.error_message = f"Failed to load data: {str(e)}"
                self.loading = False
    
    async def _get_police_type_statistics(self, service: PoliceDataMongoService) -> Dict[str, Any]:
        """Get aggregated statistics by police type."""
        # Get aggregated data by police type and state
        collection = service._get_collection()
        in_progress_states = ["NEW", "IN_PROGRESS", "PROGRESS"]
        success_states = ["SUCCESS", "CONFIRMED", "COMPLETE"]
        error_states = ["ERROR", "FAILED", "INVALID"]
        # Simplified aggregation pipeline for police type statistics
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "police_type": "$police_type",
                        "state": "$state"
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$group": {
                    "_id": "$_id.police_type",
                    "states": {
                        "$push": {
                            "state": "$_id.state",
                            "count": "$count"
                        }
                    },
                    "total": {"$sum": "$count"}
                }
            }
        ]
        result = list(collection.aggregate(pipeline))
        # Process the aggregated data
        police_type_stats = {}
        for item in result:
            police_type = item["_id"]
            total_records = item["total"]
            states = {state_info["state"]: state_info["count"] for state_info in item["states"]}
            success_count = sum(count for state, count in states.items() if state in success_states)
            success_rate = calculate_success_rate(
                states=states,
                reason="",  # Pass empty reason since we're not grouping by reason at this level
                in_progress_states=in_progress_states,
                success_states=success_states,
                error_states=error_states
            )
            # Determine status
            if success_rate >= 90:
                status = "Good"
                color = "green"
                icon = "check"
            elif success_rate >= 70:
                status = "Warning"
                color = "orange"
                icon = "triangle-alert"
            else:
                status = "Error"
                color = "red"
                icon = "circle-x"

            police_type_stats[police_type] = {
                "total_records": total_records,
                "success_rate": round(success_rate, 1),
                "status": status,
                "color": color,
                "icon": icon,
                "success_records": success_count,
                "states": states
            }

        return police_type_stats

    @rx.event(background=True)
    async def fetch_police_data(self):
        """Legacy method - now just calls fetch_dashboard_stats for compatibility."""
        return PoliceDataState.fetch_dashboard_stats

    @rx.event
    def set_selected_police_type(self, police_type: str):
        """Set the selected police type for detailed view."""
        self.selected_police_type = police_type

    @rx.var
    def get_police_data(self) -> list[dict]:
        """Return empty list - use specific statistics methods instead."""
        return []
    
    @rx.var
    def get_police_state_chart_data(self) -> list[dict]:
        """Get police data aggregated by state for pie chart."""
        if not self.stats_cache or "state_distribution" not in self.stats_cache:
            return []
        
        # Convert state distribution to chart format
        state_dist = self.stats_cache["state_distribution"]
        return [{"name": state, "value": count} for state, count in state_dist.items()]
    
    @rx.var
    def get_police_type_chart_data(self) -> list[dict]:
        """Get police data aggregated by police type for pie chart."""
        if not self.stats_cache or "police_type_distribution" not in self.stats_cache:
            return []
        
        # Convert type distribution to chart format
        type_dist = self.stats_cache["police_type_distribution"]
        return [{"name": police_type, "value": count} for police_type, count in type_dist.items()]
    
    @rx.var
    def get_total_records(self) -> int:
        """Get total number of police records."""
        return self.stats_cache.get("total_records", 0)
    
    @rx.var
    def get_success_rate(self) -> float:
        """Get success rate percentage."""
        if not self.stats_cache or "state_distribution" not in self.stats_cache:
            return 0.0
        
        state_dist = self.stats_cache["state_distribution"]
        
        # Define states that should be excluded from success rate calculation
        in_progress_states = ["NEW", "IN_PROGRESS", "PROGRESS"]
        success_states = ["SUCCESS", "CONFIRMED", "COMPLETE"]
        
        # Calculate totals
        completed_count = sum(count for state, count in state_dist.items() if state not in in_progress_states)
        success_count = sum(count for state, count in state_dist.items() if state in success_states)
        
        if completed_count == 0:
            return 0.0
        
        return round((success_count / completed_count) * 100, 1)
    
    @rx.var
    def get_error_count(self) -> int:
        """Get count of error records."""
        if not self.stats_cache or "state_distribution" not in self.stats_cache:
            return 0
        
        return self.stats_cache["state_distribution"].get("ERROR", 0)
    
    @rx.var
    def get_active_types(self) -> int:
        """Get number of different police types."""
        if not self.stats_cache or "police_type_distribution" not in self.stats_cache:
            return 0
        
        return len(self.stats_cache["police_type_distribution"])
    
    @rx.var
    def get_service_status(self) -> str:
        """Get service status based on success rate thresholds."""
        # Calculate success rate inline instead of calling another @rx.var method
        if not self.stats_cache or "state_distribution" not in self.stats_cache:
            return "Error"
        
        state_dist = self.stats_cache["state_distribution"]
        in_progress_states = ["NEW", "IN_PROGRESS", "PROGRESS"]
        success_states = ["SUCCESS", "CONFIRMED", "COMPLETE"]
        
        completed_count = sum(count for state, count in state_dist.items() if state not in in_progress_states)
        success_count = sum(count for state, count in state_dist.items() if state in success_states)
        
        if completed_count == 0:
            success_rate = 0.0
        else:
            success_rate = (success_count / completed_count) * 100
        
        if success_rate >= 90:
            return "Good"
        elif success_rate >= 70:
            return "Warning"
        else:
            return "Error"
    
    @rx.var
    def get_service_status_color(self) -> str:
        """Get service status color."""
        status = self.get_service_status
        if status == "Good":
            return "green"
        elif status == "Warning":
            return "orange"
        else:
            return "red"
    
    @rx.var
    def get_service_status_icon(self) -> str:
        """Get service status icon."""
        status = self.get_service_status
        if status == "Good":
            return "check"
        elif status == "Warning":
            return "triangle-alert"
        else:
            return "circle-x"
    
    @rx.var
    def get_police_type_status(self) -> list[dict]:
        """Get service status for each police type."""
        if not self.police_type_data:
            return []
        
        # Convert police type data to list format expected by UI
        result = []
        for police_type, data in self.police_type_data.items():
            result.append({
                "type": police_type,
                "status": data["status"],
                "color": data["color"],
                "icon": data["icon"],
                "success_rate": data["success_rate"],
                "total_records": data["total_records"],
                "success_records": data["success_records"]
            })
        
        return sorted(result, key=lambda x: x["success_rate"], reverse=True)
    
    @rx.var
    def get_police_type_detail_data(self) -> dict:
        """Get detailed data for the selected police type."""
        if not self.police_type_data or not self.selected_police_type:
            return {}
        
        if self.selected_police_type not in self.police_type_data:
            return {
                "type": self.selected_police_type,
                "total_records": 0,
                "success_records": 0,
                "success_rate": 0.0,
                "status": "Unknown"
            }
        
        data = self.police_type_data[self.selected_police_type]
        return {
            "type": self.selected_police_type,
            "total_records": data["total_records"],
            "success_records": data["success_records"],
            "success_rate": data["success_rate"],
            "status": data["status"]
        }
    
    @rx.var
    def get_police_type_recent_records(self) -> list[dict]:
        """Get recent records for the selected police type - now returns empty for performance."""
        # For performance, we no longer load individual records
        # This could be implemented as a separate on-demand fetch if needed
        return []