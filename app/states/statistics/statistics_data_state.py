# Fixed remaining long lines in `StatisticsDataState`
import reflex as rx
from services.stats.stats_data_mongo_service import StatDataMongoService
from database_manager import DatabaseManager
from typing import Dict, Any
from app.states.success_rate_utils import calculate_stat_success_rate
from settings import settings
from dataclasses import dataclass, field
from app.states.police.config import (
    IN_PROGRESS_STATES,
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


@dataclass
class StatisticsTypeStatusResult:

    stat_type: str
    total_records: int
    success_rate: float
    status: str
    color: str
    icon: str
    success_records: int
    states: Dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StatisticsTypeStatusResult":
        return cls(
            stat_type=data["stat_type"],
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
            "stat_type": self.stat_type,
            "total_records": self.total_records,
            "success_rate": self.success_rate,
            "status": self.status,
            "color": self.color,
            "icon": self.icon,
            "success_records": self.success_records,
            "states": self.states,
        }


class StatisticsDataState(rx.State):
    # Store aggregated statistics instead of all raw data
    stats_cache: Dict[str, Any] = {}
    statistics_type_data: Dict[str, Any] = {}
    loading: bool = True
    error_message: str = ""
    selected_statistics_type: str = ""
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
        stats_data_service = StatDataMongoService(db_manager=db_manager)
        # Use context manager to modify state in background task
        async with self:
            try:
                # Get aggregated statistics instead of all data
                stats = stats_data_service.get_statistics()
                self.stats_cache = stats
                self.cache_timestamp = current_time
                # Get statistics type status data
                self.statistics_type_data = await self._get_statistics_type_statistics(
                    stats_data_service
                )
                self.loading = False
            except Exception as e:
                self.error_message = f"Failed to load data: {str(e)}"
                self.loading = False

    async def _get_statistics_type_statistics(
        self, service: StatDataMongoService
    ) -> Dict[str, StatisticsTypeStatusResult]:
        """Get aggregated statistics by statistics type."""
        collection = service._get_collection()
        success_states = SUCCESS_STATES
        error_states = ERROR_STATES
        pipeline = [
            {
                "$project": {
                    "stat_type": 1,
                    "registrations": {
                        "$concatArrays": [
                            [{"state": "$status_check_in"}],
                            [{"state": "$status_check_out"}],
                        ]
                    },
                }
            },
            {"$unwind": "$registrations"},
            {
                "$group": {
                    "_id": {
                        "stat_type": "$stat_type",
                        "state": "$registrations.state",
                    },
                    "count": {"$sum": 1},
                }
            },
            {
                "$group": {
                    "_id": "$_id.stat_type",
                    "total": {"$sum": "$count"},
                    "states": {
                        "$push": {"state": "$_id.state", "count": "$count"}
                    },
                }
            },
            {"$sort": {"total": -1}},
        ]

        from collections import Counter
        result = list(collection.aggregate(pipeline))
        # Process the aggregated data into expected structures
        police_type_stats = {}
        for item in result:
            stat_type = item["_id"]
            total_records = item.get("total", 0)
            # item["states"] is already an array of {state, count}
            state_counter = Counter(
                {s["state"]: s["count"] for s in item.get("states", [])}
            )
            states = dict(state_counter)
            success_count = sum(
                count for state, count in states.items()
                if state in success_states
            )
            try:
                sample_docs = list(
                    collection.find(
                        {"stat_type": stat_type},
                        {
                            "status_check_in": 1,
                            "status_check_out": 1,
                            "status_check_in_details": 1,
                            "status_check_out_details": 1,
                        },
                    )
                )
            except Exception:
                # If fetching sample documents fails for any reason, fall
                # back to an empty list so we don't crash the dashboard.
                sample_docs = []

            success_rate = calculate_stat_success_rate(
                success_count=success_count,
                error_states=error_states,
                docs=sample_docs,
                stat_type=stat_type,
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

            police_type_stats[stat_type] = StatisticsTypeStatusResult(
                stat_type=stat_type,
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
    async def fetch_statistics_data(self):
        """
        Legacy method - now just calls fetch_dashboard_stats for compatibility.
        """
        yield StatisticsDataState.fetch_dashboard_stats

    @rx.event
    def set_selected_statistics_type(self, statistics_type: str):
        """Set the selected statistics type for detailed view."""
        self.selected_statistics_type = statistics_type

    @rx.var
    def get_statistics_data(self) -> list[dict]:
        """Return empty list - use specific statistics methods instead."""
        return []

    @rx.var
    def get_statistics_state_chart_data(self) -> list[dict]:
        """Get statistics data aggregated by state for pie chart."""
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
    def get_statistics_type_chart_data(self) -> list[dict]:
        """Get statistics data aggregated by statistics type for pie chart."""
        if (
            not self.stats_cache or
            "statistics_type_distribution" not in self.stats_cache
        ):
            return []

        # Convert type distribution to chart format
        type_dist = self.stats_cache["statistics_type_distribution"]
        return [
            {"name": statistics_type, "value": count}
            for statistics_type, count in type_dist.items()
        ]

    @rx.var
    def get_total_records(self) -> int:
        """Get total number of statistics records."""
        return self.stats_cache.get("total_records", 0)

    @rx.var
    def get_success_rate(self) -> float:
        """Get success rate percentage."""
        if (
            not self.stats_cache or
            "state_distribution" not in self.stats_cache
        ):
            return 0.0

        state_dist = self.stats_cache["state_distribution"]

        # Define states that should be excluded from success rate calculation
        in_progress_states = IN_PROGRESS_STATES
        success_states = SUCCESS_STATES

        # Calculate totals
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
            return 0.0

        return round((success_count / completed_count) * 100, 1)

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
        """Get number of different statistics types."""
        if (
            not self.stats_cache or
            "statistics_type_distribution" not in self.stats_cache
        ):
            return 0

        return len(self.stats_cache["statistics_type_distribution"])

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
    def get_statistics_type_status(self) -> list[dict]:
        """Get service status for each statistics type."""
        if not self.statistics_type_data:
            return []

        # Convert statistics type data to list format expected by UI
        result = []
        for statistics_type, data in self.statistics_type_data.items():
            # Ensure data is a StatisticsTypeStatusResult instance
            if isinstance(data, dict):
                data = StatisticsTypeStatusResult.from_dict(data)
            result.append(
                {
                    "type": statistics_type,
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
    def get_statistics_type_detail_data(self) -> dict:
        """Get detailed data for the selected statistics type."""
        if not self.statistics_type_data or not self.selected_statistics_type:
            return {}

        if self.selected_statistics_type not in self.statistics_type_data:
            return {
                "type": self.selected_statistics_type,
                "total_records": 0,
                "success_records": 0,
                "success_rate": 0.0,
                "status": "Unknown",
            }

        data = self.statistics_type_data[self.selected_statistics_type]
        return {
            "type": self.selected_statistics_type,
            "total_records": data.total_records,
            "success_records": data.success_records,
            "success_rate": data.success_rate,
            "status": data.status,
        }

    @rx.var
    def get_statistics_type_recent_records(self) -> list[dict]:
        """
        Get recent records for the selected statistics type - now returns empty for
        performance.
        """
        # For performance, we no longer load individual records
        # This could be implemented as a separate on-demand fetch if needed
        return []

