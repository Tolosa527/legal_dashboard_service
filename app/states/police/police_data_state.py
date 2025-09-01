import reflex as rx
from services.police.police_data_mongo_service import PoliceDataMongoService
from app.states.success_rate_utils import calculate_police_success_rate
from database_manager import DatabaseManager
from typing import Dict, Any

from settings import settings
from dataclasses import dataclass, field
from app.states.police.config import (
    SUCCESS_STATES,
    ERROR_STATES,
    SUCCESS_RATE_THRESHOLDS,
    STATUS_LABELS,
    STATUS_COLORS,
    STATUS_ICONS,
    CACHE_TIMEOUT,
)

from logging import Logger

logger = Logger(__name__)

LIMIT_OF_DETAIL = 10


@dataclass
class PoliceTypeStatusResult:
    police_type: str
    total_records: int
    success_rate: float
    status: str
    color: str
    icon: str
    success_records: int
    states: Dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PoliceTypeStatusResult":
        return cls(
            police_type=data["police_type"],
            total_records=data["total_records"],
            success_rate=data["success_rate"],
            status=data["status"],
            color=data["color"],
            icon=data["icon"],
            success_records=data["success_records"],
            states=data.get("states", {}),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "police_type": self.police_type,
            "total_records": self.total_records,
            "success_rate": self.success_rate,
            "status": self.status,
            "color": self.color,
            "icon": self.icon,
            "success_records": self.success_records,
            "states": self.states,
        }


class PoliceDataState(rx.State):
    # Store aggregated statistics instead of all raw data
    stats_cache: Dict[str, Any] = {}
    police_type_data: Dict[str, Any] = {}
    loading: bool = True
    error_message: str = ""
    selected_police_type: str = ""
    cache_timestamp: float = 0

    # Cache timeout in seconds (from config)
    CACHE_TIMEOUT: float = CACHE_TIMEOUT

    @rx.event(background=True)
    async def fetch_dashboard_stats(self):
        """Fetch only dashboard statistics (much faster than full data)."""
        import time

        # Check if cache is still valid
        current_time = time.time()
        if (
            self.stats_cache
            and (current_time - self.cache_timestamp) < self.CACHE_TIMEOUT
        ):
            async with self:
                self.loading = False
            return

        # Use singleton database manager for connection pooling
        db_manager = DatabaseManager.get_instance()
        db_manager.connect_mongo(
            connection_string=settings.get_mongo_connection_string(),
            database=settings.get_mongo_database(),
        )
        police_data_service = PoliceDataMongoService(db_manager=db_manager)
        # Use context manager to modify state in background task
        async with self:
            try:
                # Get aggregated statistics instead of all data
                stats = police_data_service.get_statistics()
                self.stats_cache = stats
                self.cache_timestamp = current_time
                # Get police type status data
                self.police_type_data = await self._get_police_type_statistics(
                    police_data_service
                )
                self.loading = False
            except Exception as e:
                self.error_message = f"Failed to load data: {str(e)}"
                self.loading = False

    async def _get_police_type_statistics(
        self, service: PoliceDataMongoService
    ) -> Dict[str, PoliceTypeStatusResult]:
        """Get aggregated statistics by police type."""
        # Get aggregated data by police type and state
        collection = service._get_collection()
        success_states = SUCCESS_STATES
        error_states = ERROR_STATES
        # Simplified aggregation pipeline for police type statistics
        pipeline = [
            {
                "$group": {
                    "_id": "$police_type",
                    "states": {"$push": {"state": "$state", "count": 1}},
                    "total": {"$sum": 1},
                    "docs": {
                        "$push": {
                            "state": "$state",
                            "reason": "$reason"
                        }
                    },
                }
            }
        ]
        from collections import Counter
        result = list(collection.aggregate(pipeline))
        # Process the aggregated data
        police_type_stats = {}
        for item in result:
            police_type = item["_id"]
            total_records = item["total"]
            # Aggregate state counts properly
            state_counter: Counter[str] = Counter()
            for state_info in item["states"]:
                state = state_info["state"]
                count = state_info["count"]
                state_counter[state] += count
            states = dict(state_counter)
            success_count = sum(
                count for state, count in states.items()
                if state in success_states
            )
            success_rate = calculate_police_success_rate(
                success_count=success_count,
                error_states=error_states,
                docs=item.get("docs", []),
                police_type=police_type,
            )
            # Determine status
            if success_rate >= SUCCESS_RATE_THRESHOLDS.good:
                status = STATUS_LABELS.good
                color = STATUS_COLORS.good
                icon = STATUS_ICONS.good
            elif success_rate >= SUCCESS_RATE_THRESHOLDS.warning:
                status = STATUS_LABELS.warning
                color = STATUS_COLORS.warning
                icon = STATUS_ICONS.warning
            else:
                status = STATUS_LABELS.error
                color = STATUS_COLORS.error
                icon = STATUS_ICONS.error

            police_type_stats[police_type] = PoliceTypeStatusResult(
                police_type=police_type,
                total_records=total_records,
                success_rate=round(success_rate, 1),
                status=status,
                color=color,
                icon=icon,
                success_records=success_count,
                states=states,
            )

        return police_type_stats

    @rx.event(background=True)
    async def fetch_police_data(self):
        """
        Legacy method - now just calls fetch_dashboard_stats for compatibility.
        """
        yield PoliceDataState.fetch_dashboard_stats

    @rx.event
    def set_selected_police_type(self, police_type: str):
        """Set the selected police type for detailed view."""
        self.selected_police_type = police_type

    @rx.var
    def get_current_police_type_from_url(self) -> str:
        """Get police type from URL path."""
        try:
            path = self.router.url.path
            if "/police-type/" in path:
                return path.split("/police-type/")[-1]
            return "Unknown"
        except Exception:
            return "Unknown"

    @rx.var
    def get_police_data(self) -> list[dict]:
        """Return empty list - use specific statistics methods instead."""
        return []

    @rx.var
    def get_police_state_chart_data(self) -> list[dict]:
        """Get police data aggregated by state for pie chart."""
        if (
            not self.stats_cache or
            "state_distribution" not in self.stats_cache
        ):
            return []

        # Convert state distribution to chart format
        state_dist = self.stats_cache["state_distribution"]
        return [
            {"name": state, "value": count}
            for state, count in state_dist.items()
        ]

    @rx.var
    def get_police_type_chart_data(self) -> list[dict]:
        """Get police data aggregated by police type for pie chart."""
        if (
            not self.stats_cache or
            "police_type_distribution" not in self.stats_cache
        ):
            return []

        # Convert type distribution to chart format
        type_dist = self.stats_cache["police_type_distribution"]
        return [
            {"name": police_type, "value": count}
            for police_type, count in type_dist.items()
        ]

    @rx.var
    def get_total_records(self) -> int:
        """Get total number of police records."""
        return self.stats_cache.get("total_records", 0)

    @rx.var
    def get_success_rate(self) -> float:
        """Get success rate percentage with expected error filtering."""
        if not self.police_type_data:
            return 0.0

        # Calculate weighted average of success rates from individual
        # police types which already have error filtering applied
        total_records = 0
        weighted_success = 0.0

        for police_data in self.police_type_data.values():
            records = police_data.total_records
            success_rate = police_data.success_rate
            
            total_records += records
            weighted_success += (success_rate * records)

        if total_records == 0:
            return 0.0

        return round(weighted_success / total_records, 1)

    @rx.var
    def get_error_count(self) -> int:
        """Get count of error records."""
        if (
            not self.stats_cache or
            "state_distribution" not in self.stats_cache
        ):
            return 0

        return self.stats_cache["state_distribution"].get("ERROR", 0)

    @rx.var
    def get_active_types(self) -> int:
        """Get number of different police types."""
        if (
            not self.stats_cache or
            "police_type_distribution" not in self.stats_cache
        ):
            return 0

        return len(self.stats_cache["police_type_distribution"])

    @rx.var
    def get_service_status(self) -> str:
        """Get service status based on success rate thresholds."""
    # Calculate success rate inline instead of calling another @rx.var method
        if (
            not self.stats_cache or
            "state_distribution" not in self.stats_cache
        ):
            return "Error"

        state_dist = self.stats_cache["state_distribution"]
        in_progress_states = ["NEW", "IN_PROGRESS", "PROGRESS"]
        success_states = ["SUCCESS", "CONFIRMED", "COMPLETE"]

        completed_count = sum(
            count
            for state, count in state_dist.items()
            if state not in in_progress_states
        )
        success_count = sum(
            count for state, count in state_dist.items()
            if state in success_states
        )

        if completed_count == 0:
            success_rate = 0.0
        else:
            success_rate = (success_count / completed_count) * 100

        if success_rate >= SUCCESS_RATE_THRESHOLDS.good:
            return STATUS_LABELS.good
        elif success_rate >= SUCCESS_RATE_THRESHOLDS.warning:
            return STATUS_LABELS.warning
        else:
            return STATUS_LABELS.error

    @rx.var
    def get_service_status_color(self) -> str:
        """Get service status color."""
        status = self.get_service_status
        if status == STATUS_LABELS.good:
            return STATUS_COLORS.good
        elif status == STATUS_LABELS.warning:
            return STATUS_COLORS.warning
        else:
            return STATUS_COLORS.error

    @rx.var
    def get_service_status_icon(self) -> str:
        """Get service status icon."""
        status = self.get_service_status
        if status == STATUS_LABELS.good:
            return STATUS_ICONS.good
        elif status == STATUS_LABELS.warning:
            return STATUS_ICONS.warning
        else:
            return STATUS_ICONS.error

    @rx.var
    def get_police_type_status(self) -> list[dict]:
        """Get service status for each police type."""
        if not self.police_type_data:
            return []

        # Convert police type data to list format expected by UI
        result = []
        for police_type, data in self.police_type_data.items():
            # Ensure data is a PoliceTypeStatusResult instance
            if isinstance(data, dict):
                data = PoliceTypeStatusResult.from_dict(data)
            result.append(
                {
                    "type": police_type,
                    "status": getattr(data, "status", "Unknown"),
                    "color": getattr(data, "color", "grey"),
                    "icon": getattr(data, "icon", ""),
                    "success_rate": getattr(data, "success_rate", 0.0),
                    "total_records": getattr(data, "total_records", 0),
                    "success_records": getattr(data, "success_records", 0),
                }
            )

        return sorted(result, key=lambda x: x["success_rate"], reverse=True)

    @rx.var
    def get_police_type_detail_data(self) -> dict:
        """Get detailed data for the selected police type."""
        # Get police_type from URL params if selected_police_type is not set
        police_type = self.selected_police_type
        if not police_type:
            try:
                # Try to extract police_type from the URL path
                path = self.router.url.path
                if "/police-type/" in path:
                    police_type = path.split("/police-type/")[-1]
                else:
                    police_type = ""
            except Exception:
                police_type = ""
        
        if not self.police_type_data or not police_type:
            return {}

        if police_type not in self.police_type_data:
            return {
                "type": police_type,
                "total_records": 0,
                "success_records": 0,
                "success_rate": 0.0,
                "status": "Unknown",
            }

        data = self.police_type_data[police_type]
        return {
            "type": police_type,
            "total_records": data.total_records,
            "success_records": data.success_records,
            "success_rate": data.success_rate,
            "status": data.status,
        }

    @rx.var
    def get_police_type_recent_records(self) -> list[dict]:
        """Get recent records (state and reason) for selected police type."""
        # Get police_type from URL params if selected_police_type is not set
        police_type = self.selected_police_type
        if not police_type:
            try:
                # Try to extract police_type from the URL path
                path = self.router.url.path
                if "/police-type/" in path:
                    police_type = path.split("/police-type/")[-1]
                else:
                    police_type = ""
            except Exception:
                police_type = ""
        if not police_type:
            return []

        # Use the DB manager to get records for the selected police type
        try:
            # Create a new database connection
            db_manager = DatabaseManager.get_instance()
            mongo_db = db_manager.connect_mongo(
                connection_string=settings.get_mongo_connection_string(),
                database=settings.get_mongo_database(),
            )
            collection = mongo_db["police_data"]
            # Exclude documents with state "NEW"
            records = list(collection.find(
                {
                    "police_type": police_type,
                    "state": {"$nin": ["NEW", "SCHEDULED", "CANCELED"]}
                },
                {"state": 1, "reason": 1, "created_at": 1, "_id": 0}
            ).sort("created_at", -1).limit(LIMIT_OF_DETAIL))
            return records
        except Exception as e:
            logger.error(f"Error fetching recent records: {str(e)}")
            return []
